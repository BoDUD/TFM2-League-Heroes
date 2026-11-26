//! 吕布奉先（`ragnarok_lubu`）数据做不到的部分。数据（tools/kit/build_lubu.py）的 `passive` 是这里的
//! `ragnarok_lubu:breaker`，参数从数据的 `passive.params` 来（build_lubu.py 的参数表 P，`NATIVE_KEYS`）。
//!
//! 被动「盾牌破坏者」：
//! - 无视护甲：每条命一开始就挂上 `ragnarok_lubu_p_pen`（护甲穿透 `p_pen`%，永久）。
//! - 打盾加倍：他打到带护盾的敌人时，这一下对护盾多算 `p_shield`%。只加到刚好打掉护盾为止，不会越过护盾多打血
//!   （护盾 s、这一下 d、比例 k：加 min(d*k, s*k/(1+k))，打碎时血掉 d - s/(1+k)，没碎时护盾少 d*(1+k)）。
//! - 真的打碎才算：这一下之后的下一拍再读目标的护盾，确实没了才播碎盾的画面和声音，再补 `p_break`% 攻击力的物理伤害。
//!   这一拍别人给他新挂了盾、或者盾本来就要到时间，都按读回来的为准。
//!
//! 配音（关智一的原声，Codex 截的十句）：第一次和敌方英雄交手、杀了英雄、复活、放破阵时偶尔说一句，每句有自己的冷却，
//! 两句之间至少隔一会儿，不会每下普攻都喊。天喰蓄力的那句「全身全霊」是数据自己放的。
//!
//! 经典 SDK 跑不了这里的代码，平衡模拟用 build_lubu.py --plain（护甲穿透改成第一个技能挂上，没有护盾那部分）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\ragnarok_lubu.log`，每次启动重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "ragnarok_lubu";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("ragnarok_lubu_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("RAGNAROK_LUBU_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("ragnarok_lubu.log");
        }
    }
    PathBuf::from("ragnarok_lubu.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // 文件一直开着，每行都重新打开会卡住模拟线程
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 护甲穿透，百分比
    pub p_pen: usize,
    /// 对护盾多算的百分比
    pub p_shield: usize,
    /// 打碎护盾时补的物理伤害，攻击力的百分比
    pub p_break: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_pen: 15,
            p_shield: 100,
            p_break: 30,
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
            "p_pen" => p.p_pen = u.min(100),
            "p_shield" => p.p_shield = u.min(1000),
            "p_break" => p.p_break = u.min(1000),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// 这一下对护盾要多加多少：多算 pct%，但最多加到刚好打碎护盾，碎了以后的部分照常打血。
pub fn shield_bonus(damage: usize, shield: usize, pct: usize) -> usize {
    if shield == 0 || damage == 0 || pct == 0 {
        return 0;
    }
    let by_hit = damage * pct / 100;
    let to_break = shield * pct / (100 + pct);
    by_hit.min(to_break)
}

/// 护甲穿透的 buff，每条命挂一次，永久。
pub fn pen_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::named(&vo("p_pen"));
    b.defence_penetration = p.p_pen;
    b
}

/// 配音：事件、几句里挑哪句、这句自己的冷却（拍）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 杀了敌方英雄
    Kill,
    /// 复活回来
    Respawn,
    /// 放破阵冲进去
    Charge,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        Cue::Start => &["v_start"],
        Cue::Kill => &["v_praise", "v_taunt_strong", "v_taunt_gods"],
        Cue::Respawn => &["v_select"],
        Cue::Charge => &["v_challenge", "v_encounter", "v_swing_call", "v_power"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Kill => 20 * SECOND,
        Cue::Respawn => 60 * SECOND,
        Cue::Charge => 25 * SECOND,
    }
}

/// 破阵时说不说：冷却到了也只有三成的时候开口。
pub const CHARGE_CHANCE: u64 = 30;

/// 一份模拟里的配音节奏：上一句的拍数、每种事件上次的拍数、每种事件轮到第几句。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    turn: HashMap<&'static str, usize>,
    started: bool,
}

impl Voice {
    fn key(cue: Cue) -> &'static str {
        match cue {
            Cue::Start => "start",
            Cue::Kill => "kill",
            Cue::Respawn => "respawn",
            Cue::Charge => "charge",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        if cue == Cue::Start && self.started {
            return None;
        }
        if self.last_any.is_some_and(|t| tick < t + VOICE_GAP) {
            return None;
        }
        let k = Self::key(cue);
        if self.last.get(k).is_some_and(|&t| tick < t.saturating_add(cue_cooldown(cue))) {
            return None;
        }
        let lines = lines_of(cue);
        let turn = self.turn.entry(k).or_insert(0);
        let line = lines[*turn % lines.len()];
        *turn += 1;
        self.last.insert(k, tick);
        self.last_any = Some(tick);
        if cue == Cue::Start {
            self.started = true;
        }
        Some(line)
    }
}

// ===================== 游戏里 =====================

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 等着下一拍核对的一下：打的是谁、打之前的护盾、哪一拍打的。
#[derive(Clone, Copy, Debug)]
struct Hit {
    target: usize,
    shield: usize,
    tick: usize,
}

#[derive(Clone, Default)]
struct Breaker {
    p: Params,
    me: usize,
    was_alive: bool,
    lives: usize,
    hits: Vec<Hit>,
    voice: Voice,
    /// 破阵的冷却上一拍是多少，用来认出这一拍刚放了破阵
    e_cd: usize,
    /// 自己补伤害时不再算一遍
    busy: bool,
}

impl Breaker {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        if let Some(k) = counted("voice") {
            wlog(format!("{} VOICE #{k}: {cue:?} -> {line}", head(sim, me)));
        }
    }

    /// 下一拍核对：护盾真的没了才算打碎。
    fn settle(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let (due, wait): (Vec<Hit>, Vec<Hit>) = self.hits.drain(..).partition(|h| h.tick < now);
        self.hits = wait;
        let mut seen: Vec<usize> = Vec::new();
        for h in due {
            if seen.contains(&h.target) {
                continue;
            }
            seen.push(h.target);
            let Some(t) = sim.get_entity(h.target) else { continue };
            let (alive, left) = (t.is_alive(), t.shield());
            if left > 0 {
                if let Some(k) = counted("held") {
                    wlog(format!("{} HELD #{k}: #{} shield {} -> {left}, not broken", head(sim, me), h.target, h.shield));
                }
                continue;
            }
            let on = InputTargetV1::target(h.target);
            sim.play_view_effect(&vo("p_break"), me, &on, 0, 0, 0);
            sim.play_sfx(&vo("p_break"), me, &on);
            let attack = sim.get_entity(me).map_or(0, |e| e.stat().attack);
            let extra = attack * self.p.p_break / 100;
            if alive && extra > 0 {
                self.busy = true;
                sim.deal_damage(me, h.target, extra, 0, AttackTypeV1::Skill);
                self.busy = false;
            }
            if let Some(k) = counted("break") {
                wlog(format!("{} BREAK #{k}: #{} shield {} -> 0, +{extra} physical{}", head(sim, me), h.target,
                             h.shield, if alive { "" } else { " (target already dead, none)" }));
            }
        }
    }
}

impl StablePassive for Breaker {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：这里先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: ragnarok.dll's Lu Bu (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if alive && !self.was_alive {
            self.lives += 1;
            if !sim.get_entity(me).is_some_and(|e| has_buff(&e, &vo("p_pen"))) {
                sim.add_buff(me, &pen_buff(&self.p));
            }
            if self.lives > 1 {
                self.say(sim, Cue::Respawn);
            }
        }
        self.was_alive = alive;
        if !alive {
            self.hits.clear();
            return;
        }
        self.settle(sim, me);
        // 破阵的冷却从 0 跳上去就是刚放了
        let e_cd = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.2);
        if e_cd > self.e_cd + 30 && (rng % 100) < CHARGE_CHANCE {
            self.say(sim, Cue::Charge);
        }
        self.e_cd = e_cd;
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if self.busy {
            return;
        }
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some((team, champion, shield)) = sim.get_entity(target).map(|t| (t.team(), t.is_champion(), t.shield()))
        else {
            return;
        };
        if team == my_team {
            return;
        }
        if champion {
            self.say(sim, Cue::Start);
        }
        if shield == 0 {
            return;
        }
        let before = *damage;
        let add = shield_bonus(before, shield, self.p.p_shield);
        *damage = before + add;
        let tick = sim.tick();
        self.hits.push(Hit { target, shield, tick });
        if let Some(k) = counted("shield") {
            wlog(format!("{} SHIELD #{k}: #{target} shield {shield}, hit {before} +{add} = {}", head(sim, me), *damage));
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.me = me;
        let champion = sim.get_entity(victim).is_some_and(|v| v.is_champion());
        if champion {
            self.say(sim, Cue::Kill);
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.hits.clear();
        self.was_alive = false;
    }
}

// ===================== 注册 =====================

/// 吕布的被动，注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Lu Bu: Shield Breaker - armour, shields counted double, real breaks; voice lines) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:breaker"), Breaker::default());
    host.log(LogLevel::Info, "ragnarok.dll: Lu Bu (Shield Breaker).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_break":30,"p_pen":15,"p_shield":100}"#;
        assert_eq!(parse_params(json), Params::default());
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"p_pen":250}"#).p_pen, 100);
    }

    /// 护盾 s、这一下 d、多算一倍：碎了的话血掉 d - s/2，没碎的话护盾少 2d，两边都不会多打。
    #[test]
    fn shields_take_double_and_never_more() {
        // 盾 100，打 80：只需要加 50 就碎（80+50-100=30 = 80-100/2）
        assert_eq!(shield_bonus(80, 100, 100), 50);
        // 盾 300，打 80：碎不了，这一下对盾算 160
        assert_eq!(shield_bonus(80, 300, 100), 80);
        // 盾正好 2d
        assert_eq!(shield_bonus(80, 160, 100), 80);
        // 没盾、没伤害、比例 0 都不加
        assert_eq!(shield_bonus(80, 0, 100), 0);
        assert_eq!(shield_bonus(0, 100, 100), 0);
        assert_eq!(shield_bonus(80, 100, 0), 0);
        // 多算一半：盾 90，打 100 -> 加到 30 就碎（血掉 100+30-90 = 40 = 100 - 90/1.5）
        assert_eq!(shield_bonus(100, 90, 50), 30);
    }

    #[test]
    fn health_after_the_hit_is_what_double_damage_gives() {
        for &(d, s) in &[(80usize, 100usize), (80, 300), (10, 15), (200, 50), (1, 1)] {
            let total = d + shield_bonus(d, s, 100);
            let to_hp = total.saturating_sub(s);
            let want = if 2 * d >= s { d - s / 2 } else { 0 };
            assert!(to_hp.abs_diff(want) <= 1, "d {d} s {s}: {to_hp} vs {want}");
        }
    }

    #[test]
    fn the_armour_buff() {
        let b = pen_buff(&Params::default());
        assert_eq!(b.name(), "ragnarok_lubu_p_pen");
        assert_eq!(b.defence_penetration, 15);
        assert_eq!(b.duration_kind, BuffDurationV1::Permanent.code());
    }

    #[test]
    fn the_start_line_once_a_match() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 100), Some("v_start"));
        assert_eq!(v.pick(Cue::Start, 100 + 600 * SECOND), None);
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_praise"));
        // 刚说完，别的也不说
        assert_eq!(v.pick(Cue::Charge, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Charge, 1000 + VOICE_GAP), Some("v_challenge"));
        // 杀人那几句自己的冷却
        assert_eq!(v.pick(Cue::Kill, 1000 + 20 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 20 * SECOND), Some("v_taunt_strong"));
        assert_eq!(v.pick(Cue::Kill, 1000 + 40 * SECOND), Some("v_taunt_gods"));
        assert_eq!(v.pick(Cue::Kill, 1000 + 60 * SECOND), Some("v_praise"));
    }

    #[test]
    fn every_line_is_one_of_codexs_ten() {
        let ten = ["select", "start", "taunt_strong", "taunt_gods", "challenge", "swing_call", "praise", "encounter",
                   "ult", "power"];
        for cue in [Cue::Start, Cue::Kill, Cue::Respawn, Cue::Charge] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(ten.contains(&clip), "{line}");
            }
        }
    }
}
