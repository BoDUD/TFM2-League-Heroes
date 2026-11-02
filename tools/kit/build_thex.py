"""Build tft_thex.data_champion (a tft pack hero: T-Hex, top, Melee) from the parameters P.

    python tools/kit/build_thex.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

T-Hex (海克斯霸龙) is Teamfight Tactics set 16's 5-cost HexMech / Piltover / Gunslinger mech (TFT16_THex, range 2, 1100
health, 110 AD, 0.90 attack speed, 80 armour and magic resistance, 10/80 mana): Hex Armory / 海克斯军械库 - passive:
its attacks fire a barrage of 4 bullets; active: a shield (base + 10% health), then 30 mana a second drained: every
second a laser (physical, 70% less for each enemy it has passed, 90% less at most) and 4 missiles a second (one more
for each 25% bonus attack speed) shared out over the 4 nearest enemies. HexMech: a pilot jumps in at the start of a
fight; when the mech dies the pilot is thrown out and the mech knocks back and stuns the enemies near it. The kit is
our own design from that (the user's pick, 2026-11-02: top, plan A 「海克斯军械库」):
  passive Pilot Eject (驾驶员弹射): each life the pilot jumps in (a sound); when T-Hex dies the mech bursts: every
          enemy within p_r takes p_dmg + p_ratio% AD, is knocked back p_kb x p_kb_t and stunned p_stun ticks
          (tft.dll `tft_thex:pilot`; --plain: none - the data has no moment for a death).
  attack  Gatling Barrage (加特林弹幕) on `Enemy` (towers too): a_n bullets a_gap ticks apart from atk_st, a_pct% AD
          each; every fourth attack (Gunslinger, the hidden counters a_n1..a_n3) the last bullet adds a4_dmg + a4_ratio%
          AD.
  skill   Homing Missiles (追踪导弹), `Targeting` on `EnemyWithoutTower` (q_range): the back pods open at q_st and
          q_n missiles fall on random enemies within q_r, q_gap ticks apart: q_dmg + q_ratio% AD each.
  skill2  Rex Charge (霸龙冲撞), `Targeting` on `EnemyWithoutTower` (e_range): it charges the target (`MoveToTarget`
          e_speed) and bites: e_dmg + e_ratio% AD, knocked back e_kb x e_kb_t, e_slow% slower for e_slow_t ticks.
  ult     Hex Armory (海克斯军械库, TFT's), `Targeting` on `EnemyChampion` (r_range): a shield of r_sh + r_sh_ad% AD for
          r_sh_t ticks, then the pods open for r_n beats r_every ticks apart (it stands and fires): each beat a laser
          through the target, r_len long and r_w wide (tft.dll `tft_thex:laser`: r_dmg + r_ratio% AD on the first
          enemy, r_fall% less for each one before it, r_min% at least; --plain: r_plain% of it on every enemy in the
          line), and r_m missiles on random enemies within r_mr: r_mdmg + r_mratio% AD each.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/thex.rs; the passive is tft_thex:pilot,
params NATIVE_KEYS). A build of P checks thex.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_thex"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: TFT's range 2 = a short gun, 38000 (melee 25000-27000, the pack's ranged 55000-60000); radii count the unit's
# collision radius (~15000) on top. Timings are placeholders until the strips are rigged (tools/art/rig_thex.py). Stats
# start from the pack's top fighter-tanks (tft_brock hp 1200 / atk 72 every 78 / def 38, tft_sevika, league_jayce): a
# 5-cost mech, armoured, its damage physical and spread over many hits like TFT's.
# Numbers = the 10-min classic-SDK simulations (C:/t/al_sim/kd.py: top lane 0 against the base fighter, executioner,
# knight, berserker, lancer and pole warrior, three lineups, both sides; 2026-11-02), all --plain (no death burst, the
# laser r_plain% on every enemy in its line): the draft (hp 1150 def 40 mr 34 atk 70, R shield 150) -2.99 on seeds 1-8
# against tft_brock --plain +1.60 - it died a lot; hp 1350 def 55 mr 45 shield 250 -1.56; hp 1450 def 60 mr 50 shield 300
# atk 80 Q 40% bullets 30% +0.18; that with atk 84 and the laser 130% = P: +1.47 / +0.38 on seeds 1-8 / 9-16 (atk 82,
# laser 120%: +0.35 / +0.11).
P = {
    # stats (Melee, a top fighter-tank)
    "hp": 1450, "hp_g": 110, "atk": 84, "atk_g": 11, "apw": 20, "apw_g": 8, "def": 60, "def_g": 8, "mr": 50, "mr_g": 7,
    "ms": 950, "ms_g": 10,
    "atk_range": 38000, "atk_dur": 30, "atk_cd": 70, "atk_st": 10,
    # Gatling Barrage (TFT: attacks fire a barrage of 4 bullets; Gunslinger: every 4th attack bonus damage)
    "a_n": 4, "a_gap": 3, "a_pct": 30, "a_speed": 6000, "a_y": 9000, "a4_dmg": 30, "a4_ratio": 40,
    # Homing Missiles
    "q_cd": 540, "q_range": 60000, "q_dur": 36, "q_st": 14, "q_n": 6, "q_gap": 4, "q_r": 60000, "q_dmg": 20,
    "q_ratio": 40,
    # Rex Charge
    "e_cd": 720, "e_range": 55000, "e_dur": 30, "e_speed": 2400, "e_dmg": 40, "e_ratio": 90, "e_kb": 1500, "e_kb_t": 10,
    "e_slow": 30, "e_slow_t": 90,
    # Hex Armory (TFT: shield, a laser a second with 70% falloff a target (90% at most), 4 missiles a second)
    "r_cd": 3000, "r_range": 60000, "r_dur": 200, "r_st": 20, "r_sh": 300, "r_sh_ad": 120, "r_sh_t": 240,
    "r_n": 3, "r_every": 60, "r_len": 90000, "r_w": 14000, "r_dmg": 80, "r_ratio": 130, "r_fall": 70, "r_min": 10,
    "r_plain": 60, "r_m": 4, "r_mr": 60000, "r_mdmg": 15, "r_mratio": 25,
    # Pilot Eject (TFT's HexMech death: knock back and stun the enemies near it)
    "p_r": 40000, "p_dmg": 100, "p_ratio": 100, "p_kb": 1800, "p_kb_t": 12, "p_stun": 90,
}
# what tft.dll reads from passive.params (addons/tft/src/thex.rs)
NATIVE_KEYS = ("p_r", "p_dmg", "p_ratio", "p_kb", "p_kb_t", "p_stun", "r_len", "r_w", "r_dmg", "r_ratio", "r_fall",
               "r_min")
# names thex.rs uses that need no view: the pilot's sounds and the mech's burst
NATIVE_ONLY = {"p_in", "p_eject", "d"}


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
    return effects[0] if tick <= 0 and len(effects) == 1 else {"type": "Delayed", "tick": tick, "effects": list(effects)}


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


def on_me(*effects):
    """Effects on it alone."""
    return around(1000, "AllyOnlySelf", effects)


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, length, width, target, effects, apply=1):
    """A line from it through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it), hitting
    once `apply - 1` ticks after it appears (league_chogath's); no picture of its own."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": apply + 1,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def bolt(name, speed, rng, y):
    """The laser's picture: a fast view-only bolt from its mouth along the line (tft_aoshin's breath; a
    LineRangeProjectile's own picture is drawn at its feet' height and stands still)."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": "EnemyWithoutTower",
            "applied_effects": [], "end_effects": [], "speed": speed, "range": rng, "shape": circle(1000),
            "y_offset": y}


def rain(rng, effects):
    """One missile on a random enemy (no towers) within rng."""
    return {"type": "RandomTarget", "range": rng, "casting_target": "EnemyWithoutTower", "from_projectile": False,
            "effects": list(effects)}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: Gatling Barrage
    def bullet(extra=()):
        return homing("a_bullet", "Enemy", [attack(0, p["a_pct"]), view("a_hit"), *extra], p["a_speed"], p["a_y"])
    bonus = [attack(p["a4_dmg"], p["a4_ratio"]), view("a_crit"), tsfx("a_crit")]
    # every fourth attack: a_n1 after the first, a_n2 after the second, a_n3 after the third; the fourth's last bullet
    # carries the bonus and clears
    last = when("a_n3", combine(unflag("a_n3"), bullet(bonus)),
                when("a_n2", combine(unflag("a_n2"), flag("a_n3", None), bullet()),
                     when("a_n1", combine(unflag("a_n1"), flag("a_n2", None), bullet()),
                          combine(flag("a_n1", None), bullet()))))
    volley = [delayed(p["atk_st"] - 1 + k * p["a_gap"], bullet()) for k in range(p["a_n"] - 1)]
    volley.append(delayed(p["atk_st"] - 1 + (p["a_n"] - 1) * p["a_gap"], last))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), *volley), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Homing Missiles
    missile = [view("q_fall"), attack(p["q_dmg"], p["q_ratio"]), tsfx("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_st"] - 1, cview("q_launch"),
                                             *[delayed(k * p["q_gap"], rain(p["q_r"], missile)) for k in range(p["q_n"])])))

    # ------------------------------------------------------------------ skill2: Rex Charge
    bite = [attack(p["e_dmg"], p["e_ratio"]), {"type": "Knockback", "speed": p["e_kb"], "tick": p["e_kb_t"]},
            buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"), tsfx("e_hit")]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), cview("e_dash"),
                            {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000,
                             "end_effects": bite}))

    # ------------------------------------------------------------------ ult: Hex Armory
    if is_native:   # tft.dll: the laser loses r_fall% for each enemy it has passed
        laser = native("laser")
    else:           # --plain: r_plain% of the full beam on every enemy in the line
        laser = line("r_line", p["r_len"], p["r_w"], "EnemyWithoutTower",
                     [attack(p["r_dmg"] * p["r_plain"] // 100, p["r_ratio"] * p["r_plain"] // 100), view("r_hit")])
    rocket = [view("r_fall"), attack(p["r_mdmg"], p["r_mratio"]), tsfx("r_hit")]
    beat = [sfx("r_laser"), bolt("r_beam", 9000, p["r_len"], 9000), laser,
            *[delayed(k * p["r_every"] // p["r_m"], rain(p["r_mr"], rocket)) for k in range(p["r_m"])]]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_shield"), on_me(shield(p["r_sh"], p["r_sh_ad"], p["r_sh_t"])),
                         flag("r_shield", p["r_sh_t"]),
                         *[delayed(p["r_st"] - 1 + k * p["r_every"], *beat) for k in range(p["r_n"])]))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                             "tag": tag or name, "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the missiles fall where they were aimed (not following; the ult's are Q's picture); the charge's dust stays where
    # it left; the death burst where it fell (thex.rs plays it)
    views_e = [E("a_hit"), E("a_crit"), E("q_launch"), E("q_fall", BIG, 2, False), E("e_dash", FX, -1, False),
               E("e_hit"), E("r_hit"), E("r_fall", BIG, 2, False, "q_fall"), E("p_blast", BIG, 2, False)]
    views_b = [B_("e_slow"), B_("r_shield", BIG)]
    views_p = [B_("a_bullet", FX, 2), B_("r_beam", BIG, 2)]
    if not is_native:
        views_p += [B_("r_line", FX, 2, "r_hit")]   # a LineRangeProjectile's picture stands at its feet: a burn
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
    if is_native:   # tft.dll (addons/tft/src/thex.rs): the pilot's death burst and the laser's falloff
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:pilot", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Hex Armory as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll. The kit's --plain ult: the
    shield, the lasers (r_plain% on the whole line) and the missiles. The views are the kit's own (tft_thex_*)."""
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
    """addons/tft/src/thex.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback) and every name it plays or puts on (`tx("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "thex.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"thex.rs Params::default() differs from P (thex.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'tx\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"thex.rs plays or puts on names the kit does not have: {missing}")


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
