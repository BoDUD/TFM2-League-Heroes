//! 希瓦娜附加包（用户 2026-10-24：「龙女变成龙不能保持住？」）。本包补数据做不到的两件事：
//!
//! - **整身变龙**（`view.rs`）：龙形时站着、跑着、挨打、阵亡也是龙（纳尔附加包整身变巨型的做法）。主包只有出招是龙
//!   （`CasterAnimation` 播 `d_*`），游戏按名字自动播的 idle / run / hit / dead 仍是人形。
//! - **龙鳞铁衣**（0.1.2，用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」）：英雄联盟 "Large monsters and
//!   large minions grant 1 stack, while enemy champions and epic monsters grant 3"，每层 0.3 护甲、0.3 魔抗。主包的数据
//!   看不到击杀，把它折进了龙形（龙形期间护甲、魔抗 +30%）。`mod.override_info` 把希瓦娜换成 `override/` 里的副本
//!   （`make_override.py` 从主包生成：龙形只留生命，挂上本包的被动；普攻一个字节都不动——另一边正在量她的普攻），被动
//!   `league_shyvana:scalemail` 数层：英雄击杀和助攻（`on_kill` / `on_assist`）、史诗野怪（最后一击）各 `champion` /
//!   `epic` 层，野怪营地（`on_unit_kill`）`large` 层；这局地图上没有大型小兵，小兵不算。层数整局都在（阵亡不丢），护甲、
//!   魔抗挂在一个永久 buff `SCALE` 上（每层 `per10` / 10，取整），层数变了、复活时重新挂。数字在英雄数据的
//!   `passive.params`。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shyvana.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! 显示处理表的槽换上没有、每个希瓦娜换形态的那一帧、每 10 秒换了几次动画名。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_shyvana";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_shyvana") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 龙形的 buff（主包数据：变龙 dg_t tick）和龙形刚结束、还没播变回动作的标记。
pub const DRAGON: [&str; 2] = ["league_shyvana_dg", "league_shyvana_was_dg"];
/// 龙鳞铁衣的护甲、魔抗（一个永久 buff，层数变了、复活时重新挂）。
pub const SCALE: &str = "league_shyvana_scalemail";
/// 被动：副本的 `passive.passive_ref`。
pub const PASSIVE: &str = "league_shyvana:scalemail";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SHYVANA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_shyvana.log");
        }
    }
    PathBuf::from("league_shyvana.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line stalled the simulation thread (2026-10-12, #242)
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

// ===================== 龙鳞铁衣 =====================

/// 一层从哪来。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source {
    Champion,
    Epic,
    Large,
}

/// 副本的 `passive.params`：每种来源几层、每层多少（十分之一点）护甲和魔抗。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub champion: usize,
    pub epic: usize,
    pub large: usize,
    pub per10: usize,
}

impl Default for Params {
    fn default() -> Self {
        // League (V26.06 hotfix): champions and epic monsters 3, large monsters / large minions 1; 0.3 a stack
        Params { champion: 3, epic: 3, large: 1, per10: 3 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k.trim().trim_matches('"') {
            "champion" => p.champion = v,
            "epic" => p.epic = v,
            "large" => p.large = v,
            "per10" => p.per10 = v,
            _ => {}
        }
    }
    p
}

impl Params {
    pub fn stacks(&self, source: Source) -> usize {
        match source {
            Source::Champion => self.champion,
            Source::Epic => self.epic,
            Source::Large => self.large,
        }
    }

    /// 这么多层的护甲（魔抗一样）：每层 `per10` / 10，取整。
    pub fn armour(&self, stacks: usize) -> i32 {
        (stacks * self.per10 / 10).min(i32::MAX as usize) as i32
    }
}

/// 一个被打死的非英雄单位算哪一种。小兵：这局地图上没有大型小兵，不算。
pub fn unit_source(kind: Option<EntityKindV1>) -> Option<Source> {
    match kind {
        Some(EntityKindV1::Jungle) => Some(Source::Large),
        Some(EntityKindV1::Epic | EntityKindV1::Serpen) => Some(Source::Epic),
        _ => None,
    }
}

/// 同一只史诗野怪只算一次（`on_kill` 和 `on_unit_kill` 都可能报它）：记下的 (单位, tick) 留这么久。
const SEEN_TICKS: usize = 600;

static COUNTS: LazyLock<Mutex<std::collections::HashMap<&'static str, usize>>> =
    LazyLock::new(|| Mutex::new(std::collections::HashMap::new()));
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;

/// 日志行：你看的那场每一行都写，服务器的预模拟每种先写 `LOG_FIRST` 行，之后每 `LOG_EVERY` 行一行（整个游戏一个计数）。
fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let shown = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, me: usize) -> String {
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
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

/// 看一眼 buff 的间隔（复活是新的实体：那时马上补挂）。
const KEEP_EVERY: usize = 3;

/// 层数、记过的史诗野怪（单元测试用；被动里就是它）。
#[derive(Clone, Debug, Default)]
pub struct Stacks {
    pub n: usize,
    seen: Vec<(usize, usize)>,
}

impl Stacks {
    /// 加一种来源的层数；返回加了几层。史诗野怪同一只（`victim`）`SEEN_TICKS` 内只算一次。
    pub fn gain(&mut self, p: &Params, source: Source, victim: Option<usize>, tick: usize) -> usize {
        if source == Source::Epic {
            self.seen.retain(|&(_, t)| t + SEEN_TICKS > tick);
            if let Some(v) = victim {
                if self.seen.iter().any(|&(s, _)| s == v) {
                    return 0;
                }
                self.seen.push((v, tick));
            }
        }
        let n = p.stacks(source);
        self.n += n;
        n
    }
}

#[derive(Clone, Default)]
struct Scalemail {
    p: Params,
    stacks: Stacks,
    /// 现在挂着的：(她的实体, 护甲)。
    shown: Option<(usize, i32)>,
}

impl Scalemail {
    fn gain(&mut self, sim: &mut StableSim<'_>, me: usize, source: Source, victim: Option<usize>, what: &str) {
        let n = self.stacks.gain(&self.p, source, victim, sim.tick());
        if n == 0 {
            return;
        }
        self.keep(sim, me);
        if let Some(k) = tally(sim, "scale") {
            let a = self.p.armour(self.stacks.n);
            wlog(format!("{} SCALE #{k}: +{n} ({what}) -> {} stacks, +{a} armour and magic resist", head(sim, me),
                         self.stacks.n));
        }
    }

    /// 她身上的 `SCALE` 是这么多层的护甲、魔抗（不是就重新挂）；死着不挂。
    fn keep(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let want = self.p.armour(self.stacks.n);
        let Some(on) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| {
            (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == SCALE).map(|b| (b.defence, b.magic_resistance))
        }) else {
            return;
        };
        let new_body = self.shown.is_some_and(|(body, _)| body != me);
        if on == Some((want, want)) || (want == 0 && on.is_none()) {
            self.shown = Some((me, want));
            return;
        }
        sim.entity_remove_buff(me, SCALE);
        if want > 0 {
            let mut b = BuffV1::named(SCALE);
            b.defence = want;
            b.magic_resistance = want;
            sim.add_buff(me, &b);
        }
        if new_body {
            if let Some(k) = tally(sim, "keep") {
                wlog(format!("{} SCALE KEEP #{k}: a new body, {} stacks hung again (+{want})", head(sim, me), self.stacks.n));
            }
        }
        self.shown = Some((me, want));
    }

    fn unit(&mut self, sim: &mut StableSim<'_>, me: usize, victim: usize, hook: &str) {
        let kind = sim.get_entity(victim).and_then(|e| e.kind());
        match unit_source(kind) {
            Some(Source::Epic) => self.gain(sim, me, Source::Epic, Some(victim), &format!("epic monster #{victim}, {hook}")),
            // camps come by on_unit_kill (an on_kill of one would count twice)
            Some(Source::Large) if hook == "on_unit_kill" => {
                self.gain(sim, me, Source::Large, Some(victim), &format!("camp #{victim}"))
            }
            _ => {}
        }
    }
}

impl StablePassive for Scalemail {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if let Some(k) = tally(sim, "spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Shyvana (player {player}), {} stacks, {:?}", head(sim, me),
                         self.stacks.n, self.p));
        }
        self.keep(sim, me);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.gain(sim, me, Source::Champion, None, &format!("killed #{victim}"));
        } else {
            self.unit(sim, me, victim, "on_kill");
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.gain(sim, me, Source::Champion, None, "assist");
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.unit(sim, me, victim, "on_unit_kill");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if sim.tick() % KEEP_EVERY == 0 || self.shown.is_none_or(|(body, _)| body != me) {
            self.keep(sim, me);
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
        "=== {ID} v{VERSION} (Shyvana: the whole-body dragon, Scalemail stacks on takedowns) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(PASSIVE, Scalemail::default());
    host.log(LogLevel::Info, "league_shyvana loaded (whole-body dragon, Scalemail).");
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

    /// League's Scalemail: champions (kills and assists) and epic monsters 3 stacks, large monsters 1, 0.3 armour and
    /// magic resist a stack; one epic monster counted once whichever hook tells of it.
    #[test]
    fn scalemail_stacks_by_source() {
        let p = parse_params(r#"{"champion":3,"epic":3,"large":1,"per10":3}"#);
        assert_eq!(p, Params::default());
        let mut s = Stacks::default();
        assert_eq!(s.gain(&p, Source::Large, Some(40), 100), 1);
        assert_eq!(s.gain(&p, Source::Large, Some(41), 200), 1);
        assert_eq!(s.gain(&p, Source::Champion, None, 300), 3);
        assert_eq!(s.gain(&p, Source::Champion, None, 300), 3); // a kill and an assist in one tick: two takedowns
        assert_eq!(s.gain(&p, Source::Epic, Some(77), 400), 3);
        assert_eq!(s.gain(&p, Source::Epic, Some(77), 401), 0); // the same monster told twice
        assert_eq!(s.gain(&p, Source::Epic, Some(77), 400 + SEEN_TICKS), 3); // a new one under the same id later
        assert_eq!(s.n, 14);
        // 0.3 a stack, rounded down
        assert_eq!(p.armour(0), 0);
        assert_eq!(p.armour(3), 0);
        assert_eq!(p.armour(4), 1);
        assert_eq!(p.armour(14), 4);
        assert_eq!(p.armour(100), 30);
        // camps are large monsters; the serpent and the epic monster epic; minions (no large ones on this map) nothing
        assert_eq!(unit_source(Some(EntityKindV1::Jungle)), Some(Source::Large));
        assert_eq!(unit_source(Some(EntityKindV1::Serpen)), Some(Source::Epic));
        assert_eq!(unit_source(Some(EntityKindV1::Epic)), Some(Source::Epic));
        assert_eq!(unit_source(Some(EntityKindV1::Minion)), None);
        assert_eq!(unit_source(Some(EntityKindV1::Summon)), None);
        assert_eq!(unit_source(None), None);
        assert!(SCALE.len() <= BUFF_NAME_CAP);
    }

    /// The copy: the main pack's attack to the byte (another session measures it), the dragon with only its health
    /// (Scalemail is the passive now), the passive hung.
    #[test]
    fn the_copy_keeps_her_attack_and_moves_scalemail_to_the_passive() {
        // the main pack from the repo (league_addons, which compiles this test too, sits next to this crate); the copy
        // next to this file
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
        let main = std::fs::read_to_string(root.join("../../league/champion/league_shyvana.data_champion")).unwrap()
            .replace("\r\n", "\n");
        let copy = include_str!("../override/league_shyvana.data_champion").replace("\r\n", "\n");
        let section = |text: &str, key: &str| -> String {
            let start = text.find(&format!("\n  \"{key}\": ")).unwrap_or_else(|| panic!("no {key}"));
            let rest = &text[start + 1..];
            let end = rest[1..].find("\n  \"").map_or(rest.len(), |e| e + 1);
            rest[..end].trim_end_matches(['\n', ',']).to_string()
        };
        assert_eq!(section(&main, "attack"), section(&copy, "attack"), "the copy's attack differs from the main pack's");
        assert!(section(&main, "ult").contains("\"defence_mult\": 30"), "the main pack's dragon changed: check make_override.py");
        assert!(!section(&copy, "ult").contains("defence_mult") && !section(&copy, "ult").contains("magic_resistance_mult"));
        assert!(section(&copy, "ult").contains("\"hp_mult\": 30"), "the dragon keeps its health");
        assert!(copy.contains(&format!("\"passive_ref\": \"{PASSIVE}\"")));
    }

    /// The form buffs are the main pack's (build_shyvana.py's `dg` and `was_dg`).
    #[test]
    fn the_dragon_buffs_are_in_the_main_pack() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../league/champion/league_shyvana.data_champion");
        let data = std::fs::read_to_string(path).unwrap();
        for b in DRAGON {
            assert!(data.contains(&format!("\"{b}\"")), "{b}");
        }
    }
}
