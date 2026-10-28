//! 佐伊附加包：照英雄联盟的规则做主包数据做不到的三件事。
//!
//! 主包保持纯数据：飞星按飞行时间分近 / 中 / 远三档伤害，窃法巧手只跟着大招射飞弹；昏睡从游戏 0.7.0 起是游戏自己的睡眠（主包、
//! 副本都一样，见下）。`mod.override_info` 把主包的佐伊换成 `override/` 里的副本（`tools/kit/build_zoe.py --native`），被动
//! `league_zoe:sparkles`：
//!
//! - **催眠气泡**（0.4.0，用户：「新控制"睡眠"……冲突就直接调用官方的」「这两个顺带一起改了」）：困倦结束时数据里落下
//!   **游戏的官方睡眠**（催眠师 E 的原生效果 `hypnotist_skill2`，副本 `e_sleep_n` tick，英雄联盟 2.25 秒）：**任何伤害**都会
//!   打醒，打醒的那一下伤害提高 `e_amp`%，画面和声音都是游戏的。副本里气泡打中英雄时另挂 `league_zoe_e_mark`（困倦那
//!   `e_drowsy` tick）；被动看见新的标记，睡眠落下时给他挂睡泡 `league_zoe_e_zz`，醒了就摘掉，被打醒的放 `league_zoe_e_wake`
//!   的画面（[`watch`]；稳定接口把睡眠报成眩晕）。以前自己的昏睡（原生眩晕）、自己打醒、补真实伤害（有封顶）都去掉了。
//! - **飞星乱入！**：副本里飞星打中的单位挂 `league_zoe_q_hit`（2 tick），伤害只算近的一档；她出手时身上有 `league_zoe_q_go`。
//!   被动记下出手的位置，打中时按真实距离补上：`q_n0` 以内不加，到 `q_n1d` 加到 `q_far`%（中间线性）。
//! - **窃法巧手**：敌方英雄放大招（大招冷却从 0 跳起来）时原地掉下一块法术碎片（`league_zoe_w_shard`，`s_t` tick），她走到 `s_r`
//!   以内就捡起来：`w_n` 颗飞弹（每 `w_gap` tick 一颗，打 `w_r` 以内最近的敌方英雄，每颗 `w_dmg` + `w_ratio`% 法强魔法伤害）
//!   和 `w_ms`% 移速 `w_ms_t` tick（英雄联盟：捡起召唤师技能 / 主动装备的碎片）。主包大招自己的 3 颗飞弹照旧。
//!
//! - **召唤师技能**（0.2.0，用户：「可以改成召唤师技能那种效果吗 随机的」「能做成智能释放吗」）：窃法巧手每次发动（大招射
//!   飞弹那一刻 = 身上的 `league_zoe_w_haste` 刚挂上，或捡起碎片时）先放一个召唤师技能，再射原来的飞弹：按局面挑（`summon.rs`：
//!   被控净化、残血被贴脸闪现、残血或队友快死治疗、敌人快死点燃、被贴脸虚弱、打架掉血屏障、附近没人幽灵疾步），都不是就在
//!   点燃 / 虚弱 / 屏障 / 幽灵疾步里随机（比赛的种子定，两份模拟一样）。数字在下面的 `S_*`。日志 `SUMMON`。
//!   画面（0.3.0，用户：「加啊」「地面上最好也要有图标显示」）：放的时候她脚下的地上亮起那个技能的图标
//!   （`league_zoe_sg_<技能>`）；闪现在她和被弹开的人身上一闪（`s_flash`），净化一道光环从脚扫到头（`s_cleanse`），屏障一个金色
//!   气泡（`s_barrier`），治疗、点燃、虚弱、幽灵疾步是它们 buff 的画面；地上的碎片每次重画换一个图标（`ss_<技能>`，七个轮流），
//!   捡起来才按局面定是哪个。图在 `league_zoe_spells`（tools/art/draw_zoe_spells.py）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个佐伊自己的被动实例里，
//! 服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zoe.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

mod maps;
pub mod summon;

const ID: &str = "league_zoe";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.4.0";
/// 场上最多同时留几块碎片（多了丢最早的）。
const MAX_SHARDS: usize = 3;
/// 碎片的画面多少 tick 重放一次（画面 4 帧 x 约 100 ms）。
const SHARD_VIEW: usize = 15;
/// 飞星出手后多少 tick 内看打中（95000 / 4000 一 tick 不到 30 tick 就飞完）。
const Q_WINDOW: usize = 60;
/// 大招冷却从 0 跳到多少以上算放了大招。
const ULT_JUMP: usize = 60;
/// 困倦结束后多少 tick 内看见控制才算这一泡的睡眠（数据里官方睡眠在标记掉的那一 tick 之后一两 tick 落下）。
pub const SLEEP_LATE: usize = 4;

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
    /// 催眠气泡：困倦的 tick，睡眠的 tick（数据里官方睡眠的时长）。
    pub e_drowsy: usize,
    pub e_sleep_n: usize,
    /// 碎片的飞弹：每颗伤害（固定值、法强 %）、颗数、间隔 tick、找目标的距离；移速 % 和 tick。
    pub w_dmg: usize,
    pub w_ratio: usize,
    pub w_n: usize,
    pub w_gap: usize,
    pub w_r: usize,
    pub w_ms: usize,
    pub w_ms_t: usize,
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
            e_drowsy: 84,
            e_sleep_n: 135,
            w_dmg: 45,
            w_ratio: 15,
            w_n: 3,
            w_gap: 5,
            w_r: 70000,
            w_ms: 40,
            w_ms_t: 150,
            s_t: 1200,
            s_r: 18000,
        }
    }
}

/// `{"q_dmg":105,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "q_dmg" => &mut p.q_dmg,
            "q_ratio" => &mut p.q_ratio,
            "q_far" => &mut p.q_far,
            "q_n0" => &mut p.q_n0,
            "q_n1d" => &mut p.q_n1d,
            "e_drowsy" => &mut p.e_drowsy,
            "e_sleep_n" => &mut p.e_sleep_n,
            "w_dmg" => &mut p.w_dmg,
            "w_ratio" => &mut p.w_ratio,
            "w_n" => &mut p.w_n,
            "w_gap" => &mut p.w_gap,
            "w_r" => &mut p.w_r,
            "w_ms" => &mut p.w_ms,
            "w_ms_t" => &mut p.w_ms_t,
            "s_t" => &mut p.s_t,
            "s_r" => &mut p.s_r,
            _ => continue,
        };
        *slot = v;
    }
    p.q_n1d = p.q_n1d.max(p.q_n0 + 1);
    p.q_far = p.q_far.max(100);
    p.w_gap = p.w_gap.max(1);
    p
}

// ===================== 计算 =====================

/// 飞星飞了 `dist` 时总伤害的倍数（%）：`q_n0` 以内 100，到 `q_n1d` 加到 `q_far`。
pub fn star_pct(p: &Params, dist: u64) -> usize {
    let (lo, hi) = (p.q_n0 as u64, p.q_n1d as u64);
    let d = dist.clamp(lo, hi);
    100 + ((p.q_far - 100) as u64 * (d - lo) / (hi - lo)) as usize
}

/// 飞星在近的一档之外补的魔法伤害（减免前）。
pub fn star_bonus(p: &Params, dist: u64, ap: usize) -> usize {
    let base = p.q_dmg + p.q_ratio * ap / 100;
    base * (star_pct(p, dist) - 100) / 100
}

/// 一颗碎片飞弹的魔法伤害（减免前）。
pub fn shard_damage(p: &Params, ap: usize) -> usize {
    p.w_dmg + p.w_ratio * ap / 100
}

/// 大招冷却从 `was` 变成 `now`：放了大招（从好着跳到 ULT_JUMP 以上）。
pub fn ult_cast(was: usize, now: usize) -> bool {
    was == 0 && now > ULT_JUMP
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
    /// 困倦结束、官方睡眠落下的 tick。
    sleep_at: usize,
    /// 睡着后到这一 tick 自己醒；0 = 还没睡着。
    until: usize,
}

/// 这一 tick 对一个中了气泡的人做什么（[`watch`]）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Watch {
    /// 还困着，或睡眠还没落下。
    Wait,
    /// 睡着了：挂上睡泡。
    Fell,
    /// 没睡着（净化了、跳出了睡眠的范围）：不管了。
    Missed,
    /// 还睡着。
    Asleep,
    /// 提前醒了（被打醒）：摘掉睡泡，放醒来的画面。
    Woke,
    /// 到时间自己醒了：摘掉睡泡。
    Ended,
}

/// 中了气泡的人这一 tick 的样子：`sleep_at` 困倦结束的 tick，`until` 睡着后自己醒的 tick（还没睡着是 0），`held` 他身上有
/// 眩晕（稳定接口把游戏的睡眠报成眩晕）。困倦时别人的眩晕不算睡着。
pub fn watch(tick: usize, sleep_at: usize, until: usize, held: bool) -> Watch {
    if until == 0 {
        if held && tick >= sleep_at {
            Watch::Fell
        } else if tick > sleep_at + SLEEP_LATE {
            Watch::Missed
        } else {
            Watch::Wait
        }
    } else if held {
        Watch::Asleep
    } else if tick + 2 < until {
        Watch::Woke
    } else {
        Watch::Ended
    }
}

#[derive(Clone, Debug)]
struct Shard {
    at: (u64, u64),
    until: usize,
    next_view: usize,
}

/// 每个佐伊一份。
#[derive(Clone, Default)]
struct Sparkles {
    p: Params,
    sleepers: Vec<Sleeper>,
    /// 上一 tick 身上有气泡标记的敌方英雄。
    marked: Vec<usize>,
    /// 飞星出手的位置和看打中到哪一 tick。
    q_from: Option<((u64, u64), usize)>,
    q_go_was: bool,
    /// 上一 tick 身上有飞星标记的单位。
    q_seen: Vec<usize>,
    /// 每个敌方英雄上一 tick 的大招冷却。
    ult_cd: Vec<(usize, usize)>,
    shards: Vec<Shard>,
    /// 还要射的碎片飞弹：(射的 tick, 剩几颗)。
    volleys: Vec<(usize, usize)>,
    stars: usize,
    sleeps: usize,
    wakes: usize,
    picked: usize,
    dropped: usize,
    next_report: usize,
    /// 上一 tick 身上有没有 w_haste（刚挂上 = 大招的窃法巧手）、点燃：(目标, 下一跳的 tick, 还剩几跳)、放过几次召唤师技能。
    haste_was: bool,
    burns: Vec<(usize, usize, usize)>,
    summons: usize,
    /// 屏障放出的 tick（护盾归零后摘掉气泡，放出那一 tick 不算）。
    barrier_at: usize,
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id)
        .map_or(false, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 身上有眩晕（游戏的睡眠在稳定接口里就是眩晕）。
fn held(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id)
        .map_or(false, |e| (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| c.kind == CcKindV1::Stun.code()))
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

impl Sparkles {
    /// 窃法巧手发动：按局面挑一个召唤师技能放（summon.rs），`why` 是谁触发的（大招 / 捡碎片）。
    fn summon(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
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
        let (spell, target, reason) = summon::pick(me_hp, controlled, &foes, &allies, summon::roll(sim.seed(), tick, me));
        let on_me = InputTargetV1::target(me);
        sim.play_view_effect(&zo(&format!("sg_{}", spell.key())), me, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
        match spell {
            summon::Spell::Cleanse => {
                sim.entity_clear_cc(me);
                sim.play_view_effect(&zo("s_cleanse"), me, &on_me, 0, 0, 0);
            }
            summon::Spell::Flash => {
                // a flash where she was and where she lands (s_flash stays where it is played)
                sim.play_view_effect(&zo("s_flash"), me, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
                let from = target.and_then(|t| sim.get_entity(t)).map(|t| t.pos());
                if let Some(to) = from.and_then(|f| summon::flash_spot(pos, f)) {
                    sim.entity_set_pos(me, to.0, to.1);
                    sim.play_view_effect(&zo("s_flash"), me, &InputTargetV1::pos(to.0, to.1), 0, 0, 0);
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

    /// 飞星：出手时记下位置，打中时按真实距离补伤害。
    fn star(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), ap: usize, tick: usize) {
        let go = has_buff(sim, me, &zo("q_go"));
        if go && !self.q_go_was {
            self.q_from = Some((pos, tick + Q_WINDOW));
        }
        self.q_go_was = go;
        let Some((from, until)) = self.q_from else { return };
        if tick > until {
            self.q_from = None;
            self.q_seen.clear();
            return;
        }
        let mark = zo("q_hit");
        let mut now = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.team() == team || !e.is_alive() || e.is_tower() {
                continue;
            }
            let id = e.id();
            if (0..e.buff_count()).filter_map(|k| e.buff_at(k)).any(|b| b.name() == mark) {
                now.push((id, e.pos()));
            }
        }
        for &(id, at) in &now {
            if self.q_seen.contains(&id) {
                continue;
            }
            let d = dist(from, at);
            let bonus = star_bonus(&self.p, d, ap);
            if bonus > 0 {
                sim.deal_damage_typed(me, id, bonus, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
            self.stars += 1;
            if self.stars <= 8 || self.stars % 25 == 0 {
                wlog(format!("{} STAR #{}: #{id} hit {d} away -> x{}% (+{bonus} magic)", head(sim, me), self.stars,
                             star_pct(&self.p, d)));
            }
        }
        self.q_seen = now.into_iter().map(|(id, _)| id).collect();
    }

    /// 催眠气泡：新标记 -> 困倦结束时游戏的睡眠落下，挂上睡泡；醒了（被打醒或到时间）摘掉。睡和醒都是游戏的：这里只管画面。
    fn bubble(&mut self, sim: &mut StableSim<'_>, me: usize, foes: &[(usize, (u64, u64))], tick: usize) {
        let mark = zo("e_mark");
        let now: Vec<usize> = foes.iter().map(|f| f.0).filter(|&id| has_buff(sim, id, &mark)).collect();
        for &id in &now {
            if !self.marked.contains(&id) {
                self.sleepers.retain(|s| s.target != id);
                self.sleepers.push(Sleeper { target: id, sleep_at: tick + self.p.e_drowsy, until: 0 });
            }
        }
        self.marked = now;
        let zz = zo("e_zz");
        let mut keep = Vec::new();
        for mut s in std::mem::take(&mut self.sleepers) {
            if !sim.get_entity(s.target).map_or(false, |e| e.is_alive()) {
                continue;
            }
            match watch(tick, s.sleep_at, s.until, held(sim, s.target)) {
                Watch::Wait | Watch::Asleep => keep.push(s),
                Watch::Fell => {
                    sim.add_buff(s.target, &BuffV1::timed(&zz, self.p.e_sleep_n));
                    s.until = tick + self.p.e_sleep_n;
                    self.sleeps += 1;
                    keep.push(s);
                }
                Watch::Missed => {}
                Watch::Woke => {
                    sim.entity_remove_buff(s.target, &zz);
                    sim.play_view_effect(&zo("e_wake"), me, &InputTargetV1::target(s.target), 0, 0, 0);
                    self.wakes += 1;
                    if self.wakes <= 8 || self.wakes % 20 == 0 {
                        wlog(format!("{} WAKE #{}: #{} woke {} ticks early", head(sim, me), self.wakes, s.target, s.until - tick));
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
            if was.is_some_and(|w| ult_cast(w, now)) {
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
                self.volleys.push((tick, self.p.w_n));
                let mut b = BuffV1::timed(&zo("w_haste"), self.p.w_ms_t);
                b.move_speed_mult = self.p.w_ms as i32;
                sim.add_buff(me, &b);
                wlog(format!("{} PICK #{}: shard at {:?} -> {} missiles", head(sim, me), self.picked, s.at, self.p.w_n));
                // the shard's summoner spell (its w_haste is not the ult's: no second summon next tick)
                self.haste_was = true;
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
        // the missiles: one every w_gap ticks at the nearest enemy champion within w_r
        let mut left = Vec::new();
        for (at, n) in std::mem::take(&mut self.volleys) {
            if tick < at {
                left.push((at, n));
                continue;
            }
            if !alive {
                continue;
            }
            let near = foes.iter().map(|&(id, p_)| (dist(pos, p_), id)).filter(|&(d, _)| d <= self.p.w_r as u64).min();
            if let Some((_, id)) = near {
                let t = InputTargetV1::target(id);
                sim.play_sfx(&zo("w_shot"), me, &t);
                sim.deal_damage_typed(me, id, shard_damage(&self.p, ap), DamageTypeV1::Ap, AttackTypeV1::Skill);
                sim.play_view_effect(&zo("w_hit"), me, &t, 0, 0, 0);
            }
            if n > 1 {
                left.push((tick + self.p.w_gap, n - 1));
            }
        }
        self.volleys = left;
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
        // the ult's Spell Thief: its w_haste just put on - the summoner spell first (the data fires the missiles)
        let haste = alive && has_buff(sim, me, &zo("w_haste"));
        if haste && !self.haste_was {
            self.summon(sim, me, "the ult");
        }
        self.haste_was = haste;
        if tick > self.barrier_at + 1 && has_buff(sim, me, &zo("s_barrier")) && sim.get_entity(me).is_some_and(|e| e.shield() == 0) {
            sim.entity_remove_buff(me, &zo("s_barrier"));
        }
        self.burn(sim, me, ap, tick);
        // the star flying and the sleepers go on after her death; only a living Zoe picks a shard up
        self.star(sim, me, team, pos, ap, tick);
        self.bubble(sim, me, &foes, tick);
        self.shards(sim, me, &foes, pos, alive, ap, tick);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: stars {}, sleeps {}, wakes {}, shards dropped {} picked {}, summoner spells {}",
                             head(sim, me), self.stars, self.sleeps, self.wakes, self.dropped, self.picked, self.summons));
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
        "=== {ID} v{VERSION} (the Zz of the game's sleep, Paddle Star by distance, Spell Thief's shards) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:sparkles"), Sparkles::default());
    host.log(LogLevel::Info, "league_zoe v1 loaded (the Zz of the game's sleep, Paddle Star by distance, Spell Thief's shards).");
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
    fn the_zz_follows_the_games_sleep() {
        // the bubble's mark came off at 100: the game's sleep lands a tick or two later and lasts 135
        assert_eq!(watch(99, 100, 0, false), Watch::Wait);
        assert_eq!(watch(90, 100, 0, true), Watch::Wait, "someone else's stun while he is only drowsy");
        assert_eq!(watch(101, 100, 0, true), Watch::Fell);
        assert_eq!(watch(100 + SLEEP_LATE, 100, 0, false), Watch::Wait);
        assert_eq!(watch(101 + SLEEP_LATE, 100, 0, false), Watch::Missed, "cleansed, or out of the sleep's reach");
        assert_eq!(watch(150, 100, 236, true), Watch::Asleep);
        assert_eq!(watch(150, 100, 236, false), Watch::Woke, "hit: the game woke him");
        assert_eq!(watch(234, 100, 236, false), Watch::Ended, "its own end");
    }

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"q_dmg":90,"q_far":220,"e_sleep_n":120,"w_n":2,"s_r":15000,"x":1}"#);
        assert_eq!((p.q_dmg, p.q_far, p.e_sleep_n, p.w_n, p.s_r), (90, 220, 120, 2, 15000));
        assert_eq!(p.q_ratio, Params::default().q_ratio);
        assert_eq!(parse_params("{}"), Params::default());
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
        // 105 + 60 % of 100 AP = 165; at the far end 150 % more
        assert_eq!(star_bonus(&p, 85000, 100), 247);
        assert_eq!(star_bonus(&p, 10000, 100), 0);
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
        for x in ["e_mark", "e_zz", "e_wake", "q_go", "q_hit", "w_haste", "w_shard", "w_shot", "w_hit", "e_sleep", "s_heal", "s_ignite", "s_exhaust", "s_ghost", "s_flash", "s_cleanse", "s_barrier"] {
            assert!(zo(x).len() <= BUFF_NAME_CAP);
        }
        for s in summon::Spell::ALL {
            assert!(zo(&format!("sg_{}", s.key())).len() <= BUFF_NAME_CAP);
        }
    }
}
