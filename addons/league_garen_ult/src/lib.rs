//! 盖伦附加包：R「德玛西亚正义」照英雄联盟做成斩杀（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补
//! 附加包」）。
//!
//! 主包是纯数据：读不到生命，R 写成 150 + 120% 攻击力 + 12% 目标最大生命的真实伤害，AI 一好就放，常常砍在满血的人身上。
//! 英雄联盟的 R 按目标**已损失**生命算，玩家留着它收人头。本包：
//!
//! - **AI 钩子 `league_garen_ult:ult`**：读射程内每个敌方英雄的生命、最大生命、护盾、免死和受到伤害增减，按这一剑落下的
//!   伤害（`plan.rs`：150 + 120% 攻击力 + 已损失生命的 30%）只在砍得死人时放，几个时砍生命 + 护盾最少的；AI 想放但
//!   砍不死，改成普攻那个人（打不到就走过去）。AI 钩子自己看 R 的冷却和等级。
//! - **被动 `league_garen_ult:verdict`**：副本的 R 不再有 12% 最大生命，出手时给目标挂 `league_garen_ult_mark`；本包看到
//!   标记，`MARK_TO_LAND` tick 后（主包的巨剑落下的那一刻）按他那时的已损失生命补 30% 的真实伤害。
//!
//! 画面、声音、主包那份伤害都在数据里。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_garen_ult.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod plan;
use plan::{plan as decide, Foe, Plan, HERO, MARK, MARK_TO_LAND, R_MISSING, R_RANGE};

const ID: &str = "league_garen_ult";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_garen_ult") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// R 从这一级起能放（同 league_darius_ult）。
const ULT_LEVEL: usize = 5;
/// 同一类日志至少隔这么多 tick 记一次。
const LOG_EVERY: usize = 120;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_GAREN_ULT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_garen_ult.log");
        }
    }
    PathBuf::from("league_garen_ult.log")
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

fn head(sim: &StableSim<'_>, who: &str) -> String {
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
    format!("[{kind} m={} s={}] t={} {who}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 读状态 =====================

fn read_foe(e: &StableEntity<'_, '_>) -> Foe {
    let (hp, max) = e.hp();
    let mut foe = Foe { id: e.id(), hp, max, shield: e.shield(), ..Foe::default() };
    for b in (0..e.buff_count()).filter_map(|i| e.buff_at(i)) {
        foe.undying |= b.undying;
        foe.reduce += b.damaged_reduce;
        foe.amplify += b.damaged_amplify;
        foe.skill_reduce += b.skill_damaged_reduce;
    }
    foe
}

fn ult(id: usize) -> InputV1 {
    InputV1::action(InputKindV1::Ult, InputTargetV1::target(id))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== AI 钩子 =====================

#[derive(Clone, Default)]
struct UltAi {
    last_hold: Option<usize>,
    last_cast_log: Option<(usize, usize)>,
    told_no_sim: bool,
}

impl StablePlayerAi for UltAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ult")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let wants_ult = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        let ai_target = base.filter(|_| wants_ult).and_then(|b| {
            (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
        });
        let busy = base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        let read = {
            let Some(sim) = ctx.sim() else {
                if !self.told_no_sim {
                    self.told_no_sim = true;
                    wlog(format!("t={tick} player {player}: no simulation to read, R left to the AI"));
                }
                return None;
            };
            (|| {
                let pl = sim.get_player(player)?;
                let cd = pl.cooldowns().map(|c| c.3);
                let me = pl.champion().filter(|e| e.is_alive())?;
                let free = pl.level() >= ULT_LEVEL && cd == Some(0);
                let (id, team) = (me.id(), me.team());
                let r2 = (R_RANGE as u64).saturating_mul(R_RANGE as u64);
                let enemy = |e: &StableEntity<'_, '_>| e.is_champion() && e.is_alive() && e.team() != team;
                let foes: Vec<Foe> = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .filter(|e| enemy(e) && e.is_targetable() && sim.distance_sq(id, e.id()) <= r2)
                    .map(|e| read_foe(&e))
                    .collect();
                let target = ai_target.and_then(|t| sim.get_entity(t));
                let ai_foe = target.as_ref().filter(|e| enemy(e)).map(|e| read_foe(e));
                let target_pos = target.as_ref().map(|e| e.pos());
                Some((me.stat().attack, free, foes, ai_foe, target_pos, me.pos(), head(&sim, &format!("#{id}"))))
            })()
        };
        let (attack, free, foes, ai_foe, target_pos, my_pos, line) = read?;
        let foes: Vec<Foe> = foes.into_iter().filter(|f| ctx.is_valid_input(&ult(f.id))).collect();
        let foe_of = |id: usize| foes.iter().chain(ai_foe.iter()).find(|f| f.id == id).copied();
        match decide(ai_target, ai_foe, &foes, attack, free && !busy) {
            Plan::Keep => None,
            Plan::Ult(id) => {
                let input = ult(id);
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if self.last_cast_log.is_none_or(|(t0, i)| i != id || tick >= t0 + LOG_EVERY) {
                    self.last_cast_log = Some((tick, id));
                    if let Some(f) = foe_of(id) {
                        wlog(format!("{line} R KILL: #{id} hp {}/{} + shield {} vs {} (attack {attack}){}", f.hp, f.max,
                                     f.shield, f.damage_from(f.r_damage(attack)),
                                     if ai_target.is_some() { "" } else { ", the AI had not cast it" }));
                    }
                }
                Some(input)
            }
            Plan::Hold(x) => {
                if self.last_hold.is_none_or(|t0| tick >= t0 + LOG_EVERY) {
                    self.last_hold = Some(tick);
                    let who = foe_of(x).map_or(format!("#{x} is no enemy champion alive"), |f| {
                        format!("#{x} hp {}/{} + shield {} > {}", f.hp, f.max, f.shield, f.damage_from(f.r_damage(attack)))
                    });
                    wlog(format!("{line} R HELD: {who}, attacking instead"));
                }
                let atk = InputV1::action(InputKindV1::Attack, InputTargetV1::target(x));
                if ctx.is_valid_input(&atk) {
                    return Some(atk);
                }
                let (x, y) = target_pos.unwrap_or(my_pos);
                Some(InputV1::move_to(x, y))
            }
        }
    }
}

// ===================== 被动：落剑时按已损失生命补伤害 =====================

#[derive(Clone, Default)]
struct Verdict {
    /// 看到标记的目标和那时的 tick。
    seen: Vec<(usize, usize)>,
    blows: usize,
}

impl StablePassive for Verdict {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.seen.clear();
        wlog(format!("{} SPAWN: the add-on's Garen (player {player})", head(sim, &format!("#{me}"))));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        // new marks: his R has just gone out at this champion
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.team() == team || !e.is_champion() {
                continue;
            }
            let id = e.id();
            if has_buff(sim, id, MARK) && !self.seen.iter().any(|s| s.0 == id) {
                self.seen.push((id, tick));
            }
        }
        // the sword lands: the share of the health he is missing now
        let due: Vec<(usize, usize)> = self.seen.iter().copied().filter(|s| tick >= s.1 + MARK_TO_LAND).collect();
        self.seen.retain(|s| tick < s.1 + MARK_TO_LAND);
        for (id, _) in due {
            sim.entity_remove_buff(id, MARK);
            let Some(e) = sim.get_entity(id) else { continue };
            if !e.is_alive() {
                continue;
            }
            let (hp, max) = e.hp();
            let extra = max.saturating_sub(hp) * R_MISSING / 100;
            if extra > 0 {
                sim.deal_damage_typed(me, id, extra, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            }
            self.blows += 1;
            if self.blows <= 80 || self.blows % 25 == 0 {
                wlog(format!("{} VERDICT #{} on #{id}: hp {hp}/{max}, +{extra} true damage", head(sim, &format!("#{me}")),
                             self.blows));
            }
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        // a sword already falling still lands (the main pack's Delayed runs); only forget nothing
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Garen's R an execute on missing health, cast only for a kill) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(UltAi::default());
    module.add_native_passive(format!("{ID}:verdict"), Verdict::default());
    host.log(LogLevel::Info, "league_garen_ult v1 loaded (Garen's R: an execute on missing health, only for a kill).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);
