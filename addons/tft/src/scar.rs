//! 刀疤（`tft_scar`）数据做不到的部分（金铲铲第 13 赛季的野火帮 / 监察，技能按用户选的方案 A「野火坦克」，2026-10-28）。
//! 他的数据（tools/kit/build_scar.py）的 `passive` 是这里的 `tft_scar:firelight`，参数从数据的 `passive.params` 来
//! （build_scar.py 从参数表 P 写进去，`NATIVE_KEYS`），按他的单位编号记一份给效果用：
//!
//! - **野火冲刺**：冲刺本身（滑板冲到目标身上捅一矛）是数据的普攻；数据在冲刺打中时给他挂 2 拍的 `tft_scar_p_surf`。
//!   被动记下他这条命从上次冲刺以来受到的伤害（`on_damaged`），看到 `p_surf` 就回复其中的 `p_heal`%，亮 `p_heal`。
//! - **监察**：数据读不到生命。被动每拍看他的生命：不低于 `w_line`% 时减伤 `w_hi`%，低于时 `w_lo`%（`tft_scar_w_watch`）。
//! - **水坑狙击惊喜**（`tft_scar:bombs`：技能出手）：`q_range` 以内**最近**的 `q_n` 个敌人（先英雄再小兵野怪，不重复）各
//!   飞去一颗炸弹（`tft_scar_q_bomb`）；炸弹打中（`tft_scar:bomb`）造成 `q_dmg` + 法强 `q_ap`% 魔法伤害、晕眩 `q_stun` 拍。
//!   他自己的回复是数据的。
//!
//! 长矛横扫和野火突袭是数据自己的。只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_scar.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_scar";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const BOMB_FX: &str = "tft_scar:bomb";
/// The sounds tft.dll plays itself (the tft pack's sound_info; the rest the data plays).
const SFX_HEAL: &str = "tft_scar_p_heal";
const SFX_BOMB_HIT: &str = "tft_scar_q_hit";

fn sc(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SCAR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_scar.log");
        }
    }
    PathBuf::from("tft_scar.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;
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
        _ => "unknown",
    };
    format!("[{kind} t={}] #{id}", sim.tick())
}

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n} #{id}"))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 野火冲刺：回复上次冲刺以来所受伤害的 p_heal%。
    pub p_heal: usize,
    /// 监察：生命不低于 w_line% 时减伤 w_hi%，低于时 w_lo%。
    pub w_line: usize,
    pub w_lo: usize,
    pub w_hi: usize,
    /// 水坑狙击惊喜：q_range 以内最近的 q_n 个敌人，炸弹速度 q_speed，q_dmg + 法强 q_ap% 魔法伤害，晕眩 q_stun 拍。
    pub q_range: usize,
    pub q_n: usize,
    pub q_speed: usize,
    pub q_dmg: usize,
    pub q_ap: usize,
    pub q_stun: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_heal: 25,
            w_line: 50,
            w_lo: 10,
            w_hi: 20,
            q_range: 45000,
            q_n: 3,
            q_speed: 2400,
            q_dmg: 70,
            q_ap: 80,
            q_stun: 60,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        let u = v.max(0) as usize;
        match k {
            "p_heal" => p.p_heal = u.min(100),
            "w_line" => p.w_line = u.min(100),
            "w_lo" => p.w_lo = u.min(100),
            "w_hi" => p.w_hi = u.min(100),
            "q_range" => p.q_range = u,
            "q_n" => p.q_n = u,
            "q_speed" => p.q_speed = u.max(1),
            "q_dmg" => p.q_dmg = u,
            "q_ap" => p.q_ap = u,
            "q_stun" => p.q_stun = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== 规则（单元测试用） =====================

/// (id, position, is a champion)
pub type Foe = (usize, (u64, u64), bool);

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// The bombs' targets: the `n` nearest enemies within `reach` of `at`, champions first (then the nearer, then the
/// lower id), each once.
pub fn nearest(foes: &[Foe], at: (u64, u64), reach: u64, n: usize) -> Vec<usize> {
    let r2 = (reach as u128) * (reach as u128);
    let mut near: Vec<&Foe> = foes.iter().filter(|f| dist_sq(f.1, at) <= r2).collect();
    near.sort_by_key(|f| (!f.2, dist_sq(f.1, at), f.0));
    near.into_iter().take(n).map(|f| f.0).collect()
}

/// Watcher's damage reduction at `hp` of `max`.
pub fn watch(p: &Params, hp: usize, max: usize) -> usize {
    if max > 0 && hp * 100 >= max * p.w_line { p.w_hi } else { p.w_lo }
}

/// The dash's heal: p_heal% of the damage taken since the last dash.
pub fn dash_heal(p: &Params, taken: usize) -> usize {
    taken * p.p_heal / 100
}

/// A bomb's magic damage before resistances.
pub fn bomb_damage(p: &Params, ap: usize) -> usize {
    p.q_dmg + ap * p.q_ap / 100
}

// ===================== 模拟里的小工具 =====================

/// His enemies he can throw at: alive, targetable, not a tower or a nexus.
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<Foe> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos(), u.is_champion()))
        .collect()
}

fn unit(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    (0..).map_while(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

// ===================== 被动：野火冲刺 + 监察 =====================

#[derive(Clone, Default)]
struct Firelight {
    p: Params,
    /// Damage taken this life since the last dash.
    taken: usize,
    /// Watcher's reduction now on (None: not put on yet this life), and whether he was alive last tick.
    watch: Option<usize>,
    was_alive: bool,
}

impl StablePassive for Firelight {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Scar (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _: usize, damage: usize) {
        if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.taken = self.taken.saturating_add(damage);
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        let Some((alive, (hp, max))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if alive && !self.was_alive {   // the first tick of a life: nothing taken yet, Watcher put on again
            self.taken = 0;
            self.watch = None;
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        // Watcher by health
        let w = watch(&self.p, hp, max);
        if self.watch != Some(w) {
            let mut b = BuffV1::named(&sc("w_watch"));
            b.damaged_reduce = w;
            put(sim, me, &b);
            if self.watch.is_some() {
                if let Some(k) = counted("watch") {
                    wlog(format!("{} WATCH #{k}: {hp}/{max}: {w}% damage reduction", head(sim, me)));
                }
            }
            self.watch = Some(w);
        }
        // the dash struck: heal by the damage taken since the last one
        if has(sim, me, &sc("p_surf")) {
            sim.entity_remove_buff(me, &sc("p_surf"));
            let amount = dash_heal(&self.p, self.taken);
            if amount > 0 {
                sim.heal(me, me, amount);
            }
            let on = InputTargetV1::target(me);
            sim.play_view_effect(&sc("p_heal"), me, &on, 0, 0, 0);
            sim.play_sfx(SFX_HEAL, me, &on);
            if let Some(k) = counted("surf") {
                wlog(format!("{} SURF #{k}: took {} since the last dash, heals {amount} ({hp}/{max})", head(sim, me),
                             self.taken));
            }
            self.taken = 0;
        }
    }
}

// ===================== 水坑狙击惊喜 =====================

/// The throw: one bomb at each of the q_n nearest enemies.
struct Bombs;
impl StableEffectType for Bombs {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else { return };
        let p = params_of(me);
        let mut targets = nearest(&foes(sim, me), at, p.q_range as u64, p.q_n);
        if targets.is_empty() {   // the AI's own target (it chose one in range)
            targets.extend(unit(&input));
        }
        let mut thrown = 0;
        for &id in &targets {
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x: at.0,
                y: at.1,
                radius: 0,
                speed: p.q_speed as u64,
                move_kind: ProjectileMoveKindV1::Target.code(),
                target_id: id,
                target_x: 0,
                target_y: 0,
                penetrate: false,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::EnemyWithoutTower.code(),
            };
            if sim.spawn_projectile(&sc("q_bomb"), BOMB_FX, &spec) {
                thrown += 1;
            }
        }
        if let Some(k) = counted("bombs") {
            let who: Vec<String> = targets.iter().map(|&id| name_of(sim, id)).collect();
            wlog(format!("{} BOMBS #{k}: {thrown}/{} thrown at {}", head(sim, me), targets.len(), who.join(", ")));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (0, bomb_damage(&p, caster_stat.magic_power) * p.q_n)
    }

    fn expected_cc_time(&self) -> Option<usize> {
        Some(Params::default().q_stun)
    }
}

/// A bomb hit: magic damage and a stun.
struct Bomb;
impl StableEffectType for Bomb {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        let p = params_of(me);
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let dmg = bomb_damage(&p, ap);
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
            sim.apply_cc(id, &CcV1::stun(p.q_stun as u64));
            put(sim, id, &BuffV1::timed(&sc("q_stun"), p.q_stun));
        }
        let on = InputTargetV1::target(id);
        sim.play_view_effect(&sc("q_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_BOMB_HIT, me, &on);
        if let Some(k) = counted("bomb") {
            wlog(format!("{} BOMB #{k}: {} takes {dmg} magic, stunned {}", head(sim, me), name_of(sim, id), p.q_stun));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        (0, bomb_damage(&Params::default(), caster_stat.magic_power))
    }
}

// ===================== 注册 =====================

/// Scar's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Scar: the Firelight dash's heal, Watcher, the bombs) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:firelight"), Firelight::default());
    module.add_native_effect(format!("{ID}:bombs"), Bombs);
    module.add_native_effect(format!("{ID}:bomb"), Bomb);
    host.log(LogLevel::Info, "tft.dll: Scar (Firelight, Watcher, Puddle Jumper Surprise).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_heal":25,"q_ap":80,"q_dmg":70,"q_n":3,"q_range":45000,"q_speed":2400,"q_stun":60,"w_hi":20,"w_line":50,"w_lo":10}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_nearest_three_champions_first() {
        let at = (100_000, 100_000);
        let foes = [
            (1, (110_000, 100_000), false),   // a minion, nearest
            (2, (130_000, 100_000), true),
            (3, (120_000, 100_000), true),
            (4, (100_000, 125_000), true),
            (5, (200_000, 100_000), true),    // out of reach
        ];
        assert_eq!(nearest(&foes, at, 45_000, 3), vec![3, 4, 2]);
        assert_eq!(nearest(&foes, at, 45_000, 5), vec![3, 4, 2, 1]);
        assert!(nearest(&foes, at, 5_000, 3).is_empty());
    }

    #[test]
    fn watcher_by_health() {
        let p = Params::default();
        assert_eq!(watch(&p, 500, 1000), 20);
        assert_eq!(watch(&p, 499, 1000), 10);
        assert_eq!(watch(&p, 0, 0), 10);
    }

    #[test]
    fn heal_and_damage() {
        let p = Params::default();
        assert_eq!(dash_heal(&p, 400), 100);
        assert_eq!(bomb_damage(&p, 50), 110);
    }
}
