//! 拉莫斯附加包（用户 2026-10-19：技能方案 A，做附加包）。主包保持纯数据；`mod.override_info` 把主包的拉莫斯换成 `override/` 里的
//! 副本（`make_override.py` 用 tools/kit/build_rammus.py 的 `native=1` 生成：被动换成本包的 `league_rammus:shell`，普攻不带锥刺甲壳的
//! 魔法伤害，尖刺防御不按百分比反伤，Q 只缩成球、挂上 `league_rammus_q_ball`，普攻、技能1、技能2 的说明开头加【扩展包】），本包补
//! 数据做不到的几件事，0.2.0（2026-11-21）起照英雄联盟 V26.21：
//!
//! - **锥刺甲壳 = 护甲、魔抗换攻击力**：他身上一直挂着 `league_rammus_p_ad`，攻击力 = `ad_arm`% 总护甲 + `ad_mr`% 总魔抗，护甲、魔抗
//!   一变（升级、装备、尖刺防御）就跟着改，面板上看得到。主包数据读不到护甲，还是普攻附带魔法伤害。
//! - **尖刺防御只回敬普攻他的人**：蜷着的时候（数据的守望挂 `league_rammus_w_on`）被普攻打中，攻击者受到 `w_hit` + `w_hit_arm`% 护甲 +
//!   `w_hit_mr`% 魔抗 的魔法伤害（下一 tick 付），同一下普攻只算一次；技能、持续伤害、防御塔不算。`on_damaged` 不给伤害类型，按攻击者
//!   的冷却认（`champion_blow`）。主包还是反弹受到伤害的百分比。
//! - **动力冲刺照英雄联盟滚**：副本的 Q 缩成球后挂 `q_ball`（最多 6 秒），本包让他越滚越快：从 +0 开始，每秒加 `q_acc`（1 级
//!   `acc0`、12 级 `acc1`，万分之一）的移速，一 tick 一 tick 加；他照常走向目标，身边 `Q_TOUCH` 内一有敌方单位（不算防御塔）就挂
//!   1 tick 的 `q_go`，数据里每 tick 看一次的守望把它变成撞击（伤害、击退、眩晕、减速、他弹出球来）。滚着普攻也算撞上；游戏的 AI
//!   滚着想放 E 改成普攻（英雄联盟滚着不能放 E）。主包里 Q 是一次冲到目标的冲刺。
//!   0.2.1（用户 2026-11-21：「改，滚久一点」）：以前 99 次滚球 85 次不到半秒就撞上（AI 在 30000–45000 才开球，路上碰到小兵就停），
//!   局内看不出在滚。现在 AI 钩子从 `Q_FAR`（100000）外就开球（目标在敌方塔下不开），副本 Q 的射程跟着放到 100000；滚向英雄时一路
//!   的小兵碾过去不停，AI 让他打别的、往别处走改成冲向那个英雄（他身上挂 `league_rammus_q_at:<号>`）。
//! - 放动力冲刺、冲天猛撞时尖刺防御收起、滚着的时候不蜷、双抗「固定 + 总量 %」都是数据做的，两个包一样（主包的守望还只在动力冲刺
//!   冷却时蜷）。
//! - **整身换形态**（`view.rs`，游戏 0.6.4 起的 Windows 版）：滚着的时候站着、走着、挨打都是滚动的刺球（`b_*`），尖刺防御开着的时候是蜷着的防御
//!   姿势（`c_*`）。
//!
//! 数字在副本的 `passive.params` 里（`configure` 读），下面的常量是默认值，`make_override.py` 核对它们和 build_rammus.P 一样。
//! 旧存档里的 0.1.x 副本（参数里没有 `p_ad_arm`）照旧：锥刺甲壳是数据里的 `league_rammus:spikes`，反伤是数据的百分比，本包不再加攻击力、
//! 不回敬（日志 `OLD COPY`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rammus.log`，每次启动游戏重写，上一次的留在 .prev.log：`ROLL`（缩成球、
//! 撞上谁 / 滚完没撞上、滚了多久多快）、`SHELL`（锥刺甲壳按多少护甲魔抗给了多少攻击力）、`CURL` / `RETURN`（尖刺防御开关、回敬了谁多少）、
//! `E HELD`、`OPEN`、`Q HELD`（AI 钩子）、`FORM`（画面里换形态），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_rammus";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_rammus") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 滚球（副本的 Q 挂的）和尖刺防御（数据的守望挂的）：view.rs 照它们换画面。
pub const BALL: &str = "league_rammus_q_ball";
pub const CURL: &str = "league_rammus_w_on";
/// 撞上的信号（本包挂 1 tick，副本 Q 的守望看到就撞）和本包给的加速。
pub const GO: &str = "league_rammus_q_go";
pub const RUSH: &str = "league_rammus_q_rush";
/// 锥刺甲壳的攻击力 buff（0.2.0）。
pub const SHELL_AD: &str = "league_rammus_p_ad";
/// 锥刺甲壳：攻击力 = 总护甲 `P_AD_ARM`% + 总魔抗 `P_AD_MR`%（build_rammus.P 的 p_ad_arm / p_ad_mr）。英雄联盟 V25.12 起是 15% + 15%，
/// 可这个游戏的坦克护甲、魔抗低得多（10 分钟里他平均约 165），15% 只给平均 25 攻击力，比 0.1.x 每下普攻约 59 的魔法伤害少一大截，
/// 经典引擎里副本的击杀差 +3.80 → +2.40；35% 平均约 60 攻击力，+3.85。
pub const P_AD_ARM: usize = 35;
pub const P_AD_MR: usize = 35;
/// 尖刺防御回敬一下普攻：`W_HIT` + 护甲 `W_HIT_ARM`% + 魔抗 `W_HIT_MR`%（P 的 w_hit / w_hit_arm / w_hit_mr；英雄联盟 15 + 10% + 10%）。
pub const W_HIT: usize = 20;
pub const W_HIT_ARM: usize = 10;
pub const W_HIT_MR: usize = 10;
/// 尖刺防御开着的 tick 数（P 的 w_t）：比它短就是被 Q / R 提前收起来了（日志）。
pub const W_T: usize = 420;
/// 动力冲刺：最多滚几 tick（P 的 q_ball_t，英雄联盟 6 秒）；每秒加多少移速（万分之一：1 级 `Q_ACC0`，`MAX_LEVEL` 级 `Q_ACC1`，
/// 英雄联盟 1–18 级 25% → 40.83%，摊到这个游戏的 1–12 级；P 的 q_acc0 / q_acc1）；两个身子的边缘隔多近算撞上（P 的 q_touch）。
/// 0.1.1：q_touch 以前是 26000、从他的中心量到对方的边（≥ 普攻射程），AI 又在差不多这个距离放 Q，11-04 的日志里 40 次撞击 38 次
/// 「after 0 ticks」、每次 ROLL over 都是「0 rolled」——球从来没滚过；现在量两个身子之间的空隙。
pub const Q_BALL_T: usize = 360;
pub const Q_ACC0: usize = 2_500;
pub const Q_ACC1: usize = 4_083;
pub const MAX_LEVEL: usize = 12;
pub const Q_TOUCH: usize = 3_000;
/// 单位半径读不到时用的值。
pub const BODY: f64 = 6_000.0;
/// Q 的目标（副本的 Q 给目标挂的，蜷起那一 tick 已经贴着他的敌人里只有它算撞上）。
pub const AIM: &str = "league_rammus_q_aim";
/// 副本 Q 的施法标记（AI 钩子不在它和尖刺防御期间开球）。
pub const BUSY: &str = "league_rammus_busy";
/// AI 钩子 `league_rammus:open`（0.1.1）：最近的敌方英雄在 `Q_OPEN` 到 `Q_FAR` 之间、Q 好了就先滚过去，不等游戏的 AI 走到普攻
/// 距离才按。0.2.1（用户 2026-11-21：「改，滚久一点」）：以前只到 Q 的射程 45000，11-21 的日志里 99 次滚球 85 次不到半秒就撞上
/// （中位数 8 tick），局内看不出在滚；现在从 100000 外就滚过去，副本 Q 的射程跟着放到 `Q_FAR`（build_rammus.P 的 q_far）。
/// 目标在敌方防御塔 `TOWER_GUARD` 以内不开（不滚进塔下）。
pub const Q_OPEN: u64 = 30_000;
pub const Q_RANGE: u64 = 45_000;
pub const Q_FAR: u64 = 100_000;
pub const TOWER_GUARD: f64 = 80_000.0;
/// 0.2.1：滚向英雄时，被动给他挂 `league_rammus_q_at:<英雄的实体号>`（滚完摘掉）：一路碰到的小兵不算撞上（碾过去），AI 钩子把
/// 滚着时打别的、往别处走的命令改成冲向这个英雄。滚向小兵 / 野怪（游戏的 AI 拿 Q 清兵）照旧碰到谁撞谁。
pub const AT: &str = "league_rammus_q_at:";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RAMMUS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_rammus.log");
        }
    }
    PathBuf::from("league_rammus.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
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

// ===================== 规则（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 副本 `passive.params` 里本包用的数（build_rammus.P）。`new` 是 0.2.0 起的副本：旧副本（没有 `p_ad_arm`）的锥刺甲壳和反伤在数据里。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub ad_arm: usize,
    pub ad_mr: usize,
    pub w_hit: usize,
    pub w_hit_arm: usize,
    pub w_hit_mr: usize,
    pub w_t: usize,
    pub acc0: usize,
    pub acc1: usize,
    pub ball_t: usize,
    pub new: bool,
}

impl Default for Params {
    fn default() -> Self {
        Params { ad_arm: P_AD_ARM, ad_mr: P_AD_MR, w_hit: W_HIT, w_hit_arm: W_HIT_ARM, w_hit_mr: W_HIT_MR, w_t: W_T,
                 acc0: Q_ACC0, acc1: Q_ACC1, ball_t: Q_BALL_T, new: true }
    }
}

/// 从被动参数（排好序的整数 JSON，如 `{"p_ad_arm":15,"q_acc0":2500}`）读一个值。
pub fn param(json: &str, key: &str) -> Option<usize> {
    let at = json.find(&format!("\"{key}\""))?;
    let rest = json[at + key.len() + 2..].trim_start().strip_prefix(':')?.trim_start();
    let end = rest.find(|c: char| !c.is_ascii_digit()).unwrap_or(rest.len());
    rest[..end].parse().ok()
}

pub fn parse_params(json: &str) -> Params {
    let d = Params::default();
    let g = |k: &str, v: usize| param(json, k).unwrap_or(v);
    Params {
        ad_arm: g("p_ad_arm", d.ad_arm),
        ad_mr: g("p_ad_mr", d.ad_mr),
        w_hit: g("w_hit", d.w_hit),
        w_hit_arm: g("w_hit_arm", d.w_hit_arm),
        w_hit_mr: g("w_hit_mr", d.w_hit_mr),
        w_t: g("w_t", d.w_t),
        acc0: g("q_acc0", d.acc0),
        acc1: g("q_acc1", d.acc1),
        ball_t: g("q_ball_t", d.ball_t),
        new: param(json, "p_ad_arm").is_some(),
    }
}

impl Params {
    /// 锥刺甲壳的攻击力：总护甲、总魔抗各取一个百分比。
    pub fn shell_ad(&self, armour: usize, mr: usize) -> usize {
        (self.ad_arm * armour + self.ad_mr * mr) / 100
    }

    /// 尖刺防御回敬一下普攻的魔法伤害（他这时的总护甲、总魔抗）。
    pub fn w_return(&self, armour: usize, mr: usize) -> usize {
        self.w_hit + (self.w_hit_arm * armour + self.w_hit_mr * mr) / 100
    }

    /// 他这一级每秒加多少移速（万分之一）：1 级 acc0，MAX_LEVEL 级 acc1，中间线性。
    pub fn q_acc(&self, level: usize) -> usize {
        let l = level.clamp(1, MAX_LEVEL) - 1;
        self.acc0 + self.acc1.saturating_sub(self.acc0) * l / (MAX_LEVEL - 1)
    }

    /// 滚了 t tick 时的加速（移速 %）：从 0 开始，一 tick 加 q_acc / 60，四舍五入；滚满 ball_t 就不再加。
    pub fn rush(&self, t: usize, level: usize) -> i32 {
        ((self.q_acc(level) * t.min(self.ball_t) + 3_000) / 6_000) as i32
    }
}

/// 两个身子碰上了（0.1.1）：中心相距 `d`、半径 `r_me` / `r_u`，边缘的空隙不超过 Q_TOUCH。读不到的半径（0）按 `BODY`。
pub fn body(r: u64) -> f64 {
    if r == 0 { BODY } else { r as f64 }
}

pub fn contact(d: f64, r_me: f64, r_u: f64) -> bool {
    d - r_me - r_u <= Q_TOUCH as f64
}

/// AI 钩子该从这个距离开球：Q_OPEN 到 Q_FAR 之间（近的游戏 AI 自己会按）。
pub fn open_from(d2: u64) -> bool {
    d2 > Q_OPEN * Q_OPEN && d2 <= Q_FAR * Q_FAR
}

/// 目标离最近的敌方（对他来说是敌方，也就是我方）防御塔不到 TOWER_GUARD：不开球滚过去。
pub fn guarded(target: Pt, towers: &[Pt]) -> bool {
    towers.iter().any(|t| dist(*t, target) < TOWER_GUARD)
}

/// 滚着的时候这个单位碰到了算不算撞上：滚向英雄（`at_champion`）时小兵不算（碾过去），别的都算。
pub fn stops_ball(at_champion: bool, minion: bool) -> bool {
    !(at_champion && minion)
}

/// 滚向的英雄挂在他身上的标记名。
pub fn at_buff(id: usize) -> String {
    format!("{AT}{id}")
}

/// 从他身上的 buff 名认出滚向的英雄。
pub fn at_of(name: &str) -> Option<usize> {
    name.strip_prefix(AT)?.parse().ok()
}

// ===================== 尖刺防御：认出普攻 =====================

/// 打中他的这一下是什么。`on_damaged` 只给攻击者和伤害量（物品的 `on_damaged_ex` 才有类型），所以按攻击者的冷却认：游戏在一个
/// 动作开始时把这个槽的冷却拉满，`cooltime - remaining` 就是它出手了几 tick。
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Blow {
    /// 普攻，这下普攻是第 `.0` tick 出手的（同一下普攻打出的几段伤害只算一次）。
    Attack(usize),
    /// 技能、持续伤害：攻击者的普攻没在冷却，或者普攻之后又放了技能。
    Skill,
    /// 防御塔、水晶（英雄联盟不算）。
    Tower,
    /// 读不到攻击者的冷却（ABI 10 以前的游戏）：不算。
    Unknown,
}

/// 一个技能槽离上次放过了几 tick；冷却没在走、没解锁、充能的（剩余时间不是按一次施放算）是 None。
pub fn since_cast(c: &CooldownV1) -> Option<usize> {
    (c.unlocked && c.remaining > 0 && c.max_charges <= 1).then(|| c.cooltime.saturating_sub(c.remaining))
}

/// 英雄打中他（`now` 这一 tick）：普攻在冷却、普攻之后没放过技能，就是这一下普攻。
/// 认错的情形：普攻打别人时自己的持续伤害、慢弹落在他身上算成普攻（同一下普攻最多一次）；远程普攻在飞的时候攻击者放了技能，
/// 这一下算成技能。
pub fn champion_blow(now: usize, attack: Option<CooldownV1>, skills: &[Option<CooldownV1>]) -> Blow {
    let Some(a) = attack else { return Blow::Unknown };
    if a.remaining == 0 {
        return Blow::Skill;
    }
    let since = a.cooltime.saturating_sub(a.remaining);
    if skills.iter().flatten().filter_map(since_cast).any(|s| s <= since) {
        return Blow::Skill;
    }
    Blow::Attack(now.saturating_sub(since))
}

/// 小兵、野怪、召唤物只会普攻；防御塔、水晶不算。
pub fn unit_blow(now: usize, kind: Option<EntityKindV1>, tower: bool) -> Blow {
    if tower || matches!(kind, Some(EntityKindV1::Tower | EntityKindV1::Nexus)) {
        Blow::Tower
    } else {
        Blow::Attack(now)
    }
}

/// 同一个攻击者两次回敬之间至少隔几 tick（不是英雄的：普攻间隔读不到时）。
pub const UNIT_GAP: usize = 30;
/// 记下的回敬留多久（tick）。
pub const STRUCK_KEEP: usize = 600;

/// 这一下普攻（攻击者 `foe`，第 `start` tick 出手）还没回敬过吗：英雄看出手的 tick（差 2 tick 以内算同一下），别的单位看离上次
/// 回敬过了没有 `gap` tick。`struck` 是 (攻击者, 出手 tick)。
pub fn fresh_blow(struck: &[(usize, usize)], foe: usize, start: usize, champion: bool, gap: usize) -> bool {
    !struck.iter().any(|&(id, at)| {
        id == foe && if champion { at.abs_diff(start) <= 2 } else { start < at + gap.max(1) }
    })
}

/// AI 想在他滚着的时候放 E（英雄联盟滚着不能放 E）：改成对同一个人普攻（滚着普攻就是撞上去）。
pub fn holds_e(kind: u32, ball: bool) -> bool {
    ball && kind == InputKindV1::Skill2.code()
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 他身上本包关心的几个 buff（一次扫完）。
#[derive(Clone, Copy, Default)]
struct Marks {
    ball: bool,
    go: bool,
    curl: bool,
    ad: Option<i32>,
}

fn marks(sim: &StableSim<'_>, id: usize) -> Marks {
    let mut m = Marks::default();
    let Some(e) = sim.get_entity(id) else { return m };
    for b in (0..e.buff_count()).filter_map(|i| e.buff_at(i)) {
        match b.name() {
            BALL => m.ball = true,
            GO => m.go = true,
            CURL => m.curl = true,
            SHELL_AD => m.ad = Some(m.ad.unwrap_or(0) + b.attack),
            _ => {}
        }
    }
    m
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

fn kind_name(kind: Option<EntityKindV1>, champion: bool) -> &'static str {
    match kind {
        Some(EntityKindV1::Champion) => "champion",
        Some(EntityKindV1::Minion) => "minion",
        Some(EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen) => "monster",
        Some(EntityKindV1::Summon) => "summon",
        _ if champion => "champion",
        _ => "unit",
    }
}

// ===================== 旧副本的锥刺甲壳（普攻里的原生效果） =====================

/// 0.1.x 的副本普攻里调这个（15 + 30% 法强 + 15% 护甲 魔法伤害）。0.2.0 的副本不再调，留着给旧存档里的副本用。
fn spikes_hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(foe) = target_of(&input) else { return };
    if !sim.get_entity(foe).is_some_and(|e| e.is_alive()) {
        return;
    }
    let Some(st) = sim.get_entity(me).map(|e| e.stat()) else { return };
    let amount = 15 + 30 * st.magic_power / 100 + 15 * st.defence / 100;
    sim.deal_damage_typed(me, foe, amount, DamageTypeV1::Ap, AttackTypeV1::BaseAttack);
    if let Some(k) = counted("spikes") {
        wlog(format!("{} SPIKES (an old copy) #{foe}: armour {} AP {} -> {amount} magic #{k}", head(sim, me), st.defence,
                     st.magic_power));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动：锥刺甲壳、尖刺防御的回敬、动力冲刺的滚球 =====================

/// 欠着的一下回敬（`on_damaged` 里记下，下一 tick 的 `on_update` 付）。
#[derive(Clone, Copy, Debug)]
struct Owed {
    foe: usize,
    amount: usize,
    what: &'static str,
    /// 这下普攻出手了几 tick（日志）。
    since: usize,
}

/// 一次蜷起的账（CURL off 那行）。
#[derive(Clone, Debug, Default)]
struct CurlTally {
    since: usize,
    returned: usize,
    dealt: usize,
    champions: usize,
    minions: usize,
    monsters: usize,
    others: usize,
    skills: usize,
    towers: usize,
    repeats: usize,
}

#[derive(Clone, Default)]
struct Shell {
    p: Params,
    /// 这一次滚球已经滚了几 tick（没在滚是 None）。
    rolling: Option<usize>,
    /// 缩成球时的位置（日志里记滚了多远）。
    from: Option<Pt>,
    /// 蜷起那一 tick 就贴着他的敌人（不是 Q 的目标）：离开过才算撞（0.1.1）。
    skip: Vec<usize>,
    /// 0.2.1：这一次滚向的英雄（Q 的目标是英雄时），和一路碾过了几个小兵。
    at: Option<usize>,
    passed: Vec<usize>,
    /// 回敬过的普攻：(攻击者, 出手 tick)。
    struck: Vec<(usize, usize)>,
    owed: Vec<Owed>,
    /// 上一 tick 他蜷着吗（CURL on / off 两行；旧副本拿它记「OLD COPY 写过了」），和这次蜷起的账。
    curled: bool,
    tally: CurlTally,
}

impl Shell {
    /// 贴着他的敌方单位（不算防御塔、要能被选中）：`skip` 以外、算撞上的（`at_champion` 时小兵不算，0.2.1）空隙最小的
    /// (id, 空隙)，和贴着的全部，和贴着却碾过去的小兵。
    fn touching(sim: &StableSim<'_>, me: usize, skip: &[usize], at_champion: bool)
                -> (Option<(usize, f64)>, Vec<usize>, Vec<usize>) {
        let Some(e) = sim.get_entity(me) else { return (None, Vec::new(), Vec::new()) };
        let (team, at, r_me) = (e.team(), (e.pos().0 as f64, e.pos().1 as f64), body(e.radius() as u64));
        let mut best: Option<(usize, f64)> = None;
        let (mut all, mut passed) = (Vec::new(), Vec::new());
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable() {
                continue;
            }
            let r_u = body(u.radius() as u64);
            let d = dist((u.pos().0 as f64, u.pos().1 as f64), at);
            if !contact(d, r_me, r_u) {
                continue;
            }
            all.push(u.id());
            if !stops_ball(at_champion, u.kind() == Some(EntityKindV1::Minion)) {
                passed.push(u.id());
                continue;
            }
            let gap = d - r_me - r_u;
            if !skip.contains(&u.id()) && best.is_none_or(|b| gap < b.1) {
                best = Some((u.id(), gap));
            }
        }
        (best, all, passed)
    }

    /// 滚向的英雄还活着、看得见：一路的小兵碾过去（0.2.1）。
    fn at_champion(&self, sim: &StableSim<'_>, me: usize) -> bool {
        let Some(id) = self.at else { return false };
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return false };
        sim.get_entity(id).is_some_and(|u| u.is_alive() && u.is_targetable()) && sim.is_visible(team, id)
    }

    fn touched(&mut self, sim: &StableSim<'_>, me: usize) -> Option<(usize, f64)> {
        let at_champion = self.at_champion(sim, me);
        let (best, all, passed) = Self::touching(sim, me, &self.skip, at_champion);
        // the ones curled up against him count once they have been off him
        self.skip.retain(|id| all.contains(id));
        for id in passed {
            if !self.passed.contains(&id) {
                self.passed.push(id);
            }
        }
        best
    }

    /// 上一 tick 记下的回敬付掉。
    fn pay(&mut self, sim: &mut StableSim<'_>, me: usize) {
        for o in std::mem::take(&mut self.owed) {
            if !sim.get_entity(o.foe).is_some_and(|e| e.is_alive() && e.is_targetable()) {
                continue;
            }
            sim.deal_damage_typed(me, o.foe, o.amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
            if let Some(k) = counted("return") {
                // 英雄记上普攻出手到打中隔了几 tick（近战十来 tick，远程再加上飞的时间），别的单位没有这个数
                let when = if o.what == "champion" { format!(", its attack went out {} ticks before the hit", o.since) } else { String::new() };
                wlog(format!("{} RETURN #{} ({}{when}) <- {} magic #{k}", head(sim, me), o.foe, o.what, o.amount));
            }
        }
    }

    /// 锥刺甲壳：攻击力跟着护甲、魔抗走（死了 buff 会被清掉，活着的每一 tick 都对一遍）。
    fn shell(&mut self, sim: &mut StableSim<'_>, me: usize, on: Option<i32>) {
        let Some(st) = sim.get_entity(me).map(|e| e.stat()) else { return };
        let want = self.p.shell_ad(st.defence, st.magic_resistance) as i32;
        if on == Some(want) {
            return;
        }
        if on.is_some() {
            sim.entity_remove_buff(me, SHELL_AD);
        }
        let mut b = BuffV1::named(SHELL_AD);
        b.attack = want;
        sim.add_buff(me, &b);
        if let Some(k) = counted("shell") {
            let was = on.map_or_else(|| "none".to_string(), |v| format!("+{v}"));
            wlog(format!("{} SHELL armour {} MR {} -> +{want} attack (was {was}) #{k}", head(sim, me), st.defence,
                         st.magic_resistance));
        }
    }

    /// 尖刺防御开了、收了：各记一行（收的时候带上这次的账）。
    fn curl_log(&mut self, sim: &StableSim<'_>, me: usize, curled: bool) {
        let now = sim.tick();
        if curled && !self.curled {
            self.tally = CurlTally { since: now, ..CurlTally::default() };
            if let Some(k) = counted("curl") {
                let st = sim.get_entity(me).map(|e| e.stat()).unwrap_or_default();
                wlog(format!("{} CURL on: armour {} MR {} #{k}", head(sim, me), st.defence, st.magic_resistance));
            }
        } else if !curled && self.curled {
            let c = std::mem::take(&mut self.tally);
            if let Some(k) = counted("curl_off") {
                let lasted = now.saturating_sub(c.since);
                let short = if lasted + 2 < self.p.w_t { ", cut short (Powerball / Soaring Slam or death)" } else { "" };
                wlog(format!("{} CURL off after {lasted} ticks{short}: returned {} basic attacks for {} magic (champions {}, \
                              minions {}, monsters {}, others {}); not returned: {} skill or damage-over-time hits, {} tower \
                              hits, {} more hits of an attack already returned #{k}", head(sim, me), c.returned, c.dealt,
                             c.champions, c.minions, c.monsters, c.others, c.skills, c.towers, c.repeats));
            }
        }
        self.curled = curled;
    }
}

impl StablePassive for Shell {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.rolling = None;
        self.from = None;
        self.owed.clear();
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _player: usize, me: usize, attacker: usize, damage: usize) {
        if !self.p.new || damage == 0 || attacker == me || !has_buff(sim, me, CURL) {
            return;
        }
        let now = sim.tick();
        let (team, armour, mr) = {
            let Some(e) = sim.get_entity(me).filter(|e| e.is_alive()) else { return };
            let st = e.stat();
            (e.team(), st.defence, st.magic_resistance)
        };
        let Some(a) = sim.get_entity(attacker) else { return };
        if a.team() == team {
            return;
        }
        let (kind, champion) = (a.kind(), a.is_champion());
        let blow = if champion {
            let skills = [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].map(|s| a.cooldown(s));
            champion_blow(now, a.cooldown(SkillSlotV1::Attack), &skills)
        } else {
            unit_blow(now, kind, a.is_tower())
        };
        let gap = match a.attack_interval() {
            0 => UNIT_GAP,
            n => n.saturating_sub(2),
        };
        let what = kind_name(kind, champion);
        let c = &mut self.tally;
        let start = match blow {
            Blow::Attack(start) => start,
            Blow::Skill | Blow::Unknown => {
                c.skills += 1;
                return;
            }
            Blow::Tower => {
                c.towers += 1;
                return;
            }
        };
        if !fresh_blow(&self.struck, attacker, start, champion, gap) {
            c.repeats += 1;
            return;
        }
        self.struck.retain(|&(_, at)| at + STRUCK_KEEP > now);
        self.struck.push((attacker, start));
        let amount = self.p.w_return(armour, mr);
        c.returned += 1;
        c.dealt += amount;
        match what {
            "champion" => c.champions += 1,
            "minion" => c.minions += 1,
            "monster" => c.monsters += 1,
            _ => c.others += 1,
        }
        self.owed.push(Owed { foe: attacker, amount, what, since: now.saturating_sub(start) });
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        let m = if alive { marks(sim, me) } else { Marks::default() };
        if self.p.new {
            if alive {
                self.pay(sim, me);
                self.shell(sim, me, m.ad);
            } else {
                self.owed.clear();
            }
            self.curl_log(sim, me, alive && m.curl);
        } else if !self.curled {
            // 旧副本不走 curl_log，curled 借来记「这一个写过了」
            self.curled = true;
            if let Some(k) = counted("old copy") {
                wlog(format!("{} OLD COPY: this Rammus is a 0.1.x copy (no p_ad_arm in its params; a save from before \
                              0.2.0): Spiked Shell and the curl's reflect stay its data's, the ball rolls 0.2.0's way - refresh \
                              the save's hero copies #{k}", head(sim, me)));
            }
        }
        if !(alive && m.ball) {
            if let Some(t) = self.rolling.take() {
                sim.entity_remove_buff(me, RUSH);
                if let Some(id) = self.at.take() {
                    sim.entity_remove_buff(me, &at_buff(id));
                }
                if let Some(k) = counted("roll") {
                    let far = match (self.from, pos(sim, me)) {
                        (Some(a), Some(b)) => dist(a, b),
                        _ => 0.0,
                    };
                    let level = sim.get_entity(me).map_or(1, |e| e.level());
                    wlog(format!("{} ROLL over after {t} ticks ({:.1} s), {far:.0} rolled, up to +{}% speed, {} minions rolled                                   past #{k}", head(sim, me), t as f64 / 60.0, self.p.rush(t, level), self.passed.len()));
                }
            }
            return;
        }
        let t = match self.rolling {
            None => {
                self.from = pos(sim, me);
                // the enemies against him as he curls up (not Q's target) are no hit until they have been off him
                let (_, all, _) = Self::touching(sim, me, &[], false);
                self.skip = all.into_iter().filter(|&id| !has_buff(sim, id, AIM)).collect();
                // 0.2.1：Q 的目标是英雄就记下来（他身上挂 q_at:<号>，AI 钩子照它把他往那个英雄赶），一路的小兵碾过去
                self.passed.clear();
                self.at = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                    .find(|u| u.is_champion() && u.is_alive() && (0..u.buff_count()).filter_map(|j| u.buff_at(j)).any(|b| b.name() == AIM))
                    .map(|u| u.id());
                if let Some(id) = self.at {
                    sim.add_buff(me, &BuffV1::timed(&at_buff(id), self.p.ball_t + 2));
                }
                if let Some(k) = counted("roll") {
                    wlog(format!("{} ROLL curled up{}{} #{k}", head(sim, me),
                                 self.at.map_or(String::new(), |id| format!(" at champion #{id}")),
                                 if self.skip.is_empty() { String::new() } else { format!(", {} already against him", self.skip.len()) }));
                }
                0
            }
            Some(t) => t + 1,
        };
        self.rolling = Some(t);
        // faster and faster: one buff, its speed raised every tick (from +0, League's way)
        let level = sim.get_entity(me).map_or(1, |e| e.level());
        let mut b = BuffV1::timed(RUSH, 3);
        b.move_speed_mult = self.p.rush(t, level);
        sim.entity_remove_buff(me, RUSH);
        sim.add_buff(me, &b);
        if t % 24 == 12 {
            if let Some(at) = pos(sim, me) {
                sim.play_view_effect("league_rammus_q_dust", me, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
            }
        }
        if m.go {
            return;
        }
        if let Some((foe, d)) = self.touched(sim, me) {
            sim.add_buff(me, &BuffV1::timed(GO, 2));
            if let Some(k) = counted("hit") {
                let what = if sim.get_entity(foe).is_some_and(|e| e.is_champion()) { "champion" } else { "unit" };
                wlog(format!("{} ROLL hit #{foe} ({what}) after {t} ticks at +{}% speed (gap {d:.0}), {} minions rolled past #{k}",
                             head(sim, me), self.p.rush(t, level), self.passed.len()));
            }
        }
    }
}

// ===================== AI 钩子：从远处开球，滚着不放 E =====================

/// The AI's Powerball at an enemy champion already against him (0.1.2): the gap between their bodies within `Q_TOUCH`.
/// The ball would hit him on the tick it curls up and never roll (11-06's logs: 36 "ROLL hit ... after 0 ticks", each
/// followed by "ROLL over after 0 ticks, 0 rolled" - all the game AI's own Q, none after OPEN): an attack instead, Q kept
/// for a run-up (OPEN from `Q_OPEN`..`Q_RANGE`, or the AI's own Q from further off).
pub fn point_blank(champion: bool, d: f64, r_me: f64, r_u: f64) -> bool {
    champion && contact(d, r_me, r_u)
}

/// A Q HELD line at `now` for `target` starts a streak (`last`: the last hold's target and tick): one line a streak.
pub fn new_hold(last: Option<(usize, usize)>, target: usize, now: usize) -> bool {
    last.is_none_or(|(t, at)| t != target || now < at || now > at + HOLD_GAP)
}

/// Holds of the AI's Q at the same champion within this many ticks of the last are one streak (the AI asks again on its
/// judgement ticks).
pub const HOLD_GAP: usize = 60;

/// 游戏的 AI 在普攻距离附近才放 Q（11-04 的日志：撞击全在 0 tick）。这个钩子（0.1.1）：他活着、没在滚、没在施法 / 蜷着、
/// Q 解锁且冷却好了，AI 想普攻或走路（不在回城、放技能），最近的敌方英雄在 `Q_OPEN`..`Q_RANGE` 之间：改成对他放 Q。
/// 0.1.2：AI 自己对已经贴着他的敌方英雄放 Q（`point_blank`）改成普攻他，Q 留着助跑用。
/// 0.2.0：滚着的时候 AI 想放 E（英雄联盟滚着不能放 E）改成普攻同一个人：滚着普攻就是撞上去，撞完再嘲讽。
/// 蜷着时 AI 的 Q 照放（放 Q 会收起尖刺防御，英雄联盟也是这样）：经典引擎里试过蜷着时先压下 Q（改成普攻、够不着就走过去），
/// 他少了 Q 的眩晕、追着人走进人堆，死得更多，没留。
#[derive(Clone, Default)]
struct Open {
    recalling: bool,
    /// The last held Q: (its target, the tick) - the Q HELD line one a streak.
    held: Option<(usize, usize)>,
    /// 上一次滚着拦下 E：(目标, tick)，一串拦截记一行。
    e_held: Option<(usize, usize)>,
    /// 0.2.1：上一次滚着把 AI 的命令改成冲向滚向的英雄：(英雄, tick)，一串记一行。
    steered: Option<(usize, usize)>,
}

impl Open {
    /// The AI's Q at `target`: an attack on him instead when he is a champion against Rammus already (None: the AI's Q goes).
    fn hold_q(&mut self, ctx: &mut StableAiContext<'_>, target: usize) -> Option<InputV1> {
        let player = ctx.player_id();
        let (gap, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion().filter(|e| e.is_alive())?;
            let u = sim.get_entity(target).filter(|u| u.is_alive() && u.team() != me.team())?;
            let (r_me, r_u) = (body(me.radius() as u64), body(u.radius() as u64));
            let d = dist((me.pos().0 as f64, me.pos().1 as f64), (u.pos().0 as f64, u.pos().1 as f64));
            if !point_blank(u.is_champion(), d, r_me, r_u) {
                return None;
            }
            (d - r_me - r_u, head(&sim, me.id()))
        };
        let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(target));
        if !ctx.is_valid_input(&attack) {
            return None;
        }
        let now = ctx.tick();
        if new_hold(self.held, target, now) {
            if let Some(k) = counted("q held") {
                wlog(format!("{line} Q HELD: the AI's Powerball at #{target} against him (gap {gap:.0}) - attacking instead, \
                              Q kept for a run-up #{k}"));
            }
        }
        self.held = Some((target, now));
        Some(attack)
    }

    /// 滚向英雄的时候（他身上有 q_at:<号>），AI 让他打别的、往别处走：改成普攻那个英雄（滚过去撞他）。那个英雄死了、看不见，
    /// 或者 AI 本来就在打他：不管（None）。
    fn steer(&mut self, ctx: &mut StableAiContext<'_>, base: InputV1) -> Option<InputV1> {
        if !matches!(InputKindV1::from_code(base.kind), Some(InputKindV1::Attack | InputKindV1::Move)) {
            return None;
        }
        let player = ctx.player_id();
        let (at, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion().filter(|e| e.is_alive())?;
            if !has_buff(&sim, me.id(), BALL) {
                return None;
            }
            let at = (0..me.buff_count()).filter_map(|i| me.buff_at(i)).find_map(|b| at_of(b.name()))?;
            let ok = sim.get_entity(at).is_some_and(|u| u.is_alive() && u.is_targetable()) && sim.is_visible(me.team(), at);
            if !ok {
                return None;
            }
            (at, head(&sim, me.id()))
        };
        if base.kind == InputKindV1::Attack.code() && target_of(&base.target) == Some(at) {
            return None;
        }
        let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(at));
        if !ctx.is_valid_input(&attack) {
            return None;
        }
        let now = ctx.tick();
        if new_hold(self.steered, at, now) {
            if let Some(k) = counted("steer") {
                wlog(format!("{line} STEER: rolling at #{at} - the AI's {:?} turned into a roll at him #{k}",
                             InputKindV1::from_code(base.kind)));
            }
        }
        self.steered = Some((at, now));
        Some(attack)
    }

    /// 滚着的时候 AI 的 E：对同一个人普攻（撞上去）；普攻不成就不管（None）。
    fn hold_e(&mut self, ctx: &mut StableAiContext<'_>, target: Option<usize>) -> Option<InputV1> {
        let target = target?;
        let player = ctx.player_id();
        let line = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion().filter(|e| e.is_alive())?;
            head(&sim, me.id())
        };
        let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(target));
        if !ctx.is_valid_input(&attack) {
            return None;
        }
        let now = ctx.tick();
        if new_hold(self.e_held, target, now) {
            if let Some(k) = counted("e held") {
                wlog(format!("{line} E HELD: the AI's Frenzying Taunt at #{target} while rolling - rolling into him instead \
                              (no E in the ball) #{k}"));
            }
        }
        self.e_held = Some((target, now));
        Some(attack)
    }
}

impl StablePlayerAi for Open {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:open")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        // the AI's recall: ordered once, quiet until any other order (league_akshan's rule)
        self.recalling = match base {
            Some(b) => b.kind == InputKindV1::Return.code(),
            None => self.recalling,
        };
        // no Frenzying Taunt in the ball (0.2.0)
        if let Some(b) = base.filter(|b| b.kind == InputKindV1::Skill2.code()) {
            let ball = {
                let player = ctx.player_id();
                let sim = ctx.sim()?;
                let me = sim.get_player(player)?.champion()?;
                has_buff(&sim, me.id(), BALL)
            };
            if holds_e(b.kind, ball) {
                return self.hold_e(ctx, target_of(&b.target));
            }
            return None;
        }
        // 0.2.1: rolling at a champion, the AI's attack / walk elsewhere becomes a roll at him
        if let Some(b) = base {
            if let Some(i) = self.steer(ctx, b) {
                return Some(i);
            }
        }
        // the AI's own Q at a champion already against him: an attack, Q kept for a run-up (0.1.2)
        let q_at = base.filter(|b| b.kind == InputKindV1::Skill.code())
            .filter(|b| InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target))
            .map(|b| b.target.target_id);
        if let Some(t) = q_at {
            return self.hold_q(ctx, t);
        }
        let walking = base.is_some_and(|b| matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Attack | InputKindV1::Move)));
        if self.recalling || !walking {
            return None;
        }
        let player = ctx.player_id();
        let (pick, d2, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion().filter(|e| e.is_alive())?;
            let (id, team) = (me.id(), me.team());
            let ready = me.cooldown(SkillSlotV1::Skill).is_some_and(|c| c.unlocked && c.remaining == 0);
            if !ready || has_buff(&sim, id, BALL) || has_buff(&sim, id, BUSY) || has_buff(&sim, id, CURL) {
                return None;
            }
            let (pick, d2) = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_champion() && u.is_alive() && u.is_targetable() && sim.is_visible(team, u.id()))
                .map(|u| (u.id(), sim.distance_sq(id, u.id())))
                .min_by_key(|u| u.1)?;
            // 0.2.1：从远处滚过去之前看一眼目标是不是在敌方防御塔下
            let towers: Vec<Pt> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_tower() && u.is_alive())
                .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
                .collect();
            let there = sim.get_entity(pick).map(|u| (u.pos().0 as f64, u.pos().1 as f64))?;
            if open_from(d2) && guarded(there, &towers) {
                if let Some(k) = counted("open_guarded") {
                    wlog(format!("{} OPEN NOT: #{pick} {:.0} away is under a tower #{k}", head(&sim, id), (d2 as f64).sqrt()));
                }
                return None;
            }
            (pick, d2, head(&sim, id))
        };
        if !open_from(d2) {
            return None;
        }
        let input = InputV1::action(InputKindV1::Skill, InputTargetV1::target(pick));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(k) = counted("open") {
            wlog(format!("{line} OPEN: Powerball at #{pick} from {:.0} away (the AI had {:?}) #{k}", (d2 as f64).sqrt(),
                         base.map(|b| b.kind)));
        }
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Rammus as in League V26.21: Spiked Shell turns armour and MR into attack, Defensive Ball Curl \
         returns basic attacks, Powerball rolls up to 6 s speeding up from +0, the ball / curl bodies) loaded: game {}.{}.{} \
         abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    // 0.1.x 的副本（旧存档）普攻里还调它
    module.add_native_effect(format!("{ID}:spikes"), Step(spikes_hit));
    module.add_native_passive(format!("{ID}:shell"), Shell::default());
    module.add_player_input_ai(Open::default());
    host.log(LogLevel::Info, "league_rammus loaded (Spiked Shell from armour and MR, the curl's return, the rolling Powerball, the ball / curl bodies).");
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

    fn cd(remaining: usize, cooltime: usize) -> Option<CooldownV1> {
        Some(CooldownV1 { size: std::mem::size_of::<CooldownV1>(), remaining, cooltime, max_charges: 1,
                          charges: (remaining == 0) as usize, next_charge_ticks: remaining, unlocked: true })
    }

    #[test]
    fn spiked_shell_turns_armour_and_mr_into_attack() {
        let p = Params::default();
        assert_eq!(p.shell_ad(0, 0), 0);
        assert_eq!(p.shell_ad(44, 30), (P_AD_ARM * 44 + P_AD_MR * 30) / 100, "level 1");
        assert_eq!(p.shell_ad(44, 30), 25, "level 1: 35% of 44 + 30");
        assert_eq!(p.shell_ad(300, 100), 140, "a full tank");
        assert_eq!(Params { ad_arm: 15, ad_mr: 15, ..p }.shell_ad(300, 100), 60, "League's 15% + 15%");
    }

    #[test]
    fn the_curl_returns_a_flat_hit_from_his_resistances() {
        let p = Params::default();
        assert_eq!(p.w_return(0, 0), W_HIT);
        assert_eq!(p.w_return(200, 100), W_HIT + 20 + 10);
    }

    #[test]
    fn the_ball_speeds_up_from_nothing_by_level() {
        let p = Params::default();
        assert_eq!(p.rush(0, 1), 0, "League: from +0");
        assert_eq!(p.rush(60, 1), 25, "+25% after 1 s at level 1");
        assert_eq!(p.rush(360, 1), 150, "6 s at level 1: League's 150%");
        assert_eq!(p.rush(360, MAX_LEVEL), 245, "6 s at the top level: League's 245%");
        assert_eq!(p.rush(60, MAX_LEVEL), 41);
        assert_eq!(p.rush(1_000, 1), 150, "no more after 6 s");
        assert_eq!(p.q_acc(0), Q_ACC0);
        assert_eq!(p.q_acc(30), Q_ACC1);
        assert!(p.q_acc(6) > Q_ACC0 && p.q_acc(6) < Q_ACC1);
    }

    #[test]
    fn the_copy_params_tell_new_from_old() {
        let new = "{\"p_ad_arm\":35,\"p_ad_mr\":35,\"q_acc0\":2500,\"q_acc1\":4083,\"q_ball_t\":360,\"q_touch\":3000,\
                   \"w_hit\":20,\"w_hit_arm\":10,\"w_hit_mr\":10,\"w_t\":420}";
        let p = parse_params(new);
        assert!(p.new);
        assert_eq!(p, Params::default());
        let old = "{\"p_arm\":15,\"p_ap\":30,\"p_dmg\":15,\"q_ball_t\":240,\"q_ms0\":30,\"q_ms1\":100,\"q_ramp\":120,\"q_touch\":3000}";
        let o = parse_params(old);
        assert!(!o.new, "a 0.1.x copy");
        assert_eq!(o.ball_t, 240);
        assert_eq!(parse_params("{\"p_ad_arm\":25,\"w_hit\":40}").shell_ad(100, 0), 25);
    }

    #[test]
    fn a_champion_hit_is_an_attack_only_after_his_last_attack() {
        let none = [None, None, None];
        // his attack went out 11 ticks ago (cooltime 70), no skill on cooldown: that attack, started at tick 989
        assert_eq!(champion_blow(1_000, cd(59, 70), &none), Blow::Attack(989));
        // his attack is ready: no attack hit
        assert_eq!(champion_blow(1_000, cd(0, 70), &none), Blow::Skill);
        // a skill cast 5 ticks ago, after the attack 30 ticks ago: the skill's hit
        assert_eq!(champion_blow(1_000, cd(40, 70), &[cd(415, 420), None, None]), Blow::Skill);
        // the skill went out 200 ticks ago, the attack 11: the attack's
        assert_eq!(champion_blow(1_000, cd(59, 70), &[cd(220, 420), cd(100, 300), None]), Blow::Attack(989));
        // a skill with charges says nothing of when it went out
        let mut charged = cd(415, 420).unwrap();
        charged.max_charges = 3;
        assert_eq!(champion_blow(1_000, cd(59, 70), &[Some(charged), None, None]), Blow::Attack(989));
        // a locked slot neither
        let mut locked = cd(5, 420).unwrap();
        locked.unlocked = false;
        assert_eq!(champion_blow(1_000, cd(59, 70), &[None, None, Some(locked)]), Blow::Attack(989));
        // no cooldowns from the host: not counted
        assert_eq!(champion_blow(1_000, None, &none), Blow::Unknown);
        // minions and monsters only attack; towers are no hit
        assert_eq!(unit_blow(500, Some(EntityKindV1::Minion), false), Blow::Attack(500));
        assert_eq!(unit_blow(500, Some(EntityKindV1::Jungle), false), Blow::Attack(500));
        assert_eq!(unit_blow(500, Some(EntityKindV1::Tower), false), Blow::Tower);
        assert_eq!(unit_blow(500, None, true), Blow::Tower);
    }

    #[test]
    fn one_attack_is_returned_once() {
        let struck = [(7, 989), (9, 960)];
        // the same attack's second hit (an on-hit part): already returned
        assert!(!fresh_blow(&struck, 7, 989, true, 0));
        assert!(!fresh_blow(&struck, 7, 990, true, 0), "a tick off after an attack-speed change");
        // his next attack
        assert!(fresh_blow(&struck, 7, 1_059, true, 0));
        // another champion
        assert!(fresh_blow(&struck, 8, 989, true, 0));
        // a minion: once an attack interval
        assert!(!fresh_blow(&struck, 9, 960 + 40, false, 45));
        assert!(fresh_blow(&struck, 9, 960 + 45, false, 45));
    }

    #[test]
    fn the_ball_hits_on_body_contact_only() {
        // 11-04 logs: 38 of 40 hits after 0 ticks - the old 26000 from his centre to the enemy's edge was the attack
        // range; the AI casts Q about there. Two champions (10000 each): touching at 20000, a 3000 gap still counts
        assert!(contact(20_000.0, 10_000.0, 10_000.0));
        assert!(contact(23_000.0, 10_000.0, 10_000.0));
        assert!(!contact(23_001.0, 10_000.0, 10_000.0));
        assert!(!contact(26_000.0, 10_000.0, 6_000.0), "the old reach is no contact");
        assert_eq!(body(0), BODY);
        assert_eq!(body(8_000), 8_000.0);
        // the hook opens with Q between Q_OPEN and the range
        assert!(!open_from(30_000 * 30_000));
        assert!(open_from(30_001 * 30_001));
        // 0.2.1：从 100000 外就滚过去（以前到 45000 为止，球滚 8 tick 就撞上）
        assert!(open_from(45_001 * 45_001));
        assert!(open_from(100_000 * 100_000));
        assert!(!open_from(100_001 * 100_001));
    }

    #[test]
    fn the_ball_opens_from_afar_but_not_into_a_tower() {
        // 目标离敌方防御塔不到 80000：不开球滚过去
        let towers = [(272_000.0, 48_000.0), (528_000.0, 48_000.0)];
        assert!(guarded((272_000.0, 120_000.0), &towers));
        assert!(!guarded((272_000.0, 128_000.0), &towers));
        assert!(!guarded((400_000.0, 400_000.0), &towers));
        assert!(!guarded((400_000.0, 400_000.0), &[]));
    }

    #[test]
    fn rolling_at_a_champion_it_rolls_past_minions() {
        // 滚向英雄：小兵不算撞上，英雄、野怪算；滚向小兵 / 野怪（AI 拿 Q 清兵）：碰到谁撞谁
        assert!(!stops_ball(true, true));
        assert!(stops_ball(true, false));
        assert!(stops_ball(false, true));
        assert!(stops_ball(false, false));
        // 他身上的标记认得出滚向的是谁
        assert_eq!(at_buff(27), "league_rammus_q_at:27");
        assert_eq!(at_of(&at_buff(27)), Some(27));
        assert_eq!(at_of("league_rammus_q_ball"), None);
        assert_eq!(at_of("league_rammus_q_at:x"), None);
        assert!(at_buff(usize::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn the_ais_point_blank_q_at_a_champion_is_held() {
        // 11-06's logs: 36 Powerball hits "after 0 ticks" (gap -509 .. -25000), each "ROLL over after 0 ticks, 0 rolled":
        // the game AI's own Q at a champion against him. An attack instead, Q kept for a run-up
        assert!(point_blank(true, 20_000.0 - 11_269.0, 10_000.0, 10_000.0), "gap -11269");
        assert!(point_blank(true, 23_000.0, 10_000.0, 10_000.0), "a 3000 gap still touches");
        assert!(!point_blank(true, 23_001.0, 10_000.0, 10_000.0), "a run-up's worth away: the AI's Q goes");
        assert!(!point_blank(false, 5_000.0, 10_000.0, 6_000.0), "a minion or monster: the AI's Q goes (farming)");
        // one Q HELD line a streak
        assert!(new_hold(None, 25, 1_000));
        assert!(!new_hold(Some((25, 1_000)), 25, 1_000 + HOLD_GAP));
        assert!(new_hold(Some((25, 1_000)), 25, 1_000 + HOLD_GAP + 1));
        assert!(new_hold(Some((25, 1_000)), 26, 1_001), "another champion");
    }

    #[test]
    fn no_taunt_in_the_ball() {
        assert!(holds_e(InputKindV1::Skill2.code(), true));
        assert!(!holds_e(InputKindV1::Skill2.code(), false), "out of the ball E goes");
        assert!(!holds_e(InputKindV1::Ult.code(), true), "R in the ball is League's combo");
        assert!(!holds_e(InputKindV1::Attack.code(), true));
    }

    #[test]
    fn the_copy_names_this_crates_effects() {
        let s = include_str!("../override/league_rammus.data_champion");
        let flat: String = s.split_whitespace().collect();
        assert!(s.contains("\"league_rammus:shell\""));
        // 0.2.0: no Spiked Shell magic in the attack, no percentage reflect in the curl
        assert!(!s.contains("\"league_rammus:spikes\""), "the copy's attack still calls the old Spiked Shell");
        assert!(!flat.contains("\"damage_reflect\":"), "the copy's curl still reflects a share of every hit");
        assert!(s.contains(&format!("\"{BALL}\"")) && s.contains(&format!("\"{GO}\"")) && s.contains(&format!("\"{CURL}\"")));
        // 0.1.1: Q marks its target (`q_aim`), the touch is the gap between bodies; 0.2.1: Q's range is the hook's Q_FAR
        assert!(s.contains(&format!("\"{AIM}\"")) && s.contains(&format!("\"{BUSY}\"")));
        assert!(s.contains(&format!("\"q_touch\": {Q_TOUCH}")));
        assert!(flat.contains(&format!("\"range\":{Q_FAR},\"casting_type\":\"Targeting\",\"casting_target\":\"EnemyWithoutTower\"")),
                "Q's range is not {Q_FAR}");
        let kit = include_str!("../../../tools/kit/build_rammus.py");
        assert!(kit.contains(&format!("\"q_far\": {Q_FAR}")) && kit.contains(&format!("\"q_range\": {Q_RANGE}")));
        // the params this crate reads
        let p = s.find("\"params\"").map(|i| &s[i..]).unwrap_or("");
        let p = parse_params(&p[..p.find('}').unwrap_or(p.len())]);
        assert!(p.new);
        assert_eq!(p, Params::default(), "the copy's passive.params differ from this crate's defaults");
        // the ball lasts League's 6 s
        assert!(flat.contains(&format!("\"name\":\"{BALL}\",\"duration\":{{\"Time\":{{\"tick\":{Q_BALL_T}}}}}")),
                "the copy's ball does not last {Q_BALL_T} ticks");
    }
}
