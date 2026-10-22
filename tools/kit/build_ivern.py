"""Build league_ivern.data_champion (jungle, Util: the Green Father) from the parameters P.

    python tools/kit/build_ivern.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-22: JUNGLE, layout A - E / Q / R, W folded into the passive; 「有连招要做连招」,
add-on 「需要就做」). TFM2 has three active slots: Triggerseed (E) is `skill`, Rootcaller (Q) `skill2`, Daisy! (R) the
`ult`. He clears camps with the attack and both skills (`EnemyWithoutTower`); Friend of the Forest's camp blessing has
nothing to stand on in TFM2 (no camps to spare), so the passive is Brushmaker's.
  passive Brushmaker (揠苗助攻, W folded in): every E cast grows a brush round his feet (w_t ticks, radius w_r):
          the allied champions in it as it grows get w_atk% attack for its life (League: allies' attacks in his brush deal bonus magic damage),
          and while it stands (`w_in`, w_t ticks) his own attacks deal w_dmg + w_ratio% AP magic damage more.
  attack  A thrown seed (100% AD on `Enemy`, a homing seed a_seed).
  skill   E Triggerseed (种豆得瓜, cooldown flag `e_cd`): a `Targeting` cast on `EnemyWithoutTower` (e_range; a shield
          scores its full amount on anyone, so it is cast on an enemy and handed on - league_janna E's way). The
          allied champion nearest him within e_ally (`AllyNotSelf`) gets the seed: a shield e_sh + e_sh_r% AP for
          e_t ticks and, at e_t, the burst round it (an `AddCasted` on the ally lobs a one-tick hidden projectile onto
          it, league_tristana E's detonation): e_dmg + e_ratio% AP to the enemies within e_r, slowed e_slow% for
          e_slow_t. Nobody beside him - in the jungle, mostly - the seed is his own (League lets him shield himself).
  skill2  Q Rootcaller (根深敌固, cooldown flag `q_cd`): a `Targeting` cast on `EnemyWithoutTower` (q_range). A vine flies
          at the target (a homing projectile): q_dmg + q_ratio% AP and a q_root-tick root; the allied champions within
          q_ally of him get q_ms% move speed for q_ms_t (League: allies may dash to the rooted target; the add-on can
          make it a real dash).
  ult     R Daisy! (小菊！, the Tibbers way, champion-data section 7): a `Targeting` cast on `EnemyChampion` (r_range).
          Daisy drops on the champion (r_drop + r_drop_r% AP round it, `Airborne` r_up) and stays on it r_t ticks: an
          `AddCasted` on the champion runs every r_per ticks, each run a punch (r_dmg + r_ratio% AP) and every third a
          slam (r_slam + r_slam_r% AP and `Airborne` r_up, League's third-hit shockwave). Her pictures ride on the
          champion; its death ends her.
  combos  Q -> E (根深敌固 -> 种豆得瓜): the vine's hit seeds the nearest ally at once if E is ready (the burst lands on the
          rooted one). R -> Q (小菊！ -> 根深敌固): Daisy's drop roots the champion with the vine if Q is ready.
Timings: drafts until the frames exist (a frame's start in ticks = ms x 0.06): a_rel, e_rel, q_rel, r_rel.
Numbers: League 16.20 (CommunityDragon ivern.bin) read into the jungle range; balanced on the classic-SDK simulations
(kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/iv_sim, 2026-10-22): the draft +0.88 on
seeds 1-8 and +1.95 on 9-16 (+1.42; league_hwei +1.44 on 1-16, base hunter +0.59 on 1-8 the same day); he farms
slowly (34 cs a game against the base hunter's 48) and wins on his allies' fights (4.9 assists).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_ivern.data_champion")
ID = "league_ivern"
FX = "asset/league/effects/league_ivern_fx"
BIG = "asset/league/effects/league_ivern_big"

# League's Ivern (16.20): 630 +99 hp, 50 AD, 27 armour, 32 mr, 330 move, 475 range. Q: 1125 vine, 80-280 + 70% AP,
# root 1.2-2 s, allies dash to the rooted target, cd 14-10. W: brush; allies' attacks in it deal 30-80 + 30% AP magic.
# E: shield 80-200 + 75% AP for 2 s on an ally, then a burst 70-190 + 80% AP round it, 50-70% slow 2 s, cd 11-7.
# R: Daisy (1300-3500 hp) for 60 s, 20-60 + 30% AP punches, every third a shockwave knock-up 1 s; cd 140-120.
P = {
    # stats (Util jungle: league_lillia 960 +95 hp, 45 +20 ap; the support enchanters 900-950)
    "hp": 950, "hp_g": 95, "atk": 60, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 24, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 47500, "atk_dur": 26, "atk_cd": 80, "a_rel": 10, "a_speed": 4000, "a_y": -4000,
    # passive: Brushmaker
    "w_t": 240, "w_r": 26000, "w_atk": 15, "w_dmg": 15, "w_ratio": 15,
    # skill: E Triggerseed
    "e_cd": 540, "e_range": 50000, "e_dur": 24, "e_rel": 9, "e_ally": 45000,
    "e_sh": 60, "e_sh_r": 45, "e_t": 120, "e_r": 22000, "e_dmg": 50, "e_ratio": 50, "e_slow": 50, "e_slow_t": 90,
    # skill2: Q Rootcaller
    "q_cd": 660, "q_range": 75000, "q_dur": 26, "q_rel": 10, "q_speed": 4500, "q_dmg": 70, "q_ratio": 55,
    "q_root": 80, "q_ally": 60000, "q_ms": 35, "q_ms_t": 90,
    # ult: Daisy!
    "r_cd": 2400, "r_range": 70000, "r_dur": 34, "r_rel": 14, "r_drop": 60, "r_drop_r": 40, "r_up": 50,
    "r_t": 481, "r_per": 60, "r_dmg": 25, "r_ratio": 20, "r_slam": 40, "r_slam_r": 30, "rq_gap": 8,
    # his spoken lines, at most one every vo_gap ticks
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
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


NONE = {"type": "Combine", "effects": []}


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


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
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, first, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def casted(kind, tick, period, *effects):
    return {"type": "AddCasted", "casted_type": kind, "duration": tick, "period": period,
            "effects": [e for e in effects if e is not None]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Brushmaker (grown by every E)
    # the allies standing in it as it grows keep the bonus for its life (a zone on `AllyChampion` gave nobody a buff
    # in the classic engine's trace, 2026-10-22)
    brush = combine(view("w_brush"), sfx("w"), refresh("w_in", p["w_t"]),
                    around(p["w_r"], "AllyNotSelf", [buff("w_buff", p["w_t"], attack_mult=p["w_atk"])]))

    # ------------------------------------------------------------------ attack: a thrown seed
    on_hit = sw("w_in", combine(ap(p["w_dmg"], p["w_ratio"]), view("w_hit")))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), delayed(p["a_rel"] - 1, alive(
                          sfx("a"), homing("a_seed", "Enemy", [attack(0, 100), on_hit, view("a_hit"), tsfx("a_hit")],
                                           p["a_speed"], p["a_y"])))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: E Triggerseed
    burst = [view("e_burst"), sfx("e_burst"),
             zone("e_hit", p["e_r"], [ap(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"],
                                                                          move_speed_mult=-p["e_slow"]),
                                      tsfx("e_hit")])]
    seeded = [shield(p["e_sh"], p["e_sh_r"], p["e_t"]), buff("e_seed", p["e_t"]),
              casted("Fire", p["e_t"] + 1, p["e_t"], lob("e_boom", 1, burst, target="AllyChampion"))]

    def seed():
        """The seed on the nearest ally beside him, else on himself (a 1-tick lock tells which)."""
        return combine(*rm("e_ally"),
                       pick(p["e_ally"], "AllyNotSelf", flag("e_ally", 1), *seeded),
                       sw("e_ally", NONE, combine(on_me(shield(p["e_sh"], p["e_sh_r"], p["e_t"]), buff("e_seed", p["e_t"])),
                                                  delayed(p["e_t"], alive(around(p["e_r"], "EnemyWithoutTower", [
                                                      ap(p["e_dmg"], p["e_ratio"]),
                                                      buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                                                      tsfx("e_hit")]), view("e_burst_me"), sfx("e_burst"))))),
                       *rm("e_ally"))

    def e_cast():
        return combine(refresh("e_cd", p["e_cd"]), seed(), brush, sfx("e"))

    skill = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["e_dmg"], p["e_ratio"], ap),
                           sw("e_cd", NONE, combine(anim("skill", p["e_dur"]), voice("vo_e", p),
                                                    delayed(p["e_rel"] - 1, alive(e_cast()))))),
                   key="skill")

    # ------------------------------------------------------------------ skill2: Q Rootcaller
    def vine():
        """The vine at the action's target; Q -> E: its hit seeds the nearest ally (the burst on the rooted one)."""
        return homing("q_vine", "EnemyWithoutTower", [
            ap(p["q_dmg"], p["q_ratio"]), {"type": "Bind", "duration": p["q_root"]}, buff("q_root", p["q_root"]),
            view("q_hit"), tsfx("q_hit"),
            sw("e_cd", NONE, e_cast())], p["q_speed"], p["a_y"])

    def q_cast():
        rush = around(p["q_ally"], "AllyNotSelf", [buff("q_rush", p["q_ms_t"], move_speed_mult=p["q_ms"])])
        return combine(refresh("q_cd", p["q_cd"]), sfx("q"), vine(), rush)

    skill2 = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["q_dmg"], p["q_ratio"], ap),
                            sw("q_cd", NONE, combine(anim("skill2", p["q_dur"]), voice("vo_q", p),
                                                     delayed(p["q_rel"] - 1, alive(q_cast()))))),
                    key="skill2")

    # ------------------------------------------------------------------ ult: Daisy!
    up = {"type": "Airborne", "duration": p["r_up"]}
    # the count of her punches lives on him (d1, d2): punch, punch, slam
    punch = combine(ap(p["r_dmg"], p["r_ratio"]), view("r_punch"), tsfx("r_punch"))
    slam = combine(ap(p["r_dmg"] + p["r_slam"], p["r_ratio"] + p["r_slam_r"]), up, view("r_slam"), tsfx("r_slam"))
    count = sw("d2", combine(*rm("d1", "d2"), slam),
               sw("d1", combine(*rm("d1"), flag("d2", None), punch), combine(flag("d1", None), punch)))
    # R -> Q: the vine on the champion Daisy dropped on, if Q is ready
    rq = delayed(p["rq_gap"], sw("q_cd", NONE, combine(refresh("q_cd", p["q_cd"]), sfx("q"), anim("skill2", p["q_dur"]),
                                                     view("q_hit"), tsfx("q_hit"), ap(p["q_dmg"], p["q_ratio"]),
                                                     {"type": "Bind", "duration": p["q_root"]},
                                                     buff("q_root", p["q_root"]))))
    drop = [ap(p["r_drop"], p["r_drop_r"]), up, view("r_drop"), tsfx("r_drop"),
            casted("Bleed", p["r_t"], p["r_per"], count), rq]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_drop"], p["r_drop_r"], ap), sfx("r"), voice("vo_r", p), *rm("d1", "d2"),
                         delayed(p["r_rel"] - 1, alive(homing("r_call", "EnemyChampion", drop, 100000)))))

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("a_seed"), Pj("q_vine")]
    views_e = [E("a_hit"), E("w_hit"), E("w_brush", BIG, -1, False), E("e_burst", BIG, 3), E("e_burst_me", BIG, 3, False),
               E("q_hit"), E("r_drop", BIG, 3), E("r_punch", BIG, 3), E("r_slam", BIG, 3)]
    views_b = [B_("e_seed", FX, 3), B_("e_slow", FX, -1), B_("q_root", FX, 3), B_("q_rush", FX, -1),
               B_("w_buff", FX, -1)]
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Range", "CC", "Shield"],
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
