"""Build league_ryze.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_ryze.py [--set key=value ...] [--out file] [--params json]

Kit (the user's picks, 2026-10-02, all A):
  passive Arcane Mastery: League scales his spells with bonus mana; TFM2 has no mana, so every spell's magic damage adds
          p_hp% of his maximum health (hp_ratio), and he has a battle mage's health growth.
  attack  a rune orb at the target (physical), League's 550 range.
  skill   Q Overload alone: a Direction cast on EnemyWithoutTower (aim fixed at the cast), a bolt that stops on the first
          enemy: magic damage. If Flux is up (any of his Flux marks live), the hit sets off the marks: every enemy
          carrying Flux takes the Flux burst (League: bonus damage and the bounce to the Flux'd ones), and the Flux is
          used up.
  skill2  League's combo E -> W -> Q -> E -> Q in one cast (W and E refresh Q; 2026-10-05, the user: 「没有高爆发的连招
          查查高手怎么玩的」 - high-elo Ryze chains Q between every E and W, Q-E-Q-W-Q-E-Q, so the second E and Q are
          added): a Targeting cast on EnemyWithoutTower.
          E Spell Flux: an orb at the target, magic damage; where it lands Flux goes on the target and the enemies
          round it (wider if Flux was already up: League's spread). W Rune Prison: magic damage, a root while Flux is
          up, else a slow (Flux is not used up here, so the Q after it can burst it). Q Overload: the bolt at the
          target; E and W each charged a rune, so this Q discharges two: move speed for a moment (League's Q passive).
          Then E again (Flux back on the target and round it - wider, as the first Q used it up) and a second Q that
          bursts it.
  ult     R Realm Warp, for League's two uses (the user: chase or escape, and take the minions along; never at an
          enemy already in front of him). The slot arms it as he closes in; while armed, a check every r_poll ticks:
          two enemy champions on him, or one with no ally near -> the portal opens and after r_ch ticks of channel
          (crowd control breaks it) he jumps r_back straight away; an enemy champion his team was fighting has left
          his reach, with an ally standing in his portal and no teamfight round him (fewer than r_crowd enemy
          champions within r_chase) -> a second portal opens where the line toward it comes within r_stop (inside his
          reach, never on top of it), and after the channel he blinks there. 2026-10-05, the user: 「团战开了大往里面
          送」 - the old chase landed 5000 from the first enemy champion on the line, often with nobody along; League's
          players warp to flank or rotate with the team and keep a mage at range, so he now lands at casting range,
          with an ally, and never chases into a teamfight (the escape stays). Either way the allied champions and minions standing in his portal are pulled
          through to him (Grab), and on landing he throws a free Spell Flux at an enemy champion in reach. Left
          unused, the window refunds the cooldown. R's passive: after his first R in a life the Flux burst of Q is
          stronger (League: Overload's bonus against Flux rises with R).
Flux is a mark per unit: two AddCasted on each enemy the E zone reaches (one plays the rune mark picture while the
generation flag holds, one checks every pop_period ticks for the caster flag q_pop and bursts). Three generations
(fx_c from the combo's first E, fx_d from its second, fx_r from R's landing E): a new E switches the other generation off, so a unit never carries
two live marks.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_ryze.data_champion")
ID = "league_ryze"
FX = "asset/league/effects/league_ryze_fx"
BIG = "asset/league/effects/league_ryze_big"

# 2026-10-05 (the user: 「瑞兹大招 逻辑现在团战开了大往里面送 而且没有高爆发的连招」): the combo E-W-Q-E-Q and the
# chase at casting range, with an ally, never into a teamfight. The first try (the old numbers) +5.12 kill difference
# (720 games, the old kit +1.41); Q 55 + 50%, E 45 + 45%, the Flux burst 35 + 35% (50 + 55% after R) and the combo every
# 14 s: +1.63 / +1.61 on seeds 1-24 / 25-48 (the old kit +1.41 / +1.35, league_ahri +1.55 / +1.76, league_annie +1.65 /
# +1.36); his kills 3.1 -> 4.2 a game. R's landings (sim/ryzeland.py, 240 games): an enemy champion within 20000 16% ->
# 8%, two within 45000 17% -> 8%, dead within 3 s 16% -> 14%, chases 2.3 -> 1.8 a game.
P = {
    # stats (Magician base: attack 80 +6, magic power 40 +20, hp 900 +100, defence 20, mr 20, move 900, range 60000,
    # attack cooldown 90); League's Ryze is a battle mage (645 health, 3rd highest base among mages) who builds mana
    # (Rod of Ages, Seraph's): more health and its growth here, the passive turns it into damage
    "hp": 900, "hp_g": 105, "atk": 78, "atk_g": 6, "mp": 35, "mp_g": 20, "def": 22, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 920, "ms_g": 10,
    # attack (League 550 range like Ahri / Lux / Veigar here)
    "atk_range": 55000, "atk_dur": 28, "atk_cd": 90, "atk_st": 9, "orb_speed": 4500, "orb_y": 1500,
    # passive Arcane Mastery: % of his max health added to every spell's magic damage
    "p_hp": 2,
    # skill: Q Overload
    "q_cd": 210, "q_range": 80000, "q_dur": 26, "q_st": 7, "q_speed": 6000, "q_len": 90000, "q_rad": 6000,
    "q_y": 1500, "q_dmg": 55, "q_ap": 50,
    # the Flux burst on every Flux'd enemy when Q hits (before / after his first R in a life)
    "fb_dmg": 35, "fb_ap": 35, "fbr_dmg": 50, "fbr_ap": 55,
    # skill2: E -> W -> Q (ticks from the cast)
    "c_cd": 840, "c_range": 60000, "c_dur": 56, "c_e": 6, "c_w": 16, "c_q": 26, "c_e2": 36, "c_q2": 46, "c_two": 1,
    "e_speed": 4500, "e_dmg": 45, "e_ap": 45, "flux_t": 240, "flux_r": 25000, "flux_r2": 38000,
    "w_dmg": 70, "w_ap": 55, "w_root": 75, "w_slow": 40, "w_slow_t": 90,
    "rune_ms": 30, "rune_t": 120,
    # the Flux marks: how often a mark checks for the burst, how long the burst window lasts, a tick of delay
    "pop_period": 2, "pop_window": 3, "pop_delay": 0,
    # ult: R Realm Warp - armed as he closes in (r_range), for r_arm ticks, checked every r_poll ticks.
    # Escape: two enemy champions within r_esc (or, with r_alone, one within r_esc1 and no allied champion within
    # r_mates) -> a jump of r_back in r_back_t ticks away from one of them. Chase: no enemy champion within r_reach
    # (his attack range) though one was within the last r_seen ticks, one his team hit lately within r_chase (and,
    # with r_chase_mate, an allied champion within r_mates) -> the portal where the line toward it touches the first
    # enemy champion (r_stop), at most r_move away. The allied units standing in his portal (r_portal) come along.
    "r_cd": 3000, "r_range": 120000, "r_arm": 600, "r_poll": 10, "r_ch": 60,
    "r_esc": 30000, "r_alone": 1, "r_esc1": 15000, "r_mates": 50000, "r_back": 60000, "r_back_t": 4,
    "r_reach": 45000, "r_seen": 90, "r_chase": 100000, "r_chase_mate": 1, "r_move": 80000, "r_stop": 38000,
    "r_crowd": 3, "r_chase_mates": 25000,
    "r_portal": 25000, "r_grab": 15000, "r_carry": 30000, "r_land": 16, "r_e_range": 70000,
    # his spoken lines: one every vo_gap ticks at most
    "vo_gap": 600,
}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def n(x):
    return f"{ID}_{x}"


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


NONE = {"type": "Combine", "effects": []}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    duration = tick if isinstance(tick, str) else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": duration, **fields},
            "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    duration = tick if isinstance(tick, str) else {"Time": {"tick": tick}}
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": duration, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def self_only(*effects):
    """Effects on the caster alone, queued on his own unit (a WithSelf would also hit the action's target)."""
    return around(1000, "AllyOnlySelf", effects)


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


GENS = ("c", "d", "r")


def build(p):
    hp = p["p_hp"]

    # ------------------------------------------------------------------ Flux marks
    def burst_damage():
        return sw("r_pass", ap(p["fbr_dmg"], p["fbr_ap"], hp), ap(p["fb_dmg"], p["fb_ap"], hp))

    def marks(gen):
        """The two AddCasted a unit in the E zone gets: the rune picture while the generation lives, and the check
        that bursts it when a Q hit raised q_pop."""
        pic = {"type": "AddCasted", "casted_type": "Bleed", "duration": p["flux_t"], "period": 12,
               "effects": [sw(f"fx_{gen}", view("flux"))]}
        burst = combine(burst_damage(), view("q_pop"), tsfx("q_pop"))
        check = {"type": "AddCasted", "casted_type": "Bleed", "duration": p["flux_t"], "period": p["pop_period"],
                 "effects": [sw(f"fx_{gen}", sw("q_pop", burst))]}
        return [pic, check]

    def flux_up(yes, no=None):
        """`yes` while a Flux generation lives."""
        return sw("fx_any", yes, no)        # one flag for every generation: three nested checks tripled `yes`

    def spell_flux(gen, target_from_cast=True):
        """E: an orb at the unit; on the hit its damage, the generation switched on (the other off), and a lob of
        one tick that lands on the unit and lays the Flux zone there (wider when Flux was already up)."""
        others = [g for g in GENS if g != gen]

        def zone(r):
            return {"type": "RangeProjectile", "name": n(f"e_zone_{gen}"), "shape": circle(r), "delay": 2, "apply": 1,
                    "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in marks(gen)]}

        lob = {"type": "ParabolicProjectile", "name": n("e_lob"), "travel_time": 1, "range": 200000,
               "shape": circle(1000), "range_effect_name": "", "applied_target": "EnemyWithoutTower",
               "applied_effects": [], "end_effects": [sw("e_wide", zone(p["flux_r2"]), zone(p["flux_r"]))]}
        hit = [ap(p["e_dmg"], p["e_ap"], hp), view("e_hit"), tsfx("e_hit"),
               self_only(flux_up(flag("e_wide", 4)), *rm(*[f"fx_{o}" for o in others]), refresh(f"fx_{gen}", p["flux_t"]),
                         refresh("fx_any", p["flux_t"])),
               delayed(1, lob)]
        return {"type": "TargetProjectile", "name": n("e_orb"), "speed": p["e_speed"], "y_offset": p["orb_y"],
                "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in hit]}

    # ------------------------------------------------------------------ Q Overload's bolt
    def pop():
        """A Q hit while Flux is up: every Flux mark bursts once, then the Flux is used up."""
        w, d = p["pop_window"], p["pop_delay"]
        go = [flag("q_pop", w), self_only(delayed(w, *rm("fx_c", "fx_d", "fx_r", "fx_any", "q_pop")))]
        if d:
            return self_only(delayed(d, *go))
        return combine(*go)

    def bolt(name):
        hit = [ap(p["q_dmg"], p["q_ap"], hp), view("q_hit"), tsfx("q_hit"), flux_up(pop())]
        return {"type": "LinearProjectile", "name": n(name), "speed": p["q_speed"], "range": p["q_len"],
                "shape": circle(p["q_rad"]), "penetrate": False, "y_offset": p["q_y"],
                "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in hit], "end_effects": []}

    # ------------------------------------------------------------------ attack
    orb = {"type": "TargetProjectile", "name": n("orb"), "speed": p["orb_speed"], "y_offset": p["orb_y"],
           "applied_target": "Enemy",
           "applied_effects": [T(attack(0, 100)), T(view("hit")), T(tsfx("attack_hit"))]}
    # (the engine itself plays league_ryze_attack on every attack)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", orb,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q alone
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Direction", "EnemyWithoutTower", combine(
        sfx("q_cast"), voice("vo_q", p), cview("q_cast"), bolt("q_bolt")))

    # ------------------------------------------------------------------ skill2: E -> W -> Q
    # W and Q go at the cast's target, queued on it (a Delayed on a unit that died runs only its pictures); each sets a
    # flag, and a tick later his own unit checks it: the target died -> W at a champion in reach, Q at a champion in
    # reach, else at any enemy in reach. Sounds, runes and the haste are queued on him (they always play).
    def rand(target, rng, effects):
        return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
                "effects": list(effects)}

    w_hit = combine(ap(p["w_dmg"], p["w_ap"], hp), tsfx("w_hit"),
                    flux_up(combine({"type": "Bind", "duration": p["w_root"]}, view("w_root")),
                            combine(buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_cage"))))
    w_fb = sw("c_w_ok", NONE, rand("EnemyChampion", p["c_range"], [w_hit]))
    def q_fb(ok):
        return sw(ok, NONE, combine(
            rand("EnemyChampion", p["q_range"], [flag("c_fb", 1), bolt("q_bolt")]),
            sw("c_fb", NONE, rand("EnemyWithoutTower", p["q_range"], [bolt("q_bolt")]))))
    dw, dq = p["c_w"] - p["c_e"], p["c_q"] - p["c_e"]
    de2, dq2 = p["c_e2"] - p["c_e"], p["c_q2"] - p["c_e"]
    skill2 = action("skill2", p["c_dur"], p["c_cd"], p["c_e"], p["c_range"], "Targeting", "EnemyWithoutTower", combine(
        voice("vo_e", p), sfx("e_cast"), cview("e_cast"), spell_flux("c"),
        delayed(dw, w_hit, flag("c_w_ok", 3)),
        delayed(dq, bolt("q_bolt"), flag("c_q_ok", 3)),
        # the second E and Q only at the cast's target (a fallback for each put the tree at 515 nodes, copied every
        # tick): a target dead by then took the first three
        *([delayed(de2, spell_flux("d")), delayed(dq2, bolt("q_bolt"))] if p["c_two"] else []),
        self_only(
            refresh("rune1", dq + 2),
            delayed(dw, sfx("w_cast"), *rm("rune1"), refresh("rune2", dq - dw + 2)),
            delayed(dw + 1, w_fb),
            delayed(dq, sfx("q_cast"), cview("q_cast"), *rm("rune2"), cview("rune_out"),
                    refresh("q_haste", p["rune_t"], move_speed_mult=p["rune_ms"])),
            delayed(dq + 1, q_fb("c_q_ok")),
            *([delayed(de2, sfx("e_cast"), cview("e_cast"), refresh("rune1", dq2 - de2 + 2)),
               delayed(dq2, sfx("q_cast"), cview("q_cast"), *rm("rune1"), cview("rune_out"),
                       refresh("q_haste", p["rune_t"], move_speed_mult=p["rune_ms"]))] if p["c_two"] else []),
            )))

    # ------------------------------------------------------------------ ult: R Realm Warp
    # The slot only arms R (a 3-tick action on the idle tag, cast as he closes in on an enemy champion); while armed a
    # check every r_poll ticks picks the use: an enemy champion right on him -> the portal opens and he jumps away from
    # that champion; else, with no enemy champion in his reach, one his team has been hitting within r_chase -> the
    # portal opens toward it and he lands about his attack range short of it; else nothing (an enemy already in reach
    # is fought where he stands). Left unused, the window refunds the cooldown.
    ch = p["r_ch"]
    # crowd control breaks the channel: `r_cut` (the jump waits for its absence)
    cc_check = rand("AllyChampionInCC", 1, [refresh("r_cut", ch), {"type": "RemoveCasterAnimation", "name": "ult"}])
    land_e = rand("EnemyChampion", p["r_e_range"], [sfx("e_cast"), spell_flux("r")])
    # every allied unit standing in his portal comes along (champions and minions): the zone sends each a homing shot
    # on BothWithoutTower that carries the Grab - a Grab straight from a zone on allies drags the towers too
    carry = {"type": "TargetProjectile", "name": n("r_carry"), "speed": p["r_carry"], "y_offset": 0,
             "applied_target": "BothWithoutTower",
             "applied_effects": [T({"type": "Grab", "speed": p["r_grab"]}), T(view("r_ally"))]}
    pull = {"type": "RangeProjectile", "name": n("r_pull"), "shape": circle(p["r_portal"]), "delay": 2, "apply": 1,
            "applied_target": "AllyNotSelf", "applied_effects": [T(carry)]}

    def anchor(after):
        """His own portal's spot (Ekko's anchor, a line of 1): `after` ticks on, once he has gone, the pull there."""
        return {"type": "LinearProjectile", "name": n("r_anchor"), "speed": 1, "range": 1, "shape": circle(1000),
                "penetrate": True, "y_offset": 5000, "applied_target": "EnemyChampion", "applied_effects": [],
                "end_effects": [delayed(after, sw("r_go", pull))]}

    def start():
        """The channel: his portal, the cast animation, the crowd-control checks (queued on him)."""
        return [*rm("r_armed", "r_cut", "r_go"), anim("ult", ch), sfx("r_cast"), sfx("vo_r"), cview("r_portal"),
                self_only(*[delayed(t, cc_check) for t in range(15, ch, 15)])]

    def arrive(go_t):
        return [flag("r_go", go_t), sw("r_pass", NONE, flag("r_pass", "Permanent")), cview("r_out"), sfx("r_warp")]

    def land():
        return [anim("ult_land", p["r_land"]), cview("r_in"), delayed(3, land_e)]

    # the chase (on the champion picked): a hidden line toward it that stops r_stop short of the first enemy champion
    # (or after r_move) plays the far portal where it stops, and at the end of the channel puts him there
    beacon = {"type": "LinearProjectile", "name": n("r_beacon"), "speed": max(1, p["r_move"] // 3), "range": p["r_move"],
              "shape": circle(p["r_stop"]), "penetrate": False, "y_offset": 5000, "applied_target": "EnemyChampion",
              "applied_effects": [], "end_effects": [view("r_dest"), delayed(ch - 3, sw("r_cut", NONE, combine(
                  *arrive(8), {"type": "Teleport"}, *land())))]}
    chase = combine(*start(), beacon, anchor(ch + 1))
    # the escape (on the champion right on him): at the end of the channel a jump straight away from it
    bt = p["r_back_t"]
    escape = combine(*start(), anchor(ch + bt + 1), delayed(ch, sw("r_cut", NONE, combine(
        *arrive(bt + 3), {"type": "MoveBack", "speed": p["r_back"] // bt, "tick": bt}, delayed(bt, *land())))))
    # the check: count the enemy champions round him (league_kayle R's ladder), note one in his reach, and a tick
    # later pick escape, chase or nothing
    def crowd(n):
        """league_kayle R's ladder: one more of r_c1..r_cn for every enemy champion the zone reaches."""
        e = flag(f"r_c1", 2)
        for i in range(2, n + 1):
            e = sw(f"r_c{i - 1}", flag(f"r_c{i}", 2), e)
        return sw(f"r_c{n}", NONE, e) if n > 1 else e
    alone = [rand("EnemyChampion", p["r_esc1"], [sw("r_mate", NONE, flag("r_n2", 2))])] if p["r_alone"] else []
    hunt = rand("EnemyChampionRecentlyAttacked", p["r_chase"], [sw("r_armed", chase)])
    # never into a teamfight: r_crowd enemy champions within r_chase round him -> no chase
    hunt = sw(f"r_c{p['r_crowd']}", NONE, hunt)
    if p["r_chase_mate"]:
        hunt = sw("r_mate2", hunt)
    r_try = sw("r_armed", combine(
        *rm("r_n1", "r_n2", "r_near", "r_mate", "r_mate2", *[f"r_c{i}" for i in range(1, p["r_crowd"] + 1)]),
        around(p["r_chase"], "EnemyChampion", [crowd(p["r_crowd"])]),
        rand("AllyNotSelf", p["r_chase_mates"], [flag("r_mate2", 2)]),
        around(p["r_esc"], "EnemyChampion", [sw("r_n1", flag("r_n2", 2), flag("r_n1", 2))]),
        rand("AllyNotSelf", p["r_mates"], [flag("r_mate", 2)]), *alone,
        rand("EnemyChampion", p["r_reach"], [flag("r_near", 2), refresh("r_seen", p["r_seen"])]),
        delayed(1, sw("r_armed", sw("r_n2", rand("EnemyChampion", p["r_esc"], [sw("r_armed", escape)]),
                                    sw("r_near", NONE, sw("r_seen", hunt)))))))
    poll = {"type": "AddCasted", "casted_type": "Bleed", "duration": p["r_arm"], "period": p["r_poll"], "effects": [r_try]}
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "None", "EnemyChampion", combine(
        *rm("r_armed"), flag("r_armed", p["r_arm"]), self_only(poll),
        self_only(delayed(p["r_arm"], sw("r_armed", combine(*rm("r_armed"), flag("r_refund", 3, ult_cooldown_mult=4900)))))),
        key="ult")

    # ------------------------------------------------------------------ views
    views_p = [
        {"type": "Animated", "name": n("orb"), "anim": FX, "tag": "orb", "repeat": True, "z": 1},
        {"type": "Animated", "name": n("q_bolt"), "anim": FX, "tag": "q_bolt", "repeat": True, "z": 1},
        {"type": "Animated", "name": n("e_orb"), "anim": FX, "tag": "e_orb", "repeat": True, "z": 1},
    ]
    E = lambda name, anim_, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                 "z": z, "is_follow": follow}
    views_e = [E("hit", FX), E("q_cast", FX, follow=False), E("q_hit", FX), E("q_pop", FX, 2), E("e_cast", FX), E("e_hit", FX),
               E("flux", FX, 2), E("w_root", FX), E("w_cage", FX), E("rune_out", FX),
               E("r_portal", BIG, -1, False), E("r_dest", BIG, -1, False), E("r_out", BIG, 1, False),
               E("r_in", BIG, 1), E("r_ally", FX, 2)]
    B_ = lambda name, z=1: {"type": "Animated", "name": n(name), "anim": FX, "tag": name, "repeat": True, "z": z}
    views_b = [B_("rune1"), B_("rune2"), B_("w_slow", -1), B_("q_haste", -1)]
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }


def nodes(o):
    """Effect nodes in a tree (what the engine copies every tick for skill and skill2)."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[])
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = v if isinstance(p[k], str) else type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    d = build(p)
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    os.makedirs(os.path.dirname(lp(a.out)), exist_ok=True)
    with open(lp(a.out), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(a.out, len(text), "nodes", {k: nodes(d[k]["effect"]) for k in ("attack", "skill", "skill2", "ult")})


if __name__ == "__main__":
    main()
