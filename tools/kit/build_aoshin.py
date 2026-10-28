"""Build tft_aoshin.data_champion (the tft pack's twelfth hero: Ao Shin, mid, Magician) from the parameters P.

    python tools/kit/build_aoshin.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Ao Shin (敖兴) is the storm dragon of Teamfight Tactics set 7 (Dragonlands), the pack's first set-7 hero: the 5-cost
unit TFT7_AoShin (Tempest / Dragon, APCaster, range 4, 800 health, 160 mana). TFT gives him one ability (Lightning
Storm 闪电暴雨: 20 bolts at random enemies, magic damage each, 10 mana drained from the current target) and his traits
(Tempest 风暴龙: 8 s into combat lightning strikes the whole board, % max health true damage and a 1 s stun, then the
Tempest units deal more damage). The rest is our own design (the user's pick, 2026-10-28: mid lane, plan A 「风暴龙神」):
  passive Tempest Might (风暴龙威): p_delay ticks into a fight (an enemy champion within p_sense of him, the count kept
          through short lulls) lightning falls on every enemy champion within p_r: true damage p_hp% of their maximum
          health and a stun of p_stun ticks (the bolt picture p_bolt on each); then he deals more (magic_power_mult
          +p_amp% for p_t ticks: p_storm, crackling round him). Once every p_cd ticks. tft.dll (below).
  attack  ball lightning (100% AD), homing on `Enemy` (towers too), released on a_rel from his jaw (a_y).
  skill   Thunder Breath (雷息), `Targeting` on `EnemyWithoutTower` (q_range): a straight bolt q_len long
          from him through the target (a `LineRangeProjectile` q_w wide: a band about q_w + 15000 to either side, the
          picture a view-only bolt from his jaw, q_speed a tick, q_y): q_dmg + q_ratio% AP magic damage and the static
          (BlockSkill q_sil ticks: TFT drains mana, and the engine can only shorten a cooldown, never lengthen one -
          `skill_cooldown_mult` caps, `entity_reduce_cooldown` cuts - so the drain is a short silence, the same "no
          spell for a while").
  skill2  Cloud Ride (腾云), `Targeting` on `EnemyChampion` (e_range, a champion close): he flies straight away from it
          (MoveBack e_back x e_back_t) under a storm-cloud shield (e_sh + e_ratio% AP for e_sh_t ticks).
  ult     Lightning Storm (闪电暴雨, TFT's ability), `Targeting` on `EnemyChampion` (r_range): he rears up and calls the
          storm; r_n bolts every r_gap ticks, each on a random enemy champion within r_rng of him (the bolt an upright
          picture on the struck one): r_dmg + r_ratio% AP magic damage and the static (BlockSkill r_sil ticks).

What the data cannot read is the tft pack's own code (tft.dll, addons/tft/src/aoshin.rs; the passive is
tft_aoshin:storm, params NATIVE_KEYS): a fight's length - the data only runs in actions, so it cannot count the ticks
since enemy champions came near. --plain builds the data alone for the classic-engine balance sims (they run no DLL
code): the storm rides on the Thunder Breath - a cast with an enemy champion within p_sense, the storm off p_cool, sets
p_cool for p_cd ticks and lets the storm fall p_delay ticks later (FixedAttack target_hp_ratio p_hp, the stun, the
p_storm buff on him). A build of P checks aoshin.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_aoshin"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 55000 like every mid; radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips exist (tools/art/rig_aoshin.py). Numbers = the 10-min classic-SDK simulations (C:/t/ao_sim,
# mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both sides; 2026-10-28),
# all --plain: the draft (hp 860, Q 40 + 34% every 300, R 10 x 34 + 20%, E shield 70 every 660 within 32000, storm 8%
# every 1500, +20% ap) -2.96 on seeds 1-8 (tft_alune +1.20, league_ziggs +1.38); Q 55 + 45%, R 45 + 28% -2.07; + hp 920,
# E 110 every 480, storm 12% every 1200 +30% -1.95; + Q every 240 at 60 + 50%, E within 42000 -0.34; + R 12 x 55 + 32%,
# attack 80 +1.40 / +1.14 (seeds 9-16); the breath's picture moved to a view-only bolt from his jaw (a bolt that hit as
# it flew, 6000 a tick, scored -0.02: the line's band is wider) +1.31 / +1.34 = P. Timings and heights then set on the
# strips (rig_aoshin.MS): a projectile leaves 5000 - y_offset over his pivot, his snout 8 px over the ground in the lunge
# and the breath frames (3 under the pivot): a_y = q_y = 8000 (the -18000 first set put the breath 34 px up); the line
# strikes q_at - 1 ticks after it appears, when the bolt (6 px a tick) reaches a target 48 px off (it struck at once):
# seeds 1-24 +0.97 / +1.43 / +1.52 striking at once, +0.68 / +0.90 (1-16) at q_at 9, + Q 70 +0.44 / +1.49 / +0.85,
# + Q 80 +0.64 / +1.23 / +1.17 (mean +1.01, tft_alune +1.20) = P.
P = {
    # stats (Magician base: attack 80 +6, ap 40 +20, hp 900 +100, def 20 +7, mr 20 +4, move 900 +9)
    "hp": 920, "hp_g": 96, "atk": 80, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 24, "atk_cd": 90, "a_rel": 9, "a_speed": 4000, "a_y": 8000,
    # passive Tempest Might (TFT: 8 s, 10-30% max health true damage, 1 s stun, 10-60% damage amp)
    "p_sense": 70000, "p_delay": 180, "p_quiet": 120, "p_r": 85000, "p_hp": 12, "p_stun": 50, "p_amp": 30, "p_t": 360,
    "p_cd": 1200,
    # Thunder Breath
    "q_cd": 240, "q_range": 60000, "q_dur": 30, "q_rel": 12, "q_len": 75000, "q_w": 12000, "q_speed": 6000, "q_y": 8000, "q_at": 9,
    "q_dmg": 80, "q_ratio": 50, "q_sil": 40,
    # Cloud Ride
    "e_cd": 480, "e_range": 42000, "e_dur": 18, "e_rel": 4, "e_back": 3000, "e_back_t": 8,
    "e_sh": 110, "e_ratio": 40, "e_sh_t": 180,
    # Lightning Storm (TFT: 20 bolts of 160 / 235 / 666 at 1-3 stars, 10 mana drained each)
    "r_cd": 3000, "r_range": 70000, "r_rel": 24, "r_n": 12, "r_gap": 6, "r_rng": 75000,
    "r_dmg": 55, "r_ratio": 32, "r_sil": 18,
}
# what tft.dll reads from passive.params (addons/tft/src/aoshin.rs)
NATIVE_KEYS = ("p_sense", "p_delay", "p_quiet", "p_r", "p_hp", "p_stun", "p_amp", "p_t", "p_cd")


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


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


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


def silence(tick):
    return {"type": "BlockSkill", "tick": tick}


def pick(rng, target, effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, length, width, target, effects, apply=1):
    """A line from him through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it),
    hitting once `apply - 1` ticks after it appears (league_chogath's); no picture of its own."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": apply + 1,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def bolt(name, speed, rng, y):
    """The breath's picture: a fast view-only bolt from his jaw (leaving 5000 - y over his pivot) along the line (league_aurelionsol's breath; a
    LineRangeProjectile's own picture is drawn at his feet' height and stands still)."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": "EnemyWithoutTower",
            "applied_effects": [], "end_effects": [], "speed": speed, "range": rng, "shape": circle(1000),
            "y_offset": y}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def storm(p):
    """The passive's lightning as data (--plain): every enemy champion within p_r, then his damage up."""
    hit = [{"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": p["p_hp"]},
           {"type": "Stun", "duration": p["p_stun"]}, buff("p_bolt", 30), tsfx("p_stun")]
    return combine(sfx("p"), sfx("p_bolt"), around(p["p_r"], "EnemyChampion", hit),
                   flag("p_storm", p["p_t"], magic_power_mult=p["p_amp"]))


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: ball lightning
    hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_ball", "Enemy", hit, p["a_speed"], p["a_y"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Thunder Breath (+ the plain storm)
    zap = [ap(p["q_dmg"], p["q_ratio"]), silence(p["q_sil"]), buff("q_sil", p["q_sil"]), view("q_hit"), tsfx("q_hit")]
    breath = combine(sfx("q"), line("q_line", p["q_len"], p["q_w"], "EnemyWithoutTower", zap, p["q_at"]),
                     bolt("q_beam", p["q_speed"], p["q_len"], p["q_y"]))
    plain_storm = None
    if not is_native:   # tft.dll counts the fight; the sims let a breath near a champion start the storm's clock
        plain_storm = when("p_cool", combine(), pick(p["p_sense"], "EnemyChampion", [
            flag("p_cool", p["p_cd"]), delayed(p["p_delay"], storm(p))]))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   delayed(p["q_rel"] - 1, breath, plain_storm))

    # ------------------------------------------------------------------ skill2: Cloud Ride
    ride = combine(sfx("e"), cview("e_cast"), {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]},
                   on_me({"type": "Shield", "amount": p["e_sh"], "attack_ratio": 0, "ap_ratio": p["e_ratio"],
                          "tick": p["e_sh_t"]}),
                   flag("e_shield", p["e_sh_t"]), sfx("e_shield"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    delayed(p["e_rel"] - 1, ride))

    # ------------------------------------------------------------------ ult: Lightning Storm
    strike = [view("r_bolt"), tsfx("r_bolt"), ap(p["r_dmg"], p["r_ratio"]), silence(p["r_sil"]),
              buff("r_sil", p["r_sil"])]
    strikes = [delayed(k * p["r_gap"], pick(p["r_rng"], "EnemyChampion", strike)) for k in range(p["r_n"])]
    r_dur = p["r_rel"] + p["r_n"] * p["r_gap"] + 6
    ult = action("ult", r_dur, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_roar"), flag("r_cloud", r_dur),
                         delayed(p["r_rel"] - 1, *strikes)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # a_ball is a round ball of lightning, the same turned with its flight; q_beam a level bolt segment flying along the line
    # (turned half round to the left it reads the same: a jagged band, top-bottom symmetric). r_bolt falls upright on the struck champion (a
    # ViewEffect on its target, never turned, over the units: z 3); r_cloud hangs over him while he calls the storm;
    # p_bolt (tft.dll's storm and the plain one) is a buff picture: dll-played pictures are not seen in game
    views_p = [B_("a_ball"), B_("q_beam")]
    views_e = [E("a_hit"), E("q_hit"), E("e_cast", FX, 2, False), E("r_bolt", BIG, 3, False)]
    views_b = [B_("p_bolt", BIG, 3), B_("p_storm", FX, 3), B_("q_sil", FX, 4), B_("r_sil", FX, 4, "q_sil"),
               B_("e_shield", FX, 3), B_("r_cloud", BIG, 4)]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"],
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
    if is_native:   # tft.dll (addons/tft/src/aoshin.rs): the storm after a fight's first seconds
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:storm", "params": {k: p[k] for k in NATIVE_KEYS}},
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


# names only tft.dll gives (its storm's buffs and sounds: the native kit's data never sets or plays them; the views
# and the sound files still exist)
NATIVE_ONLY = {"p_bolt", "p_storm", "p", "p_stun"}


def check_dll(p, kit):
    """addons/tft/src/aoshin.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), and every name it reads off the data or plays (`ao("...")`) is the kit's (a view, a sound) or
    NATIVE_ONLY."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "aoshin.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"aoshin.rs Params::default() differs from P (aoshin.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'ao\("(\w+)"\)', src))
    have = names(kit) | {n(x) for x in NATIVE_ONLY}
    missing = sorted(x for x in read if n(x) not in have)
    if not read or missing:
        raise SystemExit(f"aoshin.rs reads or plays names the kit does not have: {missing}")


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
