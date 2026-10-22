//! Caitlyn's lane pressure (the user, 2026-10-22: 「女警前期压制力太低」「再想想AI那边的办法」「做附加包之类的也行」).
//! Pure: the classic-SDK simulator and league_caitlyn's AI hook share it.
//!
//! Early on (before LANE_T) the game's AI spends her on minions (11 of her first 15 Qs hit minions in the trace) while
//! the enemy laner stands in her range - League's Caitlyn trades with her range and Piltover Peacemaker. So, only when
//! the AI already chose to attack (never a move, retreat, recall or another cast):
//! - Q ready and an enemy champion within Q_REACH: Q at it (the lowest health first);
//! - attacking a minion that is not a last hit, with an enemy champion within her attack reach: shoot the champion.
//! Never when she or the target stands in an enemy tower's reach, she is under LOW_HP %, or more enemy champions than
//! allied ones (her included) are within FIGHT_R.

pub type Pt = (f64, f64);

pub const LANE_T: usize = 600 * 60; // ticks: the first ten minutes
pub const ATK_REACH: f64 = 65_000.0 + 4_000.0; // her attack range + a little for the radii
pub const STEP: f64 = 20_000.0; // she steps up this much to shoot the laner instead of a minion
pub const Q_REACH: f64 = 100_000.0; // the data's own champion pick for Q (RandomTarget 100000)
pub const TOWER_R: f64 = 80_000.0;
pub const FIGHT_R: f64 = 90_000.0;
pub const LOW_HP: usize = 35;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Champ {
    pub id: usize,
    pub pos: Pt,
    pub hp_pct: usize,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Base {
    /// the AI attacks a champion
    AttackChamp(usize),
    /// the AI attacks something else; `last_hit`: it dies to this shot
    AttackOther { last_hit: bool },
    /// the AI casts Q (anywhere: at minions mostly)
    Q,
    /// a move, a cast, a recall or nothing: left alone
    Other,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Plan {
    Keep,
    Q(usize),
    Attack(usize),
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Why {
    Late,
    NotAttacking,
    Danger,
    Tower,
    QPoke,
    Harass,
    LastHit,
    NoneInReach,
}

pub fn d(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn under(p: Pt, towers: &[Pt]) -> bool {
    towers.iter().any(|t| d(*t, p) <= TOWER_R)
}

/// `foes` / `allies`: living champions (allies without her); `enemy_towers`: standing ones.
#[allow(clippy::too_many_arguments)]
pub fn plan(tick: usize, me: Pt, my_hp_pct: usize, base: Base, foes: &[Champ], allies: &[Champ], enemy_towers: &[Pt],
            q_ready: bool) -> (Plan, Why) {
    if tick >= LANE_T {
        return (Plan::Keep, Why::Late);
    }
    if matches!(base, Base::Other) {
        return (Plan::Keep, Why::NotAttacking);
    }
    let near = |list: &[Champ]| list.iter().filter(|c| d(c.pos, me) <= FIGHT_R).count();
    if my_hp_pct < LOW_HP || near(foes) > near(allies) + 1 {
        return (Plan::Keep, Why::Danger);
    }
    if under(me, enemy_towers) {
        return (Plan::Keep, Why::Tower);
    }
    let mut open: Vec<&Champ> = foes.iter().filter(|c| !under(c.pos, enemy_towers)).collect();
    open.sort_by(|a, b| a.hp_pct.cmp(&b.hp_pct).then(d(a.pos, me).total_cmp(&d(b.pos, me))));
    if q_ready {
        if let Some(c) = open.iter().find(|c| d(c.pos, me) <= Q_REACH) {
            return (Plan::Q(c.id), Why::QPoke);
        }
    }
    match base {
        // the AI's own Q: at a champion in reach rather than the wave
        Base::Q => match open.iter().find(|c| d(c.pos, me) <= Q_REACH) {
            Some(c) => (Plan::Q(c.id), Why::QPoke),
            None => (Plan::Keep, Why::NoneInReach),
        },
        Base::AttackOther { last_hit: true } => (Plan::Keep, Why::LastHit),
        Base::AttackOther { last_hit: false } => match open.iter().find(|c| d(c.pos, me) <= ATK_REACH + STEP) {
            Some(c) => (Plan::Attack(c.id), Why::Harass),
            None => (Plan::Keep, Why::NoneInReach),
        },
        _ => (Plan::Keep, Why::NoneInReach),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn c(id: usize, x: f64, hp: usize) -> Champ {
        Champ { id, pos: (x, 0.0), hp_pct: hp }
    }

    #[test]
    fn rules() {
        let me = (0.0, 0.0);
        let other = Base::AttackOther { last_hit: false };
        assert_eq!(plan(100, me, 90, other, &[c(7, 60_000.0, 80)], &[], &[], false), (Plan::Attack(7), Why::Harass));
        assert_eq!(plan(100, me, 90, other, &[c(7, 95_000.0, 80)], &[], &[], true), (Plan::Q(7), Why::QPoke));
        assert_eq!(plan(100, me, 90, Base::Q, &[c(7, 95_000.0, 80)], &[], &[], false), (Plan::Q(7), Why::QPoke));
        assert_eq!(plan(100, me, 90, other, &[c(7, 85_000.0, 80)], &[], &[], false), (Plan::Attack(7), Why::Harass));
        assert_eq!(plan(100, me, 90, other, &[c(7, 95_000.0, 80)], &[], &[], false).1, Why::NoneInReach);
        assert_eq!(plan(100, me, 90, Base::AttackOther { last_hit: true }, &[c(7, 60_000.0, 80)], &[], &[], false).1, Why::LastHit);
        assert_eq!(plan(100, me, 90, Base::Other, &[c(7, 60_000.0, 80)], &[], &[], true).1, Why::NotAttacking);
        assert_eq!(plan(LANE_T, me, 90, other, &[c(7, 60_000.0, 80)], &[], &[], true).1, Why::Late);
        assert_eq!(plan(100, me, 30, other, &[c(7, 60_000.0, 80)], &[], &[], true).1, Why::Danger);
        // two of them, none with her
        assert_eq!(plan(100, me, 90, other, &[c(7, 60_000.0, 80), c(8, 50_000.0, 80)], &[], &[], true).1, Why::Danger);
        // the target under its tower
        assert_eq!(plan(100, me, 90, other, &[c(7, 60_000.0, 80)], &[], &[(120_000.0, 0.0)], false).1, Why::NoneInReach);
    }
}
