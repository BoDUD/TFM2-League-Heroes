"""Build tft_elderdragon.data_champion (a tft pack hero: the Elder Dragon, top, Melee) from the parameters P.

    python tools/kit/build_elderdragon.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Elder Dragon (远古巨龙) is Teamfight Tactics set 18's 5-cost Apex Predator / Rift Monster (DA_18_ElderDragon, range 2,
1800 health, 125 AD, 0.50 attack speed, 75 armour and magic resistance, 20/60 mana): Heat Without Equal / 绝伦火热 -
passive: attacks splash the enemies next to the target; active: invulnerable, it flies up and on its return stuns every
enemy, gains omnivamp and Ignites them (% of their maximum health as physical damage a second), then the ability turns
into Flame Breath and is cast at once (fire along the line through the target with the most enemies, less for each it
passes, Igniting them); the Elder buff: damage executes enemies under a share of their health. The kit is our own
design from that (the user's pick, 2026-11-01: top, plan A 「绝伦火热」):
  passive Elder buff (远古巨龙霸符): an enemy champion it damages that is left at or under p_exec% of its maximum health
          dies - tft.dll's `tft_elderdragon:elder`. --plain: left out.
  attack  Dragonfire Bite (龙焰撕咬) on `Enemy` (towers too): 100% AD at atk_st; the others within a_r of its target (no
          towers) take a_splash% AD - tft.dll's `tft_elderdragon:bite`. --plain: a RangeEffect a_r round the point
          atk_range ahead (the target too).
  skill   Flame Breath (烈焰吐息), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too): at q_st it breathes
          fire along the line through its target with the most enemy champions (tft.dll's `tft_elderdragon:breath`): each
          one burned takes q_dmg + q_ad% AD physical, q_decay% less for each burned before it (never under q_min%), and is
          Ignited: ig_hp per mille of its maximum health physical every ig_every ticks for ig_t. --plain: a
          LineRangeProjectile toward the target, full damage, Ignite a Fire AddCasted of target_hp_ratio.
  skill2  Wing Storm (龙翼风暴), `Targeting` on `EnemyWithoutTower` (e_range): it rears up and beats its wings at e_st:
          every enemy within e_r takes e_dmg + e_ad% AD, is knocked back (e_kb x e_kb_t) and e_slow% slower for e_t; it
          takes e_dr% less damage for e_t.
  ult     Heat Without Equal (绝伦火热, TFT's), `Targeting` on `EnemyChampion` (r_range, only in fights): invulnerable
          (damaged_reduce 100, cc_immune) it flies up for r_air ticks; landing, every enemy within r_r takes r_dmg + r_ad%
          AD, is stunned r_stun and Ignited; it gains r_vamp% omnivamp for r_vamp_t, and breathes a Flame Breath at once.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/elderdragon.rs; the passive is
tft_elderdragon:elder, params NATIVE_KEYS): the data reads no target's health for the execute, tells no main target from
the rest for the splash, picks no line by who stands in it and counts nobody it passes. A build of P checks
elderdragon.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_elderdragon"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: its bite reaches 30000 (TFT's range 2; the long neck); radii count the unit's collision radius (~15000) on top.
# Timings are placeholders until the strips are rigged (tools/art/rig_elderdragon.py). Stats start from the pack's top
# bruisers (tft_krug hp 1200 +118 / atk 80, league_volibear 1180 / 88): the 5-cost dragon, slow heavy bites, all
# physical, thick hide.
P = {
    # stats (Melee, a top bruiser with physical skills)
    "hp": 1200, "hp_g": 118, "atk": 88, "atk_g": 15, "apw": 0, "apw_g": 0, "def": 38, "def_g": 8, "mr": 32, "mr_g": 7,
    "ms": 1000, "ms_g": 10,
    "atk_range": 30000, "atk_dur": 36, "atk_cd": 72, "atk_st": 18,
    # passive Elder buff (tft.dll)
    "p_exec": 15,
    # the bite's splash (tft.dll; --plain: round the point ahead)
    "a_r": 22000, "a_splash": 35,
    # Flame Breath (tft.dll's line; --plain: a LineRangeProjectile)
    "q_cd": 480, "q_range": 45000, "q_dur": 36, "q_st": 16, "q_len": 75000, "q_w": 13000, "q_speed": 6000,
    "q_dmg": 70, "q_ad": 130, "q_decay": 20, "q_min": 40,
    # Ignite (tft.dll; --plain: a Fire AddCasted)
    "ig_t": 180, "ig_every": 60, "ig_hp": 25, "ig_cap": 100,
    # Wing Storm
    "e_cd": 600, "e_range": 25000, "e_dur": 36, "e_st": 16, "e_r": 35000, "e_dmg": 30, "e_ad": 60, "e_kb": 2500,
    "e_kb_t": 12, "e_slow": 35, "e_t": 120, "e_dr": 25,
    # Heat Without Equal (TFT: invulnerable flight, stun all, omnivamp, Ignite, Flame Breath at once)
    "r_cd": 3600, "r_range": 40000, "r_air": 90, "r_r": 55000, "r_dmg": 80, "r_ad": 80, "r_stun": 75, "r_vamp": 30,
    "r_vamp_t": 300,
}
# what tft.dll reads from passive.params (addons/tft/src/elderdragon.rs)
NATIVE_KEYS = ("p_exec", "a_r", "a_splash", "q_len", "q_w", "q_speed", "q_dmg", "q_ad", "q_decay", "q_min", "ig_t",
               "ig_every", "ig_hp", "ig_cap")
# names elderdragon.rs uses that need no view: sounds (the execute, the Ignite catching, the fall)
NATIVE_ONLY = {"p", "burn", "d"}


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


def attack(dmg, ratio, hp=0, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def ignite_plain(p):
    """--plain's Ignite: a Fire AddCasted of the target's maximum health (towers too, no cap)."""
    tick = attack(0, 0, target_hp=max(1, p["ig_hp"] // 10))
    return {"type": "AddCasted", "casted_type": "Fire", "duration": p["ig_t"] + 1, "period": p["ig_every"],
            "effects": [tick]}


def breath(p, is_native):
    """The Flame Breath (Q, and again after the ult's landing)."""
    if is_native:   # tft.dll: the line through the target with the most enemy champions, the decay, the Ignite
        return native("breath")
    hit = [attack(p["q_dmg"], p["q_ad"]), ignite_plain(p), view("q_hit_v")]
    return {"type": "LineRangeProjectile", "name": n("q_line"), "width": p["q_w"], "length": p["q_len"], "delay": 2,
            "apply": 1, "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in hit]}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: Dragonfire Bite, the splash
    if is_native:   # tft.dll: the others round its target
        splash = native("bite")
    else:           # --plain: round the point a bite ahead (the target too)
        splash = {"type": "RangeEffect", "shape": circle(p["a_r"]), "target": "EnemyWithoutTower",
                  "apply_type": {"Forward": {"offset": p["atk_range"]}},
                  "effects": [attack(0, p["a_splash"])]}
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"), splash)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Flame Breath
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q_vo"), delayed(p["q_st"] - 1, sfx("q"), breath(p, is_native))))

    # ------------------------------------------------------------------ skill2: Wing Storm
    struck = [attack(p["e_dmg"], p["e_ad"]), {"type": "Knockback", "speed": p["e_kb"], "tick": p["e_kb_t"]},
              buff("e_slow", p["e_t"], move_speed_mult=-p["e_slow"]), tsfx("e_hit")]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e_vo"), delayed(p["e_st"] - 1, sfx("e"), cview("e_cast"),
                                                 flag("e_guard", p["e_t"], damaged_reduce=p["e_dr"]),
                                                 around(p["e_r"], "EnemyWithoutTower", struck))))

    # ------------------------------------------------------------------ ult: Heat Without Equal
    if is_native:   # tft.dll's Ignite on each one it lands on
        lit = native("ignite")
    else:
        lit = ignite_plain(p)
    landed = [attack(p["r_dmg"], p["r_ad"]), {"type": "Stun", "duration": p["r_stun"]},
              buff("r_stun", p["r_stun"]), lit]
    ult = action("ult", p["r_air"] + p["q_st"] + 4, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r_vo"), sfx("r"),
                         flag("r_fly", p["r_air"], damaged_reduce=100, cc_immune=True),
                         delayed(p["r_air"] - 1, sfx("r_land"), sfx("r_slam"), view("r_slam"),
                                 around(p["r_r"], "EnemyWithoutTower", landed),
                                 flag("r_vamp", p["r_vamp_t"], vamp=p["r_vamp"])),
                         delayed(p["r_air"] + p["q_st"] - 1, sfx("q"), breath(p, is_native))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                             "tag": tag or name, "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the bite's mark rides its target; the wing storm rides it; the slam lies on the ground where it landed
    views_e = [E("a_hit"), E("e_cast", BIG, 3), E("r_slam", BIG, -1, False)]
    views_b = [B_("e_slow"), B_("e_guard", BIG), B_("r_stun", FX, 4), B_("r_vamp", BIG)]
    views_p = [B_("q_fire", FX, 3)]   # tft.dll's breath (a projectile it spawns), or --plain's line
    if is_native:   # the buffs tft.dll gives
        views_b += [B_("a_splash"), B_("q_hit"), B_("ig"), B_("p_exec", FX, 4)]
    else:
        views_e += [E("q_hit_v", FX, 3, True, "q_hit")]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Dot", "CC", "Tank"],
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
    if is_native:   # tft.dll (addons/tft/src/elderdragon.rs): the execute, the splash, the breath, the Ignite
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:elder", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/elderdragon.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults
    are its fallback) and every name it plays or puts on (`ed("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "elderdragon.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"elderdragon.rs Params::default() differs from P (elderdragon.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'\bed\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"elderdragon.rs plays or puts on names the kit does not have: {missing}")


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
