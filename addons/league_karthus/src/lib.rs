//! 卡尔萨斯附加包（用户选「被动做附加包」）：主包数据做不到的死亡契约。
//!
//! `mod.override_info` 把主包的卡尔萨斯换成 `override/` 里的副本（tools/kit/build_karthus.py 的 native=1）：数据和主包
//! 一样，只是被动挂本包的 `league_karthus:death_defied`（参数在英雄数据的 `passive.params` 里），多一个灵体的画面。
//!
//! - **死亡契约**：英雄联盟里卡尔萨斯死后化成灵体，7 秒内照样放技能，然后才倒下。数据读不到血量，主包做不了。
//!   本包一直给他挂着「不死」`league_karthus_p_guard`，致命伤害只会把他打到 1 血；到 1 血（身上没有别人给的不死）时
//!   **化成灵体** `p_t` tick：隐身（敌人选不中他，`entity_set_invisible`）、不再受伤（`damaged_reduce` 100%）、免控，
//!   照常走动、放技能、攻击（灵体时 AI 钩子 `spirit_ai` 替游戏的逃跑 AI 放 R / Q / E、打人）；身上挂 `league_karthus_p_spirit`（画面）。时间到就倒下，击杀算最后打他的那个人。
//!   每条命都有（英雄联盟每次死亡都会触发）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_karthus.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_karthus";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_karthus") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 「不死」挂多久、多久续一次（一直挂着，化成灵体前不断）。
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;
/// 灵体的隐身每隔多久续一次（放技能、攻击可能让隐身断掉）。
pub const HIDE_EVERY: usize = 30;
/// 灵体里该放的技能（Q 好了、射程里有敌方英雄，或值得放的 R）这么多 tick 还没放出来，就现形 `REVEAL_T` tick 再试
/// （2026-11-01 的日志：灵体按了 50 tick 的 Q，Q 一直好着、塔里克就在射程里，一下都没放出来，原因不明）。
pub const STUCK_T: usize = 20;
pub const REVEAL_T: usize = 20;

fn sn(x: &str) -> String {
    format!("league_karthus_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KARTHUS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_karthus.log");
        }
    }
    PathBuf::from("league_karthus.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the game, 2026-10-12)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 计算（单元测试用） =====================

/// 名字是不是本包的「不死」（别的「不死」在身上时不化成灵体）。
pub fn ours(name: &str) -> bool {
    name == sn("p_guard") || name == sn("p_spirit")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

/// 灵体第 `k` tick（0 起）该不该续隐身。
pub fn hide_due(k: usize) -> bool {
    k % HIDE_EVERY == 0
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_t: 420 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        if k == "p_t" {
            p.p_t = v;
        }
    }
    p
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

#[derive(Clone, Default)]
struct DeathDefied {
    p: Params,
    me: usize,
    /// 灵体开始的 tick（不是灵体时 None）。
    spirit: Option<usize>,
    /// 这条命还没化过灵体。
    ready: bool,
    /// 最后一个打他的（倒下时算击杀）。
    last_hit: Option<usize>,
    next_guard: usize,
    /// 这条命里见过他 1 血以上：游戏 0.6.4 开局第 0 tick 读到的血量是 0，那不是致命伤（赛恩附加包的教训）。
    alive_seen: bool,
    /// 灵体里有技能该放的起始 tick（`watch_casts`）。
    due_since: Option<usize>,
    /// 现形到这个 tick（之后照常隐身）。
    reveal_until: usize,
    /// 上一 tick Q、E、R 的剩余冷却：变大了就是放出来了。
    cds: [usize; 3],
}

impl DeathDefied {
    fn guard(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        if now < self.next_guard {
            return;
        }
        let mut g = BuffV1::timed(&sn("p_guard"), GUARD_T);
        g.undying = true;
        sim.entity_remove_buff(me, &sn("p_guard"));
        sim.add_buff(me, &g);
        self.next_guard = now + GUARD_EVERY;
    }

    fn rise(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        self.ready = false;
        self.spirit = Some(now);
        self.due_since = None;
        self.reveal_until = 0;
        self.cds = cooldowns(sim, me);
        sim.entity_remove_buff(me, &sn("p_guard"));
        let mut s = BuffV1::timed(&sn("p_spirit"), self.p.p_t + 2);
        s.undying = true;
        s.damaged_reduce = 100;
        s.cc_immune = true;
        sim.add_buff(me, &s);
        let hidden = sim.entity_set_invisible(me, self.p.p_t);
        sim.play_sfx(&sn("p"), me, &InputTargetV1::target(me));
        sim.play_sfx(&sn("vo_p"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("spirit") {
            wlog(format!("{} SPIRIT #{k}: lethal damage caught at 1 hp (last hit by {}), a spirit for {} ticks{}",
                         head(sim, me), self.last_hit.map_or_else(|| "-".to_string(), |a| who(sim, a)), self.p.p_t,
                         if hidden { "" } else { " (entity_set_invisible refused)" }));
        }
    }

    /// 灵体里技能放不出来的自诊断：该放的技能（灵体 AI 这时每 tick 都按）`STUCK_T` tick 没放出来，就现形 `REVEAL_T` tick
    /// （隐身挡住出手的话这时能放出来），记 SPIRIT STUCK；放出来时记 SPIRIT CAST（等了多久、是隐身还是现形时放的）。
    fn watch_casts(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let cds = cooldowns(sim, me);
        let cast = (0..3).find(|&i| cds[i] > self.cds[i]);
        self.cds = cds;
        let due = sim.get_entity(me).is_some_and(|e| {
            let at = (e.pos().0 as f64, e.pos().1 as f64);
            let power = e.stat().magic_power.max(0) as usize;
            let hits: Vec<(usize, usize, usize)> = foes_toll(sim, e.team(), power).iter().map(|f| (f.1, f.2, f.3)).collect();
            let q_due = ready(&e, SkillSlotV1::Skill)
                && foes_by_distance(sim, e.team(), at).first().is_some_and(|f| f.1 <= Q_RANGE);
            q_due || ready(&e, SkillSlotV1::Ult) && r_worth(RWhen::Spirit, &hits, power)
        });
        if let Some(i) = cast {
            if let Some(c) = counted("spirit_cast_seen") {
                wlog(format!("{} SPIRIT CAST #{c}: {} went {} ticks after it was due{}", head(sim, me), ["Q", "E", "R"][i],
                             self.due_since.map_or(0, |t| now - t),
                             if now < self.reveal_until { ", revealed" } else { ", hidden" }));
            }
            self.due_since = None;
        }
        if !due {
            self.due_since = None;
        } else if self.due_since.is_none() {
            self.due_since = Some(now);
        }
        if self.due_since.is_some_and(|t| now - t >= STUCK_T) && now >= self.reveal_until {
            let targetable = sim.get_entity(me).is_some_and(|e| e.is_targetable());
            let shown = sim.entity_set_invisible(me, 0);
            self.reveal_until = now + REVEAL_T;
            self.due_since = Some(now);
            if let Some(c) = counted("spirit_stuck") {
                wlog(format!("{} SPIRIT STUCK #{c}: a ready Q / R due for {STUCK_T} ticks did not go (targetable {targetable})                               - revealed for {REVEAL_T} ticks (entity_set_invisible 0: {shown})", head(sim, me)));
            }
        }
    }

    fn fall(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.spirit = None;
        sim.entity_remove_buff(me, &sn("p_spirit"));
        let (hp, _) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        let killer = self.last_hit.filter(|&a| sim.get_entity(a).is_some()).unwrap_or(me);
        sim.deal_damage_typed(killer, me, hp + 1000, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        if let Some(k) = counted("fall") {
            wlog(format!("{} FALL #{k}: the spirit's time is up, killed by {}", head(sim, me), who(sim, killer)));
        }
    }
}

impl StablePassive for DeathDefied {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.ready = true;
        self.spirit = None;
        self.last_hit = None;
        self.next_guard = 0;
        self.alive_seen = false;
        self.due_since = None;
        self.reveal_until = 0;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Karthus (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (hp, _) = e.hp();
        let now = sim.tick();
        if let Some(t0) = self.spirit {
            let k = now.saturating_sub(t0);
            self.watch_casts(sim, me, now);
            // re-hide on the period, not while revealed by `watch_casts`, and at once when the reveal ends
            let hide = now >= self.reveal_until && (hide_due(k) || now == self.reveal_until);
            // a Requiem begun as a spirit is not cut by the spirit's end (the user 2026-11-01: 「灵体状态下放大是不能被打断的」):
            // the fall waits for its channel (`r_ch` on him, R_CH ticks at most), the spirit kept on meanwhile
            let channel = buffs(sim, me).iter().any(|b| b.name() == sn("r_ch"));
            if k >= self.p.p_t && channel && k < self.p.p_t + R_CH {
                if k == self.p.p_t {
                    if let Some(c) = counted("spirit_holds") {
                        wlog(format!("{} SPIRIT HOLDS #{c}: Requiem still channelling as the spirit's time runs out",
                                     head(sim, me)));
                    }
                }
                let mut s = BuffV1::timed(&sn("p_spirit"), 3);
                s.undying = true;
                s.damaged_reduce = 100;
                s.cc_immune = true;
                sim.entity_remove_buff(me, &sn("p_spirit"));
                sim.add_buff(me, &s);
                if hide {
                    sim.entity_set_invisible(me, HIDE_EVERY + 2);
                }
            } else if k >= self.p.p_t {
                self.fall(sim, me);
            } else if k > 0 && hide {
                sim.entity_set_invisible(me, self.p.p_t - k);
            }
            return;
        }
        if !self.ready {
            return;
        }
        if hp > 1 {
            self.alive_seen = true;
        }
        self.guard(sim, me, now);
        if hp <= 1 && self.alive_seen {
            let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
            if !other_undying(&list) {
                self.rise(sim, me, now);
            }
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, _: usize, attacker: usize, damage: usize) {
        if damage > 0 && attacker != self.me && sim.get_entity(attacker).is_some() && self.spirit.is_none() {
            self.last_hit = Some(attacker);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if self.spirit.is_some() {
            if let Some(k) = counted("spirit_kill") {
                wlog(format!("{} SPIRIT KILL #{k}: {} killed by the spirit", head(sim, me), who(sim, victim)));
            }
        }
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.spirit = None;
        self.ready = false;
    }
}

// ===================== AI 钩子：灵体照常打，R 挑时机 =====================

/// Q 和 E 的施法距离（build_karthus.py 的 q_range / e_cast；单元测试核对）。R 是全图的。
pub const Q_RANGE: f64 = 80000.0;
pub const E_RANGE: f64 = 40000.0;

/// R 的伤害（build_karthus.py 的 r_dmg / r_ratio；单元测试核对）：魔法伤害，按目标魔抗 100 / (100 + mr) 打折
/// （league_ekko_rewind 的算法）。
pub const R_DMG: usize = 200;
pub const R_RATIO: usize = 75;
/// R 的引导（build_karthus.py 的 r_ch；单元测试核对）：灵体时开始的 R 引导完才倒下，最多等这么久。
pub const R_CH: usize = 180;
/// 泉水：离他这条命出生（开局、复活）的位置这么近以内。
pub const FOUNTAIN_R: f64 = 25000.0;
/// 灵体时放 R：能打死一个敌方英雄，或者把一个打到最大生命的这个百分比以下。
pub const SPIRIT_LOW: usize = 30;
/// 泉水里放 R：能打死一个，或者把至少 `FOUNTAIN_LOW_N` 个打到最大生命的 `FOUNTAIN_LOW`% 以下。
pub const FOUNTAIN_LOW: usize = 20;
pub const FOUNTAIN_LOW_N: usize = 2;
/// 拦下 R 时改成普攻的敌方英雄最远多远（再远就照游戏的 AI 原来的走路命令走，不穿过半张地图去打人）。
pub const HOLD_ATTACK_R: f64 = 70000.0;

/// R 打在魔抗 `mr` 的英雄身上的伤害（他的法强 `power`）。
pub fn r_damage(power: usize, mr: usize) -> usize {
    (R_DMG + power * R_RATIO / 100) * 100 / (100 + mr)
}

/// R 打完：(打死几个, 没死但剩的血不到最大生命 `low`% 的几个)。`foes`：每个敌方英雄的 (生命 + 护盾, 最大生命, 魔抗)。
pub fn r_toll(foes: &[(usize, usize, usize)], power: usize, low: usize) -> (usize, usize) {
    let mut kills = 0;
    let mut low_left = 0;
    for &(hp, max, mr) in foes {
        let d = r_damage(power, mr);
        if hp <= d {
            kills += 1;
        } else if (hp - d) * 100 <= low * max {
            low_left += 1;
        }
    }
    (kills, low_left)
}

/// 什么时候放 R（用户 2026-11-01：「最好改成死后放大 或者复活后在泉水放大 放大也要看敌方血量吧？不能乱放吧」）：死后的灵体里，
/// 或者复活后（回城后）在泉水里，而且要看敌方的血量；别的时候游戏的 AI 想放也拦下。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RWhen {
    Spirit,
    Fountain,
}

/// 这时候放 R 值不值：灵体里打死或打残（`SPIRIT_LOW`）一个就放；泉水里打死一个、或打残（`FOUNTAIN_LOW`）两个以上才放。
pub fn r_worth(when: RWhen, foes: &[(usize, usize, usize)], power: usize) -> bool {
    match when {
        RWhen::Spirit => {
            let (k, l) = r_toll(foes, power, SPIRIT_LOW);
            k + l >= 1
        }
        RWhen::Fountain => {
            let (k, l) = r_toll(foes, power, FOUNTAIN_LOW);
            k >= 1 || l >= FOUNTAIN_LOW_N
        }
    }
}

/// 正在施法（R 的引导也是）或被强制位移：不替 AI 按，按了会打断。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

fn busy(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| BUSY.iter().any(|k| k.code() == c.kind)))
}

fn spirit_on(e: &StableEntity<'_, '_>) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == sn("p_spirit"))
}

/// 这一格现在能按：解锁了，冷却好了（引擎的「输入合法」不看冷却，league_pyke 的教训）。
fn ready(e: &StableEntity<'_, '_>, slot: SkillSlotV1) -> bool {
    e.cooldown(slot).is_some_and(|c| c.unlocked && (c.remaining == 0 || c.charges > 0))
}

/// Q、E、R 的剩余冷却（读不到算 0）。
fn cooldowns(sim: &StableSim<'_>, me: usize) -> [usize; 3] {
    let e = sim.get_entity(me);
    [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult]
        .map(|s| e.as_ref().and_then(|e| e.cooldown(s)).map_or(0, |c| c.remaining))
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 敌队活着、选得中的英雄，近的在前。
fn foes_by_distance(sim: &StableSim<'_>, team: usize, at: (f64, f64)) -> Vec<(usize, f64)> {
    let mut out: Vec<(usize, f64)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && u.is_champion())
        .map(|u| (u.id(), dist(at, (u.pos().0 as f64, u.pos().1 as f64))))
        .collect();
    out.sort_by(|a, b| a.1.total_cmp(&b.1));
    out
}

/// 灵体这一 tick 按什么：R（全图，近的先）> Q > E（在施法距离内）> 普攻最近的英雄（够不着就走过去）。
/// `ready` 给出 R / Q / E 三格能不能按。返回 (格子, 目标)。
pub fn spirit_pick(foes: &[(usize, f64)], ready: [bool; 3]) -> Vec<(InputKindV1, usize)> {
    let mut out = Vec::new();
    if ready[0] {
        out.extend(foes.iter().map(|f| (InputKindV1::Ult, f.0)));
    }
    if ready[1] {
        out.extend(foes.iter().filter(|f| f.1 <= Q_RANGE).map(|f| (InputKindV1::Skill, f.0)));
    }
    if ready[2] {
        out.extend(foes.iter().filter(|f| f.1 <= E_RANGE).map(|f| (InputKindV1::Skill2, f.0)));
    }
    out.extend(foes.first().map(|f| (InputKindV1::Attack, f.0)));
    out
}

/// 敌队活着、选得中的英雄：(实体, 生命 + 护盾, 最大生命, 魔抗)，R 打完剩血最少的在前。
fn foes_toll(sim: &StableSim<'_>, team: usize, power: usize) -> Vec<(usize, usize, usize, usize)> {
    let mut out: Vec<(usize, usize, usize, usize)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && u.is_champion())
        .map(|u| (u.id(), u.hp().0 + u.shield(), u.hp().1.max(1), u.stat().magic_resistance.max(0) as usize))
        .collect();
    out.sort_by_key(|f| f.1.saturating_sub(r_damage(power, f.3)));
    out
}

/// 这一 tick 想怎么做（读 sim 时定好，读完再问游戏这些输入合不合法）。
enum Want {
    /// 灵体：按顺序试这些（R 只在值得时在里面）。
    Spirit(Vec<(InputKindV1, usize)>),
    /// 泉水里放 R：按顺序试这些目标；(打死几个, 打残几个)。
    Fountain(Vec<usize>, (usize, usize)),
    /// 游戏的 AI 想放 R，这时候不放：改按这些（Q、E、近处的普攻），都不行就照它原来的走路命令。
    Hold(Vec<(InputKindV1, usize)>),
}

/// 游戏的 AI 看他 1 血就跑（`run_away_input`）或回城，灵体 7 秒白白浪费：灵体时换成放技能、打人。R 只在灵体或泉水里、
/// 敌方血量够低时放（`r_worth`），别的时候游戏的 AI 想放就拦下。
#[derive(Clone, Default)]
struct SpiritAi {
    /// 他这条命出生的位置（泉水）：开局和每次复活后第一次看到他活着时记下。
    home: Option<(f64, f64)>,
    alive: bool,
    /// 游戏的 AI 最近一次下的走路命令：拦下它想放的 R 时照着走。
    last_move: Option<InputV1>,
}

impl StablePlayerAi for SpiritAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:spirit_ai")
    }

    /// 在 league_ult_press（100）之后：灵体时由本钩子说了算。
    fn priority(&self) -> i32 {
        105
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let was = base.and_then(|b| InputKindV1::from_code(b.kind));
        if was == Some(InputKindV1::Move) {
            self.last_move = base;
        }
        let (want, names, line, spot) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                self.alive = false;
                return None;
            }
            let at = (me.pos().0 as f64, me.pos().1 as f64);
            if !self.alive || self.home.is_none() {
                self.home = Some(at);
                self.alive = true;
            }
            if busy(&me) {
                return None;
            }
            let spirit = spirit_on(&me);
            let in_home = self.home.is_some_and(|h| dist(at, h) <= FOUNTAIN_R);
            if !spirit && !in_home && was != Some(InputKindV1::Ult) {
                return None; // nothing of ours to decide this tick
            }
            let power = me.stat().magic_power.max(0) as usize;
            let toll = foes_toll(&sim, me.team(), power);
            let hits: Vec<(usize, usize, usize)> = toll.iter().map(|f| (f.1, f.2, f.3)).collect();
            let r_ready = ready(&me, SkillSlotV1::Ult);
            let foes = foes_by_distance(&sim, me.team(), at);
            let qe = [ready(&me, SkillSlotV1::Skill), ready(&me, SkillSlotV1::Skill2)];
            let want = if spirit {
                Want::Spirit(spirit_pick(&foes, [r_ready && r_worth(RWhen::Spirit, &hits, power), qe[0], qe[1]]))
            } else if in_home && r_ready && r_worth(RWhen::Fountain, &hits, power) {
                Want::Fountain(toll.iter().map(|f| f.0).collect(), r_toll(&hits, power, FOUNTAIN_LOW))
            } else if was == Some(InputKindV1::Ult) {
                let near: Vec<(usize, f64)> = foes.iter().copied().filter(|f| f.1 <= HOLD_ATTACK_R).collect();
                Want::Hold(spirit_pick(&near, [false, qe[0], qe[1]]))
            } else {
                return None;
            };
            let names: HashMap<usize, String> = foes.iter().map(|f| (f.0, who(&sim, f.0))).collect();
            (want, names, head(&sim, me.id()), me.pos())
        };
        let name = |t: usize| names.get(&t).cloned().unwrap_or_default();
        let first_valid = |ctx: &StableAiContext<'_>, cands: Vec<(InputKindV1, usize)>| {
            cands.into_iter().find_map(|(k, t)| {
                let input = InputV1::action(k, InputTargetV1::target(t));
                ctx.is_valid_input(&input).then_some((k, t, input))
            })
        };
        match want {
            Want::Spirit(cands) => {
                let (kind, t, input) = first_valid(ctx, cands)?;
                if was == Some(kind) {
                    return None;
                }
                let tag = if kind == InputKindV1::Attack { "spirit_attack" } else { "spirit_cast" };
                if let Some(k) = counted(tag) {
                    wlog(format!("{line} SPIRIT AI #{k}: {:?} on {} (the game's AI: {})", kind, name(t),
                                 was.map_or_else(|| "none".to_string(), |w| format!("{w:?}"))));
                }
                Some(input)
            }
            Want::Fountain(targets, (kills, low)) => {
                let (_, t, input) = first_valid(ctx, targets.into_iter().map(|t| (InputKindV1::Ult, t)).collect())?;
                if let Some(k) = counted("r_fountain") {
                    wlog(format!("{line} R FOUNTAIN #{k}: Requiem from the fountain on {} - {kills} would die, {low} left \
                                  under {FOUNTAIN_LOW}%", name(t)));
                }
                Some(input)
            }
            Want::Hold(cands) => {
                let instead = first_valid(ctx, cands);
                let input = instead.map(|i| i.2).or(self.last_move).filter(|i| ctx.is_valid_input(i));
                if let Some(k) = counted("r_held") {
                    wlog(format!("{line} R HELD #{k}: the game's AI wanted Requiem away from the fountain and alive - {}",
                                 match (&instead, &input) {
                                     (Some((kind, t, _)), _) => format!("{kind:?} on {} instead", name(*t)),
                                     (None, Some(_)) => "its last walk instead".to_string(),
                                     _ => "standing instead".to_string(),
                                 }));
                }
                Some(input.unwrap_or_else(|| InputV1::move_to(spot.0, spot.1)))
            }
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Karthus: Death Defied's spirit) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:death_defied"), DeathDefied::default());
    module.add_player_input_ai(SpiritAi::default());
    host.log(LogLevel::Info, "league_karthus loaded (Death Defied's spirit, casting while a spirit).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn only_someone_elses_undying_holds_the_spirit_back() {
        let l = |v: &[(&str, bool)]| v.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        assert!(!other_undying(&l(&[("league_karthus_p_guard", true)])));
        assert!(!other_undying(&l(&[("league_karthus_p_spirit", true), ("league_karthus_e_on", false)])));
        assert!(other_undying(&l(&[("league_karthus_p_guard", true), ("league_soraka_w_guard", true)])));
    }

    #[test]
    fn the_veil_is_renewed() {
        assert!(hide_due(30));
        assert!(!hide_due(31));
    }

    #[test]
    fn params_parse() {
        assert_eq!(parse_params(r#"{"p_t":420}"#), Params::default());
        assert_eq!(parse_params(r#"{"p_t":300}"#).p_t, 300);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_karthus.py");
        let src = std::fs::read_to_string(path).expect("build_karthus.py");
        let d = Params::default();
        assert!(src.contains(&format!("\"p_t\": {}", d.p_t)), "p_t is not {} in build_karthus.P", d.p_t);
        assert!(src.contains(&format!("\"q_range\": {}", Q_RANGE as usize)), "q_range is not {Q_RANGE}");
        assert!(src.contains(&format!("\"e_cast\": {}", E_RANGE as usize)), "e_cast is not {E_RANGE}");
        assert!(src.contains(&format!("\"r_dmg\": {R_DMG}, \"r_ratio\": {R_RATIO}")), "r_dmg / r_ratio are not {R_DMG} / {R_RATIO}");
        assert!(src.contains(&format!("\"r_ch\": {R_CH}")), "r_ch is not {R_CH}");
    }

    #[test]
    fn requiem_waits_for_low_enemies() {
        // 300 AP: 200 + 225 = 425 raw; 25 magic resist -> 340
        assert_eq!(r_damage(300, 0), 425);
        assert_eq!(r_damage(300, 25), 340);
        let foes = [(300, 1500, 25), (900, 1500, 25), (2000, 2500, 0)];
        // the first dies; the second is left at 560 of 1500 (37 %); the third at 1575 of 2500
        assert_eq!(r_toll(&foes, 300, 20), (1, 0));
        assert_eq!(r_toll(&foes, 300, 40), (1, 1));
        assert!(r_worth(RWhen::Spirit, &foes, 300));
        assert!(r_worth(RWhen::Fountain, &foes, 300));
        // nobody low: never from the fountain, never as a spirit
        let healthy = [(1400, 1500, 25), (2400, 2500, 0)];
        assert!(!r_worth(RWhen::Spirit, &healthy, 300));
        assert!(!r_worth(RWhen::Fountain, &healthy, 300));
        // one left at 25 %: enough for the spirit, the fountain wants two under 20 % (or a kill)
        let one = [(715, 1500, 25), (2400, 2500, 0)];
        assert!(r_worth(RWhen::Spirit, &one, 300));
        assert!(!r_worth(RWhen::Fountain, &one, 300));
        let two = [(600, 1500, 25), (600, 1500, 25)];
        assert!(r_worth(RWhen::Fountain, &two, 300));
    }

    #[test]
    fn the_spirit_casts_r_then_q_then_e_then_attacks() {
        let foes = [(7, 20000.0), (8, 60000.0), (9, 500000.0)];
        let k = |v: Vec<(InputKindV1, usize)>| v.iter().map(|c| (c.0.code(), c.1)).collect::<Vec<_>>();
        let all = spirit_pick(&foes, [true, true, true]);
        assert_eq!(k(all)[..4], [(InputKindV1::Ult.code(), 7), (InputKindV1::Ult.code(), 8), (InputKindV1::Ult.code(), 9),
                                 (InputKindV1::Skill.code(), 7)]);
        // nothing ready: the nearest champion is attacked (walked to when out of reach)
        assert_eq!(k(spirit_pick(&foes, [false; 3])), [(InputKindV1::Attack.code(), 7)]);
        // Q only in its range, E only in its own
        let q = spirit_pick(&foes, [false, true, true]);
        assert_eq!(k(q), [(InputKindV1::Skill.code(), 7), (InputKindV1::Skill.code(), 8),
                          (InputKindV1::Skill2.code(), 7), (InputKindV1::Attack.code(), 7)]);
        assert!(spirit_pick(&[], [true; 3]).is_empty());
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_guard", "p_spirit", "p", "vo_p"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
