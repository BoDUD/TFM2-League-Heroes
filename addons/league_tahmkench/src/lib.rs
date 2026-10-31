//! 塔姆附加包（用户选「主包数据 + 附加包」，2026-10-15）：主包数据做不到的几件事。
//!
//! `mod.override_info` 把主包的塔姆换成 `override/` 里的副本（tools/kit/build_tahmkench.py 的 native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_tahmkench:skin`（参数在英雄数据的 `passive.params` 里）；
//! - 普攻、W 命中英雄叠层调本包的 `league_tahmkench:taste`，Q 命中英雄调 `league_tahmkench:lash`，不再走主包「数他自己命中
//!   次数」的阶梯；没有主包的固定减伤（厚实表皮由本包按真实伤害做）；
//! - W、R 都是普通的点目标施放，目标由本包的 AI 钩子挑（或者不放）；R 的吞下本身还是数据（放逐只有数据能做）：一个只落在队友
//!   身上的探针、一个只落在敌方英雄身上的探针，各自带着那一边的效果，并调 `league_tahmkench:devour` 记下吞了谁。
//!
//! - **培养品味按每个英雄记层**：层数是挂在敌方英雄身上的 buff `league_tahmkench_t_mark`（`entity_stack_buff`，每层 `hold`
//!   tick、叠一层就全部刷新），最多 3 层；头顶的鱼标记 `t_pip1..3` 跟着层数画。Q 打中 3 层的英雄：R 好了就留着层给 R 吞，
//!   否则眩晕 `q_stun` tick 并吃掉层数。
//! - **厚实表皮是真的灰色生命**：受到的伤害存 `store`%（最多最大生命的一半）；3 秒没挨英雄打就慢慢回成生命；被两名以上敌方英雄
//!   围住（`e_near` 以内）或生命低于 40% 时，把存的灰色生命加 `e_sh` + `e_sh_ap`% 法强变成护盾（`e_t` tick，冷却 `e_cd`）。
//! - **大快朵颐灵活判断**（用户：「塔姆的R救队友的时候灵活判断 别乱放」）：AI 要放 R 时，先看身边 `R_ALLY_R` 以内的队友——生命
//!   低于 35% 且附近有敌方英雄，或 1 秒内掉了四分之一以上生命，或被控住且身边有两个敌方英雄——挑生命最低的吞；没有就看近身
//!   `R_REACH` 以内有没有 3 层的敌方英雄；都没有就不放（改成普攻）。吞着队友时他往己方后撤，吞着敌人时往队友那边走；吐出的
//!   一刻把人放到他身边（队友放在他背后，敌人放在他前面）。
//! - **深渊潜航看时机**（「W也别乱放 看好时机」）：要有队友在身边；目标被控住（一个队友就够）或身边两个以上队友；落点附近的
//!   敌方英雄不多于身边队友加一；他自己生命不低于 30%。不满足就不放（改成普攻或回到队友身边）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_tahmkench.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_tahmkench";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.5";
const HERO: &str = "league_tahmkench";

// ===================== 数值（主包 build_tahmkench.P） =====================

/// R：AI 放 R 的距离（r_range）、吞敌人的近身距离（r_reach）、看队友的距离（r_ally_r）。
pub const R_RANGE: f64 = 50_000.0;
pub const R_REACH: f64 = 30_000.0;
pub const R_ALLY_R: f64 = 40_000.0;
/// W：射程（w_range）、看身边队友的距离（w_ally_r）。
pub const W_RANGE: f64 = 70_000.0;
pub const W_ALLY_R: f64 = 50_000.0;
/// 队友「附近有敌人」的距离、落点附近数敌人的距离、吞着人时走多远。
pub const NEAR: f64 = 40_000.0;
pub const LANDING: f64 = 30_000.0;
pub const WALK: f64 = 30_000.0;
/// 吐出时离他多远。
pub const SPIT: f64 = 9_000.0;
/// 队友危险：生命低于这个 %，或 BURST_TICKS 里掉了 BURST % 以上。
pub const LOW_PCT: usize = 35;
pub const BURST: usize = 25;
pub const BURST_TICKS: usize = 60;
/// W：他自己的生命至少这个 %。
pub const W_SELF_PCT: usize = 30;
/// 灰色生命：多久没挨英雄打开始回、每 tick 回存量的几分之一、最多存最大生命的几成。
pub const CALM: usize = 180;
pub const MEND: usize = 60;
pub const STORE_CAP_PCT: usize = 50;
/// 厚实表皮：生命低于这个 % 也转护盾；存量至少这么多才转。
pub const SKIN_LOW_PCT: usize = 40;
pub const SKIN_MIN: usize = 60;

fn tk(x: &str) -> String {
    format!("league_tahmkench_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TAHMKENCH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_tahmkench.log");
        }
    }
    PathBuf::from("league_tahmkench.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
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

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub fn pct(hp: usize, max: usize) -> usize {
    if max == 0 { 0 } else { hp * 100 / max }
}

/// 从 `from` 朝着离开 `away` 的方向走 `len`（`away` 和 `from` 重合时原地）。
pub fn step_away(from: (f64, f64), away: (f64, f64), len: f64) -> (f64, f64) {
    let d = dist(from, away);
    if d <= 0.0 {
        return from;
    }
    (from.0 + (from.0 - away.0) / d * len, from.1 + (from.1 - away.1) / d * len)
}

/// 一组点的中心。
pub fn centre(pts: &[(f64, f64)]) -> Option<(f64, f64)> {
    if pts.is_empty() {
        return None;
    }
    let n = pts.len() as f64;
    Some((pts.iter().map(|p| p.0).sum::<f64>() / n, pts.iter().map(|p| p.1).sum::<f64>() / n))
}

/// 一名队友的情况（AI 挑吞谁）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Mate {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: usize,
    pub max: usize,
    /// 最近 BURST_TICKS 里最高的生命。
    pub peak: usize,
    pub cc: bool,
}

/// 这名队友危险吗（附近 NEAR 以内的敌方英雄数 `foes_near`）：返回原因。
pub fn in_danger(m: &Mate, foes_near: usize) -> Option<&'static str> {
    if foes_near == 0 {
        return None;
    }
    if pct(m.hp, m.max) < LOW_PCT {
        return Some("LOW");
    }
    if m.peak > m.hp && (m.peak - m.hp) * 100 >= BURST * m.max {
        return Some("BURST");
    }
    if m.cc && foes_near >= 2 {
        return Some("HELD");
    }
    None
}

/// W 的时机：身边队友数、目标被控住吗、落点附近的敌方英雄数、他自己的生命 %。
pub fn dive_ok(allies: usize, held: bool, foes_at_landing: usize, my_pct: usize) -> bool {
    allies >= 1 && (held || allies >= 2) && foes_at_landing <= allies + 1 && my_pct >= W_SELF_PCT
}

/// 存进灰色生命多少（`store`%），不超过上限。
pub fn stored(grey: usize, damage: usize, store: usize, cap: usize) -> usize {
    (grey + damage * store / 100).min(cap)
}

// ===================== 小工具 =====================

fn count_buff(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count())
}

/// 硬控（击飞、晕眩、定身、嘲讽、恐惧、魅惑、被强制位移）：「被控住」的队友才值得吞、被控住的目标才值得潜过去接。不是
/// `cc_count() > 0`：游戏把正在播的施法动作也记成一种控制（`CcKindV1::Animation`），谁在放技能都算「被控」，大招和 W 的
/// 时机就松了（卡莉丝塔附加包 10-16 查出：她每一跳都被自己的动作叫停）。
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

fn hard_cc(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
}

/// 他身上免疫控制的 buff 的名字（希维尔的法术护盾 `league_sivir_e_shroud` 这类），没有就 None：有的话大快朵颐吞不了他
/// （英雄联盟里法术护盾挡下 R）。
fn immune_by(sim: &StableSim<'_>, id: usize) -> Option<String> {
    let e = sim.get_entity(id)?;
    let names: Vec<String> = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.cc_immune)
        .map(|b| b.name().to_string()).collect();
    (!names.is_empty()).then(|| names.join(" "))
}

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

/// 一队的英雄（活着、能被选中）：(id, 位置)。`mine` = 和 `team` 同队，否则敌队。
fn champions(sim: &StableSim<'_>, team: usize, mine: bool) -> Vec<(usize, (f64, f64))> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if (u.team() == team) != mine || !u.is_alive() || !u.is_targetable() || !u.is_champion() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((u.id(), (x as f64, y as f64)));
    }
    out
}

fn within(list: &[(usize, (f64, f64))], at: (f64, f64), r: f64) -> usize {
    list.iter().filter(|c| dist(c.1, at) <= r).count()
}

fn player_of(sim: &StableSim<'_>, champ: usize) -> Option<usize> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find(|p| p.champion().is_some_and(|c| c.id() == champ)).map(|p| p.id())
}

fn ult_ready(sim: &StableSim<'_>, champ: usize) -> bool {
    let Some(pid) = player_of(sim, champ) else { return false };
    sim.get_player(pid).and_then(|p| p.cooldowns()).is_some_and(|c| c.3 == 0)
}

// ===================== 共享状态 =====================

#[derive(Clone, Copy, Debug)]
struct Carry {
    target: usize,
    ally: bool,
    release: usize,
    /// the devour's tick
    since: usize,
}

/// Ticks after the devour before a targetable carried unit counts as out of his belly (the banish lands with the cast).
pub const OUT_GRACE: usize = 2;

/// 每份模拟的塔姆一个编号，出生时由被动挂在他身上（buff `league_tahmkench_sim:<编号>`，没有数值、没有画面），吞人、吐人、
/// AI 钩子按他身上的它找到同一份记录。游戏同时跑同一局的几份模拟（两份预模拟 + 画面那份），实体编号一样：按编号记时一份
/// 吐出就删了别份的记录，那几份的人原地出来、塔姆不再往回走，画面那场和预模拟算的就不是同一场了（2026-10-16 第 588 场日志：
/// 画面里吞下的墨菲特、布隆没有 SPIT）。莫德凯撒、蛮王附加包的做法。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
const SIM_TAG: &str = "league_tahmkench_sim:";

/// (这份模拟的编号, 塔姆的 entity id) -> 他嘴里的人。
static CARRY: LazyLock<Mutex<HashMap<(u64, usize), Carry>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// (这份模拟的编号, 英雄 id) -> 最近几次记下的 (tick, 生命)（每 10 tick 一次，留 BURST_TICKS 以内的）。
static HP_LOG: LazyLock<Mutex<HashMap<(u64, usize), Vec<(usize, usize)>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// 参数（英雄数据的 passive.params；钩子和效果也要读）。
static PARAMS: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn params() -> Params {
    *PARAMS.lock().unwrap_or_else(|e| e.into_inner())
}

/// The number the passive hung on `tahm` when he spawned in this sim (0: none).
pub fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    names.into_iter().find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn sim_of(sim: &StableSim<'_>, tahm: usize) -> u64 {
    sim.get_entity(tahm).map_or(0, |e| sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string())))
}

fn peak_hp(tag: u64, id: usize, now: usize, hp: usize) -> usize {
    let log = HP_LOG.lock().unwrap_or_else(|e| e.into_inner());
    log.get(&(tag, id)).map_or(hp, |v| v.iter().filter(|s| s.0 + BURST_TICKS >= now).map(|s| s.1).max().unwrap_or(hp).max(hp))
}

// ===================== 培养品味 =====================

fn set_pips(sim: &mut StableSim<'_>, target: usize, n: usize, hold: usize) {
    for k in 1..=3 {
        sim.entity_remove_buff(target, &tk(&format!("t_pip{k}")));
    }
    for k in 1..=n.min(3) {
        sim.add_buff(target, &BuffV1::timed(&tk(&format!("t_pip{k}")), hold));
    }
}

fn stacks(sim: &StableSim<'_>, target: usize) -> usize {
    count_buff(sim, target, &tk("t_mark")).min(3)
}

fn clear_stacks(sim: &mut StableSim<'_>, target: usize) {
    sim.entity_remove_buff(target, &tk("t_mark"));
    set_pips(sim, target, 0, 1);
}

/// 叠一层（最多 3），返回现在的层数。
fn add_stack(sim: &mut StableSim<'_>, target: usize, hold: usize) -> usize {
    let mark = tk("t_mark");
    let n = (count_buff(sim, target, &mark) + 1).min(3);
    sim.entity_remove_buff(target, &mark);
    for _ in 0..n {
        sim.add_buff(target, &BuffV1::timed(&mark, hold));
    }
    set_pips(sim, target, n, hold);
    n
}

fn taste(sim: &mut StableSim<'_>, me: usize, target: usize, lash: bool) {
    let Some(t) = sim.get_entity(target) else { return };
    if !t.is_alive() || !t.is_champion() {
        return;
    }
    let p = params();
    let before = stacks(sim, target);
    if lash && before >= 3 {
        if ult_ready(sim, me) {
            add_stack(sim, target, p.hold);
            if let Some(n) = counted("keep") {
                wlog(format!("{} KEEP #{n} {}: 3 stacks kept for Devour (ult ready)", head(sim, me), who(sim, target)));
            }
            return;
        }
        clear_stacks(sim, target);
        sim.apply_cc(target, &CcV1::stun(p.q_stun as u64));
        let at = InputTargetV1::target(target);
        sim.play_view_effect(&tk("q_stun"), me, &at, 0, 0, 0);
        sim.play_sfx(&tk("q_stun"), me, &at);
        if let Some(n) = counted("stun") {
            wlog(format!("{} STUN #{n} {}: 3 stacks eaten, stunned {} ticks", head(sim, me), who(sim, target), p.q_stun));
        }
        return;
    }
    let n = add_stack(sim, target, p.hold);
    if n == 3 && before < 3 {
        let at = InputTargetV1::target(target);
        sim.play_sfx(&tk("p_stack"), me, &at);
    }
    if let Some(k) = counted("stack") {
        wlog(format!("{} STACK #{k} {} -> {n} ({})", head(sim, me), who(sim, target), if lash { "Q" } else { "attack/W" }));
    }
}

struct Taste;

impl StableEffectType for Taste {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target) {
            taste(sim, caster, input.target_id, false);
        }
    }
}

struct Lash;

impl StableEffectType for Lash {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target) {
            taste(sim, caster, input.target_id, true);
        }
    }
}

// ===================== 大快朵颐：记下吞了谁 =====================

struct Devour;

impl StableEffectType for Devour {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        let (Some(me), Some(t)) = (sim.get_entity(caster), sim.get_entity(target)) else { return };
        let ally = me.team() == t.team();
        let p = params();
        let hold = if ally { p.r_ally_t } else { p.r_t };
        if !ally {
            clear_stacks(sim, target);
        }
        let since = sim.tick() as usize;
        let release = since + hold;
        CARRY.lock().unwrap_or_else(|e| e.into_inner()).insert((sim_of(sim, caster), caster), Carry { target, ally, release, since });
        if let Some(n) = counted("devour") {
            wlog(format!("{} DEVOUR #{n} {} {} for {hold} ticks", head(sim, caster), if ally { "ALLY" } else { "ENEMY" },
                         who(sim, target)));
        }
    }
}

// ===================== 大快朵颐：免疫控制的敌人吞不了 =====================

/// 吞敌人的探针落下时先调（副本：`league_tahmkench:guard`）：他免疫控制（希维尔开着法术护盾，用户 2026-10-29：「希维尔开盾时
/// 塔姆可以吞」）就在塔姆身上挂 1 tick 的 `r_blocked`，数据接着跳过放逐、伤害和 `devour`。大招照样用掉（英雄联盟里法术护盾
/// 挡下技能也一样）。
struct Guard;

impl StableEffectType for Guard {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        let Some(by) = immune_by(sim, target) else { return };
        sim.add_buff(caster, &BuffV1::timed(&tk("r_blocked"), 1));
        if let Some(n) = counted("blocked") {
            wlog(format!("{} R BLOCKED #{n}: {} immune to crowd control ({by}), not eaten", head(sim, caster), who(sim, target)));
        }
    }
}

// ===================== 被动：厚实表皮、吐出、生命记录 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub hold: usize,
    pub q_stun: usize,
    pub r_t: usize,
    pub r_ally_t: usize,
    pub e_sh: usize,
    pub e_sh_ap: usize,
    pub e_t: usize,
    pub e_near: usize,
    pub e_cd: usize,
    pub store: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { hold: 300, q_stun: 75, r_t: 150, r_ally_t: 150, e_sh: 160, e_sh_ap: 80, e_t: 150, e_near: 35_000,
                 e_cd: 720, store: 30 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "hold" => p.hold = v,
            "q_stun" => p.q_stun = v,
            "r_t" => p.r_t = v,
            "r_ally_t" => p.r_ally_t = v,
            "e_sh" => p.e_sh = v,
            "e_sh_ap" => p.e_sh_ap = v,
            "e_t" => p.e_t = v,
            "e_near" => p.e_near = v,
            "e_cd" => p.e_cd = v,
            "store" => p.store = v,
            _ => {}
        }
    }
    p
}

#[derive(Clone, Default)]
struct Skin {
    p: Params,
    grey: usize,
    last_hit: usize,
    ready_at: usize,
    mended: usize,
    /// This sim's number (`SIM_TAG`), drawn at his first spawn.
    sim_no: u64,
}

impl Skin {
    fn record_hp(&self, sim: &StableSim<'_>, team: usize) {
        let now = sim.tick() as usize;
        if now % 10 != 0 {
            return;
        }
        let mut log = HP_LOG.lock().unwrap_or_else(|e| e.into_inner());
        for (id, _) in champions(sim, team, true) {
            let Some(e) = sim.get_entity(id) else { continue };
            let v = log.entry((self.sim_no, id)).or_default();
            v.push((now, e.hp().0));
            v.retain(|s| s.0 + BURST_TICKS + 10 >= now);
        }
    }

    fn spit(&self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let now = sim.tick() as usize;
        let Some(c) = CARRY.lock().unwrap_or_else(|e| e.into_inner()).get(&(self.sim_no, me)).copied() else { return };
        // out early: game 0.6.5 fixed a seal staying on a unit with Tenacity after its crowd control (Taoist's ult) - a
        // banish cut short by Tenacity the same way lets the carried one out before the release; put down now, by him,
        // not later from where it was swallowed
        let early = now > c.since + OUT_GRACE && sim.get_entity(c.target).is_some_and(|t| t.is_alive() && t.is_targetable());
        if now < c.release && !early {
            return;
        }
        let Some(t) = sim.get_entity(c.target) else {
            CARRY.lock().unwrap_or_else(|e| e.into_inner()).remove(&(self.sim_no, me));
            return;
        };
        // a banished unit does not move: wait until the banish is over (a few ticks at most), then put it down once
        if !t.is_targetable() && now < c.release + 5 {
            return;
        }
        CARRY.lock().unwrap_or_else(|e| e.into_inner()).remove(&(self.sim_no, me));
        let Some(at) = alive_at(sim, me) else { return };
        let foes: Vec<(f64, f64)> = champions(sim, team, false).into_iter().map(|c| c.1).collect();
        let front = centre(&foes).unwrap_or((at.0 + 1.0, at.1));
        // an ally goes down behind him (away from the enemies), an enemy in front of him
        let spot = if c.ally { step_away(at, front, SPIT) } else { step_away(at, front, -SPIT) };
        let ok = sim.entity_set_pos(c.target, spot.0.max(0.0) as u64, spot.1.max(0.0) as u64);
        if let Some(n) = counted("spit") {
            wlog(format!("{} SPIT #{n} {} {} at ({:.0}, {:.0}){}{}", head(sim, me), if c.ally { "ALLY" } else { "ENEMY" },
                         who(sim, c.target), spot.0, spot.1, if ok { "" } else { " (the host kept it where it was)" },
                         if now < c.release { format!(" early: out of the banish {} ticks in (Tenacity?)", now - c.since) }
                         else { String::new() }));
        }
    }

    fn mend_and_shield(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let now = sim.tick() as usize;
        let Some(e) = sim.get_entity(me).filter(|e| e.is_alive()) else { return };
        let (hp, max) = e.hp();
        let ap = e.stat().magic_power;
        let Some(at) = alive_at(sim, me) else { return };
        // out of champion fights: the grey health comes back as health
        if self.grey > 0 && now >= self.last_hit + CALM {
            let h = (self.grey / MEND).max(1).min(self.grey);
            sim.entity_set_hp(me, (hp + h).min(max));
            self.grey -= h;
            self.mended += h;
        }
        // surrounded or low: the store becomes a shield
        if now < self.ready_at || self.grey < SKIN_MIN {
            return;
        }
        let foes = champions(sim, team, false);
        let near = within(&foes, at, self.p.e_near as f64);
        if near >= 2 || (near >= 1 && pct(hp, max) < SKIN_LOW_PCT) {
            let amount = self.grey + self.p.e_sh + self.p.e_sh_ap * ap / 100;
            sim.entity_add_shield(me, amount, self.p.e_t);
            let tgt = InputTargetV1::target(me);
            sim.play_view_effect(&tk("e_shield"), me, &tgt, 0, 0, 0);
            sim.play_sfx(&tk("e_shield"), me, &tgt);
            if let Some(n) = counted("skin") {
                wlog(format!("{} SHIELD #{n} {amount} ({} grey, {near} enemy champions near, {}% hp)", head(sim, me),
                             self.grey, pct(hp, max)));
            }
            self.grey = 0;
            self.ready_at = now + self.p.e_cd;
        }
    }
}

impl StablePassive for Skin {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
        *PARAMS.lock().unwrap_or_else(|e| e.into_inner()) = self.p;
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.grey = 0;
        self.ready_at = 0;
        if self.sim_no == 0 {
            self.sim_no = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim_no);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Tahm Kench (player {player}, team {team}, sim {}), {:?}", head(sim, me),
                     self.sim_no, self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(team) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.team()) else { return };
        self.record_hp(sim, team);
        self.spit(sim, me, team);
        self.mend_and_shield(sim, me, team);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        if damage == 0 {
            return;
        }
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        self.grey = stored(self.grey, damage, self.p.store, max * STORE_CAP_PCT / 100);
        if sim.get_entity(attacker).is_some_and(|a| a.is_champion()) {
            self.last_hit = sim.tick() as usize;
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.grey = 0;
        // dying with someone in his belly spits them out where he fell
        let c = CARRY.lock().unwrap_or_else(|e| e.into_inner()).remove(&(self.sim_no, me));
        if let (Some(c), Some(at)) = (c, sim.get_entity(me).map(|e| e.pos())) {
            sim.entity_set_pos(c.target, at.0, at.1);
        }
    }
}

// ===================== AI 钩子：R 吞谁、W 什么时候放、吞着人往哪走 =====================

#[derive(Clone, Default)]
struct Ai;

enum Plan {
    Keep,
    Ult(usize, String),
    /// What he does instead of the held cast, and a walk toward its target for when the game refuses the attack (out of
    /// reach, in an action): never the AI's own cast (2026-10-30: 37 of 39 devours went through a hold that way, 13 of
    /// them on allies in no danger).
    Instead(InputV1, InputV1, String),
}

impl Ai {
    fn plan(&self, sim: &StableSim<'_>, me: usize, kind: InputKindV1, current: Option<usize>) -> Option<Plan> {
        let e = sim.get_entity(me)?;
        let team = e.team();
        let (hp, max) = e.hp();
        let at = (e.pos().0 as f64, e.pos().1 as f64);
        let now = sim.tick() as usize;
        let foes = champions(sim, team, false);
        let mates: Vec<(usize, (f64, f64))> = champions(sim, team, true).into_iter().filter(|c| c.0 != me).collect();
        // carrying someone: walk (an ally away from the enemies, an enemy to his team)
        let tag = sim_of(sim, me);
        let carry = CARRY.lock().unwrap_or_else(|e| e.into_inner()).get(&(tag, me)).copied();
        if let Some(c) = carry {
            let enemies: Vec<(f64, f64)> = foes.iter().map(|f| f.1).collect();
            let friends: Vec<(f64, f64)> = mates.iter().map(|m| m.1).collect();
            let to = if c.ally {
                centre(&enemies).map_or(at, |f| step_away(at, f, WALK))
            } else {
                centre(&friends).unwrap_or(at)
            };
            let walk = InputV1::move_to(to.0.max(0.0) as u64, to.1.max(0.0) as u64);
            return Some(Plan::Instead(walk, walk,
                                      format!("CARRY {}", if c.ally { "ally: back off" } else { "enemy: to the team" })));
        }
        match kind {
            InputKindV1::Ult => {
                // 1. an ally in danger, the lowest first
                let mut best: Option<(Mate, &'static str)> = None;
                // not one immune to crowd control: the swallow (a banish) does not hold him and R is wasted (0.1.5, the
                // 2026-11-01 log: Sivir's spell shield up, spat out 3 ticks in)
                for &(id, p) in mates.iter().filter(|m| dist(at, m.1) <= R_ALLY_R && immune_by(sim, m.0).is_none()) {
                    let Some(u) = sim.get_entity(id) else { continue };
                    let (h, mx) = u.hp();
                    let m = Mate { id, at: p, hp: h, max: mx, peak: peak_hp(tag, id, now, h), cc: hard_cc(&u) };
                    if let Some(why) = in_danger(&m, within(&foes, p, NEAR)) {
                        if best.is_none_or(|b| pct(m.hp, m.max) < pct(b.0.hp, b.0.max)) {
                            best = Some((m, why));
                        }
                    }
                }
                if let Some((m, why)) = best {
                    return Some(Plan::Ult(m.id, format!("ALLY {} ({why}, {}% hp)", who(sim, m.id), pct(m.hp, m.max))));
                }
                // 2. an enemy champion with three stacks close by, not immune to crowd control (a spell shield up)
                let full = foes.iter().filter(|f| dist(at, f.1) <= R_REACH + 8_000.0 && stacks(sim, f.0) >= 3)
                    .filter(|f| immune_by(sim, f.0).is_none())
                    .min_by(|a, b| dist(at, a.1).partial_cmp(&dist(at, b.1)).unwrap_or(std::cmp::Ordering::Equal));
                if let Some(&(id, _)) = full {
                    return Some(Plan::Ult(id, format!("ENEMY {} (3 stacks)", who(sim, id))));
                }
                Some(self.instead(at, current, &foes, &mates, "R HELD: nobody in danger, no 3 stacks"))
            }
            InputKindV1::Skill2 => {
                let t = current?;
                let tp = alive_at(sim, t)?;
                let allies = within(&mates, at, W_ALLY_R);
                let held = sim.get_entity(t).is_some_and(|u| hard_cc(&u));
                let crowd = within(&foes, tp, LANDING);
                if dive_ok(allies, held, crowd, pct(hp, max)) {
                    return Some(Plan::Keep);
                }
                let why = format!("W HELD: {allies} allies, target {}held, {crowd} enemies at the landing, {}% hp",
                                  if held { "" } else { "not " }, pct(hp, max));
                Some(self.instead(at, current, &foes, &mates, &why))
            }
            _ => None,
        }
    }

    /// Instead of a held cast: attack what the AI aimed at (or the nearest enemy champion), else walk back to the team.
    fn instead(&self, at: (f64, f64), current: Option<usize>, foes: &[(usize, (f64, f64))],
               mates: &[(usize, (f64, f64))], why: &str) -> Plan {
        let target = current.and_then(|c| foes.iter().find(|f| f.0 == c)).or_else(|| {
            foes.iter().min_by(|a, b| dist(at, a.1).partial_cmp(&dist(at, b.1)).unwrap_or(std::cmp::Ordering::Equal))
        });
        if let Some(&(t, p)) = target {
            return Plan::Instead(InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)),
                                 InputV1::move_to(p.0.max(0.0) as u64, p.1.max(0.0) as u64), why.to_string());
        }
        let to = centre(&mates.iter().map(|m| m.1).collect::<Vec<_>>()).unwrap_or(at);
        let walk = InputV1::move_to(to.0.max(0.0) as u64, to.1.max(0.0) as u64);
        Plan::Instead(walk, walk, why.to_string())
    }
}

impl StablePlayerAi for Ai {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ai")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        let kind = InputKindV1::from_code(b.kind)?;
        let current = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id);
        let player = ctx.player_id();
        let (plan, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let carrying = CARRY.lock().unwrap_or_else(|e| e.into_inner()).contains_key(&(sim_of(&sim, me.id()), me.id()));
            if !carrying && !matches!(kind, InputKindV1::Ult | InputKindV1::Skill2) {
                return None;
            }
            let plan = self.plan(&sim, me.id(), kind, current)?;
            (plan, head(&sim, me.id()))
        };
        match plan {
            Plan::Keep => {
                if let Some(k) = counted("dive") {
                    wlog(format!("{line} W KEPT #{k} (allies near, a good moment)"));
                }
                None
            }
            Plan::Ult(id, why) => {
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(id));
                if !ctx.is_valid_input(&input) {
                    if let Some(k) = counted("refused") {
                        wlog(format!("{line} R {why}: refused by the game #{k}"));
                    }
                    return None;
                }
                if let Some(k) = counted("pick") {
                    wlog(format!("{line} R PICK #{k} {why}"));
                }
                Some(input)
            }
            Plan::Instead(input, walk, why) => {
                let input = if ctx.is_valid_input(&input) { input } else { walk };
                // one count each: CARRY (thousands a launch) hid every R HELD after the first 40
                let kind = if why.starts_with("CARRY") { "carry" } else if why.starts_with("R ") { "r held" } else { "w held" };
                if let Some(k) = counted(kind) {
                    wlog(format!("{line} {why} #{k}"));
                }
                Some(input)
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Tahm Kench: An Acquired Taste per champion, real grey health, Devour and Abyssal Dive at the right moment) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:skin"), Skin::default());
    module.add_native_effect(format!("{ID}:taste"), Taste);
    module.add_native_effect(format!("{ID}:lash"), Lash);
    module.add_native_effect(format!("{ID}:devour"), Devour);
    // 0.1.3: an enemy immune to crowd control (a spell shield up) is not eaten
    module.add_native_effect(format!("{ID}:guard"), Guard);
    module.add_player_input_ai(Ai);
    host.log(LogLevel::Info, "league_tahmkench loaded (stacks per champion, grey health, Devour and Abyssal Dive timing).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    fn mate(hp: usize, peak: usize, cc: bool) -> Mate {
        Mate { id: 1, at: (0.0, 0.0), hp, max: 1000, peak, cc }
    }

    #[test]
    fn the_sim_tag_reads_back() {
        let names = vec!["league_tahmkench_t_mark".to_string(), format!("{SIM_TAG}7")];
        assert_eq!(sim_tag(names.into_iter()), 7);
        assert_eq!(sim_tag(vec!["league_mordekaiser_sim:3".to_string()].into_iter()), 0);
    }

    #[test]
    fn who_is_in_danger() {
        assert_eq!(in_danger(&mate(300, 300, false), 1), Some("LOW"));
        assert_eq!(in_danger(&mate(300, 300, false), 0), None, "no enemy near: no save");
        assert_eq!(in_danger(&mate(600, 900, false), 1), Some("BURST"));
        assert_eq!(in_danger(&mate(800, 900, false), 1), None);
        assert_eq!(in_danger(&mate(900, 900, true), 2), Some("HELD"));
        assert_eq!(in_danger(&mate(900, 900, true), 1), None, "held by one enemy is not enough");
        assert_eq!(in_danger(&mate(1000, 1000, false), 3), None, "a full ally among enemies is not saved");
    }

    #[test]
    fn when_to_dive() {
        assert!(!dive_ok(0, true, 1, 100), "never alone");
        assert!(dive_ok(1, true, 1, 100));
        assert!(!dive_ok(1, false, 1, 100), "one ally: only on a held champion");
        assert!(dive_ok(2, false, 3, 100));
        assert!(!dive_ok(2, false, 4, 100), "too many enemies where he lands");
        assert!(!dive_ok(3, true, 1, 20), "too low himself");
    }

    #[test]
    fn grey_health_is_capped() {
        assert_eq!(stored(0, 200, 30, 500), 60);
        assert_eq!(stored(480, 200, 30, 500), 500);
    }

    #[test]
    fn walking_away() {
        let p = step_away((10.0, 0.0), (0.0, 0.0), 5.0);
        assert!((p.0 - 15.0).abs() < 1e-9 && p.1.abs() < 1e-9);
        assert_eq!(centre(&[(0.0, 0.0), (4.0, 2.0)]), Some((2.0, 1.0)));
        assert_eq!(centre(&[]), None);
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"e_cd":720,"e_near":35000,"e_sh":160,"e_sh_ap":80,"e_t":150,"hold":300,"q_stun":75,"r_ally_t":150,"r_t":150,"store":30}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_tahmkench.py");
        let src = std::fs::read_to_string(path).expect("build_tahmkench.py");
        for (key, v) in [("r_range", R_RANGE as usize), ("r_reach", R_REACH as usize), ("r_ally_r", R_ALLY_R as usize),
                         ("w_range", W_RANGE as usize), ("w_ally_r", W_ALLY_R as usize)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_tahmkench.P");
        }
        let d = Params::default();
        for (key, v) in [("p_hold", d.hold), ("q_stun", d.q_stun), ("r_t", d.r_t), ("r_ally_t", d.r_ally_t),
                         ("e_sh", d.e_sh), ("e_sh_ap", d.e_sh_ap), ("e_t", d.e_t), ("e_near", d.e_near),
                         ("e_cd", d.e_cd), ("e_store", d.store)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_tahmkench.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["t_mark", "t_pip1", "t_pip2", "t_pip3", "q_stun", "e_shield", "p_stack", "r_blocked"] {
            assert!(tk(x).len() <= BUFF_NAME_CAP);
        }
    }

    /// The copy's enemy probe asks league_tahmkench:guard before anything of the swallow (2026-10-29: a spell shield
    /// up, Devour ate Sivir anyway): the guard first, then the switch on r_blocked holding the banish and the devour.
    #[test]
    fn the_guard_comes_before_the_banish() {
        let copy = include_str!("../override/league_tahmkench.data_champion").replace('\r', "");
        let probe = &copy[copy.find("\"name\": \"league_tahmkench_r_enemy_go\"").expect("no enemy probe in the copy")..];
        let guard = probe.find("\"effect_ref\": \"league_tahmkench:guard\"").expect("the enemy probe has no guard");
        let switch = probe.find("\"buff_name\": \"league_tahmkench_r_blocked\"").expect("no switch on r_blocked");
        let banish = probe.find("\"type\": \"Banish\"").expect("no banish");
        let devour = probe.find("\"effect_ref\": \"league_tahmkench:devour\"").expect("no devour");
        assert!(guard < switch && switch < banish && banish < devour);
    }
}
