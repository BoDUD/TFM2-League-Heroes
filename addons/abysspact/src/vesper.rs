//! 烛灵 (`abysspact_vesper`) · 灵媒少女 · 辅助
//!
//! - 被动「烛冠」：身边 5 万内每死一个英雄（敌我都算）点亮一支蜡烛，最多 5 支（头顶 `candle_1..5`），每支让她的
//!   回血和护盾 +10%：引路（Q）的回血、护盾由本包按支数补上那一截（引路的数值在数据的 passive.params 里），R 的群盾
//!   直接乘上去。她倒下时蜡烛全灭（设计的倒地动作：蜡烛一支支熄灭）。蜡烛不加法强。
//! - R「回魂」：数据的 R 只是 3 tick 的「备好」（敌方英雄 6 万内就按），挂 `r_ask`；本包在备好的 6 秒里等：
//!   * 有 10 秒内倒在她 6 万内、还没复活的队友 → 回魂：复活时间改成 1 tick（阿克尚附加包核对过的写法），复活后放回
//!     倒下的地方，挂魂体 `spirit`（受到的伤害减半、不能被治疗，8 秒）和记号 `soul:<开始时己方击杀数>:<结束 tick>`；
//!     她放大招动作、说大招台词，倒下的地方升起光柱；
//!   * 否则身边 5 万内有队友（她自己也算）生命低于 35%、附近有敌方英雄 → 身边所有队友 100 + 60% 法强的盾（乘烛冠）；
//!   * 6 秒都没用上 → 冷却退到只剩 3 秒，下次打起来再备。
//!   以前 R 一好就被 AI 放掉（对友方放、没有数值的大招 AI 一好就按），几乎等不到阵亡的队友，回回都是一层盾。
//! - 魂体由排进效果队列的 `abysspact_vesper:soul` 每 6 tick 看一次（排下的效果她死了也照跑，不靠她的被动）：
//!   8 秒里己方拿到击杀就真复活（生命设成 30%，暖金光圈）；没拿到就散掉（生命设成 0）。魂体散掉倒下、或者被打倒，
//!   都把他的复活时间改回本来该复活的那一刻，一次没成的回魂不会让他多等一轮。人一倒下身上的 buff 就被游戏清掉了，
//!   所以玩家和本来复活的 tick 不记在他身上，跟着排下的效果走（借位置输入的两个坐标带，[`carry_input`]）。

use std::collections::HashMap;
use std::sync::Mutex;
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_vesper";
pub const NATIVE_MARK: &str = "abysspact_vesper_native";
pub const SPIRIT_BUFF: &str = "abysspact_vesper_spirit";
pub const R_ASK: &str = "abysspact_vesper_r_ask";
/// 引路挂在队友身上的 buff（数据的 Q）。
pub const GUIDE_BUFF: &str = "abysspact_vesper_guide";
/// 魂体身上的记号前缀。
pub const SOUL_MARK: &str = "abysspact_vesper_soul";
pub const SOUL_FX: &str = "abysspact_vesper:soul";

pub const CANDLE_CAP: usize = 5;
pub const CANDLE_RADIUS: u64 = 50_000; // 5.0万
pub const FALLEN_WINDOW: usize = 600; // 10.0s recent death window
pub const SPIRIT_TICKS: usize = 480; // 8.0s spirit fight duration
pub const TRUE_REVIVE_HP_PCT: usize = 30;
pub const FALLBACK_SHIELD_RANGE: u64 = 50_000;
pub const FALLBACK_SHIELD_TICKS: usize = 240;
/// 回魂够得着的队友：倒在她 6 万内（R 的射程）。
pub const REVIVE_RANGE: u64 = 60_000;
/// R 备好以后等多久、没用上退冷却退到只剩多少。
pub const ARM_TICKS: usize = 360;
pub const REARM_TICKS: usize = 180;
/// 队友生命低于这个 % 才给群盾。
pub const DANGER_PCT: usize = 35;
/// 魂体多久看一次。
pub const SOUL_POLL: usize = 6;
/// 大招动作（图集里 ult 排成 44 tick）。
pub const ULT_POSE: u64 = 44;
/// 回魂后等队友复活、放回原地，最多等这么久。
pub const PLACE_WAIT: usize = 30;
/// 魂体散掉时生命设成 0，最多再等这么久让他倒下。
pub const FADE_GRACE: usize = 60;
/// 借位置输入带两个数：都加上一个身位（落在地图里面），玩家号每个隔一万。
pub const CARRY_BASE: u64 = 30_000;
pub const CARRY_STEP: u64 = 10_000;

pub fn candle_buff_name(k: usize) -> Option<&'static str> {
    match k {
        1 => Some("abysspact_vesper_candle_1"),
        2 => Some("abysspact_vesper_candle_2"),
        3 => Some("abysspact_vesper_candle_3"),
        4 => Some("abysspact_vesper_candle_4"),
        5 => Some("abysspact_vesper_candle_5"),
        _ => None,
    }
}

/// 烛冠的加成：每支 +10%，最多 5 支。
pub fn with_candles(base: usize, candles: usize) -> usize {
    base.saturating_mul(100 + candles.min(CANDLE_CAP) * 10) / 100
}

/// 只要烛冠多出来的那一截（数据已经给了基础的那份）。
pub fn candle_bonus(base: usize, candles: usize) -> usize {
    base.saturating_mul(candles.min(CANDLE_CAP) * 10) / 100
}

pub fn fallback_shield_amount(ap: usize, candles: usize) -> usize {
    with_candles(100 + ap.saturating_mul(60) / 100, candles)
}

/// 引路的数值（数据 passive.params 传进来，键排好序、值是整数）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct GuideNums {
    pub heal: usize,
    pub heal_ap: usize,
    pub sh: usize,
    pub sh_ap: usize,
    pub sh_t: usize,
}

impl Default for GuideNums {
    fn default() -> Self {
        Self { heal: 35, heal_ap: 23, sh: 62, sh_ap: 46, sh_t: 180 }
    }
}

/// 读 `{"q_heal":35,"q_heal_ap":23,...}`；认不出的键不管，缺的用默认值。
pub fn parse_params(json: &str) -> GuideNums {
    let mut n = GuideNums::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for part in body.split(',') {
        let Some((k, v)) = part.split_once(':') else { continue };
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k.trim().trim_matches('"') {
            "q_heal" => n.heal = v,
            "q_heal_ap" => n.heal_ap = v,
            "q_sh" => n.sh = v,
            "q_sh_ap" => n.sh_ap = v,
            "q_sh_t" => n.sh_t = v,
            _ => {}
        }
    }
    n
}

/// 魂体活着时身上的记号：开始时己方击杀数、结束 tick。
pub fn soul_name(kills: usize, end: usize) -> String {
    format!("{SOUL_MARK}:{kills}:{end}")
}

pub fn parse_soul(name: &str) -> Option<(usize, usize)> {
    let (k, end) = name.strip_prefix(SOUL_MARK)?.strip_prefix(':')?.split_once(':')?;
    Some((k.parse().ok()?, end.parse().ok()?))
}

/// 排给魂体检查的输入：(玩家, 本来复活的 tick) 放在位置输入的两个坐标里。
pub fn carry_input(player: usize, back: usize) -> InputTargetV1 {
    InputTargetV1::pos(CARRY_BASE + player as u64 * CARRY_STEP, CARRY_BASE + back as u64)
}

/// 从输入里读回 (玩家, 本来复活的 tick)；不是位置输入就是 None。
pub fn carried(input: &InputTargetV1) -> Option<(usize, usize)> {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Pos) {
        return None;
    }
    let p = input.x.checked_sub(CARRY_BASE)?;
    let back = input.y.checked_sub(CARRY_BASE)?;
    Some((((p + CARRY_STEP / 2) / CARRY_STEP) as usize, back as usize))
}

// ---------------------------------------------------------------------------
// 缩短阵亡玩家的复活时间：读游戏两个接口的机器码找到内存位置，核对过才写，写完读回核对（阿克尚附加包的做法）
// ---------------------------------------------------------------------------
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct LifeLayout {
    getp: usize,
    tag: usize,
    val: usize,
}

#[derive(Default)]
struct Scan {
    getp: Option<usize>,
    tag_cmp: Option<usize>,
    val: Option<usize>,
    tag_movzx: Option<usize>,
    dec_rdx: bool,
    load_data: bool,
    load_vt: bool,
}

fn modrm_disp(code: &[u8], at: usize) -> Option<(u8, usize, usize)> {
    let m = *code.get(at)?;
    let (md, reg, rm) = (m >> 6, (m >> 3) & 7, m & 7);
    if rm == 4 {
        return None;
    }
    match md {
        1 => Some((reg, *code.get(at + 1)? as i8 as isize as usize, 2)),
        2 => {
            let b = code.get(at + 1..at + 5)?;
            Some((reg, i32::from_le_bytes([b[0], b[1], b[2], b[3]]) as isize as usize, 5))
        }
        _ => None,
    }
}

fn scan(code: &[u8]) -> Scan {
    let mut s = Scan::default();
    let mut i = 0;
    while i + 3 < code.len() {
        let rex = (0x40..=0x4f).contains(&code[i]);
        let (w, op) = if rex { (code[i] & 8 != 0, i + 1) } else { (false, i) };
        let b = code[op];
        if rex && code[i] == 0x48 && b == 0xff && code.get(op + 1) == Some(&0xca) {
            s.dec_rdx = true;
        }
        if w && b == 0x8b {
            if let Some(&m) = code.get(op + 1) {
                if m >> 6 == 0 && m & 7 == 1 {
                    s.load_data = true;
                }
                if m >> 6 == 1 && m & 7 == 1 && code.get(op + 2) == Some(&8) {
                    s.load_vt = true;
                }
            }
        }
        if b == 0xff {
            if let Some((2, disp, _)) = modrm_disp(code, op + 1) {
                s.getp.get_or_insert(disp);
            }
        }
        if b == 0x80 && s.tag_cmp.is_none() {
            if let Some((7, disp, n)) = modrm_disp(code, op + 1) {
                let imm = op + 1 + n;
                if code.get(imm) == Some(&0) && code.get(imm + 1) == Some(&0x74) {
                    let target = imm + 3 + code[imm + 2] as usize;
                    if let Some(&r) = code.get(target) {
                        if (0x48..=0x4f).contains(&r) && code.get(target + 1) == Some(&0x8b) {
                            if let Some((_, v, _)) = modrm_disp(code, target + 2) {
                                s.tag_cmp = Some(disp);
                                s.val = Some(v);
                            }
                        }
                    }
                }
            }
        }
        if b == 0x0f && code.get(op + 1) == Some(&0xb6) && s.tag_movzx.is_none() {
            if let Some((_, disp, _)) = modrm_disp(code, op + 2) {
                s.tag_movzx = Some(disp);
            }
        }
        i += 1;
    }
    s
}

fn decode(respawn_time: &[u8], is_alive: &[u8]) -> Option<LifeLayout> {
    let a = scan(respawn_time);
    let b = scan(is_alive);
    let (getp, tag, val) = (a.getp?, a.tag_cmp?, a.val?);
    let ok = a.dec_rdx
        && a.load_data
        && a.load_vt
        && b.dec_rdx
        && b.getp == Some(getp)
        && b.tag_movzx == Some(tag)
        && val == tag + 8
        && getp % 8 == 0
        && getp < 0x800
        && tag < 0x10000;
    ok.then_some(LifeLayout { getp, tag, val })
}

unsafe fn follow(mut f: *const u8) -> *const u8 {
    for _ in 0..3 {
        match *f {
            0xe9 => {
                let r = i32::from_le_bytes(std::ptr::read_unaligned(f.add(1) as *const [u8; 4]));
                f = f.offset(5 + r as isize);
            }
            0xeb => f = f.offset(2 + *(f.add(1) as *const i8) as isize),
            _ => break,
        }
    }
    f
}

static LAYOUT: Mutex<Option<(usize, usize, Option<LifeLayout>)>> = Mutex::new(None);
const _: () = assert!(std::mem::size_of::<StableSim<'static>>() == std::mem::size_of::<*mut SimCtxV1>());

fn raw_ctx(sim: &StableSim<'_>) -> *mut SimCtxV1 {
    unsafe { *(sim as *const StableSim<'_> as *const *mut SimCtxV1) }
}

fn layout(sim: &StableSim<'_>) -> Option<LifeLayout> {
    let ctx = raw_ctx(sim);
    if ctx.is_null() {
        return None;
    }
    let vt = unsafe { (*ctx).sim };
    if vt.is_null() {
        return None;
    }
    let rt = unsafe { (*vt).player_respawn_time }? as usize;
    let al = unsafe { (*vt).player_is_alive }? as usize;
    let mut cache = LAYOUT.lock().unwrap_or_else(|e| e.into_inner());
    if let Some((a, b, l)) = *cache {
        if a == rt && b == al {
            return l;
        }
    }
    let l = unsafe {
        let (frt, fal) = (follow(rt as *const u8), follow(al as *const u8));
        decode(std::slice::from_raw_parts(frt, 0x60), std::slice::from_raw_parts(fal, 0x60))
    };
    *cache = Some((rt, al, l));
    l
}

type GetPlayer = unsafe extern "C" fn(*mut std::ffi::c_void, usize) -> *mut u8;

fn shorten_respawn(sim: &StableSim<'_>, player: usize, ticks: u64) -> Result<(u64, u64), &'static str> {
    let l = layout(sim).ok_or("no layout")?;
    let p = sim.get_player(player).ok_or("no player")?;
    if p.is_alive() {
        return Err("alive");
    }
    let api = p.respawn_time() as u64;
    let ctx = raw_ctx(sim);
    unsafe {
        let st = (*ctx).state as *const usize;
        if st.is_null() || *(st as *const u8).add(0x18) != 0 {
            return Err("read-only");
        }
        let (world, wvt) = (*st, *st.add(1));
        if world == 0 || wvt == 0 {
            return Err("no world");
        }
        let slot = *((wvt + l.getp) as *const usize);
        if slot == 0 {
            return Err("no get_player");
        }
        let getp: GetPlayer = std::mem::transmute(slot);
        let pp = getp(world as *mut std::ffi::c_void, player);
        if pp.is_null() {
            return Err("null player");
        }
        let tag = std::ptr::read_unaligned(pp.add(l.tag) as *const u64);
        let cur = std::ptr::read_unaligned(pp.add(l.val) as *const u64);
        if tag != 0 || cur != api || cur == 0 {
            return Err("mismatch");
        }
        let new = cur.min(ticks.max(1));
        if new < cur {
            std::ptr::write_unaligned(pp.add(l.val) as *mut u64, new);
        }
        if p.respawn_time() as u64 != new {
            return Err("verify failed");
        }
        Ok((cur, new))
    }
}

// ---------------------------------------------------------------------------
// 回魂之后
// ---------------------------------------------------------------------------

fn count_team_kills(sim: &StableSim<'_>, team: usize) -> usize {
    (0..sim.kill_log_count()).filter_map(|i| sim.kill_log_at(i)).filter(|k| k.killer_team == team).count()
}

fn soul_of(sim: &StableSim<'_>, id: usize) -> Option<(String, (usize, usize))> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find_map(|b| {
        let name = b.name().to_string();
        parse_soul(&name).map(|s| (name, s))
    })
}

/// 魂体每 6 tick 看一次：己方拿到击杀就真复活，8 秒到了就散掉；他倒下了（被打倒、散掉）就把复活时间改回本来那一刻。
#[derive(Debug)]
struct Soul;

impl StableEffectType for Soul {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, input: InputTargetV1) {
        let Some((player, back)) = carried(&input) else { return };
        let tick = sim.tick();
        let Some((alive, team)) = sim.get_player(player).map(|p| (p.is_alive(), p.team())) else { return };
        if !alive {
            // 倒下了（魂体被打倒，或者散掉了）：复活时间不比本来的长，回魂不该害他多等
            let _ = shorten_respawn(sim, player, back.saturating_sub(tick).max(1) as u64);
            return;
        }
        let Some((ally, max_hp)) = sim.get_player(player).and_then(|p| p.champion()).map(|e| (e.id(), e.hp().1)) else {
            return;
        };
        // 记号没了：已经真复活过
        let Some((mark, (kills, end))) = soul_of(sim, ally) else { return };
        if count_team_kills(sim, team) > kills {
            sim.entity_remove_buff(ally, SPIRIT_BUFF);
            sim.entity_remove_buff(ally, &mark);
            sim.entity_set_hp(ally, (max_hp.saturating_mul(TRUE_REVIVE_HP_PCT) / 100).max(1));
            sim.play_view_effect("abysspact_vesper_rebirth", caster, &InputTargetV1::target(ally), 0, 0, 0);
            sim.play_sfx("abysspact_vesper_rebirth_ring", caster, &InputTargetV1::target(ally));
            return;
        }
        if tick >= end {
            // 8 秒到了还没拿到击杀：散掉。下一次检查时他已经倒下，把复活时间改回来
            if tick > end + FADE_GRACE {
                return;
            }
            sim.entity_remove_buff(ally, SPIRIT_BUFF);
            sim.entity_set_hp(ally, 0);
            sim.play_sfx("abysspact_vesper_candle_out", caster, &InputTargetV1::target(ally));
            sim.queue_effect(SOUL_FX, AttackTypeV1::Skill, caster, &input, 2);
            return;
        }
        sim.queue_effect(SOUL_FX, AttackTypeV1::Skill, caster, &input, SOUL_POLL);
    }
}

// ---------------------------------------------------------------------------
// 烛灵的被动
// ---------------------------------------------------------------------------

#[derive(Clone, Copy)]
struct Pending {
    player: usize,
    death_pos: (u64, u64),
    kills_at_start: usize,
    /// 不回魂的话他本来哪一 tick 复活。
    back: usize,
    since: usize,
}

#[derive(Clone, Default)]
struct VesperPassive {
    voice: Voice,
    nums: GuideNums,
    candles: usize,
    /// 玩家 -> (上一 tick 活着没有, 最后看到他的地方)
    seen_players: HashMap<usize, (bool, (u64, u64))>,
    /// 最近倒下的队友：player_id -> (倒下的地方, 倒下的 tick)
    fallen_allies: HashMap<usize, ((u64, u64), usize)>,
    /// R 备好到哪一 tick。
    armed_until: Option<usize>,
    /// 回魂了、等他复活放回原地。
    pending: Option<Pending>,
    /// 身上有引路的队友：实体 -> 第一次看到的 tick。
    guided: HashMap<usize, usize>,
}

impl VesperPassive {
    fn sync_candles(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        for k in 1..=CANDLE_CAP {
            if let Some(n) = candle_buff_name(k) {
                sim.entity_remove_buff(entity, n);
            }
        }
        if let Some(n) = candle_buff_name(self.candles) {
            sim.add_buff(entity, &BuffV1::named(n));
        }
    }

    /// 记下现在谁活着、在哪（她刚复活时用：她死着的时候被动不跑，之前记的已经不作数）。
    fn seed_players(&mut self, sim: &StableSim<'_>) {
        self.seen_players.clear();
        for i in 0..sim.player_count() {
            let Some(p) = sim.player_at(i) else { continue };
            let at = p.champion().map(|c| c.pos()).unwrap_or((0, 0));
            self.seen_players.insert(p.id(), (p.is_alive(), at));
        }
    }

    /// 谁刚倒下：身边的点蜡烛，队友记进最近阵亡。
    fn observe(&mut self, sim: &StableSim<'_>, my_player: usize, my_team: usize, my_pos: (u64, u64), tick: usize) -> bool {
        let r2 = CANDLE_RADIUS * CANDLE_RADIUS;
        let mut lit = false;
        for i in 0..sim.player_count() {
            let Some(p) = sim.player_at(i) else { continue };
            let pid = p.id();
            let alive = p.is_alive();
            let cur_pos = p.champion().map(|c| c.pos());
            let prev = self.seen_players.get(&pid).copied();
            if let Some((was_alive, last_pos)) = prev {
                if was_alive && !alive {
                    if self.candles < CANDLE_CAP && dist_sq(my_pos, last_pos) <= r2 {
                        self.candles += 1;
                        lit = true;
                    }
                    if p.team() == my_team && pid != my_player {
                        self.fallen_allies.insert(pid, (last_pos, tick));
                    }
                }
            }
            let store = if alive { cur_pos.or(prev.map(|x| x.1)) } else { prev.map(|x| x.1) };
            self.seen_players.insert(pid, (alive, store.unwrap_or(my_pos)));
        }
        lit
    }

    /// 放大招动作、说台词、指针声。
    fn pose(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        let mut pose = CcV1::of_kind(CcKindV1::Animation, ULT_POSE);
        pose.set_name("ult");
        sim.apply_cc(entity, &pose);
        sim.play_sfx("abysspact_vesper_r_pointer", entity, &InputTargetV1::target(entity));
        self.voice.play(sim, HERO, entity, Cue::Ult);
    }

    /// 回魂：10 秒内倒在她 6 万内、还没复活的队友，挑最近倒下的那个。
    fn try_revive(&mut self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, my_pos: (u64, u64), tick: usize) -> bool {
        let r2 = REVIVE_RANGE * REVIVE_RANGE;
        let mut picks: Vec<(usize, (u64, u64), usize)> = self
            .fallen_allies
            .iter()
            .filter(|&(_, &(pos, _))| dist_sq(my_pos, pos) <= r2)
            .map(|(&pid, &(pos, t))| (pid, pos, t))
            .collect();
        picks.sort_by_key(|&(pid, _, t)| (std::cmp::Reverse(t), pid));
        for (pid, dpos, _) in picks {
            let Ok((cur, _)) = shorten_respawn(sim, pid, 1) else { continue };
            self.fallen_allies.remove(&pid);
            self.pending = Some(Pending {
                player: pid,
                death_pos: dpos,
                kills_at_start: count_team_kills(sim, my_team),
                back: tick + cur as usize,
                since: tick,
            });
            self.pose(sim, entity);
            sim.play_view_effect("abysspact_vesper_pillar", entity, &InputTargetV1::pos(dpos.0, dpos.1), 0, 0, 0);
            sim.play_sfx("abysspact_vesper_return_pillar", entity, &InputTargetV1::pos(dpos.0, dpos.1));
            return true;
        }
        false
    }

    /// 没人可回魂时：身边有队友残血、附近有敌方英雄，就给身边所有队友加盾。
    fn try_shield(&mut self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, my_pos: (u64, u64), ap: usize) -> bool {
        let r2 = FALLBACK_SHIELD_RANGE * FALLBACK_SHIELD_RANGE;
        let mut allies = Vec::new();
        let mut hurt = false;
        let mut foe_near = false;
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() || !e.is_champion() || dist_sq(my_pos, e.pos()) > r2 {
                continue;
            }
            if e.team() == my_team {
                let (hp, max) = e.hp();
                hurt |= hp.saturating_mul(100) < max.saturating_mul(DANGER_PCT);
                allies.push(e.id());
            } else {
                foe_near = true;
            }
        }
        if !hurt || !foe_near {
            return false;
        }
        let amt = fallback_shield_amount(ap, self.candles);
        for aid in allies {
            sim.entity_add_shield(aid, amt, FALLBACK_SHIELD_TICKS);
            sim.play_view_effect("abysspact_vesper_shield", entity, &InputTargetV1::target(aid), 0, 0, 0);
        }
        self.pose(sim, entity);
        sim.play_sfx("abysspact_vesper_warm_shield", entity, &InputTargetV1::target(entity));
        true
    }

    /// 回魂的人复活了：放回倒下的地方，挂魂体和记号，排上魂体的检查。等太久（不是这次回魂让他复活的）就不放了。
    fn place(&mut self, sim: &mut StableSim<'_>, entity: usize, tick: usize) {
        let Some(pd) = self.pending else { return };
        if tick > pd.since + PLACE_WAIT {
            self.pending = None;
            return;
        }
        let ally = sim.get_player(pd.player).filter(|p| p.is_alive()).and_then(|p| p.champion()).map(|e| e.id());
        let Some(ally) = ally else { return };
        self.pending = None;
        sim.entity_set_pos(ally, pd.death_pos.0, pd.death_pos.1);
        // 挪一小步：画面只跟着走路和强制位移走，不挪的话他在泉水那儿站着，下次走路才跳过来
        let mut nudge = CcV1::of_kind(CcKindV1::ForceMove, 1);
        nudge.dx = 200;
        nudge.speed = 200;
        sim.apply_cc(ally, &nudge);
        let mut sb = BuffV1::timed(SPIRIT_BUFF, SPIRIT_TICKS);
        sb.damaged_reduce = 50;
        sb.heal_reduce = 100;
        sim.add_buff(ally, &sb);
        let end = tick + SPIRIT_TICKS;
        sim.add_buff(ally, &BuffV1::timed(&soul_name(pd.kills_at_start, end), SPIRIT_TICKS + FADE_GRACE));
        sim.queue_effect(SOUL_FX, AttackTypeV1::Skill, entity, &carry_input(pd.player, pd.back), SOUL_POLL);
        sim.play_view_effect("abysspact_vesper_pillar", entity, &InputTargetV1::target(ally), 0, 0, 0);
        sim.play_sfx("abysspact_vesper_soul_form", entity, &InputTargetV1::target(ally));
    }

    /// 烛冠补引路的回血（落地、1 秒、2 秒各一次）和结束时的护盾。
    fn guide_bonus(&mut self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, ap: usize, tick: usize) {
        if self.candles == 0 {
            self.guided.clear();
            return;
        }
        let heal = candle_bonus(self.nums.heal + ap.saturating_mul(self.nums.heal_ap) / 100, self.candles);
        let shield = candle_bonus(self.nums.sh + ap.saturating_mul(self.nums.sh_ap) / 100, self.candles);
        let mut now = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.id() != entity && e.is_alive() && e.is_champion() && e.team() == my_team && has_buff(sim, e.id(), GUIDE_BUFF) {
                now.push(e.id());
            }
        }
        for &id in &now {
            let first = *self.guided.entry(id).or_insert(tick);
            let k = tick - first;
            if (k == 0 || k == 60 || k == 120) && heal > 0 {
                sim.heal(entity, id, heal);
            }
        }
        let ended: Vec<usize> = self.guided.keys().filter(|id| !now.contains(id)).copied().collect();
        for id in ended {
            self.guided.remove(&id);
            if shield > 0 && sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                sim.entity_add_shield(id, shield, self.nums.sh_t);
            }
        }
    }
}

impl StablePassive for VesperPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.nums = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.voice.on_spawn(sim, HERO, entity);
        self.seed_players(sim);
        self.fallen_allies.clear();
        self.guided.clear();
        self.armed_until = None;
        self.pending = None;
        self.sync_candles(sim, entity);
    }

    fn on_attack(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        target: usize,
        _damage: &mut usize,
    ) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        // 她倒下：蜡烛全灭，没用上的 R 作废，还没放回原地的回魂也不放了
        self.candles = 0;
        self.armed_until = None;
        self.pending = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, my_player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, ap)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.stat().magic_power))
        else {
            return;
        };
        if !alive {
            return;
        }
        let tick = sim.tick();
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }

        // 1. 谁倒下了：点蜡烛、记下阵亡的队友（只留 10 秒内、还没复活的）
        if self.observe(sim, my_player, my_team, my_pos, tick) {
            self.sync_candles(sim, entity);
        }
        self.fallen_allies.retain(|&pid, &mut (_, dt)| {
            tick.saturating_sub(dt) <= FALLEN_WINDOW && sim.get_player(pid).is_some_and(|p| !p.is_alive())
        });

        // 2. 回魂的人复活了就放回原地
        self.place(sim, entity, tick);

        // 3. R 备好了：等着回魂或者加盾，6 秒没用上就退冷却
        if consume_buff(sim, entity, R_ASK) {
            self.armed_until = Some(tick + ARM_TICKS);
        }
        if let Some(until) = self.armed_until {
            if self.try_revive(sim, entity, my_team, my_pos, tick) || self.try_shield(sim, entity, my_team, my_pos, ap) {
                self.armed_until = None;
            } else if tick >= until {
                // 备好的 3 tick 动作早就结束了，冷却已经在走：退到只剩 3 秒
                self.armed_until = None;
                crate::refund_cooldown(sim, entity, SkillSlotV1::Ult, REARM_TICKS);
            }
        }

        // 4. 烛冠补引路
        self.guide_bonus(sim, entity, my_team, ap, tick);
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_vesper:vigil", VesperPassive::default());
    module.add_native_effect(SOUL_FX, Soul);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn candle_buffs_and_fallback_shield_scale_up_to_5_candles() {
        assert_eq!(candle_buff_name(0), None);
        assert_eq!(candle_buff_name(1), Some("abysspact_vesper_candle_1"));
        assert_eq!(candle_buff_name(5), Some("abysspact_vesper_candle_5"));
        assert_eq!(candle_buff_name(6), None);
        // base 100 + 60% of 100 AP = 160; 5 candles = +50% -> 240（法强不再被蜡烛放大，只乘一次）
        assert_eq!(fallback_shield_amount(100, 0), 160);
        assert_eq!(fallback_shield_amount(100, 5), 240);
        assert_eq!(fallback_shield_amount(100, 9), 240);
        // 引路只补多出来的那一截：3 支 = 30%
        assert_eq!(candle_bonus(100, 3), 30);
        assert_eq!(candle_bonus(100, 0), 0);
    }

    #[test]
    fn guide_numbers_come_from_the_kit() {
        let n = parse_params(r#"{"q_heal":40,"q_heal_ap":25,"q_sh":70,"q_sh_ap":50,"q_sh_t":200}"#);
        assert_eq!(n, GuideNums { heal: 40, heal_ap: 25, sh: 70, sh_ap: 50, sh_t: 200 });
        assert_eq!(parse_params("{}"), GuideNums::default());
        assert_eq!(parse_params(""), GuideNums::default());
    }

    #[test]
    fn the_soul_mark_reads_back_and_fits_a_buff_name() {
        let name = soul_name(12, 123_456);
        assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        assert_eq!(parse_soul(&name), Some((12, 123_456)));
        assert_eq!(parse_soul("abysspact_vesper_spirit"), None);
        assert_eq!(parse_soul("abysspact_vesper_soul:1"), None);
    }

    #[test]
    fn the_player_and_his_respawn_tick_ride_with_the_check() {
        // 倒下的人身上读不到记号，这两个数跟着排下的效果走
        for (player, back) in [(0, 0), (3, 7_260), (9, 216_000)] {
            let input = carry_input(player, back);
            assert_eq!(carried(&input), Some((player, back)));
            // 落在地图里面（引擎就算把位置夹进地图也不会变）
            assert!(input.x >= 22_500 && input.x <= 937_500 && input.y >= 22_500 && input.y <= 937_500, "{input:?}");
        }
        // 别的输入不认
        assert_eq!(carried(&InputTargetV1::target(5)), None);
    }

    #[test]
    fn the_armed_ult_keeps_the_ult_tooltip() {
        // R 的动作名是 idle（3 tick 的备好），说明文字还得指向 .ult，不然各语言都缺这一条
        let kit = include_str!("../../../abysspact/champion/abysspact_vesper.data_champion");
        assert!(kit.contains("\"description\": \"#asset/base/text/champion?description.abysspact_vesper.ult\""));
        assert!(!kit.contains("description.abysspact_vesper.idle"));
        let text = include_str!("../../../abysspact/text/champion.i18n");
        let at = text.find("\"abysspact_vesper\"").expect("vesper in the text");
        assert!(text[at..].contains("\"ult\""));
    }
}
