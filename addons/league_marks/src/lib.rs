//! 目标标记附加包：读敌人身上的标记，照英雄联盟做「只对带标记的那个目标」的效果（用户 2026-10-24：「查看现在没有做附加包的
//! 英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据：`SwitchByBuff` 只读得到施放者自己身上的 buff，读不到目标身上的，所以「目标带不带标记」都改成了「她自己最近
//! 有没有打中过」。原生代码读得到每个单位的 buff。`mod.override_info` 换上的副本（`make_override.py` 从主包生成）在要判断
//! 的那一下给目标挂一个短的「问」标记，本包看那个目标身上有没有主包的标记，把答案挂在施放者身上让数据读：
//!
//! - **黛安娜 `league_marks:diana`**：E「月光冲击」冲向的目标身上有月光（主包 Q 挂的 `league_diana_moon_mark`）时，才挂
//!   `league_diana_moonlit`，数据读到就立刻再冲一次；同时把所有敌人身上的月光去掉（英雄联盟：冲到带月光的目标会消耗全部
//!   月光）。主包是 Q 打中过任何东西就能再冲。
//!
//! - **凯南 `league_marks:kennen`**：雷缚印按目标数层（主包记在凯南自己身上：打 A 一次、打 B 两次，B 就被眩晕）。副本每次
//!   印记命中给目标挂 `KENNEN_HIT`；本包给那个目标记一层（`KENNEN_LIFE` tick 内有效），第三层眩晕他 `KENNEN_STUN` tick
//!   （他 `KENNEN_RECENT` tick 内被凯南眩晕过就只有 `KENNEN_STUN_AGAIN`），播主包的印记、眩晕画面和音效。
//! - **卡莎 `league_marks:kaisa`**：体表活肤的电浆按目标数层（主包记在卡莎身上）。副本把普攻、被控英雄的加层和 W 的加层
//!   各换成给目标挂一个标记（`KAISA_ATTACK` / `KAISA_CC` / `KAISA_W2` / `KAISA_W3`）；本包给那个目标加层（`KAISA_LIFE`
//!   tick 内有效）：普攻每次附加 `base + step × 层数` + `ap`% 法强的魔法伤害，第五层引爆：`pop` + `pop_ad`% 攻击力 +
//!   `pop_hp`% 目标最大生命的真实伤害（数字照主包，在 `passive.params`），播主包的层数和引爆画面。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_marks.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_marks";
pub const DIANA_MOON: &str = "league_diana_moon_mark";
pub const DIANA_ASK: &str = "league_marks_diana_e";
pub const DIANA_YES: &str = "league_diana_moonlit";
/// 答案挂多久（数据隔 2 tick 来读）。
pub const ANSWER: usize = 4;
pub const KENNEN_HIT: &str = "league_marks_kennen_hit";
pub const KENNEN_LIFE: usize = 360;
pub const KENNEN_STUN: u64 = 75;
pub const KENNEN_STUN_AGAIN: u64 = 30;
pub const KENNEN_RECENT: usize = 420;
pub const KAISA_ATTACK: &str = "league_marks_kaisa_a";
pub const KAISA_CC: &str = "league_marks_kaisa_c";
pub const KAISA_W2: &str = "league_marks_kaisa_w2";
pub const KAISA_W3: &str = "league_marks_kaisa_w3";
pub const KAISA_LIFE: usize = 240;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MARKS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_marks.log");
        }
    }
    PathBuf::from("league_marks.log")
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

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// Enemies of `team` alive with `name` on them.
fn enemies_with(sim: &StableSim<'_>, team: usize, name: &str) -> Vec<usize> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.team() != team && e.is_alive() && has(e, name))
        .map(|e| e.id())
        .collect()
}

// ===================== 黛安娜 =====================

#[derive(Clone, Default)]
struct Diana {
    asked: usize,
    yes: usize,
}

impl StablePassive for Diana {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Diana (player {player})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        for target in enemies_with(sim, team, DIANA_ASK) {
            sim.entity_remove_buff(target, DIANA_ASK);
            self.asked += 1;
            let moonlit = sim.get_entity(target).is_some_and(|e| has(&e, DIANA_MOON));
            if moonlit {
                self.yes += 1;
                sim.entity_remove_buff(me, DIANA_YES);
                sim.add_buff(me, &BuffV1::timed(DIANA_YES, ANSWER));
                for lit in enemies_with(sim, team, DIANA_MOON) {
                    sim.entity_remove_buff(lit, DIANA_MOON);
                }
            }
            if self.asked <= 80 {
                wlog(format!("{} DIANA E #{} on #{target}: {} ({} of {} moonlit)", head(sim, me), self.asked,
                             if moonlit { "moonlit, dash again" } else { "no moonlight" }, self.yes, self.asked));
            }
        }
    }
}

// ===================== 按目标数层 =====================

/// One target's stacks: id, count, the tick of the last stack.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Stack {
    pub id: usize,
    pub n: usize,
    pub at: usize,
}

/// The count on `id` now (gone after `life` ticks without a new stack).
pub fn count(stacks: &[Stack], id: usize, now: usize, life: usize) -> usize {
    stacks.iter().find(|s| s.id == id && now <= s.at + life).map_or(0, |s| s.n)
}

pub fn set(stacks: &mut Vec<Stack>, id: usize, n: usize, now: usize) {
    stacks.retain(|s| s.id != id);
    if n > 0 {
        stacks.push(Stack { id, n, at: now });
    }
}

/// Kennen's mark landing on one with `n` marks: (marks after, stunned now).
pub fn kennen_mark(n: usize) -> (usize, bool) {
    if n >= 2 { (0, true) } else { (n + 1, false) }
}

/// Kai'Sa: one kind of hit on a target with `n` stacks, adding `add`: (stacks after, the attack's extra hit with `n`
/// stacks before it, popped).
pub fn kaisa_hit(n: usize, add: usize, attack: bool) -> (usize, Option<usize>, bool) {
    if n + add >= 5 {
        (0, attack.then_some(n), true)
    } else {
        (n + add, attack.then_some(n), false)
    }
}

/// (target, which of `marks`) for every mark on a living enemy of `team` (twice when it carries two).
fn gather(sim: &StableSim<'_>, team: usize, marks: &[&str]) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || !e.is_alive() {
            continue;
        }
        for (k, m) in marks.iter().enumerate() {
            let n = (0..e.buff_count()).filter_map(|j| e.buff_at(j)).filter(|b| b.name() == *m).count();
            for _ in 0..n {
                out.push((e.id(), k));
            }
        }
    }
    out
}

fn view(sim: &mut StableSim<'_>, me: usize, target: usize, name: &str, sound: bool) {
    let at = InputTargetV1::target(target);
    sim.play_view_effect(name, me, &at, 0, 0, 0);
    if sound {
        sim.play_sfx(name, me, &at);
    }
}

fn params(json: &str) -> Vec<(String, usize)> {
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    body.split(',')
        .filter_map(|pair| {
            let (k, v) = pair.split_once(':')?;
            Some((k.trim().trim_matches('"').to_string(), v.trim().parse::<usize>().ok()?))
        })
        .collect()
}

fn get(p: &[(String, usize)], k: &str) -> usize {
    p.iter().find(|(n, _)| n == k).map_or(0, |(_, v)| *v)
}

#[derive(Clone, Default)]
struct Kennen {
    stacks: Vec<Stack>,
    stunned: Vec<(usize, usize)>,
    n: usize,
}

impl StablePassive for Kennen {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Kennen (player {player})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let now = sim.tick();
        let hits = gather(sim, team, &[KENNEN_HIT]);
        for &(target, _) in hits.iter() {
            sim.entity_remove_buff(target, KENNEN_HIT);
        }
        for (target, _) in hits {
            let (after, stun) = kennen_mark(count(&self.stacks, target, now, KENNEN_LIFE));
            set(&mut self.stacks, target, after, now);
            if stun {
                let again = self.stunned.iter().any(|&(id, t)| id == target && now <= t + KENNEN_RECENT);
                let ticks = if again { KENNEN_STUN_AGAIN } else { KENNEN_STUN };
                sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Stun, ticks));
                self.stunned.retain(|&(id, _)| id != target);
                self.stunned.push((target, now));
                view(sim, me, target, "league_kennen_k_stun", true);
                self.n += 1;
                if self.n <= 80 {
                    wlog(format!("{} KENNEN STUN #{} on #{target}: {ticks} ticks", head(sim, me), self.n));
                }
            } else {
                view(sim, me, target, if after == 1 { "league_kennen_k_mark1" } else { "league_kennen_k_mark2" }, false);
            }
        }
    }
}

#[derive(Clone, Default)]
struct Kaisa {
    p: Vec<(String, usize)>,
    stacks: Vec<Stack>,
    pops: usize,
}

impl StablePassive for Kaisa {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Kai'Sa (player {player}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, attack, power) = (e.team(), e.stat().attack, e.stat().magic_power);
        let now = sim.tick();
        // her attack first (its extra hit reads the stacks before it), then the CC twin, then W
        let mut hits = gather(sim, team, &[KAISA_ATTACK, KAISA_CC, KAISA_W2, KAISA_W3]);
        hits.sort_by_key(|&(_, k)| k);
        for name in [KAISA_ATTACK, KAISA_CC, KAISA_W2, KAISA_W3] {
            for &(target, _) in hits.iter() {
                sim.entity_remove_buff(target, name);
            }
        }
        for (target, kind) in hits {
            let add = [1, 1, 2, 3][kind];
            let (after, extra, popped) = kaisa_hit(count(&self.stacks, target, now, KAISA_LIFE), add, kind == 0);
            set(&mut self.stacks, target, after, now);
            if let Some(before) = extra {
                let d = get(&self.p, "base") + get(&self.p, "step") * before + power * get(&self.p, "ap") / 100;
                sim.deal_damage_typed(me, target, d, DamageTypeV1::Ap, AttackTypeV1::BaseAttack);
            }
            if popped {
                let max = sim.get_entity(target).map_or(0, |t| t.hp().1);
                let d = get(&self.p, "pop") + attack * get(&self.p, "pop_ad") / 100 + max * get(&self.p, "pop_hp") / 100;
                sim.deal_damage_typed(me, target, d, DamageTypeV1::Fixed, AttackTypeV1::BaseAttack);
                view(sim, me, target, "league_kaisa_p_burst", true);
                self.pops += 1;
                if self.pops <= 80 {
                    wlog(format!("{} KAISA POP #{} on #{target}: {d} true", head(sim, me), self.pops));
                }
            } else {
                view(sim, me, target, &format!("league_kaisa_pl_{after}"), false);
            }
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (marks read on the target: Diana, Kennen, Kai'Sa) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:diana"), Diana::default());
    module.add_native_passive(format!("{ID}:kennen"), Kennen::default());
    module.add_native_passive(format!("{ID}:kaisa"), Kaisa::default());
    host.log(LogLevel::Info, "league_marks v1 loaded (marks read on the target).");
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
    fn kennen_stuns_on_the_third_mark_of_one_target() {
        assert_eq!(kennen_mark(0), (1, false));
        assert_eq!(kennen_mark(1), (2, false));
        assert_eq!(kennen_mark(2), (0, true));
        let mut s = Vec::new();
        set(&mut s, 7, 2, 100);
        set(&mut s, 8, 1, 100);
        assert_eq!(count(&s, 7, 200, KENNEN_LIFE), 2);
        assert_eq!(count(&s, 8, 100 + KENNEN_LIFE + 1, KENNEN_LIFE), 0);
    }

    #[test]
    fn kaisa_pops_on_the_fifth() {
        assert_eq!(kaisa_hit(0, 1, true), (1, Some(0), false));
        assert_eq!(kaisa_hit(4, 1, true), (0, Some(4), true));
        assert_eq!(kaisa_hit(2, 3, false), (0, None, true));
        assert_eq!(kaisa_hit(1, 2, false), (3, None, false));
    }

    #[test]
    fn the_names_fit() {
        for n in [DIANA_MOON, DIANA_ASK, DIANA_YES, KENNEN_HIT, KAISA_ATTACK, KAISA_CC, KAISA_W2, KAISA_W3] {
            assert!(n.len() <= BUFF_NAME_CAP);
        }
    }
}
