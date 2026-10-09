"""Build league_draven.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_draven.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-10: ADC, Range, League's whole kit with the pros' play). TFM2 has three active slots:
Spinning Axe is `skill`, Stand Aside `skill2`, Whirling Death the `ult`; Blood Rush turns itself on in the attack
(League's W has no cast time and the pros press it after every catch).
  passive League of Draven (德莱文联盟): every axe he catches is one Adoration level more (p_1..p_n, each p_atk attack,
          kept while he lives). A champion he kills with an axe (attack or ult) cashes them in (League's bonus gold):
          p_heal health a level and p_as% attack speed for p_t ticks, and the count starts again.
  attack  An axe thrown at the target (homing, physical 100% AD), released on tick a_st.
  skill   Q Spinning Axe (旋转飞斧): a `None` cast when an enemy is within attack range: one more axe spinning in his
          hands (two at most, each q_hold ticks). The next attack throws a spinning one: q_dmg + q_ratio% AD more.
          It ricochets off the target up into the air and comes down where he stood when it hit, q_fly ticks later -
          a catch circle there the whole time (a picture where he stands: a non-following caster picture, section 8's
          rule). Standing in it (catch_r) when it lands = caught: back in his hands spinning, Blood Rush ready again
          and one Adoration level; walked away = it falls and is gone.
  W       Blood Rush (血性冲刺, automatic): with w_cd off and an enemy champion within w_r, the attack also rushes -
          w_ms% move speed for w_ms_t ticks and w_as% attack speed for w_as_t; w_cd after. A caught axe clears w_cd.
  skill2  E Stand Aside (开道利斧): a `Direction` cast on `EnemyWithoutTower` (e_range); at the release the axes fly
          down a line through everything: e_dmg + e_ratio% AD, knocked back (e_kb speed, e_kb_t ticks) and e_slow%
          slow for e_slow_t.
  ult     R Whirling Death (冷血追命): a `Direction` cast on `EnemyChampionRecentlyAttacked` (r_range: not wasted on a
          champion at full health). Two axe blades fly down the line through every enemy (r_dmg + r_ratio% AD) and
          turn back at the first champion they meet (or at the line's end), flying back to him through everything
          again for the same damage.
  combos  (「加入高手连招」)
          接斧连击 (Q-W juggling): every caught axe re-arms Blood Rush, so the next attack rushes again (above).
          E -> R (击退接大招): a champion Stand Aside hits is marked e_up ticks; R cast while the mark holds throws
                  the blades faster (r_fast) at the knocked-back target.
          R 收割兑现 (R execute + cash-in): an ult kill on a champion cashes the Adoration in like an axe kill.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_draven.data_champion")
ID = "league_draven"
FX = "asset/league/effects/league_draven_fx"
BIG = "asset/league/effects/league_draven_big"

# Numbers: draft c0 (to be balanced in dv_sim against the merged ADCs).
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Draven: 550
    # range, 62 AD +3.6 (high), 675 +104 hp, 29 armour, 330 move, attack speed 0.679
    "hp": 930, "hp_g": 90, "atk": 104, "atk_g": 19, "def": 22, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    # attack: the axe leaves the hand on a_st (retimed to the strips later)
    "atk_range": 55000, "atk_dur": 22, "atk_cd": 60, "a_st": 10, "axe_speed": 6000, "axe_y": 0,
    # passive League of Draven (League: a stack a catch, cashed in on a champion kill for gold)
    "p_n": 6, "p_atk": 4, "p_heal": 25, "p_as": 30, "p_t": 240,
    # Q Spinning Axe (League: +40-60 + 75-115% bonus AD, 5.8 s in hand, two at most, cd 12-8 s)
    "q_cd": 540, "q_range": 55000, "q_dur": 12, "q_hold": 348, "q_dmg": 40, "q_ratio": 55, "q_fly": 42,
    "catch_r": 12000,
    # W Blood Rush (League: +50-70% decaying move speed 1.5 s, +30-50% attack speed 3 s, cd 12 s, reset by a catch)
    "w_cd": 720, "w_r": 70000, "w_ms": 40, "w_ms_t": 90, "w_as": 35, "w_as_t": 180,
    # E Stand Aside (League: 1050 range, 75-235 + 50% bonus AD, knocked aside, 20-40% slow 2 s, cd 18-14 s)
    "e_cd": 900, "e_range": 95000, "e_dur": 24, "e_rel": 12, "e_speed": 6000, "e_len": 105000, "e_rad": 8000,
    "e_y": 0, "e_dmg": 70, "e_ratio": 50, "e_kb": 1800, "e_kb_t": 8, "e_slow": 30, "e_slow_t": 120,
    # R Whirling Death (League: global, 175-375 + 110% bonus AD a pass, turns on the first champion, cd 100-60 s)
    "r_cd": 2700, "r_range": 150000, "r_dur": 30, "r_rel": 16, "r_speed": 4500, "r_fast": 6500, "r_len": 200000,
    "r_rad": 9000, "r_back": 5000, "r_dmg": 110, "r_ratio": 80,
    # combos
    "e_up": 150,
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


def heal(amount):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": 0, "heal_type": "Caster"}


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


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, rng, radius, target, effects, end=()):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius)}


def lob(name, travel, target, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def kill_check(src, reward):
    """On a hit champion, around its damage: the flag before, the living target's clear after, the read on him later
    (league_jinx Get Excited!; a dead target's `Delayed` adds nothing, so the flag stays)."""
    k = f"k_{src}"
    return (combine(*rm(k), flag(k, 40)),
            combine(casted(3, 1, *rm(k)), on_me(delayed(4, sw(k, combine(*rm(k), reward))))))


def build(p):
    N = p["p_n"]
    lv = [f"p_{k}" for k in range(1, N + 1)]

    # ------------------------------------------------------------------ passive: League of Draven
    def climb():
        """One Adoration level more (at most N): the first missing level goes on."""
        out = NONE
        for k in range(N, 0, -1):
            out = sw(lv[k - 1], out, flag(lv[k - 1], None, attack=p["p_atk"]))
        return out

    def cash_in():
        """A champion kill: p_heal a level (the highest level on is the count), the attack-speed burst; the count
        starts again."""
        heal_by = NONE
        for k in range(1, N + 1):             # built inside out: the outermost switch asks for p_N
            heal_by = sw(lv[k - 1], heal(p["p_heal"] * k), heal_by)
        return combine(heal_by, *rm(*lv), refresh("p_glory", p["p_t"], attack_speed_mult=p["p_as"]),
                       cview("p_cash"), sfx("p_cash"))

    k_set, k_read = kill_check("a", on_me(cash_in()))

    # ------------------------------------------------------------------ W Blood Rush (automatic, in the attack)
    rush = combine(refresh("w_cd", p["w_cd"]), refresh("w_ms", p["w_ms_t"], move_speed_mult=p["w_ms"]),
                   refresh("w_as", p["w_as_t"], attack_speed_mult=p["w_as"]), cview("w_cast"), sfx("w"),
                   voice("vo_w", p))
    w_check = sw("w_cd", NONE, pick(p["w_r"], "EnemyChampion", on_me(rush)))

    # ------------------------------------------------------------------ Q Spinning Axe
    def add_axe():
        """One more axe spinning in his hands (two at most); both timers start again."""
        return sw("ax1", combine(refresh("ax1", p["q_hold"]), refresh("ax2", p["q_hold"])),
                  refresh("ax1", p["q_hold"]))

    use_axe = sw("ax2", combine(*rm("ax2")), combine(*rm("ax1")))
    caught = combine(add_axe(), *rm("w_cd"), climb(), cview("q_catch"), sfx("q_catch"))
    # the ricochet: from the hit, a hidden lob onto him lands where he stands q_fly ticks later; the circle and the
    # falling axe are a non-following caster picture started on the same tick (a ViewEffect on his own spot is
    # not shown in game)
    drop = on_me(cview("q_zone"), lob("q_drop", p["q_fly"], "AllyOnlySelf", [
        pick(p["catch_r"], "AllyOnlySelf", flag("q_got", 2), fp=True),
        sw("q_got", combine(*rm("q_got"), caught), combine(view("q_lost"), sfx("q_lost")))]))
    spin_hit = [attack(p["q_dmg"], 100 + p["q_ratio"]), view("q_hit"), tsfx("q_hit"), delayed(1, drop)]
    a_hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    twin = homing("a_twin", p["axe_speed"], p["axe_y"], "EnemyChampion", [k_set, k_read])
    throw = sw("ax1", combine(use_axe, sfx("q_throw"),
                              homing("q_axe", p["axe_speed"], p["axe_y"], "Enemy", spin_hit)),
               combine(sfx("a_throw"), homing("a_axe", p["axe_speed"], p["axe_y"], "Enemy", a_hit)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(w_check, throw, twin), atype="BaseAttack", cancel=True)

    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "None", "EnemyWithoutTower",
                   combine(anim("skill", p["q_dur"]), add_axe(), sfx("q"), voice("vo_q", p)), cancel=True)

    # ------------------------------------------------------------------ E Stand Aside
    e_hit = [attack(p["e_dmg"], p["e_ratio"]), {"type": "Knockback", "speed": p["e_kb"], "tick": p["e_kb_t"]},
             buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"), tsfx("e_hit")]
    e_mark = line("e_twin", p["e_speed"], p["e_len"], p["e_rad"], p["e_y"], "EnemyChampion", True,
                  [on_me(refresh("e_up", p["e_up"]))])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Direction", "EnemyWithoutTower",
                    combine(anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"], sfx("e_throw"),
                                    line("e_axes", p["e_speed"], p["e_len"], p["e_rad"], p["e_y"],
                                         "EnemyWithoutTower", True, e_hit),
                                    e_mark)))

    # ------------------------------------------------------------------ R Whirling Death
    r_kset, r_kread = kill_check("r", on_me(cash_in()))
    r_hits = [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]

    def blades(speed):
        """The damage line out (hidden, through everything), the champion line that turns them (seen)."""
        ret = back("r_back", p["r_back"], p["r_len"] + 100000, p["r_rad"], "EnemyWithoutTower", r_hits)
        ret_k = back("r_backk", p["r_back"], p["r_len"] + 100000, p["r_rad"], "EnemyChampion", [r_kset, r_kread])
        out = line("r_cut", speed, p["r_len"], p["r_rad"], 0, "EnemyWithoutTower", True, r_hits)
        turn = line("r_out", speed, p["r_len"], p["r_rad"], 0, "EnemyChampion", False, [r_kset, r_kread],
                    end=[sfx("r_turn"), ret, ret_k])
        return combine(out, turn)

    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Direction", "EnemyChampionRecentlyAttacked",
                 combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                         delayed(p["r_rel"], sfx("r_throw"),
                                 sw("e_up", combine(*rm("e_up"), blades(p["r_fast"])), blades(p["r_speed"])))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_axe"), P_("q_axe"), P_("e_axes"), P_("r_out", BIG), P_("r_back", BIG)]
    views_e = [E("a_hit"), E("q_hit"), E("q_zone", FX, -1, False), E("q_catch", FX, 3), E("q_lost", FX, 1, False),
               E("w_cast", FX, 3), E("e_hit"), E("r_hit"), E("p_cash", FX, 3)]
    views_b = [B_("ax1", FX, 3), B_("ax2", FX, 3), B_("w_ms", FX, -1), B_("e_slow", FX, -1), B_(f"p_{N}", FX, 3)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range"],
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
