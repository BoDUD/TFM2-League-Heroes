//! 参与击杀附加包：金克丝、崔丝塔娜、易的「击杀后」效果照英雄联盟算每一次参与击杀（击杀和助攻），易还有普攻减 Q 冷却、
//! 大招免疫减速（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据，只认得出她（他）自己打出的最后一击（league_jinx 的击杀检查），助攻看不见。`mod.override_info` 把三人换成
//! `override/` 里的副本（`make_override.py` 从主包生成），各挂本包的一个被动：
//!
//! - **金克丝 `league_takedowns:jinx`**：每一次英雄击杀和助攻都给「罪恶快感」——主包的四个 buff（攻速、三段移速，名字和
//!   数字照主包，`make_override.py` 核对），播主包的画面和音效。副本去掉数据里的击杀检查（不然她自己的击杀算两次）。
//! - **崔丝塔娜 `league_takedowns:tristana`**：每一次英雄击杀和助攻都刷新火箭跳跃（去掉主包的冷却标记 `league_tristana_w_cd`，
//!   播主包的「就绪」画面）。主包自己的击杀检查留着（同一个标记，去两次也一样）。
//! - **易 `league_takedowns:masteryi`**：每一次英雄击杀和助攻，阿尔法突袭和冥想（无极剑道）的剩余冷却减 `YI_CUT`%；
//!   无极剑道开着时再延长 `YI_EXTEND` tick。他每次普攻，阿尔法突袭冷却减 `YI_ATTACK_CUT` tick。无极剑道期间身上的
//!   减速都去掉（免疫减速）。副本的无极剑道去掉主包近似用的「冷却加快 40%」。
//!
//! - **图奇 `league_takedowns:twitch`**：英雄联盟里身上有毒的敌方英雄死了就刷新埋伏。主包只认他自己的击杀（击杀检查留着），
//!   本包补上助攻：清掉 Q 的剩余冷却（`entity_reduce_cooldown`），播主包的刷新画面和声音（`TWITCH_RESET`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_takedowns.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_takedowns";

/// 金克丝「罪恶快感」：主包的四个 buff（名字、持续 tick、攻速 %、移速 %）。
pub const JINX_EXCITED: [(&str, usize, i32, i32); 4] = [
    ("league_jinx_excited", 360, 25, 0),
    ("league_jinx_excited_ms1", 120, 0, 40),
    ("league_jinx_excited_ms2", 240, 0, 30),
    ("league_jinx_excited_ms3", 360, 0, 30),
];
pub const JINX_VIEW: &str = "league_jinx_excited";
/// 崔丝塔娜火箭跳跃的冷却标记和「就绪」画面。
pub const TRIS_W_CD: &str = "league_tristana_w_cd";
pub const TRIS_READY: &str = "league_tristana_w_ready";
/// 图奇埋伏刷新的画面和声音（主包同名）；一次减掉的冷却（比 Q 的 900 tick 长就是清零）。
pub const TWITCH_RESET: &str = "league_twitch_q_reset";
pub const TWITCH_CUT: usize = 3_600;
/// 易：无极剑道的 buff，参与击杀减剩余冷却 %，延长 tick，普攻减 Q 冷却 tick。
pub const YI_HIGHLANDER: &str = "league_masteryi_highlander";
pub const YI_CUT: usize = 70;
pub const YI_EXTEND: usize = 240;
pub const YI_ATTACK_CUT: usize = 60;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TAKEDOWNS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_takedowns.log");
        }
    }
    PathBuf::from("league_takedowns.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 小工具 =====================

fn buff_left(sim: &StableSim<'_>, id: usize, name: &str) -> Option<usize> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).map(|b| {
        if BuffDurationV1::from_code(b.duration_kind) == Some(BuffDurationV1::Time) { b.duration_tick } else { usize::MAX }
    }).max()
}

fn remaining(sim: &StableSim<'_>, id: usize, slot: SkillSlotV1) -> usize {
    sim.get_entity(id).and_then(|e| e.cooldown(slot)).map_or(0, |c| c.remaining)
}

/// `pct`% of the remaining cooldown off (rounded down).
pub fn cut(left: usize, pct: usize) -> usize {
    left * pct / 100
}

fn victim_is_champion(sim: &StableSim<'_>, victim: usize) -> bool {
    sim.get_entity(victim).is_some_and(|v| v.is_champion())
}

// ===================== 金克丝 =====================

#[derive(Clone, Default)]
struct Jinx {
    n: usize,
}

impl Jinx {
    fn excite(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        for (name, ticks, attack_speed, move_speed) in JINX_EXCITED {
            sim.entity_remove_buff(me, name);
            let mut b = BuffV1::timed(name, ticks);
            b.attack_speed_mult = attack_speed;
            b.move_speed_mult = move_speed;
            sim.add_buff(me, &b);
        }
        let at = InputTargetV1::target(me);
        sim.play_view_effect(JINX_VIEW, me, &at, 0, 0, 0);
        sim.play_sfx(JINX_VIEW, me, &at);
        self.n += 1;
        if self.n <= 80 {
            wlog(format!("{} JINX EXCITED #{} ({why})", head(sim, me), self.n));
        }
    }
}

impl StablePassive for Jinx {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Jinx (player {player})", head(sim, me)));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if victim_is_champion(sim, victim) {
            self.excite(sim, me, &format!("killed #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.excite(sim, me, "assist");
    }
}

// ===================== 崔丝塔娜 =====================

#[derive(Clone, Default)]
struct Tristana {
    n: usize,
}

impl Tristana {
    fn reset(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        if sim.entity_remove_buff(me, TRIS_W_CD) > 0 {
            sim.play_view_effect(TRIS_READY, me, &InputTargetV1::target(me), 0, 0, 0);
        }
        self.n += 1;
        if self.n <= 80 {
            wlog(format!("{} TRISTANA W RESET #{} ({why})", head(sim, me), self.n));
        }
    }
}

impl StablePassive for Tristana {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Tristana (player {player})", head(sim, me)));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if victim_is_champion(sim, victim) {
            self.reset(sim, me, &format!("killed #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.reset(sim, me, "assist");
    }
}

// ===================== 图奇 =====================

#[derive(Clone, Default)]
struct Twitch {
    n: usize,
}

impl StablePassive for Twitch {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Twitch (player {player})", head(sim, me)));
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        let left = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill)).map(|c| c.remaining).unwrap_or(0);
        if left == 0 {
            return;
        }
        sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, TWITCH_CUT);
        sim.play_view_effect(TWITCH_RESET, me, &InputTargetV1::target(me), 0, 0, 0);
        sim.play_sfx(TWITCH_RESET, me, &InputTargetV1::target(me));
        self.n += 1;
        if self.n <= 80 {
            wlog(format!("{} TWITCH Q RESET #{} (assist, {left} ticks left)", head(sim, me), self.n));
        }
    }
}

// ===================== 易 =====================

#[derive(Clone, Default)]
struct MasterYi {
    n: usize,
}

impl MasterYi {
    fn takedown(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let (q, w) = (remaining(sim, me, SkillSlotV1::Skill), remaining(sim, me, SkillSlotV1::Skill2));
        if q > 0 {
            sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, cut(q, YI_CUT));
        }
        if w > 0 {
            sim.entity_reduce_cooldown(me, SkillSlotV1::Skill2, cut(w, YI_CUT));
        }
        let extended = match buff_left(sim, me, YI_HIGHLANDER) {
            Some(left) if left != usize::MAX => {
                // the copy's Highlander: the main pack's speeds, no cooldown share; made again, YI_EXTEND longer
                let mut b = BuffV1::timed(YI_HIGHLANDER, left + YI_EXTEND);
                let e = sim.get_entity(me);
                if let Some(old) = e.and_then(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == YI_HIGHLANDER)) {
                    b.attack_speed_mult = old.attack_speed_mult;
                    b.move_speed_mult = old.move_speed_mult;
                }
                sim.entity_remove_buff(me, YI_HIGHLANDER);
                sim.add_buff(me, &b);
                true
            }
            _ => false,
        };
        self.n += 1;
        if self.n <= 80 {
            wlog(format!("{} YI TAKEDOWN #{} ({why}): Q {q} -> {}, W {w} -> {}{}", head(sim, me), self.n, q - cut(q, YI_CUT),
                         w - cut(w, YI_CUT), if extended { ", Highlander extended" } else { "" }));
        }
    }
}

impl StablePassive for MasterYi {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Master Yi (player {player})", head(sim, me)));
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _target: usize, _damage: &mut usize) {
        if remaining(sim, me, SkillSlotV1::Skill) > 0 {
            sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, YI_ATTACK_CUT);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if victim_is_champion(sim, victim) {
            self.takedown(sim, me, &format!("killed #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.takedown(sim, me, "assist");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if buff_left(sim, me, YI_HIGHLANDER).is_none() {
            return;
        }
        // Highlander: immune to slows (every buff on him that lowers his move speed goes)
        let slows: Vec<String> = match sim.get_entity(me) {
            Some(e) => (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.move_speed_mult < 0)
                .map(|b| b.name().to_string()).collect(),
            None => return,
        };
        for name in slows {
            sim.entity_remove_buff(me, &name);
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Jinx, Tristana, Master Yi and Twitch on every takedown) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:jinx"), Jinx::default());
    module.add_native_passive(format!("{ID}:tristana"), Tristana::default());
    module.add_native_passive(format!("{ID}:masteryi"), MasterYi::default());
    module.add_native_passive(format!("{ID}:twitch"), Twitch::default());
    host.log(LogLevel::Info, "league_takedowns v1 loaded (Jinx, Tristana and Master Yi on every takedown).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_takedown_cuts_most_of_what_is_left() {
        assert_eq!(cut(400, YI_CUT), 280);
        assert_eq!(cut(0, YI_CUT), 0);
    }

    #[test]
    fn the_names_fit() {
        for (n, ..) in JINX_EXCITED {
            assert!(n.len() <= BUFF_NAME_CAP);
        }
        assert!(YI_HIGHLANDER.len() <= BUFF_NAME_CAP);
    }
}
