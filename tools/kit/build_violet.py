"""Build tft_violet.data_champion (the tft pack's ninth hero: Violet, jungle, Melee) from the parameters P.

    python tools/kit/build_violet.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Violet is young Vi from Arcane's first act, Powder's big sister and Vander's adopted daughter, a Zaun street fighter
with two huge gauntlets, a 1-cost of Teamfight Tactics set 13 (TFT13_Red, Family / Pit Fighter, range 1, 650 health,
20/65 mana). TFT gives her one ability (1-2-3 Combo / 1-2-3连招: two jabs of 135% AD, then an uppercut of 330% AD that
knocks the target up 0.25 s) and the Pit Fighter trait (15% omnivamp and 6% bonus true damage; once a fight at 50%
health she heals 10% of her max health over 2 s). The rest is our own design (the user's pick, 2026-10-28: jungle,
plan A 「搏击手·1-2-3连招」):
  passive Pit Fighter (搏击手): every hit of hers (the punch, the combo, the dash punch, the slam) adds p_true% AD of
          true damage, and from her first action she has p_vamp% omnivamp; the first time a life drops to p_line%
          health tft.dll heals her p_heal% of her max health over p_t ticks (the data reads no health; --plain has no
          second wind).
  attack  a gauntlet jab on `Enemy` (towers too): 100% AD on atk_st.
  skill   1-2-3 Combo (1-2-3连招), `Targeting` on `EnemyWithoutTower` (q_range, camps too): a jab on q_j1 and a jab on q_j2
          (each q_jab% AD), then on q_j3 an uppercut, q_dmg + q_ad% AD, that throws the target up q_air ticks.
  skill2  Gauntlet Rush (冲拳), `Targeting` on `EnemyWithoutTower` (e_range): she rushes onto the target
          (`MoveToTarget` e_speed) and on arrival punches it (`CasterAnimation` punch, e_hit_t ticks): e_dmg + e_ad%
          AD and a short knock-back (e_kb_speed x e_kb_t: a long one throws the target out of her team's reach,
          league_loris's lesson).
  ult     Undercity Fist (底城怒拳), `Targeting` on `EnemyChampion` (r_range): she leaps at the target (`MoveToTarget`
          r_speed, in the air) and on landing smashes both gauntlets into the ground (`CasterAnimation` slam, r_slam_t
          ticks): every enemy within r_r takes r_dmg + r_ad% AD and is thrown up r_up ticks; then for r_t ticks she
          fights in a fury: r_as% attack speed and r_vamp% more omnivamp, and tft.dll adds r_fam% attack speed for each
          Family ally on her team (tft_powder, tft_vander, league_jinx: TFT's Family, her sister and her father).

tft.dll (addons/tft/src/violet.rs): the second wind by health (passive tft_violet:pugilist) and the fury's Family
bonus (tft_violet:fury). A build of P checks violet.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_violet"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 24000-25000 like the pack's jungle bruisers (league_vi, tft_vander); radii count the unit's
# collision radius (~15000) on top. Timings are placeholders until the strips exist (tools/art/rig_violet.py).
# Stats start from league_vi's (hp 1000 +100, atk 95 +20, def 30, mr 22); TFT's Violet: 650 health, 46 attack, 0.8
# attack speed, 40 armour / magic resist - a 1-cost fighter, lighter than Vi, quicker hands.
# Numbers = the 10-min classic-SDK simulations (C:/t/vo_sim, Alune's copy of the balance sim: jungle lane against the
# base ninja, demon, hunter, werewolf and vampire, three lineups, both sides; 2026-10-28), all --plain (no second wind):
# the draft (hp 980, atk 84, true 8%, fury vamp 10) +2.71 on seeds 1-8 against league_vi +2.08 and tft_vander +0.06;
# true 6% +2.55; + hp 940, fury vamp 5 +2.24; + true 5%, atk 82 = P: +2.06 / +0.93 (seeds 9-16; league_vi +1.99).
P = {
    # stats (Melee, jungle)
    "hp": 940, "hp_g": 100, "atk": 82, "atk_g": 17, "apw": 0, "apw_g": 0, "def": 30, "def_g": 8, "mr": 24, "mr_g": 4,
    "ms": 1050, "ms_g": 11,
    "atk_range": 24000, "atk_dur": 22, "atk_cd": 56, "atk_st": 10,
    # passive Pit Fighter (TFT 2 Pit Fighters: 15% omnivamp, 6% true damage, 10% max health over 2 s at half health)
    "p_true": 5, "p_vamp": 10, "p_line": 50, "p_heal": 15, "p_t": 120,
    # 1-2-3 Combo (TFT: 2 x 135% AD, uppercut 330% AD, knock-up 0.25 s)
    "q_cd": 480, "q_range": 30000, "q_dur": 54, "q_j1": 8, "q_j2": 20, "q_j3": 36, "q_jab": 50, "q_dmg": 40,
    "q_ad": 120, "q_air": 30,
    # Gauntlet Rush
    "e_cd": 600, "e_range": 45000, "e_dur": 24, "e_speed": 5000, "e_dmg": 40, "e_ad": 100, "e_kb_speed": 1200,
    "e_kb_t": 4, "e_hit_t": 16,
    # Undercity Fist
    "r_cd": 3000, "r_range": 50000, "r_dur": 40, "r_speed": 4000, "r_r": 32000, "r_dmg": 120, "r_ad": 130, "r_up": 48,
    "r_as": 40, "r_vamp": 5, "r_fam": 10, "r_t": 300, "r_slam_t": 18,
}
# what tft.dll reads from passive.params (addons/tft/src/violet.rs)
NATIVE_KEYS = ("p_line", "p_heal", "p_t", "r_as", "r_vamp", "r_fam", "r_t")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


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


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def true_part(p):
    """The Pit Fighter's bonus true damage on a hit of hers."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": p["p_true"], "hp_ratio": 0, "target_hp_ratio": 0}


def around(radius, target, effects, at="AroundCaster"):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": at,
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # the Pit Fighter's omnivamp from her first action (a Permanent buff, put on once a life)
    first = when("p_on", combine(), combine(flag("p_on", None), flag("p_vamp", None, vamp=p["p_vamp"])))
    tru = true_part(p)

    # ------------------------------------------------------------------ attack: a gauntlet jab
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(first, sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), tru, view("a_hit"),
                                                       tsfx("a_hit"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: 1-2-3 Combo
    jab = lambda: [attack(0, p["q_jab"]), tru, view("q_jab"), tsfx("q_hit")]
    upper = [attack(p["q_dmg"], p["q_ad"]), tru, {"type": "Airborne", "duration": p["q_air"]}, view("q_up"),
             tsfx("q_up")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, sfx("q"), delayed(p["q_j1"] - 1, *jab()), delayed(p["q_j2"] - 1, sfx("q"), *jab()),
                           delayed(p["q_j3"] - 1, *upper)))

    # ------------------------------------------------------------------ skill2: Gauntlet Rush
    punch = [anim("punch", p["e_hit_t"]), sfx("e_hit"), attack(p["e_dmg"], p["e_ad"]), tru,
             {"type": "Knockback", "speed": p["e_kb_speed"], "tick": p["e_kb_t"]}, view("e_hit")]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(first, sfx("e"), cview("e_dash"),
                            {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000,
                             "end_effects": punch}))

    # ------------------------------------------------------------------ ult: Undercity Fist
    struck = [attack(p["r_dmg"], p["r_ad"]), tru, {"type": "Airborne", "duration": p["r_up"]}, view("r_hit")]
    fury = native("fury") if is_native else on_me(
        flag("r_fury", p["r_t"], attack_speed_mult=p["r_as"], vamp=p["r_vamp"]))
    slam = [anim("slam", p["r_slam_t"]), sfx("r_slam"), sfx("r_buff"), cview("r_slam"),
            around(p["r_r"], "EnemyWithoutTower", struck), fury]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, sfx("r"), sfx("r_jump"),
                         {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 40000,
                          "end_effects": slam}))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the slam's shockwave lies on the ground round her (z -1), drawn round so it reads the same on both sides; the
    # rush's dust (e_dash) is left where she started
    views_e = [E("a_hit"), E("q_jab"), E("q_up"), E("e_dash", FX, 1, False), E("e_hit"),
               E("r_slam", BIG, -1, False), E("r_hit"), E("p_burst", FX, 3)]
    views_b = [B_("r_fury", FX, 3), B_("p_wind", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/violet.rs): the second wind by health, the fury's Family bonus
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:pugilist", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Undercity Fist as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's
    add-on bundle is on the Workshop and the tft mod is not, so his stolen fist cannot call tft.dll (Vander's way).
    The kit's --plain ult - the leap, the slam's knock-up, the flat fury - without the Pit Fighter's first-action flag
    (her passive, not the ult's) and without her true-damage part (also her passive). The views are the kit's own
    (tft_violet_*); make_override copies them and their sheets."""
    p = dict(P) if p is None else p
    p = {**p, "p_true": 0}
    eff = build(p, False)["ult"]["effect"]
    eff["effects"] = [e for e in eff["effects"] if not (e.get("type") == "SwitchByBuff" and e.get("buff_name") == n("p_on"))]
    strip = lambda xs: [x for x in xs if not (x.get("type") == "FixedAttack" and x.get("attack_ratio") == 0)]
    for e in eff["effects"]:
        for s in e.get("end_effects", []):
            if s.get("type") == "RangeEffect":
                s["effects"] = strip(s["effects"])
    return eff


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def names(o):
    """Every `name` in a tree: the buffs, flags, pictures and sounds the kit sets or plays."""
    if isinstance(o, dict):
        return ({o["name"]} if isinstance(o.get("name"), str) else set()).union(*(names(v) for v in o.values()))
    if isinstance(o, list):
        return set().union(*(names(v) for v in o))
    return set()


def check_dll(p, kit):
    """addons/tft/src/violet.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`vo("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "violet.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"violet.rs Params::default() differs from P (violet.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'vo\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"violet.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_violet:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects violet.rs does not register: {sorted(called - registered)}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="the data alone, no tft.dll calls (for the balance sims)")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, not a.plain)
    if not a.set and not a.params:
        check_dll(p, build(p, True))
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
