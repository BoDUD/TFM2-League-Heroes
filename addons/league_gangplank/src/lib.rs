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
//!   加速。空炸的桶也接着往下连锁（v0.2.0 起三个桶位）。
//! - **火药桶能存 3 次**（v0.2.0，英雄联盟：E 有充能）：数据里 E 只有一个冷却。本包自己记充能（`e_stock` 个，每过一轮 E 的
//!   冷却回一个）：E 放出去后手里还有桶，就把 E 的冷却减到只剩 `e_gap`（`entity_reduce_cooldown`），AI 很快能再扔。
//! - **三连桶**（v0.2.0，英雄联盟：两个连着的桶，开枪打第一个，子弹飞的时候往敌人脚下扔第三个）：枪火谈判打中（`q_fire`
//!   出现）的那个 tick，两个点燃的桶相距不超过 `e_chain`、有个敌方英雄在其中一个桶的 `e_chain` 以内却不在任何桶的爆炸范围里、
//!   手里还有桶：用掉一个桶，往他脚下扔第三个（落地画面），离他最近的那个桶炸开（桶边没人由本包空炸，有人由数据照常炸），
//!   连锁带上另一个，`THIRD_FUSE` tick 后第三个桶在他脚下炸开：伤害、无视护甲、减速、摘 `p_cd`、被动加速都照数据的桶。
//!   本包不按任何技能键。
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
/// 桶边「没有敌人」要比数据的触发区再宽这么多才算（数据看得到的边上的敌人留给数据炸）。
const EMPTY_MARGIN: u64 = 20000;
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

/// 桶边 r 以内有没有活着的敌方单位（防御塔不算，数据的触发区是 EnemyWithoutTower）。
fn enemy_near(sim: &StableSim<'_>, team: usize, at: (u64, u64), r: u64) -> bool {
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|e| {
        e.is_alive() && e.team() != team && e.kind() != Some(EntityKindV1::Tower) && within(e.pos(), at, r)
    })
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
}

impl Scurvy {
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

    /// 桶落地时记下它的位置。
    fn track(&mut self, sim: &StableSim<'_>, me: usize, now: usize, mine: &[(u64, u64)]) {
        for s in 0..SLOTS {
            let live = has(sim, me, &sn(&format!("k{}_live", s + 1)));
            if live && !self.had_live[s] {
                self.pending[s] = Some((now, self.prev.clone()));
                self.kegs[s] = None;
            }
            if !live {
                self.kegs[s] = None;
                self.pending[s] = None;
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

    /// 一个桶炸开：别的点燃的桶在 e_chain 以内就连锁。
    fn chain(&mut self, sim: &mut StableSim<'_>, me: usize) {
        for s in 0..SLOTS {
            let blew = has(sim, me, &sn(&format!("k{}_now", s + 1)));
            if blew && !self.had_now[s] {
                self.chain_from(sim, me, s);
            }
            self.had_now[s] = blew;
        }
    }

    fn chain_from(&mut self, sim: &mut StableSim<'_>, me: usize, s: usize) {
        for o in (0..SLOTS).filter(|&o| o != s) {
            let k = |x: &str| sn(&format!("k{}_{x}", o + 1));
            let (Some(from), Some(at)) = (self.kegs[s], self.kegs[o]) else { continue };
            if !has(sim, me, &k("ripe")) || !has(sim, me, &k("live")) || !within(from, at, self.p.e_chain) {
                continue;
            }
            refresh(sim, me, &BuffV1::timed(&k("cn"), 3));
            let empty = self.blow_if_empty(sim, me, o);
            if let Some(n) = counted("chain") {
                wlog(format!("{} CHAIN #{n}: keg {} blew, keg {} at ({}, {}) {}", head(sim, me), s + 1, o + 1, at.0, at.1,
                             if empty { "blown empty here" } else { "left to the data (an enemy beside it)" }));
            }
            if empty {
                self.chain_from_empty(sim, me, o, at);
            }
        }
    }

    /// 空炸的桶接着连锁（数据炸的桶由 `k<s>_now` 接着连）。
    fn chain_from_empty(&mut self, sim: &mut StableSim<'_>, me: usize, o: usize, at: (u64, u64)) {
        self.kegs[o] = Some(at);
        self.chain_from(sim, me, o);
        self.kegs[o] = None;
    }

    /// 桶边 e_r + EMPTY_MARGIN 以内没有敌方单位就由本包空炸（画面、摘 p_cd、加速同数据的爆炸）；有人就留给数据。
    fn blow_if_empty(&mut self, sim: &mut StableSim<'_>, me: usize, o: usize) -> bool {
        let Some(at) = self.kegs[o] else { return false };
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if enemy_near(sim, team, at, self.p.e_r + EMPTY_MARGIN) {
            return false;
        }
        let k = |x: &str| sn(&format!("k{}_{x}", o + 1));
        refresh(sim, me, &BuffV1::timed(&k("blew"), self.p.e_link + 1));
        sim.entity_remove_buff(me, &k("live"));
        sim.entity_remove_buff(me, &k("ripe"));
        self.fired_up(sim, me);
        self.kegs[o] = None;
        true
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
        let empty = self.blow_if_empty(sim, me, s);
        if let (true, Some(from)) = (empty, first) {
            self.chain_from_empty(sim, me, s, from);
        }
        if let Some(k) = counted("triple") {
            wlog(format!("{} TRIPLE #{k}: kegs {:?} lit, the third thrown at #{foe} ({}, {}), keg {} goes first ({}), {} in hand",
                         head(sim, me), ripe.iter().map(|k| k.0 + 1).collect::<Vec<_>>(), at.0, at.1, s + 1,
                         if empty { "blown empty here" } else { "the data's, an enemy beside it" }, self.stock.n));
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
        self.track(sim, me, now, &mine);
        self.chain(sim, me);
        self.charges(sim, me, now);
        self.triple_barrel(sim, me, now);
        self.third_boom(sim, me, now);
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
                                        r#""e_stock":3,"p_ms":20,"p_ms_t":120,"w_low":40}"#)),
                   Params::default());
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
