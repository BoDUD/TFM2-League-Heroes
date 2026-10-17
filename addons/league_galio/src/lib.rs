//! 加里奥附加包（用户选「主包数据 + 附加包」）：主包数据做不到的三件事。
//!
//! `mod.override_info` 把主包的加里奥换成 `override/` 里的副本（tools/kit/build_galio.py 的 native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_galio:colossus`（参数在英雄数据的 `passive.params` 里）；
//! - 普攻不再顺带给杜朗护盾的被动护盾（本包按「多久没挨打」给）；
//! - W 放开时不再用数据的固定嘲讽，而是调本包的 `league_galio:taunt`；
//! - R 每次轮询时问每一个友方英雄，调本包的 `league_galio:entrance`，被选中的那个才会被保护、被飞过去。
//!
//! - **杜朗护盾（被动）**：`PS_IDLE` tick 没受到伤害，就获得 `ps` + `ps_ap`% 法强的护盾（`ps_t` tick），护盾还在就不重给。
//!   英雄联盟里这个护盾只挡魔法伤害；被动的受伤钩子（`on_damaged`）不带伤害类型，所以这里挡所有伤害（README 写明）。
//! - **嘲讽按人数**：W 放开时，`w_r` 以内的敌方英雄越多，嘲讽越久（英雄联盟里蓄力越久嘲讽越久，人多时玩家会蓄满）：
//!   1 个 `TAUNT_ONE`、2 个 `w_taunt`（主包的数）、3 个及以上 `TAUNT_MANY` tick；小兵野怪同样时长。
//! - **英雄登场选人**：在离加里奥至少 `r_far`、身边 `r_sur` 以内有敌方英雄的友方英雄里，选「被控着，或者血量比例最低」的那个，
//!   身边 `r_r` 以内敌方英雄多的优先（每多一个当作血量少 10%）；只有一个敌人、没被控、血量 80% 以上的不算苦战，不飞。
//!   选中的友方英雄让加里奥身上出现 1 tick 的 `league_galio_r_this`，数据接着走护盾、引导、飞过去。
//!
//! 数字：`PS_IDLE`、`TAUNT_*` 写在这里，`tests::the_numbers_match_the_kit` 读主包的参数表核对；其余从英雄数据来。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_galio.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_galio";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.1";

// ===================== 数值（主包 build_galio.P） =====================

/// 多久没挨打给被动护盾（w_ps_cd，英雄联盟 12 秒）。
pub const PS_IDLE: usize = 720;
/// 嘲讽：身边 1 个敌方英雄、3 个及以上（2 个用主包的 w_taunt）。
pub const TAUNT_ONE: usize = 45;
pub const TAUNT_MANY: usize = 90;
/// 不算苦战：没被控、血量比例在这以上、身边只有一个敌方英雄。
pub const CALM_HP: f64 = 0.8;

fn gl(x: &str) -> String {
    format!("league_galio_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_GALIO_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_galio.log");
        }
    }
    PathBuf::from("league_galio.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
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

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 嘲讽时长：`w_r` 以内的敌方英雄数 `n`。
pub fn taunt_ticks(n: usize, mid: usize) -> usize {
    match n {
        0 | 1 => TAUNT_ONE,
        2 => mid,
        _ => TAUNT_MANY,
    }
}

/// 一个友方英雄的情况。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Ally {
    pub id: usize,
    /// 离加里奥多远。
    pub far: f64,
    /// 血量比例 0..1。
    pub hp: f64,
    pub in_cc: bool,
    /// `r_sur` 以内、`r_r` 以内的敌方英雄数。
    pub near: usize,
    pub close: usize,
}

/// 该飞去谁身边：够远、身边有敌方英雄、确实在苦战的里面，被控的优先，再按「血量比例 - 0.1 x 落点敌方英雄数」最小。
pub fn choose(allies: &[Ally], r_far: f64) -> Option<usize> {
    let key = |a: &Ally| (if a.in_cc { 0 } else { 1 }, a.hp - 0.1 * a.close as f64);
    allies
        .iter()
        .filter(|a| a.far >= r_far && a.near >= 1)
        .filter(|a| a.in_cc || a.hp < CALM_HP || a.near >= 2)
        .min_by(|a, b| {
            let (ka, kb) = (key(a), key(b));
            ka.0.cmp(&kb.0).then(ka.1.partial_cmp(&kb.1).unwrap_or(std::cmp::Ordering::Equal))
        })
        .map(|a| a.id)
}

// ===================== 小工具 =====================

/// 硬控（击飞、晕眩、定身、嘲讽、恐惧、魅惑、被强制位移）：英雄登场优先飞去「被控住」的队友身边。
/// 不是 `cc_count() > 0`：游戏 0.6.4 把正在播的施法动作也记成一种控制（`CcKindV1::Animation`），哪个队友在放技能都算
/// 「被控」、都被当成苦战（卡莉丝塔附加包 10-16 查出：她每一跳都被自己的动作叫停）。
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

/// One CC entry's kind is hard CC (not a cast animation, silence or disarm).
pub fn is_hard_cc(kind: u32) -> bool {
    HARD_CC.iter().any(|k| k.code() == kind)
}

fn hard_cc(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| is_hard_cc(c.kind)))
}

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

/// 某一队活着、能被选中的英雄：(id, 位置)。
fn champions(sim: &StableSim<'_>, team: usize, same: bool) -> Vec<(usize, (f64, f64))> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if (u.team() == team) != same || !u.is_alive() || !u.is_targetable() || !u.is_champion() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((u.id(), (x as f64, y as f64)));
    }
    out
}

// ===================== 参数（英雄数据的 passive.params） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 被动护盾 ps + ps_ap% 法强，持续 ps_t。
    pub ps: usize,
    pub ps_ap: usize,
    pub ps_t: usize,
    /// W 的半径和 2 个英雄时的嘲讽。
    pub w_r: usize,
    pub w_taunt: usize,
    /// R：至少多远的友军、友军身边多远算有敌人、落地半径。
    pub r_far: usize,
    pub r_sur: usize,
    pub r_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { ps: 90, ps_ap: 30, ps_t: 300, w_r: 26_000, w_taunt: 70, r_far: 60_000, r_sur: 25_000, r_r: 22_000 }
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
            "ps" => p.ps = v,
            "ps_ap" => p.ps_ap = v,
            "ps_t" => p.ps_t = v,
            "w_r" => p.w_r = v,
            "w_taunt" => p.w_taunt = v,
            "r_far" => p.r_far = v,
            "r_sur" => p.r_sur = v,
            "r_r" => p.r_r = v,
            _ => {}
        }
    }
    p
}

/// 每个加里奥的参数（native effect 按施法者找）。
static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== W 的嘲讽 =====================

struct Taunt;

impl StableEffectType for Taunt {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        let p = params_of(caster);
        let (Some(at), Some(team)) = (alive_at(sim, caster), sim.get_entity(caster).map(|e| e.team())) else { return };
        let n = champions(sim, team, false).iter().filter(|c| dist(at, c.1) <= p.w_r as f64).count();
        let ticks = taunt_ticks(n, p.w_taunt);
        let mut cc = CcV1::of_kind(CcKindV1::Taunt, ticks as u64);
        cc.target = caster;
        sim.apply_cc(target, &cc);
        sim.add_buff(target, &BuffV1::timed(&gl("w_taunt"), ticks));
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            if let Some(k) = counted("taunt") {
                wlog(format!("{} TAUNT #{k} {}: {ticks} ticks ({n} enemy champions near)", head(sim, caster),
                             who(sim, target)));
            }
        }
    }
}

// ===================== R 选人 =====================

/// 这一 tick 选好的友军（每份模拟的每个加里奥一份：同一 tick 每个友军都会来问一次，只算一遍）。键是 (这份模拟的编号,
/// 加里奥)：之前只按加里奥的实体编号记，几份模拟同时跑（游戏 0.6.4 同一局有两份预模拟）、编号和 tick 又一样时，一份会拿到
/// 另一份选的人，两份模拟就不一样了（莫德凯撒附加包的同类问题让第 592 场的预模拟和画面分了岔）。
static PICKS: LazyLock<Mutex<HashMap<(u64, usize), (usize, Option<usize>)>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

/// 每份模拟的加里奥一个编号，出生时由被动挂在他身上（buff `league_galio_sim:<编号>`，没有数值、没有画面）。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
const SIM_TAG: &str = "league_galio_sim:";

/// The number the passive hung on him when he spawned in this sim (0: none).
pub fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    names.into_iter().find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn sim_of(sim: &StableSim<'_>, me: usize) -> u64 {
    sim.get_entity(me).map_or(0, |e| sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i))
        .map(|b| b.name().to_string())))
}

fn pick_for(sim: &StableSim<'_>, me: usize) -> Option<usize> {
    let tick = sim.tick();
    let key = (sim_of(sim, me), me);
    if let Some(&(t, id)) = PICKS.lock().unwrap_or_else(|e| e.into_inner()).get(&key) {
        if t == tick {
            return id;
        }
    }
    let p = params_of(me);
    let at = alive_at(sim, me)?;
    let team = sim.get_entity(me)?.team();
    let foes = champions(sim, team, false);
    let mut allies = Vec::new();
    for (id, pos) in champions(sim, team, true) {
        if id == me {
            continue;
        }
        let Some(e) = sim.get_entity(id) else { continue };
        let (hp, max) = e.hp();
        allies.push(Ally {
            id,
            far: dist(at, pos),
            hp: if max > 0 { hp as f64 / max as f64 } else { 1.0 },
            in_cc: hard_cc(&e),
            near: foes.iter().filter(|f| dist(pos, f.1) <= p.r_sur as f64).count(),
            close: foes.iter().filter(|f| dist(pos, f.1) <= p.r_r as f64).count(),
        });
    }
    let id = choose(&allies, p.r_far as f64);
    let mut picks = PICKS.lock().unwrap_or_else(|e| e.into_inner());
    if picks.len() > 4096 {
        picks.clear(); // finished sims
    }
    picks.insert(key, (tick, id));
    drop(picks);
    if let Some(id) = id {
        if let Some(a) = allies.iter().find(|a| a.id == id) {
            if let Some(k) = counted("entrance") {
                wlog(format!("{} ENTRANCE #{k} -> {}: hp {:.0}%{}, {} enemy champions near, {} where he lands, {:.0} away",
                             head(sim, me), who(sim, id), a.hp * 100.0, if a.in_cc { " in cc" } else { "" }, a.near,
                             a.close, a.far));
            }
        }
    }
    id
}

struct Entrance;

impl StableEffectType for Entrance {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        if pick_for(sim, caster) == Some(input.target_id) {
            sim.add_buff(caster, &BuffV1::timed(&gl("r_this"), 1));
        }
    }
}

// ===================== 被动：杜朗护盾 =====================

/// 每个加里奥一份。
#[derive(Clone, Default)]
struct Colossus {
    p: Params,
    me: usize,
    /// 上次受伤的 tick、护盾到期的 tick。
    hurt: usize,
    until: usize,
    given: usize,
    /// This sim's number (`SIM_TAG`), drawn at his first spawn.
    sim_no: u64,
}

impl StablePassive for Colossus {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.hurt = sim.tick();
        self.until = 0;
        if self.sim_no == 0 {
            self.sim_no = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim_no);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Galio (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if alive_at(sim, me).is_none() {
            return;
        }
        let now = sim.tick();
        if now < self.until || now < self.hurt + PS_IDLE {
            return;
        }
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let amount = self.p.ps + self.p.ps_ap * ap / 100;
        if sim.entity_add_shield(me, amount, self.p.ps_t) {
            self.until = now + self.p.ps_t;
            self.given += 1;
            sim.play_view_effect(&gl("w_ps"), me, &InputTargetV1::target(me), 0, 0, 0);
            if let Some(k) = counted("ward") {
                wlog(format!("{} WARD #{k}: {amount} shield after {} ticks untouched", head(sim, me), now - self.hurt));
            }
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, _: usize, _: usize, damage: usize) {
        if damage > 0 {
            self.hurt = sim.tick();
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.hurt = sim.tick();
        self.until = 0;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Galio: Shield of Durand after {PS_IDLE} ticks untouched, taunt by the champions near, Hero's Entrance by health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:colossus"), Colossus::default());
    module.add_native_effect(format!("{ID}:taunt"), Taunt);
    module.add_native_effect(format!("{ID}:entrance"), Entrance);
    host.log(LogLevel::Info, "league_galio loaded (Shield of Durand untouched, taunt by champions near, Hero's Entrance by health).");
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
    fn a_cast_animation_is_not_hard_cc() {
        assert!(!is_hard_cc(CcKindV1::Animation.code()));
        assert!(!is_hard_cc(CcKindV1::BlockSkill.code()));
        for k in [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm,
                  CcKindV1::ForceMove] {
            assert!(is_hard_cc(k.code()));
        }
    }

    fn ally(id: usize, far: f64, hp: f64, in_cc: bool, near: usize, close: usize) -> Ally {
        Ally { id, far, hp, in_cc, near, close }
    }

    #[test]
    fn taunt_by_champions_near() {
        assert_eq!(taunt_ticks(0, 70), TAUNT_ONE);
        assert_eq!(taunt_ticks(1, 70), TAUNT_ONE);
        assert_eq!(taunt_ticks(2, 70), 70);
        assert_eq!(taunt_ticks(5, 70), TAUNT_MANY);
    }

    #[test]
    fn the_ally_to_land_on() {
        // too near, no enemy, calm (full health, one enemy): nobody
        assert_eq!(choose(&[ally(1, 30_000.0, 0.2, false, 2, 2)], 60_000.0), None);
        assert_eq!(choose(&[ally(1, 90_000.0, 0.2, false, 0, 0)], 60_000.0), None);
        assert_eq!(choose(&[ally(1, 90_000.0, 0.95, false, 1, 1)], 60_000.0), None);
        // crowd control first, then the lowest health share, enemies where he lands counting as 10% each
        let a = [ally(1, 90_000.0, 0.3, false, 1, 1), ally(2, 90_000.0, 0.7, true, 1, 0), ally(3, 90_000.0, 0.5, false, 3, 3)];
        assert_eq!(choose(&a, 60_000.0), Some(2));
        assert_eq!(choose(&a[..1], 60_000.0), Some(1));
        assert_eq!(choose(&[a[0], a[2]], 60_000.0), Some(3));
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"ps":90,"ps_ap":30,"ps_t":300,"r_far":60000,"r_r":22000,"r_sur":25000,"w_r":26000,"w_taunt":70}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_galio.py");
        let src = std::fs::read_to_string(path).expect("build_galio.py");
        assert!(src.contains(&format!("\"w_ps_cd\": {PS_IDLE}")), "w_ps_cd is not {PS_IDLE} in build_galio.P");
        let d = Params::default();
        for (key, v) in [("w_ps", d.ps), ("w_ps_ap", d.ps_ap), ("w_ps_t", d.ps_t), ("w_r", d.w_r), ("w_taunt", d.w_taunt),
                         ("r_far", d.r_far), ("r_sur", d.r_sur), ("r_r", d.r_r)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_galio.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["w_taunt", "r_this", "w_ps"] {
            assert!(gl(x).len() <= BUFF_NAME_CAP);
        }
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn each_sim_finds_its_own_number() {
        let names = |v: &[&str]| v.iter().map(|s| s.to_string()).collect::<Vec<_>>().into_iter();
        assert_eq!(sim_tag(names(&["league_galio_w_ps", "league_galio_sim:7"])), 7);
        assert_eq!(sim_tag(names(&["league_galio_r_this"])), 0);
    }
}
