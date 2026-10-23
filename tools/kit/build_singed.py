"""Build league_singed.data_champion (top, Melee tank, AP: Singed, the Mad Chemist) from the parameters P.

    python tools/kit/build_singed.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-23: TOP, layout A - E / W / R, Q's trail and the slipstream in the passive; combos W's
glue -> E into it, E's fling -> the slipstream, R's drink -> W at once, R on: a stronger trail and a shorter E).
TFM2 has three active slots for League's four buttons: Fling (E) is `skill`, Mega Adhesive (W) `skill2`, Insanity Potion
(R) the `ult`; Poison Trail (Q), always on in League's play, is the passive. E and W keep their cooldowns in flags
(`e_cd`, `w_cd`; league_zac's Q) so the combos can cast them; a slot cast while its flag is up does nothing (a 3-tick
idle). Flags die with him: a respawned Singed has E and W ready.
  passive Poison Trail (剧毒踪迹) + Noxious Slipstream (剧毒冲流): a controller on him (an AddCasted pulse every ctl_p
          ticks, hung by his attack and the ult, league_zac's) drops a poison cloud where he stands whenever he stands
          in none (a self-only zone of radius q_gap round each cloud raises `in_cloud`), so walking leaves a trail and
          standing still keeps one cloud: q_r round, q_t ticks, every q_p ticks q_dmg + q_ap% AP to every enemy in it
          (the zones start from a 1-unit anchor's end_effects: champion-data "zones start from a projectile").
          An enemy champion within p_near (passing him) gives him p_ms% move speed for p_t ticks, once every p_gap.
  attack  A blow of the shield plate (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit.
  skill   E Fling (过肩摔), `Targeting` on `EnemyWithoutTower` (e_range, `e_cd`): on e_grab he heaves the target over
          his shoulder: e_dmg + e_ap% AP + e_thp% of its maximum health (true, `FixedAttack`; League 6-9% max health),
          pulled through him for e_fly ticks (`Pull` e_speed x e_fly: a pull runs past the caster, champion-data "Pull
          vs Grab"; an `Airborne` with it kept the unit in place) to land behind him. Landing while his glue lies on the ground (`w_out`) roots it e_root ticks
          (League: landing in the glue; data reads no unit's place, so any lying glue counts - he flings toward it).
  skill2  W Mega Adhesive (强力粘胶), `Targeting` on `EnemyChampion` (w_range, `w_cd`): the vial lands w_fly ticks after
          w_rel on the spot (a lob), the glue lies w_t ticks in w_r: every w_p ticks w_slow% slow and grounding
          (`BlockMoveSkill`, no dashes) for w_p + 6 ticks; `w_out` while it lies.
  ult     R Insanity Potion (疯狂药剂), `Targeting` on `EnemyChampion` within r_range: he drinks (r_dur) and for r_t ticks
          gains r_apw ability power, r_def armour and magic resistance, r_ms% move speed and r_regen health a second.
  combos  W -> E: the glue landing on a champion lets the controller cast E on an enemy champion within e_range when
          `e_cd` is off (thrown into the glue: rooted). E -> slipstream: every fling gives the slipstream's speed at once.
          R -> W: the drink throws the glue at once at an enemy champion within w_range (its cooldown starting over).
          R on: clouds q_r_r round dealing r_q% of the damage and cutting healing r_gw% (League's Grievous Wounds) and
          E's cooldown e_cd_r instead of e_cd.
Timings: drafts until the frames exist (tools/art/rig_singed.py retimes them).
Numbers: League 16.20 read into the top tank range (league_illaoi, league_ksante), balanced on the classic-SDK
simulations (kd.py --lane 0 against fighter, executioner, knight, berserker, lancer and pole_warrior, C:/t/si_sim).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_singed.data_champion")
ID = "league_singed"
FX = "asset/league/effects/league_singed_fx"
BIG = "asset/league/effects/league_singed_big"

# League's Singed (16.20): 650 +96 hp, 63 AD, 34 armour, 32 mr, 345 move, 125 range. Q: 40-120 + 60% AP a second
# (trail 3.25 s), R: Grievous Wounds. W: 1000 range, 3 s glue, 60% slow, grounded, cd 17-13. E: 50-110 + 75% AP + 6-9%
# of the target's max health, flung 550 behind him, a 1-2 s root in the glue, cd 10-8. R: +30-80 AP, armour, mr, move
# speed, 25 s, cd 100. Passive: 20% move speed passing a champion.
P = {
    # stats (base tanks: attack 80 +6, hp 1100 +120, defence 40 +10, mr 30 +5; league_illaoi 1150 / 80)
    "hp": 1120, "hp_g": 115, "atk": 66, "atk_g": 5, "apw": 30, "apw_g": 15, "def": 38, "def_g": 9, "mr": 30, "mr_g": 5,
    "ms": 1050, "ms_g": 11,
    "atk_range": 20000, "atk_dur": 28, "atk_cd": 70, "a_hit": 11,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: Poison Trail's clouds
    "q_r": 11000, "q_gap": 9000, "q_t": 180, "q_p": 30, "q_dmg": 14, "q_ap": 14,
    # passive: Noxious Slipstream
    "p_near": 22000, "p_ms": 25, "p_t": 90, "p_gap": 240,
    # skill: E Fling
    "e_cd": 540, "e_cd_r": 360, "e_range": 20000, "e_dur": 30, "e_grab": 10, "e_dmg": 50, "e_ap": 60, "e_thp": 5,
    "e_fly": 16, "e_speed": 4800, "e_root": 60,
    # skill2: W Mega Adhesive
    "w_cd": 900, "w_range": 60000, "w_dur": 30, "w_rel": 12, "w_fly": 20, "w_t": 180, "w_r": 20000, "w_p": 6,
    "w_slow": 50, "w_e_at": 2,
    # ult: R Insanity Potion
    "r_cd": 5400, "r_range": 40000, "r_dur": 40, "r_t": 1500, "r_apw": 60, "r_def": 30, "r_ms": 15, "r_regen": 12,
    "r_q": 150, "r_q_r": 14000, "r_gw": 40, "r_w_at": 20,
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


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


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


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=ap):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def anchor(name, end):
    """A 1-unit line whose end_effects start zones where he stands (league_gwen's mist)."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": "Ally",
            "applied_effects": [], "end_effects": list(end), "speed": 1, "range": 1, "shape": circle(1000),
            "y_offset": 0}


def lob(name, travel, end, target="EnemyChampion"):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Noxious Slipstream
    haste = combine(refresh("p_gap", p["p_gap"]), refresh("p_fast", p["p_t"], move_speed_mult=p["p_ms"]),
                    cview("p_fast"))
    slip = sw("p_gap", NONE, pick(p["p_near"], "EnemyChampion", haste))

    # ------------------------------------------------------------------ passive: Poison Trail's clouds
    def cloud(r, k):
        hit = [ap(p["q_dmg"] * k // 100, p["q_ap"] * k // 100), tsfx("q_hit")]
        return [field("q_cloud", r, p["q_t"], p["q_p"], hit, first=0),
                field("q_me", p["q_gap"], p["q_t"], p["ctl_p"], [refresh("in_cloud", p["ctl_p"] + 1)],
                      target="AllyOnlySelf", first=0)]
    strong = cloud(p["r_q_r"], p["r_q"])
    strong[0]["applied_effects"].append(T(buff("q_gw", p["q_p"] + 6, heal_reduce=p["r_gw"])))
    drop = sw("in_cloud", NONE, combine(refresh("in_cloud", p["ctl_p"] + 1),
                                        sw("r_on", combine(anchor("q_drop", strong), on_me(view("q_cloud_r"))),
                                           combine(anchor("q_drop", cloud(p["q_r"], 100)), on_me(view("q_cloud"))))))

    # ------------------------------------------------------------------ E Fling
    def e_cast(target):
        root = sw("w_out", combine({"type": "Bind", "duration": p["e_root"]}, view("e_root"), tsfx("e_root")))
        # the pull straight on the target, not in the projectile (a Pull in a projectile heads for the projectile,
        # already on the target: traced 2026-10-23, 0 of 35 moved), and no Airborne (a knocked-up unit is not pulled)
        hit = [ap(p["e_dmg"], p["e_ap"]), pct(p["e_thp"]), view("e_hit"), tsfx("e_hit")]
        throw = combine({"type": "Pull", "speed": p["e_speed"], "tick": p["e_fly"]},
                        delayed(p["e_fly"], view("e_land"), root))
        cd = sw("r_on", refresh("e_cd", p["e_cd_r"]), refresh("e_cd", p["e_cd"]))
        return combine(cd, anim("skill", p["e_dur"]), sfx("e"), voice("vo_e", p),
                       delayed(p["e_grab"] - 1, alive(homing("e_grab", target, hit), throw, haste)))

    # ------------------------------------------------------------------ W Mega Adhesive
    def w_cast(target):
        glue = field("w_glue", p["w_r"], p["w_t"], p["w_p"],
                     [buff("w_slow", p["w_p"] + 6, move_speed_mult=-p["w_slow"]),
                      {"type": "BlockMoveSkill", "tick": p["w_p"] + 6}], first=0)
        land = [glue, view("w_glue"), sfx("w_land")]
        return combine(refresh("w_cd", p["w_cd"]), anim("skill2", p["w_dur"]), sfx("w"), voice("vo_w", p),
                       delayed(p["w_rel"] - 1, alive(
                           lob("w_vial", p["w_fly"], land, target),
                           # W -> E: the controller casts E once the glue lies
                           delayed(p["w_fly"], alive(refresh("w_out", p["w_t"]),
                                                     refresh("e_go", p["w_e_at"] + p["ctl_p"] + 2))))))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not
    # (league_zac): his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs.
    # It drops the clouds, the slipstream, W -> E (`e_go`) and R -> W (`w_go`).
    ctl = combine(refresh("polling", p["ctl_p"] + 2), drop, slip,
                  sw("e_go", combine(*rm("e_go"), sw("e_cd", NONE, pick(p["e_range"], "EnemyChampion",
                                                                        e_cast("EnemyChampion"))))),
                  sw("w_go", combine(*rm("w_go"), sw("w_cd", NONE, pick(p["w_range"], "EnemyChampion",
                                                                        w_cast("EnemyChampion"))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", p["ctl_p"] + 2), casted(p["ctl_t"], p["ctl_p"], ctl))))

    # ------------------------------------------------------------------ R Insanity Potion
    r_cast = combine(sfx("r"), voice("vo_r", p), cview("r_drink"),
                     refresh("r_on", p["r_t"], magic_power=p["r_apw"], defence=p["r_def"], magic_resistance=p["r_def"],
                             move_speed_mult=p["r_ms"], hp_regen=p["r_regen"]),
                     # R -> W (the controller casts it once he has drunk)
                     delayed(p["r_w_at"], alive(rm("w_cd")[0], refresh("w_go", p["ctl_p"] + 2))))

    # ------------------------------------------------------------------ attack
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100, attack), hang, delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["e_dmg"], p["e_ap"]), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["e_dmg"], p["e_ap"]), sw("e_cd", NONE, e_cast("EnemyWithoutTower"))), key="skill")
    skill2 = action("idle", 3, 60, 1, p["w_range"], "Targeting", "EnemyChampion",
                    combine(decoy(p["e_dmg"], p["e_ap"]), sw("w_cd", NONE, w_cast("EnemyChampion"))), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("w_vial")]
    views_e = [E("a_hit"), E("e_hit"), E("e_land", FX, -1, False), E("e_root"), E("w_glue", BIG, -1, False),
               E("q_cloud", BIG, -1, False), E("q_cloud_r", BIG, -1, False), E("r_drink"), E("p_fast")]
    views_b = [B_("w_slow", FX, -1, "slow"), B_("q_gw", FX, 3, "gw"), B_("r_on", FX, -1, "r_aura"),
               B_("p_fast", FX, -1, "haste")]
    return {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Tank", "CC"],
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
