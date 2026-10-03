#!/usr/bin/env python3
"""league_aatrox's kit (Aatrox, the Darkin Blade), written out from the numbers below.

    python tools/kit/aatrox_kit.py           # writes league/champion/league_aatrox.data_champion
    python tools/kit/aatrox_kit.py --check   # exit 1 when the file differs from what the numbers give

The kit is generated so the timings can follow the strips once Codex has drawn them: every tick below that waits on a
frame (the swing's hit, Q's slam, W's throw) is a placeholder until then (porting-heroes "Rerun it once the art has
set the timings"), and so are the numbers until the SDK simulation has run (champion-data section 9).

  attack + passive  Deathbringer Stance: when none of the four cooldown stages p_1..p_4 (3, 6, 9, 12 s) runs, the
                    attack plays `attack_p` and hits for 40 + 100% AD; a champion-only twin adds 7% of the target's
                    maximum health (League caps it on monsters) and heals him; every target heals him a little. A
                    sweet-spot Q or a W chain on a champion cuts the longest stage left (-3 s, once a cast; Vi's
                    Blast Shield stages). Death clears the stages: he spawns with it ready, as in League.
  skill (Q)         The Darkin Blade, a Direction cast (aim locked at the cast, dodgeable), three charges
                    (`cooltime_use_count`, a charge back every 5 s) counted by the casts like league_riven Q: Q1 a long
                    blade line, Q2 a wider shorter one, Q3 a circle ahead. Each slam spawns at tick Q_SPAWN and lands
                    on the strip's slam tick; the sweet spot is a smaller circle where the blade's tip falls (a hidden
                    LinearProjectile carries it to the tip: in a Direction cast a Forward area falls back to the
                    caster) - bonus damage and a knock-up. Champion-only twins of each area heal him (Umbral Dash's
                    passive) and the sweet one cuts the passive.
                    Umbral Dash (E) is folded in on its own 8 s cooldown: when an enemy champion hugs him as he
                    starts a Q, he hops back first (MoveBack away from that champion), so the tip lands on it -
                    League's E-during-Q.
  skill2 (W)        Infernal Chains, a Direction cast: a chain at an enemy champion in reach (through minions), else
                    along the cast to the first enemy; damage and a 25% slow. Where a champion was chained, the area
                    holds for 1.5 s (a picture on the point); then a 1-tick circle on EnemyChampion pulls whoever is
                    still in it to the centre (Pull in a projectile's effects heads for the projectile) and hits again.
  ult (R)           World Ender, armed on the way and started at the fight (league_riven R): the 3-tick slot arms it
                    for 10 s and transforms him at once when an enemy champion is within R_START, else at his first
                    attack with one that close; unused, the cooldown is refunded. The form: +25% attack damage, +40%
                    move speed for 2 s and +20% for the rest of its 10 s, every heal of the kit half again as big,
                    and the minions and monsters around him feared for 3 s (the champions get a 2-tick cc_immune
                    first, league_briar R's way). The wings and the red aura are a 1 s picture that an AddCasted on
                    himself plays every second: it stops when he dies, where a buff's picture would stay on the body.
"""
import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_aatrox.data_champion")

ID = "league_aatrox"
FX = f"asset/league/effects/{ID}_fx"            # the effect sheet (art step 3)


def n(s):
    return f"{ID}_{s}"


# ---------------------------------------------------------------- numbers (ticks: 60 a second; distances: game units)
STAT = {"attack": 90, "magic_power": 0, "hp": 1050, "defence": 32, "magic_resistance": 25, "move_speed": 1020,
        "hp_regen": 0, "stack": 0, "crit_chance": 0}
GROWTH = {"attack": 18, "magic_power": 0, "hp": 105, "defence": 8, "magic_resistance": 4, "move_speed": 10,
          "hp_regen": 0, "stack": 0, "crit_chance": 0}

ATTACK_RANGE, ATTACK_CD, ATTACK_DUR = 25000, 66, 26
ATTACK_HIT = 12                                  # the swing lands (both strips) - placeholder
P_STAGE = 180                                    # four stages: 3, 6, 9, 12 s
P_DMG = 40                                       # the empowered hit: 40 + 100% AD
P_HP = 7                                         # + 7% of a champion's maximum health
P_HEAL = (15, 10)                                # every target: 15 + 10% AD
P_HEAL_CHAMP = (30, 40)                          # a champion: another 30 + 40% AD

Q_RANGE, Q_CD, Q_CHARGES, Q_DUR, Q_WINDOW = 30000, 900, 3, 30, 240
Q_SPAWN = 6                                      # the areas appear after the hop
Q_ANIM = {1: 28, 2: 28, 3: 32}                   # q1 / q2 / q3 strips - placeholders
Q_SLAM = {1: 16, 2: 16, 3: 20}                   # the frame the blade lands - placeholders
Q = {
    1: {"width": 2000, "length": 56000, "tip": 46000, "sweet": 4000, "dmg": (25, 50), "bonus": (15, 35)},
    2: {"width": 9000, "length": 44000, "tip": 40000, "sweet": 6000, "dmg": (30, 60), "bonus": (20, 40)},
    3: {"mid": 20000, "radius": 14000, "tip": 36000, "sweet": 6000, "dmg": (35, 70), "bonus": (25, 45)},
}
KNOCKUP = 30
Q_HEAL = (8, 12)                                 # per champion the blade hits
SWEET_HEAL = (6, 8)                              # per champion on the sweet spot, on top
E_CD, E_REACH, E_SPEED, E_TICKS = 480, 12000, 3000, 5    # Umbral Dash: a 15000 hop

W_RANGE, W_CD, W_DUR, W_THROW = 60000, 840, 24, 8
W_SPEED, W_LEN, W_WIDTH = 5000, 75000, 6000
W_DMG = (30, 40)                                 # the chain, and the pull again
W_SLOW, W_SLOW_TICKS = -25, 90
W_HOLD, W_ZONE = 90, 12000                       # 1.5 s, then the pull circle (+ the body's radius)
W_PULL = (2500, 6)                               # 15000 toward the centre
W_HEAL = (6, 8)

R_CD, R_RANGE, R_START, R_ARMED = 3000, 45000, 35000, 600
R_TIME, R_ATTACK, R_MS_FAST, R_MS_FAST_TICKS, R_MS = 600, 25, 40, 120, 20
R_HEAL_MULT = 1.5
R_FEAR_RADIUS, R_FEAR = 40000, 180
ULT_ANIM = 36                                    # the transformation strip - placeholder


# ---------------------------------------------------------------- effect builders
def nothing():
    return {"type": "Combine", "effects": []}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def switch(buff, yes, no):
    return {"type": "SwitchByBuff", "buff_name": buff, "effect_buff": yes, "effect_none": no}


def state(name, tick, **stats):
    return {"name": name, "duration": {"Time": {"tick": tick}}, **stats}


def add_caster(name, tick, **stats):
    return {"type": "AddCasterBuff", "buff_state": state(name, tick, **stats), "only_to_enemy": False}


def add_buff(name, tick, **stats):
    return {"type": "AddBuff", "buff_state": state(name, tick, **stats)}


def remove(name):
    return {"type": "RemoveCasterBuff", "name": name}


def attack(damage, ratio, target_hp=0):
    return {"type": "Attack", "damage": damage, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def r_heal(amount, ratio):
    """A heal of the kit: half again as big while World Ender lasts."""
    return switch(n("r"), heal(round(amount * R_HEAL_MULT), round(ratio * R_HEAL_MULT)), heal(amount, ratio))


def view(name):
    return {"type": "ViewEffect", "name": name}


def caster_view(name):
    return {"type": "CasterViewEffect", "name": name}


def sfx(name):
    return {"type": "Sfx", "name": name}


def target_sfx(name):
    return {"type": "TargetSfx", "name": name}


def animation(tag, tick):
    return {"type": "CasterAnimation", "name": tag, "tick": tick}


def applied(*effects):
    return [{"casting_type": "Targeting", "effect": e} for e in effects]


def circle(radius):
    return {"Circle": {"radius": radius}}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def self_only(*effects):
    return around(1000, "AllyOnlySelf", *effects)


def random_target(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


# ---------------------------------------------------------------- Deathbringer Stance
STAGES = [n(f"p_{i}") for i in range(1, 5)]


def when_ready(yes, no=None):
    """`yes` when no cooldown stage runs, else `no`."""
    node = yes
    for s in reversed(STAGES):
        node = switch(s, copy.deepcopy(no) if no else nothing(), node)
    return node


def start_stages():
    return combine(*[add_caster(s, P_STAGE * (i + 1)) for i, s in enumerate(STAGES)])


def cut_stage():
    """Take the longest stage left away: 3 s off the passive's cooldown."""
    node = nothing()
    for s in STAGES:
        node = switch(s, remove(s), node)
    return node


def cut_once(lock):
    """One cut a cast, however many champions it hits in the tick."""
    return switch(lock, nothing(), combine(add_caster(lock, 3), cut_stage()))


def passive_hit():
    return combine(
        remove(n("p_hit")),
        attack(P_DMG, 100),
        r_heal(*P_HEAL),
        {"type": "TargetProjectile", "name": n("p_twin"), "speed": 30000, "y_offset": 0,
         "applied_target": "EnemyChampion", "applied_effects": applied(attack(0, 0, P_HP), r_heal(*P_HEAL_CHAMP))},
        view(n("p_hit")),
        target_sfx(n("p_hit")),
        start_stages(),
    )


def normal_hit():
    return combine(attack(0, 100), view(n("hit")), target_sfx(n("attack_hit")))


# ---------------------------------------------------------------- World Ender
def r_start():
    return combine(
        remove(n("r_armed")),
        animation("ult", ULT_ANIM),
        sfx(n("r_cast")),
        caster_view(n("r_burst")),
        around(R_FEAR_RADIUS, "EnemyChampion", add_buff(n("r_brave"), 2, cc_immune=True)),
        around(R_FEAR_RADIUS, "EnemyWithoutTower", {"type": "Fear", "tick": R_FEAR}, view(n("r_fear"))),
        remove(n("r")), add_caster(n("r"), R_TIME, attack_mult=R_ATTACK),
        remove(n("r_ms1")), add_caster(n("r_ms1"), R_MS_FAST_TICKS, move_speed_mult=R_MS_FAST),
        remove(n("r_ms2")), add_caster(n("r_ms2"), R_TIME, move_speed_mult=R_MS),
        self_only({"type": "AddCasted", "casted_type": "Heal", "duration": R_TIME, "period": 60,
                   "effects": [caster_view(n("r_wings"))]}),
    )


# ---------------------------------------------------------------- The Darkin Blade
def tip(k):
    """A hidden flight to where the blade's tip falls; the sweet spot starts there."""
    p = Q[k]
    land = Q_SPAWN + 2                            # the flight takes two ticks
    apply = Q_SLAM[k] - land + 1                  # hits apply - 1 ticks after it appears: on the slam
    sweet = applied(attack(*p["bonus"]), {"type": "Airborne", "duration": KNOCKUP}, view(n("q_sweet_hit")),
                    target_sfx(n("q_sweet")))
    return {"type": "LinearProjectile", "name": n(f"q{k}_tip"), "speed": p["tip"] // 2, "range": p["tip"],
            "shape": circle(1), "penetrate": True, "y_offset": 5000, "applied_target": "Ally", "applied_effects": [],
            "end_effects": [
                {"type": "RangeProjectile", "name": n(f"q{k}_sweet"), "delay": apply + 12, "apply": apply,
                 "shape": circle(p["sweet"]), "applied_target": "EnemyWithoutTower", "applied_effects": sweet},
                {"type": "RangeProjectile", "name": n(f"q{k}_sweet_c"), "delay": apply, "apply": apply,
                 "shape": circle(p["sweet"]), "applied_target": "EnemyChampion",
                 "applied_effects": applied(r_heal(*SWEET_HEAL), cut_once(n("q_lock")))}]}


def blade(k):
    p = Q[k]
    if k < 3:
        apply = Q_SLAM[k] - Q_SPAWN + 1
        line = {"type": "LineRangeProjectile", "width": p["width"], "length": p["length"], "delay": apply + 10,
                "apply": apply}
        return [dict(line, name=n(f"q{k}_blade"), applied_target="EnemyWithoutTower",
                     applied_effects=applied(attack(*p["dmg"]), view(n("q_hit")))),
                dict(line, name=n(f"q{k}_heal"), delay=apply, applied_target="EnemyChampion",
                     applied_effects=applied(r_heal(*Q_HEAL))),
                tip(k)]
    land = Q_SPAWN + 1
    apply = Q_SLAM[k] - land + 1
    zone = {"type": "RangeProjectile", "delay": apply + 10, "apply": apply, "shape": circle(p["radius"])}
    mid = {"type": "LinearProjectile", "name": n("q3_mid"), "speed": p["mid"], "range": p["mid"], "shape": circle(1),
           "penetrate": True, "y_offset": 5000, "applied_target": "Ally", "applied_effects": [],
           "end_effects": [dict(zone, name=n("q3_slam"), applied_target="EnemyWithoutTower",
                                applied_effects=applied(attack(*p["dmg"]), view(n("q_hit")))),
                           dict(zone, name=n("q3_heal"), delay=apply, applied_target="EnemyChampion",
                                applied_effects=applied(r_heal(*Q_HEAL)))]}
    return [mid, tip(k)]


def q_cast(k):
    return [sfx(n(f"q{k}")), delayed(Q_SPAWN - 1, *blade(k)), delayed(Q_SLAM[k] - 1, sfx(n("q_slam")))]


def umbral_dash():
    return switch(n("e_cd"), nothing(), random_target(
        E_REACH, "EnemyChampion",
        add_caster(n("e_cd"), E_CD), caster_view(n("e_dash")), sfx(n("e")),
        {"type": "MoveBack", "speed": E_SPEED, "tick": E_TICKS}))


# ---------------------------------------------------------------- Infernal Chains
def chain(at_champion):
    hit = [attack(*W_DMG), add_buff(n("w_slow"), W_SLOW_TICKS, move_speed_mult=W_SLOW), view(n("w_hit")),
           target_sfx(n("w_hit"))]
    end = [view(n("w_zone"))]
    if at_champion:
        hit += [add_caster(n("w_hit"), W_HOLD + 10), r_heal(*W_HEAL), cut_once(n("w_lock"))]
        pull = {"type": "RangeProjectile", "name": n("w_pull"), "delay": 2, "apply": 1, "shape": circle(W_ZONE),
                "applied_target": "EnemyChampion",
                "applied_effects": applied({"type": "Pull", "speed": W_PULL[0], "tick": W_PULL[1]}, attack(*W_DMG),
                                           r_heal(*W_HEAL), target_sfx(n("w_pull")))}
        end.append(delayed(W_HOLD, switch(n("w_hit"), combine(remove(n("w_hit")), pull), nothing())))
    return {"type": "LinearProjectile", "name": n("w_chain"), "speed": W_SPEED, "range": W_LEN,
            "shape": circle(W_WIDTH), "penetrate": False, "y_offset": -3000,
            "applied_target": "EnemyChampion" if at_champion else "EnemyWithoutTower",
            "applied_effects": applied(*hit), "end_effects": end}


# ---------------------------------------------------------------- the actions
def action(tag, slot, duration, cooltime, rng, casting_type, target, attack_type, effect, **extra):
    a = {"action_name": tag, "description": f"#asset/base/text/champion?description.{ID}.{slot}",
         "duration": duration, "cooltime": cooltime, "start_timing": 1, "cancelable": slot == "attack",
         "range": rng, "casting_type": casting_type, "casting_target": target, "attack_type": attack_type}
    a.update(extra)
    a["effect"] = effect
    return a


def kit():
    basic = combine(
        when_ready(combine(animation("attack_p", ATTACK_DUR), add_caster(n("p_hit"), ATTACK_HIT + 2))),
        delayed(ATTACK_HIT - 1,
                switch(n("p_hit"), passive_hit(), normal_hit()),
                switch(n("r_armed"), random_target(R_START, "EnemyChampion", r_start()), nothing())))

    q = combine(
        switch(n("q_2"),
               combine(remove(n("q_2")), animation("q3", Q_ANIM[3]), *q_cast(3)),
               switch(n("q_1"),
                      combine(remove(n("q_1")), add_caster(n("q_2"), Q_WINDOW), animation("q2", Q_ANIM[2]), *q_cast(2)),
                      combine(add_caster(n("q_1"), Q_WINDOW), animation("q1", Q_ANIM[1]), *q_cast(1)))),
        umbral_dash())

    w = combine(
        sfx(n("w_cast")),
        remove(n("w_aimed")),
        delayed(W_THROW - 1,
                random_target(W_RANGE, "EnemyChampion", add_caster(n("w_aimed"), 2), chain(True)),
                switch(n("w_aimed"), nothing(), chain(False))))

    r = combine(
        add_caster(n("r_armed"), R_ARMED),
        random_target(R_START, "EnemyChampion", r_start()),
        delayed(R_ARMED, switch(n("r_armed"),
                                combine(remove(n("r_armed")), add_caster(n("r_refund"), 3, ult_cooldown_mult=4900)),
                                nothing())))

    def fx(name, tag, z, follow, kind="Animation"):
        return {"type": kind, "name": n(name), "anim": FX, "tag": tag, "z": z, "is_follow": follow}

    def proj(name, tag, z, repeat=False):
        return {"type": "Animated", "name": n(name), "anim": FX, "tag": tag, "repeat": repeat, "z": z}

    return {
        "id": ID,
        "category": "Melee",
        "tags": ["AD", "Melee", "CC", "Heal"],
        "sprite": f"asset/league/champions/{ID}",
        "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2",
                        f"asset/league/icons/{ID}_ult"],
        "stat": STAT,
        "growth": GROWTH,
        "attack": action("attack", "attack", ATTACK_DUR, ATTACK_CD, ATTACK_RANGE, "Targeting", "Enemy", "BaseAttack",
                         basic),
        "skill": action("q1", "skill", Q_DUR, Q_CD, Q_RANGE, "Direction", "EnemyWithoutTower", "Skill", q,
                        cooltime_use_count=Q_CHARGES),
        "skill2": action("w", "skill2", W_DUR, W_CD, W_RANGE, "Direction", "EnemyWithoutTower", "Skill", w),
        "ult": action("idle", "ult", 3, R_CD, R_RANGE, "None", "EnemyChampion", "Skill", r),
        "view_projectiles": [
            proj("q1_blade", "q1_blade", -1), proj("q2_blade", "q2_blade", -1), proj("q3_slam", "q3_slam", -1),
            proj("q1_sweet", "q_sweet", 1), proj("q2_sweet", "q_sweet", 1), proj("q3_sweet", "q_sweet", 1),
            proj("w_chain", "w_chain", 1, repeat=True), proj("w_pull", "w_pull", -1),
        ],
        "view_effects": [
            fx("hit", "hit", 1, True), fx("p_hit", "p_hit", 2, True),
            fx("q_hit", "q_hit", 1, True), fx("q_sweet_hit", "q_sweet_hit", 2, True),
            fx("e_dash", "e_dash", -1, False),
            fx("w_hit", "w_hit", 2, True), fx("w_zone", "w_zone", -2, False),
            fx("r_burst", "r_burst", 2, True), fx("r_wings", "r_wings", -1, True), fx("r_fear", "r_fear", 3, True),
        ],
        "view_buffs": [],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = json.dumps(kit(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        same = os.path.exists(KIT) and open(KIT, encoding="utf-8").read() == text
        print(f"{KIT}: {'up to date' if same else 'differs from the numbers'}")
        sys.exit(0 if same else 1)
    with open(KIT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"wrote {KIT}")


if __name__ == "__main__":
    main()
