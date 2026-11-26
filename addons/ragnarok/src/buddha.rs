//! 释迦（`ragnarok_buddha`）数据做不到的部分：只有声音。数据（tools/kit/build_buddha.py）的 `passive` 是这里的
//! `ragnarok_buddha:voice`，没有参数；未来视（被动）、枪刃、观音盾、大圆寂刀·零全在数据里。
//!
//! 配音（中村悠一的官方原声，Codex 截的五句，宣传片结尾那句只给试听、不用）：一局第一次和敌方英雄交手说一句（「这也得我来吗」，
//! 五次里一次是长的「神意和诸神黄昏都无所谓」）、杀了英雄（都无所谓）、放大圆寂刀时一半的时候「天上天下唯我独尊」、复活时
//! （能让我行动的只有我自己）。每类有自己的冷却，任意两句之间至少隔一会儿。倒地：死的时候放 Codex 的着地声（延迟在 sound_info
//! 里，对上死亡动作第 8 帧着地）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `buddha`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_buddha";
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
        crate::wlog(format!("buddha [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 杀了敌方英雄
    Kill,
    /// 放了大圆寂刀·零
    Ult,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        // 五份里一份是长的「神意和诸神黄昏都无所谓」
        Cue::Start => &["v_question", "v_question", "v_indifferent", "v_question", "v_question"],
        Cue::Kill => &["v_brief"],
        Cue::Ult => &["v_resolve_short"],
        Cue::Respawn => &["v_resolve"],
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

/// 放大招时喊不喊：冷却到了也只有一半的时候开口
pub const ULT_CHANCE: u64 = 50;

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
struct BuddhaVoice {
    me: usize,
    was_alive: bool,
    lives: usize,
    /// 大招的冷却上一拍是多少，用来认出这一拍刚放了大招
    r_cd: usize,
    voice: Voice,
}

impl BuddhaVoice {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for BuddhaVoice {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Buddha (player {player}, team {team})"));
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

/// 释迦的被动（只有声音），注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("buddha: {ID} v{VERSION} (Buddha: voice lines, the fall) registered"));
    module.add_native_passive(format!("{ID}:voice"), BuddhaVoice::default());
    host.log(LogLevel::Info, "ragnarok.dll: Buddha (voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_start_line_once_a_match_sometimes_the_long_one() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_question"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 302), Some("v_indifferent"));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_brief"));
        // 刚说完，别的也不说
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_resolve_short"));
        // 杀人那句有自己的冷却
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_brief"));
        // 复活一句，冷却到了就说
        let mut r = Voice::default();
        let said: Vec<_> = (0..3).map(|i| r.pick(Cue::Respawn, i * 61 * SECOND)).collect();
        assert_eq!(said, [Some("v_resolve"), Some("v_resolve"), Some("v_resolve")]);
    }

    /// Codex 能用的五句都用上，每句只在一类里。
    #[test]
    fn every_line_is_one_of_codexs_five() {
        let five = ["question", "indifferent", "brief", "resolve", "resolve_short"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Kill, Cue::Ult, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(five.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut all = five.to_vec();
        all.sort();
        assert_eq!(used, all);
    }
}
