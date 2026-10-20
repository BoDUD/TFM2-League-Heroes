"""Build league_zyra.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_zyra.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: mid, layout A, with the add-on). TFM2 has three active slots: Deadly Spines (Q) is
`skill`, Grasping Roots (E) `skill2`, Stranglethorns (R) the `ult`. Rampant Growth (W) and the passive Garden of Thorns
have no slot: every Q and E plants a seed first and grows it at once (League's W -> Q / W -> E), so each Q leaves a
Thorn Spitter and each E a Vine Lasher where it lands.
  plants  Data has no summons: a plant is a zone (`RangePeriodProjectile`) on its spot that strikes every t_per ticks
          for t_life ticks, its picture one `ViewEffect` whose tag lasts the plant's life. A zone hits every enemy in
          it; a plant strikes one: the first enemy its period reaches lays a 1-tick caster flag (`t_shot` / `v_shot`)
          the others read, so each plant strikes one enemy a period (two plants of a kind striking on the same tick
          share the flag: rare).
          Thorn Spitter (荆棘喷射者, Q): reach t_r, t_dmg + t_ratio% AP magic damage a period.
          Vine Lasher (藤蔓鞭击者, E): reach v_r, v_dmg + v_ratio% AP and a v_slow% slow for v_slow_t ticks.
          Stranglethorns enrages them: for r_rage ticks after R every plant strike deals rage% of its damage.
  attack  a thorn seed (100% AD), homing on `Enemy` (towers too), released on a_rel.
  skill   Q Deadly Spines (致命棘刺), `Targeting` on `EnemyWithoutTower` (q_range): q_delay ticks after the release the
          spines burst on the target's spot (radius q_r): q_dmg + q_ratio% AP; a Thorn Spitter grows there.
  skill2  E Grasping Roots (缠绕之根), `Targeting` on `EnemyWithoutTower` (e_range): vines run along the ground straight
          at the target and on (penetrating, e_len): e_dmg + e_ratio% AP and a root of e_root ticks on every enemy on
          the line; a Vine Lasher grows on the target's spot when the vines reach it (a hidden lob of e_grow ticks).
  ult     R Stranglethorns (绞杀之藤), `Targeting` on `EnemyChampion` (r_range): a thicket bursts on the champion's
          spot (radius r_r): r_dmg + r_ratio% AP; r_knock ticks later it snaps shut and knocks up (`Airborne`
          r_air ticks) every enemy still in it. Her plants are enraged for r_rage ticks.
The add-on copy (--native, addons/league_zyra): see the add-on's README.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_zyra.data_champion")
ID = "league_zyra"
FX = "asset/league/effects/league_zyra_fx"
BIG = "asset/league/effects/league_zyra_big"

# League units x 100 = ours (attack range 575 -> 55000 like every mid); radii count the unit's collision radius
# (~15000) on top. Timings from the frames (tools/art/rig_zyra.py, poses.json): every action releases on its frame 3 -
# the attack's throw at 160 ms (a_rel 10), Q's fling 160 ms (q_rel 10), E's slam 160 ms (e_rel 10), R's summon 170 ms
# (r_rel 10); each action as long as its frames (27 / 33 / 33 / 37 ticks). Numbers = the 10-min classic-SDK simulations (mid lane 2 against
# pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both sides, 2026-10-20): the draft (plants
# 25 + 15% for 6 s, Q 90 + 60%, E 80 + 50%) +2.10 (8 seeds); single nerfs (plants 18 + 12%, Q / E -15, plants 4 s, hp 820
# with R 150 + 60%) +1.95..+2.56 and a shorter root +2.99 - inside the noise (about +-0.7 a batch); all the damage and the
# plants cut together (plants 18 + 12% for 4 s, Q 75 + 50%, E 65 + 40%) +0.65 / +0.78 (8 / 16 seeds); plants 20 + 12%
# for 5 s, Q 80 + 55%, E 70 + 45% +1.09 (16 seeds; with Q 85 +2.40 - the noise again) = P.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Zyra:
    # 574 +93 hp, 29 armour, 30 mr, 340 move, 575 range, attack speed 0.681
    "hp": 900, "hp_g": 95, "atk": 70, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 86, "a_rel": 10, "a_speed": 4500,
    # plants (League: Thorn Spitter 575 range, Vine Lasher 400 range with a 30% slow for 2 s; 20-100 by level
    # + 15% AP a strike, ~1 strike a second, 8 s)
    "t_life": 300, "t_per": 60, "t_first": 20, "t_r": 50000, "t_dmg": 20, "t_ratio": 12,
    "v_life": 300, "v_per": 60, "v_first": 20, "v_r": 32000, "v_dmg": 20, "v_ratio": 12, "v_slow": 30, "v_slow_t": 60,
    "rage": 150,
    # Q Deadly Spines (League: 800 range, 60-200 +60% AP, burst after 0.625 s, cd 7-5)
    "q_cd": 420, "q_range": 80000, "q_dur": 33, "q_rel": 10, "q_delay": 30, "q_r": 22000, "q_dmg": 80, "q_ratio": 55,
    # E Grasping Roots (League: 1100 range, 60-200 +50% AP, root 1-2 s, speed 1150, cd 12)
    "e_cd": 660, "e_range": 90000, "e_dur": 33, "e_rel": 10, "e_speed": 2000, "e_len": 105000, "e_w": 7000,
    "e_dmg": 70, "e_ratio": 45, "e_root": 75, "e_grow": 25,
    # R Stranglethorns (League: 700 range, radius 575, 180-350 +70% AP, knock-up 1 s after 2 s, cd 110-90)
    "r_cd": 2100, "r_range": 70000, "r_dur": 37, "r_rel": 10, "r_r": 32000, "r_dmg": 180, "r_ratio": 70,
    "r_knock": 120, "r_air": 60, "r_rage": 300,
    "vo_gap": 600,
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


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end=(), penetrate=False, y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": penetrate, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def lob(name, travel, end):
    """A hidden 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, life, period, first, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": life, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    def strike(shot, dmg, ratio, extra):
        """One plant strike on the enemy its period reached first (`shot` held 1 tick); enraged after R."""
        hit = lambda k: [ap(dmg * k // 100, ratio * k // 100), *extra]
        return sw(shot, NONE, combine(flag(shot, 1), sw("rage", combine(*hit(p["rage"])), combine(*hit(100)))))

    # ------------------------------------------------------------------ plants
    spitter = [view("t_plant"), sfx("t_grow"),
               field("t_spit", p["t_r"], p["t_life"], p["t_per"], p["t_first"],
                     [strike("t_shot", p["t_dmg"], p["t_ratio"], [view("t_hit"), tsfx("t_hit")])])]
    lasher = [view("v_plant"), sfx("v_grow"),
              field("v_lash", p["v_r"], p["v_life"], p["v_per"], p["v_first"],
                    [strike("v_shot", p["v_dmg"], p["v_ratio"],
                            [buff("v_slow", p["v_slow_t"], move_speed_mult=-p["v_slow"]), view("v_hit"),
                             tsfx("v_hit")])])]

    # ------------------------------------------------------------------ attack: the thorn seed
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), delayed(p["a_rel"] - 1, alive(
                          sfx("a"), homing("a_seed", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")],
                                           p["a_speed"])))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Deadly Spines + a Thorn Spitter
    burst = [view("q_burst"), sfx("q_burst"),
             zone("q_spines", p["q_r"], [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")]), *spitter]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap), sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive(lob("q_seed", p["q_delay"], burst)))))

    # ------------------------------------------------------------------ skill2: E Grasping Roots + a Vine Lasher
    rooted = [ap(p["e_dmg"], p["e_ratio"]), {"type": "Bind", "duration": p["e_root"]},
              buff("e_bound", p["e_root"]), tsfx("e_hit")]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(
                                line("e_roots", p["e_speed"], p["e_len"], p["e_w"], "EnemyWithoutTower", rooted,
                                     penetrate=True),
                                lob("e_seed", p["e_grow"], lasher)))))

    # ------------------------------------------------------------------ ult: R Stranglethorns
    thicket = [view("r_thicket"), sfx("r_land"),
               zone("r_burst", p["r_r"], [ap(p["r_dmg"], p["r_ratio"]), view("r_hit")]),
               delayed(p["r_knock"], sfx("r_knock"),
                       zone("r_snap", p["r_r"], [{"type": "Airborne", "duration": p["r_air"]}, view("r_knock")]))]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), sfx("r"), voice("vo_r", p),
                         delayed(p["r_rel"] - 1, alive(refresh("rage", p["r_rage"]), sfx("r_rage"), lob("r_seed", 1, thicket)))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    views_p = [Pj("a_seed"), Pj("e_roots")]
    views_e = [E("a_hit"), E("q_burst", BIG, -1, False), E("q_hit"), E("t_plant", BIG, 0, False), E("t_hit"),
               E("v_plant", BIG, 0, False), E("v_hit"), E("r_thicket", BIG, -1, False), E("r_hit"), E("r_knock")]
    views_b = [B_("e_bound", FX, 3), B_("v_slow", FX, -1)]
    extra = {}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"], **extra,
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
