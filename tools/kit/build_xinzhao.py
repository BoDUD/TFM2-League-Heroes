"""Build league_xinzhao.data_champion (jungle, Melee) from the parameters P.

    python tools/kit/build_xinzhao.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-05: E with Q folded in / W / R, the challenged one kept beside him):
  attack  A spear thrust (100% AD, crits). The strip is picked on tick 1 (league_diana's Moonsilver Blade) and the hit
          lands in a `Delayed`: Three Talon Strike's thrusts first (q1, q2, q3), else Determination's third swing
          (attack_p), else the plain thrust.
          passive Determination: every third attack (two 240-tick counters p_1, p_2, League's stacks fall off) deals
          p_ratio% AD more and heals him p_heal + p_heal_ratio% AD. Q's thrusts count too.
  skill   E Audacious Charge with Q Three Talon Strike folded in (League's E -> Q): a `Targeting` cast on
          `EnemyWithoutTower` (e_range): `MoveToTarget` (e_speed a tick) onto the target; on arrival every enemy within
          e_rad takes e_dmg + e_ratio% AD (League's magic 60% AP: he has no AP here) and is slowed e_slow% for e_slow_t;
          he gains e_as% attack speed for e_as_t (one instance) and arms Three Talon Strike: his next three attacks within
          q_t ticks deal q_dmg + q_ratio% AD more, the third knocks the target up for q_up ticks.
  skill2  W Wind Becomes Lightning: a `Targeting` cast on `EnemyWithoutTower` (w_range): on tick w_slash_at a slash in
          front of him (a cone of radius w_r, `DirDot` 1000 / w_cone = League's half circle), w1_dmg + w1_ratio% AD; on
          tick w_thrust_at a thrust down the line to the target (`LineRangeProjectile` w_len x w_width), w2_dmg + w2_ratio%
          AD and a w_slow% slow for w_slow_t. League's Challenged mark (a longer E) is left out: nothing reads it.
  ult     R Crescent Guard: a `Targeting` cast on `EnemyChampion` (r_range). On tick r_at the cast target, the challenged
          one, gets a 3-tick `cc_immune` and stays beside him; then every enemy within r_rad takes r_dmg + r_ratio% AD
          (+ r_hp% of a champion's max health: League's 15% of current health, nothing reads it) and every one but the
          challenged is knocked back (r_kb_speed x r_kb_t). For r_t ticks he takes r_red% less damage (League blocks the
          damage from beyond 450 units; the native add-on addons/league_xinzhao_guard does that instead).
Timings from the strips (tools/art/rig_xinzhao.py): the attack, Q1 and Q2 hit on tick 11, Determination on 13, Q3 on 13,
W's slash on 13 and its thrust on 17, R's sweep on 10.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_xinzhao.data_champion")
ID = "league_xinzhao"
FX = "asset/league/effects/league_xinzhao_fx"
BIG = "asset/league/effects/league_xinzhao_big"

# Numbers = the 10-min classic-SDK simulations (jungle against demon, circus_blade, hunter, inquisitor and ninja, three
# lineups, both sides, 24 seeds a batch, 2026-10-06). The draft was +2.01: Determination's heal 20 + 25% -> 15 + 15%,
# E 60% -> 50% and Q 35% -> 30% AD, attack 90 -> 86: +1.17 on placeholder timings. On the strips' timings (W and R
# faster) +1.89 / +2.26 (league_kayn +1.12 / +1.72 on the same seeds); hp 1020 -> 980, W's thrust 80% -> 65% and
# attack 86 -> 82: +1.10 / +1.29 (each alone +1.36 to +1.56 on seeds 1-24).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Xin Zhao:
    # 63 AD +3, 640 +106 hp, 35 armour, 345 move, attack speed 0.645 +3.5%
    "hp": 980, "hp_g": 102, "atk": 82, "atk_g": 18, "def": 32, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000, "ms_g": 11,
    "regen": 2, "regen_g": 1,
    # attack: the strip picked on tick 1, the hit a `Delayed` later
    "atk_range": 26000, "atk_dur": 26, "atk_cd": 60, "a_hit": 11, "a_anim": 24,
    "p_hit": 13, "p_anim": 28, "q1_hit": 11, "q2_hit": 11, "q3_hit": 13, "q_anim": 26,
    # passive Determination (League: every third attack 15-45% AD more, heals 7-92 + 10% AD + 55% AP)
    "p_t": 240, "p_ratio": 40, "p_heal": 15, "p_heal_ratio": 15,
    # Three Talon Strike (League: 16-56 + 40% bonus AD a thrust, the third knocks up 0.75 s, 4 s to use them)
    "q_t": 240, "q_dmg": 20, "q_ratio": 30, "q_up": 45,
    # skill: E Audacious Charge (League: 650 range, 50-170 + 60% AP magic, slow 30% 0.5 s, +40-60% attack speed 5 s,
    # cd 12 s)
    "e_cd": 540, "e_range": 50000, "e_dur": 18, "e_anim": 16, "e_speed": 3500, "e_rad": 20000,
    "e_dmg": 40, "e_ratio": 50, "e_slow": 30, "e_slow_t": 30, "e_as": 40, "e_as_t": 300,
    # skill2: W Wind Becomes Lightning (League: slash 30-70 + 30% AD, thrust 40-200 + 80% AD, 900 range, slow 50% 1.5 s,
    # cd 12-8 s)
    "w_cd": 600, "w_range": 60000, "w_dur": 32, "w_slash_at": 13, "w_thrust_at": 17, "w_r": 32000, "w_cone": 0,
    "w1_dmg": 20, "w1_ratio": 40, "w_len": 60000, "w_width": 8000, "w2_dmg": 40, "w2_ratio": 65, "w_slow": 50,
    "w_slow_t": 90,
    # ult: R Crescent Guard (League: 75-275 + 100% bonus AD + 15% current health, 450 radius, knock-back, 3 s of
    # immunity to damage from beyond 450, cd 120-80 s)
    "r_cd": 3000, "r_range": 30000, "r_dur": 36, "r_at": 10, "r_rad": 36000, "r_dmg": 100, "r_ratio": 100, "r_hp": 10,
    "r_kb_speed": 2500, "r_kb_t": 8, "r_red": 40, "r_t": 180,
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


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects, forward=None):
    return {"type": "RangeEffect", "shape": circle(radius) if not isinstance(radius, dict) else radius,
            "target": target, "apply_type": "AroundCaster" if forward is None else {"Forward": {"offset": forward}},
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ attack: strip, Three Talon Strike, Determination
    def strike(tag, hit_at, q_extra, passive):
        """The attack's tree for one strip: its animation now, the hit `hit_at` ticks later."""
        hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
        if q_extra is not None:
            hit += q_extra
        if passive:
            hit += [attack(0, p["p_ratio"]), on_me(heal(p["p_heal"], p["p_heal_ratio"])), view("p_hit"), tsfx("p_hit"),
                    cview("p_heal"), sfx("p_heal")]
        head = [anim(tag, p["q_anim"] if tag.startswith("q") else p["p_anim"])] if tag != "attack" else []
        swing = [sfx("q_thrust")] if tag.startswith("q") else [sfx("a_swing")]
        return head + swing + [delayed(hit_at, *hit)]

    def counted(build_for):
        """Determination's count: two 240-tick counters, the third attack the passive one."""
        third = combine(*rm("p_1", "p_2"), *build_for(True))
        second = combine(*rm("p_1"), flag("p_2", p["p_t"]), *build_for(False))
        first = combine(flag("p_1", p["p_t"]), *build_for(False))
        return sw("p_2", third, sw("p_1", second, first))

    q_bonus = [attack(p["q_dmg"], p["q_ratio"]), view("q_hit")]
    q1 = counted(lambda pas: [*rm("q_1"), flag("q_2", p["q_t"]),
                              *strike("q1", p["q1_hit"], q_bonus + [tsfx("q1")], pas)])
    q2 = counted(lambda pas: [*rm("q_2"), flag("q_3", p["q_t"]),
                              *strike("q2", p["q2_hit"], q_bonus + [tsfx("q2")], pas)])
    q3 = counted(lambda pas: [*rm("q_3"),
                              *strike("q3", p["q3_hit"], q_bonus + [{"type": "Airborne", "duration": p["q_up"]},
                                                                    view("q3_up"), tsfx("q3")], pas)])
    plain = counted(lambda pas: strike("attack_p" if pas else "attack", p["p_hit"] if pas else p["a_hit"], None, pas))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      sw("q_1", q1, sw("q_2", q2, sw("q_3", q3, plain))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: E Audacious Charge (+ Q armed)
    land = [around(p["e_rad"], "EnemyWithoutTower",
                   [attack(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
                    view("e_hit")]),
            cview("e_land"), sfx("e_hit"),
            *rm("e_as"), flag("e_as", p["e_as_t"], attack_speed_mult=p["e_as"]),
            *rm("q_1", "q_2", "q_3"), flag("q_1", p["q_t"]), sfx("q_arm")]
    charge = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"], "end_effects": land}
    skill = action("skill", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                   combine(anim("skill", p["e_anim"]), cview("e_dash"), sfx("e_cast"), charge))

    # ------------------------------------------------------------------ skill2: W Wind Becomes Lightning
    cone = {"DirDot": {"radius": p["w_r"], "range": p["w_cone"]}}
    slash = around(cone, "EnemyWithoutTower", [attack(p["w1_dmg"], p["w1_ratio"]), view("w_hit")], forward=1000)
    thrust = {"type": "LineRangeProjectile", "name": n("w_thrust"), "width": p["w_width"], "length": p["w_len"],
              "delay": 16, "apply": 2, "applied_target": "EnemyWithoutTower",
              "applied_effects": [T(e) for e in (attack(p["w2_dmg"], p["w2_ratio"]),
                                                 buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
                                                 view("w_hit2"), tsfx("w_hit"))]}
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("w_cast"),
                            delayed(p["w_slash_at"], cview("w_slash"), slash),
                            delayed(p["w_thrust_at"], sfx("w_launch"), thrust)))

    # ------------------------------------------------------------------ ult: R Crescent Guard
    sweep = [
        # the challenged one (the cast target) cannot be knocked back this tick
        buff("r_hold", 3, cc_immune=True), buff("r_chal", 90), tsfx("r_chal"),
        around(p["r_rad"], "EnemyWithoutTower",
               [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"),
                {"type": "Knockback", "speed": p["r_kb_speed"], "tick": p["r_kb_t"]}]),
        around(p["r_rad"], "EnemyChampion", [attack(0, 0, p["r_hp"])]),
        cview("r_sweep"), sfx("r_knock"),
        *rm("r_guard"), flag("r_guard", p["r_t"], damaged_reduce=p["r_red"]), sfx("r_guard"),
        delayed(p["r_t"], sfx("r_end")),
    ]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(sfx("r_cast"), cview("r_tell"), delayed(p["r_at"], *sweep)))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_e = [E("a_hit"), E("p_hit"), E("p_heal", **LATE), E("q_hit"), E("q3_up"),
               E("e_dash", BIG), E("e_land", BIG, -1, **LATE), E("e_hit"),
               E("w_slash", BIG, 2, **LATE), E("w_hit"), E("w_hit2"),
               E("r_tell", BIG), E("r_sweep", BIG, 2, **LATE), E("r_hit")]
    views_p = [{"type": "Animated", "name": n("w_thrust"), "anim": BIG, "tag": "w_thrust", "repeat": False, "z": 2}]
    views_b = [B_("q_1", FX, 3), B_("q_2", FX, 3), B_("q_3", FX, 3), B_("e_slow", FX, -1), B_("w_slow", FX, -1),
               B_("r_chal", FX, 3),
               B_("r_guard", BIG, -1)]
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0,
                 "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": p["regen_g"], "stack": 0,
                   "crit_chance": 0},
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
