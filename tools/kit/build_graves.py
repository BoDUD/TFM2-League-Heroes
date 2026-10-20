"""Build league_graves.data_champion (jungle, Range: the shotgun) from the parameters P.

    python tools/kit/build_graves.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: layout A - Q / E / R, W in the attack -, jungle, an add-on):
  passive New Destiny (新命运): the shotgun holds two shells. Every attack fires a spread: the pellet that strikes the
          target (a homing shot, a_ratio% AD) and the spread round it, a cone (`DirDot`, a_cone_r wide, about 26 degrees
          each side) of a_cone% AD on every enemy in it - the target too, so it takes the most, as in League where the
          unit in front eats most of the four pellets. The first shell sets `a_1` (a_keep ticks: out of a fight he has
          reloaded); the second plays `attack2` (the shot and the break-open reload) and blocks his attacks for a_reload
          ticks (league_jhin's reload: he walks and casts through it). The add-on lets each of the four pellets stop on
          the first unit in its line, knocks back monsters and minions hit by several, and cuts E's cooldown per hit.
  attack  The spread above. Every hit refreshes True Grit (E's stacks).
  W       Smoke Screen (烟幕弹), no slot of its own: every w_cd ticks his attack on an enemy champion also throws a smoke
          canister where it stands (a hidden lob from the hit, league_jinx R's drop): w_dmg magic damage, w_slow% slow
          for w_slow_t, and the "nearsight" as a w_blind-tick disarm on champions (league_quinn's blind); the cloud stays
          w_cloud ticks and slows whoever stands in it by w_in%.
  skill   Q End of the Line (穷途末路): a `Direction` cast on `EnemyWithoutTower` (q_cast; camps and waves too). The shell
          flies q_range through everything (q_dmg + q_ratio% AD) and lies where it stops; q_fuse ticks later it blows
          up (q_r round: q2_dmg + q2_ratio% AD; a zone whose period outlasts its life, league_lux E).
  skill2  E Quickdraw (快速拔枪): a `Targeting` cast on `EnemyWithoutTower` (e_range). An enemy champion within e_near ->
          a roll straight away from it (`MoveBack`, the pros' kite), else a dash e_dash toward the target (`RushTime`).
          True Grit: one stack (two when an enemy champion is within e_range), at most four, each e_def defence and
          e_mr magic resistance for e_t ticks; his attack hits refresh them all.
  ult     R Collateral Damage (终极爆弹): a `Direction` cast on `EnemyChampion` (r_cast). The recoil throws him back
          (`MoveBack` r_back x r_back_t - in a `Direction` cast nothing moves, so it sits in a `RandomTarget` on the
          champion aimed at, league_ezreal E) as the shell leaves; it flies r_range and stops on the FIRST enemy champion
          (r_dmg + r_ratio% AD), which blows up round it (r_r: r2_dmg + r2_ratio% AD on every enemy - League's cone
          behind the champion as a circle round it; a miss blows nothing up, league_jinx R).
Timings are placeholders until the strips exist.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_graves.data_champion")
ID = "league_graves"
FX = "asset/league/effects/league_graves_fx"
BIG = "asset/league/effects/league_graves_big"

P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9; the base junglers 120 +30,
    # hp 900 +80, move 1100 +14); League's Graves: 625 +106 hp, 66 AD, 33 +4.6 armour, 33 mr, 340 move, 425 range
    # (League 500 = 55000 here), attack speed 0.475
    "hp": 980, "hp_g": 98, "atk": 92, "atk_g": 19, "def": 26, "def_g": 7, "mr": 18, "mr_g": 3, "ms": 1000, "ms_g": 11,
    # attack: the spread (League: 4 pellets, the first full damage, the others a third; two shells, then a reload)
    "atk_range": 46000, "atk_dur": 26, "atk_cd": 54, "a_hit": 8, "a_speed": 9000, "a_y": -3000,
    "a_ratio": 75, "a_cone": 30, "a_cone_r": 56000, "a_cone_dot": 900, "a_keep": 300, "a_reload": 80,
    # W Smoke Screen (League: 950 range, 60-180 +60% AP magic, 50% slow 0.5 s, nearsight 4 s; cd 26-18 s)
    "w_cd": 720, "w_fly": 14, "w_r": 24000, "w_dmg": 60, "w_slow": 50, "w_slow_t": 30, "w_blind": 30,
    "w_cloud": 240, "w_in": 15,
    # skill: Q End of the Line (League: 925 range, 45-165 +80% bonus AD, the blast 85-285 +40-120% bonus AD after 1 s;
    # cd 13-6 s)
    "q_cd": 540, "q_cast": 75000, "q_dur": 22, "q_at": 8, "q_range": 70000, "q_speed": 5000, "q_w": 8000,
    "q_dmg": 45, "q_ratio": 60, "q_fuse": 60, "q_r": 24000, "q2_dmg": 60, "q2_ratio": 80,
    # skill2: E Quickdraw (League: 425 dash, True Grit 4-? armour / mr per stack, 8 stacks, 4 s; cd 16-12 s, -0.5 s per
    # pellet hit)
    "e_cd": 600, "e_range": 60000, "e_dur": 16, "e_at": 3, "e_near": 22000, "e_dash": 26000, "e_t_move": 8,
    "e_def": 7, "e_mr": 5, "e_t": 240,
    # ult: R Collateral Damage (League: 1100 range, 275-575 +150% bonus AD to the first champion, the cone 200-400
    # +120% bonus AD; recoil 400; cd 100-60 s)
    "r_cd": 3000, "r_cast": 100000, "r_dur": 30, "r_at": 10, "r_range": 110000, "r_speed": 9000, "r_w": 12000,
    "r_dmg": 120, "r_ratio": 90, "r_r": 32000, "r2_dmg": 80, "r2_ratio": 60, "r_back": 3000, "r_back_t": 5,
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
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def is_champ(*effects):
    """Inside a projectile's applied effects: the unit it hit, when that is a champion (league_sivir Q)."""
    return pick(1, "EnemyChampion", *effects, fp=True)


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, width, target, effects, end=(), penetrate=True):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(width)}


def lob(name, ticks, target, end):
    """A hidden 1-radius lob onto a spot (league_jinx R's drop: travel 1 lands on the unit hit)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": ticks, "range": 400000,
            "range_effect_name": "", "shape": circle(1000), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def burst(name, r, target, effects):
    """A one-tick circle where a projectile stopped (it needs that point: section 4)."""
    return {"type": "RangeProjectile", "name": n(name), "delay": 1, "apply": 1, "shape": circle(r),
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


GRIT = ["e_g1", "e_g2", "e_g3", "e_g4"]


def build(p, native=False):
    """native: the add-on's copy (addons/league_graves) - the pellets, the knockback and E's cooldown cut."""
    # ------------------------------------------------------------------ True Grit
    def grit(name):
        return combine(*rm(name), flag(name, p["e_t"], defence=p["e_def"], magic_resistance=p["e_mr"]))

    one_more = sw("e_g1", sw("e_g2", sw("e_g3", sw("e_g4", NONE, grit("e_g4")), grit("e_g3")), grit("e_g2")),
                  grit("e_g1"))
    refresh = combine(*[sw(g, grit(g)) for g in GRIT])

    # ------------------------------------------------------------------ W Smoke Screen: from a hit on a champion
    cloud = {"type": "RangePeriodProjectile", "name": n("w_cloud"), "tick": p["w_cloud"], "period": 10,
             "first_delay": 1, "shape": circle(p["w_r"]), "applied_target": "EnemyWithoutTower",
             "applied_effects": [T(debuff("w_in", 12, move_speed_mult=-p["w_in"]))], "end_effects": []}
    impact = burst("w_hit", p["w_r"], "EnemyWithoutTower", [
        magic(p["w_dmg"], 0), debuff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), tsfx("w_hit")])
    blind = burst("w_blind", p["w_r"], "EnemyChampion", [{"type": "BlockAttack", "tick": p["w_blind"]}])
    smoke = combine(flag("w_cd", p["w_cd"]), sfx("w_cast"),
                    delayed(1, lob("w_can", p["w_fly"], "EnemyChampion",
                                   [view("w_smoke"), sfx("w_boom"), impact, blind, cloud])))

    # ------------------------------------------------------------------ attack: the spread
    shell = sw("a_1", combine(*rm("a_1"), anim("attack2", p["atk_dur"]),
                              delayed(p["a_hit"] + 1, on_me({"type": "BlockAttack", "tick": p["a_reload"]}),
                                      sfx("a_reload"))),
               flag("a_1", p["a_keep"]))
    pellet = homing("a_shot", p["a_speed"], p["a_y"], "Enemy",
                    [attack(0, p["a_ratio"]), view("a_hit"), tsfx("a_hit"), refresh,
                     is_champ(sw("w_cd", NONE, smoke))])
    cone = {"type": "RangeEffect", "shape": {"DirDot": {"radius": p["a_cone_r"], "range": p["a_cone_dot"]}},
            "target": "EnemyWithoutTower", "apply_type": {"Forward": {"offset": 1000}},
            "effects": [attack(0, p["a_cone"]), view("a_spread")]}
    root = combine(shell, delayed(p["a_hit"], sfx("a_shot"), pellet, cone))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy", root,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q End of the Line
    boom = {"type": "RangePeriodProjectile", "name": n("q_boom"), "tick": p["q_fuse"] + 2, "period": 1000,
            "first_delay": p["q_fuse"], "shape": circle(p["q_r"]), "applied_target": "EnemyWithoutTower",
            "applied_effects": [T(attack(p["q2_dmg"], p["q2_ratio"])), T(view("q_hit2")), T(tsfx("q_hit2"))],
            "end_effects": []}
    shell_q = line("q_shell", p["q_speed"], p["q_range"], p["q_w"], "EnemyWithoutTower",
                   [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")],
                   end=[view("q_blast"), sfx("q_fuse"), delayed(p["q_fuse"], sfx("q_boom")), boom])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_cast"], "Direction", "EnemyWithoutTower", combine(
        anim("skill", p["q_dur"]), sfx("q_cast"), sfx("vo_q"), delayed(p["q_at"], shell_q)))

    # ------------------------------------------------------------------ skill2: E Quickdraw
    t = p["e_t_move"]
    roll = {"type": "MoveBack", "speed": p["e_dash"] // t, "tick": t}
    dash = {"type": "RushTime", "speed": p["e_dash"] // t, "tick": t, "range": 20000,
            "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": []}
    move = combine(*rm("e_dived"), pick(p["e_near"], "EnemyChampion", flag("e_dived", 1), roll),
                   sw("e_dived", NONE, dash))
    stacks = combine(*rm("e_ch"), pick(p["e_range"], "EnemyChampion", flag("e_ch", 1)),
                     one_more, sw("e_ch", one_more), *rm("e_ch"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower", combine(
        anim("skill2", p["e_dur"]), sfx("e_cast"), sfx("vo_e"), delayed(p["e_at"], move, cview("e_dust")), stacks))

    # ------------------------------------------------------------------ ult: R Collateral Damage
    blast = lob("r_drop", 1, "EnemyWithoutTower",
                [view("r_blast"), sfx("r_boom"),
                 burst("r_cone", p["r_r"], "EnemyWithoutTower", [attack(p["r2_dmg"], p["r2_ratio"]), view("r_hit2")])])
    shell_r = line("r_shell", p["r_speed"], p["r_range"], p["r_w"], "EnemyChampion",
                   [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit"), delayed(1, blast)],
                   penetrate=False)
    recoil = pick(p["r_cast"] + 20000, "EnemyChampion", {"type": "MoveBack", "speed": p["r_back"], "tick": p["r_back_t"]})
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_cast"], "Direction", "EnemyChampion", combine(
        anim("ult", p["r_dur"]), sfx("r_cast"), sfx("vo_r"),
        delayed(p["r_at"], sfx("r_fire"), shell_r, recoil)))

    # ------------------------------------------------------------------ views (tools/art/pack_graves_fx.py)
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                            "tag": tag or name, "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 1}
    views_e = [E("a_hit"), E("a_spread", tag="a_hit"), E("q_hit"), E("q_hit2", tag="a_hit"),
               E("q_blast", BIG, 1, **LATE), E("w_smoke", BIG, 1, **LATE), E("e_dust", FX, -1, **LATE),
               E("r_hit"), E("r_hit2", tag="q_hit"), E("r_blast", BIG, 2, **LATE)]
    views_p = [Pj("a_shot"), Pj("q_shell"), Pj("r_shell"), Pj("w_can")]
    views_b = [{"type": "Animated", "name": n(g), "anim": FX, "tag": "e_grit", "repeat": True, "z": -1}
               for g in GRIT[:1]] + [
               {"type": "Animated", "name": n("w_slow"), "anim": FX, "tag": "w_slow", "repeat": True, "z": 2}]
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    return kit


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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, native=a.native)
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
