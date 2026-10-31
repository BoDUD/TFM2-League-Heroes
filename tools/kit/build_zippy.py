"""Build tft_zippy.data_champion (the tft pack's twenty-fourth hero: Zippy, jungle, Melee) from the parameters P.

    python tools/kit/build_zippy.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Zippy (呲呲) is the guild dragon of Teamfight Tactics set 7 (Dragonlands): the 3-cost unit TFT7_DragonGuild (Guild /
Dragon, an AD fighter, range 1, 800 health, 85 AD, 0.85 attack speed, 60 armour and magic resistance, 0/50 mana), a
little bipedal raptor built on Kled's mount, with no rider. TFT gives it one ability (Somersault Assault / 翻滚突袭: a
375-650 shield for 2 s, then 340-1050% AD physical damage to the enemy with the highest percent health, stunning and
knocking it back slightly) and the Guild trait (each guild member raises a team bonus; Zippy's is armour and magic
resistance). The rest is our own design (the user's pick, 2026-10-31: jungle, plan A 「冒险家突击」):
  passive Adventurer's Spirit (冒险家之魂): p_def armour and magic resistance for each allied champion within p_r
          (p_max at most). tft.dll (below): counted every CHECK ticks. --plain: every attack puts p_plain allies' worth
          on it for p_plain_t ticks.
  attack  Claw Kick (利爪踢) on `Enemy` (towers too): a_pct% AD.
  skill   Backflip Kick (后空翻踢), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): it flips over and
          kicks with both feet at q_st: q_dmg + q_ad% AD, the target knocked up q_up ticks.
  skill2  Rolling Charge (翻滚冲锋), `Targeting` on `EnemyWithoutTower` (e_range): it curls into a ball and rolls at the
          target (a penetrating `RushTime`, e_speed a tick for e_t ticks): every enemy rolled over takes e_dmg + e_ad%
          AD; allied champions within e_ar of where it starts (it too) are e_ms% faster for e_ms_t ticks.
  ult     Somersault Assault (翻滚突袭, TFT's), `Targeting` on `EnemyChampion` (r_range, only in fights): a shield of
          r_sh + r_sh_ad% AD for r_sh_t ticks at once; at r_go it springs up and leaps (crowd-control immune until it
          lands) at the enemy champion with the HIGHEST PERCENT HEALTH within r_range (`tft_zippy:leap`, tft.dll:
          r_speed a tick for at most r_t ticks): landing, r_dmg + r_ad% AD, a stun of r_stun ticks and a short knockback
          (r_kb a tick for r_kb_t ticks). --plain: `MoveToTarget` onto the AI's target and the same blow.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/zippy.rs; the passive is
tft_zippy:guild, params NATIVE_KEYS): the data cannot count allies round it nor read anyone's health. A build of P
checks zippy.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_zippy"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 26000 (a short snout and a long kicking leg); radii count the unit's collision radius (~15000) on
# top. Timings are placeholders until the strips exist (tools/art/rig_zippy.py). Stats start from the tft junglers'
# (tft_syfen hp 1150 atk 84, tft_vander 1080 / 78, tft_smeech 940 / 90): Zippy is the 3-cost raptor, a quick fighter.
# Numbers = the 10-min classic-SDK simulations (C:/t/zz_sim with C:/t/al_sim/kd.py: jungle lane 1 against the base
# ninja, demon, hunter, werewolf and vampire, three lineups, both sides; 2026-10-31), all --plain: the draft (hp 1060,
# atk 80, Q 150%, E 90% and 25% speed, R 260%) +3.03 on seeds 1-8 (tft_syfen --plain +2.31, tft_vander +1.73 on the
# same games); hp 1000, atk 76, R 200%, speed 15% +2.42; + Q 130%, E 70% +0.21 / +1.29 (seeds 9-16); between the two
# (hp 1020, atk 78, Q 140%, E 80% and 20% speed, R 220%) +1.85 on seeds 1-16 (tft_vander +1.73 / +1.48) = P: the
# 3-cost a little above the 3-cost control.
P = {
    # stats (Melee, a jungle fighter with attack damage)
    "hp": 1020, "hp_g": 106, "atk": 78, "atk_g": 13, "apw": 0, "apw_g": 0, "def": 38, "def_g": 7, "mr": 30, "mr_g": 5,
    "ms": 1070, "ms_g": 10,
    "atk_range": 26000, "atk_dur": 30, "atk_cd": 58, "atk_st": 12, "a_pct": 100,
    # passive Adventurer's Spirit (TFT's Guild bonus for Zippy: armour and magic resistance)
    "p_r": 50000, "p_def": 10, "p_max": 4, "p_plain": 2, "p_plain_t": 120,
    # Backflip Kick
    "q_cd": 420, "q_range": 30000, "q_dur": 40, "q_st": 16, "q_dmg": 30, "q_ad": 140, "q_up": 40,
    # Rolling Charge
    "e_cd": 600, "e_range": 60000, "e_dur": 30, "e_st": 8, "e_speed": 3500, "e_t": 14, "e_dmg": 40, "e_ad": 80,
    "e_ar": 50000, "e_ms": 20, "e_ms_t": 150,
    # Somersault Assault (TFT: a 375 / 450 / 650 shield for 2 s, 340 / 540 / 1050% AD, a stun and a short knockback)
    "r_cd": 2400, "r_range": 70000, "r_dur": 50, "r_go": 12, "r_sh": 120, "r_sh_ad": 100, "r_sh_t": 120,
    "r_speed": 4000, "r_t": 20, "r_dmg": 80, "r_ad": 220, "r_stun": 90, "r_kb": 1500, "r_kb_t": 8,
}
# what tft.dll reads from passive.params (addons/tft/src/zippy.rs)
NATIVE_KEYS = ("p_r", "p_def", "p_max", "r_range", "r_speed", "r_t", "r_dmg", "r_ad", "r_stun", "r_kb", "r_kb_t")
# names zippy.rs uses that need no view: sounds (the death cry, the guild's chime, the landing)
NATIVE_ONLY = {"d", "p", "r_land"}


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
    """Effects on it alone."""
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
    guild = None if is_native else when("p_guild", combine(), flag("p_guild", p["p_plain_t"],
                                                                  defence=p["p_def"] * p["p_plain"],
                                                                  magic_resistance=p["p_def"] * p["p_plain"]))

    # ------------------------------------------------------------------ attack: Claw Kick
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(guild, sfx("a"), attack(0, p["a_pct"]), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Backflip Kick
    kick = delayed(p["q_st"] - 1, attack(p["q_dmg"], p["q_ad"]), {"type": "Airborne", "duration": p["q_up"]},
                   view("q_hit"), tsfx("q_hit"))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), kick))

    # ------------------------------------------------------------------ skill2: Rolling Charge
    rolled = [attack(p["e_dmg"], p["e_ad"]), view("e_hit"), tsfx("e_hit")]
    roll = {"type": "RushTime", "speed": p["e_speed"], "tick": p["e_t"], "range": 1000,
            "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": [T(e) for e in rolled]}
    cheer = around(p["e_ar"], "AllyChampion", [buff("e_speed", p["e_ms_t"], move_speed_mult=p["e_ms"])])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), sfx("e_speed"), cheer,
                            delayed(p["e_st"] - 1, sfx("e_roll"), cview("e"), roll)))

    # ------------------------------------------------------------------ ult: Somersault Assault
    if is_native:   # tft.dll: the enemy champion with the highest percent health; the blow where it lands
        leap = native("leap")
    else:
        blow = [attack(p["r_dmg"], p["r_ad"]), {"type": "Stun", "duration": p["r_stun"]},
                {"type": "Knockback", "speed": p["r_kb"], "tick": p["r_kb_t"]}, view("r_hit"), tsfx("r_hit")]
        leap = {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 40000, "end_effects": blow}
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_vo"), sfx("r_shield"), on_me(shield(p["r_sh"], p["r_sh_ad"], p["r_sh_t"])),
                         flag("r_shield", p["r_sh_t"]), flag("r_on", p["r_go"] + p["r_t"], cc_immune=True),
                         delayed(p["r_go"] - 1, sfx("r_spin"), cview("r"), leap)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the kicks, the roll and the crash burst on what they hit; the roll's dust stays where it set off and the leap's
    # spring-up dust where it sprang (not following); the speed, the shield and the guild's armour are auras (all
    # pictures symmetric: the client never mirrors them)
    views_e = [E("a_hit"), E("q_hit", FX, 3), E("e", FX, 1, False), E("e_hit", FX, 3), E("r", FX, 1, False),
               E("r_hit", BIG, 4)]
    views_b = [B_("p_guild", FX, 3), B_("e_speed", FX, 3), B_("r_shield", BIG, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC", "Shield"],
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
    if is_native:   # tft.dll (addons/tft/src/zippy.rs): the allies counted, the leap at the healthiest
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:guild", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Somersault Assault as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's
    add-on bundle is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll. The kit's --plain
    ult: the shield, then the leap onto his target and the blow. The views are the kit's own (tft_zippy_*);
    make_override copies them and their sheets."""
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
    """addons/tft/src/zippy.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every picture it puts on or plays has a view, and what it registers is what the kit calls."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "zippy.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"zippy.rs Params::default() differs from P (zippy.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    views = {v["name"] for k in ("view_projectiles", "view_effects", "view_buffs") for v in kit[k]}
    used = set(re.findall(r'zp\("(\w+)"\)', src))
    unseen = sorted(x for x in used - NATIVE_ONLY if n(x) not in views)
    if not used or unseen:
        raise SystemExit(f"pictures zippy.rs plays or puts on have no view: {unseen}")
    for reg in ("guild", "leap", "hop"):
        if f'format!("{{ID}}:{reg}")' not in src:
            raise SystemExit(f"zippy.rs does not register tft_zippy:{reg}")


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
