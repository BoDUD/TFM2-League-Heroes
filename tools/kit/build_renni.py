"""Build tft_renni.data_champion (the tft pack's thirteenth hero: Renni, top, Melee) from the parameters P.

    python tools/kit/build_renni.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Renni is one of Arcane's chem-barons of Zaun, a red-haired brawler with a green-glowing respirator, a ruff of dark
feathers and a huge brass chainsaw: a 3-cost of Teamfight Tactics set 13 (TFT13_Chainsaw, Chem-Baron / Bruiser, an AD
tank, range 1, 850 health, 40/90 mana). TFT gives her one ability (Mudrunner Slam / 泥奔者重击: over 1.5 s she heals 15%
of her maximum health while holding the target up in the air, stunned, for 500% AD; then slams it down for 200% AD to
the enemies next to it) and two traits: Chem-Baron (Shimmer, black markets, maximum health for every market passed)
and Bruiser (+20-80% maximum health). The rest is our own design (the user's pick, 2026-10-29: top lane, plan A
「泥奔者」):
  passive Shimmer Frenzy (微光狂热): under p_line% health (once every p_cd ticks) she shoots herself up with shimmer:
          p_as% attack speed for p_t ticks and p_heal% of her maximum health healed over them (tft.dll: the data reads
          no health; --plain: on her guard (E) once every p_cd ticks, a flat p_flat heal).
  attack  Chainsaw Grind (链锯研磨) on `Enemy` (towers too): the saw bites three times, at atk_st and a_gap apart,
          a_pct% AD each.
  skill   Chainsaw Charge (链锯冲撞), `Targeting` on `EnemyWithoutTower` (q_range): she charges at the target
          (`MoveToTarget` q_speed, her `charge` frames) and grinds the cone in front of her (`DirDot` q_r, q_cone)
          q_n times q_gap apart (her `grind` frames): q_dmg + q_ad% AD and q_slow% slower for q_slow_t ticks.
  skill2  Saw Guard (锯刃格挡), `Targeting` on `EnemyWithoutTower` (e_range): the saw raised in front of her - a
          shield of e_sh + e_sh_ad% AD for e_t ticks and e_dr% damage reduction as long.
  ult     Mudrunner Slam (泥奔者重击, TFT's), `Targeting` on `EnemyChampion` (r_range): on r_st she rams the saw in and
          heaves the target up overhead: r_dmg + r_ad% AD, thrown up r_up ticks (stunned in the air); she is
          unstoppable for the cast and heals r_heal% of her maximum health while she holds it (tft.dll; --plain: a flat
          r_flat); on r_slam (her `slam` frames) she slams it down: r_s + r_s_ad% AD to every enemy within r_r of the
          point in front of her.

tft.dll (addons/tft/src/renni.rs): the shimmer shot by health and both heals by maximum health (passive
tft_renni:shimmer). A build of P checks renni.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_renni"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's top fighters; radii count the unit's collision radius (~15000) on top.
# Timings are provisional until her frames are rigged (tools/art/rig_renni.py): TFT's grind bites three times in its
# loop, the lift is up at ~600 ms of its 1.4 s clip, the slam lands at ~310 ms of its 1.1 s clip. Stats start from the
# pack's top tanks (tft_scar hp 1120 +110, def 36, mr 32; tft_kobuko; league_sett) with attack instead of ability power.
# Numbers = the 10-min classic-SDK simulations (C:/t/al_sim/kd.py, top lane against the base fighter, executioner,
# knight, berserker, lancer and pole warrior, three lineups, both sides; 2026-10-29), all --plain (the shimmer shot on
# her guard, flat heals): the draft (atk 78, bites 40%, Q 30 + 50%, R 100 + 180% / slam 60 + 100%) -0.06 on seeds 1-8
# against tft_scar --plain +2.87; atk 85, bites 45%, Q 50 + 70%, R 140 + 200% / 80 + 120% +4.10 (more health and
# shield on top: +4.38 / +4.40); between = P: +2.03 / +2.05 (seeds 9-16; tft_scar +1.85, league_sett +2.07).
P = {
    # stats (Melee, a top tank with attack damage)
    "hp": 1150, "hp_g": 115, "atk": 82, "atk_g": 11, "apw": 0, "apw_g": 0, "def": 38, "def_g": 8, "mr": 30, "mr_g": 5,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 72, "atk_st": 12, "a_gap": 6, "a_pct": 42,
    # passive Shimmer Frenzy (Chem-Baron's shimmer)
    "p_line": 40, "p_cd": 1800, "p_t": 240, "p_as": 40, "p_heal": 20, "p_flat": 160,
    # Chainsaw Charge
    "q_cd": 540, "q_range": 40000, "q_dur": 50, "q_speed": 3600, "q_n": 3, "q_gap": 10, "q_r": 38000, "q_cone": 600,
    "q_dmg": 40, "q_ad": 60, "q_slow": 30, "q_slow_t": 90, "q_grind_t": 30,
    # Saw Guard
    "e_cd": 600, "e_range": 30000, "e_dur": 20, "e_sh": 100, "e_sh_ad": 80, "e_t": 150, "e_dr": 20,
    # Mudrunner Slam (TFT: 1.5 s up, 500% AD, slam 200% AD to the adjacent, heal 15% max hp)
    "r_cd": 3000, "r_range": 30000, "r_dur": 90, "r_st": 14, "r_up": 66, "r_slam": 74, "r_slam_t": 16,
    "r_dmg": 120, "r_ad": 190, "r_heal": 15, "r_flat": 150, "r_r": 30000, "r_s": 70, "r_s_ad": 110,
}
# what tft.dll reads from passive.params (addons/tft/src/renni.rs), and the names only it puts on
NATIVE_ONLY = ()
NATIVE_KEYS = ("p_line", "p_cd", "p_t", "p_as", "p_heal", "r_heal", "r_up")


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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def heal(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Caster"}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: three bites of the saw
    bite = lambda: [attack(0, p["a_pct"]), view("a_hit"), tsfx("a_hit")]
    bites = [delayed(p["atk_st"] - 1 + k * p["a_gap"], *bite()) for k in range(3)]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), *bites), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Chainsaw Charge
    cone = {"DirDot": {"radius": p["q_r"], "range": p["q_cone"]}}
    ground = [attack(p["q_dmg"], p["q_ad"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
              view("q_hit"), tsfx("q_hit")]
    grind = [anim("grind", p["q_grind_t"]), sfx("q_saw")] + [
        delayed(k * p["q_gap"], around(0, "EnemyWithoutTower", ground, {"Forward": {"offset": 1000}}, cone))
        for k in range(p["q_n"])]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), anim("charge", p["q_dur"]),
                           {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] + 40000,
                            "end_effects": grind}))

    # ------------------------------------------------------------------ skill2: Saw Guard
    # --plain: the shimmer shot rides on the guard (once every p_cd ticks): the data reads no health
    rush = None if is_native else when("p_cool", combine(), combine(
        flag("p_cool", p["p_cd"]), flag("p_rush", p["p_t"], attack_speed_mult=p["p_as"]), sfx("p"), cview("p"),
        on_me(heal(p["p_flat"], 0))))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), cview("e"),
                            on_me({"type": "Shield", "amount": p["e_sh"], "attack_ratio": p["e_sh_ad"], "ap_ratio": 0,
                                   "tick": p["e_t"]}),
                            flag("e_guard", p["e_t"], damaged_reduce=p["e_dr"]), rush))

    # ------------------------------------------------------------------ ult: Mudrunner Slam
    # the heal while she holds it up: tft.dll heals r_heal% of her maximum health over r_hold (--plain: a flat r_flat)
    held = flag("r_hold", p["r_up"]) if is_native else on_me(heal(p["r_flat"], 0))
    lift = delayed(p["r_st"] - 1, sfx("r_lift"), attack(p["r_dmg"], p["r_ad"]),
                   {"type": "Airborne", "duration": p["r_up"]}, buff("r_up", p["r_up"]), view("r_hit"), held)
    slam = delayed(p["r_slam"] - 1, anim("slam", p["r_slam_t"]), sfx("r_hit"), sfx("r_slam"), cview("r_slam"),
                   around(p["r_r"], "EnemyWithoutTower", [attack(p["r_s"], p["r_s_ad"]), view("r_hit")],
                          {"Forward": {"offset": p["atk_range"]}}))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_vo"), flag("r_air", p["r_dur"], cc_immune=True), lift, slam))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the bites, the grind and the lift spark on what they hit; the shot of shimmer and the raised saw's glint play on
    # her; the slam's crack lies on the ground in front of her (z -1, not following); the saw itself is in her frames
    views_e = [E("a_hit"), E("q_hit"), E("p", FX, 3), E("e", FX, 3), E("r_hit"), E("r_slam", BIG, -1, False)]
    views_b = [B_("q_slow", FX, 3), B_("p_rush", FX, 3), B_("e_guard", FX, 3), B_("r_up", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC", "Heal"],
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
    if is_native:   # tft.dll (addons/tft/src/renni.rs): the shimmer shot, both heals by maximum health
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:shimmer", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/renni.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`sc("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "renni.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"renni.rs Params::default() differs from P (renni.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'sc\("(\w+)"\)', src)) - set(NATIVE_ONLY)
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"renni.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_renni:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects renni.rs does not register: {sorted(called - registered)}")


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
