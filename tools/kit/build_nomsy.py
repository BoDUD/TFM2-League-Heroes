"""Build tft_nomsy.data_champion (the tft pack's seventeenth hero: Nomsy, mid, Magician) from the parameters P.

    python tools/kit/build_nomsy.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Nomsy (诺姆希) is the chubby baby dragon of Teamfight Tactics set 7 (Dragonlands): the 3-cost unit TFT7_Nomsy (Dragon /
Prodigy, APCaster, range 4, 650 health, 60 mana). TFT gives her one ability (Fireballs! 火球！: a fireball lobbed at a
random enemy explodes on impact, magic damage within 1 hex, and bounces more fireballs that deal a share of it) and her
traits (Dragon 龙神: bonus health, armour and resistances, healing each second; Prodigy 龙族小天才). The rest is our own
design (the user's pick, 2026-10-29: mid lane, plan A 「龙神飞升」):
  passive Dragon Body (龙神之躯): the health of a dragon (hp above the Magician base); while her health is under p_low%
          she heals p_pct% of her maximum health every p_every ticks (a picture p_heal on her). tft.dll (below).
  attack  a little fire bolt (100% AD), homing on `Enemy` (towers too), spat on a_rel from her mouth (a_y).
  skill   Fireballs! (火球！, TFT's), `Targeting` on `EnemyWithoutTower` (q_range): she rears up roaring and lobs a big
          fireball (q_fall ticks) at the target; where it lands it explodes: q_dmg + q_ratio% AP magic damage within q_r,
          and q_n small fireballs bounce on from there to the nearest other enemies within q_br, q_k% of that damage each.
  skill2  Dragon Breath (龙息), `Targeting` on `EnemyWithoutTower` (e_range): she throws her head back and breathes a cone
          of fire (`DirDot` e_r, e_cone): e_dmg + e_ratio% AP magic damage, a burn (e_burn + e_burn_r% AP every 30 ticks,
          e_burn_t ticks) and scorched scales (magic resistance -e_mr% for e_mr_t ticks).
  ult     Dragon Ascension (龙神飞升), `Targeting` on `EnemyChampion` (r_range): she spreads her wings and flies up
          (r_rel), circling above the fight (damage taken -r_dr%, crowd control immune); r_n fireballs rain down every
          r_gap ticks, each on a random enemy within r_rng (an upright falling picture r_fall, the hit r_fall_t ticks
          later): r_dmg + r_ratio% AP magic damage; she lands, ascended: attack speed +r_as% and ability power +r_ap% for
          r_up_t ticks.

What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/nomsy.rs; the passive is tft_nomsy:dragon,
params NATIVE_KEYS): the data reads no health, so it cannot know she is low; and a projectile from the data always
leaves its caster, so the bouncing fireballs (tft_nomsy:bounce in the big fireball's end_effects, each hit
tft_nomsy:ember) are spawned by tft.dll at the explosion. --plain builds the data alone for the classic-engine balance
sims (they run no DLL code): the heal becomes a steady hp_regen (p_regen), the bounces q_n `RandomTarget`s
(from_projectile) of the same damage round the landing point. A build of P checks nomsy.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_nomsy"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 55000 like every mid; radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips exist (tools/art/rig_nomsy.py). Numbers = the 10-min classic-SDK simulations
# (C:/t/nm_sim, mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both
# sides; 2026-10-29), all --plain: the draft (hp 980, atk 76, Q 70 + 55% every 300 r 18000 bounces 50%, E 50 + 35%,
# R 8 x 50 + 30%) -2.73 on seeds 1-8 (tft_aoshin +0.64 / +1.23 on seeds 9-16); Q every 240 at 90 + 65%, E 70 + 45%,
# R 60 + 35%, atk 80 +0.13; + hp 1020, E within 45000, R 10 falls +0.06; + bounces 60%, blast 22000, R 70 + 40% +1.06
# / +2.50; bounces 55%, R 60 + 35% +0.59 / +1.82 = P.
P = {
    # stats (Magician base: attack 80 +6, ap 40 +20, hp 900 +100, def 20 +7, mr 20 +4, move 900 +9); a dragon's health
    "hp": 1020, "hp_g": 104, "atk": 80, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 20, "mr_g": 4,
    "ms": 880, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "a_rel": 9, "a_speed": 4000, "a_y": 2000,
    # passive Dragon Body (TFT's Dragon: healing each second); p_regen = the plain sims' steady stand-in
    "p_low": 40, "p_every": 60, "p_pct": 3, "p_regen": 10,
    # Fireballs! (TFT: 1-hex blast, bouncing fireballs)
    "q_cd": 240, "q_range": 60000, "q_dur": 36, "q_rel": 18, "q_fall": 24, "q_r": 22000,
    "q_dmg": 90, "q_ratio": 65, "q_n": 2, "q_k": 55, "q_br": 45000, "q_speed": 3000,
    # Dragon Breath
    "e_cd": 420, "e_range": 45000, "e_dur": 30, "e_rel": 12, "e_r": 62000, "e_cone": 600, "e_len": 100000, "e_w": 12000,
    "e_dmg": 70, "e_ratio": 45, "e_burn": 10, "e_burn_r": 6, "e_burn_t": 120, "e_mr": 20, "e_mr_t": 240,
    # Dragon Ascension
    "r_cd": 3000, "r_range": 70000, "r_rel": 24, "r_n": 10, "r_gap": 12, "r_rng": 70000, "r_fall_t": 18,
    "r_dmg": 60, "r_ratio": 35, "r_dr": 50, "r_land": 12, "r_as": 30, "r_ap": 25, "r_up_t": 300,
}
# what tft.dll reads from passive.params (addons/tft/src/nomsy.rs)
NATIVE_KEYS = ("p_low", "p_every", "p_pct", "q_dmg", "q_ratio", "q_r", "q_n", "q_k", "q_br", "q_speed")


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


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def pick(rng, target, effects, from_projectile=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": from_projectile,
            "effects": list(effects)}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower", seen=""):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point; `seen` = the
    picture played on the landing point the whole flight (build_alune.py's)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def line(name, length, width, target, effects, delay=1):
    """A line from her through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it); on
    `Ally` with no effects it is a picture only (build_sevika.py's flame)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: a little fire bolt
    hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_bolt", "Enemy", hit, p["a_speed"], p["a_y"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Fireballs!
    blast = [ap(p["q_dmg"], p["q_ratio"]), view("q_hit")]
    if is_native:   # tft.dll spawns the small ones at the explosion
        bounces = [native("bounce")]
    else:           # the sims: the same damage on random enemies round the landing point
        small = [ap(p["q_dmg"] * p["q_k"] // 100, p["q_ratio"] * p["q_k"] // 100), view("q_bounce_hit"),
                 tsfx("q_bounce_hit")]
        bounces = [pick(p["q_br"], "EnemyWithoutTower", small, from_projectile=True) for _ in range(p["q_n"])]
    ball = lob("q_ball", p["q_fall"], [sfx("q_hit"), zone("q_blast", p["q_r"], blast), *bounces])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q_vo"), delayed(p["q_rel"] - 1, sfx("q"), ball)))

    # ------------------------------------------------------------------ skill2: Dragon Breath
    cone = {"DirDot": {"radius": p["e_r"], "range": p["e_cone"]}}
    burn = {"type": "AddCasted", "casted_type": "Fire", "duration": p["e_burn_t"], "period": 30,
            "effects": [ap(p["e_burn"], p["e_burn_r"])]}
    scorch = [ap(p["e_dmg"], p["e_ratio"]), burn, buff("e_burn", p["e_mr_t"], magic_resistance_mult=-p["e_mr"]),
              tsfx("e_hit")]
    # the flame's picture rides a picture-only line from her mouth (top-bottom symmetric, turned with the cast)
    breath = combine(sfx("e"), sfx("e_burn"),
                     line("e_flame", p["e_len"], p["e_w"], "Ally", [], delay=p["e_dur"] - p["e_rel"]),
                     around(0, "EnemyWithoutTower", scorch, {"Forward": {"offset": 1000}}, cone))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    delayed(p["e_rel"] - 1, breath))

    # ------------------------------------------------------------------ ult: Dragon Ascension
    fall = [view("r_fall"), delayed(p["r_fall_t"], ap(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit"))]
    rain = [delayed(k * p["r_gap"], sfx("r_rain"), pick(p["r_rng"], "EnemyWithoutTower", fall))
            for k in range(p["r_n"])]
    air = p["r_rel"] + p["r_n"] * p["r_gap"] + p["r_fall_t"]
    r_dur = air + p["r_land"]
    ult = action("ult", r_dur, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_vo"), flag("r_fly", air, damaged_reduce=p["r_dr"], cc_immune=True),
                         delayed(p["r_rel"] - 1, sfx("r_roar"), *rain),
                         delayed(air, sfx("r_land"), sfx("r_up"),
                                 flag("r_up", p["r_up_t"], attack_speed_mult=p["r_as"], magic_power_mult=p["r_ap"]))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # a_bolt / q_ball / q_bounce are round fireballs (the same turned with their flight); e_flame a level plume along
    # the cast line, top-bottom symmetric; q_blast has no view (its explosion q_hit is a ViewEffect on the zone's units);
    # r_fall falls upright on the struck one (a ViewEffect, never turned, over the units: z 3); p_heal / r_up / e_burn
    # are buff pictures (tft.dll's heal puts p_heal on her)
    views_p = [B_("a_bolt"), B_("q_ball", BIG), B_("q_bounce"), B_("e_flame", BIG)]
    views_e = [E("a_hit"), E("q_hit", BIG, 3, False), E("q_bounce_hit"), E("r_fall", BIG, 3, False),
               E("r_hit", BIG, 3, False)]
    views_b = [B_("p_heal", FX, 3), B_("e_burn", FX, 3), B_("r_fly", FX, -1), B_("r_up", FX, 3)]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "Dot"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0 if is_native else p["p_regen"],
                 "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/nomsy.rs): the low-health heal, the bouncing fireballs
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:dragon", "params": {k: p[k] for k in NATIVE_KEYS}},
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


# names only tft.dll gives (the heal's buff and sound, the small fireballs' flight, her death cry: the native kit's data never sets or
# plays them; the views and the sound files still exist)
NATIVE_ONLY = {"p", "p_heal", "q_bounce", "q_bounce_hit", "d"}


def check_dll(p, kit):
    """addons/tft/src/nomsy.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), and every name it reads off the data or plays (`nm("...")`) is the kit's (a view, a sound) or
    NATIVE_ONLY."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "nomsy.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"nomsy.rs Params::default() differs from P (nomsy.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'nm\("(\w+)"\)', src))
    have = names(kit) | {n(x) for x in NATIVE_ONLY}
    missing = sorted(x for x in read if n(x) not in have)
    if not read or missing:
        raise SystemExit(f"nomsy.rs reads or plays names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_nomsy:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'add_native_effect\(format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects nomsy.rs does not register: {sorted(called - registered)}")


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
