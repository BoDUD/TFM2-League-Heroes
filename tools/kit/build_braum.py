"""Build league_braum.data_champion (support, Melee tank, magic skills) from the parameters P.

    python tools/kit/build_braum.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-12: support / melee tank; Q as skill, E Unbreakable and W Stand Behind Me sharing
skill2, R Glacial Fissure, the passive in the main pack plus a native add-on addons/league_braum, the pros' combos):
  passive Concussive Blows (震荡猛击): League stacks a mark on the champion his attacks (and then his allies' attacks) hit;
          the fourth stack stuns and deals magic damage, then for a while the champion takes no new stacks and his
          attacks deal bonus magic damage. The data reads no stacks on a target, so the count is his (league_darius
          Hemorrhage's way): his attacks and Q on enemy champions (hidden champion-only twins) climb p1 -> p2 -> p3
          (p_hold ticks each, refreshed); the fourth stuns p_stun ticks and deals p_dmg + p_ap% AP, then for p_lock
          ticks no hit stacks and his attacks on champions add p_extra + p_extra_ap% AP. Every stack shows the mark
          picture (p_mark) on the champion. With native=1 the add-on keeps the stacks on each champion
          (league_braum:blow from his attacks, league_braum:bite from Q) and its passive counts his allies' attacks
          on a marked champion too (League's rule).
  attack  A shield punch, the hit on tick atk_st.
  skill   Q Winter's Bite (寒冬之咬): a `Targeting` cast on `EnemyWithoutTower` (q_range, waves and camps too): on q_at the
          ice flies (q_speed) and deals q_dmg + q_ap% AP + q_hp% of his maximum health (League: 2.5%), slows q_slow1%
          for q_slow1_t, then q_slow2% for q_slow2_t (League: 70% fading to 30% over 2 s), and stacks the passive on a
          champion. The pros' R -> Q: cast within r_combo of a fissure that threw up a champion, the ice leaves at once.
  skill2  E Unbreakable (坚不可摧) and W Stand Behind Me (挺身而出) share the slot, each on its own cooldown (caster flags
          e_cd and w_cd; the slot itself waits only s2_cd). A `None` cast on `EnemyChampion` (s2_range):
          - an allied champion within w_range in crowd control and W ready: he leaps to it (MoveToTarget w_speed),
            both get w_def armour and w_mr magic resistance for w_t ticks, and with E ready he raises the shield
            on landing (the pros' W -> E);
          - else E ready: he raises the shield for e_t ticks: e_red% less damage (League: the first hit from the
            front negated, 30-60% after it, from the front only), an e_sh + e_sh_ap% AP shield for the first hit, and
            allied champions within e_ally_r e_ally_red% less damage (League: projectiles toward the allies behind
            him hit the shield). With native=1 the add-on's passive keeps the shield toward the enemies: only damage
            from that side is cut, and allies behind him are covered;
          - else W ready: he leaps to an allied champion within w_range.
  ult     R Glacial Fissure (冰川裂隙): a `Targeting` cast on `EnemyChampion` (r_range): on r_at he slams the ground; a
          wave runs r_len toward the target (r_speed): every enemy it passes takes r_dmg + r_ap% AP and is thrown up
          r_up ticks, the first champion r_up1 ticks (League: 1-1.5 s against 0.6 s); a fissure of r_n slow fields
          (r_zr round, r_slow% slow while inside, r_zone ticks) stays on the line. The add-on's AI hook turns his
          cast to the champion whose line holds the most enemy champions.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_braum.data_champion")
ID = "league_braum"
FX = "asset/league/effects/league_braum_fx"
BIG = "asset/league/effects/league_braum_big"

# Timings from the strips (assets/source/braum/frames/frames.json, Codex's step 2 after League's clips): attack 430 ms, the
# bash lands on frame 4 (210 ms, tick 13); Q 440 ms, the ice on frame 4 (220 ms, tick 13); E's raise 400 ms; W's leap
# 370 ms; R 590 ms, the shield hits the ground on frame 5 (320 ms, tick 19).
# Numbers = candidate d3 of the 10-min classic-SDK simulations (Temp/br_sim/sim/kd.py, support lane against the base
# priest, monk, bard, pythoness and spirit caller, three lineups, both sides, 2026-10-12): +0.32 on seeds 1-24, +0.21 on
# 25-48 (league_alistar +0.84 / +0.42, league_taric +1.27 / +1.24, league_leona -0.17 on 1-24). The draft d0 was -0.67
# (Q 60+40, the passive 40+40, R 100+60, hp 1100, E 40%, W 20/20, stun 1 s).
P = {
    # stats (the pack's tank supports: league_alistar hp 1100 +120, def 38, mr 28, atk 80, interval 80, range 25000);
    # League's Braum: 610 +112 hp, 55 AD, 35 armour, 32 mr, 335 move, 125 range
    "hp": 1200, "hp_g": 120, "atk": 78, "atk_g": 6, "mp": 25, "mp_g": 15, "def": 40, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 80, "atk_st": 13,
    # passive Concussive Blows (League: 4 stacks within 4 s each; stun 1.25-1.75 s + 16-122 magic; then 8 s without new
    # stacks, his attacks +20% of that damage)
    "p_hold": 240, "p_stun": 75, "p_dmg": 70, "p_ap": 60, "p_lock": 480, "p_extra": 12, "p_extra_ap": 10,
    # Q Winter's Bite (League: 1050 range, speed 1700, 75-255 + 2.5% max hp, slow 70% fading to 30% over 2 s, cd 8-6 s)
    "q_cd": 480, "q_range": 70000, "q_dur": 26, "q_at": 13, "q_speed": 3600, "q_dmg": 90, "q_ap": 60, "q_hp": 2,
    "q_slow1": 70, "q_slow1_t": 40, "q_slow2": 35, "q_slow2_t": 80,
    # skill2 slot: E Unbreakable + W Stand Behind Me
    "s2_cd": 60, "s2_range": 45000,
    # E Unbreakable (League: 3-4 s, first hit 0, 30-60% less after it, cd 18-8 s)
    "e_cd": 840, "e_t": 210, "e_red": 50, "e_sh": 60, "e_sh_ap": 40, "e_ally_r": 25000, "e_ally_red": 20, "e_anim": 24,
    # W Stand Behind Me (League: 650 leap, 15-45 armour / mr (+ a share of his bonus) 3 s for both, cd 13-7 s)
    "w_cd": 600, "w_range": 60000, "w_speed": 4500, "w_def": 30, "w_mr": 30, "w_t": 180, "w_anim": 22,
    # R Glacial Fissure (League: 1250 line, 150-450 + 60% AP, knock-up 1-1.5 s first / 0.6 s, slow zone 40-70% 4 s,
    # cd 130-85 s)
    "r_cd": 3600, "r_range": 75000, "r_dur": 36, "r_at": 19, "r_len": 80000, "r_speed": 9000, "r_w": 9000,
    "r_dmg": 160, "r_ap": 70, "r_up": 36, "r_up1": 75, "r_n": 4, "r_zr": 10000, "r_slow": 40, "r_zone": 240,
    "r_combo": 90,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_braum: per-champion stacks (allies' attacks too), the directional shield
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
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


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


def magic(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ passive Concussive Blows (his count)
    proc = combine(*rm("p1", "p2", "p3"), refresh("p_lock", p["p_lock"]), {"type": "Stun", "duration": p["p_stun"]},
                   magic(p["p_dmg"], p["p_ap"]), buff("p_stun", p["p_stun"]), view("p_proc"), tsfx("p_proc"))
    mark = buff("p_mark", p["p_hold"])
    ladder = sw("p3", proc,
                sw("p2", combine(refresh("p3", p["p_hold"]), refresh("p2", p["p_hold"]), refresh("p1", p["p_hold"]),
                                 mark),
                   sw("p1", combine(refresh("p2", p["p_hold"]), refresh("p1", p["p_hold"]), mark),
                      combine(refresh("p1", p["p_hold"]), mark))))
    stack = sw("p_lock", NONE, ladder)
    bonus = sw("p_lock", combine(magic(p["p_extra"], p["p_extra_ap"]), view("p_extra")))
    if native:   # the add-on keeps the stacks on each champion (his allies' attacks add them too)
        a_stack, q_stack = [{"type": "Native", "effect_ref": "league_braum:blow"}], {"type": "Native",
                                                                                     "effect_ref": "league_braum:bite"}
    else:
        a_stack, q_stack = [bonus, stack], stack

    # ------------------------------------------------------------------ attack (the champion-only twin stacks)
    blow = homing("a_twin", 30000, "EnemyChampion", a_stack)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit"),
                                                      blow)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Winter's Bite
    q_hits = [magic(p["q_dmg"], p["q_ap"], p["q_hp"]), buff("q_slow", p["q_slow1_t"], move_speed_mult=-p["q_slow1"]),
              delayed(p["q_slow1_t"], buff("q_slow", p["q_slow2_t"], move_speed_mult=-p["q_slow2"])),
              view("q_hit"), tsfx("q_hit")]
    throw = combine(sfx("q"), homing("q_ice", p["q_speed"], "EnemyWithoutTower", q_hits),
                    homing("q_twin", p["q_speed"], "EnemyChampion", [q_stack]))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(voice("vo_q", p), sw("r_combo", combine(*rm("r_combo"), throw),
                                                delayed(p["q_at"] - 1, throw))))

    # ------------------------------------------------------------------ skill2: E Unbreakable / W Stand Behind Me
    raise_ = combine(flag("e_cd", p["e_cd"]), refresh("e_on", p["e_t"], damaged_reduce=0 if native else p["e_red"]),
                     on_me({"type": "Shield", "amount": p["e_sh"], "attack_ratio": 0, "ap_ratio": p["e_sh_ap"],
                            "tick": p["e_t"]}),
                     None if native else around(p["e_ally_r"], "AllyNotSelf",
                                                [buff("e_ally", p["e_t"], damaged_reduce=p["e_ally_red"])]),
                     anim("skill2", p["e_anim"]), cview("e_raise"), sfx("e"), voice("vo_e", p))
    e_cast = sw("e_cd", NONE, raise_)

    def leap(target):
        landing = [buff("w_guard", p["w_t"], defence=p["w_def"], magic_resistance=p["w_mr"]), view("w_land"),
                   on_me(refresh("w_self", p["w_t"], defence=p["w_def"], magic_resistance=p["w_mr"])),
                   sfx("w_land"), e_cast]
        go = combine(flag("w_cd", p["w_cd"]), anim("w_leap", p["w_anim"]), cview("w_dash"), sfx("w"),
                     voice("vo_w", p),
                     {"type": "MoveToTarget", "speed": p["w_speed"], "range": p["w_range"] + 40000,
                      "end_effects": landing})
        return pick(p["w_range"], target, go)

    cc = combine(*rm("w_cc"), pick(p["w_range"], "AllyChampionInCC", flag("w_cc", 1)))
    s2 = sw("w_cd", e_cast,
            combine(cc, sw("w_cc", combine(*rm("w_cc"), leap("AllyChampionInCC")),
                           sw("e_cd", leap("AllyNotSelf"), e_cast))))
    skill2 = action("idle", 3, p["s2_cd"], 1, p["s2_range"], "None", "EnemyChampion", s2, key="skill2")

    # ------------------------------------------------------------------ ult: R Glacial Fissure
    struck = [magic(p["r_dmg"], p["r_ap"]), {"type": "Airborne", "duration": p["r_up"]}, view("r_hit"), tsfx("r_hit")]
    first = [{"type": "Airborne", "duration": p["r_up1"]}, on_me(refresh("r_combo", p["r_combo"]))]
    step = p["r_len"] // p["r_n"]
    crack = [line(f"r_seg{i}", 400000, step * i, 1, "EnemyWithoutTower", True, [],
                  end=[view("r_crack"), field("r_field", p["r_zr"], p["r_zone"], 10, "EnemyWithoutTower",
                                              [buff("r_slow", 12, move_speed_mult=-p["r_slow"])])])
             for i in range(1, p["r_n"] + 1)]
    slam = combine(sfx("r_hit"), cview("r_slam"),
                   line("r_wave", p["r_speed"], p["r_len"], p["r_w"], "EnemyWithoutTower", True, struck),
                   line("r_first", p["r_speed"], p["r_len"], p["r_w"], "EnemyChampion", False, first), *crack)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r"), voice("vo_r", p), delayed(p["r_at"] - 1, slam)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("q_ice"), P_("r_wave", BIG, 2)]
    views_e = [E("a_hit"), E("p_proc"), E("p_extra"), E("q_hit"), E("e_raise", FX, 3), E("w_dash", FX, 1),
               E("w_land"), E("r_slam", BIG, 1, False), E("r_crack", BIG, -1, False), E("r_hit")]
    views_b = [B_("p_mark", FX, 3), B_("p_stun", FX, 3), B_("q_slow", FX, -1), B_("e_on", BIG, 3),
               B_("e_ally", FX, 3), B_("w_guard", FX, 3), B_("w_self", FX, 3, "w_guard"),
               B_("r_slow", FX, -1, "q_slow")]   # his own guard and the fissure's slow: the same pictures
    kit = {
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
    if native:
        kit["passive"] = {"passive_ref": "league_braum:heart",
                          "params": {"hold": p["p_hold"], "stun": p["p_stun"], "dmg": p["p_dmg"], "ap": p["p_ap"],
                                     "lock": p["p_lock"], "extra": p["p_extra"], "extra_ap": p["p_extra_ap"],
                                     "e_red": p["e_red"], "e_ally": p["e_ally_red"], "e_ally_r": p["e_ally_r"]}}
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
