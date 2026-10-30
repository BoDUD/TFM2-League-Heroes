"""Build tft_shiohyu.data_champion (the tft pack's twentieth hero: Shi Oh Yu, top, Melee) from the parameters P.

    python tools/kit/build_shiohyu.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Shi Oh Yu (石傲玉) is the jade dragon of Teamfight Tactics set 7 (Dragonlands): the 4-cost unit TFT7_DragonGreen (Jade /
Mystic / Dragon, an AD fighter, range 1, 1000 health, 75 AD, 0.75 attack speed, 65 armour and magic resistance, 30/50
mana), a jade dragon-man martial artist standing upright, two folded wings rising behind his back. TFT gives him one
ability (Jade Form / 玉龙形态: 20-50% durability and crowd-control immunity, and his next three attacks empowered - the
first stuns 1 s, the second deals true damage, the third ends the stance with a wave down a line that hits and stuns
every enemy in it, each 190-250% AD). The rest is our own design (the user's pick, 2026-10-30: top lane, plan A
「玉龙三连」):
  passive Jade Skin (玉石之肤): when his health drops under p_low% his skin turns to jade: p_red% less damage for p_t
          ticks, then not again for p_cd ticks (each life starts ready). tft.dll (below). --plain: E's cast puts the
          skin on, off a p_cd lockout.
  attack  Dragon Claw Combo (龙爪三连) on `Enemy` (towers too): three alternating claw swipes (TFT's attack1-3: `attack`,
          `attack2`, `attack3` frames, a_t ticks to land the next), the first two a_pct% AD, the third a3_dmg + a3_ad%.
          In Jade Form the next three attacks are its blows instead (ult below).
  skill   Jade Fist Barrage (玉拳连打), `Targeting` on `EnemyWithoutTower` (q_range, waves and camps too): he rushes at the
          target (`MoveToTarget` q_speed, his `dash` frames) and lands q_n punches q_gap apart (his `skill` frames), each
          q_dmg + q_ad% AD.
  skill2  Earthshaker (震地), `Targeting` on `EnemyWithoutTower` (e_range): his fist into the ground: every enemy within
          e_r takes e_dmg + e_ad% AD, is knocked up e_up ticks and slowed e_slow% for e_slow_t ticks.
  ult     Jade Form (玉龙形态, TFT's), `None` on `EnemyChampion` (r_range, only in fights): wings out, jade light - r_red%
          less damage and crowd-control immunity until the third blow (r_t ticks at most), and his next attacks are:
          blow 1 r_dmg + r_ad% AD and a stun of r_stun ticks; blow 2 r_dmg + r_ad% AD as true damage (`FixedAttack`);
          blow 3 ends the stance: a jade wave down the line to the target (`LineRangeProjectile` r3_len x r3_w) hits
          every enemy in it for r_dmg + r_ad% AD and stuns them r_stun ticks.
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/shiohyu.rs; the passive is
tft_shiohyu:jade, params NATIVE_KEYS): the data reads no health, so it cannot know he is low. A build of P checks
shiohyu.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_shiohyu"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's top fighters; radii count the unit's collision radius (~15000) on top.
# Timings are placeholders until the strips exist (tools/art/rig_shiohyu.py). Stats start from tft_sevika's (hp 1200
# +118, atk 82, def 36, mr 30): Shi Oh Yu is the 4-cost jade dragon, sturdier, with TFT's even armour and resistance.
# Numbers = the 10-min classic-SDK simulations (C:/t/sy_sim with C:/t/al_sim/kd.py: top lane 0 against the base fighter,
# executioner, knight, berserker, lancer and pole warrior, three lineups, both sides; 2026-10-30), all --plain (the skin
# on E's cast): the draft (hp 1220, atk 78, R every 35 s within 40000, 150% AD blows) -2.41 on seeds 1-8 (ult 2.2 a
# game); R every 25 s within 60000, atk 84, hp 1260, Q 45%, E 110% -0.16; + attack every 66, blows 175%, def 48 +0.66
# / +0.23 (seeds 9-16); + E's knock-up 0.75 s, E every 9 s, Q every 7 s +1.42 / +1.03 = P (tft_sevika --plain +0.94 /
# +1.91 on the same games).
P = {
    # stats (Melee, a top fighter with attack damage)
    "hp": 1260, "hp_g": 118, "atk": 84, "atk_g": 10, "apw": 0, "apw_g": 0, "def": 48, "def_g": 8, "mr": 38, "mr_g": 6,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 66, "atk_st": 12, "a_pct": 100, "a_t": 240, "a3_dmg": 20,
    "a3_ad": 130,
    # passive Jade Skin (TFT's Jade Form durability, once a fight at low health)
    "p_low": 50, "p_red": 40, "p_t": 180, "p_cd": 1800,
    # Jade Fist Barrage
    "q_cd": 420, "q_range": 45000, "q_dur": 60, "q_speed": 3500, "q_n": 4, "q_first": 6, "q_gap": 8,
    "q_dmg": 15, "q_ad": 45,
    # Earthshaker
    "e_cd": 540, "e_range": 30000, "e_dur": 36, "e_st": 14, "e_r": 45000, "e_dmg": 50, "e_ad": 110, "e_up": 45,
    "e_slow": 35, "e_slow_t": 90,
    # Jade Form (TFT: 190 / 250% AD a blow, 1 s stuns, 20-25% durability at 1-2 stars)
    "r_cd": 1500, "r_range": 60000, "r_dur": 40, "r_t": 480, "r_red": 35,
    "r_dmg": 40, "r_ad": 175, "r_stun": 60, "r3_len": 90000, "r3_w": 20000,
}
# what tft.dll reads from passive.params (addons/tft/src/shiohyu.rs)
NATIVE_KEYS = ("p_low", "p_red", "p_t", "p_cd")


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
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def true_attack(dmg, ratio):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0}


def around(radius, target, effects, at="AroundCaster", shape=None):
    return {"type": "RangeEffect", "shape": shape or circle(radius), "target": target, "apply_type": at,
            "effects": list(effects)}


def line(name, length, width, target, effects, delay=1):
    """A line from him through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it),
    hitting once a tick after it appears (league_chogath's)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: three swipes, or Jade Form's blows
    swipe = lambda tag, dmg, ratio, s: combine(anim(tag, p["atk_dur"]) if tag != "attack" else None, sfx(s),
                                               attack(dmg, ratio), view("a_hit"), tsfx("a_hit"))
    combo = when("a_2", combine(unflag("a_2"), swipe("attack3", p["a3_dmg"], p["a3_ad"], "a")),
                 when("a_1", combine(unflag("a_1"), flag("a_2", p["a_t"]), swipe("attack2", 0, p["a_pct"], "a")),
                      combine(flag("a_1", p["a_t"]), swipe("attack", 0, p["a_pct"], "a"))))
    # Jade Form's blows: r_b1 -> r_b2 -> r_b3 (each put on by the one before, all ending with the stance)
    blow1 = combine(unflag("r_b1"), flag("r_b2", p["r_t"]), sfx("r1"), attack(p["r_dmg"], p["r_ad"]),
                    {"type": "Stun", "duration": p["r_stun"]}, view("r1_hit"), tsfx("r1_hit"))
    blow2 = combine(unflag("r_b2"), flag("r_b3", p["r_t"]), anim("attack2", p["atk_dur"]), sfx("r2"),
                    true_attack(p["r_dmg"], p["r_ad"]), view("r2_hit"), tsfx("r2_hit"))
    blow3 = combine(unflag("r_b3"), unflag("r_jade"), anim("r_wave", p["atk_dur"]), sfx("r3"), sfx("r3_wave"),
                    line("r3_wave", p["r3_len"], p["r3_w"], "EnemyWithoutTower",
                         [attack(p["r_dmg"], p["r_ad"]), {"type": "Stun", "duration": p["r_stun"]}, view("r3_hit"),
                          tsfx("r3_hit")]))
    count = when("r_b3", blow3, when("r_b2", blow2, when("r_b1", blow1, combo)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      count, atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Jade Fist Barrage
    punches = [delayed(p["q_first"] + k * p["q_gap"], sfx("q_punch"), attack(p["q_dmg"], p["q_ad"]), view("q_hit"),
                       tsfx("q_hit")) for k in range(p["q_n"])]
    flurry = p["q_first"] + p["q_n"] * p["q_gap"]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), anim("dash", p["q_dur"]),
                           {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] + 40000,
                            "end_effects": [anim("skill", flurry), *punches]}))

    # ------------------------------------------------------------------ skill2: Earthshaker
    if is_native:
        skin = None
    else:   # --plain: the jade skin rides on E's cast, off a lockout (the data reads no health)
        skin = when("p_lock", combine(), combine(flag("p_lock", p["p_cd"]), flag("p_skin", p["p_t"], damaged_reduce=p["p_red"]),
                                            sfx("p"), cview("p")))
    slam = delayed(p["e_st"] - 1, sfx("e_hit"), view("e_slam"),
                   around(p["e_r"], "EnemyWithoutTower", [
                       attack(p["e_dmg"], p["e_ad"]), {"type": "Airborne", "duration": p["e_up"]},
                       buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit")]))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), skin, slam))

    # ------------------------------------------------------------------ ult: Jade Form
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "None", "EnemyChampion",
                 combine(sfx("r"), sfx("r_roar"), cview("r"),
                         flag("r_jade", p["r_t"], damaged_reduce=p["r_red"], cc_immune=True),
                         unflag("r_b2"), unflag("r_b3"), flag("r_b1", p["r_t"])))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the claws, the fists, the slam's hits and the blows burst on what they hit; the slam's crack sits on the ground
    # under him (symmetric); the stance's flash plays on him (symmetric); the wave is a line turned to the target (drawn
    # top-bottom symmetric, so turned half round to the left it reads the same); the stance and the skin are auras
    views_p = [B_("r3_wave", BIG)]
    views_e = [E("a_hit"), E("q_hit"), E("e_slam", BIG, 1, False), E("e_hit"), E("r", FX, 4), E("r1_hit"),
               E("r2_hit"), E("r3_hit"), E("p", FX, 4)]
    views_b = [B_("e_slow", FX, 3), B_("r_jade", FX, 3), B_("p_skin", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC", "Tank"],
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
    if is_native:   # tft.dll (addons/tft/src/shiohyu.rs): the jade skin at low health
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:jade", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/shiohyu.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback), every picture it puts on or plays has a view, and the passive it registers is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "shiohyu.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"shiohyu.rs Params::default() differs from P (shiohyu.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    views = {v["name"] for k in ("view_projectiles", "view_effects", "view_buffs") for v in kit[k]}
    used = set(re.findall(r'sy\("(\w+)"\)', src))
    unseen = sorted(x for x in used if n(x) not in views)
    if not used or unseen:
        raise SystemExit(f"pictures shiohyu.rs plays or puts on have no view: {unseen}")
    if f'format!("{{ID}}:jade")' not in src:
        raise SystemExit("shiohyu.rs does not register tft_shiohyu:jade")


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="the data alone, no tft.dll passive (for the balance sims)")
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
