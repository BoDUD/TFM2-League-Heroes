//! 佐佐木小次郎（`ragnarok_kojiro`）数据做不到的部分：被动「预判」、配音、倒地声，和二天岩流时换成双刀的显示。数据
//! （tools/kit/build_kojiro.py）的 `passive` 是这里的 `ragnarok_kojiro:predict`，参数 p_per / p_max 从数据的 params 读；
//! 燕返、千手无双、二天岩流全在数据里。
//!
//! 预判（「史上最强的败者」：一辈子没赢过，却把打败他的每个人都记在心里）：他每打中一个敌方英雄一次（普攻和技能，
//! `on_attack`），就记下那个人一招，之后打那个人的每一下伤害按记下的招数加（每招 p_per%，每个人最多 p_max 招）。对手按
//! 「队伍 + 英雄名」认，对手死了复活还认得；小次郎自己死了全部重新记。
//!
//! 双刀：二天岩流交错那一刀以后，数据给他挂 `ragnarok_kojiro_niten`（几秒，攻速加成，普攻变两刀）。游戏按名字自动播的
//! idle / attack 数据换不了，这里的显示钩子（game_places::hook，宙斯三种身体的做法）在他有这个 buff 时换成 `niten_idle`
//! （Codex 画的双刀待机）和 `niten_attack`（大招的双刀两连斩按普攻的节奏重排）。别的动作（跑、挨打、倒下）只画了单刀。
//!
//! 配音（山路和弘的原声，Codex 截的八句）：一局第一次和敌方英雄交手说一句（轮到我了吗 / 能和神打到什么地步，偶尔是
//! 与神交手前的思考），杀了英雄（神也会败 / 请亲眼见证），放二天岩流时偶尔「小次郎上阵」，复活时（一直败下来的剑士 /
//! 回神）。每类有自己的冷却，任意两句之间至少隔一会儿。倒地：死的时候放刀落地和身子着地（延迟在 sound_info 里）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `kojiro`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_kojiro";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// 日志只记前面这些行，之后每一百行记一行
const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 100;
static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn log(msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= LOG_FIRST || n % LOG_EVERY == 0 {
        crate::wlog(format!("kojiro #{n} {msg}"));
    }
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 每记下一招，打这个人的伤害加多少，百分比
    pub p_per: usize,
    /// 每个人最多记几招
    pub p_max: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_per: 3,
            p_max: 8,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        let u = v.max(0) as usize;
        match k {
            "p_per" => p.p_per = u.min(50),
            "p_max" => p.p_max = u.min(50),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// 记下 learned 招以后，这一下的伤害。
pub fn boosted(damage: usize, learned: usize, p: &Params) -> usize {
    damage + damage * p.p_per * learned.min(p.p_max) / 100
}

/// 记招的账本：对手（队伍 + 英雄名）→ 记下几招。
#[derive(Clone, Debug, Default)]
pub struct Book {
    learned: HashMap<String, usize>,
}

impl Book {
    /// 打中这个人一下：先按已经记下的招数加这一下的伤害，再记下这一招。→ (加过的伤害, 记下以后的招数)
    pub fn hit(&mut self, who: &str, damage: usize, p: &Params) -> (usize, usize) {
        let k = self.learned.entry(who.to_string()).or_insert(0);
        let out = boosted(damage, *k, p);
        if *k < p.p_max {
            *k += 1;
        }
        (out, *k)
    }

    pub fn forget(&mut self) {
        self.learned.clear();
    }

    pub fn of(&self, who: &str) -> usize {
        self.learned.get(who).copied().unwrap_or(0)
    }
}

/// 配音：事件。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 杀了敌方英雄
    Kill,
    /// 放了二天岩流（起手那一下）
    Ult,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        // 五份里一份是与神交手前的思考（长，偶尔说）
        Cue::Start => &["v_entry", "v_challenge", "v_entry", "v_challenge", "v_focus"],
        Cue::Kill => &["v_victory", "v_witness"],
        Cue::Ult => &["v_charge"],
        Cue::Respawn => &["v_defeats", "v_idle"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Kill => 25 * SECOND,
        Cue::Ult => 40 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 放大招时喊不喊：冷却到了也只有三成五的时候开口
pub const ULT_CHANCE: u64 = 35;

/// 一份模拟里的配音节奏：上一句的拍数、每类上次的拍数、每类轮到第几句。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    turn: HashMap<&'static str, usize>,
    started: bool,
}

impl Voice {
    fn key(cue: Cue) -> &'static str {
        match cue {
            Cue::Start => "start",
            Cue::Kill => "kill",
            Cue::Ult => "ult",
            Cue::Respawn => "respawn",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那句一局只说一次，按拍数挑，别的按顺序轮。
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        if cue == Cue::Start && self.started {
            return None;
        }
        if self.last_any.is_some_and(|t| tick < t + VOICE_GAP) {
            return None;
        }
        let k = Self::key(cue);
        if self.last.get(k).is_some_and(|&t| tick < t.saturating_add(cue_cooldown(cue))) {
            return None;
        }
        let lines = lines_of(cue);
        let line = if cue == Cue::Start {
            self.started = true;
            lines[tick % lines.len()]
        } else {
            let turn = self.turn.entry(k).or_insert(0);
            *turn += 1;
            lines[(*turn - 1) % lines.len()]
        };
        self.last.insert(k, tick);
        self.last_any = Some(tick);
        Some(line)
    }
}

// ===================== 双刀的显示 =====================

/// 二天岩流之后的 buff（数据 build_kojiro.py 的 niten）。
pub const NITEN: &str = "ragnarok_kojiro_niten";
/// 双刀有自己一套的动作（图里单刀的原名，双刀 niten_*）。
pub const NITEN_TAGS: [&str; 2] = ["idle", "attack"];

/// 正在播的动画名 + 有没有双刀 buff → 该播的名字（不用换就是 None）。buff 没了把换上去的 niten_ 换回来。
pub fn anim_for(cur: &str, niten: bool) -> Option<String> {
    let base = cur.strip_prefix("niten_").filter(|b| NITEN_TAGS.contains(b)).unwrap_or(cur);
    if !NITEN_TAGS.contains(&base) {
        return None;
    }
    let want = if niten { format!("niten_{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

#[cfg(windows)]
mod view {
    //! 显示钩子：走显示世界的实体表，名字是 ragnarok_kojiro 的按有没有双刀 buff 换正在播的动画名（宙斯 zeus.rs 的做法）。

    use std::sync::{Mutex, Once};

    use super::{anim_for, log, NITEN};
    use game_places::hook::{Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR,
                            VALUE};

    const NAME: &[u8] = b"ragnarok_kojiro";

    static LOOKS: Mutex<Vec<(usize, u64, bool)>> = Mutex::new(Vec::new());
    static HOOK: Once = Once::new();

    #[link(name = "kernel32")]
    extern "system" {
        fn GetProcessHeap() -> isize;
        fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
        fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
    }

    unsafe fn q(addr: usize) -> usize {
        std::ptr::read_unaligned(addr as *const usize)
    }

    fn plausible(p: usize) -> bool {
        (0x10000..0x7fff_ffff_ffff).contains(&p)
    }

    /// 实体身上有没有这个名字的 buff。
    unsafe fn has(v: usize, name: &str) -> bool {
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
        })
    }

    /// 显示世界里每个小次郎：有双刀 buff 就把待机、普攻换成双刀的。
    unsafe fn dress(world: usize, ents: &[Ent]) {
        for e in ents {
            let elem = e.elem;
            let v = elem + VALUE;
            if q(v + NAME_LEN_AT) != NAME.len() {
                continue;
            }
            let ptr = q(v + NAME_PTR);
            if !plausible(ptr) || std::slice::from_raw_parts(ptr as *const u8, NAME.len()) != NAME {
                continue;
            }
            let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
            if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
                continue;
            }
            let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
            let key = q(elem) as u64;
            let niten = has(v, NITEN);
            if let Ok(mut looks) = LOOKS.try_lock() {
                let look = (world, key, niten);
                if !looks.contains(&look) {
                    looks.retain(|l| !(l.0 == world && l.1 == key));
                    looks.push(look);
                    if looks.len() > 64 {
                        looks.remove(0);
                    }
                    log(format!("world {world:#x} Kojiro #{key}: {} (playing {cur})",
                                if niten { "two swords" } else { "one sword" }));
                }
            }
            let Some(want) = anim_for(cur, niten) else { continue };
            let heap = GetProcessHeap();
            let fresh = HeapAlloc(heap, 0, want.len());
            if fresh.is_null() {
                continue;
            }
            std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
            std::ptr::write_unaligned((v + ANIM_CAP) as *mut usize, want.len());
            std::ptr::write_unaligned((v + ANIM_PTR) as *mut usize, fresh as usize);
            std::ptr::write_unaligned((v + ANIM_LEN) as *mut usize, want.len());
            if acap > 0 {
                HeapFree(heap, 0, aptr as *mut u8);
            }
        }
    }

    /// 登记显示钩子（一个进程一次）：本 DLL 在 init 里先 hd_engine::defer_display()，真正换槽等第一帧（lib.rs 的 Frame）。
    pub fn install_once() {
        HOOK.call_once(|| match game_places::hook::add("ragnarok_kojiro", dress, |m: &str| crate::wlog(m)) {
            Ok(p) => crate::wlog(format!("kojiro: two swords on: {p}")),
            Err(e) => crate::wlog(format!("kojiro: two swords off ({e}): the one-sword frames only")),
        });
    }
}

// ===================== 游戏里 =====================

/// 对手的名字：「队伍:英雄名」，复活以后还是同一个人；拿不到名字时退回实体号。
fn who(sim: &StableSim<'_>, id: usize) -> Option<String> {
    let e = sim.get_entity(id)?;
    Some(match e.name() {
        Some(name) if !name.is_empty() => format!("{}:{name}", e.team()),
        _ => format!("#{id}"),
    })
}

#[derive(Clone, Default)]
struct Predict {
    me: usize,
    p: Params,
    book: Book,
    was_alive: bool,
    lives: usize,
    /// 大招的冷却上一拍是多少，用来认出这一拍刚放了大招
    r_cd: usize,
    voice: Voice,
}

impl Predict {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(format!("[t={tick}] VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for Predict {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(format!("[t={}] SPAWN #{me}: ragnarok.dll's Kojiro (player {player}, team {team}), {:?}", sim.tick(), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if alive && !self.was_alive {
            self.lives += 1;
            if self.lives > 1 {
                self.say(sim, Cue::Respawn);
            }
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        // 大招的冷却从 0 跳上去就是刚放了
        let r_cd = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.3);
        let ult = r_cd > self.r_cd + 30;
        self.r_cd = r_cd;
        if ult && (rng % 100) < ULT_CHANCE {
            self.say(sim, Cue::Ult);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let enemy_champion = sim.get_entity(target).is_some_and(|t| t.team() != my_team && t.is_champion());
        if !enemy_champion {
            return;
        }
        if let Some(name) = who(sim, target) {
            let before = *damage;
            let (out, k) = self.book.hit(&name, before, &self.p);
            *damage = out;
            log(format!("[t={}] READ #{me} -> {name}: {before} -> {out}, {k} move(s) known", sim.tick()));
        }
        self.say(sim, Cue::Start);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.me = me;
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.say(sim, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.was_alive = false;
        // 死了就全部重新记
        self.book.forget();
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// 小次郎的被动和显示钩子，注册进本包的模块（lib.rs 的 init，在 hd_engine::defer_display 之后）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("kojiro: {ID} v{VERSION} (Kojiro: prediction, two swords, voice lines) registered"));
    module.add_native_passive(format!("{ID}:predict"), Predict::default());
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "ragnarok.dll: Sasaki Kojiro (prediction, two swords, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let p = parse_params(r#"{"p_per": 3, "p_max": 8}"#);
        assert_eq!(p, Params::default());
        assert_eq!(parse_params(r#"{"p_per": 999}"#).p_per, 50);
    }

    #[test]
    fn each_foe_is_read_on_his_own_and_up_to_the_cap() {
        let p = Params::default();
        let mut b = Book::default();
        // 第一下还没记下什么，原样；记下一招
        assert_eq!(b.hit("1:league_garen", 100, &p), (100, 1));
        assert_eq!(b.hit("1:league_garen", 100, &p), (103, 2));
        // 另一个人从头记
        assert_eq!(b.hit("1:league_darius", 100, &p), (100, 1));
        for _ in 0..20 {
            b.hit("1:league_garen", 100, &p);
        }
        assert_eq!(b.of("1:league_garen"), 8);
        assert_eq!(b.hit("1:league_garen", 100, &p), (124, 8));
        b.forget();
        assert_eq!(b.of("1:league_garen"), 0);
    }

    #[test]
    fn the_start_line_once_a_match_sometimes_the_long_one() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_entry"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 304), Some("v_focus"));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_victory"));
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_charge"));
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_witness"));
    }

    /// Codex 的八句都用上，每句只在一类里。
    #[test]
    fn every_line_is_one_of_codexs_eight() {
        let eight = ["entry", "challenge", "focus", "defeats", "witness", "victory", "charge", "idle"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Kill, Cue::Ult, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(eight.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut all = eight.to_vec();
        all.sort();
        assert_eq!(used, all);
    }

    #[test]
    fn two_swords_swap_idle_and_attack_only() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("niten_idle"));
        assert_eq!(anim_for("attack", true).as_deref(), Some("niten_attack"));
        assert_eq!(anim_for("run", true), None);
        assert_eq!(anim_for("niten_idle", true), None);
        // buff 没了换回单刀
        assert_eq!(anim_for("niten_idle", false).as_deref(), Some("idle"));
        assert_eq!(anim_for("niten_attack", false).as_deref(), Some("attack"));
        assert_eq!(anim_for("idle", false), None);
        assert_eq!(anim_for("ult", false), None);
    }
}
