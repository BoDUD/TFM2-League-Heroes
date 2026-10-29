//! 瑟庄妮附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做。
//!
//! `mod.override_info` 把主包的瑟庄妮换成 `override/` 里的副本（tools/kit/build_sejuani.py --native），`passive` 换成本包的
//! `league_sejuani:frost`：
//!
//! - **霜冻层数记在每个敌人身上**：副本的普攻和 W 每打中一个敌方英雄，就往它身上挂一层 `league_sejuani_frost`（主包读不到
//!   目标身上的 buff，只能在瑟庄妮身上共用一个计数）。本包每 tick 数每个敌方英雄身上的层数，满 `f_n` 层就摘掉、把它
//!   冻住（晕 `e_stun` tick，`e_dmg` + `e_ap`% 法强的魔法伤害）——永冻领域。
//! - **碎冰对谁的晕眩都算**：她的普攻和 W 打中敌方英雄时挂 3 tick 的 `league_sejuani_hit`；本包看到这个标记时，那个英雄
//!   正被晕住或击飞（不管是谁控的，队友的也算），就碎冰：`sh_dmg` + `sh_ap`% 法强 + 它最大生命的 `sh_pct`% 魔法伤害，
//!   同一个英雄 `sh_cd` tick 一次。标记看一次就摘，冻住的那一下不会马上碎。
//! - **冰霜护甲免疫减速**：她身上有 `league_sejuani_fa`（冰霜护甲）时，每 tick 摘掉身上所有减速（移速为负的 buff）；
//!   游戏没有「免疫减速」，主包用韧性代替，副本不给韧性。她**受到伤害**也算进入战斗（主包只看她自己出手）：
//!   刷新 `league_sejuani_fight`（`fa_out` tick），护甲就不再续。
//! - **极寒突袭撞到第一个敌方英雄就停**：副本 Q 撞到第一个英雄时给她挂 `league_sejuani_q_stop`；本包记下她这时的位置，
//!   冲锋剩下的 `q_t` tick 里把她按在原地。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sejuani.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_sejuani";
/// A Frost stack on an enemy champion (build_sejuani.py native: `buff("frost", f_t)`).
const FROST: &str = "league_sejuani_frost";
/// Her attack / W hit this champion (3 ticks): the shatter looks at it once.
const HIT: &str = "league_sejuani_hit";
/// The Frost Armour on her (the data's controller renews it while she is out of combat).
const ARMOUR: &str = "league_sejuani_fa";
/// In combat: the data renews it when she attacks or casts, this add-on when she takes damage.
const FIGHT: &str = "league_sejuani_fight";
/// Arctic Assault hit its first enemy champion (a 2-tick caster flag).
const Q_STOP: &str = "league_sejuani_q_stop";
/// Crowd control that counts as stunned for the shatter.
const STUNNED: [CcKindV1; 2] = [CcKindV1::Stun, CcKindV1::Airborne];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SEJUANI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_sejuani.log");
        }
    }
    PathBuf::from("league_sejuani.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
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

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 几层霜冻冻住。
    pub f_n: usize,
    /// 冻住多少 tick。
    pub e_stun: usize,
    /// 冻住的魔法伤害：固定值 + 法强百分比。
    pub e_dmg: usize,
    pub e_ap: usize,
    /// 同一个英雄两次碎冰至少隔多少 tick。
    pub sh_cd: usize,
    /// 碎冰的魔法伤害：固定值 + 法强百分比 + 目标最大生命百分比。
    pub sh_dmg: usize,
    pub sh_ap: usize,
    pub sh_pct: usize,
    /// 极寒突袭冲锋多少 tick（撞到英雄后按住她这么久）。
    pub q_t: usize,
    /// 受伤后多少 tick 内算在战斗中（冰霜护甲不续）。
    pub fa_out: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { f_n: 4, e_stun: 60, e_dmg: 60, e_ap: 40, sh_cd: 300, sh_dmg: 30, sh_ap: 40, sh_pct: 6, q_t: 8, fa_out: 300 }
    }
}

/// `{"f_n":4,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "f_n" => p.f_n = v,
            "e_stun" => p.e_stun = v,
            "e_dmg" => p.e_dmg = v,
            "e_ap" => p.e_ap = v,
            "sh_cd" => p.sh_cd = v,
            "sh_dmg" => p.sh_dmg = v,
            "sh_ap" => p.sh_ap = v,
            "sh_pct" => p.sh_pct = v,
            "q_t" => p.q_t = v,
            "fa_out" => p.fa_out = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

/// Permafrost's magic damage before resistance.
pub fn freeze_damage(p: &Params, magic_power: usize) -> usize {
    p.e_dmg + p.e_ap * magic_power / 100
}

/// The shatter's magic damage before resistance.
pub fn shatter_damage(p: &Params, magic_power: usize, target_max_hp: usize) -> usize {
    p.sh_dmg + p.sh_ap * magic_power / 100 + p.sh_pct * target_max_hp / 100
}

/// A buff that slows (the Frost Armour clears those). Not the game's own `sed_*` bookkeeping (`sed_reward` sits on
/// every champion with a speed value below 0 and comes back each second: 0.1.x stripped it ~once a second).
pub fn is_slow(b: &BuffV1) -> bool {
    b.move_speed_mult < 0 && !b.name().starts_with("sed_")
}

fn count(e: &StableEntity<'_, '_>, name: &str) -> usize {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count()
}

fn stunned(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| STUNNED.iter().any(|k| k.code() == c.kind))
}

// ===================== 被动 =====================

/// 每个瑟庄妮一份：参数、Q 按住的位置、每个英雄的碎冰冷却、日志计数。
#[derive(Clone, Default)]
struct Frost {
    p: Params,
    /// Arctic Assault stopped here: hold her until this tick.
    pin: Option<(u64, u64, usize)>,
    /// (champion id, tick its shatter is ready again).
    sh_ready: Vec<(usize, usize)>,
    freezes: usize,
    shatters: usize,
    slows: usize,
    stops: usize,
}

impl Frost {
    fn shatter_ready(&self, id: usize, tick: usize) -> bool {
        self.sh_ready.iter().all(|&(c, at)| c != id || tick >= at)
    }

    fn set_shatter_cd(&mut self, id: usize, at: usize) {
        self.sh_ready.retain(|&(c, _)| c != id);
        self.sh_ready.push((id, at));
    }

    /// Arctic Assault: hold her where she hit the first champion until the charge would have ended.
    fn charge(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let has = sim.get_entity(me).is_some_and(|e| count(&e, Q_STOP) > 0);
        if has {
            sim.entity_remove_buff(me, Q_STOP);
            if let Some(e) = sim.get_entity(me) {
                let (x, y) = e.pos();
                self.pin = Some((x, y, tick + self.p.q_t));
                self.stops += 1;
                if self.stops <= 40 || self.stops % 100 == 0 {
                    wlog(format!("{} STOP Arctic Assault at its first champion ({x}, {y}), held {} ticks ({} stops)",
                                 head(sim, me), self.p.q_t, self.stops));
                }
            }
        }
        if let Some((x, y, until)) = self.pin {
            if tick < until {
                sim.entity_set_pos(me, x, y);
            } else {
                self.pin = None;
            }
        }
    }

    /// The Frost Armour: no slows on her while it lasts.
    fn armour(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if count(&e, ARMOUR) == 0 {
            return;
        }
        let mut slows: Vec<String> = (0..e.buff_count())
            .filter_map(|i| e.buff_at(i))
            .filter(is_slow)
            .map(|b| b.name().to_string())
            .collect();
        slows.sort();
        slows.dedup();
        for name in &slows {
            sim.entity_remove_buff(me, name);
            self.slows += 1;
            if self.slows <= 40 || self.slows % 100 == 0 {
                wlog(format!("{} SLOW {name} cleared by the Frost Armour ({} in all)", head(sim, me), self.slows));
            }
        }
    }

    /// The shatter and Permafrost on every enemy champion.
    fn champions(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let ap = e.stat().magic_power;
        let ids: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
        for id in ids {
            let Some(c) = sim.get_entity(id) else { continue };
            if c.team() == team || !c.is_alive() {
                continue;
            }
            let hits = count(&c, HIT);
            let frost = count(&c, FROST);
            let stun = stunned(&c);
            let (_, max) = c.hp();
            let on = InputTargetV1::target(id);
            // the shatter: her hit on a champion stunned by anyone (the mark is read once)
            if hits > 0 {
                sim.entity_remove_buff(id, HIT);
                if stun && self.shatter_ready(id, tick) {
                    let dmg = shatter_damage(&self.p, ap, max);
                    sim.deal_damage(me, id, 0, dmg, AttackTypeV1::Skill);
                    sim.play_view_effect(&format!("{ID}_sh_hit"), me, &on, 0, 0, 0);
                    sim.play_sfx(&format!("{ID}_sh_hit"), me, &on);
                    self.set_shatter_cd(id, tick + self.p.sh_cd);
                    self.shatters += 1;
                    if self.shatters <= 60 || self.shatters % 100 == 0 {
                        wlog(format!("{} SHATTER {} ({dmg} magic before resistance, max hp {max}; {} in all)",
                                     head(sim, me), name_of(sim, id), self.shatters));
                    }
                }
            }
            // Permafrost: f_n Frost stacks freeze it
            if frost >= self.p.f_n {
                sim.entity_remove_buff(id, FROST);
                sim.apply_cc(id, &CcV1::stun(self.p.e_stun as u64));
                let dmg = freeze_damage(&self.p, ap);
                sim.deal_damage(me, id, 0, dmg, AttackTypeV1::Skill);
                sim.play_view_effect(&format!("{ID}_e_freeze"), me, &on, 0, 0, 0);
                sim.play_sfx(&format!("{ID}_e_freeze"), me, &on);
                self.freezes += 1;
                if self.freezes <= 60 || self.freezes % 100 == 0 {
                    wlog(format!("{} FREEZE {} ({frost} Frost, stunned {} ticks, {dmg} magic before resistance; {} in all)",
                                 head(sim, me), name_of(sim, id), self.p.e_stun, self.freezes));
                }
            }
        }
    }
}

impl StablePassive for Frost {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.pin = None;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Sejuani (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _attacker: usize, damage: usize) {
        if damage == 0 {
            return;
        }
        // hurt = in combat: the Frost Armour stops being renewed (League: it lingers a moment after damage)
        sim.entity_remove_buff(me, FIGHT);
        sim.add_buff(me, &BuffV1::timed(FIGHT, self.p.fa_out));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        if !alive {
            self.pin = None;
            return;
        }
        let tick = sim.tick();
        self.charge(sim, me, tick);
        self.armour(sim, me);
        self.champions(sim, me, tick);
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.pin = None;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Frost on each champion, the shatter on anyone's stun, slow immunity, Q stops at a champion) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:frost"), Frost::default());
    host.log(LogLevel::Info, "league_sejuani v1 loaded (Sejuani: Frost per champion, shatter, slow immunity, Q stop).");
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
        let p = parse_params(r#"{"e_ap":50,"e_dmg":30,"e_stun":70,"f_n":3,"fa_out":240,"q_t":9,"sh_ap":30,"sh_cd":200,"sh_dmg":10,"sh_pct":8,"x":1}"#);
        assert_eq!(p, Params { f_n: 3, e_stun: 70, e_dmg: 30, e_ap: 50, sh_cd: 200, sh_dmg: 10, sh_ap: 30, sh_pct: 8, q_t: 9,
                               fa_out: 240 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn damage_follows_the_numbers() {
        let p = Params::default();
        assert_eq!(freeze_damage(&p, 100), 100);
        assert_eq!(shatter_damage(&p, 100, 2000), 30 + 40 + 120);
    }

    #[test]
    fn only_negative_move_speed_is_a_slow() {
        let mut b = BuffV1::timed("league_x_slow", 30);
        b.move_speed_mult = -40;
        assert!(is_slow(&b));
        b.move_speed_mult = 15;
        assert!(!is_slow(&b));
        assert!(!is_slow(&BuffV1::timed(ARMOUR, 3)));
        let mut g = BuffV1::named("sed_reward");
        g.move_speed_mult = -1;
        assert!(!is_slow(&g), "the game's own sed_ buffs are not slows");
    }

    #[test]
    fn the_shatter_waits_per_champion() {
        let mut f = Frost::default();
        assert!(f.shatter_ready(7, 0));
        f.set_shatter_cd(7, 300);
        assert!(!f.shatter_ready(7, 299));
        assert!(f.shatter_ready(7, 300));
        assert!(f.shatter_ready(8, 10));
        f.set_shatter_cd(7, 500);
        assert_eq!(f.sh_ready.len(), 1);
    }

    #[test]
    fn names_are_the_data_s() {
        for n in [FROST, HIT, ARMOUR, FIGHT, Q_STOP] {
            assert!(n.starts_with("league_sejuani_"), "{n}");
        }
    }
}
