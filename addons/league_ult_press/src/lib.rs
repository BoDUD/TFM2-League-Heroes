//! 「备好式」技能格替 AI 按（用户 2026-10-17：「莎弥拉和卡牌用附加包在合适时机替AI按R，主包保持现在这样」，
//! 之后：大嘴的 R、卡密尔的 E 同样不按）。
//!
//! 这些格子要么只是 3 tick 的「备好」动作（真技能由主包数据在备好期间自己判断时机放出，用不上就退还冷却），要么伤害
//! 全在落地之后。游戏 0.6.4 的 AI 几乎不按（只读观察包，每 10 分钟：莎弥拉 R 0.2 次、崔斯特 R 0.7 次、克格莫 R 0.6–0.9
//! 次，卡密尔 E 每分钟 0.5 次；多数英雄的 R 3–9 次），格子里加 200、1000 的护盾、一次搜敌方英雄、把施放目标放宽都没用。
//! 本包不换主包的英雄（没有 `override/`），只加一个 AI 钩子 `league_ult_press:ult`，在合适的时候替 AI 按下，之后全是
//! 主包（或别的附加包）的数据：
//!
//! - 莎弥拉（`league_samira`，R `Targeting EnemyChampion`，射程 `SAMIRA_RANGE`）：R 好了、射程内有敌方英雄——按 R，
//!   目标是最近的那个。S 评价时这一下就放出「炼狱扳机」，不到 S 就备好 330 tick，期间到了 S 再放。
//!   S 要连着换五种出手打中英雄（枪 / 剑普攻、Q、E 冲刺、落地的 W 旋转），一下打不中 9 秒就掉。游戏的 AI 几乎不对英雄放
//!   E、Q 多半打小兵，40 局一次都没到 S（用户选「帮她连招攒评价」）：R 不按时，`SAMIRA_E_RANGE` 内有敌方英雄、她生命
//!   不低于 `SAMIRA_E_HP`、目标身边 `SAMIRA_E_RANGE` 内的敌方英雄不超过 `SAMIRA_E_CROWD` 个——按 E 冲过去（落地接 W）；
//!   再不然 `SAMIRA_Q_RANGE` 内有敌方英雄、上一下打中英雄的不是 Q——Q 朝他放。其余照旧由 AI 平 A。
//! - 崔斯特（`league_twistedfate`，R `None`）：主包的「命运」备好 600 tick，期间每 10 tick 看一次：他身边 70000 内没有
//!   敌方英雄、360000 内有被我方打过的敌方英雄、那人 60000 内有我方英雄——就揭示敌方英雄、引导后传送过去。本包在
//!   同样的局面才按：他身边 `TF_ALONE` 内没有敌方英雄、生命不低于 `TF_MIN_HP`，而且有个离他 `TF_MIN_FAR` 以外、
//!   `TF_REACH` 以内的我方英雄，`TF_FIGHT` 内贴着敌方英雄（在打架）。
//! - 克格莫（`league_kogmaw`，R `Targeting EnemyChampionRecentlyAttacked`，射程 `KOG_RANGE`）：射程内引擎接受的敌方英雄
//!   （最近被我方打过的）里挑生命比例最低的按 R（大招对残血伤害更高）；一轮三发、之后锁 20 秒都是主包的数据。
//!   不限时游戏里每 10 分钟打了 31.7 发，经典模拟的设计是每局 16.9 发（用户：「大嘴 R 限一限，接近经典模拟设计的频率」）：
//!   开一轮要用一次配额（每 `KOG_VOLLEY_EVERY` tick 攒一次、最多 `KOG_VOLLEYS_MAX` 次），而且要好时机——目标被控住、
//!   生命不到 `KOG_GOOD_HP`、射程内能打的敌方英雄有两个以上，或配额攒满了；一轮开着（`KOG_VOLLEY`）就接着打完。
//! - 卡密尔（`league_camille`，E `Targeting EnemyChampion`）：E 好了、`CAMILLE_RANGE`（主包 E 的射程；附加包钩墙版是
//!   85000，取小的）内有敌方英雄——按 E，目标是最近的那个；钩索、钩墙、冲向敌人由主包 / league_camille_wall 决定。
//! - AI 很少按的小技能和大招（用户：「有问题的英雄全部改成rust」）：只读观察包 21 轮里这些格子好着、身边有敌方英雄时
//!   AI 几乎不按——每 10 分钟迦娜 R 0 次（113 局）、奥莉安娜 R 0.5、辛德拉 0.7、泽拉斯 0.8、凯尔 0.9、烬 1.1、卡尔玛 1.2、
//!   伊芙琳 1.5、卡特琳娜 1.5、费德提克 1.6、瑞兹 1.7（多数英雄 3.5–6 次）；格温 E、佛耶戈 E 一次都没放，奥莉安娜 E 0.8、
//!   卡莉丝塔 E 1.6、希维尔 E 2.5、娑娜 W 3.0、基兰 E 5.0、劫 W 5.5（劫的 W 只有 Q、E 都好着时 AI 才看得到伤害）。
//!   `plan` 按局面替 AI 按，按下去以后的事全是主包的数据：
//!   - 冲上去的（劫 W 还要 Q 好着、格温 E、佛耶戈 E、卡特琳娜 W）：他生命不低于 `ENGAGE_HP`；目标不在敌方塔下（生命
//!     `DIVE_HP` 以下的除外）、目标身边的敌方英雄不比他身边的我方英雄（含他）多，挑生命比例最低的。AI 正往远处撤时不按。
//!   - 卡特琳娜 R：她生命不低于 `KAT_R_HP`、自己不在敌方塔下，`KAT_R_REACH` 内的敌方英雄、`KAT_R_RING` 内有两个以上或
//!     目标生命不到 `KAT_R_LOW`。费德提克 R：`FIDDLE_R_RANGE` 内一处 `FIDDLE_STORM` 内有两个以上敌方英雄（或单个生命
//!     不到 `FIDDLE_LOW`）、不在敌方塔下、那里的敌方英雄最多比那里的我方英雄（含他）多一个，朝那里放。
//!   - 远处引导的（泽拉斯 R、烬 R）：身边 `CHANNEL_SAFE` 内没有敌方英雄、生命不低于 `CHANNEL_HP`，射程内生命不到
//!     `CHANNEL_LOW` 的或我方有人贴着在打的，挑生命比例最低的。辛德拉 R：目标生命不到 `SYNDRA_LOW`、被控住，或射程内
//!     两个以上（主包再按法球数和控制决定立刻放还是待命）。
//!   - 备好式的（凯尔、卡尔玛、伊芙琳、奥莉安娜、斯维因的 R：主包待命一段时间等时机，没用上退还冷却）：`*_NEAR` 内有敌方英雄就按。
//!     斯维因（用户 2026-10-19：「乌鸦开大时机挺烂的 一局开不了几次」）：主包的 R 只开 360 tick 的待命窗口，窗口里身边 60000
//!     内有两个敌方英雄、或有敌方英雄（被控住的在 55000 内）而身边有队友才变身（有队友那条是同一天按用户的选择加的），没用上冷却只剩 1 秒；游戏的 AI 难得按一次，那天看的
//!     一局整局只按开过一次（变身时身边已经没有敌方英雄），后台模拟的另一局隔 1–2 分钟一次。本包在 R 好了、`SWAIN_R_NEAR`
//!     内有敌方英雄时按，窗口在打架时一直开着，什么时候变身还是主包判断。
//!     烈娜塔 R 也是一样（用户 2026-10-19：「感觉是不放大招啊 烈娜塔」——看的那一局 11 分半只放出一次）：主包的 R 只开 360 tick
//!     的待命窗口，身边 70000 内两个敌方英雄、或 75000 内有被控住的敌方英雄而 45000 内有队友才放，没用上冷却只剩 1 秒。本包在
//!     R 好了、`RENATA_R_NEAR` 内有敌方英雄时按。
//!     瑞兹 R（也是备好式，主包判断追还是逃）：生命不到 `RYZE_FLEE` 而 `RYZE_THREAT` 内有敌方英雄，或照崔斯特的规则。
//!   - 迦娜 R：她或身边 `JANNA_R_RANGE` 内的队友生命不到 `JANNA_SAVE` 而 `JANNA_THREAT` 内有敌方英雄，或两人以上生命不到
//!     `JANNA_TEAM` 而她身边有敌方英雄。娑娜 W：她或 `SONA_HEAL_R` 内的队友生命不到 `SONA_HURT`。
//!   - 奥莉安娜 E、基兰 E：我方有人（她或射程内的队友）`FIGHT_CONTACT` 内贴着敌方英雄；基兰 E 也追射程内生命不到
//!     `CHASE_LOW` 的。希维尔 E（法术护盾）：`SIVIR_WATCH` 内的敌方英雄 `SIVIR_FRESH` tick 内刚放了技能（冷却开始走），
//!     或她生命不到 `SIVIR_LOW` 而 `SIVIR_CLOSE` 内有敌方英雄。卡莉丝塔 E：主包的「矛够了」标记在、撕裂不在冷却。
//! - 主包所有英雄（`ATTACK_RANGE`）被停住：游戏的 AI 常把他们停在敌方英雄跟前（近战对线时停在 26–32k 外，近战射程 25k；
//!   远程的敌方英雄就在普攻距离内）、下令「走到自己脚下」或什么都不下，站着不打；也会让他们一直跟着敌方英雄走、不出手
//!   （卡兹克）：普攻好了、够得着的敌方英雄（`hold_reach`：近战 `HOLD_REACH`，远程自己的普攻距离）在、AI 只下走路命令
//!   （不是明显往远处撤，`walking_away`）连着 `HOLD_WALKING` tick，也算被停住。
//!   先是卡密尔、瑟提、奥拉夫，之后加上蒙多、赵信、凯尔、洛、亚托克斯、伊芙琳、赛娜，再加上李青、泰达米尔、塔里克，然后扩到所有近战，
//!   最后扩到远程（用户：「远程英雄也补上吧 我发现德莱文这种也有问题」）。
//!   原地站了 `HOLD_STILL` tick、普攻好了、AI 还让他原地站（`holding`）时，`hold_target` 挑人普攻：
//!   他生命不低于 `HOLD_MIN_HP`、目标离敌方塔超过 `TOWER_REACH`、目标身边不比他身边人多；打出一下或 `ENGAGE_TICKS` 后重新算，
//!   AI 自己下了别的命令（普攻、技能、走开）就不管。没有要按的格子时才这样做。
//! - 被控住（眩晕、击飞、沉默等）、正在放技能（施法动作还在播，`busy`：引导中的大招人站着不动、普攻又是好的）、被强制
//!   位移（冲刺、德莱文跑去接斧头）时什么都不做；格子在冷却或还没解锁时不按。冷却由钩子自己看（引擎的「输入合法」不看冷却，
//!   league_pyke 的教训）；引擎不接的命令不下（`is_valid_input`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ult_press.log`，每次启动游戏重写，上一次的留在 .prev.log。
//! ORDER = 按了；CAST = 冷却真的开始走（按下去了，莎弥拉记下当时的评价）；FIRED = 莎弥拉的真大招放出（主包的
//! `league_samira_r_on`）；TELEPORT = 崔斯特按下之后一 tick 内移动了 `TF_JUMP` 以上；STYLE = 莎弥拉这一局到过的最高评价。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ult_press";
const VERSION: &str = env!("CARGO_PKG_VERSION");

pub const SAMIRA: &str = "league_samira";
pub const TF: &str = "league_twistedfate";
pub const KOGMAW: &str = "league_kogmaw";
pub const CAMILLE: &str = "league_camille";
/// 主包莎弥拉 R 的射程（ult range）。
pub const SAMIRA_RANGE: f64 = 50_000.0;
/// 主包莎弥拉真大招放出时挂的 buff（吸血 40，120 tick）。
pub const SAMIRA_R_ON: &str = "league_samira_r_on";
/// 主包莎弥拉的评价 E..S（一次只挂一个）。
pub const SAMIRA_GRADES: [&str; 6] =
    ["league_samira_g1", "league_samira_g2", "league_samira_g3", "league_samira_g4", "league_samira_g5", "league_samira_g6"];
/// 主包：上一下打中英雄的是 Q（同一种出手再来只保住评价，不升）。
pub const SAMIRA_LAST_Q: &str = "league_samira_l_q";
/// E（`Targeting EnemyChampion`，主包射程 60000）：这么近有敌方英雄才冲；她生命不低于这个比例；目标身边这么近的敌方
/// 英雄（含目标）不超过这么多个。
pub const SAMIRA_E_RANGE: f64 = 60_000.0;
pub const SAMIRA_E_HP: f64 = 0.4;
pub const SAMIRA_E_CROWD: usize = 2;
/// Q（`Direction`，主包射程 90000，枪弹打中第一个敌人就停）：这么近有敌方英雄才朝他放。
pub const SAMIRA_Q_RANGE: f64 = 70_000.0;
/// 崔斯特：身边这么近有敌方英雄就不按（主包门槛 70000，多留一点）。
pub const TF_ALONE: f64 = 75_000.0;
/// 我方英雄这么近贴着敌方英雄算在打架（主包门槛：敌方英雄 60000 内有我方英雄）。
pub const TF_FIGHT: f64 = 50_000.0;
/// 那个敌方英雄离他这么近以内（主包门槛 360000，少留一点：备好后人还会走）。
pub const TF_REACH: f64 = 340_000.0;
/// 那个我方英雄离他至少这么远才值得传送。
pub const TF_MIN_FAR: f64 = 100_000.0;
/// 生命比例低于这个不传送过去送死。
pub const TF_MIN_HP: f64 = 0.4;
/// 一 tick 内移动超过这么多算传送了（日志用）。
pub const TF_JUMP: f64 = 50_000.0;
/// 主包克格莫 R 的射程（r_range）。
pub const KOG_RANGE: f64 = 130_000.0;
/// 引擎每 tick 最多问几个克格莫 R 的目标（生命比例从低到高）。
const KOG_ASK: usize = 5;
/// 主包克格莫一轮炮击开着时挂的 buff（第一发挂上，第三发去掉）。
pub const KOG_VOLLEY: &str = "league_kogmaw_r_vol";
/// 克格莫开一轮的配额：每这么多 tick 攒一次、最多攒这么多次（用户：「大嘴 R 限一限，接近经典模拟设计的频率」：
/// 经典模拟每局 16.9 发 = 每 10 分钟约 5.6 轮；不限时游戏里每 10 分钟 31.7 发）。
pub const KOG_VOLLEY_EVERY: usize = 6_000;
pub const KOG_VOLLEYS_MAX: f64 = 2.0;
/// 有配额时这样才开一轮：目标生命不到这个比例、或被控住、或射程内能打的敌方英雄有两个以上、或配额攒满了。
pub const KOG_GOOD_HP: f64 = 0.5;
/// 卡密尔 E：主包的射程（league_camille_wall 的副本是 85000）。
pub const CAMILLE_RANGE: f64 = 60_000.0;

// AI 很少按的小技能和大招（射程都照主包数据的格子）
pub const ZED: &str = "league_zed";
pub const GWEN: &str = "league_gwen";
pub const VIEGO: &str = "league_viego";
pub const KATARINA: &str = "league_katarina";
pub const ORIANNA: &str = "league_orianna";
pub const SIVIR: &str = "league_sivir";
pub const SONA: &str = "league_sona";
pub const ZILEAN: &str = "league_zilean";
pub const KALISTA: &str = "league_kalista";
pub const JANNA: &str = "league_janna";
pub const SYNDRA: &str = "league_syndra";
pub const XERATH: &str = "league_xerath";
pub const KAYLE: &str = "league_kayle";
pub const JHIN: &str = "league_jhin";
pub const KARMA: &str = "league_karma";
pub const EVELYNN: &str = "league_evelynn";
pub const FIDDLESTICKS: &str = "league_fiddlesticks";
pub const RYZE: &str = "league_ryze";
pub const APHELIOS: &str = "league_aphelios";
pub const VLADIMIR: &str = "league_vladimir";
pub const SWAIN: &str = "league_swain";
pub const RENATA: &str = "league_renata";
/// 冲上去的技能：他生命不低于这个才冲；目标在敌方塔下也冲的残血线。
pub const ENGAGE_HP: f64 = 0.4;
pub const DIVE_HP: f64 = 0.25;
/// 劫 W：Q 不在冷却（主包标记 `league_zed_q_cd` 不在）才按，W-E-Q 一起出手（主包最初的设计「W 只在 Q 好着时」）。
pub const ZED_W_RANGE: f64 = 55_000.0;
pub const ZED_Q_CD: &str = "league_zed_q_cd";
pub const GWEN_E_RANGE: f64 = 45_000.0;
pub const VIEGO_E_RANGE: f64 = 46_000.0;
/// 卡特琳娜 W（`EnemyChampionRecentlyAttacked`：引擎只接最近被我方打过的）。
pub const KATARINA_W_RANGE: f64 = 55_000.0;
/// 卡特琳娜 R（射程 30000，旋转时刀飞向 50000 内每个敌方英雄）。
pub const KAT_R_REACH: f64 = 25_000.0;
pub const KAT_R_RING: f64 = 50_000.0;
pub const KAT_R_LOW: f64 = 0.5;
pub const KAT_R_HP: f64 = 0.3;
/// 奥莉安娜 E 的射程；R 待命 6 秒（球附近有敌方英雄就放），这么近有敌方英雄就按。
pub const ORI_E_RANGE: f64 = 75_000.0;
pub const ORI_R_NEAR: f64 = 60_000.0;
/// 在打架：我方有人离敌方英雄这么近。
pub const FIGHT_CONTACT: f64 = 40_000.0;
/// 希维尔 E（法术护盾，射程 65000）。
pub const SIVIR_E_RANGE: f64 = 65_000.0;
pub const SIVIR_WATCH: f64 = 60_000.0;
pub const SIVIR_FRESH: usize = 20;
pub const SIVIR_LOW: f64 = 0.4;
pub const SIVIR_CLOSE: f64 = 40_000.0;
/// 娑娜 W（射程 80000，治疗她和 60000 内一名队友）。
pub const SONA_W_RANGE: f64 = 80_000.0;
pub const SONA_HEAL_R: f64 = 60_000.0;
pub const SONA_HURT: f64 = 0.7;
/// 基兰 E 的射程；追：射程内生命比例不到这个的敌方英雄。
pub const ZILEAN_E_RANGE: f64 = 70_000.0;
pub const CHASE_LOW: f64 = 0.4;
/// 卡莉丝塔 E（`EnemyChampionRecentlyAttacked`）：主包「矛够了」的标记、撕裂的冷却标记。
pub const KALISTA_E_RANGE: f64 = 100_000.0;
pub const KALISTA_E_OK: &str = "league_kalista_e_ok";
pub const KALISTA_E_CD: &str = "league_kalista_e_cd";
/// 迦娜 R（`AllyChampion` 40000，治疗她身边 40000 内的友方英雄）。
pub const JANNA_R_RANGE: f64 = 40_000.0;
pub const JANNA_SAVE: f64 = 0.35;
pub const JANNA_TEAM: f64 = 0.6;
pub const JANNA_THREAT: f64 = 50_000.0;
/// 辛德拉 R 的射程。
pub const SYNDRA_R_RANGE: f64 = 75_000.0;
pub const SYNDRA_LOW: f64 = 0.6;
/// 远处引导的大招（泽拉斯 R 220000、烬 R 180000，站着引导 5–6 秒，被控就断）。
pub const CHANNEL_SAFE: f64 = 45_000.0;
pub const CHANNEL_HP: f64 = 0.4;
pub const CHANNEL_LOW: f64 = 0.5;
pub const XERATH_R_REACH: f64 = 160_000.0;
pub const JHIN_R_REACH: f64 = 140_000.0;
/// 备好式的大招：这么近有敌方英雄就按（凯尔 R 射程 50000、卡尔玛 70000、伊芙琳的扇形半径 45000）。
pub const KAYLE_R_NEAR: f64 = 50_000.0;
pub const KARMA_R_NEAR: f64 = 70_000.0;
pub const EVELYNN_R_NEAR: f64 = 45_000.0;
/// 斯维因 R（备好式，`Targeting EnemyChampion` 55000：主包待命 360 tick，身边 60000 内两个敌方英雄、或有敌方英雄且 45000 内
/// 有队友才变身，没用上冷却只剩 60 tick）：射程内有敌方英雄就按。
pub const SWAIN_R_NEAR: f64 = 55_000.0;
/// 烈娜塔 R（备好式，`Targeting EnemyChampion` 75000：主包待命 360 tick，身边 70000 内两个敌方英雄、或射程内有被控住的敌方
/// 英雄且 45000 内有队友才放，没用上冷却只剩 60 tick）：射程内有敌方英雄就按。
pub const RENATA_R_NEAR: f64 = 75_000.0;
/// 备好式大招按下后看这么久：冷却一下掉了很多就是退还了，没掉就是用掉了（最长的凯尔待命 900 tick）。
pub const ARM_WATCH: usize = 960;
/// 费德提克 R（`Position` 80000，引导 1 秒后传过去，鸦群打 45000 内的敌人）。
pub const FIDDLE_R_RANGE: f64 = 80_000.0;
pub const FIDDLE_STORM: f64 = 45_000.0;
pub const FIDDLE_LOW: f64 = 0.4;
/// 瑞兹 R（备好式，主包每 10 tick 判断传去打架还是逃命）：逃命的生命线和威胁距离；去打架照崔斯特（`tf_fight`）。
pub const RYZE_FLEE: f64 = 0.35;
pub const RYZE_THREAT: f64 = 60_000.0;
/// 厄斐琉斯 R（备好式，冷却 25 秒：主包待命 6 秒，正被我方打的敌方英雄身边还有别人、或被控住才放，没用上缩短冷却）：
/// 这么近有敌方英雄就按。观察包里每 10 分钟只按 3.2 次。
pub const APHELIOS_R_NEAR: f64 = 90_000.0;
/// 弗拉基米尔 R（`EnemyChampionRecentlyAttacked` 60000，血云半径 26000）：目标生命不到 `VLAD_R_LOW`，或血云里能罩住两个以上
/// 敌方英雄。观察包里每 10 分钟 3.8 次。
pub const VLAD_R_RANGE: f64 = 60_000.0;
pub const VLAD_R_CLOUD: f64 = 26_000.0;
pub const VLAD_R_LOW: f64 = 0.5;
/// 对线被 AI 停住的近战（用户：「卡密尔、瑟提、奥拉夫对线被 AI 停住时，附加包替她们上去平 A（血量够、不在对面塔下、
/// 不被以少打多）」）：只读观察包里她们常在对面英雄 26–32k 外（近战射程 25k）被 AI 下令「走到自己脚下」站着。
/// 之后（用户：「站桩的按照之前卡密尔那样改 然后合并」）：观察包里同样被停住的——站着不动 13–36%、其中 5–12% 是 AI 下令
/// 「走到自己脚下」（盖伦、贾克斯 3–4% / 1%）——蒙多、赵信、凯尔、洛、亚托克斯、伊芙琳、赛娜。
/// 再之后（用户：「李青、泰达米尔、塔里克照卡蜜尔的规则加进站桩名单，做完开 PR」）：前十位身边有敌方英雄时站着不动
/// 瑟提 22.7% → 16.8%、奥拉夫 18.0% → 12.4%、亚托克斯 14.3% → 10.0%，名单外的不变；站着不动 18–23% 的李青、泰达米尔
/// （其中 9.6% 是「走到自己脚下」）、塔里克（94% 是什么命令都没下）。
/// 最后（玩家视频里墨菲特和敌人叠在一起也不出手；用户：「站桩规则扩到所有近战英雄（自己有 AI 钩子的逐个确认）」）：观察包
/// 第 13–20 轮里名单外的近战一样站着——魔腾 23.1%、墨菲特 19.9%、芮尔 18.0%、德莱厄斯 15.6%、雷克塞 15.3%、阿木木 14.9%、
/// 永恩 13.7%、蕾欧娜、菲奥娜 13.4%、布里茨 13.0%、莉莉娅 12.1%（盖伦 2.9%、格温 3.0%、劫 3.2%）。所以换成「所有近战」：
/// 主包数据里普攻距离不超过 `MELEE_RANGE` 的英雄。
/// 自己有 AI 钩子的英雄逐个看过：布隆、伊莉丝、杰斯、奈德丽、尼菈、塔姆、李青、泰达米尔的钩子只改 AI 要放的技能（换目标或
/// 换时机），艾瑞莉娅的只在 Q 射程里没有敌方英雄时跳小兵，魔腾的鬼影重重只改打向黑暗里的出手，回城日志和米利欧看别人的
/// 钩子只看不改——AI 让他原地站着时它们都不下命令。德莱厄斯、派克能斩杀时 AI 没想放也按 R：钩子按优先级从低到高
/// 依次跑、后跑的可以换掉前面的命令（champion-data 第 8 节），他们的钩子后跑就把这里的普攻换成 R，先跑的话这里看到的是 R、
/// 不算原地站——斩杀照样出手。
/// 再之后（用户：「远程英雄也补上吧 我发现德莱文这种也有问题」「大招这种可能也是」）：远程一样被停住——观察包里卡尔玛身边
/// 28–39k 有敌方英雄（她的普攻距离 55k）、普攻好着，AI 下令「走到自己脚下」或什么都不下，和近战一样；德莱文每分钟只平 A
/// 7.9 次（其他射手 14–17 次）。所以换成主包所有英雄：近战照旧打 `HOLD_REACH` 内的，远程只打自己普攻距离内的（站着就打得到，
/// 不往前走），盯住的目标走出普攻距离 `RANGED_KEEP` 以外就不追。远程英雄自己的 AI 钩子：巴德、伊莉丝、杰斯、卡莉丝塔、
/// 千珏、奈德丽只改自己要放的技能，米利欧看别人的钩子只看不改；烈娜塔的狂暴钩子优先级 1000000、最后跑，被她大招扫中的人
/// 照样由它控制。引擎接口读不到普攻距离，表照数据写在这里，单元测试 `attack_ranges_match_the_data` 逐个对照
/// league/champion，加了新英雄没补进来就报错。
pub const MELEE_RANGE: u64 = 30_000;
pub const ATTACK_RANGE: [(&str, u64); 155] = [
    ("league_aatrox", 26000),
    ("league_ahri", 55000),
    ("league_akali", 24000),
    ("league_alistar", 25000),
    ("league_amumu", 25000),
    ("league_anivia", 55000),
    ("league_annie", 60000),
    ("league_aphelios", 55000),
    ("league_ashe", 60000),
    ("league_bard", 52000),
    ("league_blitzcrank", 25000),
    ("league_brand", 52000),
    ("league_braum", 25000),
    ("league_briar", 24000),
    ("league_caitlyn", 65000),
    ("league_camille", 25000),
    ("league_cassiopeia", 60000),
    ("league_chogath", 26000),
    ("league_corki", 55000),
    ("league_darius", 25000),
    ("league_diana", 24000),
    ("league_draven", 55000),
    ("league_drmundo", 25000),
    ("league_ekko", 24000),
    ("league_elise", 23000),
    ("league_evelynn", 24000),
    ("league_ezreal", 55000),
    ("league_fiddlesticks", 50000),
    ("league_fiora", 25000),
    ("league_fizz", 24000),
    ("league_galio", 25000),
    ("league_gangplank", 26000),
    ("league_garen", 25000),
    ("league_gnar", 25000),
    ("league_gragas", 25000),
    ("league_graves", 46000),
    ("league_gwen", 24000),
    ("league_hecarim", 25000),
    ("league_heimerdinger", 55000),
    ("league_hwei", 55000),
    ("league_ivern", 47500),
    ("league_irelia", 25000),
    ("league_janna", 60000),
    ("league_jarvaniv", 26000),
    ("league_udyr", 25000),
    ("league_qiyana", 25000),
    ("league_ziggs", 55000),
    ("league_jax", 25000),
    ("league_jayce", 25000),
    ("league_jhin", 55000),
    ("league_jinx", 64500),
    ("league_kaisa", 55000),
    ("league_kalista", 52500),
    ("league_karma", 55000),
    ("league_karthus", 50000),
    ("league_kassadin", 24000),
    ("league_katarina", 23000),
    ("league_kayle", 25000),
    ("league_kayn", 24000),
    ("league_kennen", 55000),
    ("league_khazix", 23000),
    ("league_kindred", 55000),
    ("league_kogmaw", 55000),
    ("league_ksante", 25000),
    ("league_leblanc", 52500),
    ("league_leesin", 23000),
    ("league_leona", 25000),
    ("league_lillia", 25000),
    ("league_lissandra", 55000),
    ("league_lucian", 55000),
    ("league_lulu", 55000),
    ("league_lux", 55000),
    ("league_malphite", 25000),
    ("league_maokai", 26000),
    ("league_mel", 55000),
    ("league_malzahar", 52000),
    ("league_masteryi", 25000),
    ("league_milio", 53000),
    ("league_missfortune", 55000),
    ("league_mordekaiser", 25000),
    ("league_morgana", 50000),
    ("league_naafiri", 23000),
    ("league_nami", 55000),
    ("league_nasus", 26000),
    ("league_nautilus", 25000),
    ("league_neeko", 55000),
    ("league_nidalee", 23000),
    ("league_nilah", 30000),
    ("league_nocturne", 23000),
    ("league_olaf", 25000),
    ("league_ornn", 25000),
    ("league_orianna", 55000),
    ("league_pantheon", 27000),
    ("league_poppy", 25000),
    ("league_pyke", 24000),
    ("league_quinn", 52500),
    ("league_rakan", 40000),
    ("league_rammus", 25000),
    ("league_reksai", 26000),
    ("league_rell", 25000),
    ("league_renata", 55000),
    ("league_renekton", 25000),
    ("league_rengar", 23000),
    ("league_riven", 25000),
    ("league_ryze", 55000),
    ("league_samira", 55000),
    ("league_senna", 62000),
    ("league_seraphine", 55000),
    ("league_sett", 25000),
    ("league_shaco", 23000),
    ("league_shen", 25000),
    ("league_shyvana", 25000),
    ("league_sion", 25000),
    ("league_sivir", 55000),
    ("league_smolder", 55000),
    ("league_sona", 55000),
    ("league_soraka", 60000),
    ("league_sylas", 26000),
    ("league_swain", 52000),
    ("league_syndra", 55000),
    ("league_tahmkench", 28000),
    ("league_talon", 23000),
    ("league_taric", 25000),
    ("league_teemo", 50000),
    ("league_thresh", 48000),
    ("league_tristana", 55000),
    ("league_tryndamere", 25000),
    ("league_twistedfate", 57500),
    ("league_twitch", 55000),
    ("league_urgot", 38000),
    ("league_varus", 57500),
    ("league_vayne", 55000),
    ("league_veigar", 55000),
    ("league_velkoz", 55000),
    ("league_vex", 55000),
    ("league_vi", 24000),
    ("league_viego", 26000),
    ("league_viktor", 55000),
    ("league_vladimir", 48000),
    ("league_volibear", 25000),
    ("league_warwick", 25000),
    ("league_wukong", 26000),
    ("league_akshan", 55000),
    ("league_xayah", 57500),
    ("league_xerath", 55000),
    ("league_xinzhao", 26000),
    ("league_yasuo", 25000),
    ("league_yone", 25000),
    ("league_yunara", 57500),
    ("league_yuumi", 50000),
    ("league_zed", 23000),
    ("league_zeri", 60000),
    ("league_zilean", 55000),
    ("league_zoe", 55000),
    ("league_zyra", 55000),
];
/// 远程：盯住的目标走出普攻距离这么多就不追。
pub const RANGED_KEEP: f64 = 10_000.0;

/// 主包数据里的普攻距离（不是主包的英雄就 `None`）。
pub fn attack_range(name: &str) -> Option<u64> {
    ATTACK_RANGE.iter().find(|(n, _)| *n == name).map(|&(_, r)| r)
}

/// 交给站桩规则管的英雄：主包所有英雄。
pub fn is_holder(name: &str) -> bool {
    attack_range(name).is_some()
}

/// 被停住时打多远内的敌方英雄、盯住以后走出多远就不追：近战 `HOLD_REACH` / `HOLD_KEEP`；远程是自己的普攻距离、再加 `RANGED_KEEP`。
/// [`hold_reach`] with the attack range her buffs add (`range`: league_kayle's Ascension +27500 at rank 5, +10000 at
/// rank 12): the AI stands her at the stretched reach, and with the table's melee 25000 she was never seen held
/// there - the user, 2026-10-21: 「凯尔…攻击英雄判断会占在升阶范围外毫无作用只用技能拉扯，只有当敌方到达默认攻击范围才
/// 会进行攻击」.
pub fn hold_reach_with(name: &str, extra: f64) -> (f64, f64) {
    if extra <= 0.0 {
        return hold_reach(name);
    }
    let r = attack_range(name).unwrap_or(0) as f64 + extra;
    let base = hold_reach(name);
    (base.0.max(r), base.1.max(r + RANGED_KEEP))
}

pub fn hold_reach(name: &str) -> (f64, f64) {
    match attack_range(name) {
        Some(r) if r > MELEE_RANGE => (r as f64, r as f64 + RANGED_KEEP),
        _ => (HOLD_REACH, HOLD_KEEP),
    }
}
/// 原地站了这么多 tick、普攻好了、AI 还在让她原地站（没下命令，或「走到」离她 `HOLD_HERE` 以内的地方）才算被停住。
pub const HOLD_STILL: usize = 15;
/// 走着不打（玩家 yodajones12：「Kha'zix sometimes following opponent and not attacking」）：只读观察包里卡兹克身边 50000 内
/// 有敌方英雄的 3 秒里，AI 下了约 25 次走路命令、0–2 次普攻，最近的敌方英雄在 19–46k（他的普攻射程 23000），原地站着不动只有
/// 5–7%——`HOLD_STILL` 抓不到。普攻好了、`HOLD_REACH` 内有敌方英雄、AI 只下走路命令或不下命令、不是往远处撤，连着这么多 tick
/// 也算被停住。
pub const HOLD_WALKING: usize = 30;
/// 走路的目的地比他现在离目标远这么多以上，就是在撤（拉开、回撤）：那是 AI 自己的打算，不算被停住。
pub const HOLD_AWAY: f64 = 10_000.0;
pub const HOLD_HERE: f64 = 3_000.0;
/// 近战：这么近的敌方英雄才上去打（观察到的停住距离 26–32k）；打上了之后对方走到 `HOLD_KEEP` 以外就不追。
pub const HOLD_REACH: f64 = 35_000.0;
pub const HOLD_KEEP: f64 = 45_000.0;
/// 血量够：她的生命比例不低于这个。
pub const HOLD_MIN_HP: f64 = 0.5;
/// 不在对面塔下：目标离敌方塔不到这么远就不打（league_irelia / league_kassadin 的塔下范围）。
pub const TOWER_REACH: f64 = 75_000.0;
/// 不被以少打多：目标身边这么近的敌方英雄（含目标）不多于她身边的我方英雄（含她）。
pub const CROWD_R: f64 = 60_000.0;
/// 上去之后最多替 AI 盯这么多 tick（打出一下就重新算）。
pub const ENGAGE_TICKS: usize = 90;
/// 按下后这么多 tick 内冷却开始走，就算按下去了；之后这么多 tick 内看有没有放出真大招 / 传送。
const ORDER_FRESH: usize = 30;
const WATCH_AFTER: usize = 700;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ULT_PRESS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ult_press.log");
        }
    }
    PathBuf::from("league_ult_press.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (league_kindred)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<String, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: String) -> Option<usize> {
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
    let name = sim.get_entity(id).and_then(|e| e.name()).unwrap_or_default();
    format!("[{kind} m={} s={} seed={}] t={} {name}#{id}", m(o.match_id), m(o.set_index), sim.seed(), sim.tick())
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 什么时候按（单元测试用） =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个敌方 / 我方英雄：id、位置、生命比例。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: f64,
}

/// `range` 内最近的敌方英雄（莎弥拉的 R、卡密尔的 E）。
pub fn nearest_in(me: (f64, f64), range: f64, enemies: &[Unit]) -> Option<usize> {
    enemies
        .iter()
        .map(|u| (u.id, dist(me, u.at)))
        .filter(|&(_, d)| d <= range)
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(id, _)| id)
}

/// 崔斯特：他一个人（`TF_ALONE` 内没有敌方英雄）、生命够，远处（`TF_MIN_FAR`..`TF_REACH`）有我方英雄 `TF_FIGHT` 内贴着
/// 敌方英雄 -> `(那个敌方英雄, 那个我方英雄)`，挑离他最近的一组。
pub fn tf_fight(me: (f64, f64), hp: f64, allies: &[Unit], enemies: &[Unit]) -> Option<(usize, usize)> {
    if hp < TF_MIN_HP || enemies.iter().any(|u| dist(me, u.at) <= TF_ALONE) {
        return None;
    }
    let mut best: Option<(usize, usize, f64)> = None;
    for a in allies {
        if dist(me, a.at) < TF_MIN_FAR {
            continue;
        }
        for e in enemies {
            let reach = dist(me, e.at);
            if dist(a.at, e.at) <= TF_FIGHT && reach <= TF_REACH && best.is_none_or(|b| reach < b.2) {
                best = Some((e.id, a.id, reach));
            }
        }
    }
    best.map(|(e, a, _)| (e, a))
}

/// 莎弥拉这一 tick 按什么（先后顺序，引擎接哪个就是哪个）：`ready` = Q、E、R 好了没有，`last_q` = 上一下打中英雄的是 Q。
/// R：射程内最近的敌方英雄；E：`SAMIRA_E_RANGE` 内最近的、她生命够、目标身边不挤；Q：`SAMIRA_Q_RANGE` 内最近的、上一下不是 Q。
pub fn samira_plan(me: (f64, f64), hp: f64, ready: [bool; 3], last_q: bool, enemies: &[Unit]) -> Vec<(char, usize)> {
    let mut plan = Vec::new();
    if ready[2] {
        if let Some(t) = nearest_in(me, SAMIRA_RANGE, enemies) {
            plan.push(('R', t));
        }
    }
    if ready[1] && hp >= SAMIRA_E_HP {
        if let Some(t) = nearest_in(me, SAMIRA_E_RANGE, enemies) {
            let at = enemies.iter().find(|u| u.id == t).map(|u| u.at).unwrap_or(me);
            if enemies.iter().filter(|u| dist(at, u.at) <= SAMIRA_E_RANGE).count() <= SAMIRA_E_CROWD {
                plan.push(('E', t));
            }
        }
    }
    if ready[0] && !last_q {
        if let Some(t) = nearest_in(me, SAMIRA_Q_RANGE, enemies) {
            plan.push(('Q', t));
        }
    }
    plan
}

/// 克格莫：`KOG_RANGE` 内的敌方英雄，生命比例从低到高（前 `KOG_ASK` 个；引擎再看谁最近被我方打过）。
pub fn kog_targets(me: (f64, f64), enemies: &[Unit]) -> Vec<usize> {
    let mut v: Vec<&Unit> = enemies.iter().filter(|u| dist(me, u.at) <= KOG_RANGE).collect();
    v.sort_by(|a, b| a.hp.total_cmp(&b.hp));
    v.into_iter().take(KOG_ASK).map(|u| u.id).collect()
}

/// 克格莫：引擎接受的目标（生命比例从低到高：`(生命比例, 被控住没有)`）里打哪一个、为什么。一轮开着就接着打；
/// 没开着要有配额（`volleys` >= 1），而且是好时机：被控住的、残血的、两个以上能打的、或者配额攒满了。
pub fn kog_pick(open: bool, volleys: f64, valid: &[(f64, bool)]) -> Option<(usize, &'static str)> {
    if valid.is_empty() {
        return None;
    }
    if open {
        return Some((0, "volley open"));
    }
    if volleys < 1.0 {
        return None;
    }
    if let Some(i) = valid.iter().position(|v| v.1) {
        return Some((i, "in crowd control"));
    }
    if valid[0].0 <= KOG_GOOD_HP {
        return Some((0, "low health"));
    }
    if valid.len() >= 2 {
        return Some((0, "two or more in reach"));
    }
    (volleys >= KOG_VOLLEYS_MAX).then_some((0, "volleys saved up"))
}

/// 被停住的英雄打谁（不打就 `None`）：她生命不低于 `HOLD_MIN_HP`；目标是正在盯的那个（还在 `keep` 内）或 `reach` 内最近的
/// 敌方英雄（`hold_reach`）；目标离敌方塔超过 `TOWER_REACH`；目标身边 `CROWD_R` 内的敌方英雄不多于她身边的我方英雄（含她）。
pub fn hold_target(
    me: (f64, f64),
    hp: f64,
    allies: &[Unit],
    enemies: &[Unit],
    towers: &[(f64, f64)],
    (reach, keep): (f64, f64),
    engaged: Option<usize>,
) -> Option<usize> {
    if hp < HOLD_MIN_HP {
        return None;
    }
    let kept = engaged.filter(|t| enemies.iter().any(|u| u.id == *t && dist(me, u.at) <= keep));
    let t = kept.or_else(|| nearest_in(me, reach, enemies))?;
    let p = enemies.iter().find(|u| u.id == t)?.at;
    if towers.iter().any(|&w| dist(w, p) <= TOWER_REACH) {
        return None;
    }
    let theirs = enemies.iter().filter(|u| dist(p, u.at) <= CROWD_R).count();
    let ours = 1 + allies.iter().filter(|u| dist(me, u.at) <= CROWD_R).count();
    (theirs <= ours).then_some(t)
}

/// AI 还在不在回城（0.5.0，游戏 0.6.5 改进了「什么时候回城买装备」：回城是它的决定，钩子不再打断）：回城命令开始，别的
/// 命令结束；引擎只在它判断的那些 tick 下命令（回城时隔一阵再发一次回城），其余 tick 没有命令，照旧。0.4.x 只看这一 tick
/// 是不是回城命令，回城引导中没命令的 tick 被当成「原地站着」，站够 `HOLD_STILL` tick 就让他普攻。
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// 这一步走路是不是在撤：目的地离目标比他现在离目标远 `HOLD_AWAY` 以上。跟着走、斜着走、往前走都不算。
pub fn walking_away(me: (f64, f64), to: (f64, f64), target: (f64, f64)) -> bool {
    dist(to, target) > dist(me, target) + HOLD_AWAY
}

/// 他眼前的局面：他的位置、编号、生命比例，我方英雄（不含他），看得见、选得中的敌方英雄，敌方塔，被控住的敌方英雄。
pub struct Scene<'a> {
    pub me: (f64, f64),
    pub id: usize,
    pub hp: f64,
    pub allies: &'a [Unit],
    pub enemies: &'a [Unit],
    pub towers: &'a [(f64, f64)],
    pub held: &'a [usize],
}

impl Scene<'_> {
    fn foes_within(&self, p: (f64, f64), r: f64) -> usize {
        self.enemies.iter().filter(|u| dist(p, u.at) <= r).count()
    }

    fn under_tower(&self, p: (f64, f64)) -> bool {
        self.towers.iter().any(|&w| dist(w, p) <= TOWER_REACH)
    }

    /// 打 `p` 那里是以少打多：那里 `CROWD_R` 内的敌方英雄多于他身边 `CROWD_R` 内的我方英雄（含他）。
    fn outnumbered_at(&self, p: (f64, f64)) -> bool {
        self.foes_within(p, CROWD_R) > 1 + self.allies.iter().filter(|u| dist(self.me, u.at) <= CROWD_R).count()
    }

    /// 在打架：他，或他 `reach` 内的队友，`FIGHT_CONTACT` 内有敌方英雄。
    fn in_contact(&self, reach: f64) -> bool {
        self.foes_within(self.me, FIGHT_CONTACT) > 0
            || self.allies.iter().any(|a| dist(self.me, a.at) <= reach && self.foes_within(a.at, FIGHT_CONTACT) > 0)
    }

    /// `range` 内的敌方英雄，由近到远。
    fn by_distance(&self, range: f64) -> Vec<usize> {
        let mut v: Vec<&Unit> = self.enemies.iter().filter(|u| dist(self.me, u.at) <= range).collect();
        v.sort_by(|a, b| dist(self.me, a.at).total_cmp(&dist(self.me, b.at)));
        v.into_iter().map(|u| u.id).collect()
    }
}

/// 生命比例从低到高（一样的离他近的在前）。
fn lowest_first(s: &Scene, mut v: Vec<&Unit>) -> Vec<usize> {
    v.sort_by(|a, b| a.hp.total_cmp(&b.hp).then(dist(s.me, a.at).total_cmp(&dist(s.me, b.at))));
    v.into_iter().map(|u| u.id).collect()
}

/// 冲上去的技能打谁（劫 W、格温 E、佛耶戈 E、卡特琳娜 W），先后顺序：他生命不低于 `ENGAGE_HP`；`range` 内、不在敌方塔下
/// （生命 `DIVE_HP` 以下的除外）、身边不以少打多的敌方英雄，生命比例最低的在前。
pub fn engage_targets(s: &Scene, range: f64) -> Vec<usize> {
    if s.hp < ENGAGE_HP {
        return Vec::new();
    }
    let v = s
        .enemies
        .iter()
        .filter(|u| dist(s.me, u.at) <= range && (u.hp <= DIVE_HP || !s.under_tower(u.at)) && !s.outnumbered_at(u.at))
        .collect();
    lowest_first(s, v)
}

/// 卡特琳娜 R：她生命不低于 `KAT_R_HP`、站的地方不在敌方塔下（目标残血除外）；`KAT_R_REACH` 内的敌方英雄，
/// `KAT_R_RING` 内有两个以上，或目标生命不到 `KAT_R_LOW`。由近到远（格子射程 30000）。
pub fn katarina_r(s: &Scene) -> Vec<usize> {
    if s.hp < KAT_R_HP {
        return Vec::new();
    }
    let crowd = s.foes_within(s.me, KAT_R_RING) >= 2;
    let tower = s.under_tower(s.me);
    s.by_distance(KAT_R_REACH)
        .into_iter()
        .filter(|t| s.enemies.iter().any(|u| u.id == *t && (crowd || u.hp <= KAT_R_LOW) && (!tower || u.hp <= DIVE_HP)))
        .collect()
}

/// 费德提克 R 朝哪里放：`FIDDLE_R_RANGE` 内的敌方英雄脚下，`FIDDLE_STORM` 内敌方英雄最多的一处（一样多挑生命低的）；
/// 只有一个的话他生命要不到 `FIDDLE_LOW`。他生命不低于 `ENGAGE_HP`；那里不在敌方塔下；那里 `CROWD_R` 内的敌方英雄最多比
/// 那里的我方英雄（加上传过去的他）多一个。-> `(他, 那一点, 那里的敌方英雄数)`
pub fn fiddle_r(s: &Scene) -> Option<(usize, (f64, f64), usize)> {
    if s.hp < ENGAGE_HP {
        return None;
    }
    let mut best: Option<(&Unit, usize)> = None;
    for u in s.enemies.iter().filter(|u| dist(s.me, u.at) <= FIDDLE_R_RANGE) {
        let n = s.foes_within(u.at, FIDDLE_STORM);
        if (n < 2 && u.hp > FIDDLE_LOW) || s.under_tower(u.at) {
            continue;
        }
        let ours = 1 + s.allies.iter().filter(|a| dist(u.at, a.at) <= CROWD_R).count();
        if s.foes_within(u.at, CROWD_R) > ours + 1 {
            continue;
        }
        if best.is_none_or(|(b, bn)| n > bn || (n == bn && u.hp < b.hp)) {
            best = Some((u, n));
        }
    }
    best.map(|(u, n)| (u.id, u.at, n))
}

/// 远处引导的大招（泽拉斯 R、烬 R）打谁：他身边 `CHANNEL_SAFE` 内没有敌方英雄、生命不低于 `CHANNEL_HP`；`reach` 内
/// 生命不到 `CHANNEL_LOW` 的，或我方有人 `FIGHT_CONTACT` 内贴着的敌方英雄，生命比例最低的在前。
pub fn channel_targets(s: &Scene, reach: f64) -> Vec<usize> {
    if s.hp < CHANNEL_HP || s.foes_within(s.me, CHANNEL_SAFE) > 0 {
        return Vec::new();
    }
    let v = s
        .enemies
        .iter()
        .filter(|u| {
            dist(s.me, u.at) <= reach
                && (u.hp <= CHANNEL_LOW || s.allies.iter().any(|a| dist(a.at, u.at) <= FIGHT_CONTACT))
        })
        .collect();
    lowest_first(s, v)
}

/// 辛德拉 R 打谁：射程内的敌方英雄，生命不到 `SYNDRA_LOW` 的、被控住的，或射程内有两个以上时任何一个；生命比例最低的在前。
pub fn syndra_r(s: &Scene) -> Vec<usize> {
    let all: Vec<&Unit> = s.enemies.iter().filter(|u| dist(s.me, u.at) <= SYNDRA_R_RANGE).collect();
    let crowd = all.len() >= 2;
    let v = all.into_iter().filter(|u| crowd || u.hp <= SYNDRA_LOW || s.held.contains(&u.id)).collect();
    lowest_first(s, v)
}

/// 迦娜 R 对谁放（`AllyChampion`，治疗的是她身边一圈，对谁都一样）：她或 `JANNA_R_RANGE` 内的队友生命不到 `JANNA_SAVE`
/// 而 `JANNA_THREAT` 内有敌方英雄，或两人以上生命不到 `JANNA_TEAM` 而她身边 `JANNA_THREAT` 内有敌方英雄。生命最低的在前（含她）。
pub fn janna_r(s: &Scene) -> Vec<usize> {
    let mut team = vec![(s.id, s.me, s.hp)];
    team.extend(s.allies.iter().filter(|u| dist(s.me, u.at) <= JANNA_R_RANGE).map(|u| (u.id, u.at, u.hp)));
    let threatened = |p: (f64, f64)| s.foes_within(p, JANNA_THREAT) > 0;
    let save = team.iter().any(|&(_, p, hp)| hp < JANNA_SAVE && threatened(p));
    let hurt = team.iter().filter(|t| t.2 < JANNA_TEAM).count();
    if !(save || (hurt >= 2 && threatened(s.me))) {
        return Vec::new();
    }
    team.sort_by(|a, b| a.2.total_cmp(&b.2));
    team.into_iter().map(|t| t.0).collect()
}

/// 娑娜 W：她或 `SONA_HEAL_R` 内的队友生命不到 `SONA_HURT`，射程内的敌方英雄由近到远（格子要一个敌方英雄）。
pub fn sona_w(s: &Scene) -> Vec<usize> {
    let hurt = s.hp < SONA_HURT || s.allies.iter().any(|a| dist(s.me, a.at) <= SONA_HEAL_R && a.hp < SONA_HURT);
    if hurt {
        s.by_distance(SONA_W_RANGE)
    } else {
        Vec::new()
    }
}

/// 基兰 E：在打架（`Scene::in_contact`）时射程内由近到远；不打架时追射程内生命不到 `CHASE_LOW` 的（最低的在前）。
pub fn zilean_e(s: &Scene) -> Vec<usize> {
    if s.in_contact(ZILEAN_E_RANGE) {
        return s.by_distance(ZILEAN_E_RANGE);
    }
    let v = s.enemies.iter().filter(|u| dist(s.me, u.at) <= ZILEAN_E_RANGE && u.hp < CHASE_LOW).collect();
    lowest_first(s, v)
}

/// 希维尔 E：`SIVIR_WATCH` 内有刚放了技能的敌方英雄（`fresh`），或她生命不到 `SIVIR_LOW` 而 `SIVIR_CLOSE` 内有敌方英雄。
/// 射程内的敌方英雄，刚放技能的在前、再由近到远。
pub fn sivir_e(s: &Scene, fresh: &[usize]) -> Vec<usize> {
    let spell = s.enemies.iter().any(|u| fresh.contains(&u.id) && dist(s.me, u.at) <= SIVIR_WATCH);
    let desperate = s.hp < SIVIR_LOW && s.foes_within(s.me, SIVIR_CLOSE) > 0;
    if !spell && !desperate {
        return Vec::new();
    }
    let mut v = s.by_distance(SIVIR_E_RANGE);
    v.sort_by_key(|t| !fresh.contains(t));
    v
}

/// 弗拉基米尔 R 打谁：射程内生命不到 `VLAD_R_LOW` 的，或身边 `VLAD_R_CLOUD` 内有两个以上敌方英雄（含他）的，生命比例最低的在前。
pub fn vladimir_r(s: &Scene) -> Vec<usize> {
    let v = s
        .enemies
        .iter()
        .filter(|u| dist(s.me, u.at) <= VLAD_R_RANGE && (u.hp < VLAD_R_LOW || s.foes_within(u.at, VLAD_R_CLOUD) >= 2))
        .collect();
    lowest_first(s, v)
}

/// 瑞兹 R 逃命的理由（日志里也是这几个字）。
const RYZE_ESCAPE: &str = "low on health";

/// 瑞兹 R（备好式）：逃命——生命不到 `RYZE_FLEE` 而 `RYZE_THREAT` 内有敌方英雄（最近的那个）；去打架——崔斯特的规则。
pub fn ryze_r(s: &Scene) -> Option<(usize, &'static str)> {
    if s.hp < RYZE_FLEE {
        return s.by_distance(RYZE_THREAT).first().map(|&t| (t, RYZE_ESCAPE));
    }
    tf_fight(s.me, s.hp, s.allies, s.enemies).map(|(e, _)| (e, "an ally fights far away"))
}

/// 打的是谁：一个单位，或地上一点（`Position` 施放）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Aim {
    Unit(usize),
    Spot((f64, f64)),
}

/// 一次要按的：日志里的键名、哪个格子、对着谁、为什么；`dive` = 进攻的：冲上去的、站着引导的、打人的大招（AI 正往远处撤
/// 时不按；0.5.0 起不只是冲上去的——游戏 0.6.5 的 AI 自己决定撤退、散开，护盾、治疗、逃命这些照按）。
#[derive(Clone, Debug, PartialEq)]
pub struct Plan {
    pub key: &'static str,
    pub slot: SkillSlotV1,
    pub aim: Aim,
    pub why: String,
    pub dive: bool,
}

/// 他身上的几个主包标记：劫的 Q 好着（没有 `ZED_Q_CD`）、卡莉丝塔能撕裂（`KALISTA_E_OK` 在、`KALISTA_E_CD` 不在）；
/// 刚放了技能的敌方英雄（希维尔）。
#[derive(Clone, Debug, Default)]
pub struct Marks {
    pub zed_q_ready: bool,
    pub kalista_rend: bool,
    pub fresh: Vec<usize>,
}

/// 这一 tick 替这位英雄按什么，先后顺序（引擎接哪个就是哪个）。`ready` 按 `SkillSlotV1` 的编号（普攻、技能1、技能2、大招）。
/// 只管 `slots_of` 新加的这些英雄；莎弥拉、崔斯特、克格莫、卡密尔照旧在 `think` 里。
pub fn plan(name: &str, s: &Scene, ready: [bool; 4], m: &Marks) -> Vec<Plan> {
    let (q, w, r) = (ready[1], ready[2], ready[3]);
    let mut out = Vec::new();
    let mut push = |key: &'static str, slot: SkillSlotV1, ids: Vec<usize>, why: &str, dive: bool| {
        out.extend(ids.into_iter().map(|t| Plan { key, slot, aim: Aim::Unit(t), why: why.to_string(), dive }));
    };
    use SkillSlotV1::{Skill, Skill2, Ult};
    match name {
        ZED if q && m.zed_q_ready => push("W", Skill, engage_targets(s, ZED_W_RANGE), "W-E-Q (Q ready)", true),
        GWEN if w => push("E", Skill2, engage_targets(s, GWEN_E_RANGE), "dash in", true),
        VIEGO if w => push("E", Skill2, engage_targets(s, VIEGO_E_RANGE), "mist and dash in", true),
        KATARINA => {
            if r {
                push("R", Ult, katarina_r(s), "lotus", true);
            }
            if w {
                push("W", Skill2, engage_targets(s, KATARINA_W_RANGE), "shunpo in", true);
            }
        }
        ORIANNA => {
            if r {
                push("R", Ult, s.by_distance(ORI_R_NEAR), "arm the shockwave", true);
            }
            if w && s.in_contact(ORI_E_RANGE) {
                push("E", Skill2, s.by_distance(ORI_E_RANGE), "fight on: shield", false);
            }
        }
        SIVIR if w => push("E", Skill2, sivir_e(s, &m.fresh), "spell shield", false),
        SONA if w => push("W", Skill2, sona_w(s), "someone hurt: heal", false),
        ZILEAN if w => push("E", Skill2, zilean_e(s), "slow / haste", false),
        KALISTA if w && m.kalista_rend => push("E", Skill2, s.by_distance(KALISTA_E_RANGE), "spears enough: rend", false),
        JANNA if r => push("R", Ult, janna_r(s), "monsoon heal", false),
        SYNDRA if r => push("R", Ult, syndra_r(s), "unleashed power", true),
        XERATH if r => push("R", Ult, channel_targets(s, XERATH_R_REACH), "rite from afar", true),
        JHIN if r => push("R", Ult, channel_targets(s, JHIN_R_REACH), "curtain call from afar", true),
        KAYLE if r => push("R", Ult, s.by_distance(KAYLE_R_NEAR), "arm", false),
        KARMA if r => push("R", Ult, s.by_distance(KARMA_R_NEAR), "mantra", false),
        EVELYNN if r => push("R", Ult, s.by_distance(EVELYNN_R_NEAR), "arm", true),
        APHELIOS if r => push("R", Ult, s.by_distance(APHELIOS_R_NEAR), "arm", true),
        SWAIN if r => push("R", Ult, s.by_distance(SWAIN_R_NEAR), "arm the demon", true),
        RENATA if r => push("R", Ult, s.by_distance(RENATA_R_NEAR), "arm the takeover", false),
        VLADIMIR if r => push("R", Ult, vladimir_r(s), "hemoplague", true),
        RYZE if r => {
            if let Some((t, why)) = ryze_r(s) {
                // the escape is not an attack
                push("R", Ult, vec![t], why, why != RYZE_ESCAPE);
            }
        }
        FIDDLESTICKS if r => {
            if let Some((t, at, n)) = fiddle_r(s) {
                let why = format!("crowstorm on {n}");
                out.push(Plan { key: "R", slot: Ult, aim: Aim::Spot(at), why: why.clone(), dive: true });
                out.push(Plan { key: "R", slot: Ult, aim: Aim::Unit(t), why, dive: true });
            }
        }
        _ => {}
    }
    out
}

/// 备好式的大招（主包待命一段时间等时机，没用上退还冷却）：按下以后看它退没退。
pub fn is_armed_ult(name: &str) -> bool {
    matches!(name, ORIANNA | SYNDRA | KAYLE | KARMA | EVELYNN | RYZE | APHELIOS | SWAIN | RENATA)
}

/// 放不出技能的控制。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];

fn controlled(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| NO_CAST.iter().any(|k| k.code() == c.kind)))
}

/// 正在放技能（施法动作还在播，游戏 0.6.4 记成 `Animation`）或被强制位移（`ForceMove`：冲刺、德莱文跑去接斧头）：
/// 不替 AI 按，也不算被停住——引导中的大招（卡特琳娜 R、烬 R）人站着不动、普攻又是好的，这时按普攻会打断它。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

fn busy(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| BUSY.iter().any(|k| k.code() == c.kind)))
}

/// The attack range her buffs add.
fn buff_range(e: &StableEntity<'_, '_>) -> f64 {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.range as f64).sum()
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 莎弥拉现在的评价（1..6 = E..S，0 = 没有）。
fn samira_grade(e: &StableEntity<'_, '_>) -> usize {
    SAMIRA_GRADES.iter().rposition(|g| has_buff(e, g)).map_or(0, |i| i + 1)
}

fn grade_name(g: usize) -> &'static str {
    ["-", "E", "D", "C", "B", "A", "S"][g.min(6)]
}

fn hp_share((now, max): (usize, usize)) -> f64 {
    if max > 0 {
        now as f64 / max as f64
    } else {
        1.0
    }
}

fn at(e: &StableEntity<'_, '_>) -> (f64, f64) {
    let p = e.pos();
    (p.0 as f64, p.1 as f64)
}

// ===================== AI 钩子 =====================

/// 一个替 AI 按的格子：哪个格子、日志里叫什么。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PressSlot {
    pub slot: SkillSlotV1,
    pub key: &'static str,
}

const P_R: PressSlot = PressSlot { slot: SkillSlotV1::Ult, key: "R" };
const P_E2: PressSlot = PressSlot { slot: SkillSlotV1::Skill2, key: "E" };
const P_W2: PressSlot = PressSlot { slot: SkillSlotV1::Skill2, key: "W" };
const P_W1: PressSlot = PressSlot { slot: SkillSlotV1::Skill, key: "W" };

/// 每个英雄替 AI 按哪些格子（它们的冷却开始走就记一行 CAST）。
pub fn slots_of(name: &str) -> &'static [PressSlot] {
    match name {
        SAMIRA | TF | KOGMAW | JANNA | SYNDRA | XERATH | KAYLE | JHIN | KARMA | EVELYNN | FIDDLESTICKS | RYZE | APHELIOS
        | VLADIMIR | SWAIN | RENATA => &[P_R],
        CAMILLE | GWEN | VIEGO | SIVIR | ZILEAN | KALISTA => &[P_E2],
        ORIANNA => &[P_R, P_E2],
        KATARINA => &[P_R, P_W2],
        SONA => &[P_W2],
        ZED => &[P_W1],
        _ => &[],
    }
}

/// 格子 -> 引擎的命令种类。
fn input_kind(slot: SkillSlotV1) -> InputKindV1 {
    match slot {
        SkillSlotV1::Attack => InputKindV1::Attack,
        SkillSlotV1::Skill => InputKindV1::Skill,
        SkillSlotV1::Skill2 => InputKindV1::Skill2,
        SkillSlotV1::Ult => InputKindV1::Ult,
    }
}

/// 一个候选命令：命令、日志里的键名、它从哪个被看着的格子出（`SkillSlotV1` 的编号）、为什么。
type Cand = (InputV1, &'static str, Option<usize>, String);

#[derive(Clone, Debug)]
struct Order {
    tick: usize,
    why: String,
}

#[derive(Clone, Default)]
struct UltPress {
    /// 每个格子（`SkillSlotV1` 的编号）最近一次按（`ORDER_FRESH` tick 内冷却开始走就算是它）、上一次看到的剩余冷却、
    /// 备好式大招按下去的那一 tick（`ARM_WATCH` tick 内看退没退冷却）。
    orders: [Option<Order>; 4],
    last_cds: [Option<usize>; 4],
    armed_at: Option<usize>,
    /// 希维尔看的：每个敌方英雄三个技能格上次的剩余冷却、最近一次开始走冷却的 tick。
    foe_cds: HashMap<usize, ([usize; 3], Option<usize>)>,
    /// 莎弥拉 / 崔斯特的 R 按下去的那一 tick（之后 `WATCH_AFTER` tick 内看结果）。
    cast_at: Option<usize>,
    last_pos: Option<(f64, f64)>,
    r_on: bool,
    /// 莎弥拉这一局到过的最高评价、上一次看到的 tick（新的一局 tick 会变小）。
    best_grade: usize,
    last_tick: usize,
    /// 上一次下的命令（哪个格子、哪一 tick）：一串连着按的只记一行日志。
    last_order: Option<(&'static str, usize)>,
    /// 克格莫开一轮的配额、上次算到的 tick、上一 tick 一轮开着没有。
    volleys: f64,
    volley_tick: usize,
    vol_prev: bool,
    /// 被停住的近战：原地站了几 tick、正在盯的目标和盯到哪一 tick、上一 tick 普攻好了没有。
    still_ticks: usize,
    engage: Option<(usize, usize)>,
    atk_ready_prev: bool,
    /// 走着不打：普攻好了、敌方英雄在 `HOLD_REACH` 内、AI 只下走路命令（不是撤）连着几 tick。
    walk_ticks: usize,
    /// AI 在回城（[`still_recalling`]）。
    recalling: bool,
    /// 这一局敌方的塔（实体编号、位置）：一局找一次，之后每 tick 只看还在不在（塔不会动、不会复活）。
    towers: Option<Vec<(usize, (f64, f64))>>,
    /// 这一局英雄实体在实体表里的位置和编号（按位置排）。表里的先后会变（核对版 2026-10-18：没有英雄复活，两个英雄也换了
    /// 先后），所以每 tick 看一眼这些位置上还是不是它们；有一个不是，或者有玩家的英雄是表里没见过的新实体（复活），才整表
    /// 再看一遍。
    champ_at: Vec<(usize, usize)>,
    /// 核对版：这一 tick 新代码会在看场面之前就返回（是谁）；两种找法这次谁先算。
    #[cfg(ult_press_verify)]
    verify_skip: Option<String>,
    #[cfg(ult_press_verify)]
    verify_flip: bool,
}

/// think() 看的场面：己方英雄、看得见的敌方英雄（希维尔还要他们三个技能格的剩余冷却）、其中被控住的、还在的敌方塔。
#[derive(Debug, Default, PartialEq)]
struct Seen {
    allies: Vec<Unit>,
    enemies: Vec<Unit>,
    held: Vec<usize>,
    towers: Vec<(f64, f64)>,
    foe_cds: Vec<(usize, [usize; 3])>,
}

/// 一个英雄算进场面（`look` 的两种找法共用）。
fn see(sim: &StableSim<'_>, e: &StableEntity<'_, '_>, team: usize, watch_casts: bool, seen: &mut Seen) {
    let u = Unit { id: e.id(), at: at(e), hp: hp_share(e.hp()) };
    if e.team() == team {
        seen.allies.push(u);
    } else if sim.is_visible(team, e.id()) {
        seen.enemies.push(u);
        if controlled(e) {
            seen.held.push(e.id());
        }
        if watch_casts {
            let cds = [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].map(|s| e.cooldown(s).map_or(0, |c| c.remaining));
            seen.foe_cds.push((e.id(), cds));
        }
    }
}

/// 0.4.0 及以前的找法：一个个看这局所有的实体（小兵、野怪、投射物都看一遍）。核对版拿它和新的找法逐 tick 比。
#[cfg(ult_press_verify)]
fn look_all(sim: &StableSim<'_>, mid: usize, team: usize, watch_casts: bool) -> Seen {
    let mut seen = Seen::default();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_alive() || e.id() == mid {
            continue;
        }
        if e.is_tower() {
            if e.team() != team {
                seen.towers.push(at(&e));
            }
            continue;
        }
        if !e.is_champion() || !e.is_targetable() {
            continue;
        }
        see(sim, &e, team, watch_casts, &mut seen);
    }
    seen
}

impl UltPress {
    /// 这一 tick 的场面。用户过日时采样（2026-10-18）：后台模拟线程约 15% 的时间花在这里原来的找法上——每个被管的英雄
    /// 每 tick 把这局所有实体（小兵、野怪、投射物）看一遍。现在只看英雄，按它们在实体表里的先后（`champ_at`：记下的位置上
    /// 还是它们就不整表看），「第一个」「最近的」「血最少的」和原来挑同一个；敌方的塔一局找一次，之后只看还在不在。
    #[cfg(not(ult_press_verify))]
    fn look(&mut self, sim: &StableSim<'_>, mid: usize, team: usize, watch_casts: bool) -> Seen {
        self.look_fast(sim, mid, team, watch_casts)
    }

    /// 核对版（`--cfg ult_press_verify`）：两种找法都算（轮流先算，谁也不总占着游戏数据刚读过的便宜）、计时、逐 tick 比，
    /// 用原来那份做决定。
    #[cfg(ult_press_verify)]
    fn look(&mut self, sim: &StableSim<'_>, mid: usize, team: usize, watch_casts: bool) -> Seen {
        use std::time::Instant;
        self.verify_flip = !self.verify_flip;
        let (all, fast, t_all, t_fast);
        if self.verify_flip {
            let t0 = Instant::now();
            fast = self.look_fast(sim, mid, team, watch_casts);
            let t1 = Instant::now();
            all = look_all(sim, mid, team, watch_casts);
            (t_fast, t_all) = (t1 - t0, t1.elapsed());
        } else {
            let t0 = Instant::now();
            all = look_all(sim, mid, team, watch_casts);
            let t1 = Instant::now();
            fast = self.look_fast(sim, mid, team, watch_casts);
            (t_all, t_fast) = (t1 - t0, t1.elapsed());
        }
        verify::compared(&all, &fast, sim, mid, &self.champ_at, t_all, t_fast);
        all
    }

    fn look_fast(&mut self, sim: &StableSim<'_>, mid: usize, team: usize, watch_casts: bool) -> Seen {
        let towers = self.towers.get_or_insert_with(|| {
            // once a match: every enemy tower, standing or not, in the entity table's order
            (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.is_tower() && e.team() != team)
                .map(|e| (e.id(), at(&e)))
                .collect()
        });
        let mut seen = Seen {
            towers: towers.iter().filter(|(id, _)| sim.get_entity(*id).is_some_and(|e| e.is_alive())).map(|t| t.1).collect(),
            ..Seen::default()
        };
        // the champions in the entity table's order: the slots they were in, while each still holds the same champion
        // and every player's champion is one of them; else a whole scan. A respawn is a new entity in whatever slot is
        // free, and the table moves entities about (the verify builds of 2026-10-18: sorted by entity id, then kept in
        // the order of the last whole scan, they came out in another order than the table's)
        let mut champs = Vec::with_capacity(self.champ_at.len());
        for &(i, id) in &self.champ_at {
            match sim.entity_at(i) {
                Some(e) if e.id() == id => champs.push(e),
                _ => break,
            }
        }
        let known = !self.champ_at.is_empty()
            && champs.len() == self.champ_at.len()
            && (0..sim.player_count())
                .filter_map(|i| sim.player_at(i).and_then(|p| p.champion()))
                .all(|c| self.champ_at.iter().any(|&(_, id)| id == c.id()));
        if !known {
            champs.clear();
            self.champ_at.clear();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_champion() {
                    self.champ_at.push((i, e.id()));
                    champs.push(e);
                }
            }
            #[cfg(ult_press_verify)]
            verify::scanned();
        }
        for e in &champs {
            if e.is_alive() && e.id() != mid && e.is_targetable() {
                see(sim, e, team, watch_casts, &mut seen);
            }
        }
        seen
    }
}

/// 核对版的计数：两种找法得到的场面一样不一样（英雄的先后也算；塔只用来问「附近有没有」，不算先后）、各花多少时间；
/// 新代码提前返回的 tick，原来的代码是不是也什么都不按。
#[cfg(ult_press_verify)]
mod verify {
    use super::{head, wlog, InputV1, Seen, StableSim};
    use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering::Relaxed};
    use std::time::{Duration, Instant};

    static LOOKS: AtomicUsize = AtomicUsize::new(0);
    static DIFFER: AtomicUsize = AtomicUsize::new(0);
    static SCANS: AtomicUsize = AtomicUsize::new(0);
    static NS_ALL: AtomicU64 = AtomicU64::new(0);
    static NS_FAST: AtomicU64 = AtomicU64::new(0);
    static THINKS: AtomicUsize = AtomicUsize::new(0);
    static NS_THINK: AtomicU64 = AtomicU64::new(0);
    static SKIPS: AtomicUsize = AtomicUsize::new(0);
    static SKIP_PRESSED: AtomicUsize = AtomicUsize::new(0);
    /// a summary line this often, and at most DETAILS lines of each kind of difference: the first verify build wrote
    /// 41 MB in two minutes (a difference every tick, every 50th logged) and slowed the user's game to a crawl
    const EVERY: usize = 500_000;
    const DETAILS: usize = 30;

    fn summary() {
        let n = LOOKS.load(Relaxed).max(1) as u64;
        let (all, fast, think) = (NS_ALL.load(Relaxed), NS_FAST.load(Relaxed), NS_THINK.load(Relaxed));
        let thinks = THINKS.load(Relaxed).max(1) as u64;
        wlog(format!(
            "VERIFY {} looks, {} differ (every entity vs the champions in their table slots), {} whole scans; a look {} ns the old way, {} ns the new way; a think {} ns besides the looks over {} thinks; {} early returns, {} where the old way pressed",
            LOOKS.load(Relaxed),
            DIFFER.load(Relaxed),
            SCANS.load(Relaxed),
            all / n,
            fast / n,
            think.saturating_sub(all + fast) / thinks,
            thinks,
            SKIPS.load(Relaxed),
            SKIP_PRESSED.load(Relaxed)
        ));
    }

    /// 塔：只用在 `.any()` 里，先后不影响判断。
    fn tower_set(s: &Seen) -> Vec<(u64, u64)> {
        let mut v: Vec<(u64, u64)> = s.towers.iter().map(|&(x, y)| (x as u64, y as u64)).collect();
        v.sort_unstable();
        v
    }

    pub fn compared(all: &Seen, fast: &Seen, sim: &StableSim<'_>, mid: usize, slots: &[(usize, usize)], t_all: Duration, t_fast: Duration) {
        NS_ALL.fetch_add(t_all.as_nanos() as u64, Relaxed);
        NS_FAST.fetch_add(t_fast.as_nanos() as u64, Relaxed);
        let n = LOOKS.fetch_add(1, Relaxed) + 1;
        let same = all.allies == fast.allies
            && all.enemies == fast.enemies
            && all.held == fast.held
            && all.foe_cds == fast.foe_cds
            && tower_set(all) == tower_set(fast);
        if !same {
            let k = DIFFER.fetch_add(1, Relaxed) + 1;
            if k <= DETAILS {
                let ids = |s: &Seen| {
                    format!(
                        "allies {:?} enemies {:?} held {:?} towers {} cds {:?}",
                        s.allies.iter().map(|u| u.id).collect::<Vec<_>>(),
                        s.enemies.iter().map(|u| u.id).collect::<Vec<_>>(),
                        s.held,
                        s.towers.len(),
                        s.foe_cds.iter().map(|c| c.0).collect::<Vec<_>>()
                    )
                };
                let table: Vec<(usize, usize)> = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i).filter(|e| e.is_champion()).map(|e| (i, e.id())))
                    .collect();
                wlog(format!(
                    "{} VERIFY DIFFER every entity: {} | champions: {} | (slot, champion) in the table {table:?}, kept {slots:?} #{k}",
                    head(sim, mid),
                    ids(all),
                    ids(fast)
                ));
            }
        }
        if n % EVERY == 0 {
            summary();
        }
    }

    pub fn scanned() {
        SCANS.fetch_add(1, Relaxed);
    }

    pub fn thought(t0: Instant) {
        THINKS.fetch_add(1, Relaxed);
        NS_THINK.fetch_add(t0.elapsed().as_nanos() as u64, Relaxed);
    }

    pub fn skipped(skip: Option<String>, out: Option<&InputV1>) {
        if let Some(who) = skip {
            SKIPS.fetch_add(1, Relaxed);
            if let Some(input) = out {
                if SKIP_PRESSED.fetch_add(1, Relaxed) < DETAILS {
                    wlog(format!("{who} VERIFY an early return would have dropped a press (input kind {})", input.kind));
                }
            }
        }
    }
}


/// AI 这一 tick 是不是在让她原地站：没下命令，或者「走到」她脚下 `HOLD_HERE` 以内。
fn holding(base: Option<InputV1>, me: (f64, f64)) -> bool {
    match base {
        None => true,
        Some(b) => b.kind == InputKindV1::Move.code() && dist((b.x as f64, b.y as f64), me) <= HOLD_HERE,
    }
}

impl StablePlayerAi for UltPress {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ult")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        !slots_of(&init.champion_name).is_empty() || is_holder(&init.champion_name)
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        #[cfg(ult_press_verify)]
        let t0 = std::time::Instant::now();
        let out = self.decide(ctx, base);
        #[cfg(ult_press_verify)]
        {
            verify::skipped(self.verify_skip.take(), out.as_ref());
            verify::thought(t0);
        }
        out
    }
}

impl UltPress {
    fn decide(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        // Kog'Maw: a volley open, his saved volleys, and each candidate's (health share, controlled)
        let mut kog: Option<(bool, f64, Vec<(f64, bool)>)> = None;
        // a melee champion the AI holds in lane: the enemy champion to attack, and why
        let mut hold: Option<(usize, String)> = None;
        // the presses in order: the input, its key, the watched slot it goes out of (its SkillSlotV1 code), why
        let (name, cands): (String, Vec<Cand>) = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let me = pl.champion()?;
            let (mid, team) = (me.id(), me.team());
            let name = me.name().unwrap_or_default();
            let holder = is_holder(&name);
            let slots = slots_of(&name);
            if slots.is_empty() && !holder {
                return None;
            }
            let my_at = at(&me);
            let still = self.last_pos == Some(my_at);
            self.still_ticks = if still { self.still_ticks + 1 } else { 0 };
            if tick < self.last_tick || self.volley_tick > tick {
                self.best_grade = 0;
                self.volleys = 1.0;
                self.volley_tick = tick;
                self.engage = None;
                self.walk_ticks = 0;
                self.recalling = false;
                self.armed_at = None;
                self.foe_cds.clear();
                self.towers = None;
                self.champ_at.clear();
            }
            self.volleys = (self.volleys + (tick - self.volley_tick) as f64 / KOG_VOLLEY_EVERY as f64).min(KOG_VOLLEYS_MAX);
            self.volley_tick = tick;
            let vol_open = name == KOGMAW && has_buff(&me, KOG_VOLLEY);
            self.last_tick = tick;
            let grade = if name == SAMIRA { samira_grade(&me) } else { 0 };
            if grade > self.best_grade {
                self.best_grade = grade;
                if grade >= 4 {
                    if let Some(k) = counted(format!("{name} style {grade}")) {
                        wlog(format!("{} STYLE {} reached #{k}", head(&sim, mid), grade_name(grade)));
                    }
                }
            }
            // a watched slot went out when its cooldown starts: the press behind it, or the AI's own
            for ps in slots {
                let i = ps.slot.code() as usize;
                let remaining = me.cooldown(ps.slot).map(|c| c.remaining);
                if let (Some(prev), Some(c)) = (self.last_cds[i], remaining) {
                    if prev == 0 && c > 0 {
                        let why = match self.orders[i].take().filter(|o| tick <= o.tick + ORDER_FRESH) {
                            Some(o) => format!("pressed {} ticks before: {}", tick - o.tick, o.why),
                            None => "by the AI itself".to_string(),
                        };
                        let style = if name == SAMIRA { format!(" [style {}]", grade_name(grade)) } else { String::new() };
                        if let Some(k) = counted(format!("{name} {} cast", ps.key)) {
                            wlog(format!("{} {} CAST {why}{style} #{k}", head(&sim, mid), ps.key));
                        }
                        if ps.slot == SkillSlotV1::Ult {
                            if name == SAMIRA || name == TF {
                                self.cast_at = Some(tick);
                            }
                            // Kog'Maw's first shell opens a volley: one saved volley spent
                            if name == KOGMAW && !self.vol_prev {
                                self.volleys = (self.volleys - 1.0).max(0.0);
                            }
                            if is_armed_ult(&name) {
                                self.armed_at = Some(tick);
                            }
                        }
                    } else if let Some(t0) = self.armed_at.filter(|_| ps.slot == SkillSlotV1::Ult) {
                        // an armed ult the data did not use gives its cooldown back at once (a 3-tick cooldown buff)
                        let refunded = prev > c + 10;
                        if refunded || tick > t0 + ARM_WATCH {
                            let what = if refunded { "refunded (not used)" } else { "kept (used)" };
                            if let Some(k) = counted(format!("{name} arm {what}")) {
                                wlog(format!("{} R ARMED {} ticks before: {what} #{k}", head(&sim, mid), tick - t0));
                            }
                            self.armed_at = None;
                        }
                    }
                }
                self.last_cds[i] = remaining;
            }
            self.vol_prev = vol_open;
            // what the press led to: Samira's real R (S grade), Twisted Fate's jump
            if let Some(t0) = self.cast_at {
                if tick > t0 + WATCH_AFTER {
                    self.cast_at = None;
                } else if name == SAMIRA {
                    if has_buff(&me, SAMIRA_R_ON) && !self.r_on {
                        if let Some(k) = counted(format!("{name} fired")) {
                            wlog(format!("{} R FIRED (S grade) {} ticks after the press #{k}", head(&sim, mid), tick - t0));
                        }
                    }
                } else if name == TF {
                    if let Some(p) = self.last_pos.filter(|p| dist(*p, my_at) >= TF_JUMP) {
                        if let Some(k) = counted(format!("{name} teleport")) {
                            wlog(format!("{} R TELEPORT {:.0} {} ticks after the press #{k}", head(&sim, mid), dist(p, my_at), tick - t0));
                        }
                        self.cast_at = None;
                    }
                }
            }
            self.r_on = name == SAMIRA && has_buff(&me, SAMIRA_R_ON);
            self.last_pos = Some(my_at);
            let ready_of = |s: SkillSlotV1| me.cooldown(s).is_some_and(|c| c.unlocked && c.remaining == 0);
            let ready = [SkillSlotV1::Attack, SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].map(ready_of);
            let any_ready = slots.iter().any(|ps| ready[ps.slot.code() as usize]);
            // a held melee champion's attack went out: what she was told to do is done
            let atk_ready = ready[0];
            if self.atk_ready_prev && !atk_ready {
                self.engage = None;
            }
            self.atk_ready_prev = atk_ready;
            // recalling: nothing pressed and no hold - when to go home (and buy) is the AI's call (game 0.6.5)
            self.recalling = still_recalling(self.recalling, base);
            if self.recalling {
                self.still_ticks = 0;
                self.walk_ticks = 0;
                self.engage = None;
                return None;
            }
            // casting or being moved: nothing to press, and standing in a channel is no hold
            if busy(&me) {
                self.still_ticks = 0;
                self.walk_ticks = 0;
                return None;
            }
            // Samira presses E / Q too, so her R need not be ready; a held champion may attack
            if !me.is_alive() || controlled(&me) || (!any_ready && name != SAMIRA && !holder) {
                return None;
            }
            // a held champion with no pressed slot ready and her attack not ready: below, plan() presses only ready
            // slots of slots_of and the hold only a ready attack, so nothing can come out - skip looking round. Not
            // Samira: her E / Q go out while her R cools down
            let skip = holder && !atk_ready && !any_ready && name != SAMIRA;
            // the verify build only notes it and goes on the 0.4.0 way (think() checks nothing was pressed)
            #[cfg(ult_press_verify)]
            let skip = {
                self.verify_skip = skip.then(|| head(&sim, mid));
                false
            };
            if skip {
                self.walk_ticks = 0;
                return None;
            }
            // Sivir's spell shield waits for an enemy champion's cast: a skill cooldown that starts
            let watch_casts = name == SIVIR;
            let seen = self.look(&sim, mid, team, watch_casts);
            for &(id, cds) in &seen.foe_cds {
                let entry = self.foe_cds.entry(id).or_insert((cds, None));
                if cds.iter().zip(entry.0.iter()).any(|(now, was)| *now > *was + 3) {
                    entry.1 = Some(tick);
                }
                entry.0 = cds;
            }
            let Seen { allies, enemies, held, towers, .. } = seen;
            let fresh: Vec<usize> = self
                .foe_cds
                .iter()
                .filter(|(_, v)| v.1.is_some_and(|t0| tick.saturating_sub(t0) <= SIVIR_FRESH))
                .map(|(id, _)| *id)
                .collect();
            if holder && atk_ready {
                let engaged = self.engage.filter(|&(_, until)| tick <= until).map(|(t, _)| t);
                let reach = hold_reach_with(&name, buff_range(&me));
                // walking with an enemy champion in reach and not away from him (Kha'Zix follows and never attacks)
                let near = nearest_in(my_at, reach.0, &enemies).and_then(|t| enemies.iter().find(|u| u.id == t)).map(|u| u.at);
                let walking = match (base, near) {
                    (Some(b), Some(p)) if b.kind == InputKindV1::Move.code() => {
                        !walking_away(my_at, (b.x as f64, b.y as f64), p)
                    }
                    (None, Some(_)) => true,
                    _ => false,
                };
                self.walk_ticks = if walking { self.walk_ticks + 1 } else { 0 };
                let still_held = holding(base, my_at) && self.still_ticks >= HOLD_STILL;
                let walk_held = self.walk_ticks >= HOLD_WALKING;
                if !holding(base, my_at) && !walking {
                    // the AI does something else (an attack, a skill, a walk away, a recall): its call
                    if base.is_some_and(|b| b.kind == InputKindV1::Move.code()) {
                        self.engage = None;
                    }
                } else if still_held || walk_held || engaged.is_some() {
                    match hold_target(my_at, hp_share(me.hp()), &allies, &enemies, &towers, reach, engaged) {
                        Some(t) => {
                            if engaged != Some(t) {
                                self.engage = Some((t, tick + ENGAGE_TICKS));
                            }
                            let d = enemies.iter().find(|u| u.id == t).map_or(f64::NAN, |u| dist(my_at, u.at));
                            let how = if still_held || !walk_held {
                                format!("held {} ticks", self.still_ticks)
                            } else {
                                format!("walking without attacking {} ticks", self.walk_ticks)
                            };
                            hold = Some((t, format!("{how}, {} {d:.0} away", who(&sim, t))));
                        }
                        None => self.engage = None,
                    }
                }
            } else {
                self.walk_ticks = 0;
            }
            let press = |kind: InputKindV1, t: usize| InputV1::action(kind, InputTargetV1::target(t));
            let (ult, skill2) = (Some(SkillSlotV1::Ult.code() as usize), Some(SkillSlotV1::Skill2.code() as usize));
            // 0.5.0 (game 0.6.5: its AI decides retreats, disperses and tower dives better): nothing at a champion the AI
            // walks away from, and a dash at one under an enemy tower only when he is nearly dead (engage_targets' rule)
            let unit = |t: usize| enemies.iter().find(|u| u.id == t);
            let away_from = |t: usize| match (base, unit(t)) {
                (Some(b), Some(u)) if b.kind == InputKindV1::Move.code() => walking_away(my_at, (b.x as f64, b.y as f64), u.at),
                _ => false,
            };
            let dive_ok = |t: usize| unit(t).is_some_and(|u| u.hp <= DIVE_HP || !towers.iter().any(|&w| dist(w, u.at) <= TOWER_REACH));
            let mut cands = match name.as_str() {
                SAMIRA => {
                    let ready3 = [ready[1], ready[2], ready[3]];
                    let plan = samira_plan(my_at, hp_share(me.hp()), ready3, has_buff(&me, SAMIRA_LAST_Q), &enemies);
                    let mut v = Vec::new();
                    for (k, t) in plan {
                        if away_from(t) || (k == 'E' && !dive_ok(t)) {
                            continue;
                        }
                        let why = format!("{} [style {}]", who(&sim, t), grade_name(grade));
                        match k {
                            'R' => v.push((press(InputKindV1::Ult, t), "R", ult, why)),
                            'E' => v.push((press(InputKindV1::Skill2, t), "E", None, why)),
                            _ => {
                                // Q is a Direction cast: at him, else at his spot, else toward him
                                let p = enemies.iter().find(|u| u.id == t).map_or(my_at, |u| u.at);
                                let q = |target| InputV1::action(InputKindV1::Skill, target);
                                v.push((q(InputTargetV1::target(t)), "Q", None, why.clone()));
                                v.push((q(InputTargetV1::pos(p.0.max(0.0) as u64, p.1.max(0.0) as u64)), "Q", None, why.clone()));
                                v.push((q(InputTargetV1::dir((p.0 - my_at.0) as i64, (p.1 - my_at.1) as i64)), "Q", None, why));
                            }
                        }
                    }
                    v
                }
                CAMILLE if ready[2] => match nearest_in(my_at, CAMILLE_RANGE, &enemies) {
                    Some(t) if !away_from(t) && dive_ok(t) => vec![(press(InputKindV1::Skill2, t), "E", skill2, format!("{} within {CAMILLE_RANGE:.0}", who(&sim, t)))],
                    _ => Vec::new(),
                },
                // Kog'Maw's and Twisted Fate's R only when ready (unlocked and cooled down), as before 0.4.0: since every
                // champion is held (0.4.0) the early return above no longer stops them, and the engine takes an R pressed
                // before level 5 - the game's own AI then reads a None for that champion's ult and panics
                // (game-ai battle.rs:447 / act_gates.rs:111), the match never ends and the day stops (2026-10-18)
                KOGMAW if ready[3] => {
                    let v = kog_targets(my_at, &enemies);
                    let info: Vec<(f64, bool)> = v
                        .iter()
                        .map(|t| (enemies.iter().find(|u| u.id == *t).map_or(1.0, |u| u.hp), held.contains(t)))
                        .collect();
                    let c = v
                        .iter()
                        .zip(&info)
                        .map(|(&t, &(hp, cc))| {
                            let ctl = if cc { ", in crowd control" } else { "" };
                            (press(InputKindV1::Ult, t), "R", ult, format!("{} at {:.0}%{ctl}", who(&sim, t), hp * 100.0))
                        })
                        .collect();
                    kog = Some((vol_open, self.volleys, info));
                    c
                }
                TF if ready[3] => match tf_fight(my_at, hp_share(me.hp()), &allies, &enemies) {
                    Some((e, a)) if !away_from(e) => {
                        let far = allies.iter().find(|u| u.id == a).map_or(f64::NAN, |u| dist(my_at, u.at));
                        vec![(press(InputKindV1::Ult, e), "R", ult, format!("{} fighting {} {far:.0} away, nobody near him", who(&sim, a), who(&sim, e)))]
                    }
                    _ => Vec::new(),
                },
                _ => Vec::new(),
            };
            // the slots the AI hardly presses (plan): not over its own cast of that slot, nothing offensive (`dive`)
            // while it walks away from the target (a recall returned above already)
            if base.is_none_or(|b| b.kind != InputKindV1::Return.code()) {
                let scene = Scene {
                    me: my_at,
                    id: mid,
                    hp: hp_share(me.hp()),
                    allies: &allies,
                    enemies: &enemies,
                    towers: &towers,
                    held: &held,
                };
                // only Zed's and Kalista's plans read these, and each walks all her buffs
                let marks = Marks {
                    zed_q_ready: name == ZED && !has_buff(&me, ZED_Q_CD),
                    kalista_rend: name == KALISTA && has_buff(&me, KALISTA_E_OK) && !has_buff(&me, KALISTA_E_CD),
                    fresh,
                };
                let unit_of = |t: usize| enemies.iter().chain(allies.iter()).find(|u| u.id == t).copied();
                for p in plan(&name, &scene, ready, &marks) {
                    let kind = input_kind(p.slot);
                    if base.is_some_and(|b| b.kind == kind.code()) {
                        continue;
                    }
                    let spot = match p.aim {
                        Aim::Unit(t) => unit_of(t).map(|u| u.at),
                        Aim::Spot(at) => Some(at),
                    };
                    if let (true, Some(b), Some(to)) = (p.dive, base, spot) {
                        if b.kind == InputKindV1::Move.code() && walking_away(my_at, (b.x as f64, b.y as f64), to) {
                            continue;
                        }
                    }
                    let (input, about) = match p.aim {
                        Aim::Unit(t) => {
                            let hp = unit_of(t).map_or(hp_share(me.hp()), |u| u.hp);
                            (press(kind, t), format!("{} at {:.0}%", who(&sim, t), hp * 100.0))
                        }
                        Aim::Spot((x, y)) => (
                            InputV1::action(kind, InputTargetV1::pos(x.max(0.0) as u64, y.max(0.0) as u64)),
                            format!("the spot ({x:.0}, {y:.0})"),
                        ),
                    };
                    cands.push((input, p.key, Some(p.slot.code() as usize), format!("{about} - {}", p.why)));
                }
            }
            (name, cands)
        };
        // the first press the engine takes (Kog'Maw's R: only champions his side hit lately; Samira: R, else E, else Q)
        let pressed = match kog {
            // Kog'Maw: the targets the engine takes, then the pacing (kog_pick) picks one - or none yet
            Some((open, volleys, info)) => {
                let ok: Vec<usize> = (0..cands.len()).filter(|&i| ctx.is_valid_input(&cands[i].0)).collect();
                let valid: Vec<(f64, bool)> = ok.iter().map(|&i| info[i]).collect();
                kog_pick(open, volleys, &valid).and_then(|(j, reason)| {
                    let (input, key, slot, why) = cands.into_iter().nth(ok[j])?;
                    Some((input, key, slot, format!("{why} - {reason} ({volleys:.1} volleys saved)")))
                })
            }
            None => cands.into_iter().find(|(i, _, _, _)| ctx.is_valid_input(i)),
        };
        // nothing to press: a held melee champion attacks the enemy champion in front of her
        let (input, key, slot, why) = match pressed {
            Some(p) => p,
            None => {
                let (t, why) = hold?;
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                if !ctx.is_valid_input(&attack) {
                    self.engage = None;
                    return None;
                }
                (attack, "A", None, why)
            }
        };
        if let Some(i) = slot {
            if self.orders[i].as_ref().is_none_or(|o| tick > o.tick + ORDER_FRESH) {
                self.orders[i] = Some(Order { tick, why: why.clone() });
            }
        }
        // one ORDER line a burst (the engine may take a few ticks; the hook presses again every tick meanwhile)
        if self.last_order.is_none_or(|(k0, t0)| k0 != key || tick > t0 + ORDER_FRESH) {
            if let Some(k) = counted(format!("player {player} {key} order")) {
                wlog(format!("t={tick} player {player} {name} {key} ORDER: {why} #{k}"));
            }
        }
        self.last_order = Some((key, tick));
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (presses for the AI: Samira R, Twisted Fate R, Kog'Maw R, Camille E, Zed W, Gwen E, Viego E, Katarina W and R, Orianna E and R, Sivir E, Sona W, Zilean E, Kalista E, the R of Janna, Syndra, Xerath, Kayle, Jhin, Karma, Evelynn, Fiddlesticks, Ryze, Aphelios, Vladimir, Swain and Renata; held champions attack: all {} League champions, the {} melee within {}, the ranged within their own attack range; nothing while casting or moved) loaded: game {}.{}.{} abi {} log={} ===",
        ATTACK_RANGE.len(),
        ATTACK_RANGE.iter().filter(|(_, r)| *r <= MELEE_RANGE).count(),
        HOLD_REACH,
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(UltPress::default());
    host.log(LogLevel::Info, "league_ult_press loaded (presses the slots game 0.6.4's AI hardly presses, for 24 heroes; breaks holds for every champion).");
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

    fn u(id: usize, x: f64, y: f64, hp: f64) -> Unit {
        Unit { id, at: (x, y), hp }
    }

    #[test]
    fn the_hold_reach_follows_her_range_buffs() {
        assert_eq!(hold_reach_with(KAYLE, 0.0), hold_reach(KAYLE));
        assert_eq!(hold_reach_with(KAYLE, 27_500.0), (52_500.0, 62_500.0));
        assert_eq!(hold_reach_with(KAYLE, 37_500.0), (62_500.0, 72_500.0));
    }

    #[test]
    fn samira_and_camille_press_on_the_nearest_in_range() {
        let enemies = [u(1, 40_000.0, 0.0, 1.0), u(2, 20_000.0, 0.0, 1.0), u(3, 60_000.0, 0.0, 1.0)];
        assert_eq!(nearest_in((0.0, 0.0), SAMIRA_RANGE, &enemies), Some(2));
        assert_eq!(nearest_in((0.0, 0.0), SAMIRA_RANGE, &[u(3, 60_000.0, 0.0, 1.0)]), None); // out of R's range
        assert_eq!(nearest_in((0.0, 0.0), CAMILLE_RANGE, &[u(3, 60_000.0, 0.0, 1.0)]), Some(3)); // E reaches 60000
        assert_eq!(nearest_in((0.0, 0.0), SAMIRA_RANGE, &[]), None);
    }

    #[test]
    fn twisted_fate_presses_only_alone_with_a_fight_far_away() {
        let allies = [u(10, 200_000.0, 0.0, 1.0)];
        let fight = [u(20, 230_000.0, 0.0, 1.0)];
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &fight), Some((20, 10)));
        // an enemy champion next to him
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &[u(20, 230_000.0, 0.0, 1.0), u(21, 60_000.0, 0.0, 1.0)]), None);
        // low on health
        assert_eq!(tf_fight((0.0, 0.0), 0.3, &allies, &fight), None);
        // the ally is not fighting (the enemy 80000 from him)
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &[u(20, 280_000.0, 0.0, 1.0)]), None);
        // the fight is out of R's reach
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &[u(10, 400_000.0, 0.0, 1.0)], &[u(20, 420_000.0, 0.0, 1.0)]), None);
        // the ally is close by: no need to teleport
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &[u(10, 80_000.0, 0.0, 1.0)], &[u(20, 110_000.0, 0.0, 1.0)]), None);
    }

    #[test]
    fn twisted_fate_picks_the_nearest_fight() {
        let allies = [u(10, 300_000.0, 0.0, 1.0), u(11, 0.0, 150_000.0, 1.0)];
        let enemies = [u(20, 320_000.0, 0.0, 1.0), u(21, 0.0, 170_000.0, 1.0)];
        assert_eq!(tf_fight((0.0, 0.0), 1.0, &allies, &enemies), Some((21, 11)));
    }

    #[test]
    fn samira_weaves_r_then_e_then_q() {
        let one = [u(1, 40_000.0, 0.0, 1.0)];
        // all ready, one champion at 40000: R first (fires at S, else arms), then E, then Q
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [true, true, true], false, &one), vec![('R', 1), ('E', 1), ('Q', 1)]);
        // the last hit was a Q: another Q would not climb
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [true, true, false], true, &one), vec![('E', 1)]);
        // low on health: no dash in
        assert_eq!(samira_plan((0.0, 0.0), 0.3, [true, true, false], false, &one), vec![('Q', 1)]);
        // three champions around the target: no dash into them
        let crowd = [u(1, 40_000.0, 0.0, 1.0), u(2, 60_000.0, 0.0, 1.0), u(3, 50_000.0, 20_000.0, 1.0)];
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [false, true, false], false, &crowd), vec![]);
        // out of E's reach (65000), in Q's (70000)
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [true, true, true], false, &[u(1, 65_000.0, 0.0, 1.0)]), vec![('Q', 1)]);
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [true, true, true], false, &[]), vec![]);
    }

    #[test]
    fn a_held_melee_champion_attacks_only_when_safe() {
        let lane = [u(1, 29_000.0, 0.0, 0.9)];
        // the lane opponent 29k away, she is healthy, no tower, 1 v 1: attack him
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &lane, &[], (HOLD_REACH, HOLD_KEEP), None), Some(1));
        // low on health
        assert_eq!(hold_target((0.0, 0.0), 0.4, &[], &lane, &[], (HOLD_REACH, HOLD_KEEP), None), None);
        // he stands under his tower
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &lane, &[(90_000.0, 0.0)], (HOLD_REACH, HOLD_KEEP), None), None);
        // two enemy champions round him and she is alone; with an ally by her it is even
        let two = [u(1, 29_000.0, 0.0, 0.9), u(2, 60_000.0, 0.0, 0.9)];
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &two, &[], (HOLD_REACH, HOLD_KEEP), None), None);
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[u(9, -10_000.0, 0.0, 1.0)], &two, &[], (HOLD_REACH, HOLD_KEEP), None), Some(1));
        // out of reach (40k); the one she is on is kept up to 45k
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &[u(1, 40_000.0, 0.0, 0.9)], &[], (HOLD_REACH, HOLD_KEEP), None), None);
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &[u(1, 40_000.0, 0.0, 0.9)], &[], (HOLD_REACH, HOLD_KEEP), Some(1)), Some(1));
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &[u(1, 50_000.0, 0.0, 0.9)], &[], (HOLD_REACH, HOLD_KEEP), Some(1)), None);
        // a ranged champion (Draven, 55000): the lane opponent 50k off is in reach, 60k off is not unless she is on him
        let ranged = hold_reach("league_draven");
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &[u(1, 50_000.0, 0.0, 0.9)], &[], ranged, None), Some(1));
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &[u(1, 60_000.0, 0.0, 0.9)], &[], ranged, None), None);
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &[u(1, 60_000.0, 0.0, 0.9)], &[], ranged, Some(1)), Some(1));
        assert_eq!(hold_target((0.0, 0.0), 0.8, &[], &[u(1, 70_000.0, 0.0, 0.9)], &[], ranged, Some(1)), None);
    }

    #[test]
    fn the_ai_holds_her_with_no_order_or_a_walk_to_her_own_spot() {
        assert!(holding(None, (100_000.0, 100_000.0)));
        assert!(holding(Some(InputV1::move_to(101_000, 100_000)), (100_000.0, 100_000.0)));
        assert!(!holding(Some(InputV1::move_to(130_000, 100_000)), (100_000.0, 100_000.0)));
        assert!(!holding(Some(InputV1::action(InputKindV1::Attack, InputTargetV1::target(3))), (100_000.0, 100_000.0)));
    }

    #[test]
    fn kogmaw_paces_his_volleys() {
        let full = [(0.9, false)];
        // a volley open: keep firing whatever is saved
        assert_eq!(kog_pick(true, 0.0, &full), Some((0, "volley open")));
        // nothing saved: no new volley
        assert_eq!(kog_pick(false, 0.7, &[(0.2, true)]), None);
        // one saved: only at a good moment
        assert_eq!(kog_pick(false, 1.0, &full), None);
        assert_eq!(kog_pick(false, 1.0, &[(0.4, false)]), Some((0, "low health")));
        assert_eq!(kog_pick(false, 1.0, &[(0.8, false), (0.9, true)]), Some((1, "in crowd control")));
        assert_eq!(kog_pick(false, 1.0, &[(0.8, false), (0.9, false)]), Some((0, "two or more in reach")));
        // saved up: any target
        assert_eq!(kog_pick(false, KOG_VOLLEYS_MAX, &full), Some((0, "volleys saved up")));
        // nobody the engine takes
        assert_eq!(kog_pick(true, 2.0, &[]), None);
    }

    #[test]
    fn kogmaw_asks_the_lowest_first_within_range() {
        let enemies = [u(1, 50_000.0, 0.0, 0.8), u(2, 120_000.0, 0.0, 0.3), u(3, 140_000.0, 0.0, 0.1), u(4, 10_000.0, 0.0, 0.5)];
        // #3 is lowest but out of range
        assert_eq!(kog_targets((0.0, 0.0), &enemies), vec![2, 4, 1]);
        assert!(kog_targets((0.0, 0.0), &[u(3, 140_000.0, 0.0, 0.1)]).is_empty());
        let many: Vec<Unit> = (0..8).map(|i| u(i, 1_000.0 * i as f64, 0.0, 1.0 - 0.1 * i as f64)).collect();
        assert_eq!(kog_targets((0.0, 0.0), &many).len(), KOG_ASK);
    }

    #[test]
    fn attack_ranges_match_the_data() {
        // every hero of the main pack with its attack range, and nothing else: a new hero fails this until it is added to
        // ATTACK_RANGE (the engine's API cannot read an attack range at run time)
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../league/champion");
        let mut found = Vec::new();
        for entry in std::fs::read_dir(&dir).expect("league/champion") {
            let path = entry.unwrap().path();
            if path.extension().and_then(|x| x.to_str()) != Some("data_champion") {
                continue;
            }
            let raw = std::fs::read_to_string(&path).unwrap().replace("\r\n", "\n");
            let raw = raw.trim_start_matches('\u{feff}');
            let id = raw
                .lines()
                .find_map(|l| l.strip_prefix("  \"id\": \""))
                .map(|r| r.trim_end_matches(',').trim_end_matches('"').to_string())
                .expect("id");
            let range: u64 = raw
                .lines()
                .skip_while(|l| *l != "  \"attack\": {")
                .skip(1)
                .take_while(|l| !l.starts_with("  }"))
                .find_map(|l| l.strip_prefix("    \"range\": "))
                .map(|r| r.trim_end_matches(',').parse().unwrap())
                .unwrap_or_else(|| panic!("no attack range in {}", path.display()));
            found.push((id, range));
        }
        assert!(found.len() > 100, "read only {} heroes from {}", found.len(), dir.display());
        found.sort();
        let mut listed: Vec<(String, u64)> = ATTACK_RANGE.iter().map(|&(n, r)| (n.to_string(), r)).collect();
        listed.sort();
        assert_eq!(listed, found, "ATTACK_RANGE must list every hero of league/champion with its attack range");
    }

    #[test]
    fn every_league_champion_is_held_within_its_reach() {
        for name in ["league_garen", "league_malphite", "league_rakan", "league_senna", "league_draven", "league_karma", CAMILLE] {
            assert!(is_holder(name), "{name}");
        }
        for name in ["priest", "monk", "league_nobody"] {
            assert!(!is_holder(name), "{name}");
        }
        // melee step up to HOLD_REACH; the ranged shoot from where they stand, within their own attack range
        assert_eq!(hold_reach("league_garen"), (HOLD_REACH, HOLD_KEEP));
        assert_eq!(hold_reach("league_draven"), (55_000.0, 65_000.0));
        assert_eq!(hold_reach("league_rakan"), (40_000.0, 50_000.0));
        assert_eq!(hold_reach("league_jinx"), (64_500.0, 74_500.0));
        assert_eq!(hold_reach("monk"), (HOLD_REACH, HOLD_KEEP));
    }
    #[test]
    fn a_walk_counts_unless_it_clearly_backs_off() {
        let (me, him) = ((0.0, 0.0), (30_000.0, 0.0));
        assert!(!walking_away(me, (40_000.0, 0.0), him)); // at him
        assert!(!walking_away(me, (0.0, 20_000.0), him)); // alongside: 36k from him, within 30k + HOLD_AWAY
        assert!(!walking_away(me, (-5_000.0, 0.0), him)); // a short step back
        assert!(walking_away(me, (-20_000.0, 0.0), him)); // backing off
        assert!(walking_away(me, (-15_000.0, -15_000.0), him)); // backing off on a slant
    }

    /// A scene at the origin: he is #100 with `hp`.
    fn scene<'a>(hp: f64, allies: &'a [Unit], enemies: &'a [Unit], towers: &'a [(f64, f64)], held: &'a [usize]) -> Scene<'a> {
        Scene { me: (0.0, 0.0), id: 100, hp, allies, enemies, towers, held }
    }

    #[test]
    fn engage_picks_the_lowest_safe_target_in_range() {
        // #1 and #2 on either side of him (70k apart: each alone); #3 is out of W's range
        let foes = [u(1, 30_000.0, 0.0, 0.9), u(2, -40_000.0, 0.0, 0.5), u(3, 70_000.0, 0.0, 0.1)];
        // #2 is lower than #1
        assert_eq!(engage_targets(&scene(0.8, &[], &foes[..2], &[], &[]), ZED_W_RANGE), vec![2, 1]);
        assert_eq!(engage_targets(&scene(0.8, &[], &[foes[2]], &[], &[]), ZED_W_RANGE), Vec::<usize>::new());
        // too hurt to go in
        assert!(engage_targets(&scene(0.3, &[], &foes, &[], &[]), ZED_W_RANGE).is_empty());
        // under his tower only when nearly dead
        let tower = [(40_000.0, 50_000.0)];
        assert_eq!(engage_targets(&scene(0.8, &[], &[u(2, 40_000.0, 0.0, 0.5)], &tower, &[]), ZED_W_RANGE), Vec::<usize>::new());
        assert_eq!(engage_targets(&scene(0.8, &[], &[u(2, 40_000.0, 0.0, 0.2)], &tower, &[]), ZED_W_RANGE), vec![2]);
        // two of them together against him alone: no; with an ally by him: yes
        let pair = [u(1, 40_000.0, 0.0, 0.6), u(2, 45_000.0, 10_000.0, 0.7)];
        assert!(engage_targets(&scene(0.8, &[], &pair, &[], &[]), ZED_W_RANGE).is_empty());
        assert_eq!(engage_targets(&scene(0.8, &[u(9, 5_000.0, 0.0, 1.0)], &pair, &[], &[]), ZED_W_RANGE), vec![1, 2]);
    }

    #[test]
    fn katarina_spins_on_two_or_a_low_one() {
        let one = [u(1, 20_000.0, 0.0, 0.8)];
        assert!(katarina_r(&scene(0.8, &[], &one, &[], &[])).is_empty()); // one healthy champion
        assert_eq!(katarina_r(&scene(0.8, &[], &[u(1, 20_000.0, 0.0, 0.4)], &[], &[])), vec![1]); // a low one
        let two = [u(1, 20_000.0, 0.0, 0.8), u(2, 45_000.0, 0.0, 0.9)];
        assert_eq!(katarina_r(&scene(0.8, &[], &two, &[], &[])), vec![1]); // #2 in the ring, not in reach
        assert!(katarina_r(&scene(0.2, &[], &two, &[], &[])).is_empty()); // too hurt
        assert!(katarina_r(&scene(0.8, &[], &two, &[(0.0, 60_000.0)], &[])).is_empty()); // she stands under a tower
        assert!(katarina_r(&scene(0.8, &[], &[u(1, 28_000.0, 0.0, 0.3)], &[], &[])).is_empty()); // out of reach
    }

    #[test]
    fn fiddlesticks_drops_on_the_biggest_crowd() {
        let foes = [u(1, 60_000.0, 0.0, 0.9), u(2, 70_000.0, 10_000.0, 0.8), u(3, 30_000.0, -40_000.0, 0.9)];
        // #1 and #2 stand together; #2 is lower
        assert_eq!(fiddle_r(&scene(0.8, &[u(9, 40_000.0, 0.0, 1.0)], &foes, &[], &[])), Some((2, (70_000.0, 10_000.0), 2)));
        // a lone healthy one: no; a lone low one: yes
        assert_eq!(fiddle_r(&scene(0.8, &[], &[foes[2]], &[], &[])), None);
        assert_eq!(fiddle_r(&scene(0.8, &[], &[u(3, 30_000.0, -40_000.0, 0.3)], &[], &[])), Some((3, (30_000.0, -40_000.0), 1)));
        // under their tower, or him too hurt
        assert_eq!(fiddle_r(&scene(0.8, &[], &foes[..2], &[(80_000.0, 40_000.0)], &[])), None);
        assert_eq!(fiddle_r(&scene(0.3, &[], &foes[..2], &[], &[])), None);
        // three there against him alone (and nobody of his there)
        let three = [u(1, 60_000.0, 0.0, 0.9), u(2, 70_000.0, 10_000.0, 0.8), u(4, 75_000.0, -10_000.0, 0.9)];
        assert_eq!(fiddle_r(&scene(0.8, &[], &three, &[], &[])), None);
    }

    #[test]
    fn channels_only_from_safety_on_low_or_fought_targets() {
        let far = [u(1, 120_000.0, 0.0, 0.4), u(2, 100_000.0, 0.0, 0.9)];
        assert_eq!(channel_targets(&scene(0.8, &[], &far, &[], &[]), XERATH_R_REACH), vec![1]);
        // an ally fighting #2 makes it a target too (lowest first)
        let ally = [u(9, 90_000.0, 0.0, 0.7)];
        assert_eq!(channel_targets(&scene(0.8, &ally, &far, &[], &[]), XERATH_R_REACH), vec![1, 2]);
        // an enemy champion close to him: never
        let close = [u(1, 120_000.0, 0.0, 0.4), u(3, 30_000.0, 0.0, 1.0)];
        assert!(channel_targets(&scene(0.8, &[], &close, &[], &[]), XERATH_R_REACH).is_empty());
        // too hurt to stand still; out of reach
        assert!(channel_targets(&scene(0.3, &[], &far, &[], &[]), XERATH_R_REACH).is_empty());
        assert!(channel_targets(&scene(0.8, &[], &[u(1, 150_000.0, 0.0, 0.2)], &[], &[]), JHIN_R_REACH).is_empty());
    }

    #[test]
    fn syndra_bursts_low_held_or_crowded() {
        assert!(syndra_r(&scene(0.8, &[], &[u(1, 50_000.0, 0.0, 0.9)], &[], &[])).is_empty());
        assert_eq!(syndra_r(&scene(0.8, &[], &[u(1, 50_000.0, 0.0, 0.5)], &[], &[])), vec![1]);
        assert_eq!(syndra_r(&scene(0.8, &[], &[u(1, 50_000.0, 0.0, 0.9)], &[], &[1])), vec![1]);
        let two = [u(1, 50_000.0, 0.0, 0.9), u(2, 60_000.0, 0.0, 0.8)];
        assert_eq!(syndra_r(&scene(0.8, &[], &two, &[], &[])), vec![2, 1]);
        assert!(syndra_r(&scene(0.8, &[], &[u(1, 80_000.0, 0.0, 0.1)], &[], &[])).is_empty()); // out of range
    }

    #[test]
    fn janna_heals_when_someone_is_about_to_fall() {
        let foe = [u(1, 30_000.0, 0.0, 1.0)];
        // nobody hurt
        assert!(janna_r(&scene(0.9, &[u(9, 20_000.0, 0.0, 0.8)], &foe, &[], &[])).is_empty());
        // an ally at 30% with the enemy on him: him first, then her
        assert_eq!(janna_r(&scene(0.9, &[u(9, 20_000.0, 0.0, 0.3)], &foe, &[], &[])), vec![9, 100]);
        // she herself at 30%
        assert_eq!(janna_r(&scene(0.3, &[], &foe, &[], &[])), vec![100]);
        // two at half health in a fight
        assert_eq!(janna_r(&scene(0.5, &[u(9, 20_000.0, 0.0, 0.55)], &foe, &[], &[])), vec![100, 9]);
        // the hurt ally is out of her heal; no enemy anywhere near
        assert!(janna_r(&scene(0.9, &[u(9, 50_000.0, 0.0, 0.2)], &foe, &[], &[])).is_empty());
        assert!(janna_r(&scene(0.3, &[], &[u(1, 90_000.0, 0.0, 1.0)], &[], &[])).is_empty());
    }

    #[test]
    fn sona_zilean_and_sivir_wait_for_their_moment() {
        let foe = [u(1, 60_000.0, 0.0, 1.0)];
        assert!(sona_w(&scene(0.9, &[u(9, 30_000.0, 0.0, 0.9)], &foe, &[], &[])).is_empty());
        assert_eq!(sona_w(&scene(0.9, &[u(9, 30_000.0, 0.0, 0.6)], &foe, &[], &[])), vec![1]);
        assert_eq!(sona_w(&scene(0.5, &[], &foe, &[], &[])), vec![1]);
        // Zilean: nobody in contact and nobody low -> nothing; an ally 30k from the enemy -> the slow on him
        assert!(zilean_e(&scene(0.9, &[], &foe, &[], &[])).is_empty());
        assert_eq!(zilean_e(&scene(0.9, &[u(9, 40_000.0, 0.0, 0.9)], &foe, &[], &[])), vec![1]);
        assert_eq!(zilean_e(&scene(0.9, &[], &[u(1, 60_000.0, 0.0, 0.3)], &[], &[])), vec![1]); // chase a low one
        // Sivir: a fresh cast within 60k, the caster first; desperate when low with one close
        let two = [u(1, 30_000.0, 0.0, 1.0), u(2, 55_000.0, 0.0, 1.0)];
        assert!(sivir_e(&scene(0.9, &[], &two, &[], &[]), &[]).is_empty());
        assert_eq!(sivir_e(&scene(0.9, &[], &two, &[], &[]), &[2]), vec![2, 1]);
        assert!(sivir_e(&scene(0.9, &[], &[u(2, 64_000.0, 0.0, 1.0)], &[], &[]), &[2]).is_empty()); // cast too far
        assert_eq!(sivir_e(&scene(0.3, &[], &two, &[], &[]), &[]), vec![1, 2]);
    }

    #[test]
    fn vladimir_clouds_a_low_one_or_two_together() {
        assert!(vladimir_r(&scene(0.8, &[], &[u(1, 40_000.0, 0.0, 0.9)], &[], &[])).is_empty());
        assert_eq!(vladimir_r(&scene(0.8, &[], &[u(1, 40_000.0, 0.0, 0.4)], &[], &[])), vec![1]);
        let two = [u(1, 40_000.0, 0.0, 0.9), u(2, 55_000.0, 10_000.0, 0.8)];
        assert_eq!(vladimir_r(&scene(0.8, &[], &two, &[], &[])), vec![2, 1]); // 18k apart: both in one cloud
        assert!(vladimir_r(&scene(0.8, &[], &[u(1, 65_000.0, 0.0, 0.1)], &[], &[])).is_empty()); // out of range
    }

    #[test]
    fn ryze_flees_low_or_joins_a_far_fight() {
        assert_eq!(ryze_r(&scene(0.3, &[], &[u(1, 40_000.0, 0.0, 1.0)], &[], &[])), Some((1, "low on health")));
        assert_eq!(ryze_r(&scene(0.3, &[], &[u(1, 90_000.0, 0.0, 1.0)], &[], &[])), None);
        let allies = [u(9, 200_000.0, 0.0, 1.0)];
        let fight = [u(1, 230_000.0, 0.0, 1.0)];
        assert_eq!(ryze_r(&scene(0.9, &allies, &fight, &[], &[])), Some((1, "an ally fights far away")));
        assert_eq!(ryze_r(&scene(0.9, &[], &fight, &[], &[])), None);
    }

    #[test]
    fn plan_follows_readiness_and_the_main_packs_marks() {
        let foe = [u(1, 40_000.0, 0.0, 0.5)];
        let s = scene(0.8, &[], &foe, &[], &[]);
        let marks = |zed_q_ready, kalista_rend| Marks { zed_q_ready, kalista_rend, fresh: Vec::new() };
        let keys = |v: Vec<Plan>| v.into_iter().map(|p| (p.key, p.slot, p.aim)).collect::<Vec<_>>();
        let all = [true; 4];
        // Zed's W only with Q ready, on his first skill slot
        assert_eq!(keys(plan(ZED, &s, all, &marks(true, false))), vec![("W", SkillSlotV1::Skill, Aim::Unit(1))]);
        assert!(plan(ZED, &s, all, &marks(false, false)).is_empty());
        assert!(plan(ZED, &s, [true, false, true, true], &marks(true, false)).is_empty());
        // Kalista's rend only with the spears' mark
        assert!(plan(KALISTA, &s, all, &marks(false, false)).is_empty());
        assert_eq!(keys(plan(KALISTA, &s, all, &marks(false, true))), vec![("E", SkillSlotV1::Skill2, Aim::Unit(1))]);
        // Orianna: R before E (E needs a fight: the enemy is 40k from her, within FIGHT_CONTACT)
        assert_eq!(
            keys(plan(ORIANNA, &s, all, &marks(false, false))),
            vec![("R", SkillSlotV1::Ult, Aim::Unit(1)), ("E", SkillSlotV1::Skill2, Aim::Unit(1))]
        );
        // armed ults press on anyone near; not when the slot is down
        assert_eq!(keys(plan(EVELYNN, &scene(0.8, &[], &[u(1, 40_000.0, 0.0, 1.0)], &[], &[]), all, &marks(false, false))).len(), 1);
        assert!(plan(KARMA, &s, [true, true, true, false], &marks(false, false)).is_empty());
        assert_eq!(keys(plan(APHELIOS, &s, all, &marks(false, false))), vec![("R", SkillSlotV1::Ult, Aim::Unit(1))]);
        // Swain arms the demon on anyone within the slot's range; not beyond it, not with R down
        assert_eq!(keys(plan(SWAIN, &s, all, &marks(false, false))), vec![("R", SkillSlotV1::Ult, Aim::Unit(1))]);
        assert!(plan(SWAIN, &scene(0.8, &[], &[u(1, 60_000.0, 0.0, 1.0)], &[], &[]), all, &marks(false, false)).is_empty());
        assert!(plan(SWAIN, &s, [true, true, true, false], &marks(false, false)).is_empty());
        // Renata arms the takeover the same way, within her slot's 75000
        assert_eq!(keys(plan(RENATA, &s, all, &marks(false, false))), vec![("R", SkillSlotV1::Ult, Aim::Unit(1))]);
        assert!(plan(RENATA, &scene(0.8, &[], &[u(1, 80_000.0, 0.0, 1.0)], &[], &[]), all, &marks(false, false)).is_empty());
        assert!(plan(RENATA, &s, [true, true, true, false], &marks(false, false)).is_empty());
        let low = [u(1, 40_000.0, 0.0, 0.4)];
        assert_eq!(keys(plan(VLADIMIR, &scene(0.8, &[], &low, &[], &[]), all, &marks(false, false))), vec![("R", SkillSlotV1::Ult, Aim::Unit(1))]);
        assert!(plan(VLADIMIR, &s, all, &marks(false, false)).is_empty()); // one at half health, alone: not yet
        // Fiddlesticks aims at the spot first, then at the unit
        let pair = [u(1, 60_000.0, 0.0, 0.9), u(2, 70_000.0, 10_000.0, 0.8)];
        let f = plan(FIDDLESTICKS, &scene(0.8, &[u(9, 40_000.0, 0.0, 1.0)], &pair, &[], &[]), all, &marks(false, false));
        assert_eq!(f.iter().map(|p| p.aim).collect::<Vec<_>>(), vec![Aim::Spot((70_000.0, 10_000.0)), Aim::Unit(2)]);
        assert!(f.iter().all(|p| p.dive));
        // 0.5.0: what waits while the AI walks away - the attacks; shields, heals and the escape do not
        let flag = |h: &str, sc: &Scene| plan(h, sc, all, &marks(false, true)).first().map(|p| p.dive);
        let near = [u(1, 20_000.0, 0.0, 0.4), u(2, 22_000.0, 3_000.0, 0.4)];
        assert_eq!(flag(KATARINA, &scene(0.8, &[], &near, &[], &[])), Some(true));
        for h in [SYNDRA, EVELYNN, APHELIOS, SWAIN, ORIANNA] {
            assert_eq!(flag(h, &scene(0.8, &[], &near, &[], &[])), Some(true), "{h}");
        }
        for h in [KAYLE, KARMA, RENATA, KALISTA] {
            assert_eq!(flag(h, &scene(0.8, &[], &near, &[], &[])), Some(false), "{h}");
        }
        assert_eq!(flag(RYZE, &scene(0.2, &[], &near, &[], &[])), Some(false)); // the escape
        // a hero this list does not know
        assert!(plan("league_garen", &s, all, &marks(true, true)).is_empty());
    }

    #[test]
    fn a_recall_lasts_until_the_ai_orders_something_else() {
        let ret = Some(InputV1::return_home());
        let walk = Some(InputV1::move_to(1, 2));
        assert!(still_recalling(false, ret));
        // the ticks between its orders: still recalling (0.4.x took them for standing still and attacked)
        assert!(still_recalling(true, None));
        assert!(!still_recalling(false, None));
        assert!(!still_recalling(true, walk));
        assert!(!still_recalling(true, Some(InputV1::action(InputKindV1::Attack, InputTargetV1::target(3)))));
    }

    #[test]
    fn each_pressed_hero_watches_its_slots() {
        assert_eq!(slots_of(ZED), &[PressSlot { slot: SkillSlotV1::Skill, key: "W" }]);
        assert_eq!(slots_of(ORIANNA).len(), 2);
        assert_eq!(slots_of(KATARINA).iter().map(|p| p.slot).collect::<Vec<_>>(), vec![SkillSlotV1::Ult, SkillSlotV1::Skill2]);
        for h in [SAMIRA, TF, KOGMAW, JANNA, SYNDRA, XERATH, KAYLE, JHIN, KARMA, EVELYNN, FIDDLESTICKS, RYZE, APHELIOS, VLADIMIR, SWAIN, RENATA] {
            assert_eq!(slots_of(h), &[P_R], "{h}");
        }
        for h in [CAMILLE, GWEN, VIEGO, SIVIR, ZILEAN, KALISTA] {
            assert_eq!(slots_of(h), &[P_E2], "{h}");
        }
        assert!(slots_of("league_garen").is_empty());
        assert!(is_armed_ult(KAYLE) && is_armed_ult(APHELIOS) && is_armed_ult(SWAIN) && is_armed_ult(RENATA) && !is_armed_ult(JANNA) && !is_armed_ult(VLADIMIR));
    }

    /// The action-level `"range"` of a slot in the main pack's data (four spaces in, like `melee_list_matches_the_data`).
    fn data_range(hero: &str, slot: &str) -> u64 {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join(format!("../../league/champion/{hero}.data_champion"));
        let raw = std::fs::read_to_string(&path).unwrap().replace("\r\n", "\n");
        let head = format!("  \"{slot}\": {{");
        raw.lines()
            .skip_while(|l| *l != head)
            .skip(1)
            .take_while(|l| !l.starts_with("  }"))
            .find_map(|l| l.strip_prefix("    \"range\": "))
            .map(|r| r.trim_end_matches(',').parse().unwrap())
            .unwrap_or_else(|| panic!("no {slot} range in {}", path.display()))
    }

    #[test]
    fn ranges_and_marks_match_the_data() {
        for (hero, slot, range) in [
            (ZED, "skill", ZED_W_RANGE),
            (GWEN, "skill2", GWEN_E_RANGE),
            (VIEGO, "skill2", VIEGO_E_RANGE),
            (KATARINA, "skill2", KATARINA_W_RANGE),
            (ORIANNA, "skill2", ORI_E_RANGE),
            (SIVIR, "skill2", SIVIR_E_RANGE),
            (SONA, "skill2", SONA_W_RANGE),
            (ZILEAN, "skill2", ZILEAN_E_RANGE),
            (KALISTA, "skill2", KALISTA_E_RANGE),
            (JANNA, "ult", JANNA_R_RANGE),
            (SYNDRA, "ult", SYNDRA_R_RANGE),
            (FIDDLESTICKS, "ult", FIDDLE_R_RANGE),
            (VLADIMIR, "ult", VLAD_R_RANGE),
            (SWAIN, "ult", SWAIN_R_NEAR),
            (RENATA, "ult", RENATA_R_NEAR),
        ] {
            assert_eq!(data_range(hero, slot) as f64, range, "{hero} {slot}");
        }
        // the shorter reaches stay inside the slot's range
        for (hero, reach) in [
            (KATARINA, KAT_R_REACH),
            (ORIANNA, ORI_R_NEAR),
            (XERATH, XERATH_R_REACH),
            (JHIN, JHIN_R_REACH),
            (KAYLE, KAYLE_R_NEAR),
            (KARMA, KARMA_R_NEAR),
            (EVELYNN, EVELYNN_R_NEAR),
            (RYZE, TF_REACH),
            (APHELIOS, APHELIOS_R_NEAR),
        ] {
            assert!(reach <= data_range(hero, "ult") as f64, "{hero}");
        }
        let has = |hero: &str, mark: &str| {
            let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join(format!("../../league/champion/{hero}.data_champion"));
            std::fs::read_to_string(path).unwrap().contains(&format!("\"{mark}\""))
        };
        assert!(has(ZED, ZED_Q_CD) && has(KALISTA, KALISTA_E_OK) && has(KALISTA, KALISTA_E_CD));
    }
}
