//! 佐伊附加包：照英雄联盟的规则做主包数据做不到的几件事。
//!
//! 主包保持纯数据：飞星直着飞、按飞行时间分近 / 中 / 远三档伤害，窃法巧手只跟着大招射飞弹，昏睡是固定时长的眩晕（打不醒）。
//! `mod.override_info` 把主包的佐伊换成 `override/` 里的副本（`tools/kit/build_zoe.py --native`），被动 `league_zoe:sparkles`：
//!
//! - **催眠气泡**（0.6.0，用户 2026-11-05：「佐伊问题很大 好像不能催眠别人？」）：困倦结束时数据在被打中的单位身上落下
//!   `e_sleep_n` tick 的眩晕（英雄联盟 2.25 秒）。副本里气泡打中谁就另给谁挂 `league_zoe_e_mark`（困倦那 `e_drowsy` tick）；被动
//!   看见新的标记，眩晕落下时给他挂睡泡 `league_zoe_e_zz`；睡着时生命 + 护盾少了（**任何伤害**，谁打的都算）就**叫醒**：
//!   只解除这一份眩晕（[`kept_after_wake`]），那一下掉的血再来一遍真实伤害，最多 `e_cap` + `e_cap_ratio`% 法强（英雄联盟：
//!   打醒的第一下双倍，有封顶），放 `league_zoe_e_wake` 的画面和声音（[`watch`]）。0.4.0～0.5.2 用的是游戏的官方睡眠（催眠师
//!   E 的原生效果 `hypnotist_skill2`）：它按输入目标的**位置**放一个范围，被打中的英雄是单位、不是位置，范围落在佐伊自己
//!   脚下（游戏 0.7.1 的 0x19f8726），一个人也没睡着；给它位置也会被拉回到她 E 的施法距离以内，困倦结束时多数目标在那之外。
//!   0.8.0（用户 2026-11-20：「按照你的建议改吧」）：气泡照英雄联盟碰到第一个敌方单位就停（小兵、野怪也挡，主包和副本一样），
//!   所以睡的也可能是小兵、野怪：她踢出气泡（身上的 `league_zoe_e_go`）后 `E_WINDOW` tick 内所有敌方单位都看标记，其余时候只看
//!   英雄（落地的陷阱只抓英雄）。
//! - **飞星乱入！**（0.8.0，`star.rs`）：英雄联盟的 Q 扔出去还能再按一次改方向，所以玩家先往身后扔、再拐回来砸人。副本的 Q
//!   不再放数据里的直线飞星：出手时她身上有 `league_zoe_q_go`、目标身上有 `league_zoe_q_aim`，本包自己飞一颗：先往她身后
//!   （正后方被小兵挡着就往左边或右边）飞 `q_out`，再拐向目标这时站的地方，一路上碰到的第一个敌方单位挨打，伤害按两段一共
//!   飞了多远：`q_n0` 以内 100%，到 `q_n1d` 线性加到 `q_far`%（[`star_pct`]）。画面是每 tick 放一段 `q_star`（同飞弹的做法）。
//!   日志 `STAR`。
//! - **窃法巧手**：敌方英雄放大招（大招冷却从 0 跳起来）时原地掉下一块法术碎片（`league_zoe_w_shard`，`s_t` tick），她走到 `s_r`
//!   以内就捡起来：`w_n` 颗飞弹（每 `w_gap` tick 一颗，打 `w_r` 以内最近的敌方英雄，每颗 `w_dmg` + `w_ratio`% 法强魔法伤害）
//!   和 `w_ms`% 移速 `w_ms_t` tick（英雄联盟：捡起召唤师技能 / 主动装备的碎片；游戏里没有召唤师技能和主动装备，用大招代替）。
//!   0.8.0 起**只有捡碎片**才发动：英雄联盟的折返跃迁不触发窃法巧手（只有她自己放召唤师技能才触发），副本的大招不再挂
//!   `league_zoe_w_haste`、不再甩手射飞弹，门口那颗飞星接过飞弹的伤害（`build_zoe.py` 的 `r_dmg_n` / `r_ratio_n`；主包没有附加包、
//!   没有碎片，大招照旧带着飞弹和加速，那是它唯一的窃法巧手）。
//! - **窃法巧手的飞弹**（0.7.0，用户 2026-11-09：「佐伊的飞弹做的要像英雄联盟那样啊 从背后过来的 现在不太像」）：碎片的 3 颗由
//!   本包飞，捡起那一 tick 起每 `w_gap` tick 一颗：英雄联盟的飞弹（ZoeWPassiveMissile）先绕着她转（CircleMovement）再
//!   直线追（ZoeWPassiveMissileTwo）。每颗在她身后出现，从头顶划半个椭圆到身前（[`orbit_at`]，`ORBIT_T` tick），再以 `w_speed`
//!   追向目标的胸口（[`chase`]），追上了才结算伤害、放 `w_hit` 的画面和声音，目标死了就消失。游戏的投射物只有直线和追踪，
//!   弧线是每 tick 放一段 `w_missile` 的画面拼出来的（[`piece_spec`]，league_azir 沙线的做法）。日志 `MISSILE`。
//!
//! - **召唤师技能**（0.2.0，用户：「可以改成召唤师技能那种效果吗 随机的」「能做成智能释放吗」）：窃法巧手每次发动（捡起碎片时；
//!   0.8.0 以前大招也算）先放一个召唤师技能，再射飞弹：按局面挑（`summon.rs`：
//!   被控净化、残血被贴脸闪现、残血或队友快死治疗、敌人快死点燃、被贴脸虚弱、打架掉血屏障、附近没人幽灵疾步），都不是就在
//!   点燃 / 虚弱 / 屏障 / 幽灵疾步里随机（比赛的种子定，两份模拟一样）。数字在下面的 `S_*`。日志 `SUMMON`。
//!   画面（0.3.0，用户：「加啊」「地面上最好也要有图标显示」）：放的时候她脚下的地上亮起那个技能的图标
//!   （`league_zoe_sg_<技能>`）；闪现在起点和落点各炸开一团星芒（`s_flash`），中间一串金色拖影（`s_flash_trail`），落点也亮
//!   图标（0.5.0；她在大招里（身上有 `league_zoe_r_on`）不挑闪现，传送门马上就把她送回原地），净化一道光环从脚扫到头（`s_cleanse`），屏障一个金色
//!   气泡（`s_barrier`），治疗、点燃、虚弱、幽灵疾步是它们 buff 的画面；地上的碎片每次重画换一个图标（`ss_<技能>`，七个轮流），
//!   捡起来才按局面定是哪个。图在 `league_zoe_spells`（闪现，高清）、`league_zoe_spells_1x`（跟着人的那些，1 倍：0.6.0，
//!   用户 2026-11-05：「捡起来的召唤师技能的技能特效完全错位」）和 `league_zoe_spell_icons`（tools/art/draw_zoe_spells.py）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个佐伊自己的被动实例里，
//! 服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zoe.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, rift_ground, Map};
use mod_api_stable::*;

mod maps;
pub mod star;
pub mod summon;
pub mod wall;

const ID: &str = "league_zoe";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_zoe") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 闪现的起点和落点之间放几团金色拖影（`s_flash_trail`，等分）。
const FLASH_TRAIL: usize = 4;
/// 场上最多同时留几块碎片（多了丢最早的）。
const MAX_SHARDS: usize = 3;
/// 离她这么远以内放的大招才掉碎片（0.5.2，用户 2026-11-03：「还有这个召唤师技能为什么满屏幕有 佐伊的」）：以前地图上谁放
/// 大招都掉，她去不了的远处也躺着，满屏都是；英雄联盟的碎片也只在她附近才有意义。
pub const SHARD_NEAR: u64 = 150_000;
/// 碎片的画面多少 tick 重放一次（画面 4 帧 x 约 100 ms）。
const SHARD_VIEW: usize = 15;
/// 一颗飞星最多飞多少 tick（第一段 30000 / 2000 + 第二段离她 95000 / 4000，正常 50 tick 以内就飞完；防一直飞）。
const Q_TICKS: usize = 120;
/// 她踢出气泡后多少 tick 内看所有敌方单位身上的气泡标记（85000 / 3500 不到 25 tick 就飞完，多留一些）。
const E_WINDOW: usize = 45;
/// 大招冷却从 0 跳到多少以上算放了大招。
const ULT_JUMP: usize = 60;
/// 困倦结束后多少 tick 内看见眩晕才算这一泡的睡眠（数据里的眩晕在标记掉的那一 tick 前后落下）。
pub const SLEEP_LATE: usize = 4;

// 窃法巧手的飞弹（0.7.0，见开头）：绕着她胸口（脚下往上 CHEST）的半个椭圆，前后半径 ORBIT_RX、上下 ORBIT_RY（最高处刚过头顶：
// 她 1 倍 36 行），ORBIT_T tick 从身后到身前；后一颗小 ORBIT_SHRINK（三颗不叠在一起），头 ORBIT_GROW tick 从胸口长出来；
// 然后追目标脚下往上 AIM_LIFT 的地方。1000 = 1 像素。tools/art/review_zoe_missiles.py 画出来对照。
pub const ORBIT_T: usize = 12;
pub const ORBIT_RX: f64 = 15_000.0;
pub const ORBIT_RY: f64 = 20_000.0;
pub const ORBIT_SHRINK: f64 = 2_500.0;
pub const ORBIT_GROW: usize = 3;
pub const CHEST: f64 = 17_000.0;
pub const AIM_LIFT: f64 = 12_000.0;
/// 一段飞弹画面一步至少这么长（几乎没动的那一 tick 也画得出来）。
const PIECE_MIN: f64 = 300.0;

// 召唤师技能的数字（0.3.0 照创意工坊的 Summoner Spells 对齐，用户：「创意工坊里面有双召mod你直接参考」；它照英雄联盟）。
// 点燃：每 S_IGN_PER tick 一跳、共 S_IGN_N 跳真实伤害 S_IGN_DMG + S_IGN_AP% 法强，期间受治疗 -S_IGN_CUT%；虚弱：移速
// -S_EXH_SLOW%，攻击 / 法强（造成的伤害）-S_EXH_DMG%，S_EXH_T tick；治疗：S_HEAL + S_HEAL_AP% 法强（她和快死的队友），移速
// +S_HEAL_MS% S_HEAL_MS_T tick；屏障：护盾最大生命的 S_BAR_PCT%，S_BAR_T tick；幽灵疾步：移速 +S_GHOST% S_GHOST_T tick；
// 闪现：自己瞬移 summon::FLASH_D，背着贴脸的人（summon::flash_spot 挑不在墙里的落点）；净化：解除控制。
const S_IGN_N: usize = 5;
const S_IGN_PER: usize = 60;
const S_IGN_DMG: usize = 25;
const S_IGN_AP: usize = 8;
const S_IGN_CUT: usize = 40;
const S_EXH_SLOW: i32 = 45;
const S_EXH_DMG: i32 = 35;
const S_EXH_T: usize = 180;
const S_HEAL: usize = 90;
const S_HEAL_AP: usize = 30;
const S_HEAL_MS: i32 = 20;
const S_HEAL_MS_T: usize = 120;
const S_BAR_PCT: usize = 25;
const S_BAR_T: usize = 180;
const S_GHOST: i32 = 30;
const S_GHOST_T: usize = 360;
/// 被这些控住就净化（同 league_ult_press 的 NO_CAST）。
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::BlockSkill];

/// 主包佐伊的名字（buff、声音、画面都以它开头）。
fn zo(x: &str) -> String {
    format!("league_zoe_{x}")
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZOE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_zoe.log");
        }
    }
    PathBuf::from("league_zoe.log")
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
    /// 飞星：近的一档的伤害（固定值、法强 %），最远的倍数 %，从 `q_n0` 到 `q_n1d` 距离线性加上去。
    pub q_dmg: usize,
    pub q_ratio: usize,
    pub q_far: usize,
    pub q_n0: usize,
    pub q_n1d: usize,
    /// 飞星怎么飞（0.8.0）：第一段长 `q_out`、每 tick `q_out_v`，拐弯后每 tick `q_speed`，飞到离她 `q_len` 远就没了，星的半径
    /// `q_w`。`star` = 副本带着 `q_out`（0.8.0 以后的副本）：旧存档里的旧副本自己放数据的飞星，这里就不再扔一颗。
    pub q_out: usize,
    pub q_out_v: usize,
    pub q_speed: usize,
    pub q_len: usize,
    pub q_w: usize,
    pub star: bool,
    /// 催眠气泡：困倦的 tick，睡眠的 tick（数据里眩晕的时长），打醒那一下补的真实伤害的封顶（固定值、法强 %）。
    pub e_drowsy: usize,
    pub e_sleep_n: usize,
    pub e_cap: usize,
    pub e_cap_ratio: usize,
    /// 气泡飞过墙（0.8.0，wall.rs）：平常飞 `e_len`，线上有墙时数据踢长 `e_wall` 的那颗；`e_rel` 是开始踢到出手的 tick。
    pub e_len: usize,
    pub e_wall: usize,
    pub e_rel: usize,
    /// 碎片的飞弹：每颗伤害（固定值、法强 %）、颗数、间隔 tick、找目标的距离；移速 % 和 tick。
    pub w_dmg: usize,
    pub w_ratio: usize,
    pub w_n: usize,
    pub w_gap: usize,
    pub w_r: usize,
    pub w_ms: usize,
    pub w_ms_t: usize,
    /// 大招的飞弹从窃法巧手动起来（`w_haste` 挂上）后第几 tick 起射（数据的 `w_rel`），飞弹每 tick 追多远（`w_speed`）。
    pub w_rel: usize,
    pub w_speed: usize,
    /// 碎片：留在地上多少 tick，捡起的距离。
    pub s_t: usize,
    pub s_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            q_dmg: 105,
            q_ratio: 60,
            q_far: 250,
            q_n0: 20000,
            q_n1d: 85000,
            q_out: 30000,
            q_out_v: 2000,
            q_speed: 4000,
            q_len: 95000,
            q_w: 6000,
            star: true,
            e_drowsy: 84,
            e_len: 85000,
            e_wall: 35000,
            e_rel: 13,
            e_sleep_n: 135,
            e_cap: 100,
            e_cap_ratio: 60,
            w_dmg: 45,
            w_ratio: 15,
            w_n: 3,
            w_gap: 5,
            w_r: 70000,
            w_ms: 40,
            w_ms_t: 150,
            w_rel: 4,
            w_speed: 4000,
            s_t: 1200,
            s_r: 18000,
        }
    }
}

/// `{"q_dmg":105,...}` -> 参数；缺的键用默认值，认不得的键忽略。没有 `q_out` 的是 0.8.0 以前的副本（`star` = false）。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    p.star = false;
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        if k == "q_out" {
            p.star = true;
        }
        let slot = match k {
            "q_dmg" => &mut p.q_dmg,
            "q_ratio" => &mut p.q_ratio,
            "q_far" => &mut p.q_far,
            "q_n0" => &mut p.q_n0,
            "q_n1d" => &mut p.q_n1d,
            "q_out" => &mut p.q_out,
            "q_out_v" => &mut p.q_out_v,
            "q_speed" => &mut p.q_speed,
            "q_len" => &mut p.q_len,
            "q_w" => &mut p.q_w,
            "e_drowsy" => &mut p.e_drowsy,
            "e_len" => &mut p.e_len,
            "e_wall" => &mut p.e_wall,
            "e_rel" => &mut p.e_rel,
            "e_sleep_n" => &mut p.e_sleep_n,
            "e_cap" => &mut p.e_cap,
            "e_cap_ratio" => &mut p.e_cap_ratio,
            "w_dmg" => &mut p.w_dmg,
            "w_ratio" => &mut p.w_ratio,
            "w_n" => &mut p.w_n,
            "w_gap" => &mut p.w_gap,
            "w_r" => &mut p.w_r,
            "w_ms" => &mut p.w_ms,
            "w_ms_t" => &mut p.w_ms_t,
            "w_rel" => &mut p.w_rel,
            "w_speed" => &mut p.w_speed,
            "s_t" => &mut p.s_t,
            "s_r" => &mut p.s_r,
            _ => continue,
        };
        *slot = v;
    }
    p.q_n1d = p.q_n1d.max(p.q_n0 + 1);
    p.q_far = p.q_far.max(100);
    p.q_out_v = p.q_out_v.max(1);
    p.q_speed = p.q_speed.max(1);
    p.w_gap = p.w_gap.max(1);
    p.w_speed = p.w_speed.max(1);
    p
}

// ===================== 计算 =====================

/// 飞星飞了 `dist` 时总伤害的倍数（%）：`q_n0` 以内 100，到 `q_n1d` 加到 `q_far`。
pub fn star_pct(p: &Params, dist: u64) -> usize {
    let (lo, hi) = (p.q_n0 as u64, p.q_n1d as u64);
    let d = dist.clamp(lo, hi);
    100 + ((p.q_far - 100) as u64 * (d - lo) / (hi - lo)) as usize
}

/// 飞星飞了 `dist` 打中时的魔法伤害（减免前）：`q_dmg` + `q_ratio`% 法强，乘上 [`star_pct`]。
pub fn star_damage(p: &Params, dist: u64, ap: usize) -> usize {
    let base = p.q_dmg + p.q_ratio * ap / 100;
    base * star_pct(p, dist) / 100
}

/// 打醒那一下补的真实伤害：那一下掉的生命 + 护盾，最多封顶。
pub fn wake_bonus(p: &Params, drop: usize, ap: usize) -> usize {
    drop.min(p.e_cap + p.e_cap_ratio * ap / 100)
}

/// 一颗碎片飞弹的魔法伤害（减免前）。
pub fn shard_damage(p: &Params, ap: usize) -> usize {
    p.w_dmg + p.w_ratio * ap / 100
}

/// 大招冷却从 `was` 变成 `now`：放了大招（从好着跳到 ULT_JUMP 以上）。
pub fn ult_cast(was: usize, now: usize) -> bool {
    was == 0 && now > ULT_JUMP
}

/// 地图上的一个点（游戏单位，1000 = 1 像素；y 往下）。
pub type Pt = (f64, f64);

/// 单位向量；两点重合时 None。
pub fn unit(v: Pt) -> Option<Pt> {
    let d = (v.0 * v.0 + v.1 * v.1).sqrt();
    (d > 1e-9).then(|| (v.0 / d, v.1 / d))
}

/// 朝目标的方向 `f` 的两条垂线里屏幕上朝上（y 小）的那条：飞弹从她身后经头顶到身前。
pub fn up_of(f: Pt) -> Pt {
    let (a, b) = ((f.1, -f.0), (-f.1, f.0));
    if a.1 <= b.1 {
        a
    } else {
        b
    }
}

/// 第 `k` 颗飞弹出手后第 `age` tick 绕到哪：圆心是她的胸口 `c`，从身后（-`f`）经头顶（`p`）到身前（`f`）的半个椭圆
/// （前后 ORBIT_RX、上下 ORBIT_RY，每颗小 ORBIT_SHRINK，头 ORBIT_GROW tick 从胸口长出来）；第 ORBIT_T - 1 tick 到身前。
pub fn orbit_at(c: Pt, f: Pt, p: Pt, age: usize, k: usize) -> Pt {
    let phi = std::f64::consts::PI * ((age + 1) as f64 / ORBIT_T as f64).min(1.0);
    let grow = ((age + 1) as f64 / ORBIT_GROW as f64).min(1.0);
    let shrink = ORBIT_SHRINK * k as f64;
    let rx = (ORBIT_RX - shrink).max(4_000.0) * grow;
    let ry = (ORBIT_RY - shrink).max(4_000.0) * grow;
    (c.0 - rx * f.0 * phi.cos() + ry * p.0 * phi.sin(), c.1 - rx * f.1 * phi.cos() + ry * p.1 * phi.sin())
}

/// 追的一步：从 `at` 朝 `aim` 走 `speed`；这一步够得着就是打中（None）。
pub fn chase(at: Pt, aim: Pt, speed: f64) -> Option<Pt> {
    let (dx, dy) = (aim.0 - at.0, aim.1 - at.1);
    let d = (dx * dx + dy * dy).sqrt();
    if d <= speed {
        return None;
    }
    Some((at.0 + dx / d * speed, at.1 + dy / d * speed))
}

fn ux(v: f64) -> u64 {
    v.max(0.0).round() as u64
}

/// 这一 tick 的一段飞弹画面（`w_missile`；游戏把投射物的图转向它飞的方向）：画在 `at`、朝 `dir`、一步 `step`（至少
/// PIECE_MIN）。从画的地方往回一步出发，第一步落到画的地方，这一 tick 结束时还在飞，下一 tick 才到头、那时下一段已经接上
/// （league_azir 的 tether_flight：一 tick 内生成、移动、消失的投射物，画面一帧也画不出来）。
pub fn piece_spec(me: usize, team: usize, at: Pt, dir: Pt, step: f64) -> ProjectileSpawnV1 {
    let step = step.max(PIECE_MIN);
    ProjectileSpawnV1 {
        caster_id: me,
        team,
        x: ux(at.0 - dir.0 * step),
        y: ux(at.1 - dir.1 * step),
        radius: 1_000,
        speed: step.round() as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: ux(at.0 + dir.0 * step),
        target_y: ux(at.1 + dir.1 * step),
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    }
}

fn dist(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0 as f64 - b.0 as f64;
    let dy = a.1 as f64 - b.1 as f64;
    (dx * dx + dy * dy).sqrt() as u64
}

// ===================== 被动 =====================

#[derive(Clone, Debug)]
struct Sleeper {
    target: usize,
    /// 困倦结束、数据的眩晕落下的 tick。
    sleep_at: usize,
    /// 睡着后到这一 tick 自己醒；0 = 还没睡着。
    until: usize,
    /// 上一 tick 的生命 + 护盾（睡着以后）。
    guard: usize,
}

/// 这一 tick 对一个中了气泡的人做什么（[`watch`]）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Watch {
    /// 还困着，或眩晕还没落下。
    Wait,
    /// 睡着了：挂上睡泡，记下生命 + 护盾。
    Fell,
    /// 没睡着（困倦时被净化、免疫控制）：不管了。
    Missed,
    /// 还睡着。
    Asleep,
    /// 睡着时挨了打：叫醒他（只解除这份眩晕），那一下再来一遍真实伤害，摘掉睡泡，放醒来的画面。
    Hit,
    /// 眩晕提前没了（净化）：摘掉睡泡，放醒来的画面。
    Woke,
    /// 到时间自己醒了：摘掉睡泡。
    Ended,
}

/// 中了气泡的人这一 tick 的样子：`sleep_at` 困倦结束的 tick，`until` 睡着后自己醒的 tick（还没睡着是 0），`held` 他身上有
/// 眩晕，`hurt` 睡着以后生命 + 护盾比上一 tick 少了。困倦时别人的眩晕不算睡着。
pub fn watch(tick: usize, sleep_at: usize, until: usize, held: bool, hurt: bool) -> Watch {
    if until == 0 {
        if held && tick >= sleep_at {
            Watch::Fell
        } else if tick > sleep_at + SLEEP_LATE {
            Watch::Missed
        } else {
            Watch::Wait
        }
    } else if !held {
        if tick + 2 < until {
            Watch::Woke
        } else {
            Watch::Ended
        }
    } else if hurt {
        Watch::Hit
    } else {
        Watch::Asleep
    }
}

#[derive(Clone, Debug)]
struct Shard {
    at: (u64, u64),
    until: usize,
    next_view: usize,
}

/// 一颗飞着的窃法巧手飞弹（0.7.0）：目标、伤害（出手时按她的法强算好）、出手的 tick、第几颗（绕圈的大小）、现在和上一 tick
/// 的位置、出手时朝目标的方向和它朝上的垂线、哪来的（大招 / 碎片，日志用）。
#[derive(Clone, Debug)]
struct Missile {
    target: usize,
    dmg: usize,
    born: usize,
    k: usize,
    at: Pt,
    last: Pt,
    f: Pt,
    p: Pt,
    from: &'static str,
}

/// 一颗飞着的飞星（0.8.0，`star.rs`）：第几颗、目标、飞向哪（拐弯前是出手时目标站的地方，拐弯时换成他那时站的地方）、
/// 现在在哪、拐弯的地方、拐了没有、拐弯后的方向、两段一共飞了多远、出手的 tick、第一段往哪扔。
#[derive(Clone, Debug)]
struct Flying {
    no: usize,
    target: usize,
    aim: Pt,
    at: Pt,
    out: Pt,
    turned: bool,
    dir: Pt,
    flown: f64,
    born: usize,
    how: star::Out,
}

/// 每个佐伊一份。
#[derive(Clone, Default)]
struct Sparkles {
    p: Params,
    sleepers: Vec<Sleeper>,
    /// 上一 tick 身上有气泡标记的敌方单位。
    marked: Vec<usize>,
    /// 上一 tick 她身上有没有 e_go（刚踢出气泡）；到这一 tick 为止所有敌方单位都看气泡标记（不只是英雄）。
    e_go_was: bool,
    e_scan_until: usize,
    /// 上一 tick 身上有 e_aim（她正对着他踢气泡）的敌方英雄；线上有墙、气泡踢长的那颗的次数。
    e_aimed: Vec<usize>,
    walls: usize,
    /// 飞着的飞星，上一 tick 她身上有没有 q_go；扔出、打中英雄、打中别的单位、没打中、往旁边扔（正后方被挡着）的颗数。
    stars: Vec<Flying>,
    q_go_was: bool,
    thrown: usize,
    star_champs: usize,
    star_units: usize,
    star_misses: usize,
    sideways: usize,
    /// 旧副本（没有 q_out）的那一行日志写过了。
    old_copy: bool,
    /// 每个敌方英雄上一 tick 的大招冷却。
    ult_cd: Vec<(usize, usize)>,
    shards: Vec<Shard>,
    /// 还要射的飞弹：(射下一颗的 tick, 剩几颗, 哪来的)。大招的和碎片的都在这里（0.7.0）。
    volleys: Vec<(usize, usize, &'static str)>,
    /// 飞着的飞弹；射出、打中、目标没了消失、画面没放出来的颗数。
    missiles: Vec<Missile>,
    launched: usize,
    hits: usize,
    fizzled: usize,
    refused: usize,
    /// 睡着的（其中不是英雄的）。
    sleeps: usize,
    unit_sleeps: usize,
    /// 挨打叫醒的、睡眠被净化掉的。
    wakes: usize,
    freed: usize,
    /// 困倦结束后没看见睡着的（日志里写下他当时身上的控制）。
    misses: usize,
    picked: usize,
    dropped: usize,
    next_report: usize,
    /// 点燃：(目标, 下一跳的 tick, 还剩几跳)、放过几次召唤师技能。
    burns: Vec<(usize, usize, usize)>,
    summons: usize,
    /// 屏障放出的 tick（护盾归零后摘掉气泡，放出那一 tick 不算）。
    barrier_at: usize,
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id)
        .map_or(false, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 他身上的控制：`种类代码:剩余 tick`（日志用）。
fn cc_list(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).map_or_else(String::new, |e| {
        (0..e.cc_count()).filter_map(|i| e.cc_at(i)).map(|c| format!("{}:{}", c.kind, c.tick)).collect::<Vec<_>>().join(" ")
    })
}

/// 身上有眩晕（气泡的睡眠是数据的眩晕；敌方催眠师的官方睡眠在稳定接口里也报成眩晕）。
fn held(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id)
        .map_or(false, |e| (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| c.kind == CcKindV1::Stun.code()))
}

/// 生命 + 护盾（少了 = 挨了打）。
fn guard_of(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| e.hp().0 + e.shield())
}

/// The crowd control to put back after waking `target` from this bubble's sleep: every entry but the one Stun whose ticks
/// left are nearest the sleep's own `left` (ours). The stable API can only clear every control at once
/// (`entity_clear_cc`), so waking would wipe an ally's stun or knock-up landing with the waking hit as well (0.3.1, the
/// game 0.7.0 audit).
pub fn kept_after_wake(ccs: &[CcV1], left: u64) -> Vec<CcV1> {
    let ours = ccs
        .iter()
        .enumerate()
        .filter(|(_, c)| c.kind == CcKindV1::Stun.code())
        .min_by_key(|(_, c)| c.tick.abs_diff(left))
        .map(|(i, _)| i);
    ccs.iter().enumerate().filter(|(i, _)| Some(*i) != ours).map(|(_, c)| *c).collect()
}

/// Wakes `target`: clears its crowd control and puts back everything but this bubble's sleep ([`kept_after_wake`]).
fn wake_from_sleep(sim: &mut StableSim<'_>, target: usize, left: u64) {
    let ccs: Vec<CcV1> = sim
        .get_entity(target)
        .map(|e| (0..e.cc_count()).filter_map(|i| e.cc_at(i)).collect())
        .unwrap_or_default();
    sim.entity_clear_cc(target);
    for c in kept_after_wake(&ccs, left) {
        sim.apply_cc(target, &c);
    }
}

/// 这次启动已经在日志里说过峡谷了。
static RIFT_SEEN: AtomicBool = AtomicBool::new(false);
/// 这次启动已经在日志里说过峡谷上气泡不过墙了。
static RIFT_BUBBLE_SEEN: AtomicBool = AtomicBool::new(false);

/// 闪现落在哪张图上：塔站在 1000000 以外就是召唤师峡谷（它的墙：作者的墙体坐标.json，没有时只有地图外），否则游戏自己的图。
fn ground(sim: &StableSim<'_>) -> summon::Ground<'static> {
    if map_of_sim(sim) == Map::Native {
        return summon::Ground::Native;
    }
    if !RIFT_SEEN.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: Zoe's Flash lands on the Rift's 1614545 square clear of its walls (none known without the walls \
                      file: only its edge); {} ==", rift_status()));
    }
    summon::Ground::Rift(rift_ground())
}

/// Living enemy champions of `team`: (id, position).
fn enemies(sim: &StableSim<'_>, team: usize) -> Vec<(usize, (u64, u64))> {
    let mut out = Vec::new();
    for i in 0..sim.champion_count() {
        let id = sim.champion_id_at(i);
        let Some(e) = sim.get_entity(id) else { continue };
        if e.team() != team && e.is_alive() {
            out.push((id, e.pos()));
        }
    }
    out
}

/// 飞星碰得到的敌方单位：活着、能被选中、不是塔和水晶（同主包飞星的 `EnemyWithoutTower`）：(编号, 位置, 身体半径)。
fn bodies(sim: &StableSim<'_>, team: usize) -> Vec<star::Body> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.team() != team && e.is_alive() && e.is_targetable() && !e.is_tower())
        .filter(|e| e.kind() != Some(EntityKindV1::Nexus))
        .map(|e| {
            let p = e.pos();
            (e.id(), (p.0 as f64, p.1 as f64), e.radius() as f64)
        })
        .collect()
}

/// 身上挂着 `name` 的第一个敌方单位（不只是英雄）。
fn marked_unit(sim: &StableSim<'_>, team: usize, name: &str) -> Option<(usize, (u64, u64))> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .find(|e| e.team() != team && e.is_alive() && (0..e.buff_count()).filter_map(|k| e.buff_at(k)).any(|b| b.name() == name))
        .map(|e| (e.id(), e.pos()))
}

/// 日志里写的单位种类。
fn what(sim: &StableSim<'_>, id: usize) -> &'static str {
    match sim.get_entity(id).and_then(|e| e.kind()) {
        Some(EntityKindV1::Champion) => "champion",
        Some(EntityKindV1::Minion) => "minion",
        Some(EntityKindV1::Jungle) => "monster",
        Some(EntityKindV1::Epic) => "epic monster",
        Some(EntityKindV1::Summon) => "summon",
        _ => "unit",
    }
}

fn fpos(p: (u64, u64)) -> Pt {
    (p.0 as f64, p.1 as f64)
}

fn fdist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

impl Sparkles {
    /// 窃法巧手发动：按局面挑一个召唤师技能放（summon.rs），`why` 是谁触发的（0.8.0 起只有捡碎片）。
    fn summon(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        // 在大招里（传送门马上把她拉回原地）不挑闪现，闪出去也白闪
        let in_ult = has_buff(sim, me, &zo("r_on"));
        let Some(e) = sim.get_entity(me) else { return };
        let (team, pos, ap) = (e.team(), e.pos(), e.stat().magic_power);
        let share = |e: &StableEntity<'_, '_>| {
            let (hp, max) = e.hp();
            if max == 0 { 0.0 } else { hp as f64 / max as f64 }
        };
        let me_hp = share(&e);
        let controlled = (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)));
        let mut foes = Vec::new();
        let mut allies = Vec::new();
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(c) = sim.get_entity(id) else { continue };
            if id == me || !c.is_alive() {
                continue;
            }
            let u = (id, dist(pos, c.pos()), share(&c));
            if c.team() == team {
                allies.push(u);
            } else if c.is_targetable() && sim.is_visible(team, id) {
                foes.push(u);
            }
        }
        let tick = sim.tick();
        let (spell, target, reason) =
            summon::pick(me_hp, controlled, in_ult, &foes, &allies, summon::roll(sim.seed(), tick, me));
        let on_me = InputTargetV1::target(me);
        sim.play_view_effect(&zo(&format!("sg_{}", spell.key())), me, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
        match spell {
            summon::Spell::Cleanse => {
                sim.entity_clear_cc(me);
                sim.play_view_effect(&zo("s_cleanse"), me, &on_me, 0, 0, 0);
            }
            summon::Spell::Flash => {
                // a starburst where she was and where she lands (s_flash stays where it is played), a golden streak of
                // FLASH_TRAIL puffs between them and the icon lighting up where she lands too (0.5.0, the user: 「闪现现在
                // 怎么看不出效果？」 - one small 0.2 s burst at each end, a body apart, read as nothing)
                sim.play_view_effect(&zo("s_flash"), me, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
                let from = target.and_then(|t| sim.get_entity(t)).map(|t| t.pos());
                let on = ground(sim);
                if let Some(to) = from.and_then(|f| summon::flash_spot_on(on, pos, f)) {
                    sim.entity_set_pos(me, to.0, to.1);
                    for k in 1..=FLASH_TRAIL {
                        let f = k as f64 / (FLASH_TRAIL + 1) as f64;
                        let at = |a: u64, b: u64| (a as f64 + (b as f64 - a as f64) * f).round() as u64;
                        let p = InputTargetV1::pos(at(pos.0, to.0), at(pos.1, to.1));
                        sim.play_view_effect(&zo("s_flash_trail"), me, &p, 0, 0, 0);
                    }
                    let land = InputTargetV1::pos(to.0, to.1);
                    sim.play_view_effect(&zo("s_flash"), me, &land, 0, 0, 0);
                    sim.play_view_effect(&zo("sg_flash"), me, &land, 0, 0, 0);
                }
            }
            summon::Spell::Heal => {
                for id in std::iter::once(me).chain(target) {
                    sim.heal(me, id, S_HEAL + ap * S_HEAL_AP / 100);
                    let mut b = BuffV1::timed(&zo("s_heal"), S_HEAL_MS_T);
                    b.move_speed_mult = S_HEAL_MS;
                    sim.entity_remove_buff(id, &zo("s_heal"));
                    sim.add_buff(id, &b);
                }
            }
            summon::Spell::Ignite => {
                if let Some(t) = target {
                    self.burns.retain(|b| b.0 != t);
                    self.burns.push((t, tick, S_IGN_N));
                    let mut b = BuffV1::timed(&zo("s_ignite"), S_IGN_N * S_IGN_PER);
                    b.heal_reduce = S_IGN_CUT;
                    sim.entity_remove_buff(t, &zo("s_ignite"));
                    sim.add_buff(t, &b);
                }
            }
            summon::Spell::Exhaust => {
                if let Some(t) = target {
                    let mut b = BuffV1::timed(&zo("s_exhaust"), S_EXH_T);
                    b.move_speed_mult = -S_EXH_SLOW;
                    b.attack_mult = -S_EXH_DMG;
                    b.magic_power_mult = -S_EXH_DMG;
                    sim.entity_remove_buff(t, &zo("s_exhaust"));
                    sim.add_buff(t, &b);
                }
            }
            summon::Spell::Barrier => {
                let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
                sim.entity_add_shield(me, max * S_BAR_PCT / 100, S_BAR_T);
                // the bubble: a buff's view, taken off when the shield is gone (on_update)
                sim.entity_remove_buff(me, &zo("s_barrier"));
                sim.add_buff(me, &BuffV1::timed(&zo("s_barrier"), S_BAR_T));
                self.barrier_at = tick;
            }
            summon::Spell::Ghost => {
                let mut b = BuffV1::timed(&zo("s_ghost"), S_GHOST_T);
                b.move_speed_mult = S_GHOST;
                sim.entity_remove_buff(me, &zo("s_ghost"));
                sim.add_buff(me, &b);
            }
        }
        sim.play_sfx(&zo("w_shot"), me, &on_me);
        self.summons += 1;
        if self.summons <= 60 || self.summons % 25 == 0 {
            wlog(format!("{} SUMMON #{}: {} ({reason}; from {why}; {:.0}% hp, target {})", head(sim, me), self.summons,
                         spell.name(), me_hp * 100.0, target.map_or("-".into(), |t| format!("#{t}"))));
        }
    }

    /// 点燃的每一跳（真实伤害）。
    fn burn(&mut self, sim: &mut StableSim<'_>, me: usize, ap: usize, tick: usize) {
        let mut left = Vec::new();
        for (t, next, n) in std::mem::take(&mut self.burns) {
            if tick < next {
                left.push((t, next, n));
                continue;
            }
            if !sim.get_entity(t).is_some_and(|e| e.is_alive()) {
                continue;
            }
            sim.deal_damage_typed(me, t, S_IGN_DMG + ap * S_IGN_AP / 100, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            if n > 1 {
                left.push((t, tick + S_IGN_PER, n - 1));
            }
        }
        self.burns = left;
    }

    /// 飞星出手（0.8.0）：她身上的 q_go 刚挂上就扔一颗（star.rs 挑第一段往哪扔）。目标是身上有 q_aim 的敌方单位（Q 出手前
    /// 数据挂上的），没找到（他出手前死了，补刀时常有）就是离她最近的敌方单位（英雄、小兵都算，同数据的飞星飞向他倒下的地方）。
    fn throw_star(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), tick: usize) {
        let go = has_buff(sim, me, &zo("q_go"));
        let rising = go && !self.q_go_was;
        self.q_go_was = go;
        if !rising {
            return;
        }
        if !self.p.star {
            // 0.8.0 以前的副本（存档里没刷新的英雄数据）自己放数据里的飞星，这里再扔一颗就是两颗
            if !self.old_copy {
                self.old_copy = true;
                wlog(format!("{} OLD COPY: this Zoe's hero data is older than league_zoe 0.8.0 (no q_out in its params) - \
                              its own data star flies and the add-on throws none; refresh the save's hero copies", head(sim, me)));
            }
            return;
        }
        let her = (pos.0 as f64, pos.1 as f64);
        let all = bodies(sim, team);
        let reach = self.p.q_len as f64;
        let target = marked_unit(sim, team, &zo("q_aim")).map(|(id, p)| (id, fpos(p))).or_else(|| {
            all.iter().filter(|u| fdist(her, u.1) <= reach).min_by(|a, b| fdist(her, a.1).total_cmp(&fdist(her, b.1)))
                .map(|u| (u.0, u.1))
        });
        let Some((target, aim)) = target else {
            wlog(format!("{} STAR not thrown: no target (no q_aim mark, no enemy unit within {reach:.0})", head(sim, me)));
            return;
        };
        // 第一段别扔出地图：峡谷比游戏自己的图大（1614545 见方）
        let side = map_of_sim(sim).extent();
        let (how, out) = star::pick_out(her, aim, self.p.q_out as f64, self.p.q_w as f64, &all, target, side);
        self.thrown += 1;
        if how != star::Out::Back {
            self.sideways += 1;
        }
        let dir = unit((out.0 - her.0, out.1 - her.1)).unwrap_or((1.0, 0.0));
        self.stars.push(Flying { no: self.thrown, target, aim, at: her, out, turned: false, dir, flown: 0.0, born: tick, how });
        if self.thrown <= 12 || self.thrown % 25 == 0 {
            wlog(format!("{} STAR #{} thrown at #{target} ({}) {:.0} away: out {} {}{}", head(sim, me), self.thrown,
                         what(sim, target), fdist(her, aim), how.name(), self.p.q_out,
                         if how == star::Out::Back { "" } else { " (the way behind her was blocked or off the map)" }));
        }
    }

    /// 飞着的飞星（0.8.0）：第一段飞到拐弯的地方，朝目标这时站的地方拐过去，一路上碰到的第一个敌方单位挨打，伤害按两段一共
    /// 飞了多远（[`star_damage`]），放 `q_hit` 的画面和声音；飞到离她 `q_len` 远没打中就没了。她死了也飞完。每 tick 放一段
    /// `q_star` 的画面（[`piece_spec`]）。
    fn fly_stars(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), ap: usize, tick: usize) {
        if self.stars.is_empty() {
            return;
        }
        let all = bodies(sim, team);
        let her = (pos.0 as f64, pos.1 as f64);
        let w = self.p.q_w as f64;
        let mut keep = Vec::new();
        for mut s in std::mem::take(&mut self.stars) {
            let from = s.at;
            let (next, reached) = if s.turned {
                let v = self.p.q_speed as f64;
                ((from.0 + s.dir.0 * v, from.1 + s.dir.1 * v), false)
            } else {
                star::advance(from, s.out, self.p.q_out_v as f64)
            };
            let step = fdist(from, next);
            if let Some((id, t)) = star::first_on(from, next, w, &all, None) {
                let d = s.flown + step * t;
                let dmg = star_damage(&self.p, d as u64, ap);
                let on = InputTargetV1::target(id);
                sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                sim.play_view_effect(&zo("q_hit"), me, &on, 0, 0, 0);
                sim.play_sfx(&zo("q_hit"), me, &on);
                let kind = what(sim, id);
                if kind == "champion" {
                    self.star_champs += 1;
                } else {
                    self.star_units += 1;
                }
                if s.no <= 12 || s.no % 25 == 0 {
                    wlog(format!("{} STAR #{} hit #{id} ({kind}{}) {} (thrown out {}) after {d:.0} flown -> x{}% = {dmg} magic",
                                 head(sim, me), s.no, if id == s.target { ", the target" } else { ", in the way" },
                                 if s.turned { "on the way in" } else { "on the way out" }, s.how.name(),
                                 star_pct(&self.p, d as u64)));
                }
                continue;
            }
            s.flown += step;
            s.at = next;
            if reached {
                // 拐弯：朝他这时站的地方（他死了、不能选中了就朝最后看见他的地方）
                if let Some(p) = sim.get_entity(s.target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.pos()) {
                    s.aim = (p.0 as f64, p.1 as f64);
                }
                s.dir = unit((s.aim.0 - s.at.0, s.aim.1 - s.at.1)).unwrap_or((-s.dir.0, -s.dir.1));
                s.turned = true;
            }
            if (s.turned && fdist(s.at, her) > self.p.q_len as f64) || tick >= s.born + Q_TICKS {
                self.star_misses += 1;
                if s.no <= 12 || s.no % 25 == 0 {
                    wlog(format!("{} STAR #{} gone after {:.0} flown ({} ticks), nobody hit", head(sim, me), s.no, s.flown,
                                 tick - s.born));
                }
                continue;
            }
            let mv = unit((next.0 - from.0, next.1 - from.1)).unwrap_or(s.dir);
            if !sim.spawn_projectile(&zo("q_star"), &format!("{ID}:noop"), &piece_spec(me, team, next, mv, step)) {
                self.refused += 1;
                if self.refused <= 4 || self.refused % 100 == 0 {
                    wlog(format!("{} STAR picture refused #{}: spawn_projectile {}", head(sim, me), self.refused, zo("q_star")));
                }
            }
            keep.push(s);
        }
        self.stars = keep;
    }

    /// 催眠气泡飞过墙（0.8.0，wall.rs）：她开始踢（目标身上刚挂上 e_aim）时看她到目标这条线，前 e_len 的空地以内有一段墙、
    /// 穿得出去，就给她挂 e_far，出手时数据踢长 e_wall 的那颗（英雄联盟：穿墙那段不算射程）。
    fn aim_bubble(&mut self, sim: &mut StableSim<'_>, me: usize, foes: &[(usize, (u64, u64))], pos: (u64, u64)) {
        // 墙格是游戏自己那几张图的，峡谷上用它会看见峡谷没有的墙：峡谷上不踢长的那颗
        if map_of_sim(sim) != Map::Native {
            if !RIFT_BUBBLE_SEEN.swap(true, Ordering::Relaxed) {
                wlog("== Rift: the bubble never takes the long kick over a wall here (the wall grid is the game's own maps') ==");
            }
            return;
        }
        let mark = zo("e_aim");
        let now: Vec<usize> = foes.iter().map(|f| f.0).filter(|&id| has_buff(sim, id, &mark)).collect();
        let new: Vec<(usize, (u64, u64))> =
            foes.iter().filter(|f| now.contains(&f.0) && !self.e_aimed.contains(&f.0)).copied().collect();
        self.e_aimed = now;
        for (id, tp) in new {
            let champs: Vec<Pt> =
                (0..sim.champion_count()).filter_map(|i| sim.get_entity(sim.champion_id_at(i))).map(|e| fpos(e.pos())).collect();
            let rows = wall::grid_of(&champs);
            let Some(run) = wall::crossing(rows, fpos(pos), fpos(tp), self.p.e_len as f64) else { continue };
            sim.entity_remove_buff(me, &zo("e_far"));
            sim.add_buff(me, &BuffV1::timed(&zo("e_far"), self.p.e_rel + 4));
            self.walls += 1;
            if self.walls <= 8 || self.walls % 20 == 0 {
                wlog(format!("{} BUBBLE #{} over a wall: the line to #{id} ({:.0} away) crosses {run:.0} of wall -> the long bubble ({} instead of {})", head(sim, me), self.walls, fdist(fpos(pos), fpos(tp)),
                             self.p.e_len + self.p.e_wall, self.p.e_len));
            }
        }
    }

    /// 催眠气泡：新标记 -> 困倦结束时数据的眩晕落下，挂上睡泡；睡着时挨了打就叫醒（补真实伤害），净化了或到时间摘掉睡泡。
    /// 0.8.0：飞着的气泡碰到第一个敌方单位就停，小兵、野怪也会中：她踢出气泡后 E_WINDOW tick 内所有敌方单位都看标记，
    /// 其余时候只看英雄（落地的陷阱只抓英雄）。
    fn bubble(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, foes: &[(usize, (u64, u64))], ap: usize, tick: usize) {
        let go = has_buff(sim, me, &zo("e_go"));
        if go && !self.e_go_was {
            self.e_scan_until = tick + E_WINDOW;
        }
        self.e_go_was = go;
        let mark = zo("e_mark");
        let now: Vec<usize> = if tick <= self.e_scan_until {
            (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.team() != team && e.is_alive())
                .filter(|e| (0..e.buff_count()).filter_map(|k| e.buff_at(k)).any(|b| b.name() == mark))
                .map(|e| e.id())
                .collect()
        } else {
            foes.iter().map(|f| f.0).filter(|&id| has_buff(sim, id, &mark)).collect()
        };
        for &id in &now {
            if !self.marked.contains(&id) {
                self.sleepers.retain(|s| s.target != id);
                self.sleepers.push(Sleeper { target: id, sleep_at: tick + self.p.e_drowsy, until: 0, guard: 0 });
            }
        }
        self.marked = now;
        let zz = zo("e_zz");
        let mut keep = Vec::new();
        for mut s in std::mem::take(&mut self.sleepers) {
            if !sim.get_entity(s.target).map_or(false, |e| e.is_alive()) {
                continue;
            }
            let guard = guard_of(sim, s.target);
            let drop = s.guard.saturating_sub(guard);
            let at = InputTargetV1::target(s.target);
            match watch(tick, s.sleep_at, s.until, held(sim, s.target), s.until != 0 && drop > 0) {
                Watch::Wait => keep.push(s),
                Watch::Asleep => {
                    s.guard = guard;
                    keep.push(s);
                }
                Watch::Fell => {
                    sim.add_buff(s.target, &BuffV1::timed(&zz, self.p.e_sleep_n));
                    s.until = tick + self.p.e_sleep_n;
                    s.guard = guard;
                    self.sleeps += 1;
                    let kind = what(sim, s.target);
                    if kind != "champion" {
                        self.unit_sleeps += 1;
                    }
                    if self.sleeps <= 8 || self.sleeps % 25 == 0 {
                        wlog(format!("{} SLEEP #{}: #{} ({kind}) asleep {} ticks after the drowsy ended, {} ticks", head(sim, me),
                                     self.sleeps, s.target, tick - s.sleep_at, self.p.e_sleep_n));
                    }
                    keep.push(s);
                }
                Watch::Missed => {
                    // cleansed or immune while drowsy (0.5.2's line: 11-03 / 11-05 every one of them was the game's
                    // sleep laid on Zoe's own feet - see the module's notes)
                    self.misses += 1;
                    if self.misses <= 8 || self.misses % 20 == 0 {
                        wlog(format!("{} MISS #{}: #{} not held {} ticks after the drowsy ended; crowd control now [{}]",
                                     head(sim, me), self.misses, s.target, tick - s.sleep_at, cc_list(sim, s.target)));
                    }
                }
                Watch::Hit => {
                    // any damage wakes him: only this sleep's stun comes off, the hit lands again as true damage (capped);
                    // the bonus is queued and lands after he is out of the list (no second wake)
                    let left = s.until.saturating_sub(tick);
                    wake_from_sleep(sim, s.target, left as u64);
                    sim.entity_remove_buff(s.target, &zz);
                    sim.play_view_effect(&zo("e_wake"), me, &at, 0, 0, 0);
                    sim.play_sfx(&zo("e_wake"), me, &at);
                    let bonus = wake_bonus(&self.p, drop, ap);
                    if bonus > 0 {
                        sim.deal_damage_typed(me, s.target, bonus, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                    }
                    self.wakes += 1;
                    if self.wakes <= 8 || self.wakes % 20 == 0 {
                        wlog(format!("{} WAKE #{}: #{} ({}) hit for {drop} asleep ({left} ticks left) -> +{bonus} true",
                                     head(sim, me), self.wakes, s.target, what(sim, s.target)));
                    }
                }
                Watch::Woke => {
                    sim.entity_remove_buff(s.target, &zz);
                    sim.play_view_effect(&zo("e_wake"), me, &at, 0, 0, 0);
                    self.freed += 1;
                    if self.freed <= 8 || self.freed % 20 == 0 {
                        wlog(format!("{} FREED #{}: #{}'s sleep came off {} ticks early (cleansed)", head(sim, me),
                                     self.freed, s.target, s.until - tick));
                    }
                }
                Watch::Ended => {
                    sim.entity_remove_buff(s.target, &zz);
                }
            }
        }
        self.sleepers = keep;
    }

    /// 窃法巧手的碎片：敌方英雄放大招时掉一块，她走近就捡起，射飞弹、加速。
    fn shards(&mut self, sim: &mut StableSim<'_>, me: usize, foes: &[(usize, (u64, u64))], pos: (u64, u64), alive: bool,
              ap: usize, tick: usize) {
        for &(id, at) in foes {
            let Some(cd) = sim.get_entity(id).and_then(|e| e.cooldown(SkillSlotV1::Ult)) else { continue };
            let now = cd.remaining;
            let was = self.ult_cd.iter().find(|c| c.0 == id).map(|c| c.1);
            if was.is_some_and(|w| ult_cast(w, now)) && dist(pos, at) <= SHARD_NEAR {
                if self.shards.len() >= MAX_SHARDS {
                    self.shards.remove(0);
                }
                self.shards.push(Shard { at, until: tick + self.p.s_t, next_view: tick });
                self.dropped += 1;
                if self.dropped <= 8 || self.dropped % 20 == 0 {
                    wlog(format!("{} SHARD #{}: #{id} cast his ult at {at:?}", head(sim, me), self.dropped));
                }
            }
            match self.ult_cd.iter_mut().find(|c| c.0 == id) {
                Some(c) => c.1 = now,
                None => self.ult_cd.push((id, now)),
            }
        }
        let mut keep = Vec::new();
        for mut s in std::mem::take(&mut self.shards) {
            if tick >= s.until {
                continue;
            }
            if alive && dist(pos, s.at) <= self.p.s_r as u64 {
                self.picked += 1;
                self.volleys.push((tick, self.p.w_n, "a shard"));
                let mut b = BuffV1::timed(&zo("w_haste"), self.p.w_ms_t);
                b.move_speed_mult = self.p.w_ms as i32;
                sim.add_buff(me, &b);
                wlog(format!("{} PICK #{}: shard at {:?} -> {} missiles", head(sim, me), self.picked, s.at, self.p.w_n));
                // 碎片的召唤师技能（0.8.0 起窃法巧手只从这里发动，大招不再触发）
                self.summon(sim, me, "a shard");
                continue;
            }
            if tick >= s.next_view {
                s.next_view = tick + SHARD_VIEW;
                let at = InputTargetV1::pos(s.at.0, s.at.1);
                sim.play_view_effect(&zo("w_shard"), me, &at, 0, 0, 0);
                // which spell it gives is picked at the pick-up: its icon cycles through the seven
                let icon = summon::Spell::ALL[tick / SHARD_VIEW % summon::Spell::ALL.len()];
                sim.play_view_effect(&zo(&format!("ss_{}", icon.key())), me, &at, 0, 0, 0);
            }
            keep.push(s);
        }
        self.shards = keep;
        // the shards' missiles (0.8.0: the ult fires none any more): one every w_gap ticks at the nearest enemy champion within
        // w_r, flown by fly() - out behind her, over her head, then after him (0.7.0; it was the hit at once, nothing flying)
        let mut left = Vec::new();
        for (at, n, from) in std::mem::take(&mut self.volleys) {
            if tick < at {
                left.push((at, n, from));
                continue;
            }
            if !alive {
                continue;
            }
            let near = foes.iter().map(|&(id, p_)| (dist(pos, p_), id)).filter(|&(d, _)| d <= self.p.w_r as u64).min();
            if let Some((_, id)) = near {
                let her = (pos.0 as f64, pos.1 as f64 - CHEST);
                let tp = foes.iter().find(|f_| f_.0 == id).map_or(pos, |f_| f_.1);
                let f = unit((tp.0 as f64 - her.0, tp.1 as f64 - AIM_LIFT - her.1)).unwrap_or((1.0, 0.0));
                let k = self.p.w_n.saturating_sub(n);
                self.missiles.push(Missile { target: id, dmg: shard_damage(&self.p, ap), born: tick, k, at: her, last: her, f,
                                             p: up_of(f), from });
                sim.play_sfx(&zo("w_shot"), me, &InputTargetV1::target(me));
                self.launched += 1;
                if self.launched <= 12 || self.launched % 30 == 0 {
                    wlog(format!("{} MISSILE #{} ({from}, {}/{}): at #{id} {} away", head(sim, me), self.launched, k + 1,
                                 self.p.w_n, dist(pos, tp)));
                }
            }
            if n > 1 {
                left.push((tick + self.p.w_gap, n - 1, from));
            }
        }
        self.volleys = left;
    }

    /// 飞着的飞弹（0.7.0）：先绕着她（`orbit_at`，她走到哪绕到哪），再追目标（`chase`），追上了结算伤害、放 `w_hit` 的画面
    /// 和声音；目标死了或没了就消失。她死了也飞完。每 tick 给每颗放一段 `w_missile` 的画面（`piece_spec`）。
    fn fly(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), tick: usize) {
        if self.missiles.is_empty() {
            return;
        }
        let her = (pos.0 as f64, pos.1 as f64 - CHEST);
        let speed = self.p.w_speed as f64;
        let mut keep = Vec::new();
        for mut m in std::mem::take(&mut self.missiles) {
            let Some(tp) = sim.get_entity(m.target).filter(|e| e.is_alive()).map(|e| e.pos()) else {
                self.fizzled += 1;
                if self.fizzled <= 8 || self.fizzled % 20 == 0 {
                    wlog(format!("{} MISSILE gone #{}: #{} died or left ({} ticks out)", head(sim, me), self.fizzled, m.target,
                                 tick.saturating_sub(m.born)));
                }
                continue;
            };
            let age = tick.saturating_sub(m.born);
            let next = if age < ORBIT_T {
                Some(orbit_at(her, m.f, m.p, age, m.k))
            } else {
                chase(m.at, (tp.0 as f64, tp.1 as f64 - AIM_LIFT), speed)
            };
            let Some(next) = next else {
                let t = InputTargetV1::target(m.target);
                sim.deal_damage_typed(me, m.target, m.dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                sim.play_view_effect(&zo("w_hit"), me, &t, 0, 0, 0);
                sim.play_sfx(&zo("w_hit"), me, &t);
                self.hits += 1;
                if self.hits <= 12 || self.hits % 30 == 0 {
                    wlog(format!("{} MISSILE hit #{} ({}): #{} for {} after {age} ticks", head(sim, me), self.hits, m.from,
                                 m.target, m.dmg));
                }
                continue;
            };
            m.last = m.at;
            m.at = next;
            let mv = (m.at.0 - m.last.0, m.at.1 - m.last.1);
            let dir = unit(mv).unwrap_or(m.f);
            let step = (mv.0 * mv.0 + mv.1 * mv.1).sqrt();
            if !sim.spawn_projectile(&zo("w_missile"), &format!("{ID}:noop"), &piece_spec(me, team, m.at, dir, step)) {
                self.refused += 1;
                if self.refused <= 4 || self.refused % 100 == 0 {
                    wlog(format!("{} MISSILE picture refused #{}: spawn_projectile {}", head(sim, me), self.refused,
                                 zo("w_missile")));
                }
            }
            keep.push(m);
        }
        self.missiles = keep;
    }
}

impl StablePassive for Sparkles {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.q_go_was = false;
        self.e_go_was = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Zoe (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let ap = e.stat().magic_power;
        let pos = e.pos();
        let alive = e.is_alive();
        let tick = sim.tick();
        let foes = enemies(sim, team);
        // 0.8.0 起大招不再触发窃法巧手（英雄联盟的折返跃迁不触发），副本的大招也不再挂 w_haste：召唤师技能和飞弹只从碎片来
        if tick > self.barrier_at + 1 && has_buff(sim, me, &zo("s_barrier")) && sim.get_entity(me).is_some_and(|e| e.shield() == 0) {
            sim.entity_remove_buff(me, &zo("s_barrier"));
        }
        self.burn(sim, me, ap, tick);
        // the stars flying and the sleepers go on after her death; only a living Zoe picks a shard up
        self.throw_star(sim, me, team, pos, tick);
        self.fly_stars(sim, me, team, pos, ap, tick);
        if alive {
            self.aim_bubble(sim, me, &foes, pos);
        }
        self.bubble(sim, me, team, &foes, ap, tick);
        self.shards(sim, me, &foes, pos, alive, ap, tick);
        self.fly(sim, me, team, pos, tick);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: stars {} (hit {} champions, {} other units, {} missed, {} thrown round the side), sleeps {} ({} not champions), bubbles over walls {}, wakes {}, freed {}, missed sleeps {}, shards dropped {} picked {}, summoner spells {}, missiles {} hit {} gone {} refused {}",
                             head(sim, me), self.thrown, self.star_champs, self.star_units, self.star_misses, self.sideways,
                             self.sleeps, self.unit_sleeps, self.walls, self.wakes, self.freed, self.misses, self.dropped, self.picked,
                             self.summons, self.launched, self.hits, self.fizzled, self.refused));
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
        "=== {ID} v{VERSION} (a sleep any damage breaks, on any unit; Paddle Star thrown out and redirected, by the distance flown; Spell Thief from the shards only, its missiles out behind her and over her head) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:sparkles"), Sparkles::default());
    // 0.7.0: the missiles' pictures are projectiles spawned piece by piece; a projectile needs an effect to apply on a hit
    module.add_native_effect(format!("{ID}:noop"), Noop);
    host.log(LogLevel::Info, "league_zoe v1 loaded (a sleep any damage breaks, Paddle Star redirected, Spell Thief's shards).");
}

/// 飞弹的画面一段一段地放（`piece_spec`），什么都不打（投射物要有一个打中时的效果）。
struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
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
    fn shards_fall_only_near_her() {
        // 「召唤师技能为什么满屏幕有」: a far ult drops nothing; a near one well beyond her pick-up reach still does
        let p = Params::default();
        assert!(SHARD_NEAR > 4 * p.s_r as u64 && SHARD_NEAR <= 200_000);
        assert!(dist((0, 0), (SHARD_NEAR + 1, 0)) > SHARD_NEAR);
    }

    #[test]
    fn the_sleep_falls_and_any_hit_wakes_him() {
        // the bubble's mark came off at 100: the data's stun lands about then and lasts 135
        assert_eq!(watch(99, 100, 0, false, false), Watch::Wait);
        assert_eq!(watch(90, 100, 0, true, false), Watch::Wait, "someone else's stun while he is only drowsy");
        assert_eq!(watch(100, 100, 0, true, false), Watch::Fell);
        assert_eq!(watch(101, 100, 0, true, true), Watch::Fell, "a hit before he is asleep wakes nothing");
        assert_eq!(watch(100 + SLEEP_LATE, 100, 0, false, false), Watch::Wait);
        assert_eq!(watch(101 + SLEEP_LATE, 100, 0, false, false), Watch::Missed, "cleansed or immune while drowsy");
        assert_eq!(watch(150, 100, 236, true, false), Watch::Asleep);
        assert_eq!(watch(150, 100, 236, true, true), Watch::Hit, "any damage wakes him");
        assert_eq!(watch(150, 100, 236, false, true), Watch::Woke, "cleansed (the hit came with it)");
        assert_eq!(watch(234, 100, 236, false, false), Watch::Ended, "its own end");
    }

    #[test]
    fn the_wake_up_hit_is_doubled_up_to_the_cap() {
        let p = Params::default();
        assert_eq!(wake_bonus(&p, 80, 100), 80);
        assert_eq!(wake_bonus(&p, 500, 100), 160); // 100 + 60 % of 100 AP
        assert_eq!(wake_bonus(&p, 0, 0), 0);
    }

    #[test]
    fn waking_keeps_every_other_control() {
        let stun = |t: u64| CcV1::stun(t);
        let up = CcV1::of_kind(CcKindV1::Airborne, 40);
        // our sleep has 90 ticks left; an ally's stun (30) and a knock-up (40) landed with the waking hit
        let kept = kept_after_wake(&[stun(30), stun(90), up], 90);
        assert_eq!(kept.iter().map(|c| (c.kind, c.tick)).collect::<Vec<_>>(),
                   vec![(CcKindV1::Stun.code(), 30), (CcKindV1::Airborne.code(), 40)]);
        // nothing but ours: nothing to put back; no Stun at all (already gone): everything back
        assert!(kept_after_wake(&[stun(89)], 90).is_empty());
        assert_eq!(kept_after_wake(&[up], 90).len(), 1);
    }

    #[test]
    fn the_copy_lays_a_stun_not_the_hypnotists_native() {
        // 0.4.0-0.5.2 laid the base Hypnotist's E (`hypnotist_skill2`) from the bubble's hit: the native takes its area's
        // centre from a point, and the unit hit gave it none - the sleep fell on Zoe's own feet (2026-11-05 log: 24 MISS,
        // crowd control [] on the target). The copy's bubble now stuns the champion hit for e_sleep_n, the Zz the add-on's
        let copy = include_str!("../override/league_zoe.data_champion");
        assert!(!copy.contains("hypnotist_skill2"), "the copy still calls the Hypnotist's native");
        let p = Params::default();
        assert!(copy.contains(&format!("\"duration\": {}", p.e_sleep_n)), "no e_sleep_n stun in the copy");
        assert!(copy.contains("\"e_cap\": 100") && copy.contains("\"e_cap_ratio\": 60"), "the wake cap is not in the params");
        // the pictures riding a unit come from the 1x sheet the game draws itself (a dense sheet's buff view is drawn PPU
        // times big, hanging right and down)
        for v in ["s_heal", "s_ignite", "s_exhaust", "s_ghost", "s_barrier", "s_cleanse"] {
            let at = copy.find(&format!("\"name\": \"league_zoe_{v}\"")).expect(v);
            let view = &copy[at..at + copy[at..].find('}').expect(v)];
            assert!(view.contains("\"anim\": \"asset/league/effects/league_zoe_spells_1x\""), "{v} is not on the 1x sheet");
        }
    }

    #[test]
    fn the_copy_leaves_the_star_and_spell_thief_to_the_add_on() {
        // 0.8.0 (「按照你的建议改吧」): the copy's Q throws no data star - it marks the target and lights q_go, this add-on flies
        // the star out and back; the copy's R no longer starts Spell Thief (no w_haste, no toss, no missiles); the bubble stops
        // on the first enemy unit and lights e_go for the sleep's wider look
        let copy = include_str!("../override/league_zoe.data_champion");
        let part = |from: &str, to: &str| {
            let a = copy.find(from).expect(from);
            &copy[a..a + copy[a..].find(to).expect(to)]
        };
        let q = part("\"skill\": {", "\"skill2\": {");
        assert!(!q.contains("LinearProjectile"), "the copy's Q still throws a data star");
        assert!(q.contains("\"league_zoe_q_go\"") && q.contains("\"league_zoe_q_aim\""));
        let e = part("\"skill2\": {", "\"ult\": {");
        assert!(e.contains("\"applied_target\": \"EnemyWithoutTower\""), "the bubble still passes minions");
        assert!(e.contains("\"league_zoe_e_go\""));
        // over a wall the long bubble (wall.rs): the target's e_aim at the start, her e_far picks it at the release
        assert!(e.contains("\"league_zoe_e_aim\"") && e.contains("\"buff_name\": \"league_zoe_e_far\""));
        let p = Params::default();
        assert!(e.contains(&format!("\"range\": {}", p.e_len + p.e_wall)) && e.contains(&format!("\"range\": {}", p.e_len)));
        let r = part("\"ult\": {", "\"view_projectiles\"");
        assert!(!r.contains("league_zoe_w_haste") && !r.contains("\"skill_w\"") && !r.contains("league_zoe_w_missile"),
                "the copy's R still starts Spell Thief");
        assert!(r.contains("league_zoe_r_star"), "the portal's star is gone");
        let params = part("\"params\": {", "}");
        assert!(params.contains("\"q_out\""), "no q_out: the add-on would take the copy for an old one");
    }

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"q_dmg":90,"q_far":220,"e_sleep_n":120,"e_cap":80,"w_n":2,"s_r":15000,"x":1}"#);
        assert_eq!((p.q_dmg, p.q_far, p.e_sleep_n, p.e_cap, p.w_n, p.s_r), (90, 220, 120, 80, 2, 15000));
        assert_eq!(p.q_ratio, Params::default().q_ratio);
        // a copy without q_out is older than 0.8.0: it flies its own data star
        assert!(!p.star);
        assert_eq!(parse_params("{}"), Params { star: false, ..Params::default() });
        let p = parse_params(r#"{"q_out":25000,"q_out_v":1800,"q_speed":4200,"q_len":90000,"q_w":5000}"#);
        assert!(p.star);
        assert_eq!((p.q_out, p.q_out_v, p.q_speed, p.q_len, p.q_w), (25000, 1800, 4200, 90000, 5000));
        assert_eq!(parse_params(r#"{"w_gap":0,"q_far":50}"#).w_gap, 1);
        assert_eq!(parse_params(r#"{"q_far":50}"#).q_far, 100);
    }

    #[test]
    fn the_star_grows_with_the_distance_flown() {
        let p = Params::default();
        assert_eq!(star_pct(&p, 0), 100);
        assert_eq!(star_pct(&p, 20000), 100);
        assert_eq!(star_pct(&p, 52500), 175); // half way: half of the +150 %
        assert_eq!(star_pct(&p, 85000), 250);
        assert_eq!(star_pct(&p, 200000), 250);
        // 105 + 60 % of 100 AP = 165; at the far end 250 % of it
        assert_eq!(star_damage(&p, 85000, 100), 412);
        assert_eq!(star_damage(&p, 10000, 100), 165);
    }


    #[test]
    fn an_ult_cast_is_a_cooldown_jumping_up_from_ready() {
        assert!(ult_cast(0, 3000));
        assert!(!ult_cast(0, 0));
        assert!(!ult_cast(0, 30)); // a small reset, not a cast
        assert!(!ult_cast(2000, 2999)); // still on cooldown
        assert_eq!(shard_damage(&Params::default(), 200), 75);
    }

    #[test]
    fn buff_names_fit() {
        for x in ["e_mark", "e_zz", "e_wake", "e_go", "e_aim", "e_far", "q_go", "q_aim", "q_hit", "q_star", "r_on", "w_haste", "w_shard", "w_shot", "w_hit", "e_sleep", "s_heal", "s_ignite", "s_exhaust", "s_ghost", "s_flash", "s_flash_trail", "s_cleanse", "s_barrier"] {
            assert!(zo(x).len() <= BUFF_NAME_CAP);
        }
        for s in summon::Spell::ALL {
            assert!(zo(&format!("sg_{}", s.key())).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn missiles_come_out_behind_her_over_her_head_to_her_front() {
        // 「从背后过来的」: a foe on her right - the arc starts on her left (behind), tops above her head, ends on her right
        let c = (100_000.0, 83_000.0); // her chest, her feet at y 100000
        let f = unit((60_000.0, -3_000.0)).unwrap();
        let p = up_of(f);
        assert!(p.1 < -0.9, "the arc goes up the screen: {p:?}");
        let first = orbit_at(c, f, p, 0, 0);
        assert!(first.0 < c.0, "it appears behind her: {first:?}");
        let top = (0..ORBIT_T).map(|a| orbit_at(c, f, p, a, 0)).fold(f64::MAX, |m, q| m.min(q.1));
        assert!(100_000.0 - top > 36_000.0, "it passes over her head (36 rows): {}", 100_000.0 - top);
        let last = orbit_at(c, f, p, ORBIT_T - 1, 0);
        assert!(last.0 > c.0 + ORBIT_RX * 0.9 && (last.1 - c.1).abs() < 3_000.0, "it ends before her: {last:?}");
        // a foe on her left: the mirror - starts on her right, still over the top
        let f2 = unit((-60_000.0, 0.0)).unwrap();
        let p2 = up_of(f2);
        assert!(p2.1 < -0.9 && orbit_at(c, f2, p2, 0, 0).0 > c.0);
        // the three stay apart: each later one a smaller arc
        assert!(orbit_at(c, f, p, 5, 1).1 > orbit_at(c, f, p, 5, 0).1);
    }

    #[test]
    fn a_missile_chases_until_the_step_reaches_him() {
        let speed = Params::default().w_speed as f64;
        let mut at = (0.0, 0.0);
        let aim = (30_000.0, 4_000.0);
        let mut steps = 0;
        while let Some(n) = chase(at, aim, speed) {
            at = n;
            steps += 1;
            assert!(steps < 20);
        }
        assert_eq!(steps, 7); // 30266 away at 4000 a tick
        assert!(chase((0.0, 0.0), (100.0, 0.0), speed).is_none());
    }

    #[test]
    fn a_missile_picture_lies_where_it_is_drawn_after_its_first_step() {
        let s = piece_spec(1, 0, (50_000.0, 40_000.0), (1.0, 0.0), 4_000.0);
        assert_eq!((s.x, s.y, s.target_x, s.target_y, s.speed), (46_000, 40_000, 54_000, 40_000, 4_000));
        // a tick it hardly moved still gets a picture that outlives the tick
        assert_eq!(piece_spec(1, 0, (50_000.0, 40_000.0), (0.0, -1.0), 0.0).speed, PIECE_MIN as u64);
    }

    #[test]
    fn the_missiles_numbers_come_from_the_champion_data() {
        let p = parse_params(r#"{"w_rel":5,"w_speed":3500}"#);
        assert_eq!((p.w_rel, p.w_speed), (5, 3500));
        assert_eq!(parse_params(r#"{"w_speed":0}"#).w_speed, 1);
    }
}
