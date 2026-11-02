"""Build tft_mightymech.data_champion (a tft pack hero: The Mighty Mech, support, Util) from the parameters P.

    python tools/kit/build_mightymech.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Mighty Mech (超级机甲) is Teamfight Tactics set 17's 4-cost Mecha / Voyager (TFT17_Galio, an AD tank, range 1, 1300
health, 70 AD, 60 armour and magic resistance, 40/100 mana): a red, silver and black super robot with a fan of
blade-wings. TFT gives it one ability, Gravity Matrix / 引力矩阵 - a defensive stance for 4 s: durability, it draws the
enemies' projectiles to itself and heals over the stance; when it ends, a shockwave in 2 hexes, physical damage that
scales with armour and magic resistance. Mecha: it transforms into its Ultimate form (+40% health, the giant sword);
Voyager: at the start of combat the tanks get a shield, Voyagers twice. The rest is our own design (the user's pick,
2026-11-03: support lane, plan A):
  passive Voyager Escort (旅人护航): the first time each life an enemy champion comes within p_see (and again p_cd
          ticks after), the p_n allied champions within p_r with the lowest health share get a shield of p_sh + p_sh_hp%
          of its own maximum health for p_t ticks, itself p_self% of that (tft.dll `tft_mightymech:escort`; --plain:
          none - the data has no moment for it).
  attack  Piston Slash (活塞重斩) on `Enemy` (towers too): a swing of the giant sword it always holds (the user's pick
          of the look, 2026-11-03: picture B, the sword in both hands), 100% AD on atk_st; every third swing (the hidden
          counters a_n1, a_n2) the pistons drive it down: + a3_dmg + a3_ratio% AD and a3_slow% slower for a3_slow_t ticks.
  skill   Gravity Matrix (引力矩阵, TFT's), `None` on `EnemyChampion` (q_range: only in fights): its wings close round it
          for q_t ticks, q_red% less damage taken; the enemy champions within q_pull are taunted q_taunt ticks at the
          start and again halfway (the stand-in for drawing projectiles: nothing can turn a projectile); it heals q_hot +
          q_hot_ap% AP every q_every ticks; at the end a shockwave: every enemy within q_r takes q_dmg + q_arm% of its
          armour + magic resistance as physical damage (tft.dll `tft_mightymech:shockwave`; --plain: q_dmg + q_hp% of
          its maximum health, the data reads no armour).
  skill2  Mecha Leap (机甲飞跃), `Targeting` on `EnemyChampion` (e_range): it leaps (e_air ticks) onto the enemy
          champion diving its back line - among its allies within e_guard (not itself), the one with the lowest health
          share that has an enemy champion within e_near; the enemy nearest that ally - and lands: every enemy within e_r
          takes e_dmg + e_ratio% AD, the enemy champions knocked up e_up ticks (tft.dll `tft_mightymech:leap`; --plain:
          it leaps at its target, `MoveToTarget` e_speed).
  ult     Ultimate Form: Super Blade (究极变形·超级战刃), `Targeting` on `EnemyChampion` (r_range): it transforms - a shield
          of r_sh + r_sh_ap% AP for r_sh_t ticks, r_def% more armour and magic resistance for r_form ticks - at r_sword the
          sword's orange core blazes and its blade grows, and at r_st it slashes a line through its target r_len long and r_w
          wide: every enemy in it takes r_dmg + r_ratio% AD and is knocked up r_up ticks.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/mightymech.rs; the passive is
tft_mightymech:escort, params NATIVE_KEYS): the data reads no health or armour and has no moment for a fight's start, so
it can neither pick who needs the shield nor the enemy diving an ally. A build of P checks mightymech.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_mightymech"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's tank supports (tft_idas, tft_meepsie, tft_loris); radii count the unit's
# collision radius (~15000) on top; a TFT hex ~15000. Timings are placeholders until the strips are rigged
# (tools/art/rig_mightymech.py). Stats start from tft_meepsie's (hp 1250 +118, atk 66, apw 30 +15, def 44, mr 40): a
# 4-cost mech, its damage physical (TFT's AD tank), its heals and shields scaled by ability power.
# Numbers = the 10-min classic-SDK simulations (C:/t/mm_sim with C:/t/al_sim/kd.py: support lane 4 against the base
# priest, monk, bard, enchanter and taoist, three lineups, both sides; 2026-11-03), --plain (no escort shields, the
# shockwave on q_hp% health, the leap at its target): the draft (hp 1300, Q every 10 s with 35% less damage, 1 s taunts,
# 25 heals, R 150 + 140%) +4.34 on seeds 1-8 - the stance carried every fight; Q every 12.3 s, 22% less, 0.67 s taunts,
# 18 heals, R 120 + 110% +0.85 / +0.55 (seeds 1-8 / 9-16); with 20 heals and R 125 + 115% = P: +1.31 / +1.27 (18 heals
# +0.78 / +0.54); tft_meepsie --plain +1.00 on seeds 1-8.
P = {
    # stats (Util, the tank supports)
    "hp": 1250, "hp_g": 120, "atk": 66, "atk_g": 7, "apw": 28, "apw_g": 14, "def": 46, "def_g": 8, "mr": 42, "mr_g": 7,
    "ms": 930, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 85, "atk_st": 15,
    # Piston Punch: every third punch
    "a3_dmg": 30, "a3_ratio": 60, "a3_slow": 30, "a3_slow_t": 60,
    # Gravity Matrix (TFT: 4 s stance, durability, draws projectiles, heals, 2-hex shockwave on armour + MR)
    "q_cd": 740, "q_range": 40000, "q_dur": 24, "q_st": 10, "q_t": 240, "q_red": 22, "q_pull": 40000, "q_taunt": 40,
    "q_every": 30, "q_hot": 20, "q_hot_ap": 15, "q_r": 45000, "q_dmg": 60, "q_arm": 60, "q_hp": 3,
    # Mecha Leap (tft.dll; --plain: at its target)
    "e_cd": 720, "e_range": 70000, "e_dur": 40, "e_st": 8, "e_guard": 70000, "e_near": 35000, "e_air": 24,
    "e_speed": 2600, "e_r": 30000, "e_dmg": 60, "e_ratio": 80, "e_up": 45,
    # Ultimate Form: Super Blade (Mecha: the Ultimate form, the giant sword)
    "r_cd": 3000, "r_range": 60000, "r_dur": 90, "r_sword": 30, "r_st": 50, "r_sh": 150, "r_sh_ap": 80, "r_sh_t": 300,
    "r_def": 30, "r_form": 360, "r_len": 75000, "r_w": 20000, "r_dmg": 125, "r_ratio": 115, "r_up": 75,
    # Voyager Escort (TFT: combat start, the tanks shielded, Voyagers twice)
    "p_see": 70000, "p_r": 60000, "p_n": 1, "p_sh": 80, "p_sh_hp": 6, "p_self": 200, "p_t": 600, "p_cd": 1800,
}
# what tft.dll reads from passive.params (addons/tft/src/mightymech.rs)
NATIVE_KEYS = ("p_see", "p_r", "p_n", "p_sh", "p_sh_hp", "p_self", "p_t", "p_cd", "q_r", "q_dmg", "q_arm", "e_guard",
               "e_near", "e_air", "e_r", "e_dmg", "e_ratio", "e_up")
# names mightymech.rs uses that need no view: sounds (the escort's shields, the leap's landing, the fall)
NATIVE_ONLY = {"p", "e_hit", "d"}


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
    effects = [e for e in effects if e is not None]
    return effects[0] if tick <= 0 and len(effects) == 1 else {"type": "Delayed", "tick": tick, "effects": effects}


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


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Caster"}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": [e for e in effects if e is not None]}


def on_me(*effects):
    """Effects on it alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def line(name, length, width, target, effects, apply=1):
    """A line from it through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it), hitting
    once `apply - 1` ticks after it appears; its picture lies on the ground along the line (the slash's cut)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": apply + 1,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: Piston Slash
    punch = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    crush = [attack(p["a3_dmg"], p["a3_ratio"]), buff("a_slow", p["a3_slow_t"], move_speed_mult=-p["a3_slow"]),
             view("a_crush")]
    # every third swing: a_n1 after the first, a_n2 after the second; the third carries the pistons and clears
    hit = when("a_n2", combine(unflag("a_n2"), *punch, *crush),
               when("a_n1", combine(unflag("a_n1"), flag("a_n2", None), *punch),
                    combine(flag("a_n1", None), *punch)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["atk_st"] - 1, hit)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Gravity Matrix
    pull = around(p["q_pull"], "EnemyChampion", [{"type": "Taunt", "duration": p["q_taunt"]}, view("q_taunt")])
    mends = [delayed(k * p["q_every"] - 1, on_me(heal(p["q_hot"], p["q_hot_ap"])))
             for k in range(1, p["q_t"] // p["q_every"] + 1)]
    if is_native:   # tft.dll: the shockwave on its armour + magic resistance
        wave = native("shockwave")
    else:
        wave = combine(sfx("q_hit"), around(p["q_r"], "EnemyWithoutTower", [attack(p["q_dmg"], 0, p["q_hp"]),
                                                                            view("q_hit")]))
    stance = combine(sfx("q_shield"), flag("q_stance", p["q_t"], damaged_reduce=p["q_red"]), pull,
                     delayed(p["q_t"] // 2 - 1, sfx("q_shield"), pull), *mends,
                     delayed(p["q_t"] - 1, unflag("q_stance"), cview("q_wave"), wave))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "None", "EnemyChampion",
                   combine(sfx("q"), delayed(p["q_st"] - 1, stance)))

    # ------------------------------------------------------------------ skill2: Mecha Leap
    if is_native:   # tft.dll: onto the enemy diving its weakest ally, the leap, the landing
        leap = native("leap")
    else:           # --plain: at its target
        landed = [sfx("e_hit"), cview("e_slam"),
                  around(p["e_r"], "EnemyWithoutTower", [attack(p["e_dmg"], p["e_ratio"])]),
                  around(p["e_r"], "EnemyChampion", [{"type": "Airborne", "duration": p["e_up"]}, view("e_up")])]
        leap = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000, "end_effects": landed}
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(sfx("e"), delayed(p["e_st"] - 1, leap)))

    # ------------------------------------------------------------------ ult: Ultimate Form: Super Blade
    slash = line("r_slash", p["r_len"], p["r_w"], "EnemyWithoutTower",
                 [attack(p["r_dmg"], p["r_ratio"]), {"type": "Airborne", "duration": p["r_up"]}, view("r_hit")])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), cview("r_transform"), on_me(shield(p["r_sh"], p["r_sh_ap"], p["r_sh_t"])),
                         flag("r_form", p["r_form"], defence_mult=p["r_def"], magic_resistance_mult=p["r_def"]),
                         delayed(p["r_sword"] - 1, sfx("r_sword"), cview("r_sword")),
                         delayed(p["r_st"] - 1, sfx("r_swing"), sfx("r_hit"), slash)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    # the shockwave ring and the landing's crater lie where they happened (not following); the transform's flare and
    # the blazing, growing blade ride on it; r_slash is the cut along the slash's line (a LineRangeProjectile's picture stands
    # at its feet, turned with the cast)
    views_e = [E("a_hit"), E("a_crush"), E("q_taunt", FX, 3), E("q_wave", BIG, -1, False), E("q_hit"),
               E("e_slam", BIG, -1, False), E("e_up", FX, 3), E("r_transform", BIG, 3), E("r_sword", BIG, 3), E("r_hit")]
    views_b = [B_("a_slow"), B_("q_stance", BIG), B_("r_form", FX, 1), B_("p_shield")]
    views_p = [B_("r_slash", BIG, 1)]
    kit = {
        "id": ID, "category": "Util", "tags": ["AD", "Melee", "Tank", "CC", "Shield", "Heal"],
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
    if is_native:   # tft.dll (addons/tft/src/mightymech.rs): the escort, the shockwave, the leap, the fall
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:escort", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Ultimate Form: Super Blade as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN):
    the ult is the data's own (no tft.dll), so his copy is the kit's: the shield, the armour, the blade, the slash. The
    views are the kit's own (tft_mightymech_*); make_override copies them and their sheets."""
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
    """addons/tft/src/mightymech.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`mm("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "mightymech.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"mightymech.rs Params::default() differs from P (mightymech.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'\bmm\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"mightymech.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"(?:effect_ref|passive_ref)": "tft_mightymech:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native code mightymech.rs does not register: {sorted(called - registered)}")


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
