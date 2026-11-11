//! 卡尔萨斯附加包（用户选「被动做附加包」）：主包数据做不到的死亡契约。
//!
//! `mod.override_info` 把主包的卡尔萨斯换成 `override/` 里的副本（tools/kit/build_karthus.py 的 native=1）：数据和主包
//! 一样，只是被动挂本包的 `league_karthus:death_defied`（参数在英雄数据的 `passive.params` 里），多一个灵体的画面。
//!
//! - **死亡契约**：英雄联盟里卡尔萨斯死后化成灵体，7 秒内照样放技能，然后才倒下；灵体选不中、不受伤害、免控，不能走动、
//!   不能普攻。数据读不到血量，主包做不了。本包一直给他挂着「不死」`league_karthus_p_guard`，致命伤害只会把他打到 1 血；
//!   到 1 血（身上没有别人给的不死）时**化成灵体** `p_t` tick。
//! - **灵体照英雄联盟**（0.5.0，用户 2026-11-03：「死了灵体还能移动 还能有残血？」「这能和英雄联盟一样吗」「还有死了后为什么
//!   AI还攻击灵体 很奇怪啊」）：0.4.x 的灵体是 1 血、活着的他——游戏只认放逐是选不中，它只放了开头 12 tick：之后小兵、塔照打
//!   （1 血的英雄正是 AI 最想补的），挨每个英雄的钩子 `shun` 拦下的出手也照样飞来，头上挂着一条残血，移速 −100% 也挡不住位移。
//!   现在**整个灵体放逐着**（`entity_banish` `p_t` tick，扎亨复活的做法）：谁都选不中、打不到，没有血条，不能走、不能回城；
//!   倒下的地方画着他的灵体（`league_karthus_p_ghost_r` / `_l`，`tools/art/draw_karthus_ghost.py`，面朝最近的敌方英雄；0.5.6
//!   以前是放逐的锁定画面），身体每 tick 钉住（0.5.7 起等在泉水里，见下）。放逐也锁住他自己出手，所以**灵体的技能由本包放**（`spirit_casts`，数字、画面照主包）：亵渎一直
//!   烧（每 `E_PER` tick 圈里每个敌人），荒芜每 `Q_CD` tick 落在射程里最近的敌方英雄（没有就别的单位）脚下（`Q_DELAY` tick 后
//!   炸开，只炸到一个两倍），安魂曲好了又值得（`r_worth`）时引导 `R_CH` tick 打每个敌方英雄。击杀照样算他的。
//! - **灵体就是已经死了**（0.4.1，用户 2026-11-03：「灵体死了还能回城的？？？」「灵体出现就代表已经是死亡了 懂吗」「有时候
//!   死了又没灵体」）：不能回城，倒下后复活倒计时扣掉灵体待的时间（英雄联盟从化成灵体就开始算，`life.rs` 改游戏的剩余复活
//!   tick）。
//! - **倒下就是真的死了**（0.5.1，用户 2026-11-03：「不行死歌还是不对 灵体结束后还能回城」「被人击杀后显示灵体就已经是死亡了
//!   啊」）：0.4.x、0.5.0 倒下时在同一 tick 里先摘掉灵体的 buff（不死、减伤 100%）再补致命一击，可这一 tick 里刚摘掉的 buff
//!   还算数，那一下只打出 1 点：他 1 血活下来，放逐一完游戏的 AI 就让他回城（11-03 晚上的日志：倒下后同一个他还在下命令，
//!   回城日志里倒下一秒后他 0% 血回城；身边有敌人时随手被补掉，看着像倒下了，0.4.2 不放逐时也一样）。现在灵体最后一 tick
//!   （`Stage::LayDown`）把 `p_spirit` 换成 `p_fall`（不死、减伤都没有，照样钉住、谁都不选），灵体的放逐正好在时间到时结束，
//!   下一 tick 才补致命一击（`strike`；伤害在那一 tick 结算时才扣），再下一 tick 他还站着就再补（`FALL RETRY`），`FALL_SLACK`
//!   tick 还不行就把血设成 0（`FALL FORCED`）。倒下前他什么命令都不下，回城也换成原地站着（`SPIRIT RECALL STOPPED`）；韧性缩短了
//!   放逐、灵体中途能被选中时重新放逐（`REBANISH`）。复活倒计时：0.4.x 在 `on_dead` 里改（那时游戏还没把他记成阵亡）、0.5.0
//!   由他自己的 AI 钩子在阵亡后改（阵亡后他自己的钩子都不跑了），都没改成过（11-03 的日志一条 `RESPAWN` 都没有）；现在
//!   `on_dead` 记下要扣的时间，等游戏登记好阵亡再扣（`cut_respawns`）。0.5.2：0.5.1 由每个英雄的 AI 钩子 `shun` 扣、按模拟状态
//!   指针配对，可 AI 钩子拿到的指针和被动的不一样，11-03 晚上 120 次全没扣成；现在由本包的比赛钩子（`Respawns`，每局每 tick）
//!   扣，按「哪一局」（种类、比赛、小局）、玩家、阵亡 tick 配对，扣到同一个复活 tick（同一局并排的两份预演共用一条，扣不了两遍）。
//!   0.5.3（用户 2026-11-04：「死歌灵体死了后秒复活？」）：0.5.2 的记录按真实时间放 30 秒，期间他再死一次就被旧记录扣成 1 tick；
//!   现在一条记录只管它那一次阵亡（`note_open`）。0.5.5（2026-11-06，画面和预模拟分叉的排查）：每份模拟一条记录，按这份模拟的
//!   编号（被动挂在他身上的 `league_karthus_sim:<n>`，尸体上留到复活）认，只由这份模拟扣、按它自己的 tick 删；以前按「哪一局」
//!   配，预模拟没有局号，同一场比赛别的小局的预模拟也会被它扣，记录还按真实时间丢。0.5.6（2026-11-08 的日志检查）：0.5.5 起
//!   一次都没扣成（11-08 的日志一条 `RESPAWN:` 都没有，全是 `RESPAWN NOT CUT (no match tick found …)`）——游戏在他阵亡时清掉
//!   尸体身上的 buff（尸体留着 buff 只是 SDK 里的事），比赛钩子从尸体上读不到编号。现在编号也挂在水晶上（水晶不收就挂防御塔，
//!   league_eggs 的做法；开局第 1 tick 挂，每 `ANCHOR_RETRY` tick 看一眼还在不在），记录带着这些建筑，比赛钩子认建筑上的编号。
//! - **灵体照样放技能**（0.5.1，用户 2026-11-03：「灵体状态下会放其他技能吗 也检查下 我怎么感觉不会放」）：放逐的单位不给队伍
//!   视野，0.5.0 的灵体只挑他队伍看得见的敌人，身边没队友时荒芜、亵渎什么都打不到（只有不看视野的安魂曲放得出来）；现在用灵体
//!   自己的眼睛（射程里的都算，亵渎和荒芜的爆炸本来就不挑）。痛苦之墙主包挂在普攻上，灵体不能普攻，一面都没立过；现在 W 好了
//!   （他身上没有 `w_cd` 标记）就立在 `W_R` 里最近的敌方英雄身上，照主包的墙减速、减魔抗。`FALL` 记下这个灵体放了几次 Q、W、
//!   E、R。
//! - **敌人不再围着灵体等**（0.5.7，玩家反馈 2026-11-10：「死歌灵体后 AI 会在附近一直等着」）：放逐着的身体对游戏的 AI 还是
//!   一个活着的敌方英雄，站在倒下的地方，周围的敌人就围着等到他倒下（11-10 的日志：灵体期间几乎没人对他下命令，`SHUN` 只在
//!   灵体开头和倒下那一刻）。游戏的 AI 不管泉水里的敌人（0.5.1 SDK 带符号的 game_core 里的 `is_ignored_battle_enemy`，0.7.1 的
//!   EXE 里同样的范围比较有一百多处），所以灵体期间身体等在自家泉水（出生点，[`body_at`]），放逐结束前 `BACK_EARLY` tick 回到
//!   倒下的地方，倒下、死亡动作照旧在那里。灵体的画面改成倒下的地方单独放的一张图（放逐的锁定画面跟着身体走），技能本来就按
//!   倒下的地方放；`shun` 让人退出亵渎圈也按倒下的地方算（身上挂着 [`SPOT_TAG`]）。`SPAWN` 记下出生点在不在游戏认的泉水里，
//!   `FALL` 记下倒下的地方附近的敌方英雄（化成灵体时、灵体期间平均、最后）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_karthus.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
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
/// 灵体倒下后，复活倒计时扣掉灵体待了的 tick，至少还剩这么多（`respawn_after_spirit`）。
pub const BACK_MIN: u64 = 60;
/// 倒下（0.5.1）：灵体的放逐在灵体的时间到时结束；之后他还选不中（别人的放逐）最多等 `FALL_WAIT` tick 再补致命一击；
/// 补了 `FALL_SLACK` tick 还没倒下就把血设成 0（之后照样每 tick 补，倒下前他什么命令都不下）。
pub const FALL_WAIT: usize = 10;
pub const FALL_SLACK: usize = 60;
/// 灵体开始这么多 tick 后，他又能被选中了（韧性缩短了放逐）就重新放逐（`rebanish`）。
pub const REBANISH_AFTER: usize = 2;
/// 复活倒计时（`cut_respawns`）：阵亡后最多等游戏这么多 tick 把他登记成阵亡（按这份模拟的 tick；0.5.5 起不再按真实时间丢记录）。
pub const CUT_WAIT: usize = 30;
/// 灵体期间身体等在他的泉水里（0.5.7，[`body_at`]），灵体的放逐结束前这么多 tick 回到倒下的地方：倒下、死亡动作还在那里，
/// 回去时他还放逐着（看不见），画面上的位置有几帧跟过去也没人看见。
pub const BACK_EARLY: usize = 12;
/// `FALL` 数倒下的地方附近的敌方英雄（0.5.7）：这么近以内、每隔这么多 tick 数一次。
pub const NEAR_R: f64 = 60000.0;
pub const NEAR_EVERY: usize = 30;
/// 倒下的地方挂在他身上（0.5.7，buff `league_karthus_spot:<x>,<y>`，没有数值、没有画面）：身体在泉水里时，`shun` 让人退出亵渎圈
/// 要按倒下的地方算。
pub const SPOT_TAG: &str = "league_karthus_spot:";
/// 游戏 AI 认的泉水（0.5.7）：0.5.1 SDK 带符号的 game_core 里 `plan_legacy::old::battle::is_ignored_battle_enemy` 的范围，
/// 0.7.1 的 EXE 里同样的比较内联在一百多处。蓝方（队伍 0）在左下角：x < `WELL_NEAR` 且 `WELL_FAR` <= y < `MAP_END`，或者
/// x < `WELL_WIDE` 且 `WELL_DEEP` <= y < `MAP_END`；红方（队伍 1）在右上角，x、y 对调。
pub const WELL_NEAR: u64 = 64001;
pub const WELL_WIDE: u64 = 160001;
pub const WELL_FAR: u64 = 800000;
pub const WELL_DEEP: u64 = 896000;
pub const MAP_END: u64 = 960001;
// 0.4.0 只在化成灵体时放逐他 12 tick（`FLUSH_T`，正在打他、追他的单位丢了目标）、之后免控（`p_ward`）：游戏里只有放逐让单位
// 选不中（tfm2-hero-mod 的 champion-data「Invisible is not untargetable」），放逐完小兵、塔、英雄又打上来。0.5.0 整个灵体放逐。

pub mod life;

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

/// 倒下时剩的复活 tick `left` 扣掉灵体待了的 `spirit` tick，至少留 `BACK_MIN`（英雄联盟的死亡计时从化成灵体就开始）。
pub fn respawn_after_spirit(left: u64, spirit: u64) -> u64 {
    left.saturating_sub(spirit).max(BACK_MIN)
}

/// 游戏的 AI 是不是正在让他回城（league_graves 的写法）：下了回城命令，之后没有新命令时回城还在走，别的命令就停了。
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// 灵体第 `k` tick（共 `p_t`）该做什么（0.5.1）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stage {
    /// 放技能（`spirit_casts`）。
    Cast,
    /// 最后一 tick：`p_spirit`（不死、减伤）换成 `p_fall`，致命一击留到下一 tick（同一 tick 里刚摘掉的 buff 还算数）。
    LayDown,
    /// 时间到了：补致命一击，直到他真的倒下。
    Strike,
}

pub fn stage(k: usize, p_t: usize, laid_down: bool) -> Stage {
    if laid_down {
        Stage::Strike
    } else if k + 1 >= p_t {
        Stage::LayDown
    } else {
        Stage::Cast
    }
}

/// 灵体第 `k` tick 他的身体在哪（0.5.7，玩家反馈 2026-11-10：「死歌灵体后 AI 会在附近一直等着」）：放逐着的身体对游戏的 AI
/// 还是一个活着的敌方英雄，站在倒下的地方，周围的敌人围着等它（灵体期间几乎不对它下命令，`SHUN` 只出现在灵体开头和倒下那一刻），
/// 要等 7 秒他倒下才走。游戏的 AI 不管泉水里的敌人（[`in_well`]），所以身体等在自家泉水 `home`（出生点），放逐结束前
/// `BACK_EARLY` tick 回到倒下的地方 `spot`；不知道出生点就一直钉在倒下的地方（0.5.6 的做法）。灵体的画面和技能都在倒下的地方，
/// 不跟着身体走。
pub fn body_at(k: usize, p_t: usize, home: Option<(u64, u64)>, spot: (u64, u64)) -> (u64, u64) {
    match home {
        Some(h) if k + BACK_EARLY < p_t => h,
        _ => spot,
    }
}

/// 队伍 `team` 的英雄站在 `at` 是不是在游戏 AI 认的泉水里（[`WELL_NEAR`] 那几个范围）。
pub fn in_well(team: usize, at: (u64, u64)) -> bool {
    let (a, b) = if team == 0 { at } else { (at.1, at.0) };
    b < MAP_END && ((a < WELL_NEAR && b >= WELL_FAR) || (a < WELL_WIDE && b >= WELL_DEEP))
}

/// 倒下的地方挂在他身上的 buff 名（[`SPOT_TAG`]）。
pub fn spot_tag(spot: (u64, u64)) -> String {
    format!("{SPOT_TAG}{},{}", spot.0, spot.1)
}

/// 从 buff 名读回倒下的地方（不是这种 buff 就 None）。
pub fn parse_spot(buff: &str) -> Option<(u64, u64)> {
    let (x, y) = buff.strip_prefix(SPOT_TAG)?.split_once(',')?;
    Some((x.parse().ok()?, y.parse().ok()?))
}

/// 出生点（0.5.7，[`body_at`] 的 `home`）：出生时站的地方；读到 (0, 0)（还没摆上地图）就按队伍取游戏的泉水角落。
pub fn home_of(team: usize, spawned_at: (u64, u64)) -> (u64, u64) {
    if spawned_at != (0, 0) {
        spawned_at
    } else if team == 0 {
        (WELL_NEAR / 2, (WELL_DEEP + MAP_END) / 2)
    } else {
        ((WELL_DEEP + MAP_END) / 2, WELL_NEAR / 2)
    }
}

/// 灵体期间倒下的地方附近的敌方英雄（0.5.7，记进 `FALL`）：化成灵体时几个，之后每 `NEAR_EVERY` tick 数一次（几次、加起来几个），
/// 最后一次几个。
#[derive(Clone, Copy, Debug, Default)]
pub struct Near {
    pub at_rise: usize,
    pub samples: usize,
    pub sum: usize,
    pub last: usize,
    /// 身体不在该在的地方的 tick（[`body_at`]；身体搬过去之后：游戏要是把放逐着的单位按回原处，这里会接近整个灵体）。
    pub body_off: usize,
}

impl Near {
    pub fn add(&mut self, n: usize) {
        self.samples += 1;
        self.sum += n;
        self.last = n;
    }

    pub fn mean(&self) -> f64 {
        if self.samples == 0 { 0.0 } else { self.sum as f64 / self.samples as f64 }
    }
}

/// 每份模拟的编号（0.5.5，league_galio / league_brand 的做法）：被动第一次出生时抽一个，每次出生挂在他身上（buff
/// `league_karthus_sim:<编号>`，没有数值、没有画面；league.dll 的分叉校验不看带 `_sim:` 的 buff）。0.5.5 以为尸体身上的 buff
/// 留到复活、比赛钩子能从尸体上读回编号——那只是 SDK 里的事：游戏在阵亡时清掉 buff（league_nidalee、league_kayn_form 的画面
/// 也这么写），11-08 的日志里一次都没认出来。0.5.6 起编号也挂在建筑上（[`hang_tag`]：水晶，水晶不收时防御塔；league_eggs 的
/// 做法，它的 `EGGS sim #n` 说明预模拟里水晶留着 `_sim:` buff），记录带着这些建筑（`Cut::anchors`），比赛钩子认建筑上的编号。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
pub const SIM_TAG: &str = "league_karthus_sim:";
/// 编号挂不上（没有建筑收下）时隔这么多 tick 再挂；挂上了也每这么多 tick 看一眼还在不在（塔倒了、这份模拟从头再跑）（0.5.6）。
pub const ANCHOR_RETRY: usize = 60;

/// This add-on's tag of simulation `no`.
pub fn sim_tag(no: u64) -> String {
    format!("{SIM_TAG}{no}")
}

/// The number in a buff name of this add-on's tag (None: another buff).
pub fn parse_tag(buff: &str) -> Option<u64> {
    buff.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())
}

/// The simulation number on unit `id` - his living body, or his corpse in the SDK (the game clears a corpse's buffs) (0: none).
fn tag_of(sim: &StableSim<'_>, id: usize) -> u64 {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find_map(|b| parse_tag(b.name())).unwrap_or(0))
}

/// Unit `id` carries the buff `name` - the exact name (a nexus also carries league_eggs' `league_eggs_sim:<n>`).
fn carries(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| has_buff(&e, name))
}

/// Hangs `tag` on the living nexuses, or on the living towers when no nexus takes it (league_eggs' anchors, 0.5.6): the buildings
/// that carry it now (none: refused), which kind they are, and how many buildings stand (0 at tick 0: they come after it).
fn hang_tag(sim: &mut StableSim<'_>, tag: &str) -> (Vec<usize>, &'static str, usize) {
    let (mut nexus, mut towers) = (Vec::new(), Vec::new());
    for e in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|e| e.is_alive()) {
        match kind_of(&e) {
            Some(EntityKindV1::Nexus) => nexus.push(e.id()),
            Some(EntityKindV1::Tower) => towers.push(e.id()),
            _ => {}
        }
    }
    let stand = nexus.len() + towers.len();
    for (group, what) in [(nexus, "nexus"), (towers, "towers")] {
        for &a in &group {
            // once on each (hung again when a run starts over)
            sim.entity_remove_buff(a, tag);
            sim.add_buff(a, &BuffV1::named(tag));
        }
        let took: Vec<usize> = group.into_iter().filter(|&a| carries(sim, a, tag)).collect();
        if !took.is_empty() {
            return (took, what, stand);
        }
    }
    (Vec::new(), "", stand)
}

/// 一次灵体倒下后要扣的复活时间：哪份模拟（[`SIM_TAG`] 的编号）、他的身体（阵亡后是尸体；SDK 里编号在上面，游戏里不在）、
/// 挂着这份模拟编号的建筑（0.5.6）、哪个玩家、阵亡的 tick、灵体待了多少 tick；他该复活的 tick（`back_tick`，这份模拟第一次
/// 看到他登记成阵亡时算出）；日志行头，记过没有。
///
/// 0.5.5（2026-11-06）：每份模拟一条、只由这份模拟扣和删。0.5.2-0.5.4 按「哪一局」（种类、比赛、小局）配：服务器的预模拟没有
/// 局号（s=-），同一场比赛不同小局的预模拟共用记录（另一局里同一个玩家碰巧阵亡就被扣），同一局并排的两份预演、画面的两遍也共用
/// 一条（谁先看到谁定 `back`）；记录按真实时间放 30 秒就丢（暂停、卡顿久了，没扣的那份就不扣了）。
#[derive(Clone, Debug)]
struct Cut {
    sim: u64,
    body: usize,
    /// the buildings carrying this simulation's number when he died (0.5.6: the game clears his corpse's buffs)
    anchors: Vec<usize>,
    player: usize,
    at: usize,
    spent: u64,
    back: Option<usize>,
    line: String,
    told: bool,
}

/// 被动在他阵亡时（`on_dead`）记下，游戏登记好阵亡以后由 `cut_respawns` 扣。游戏在 `on_dead` 之后才把他记成阵亡，那之后他
/// 自己的钩子都不跑了：扣的是本包的比赛钩子（`Respawns`，每局每 tick，0.5.2）；他阵亡后被动若还被叫到也扣一下。
/// 一条记录由它那份模拟删：扣过、他该复活了（`note_open` 关了），或者他复活（`on_spawn`）、再阵亡（新的一条换掉旧的）；比赛在他
/// 阵亡期间打完的那几条留着，超过 [`CUTS_MOST`] 条丢最早的。
static CUTS: Mutex<Vec<Cut>> = Mutex::new(Vec::new());
static CUTS_N: AtomicUsize = AtomicUsize::new(0);
/// 最多留这么多条（正在用的几条都是刚记的；多出来的是打完的比赛里的）。
pub const CUTS_MOST: usize = 256;

/// A note `c` is this simulation's: a building it names carries the note's number, the exact tag (0.5.6; another simulation's
/// building with the same entity id carries its own number, or none) - or, in the SDK, where a corpse keeps its buffs, the body
/// it is about does (0.5.5 went by that alone, and in the game never owned a note: the corpse's buffs are cleared at death).
fn owns(sim: &StableSim<'_>, c: &Cut) -> bool {
    if c.sim == 0 {
        return false;
    }
    let tag = sim_tag(c.sim);
    c.anchors.iter().any(|&a| carries(sim, a, &tag)) || tag_of(sim, c.body) == c.sim
}

/// The note of `sim`'s Karthus of `player` goes into `cuts` (the one of his last death, if still there, gives way); past
/// [`CUTS_MOST`] the oldest note goes.
fn add_cut(cuts: &mut Vec<Cut>, cut: Cut) {
    cuts.retain(|c| !(c.sim == cut.sim && c.player == cut.player));
    cuts.push(cut);
    if cuts.len() > CUTS_MOST {
        cuts.remove(0);
    }
}

/// The note of simulation `sim` and `player`, taken off (his respawn: that death is over).
fn take_cut(cuts: &mut Vec<Cut>, sim: u64, player: usize) -> Option<Cut> {
    let i = cuts.iter().position(|c| c.sim == sim && c.player == player)?;
    Some(cuts.remove(i))
}

/// 他该复活的 tick：第一次看到他阵亡（`now`，复活倒计时还剩 `left`）时，倒计时扣掉灵体待的 `spent`（`respawn_after_spirit`）。
pub fn back_tick(now: usize, left: u64, spent: u64) -> usize {
    now + respawn_after_spirit(left, spent) as usize
}

/// 第一次看到他阵亡时他该复活的 tick（`back_tick`）；游戏还没设复活倒计时（`left` 为 0）就再等一 tick，不拿 0 去算（0.5.3）。
pub fn first_back(now: usize, left: u64, spent: u64) -> Option<usize> {
    (left > 0).then(|| back_tick(now, left, spent))
}

/// 一条记录在 `now` 这一 tick 还管不管用（0.5.3）：只管记它的那一次阵亡——阵亡后 `CUT_WAIT` tick 内第一次看到他阵亡时扣，之后扣到
/// `back`（那时他已经复活，再死是另一条记录的事）。0.5.2 的记录按真实时间放 30 秒：预演几秒就跑完上万 tick、你看的那局快进时
/// 也一样，他这期间再死一次，旧记录的 `back` 早过了，新的复活倒计时被扣成 1 tick——灵体倒下后秒复活（用户 2026-11-04：
/// 「死歌灵体死了后秒复活？」；11-04 的日志 40 条 `RESPAWN` 里 18 条是 `2400 -> 1 ticks`，都是阵亡一两万 tick 之后扣的）。
pub fn note_open(at: usize, back: Option<usize>, now: usize) -> bool {
    match back {
        None => now <= at + CUT_WAIT,
        Some(b) => now < b,
    }
}

/// 这一 tick 把剩余复活 tick 改成多少：不晚于 `back`；已经不晚于它就不改（同一局的另一份预演扣过，或这份上一 tick 扣过）。
pub fn cut_to(back: usize, now: usize, left: u64) -> Option<u64> {
    let want = back.saturating_sub(now).max(1) as u64;
    (want < left).then_some(want)
}

/// What a match tick does with a note.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Step {
    /// Another simulation's note, or nothing to do this tick.
    Skip,
    /// This simulation's note, done by its own clock: it goes.
    Drop,
    /// Cut the respawn to `want` ticks (`left` were left).
    Cut { want: u64, left: u64 },
}

/// What a match tick at `now` does with note `c`: `mine` says whether it is this simulation's (asked only when it matters: it
/// reads the buildings), `dead_left` the player's respawn ticks left when he is dead in this simulation (None: alive, no such
/// player). The first tick this simulation sees him dead sets the note's `back`.
fn step(c: &mut Cut, now: usize, mine: &dyn Fn(&Cut) -> bool, dead_left: &dyn Fn() -> Option<u64>) -> Step {
    if now < c.at {
        return Step::Skip;
    }
    if !note_open(c.at, c.back, now) {
        return if mine(c) { Step::Drop } else { Step::Skip };
    }
    let Some(left) = dead_left() else { return Step::Skip };
    if !mine(c) {
        return Step::Skip;
    }
    let back = match c.back {
        Some(b) => b,
        None => match first_back(now, left, c.spent) {
            Some(b) => *c.back.insert(b),
            None => return Step::Skip,
        },
    };
    cut_to(back, now, left).map_or(Step::Skip, |want| Step::Cut { want, left })
}

/// 扣这份模拟里到了的复活时间。每局每 tick 都叫：没有记录时一读就走。只碰这份模拟自己的记录（[`owns`]：建筑上的编号，
/// 0.5.6），关了的（`note_open`，按这份模拟的 tick）就删。
fn cut_respawns(sim: &StableSim<'_>) {
    if CUTS_N.load(Ordering::Relaxed) == 0 {
        return;
    }
    let now = sim.tick();
    let mut lines = Vec::new();
    {
        let mut cuts = CUTS.lock().unwrap_or_else(|e| e.into_inner());
        let mut i = 0;
        while i < cuts.len() {
            let player = cuts[i].player;
            // the player first (one call): the number on the buildings is read only when he is dead here or the note is done
            let dead_left = || sim.get_player(player).filter(|p| !p.is_alive()).map(|p| p.respawn_time() as u64);
            match step(&mut cuts[i], now, &|c| owns(sim, c), &dead_left) {
                Step::Skip => i += 1,
                Step::Drop => {
                    // its death is over (cut, and he is back by `back`) or he was never seen dead in time: a later death of
                    // his is another note's
                    let c = cuts.remove(i);
                    if c.back.is_none() && !c.told {
                        lines.push(format!("{} RESPAWN NOT CUT (not seen dead within {CUT_WAIT} ticks of his death)", c.line));
                    }
                }
                Step::Cut { want, left } => {
                    let c = &mut cuts[i];
                    i += 1;
                    let res = life::shorten_respawn(sim, c.player, want);
                    if !c.told {
                        c.told = true;
                        lines.push(match res {
                            Ok((was, to)) => format!("{} RESPAWN: {was} -> {to} ticks (the spirit's {} counted, {} ticks after \
                                                      his death)", c.line, c.spent, now - c.at),
                            Err(why) => format!("{} RESPAWN NOT CUT ({why}): {left} ticks left, the spirit's {} not counted",
                                                c.line, c.spent),
                        });
                    }
                }
            }
        }
        CUTS_N.store(cuts.len(), Ordering::Relaxed);
    }
    for l in lines {
        if let Some(k) = counted("respawn") {
            wlog(format!("{l} #{k}"));
        }
    }
}

/// 灵体挨的打（倒下时记日志，看钩子 `shun` 管不管用）：谁打的。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Hits {
    pub champions: usize,
    pub minions: usize,
    pub towers: usize,
    pub others: usize,
}

impl Hits {
    pub fn add(&mut self, kind: Option<EntityKindV1>) {
        match kind {
            Some(EntityKindV1::Champion) => self.champions += 1,
            Some(EntityKindV1::Minion) => self.minions += 1,
            Some(EntityKindV1::Tower) => self.towers += 1,
            _ => self.others += 1,
        }
    }
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

/// The player whose champion `id` is (None: a tower, a minion, a monster).
fn player_of(sim: &StableSim<'_>, id: usize) -> Option<usize> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find(|p| p.champion().is_some_and(|c| c.id() == id)).map(|p| p.id())
}

/// 灵体倒下时算谁的击杀：最后打他的还在就是他；他在灵体期间死了又复活（新的实体），算他玩家现在的英雄；都没有就算最近的
/// 活着的敌方英雄——从不算卡尔萨斯自己（0.4.2，league_sion 一样的毛病：11-02 的日志里赛恩 1/6 的倒下算成了自杀）。
fn killer(sim: &StableSim<'_>, me: usize, last: Option<usize>, player: Option<usize>) -> usize {
    if let Some(a) = last.filter(|&a| sim.get_entity(a).is_some()) {
        return a;
    }
    if let Some(c) = player.and_then(|p| sim.get_player(p)).and_then(|p| p.champion()).filter(|c| c.is_alive()) {
        return c.id();
    }
    let Some(e) = sim.get_entity(me) else { return me };
    let (team, here) = (e.team(), e.pos());
    let d2 = |p: (u64, u64)| (p.0 as f64 - here.0 as f64).powi(2) + (p.1 as f64 - here.1 as f64).powi(2);
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_champion() && u.is_alive())
        .min_by(|a, b| d2(a.pos()).total_cmp(&d2(b.pos())))
        .map_or(me, |u| u.id())
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

/// 灵体的 buff（副本里绑着灵体的画面）：不死、不受伤害、不能走动（英雄联盟的灵体站在原地放技能）。
fn spirit_buff(t: usize) -> BuffV1 {
    let mut s = BuffV1::timed(&sn("p_spirit"), t);
    s.undying = true;
    s.damaged_reduce = 100;
    s.move_speed_mult = -100;
    s
}

/// 倒下前的 buff（0.5.1，灵体最后一 tick 换上，到他真倒下为止）：不死、减伤都没有，照样不能走；`spirit_on` 认它（谁都不选他，
/// `spirit_ai` 不让他下命令）。
fn fall_buff(t: usize) -> BuffV1 {
    let mut s = BuffV1::timed(&sn("p_fall"), t);
    s.move_speed_mult = -100;
    s
}

/// 倒下（0.5.1）：灵体最后一 tick（换下不死的那一 tick），补了几下、最近一下算谁的，血设成 0 了没有。
#[derive(Clone, Default)]
struct Falling {
    since: usize,
    tries: usize,
    killer: Option<usize>,
    forced: bool,
}

/// 灵体由本包放的技能（他放逐着自己出不了手）：倒下的地方（技能和灵体的画面都在这里，0.5.7 起身体不在），下一次荒芜、亵渎、
/// 亵渎圈画面的 tick，落下的荒芜（位置、炸开的 tick），立着的痛苦之墙（位置、倒下的 tick），安魂曲打下来的 tick，这个灵体放过
/// 安魂曲没有，放了些什么。
#[derive(Clone, Default)]
struct Cast {
    anchor: (u64, u64),
    q_next: usize,
    e_next: usize,
    ring_next: usize,
    booms: Vec<((u64, u64), usize)>,
    walls: Vec<((u64, u64), usize)>,
    requiem: Option<usize>,
    r_used: bool,
    tally: Tally,
}

/// 一个灵体放了什么（0.5.1，倒下时记进 `FALL`）：荒芜几次、炸到几个，痛苦之墙几面、墙碰到几次，亵渎烫到几次，安魂曲几次。
#[derive(Clone, Copy, Debug, Default)]
struct Tally {
    q: usize,
    q_hits: usize,
    w: usize,
    w_hits: usize,
    e_hits: usize,
    r: usize,
    /// re-banished (targetable again mid-spirit), every try (0.5.5)
    rebanish: usize,
}

/// 单位（中心 `at`、半径 `r`）碰到立在 `wall` 的痛苦之墙没有（0.5.1）：墙是 `W_HW` 宽、`W_HH` 高的竖直长方形（游戏的 `Rect`：
/// 宽高是整个的，外面再加单位自己的半径，champion-data）。
pub fn in_wall(at: (u64, u64), r: u64, wall: (u64, u64)) -> bool {
    at.0.abs_diff(wall.0) <= W_HW / 2 + r && at.1.abs_diff(wall.1) <= W_HH / 2 + r
}

/// 灵体的画面面朝哪边（效果图不会镜像，左右各画一张）：最近的敌方英雄在右边（或没有）就朝右。
pub fn side(me_x: u64, foe_x: Option<u64>) -> &'static str {
    match foe_x {
        Some(x) if x < me_x => "l",
        _ => "r",
    }
}

/// 单位的种类（读不到时按英雄、小兵、塔的判断）。
fn kind_of(e: &StableEntity<'_, '_>) -> Option<EntityKindV1> {
    e.kind().or_else(|| {
        if e.is_champion() {
            Some(EntityKindV1::Champion)
        } else if e.is_minion() {
            Some(EntityKindV1::Minion)
        } else if e.is_tower() {
            Some(EntityKindV1::Tower)
        } else {
            None
        }
    })
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
    /// 最后一个打他的英雄的玩家：那个英雄在灵体期间死了又复活（新的实体），击杀算他的新英雄（`killer`）。
    last_player: Option<usize>,
    next_guard: usize,
    /// 这条命里见过他 1 血以上：游戏 0.6.4 开局第 0 tick 读到的血量是 0，那不是致命伤（赛恩附加包的教训）。
    alive_seen: bool,
    /// 这次灵体挨的打。
    hits: Hits,
    /// 灵体由本包放的技能。
    cast: Cast,
    /// 这条命化成灵体的 tick（阵亡时扣复活时间用，到 `on_dead` / 复活为止）。
    rose_at: Option<usize>,
    /// 倒下：灵体的最后一 tick 起到他真倒下（None = 还没到）。
    fall: Option<Falling>,
    /// 上一次重新放逐的 tick：下一 tick 又要重新放逐（放逐没成，比如他免控）算同一串，一串只记一行（0.5.5）。
    rebanished: Option<usize>,
    /// 这份模拟的编号（[`SIM_TAG`]），第一次出生时抽（0.5.5）。
    sim: u64,
    /// 挂着这份模拟编号的建筑（0.5.6，`keep_anchored`）：开局第 1 tick 起挂，复活时不清（建筑整局都在）。
    anchored: Vec<usize>,
    /// 挂不上时这一 tick 前不再挂（隔 `ANCHOR_RETRY` tick）。
    anchor_next: usize,
    /// `ANCHOR REFUSED` 记过了（每份模拟一行）。
    anchor_told: bool,
    /// 出生点（0.5.7，[`home_of`]）：灵体期间身体等在这里（[`body_at`]）。
    home: Option<(u64, u64)>,
    /// 这次灵体期间倒下的地方附近的敌方英雄（0.5.7，记进 `FALL`）。
    near: Near,
}

/// A try to re-banish at `now` after the last one at `last`: the same run when it is the very next tick (the banish did not
/// take - a cc-immune spirit refuses it: 11-06, `REBANISH #1..#6` on ticks 28699-28704).
pub fn rebanish_run(last: Option<usize>, now: usize) -> bool {
    last.is_some_and(|t| now == t + 1)
}

/// What `on_damaged` reports while he is a spirit: not his own fall blow (0.5.5: `strike` deals hp + 1000 credited to the
/// last hitter, and every blow showed up as `SPIRIT HIT ... (1000+ damage)` and one more champion hit in `FALL`).
pub fn spirit_hit_counts(fall_tries: Option<usize>) -> bool {
    fall_tries.is_none_or(|n| n == 0)
}

impl DeathDefied {
    /// 这份模拟的编号挂在建筑上（0.5.6）：游戏清掉尸体的 buff，比赛钩子按记录里的建筑认记录（[`owns`]）。他活着时从第 1 tick
    /// 起挂（第 0 tick 还没有建筑，开局一会儿还没有就下一 tick 再找）；建筑都不收就每 `ANCHOR_RETRY` tick 再挂，
    /// `ANCHOR REFUSED` 只记一行。挂上了也每 `ANCHOR_RETRY` tick 看一眼：一个都不带了（塔倒了、这份模拟从头再跑）就重挂。
    fn keep_anchored(&mut self, sim: &mut StableSim<'_>, now: usize) {
        if self.sim == 0 || now == 0 {
            return;
        }
        let tag = if !self.anchored.is_empty() {
            if !now.is_multiple_of(ANCHOR_RETRY) {
                return;
            }
            let tag = sim_tag(self.sim);
            if self.anchored.iter().any(|&a| carries(sim, a, &tag)) {
                return;
            }
            tag
        } else if now < self.anchor_next {
            return;
        } else {
            sim_tag(self.sim)
        };
        let lost = std::mem::take(&mut self.anchored);
        let (took, what, stand) = hang_tag(sim, &tag);
        self.anchored = took;
        if !self.anchored.is_empty() {
            if let Some(k) = counted("anchor") {
                wlog(format!("{} ANCHOR #{k}: sim #{} hung on {what} {:?} (of {stand} buildings standing){}", head(sim, self.me),
                             self.sim, self.anchored,
                             if lost.is_empty() { String::new() } else { format!(" - again: none of {lost:?} carried it") }));
            }
        } else if stand > 0 || now >= ANCHOR_RETRY {
            self.anchor_next = now + ANCHOR_RETRY;
            if !self.anchor_told {
                self.anchor_told = true;
                if let Some(k) = counted("anchor_refused") {
                    wlog(format!("{} ANCHOR REFUSED #{k}: {} - sim #{}'s respawn cuts wait for it, tried again every \
                                  {ANCHOR_RETRY} ticks", head(sim, self.me),
                                 if stand == 0 { "no nexus or tower stands".to_string() }
                                 else { format!("none of {stand} nexus / towers took {tag}") }, self.sim));
                }
            }
        }
    }

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
        self.hits = Hits::default();
        sim.entity_remove_buff(me, &sn("p_guard"));
        let Some((pos, team)) = sim.get_entity(me).map(|e| (e.pos(), e.team())) else { return };
        let nearest = foes_by_distance(sim, team, (pos.0 as f64, pos.1 as f64)).first().and_then(|f| sim.get_entity(f.0));
        let face = side(pos.0, nearest.map(|e| e.pos().0));
        // the whole spirit banished (0.5.0): untargetable for everyone, no health bar, rooted, recall-proof - before anything
        // cc_immune, which it refuses. 0.5.1: it ends with the spirit's time (it was p_t + 2), so the strike after it finds
        // him targetable. 0.5.7: no lock picture - it goes where his body goes, and the body waits in his well (`body_at`);
        // his ghost is a picture of its own where he fell (one 7.68 s play of the tag, longer than the spirit, as the lock
        // picture was)
        let banished = sim.entity_banish(me, me, self.p.p_t, "", "");
        sim.play_view_effect(&sn(&format!("p_ghost_{face}")), me, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
        sim.add_buff(me, &spirit_buff(self.p.p_t + 2));
        // where he fell, for `shun` (an older one first: a revive mid-spirit keeps his buffs)
        for old in buffs(sim, me).iter().map(|b| b.name().to_string()).filter(|b| parse_spot(b).is_some()) {
            sim.entity_remove_buff(me, &old);
        }
        sim.add_buff(me, &BuffV1::named(&spot_tag(pos)));
        self.cast = Cast { anchor: pos, q_next: now + 1, e_next: now + 1, ..Cast::default() };
        self.rose_at = Some(now);
        self.fall = None;
        self.rebanished = None;
        let spot = (pos.0 as f64, pos.1 as f64);
        self.near = Near { at_rise: foes_near(sim, team, spot, NEAR_R, false).0.len(), ..Near::default() };
        sim.play_sfx(&sn("p"), me, &InputTargetV1::target(me));
        sim.play_sfx(&sn("vo_p"), me, &InputTargetV1::target(me));
        let body = body_at(0, self.p.p_t, self.home, pos);
        let moved = body != pos && sim.entity_set_pos(me, body.0, body.1);
        if let Some(k) = counted("spirit") {
            wlog(format!("{} SPIRIT #{k}: lethal damage caught at 1 hp (last hit by {}), a spirit for {} ticks{}{}", head(sim, me),
                         self.last_hit.map_or_else(|| "-".to_string(), |a| who(sim, a)), self.p.p_t,
                         if banished { format!(", banished with his ghost facing {face}") }
                         else { " - entity_banish refused: he stays targetable".to_string() },
                         if moved { format!("; his body waits in his well {body:?}, {} foes within {NEAR_R} of where he fell",
                                            self.near.at_rise) }
                         else if body != pos { format!(" - entity_set_pos refused: his body stays at {pos:?}") }
                         else { String::new() }));
        }
    }

    /// 灵体放的技能（他放逐着出不了手，`Cast`）：亵渎一直烧，荒芜落在最近的敌人脚下，痛苦之墙立在最近的敌方英雄身上，安魂曲在
    /// 值得时引导。数字、画面照主包。挑目标用灵体自己的眼睛（0.5.1，用户 2026-11-03：「灵体状态下会放其他技能吗 我怎么感觉不会
    /// 放」）：放逐的单位不给队伍视野（champion-data），0.5.0 的灵体只挑他队伍看得见的，身边没队友时荒芜、亵渎什么都打不到。
    fn spirit_casts(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, k: usize) {
        let Some((team, power, r_ready, w_ready)) = sim.get_entity(me).map(|e| {
            (e.team(), e.stat().magic_power.max(0) as usize, ready(&e, SkillSlotV1::Ult), !has_buff(&e, &sn("w_cd")))
        }) else {
            return;
        };
        let at = self.cast.anchor;
        let here = (at.0 as f64, at.1 as f64);
        let here_t = InputTargetV1::pos(at.0, at.1);
        // E Defile, burning the whole spirit (League's spirit keeps it on, free)
        if now >= self.cast.e_next {
            self.cast.e_next = now + E_PER;
            let (champs, others) = foes_near(sim, team, here, E_R, false);
            for id in champs.iter().chain(&others).map(|f| f.0) {
                sim.deal_damage_typed(me, id, e_damage(power), DamageTypeV1::Ap, AttackTypeV1::Skill);
                sim.play_view_effect(&sn("e_hit"), me, &InputTargetV1::target(id), 0, 0, 0);
                self.cast.tally.e_hits += 1;
            }
            if now >= self.cast.ring_next {
                self.cast.ring_next = now + E_RING_EVERY;
                sim.play_view_effect(&sn("e_ring"), me, &here_t, 0, 0, 0);
            }
        }
        // Q Lay Waste: the blasts that fall now, then a new one
        let (due, keep): (Vec<_>, Vec<_>) = std::mem::take(&mut self.cast.booms).into_iter().partition(|b| b.1 <= now);
        self.cast.booms = keep;
        for (spot, _) in due {
            let (champs, others) = foes_near(sim, team, (spot.0 as f64, spot.1 as f64), Q_R, false);
            let hit: Vec<usize> = champs.iter().chain(&others).map(|f| f.0).collect();
            let dmg = q_damage(power, hit.len());
            for &id in &hit {
                sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                let view = if hit.len() == 1 { "q_lone" } else { "q_hit" };
                sim.play_view_effect(&sn(view), me, &InputTargetV1::target(id), 0, 0, 0);
            }
            self.cast.tally.q_hits += hit.len();
            sim.play_view_effect(&sn("q_boom"), me, &InputTargetV1::pos(spot.0, spot.1), 0, 0, 0);
            sim.play_sfx(&sn("q_boom"), me, &InputTargetV1::pos(spot.0, spot.1));
        }
        if now >= self.cast.q_next {
            let (champs, others) = foes_near(sim, team, here, Q_RANGE, false);
            if let Some(spot) = champs.first().or(others.first()).and_then(|f| sim.get_entity(f.0)).map(|e| e.pos()) {
                self.cast.q_next = now + Q_CD;
                self.cast.booms.push((spot, now + Q_DELAY));
                self.cast.tally.q += 1;
                sim.play_view_effect(&sn("q_mark"), me, &InputTargetV1::pos(spot.0, spot.1), 0, 0, 0);
                sim.play_sfx(&sn("q"), me, &here_t);
            }
        }
        // W Wall of Pain (0.5.1): the kit has it ride his attack, which the spirit has not, so it never went up. When his W is
        // ready (no `w_cd` flag), on the nearest enemy champion within W_R; the wall stands W_T ticks and every W_EVERY ticks
        // slows the enemies touching it W_SLOW% (W_SLOW_T) and cuts their magic resistance W_MR% (W_MR_T), as the kit's zone
        if w_ready && k + W_LATE < self.p.p_t {
            let (champs, _) = foes_near(sim, team, here, W_R, false);
            if let Some(spot) = champs.first().and_then(|f| sim.get_entity(f.0)).map(|e| e.pos()) {
                sim.add_buff(me, &BuffV1::timed(&sn("w_cd"), W_CD));
                self.cast.walls.push((spot, now + W_T));
                self.cast.tally.w += 1;
                sim.play_view_effect(&sn("w_wall"), me, &InputTargetV1::pos(spot.0, spot.1), 0, 0, 0);
                sim.play_sfx(&sn("w"), me, &InputTargetV1::pos(spot.0, spot.1));
            }
        }
        self.cast.walls.retain(|w| w.1 > now);
        if !self.cast.walls.is_empty() && now % W_EVERY == 0 {
            let walls = self.cast.walls.clone();
            let touched: Vec<usize> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower()
                    && kind_of(u) != Some(EntityKindV1::Nexus) && !spirit_on(u))
                .filter(|u| walls.iter().any(|w| in_wall(u.pos(), u.radius() as u64, w.0)))
                .map(|u| u.id())
                .collect();
            let mut slow = BuffV1::timed(&sn("w_slow"), W_SLOW_T);
            slow.move_speed_mult = -W_SLOW;
            let mut shred = BuffV1::timed(&sn("w_shred"), W_MR_T);
            shred.magic_resistance_mult = -W_MR;
            for id in touched {
                sim.entity_stack_buff(id, &slow, 1, true);
                sim.entity_stack_buff(id, &shred, 1, true);
                self.cast.tally.w_hits += 1;
            }
        }
        // R Requiem: one channel a spirit, when it is worth it and there is time to finish it
        match self.cast.requiem {
            Some(t) if now >= t => {
                self.cast.requiem = None;
                let foes = foes_by_distance(sim, team, here);
                for &(id, _) in &foes {
                    sim.deal_damage_typed(me, id, R_DMG + power * R_RATIO / 100, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    sim.play_view_effect(&sn("r_hit"), me, &InputTargetV1::target(id), 0, 0, 0);
                }
                sim.play_sfx(&sn("r_boom"), me, &here_t);
                if let Some(c) = counted("spirit_r_hit") {
                    wlog(format!("{} SPIRIT REQUIEM #{c}: {} enemy champions struck", head(sim, me), foes.len()));
                }
            }
            None if r_ready && !self.cast.r_used && r_in_time(k, self.p.p_t) => {
                let toll = foes_toll(sim, team, power);
                let hits: Vec<(usize, usize, usize)> = toll.iter().map(|f| (f.1, f.2, f.3)).collect();
                if r_worth(RWhen::Spirit, &hits, power) {
                    self.cast.r_used = true;
                    self.cast.tally.r += 1;
                    self.cast.requiem = Some(now + R_CH);
                    for &(id, ..) in &toll {
                        sim.add_buff(id, &BuffV1::timed(&sn("r_mark"), R_CH));
                    }
                    // seen by spirit_ai, which holds the game's AI's Requiem for R_CD after he is back
                    sim.add_buff(me, &BuffV1::timed(&sn("r_used"), self.p.p_t + 2));
                    sim.play_view_effect(&sn("r_cast"), me, &here_t, 0, 0, 0);
                    sim.play_sfx(&sn("r"), me, &here_t);
                    sim.play_sfx(&sn("vo_r"), me, &here_t);
                    if let Some(c) = counted("spirit_r") {
                        let (kills, low) = r_toll(&hits, power, SPIRIT_LOW);
                        wlog(format!("{} SPIRIT REQUIEM #{c}: channelling {R_CH} ticks - {kills} would die, {low} left under \
                                      {SPIRIT_LOW}%", head(sim, me)));
                    }
                }
            }
            _ => {}
        }
    }

    /// 灵体中途又能被选中了（0.5.1：韧性缩短了放逐，游戏 0.6.5 起放逐吃韧性）：照灵体剩下的时间重新放逐（league_mordekaiser
    /// 的做法）。0.5.7 起不带锁定画面：灵体的画面在倒下的地方接着放（`rise`），身体在泉水里。
    fn rebanish(&mut self, sim: &mut StableSim<'_>, me: usize, k: usize) {
        let left = self.p.p_t.saturating_sub(k);
        let ok = sim.entity_banish(me, me, left, "", "");
        let now = sim.tick();
        self.cast.tally.rebanish += 1;
        // one line a run: targetable again the very next tick means the banish did not take (0.5.5; the tries in FALL)
        let run = rebanish_run(self.rebanished, now);
        self.rebanished = Some(now);
        if run {
            return;
        }
        if let Some(c) = counted("rebanish") {
            wlog(format!("{} REBANISH #{c}: targetable again {k} ticks into the spirit - banished for the last {left}{}",
                         head(sim, me), if ok { "" } else { " (entity_banish refused)" }));
        }
    }

    /// 灵体最后一 tick（0.5.1）：摘掉灵体的不死、减伤（`p_spirit`）和「不死」，换上 `p_fall`（照样钉住、谁都不选，他也不下命令，
    /// 只是不再保命）。致命一击留到下一 tick：同一 tick 里刚摘掉的 buff 还算数，0.4.x、0.5.0 在这里直接补的那一下只打出 1 点。
    fn lay_down(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        self.cast.booms.clear();
        sim.entity_remove_buff(me, &sn("p_spirit"));
        sim.entity_remove_buff(me, &sn("p_guard"));
        sim.add_buff(me, &fall_buff(FALL_SLACK));
        self.fall = Some(Falling { since: now, ..Falling::default() });
    }

    /// 补致命一击（0.5.1）：他还放逐着（灵体的放逐在时间到时结束；别人的放逐）就最多等 `FALL_WAIT` tick；清掉护盾，打
    /// `hp + 1000` 真实伤害，击杀算最后打他的人。伤害在这一 tick 结算时才扣（league_pyke 的处决也是），他倒下时 `on_dead` 记
    /// `FALL`；下一 tick 他还站着就是没打死，再补一下（`FALL RETRY`），补了 `FALL_SLACK` tick 还不行就把血设成 0
    /// （`FALL FORCED`）。`p_fall` 一直续着：倒下前他什么命令都不下。
    fn strike(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let Some(mut f) = self.fall.clone() else { return };
        let Some((targetable, hp)) = sim.get_entity(me).map(|e| (e.is_targetable(), e.hp().0)) else { return };
        let waited = now.saturating_sub(f.since);
        if f.tries == 0 && !targetable && waited <= FALL_WAIT {
            return;
        }
        if f.tries > 0 {
            // the last blow did not take him (it would have been settled by now): he stays a dead man until one does
            sim.entity_remove_buff(me, &sn("p_fall"));
            sim.add_buff(me, &fall_buff(FALL_SLACK));
            let undying: Vec<String> = buffs(sim, me).iter().filter(|b| b.undying).map(|b| b.name().to_string()).collect();
            let by = f.killer.map_or_else(|| "-".to_string(), |a| who(sim, a));
            if waited >= FALL_SLACK && !f.forced {
                f.forced = true;
                let set = sim.entity_set_hp(me, 0);
                if let Some(k) = counted("fall_forced") {
                    wlog(format!("{} FALL FORCED #{k}: {} blows by {by} left him at {hp} hp in {waited} ticks (targetable \
                                  {targetable}, undying {undying:?}) - hp set to 0{}", head(sim, me), f.tries,
                                 if set { "" } else { " (entity_set_hp refused)" }));
                }
            } else if let Some(k) = counted("fall_retry") {
                wlog(format!("{} FALL RETRY #{k}: blow {} by {by} did not take him - {hp} hp, targetable {targetable}, \
                              undying {undying:?}", head(sim, me), f.tries));
            }
        }
        sim.entity_clear_shield(me);
        let killer = killer(sim, me, self.last_hit, self.last_player);
        f.tries += 1;
        f.killer = Some(killer);
        // noted before the blow: should the game settle it inside the call, `on_dead` logs the fall from this
        self.fall = Some(f);
        if !sim.deal_damage_typed(killer, me, hp + 1000, DamageTypeV1::Fixed, AttackTypeV1::Skill) {
            if let Some(k) = counted("fall_refused") {
                wlog(format!("{} FALL BLOW REFUSED #{k}: deal_damage_typed by {} (targetable {targetable})", head(sim, me),
                             who(sim, killer)));
            }
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
        self.last_player = None;
        self.next_guard = 0;
        self.alive_seen = false;
        self.hits = Hits::default();
        self.cast = Cast::default();
        self.rose_at = None;
        self.fall = None;
        self.rebanished = None;
        // this simulation's number, on him every life (a respawn is a new entity); the game clears it off his corpse, so the
        // match hook goes by the buildings carrying it (`keep_anchored`, 0.5.6; `anchored` stays: they stand all match)
        if self.sim == 0 {
            self.sim = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = sim_tag(self.sim);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        // back: the note of his last death is done with (one no match tick of this simulation ever claimed is said, with what
        // the match hook had to go by: the corpse, the buildings still carrying the number)
        let left = take_cut(&mut CUTS.lock().unwrap_or_else(|e| e.into_inner()), self.sim, player);
        if let Some(c) = left.filter(|c| c.back.is_none() && !c.told) {
            if let Some(k) = counted("respawn") {
                let corpse = sim.get_entity(c.body).map_or_else(|| "gone".to_string(), |e| format!("with {} buffs", e.buff_count()));
                let carry = c.anchors.iter().filter(|&&a| carries(sim, a, &tag)).count();
                wlog(format!("{} RESPAWN NOT CUT (no match tick found this simulation's number: corpse #{} {corpse}, {carry} of \
                              the buildings {:?} carry it) #{k}", c.line, c.body, c.anchors));
            }
        }
        let (team, spawned_at) = sim.get_entity(me).map_or((0, (0, 0)), |e| (e.team(), e.pos()));
        // where his body waits while he is a spirit (0.5.7): the spawn point, his well
        let home = home_of(team, spawned_at);
        self.home = Some(home);
        self.near = Near::default();
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Karthus (player {player}, team {team}, sim #{}), {:?}, home {home:?}{}",
                         head(sim, me), self.sim, self.p,
                         if in_well(team, home) { " (the game's well)" } else { " - NOT in the box the game's AI takes for the well" }));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            // dead, should the game still run his passive: his respawn cut, as the match hook makes it
            cut_respawns(sim);
            return;
        }
        let (hp, _) = e.hp();
        let pos = e.pos();
        let team = e.team();
        let targetable = e.is_targetable();
        let now = sim.tick();
        self.keep_anchored(sim, now);
        if let Some(t0) = self.spirit {
            let k = now.saturating_sub(t0);
            // a dead man does not walk: his body waits in his well, back where he fell for the fall (0.5.7, `body_at`; the
            // spirit stands and casts there, League's)
            let want = body_at(k, self.p.p_t, self.home, self.cast.anchor);
            if pos != want {
                // moved there on the tick before (the rise, or the way back): the game put him back
                if k >= 1 && want == body_at(k - 1, self.p.p_t, self.home, self.cast.anchor) {
                    self.near.body_off += 1;
                    if self.near.body_off == 1 {
                        if let Some(c) = counted("body_held") {
                            wlog(format!("{} BODY HELD #{c}: {k} ticks into the spirit his body is at {pos:?}, not at {want:?} \
                                          where it was put", head(sim, me)));
                        }
                    }
                }
                sim.entity_set_pos(me, want.0, want.1);
            }
            match stage(k, self.p.p_t, self.fall.is_some()) {
                Stage::Cast => {
                    if targetable && k >= REBANISH_AFTER {
                        self.rebanish(sim, me, k);
                    }
                    if k > 0 && k.is_multiple_of(NEAR_EVERY) {
                        let spot = (self.cast.anchor.0 as f64, self.cast.anchor.1 as f64);
                        self.near.add(foes_near(sim, team, spot, NEAR_R, false).0.len());
                    }
                    self.spirit_casts(sim, me, now, k);
                }
                Stage::LayDown => {
                    // the spirit's last tick still casts (a Requiem started in time lands here at the latest)
                    self.spirit_casts(sim, me, now, k);
                    self.lay_down(sim, me, now);
                }
                Stage::Strike => self.strike(sim, me, now),
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
        // his own fall blow (credited to the last hitter) is no hit on the spirit (0.5.5)
        if !spirit_hit_counts(self.fall.as_ref().map(|f| f.tries)) {
            return;
        }
        let Some(kind) = sim.get_entity(attacker).filter(|_| attacker != self.me).map(|a| kind_of(&a)) else { return };
        if self.spirit.is_some() {
            // nothing should reach the spirit: who still does
            self.hits.add(kind);
            if let Some(k) = counted("spirit_hit") {
                wlog(format!("{} SPIRIT HIT #{k}: struck by {} ({damage} damage)", head(sim, self.me), who(sim, attacker)));
            }
        } else if damage > 0 {
            self.last_hit = Some(attacker);
            self.last_player = player_of(sim, attacker);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if self.spirit.is_some() {
            if let Some(k) = counted("spirit_kill") {
                wlog(format!("{} SPIRIT KILL #{k}: {} killed by the spirit", head(sim, me), who(sim, victim)));
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        // the respawn timer counts the spirit (League's death timer runs from its start), but here the game has not marked him
        // dead yet (0.4.x: every try said `RESPAWN NOT CUT (alive)`) and afterwards none of his own hooks run (0.5.0's AI hook
        // never cut one): noted for `cut_respawns`, which any living champion's `shun` runs once he is marked dead
        let now = sim.tick();
        if let Some(f) = self.fall.take() {
            if let Some(k) = counted("fall") {
                let (h, c, n) = (self.hits, self.cast.tally, self.near);
                wlog(format!("{} FALL #{k}: the spirit's time is up, he fell {} ticks after it laid down - blow {} by {}{}; \
                              cast as a spirit: Q {} ({} hit), W {} ({} touches), E {} burns, R {}; struck as a spirit by \
                              champions {} times, minions {}, towers {}, others {}; re-banished {} times; foes within {NEAR_R} \
                              of where he fell: {} at the rise, {:.1} on average over the spirit (every {NEAR_EVERY} ticks), {} \
                              at the end; his body off its place {} ticks", head(sim, self.me),
                             now.saturating_sub(f.since), f.tries, f.killer.map_or_else(|| "-".to_string(), |a| who(sim, a)),
                             if f.forced { ", hp set to 0 first" } else { "" }, c.q, c.q_hits, c.w, c.w_hits, c.e_hits, c.r,
                             h.champions, h.minions, h.towers, h.others, c.rebanish, n.at_rise, n.mean(), n.last, n.body_off));
            }
        } else if self.spirit.is_some() {
            if let Some(k) = counted("spirit_died") {
                wlog(format!("{} SPIRIT DIED #{k}: dead before the spirit's time was up", head(sim, self.me)));
            }
        }
        if let Some(t0) = self.rose_at.take() {
            // this simulation's own note (0.5.5: the twin presim, the view's other run and another set's presim each have
            // theirs), found again by the number on the buildings it names (0.5.6: his corpse keeps no buff in the game)
            let cut = Cut { sim: self.sim, body: self.me, anchors: self.anchored.clone(), player, at: now,
                            spent: now.saturating_sub(t0) as u64, back: None, line: head(sim, self.me), told: false };
            let mut cuts = CUTS.lock().unwrap_or_else(|e| e.into_inner());
            add_cut(&mut cuts, cut);
            CUTS_N.store(cuts.len(), Ordering::Relaxed);
        }
        self.spirit = None;
        self.ready = false;
    }
}

// ===================== AI 钩子：灵体站着放技能，R 挑时机 =====================

/// Q 和 E 的施法距离、E 的圈、痛苦之墙找英雄的范围、普攻距离（build_karthus.py 的 q_range / e_cast / e_r / w_r /
/// atk_range；单元测试核对）。R 是全图的。
pub const Q_RANGE: f64 = 80000.0;
pub const E_RANGE: f64 = 55000.0;
pub const E_R: f64 = 55000.0;
pub const W_R: f64 = 60000.0;
pub const ATK_RANGE: f64 = 50000.0;

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

/// 灵体由本包放的技能（0.5.0，build_karthus.py 的 q_cd / q_delay / q_r / q_dmg / q_ratio、e_per / e_dmg / e_ratio、r_cd；
/// 单元测试核对）：荒芜的冷却、标出落点后多久炸开、炸开的半径、伤害（只炸到一个两倍，英雄联盟的「孤立」）；亵渎每多少 tick
/// 烧一次、每次的伤害；R 的冷却（灵体放过安魂曲，复活后 `spirit_ai` 在这之前照样拦下游戏的 AI 的 R）。
pub const Q_CD: usize = 150;
pub const Q_DELAY: usize = 32;
pub const Q_R: f64 = 15000.0;
pub const Q_DMG: usize = 45;
pub const Q_RATIO: usize = 30;
pub const E_PER: usize = 15;
pub const E_DMG: usize = 10;
pub const E_RATIO: usize = 5;
pub const R_CD: usize = 4200;
/// 亵渎的圈（`e_ring`：主包 `e_on` 的画面放在地上）多久在灵体脚下重放一次。
pub const E_RING_EVERY: usize = 60;
/// 灵体的痛苦之墙（0.5.1，build_karthus.py 的 w_cd / w_t / w_hw / w_hh / w_slow / w_slow_t / w_mr / w_mr_t；单元测试核对）：
/// 冷却（他身上的 `w_cd` 标记），墙立多久，墙的宽、高（整个的），碰到的敌人减速多少 %、多久，魔抗少多少 %、多久；
/// `W_EVERY` tick 给碰到墙的敌人续一次（主包的墙每 3 tick 一次）。
pub const W_CD: usize = 720;
pub const W_T: usize = 300;
pub const W_HW: u64 = 3000;
pub const W_HH: u64 = 30000;
pub const W_SLOW: i32 = 40;
pub const W_SLOW_T: usize = 45;
pub const W_MR: i32 = 20;
pub const W_MR_T: usize = 240;
pub const W_EVERY: usize = 3;
/// 灵体最后这么多 tick 不立墙：墙由灵体的被动维持，他倒下墙就不再减速了。
pub const W_LATE: usize = 60;

/// 灵体的荒芜：炸到 `hit` 个敌人时每人的魔法伤害（只炸到一个两倍）。
pub fn q_damage(power: usize, hit: usize) -> usize {
    let d = Q_DMG + power * Q_RATIO / 100;
    if hit == 1 { d * 2 } else { d }
}

/// 灵体的亵渎：每 `E_PER` tick 每个敌人的魔法伤害。
pub fn e_damage(power: usize) -> usize {
    E_DMG + power * E_RATIO / 100
}

/// 灵体待到第 `k` tick（共 `p_t`）还来得及引导完安魂曲。
pub fn r_in_time(k: usize, p_t: usize) -> bool {
    k + R_CH + 1 <= p_t
}

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

/// 已经死了的人：灵体（`p_spirit`），0.5.1 起也算倒下前的 `p_fall`。谁都不选他，他自己也不下命令。
fn spirit_on(e: &StableEntity<'_, '_>) -> bool {
    let (spirit, fall) = (sn("p_spirit"), sn("p_fall"));
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == spirit || b.name() == fall)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 这一格现在能按：解锁了，冷却好了（引擎的「输入合法」不看冷却，league_pyke 的教训）。
fn ready(e: &StableEntity<'_, '_>, slot: SkillSlotV1) -> bool {
    e.cooldown(slot).is_some_and(|c| c.unlocked && (c.remaining == 0 || c.charges > 0))
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn at(e: &StableEntity<'_, '_>) -> (f64, f64) {
    (e.pos().0 as f64, e.pos().1 as f64)
}

/// 灵体倒下的地方（0.5.7：身体等在泉水里，倒下的地方挂在他身上，[`SPOT_TAG`]）；没挂就是身体站的地方。
fn spot_of(e: &StableEntity<'_, '_>) -> (f64, f64) {
    (0..e.buff_count())
        .filter_map(|i| e.buff_at(i))
        .find_map(|b| parse_spot(b.name()))
        .map_or_else(|| at(e), |p| (p.0 as f64, p.1 as f64))
}

/// 队伍 `team` 看得见的 `foes_near`：游戏的 AI 下的命令只能点看得见的目标（灵体自己按 Q 的 0.4.x，对着射程里的英雄按了几十到
/// 上百 tick 放不出来，2026-10-31、11-02 的日志，那时目标多半在草里）。
fn seen_foes(sim: &StableSim<'_>, team: usize, from: (f64, f64), reach: f64) -> (Vec<(usize, f64)>, Vec<(usize, f64)>) {
    foes_near(sim, team, from, reach, true)
}

/// 队伍 `team` 的敌方单位里能挑的：活着、选得中，不是塔、水晶、灵体，离 `from` 不超过 `reach`（`sight`：还要 `team` 看得见）：
/// (英雄, 别的单位)，各自 (实体, 距离)，近的在前。
fn foes_near(sim: &StableSim<'_>, team: usize, from: (f64, f64), reach: f64, sight: bool)
             -> (Vec<(usize, f64)>, Vec<(usize, f64)>) {
    let mut champs = Vec::new();
    let mut others = Vec::new();
    for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower()
            || kind_of(&u) == Some(EntityKindV1::Nexus) || spirit_on(&u) || (sight && !sim.is_visible(team, u.id())) {
            continue;
        }
        let d = dist(from, at(&u));
        if d > reach {
            continue;
        }
        if u.is_champion() {
            champs.push((u.id(), d));
        } else {
            others.push((u.id(), d));
        }
    }
    champs.sort_by(|a, b| a.1.total_cmp(&b.1));
    others.sort_by(|a, b| a.1.total_cmp(&b.1));
    (champs, others)
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

/// 他活着、拦下游戏的 AI 想放的 R 时改按什么：Q > E（在施法距离内）> 普攻最近的英雄（够不着就走过去）。
pub fn hold_pick(foes: &[(usize, f64)], ready: [bool; 2]) -> Vec<(InputKindV1, usize)> {
    let mut out = Vec::new();
    if ready[0] {
        out.extend(foes.iter().filter(|f| f.1 <= Q_RANGE).map(|f| (InputKindV1::Skill, f.0)));
    }
    if ready[1] {
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
    /// 泉水里放 R：按顺序试这些目标；(打死几个, 打残几个)。
    Fountain(Vec<usize>, (usize, usize)),
    /// 游戏的 AI 想放 R，这时候不放：改按这些（Q、E、近处的普攻），都不行就照它原来的走路命令。
    Hold(Vec<(InputKindV1, usize)>),
}

/// R 只在泉水里、敌方血量够低时放（`r_worth`），别的时候游戏的 AI 想放就拦下（用户 2026-11-01：「最好改成死后放大 或者复活后在
/// 泉水放大」）。灵体放逐着、自己出不了手，它的技能由被动放（`spirit_casts`，0.5.0）。灵体和倒下前（`spirit_on`）他是已经死了的
/// 人：游戏的 AI 想让他做什么（回城最要紧，回城到一半也算）都换成原地站着（0.5.1）。灵体放过安魂曲，复活回来 `R_CD` tick 内
/// 照样拦下（技能格没见过那一招，冷却是好的）。
#[derive(Clone, Default)]
struct SpiritAi {
    /// 他这条命出生的位置（泉水）：开局和每次复活后第一次看到他活着时记下。
    home: Option<(f64, f64)>,
    alive: bool,
    /// 游戏的 AI 最近一次下的走路命令：拦下它想放的 R 时照着走。
    last_move: Option<InputV1>,
    /// 游戏的 AI 正在让他回城（`still_recalling`）。
    recalling: bool,
    /// 灵体放过安魂曲的 tick。
    r_used_at: Option<usize>,
}

impl StablePlayerAi for SpiritAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:spirit_ai")
    }

    /// 在 league_ult_press（100）之后：他的 R 由本钩子说了算。
    fn priority(&self) -> i32 {
        105
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let was = base.and_then(|b| InputKindV1::from_code(b.kind));
        if was == Some(InputKindV1::Move) {
            self.last_move = base;
        }
        let recalling = still_recalling(self.recalling, base);
        self.recalling = recalling;
        let (want, names, line, spot) = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let me = pl.champion().filter(|_| pl.is_alive()).filter(|c| c.is_alive());
            let Some(me) = me else {
                self.alive = false;
                self.recalling = false;
                return None;
            };
            let here = at(&me);
            if !self.alive || self.home.is_none() {
                self.home = Some(here);
                self.alive = true;
            }
            if spirit_on(&me) {
                // a dead man (the spirit, then the tick or two before he falls) gives no orders, the passive casts for the
                // spirit: whatever the game's AI wants - a recall above all, also one under way - becomes a stand where he is
                if has_buff(&me, &sn("r_used")) && self.r_used_at.is_none_or(|t| tick > t + R_CD) {
                    self.r_used_at = Some(tick);
                }
                if base.is_none() && !recalling {
                    return None;
                }
                if recalling {
                    self.recalling = false;
                    if let Some(k) = counted("spirit_recall") {
                        wlog(format!("{} SPIRIT RECALL STOPPED #{k}: the game's AI sent the dead man home - standing instead",
                                     head(&sim, me.id())));
                    }
                }
                let (x, y) = me.pos();
                return Some(InputV1::move_to(x, y));
            }
            if busy(&me) {
                return None;
            }
            let in_home = self.home.is_some_and(|h| dist(here, h) <= FOUNTAIN_R);
            if !in_home && was != Some(InputKindV1::Ult) {
                return None; // nothing of ours to decide this tick
            }
            let power = me.stat().magic_power.max(0) as usize;
            let toll = foes_toll(&sim, me.team(), power);
            let hits: Vec<(usize, usize, usize)> = toll.iter().map(|f| (f.1, f.2, f.3)).collect();
            let r_ready = ready(&me, SkillSlotV1::Ult) && self.r_used_at.is_none_or(|t| tick >= t + R_CD);
            let qe = [ready(&me, SkillSlotV1::Skill), ready(&me, SkillSlotV1::Skill2)];
            let want = if in_home && r_ready && r_worth(RWhen::Fountain, &hits, power) {
                Want::Fountain(toll.iter().map(|f| f.0).collect(), r_toll(&hits, power, FOUNTAIN_LOW))
            } else if was == Some(InputKindV1::Ult) {
                let near: Vec<(usize, f64)> =
                    foes_by_distance(&sim, me.team(), here).into_iter().filter(|f| f.1 <= HOLD_ATTACK_R).collect();
                Want::Hold(hold_pick(&near, qe))
            } else {
                return None;
            };
            let ids: Vec<usize> = match &want {
                Want::Hold(c) => c.iter().map(|x| x.1).collect(),
                Want::Fountain(t, _) => t.clone(),
            };
            let names: HashMap<usize, String> = ids.into_iter().map(|t| (t, who(&sim, t))).collect();
            (want, names, head(&sim, me.id()), me.pos())
        };
        let name = |t: usize| names.get(&t).cloned().unwrap_or_else(|| format!("#{t}"));
        let first_valid = |ctx: &StableAiContext<'_>, cands: Vec<(InputKindV1, usize)>| {
            cands.into_iter().find_map(|(k, t)| {
                let input = InputV1::action(k, InputTargetV1::target(t));
                ctx.is_valid_input(&input).then_some((k, t, input))
            })
        };
        match want {
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

// ===================== 钩子：谁都不选灵体 =====================

/// 排在别的挑目标的钩子之后（最晚的是 league_sion 僵尸的 130），在蕾娜塔的狂暴（1_000_000）和解锁总闸
/// （league_unlock_guard，最后一个）之前。
pub const SHUN_PRIORITY: i32 = 200_000;
/// 改打别的单位：离出手的人这么近以内。
pub const SHUN_REACH: f64 = 90000.0;
/// 没有别的可打：退到灵体的亵渎圈外这么远（圈 `E_R` 外再加这些）。
pub const STEP_OUT: f64 = 15000.0;

/// 没有别的可打时往哪走：离灵体不到 `E_R + STEP_OUT` 就从灵体往自己这边退到那么远（叠在一起时往左），够远了就站着（None）。
pub fn step_out(me: (f64, f64), spirit: (f64, f64)) -> Option<(f64, f64)> {
    let keep = E_R + STEP_OUT;
    let d = dist(me, spirit);
    if d >= keep {
        return None;
    }
    let (ux, uy) = if d < 1.0 { (-1.0, 0.0) } else { ((me.0 - spirit.0) / d, (me.1 - spirit.1) / d) };
    Some(((spirit.0 + ux * keep).max(0.0), (spirit.1 + uy * keep).max(0.0)))
}

/// 英雄联盟的灵体谁都选不中：游戏的 AI（或别的钩子）让一个英雄普攻、放技能点向敌方的卡尔萨斯灵体时，改成同一格点向它
/// `SHUN_REACH` 内看得见的别的敌方英雄（普攻还可以是灵体那一队的小兵、召唤物，不打塔、不打野怪），近的先；都不行就退出
/// 亵渎的圈、站着。队友的技能（治疗、护盾）点向自己这边的灵体也一样（0.4.1：灵体是已经死了的人），改给 `SHUN_REACH` 内别的
/// 队友英雄；没有别的队友就照游戏的 AI（站着发呆比奶一下灵体更难看）。挂在每个英雄上：几乎每 tick 都没有新命令，或者命令不是点单位的，一读就走。
#[derive(Clone, Default)]
struct Shun;

/// 队伍 `team` 的英雄里能改给的（活着、选得中、不是灵体、不是 `but`），离 `from` 不超过 `reach`，近的在前。
fn mates(sim: &StableSim<'_>, team: usize, from: (f64, f64), reach: f64, but: usize) -> Vec<usize> {
    let mut out: Vec<(usize, f64)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() == team && u.id() != but && u.is_champion() && u.is_alive() && u.is_targetable() && !spirit_on(u))
        .map(|u| (u.id(), dist(from, at(&u))))
        .filter(|f| f.1 <= reach)
        .collect();
    out.sort_by(|a, b| a.1.total_cmp(&b.1));
    out.into_iter().map(|f| f.0).collect()
}

impl StablePlayerAi for Shun {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:shun")
    }

    fn priority(&self) -> i32 {
        SHUN_PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        let kind = InputKindV1::from_code(b.kind)?;
        if matches!(kind, InputKindV1::Move | InputKindV1::Return)
            || InputTargetKindV1::from_code(b.target.kind) != Some(InputTargetKindV1::Target) {
            return None;
        }
        let player = ctx.player_id();
        let (cands, here, spirit, ally, line, names) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            let s = sim.get_entity(b.target.target_id)?;
            if s.id() == me.id() || !spirit_on(&s) {
                return None;
            }
            let here = at(&me);
            let ally = s.team() == me.team();
            if ally && kind == InputKindV1::Attack {
                return None; // not an ally's order (Renata's berserk comes after this hook)
            }
            let cands: Vec<usize> = if ally {
                mates(&sim, me.team(), here, SHUN_REACH, s.id())
            } else {
                let (champs, others) = seen_foes(&sim, me.team(), here, SHUN_REACH);
                let mut c: Vec<usize> = champs.iter().map(|f| f.0).collect();
                if kind == InputKindV1::Attack {
                    // his side's minions and summons, not the jungle's monsters
                    c.extend(others.iter().map(|f| f.0).filter(|&t| sim.get_entity(t).is_some_and(|u| u.team() == s.team())));
                }
                c
            };
            let names: HashMap<usize, String> =
                cands.iter().chain([&s.id()]).map(|&t| (t, who(&sim, t))).collect();
            (cands, here, spot_of(&s), ally, format!("{} {}", head(&sim, me.id()), who(&sim, me.id())), names)
        };
        let name = |t: usize| names.get(&t).cloned().unwrap_or_else(|| format!("#{t}"));
        let other = cands.into_iter().find_map(|t| {
            let input = InputV1::action(kind, InputTargetV1::target(t));
            ctx.is_valid_input(&input).then_some((t, input))
        });
        let (input, what) = match other {
            Some((t, input)) => (input, format!("{kind:?} on {}", name(t))),
            // no other ally for a heal or a shield: let it go (standing idle by the spirit would look worse, and the game's
            // AI would pick him again next tick)
            None if ally => return None,
            None => match step_out(here, spirit) {
                Some(p) => (InputV1::move_to(p.0 as u64, p.1 as u64), "out of Defile".to_string()),
                None => (InputV1::move_to(here.0 as u64, here.1 as u64), "a stand".to_string()),
            },
        };
        let tag = match (ally, kind == InputKindV1::Attack) {
            (true, _) => "shun_ally",
            (false, true) => "shun_attack",
            (false, false) => "shun_cast",
        };
        if let Some(k) = counted(tag) {
            wlog(format!("{line} SHUN #{k}: {kind:?} on the {} spirit {} -> {what}", if ally { "allied" } else { "enemy" },
                         name(b.target.target_id)));
        }
        Some(input)
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
    module.add_player_input_ai(Shun);
    module.set_match_hook(Respawns);
    host.log(LogLevel::Info, "league_karthus loaded (Death Defied's spirit: untargetable, rooted, casting).");
}

// ===================== 比赛钩子：阵亡后扣复活时间 =====================

/// 每局每 tick（游戏的世界 tick 和输入之后）扣到了的复活时间（`cut_respawns`，0.5.2）：他阵亡后自己的钩子都不跑了，0.5.1 借每个
/// 英雄的钩子 `shun` 扣，可 AI 钩子拿到的模拟状态和被动的配不上，一次都没扣成。一个模块只有一个比赛钩子
/// （`StableMod::set_match_hook`）：单独装时本包设它；附加包合集里由 league_addons 的 `BundleMatch` 转发（0.5.4 起，和
/// league_eggs 的彩蛋一起），所以是 `pub`。开局记一行，看它在不在跑。
pub struct Respawns;

impl StableMatchHook for Respawns {
    fn on_match_start(&self, sim: &mut StableSim<'_>) {
        if let Some(k) = counted("match_hook") {
            wlog(format!("{} MATCH HOOK #{k}: running - it cuts a fallen spirit's respawn", head(sim, 0)));
        }
    }

    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        cut_respawns(sim);
    }
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
    fn a_run_of_rebanishes_is_one_line() {
        // 11-06: #722 cc-immune, REBANISH #1..#6 on ticks 28699-28704
        let mut last = None;
        let lines: Vec<usize> = (28_699..=28_704)
            .filter(|&t| {
                let run = rebanish_run(last, t);
                last = Some(t);
                !run
            })
            .collect();
        assert_eq!(lines, [28_699]);
        // targetable again later in the same spirit: a new line
        assert!(!rebanish_run(Some(28_704), 28_760));
        assert!(!rebanish_run(None, 5));
    }

    #[test]
    fn his_own_fall_blow_is_no_spirit_hit() {
        // 11-06: 47 of 99 SPIRIT HIT lines were the blow (1000+), each one more champion hit in FALL
        assert!(spirit_hit_counts(None));
        assert!(spirit_hit_counts(Some(0)), "laid down, no blow yet");
        assert!(!spirit_hit_counts(Some(1)) && !spirit_hit_counts(Some(3)));
    }

    #[test]
    fn the_body_waits_in_his_well_and_falls_where_he_fell() {
        let (home, spot) = ((32000, 928000), (400000, 500000));
        let p_t = 420;
        assert_eq!(body_at(0, p_t, Some(home), spot), home, "from the first tick");
        assert_eq!(body_at(p_t - BACK_EARLY - 1, p_t, Some(home), spot), home);
        assert_eq!(body_at(p_t - BACK_EARLY, p_t, Some(home), spot), spot, "back while still banished");
        assert_eq!(body_at(p_t - 1, p_t, Some(home), spot), spot, "the lay-down tick");
        assert_eq!(body_at(p_t + 5, p_t, Some(home), spot), spot, "the strike, however long it takes");
        assert_eq!(body_at(0, p_t, None, spot), spot, "no spawn point known: 0.5.6's pin");
        // the stage machine lays him down after he is back
        assert_eq!(stage(p_t - BACK_EARLY, p_t, false), Stage::Cast);
        assert!(BACK_EARLY > 1 && BACK_EARLY + 1 < p_t);
    }

    #[test]
    fn the_wells_the_games_ai_ignores() {
        // the map's nexuses (league_macro_log MAP line): T0 (96000, 864000), T1 (864000, 96000)
        assert!(in_well(0, (32000, 928000)) && in_well(1, (928000, 32000)));
        assert!(in_well(0, (150000, 950000)), "the wide strip along the bottom edge");
        assert!(!in_well(0, (150000, 850000)), "beside the nexus, outside the box");
        assert!(!in_well(0, (928000, 32000)) && !in_well(1, (32000, 928000)), "the other side's well");
        assert!(!in_well(0, (32000, 960001)), "off the map");
        assert!(in_well(0, home_of(0, (0, 0))) && in_well(1, home_of(1, (0, 0))), "the fallback corners");
        assert_eq!(home_of(1, (900000, 40000)), (900000, 40000));
    }

    #[test]
    fn the_spot_rides_on_a_buff_name() {
        let spot = (412345, 98765);
        assert_eq!(parse_spot(&spot_tag(spot)), Some(spot));
        assert_eq!(parse_spot("league_karthus_sim:3"), None);
        assert_eq!(parse_spot("league_karthus_spot:12"), None);
        assert_eq!(parse_spot("league_karthus_spot:a,b"), None);
        let mut n = Near { at_rise: 3, ..Near::default() };
        assert_eq!(n.mean(), 0.0);
        n.add(2);
        n.add(0);
        assert_eq!((n.samples, n.sum, n.last, n.mean()), (2, 2, 0, 1.0));
    }

    fn note(sim: u64, at: usize) -> Cut {
        Cut { sim, body: 5, anchors: Vec::new(), player: 2, at, spent: 422, back: None, line: String::new(), told: false }
    }

    /// 0.5.5 (2026-11-06): the twin presims of a set (sims 7 and 8: the same body #5, player 2, death tick) and another set's
    /// presim (sim 9, the same match and no set either) run interleaved, one far ahead: each cuts only by its own note and
    /// its own clock (before, one note per (kind, match, set) was shared: presims carry no set, and the first to see him dead set
    /// `back` for all).
    #[test]
    fn respawn_notes_are_each_simulations_own() {
        let mut a = note(7, 12_000);
        let mut b = note(8, 12_000);
        let dead = |left: u64| move || Some(left);
        let alive = || None;
        let of = |sim: u64| move |c: &Cut| c.sim == sim;
        // A sees him dead first (2400 left): its own back, B's note untouched
        assert_eq!(step(&mut a, 12_001, &of(7), &dead(2_400)), Step::Cut { want: 1_978, left: 2_400 });
        assert_eq!(step(&mut b, 12_001, &of(7), &dead(2_400)), Step::Skip);
        assert_eq!((a.back, b.back), (Some(12_001 + 1_978), None));
        // set 2's presim (sim 9) has player 2 dead at that tick too: neither note is its
        assert_eq!(step(&mut a, 12_001, &of(9), &dead(900)), Step::Skip);
        assert_eq!(step(&mut b, 12_001, &of(9), &dead(900)), Step::Skip);
        // A runs on past its back: its note goes by its clock; B's (no back yet) does not
        assert_eq!(step(&mut a, 14_000, &of(7), &alive), Step::Drop);
        assert_eq!(step(&mut b, 14_000, &of(7), &alive), Step::Skip);
        // B gets there later, with what it sees (he took longer to be marked dead there: 2 ticks)
        assert_eq!(step(&mut b, 12_001, &of(8), &alive), Step::Skip, "not marked dead yet");
        assert_eq!(step(&mut b, 12_002, &of(8), &dead(2_399)), Step::Cut { want: 1_977, left: 2_399 });
        assert_eq!(step(&mut b, 12_003, &of(8), &dead(1_976)), Step::Skip, "cut already (the game counts down)");
        assert_eq!(step(&mut b, 12_002 + 1_977, &of(8), &alive), Step::Drop);
        // a note no tick of its simulation ever saw dead closes after CUT_WAIT of its own ticks
        let mut c = note(7, 30_000);
        assert_eq!(step(&mut c, 30_000 + CUT_WAIT, &of(7), &alive), Step::Skip);
        assert_eq!(step(&mut c, 30_001 + CUT_WAIT, &of(8), &alive), Step::Skip, "not by another simulation's clock");
        assert_eq!(step(&mut c, 30_001 + CUT_WAIT, &of(7), &alive), Step::Drop);
    }

    #[test]
    fn one_note_per_simulation_and_player() {
        let mut cuts = Vec::new();
        add_cut(&mut cuts, note(7, 100));
        add_cut(&mut cuts, note(8, 100));
        add_cut(&mut cuts, note(7, 900)); // his next death in sim 7: the old note gives way
        assert_eq!(cuts.iter().map(|c| (c.sim, c.at)).collect::<Vec<_>>(), [(8, 100), (7, 900)]);
        assert_eq!(take_cut(&mut cuts, 7, 2).map(|c| c.at), Some(900));
        assert_eq!(take_cut(&mut cuts, 7, 2).map(|c| c.at), None);
        // finished matches' notes past the cap: the oldest goes, not all
        for s in 100..100 + CUTS_MOST as u64 {
            add_cut(&mut cuts, note(s, 5));
        }
        assert_eq!(cuts.len(), CUTS_MOST);
        assert!(!cuts.iter().any(|c| c.sim == 8), "the oldest went");
        assert!(cuts.iter().any(|c| c.sim == 100 + CUTS_MOST as u64 - 1));
    }

    /// One unit of a fake simulation: its kind, alive or not, its buffs; a `deaf` one refuses buffs.
    #[derive(Clone)]
    struct Unit {
        kind: EntityKindV1,
        alive: bool,
        buffs: Vec<BuffV1>,
        deaf: bool,
    }

    type World = std::collections::BTreeMap<usize, Unit>;

    fn unit(kind: EntityKindV1, names: &[&str]) -> Unit {
        Unit { kind, alive: true, buffs: names.iter().map(|n| BuffV1::named(n)).collect(), deaf: false }
    }

    /// `f` run on `world` through the host's simulation vtable (only the slots `owns` and `hang_tag` use).
    fn with_sim<R>(world: &mut World, f: impl FnOnce(&mut StableSim<'_>) -> R) -> R {
        use std::ffi::c_void;
        use std::mem::{size_of, zeroed};
        unsafe fn w<'a>(s: *const c_void) -> &'a mut World {
            &mut *(s as *mut World)
        }
        unsafe fn one<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a mut Unit> {
            h.id().and_then(|id| w(s).get_mut(&id))
        }
        unsafe extern "C" fn count(s: *const c_void) -> usize {
            w(s).len()
        }
        unsafe extern "C" fn nth(s: *const c_void, i: usize) -> EntityHandleV1 {
            w(s).keys().nth(i).map_or(EntityHandleV1::NULL, |&id| EntityHandleV1::from_id(id))
        }
        unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
            one(s, h).is_some()
        }
        unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
            one(s, h).is_some_and(|u| u.alive)
        }
        unsafe extern "C" fn kind(s: *const c_void, h: EntityHandleV1) -> u32 {
            one(s, h).map_or(u32::MAX, |u| u.kind.code())
        }
        unsafe extern "C" fn buffs(s: *const c_void, h: EntityHandleV1) -> usize {
            one(s, h).map_or(0, |u| u.buffs.len())
        }
        unsafe extern "C" fn buff(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
            let Some(b) = one(s, h).and_then(|u| u.buffs.get(i).copied()) else { return false };
            *out = b;
            true
        }
        unsafe extern "C" fn add(s: *mut c_void, id: usize, b: *const BuffV1) {
            if let Some(u) = w(s).get_mut(&id).filter(|u| !u.deaf) {
                u.buffs.push(*b);
            }
        }
        unsafe extern "C" fn remove(s: *mut c_void, h: EntityHandleV1, name: *const u8, len: usize) -> usize {
            let name = std::str::from_utf8(std::slice::from_raw_parts(name, len)).unwrap_or("");
            let Some(u) = one(s, h) else { return 0 };
            let was = u.buffs.len();
            u.buffs.retain(|b| b.name() != name);
            was - u.buffs.len()
        }
        let mut vt: SimVtableV1 = unsafe { zeroed() };
        vt.size = size_of::<SimVtableV1>();
        vt.entity_count = Some(count);
        vt.entity_at = Some(nth);
        vt.entity_is_valid = Some(valid);
        vt.entity_is_alive = Some(alive);
        vt.entity_kind = Some(kind);
        vt.entity_buff_count = Some(buffs);
        vt.entity_buff_at = Some(buff);
        vt.add_buff = Some(add);
        vt.entity_remove_buff = Some(remove);
        let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(),
                                 state: world as *mut World as *mut c_void };
        let mut sim = unsafe { StableSim::from_raw(&mut ctx) }.expect("a simulation context");
        f(&mut sim)
    }

    /// 0.5.6 (2026-11-08): the game clears his corpse's buffs at death (0.5.5 read its number off the corpse and never cut a
    /// respawn: 0 `RESPAWN:` in the 11-08 logs), so a note goes by the buildings carrying its simulation's number - in each twin
    /// the same nexus #1 carries its own.
    #[test]
    fn a_note_is_owned_by_the_number_on_the_buildings() {
        let (t7, t8) = (sim_tag(7), sim_tag(8));
        let corpse = unit(EntityKindV1::Champion, &[]);
        let mut twin_a = World::from([(1, unit(EntityKindV1::Nexus, &[t7.as_str()])), (5, corpse.clone())]);
        // league_eggs' number on the same nexus, with the same digits: not ours
        let mut twin_b = World::from([(1, unit(EntityKindV1::Nexus, &["league_eggs_sim:7", t8.as_str()])), (5, corpse)]);
        let mine = |n: u64| Cut { anchors: vec![1], ..note(n, 1) };
        assert!(with_sim(&mut twin_a, |s| owns(s, &mine(7)) && !owns(s, &mine(8))));
        assert!(with_sim(&mut twin_b, |s| owns(s, &mine(8)) && !owns(s, &mine(7))));
        assert!(with_sim(&mut twin_a, |s| !owns(s, &note(7, 1))), "no building named, nothing on the corpse");
        assert!(with_sim(&mut twin_a, |s| !owns(s, &Cut { anchors: vec![9], ..note(7, 1) })), "no such building");
        assert!(with_sim(&mut twin_a, |s| !owns(s, &mine(0))), "no number");
        // the SDK, where a corpse keeps its buffs: the number on his body still counts
        let fall = sn("p_fall");
        let mut sdk = World::from([(5, unit(EntityKindV1::Champion, &[fall.as_str(), t7.as_str()]))]);
        assert!(with_sim(&mut sdk, |s| owns(s, &note(7, 1)) && !owns(s, &note(8, 1))));
        let mut other = World::from([(5, unit(EntityKindV1::Champion, &["league_mordekaiser_sim:7"]))]);
        assert!(with_sim(&mut other, |s| !owns(s, &note(7, 1))), "another add-on's number");
        assert_eq!(parse_tag(&sim_tag(u64::MAX)), Some(u64::MAX));
        assert!(sim_tag(u64::MAX).len() <= BUFF_NAME_CAP);
    }

    /// 0.5.6: the number goes on the living nexuses - on the living towers only when no nexus takes it - once each, and on
    /// nothing else.
    #[test]
    fn the_number_hangs_on_the_buildings() {
        let tag = sim_tag(7);
        let b = |k: EntityKindV1| unit(k, &[]);
        let fallen = Unit { alive: false, ..b(EntityKindV1::Tower) };
        let mut rift = World::from([(1, unit(EntityKindV1::Nexus, &["league_eggs_sim:3"])), (2, b(EntityKindV1::Nexus)),
                                    (3, b(EntityKindV1::Tower)), (4, fallen.clone()), (5, b(EntityKindV1::Champion))]);
        assert_eq!(with_sim(&mut rift, |s| hang_tag(s, &tag)), (vec![1, 2], "nexus", 3));
        // hung again (a run started over): still one on each
        assert_eq!(with_sim(&mut rift, |s| hang_tag(s, &tag)), (vec![1, 2], "nexus", 3));
        let names = |w: &World, id: usize| w[&id].buffs.iter().map(|b| b.name().to_string()).collect::<Vec<_>>();
        assert_eq!(names(&rift, 1), ["league_eggs_sim:3", tag.as_str()]);
        assert!(names(&rift, 3).is_empty() && names(&rift, 4).is_empty() && names(&rift, 5).is_empty());
        // the nexus refuses it: the standing towers
        let deaf = Unit { deaf: true, ..b(EntityKindV1::Nexus) };
        let mut keep = World::from([(1, deaf), (3, b(EntityKindV1::Tower)), (4, fallen), (6, b(EntityKindV1::Tower))]);
        assert_eq!(with_sim(&mut keep, |s| hang_tag(s, &tag)), (vec![3, 6], "towers", 3));
        // no building yet (tick 0): nothing
        let mut bare = World::from([(5, b(EntityKindV1::Champion))]);
        assert_eq!(with_sim(&mut bare, |s| hang_tag(s, &tag)), (vec![], "", 0));
    }

    #[test]
    fn only_someone_elses_undying_holds_the_spirit_back() {
        let l = |v: &[(&str, bool)]| v.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        assert!(!other_undying(&l(&[("league_karthus_p_guard", true)])));
        assert!(!other_undying(&l(&[("league_karthus_p_spirit", true), ("league_karthus_e_on", false)])));
        assert!(other_undying(&l(&[("league_karthus_p_guard", true), ("league_soraka_w_guard", true)])));
    }

    #[test]
    fn the_respawn_counts_the_spirit() {
        // 25 s left at the fall, the spirit stood 7 s: 18 s left
        assert_eq!(respawn_after_spirit(1500, 420), 1080);
        // a Requiem held the fall 2 s longer: those count too
        assert_eq!(respawn_after_spirit(1500, 540), 960);
        // a short death timer: back a second after the fall, never at once
        assert_eq!(respawn_after_spirit(300, 420), BACK_MIN);
    }

    #[test]
    fn the_spirit_lays_down_a_tick_before_the_blow() {
        // 「灵体结束后还能回城」: the blow landed in the tick the undying spirit buff came off, when it still counted (1 damage)
        assert_eq!(stage(1, 420, false), Stage::Cast);
        assert_eq!(stage(418, 420, false), Stage::Cast);
        assert_eq!(stage(419, 420, false), Stage::LayDown);
        assert_eq!(stage(420, 420, true), Stage::Strike);
        // a late tick still lays him down first; once laid down, every tick strikes until he falls
        assert_eq!(stage(425, 420, false), Stage::LayDown);
        assert_eq!(stage(480, 420, true), Stage::Strike);
        // a Requiem started in time lands on the spirit's last tick at the latest, which still casts
        let last = 420 - R_CH - 1;
        assert!(r_in_time(last, 420) && !r_in_time(last + 1, 420));
        assert_eq!(stage(last + R_CH, 420, false), Stage::LayDown);
    }

    #[test]
    fn the_respawn_cut_is_made_once_whoever_makes_it() {
        // first seen dead with 25 s left, the spirit stood 7 s: back 18 s later
        let back = back_tick(1000, 1500, 420);
        assert_eq!(back, 1000 + 1080);
        assert_eq!(cut_to(back, 1000, 1500), Some(1080));
        // the same sim a tick later, cut and counting down: nothing more
        assert_eq!(cut_to(back, 1001, 1079), None);
        // a few ticks on and still uncut (until the 11-06 fix the set's other presim, which shared the note): to the same tick
        assert_eq!(cut_to(back, 1003, 1497), Some(1077));
        // a short death timer: back BACK_MIN after he was first seen dead
        assert_eq!(cut_to(back_tick(1000, 300, 420), 1000, 300), Some(BACK_MIN));
    }

    #[test]
    fn a_note_serves_only_the_death_it_was_made_for() {
        // the 11-04 log: died on tick 12665 (the timer then 1726, the spirit 422), cut once; died again on tick 38062 with
        // 2400 left - 0.5.2's note, kept 30 wall-clock seconds, cut that one to 1 tick: up again at once
        let back = first_back(12666, 1726, 422).unwrap();
        assert_eq!(back, 12666 + 1304);
        assert!(note_open(12665, Some(back), 12666));
        assert!(note_open(12665, Some(back), back - 1), "until he is back");
        assert!(!note_open(12665, Some(back), back));
        assert!(!note_open(12665, Some(back), 38062), "a later death is not this note's");
        // never seen dead in time: closed for good (a death seen later is another one)
        assert!(note_open(12665, None, 12665 + CUT_WAIT));
        assert!(!note_open(12665, None, 12665 + CUT_WAIT + 1));
        assert!(!note_open(12665, None, 38062));
        // the game has not set his timer yet: no back from a 0 (it gave 0.5.2's back BACK_MIN ticks on)
        assert_eq!(first_back(12666, 0, 422), None);
        // the set's twin presim a few ticks behind, still dead: the same back
        assert_eq!(cut_to(back, 12668, 1724), Some((back - 12668) as u64));
    }

    #[test]
    fn a_recall_runs_until_another_order() {
        let mv = Some(InputV1::move_to(1, 1));
        assert!(still_recalling(false, Some(InputV1::return_home())));
        assert!(still_recalling(true, None));
        assert!(!still_recalling(true, mv));
        assert!(!still_recalling(false, None));
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
        assert!(src.contains(&format!("\"e_r\": {}", E_R as usize)), "e_r is not {E_R}");
        assert!(src.contains(&format!("\"w_r\": {}", W_R as usize)), "w_r is not {W_R}");
        assert!(src.contains(&format!("\"atk_range\": {}", ATK_RANGE as usize)), "atk_range is not {ATK_RANGE}");
        assert!(src.contains(&format!("\"r_dmg\": {R_DMG}, \"r_ratio\": {R_RATIO}")), "r_dmg / r_ratio are not {R_DMG} / {R_RATIO}");
        assert!(src.contains(&format!("\"r_ch\": {R_CH}")), "r_ch is not {R_CH}");
        // the spirit's own casts (0.5.0)
        for (k, v) in [("q_cd", Q_CD), ("q_delay", Q_DELAY), ("q_r", Q_R as usize), ("q_dmg", Q_DMG), ("q_ratio", Q_RATIO),
                       ("e_per", E_PER), ("e_dmg", E_DMG), ("e_ratio", E_RATIO), ("r_cd", R_CD)] {
            assert!(src.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in build_karthus.P");
        }
        // the spirit's Wall of Pain (0.5.1)
        for (k, v) in [("w_cd", W_CD), ("w_t", W_T), ("w_hw", W_HW as usize), ("w_hh", W_HH as usize),
                       ("w_slow", W_SLOW as usize), ("w_slow_t", W_SLOW_T), ("w_mr", W_MR as usize), ("w_mr_t", W_MR_T)] {
            assert!(src.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in build_karthus.P");
        }
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

    fn codes(v: Vec<(InputKindV1, usize)>) -> Vec<(u32, usize)> {
        v.iter().map(|c| (c.0.code(), c.1)).collect()
    }

    #[test]
    fn the_banished_spirit_casts_lay_waste_defile_and_requiem() {
        // 「死了灵体还能移动 还能有残血？」「这能和英雄联盟一样吗」: the whole spirit is banished, its spells are the passive's
        assert_eq!(q_damage(0, 3), Q_DMG);
        assert_eq!(q_damage(100, 2), Q_DMG + Q_RATIO);
        assert_eq!(q_damage(100, 1), 2 * (Q_DMG + Q_RATIO), "one alone: twice (League's isolation)");
        assert_eq!(e_damage(200), E_DMG + 2 * E_RATIO);
        // a Requiem only while there is time to finish it before the spirit falls
        assert!(r_in_time(0, 420));
        assert!(r_in_time(420 - R_CH - 1, 420));
        assert!(!r_in_time(420 - R_CH, 420));
        // 「灵体状态下会放其他技能吗」: Wall of Pain too (0.5.1) - a wall 3000 across and 30000 high, a unit's radius round it
        let wall = (100000, 100000);
        assert!(in_wall((100000, 100000), 0, wall));
        assert!(in_wall((101500, 115000), 0, wall) && !in_wall((101501, 100000), 0, wall));
        assert!(!in_wall((100000, 115001), 0, wall) && in_wall((100000, 115001), 1, wall));
        assert!(in_wall((104000, 100000), 2500, wall), "a champion's body touching the wall counts");
        // his ghost faces the nearest enemy champion (an effect picture is never mirrored)
        assert_eq!(side(500, Some(400)), "l");
        assert_eq!(side(500, Some(600)), "r");
        assert_eq!(side(500, None), "r");
    }

    #[test]
    fn a_held_requiem_turns_into_q_e_or_an_attack() {
        let (q, e, a) = (InputKindV1::Skill.code(), InputKindV1::Skill2.code(), InputKindV1::Attack.code());
        let foes = [(7, 20000.0), (8, 60000.0), (9, 500000.0)];
        assert_eq!(codes(hold_pick(&foes, [true, true])), [(q, 7), (q, 8), (e, 7), (a, 7)]);
        assert_eq!(codes(hold_pick(&foes, [false, false])), [(a, 7)]);
        assert!(hold_pick(&[], [true, true]).is_empty());
    }

    #[test]
    fn enemies_step_out_of_defile_then_stand() {
        let s = (100000.0, 100000.0);
        let p = step_out((120000.0, 100000.0), s).expect("inside the ring: out");
        assert!((p.0 - (100000.0 + E_R + STEP_OUT)).abs() < 1e-6 && (p.1 - 100000.0).abs() < 1e-6);
        assert_eq!(step_out((100000.0 + E_R + STEP_OUT, 100000.0), s), None);
        let on_it = step_out(s, s).expect("on the spirit: out");
        assert!(on_it.0 < s.0);
    }

    #[test]
    fn the_shun_comes_after_the_target_pickers() {
        // league_sion's zombie hook (130) is the last that picks targets; Renata's berserk (1_000_000) comes after
        assert!(SHUN_PRIORITY > 130 && SHUN_PRIORITY < 1_000_000);
    }

    #[test]
    fn hits_count_by_kind() {
        let mut h = Hits::default();
        for k in [Some(EntityKindV1::Champion), Some(EntityKindV1::Champion), Some(EntityKindV1::Tower), None] {
            h.add(k);
        }
        assert_eq!(h, Hits { champions: 2, minions: 0, towers: 1, others: 1 });
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_guard", "p_spirit", "p_fall", "p_ward", "p", "vo_p", "e_on", "w_cd"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
        assert!(spot_tag((u32::MAX as u64, u32::MAX as u64)).len() <= BUFF_NAME_CAP, "the spot, whatever the map");
    }
}
