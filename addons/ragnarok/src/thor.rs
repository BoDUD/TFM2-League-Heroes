//! 索尔（`ragnarok_thor`）数据做不到的部分：只有声音。数据（tools/kit/build_thor.py）的 `passive` 是这里的
//! `ragnarok_thor:voice`，没有参数；雷槌觉醒、投锤回锤、护盾、大招这些规则全在数据里。
//!
//! 配音（绿川光的原声，Codex 截的十句，事件按 Codex 的 audio_events.json 分）：一局第一次和敌方英雄交手说一句、杀了英雄、
//! 雷槌觉醒、复活的时候偶尔说一句，每类有自己的冷却，任意两句之间至少隔一会儿，不会每下普攻都喊。觉醒雷槌那句
//! 「一撃のもとに」是数据自己放的：大招一放就当刚说过话，大招带出来的觉醒不再叠一句。
//! 倒地：死的时候放 Codex 的倒地声（延迟在 sound_info 里，对上死亡动作躺下的那一帧）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `thor`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_thor";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// 日志只记前面这些行，之后每一百行记一行，免得一晚上的比赛把日志写满
const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 100;
static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn log(sim: &StableSim<'_>, msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= LOG_FIRST || n % LOG_EVERY == 0 {
        crate::wlog(format!("thor [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 杀了敌方英雄
    Kill,
    /// 雷槌觉醒（第三次放技能那下，不算大招带出来的）
    Awake,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        Cue::Start => &["v_worthy", "v_wake", "v_address"],
        Cue::Kill => &["v_smash_call", "v_praise"],
        Cue::Awake => &["v_weapon"],
        Cue::Respawn => &["v_anticipation", "v_warning", "v_sleepy"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Kill => 20 * SECOND,
        Cue::Awake => 25 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 觉醒时说不说：冷却到了也只有一半的时候开口（一局觉醒二十几次）
pub const AWAKE_CHANCE: u64 = 50;

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
            Cue::Awake => "awake",
            Cue::Respawn => "respawn",
        }
    }

    /// 数据自己放了一句（大招那句）：当成刚说过，别的先别接。
    pub fn hold(&mut self, tick: usize) {
        self.last_any = Some(tick);
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那句一局只说一次，三句里按拍数挑一句（同一局的几份
    /// 模拟挑的一样）；别的按顺序轮。
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

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

#[derive(Clone, Default)]
struct ThorVoice {
    me: usize,
    was_alive: bool,
    lives: usize,
    /// 上一拍雷槌醒着没有（数据的 `ragnarok_thor_awake`）
    was_awake: bool,
    /// 大招的冷却上一拍是多少，用来认出这一拍刚放了大招
    r_cd: usize,
    voice: Voice,
}

impl ThorVoice {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for ThorVoice {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：这里先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.was_awake = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Thor (player {player}, team {team})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some((alive, awake)) = sim.get_entity(me).map(|e| (e.is_alive(), has_buff(&e, &vo("awake")))) else {
            return;
        };
        if alive && !self.was_alive {
            self.lives += 1;
            if self.lives > 1 {
                self.say(sim, Cue::Respawn);
            }
        }
        self.was_alive = alive;
        if !alive {
            self.was_awake = false;
            return;
        }
        // 大招的冷却从 0 跳上去就是刚放了：数据放了「一撃のもとに」，这一拍的觉醒也是大招带的
        let r_cd = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.3);
        let ult = r_cd > self.r_cd + 30;
        self.r_cd = r_cd;
        if ult {
            self.voice.hold(sim.tick());
        }
        if awake && !self.was_awake && !ult && (rng % 100) < AWAKE_CHANCE {
            self.say(sim, Cue::Awake);
        }
        self.was_awake = awake;
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
        self.was_awake = false;
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// 索尔的被动，注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("thor: {ID} v{VERSION} (Thor: voice lines, the fall) registered"));
    module.add_native_passive(format!("{ID}:voice"), ThorVoice::default());
    host.log(LogLevel::Info, "ragnarok.dll: Thor (voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_start_line_once_a_match_picked_by_the_tick() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 301), Some("v_wake"));
        assert_eq!(v.pick(Cue::Start, 301 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 300), Some("v_worthy"));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_smash_call"));
        // 刚说完，别的也不说
        assert_eq!(v.pick(Cue::Awake, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Awake, 1000 + VOICE_GAP), Some("v_weapon"));
        // 杀人那两句自己的冷却，轮着说
        assert_eq!(v.pick(Cue::Kill, 1000 + 20 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 20 * SECOND), Some("v_praise"));
        assert_eq!(v.pick(Cue::Kill, 1000 + 40 * SECOND), Some("v_smash_call"));
        // 复活三句轮着说
        let mut r = Voice::default();
        let said: Vec<_> = (0..4).map(|i| r.pick(Cue::Respawn, i * 61 * SECOND)).collect();
        assert_eq!(said, [Some("v_anticipation"), Some("v_warning"), Some("v_sleepy"), Some("v_anticipation")]);
    }

    #[test]
    fn the_ults_own_line_holds_the_rest() {
        let mut v = Voice::default();
        v.hold(5000);
        assert_eq!(v.pick(Cue::Awake, 5000), None);
        assert_eq!(v.pick(Cue::Kill, 5000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Kill, 5000 + VOICE_GAP), Some("v_smash_call"));
    }

    /// Codex 的十句：九句这里放，「一撃のもとに」（one_strike）是数据的大招放的。
    #[test]
    fn every_line_is_one_of_codexs_ten() {
        let ten = ["smash_call", "weapon", "one_strike", "worthy", "anticipation", "warning", "wake", "sleepy",
                   "address", "praise"];
        let mut used = vec!["one_strike"];
        for cue in [Cue::Start, Cue::Kill, Cue::Awake, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(ten.contains(&clip), "{line}");
                used.push(clip);
            }
        }
        used.sort();
        let mut all = ten.to_vec();
        all.sort();
        assert_eq!(used, all, "every line used once");
    }
}
