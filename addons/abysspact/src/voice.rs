//! Shared 5-cue AI voice controller (start / ult / kill / respawn / dead) with an 8s global gap.

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
}

impl Voice {
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        if cue == Cue::Start && self.started {
            return None;
        }
        if let Some(prev) = self.last_any {
            if tick.saturating_sub(prev) < VOICE_GAP {
                return None;
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

    pub fn play(&mut self, sim: &mut StableSim<'_>, hero_id: &str, entity: usize, cue: Cue) {
        let tick = sim.tick();
        if let Some(suf) = self.pick(cue, tick) {
            let name = format!("{hero_id}_{suf}");
            sim.play_sfx(&name, entity, &InputTargetV1::target(entity));
        }
    }

    pub fn on_spawn(&mut self, sim: &mut StableSim<'_>, hero_id: &str, entity: usize) {
        if self.was_dead {
            self.was_dead = false;
            self.play(sim, hero_id, entity, Cue::Respawn);
        }
    }

    pub fn on_dead(&mut self, sim: &mut StableSim<'_>, hero_id: &str, entity: usize) {
        self.was_dead = true;
        self.play(sim, hero_id, entity, Cue::Dead);
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
}
