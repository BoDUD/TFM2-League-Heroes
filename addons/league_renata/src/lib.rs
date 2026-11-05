//! 烈娜塔附加包（用户 2026-10-17：「方案可以，全按推荐做（辅助、Util，布局 A，做扩展包，PPU 1.5）」）。主包保持纯数据；
//! `mod.override_info` 把主包的烈娜塔换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_renata.py 的 `native=1`
//! 生成：普攻照样挂印记但数据不再引爆、数据不再放 W、狂暴照样禁攻击禁技能但不带数据的「乱打一圈」，被动换成本包的
//! `league_renata:glasc`，普攻和大招的说明开头加【附加包】），本包把这三件事做成英雄联盟的样子：
//!
//! - **物尽其用**：队友真的出手打带印记的敌方英雄时引爆（league_braum 的做法：队友的普攻 / 技能冷却跳起来就是出手了；普攻看他身边
//!   最近的敌方单位是不是带印记的英雄，技能看他身边带印记的敌方英雄；POP_WAIT tick 后打中时还带着印记就引爆）：p_pop +
//!   p_pop_ap% 法强的魔法伤害、最大生命 p_pop_hp% 的真实伤害，去掉印记。主包的数据版是「印记附近有两个她这边的英雄就引爆」。
//! - **及时救难**（英雄联盟的规则）：她活着、W 不在冷却时每 WATCH tick 看一次，w_range 内的队友（不算她自己）身边 DANGER_NEAR 内
//!   有敌方英雄、又被硬控或生命不到 DANGER_HP，就挑生命比例最低的那个：攻速 +w_as%、移速 +w_ms%、w_t tick 不死（主包的 buff
//!   `league_renata_w_buff`，画面照主包）。期间受到致命伤害（生命到 1、身上没有别人有时限的「不死」——死歌、塞恩等一直挂着的被动护身
//!   `*_p_guard` / `*_rv_guard` 和基兰的符文不算，它们等她，她先救；0.2.0）就回满生命，再在 w_doom tick 内烧光；
//!   烧的时候不再不死，敌人照样打得死他（0.1.5 起，英雄联盟就是这样；以前这 3 秒打不死，参与击杀后还留着几乎满的血，看着像复活）；
//!   这期间他参与击杀（击杀或助攻数变多，和致命一击同一 tick 的也算）就止住，生命定在最大生命的 w_keep%（英雄联盟 20%），没参与就
//!   阵亡（算离他最近的敌方英雄的，附近没有敌方英雄才算最近的敌方单位；补刀照死歌的 FALL：清护盾、生命设 1、一刀 1001，再补，
//!   DOOM_SLACK 后设 0，真倒下才记 DOOMED）。烧到 1 血时别人的被动 / 基兰的倒流接手就放手（BURN HANDED OVER）。已在死后形态、放逐、停在
//!   1 血的队友不救。她阵亡时正在烧的：状态在他身上的 buff 名字里，效果队列的 `league_renata:burn` 接着烧（0.2.0）。主包的数据版是
//!   「不会阵亡、结束时回血」。
//! - **恶意收购**：被化学波扫中的敌方英雄（主包的 `league_renata_r_berserk`，数据已禁攻击、禁技能）真的转身打自己人：AI 钩子
//!   （`league_renata:berserk`，所有玩家）让他走向最近的队友，到 LASH_REACH 内就站住；本包按他自己的攻击间隔、用他自己的攻击力打那个
//!   队友，挥一下（Animation "attack"）、播主包的 r_lash_hit。这一下算烈娜塔出手（`deal_damage_typed` 的攻击者是她），和英雄联盟一样
//!   击杀、助攻记在她头上：0.6.4 引擎照收同队伤害（宿主不查阵营、只要两边实体还在就返回 true），可死者的击杀者取的是最近一次伤他的
//!   英雄，同队的人打死他，个人击杀、赏金和助攻就落到狂暴的那个敌人自己的玩家身上（只有团队比分照样记给死者的对面），0.1.0 的
//!   「算他自己的」就是这样。主包的数据版是「每 r_per 秒对身边的队友造成魔法伤害」。
//!
//! 引擎细节（反汇编 0.6.4，2026-10-17）：`deal_damage_typed` 只把伤害效果排进当 tick 的效果队列，返回 true 不代表已经扣血，出手后
//! 马上读生命读不到变化；击杀、助攻计数在单位死亡结算的那一步里加（和击杀记录、团队比分同一处），被动每 tick 读，及时救难的
//! w_doom tick 来得及。
//!
//! 被动在玩家身上、每份模拟各一份。她死了被动就不再每 tick 跑（2026-10-30 的日志：DEAD 之后到她复活那一 tick 一行都没有），
//! 所以及时救难在她阵亡时当场了结（`on_dead`）：还只是护着的，换成不带「不死」的同名 buff 跑完剩下的时间（攻速、移速照给，
//! 0.1.4 以前留着「不死」，她一死队友就白白不死到 5 秒结束）；已经在烧的，被救后参与过击杀就保住（生命定在 w_keep%），没参与就
//! 当场阵亡（以前会冻住：队友白拿着回满的血，等她复活那一刻才被判死，算在身边的小兵头上）。狂暴的挥打同样停到她复活。日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_renata.log`，每次启动游戏重写，上一次的留在 .prev.log：`POP`、`BAILOUT`、
//! `REFILL`、`BURNED`、`SAVED`、`DOOMED`、`LASH`，都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_renata";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_renata") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 物尽其用的印记（主包数据：她打中敌方英雄时挂上）。
pub const MARK: &str = "league_renata_p_mark";
/// 及时救难（主包数据的 buff 名：画面绑在它上面）。
pub const W_BUFF: &str = "league_renata_w_buff";
/// 狂暴（主包数据：化学波扫中的敌方英雄）。
pub const BERSERK: &str = "league_renata_r_berserk";

/// 每隔几 tick 看一次要不要放 W（主包的看守也是 15）。
const WATCH: usize = 15;
/// 烧到期这么多 tick 后才看到（中间没跑）：照样补刀，日志注明晚了多少（0.2.0；以前只撤掉不判死，她阵亡时被动停了——现在效果队列接着烧）。
const STALE: usize = 30;
/// 队友出手（冷却跳起）后多少 tick 算打中：普攻的前摇加飞行。
const POP_WAIT: usize = 10;
/// 普攻：他身边这么远内最近的敌方单位就是他打的；技能：这么远内带印记的敌方英雄。
const ATTACK_REACH: f64 = 75000.0;
const SKILL_REACH: f64 = 90000.0;
/// 队友危急：身边这么远内有敌方英雄，并且被硬控或生命比例不到 DANGER_HP。
const DANGER_NEAR: f64 = 60000.0;
const DANGER_HP: f64 = 0.45;
/// 狂暴：走向最近的队友（CHASE 内），到 LASH_REACH 内站住挥打；第一下在狂暴后 FIRST_SWING tick，攻击间隔读不到时 SWING。
const CHASE: f64 = 120000.0;
const LASH_REACH: f64 = 40000.0;
const FIRST_SWING: usize = 12;
const SWING: usize = 60;
const SWING_ANIM: u64 = 12;
/// 放不出技能的控制（她被控住时不放 W）；算「被硬控」的控制（league_milio 的表）。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];
const HARD: [CcKindV1; 6] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];
/// 同一句台词至少隔这么多 tick（主包的 vo_gap）。
const VO_GAP: usize = 600;

fn rn(name: &str) -> String {
    format!("{ID}_{name}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RENATA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_renata.log");
        }
    }
    PathBuf::from("league_renata.log")
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
const LOG_EVERY: usize = 50;

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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 印记的时长（日志用）。
    pub p_t: usize,
    /// 引爆：p_pop + p_pop_ap% 法强的魔法伤害，最大生命 p_pop_hp% 的真实伤害。
    pub p_pop: usize,
    pub p_pop_ap: usize,
    pub p_pop_hp: usize,
    /// 及时救难：冷却、时长、攻速、移速、找队友的距离、危急时的流失时长、她的施法动作。
    pub w_cd: usize,
    pub w_t: usize,
    pub w_as: usize,
    pub w_ms: usize,
    pub w_range: usize,
    pub w_r2: usize,
    pub fight_r: usize,
    pub w_anim: usize,
    pub w_doom: usize,
    /// 烧的时候参与击杀：生命定在最大生命的 w_keep%（英雄联盟 20%）。
    pub w_keep: usize,
    /// 狂暴的时长（主包数据管；日志用）。
    pub r_t: usize,
    pub r_per: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_t: 240,
            p_pop: 30,
            p_pop_ap: 20,
            p_pop_hp: 3,
            w_cd: 1500,
            w_t: 300,
            w_as: 40,
            w_ms: 20,
            w_range: 80000,
            w_r2: 60000,
            fight_r: 70000,
            w_anim: 18,
            w_doom: 180,
            w_keep: 20,
            r_t: 105,
            r_per: 30,
        }
    }
}

/// `{"p_pop":30,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "p_t" => p.p_t = v,
            "p_pop" => p.p_pop = v,
            "p_pop_ap" => p.p_pop_ap = v,
            "p_pop_hp" => p.p_pop_hp = v,
            "w_cd" => p.w_cd = v,
            "w_t" => p.w_t = v,
            "w_as" => p.w_as = v,
            "w_ms" => p.w_ms = v,
            "w_range" => p.w_range = v,
            "w_r2" => p.w_r2 = v,
            "fight_r" => p.fight_r = v,
            "w_anim" => p.w_anim = v,
            "w_doom" => p.w_doom = v,
            "w_keep" => p.w_keep = v,
            "r_t" => p.r_t = v,
            "r_per" => p.r_per = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

/// 一个她这边的英雄（不算她）：id、位置、生命比例、被硬控没有。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Ally {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: f64,
    pub held: bool,
}

/// 危急：身边 DANGER_NEAR 内有敌方英雄，并且被硬控或生命比例不到 DANGER_HP。
pub fn in_danger(a: &Ally, enemies: &[(f64, f64)]) -> bool {
    enemies.iter().any(|e| dist(a.at, *e) <= DANGER_NEAR) && (a.held || a.hp < DANGER_HP)
}

/// 她在 `me`：`reach` 内危急的队友里生命比例最低的那个。
pub fn pick_bailout(me: (f64, f64), reach: f64, allies: &[Ally], enemies: &[(f64, f64)]) -> Option<usize> {
    allies
        .iter()
        .filter(|a| dist(me, a.at) <= reach && in_danger(a, enemies))
        .min_by(|a, b| a.hp.total_cmp(&b.hp))
        .map(|a| a.id)
}

/// 危急流失：每 tick 掉多少（最大生命在 `doom` tick 内掉光，至少 1）。
pub fn drain_step(max: usize, doom: usize) -> usize {
    (max / doom.max(1)).max(1)
}

/// 烧的时候参与击杀：生命定在最大生命的 `keep`%（至少 1）。英雄联盟是「设为」20%，不是回复 20%：烧得还多时也降到这里。
pub fn kept_hp(max: usize, keep: usize) -> usize {
    (max * keep / 100).max(1)
}

/// 及时救难的 buff（主包的名字，画面绑在它上面）：攻速、移速，`undying` 只在致命一击之前给（之后烧的时候敌人打得死他）。
pub fn w_buff(p: &Params, ticks: usize, undying: bool) -> BuffV1 {
    let mut buff = BuffV1::timed(W_BUFF, ticks);
    buff.attack_speed_mult = p.w_as as i32;
    buff.move_speed_mult = p.w_ms as i32;
    buff.undying = undying;
    buff
}

/// 流失到头、没参与击杀的人算谁打死的：候选 (id, 距离, 是不是英雄) 里最近的敌方英雄，没有英雄才是最近的单位。
pub fn pick_doom_killer(cands: &[(usize, f64, bool)]) -> Option<usize> {
    let nearest = |champ_only: bool| {
        cands.iter().filter(|c| !champ_only || c.2).min_by(|a, b| a.1.total_cmp(&b.1)).map(|c| c.0)
    };
    nearest(true).or_else(|| nearest(false))
}

/// 队友这次出手是哪种：普攻冷却跳起（Some(true)）、技能冷却跳起（Some(false)）、没出手（None）。冷却跳起 = 比上一 tick 多 5 以上。
pub fn swung(was: (usize, usize, usize, usize), now: (usize, usize, usize, usize)) -> Option<bool> {
    if now.0 > was.0 + 5 {
        Some(true)
    } else if now.1 > was.1 + 5 || now.2 > was.2 + 5 || now.3 > was.3 + 5 {
        Some(false)
    } else {
        None
    }
}

/// Whether any buff on `id` passes `f`, read one at a time and stopping at the first: no Vec. Frenzy asks this for
/// every player every tick of every simulation; collecting the buffs into a Vec first was about half of all the time
/// league_addons took in the game's background simulations (2026-10-19 profile, 「游戏卡顿的原因是什么」).
fn any_buff(sim: &StableSim<'_>, id: usize, f: impl Fn(&BuffV1) -> bool) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| f(&b)))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    any_buff(sim, id, |b| b.name() == name)
}

/// 基兰的时光符文（league_zilean_rewind）：它等别人的「不死」，本包不等它（0.2.0：两个真救命的不互相等；救难先回满，符文留着，
/// 烧到 1 血时基兰再倒流）。
pub const ZILEAN_RUNE: &str = "league_zilean_r_rune";
/// 基兰倒流时的放逐 buff 的名字开头（`league_zilean_rw_hold:<heal>:<zilean>`）：不死、放逐，他已经被基兰接走了。
pub const ZILEAN_HOLD: &str = "league_zilean_rw_hold";
/// 别的附加包「死后变身」的形态（塞恩的尸体、死歌的灵体和倒下、艾尼维亚的蛋、扎克的一滩、扎恩的复活、石甲虫的碎块）：
/// 身在其中的人不救（救了就是真复活：塞恩的尸体回满），烧的时候进了这些形态就是「死进被动里」，本包放手。
pub const DEAD_FORMS: [&str; 7] = [
    "league_sion_p_zombie",
    "league_karthus_p_spirit",
    "league_karthus_p_fall",
    "league_anivia_egg_on",
    "league_zac_split_form",
    "league_zaahen_rv_hold",
    "tft_krug_p_shatter",
];

/// 别的附加包一直挂着的被动护身「不死」（名字以 `_p_guard` / `_rv_guard` 结尾：死歌、塞恩、艾尼维亚、扎克、扎恩、tft 的石甲虫）。它们
/// 自己的复活都等别人的「不死」先用掉，0.1.x 的救难也等它们：队友停在 1 血谁也不动，5 秒后救难「没用上」、他的被动才触发。
/// 英雄联盟里及时救难先救，所以本包不等它们。
pub fn passive_guard(name: &str) -> bool {
    name.ends_with("_p_guard") || name.ends_with("_rv_guard")
}

/// 这个 buff 是不是让及时救难让路的「不死」：不是本包的 W、不是被动护身、不是基兰的符文的「不死」（凯尔的大招、千珏的大招、
/// 索拉卡的护身等：让它们自己管，等它们过了再说）。
pub fn yields_to(name: &str, undying: bool) -> bool {
    undying && name != W_BUFF && !passive_guard(name) && name != ZILEAN_RUNE
}

/// 身上这些 buff（名字，带不带「不死」）里有没有让救难让路的。
pub fn other_undying_in(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(n, u)| yields_to(n, *u))
}

/// 这个 buff 是不是别人的「死后形态」（DEAD_FORMS，基兰的倒流）。
pub fn dead_form(name: &str) -> bool {
    DEAD_FORMS.contains(&name) || name.starts_with(ZILEAN_HOLD)
}

/// 烧的时候别人把他接走了吗：进了死后形态，或者挂上了让路的「不死」（基兰的倒流、死歌的灵体……他死进了别人的救命里，本包放手）。
pub fn taken_over(names_undying: &[(String, bool)]) -> Option<&str> {
    names_undying.iter().find(|(n, u)| dead_form(n) || yields_to(n, *u)).map(|(n, _)| n.as_str())
}

/// 这个队友救不救得了：选得中（放逐的不行）、生命在 1 以上（已经停在 1 血的是别人的「不死」在撑着）、不在死后形态里。
pub fn can_bail(targetable: bool, hp: usize, buff_names: &[String]) -> bool {
    targetable && hp > 1 && !buff_names.iter().any(|n| dead_form(n))
}

/// 身上有让救难让路的「不死」吗。
fn other_undying(sim: &StableSim<'_>, id: usize) -> bool {
    any_buff(sim, id, |b| yields_to(b.name(), b.undying))
}

fn buffs_of(sim: &StableSim<'_>, id: usize) -> Vec<(String, bool)> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| (b.name().to_string(), b.undying)).collect()
    })
}

/// 烧的状态，写在他身上的 buff 名字里（`league_renata_w_doom:<到期 tick>:<救下时的击杀 + 助攻>:<最大生命>:<补了几刀>:<算谁的>`）：
/// 她阵亡被动停了，排进效果队列的 `league_renata:burn` 每 tick 照样接着烧（0.2.0）。
pub const DOOM_STATE: &str = "league_renata_w_doom";
/// 烧完补刀：补了这么多 tick 还站着就把生命设成 0（死歌的 FALL_SLACK 的做法）。
pub const DOOM_SLACK: usize = 30;

/// 一次烧：到期的 tick、救下时的击杀 + 助攻、回满时的最大生命、补了几刀、算谁的（第一刀时定下）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Burn {
    pub until: usize,
    pub td: usize,
    pub full: usize,
    pub tries: usize,
    pub killer: usize,
}

impl Burn {
    pub fn name(&self) -> String {
        format!("{DOOM_STATE}:{}:{}:{}:{}:{}", self.until, self.td, self.full, self.tries, self.killer)
    }

    pub fn parse(name: &str) -> Option<Self> {
        let rest = name.strip_prefix(DOOM_STATE)?.strip_prefix(':')?;
        let mut it = rest.split(':').map(|x| x.parse::<usize>().ok());
        let b = Self { until: it.next()??, td: it.next()??, full: it.next()??, tries: it.next()??, killer: it.next()?? };
        it.next().is_none().then_some(b)
    }
}

/// 他身上的烧的状态（名字和解析出来的）。
fn burn_of(sim: &StableSim<'_>, id: usize) -> Option<(String, Burn)> {
    sim.get_entity(id).and_then(|e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find_map(|b| Burn::parse(b.name()).map(|p| (b.name().to_string(), p)))
    })
}

/// 把烧的状态写到他身上（旧的拿掉）。
fn put_burn(sim: &mut StableSim<'_>, id: usize, old: Option<&str>, b: &Burn) {
    if let Some(o) = old {
        sim.entity_remove_buff(id, o);
    }
    sim.add_buff(id, &BuffV1::timed(&b.name(), DOOM_SLACK + 2));
}

fn cc_left(e: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> usize {
    (0..e.cc_count())
        .filter_map(|i| e.cc_at(i))
        .filter(|c| kinds.iter().any(|k| k.code() == c.kind))
        .map(|c| c.tick as usize)
        .max()
        .unwrap_or(0)
}

fn hp_share((now, max): (usize, usize)) -> f64 {
    if max > 0 {
        now as f64 / max as f64
    } else {
        1.0
    }
}

/// 某个英雄的玩家：(玩家 id, 击杀 + 助攻)。
fn takedowns(sim: &StableSim<'_>, champion: usize) -> Option<(usize, usize)> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find_map(|pl| {
        let c = pl.champion()?;
        (c.id() == champion).then(|| (pl.id(), pl.kills() + pl.assists()))
    })
}

/// 离 `at` 最近的、`team` 以外的活着的可选中单位（不算塔），`reach` 以内：(id, 是不是英雄)。
fn nearest_foe(sim: &StableSim<'_>, team: usize, at: (f64, f64), reach: f64) -> Option<(usize, bool)> {
    let mut best: Option<(usize, bool, f64)> = None;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        let d = dist(at, fpos(u.pos()));
        if d <= reach && best.is_none_or(|b| d < b.2) {
            best = Some((u.id(), u.is_champion(), d));
        }
    }
    best.map(|b| (b.0, b.1))
}

/// 及时救难没保住的人（在 `team`、`at`）算谁打死的：`reach` 内最近的敌方英雄，没有就是最近的敌方单位（不算塔）。
fn doom_killer(sim: &StableSim<'_>, team: usize, at: (f64, f64), reach: f64) -> Option<usize> {
    let mut cands = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_tower() {
            continue;
        }
        let d = dist(at, fpos(u.pos()));
        if d <= reach {
            cands.push((u.id(), d, u.is_champion()));
        }
    }
    pick_doom_killer(&cands)
}

/// 离 `at` 最近的带印记的敌方英雄（`team` 以外），`reach` 以内。
fn nearest_marked(sim: &StableSim<'_>, team: usize, at: (f64, f64), reach: f64) -> Option<usize> {
    let mut best: Option<(usize, f64)> = None;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_champion() {
            continue;
        }
        let d = dist(at, fpos(u.pos()));
        if d <= reach && best.is_none_or(|b| d < b.1) && has_buff(sim, u.id(), MARK) {
            best = Some((u.id(), d));
        }
    }
    best.map(|b| b.0)
}

/// 狂暴的 `me` 最近的自己人（同队、活着、可选中、不是塔，英雄优先）：(id, 位置, 距离)，`reach` 以内。
fn nearest_friend(sim: &StableSim<'_>, me: usize, team: usize, at: (f64, f64), reach: f64) -> Option<(usize, (f64, f64), f64)> {
    let mut best: Option<(usize, (f64, f64), f64, bool)> = None;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.id() == me || u.team() != team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        let p = fpos(u.pos());
        let d = dist(at, p);
        if d > reach {
            continue;
        }
        let champ = u.is_champion();
        let better = match best {
            None => true,
            Some((_, _, bd, bc)) => (champ && !bc) || (champ == bc && d < bd),
        };
        if better {
            best = Some((u.id(), p, d, champ));
        }
    }
    best.map(|b| (b.0, b.1, b.2))
}

// ===================== 烧（被动驱动；她阵亡后由效果队列驱动） =====================

/// 一 tick 的烧（`me`：她活着时是她，日志和画面的出手人；她阵亡后 None，用他自己）。他死了：烧的时候被打死 `BURNED`，补刀之后死的
/// `DOOMED`（0.2.0 起只在他真倒下时记）；参与击杀就止住，生命定在 w_keep%（`SAVED`）；别人把他接走了（进了死后形态、挂上让路的
/// 「不死」、选不中了）就放手（`BURN HANDED OVER`：他死进了死歌 / 塞恩 / 艾尼维亚的被动、基兰的倒流里，英雄联盟也这样算）；到期没参与
/// 就补刀：清护盾、生命设 1、算离他最近的敌方英雄的一刀 1001 真实伤害，下一 tick 还站着就再补（`DOOM RETRY`），`DOOM_SLACK` tick
/// 还不行就把生命设成 0（`DOOM FORCED`，死歌 FALL 的做法）。没到期就每 tick 扣最大生命的 1/w_doom（最低 1）。
/// 返回 None 就是结束了（状态 buff 已拿掉或他已不在）。
fn burn_tick(sim: &mut StableSim<'_>, me: Option<usize>, ally: usize, name: &str, mut b: Burn, now: usize, p: &Params)
             -> Option<Burn> {
    let caster = me.unwrap_or(ally);
    let line = head(sim, caster);
    let state = sim.get_entity(ally).map(|a| (a.is_alive(), a.hp(), fpos(a.pos()), a.team(), a.is_targetable()));
    let Some((true, (hp, max), at, team, targetable)) = state else {
        let gone = if state.is_none() { " (gone)" } else { "" };
        if b.tries > 0 {
            if let Some(k) = counted("doomed") {
                wlog(format!("{line} DOOMED #{k}: {name} got no takedown, killed by {} ({} blow{}){gone}", who(sim, b.killer),
                             b.tries, if b.tries == 1 { "" } else { "s" }));
            }
        } else if let Some(k) = counted("burned") {
            wlog(format!("{line} BURNED #{k}: {name} was killed while burning{gone}"));
        }
        return None;
    };
    let on = InputTargetV1::target(ally);
    let old = b.name();
    if takedowns(sim, ally).map_or(0, |t| t.1) > b.td {
        // a takedown stops the burn and sets his health to w_keep% (League: 20%) - not what was left of the refill,
        // which read as a revive
        let keep = kept_hp(b.full, p.w_keep);
        sim.entity_remove_buff(ally, W_BUFF);
        sim.entity_remove_buff(ally, &old);
        sim.entity_set_hp(ally, keep);
        sim.play_view_effect(&rn("w_save"), caster, &on, 0, 0, 0);
        sim.play_sfx(&rn("w_save"), caster, &on);
        if let Some(k) = counted("saved") {
            wlog(format!("{line} SAVED #{k}: {name} scored a takedown, {hp} -> {keep}/{max}"));
        }
        return None;
    }
    let list = buffs_of(sim, ally);
    let by = taken_over(&list).map(str::to_string).or_else(|| (!targetable).then(|| "banished".to_string()));
    if let Some(by) = by {
        sim.entity_remove_buff(ally, W_BUFF);
        sim.entity_remove_buff(ally, &old);
        if let Some(k) = counted("handed") {
            wlog(format!("{line} BURN HANDED OVER #{k}: {name} taken by {by} at {hp}/{max}{}", if b.tries > 0 {
                format!(" after {} blow(s)", b.tries)
            } else {
                String::new()
            }));
        }
        return None;
    }
    if now >= b.until {
        if b.tries >= DOOM_SLACK {
            let set = sim.entity_set_hp(ally, 0);
            if b.tries == DOOM_SLACK {
                if let Some(k) = counted("doom_forced") {
                    wlog(format!("{line} DOOM FORCED #{k}: {} blows by {} left {name} at {hp} hp - hp set to 0{}", b.tries,
                                 who(sim, b.killer), if set { "" } else { " (entity_set_hp refused)" }));
                }
            }
        } else {
            if b.tries == 0 {
                b.killer = doom_killer(sim, team, at, 200000.0).unwrap_or(ally);
                if now > b.until + STALE {
                    wlog(format!("{line} DOOM on {name} is {} ticks late", now - b.until));
                }
            } else if let Some(k) = counted("doom_retry") {
                wlog(format!("{line} DOOM RETRY #{k}: blow {} by {} did not take {name} - {hp} hp, undying {:?}", b.tries,
                             who(sim, b.killer), list.iter().filter(|(_, u)| *u).map(|(n, _)| n.as_str()).collect::<Vec<_>>()));
            }
            // sure to kill, like Karthus's fall: no shield, 1 hp, then a blow of 1001 (a shield or a damage reduction
            // used to absorb `hp + 1000`, and DOOMED was logged all the same)
            sim.entity_clear_shield(ally);
            sim.entity_set_hp(ally, 1);
            if !sim.deal_damage_typed(b.killer, ally, 1001, DamageTypeV1::Fixed, AttackTypeV1::Skill) {
                if let Some(k) = counted("doom_refused") {
                    wlog(format!("{line} DOOM BLOW REFUSED #{k}: deal_damage_typed by {} on {name}", who(sim, b.killer)));
                }
            }
        }
        b.tries += 1;
        put_burn(sim, ally, Some(&old), &b);
        return Some(b);
    }
    sim.entity_set_hp(ally, hp.saturating_sub(drain_step(b.full, p.w_doom)).max(1));
    put_burn(sim, ally, Some(&old), &b);
    Some(b)
}

/// 把 `league_renata:burn` 排到下一 tick，出手人是他自己（她可能已经不在了）。
fn queue_burn(sim: &mut StableSim<'_>, ally: usize) {
    let name = format!("{ID}:burn");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, ally, &InputTargetV1::target(ally), 1) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, ally)));
    }
}

/// 效果队列里的烧（她阵亡后）：读他身上的状态 buff，跑一 tick，没完就再排一次。参数读不到她的（她不在了），用默认的 w_doom / w_keep
/// （主包的数字就是默认值，`the_copy_carries_the_default_params`）。
struct BurnOn;

impl StableEffectType for BurnOn {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, ally: usize, _: InputTargetV1) {
        let now = sim.tick();
        let Some((_, burn)) = burn_of(sim, ally) else {
            let state = sim.get_entity(ally).map(|a| a.is_alive());
            if state != Some(true) {
                // he is dead or gone, and his buffs with him: the end of the burn, no more to say than that
                wlog(format!("[t={now}] BURN ended: #{ally} is {} (Renata dead; killed while burning or by the doom)",
                             if state.is_none() { "gone" } else { "dead" }));
            }
            return;
        };
        let who_ = who(sim, ally);
        if burn_tick(sim, None, ally, &who_, burn, now, &Params::default()).is_some() {
            queue_burn(sim, ally);
        }
    }
}

// ===================== 被动：杠杆（引爆、救难、狂暴） =====================

/// 一次及时救难：队友（和他的名字：他死后实体多半下一 tick 就没了，日志照样写得出是谁）、结束的 tick、上一 tick 他的击杀 + 助攻
/// （致命一击那一 tick 的击杀也算参与），被救下后的烧（`Burn`，同时写在他身上的 buff 名字里）。
#[derive(Clone, Debug)]
struct Bail {
    ally: usize,
    name: String,
    until: usize,
    td_last: usize,
    doom: Option<Burn>,
}

#[derive(Clone, Default)]
struct Glasc {
    p: Params,
    /// 她这边各玩家上一 tick 的冷却（普攻、技能、技能 2、大招）。
    last_cd: HashMap<usize, (usize, usize, usize, usize)>,
    /// 等着算打中的出手：(队友, 敌方英雄, 第几 tick)。
    pending: Vec<(usize, usize, usize)>,
    /// W 好了的 tick；正在救的人。
    w_ready: usize,
    bail: Option<Bail>,
    /// 狂暴的敌方英雄 -> 下一下挥打的 tick。
    lash: HashMap<usize, usize>,
    /// 上次说 W 台词的 tick。
    vo_at: Option<usize>,
    was_alive: bool,
}

impl Glasc {
    /// 队友出手：冷却跳起来就记下他要打的带印记英雄，POP_WAIT tick 后还带着印记就引爆。
    fn ally_hits(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, now: usize) {
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            let pid = pl.id();
            let Some(c) = pl.champion() else { continue };
            if c.team() != team || c.id() == me {
                continue;
            }
            let Some(cd) = pl.cooldowns() else { continue };
            let was = self.last_cd.insert(pid, cd);
            let (Some(was), true) = (was, c.is_alive()) else { continue };
            let at = fpos(c.pos());
            let foe = match swung(was, cd) {
                Some(true) => match nearest_foe(sim, team, at, ATTACK_REACH) {
                    Some((f, true)) if has_buff(sim, f, MARK) => Some(f),
                    _ => None,
                },
                Some(false) => nearest_marked(sim, team, at, SKILL_REACH),
                None => None,
            };
            if let Some(f) = foe {
                if !self.pending.iter().any(|&(_, pf, _)| pf == f) {
                    self.pending.push((c.id(), f, now + POP_WAIT));
                }
            }
        }
        let due: Vec<(usize, usize, usize)> = self.pending.iter().copied().filter(|&(_, _, at)| at <= now).collect();
        self.pending.retain(|&(_, _, at)| at > now);
        for (ally, foe) in due.into_iter().map(|(a, f, _)| (a, f)) {
            if sim.get_entity(foe).is_some_and(|e| e.is_alive()) && has_buff(sim, foe, MARK) {
                self.pop(sim, me, foe, ally);
            }
        }
    }

    fn pop(&mut self, sim: &mut StableSim<'_>, me: usize, foe: usize, ally: usize) {
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let max = sim.get_entity(foe).map_or(0, |e| e.hp().1);
        let magic = self.p.p_pop + self.p.p_pop_ap * ap / 100;
        let fixed = (max * self.p.p_pop_hp / 100).max(1);
        sim.entity_remove_buff(foe, MARK);
        let a = sim.deal_damage_typed(me, foe, magic, DamageTypeV1::Ap, AttackTypeV1::Skill);
        let b = sim.deal_damage_typed(me, foe, fixed, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        let on = InputTargetV1::target(foe);
        sim.play_view_effect(&rn("p_pop"), me, &on, 0, 0, 0);
        sim.play_sfx(&rn("p_pop"), me, &on);
        if let Some(k) = counted("pop") {
            wlog(format!("{} POP #{k}: {} hit {} -> {magic} magic + {fixed} true{}", head(sim, me), who(sim, ally),
                         who(sim, foe), if a && b { "" } else { " (refused)" }));
        }
    }

    /// 及时救难：救着人时管流失和保命；没在救、W 好了时每 WATCH tick 找危急的队友。
    fn bailout(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, now: usize) {
        if let Some(b) = self.bail.take() {
            self.bail = self.keep_bail(sim, me, b, now);
            return;
        }
        if now < self.w_ready || now % WATCH != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() || cc_left(&e, &NO_CAST) > 0 {
            return;
        }
        let at = fpos(e.pos());
        let mut allies = Vec::new();
        let mut enemies = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_champion() || !u.is_alive() {
                continue;
            }
            if u.team() != team {
                enemies.push(fpos(u.pos()));
            } else if u.id() != me {
                // not a zombie Sion, a Karthus spirit, an egg, a puddle, a banished man or one already held at 1 hp by
                // someone else's undying (0.2.0: a Bailout on those read as a real revive, or was wasted)
                let names: Vec<String> = buffs_of(sim, u.id()).into_iter().map(|(n, _)| n).collect();
                if !can_bail(u.is_targetable(), u.hp().0, &names) {
                    continue;
                }
                allies.push(Ally { id: u.id(), at: fpos(u.pos()), hp: hp_share(u.hp()), held: cc_left(&u, &HARD) > 0 });
            }
        }
        let Some(ally) = pick_bailout(at, self.p.w_range as f64, &allies, &enemies) else { return };
        sim.add_buff(ally, &w_buff(&self.p, self.p.w_t, true));
        let on = InputTargetV1::target(ally);
        let at_me = InputTargetV1::target(me);
        sim.play_view_effect(&rn("w_cast"), me, &on, 0, 0, 0);
        sim.play_sfx(&rn("w"), me, &at_me);
        sim.play_sfx(&rn("w_buff"), me, &on);
        if self.vo_at.is_none_or(|t| now >= t + VO_GAP) {
            sim.play_sfx(&rn("vo_w"), me, &at_me);
            self.vo_at = Some(now);
        }
        let mut anim = CcV1::of_kind(CcKindV1::Animation, self.p.w_anim as u64);
        anim.set_name("skill_w");
        sim.apply_cc(me, &anim);
        self.w_ready = now + self.p.w_cd;
        let td_last = takedowns(sim, ally).map_or(0, |t| t.1);
        self.bail = Some(Bail { ally, name: who(sim, ally), until: now + self.p.w_t, td_last, doom: None });
        if let Some(k) = counted("bailout") {
            let a = allies.iter().find(|a| a.id == ally).copied().unwrap_or_default();
            wlog(format!("{} BAILOUT #{k} on {} (hp {:.0}%{})", head(sim, me), who(sim, ally), a.hp * 100.0,
                         if a.held { ", held" } else { "" }));
        }
    }

    /// 一 tick 的救难。护着的时候：生命到 1、身上没有让路的「不死」就回满、开始烧（先看生命再看到期：到期那一 tick 的致命一击也救）；
    /// 到期没出事就结束。烧的时候交给 `burn_tick`（她阵亡后排进效果队列的 `league_renata:burn` 接着跑同一段）。
    fn keep_bail(&mut self, sim: &mut StableSim<'_>, me: usize, mut b: Bail, now: usize) -> Option<Bail> {
        if let Some(burn) = b.doom {
            return burn_tick(sim, Some(me), b.ally, &b.name, burn, now, &self.p).map(|burn| Bail { doom: Some(burn), ..b });
        }
        let ally = sim.get_entity(b.ally).map(|a| (a.is_alive(), a.hp().0));
        let Some((true, hp)) = ally else {
            // dead, or gone: a dead champion's entity is usually gone by the next tick - that ended a bailout with no line
            // at all (0.1.6, 2026-11-03 night logs: `REFILL #1: league_kindred caught at 1 hp ...` and then nothing)
            wlog(format!("{} BAILOUT ended: {} died anyway{}", head(sim, me), b.name, if ally.is_none() { " (gone)" } else { "" }));
            return None;
        };
        if hp <= 1 && !other_undying(sim, b.ally) {
            // the lethal hit (0.2.0: checked before the end of the 5 s, and another add-on's permanent passive guard no
            // longer makes her wait - League's order is Bailout first, the passive keeps for later)
            let burn = self.refill(sim, me, &b, now, "");
            return Some(Bail { doom: Some(burn), ..b });
        }
        if now >= b.until {
            sim.entity_remove_buff(b.ally, W_BUFF);
            if let Some(k) = counted("unused") {
                wlog(format!("{} BAILOUT #{k} on {} ended unused{}", head(sim, me), who(sim, b.ally),
                             if hp <= 1 { " (held at 1 hp by someone else's undying)" } else { "" }));
            }
            return None;
        }
        b.td_last = takedowns(sim, b.ally).map_or(b.td_last, |t| t.1);
        Some(b)
    }

    /// 致命一击：回满，buff 换成不带「不死」的（烧的时候敌人照样打得死他：League "health is set back to full but they suffer a
    /// true damage burn"），烧的状态写到他身上。`note` 进日志（她阵亡那一 tick 救下的写明）。
    fn refill(&self, sim: &mut StableSim<'_>, me: usize, b: &Bail, now: usize, note: &str) -> Burn {
        let max = sim.get_entity(b.ally).map_or(0, |a| a.hp().1);
        let on = InputTargetV1::target(b.ally);
        sim.entity_set_hp(b.ally, max);
        sim.entity_remove_buff(b.ally, W_BUFF);
        sim.add_buff(b.ally, &w_buff(&self.p, self.p.w_doom + 2, false));
        sim.play_view_effect(&rn("w_save"), me, &on, 0, 0, 0);
        sim.play_sfx(&rn("w_save"), me, &on);
        // the count before this tick: a takedown on the lethal tick itself (a trade) still saves him
        let td = b.td_last;
        let td_now = takedowns(sim, b.ally).map_or(td, |t| t.1);
        let burn = Burn { until: now + self.p.w_doom, td, full: max, tries: 0, killer: b.ally };
        put_burn(sim, b.ally, None, &burn);
        if let Some(k) = counted("refill") {
            wlog(format!("{} REFILL #{k}: {} caught at 1 hp -> {max}, burns over {} ticks, killable ({td} takedowns \
                          before{}){note}",
                         head(sim, me), who(sim, b.ally), self.p.w_doom, if td_now > td { ", one on this tick" } else { "" }));
        }
        burn
    }

    /// 她阵亡：被动到她复活前不再跑。还只是护着的：这一 tick 正好是致命一击就照样救下（回满、开始烧），不然换成不带「不死」的同名
    /// buff 跑完剩下的时间（攻速、移速照给；留着「不死」没人管，队友就白白不死到 5 秒结束）。在烧的（和刚救下的）交给效果队列的
    /// `league_renata:burn` 接着烧到底（0.2.0；以前她一死就当场判定，没参与的当场阵亡）。
    fn bail_ends_with_her(&mut self, sim: &mut StableSim<'_>, me: Option<usize>) {
        let Some(mut b) = self.bail.take() else { return };
        let now = sim.tick();
        let line = me.map_or_else(|| format!("[t={now}]"), |m| head(sim, m));
        let ally = sim.get_entity(b.ally).map(|a| (a.is_alive(), a.hp().0));
        let Some((true, hp)) = ally else {
            // dead too (or gone): one line, as when she lives (0.1.6)
            wlog(format!("{line} BAILOUT ended: {} dead too (Renata died){}", b.name, if ally.is_none() { " (gone)" } else { "" }));
            return;
        };
        if b.doom.is_none() {
            if hp <= 1 && !other_undying(sim, b.ally) {
                let caster = me.unwrap_or(b.ally);
                b.doom = Some(self.refill(sim, caster, &b, now, " (Renata died this tick)"));
            } else {
                let left = b.until.saturating_sub(now);
                sim.entity_remove_buff(b.ally, W_BUFF);
                if left > 0 {
                    sim.add_buff(b.ally, &w_buff(&self.p, left, false));
                }
                if let Some(k) = counted("unused") {
                    wlog(format!("{line} BAILOUT #{k} on {}: Renata died, the last {left} ticks keep the speed without the save",
                                 who(sim, b.ally)));
                }
                return;
            }
        }
        queue_burn(sim, b.ally);
        wlog(format!("{line} BURN on {} goes on without her (Renata died)", b.name));
    }

    /// 狂暴的敌方英雄按自己的攻击间隔、用自己的攻击力打 LASH_REACH 内最近的自己人（走过去是 AI 钩子的事）；算她出手，击杀和助攻
    /// 记在她头上（英雄联盟的规则；引擎会把同队打死的击杀、赏金和助攻给狂暴的那个人自己）。
    fn berserk(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, now: usize) {
        let mut mad = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() != team && u.is_alive() && u.is_champion() && has_buff(sim, u.id(), BERSERK) {
                mad.push(u.id());
            }
        }
        self.lash.retain(|id, _| mad.contains(id));
        for u in mad {
            let next = *self.lash.entry(u).or_insert(now + FIRST_SWING);
            if now < next {
                continue;
            }
            let Some(e) = sim.get_entity(u) else { continue };
            let (st, interval, at, side) = (e.stat(), e.attack_interval(), fpos(e.pos()), e.team());
            let Some((victim, _, _)) = nearest_friend(sim, u, side, at, LASH_REACH) else { continue };
            // his attack, her hit: the engine credits a death to the last champion that hit the victim, team or not
            let dealt = sim.deal_damage_typed(me, victim, st.attack, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
            let mut anim = CcV1::of_kind(CcKindV1::Animation, SWING_ANIM);
            anim.set_name("attack");
            sim.apply_cc(u, &anim);
            sim.play_view_effect(&rn("r_lash_hit"), me, &InputTargetV1::target(victim), 0, 0, 0);
            self.lash.insert(u, now + if interval > 0 { interval } else { SWING });
            if let Some(k) = counted("lash") {
                wlog(format!("{} LASH #{k}: berserk {} hits its own {} for {} (credited to her){}{}", head(sim, me),
                             who(sim, u), who(sim, victim), st.attack, if dealt { "" } else { ", refused" },
                             if interval > 0 { String::new() } else { format!(", interval unknown -> {SWING}") }));
            }
        }
    }
}

impl StablePassive for Glasc {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        if self.p != p {
            if let Some(k) = counted("params") {
                wlog(format!("params {params_json} -> {p:?} #{k}"));
            }
            self.p = p;
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team) = (e.is_alive(), e.team());
        let now = sim.tick();
        if alive != self.was_alive {
            if let Some(k) = counted("life") {
                wlog(format!("{} {} #{k}", head(sim, me), if alive { "ALIVE" } else { "DEAD" }));
            }
            self.was_alive = alive;
        }
        self.ally_hits(sim, me, team, now);
        self.bailout(sim, me, team, now);
        self.berserk(sim, me, team, now);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        let me = sim.get_player(player).and_then(|p| p.champion()).map(|e| e.id());
        self.bail_ends_with_her(sim, me);
    }
}

// ===================== AI 钩子：狂暴的人走向自己人 =====================

/// 所有玩家都问：英雄身上有狂暴，就走向 CHASE 内最近的自己人，到 LASH_REACH 内站住（挥打是被动做的）；没有就不管。
#[derive(Clone, Default)]
struct Frenzy {
    last_log: Option<usize>,
}

impl StablePlayerAi for Frenzy {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:berserk")
    }

    fn priority(&self) -> i32 {
        1_000_000
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, _base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let sim = ctx.sim()?;
        let me = sim.get_player(player)?.champion()?;
        if !me.is_alive() || !has_buff(&sim, me.id(), BERSERK) {
            return None;
        }
        let at = fpos(me.pos());
        let (friend, to, d) = nearest_friend(&sim, me.id(), me.team(), at, CHASE)?;
        let now = sim.tick();
        if self.last_log.is_none_or(|t| now >= t + 60) {
            self.last_log = Some(now);
            if let Some(k) = counted("chase") {
                wlog(format!("{} BERSERK #{k}: {} goes for its own {} ({d:.0} away)", head(&sim, me.id()),
                             who(&sim, me.id()), who(&sim, friend)));
            }
        }
        if d <= LASH_REACH {
            Some(InputV1::move_to(at.0 as u64, at.1 as u64))
        } else {
            Some(InputV1::move_to(to.0 as u64, to.1 as u64))
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
        "=== {ID} v{VERSION} (Renata: Leverage popped by allies' hits, League's Bailout, a real berserk) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:glasc"), Glasc::default());
    module.add_native_effect(format!("{ID}:burn"), BurnOn);
    module.add_player_input_ai(Frenzy::default());
    host.log(LogLevel::Info, "league_renata loaded (Leverage popped by allies' hits, League's Bailout, a real berserk).");
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

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"p_pop":40,"junk":7,"w_doom":120,"w_cd":900,"fight_r":65000,"w_keep":25}"#);
        assert_eq!((p.p_pop, p.w_doom, p.w_cd, p.fight_r, p.w_keep), (40, 120, 900, 65000, 25));
    }

    #[test]
    fn the_copy_carries_the_default_params() {
        let copy = include_str!("../override/league_renata.data_champion");
        let at = copy.find("\"passive_ref\": \"league_renata:glasc\"").expect("no league_renata:glasc passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("p_t", d.p_t), ("p_pop", d.p_pop), ("p_pop_ap", d.p_pop_ap), ("p_pop_hp", d.p_pop_hp),
                       ("w_cd", d.w_cd), ("w_t", d.w_t), ("w_as", d.w_as), ("w_ms", d.w_ms), ("w_range", d.w_range),
                       ("w_r2", d.w_r2), ("fight_r", d.fight_r), ("w_anim", d.w_anim), ("w_doom", d.w_doom),
                       ("w_keep", d.w_keep), ("r_t", d.r_t), ("r_per", d.r_per)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in [MARK, W_BUFF, BERSERK] {
            assert!(copy.contains(&format!("\"name\": \"{name}\"")), "the copy has no {name}");
        }
        assert!(!copy.contains("league_renata_w_bolt"), "the copy still casts the data's Bailout");
        assert!(!copy.contains("league_renata_p_probe"), "the copy still pops the mark in data");
    }

    #[test]
    fn bailout_goes_to_the_ally_in_most_danger() {
        let me = (0.0, 0.0);
        let enemy = [(30000.0, 0.0)];
        let low = Ally { id: 1, at: (20000.0, 0.0), hp: 0.30, held: false };
        let lower_far = Ally { id: 2, at: (90000.0, 0.0), hp: 0.10, held: false };
        let held = Ally { id: 3, at: (25000.0, 5000.0), hp: 0.80, held: true };
        let fine = Ally { id: 4, at: (10000.0, 0.0), hp: 0.90, held: false };
        assert_eq!(pick_bailout(me, 80000.0, &[low, lower_far, held, fine], &enemy), Some(1));
        assert_eq!(pick_bailout(me, 80000.0, &[held, fine], &enemy), Some(3));
        assert_eq!(pick_bailout(me, 80000.0, &[fine], &enemy), None);
        // nobody near an enemy champion: no Bailout
        assert_eq!(pick_bailout(me, 80000.0, &[low], &[(200000.0, 0.0)]), None);
    }

    #[test]
    fn the_drain_empties_the_bar_in_time() {
        assert_eq!(drain_step(1800, 180), 10);
        assert_eq!(drain_step(100, 180), 1);
        assert_eq!(drain_step(1000, 0), 1000);
    }

    #[test]
    fn only_the_buff_before_the_lethal_hit_is_undying() {
        // 11-03 report 「她的W技能直接就把英雄复活了」: the refill kept undying, so for 3 s nothing could kill him
        let p = Params::default();
        let guard = w_buff(&p, p.w_t, true);
        let burn = w_buff(&p, p.w_doom + 2, false);
        assert!(guard.undying && !burn.undying);
        assert_eq!((burn.name(), burn.duration_tick), (W_BUFF, p.w_doom + 2));
        assert_eq!((burn.attack_speed_mult, burn.move_speed_mult), (p.w_as as i32, p.w_ms as i32));
    }

    #[test]
    fn a_takedown_sets_a_fifth_of_max_health() {
        // League: the burn stops and health is set to 20% of max - not what was left of the refill
        assert_eq!(kept_hp(1800, 20), 360);
        assert_eq!(kept_hp(2400, Params::default().w_keep), 480);
        assert_eq!(kept_hp(3, 20), 1);
        assert_eq!(kept_hp(0, 20), 1);
    }

    #[test]
    fn the_doom_is_credited_to_an_enemy_champion() {
        // a minion closer than the champions: the nearest champion gets the kill
        assert_eq!(pick_doom_killer(&[(7, 5000.0, false), (3, 90000.0, true), (4, 120000.0, true)]), Some(3));
        // no enemy champion near: the nearest unit
        assert_eq!(pick_doom_killer(&[(7, 5000.0, false), (8, 3000.0, false)]), Some(8));
        assert_eq!(pick_doom_killer(&[]), None);
    }

    #[test]
    fn an_ally_swings_when_a_cooldown_jumps() {
        assert_eq!(swung((0, 0, 0, 0), (60, 0, 0, 0)), Some(true));
        assert_eq!(swung((10, 0, 0, 0), (9, 0, 0, 0)), None);
        assert_eq!(swung((0, 0, 0, 0), (0, 300, 0, 0)), Some(false));
        assert_eq!(swung((0, 0, 0, 4), (0, 0, 0, 3000)), Some(false));
        assert_eq!(swung((5, 5, 5, 5), (9, 9, 9, 9)), None);
    }

    #[test]
    fn bailout_goes_first_before_the_passive_guards_and_the_rune() {
        // 11-05 review: Karthus / Sion / Anivia / Zac / Zaahen / Krug keep a permanent *_p_guard / *_rv_guard whose own
        // revive waits for other undying, and Zilean's rune waits too - waiting for them deadlocked the ally at 1 hp
        let l = |xs: &[(&str, bool)]| xs.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        for g in ["league_karthus_p_guard", "league_sion_p_guard", "league_anivia_p_guard", "league_zac_p_guard",
                  "league_zaahen_rv_guard", "tft_krug_p_guard"] {
            assert!(passive_guard(g), "{g}");
            assert!(!other_undying_in(&l(&[(g, true), (W_BUFF, true)])), "{g} must not hold the Bailout back");
        }
        assert!(!other_undying_in(&l(&[(ZILEAN_RUNE, true)])), "the rune waits for her, not she for it");
        // a real timed undying from someone else (Kindred's R, Kayle's R, Soraka's guard): hers waits for it
        assert!(other_undying_in(&l(&[("league_kindred_r_on", true), (W_BUFF, true)])));
        assert!(other_undying_in(&l(&[("league_soraka_w_guard", true)])));
        assert!(!other_undying_in(&l(&[("league_kindred_r_on", false), (W_BUFF, true)])));
        assert!(!passive_guard("league_renata_w_buff") && !passive_guard("league_sion_p_guardian"));
    }

    #[test]
    fn no_bailout_on_the_dead_forms_the_banished_or_the_held() {
        let n = |xs: &[&str]| xs.iter().map(|x| x.to_string()).collect::<Vec<_>>();
        assert!(can_bail(true, 300, &n(&["league_karthus_p_guard", "league_renata_p_mark"])));
        for f in DEAD_FORMS {
            assert!(!can_bail(true, 300, &n(&[f])), "{f} is a dead form");
            assert!(dead_form(f));
        }
        assert!(!can_bail(true, 300, &n(&["league_zilean_rw_hold:400:12"])));
        assert!(!can_bail(false, 300, &n(&[])), "banished");
        assert!(!can_bail(true, 1, &n(&[])), "already held at 1 hp by someone else's undying");
        assert!(!can_bail(true, 0, &n(&[])));
    }

    #[test]
    fn the_burn_lets_go_when_another_save_takes_him() {
        let l = |xs: &[(&str, bool)]| xs.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        assert_eq!(taken_over(&l(&[("league_karthus_p_guard", true), (W_BUFF, false)])), None);
        assert_eq!(taken_over(&l(&[("league_karthus_p_spirit", true)])), Some("league_karthus_p_spirit"));
        assert_eq!(taken_over(&l(&[("league_sion_p_zombie", false)])), Some("league_sion_p_zombie"));
        assert_eq!(taken_over(&l(&[("league_zilean_rw_hold:400:12", true)])), Some("league_zilean_rw_hold:400:12"));
        // the rune itself is not a takeover: it fires only when the burn (or an enemy) brings him to 1 hp
        assert_eq!(taken_over(&l(&[(ZILEAN_RUNE, true), (W_BUFF, false)])), None);
        assert_eq!(taken_over(&l(&[("league_kindred_r_on", true)])), Some("league_kindred_r_on"));
    }

    #[test]
    fn the_burn_state_survives_in_a_buff_name() {
        let b = Burn { until: 31095, td: 3, full: 2400, tries: 30, killer: 1234 };
        let name = b.name();
        assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        assert_eq!(Burn::parse(&name), Some(b));
        assert_eq!(Burn::parse("league_renata_w_doom:1:2:3:4"), None);
        assert_eq!(Burn::parse("league_renata_w_doom:1:2:3:4:5:6"), None);
        assert_eq!(Burn::parse("league_renata_w_buff"), None);
        assert_eq!(Burn::parse(&format!("{DOOM_STATE}x:1:2:3:4:5")), None);
    }
}
