"""Build league_zeri.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_zeri.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-11, all the recommended options; the wall laser and the real shield steal go into the
add-on addons/league_zeri, which swaps in build(p, native=True)):
  attack  Q Burst Fire (电火迸射): League's Q is her attack. A burst of seven rounds as one non-penetrating
          `LinearProjectile` on `Enemy` (`a_burst`) at the target: the first unit on its line takes it (minions block, as in
          League), 100% AD physical, a `BaseAttack` (it crits). Range a little longer than the base gunners'.
  passive Living Battery (内能迁转): every attack charges the pack one rung (c1..c<p_need - 1>, then `p_full`; R's nova
          fills it at once). With `p_full` the next attack is the charged shot instead of the burst: a homing spark
          (`p_spark`, League's targeted right click; never blocked) for 100% AD + p_dmg + p_ap% AP magic, a p_slow% slow
          for p_slow_t ticks, and on a champion p_hp% of its max health (true: magic has no max-health part) and for her
          a p_sh + p_sh_r% AD shield (p_sh_t ticks) and p_haste% move speed for p_haste_t ticks (League's 1.5 s haste).
          The shield stands for League's shield steal; with the add-on it is left out (native=True) and the passive
          league_zeri:battery steals p_steal% of the shield her damage hits instead.
  skill   W Ultrashock Laser (强穿激光): a `Direction` cast on `EnemyWithoutTower` (w_range): after w_rel ticks a fast
          non-penetrating pulse (`w_pulse`) hits the first enemy for w_dmg + w_ratio% AD and a w_slow% slow (w_slow_t). A
          minion or monster hit first stands for League's wall: where the pulse stopped a laser runs on away from her
          (a `DirDot` `RangeProjectile` on the stop point, league_viktor E's way; the picture a hitless
          `LineRangeProjectile` drawn from that point on) hitting everything behind it the same way. A champion hit with
          the pack full fires the charged spark at it at once (the pros' W -> charged shot). With the add-on (native=True)
          the pulse lays w_go on her while it flies; the passive follows it and, where it meets a wall cell or the map's
          edge, lays w_wall (the pulse hits nothing more) and fires the laser on from there (League's wall laser).
  skill2  E Spark Surge (灿丽花火): a `Targeting` cast on `EnemyWithoutTower` (e_range): league_vayne Q's three ways - a dash
          away from a champion within e_near, a hop back while anything is in her attack range, else a dash toward the
          target (all e_dist) - then e_on for e_t ticks: the burst's first unit takes 100 - e_pierce% AD and where it
          stopped a narrow cone (`DirDot`, e_reach) through that unit and on behind it deals e_pierce% AD + e_dmg + e_ap%
          AP magic to every enemy in it (League: the first full, the rest 75-105%, bonus magic on hit). Each champion
          her burst hits in e_on climbs a ladder ec1..ec<e_n> that caps both basic cooldowns a bit lower (League takes
          0.75 s off E per champion hit). Combo E -> W: with W ready, the pulse follows at a champion within w_range.
  ult     R Lightning Crash (超限爆闪): a 3-tick `Targeting` cast on `EnemyChampion` (r_slot), armed like league_twitch R:
          two enemy champions within r_count fire it at once, else it arms r_armed for r_arm ticks (each attack checks
          again, one champion in reach is enough after r_hold) and refunds the cooldown when it lapses. Fire: the cast
          pose, on r_rel a nova round her (r_reach) for r_dmg + r_ap% AP magic + r_ratio% AD physical to every enemy,
          the pack filled, and r_on for r_t ticks: +r_as% attack speed, +r_ms% move speed; every champion her attacks hit
          climbs rs1..rs<r_n> (+r_ms_step% move speed each) and, while r_on holds, renews r_ext (r_ext_t) - read at her
          next attack from the flag hit_c the hit lays (E's ladder too: one copy of each in the tree); when r_on
          ends a poll keeps the overcharge (r_st2) while r_ext holds - at most r_ext_t ticks longer (League's
          refresh, capped). Overcharged, the burst is the triple shot `r_shot` (r_shot_ratio% AD) whose stop point
          chains lightning to every enemy within r_chain: r_cdmg + r_cap% AP magic. Combo R -> E: R fired from the slot
          dashes with E (when ready) at a champion in reach.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_zeri.data_champion")
ID = "league_zeri"
FX = "asset/league/effects/league_zeri_fx"
BIG = "asset/league/effects/league_zeri_big"

# Numbers = draft d0 (before the simulation).
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Zeri: 600 +110 hp,
    # 56 AD, 330 move (the fastest base move speed among marksmen), 550 attack range (Q 825)
    "hp": 860, "hp_g": 86, "atk": 92, "atk_g": 18, "ap": 20, "ap_g": 8, "def": 20, "def_g": 7, "mr": 15, "mr_g": 3,
    "ms": 920, "ms_g": 10,
    # attack: Burst Fire leaves the rifle on a_st (the action's start timing: attack speed shortens it); the rounds, the
    # spark and W's pulse start 5000 - a_y over her pivot: 11 px, the dense frames' levelled muzzle as league.dll shows
    # them at 105% (tools/art/ppu_zeri.py SCALE; the user: 「挪到高清枪口」 - the 1x rifle's was 6 px over it, a_y -1000)
    "atk_range": 60000, "atk_dur": 24, "atk_cd": 56, "a_st": 8, "burst_speed": 9000, "burst_r": 3000, "a_y": -6000,
    # passive: Living Battery (League: charged attack 90-200 + 110% AP + 1-11% max hp; shield steal 45% 3 s; haste 10% 1.5 s)
    "p_need": 5, "p_speed": 8000, "p_dmg": 40, "p_ap": 100, "p_hp": 4, "p_slow": 40, "p_slow_t": 30,
    "p_sh": 40, "p_sh_r": 30, "p_sh_t": 180, "p_haste": 10, "p_haste_t": 90, "p_steal": 45,
    # skill: W Ultrashock Laser (League: 30-230 + 120% AD, slow 25-55% 2 s, 1200 range, laser 1500, cd 12-8 s)
    "w_cd": 600, "w_range": 90000, "w_dur": 30, "w_rel": 16, "w_speed": 9000, "w_len": 110000, "w_r": 4000,
    "w_dmg": 60, "w_ratio": 110, "w_slow": 35, "w_slow_t": 120, "w_laser": 100000, "w_cos": 990, "w_lw": 9000,
    "w_lapply": 3, "w_ldelay": 14,
    # skill2: E Spark Surge (League: dash 300, 5 s, pierce 75-105%, 20-32 + 20% AP magic on hit, cd 24-18 s,
    # -0.75 s a champion hit)
    "e_cd": 1200, "e_range": 75000, "e_dur": 18, "e_near": 30000, "e_dist": 30000, "e_t": 300, "e_pierce": 80,
    "e_dmg": 20, "e_ap": 30, "e_reach": 40000, "e_cos": 985, "e_n": 5, "e_cut": 8,
    # ult: R Lightning Crash (League: nova 825, 150-650 + 100% bonus AD + 110% AP magic, overcharge 5 s +30% AS,
    # +20% MS +2% a stack, refreshed by champion hits; triple shot chaining to 5 at 40%? AD; cd 80-70 s)
    "r_cd": 3600, "r_slot": 70000, "r_count": 90000, "r_reach": 75000, "r_arm": 600, "r_hold": 180, "r_anim": 20, "r_rel": 9,
    "r_dmg": 150, "r_ap": 100, "r_ratio": 60, "r_t": 300, "r_as": 30, "r_ms": 20, "r_n": 5, "r_ms_step": 3,
    "r_ext_t": 150, "r_poll": 10, "r_shot_ratio": 100, "r_chain": 30000, "r_cdmg": 15, "r_cap": 40,
    # her spoken lines, at most one every vo_gap ticks
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
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def true_hp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def cone(name, radius, cos, delay, apply, target, effects):
    """A wedge opening away from her on the point a projectile stopped at (league_viktor E's hit)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": {"DirDot": {"radius": radius, "range": cos}},
            "delay": delay, "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def burst_zone(name, radius, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 2, "apply": 2,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def picture_line(name, length, width, delay):
    """A hitless line: only its picture (drawn at the point it starts on, turned from her to it)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": "Ally", "applied_effects": []}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def ladder(names, top, last=None):
    """One flag of names at a time, read from the top: names[-1] runs `last` (default: nothing more), names[k] steps up
    to names[k+1], none starts names[0]; `top` builds the flag added for a rung (name -> effect)."""
    out = top(names[0])
    for k in range(len(names) - 1):
        out = sw(names[k], combine(*rm(names[k]), top(names[k + 1])), out)
    return sw(names[-1], last or NONE, out)


def build(p, native=False):
    # ------------------------------------------------------------------ passive: Living Battery
    cs = [f"c{k}" for k in range(1, p["p_need"])]
    full = combine(*rm(*cs), flag("p_full", None), cview("p_ready"), sfx("ready"), voice("vo_ready", p))

    def fill():
        """The pack full at once (R's nova)."""
        return sw("p_full", NONE, full)

    charge = sw("p_full", NONE, ladder(cs, lambda c: flag(c, None), last=full))
    perks = [shield(p["p_sh"], p["p_sh_r"], p["p_sh_t"]), refresh("p_shv", p["p_sh_t"]), sfx("shield")] if not native else []
    spark_champ = pick(1000, "EnemyChampion", true_hp(p["p_hp"]),
                       on_me(*perks, refresh("p_haste", p["p_haste_t"], move_speed_mult=p["p_haste"])), fp=True)

    def spark():
        return combine(*rm("p_full"), sfx("charged"),
                       homing("p_spark", p["p_speed"], p["a_y"], "Enemy",
                              [attack(0, 100), magic(p["p_dmg"], p["p_ap"]),
                               buff("p_slow", p["p_slow_t"], move_speed_mult=-p["p_slow"]), view("p_hit"),
                               tsfx("charged_hit"), spark_champ]))

    # ------------------------------------------------------------------ R's overcharge: champion hits
    rs = [f"rs{k}" for k in range(1, p["r_n"] + 1)]
    r_climb = ladder(rs, lambda s: flag(s, p["r_t"] + p["r_ext_t"],
                                        move_speed_mult=p["r_ms_step"] * (rs.index(s) + 1)))
    r_champ = sw("r_on", combine(r_climb, refresh("r_ext", p["r_ext_t"])), sw("r_st2", r_climb))
    # E's cooldown ladder: each champion hit in e_on caps the basic cooldowns a little lower
    ecs = [f"ec{k}" for k in range(1, p["e_n"] + 1)]
    cut = lambda k: refresh(f"cut{k}", 2, skill_cooldown_mult=p["e_cut"] * k, ult_cooldown_mult=-p["e_cut"] * k)
    e_climb = ladder(ecs, lambda c: combine(flag(c, p["e_t"]), cut(ecs.index(c) + 1)),
                     last=cut(len(ecs)))
    e_champ = sw("e_on", e_climb)
    # a champion hit only lays hit_c; her next attack reads it (one ladder in the tree, not one per projectile)
    champ_hit = pick(1000, "EnemyChampion", refresh("hit_c", p["atk_cd"] * 2), fp=True)
    read_hits = sw("hit_c", combine(*rm("hit_c"), r_champ, e_champ))

    # ------------------------------------------------------------------ attack: burst, charged spark, E / R rounds
    def rounds(name, ratio, *extra, end=()):
        return line(name, p["burst_speed"], p["atk_range"] + 20000, p["burst_r"], p["a_y"], "Enemy", False,
                    [attack(0, ratio), view("a_hit"), tsfx("hit"), champ_hit, *extra], end=end)

    e_cone = cone("e_cone", p["e_reach"], p["e_cos"], 3, 2, "EnemyWithoutTower",
                  [attack(0, p["e_pierce"]), magic(p["e_dmg"], p["e_ap"]), view("e_hit")])
    chain = burst_zone("r_chain", p["r_chain"], "EnemyWithoutTower",
                       [magic(p["r_cdmg"], p["r_cap"]), view("r_zap"), tsfx("r_chain")])

    def burst(over):
        """The burst by her state: overcharged (the triple shot and its chain), E's rounds (the first unit 100 - e_pierce%
        and the cone through it), both, or the plain burst."""
        if over:
            e_way = rounds("r_shot", p["r_shot_ratio"] - p["e_pierce"], end=[e_cone, chain])
            plain = rounds("r_shot", p["r_shot_ratio"], end=[chain])
        else:
            e_way = rounds("e_shot", 100 - p["e_pierce"], end=[e_cone])
            plain = rounds("a_burst", 100)
        return combine(sfx("shot"), sw("e_on", e_way, plain))

    over = burst(True)
    shoot = sw("p_full", spark(),
               combine(charge, sw("r_on", over, sw("r_st2", over, burst(False)))))

    # ------------------------------------------------------------------ W Ultrashock Laser
    w_hit = [attack(p["w_dmg"], p["w_ratio"]), buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"])]
    laser = combine(sfx("w_beam"), picture_line("w_laser", 2 * p["w_laser"], p["w_lw"], p["w_ldelay"]),
                    cone("w_beam", p["w_laser"], p["w_cos"], p["w_lapply"] + 1, p["w_lapply"], "EnemyWithoutTower",
                         [*w_hit, view("w_hit")]))
    hit = combine(*w_hit, view("w_hit"), tsfx("w_hit"), on_me(flag("w_unit", 3)),
                  pick(1000, "EnemyChampion", on_me(flag("w_champ", 3)), champ_hit, sw("p_full", spark()), fp=True))
    stop = combine(sw("w_unit", sw("w_champ", NONE, laser)), *rm("w_unit", "w_champ"))
    if native:     # the add-on turns a pulse that meets a wall into its laser and lays w_wall: the pulse is spent there
        hit, stop = sw("w_wall", NONE, hit), sw("w_wall", NONE, stop)
    pulse = line("w_pulse", p["w_speed"], p["w_len"], p["w_r"], p["a_y"], "EnemyWithoutTower", False, [hit], end=[stop])
    go = [refresh("w_go", p["w_len"] // p["w_speed"] + 2), *rm("w_wall")] if native else []

    def w_fire(pose):
        out = [refresh("w_cd", p["w_cd"]), sfx("w_cast"), voice("vo_w", p), cview("w_cast"),
               delayed(p["w_rel"], sfx("w_launch"), *go, pulse)]
        if pose:
            out.insert(0, anim("skill", p["w_dur"]))
        return combine(*out)

    skill = action("skill", p["w_dur"], p["w_cd"], 1, p["w_range"], "Direction", "EnemyWithoutTower",
                   sw("w_cd", NONE, w_fire(False)))

    # ------------------------------------------------------------------ E Spark Surge
    def e_fire():
        dash = combine(
            pick(p["e_near"], "EnemyChampion", flag("e_near", 1), anim("skill2_back", p["e_dur"]),
                 {"type": "MoveBack", "speed": p["e_dist"] // 5, "tick": 5}),
            sw("e_near", NONE, combine(
                pick(p["atk_range"], "EnemyWithoutTower", flag("e_in", 1)),
                sw("e_in", combine(anim("skill2_back", p["e_dur"]),
                                   {"type": "MoveBack", "speed": p["e_dist"] // 6, "tick": 6}),
                   combine(anim("skill2", p["e_dur"]),
                           {"type": "RushTime", "speed": p["e_dist"] // 10, "tick": 10, "range": p["e_dist"],
                            "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": []})))))
        follow_w = delayed(p["e_dur"], sw("w_cd", NONE, pick(p["w_range"], "EnemyChampion", w_fire(True))))
        return combine(refresh("e_cd", p["e_cd"]), refresh("e_on", p["e_t"]), *rm(*ecs), sfx("e_cast"),
                       voice("vo_e", p), cview("e_cast"), dash, delayed(10, sfx("e_land")), follow_w)

    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    sw("e_cd", NONE, e_fire()))

    # ------------------------------------------------------------------ R Lightning Crash
    def count():
        """2-tick flags u1 -> u2: two enemy champions within r_count."""
        return combine(*rm("u1", "u2"),
                       around(p["r_count"], "EnemyChampion", [sw("u1", refresh("u2", 2), refresh("u1", 2))]))

    nova = combine(sfx("r_cast"), cview("r_nova"), fill(),
                   around(p["r_reach"], "EnemyWithoutTower",
                          [magic(p["r_dmg"], p["r_ap"]), attack(0, p["r_ratio"]), view("r_hit")]))
    keep = sw("r_ext", refresh("r_st2", p["r_poll"] + 2, attack_speed_mult=p["r_as"], move_speed_mult=p["r_ms"]))

    def fire(slot):
        out = [*rm("r_armed", "r_st2", "r_ext", *rs), refresh("r_on", p["r_t"], attack_speed_mult=p["r_as"],
                                                             move_speed_mult=p["r_ms"]),
               voice("vo_r", p), sfx("r_buff"),
               on_me(delayed(p["r_t"], casted(p["r_ext_t"], p["r_poll"], keep)))]
        if slot:     # the cast pose, the nova on r_rel, then E when it is ready (R -> E)
            out += [anim("ult", p["r_anim"]), delayed(p["r_rel"], nova),
                    delayed(p["r_anim"], sw("e_cd", NONE, pick(p["r_reach"], "EnemyChampion", e_fire())))]
        else:
            out.append(nova)
        return combine(*out)

    arm = combine(refresh("r_armed", p["r_arm"]), refresh("r_wait", p["r_hold"]),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    ult = action("ult", 3, p["r_cd"], 1, p["r_slot"], "Targeting", "EnemyChampion",
                 combine(count(), sw("u2", fire(True), arm)))

    # armed: two champions in reach fire it from an attack, or one in reach once r_hold ticks have passed
    solo = combine(*rm("r_solo"), pick(p["r_reach"], "EnemyChampion", flag("r_solo", 2)), sw("r_solo", fire(False)))
    go = sw("r_armed", combine(count(), sw("u2", fire(False), sw("r_wait", NONE, solo))))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(read_hits, go, shoot), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    # flying rounds drawn top-bottom symmetric; buffs, hits and caster pictures left-right symmetric; the laser's
    # picture a hitless line (its right half from the centre), never a zone's own picture
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_burst"), P_("e_shot"), P_("r_shot"), P_("p_spark"), P_("w_pulse"), P_("w_laser", BIG, 2)]
    views_e = [E("a_hit"), E("p_hit"), E("p_ready", FX, 3), E("w_cast", FX, 3), E("w_hit"), E("e_cast", BIG, -1),
               E("e_hit"), E("r_nova", BIG, -1), E("r_hit"), E("r_zap")]
    views_b = [B_("p_slow", FX, -1), B_("w_slow", FX, -1), B_("p_haste", FX, -1), B_("e_on", FX, 3),
               B_("r_on", BIG, 2), B_("r_st2", BIG, 2)]
    views_b.insert(2, B_("p_shv", FX, 3))     # the shield's picture: the data's shield, or the add-on's stolen one
    if native:     # the add-on's laser from a wall (a projectile it spawns, turned with its flight)
        views_p.append(P_("w_wall", BIG, 2))
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_zeri:battery",
                          "params": {"steal": p["p_steal"], "steal_t": p["p_sh_t"], "w_laser": p["w_laser"],
                                     "w_speed": p["w_speed"], "w_dmg": p["w_dmg"], "w_ratio": p["w_ratio"],
                                     "w_slow": p["w_slow"], "w_slow_t": p["w_slow_t"], "w_lw": p["w_lw"]}}
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (addons/league_zeri/make_override.py)")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, a.native)
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
