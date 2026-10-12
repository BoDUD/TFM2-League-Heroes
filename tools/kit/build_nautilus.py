"""Build league_nautilus.data_champion (support, Util) from the parameters P.

    python tools/kit/build_nautilus.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-11: support / Util; Q pulls both together; W and E in one slot; R at the farthest enemy
champion in reach; the passive in the main pack; a native add-on for Q on a wall; the pros' combos):
  passive Staggering Blow (排山倒海): his attack on an enemy champion roots it p_root ticks and deals p_dmg + p_ratio% AP
          more, then rests p_cd ticks (League: once per champion every 6 s; the data reads no buff on a target, so the
          rest is his). Champions only: a champion-only twin of the attack (league_viego's) carries it.
  attack  The anchor swung, the hit a_st ticks in (the strip's swing frame 4).
  skill   Q Dredge Line (疏通航道): a `Direction` cast on `EnemyChampion` (q_range): on tick q_at the anchor flies
          (q_speed, q_reach) past minions to the first enemy champion (league_amumu Q's bandage, wide: q_rad): q_dmg +
          q_ratio% AP, and the two are pulled together - the champion dragged toward him (`Grab`, q_pull a tick for q_pull_t
          ticks) while he hauls himself toward it (`MoveToTarget` a tick later, the skill_pull strip): they meet between.
          A miss pulls nobody. The hook arms the passive at once (q_land): the next attack roots even while it rests.
          On a wall the anchor pulls him to it and half the cooldown comes back - native, addons/league_nautilus (the copy
          built with native=1 calls its league_nautilus:hook as the anchor flies).
  skill2  W Titan's Wrath (泰坦之怒) + E Riptide (暗流涌动): a `Targeting` cast on `EnemyWithoutTower` (c_range): a shield
          of w_shield + w_ap% AP for w_t ticks, while it holds his attacks also hit everything round the target
          (w_dmg + w_ratio% AP, w_r); on tick e_at the slam: three waves (e_gap ticks apart) round him (e_r), every enemy
          takes e_dmg + e_ratio% AP once and is slowed e_slow% for e_slow_t.
  ult     R Depth Charge (深海冲击): a `Targeting` cast on `EnemyChampion` (r_range): the shockwave runs at an enemy
          champion within r_range picked at random (the farthest cannot be read: no effect sorts by distance; a random
          one reaches the back line as often as the front), knocking up every enemy on its way (r_path_up ticks,
          r_path_dmg + r_path_ratio% AP) and, on the champion, r_dmg + r_ratio% AP, r_up ticks in the air, then a
          r_stun-tick stun.
  combos  Q -> passive: the hooked champion is rooted by the next attack whatever its rest (q_land); Q -> R: R cast while
          q_land lasts goes at the hooked champion's spot first - the nearest within q_near - not at random.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_nautilus.data_champion")
ID = "league_nautilus"
FX = "asset/league/effects/league_nautilus_fx"
BIG = "asset/league/effects/league_nautilus_big"

# Timings from the strips (tools/art/fix_nautilus_strips2.py, assets/source/native/nautilus_cells.json): the attack's
# swing lands on frame 4 (tick 13), Q lets go on frame 5 (tick 14), the slam on skill2 frame 3 (tick 8), R's blow on
# frame 5 (tick 16); the strips last 28, 28, 31 and 39 ticks, skill_pull 24.
P = {
    # stats (Util base: attack 80 +6, hp 900 +100, defence 30, move 1000); League's Nautilus: 646 +100 hp, 61 AD +3.3,
    # 39 armour, 32 mr, 325 move, 175 range - a tank support like league_leona and league_blitzcrank
    "hp": 1120, "hp_g": 120, "atk": 78, "atk_g": 6, "mp": 25, "mp_g": 12, "def": 40, "def_g": 8, "mr": 28, "mr_g": 5,
    "ms": 990, "ms_g": 10,
    # attack: the anchor swung
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 80, "a_st": 13,
    # passive Staggering Blow (League: 2-? + 8 x level physical, root 0.75-1.75 s, 6 s per champion)
    "p_dmg": 20, "p_ratio": 30, "p_root": 50, "p_cd": 360,
    # Q Dredge Line (League: 1122 range, 2000 speed, 85-265 + 90% AP, cd 14-10 s)
    "q_cd": 600, "q_range": 75000, "q_dur": 28, "q_at": 14, "q_speed": 6000, "q_reach": 85000, "q_rad": 10000,
    "q_y": 3000, "q_dmg": 75, "q_ratio": 60, "q_pull": 2500, "q_pull_t": 8, "q_dash": 2500, "q_anim": 24, "q_land": 120,
    # skill2: W Titan's Wrath (League: 45-165 + 8-12% bonus hp shield 6 s, attacks deal 30-110 + 40% AP round the
    # target) + E Riptide (League: 3 waves 55-215 + 50% AP, slow 30-50% decaying over 1.25 s, cd 7-5 s)
    "c_cd": 480, "c_range": 25000, "c_dur": 31, "w_shield": 110, "w_ap": 60, "w_t": 360, "w_dmg": 15, "w_ratio": 20,
    "w_r": 18000, "e_at": 8, "e_gap": 5, "e_r": 32000, "e_dmg": 70, "e_ratio": 50, "e_slow": 40, "e_slow_t": 75,
    # R Depth Charge (League: 825 range, 150-350 + 80% AP, knock-up 1 s then stun 1-2 s; the path 125-275 + 40% AP)
    "r_cd": 3000, "r_range": 80000, "r_dur": 39, "r_at": 16, "r_speed": 2500, "r_dmg": 150, "r_ratio": 80, "r_up": 60,
    "r_stun": 45, "r_path_dmg": 60, "r_path_ratio": 30, "r_path_up": 30, "r_path_rad": 8000, "r_y": 0, "q_near": 30000,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_nautilus: the anchor's flight also asks league_nautilus:hook whether it bites a wall
    "native": 0,
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


NONE = {"type": "Combine", "effects": []}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


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


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ attack + passive Staggering Blow
    root = [{"type": "Bind", "duration": p["p_root"]}, buff("p_root", p["p_root"]), magic(p["p_dmg"], p["p_ratio"]),
            view("p_hit"), tsfx("p"), on_me(refresh("p_cd", p["p_cd"]), *rm("q_land"))]
    # the root rides a champion-only twin of the swing: a minion or a monster struck sets nothing off
    staggering = homing("p_twin", 100000, 0, "EnemyChampion", root)
    wrath = around(p["w_r"], "EnemyWithoutTower", [magic(p["w_dmg"], p["w_ratio"]), view("w_hit")])
    swing = combine(sfx("a_swing"), attack(0, 100), view("a_hit"), tsfx("a_hit"),
                    sw("q_land", staggering, sw("p_cd", NONE, staggering)),
                    sw("w_on", wrath))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy", swing,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Dredge Line
    hooked = [magic(p["q_dmg"], p["q_ratio"]), {"type": "Grab", "speed": p["q_pull"], "tick": p["q_pull_t"]},
              view("q_hit"), tsfx("q_hit"), on_me(refresh("q_land", p["q_land"])),
              delayed(1, anim("skill_pull", p["q_anim"]),
                      {"type": "MoveToTarget", "speed": p["q_dash"], "range": p["q_reach"] + 30000,
                       "end_effects": []})]
    wall = [{"type": "Native", "effect_ref": "league_nautilus:hook"}] if p["native"] else []
    throw = combine(sfx("q"), voice("vo_q", p),
                    delayed(p["q_at"], sfx("q_fly"),
                            line("q_anchor", p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], "EnemyChampion", False,
                                 hooked), *wall))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Direction", "EnemyChampion", throw)

    # ------------------------------------------------------------------ skill2: W Titan's Wrath + E Riptide
    slow = buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"])
    waves = [delayed(p["e_at"] + k * p["e_gap"], cview(f"e_wave{k + 1}")) for k in range(3)]
    slam = delayed(p["e_at"], sfx("e"), around(p["e_r"], "EnemyWithoutTower",
                                              [magic(p["e_dmg"], p["e_ratio"]), slow, view("e_hit"), tsfx("e_hit")]))
    skill2 = action("skill2", p["c_dur"], p["c_cd"], 1, p["c_range"], "Targeting", "EnemyWithoutTower",
                    combine(on_me(shield(p["w_shield"], p["w_ap"], p["w_t"])), refresh("w_on", p["w_t"]),
                            sfx("w"), voice("vo_e", p), slam, *waves))

    # ------------------------------------------------------------------ ult: R Depth Charge
    struck = [magic(p["r_dmg"], p["r_ratio"]), {"type": "Airborne", "duration": p["r_up"]}, view("r_hit"),
              tsfx("r_hit"), delayed(p["r_up"], {"type": "Stun", "duration": p["r_stun"]}, buff("r_stun", p["r_stun"]))]
    path = [magic(p["r_path_dmg"], p["r_path_ratio"]), {"type": "Airborne", "duration": p["r_path_up"]},
            view("r_up")]

    def charge():
        """The shockwave at the unit picked: a homing wave on it, a hidden line through those on its way."""
        return [homing("r_wave", p["r_speed"], p["r_y"], "EnemyChampion", struck),
                line("r_path", p["r_speed"], p["r_range"] + 10000, p["r_path_rad"], 0, "EnemyWithoutTower", True,
                     path)]
    go = sw("q_land", combine(*rm("q_land"), pick(p["q_near"], "EnemyChampion", flag("r_go", 1), *charge())))
    rand = sw("r_go", NONE, pick(p["r_range"], "EnemyChampion", *charge()))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(*rm("r_go"), sfx("r"), voice("vo_r", p), cview("r_cast"),
                         delayed(p["r_at"], sfx("r_wave"), go, rand)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("q_anchor"), P_("r_wave", BIG, -1)]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("w_hit"), E("e_hit"), E("r_hit", BIG), E("r_up"),
               E("r_cast", FX, 2, False), E("e_wave1", BIG, -1, False), E("e_wave2", BIG, -1, False),
               E("e_wave3", BIG, -1, False)]
    views_b = [B_("p_root", FX, -1), B_("e_slow", FX, -1), B_("r_stun", FX, 3), B_("w_on", FX, 3)]
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "CC", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }


def nodes(o):
    """Effect nodes in a tree (dicts with a `type`), the measure the game's per-tick clone cost follows."""
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[])
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p)
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
