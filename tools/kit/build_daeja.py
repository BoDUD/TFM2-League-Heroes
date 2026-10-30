"""Build tft_daeja.data_champion (the tft pack's nineteenth hero: Daeja, bottom lane, Range) from the parameters P.

    python tools/kit/build_daeja.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Daeja (迭嘉) is the blue Mirage dragon of Teamfight Tactics set 7 (Dragonlands): the 4-cost unit TFT7_DragonBlue
(Mirage / Dragon, an AP carry, range 4, 800 health, 0.60 attack speed, 35 armour and magic resistance, 0/100 mana), a
crystal dragon-man standing upright, two wing fans folded up behind his back. TFT gives him one ability (Windblast /
罡风轰击: passive - his attacks launch three barrages, each bonus magic damage and -5 magic resistance; active - magic
damage in the line with the most enemies). The rest is our own design (the user's pick, 2026-10-30: bottom lane,
plan A 「罡风弹幕」):
  attack  Wind Bolt (风弹) on `Enemy` (towers too): a homing bolt from his fist, 100% AD.
  passive Barrage (三连弹幕, TFT's passive half): every attack sends p_n small wind bolts after the first, p_gap ticks
          apart: p_dmg + p_ap% AP magic each, and magic resistance -p_mr for p_mr_t ticks (same-name buffs add up:
          the shred stacks, each with its own timer).
  skill   Windblast (罡风轰击, TFT's active half), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): his
          wings sweep forward and a wave of wind (q_w wide, q_len long) runs through every enemy in its line: q_dmg +
          q_ratio% AP magic. tft.dll aims it down the line with the most enemies (below); --plain: at the target.
  skill2  Wingbeat Retreat (振翼退风), `Targeting` on `EnemyChampion` (e_range, a champion close): one beat of the wings
          throws a gust at them (a line e_len long: e_dmg + e_ratio% AP and e_slow% slow for e_slow_t ticks) and carries
          him back (MoveBack e_back x e_back_t, straight away from them).
  ult     Sky Gale (苍穹罡风), `Targeting` on `EnemyChampion` (r_range): he spreads his wings and rises (r_dr% less damage
          taken, no crowd control), then r_n big waves r_gap ticks apart (r_w wide, r_len long, r_dmg + r_ratio% AP
          each), each down the line with the most enemies (tft.dll; --plain: at the target), then lands.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/daeja.rs): no data effect counts the
enemies along a line, so `tft_daeja:windblast` / `tft_daeja:skygale` (Natives at the release) pick the direction and
spawn the penetrating wave, whose hits run `tft_daeja:wave_hit` / `tft_daeja:sky_hit`. The passive
`tft_daeja:mirage` holds the parameters (NATIVE_KEYS) and plays his death cry. A build of P checks daeja.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_daeja"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 60000 like the pack's long-range bottoms (tft_maddie 68000, the base archer 60000); radii count
# the unit's collision radius (~15000) on top. Timings are placeholders until the strips exist (tools/art/rig_daeja.py).
# Stats from the Range base (attack 100 +20, hp 900 +90, def 20 +7, mr 15 +3, move 900 +9), a little attack traded
# for magic power: his damage is half attacks, half the barrages' and waves' magic. Numbers = the 10-min classic-SDK
# simulations (C:/t/dj_sim with C:/t/al_sim/kd.py: bottom lane 3 against the base archer, gunner, boomerang and
# poison-dart hunters, three lineups, both sides; 2026-10-30), all --plain (the waves at the target): the draft (Q 120 +
# 75%, E within 30000) +1.58 on seeds 1-8 / +0.52 on 9-16, E cast 3 times a game; E within 40000 +1.86 / +1.09 (4 a
# game); + Q 110 + 70% +1.39 / +1.17 = P (tft_nomsy's final +1.12 / +1.16 in mid).
P = {
    "hp": 880, "hp_g": 90, "atk": 90, "atk_g": 17, "apw": 30, "apw_g": 14, "def": 20, "def_g": 7, "mr": 18, "mr_g": 3,
    "ms": 900, "ms_g": 9,
    "atk_range": 60000, "atk_dur": 24, "atk_cd": 72, "a_rel": 8, "a_speed": 5000, "a_y": 2000,
    # passive Barrage (TFT: 3 barrages of 35/50 (AP) magic, -5 magic resistance each)
    "p_n": 3, "p_gap": 4, "p_speed": 6000, "p_dmg": 10, "p_ap": 15, "p_mr": 4, "p_mr_t": 180,
    # Windblast (TFT: 265/400 (AP) magic in the line with the most enemies)
    "q_cd": 360, "q_range": 65000, "q_dur": 30, "q_rel": 14, "q_len": 90000, "q_w": 9000, "q_speed": 6000,
    "q_dmg": 110, "q_ratio": 70,
    # Wingbeat Retreat
    "e_cd": 600, "e_range": 40000, "e_dur": 24, "e_rel": 6, "e_len": 45000, "e_w": 14000, "e_dmg": 40, "e_ratio": 30,
    "e_slow": 40, "e_slow_t": 90, "e_back": 5000, "e_back_t": 6,
    # Sky Gale
    "r_cd": 2700, "r_range": 75000, "r_rise": 24, "r_n": 3, "r_gap": 24, "r_land": 18, "r_dr": 30, "r_len": 110000,
    "r_w": 12000, "r_speed": 7000, "r_dmg": 150, "r_ratio": 70,
}
# what tft.dll reads from passive.params (addons/tft/src/daeja.rs)
NATIVE_KEYS = ("q_len", "q_w", "q_speed", "q_dmg", "q_ratio", "r_len", "r_w", "r_speed", "r_dmg", "r_ratio")


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


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def wave(name, speed, length, width, effects):
    """A penetrating skillshot at the action's target (the --plain stand-in for tft.dll's waves): every enemy it runs
    through takes `effects` once."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": "EnemyWithoutTower",
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": length,
            "shape": circle(width), "y_offset": 0}


def line(name, length, width, target, effects, delay=1):
    """A line from him through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: the wind bolt + the barrage
    hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    shred = [ap(p["p_dmg"], p["p_ap"]), buff("p_shred", p["p_mr_t"], magic_resistance=-p["p_mr"]), view("p_hit"),
             tsfx("p_hit")]
    barrage = [delayed(k * p["p_gap"], sfx("p"), homing("p_bolt", "Enemy", shred, p["p_speed"], p["a_y"]))
               for k in range(1, p["p_n"] + 1)]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_bolt", "Enemy", hit, p["a_speed"], p["a_y"]),
                              *barrage),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Windblast
    blast = [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")]
    q_go = native("windblast") if is_native else wave("q_wave", p["q_speed"], p["q_len"], p["q_w"], blast)
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_rel"] - 1, sfx("q_launch"), q_go)))

    # ------------------------------------------------------------------ skill2: Wingbeat Retreat
    gust = [ap(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), tsfx("e_slow")]
    beat = combine(sfx("e_wind"), line("e_gust", p["e_len"], p["e_w"], "EnemyWithoutTower", gust, delay=12),
                   {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]})
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(sfx("e"), delayed(p["e_rel"] - 1, beat)))

    # ------------------------------------------------------------------ ult: Sky Gale
    big = [ap(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]
    r_go = native("skygale") if is_native else wave("r_wave", p["r_speed"], p["r_len"], p["r_w"], big)
    air = p["r_rise"] + p["r_n"] * p["r_gap"]
    blasts = [delayed(p["r_rise"] - 1 + k * p["r_gap"], sfx("r_blast"), r_go) for k in range(p["r_n"])]
    ult = action("ult", air + p["r_land"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), flag("r_fly", air, damaged_reduce=p["r_dr"], cc_immune=True),
                         delayed(p["r_rise"] - 1, sfx("r_roar")), *blasts, delayed(air, sfx("r_land"))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # a_bolt / p_bolt are round wind balls, q_wave / r_wave / e_gust level crescents of wind along their flight, top-
    # bottom symmetric (turned with it); the hits are ViewEffects on the struck; p_shred / e_slow are buff pictures on
    # the target, r_fly the wind under him while he flies (z -1)
    views_p = [B_("a_bolt"), B_("p_bolt"), B_("q_wave", BIG), B_("e_gust", BIG), B_("r_wave", BIG)]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit", FX, 3, False), E("r_hit", BIG, 3, False)]
    views_b = [B_("p_shred", FX, 3), B_("e_slow", FX, 3), B_("r_fly", FX, -1)]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "AP", "Magic", "Range"],
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
    if is_native:   # tft.dll (addons/tft/src/daeja.rs): the waves down the line with the most enemies
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:mirage", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Sky Gale as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll (the user, 2026-10-27:
    「塞拉斯的大招什么一定要能偷到特效版本的」). The kit's --plain ult: the flight, three penetrating waves at the champion he
    casts at, their hits. The views are the kit's own (tft_daeja_*); make_override copies them and their sheets."""
    p = dict(P) if p is None else p
    return build(p, False)["ult"]["effect"]


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


# names only tft.dll plays (the waves' flights, his death cry: the native kit's data never sends or plays them; the
# views and the sound files still exist)
NATIVE_ONLY = {"q_wave", "r_wave", "d"}


def check_dll(p, kit):
    """addons/tft/src/daeja.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays (`dj("...")`) is the kit's or NATIVE_ONLY, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "daeja.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"daeja.rs Params::default() differs from P (daeja.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'dj\("(\w+)"\)', src))
    have = names(build(p, False)) | {n(x) for x in NATIVE_ONLY}
    missing = sorted(x for x in read if n(x) not in have)
    if not read or missing:
        raise SystemExit(f"daeja.rs plays names the kit does not have: {missing}")
    called = set(re.findall(r'"(?:effect_ref|passive_ref)": "tft_daeja:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native code daeja.rs does not register: {sorted(called - registered)}")


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
