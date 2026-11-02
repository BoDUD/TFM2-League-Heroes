"""Build tft_riftherald.data_champion (a tft pack hero: the Rift Herald, top, Melee) from the parameters P.

    python tools/kit/build_riftherald.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Rift Herald (峡谷先锋) is Teamfight Tactics set 16's 4-cost Void bruiser (TFT16_RiftHerald, range 1, 1100 health, 60
AD, 0.60 attack speed, 60 armour and magic resistance, 60/125 mana): Warp Armor / 扭曲护甲 - gain max health and grow
larger, slam a 2-hex circle on the target (magic, AP + % health), for 4 s gain durability, +1% for each enemy targeting
it. Set 9's summoned Herald had Void Charge (charge forward: % max health magic damage and a stun). The kit is our own
design from those and League's Herald (the user's pick, 2026-11-02: 「按方案做，上单」):
  passive Void Shell (虚空甲壳): p_dr% less damage taken for each enemy champion within p_r, at most p_max of them
          (tft.dll `tft_riftherald:shell` keeps the buff `p_shell` up to date every CHECK ticks; --plain: a flat
          p_plain% from its first action, Permanent).
  attack  Rending Pincer (裂钳) on `Enemy` (towers too): the pincer comes down at atk_st, 100% AD.
  skill   Spin Sweep (回旋横扫, TFT's SpinAttack), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too): at
          q_st it spins once, every enemy within q_r takes q_dmg + q_ratio% AD + q_hp% of its maximum health and is
          q_slow% slower for q_slow_t ticks.
  skill2  Void Charge (虚空冲锋, League's charge + set 9's), `Targeting` on `EnemyChampion` (e_range): it rears up
          (unstoppable for e_wind ticks), flips and charges onto the target (MoveToTarget, e_speed): everything on the
          way (a line e_len long, e_w wide from where it set off) takes e_dmg + e_hp% of its maximum health and is
          knocked aside (Airborne e_up); where it lands the champions within e_r take the same again and are stunned
          e_stun ticks.
  ult     Warp Armor (扭曲护甲, TFT's), `Targeting` on `EnemyChampion` (r_range): it roars and grows (the flag `r_big`,
          r_big_t ticks: +r_hpb maximum health, healed by as much; league.dll hd::FORMS draws it bigger), at r_st slams
          the ground in front of it: every enemy within r_r of the point r_off ahead takes r_dmg + r_ap% AP + r_hp% of
          its maximum health as magic damage; for r_t ticks (the flag `r_armor`) r_dr% less damage taken, and the shell
          counts r_per% more for each enemy champion near (tft.dll; --plain: r_dr only).
What the data cannot do is the tft pack's own code (tft.dll, addons/tft/src/riftherald.rs; the passive is
tft_riftherald:shell, params NATIVE_KEYS). A build of P checks riftherald.rs's Params::default() against it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_riftherald"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: melee range 25000 (the pincers); radii count the unit's collision radius (~15000) on top. Timings are
# placeholders until the strips are rigged (tools/art/rig_riftherald.py). Stats start from the pack's top tanks (tft_brock
# hp 1200 / atk 72 every 78 / def 38, tft_terra): the 4-cost void beast, a little lighter than Brock's 5-cost, its
# skills scaled by its health like TFT's.
# Numbers = the 10-min classic-SDK simulations (python -I C:/t/al_sim/kd.py <kit> --lane 0: top against the base fighter,
# executioner, knight, berserker, lancer and pole warrior, three lineups, both sides; 2026-11-02), all --plain (the shell a
# flat p_plain%): the draft (atk 66, Q 30 + 70% + 2%, E 30 + 3%, R 80 + 100% AP + 5%, shell 8%) -0.17 on seeds 1-8 against
# tft_brock --plain +1.60 and tft_terra --plain +0.94 (their sessions' numbers, the same games); v2 = P (atk 72, Q 40 + 90%
# + 3%, E 40 + 4%, R 100 + 120% + 6%, shell 10%) +1.25; v3 (atk 76, hp 1350, Q 50 + 100% + 3% every 7 s, E 50 + 5%, R 120 +
# 140% + 7%, shell 12%) +3.57 - too strong.
# q_r 38000 -> 45000 after the skills preview (2026-11-02): 38000 + a body's 15000 fell short of the enemy it fights at its
# own attack range (25000 + both bodies = 55000 centre to centre): the spin missed its own target; P with it +1.36 on
# seeds 1-16.
P = {
    # stats (Melee, a top fighter-tank)
    "hp": 1250, "hp_g": 120, "atk": 72, "atk_g": 11, "apw": 20, "apw_g": 8, "def": 40, "def_g": 8, "mr": 32, "mr_g": 6,
    "ms": 930, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 40, "atk_cd": 80, "atk_st": 22,
    # Void Shell (TFT: +1% durability for each enemy targeting it; ours per enemy champion near)
    "p_r": 45000, "p_dr": 4, "p_max": 5, "p_plain": 10,
    # Spin Sweep
    "q_cd": 480, "q_range": 30000, "q_dur": 40, "q_st": 20, "q_r": 45000, "q_dmg": 40, "q_ratio": 90, "q_hp": 3,
    "q_slow": 30, "q_slow_t": 60,
    # Void Charge (League: the Herald rams; set 9: % max health damage and a stun)
    "e_cd": 900, "e_range": 70000, "e_dur": 60, "e_wind": 24, "e_speed": 5000, "e_len": 70000, "e_w": 14000,
    "e_dmg": 40, "e_hp": 4, "e_up": 18, "e_r": 26000, "e_stun": 60,
    # Warp Armor (TFT: +health and bigger, a 2-hex slam AP + % health, 4 s durability + 1% an enemy targeting it)
    "r_cd": 3000, "r_range": 30000, "r_dur": 70, "r_st": 48, "r_big_t": 480, "r_hpb": 300, "r_off": 18000,
    "r_r": 40000, "r_dmg": 100, "r_ap": 120, "r_hp": 6, "r_t": 240, "r_dr": 15, "r_per": 3,
}
# what tft.dll reads from passive.params (addons/tft/src/riftherald.rs)
NATIVE_KEYS = ("p_r", "p_dr", "p_max", "r_per")
# names riftherald.rs uses that need no view: the death's sound and the shell (its strength alone)
NATIVE_ONLY = {"d", "p_shell"}


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


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap_attack(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def ahead(offset, radius, target, effects):
    """An area round the point `offset` in front of it, toward the action's target."""
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": {"Forward": {"offset": offset}},
            "effects": list(effects)}


def on_me(*effects):
    """Effects on it alone."""
    return around(1000, "AllyOnlySelf", effects)


def line(name, width, length, target, effects):
    """A one-tick strip from it toward the action's target."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": 2,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def shell(p):
    """--plain's Void Shell: a flat p_plain% less damage taken, put on (Permanent) by its first action each life."""
    return when("p_shell", combine(), flag("p_shell", None, damaged_reduce=p["p_plain"]))


def build(p, is_native=False):
    init = None if is_native else shell(p)

    # ------------------------------------------------------------------ attack: Rending Pincer
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(init, sfx("a"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Spin Sweep
    swept = [attack(p["q_dmg"], p["q_ratio"], p["q_hp"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
             view("q_hit"), tsfx("q_hit")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(init, sfx("q_vox"),
                           delayed(p["q_st"] - 1, sfx("q"), cview("q_spin"), around(p["q_r"], "EnemyWithoutTower", swept))))

    # ------------------------------------------------------------------ skill2: Void Charge
    rammed = [ap_attack(p["e_dmg"], 0, p["e_hp"]), {"type": "Airborne", "duration": p["e_up"]}, view("e_hit")]
    landing = around(p["e_r"], "EnemyChampion",
                     [ap_attack(p["e_dmg"], 0, p["e_hp"]), {"type": "Stun", "duration": p["e_stun"]},
                      buff("e_stun", p["e_stun"]), view("e_hit")])
    run = combine(sfx("e_boom"), anim("charge", 40), line("e_path", p["e_w"], p["e_len"], "EnemyWithoutTower", rammed),
                  {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"],
                   "end_effects": [sfx("e_hit"), cview("e_crash"), landing]})
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(init, sfx("e"), flag("e_wind", p["e_wind"] + 2, cc_immune=True),
                            delayed(p["e_wind"] - 1, run)))

    # ------------------------------------------------------------------ ult: Warp Armor
    slam = combine(sfx("r_hit"), view("r_slam"),
                   ahead(p["r_off"], p["r_r"], "EnemyWithoutTower", [ap_attack(p["r_dmg"], p["r_ap"], p["r_hp"])]),
                   sfx("r_armor"), flag("r_armor", p["r_t"], damaged_reduce=p["r_dr"]))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(init, sfx("r"), sfx("r_roar"), cview("r_roar"), flag("r_big", p["r_big_t"], hp=p["r_hpb"]),
                         delayed(2, on_me({"type": "Heal", "amount": p["r_hpb"], "attack_ratio": 0, "ap_ratio": 0,
                                           "heal_type": "Caster"})),
                         delayed(p["r_st"] - 1, slam)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    # the spin's ring, the charge's crash and the slam's crater lie on the ground where they struck (z -1, not following)
    views_e = [E("a_hit"), E("q_spin", BIG, -1, False), E("q_hit"), E("e_hit"), E("e_crash", BIG, -1, False),
               E("r_roar", BIG, 3), E("r_slam", BIG, -1, False)]
    views_b = [B_("q_slow"), B_("e_stun"), B_("r_armor", BIG)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AP", "Melee", "Tank", "CC"],
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
    if is_native:   # tft.dll (addons/tft/src/riftherald.rs): the Void Shell
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:shell", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def sylas_ult(p=None):
    """Warp Armor as plain data for league_sylas's copy (addons/league_sylas/make_override.py STOLEN): Sylas's add-on
    bundle is on the Workshop and the tft mod is not, so his stolen ult cannot call tft.dll - and the ult itself calls
    nothing native: the roar, the bigger health, the slam and the armour are all data. The views are the kit's own
    (tft_riftherald_*)."""
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
    """addons/tft/src/riftherald.rs's Params::default() holds P's numbers (tft.dll reads passive.params; the defaults are
    its fallback) and every name it plays or puts on (`rh("...")`) is the kit's."""
    import re
    src = open(lp(os.path.join(REPO, "addons", "tft", "src", "riftherald.rs")), encoding="utf-8").read()
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    got = {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+): ([\d_]+),", m.group(1))}
    bad = {k: (got.get(k), p[k]) for k in NATIVE_KEYS if got.get(k) != p[k]}
    if bad or set(got) != set(NATIVE_KEYS):
        raise SystemExit(f"riftherald.rs Params::default() differs from P (riftherald.rs, P): {bad}, keys "
                         f"{sorted(set(got) ^ set(NATIVE_KEYS))}")
    read = set(re.findall(r'rh\("(\w+)"\)', src))
    missing = sorted(x for x in read if n(x) not in names(kit) and x not in NATIVE_ONLY)
    if not read or missing:
        raise SystemExit(f"riftherald.rs plays or puts on names the kit does not have: {missing}")


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
