//! 波塞冬（`ragnarok_poseidon`）数据做不到的部分：被动「神无须依赖」和声音。数据（tools/kit/build_poseidon.py）的
//! `passive` 是这里的 `ragnarok_poseidon:alone`，参数 p_r / p_atk / p_dr 从数据的 params 读；怒涛连刺、暴雨斜刺、
//! 四十昼夜的大洪水全在数据里。
//!
//! 神无须依赖：每隔几拍看一次，身边 p_r 以内没有活着的友方英雄（不算自己）就挂上 `ragnarok_poseidon_p_alone`
//! （攻击力 +p_atk%、受到的伤害降低 p_dr%），有了就去掉。死了 buff 跟着没了，复活后照样重看。
//!
//! 配音（樱井孝宏的原声，Codex 截的九句，用法照 Codex 的 audio/voice_cuts.json）：一局第一次和敌方英雄交手说一句
//! （人类的命运与我无关、休想反抗神明，偶尔是无需同伴）、杀了英雄（扫清拦路者、轻蔑的一句，偶尔是神无须依赖）、
//! 放大洪水时偶尔一句「这才是神」、复活时（准你亲眼看这场战斗、不准错过）。每类有自己的冷却，任意两句之间至少隔一会儿。
//! 倒地：死的时候放三叉戟落地和身子着地（延迟在 sound_info 里，对上死亡动作）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `poseidon`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_poseidon";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// 日志只记前面这些行，之后每一百行记一行
const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 100;
static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn log(sim: &StableSim<'_>, msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= LOG_FIRST || n % LOG_EVERY == 0 {
        crate::wlog(format!("poseidon [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 多远以内有友方英雄就不算一个人
    pub p_r: usize,
    /// 一个人时攻击力加成，百分比
    pub p_atk: usize,
    /// 一个人时受到的伤害降低，百分比
    pub p_dr: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_r: 70000,
            p_atk: 15,
            p_dr: 10,
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
            "p_r" => p.p_r = u.min(1_000_000),
            "p_atk" => p.p_atk = u.min(500),
            "p_dr" => p.p_dr = u.min(90),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// 多久看一次身边（拍）
pub const CHECK_EVERY: usize = 6;

/// 身边 r 以内有没有队友：mates 是活着的友方英雄（不含自己）的位置。
pub fn alone(me: (f64, f64), mates: &[(f64, f64)], r: usize) -> bool {
    let r = r as f64;
    !mates.iter().any(|m| (m.0 - me.0).powi(2) + (m.1 - me.1).powi(2) <= r * r)
}

/// 一个人时挂的 buff，永久，靠代码去掉。
pub fn alone_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::named(&vo("p_alone"));
    b.attack_mult = p.p_atk as i32;
    b.damaged_reduce = p.p_dr;
    b
}

/// 配音：事件。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 杀了敌方英雄
    Kill,
    /// 放了大洪水（蓄势那一下）
    Ult,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        // 五份里一份是无需同伴（Codex 标的 intro_rare）
        Cue::Start => &["v_indifferent", "v_no_defiance", "v_indifferent", "v_no_defiance", "v_alone"],
        // 三份里一份是神无须依赖（taunt_rare）
        Cue::Kill => &["v_no_mercy", "v_in_my_way", "v_divine_independence"],
        Cue::Ult => &["v_a_true_god"],
        Cue::Respawn => &["v_watch_me", "v_dont_miss"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Kill => 25 * SECOND,
        Cue::Ult => 40 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 放大招时喊不喊：冷却到了也只有三成多的时候开口（Codex 标的 flood_windup_rare）
pub const ULT_CHANCE: u64 = 35;

/// 一份模拟里的配音节奏：上一句的拍数、每类上次的拍数、每类轮到第几句。
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
            Cue::Ult => "ult",
            Cue::Respawn => "respawn",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那句一局只说一次，按拍数挑，别的按顺序轮。
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
        let line = if cue == Cue::Start {
            self.started = true;
            lines[tick % lines.len()]
        } else {
            let turn = self.turn.entry(k).or_insert(0);
            *turn += 1;
            lines[(*turn - 1) % lines.len()]
        };
        self.last.insert(k, tick);
        self.last_any = Some(tick);
        Some(line)
    }
}

// ===================== 游戏里 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 活着的友方英雄（不含自己）的位置。
fn mates(sim: &StableSim<'_>, me: usize, team: usize) -> Vec<(f64, f64)> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.id() == me || u.team() != team || !u.is_alive() || !u.is_champion() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((x as f64, y as f64));
    }
    out
}

#[derive(Clone, Default)]
struct Alone {
    me: usize,
    p: Params,
    was_alive: bool,
    lives: usize,
    /// 大招的冷却上一拍是多少，用来认出这一拍刚放了大招
    r_cd: usize,
    voice: Voice,
}

impl Alone {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }

    /// 身边没人就挂上 buff，有人就去掉。
    fn check(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), e.pos())) else { return };
        let here = (at.0 as f64, at.1 as f64);
        let solo = alone(here, &mates(sim, me, team), self.p.p_r);
        let name = vo("p_alone");
        let on = has_buff(sim, me, &name);
        if solo && !on {
            sim.add_buff(me, &alone_buff(&self.p));
            log(sim, format!("ALONE #{me}: on"));
        } else if !solo && on {
            sim.entity_remove_buff(me, &name);
            log(sim, format!("ALONE #{me}: off"));
        }
    }
}

impl StablePassive for Alone {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Poseidon (player {player}, team {team}), {:?}", self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if alive && !self.was_alive {
            self.lives += 1;
            if self.lives > 1 {
                self.say(sim, Cue::Respawn);
            }
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        if sim.tick() % CHECK_EVERY == 0 {
            self.check(sim, me);
        }
        // 大招的冷却从 0 跳上去就是刚放了
        let r_cd = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.3);
        let ult = r_cd > self.r_cd + 30;
        self.r_cd = r_cd;
        if ult && (rng % 100) < ULT_CHANCE {
            self.say(sim, Cue::Ult);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let enemy_champion = sim.get_entity(target).is_some_and(|t| t.team() != my_team && t.is_champion());
        if enemy_champion {
            self.say(sim, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.me = me;
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.say(sim, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.was_alive = false;
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// 波塞冬的被动，注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("poseidon: {ID} v{VERSION} (Poseidon: A God Needs No One, voice lines, the fall) registered"));
    module.add_native_passive(format!("{ID}:alone"), Alone::default());
    host.log(LogLevel::Info, "ragnarok.dll: Poseidon (alone buff, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let p = parse_params(r#"{"p_r": 70000, "p_atk": 15, "p_dr": 10}"#);
        assert_eq!(p, Params::default());
        assert_eq!(parse_params(r#"{"p_atk": 999, "p_dr": 99}"#).p_dr, 90);
    }

    #[test]
    fn alone_when_no_mate_within_reach() {
        assert!(alone((0.0, 0.0), &[], 70000));
        assert!(alone((0.0, 0.0), &[(70001.0, 0.0)], 70000));
        assert!(!alone((0.0, 0.0), &[(70000.0, 0.0)], 70000));
        assert!(!alone((0.0, 0.0), &[(200000.0, 0.0), (30000.0, 40000.0)], 70000));
    }

    #[test]
    fn the_alone_buff() {
        let b = alone_buff(&Params::default());
        assert_eq!(b.attack_mult, 15);
        assert_eq!(b.damaged_reduce, 10);
    }

    #[test]
    fn the_start_line_once_a_match_sometimes_the_rare_one() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_indifferent"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 304), Some("v_alone"));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_no_mercy"));
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_a_true_god"));
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_in_my_way"));
    }

    /// Codex 的九句都用上，每句只在一类里。
    #[test]
    fn every_line_is_one_of_codexs_nine() {
        let nine = ["indifferent", "in_my_way", "no_mercy", "no_defiance", "watch_me", "dont_miss", "divine_independence",
                    "a_true_god", "alone"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Kill, Cue::Ult, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(nine.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut all = nine.to_vec();
        all.sort();
        assert_eq!(used, all);
    }
}
