"""Build tft_terra.data_champion (the tft pack's twenty-third hero: Terra, top, Melee) from the parameters P.

    python tools/kit/build_terra.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Terra (泰拉) is the earth dragon of Teamfight Tactics set 7.5 (Uncharted Realms): the 5-cost unit TFT7_DragonEarth
(Monolith / Dragon, an AD tank, range 1, 1050 health, 80 AD, 0.65 attack speed, 100 armour and magic resistance, 30/70
mana), a four-legged dragon armoured in rock, her wings folded at her sides. TFT gives her one ability (Earthquake / 地震:
stomp three times, a surrounding quake of physical damage scaling with her armour, magic resistance and AD; when it ends
130-165 armour and magic resistance for 8 s; unstoppable while casting) and the Monolith trait (units on its tiles take
18% less damage). The rest is our own design (the user's pick, 2026-10-31: top lane, plan A 「地震巨岩」):
  passive Monolith Hide (巨岩之躯): p_red% less damage taken, always (TFT's Monolith tile, her own). tft.dll (below):
          a permanent buff on her every life. --plain: her first attack of a life puts the same permanent flag on.
  attack  Rock Claw (岩爪) on `Enemy` (towers too): a_pct% AD.
  skill   Rending Bite (裂地咬), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): she drops her head and
          lunges onto the target (`MoveToTarget` q_speed after q_st ticks) and bites: q_dmg + q_ad% AD + q_def% of her
          armour + magic resistance, q_slow% slower for q_slow_t ticks.
  skill2  Dragon's Roar (龙威咆哮), `Targeting` on `EnemyWithoutTower` (e_range): wings out, a roar: every enemy within e_r
          is taunted e_taunt ticks; a rock shield of e_sh + e_sh_ad% AD for e_sh_t ticks on her.
  ult     Earthquake (地震, TFT's), `Targeting` on `EnemyChampion` (r_range, only in fights): she rears and stomps three
          times (crowd-control immune for the cast, r_dur ticks): at r_t1, r_t2 and r_t3 every enemy within r_r takes
          r_dmg + r_ad% AD + r_def% of her armour + magic resistance; after the third, r_res armour and magic resistance
          for r_res_t ticks.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/terra.rs; the passive is tft_terra:monolith,
params NATIVE_KEYS): the data scales no damage with armour or magic resistance (tft_terra:bite, tft_terra:quake add that
part on each one hit) and has no moment for a life's start or a death. --plain: the armour part is p_plain_def% of
q_def / r_def as flat damage (her armour + magic resistance at mid game). A build of P checks terra.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_terra"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 28000 (a long snout, like tft_syfen's 30000); radii count the unit's collision radius (~15000) on top.
# Timings are placeholders until the strips exist (tools/art/rig_terra.py). Stats start from the tft top tanks'
# (tft_shiohyu hp 1260 atk 84 def 48 mr 38, tft_renni, tft_krug 1200 / 80): Terra is the 5-cost earth dragon, TFT's
# 100 armour and magic resistance, a slow attack.
# Numbers = the 10-min classic-SDK simulations (C:/t/te_sim with C:/t/al_sim/kd.py: top lane 0 against the base fighter,
# executioner, knight, berserker, lancer and pole warrior, three lineups, both sides; 2026-10-31), all --plain: the draft
# (hp 1320, atk 76 every 72, Q 100%, R 50% + 25%, the armour part at 220) +0.10 on seeds 1-8 (tft_shiohyu --plain +1.31
# on the same games); her armour + resistance at mid game is ~250 (level 10.5: 58 + 9 x 10.5 and 48 + 7 x 10.5), atk 82,
# Q 130%, R 70% + 30% +0.62; + hp 1380, attack every 66, taunt 1.5 s +1.28 / +0.69 (seeds 9-16; tft_shiohyu +1.14); +
# atk 84, Q 50% and R 35% of armour + resistance +1.92 / +1.32 = P (a 5-cost a little above the 4-cost control).
P = {
    # stats (Melee, a top tank with attack damage)
    "hp": 1380, "hp_g": 125, "atk": 84, "atk_g": 9, "apw": 0, "apw_g": 0, "def": 58, "def_g": 9, "mr": 48, "mr_g": 7,
    "ms": 990, "ms_g": 10,
    "atk_range": 28000, "atk_dur": 30, "atk_cd": 66, "atk_st": 14, "a_pct": 100,
    # passive Monolith Hide (TFT's Monolith tile: 18% less damage); --plain's mid-game armour + resistance (x100)
    "p_red": 18, "p_plain_def": 250,
    # Rending Bite
    "q_cd": 480, "q_range": 34000, "q_dur": 40, "q_st": 14, "q_speed": 3000, "q_dmg": 40, "q_ad": 130, "q_def": 50,
    "q_slow": 30, "q_slow_t": 90,
    # Dragon's Roar
    "e_cd": 720, "e_range": 30000, "e_dur": 36, "e_st": 14, "e_r": 42000, "e_taunt": 90, "e_sh": 80, "e_sh_ad": 80,
    "e_sh_t": 180,
    # Earthquake (TFT: 160 / 240% of armour + resistance and AD in all, then 130 / 165 of each for 8 s)
    "r_cd": 2400, "r_range": 40000, "r_dur": 110, "r_t1": 30, "r_t2": 58, "r_t3": 86, "r_r": 48000,
    "r_dmg": 30, "r_ad": 70, "r_def": 35, "r_res": 60, "r_res_t": 480,
}
# what tft.dll reads from passive.params (addons/tft/src/terra.rs)
NATIVE_KEYS = ("p_red", "q_def", "r_def")
# names terra.rs uses that need no view: the death cry and the hide (a buff with no picture)
NATIVE_ONLY = {"d", "p_rock"}


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
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone."""
    return around(1000, "AllyOnlySelf", effects)


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ passive (--plain stand-in)
    hide = None if is_native else when("p_rock", combine(), flag("p_rock", None, damaged_reduce=p["p_red"]))

    def rock(key):
        """The armour + magic resistance part of a hit: tft.dll reads her stats; --plain a mid-game flat stand-in."""
        return (native(key), 0) if is_native else (None, p["p_plain_def"] * p[f"{key[0]}_def"] // 100)

    # ------------------------------------------------------------------ attack: Rock Claw
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(hide, sfx("a"), attack(0, p["a_pct"]), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Rending Bite
    q_rock, q_flat = rock("q_bite")
    bite = [attack(p["q_dmg"] + q_flat, p["q_ad"]), q_rock, buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
            view("q_hit"), tsfx("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_st"] - 1, {"type": "MoveToTarget", "speed": p["q_speed"],
                                                             "range": p["q_range"] + 40000,
                                                             "end_effects": [e for e in bite if e is not None]})))

    # ------------------------------------------------------------------ skill2: Dragon's Roar
    taunted = [{"type": "Taunt", "duration": p["e_taunt"]}, buff("e_taunt", p["e_taunt"])]
    roar = delayed(p["e_st"] - 1, sfx("e_taunt"), sfx("e_shield"), cview("e"),
                   on_me(shield(p["e_sh"], p["e_sh_ad"], p["e_sh_t"])), flag("e_shield", p["e_sh_t"]),
                   around(p["e_r"], "EnemyWithoutTower", taunted))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), roar))

    # ------------------------------------------------------------------ ult: Earthquake
    r_rock, r_flat = rock("r_quake")
    quake_hit = [e for e in (attack(p["r_dmg"] + r_flat, p["r_ad"]), r_rock, view("r_hit")) if e is not None]
    stomps = [delayed(p[f"r_t{k}"] - 1, sfx(f"r_stomp{k}"), sfx("r_hit"), cview("r_quake"),
                      around(p["r_r"], "EnemyWithoutTower", quake_hit)) for k in (1, 2, 3)]
    armour = delayed(p["r_t3"], sfx("r_armor"),
                     flag("r_res", p["r_res_t"], defence=p["r_res"], magic_resistance=p["r_res"]))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_vo"), cview("r"), flag("r_on", p["r_dur"], cc_immune=True), *stomps,
                         armour))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the claw and the bite burst on what they hit; the roar's rings and the rear-up dust play on her; each stomp's quake
    # ring lies round her on the ground (z -1, not following: the crack stays where she stomped); the slow, the taunt,
    # the rock shield and the quake's armour are auras (all pictures symmetric: the client never mirrors them)
    views_e = [E("a_hit"), E("q_hit", FX, 3), E("e", BIG, 4), E("r", FX, 3), E("r_quake", BIG, -1, False),
               E("r_hit", FX, 3)]
    views_b = [B_("q_slow", FX, 3), B_("e_taunt", FX, 3), B_("e_shield", BIG, 3), B_("r_res", BIG, 3)]
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
    if is_native:   # tft.dll (addons/tft/src/terra.rs): the hide on every life, the armour part of the bite and quake
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:monolith", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Earthquake as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on bundle
    is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll. The kit's --plain ult: the three
    stomps with the armour part as flat damage, the armour after. The views are the kit's own (tft_terra_*); make_override
    copies them and their sheets."""
    p = dict(P) if p is None else p
    return build(p, False)["ult"]["effect"]


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def check_dll(p, kit):
    """addons/tft/src/terra.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every picture it puts on or plays has a view, and what it registers is what the kit calls."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "terra.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"terra.rs Params::default() differs from P (terra.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    views = {v["name"] for k in ("view_projectiles", "view_effects", "view_buffs") for v in kit[k]}
    used = set(re.findall(r'te\("(\w+)"\)', src))
    unseen = sorted(x for x in used - NATIVE_ONLY if n(x) not in views)
    if not used or unseen:
        raise SystemExit(f"pictures terra.rs plays or puts on have no view: {unseen}")
    for reg in ("monolith", "q_bite", "r_quake"):
        if f'format!("{{ID}}:{reg}")' not in src:
            raise SystemExit(f"terra.rs does not register tft_terra:{reg}")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="the data alone, no tft.dll passive (for the balance sims)")
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
