//! 奇亚娜附加包（用户 2026-10-22「插件按局势选」，同一天「改成按地形：E 落地看附近的草丛、墙、河，附近都没有就退回按局势
//! 选」）：方圆塑令按身边的地形选元素、凌人贵气按每个敌人算、以绪塔尔之锋的岩石斩杀。
//!
//! 主包是纯数据：读不到地图，元素只能按草丛 -> 河流 -> 岩石轮换；`SwitchByBuff` 只读施法者自己，凌人贵气只能是她自己的
//! 冷却（一次触发后 `rp_cd` tick 内谁都不加伤）；岩石读不到目标的生命，只好对谁都多打一点。`mod.override_info` 把主包的
//! 奇亚娜换成 `override/` 里的副本（tools/kit/build_qiyana.py 的 native=1）：数据和主包一样，只是
//! - 天纵之勇落地时的附魔换成本包的原生效果 `league_qiyana:element`，按她身边 `NEAR` 内的地形挑元素（[`pick`]，地形在
//!   [`terrain`]：草丛格子 -> 草丛，墙格子和地图四边的墙面 -> 岩石，河道 -> 河流，英雄联盟的 W 朝哪块地形放就拿哪种）：
//!   身边有局势想要的那种就拿它，没有就拿最近的那种；身边什么都没有时按局势挑（[`choose`]）：她自己残血、或者残血又被
//!   围着 -> 草丛（伪装逃走），目标是残血英雄 -> 岩石（斩杀），目标是英雄 -> 河流（定身），打野怪和小兵 -> 岩石；
//! - 每一下命中里的凌人贵气换成 `league_qiyana:royal`：每个敌人 `rp_rest` tick 内只加一次 `rp_dmg` + `rp_ratio`% 攻击力
//!   （英雄联盟：对每个敌人的第一次普攻或技能）；
//! - 岩石的以绪塔尔之锋换成 `league_qiyana:rock`：目标生命不到 `q_exec`% 时多打 2 x (`q_rock` + `q_rock_r`% 攻击力)，
//!   高于时不加（英雄联盟：对生命低于 50% 的敌人造成额外伤害）。
//! 被动 `league_qiyana:empress` 只把这些数字（`passive.params`）留给原生效果用。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_qiyana.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod terrain;

const ID: &str = "league_qiyana";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_qiyana") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_qiyana";

/// 主包奇亚娜的名字（buff、画面、音效都以它开头）。
fn qy(x: &str) -> String {
    format!("{HERO}_{x}")
}

/// 她自己生命不到这个百分比：草丛（伪装逃走）。
pub const GRASS_HP: usize = 35;
/// ……或者不到这个百分比，身边 `CROWD_R` 内又有两名以上敌方英雄。
pub const CROWDED_HP: usize = 60;
pub const CROWD_R: u64 = 40_000;
/// 落地时看这么远内的地形（两格；英雄联盟的 W 朝身边的地形放）。
pub const NEAR: f64 = 64_000.0;
/// league_ivern 给站在艾翁草丛里的英雄挂的标记（用户 2026-10-22：「还有奇安娜也可以触发元素 艾翁的这个草 你们两可以联动一下」）。
pub const IVERN_BRUSH: &str = "league_ivern_in_brush";

fn me_in_ivern_brush(sim: &StableSim<'_>, me: usize) -> bool {
    sim.get_entity(me).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == IVERN_BRUSH))
}

/// 同一类日志隔这么多 tick 才再写。
const LOG_EVERY: usize = 120;

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

/// 被动的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub rp_dmg: usize,
    pub rp_ratio: usize,
    pub rp_rest: usize,
    pub q_rock: usize,
    pub q_rock_r: usize,
    pub q_exec: usize,
    pub w_as: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { rp_dmg: 40, rp_ratio: 50, rp_rest: 600, q_rock: 25, q_rock_r: 40, q_exec: 50, w_as: 25 }
    }
}

/// `{"rp_dmg":25,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "rp_dmg" => &mut p.rp_dmg,
            "rp_ratio" => &mut p.rp_ratio,
            "rp_rest" => &mut p.rp_rest,
            "q_rock" => &mut p.q_rock,
            "q_rock_r" => &mut p.q_rock_r,
            "q_exec" => &mut p.q_exec,
            "w_as" => &mut p.w_as,
            _ => continue,
        };
        *slot = v;
    }
    p
}

/// 每份模拟的编号（2026-11-01 复查；league_galio 的做法）：被动第一次出生时抽一个，每次出生挂在她身上（buff `SIM_TAG<n>`）。
/// 以前按 sim 种子分：服务器并排跑的两份预演种子一样，第二份的凌人贵气被第一份记的时间挡掉。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
pub const SIM_TAG: &str = "league_qiyana_sim:";

fn sim_no(sim: &StableSim<'_>, id: usize) -> u64 {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .find_map(|b| b.name().strip_prefix(SIM_TAG).and_then(|v| v.parse().ok()))
            .unwrap_or(0)
    })
}

/// 每局的被动参数，给原生效果用：(这份模拟的编号, 她) -> 参数（league_naafiri 的做法；服务端预模拟和画面各算各的）。
static PARAMS: Mutex<Vec<((u64, usize), Params)>> = Mutex::new(Vec::new());

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
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
}

/// 落地时的局势。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Spot {
    /// 她自己的生命百分比。
    pub my_hp: usize,
    /// `CROWD_R` 内的敌方英雄数。
    pub foes_near: usize,
    /// 突进的目标是英雄。
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
    /// 身边没有地形：按局势。
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

fn pct(hp: usize, max: usize) -> usize {
    hp * 100 / max.max(1)
}

/// 岩石的额外伤害：目标生命不到 `q_exec`% 时 2 x (`q_rock` + `q_rock_r`% 攻击力)，否则 0。
pub fn rock_damage(p: &Params, attack: usize, hp: usize, max: usize) -> usize {
    if pct(hp, max) <= p.q_exec {
        2 * (p.q_rock + attack * p.q_rock_r / 100)
    } else {
        0
    }
}

// ===================== 凌人贵气：每个敌人一次 =====================

/// (这份模拟的编号, 她, 敌人) -> 上一次加伤的 tick。
static ROYAL: Mutex<Vec<((u64, usize, usize), usize)>> = Mutex::new(Vec::new());

/// 这一 tick 对这个敌人加不加伤（加的话记下）。
pub fn royal_ready(seed: u64, me: usize, target: usize, tick: usize, rest: usize) -> bool {
    let key = (seed, me, target);
    let mut all = ROYAL.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(slot) = all.iter_mut().find(|(k, _)| *k == key) {
        if tick >= slot.1 && tick - slot.1 < rest {
            return false;
        }
        slot.1 = tick;
        return true;
    }
    all.push((key, tick));
    if all.len() > 4096 {
        all.drain(..1024);
    }
    true
}

fn target_of(input: InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

struct Royal;
impl StableEffectType for Royal {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(target) = target_of(input) else { return };
        let Some(atk) = sim.get_entity(caster).map(|e| e.stat().attack) else { return };
        if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
            return;
        }
        let p = params_of(sim, caster);
        if royal_ready(sim_no(sim, caster), caster, target, sim.tick(), p.rp_rest) {
            sim.deal_damage(caster, target, p.rp_dmg + atk * p.rp_ratio / 100, 0, AttackTypeV1::Skill);
            let at = InputTargetV1::target(target);
            sim.play_view_effect(&qy("p_hit"), caster, &at, 0, 0, 0);
            sim.play_sfx(&qy("p_hit"), caster, &at);
        }
    }
}

struct Rock;
impl StableEffectType for Rock {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(target) = target_of(input) else { return };
        let Some(atk) = sim.get_entity(caster).map(|e| e.stat().attack) else { return };
        let Some((hp, max, champion)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| {
            let (hp, max) = e.hp();
            (hp, max, e.is_champion())
        }) else { return };
        let p = params_of(sim, caster);
        let d = rock_damage(&p, atk, hp, max);
        if d > 0 {
            sim.deal_damage(caster, target, d, 0, AttackTypeV1::Skill);
            if champion {
                wlog(format!("{} ROCK #{target}: hp {hp}/{max}, {d} more before armour", head(sim, caster)));
            }
        }
    }
}

struct Enchant {
    last: Mutex<Option<(usize, Element)>>,
}

impl StableEffectType for Enchant {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(me) = sim.get_entity(caster) else { return };
        let (hp, max) = me.hp();
        let team = me.team();
        let foes_near = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive() && u.team() != team)
            .filter(|u| sim.distance_sq(caster, u.id()) <= CROWD_R.saturating_mul(CROWD_R))
            .count();
        let (champion, target_hp) = target_of(input)
            .and_then(|t| sim.get_entity(t))
            .map_or((false, 100), |t| {
                let (h, m) = t.hp();
                (t.is_champion(), pct(h, m))
            });
        let p = params_of(sim, caster);
        let spot = Spot { my_hp: pct(hp, max), foes_near, champion, target_hp };
        let (x, y) = me.pos();
        let points: Vec<(f64, f64)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_alive())
            .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
            .collect();
        let mut near = terrain::pick_map(&points, &terrain::maps())
            .map_or_else(terrain::Near::default, |m| terrain::near(&m, x as f64, y as f64, NEAR));
        if me_in_ivern_brush(sim, caster) {
            near.grass = Some(0.0);                     // standing in Ivern's brush: grass right here
        }
        let (el, why) = pick(&near, &spot, p.q_exec);
        for f in ["el_g", "el_w", "el_r", "el_on"] {
            sim.entity_remove_buff(caster, &qy(f));
        }
        let mut on = BuffV1::named(&qy("el_on"));
        on.attack_speed_mult = p.w_as as i32;
        sim.add_buff(caster, &on);
        sim.add_buff(caster, &BuffV1::named(&qy(el.flag())));
        let tick = sim.tick();
        let mut last = self.last.lock().unwrap_or_else(|e| e.into_inner());
        if last.is_none_or(|(t0, e0)| e0 != el || tick >= t0 + LOG_EVERY) {
            *last = Some((tick, el));
            let d = |v: Option<f64>| v.map_or("-".to_string(), |d| format!("{d:.0}"));
            wlog(format!("{} ELEMENT {el:?} by {why:?} at ({x}, {y}): grass {} rock {} river {}; {spot:?}", head(sim, caster),
                         d(near.grass), d(near.rock), d(near.river)));
        }
    }
}

// ===================== 被动：只留参数 =====================

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
        wlog(format!("{} SPAWN: the add-on's Qiyana (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Qiyana: the element by the terrain beside her, else by the situation, Royal Privilege per enemy, the rock execute) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:empress"), Empress::default());
    module.add_native_effect(format!("{ID}:element"), Enchant { last: Mutex::new(None) });
    module.add_native_effect(format!("{ID}:royal"), Royal);
    module.add_native_effect(format!("{ID}:rock"), Rock);
    host.log(LogLevel::Info, "league_qiyana loaded (Qiyana's elements by the terrain beside her, else by the situation, Royal Privilege per enemy, the rock execute).");
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
        // nothing beside her: by the situation
        assert_eq!(pick(&Near::default(), &healthy, 50), (Element::River, Why::Situation));
        assert_eq!(pick(&Near::default(), &spot(90, 0, false, 100), 50), (Element::Rock, Why::Situation));
    }

    #[test]
    fn rock_only_under_the_threshold() {
        let p = Params::default();
        assert_eq!(rock_damage(&p, 100, 500, 1000), 2 * (25 + 40));
        assert_eq!(rock_damage(&p, 100, 510, 1000), 0);
    }

    #[test]
    fn royal_privilege_once_per_enemy_per_rest() {
        assert!(royal_ready(7, 1, 10, 100, 600));
        assert!(!royal_ready(7, 1, 10, 200, 600));
        assert!(royal_ready(7, 1, 11, 200, 600)); // another enemy
        assert!(royal_ready(7, 1, 10, 700, 600)); // rested
        assert!(royal_ready(8, 1, 10, 200, 600)); // another game
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"rp_rest":300,"q_exec":40,"x":1}"#),
                   Params { rp_rest: 300, q_exec: 40, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_names_fit() {
        for x in ["el_g", "el_w", "el_r", "el_on", "p_hit"] {
            assert!(qy(x).len() <= BUFF_NAME_CAP);
        }
    }
}
