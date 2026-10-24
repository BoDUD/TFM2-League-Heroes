//! 大招瞄准附加包：AI 放大招时挑英雄联盟玩家会挑的那个目标（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话
//! 全部补附加包」）。只有 AI 钩子，不换英雄数据。
//!
//! - **墨菲特 `league_ult_aim:malphite`**：英雄联盟的「势不可挡」朝一个点冲，玩家挑能撞起最多英雄的地方。主包的 R 只能点一名
//!   敌方英雄、落在他身上、撞起他身边 `MALPHITE_R`（30000）内的人，AI 点的常常是离得最近的那个。钩子数射程（75000）内每个
//!   敌方英雄身边 `MALPHITE_R` 内有几个敌方英雄，AI 想放 R 时改点数到最多的那个（一样多就照 AI 的）；R 好了、AI 没想放、
//!   有人身边能撞起 `MALPHITE_EAGER` 个以上英雄，就替它放。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ult_aim.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ult_aim";
/// R 从这一级起能放（同 league_darius_ult）。
const ULT_LEVEL: usize = 5;
const LOG_EVERY: usize = 120;
pub const MALPHITE: &str = "league_malphite";
pub const MALPHITE_RANGE: u64 = 75_000;
pub const MALPHITE_R: u64 = 30_000;
pub const MALPHITE_EAGER: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ULT_AIM_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ult_aim.log");
        }
    }
    PathBuf::from("league_ult_aim.log")
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

// ===================== 挑目标 =====================

/// An enemy champion in reach: id and how many enemy champions stand within the slam's radius of him (him included).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Spot {
    pub id: usize,
    pub around: usize,
}

/// The best of `spots` for the AI's `ai` target: the most around (the AI's own when it is as good).
pub fn best(spots: &[Spot], ai: Option<usize>) -> Option<Spot> {
    let top = spots.iter().map(|s| s.around).max()?;
    spots.iter().copied().filter(|s| s.around == top).find(|s| Some(s.id) == ai)
        .or_else(|| spots.iter().copied().find(|s| s.around == top))
}

fn ult(id: usize) -> InputV1 {
    InputV1::action(InputKindV1::Ult, InputTargetV1::target(id))
}

#[derive(Clone, Default)]
struct Malphite {
    last_log: Option<usize>,
}

impl StablePlayerAi for Malphite {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:malphite")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == MALPHITE
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let wants = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        let ai = base.filter(|_| wants).and_then(|b| {
            (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
        });
        let busy = base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        let (spots, free) = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let free = pl.level() >= ULT_LEVEL && pl.cooldowns().map(|c| c.3) == Some(0);
            let me = pl.champion().filter(|e| e.is_alive())?;
            let (id, team) = (me.id(), me.team());
            let foes: Vec<usize> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.is_champion() && e.is_alive() && e.team() != team && e.is_targetable())
                .map(|e| e.id())
                .collect();
            let reach = MALPHITE_RANGE * MALPHITE_RANGE;
            let slam = MALPHITE_R * MALPHITE_R;
            let spots: Vec<Spot> = foes
                .iter()
                .filter(|&&f| sim.distance_sq(id, f) <= reach)
                .map(|&f| Spot { id: f, around: foes.iter().filter(|&&g| sim.distance_sq(f, g) <= slam).count() })
                .collect();
            (spots, free)
        };
        let spots: Vec<Spot> = spots.into_iter().filter(|s| ctx.is_valid_input(&ult(s.id))).collect();
        let pick = best(&spots, ai)?;
        let take = if wants { ai != Some(pick.id) } else { free && !busy && pick.around >= MALPHITE_EAGER };
        if !take {
            return None;
        }
        if self.last_log.is_none_or(|t| tick >= t + LOG_EVERY) {
            self.last_log = Some(tick);
            wlog(format!("t={tick} player {player} MALPHITE R -> #{} ({} champions around), the AI {}", pick.id, pick.around,
                         match ai { Some(x) => format!("had #{x}"), None => "had not cast it".to_string() }));
        }
        Some(ult(pick.id))
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (ults aimed as League players aim them: Malphite) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Malphite::default());
    host.log(LogLevel::Info, "league_ult_aim v1 loaded (Malphite's ult aimed at the most champions).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_most_around_wins_the_ais_own_on_a_tie() {
        let s = [Spot { id: 1, around: 1 }, Spot { id: 2, around: 3 }, Spot { id: 3, around: 3 }];
        assert_eq!(best(&s, Some(1)).map(|x| x.id), Some(2));
        assert_eq!(best(&s, Some(3)).map(|x| x.id), Some(3));
        assert_eq!(best(&[], Some(3)), None);
    }
}
