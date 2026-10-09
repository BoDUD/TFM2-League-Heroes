"""Build league_hecarim.data_champion (jungle, Melee fighter) from the parameters P.

    python tools/kit/build_hecarim.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-09: jungle, League's whole kit + the pros' combos). TFM2 has three active slots:
Rampage is `skill`, Devastating Charge `skill2`, Onslaught of Shadows the `ult`; Spirit of Dread runs on its own.
  passive Warpath (征战之路): League turns his bonus move speed into attack damage. Every haste of his carries attack
          too: the charge's pace rungs (e1..e3, `e_warp` % attack a rung), the haste after the charge (`e_haste`) and
          the ult's ride (`r_warp`).
  attack  The glaive swing, the hit on tick a_st.
  skill   Q Rampage (暴走): a spin on `EnemyWithoutTower` within q_r (so he spins on waves and camps): q_dmg + q_ratio%
          AD to every enemy round him. A hit gives a Rampage stack (q1, q2: q_stk_t ticks, renewed), each q_stk% more
          damage on the next spins; stacks built on camps carry into a gank.
  W       Spirit of Dread (恐惧之灵, automatic): the first spin, charge landing or ult landing with an enemy champion
          within w_r and w_cd off starts it: w_t ticks of w_def armour / w_mr magic resistance and a pulse every 60
          ticks - w_dmg magic damage to every enemy round him and a heal of w_heal for each one it reaches (League heals
          a share of the damage dealt round him; nothing reads damage, so it is per unit hit).
  skill2  E Devastating Charge (毁灭冲锋): on `EnemyWithoutTower` within e_range: he gallops onto the target
          (MoveToTarget e_speed from tick e_go); the longer the ride the harder the hit, as League's ramp - rungs e2 / e3
          after e_t2 / e_t3 ticks of riding: e_dmg + e_ratio% AD, x e_mid% / x e_max% on the rungs, and a knockback
          (e_kb_t ticks at e_kb_speed: away from him). Then e_haste% move speed for e_haste_t ticks.
  ult     R Onslaught of Shadows (暗影冲击): on `EnemyChampion` within r_range: spectral riders (a penetrating line,
          r_dmg + r_ratio% AD to every enemy they pass) and he rides with them onto the champion (MoveToTarget r_speed,
          cc_immune while riding); on landing every enemy within r_r is feared (r_fear ticks; r_fear_far after a long
          ride - League's fear grows with the distance).
  combos  (the pros' Hecarim, slot-played like league_kennen's E -> R: a combo never holds another slot)
          E -> R (冲锋接大招): a charge that lands on a champion while the ult is unlocked (`r_open`, set by the ult
                  slot's every cast) and unused (`r_cd`) ends in the Onslaught at once - the riders' burst, the fear
                  round him and the charge's knockback; the ult slot then finds `r_cd` and goes out empty.
          R -> Q (落地回旋): every Onslaught landing spins a free Rampage (rq_pct% of its damage, a stack, no cooldown).
          W on engage: Spirit of Dread starts on the landing of a charge or an Onslaught (the dive heals him).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_hecarim.data_champion")
ID = "league_hecarim"
FX = "asset/league/effects/league_hecarim_fx"
BIG = "asset/league/effects/league_hecarim_big"

# Timings from the strips (assets/source/hecarim/poses.json, MODEL_STRIPS.md): the chop on tick 11 (attack frame 4), the
# Rampage sweep on tick 9 (skill frame 4), the charge's smash 5 ticks into skill2_hit (frame 3 starts on tick 6), the
# rear-up that sends the riders on tick 7 (ult frame 3).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30, mr 25, move 1000, range 25000, cd 65); League's
    # Hecarim: 625 +110 hp, 66 AD +3.2, 32 armour, 345 move (fast), 175 range
    "hp": 1050, "hp_g": 100, "atk": 95, "atk_g": 17, "def": 32, "def_g": 8, "mr": 22, "mr_g": 4, "ms": 1080,
    "ms_g": 12,
    # attack: the glaive swing
    "atk_range": 25000, "atk_dur": 25, "atk_cd": 62, "a_st": 11,
    # skill: Q Rampage (League: 375 radius, 60-140 + 90% bonus AD, a stack 8 s, up to 2: +? damage, cd 4 s)
    "q_cd": 240, "q_dur": 24, "q_at": 9, "q_r": 26000, "q_dmg": 45, "q_ratio": 85, "q_stk": 20, "q_stk_t": 480,
    # W Spirit of Dread (League: 4 s, 525 radius, 20-80 + 20% AP magic over 4 s, +armour / mr, heals 25% of his
    # damage to enemies round him, cd 14-10 s)
    "w_cd": 840, "w_t": 240, "w_r": 30000, "w_dmg": 14, "w_heal": 12, "w_def": 20, "w_mr": 20,
    # skill2: E Devastating Charge (League: 25-65% ramping move speed over 4 s, 30-90 + 50% bonus AD x2 at full ramp,
    # a knockback; cd 20-16 s)
    "e_cd": 600, "e_dur": 30, "e_go": 4, "e_range": 60000, "e_speed": 2500, "e_t2": 8, "e_t3": 16,
    "e_dmg": 30, "e_ratio": 60, "e_mid": 150, "e_max": 200, "e_kb_speed": 2000, "e_kb_t": 10, "e_warp": 8,
    "e_haste": 25, "e_haste_t": 120, "e_land_r": 20000, "e_smash": 5,
    # ult: R Onslaught of Shadows (League: 1000 range, 150-350 + 100% bonus AD, fear 0.75-1.5 s by distance, cd 140 s)
    "r_cd": 3000, "r_dur": 30, "r_go": 7, "r_range": 70000, "r_speed": 3000, "r_dmg": 70, "r_ratio": 100,
    "r_rad": 12000, "r_len": 75000, "r_r": 26000, "r_fear": 45, "r_fear_far": 80, "r_far_t": 12, "r_warp": 20,
    "r_warp_t": 180, "r_cc": 30,
    # combos: the free spin on landing, % of a Rampage
    "rq_pct": 60,
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


def ap_attack(dmg):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": 0, "can_crit": False}


def heal(amount):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ Rampage stacks
    def stack():
        return sw("q1", combine(*rm("q1"), refresh("q2", p["q_stk_t"])),
                  sw("q2", refresh("q2", p["q_stk_t"]), refresh("q1", p["q_stk_t"])))

    def spin(pct):
        """Rampage round him at pct% of its damage, more for each stack; a stack if it reached anyone."""
        def hit(mult):
            k = pct * mult // 100
            return around(p["q_r"], "EnemyWithoutTower", [attack(p["q_dmg"] * k // 100, p["q_ratio"] * k // 100),
                                                          view("q_hit"), tsfx("q_hit")])
        return combine(cview("q_spin"), sfx("q"),
                       sw("q2", hit(100 + 2 * p["q_stk"]), sw("q1", hit(100 + p["q_stk"]), hit(100))),
                       pick(p["q_r"], "EnemyWithoutTower", stack()))

    # ------------------------------------------------------------------ W Spirit of Dread (automatic)
    pulse = around(p["w_r"], "EnemyWithoutTower", [ap_attack(p["w_dmg"]), heal(p["w_heal"]), view("w_hit")])
    dread = combine(flag("w_cd", p["w_cd"]),
                    refresh("w_on", p["w_t"], defence=p["w_def"], magic_resistance=p["w_mr"]),
                    sfx("w"), voice("vo_w", p), cview("w_start"),
                    casted(p["w_t"] + 1, 60, pulse))
    # only with an enemy champion near: RandomTarget runs it once, for one picked champion
    w_auto = sw("w_cd", NONE, pick(p["w_r"], "EnemyChampion", on_me(dread)))

    # ------------------------------------------------------------------ the Onslaught's landing (R, E -> R)
    def landing(far):
        fear = {"type": "Fear", "tick": p["r_fear_far"] if far else p["r_fear"]}
        return combine(cview("r_land"), sfx("r_hit"),
                       around(p["r_r"], "EnemyWithoutTower", [fear, view("r_fear")]),
                       refresh("r_warp", p["r_warp_t"], attack_mult=p["r_warp"]),
                       spin(p["rq_pct"]), w_auto)

    land = sw("r_far", combine(*rm("r_far"), landing(True)), landing(False))
    riders = line("r_riders", p["r_speed"], p["r_len"], p["r_rad"], 0, "EnemyWithoutTower", True,
                  [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_pass")])

    # ------------------------------------------------------------------ the attack
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), attack(0, 100), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Rampage
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_r"], "Targeting", "EnemyWithoutTower",
                   combine(anim("skill", p["q_dur"]), voice("vo_q", p), delayed(p["q_at"] - 1, spin(100), w_auto)))

    # ------------------------------------------------------------------ skill2: E Devastating Charge
    def e_hit(mult):
        return [attack(p["e_dmg"] * mult // 100, p["e_ratio"] * mult // 100),
                {"type": "Knockback", "speed": p["e_kb_speed"], "tick": p["e_kb_t"]}, view("e_hit"), tsfx("e_hit")]

    e_rungs = on_me(delayed(p["e_t2"], sw("e_ride", combine(*rm("e1"), refresh("e2", 60, attack_mult=2 * p["e_warp"])))),
                    delayed(p["e_t3"], sw("e_ride", combine(*rm("e2"), refresh("e3", 60, attack_mult=3 * p["e_warp"])))))
    # E -> R: the landing on a champion with the ult ready plays the Onslaught's landing (a long ride: the long fear)
    e_to_r = sw("r_open", sw("r_cd", NONE, combine(flag("r_cd", p["r_cd"]), refresh("r_far", 2), cview("r_riders"),
                                                   sfx("r"), voice("vo_r", p), land)))
    e_land = combine(anim("skill2_hit", 14), *rm("e_ride"),
                     # the blow on the smash frame (queued on the target: end_effects run on it); the rung is read
                     # now - the flags go below, before the delay ends
                     sw("e3", delayed(p["e_smash"], *e_hit(p["e_max"])),
                        sw("e2", delayed(p["e_smash"], *e_hit(p["e_mid"])), delayed(p["e_smash"], *e_hit(100)))),
                     *rm("e1", "e2", "e3"),
                     refresh("e_haste", p["e_haste_t"], move_speed_mult=p["e_haste"], attack_mult=p["e_warp"]),
                     # a champion where he lands (a projectile from the dash's end_effects is removed unflown)
                     pick(p["e_land_r"], "EnemyChampion", on_me(w_auto, e_to_r)))
    charge = combine(anim("skill2", p["e_dur"]), sfx("e"),
                     refresh("e_ride", 120), refresh("e1", 60, attack_mult=p["e_warp"]), cview("e_dust"), e_rungs,
                     delayed(p["e_go"] - 1, {"type": "MoveToTarget", "speed": p["e_speed"],
                                             "range": p["e_range"] + 20000, "end_effects": [e_land]}))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower", charge)

    # ------------------------------------------------------------------ ult: R Onslaught of Shadows
    ride = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p), cview("r_riders"),
                   refresh("r_ride", p["r_cc"], cc_immune=True),
                   on_me(delayed(p["r_go"] + p["r_far_t"], sw("r_ride", refresh("r_far", 60)))),
                   delayed(p["r_go"] - 1, riders,
                           {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 20000,
                            "end_effects": [*rm("r_ride"), land]}))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_open", None), sw("r_cd", NONE, combine(flag("r_cd", p["r_cd"]), ride))))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring); every
    # picture here is left-right symmetric
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, tag=None, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("r_riders", BIG, 2)]
    views_e = [E("a_hit"), E("q_spin", BIG, 3, False), E("q_hit"), E("w_start", BIG, -1, False), E("w_hit"),
               E("e_dust", FX, -1, False), E("e_hit"), E("r_riders", BIG, 3, False), E("r_land", BIG, -1, False),
               E("r_hit"), E("r_fear")]
    views_b = [B_("q1", "q1", FX, 4), B_("q2", "q2", FX, 4), B_("w_on", "w_aura", BIG, -1),
               B_("e_ride", "e_ride", FX, -1), B_("e_haste", "e_haste", FX, -1)]
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
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
