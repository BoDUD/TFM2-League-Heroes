//! 塞拉斯附加包（用户选「做，含按类别偷大招+连招」）：主包数据做不到的两件事，加上连招。
//!
//! `mod.override_info` 把主包的塞拉斯换成 `override/` 里的副本（tools/kit/build_sylas.py 的 native）：数据和主包一样，
//! 只是弑君突刺的回血调本包的 `league_sylas:kingslayer`，R 的锁链打中英雄时在对方身上挂 `league_sylas_r_mark`（3 tick），
//! 第二次 R 按身上的 `league_sylas_cls_<类别>` 换成五套夺来的大招之一，被动挂本包的 `league_sylas:hijack`（参数在英雄数据的
//! `passive.params` 里）。
//!
//! - **其人之道**：英雄联盟里塞拉斯偷走对方的大招。0.2.0 起偷到本包的英雄联盟英雄时，副本的第二段 R 放的就是那名英雄自己的大招
//!   （`make_override.py` 把主包每个英雄的大招效果树整棵抄进来，动作标签换成塞拉斯的 ult_cast / ult_dash，用到的画面条目一并抄来；
//!   被动给塞拉斯挂 `steal_<英雄>` 和 `r_real`），放的时候数据挂 `r_power_go`，被动给他加法强 `r2_ad`% 的攻击（`r2_ad_t` tick），
//!   照英雄联盟把攻击力系数换成法强。偷到原版英雄和别的 mod 的英雄时照佛耶戈附加包的做法分五类：被动每 tick 找
//!   身上有 `r_mark` 的敌方英雄，按它的 id 查 `classes.rs`（原版英雄和本包英雄的类别，`make_override.py` 生成；查不到的别的
//!   mod 英雄算近战），给塞拉斯挂 `cls_<类别>`（`r_keep` tick），第二次 R 放出对应的那一套：近战 = 跃起重砸眩晕、
//!   射手 = 贯穿长箭减速、法师 = 原地爆发击飞（主包那一套）、辅助 = 治疗和护盾周围友方英雄并减速敌人、刺客 = 闪到目标身边重击并隐身。
//! - **弑君突刺**：英雄联盟里回血随已损失生命最多多 150%。`kingslayer` 回 (`w_heal` + `w_heal_r`% 法强) × (1 + `w_miss`% × 已损失
//!   生命比例)。
//! - **连招**（用户：「有连招要做连招」；`combo.rs`）：AI 钩子 `league_sylas:combo` 替游戏的 AI 按 Q、E、R。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sylas.log`，每次启动游戏重写：`SPAWN`、`STEAL`（偷到谁、哪一类）、
//! `HEAL`、连招各条，都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod classes;
pub mod combo;
pub mod stealable;

const ID: &str = "league_sylas";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.2.0";
/// 五个类别（和佛耶戈附加包一样）。
pub const CLASSES: [&str; 5] = ["melee", "range", "mage", "util", "assassin"];

fn sn(x: &str) -> String {
    format!("league_sylas_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SYLAS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_sylas.log");
        }
    }
    PathBuf::from("league_sylas.log")
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub w_heal: usize,
    pub w_heal_r: usize,
    pub w_miss: usize,
    pub w_r: usize,
    pub w_cd: usize,
    pub atk_range: usize,
    pub q_range: usize,
    pub e_range: usize,
    pub e_dur: usize,
    pub r_range: usize,
    pub r_keep: usize,
    pub r2_r: usize,
    pub r_cd: usize,
    pub r_dur: usize,
    pub r2_ad: usize,
    pub r2_ad_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { w_heal: 40, w_heal_r: 35, w_miss: 150, w_r: 34000, w_cd: 540, atk_range: 26000, q_range: 60000,
                 e_range: 70000, e_dur: 34, r_range: 70000, r_keep: 600, r2_r: 32000, r_cd: 2700, r_dur: 30,
                 r2_ad: 60, r2_ad_t: 300 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "w_heal" => p.w_heal = v,
            "w_heal_r" => p.w_heal_r = v,
            "w_miss" => p.w_miss = v,
            "w_r" => p.w_r = v,
            "w_cd" => p.w_cd = v,
            "atk_range" => p.atk_range = v,
            "q_range" => p.q_range = v,
            "e_range" => p.e_range = v,
            "e_dur" => p.e_dur = v,
            "r_range" => p.r_range = v,
            "r_keep" => p.r_keep = v,
            "r2_r" => p.r2_r = v,
            "r_cd" => p.r_cd = v,
            "r_dur" => p.r_dur = v,
            "r2_ad" => p.r2_ad = v,
            "r2_ad_t" => p.r2_ad_t = v,
            _ => {}
        }
    }
    p
}

/// 每个塞拉斯的参数（被动 configure 时存下，原生效果和 AI 钩子里读）：键是 (这局的种子, 他的编号)。
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim.seed(), me)).copied().unwrap_or_default()
}

// ===================== 计算（单元测试用） =====================

/// 弑君突刺回多少：(`w_heal` + `w_heal_r`% 法强) × (1 + `w_miss`% × 已损失生命比例)；`share` 是他现在的生命比例（0–1）。
pub fn kingslayer_heal(ap: usize, share: f64, p: &Params) -> usize {
    let base = p.w_heal as f64 + p.w_heal_r as f64 * ap as f64 / 100.0;
    let missing = (1.0 - share).clamp(0.0, 1.0);
    (base * (1.0 + p.w_miss as f64 / 100.0 * missing)).round() as usize
}

/// 偷到这名英雄时放他自己的大招吗（本包的英雄联盟英雄，`stealable.rs`），放的话是 `steal_<英雄>` 里的英雄名。
pub fn own_ult(name: &str) -> Option<&str> {
    stealable::STEALABLE.binary_search(&name).ok().and_then(|_| name.strip_prefix("league_"))
}

/// 夺来的大招放的时候加多少攻击：法强的 `r2_ad`%（英雄联盟把偷来的大招的攻击力系数换成塞拉斯的法强）。
pub fn power_of(ap: usize, p: &Params) -> i32 {
    (ap * p.r2_ad / 100) as i32
}

/// 英雄 id → 五类之一：查表（本包英雄和原版英雄），查不到的（别的 mod）按攻击距离：35000 以上算射手。
pub fn class_of(name: &str, range: Option<usize>) -> &'static str {
    match classes::CLASSES_OF.binary_search_by(|s| s.0.cmp(name)) {
        Ok(i) => classes::CLASSES_OF[i].1,
        Err(_) if range.unwrap_or(0) >= 35000 => "range",
        Err(_) => "melee",
    }
}

fn share(e: &StableEntity<'_, '_>) -> f64 {
    let (hp, max) = e.hp();
    if max == 0 { 1.0 } else { hp as f64 / max as f64 }
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 原生效果 =====================

/// 弑君突刺：按他已损失的生命回血（主包是固定的 `w_heal` + `w_heal_r`% 法强）。
fn kingslayer(sim: &mut StableSim<'_>, me: usize) {
    let Some(e) = sim.get_entity(me) else { return };
    if !e.is_alive() {
        return;
    }
    let s = share(&e);
    let ap = e.stat().magic_power;
    let p = params_of(sim, me);
    let amount = kingslayer_heal(ap, s, &p);
    sim.heal(me, me, amount);
    if let Some(k) = counted("heal") {
        wlog(format!("{} HEAL #{k}: Kingslayer at {:.0}% health (ap {ap}) - healed {amount}", head(sim, me), s * 100.0));
    }
}

struct KingslayerFx;
impl StableEffectType for KingslayerFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        kingslayer(sim, caster);
    }
}

// ===================== 被动：其人之道 =====================

#[derive(Clone, Default)]
struct Hijack {
    p: Params,
}

impl Hijack {
    fn tick(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        if has_buff(&e, &sn("r_power_go")) {
            let ap = e.stat().magic_power;
            let mut b = BuffV1::timed(&sn("r_power"), self.p.r2_ad_t);
            b.attack = power_of(ap, &self.p);
            sim.entity_remove_buff(me, &sn("r_power_go"));
            sim.entity_remove_buff(me, &sn("r_power"));
            sim.entity_stack_buff(me, &b, 1, true);
            if let Some(k) = counted("power") {
                wlog(format!("{} POWER #{k}: a stolen ult cast - attack +{} for {} ticks (ap {ap})", head(sim, me),
                             b.attack, self.p.r2_ad_t));
            }
        }
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let mark = sn("r_mark");
        let mut robbed = None;
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_champion() || !has_buff(&u, &mark) {
                continue;
            }
            robbed = Some((u.id(), u.name().unwrap_or_default()));
            break;
        }
        let Some((victim, name)) = robbed else { return };
        sim.entity_remove_buff(victim, &mark);
        let cls = class_of(&name, None);
        for c in CLASSES {
            sim.entity_remove_buff(me, &sn(&format!("cls_{c}")));
        }
        let old: Vec<String> = sim.get_entity(me).map_or_else(Vec::new, |e| {
            (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string())
                .filter(|n| n.starts_with(&sn("steal_"))).collect()
        });
        for n in old {
            sim.entity_remove_buff(me, &n);
        }
        sim.entity_remove_buff(me, &sn("r_real"));
        let kind = match own_ult(&name) {
            Some(hero) => {
                sim.entity_stack_buff(me, &BuffV1::timed(&sn(&format!("steal_{hero}")), self.p.r_keep), 1, true);
                sim.entity_stack_buff(me, &BuffV1::timed(&sn("r_real"), self.p.r_keep), 1, true);
                "his own ult".to_string()
            }
            None => {
                sim.entity_stack_buff(me, &BuffV1::timed(&sn(&format!("cls_{cls}")), self.p.r_keep), 1, true);
                format!("by class: {cls}")
            }
        };
        if let Some(k) = counted("steal") {
            wlog(format!("{} STEAL #{k}: the ult of {} ({kind})", head(sim, me), who(sim, victim)));
        }
    }
}

impl StablePassive for Hijack {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert((sim.seed(), me), self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Sylas (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.tick(sim, me);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sylas: Hijack by class, Kingslayer by missing health, the combos) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:kingslayer"), KingslayerFx);
    module.add_native_passive(format!("{ID}:hijack"), Hijack::default());
    module.add_player_input_ai(combo::Combo);
    host.log(LogLevel::Info, "league_sylas loaded (Hijack by class, Kingslayer by missing health, the combos).");
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
    fn kingslayer_heals_more_when_hurt() {
        let p = Params::default();
        assert_eq!(kingslayer_heal(100, 1.0, &p), 75);
        assert_eq!(kingslayer_heal(100, 0.5, &p), 131);
        assert_eq!(kingslayer_heal(100, 0.0, &p), 188);
    }

    #[test]
    fn classes_are_found() {
        assert_eq!(class_of("fighter", None), "melee");
        assert_eq!(class_of("league_jinx", None), "range");
        assert_eq!(class_of("league_lux", None), "mage");
        assert_eq!(class_of("league_soraka", None), "util");
        assert_eq!(class_of("league_zed", None), "assassin");
        assert_eq!(class_of("someone_else", Some(50000)), "range");
        assert_eq!(class_of("someone_else", Some(20000)), "melee");
    }

    #[test]
    fn league_champions_give_their_own_ult() {
        assert_eq!(own_ult("league_jinx"), Some("jinx"));
        assert_eq!(own_ult("league_soraka"), Some("soraka"));
        assert_eq!(own_ult("league_sylas"), None);
        assert_eq!(own_ult("league_mel"), None);        // BY_CLASS: her R strikes only her own stacks
        assert_eq!(own_ult("fighter"), None);
        assert_eq!(own_ult("tft_powder"), None);
        assert!(stealable::STEALABLE.windows(2).all(|w| w[0] < w[1]));
        assert!(stealable::STEALABLE.iter().all(|n| sn(&format!("steal_{}", &n[7..])).len() <= BUFF_NAME_CAP));
    }

    #[test]
    fn the_stolen_ult_pays_attack_from_ability_power() {
        let p = Params::default();
        assert_eq!(power_of(210, &p), 126);
        assert_eq!(power_of(0, &p), 0);
    }

    #[test]
    fn the_table_is_sorted() {
        assert!(classes::CLASSES_OF.windows(2).all(|w| w[0].0 < w[1].0));
        assert!(classes::CLASSES_OF.iter().all(|c| CLASSES.contains(&c.1)));
    }

    #[test]
    fn params_parse() {
        assert_eq!(parse_params(r#"{"w_heal":40,"w_heal_r":35,"w_miss":150,"w_r":34000,"w_cd":540,"atk_range":26000,"q_range":60000,"e_range":70000,"e_dur":34,"r_range":70000,"r_keep":600,"r2_r":32000,"r_cd":2700,"r_dur":30,"r2_ad":60,"r2_ad_t":300}"#), Params::default());
        assert_eq!(parse_params(r#"{"w_heal":30}"#).w_heal, 30);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_sylas.py");
        let src = std::fs::read_to_string(path).expect("build_sylas.py");
        let d = Params::default();
        for (k, v) in [("w_heal", d.w_heal), ("w_heal_r", d.w_heal_r), ("w_miss", d.w_miss), ("w_r", d.w_r),
                       ("w_cd", d.w_cd), ("atk_range", d.atk_range), ("q_range", d.q_range), ("e_range", d.e_range),
                       ("e_dur", d.e_dur), ("r_range", d.r_range), ("r_keep", d.r_keep), ("r2_r", d.r2_r),
                       ("r_cd", d.r_cd), ("r_dur", d.r_dur), ("r2_ad", d.r2_ad), ("r2_ad_t", d.r2_ad_t)] {
            assert!(src.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in build_sylas.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["r_mark", "r_have", "cls_assassin"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
