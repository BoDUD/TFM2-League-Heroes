//! Shared 5-cue AI voice controller (start / ult / kill / respawn / dead) with an 8s global gap.
//!
//! 被动的 on_dead 只给玩家编号，不给单位：阵亡那句要用英雄自己的单位放（以前 20 个英雄都把玩家编号当单位传进来，
//! 声音落在不相干的单位上或者根本不响）。这里在出生、每次说话（和愿意调 [`Voice::observe`] 的英雄每 tick）时记下单位，
//! 阵亡时用记下的那个，各英雄的文件不用改。

use std::collections::HashMap;
use mod_api_stable::*;

pub const SECOND: usize = 60;
pub const VOICE_GAP: usize = 8 * SECOND;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Cue {
    Start,
    Ult,
    Kill,
    Respawn,
    Dead,
}

impl Cue {
    pub fn suffix(self) -> &'static str {
        match self {
            Cue::Start => "v_start",
            Cue::Ult => "v_ult",
            Cue::Kill => "v_kill",
            Cue::Respawn => "v_respawn",
            Cue::Dead => "v_dead",
        }
    }

    pub fn cooldown(self) -> usize {
        match self {
            Cue::Start => usize::MAX,
            Cue::Ult => 35 * SECOND,
            Cue::Kill => 22 * SECOND,
            Cue::Respawn => 45 * SECOND,
            Cue::Dead => 30 * SECOND,
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<Cue, usize>,
    started: bool,
    was_dead: bool,
    /// 英雄自己的单位（出生、说话、observe 时记下）：阵亡那句在它身上放。
    me: Option<usize>,
}

impl Voice {
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        if cue == Cue::Start && self.started {
            return None;
        }
        // 倒地那句不让别的台词压掉：每条命都该有一句，只看它自己的冷却
        if cue != Cue::Dead {
            if let Some(prev) = self.last_any {
                if tick.saturating_sub(prev) < VOICE_GAP {
                    return None;
                }
            }
        }
        if let Some(&prev) = self.last.get(&cue) {
            if tick.saturating_sub(prev) < cue.cooldown() {
                return None;
            }
        }
        if cue == Cue::Start {
            self.started = true;
        }
        self.last_any = Some(tick);
        self.last.insert(cue, tick);
        Some(cue.suffix())
    }

    /// 记下英雄这条命的单位（复活后是新的单位号）。
    pub fn observe(&mut self, entity: usize) {
        self.me = Some(entity);
    }

    /// 阵亡那句该在哪个单位上放。
    pub fn speaker(&self) -> Option<usize> {
        self.me
    }

    pub fn play(&mut self, sim: &mut StableSim<'_>, hero_id: &str, entity: usize, cue: Cue) {
        self.me = Some(entity);
        let tick = sim.tick();
        if let Some(suf) = self.pick(cue, tick) {
            let name = format!("{hero_id}_{suf}");
            sim.play_sfx(&name, entity, &InputTargetV1::target(entity));
        }
    }

    pub fn on_spawn(&mut self, sim: &mut StableSim<'_>, hero_id: &str, entity: usize) {
        self.me = Some(entity);
        if self.was_dead {
            self.was_dead = false;
            self.play(sim, hero_id, entity, Cue::Respawn);
        }
    }

    /// `_player` 是被动 on_dead 给的玩家编号（不是单位，留着参数只为各英雄的调用不用改）：声音放在记下的单位上。
    /// 游戏在 on_dead 之后才把他登记成阵亡，这时他的单位还在。
    pub fn on_dead(&mut self, sim: &mut StableSim<'_>, hero_id: &str, _player: usize) {
        self.was_dead = true;
        let Some(me) = self.me else { return };
        if let Some(suf) = self.pick(Cue::Dead, sim.tick()) {
            let name = format!("{hero_id}_{suf}");
            sim.play_sfx(&name, me, &InputTargetV1::target(me));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn start_once_and_gap_enforced() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 100), Some("v_start"));
        assert_eq!(v.pick(Cue::Start, 10000), None);
        assert_eq!(v.pick(Cue::Kill, 100 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Kill, 100 + VOICE_GAP), Some("v_kill"));
    }

    #[test]
    fn the_death_line_is_not_held_back_by_a_line_just_said() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_kill"));
        assert_eq!(v.pick(Cue::Dead, 1001), Some("v_dead"));
        // 它自己的冷却还在
        assert_eq!(v.pick(Cue::Dead, 1002 + VOICE_GAP), None);
    }

    #[test]
    fn the_death_line_goes_to_the_hero_not_the_player_number() {
        let mut v = Voice::default();
        assert_eq!(v.speaker(), None);
        v.observe(1020);
        assert_eq!(v.speaker(), Some(1020));
        // 复活是新的单位
        v.observe(1544);
        assert_eq!(v.speaker(), Some(1544));
    }
}
