"""Build tft_idas.data_champion (the tft pack's eighteenth hero: Idas, support, Util) from the parameters P.

    python tools/kit/build_idas.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Idas (艾达丝) is the golden dragon of Teamfight Tactics set 7 (Dragonlands): the 4-cost unit TFT7_DragonGold
(Shimmerscale / Dragon / Guardian, an AP tank, range 1, 1050 health, 90 AD, 0.55 attack speed, 60 armour and magic
resistance, 40/100 mana), standing upright, her wings grown on her arms. TFT gives her one ability (Golden Scales /
黄金龙鳞: for 2 s she takes 30-50% less damage, then heals 450-600 (AP) and shields the allies near her 150-250 (AP) for
5 s; the shield gives 30% attack speed while it holds) and the Guardian trait (once a combat at 50% health a shield of
her maximum health on her and the nearest ally). The rest is our own design (the user's pick, 2026-10-30: support lane,
plan A 「黄金守护」):
  passive Guardian's Vow (护卫之誓): when her health drops under p_low% she and the allied champion nearest her within
          p_r get a shield of p_pct% of her maximum health for p_t ticks, then not again for p_cd ticks (each life starts
          ready). tft.dll (below). --plain: E's cast gives the shield (p_plain flat) to her and a random ally within p_r,
          off a p_cd lockout.
  attack  Dragon Claw (龙爪) on `Enemy` (towers too): 100% AD on atk_st.
  skill   Golden Breath (黄金龙息), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): she thrusts her head
          forward and breathes a cone of gold (`DirDot` q_r, q_cone): q_dmg + q_ratio% AP magic damage and molten scales
          (armour -q_shred% for q_shred_t ticks).
  skill2  Dragon's Roar (龙威振翅), `None` on `EnemyChampion` (e_range, only in fights): her wings snap open and she roars:
          every enemy within e_r is stunned e_stun ticks (the dragon's awe) and slowed e_slow% for e_slow_t ticks; she and every ally within e_ar get a shield of
          e_sh + e_sh_ap% AP for e_sh_t ticks.
  ult     Golden Scales (黄金龙鳞, TFT's), `None` on `EnemyChampion` (r_range): she wraps her wings round herself and takes
          r_red% less damage for r_t ticks; then the wings burst open: she heals r_heal + r_heal_ap% AP and every other
          allied champion within r_r gets a shield of r_sh + r_sh_ap% AP for r_sh_t ticks and r_as% attack speed while
          that shield holds (`WithShield`).
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/idas.rs; the passive is tft_idas:guardian,
params NATIVE_KEYS): the data reads no health, so it cannot know she is low, nor find the nearest ally. A build of P
checks idas.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_idas"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's tank supports (tft_loris, tft_steb, league_braum); radii count the unit's
# collision radius (~15000) on top. Timings are placeholders until the strips exist (tools/art/rig_idas.py). Stats
# start from tft_loris's (hp 1250 +115, atk 74, apw 30 +15, def 42, mr 30): Idas is the 4-cost dragon, a little
# sturdier, with TFT's even armour and resistance. Numbers = the 10-min classic-SDK simulations (C:/t/id_sim with
# C:/t/al_sim/kd.py: support lane 4 against the base priest, monk, bard, enchanter and taoist, three lineups, both
# sides; 2026-10-30), all --plain (the vow on E's cast, a flat p_plain shield, a random ally): the draft (Q 80 + 55%
# every 6 s, E every 10 s within 40000, R every 40 s, attack every 100 ticks) -2.93 on seeds 1-8 (tft_loris --plain
# +1.40 / +0.86 on seeds 9-16); attack every 84, Q 110 + 70% every 5 s, E every 9 s within 55000, R every 30 s -0.80;
# R every 25 s within 70000 -0.74, Q's shred 35% and E's slow 50% for 2 s -0.61, R 60% less damage, 200 heal, 150
# shields -0.58, all of them -0.87: no crowd control is what she lacks (tft_steb's way); + a 0.75 s stun on E's roar
# (e_stun 45) +1.18 / +1.40 = P.
P = {
    # stats (Util, the tank supports)
    "hp": 1250, "hp_g": 120, "atk": 72, "atk_g": 6, "apw": 35, "apw_g": 16, "def": 42, "def_g": 8, "mr": 36, "mr_g": 5,
    "ms": 960, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 84, "atk_st": 14,
    # passive Guardian's Vow (TFT's Guardian: 50% health, 35-150% of her health shared as shields, once a combat)
    "p_low": 50, "p_pct": 18, "p_t": 300, "p_r": 60000, "p_cd": 1800, "p_plain": 200,
    # Golden Breath
    "q_cd": 300, "q_range": 35000, "q_dur": 36, "q_rel": 14, "q_r": 50000, "q_cone": 600, "q_len": 70000, "q_w": 12000,
    "q_dmg": 110, "q_ratio": 70, "q_shred": 35, "q_shred_t": 240,
    # Dragon's Roar
    "e_cd": 540, "e_range": 55000, "e_dur": 30, "e_st": 12, "e_r": 42000, "e_slow": 50, "e_slow_t": 120,
    "e_stun": 45, "e_ar": 60000, "e_sh": 50, "e_sh_ap": 30, "e_sh_t": 180,
    # Golden Scales (TFT: 2 s, then the heal and the allies' shields for 5 s, +30% attack speed while they hold)
    "r_cd": 1500, "r_range": 70000, "r_t": 120, "r_out": 18, "r_red": 60, "r_heal": 200, "r_heal_ap": 60,
    "r_r": 60000, "r_sh": 150, "r_sh_ap": 50, "r_sh_t": 300, "r_as": 30,
}
# what tft.dll reads from passive.params (addons/tft/src/idas.rs)
NATIVE_KEYS = ("p_low", "p_pct", "p_t", "p_r", "p_cd")


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
    dur = "WithShield" if tick == "WithShield" else {"Time": {"tick": tick}}
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": dur, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def heal(amount, ratio, kind="Caster"):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": kind}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": [e for e in effects if e is not None]}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def line(name, length, width, target, effects, delay=1):
    """A line from her through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it); on
    `Ally` with no effects it is a picture only (build_nomsy.py's flame)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: the claw
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Golden Breath
    cone = {"DirDot": {"radius": p["q_r"], "range": p["q_cone"]}}
    melt = [ap(p["q_dmg"], p["q_ratio"]), buff("q_shred", p["q_shred_t"], defence_mult=-p["q_shred"]), tsfx("q_hit")]
    # the breath's picture rides a picture-only line from her mouth (top-bottom symmetric, turned with the cast)
    breath = combine(sfx("q_shred"), line("q_breath", p["q_len"], p["q_w"], "Ally", [], delay=p["q_dur"] - p["q_rel"]),
                     around(0, "EnemyWithoutTower", melt, {"Forward": {"offset": 1000}}, cone))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_rel"] - 1, breath)))

    # ------------------------------------------------------------------ skill2: Dragon's Roar
    guard = None
    if not is_native:   # the sims: the passive's shield on E's cast, off a p_cd lockout (the data reads no health)
        vow = [shield(p["p_plain"], 0, p["p_t"]), view("p_burst")]
        guard = when("p_cd", combine(), combine(flag("p_cd", p["p_cd"]), sfx("p"), on_me(*vow),
                                           pick(p["p_r"], "AllyNotSelf", *vow)))
    stun = [{"type": "Stun", "duration": p["e_stun"]}] if p["e_stun"] else []
    roar = combine(sfx("e_wing"), cview("e_roar"),
                   around(p["e_r"], "EnemyWithoutTower", [buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                                                           *stun]),
                   on_me(shield(p["e_sh"], p["e_sh_ap"], p["e_sh_t"])),
                   around(p["e_ar"], "AllyNotSelf", [shield(p["e_sh"], p["e_sh_ap"], p["e_sh_t"]),
                                                     buff("e_shield", p["e_sh_t"]), tsfx("e_shield")]),
                   guard)
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "None", "EnemyChampion",
                    combine(sfx("e"), delayed(p["e_st"] - 1, roar)))

    # ------------------------------------------------------------------ ult: Golden Scales
    burst = combine(sfx("r_hit"), sfx("r_roar"), sfx("r_heal"), cview("r_burst"),
                    on_me(heal(p["r_heal"], p["r_heal_ap"]), view("r_heal")),
                    around(p["r_r"], "AllyNotSelf", [shield(p["r_sh"], p["r_sh_ap"], p["r_sh_t"]),
                                                     buff("r_shield", "WithShield", attack_speed_mult=p["r_as"]),
                                                     tsfx("r_shield")]))
    ult = action("ult", p["r_t"] + p["r_out"], p["r_cd"], 1, p["r_range"], "None", "EnemyChampion",
                 combine(sfx("r"), sfx("r_loop"), flag("r_wrap", p["r_t"], damaged_reduce=p["r_red"]),
                         delayed(p["r_t"] - 1, burst)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # q_breath is a level plume along the cast line, top-bottom symmetric; e_roar / r_burst ride on her, drawn left-right
    # symmetric (the client never mirrors a picture); r_wrap's golden shell on her while the wings close (a caster
    # buff); the shields' glows (p_shield, e_shield, r_shield) are buff pictures on whoever holds them
    views_p = [B_("q_breath", BIG)]
    views_e = [E("a_hit"), E("p_burst", FX, 3), E("e_roar", BIG, 3), E("r_burst", BIG, 3), E("r_heal", FX, 3)]
    views_b = [B_("q_shred", FX, 3), B_("e_slow", FX, 3), B_("e_shield", FX, 3), B_("r_wrap", FX, 3),
               B_("r_shield", FX, 3)]
    if is_native:
        views_b += [B_("p_shield", FX, 3)]
    kit = {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "Heal", "Shield"],
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
    if is_native:   # tft.dll (addons/tft/src/idas.rs): the Guardian's shields at low health
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:guardian", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Golden Scales as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): the kit's ult
    is data alone (no tft.dll in it). The views are the kit's own (tft_idas_*); make_override copies them and their
    sheets."""
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
    """addons/tft/src/idas.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every picture it plays or puts on (`ia("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "idas.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"idas.rs Params::default() differs from P (idas.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'ia\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"idas.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"(?:effect_ref|passive_ref)": "tft_idas:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native code idas.rs does not register: {sorted(called - registered)}")


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
