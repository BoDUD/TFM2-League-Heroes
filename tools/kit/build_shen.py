"""Build league_shen.data_champion (top, Melee + Tank tag) from the parameters P.

    python tools/kit/build_shen.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-10: top, tank, League's whole kit with the pros' play; R armed like league_kayle R).
TFM2 has three active slots: Twilight Assault is `skill`, Shadow Dash `skill2`, Stand United the `ult`; Spirit's
Refuge runs on its own when the spirit blade comes back with an enemy champion near (Q -> W, League's habit).
  passive Ki Barrier (忍法！气合盾): League shields him for a moment after every ability. Here every Q, W, E and R gives
          p_sh + p_sh_ratio% AD for p_sh_t ticks, at most once every p_cd ticks; an ability that touches an enemy
          champion cuts the wait to p_cd_hit.
  attack  The sword swing, the hit on tick atk_st. While Twilight Assault's charges last (q_n, q_t ticks) the
          attack adds q_a_dmg and, on champions, q_a_hp% of their maximum health (q_a_hp_big% and q_as% attack speed
          when the blade had passed through a champion: League's empowered attacks).
  skill   Q Twilight Assault (奥义！暮临): a `Targeting` cast on `EnemyWithoutTower` (q_range). On tick q_at the spirit
          blade is sent q_out past him toward the target (a hidden line) and flies back to him from there
          (`BackToCasterLinearProjectile`), through everything on the way: q_dmg + q_ratio% AD and q_slow% slow for
          q_slow_t. Back in his hand it gives the q_n empowered attacks; and when an enemy champion is within w_trig
          and Spirit's Refuge is ready, the blade plants the refuge where he stands.
  W       Spirit's Refuge (奥义！魂佑, automatic): for w_t ticks a zone of w_r round his spot (where the blade came back)
          lets no basic attack hurt allied champions in it (`base_attack_damaged_reduce` 100); w_cd between.
  skill2  E Shadow Dash (奥义！影缚): a `Targeting` cast on `EnemyChampion` (e_range; an engage): he dashes onto its spot, every enemy
          passed takes e_dmg + e_ratio% AD and is taunted e_taunt ticks. The pros' E -> Q: when the dash taunts a
          champion and the blade is ready, the blade is pulled from where the dash began back to him, through the
          taunted line (Q's own cast then goes out empty once and starts its cooldown).
  ult     R Stand United (秘奥义！慈悲度魂落): League shields the ally champion lowest on health anywhere, then he channels
          and teleports to it. Nothing in the data reads health, so the slot only arms it (league_kayle R): a 3-tick
          `None` action, then while r_arm lasts a poll every r_poll ticks on him looks for an allied champion
          (a) in crowd control anywhere, else (b) with an enemy champion within r_sur two polls in a row - and at
          least r_far from him (a fight he is not in). That ally gets r_sh + r_sh_ratio% AD of shield for r_sh_t;
          he channels r_ch ticks (crowd control on him every 15 ticks breaks it) and teleports onto it. Unused,
          the window ends with the cooldown capped (the AI arms it again on the next approach).
          The add-on addons/league_shen_unite (native=1) picks the ally by health instead (League's rule).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_shen.data_champion")
ID = "league_shen"
FX = "asset/league/effects/league_shen_fx"
BIG = "asset/league/effects/league_shen_big"

# Numbers = candidate c3 of the 10-min classic-SDK simulations (sn_sim/sim/kd.py, top lane against fighter, executioner,
# lancer, pole_warrior, knight and berserker, three lineups, both sides, 2026-10-10): +0.41 on seeds 1-12, +0.89 on
# 25-36 (league_malphite +1.06 / +0.74, league_sett +1.08 on 1-12). The draft c0 was -1.14 (attack 86, hp 1150, Q 50+60,
# E 70+60): its E, a `Direction` cast, taunted champions 2 times in 27 - e_champ / e_len fixed that (+1.3 alone).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Shen: 610 +99 hp,
    # 64 AD +3, 34 armour, 32 mr, 340 move, 125 range - a tank: more health and resistances, less attack
    "hp": 1200, "hp_g": 110, "atk": 94, "atk_g": 15, "def": 38, "def_g": 9, "mr": 30, "mr_g": 5, "ms": 1000, "ms_g": 11,
    # attack: the sword
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 68, "atk_st": 12,
    # passive Ki Barrier (League: 50-101 + 14% bonus hp shield 2 s, cd 9-6 s, cut by abilities hitting champions)
    "p_sh": 90, "p_sh_ratio": 40, "p_sh_t": 120, "p_cd": 480, "p_cd_hit": 150,
    # Q Twilight Assault (League: 2-4% max hp per empowered hit, 5-7% + 50% attack speed after a champion; cd 8-4 s)
    "q_cd": 420, "q_range": 40000, "q_dur": 18, "q_at": 8, "q_out": 46000, "q_speed": 4000, "q_rad": 6000,
    "q_y": 5000, "q_dmg": 70, "q_ratio": 80, "q_slow": 25, "q_slow_t": 90,
    "q_n": 3, "q_t": 480, "q_a_dmg": 25, "q_a_hp": 4, "q_a_hp_big": 6, "q_as": 50,
    # W Spirit's Refuge (League: 1.75 s, blocks basic attacks on allies in the zone; cd 18-14 s)
    "w_cd": 900, "w_r": 22000, "w_t": 105, "w_trig": 45000,
    # E Shadow Dash (League: 600 units, 70-150 + 15% bonus hp, taunt 1.25 s; cd 18-14 s)
    "e_cd": 840, "e_range": 42000, "e_dur": 18, "e_len": 66000, "e_speed": 3500, "e_rad": 7000, "e_y": 4000,
    "e_dmg": 90, "e_ratio": 80, "e_taunt": 70,
    # 1 = a `Targeting` cast at an enemy champion (an engage, like league_amumu Q): as a `Direction` cast on
    # EnemyWithoutTower the AI spent 25 of 27 dashes on waves (log c2, seed 1), and a `Direction` cast on EnemyChampion
    # still aimed at no one (1 champion in 22 dashes); `MoveTo` in a `Targeting` cast runs to the target's spot
    "e_champ": 1,
    # R Stand United (League: shield 140-460 + 17.5% bonus hp for 5 s, 3 s channel, global; cd 200-160 s)
    "r_cd": 4200, "r_arm": 900, "r_poll": 10, "r_reset": 4900, "r_sur": 25000, "r_far": 60000, "r_seen": 25,
    "r_sh": 260, "r_sh_ratio": 60, "r_sh_t": 300, "r_ch": 150, "r_brk": 15,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_shen_unite: its native passive picks the ally by health and sets r_pick
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


def attack(dmg, ratio, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `WithSelf` would also hit the action's target)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, proj=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": proj,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, rng, radius, y, target, effects, end=()):
    """Flies from where it is started (a line's end) back to him, through everything; end_effects on him."""
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def pzone(name, r, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(r), "tick": tick, "period": period,
            "first_delay": 0, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ passive: Ki Barrier
    ki = sw("p_cd", NONE, combine(flag("p_cd", p["p_cd"]), refresh("p_on", p["p_sh_t"]),
                                  on_me(shield(p["p_sh"], p["p_sh_ratio"], p["p_sh_t"])), sfx("p")))
    ki_cut = sw("p_cd", refresh("p_cd", p["p_cd_hit"]))  # an ability touched an enemy champion

    # ------------------------------------------------------------------ W Spirit's Refuge (planted by the blade)
    refuge = combine(flag("w_cd", p["w_cd"]), cview("w_zone"), sfx("w"), voice("vo_w", p), ki,
                     pzone("w_zone", p["w_r"], p["w_t"], 3, "AllyChampion",
                           [buff("w_safe", 4, base_attack_damaged_reduce=100)]))
    w_check = sw("w_cd", NONE, combine(pick(p["w_trig"], "EnemyChampion", flag("w_go", 1)),
                                       sw("w_go", combine(*rm("w_go"), refuge))))

    # ------------------------------------------------------------------ Q Twilight Assault: the blade's return
    charges = [f"q_{k}" for k in range(1, p["q_n"] + 1)]
    arm_small = combine(*rm(*charges, "q_big"), *[flag(c, p["q_t"]) for c in charges])
    arm_big = combine(*rm(*charges, "q_big"), *[flag(c, p["q_t"]) for c in charges],
                      flag("q_big", p["q_t"], attack_speed_mult=p["q_as"]))
    home = [sw("q_champ", combine(*rm("q_champ"), arm_big), arm_small), sfx("q_back"), w_check]
    blade_hit = [attack(p["q_dmg"], p["q_ratio"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                 view("q_hit"), tsfx("q_hit")]
    champ_hit = [on_me(refresh("q_champ", 60), ki_cut)]

    def blades(rng):
        """The seen blade (waves, camps, champions) and its champion-only twin, flying back to him from here."""
        return [back("q_blade", p["q_speed"], rng, p["q_rad"], p["q_y"], "EnemyWithoutTower", blade_hit, home),
                back("q_twin", p["q_speed"], rng, p["q_rad"], p["q_y"], "EnemyChampion", champ_hit)]

    q_use = combine(refresh("q_cd", p["q_cd"]), refresh("q_skip", p["q_cd"] // 2))
    send = line("q_out", p["q_out"], p["q_out"], 1000, p["q_y"], "EnemyChampion", True, [],
                end=blades(p["q_out"] + 20000))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_skip", combine(*rm("q_skip")),
                      combine(anim("skill", p["q_dur"]), q_use, sfx("q"), voice("vo_q", p), ki,
                              delayed(p["q_at"] - 1, send))))

    # ------------------------------------------------------------------ attack (empowered by the blade)
    def emp():
        twin = homing("a_twin", 100000, 0, "EnemyChampion",
                      [sw("q_big", attack(0, 0, p["q_a_hp_big"]), attack(0, 0, p["q_a_hp"]))])
        return combine(attack(p["q_a_dmg"], 100), twin, view("a_emp"), tsfx("a_emp"))

    use = NONE
    for k, c in enumerate(charges):  # the highest charge on is spent; the last one takes the speed too
        last = rm(c, "q_big") if k == 0 else rm(c)
        use = sw(c, combine(*last, emp()), use) if k else sw(c, combine(*last, emp()))
    swing = sw(charges[0], use, combine(attack(0, 100), view("a_hit"), tsfx("a_hit")))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), swing), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill2: E Shadow Dash (+ the pros' E -> Q)
    e_hit = [attack(p["e_dmg"], p["e_ratio"]), {"type": "Taunt", "duration": p["e_taunt"]}, view("e_hit"),
             tsfx("e_hit")]
    e_champ = [on_me(refresh("e_got", 40), ki_cut)]
    dash_t = -(-p["e_len"] // p["e_speed"])
    combo = sw("e_got", sw("q_cd", NONE, combine(*rm("e_got"), q_use, sfx("q"), *blades(p["e_len"] + 20000))))
    anchor = line("e_from", 1000, 1000, 1000, 0, "EnemyChampion", True, [], end=[delayed(dash_t + 1, combo)])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting" if p["e_champ"] else "Direction",
                    "EnemyChampion" if p["e_champ"] else "EnemyWithoutTower",
                    combine(anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p), ki, anchor,
                            {"type": "MoveTo", "speed": p["e_speed"], "range": p["e_len"], "end_effects": []},
                            line("e_dash", p["e_speed"], p["e_len"], p["e_rad"], p["e_y"], "EnemyWithoutTower", True,
                                 e_hit),
                            line("e_twin", p["e_speed"], p["e_len"], p["e_rad"], p["e_y"], "EnemyChampion", True,
                                 e_champ)))

    # ------------------------------------------------------------------ ult: R Stand United
    breaks = [delayed(t, pick(1, "AllyChampionInCC", *rm("r_ch"))) for t in range(p["r_brk"], p["r_ch"], p["r_brk"])]

    def save():
        """On the ally (the probe's hit): the shield now, the channel on him, the teleport onto it at the end."""
        return combine(*rm("r_arm", "r_seen"), refresh("r_ch", p["r_ch"] + 2),
                       shield(p["r_sh"], p["r_sh_ratio"], p["r_sh_t"]), buff("r_shield", p["r_sh_t"]),
                       sfx("r_ally"),
                       on_me(anim("ult", p["r_ch"]), cview("r_cast"), sfx("r"), voice("vo_r", p), ki, *breaks),
                       delayed(p["r_ch"], sw("r_ch", combine(*rm("r_ch"), {"type": "Teleport"}, view("r_land"),
                                                              sfx("r_land")))))

    def probe(cc):
        """A homing probe at the ally picked: far enough from him, and in crowd control or held in a fight."""
        far = pick(p["r_far"], "AllyOnlySelf", flag("r_near", 1), proj=True)
        if cc:
            go = sw("r_near", combine(*rm("r_near")), save())
        else:
            fight = pick(p["r_sur"], "EnemyChampion", flag("r_e", 1), proj=True)
            go = combine(fight, sw("r_near", combine(*rm("r_near", "r_e")),
                                   sw("r_e", combine(*rm("r_e"), sw("r_seen", save(), refresh("r_seen", p["r_seen"]))))))
        return homing("r_probe", 1000000, 0, "AllyChampion", [far, go])

    if native:  # the add-on marks the ally to save (lowest health) with r_pick on him: only that one is probed
        look = sw("r_pick", pick(960000, "AllyNotSelf", probe(True)))
    else:
        look = combine(pick(960000, "AllyChampionInCC", flag("r_cc", 1)),
                       sw("r_cc", combine(*rm("r_cc"), pick(960000, "AllyChampionInCC", probe(True))),
                          pick(960000, "AllyNotSelf", probe(False))))
    poll = combine(pick(1, "AllyChampionInCC", flag("r_me", 1)),
                   sw("r_me", combine(*rm("r_me")), sw("r_arm", sw("r_ch", NONE, look))))
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_reset", 3, ult_cooldown_mult=p["r_reset"])))
    ult = action("idle", 3, p["r_cd"], 1, 960000, "None", "EnemyChampion",
                 combine(refresh("r_arm", p["r_arm"]),
                         on_me(casted(p["r_arm"], p["r_poll"], poll), delayed(p["r_arm"], reset))), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("q_blade")]
    views_e = [E("a_hit"), E("a_emp"), E("q_hit"), E("e_hit"), E("w_zone", BIG, -1, False), E("r_cast", BIG, 3),
               E("r_land", BIG, 3)]
    views_b = [B_("p_on", FX, 3), B_("q_1", FX, 3), B_("q_slow", FX, -1), B_("w_safe", FX, 3),
               B_("r_shield", BIG, 3)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_shen_unite:unite", "params": {}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC", "Shield"], **extra,
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (the ally picked by health)")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    if a.native:
        p["native"] = 1
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
