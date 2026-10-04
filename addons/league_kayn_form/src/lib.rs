//! 凯隐附加包：被动「暗裔魔镰」照英雄联盟——打近战英雄攒暗裔、打远程英雄攒影流，变身后永久（复活也保留）。
//!
//! 主包（纯数据）读不到目标是近战还是远程，只能「技能打中身边英雄攒暗裔、W 只打中远处英雄攒影流」，
//! 而且数据 buff 死亡就清掉，形态每条命重攒。`mod.override_info` 把主包的凯隐换成 `override/` 里的副本
//! （`make_override.py` 从主包生成）：
//!
//! - 主包里四处攒能量的数据块（开头有 `league_kayn_mk_charge` 标记）换成「在打中的英雄身上挂
//!   `league_kayn_tag` 30 tick」，普攻打中英雄也挂；
//! - 普攻第 1 tick 多一段：身上有 `league_kayn_ready_d` / `_s` 就播主包的变身（动作、画面、声音、永久的
//!   形态 buff `league_kayn_form_d` / `_s`），并去掉准备标记；
//! - `passive` 挂本包的被动 `league_kayn_form:orbs`（参数 `darkin_need`、`shadow_need`）。
//!
//! 被动 `orbs` 每 tick 看敌方英雄身上的标记：每一层算一次命中，按英雄 id 查攻击距离（`ranges.rs`：原版英雄
//! 来自游戏数据，本包英雄来自各自的技能文件），`RANGED_FROM` 以上算远程（影流），以下算近战（暗裔）；
//! 查不到的英雄（别的 mod）按挂标记那一刻离凯隐多远猜：`NEAR_UNKNOWN` 以外算远程。数完去掉标记。
//! 哪边先满就给凯隐挂准备标记（等下一次普攻变身），形态记在被动里（被动在玩家身上，死了不丢）：
//! 复活（`on_spawn`）和之后每 tick 发现身上没有形态 buff、也没有准备标记时直接补上永久的形态 buff
//! （光环跟着回来，变身动作只播第一次）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kayn_form.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

mod ranges;

const ID: &str = "league_kayn_form";

/// 主包（本包的副本）在凯隐打中的英雄身上挂的标记，每次命中一层，30 tick。
pub const TAG: &str = "league_kayn_tag";
/// 本包 → 数据：下一次普攻变身。
pub const READY_D: &str = "league_kayn_ready_d";
pub const READY_S: &str = "league_kayn_ready_s";
/// 数据的永久形态 buff（带光环画面）。
pub const FORM_D: &str = "league_kayn_form_d";
pub const FORM_S: &str = "league_kayn_form_s";
/// 准备标记最多等这么久（一分钟内总会普攻）。
pub const READY_T: usize = 3600;
/// 攻击距离到这么远算远程英雄（本包和原版的近战 23000-30000，远程 40000 以上）。
pub const RANGED_FROM: u32 = 35_000;
/// 查不到攻击距离的英雄：挂标记时离凯隐这么远以外算远程。
pub const NEAR_UNKNOWN: f64 = 30_000.0;
/// 参数缺了时的门槛（主包副本里写的是 14 / 14）。
pub const NEED: u32 = 14;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KAYN_FORM_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_kayn_form.log");
        }
    }
    PathBuf::from("league_kayn_form.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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
    format!("[{kind} m={} s={}] t={} {}", m(o.match_id), m(o.set_index), sim.tick(), who(sim, id))
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    let name = sim.get_entity(id).and_then(|e| e.name()).unwrap_or_default();
    format!("#{id} {name}")
}

// ===================== 近战 / 远程 =====================

/// 形态。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Form {
    Darkin,
    Shadow,
}

impl Form {
    pub fn buff(self) -> &'static str {
        match self {
            Form::Darkin => FORM_D,
            Form::Shadow => FORM_S,
        }
    }
    pub fn ready(self) -> &'static str {
        match self {
            Form::Darkin => READY_D,
            Form::Shadow => READY_S,
        }
    }
    fn label(self) -> &'static str {
        match self {
            Form::Darkin => "DARKIN",
            Form::Shadow => "SHADOW",
        }
    }
}

/// 这个英雄的攻击距离（查不到时 None）。
pub fn attack_range(name: &str) -> Option<u32> {
    ranges::RANGES.iter().find(|(n, _)| *n == name).map(|(_, r)| *r)
}

/// 打中这个英雄攒哪一边：远程英雄攒影流，近战英雄攒暗裔；查不到的按离凯隐多远猜。
pub fn charges(name: &str, dist_from_kayn: f64) -> Form {
    let ranged = match attack_range(name) {
        Some(r) => r >= RANGED_FROM,
        None => dist_from_kayn > NEAR_UNKNOWN,
    };
    if ranged {
        Form::Shadow
    } else {
        Form::Darkin
    }
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buffs(sim, id).iter().any(|b| b.name() == name)
}

/// 从被动参数（排好序的整数 JSON，如 `{"darkin_need":14,"shadow_need":14}`）读一个值。
pub fn param(json: &str, key: &str) -> Option<u32> {
    let at = json.find(&format!("\"{key}\""))?;
    let rest = json[at + key.len() + 2..].trim_start().strip_prefix(':')?.trim_start();
    let end = rest.find(|c: char| !c.is_ascii_digit()).unwrap_or(rest.len());
    rest[..end].parse().ok()
}

/// 每个凯隐一份（在玩家身上，死了不丢）：两边的命中数、门槛、定下的形态。
#[derive(Clone, Debug)]
pub struct Orbs {
    pub darkin: u32,
    pub shadow: u32,
    pub need_d: u32,
    pub need_s: u32,
    pub form: Option<Form>,
}

impl Default for Orbs {
    fn default() -> Self {
        Orbs { darkin: 0, shadow: 0, need_d: NEED, need_s: NEED, form: None }
    }
}

impl Orbs {
    /// 记一次命中；哪边先满就定下形态（返回刚定下的形态）。
    pub fn count(&mut self, f: Form) -> Option<Form> {
        if self.form.is_some() {
            return None;
        }
        match f {
            Form::Darkin => self.darkin += 1,
            Form::Shadow => self.shadow += 1,
        }
        if self.darkin >= self.need_d {
            self.form = Some(Form::Darkin);
        } else if self.shadow >= self.need_s {
            self.form = Some(Form::Shadow);
        }
        self.form
    }

    /// 身上没有形态 buff、也没有准备标记时补上永久的形态 buff（复活后、或主包的变身没播成）。
    fn keep_form(&self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let Some(f) = self.form else { return };
        if has_buff(sim, me, f.buff()) || has_buff(sim, me, f.ready()) {
            return;
        }
        sim.add_buff(me, &BuffV1::named(f.buff()));
        wlog(format!("{} {} form restored ({why})", head(sim, me), f.label()));
    }
}

impl StablePassive for Orbs {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.need_d = param(params_json, "darkin_need").unwrap_or(NEED).max(1);
        self.need_s = param(params_json, "shadow_need").unwrap_or(NEED).max(1);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.keep_form(sim, me, "respawn");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(k) = sim.get_entity(me) else { return };
        if !k.is_alive() {
            return;
        }
        let team = k.team();
        let (kx, ky) = k.pos();
        // 敌方英雄身上的标记：每一层是凯隐的一次命中
        let mut hits: Vec<(usize, String, f64, usize)> = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || e.team() == team {
                continue;
            }
            let n = (0..e.buff_count()).filter_map(|j| e.buff_at(j)).filter(|b| b.name() == TAG).count();
            if n == 0 {
                continue;
            }
            let (x, y) = e.pos();
            let d = ((x as f64 - kx as f64).powi(2) + (y as f64 - ky as f64).powi(2)).sqrt();
            hits.push((e.id(), e.name().unwrap_or_default(), d, n));
        }
        for (id, name, d, n) in hits {
            sim.entity_remove_buff(id, TAG);
            let f = charges(&name, d);
            for _ in 0..n {
                if let Some(form) = self.count(f) {
                    sim.add_buff(me, &BuffV1::timed(form.ready(), READY_T));
                    wlog(format!(
                        "{} {} ready: darkin {}/{} shadow {}/{} (last hit #{id} {name}, range {:?})",
                        head(sim, me),
                        form.label(),
                        self.darkin,
                        self.need_d,
                        self.shadow,
                        self.need_s,
                        attack_range(&name)
                    ));
                }
            }
        }
        self.keep_form(sim, me, "no form buff");
    }
}

fn init(host: &StableHost) -> StableMod {
    // 上一次启动的日志留一份（.prev.log），重启游戏不丢
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v0.1 (melee hits charge the Darkin, ranged the Shadow Assassin; the form stays) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let mut module = StableMod::new(ID);
    module.add_native_passive(format!("{ID}:orbs"), Orbs::default());
    host.log(LogLevel::Info, "league_kayn_form loaded (Kayn's Darkin Scythe as in League: melee/ranged hits, the form survives death).");
    module
}

declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn melee_hits_charge_the_darkin_and_ranged_the_shadow() {
        assert_eq!(charges("fighter", 10_000.0), Form::Darkin);
        assert_eq!(charges("archer", 10_000.0), Form::Shadow);
        assert_eq!(charges("league_jinx", 10_000.0), Form::Shadow);
        assert_eq!(charges("league_garen", 50_000.0), Form::Darkin);
        // 查不到的英雄：按距离
        assert_eq!(charges("someone_elses_hero", 10_000.0), Form::Darkin);
        assert_eq!(charges("someone_elses_hero", 45_000.0), Form::Shadow);
    }

    #[test]
    fn the_first_full_side_is_the_form() {
        let mut o = Orbs { need_d: 3, need_s: 2, ..Default::default() };
        assert_eq!(o.count(Form::Darkin), None);
        assert_eq!(o.count(Form::Darkin), None);
        assert_eq!(o.count(Form::Shadow), None);
        assert_eq!(o.count(Form::Shadow), Some(Form::Shadow));
        // 定下以后不再变
        assert_eq!(o.count(Form::Darkin), None);
        assert_eq!(o.form, Some(Form::Shadow));
    }

    #[test]
    fn params_are_read_from_the_passive_json() {
        assert_eq!(param(r#"{"darkin_need":14,"shadow_need":9}"#, "darkin_need"), Some(14));
        assert_eq!(param(r#"{"darkin_need":14,"shadow_need":9}"#, "shadow_need"), Some(9));
        assert_eq!(param(r#"{"darkin_need": 7}"#, "darkin_need"), Some(7));
        assert_eq!(param("{}", "darkin_need"), None);
        let mut o = Orbs::default();
        o.configure(r#"{"darkin_need":5,"shadow_need":6}"#);
        assert_eq!((o.need_d, o.need_s), (5, 6));
    }
}
