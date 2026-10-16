"""Build league_orianna.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_orianna.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-16: mid lane, the main pack plus a native add-on addons/league_orianna, PPU 1.5; every
recommended option - W fires by itself at the ball sharing Q's icon, R waits for a good moment, E Janna's way):
  The Ball. It is in one of three places, as in League: beside her (the caster flag `home`, a Permanent buff whose
          view_buffs picture floats at her side and whose armour and magic resistance are E's passive), lying where Q
          threw it (a hidden lob's landing: a nested chain of checkpoints every b_step ticks re-stamps its picture,
          checks the leash and fires W / R there - champion-data "Feathers that lie where a blade stopped" and "A shadow
          that copies the combo", a flat list: nested, the JSON went 373 levels deep), or riding an ally E sent it to (an AddCasted on the ally, league_taric's Bastion: a
          one-tick lob onto the ally every e_period ticks fires W / R round him). It flies back to her (a
          `BackToCasterLinearProjectile`) when she is farther than `leash` from it or after b_life ticks on the ground /
          e_ride on an ally; it vanishes with a new throw (every throw is generation gA or gB in turn and its checkpoints go on
          only while that flag is up; a ride the same with eA / eB) and is beside her again at every life's first action.
  The controller. skill and skill2 are cloned every tick (champion-data 8, tools/perf), a periodic AddCasted hung on
          the hero is not (measured on league_zed, 2026-10-10): her attacks hang one on her (ctl_t ticks,
          period ctl_p) unless the flag `polling` says one runs. It throws Q (q_go), sends E (e_go), fires W / R round
          her while the ball is home and brings the ball home when its ally is gone. The Q and E slots only raise those
          flags; with no controller yet in this life (no attack since she respawned) Q throws a ball that comes straight
          back and E shields her; R waits for one.
  passive Clockwork Windup (发条驱动): every attack adds p_dmg + p_ap% AP magic damage; attacks within p_t ticks of the
          last stack it, p_st + p_st_ap% AP more for each of two stacks (League: on the same target; nothing in the data
          tells which unit a hit is on, so any target).
  attack  A bolt (League's flick, 525 range).
  skill   Q Command: Attack (指令：攻击): a `Targeting` cast on `EnemyWithoutTower` (q_range). With an enemy champion within
          q_range the controller throws the ball at one: it lands q_travel ticks later where the champion stood at the
          throw (dodged by walking off), q_dmg + q_ap% AP to the first unit within q_r and q_next% of that to the others
          (League: 70% for the rest), and stays there. At a minion or monster the slot throws it itself and it comes
          straight back (a lying ball's tree is the controller's; one more selector would double it).
          W Command: Dissonance (指令：杂音) shares the icon (no slot of its own): while its cooldown flag w_cd is off, an
          enemy champion within w_r of the ball (else, with no champion within w_farm of it, any enemy unit within
          w_r: the wave) sets it off there: w_dmg + w_ap% AP, w_slow% slow on enemies and w_haste% haste on allies for
          w_t ticks (League: the field lasts 3 s and the slow fades over 2 s).
  skill2  E Command: Protect (指令：保护): a `Targeting` cast on `EnemyChampion` (e_range: only in a fight,
          league_janna E). An enemy champion within e_self of her: the ball comes to her and shields her. Else the
          ball flies to the ally nearest an enemy champion (an enemy champion within e_range, an ally within e_near of
          it; else herself): e_sh + e_ap% AP shield for e_t ticks, e_dmg + e_dap% AP to
          enemies on the line toward him, and while it rides him e_def armour and magic resistance (League's passive).
  ult     R Command: Shockwave (指令：冲击波): the slot arms the ult for r_arm ticks (league_syndra / league_pantheon R);
          wherever the ball is, it fires once two enemy champions stand within r_r of it, or one champion his team is
          fighting (EnemyChampionRecentlyAttacked) within r_r with no second enemy champion within r_iso (an isolated
          target). r_delay ticks after the cast (League: 0.5 s) r_dmg + r_ap% AP to every enemy within r_r, flung
          toward the ball and through it (`Pull` r_pull x r_pull_t at the ball's spot; League: 325 units). Unused, the
          window ends with the cooldown capped (r_reset).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_orianna.data_champion")
ID = "league_orianna"
FX = "asset/league/effects/league_orianna_fx"
BIG = "asset/league/effects/league_orianna_big"

# Numbers: League's V26.20 ratios inside the base Magician ranges (champion-data 2) and the pack's mids (league_syndra,
# league_viktor). Balance: Temp/or_sim/sim/kd.py --lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage,
# white_mage.
P = {
    # stats (Magician base: attack 80 +6, magic power 40 +20, hp 900 +100, defence 20, mr 20, move 900, range 60000,
    # attack every 90 ticks); League's Orianna: 565 +110 hp, 44 AD, 20 armour, 26 mr, 325 move, 525 range
    "hp": 860, "hp_g": 95, "atk": 76, "atk_g": 6, "mp": 40, "mp_g": 20, "def": 20, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 28, "atk_cd": 90, "a_st": 10, "bolt_speed": 4500, "bolt_y": -3000,
    # passive (League: 10-55 + 15% AP; a stack adds 15% of it, two at most, 4 s)
    "p_dmg": 18, "p_ap": 15, "p_st": 4, "p_st_ap": 3, "p_t": 240,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # the ball (League: leash 1290, +100 on an ally)
    "b_step": 15, "b_life": 300, "leash": 110000, "leash_ally": 118000, "b_back": 4500,
    # Q (League: 60-180 + 55% AP, the others 70%, radius 175, range 825, speed 1400, cd 7-3 s)
    "q_cd": 300, "q_range": 70000, "q_dur": 20, "q_st": 6, "q_travel": 18, "q_r": 16000, "q_dmg": 70, "q_ap": 55,
    "q_next": 70,
    # W (League: 70-230 + 80% AP, radius 225, 20-40% haste / slow, cd 7 s)
    "w_cd": 420, "w_r": 24000, "w_farm": 70000, "w_dmg": 70, "w_ap": 70, "w_slow": 30, "w_haste": 30, "w_t": 120,
    "w_anim": 18,
    # E (League: shield 55-195 + 45% AP 2.5 s, 60-180 + 30% AP on the way, 6-30 armour / mr, range 1120, cd 9 s)
    "e_cd": 540, "e_range": 75000, "e_dur": 18, "e_st": 6, "e_self": 22000, "e_near": 40000,
    "e_sh": 60, "e_ap": 45, "e_t": 150, "e_speed": 3500, "e_y": -3000, "e_dmg": 60, "e_dap": 30, "e_len": 60000,
    "e_w": 8000, "e_def": 12, "e_ride": 600, "e_period": 4,
    # R (League: 225-475 + 110% AP radius 415 after 0.5 s, flung 325 units, cd 110-80 s)
    "r_cd": 4200, "r_slot": 90000, "r_arm": 360, "r_reset": 4900, "r_delay": 30, "r_r": 36000, "r_iso": 70000,
    "r_dmg": 250, "r_ap": 100, "r_pull": 2400, "r_pull_t": 12, "r_anim": 36,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_orianna: the Ball's flights start where it really is (league_orianna:q / :e / :back
    # draw them, the data's own lob and homing fly hidden from her), E goes to the ally native picks (league_orianna:e_pick
    # raises e_this on him), E's line hits from where the ball was (league_orianna:e_hit; the data's line only from her),
    # R fires for two champions or a kill (league_orianna:r_kill raises c2) instead of an isolated target
    "native": 0,
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


NONE = {"type": "Combine", "effects": []}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


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


def magic(dmg, ap):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap, "hp_ratio": 0, "can_crit": False}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a target's or a projectile's list (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, y=-3000):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, end):
    """The ball flying back to her from where the effect runs (a projectile's end point; picture only: on `Ally`, so the
    enemy AI does not dodge it - champion-data 8)."""
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": 960000,
            "shape": circle(1000), "penetrate": True, "applied_target": "Ally", "applied_effects": [],
            "end_effects": list(end)}


def probe(end):
    """A hidden projectile that starts where the effect runs (a `Delayed` at a lying ball) and ends there at once, so its
    end_effects can search round that spot (`RandomTarget {from_projectile}`)."""
    return {"type": "BackToCasterLinearProjectile", "name": n("b_probe"), "speed": 1000, "range": 1,
            "shape": circle(1), "penetrate": True, "applied_target": "Ally", "applied_effects": [],
            "end_effects": list(end)}


def lob(name, travel, target, end):
    """A ParabolicProjectile onto the target's spot as it is now (hidden unless `name` has a view)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 960000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, target, effects):
    """A one-tick area where it is started (a projectile's end_effects or a `Delayed` there)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def alive(*effects):
    """Only while she lives (a dead caster's `Delayed` effects and casteds run in the game, champion-data 5): a search
    that finds no dead caster raises a 1-tick flag, read and taken off in the same list."""
    return combine(pick(1, "AllyOnlySelf", flag("al", 1)), sw("al", combine(*rm("al"), *effects)), *rm("al"))


def ladder(a, b, t):
    """Counting units one by one in an area's list: the first raises a, the second b."""
    return sw(a, refresh(b, t), refresh(a, t))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    nat = bool(p["native"])
    step = p["b_step"]

    def native(ref):
        """The add-on's native effect (native=1 only)."""
        return {"type": "Native", "effect_ref": f"{ID}:{ref}"} if nat else None
    held = dict(defence=p["e_def"], magic_resistance=p["e_def"])
    # every life starts with the ball beside her (death clears a mod's buffs)
    init = sw("init", NONE, combine(flag("init", None), refresh("home", None, **held)))

    # ------------------------------------------------------------------ W and R wherever the ball is
    def w_fire(here):
        """W's pulse: at the ball's spot (here: a projectile's end point or a Delayed there) or round her."""
        hits = [magic(p["w_dmg"], p["w_ap"]), buff("w_slow", p["w_t"], move_speed_mult=-p["w_slow"]), view("w_hit")]
        haste = [buff("w_haste", p["w_t"], move_speed_mult=p["w_haste"])]
        if here:
            out = [view("w_ring"), zone("w_dmg", p["w_r"], "EnemyWithoutTower", hits),
                   zone("w_fast", p["w_r"], "AllyChampion", haste)]
        else:
            out = [cview("w_ring"), around(p["w_r"], "EnemyWithoutTower", hits),
                   around(p["w_r"], "AllyChampion", haste)]
        return combine(flag("w_cd", p["w_cd"]), anim("skill_w", p["w_anim"]), sfx("w"), voice("vo_w", p), *out)

    def w_check(here):
        """An enemy champion within w_r of the ball, else (no champion within w_farm) any enemy unit within w_r."""
        fp = here
        return sw("w_cd", NONE, combine(
            pick(p["w_r"], "EnemyChampion", flag("w_now", 1), fp=fp),
            sw("w_now", NONE, combine(pick(p["w_farm"], "EnemyChampion", flag("w_busy", 1), fp=fp),
                                      sw("w_busy", NONE, pick(p["w_r"], "EnemyWithoutTower", flag("w_now", 1), fp=fp)),
                                      *rm("w_busy"))),
            sw("w_now", combine(*rm("w_now"), w_fire(here)))))

    def r_fire(here):
        """The shockwave: the picture now (its blast frame r_delay ticks in), the blow and the fling r_delay later."""
        hits = [magic(p["r_dmg"], p["r_ap"]), {"type": "Pull", "speed": p["r_pull"], "tick": p["r_pull_t"]},
                view("r_hit"), tsfx("r_hit")]
        if here:
            blow = [view("r_wave"), delayed(p["r_delay"], zone("r_dmg", p["r_r"], "EnemyWithoutTower", hits))]
        else:
            blow = [cview("r_wave"), delayed(p["r_delay"], alive(around(p["r_r"], "EnemyWithoutTower", hits)))]
        return combine(*rm("r_arm"), anim("ult", p["r_anim"]), sfx("r"), voice("vo_r", p), *blow)

    counts = ("c1", "c2", "ra", "i1", "i2")
    # two enemy champions within r_r, or one his team is fighting with no second one within r_iso: r_go (the blow
    # written once, not once per rule)
    def r_check(here):
        rule = flag("r_go", 1) if nat else sw("ra", sw("i2", NONE, flag("r_go", 1)))
        go = lambda: [sw("c2", flag("r_go", 1), rule), *rm(*counts),
                      sw("r_go", combine(*rm("r_go"), r_fire(here)))]
        if nat and here:
            return sw("r_arm", combine(
                zone("r_c", p["r_r"], "EnemyChampion", [ladder("c1", "c2", 3), native("r_kill")]),
                delayed(2, alive(sw("r_arm", combine(*go()), combine(*rm(*counts)))))))
        if nat:
            return sw("r_arm", combine(
                around(p["r_r"], "EnemyChampion", [ladder("c1", "c2", 2), native("r_kill")]), *go()))
        if here:   # areas at the spot count on the next tick
            return sw("r_arm", combine(
                zone("r_c", p["r_r"], "EnemyChampion", [ladder("c1", "c2", 3)]),
                zone("r_ra", p["r_r"], "EnemyChampionRecentlyAttacked", [refresh("ra", 3)]),
                zone("r_i", p["r_iso"], "EnemyChampion", [ladder("i1", "i2", 3)]),
                delayed(2, alive(sw("r_arm", combine(*go()), combine(*rm(*counts)))))))
        return sw("r_arm", combine(
            around(p["r_r"], "EnemyChampion", [ladder("c1", "c2", 2)]),
            around(p["r_r"], "EnemyChampionRecentlyAttacked", [refresh("ra", 2)]),
            around(p["r_iso"], "EnemyChampion", [ladder("i1", "i2", 2)]),
            *go()))

    # ------------------------------------------------------------------ the ball's moves
    def leave():
        """The ball leaves where it was: a lying ball stops at its next checkpoint (its generation flag gA / gB is
        gone), a ride at its next run (eA / eB), a ball on its way back does not land (b_ret)."""
        return combine(*rm("home", "gA", "gB", "eA", "eB", "b_ret"))

    def go_home():
        """From here (a projectile's end point or a Delayed there) back to her; beside her again when it arrives."""
        return combine(refresh("b_ret", 120), back("b_back", p["b_back"], [
            sw("b_ret", combine(*rm("b_ret"), refresh("home", None, **held), cview("b_home_in")))]))

    def lying(gen):
        """A ball lying at the spot: a flat list of checkpoints every b_step ticks from the landing (a nested chain
        went 373 levels deep in the JSON - Xayah's 109 is the deepest shipped), each going on only while its
        generation flag is up: the ball's picture for the step, the leash, W and R there; at b_life it flies home."""
        def checkpoint(r, later):
            """`later`: in a `Delayed` the projectile is gone and a `RandomTarget {from_projectile}` finds nothing
            (the sim, 2026-10-16: every lying ball flew home at its second checkpoint), so the searches run in the
            end_effects of a probe that leaves the spot and ends there (a `BackToCasterLinearProjectile` of range 1:
            the only projectile that starts at such a spot)."""
            near = pick(p["leash"], "AllyOnlySelf", flag("b_near", 1), fp=True)
            here = [w_check(True)] + ([r_check(True)] if r else [])
            look = [near, sw("b_near", combine(*rm("b_near"), *here), combine(*rm(gen), go_home()))]
            return alive(sw(gen, combine(view("b_ground"), probe(look) if later else combine(*look))))
        # R looks every other checkpoint (it waits for a moment anyway; its areas are most of a checkpoint's nodes)
        out = [checkpoint(True, False)]
        out += [delayed(t, checkpoint(t % (2 * step) == 0, True)) for t in range(step, p["b_life"], step)]
        out.append(delayed(p["b_life"], alive(sw(gen, combine(*rm(gen), go_home())))))
        return out

    def landing(gen):
        first = [magic(p["q_dmg"], p["q_ap"]), refresh("q_first", 3)]
        rest = [magic(p["q_dmg"] * p["q_next"] // 100, p["q_ap"] * p["q_next"] // 100)]
        return [view("q_land"), sfx("q_land"),
                zone("q_hit", p["q_r"], "EnemyWithoutTower", [sw("q_first", combine(*rest), combine(*first)),
                                                              view("q_hit"), tsfx("q_hit")]),
                delayed(2, *rm("q_first")), *lying(gen)]

    # thrown at an enemy champion within q_range (the slot throws at other units itself): every other throw is
    # generation B, so the lying ball of the last one stops
    q_name = "q_fly" if nat else "q_ball"

    def throw(gen):
        return combine(native("q"), leave(), flag(gen, None), sfx("q"),
                       lob(q_name, p["q_travel"], "EnemyChampion", landing(gen)))

    q_throw = sw("par", combine(*rm("par"), pick(p["q_range"], "EnemyChampion", throw("gB"))),
                 combine(flag("par", None), pick(p["q_range"], "EnemyChampion", throw("gA"))))

    # the ball riding an ally (gen: eA / eB, so a ride the next E replaced stops)
    def ride(gen):
        near = pick(p["leash_ally"], "AllyOnlySelf", flag("b_near", 1), fp=True)
        lookout = lob("b_on", 1, "AllyChampion", [near, sw("b_near", combine(*rm("b_near"), w_check(True),
                                                                              r_check(True)),
                                                           combine(*rm("eA", "eB"), go_home()))])
        # the Ball on him is e_def's picture (view_buffs, tag ball_side): a ViewEffect re-stamped every e_period ticks
        # would only ever show its first frame
        run = alive(sw(gen, combine(refresh("ride", p["e_period"] + 3),
                                    buff("e_def", p["e_period"] + 2, **held), lookout)))
        return casted(p["e_ride"], p["e_period"], run)

    def hug(gen):
        return [shield(p["e_sh"], p["e_ap"], p["e_t"]), view("e_shield"), tsfx("e_shield"), ride(gen)]

    def send():
        """On the ally picked: the ball flies to him (hitting the enemies on the way), shields him and rides him."""
        flight = p["e_range"] // p["e_speed"] + 4
        e_name = "e_fly" if nat else "e_ball"
        go = sw("epar", combine(*rm("epar"), flag("eB", None), homing(e_name, p["e_speed"], p["e_y"],
                                                                     "AllyChampion", hug("eB"))),
                combine(flag("epar", None), flag("eA", None), homing(e_name, p["e_speed"], p["e_y"],
                                                                    "AllyChampion", hug("eA"))))
        path = line("e_path", p["e_speed"], p["e_len"], p["e_w"], "EnemyWithoutTower",
                    [magic(p["e_dmg"], p["e_dap"]), view("e_hit")])
        if nat:
            return combine(native("e"), sw("home", path), flag("e_lock", 3), leave(),
                           refresh("ride", flight + p["e_period"] + 4), sfx("e"), go)
        return combine(flag("e_lock", 3), leave(), refresh("ride", flight + p["e_period"] + 4), sfx("e"), go, path)

    def to_me():
        """E on herself: the ball comes back at once and she takes the shield."""
        return combine(native("back"), flag("e_lock", 3), leave(), refresh("home", None, **held), cview("b_home_in"), sfx("e"),
                       on_me(shield(p["e_sh"], p["e_ap"], p["e_t"]), view("e_shield")))

    if nat:
        beside = around(p["e_range"], "AllyNotSelf", [native("e_pick"), sw("e_this", combine(
            *rm("e_this"), sw("e_lock", NONE, send())))])
    else:
        beside = pick(p["e_range"], "EnemyChampion",
                      lob("e_look", 1, "EnemyChampion", [pick(p["e_near"], "AllyNotSelf", sw("e_lock", NONE, send()),
                                                              fp=True)]))
    e_send = combine(*rm("e_lock", "e_me"), pick(p["e_self"], "EnemyChampion", flag("e_me", 1)),
                     sw("e_me", combine(*rm("e_me"), to_me()),
                        combine(beside, delayed(2, alive(sw("e_lock", NONE, to_me()))))))

    # the ball's ally is gone (dead, or the ride ran out): beside her again
    lost = sw("eA", sw("ride", NONE, combine(*rm("eA", "eB"), refresh("home", None, **held), cview("b_home_in"))),
              sw("eB", sw("ride", NONE, combine(*rm("eA", "eB"), refresh("home", None, **held), cview("b_home_in")))))

    ctl = combine(refresh("polling", p["ctl_p"] + 2),
                  sw("q_go", combine(*rm("q_go"), q_throw)),
                  sw("e_go", combine(*rm("e_go"), e_send)),
                  sw("home", combine(w_check(False), r_check(False))),
                  lost)
    hang = on_me(sw("polling", NONE, combine(refresh("polling", p["ctl_p"] + 2), casted(p["ctl_t"], p["ctl_p"], ctl))))

    # ------------------------------------------------------------------ attack: the bolt + Clockwork Windup
    windup = [magic(p["p_dmg"], p["p_ap"]), sw("p1", magic(p["p_st"], p["p_st_ap"])),
              sw("p2", magic(p["p_st"], p["p_st_ap"]))]
    stack = sw("p1", combine(refresh("p1", p["p_t"]), refresh("p2", p["p_t"])), refresh("p1", p["p_t"]))
    shoot = delayed(p["a_st"], sfx("a_shot"), homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy",
                                                      [attack(0, 100), *windup, view("a_hit"), tsfx("a_hit")]), stack)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(init, hang, shoot), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q (the controller throws)
    # at a minion or a monster (no enemy champion within q_range), or with no controller yet in this life: the ball
    # flies to the target and straight back
    lone = combine(native("q"), leave(), sfx("q"),
                   lob(q_name, p["q_travel"], "EnemyWithoutTower", [
                       view("q_land"), sfx("q_land"),
                       zone("q_hit", p["q_r"], "EnemyWithoutTower", [magic(p["q_dmg"], p["q_ap"]), view("q_hit")]),
                       go_home()]))
    # the AI scores the branch the flags pick between ticks (champion-data 8): q_x is never there then, so it reads Q's
    # damage; when the slot runs, the flag is up and the real branch goes
    champ = combine(*rm("q_ch"), pick(p["q_range"], "EnemyChampion", flag("q_ch", 1)),
                    sw("q_ch", combine(*rm("q_ch"), refresh("q_go", 4)), lone))
    q_go = combine(flag("q_x", 1), sw("q_x", combine(*rm("q_x"), sw("polling", champ, lone)),
                                      magic(p["q_dmg"], p["q_ap"])), *rm("q_x"))
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(init, voice("vo_q", p), q_go))

    # ------------------------------------------------------------------ skill2: E (the controller sends)
    e_real = sw("polling", refresh("e_go", 4),
                combine(on_me(shield(p["e_sh"], p["e_ap"], p["e_t"]), view("e_shield")), sfx("e")))
    # Q's q_x trick: the game's AI scores the branch the flags pick between ticks, and with the controller running that
    # was a bare flag - worth nothing, so in game E was hardly ever cast (the add-on's log, 2026-10-16: one E in a
    # 10-minute match; the classic SDK's AI casts it anyway). e_x is never there between ticks, so the AI reads E's
    # damage on the champion it targets; when the slot runs, the flag is up and the real branch goes
    e_go = combine(flag("e_x", 1), sw("e_x", combine(*rm("e_x"), e_real), magic(p["e_dmg"], p["e_dap"])), *rm("e_x"))
    skill2 = action("skill_e", p["e_dur"], p["e_cd"], p["e_st"], p["e_range"], "Targeting", "EnemyChampion",
                    combine(init, voice("vo_e", p), e_go), key="skill2")

    # ------------------------------------------------------------------ ult: arms R (the controller fires it)
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_reset", 3, ult_cooldown_mult=p["r_reset"])))
    ult = action("idle", 3, p["r_cd"], 1, p["r_slot"], "None", "EnemyChampion",
                 combine(init, refresh("r_arm", p["r_arm"]), on_me(delayed(p["r_arm"], reset))), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the Ball's three pictures (tools/art/pack_orianna_fx.py): beside a champion (her `home`, the ally's `e_def`), lying
    # on the ground (b_ground), flying (Q's throw, E's send, the way back)
    views_p = [P_("a_bolt"), P_("q_ball", tag="ball_fly"), P_("e_ball", tag="ball_fly"), P_("b_back", tag="ball_fly")]
    views_e = [E("a_hit"), E("q_land", FX, 1, False), E("q_hit"), {**E("b_ground", FX, 1, False), "tag": "ball_ground"},
               E("b_home_in", FX, 2, False), E("w_ring", BIG, -1, False), E("w_hit"), E("e_shield"), E("e_hit"),
               E("r_wave", BIG, -1, False), E("r_hit")]
    views_b = [B_("home", FX, 2, "ball_side"), B_("e_def", FX, 2, "ball_side"), B_("w_slow", FX, -1),
               B_("w_haste", FX, -1)]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if nat:
        kit["passive"] = {"passive_ref": f"{ID}:ball", "params": {k: p[k] for k in (
            "q_travel", "e_speed", "e_range", "e_near", "e_len", "e_w", "e_dmg", "e_dap", "b_back", "r_dmg", "r_ap")}}
    return kit


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
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
    ap_.add_argument("--nodes", action="store_true")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p)
    if a.nodes:
        for s in ("attack", "skill", "skill2", "ult"):
            print(f"{s:7s} {nodes(kit[s]['effect']):4d} nodes")
    text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    os.makedirs(os.path.dirname(lp(a.out)), exist_ok=True)
    with open(lp(a.out), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(a.out, len(text))


if __name__ == "__main__":
    main()
