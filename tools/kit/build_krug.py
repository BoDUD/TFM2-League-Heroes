"""Build tft_krug.data_champion (the tft pack's tenth hero: the Ancient Krug, jungle, Melee) from the parameters P.

    python tools/kit/build_krug.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Ancient Krug (远古石甲虫) is Teamfight Tactics set 18's 3-cost Rift Monster brawler (DA_Krug18, 峡谷野怪 / 斗士, range 1,
1100 health, 80/135 mana: Rock and Roll / 岩之摇滚 - he gains maximum health and rolls into his target, damage from his
AD and health; on death he splits into two Mini Krugs that taunt). The kit is our own design from that (the user's
pick, 2026-10-28: jungle, plan A 「岩之摇滚」); summons cannot walk or attack in data, so the split is a rebirth:
  passive Shattered Rebirth (碎岩重生): the first time each life a blow would kill him (and at most every p_cd ticks)
          he shatters instead: p_t ticks untouchable and unable to act, then he stands up again as a Mini Krug with
          p_hp% of his maximum health, p_as% more attack speed for the rest of that life, and every enemy within p_r
          is taunted p_taunt ticks (p_r from his centre to theirs; tft.dll: the data reads no health; --plain gives him p_red% less damage taken
          from his first action instead, about what one rebirth a life is worth).
  attack  a rock-fist slam on `Enemy` (towers too): 100% AD on atk_st.
  skill   Rock and Roll (岩之摇滚), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too): a stone layer
          (a shield of q_sh + q_sh_ap% AP for q_sh_t ticks), then he curls into a boulder and rolls onto the target
          (MoveToTarget, q_speed); it takes q_dmg + q_ratio% AD + q_hp% of his maximum health and is knocked back
          (q_kb_speed, q_kb ticks).
  skill2  Stone Shell (坚岩外壳), `Targeting` on `EnemyWithoutTower` (e_range): he pulls into his boulder for e_t ticks
          (+e_def armour, +e_mr magic resist) and every enemy within e_r is taunted e_taunt ticks.
  ult     Ancient Landslide (远古崩落), `Targeting` on `EnemyChampion` (r_range): he springs out of sight (r_at ticks
          unseen, untouchable and unstoppable) and crashes down on the target: every enemy within r_r takes r_dmg +
          r_ratio% AD + r_hp% of his maximum health and is thrown up r_up ticks; r_rock_t ticks later the rocks he
          shook loose fall round him, r_rock + r_rock_hp% of his maximum health to every enemy within r_rock_r.

tft.dll (addons/tft/src/krug.rs): the Shattered Rebirth (passive tft_krug:split). A build of P checks krug.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_krug"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's fighters; radii count the unit's collision radius (~15000) on top.
# Timings are placeholders until the strips are rigged (tools/art/rig_krug.py): the slam lands on atk_st.
# Stats start from the pack's jungle tanks (tft_vander 1080 +105 / atk 78 +14 / def 34, league_rammus, league_sejuani):
# a slow heavy brawler - more health and armour, a slower step.
# Numbers = the 10-min classic-SDK simulations (C:/t/kr_sim, Alune's balance sim: jungle against the base ninja, demon,
# hunter, werewolf and vampire, three lineups, both sides; 2026-10-28), all --plain (the rebirth stood in by 15% less
# damage taken): the draft (hp 1120 / atk 74, Q every 10 s 100% AD + 4% health, E every 12 s, R 80% + 5%) -0.82 on seeds
# 1-8 against league_rammus +2.62 - too little damage (4100 dealt to the jungler's 8100). Atk 80, attack every 1.2 s,
# Q 140% + 6%, R 100% + 6% +0.92; with E's taunt 1 s and 22% less damage taken +2.13 / +1.90 (seeds 9-16); instead with
# hp 1200 +118, Q every 8 s and E every 10 s = P: +2.06 / +1.89 (league_rammus +2.62 / +2.14, league_vi +2.08 / +1.99).
# tft.dll's rebirth is not simulated.
P = {
    # stats (Melee, a jungle tank that brawls)
    "hp": 1200, "hp_g": 118, "atk": 80, "atk_g": 14, "apw": 20, "apw_g": 10, "def": 38, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 960, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 32, "atk_cd": 72, "atk_st": 16,
    # passive Shattered Rebirth (TFT set 18: two Mini Krugs that taunt)
    "p_hp": 35, "p_cd": 3600, "p_t": 45, "p_as": 30, "p_r": 40000, "p_taunt": 60, "p_red": 15,
    # Rock and Roll (TFT set 18: + max health (AP), the roll AD + health damage)
    "q_cd": 480, "q_range": 45000, "q_dur": 30, "q_speed": 3200, "q_sh": 80, "q_sh_ap": 60, "q_sh_t": 240,
    "q_dmg": 40, "q_ratio": 140, "q_hp": 6, "q_kb_speed": 2500, "q_kb": 12,
    # Stone Shell
    "e_cd": 600, "e_range": 30000, "e_dur": 24, "e_t": 150, "e_def": 40, "e_mr": 30, "e_r": 28000, "e_taunt": 45,
    # Ancient Landslide
    "r_cd": 3000, "r_range": 50000, "r_dur": 60, "r_go": 15, "r_at": 36, "r_r": 36000,
    "r_dmg": 70, "r_ratio": 100, "r_hp": 6, "r_up": 48, "r_rock_t": 30, "r_rock_r": 40000, "r_rock": 40, "r_rock_hp": 4,
}
# what tft.dll reads from passive.params (addons/tft/src/krug.rs)
NATIVE_KEYS = ("p_hp", "p_cd", "p_t", "p_as", "p_r", "p_taunt")


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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def stone(p):
    """--plain's stand-in for the rebirth: less damage taken, put on (Permanent) by his first action each life."""
    return when("p_stone", combine(), flag("p_stone", None, damaged_reduce=p["p_red"]))


def build(p, is_native=False):
    init = None if is_native else stone(p)

    # ------------------------------------------------------------------ attack: a rock-fist slam
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(init, sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Rock and Roll
    rolled = [sfx("q_hit"), attack(p["q_dmg"], p["q_ratio"], p["q_hp"]),
              {"type": "Knockback", "speed": p["q_kb_speed"], "tick": p["q_kb"]}, view("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(init, sfx("q"), sfx("q_shield"), on_me(shield(p["q_sh"], p["q_sh_ap"], p["q_sh_t"])),
                           cview("q_shield"),
                           {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] + 20000,
                            "end_effects": rolled}))

    # ------------------------------------------------------------------ skill2: Stone Shell
    taunted = [{"type": "Taunt", "duration": p["e_taunt"]}, buff("e_taunt", p["e_taunt"])]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(init, sfx("e"), sfx("e_taunt"), cview("e_cast"),
                            flag("e_shell", p["e_t"], defence=p["e_def"], magic_resistance=p["e_mr"]),
                            around(p["e_r"], "EnemyWithoutTower", taunted)))

    # ------------------------------------------------------------------ ult: Ancient Landslide
    hit = [attack(p["r_dmg"], p["r_ratio"], p["r_hp"]), {"type": "Airborne", "duration": p["r_up"]}, view("r_hit")]
    rocks = combine(sfx("r_rocks"), cview("r_rocks"),
                    around(p["r_rock_r"], "EnemyWithoutTower", [attack(p["r_rock"], 0, p["r_rock_hp"]), view("r_rock_hit")]))
    crash = combine({"type": "Teleport"}, sfx("r_slam"), sfx("r_hit"), cview("r_slam"),
                    around(p["r_r"], "EnemyWithoutTower", hit), delayed(p["r_rock_t"], rocks))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(init, sfx("r"), view("r_mark"),
                         flag("r_air", p["r_at"], damaged_reduce=100, cc_immune=True),
                         delayed(p["r_go"] - 1, cview("r_jump"), {"type": "CasterInvisible", "tick": p["r_at"] - p["r_go"]}),
                         delayed(p["r_at"] - 1, crash)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the crash's shockwave and the falling rocks lie round him on the ground (z -1), drawn round so they read the same
    # on both sides; the leap's dust stays where he sprang from, the landing mark rides the target while he is up.
    # tft.dll plays the rebirth's shatter (p_burst) and reforming (p_up) itself
    views_e = [E("a_hit"), E("q_shield", FX, 3), E("q_hit"), E("e_cast", FX, 3), E("r_jump", FX, 1, False),
               E("r_mark", FX, -1), E("r_slam", BIG, -1, False), E("r_hit"), E("r_rocks", BIG, 3, False),
               E("r_rock_hit")]
    if is_native:
        views_e += [E("p_burst", FX, 3, False), E("p_up", FX, 3)]
    views_b = [B_("e_shell", FX, 3), B_("e_taunt", FX, 4)]
    if is_native:
        views_b += [B_("p_mini", FX, -1)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC", "Shield"],
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
    if is_native:   # tft.dll (addons/tft/src/krug.rs): the Shattered Rebirth
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:split", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/krug.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback) and every name it plays or puts on (`kr("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "krug.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"krug.rs Params::default() differs from P (krug.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'kr\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in DLL_ONLY)
    if not read or missing:
        raise SystemExit(f"krug.rs plays or puts on names the kit does not have: {missing}")


# names only tft.dll uses (its own guard; no picture)
DLL_ONLY = ("p_guard", "p_shatter")


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
