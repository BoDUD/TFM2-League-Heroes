"""Build league_renekton.data_champion (top, Melee) from the parameters P.

    python tools/kit/build_renekton.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-07, all the recommended options: Q alone / E -> W combo with the pro combos / Fury as
five stacks that empower the next skill, the below-half-health bonus left to a native add-on later / R armed, a
transformation when the fight starts):
  passive Reign of Anger (怒之领域): Fury is a ladder of five exclusive caster flags f1..f5 (league_twitch's venom
          ladder): a gain steps one rung up and runs the hold f_t again; f_t ticks without a gain drop it all (League's
          out-of-combat decay, folded into one drop). His attack climbs a rung, Q a rung for each champion it hits and
          one for the rest, Slice a rung for every unit it passes, W a rung (when not empowered), R two rungs on the
          cast and one every r_fury ticks while it lasts. At f5 (League's 50 Fury) the next skill is empowered and
          spends it all - except Q, which takes it only while W is cooling down (the pro rule: keep the Fury for W's
          long stun). League's +50% Fury below half health reads his health: a native add-on, later.
  attack  A melee slash (100% AD) that climbs a rung; while R is armed it fires R when an enemy champion is in reach.
  skill   Q Cull the Meek (巨鳄狂袭): a `Targeting` cast on `EnemyWithoutTower` (q_range). On q_hit every enemy within
          q_r takes q_dmg + q_ratio% AD; he heals q_hm + q_hm_r% AD for every unit hit and q_hc + q_hc_r% AD more for
          every champion. Empowered: q_dmg_e + q_ratio_e% AD, the heals x q_heal_x, no Fury. The slot keeps the flag
          q_cd (the combo's Q lays it too): a slot cast inside it is a 1-tick nothing.
  skill2  E Slice and Dice (横冲直撞) -> W Ruthless Predator (冷酷捕猎): a `Targeting` cast on `EnemyChampion` (e_range).
          Slice: `RushTime` (e_speed x e_tick, penetrate, e_rad) through the target, e_dmg + e_ratio% AD to everything
          passed, a rung each, and Dice opens (d_open) when it hit anything. On landing W at the target: two strikes
          w_gap apart, each w_dmg + w_ratio% AD, and a w_stun stun; empowered three strikes and w_stun_e (League 0.75 /
          1.5 s). Pro combo E -> W -> Q: Q follows when q_cd is off (the heal right after the stun). Then Dice: the
          second dash through the champion (e_dmg + e_ratio% AD), empowered it shreds e_shred% armour for e_shred_t.
  ult     R Dominus (终极统治): a 3-tick cast on `EnemyChampion` (r_slot), armed like league_twitch R: with an enemy
          champion within r_reach it transforms at once, else r_armed for r_arm ticks and his attacks fire it (the
          cooldown refunded when it lapses). The transformation: r_t ticks of +r_hp health (and the same healed), every
          r_period an aura of r_dmg + r_hp_dmg% of his max health magic damage round him (r_r), two Fury rungs at once
          and one every r_fury.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_renekton.data_champion")
ID = "league_renekton"
FX = "asset/league/effects/league_renekton_fx"
BIG = "asset/league/effects/league_renekton_big"

# Numbers = candidate c9 of the 10-min classic-SDK simulations (rk_sim/sim/kd.py --lane 0 against fighter, executioner,
# lancer, pole_warrior, knight and berserker, three lineups, both sides, 2026-10-07): +1.51 on seeds 1-24
# (league_tryndamere +1.34, league_gwen +1.16, league_darius +1.18 on seeds 1-12). The draft c0 was +4.38: R's cooldown
# 60 -> 90 s and 15 -> 10 s changed nothing (+4.70 on 6 seeds); attack 88 -> 80 and hp 1050 -> 980 (+3.11), Q's heals
# 4 + 2% / 20 + 17% -> 2 + 1% / 10 + 10% and E 50 + 90% -> 40 + 70% (+3.50), both +2.48; then E's cooldown 12 -> 15 s
# and Q 60 + 100% -> 45 + 80%. Placeholder timings (no strips yet).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Renekton:
    # 69 AD +3.75, 660 +111 hp, 35 armour, 345 move, attack speed 0.665
    "hp": 980, "hp_g": 105, "atk": 80, "atk_g": 17, "def": 32, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000, "ms_g": 11,
    # attack
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 62, "atk_st": 12,
    # passive: Reign of Anger (League: 5 Fury an attack, 50 empowers, decays after 12 s out of combat)
    "f_n": 5, "f_t": 480,
    # skill: Q Cull the Meek (League: r 325, 60-210 + 100% AD; heal 2-7 + 2% AD a minion, 12-52 + 17% AD a champion;
    # empowered 90-315 + 140% AD, heals x3; cd 7 s)
    "q_cd": 420, "q_range": 25000, "q_dur": 24, "q_hit": 10, "q_r": 32000, "q_dmg": 45, "q_ratio": 80,
    "q_dmg_e": 100, "q_ratio_e": 140, "q_hm": 2, "q_hm_r": 1, "q_hc": 10, "q_hc_r": 10, "q_heal_x": 3,
    # skill2: E Slice (League: 450 dash, 40-190 + 90% AD, cd 16-10 s; Dice within 4 s, empowered shreds 22.5-37.5%
    # armour 4 s) -> W Ruthless Predator (League: 2 strikes 5-80 + 75% AD each, stun 0.75 s; empowered 3 strikes, 1.5 s)
    "e_cd": 900, "e_range": 45000, "e_speed": 4000, "e_tick": 10, "e_rad": 14000, "e_dmg": 40, "e_ratio": 70,
    "d_open": 240, "d_gap": 8, "e_shred": 25, "e_shred_t": 240,
    "w_dur": 24, "w_h1": 6, "w_gap": 6, "w_dmg": 20, "w_ratio": 75, "w_stun": 45, "w_stun_e": 90,
    # ult: R Dominus (League: 15 s, +300-700 hp, aura 0.5 s ticks, 5 Fury a second + 20 on the cast, cd 120/100/80 s)
    "r_cd": 5400, "r_slot": 70000, "r_reach": 35000, "r_arm": 600, "r_anim": 24, "r_t": 600, "r_hp": 300,
    "r_period": 30, "r_r": 30000, "r_dmg": 15, "r_hp_dmg": 1, "r_fury": 60,
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
    return {"type": "Combine", "effects": list(effects)}


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


def ap(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def rush(p, effects):
    return {"type": "RushTime", "speed": p["e_speed"], "tick": p["e_tick"], "range": p["e_rad"],
            "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    fs = [f"f{k}" for k in range(1, p["f_n"] + 1)]

    # ------------------------------------------------------------------ passive: Reign of Anger (Fury)
    # one flag at a time, read from the top: f5 renews itself, f<k> steps up to f<k+1>, none starts f1
    climb = flag(fs[0], p["f_t"])
    for k in range(len(fs) - 1):
        climb = sw(fs[k], combine(*rm(fs[k]), flag(fs[k + 1], p["f_t"])), climb)
    climb = sw(fs[-1], refresh(fs[-1], p["f_t"]), climb)
    spend = rm(*fs)
    full = fs[-1]

    # ------------------------------------------------------------------ Q Cull the Meek
    def cull(empowered):
        x = p["q_heal_x"] if empowered else 1
        dmg = attack(p["q_dmg_e"], p["q_ratio_e"]) if empowered else attack(p["q_dmg"], p["q_ratio"])
        units = [dmg, heal(p["q_hm"] * x, p["q_hm_r"] * x), view("q_hit"), tsfx("q_hit")]
        champs = [heal(p["q_hc"] * x, p["q_hc_r"] * x)]
        out = [anim("skill", p["q_dur"]), sfx("q_cast"), voice("vo_q", p), refresh("q_cd", p["q_cd"])]
        if empowered:
            out += [*spend, cview("q_spin_e")]
            hit = [around(p["q_r"], "EnemyWithoutTower", units), around(p["q_r"], "EnemyChampion", champs)]
        else:
            out.append(cview("q_spin"))
            # a rung for each champion and one for the rest (q_any: a 2-tick flag any hit lays)
            hit = [around(p["q_r"], "EnemyWithoutTower", units + [refresh("q_any", 2)]),
                   around(p["q_r"], "EnemyChampion", champs + [climb]),
                   delayed(1, sw("q_any", combine(*rm("q_any"), climb)))]
        out.append(delayed(p["q_hit"], *hit))
        return combine(*out)

    # empowered only while W cools down (the pro rule: the stun gets the Fury); e_cd is W's flag
    q_cast = sw(full, sw("e_cd", cull(True), cull(False)), cull(False))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_cd", NONE, q_cast))

    # ------------------------------------------------------------------ skill2: E Slice -> W Ruthless Predator -> Dice
    def strikes(k, stun):
        out = []
        for i in range(k):
            last = i == k - 1
            hit = [attack(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")]
            if last:
                hit += [{"type": "Stun", "duration": stun}, buff("w_stun", stun), sfx("w_stun")]
            out.append(delayed(p["w_h1"] + i * p["w_gap"], sfx("w_cast"),
                               homing("w_blade", 100000, 0, "EnemyChampion", hit)))
        return out

    w_plain = combine(anim("skill2_w", p["w_dur"]), climb, *strikes(2, p["w_stun"]))
    w_emp = combine(anim("skill2_w", p["w_dur"] + p["w_gap"]), *spend, cview("w_glow"), sfx("w_super"), voice("vo_w", p),
                    *strikes(3, p["w_stun_e"]))
    w_strike = sw(full, w_emp, w_plain)

    dice_plain = rush(p, [attack(p["e_dmg"], p["e_ratio"]), climb, view("e_hit"), tsfx("e_hit")])
    dice_emp = rush(p, [attack(p["e_dmg"], p["e_ratio"]), buff("e_shred", p["e_shred_t"], defence_mult=-p["e_shred"]),
                        view("e_hit"), tsfx("e_hit")])
    dice = sw("d_open", combine(*rm("d_open"), anim("skill2", p["e_tick"] + 4), sfx("e_dash"), cview("e_dash"),
                                sw(full, combine(*spend, pick(p["e_range"], "EnemyChampion", dice_emp)),
                                   pick(p["e_range"], "EnemyChampion", dice_plain))))
    slice_ = rush(p, [attack(p["e_dmg"], p["e_ratio"]), climb, refresh("d_open", p["d_open"]), view("e_hit"),
                      tsfx("e_hit")])
    w_end = p["e_tick"] + p["w_dur"] + 2 * p["w_gap"]
    # E -> W -> Q (the heal right after the stun) when Q is ready, then Dice; W's flag is on here, so Q takes a full
    # Fury the strikes and Slice built back
    after_w = sw("q_cd", delayed(p["d_gap"], dice),
                 combine(pick(p["q_range"] + 10000, "EnemyChampion", sw(full, cull(True), cull(False))),
                         delayed(p["q_dur"] + p["d_gap"], dice)))
    skill2 = action("skill2", p["e_tick"] + p["w_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_tick"] + 4), sfx("e_dash"),
                            voice("vo_e", p), cview("e_dash"), slice_,
                            delayed(p["e_tick"], w_strike), delayed(w_end, after_w)))

    # ------------------------------------------------------------------ R Dominus
    aura = casted(p["r_t"], p["r_period"], around(p["r_r"], "EnemyWithoutTower",
                                                    [ap(p["r_dmg"], 0, p["r_hp_dmg"]), view("r_burn")]))
    fury_tick = casted(p["r_t"], p["r_fury"], climb)

    def fire(pose):
        out = [*rm("r_armed"), refresh("r_on", p["r_t"], hp=p["r_hp"]), heal(p["r_hp"], 0), climb, climb,
               sfx("r_cast"), sfx("r_roar"), voice("vo_r", p), cview("r_cast"), on_me(aura, fury_tick)]
        if pose:
            out.append(anim("ult", p["r_anim"]))
        return combine(*out)

    def near(then, otherwise=NONE):
        """A 2-tick flag u1 when an enemy champion is within r_reach."""
        return combine(*rm("u1"), around(p["r_reach"], "EnemyChampion", [refresh("u1", 2)]), sw("u1", then, otherwise))

    arm = combine(refresh("r_armed", p["r_arm"]),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    ult = action("ult", 3, p["r_cd"], 1, p["r_slot"], "Targeting", "EnemyChampion", near(fire(True), arm))

    # ------------------------------------------------------------------ attack
    swing = combine(sfx("a_swing"), climb, attack(0, 100), view("a_hit"), tsfx("a_hit"),
                    sw("r_armed", near(fire(False))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", swing,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring); the buffs
    # left-right symmetric
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("w_blade")]
    views_e = [E("a_hit"), E("q_hit"), E("q_spin", BIG, 2, **LATE), E("q_spin_e", BIG, 2, **LATE), E("e_dash", BIG, -1),
               E("e_hit"), E("w_hit"), E("w_glow", FX, 3, **LATE), E("r_cast", BIG, 2, **LATE), E("r_burn")]
    views_b = [B_(full, FX, -1), B_("w_stun", FX, 3), B_("e_shred", FX, 3), B_("r_on", BIG, -1)]
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Heal"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
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
