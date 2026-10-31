"""Build tft_meepsie.data_champion (a tft pack hero: Meepsie, support, Util) from the parameters P.

    python tools/kit/build_meepsie.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Meepsie (小木灵; the user called it 米普西 and picked the official name) is Teamfight Tactics set 17's 2-cost Meeple /
Shepherd / Voyager (TFT17_IvernMinion, an AP fighter, range 1, 950 health, 45 armour and magic resistance, 0/55 mana): a
moon-rock golem piloted by a little green meep in a crater cockpit on its chest. TFT gives it one ability, The Big Bang /
宇宙大爆炸 - passive: attacks deal bonus magic damage; active: it leaps to the largest group of enemies within 2 hexes
and slams, magic damage in 3 hexes, 35% less for each hex from the centre, the closest 3 enemies knocked up 1-1.5 s. The
rest is our own design (the user's pick, 2026-11-01: support lane, plan A 「木灵守护」):
  passive Meep Pilot (木灵驾驶员): every punch deals p_dmg + p_ap% AP bonus magic damage (the data, on the attack's hit).
  attack  Moon-Rock Punch (月岩重拳) on `Enemy` (towers too): 100% AD on atk_st.
  skill   Moon-Dust Quake (月尘震地), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too): it punches the
          ground ahead at q_st: every enemy in the cone ahead (`DirDot` q_r, q_cone) takes q_dmg + q_ap% AP magic damage
          and is q_slow% slower for q_slow_t ticks.
  skill2  Healing Meeps (治疗木灵), `None` on `EnemyChampion` (e_range, only in fights): at e_st the pilot waves and a
          meep flies to each of the e_n allied champions within e_r with the lowest health share (the others first,
          itself with a slot left): each heals e_hot + e_hot_ap% AP every e_every ticks for e_t (tft.dll's
          `tft_meepsie:meeps`). --plain: every ally within e_r and itself get the same heals.
  ult     The Big Bang (宇宙大爆炸, TFT's), `Targeting` on `EnemyChampion` (r_range): it leaps (r_air ticks) to the spot
          within r_leap with the most enemy champions within r_r and slams: every enemy within r_r takes r_dmg + r_ap% AP
          magic damage, r_fall% less for every r_hex out; the r_n enemy champions nearest the centre are knocked up r_up
          ticks (tft.dll's `tft_meepsie:bigbang`). --plain: it leaps at its target (MoveToTarget) and every enemy
          within r_r takes the full damage, every enemy champion knocked up.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/meepsie.rs; the passive is tft_meepsie:pilot,
params NATIVE_KEYS): the data reads no health, so it cannot pick who needs the meeps, nor a landing spot by who stands
round it, nor scale damage by distance or knock up only the nearest. A build of P checks meepsie.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_meepsie"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's tank supports (tft_idas, tft_steb, league_braum); radii count the unit's
# collision radius (~15000) on top; a TFT hex ~15000 (r_hex). Timings are placeholders until the strips are rigged
# (tools/art/rig_meepsie.py). Stats start from tft_idas's (hp 1250 +120, atk 72, apw 35 +16, def 42, mr 36): the 2-cost
# golem, slow and heavy, TFT's even armour and resistance.
P = {
    # stats (Util, the tank supports)
    "hp": 1250, "hp_g": 118, "atk": 66, "atk_g": 6, "apw": 30, "apw_g": 15, "def": 44, "def_g": 8, "mr": 40, "mr_g": 6,
    "ms": 940, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 90, "atk_st": 15,
    # passive Meep Pilot (TFT: attacks deal bonus magic damage)
    "p_dmg": 15, "p_ap": 25,
    # Moon-Dust Quake
    "q_cd": 360, "q_range": 30000, "q_dur": 36, "q_st": 18, "q_r": 65000, "q_cone": 700, "q_len": 70000, "q_w": 12000,
    "q_dmg": 90, "q_ap": 70, "q_slow": 40, "q_slow_t": 120,
    # Healing Meeps (tft.dll; --plain: everyone within e_r)
    "e_cd": 540, "e_range": 60000, "e_dur": 30, "e_st": 14, "e_r": 60000, "e_n": 4, "e_speed": 2500, "e_t": 180,
    "e_every": 30, "e_hot": 20, "e_hot_ap": 10,
    # The Big Bang (TFT: 2 hexes, 3-hex slam, -35% a hex, 3 knocked up 1-1.5 s)
    "r_cd": 2400, "r_range": 45000, "r_dur": 54, "r_leap": 45000, "r_air": 30, "r_speed": 2000, "r_r": 45000,
    "r_hex": 15000, "r_fall": 35, "r_dmg": 160, "r_ap": 90, "r_n": 3, "r_up": 75,
}
# what tft.dll reads from passive.params (addons/tft/src/meepsie.rs)
NATIVE_KEYS = ("e_r", "e_n", "e_speed", "e_t", "e_every", "e_hot", "e_hot_ap", "r_leap", "r_air", "r_r", "r_hex",
               "r_fall", "r_dmg", "r_ap", "r_n", "r_up")
# names meepsie.rs uses that need no view: sounds (the meeps flying, the heal, coming down, the slam, the fall)
NATIVE_ONLY = {"e_fly", "e_heal", "r_into", "r_hit", "d"}


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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def heal(amount, ratio, kind="Caster"):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": kind}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": [e for e in effects if e is not None]}


def on_me(*effects):
    """Effects on it alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def line(name, length, width, target, effects, delay=1):
    """A line from it through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it); on
    `Ally` with no effects it is a picture only (build_idas.py's breath)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: the punch + the pilot's zap
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), magic(p["p_dmg"], p["p_ap"]),
                                                view("a_hit"), tsfx("a_hit"), tsfx("p"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Moon-Dust Quake
    cone = {"DirDot": {"radius": p["q_r"], "range": p["q_cone"]}}
    shaken = [magic(p["q_dmg"], p["q_ap"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
              view("q_hit"), tsfx("q_slow")]
    # the dust wave's picture rides a picture-only line from its fist (top-bottom symmetric, turned with the cast)
    quake = combine(sfx("q_hit"), line("q_wave", p["q_len"], p["q_w"], "Ally", []),
                    around(0, "EnemyWithoutTower", shaken, {"Forward": {"offset": 1000}}, cone))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), delayed(p["q_st"] - 1, quake)))

    # ------------------------------------------------------------------ skill2: Healing Meeps
    if is_native:   # tft.dll: one meep to each of the e_n allies in most need
        meeps = native("meeps")
    else:           # --plain: everyone within e_r and itself, the same heals
        mend = lambda: combine(on_me(heal(p["e_hot"], p["e_hot_ap"])),
                               around(p["e_r"], "AllyNotSelf", [heal(p["e_hot"], p["e_hot_ap"], "Ally")]))
        meeps = combine(on_me(buff("e_hot", p["e_t"])), around(p["e_r"], "AllyNotSelf", [buff("e_hot", p["e_t"])]),
                        *[delayed(k * p["e_every"] - 1, mend()) for k in range(1, p["e_t"] // p["e_every"] + 1)])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "None", "EnemyChampion",
                    combine(sfx("e_vo"), delayed(p["e_st"] - 1, sfx("e"), cview("e_cast"), meeps)))

    # ------------------------------------------------------------------ ult: The Big Bang
    if is_native:   # tft.dll: the landing spot, the leap, the falloff, the nearest knocked up
        bang = native("bigbang")
    else:
        struck = [magic(p["r_dmg"], p["r_ap"]), {"type": "Airborne", "duration": p["r_up"]}]
        land = [sfx("r_hit"), cview("r_slam"), around(p["r_r"], "EnemyWithoutTower", struck)]
        bang = {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 40000, "end_effects": land}
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r_vo"), sfx("r"), bang))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # q_wave is a level dust wave along the cast line, top-bottom symmetric; e_cast (the pilot's wave, the meeps popping
    # out) rides on it, left-right symmetric (the client never mirrors a picture); r_slam lies on the ground where it
    # lands (not following); e_meep a meep curled into a glowing ball, the same every way it flies
    views_p = [B_("q_wave", BIG), B_("e_meep", FX, 3)]
    views_e = [E("a_hit"), E("q_hit", FX, 3), E("e_cast", BIG, 3), E("r_slam", BIG, -1, False), E("r_up", FX, 3)]
    views_b = [B_("q_slow", FX, 3), B_("e_hot", FX, 3)]
    kit = {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "Heal", "CC"],
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
    if is_native:   # tft.dll (addons/tft/src/meepsie.rs): the meeps, the Big Bang, the death cry
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:pilot", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """The Big Bang as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll (the user, 2026-10-27:
    「塞拉斯的大招什么一定要能偷到特效版本的」). The kit's --plain ult: the leap at his target, the slam's picture, the
    damage and the knock-up round it. The views are the kit's own (tft_meepsie_*); make_override copies them and their
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
    """addons/tft/src/meepsie.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays or puts on (`mp("...")`) is the kit's, and every Native the kit calls it
    registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "meepsie.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"meepsie.rs Params::default() differs from P (meepsie.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'\bmp\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"meepsie.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"(?:effect_ref|passive_ref)": "tft_meepsie:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native code meepsie.rs does not register: {sorted(called - registered)}")


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
