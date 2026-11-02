"""Build tft_sentry.data_champion (a tft pack hero: the Sentry, bottom lane, Range) from the parameters P.

    python tools/kit/build_sentry.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Sentry (苍蓝哨戒; en Pebbles) is Teamfight Tactics set 18's 1-cost Rift Monster / Oracle (DA_18_Sentry, range 4, 500
health, 35 AD, 0.80 attack speed, 25 armour and magic resistance, 30/70 mana): Azure Laser / 蔚蓝激光 - it drains a
share of its maximum mana a second and channels a laser at its target: magic damage every second and magic resistance
down; Blue Buff: every few seconds channelled, mana regeneration. Two floating crystal shards with a blue core. The kit
is our own design from that (the user's pick, 2026-11-02: bottom lane, plan A 「蔚蓝激光」):
  passive Blue Buff (青霸符): while the laser is channelled, every full p_every ticks the ult's remaining cooldown is
          p_cut ticks shorter (`tft_sentry:blue`, tft.dll: a 2-tick ult_cooldown_mult that caps it there; the engine's
          one skill_cooldown_mult cuts Q and E together, and Q is cooling down while it lases, so only the ult can take
          an exact cut). tft.dll also folds the laser when the lit enemy leaves q_break (or dies). --plain: no refund.
  attack  Shard Bolt (碎光弹) on `Enemy` (towers too): a homing azure bolt from the core, 100% AD + a_ap% AP magic.
  skill   Azure Laser (蔚蓝激光, TFT's), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): it lases
          the target q_t ticks (`skill` then `skill_loop`; q_ch: move_speed_mult -q_root, 0 in P: it floats on while it
          lases, the sims' pick over standing still): every q_p ticks a zap (a fast homing projectile) deals q_dmg + q_ratio% AP magic in q_t / q_p equal parts and q_mr magic
          resistance down for q_hold ticks (same-name buffs stack), and keeps the lock (q_lock) on it for tft.dll. The
          beam's picture rides a slow homing projectile lifted to the core (league_velkoz R's way). Crowd control on it
          ends the channel at the next check (league_velkoz R's breaks); its death ends the laser (alive()).
  skill2  Rift Leap (裂石跃迁), `Targeting` on `EnemyChampion` (e_range: one is close): the two halves split - every
          enemy within e_r takes e_dmg + e_ratio% AP magic and is e_slow% slower for e_hold ticks, the shard ring left on
          the ground - and it blinks back (MoveBack e_back x e_back_t) as they close again.
  ult     Prism Sweep (棱镜扫射), `Position` on `EnemyChampion` (r_range, only in fights): the halves open wide and the core
          fires a thick beam swept across a cone in front (r_len, r_cos): r_dmg + r_ratio% AP magic and r_mr magic
          resistance down for r_hold ticks to every enemy in it; the sweep's picture rides a view-only line.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/sentry.rs; the passive is
tft_sentry:blue, params NATIVE_KEYS): no data passive counts time or reads a cooldown or a distance. A build of P
checks sentry.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_sentry"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 60000 like the pack's bottoms (tft_daeja, tft_gromp); radii count the unit's collision radius
# (~15000) on top. Timings from the frames (tools/art/rig_sentry.py MS): the bolt leaves on a_rel 8 (133 ms: a_fire
# showing), the laser from q_rel 10 (skill 200 ms = q_anim 12, then skill_loop), Rift Leap's blink on e_rel 4 inside its
# 300 ms (e_dur 18), the sweep on r_rel 18 (300 ms: r_blast showing) inside its 667 ms (r_dur 40). Heights (a projectile
# starts 5000 - y_offset above the pivot, 1000 a game px; the pivot is 11 px over the ground): its core is 19 px over
# the ground with the hover (22 design rows + 3 at PPU 1.29), 8 over the pivot: a_y / q_by -3000. The laser's and the
# sweep's pictures creep 1 px a tick (q_bspeed, r_speed 1000) and are drawn held on the core
# (tools/art/import_sentry_fx.py).
# Stats from the Range base (attack 100 +20, hp 900 +90, def 20 +7, mr 15 +3, move 900 +9), less attack and more magic
# power: an AP carry like tft_daeja and tft_gromp. Numbers = the 10-min classic-SDK simulations (C:/t/pb_sim with
# C:/t/al_sim/kd.py: bottom lane 3 against the base archer, gunner, boomerang and poison-dart hunters, three lineups,
# both sides; 2026-11-02), all --plain (no Blue Buff refund): the draft (atk 90, Q 200 + 120% rooted, E reach 30000, R
# 220 + 110%, hp 820) -4.45 on seeds 1-8 against tft_gromp --plain +1.51 / +0.50 (seeds 1-8 / 9-16): the rooted laser
# cost it its attacks and its life, E came out 2.4 times a game; Q 400 + 220% / cd 360, E reach 45000, R 280 + 140%,
# atk 95, bolt +45% -2.00; free to move while lasing (q_root 0) and hp 950 def 26 mr 22 -0.57 / -2.24; R 320 + 160%, E
# 80 + 45% +0.27 / -0.61; Q 460 + 250%, hp 1000 +0.24 / +0.47 = P (+ the shred 6 / 30: +0.40 / -0.21): the 1-cost a
# little under the 2-cost Gromp.
P = {
    # stats (Range, an AP carry)
    "hp": 1000, "hp_g": 80, "atk": 95, "atk_g": 11, "apw": 30, "apw_g": 16, "def": 26, "def_g": 7, "mr": 22, "mr_g": 3,
    "ms": 900, "ms_g": 9,
    "atk_range": 60000, "atk_dur": 24, "atk_cd": 72, "a_rel": 8, "a_speed": 5000, "a_y": -3000, "a_ap": 45,
    # passive Blue Buff (TFT: mana regeneration every few seconds channelled; ours: the ult's cooldown)
    "p_every": 60, "p_cut": 60, "q_break": 85000,
    # Azure Laser (TFT: magic a second + magic resistance down while channelled)
    "q_cd": 360, "q_range": 65000, "q_rel": 10, "q_anim": 12, "q_t": 150, "q_p": 15, "q_dmg": 460, "q_ratio": 250,
    "q_mr": 4, "q_hold": 120, "q_brk": 5, "q_root": 0, "q_zap": 30000, "q_bspeed": 1000, "q_by": -3000,
    # Rift Leap
    "e_cd": 600, "e_range": 45000, "e_dur": 18, "e_rel": 4, "e_r": 24000, "e_dmg": 80, "e_ratio": 45, "e_slow": 40,
    "e_hold": 90, "e_back": 6000, "e_back_t": 6,
    # Prism Sweep
    "r_cd": 2100, "r_range": 70000, "r_dur": 40, "r_rel": 18, "r_len": 85000, "r_cos": 500, "r_dmg": 320,
    "r_ratio": 160, "r_mr": 25, "r_hold": 180, "r_speed": 1000,
}
# what tft.dll reads from passive.params (addons/tft/src/sentry.rs)
NATIVE_KEYS = ("p_every", "p_cut", "r_cd", "q_break")
# names sentry.rs uses that need no view: sounds (the refund, the death), the refund buff
NATIVE_ONLY = {"d", "p", "p_cd"}


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


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def unanim(*names):
    return [{"type": "RemoveCasterAnimation", "name": x} for x in names]


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def view_line(name, speed, rng, y):
    """A line that hits nothing: only its picture flies (the sweep)."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": "EnemyWithoutTower",
            "applied_effects": [], "end_effects": [], "speed": speed, "range": rng, "shape": circle(1), "y_offset": y}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on it alone, also from a target's list (a `Delayed` here is queued on it)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def alive(*effects):
    """Run only while it lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_velkoz)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def cone(radius, target, effects, cos):
    """A cone in front of it toward the action's target point (league_darius E / league_cassiopeia R)."""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: the shard bolt
    bolt = [attack(0, 100), ap(0, p["a_ap"]), view("a_hit"), tsfx("a_hit")]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_bolt", "Enemy", bolt, p["a_speed"], p["a_y"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Azure Laser
    waves = p["q_t"] // p["q_p"]
    dmg, ratio = round(p["q_dmg"] / waves), round(p["q_ratio"] / waves)
    lit = [ap(dmg, ratio), buff("q_shred", p["q_hold"], magic_resistance=-p["q_mr"]), buff("q_lock", p["q_p"] + 6),
           view("q_hit"), tsfx("q_hit")]

    def wave(k):
        """The k-th zap on the target and the beam's picture from the core; every third one the shred's sound."""
        hits = lit + ([tsfx("q_shred")] if k % 3 == 2 else [])
        return combine(homing("q_zap", "EnemyWithoutTower", hits, p["q_zap"], p["q_by"]),
                       homing("q_beam", "EnemyWithoutTower", [], p["q_bspeed"], p["q_by"]))
    # folded once: the flag gone (crowd control, tft.dll's range break) while q_on still says it was lasing
    fold = sw("q_on", combine(*rm("q_on"), *unanim("skill", "skill_loop"), sfx("q_end")))
    breaks = casted(p["q_t"], p["q_brk"], pick(1, "AllyChampionInCC", *rm("q_ch")))
    t0 = p["q_rel"] - 1
    hold = p["q_t"] + p["q_rel"]
    laser = combine(
        *rm("q_ch", "q_on"), flag("q_ch", hold, move_speed_mult=-p["q_root"]), flag("q_on", hold),
        anim("skill", p["q_anim"]), delayed(p["q_anim"], sw("q_ch", anim("skill_loop", hold - p["q_anim"]))),
        on_me(breaks), delayed(t0, alive(sw("q_ch", sfx("q")))),
        *[delayed(t0 + k * p["q_p"], alive(sw("q_ch", wave(k), fold))) for k in range(waves)],
        delayed(t0 + p["q_t"], fold, *rm("q_ch")))
    skill = action("skill", p["q_rel"] + 2, p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", laser)

    # ------------------------------------------------------------------ skill2: Rift Leap
    split = [ap(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_hold"], move_speed_mult=-p["e_slow"])]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(sfx("e_split"), cview("e_split"), cview("e_ring"), sfx("e_ring"),
                            around(p["e_r"], "EnemyWithoutTower", split), delayed(3, sfx("e_slow")),
                            delayed(p["e_rel"] - 1, sfx("e"),
                                    {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]})))

    # ------------------------------------------------------------------ ult: Prism Sweep
    swept = [ap(p["r_dmg"], p["r_ratio"]), buff("r_shred", p["r_hold"], magic_resistance=-p["r_mr"]), view("r_hit"),
             tsfx("r_hit")]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Position", "EnemyChampion",
                 combine(sfx("r"), cview("r_open"), delayed(6, sfx("r_charge")),
                         delayed(p["r_rel"] - 1, sfx("r_beam"),
                                 cone(p["r_len"], "EnemyWithoutTower", swept, p["r_cos"]),
                                 view_line("r_sweep", p["r_speed"], p["r_len"], p["q_by"]))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, rep=True: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                                "repeat": rep, "z": z}
    # a_bolt / q_zap fly laid along their flight, top-bottom symmetric (turned with it); q_beam the beam from the core
    # (league_velkoz R's slow lifted projectile); r_sweep the swept beam (BIG, turned with the cast); the hits are
    # ViewEffects on the struck; e_split / r_open on it (caster pictures, never mirrored: drawn symmetric); e_ring the
    # shards left on the ground (not following); q_shred / r_shred the cracked-blue mark on the shredded, e_slow the
    # shard dust on the slowed
    views_p = [B_("a_bolt"), B_("q_zap"), B_("q_beam", BIG, rep=False), B_("r_sweep", BIG, rep=False)]
    views_e = [E("a_hit"), E("q_hit"), E("e_split", FX, 3), E("e_ring", BIG, -1, False), E("r_open", BIG, 3),
               E("r_hit")]
    views_b = [B_("q_shred", FX, 3), B_("e_slow", FX, 3), B_("r_shred", FX, 3)]
    kit = {
        "id": ID, "category": "Range", "tags": ["AP", "Magic", "Range"],
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
    if is_native:   # tft.dll (addons/tft/src/sentry.rs): Blue Buff's ult refund and the laser's range break
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:blue", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/sentry.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every name it plays, reads or puts on (`gp("...")`) is the kit's or NATIVE_ONLY, and every Native
    the kit calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "sentry.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"sentry.rs Params::default() differs from P (sentry.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'gp\("(\w+)"\)', src))
    have = names(build(p, False)) | names(kit) | {n(x) for x in NATIVE_ONLY}
    missing = sorted(x for x in read if n(x) not in have)
    if not read or missing:
        raise SystemExit(f"sentry.rs plays names the kit does not have: {missing}")
    called = set(re.findall(r'"(?:effect_ref|passive_ref)": "tft_sentry:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native code sentry.rs does not register: {sorted(called - registered)}")


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
