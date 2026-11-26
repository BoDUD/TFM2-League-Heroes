//! 西蒙·海耶（`ragnarok_simo`）数据做不到的部分。数据（tools/kit/build_simo.py）的 `passive` 是这里的 `ragnarok_simo:contract`，参数 p_cost 从数据的 params 读。
//!
//! 配音（Codex 用语音合成做的六句，用户 2026-11-26 说要用）：一局第一次和敌方英雄交手（「静かな森だ」），第一次和洛基交手（「ここは、任せてくれ」）；放对神狙击术（「見つけた」）、雪中隐踪（「雪が降ってきたな」）、天空的残光（「これで、終わりだ」）时说；杀了英雄（「これで、終わりだ」）；复活时（「準備はできている」）。
//! 死神的契约：对神狙击术（Q）和天空的残光（R）打出去的是器官换来的弑神弹，放的那一拍（冷却从 0 跳上去）先扣他p_cost% 最大生命，最多扣到 1 点（不会自己打死自己）。
//! 每类有自己的冷却，任意两句之间至少隔一会儿。倒地：死的时候放 Codex 的倒地声（延迟在 sound_info 里）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `simo`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_simo";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 第十一回合的对手洛基
const RIVAL_ID: &str = "ragnarok_loki";

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
        crate::wlog(format!("simo [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 参数和扣血（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 每发扣最大生命的百分之几
    pub p_cost: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_cost: 3 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        if k == "p_cost" {
            p.p_cost = (v.max(0) as usize).min(50);
        }
    }
    p
}

/// 扣完以后的生命：现在 hp、最多 max，扣 cost% 最大生命，最多扣到 1 点（已经只剩 1 点就不扣）。
pub fn after_cost(hp: usize, max: usize, cost: usize) -> usize {
    if hp <= 1 {
        return hp;
    }
    hp.saturating_sub(max * cost / 100).max(1)
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 一局里第一次和第十一回合的对手洛基交手
    Rival,
    /// 放了 Q
    Q,
    /// 放了 E
    E,
    /// 放了大招
    Ult,
    /// 杀了敌方英雄
    Kill,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        Cue::Start => &["v_start"],
        Cue::Rival => &["v_challenge"],
        Cue::Q => &["v_q"],
        Cue::E => &["v_e"],
        Cue::Ult => &["v_r"],
        Cue::Kill => &["v_r"],
        Cue::Respawn => &["v_select"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Rival => usize::MAX,
        Cue::Q => 20 * SECOND,
        Cue::E => 30 * SECOND,
        Cue::Ult => 40 * SECOND,
        Cue::Kill => 25 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 一份模拟里的配音节奏：上一句的拍数、每类上次的拍数、每类轮到第几句。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    turn: HashMap<&'static str, usize>,
    once: Vec<&'static str>,
}

impl Voice {
    fn key(cue: Cue) -> &'static str {
        match cue {
            Cue::Start => "start",
            Cue::Rival => "rival",
            Cue::Q => "q",
            Cue::E => "e",
            Cue::Ult => "ult",
            Cue::Kill => "kill",
            Cue::Respawn => "respawn",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那几句一局各说一次，别的按顺序轮。
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        let k = Self::key(cue);
        let once = matches!(cue, Cue::Start | Cue::Rival);
        if once && self.once.contains(&k) {
            return None;
        }
        if self.last_any.is_some_and(|t| tick < t + VOICE_GAP) {
            return None;
        }
        if self.last.get(k).is_some_and(|&t| tick < t.saturating_add(cue_cooldown(cue))) {
            return None;
        }
        let lines = lines_of(cue);
        let line = if once {
            self.once.push(k);
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

#[derive(Clone, Default)]
struct SimoPassive {
    me: usize,
    p: Params,
    was_alive: bool,
    lives: usize,
    /// Q、E、大招的冷却上一拍是多少，用来认出这一拍刚放了
    cds: (usize, usize, usize),
    voice: Voice,
}

impl SimoPassive {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }

    /// 死神的契约：这一发是器官换来的，先扣血。
    fn pay(&mut self, sim: &mut StableSim<'_>, what: &str) {
        let me = self.me;
        let Some((hp, max)) = sim.get_entity(me).map(|e| e.hp()) else { return };
        let after = after_cost(hp, max, self.p.p_cost);
        if after < hp && sim.entity_set_hp(me, after) {
            log(sim, format!("COST #{me}: {what} {hp} -> {after} of {max}"));
        }
    }
}

impl StablePassive for SimoPassive {
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
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Simo (player {player}, team {team})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
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
        // 冷却从 0 跳上去就是刚放了
        let (_, q, e, r) = sim.get_player(player).and_then(|p| p.cooldowns()).unwrap_or((0, 0, 0, 0));
        let (q0, e0, r0) = self.cds;
        self.cds = (q, e, r);
        if q > q0 + 30 {
            self.pay(sim, "the skill");
            self.say(sim, Cue::Q);
        }
        if e > e0 + 30 {
            self.say(sim, Cue::E);
        }
        if r > r0 + 30 {
            self.pay(sim, "the ult");
            self.say(sim, Cue::Ult);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some(t) = sim.get_entity(target) else { return };
        if t.team() == my_team || !t.is_champion() {
            return;
        }
        let name = t.name();
        if name.as_deref() == Some(RIVAL_ID) {
            self.say(sim, Cue::Rival);
        } else {
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

/// 西蒙·海耶的被动，注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("simo: {ID} v{VERSION} (Simo: voice lines, organ bullets' cost, the fall) registered"));
    module.add_native_passive(format!("{ID}:contract"), SimoPassive::default());
    host.log(LogLevel::Info, "ragnarok.dll: Simo (voice lines, organ bullets' cost, the fall).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_start_line_once_a_match() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_start"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_r"));
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_r"));
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_r"));
    }

    /// Codex 的每一句都用上。
    #[test]
    fn every_line_is_used() {
        let all = ["select", "start", "challenge", "q", "e", "r"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Rival, Cue::Q, Cue::E, Cue::Ult, Cue::Kill, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(all.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut want = all.to_vec();
        want.sort();
        assert_eq!(used, want);
    }

    #[test]
    fn the_cost_never_kills() {
        assert_eq!(after_cost(1000, 1000, 3), 970);
        assert_eq!(after_cost(20, 1000, 3), 1);
        assert_eq!(after_cost(1, 1000, 3), 1);
        assert_eq!(parse_params(r#"{"p_cost": 3}"#), Params::default());
        assert_eq!(parse_params(r#"{"p_cost": 999}"#).p_cost, 50);
    }
}
