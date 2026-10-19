"""Build league_quinn.data_champion (top, Range marksman) from the parameters P.

    python tools/kit/build_quinn.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-19: top lane, layout A, Q's blind = a disarm, R = a ride in the main pack plus the add-on's
ride form, Valor circling over her head). TFM2 has three active slots for League's four buttons: Q Blinding Assault is
`skill`, E Vault `skill2`, R Behind Enemy Lines the `ult`; the passive and W Heightened Senses' passive ride in her
attack, W's active (vision) means nothing here and is left out.
  Valor   her eagle (华洛) circles over her head: a following buff picture (`valor`, permanent) put on by her first action
          of each life (`init`; death clears buffs), taken off while he flies Q and while she rides him (R), back on
          when he returns.
  passive Harrier (侵扰): every p_cd ticks Valor marks her next target (`p_ready`; Q, E and R mark too - League's Q and E
          put Harrier on what they hit). Her next attack with the mark on: Valor dives on the target (p_dive) and the
          bolt deals p_dmg + p_ratio% AD more; then W.
  W       Heightened Senses (敏锐感知), passive only: after a Harrier hit, w_as% attack speed and w_ms% move speed for w_t.
  attack  a wrist-crossbow bolt (homing, `Enemy`: towers too) on a_hit.
  skill   Q Blinding Assault (炫目攻势), `Direction` on `EnemyWithoutTower` (q_cast): Valor flies out (q_speed, stops on the
          first enemy, q_range at most) and bursts where he stops: q_dmg + q_ratio% AD to every enemy within q_r. The
          first unit hit is marked (`p_ready` for her); a champion is also disarmed q_blind ticks (League's nearsight:
          data cannot shorten an attack range - the field is unsigned - so the old Quinn's blind). Valor flies back to
          her and circles again.
  skill2  E Vault (旋翔掠杀), `Targeting` on `EnemyWithoutTower` (e_range): she dashes to the target (e_speed); on contact
          e_dmg + e_ratio% AD, a e_stun-tick interrupt, e_slow% slow for e_slow_t, the mark; then she flips back off it
          (MoveBack e_back x e_back_t: about her attack range away).
  ult     R Behind Enemy Lines (深入敌后), `Targeting` on `EnemyChampion` (r_range): she calls Valor down and mounts him
          (r_mount ticks), rides at the target (`MoveToTarget` r_speed, the ride strip held, r_ms% move speed meanwhile)
          and on arrival casts Skystrike (鹰翼天翔): r_dmg + r_ratio% AD to every enemy within r_r, the mark; she jumps off.
          League rides for as long as the player likes, ending with Skystrike on the first attack or cast: data cannot
          change her idle or run picture while she walks, so the main pack rides only inside the ult; the add-on rides
          League's way.
The add-on copy (--native, addons/league_quinn): R mounts her and sets `r_ride` for r_ride_t ticks with r_ride_ms% move
speed; the add-on's display hook draws her riding (r_idle / r_run / r_hit) while it is on, and her next attack, Q or E
- or the ride's end - casts Skystrike first (the `r_ride` switch in every action and the add-on's watch).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_quinn.data_champion")
ID = "league_quinn"
FX = "asset/league/effects/league_quinn_fx"
BIG = "asset/league/effects/league_quinn_big"

# League units x 100 = ours for skill ranges (League's 525 attack range -> 52500). Timings from the strips
# (tools/art/rig_quinn.py MS, 60 ticks a second): the attack 440 ms (atk_dur 26), the bolt off the crossbow's kick on
# frame 3 at 150 ms (a_hit 10); Q 470 ms (q_dur 28), Valor out on frame 2 (q_rel 9); E's dash 120 ms (e_dur 8), the
# flip 300 ms (e_flip 18); R's call 500 ms (r_mount 30), Skystrike's landing 480 ms (r_land 29). League 16.20 (Quinn.bin): passive Harrier every 8 s, mark 4 s, ADRatio 0.4 (+ level part); Q 1025
# range, missile 1550, burst r 210, 20-100 + 80-140% AD + 50% AP, nearsight 1.75 s, cd 11.5-9; W after a Harrier hit
# +15-93% attack speed (by level), +15-45% ms for 2 s; E 600 range, 40-140 + 20% bonus AD, slow 50% decaying over
# 1.5 s, cd 13-8; R channel 2 s, then +40-220% ms ride, Skystrike r 700, 30-210 + 35-100% AD, cd 3 s.
# League's Quinn: 565 +107 hp, 59 +2.4 AD, 28 +4.4 armour, 30 +1.3 MR, 330 move, attack speed 0.668 +3.1%.
# Numbers = the 10-min classic-SDK simulations (top lane 0 against fighter, executioner, lancer, pole_warrior, knight and
# berserker, three lineups, both sides, seeds 1-8, 2026-10-19, placeholder timings): the draft (hp 950, atk 98, Q 50 +90%,
# Harrier 25 +40%, R from 140000) -4.49 (league_volibear +1.31, league_teemo +1.05 in the same batch); R from 60000 -2.58;
# + hp 1000, atk 106, Q 80 +110%, Harrier 40 +60% = P: +2.14 (without R +1.38, without E -0.19).
P = {
    # stats (Range base: 100 +20 attack, 900 +90 hp, 20 +7 defence, 15 +3 mr, 900 +9 move; a ranged top laner gets a
    # little more health and armour against the fighters there)
    "hp": 1000, "hp_g": 95, "atk": 106, "atk_g": 19, "def": 24, "def_g": 8, "mr": 18, "mr_g": 3, "ms": 950, "ms_g": 10,
    "atk_range": 52500, "atk_dur": 26, "atk_cd": 62, "a_hit": 10, "a_speed": 7000, "a_y": -9000,
    # passive Harrier + W Heightened Senses
    "p_cd": 480, "p_dmg": 40, "p_ratio": 60, "w_as": 35, "w_ms": 25, "w_t": 120, "dive_t": 30,
    # Q Blinding Assault
    "q_cd": 600, "q_cast": 95000, "q_dur": 28, "q_rel": 9, "q_range": 100000, "q_speed": 6000, "q_w": 6000,
    "q_r": 21000, "q_dmg": 80, "q_ratio": 110, "q_blind": 45, "q_back": 7000,
    # E Vault
    "e_cd": 660, "e_range": 60000, "e_dur": 8, "e_speed": 4000, "e_dmg": 50, "e_ratio": 60, "e_stun": 6,
    "e_slow": 50, "e_slow_t": 90, "e_back": 4000, "e_back_t": 12, "e_flip": 18,
    # R Behind Enemy Lines + Skystrike
    "r_cd": 2400, "r_range": 60000, "r_mount": 30, "r_speed": 3200, "r_ms": 0, "r_r": 30000, "r_dmg": 150,
    "r_ratio": 100, "r_land": 29,
    # the add-on's ride (League: +40-220% ms, rides until she attacks or casts)
    "r_ride_t": 360, "r_ride_ms": 80,
    "vo_gap": 600,
    # 1 = the copy for addons/league_quinn
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


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def is_champ(*effects):
    """Inside a projectile's applied effects: the unit it hit, when that is a champion (league_sivir Q)."""
    return pick(1, "EnemyChampion", *effects, fp=True)


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, width, target, effects, end=(), penetrate=True, back=False):
    return {"type": "BackToCasterLinearProjectile" if back else "LinearProjectile", "name": n(name),
            "penetrate": penetrate, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": list(end), "speed": speed, "range": rng, "shape": circle(width)}


def burst(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick circle on the point it is started at (a projectile's end): hits the tick it appears."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 2, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """Her line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    nat = bool(p["native"])
    valor_on = refresh("valor", None)
    valor_off = combine(*rm("valor"))
    mark = refresh("p_ready", None)
    # Valor back over her head - in the add-on's copy not while she rides him
    back = sw("r_ride", NONE, valor_on) if nat else valor_on
    # Harrier's watch: every p_cd ticks Valor marks again (a flag on her: nothing reads a buff on the target)
    harrier = on_me({"type": "AddCasted", "casted_type": "Heal", "duration": 1000000, "period": p["p_cd"],
                     "effects": [sw("p_ready", NONE, mark)]})
    life = sw("init", NONE, combine(flag("init", None), valor_on, mark, harrier))

    # ------------------------------------------------------------------ Skystrike (the end of R)
    def skystrike():
        # in the add-on's copy she jumps off Valor here (an attack, Q or E while riding, or the ride's end); the main
        # pack's ride lands with its own CasterAnimation
        land = [anim("ult_land", p["r_land"])] if nat else []
        return combine(*land, sfx("r_land"), cview("r_land"),
                       around(p["r_r"], "EnemyWithoutTower", [attack(p["r_dmg"], p["r_ratio"]), view("r_hit")]),
                       mark, valor_on, *rm("r_ride"), *(rm("r_end") if nat else ()))

    # ------------------------------------------------------------------ attack: the bolt + Harrier + W
    senses = on_me(refresh("w_haste", p["w_t"], attack_speed_mult=p["w_as"], move_speed_mult=p["w_ms"]))
    plain = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    harrier_hit = [attack(p["p_dmg"], p["p_ratio"]), view("p_hit"), tsfx("p_hit"), senses]
    bolt = homing("a_bolt", p["a_speed"], p["a_y"], "Enemy", plain)
    bolt_h = homing("a_bolt", p["a_speed"], p["a_y"], "Enemy", plain + harrier_hit)
    # the dive: Valor leaves her head, swoops on the target, and is back over her dive_t ticks later
    dive = combine(*rm("p_ready"), valor_off, view("p_dive"), sfx("p_dive"),
                   delayed(p["dive_t"], alive(back)))
    shot = combine(sfx("a_shot"), sw("p_ready", combine(dive, delayed(p["a_hit"] - 1, bolt_h)),
                                     delayed(p["a_hit"] - 1, bolt)))
    if nat:
        shot = sw("r_ride", skystrike(), shot)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, shot), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Blinding Assault
    home = line("q_home", p["q_back"], 400000, 1000, "EnemyChampion", [],
                end=[alive(back)], back=True)
    first = [mark, is_champ({"type": "BlockAttack", "tick": p["q_blind"]}, buff("q_blind", p["q_blind"]))]
    boom = burst("q_burst", p["q_r"], [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")])
    out = line("q_bird", p["q_speed"], p["q_range"], p["q_w"], "EnemyWithoutTower", first,
               end=[boom, view("q_burst"), sfx("q_burst"), home], penetrate=False)
    q_cast = combine(valor_off, sfx("q"), voice("vo_q", p), delayed(p["q_rel"] - 1, out),
                     # Valor back on her head if he never returned (she walked out of reach, a long flight)
                     delayed(240, alive(sw("valor", NONE, back))))
    if nat:
        q_cast = combine(sw("r_ride", skystrike()), q_cast)
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_cast"], "Direction", "EnemyWithoutTower",
                   combine(life, q_cast))

    # ------------------------------------------------------------------ skill2: E Vault
    contact = [attack(p["e_dmg"], p["e_ratio"]), {"type": "Stun", "duration": p["e_stun"]},
               buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"), tsfx("e_hit"), mark,
               anim("e_flip", p["e_flip"]), sfx("e_flip"),
               {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]}]
    e_cast = combine(anim("skill2", 60), sfx("e"), voice("vo_e", p),
                     {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000,
                      "end_effects": contact})
    if nat:
        e_cast = combine(sw("r_ride", skystrike()), e_cast)
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(life, e_cast))

    # ------------------------------------------------------------------ ult: R Behind Enemy Lines
    if nat:
        # the add-on's ride: she stays mounted for r_ride_t (drawn r_* by its display hook); her next action or the
        # ride's end (the add-on's watch casts it) is Skystrike
        ride = [refresh("r_ride", p["r_ride_t"], move_speed_mult=p["r_ride_ms"]), cview("r_mount_fx"), sfx("r_ride"),
                # the ride's end: the add-on lays `r_end` on her a tick before `r_ride` runs out; this watch turns it
                # into Skystrike (data cannot act when a buff expires)
                on_me({"type": "AddCasted", "casted_type": "Heal", "duration": p["r_ride_t"] + 10, "period": 1,
                       "effects": [sw("r_end", skystrike())]})]
    else:
        land = [anim("ult_land", p["r_land"]), skystrike()]
        ride = [anim("ult_ride", 240), sfx("r_ride"),
                {"type": "MoveToTarget", "speed": p["r_speed"], "range": 400000, "end_effects": land}]
    ult = action("ult", p["r_mount"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(life, valor_off, anim("ult", p["r_mount"]), cview("r_call"), sfx("r"), voice("vo_r", p),
                         delayed(p["r_mount"] - 1, alive(*ride))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None: {"type": "Animated", "name": n(name), "anim": FX, "tag": tag or name, "repeat": True,
                                 "z": 1}
    views_e = [E("a_hit"), E("p_dive", BIG, 3), E("p_hit"), E("q_hit"), E("q_burst", BIG, 2, False), E("e_hit"),
               E("r_call", BIG, 2), E("r_land", BIG, -1), E("r_hit")]
    if nat:
        views_e.append(E("r_mount_fx", BIG, 2))
    views_p = [Pj("a_bolt"), Pj("q_bird"), Pj("q_home", "q_bird")]
    views_b = [B_("valor", BIG, 3), B_("q_blind", FX, 3), B_("e_slow", FX, 3), B_("w_haste", FX, -1)]
    extra = {}
    if nat:
        extra["passive"] = {"passive_ref": f"{ID}:ride", "params": {k: int(p[k]) for k in ("r_ride_t", "r_ride_ms")}}
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range"], **extra,
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
