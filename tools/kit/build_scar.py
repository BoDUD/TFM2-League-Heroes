"""Build tft_scar.data_champion (the tft pack's eleventh hero: Scar, top, Melee) from the parameters P.

    python tools/kit/build_scar.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Scar is the Firelights' lookout from Arcane, Ekko's right hand, a lanky Zaunite behind a skull mask with a long spear:
a 3-cost of Teamfight Tactics set 13 (TFT13_FlyGuy, Firelight / Watcher, an AP tank, range 1, 800 health, 80/170 mana).
TFT gives him one ability (Puddle Jumper Surprise / 水坑狙击惊喜: bombs at the 3 nearest enemies, each stunned 1.5 s and
dealt 80-240 magic damage; he heals 245-330) and two traits: Firelight (every 6 s the Firelights dash on their
hoverboards, attack, and heal 25-45% of the damage they took since the last dash) and Watcher (15-40% damage
reduction, 30-50% above half health). The rest is our own design (the user's pick, 2026-10-28: top lane, plan A
「野火坦克」):
  passive Firelight Dash (野火冲刺) + Watcher (监察): every p_cd ticks his next attack becomes a hoverboard dash
          (`MoveToTarget` p_speed, his `surf` frames) that strikes for p_dmg + p_ad% AD + p_ap% AP; tft.dll then heals
          him p_heal% of the damage he took since the last dash (--plain: a flat p_flat + p_flat_ap% AP). Watcher:
          tft.dll gives him w_hi% damage reduction at or above w_line% health and w_lo% under it (the data reads no
          health; --plain: w_lo% from his first action).
  attack  a spear thrust on `Enemy` (towers too): 100% AD on atk_st.
  skill   Puddle Jumper Surprise (水坑狙击惊喜), `Targeting` on `EnemyWithoutTower` (q_range, camps too): he flings
          bombs on q_rel - tft.dll throws one at each of the q_n nearest enemies within q_range (--plain: the AI's
          target and q_n - 1 random ones) - each q_dmg + q_ap% AP magic damage and a q_stun-tick stun; he heals
          q_heal + q_heal_ap% AP.
  skill2  Spear Sweep (长矛横扫), `Targeting` on `EnemyWithoutTower` (e_range): on e_st a sweep through the cone in
          front of him (`DirDot` e_r, e_cone): e_dmg + e_ad% AD + e_hp% of his maximum health and a knock-back
          (e_kb_speed x e_kb_t).
  ult     Firelight Raid (野火突袭), `Targeting` on `EnemyChampion` (r_range): he jumps on his hoverboard and rides at
          the target (`MoveToTarget` r_speed, his `ride` frames, unstoppable), dropping fire bombs at r_b1 and r_b2
          (r_bomb + r_bomb_ap% AP to every enemy within r_bomb_r of him); on arrival (his `land` frames) a last blast,
          r_dmg + r_ap% AP to every enemy within r_r, thrown up r_up ticks, and he guards r_t ticks with r_dr% damage
          reduction.

tft.dll (addons/tft/src/scar.rs): the dash's heal by damage taken and Watcher by health (passive tft_scar:firelight),
the bombs at the nearest enemies (tft_scar:bombs, each tft_scar:bomb). A build of P checks scar.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_scar"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's top fighters; radii count the unit's collision radius (~15000) on top.
# Timings follow the strips (tools/art/rig_scar.py MS): the thrust lands at 233 ms (atk_st 14, in a_thrust from
# 133 ms), the bombs fly at 300 ms (q_rel 18, in q_throw from 250 ms), the sweep at 200 ms (e_st 12, in e_sweep from
# 150 ms); the dash plays `surf` (p_surf_t, 400 ms), the raid `ride` for the cast (r_dur, 833 ms: the hop and the board)
# and `land` on arrival (r_land_t, 300 ms). Stats start from the pack's top tanks
# (tft_kobuko hp 1110 +110, def 36, mr 28; league_ornn, league_malphite) with ability power for the bombs and the raid.
# Numbers = the 10-min classic-SDK simulations (C:/t/sc_sim, Alune's copy of the balance sim: top lane against the base
# fighter, executioner, knight, berserker, lancer and pole warrior, three lineups, both sides; 2026-10-28), all --plain
# (the dash heals a flat amount, Watcher's lower reduction always on): the draft (hp 1080, atk 70, apw 30, Q 50 + 60%,
# R 80 + 80%) -0.06 on seeds 1-8 against tft_kobuko --plain +1.99 and league_sett +2.07; + atk 80, apw 40, Q 70 + 80%,
# R 120 + 100% +1.66; + hp 1150, dash 50, E 60 + 90% +2.54; between = P: +2.86 / +1.97 (seeds 9-16; tft_kobuko +2.90).
P = {
    # stats (Melee, a top tank with ability power)
    "hp": 1120, "hp_g": 110, "atk": 80, "atk_g": 11, "apw": 40, "apw_g": 12, "def": 36, "def_g": 8, "mr": 32, "mr_g": 5,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 72, "atk_st": 14,
    # passive Firelight Dash (TFT: every 6 s, heal 25-45% of the damage taken since the last dash) + Watcher (TFT 2
    # Watchers: 15% damage reduction, 30% above half health)
    "p_cd": 360, "p_speed": 4000, "p_surf_t": 24, "p_dmg": 40, "p_ad": 110, "p_ap": 30, "p_heal": 25,
    "p_flat": 40, "p_flat_ap": 40, "w_line": 50, "w_lo": 10, "w_hi": 20,
    # Puddle Jumper Surprise (TFT: 3 nearest, stun 1.5 s, 80-240 magic, heal 245-330)
    "q_cd": 600, "q_range": 45000, "q_dur": 40, "q_rel": 18, "q_n": 3, "q_speed": 2400, "q_dmg": 70, "q_ap": 80,
    "q_stun": 60, "q_heal": 60, "q_heal_ap": 60,
    # Spear Sweep
    "e_cd": 540, "e_range": 30000, "e_dur": 26, "e_st": 12, "e_r": 40000, "e_cone": 600, "e_dmg": 50, "e_ad": 80,
    "e_hp": 2, "e_kb_speed": 1500, "e_kb_t": 6,
    # Firelight Raid
    "r_cd": 3000, "r_range": 50000, "r_dur": 50, "r_speed": 3200, "r_b1": 8, "r_b2": 16, "r_bomb_r": 22000,
    "r_bomb": 40, "r_bomb_ap": 40, "r_r": 32000, "r_dmg": 120, "r_ap": 100, "r_up": 30, "r_dr": 40, "r_t": 240, "r_land_t": 18,
}
# what tft.dll reads from passive.params (addons/tft/src/scar.rs), and the names only it puts on (no view: Watcher's
# reduction has no picture)
NATIVE_ONLY = ("w_watch",)
NATIVE_KEYS = ("p_heal", "w_line", "w_lo", "w_hi", "q_range", "q_n", "q_speed", "q_dmg", "q_ap", "q_stun")


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


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


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


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap_attack(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def heal(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Caster"}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone."""
    return around(1000, "AllyOnlySelf", effects)


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain: Watcher's lower damage reduction from his first action (a Permanent buff, put on once a life)
    first = None if is_native else when("w_on", combine(), combine(flag("w_on", None),
                                                                    flag("w_watch", None, damaged_reduce=p["w_lo"])))

    # ------------------------------------------------------------------ attack: a spear thrust, or the Firelight Dash
    # the dash is ready when p_cool is off; it puts p_cool on for p_cd ticks and p_surf on for 2 ticks, which tft.dll
    # reads to heal him by the damage he took since the last one
    thrust = delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"))
    struck = [sfx("p_hit"), attack(p["p_dmg"], p["p_ad"]), ap_attack(0, p["p_ap"]), view("p_hit"),
              flag("p_surf", 2) if is_native else on_me(heal(p["p_flat"], p["p_flat_ap"]))]
    dash = combine(flag("p_cool", p["p_cd"]), sfx("p"), anim("surf", p["p_surf_t"]),
                   {"type": "MoveToTarget", "speed": p["p_speed"], "range": p["atk_range"] + 40000,
                    "end_effects": struck})
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(first, sfx("a"), when("p_cool", thrust, dash)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Puddle Jumper Surprise
    bomb_hit = [ap_attack(p["q_dmg"], p["q_ap"]), {"type": "Stun", "duration": p["q_stun"]}, buff("q_stun", p["q_stun"]),
                view("q_hit"), tsfx("q_hit")]
    if is_native:   # tft.dll: one bomb at each of the q_n nearest enemies
        bombs = native("bombs")
    else:           # the AI's target, then q_n - 1 random ones (they may repeat)
        bomb = homing("q_bomb", "EnemyWithoutTower", bomb_hit, p["q_speed"])
        bombs = combine(bomb, *[{"type": "RandomTarget", "range": p["q_range"], "casting_target": "EnemyWithoutTower",
                                 "from_projectile": False, "effects": [bomb]} for _ in range(p["q_n"] - 1)])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, sfx("q"), sfx("q_vo"),
                           delayed(p["q_rel"] - 1, bombs, on_me(heal(p["q_heal"], p["q_heal_ap"])), sfx("p_heal"))))

    # ------------------------------------------------------------------ skill2: Spear Sweep
    swept = [attack(p["e_dmg"], p["e_ad"], p["e_hp"]), {"type": "Knockback", "speed": p["e_kb_speed"],
                                                        "tick": p["e_kb_t"]}, view("e_hit"), tsfx("e_hit")]
    cone = {"DirDot": {"radius": p["e_r"], "range": p["e_cone"]}}
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(first, sfx("e"), delayed(p["e_st"] - 1, around(0, "EnemyWithoutTower", swept,
                                                                         {"Forward": {"offset": 1000}}, cone))))

    # ------------------------------------------------------------------ ult: Firelight Raid
    fire = lambda: delayed(0, sfx("r_bomb"), cview("r_bomb"),
                           around(p["r_bomb_r"], "EnemyWithoutTower", [ap_attack(p["r_bomb"], p["r_bomb_ap"]),
                                                                       view("r_hit")]))
    land = [anim("land", p["r_land_t"]), sfx("r_mines"), sfx("r_guard"), cview("r_land"),
            around(p["r_r"], "EnemyWithoutTower", [ap_attack(p["r_dmg"], p["r_ap"]),
                                                   {"type": "Airborne", "duration": p["r_up"]}, view("r_hit")]),
            flag("r_guard", p["r_t"], damaged_reduce=p["r_dr"])]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, sfx("r"), anim("ride", p["r_dur"]), flag("r_air", p["r_dur"], cc_immune=True),
                         {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 40000,
                          "end_effects": land},
                         delayed(p["r_b1"] - 1, fire()), delayed(p["r_b2"] - 1, fire())))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the bombs fly as round pictures (the same turned); the raid's fire bombs burst on the ground where he passed and
    # its last blast lies round him (z -1, drawn round: the same on both sides); the hoverboard and the sweep are in
    # his own frames (surf, ride, skill2). tft.dll plays q_hit on what its bombs hit and p_heal on the dash's heal
    views_p = [B_("q_bomb")]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("e_hit"), E("r_bomb", FX, -1, False), E("r_land", BIG, -1, False),
               E("r_hit")]
    if is_native:
        views_e.append(E("p_heal", FX, 3))
    views_b = [B_("q_stun", FX, 3), B_("r_guard", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AP", "Melee", "Tank", "CC", "Heal"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/scar.rs): the dash's heal, Watcher, the bombs
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:firelight", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


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
    """addons/tft/src/scar.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every name it plays or puts on (`sc("...")`) is the kit's, and every Native the kit calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "scar.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"scar.rs Params::default() differs from P (scar.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'sc\("(\w+)"\)', src)) - set(NATIVE_ONLY)
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"scar.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_scar:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects scar.rs does not register: {sorted(called - registered)}")


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
