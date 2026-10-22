"""Build league_ksante.data_champion (top, Melee tank: the Pride of Nazumah, base and All Out stances) from the
parameters P.

    python tools/kit/build_ksante.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-22: TOP, layout A - Q / W / R, All Out with an action set of its own; 「有连招要做连
招」). TFM2 has three active slots: Ntofo Strikes (Q) is `skill`, Path Maker (W) `skill2`, All Out (R) the `ult`.
Footwork (E)'s dash shield rides W's dash; the passive marks for the attack. The stances work like league_shyvana's
forms: every action reads the All Out buff `ao` first and plays that stance's own tags (ao_*, CasterAnimation; idle,
run, hit and death are the add-on's view swap, league_gnar's way).
  passive Dauntless Instinct (血性本能): League's abilities mark their targets for his next attack. Here every Q, W or R
          that lands sets the caster flag `mark` (p_t ticks) and his next attack hit adds p_dmg + p_hp% of the
          target's max health (League: 1-2% of it plus a flat part).
  attack  A swing of the ntofos (100% AD on `Enemy`); All Out: ao_attack, the stance's numbers in `ao`.
  skill   Q Ntofo Strikes (无双陀斧, cooldown q_cd, the slot's own): a `Targeting` cast on `EnemyWithoutTower`
          (q_range). Q1 / Q2 strike a short line ahead (q_off / q_rad): q_dmg + q_ratio% AD + q_hp% of his max health
          (League's 40% bonus armour and magic resistance: no effect reads armour, so his health), slowed q_slow% for
          q_slow_t. A strike that hits anything is one stack (`q_s1`, then `q_s2`, each q_win ticks); at two stacks
          the next Q is Q3: a shockwave line (q3_range, q3_w) that pulls every enemy it crosses toward him (`Pull`)
          for q3_dmg + q3_ratio% AD + q3_hp%. Tags skill (Q1), skill_b (Q2), skill_c (Q3); ao_skill / ao_skill_b /
          ao_skill_c in All Out. All Out caps his skill cooldowns (`ao` skill_cooldown_mult ao_cdr: League's Q -33%).
  skill2  W Path Maker (辟路先锋, cooldown w_cd): a `Targeting` cast on `EnemyChampion` (w_range). He braces for
          w_charge ticks taking w_dr% less damage (All Out ao_w_dr%), shielded e_sh + e_ratio% AD (Footwork's
          shield), then rams onto the champion (`MoveToTarget`): round him (w_r) w_dmg + w_ratio% AD + w_thp% of each
          target's max health, a knockback and a w_stun-tick stun. All Out: no knockback or stun, ao_w_thp% instead
          and a quicker brace (ao_w_charge). Tags skill2 (brace), skill2_dash; ao_skill2 / ao_skill2_dash.
  ult     R All Out (傲岸雄姿, cooldown r_cd): a `Targeting` cast on `EnemyChampion` (r_range). He kicks the champion
          away (r_at): r_dmg + r_ratio% AD, a knockback (r_kb_t ticks) and a r_stun-tick stun, then dashes after it
          (r_chase ticks later) and slams it on arrival: r2_dmg + r2_ratio% AD + r2_hp% of his max health. He goes
          All Out for ao_t ticks (`ao`): ao_atk% attack, ao_as% attack speed, ao_vamp% lifesteal, ao_pen defence
          penetration, skill cooldowns capped (ao_cdr), and ao_def% less armour and magic resistance (League: 85% of
          the bonus resistances lost). Tags ult (the kick), ult_dash (the chase), the slam in ao_attack's swing.
          The kick sends the champion twice as far as it first did (r_kb 3000 -> 6000, 2026-10-22, the user: 「踢得更远，把对面
          的人踢离他的队友」), the chase faster (r_speed 6000) and reaching the whole kick (range r_range + the knockback's
          r_kb x r_kb_t + 30000).
  combos  Q -> Q -> Q3 (the stacks), Q3 -> W (无双陀斧三段拉人接辟路先锋): a Q3 that reaches a champion opens `w_go` for
          win_w ticks, and a W cast in it skips most of the brace (w_fast). R -> W (傲岸雄姿接辟路先锋): the slam opens
          `w_go` for win_w ticks the same way and W's cooldown left drops to a tenth (r_cdr: W ready about a second after the
          slam) (All Out's ram). W -> Q (辟路先锋晕眩接无双陀斧): a ram that hits a champion
          is one more Q stack. Every ability that lands arms the passive for the next attack (Q -> A).
Timings: the frames' (tools/art/rig_ksante.py MS; a frame's start in ticks = ms x 0.06): a_hit 10 (the thrust, 167
ms), q_at 10, q3_rel 12, w_charge 45 / ao_w_charge 24 (the braces), w_dash_dur 18, r_at 12 (the bash), r_dash_dur 22,
and the actions' lengths. Numbers: League 16.20 (CommunityDragon ksante.bin) read into the Melee tank range;
balanced on the classic-SDK simulations (kd.py --lane 0 against fighter, executioner, knight, berserker,
lancer and pole_warrior, C:/t/ks_sim, 2026-10-22; league_ornn +1.86 on seeds 1-8 the same day): the draft (hp 1150, Q 30 +
60%, Q3 40, W 20 + 50%, R 80 / 60, All Out -40% resistances, R 60 s, W 12 s) -0.46; more damage +0.38; then All Out -25%,
R 50 s, W 11 s, def 42 = P +1.18 / +1.56 (seeds 1-8 / 9-16); a tankier W (35% reduction, shield 100) on top +0.57.
Combos measured in traces (trace.exe, seeds 3 and 5): the Q3 -> W window mostly opens right after a W (the AI plays
W -> Q -> Q3), so only R -> W got a refund (r_cdr); with it +1.90, then Q 35, W 30, the slam 60 = P +1.28 / +2.22 (seeds 1-8 / 9-16).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_ksante.data_champion")
ID = "league_ksante"
FX = "asset/league/effects/league_ksante_fx"
BIG = "asset/league/effects/league_ksante_big"

# League's K'Sante (16.20, CommunityDragon ksante.bin): 625 +120 hp, 64 AD, 36 +5.2 armour, 30 +2.1 mr, 330 move, 150
# range, attack speed 0.688. P: marks 4 s, the next attack +1-2% max health. Q: 465 x 100 line, 40-190 + 40% bonus
# armour and mr, 80% slow decaying over 0.5 s; two stacks within 6 s -> Q3 a 700 shockwave pulling enemies 300; cd 3.5
# (down to 2 with bonus resistances), All Out -33%. W: 0.4-1 s charge, 25% damage reduction (All Out 70%), a 100-450
# dash, 15-165 + 8% of the target's max health, knockback and stun 0.5-1.75 s (All Out: none, +10-80% damage); cd
# 16-12. E: a 550 dash and 27-240 + 13.5% bonus health shield 2 s. R: 350 range, 45-220 kick knocking back (stun 0.25 s,
# 0.5 s into a wall), the slam 45-220 + 5% bonus health; All Out 15 s: 20% omnivamp, +20-120% attack speed, 50% armour
# penetration, 85% of bonus resistances and 35% of bonus health lost; cd 120-80.
P = {
    # stats (Melee tank: league_ornn 1100 +115 hp, 80 +8 attack, 38 +9 def; league_sion 1400 +140, 88 +16, 42 +8)
    "hp": 1220, "hp_g": 115, "atk": 82, "atk_g": 9, "def": 42, "def_g": 8, "mr": 30, "mr_g": 4, "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 72, "a_hit": 10, "a_speed": 20000,
    # passive Dauntless Instinct
    "p_t": 240, "p_dmg": 15, "p_hp": 2,
    # Q Ntofo Strikes
    "q_cd": 240, "q_range": 30000, "q_dur": 26, "q_at": 10, "q_off": 14000, "q_rad": 15000,
    "q_dmg": 35, "q_ratio": 70, "q_hp": 2, "q_slow": 50, "q_slow_t": 30, "q_win": 360,
    "q3_dur": 30, "q3_rel": 12, "q3_speed": 4500, "q3_range": 70000, "q3_w": 9000,
    "q3_dmg": 55, "q3_ratio": 70, "q3_hp": 3, "q3_pull": 1500, "q3_pull_t": 12,
    # W Path Maker (+ Footwork's shield)
    "w_cd": 660, "w_range": 45000, "w_charge": 45, "w_fast": 8, "w_dash_dur": 18, "w_speed": 4500,
    "w_dr": 25, "e_sh": 70, "e_ratio": 50, "e_sh_t": 120, "w_r": 16000,
    "w_dmg": 30, "w_ratio": 60, "w_thp": 6, "w_kb": 2500, "w_kb_t": 8, "w_stun": 50,
    # R All Out
    "r_cd": 3000, "r_range": 30000, "r_dur": 34, "r_at": 12, "r_dmg": 100, "r_ratio": 80, "r_kb": 6000, "r_kb_t": 15,
    "r_stun": 30, "r_chase": 16, "r_speed": 6000, "r_dash_dur": 22, "r2_dmg": 60, "r2_ratio": 60, "r2_hp": 4,
    # the All Out stance
    "ao_t": 900, "ao_atk": 20, "ao_as": 40, "ao_vamp": 20, "ao_pen": 30, "ao_def": -25, "ao_cdr": 50,
    "ao_w_dr": 50, "ao_w_charge": 24, "ao_w_thp": 9,
    # the combo windows (Q3 -> W, R -> W)
    "win_w": 180, "r_cdr": 900,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
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


def attack(dmg, ratio, hp=0, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def ahead(offset, radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": {"Forward": {"offset": offset}},
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def stance(all_out, base):
    """All Out's version while `ao` holds, the base stance's otherwise."""
    return sw("ao", all_out, base)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    slow = lambda name, pct, t: buff(name, t, move_speed_mult=-pct)
    mark = refresh("mark", p["p_t"])          # the passive: his next attack hits harder
    # a combo's refund: a 2-tick skill_cooldown_mult caps the skills' cooldowns left at 100 / (100 + m) of their
    # cooltime (W is the one that matters), ult_cooldown_mult -m keeps the ult's own (champion-data section 5)
    refund = lambda m: refresh("cdr", 2, skill_cooldown_mult=m, ult_cooldown_mult=-m)

    # ------------------------------------------------------------------ attack (the passive's mark)
    marked = combine(*rm("mark"), attack(p["p_dmg"], 0, 0, p["p_hp"]), view("p_hit"), tsfx("p_hit"))
    on_hit = [attack(0, 100), sw("mark", marked), view("a_hit"), tsfx("a_hit")]
    swing = delayed(p["a_hit"] - 1, homing("a_hit", p["a_speed"], "Enemy", on_hit))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(stance(combine(anim("ao_attack", p["atk_dur"]), sfx("ao_a")), sfx("a")), swing),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q Ntofo Strikes
    # a strike that hits anything leaves a 2-tick `q_hit`; a tick later it becomes one stack (q_s1 -> q_s2)
    stack_up = sw("q_s1", combine(*rm("q_s1"), flag("q_s2", p["q_win"])), refresh("q_s1", p["q_win"]))
    took = delayed(1, sw("q_hit", combine(*rm("q_hit"), stack_up, mark)))
    strike = ahead(p["q_off"], p["q_rad"], "EnemyWithoutTower",
                   [attack(p["q_dmg"], p["q_ratio"], p["q_hp"]), slow("q_slow", p["q_slow"], p["q_slow_t"]),
                    refresh("q_hit", 2), view("q_hit"), tsfx("q_hit")])
    q12 = combine(sw("q_s1", stance(anim("ao_skill_b", p["q_dur"]), anim("skill_b", p["q_dur"])),
                     stance(anim("ao_skill", p["q_dur"]), anim("skill", p["q_dur"]))),
                  sfx("q"), voice("vo_q", p), delayed(p["q_at"] - 1, strike, took))
    # Q3: the shockwave; a champion it crosses opens Q3 -> W
    q3_hits = [attack(p["q3_dmg"], p["q3_ratio"], p["q3_hp"]), {"type": "Pull", "speed": p["q3_pull"],
                                                                 "tick": p["q3_pull_t"]},
               view("q3_hit"), tsfx("q3_hit")]
    q3_champ = line("q3_twin", p["q3_speed"], p["q3_range"], p["q3_w"], "EnemyChampion", False,
                    [refresh("w_go", p["win_w"]), mark])
    q3 = combine(*rm("q_s2"), stance(anim("ao_skill_c", p["q3_dur"]), anim("skill_c", p["q3_dur"])), sfx("q3"),
                 voice("vo_q3", p),
                 delayed(p["q3_rel"] - 1, line("q3_wave", p["q3_speed"], p["q3_range"], p["q3_w"], "EnemyWithoutTower",
                                               True, q3_hits), q3_champ))
    skill = action("skill", max(p["q_dur"], p["q3_dur"]), p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_s2", q3, q12))

    # ------------------------------------------------------------------ W Path Maker (+ Footwork's shield)
    # the ram, written once: All Out (read on the hit) swaps the knockback and stun for more of the target's health
    cc = combine({"type": "Knockback", "speed": p["w_kb"], "tick": p["w_kb_t"]}, {"type": "Stun", "duration": p["w_stun"]})
    hit = [attack(p["w_dmg"], p["w_ratio"], 0, p["w_thp"]),
           stance(attack(0, 0, 0, p["ao_w_thp"] - p["w_thp"]), cc), view("w_hit"), tsfx("w_hit")]
    # W -> Q: a ram that reaches a champion is one more Q stack (and arms the passive)
    ram = [around(p["w_r"], "EnemyWithoutTower", hit), pick(p["w_r"], "EnemyChampion", stack_up, mark),
           cview("w_land"), sfx("w_land")]
    dash = alive(stance(anim("ao_skill2_dash", p["w_dash_dur"]), anim("skill2_dash", p["w_dash_dur"])), sfx("w_dash"),
                 {"type": "MoveToTarget", "speed": p["w_speed"], "range": p["w_range"] + 20000, "end_effects": ram})

    def go(charge, pre):
        return combine(anim(pre + "skill2", charge), delayed(charge - 1, dash))
    brace = combine(refresh("w_dr", p["w_charge"] + p["w_dash_dur"], damaged_reduce=p["w_dr"]),
                    stance(refresh("w_dr", p["ao_w_charge"] + p["w_dash_dur"], damaged_reduce=p["ao_w_dr"]), None),
                    on_me(shield(p["e_sh"], p["e_ratio"], p["e_sh_t"])), sfx("w"), voice("vo_w", p), cview("w_brace"))
    # Q3 -> W and R -> W: a cast in the window (`w_go`) rams almost at once
    skill2 = action("skill2", p["w_charge"] + p["w_dash_dur"], p["w_cd"], 1, p["w_range"], "Targeting",
                    "EnemyChampion",
                    combine(brace, sw("w_go", combine(*rm("w_go"), stance(go(p["w_fast"], "ao_"), go(p["w_fast"], ""))),
                                      stance(go(p["ao_w_charge"], "ao_"), go(p["w_charge"], "")))))

    # ------------------------------------------------------------------ R All Out
    all_out = combine(*rm("ao"), flag("ao", p["ao_t"], attack_mult=p["ao_atk"], attack_speed_mult=p["ao_as"],
                                      vamp=p["ao_vamp"], defence_penetration=p["ao_pen"],
                                      defence_mult=p["ao_def"], magic_resistance_mult=p["ao_def"],
                                      skill_cooldown_mult=p["ao_cdr"], ult_cooldown_mult=-p["ao_cdr"]),
                      cview("ao_on"), sfx("ao_on"))
    slam = [attack(p["r2_dmg"], p["r2_ratio"], p["r2_hp"]), view("r_slam"), tsfx("r_slam"), mark,
            refresh("w_go", p["win_w"]), refund(p["r_cdr"])]
    chase = combine(anim("ult_dash", p["r_dash_dur"]), sfx("r_dash"),
                    {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + p["r_kb"] * p["r_kb_t"] + 30000,
                     "end_effects": slam})
    kick = homing("r_kick", 100000, "EnemyChampion",
                  [attack(p["r_dmg"], p["r_ratio"]), {"type": "Knockback", "speed": p["r_kb"], "tick": p["r_kb_t"]},
                   {"type": "Stun", "duration": p["r_stun"]}, view("r_hit"), tsfx("r_hit")])
    r_go = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                   delayed(p["r_at"] - 1, kick, all_out),
                   delayed(p["r_at"] + p["r_chase"] - 1, alive(chase)))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", r_go)

    # ------------------------------------------------------------------ views (the step-3 effects pack)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("q3_wave", BIG)]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("q3_hit"), E("w_brace", BIG, 3), E("w_land", BIG, -1),
               E("w_hit"), E("r_hit"), E("r_slam", BIG), E("ao_on", BIG, 3)]
    views_b = [B_("mark", FX, 3, "p_mark"), B_("q_slow", FX, 3), B_("ao", BIG, -1, "ao_aura")]
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "Shield", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
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
