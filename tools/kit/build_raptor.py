"""Build tft_raptor.data_champion (a tft pack hero: the Crimson Raptor, bottom lane, Range) from the parameters P.

    python tools/kit/build_raptor.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Crimson Raptor (深红锋喙鸟, the user's 锋啄鸟; en Mama Beak) is Teamfight Tactics set 18's 3-cost Rift Monster /
Summoner / Rapidfire (DA_CrimsonRaptor18, range 4, 650 health, 60 AD, 0.75 attack speed, 35 armour and magic
resistance, 20/60 mana): Flock Family / 鸟群之家 - four untargetable Tiny Beaks for a few seconds, each of her attacks
they attack the same enemy for physical damage; Orange Buff: her physical damage lowers the enemy's armour. The kit is
our own design from that (the user's pick, 2026-10-31: bottom lane, plan A 「鸟群之家」):
  passive Orange Buff (橙霸符): every physical hit of hers (attack, Q's feathers, the Tiny Beaks' pecks) takes p_arm
          armour off the target for p_t ticks, up to p_max stacks (`tft_raptor:shred`, tft.dll: the engine's stacked
          buff with a cap and a refresh; --plain: same-name data buffs, uncapped).
  attack  Feather Shot (锋羽射击) on `Enemy` (towers too): a homing red feather, 100% AD.
  skill   Feather Fan (羽刃扇射), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): she flares her crest
          and wings and throws q_n blade feathers in a fan q_spread degrees apart toward the target
          (`tft_raptor:fan`, tft.dll: each its own straight flight q_len long, stopping at the first enemy it meets:
          q_dmg + q_ratio% AD physical, so close up one enemy takes most of them); --plain: a cone as wide as the fan,
          q_plain feathers' damage on each enemy in it.
  skill2  Startled Hop (惊飞跃退), `Targeting` on `EnemyChampion` (e_range, a champion close): a screech and a hop
          straight away from them (MoveBack e_back x e_back_t), then e_as% attack speed for e_t ticks (Rapidfire).
  ult     Flock Family (鸟群之家, TFT's), `Targeting` on `EnemyChampion` (r_range, only in fights): her call brings
          four Tiny Beaks round her (the flag r_flock, drawn round her) for r_t ticks: each of her attacks meanwhile
          sends r_n pecks after her feather, r_gap ticks apart, each r_dmg + r_ratio% AD physical (and Orange Buff).
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/raptor.rs; the passive is
tft_raptor:flock, params NATIVE_KEYS): no projectile takes an angle, and a data buff has no stack cap. A build of P
checks raptor.rs's Params::default() against it.
"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_raptor"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 60000 like the pack's bottoms (tft_daeja 60000, the base archer 60000); radii count the unit's
# collision radius (~15000) on top. Timings are placeholders until the strips are rigged (tools/art/rig_raptor.py).
# Stats from the Range base (attack 100 +20, hp 900 +90, def 20 +7, mr 15 +3, move 900 +9): all physical, no magic
# power. Numbers = the 10-min classic-SDK simulations (C:/t/rp_sim with C:/t/al_sim/kd.py: bottom lane 3 against the
# base archer, gunner, boomerang and poison-dart hunters, three lineups, both sides; 2026-10-31), all --plain (the fan
# a cone, Orange Buff uncapped): the draft (atk 92, Q 30 + 45% x2, pecks 12 + 22%, R 6 s, E +60% AS, shred 5) +0.08 /
# -0.02 on seeds 1-8 / 9-16 against tft_daeja --plain +1.39 / +1.17; atk 98, Q 35 + 55% +0.45; + pecks 18 + 30%, R 7 s
# +0.37; + E +80% AS, shred 7 +2.31 / +1.01; between the last two (E +70%, shred 6) +0.69 / +1.47 = P: the 3-cost a
# little under the 4-cost Daeja.
P = {
    # stats (Range, an AD carry)
    "hp": 860, "hp_g": 88, "atk": 98, "atk_g": 18, "apw": 0, "apw_g": 0, "def": 22, "def_g": 7, "mr": 18, "mr_g": 3,
    "ms": 920, "ms_g": 9,
    "atk_range": 60000, "atk_dur": 24, "atk_cd": 70, "a_rel": 8, "a_speed": 5500, "a_y": 2000,
    # passive Orange Buff (TFT: physical damage lowers the enemy's armour)
    "p_arm": 6, "p_max": 5, "p_t": 180,
    # Feather Fan
    "q_cd": 360, "q_range": 60000, "q_dur": 30, "q_rel": 12, "q_n": 5, "q_spread": 12, "q_len": 70000, "q_w": 4000,
    "q_speed": 6500, "q_dmg": 35, "q_ratio": 55, "q_plain": 2,
    # Startled Hop
    "e_cd": 540, "e_range": 35000, "e_dur": 18, "e_rel": 4, "e_back": 5000, "e_back_t": 6, "e_as": 70, "e_t": 180,
    # Flock Family (TFT: 4 untargetable Tiny Beaks, each attack they attack the same enemy, physical)
    "r_cd": 2700, "r_range": 65000, "r_dur": 30, "r_rel": 12, "r_t": 420, "r_n": 4, "r_gap": 3, "r_speed": 6000,
    "r_dmg": 18, "r_ratio": 30,
}
# what tft.dll reads from passive.params (addons/tft/src/raptor.rs)
NATIVE_KEYS = ("p_arm", "p_max", "p_t", "q_n", "q_spread", "q_len", "q_w", "q_speed", "q_dmg", "q_ratio")
# names raptor.rs uses that need no view: sounds (the death cry, Orange Buff filling up)
NATIVE_ONLY = {"d", "p"}


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


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


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


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def shred(p, is_native):
    """Orange Buff on the one struck: tft.dll's capped stack, or (--plain) a same-name data buff (they add up)."""
    return native("shred") if is_native else buff("p_shred", p["p_t"], defence=-p["p_arm"])


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: the feather + the Tiny Beaks' pecks
    hit = [attack(0, 100), shred(p, is_native), view("a_hit"), tsfx("a_hit")]
    peck = [attack(p["r_dmg"], p["r_ratio"]), shred(p, is_native), view("r_peck_hit"), tsfx("r_peck_hit")]
    pecks = [delayed(k * p["r_gap"], sfx("r_peck"), homing("r_peck", "Enemy", peck, p["r_speed"], p["a_y"]))
             for k in range(1, p["r_n"] + 1)]
    flock = {"type": "SwitchByBuff", "buff_name": n("r_flock"), "effect_buff": combine(*pecks),
             "effect_none": combine()}
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_bolt", "Enemy", hit, p["a_speed"], p["a_y"]), flock),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Feather Fan
    if is_native:   # tft.dll: q_n feathers in a fan, each stopping at the first enemy
        fan = native("fan")
    else:           # --plain: a cone as wide as the fan (half its spread plus a feather's own angle each side)
        half = math.radians((p["q_n"] - 1) / 2 * p["q_spread"] + p["q_spread"] / 2)
        struck = [attack(p["q_dmg"] * p["q_plain"], p["q_ratio"] * p["q_plain"]), shred(p, False), view("q_hit")]
        fan = {"type": "RangeEffect", "shape": {"DirDot": {"radius": p["q_len"], "range": round(1000 * math.cos(half))}},
               "target": "EnemyWithoutTower", "apply_type": {"Forward": {"offset": 1000}}, "effects": struck}
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q_vo"), delayed(p["q_rel"] - 1, sfx("q"), fan)))

    # ------------------------------------------------------------------ skill2: Startled Hop
    hop = combine(sfx("e"), cview("e_jump"), {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]},
                  delayed(p["e_back_t"], sfx("e_rush"), flag("e_rush", p["e_t"], attack_speed_mult=p["e_as"])))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(sfx("e_vo"), delayed(p["e_rel"] - 1, hop)))

    # ------------------------------------------------------------------ ult: Flock Family
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), delayed(p["r_rel"] - 1, sfx("r_chick"), flag("r_flock", p["r_t"]),
                                           delayed(p["r_t"], sfx("r_end")))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # a_bolt / q_feather / r_peck fly laid along their flight, top-bottom symmetric (turned with it); the hits are
    # ViewEffects on the struck (never mirrored: left-right symmetric); e_jump the dust she hops from (on the ground
    # where she stood); p_shred the orange crack on a shredded target, e_rush the red rush round her, r_flock the
    # four Tiny Beaks round her, drawn facing us (a buff picture is never mirrored)
    views_p = [B_("a_bolt"), B_("q_feather"), B_("r_peck")]
    views_e = [E("a_hit"), E("q_hit"), E("r_peck_hit"), E("e_jump", FX, -1, False)]
    views_b = [B_("p_shred", FX, 3), B_("e_rush", FX, 3), B_("r_flock", BIG, 3)]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range"],
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
    if is_native:   # tft.dll (addons/tft/src/raptor.rs): the fan and the capped Orange Buff
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:flock", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


# Sylas's copy: the flock comes for SY_WAVES waves SY_GAP ticks apart (the flag r_flock on him as long), each wave the
# r_n pecks at his target
SY_WAVES, SY_GAP = 3, 24


def sylas_ult(p=None):
    """Flock Family as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): the kit's ult is
    a flag only its own attack reads, so in his hands it would do nothing; his flock dives at his target instead - the
    call, the four Tiny Beaks round him (r_flock) for SY_WAVES waves of the r_n pecks (r_dmg + r_ratio% AD physical,
    Orange Buff's data shred), then they fly off. The views are the kit's own (tft_raptor_*); make_override copies them
    and their sheets."""
    p = dict(P) if p is None else p
    peck = [attack(p["r_dmg"], p["r_ratio"]), shred(p, False), view("r_peck_hit"), tsfx("r_peck_hit")]
    waves = [delayed(w * SY_GAP + k * p["r_gap"], sfx("r_peck"), homing("r_peck", "Enemy", peck, p["r_speed"], p["a_y"]))
             for w in range(SY_WAVES) for k in range(p["r_n"])]
    stay = SY_WAVES * SY_GAP
    return combine(sfx("r"), delayed(p["r_rel"] - 1, sfx("r_chick"), flag("r_flock", stay), *waves,
                                     delayed(stay, sfx("r_end"))))


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
    """addons/tft/src/raptor.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`rp("...")`) is the kit's or NATIVE_ONLY, and every Native the kit
    calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "raptor.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"raptor.rs Params::default() differs from P (raptor.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'rp\("(\w+)"\)', src))
    have = names(build(p, False)) | names(kit) | {n(x) for x in NATIVE_ONLY}
    missing = sorted(x for x in read if n(x) not in have)
    if not read or missing:
        raise SystemExit(f"raptor.rs plays names the kit does not have: {missing}")
    called = set(re.findall(r'"(?:effect_ref|passive_ref)": "tft_raptor:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native code raptor.rs does not register: {sorted(called - registered)}")


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
