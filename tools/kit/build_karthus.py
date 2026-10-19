"""Build league_karthus.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_karthus.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: mid, layout A, Death Defied in the add-on). TFM2 has three active slots: Lay Waste
(Q) is `skill`, Defile (E) `skill2`, Requiem (R) the `ult`; Wall of Pain (W) has no slot - it rides his attack.
  passive Death Defied (死亡契约): League's spirit form needs his health read - the add-on (native=1) does it.
  attack  a dark bolt (100% AD), homing on `Enemy` (towers too), released on a_rel.
  W       Wall of Pain (痛苦之墙), in the attack: every w_cd ticks, with an enemy champion within w_r, his attack is
          `attack_w` and lays the wall where that champion stands (a `RandomTarget` puts the zone on it): an upright
          screen (`Rect`, w_hw across x w_hh up and down: the map's axes, a zone's shape is never turned) for w_t
          ticks; every enemy in it is slowed w_slow% (w_slow_t ticks after he leaves it) and loses w_mr% magic
          resistance for w_mr_t (League: 40-60% slow decaying over 5 s, 15% magic resistance, the wall 5 s, cd 15 s).
  skill   Q Lay Waste (荒芜), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): a hidden lob to where
          the target stands (its mark on the ground the whole flight), q_delay ticks later the blast (radius q_r): q_dmg + q_ratio% AP, and the same again
          when it hit only one enemy (League: isolated targets take double). The count: every unit hit adds the caster
          flag q_c1, or q_c2 when q_c1 is already on; a tick later the hit unit takes the bonus if q_c2 is off.
  skill2  E Defile (亵渎), `Targeting` on `EnemyWithoutTower` (e_cast): for e_t ticks souls whirl round him and every
          e_per ticks each enemy within e_r takes e_dmg + e_ratio% AP (League: 30-110 + 20% AP a second, a toggle that
          drains mana; here e_cd).
  ult     R Requiem (安魂曲), `Targeting` on `EnemyChampionRecentlyAttacked` anywhere (r_range: his team is fighting
          someone): he channels r_ch ticks (spell4 + spell4_loop), crowd control on him (checked every r_brk ticks)
          breaks it; then every enemy champion on the map takes r_dmg + r_ratio% AP (League: 200-500 + 75% AP after 3 s).
The add-on copy (--native, addons/league_karthus): the passive league_karthus:death_defied - a lethal blow leaves him
at 1 health as a spirit for p_t ticks, untargetable, casting on, then he falls (the kill to whoever struck it).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_karthus.data_champion")
ID = "league_karthus"
FX = "asset/league/effects/league_karthus_fx"
BIG = "asset/league/effects/league_karthus_big"

# League units x 100 = ours (attack range 450 -> 45000; mids sit at 55000, his bolt reaches 50000); radii count the
# unit's collision radius (~15000) on top. Timings: drafts until the strips set them (tools/art/rig_karthus.py).
# Numbers = the 10-min classic-SDK simulations (mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and
# white_mage, three lineups, both sides, 8 seeds, 2026-10-20): the draft with Q and W as zones started straight from the
# action (they hit nothing) -4.72; on hidden lobs (Q 55 + 35%, R 250 + 75% every 60 s) +2.89 (league_zoe +1.30 the
# same day); Q 45 + 30% +2.22; R 200 every 70 s +2.23; both +1.46 = P.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Karthus:
    # 620 +110 hp, 21 armour, 30 mr, 335 move, 450 range, attack speed 0.625
    "hp": 880, "hp_g": 95, "atk": 76, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 50000, "atk_dur": 27, "atk_cd": 92, "a_rel": 10, "a_speed": 4500,
    # W Wall of Pain in the attack
    "w_cd": 720, "w_r": 60000, "w_dur": 27, "w_rel": 10, "w_t": 300, "w_hw": 3000, "w_hh": 30000, "w_slow": 40,
    "w_slow_t": 45, "w_mr": 20, "w_mr_t": 240,
    # Q Lay Waste (League: 45-205 + 35% AP, x2 on one target, 0.53 s delay, radius 160 (+ 0.2 s cast), cd 1 s)
    "q_cd": 150, "q_range": 80000, "q_dur": 24, "q_rel": 8, "q_delay": 32, "q_r": 15000, "q_dmg": 45, "q_ratio": 30,
    # E Defile (League: radius 550, 30-110 + 20% AP a second)
    "e_cd": 600, "e_cast": 40000, "e_dur": 24, "e_rel": 8, "e_t": 300, "e_per": 15, "e_r": 30000, "e_dmg": 10,
    "e_ratio": 5,
    # R Requiem (League: 3 s channel, 200-500 + 75% AP to every enemy champion, cd 200-160 s)
    "r_cd": 4200, "r_range": 960000, "r_rel": 2, "r_ch": 180, "r_brk": 15, "r_dmg": 200, "r_ratio": 75,
    "vo_gap": 600,
    # the add-on (addons/league_karthus): the spirit lasts p_t ticks
    "p_t": 420,
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
    return {"type": "Combine", "effects": list(effects)}


NONE = {"type": "Combine", "effects": []}


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def around(r, target, *effects):
    return {"type": "RangeEffect", "shape": circle(r), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (its estimate follows the flags he has while it reads, so a hit
    under alive() reads as nothing; league_zoe's decoy): a flag he never has while it reads; on the cast the flag is
    up and the hit is skipped."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def blast(name, radius, delay, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": delay,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, seen=""):
    """A hidden lob: it lands where its target stood when it left, `travel` ticks later; `end` runs on that point (a
    zone started straight from the action lands nowhere: league_brand's / league_cassiopeia's way); `seen` = a picture
    played on the landing point the whole flight."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": "EnemyWithoutTower",
            "applied_effects": [], "end_effects": list(end)}


def zone(name, shape, tick, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": shape, "tick": tick, "period": 3,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ attack: the dark bolt + W Wall of Pain
    bolt = combine(sfx("a"), homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"]))
    plain = delayed(p["a_rel"] - 1, alive(bolt))
    pain = [buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
            buff("w_shred", p["w_mr_t"], magic_resistance_mult=-p["w_mr"])]
    wall = lob("w_lob", 1, [view("w_wall"), sfx("w"),
                            zone("w_wall", {"Rect": {"width": p["w_hw"], "height": p["w_hh"]}}, p["w_t"], pain)])
    # the wall goes up on an enemy champion near him; none near, the attack stays plain and W stays ready
    lay = combine(pick(p["w_r"], "EnemyChampion", flag("w_go", 1)),
                  sw("w_go", combine(*rm("w_go"), flag("w_cd", p["w_cd"]), anim("attack_w", p["w_dur"]),
                                     voice("vo_w", p), sfx("w_cast"),
                                     delayed(p["w_rel"] - 1, alive(bolt, pick(p["w_r"], "EnemyChampion", wall)))),
                     plain))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("w_cd", plain, lay)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Lay Waste
    count = sw("q_c1", flag("q_c2", 3), flag("q_c1", 3))
    lone = delayed(1, sw("q_c2", NONE, combine(ap(p["q_dmg"], p["q_ratio"]), view("q_lone"), tsfx("q_lone"))))
    burst = lob("q_lob", p["q_delay"], [view("q_boom"), sfx("q_boom"), blast(
        "q_blast", p["q_r"], 1, "EnemyWithoutTower", [count, ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit"),
                                                     lone])], seen="q_mark")
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap), sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive(*rm("q_c1", "q_c2"), sfx("q_mark"), burst))))

    # ------------------------------------------------------------------ skill2: E Defile
    pulses = [delayed(p["e_rel"] - 1 + k, alive(around(p["e_r"], "EnemyWithoutTower", ap(p["e_dmg"], p["e_ratio"]),
                                                        view("e_hit"))))
              for k in range(p["e_per"], p["e_t"] + 1, p["e_per"])]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_cast"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"] * 4, p["e_ratio"] * 4, ap), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(refresh("e_on", p["e_t"]), sfx("e_loop"))), *pulses))

    # ------------------------------------------------------------------ ult: R Requiem
    brk = [delayed(k, pick(1, "AllyChampionInCC", *rm("r_ch"), {"type": "RemoveCasterAnimation", "name": "ult"}))
           for k in range(p["r_brk"], p["r_ch"], p["r_brk"])]
    toll = around(p["r_range"], "EnemyChampion", ap(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit"))
    ult = action("ult", p["r_ch"] + 6, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), refresh("r_ch", p["r_ch"] + 2), anim("ult", p["r_ch"]),
                         sfx("r"), voice("vo_r", p), delayed(p["r_rel"], alive(cview("r_cast"))), *brk,
                         delayed(p["r_ch"] - 1, alive(sw("r_ch", combine(*rm("r_ch"), sfx("r_boom"), toll))))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    views_p = [Pj("a_bolt")]       # round; the zones carry no picture (an upright one would turn with the cast)
    views_e = [E("a_hit"), E("q_mark", BIG, -1, False), E("q_boom", BIG, 2, False), E("q_hit"), E("q_lone"), E("e_hit"),
               E("w_wall", BIG, -1, False), E("r_cast", BIG, 3, True), E("r_hit")]
    views_b = [B_("e_on", BIG, -1), B_("w_slow", FX, 3), B_("w_shred", FX, 3)]
    extra = {}
    if native:          # the add-on's spirit
        views_b.append(B_("p_spirit", BIG, 3))
        extra["passive"] = {"passive_ref": "league_karthus:death_defied", "params": {"p_t": p["p_t"]}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
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
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--native", action="store_true", help="the add-on's copy")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    if a.native:
        p["native"] = 1
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
