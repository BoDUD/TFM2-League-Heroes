//! 奇亚娜附加包（用户 2026-10-22「插件按局势选」，同一天「改成按地形」；2026-11-04「奇亚娜很多机制和英雄联盟不一样 你仔细对比看看
//! 怎么改吧」：0.3.0 照英雄联盟 V26.21 重做）。
//!
//! 主包是纯数据：读不到地图和生命，又只有三个技能格，方圆塑令（W）只能并进天纵之勇（E）、元素按草丛 -> 河流 -> 岩石轮换，
//! 惊才绝景（R）的冲击波只能见人就晕。`mod.override_info` 把主包的奇亚娜换成 `override/` 里的副本（tools/kit/build_qiyana.py 的
//! native=1）：数据还是主包的（动作、动画、声音、冷却标记、连招），打人的部分换成本包的原生代码：
//! - **被动凌人贵气**（[`royal`]）：普攻和 Q、E（不含 R）对每个敌人 `rp_rest` tick（25 秒）只加一次 `rp_dmg` + `rp_ratio`% 攻击力；
//!   W 拿到元素时，上次是带着别的元素（或没元素）触发的那些敌人立刻可以再触发（英雄联盟的规则）。
//! - **W 方圆塑令**是本包自己的技能（[`Empress`] 被动每 `W_EVERY` tick 看一次，[`try_w`]）：学会 E 以后、冷却 `w_cd`，打架时
//!   （`w_fight` 内有敌方英雄，或在打的野怪）Q 在冷却或手上没元素，身边 `w_reach` 内有地形就冲 `w_dash` 过去拿那种元素
//!   （草丛 -> 草丛，墙和地图四边 -> 岩石，河道 -> 河流；几种都在时按局势挑，[`pick`]）、刷新 Q；E 落地时 W 好了也接一个
//!   （E -> W -> Q）。复活时（学会 E 以后）手上是岩石。附着元素时攻速 +`w_as`%、攻击距离 +`w_range`，普攻和 Q、E 多打
//!   `w_on` + `w_on_r`% 攻击力 + `w_on_ap`% 法强魔法伤害；离开战斗、站在手上元素的地形旁边时移速 +`w_oc_ms`%。
//! - **Q 以绪塔尔之锋**（[`q`]）：没元素时是身前一条线（`q_len`，宽 `q_hw` + 身体），第一个人 100%、后面的 `q_far`%，野怪
//!   `q_mon`%。有元素时是元素之怒：环刃扔出去（`q2_len`，画面 `league_qiyana_q_blade`），打中第一个敌人或飞到头就炸（`q2_blast`
//!   的圈：第一个人 100%，其余 `q_far`%）：河流定身 `q_root` tick 再减速 `q_slow`%；岩石对生命低于 `q_exec`% 的多打 `q_rock_pct`%
//!   （其余人 `q_rock_far`%）；草丛在她脚下留一片草地 `q_field_t` tick：站在里面隐身、加速 `q_ms`%，普攻、放 Q / E / R 或走出去就没了
//!   （[`field_upkeep`]）。动作的距离是元素之怒的（`q2_range`）：AI 钩子（[`ai`]）在她没元素时把 Q 留到目标进了直线的距离。
//! - **E 天纵之勇**（[`e`]）：突进落地时目标还在 `e_reach` 内才打 `e_dmg` + `e_ratio`% 攻击力。
//! - **R 惊才绝景**（[`ult`]）：风只击退不伤害，碰到第一面墙停下；冲击波沿路过的草丛、河道和撞上的墙边走，伤害 + 最大生命的
//!   `r_hp`%（野怪最多 `r_mon_cap`）、按离起点的远近晕 `r_stun_min`..`r_stun_max` tick。AI 钩子只在冲击波打得到敌方英雄时放 R。
//!   读不到地图时照主包：路上的人都伤害、击退、晕。
//! - **两张 5v5 地图**（2026-11-10）：游戏自己的地图照旧读地图文档；Rin 的召唤师峡谷 α 上（`current_map`）W、R 按峡谷的墙格子
//!   （没有墙体文件时只有地图四边算墙）和放大的河道斜带，没有草丛（只有艾翁的草丛给草元素），见 [`terrain`]。
//! 被动 `league_qiyana:empress` 把数字（`passive.params`）留给这些原生效果，并跑 W、草地和复活的元素。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_qiyana.log`，每次启动游戏重写。

use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, LazyLock, Mutex};

use game_places::terrain::{self as places, Map};
use mod_api_stable::*;

pub mod ai;
pub mod terrain;
pub mod ult;

use terrain::{Kind, MapGrids, Pt};

const ID: &str = "league_qiyana";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_qiyana") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_qiyana";

/// 主包奇亚娜的名字（buff、画面、音效都以它开头）。
pub fn qy(x: &str) -> String {
    format!("{HERO}_{x}")
}

/// 她自己生命不到这个百分比：草丛（伪装逃走）。
pub const GRASS_HP: usize = 35;
/// ……或者不到这个百分比，身边 `CROWD_R` 内又有两名以上敌方英雄。
pub const CROWDED_HP: usize = 60;
pub const CROWD_R: f64 = 40_000.0;
/// league_ivern 给站在艾翁草丛里的英雄挂的标记（用户 2026-10-22：「还有奇安娜也可以触发元素 艾翁的这个草 你们两可以联动一下」）。
pub const IVERN_BRUSH: &str = "league_ivern_in_brush";
/// W 隔这么多 tick 看一次。
pub const W_EVERY: usize = 3;
/// Q 的冷却还剩不到这么多 tick 就不为刷新它放 W（马上就好了）。
pub const W_Q_MIN: usize = 90;
/// 打野怪也放 W：Q 够得着（直线的距离 + 身体）、已经掉了血的野怪。
pub const W_MONSTER_HURT: usize = 99;
/// 离开战斗：这么近没有敌方英雄；手上元素的地形在这么近内：移速加成（每 `OC_EVERY` tick 看一次，加 `OC_EVERY` + 5 tick）。
pub const OC_FOE: f64 = 90_000.0;
pub const OC_NEAR: f64 = 32_000.0;
pub const OC_EVERY: usize = 15;
/// 草地：每 `FIELD_EVERY` tick 续 `FIELD_HIDE` tick 的隐身和加速（走出去、出手后至多这么久就没了）。
pub const FIELD_EVERY: usize = 2;
pub const FIELD_HIDE: usize = 6;
/// W 冲向墙时停在墙前多远（身体之外）；冲进草丛、河道时多冲进去多少。
pub const W_WALL_GAP: f64 = 2_000.0;
pub const W_INTO: f64 = 4_000.0;
/// W 冲不到这么远就不冲（站在草丛、河里或贴着墙：原地拿元素）。
pub const W_MIN_DASH: f64 = 2_000.0;

/// 同一种元素隔这么多 tick 才再记一行（每份模拟、每个她各算各的：[`news`]）。
const LOG_SAME: usize = 120;
/// 日志条数（2026-11-03 的日志：一次启动 0.68-0.71 MB，ELEMENT 约 3200 行、SPAWN 约 620 行都不限量）：每种整次启动一个计数，
/// 服务器的预模拟先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条；你看的那场（画面、观战、回放）每条都写。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_QIYANA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_qiyana.log");
        }
    }
    PathBuf::from("league_qiyana.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the simulation thread in game, league_talon_vault)
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

pub(crate) fn head(sim: &StableSim<'_>, id: usize) -> String {
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

/// 这一类的第 `n` 行写不写：你看的那场（`shown`）每行都写，预模拟写前 `LOG_FIRST` 行，之后每 `LOG_EVERY` 行一行。
pub fn logged(n: usize, shown: bool) -> bool {
    shown || n <= LOG_FIRST || n % LOG_EVERY == 0
}

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// 这一类日志又来了一行：它是整次启动的第几行（不写就是 None，[`logged`]）。
pub(crate) fn counted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    logged(*n, shown).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
pub(crate) fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

/// 记一行（这一类计数到了才写）。
pub(crate) fn note(sim: &StableSim<'_>, kind: &'static str, who: usize, text: impl FnOnce(usize) -> String) {
    if let Some(n) = counted(kind, on_screen(sim)) {
        wlog(format!("{} {}", head(sim, who), text(n)));
    }
}

// ===================== 参数 =====================

/// 被动的数字（`passive.params`，全是非负整数；默认值就是 tools/kit/build_qiyana.py 的 P，make_override.py 核对）。
macro_rules! params {
    ($($name:ident = $v:expr),* $(,)?) => {
        #[derive(Clone, Debug, PartialEq)]
        pub struct Params { $(pub $name: usize,)* }

        impl Default for Params {
            fn default() -> Self {
                Self { $($name: $v,)* }
            }
        }

        impl Params {
            /// 参数的名字（passive.params 的键）。
            pub const KEYS: &'static [&'static str] = &[$(stringify!($name)),*];

            fn slot(&mut self, key: &str) -> Option<&mut usize> {
                match key {
                    $(stringify!($name) => Some(&mut self.$name),)*
                    _ => None,
                }
            }
        }
    };
}

params! {
    rp_dmg = 45, rp_ratio = 55, rp_rest = 1500,
    w_as = 25, w_range = 1500, w_on = 15, w_on_r = 15, w_on_ap = 45,
    w_cd = 420, w_dash = 18000, w_reach = 64000, w_speed = 4500, w_fight = 60000, w_oc_ms = 8,
    q_len = 31500, q_hw = 7000, q2_len = 52000, q2_speed = 9000, q2_bw = 4000, q2_blast = 10000,
    q_dmg = 60, q_ratio = 110, q_far = 75, q_mon = 160,
    q_root = 30, q_slow = 20, q_slow_t = 60,
    q_exec = 50, q_rock_pct = 60, q_rock_far = 35,
    q_ms = 20, q_field_t = 180, q_field_r = 30000,
    e_dmg = 60, e_ratio = 70, e_reach = 15000,
    r_len = 60000, r_w = 13000, r_speed = 9000, r_dmg = 50, r_ratio = 90, r_hp = 10, r_mon_cap = 300,
    r_kb_speed = 2500, r_kb_t = 10, r_stun = 54, r_stun_min = 30, r_stun_max = 60, r_det = 16,
    r_border = 12000, r_span = 96000,
}

/// `{"rp_dmg":25,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        if let Some(slot) = p.slot(k) {
            *slot = v;
        }
    }
    p
}

/// 每份模拟的编号（2026-11-01 复查；league_galio 的做法）：被动第一次出生时抽一个，每次出生挂在她身上（buff `SIM_TAG<n>`）。
/// 以前按 sim 种子分：服务器并排跑的两份预演种子一样，第二份的凌人贵气被第一份记的时间挡掉。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
pub const SIM_TAG: &str = "league_qiyana_sim:";

pub(crate) fn sim_no(sim: &StableSim<'_>, id: usize) -> u64 {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .find_map(|b| b.name().strip_prefix(SIM_TAG).and_then(|v| v.parse().ok()))
            .unwrap_or(0)
    })
}

/// 每局的被动参数，给原生效果用：(这份模拟的编号, 她) -> 参数（league_naafiri 的做法；服务端预模拟和画面各算各的）。
static PARAMS: Mutex<Vec<((u64, usize), Params)>> = Mutex::new(Vec::new());

pub(crate) fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    let key = (sim_no(sim, me), me);
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).iter().find(|(k, _)| *k == key).map_or_else(Params::default, |(_, p)| p.clone())
}

fn keep_params(sim: &StableSim<'_>, me: usize, p: &Params) {
    let key = (sim_no(sim, me), me);
    let mut all = PARAMS.lock().unwrap_or_else(|e| e.into_inner());
    all.retain(|(k, _)| *k != key);
    all.push((key, p.clone()));
    if all.len() > 64 {
        all.remove(0);
    }
}

// ===================== 小工具 =====================

pub(crate) fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub(crate) fn unit(v: Pt) -> Option<Pt> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

pub(crate) fn pt(p: Pt) -> String {
    format!("({:.0}, {:.0})", p.0, p.1)
}

pub(crate) fn upos(p: Pt) -> (u64, u64) {
    (p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

/// (x, y) 到线段 a-b 的距离，和它在线段方向上离 a 多远（投影，可以在线段外）。
pub fn seg(p: Pt, a: Pt, b: Pt) -> (f64, f64) {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len = (dx * dx + dy * dy).sqrt();
    let along = if len > 0.0 { ((p.0 - a.0) * dx + (p.1 - a.1) * dy) / len } else { 0.0 };
    let t = along.clamp(0.0, len);
    let q = if len > 0.0 { (a.0 + dx / len * t, a.1 + dy / len * t) } else { a };
    (dist(p, q), along)
}

pub(crate) fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).filter(|e| e.is_alive()).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

pub(crate) fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 这个 buff 还剩多少 tick（没有为 None）。
pub(crate) fn buff_left(sim: &StableSim<'_>, id: usize, name: &str) -> Option<usize> {
    sim.get_entity(id).and_then(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == name).map(|b| b.duration_tick))
}

pub(crate) fn has_cc(sim: &StableSim<'_>, id: usize, kinds: &[CcKindV1]) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind))))
}

/// 放不了 W 的状态：硬控、沉默、禁位移技能、正在位移、正在放带动作的技能（同 league_leesin_hop 的 BUSY）。
pub const BUSY: [CcKindV1; 10] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::BlockMoveSkill, CcKindV1::ForceMove, CcKindV1::Animation];

fn me_in_ivern_brush(sim: &StableSim<'_>, me: usize) -> bool {
    has_buff(sim, me, IVERN_BRUSH)
}

/// 当前对局的地图（读不到为 None：照主包）。峡谷（2026-11-10，game_places 从塔和水晶看出来）用峡谷的地形
/// （[`terrain::rift_map`]：它的墙格子，没有草丛，放大的河道斜带），不用地图文档里游戏自己的 5v5 地图的格子。
pub(crate) fn current_map(sim: &StableSim<'_>) -> Option<Arc<MapGrids>> {
    if places::map_of_sim(sim) == Map::Rift {
        return Some(terrain::rift_map());
    }
    let maps = terrain::maps();
    if maps.is_empty() {
        return None;
    }
    let points: Vec<Pt> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect();
    terrain::pick_map(&points, &maps)
}

/// 一个敌方单位（防御塔、水晶不算）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub r: f64,
    pub champion: bool,
    /// 野怪（打野怪、史诗野怪、峡谷先锋）。
    pub monster: bool,
    pub hp: usize,
    pub max: usize,
    /// 免控（`cc_immune`）。
    pub immune: bool,
}

pub(crate) fn foe_of(sim: &StableSim<'_>, id: usize) -> Option<Foe> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() || !e.is_targetable() || e.is_tower() || matches!(e.kind(), Some(EntityKindV1::Tower | EntityKindV1::Nexus)) {
        return None;
    }
    let (hp, max) = e.hp();
    Some(Foe {
        id,
        at: (e.pos().0 as f64, e.pos().1 as f64),
        r: (e.radius() as f64).max(1.0),
        champion: e.is_champion(),
        monster: matches!(e.kind(), Some(EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen)),
        hp,
        max,
        immune: (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune),
    })
}

/// 她的敌人（活着、选得中，防御塔、水晶不算）。
pub(crate) fn foes(sim: &StableSim<'_>, me: usize) -> Vec<Foe> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team)
        .filter_map(|u| foe_of(sim, u.id()))
        .collect()
}

fn target_of(input: InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

pub(crate) fn pct(hp: usize, max: usize) -> usize {
    hp * 100 / max.max(1)
}

// ===================== 元素 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Element {
    Grass,
    River,
    Rock,
}

impl Element {
    /// 主包的 caster flag。
    pub fn flag(self) -> &'static str {
        match self {
            Element::Grass => "el_g",
            Element::River => "el_w",
            Element::Rock => "el_r",
        }
    }

    /// 凌人贵气记的元素：0 没元素。
    pub fn code(el: Option<Element>) -> u8 {
        match el {
            None => 0,
            Some(Element::Grass) => 1,
            Some(Element::River) => 2,
            Some(Element::Rock) => 3,
        }
    }

    /// 拿这种元素的地形。
    pub fn kind(self) -> Kind {
        match self {
            Element::Grass => Kind::Brush,
            Element::River => Kind::River,
            Element::Rock => Kind::Wall,
        }
    }
}

/// 她手上的元素（主包的 flag）。
pub(crate) fn held(sim: &StableSim<'_>, me: usize) -> Option<Element> {
    let e = sim.get_entity(me)?;
    let names: Vec<String> = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect();
    if !names.iter().any(|n| *n == qy("el_on")) {
        return None;
    }
    [Element::Grass, Element::River, Element::Rock].into_iter().find(|el| names.iter().any(|n| *n == qy(el.flag())))
}

/// 换上一种元素：去掉身上的元素，挂上 `el_on`（攻速、攻击距离）和那一种的 flag（数据读它们：Q 的动作、元素的画面）。
pub(crate) fn set_element(sim: &mut StableSim<'_>, me: usize, el: Element, p: &Params) {
    for f in ["el_g", "el_w", "el_r", "el_on"] {
        sim.entity_remove_buff(me, &qy(f));
    }
    let mut on = BuffV1::named(&qy("el_on"));
    on.attack_speed_mult = p.w_as as i32;
    // the +w_range attack range is league.dll's league:range reading el_on (2026-11-07), not a `range` here
    sim.add_buff(me, &on);
    sim.add_buff(me, &BuffV1::named(&qy(el.flag())));
}

/// 当时的局势（几种地形都在身边时挑哪种）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Spot {
    /// 她自己的生命百分比。
    pub my_hp: usize,
    /// `CROWD_R` 内的敌方英雄数。
    pub foes_near: usize,
    /// 打的是英雄。
    pub champion: bool,
    /// 目标的生命百分比。
    pub target_hp: usize,
}

/// 按局势挑元素（职业玩家的用法）：残血时用草丛伪装脱身，残血英雄用岩石斩杀，其他英雄用河流定住，打野怪和小兵用岩石。
pub fn choose(s: &Spot, q_exec: usize) -> Element {
    if s.my_hp < GRASS_HP || (s.my_hp < CROWDED_HP && s.foes_near >= 2) {
        Element::Grass
    } else if !s.champion || s.target_hp <= q_exec {
        Element::Rock
    } else {
        Element::River
    }
}

/// 元素是从哪来的。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Why {
    /// 身边的地形。
    Terrain,
    /// 身边没有地形：按局势（只在读不到地图时用）。
    Situation,
}

/// 按身边的地形挑：局势想要的那种在身边就拿它，否则拿最近的一种；身边什么都没有就按局势（[`choose`]）。
pub fn pick(near: &terrain::Near, s: &Spot, q_exec: usize) -> (Element, Why) {
    let want = choose(s, q_exec);
    let of = |e: Element| match e {
        Element::Grass => near.grass,
        Element::River => near.river,
        Element::Rock => near.rock,
    };
    if of(want).is_some() {
        return (want, Why::Terrain);
    }
    [Element::Grass, Element::River, Element::Rock]
        .into_iter()
        .filter_map(|e| of(e).map(|d| (e, d)))
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .map_or((want, Why::Situation), |(e, _)| (e, Why::Terrain))
}

// ===================== 凌人贵气：每个敌人一次 =====================

/// (这份模拟的编号 [`SIM_TAG`], 她, 敌人) -> (上一次加伤的 tick, 那时手上的元素 [`Element::code`])。
///
/// 0.3.2（2026-11-06）：每份模拟只删自己的。她每次触发时删掉她在这份模拟里过了 `rp_rest` 的行（按这份模拟自己的 tick：和没有
/// 这一行一样）；全表超过 [`ROYAL_MOST`] 行时丢编号最小（最早开始、早已打完）的模拟的行，正在触发的这一份从不丢。以前从不删、
/// 超过 4096 行整张清掉：别的模拟里还在冷却的敌人一下全都又能触发，两份本该一样的模拟在不同的 tick 被清，凌人贵气多打的那一下只
/// 出现在其中一份（11-06 画面和预模拟分叉的排查）。
pub type Royal = BTreeMap<(u64, usize, usize), (usize, u8)>;
static ROYAL: Mutex<Royal> = Mutex::new(BTreeMap::new());
/// 全表最多这么多行（每份模拟只留冷却里的几行；多出来的是打完的模拟的）。
pub const ROYAL_MOST: usize = 4096;

/// 这一 tick 对这个敌人加不加伤（加的话记下 tick 和元素）。`sim`：这份模拟的编号。
pub fn royal_ready(sim: u64, me: usize, target: usize, tick: usize, rest: usize, el: u8) -> bool {
    royal_ready_in(&mut ROYAL.lock().unwrap_or_else(|e| e.into_inner()), sim, me, target, tick, rest, el)
}

/// [`royal_ready`] on the table `all`.
pub fn royal_ready_in(all: &mut Royal, sim: u64, me: usize, target: usize, tick: usize, rest: usize, el: u8) -> bool {
    // her rows in this simulation past their rest are the same as none: gone, by this simulation's own clock (rows without
    // a number are shared by every simulation and have no clock of their own)
    if sim != 0 {
        let stale: Vec<_> = all
            .range((sim, me, 0)..=(sim, me, usize::MAX))
            .filter(|(_, v)| tick >= v.0 && tick - v.0 >= rest)
            .map(|(k, _)| *k)
            .collect();
        for k in stale {
            all.remove(&k);
        }
    }
    let key = (sim, me, target);
    if let Some(slot) = all.get_mut(&key) {
        if tick >= slot.0 && tick - slot.0 < rest {
            return false;
        }
        *slot = (tick, el);
        return true;
    }
    all.insert(key, (tick, el));
    // past ROYAL_MOST: the oldest simulation's rows go (the smallest number: one that ended), never this one's
    while all.len() > ROYAL_MOST {
        let Some(old) = all.keys().next().map(|k| k.0).filter(|&s| s != sim) else { break };
        let gone: Vec<_> = all.range((old, 0, 0)..=(old, usize::MAX, usize::MAX)).map(|(k, _)| *k).collect();
        for k in gone {
            all.remove(&k);
        }
    }
    true
}

/// W 拿到元素 `el`：上次带着别的元素（或没元素）触发的敌人可以再触发；返回清掉几个。
pub fn royal_reset(sim: u64, me: usize, el: u8) -> usize {
    let mut all = ROYAL.lock().unwrap_or_else(|e| e.into_inner());
    let before = all.len();
    all.retain(|&(s, m, _), v| s != sim || m != me || v.1 == el);
    before - all.len()
}

/// 凌人贵气打这个敌人（她手上的元素 `el`）。返回打了多少（没打为 0）。
pub(crate) fn royal(sim: &mut StableSim<'_>, me: usize, target: usize, el: Option<Element>) -> usize {
    let Some(f) = foe_of(sim, target) else { return 0 };
    let Some(atk) = sim.get_entity(me).map(|e| e.stat().attack) else { return 0 };
    let p = params_of(sim, me);
    if !royal_ready(sim_no(sim, me), me, f.id, sim.tick(), p.rp_rest, Element::code(el)) {
        return 0;
    }
    let d = p.rp_dmg + atk * p.rp_ratio / 100;
    sim.deal_damage(me, f.id, d, 0, AttackTypeV1::Skill);
    let at = InputTargetV1::target(f.id);
    sim.play_view_effect(&qy("p_hit"), me, &at, 0, 0, 0);
    sim.play_sfx(&qy("p_hit"), me, &at);
    d
}

/// 方圆塑令附着元素时的魔法伤害：`w_on` + `w_on_r`% 攻击力 + `w_on_ap`% 法强。
pub fn w_magic_amount(p: &Params, ad: usize, ap: usize) -> usize {
    p.w_on + ad * p.w_on_r / 100 + ap * p.w_on_ap / 100
}

// ===================== Q 以绪塔尔之锋 =====================

/// Q 打一个人多少（物理，护甲前）：第一个人 100%，其余 `q_far`%，野怪再乘 `q_mon`%。
pub fn q_amount(p: &Params, ad: usize, first: bool, monster: bool) -> usize {
    let base = p.q_dmg + ad * p.q_ratio / 100;
    let base = if first { base } else { base * p.q_far / 100 };
    if monster { base * p.q_mon / 100 } else { base }
}

/// 岩石：生命低于 `q_exec`% 时多打 `q_rock_pct`%（其余人 `q_rock_far`%）。
pub fn rock_bonus(p: &Params, amount: usize, first: bool, hp: usize, max: usize) -> usize {
    if pct(hp, max) < p.q_exec {
        amount * if first { p.q_rock_pct } else { p.q_rock_far } / 100
    } else {
        0
    }
}

/// 身前那条线（从 `from` 沿 `dir` 到 `len`，宽 `half` + 身体）上的人，按离她远近排。
pub fn line_hits(from: Pt, dir: Pt, len: f64, half: f64, foes: &[Foe]) -> Vec<Foe> {
    let end = (from.0 + dir.0 * len, from.1 + dir.1 * len);
    let mut hit: Vec<(f64, Foe)> = foes
        .iter()
        .filter_map(|f| {
            let (d, along) = seg(f.at, from, end);
            (d <= half + f.r && along > -f.r).then_some((along, *f))
        })
        .collect();
    hit.sort_by(|a, b| a.0.total_cmp(&b.0));
    hit.into_iter().map(|(_, f)| f).collect()
}

/// 扔出去的环刃停在哪：路上（宽 `half` + 身体）第一个人的位置在路线上的那一点，没人就飞到头。
pub fn blade_stop(from: Pt, dir: Pt, len: f64, half: f64, foes: &[Foe]) -> (Pt, Option<usize>) {
    match line_hits(from, dir, len, half, foes).first() {
        Some(f) => {
            let (_, along) = seg(f.at, from, (from.0 + dir.0 * len, from.1 + dir.1 * len));
            let a = along.clamp(0.0, len);
            ((from.0 + dir.0 * a, from.1 + dir.1 * a), Some(f.id))
        }
        None => ((from.0 + dir.0 * len, from.1 + dir.1 * len), None),
    }
}

/// 炸开的圈（半径 `radius` + 身体）里的人。
pub fn blast_hits(at: Pt, radius: f64, foes: &[Foe]) -> Vec<Foe> {
    foes.iter().filter(|f| dist(f.at, at) <= radius + f.r).copied().collect()
}

/// 扔出去还没炸的环刃：(这份模拟, 她) -> 它。
#[derive(Clone, Copy, Debug)]
struct Blade {
    el: Element,
    stop: Pt,
    first: Option<usize>,
}

static BLADES: LazyLock<Mutex<HashMap<(u64, usize), Blade>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// Q 朝哪：动作的目标；目标没了就朝 `reach` 内最近的敌人。
fn aim(sim: &StableSim<'_>, me: usize, here: Pt, input: InputTargetV1, reach: f64) -> Option<(Pt, Option<usize>)> {
    if let Some(t) = target_of(input) {
        if let Some(at) = alive_at(sim, t) {
            if let Some(d) = unit((at.0 - here.0, at.1 - here.1)) {
                return Some((d, Some(t)));
            }
        }
    }
    foes(sim, me)
        .into_iter()
        .filter(|f| dist(f.at, here) <= reach + f.r)
        .min_by(|a, b| dist(a.at, here).total_cmp(&dist(b.at, here)))
        .and_then(|f| unit((f.at.0 - here.0, f.at.1 - here.1)).map(|d| (d, Some(f.id))))
}

/// 只给人看的飞行物（环刃）：从 `from` 飞到 `to`，什么都不打。
fn picture(sim: &mut StableSim<'_>, me: usize, name: &str, from: Pt, to: Pt, speed: f64) -> bool {
    let (x, y) = upos(from);
    let (tx, ty) = upos(to);
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team: sim.get_entity(me).map_or(0, |e| e.team()),
        x,
        y,
        radius: 1_000,
        speed: speed.max(1.0) as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: tx,
        target_y: ty,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(name, &format!("{ID}:noop"), &spec)
}

pub(crate) fn queue(sim: &mut StableSim<'_>, stage: &str, me: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{stage}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, me, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, me)));
    }
}

/// Q 出手（主包的 `q_at`）：没元素打身前的线，有元素扔环刃（`q_blast` 在它停下时炸）。
fn q(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let el = held(sim, me);
    break_field(sim, me, "Q");
    let Some(here) = alive_at(sim, me) else { return };
    let p = params_of(sim, me);
    let reach = if el.is_some() { p.q2_len } else { p.q_len } as f64;
    let Some((dir, aimed)) = aim(sim, me, here, input, reach) else {
        note(sim, "q", me, |n| format!("Q #{n}: nobody to aim at"));
        return;
    };
    let all = foes(sim, me);
    let Some(el) = el else {
        let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        let hits = line_hits(here, dir, p.q_len as f64, p.q_hw as f64, &all);
        for (i, f) in hits.iter().enumerate() {
            sim.deal_damage(me, f.id, q_amount(&p, ad, i == 0, f.monster), 0, AttackTypeV1::Skill);
            royal(sim, me, f.id, None);
            let at = InputTargetV1::target(f.id);
            sim.play_view_effect(&qy("q_hit"), me, &at, 0, 0, 0);
            sim.play_sfx(&qy("q_hit"), me, &at);
        }
        let champs = hits.iter().filter(|f| f.champion).count();
        if champs > 0 || hits.is_empty() {
            note(sim, "q", me, |n| format!("Q #{n} the plain line at #{}: {} hit ({champs} champions), first #{}", aimed.unwrap_or(0),
                                           hits.len(), hits.first().map_or("-".to_string(), |f| f.id.to_string())));
        }
        return;
    };
    let (stop, first) = blade_stop(here, dir, p.q2_len as f64, p.q2_bw as f64, &all);
    let flight = ((dist(here, stop) / p.q2_speed.max(1) as f64).ceil() as usize).max(1);
    let flew = picture(sim, me, &qy("q_blade"), here, stop, p.q2_speed as f64);
    if el == Element::Grass {
        start_field(sim, me, here, &p);
    }
    BLADES.lock().unwrap_or_else(|e| e.into_inner()).insert((sim_no(sim, me), me), Blade { el, stop, first });
    let (x, y) = upos(stop);
    queue(sim, "q_blast", me, InputTargetV1::pos(x, y), flight);
    // the throws at champions (a camp's would fill the log)
    if aimed.is_some_and(|t| sim.get_entity(t).is_some_and(|e| e.is_champion())) || !flew {
        note(sim, "q2", me, |n| format!("Q2 #{n} {el:?}: the blade thrown {:.0} toward #{} - {} in {flight} ticks{}", dist(here, stop),
                                        aimed.unwrap_or(0), first.map_or("its end".to_string(), |f| format!("first #{f}")),
                                        if flew { "" } else { " (spawn_projectile refused: no flying blade)" }));
    }
}

/// 环刃停下：炸开（第一个人 100%，圈里其余的 `q_far`%），元素的效果。
fn q_blast(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let key = (sim_no(sim, me), me);
    let Some(b) = BLADES.lock().unwrap_or_else(|e| e.into_inner()).remove(&key) else { return };
    let p = params_of(sim, me);
    let Some((ad, ap)) = sim.get_entity(me).map(|e| (e.stat().attack, e.stat().magic_power)) else { return };
    let at = if input.kind == InputTargetKindV1::Pos.code() { (input.x as f64, input.y as f64) } else { b.stop };
    let all = foes(sim, me);
    let mut hits = blast_hits(at, p.q2_blast as f64, &all);
    // the first one hit: in the blast though he stepped on meanwhile
    if let Some(f) = b.first.and_then(|id| all.iter().find(|f| f.id == id)) {
        if !hits.iter().any(|h| h.id == f.id) && dist(f.at, at) <= p.q2_blast as f64 + f.r + 8_000.0 {
            hits.push(*f);
        }
    }
    let first = b.first.filter(|id| hits.iter().any(|h| h.id == *id)).or_else(|| {
        hits.iter().min_by(|x, y| dist(x.at, at).total_cmp(&dist(y.at, at))).map(|f| f.id)
    });
    let view = match b.el {
        Element::River => "q_w_hit",
        Element::Rock => "q_r_hit",
        Element::Grass => "q_g_hit",
    };
    let (mut rooted, mut rocks, mut champs) = (0, Vec::new(), 0);
    for f in &hits {
        let is_first = Some(f.id) == first;
        let mut d = q_amount(&p, ad, is_first, f.monster);
        if b.el == Element::Rock {
            let more = rock_bonus(&p, d, is_first, f.hp, f.max);
            if more > 0 && f.champion {
                rocks.push((f.id, pct(f.hp, f.max), more));
            }
            d += more;
        }
        sim.deal_damage(me, f.id, d, w_magic_amount(&p, ad, ap), AttackTypeV1::Skill);
        royal(sim, me, f.id, Some(b.el));
        if b.el == Element::River {
            if !f.immune {
                sim.apply_cc(f.id, &CcV1::of_kind(CcKindV1::Bind, p.q_root as u64));
                rooted += 1;
            }
            let mut slow = BuffV1::timed(&qy("q_slow"), p.q_root + p.q_slow_t);
            slow.move_speed_mult = -(p.q_slow as i32);
            sim.entity_remove_buff(f.id, &qy("q_slow"));
            sim.add_buff(f.id, &slow);
        }
        champs += f.champion as usize;
        let on = InputTargetV1::target(f.id);
        sim.play_view_effect(&qy(view), me, &on, 0, 0, 0);
        sim.play_sfx(&qy(view), me, &on);
    }
    let (x, y) = upos(at);
    if hits.is_empty() {
        sim.play_view_effect(&qy(view), me, &InputTargetV1::pos(x, y), 0, 0, 0);
    }
    if champs > 0 || hits.is_empty() {
        note(sim, "q2 blast", me, |n| {
            let rock = rocks.iter().map(|(id, h, m)| format!("#{id} at {h}% +{m}")).collect::<Vec<_>>().join(", ");
            format!("Q2 BLAST #{n} {:?} at {}: {} hit ({champs} champions), first #{}{}{}", b.el, pt(at), hits.len(),
                    first.map_or("-".to_string(), |f| f.to_string()),
                    if b.el == Element::River { format!(", {rooted} rooted") } else { String::new() },
                    if rock.is_empty() { String::new() } else { format!(", rock under half: {rock}") })
        });
    }
}

// ===================== 草地（元素之怒·草丛） =====================

/// 草地：(这份模拟, 她) -> (中心, 到哪一 tick)。
static FIELDS: LazyLock<Mutex<HashMap<(u64, usize), (Pt, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn start_field(sim: &mut StableSim<'_>, me: usize, at: Pt, p: &Params) {
    let until = sim.tick() + p.q_field_t;
    FIELDS.lock().unwrap_or_else(|e| e.into_inner()).insert((sim_no(sim, me), me), (at, until));
    hide(sim, me, p);
    note(sim, "field", me, |n| format!("FIELD #{n}: grass at {} for {} ticks (radius {})", pt(at), p.q_field_t, p.q_field_r));
}

/// 草地里：隐身和加速再续 `FIELD_HIDE` tick（走出去、出手后至多这么久就没了）。
fn hide(sim: &mut StableSim<'_>, me: usize, p: &Params) {
    sim.entity_set_invisible(me, FIELD_HIDE);
    let mut haste = BuffV1::timed(&qy("q_haste"), FIELD_HIDE);
    haste.move_speed_mult = p.q_ms as i32;
    sim.entity_remove_buff(me, &qy("q_haste"));
    sim.add_buff(me, &haste);
}

/// 她出手了（普攻、Q、E、R）：草地没了。
pub(crate) fn break_field(sim: &mut StableSim<'_>, me: usize, why: &str) {
    let key = (sim_no(sim, me), me);
    let gone = FIELDS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key);
    if let Some((_, until)) = gone {
        let left = until.saturating_sub(sim.tick());
        note(sim, "field end", me, |n| format!("FIELD END #{n}: {why} ({left} ticks were left)"));
    }
}

/// 每 tick：草地还在、她还在里面就续隐身和加速；时间到了、走出去了就收起。
fn field_upkeep(sim: &mut StableSim<'_>, me: usize) {
    let key = (sim_no(sim, me), me);
    let Some((at, until)) = FIELDS.lock().unwrap_or_else(|e| e.into_inner()).get(&key).copied() else { return };
    let p = params_of(sim, me);
    let tick = sim.tick();
    let here = alive_at(sim, me);
    let r = sim.get_entity(me).map_or(0.0, |e| e.radius() as f64);
    let why = match here {
        None => Some("she died"),
        Some(_) if tick >= until => Some("its time is over"),
        Some(h) if dist(h, at) > p.q_field_r as f64 + r => Some("she left it"),
        _ => None,
    };
    if let Some(why) = why {
        break_field(sim, me, why);
        return;
    }
    if tick % FIELD_EVERY == 0 {
        hide(sim, me, &p);
    }
}

// ===================== E 天纵之勇 =====================

/// E 落地：目标还在 `e_reach` 内才打；W 好了（Q 在冷却或手上没元素）就接一个 W（E -> W -> Q）。
fn e(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    break_field(sim, me, "E");
    let Some(here) = alive_at(sim, me) else { return };
    let p = params_of(sim, me);
    let (my_r, ad, ap) = sim.get_entity(me).map_or((0.0, 0, 0), |e| (e.radius() as f64, e.stat().attack, e.stat().magic_power));
    let t = target_of(input).and_then(|t| foe_of(sim, t));
    let el = held(sim, me);
    let said = match t {
        Some(f) if dist(here, f.at) <= p.e_reach as f64 + my_r + f.r => {
            let magic = if el.is_some() { w_magic_amount(&p, ad, ap) } else { 0 };
            sim.deal_damage(me, f.id, p.e_dmg + ad * p.e_ratio / 100, magic, AttackTypeV1::Skill);
            royal(sim, me, f.id, el);
            let on = InputTargetV1::target(f.id);
            sim.play_view_effect(&qy("e_hit"), me, &on, 0, 0, 0);
            sim.play_sfx(&qy("e_hit"), me, &on);
            format!("struck #{}", f.id)
        }
        Some(f) => format!("MISSED #{} ({:.0} away at the landing)", f.id, dist(here, f.at)),
        None => "its target is gone".to_string(),
    };
    let w = w_ready(sim, me) && w_needed(sim, me) && try_w(sim, me, t.map(|f| f.id), "after E");
    if t.is_some_and(|f| f.champion) {
        note(sim, "e", me, |n| format!("E #{n}: {said}{}", if w { ", then W" } else { "" }));
    }
}

// ===================== 普攻 =====================

/// 普攻打中：附着元素时的魔法伤害、凌人贵气、草地没了。
fn hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    break_field(sim, me, "an attack");
    let Some(t) = target_of(input) else { return };
    if !sim.get_entity(t).is_some_and(|e| e.is_alive()) {
        return;
    }
    let el = held(sim, me);
    if el.is_some() {
        let p = params_of(sim, me);
        if let Some(s) = sim.get_entity(me).map(|e| e.stat()) {
            sim.deal_damage(me, t, 0, w_magic_amount(&p, s.attack, s.magic_power), AttackTypeV1::Skill);
        }
        sim.play_view_effect(&qy("w_hit"), me, &InputTargetV1::target(t), 0, 0, 0);
    }
    royal(sim, me, t, el);
}

// ===================== W 方圆塑令 =====================

/// W 好了：学会了 E（第 3 级起），不在冷却。
pub(crate) fn w_ready(sim: &StableSim<'_>, me: usize) -> bool {
    let learned = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill2)).is_none_or(|c| c.unlocked);
    learned && !has_buff(sim, me, &qy("w_cd"))
}

/// 值得放 W：Q 的冷却还长（刷新它），或手上没元素。
pub(crate) fn w_needed(sim: &StableSim<'_>, me: usize) -> bool {
    held(sim, me).is_none() || buff_left(sim, me, &qy("q_cd")).is_some_and(|t| t >= W_Q_MIN)
}

/// 打架的对象：`w_fight` 内最近的敌方英雄（看得见的），不然是 Q 够得着、掉了血的野怪。
fn fight_target(sim: &StableSim<'_>, me: usize, p: &Params) -> Option<Foe> {
    let here = alive_at(sim, me)?;
    let team = sim.get_entity(me)?.team();
    let all = foes(sim, me);
    let champ = all
        .iter()
        .filter(|f| f.champion && sim.is_visible(team, f.id) && dist(f.at, here) <= p.w_fight as f64)
        .min_by(|a, b| dist(a.at, here).total_cmp(&dist(b.at, here)));
    if let Some(f) = champ {
        return Some(*f);
    }
    let r = sim.get_entity(me).map_or(0.0, |e| e.radius() as f64);
    all.into_iter()
        .filter(|f| f.monster && pct(f.hp, f.max) <= W_MONSTER_HURT && dist(f.at, here) <= (p.q_len + p.q_hw) as f64 + r + f.r)
        .min_by(|a, b| dist(a.at, here).total_cmp(&dist(b.at, here)))
}

/// W 冲多远：地形在 `d` 外（她的身体 `r`）——墙停在墙前 `W_WALL_GAP`，草丛、河道冲进去 `W_INTO`，最多 `w_dash`；不到
/// `W_MIN_DASH` 不冲（None：原地拿元素）。
pub fn w_dash_len(el: Element, d: f64, r: f64, p: &Params) -> Option<f64> {
    let len = match el {
        Element::Rock => d - r - W_WALL_GAP,
        _ => d + W_INTO,
    }
    .min(p.w_dash as f64);
    (len >= W_MIN_DASH).then_some(len)
}

/// 冲向 `to`（强制位移，速度取整到每 tick 一样长）；返回 tick 数。
fn dash_self(sim: &mut StableSim<'_>, me: usize, from: Pt, to: Pt, speed: f64) -> usize {
    let d = dist(from, to);
    if d < 1.0 {
        return 0;
    }
    let ticks = (d / speed.max(1.0)).ceil().max(1.0);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (to.0 - from.0).round() as i64;
    cc.dy = (to.1 - from.1).round() as i64;
    cc.speed = (d / ticks).ceil() as u64;
    sim.apply_cc(me, &cc);
    ticks as usize
}

/// 放 W：挑身边 `w_reach` 内的地形（按局势挑哪种，[`pick`]），冲过去拿元素、刷新 Q。地图读得到而身边没有地形就不放（英雄联盟的
/// W 要对着地形放）；读不到地图时按局势给元素、不冲。返回放没放。
pub(crate) fn try_w(sim: &mut StableSim<'_>, me: usize, foe: Option<usize>, why: &str) -> bool {
    let Some(here) = alive_at(sim, me) else { return false };
    let p = params_of(sim, me);
    let (hp, max) = sim.get_entity(me).map_or((1, 1), |e| e.hp());
    let crowd = foes(sim, me).iter().filter(|f| f.champion && dist(f.at, here) <= CROWD_R).count();
    let target = foe.and_then(|t| foe_of(sim, t));
    let spot = Spot { my_hp: pct(hp, max), foes_near: crowd, champion: target.is_some_and(|f| f.champion),
                      target_hp: target.map_or(100, |f| pct(f.hp, f.max)) };
    let map = current_map(sim);
    let reach = p.w_reach as f64;
    let mut near = map.as_ref().map_or_else(terrain::Near::default, |m| terrain::near(m, here.0, here.1, reach));
    let ivern = me_in_ivern_brush(sim, me);
    if ivern {
        near.grass = Some(0.0); // standing in Ivern's brush: grass right here
    }
    let (el, how) = pick(&near, &spot, p.q_exec);
    if map.is_some() && how == Why::Situation {
        // 0.3.1: asked every W_EVERY ticks while she fights in the open: one line a LOG_SAME (248 view lines a game before)
        if no_terrain_news(sim_no(sim, me), me, sim.tick()) {
            note(sim, "w none", me, |n| format!("W NO TERRAIN #{n} ({why}) at {}: nothing within {reach:.0} (next line {LOG_SAME} \
                                                  ticks on at the soonest)", pt(here)));
        }
        return false;
    }
    let point = if ivern && el == Element::Grass {
        None
    } else {
        map.as_ref().and_then(|m| terrain::nearest_point(m, el.kind(), here.0, here.1, reach))
    };
    gather(sim, me, el, here, point, &near, &spot, why, &p);
    true
}

/// W：换上元素、刷新 Q、清掉凌人贵气上别的元素的记录、冷却；冲向那块地形（墙停在墙前，草丛、河道冲进去一点）。
#[allow(clippy::too_many_arguments)]
fn gather(sim: &mut StableSim<'_>, me: usize, el: Element, here: Pt, point: Option<(f64, Pt)>, near: &terrain::Near, spot: &Spot,
          why: &str, p: &Params) {
    let q_was = buff_left(sim, me, &qy("q_cd"));
    set_element(sim, me, el, p);
    sim.entity_remove_buff(me, &qy("q_cd"));
    sim.entity_remove_buff(me, &qy("w_cd"));
    sim.add_buff(me, &BuffV1::timed(&qy("w_cd"), p.w_cd));
    let reset = royal_reset(sim_no(sim, me), me, Element::code(Some(el)));
    let on = InputTargetV1::target(me);
    sim.play_view_effect(&qy("w_on"), me, &on, 0, 0, 0);
    sim.play_sfx(&qy("w_on"), me, &on);
    let r = sim.get_entity(me).map_or(0.0, |e| e.radius() as f64);
    let mut dashed = 0.0;
    if let Some((d, to)) = point {
        if let (Some(len), Some(dir)) = (w_dash_len(el, d, r, p), unit((to.0 - here.0, to.1 - here.1))) {
            let end = (here.0 + dir.0 * len, here.1 + dir.1 * len);
            dash_self(sim, me, here, end, p.w_speed as f64);
            dashed = len;
        }
    }
    if !news(sim_no(sim, me), me, sim.tick(), el) {
        return;
    }
    let d = |v: Option<f64>| v.map_or("-".to_string(), |d| format!("{d:.0}"));
    note(sim, "w", me, |n| format!(
        "W #{n} {el:?} ({why}) at {}: grass {} rock {} river {}; dash {dashed:.0}{}; Q {}; Royal Privilege ready again on {reset}; {spot:?}",
        pt(here), d(near.grass), d(near.rock), d(near.river),
        point.map_or(String::new(), |(_, to)| format!(" toward {}", pt(to))),
        q_was.map_or("was ready".to_string(), |t| format!("reset ({t} ticks were left)"))));
}

/// (这份模拟的编号, 她) -> 上一次记下 W 的 (tick, 元素)。以前整个附加包只有一个 `last`：服务器并排跑的两份预演
/// 种子、局、实体号都一样，互相冲掉对方记的那一次（2026-11-03 复查）。
static ELEMENT_LOGGED: Mutex<Vec<((u64, usize), (usize, Element))>> = Mutex::new(Vec::new());

/// 这一次附魔值不值得记一行：这份模拟（`sim`，[`SIM_TAG`]）里她（`me`）上一次记的是别的元素，或者已经过了 `LOG_SAME`
/// tick（值得的话记下这一次）。
pub fn news(sim: u64, me: usize, tick: usize, el: Element) -> bool {
    let key = (sim, me);
    let mut all = ELEMENT_LOGGED.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(slot) = all.iter_mut().find(|(k, _)| *k == key) {
        let (t0, e0) = slot.1;
        if e0 == el && tick >= t0 && tick - t0 < LOG_SAME {
            return false;
        }
        slot.1 = (tick, el);
        return true;
    }
    all.push((key, (tick, el)));
    if all.len() > 256 {
        all.drain(..64);
    }
    true
}

/// 0.3.1: (这份模拟的编号, 她) -> 上一次记 `W NO TERRAIN` 的 tick。
static NO_TERRAIN_LOGGED: Mutex<Vec<((u64, usize), usize)>> = Mutex::new(Vec::new());

/// 「身边没有地形」这一行值不值得记：这份模拟里她上一行已经过了 `LOG_SAME` tick（值得的话记下这一次）。被动每 `W_EVERY` tick
/// 问一次 W，在空地上打架时以前每 3 tick 一行。
pub fn no_terrain_news(sim: u64, me: usize, tick: usize) -> bool {
    let key = (sim, me);
    let mut all = NO_TERRAIN_LOGGED.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(slot) = all.iter_mut().find(|(k, _)| *k == key) {
        if tick >= slot.1 && tick - slot.1 < LOG_SAME {
            return false;
        }
        slot.1 = tick;
        return true;
    }
    all.push((key, tick));
    if all.len() > 256 {
        all.drain(..64);
    }
    true
}

/// 离开战斗、站在手上元素的地形旁边：移速加成（英雄联盟 W 的被动）。
fn out_of_combat(sim: &mut StableSim<'_>, me: usize, p: &Params) {
    let Some(el) = held(sim, me) else { return };
    let Some(here) = alive_at(sim, me) else { return };
    let team = sim.get_entity(me).map_or(0, |e| e.team());
    if foes(sim, me).iter().any(|f| f.champion && sim.is_visible(team, f.id) && dist(f.at, here) <= OC_FOE) {
        return;
    }
    let Some(map) = current_map(sim) else { return };
    if terrain::nearest_point(&map, el.kind(), here.0, here.1, OC_NEAR).is_none() {
        return;
    }
    let mut b = BuffV1::timed(&qy("w_ms"), OC_EVERY + 5);
    b.move_speed_mult = p.w_oc_ms as i32;
    sim.entity_remove_buff(me, &qy("w_ms"));
    sim.add_buff(me, &b);
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
pub struct Empress {
    p: Params,
    /// This simulation's number (`SIM_TAG`), drawn at her first spawn.
    sim: u64,
}

impl StablePassive for Empress {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if self.sim == 0 {
            self.sim = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        keep_params(sim, me, &self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        // League: once W is learned she respawns holding terrain (rock)
        let learned = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill2)).is_some_and(|c| c.unlocked);
        if learned {
            set_element(sim, me, Element::Rock, &self.p);
        }
        let p = self.p.clone();
        note(sim, "spawn", me, |n| format!("SPAWN #{n}: the add-on's Qiyana (player {player}, team {team}){}, {p:?}",
                                           if learned { ", holding rock (W learned)" } else { "" }));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng_seed: u64, _player: usize, me: usize) {
        field_upkeep(sim, me);
        let tick = sim.tick();
        if tick % OC_EVERY == 0 {
            out_of_combat(sim, me, &self.p);
        }
        if tick % W_EVERY != 0 || !w_ready(sim, me) || !w_needed(sim, me) {
            return;
        }
        if !sim.get_entity(me).is_some_and(|e| e.is_alive() && e.is_targetable()) || has_cc(sim, me, &BUSY) {
            return;
        }
        let Some(f) = fight_target(sim, me, &self.p) else { return };
        try_w(sim, me, Some(f.id), if f.champion { "fight" } else { "a monster" });
    }
}

// ===================== 注册 =====================

/// A native effect: the function, and the AI's reading of its hit (flat, % AD) from the data's numbers.
struct Fx(fn(&mut StableSim<'_>, usize, InputTargetV1), (usize, usize));
impl StableEffectType for Fx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        let (flat, ratio) = self.1;
        if flat == 0 && ratio == 0 {
            return (0, 0);
        }
        (flat + s.attack * ratio / 100, 0)
    }
}

fn noop(_: &mut StableSim<'_>, _: usize, _: InputTargetV1) {}

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Qiyana as in League: W Terrashape of her own from the terrain, Edge of Ixtal's line and thrown blade, Royal Privilege per enemy, Supreme Display of Talent by the terrain) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let d = Params::default();
    module.add_native_passive(format!("{ID}:empress"), Empress::default());
    module.add_native_effect(format!("{ID}:q"), Fx(q, (d.q_dmg, d.q_ratio)));
    module.add_native_effect(format!("{ID}:q_blast"), Fx(q_blast, (0, 0)));
    module.add_native_effect(format!("{ID}:e"), Fx(e, (d.e_dmg, d.e_ratio)));
    module.add_native_effect(format!("{ID}:hit"), Fx(hit, (0, 0)));
    module.add_native_effect(format!("{ID}:r"), Fx(ult::launch, (0, 0)));
    module.add_native_effect(format!("{ID}:r_push"), Fx(ult::push, (0, 0)));
    module.add_native_effect(format!("{ID}:r_boom"), Fx(ult::boom, (0, 0)));
    module.add_native_effect(format!("{ID}:r_stun"), Fx(ult::stun, (0, 0)));
    module.add_native_effect(format!("{ID}:noop"), Fx(noop, (0, 0)));
    module.add_player_input_ai(ai::QiyanaAi::default());
    host.log(LogLevel::Info, "league_qiyana loaded (Qiyana as in League: W Terrashape from the terrain, Edge of Ixtal's line and thrown blade, Royal Privilege per enemy, Supreme Display of Talent by the terrain).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module.set_map_customizer(terrain::TerrainReader);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    fn spot(my_hp: usize, foes_near: usize, champion: bool, target_hp: usize) -> Spot {
        Spot { my_hp, foes_near, champion, target_hp }
    }

    fn foe(id: usize, at: Pt) -> Foe {
        Foe { id, at, r: 10_000.0, champion: true, monster: false, hp: 1000, max: 1000, immune: false }
    }

    #[test]
    fn the_element_follows_the_situation() {
        // low herself, or hurt in a crowd: grass to slip away
        assert_eq!(choose(&spot(30, 0, true, 90), 50), Element::Grass);
        assert_eq!(choose(&spot(55, 2, true, 40), 50), Element::Grass);
        // a wounded champion: rock to finish him
        assert_eq!(choose(&spot(90, 2, true, 50), 50), Element::Rock);
        // a healthy champion: river to hold him
        assert_eq!(choose(&spot(90, 1, true, 80), 50), Element::River);
        // a camp or a minion: rock
        assert_eq!(choose(&spot(90, 0, false, 100), 50), Element::Rock);
    }

    #[test]
    fn the_element_follows_the_terrain() {
        use terrain::Near;
        let healthy = spot(90, 1, true, 80); // wants river
        // the river beside her: river
        assert_eq!(pick(&Near { river: Some(5.0), rock: Some(1.0), grass: None }, &healthy, 50), (Element::River, Why::Terrain));
        // no river beside her: the nearest of what is there
        assert_eq!(pick(&Near { grass: Some(30.0), rock: Some(10.0), river: None }, &healthy, 50), (Element::Rock, Why::Terrain));
        assert_eq!(pick(&Near { grass: Some(3.0), rock: Some(10.0), river: None }, &healthy, 50), (Element::Grass, Why::Terrain));
        // low herself with a bush beside her: grass
        assert_eq!(pick(&Near { grass: Some(40.0), rock: Some(0.0), river: None }, &spot(30, 0, true, 90), 50), (Element::Grass, Why::Terrain));
        // nothing beside her: by the situation (W is then not cast where the map is known)
        assert_eq!(pick(&Near::default(), &healthy, 50), (Element::River, Why::Situation));
        assert_eq!(pick(&Near::default(), &spot(90, 0, false, 100), 50), (Element::Rock, Why::Situation));
    }

    #[test]
    fn q_falls_off_beyond_the_first_and_bites_monsters() {
        let p = Params::default();
        let first = q_amount(&p, 200, true, false);
        assert_eq!(first, 60 + 220);
        assert_eq!(q_amount(&p, 200, false, false), first * 75 / 100);
        assert_eq!(q_amount(&p, 200, true, true), first * 160 / 100);
        // rock: 60% more on the first under half health, 35% on the others, none at half or above
        assert_eq!(rock_bonus(&p, 280, true, 490, 1000), 168);
        assert_eq!(rock_bonus(&p, 210, false, 490, 1000), 73);
        assert_eq!(rock_bonus(&p, 280, true, 500, 1000), 0);
    }

    #[test]
    fn the_line_and_the_blade() {
        let me = (100_000.0, 100_000.0);
        let dir = (1.0, 0.0);
        let near = foe(1, (120_000.0, 100_000.0));
        let far = foe(2, (138_000.0, 104_000.0));
        let aside = foe(3, (120_000.0, 130_000.0));
        let behind = foe(4, (75_000.0, 100_000.0));
        let beyond = foe(5, (160_000.0, 100_000.0));
        let all = [far, aside, near, behind, beyond];
        // the plain line (31500 long, 7000 + the body wide): the near one first, the far one second; not aside, not
        // behind her, not beyond its tip
        let hits: Vec<usize> = line_hits(me, dir, 31_500.0, 7_000.0, &all).iter().map(|f| f.id).collect();
        assert_eq!(hits, vec![1, 2]);
        // the blade stops on the first one in its way, else flies its whole length
        assert_eq!(blade_stop(me, dir, 52_000.0, 4_000.0, &all), ((120_000.0, 100_000.0), Some(1)));
        assert_eq!(blade_stop(me, (0.0, -1.0), 52_000.0, 4_000.0, &all), ((100_000.0, 48_000.0), None));
        // the blast round it
        let ids: Vec<usize> = blast_hits((120_000.0, 100_000.0), 10_000.0, &all).iter().map(|f| f.id).collect();
        assert_eq!(ids, vec![2, 1]);
    }

    #[test]
    fn royal_privilege_once_per_enemy_and_an_element_change_resets_it() {
        assert!(royal_ready(7, 1, 10, 100, 1500, 0));
        assert!(!royal_ready(7, 1, 10, 200, 1500, 0));
        assert!(royal_ready(7, 1, 11, 300, 1500, 3)); // another enemy (procced holding rock)
        assert!(royal_ready(7, 1, 10, 1600, 1500, 0)); // rested
        assert!(royal_ready(8, 1, 10, 200, 1500, 0)); // another game
        // gathering rock: the one last procced with none is ready again, the rock one is not
        assert!(!royal_ready(7, 1, 10, 1700, 1500, 3));
        assert_eq!(royal_reset(7, 1, 3), 1);
        assert!(royal_ready(7, 1, 10, 1700, 1500, 3));
        assert!(!royal_ready(7, 1, 11, 1700, 1500, 3));
        // another simulation's records stay
        assert!(!royal_ready(8, 1, 10, 300, 1500, 0));
    }

    /// 0.3.2 (2026-11-06): two simulations of one set (the same entity ids) run side by side, one far ahead of the other,
    /// and old simulations fill the table: each keeps its own cooldowns - nothing of one is pruned by the other's clock,
    /// and a full table drops finished simulations' rows, never a running one's (0.3.1 cleared the whole table past 4096).
    #[test]
    fn royal_privilege_rows_are_kept_and_pruned_per_simulation() {
        let mut all = Royal::new();
        // the twins drew their numbers after the finished simulations below
        let (a, b) = (5_000, 5_001);
        assert!(royal_ready_in(&mut all, a, 1, 10, 100, 1500, 0));
        assert!(royal_ready_in(&mut all, b, 1, 10, 100, 1500, 0));
        // A runs on to tick 5000 (its row from 100 goes by its own clock); B, at 900, still rests on enemy #10
        assert!(royal_ready_in(&mut all, a, 1, 11, 5_000, 1500, 0));
        assert!(!all.contains_key(&(a, 1, 10)), "A's rested row pruned by A's clock");
        assert!(!royal_ready_in(&mut all, b, 1, 10, 900, 1500, 0), "B's cooldown stays");
        // a thousand finished simulations' rows, more than the table holds
        for old in 1..=1_000u64 {
            for t in 0..5 {
                all.insert((old, 1, 100 + t), (10, 0));
            }
        }
        assert!(royal_ready_in(&mut all, a, 1, 12, 5_010, 1500, 0));
        assert!(all.len() <= ROYAL_MOST, "{}", all.len());
        assert!(!all.contains_key(&(1, 1, 100)), "the oldest simulation went first");
        assert!(!royal_ready_in(&mut all, b, 1, 10, 950, 1500, 0), "B's cooldown survived the overflow");
        assert!(!royal_ready_in(&mut all, a, 1, 11, 5_020, 1500, 0), "A's cooldown survived the overflow");
        // B's own clock frees #10 at 1600, whatever A's says
        assert!(royal_ready_in(&mut all, b, 1, 10, 1_600, 1500, 0));
    }

    #[test]
    fn r_plans_are_kept_and_pruned_per_simulation() {
        use ult::{remember_in, Plans, Planned, PLANS_MOST, PLAN_FRESH};
        let plan = |tick| Planned { tick, target: 9, dir: (1.0, 0.0), caught: 1 };
        let mut all = Plans::new();
        let (a, b) = (5_000, 5_001);
        remember_in(&mut all, (a, 3), plan(100));
        remember_in(&mut all, (b, 3), plan(100));
        // A's next life plans far later: its old plan (void past PLAN_FRESH) goes, B's (at its own tick 100) stays
        remember_in(&mut all, (a, 40), plan(5_000));
        assert!(!all.contains_key(&(a, 3)) && all.contains_key(&(b, 3)) && all.contains_key(&(a, 40)));
        // finished simulations' plans past the cap: the oldest go, never the running ones'
        for old in 1..=(PLANS_MOST as u64) {
            all.insert((old, 3), plan(10));
        }
        remember_in(&mut all, (a, 40), plan(5_000 + PLAN_FRESH));
        assert!(all.len() <= PLANS_MOST && all.contains_key(&(b, 3)) && !all.contains_key(&(1, 3)), "{}", all.len());
    }

    #[test]
    fn w_dashes_toward_the_terrain() {
        let p = Params::default();
        // a wall 40000 off: up to its face less her body and the gap; a far one: the whole dash
        assert_eq!(w_dash_len(Element::Rock, 40_000.0, 10_000.0, &p), Some(18_000.0));
        assert_eq!(w_dash_len(Element::Rock, 25_000.0, 10_000.0, &p), Some(13_000.0));
        // against the wall already: no dash, the element where she stands
        assert_eq!(w_dash_len(Element::Rock, 11_000.0, 10_000.0, &p), None);
        // brush and river: into them
        assert_eq!(w_dash_len(Element::Grass, 6_000.0, 10_000.0, &p), Some(10_000.0));
        assert_eq!(w_dash_len(Element::River, 0.0, 10_000.0, &p), Some(4_000.0));
        assert_eq!(w_dash_len(Element::River, 60_000.0, 10_000.0, &p), Some(18_000.0));
    }

    #[test]
    fn the_enchant_magic() {
        let p = Params::default();
        assert_eq!(w_magic_amount(&p, 200, 0), 15 + 30);
        assert_eq!(w_magic_amount(&p, 200, 100), 15 + 30 + 45);
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"rp_rest":300,"q_exec":40,"x":1}"#),
                   Params { rp_rest: 300, q_exec: 40, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
        assert!(Params::KEYS.contains(&"r_span") && Params::KEYS.len() > 40);
    }

    #[test]
    fn segments() {
        let (d, along) = seg((5.0, 3.0), (0.0, 0.0), (10.0, 0.0));
        assert_eq!((d, along), (3.0, 5.0));
        let (d, along) = seg((-4.0, 3.0), (0.0, 0.0), (10.0, 0.0));
        assert_eq!((d, along), (5.0, -4.0));
    }

    #[test]
    fn the_presims_log_the_first_lines_then_a_sample() {
        assert!(logged(1, false) && logged(LOG_FIRST, false));
        assert!(!logged(LOG_FIRST + 1, false) && !logged(LOG_EVERY - 1, false));
        assert!(logged(LOG_EVERY, false) && logged(3 * LOG_EVERY, false));
        // the match on screen: every line
        assert!(logged(LOG_FIRST + 1, true) && logged(LOG_EVERY + 1, true));
    }

    #[test]
    fn the_same_element_is_skipped_per_sim_and_qiyana() {
        // sims 901 and 902: the server's twin presims (the same match, set, entity ids and ticks)
        assert!(news(901, 20, 1000, Element::River));
        assert!(news(902, 20, 1000, Element::River), "the twin keeps its own record");
        assert!(!news(901, 20, 1060, Element::River), "the same element within LOG_SAME");
        assert!(news(901, 21, 1060, Element::River), "another Qiyana");
        assert!(news(901, 20, 1070, Element::Rock), "another element");
        assert!(!news(902, 20, 1000 + LOG_SAME - 1, Element::River));
        assert!(news(902, 20, 1000 + LOG_SAME, Element::River), "past LOG_SAME");
        assert!(news(901, 20, 500, Element::Rock), "an earlier tick: another run");
    }

    #[test]
    fn no_terrain_is_said_once_a_while() {
        // 0.3.1: asked every W_EVERY ticks in the open: one line a LOG_SAME per sim and Qiyana
        assert!(no_terrain_news(903, 30, 2000));
        assert!(!no_terrain_news(903, 30, 2000 + W_EVERY));
        assert!(no_terrain_news(904, 30, 2000 + W_EVERY), "the twin keeps its own record");
        assert!(no_terrain_news(903, 31, 2000 + W_EVERY), "another Qiyana");
        assert!(!no_terrain_news(903, 30, 2000 + LOG_SAME - 1));
        assert!(no_terrain_news(903, 30, 2000 + LOG_SAME), "past LOG_SAME");
        assert!(no_terrain_news(903, 30, 100), "an earlier tick: another run");
    }

    #[test]
    fn the_names_fit() {
        for x in ["el_g", "el_w", "el_r", "el_on", "p_hit", "q_cd", "w_cd", "w_ms", "q_haste", "q_slow", "r_go", "q_blade"] {
            assert!(qy(x).len() <= BUFF_NAME_CAP);
        }
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
    }
}
