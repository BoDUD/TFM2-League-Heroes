"""Build tft_baronnashor.data_champion (a tft pack hero: Baron Nashor, jungle, Melee) from the parameters P.

    python tools/kit/build_baronnashor.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Baron Nashor (纳什男爵) is Teamfight Tactics set 16's 5-cost Void unit (TFT16_BaronNashor, range 2, 3000 health, 120
AD, 0.50 attack speed, 85 armour and magic resistance, 0/50 mana, 25% crit; its own trait takes two team slots and opens
a void rift after 8 s): Void's Wrath / 虚空之怒 - passive: immune to crowd control; attacks damage a line through the
target; with no enemy in range it burrows to the next target and knocks up the enemies next to it on arrival; in the
rift a tentacle bursts up under a random enemy every 3 s (a 1.5 s knock-up). Active: a slam raising spikes in a 2-hex
circle (physical), then 10 acid balls over 3 s. League's Baron spits corrosive acid (armour and magic resistance down)
and knocks up with a tentacle. The kit is our own design from those (the user's pick, 2026-11-03: 「方案A 打野」):
  passive Void Rift (虚空裂隙): in a fight (an enemy champion within p_range) every p_every ticks, the first p_first
          ticks after it meets one, a tentacle bursts up under a random enemy champion within p_range: p_dmg + p_ad% AD
          physical and knocked up p_up ticks (tft.dll `tft_baronnashor:rift`; --plain: one tentacle in every Q cast).
  attack  Corrosive Bite (腐蚀撕咬) on `Enemy` (towers too): it rears and strikes at atk_st: 100% AD on the target,
          and everything else (no towers) in a line a_len long and a_w wide from it through the target takes a_line%
          AD (TFT's line; the target takes it too, the numbers count that).
  skill   Corrosive Breath (腐蚀吐息, League's acid), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too):
          at q_st a cone of acid in front of it (q_r long, acos(q_cone / 1000) each side): q_dmg + q_ad% AD and
          q_shred% less armour and magic resistance for q_t ticks (`q_acid`).
  skill2  Burrow Strike (钻地突袭, TFT's dash), `Targeting` on `EnemyWithoutTower` (e_range): it dives (crowd-control
          immune until it is up again, the `dig` frames), travels under the ground to the target (MoveToTarget e_speed)
          and bursts up (`rise`): every enemy (no towers) within e_r takes e_dmg + e_ad% AD and is knocked up e_up ticks.
  ult     Void's Wrath (虚空之怒, TFT's), `Targeting` on `EnemyChampion` (r_range): crowd-control immune for the whole
          cast (TFT's passive); at r_st it slams: spikes in a circle of r_r round it, r_dmg + r_ad% AD; then r_n acid
          balls r_every ticks apart on random enemies within r_mr: r_mdmg + r_mad% AD and the acid of Q (`q_acid`).
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/baronnashor.rs; the passive is
tft_baronnashor:rift, params NATIVE_KEYS): no moment of its own every few seconds. A build of P checks baronnashor.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_baronnashor"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: TFT's range 2 = a long neck's reach, 32000 (melee 23000-27000, T-Hex's short gun 38000); radii count the unit's
# collision radius (~15000) on top. Timings are placeholders until the strips are rigged (tools/art/rig_baronnashor.py):
# the bite lands at 400 ms (TFT's attack clip rears ~416 ms, strikes ~624 of 1670). Stats start from the pack's jungle
# bruisers (tft_brambleback hp 1100 +108 / atk 92 every 66 / def 34, tft_krug 1200 +118): a 5-cost serpent, slow heavy
# bites, all physical, armoured.
# Numbers = the 10-min classic-SDK simulations (python -I C:/t/al_sim/kd.py <kit --plain> --lane 1: jungle against the
# base ninja, demon, hunter, werewolf and vampire, three lineups, both sides), all --plain (a tentacle in every Q cast): the draft (atk 90, Q 90%, E 100%, R 150%, line 30%) +4.06 on seeds 1-8
# against tft_brambleback --plain +2.15 / +1.34 and tft_krug +2.06 / +1.89 (their sessions' numbers, the same games) - far
# too strong; v2 = P (atk 82, Q 70%, E 80%, R 120%, line 20%) +2.11; v3 (atk 78, hp 1100, Q 60%, E 70%, R 110%) +0.95;
# v4 (atk 80, hp 1150, def 34, mr 28, Q 60%, shred 15%) +1.86.
P = {
    # stats (Melee, a jungle bruiser with physical skills)
    "hp": 1200, "hp_g": 115, "atk": 82, "atk_g": 15, "apw": 0, "apw_g": 0, "def": 40, "def_g": 8, "mr": 34, "mr_g": 6,
    "ms": 1000, "ms_g": 10,
    "atk_range": 32000, "atk_dur": 40, "atk_cd": 80, "atk_st": 24,
    # Corrosive Bite (TFT: attacks damage a line through the target)
    "a_len": 70000, "a_w": 12000, "a_line": 20,
    # Void Rift (TFT: in the rift a tentacle under a random enemy every 3 s, knocked up 1.5 s)
    "p_range": 60000, "p_every": 360, "p_first": 120, "p_dmg": 40, "p_ad": 60, "p_up": 45,
    # Corrosive Breath (League's acid: armour and magic resistance down)
    "q_cd": 420, "q_range": 40000, "q_dur": 36, "q_st": 18, "q_r": 46000, "q_cone": 600, "q_dmg": 40, "q_ad": 70,
    "q_shred": 20, "q_t": 240,
    # Burrow Strike (TFT: no enemy in range -> burrow to the next, knock up the enemies next to it)
    "e_cd": 720, "e_range": 75000, "e_dur": 40, "e_st": 12, "e_speed": 3500, "e_r": 30000, "e_dmg": 50, "e_ad": 80,
    "e_up": 45, "e_rise": 30,
    # Void's Wrath (TFT: spikes in a 2-hex circle, then 10 acid balls over 3 s)
    "r_cd": 3000, "r_range": 40000, "r_st": 30, "r_r": 45000, "r_dmg": 100, "r_ad": 120, "r_n": 10, "r_every": 18,
    "r_mr": 60000, "r_mdmg": 15, "r_mad": 30,
}
# what tft.dll reads from passive.params (addons/tft/src/baronnashor.rs)
NATIVE_KEYS = ("p_range", "p_every", "p_first", "p_dmg", "p_ad", "p_up")
# names baronnashor.rs uses that need no view: the tentacle's sound, the death's sound
NATIVE_ONLY = {"p", "d"}


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
    return effects[0] if tick <= 0 and len(effects) == 1 else {"type": "Delayed", "tick": tick, "effects": list(effects)}


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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def cone(radius, dot, target, effects):
    """A cone in front of it toward the action's target (league_darius E's: Forward 1000 + DirDot)."""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": dot}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def line(name, length, width, target, effects):
    """A one-tick strip from it through the action's target (league_chogath's)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": 2,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def rain(rng, target, effects):
    """One random unit of `target` within rng."""
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def acid(p):
    """Corrosive acid: q_shred% less armour and magic resistance for q_t ticks."""
    return buff("q_acid", p["q_t"], defence_mult=-p["q_shred"], magic_resistance_mult=-p["q_shred"])


def tentacle(p):
    """--plain's Void Rift: one tentacle under a random enemy champion within p_range (in every Q cast)."""
    return rain(p["p_range"], "EnemyChampion", [sfx("p"), view("p_tent"), attack(p["p_dmg"], p["p_ad"]),
                                                 {"type": "Airborne", "duration": p["p_up"]}])


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: Corrosive Bite
    bite = delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"),
                   line("a_line", p["a_len"], p["a_w"], "EnemyWithoutTower", [attack(0, p["a_line"])]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), bite), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Corrosive Breath
    breath = [attack(p["q_dmg"], p["q_ad"]), acid(p), view("q_hit"), tsfx("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), None if is_native else tentacle(p),
                           delayed(p["q_st"] - 1, sfx("q_breath"), cview("q_cone"),
                                   cone(p["q_r"], p["q_cone"], "EnemyWithoutTower", breath))))

    # ------------------------------------------------------------------ skill2: Burrow Strike
    burst = [sfx("e_up"), sfx("e_hit"), anim("rise", p["e_rise"]), cview("e_burst"),
             around(p["e_r"], "EnemyWithoutTower", [attack(p["e_dmg"], p["e_ad"]),
                                                    {"type": "Airborne", "duration": p["e_up"]}, view("e_hit")])]
    dive = combine(anim("dig", 60), {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000,
                                     "end_effects": burst})
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), flag("e_dig", p["e_st"] + 60, cc_immune=True), delayed(p["e_st"] - 1, dive)))

    # ------------------------------------------------------------------ ult: Void's Wrath
    ball = [view("r_fall"), attack(p["r_mdmg"], p["r_mad"]), acid(p), tsfx("r_hit")]
    barrage = [delayed(k * p["r_every"], sfx("r_acid"), rain(p["r_mr"], "EnemyWithoutTower", ball))
               for k in range(p["r_n"])]
    r_dur = p["r_st"] + p["r_n"] * p["r_every"] + 6
    slam = combine(sfx("r"), cview("r_spikes"),
                   around(p["r_r"], "EnemyWithoutTower", [attack(p["r_dmg"], p["r_ad"]), view("r_hit")]))
    ult = action("ult", r_dur, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r_roar"), flag("r_wrath", r_dur + 2, cc_immune=True),
                         delayed(p["r_st"] - 1, slam, *barrage)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                             "tag": tag or name, "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the breath's cone, the burst's broken ground, the spikes and the falling acid stay where they struck; the
    # tentacle rises where its prey stood (baronnashor.rs plays it there; --plain on the prey)
    views_e = [E("a_hit"), E("q_cone", BIG, 2, False), E("q_hit"), E("e_burst", BIG, -1, False), E("e_hit"),
               E("r_spikes", BIG, -1, False), E("r_hit"), E("r_fall", BIG, 2, False), E("p_tent", BIG, 2, False)]
    views_b = [B_("q_acid")]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC"],
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
    if is_native:   # tft.dll (addons/tft/src/baronnashor.rs): the Void Rift's tentacles
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:rift", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Void's Wrath as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): the ult calls
    nothing native - the slam, the acid barrage and the immunity are all data. The views are the kit's own
    (tft_baronnashor_*)."""
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


def check_dll(p, kit):
    """addons/tft/src/baronnashor.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults
    are its fallback) and every name it plays (`bn("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "baronnashor.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"baronnashor.rs Params::default() differs from P (baronnashor.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'bn\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"baronnashor.rs plays names the kit does not have: {missing}")


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
    if not a.set and not a.params and not a.plain:
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
