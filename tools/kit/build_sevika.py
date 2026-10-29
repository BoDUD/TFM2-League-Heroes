"""Build tft_sevika.data_champion (the tft pack's fifteenth hero: Sevika, top, Melee) from the parameters P.

    python tools/kit/build_sevika.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Sevika is Arcane's Zaun enforcer turned chem-baron: a broad-shouldered woman whose left arm is a huge brass mechanical
arm that Jinx painted over - teal plates, magenta spikes, a pair of claws that open as a jaw, and a slot machine on its
shoulder. A 5-cost of Teamfight Tactics set 13 (TFT13_Lieutenant, High Roller / Chem-Baron / Pit Fighter, an AD
fighter, range 1, 1277 health, 0/50 mana). TFT gives her one ability (Beat the Odds / 扭转局势: randomly one of three
spells - Flamethrower, Extendo-Punch, Chomp - with a chance of a jackpot) and High Roller (each cast rolls one of Jinx's
mods: rockets, a shield, gold, or triple = the spell empowered). Our own design (the user's pick, 2026-10-29: top lane,
plan A 「百变铁手」) takes the three spells apart into her three slots:
  passive High Roller (百变铁手): each skill, skill2 and ult cast rolls the slot machine (tft.dll `tft_sevika:roll`):
          p_tri% the jackpot (triple: this cast empowered, `p_triple` for p_tri_t ticks), else one of three mods
          alike: rockets (p_rk_n homing rockets, p_rk_gap apart, each at a random enemy within p_rk_r: p_rk_dmg +
          p_rk_ad% AD), a shield (p_sh + p_sh_ad% AD for p_sh_t ticks) or shimmer (p_as% attack speed for p_as_t).
          (--plain: every cast a third of each mod - a third of the rockets on the target, a third of the shield and
          of the shimmer; never the jackpot.)
  attack  Mechanical Fist (机械铁拳) on `Enemy` (towers too): a punch, a_pct% AD; every third one (a_t ticks to land the
          next) the claws clamp: a2_dmg + a2_ad% AD.
  skill   Flamethrower (喷火器), `Targeting` on `EnemyWithoutTower` (q_range): the arm levelled, q_n waves of flame
          q_gap apart into the cone in front of her (`DirDot` q_r, q_cone): q_dmg + q_ad% AD each (x q_tri_k% on the
          jackpot) and a burn picture; q_dr% less damage taken while she flames.
  skill2  Extendo-Punch (伸缩拳), `Targeting` on `EnemyWithoutTower` (e_range): the fist shot on a spring at the target
          (tft.dll `tft_sevika:punch`: the first enemy in its line takes e_dmg + e_ad% AD and is knocked back
          e_kb_speed x e_kb_t; an enemy within e_behind of where it lands is hit for e_dmg2% of it and both are stunned
          e_stun ticks; on the jackpot the target is stunned anyway and takes e_tri% more). (--plain: a homing fist:
          the damage, the knockback and a stun of e_stun / 2.)
  ult     Chomp (嚼一嚼), `Targeting` on `EnemyChampion` (r_range): she dashes to the target (`MoveToTarget` r_speed, her
          `dash` frames) and the claws bite (tft.dll `tft_sevika:chomp`, her `chomp` frames): r_n bites r_gap apart
          (r_tri_n on the jackpot), r_dmg + r_ad% AD each, the first stuns r_stun ticks, each a bleed (r_bl_ad% AD over
          r_bleed ticks, the passive's); a target under r_exec% (r_exec_tri% on the jackpot) health after the last
          bite is executed; a kill re-dashes to the nearest enemy champion within r_reset (r_resets times a cast) at
          r_fall% damage. (--plain: the bites, the stun and the bleed as delayed hits; no execute, no re-dash.)

tft.dll (addons/tft/src/sevika.rs): the roll, the punch, the chomp and the bleed (passive tft_sevika:roll). A build of
P checks sevika.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_sevika"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's top fighters; radii count the unit's collision radius (~15000) on top.
# Timings are provisional until her frames are rigged (tools/art/rig_sevika.py): TFT's punch lands at ~200 ms of its
# loop, the flamethrower holds 0.67 s loops, the chomp's two slams come ~400 ms apart. Stats start from the pack's top
# fighters (tft_renni hp 1150 +115, atk 82; league_sett) - a 5-cost, a little stronger in a fight, less of a tank.
P = {
    # stats (Melee, a top fighter with attack damage)
    "hp": 1180, "hp_g": 118, "atk": 80, "atk_g": 11, "apw": 0, "apw_g": 0, "def": 36, "def_g": 7, "mr": 30, "mr_g": 5,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 66, "atk_st": 12, "a_pct": 100, "a_t": 240, "a2_dmg": 25,
    "a2_ad": 150,
    # passive High Roller (the slot machine on every skill cast)
    "p_tri": 12, "p_tri_t": 150,
    "p_rk_n": 4, "p_rk_gap": 6, "p_rk_r": 60000, "p_rk_dmg": 15, "p_rk_ad": 30, "p_rk_speed": 5000,
    "p_sh": 60, "p_sh_ad": 100, "p_sh_t": 180,
    "p_as": 35, "p_as_t": 180,
    # Flamethrower
    "q_cd": 480, "q_range": 32000, "q_dur": 72, "q_st": 10, "q_n": 5, "q_gap": 12, "q_r": 40000, "q_cone": 700,
    "q_dmg": 12, "q_ad": 30, "q_tri_k": 160, "q_dr": 30, "q_burn_t": 60, "q_len": 45000, "q_w": 22000,
    # Extendo-Punch
    "e_cd": 600, "e_range": 55000, "e_dur": 40, "e_st": 14, "e_w": 8000, "e_speed": 4000,
    "e_dmg": 40, "e_ad": 120, "e_kb_speed": 2500, "e_kb_t": 10, "e_behind": 30000, "e_stun": 72, "e_dmg2": 50,
    "e_tri": 50,
    # Chomp (TFT: 2 slams 320% AD, stun 1.25 s, bleed 75% AD over 5 s, execute 15%, re-dash 2 hexes at 80%)
    "r_cd": 2700, "r_range": 40000, "r_dur": 70, "r_speed": 4000, "r_chomp_t": 40,
    "r_n": 2, "r_tri_n": 4, "r_gap": 18, "r_dmg": 60, "r_ad": 130, "r_stun": 66, "r_bleed": 300, "r_bl_ad": 60,
    "r_exec": 15, "r_exec_tri": 25, "r_reset": 30000, "r_resets": 2, "r_fall": 80,
}
# what tft.dll reads from passive.params (addons/tft/src/sevika.rs), and the names only it puts on or plays
NATIVE_ONLY = ("p_rocket", "p_rocket_hit", "p_shield", "p_shimmer", "p_jackpot", "p_jackpot_fx", "e_fist", "e_hit",
               "e_stun", "e_launch", "e_tri", "r_bleed", "r_hit", "r_kill", "r_hop", "r_tri")
NATIVE_KEYS = ("p_tri", "p_tri_t", "p_rk_n", "p_rk_gap", "p_rk_r", "p_rk_dmg", "p_rk_ad", "p_rk_speed",
               "p_sh", "p_sh_ad", "p_sh_t", "p_as", "p_as_t",
               "e_range", "e_w", "e_speed", "e_dmg", "e_ad", "e_kb_speed", "e_kb_t", "e_behind", "e_stun", "e_dmg2",
               "e_tri",
               "r_n", "r_tri_n", "r_gap", "r_dmg", "r_ad", "r_stun", "r_bleed", "r_bl_ad", "r_exec", "r_exec_tri",
               "r_reset", "r_resets", "r_fall")


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


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone."""
    return around(1000, "AllyOnlySelf", effects)


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, length, width, target, effects, delay=1):
    """A line from her through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it),
    hitting once a tick after it appears (league_chogath's); on `Ally` with no effects it is a picture only."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def plain_roll(p):
    """--plain: the slot machine's average - a third of each mod, never the jackpot (the data rolls nothing)."""
    k = p["p_rk_n"]
    return combine(attack(p["p_rk_dmg"] * k // 3, p["p_rk_ad"] * k // 3), view("p_rocket_hit"),
                   on_me({"type": "Shield", "amount": p["p_sh"] // 3, "attack_ratio": p["p_sh_ad"] // 3,
                          "ap_ratio": 0, "tick": p["p_sh_t"]}),
                   flag("p_shimmer", p["p_as_t"], attack_speed_mult=p["p_as"] // 3))


def build(p, is_native=False):
    roll = (lambda: combine(sfx("p"), cview("p"), native("roll"))) if is_native else \
        (lambda: combine(sfx("p"), cview("p"), plain_roll(p)))

    # ------------------------------------------------------------------ attack: a punch, every third the claws clamp
    hit = lambda: [attack(0, p["a_pct"]), view("a_hit"), tsfx("a_hit")]
    clamp = [attack(p["a2_dmg"], p["a2_ad"]), view("a2_hit"), tsfx("a2_hit")]
    count = when("a_2", combine(unflag("a_2"), sfx("a2"), *clamp),
                 when("a_1", combine(unflag("a_1"), flag("a_2", p["a_t"]), sfx("a"), *hit()),
                      combine(flag("a_1", p["a_t"]), sfx("a"), *hit())))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      count, atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Flamethrower
    cone = {"DirDot": {"radius": p["q_r"], "range": p["q_cone"]}}
    lick = lambda k: [attack(p["q_dmg"] * k // 100, p["q_ad"] * k // 100), buff("q_burn", p["q_burn_t"])]
    # the jackpot read once per wave (one shared subtree: the damage alone differs)
    burn = when("p_triple", around(0, "EnemyWithoutTower", lick(p["q_tri_k"]), {"Forward": {"offset": 1000}}, cone),
                around(0, "EnemyWithoutTower", lick(100), {"Forward": {"offset": 1000}}, cone))
    waves = [delayed(p["q_st"] - 1 + k * p["q_gap"], sfx("q_fire") if k == 0 else None,
                     line("q_flame", p["q_len"], p["q_w"], "Ally", [], delay=p["q_gap"]), burn,
                     unflag("p_triple") if k == p["q_n"] - 1 else None)
             for k in range(p["q_n"])]
    for w in waves:
        w["effects"] = [e for e in w["effects"] if e is not None]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(roll(), sfx("q"), sfx("q_loop"), anim("flame", p["q_dur"]),
                           flag("q_guard", p["q_dur"], damaged_reduce=p["q_dr"]), *waves))

    # ------------------------------------------------------------------ skill2: Extendo-Punch
    if is_native:
        punch = delayed(p["e_st"] - 1, native("punch"))
    else:   # --plain: a homing fist, the knockback and half the stun
        punch = delayed(p["e_st"] - 1, homing("e_fist", p["e_speed"], "EnemyWithoutTower",
                                              [attack(p["e_dmg"], p["e_ad"]), view("e_hit"),
                                               {"type": "Knockback", "speed": p["e_kb_speed"], "tick": p["e_kb_t"]},
                                               {"type": "Stun", "duration": p["e_stun"] // 2}]))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(roll(), sfx("e"), punch))

    # ------------------------------------------------------------------ ult: Chomp
    if is_native:
        bite = [anim("chomp", p["r_chomp_t"]), sfx("r_vo"), native("chomp")]
    else:   # --plain: the bites, the stun and the bleed as delayed hits on the target
        bl = p["r_bleed"] // 5
        bite = [anim("chomp", p["r_chomp_t"]), sfx("r_vo"),
                around(p["atk_range"] + 10000, "EnemyChampion", [
                    {"type": "Stun", "duration": p["r_stun"]},
                    *[delayed(k * p["r_gap"] + 1, attack(p["r_dmg"], p["r_ad"]), view("r_hit"))
                      for k in range(p["r_n"])],
                    *[delayed(k * bl + bl, attack(0, p["r_bl_ad"] // 5)) for k in range(5)]])]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(roll(), sfx("r"), anim("dash", p["r_dur"]),
                         flag("r_rush", p["r_dur"], cc_immune=True),
                         {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 40000,
                          "end_effects": [sfx("r_dash"), *bite]}))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the punches, the clamp, the rockets, the fist and the bites burst on what they hit; the slot machine's spin and the
    # jackpot play on her (symmetric); the flame is a picture-only line turned to the target (drawn top-bottom
    # symmetric, so turned half round to the left it reads the same); the rockets and the fist fly (turned with
    # their flight)
    views_p = [B_("q_flame", BIG), B_("p_rocket"), B_("e_fist")]
    views_e = [E("a_hit"), E("a2_hit"), E("p", FX, 4), E("p_rocket_hit"), E("e_hit"), E("r_hit"), E("r_kill", BIG, 3)]
    views_b = [B_("q_burn", FX, 3), B_("p_shimmer", FX, 3), B_("p_triple", FX, 4), B_("e_stun", FX, 4),
               B_("r_bleed", FX, 3)]
    if is_native:
        views_e += [E("p_jackpot", BIG, 4), E("p_shield", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC", "Shield", "Dot"],
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
    if is_native:   # tft.dll (addons/tft/src/sevika.rs): the roll, the punch, the chomp, the bleed
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:roll", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Chomp as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on bundle
    is on the Workshop and the tft mod is not, so the bites cannot be tft.dll's: the kit's --plain ult without the
    slot machine (a stolen arm rolls nothing). The views are the kit's own (tft_sevika_*); make_override copies them
    and their sheets."""
    p = dict(P) if p is None else p
    ult = build(p, False)["ult"]["effect"]
    ult["effects"] = ult["effects"][1:]
    return ult


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
    """addons/tft/src/sevika.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`sv("...")`) is the kit's or NATIVE_ONLY's, and every Native the
    kit calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "sevika.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"sevika.rs Params::default() differs from P (sevika.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'sv\("(\w+)"\)', src)) - set(NATIVE_ONLY)
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"sevika.rs plays or puts on names the kit does not have: {missing}")
    views = {v["name"] for k in ("view_projectiles", "view_effects", "view_buffs") for v in kit[k]}
    unseen = sorted(x for x in ("p_rocket", "p_rocket_hit", "p_shield", "p_shimmer", "p_jackpot", "e_fist", "e_hit",
                                "e_stun", "r_bleed", "r_hit", "r_kill") if n(x) not in views)
    if unseen:
        raise SystemExit(f"pictures sevika.rs plays have no view: {unseen}")
    called = set(re.findall(r'"effect_ref": "tft_sevika:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects sevika.rs does not register: {sorted(called - registered)}")


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
