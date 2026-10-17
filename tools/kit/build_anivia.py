"""Build league_anivia.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_anivia.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-17: 「全按推荐做：主包近似蛋、W 折进 Q、做扩展包三项、PPU 1.2、加高手连招」, then 「冰墙我要的是
真的墙 可以卡住人的那种」). TFM2 has three active slots: Flash Frost is `skill`, Frostbite `skill2`, Glacial Storm the
`ult`; Crystallize (W) rides on Q, Rebirth is the watch's.
  attack  an ice bolt (100% AD), a homing bolt at a_speed released on a_rel; its champion-only twin marks the fight.
  skill   Q Flash Frost (寒冰闪耀), `Position` on `EnemyWithoutTower` (q_range): the cast point is where the target
          stood (League's skillshot: walking off the line dodges it). A hidden ball on `EnemyWithoutTower` passes
          through (q_pass + q_pass_r% AP and q_slow% for q_slow_t ticks); the seen ball, a champion-only twin on the
          same line, stops on the first enemy champion or at the cast point and blows up there (League's recast at
          the right moment): q_dmg + q_ratio% AP and a q_stun-tick stun in q_r, a champion-only twin zone of the same
          size flags the stun (`q_stc`).
  W       Crystallize (寒冰屏障), on Q: two ticks after a blast that stunned a champion, with `w_cd` off, a wall stands
          on the blast point for w_t ticks: a `Rect` w_w x w_h (axis-aligned, so always upright on the screen - the
          fights run left-right), its picture ice blocks stacked up (never turned). Enemies on it when it rises are
          pulled w_pull toward her (League pushes them off); every w_p ticks each enemy touching it gets w_slow% (a
          slow, not crowd control) for w_p + 2 ticks: whoever walks into it, from either side, stops at its edge
          until it melts. The add-on's wall is real terrain (nobody passes, allies neither).
  combo   (the user's 「加高手连招」) Q stuns -> the wall behind -> Frostbite (doubled on the stunned champion) ->
          Glacial Storm (the watch's R fires on a champion in crowd control first).
  skill2  E Frostbite (霜寒刺骨), `Targeting` on `EnemyWithoutTower` (e_range): an ice shard (e_dmg + e_ratio% AP).
          Doubled on an Iced target: League's Iced = 3 s after Flash Frost or a fully formed storm hit. The data reads
          no state on the target, so the main pack doubles when the target is in crowd control (a twin on
          `EnemyChampionInCC`, read at the hit: Q's stun) or when her storm is fully formed and has struck a champion
          within r_ice ticks (`r_ice`, a flag on her: approximate). The add-on reads the real per-target mark.
  ult     R Glacial Storm (冰川风暴): the slot (a 3-tick `Targeting` on `EnemyChampion` within r_range) only arms the
          ult for r_arm ticks (league_swain / league_nasus); the watch drops the storm on an enemy champion in
          crowd control within r_range, else - with two enemy champions within r_cnt of her - on one recently hit.
          Unused, the window ends with the cooldown capped at 60 ticks (`r_retry`). The storm stands r_t ticks where
          the champion stood: it grows r_r0 -> r_r1 -> r_r2 (r_grow ticks each) to r_r (fully formed); every r_p
          ticks r_dmg + r_ratio% AP and r_slow% (formed: x r_full, r_slow2%).
  passive Rebirth (寒霜涅槃): the add-on's alone (the user's pick after the simulation: a danger rule in the data egged
          her at 20-100% health - the data reads no health and nothing fires on a death). With the add-on: the lethal
          hit leaves her at 1 health, she curls into the egg with her full health as the egg's, armour and magic
          resistance -egg_def, for egg_t ticks; the egg broken is her death (the killer's); whole, she hatches with the
          egg's health. Once every egg_cd ticks, kept across deaths. The main pack's tooltip says it needs the add-on.
The add-on copy (--native): the passive `league_anivia:rebirth` decides the egg (the copy shows it: `egg_go` /
`egg_hatch` flags, a 2-tick watch), the wall (real terrain: the copy's wall has no slow ring, `w_slow` 0) and the
per-target Iced mark (both packs lay `iced` on the champions Q and the formed storm strike, ice_t ticks; in the copy
E's hit raises `e_now` on her for a tick and the add-on's on_attack doubles it on an `iced` target).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_anivia.data_champion")
ID = "league_anivia"
FX = "asset/league/effects/league_anivia_fx"
BIG = "asset/league/effects/league_anivia_big"

# Numbers = the 10-min classic-SDK simulations (mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and
# white_mage, three lineups, both sides, 8 seeds, 2026-10-17; league_syndra +1.17 / +1.42 on seeds 1-8 / 25-32): the
# draft (Q 70 + 50%, E 55 + 55%, R 25 + 10%, hp 880) -0.40 / -0.67 (deal 7060-7255); +25% damage +0.70; +40% and Q every
# 7 s +1.61 / +2.03 (too strong); between (Q 95 + 65%, pass 55 + 32%, E 75 + 65%, R 32 + 13%, hp 900, Q every 7.5 s)
# +0.90 on 25-32; on seeds 9-16 with Q every 7 s +1.93, every 7.5 s +1.45 (league_syndra +1.22). P = Q every 7.5 s.
# League units x 100 = ours (attack range 600 -> 55000 like every mid); radii count the unit's collision radius
# (~15000) on top, so League's 225 blast is q_r 14000.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Anivia:
    # 550 +92 hp, 21 armour, 30 mr, 325 move (slow), 600 range
    "hp": 900, "hp_g": 95, "atk": 76, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 880, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 28, "atk_cd": 90, "a_rel": 10, "a_speed": 4500, "f_t": 180,
    # Q Flash Frost (League: 1100 range, speed 950, pass 50-130 +25%, slow 20-40% 3 s, blast 60-200 +45%, stun
    # 1.1-1.5 s r225, cd 11-7)
    "q_cd": 450, "q_range": 95000, "q_dur": 24, "q_rel": 9, "q_speed": 1600, "q_w": 5000, "q_pass": 55, "q_pass_r": 32,
    "q_slow": 30, "q_slow_t": 180, "q_dmg": 95, "q_ratio": 65, "q_stun": 66, "q_r": 14000,
    # W Crystallize (League: width 400-1000, 5 s, cd 17)
    "w_cd": 900, "w_t": 300, "w_w": 8000, "w_h": 50000, "w_p": 2, "w_slow": 99, "w_pull": 16000, "w_mode": 0,
    # E Frostbite (League: 600 range, speed 1600, 55-155 +55%, doubled on Iced, cd 4)
    "e_cd": 300, "e_range": 65000, "e_dur": 24, "e_rel": 9, "e_speed": 2700, "e_dmg": 75, "e_ratio": 65,
    # the combo's Frostbite after a stun (its own cooldown, e_cd)
    "e_combo": 1, "e_combo_at": 10, "ice_t": 180,
    # R Glacial Storm (League: 750 range, r 200 -> 400 over 1.5 s, every 0.5 s 15-30 +6.25% AP, slow 20-40%;
    # formed x3 and 30-60%)
    "r_cd": 2400, "r_range": 75000, "r_arm": 600, "r_dur": 24, "r_rel": 10, "r_t": 360, "r_grow": 30,
    "r_r0": 12000, "r_r1": 18000, "r_r2": 24000, "r_r": 32000, "r_p": 30, "r_dmg": 32, "r_ratio": 13, "r_full": 3,
    "r_slow": 25, "r_slow2": 45, "r_ice": 60, "r_cnt": 45000,
    # Rebirth, the add-on's (League: 6 s egg, -40..-20 armour / mr, cd 240 s)
    "egg_t": 360, "egg_def": 20, "egg_cd": 14400, "egg_in": 12, "egg_out": 18,
    "watch_p": 12,
    "vo_gap": 600,
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


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else ("WithShield" if tick == "shield" else {"Time": {"tick": tick}})
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
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


def rect(w, h):
    return {"Rect": {"width": w, "height": h}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Caster"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, width, target, effects, end, penetrate):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "shape": circle(width),
            "penetrate": penetrate, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def lob(name, travel, end, target="EnemyWithoutTower"):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, shape, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": shape, "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, shape, tick, period, effects, first=None, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": shape, "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # a champion struck: the fight
    marked = [refresh("fight", p["f_t"])]

    # ------------------------------------------------------------------ E: Frostbite (the shard, its doubles)
    def shard(name):
        if native:      # the add-on doubles the hit on a target carrying `iced` (its on_attack sees `e_now` on her)
            hit = [refresh("e_now", 1), ap(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]
            return combine(homing(name, "EnemyWithoutTower", hit, p["e_speed"]),
                           homing(f"{name}_st", "EnemyChampion", marked, p["e_speed"]))
        hit = [ap(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]
        iced = [ap(p["e_dmg"], p["e_ratio"]), view("e_iced"), refresh("e_dbl", 1)]
        storm = [sw("e_dbl", NONE, sw("r_ice", combine(ap(p["e_dmg"], p["e_ratio"]), view("e_iced"))))]
        return combine(homing(name, "EnemyWithoutTower", hit, p["e_speed"]),
                       homing(f"{name}_cc", "EnemyChampionInCC", iced, p["e_speed"]),
                       homing(f"{name}_st", "EnemyChampion", storm + marked, p["e_speed"]))

    # League's Iced mark on a champion (3 s after Flash Frost or the formed storm): seen in both packs, read by the add-on
    iced = buff("iced", p["ice_t"])

    # ------------------------------------------------------------------ W: Crystallize (on Q's stun)
    wall_view = [view("w_wall"), sfx("w")]
    rise = [zone("w_rise", rect(p["w_w"], p["w_h"]), [{"type": "Pull", "speed": 2000, "tick": p["w_pull"] // 2000}])]
    if p["w_slow"]:
        rise.append(field("w_ice", rect(p["w_w"], p["w_h"]), p["w_t"], p["w_p"],
                          [buff("w_stuck", p["w_p"] + 2, move_speed_mult=-p["w_slow"])] if not p["w_mode"] else
                          [{"type": "Bind", "duration": p["w_p"] + 1}, buff("w_stuck", p["w_p"] + 2)], first=1))
    else:       # the add-on's copy: the wall is real terrain; this hitless field only marks where it stands (the add-on
                # finds it among her zones the tick w_cd rises - the one-tick w_rise may be gone by then)
        rise.append(field("w_mark", circle(1), p["w_t"], p["w_t"], [], first=p["w_t"], target="EnemyChampion"))
    wall = sw("w_cd", NONE, combine(flag("w_cd", p["w_cd"]), voice("vo_w", p), *wall_view, *rise))

    # ------------------------------------------------------------------ skill: Q Flash Frost
    burst = [ap(p["q_dmg"], p["q_ratio"]), {"type": "Stun", "duration": p["q_stun"]}, view("q_stun"), tsfx("q_hit")]
    combo_e = []
    if p["e_combo"]:
        combo_e = [sw("e_cc", NONE, combine(flag("e_cc", p["e_cd"]),
                                            delayed(p["e_combo_at"], sfx("e"), shard("e_combo"))))]
    stc = [refresh("q_stc", 4), iced] + marked + combo_e
    blast = [view("q_blast"), sfx("q_blast"), zone("q_burst", circle(p["q_r"]), burst),
             zone("q_burst_c", circle(p["q_r"]), stc, target="EnemyChampion"),
             delayed(2, sw("q_stc", wall))]
    pass_ = [ap(p["q_pass"], p["q_pass_r"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
             tsfx("q_pass")]
    ball = combine(line("q_hide", p["q_speed"], p["q_range"] + 20000, p["q_w"], "EnemyWithoutTower", pass_, [], True),
                   line("q_ice", p["q_speed"], p["q_range"] + 20000, p["q_w"], "EnemyChampion", [iced], [], True),
                   line("q_ball", p["q_speed"], p["q_range"] + 20000, p["q_w"], "EnemyChampion", [], blast, False))
    frost = combine(sfx("q"), voice("vo_q", p), delayed(p["q_rel"] - 1, ball))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower", frost)

    # ------------------------------------------------------------------ skill2: E Frostbite
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), voice("vo_e", p), delayed(p["e_rel"] - 1, shard("e_shard"))))

    # ------------------------------------------------------------------ ult: R Glacial Storm (dropped by the watch)
    def ring(k, r, t, first, dmg, slow, formed):
        hit = [ap(dmg, p["r_ratio"] * (p["r_full"] if formed else 1)), buff("r_slow", p["r_p"] + 10,
                                                                           move_speed_mult=-slow), tsfx("r_hit")]
        f = [field(f"r_s{k}", circle(r), t, p["r_p"], hit, first=first)]
        if formed:      # a champion struck by the formed storm: Iced for r_ice ticks (her flag, approximate)
            f.append(field(f"r_s{k}c", circle(r), t, p["r_p"], [refresh("r_ice", p["r_ice"]), iced], first=first,
                           target="EnemyChampion"))
        return f

    g = p["r_grow"]
    storm = ([view("r_storm"), sfx("r_storm")]
             + ring(0, p["r_r0"], g, 1, p["r_dmg"], p["r_slow"], False)
             + [delayed(g, *ring(1, p["r_r1"], g, 1, p["r_dmg"], p["r_slow"], False))]
             + [delayed(2 * g, *ring(2, p["r_r2"], g, 1, p["r_dmg"], p["r_slow"], False))]
             + [delayed(3 * g, view("r_formed"), *ring(3, p["r_r"], p["r_t"] - 3 * g, 1, p["r_dmg"] * p["r_full"],
                                                          p["r_slow2"], True))])
    drop = combine(*rm("r_arm"), refresh("r_fired", 4), anim("ult", p["r_dur"]), cview("r_cast"), sfx("r"),
                   voice("vo_r", p), delayed(p["r_rel"] - 1, lob("r_lob", 1, storm)))

    # ------------------------------------------------------------------ passive: Rebirth - the add-on's alone
    # The main pack has no egg (the user, 2026-10-17: 「主包不做蛋，寒霜涅槃只放在扩展包里，说明写清楚」): the data reads no
    # health and nothing fires on a death; a danger rule (two enemy champions near, a long fight, her in crowd control)
    # egged her at 20-100% health in the simulation. The add-on's passive `league_anivia:rebirth` catches the lethal hit
    # (league_sion's undying guard), fills her health as the egg's and raises `egg_go`; the egg breaking is her death.
    # The data shows it: egg_go -> `egg_on` (armour and magic resistance -egg_def, egg_t ticks) and the curl-up, the egg
    # held by its loop every 30 ticks; `egg_hatch` (the add-on, egg_t ticks later with her alive) -> the hatch.
    egg_watch = NONE
    if native:
        t_ = p["egg_t"]
        start = sw("egg_go", combine(*rm("egg_go"), refresh("egg_on", t_, defence=-p["egg_def"],
                                                            magic_resistance=-p["egg_def"]),
                                     refresh("egg_hold", p["egg_in"]), anim("egg_in", p["egg_in"] + 2),
                                     cview("p_egg_in"), sfx("p_egg")))
        hold = sw("egg_on", sw("egg_hold", NONE, combine(flag("egg_hold", 30), anim("egg", 32))))
        out = sw("egg_hatch", combine(*rm("egg_hatch", "egg_on", "egg_hold"), anim("hatch", p["egg_out"]),
                                      cview("p_hatch"), sfx("p_hatch"), voice("vo_p", p)))
        egg_watch = casted(1000000, 2, start, hold, out)

    # ------------------------------------------------------------------ the watch (R's moment)
    tick = p["watch_p"]
    count = combine(*rm("c_e1", "c_e2"),
                    around(p["r_cnt"], "EnemyChampion", [sw("c_e1", flag("c_e2", 3), flag("c_e1", 3))]))
    fire = sw("r_arm", combine(pick(p["r_range"], "EnemyChampionInCC", drop),
                               delayed(1, sw("r_fired", NONE, sw("c_e2", pick(p["r_range"],
                                                                              "EnemyChampionRecentlyAttacked",
                                                                              drop))))))
    # in the add-on's copy the storm waits while she is an egg
    watch = on_me(casted(1000000, tick, count, delayed(1, sw("egg_on", NONE, fire) if native else fire)), egg_watch)
    life = sw("init", NONE, combine(flag("init", None), watch))

    # ------------------------------------------------------------------ attack: the ice bolt
    bolt = combine(sfx("a"), homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"]),
                   homing("a_twin", "EnemyChampion", marked, p["a_speed"]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, delayed(p["a_rel"] - 1, bolt)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ ult slot: arms the window
    retry = p["r_cd"] * 100 // 60 - 100
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_retry", 3, ult_cooldown_mult=retry)))
    arm_r = combine(refresh("r_arm", p["r_arm"]), on_me(delayed(p["r_arm"], reset)))
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), arm_r), ap(100, 100)), *rm("r_x"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(life, scored),
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                 "z": 2}
    # the projectiles are drawn pointing right and turned with the flight, so each is symmetric top to bottom (a ball, a
    # bolt, a shard); everything else is left-right symmetric (the client never mirrors a picture on the red side)
    Pj2 = lambda name, tag: {"type": "Animated", "name": n(name), "anim": FX, "tag": tag, "repeat": True, "z": 2}
    views_p = [Pj("a_bolt"), Pj("q_ball"), Pj("e_shard"), Pj2("e_combo", "e_shard")]
    views_e = [E("a_hit"), E("q_stun"), E("q_blast", BIG, 2, False), E("w_wall", BIG, 1, False), E("e_hit"),
               E("e_iced"), E("r_cast"), E("r_storm", BIG, -1, False), E("r_formed", BIG, -1, False)]
    if native:          # the egg's pictures (main pack sheets) bound only in the add-on's copy, the one that plays them
        views_e += [E("p_egg_in"), E("p_hatch")]
    views_b = [B_("iced", FX, 3)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_anivia:rebirth", "params": {
            "egg_t": p["egg_t"], "egg_cd": p["egg_cd"], "w_t": p["w_t"], "w_w": p["w_w"], "w_h": p["w_h"],
            "ice_t": p["ice_t"]}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "CC"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }


def nodes(o):
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
