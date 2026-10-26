"""Build tft_maddie.data_champion (the tft pack's fifth hero: Maddie, bot, Range) from the parameters P.

    python tools/kit/build_maddie.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

Maddie is the Piltover enforcer and sharpshooter from Arcane, a 1-cost of Teamfight Tactics set 13 (TFT13_Shooter,
Enforcer / Sniper, range 6, 500 health, 20/120 mana). TFT gives her one ability (Fan the Hammer: 6 shots at the
FARTHEST enemy, each hitting the first enemy in its way for 135% AD) and two traits (Sniper: more damage the farther
the target; Enforcer: the enemy with the most health is Wanted, and a Wanted kill gives attack speed). The rest is our
own design (the user's pick, 2026-10-27: bot lane, plan A 「狙神·通缉」):
  passive Sniper (狙神): her attack, the bullets and the snipe deal p_max% more the farther the unit hit stands
          from her, rising evenly up to p_far (tft.dll's passive raises every hit of hers as it lands, on_attack: the
          data cannot measure a distance; --plain adds p_avg% to each ratio, the bonus at about her attack range).
  attack  a rifle shot at `Enemy` (towers too): 100% AD, a fast homing bullet released on a_rel.
  skill   Fan the Hammer (连拨击锤, TFT's ability), `Targeting` on `EnemyWithoutTower` (q_range): she crouches and fans q_n
          shots, q_gap ticks apart, at the FARTHEST enemy within q_range (champions first); each bullet flies in a line
          and hits the first enemy in its way for q_dmg + q_ratio% AD (tft.dll; --plain: q_n homing bullets at the
          target the AI picked).
  skill2  Wanted (通缉令), `Targeting` on `EnemyChampion` (e_range, only in fights): the enemy champion with the most
          health within e_range is Wanted for e_t ticks: it takes e_amp% more damage from everyone; when it dies Wanted,
          she gets a bounty, w_as% attack speed for the rest of her life (up to w_max bounties) (tft.dll; --plain: the
          mark on the AI's target and no bounty).
  ult     Enforcer's Snipe (执法狙杀), `Targeting` on `EnemyChampion` (r_range): she aims r_rel ticks, then one piercing
          round flies at the enemy champion with the lowest health share within r_range: every enemy in its line takes
          r_dmg + r_ratio% AD, raised by r_exec% of the share of health it is missing (tft.dll; --plain: one bullet at
          the AI's target, r_exec at half health).

tft.dll's part is addons/tft/src/maddie.rs: the passive tft_maddie:sniper (params, the Sniper bonus, the bounties),
tft_maddie:fan -> tft_maddie:shot -> tft_maddie:bullet (Fan the Hammer),
tft_maddie:wanted, tft_maddie:snipe -> tft_maddie:round (the ult). A build of P checks maddie.rs's Params::default()
against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_maddie"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 68000 (Caitlyn 65000: TFT's range 6 is the longest there is); radii count the unit's collision
# radius (~15000) on top. Timings are placeholders until the strips exist (tools/art/rig_maddie.py). Numbers = the
# 10-min classic-SDK simulations (C:/t/md_sim, Silco's copy of the balance sim: bot lane 3 against archer, gunner,
# boomerang_hunter and poison_dart_hunter, three lineups, both sides), all --plain.
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, def 20 +7, mr 15 +3, move 900 +9; TFT's Maddie is a 1-cost
    # with 500 health and a slow 0.70 attack speed against the longest range)
    "hp": 880, "hp_g": 88, "atk": 104, "atk_g": 20, "apw": 0, "apw_g": 0, "def": 18, "def_g": 7, "mr": 15, "mr_g": 3,
    "ms": 900, "ms_g": 9,
    "atk_range": 68000, "atk_dur": 24, "atk_cd": 66, "a_rel": 10, "a_speed": 9000,
    # passive Sniper (TFT: 5-20% a hex, 5-75% base)
    "p_max": 25, "p_far": 100000, "p_avg": 15,
    # Fan the Hammer (TFT: 6 shots of 135% AD at the farthest enemy, 1.15 s)
    "q_cd": 540, "q_range": 80000, "q_dur": 72, "q_rel": 14, "q_n": 6, "q_gap": 8, "q_dmg": 10, "q_ratio": 40,
    "q_speed": 9000, "q_width": 4000,
    # Wanted (TFT Enforcer: the most health; +30% attack speed a Wanted kill)
    "e_cd": 900, "e_range": 90000, "e_dur": 30, "e_rel": 12, "e_t": 480, "e_amp": 15, "w_as": 15, "w_max": 4,
    # Enforcer's Snipe
    "r_cd": 3000, "r_range": 200000, "r_dur": 90, "r_rel": 66, "r_dmg": 220, "r_ratio": 140, "r_exec": 60,
    "r_speed": 16000, "r_width": 6000,
}
# what tft.dll reads from passive.params (addons/tft/src/maddie.rs)
NATIVE_KEYS = ("p_max", "p_far", "q_range", "q_n", "q_gap", "q_dmg", "q_ratio", "q_speed", "q_width", "e_range", "e_t",
               "e_amp", "w_as", "w_max", "r_range", "r_dmg", "r_ratio", "r_exec", "r_speed", "r_width")


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
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # --plain: the Sniper bonus at about her attack range on every ratio
    up = (lambda r: r) if is_native else (lambda r: r * (100 + p["p_avg"]) // 100)

    # ------------------------------------------------------------------ attack: a rifle shot
    hit = [attack(0, up(100)), view("a_hit"), tsfx("a_hit")]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"), homing("a_bullet", "Enemy", hit, p["a_speed"])),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Fan the Hammer
    if is_native:   # tft.dll picks the farthest enemy and fires the bullets in lines
        fan = combine(sfx("q_cast"), delayed(p["q_rel"] - 1, native("fan")))
    else:           # q_n homing bullets at the AI's target
        shot = homing("q_bullet", "EnemyWithoutTower", [attack(p["q_dmg"], up(p["q_ratio"])), view("q_hit"),
                                                        tsfx("q_hit")], p["q_speed"])
        fan = combine(sfx("q_cast"), *[delayed(p["q_rel"] - 1 + k * p["q_gap"], sfx("q"), shot)
                                       for k in range(p["q_n"])])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", fan)

    # ------------------------------------------------------------------ skill2: Wanted
    if is_native:
        mark = native("wanted")
    else:
        mark = combine(buff("e_wanted", p["e_t"], damaged_amplify=p["e_amp"]), view("e_mark"), tsfx("e"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    delayed(p["e_rel"] - 1, mark))

    # ------------------------------------------------------------------ ult: Enforcer's Snipe
    if is_native:
        snipe = native("snipe")
    else:   # one round at the AI's target, the execute at half health
        dmg = p["r_dmg"] * (200 + p["r_exec"]) // 200
        snipe = homing("r_round", "EnemyChampion", [attack(dmg, up(p["r_ratio"]) * (200 + p["r_exec"]) // 200),
                                                    view("r_hit"), tsfx("r_hit")], p["r_speed"])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), sfx("r_aim"), view("r_sight"), delayed(p["r_rel"] - 1, sfx("r_shot"), snipe)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                            "tag": tag or name, "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the bullets fly as pictures turned with their flight; the hits on the unit hit; r_sight is the crosshair over the
    # ult's target while she aims (the AI's target: tft.dll fires at the weakest, mostly the same champion); tft.dll
    # plays q_hit / r_hit on what its bullets hit and p_bounty on her when a Wanted enemy dies
    views_p = [B_("a_bullet"), B_("q_bullet"), B_("r_round", BIG)]
    views_e = [E("a_hit"), E("q_hit"), E("e_mark", FX, 4), E("r_sight", BIG, 4), E("r_hit", BIG, 3)]
    if is_native:
        views_e.append(E("p_bounty", FX, 4))
    views_b = [B_("e_wanted", FX, 4), B_("p_bounty", FX, 3, "p_bounty_loop")]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "Execute"],
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
    if is_native:   # tft.dll (addons/tft/src/maddie.rs)
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:sniper", "params": {k: p[k] for k in NATIVE_KEYS}},
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
    """addons/tft/src/maddie.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are its
    fallback), every name it plays or puts on (`md("...")`) is the kit's, and every Native the kit calls it registers."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "maddie.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"maddie.rs Params::default() differs from P (maddie.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'md\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit))
    if not read or missing:
        raise SystemExit(f"maddie.rs plays or puts on names the kit does not have: {missing}")
    called = set(re.findall(r'"effect_ref": "tft_maddie:(\w+)"', json.dumps(kit)))
    registered = set(re.findall(r'format!\("\{ID\}:(\w+)"\)', src))
    if called - registered:
        raise SystemExit(f"the kit calls Native effects maddie.rs does not register: {sorted(called - registered)}")


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
