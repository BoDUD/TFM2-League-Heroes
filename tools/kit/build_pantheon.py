"""Build league_pantheon.data_champion (top, Melee diver) from the parameters P.

    python tools/kit/build_pantheon.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-16: top lane, the main pack plus a native add-on addons/league_pantheon, PPU 1.5; every
recommended option - 「方案可以，全按推荐做（上单，做附加包，PPU 1.5）」):
  passive Mortal Will (凡人意志): every basic attack that lands and every basic ability cast adds a stack (caster flags
          m1..m4, then pw at five); with pw on, the next Q, W or E is empowered and takes the stacks. Every life starts
          with pw (League: full stacks at the start and on respawn; a `Permanent` init flag, champion-data 5 "Death
          clears a mod's buffs"). R's passive, armour penetration, is his from the start (r_pen%: the data cannot
          tell level 5 from level 3).
  attack  A spear thrust (atk_range: League's 175 reach against the usual 125), the hit on a_st. Empowered W's three
          thrusts replace the next one (attack_w).
  skill   Q Comet Spear (贯星长枪): a `Targeting` cast on `EnemyWithoutTower` (q_range, waves and camps too). A probe asks
          whether the target stands within the thrust's reach (q_near): then he thrusts (League's tap) - a line of
          q_len x q_w toward it, q_dmg + q_ratio% AD to every enemy on it; else he raises the spear (q_hold ticks,
          League's hold) and throws it at where the target stood q_aim ticks before the release (dodged by walking off
          the line: league_tahmkench Q's lock), through everything on the line: the first unit q_dmg + q_ratio% AD, the
          ones after half of it (League's falloff). Empowered: q_emp + q_emp_ratio% AD more on every unit hit. League's
          cooldown refund on a tap is folded into a shorter q_cd (a `skill_cooldown_mult` would cut W and E's too), and
          its bonus below 20% health is the add-on's (nothing in the data reads health).
  skill2  W Shield Vault (斗盾跃击) and E Aegis Assault (神佑之盾) share the slot, each on its own cooldown (caster flags w_cd
          and e_cd; the slot waits only s2_cd). A `Targeting` cast on `EnemyChampion` (w_range):
          - W ready: he leaps onto the champion (`MoveToTarget` w_speed) and on landing deals w_dmg + w_hp% of its
            maximum health and stuns it w_stun ticks (League: 6-8% max health, 1 s). Empowered: his next attack within
            w_tri_t ticks thrusts three times, w_tri_ratio% AD each (League: 40-55% each).
          - else E ready and an enemy champion within e_trig: he plants the shield toward the target for e_t ticks
            (League: 1.5 s): immune to crowd control, e_red% less damage from every side (League: all of it from the
            front; with native=1 the add-on blocks the front only, like league_braum's Unbreakable), stabbing the cone in
            front (e_r, DirDot e_cone) e_n times for e_stab% AD each; then the shield bash: e_dmg + e_ratio% AD in the
            cone. Empowered: e_def armour and magic resistance for e_def_t and e_ms% move speed for e_ms_t after it.
          - else nothing; the slot tries again.
  ult     R Grand Starfall (大荒星陨): the slot arms the ult (league_galio R's way): for r_arm ticks a poll every r_poll
          ticks looks at a champion his team is fighting (EnemyChampionRecentlyAttacked) at least r_min from him with
          an allied champion within r_sur of it (a fight to join), and he not in crowd control. (Another enemy champion
          there was enough at first: the add-on's log, 2026-10-16, had 35 of 41 falls land with no ally near, mostly on
          two enemies, and he died within ~30 s of nearly every one - the user: 「看一下附加包的日志对不对」.)
          Then he crouches r_ch ticks (unseen and immune to crowd control: League's first channel), leaps (banished
          r_fall ticks: in the sky) and comes down where that champion stood at the leap, a ring marking it: on r_sp his
          spear strikes it first (r_sp_dmg + r_sp_ratio% AD within r_r and an r_slow% slow for r_slow_t), then he lands
          (Teleport): r_dmg magic within r_rc, half of it out to r_r, and full Mortal Will. Unused, the window ends
          with the cooldown capped (r_reset).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_pantheon.data_champion")
ID = "league_pantheon"
FX = "asset/league/effects/league_pantheon_fx"
BIG = "asset/league/effects/league_pantheon_big"

# Numbers: the first draft from League's ratios inside the base Melee ranges (champion-data 2); 10-min classic-SDK
# simulations (Temp/pn_sim/sim/kd.py --lane 0 against fighter, executioner, lancer, pole_warrior, knight, berserker, three
# lineups, both sides): the draft d0 (a 60-tick fall, the spear at 30, radius 28000: the landing hit 1 of 6 casts in a
# logged game - the champions walked off the locked spot) +0.99 on 8 seeds; d1 (here: a 40-tick fall, the spear at 20,
# radius 32000) +1.96 on seeds 1-8, +1.37 on 9-24 (league_darius +1.99, league_garen -1.11). Retimed to the strips (d2):
# +0.96 on seeds 1-16, +0.62 on 17-32; attack 96 (here) +1.40 / +1.60 (hp 1050 +1.70, Q 100 +1.56 on seeds 1-16).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30, mr 25, move 1000, range 25000, attack every 65 ticks);
    # League's Pantheon: 650 +109 hp, 64 AD +3.3, 40 armour +4.95, 28 mr, 345 move, 175 range, 0.658 attack speed
    "hp": 1000, "hp_g": 105, "atk": 96, "atk_g": 18, "def": 34, "def_g": 8, "mr": 26, "mr_g": 4, "ms": 1000, "ms_g": 10,
    "atk_range": 27000, "atk_dur": 26, "atk_cd": 66, "a_st": 10,
    # R's passive (League: 10-30% armour penetration)
    "r_pen": 15,
    # Q Comet Spear (League: 70-190 + 115% bonus AD, the throw 1200 range at 2700 speed, falloff 50%, cd 11-8 s, the
    # tap refunding 60%; empowered 20-266 + 115% bonus AD more)
    "q_cd": 330, "q_range": 75000, "q_dur": 18, "q_near": 20000, "q_t_at": 7, "q_len": 48000, "q_w": 5000, "q_thrust_t": 12,
    "q_hold": 19, "q_anim": 36, "q_aim": 6, "q_speed": 4500, "q_line": 100000, "q_rad": 6000, "q_dmg": 90, "q_ratio": 100,
    "q_emp": 50, "q_emp_ratio": 60,
    # skill2 slot
    "s2_cd": 60,
    # W Shield Vault (League: 600 range, 6-8% max health, stun 1 s, cd 13-9 s; empowered: 3 hits of 40-55% AD)
    "w_cd": 600, "w_range": 45000, "w_dur": 26, "w_speed": 3500, "w_dmg": 30, "w_hp": 7, "w_stun": 60,
    "w_tri_t": 240, "w_tri_ratio": 50, "w_tri_at1": 4, "w_tri_at2": 11, "w_tri_at3": 18, "w_tri_anim": 28,
    # E Aegis Assault (League: 1.5 s, the front immune, a stab every 0.125 s of 8.3% AD (100% AD at most), the slam
    # 55-255 + 150% bonus AD, cd 22-18 s; empowered 5-33 armour and mr 4 s, 60% move speed 1.5 s)
    "e_cd": 1080, "e_trig": 32000, "e_t": 90, "e_red": 60, "e_r": 42000, "e_cone": 800, "e_n": 6, "e_stab": 15,
    "e_dmg": 110, "e_ratio": 100, "e_bash_t": 23, "e_bash_at": 7, "e_def": 20, "e_def_t": 240, "e_ms": 60, "e_ms_t": 90,
    # R Grand Starfall (League: 5500 range, 2 s crouch then 2.25 s fall, the spear at 0.8 s for 40-190 + 115% bonus AD
    # and a 50% slow 2 s, the landing 300-700 magic (half at the edge) radius 700, cd 180-150 s)
    "r_cd": 3600, "r_arm": 900, "r_poll": 10, "r_reset": 4900, "r_min": 35000, "r_sur": 30000,
    "r_ch": 60, "r_fall": 40, "r_sp": 20, "r_r": 32000, "r_rc": 12000, "r_sp_dmg": 80, "r_sp_ratio": 100,
    "r_slow": 50, "r_slow_t": 120, "r_dmg": 300, "r_land": 30, "r_leap": 17, "r_hit_at": 5,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_pantheon
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


def magic(dmg):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": 0, "can_crit": False,
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


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
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


def zone(name, radius, target, effects):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def lives(*effects):
    """A `Delayed` chain's effects only while he lives (a dead caster's Delayed effects run in the game): a 1-tick
    flag from a search that finds no dead caster; the copy in the search is what the AI reads (champion-data 5)."""
    return combine(pick(1, "AllyOnlySelf", flag("live", 1)),
                   sw("live", combine(*effects), pick(1, "AllyOnlySelf", *effects)), *rm("live"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    nat = bool(p["native"])

    # ------------------------------------------------------------------ passive: Mortal Will
    # every life starts with full stacks and R's armour penetration (death clears a mod's buffs)
    init = sw("init", NONE, combine(flag("init", None), refresh("pw", None),
                                    refresh("r_pen", None, defence_penetration=p["r_pen"])))
    ms = ["m1", "m2", "m3", "m4"]
    ladder = sw("m4", combine(*rm("m4"), flag("pw", None), cview("p_ready"), sfx("p_ready")),
                sw("m3", combine(*rm("m3"), flag("m4", None)),
                   sw("m2", combine(*rm("m2"), flag("m3", None)),
                      sw("m1", combine(*rm("m1"), flag("m2", None)), flag("m1", None)))))
    climb = sw("pw", NONE, ladder)

    def cast(emp):
        """A basic ability's cast: with pw it is empowered (`emp`: its flag, or what it gives) and takes the stacks,
        else a stack (the ladder alone: pw is off there)."""
        return sw("pw", combine(*rm("pw", *ms), emp), ladder)

    # ------------------------------------------------------------------ attack (+ empowered W's three thrusts)
    stab = combine(attack(0, 100), view("a_hit"), tsfx("a_hit"))
    normal = combine(sfx("a_swing"), stab, climb)
    # the three thrusts on attack_w's thrust frames (2, 4 and 6 of its strip)
    tri = [delayed(p[f"w_tri_at{k}"], lives(attack(0, p["w_tri_ratio"]), view("a_hit"), tsfx("a_hit")))
           for k in range(1, 4)]
    triple = combine(*rm("w_tri"), anim("attack_w", p["w_tri_anim"]), sfx("w_tri"), *tri, climb)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(init, sw("w_tri", triple, normal)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Comet Spear
    def q_hit(dmg, ratio):
        out = [attack(dmg, ratio), sw("q_emp", attack(p["q_emp"], p["q_emp_ratio"])), view("q_hit"), tsfx("q_hit")]
        if nat:   # the add-on's bonus below 20% health
            out.append({"type": "Native", "effect_ref": f"{ID}:spear"})
        return out

    # the thrust's light rides the line (its picture turns with it: a caster picture would point right on the red side)
    thrust = combine(sfx("q_tap"),
                     {"type": "LineRangeProjectile", "name": n("q_thrust"), "width": p["q_w"], "length": p["q_len"],
                      "delay": p["q_thrust_t"], "apply": 1, "applied_target": "EnemyWithoutTower",
                      "applied_effects": [T(e) for e in q_hit(p["q_dmg"], p["q_ratio"])]},
                     delayed(3, *rm("q_emp")))
    # the first unit the spear meets takes all of it, the ones after half (q_first lasts the flight)
    flight = p["q_line"] // p["q_speed"] + 4
    spear = line("q_spear", p["q_speed"], p["q_line"], p["q_rad"], "EnemyWithoutTower", True,
                 [sw("q_first", combine(*q_hit(p["q_dmg"] // 2, p["q_ratio"] // 2)),
                     combine(refresh("q_first", flight), *q_hit(p["q_dmg"], p["q_ratio"])))])
    throw = combine(anim("skill_throw", p["q_anim"]), sfx("q_hold"),
                    delayed(p["q_hold"] - p["q_aim"],
                            lob("q_aim", p["q_aim"], "EnemyWithoutTower",
                                [*rm("q_first"), spear, sfx("q_throw")])),
                    delayed(p["q_hold"] + flight, *rm("q_emp", "q_first")))
    probe = homing("q_probe", 1000000, "EnemyWithoutTower",
                   [pick(p["q_near"], "AllyOnlySelf", refresh("q_close", 3), fp=True)])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(init, *rm("q_close"), cast(refresh("q_emp", p["q_hold"] + flight + 4)), voice("vo_q", p),
                           probe,
                           delayed(2, lives(sw("q_close", combine(*rm("q_close"), delayed(p["q_t_at"] - 3, thrust)),
                                               throw)))))

    # ------------------------------------------------------------------ skill2: W Shield Vault / E Aegis Assault
    w_land = [attack(p["w_dmg"], 0, p["w_hp"]), {"type": "Stun", "duration": p["w_stun"]}, view("w_hit"),
              tsfx("w_hit")]
    w_post = [anim("skill2", p["w_dur"]), sfx("w"), voice("vo_w", p),
              {"type": "MoveToTarget", "speed": p["w_speed"], "range": p["w_range"], "end_effects": w_land}]

    cone = {"DirDot": {"radius": p["e_r"], "range": p["e_cone"]}}
    gap = p["e_t"] // (p["e_n"] + 1)
    stabs = [delayed(k * gap, lives(around(cone, "EnemyWithoutTower", [attack(0, p["e_stab"]), view("e_stab")],
                                           forward=1000)))
             for k in range(1, p["e_n"] + 1)]
    bash = delayed(p["e_t"], lives(anim("e_bash", p["e_bash_t"]), sfx("e_bash")), delayed(p["e_bash_at"], lives(
                                   cview("e_bash"),
                                   around(cone, "EnemyWithoutTower", [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"),
                                                                      tsfx("e_hit")], forward=1000),
                                   sw("e_emp", combine(*rm("e_emp"),
                                                       refresh("e_def", p["e_def_t"], defence=p["e_def"],
                                                               magic_resistance=p["e_def"]),
                                                       refresh("e_haste", p["e_ms_t"], move_speed_mult=p["e_ms"]))))))
    hold = [refresh("e_hold", p["e_t"], cc_immune=True)]
    if not nat:   # the add-on blocks the front itself
        hold.append(refresh("e_red", p["e_t"], damaged_reduce=p["e_red"]))
    e_post = [anim("e_hold", p["e_t"]), sfx("e"), voice("vo_e", p), cview("e_shield"), *hold, *stabs, bash]
    near = combine(*rm("e_near"), pick(p["e_trig"], "EnemyChampion", flag("e_near", 1)))
    # W with w_cd off; else E with e_cd off and an enemy champion within e_trig (e_near, its 1-tick find); else nothing.
    # Mortal Will's cast is written once for both (skill-tree slimming, 2026-10-18): W raises e_near too, and both take
    # it off at the end of the run, so it is never on between ticks - every reading of the slot (the AI's, at any tick)
    # still sees W's leap under w_cd off and nothing under w_cd on. The hidden flags w_cd, e_cd and e_near go on after
    # the cast instead of before it; W's empowered thrusts (w_tri) come from the cast itself (its flag w_emp was added
    # and taken back in the same run). w_cd, e_cd, e_near, w_emp and e_emp are added, read and taken off only here (the
    # attack, Q, R and addons/league_pantheon/src never name them), so nothing else sees the difference.
    go = cast(sw("w_cd", refresh("e_emp", p["e_t"] + 4), refresh("w_tri", p["w_tri_t"])))
    skill2 = action("idle", 3, p["s2_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
                    combine(init, sw("w_cd", sw("e_cd", NONE, near), flag("e_near", 1)), sw("e_near", go),
                            sw("w_cd", sw("e_near", combine(*rm("e_near"), flag("e_cd", p["e_cd"]), *e_post)),
                               combine(*rm("e_near"), flag("w_cd", p["w_cd"]), *w_post))), key="skill2")

    # ------------------------------------------------------------------ ult: R Grand Starfall
    spear_down = [zone("r_spear", p["r_r"], "EnemyWithoutTower",
                       [attack(p["r_sp_dmg"], p["r_sp_ratio"]),
                        buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]), view("r_sp_hit")]),
                  sfx("r_spear")]
    # he lands on the landing frame's spot, the blow on its second frame (the spear driven in)
    landing = [{"type": "Teleport"}, anim("ult_land", p["r_land"]), sfx("r_land"),
               delayed(p["r_hit_at"], view("r_land"),
                       zone("r_core", p["r_rc"], "EnemyWithoutTower", [magic(p["r_dmg"] // 2), view("r_hit")]),
                       zone("r_edge", p["r_r"], "EnemyWithoutTower", [magic(p["r_dmg"] // 2)])),
               refresh("pw", None), cview("p_ready")]
    # the leap is seen (r_leap ticks), then he is gone into the sky until the landing
    leap = combine(anim("ult_leap", p["r_leap"]), sfx("r_leap"), voice("vo_r_leap", p),
                   on_me(delayed(p["r_leap"], {"type": "Banish", "duration": p["r_fall"] - p["r_leap"]})),
                   lob("r_spot", p["r_sp"], "EnemyChampion", spear_down, mark="r_mark"),
                   # the spear's fall plays on the landing spot from the leap (its third frame strikes at r_sp)
                   lob("r_fall", p["r_fall"], "EnemyChampion", landing, mark="r_spear"))

    def fire():
        """On the champion (the probe's hit): the crouch now, the leap at its end, both on where it stands then."""
        return combine(*rm("r_arm"), refresh("r_ch", p["r_ch"] + 2, cc_immune=True),
                       on_me(anim("ult", p["r_ch"]), cview("r_cast"), sfx("r"), voice("vo_r", p),
                             {"type": "CasterInvisible", "tick": p["r_ch"]}),
                       delayed(p["r_ch"], lives(*rm("r_ch"), leap)))

    def probe_r():
        far = pick(p["r_min"], "AllyOnlySelf", flag("r_near", 1), fp=True)
        crowd = pick(p["r_sur"], "AllyNotSelf", flag("r_ok", 1), fp=True)
        go = combine(far, crowd, sw("r_near", NONE, sw("r_ok", fire())), *rm("r_near", "r_ok"))
        return homing("r_probe", 1000000, "EnemyChampion", [go])

    if nat:   # every enemy champion is asked; league_pantheon:starfall raises the 1-tick flag r_this for the spot
        look = around(960000, "EnemyChampion", [{"type": "Native", "effect_ref": f"{ID}:starfall"},
                                                sw("r_this", combine(*rm("r_this"), fire()))])
    else:
        look = pick(960000, "EnemyChampionRecentlyAttacked", probe_r())
    poll = combine(pick(1, "AllyChampionInCC", flag("r_me", 1)),
                   sw("r_me", combine(*rm("r_me")), sw("r_arm", sw("r_ch", NONE, look))))
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_reset", 3, ult_cooldown_mult=p["r_reset"])))
    ult = action("idle", 3, p["r_cd"], 1, 960000, "None", "EnemyChampion",
                 combine(init, refresh("r_arm", p["r_arm"]),
                         on_me(casted(p["r_arm"], p["r_poll"], poll), delayed(p["r_arm"], reset))), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("q_spear"), P_("q_thrust", BIG, 2)]
    views_e = [E("a_hit"), E("p_ready", FX, 3), E("q_hit"), E("w_hit"), E("e_shield", BIG, -1),
               E("e_stab"), E("e_bash", BIG, 3, False), E("e_hit"), E("r_cast", BIG, -1), E("r_mark", BIG, -1, False),
               E("r_spear", BIG, 2, False), E("r_sp_hit"), E("r_land", BIG, -1, False), E("r_hit")]
    if nat:
        views_e.append(E("q_low"))
    views_b = [B_("r_slow", FX, -1), B_("e_def", FX, 3)]
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
        kit["passive"] = {"passive_ref": f"{ID}:will",
                          "params": {k: p[k] for k in ("q_dmg", "q_ratio", "r_min", "r_sur", "r_r")}}
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
