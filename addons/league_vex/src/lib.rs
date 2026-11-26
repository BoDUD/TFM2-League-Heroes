//! 薇古丝附加包：照英雄联盟 V26.13 做主包数据做不到的部分（用户 2026-10-20：技能方案 A，做附加包；2026-11-26 再核对一遍）。
//!
//! 主包保持纯数据：数据只能读她自己身上的 buff，读不到敌人身上的暮气、读不到等级（只有到没到 3 级）、看不到别人在突进，
//! 也刷新不了大招。`mod.override_info` 把主包的薇古丝换成 `override/` 里的副本（`tools/kit/build_vex.py --native`），
//! 被动 `league_vex:gloom`：
//!
//! - **暮气**：溟濛渐染打中的敌人挂 `league_vex_g_mark`（`g_t` tick，主包也挂）；她 `p_dash_r` 以内突进或闪现的敌方英雄和野怪
//!   （一 tick 里移动了 `DASH_STEP` 到 `BLINK_MAX`，被击退、拉拽、击飞的不算）也被挂上。副本里她的普攻、Q、W 打中的单位挂
//!   2 tick 的 `league_vex_v_hit`（E、R 不挂：英雄联盟里它们不引爆）；带暮气的单位被她打中就**引爆**：摘掉暮气，补魔法伤害
//!   （`g_lo` 到 `g_hi` 按等级 + `g_ratio`% 法强，对非英雄只打 `g_u_lo`% 到 `g_u_hi`%），终焉的等待缩短 `g_cut`%（非英雄 `g_cut_u`%）。
//! - **终焉**：数据用掉终焉时给她挂 `league_vex_p_wait`（`p_cd1` tick）；本包看到新挂上的就按等级改成英雄联盟的比例
//!   （25 / 22 / 19 / 16），复活时清掉（英雄联盟：复活时重置）；等待结束时放 `p_ready` 的画面和声音。
//! - **恐惧**：副本里终焉的 Q / W 打中的挂 `league_vex_f_q`、E 打中的挂 `league_vex_f_e`；本包放恐惧：时长按等级
//!   （`p_fear` 到 `p_fear4`），Q / W 的背着她跑，E 的背着 E 的中心跑；恐惧时减速，离她越远越大（`p_fs_lo`% 到 `p_fs_hi`%）。
//!   击倒（打断冲刺）是数据里那 2 tick 的击飞。
//! - **溟濛渐染**：出手时目标挂 `league_vex_e_aim`，本包记下影子落在哪；落地时在那一圈里死掉的，终焉等待缩短 `e_cut_c`%
//!   （英雄）/ `e_cut`%（别的）。
//! - **愁煞**：飞弹打中的英雄挂 `league_vex_r_mark`（标记先挂、再扣血，飞弹自己打死他也看得到）。本包看这一下冲上去能不能
//!   杀他（冲击 + 好了的生人勿近，按他的魔抗算，`r_kill`%），他身边别的敌方英雄不超过 `r_crowd` 个，就给她挂 `league_vex_r_in`：
//!   数据冲到他身上（冲刺时免控），否则停在他外面。他在 `r_reset` tick 内阵亡（谁杀的都算，她打过他就有助攻），
//!   `r_free` tick 后愁煞能再放。
//!
//! 游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列，下一次 on_update 之前才扣血（莉莉娅 0.1.2 的教训）：引爆补的伤害不挂
//! `v_hit`，不会再引爆一次。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个薇古丝自己的被动实例里，
//! 服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vex.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `GLOOM`（引爆）、`DASH`（突进挂暮气）、`DOOM`（终焉好了 / 冷却按等级 / 复活重置）、`FEAR`（恐惧）、`EKILL`（E 打死人）、
//! `SURGE`（冲不冲上去）、`RESET`（大招刷新）、`WATCH`（每 30 秒的计数），都限了条数。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_vex";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_vex") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 突进：连着两 tick 平均每 tick 走了至少 `DASH_STEP`、也至少是他移速的 `DASH_X` 倍（走路一 tick 走一个移速；引擎偶尔
/// 一 tick 不动、下一 tick 补两步，两 tick 平均就不会当成突进）。闪现也算（英雄联盟 400 码 = 40000），一 tick 超过
/// `BLINK_MAX` 的是传送、回城、复活，不算。
pub const DASH_STEP: f64 = 2_200.0;
pub const DASH_X: f64 = 2.0;
pub const BLINK_MAX: f64 = 100_000.0;
/// 这个游戏的最高等级。
pub const MAX_LEVEL: usize = 12;
/// 终焉冷却按等级的比例（英雄联盟 25 / 22 / 19 / 16 秒，1 / 6 / 11 / 16 级；这里 1 / 5 / 8 / 11 级）。
pub const DOOM_STEPS: [usize; 4] = [25, 22, 19, 16];
/// 看他身边有几个敌方英雄的半径（冲上去会不会被围）。
pub const CROWD_R: f64 = 60_000.0;
/// 冷却清零时一次减掉的 tick（比任何大招的冷却都长）。
const RESET_TICKS: usize = 100_000;

/// 主包薇古丝的名字（buff、声音、画面都以它开头）。
fn vx(x: &str) -> String {
    format!("league_vex_{x}")
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VEX_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_vex.log");
        }
    }
    PathBuf::from("league_vex.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    // the file stays open (league_lillia's log_open_once fix: opening it for every line stalled the simulation thread)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// 每种行前 10 条都写，之后每 25 条写一条。
fn logged(n: usize) -> bool {
    n <= 10 || n % 25 == 0
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

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 终焉 1 级的冷却（tick），恐惧 1 级 / 11 级以上的时长，恐惧减速（离她 0 / `p_fs_d` 以外的 %）。
    pub p_cd1: usize,
    pub p_fear: usize,
    pub p_fear4: usize,
    pub p_fs_lo: usize,
    pub p_fs_hi: usize,
    pub p_fs_d: usize,
    /// 突进 / 闪现的人离她多近会被挂上暮气。
    pub p_dash_r: usize,
    /// 暮气：持续 tick；引爆伤害 1 级 / 12 级、法强 %；对非英雄打几成（1 级 / 12 级 %）；终焉等待缩短的 %（英雄 / 别的）。
    pub g_t: usize,
    pub g_lo: usize,
    pub g_hi: usize,
    pub g_ratio: usize,
    pub g_u_lo: usize,
    pub g_u_hi: usize,
    pub g_cut: usize,
    pub g_cut_u: usize,
    /// E 打死别的 / 英雄缩短终焉等待的 %；E 的半径、影子飞几 tick。
    pub e_cut: usize,
    pub e_cut_c: usize,
    pub e_r: usize,
    pub e_fly: usize,
    /// 愁煞：标记后多少 tick 内阵亡算数，刷新后多少 tick 能再放；冲上去前等几 tick；多大把握算杀得死（%）、他身边最多几个
    /// 别的敌方英雄；冲击和生人勿近的伤害（估算能不能杀）。
    pub r_reset: usize,
    pub r_free: usize,
    pub r_wait: usize,
    pub r_kill: usize,
    pub r_crowd: usize,
    pub r2_dmg: usize,
    pub r2_ratio: usize,
    pub w_dmg: usize,
    pub w_ratio: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_cd1: 1030, p_fear: 45, p_fear4: 90, p_fs_lo: 60, p_fs_hi: 99, p_fs_d: 80000, p_dash_r: 160000, g_t: 360,
            g_lo: 26, g_hi: 107, g_ratio: 25, g_u_lo: 40, g_u_hi: 60, g_cut: 25, g_cut_u: 10, e_cut: 10, e_cut_c: 25,
            e_r: 25000, e_fly: 18, r_reset: 480, r_free: 30, r_wait: 8, r_kill: 100, r_crowd: 1, r2_dmg: 164,
            r2_ratio: 50, w_dmg: 105, w_ratio: 30,
        }
    }
}

/// `{"g_lo":40,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "p_cd1" => &mut p.p_cd1,
            "p_fear" => &mut p.p_fear,
            "p_fear4" => &mut p.p_fear4,
            "p_fs_lo" => &mut p.p_fs_lo,
            "p_fs_hi" => &mut p.p_fs_hi,
            "p_fs_d" => &mut p.p_fs_d,
            "p_dash_r" => &mut p.p_dash_r,
            "g_t" => &mut p.g_t,
            "g_lo" => &mut p.g_lo,
            "g_hi" => &mut p.g_hi,
            "g_ratio" => &mut p.g_ratio,
            "g_u_lo" => &mut p.g_u_lo,
            "g_u_hi" => &mut p.g_u_hi,
            "g_cut" => &mut p.g_cut,
            "g_cut_u" => &mut p.g_cut_u,
            "e_cut" => &mut p.e_cut,
            "e_cut_c" => &mut p.e_cut_c,
            "e_r" => &mut p.e_r,
            "e_fly" => &mut p.e_fly,
            "r_reset" => &mut p.r_reset,
            "r_free" => &mut p.r_free,
            "r_wait" => &mut p.r_wait,
            "r_kill" => &mut p.r_kill,
            "r_crowd" => &mut p.r_crowd,
            "r2_dmg" => &mut p.r2_dmg,
            "r2_ratio" => &mut p.r2_ratio,
            "w_dmg" => &mut p.w_dmg,
            "w_ratio" => &mut p.w_ratio,
            _ => continue,
        };
        *slot = v;
    }
    for c in [&mut p.g_cut, &mut p.g_cut_u, &mut p.e_cut, &mut p.e_cut_c, &mut p.p_fs_lo, &mut p.p_fs_hi] {
        *c = (*c).min(100);
    }
    p.p_fs_d = p.p_fs_d.max(1);
    p
}

// ===================== 计算 =====================

/// 第几档（0–3）：1–4 级、5–7 级、8–10 级、11 级以上（英雄联盟 1 / 6 / 11 / 16 级）。
pub fn rank4(level: usize) -> usize {
    match level {
        0..=4 => 0,
        5..=7 => 1,
        8..=10 => 2,
        _ => 3,
    }
}

/// 1 级到 12 级之间的位置（0 到 11）。
fn lvl(level: usize) -> usize {
    level.clamp(1, MAX_LEVEL) - 1
}

/// 这一级终焉的冷却（tick）。
pub fn doom_cd(p: &Params, level: usize) -> usize {
    p.p_cd1 * DOOM_STEPS[rank4(level)] / DOOM_STEPS[0]
}

/// 这一级恐惧的时长（tick）。
pub fn fear_ticks(p: &Params, level: usize) -> usize {
    let (lo, hi) = (p.p_fear, p.p_fear4.max(p.p_fear));
    lo + (hi - lo) * rank4(level) / 3
}

/// 恐惧时的减速 %：离她越远越大。
pub fn fear_slow(p: &Params, dist: f64) -> usize {
    let (lo, hi) = (p.p_fs_lo, p.p_fs_hi.max(p.p_fs_lo));
    let d = dist.clamp(0.0, p.p_fs_d as f64);
    lo + ((hi - lo) as f64 * d / p.p_fs_d as f64).round() as usize
}

/// 引爆暮气的魔法伤害（减免前）：她的等级、法强，打的是不是英雄。
pub fn gloom_damage(p: &Params, level: usize, ap: usize, champion: bool) -> usize {
    let l = lvl(level);
    let base = p.g_lo + p.g_hi.saturating_sub(p.g_lo) * l / (MAX_LEVEL - 1);
    let full = base + p.g_ratio * ap / 100;
    if champion {
        return full;
    }
    let share = p.g_u_lo + p.g_u_hi.saturating_sub(p.g_u_lo) * l / (MAX_LEVEL - 1);
    full * share / 100
}

/// 终焉还要等 `left` tick 时缩短 `pct`% 后还要等多久。
pub fn doom_after_cut(left: usize, pct: usize) -> usize {
    left * (100 - pct.min(100)) / 100
}

/// 这一 tick 走了 `step`、上一 tick 走了 `prev`、移速 `ms`：算不算突进 / 闪现（传送、回城、复活那么远的不算）。
pub fn is_dash(step: f64, prev: f64, ms: usize) -> bool {
    step <= BLINK_MAX && (step + prev) / 2.0 >= DASH_STEP.max(DASH_X * ms as f64)
}

/// 魔法伤害过了魔抗还剩多少。
pub fn after_mr(dmg: usize, mr: usize) -> usize {
    dmg * 100 / (100 + mr)
}

/// 冲上去这一下（估算的伤害 `est`，已经过了魔抗）能不能杀掉还剩 `hp` 的他。
pub fn kills(p: &Params, hp: usize, est: usize) -> bool {
    hp * 100 <= est * p.r_kill
}

fn dist(a: (u64, u64), b: (u64, u64)) -> f64 {
    let dx = a.0 as f64 - b.0 as f64;
    let dy = a.1 as f64 - b.1 as f64;
    (dx * dx + dy * dy).sqrt()
}

/// 从 `from` 指向 `to` 的方向（恐惧往这边跑）；两点重合时往右。
pub fn away(from: (u64, u64), to: (u64, u64)) -> (i64, i64) {
    let dx = to.0 as i64 - from.0 as i64;
    let dy = to.1 as i64 - from.1 as i64;
    if dx == 0 && dy == 0 { (1000, 0) } else { (dx, dy) }
}

// ===================== 被动 =====================

/// 这一 tick 看到的一个敌方单位。
#[derive(Clone, Debug, Default)]
struct Seen {
    id: usize,
    pos: (u64, u64),
    alive: bool,
    champion: bool,
    monster: bool,
    hp: usize,
    mr: usize,
    ms: usize,
    gloom: bool,
    hit: bool,
    f_q: bool,
    f_e: bool,
    e_aim: bool,
    r_mark: bool,
    /// 被击退、拉拽、击飞着（不是自己冲的）。
    displaced: bool,
    /// 身上有免控的 buff（黑盾之类）：终焉的恐惧不吃。
    immune: bool,
}

/// 一次溟濛渐染：影子落在哪、什么时候落地，落地前那一圈里还活着的人。
#[derive(Clone, Debug, Default)]
struct ECast {
    at: (u64, u64),
    land: usize,
    watch: Vec<(usize, bool)>,
}

/// 每个薇古丝一份。
#[derive(Clone, Default)]
struct Gloom {
    p: Params,
    /// 上一 tick 身上有暮气 / 她的打中标记的单位（一下只引爆一次）。
    gloomed: Vec<usize>,
    hit_seen: Vec<usize>,
    /// 每个敌方英雄和野怪上一 tick 的位置、那一 tick 走了多远。
    last_pos: Vec<(usize, (u64, u64), f64)>,
    /// 上一 tick 她身上有终焉的等待、她活着。
    waiting: bool,
    alive: bool,
    /// 最近一次溟濛渐染。
    e: Option<ECast>,
    /// 愁煞打中的英雄和刷新的截止 tick。
    marked: Vec<(usize, usize)>,
    r_seen: Vec<usize>,
    pops: usize,
    dashes: usize,
    dooms: usize,
    fears: usize,
    e_kills: usize,
    surges: usize,
    resets: usize,
    next_report: usize,
}

fn buff_of(sim: &StableSim<'_>, id: usize, name: &str) -> Option<BuffV1> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == name)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buff_of(sim, id, name).is_some()
}

/// 敌方单位一遍（防御塔、水晶除外）。
fn scan(sim: &StableSim<'_>, team: usize) -> Vec<Seen> {
    let names = [vx("g_mark"), vx("v_hit"), vx("f_q"), vx("f_e"), vx("e_aim"), vx("r_mark")];
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || e.is_tower() {
            continue;
        }
        let kind = e.kind();
        if matches!(kind, Some(EntityKindV1::Nexus) | Some(EntityKindV1::Tower)) {
            continue;
        }
        let mut s = Seen { id: e.id(), pos: e.pos(), alive: e.is_alive(), champion: e.is_champion(), ..Seen::default() };
        s.monster = matches!(kind, Some(EntityKindV1::Jungle) | Some(EntityKindV1::Epic));
        s.hp = e.hp().0;
        let st = e.stat();
        s.mr = st.magic_resistance;
        s.ms = st.move_speed;
        for k in 0..e.buff_count() {
            let Some(b) = e.buff_at(k) else { continue };
            s.immune |= b.cc_immune;
            let n = b.name();
            s.gloom |= n == names[0];
            s.hit |= n == names[1];
            s.f_q |= n == names[2];
            s.f_e |= n == names[3];
            s.e_aim |= n == names[4];
            s.r_mark |= n == names[5];
        }
        let moved = |c: &CcV1| c.kind == CcKindV1::ForceMove.code() || c.kind == CcKindV1::Airborne.code();
        s.displaced = (0..e.cc_count()).filter_map(|k| e.cc_at(k)).any(|c| moved(&c));
        out.push(s);
    }
    out
}

impl Gloom {
    /// 终焉等待剩下的缩短 `pct`%：-> (原来, 现在)。
    fn cut_doom(&self, sim: &mut StableSim<'_>, me: usize, pct: usize) -> Option<(usize, usize)> {
        let b = buff_of(sim, me, &vx("p_wait"))?;
        let rest = doom_after_cut(b.duration_tick, pct);
        sim.entity_remove_buff(me, &vx("p_wait"));
        if rest > 0 {
            sim.add_buff(me, &BuffV1::timed(&vx("p_wait"), rest));
        }
        Some((b.duration_tick, rest))
    }

    /// 终焉：新挂上的等待按等级改，复活时清掉，等完了放「终焉好了」。
    fn doom(&mut self, sim: &mut StableSim<'_>, me: usize, alive: bool, level: usize) {
        let mut waiting = buff_of(sim, me, &vx("p_wait"));
        if alive && !self.alive && waiting.is_some() {
            sim.entity_remove_buff(me, &vx("p_wait"));
            waiting = None;
            wlog(format!("{} DOOM: back on respawn", head(sim, me)));
        }
        if let Some(b) = waiting.filter(|_| !self.waiting) {
            let want = doom_cd(&self.p, level);
            if want != b.duration_tick {
                sim.entity_remove_buff(me, &vx("p_wait"));
                sim.add_buff(me, &BuffV1::timed(&vx("p_wait"), want));
            }
            if self.dooms < 6 {
                wlog(format!("{} DOOM: spent at level {level}, back in {want} ticks", head(sim, me)));
            }
        }
        let now = waiting.is_some();
        if self.waiting && !now && alive {
            let at = InputTargetV1::target(me);
            sim.play_view_effect(&vx("p_ready"), me, &at, 0, 0, 0);
            sim.play_sfx(&vx("p_ready"), me, &at);
            self.dooms += 1;
            if self.dooms <= 6 {
                wlog(format!("{} DOOM #{}: ready", head(sim, me), self.dooms));
            }
        }
        self.waiting = now;
        self.alive = alive;
    }

    /// 暮气：她打中带暮气的单位就引爆。
    fn detonate(&mut self, sim: &mut StableSim<'_>, me: usize, seen: &[Seen], ap: usize, level: usize) {
        let mut popped = Vec::new();
        for s in seen.iter().filter(|s| s.alive && s.hit) {
            // a mark laid this very tick (E lands and the add-on sees it with her hit) waits for the next hit
            if self.hit_seen.contains(&s.id) || !s.gloom || !self.gloomed.contains(&s.id) {
                continue;
            }
            sim.entity_remove_buff(s.id, &vx("g_mark"));
            let dmg = gloom_damage(&self.p, level, ap, s.champion);
            sim.deal_damage_typed(me, s.id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            let at = InputTargetV1::target(s.id);
            sim.play_view_effect(&vx("g_pop"), me, &at, 0, 0, 0);
            sim.play_sfx(&vx("g_pop"), me, &at);
            popped.push(s.id);
            self.pops += 1;
            let cut = self.cut_doom(sim, me, if s.champion { self.p.g_cut } else { self.p.g_cut_u });
            if logged(self.pops) {
                wlog(format!("{} GLOOM #{}: #{} ({}) popped for {dmg} magic at level {level}; Doom wait {cut:?}",
                             head(sim, me), self.pops, s.id, if s.champion { "champion" } else { "unit" }));
            }
        }
        self.gloomed = seen.iter().filter(|s| s.alive && s.gloom && !popped.contains(&s.id)).map(|s| s.id).collect();
        self.hit_seen = seen.iter().filter(|s| s.hit).map(|s| s.id).collect();
    }

    /// 她身边突进 / 闪现的敌方英雄和野怪挂上暮气（被别人击退、拉拽、击飞的不算）。
    fn dashes(&mut self, sim: &mut StableSim<'_>, me: usize, seen: &[Seen], pos: (u64, u64), alive: bool) {
        let mut now = Vec::new();
        for s in seen.iter().filter(|s| s.alive && (s.champion || s.monster)) {
            let Some(&(_, was, prev)) = self.last_pos.iter().find(|x| x.0 == s.id) else {
                now.push((s.id, s.pos, 0.0));
                continue;
            };
            let step = dist(was, s.pos);
            now.push((s.id, s.pos, step));
            if !alive || s.displaced || dist(pos, s.pos) > self.p.p_dash_r as f64 || !is_dash(step, prev, s.ms) {
                continue;
            }
            if s.gloom {
                sim.entity_remove_buff(s.id, &vx("g_mark"));
            } else {
                self.dashes += 1;
                if logged(self.dashes) {
                    wlog(format!("{} DASH #{}: #{} moved {step:.0} within {:.0} of her -> Gloom", head(sim, me),
                                 self.dashes, s.id, dist(pos, s.pos)));
                }
                sim.play_sfx(&vx("e_hit"), me, &InputTargetV1::target(s.id));
            }
            sim.add_buff(s.id, &BuffV1::timed(&vx("g_mark"), self.p.g_t));
        }
        self.last_pos = now;
    }

    /// 终焉的恐惧：Q / W 打中的背着她跑，E 打中的背着 E 的中心跑；时长按等级，减速按离她的远近。
    fn fears(&mut self, sim: &mut StableSim<'_>, me: usize, seen: &[Seen], pos: (u64, u64), level: usize) {
        let ticks = fear_ticks(&self.p, level);
        for s in seen.iter().filter(|s| s.f_q || s.f_e) {
            sim.entity_remove_buff(s.id, &vx(if s.f_e { "f_e" } else { "f_q" }));
            if !s.alive || s.immune {
                continue;
            }
            let from = match (&self.e, s.f_e) {
                (Some(c), true) => c.at,
                _ => pos,
            };
            let (dx, dy) = away(from, s.pos);
            let mut cc = CcV1::of_kind(CcKindV1::Fear, ticks as u64);
            cc.dx = dx;
            cc.dy = dy;
            sim.apply_cc(s.id, &cc);
            let d = dist(pos, s.pos);
            let slow = fear_slow(&self.p, d);
            let mut b = BuffV1::timed(&vx("f_slow"), ticks);
            b.move_speed_mult = -(slow as i32);
            sim.entity_remove_buff(s.id, &vx("f_slow"));
            sim.add_buff(s.id, &b);
            self.fears += 1;
            if logged(self.fears) {
                wlog(format!("{} FEAR #{}: #{} {} ticks at level {level}, away from {} ({dx},{dy}), {d:.0} off her -> slow {slow}%",
                             head(sim, me), self.fears, s.id, ticks, if s.f_e { "the E spot" } else { "her" }));
            }
        }
    }

    /// 溟濛渐染：出手时记下落点，落地后那一圈里死掉的缩短终焉。
    fn darkness(&mut self, sim: &mut StableSim<'_>, me: usize, seen: &[Seen], tick: usize) {
        if let Some(s) = seen.iter().find(|s| s.e_aim) {
            sim.entity_remove_buff(s.id, &vx("e_aim"));
            self.e = Some(ECast { at: s.pos, land: tick + self.p.e_fly, watch: Vec::new() });
        }
        let Some(c) = self.e.as_mut() else { return };
        let reach = self.p.e_r as f64 + 15_000.0;
        if tick + 2 == c.land {
            c.watch = seen.iter().filter(|s| s.alive && dist(s.pos, c.at) <= reach).map(|s| (s.id, s.champion)).collect();
        }
        if tick == c.land + 2 {
            let gone: Vec<(usize, bool)> = c.watch.iter().copied()
                .filter(|(id, _)| sim.get_entity(*id).map_or(true, |e| !e.is_alive()))
                .collect();
            c.watch.clear();
            for (id, champion) in gone {
                let cut = self.cut_doom(sim, me, if champion { self.p.e_cut_c } else { self.p.e_cut });
                self.e_kills += 1;
                if logged(self.e_kills) {
                    wlog(format!("{} EKILL #{}: #{id} ({}) died under Looming Darkness; Doom wait {cut:?}", head(sim, me),
                                 self.e_kills, if champion { "champion" } else { "unit" }));
                }
            }
        }
    }

    /// 愁煞：打中时看冲不冲上去；打中的英雄在 `r_reset` tick 内死了，`r_free` tick 后能再放。
    fn surge(&mut self, sim: &mut StableSim<'_>, me: usize, seen: &[Seen], pos: (u64, u64), ap: usize, tick: usize) {
        let mut now = Vec::new();
        for s in seen.iter().filter(|s| s.champion && s.r_mark) {
            now.push(s.id);
            if self.r_seen.contains(&s.id) {
                continue;
            }
            self.marked.retain(|m| m.0 != s.id);
            self.marked.push((s.id, tick + self.p.r_reset));
            if !s.alive {
                continue;
            }
            let w_ready = !has_buff(sim, me, &vx("w_cd"));
            let mut est = after_mr(self.p.r2_dmg + self.p.r2_ratio * ap / 100, s.mr);
            if w_ready {
                est += after_mr(self.p.w_dmg + self.p.w_ratio * ap / 100, s.mr);
            }
            let crowd = seen.iter().filter(|o| o.champion && o.alive && o.id != s.id && dist(o.pos, s.pos) <= CROWD_R).count();
            let into = kills(&self.p, s.hp, est) && crowd <= self.p.r_crowd;
            if into {
                sim.add_buff(me, &BuffV1::timed(&vx("r_in"), self.p.r_wait + 4));
            }
            self.surges += 1;
            if logged(self.surges) {
                wlog(format!("{} SURGE #{}: #{} hp {} vs ~{est} (W {}), {crowd} more near him, {:.0} off her -> {}",
                             head(sim, me), self.surges, s.id, s.hp, if w_ready { "ready" } else { "down" },
                             dist(pos, s.pos), if into { "onto him" } else { "stop outside" }));
            }
        }
        self.r_seen = now;
        let mut keep = Vec::new();
        for (id, until) in std::mem::take(&mut self.marked) {
            if tick > until {
                continue;
            }
            if sim.get_entity(id).map_or(false, |e| e.is_alive()) {
                keep.push((id, until));
                continue;
            }
            let cd = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Ult)).map_or(0, |c| c.remaining);
            if cd > self.p.r_free {
                sim.entity_reduce_cooldown(me, SkillSlotV1::Ult, (cd - self.p.r_free).min(RESET_TICKS));
            }
            self.resets += 1;
            if logged(self.resets) {
                wlog(format!("{} RESET #{}: #{id} died {} ticks before the mark ran out -> ult cooldown {cd} -> {}",
                             head(sim, me), self.resets, until - tick, cd.min(self.p.r_free)));
            }
        }
        self.marked = keep;
    }
}

impl StablePassive for Gloom {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        self.last_pos.clear();
        self.alive = true;
        wlog(format!("{} SPAWN: the add-on's Vex (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let ap = e.stat().magic_power;
        let pos = e.pos();
        let alive = e.is_alive();
        let level = e.level();
        let tick = sim.tick();
        let seen = scan(sim, team);
        // Gloom pops, fears and the reset go on after her death (her bolts still flying); only a living Vex marks a dash
        self.doom(sim, me, alive, level);
        self.detonate(sim, me, &seen, ap, level);
        self.dashes(sim, me, &seen, pos, alive);
        self.darkness(sim, me, &seen, tick);
        self.fears(sim, me, &seen, pos, level);
        self.surge(sim, me, &seen, pos, ap, tick);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: Gloom pops {}, dashes marked {}, Doom ready {}, fears {}, E kills {}, surges {}, \
                              ult resets {}", head(sim, me), self.pops, self.dashes, self.dooms, self.fears, self.e_kills,
                             self.surges, self.resets));
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
        "=== {ID} v{VERSION} (Vex as in League V26.13: Gloom on each enemy, Doom by level, the fears, Shadow Surge's \
         surge and reset) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:gloom"), Gloom::default());
    host.log(LogLevel::Info, "league_vex v2 loaded (Vex as in League V26.13).");
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
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"g_lo":50,"g_cut":30,"r_reset":300,"x":1}"#);
        assert_eq!((p.g_lo, p.g_cut, p.r_reset), (50, 30, 300));
        assert_eq!(p.g_ratio, Params::default().g_ratio);
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"g_cut":150}"#).g_cut, 100);
        assert_eq!(parse_params(r#"{"p_fs_d":0}"#).p_fs_d, 1);
    }

    #[test]
    fn doom_goes_by_level_as_in_league() {
        let p = Params::default();
        // 25 / 22 / 19 / 16 s from p_cd1 at level 1
        assert_eq!([1, 4, 5, 7, 8, 10, 11, 12].map(|l| doom_cd(&p, l)), [1030, 1030, 906, 906, 782, 782, 659, 659]);
        // 0.75 / 1 / 1.25 / 1.5 s
        assert_eq!([1, 5, 8, 11].map(|l| fear_ticks(&p, l)), [45, 60, 75, 90]);
    }

    #[test]
    fn the_fear_slows_more_the_farther_from_her() {
        let p = Params::default();
        assert_eq!(fear_slow(&p, 0.0), 60);
        assert_eq!(fear_slow(&p, 40_000.0), 80);
        assert_eq!(fear_slow(&p, 80_000.0), 99);
        assert_eq!(fear_slow(&p, 200_000.0), 99);
    }

    #[test]
    fn a_pop_goes_by_level_and_hits_units_for_less() {
        let p = Params::default();
        assert_eq!(gloom_damage(&p, 1, 100, true), 26 + 25);
        assert_eq!(gloom_damage(&p, 12, 100, true), 107 + 25);
        assert_eq!(gloom_damage(&p, 1, 100, false), 51 * 40 / 100);
        assert_eq!(gloom_damage(&p, 12, 100, false), 132 * 60 / 100);
        assert_eq!(doom_after_cut(800, 25), 600);
        assert_eq!(doom_after_cut(800, 10), 720);
        assert_eq!(doom_after_cut(0, 25), 0);
        assert_eq!(doom_after_cut(800, 100), 0);
    }

    #[test]
    fn a_dash_or_a_blink_counts_a_teleport_does_not() {
        // 走路（移速 1000）、加速走、引擎补的两步都不算
        assert!(!is_dash(1_000.0, 1_000.0, 1000));
        assert!(!is_dash(1_500.0, 1_500.0, 1500));
        assert!(!is_dash(2_705.0, 0.0, 1353));
        assert!(!is_dash(2_705.0, 1_353.0, 1353));
        // 冲刺 4500、从站着起冲、闪现 400 码
        assert!(is_dash(4_500.0, 1_000.0, 1000));
        assert!(is_dash(4_500.0, 0.0, 1000));
        assert!(is_dash(4_500.0, 4_500.0, 1353));
        assert!(is_dash(40_000.0, 0.0, 1000));
        // 回城、复活
        assert!(!is_dash(300_000.0, 0.0, 1000));
    }

    #[test]
    fn the_surge_goes_in_only_for_a_kill() {
        let p = Params::default();
        let est = after_mr(164 + 50 * 300 / 100, 40);
        assert_eq!(est, 314 * 100 / 140);
        assert!(kills(&p, est, est));
        assert!(!kills(&p, est + 1, est));
        assert!(kills(&Params { r_kill: 150, ..p.clone() }, est + 50, est));
        assert!(!kills(&Params { r_kill: 0, ..p }, 1, est));
    }

    #[test]
    fn fears_run_away_from_the_spot() {
        assert_eq!(away((100, 100), (130, 60)), (30, -40));
        assert_eq!(away((100, 100), (100, 100)), (1000, 0));
    }

    #[test]
    fn buff_names_fit() {
        for x in ["g_mark", "v_hit", "g_pop", "p_wait", "p_ready", "r_mark", "r_in", "e_hit", "e_aim", "f_q", "f_e", "f_slow",
                  "w_cd"] {
            assert!(vx(x).len() <= BUFF_NAME_CAP);
        }
    }
}
