"""Build tft_kobuko.data_champion (the tft pack's seventh hero: Kobuko, top, Melee) from the parameters P.

    python tools/kit/build_kobuko.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Kobuko is the big kung-fu cat yordle, the old master; drawn as Teamfight Tactics set 15's 2-cost (TFT15_Kobuko, Heavyweight /
Mentor, range 1, 800 health, 30/85 mana: Golden Claw Mantra / 金爪真言, a shield, then the next attack deals bonus physical
damage and stuns). Set 14's boss Kobuko adds the "second phase" (at half health he is enraged for the rest of the fight:
attack speed, omnivamp) and the slam (a nearby enemy picked, the enemies round it thrown up, then he crashes down on
it: "Game over!"). The kit is our own design from those (the user's pick, 2026-10-27: top lane, plan A 「金爪宗师」):
  passive Second Phase (第二阶段): the first time each life his health falls under p_hi% he is enraged until he dies:
          p_as% attack speed and p_vamp% life steal (tft.dll: the data reads no health; --plain puts the rage on at his
          first ult, the moment a fight is surely on).
  attack  a palm strike on `Enemy` (towers too): 100% AD on atk_st. While Golden Claw is armed (q_on) the strike
          instead deals q_dmg + q_ratio% AD + q_hp% of his maximum health and stuns q_stun ticks (his `claw`
          frames: the glowing palm slammed out), and disarms it.
  skill   Golden Claw Mantra (金爪真言), `Targeting` on `EnemyWithoutTower` at his attack range (waves and camps too): a
          shield of q_sh + q_sh_ap% AP for q_sh_t ticks and the claw armed for q_t ticks.
  skill2  Tiger Pounce (猛虎扑), `Targeting` on `EnemyWithoutTower` (e_range): he pounces onto the target (MoveToTarget,
          e_speed) and on landing every enemy within e_r takes e_dmg + e_ratio% AD + e_hp% of his maximum health and is
          thrown up e_up ticks.
  ult     Game Over! (游戏结束！), `Targeting` on `EnemyChampion` (r_range): he springs out of sight (dust where he
          sprang, a mark under the target; r_at ticks unseen, untouchable and unstoppable) and crashes down on the target: it takes r_main + r_main_ratio% AD + r_main_hp% of
          his maximum health, and every enemy within r_r (the target too) r_dmg + r_ratio% AD + r_hp% and is thrown up
          r_up ticks.

tft.dll (addons/tft/src/kobuko.rs): the Second Phase (passive tft_kobuko:rage). A build of P checks kobuko.rs's
Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_kobuko"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 like the pack's top fighters; radii count the unit's collision radius (~15000) on top.
# Timings follow the strips (tools/art/rig_kobuko.py MS): the palm lands at 233 ms, the golden claw plays its own tag
# (claw, 350 ms) from the strike; the ult's crouch and spring take r_go ticks before he is unseen. Stats start from the
# pack's top tanks and fighters (league_ornn, league_sett, league_volibear: hp 1100 +105..115, def 32-38, atk 80-90).
# Numbers = the 10-min classic-SDK simulations (C:/t/kb_sim, Alune's copy of the balance sim: top lane against the base
# fighter, executioner, knight, berserker, lancer and pole warrior, three lineups, both sides; 2026-10-27), all --plain
# (the rage from his first ult): the draft (Q every 7 s, 140% AD + 4% health, stun 1.5 s; E every 9 s up 0.6 s; R 120 +
# 100% on the target) +5.64 on seeds 1-8 against league_sett's +2.07 - the stun and the knock-ups kept the lane locked
# and the untouchable leap saved him (0.74 deaths a game). Q every 10 s, stun 1 s, 110% + 3%, E every 10 s up 0.4 s,
# R 80 on the target +2.83; with less damage and hp 1080 / atk 78 +1.61; lower still (rage 30% / 12%) -0.44. Between
# the first two = P: +2.01 / +1.84 (seeds 9-16; league_sett +2.58; the ult's knock-up then 50 ticks, now 48 = 0.8 s).
# tft.dll's rage at half health is not simulated.
P = {
    # stats (Melee, a top bruiser that tanks)
    "hp": 1110, "hp_g": 110, "atk": 80, "atk_g": 13, "apw": 20, "apw_g": 10, "def": 36, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 72, "atk_st": 14, "claw_t": 21,
    # passive Second Phase (TFT set 14: at 50%, 40-60% attack speed, 20-35% omnivamp)
    "p_hi": 50, "p_as": 40, "p_vamp": 20,
    # Golden Claw Mantra (TFT set 15: a 250-400 shield (+AP) 4 s; the next attack 150-225% AD + 4-6% health, stun 1.5 s)
    "q_cd": 570, "q_dur": 24, "q_sh": 70, "q_sh_ap": 50, "q_sh_t": 240, "q_t": 240,
    "q_dmg": 40, "q_ratio": 105, "q_hp": 2, "q_stun": 60,
    # Tiger Pounce
    "e_cd": 630, "e_range": 45000, "e_dur": 24, "e_speed": 3500, "e_r": 28000,
    "e_dmg": 40, "e_ratio": 70, "e_hp": 2, "e_up": 24,
    # Game Over! (TFT set 14: 2-hex knock-up 1-1.5 s, the slam on the picked one)
    "r_cd": 3000, "r_range": 50000, "r_dur": 60, "r_go": 15, "r_at": 36, "r_r": 36000,
    "r_main": 70, "r_main_ratio": 100, "r_main_hp": 6, "r_dmg": 70, "r_ratio": 60, "r_hp": 3, "r_up": 48,
}
# what tft.dll reads from passive.params (addons/tft/src/kobuko.rs)
NATIVE_KEYS = ("p_hi", "p_as", "p_vamp")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


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


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def rage(p):
    """The Second Phase's buff: tft.dll puts it on at p_hi% health; --plain at his first ult."""
    return flag("p_rage", None, attack_speed_mult=p["p_as"], vamp=p["p_vamp"])


def build(p, is_native=False):
    # ------------------------------------------------------------------ attack: a palm strike, or the golden claw
    plain = combine(attack(0, 100), view("a_hit"), tsfx("a_hit"))
    claw = combine(unflag("q_on"), {"type": "CasterAnimation", "name": "claw", "tick": p["claw_t"]},
                   attack(p["q_dmg"], p["q_ratio"], p["q_hp"]), {"type": "Stun", "duration": p["q_stun"]},
                   buff("q_stun", p["q_stun"]), view("q_hit"), tsfx("q_hit"), tsfx("q_stun"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a"), delayed(p["atk_st"] - 1, when("q_on", claw, plain))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Golden Claw Mantra
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["atk_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), on_me(shield(p["q_sh"], p["q_sh_ap"], p["q_sh_t"])), cview("q_shield"),
                           flag("q_on", p["q_t"])))

    # ------------------------------------------------------------------ skill2: Tiger Pounce
    struck = [attack(p["e_dmg"], p["e_ratio"], p["e_hp"]), {"type": "Airborne", "duration": p["e_up"]}, view("e_hit")]
    landing = [sfx("e_hit"), cview("e_land"), around(p["e_r"], "EnemyWithoutTower", struck)]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 20000,
                                       "end_effects": landing}))

    # ------------------------------------------------------------------ ult: Game Over!
    hit = [attack(p["r_dmg"], p["r_ratio"], p["r_hp"]), {"type": "Airborne", "duration": p["r_up"]}, view("r_hit")]
    crash = combine({"type": "Teleport"}, sfx("r_slam"), sfx("r_hit"), cview("r_slam"),
                    attack(p["r_main"], p["r_main_ratio"], p["r_main_hp"]), around(p["r_r"], "EnemyWithoutTower", hit))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(None if is_native else rage(p), sfx("r"), sfx("vo"), view("r_mark"),
                         flag("r_air", p["r_at"], damaged_reduce=100, cc_immune=True),
                         delayed(p["r_go"] - 1, cview("r_jump"), {"type": "CasterInvisible", "tick": p["r_at"] - p["r_go"]}),
                         delayed(p["r_at"] - 1, crash)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the crash's shockwave and the pounce's landing ring lie on the ground round him (z -1), drawn round so they read
    # the same on both sides; the leap's dust stays where he sprang from, the landing mark rides the target while he is
    # up; the rage's flames burn behind him (z -1: over him they hid his body). tft.dll plays the Second Phase's flash
    # (p_burst) itself
    views_e = [E("a_hit"), E("q_shield", FX, 3), E("q_hit"), E("e_land", FX, -1, False), E("e_hit"),
               E("r_jump", FX, 1, False), E("r_mark", FX, -1), E("r_slam", BIG, -1, False), E("r_hit")]
    if is_native:
        views_e += [E("p_burst", FX, 3)]
    views_b = [B_("q_stun", FX, 3), B_("q_on", FX, 3), B_("p_rage", FX, -1)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC", "Shield"],
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
    if is_native:   # tft.dll (addons/tft/src/kobuko.rs): the Second Phase
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:rage", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/kobuko.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback) and every name it plays or puts on (`kb("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "kobuko.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"kobuko.rs Params::default() differs from P (kobuko.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'kb\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"kobuko.rs plays or puts on names the kit does not have: {missing}")


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
