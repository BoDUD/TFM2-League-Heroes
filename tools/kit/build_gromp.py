"""Build tft_gromp.data_champion (a tft pack hero: Gromp, bottom lane, Range) from the parameters P.

    python tools/kit/build_gromp.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Gromp (魔沼蛙; en Gromp) is Teamfight Tactics set 18's 2-cost Rift Monster / Adaptor (DA_Gromp18_AP, range 4, 550
health, 30 AD, 0.70 attack speed, 30 armour and magic resistance, 0/45 mana): Belchy Bubble / 打嗝泡泡 - a noxious
bubble at the current target that explodes on the first enemy hit (magic), enemies within 1 hex of the explosion
poisoned (magic over a few seconds); as an AD Adaptor it heavily slows the target instead; Purple Buff: every few
seconds it gains Ability Power. The kit is our own design from that (the user's pick, 2026-11-01: bottom lane, plan A
「打嗝泡泡」):
  passive Purple Buff (紫霸符): while an enemy champion is within p_near, every p_every ticks one more stack of p_ap
          magic power, up to p_max, each p_t ticks long and refreshed by the next (`tft_gromp:purple`, tft.dll: the
          engine's stacked buff with a cap; --plain: p_plain stacks as plain magic power).
  attack  Toxic Spit (毒涎吐射) on `Enemy` (towers too): a homing glob of spit, 100% AD + a_ap% AP magic.
  skill   Belchy Bubble (打嗝泡泡, TFT's), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): its belly
          swells and it belches a bubble straight at the target (q_len long, stopping at the first enemy it meets):
          that one takes q_dmg + q_ratio% AP magic, and the bubble bursts there: every enemy within q_r is poisoned
          for q_t ticks (q_dot + q_dratio% AP magic in all, every q_p ticks). A miss bursts nowhere (the end only
          runs on the flag the hit raises).
  skill2  Slime Swamp (黏液沼泽, TFT's AD-form slow), `Position` on `EnemyChampion` (e_range): it spits a glob of slime
          that lands e_travel ticks later and lies e_t ticks in e_r: every e_p ticks e_dmg + e_ratio% AP magic and an
          e_slow% slow for e_hold ticks.
  ult     Swamp Belch (毒沼大嗝), `Position` on `EnemyChampion` (r_range, only in fights): it rears up, the belly swelling
          to its biggest (the flag r_big for r_grow ticks: drawn bigger by league.dll's hd::FORMS, r_dr% less damage
          taken), and belches a cone of poison (r_len, r_cos): r_dmg + r_ratio% AP magic and an r_slow% slow for
          r_hold ticks; the cloud stays on the aimed spot r_t ticks in r_r: every r_p ticks r_fdmg + r_fratio% AP magic.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/gromp.rs; the passive is
tft_gromp:purple, params NATIVE_KEYS): no data passive counts time, and a data buff has no stack cap. A build of P
checks gromp.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_gromp"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 60000 like the pack's bottoms (tft_daeja, tft_raptor); radii count the unit's collision radius
# (~15000) on top. Timings are placeholders until the strips are rigged (tools/art/rig_gromp.py).
# Stats from the Range base (attack 100 +20, hp 900 +90, def 20 +7, mr 15 +3, move 900 +9), less attack and more magic
# power: an AP carry like tft_daeja.
P = {
    # stats (Range, an AP carry)
    "hp": 820, "hp_g": 85, "atk": 70, "atk_g": 12, "apw": 30, "apw_g": 16, "def": 20, "def_g": 7, "mr": 18, "mr_g": 3,
    "ms": 900, "ms_g": 9,
    "atk_range": 60000, "atk_dur": 24, "atk_cd": 72, "a_rel": 8, "a_speed": 5000, "a_y": 2000, "a_ap": 25,
    # passive Purple Buff (TFT: every few seconds, Ability Power)
    "p_every": 240, "p_ap": 8, "p_max": 8, "p_t": 600, "p_near": 90000, "p_plain": 3,
    # Belchy Bubble (TFT: magic on the first enemy hit, 1-hex poison round it)
    "q_cd": 360, "q_range": 65000, "q_dur": 30, "q_rel": 14, "q_len": 80000, "q_w": 5000, "q_speed": 5000,
    "q_dmg": 90, "q_ratio": 70, "q_r": 25000, "q_t": 180, "q_p": 30, "q_dot": 60, "q_dratio": 45,
    # Slime Swamp (TFT's AD form: heavily slows)
    "e_cd": 600, "e_range": 60000, "e_dur": 24, "e_rel": 8, "e_travel": 14, "e_r": 26000, "e_t": 240, "e_p": 15,
    "e_dmg": 4, "e_ratio": 3, "e_slow": 45, "e_hold": 20, "e_show": 15,
    # Swamp Belch
    "r_cd": 2700, "r_range": 60000, "r_dur": 36, "r_rel": 18, "r_grow": 300, "r_dr": 20, "r_len": 55000, "r_cos": 600,
    "r_dmg": 140, "r_ratio": 70, "r_slow": 35, "r_hold": 90, "r_travel": 10, "r_r": 32000, "r_t": 240, "r_p": 20,
    "r_fdmg": 8, "r_fratio": 5, "r_show": 15,
}
# what tft.dll reads from passive.params (addons/tft/src/gromp.rs)
NATIVE_KEYS = ("p_every", "p_ap", "p_max", "p_t", "p_near")
# names gromp.rs uses that need no view: sounds (the death cry, Purple Buff filling up)
NATIVE_ONLY = {"d", "p"}


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


NONE = combine()


def sw(name, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def poison(total, ratio, tick, period):
    """Magic over `tick` ticks, every `period`: total + ratio% AP in all."""
    runs = max(1, tick // period)
    return {"type": "AddCasted", "casted_type": "Poison", "duration": tick, "period": period,
            "effects": [ap(round(total / runs), round(ratio / runs))]}


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, effects, end=()):
    """A non-penetrating skillshot: stops at the first unit it meets; `end` runs where it stopped."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": False, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A ParabolicProjectile: lands where its target point was when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 0, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def cone(radius, target, effects, cos):
    """A cone in front of it toward the action's target point (league_darius E / league_cassiopeia R)."""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: the spit
    spit = [attack(0, 100), ap(0, p["a_ap"]), view("a_hit"), tsfx("a_hit")]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_spit", "Enemy", spit, p["a_speed"], p["a_y"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Belchy Bubble
    # the first enemy met takes the hit and raises q_pop on it; the end (where the bubble stopped) bursts only then
    struck = [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), {"type": "AddCasterBuff", "only_to_enemy": False,
                                                              "buff_state": {"name": n("q_pop"),
                                                                             "duration": {"Time": {"tick": 2}}}}]
    sick = [poison(p["q_dot"], p["q_dratio"], p["q_t"], p["q_p"]), buff("q_poison", p["q_t"])]
    burst = sw("q_pop", combine(*rm("q_pop"), view("q_burst"), sfx("q_hit"), zone("q_cloud", p["q_r"], sick)))
    bubble = line("q_bubble", p["q_speed"], p["q_len"], p["q_w"], p["a_y"], "EnemyWithoutTower", struck, [burst])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q_vo"), delayed(p["q_rel"] - 1, sfx("q"), bubble)))

    # ------------------------------------------------------------------ skill2: Slime Swamp
    stuck = [ap(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_hold"], move_speed_mult=-p["e_slow"])]
    land = [view("e_land"), sfx("e_hit"), field("e_pool", p["e_r"], p["e_t"], p["e_p"], stuck),
            delayed(4, sfx("e_slow"))]
    lying = [delayed(k, view("e_pool")) for k in range(0, p["e_t"], p["e_show"])]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Position", "EnemyChampion",
                    combine(sfx("e_vo"), delayed(p["e_rel"] - 1, sfx("e"), lob("e_glob", p["e_travel"], land)),
                            delayed(p["e_rel"] - 1 + p["e_travel"], *lying)))

    # ------------------------------------------------------------------ ult: Swamp Belch
    blast = [ap(p["r_dmg"], p["r_ratio"]), buff("r_slow", p["r_hold"], move_speed_mult=-p["r_slow"]), view("r_hit"),
             tsfx("r_tick")]
    fog = [ap(p["r_fdmg"], p["r_fratio"])]
    fogs = [delayed(k, view("r_fog")) for k in range(0, p["r_t"], p["r_show"])]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Position", "EnemyChampion",
                 combine(sfx("r"), sfx("r_vo"), flag("r_big", p["r_grow"], damaged_reduce=p["r_dr"]),
                         delayed(p["r_rel"] - 1, cview("r_cast"), sfx("r_cloud"),
                                 cone(p["r_len"], "EnemyWithoutTower", blast, p["r_cos"]),
                                 lob("r_drop", p["r_travel"], [field("r_cloud", p["r_r"], p["r_t"], p["r_p"], fog)])),
                         delayed(p["r_rel"] - 1 + p["r_travel"], *fogs)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # a_spit / q_bubble / e_glob fly laid along their flight, top-bottom symmetric (turned with it); the hits are
    # ViewEffects on the struck (never mirrored: left-right symmetric); q_burst / e_land / e_pool / r_fog on the ground
    # where they burst or lie (not following); r_cast the belch at its mouth (a caster picture, never mirrored: drawn
    # symmetric); p_ap the purple rune on it while Purple Buff holds, q_poison the bubbles on the poisoned, e_slow /
    # r_slow the slime on the slowed
    views_p = [B_("a_spit"), B_("q_bubble"), B_("e_glob")]
    views_e = [E("a_hit"), E("q_hit"), E("q_burst", BIG, 2, False), E("e_land", BIG, -1, False),
               E("e_pool", BIG, -2, False), E("r_cast", BIG, 3), E("r_hit"), E("r_fog", BIG, 3, False)]
    views_b = [B_("p_ap", FX, 3), B_("q_poison", FX, 3), B_("e_slow", FX, 3), B_("r_slow", FX, 3)]
    stat_apw = p["apw"] + (0 if is_native else p["p_ap"] * p["p_plain"])
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "AP", "Magic", "Range"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": stat_apw, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/gromp.rs): Purple Buff's timed, capped stacks
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:purple", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/gromp.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`gp("...")`) is the kit's or NATIVE_ONLY, and every Native the kit
    calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "gromp.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"gromp.rs Params::default() differs from P (gromp.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'gp\("(\w+)"\)', src))
    have = names(build(p, False)) | names(kit) | {n(x) for x in NATIVE_ONLY}
    missing = sorted(x for x in read if n(x) not in have)
    if not read or missing:
        raise SystemExit(f"gromp.rs plays names the kit does not have: {missing}")
    called = set(re.findall(r'"(?:effect_ref|passive_ref)": "tft_gromp:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native code gromp.rs does not register: {sorted(called - registered)}")


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
