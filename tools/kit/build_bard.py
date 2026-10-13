"""Build league_bard.data_champion (support, Util, ranged AP) from the parameters P.

    python tools/kit/build_bard.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-13: Q stuns only with a second target, W + E escape portal, R a true stasis for
everyone in the zone):
  attack  Bard's star bolt (homing, physical) and Traveler's Call (passive): every p_cd ticks his next attack also
          sends a Meep - a homing bolt that bursts on the target (p_r round it): p_dmg + p_ap% AP magic damage and a
          p_slow% slow for p_slow_t ticks to every enemy in the burst (League: 35 + 40% AP, slow, cone behind the
          target, a Meep every 8 s and more with chimes). The chimes themselves are left out: nothing spawns on the
          map and death clears a mod's buffs (an add-on can count them later).
  skill   Q Cosmic Binding: a `Targeting` cast on `EnemyWithoutTower` fires the bolt along the line to the target
          (league_missfortune Q's twin): the first unit it touches takes q_dmg + q_ap% AP magic damage and a q_slow%
          slow for q_slow_t ticks; a wide twin with no picture finds the next enemy behind it while q_win ticks last
          (q_speed x q_win units on): that one takes the damage and a q_stun-tick stun, and so does the first,
          q_win + 1 ticks after its hit (a Delayed queued on it reads the `q_two` flag the second hit set). No
          second unit: the slow only (no walls in TFM2 - League also stuns against terrain).
  skill2  W Caretaker's Shrine + E Magical Journey: a `Targeting` cast on `EnemyChampion` (w_range), so it comes in
          fights only (league_janna E's way). With E off its own cooldown (`e_cd`, e_cd_t ticks) and Bard dived -
          two enemy champions within e_near or one within e_close - E opens the door: he travels e_speed x e_tick
          units straight away from the nearest enemy champion (MoveBack), every allied champion within e_ride of the
          door is pulled through after him (a Grab that ends on him) and they all get e_ms% move speed for e_ms_t
          ticks. The door goes through the jungle's rocks: forced moves (MoveBack, Grab) never stop at the map's
          walls (SDK simulation 2026-10-13: 78 of 159 long test trips crossed rock, none was cut short; an exit inside
          a rock is walked out of), and an `ignore_wall` buff over the trip (e_ghost) keeps it so should the game check
          walls on forced moves. Else W: a shrine thrown at an allied champion in crowd control, else at a random one within w_r,
          else at his feet: w_heal + w_ap% AP heal and w_ms% move speed for w_ms_t ticks.
  ult     R Tempered Fate, armed like league_lulu R: a 3-tick `None` cast on `EnemyChampion` (r_arm_range) arms
          r_armed for r_arm ticks; every attack, Q and W/E check it: an allied champion in crowd control within
          r_range with an enemy champion within r_r of him is frozen with them (the save), else a probe on a random
          enemy champion within r_range counts the champions within r_r of him: r_need enemies and no ally (Bard
          neither) -> the golden orb is lobbed there (r_travel ticks) and every unit in r_r but towers - enemies,
          allies, Bard - is banished for r_t ticks (League's stasis: untargetable, nothing it can do, nothing reaches
          it; the Banish plays r_lock on each for as long and r_free as it ends). Unused, the cooldown is refunded.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_bard.data_champion")
ID = "league_bard"
FX = "asset/league/effects/league_bard_fx"
BIG = "asset/league/effects/league_bard_big"

P = {
    # stats (the pack's ranged supports: Lulu/Janna hp 880-900 +80-90, atk 75-80 +6, ap 30 +15, def 20-22, mr 20-24;
    # Bard's League range 500 is a little short of theirs)
    "hp": 900, "hp_g": 90, "atk": 75, "atk_g": 6, "ap": 30, "ap_g": 15, "def": 22, "def_g": 7, "mr": 24, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 52000, "atk_dur": 24, "atk_cd": 90, "atk_st": 11, "a_speed": 5000, "a_y": -1000,
    # passive: Traveler's Call, the Meeps (League: 35 + 40% AP, 1 s slow 25-80%?, a Meep every 8 s)
    "p_cd": 240, "p_speed": 4500, "p_y": -3000, "p_r": 14000, "p_dmg": 35, "p_ap": 40, "p_slow": 25, "p_slow_t": 60,
    # skill: Q Cosmic Binding (League: 950 + 525 behind, speed 1500; 80-280 + 65% AP; slow 60% / stun 1-1.8 s;
    # cd 12-7 s)
    "q_cd": 420, "q_range": 65000, "q_dur": 24, "q_st": 10, "q_speed": 6000, "q_reach": 95000, "q_rad": 6000,
    "q_twin": 18000, "q_win": 9, "q_y": -1000, "q_dmg": 80, "q_ap": 65, "q_slow": 60, "q_slow_t": 72, "q_stun": 72,
    # skill2: W Caretaker's Shrine (League: heal 25-150 -> 50-237.5 + 30-90% AP, ms 17.5-32.5% 1.5 s, 2 charges /
    # 18 s) + E Magical Journey (League: 900 door, ally ms 33-50%, cd 22-16 s)
    "w_cd": 420, "w_range": 90000, "w_dur": 22, "w_st": 1, "w_lag": 9, "w_r": 50000, "w_speed": 4000, "w_y": -2000,
    "w_heal": 110, "w_ap": 50, "w_ms": 30, "w_ms_t": 90,
    "e_cd_t": 960, "e_near": 30000, "e_close": 15000, "e_wind": 9, "e_speed": 4000, "e_tick": 15, "e_ride": 25000,
    "e_pull": 5000, "e_pull_t": 40, "e_ghost": 1, "e_ms": 40, "e_ms_t": 120, "e_anim": 24,
    # ult: R Tempered Fate (League: 3400 range, radius 350, 0.5 s cast + flight, stasis 2.5 s; cd 110-80 s)
    "r_cd": 3600, "r_arm": 900, "r_arm_range": 90000, "r_range": 80000, "r_need": 2, "r_anim": 30, "r_travel": 24,
    "r_r": 26000, "r_t": 150,
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


def flat(node):
    """The tree with every Combine that sits straight in a Combine's, a Delayed's or a RandomTarget's `effects`
    spliced into that list (the same effects in the same order, fewer nodes for the game's per-tick copy)."""
    if isinstance(node, list):
        return [flat(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {k: flat(v) for k, v in node.items()}
    if out.get("type") in ("Combine", "Delayed", "RandomTarget"):
        eff = []
        for x in out["effects"]:
            if isinstance(x, dict) and x.get("type") == "Combine":
                eff.extend(x["effects"])
            else:
                eff.append(x)
        out["effects"] = eff
    return out


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def dur(tick):
    return tick if isinstance(tick, (str, dict)) else {"Time": {"tick": tick}}


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur(tick), **fields},
            "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": dur(tick), **fields}}


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


def heal(amount, ap, kind="Ally"):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": kind}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def splash(name, speed, rng, y, target, effects):
    return {"type": "TargetSplashProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def action(name, dur_, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur_, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ ult: R Tempered Fate (the armed check)
    def drop(name, *end, hit=(), target="EnemyChampion"):
        """A hidden one-tick lob onto the unit in hand (league_annie R): its end_effects start a zone on that spot,
        `hit` runs on the unit itself (a Delayed there is queued on him)."""
        return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000,
                "shape": circle(1000), "applied_target": target, "applied_effects": [T(e) for e in hit],
                "end_effects": list(end)}

    def zone(name, radius, target, effects):
        return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
                "applied_target": target, "applied_effects": [T(e) for e in effects]}

    stasis = zone("r_zone", p["r_r"], "BothWithoutTower",
                  [{"type": "Banish", "duration": p["r_t"], "lock_effect_name": n("r_lock"),
                    "end_effect_name": n("r_free")}, tsfx("r_lock")])

    def fire(target):
        """The golden orb lobbed onto the unit the check picked; the stasis where it lands."""
        return combine(*rm("r_armed"), flag("r_got", 1), anim("ult", p["r_anim"]), sfx("r_cast"), sfx("vo_r"),
                       {"type": "ParabolicProjectile", "name": n("r_orb"), "travel_time": p["r_travel"],
                        "range": 400000, "shape": circle(1000), "range_effect_name": n("r_mark"),
                        "applied_target": target, "applied_effects": [],
                        "end_effects": [view("r_dome"), sfx("r_land"), stasis]})

    # engage: a probe lob onto a random enemy champion in reach counts the enemy champions (r_n1 -> r_n2) and the
    # allied ones (r_a1, Bard too) within r_r of him; two ticks later, on him: r_need enemies and no ally -> fire.
    need = "r_n2" if p["r_need"] >= 2 else "r_n1"
    probe = drop("r_probe", zone("r_count", p["r_r"], "EnemyChampion", [sw("r_n1", flag("r_n2", 4), flag("r_n1", 4))]),
                 zone("r_allies", p["r_r"], "AllyChampion", [flag("r_a1", 4)]),
                 hit=[delayed(2, sw("r_armed", sw(need, sw("r_a1", NONE, fire("EnemyChampion")))))])
    # save: an allied champion in crowd control with an enemy champion beside him is frozen with them
    save = drop("r_sprobe", zone("r_scount", p["r_r"], "EnemyChampion", [flag("r_s1", 4)]), target="AllyChampion",
                hit=[delayed(2, sw("r_armed", sw("r_s1", fire("AllyChampion"))))])
    r_check = sw("r_armed", combine(
        *rm("r_got", "r_n1", "r_n2", "r_a1", "r_s1"), pick(p["r_range"], "AllyChampionInCC", save),
        pick(p["r_range"], "EnemyChampion", probe)))
    ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion", flat(combine(
        *rm("r_armed"), flag("r_armed", p["r_arm"]), r_check,
        delayed(p["r_arm"], sw("r_armed", combine(*rm("r_armed"), flag("r_refund", 3, ult_cooldown_mult=4900)))))),
        key="ult")

    # ------------------------------------------------------------------ attack + passive: the Meeps
    meep = splash("p_meep", p["p_speed"], p["p_r"], p["p_y"], "EnemyWithoutTower",
                  [magic(p["p_dmg"], p["p_ap"]), buff("p_slow", p["p_slow_t"], move_speed_mult=-p["p_slow"]),
                   view("p_hit"), tsfx("p_hit")])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", flat(combine(
        r_check, sfx("a_cast"),
        homing("a_bolt", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
        sw("p_cd", NONE, combine(flag("p_cd", p["p_cd"]), sfx("p_meep"), meep)))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Cosmic Binding
    first = sw("q_first", NONE, combine(
        flag("q_first", p["q_win"] + 30), flag("q_window", p["q_win"]), flag("q_wait", 1),
        magic(p["q_dmg"], p["q_ap"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
        view("q_hit"), tsfx("q_hit"),
        delayed(p["q_win"] + 1, sw("q_two", combine({"type": "Stun", "duration": p["q_stun"]}, view("q_bind"))))))
    second = sw("q_wait", NONE, sw("q_window", combine(
        *rm("q_window"), flag("q_two", p["q_win"] + 4),
        magic(p["q_dmg"], p["q_ap"]), {"type": "Stun", "duration": p["q_stun"]}, view("q_hit"), view("q_bind"),
        tsfx("q_bind"))))
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Targeting", "EnemyWithoutTower", flat(combine(
        r_check, *rm("q_first", "q_window", "q_two"), sfx("q_cast"), sfx("vo_q"),
        line("q_seek", p["q_speed"], p["q_reach"], p["q_twin"], p["q_y"], "EnemyWithoutTower", True, [second]),
        line("q_bolt", p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], "EnemyWithoutTower", True, [first]))))

    # ------------------------------------------------------------------ skill2: W Caretaker's Shrine + E Magical Journey
    def shrine_on(extra):
        return [heal(p["w_heal"], p["w_ap"]), buff("w_haste", p["w_ms_t"], move_speed_mult=p["w_ms"]),
                view("w_land"), *extra]

    def throw():
        return combine(flag("w_got", 1), homing("w_shrine", p["w_speed"], p["w_y"], "AllyChampion",
                                                shrine_on([tsfx("w_heal")])))

    w_self = around(1000, "AllyOnlySelf", [heal(p["w_heal"], p["w_ap"], "Caster"),
                                           buff("w_haste", p["w_ms_t"], move_speed_mult=p["w_ms"]),
                                           view("w_land"), sfx("w_heal")])
    w = delayed(p["w_lag"], *rm("w_got"), sfx("w_cast"), sfx("vo_w"), pick(p["w_r"], "AllyChampionInCC", throw()),
                sw("w_got", NONE, combine(pick(p["w_r"], "AllyNotSelf", throw()), sw("w_got", NONE, w_self))))

    e = combine(
        flag("e_cd", p["e_cd_t"]), *([flag("e_ghost", p["e_wind"] + p["e_tick"] + 2, ignore_wall=True)] if p["e_ghost"] else []),
        anim("skill2_e", p["e_anim"]), sfx("e_cast"), sfx("vo_e"), cview("e_door"),
        around(p["e_ride"], "AllyNotSelf", [buff("e_haste", p["e_ms_t"], move_speed_mult=p["e_ms"]),
                                            *([buff("e_ghost", p["e_wind"] + p["e_tick"] + p["e_pull_t"],
                                                    ignore_wall=True)] if p["e_ghost"] else []),
                                            delayed(p["e_wind"] + p["e_tick"], {"type": "Grab", "speed": p["e_pull"]},
                                                    view("e_ride"))]),
        pick(p["e_near"], "EnemyChampion", delayed(p["e_wind"], {"type": "MoveBack", "speed": p["e_speed"],
                                                                 "tick": p["e_tick"]})),
        around(1000, "AllyOnlySelf", [buff("e_haste", p["e_ms_t"], move_speed_mult=p["e_ms"])]),
        delayed(p["e_wind"] + p["e_tick"], cview("e_door_out"), sfx("e_out")))
    # dived? two enemy champions within e_near (the n1 -> n2 ladder) or one within e_close
    count = combine(*rm("e_n1", "e_n2"),
                    around(p["e_near"], "EnemyChampion", [sw("e_n1", flag("e_n2", 1), flag("e_n1", 1))]),
                    pick(p["e_close"], "EnemyChampion", flag("e_n2", 1)))
    skill2 = action("skill2", p["w_dur"], p["w_cd"], p["w_st"], p["w_range"], "Targeting", "EnemyChampion", flat(combine(
        r_check, sw("e_cd", w, combine(count, sw("e_n2", e, w), *rm("e_n1", "e_n2"))))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                      "repeat": True, "z": z}
    views_p = [P_("a_bolt"), P_("p_meep"), P_("q_bolt"), P_("w_shrine"), P_("r_orb", BIG)]
    views_e = [E("a_hit", FX, 2), E("p_hit", FX, 2), E("q_hit", FX, 2), E("q_bind", FX, 2), E("w_land", FX, 2),
               E("e_door", BIG, -1, False), E("e_door_out", BIG, -1), E("e_ride", FX, 2),
               E("r_mark", BIG, -1, False), E("r_dome", BIG, 2, False), E("r_lock", BIG, 2, False),
               E("r_free", BIG, 2, False)]
    views_b = [P_("p_slow", FX, 1), P_("q_slow", FX, 1), P_("w_haste", FX, 1), P_("e_haste", FX, 1)]
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Range", "CC", "Heal"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
        p[k] = v if isinstance(p[k], str) else type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
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
