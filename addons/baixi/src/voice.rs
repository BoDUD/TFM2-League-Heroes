//! 百戏五位英雄共用的配音与倒地声调度（照女武神规范：任意两句至少隔 8 秒）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

pub const SECOND: usize = 60;
pub const VOICE_GAP: usize = 8 * SECOND;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    Start,
    Ult,
    Kill,
    Respawn,
    Dead,
}

impl Cue {
    pub fn clip(self) -> &'static str {
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
            Cue::Respawn => 55 * SECOND,
            Cue::Dead => 25 * SECOND,
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct VoiceBook {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    started: bool,
}

impl VoiceBook {
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        if cue == Cue::Start && self.started {
            return None;
        }
        if self.last_any.is_some_and(|t| tick < t + VOICE_GAP) {
            return None;
        }
        let k = cue.clip();
        if self.last.get(k).is_some_and(|&t| tick < t.saturating_add(cue.cooldown())) {
            return None;
        }
        if cue == Cue::Start {
            self.started = true;
        }
        self.last.insert(k, tick);
        self.last_any = Some(tick);
        Some(k)
    }
}

static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn vlog(id: &str, sim: &StableSim<'_>, msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= 80 || n % 100 == 0 {
        crate::wlog(format!("{id} [t={}] #{n} {msg}", sim.tick()));
    }
}

#[derive(Clone)]
pub struct HeroVoice {
    pub id: &'static str,
    pub me: usize,
    pub was_alive: bool,
    pub lives: usize,
    pub ult_cd: usize,
    pub voice: VoiceBook,
    /// 麦芽：出生时自动挂上头顶糖龙图标（若身上尚无凤/鱼标记）。
    pub init_buff: Option<&'static str>,
    pub skip_if_buffs: &'static [&'static str],
}

impl HeroVoice {
    pub fn new(id: &'static str) -> Self {
        Self {
            id,
            me: 0,
            was_alive: false,
            lives: 0,
            ult_cd: 0,
            voice: VoiceBook::default(),
            init_buff: None,
            skip_if_buffs: &[],
        }
    }

    pub fn with_init_buff(mut self, buff: &'static str, skip_if: &'static [&'static str]) -> Self {
        self.init_buff = Some(buff);
        self.skip_if_buffs = skip_if;
        self
    }

    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(clip) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&format!("{}_{clip}", self.id), me, &InputTargetV1::target(me));
        vlog(self.id, sim, format!("VOICE #{me}: {cue:?} -> {clip}"));
    }

    fn ensure_init_buff(&self, sim: &mut StableSim<'_>, me: usize) {
        let Some(init) = self.init_buff else { return };
        let has_any = sim.get_entity(me).is_some_and(|e| {
            (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| {
                let n = b.name();
                n == init || self.skip_if_buffs.contains(&n)
            })
        });
        if !has_any {
            sim.add_buff(me, &BuffV1::named(init));
        }
    }
}

impl StablePassive for HeroVoice {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.was_alive = false;
        self.me = me;
        self.ensure_init_buff(sim, me);
        vlog(self.id, sim, format!("SPAWN #{me} (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if alive && !self.was_alive {
            self.lives += 1;
            self.ensure_init_buff(sim, me);
            if self.lives > 1 {
                self.say(sim, Cue::Respawn);
            }
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        let r = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.3);
        let r0 = self.ult_cd;
        self.ult_cd = r;
        if r > r0 + 30 {
            self.say(sim, Cue::Ult);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some(t) = sim.get_entity(target) else { return };
        if t.team() != my_team && t.is_champion() {
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
        sim.play_sfx(&format!("{}_dead", self.id), me, &InputTargetV1::target(me));
        self.say(sim, Cue::Dead);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn voice_gap_and_start_once() {
        let mut v = VoiceBook::default();
        assert_eq!(v.pick(Cue::Start, 100), Some("v_start"));
        assert_eq!(v.pick(Cue::Start, 100 + 600 * SECOND), None);
        assert_eq!(v.pick(Cue::Kill, 100 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Kill, 100 + VOICE_GAP), Some("v_kill"));
    }
}
