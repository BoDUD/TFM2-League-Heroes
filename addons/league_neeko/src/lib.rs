//! 妮蔻附加包（用户 2026-10-21 选「做，附加包」）：被动「天生幻魅」照英雄联盟做——**她整个身体画成一名友方英雄**，放伤害
//! 技能、被控制、或者挨了一大口伤害就现出原形，过一阵再变。
//!
//! 主包是纯数据：数据换不了外形，主包的妮蔻没有被动。`mod.override_info` 把主包的妮蔻换成 `override/` 里的副本
//! （tools/kit/build_neeko.py 的 native=1：数据和主包一样，只多了被动 `league_neeko:glamour` 和现形 / 变身的画面
//! `league_neeko_p_poof`）。被动每 tick：
//!
//! - **变身**：没在假扮、离上次现形 `p_cd` tick 以上、`p_calm` tick 没挨打、没被控 → 变成附近最近的、活着的友方英雄
//!   （只挑 src/souls.rs 里有动作表的英雄：别的 mod 的英雄名字对不上图会让游戏 panic），开局 `p_first` tick 后第一次变；
//! - **现形**：她放了技能（Q / E / R 冷却从 0 跳上去：三个都是伤害技能）——英雄联盟的现形加穿透：`league_neeko_p_pen`
//!   `p_pen_t` tick 法术穿透 `p_pen`%；被控（击飞、晕眩、禁锢、嘲讽、恐惧、魅惑、强制位移）；假扮以来挨的伤害到她最大生命的
//!   `p_hp`%（英雄联盟：打掉伪装的那条血）；她假扮的那名队友阵亡；她自己阵亡。
//!
//! 外形（[`view`]，佛耶戈附身 0.1.7 的做法）：屏幕放的那场模拟几秒钟就把整局跑完，屏幕几分钟后才放到，所以被动在屏幕放的
//! 那场模拟里把每次变身 / 现形的 tick 和队友的英雄 id 记下来，显示钩子按屏幕上的比赛时钟（game_places::clock，由
//! league_addons 里佛耶戈的读时钟扩展喂）把她的身体资源名换成那名队友的、动作名换成他图里有的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_neeko.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_viego_soul/src/souls.rs"]
#[allow(dead_code)]
mod souls;
pub mod view;

const ID: &str = "league_neeko";
pub const HERO: &str = "league_neeko";

fn nk(x: &str) -> String {
    format!("{HERO}_{x}")
}

/// 现形后的法术穿透（数据里没有，原生加）。
pub const PEN: &str = "league_neeko_p_pen";
/// 技能冷却从 0 跳到这么多以上算放了一次（league_yuumi 的做法）。
const CAST_JUMP: usize = 30;
/// 这些控制打破假扮。
const BREAK: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::ForceMove];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NEEKO_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_neeko.log");
        }
    }
    PathBuf::from("league_neeko.log")
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
    let t = sim.tick();
    format!("[{kind} m={} s={}] t={t} ({}:{:02}) #{id}", m(o.match_id), m(o.set_index), t / 3600, t / 60 % 60)
}

/// The sims the screen replays (the client's match view, spectating, a replay): the screen draws their disguises.
fn on_screen(sim: &StableSim<'_>) -> Option<(u64, u64)> {
    let o = sim.sim_origin().unwrap_or_default();
    matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay))
        .then_some((o.match_id, o.set_index))
}

// ===================== 参数 =====================

/// 被动的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 开局多久第一次变
    pub p_first: usize,
    /// 现形后多久才能再变（英雄联盟 PassiveCooldown 6 s）
    pub p_cd: usize,
    /// 这么久没挨打才变（英雄联盟 ChargeTime 2 s）
    pub p_calm: usize,
    /// 假扮以来挨的伤害到最大生命的这么多 % 就现形
    pub p_hp: usize,
    /// 放技能现形后的法术穿透 %、多久（英雄联盟 MagicPen 20%、4 s）
    pub p_pen: usize,
    pub p_pen_t: usize,
    /// 只变这么远以内的队友
    pub p_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_first: 120, p_cd: 360, p_calm: 120, p_hp: 35, p_pen: 20, p_pen_t: 240, p_r: 200_000 }
    }
}

/// `{"p_cd":360,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "p_first" => &mut p.p_first,
            "p_cd" => &mut p.p_cd,
            "p_calm" => &mut p.p_calm,
            "p_hp" => &mut p.p_hp,
            "p_pen" => &mut p.p_pen,
            "p_pen_t" => &mut p.p_pen_t,
            "p_r" => &mut p.p_r,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 算式 =====================

/// 她能变成的英雄：有动作表（src/souls.rs）、不是妮蔻。
pub fn can_wear(name: &str) -> bool {
    name != HERO && souls::SOULS.binary_search_by(|s| s.0.cmp(name)).is_ok()
}

/// 冷却从 0 跳上去 = 放了一次。
pub fn cast_seen(was: usize, now: usize) -> bool {
    was == 0 && now > CAST_JUMP
}

/// 假扮以来挨的伤害够不够打破伪装。
pub fn hit_through(taken: usize, max_hp: usize, p_hp: usize) -> bool {
    max_hp > 0 && taken * 100 >= max_hp * p_hp
}

// ===================== 被动 =====================

#[derive(Clone, Debug)]
struct Disguise {
    ally: usize,
    name: String,
    taken: usize,
}

#[derive(Clone, Default)]
pub struct Glamour {
    p: Params,
    on: Option<Disguise>,
    ready: usize,
    hurt: usize,
    cds: [usize; 3],
    started: bool,
    count: usize,
    /// Her unit, set by every update (`on_dead` is given only the player; a respawn is a new unit).
    me: Option<usize>,
}

const SLOTS: [SkillSlotV1; 3] = [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult];

impl Glamour {
    fn poof(sim: &mut StableSim<'_>, me: usize, sound: &str) {
        let at_me = InputTargetV1::target(me);
        sim.play_view_effect(&nk("p_poof"), me, &at_me, 0, 0, 0);
        sim.play_sfx(&nk(sound), me, &at_me);
    }

    fn end(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str, pen: bool) {
        let Some(on) = self.on.take() else { return };
        let t = sim.tick();
        self.ready = t + self.p.p_cd;
        if why != "dead" {
            Self::poof(sim, me, "p_off");
        }
        if pen {
            let mut b = BuffV1::timed(PEN, self.p.p_pen_t);
            b.magic_resistance_penetration = self.p.p_pen;
            sim.entity_remove_buff(me, PEN);
            sim.add_buff(me, &b);
        }
        if self.count <= 200 {
            wlog(format!("{} REVEAL from {} ({why}{}; {} damage taken in disguise)", head(sim, me), on.name,
                         if pen { ", magic pen" } else { "" }, on.taken));
        }
        if let Some((m, s)) = on_screen(sim) {
            view::note_off(m, s, me, t);
        }
    }

    fn start(&mut self, sim: &mut StableSim<'_>, me: usize, ally: usize, name: String) {
        let t = sim.tick();
        Self::poof(sim, me, "p_on");
        self.count += 1;
        if self.count <= 200 {
            wlog(format!("{} DISGUISE {} as {name} (#{ally})", head(sim, me), self.count));
        }
        if let Some((m, s)) = on_screen(sim) {
            view::note_on(m, s, me, t, &name);
        }
        self.on = Some(Disguise { ally, name, taken: 0 });
    }

    /// The nearest living allied champion she can wear.
    fn pick(&self, sim: &StableSim<'_>, me: usize, team: usize) -> Option<(usize, String)> {
        let r = self.p.p_r as u64;
        (0..sim.champion_count())
            .filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
            .filter(|u| u.id() != me && u.team() == team && u.is_alive())
            .filter_map(|u| u.name().filter(|n| can_wear(n)).map(|n| (u.id(), n)))
            .filter(|(id, _)| sim.distance_sq(me, *id) <= r.saturating_mul(r))
            .min_by_key(|(id, _)| sim.distance_sq(me, *id))
    }
}

impl StablePassive for Glamour {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.ready = sim.tick() + self.p.p_first;
        self.me = Some(me);
        self.on = None; // a new life starts undisguised
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Neeko (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, _me: usize, _attacker: usize, damage: usize) {
        self.hurt = sim.tick();
        if let Some(on) = self.on.as_mut() {
            on.taken += damage;
        }
    }

    /// Her death ends a disguise at once (0.1.1, the 2026-11-01 logs: a dead Neeko's update does not run, so the disguise
    /// outlived her and "revealed" on the respawned Neeko - a poof at the fountain, or 20 % magic pen for a disguise the screen
    /// never drew).
    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        if let Some(me) = self.me {
            self.end(sim, me, "dead", false);
        }
        self.ready = self.ready.max(sim.tick() + self.p.p_first);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        self.me = Some(me);
        let t = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        if !self.started {
            self.started = true;
            if let Some((m, s)) = on_screen(sim) {
                view::note_view(m, s);
                wlog(format!("{} the passive is on; this sim is the one the screen replays", head(sim, me)));
            }
        }
        if !e.is_alive() {
            self.end(sim, me, "dead", false);
            self.ready = self.ready.max(t + self.p.p_first);
            return;
        }
        let team = e.team();
        let max_hp = e.hp().1;
        let held = (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| BREAK.iter().any(|k| k.code() == c.kind)));
        let mut cast = false;
        for (k, slot) in SLOTS.iter().enumerate() {
            let now = e.cooldown(*slot).map_or(0, |c| c.remaining);
            cast |= cast_seen(self.cds[k], now);
            self.cds[k] = now;
        }
        if let Some(on) = &self.on {
            let ally_up = sim.get_entity(on.ally).is_some_and(|a| a.is_alive());
            if cast {
                self.end(sim, me, "cast", true);
            } else if held {
                self.end(sim, me, "crowd control", false);
            } else if hit_through(on.taken, max_hp, self.p.p_hp) {
                self.end(sim, me, "hit through", false);
            } else if !ally_up {
                self.end(sim, me, "the ally fell", false);
            }
            return;
        }
        if t < self.ready || t < self.hurt + self.p.p_calm || held {
            return;
        }
        if let Some((ally, name)) = self.pick(sim, me, team) {
            self.start(sim, me, ally, name);
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
        "=== {ID} v{} (Neeko: Inherent Glamour, drawn as an ally) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:glamour"), Glamour::default());
    // its own DLL reads the screen clock itself; in league_addons Viego's reader feeds the shared clock
    #[cfg(not(league_bundle))]
    module.set_extension(view::ClockFeed);
    view::install_once();
    host.log(LogLevel::Info, "league_neeko loaded (Neeko's disguise as an ally).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_read_and_default() {
        let p = parse_params(r#"{"p_cd":300,"p_hp":40,"zzz":1}"#);
        assert_eq!(p.p_cd, 300);
        assert_eq!(p.p_hp, 40);
        assert_eq!(p.p_pen, Params::default().p_pen);
    }

    #[test]
    fn casts_are_cooldown_jumps() {
        assert!(cast_seen(0, 420));
        assert!(!cast_seen(0, 10));
        assert!(!cast_seen(300, 420));
    }

    #[test]
    fn a_big_hit_breaks_it() {
        assert!(!hit_through(300, 1000, 35));
        assert!(hit_through(350, 1000, 35));
        assert!(!hit_through(10, 0, 35));
    }

    #[test]
    fn she_wears_known_heroes_only() {
        assert!(can_wear("league_garen"));
        assert!(!can_wear(HERO));
        assert!(!can_wear("someone_elses_hero"));
    }

    #[test]
    fn buff_names_fit() {
        assert!(PEN.len() <= BUFF_NAME_CAP);
        assert!(nk("p_poof").len() <= BUFF_NAME_CAP);
    }
}
