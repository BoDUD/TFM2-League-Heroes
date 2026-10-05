"""Build league_xerath.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_xerath.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-05: all the recommended options):
  attack  An arcane orb at the target (homing, physical 100% AD), League's 525 range.
  passive Mana Surge: TFM2 has no mana, so the surge that refills League's mana refills his spells instead. Every
          p_step x 4 ticks his next attack is a surge: a bigger orb with p_dmg + p_ap% AP magic damage, and on its hit
          Q's and skill2's remaining cooldowns are capped at 100 / (100 + p_cdr) of their cooltime (a 2-tick
          skill_cooldown_mult; ult_cooldown_mult -p_cdr keeps the ult's cap). The wait is four caster flags laid at once
          (p_a .. p_d, p_step x 1..4 ticks: he is ready when none is left); every unit his orb or his Shocking Orb kills
          (league_jinx's kill check) removes the longest one left, so a kill brings the next surge p_step ticks closer
          (League: 3.5 s per kill).
  skill   Q Arcanopulse, smart charge (league_varus Q's pacing): a `Direction` cast on `EnemyWithoutTower`. An enemy
          champion within q_aim_f at the cast -> the full charge (CasterAnimation skill, q_full_t ticks), else the quick
          one (skill_quick, q_quick_t ticks, q_quick% damage and a shorter beam). The action lasts 3 ticks and the
          animation holds him. At the release an enemy champion within reach gets the beam (a straight line at where
          he stands then: dodged by walking off it), else the cast's direction. The beam pierces every unit in the line.
  skill2  E -> W, the combo of League's players: a `Targeting` cast on `EnemyWithoutTower`.
          E Shocking Orb: a straight orb at where the target stands at the release; it stops on the first enemy:
          magic damage and a stun that grows with the distance flown (League 0.75 -> 2.25 s): the orb's flight time is
          read from two caster flags laid at the release (e_d1 / e_d2: e_band1 / e_band2 ticks). A champion-only twin
          on the same path (it passes minions) marks the first enemy champion on the line.
          W Eye of Destruction: a tick after the twin's hit, a 1-tick lob lands on that champion (stunned if the orb hit
          him too) and opens the eye there; with no champion on the line, e_fall ticks after the release it opens on
          the cast target. w_delay ticks later the blast: w_dmg + w_ap% AP and a w_slow% slow round it (w_r_out), and
          in the centre (w_r_in) League's sweet spot: w_mid% more damage and w_slow_mid% more slow.
  ult     R Rite of the Arcane, a standing channel (league_jhin R's pattern): a `Targeting` cast on `EnemyChampion`
          within r_range. He rises (ult, r_deploy ticks) and channels (ult_loop) for r_win ticks; a poll on him every
          r_poll ticks ends it when he is crowd-controlled and, between shots (r_gap ticks apart), calls an artillery
          shell on an enemy champion his team is hitting within r_range, else any within r_range: a 1-tick lob marks
          the spot (the warning circle and the falling bolt as `ViewEffect`s on the point, never turned) and r_delay
          ticks later the blast hits round it (r_r): r_dmg + r_ap% AP, r_ramp more for every shell of this channel
          that hit a champion before (League's ramp damage). r_n shells, then the channel ends.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_xerath.data_champion")
ID = "league_xerath"
FX = "asset/league/effects/league_xerath_fx"
BIG = "asset/league/effects/league_xerath_big"

P = {
    # stats (Magician base: attack 80 +6, magic power 40 +20, hp 900 +100, defence 20, mr 20, move 900, range 60000,
    # attack cooldown 90); League's Xerath is the artillery mage: a long range, little health, slow on his feet
    "hp": 860, "hp_g": 95, "atk": 78, "atk_g": 6, "mp": 42, "mp_g": 21, "def": 18, "def_g": 7, "mr": 20, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    # attack (League 525 range)
    "atk_range": 55000, "atk_dur": 28, "atk_cd": 90, "atk_st": 10, "orb_speed": 4500, "orb_y": -2000,
    # passive Mana Surge (League: every 16 s, -3.5 s per kill)
    "p_step": 210, "p_dmg": 40, "p_ap": 40, "p_cdr": 30, "k_hold": 40, "k_read": 4,
    # skill: Q Arcanopulse (League: 1.5 s charge, 750 -> 1450 range, width 145, 70-230 + 85% AP, cd 9-5 s)
    "q_cd": 330, "q_range": 100000, "q_full_t": 54, "q_quick_t": 22, "q_rec": 10, "q_aim_f": 140000,
    "q_reach_f": 150000, "q_reach_q": 95000, "q_speed": 15000, "q_rad": 7000, "q_y": -2000,
    "q_dmg": 95, "q_ap": 75, "q_quick": 65,
    # skill2: E Shocking Orb (League: 1125 range at 1400/s, width 60, 80-240 + 45% AP, stun 0.75-2.25 s, cd 13.5-11 s)
    # -> W Eye of Destruction (League: 0.5 s delay, radius 275 / centre ~100, 60-200 + 60% AP, centre x1.667,
    # slow 25% / centre 60-80% decaying over 2.5 s, cd 14-9 s)
    "c_cd": 600, "c_range": 95000, "c_dur": 30, "c_st": 10,
    "e_speed": 4000, "e_reach": 110000, "e_rad": 5000, "e_y": -2000, "e_dmg": 60, "e_ap": 45,
    "e_band1": 9, "e_band2": 18, "e_stun1": 45, "e_stun2": 80, "e_stun3": 120, "e_fall": 30,
    "w_delay": 30, "w_r_out": 26000, "w_r_in": 11000, "w_dmg": 60, "w_ap": 50, "w_mid": 67,
    "w_slow": 25, "w_slow_mid": 35, "w_slow_t": 150,
    # ult: R Rite of the Arcane (League: 5000 range, 3-5 shells 0.6 s apart, radius 200, 200-300 + 45% AP, ramp
    # +25-35 per champion hit, cd 130/115/100 s)
    "r_cd": 3000, "r_range": 220000, "r_deploy": 30, "r_win": 330, "r_poll": 6, "r_gap": 54, "r_n": 4,
    "r_delay": 36, "r_r": 18000, "r_dmg": 120, "r_ap": 45, "r_ramp": 20, "r_shot_t": 14,
    # his spoken lines: one every vo_gap ticks at most
    "vo_gap": 600,
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
    return {"type": "Combine", "effects": list(effects)}


NONE = {"type": "Combine", "effects": []}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields},
            "only_to_enemy": False}


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


def unanim(*names):
    return [{"type": "RemoveCasterAnimation", "name": x} for x in names]


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lob(name, end):
    """A hidden 1-tick lob: it lands on the unit's spot the tick it is fired; `end` runs on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000, "shape": circle(1000),
            "range_effect_name": "", "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


WAIT = ("p_a", "p_b", "p_c", "p_d")      # the passive's wait, shortest first


def build(p):
    # ------------------------------------------------------------------ passive: Mana Surge
    def ready(yes, no):
        """`yes` when none of the wait flags is left."""
        e = yes
        for w in reversed(WAIT):
            e = sw(w, no, e)
        return e

    # a kill takes the longest wait flag left: the next surge comes p_step ticks sooner
    # (built shortest-first, so the outermost check is the longest flag)
    shorten = NONE
    for w in WAIT:
        shorten = sw(w, combine(*rm(w)), shorten)

    def kill_check(src):
        """On a hit unit, around its damage: the flag before, the living target's clear after, the read on him later."""
        k = f"k_{src}"
        return (refresh(k, p["k_hold"]),
                combine(casted(3, 1, *rm(k)), on_me(delayed(p["k_read"], sw(k, combine(*rm(k), shorten))))))

    # ------------------------------------------------------------------ attack: the orb (a surge when ready)
    ka_set, ka_read = kill_check("a")
    orb = homing("a_orb", p["orb_speed"], p["orb_y"], "Enemy",
                 [ka_set, attack(0, 100), view("a_hit"), tsfx("a_hit"), ka_read])
    cut = flag("p_cut", 2, skill_cooldown_mult=p["p_cdr"], ult_cooldown_mult=-p["p_cdr"])
    surge_orb = homing("a_orb_p", p["orb_speed"], p["orb_y"], "Enemy",
                       [ka_set, attack(0, 100), ap(p["p_dmg"], p["p_ap"]), view("p_hit"), tsfx("p_hit"), ka_read,
                        combine(*rm("p_cut"), cut)])
    surge = combine(*[flag(w, p["p_step"] * (i + 1)) for i, w in enumerate(WAIT)], cview("p_surge"), sfx("p_surge"),
                    surge_orb)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_cast"), cview("a_flash"), ready(surge, orb)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Arcanopulse
    def beam(full):
        scale = 100 if full else p["q_quick"]
        reach = p["q_reach_f"] if full else p["q_reach_q"]
        hit = [ap(p["q_dmg"] * scale // 100, p["q_ap"] * scale // 100), view("q_hit"), tsfx("q_hit")]
        return line("q_beam" if full else "q_beam_s", p["q_speed"], reach, p["q_rad"], p["q_y"], "EnemyWithoutTower",
                    True, hit)

    def release(full):
        aim = (p["q_reach_f"] if full else p["q_reach_q"]) - 10000
        tag = "q_go_f" if full else "q_go_q"
        fire = combine(cview("q_fire"), sfx("q_fire"))
        return combine(*rm(tag), fire, pick(aim, "EnemyChampion", flag(tag, 1), beam(full)), sw(tag, NONE, beam(full)))

    full = combine(anim("skill", p["q_full_t"] + p["q_rec"]), cview("q_charge"), sfx("q_charge"), voice("vo_q", p),
                   delayed(p["q_full_t"], release(True)))
    quick = combine(anim("skill_quick", p["q_quick_t"] + p["q_rec"]), cview("q_charge_s"), sfx("q_charge"),
                    delayed(p["q_quick_t"], release(False)))
    skill = action("skill", 3, p["q_cd"], 1, p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(*rm("q_full"), pick(p["q_aim_f"], "EnemyChampion", flag("q_full", 1)),
                           sw("q_full", full, quick)))

    # ------------------------------------------------------------------ skill2: E Shocking Orb -> W Eye of Destruction
    def stun(t):
        return combine({"type": "Stun", "duration": t}, buff("e_stun", t))

    ke_set, ke_read = kill_check("e")
    e_hit = [ke_set, ap(p["e_dmg"], p["e_ap"]),
             sw("e_d1", stun(p["e_stun1"]), sw("e_d2", stun(p["e_stun2"]), stun(p["e_stun3"]))),
             view("e_hit"), tsfx("e_hit"), ke_read]
    e_orb = line("e_orb", p["e_speed"], p["e_reach"], p["e_rad"], p["e_y"], "EnemyWithoutTower", False, e_hit)

    w_t = p["w_delay"] + 1
    mid = p["w_mid"]
    eye = lob("w_lob", [
        view("w_mark"), sfx("w_cast"),
        zone("w_blast", p["w_r_out"], w_t, w_t, "EnemyWithoutTower",
             [ap(p["w_dmg"], p["w_ap"]), buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_hit"),
              tsfx("w_hit")]),
        zone("w_core", p["w_r_in"], w_t, w_t, "EnemyWithoutTower",
             [ap(p["w_dmg"] * mid // 100, p["w_ap"] * mid // 100),
              buff("w_slow2", p["w_slow_t"], move_speed_mult=-p["w_slow_mid"])]),
        delayed(p["w_delay"] - 1, view("w_blast"), sfx("w_blast"))])
    e_twin = line("e_twin", p["e_speed"], p["e_reach"], p["e_rad"], p["e_y"], "EnemyChampion", False,
                  [refresh("w_on", p["e_fall"] + 10), delayed(1, eye)])
    skill2 = action("skill2", p["c_dur"], p["c_cd"], p["c_st"], p["c_range"], "Targeting", "EnemyWithoutTower", combine(
        *rm("w_on"), flag("e_d1", p["e_band1"]), flag("e_d2", p["e_band2"]),
        cview("e_cast"), sfx("e_cast"), voice("vo_e", p), e_orb, e_twin,
        delayed(p["e_fall"], sw("w_on", NONE, eye))))

    # ------------------------------------------------------------------ ult: R Rite of the Arcane
    shots = [f"r_s{i}" for i in range(1, p["r_n"])]
    hits = [f"r_h{i}" for i in range(1, p["r_n"])]
    stop = combine(*rm("r_chan", "r_wait", *shots), *unanim("ult", "ult_loop", "ult_shot"), cview("r_end"),
                   sfx("r_end"))

    def blast_damage():
        e = ap(p["r_dmg"], p["r_ap"])
        for k, h in enumerate(hits, 1):
            pct = 100 + p["r_ramp"] * k
            e = sw(h, ap(p["r_dmg"] * pct // 100, p["r_ap"] * pct // 100), e) if k == 1 else \
                sw(h, ap(p["r_dmg"] * pct // 100, p["r_ap"] * pct // 100), e)
        # the outermost check must be the highest rung
        return e

    def climb_hits():
        e = flag(hits[0], p["r_win"] + p["r_deploy"])
        for k in range(1, len(hits)):
            e = sw(hits[k - 1], combine(flag(hits[k], p["r_win"] + p["r_deploy"])), e)
        return sw(hits[-1], NONE, e)

    r_t = p["r_delay"] + 1
    shell = lob("r_lob", [
        view("r_mark"), sfx("r_shot"),
        zone("r_blast", p["r_r"], r_t, r_t, "EnemyWithoutTower",
             [blast_damage(), view("r_hit"), tsfx("r_hit")]),
        # the champion twin climbs the ramp for the shells after this one
        zone("r_blast_c", p["r_r"], r_t, r_t, "EnemyChampion", [refresh("r_hc", 2)]),
        delayed(p["r_delay"] + 1, on_me(sw("r_hc", climb_hits()))),
        delayed(p["r_delay"] - 8, view("r_bolt"), sfx("r_blast"))])

    def count():
        """One more shell: the count on him, the last one ends the channel."""
        e = flag(shots[0], p["r_win"] + p["r_deploy"])
        for k in range(1, len(shots)):
            e = sw(shots[k - 1], flag(shots[k], p["r_win"] + p["r_deploy"]), e)
        return sw(shots[-1], combine(*rm("r_chan"), delayed(p["r_shot_t"], stop)), e)

    def fire():
        go = combine(refresh("r_wait", p["r_gap"]), anim("ult_shot", p["r_shot_t"]), cview("r_cast_shot"),
                     delayed(p["r_shot_t"], sw("r_chan", anim("ult_loop", p["r_win"]))), count())
        return combine(*rm("r_go"),
                       pick(p["r_range"], "EnemyChampionRecentlyAttacked", flag("r_go", 1), shell),
                       sw("r_go", NONE, pick(p["r_range"], "EnemyChampion", flag("r_go", 1), shell)),
                       sw("r_go", go))

    poll = casted(p["r_win"], p["r_poll"],
                  sw("r_chan", pick(1, "AllyChampionInCC", stop)),
                  sw("r_chan", sw("r_wait", NONE, fire())))
    end = p["r_deploy"] + p["r_win"]
    ult = action("ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(
        *rm("r_chan", "r_wait", "r_go", "r_hc", *shots, *hits), flag("r_chan", end),
        anim("ult", p["r_deploy"]), cview("r_rise"), sfx("r_cast"), voice("vo_r", p),
        on_me(delayed(p["r_deploy"], sw("r_chan", combine(anim("ult_loop", p["r_win"]), poll))),
              delayed(end, sw("r_chan", stop)))))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring)
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    # the eye and the shells have no zone views (a zone's view is turned to the cast: upside down on the red side);
    # their pictures play as ViewEffects on the landing point, unturned
    views_p = [P_("a_orb"), P_("a_orb_p"), P_("q_beam"), P_("q_beam_s"), P_("e_orb")]
    views_e = [E("a_flash", FX, 2, **LATE), E("a_hit", FX, 2), E("p_surge", FX, 2, **LATE), E("p_hit", FX, 2),
               E("q_charge"), E("q_charge_s"), E("q_fire", FX, 2, **LATE), E("q_hit", FX, 2),
               E("e_cast", FX, 2, **LATE), E("e_hit", FX, 2),
               E("w_mark", BIG, -1, False), E("w_blast", BIG, 2, False), E("w_hit", FX, 2),
               E("r_rise", BIG, 2), E("r_cast_shot", FX, 2, **LATE), E("r_end", FX, 2, **LATE),
               E("r_mark", BIG, -1, False), E("r_bolt", BIG, 2, False), E("r_hit", FX, 2)]
    views_b = [B_("e_stun", FX, 3), B_("w_slow", FX, -1), B_("r_chan", BIG, -1)]
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
