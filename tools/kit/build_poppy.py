"""Build league_poppy.data_champion (support, Util, tank) from the parameters P.

    python tools/kit/build_poppy.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-18: support, plan A with the add-on league_poppy). TFM2 has three active slots for
League's four buttons, so Steadfast Presence's active rides in her other casts (league_draven's Blood Rush):
  passive Iron Ambassador (钢铁大使): with p_cd off she carries the buckler (`p_rdy`: +p_brange attack range, so the AI
          throws it from afar); her next attack throws it (a homing buckler, p_dmg + p_ap% AP magic on top of the
          blow). It bounces back toward her: a hidden line from her toward the unit hit, p_far long, ends p_fly
          ticks later on the spot where it lies for p_lie ticks (a picture stamped every 15 ticks); walking within
          p_catch of it picks it up (a zone on herself) - a p_sh + p_sh_ad% AD shield for p_sh_t ticks.
  W       Steadfast Presence (坚定风采): passive w_def% armour and MR (a permanent buff her attacks put back after a
          death). Active, with w_cd off, from her attack or a cast whenever an enemy champion is within w_go:
          w_ms% move speed and, for w_t ticks, an aura (an AddCasted pulse on her every w_p ticks) that grounds
          every enemy champion within w_r (`BlockMoveSkill` w_hold: no new dashes). League's interrupt of a dash
          already in flight (knock-up, damage, then grounded + slowed) is the add-on's.
  skill   Q Hammer Shock (圣锤猛击), `Position` on `EnemyWithoutTower` (q_range): on q_rel the hammer hits the spot
          (q_r): q_dmg + q_ratio% AD (+ q_hp% max hp on champions), the ground cracks and slows q_slow% for q_t
          ticks, then ruptures for the same damage.
  skill2  E Heroic Charge (英勇冲锋), `Targeting` on `EnemyChampion` (e_range): she charges (MoveToTarget e_speed);
          on contact e_dmg + e_ratio% AD and she carries the target (Knockback e_kb_speed x e_kb_t, her dash after
          it). Data cannot see walls: the main pack stuns e_stun_m ticks at the end of every carry; the add-on stops
          the carry at a wall and stuns e_stun with the damage again (League), nothing without a wall.
  ult     R Keeper's Verdict (持卫的裁决), `Direction` on `EnemyChampion` (r_range): League's hold-to-charge as a
          smart choice (league_varus Q): two or more enemy champions within r_tap_r -> the quick slam (r_tap_dmg,
          a ring round her, airborne r_up); else she charges r_ch ticks (slowed, aim locked) and the swing sends a
          shockwave down the line (r_len): every enemy champion hit takes r_dmg + r_ratio% AD and flies far away, in
          the air (the main pack: Airborne r_air + Knockback r_kb_speed x r_kb_t, away from her; the add-on: toward his
          own fountain).
The add-on copy (--native, addons/league_poppy): the passive league_poppy:steadfast doubles W's armour / MR under
40% health and interrupts dashes inside the aura; E's contact is league_poppy:charge (the wall check); R's hit is
league_poppy:verdict (the fountain-ward flight).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_poppy.data_champion")
ID = "league_poppy"
FX = "asset/league/effects/league_poppy_fx"
BIG = "asset/league/effects/league_poppy_big"

# League units x 100 = ours for skill ranges (the pack's melee attack is 25000 against League's 125). Release ticks are
# from the strips (rig_poppy.MS). Numbers = the 10-min classic-SDK simulations (support lane 4 against priest, bard,
# enchanter, monk and taoist, three lineups, both sides, seeds 1-8 and 9-16, 2026-10-18; league_alistar +0.97 / +1.12):
# the draft (from league_alistar: hp 1080, atk 78, Q 40 +50%, E 50 +60%, buckler 40) -0.79 / -1.60; Q 60 +70%, E 70 +80%,
# buckler 60 +0.30 / +0.51; + atk 86, hp 1150 +0.48 / +0.57; + E's stun 45 ticks, Q 6% max hp +0.91 / +1.08 = P (+1.00);
# + W 24% and a 160 shield +1.07 / +0.93 (not taken: League's 16% kept).
P = {
    "hp": 1150, "hp_g": 115, "atk": 86, "atk_g": 6, "mp": 20, "mp_g": 10, "def": 38, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 80, "atk_st": 12,
    # passive Iron Ambassador (League: cd 16-6 s, +350 range, 20-199 magic, lands over 1 s, lies 4 s, shield 11-21%
    # max hp for 3 s)
    "p_cd": 480, "p_brange": 30000, "p_speed": 4000, "p_dmg": 60, "p_ap": 30, "p_far": 26000, "p_fly": 40,
    "p_lie": 240, "p_catch": 16000, "p_sh": 120, "p_sh_ad": 60, "p_sh_t": 180,
    # W Steadfast Presence (League: +16% armour / MR, x2 under 40% hp; +40% ms, aura r 400 for 2 s, dashers knocked
    # up 0.5 s, then grounded + 25% slow 2 s, cd 20-12)
    "w_def": 16, "w_cd": 900, "w_go": 40000, "w_r": 35000, "w_t": 120, "w_p": 3, "w_hold": 6, "w_ms": 40,
    # the add-on's interrupt (League: 70-230 +70% AP magic, knock-up 0.5 s, then grounded + 25% slow 2 s; armour / MR
    # doubled under 40% health) and its buckler shield (League: 11-21% max health by level)
    "w_dmg": 70, "w_ap": 70, "w_up": 30, "w_ground": 120, "w_slow": 25, "w_low": 40, "p_sh_min": 11, "p_sh_max": 21,
    # Q Hammer Shock (League: 430 range, 30-130 +75% bonus AD +7-9% max hp, slow 20-32% 1 s, then again, cd 8-4)
    "q_cd": 420, "q_range": 30000, "q_dur": 28, "q_rel": 12, "q_r": 18000, "q_dmg": 60, "q_ratio": 70, "q_hp": 6,
    "q_t": 60, "q_slow": 25, "q_p": 10,
    # E Heroic Charge (League: 475 range, 1800 speed, carry 400, 40-120 +60% bonus AD, wall: again + stun 1.6-2 s,
    # cd 14-10)
    "e_cd": 660, "e_range": 50000, "e_speed": 3500, "e_dmg": 70, "e_ratio": 80, "e_kb_speed": 2500, "e_kb_t": 12,
    "e_stun_m": 45, "e_stun": 105, "e_anim": 16,
    # R Keeper's Verdict (League: tap 100-200 +45% knock-up 1 s r 180; charged 200-400 +90%, 850-1200 range,
    # knock-back up to 3400 toward their fountain; channel up to 4 s, 15% slow; cd 140-100)
    "r_cd": 3600, "r_range": 55000, "r_tap_r": 28000, "r_tap_dmg": 80, "r_tap_ratio": 40, "r_up": 60, "r_tap_t": 20,
    "r_tap_rel": 8, "r_ch": 40, "r_rel": 8, "r_rec": 14, "r_len": 70000, "r_speed": 7000, "r_w": 9000,
    "r_dmg": 150, "r_ratio": 70, "r_kb_speed": 6000, "r_kb_t": 25, "r_air": 25,
    # the add-on's flight toward his own fountain (League: up to 3400 units, a quarter of the map)
    "r_far": 150000, "r_far_speed": 6000,
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


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=(), y=5000):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, end, target="EnemyWithoutTower", seen=""):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def build(p):
    nat = bool(p["native"])

    # ------------------------------------------------------------------ W Steadfast Presence
    w_passive = sw("w_pas", NONE, flag("w_pas", None, defence_mult=p["w_def"], magic_resistance_mult=p["w_def"]))
    pulse = around(p["w_r"], "EnemyChampion", [{"type": "BlockMoveSkill", "tick": p["w_hold"]}])
    # (the add-on grounds only the enemies it catches dashing: no pulses in its copy)
    grounds = [] if nat else [pulse, on_me(casted(p["w_t"], p["w_p"], pulse))]
    steadfast = combine(flag("w_cd", p["w_cd"]), refresh("w_ms", p["w_t"], move_speed_mult=p["w_ms"]),
                        refresh("w_on", p["w_t"]), cview("w_cast"), sfx("w"), voice("vo_w", p), *grounds)
    w_check = combine(w_passive, sw("w_cd", NONE, pick(p["w_go"], "EnemyChampion", on_me(steadfast))))

    # ------------------------------------------------------------------ passive Iron Ambassador (in the attack)
    give = native("pick") if nat else {"type": "Shield", "amount": p["p_sh"], "attack_ratio": p["p_sh_ad"], "ap_ratio": 0,
                                         "tick": p["p_sh_t"]}
    shield = on_me(give, flag("p_shown", p["p_sh_t"]), delayed(p["p_sh_t"], *rm("p_shown")))
    grab = sw("p_got", NONE, combine(flag("p_got", p["p_lie"]), shield, cview("p_pick"), sfx("p_pick")))
    lying = [delayed(k, sw("p_got", NONE, view("p_lie"))) for k in range(0, p["p_lie"], 15)]
    lands = [sfx("p_land"), field("p_ground", p["p_catch"], p["p_lie"], 3, [grab], target="AllyOnlySelf", first=0),
             *lying]
    bounce = line("p_bounce", -(-p["p_far"] // p["p_fly"]), p["p_far"], 1000, "EnemyWithoutTower", True, [],
                  end=lands)
    ready = combine(flag("p_rdy", None, range=p["p_brange"]))
    throw = combine(*rm("p_rdy", "p_got"), flag("p_cd", p["p_cd"]), on_me(delayed(p["p_cd"], ready)), sfx("p_throw"),
                    homing("p_buckler", "Enemy", [attack(0, 100), ap(p["p_dmg"], p["p_ap"]), view("a_hit"),
                                                  tsfx("p_hit"), delayed(1, bounce)], p["p_speed"]))
    # after a death (a new entity: no flags) the buckler is back at once
    rearm = sw("p_cd", NONE, sw("p_rdy", NONE, ready))
    blow = combine(attack(0, 100), view("a_hit"), tsfx("a_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(w_check, rearm, sw("p_rdy", throw, blow)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Hammer Shock
    def shock(name):
        return [view(name), sfx(name),
                zone(name + "_z", p["q_r"], [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")]),
                zone(name + "_c", p["q_r"], [attack(0, 0, p["q_hp"])], target="EnemyChampion")]
    crack = field("q_field", p["q_r"], p["q_t"], p["q_p"],
                  [buff("q_slow", p["q_p"] + 2, move_speed_mult=-p["q_slow"])], first=0)
    cracks = [delayed(k, view("q_crack")) for k in range(0, p["q_t"], 15)]
    q_land = [*shock("q_slam"), crack, *cracks, delayed(p["q_t"], *shock("q_burst"))]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(w_check, sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, lob("q_drop", 1, q_land))))

    # ------------------------------------------------------------------ skill2: E Heroic Charge
    wall = [native("charge")] if nat else [delayed(p["e_kb_t"], {"type": "Stun", "duration": p["e_stun_m"]},
                                                   buff("e_stun", p["e_stun_m"]))]
    push = [] if nat else [{"type": "Knockback", "speed": p["e_kb_speed"], "tick": p["e_kb_t"]}]
    contact = [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit"), *push, *wall]
    follow = {"type": "MoveToTarget", "speed": p["e_kb_speed"], "range": p["e_kb_speed"] * p["e_kb_t"] + 20000,
              "end_effects": []}
    charge = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000,
              "end_effects": [*contact, delayed(2, follow)]}
    skill2 = action("skill2", p["e_anim"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(w_check, sfx("e"), voice("vo_e", p), anim("skill2", p["e_anim"]), charge))

    # ------------------------------------------------------------------ ult: R Keeper's Verdict
    if nat:
        fly = [native("verdict")]
    else:
        # League's charged Verdict sends them flying far (up to 3400 units, a quarter of the map): knocked up for the
        # whole flight and knocked back 150000 (an Airborne beside the Knockback still lets it carry them - measured)
        fly = [{"type": "Airborne", "duration": p["r_air"]}, {"type": "Knockback", "speed": p["r_kb_speed"], "tick": p["r_kb_t"]}]
    struck = [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit"), *fly]
    wave = line("r_wave", p["r_speed"], p["r_len"], p["r_w"], "EnemyChampion", True, struck)
    full = combine(anim("ult_charge", p["r_ch"]), refresh("r_slow", p["r_ch"], move_speed_mult=-15),
                   cview("r_charge"), sfx("r_charge"), voice("vo_r", p),
                   delayed(p["r_ch"], anim("ult", p["r_rel"] + p["r_rec"]), sfx("r_swing")),
                   delayed(p["r_ch"] + p["r_rel"] - 1, alive(wave)))
    tap = combine(anim("ult_tap", p["r_tap_t"]), sfx("r_tap"), voice("vo_r", p),
                  delayed(p["r_tap_rel"] - 1, alive(cview("r_tap"), around(p["r_tap_r"], "EnemyWithoutTower", [
                      attack(p["r_tap_dmg"], p["r_tap_ratio"]), {"type": "Airborne", "duration": p["r_up"]},
                      view("r_hit"), tsfx("r_hit")]))))
    count = around(p["r_tap_r"], "EnemyChampion", [sw("t1", flag("t2", 3), flag("t1", 3))])
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Direction", "EnemyChampion",
                 combine(*rm("t1", "t2"), count, delayed(1, sw("t2", tap, full))), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                 "z": 2}
    views_p = [Pj("p_buckler"), Pj("r_wave", BIG)]
    # (the pack's 19 pictures, tools/art/pack_poppy_fx.py; w_block / e_wall are the add-on's interrupt and wall slam)
    views_e = [E("a_hit"), E("p_lie", FX, -1, False), E("p_pick"), E("w_cast", BIG, -1),
               E("q_slam", BIG, -1, False), E("q_burst", BIG, -1, False), E("q_crack", BIG, -2, False), E("q_hit"),
               E("e_hit"), E("r_charge", BIG, 3), E("r_tap", BIG, -1, False), E("r_hit")]
    # w_block / e_wall: buffs the add-on hangs on the enemy it catches dashing / slams into a wall (pictures by name)
    views_b = [B_("p_shown", FX, -1), B_("w_on", BIG, -1), B_("e_stun"), *([B_("w_block"), B_("e_wall")] if nat else [])]
    extra = {}
    if nat:
        extra["passive"] = {"passive_ref": f"{ID}:steadfast", "params": {
            k: p[k] for k in ("w_def", "w_low", "w_r", "w_dmg", "w_ap", "w_up", "w_ground", "w_slow", "e_dmg", "e_ratio",
                              "e_kb_speed", "e_kb_t", "e_stun", "p_sh_min", "p_sh_max", "p_sh_t", "r_kb_speed", "r_kb_t",
                              "r_air", "r_far", "r_far_speed")}}
    return {
        "id": ID, "category": "Util", "tags": ["AD", "Melee", "Tank", "CC", "Shield"], **extra,
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
