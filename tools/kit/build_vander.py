"""Build tft_vander.data_champion (the tft pack's eighth hero: Vander, jungle, Melee) from the parameters P.

    python tools/kit/build_vander.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Vander is the old Zaun brawler from Arcane, Vi and Powder's adoptive father, with the great red-and-brass gauntlet, a
2-cost of Teamfight Tactics set 13 (TFT13_Prime, Family / Watcher, range 1, 800 health, 0/50 mana). TFT gives him one
ability (The Hound of the Underground / 地下猎犬: he stops attacking and holds a defensive stance 2.5 s that taunts,
with bonus armour and magic resist; his next attack is replaced by a strike of 400% AD, +100% AD for each 1-2 cost
ally; the HERO version stuns 0.75 s and splashes 35%) and the Watcher trait (damage reduction, higher above 50%
health). The rest is our own design (the user's pick, 2026-10-27: jungle, plan A 「监察·地下猎犬」):
  passive Watcher (监察): he takes p_lo% less damage, p_hi% while his health is above p_line% (tft.dll: the data reads
          no health; --plain lays a flat p_plain% on at his first action).
  attack  a gauntlet punch on `Enemy` (towers too): 100% AD on atk_st. With `q_ready` on (Q's strike waiting) the
          punch is the heavy strike instead: q_dmg + q_ad% AD, and tft.dll adds q_fam% AD for each Family ally on his
          team (tft_powder, league_vi, league_jinx: TFT's bonus per cheap ally, made his family's).
  skill   The Hound of the Underground (地下猎犬), `Targeting` on `EnemyWithoutTower` (q_range, camps too): he drops into
          the guard: every enemy within q_r is taunted q_taunt ticks, he gets q_def armour and q_mr magic resist for
          q_t ticks, and his next punch within q_wait ticks is the heavy strike.
  skill2  Iron Fist (铁拳突进), `Targeting` on `EnemyWithoutTower` (e_range): he rushes onto the target
          (`MoveToTarget` e_speed, coiled) and on arrival uppercuts it (`CasterAnimation` upper, e_up_t ticks):
          e_dmg + e_ad% AD and an e_stun-tick stun; every enemy within e_sr round him (the target too) takes
          e_splash% of the blow (a RangeEffect centres on the caster only).
  ult     Last Stand on the Bridge (桥头死守), `Targeting` on `EnemyChampion` (r_range): he springs at the target
          (`MoveToTarget` r_speed, in the air) and on landing slams the gauntlet into the ground
          (`CasterAnimation` slam, r_slam_t ticks): every enemy within r_r takes
          r_dmg + r_ad% AD and is thrown up r_up ticks; for r_t ticks he takes r_red% less damage, and tft.dll adds
          r_per% for each enemy champion within r_r at the slam (up to r_cap of them).

tft.dll (addons/tft/src/vander.rs): the Watcher's reduction by health (passive tft_vander:watcher), the Family bonus
of the strike (tft_vander:family) and the stand's reduction by the enemies round him (tft_vander:stand). A build of P
checks vander.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_vander"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's jungle bruisers (league_warwick, league_vi, league_sett); radii count the
# unit's collision radius (~15000) on top. Timings are placeholders until the strips exist (tools/art/rig_vander.py).
# Stats start from league_warwick's / league_sett's (hp 1100-1120 +105-110, def 34-36, mr 25-26, atk 90-92 +18); TFT's
# Vander: 800 health, 55 attack, 45 armour / 45 magic resist (a tank: more health and armour, less attack).
# Numbers = the 10-min classic-SDK simulations (C:/t/vd_sim, Alune's copy of the balance sim: jungle lane against the
# base ninja, demon, hunter, werewolf and vampire, three lineups, both sides; 2026-10-27), all --plain: the draft (hp
# 1180, atk 84, Q every 8 s taunting 1.5 s round 34000, strike 60 + 180%) +8.18 on seeds 1-8 against league_warwick
# +0.57 and league_vi +2.08: the taunt round him every Q carried the fights (taunt cut to 0.75 s in 26000 +5.40; taunt
# off +4.88). Taunt 45 / 26000, Q every 10 s, strike 40 + 140%, E 90% and stun 0.5 s, hp 1080 +105, atk 78 +14, def 34,
# mr 26, stand 15% = P: +2.15 / +1.07 (seeds 9-16; league_vi +1.99, league_warwick +0.52). tft.dll's Watcher by health,
# the Family strike and the stand's count are not simulated (the plain Watcher is a flat p_plain%).
P = {
    # stats (Melee, jungle)
    "hp": 1080, "hp_g": 105, "atk": 78, "atk_g": 14, "apw": 0, "apw_g": 0, "def": 34, "def_g": 8, "mr": 26, "mr_g": 4,
    "ms": 1030, "ms_g": 11,
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 64, "atk_st": 12,
    # passive Watcher (TFT 2 Watchers: 15%, 30% above half health)
    "p_lo": 10, "p_hi": 20, "p_line": 50, "p_plain": 15,
    # The Hound of the Underground (TFT: stance 2.5 s, +90 resists, strike 400% AD (+100% per cheap ally))
    "q_cd": 600, "q_range": 30000, "q_dur": 30, "q_r": 26000, "q_taunt": 45, "q_def": 40, "q_mr": 30, "q_t": 150,
    "q_wait": 300, "q_dmg": 40, "q_ad": 140, "q_fam": 40,
    # Iron Fist (TFT HERO: stun 0.75 s, 35% splash)
    "e_cd": 600, "e_range": 45000, "e_dur": 26, "e_speed": 5000, "e_dmg": 50, "e_ad": 90, "e_stun": 30,
    "e_sr": 22000, "e_splash": 35, "e_up_t": 18,
    # Last Stand on the Bridge
    "r_cd": 3000, "r_range": 50000, "r_dur": 40, "r_speed": 4000, "r_r": 34000, "r_dmg": 150, "r_ad": 150, "r_up": 60,
    "r_red": 15, "r_per": 8, "r_cap": 4, "r_t": 240, "r_slam_t": 18,
}
# what tft.dll reads from passive.params (addons/tft/src/vander.rs)
NATIVE_KEYS = ("p_lo", "p_hi", "p_line", "q_fam", "r_r", "r_red", "r_per", "r_cap", "r_t")


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


def around(radius, target, effects, at="AroundCaster"):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": at,
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain: the Watcher's reduction at his first action (no health in the data); tft.dll sets it by his health
    first = None if is_native else when("p_on", combine(), combine(
        flag("p_on", None), flag("p_watch", None, damaged_reduce=p["p_plain"])))

    # ------------------------------------------------------------------ attack: a gauntlet punch / Q's heavy strike
    strike = combine(unflag("q_ready"), sfx("q_hit"), attack(p["q_dmg"], p["q_ad"]),
                     native("family") if is_native else None, view("q_hit"))
    punch = combine(attack(0, 100), view("a_hit"), tsfx("a_hit"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(first, sfx("a"), delayed(p["atk_st"] - 1, when("q_ready", strike, punch))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: The Hound of the Underground
    taunted = [{"type": "Taunt", "duration": p["q_taunt"]}, buff("q_taunt", p["q_taunt"])]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, sfx("q"), sfx("q_buff"), cview("q_guard_in"),
                           flag("q_guard", p["q_t"], defence=p["q_def"], magic_resistance=p["q_mr"]),
                           flag("q_ready", p["q_wait"]),
                           around(p["q_r"], "EnemyWithoutTower", taunted)))

    # ------------------------------------------------------------------ skill2: Iron Fist
    splash = around(p["e_sr"], "EnemyWithoutTower",
                    [attack(p["e_dmg"] * p["e_splash"] // 100, p["e_ad"] * p["e_splash"] // 100)])
    uppercut = [anim("upper", p["e_up_t"]), sfx("e_hit"), attack(p["e_dmg"], p["e_ad"]), {"type": "Stun", "duration": p["e_stun"]},
                buff("e_stun", p["e_stun"]), view("e_hit"), splash]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(first, sfx("e"), cview("e_dash"),
                            {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 40000,
                             "end_effects": uppercut}))

    # ------------------------------------------------------------------ ult: Last Stand on the Bridge
    struck = [attack(p["r_dmg"], p["r_ad"]), {"type": "Airborne", "duration": p["r_up"]}, view("r_hit")]
    hold = native("stand") if is_native else on_me(flag("r_hold", p["r_t"], damaged_reduce=p["r_red"]))
    slam = [anim("slam", p["r_slam_t"]), sfx("r_slam"), cview("r_slam"), around(p["r_r"], "EnemyWithoutTower", struck), hold]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, sfx("r"), sfx("r_jump"),
                         {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 40000,
                          "end_effects": slam}))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the slam's shockwave lies on the ground round him (z -1), drawn round so it reads the same on both sides; the
    # rush's dust (e_dash) is left where he started
    views_e = [E("a_hit"), E("q_guard_in", FX, 3), E("q_hit"), E("e_dash", FX, 1, False), E("e_hit"),
               E("r_slam", BIG, -1, False), E("r_hit")]
    views_b = [B_("q_guard", FX, 3), B_("q_ready", FX, 3), B_("q_taunt", FX, 4), B_("e_stun", FX, 3),
               B_("r_hold", FX, 3), B_("p_watch", FX, 1)]
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
    if is_native:   # tft.dll (addons/tft/src/vander.rs): the Watcher by health, the Family strike, the stand
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:watcher", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Last Stand as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, so his stolen stand cannot call tft.dll (Silco's and Maddie's
    way). The kit's --plain ult - the leap, the slam's shockwave and knock-up, the flat r_red% stand - without the
    Watcher flag the plain kit lays on at a first action (that is Vander's passive, not the ult's). The views are the
    kit's own (tft_vander_*); make_override copies them and their sheets."""
    p = dict(P) if p is None else p
    eff = build(p, False)["ult"]["effect"]
    eff["effects"] = [e for e in eff["effects"] if not (e.get("type") == "SwitchByBuff" and e.get("buff_name") == n("p_on"))]
    return eff


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
    """addons/tft/src/vander.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`va("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "vander.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"vander.rs Params::default() differs from P (vander.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'va\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"vander.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_vander:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects vander.rs does not register: {sorted(called - registered)}")


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
