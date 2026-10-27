"""Build tft_loris.data_champion (the tft pack's sixth hero: Loris, support, Util) from the parameters P.

    python tools/kit/build_loris.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Loris is the bearded Piltover enforcer with the great tower shield from Arcane, a 3-cost of Teamfight Tactics set 16
(TFT16_Loris, Piltover / Warden, range 1, 950 health, 70/140 mana). TFT gives him one ability (Piltover Brawl / 皮城争斗:
a shield for 4 s, a charge at the target that knocks it back, 1.25 s stun and magic damage to it and the units hit, then
nearby enemies are made to attack him) and the Warden trait (a shield of a share of his health when he first falls to
75% and to 25%). The rest is our own design (the user's pick, 2026-10-27: support lane, plan A 「神盾使·皮城争斗」; TFT's
ability split into the charge (Q) and the taunt (R), E the support's guard):
  passive Warden (神盾使): the first time each life his health falls under p_hi% and under p_lo% he gets a shield of
          p_pct% of his maximum health for p_t ticks (tft.dll: the data reads no health; --plain lays a flat p_plain
          shield on at his first action).
  attack  a shield bash on `Enemy` (towers too): 100% AD on atk_st.
  skill   Piltover Brawl (皮城争斗), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): a shield of q_sh +
          q_sh_ap% AP for q_sh_t ticks, then on q_go he charges behind the raised shield (`RushTime`, q_speed x q_t,
          penetrate): every enemy he runs through takes q_dmg + q_ap% AP magic, is knocked back (q_kb_speed x q_kb_t)
          and stunned q_stun ticks.
  skill2  Bulwark (盾卫), `None` on `EnemyChampion` (e_range, only in fights): he leaps to the allied champion with the
          lowest share of health within e_r (tft.dll: a step every tick at e_speed), both get a shield of e_sh +
          e_sh_ap% AP for e_t ticks, and for e_t ticks he takes e_share% of the damage meant for that ally (the ally
          takes e_share% less, he loses the same; never his last point). No ally in reach: the shield on him alone.
          --plain: a random allied champion within e_r (MoveToTarget), the ally's share a damaged_reduce buff.
  ult     Iron Line (钢铁防线), `Targeting` on `EnemyChampion` (r_range): he lifts the shield and on r_at slams it into the
          ground: every enemy within r_r takes r_dmg + r_ap% AP magic, is thrown up r_up ticks and taunted r_taunt
          ticks (they must attack him); he takes r_red% less damage for r_t ticks.

tft.dll (addons/tft/src/loris.rs): the Warden shields (passive tft_loris:warden), Bulwark's pick, leap and guard
(tft_loris:bulwark, tft_loris:leap; the share moved onto him by the passive every tick). A build of P checks loris.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_loris"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's tank supports (league_braum, league_alistar); radii count the unit's collision
# radius (~15000) on top. Timings are placeholders until the strips exist (tools/art/rig_loris.py). Stats start from
# league_braum's (hp 1300 +120, def 44, mr 28, atk 78); TFT's Loris: 950 health, 50 armour / 50 magic resistance.
# Numbers = the 10-min classic-SDK simulations (C:/t/lo_sim, Maddie's copy of the balance sim: support lane against the
# base priest, monk, bard, enchanter and taoist, three lineups, both sides; 2026-10-27), all --plain: the draft (Q 70 +
# 60%, knock-back 2500 x 6, charge 5000 x 8 at 45000, R 150 + 60%) -1.15 on seeds 1-8 (league_braum +1.52); more damage
# alone stayed at -1.2..-1.7: the knock-back pushed the enemies he charged out of his team's reach. Without it (and a
# charge as long as the cast range, stun 75) +0.33; a 2-square knock-back kept to show the hit (800 x 3) +0.22; + Q every
# 7 s, stun 1.5 s +0.45; + R every 50 s, r_r 36000, thrown up 1 s +1.40 / +0.86 (seeds 9-16; league_braum +1.25) = P.
# Taunt off: -1.85 (it is worth keeping). tft.dll's Warden shields and the Bulwark guard are not simulated.
P = {
    # stats (Util, the tank supports)
    "hp": 1250, "hp_g": 115, "atk": 74, "atk_g": 6, "apw": 30, "apw_g": 15, "def": 42, "def_g": 8, "mr": 30, "mr_g": 4,
    "ms": 980, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 84, "atk_st": 14,
    # passive Warden (TFT: 16-33% of max health at 75% and at 25%)
    "p_hi": 75, "p_lo": 25, "p_pct": 12, "p_t": 240, "p_plain": 150,
    # Piltover Brawl (TFT: a 700-1200 shield 4 s; 150-495 magic, stun 1.25 s)
    "q_cd": 420, "q_range": 42000, "q_dur": 30, "q_go": 8, "q_speed": 5000, "q_t": 10, "q_sh": 70, "q_sh_ap": 50,
    "q_sh_t": 240, "q_dmg": 110, "q_ap": 70, "q_kb_speed": 800, "q_kb_t": 3, "q_stun": 90,
    # Bulwark
    "e_cd": 600, "e_range": 50000, "e_dur": 24, "e_r": 70000, "e_speed": 4500, "e_sh": 70, "e_sh_ap": 45, "e_t": 240,
    "e_share": 30,
    # Iron Line (TFT's taunt after the charge)
    "r_cd": 3000, "r_range": 30000, "r_dur": 40, "r_at": 22, "r_r": 36000, "r_dmg": 220, "r_ap": 80, "r_up": 60,
    "r_taunt": 120, "r_red": 50, "r_t": 240,
}
# what tft.dll reads from passive.params (addons/tft/src/loris.rs)
NATIVE_KEYS = ("p_hi", "p_lo", "p_pct", "p_t", "e_r", "e_speed", "e_sh", "e_sh_ap", "e_t", "e_share")


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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain: the Warden shield at his first action (no health in the data); tft.dll gives it at 75% / 25%
    first = None if is_native else when("p_on", combine(), combine(flag("p_on", None),
                                                                    on_me(shield(p["p_plain"], 0, p["p_t"]))))

    # ------------------------------------------------------------------ attack: a shield bash
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(first, sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Piltover Brawl
    hit = [ap(p["q_dmg"], p["q_ap"]), {"type": "Knockback", "speed": p["q_kb_speed"], "tick": p["q_kb_t"]},
           {"type": "Stun", "duration": p["q_stun"]}, buff("q_stun", p["q_stun"]), view("q_hit"), tsfx("q_hit")]
    rush = {"type": "RushTime", "speed": p["q_speed"], "tick": p["q_t"], "range": 1000,
            "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": [T(e) for e in hit]}
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(first, sfx("q"), on_me(shield(p["q_sh"], p["q_sh_ap"], p["q_sh_t"])), cview("q_shield"),
                           delayed(p["q_go"] - 1, sfx("q_dash"), cview("q_dash"), rush)))

    # ------------------------------------------------------------------ skill2: Bulwark
    if is_native:   # tft.dll picks the hurt ally, leaps, shields both and moves the share onto him
        guard = combine(sfx("e"), native("bulwark"))
    else:
        landing = [shield(p["e_sh"], p["e_sh_ap"], p["e_t"]), buff("e_guard", p["e_t"], damaged_reduce=p["e_share"]),
                   view("e_land"), on_me(shield(p["e_sh"], p["e_sh_ap"], p["e_t"])), sfx("e_shield")]
        leap = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_r"] + 40000, "end_effects": landing}
        guard = combine(pick(p["e_r"], "AllyNotSelf", flag("e_go", 1)),
                        when("e_go", combine(unflag("e_go"), sfx("e"),
                                             pick(p["e_r"], "AllyNotSelf", leap)),
                             combine(on_me(shield(p["e_sh"], p["e_sh_ap"], p["e_t"])), sfx("e_shield"))))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "None", "EnemyChampion", combine(first, guard))

    # ------------------------------------------------------------------ ult: Iron Line
    struck = [ap(p["r_dmg"], p["r_ap"]), {"type": "Airborne", "duration": p["r_up"]},
              {"type": "Taunt", "duration": p["r_taunt"]}, buff("r_taunt", p["r_taunt"]), view("r_hit")]
    slam = combine(sfx("r_slam"), sfx("r_hit"), cview("r_slam"), around(p["r_r"], "EnemyWithoutTower", struck),
                   on_me(flag("r_wall", p["r_t"], damaged_reduce=p["r_red"])))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(first, sfx("r"), sfx("vo"), delayed(p["r_at"] - 1, slam)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the slam's shockwave lies on the ground round him (z -1), drawn round so it reads the same on both sides; the
    # charge's dust (q_dash) is left where he started. tft.dll plays the Warden shield's flash (p_burst) and the leap's
    # landing (e_land) itself
    views_e = [E("a_hit"), E("q_shield", FX, 3), E("q_dash", FX, 1, False), E("q_hit"), E("e_land"),
               E("r_slam", BIG, -1, False), E("r_hit")]
    if is_native:
        views_e += [E("p_burst", FX, 3)]
    views_b = [B_("q_stun", FX, 3), B_("e_guard", FX, 3), B_("r_taunt", FX, 4), B_("r_wall", FX, 3),
               B_("p_shield", FX, 3)]
    kit = {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "CC", "Shield"],
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
    if is_native:   # tft.dll (addons/tft/src/loris.rs): the Warden shields, Bulwark's leap and guard
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:warden", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/loris.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every name it plays or puts on (`lo("...")`) is the kit's, and every Native the kit calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "loris.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"loris.rs Params::default() differs from P (loris.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'lo\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"loris.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_loris:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects loris.rs does not register: {sorted(called - registered)}")


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
