"""Build league_lulu.data_champion (support, Util, enchanter) from the parameters P.

    python tools/kit/build_lulu.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-08: A - W and E in one cast; the polymorph drawn over the target; R a growth aura):
  attack  Lulu's bolt (homing, physical) and Pix, Faerie Companion (passive): Pix fires p_n homing bolts p_gap ticks
          apart at the same target, each p_dmg + p_ap% AP magic damage (League: 3 bolts, ~5% AP each, blocked by
          the first unit - here they home).
  skill   Q Glitterlance: a `Direction` cast on `EnemyWithoutTower` (the aim is locked at the cast: dodgeable). Lulu's
          bolt (a penetrating LinearProjectile) deals q_dmg + q_ap% AP to every enemy on the line and slows it: q_s1%
          for q_t1 ticks on top of q_s2% for q_t2 ticks (League: 80% decaying over 2 s). Pix's bolt flies beside it,
          higher (y_offset), as a picture: League lets an enemy take only one bolt's damage.
  skill2  W Whimsy + E Help, Pix! (one cast, `Targeting` on `EnemyChampion`): a homing bolt polymorphs the champion -
          w_t ticks of BlockAttack + BlockSkill and w_slow% slower (League: silenced, disarmed, slowed; 1.2-2 s) and
          e_dmg + e_ap% AP magic damage (Pix hampers him). The puff and the critter are a buff picture drawn over him
          (z 1): the engine cannot swap his sprite. Pix flies to the nearest allied champion (rings e_r1, e_r2 -
          league_rakan's way): a shield e_sh + e_ap2% AP for e_t ticks with Pix's picture on him, and Whimsy's haste
          (w_ms% move speed, w_as% attack speed, w_ht ticks). No ally in reach: Lulu takes them herself.
  ult     R Wild Growth, armed like league_kayle R: a 3-tick `None` cast on `EnemyChampion` (r_arm_range) arms r_armed
          for r_arm ticks; every attack, Q and W/E check it: an allied champion in crowd control within r_range gets it
          first, else a probe (a hidden lob) onto a random allied champion within r_range (her too) counts the enemy
          champions within r_near of him: r_need or more -> he gets it. The champion grows: r_hp health (a flat `hp` buff + the same heal), radius_mult r_rad, the growth
          aura (its picture a buff on him) for r_t ticks; every enemy within r_r of him is knocked up r_up ticks, and
          every r_period ticks the aura slows the enemies within r_r by r_slow% (a casted on him whose runs drop a
          one-tick zone on his spot). Unused, the cooldown is refunded (60 ticks).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_lulu.data_champion")
ID = "league_lulu"
FX = "asset/league/effects/league_lulu_fx"
BIG = "asset/league/effects/league_lulu_big"

# Numbers = candidate c4 of the 10-min classic-SDK simulations (lul_sim/sim/kd.py, support lane against the five base
# supports, both sides, 3 lineups, 2026-10-08): +0.60 on seeds 13-36 (league_janna -0.24 on the same seeds; c3 +0.27, its
# +0.50 on seeds 1-12 against Janna's +0.62). The draft c1 was +0.13: Q 70+50% / 7 s, shield 70, polymorph 1.5 s, Pix
# 8+6%. Raised: Q 80+60% / 6 s, W/E cd 9 s, polymorph 1.75 s, E damage 70, shield 110, Pix 12+8%, R health 350.
P = {
    # stats (the pack's ranged supports: Janna/Nami/Sona/Seraphine/Zilean hp 880-950 +80-95, atk 75-80, ap 30 +15,
    # def 20-24, mr 20-24, range 55000-60000, attack cooldown 90)
    "hp": 880, "hp_g": 90, "atk": 75, "atk_g": 6, "ap": 30, "ap_g": 15, "def": 22, "def_g": 7, "mr": 24, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "atk_st": 11, "a_speed": 5000, "a_y": -1000,
    # passive: Pix, Faerie Companion (League: 3 bolts at her attack target, 5-? + 5% AP each)
    "p_n": 3, "p_gap": 4, "p_speed": 5500, "p_y": -4000, "p_dmg": 12, "p_ap": 8,
    # skill: Q Glitterlance (League: 950 range, 1450 speed, width 60; 70-250 + 40% AP; slow 80% decaying over 2 s;
    # cd 7 s)
    "q_cd": 360, "q_range": 60000, "q_dur": 22, "q_st": 10, "q_speed": 5000, "q_reach": 70000, "q_rad": 6000,
    "q_y": 0, "q_pix_y": -4000, "q_dmg": 80, "q_ap": 60, "q_s1": 30, "q_t1": 30, "q_s2": 50, "q_t2": 90,
    # skill2: W Whimsy (League: 650 range; polymorph 1.2-2 s, silence + disarm + -60 move speed; ally: +30% move,
    # +25-45% attack speed for 3.5-5.5 s; cd 17-12 s) + E Help, Pix! (League: shield 75-235 + 40% AP for 2.5 s;
    # enemy: 80-240 + 40% AP; cd 9-7.5 s)
    "w_cd": 540, "w_range": 55000, "w_dur": 20, "w_st": 10, "w_speed": 5000, "w_y": -4000, "w_t": 105, "w_slow": 30,
    "e_dmg": 70, "e_ap": 40, "e_r1": 30000, "e_r2": 60000, "e_speed": 4500, "e_sh": 110, "e_ap2": 50, "e_t": 150,
    "w_ms": 25, "w_as": 25, "w_ht": 210,
    # ult: R Wild Growth (League: 900 range; +300-500 health, knock-up 1 s in 400 units, slow aura 30-40% for 7 s;
    # cd 120-80 s)
    "r_cd": 3600, "r_arm": 900, "r_arm_range": 70000, "r_range": 50000, "r_near": 25000, "r_need": 1,
    "r_hp": 350, "r_hp_ap": 50, "r_rad": 30, "r_t": 420, "r_r": 22000, "r_up": 60, "r_period": 15, "r_slow": 30,
    "r_anim": 24, "r_lag": 7,
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


def heal_ally(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Ally"}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def drop(name, *end, hit=()):
    """A hidden one-tick lob onto the unit in hand (league_annie R): its end_effects start a zone on that spot,
    `hit` runs on the unit itself (a Delayed there is queued on him)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000,
            "shape": circle(1000), "applied_target": "AllyChampion", "applied_effects": [T(e) for e in hit],
            "end_effects": list(end)}


def zone(name, radius, target, effects):
    """A one-tick area on the lob's landing spot."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur_, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur_, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ ult: R Wild Growth (the armed check)
    def grow():
        """On the champion the check picked: the growth, the knock-up round him, the slowing aura."""
        return combine(
            *rm("r_armed"), flag("r_got", 1), anim("ult", p["r_anim"]), sfx("r_cast"),
            delayed(p["r_lag"], tsfx("r_grow"),
                    buff("r_on", p["r_t"], hp=p["r_hp"], radius_mult=p["r_rad"]), heal_ally(p["r_hp"], p["r_hp_ap"]),
                    view("r_burst"),
                    drop("r_lob", zone("r_up", p["r_r"], "EnemyWithoutTower",
                                       [{"type": "Airborne", "duration": p["r_up"]}, view("r_hit"),
                                        buff("r_slow", p["r_period"] + 2, move_speed_mult=-p["r_slow"])])),
                    casted(p["r_t"], p["r_period"],
                           drop("r_aura", zone("r_slow", p["r_r"], "EnemyWithoutTower",
                                               [buff("r_slow", p["r_period"] + 2, move_speed_mult=-p["r_slow"])])))))

    # the probe: a hidden lob onto a random allied champion in reach (her too) counts the enemy champions round him
    # (r_n1, r_n2 on her); two ticks later, on him, enough of them -> he grows
    need = "r_n2" if p["r_need"] >= 2 else "r_n1"
    probe = drop("r_probe", zone("r_count", p["r_near"], "EnemyChampion",
                                 [sw("r_n1", flag("r_n2", 4), flag("r_n1", 4))]),
                 hit=[delayed(2, sw("r_armed", sw(need, grow())))])
    r_check = sw("r_armed", combine(
        *rm("r_got", "r_n1", "r_n2"), pick(p["r_range"], "AllyChampionInCC", grow()),
        sw("r_got", NONE, pick(p["r_range"], "AllyChampion", probe))))

    # ------------------------------------------------------------------ attack + passive: Pix's bolts
    pix = [delayed(i * p["p_gap"], homing("p_bolt", p["p_speed"], p["p_y"], "Enemy",
                                          [magic(p["p_dmg"], p["p_ap"]), view("p_hit")]))
           for i in range(p["p_n"])]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", flat(combine(
        r_check, sfx("a_cast"),
        homing("a_bolt", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
        *pix)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Glitterlance
    lance = line("q_lance", p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], "EnemyWithoutTower", True,
                 [magic(p["q_dmg"], p["q_ap"]), buff("q_slow1", p["q_t1"], move_speed_mult=-p["q_s1"]),
                  buff("q_slow2", p["q_t2"], move_speed_mult=-p["q_s2"]), view("q_hit"), tsfx("q_hit")])
    pix_lance = line("q_pix", p["q_speed"], p["q_reach"], p["q_rad"], p["q_pix_y"], "EnemyWithoutTower", True, [])
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Direction", "EnemyWithoutTower",
                   flat(combine(r_check, sfx("q_cast"), lance, pix_lance)))

    # ------------------------------------------------------------------ skill2: W Whimsy + E Help, Pix!
    def help_on(target_effects):
        return combine(shield(p["e_sh"], p["e_ap2"], p["e_t"]), buff("e_on", "WithShield"),
                       buff("w_haste", p["w_ht"], move_speed_mult=p["w_ms"], attack_speed_mult=p["w_as"]),
                       view("e_land"), *target_effects)

    def e_go():
        return combine(flag("e_got", 1), sfx("e_cast"),
                       homing("e_pix", p["e_speed"], p["p_y"], "AllyChampion", [help_on([tsfx("e_shield")])]))

    e_self = around(1000, "AllyOnlySelf", [help_on([sfx("e_shield")])])
    e_rings = combine(*rm("e_got"), pick(p["e_r1"], "AllyNotSelf", e_go()),
                      sw("e_got", NONE, combine(pick(p["e_r2"], "AllyNotSelf", e_go()), sw("e_got", NONE, e_self))))
    poly = homing("w_bolt", p["w_speed"], p["w_y"], "EnemyChampion",
                  [{"type": "BlockAttack", "tick": p["w_t"]}, {"type": "BlockSkill", "tick": p["w_t"]},
                   buff("w_poly", p["w_t"], move_speed_mult=-p["w_slow"]), magic(p["e_dmg"], p["e_ap"]),
                   tsfx("w_hit")])
    skill2 = action("skill2", p["w_dur"], p["w_cd"], p["w_st"], p["w_range"], "Targeting", "EnemyChampion",
                    flat(combine(r_check, sfx("w_cast"), poly, e_rings)))

    # ------------------------------------------------------------------ ult: arms Wild Growth
    ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion", flat(combine(
        *rm("r_armed"), flag("r_armed", p["r_arm"]), r_check,
        delayed(p["r_arm"], sw("r_armed", combine(*rm("r_armed"), flag("r_refund", 3, ult_cooldown_mult=4900)))))),
        key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                      "repeat": True, "z": z}
    B3 = lambda name, anim_=FX, z=1: {"type": "ThreePhase", "name": n(name), "anim": anim_, "pre_tag": name + "_in",
                                      "loop_tag": name, "remove_tag": name + "_out", "z": z}
    views_p = [P_("a_bolt"), P_("p_bolt"), P_("q_lance"), P_("q_pix"), P_("w_bolt"), P_("e_pix")]
    views_e = [E("a_hit", FX, 2), E("p_hit", FX, 2), E("q_hit", FX, 2), E("e_land", FX, 2),
               E("r_burst", BIG, 2), E("r_hit", FX, 2)]
    # the polymorph's puff and critter over the target (z 1 covers him); Pix and the shield on the ally; the growth
    # aura on the ground round the grown champion
    views_b = [B3("w_poly", FX, 2), P_("e_on", FX, 2), P_("w_haste", FX, 1), B3("r_on", BIG, -1),
               P_("q_slow2", FX, 1)]
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Range", "CC", "Shield"],
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
