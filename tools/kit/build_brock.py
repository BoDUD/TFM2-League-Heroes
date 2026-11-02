"""Build tft_brock.data_champion (a tft pack hero: Brock, top, Melee) from the parameters P.

    python tools/kit/build_brock.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Brock (岩宝) is Teamfight Tactics set 16's 5-cost Ixtal fighter (TFT16_Brock, range 1, 1800 health, 270 AD, 0.50 attack
speed, 60 armour and magic resistance, 40/100 mana): Seismic Slam / 震地猛击 - passive: immune to crowd control, his
attacks briefly knock up and splash 50% within a hex; active: he slams the ground, every enemy takes damage from his
health and AD, 15% less a hex from the centre (40% at least), the first time in a fight knocked up 1.75 s, and 12 rocks
fall round the board. The kit is our own design from that (the user's pick, 2026-11-02: top, plan A 「震地猛击」):
  passive Stone Heart (岩心不动): immune to crowd control (tft.dll puts `p_stone` on each life; --plain: his first
          action does, Permanent).
  attack  Quake Fist (震地拳) on `Enemy` (towers too): both fists down at atk_st, 100% AD on the target and a_splash% AD
          on every enemy within a_r of the point a_off in front of him (the target too); every third blow knocks the
          target up a_up ticks (the hidden counters a_n1 / a_n2).
  skill   Boulder Toss (巨岩投掷), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too): at q_st he hurls a
          boulder (a homing TargetProjectile, q_speed): q_dmg + q_ratio% AD + q_hp% of his maximum health, q_slow%
          slower for q_slow_t ticks.
  skill2  Moss Grip (苔藤缠握), `Targeting` on `EnemyWithoutTower` (e_range): at e_st roots burst under the target: e_dmg +
          e_ratio% AD, rooted (Bind) e_root ticks; he takes a mossy shield of e_sh + e_sh_ad% AD for e_sh_t ticks.
  ult     Seismic Slam (震地猛击, TFT's), `Targeting` on `EnemyChampion` (r_range): he leaps (r_air: untouchable and
          unstoppable until he lands), is out of sight from r_go, lands on the target at r_at: every enemy within r_r
          takes r_dmg + r_ratio% AD + r_hp% of his maximum health, r_fall% less a hex (r_hex) out, r_min% at least; the
          first time in r_mark ticks knocked up r_up ticks (tft.dll `tft_brock:slam`; --plain: three rings, the outer
          r_min% of it, every ring knocks up). Then r_rocks rocks fall on random enemies within r_rock_r, every
          r_rock_gap ticks from r_rock_t after the landing: r_rock + r_rock_ratio% AD each.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/brock.rs; the passive is tft_brock:stone,
params NATIVE_KEYS). A build of P checks brock.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_brock"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 27000 (the huge fists); radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips are rigged (tools/art/rig_brock.py). Stats start from the pack's top tanks (tft_terra hp
# 1380 / atk 84 every 66 / def 40, league_malphite, league_ornn): the 5-cost stone golem, slow and heavy, his skills
# physical and scaled by his health like TFT's.
# Numbers = the 10-min classic-SDK simulations (C:/t/br_sim/run.sh with C:/t/al_sim/kd.py: top lane 0 against the base
# fighter, executioner, knight, berserker, lancer and pole warrior, three lineups, both sides; 2026-11-02), all --plain
# (the stone heart from his first action, the slam three rings knocking every one up): the draft (atk 82, Q 60 + 120% + 3%
# every 8 s, E root 1.25 s + 120 shield every 10 s, R 120 + 110% + 5%) +6.83 on seeds 1-8 against tft_terra --plain +0.94
# - far too strong (14800 dealt: crowd-control immunity for good is worth a lot); toned down v2 +4.92; v3 = P (atk 72,
# hp 1200, splash 25%, Q 30 + 80% + 2% every 10 s, E root 0.83 s + 60 + 50% shield every 13 s, R 90 + 80% + 3%) +1.60 /
# +1.09 on seeds 1-8 / 9-16 (tft_terra +0.94 / +1.37); v4 (atk 70, root 0.75 s) +1.04 on 1-8.
P = {
    # stats (Melee, a top fighter-tank)
    "hp": 1200, "hp_g": 115, "atk": 72, "atk_g": 12, "apw": 20, "apw_g": 8, "def": 38, "def_g": 8, "mr": 30, "mr_g": 6,
    "ms": 940, "ms_g": 10,
    "atk_range": 27000, "atk_dur": 38, "atk_cd": 78, "atk_st": 20,
    # Quake Fist (TFT: attacks splash 50% within a hex and briefly knock up)
    "a_off": 22000, "a_r": 18000, "a_splash": 25, "a_up": 20,
    # Boulder Toss
    "q_cd": 600, "q_range": 50000, "q_dur": 32, "q_st": 18, "q_speed": 3000, "q_dmg": 30, "q_ratio": 80, "q_hp": 2,
    "q_slow": 30, "q_slow_t": 90,
    # Moss Grip
    "e_cd": 780, "e_range": 40000, "e_dur": 32, "e_st": 16, "e_dmg": 20, "e_ratio": 30, "e_root": 50, "e_sh": 60,
    "e_sh_ad": 50, "e_sh_t": 180,
    # Seismic Slam (TFT: health + AD damage, -15% a hex (40% at least), the first hit knocks up 1.75 s, 12 rocks)
    "r_cd": 3000, "r_range": 60000, "r_dur": 84, "r_go": 22, "r_at": 54, "r_r": 50000, "r_dmg": 90, "r_ratio": 80,
    "r_hp": 3, "r_hex": 18000, "r_fall": 15, "r_min": 40, "r_up": 75, "r_mark": 3600,
    "r_rocks": 6, "r_rock_t": 10, "r_rock_gap": 8, "r_rock_r": 60000, "r_rock": 25, "r_rock_ratio": 30,
}
# what tft.dll reads from passive.params (addons/tft/src/brock.rs)
NATIVE_KEYS = ("r_r", "r_dmg", "r_ratio", "r_hp", "r_hex", "r_fall", "r_min", "r_up", "r_mark")
# names brock.rs uses that need no view: the death crumble's sound, the hidden mark and the stone heart
NATIVE_ONLY = {"d", "r_mark", "p_stone"}


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


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def ahead(offset, radius, target, effects):
    """An area round the point `offset` in front of him, toward the action's target."""
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": {"Forward": {"offset": offset}},
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def stone():
    """--plain's Stone Heart: immune to crowd control, put on (Permanent) by his first action each life."""
    return when("p_stone", combine(), flag("p_stone", None, cc_immune=True))


def build(p, is_native=False):
    init = None if is_native else stone()

    # ------------------------------------------------------------------ attack: Quake Fist
    blow = [attack(0, 100), view("a_hit"), tsfx("a_hit"), view("a_quake"),
            ahead(p["a_off"], p["a_r"], "EnemyWithoutTower", [attack(0, p["a_splash"])])]
    thrown = combine({"type": "Airborne", "duration": p["a_up"]}, buff("a_up", p["a_up"]), tsfx("a_up"))
    # every third blow: a_n1 after the first, a_n2 after the second, the third throws and clears
    count = when("a_n2", combine(thrown, unflag("a_n2")),
                 when("a_n1", combine(unflag("a_n1"), flag("a_n2", None)),
                      flag("a_n1", None)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(init, sfx("a"), delayed(p["atk_st"] - 1, *blow, count)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Boulder Toss
    struck = [attack(p["q_dmg"], p["q_ratio"], p["q_hp"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
              view("q_hit"), tsfx("q_hit")]
    rock = {"type": "TargetProjectile", "name": n("q_rock"), "speed": p["q_speed"], "y_offset": 14000,
            "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in struck]}
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(init, delayed(p["q_st"] - 1, sfx("q"), rock)))

    # ------------------------------------------------------------------ skill2: Moss Grip
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(init, sfx("e"),
                            delayed(p["e_st"] - 1, view("e_vine"), tsfx("e_root"), attack(p["e_dmg"], p["e_ratio"]),
                                    {"type": "Bind", "duration": p["e_root"]}, buff("e_root", p["e_root"]),
                                    sfx("e_shield"), on_me(shield(p["e_sh"], p["e_sh_ad"], p["e_sh_t"])),
                                    flag("e_shield", p["e_sh_t"]))))

    # ------------------------------------------------------------------ ult: Seismic Slam
    full = (p["r_dmg"], p["r_ratio"], p["r_hp"])
    if is_native:   # tft.dll: damage by distance, the first-hit knock-up
        landing = native("slam")
    else:           # --plain: three rings (inner + middle + outer = 100%, the outer alone r_min%), all knocked up
        inner = (100 - p["r_min"]) // 2
        part = lambda pct: attack(*(v * pct // 100 for v in full))
        landing = combine(around(p["r_r"] // 3, "EnemyWithoutTower", [part(inner)]),
                          around(p["r_r"] * 2 // 3, "EnemyWithoutTower", [part(100 - p["r_min"] - inner)]),
                          around(p["r_r"], "EnemyWithoutTower", [part(p["r_min"]), {"type": "Airborne", "duration": p["r_up"]},
                                                                  view("r_hit")]))
    rocks = [delayed(p["r_rock_t"] + k * p["r_rock_gap"],
                     {"type": "RandomTarget", "range": p["r_rock_r"], "casting_target": "EnemyWithoutTower",
                      "from_projectile": False,
                      "effects": [view("r_rock"), attack(p["r_rock"], p["r_rock_ratio"]), tsfx("r_rock")]})
             for k in range(p["r_rocks"])]
    crash = combine({"type": "Teleport"}, sfx("r_slam"), cview("r_slam"), landing, *rocks)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(init, sfx("r"), cview("r_jump"), flag("r_air", p["r_at"], damaged_reduce=100, cc_immune=True),
                         delayed(p["r_go"] - 1, {"type": "CasterInvisible", "tick": p["r_at"] - p["r_go"] - 6}),
                         delayed(p["r_at"] - 7, {"type": "Teleport"}),
                         delayed(p["r_at"] - 1, crash)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the fist's ring, the launch dust and the landing shockwave lie on the ground where they struck (z -1, not
    # following); the roots and the falling rocks stay where they came up / down
    views_e = [E("a_hit"), E("a_quake", FX, -1, False), E("q_hit"), E("e_vine", FX, 2, False),
               E("r_jump", BIG, -1, False), E("r_slam", BIG, -1, False), E("r_rock", BIG, 2, False)]
    views_b = [B_("a_up"), B_("q_slow"), B_("e_root"), B_("e_shield", BIG)]
    views_p = [B_("q_rock", FX, 2)]
    if is_native:   # the buff tft.dll gives the thrown
        views_b += [B_("r_hit")]
    else:
        views_e += [E("r_hit", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC", "Shield"],
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
    if is_native:   # tft.dll (addons/tft/src/brock.rs): the Stone Heart and the slam's landing
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:stone", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Seismic Slam as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll. The kit's --plain ult: the
    leap, the rings, the knock-up and the rocks. The views are the kit's own (tft_brock_*)."""
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
    """addons/tft/src/brock.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback) and every name it plays or puts on (`bk("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "brock.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"brock.rs Params::default() differs from P (brock.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'bk\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"brock.rs plays or puts on names the kit does not have: {missing}")


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
