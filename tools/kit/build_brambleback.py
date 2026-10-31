"""Build tft_brambleback.data_champion (a tft pack hero: the Crimson Brambleback, jungle, Melee) from the parameters P.

    python tools/kit/build_brambleback.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Crimson Brambleback (绯红印记树怪) is Teamfight Tactics set 18's 4-cost Rift Monster / Berserker (DA_Brambleback18,
range 1, 1100 health, 120 AD, 0.55 attack speed, 65 armour and magic resistance, 0/40 mana): Crimson Fury / 猩红之怒 -
passive: when its target dies it leaps at the next, dealing physical damage; active: bonus AD for a few seconds,
ignoring part of the armour; Red Buff: attacks burn and heal it. The kit is our own design from that (the user's pick,
2026-10-31: jungle, plan A 「猩红之怒」):
  passive Red Buff (红霸符): every claw that lands heals it p_heal per mille of its maximum health and burns a target that
          is no tower: p_burn per mille of the target's maximum health every p_burn_every ticks for p_burn_t (at most
          p_burn_cap a tick; a new hit only renews it) - tft.dll's `tft_brambleback:red`. And TFT's passive: when it
          kills (a champion, or a jungle monster while it clears), every k_cd ticks it leaps at the nearest enemy
          champion within k_range (else, after a monster, the nearest monster) and lands for k_dmg + k_ad% AD.
          --plain: a Fire `AddCasted` of `FixedAttack {target_hp_ratio: p_pburn}` every p_pevery for p_burn_t and
          `Heal` p_pheal on itself (towers burn too; the leap left out).
  attack  Bramble Claw (荆爪横扫) on `Enemy` (towers too): 100% AD at atk_st, Red Buff on the hit.
  skill   Bramble Pounce (荆棘飞扑), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too): it springs at
          its target (`MoveToTarget` q_speed) and lands for q_dmg + q_ad% AD, the target q_slow% slower for q_slow_t.
  skill2  Crimson Roar (绯红咆哮), `Targeting` on `EnemyWithoutTower` (e_range): it rears up and roars at e_st: every
          enemy within e_r e_slow% slower and e_atk% weaker for e_t ticks, itself e_dr% less damage taken for e_t.
  ult     Crimson Fury (猩红之怒, TFT's), `Targeting` on `EnemyChampion` (r_range, only in fights): for r_t ticks
          r_atk% more attack, r_as% more attack speed and r_pen% of its targets' armour ignored, ablaze.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/brambleback.rs; the passive is
tft_brambleback:fury, params NATIVE_KEYS): the data reads neither who its claw hit (a tower or not), nor its maximum
health for a heal, nor who it killed. A build of P checks brambleback.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_brambleback"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 (the long arms); radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips are rigged (tools/art/rig_brambleback.py). Stats start from the pack's jungle bruisers
# (tft_krug hp 1200 +118 / atk 80, league_warwick 1120 / 92, league_udyr 1120 / 86): the 4-cost berserker, slow
# heavy claws, all physical.
P = {
    # stats (Melee, a jungle bruiser with physical skills)
    "hp": 1100, "hp_g": 108, "atk": 88, "atk_g": 16, "apw": 0, "apw_g": 0, "def": 34, "def_g": 8, "mr": 28, "mr_g": 6,
    "ms": 1040, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 32, "atk_cd": 66, "atk_st": 16,
    # passive Red Buff (tft.dll) and its --plain stand-in
    "p_burn": 6, "p_burn_t": 180, "p_burn_every": 30, "p_burn_cap": 40, "p_heal": 15,
    "p_pburn": 1, "p_pevery": 60, "p_pheal": 20,
    # the leap on to the next (tft.dll; TFT's passive)
    "k_range": 60000, "k_speed": 4000, "k_t": 24, "k_dmg": 60, "k_ad": 120, "k_cd": 60,
    # Bramble Pounce
    "q_cd": 420, "q_range": 55000, "q_dur": 30, "q_speed": 3500, "q_dmg": 60, "q_ad": 130, "q_slow": 30,
    "q_slow_t": 60,
    # Crimson Roar
    "e_cd": 600, "e_range": 30000, "e_dur": 36, "e_st": 14, "e_r": 34000, "e_slow": 30, "e_atk": 20, "e_t": 180,
    "e_dr": 25,
    # Crimson Fury (TFT: bonus AD, armour ignored)
    "r_cd": 3000, "r_range": 40000, "r_dur": 30, "r_st": 12, "r_t": 360, "r_atk": 45, "r_as": 35, "r_pen": 40,
}
# what tft.dll reads from passive.params (addons/tft/src/brambleback.rs)
NATIVE_KEYS = ("p_burn", "p_burn_t", "p_burn_every", "p_burn_cap", "p_heal", "k_range", "k_speed", "k_t", "k_dmg",
               "k_ad", "k_cd")
# names brambleback.rs uses that need no view: sounds (the burn's start, the leap on, the collapse)
NATIVE_ONLY = {"p", "q_next", "d"}


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
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


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


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def magic(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on it alone."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: Bramble Claw, Red Buff on the hit
    if is_native:   # tft.dll: the heal, and the burn on whatever is no tower
        red = native("red")
    else:           # --plain: a Fire burn of target_hp_ratio (towers too) and a flat heal
        burn = {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": p["p_pburn"]}
        red = combine({"type": "AddCasted", "casted_type": "Fire", "duration": p["p_burn_t"] + 1,
                       "period": p["p_pevery"], "effects": [burn]},
                      {"type": "Heal", "amount": p["p_pheal"], "attack_ratio": 0, "ap_ratio": 0, "heal_type": "Caster"})
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"), red)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Bramble Pounce
    landed = [attack(p["q_dmg"], p["q_ad"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
              view("q_hit"), tsfx("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"],
                                      "end_effects": landed}))

    # ------------------------------------------------------------------ skill2: Crimson Roar
    roared = [buff("e_slow", p["e_t"], move_speed_mult=-p["e_slow"], attack_mult=-p["e_atk"])]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), delayed(p["e_st"] - 1, sfx("e_guard"), sfx("e_slow"), cview("e_cast"),
                                              flag("e_guard", p["e_t"], damaged_reduce=p["e_dr"]),
                                              around(p["e_r"], "EnemyWithoutTower", roared))))

    # ------------------------------------------------------------------ ult: Crimson Fury
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r_vo"), delayed(p["r_st"] - 1, sfx("r"), sfx("r_fire"), cview("r_cast"),
                                              flag("r_fury", p["r_t"], attack_mult=p["r_atk"],
                                                   attack_speed_mult=p["r_as"], defence_penetration=p["r_pen"]))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the roar's ring and the fury's flare ride it; the guard and the fury's fire ride it as buffs
    views_e = [E("a_hit"), E("q_hit", FX, 3), E("e_cast", BIG, 3), E("r_cast", BIG, 3)]
    views_b = [B_("q_slow"), B_("e_slow"), B_("e_guard", BIG), B_("r_fury", BIG)]
    if is_native:   # the burn tft.dll puts on
        views_b += [B_("p_burn", FX, 4)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Dot", "Heal"],
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
    if is_native:   # tft.dll (addons/tft/src/brambleback.rs): Red Buff and the leap on to the next
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:fury", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/brambleback.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback) and every name it plays or puts on (`bb("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "brambleback.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"brambleback.rs Params::default() differs from P (brambleback.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'bb\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"brambleback.rs plays or puts on names the kit does not have: {missing}")


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
