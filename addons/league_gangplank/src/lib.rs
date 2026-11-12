//! 普朗克扩展包（用户选：「技能方案按 A 做」——带扩展包）：主包数据清不掉已经在他身上的控制、读不到生命、量不了两个桶的距离，这三件事在这里做。
//!
//! `mod.override_info` 把主包的普朗克换成 `override/` 里的副本（tools/kit/build_gangplank.py 的 native=1）：数据和主包一样，
//! 只是被动挂本包的 `league_gangplank:scurvy`，吃橘子时给他挂 2 tick 的 `league_gangplank_w_now`，桶炸开后一 tick 挂
//! `league_gangplank_k<s>_now`，桶的连锁读本包给的 `league_gangplank_k<s>_cn`（主包的连锁不量距离）。
//!
//! - **坏血病疗法清控**（英雄联盟：W 解除控制）：`w_now` 出现的那个 tick，他身上有硬控就 `entity_clear_cc`。数据把吃橘子的
//!   动作、声音和回血放在决定之后 2 tick（清控也会清掉正在放的施法动作，0.6.4 把它记成一种控制），免控 `w_imm` 在决定时
//!   就挂上，所以这 2 tick 里不会再被控。
//! - **残血吃橘子**：活着、生命低于最大值的 `w_low`% 时一直挂着 `league_gangplank_w_low`，数据的自检看到它也会吃（3 级起、
//!   W 不在冷却）；回到线上就摘掉。
//! - **火药桶连锁**（英雄联盟：桶炸开时引爆范围内相连的桶）：每个桶落地（`k<s>_live` 出现）时，他新出现的两个区域在同一点，
//!   那就是桶的位置。一个桶炸开（`k<s>_now` 出现），另一个桶已点燃（`k<o>_ripe`）、两桶相距不超过 `e_chain`：挂 3 tick 的
//!   `k<o>_cn`，桶边有敌人时数据的触发区下一 tick 就把它炸开（伤害、减速都是数据）；桶边 `e_r` + 20000 以内一个敌方单位都没有
//!   时由本包空炸：挂 `k<o>_blew`（数据的下一次贴图画爆炸）、摘掉 `k<o>_live` / `k<o>_ripe`，和数据的爆炸一样摘 `p_cd`、给被动
//!   加速。空炸的桶也接着往下连锁（v0.2.0 起三个桶位）。交给数据的桶 `RECHECK` tick 后数据还没炸（人在 e_r 外、e_r + 20000
//!   内），也由本包空炸、接着连锁（v0.2.3，`CHAIN LATE`）。
//! - **火药桶能存 3 次**（v0.2.0，英雄联盟：E 有充能）：数据里 E 只有一个冷却。本包自己记充能（`e_stock` 个，每过一轮 E 的
//!   冷却回一个）：E 放出去后手里还有桶，就把 E 的冷却减到只剩 `e_gap`（`entity_reduce_cooldown`），AI 很快能再扔。
//! - **三连桶**（v0.2.0，英雄联盟：两个连着的桶，开枪打第一个，子弹飞的时候往敌人脚下扔第三个）：枪火谈判打中（`q_fire`
//!   出现）的那个 tick，两个点燃的桶相距不超过 `e_chain`、有个敌方英雄在其中一个桶的 `e_chain` 以内却不在任何桶的爆炸范围里、
//!   手里还有桶：用掉一个桶，往他脚下扔第三个（落地画面），离他最近的那个桶炸开（桶边没人由本包空炸，有人由数据照常炸），
//!   连锁带上另一个，`THIRD_FUSE` tick 后第三个桶在他脚下炸开：伤害、无视护甲、减速、摘 `p_cd`、被动加速都照数据的桶。
//!   本包不按任何技能键。
//! - **银蛇币**（v0.3.0，用户：「船长银蛇币的系统能做吗」「回泉水才能买 购买顺序按照对局智能判断 数值也是按照这个游戏的节奏来」；
//!   英雄联盟：枪火谈判击杀掠夺 4-8 枚银蛇币和 3-7 金币，商店里 500 枚一个给加农炮幕买升级）：枪火谈判打死目标（数据的
//!   击杀检查挂 3 tick 的 `q_kill`）掠夺 [`plunder`] 枚银蛇币（`sv_scale`%：经典引擎里他一局的枪火谈判击杀只有英雄联盟的十分
//!   之一左右）和 [`plunder_gold`] 金币（`player_add_gold`），枪火谈判的等级跟比赛时钟走（每 `sv_rank_t` tick 一级）。他在泉水
//!   （出生、复活的地方 `sv_home` 以内）、手里够 `sv_cost` 枚就按局势买一个升级（[`choose`]：人头差、两队护甲、他的炮幕平均
//!   罩住几个敌我英雄），旗子 `league_gangplank_up_dd` / `up_faw` / `up_rm` 挂在他身上（复活后补回），数据的加农炮幕读它：死神的
//!   女儿（中间砸一颗大炮弹：真实伤害、强减速）、开火（同样时间打 18 波）、鼓舞士气（炮幕里的友方英雄加速）。手里的银蛇币挂成
//!   `league_gangplank_sv_<n>`，league.dll 的技能栏层数格显示它。日志：`HOME` / `PLUNDER` / `BARRAGE` / `BUY`。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_gangplank.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_gangplank";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_gangplank") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 桶边「没有敌人」要比数据的触发区再宽这么多才算（数据看得到的边上的敌人留给数据炸）。0.2.3 起数据没炸的由 [`RECHECK`]
/// 接手，这个宽度只决定先交给谁，桶不会再留在原地。
const EMPTY_MARGIN: u64 = 20000;
/// 交给数据炸的桶（连锁的 `k<o>_cn` 挂 3 tick、数据看得到其中 2 tick；三连桶靠 `q_fire`）过这么多 tick 再看一眼（0.2.3）：
/// 数据炸开的桶下一 tick 就摘掉 `k<o>_live`；这时它还亮着、还点着、还是那个桶，就是数据的触发区里一个人都没有——数据的圈只量
/// e_r 内的单位，本包按 e_r + EMPTY_MARGIN 判「边上有人」（11-06 的日志：交给数据的 keg 3 44 tick 后还在，又被连锁一次）。由本包
/// 空炸、接着连锁，同英雄联盟（连到的桶一定炸）。
pub const RECHECK: usize = 4;
/// 桶落地后最多等这么多 tick 找它的两个区域。
const KEG_LOOK: usize = 4;
/// 桶位（和 build_gangplank.P 的 e_slots 一样）。
pub const SLOTS: usize = 3;
/// 三连桶的第三个桶落地后这么多 tick 炸开（前两个桶的连锁先到）。
pub const THIRD_FUSE: usize = 6;

fn sn(x: &str) -> String {
    format!("league_gangplank_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_GANGPLANK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_gangplank.log");
        }
    }
    PathBuf::from("league_gangplank.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 低于最大生命的这个百分比就吃橘子。
    pub w_low: u64,
    /// 两个桶相距不超过这么远才连锁。
    pub e_chain: u64,
    /// 桶的爆炸半径（数据的触发区）。
    pub e_r: u64,
    /// 数据每隔这么多 tick 贴一次桶的图。
    pub e_link: usize,
    /// 被动的加速（%）和时长（tick）。
    pub p_ms: i32,
    pub p_ms_t: usize,
    /// 能存几个桶、两次扔桶至少隔多久（tick）。
    pub e_stock: usize,
    pub e_gap: usize,
    /// 三连桶：第三个桶最远扔多远，它的伤害（同数据的桶：基础 + AD%，英雄再加，无视护甲%）和减速（%、tick）。
    pub e_range: u64,
    pub e_dmg: usize,
    pub e_ratio: usize,
    pub e_champ: usize,
    pub e_pen: usize,
    pub e_slow: i32,
    pub e_slow_t: usize,
    /// 银蛇币（0.3.0）：一次枪火谈判击杀给英雄联盟 4-8 枚的百分之几（按这个游戏的节奏放大）、枪火谈判每隔多少 tick
    /// 升一级（英雄联盟 1/3/5/7/9 级加点）、一个升级多少枚、击杀多给的金币是英雄联盟 3-7 的百分之几、离出生点多近算在泉水。
    pub sv_scale: u64,
    pub sv_rank_t: usize,
    pub sv_cost: u64,
    pub sv_gold: u64,
    pub sv_home: u64,
}

impl Default for Params {
    fn default() -> Self {
        Params {
            w_low: 40,
            e_chain: 70000,
            e_r: 30000,
            e_link: 10,
            p_ms: 20,
            p_ms_t: 120,
            e_stock: 3,
            e_gap: 60,
            e_range: 70000,
            e_dmg: 40,
            e_ratio: 100,
            e_champ: 60,
            e_pen: 40,
            e_slow: 40,
            e_slow_t: 120,
            sv_scale: 1000,
            sv_rank_t: 10800,
            sv_cost: 500,
            sv_gold: 100,
            sv_home: 60000,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        match k {
            "w_low" => p.w_low = v,
            "e_chain" => p.e_chain = v,
            "e_r" => p.e_r = v,
            "e_link" => p.e_link = v as usize,
            "p_ms" => p.p_ms = v as i32,
            "p_ms_t" => p.p_ms_t = v as usize,
            "e_stock" => p.e_stock = v as usize,
            "e_gap" => p.e_gap = v as usize,
            "e_range" => p.e_range = v,
            "e_dmg" => p.e_dmg = v as usize,
            "e_ratio" => p.e_ratio = v as usize,
            "e_champ" => p.e_champ = v as usize,
            "e_pen" => p.e_pen = v as usize,
            "e_slow" => p.e_slow = v as i32,
            "e_slow_t" => p.e_slow_t = v as usize,
            "sv_scale" => p.sv_scale = v,
            "sv_rank_t" => p.sv_rank_t = v as usize,
            "sv_cost" => p.sv_cost = v,
            "sv_gold" => p.sv_gold = v,
            "sv_home" => p.sv_home = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 生命低到该吃橘子了吗。
pub fn low(p: &Params, hp: usize, max_hp: usize) -> bool {
    hp > 0 && max_hp > 0 && (hp as u64) * 100 < p.w_low * max_hp as u64
}

pub fn within(a: (u64, u64), b: (u64, u64), r: u64) -> bool {
    let dx = a.0 as f64 - b.0 as f64;
    let dy = a.1 as f64 - b.1 as f64;
    dx * dx + dy * dy <= (r as f64) * (r as f64)
}

/// 桶落地时他新出现的区域（`now` 里比 `base` 多出来的）里，至少两个落在同一点的那个点：桶的触发区和英雄加伤区。
pub fn keg_point(base: &[(u64, u64)], now: &[(u64, u64)]) -> Option<(u64, u64)> {
    let mut left: HashMap<(u64, u64), usize> = HashMap::new();
    for p in base {
        *left.entry(*p).or_insert(0) += 1;
    }
    let mut new: HashMap<(u64, u64), usize> = HashMap::new();
    for p in now {
        match left.get_mut(p) {
            Some(n) if *n > 0 => *n -= 1,
            _ => *new.entry(*p).or_insert(0) += 1,
        }
    }
    new.into_iter().filter(|(_, n)| *n >= 2).map(|(p, _)| p).min()
}

/// E 的充能：手里几个桶、下一个什么时候回来、上次扔桶的 tick、上一 tick 读到的冷却。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Stock {
    pub n: usize,
    pub refill_at: Option<usize>,
    pub last: Option<usize>,
    pub prev_cd: usize,
    pub armed: bool,
}

impl Stock {
    /// 一个 tick：`remaining` / `cycle` 是这一 tick 读到的 E 冷却和整轮冷却。返回要从冷却里减掉多少（手里还有桶时冷却
    /// 只留 e_gap），以及这一 tick 是不是刚扔了一个桶。
    pub fn step(&mut self, p: &Params, now: usize, remaining: usize, cycle: usize) -> (usize, bool) {
        if !self.armed {
            *self = Stock { n: 1, armed: true, prev_cd: remaining, ..Stock::default() }; // E 解锁时手里一个桶
        }
        let thrown = remaining > self.prev_cd;
        if thrown {
            self.n = self.n.saturating_sub(1);
            self.last = Some(now);
        }
        self.tick_refill(p, now, cycle);
        let left = self.last.map_or(0, |t| (t + p.e_gap).saturating_sub(now));
        let cut = if self.n > 0 && remaining > left { remaining - left } else { 0 };
        self.prev_cd = remaining - cut;
        (cut, thrown)
    }

    /// 不满时每过一整轮冷却回一个桶。
    fn tick_refill(&mut self, p: &Params, now: usize, cycle: usize) {
        if self.n >= p.e_stock {
            self.refill_at = None;
            return;
        }
        match self.refill_at {
            None => self.refill_at = Some(now + cycle.max(1)),
            Some(t) if now >= t => {
                self.n += 1;
                self.refill_at = (self.n < p.e_stock).then_some(now + cycle.max(1));
            }
            _ => {}
        }
    }

    /// 三连桶用掉一个桶。
    pub fn take(&mut self, p: &Params, now: usize, cycle: usize) -> bool {
        if self.n == 0 {
            return false;
        }
        self.n -= 1;
        self.last = Some(now);
        self.tick_refill(p, now, cycle);
        true
    }
}

/// 三连桶：`ripe` 是点燃的桶（桶位、位置），`foes` 是扔得到的敌方英雄（id、位置）。两个点燃的桶相距不超过 e_chain，
/// 一个敌方英雄在某个桶的 e_chain 以内、却不在任何点燃的桶的 e_r 以内（那样的数据自己会炸）：返回（先炸的桶位、他的 id、
/// 他的位置），先炸离他最近的桶，几个人取离桶最近的。
pub fn triple(p: &Params, ripe: &[(usize, (u64, u64))], foes: &[(usize, (u64, u64))]) -> Option<(usize, usize, (u64, u64))> {
    let linked = |a: &(usize, (u64, u64))| ripe.iter().any(|b| b.0 != a.0 && within(a.1, b.1, p.e_chain));
    let d2 = |a: (u64, u64), b: (u64, u64)| (a.0 as f64 - b.0 as f64).powi(2) + (a.1 as f64 - b.1 as f64).powi(2);
    foes.iter()
        .filter(|f| !ripe.iter().any(|k| within(k.1, f.1, p.e_r)))
        .flat_map(|f| ripe.iter().filter(|k| linked(k) && within(k.1, f.1, p.e_chain)).map(move |k| (k, f)))
        .min_by(|a, b| d2(a.0 .1, a.1 .1).total_cmp(&d2(b.0 .1, b.1 .1)))
        .map(|(k, f)| (k.0, f.0, f.1))
}

/// 交给数据炸的一个桶（0.2.3）：再看一眼的 tick、桶位、位置。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Handed {
    pub due: usize,
    pub slot: usize,
    pub at: (u64, u64),
}

/// 把桶位 `slot` 上 `at` 的桶交给数据，[`RECHECK`] tick 后再看；同一个桶已经在等就不再记。
pub fn hand(handed: &mut Vec<Handed>, now: usize, slot: usize, at: (u64, u64)) {
    if !handed.iter().any(|h| h.slot == slot && h.at == at) {
        handed.push(Handed { due: now + RECHECK, slot, at });
    }
}

/// 到 `now` 该再看的桶（都从 `handed` 里拿走）里，还是那个桶（`kegs` 里还记着它的位置：数据炸了或换了新桶就不是）、还亮着
/// 还点着（`lit`）的：本包空炸。晚了 RECHECK 以上的不算——他死了（死人的被动不跑），复活时不去炸一个早就交出去的桶。
pub fn late_blows(handed: &mut Vec<Handed>, now: usize, kegs: &[Option<(u64, u64)>; SLOTS], lit: [bool; SLOTS])
    -> Vec<(usize, (u64, u64))> {
    let mut out: Vec<(usize, (u64, u64))> = Vec::new();
    handed.retain(|h| {
        if h.due > now {
            return true;
        }
        if now <= h.due + RECHECK && kegs[h.slot] == Some(h.at) && lit[h.slot] && !out.iter().any(|o| o.0 == h.slot) {
            out.push((h.slot, h.at));
        }
        false
    });
    out
}

// ===================== 银蛇币（0.3.0） =====================

/// 枪火谈判在 `tick` 时是几级（1..=5）：每 `sv_rank_t` tick 升一级（英雄联盟 1/3/5/7/9 级加点：这里跟着比赛时钟）。
pub fn q_rank(p: &Params, tick: usize) -> u64 {
    (1 + tick / p.sv_rank_t.max(1)).min(5) as u64
}

/// 一次枪火谈判击杀掠夺的银蛇币：英雄联盟 4-8 枚（按级）的 `sv_scale`%。
pub fn plunder(p: &Params, tick: usize) -> u64 {
    ((3 + q_rank(p, tick)) * p.sv_scale + 50) / 100
}

/// 一次枪火谈判击杀多给的金币：英雄联盟 3-7（按级）的 `sv_gold`%。
pub fn plunder_gold(p: &Params, tick: usize) -> i64 {
    (((2 + q_rank(p, tick)) * p.sv_gold + 50) / 100) as i64
}

/// 加农炮幕的三个升级（英雄联盟商店里各 500 银蛇币）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Upgrade {
    /// 死神的女儿：开始 0.5 秒后中间砸一颗超大炮弹（一波的 300% 真实伤害、强减速）。
    Daughter,
    /// 开火：同样的时间里多打 6 波（18 波）。
    FireAtWill,
    /// 鼓舞士气：炮幕里的友方英雄加速，离开后还有 2 秒。
    Morale,
}

impl Upgrade {
    /// 平手时的先后（死神的女儿最先：开团抓人最显眼）。
    pub const ALL: [Upgrade; 3] = [Upgrade::Daughter, Upgrade::FireAtWill, Upgrade::Morale];

    pub fn index(self) -> usize {
        match self {
            Upgrade::Daughter => 0,
            Upgrade::FireAtWill => 1,
            Upgrade::Morale => 2,
        }
    }

    /// 数据读的旗子（数据：`SwitchByBuff league_gangplank_up_*`）。
    pub fn flag(self) -> &'static str {
        match self {
            Upgrade::Daughter => "up_dd",
            Upgrade::FireAtWill => "up_faw",
            Upgrade::Morale => "up_rm",
        }
    }

    pub fn label(self) -> &'static str {
        match self {
            Upgrade::Daughter => "Death's Daughter",
            Upgrade::FireAtWill => "Fire at Will",
            Upgrade::Morale => "Raise Morale",
        }
    }
}

/// 买的那一刻对局的样子。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Situation {
    /// 他这一队的击杀减对面的。
    pub kill_diff: i64,
    /// 对面活着的英雄平均护甲是他这一队的几倍（真实伤害对厚的人更值）。
    pub foe_armour: f64,
    /// 他的炮幕落地时平均罩住几个敌方英雄、几个己方英雄，一共落过几次。
    pub foes_per: f64,
    pub allies_per: f64,
    pub barrages: u32,
}

/// 落后这么多个人头、领先这么多个人头。
pub const BEHIND: i64 = -3;
pub const AHEAD: i64 = 3;
/// 对面护甲是这一队的这么多倍算「厚」。
pub const TANKY: f64 = 1.25;
/// 炮幕平均罩住这么多敌人算「打得到人堆」、这么多队友算「队友在炮幕里打」；至少看过这么多次才算数。
pub const CROWD: f64 = 2.0;
pub const WITH_ALLIES: f64 = 1.0;
pub const SEEN: u32 = 2;

/// 按局势挑下一个升级（用户：「购买顺序按照对局智能判断」）：
/// - 死神的女儿 2 分，落后再加 2（真实伤害的大炮弹抓人、守），对面比这一队厚再加 1；
/// - 开火 2 分，领先再加 2（多 6 波滚雪球），炮幕常罩住人堆再加 1；
/// - 鼓舞士气 1 分，队友常在炮幕里一起打再加 2。
/// 分高的先买，一样高按 [`Upgrade::ALL`] 的先后。返回升级和理由（日志用）。
pub fn choose(bought: [bool; 3], s: &Situation) -> Option<(Upgrade, String)> {
    let seen = s.barrages >= SEEN;
    let mut best: Option<(Upgrade, u32, String)> = None;
    for u in Upgrade::ALL {
        if bought[u.index()] {
            continue;
        }
        let (score, why) = match u {
            Upgrade::Daughter => {
                let behind = s.kill_diff <= BEHIND;
                let tanky = s.foe_armour >= TANKY;
                (2 + 2 * behind as u32 + tanky as u32,
                 format!("{}{}", if behind { "behind, " } else { "" }, if tanky { "tanky foes, " } else { "" }))
            }
            Upgrade::FireAtWill => {
                let ahead = s.kill_diff >= AHEAD;
                let crowd = seen && s.foes_per >= CROWD;
                (2 + 2 * ahead as u32 + crowd as u32,
                 format!("{}{}", if ahead { "ahead, " } else { "" }, if crowd { "barrages hit crowds, " } else { "" }))
            }
            Upgrade::Morale => {
                let with = seen && s.allies_per >= WITH_ALLIES;
                (1 + 2 * with as u32, if with { "allies fight in the barrages, ".to_string() } else { String::new() })
            }
        };
        if best.as_ref().is_none_or(|b| score > b.1) {
            best = Some((u, score, why));
        }
    }
    best.map(|(u, score, why)| {
        let why = why.trim_end_matches(", ");
        (u, format!("score {score}{}", if why.is_empty() { String::new() } else { format!(": {why}") }))
    })
}

/// 面板上显示的银蛇币数：league.dll 的层数格读 `league_gangplank_sv_<n>`（tools/kit/stack_nums.py 的梯子规则）。
pub fn count_name(coins: u64) -> String {
    sn(&format!("sv_{coins}"))
}

/// 一局里这个普朗克的银蛇币。
#[derive(Clone, Default)]
pub struct Serpents {
    pub coins: u64,
    pub bought: [bool; 3],
    /// 他的泉水：出生、复活时站的地方（复活是新的实体 `body`；原地复活的还是那个身子，不算）。
    pub home: Option<(u64, u64)>,
    body: Option<usize>,
    pub player: Option<usize>,
    pub kills: u32,
    pub gold: i64,
    pub barrages: u32,
    pub foes_in: u32,
    pub allies_in: u32,
    had_kill: bool,
    had_land: bool,
    /// 炮幕落地后数罩住了几个英雄的那个 tick（标记比 `r_land` 晚一 tick 挂上）。
    count_at: Option<usize>,
    shown: Option<u64>,
}

// ===================== 被动 =====================

/// 算「被控」的硬控（游戏 0.6.4 把施法动作也记成一种控制 Animation，不能用 cc_count() > 0）。
pub const HARD_CC: [CcKindV1; 7] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::ForceMove,
];

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn hard_cc(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
    })
}

/// 离桶最近的活着的敌方单位有多远（防御塔不算，数据的触发区是 EnemyWithoutTower）；没有就是 None。
fn nearest_enemy(sim: &StableSim<'_>, team: usize, at: (u64, u64)) -> Option<f64> {
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|e| e.is_alive() && e.team() != team && e.kind() != Some(EntityKindV1::Tower))
        .map(|e| (e.pos().0 as f64 - at.0 as f64).hypot(e.pos().1 as f64 - at.1 as f64))
        .min_by(|a, b| a.total_cmp(b))
}

fn far(d: Option<f64>) -> String {
    d.map_or("no enemy".to_string(), |d| format!("{d:.0} away"))
}

/// 每隔这么多 tick 看一眼升级的旗子和面板上的数（死了复活后旗子没了，补回去）。
const KEEP_EVERY: usize = 6;

/// 带着炮幕落地标记（`r_in` 敌方英雄、`r_ally` 己方英雄，3 tick）的英雄各有几个。
fn marked(sim: &StableSim<'_>) -> (u32, u32) {
    let (foe, ally) = (sn("r_in"), sn("r_ally"));
    let mut out = (0, 0);
    for e in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|e| e.is_champion()) {
        let names: Vec<String> = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect();
        out.0 += names.iter().any(|n| *n == foe) as u32;
        out.1 += names.iter().any(|n| *n == ally) as u32;
    }
    out
}

/// 一队活着的英雄的平均护甲（`own`：他这一队）；没人就是 None。
fn mean_armour(sim: &StableSim<'_>, team: usize, own: bool) -> Option<f64> {
    let v: Vec<f64> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|e| e.is_champion() && e.is_alive() && (e.team() == team) == own)
        .map(|e| e.stat().defence as f64)
        .collect();
    (!v.is_empty()).then(|| v.iter().sum::<f64>() / v.len() as f64)
}

fn refresh(sim: &mut StableSim<'_>, me: usize, buff: &BuffV1) {
    sim.entity_remove_buff(me, buff.name());
    sim.add_buff(me, buff);
}

#[derive(Clone, Default)]
struct Scurvy {
    p: Params,
    had_w_now: bool,
    kegs: [Option<(u64, u64)>; SLOTS],
    pending: [Option<(usize, Vec<(u64, u64)>)>; SLOTS],
    had_live: [bool; SLOTS],
    had_now: [bool; SLOTS],
    prev: Vec<(u64, u64)>,
    stock: Stock,
    had_q: bool,
    /// 三连桶的第三个桶：炸开的 tick、位置。
    third: Vec<(usize, (u64, u64))>,
    /// 交给数据炸、等着再看一眼的桶（0.2.3）。
    handed: Vec<Handed>,
    /// 银蛇币（0.3.0）。
    sv: Serpents,
}

impl Scurvy {
    /// 银蛇币（0.3.0，用户：「船长银蛇币的系统能做吗」「回泉水才能买 购买顺序按照对局智能判断 数值也是按照这个游戏的节奏来」）：
    /// 枪火谈判击杀（数据挂 3 tick 的 `q_kill`）掠夺银蛇币和金币；炮幕落地（`r_land`）后一 tick 数罩住了几个敌方、己方英雄；
    /// 在泉水（出生、复活的地方 `sv_home` 以内）攒够 `sv_cost` 就按局势买一个升级。
    fn serpents(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, alive: bool) {
        let Some((team, pos)) = sim.get_entity(me).map(|e| (e.team(), e.pos())) else { return };
        // the first tick of a new body (a respawn is a new entity) he stands in his fountain; a revive where he fell
        // (the same body) is not his fountain
        if alive && self.sv.body != Some(me) {
            self.fountain(sim, me, pos);
        }

        let kill = has(sim, me, &sn("q_kill"));
        if kill && !self.sv.had_kill {
            let gain = plunder(&self.p, now);
            let gold = plunder_gold(&self.p, now);
            self.sv.coins += gain;
            self.sv.kills += 1;
            let paid = gold > 0 && self.sv.player.is_some_and(|pl| sim.player_add_gold(pl, gold));
            if paid {
                self.sv.gold += gold;
            }
            if let Some(k) = counted("plunder") {
                wlog(format!("{} PLUNDER #{k}: Parrrley kill {} (rank {}): +{gain} serpents = {}, +{gold} gold{}",
                             head(sim, me), self.sv.kills, q_rank(&self.p, now), self.sv.coins,
                             if paid { "" } else { " (not paid)" }));
            }
        }
        self.sv.had_kill = kill;

        // the marks on the champions in the barrage come a tick after `r_land`
        let land = has(sim, me, &sn("r_land"));
        if land && !self.sv.had_land {
            self.sv.count_at = Some(now + 1);
        }
        self.sv.had_land = land;
        if self.sv.count_at.is_some_and(|t| now >= t) {
            self.sv.count_at = None;
            let (foes, allies) = marked(sim);
            self.sv.barrages += 1;
            self.sv.foes_in += foes;
            self.sv.allies_in += allies;
            if let Some(k) = counted("barrage") {
                wlog(format!("{} BARRAGE #{k}: landed on {foes} enemy and {allies} allied champion(s) ({} so far)",
                             head(sim, me), self.sv.barrages));
            }
        }

        let at_home = self.sv.home.is_some_and(|h| within(pos, h, self.p.sv_home));
        if alive && at_home && self.sv.coins >= self.p.sv_cost {
            let s = self.situation(sim, team);
            if let Some((u, why)) = choose(self.sv.bought, &s) {
                self.sv.bought[u.index()] = true;
                self.sv.coins -= self.p.sv_cost;
                if let Some(k) = counted("buy") {
                    wlog(format!("{} BUY #{k}: {} for {} serpents at the fountain ({why}; kills {:+}, foe armour x{:.2}, \
                                  {} barrage(s), {:.1} foes / {:.1} allies in each) - {} left",
                                 head(sim, me), u.label(), self.p.sv_cost, s.kill_diff, s.foe_armour, s.barrages,
                                 s.foes_per, s.allies_per, self.sv.coins));
                }
            }
        }
        if now % KEEP_EVERY == 0 {
            self.keep(sim, me);
        }
    }

    /// 他的泉水：新的身子（出生、复活）第一次站的地方。
    fn fountain(&mut self, sim: &StableSim<'_>, me: usize, pos: (u64, u64)) {
        self.sv.body = Some(me);
        if self.sv.home != Some(pos) {
            if let Some(k) = counted("home") {
                wlog(format!("{} HOME #{k}: his fountain at ({}, {})", head(sim, me), pos.0, pos.1));
            }
            self.sv.home = Some(pos);
        }
    }

    /// 对局的样子：击杀记录里两队的人头、两队活着的英雄的平均护甲、他的炮幕平均罩住几个人。
    fn situation(&self, sim: &StableSim<'_>, team: usize) -> Situation {
        let (mut mine, mut theirs) = (0i64, 0i64);
        for k in (0..sim.kill_log_count()).filter_map(|i| sim.kill_log_at(i)) {
            if k.killer_team == team {
                mine += 1;
            } else {
                theirs += 1;
            }
        }
        let foe_armour = match (mean_armour(sim, team, true), mean_armour(sim, team, false)) {
            (Some(m), Some(f)) if m > 0.0 => f / m,
            _ => 1.0,
        };
        let n = self.sv.barrages.max(1) as f64;
        Situation { kill_diff: mine - theirs, foe_armour, foes_per: self.sv.foes_in as f64 / n,
                    allies_per: self.sv.allies_in as f64 / n, barrages: self.sv.barrages }
    }

    /// 买过的升级的旗子挂在他身上（数据的 `SwitchByBuff` 读施法者的；死了复活旗子会没，这里补回去。塞拉斯偷到的、佛耶戈
    /// 附身用的加农炮幕是主包那份，没有升级），面板上的数（`league_gangplank_sv_<n>`）跟着银蛇币改。
    fn keep(&mut self, sim: &mut StableSim<'_>, me: usize) {
        for u in Upgrade::ALL.iter().filter(|u| self.sv.bought[u.index()]) {
            let flag = sn(u.flag());
            if !has(sim, me, &flag) {
                sim.add_buff(me, &BuffV1::named(&flag));
            }
        }
        let name = count_name(self.sv.coins);
        if let Some(old) = self.sv.shown.filter(|&c| c != self.sv.coins) {
            sim.entity_remove_buff(me, &count_name(old));
        }
        if !has(sim, me, &name) {
            sim.add_buff(me, &BuffV1::named(&name));
        }
        self.sv.shown = Some(self.sv.coins);
    }

    /// W 吃下去的那个 tick 清掉他身上的硬控。
    fn cleanse(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let w_now = has(sim, me, &sn("w_now"));
        if w_now && !self.had_w_now && hard_cc(sim, me) {
            let n = sim.entity_clear_cc(me);
            if let Some(k) = counted("cleanse") {
                wlog(format!("{} CLEANSE #{k}: Remove Scurvy cleared {n} crowd control(s)", head(sim, me)));
            }
        }
        self.had_w_now = w_now;
    }

    /// 残血时挂着 w_low，回到线上摘掉。
    fn low_flag(&mut self, sim: &mut StableSim<'_>, me: usize, alive: bool) {
        let (hp, max_hp) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        let want = alive && low(&self.p, hp, max_hp);
        let name = sn("w_low");
        let on = has(sim, me, &name);
        if want && !on {
            sim.add_buff(me, &BuffV1::named(&name));
            if let Some(k) = counted("low") {
                wlog(format!("{} LOW #{k}: {hp}/{max_hp} under {}%: w_low on", head(sim, me), self.p.w_low));
            }
        } else if !want && on {
            sim.entity_remove_buff(me, &name);
        }
    }

    /// 桶灭了（`k<s>_live` 没了）就忘掉它的位置（0.2.2：在 [`Scurvy::blown`] 读过炸开的桶的位置之后才忘）。
    fn forget(&mut self, live: [bool; SLOTS]) {
        for s in 0..SLOTS {
            if !live[s] {
                self.kegs[s] = None;
                self.pending[s] = None;
            }
        }
    }

    /// 桶落地时记下它的位置。
    fn track(&mut self, sim: &StableSim<'_>, me: usize, now: usize, mine: &[(u64, u64)]) {
        let live: [bool; SLOTS] = std::array::from_fn(|s| has(sim, me, &sn(&format!("k{}_live", s + 1))));
        self.forget(live);
        for s in 0..SLOTS {
            let live = live[s];
            if live && !self.had_live[s] {
                self.pending[s] = Some((now, self.prev.clone()));
                self.kegs[s] = None;
            }
            if let Some((t0, base)) = self.pending[s].take() {
                match keg_point(&base, mine) {
                    Some(at) => {
                        self.kegs[s] = Some(at);
                        if let Some(k) = counted("keg") {
                            wlog(format!("{} KEG #{k}: keg {} at ({}, {}) ({} tick(s) after it landed)",
                                         head(sim, me), s + 1, at.0, at.1, now - t0));
                        }
                    }
                    None if now >= t0 + KEG_LOOK => {
                        if let Some(k) = counted("keg_lost") {
                            wlog(format!("{} KEG? #{k}: keg {} landed at t={t0} but no two new zones of his at one point",
                                         head(sim, me), s + 1));
                        }
                    }
                    None => self.pending[s] = Some((t0, base)),
                }
            }
            self.had_live[s] = live;
        }
    }

    /// 这 tick 炸开的桶（`k<s>_now` 刚出现）和它们的位置。数据的爆炸在同一个 Delayed 里摘 `k<s>_live`、挂 `k<s>_now`：
    /// 0.2.1 以前 `track()` 先跑、先把桶位忘了，连锁读到的总是 None（11-04 的日志：全天 0 CHAIN），所以这里要在
    /// [`Scurvy::forget`] 之前读。
    fn blown(&mut self, now: [bool; SLOTS]) -> Vec<(usize, (u64, u64))> {
        let mut out = Vec::new();
        for s in 0..SLOTS {
            if now[s] && !self.had_now[s] {
                if let Some(at) = self.kegs[s] {
                    out.push((s, at));
                }
            }
            self.had_now[s] = now[s];
        }
        out
    }

    /// 一个桶炸开：别的点燃的桶在 e_chain 以内就连锁。
    fn chain(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now: [bool; SLOTS] = std::array::from_fn(|s| has(sim, me, &sn(&format!("k{}_now", s + 1))));
        for (s, from) in self.blown(now) {
            self.chain_from(sim, me, s, from);
        }
    }

    fn chain_from(&mut self, sim: &mut StableSim<'_>, me: usize, s: usize, from: (u64, u64)) {
        for o in (0..SLOTS).filter(|&o| o != s) {
            let k = |x: &str| sn(&format!("k{}_{x}", o + 1));
            let Some(at) = self.kegs[o] else { continue };
            if !has(sim, me, &k("ripe")) || !has(sim, me, &k("live")) || !within(from, at, self.p.e_chain) {
                continue;
            }
            refresh(sim, me, &BuffV1::timed(&k("cn"), 3));
            let (empty, near) = self.blow_if_empty(sim, me, o);
            if let Some(n) = counted("chain") {
                let how = if empty {
                    "blown empty here".to_string()
                } else {
                    format!("left to the data (an enemy beside it, {})", far(near))
                };
                wlog(format!("{} CHAIN #{n}: keg {} blew, keg {} at ({}, {}) {how}", head(sim, me), s + 1, o + 1, at.0, at.1));
            }
            if empty {
                self.chain_from_empty(sim, me, o, at);
            }
        }
    }

    /// 空炸的桶接着连锁（数据炸的桶由 `k<s>_now` 接着连）。
    fn chain_from_empty(&mut self, sim: &mut StableSim<'_>, me: usize, o: usize, at: (u64, u64)) {
        self.kegs[o] = None;
        self.chain_from(sim, me, o, at);
    }

    /// 桶边 e_r + EMPTY_MARGIN 以内没有敌方单位就由本包空炸（画面、摘 p_cd、加速同数据的爆炸）：true；有人就留给数据，
    /// [`RECHECK`] tick 后再看一眼（0.2.3）。另外给离桶最近的敌方单位多远（日志）。
    fn blow_if_empty(&mut self, sim: &mut StableSim<'_>, me: usize, o: usize) -> (bool, Option<f64>) {
        let Some(at) = self.kegs[o] else { return (false, None) };
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let near = nearest_enemy(sim, team, at);
        if near.is_some_and(|d| d <= (self.p.e_r + EMPTY_MARGIN) as f64) {
            hand(&mut self.handed, sim.tick(), o, at);
            return (false, near);
        }
        self.blow_empty(sim, me, o);
        (true, near)
    }

    /// 本包把桶位 `o` 的桶空炸：`k<o>_blew`（数据的下一次贴图画爆炸）、摘掉 `live` / `ripe`，和数据的爆炸一样摘 `p_cd`、加速。
    fn blow_empty(&mut self, sim: &mut StableSim<'_>, me: usize, o: usize) {
        let k = |x: &str| sn(&format!("k{}_{x}", o + 1));
        refresh(sim, me, &BuffV1::timed(&k("blew"), self.p.e_link + 1));
        sim.entity_remove_buff(me, &k("live"));
        sim.entity_remove_buff(me, &k("ripe"));
        self.fired_up(sim, me);
        self.kegs[o] = None;
    }

    /// 交给数据的桶再看一眼（0.2.3）：数据没炸（还亮着、还点着、还是那个桶）就由本包空炸、接着连锁。在 [`Scurvy::track`]
    /// 之后跑：数据炸掉的桶那时已经被忘掉。
    fn recheck(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        if self.handed.is_empty() {
            return;
        }
        let lit: [bool; SLOTS] = std::array::from_fn(|s| {
            has(sim, me, &sn(&format!("k{}_live", s + 1))) && has(sim, me, &sn(&format!("k{}_ripe", s + 1)))
        });
        let kegs = self.kegs;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        for (o, at) in late_blows(&mut self.handed, now, &kegs, lit) {
            let near = nearest_enemy(sim, team, at);
            self.blow_empty(sim, me, o);
            if let Some(n) = counted("late") {
                wlog(format!("{} CHAIN LATE #{n}: keg {} at ({}, {}) still lit {RECHECK} ticks after it was left to the data \
                              (nearest enemy {}, the data's zone {}) - blown empty here",
                             head(sim, me), o + 1, at.0, at.1, far(near), self.p.e_r));
            }
            self.chain_from_empty(sim, me, o, at);
        }
    }

    /// 桶炸开时他身上的变化（同数据）：摘被动的冷却 `p_cd`，被动加速。
    fn fired_up(&self, sim: &mut StableSim<'_>, me: usize) {
        sim.entity_remove_buff(me, &sn("p_cd"));
        let mut fast = BuffV1::timed(&sn("p_ms"), self.p.p_ms_t);
        fast.move_speed_mult = self.p.p_ms;
        refresh(sim, me, &fast);
    }

    /// E 的充能：手里还有桶时把冷却减到只剩 e_gap。
    fn charges(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let Some(cd) = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill2)).filter(|c| c.unlocked) else {
            return;
        };
        let (cut, thrown) = self.stock.step(&self.p, now, cd.remaining, cd.cooltime);
        if cut > 0 {
            sim.entity_reduce_cooldown(me, SkillSlotV1::Skill2, cut);
        }
        if thrown {
            if let Some(k) = counted("stock") {
                wlog(format!("{} STOCK #{k}: a keg thrown, {} left in hand{}", head(sim, me), self.stock.n,
                             if cut > 0 { format!(", cooldown cut by {cut}") } else { String::new() }));
            }
        }
    }

    /// 三连桶：枪火谈判打中的那个 tick（`q_fire` 出现）看两个点燃的连着的桶和桶外的敌方英雄。
    fn triple_barrel(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let q = has(sim, me, &sn("q_fire"));
        let shot = q && !self.had_q;
        self.had_q = q;
        if !shot || self.stock.n == 0 {
            return;
        }
        let Some((team, here, cycle)) = sim.get_entity(me).filter(|e| e.is_alive())
            .map(|e| (e.team(), e.pos(), e.cooldown(SkillSlotV1::Skill2).map_or(0, |c| c.cooltime))) else { return };
        let ripe: Vec<(usize, (u64, u64))> = (0..SLOTS)
            .filter(|&s| has(sim, me, &sn(&format!("k{}_ripe", s + 1))) && has(sim, me, &sn(&format!("k{}_live", s + 1))))
            .filter_map(|s| self.kegs[s].map(|at| (s, at)))
            .collect();
        if ripe.len() < 2 {
            return;
        }
        let foes: Vec<(usize, (u64, u64))> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive() && u.is_targetable() && u.team() != team
                && within(here, u.pos(), self.p.e_range))
            .map(|u| (u.id(), u.pos()))
            .collect();
        let Some((s, foe, at)) = triple(&self.p, &ripe, &foes) else { return };
        if !self.stock.take(&self.p, now, cycle) {
            return;
        }
        let input = InputTargetV1::pos(at.0, at.1);
        sim.play_view_effect(&sn("e_land"), me, &input, 0, 0, 0);
        sim.play_view_effect(&sn("e_keg_lit"), me, &input, 0, 0, 0);
        sim.play_sfx(&sn("e_land"), me, &input);
        self.third.push((now + THIRD_FUSE, at));
        let first = self.kegs[s];
        // an enemy beside it: the data's on q_fire, looked at again RECHECK ticks on (0.2.3)
        let (empty, near) = self.blow_if_empty(sim, me, s);
        if let (true, Some(from)) = (empty, first) {
            self.chain_from_empty(sim, me, s, from);
        }
        if let Some(k) = counted("triple") {
            let how = if empty { "blown empty here".to_string() } else { format!("the data's, an enemy beside it, {}", far(near)) };
            wlog(format!("{} TRIPLE #{k}: kegs {:?} lit, the third thrown at #{foe} ({}, {}), keg {} goes first ({how}), {} in hand",
                         head(sim, me), ripe.iter().map(|k| k.0 + 1).collect::<Vec<_>>(), at.0, at.1, s + 1, self.stock.n));
        }
    }

    /// 第三个桶到时候炸开：伤害、无视护甲、减速同数据的桶。
    fn third_boom(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let due: Vec<(u64, u64)> = self.third.iter().filter(|t| t.0 <= now).map(|t| t.1).collect();
        self.third.retain(|t| t.0 > now);
        if due.is_empty() {
            return;
        }
        let Some((team, ad)) = sim.get_entity(me).map(|e| (e.team(), e.stat().attack)) else { return };
        for at in due {
            let input = InputTargetV1::pos(at.0, at.1);
            sim.play_view_effect(&sn("e_boom"), me, &input, 0, 0, 0);
            sim.play_sfx(&sn("e_boom"), me, &input);
            let hit: Vec<(usize, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.is_alive() && u.is_targetable() && u.team() != team && u.kind() != Some(EntityKindV1::Tower)
                    && within(u.pos(), at, self.p.e_r))
                .map(|u| (u.id(), u.is_champion()))
                .collect();
            let mut pen = BuffV1::timed(&sn("e_pen"), 1);
            pen.defence_penetration = self.p.e_pen;
            refresh(sim, me, &pen);
            let base = self.p.e_dmg + ad as usize * self.p.e_ratio / 100;
            for &(id, champ) in &hit {
                let dmg = base + if champ { self.p.e_champ } else { 0 };
                sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
                let mut slow = BuffV1::timed(&sn("e_slow"), self.p.e_slow_t);
                slow.move_speed_mult = -self.p.e_slow;
                sim.add_buff(id, &slow);
                sim.play_view_effect(&sn("e_hit"), me, &InputTargetV1::target(id), 0, 0, 0);
            }
            self.fired_up(sim, me);
            if let Some(k) = counted("third") {
                wlog(format!("{} THIRD #{k}: the third keg blew at ({}, {}): {} enemies hit ({} champions) for {base}",
                             head(sim, me), at.0, at.1, hit.len(), hit.iter().filter(|h| h.1).count()));
            }
        }
    }
}

impl StablePassive for Scurvy {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Gangplank (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
        // the Silver Serpents' gold goes to his player; he spawns in his fountain
        self.sv.player = Some(player);
        if let Some(pos) = sim.get_entity(me).map(|e| e.pos()) {
            self.fountain(sim, me, pos);
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        let mine: Vec<(u64, u64)> = (0..sim.projectile_count())
            .filter_map(|i| sim.projectile_at(i))
            .filter(|q| q.caster_id == me && !q.is_end)
            .map(|q| (q.x, q.y))
            .collect();
        if alive {
            self.cleanse(sim, me);
        }
        self.low_flag(sim, me, alive);
        // chain before track: the blast takes k<s>_live off and raises k<s>_now in one tick (0.2.2)
        self.chain(sim, me);
        self.track(sim, me, now, &mine);
        // after track: a keg the data blew is forgotten by now; one it left lit is blown here (0.2.3)
        if alive {
            self.recheck(sim, me, now);
        }
        self.charges(sim, me, now);
        self.triple_barrel(sim, me, now);
        self.third_boom(sim, me, now);
        self.serpents(sim, me, now, alive);
        self.prev = mine;
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Gangplank: Remove Scurvy cleanses and is eaten at low health, kegs chain) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:scurvy"), Scurvy::default());
    host.log(LogLevel::Info, "league_gangplank loaded (Remove Scurvy cleanses and is eaten at low health, kegs chain).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    fn p() -> Params {
        Params::default()
    }

    #[test]
    fn params_from_the_kit() {
        assert_eq!(parse_params(concat!(r#"{"e_chain":70000,"e_champ":60,"e_dmg":40,"e_gap":60,"e_link":10,"e_pen":40,"#,
                                        r#""e_r":30000,"e_range":70000,"e_ratio":100,"e_slow":40,"e_slow_t":120,"#,
                                        r#""e_stock":3,"p_ms":20,"p_ms_t":120,"sv_cost":500,"sv_gold":100,"#,
                                        r#""sv_home":60000,"sv_rank_t":10800,"sv_scale":1000,"w_low":40}"#)),
                   Params::default());
        let read = parse_params(r#"{"sv_scale":700,"sv_rank_t":9000,"sv_cost":400,"sv_gold":50,"sv_home":1}"#);
        assert_eq!((read.sv_scale, read.sv_rank_t, read.sv_cost, read.sv_gold, read.sv_home), (700, 9000, 400, 50, 1));
    }

    #[test]
    fn plunder_follows_the_clock() {
        let pp = p();
        let at = |rank: usize| (rank - 1) * pp.sv_rank_t;
        // League's 4-8 serpents and 3-7 gold a kill at Parrrley's ranks 1-5; x10 serpents here (sv_scale 1000)
        assert_eq!((q_rank(&pp, 0), plunder(&pp, 0), plunder_gold(&pp, 0)), (1, 40, 3));
        assert_eq!((q_rank(&pp, at(2) - 1), plunder(&pp, at(2) - 1)), (1, 40));
        assert_eq!((q_rank(&pp, at(2)), plunder(&pp, at(2)), plunder_gold(&pp, at(2))), (2, 50, 4));
        assert_eq!((q_rank(&pp, at(5)), plunder(&pp, at(5)), plunder_gold(&pp, at(5))), (5, 80, 7));
        assert_eq!((q_rank(&pp, at(9)), plunder(&pp, at(9))), (5, 80), "rank 5 is the last");
        // at 100 % it is League's own count
        let league = Params { sv_scale: 100, ..pp };
        assert_eq!((plunder(&league, 0), plunder(&league, at(5))), (4, 8));
        // sv_rank_t 0 does not divide by zero
        assert_eq!(q_rank(&Params { sv_rank_t: 0, ..pp }, 5), 5);
    }

    #[test]
    fn upgrades_follow_the_match() {
        let none = [false; 3];
        let pick = |bought: [bool; 3], s: Situation| choose(bought, &s).map(|c| c.0);
        let even = Situation { foe_armour: 1.0, ..Situation::default() };
        // even and no barrage seen yet: Death's Daughter, then Fire at Will, then Raise Morale (ties go by ALL)
        assert_eq!(pick(none, even), Some(Upgrade::Daughter));
        assert_eq!(pick([true, false, false], even), Some(Upgrade::FireAtWill));
        assert_eq!(pick([true, true, false], even), Some(Upgrade::Morale));
        assert_eq!(pick([true; 3], even), None);
        // ahead: Fire at Will; behind: Death's Daughter, even with his barrages on crowds
        let ahead = Situation { kill_diff: AHEAD, ..even };
        assert_eq!(pick(none, ahead), Some(Upgrade::FireAtWill));
        assert_eq!(pick(none, Situation { kill_diff: AHEAD - 1, ..even }), Some(Upgrade::Daughter));
        assert_eq!(pick(none, Situation { kill_diff: BEHIND, foes_per: 3.0, barrages: 5, ..even }), Some(Upgrade::Daughter));
        // his barrages on crowds: Fire at Will; foes tankier than his team on top of that: Death's Daughter (a tie)
        let crowd = Situation { foes_per: CROWD, barrages: SEEN, ..even };
        assert_eq!(pick(none, crowd), Some(Upgrade::FireAtWill));
        assert_eq!(pick(none, Situation { foe_armour: TANKY, ..crowd }), Some(Upgrade::Daughter));
        // allies in his barrages: Raise Morale - not before SEEN barrages
        let allies = Situation { allies_per: WITH_ALLIES, foes_per: 1.0, barrages: SEEN, ..even };
        assert_eq!(pick(none, allies), Some(Upgrade::Morale));
        assert_eq!(pick(none, Situation { barrages: SEEN - 1, ..allies }), Some(Upgrade::Daughter));
        assert_eq!(pick([false, false, true], allies), Some(Upgrade::Daughter));
        // the reason for the log
        assert_eq!(choose(none, &ahead).unwrap().1, "score 4: ahead");
        assert_eq!(choose(none, &even).unwrap().1, "score 2");
        assert_eq!(choose(none, &Situation { kill_diff: BEHIND, foe_armour: 2.0, ..even }).unwrap().1,
                   "score 5: behind, tanky foes");
    }

    #[test]
    fn serpent_count_on_the_panel() {
        // league.dll's stack box reads the number after `league_gangplank_sv_` (tools/kit/stack_nums.py)
        assert_eq!(count_name(0), "league_gangplank_sv_0");
        assert_eq!(count_name(1230), "league_gangplank_sv_1230");
    }

    #[test]
    fn low_health_line() {
        assert!(low(&p(), 399, 1000));
        assert!(!low(&p(), 400, 1000));
        assert!(!low(&p(), 0, 1000));
    }

    #[test]
    fn chain_reach() {
        assert!(within((100000, 100000), (170000, 100000), p().e_chain));
        assert!(!within((100000, 100000), (170001, 100000), p().e_chain));
    }

    #[test]
    fn three_kegs_in_hand() {
        let p = p();
        let mut st = Stock::default();
        // E unlocks ready with one keg; nothing to cut
        assert_eq!(st.step(&p, 100, 0, 480), (0, false));
        assert_eq!(st.n, 1);
        // the first throw: none left, the cooldown runs whole
        assert_eq!(st.step(&p, 101, 480, 480), (0, true));
        assert_eq!(st.n, 0);
        // a full cycle later (from the unlock) a keg is back: the cooldown is cut to what is left of e_gap (none)
        let (cut, thrown) = st.step(&p, 580, 400, 480);
        assert_eq!((cut, thrown, st.n), (400, false, 1));
        // two more cycles: three in hand, no more
        for t in 581..2000 {
            st.step(&p, t, 0, 480);
        }
        assert_eq!(st.n, 3);
        // a throw with kegs left: the cooldown keeps e_gap only
        assert_eq!(st.step(&p, 2000, 480, 480), (480 - p.e_gap, true));
        assert_eq!(st.n, 2);
        assert!(st.take(&p, 2001, 480));
        assert_eq!(st.n, 1);
    }

    #[test]
    fn triple_barrel_needs_two_linked_kegs_and_a_champion_outside_them() {
        let p = p();
        let a = (0, (100000, 100000));
        let b = (1, (160000, 100000)); // 60000 from a: linked
        let foe = (7, (220000, 100000)); // 60000 from b, out of both blasts
        assert_eq!(triple(&p, &[a, b], &[foe]), Some((1, 7, (220000, 100000))));
        // one keg: no triple
        assert_eq!(triple(&p, &[b], &[foe]), None);
        // kegs not linked
        assert_eq!(triple(&p, &[a, (1, (250000, 100000))], &[(7, (300000, 100000))]), None);
        // the champion already inside a keg's blast: the data blows that keg itself
        assert_eq!(triple(&p, &[a, b], &[(7, (180000, 100000))]), None);
        // too far from every keg
        assert_eq!(triple(&p, &[a, b], &[(7, (240000, 100000))]), None);
    }

    #[test]
    fn a_keg_blown_by_the_data_is_still_placed_when_the_chain_reads_it() {
        // 11-04 logs: 0 CHAIN all day. The blast takes k1_live off and raises k1_now in one Delayed: on that tick
        // chain() must read keg 1's point before track() forgets it
        let mut gp = Scurvy { kegs: [Some((100000, 100000)), Some((160000, 100000)), None], ..Scurvy::default() };
        let (live, now) = ([false, true, false], [true, false, false]);
        // 0.2.2's order: the blown keg's point first, then the slot is dropped
        assert_eq!(gp.blown(now), vec![(0, (100000, 100000))]);
        gp.forget(live);
        assert_eq!(gp.kegs, [None, Some((160000, 100000)), None]);
        // k1_now still up next tick: no second blast; the keg landing again later is a new one
        assert_eq!(gp.blown(now), vec![]);
        gp.kegs[0] = Some((300000, 300000));
        assert_eq!(gp.blown([false, false, false]), vec![]);
        assert_eq!(gp.blown([true, false, false]), vec![(0, (300000, 300000))]);
        // the old order (0.2.1): forget first, nothing to chain from
        let mut old = Scurvy { kegs: [Some((100000, 100000)), Some((160000, 100000)), None], ..Scurvy::default() };
        old.forget(live);
        assert_eq!(old.blown(now), vec![]);
    }

    #[test]
    fn a_keg_left_to_the_data_is_blown_when_the_data_did_not() {
        // 11-06's logs: m=2848 keg 3 "left to the data (an enemy beside it)" at t=20202, still lit and chained again at
        // 20246 - the enemy stood within e_r + 20000 but outside the data's e_r
        let at = (26555, 270358);
        let mut handed = Vec::new();
        hand(&mut handed, 20202, 2, at);
        hand(&mut handed, 20203, 2, at); // chained again before the look: still one look, at the first one's tick
        assert_eq!(handed, vec![Handed { due: 20202 + RECHECK, slot: 2, at }]);
        let kegs = [None, Some((1, 1)), Some(at)];
        let lit = [false, true, true];
        assert!(late_blows(&mut handed, 20202 + RECHECK - 1, &kegs, lit).is_empty(), "the data's ticks first");
        assert_eq!(handed.len(), 1);
        assert_eq!(late_blows(&mut handed, 20202 + RECHECK, &kegs, lit), vec![(2, at)]);
        assert!(handed.is_empty(), "looked at once");
        // the data blew it: its slot forgotten (track) or no longer lit - nothing to do
        hand(&mut handed, 100, 2, at);
        assert!(late_blows(&mut handed, 100 + RECHECK, &[None, None, None], lit).is_empty());
        hand(&mut handed, 100, 2, at);
        assert!(late_blows(&mut handed, 100 + RECHECK, &kegs, [false, true, false]).is_empty());
        // a new keg in the slot by then is not the one handed over
        hand(&mut handed, 200, 2, at);
        assert!(late_blows(&mut handed, 200 + RECHECK, &[None, None, Some((5, 5))], lit).is_empty());
        // he died meanwhile (his passive did not run): a look long overdue is dropped at his respawn
        hand(&mut handed, 300, 2, at);
        assert!(late_blows(&mut handed, 300 + 3 * RECHECK, &kegs, lit).is_empty());
        assert!(handed.is_empty());
        // two slots due together: both
        hand(&mut handed, 400, 1, (1, 1));
        hand(&mut handed, 400, 2, at);
        assert_eq!(late_blows(&mut handed, 400 + RECHECK, &kegs, lit), vec![(1, (1, 1)), (2, at)]);
    }

    #[test]
    fn keg_is_the_new_pair() {
        let base = [(5, 5), (9, 9)];
        assert_eq!(keg_point(&base, &[(5, 5), (9, 9), (40, 50), (40, 50), (7, 7)]), Some((40, 50)));
        // a bullet alone is no keg; a zone already there before is not new
        assert_eq!(keg_point(&base, &[(5, 5), (9, 9), (7, 7)]), None);
        assert_eq!(keg_point(&[(40, 50), (40, 50)], &[(40, 50), (40, 50)]), None);
        // the other keg's pair stays, the new pair is found beside it
        assert_eq!(keg_point(&[(40, 50), (40, 50)], &[(40, 50), (40, 50), (80, 90), (80, 90)]), Some((80, 90)));
    }
}
