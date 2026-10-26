"""Build tft_silco.data_champion (the tft pack's fourth hero: Silco, mid, Magician) from the parameters P.

    python tools/kit/build_silco.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Silco is Zaun's chem-baron from Arcane, a 4-cost of Teamfight Tactics set 13 (TFT13_Silco, Chem-Baron / Dominator,
range 4, 800 health, 30/80 mana). TFT gives him one ability (Canister of Monstrosities: a canister thrown at the target
deals magic damage and releases monstrosities that attack 5 times each) and the Dominator trait (a shield when combat
starts; casting grants stacking ability power). The rest is our own design (the user's pick, 2026-10-27: mid lane,
plan A 「统领·畸变体」):
  passive Dominator (统领): a shield of s_amt + s_ap% AP for s_t ticks each time he spawns (tft.dll: the data has no
          spawn hook; --plain lays it on at his first action); every cast of skill, skill2 or the ult climbs a ladder of
          permanent flags d1..d_max (magic_power_mult d_ap% a step), gone when he dies (the respawned hero is a new unit).
  attack  a Shimmer vial thrown at `Enemy` (towers too): 100% AD, a homing projectile released on a_rel.
  skill   Canister of Monstrosities (罐装畸变体, TFT's ability), `Targeting` on `EnemyWithoutTower` (q_range): a canister
          lobbed at the target (q_fall ticks) bursts for q_dmg + q_ratio% AP within q_r and lets out q_n monstrosities
          (tft.dll, below).
  skill2  Shimmer Shot (微光注射), `Targeting` on `EnemyChampion` (e_range, only in fights): the allied champion with the
          most attack within e_r of him (himself when none) gets e_as% attack speed and e_ms% move speed for e_t ticks,
          then the comedown takes e_cost% of his current health (tft.dll; never kills).
  ult     Chem-Baron's Flood (炼金狂潮), `Targeting` on `EnemyChampion` (r_range): a giant canister lobbed at the champion
          (warning ring r_warn r_fall ticks) bursts for r_dmg + r_ratio% AP within r_r, lets out r_n monstrosities and
          leaves a Shimmer fog of r_fog_r for r_fog_t ticks: enemies inside slowed r_slow% and burnt r_fog_dmg +
          r_fog_ratio% AP a second (tft.dll).

The monstrosities are tft.dll's (addons/tft/src/silco.rs; the data calls tft_silco:canister and tft_silco:flood on the
landing point): each pounces on an enemy near the canister (champions first, spread over different enemies), bites it
m_n times, one every m_gap ticks, for m_dmg + m_ratio% AP magic each; when its victim dies or gets away it leaps to the
nearest enemy within m_reach, and it melts after m_n bites or m_life ticks. They are pictures riding on their victim
(m_leap the pounce, m_bite_l / m_bite_r the gnawing, on its left or right side; m_die), like league_annie's Tibbers.
--plain builds the data alone for the classic-engine balance sims (they run no DLL code): the monstrosities are a
poison on the canister's target (all their bites on it), the fog a slow on the ult's burst, the shield at the first
action, the Shimmer Shot on himself and no comedown. A build of P checks silco.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_silco"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 55000 like every mid; radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips exist (tools/art/rig_silco.py). Numbers = the 10-min classic-SDK simulations (C:/t/sc_sim,
# Alune's copy of the balance sim: mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage,
# three lineups, both sides; 2026-10-27), all --plain: the draft (Q 40 + 30%, bites 8 + 6%, R 150 + 65%, E +40%, steps
# 8%, hp 860) -2.40 on seeds 1-8 (league_ziggs +1.17); Q 55 + 40%, bites 12 + 9%, R 180 + 80%, steps 10%, hp 900 -0.30;
# + bites 15 + 11%, E +50% +0.32; + Q 65 + 45% +1.25 / +1.22 (seeds 9-16; league_ziggs +2.22) = P; + shield 160 + 50%
# +1.50. tft.dll's rules are not simulated: the monstrosities bite the canister's target there, the fog is a slow.
P = {
    # stats (Magician base: attack 80 +6, ap 40 +20, hp 900 +100, def 20 +7, mr 20 +4, move 900 +9; TFT's Silco has
    # 800 health against Alune's 900)
    "hp": 900, "hp_g": 94, "atk": 72, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "a_rel": 10, "a_speed": 4000,
    # passive Dominator (TFT: a 350-800 shield for 15 s; 25-65% of the mana spent as stacking AP)
    "s_amt": 120, "s_ap": 40, "s_t": 900, "d_ap": 10, "d_max": 5,
    # Canister of Monstrosities (TFT: 140 / 200 / 1000 damage, 4 / 4 / 8 monstrosities of 5 attacks, 30-100 each)
    "q_cd": 300, "q_range": 65000, "q_dur": 36, "q_rel": 16, "q_fall": 24, "q_r": 20000, "q_dmg": 65, "q_ratio": 45,
    "q_n": 2,
    # the monstrosities (tft.dll)
    "m_n": 5, "m_gap": 45, "m_leap": 18, "m_dmg": 15, "m_ratio": 11, "m_reach": 45000, "m_life": 600,
    # Shimmer Shot
    "e_cd": 720, "e_range": 60000, "e_dur": 24, "e_rel": 10, "e_r": 50000, "e_as": 50, "e_ms": 20, "e_t": 240,
    "e_cost": 8,
    # Chem-Baron's Flood
    "r_cd": 3000, "r_range": 70000, "r_dur": 40, "r_rel": 24, "r_fall": 40, "r_r": 40000, "r_dmg": 180, "r_ratio": 80,
    "r_n": 4, "r_fog_r": 40000, "r_fog_t": 240, "r_slow": 30, "r_fog_dmg": 6, "r_fog_ratio": 4,
}
# what tft.dll reads from passive.params (addons/tft/src/silco.rs)
NATIVE_KEYS = ("s_amt", "s_ap", "s_t", "q_n", "m_n", "m_gap", "m_leap", "m_dmg", "m_ratio", "m_reach", "m_life",
               "e_r", "e_as", "e_ms", "e_t", "e_cost", "r_n", "r_fog_r", "r_fog_t", "r_slow", "r_fog_dmg",
               "r_fog_ratio")


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


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def poison(duration, period, effects):
    return {"type": "AddCasted", "casted_type": "Poison", "duration": duration, "period": period,
            "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower", seen="", applied=()):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point; `seen` = the
    picture played on the landing point the whole flight; `applied` run on the target it was thrown at."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [T(e) for e in applied], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ passive Dominator: one step a cast
    def dominate():
        # d1..d_max, the top asked first: held -> nothing more; step k held -> k + 1; none held -> the first
        chain = flag("d1", None, magic_power_mult=p["d_ap"])
        for k in range(1, p["d_max"]):
            up = combine(unflag(f"d{k}"), flag(f"d{k + 1}", None, magic_power_mult=p["d_ap"] * (k + 1)))
            chain = when(f"d{k}", up, chain)
        return when(f"d{p['d_max']}", combine(), chain)

    # --plain: the shield at his first action (no spawn hook in the data); tft.dll gives it at every spawn
    first = None if is_native else when("s_on", combine(), combine(flag("s_on", None),
                                                                    shield(p["s_amt"], p["s_ap"], p["s_t"])))

    # ------------------------------------------------------------------ attack: a Shimmer vial
    hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(first, delayed(p["a_rel"] - 1, sfx("a"), homing("a_vial", "Enemy", hit, p["a_speed"]))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Canister of Monstrosities
    bites = p["m_n"] * p["m_gap"]
    burst = [sfx("q_hit"), view("q_burst"), zone("q_zone", p["q_r"], [ap(p["q_dmg"], p["q_ratio"])])]
    if is_native:
        can = lob("q_can", p["q_fall"], burst + [native("canister")], seen="q_warn")
    else:   # every bite of the q_n monstrosities on the canister's target
        can = lob("q_can", p["q_fall"], burst, seen="q_warn",
                  applied=[poison(bites, p["m_gap"], [ap(p["m_dmg"] * p["q_n"], p["m_ratio"] * p["q_n"])])])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, sfx("q"), delayed(p["q_rel"] - 1, can, dominate())))

    # ------------------------------------------------------------------ skill2: Shimmer Shot
    if is_native:
        dose = native("inject")
    else:
        dose = combine(flag("e_shimmer", p["e_t"], attack_speed_mult=p["e_as"], move_speed_mult=p["e_ms"]))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(first, delayed(p["e_rel"] - 1, sfx("e"), dose, dominate())))

    # ------------------------------------------------------------------ ult: Chem-Baron's Flood
    rburst = [sfx("r_hit"), view("r_burst"), zone("r_zone", p["r_r"], [ap(p["r_dmg"], p["r_ratio"])])]
    if is_native:
        big = lob("r_can", p["r_fall"], rburst + [native("flood")], target="EnemyChampion", seen="r_warn")
    else:
        fog = p["r_fog_t"] // 60 * p["r_fog_dmg"], p["r_fog_t"] // 60 * p["r_fog_ratio"]
        big = lob("r_can", p["r_fall"], rburst, target="EnemyChampion", seen="r_warn",
                  applied=[poison(bites, p["m_gap"], [ap(p["m_dmg"] * p["r_n"] + fog[0] // p["m_n"],
                                                         p["m_ratio"] * p["r_n"] + fog[1] // p["m_n"])]),
                           buff("r_slow", p["r_fog_t"], move_speed_mult=-p["r_slow"])])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, sfx("r"), delayed(p["r_rel"] - 1, big, dominate())))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                            "tag": tag or name, "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the canisters fly as pictures turned with their flight; q_warn / r_warn mark the landing spot on the ground under
    # the units (z -2) the whole flight; the bursts over them. tft.dll plays the monstrosities (m_*, riding their victim),
    # the fog (r_fog, a ground loop it replays), the Shimmer Shot's dose and comedown on the ally (e_dose, e_crash)
    views_p = [B_("a_vial"), B_("q_can"), B_("r_can", BIG)]
    views_e = [E("a_hit"), E("q_warn", FX, -2, False), E("q_burst", BIG, 3, False), E("r_warn", BIG, -2, False),
               E("r_burst", BIG, 3, False)]
    if is_native:
        views_e += [E("m_leap"), E("m_bite_l", FX, 3, True, "m_bite"), E("m_bite_r", FX, 3, True),
                    E("m_die", FX, 2, False), E("r_fog", BIG, -2, False), E("e_dose"), E("e_crash")]
    views_b = [B_("e_shimmer", FX, 3), B_("p_shield", FX, 3), B_(f"d{p['d_max']}", FX, 4, "p_dom"),
               B_("r_slow", FX, 3)]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "Shield"],
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
    if is_native:   # tft.dll (addons/tft/src/silco.rs): the monstrosities, the spawn shield, the dose, the fog
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:baron", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/silco.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every name it plays or puts on (`sc("...")`) is the kit's, and every Native the kit calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "silco.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"silco.rs Params::default() differs from P (silco.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'sc\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"silco.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_silco:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects silco.rs does not register: {sorted(called - registered)}")


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
