"""Build tft_sohm.data_champion (the tft pack's twenty-second hero: Sohm, mid, Magician) from the parameters P.

    python tools/kit/build_sohm.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Sohm (索姆) is the sea dragon of Teamfight Tactics set 7 (Dragonlands): the 4-cost unit TFT7_AquaticDragon (Lagoon /
Mage / Dragon, APCaster, range 4, 800 health, 40 mana), a long eastern dragon who always floats, coiled in the air.
TFT gives her one ability (Tideblossom / 潮涌: a wave at an enemy without her mark, magic damage to every enemy on the
way, the mark - a water flower - moving to a nearby enemy when its bearer dies; after 3 casts the next one blasts 2
hexes round every marked enemy) and the Lagoon trait (ability power and attack speed for the casts). The rest is our own
design (the user's pick, 2026-10-30: mid lane, plan A 「潮汐之花」):
  passive Lagoon Power (碧波之力): every cast of Q, E or R adds a tide stack: ability power +p_ap% and attack speed
          +p_as% for p_t ticks, at most p_max stacks, every stack timed afresh. tft.dll (below).
  attack  a water bolt (水泡弹, 100% AD), homing on `Enemy` (towers too), spat on a_rel from her mouth (a_y).
  skill   Tideblossom (潮涌, TFT's), `Targeting` on `EnemyWithoutTower` (q_range): she rears up and sends a wave in a
          straight line at the nearest enemy champion without her flower (else at the cast's target): q_dmg + q_ratio%
          AP magic damage to every enemy it passes (q_w wide); when it gets there a water flower opens over the target
          for m_t ticks; a flowered enemy who falls sends its flower to the nearest enemy without one within j_r.
  skill2  Tidecaller's Guard (海潮护佑), `None` on `EnemyWithoutTower` (e_range: in lane and in fights alike; on
          `EnemyChampion` the AI cast it 8.6 times a game, here 29): her little claws push the
          water out: the allied champion within e_ar with the lowest share of health (she too) gets a water shield of
          e_sh + e_sh_ap% AP for e_sh_t ticks and attack speed +e_as% as long.
  ult     Tidal Bloom (潮汐绽放, TFT's fourth cast), `Targeting` on `EnemyChampion` (r_range): she rises and lifts her
          claws: every flower of hers bursts, r_dmg + r_ratio% AP magic damage to every enemy within r_r of any flower
          (each once), and the flowers are gone; with no flower out it bursts on the cast's target.

What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/sohm.rs; the passive is tft_sohm:lagoon,
params NATIVE_KEYS): the data reads no buffs on other units, so it cannot tell who has her flower, nor move a flower
from the fallen; it reads no health, so it cannot find the weakest ally (the AI hands ally casts out without looking at
health, champion-data section 3); and a buff added again in data stacks without a cap and keeps its own timer.
--plain builds the data alone for the classic-engine balance sims (they run no DLL code): the tide is a timed caster
buff on each cast (no cap), the wave a line through the target (q_range long) and the flower nothing; the shield goes
to a random allied champion within e_ar; the bloom bursts on r_plain_n random enemy champions within r_range. A build
of P checks sohm.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_sohm"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 55000 like every mid; radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips exist (tools/art/rig_sohm.py). Stats start from tft_nomsy's (the Magician base: attack
# 80 +6, ap 40 +20, hp 900 +100, def 20 +7, mr 20 +4, move 900 +9); Sohm is the 4-cost dragon with TFT's higher
# resistance. Numbers = the 10-min classic-SDK simulations (C:/t/so_sim with C:/t/al_sim/kd.py: mid lane 2 against
# the base pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both sides; 2026-10-30),
# all --plain, tft_nomsy --plain the control (+1.12 on seeds 1-8, +1.16 on 9-16): the draft (tide 8% / 8%, Q 70 + 50%
# every 270, E on `EnemyChampion` with an 80 + 60% shield, R 140 + 70% every 2400) -1.81, E cast 8.6 times a game; E on
# `EnemyWithoutTower` -1.89 (29.6 casts); Q 95 + 65% every 240, R 180 + 90% every 2100 +0.42; both +0.82; + tide
# 10% / 10% and a 110 + 70% shield +1.84; the tide 9% / 9% and a 95 + 65% shield +1.46 / +0.90 (seeds 9-16) = P.
P = {
    # stats
    "hp": 980, "hp_g": 102, "atk": 78, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 20, "def_g": 7, "mr": 24, "mr_g": 5,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "a_rel": 10, "a_speed": 4000, "a_y": 2000,
    # passive Lagoon Power (TFT's Lagoon: ability power and attack speed for the casts)
    "p_max": 5, "p_t": 360, "p_ap": 9, "p_as": 9,
    # Tideblossom
    "q_cd": 240, "q_range": 62000, "q_dur": 36, "q_rel": 18, "q_dmg": 95, "q_ratio": 65, "q_w": 9000, "q_speed": 3500,
    "m_t": 900, "j_r": 40000, "j_speed": 3000,
    # Tidecaller's Guard
    "e_cd": 480, "e_range": 60000, "e_dur": 30, "e_rel": 14, "e_ar": 55000, "e_sh": 95, "e_sh_ap": 65, "e_sh_t": 180,
    "e_as": 25,
    # Tidal Bloom
    "r_cd": 2100, "r_range": 70000, "r_dur": 48, "r_rel": 24, "r_r": 32000, "r_dmg": 180, "r_ratio": 90,
    "r_plain_n": 2,
}
# what tft.dll reads from passive.params (addons/tft/src/sohm.rs)
NATIVE_KEYS = ("p_max", "p_t", "p_ap", "p_as", "q_range", "q_dmg", "q_ratio", "q_w", "q_speed", "m_t", "j_r",
               "j_speed", "e_ar", "e_sh", "e_sh_ap", "e_sh_t", "e_as", "r_r", "r_dmg", "r_ratio")


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


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def pick(rng, target, effects, from_projectile=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": from_projectile,
            "effects": list(effects)}


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def line(name, length, width, target, effects, delay=1):
    """A line from her through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ passive: Lagoon Power (one tide stack a cast)
    if is_native:
        tide = native("tide")
    else:   # the sims: a timed stack per cast, no cap
        tide = flag("p_tide", p["p_t"], magic_power_mult=p["p_ap"], attack_speed_mult=p["p_as"])

    # ------------------------------------------------------------------ attack: a water bolt
    hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_bolt", "Enemy", hit, p["a_speed"], p["a_y"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Tideblossom
    if is_native:   # tft.dll picks the unflowered enemy, sends the wave, opens the flower
        wave = native("wave")
    else:           # the sims: a line through the cast's target
        wave = line("q_wave", p["q_range"], p["q_w"], "EnemyWithoutTower", [ap(p["q_dmg"], p["q_ratio"]), view("q_hit")])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   delayed(p["q_rel"] - 1, sfx("q"), tide, wave))

    # ------------------------------------------------------------------ skill2: Tidecaller's Guard
    if is_native:   # tft.dll finds the weakest ally
        guard = native("guard")
    else:           # the sims: a random allied champion in reach
        guard = pick(p["e_ar"], "AllyChampion", [shield(p["e_sh"], p["e_sh_ap"], p["e_sh_t"]),
                                                 buff("e_shield", p["e_sh_t"], attack_speed_mult=p["e_as"])])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "None", "EnemyWithoutTower",
                    delayed(p["e_rel"] - 1, sfx("e"), view("e"), tide, guard))

    # ------------------------------------------------------------------ ult: Tidal Bloom
    if is_native:   # tft.dll bursts every flower of hers
        bloom = native("bloom")
    else:           # the sims (and Sylas's stolen copy): bursts on random enemy champions, the lotus on each
        burst = lob("r_seed", 2, [view("r_bloom"), zone("r_zone", p["r_r"], [ap(p["r_dmg"], p["r_ratio"]),
                                                                             view("r_hit")])], "EnemyChampion")
        bloom = combine(*[pick(p["r_range"], "EnemyChampion", [burst]) for _ in range(p["r_plain_n"])])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), delayed(p["r_rel"] - 1, sfx("r_cast"), tide, bloom)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # a_bolt / q_jump are round (the same turned with their flight); q_wave a level torrent along its flight, top-bottom
    # symmetric (turned with it; tft.dll flies it); q_hit / r_hit splash on the struck one; r_bloom the flower's big
    # burst (z 3, over the units); e the ripple at her claws; q_flower floats over the flowered one's head, e_shield a
    # water bubble round the shielded one, p_glow her tide (behind her, z -1)
    views_p = [B_("a_bolt"), B_("q_wave", BIG), B_("q_jump")]
    views_e = [E("a_hit"), E("q_hit"), E("e"), E("r_bloom", BIG, 3, False), E("r_hit", FX, 3, False)]
    views_b = [B_("q_flower", FX, 3), B_("e_shield", FX, 3), B_("p_glow", FX, -1)]
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
    if is_native:   # tft.dll (addons/tft/src/sohm.rs): the tides, the flowers, the shield, the bloom
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:lagoon", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Tidal Bloom as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll (the user, 2026-10-27:
    「塞拉斯的大招什么一定要能偷到特效版本的」). The kit's --plain ult: r_plain_n lotuses bursting on random enemy
    champions, their hits. The views are the kit's own (tft_sohm_*); make_override copies them and their sheets."""
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


# names only tft.dll gives (the tide's buffs and sound, the wave, the flowers and their sounds, the shield, the bloom, her
# death cry: the native kit's data never sets or plays them; the views and the sound files still exist)
NATIVE_ONLY = {"p", "p_tide", "p_glow", "q_wave", "q_hit", "q_mark", "q_flower", "q_jump", "q_jump_hit", "e_shield",
               "r_bloom", "r_hit", "d"}


def check_dll(p, kit):
    """addons/tft/src/sohm.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), and every name it reads off the data or plays (`sm("...")`) is the kit's (a view, a sound) or
    NATIVE_ONLY."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "sohm.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"sohm.rs Params::default() differs from P (sohm.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'sm\("(\w+)"\)', src))
    have = names(kit) | {n(x) for x in NATIVE_ONLY}
    missing = sorted(x for x in read if n(x) not in have)
    if not read or missing:
        raise SystemExit(f"sohm.rs reads or plays names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_sohm:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'add_native_effect\(format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects sohm.rs does not register: {sorted(called - registered)}")


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
