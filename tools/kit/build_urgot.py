"""Build league_urgot.data_champion (top, Melee juggernaut) from the parameters P.

    python tools/kit/build_urgot.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-16: top lane, W folded into Q and E, the main pack plus a native add-on
addons/league_urgot, PPU 1.5 - 「方案可以，全按推荐做（上单，W 并进 Q/E，做附加包，PPU 1.5）」):
  passive Echoing Flames (回响烈焰): six shotgun legs take turns. A basic attack or a Purge shot fires the next leg when
          it is ready (one caster flag leg_cd: League's per-leg cooldown over six legs, leg_t0 ticks below level 3 and
          leg_t from it - SwitchByLevel3 is the only level the data reads): a cone (DirDot p_r / p_cone) toward the
          target, p_ratio% AD + p_hp% of each unit's maximum health. With native=1 the add-on picks the leg by the
          target's real direction and keeps six cooldowns (League's rule).
  attack  A shot from the cannon arm (atk_range: League's 350 against the usual 125-175 and 550 of a marksman).
          With Purge on, every attack is a machine-gun shot instead (w_dmg + w_ratio% AD, half his on-hit: the leg
          only) at w_as% more attack speed, and he moves w_slow% slower.
  skill   Q Corrosive Charge (腐蚀电荷): a `Targeting` cast on `EnemyWithoutTower` (q_range, waves and camps too); a
          hidden lob onto the target's spot as it stands at the cast (dodged by walking off: league_pantheon's lock)
          lands after q_travel, the blast q_apply ticks later (League's 0.3 s fuse): q_dmg + q_ratio% AD within q_r and
          a q_slow% slow for q_slow_t. A hit opens Purge.
  W       Purge (净除), no slot of its own: a Q hit or an E catch opens it (at most once every w_gap ticks) for w_t ticks
          (League: 4 s; a permanent toggle at rank 5).
  skill2  E Disdain (鄙弃): a `Targeting` cast on `EnemyChampion` (e_range; a Direction cast holding a dash would make the
          game's AI fire it on the move, champion-data 7). A shield of e_sh + e_sh_ratio% AD for e_sh_t from the
          start, a charge onto the champion (MoveToTarget e_speed); on the catch e_dmg + e_ratio% AD, a stun of e_stun,
          and e_fling ticks later he hurls it over himself (a Pull through him: speed e_pull x e_pull_t, forced
          movement = crowd control for league_yasuo's R). The catch opens Purge.
  ult     R Fear Beyond Death (超越死亡的恐惧): a `Targeting` cast on `EnemyChampionRecentlyAttacked` (r_range: a champion
          his team is already hurting, the stand-in for a wounded one; nothing in the data reads current health).
          A hidden lob locks where it stands r_aim ticks before the drill leaves; the drill (LinearProjectile, stops on
          the first enemy champion, minions let through like League's) deals r_dmg + r_ratio% AD, slows r_slow% and
          leashes it for r_t ticks; then he reels it in and executes it: r_ex% of its maximum health as true damage
          (League's execute line is 25% of maximum health: a champion under it dies, any other takes that much).
          An execute that kills makes the enemies within r_fear_r flee for r_fear ticks (league_darius R's kill
          trigger). With native=1 the add-on reels in only a champion under 25% health (League's recast) and kills
          it outright; the others keep the leash and the drill's damage.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_urgot.data_champion")
ID = "league_urgot"
FX = "asset/league/effects/league_urgot_fx"
BIG = "asset/league/effects/league_urgot_big"

# Numbers: the first draft from League's ratios inside the base Melee ranges (champion-data 2), to be tuned by 10-min
# classic-SDK simulations (Temp/ur_sim/sim/kd.py --lane 0 against fighter, executioner, lancer, pole_warrior, knight,
# berserker, three lineups, both sides, two batches of seeds). The draft u1 (hp 1080, atk 90, legs 50% AD + 3% max hp every
# 120 / 300 ticks, E stun 90 shield 80 + 60%, Q 70 + 70%) +5.16 on 12 seeds (league_darius +1.71, league_pantheon +1.40);
# taken apart on 8: no W +5.90 (Purge's gun is a net loss), no legs +3.00, no E +2.47, no R damage +4.93, range 30000
# +5.24; legs, E, Q and his stats cut step by step: +3.31, +2.36, +2.38, then here (hp 960, def 32) +1.53.
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30, mr 25, move 1000, range 25000, attack every 65 ticks);
    # League's Urgot: 655 +102 hp, 63 AD +5, 36 armour +5.2, 32 mr, 330 move, 350 range, 0.625 attack speed
    "hp": 960, "hp_g": 108, "atk": 86, "atk_g": 17, "def": 32, "def_g": 8, "mr": 28, "mr_g": 4, "ms": 980, "ms_g": 10,
    "atk_range": 38000, "atk_dur": 26, "atk_cd": 72, "a_st": 8, "shot_speed": 6000, "shot_y": -2000,
    # passive Echoing Flames (League: 6 legs, 30/20/10/5/2.5 s each by level, cone 700 x 60 deg, 40-100% AD + 2-6% max hp)
    "leg_t0": 480, "leg_t": 180, "p_r": 52000, "p_cone": 850, "p_ratio": 40, "p_hp": 1, "p_len": 52000, "p_w": 14000,
    # Q Corrosive Charge (League: 800 range, 210 radius, 0.3 s fuse, 25-205 + 70% AD, slow 45-65% 1.25 s, cd 10-8 s)
    "q_cd": 480, "q_range": 75000, "q_dur": 20, "q_st": 6, "q_travel": 16, "q_apply": 12, "q_r": 21000,
    "q_dmg": 50, "q_ratio": 55, "q_slow": 45, "q_slow_t": 75,
    # W Purge (League: 4 s, 3 shots a second at 12 + 20-34% AD, on-hit at 50%, -125 move speed, cd 12-0 s)
    "w_t": 240, "w_gap": 360, "w_as": 180, "w_slow": 15, "w_dmg": 14, "w_ratio": 45,
    # E Disdain (League: 475 range, shield 55-135 + 135% bonus AD 4 s, 90-210 + 100% bonus AD, stun 1.5 s, the fling
    # 0.25 s after, cd 16-14 s)
    "e_cd": 960, "e_range": 46000, "e_dur": 26, "e_speed": 3200, "e_sh": 60, "e_sh_ratio": 40, "e_sh_t": 240,
    "e_dmg": 40, "e_ratio": 80, "e_stun": 60, "e_fling": 15, "e_pull": 2600, "e_pull_t": 10,
    # R Fear Beyond Death (League: 2500 range, 3200 speed, 100-350 + 50% bonus AD, leash 4 s with a slow to 75%,
    # recast under 25% max hp: a 1.5 s reel-in then the execute, nearby enemies flee 1.5 s, cd 100-70 s)
    "r_cd": 3000, "r_range": 110000, "r_dur": 30, "r_st": 8, "r_aim": 4, "r_speed": 6000, "r_rad": 8000,
    "r_dmg": 150, "r_ratio": 50, "r_slow": 40, "r_t": 240, "r_reel": 20, "r_ex": 25, "r_fear_r": 40000, "r_fear": 90,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_urgot
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


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def true_dmg(thp):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def around(shape, target, effects, forward=None):
    return {"type": "RangeEffect", "shape": circle(shape) if isinstance(shape, int) else shape, "target": target,
            "apply_type": "AroundCaster" if forward is None else {"Forward": {"offset": forward}},
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, target, effects, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": -3000}


def lob(name, travel, target, end, mark=""):
    """A hidden ParabolicProjectile onto the target's spot as it is now (mark: a picture there while it flies)."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 960000,
            "range_effect_name": n(mark) if mark else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, target, effects, apply=1):
    """An area where it is started (a projectile's end_effects), hitting `apply` ticks later."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": apply, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    nat = bool(p["native"])

    # ------------------------------------------------------------------ passive: Echoing Flames
    cone = {"DirDot": {"radius": p["p_r"], "range": p["p_cone"]}}
    blast = combine(sfx("p_leg"),
                    # the fan rides a line (its picture turns with the shot: a caster picture points right on red)
                    {"type": "LineRangeProjectile", "name": n("p_fan"), "width": p["p_w"], "length": p["p_len"],
                     "delay": 12, "apply": 1, "applied_target": "EnemyWithoutTower", "applied_effects": []},
                    around(cone, "EnemyWithoutTower", [attack(0, p["p_ratio"], p["p_hp"]), view("p_hit")],
                           forward=1000))
    if nat:   # the add-on keeps six cooldowns and picks the leg facing the target
        leg = {"type": "Native", "effect_ref": f"{ID}:leg"}
        legs = combine(leg, sw("leg_go", combine(*rm("leg_go"), blast)))
    else:
        legs = sw("leg_cd", NONE, combine(
            {"type": "SwitchByLevel3", "effect_start": flag("leg_cd", p["leg_t0"]),
             "effect_level3": flag("leg_cd", p["leg_t"])}, blast))

    # ------------------------------------------------------------------ W: Purge (opened by Q and E)
    purge = sw("w_gap", NONE, combine(flag("w_gap", p["w_gap"]),
                                      refresh("w_on", p["w_t"], attack_speed_mult=p["w_as"],
                                              move_speed_mult=-p["w_slow"]),
                                      sfx("w_on")))

    # ------------------------------------------------------------------ attack (a Purge shot while it is on)
    shot = homing("a_shot", p["shot_speed"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], y=p["shot_y"])
    gun = homing("w_shot", p["shot_speed"], "Enemy", [attack(p["w_dmg"], p["w_ratio"]), view("w_hit")], y=p["shot_y"])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      sw("w_on", combine(anim("attack_w", 10), sfx("w_shot"), gun, legs),
                         combine(sfx("a_shot"), shot, legs)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Corrosive Charge
    blow = zone("q_zone", p["q_r"], "EnemyWithoutTower",
                [attack(p["q_dmg"], p["q_ratio"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                 view("q_hit"), purge], apply=p["q_apply"])
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q"), voice("vo_q", p),
                           # the blast's picture plays on the landing spot (a ground zone's own picture turns half
                           # round when it faces left: SKILL.md "Both sides")
                           lob("q_charge", p["q_travel"], "EnemyWithoutTower",
                               [view("q_blast"), blow, sfx("q_land")], mark="q_mark")))

    # ------------------------------------------------------------------ skill2: E Disdain
    catch = [attack(p["e_dmg"], p["e_ratio"]), {"type": "Stun", "duration": p["e_stun"]}, view("e_hit"), tsfx("e_hit"),
             delayed(p["e_fling"], {"type": "Pull", "speed": p["e_pull"], "tick": p["e_pull_t"]}, view("e_fling")),
             on_me(purge)]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(sfx("e"), voice("vo_e", p), cview("e_shield"),
                            on_me({"type": "Shield", "amount": p["e_sh"], "attack_ratio": p["e_sh_ratio"],
                                   "ap_ratio": 0, "tick": p["e_sh_t"]}),
                            {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"],
                             "end_effects": catch}))

    # ------------------------------------------------------------------ ult: R Fear Beyond Death
    # the fear when the execute kills: the flag stays on him only when the target is dead a tick later
    fear = combine(*rm("r_kill"), sfx("vo_r_kill"), cview("r_fear"),
                   around(p["r_fear_r"], "EnemyChampion", [{"type": "Fear", "tick": p["r_fear"]},
                                                          buff("r_flee", p["r_fear"], move_speed_mult=-50)]))
    if nat:   # league_urgot:mercy reels in and kills a champion under 25% health, and only that one
        execute = [{"type": "Native", "effect_ref": f"{ID}:mercy"}]
    else:
        # pictures from a target's Delayed play on a corpse too: only an AddCasted runs on the living alone
        execute = [{"type": "Grab", "speed": 3000}, casted(1, 1, view("r_reel")),
                   delayed(p["r_reel"], refresh("r_kill", 40), true_dmg(p["r_ex"]), casted(1, 1, view("r_ex")),
                           tsfx("r_ex"), delayed(1, casted(3, 1, *rm("r_kill")))),
                   on_me(delayed(p["r_reel"] + 4, sw("r_kill", fear)))]
    impale = [attack(p["r_dmg"], p["r_ratio"]), buff("r_leash", p["r_t"], move_speed_mult=-p["r_slow"]),
              view("r_hit"), tsfx("r_hit"), delayed(p["r_t"], *execute)]
    drill = line("r_drill", p["r_speed"], p["r_range"], p["r_rad"], "EnemyChampion", False, impale)
    ult = action("ult", p["r_dur"], p["r_cd"], p["r_st"], p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(sfx("r"), voice("vo_r", p),
                         lob("r_aim", p["r_aim"], "EnemyChampion", [drill, sfx("r_fire")])))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_shot"), P_("w_shot"), P_("p_fan", BIG, 2), P_("q_charge"), P_("r_drill")]
    views_e = [E("a_hit"), E("w_hit"), E("p_hit"), E("q_mark", FX, -1, False), E("q_blast", BIG, 2, False), E("q_hit"),
               E("e_shield", FX, 3), E("e_hit"), E("e_fling"), E("r_hit"), E("r_reel"), E("r_ex", BIG, 3),
               E("r_fear", BIG, -1)]
    views_b = [B_("q_slow", FX, -1), B_("r_leash", FX, 3), B_("w_on", FX, -1), B_("r_flee", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if nat:
        kit["passive"] = {"passive_ref": f"{ID}:legs",
                          "params": {k: p[k] for k in ("leg_t0", "leg_t", "r_ex")}}
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
