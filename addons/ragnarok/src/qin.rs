//! 秦始皇（`ragnarok_qin`）数据做不到的部分：只有声音。数据（tools/kit/build_qin.py）的 `passive` 是这里的
//! `ragnarok_qin:voice`，没有参数；星（被动）、波流龟气弹、神罗铠袖·承力天凤、始皇勾践剑全在数据里。
//!
//! 配音（石川界人的官方原声，Codex 截的七句）：一局第一次和敌方英雄交手说一句（「头抬得太高了」，五次里一次是长的入场
//! 「朕所至之处」），第一次和哈迪斯交手（对面有他的话）说「冥界之王」那句；放神罗铠袖时一半的时候喊（蚩尤铠式、承力天凤
//! 轮着说）；拔勾践剑时「天下只此一王」；杀了英雄（「你还挺有精神」）；复活时（入场那句）。每类有自己的冷却，任意两句之间
//! 至少隔一会儿。倒地：死的时候放 Codex 的着地声（延迟在 sound_info 里，对上死亡动作第 8 帧着地）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `qin`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_qin";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 宿敌：第七回合的对手
const RIVAL: &str = "ragnarok_hades";

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
        crate::wlog(format!("qin [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 一局里第一次和哈迪斯交手
    Rival,
    /// 放了神罗铠袖
    Guard,
    /// 放了始皇勾践剑
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
        // 五份里一份是长的入场「朕所至之处」
        Cue::Start => &["v_taunt", "v_taunt", "v_entrance", "v_taunt", "v_taunt"],
        Cue::Rival => &["v_hades"],
        Cue::Guard => &["v_armor", "v_counter"],
        Cue::Ult => &["v_one_king"],
        Cue::Kill => &["v_big_one"],
        Cue::Respawn => &["v_entrance"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start | Cue::Rival => usize::MAX,
        Cue::Guard => 30 * SECOND,
        Cue::Ult => 40 * SECOND,
        Cue::Kill => 25 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 放神罗铠袖时喊不喊：冷却到了也只有一半的时候开口
pub const SKILL_CHANCE: u64 = 50;

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
            Cue::Guard => "guard",
            Cue::Ult => "ult",
            Cue::Kill => "kill",
            Cue::Respawn => "respawn",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那两句一局各说一次，开场那句按拍数挑（同一局的几份模拟挑的
    /// 一样），别的按顺序轮。
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
struct QinVoice {
    me: usize,
    was_alive: bool,
    lives: usize,
    /// 神罗铠袖、勾践剑的冷却上一拍是多少，用来认出这一拍刚放了哪个
    cds: (usize, usize),
    voice: Voice,
}

impl QinVoice {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(sim, format!("VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for QinVoice {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(sim, format!("SPAWN #{me}: ragnarok.dll's Qin Shi Huang (player {player}, team {team})"));
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
        // 冷却从 0 跳上去就是刚放了
        let (e, r) = sim.get_player(player).and_then(|p| p.cooldowns()).map_or((0, 0), |c| (c.2, c.3));
        let (e0, r0) = self.cds;
        self.cds = (e, r);
        if r > r0 + 30 {
            self.say(sim, Cue::Ult);
        } else if e > e0 + 30 && (rng % 100) < SKILL_CHANCE {
            self.say(sim, Cue::Guard);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some(t) = sim.get_entity(target) else { return };
        if t.team() == my_team || !t.is_champion() {
            return;
        }
        if t.name().as_deref() == Some(RIVAL) {
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

/// 秦始皇的被动（只有声音），注册进本包的模块（lib.rs 的 init）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("qin: {ID} v{VERSION} (Qin Shi Huang: voice lines, the fall) registered"));
    module.add_native_passive(format!("{ID}:voice"), QinVoice::default());
    host.log(LogLevel::Info, "ragnarok.dll: Qin Shi Huang (voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_start_line_once_a_match_sometimes_the_long_one() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_taunt"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 302), Some("v_entrance"));
    }

    #[test]
    fn the_rival_line_once_a_match_apart_from_the_start_line() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Rival, 300), Some("v_hades"));
        // 和哈迪斯交手过了，第一次打别的英雄还会说开场那句（隔够了就行）
        assert_eq!(v.pick(Cue::Start, 300 + VOICE_GAP), Some("v_taunt"));
        assert_eq!(v.pick(Cue::Rival, 300 + 600 * SECOND), None);
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_big_one"));
        // 刚说完，别的也不说
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_one_king"));
        // 杀人那句有自己的冷却
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_big_one"));
        // 神罗铠袖两句轮着说，各隔 30 秒
        let mut g = Voice::default();
        assert_eq!(g.pick(Cue::Guard, 0), Some("v_armor"));
        assert_eq!(g.pick(Cue::Guard, 30 * SECOND - 1), None);
        assert_eq!(g.pick(Cue::Guard, 30 * SECOND), Some("v_counter"));
        assert_eq!(g.pick(Cue::Guard, 60 * SECOND), Some("v_armor"));
    }

    /// Codex 的七句都用上。
    #[test]
    fn every_line_is_one_of_codexs_seven() {
        let seven = ["taunt", "entrance", "big_one", "armor", "counter", "hades", "one_king"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Rival, Cue::Guard, Cue::Ult, Cue::Kill, Cue::Respawn] {
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
