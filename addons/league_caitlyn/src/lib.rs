//! 凯特琳附加包（用户 2026-10-22：「女警前期压制力太低」「再想想AI那边的办法」「做附加包之类的也行」）。主包数据一字不改，
//! 本包只有一个 AI 钩子 `league_caitlyn:lane`：前 10 分钟对线时让游戏的 AI 拿她的射程和 Q 消耗对面英雄。
//!
//! 经典引擎模拟里（C:/t/ct_sim，诺手钩子的做法）：游戏的 AI 一好 Q 就拿去清兵（前 5 分钟 15 个 Q 有 11 个打在小兵上），
//! 打小兵时对面英雄就在射程边上也不打。钩子只在 AI 已经要普攻或放 Q 时改它的目标（走位、撤退、回城、别的技能都不碰），
//! 规则在 `plan.rs`（和模拟器同一份）：
//! - AI 放 Q（不管朝哪）：Q 射程内有对面英雄就朝他放（血少的先）；
//! - AI 普攻、Q 好了：Q 射程内有对面英雄就先 Q 他；
//! - AI 打的小兵不是补刀（这一枪打不死）：对面英雄在射程里（或往前一小步就到）就改打英雄；
//! - 她或目标在敌方塔下、她血量低于 35%、附近敌方英雄比我方多：不改。
//! 8 个种子（下路对 4 个原版射手、3 套阵容、两边）：前 5 分钟击杀差 +0.38 → +0.74，10 分钟 +1.65 → +2.14。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_caitlyn.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `Q POKE`（Q 改打英雄）、`HARASS`（普攻改打英雄）、`TALLY`（每个凯特琳每分钟一行：改了几次、为什么没改），都限了条数。

use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod plan;
use plan::{Base, Champ, Plan, Pt, Why};

const ID: &str = "league_caitlyn";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_caitlyn") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_CAITLYN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_caitlyn.log");
        }
    }
    PathBuf::from("league_caitlyn.log")
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

/// 每分钟一行：这一分钟里钩子的每种判断各几次（看它是不是在干活、为什么没改）。每个凯特琳一份，记在她的 AI 钩子上（引擎给
/// 每份模拟的每个玩家各一个钩子）：0.1.0 整个游戏只有一份、一个分钟数，几份模拟同时跑时（服务器同一局两份预模拟并排跑，局、
/// 实体编号都一样）每换一份就把上一份的写出去，日志里 m=2211 / m=2115 交替、每行只有一两项。钩子拿到的模拟是只读的，挂不了
/// 加里奥附加包 `SIM_TAG` 那样的模拟编号 buff，钩子自己就是每份模拟一个。
#[derive(Clone, Default)]
struct Tally {
    minute: Option<usize>,
    counts: BTreeMap<String, usize>,
}

impl Tally {
    /// One more `key` at `minute`: the minute before and its counts when this one starts a new minute (the line to write;
    /// an earlier minute is another match: started over, nothing written).
    fn add(&mut self, minute: usize, key: String) -> Option<(usize, BTreeMap<String, usize>)> {
        let mut done = None;
        if self.minute != Some(minute) {
            let counts = std::mem::take(&mut self.counts);
            if let Some(last) = self.minute.filter(|&m| m < minute && !counts.is_empty()) {
                done = Some((last, counts));
            }
            self.minute = Some(minute);
        }
        *self.counts.entry(key).or_insert(0) += 1;
        done
    }
}

// ===================== AI 钩子 =====================

/// 她这一枪对这个单位（护甲按 100 / (100 + 护甲)）。
pub fn shot(attack: usize, defence: usize) -> usize {
    attack * 100 / (100 + defence)
}

fn pct(hp: (usize, usize)) -> usize {
    if hp.1 > 0 {
        100 * hp.0 / hp.1
    } else {
        100
    }
}

fn at(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

#[derive(Clone, Default)]
struct Lane {
    /// her `TALLY` (each sim's Caitlyn her own)
    tally: Tally,
}

impl Lane {
    fn tally(&mut self, sim: &StableSim<'_>, me: usize, why: Why, changed: bool) {
        let minute = sim.tick() as usize / 3600;
        if let Some((m, counts)) = self.tally.add(minute, format!("{why:?}{}", if changed { "" } else { "_kept" })) {
            if let Some(k) = counted("tally") {
                let list: Vec<String> = counts.iter().map(|(w, n)| format!("{w}:{n}")).collect();
                wlog(format!("{} TALLY minute {m}: {} #{k}", head(sim, me), list.join(" ")));
            }
        }
    }
}

impl StablePlayerAi for Lane {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:lane")
    }

    /// 在 league_ult_press（100）之后：它把普攻换成 R 时本包不碰（只改普攻和 Q）。
    fn priority(&self) -> i32 {
        105
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        let kind = InputKindV1::from_code(b.kind)?;
        if !matches!(kind, InputKindV1::Attack | InputKindV1::Skill) {
            return None; // moves, retreats, recalls, W, R: the game's AI decides
        }
        let player = ctx.player_id();
        let (input, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (my_id, team, here) = (me.id(), me.team(), at(&me));
            let base_kind = match kind {
                InputKindV1::Skill => Base::Q,
                _ => {
                    let target = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target))
                        .then_some(b.target.target_id)
                        .and_then(|t| sim.get_entity(t));
                    match target {
                        Some(t) if t.is_champion() => Base::AttackChamp(t.id()),
                        Some(t) => Base::AttackOther {
                            last_hit: t.kind() != Some(EntityKindV1::Tower)
                                && t.hp().0 <= shot(me.stat().attack, t.stat().defence),
                        },
                        None => Base::Other,
                    }
                }
            };
            let q_ready = me.cooldown(SkillSlotV1::Skill).is_some_and(|c| c.unlocked && (c.remaining == 0 || c.charges > 0));
            let (mut foes, mut allies, mut towers): (Vec<Champ>, Vec<Champ>, Vec<Pt>) = (vec![], vec![], vec![]);
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if !u.is_alive() || u.id() == my_id {
                    continue;
                }
                if u.kind() == Some(EntityKindV1::Tower) {
                    if u.team() != team {
                        towers.push(at(&u));
                    }
                    continue;
                }
                if !u.is_champion() || (u.team() != team && !u.is_targetable()) {
                    continue;
                }
                let c = Champ { id: u.id(), pos: at(&u), hp_pct: pct(u.hp()) };
                if u.team() == team {
                    allies.push(c);
                } else {
                    foes.push(c);
                }
            }
            let (p, why) = plan::plan(sim.tick() as usize, here, pct(me.hp()), base_kind, &foes, &allies, &towers, q_ready);
            let input = match p {
                Plan::Keep => None,
                Plan::Q(t) => {
                    let to = sim.get_entity(t).map(|e| at(&e)).unwrap_or(here);
                    let (dx, dy) = ((to.0 - here.0).round() as i64, (to.1 - here.1).round() as i64);
                    Some(InputV1::action(InputKindV1::Skill, InputTargetV1::dir(dx, dy)))
                }
                Plan::Attack(t) => Some(InputV1::action(InputKindV1::Attack, InputTargetV1::target(t))),
            };
            self.tally(&sim, my_id, why, input.is_some());
            let line = input.map(|_| {
                let t = match p {
                    Plan::Q(t) | Plan::Attack(t) => t,
                    Plan::Keep => 0,
                };
                let d = sim.get_entity(t).map_or(0.0, |e| plan::d(at(&e), here));
                (why, format!("{} {} {} ({d:.0} away, the AI wanted {:?})", head(&sim, my_id),
                              if why == Why::QPoke { "Q POKE at" } else { "HARASS" }, who(&sim, t), kind))
            });
            (input, line)
        };
        let input = input?;
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some((why, text)) = line {
            if let Some(k) = counted(if why == Why::QPoke { "q" } else { "harass" }) {
                wlog(format!("{text} #{k}"));
            }
        }
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Caitlyn: lane pressure - Q and shots at the enemy laner early) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Lane::default());
    host.log(LogLevel::Info, "league_caitlyn loaded (Caitlyn's early lane pressure).");
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
    fn a_shot_through_armour() {
        assert_eq!(shot(100, 0), 100);
        assert_eq!(shot(100, 25), 80);
    }

    #[test]
    fn each_caitlyn_keeps_her_own_minute() {
        // two sims side by side, their thinks taking turns: neither writes out the other's minute
        let (mut a, mut b) = (Tally::default(), Tally::default());
        for _ in 0..3 {
            assert_eq!(a.add(2, "Harass".into()), None);
            assert_eq!(b.add(2, "Late_kept".into()), None);
        }
        let (m, counts) = a.add(3, "QPoke".into()).unwrap();
        assert_eq!((m, counts.len(), counts.get("Harass")), (2, 1, Some(&3)));
        assert_eq!(b.add(2, "Late_kept".into()), None);
        // a minute without a think: the line names the minute counted
        assert_eq!(a.add(5, "QPoke".into()).map(|(m, c)| (m, c.len())), Some((3, 1)));
        // an earlier minute: another match, started over
        assert_eq!(a.add(0, "Harass".into()), None);
        assert_eq!(a.add(1, "Harass".into()).map(|(m, c)| (m, c.get("Harass").copied())), Some((0, Some(1))));
    }

    #[test]
    fn the_q_reach_is_the_datas_own_pick() {
        // the main pack's Q picks a champion within 100000 (RandomTarget) and fires up to 120000
        let src = include_str!("../../../league/champion/league_caitlyn.data_champion");
        assert!(src.contains("\"range\": 100000"), "Q's champion pick moved");
        assert!(src.contains("\"range\": 65000"), "her attack range moved: ATK_REACH");
    }
}
