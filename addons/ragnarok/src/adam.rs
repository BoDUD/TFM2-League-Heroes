//! 亚当（`ragnarok_adam`）数据做不到的部分：只有声音。数据（tools/kit/build_adam.py）的 `passive` 是这里的
//! `ragnarok_adam:voice`，没有参数；神虚视的闪避和记录、模仿反击、超越时间之拳全在数据里。
//!
//! 配音（齐藤壮马的原声，Codex 截的七句，用法照 Codex 的 audio/voice_cuts.json）：一局第一次和敌方英雄交手说一句
//! （与神交手的决意、自报姓名，偶尔是保护孩子那句）、杀了英雄、放超越时间之拳时偶尔喊一句全力出拳、复活时说最早的
//! 人类或大家认得我吗。每类有自己的冷却，任意两句之间至少隔一会儿。
//! 倒地：死的时候放 Codex 的倒地声（延迟在 sound_info 里，对上死亡动作第 6 帧着地）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `adam`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_adam";
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
        crate::wlog(format!("adam [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 杀了敌方英雄
    Kill,
    /// 放了超越时间之拳（蓄势那一下）
    Ult,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        // 五份里一份是保护孩子那句（Codex 标的 intro_rare）
        Cue::Start => &["v_duel_resolve", "v_introduce", "v_duel_resolve", "v_introduce", "v_protect"],
        Cue::Kill => &["v_unfazed"],
        Cue::Ult => &["v_full_force"],
        Cue::Respawn => &["v_first_human", "v_recognized"],
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

/// 放大招时喊不喊：冷却到了也只有三成多的时候开口（Codex 标的 signature_windup_rare）
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

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那句一局只说一次，按拍数挑（同一局的几份模拟挑的一样），
    /// 别的按顺序轮。
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

#[derive(Clone, Default)]
struct AdamVoice {
    me: usize,
    was_alive: bool,
    lives: usize,
    /// 大招的冷却上一拍是多少，用来认出这一拍刚放了大招
    r_cd: usize,
    voice: Voice,
}

impl AdamVoice {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for AdamVoice {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Adam (player {player}, team {team})"));
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

/// 亚当的被动，注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("adam: {ID} v{VERSION} (Adam: voice lines, the fall) registered"));
    module.add_native_passive(format!("{ID}:voice"), AdamVoice::default());
    host.log(LogLevel::Info, "ragnarok.dll: Adam (voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_start_line_once_a_match_sometimes_the_rare_one() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_duel_resolve"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 304), Some("v_protect"));
        let mut x = Voice::default();
        assert_eq!(x.pick(Cue::Start, 301), Some("v_introduce"));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_unfazed"));
        // 刚说完，别的也不说
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_full_force"));
        // 杀人那句有自己的冷却
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_unfazed"));
        // 复活两句轮着说
        let mut r = Voice::default();
        let said: Vec<_> = (0..3).map(|i| r.pick(Cue::Respawn, i * 61 * SECOND)).collect();
        assert_eq!(said, [Some("v_first_human"), Some("v_recognized"), Some("v_first_human")]);
    }

    /// Codex 的七句都用上，每句只在一类里。
    #[test]
    fn every_line_is_one_of_codexs_seven() {
        let seven = ["introduce", "recognized", "first_human", "duel_resolve", "unfazed", "full_force", "protect"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Kill, Cue::Ult, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(seven.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut all = seven.to_vec();
        all.sort();
        assert_eq!(used, all);
    }
}
