"""Build league_taliyah.data_champion (mid, Magician: Taliyah, the Stoneweaver) from the parameters P.

    python tools/kit/build_taliyah.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-24: MID, layout A - Q / W with E folded in / R; combos W's throw through the mines = a
stun, Q on Worked Ground = the boulder, R's wall -> W at once into the wall, the surf's haste after R and out of fights).
TFM2 has three active slots for League's four buttons: Threaded Volley (Q) is `skill`, Seismic Shove (W) `skill2` with
Unraveled Earth (E) laid first, Weaver's Wall (R) the `ult`; Rock Surfing is the passive. W keeps its cooldown in a flag
(`w_cd`, league_singed's way) so R can cast it; the slot cast while the flag is up does nothing (a 3-tick idle).
  passive Rock Surfing (浮石冲): out of fights she surfs - p_ms% move speed while no `fight` flag is up (her hits on
          champions raise it for f_t ticks; the last one's Delayed puts the surf back f_t ticks later, league data
          has no "near a wall"); after R r_ms% for r_surf ticks (she surfs her wall).
  attack  A thrown pebble (100% AD): a homing rock at a_speed released on a_rel; its champion-only twin raises `fight`.
  skill   Q Threaded Volley (石穿), `Position` on `EnemyWithoutTower` (q_range): q_n rocks one every q_gap ticks along
          the line, each stopping on the first enemy (q_dmg + q_ap% AP; a wave soaks them, League's 50% on repeat hits
          is left out). The volley works the ground under her: a self-only zone (q_gr round, q_gt ticks) raises
          `on_ground` while she stands in it. Q cast on Worked Ground (combo) throws one boulder instead: q_b_dmg +
          q_b_ap% AP and q_b_slow% for q_b_slow_t ticks to every enemy on its line, and spends the ground (`q_used`
          until it would have ended; a volley lays new ground).
  skill2  W Seismic Shove (岩突) with E Unraveled Earth (撒石阵), `Targeting` on `EnemyChampion` (w_range, `w_cd`): she
          sweeps the mines out first - they land with the eruption, a field e_r round for e_t ticks slowing e_slow%
          (League's minefield) - and the ground erupts w_delay ticks after w_rel where the target stood: w_dmg + w_ap%
          AP to every enemy in w_r, thrown toward her (`Grab` w_go x w_throw: a Grab heads for the caster even from a
          projectile, league_anivia) right through the mines, which blow up on them as they land (combo): e_dmg +
          e_ap% AP and an e_stun-tick stun. With her wall standing (`r_wall`) she shoves them away from her instead,
          into the wall (Knockback r_kb_speed x r_kb) and they are stunned r_wstun ticks against it.
  ult     R Weaver's Wall (墙幔), `Targeting` on `EnemyChampion` (r_range): a long upright wall (`Rect` r_w x r_h,
          axis-aligned: always upright on the screen) rises where the target stands r_rel ticks after the cast and
          stays r_t ticks: whoever stands on it when it rises is dragged out to her side (league_anivia's Grab field,
          r_out ticks), every r_p ticks each enemy touching it is slowed r_slow% (stuck at its edge) - when an enemy
          champion is within r_near or she is already in a fight. R -> W (combo): r_w_at ticks later she casts W on
          the target at once if W is ready (r_reset 1: always, its cooldown started over), shoving it into the wall.
          Otherwise (the target far, no fight) she lays a long horizontal wall from her toward it (r_n stretches r_seg
          apart, picture r_wall_h, the same slow) and rides its crest in RushTime steps (r_speed x r_step, r_steps at
          most), jumping off as soon as an enemy champion is within r_off - W at once if ready (the eruption throws
          the target across her mines). Either way she surfs (the passive's r_ms%) for r_surf ticks.
The add-on's copy (--native, addons/league_taliyah/make_override.py): the walls neither slow nor drag - the passive
`league_taliyah:wall` makes them real terrain, found from the `wall_up` / `lay_up` flags and the `aim` mark on the target.
Timings: drafts until the frames exist (a rig script retimes them).
Numbers: League 16.21 read into the mid mage range (league_aurora, league_syndra); balanced on the classic-SDK
simulations (kd.py --lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, C:/t/ta_sim,
2026-10-24; league_aurora +0.93 on seeds 1-8): the draft (mines stun 50 every W, the wall 99%, Q 26 + 14%, W 70 + 40%,
mines 80 + 40%) +4.58 - she won by crowd control alone; the stun 24, W every 16 s, the wall 50% and its stun 40, the
surf 10% with every hit cut +0.47 (deal 5214 against Aurora's 11398); damage back - Q 32 + 17% a rock, W 60 + 35%,
mines 45 + 28% +0.85 / +1.89 on seeds 1-8 / 9-16 (mean +1.37: league_syndra +1.17 / +1.42, league_anivia +1.29);
the wall's band widened to r_w 12000 (it was thinner than its 16-px picture: a champion dragged out still stood in it)
+1.68 / +1.65 - the wall's slow and slam drive it (Q 29 + 15% left it at +1.67 / +1.61); the slow 35% and the slam 32
ticks +0.72 / +0.61; the slow 42% and the slam 36 ticks +1.02 / +1.25 (mean +1.14).
The skills redone as League (the user, 2026-10-24: Q's rocks a beat apart, the mines in front of her, the ride with the
horizontal wall): the ride as one MoveToTarget (always all the way: into them) -0.71 .. -1.28; in RushTime steps
with the jump-off at r_off +1.48 / +2.21 - every R a free W (its cooldown reset), a sure stun across the mines; damage,
health or R's cooldown cut barely moved it (+1.45 .. +2.2); R -> W only when W is ready (r_reset 0) = P +0.55 / +1.12 /
+1.81 / +2.21 on seeds 1-32 (mean +1.42: league_syndra +1.17 / +1.42) - but the AI always casts W before R, so in
a trace the R -> W slam never came (4 upright walls, 0 slams); the combo kept (r_reset 1) with every hit cut (Q 46 +
24% a rock, repeats 23 + 12%, W 50 + 30%, mines 38 + 24%) = P +1.62 / +1.39 / +1.73 / +1.38 on seeds 1-32 (mean +1.53).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_taliyah.data_champion")
ID = "league_taliyah"
FX = "asset/league/effects/league_taliyah_fx"
BIG = "asset/league/effects/league_taliyah_big"

# League's Taliyah (16.21): 550 +104 hp, 18 armour, 30 mr, 330 move, 525 range. Q: 5 rocks, 45-145 + 50% AP (repeat hits
# on one target 50%), Worked Ground: the boulder slows, cd 7-3. W: 900 range, erupts after 0.8 s, 60-260 + 40% AP, the
# throw toward her choice, cd 14-8. E: 950 range, 60-160 + 60% AP and a 1 s stun per mine (dashed or thrown through), 20%
# slow, 4 s, cd 14. R: a 2500-6500 wall for 4 s, she surfs it, cd 180-120. Passive: 15-45% move speed near walls.
# League units x 100 = ours (attack range 525 -> 55000 like every mid); radii count ~15000 of collision on top.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9; league_aurora 960)
    "hp": 920, "hp_g": 95, "atk": 68, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 19, "def_g": 6, "mr": 26, "mr_g": 4,
    "ms": 890, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 90, "a_rel": 10, "a_speed": 4500, "f_t": 240,
    # passive: Rock Surfing
    "p_ms": 10,
    # skill: Q Threaded Volley
    "q_cd": 360, "q_range": 90000, "q_dur": 16, "q_rel": 8, "q_n": 5, "q_gap": 12, "q_speed": 4500, "q_w": 4000,
    "q_dmg": 46, "q_ap": 24, "q_dmg2": 23, "q_ap2": 12, "q_gr": 14000, "q_gt": 480, "q_p": 3,
    "q_b_dmg": 110, "q_b_ap": 60, "q_b_w": 7000, "q_b_speed": 3500, "q_b_slow": 40, "q_b_slow_t": 90,
    # skill2: W Seismic Shove with E Unraveled Earth
    "w_cd": 960, "w_range": 80000, "w_dur": 36, "w_rel": 21, "w_delay": 30, "w_r": 16000, "w_dmg": 50, "w_ap": 30,
    "w_go": 3500, "w_throw": 10,
    "e_r": 22000, "e_t": 240, "e_p": 6, "e_slow": 20, "e_dmg": 38, "e_ap": 24, "e_stun": 24, "e_rel": 14, "e_dist": 25000,
    "e_speed": 6000,
    # ult: R Weaver's Wall
    "r_cd": 4200, "r_range": 90000, "r_dur": 40, "r_rel": 16, "r_t": 300, "r_w": 12000, "r_h": 120000, "r_out": 24,
    "r_go": 2500, "r_p": 2, "r_slow": 42, "r_w_at": 30, "r_kb_speed": 2500, "r_kb": 8, "r_wstun": 36,
    "r_ms": 40, "r_surf": 300,
    # the ride (a target beyond r_near, out of a fight): r_n wall stretches r_seg apart laid from her toward it; from
    # r_ride_at she rides it in steps (r_speed for r_step ticks each, r_steps at most) and jumps off as soon as an enemy
    # champion is within r_off (W + E's sweet spot) or the steps run out - W at once on the target
    "r_near": 60000, "r_speed": 2500, "r_ride_at": 8, "r_step": 2, "r_steps": 8, "r_off": 55000, "r_seg": 26000,
    "r_n": 6, "r_lay_speed": 8000,
    # 1: R starts W's cooldown over and casts it at once; 0: R casts W only when it is ready
    "r_reset": 1,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1: the add-on's copy (addons/league_taliyah: the walls real terrain)
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


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


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


def rect(w, h):
    return {"Rect": {"width": w, "height": h}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=ap):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, width, target, effects, end=(), penetrate=False):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "shape": circle(width),
            "penetrate": penetrate, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def anchor(name, end):
    """A 1-unit line whose end_effects start zones where she stands (league_gwen's mist)."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": "Ally",
            "applied_effects": [], "end_effects": list(end), "speed": 1, "range": 1, "shape": circle(1000),
            "y_offset": 0}


def lob(name, travel, end, target="EnemyChampion"):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, shape, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": shape, "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def field(name, shape, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": shape, "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Rock Surfing
    # a hit on a champion: the fight - no surf until f_t ticks after the last one (that one's Delayed puts it back)
    surf = flag("surf", None, move_speed_mult=p["p_ms"])
    fight = [*rm("surf"), refresh("fight", p["f_t"]), delayed(p["f_t"] + 1, alive(sw("fight", NONE, sw("surf", NONE, surf))))]

    # ------------------------------------------------------------------ skill: Q Threaded Volley
    rng = p["q_range"] + 10000

    def rock(k):
        """The k-th rock (League's repeat rocks: half damage), thrown from where she is then - she walks on after the
        first (the action ends at q_dur; the rest follow by Delayed)."""
        hit = [ap(p["q_dmg"], p["q_ap"]) if k == 0 else ap(p["q_dmg2"], p["q_ap2"]), view("q_hit"), tsfx("q_hit")]
        return alive(sfx("q_rock"), line("q_rock", p["q_speed"], rng, p["q_w"], "EnemyWithoutTower", hit))
    volley = [delayed(k * p["q_gap"], rock(k)) for k in range(p["q_n"])]
    ground = anchor("q_work", [field("q_ground", circle(p["q_gr"]), p["q_gt"], p["q_p"],
                                     [refresh("on_ground", p["q_p"] + 1)], target="AllyOnlySelf", first=0)])
    boulder_hit = [ap(p["q_b_dmg"], p["q_b_ap"]), buff("q_slow", p["q_b_slow_t"], move_speed_mult=-p["q_b_slow"]),
                   view("q_big_hit"), tsfx("q_big_hit")]
    boulder = combine(refresh("q_used", p["q_gt"]), sfx("q_big"),
                      line("q_boulder", p["q_b_speed"], rng, p["q_b_w"], "EnemyWithoutTower", boulder_hit,
                           penetrate=True))
    threads = combine(*rm("q_used"), ground, on_me(view("q_ground")), *volley)
    q_cast = combine(anim("skill", p["q_dur"]), voice("vo_q", p), delayed(p["q_rel"] - 1, alive(
        # Worked Ground: on it (and not spent) the boulder, else a volley and new ground (combo); the volley written once
        sw("on_ground", sw("q_used", NONE, flag("big", 1))), sw("big", combine(*rm("big"), boulder), threads))))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"] * 3, p["q_ap"] * 3), q_cast))

    # ------------------------------------------------------------------ skill2: W Seismic Shove + E Unraveled Earth
    def w_cast(target):
        mines = field("e_mines", circle(p["e_r"]), p["e_t"], p["e_p"],
                      [buff("e_slow", p["e_p"] + 6, move_speed_mult=-p["e_slow"])], first=0)
        blast = [ap(p["e_dmg"], p["e_ap"]), {"type": "Stun", "duration": p["e_stun"]}, view("e_blast"),
                 tsfx("e_blast")]
        # thrown toward her through the mines, which blow up as they land
        toward = zone("w_up", circle(p["w_r"]), [ap(p["w_dmg"], p["w_ap"]), {"type": "Grab", "speed": p["w_go"],
                                                                           "tick": p["w_throw"]},
                                                 view("w_hit"), tsfx("w_hit"),
                                                 delayed(p["w_throw"], *blast)])
        # her wall standing: shoved away, into it, and stunned against it (combo)
        into = zone("w_up_r", circle(p["w_r"]), [ap(p["w_dmg"], p["w_ap"]), {"type": "Knockback",
                                                                            "speed": p["r_kb_speed"], "tick": p["r_kb"]},
                                                 view("w_hit"), tsfx("w_hit"),
                                                 delayed(p["r_kb"], {"type": "Stun", "duration": p["r_wstun"]},
                                                         view("e_blast"), tsfx("r_slam"))])
        champ = zone("w_up_c", circle(p["w_r"]), fight, target="EnemyChampion")
        erupt = [view("w_erupt"), sfx("w_erupt"), champ, sw("r_wall", into, toward)]
        # E first: the mines thrown onto the ground in front of her (e_dist toward the target), then W's warning crack
        # under the target and the eruption w_delay later - the throw toward her carries it across the mines
        toss = line("e_toss", p["e_speed"], p["e_dist"], 1000, "Ally", [],
                    end=[mines, view("e_mines"), sfx("e_land")], penetrate=True)
        return combine(refresh("w_cd", p["w_cd"]), anim("skill2", p["w_dur"]), sfx("w"), voice("vo_w", p),
                       delayed(p["e_rel"] - 1, alive(toss)),
                       delayed(p["w_rel"] - 1, alive(lob("w_warn", 1, [view("w_warn")], target),
                                                     lob("w_mark", p["w_delay"], erupt, target))))

    skill2 = action("idle", 3, 60, 1, p["w_range"], "Targeting", "EnemyChampion",
                    combine(decoy(p["w_dmg"] + p["e_dmg"], p["w_ap"] + p["e_ap"]),
                            sw("w_cd", NONE, w_cast("EnemyChampion"))), key="skill2")

    # ------------------------------------------------------------------ ult: R Weaver's Wall
    native = bool(p["native"])
    # the add-on's copy (native): no slow and no drag - addons/league_taliyah makes the walls real terrain (it finds the
    # upright one under the champion carrying `aim` the tick `wall_up` rises, the ride's stretches from her spot toward
    # that champion the tick `lay_up` rises, snapped onto the stretches' empty zones)
    marks = lambda up: [flag(up, 3), buff("aim", 3)] if native else []
    wall = [view("r_wall"), sfx("r_wall")] if native else [view("r_wall"), sfx("r_wall"),
            # on it when it rises: dragged out to her side (a Grab heads for the caster, league_anivia)
            field("r_out", rect(p["r_w"], p["r_h"]), p["r_out"], 2, [{"type": "Grab", "speed": p["r_go"], "tick": 2}],
                  first=1),
            field("r_stone", rect(p["r_w"], p["r_h"]), p["r_t"], p["r_p"],
                  [buff("r_stuck", p["r_p"] + 2, move_speed_mult=-p["r_slow"])], first=1)]
    # R -> W only for Taliyah herself (`own`, a flag her attack raises): league_sylas's copy steals the ult tree, and
    # League's Sylas gets the wall (and the ride), not her Shove
    w_now = sw("own", combine(*rm("w_cd"), w_cast("EnemyChampion")) if p["r_reset"] else
               sw("w_cd", NONE, w_cast("EnemyChampion")))
    surf_on = refresh("r_surf", p["r_surf"], move_speed_mult=p["r_ms"])
    # near (an enemy champion within r_near): the upright wall where the target stands, then W into it
    upright = combine(anim("ult", p["r_dur"]), delayed(p["r_rel"] - 1, alive(
        refresh("r_wall", p["r_t"]), *marks("wall_up"), lob("r_mark", 1, wall), surf_on,
        # R -> W at once on the same champion, into the wall (W's cooldown starts over)
        delayed(p["r_w_at"], alive(w_now)))))
    # far: she rides - a long horizontal wall laid from her toward the target (r_n stretches r_seg apart: hidden lines
    # flying 0, r_seg, 2 r_seg ... and laying a Rect r_seg long and r_w thick where each stops, its picture r_wall_h),
    # then rides along it step by step (League: she jumps off wherever she likes): before every step (a RushTime of
    # r_speed x r_step toward the target, the action's own) she looks round her - an enemy champion within r_off and she
    # jumps off there, the shove at once on the target (R -> W: the eruption throws it across her mines); with nobody
    # that near she rides on, r_steps at most, and jumps off at the end. `riding` is up while she rides; jumping off
    # takes it down, so the steps after it do nothing; W's CasterAnimation ends the ride's.
    stretch = [view("r_wall_h"),
               field("r_seg", rect(p["r_seg"], p["r_w"]), p["r_t"], p["r_p"],
                     [] if native else [buff("r_stuck", p["r_p"] + 2, move_speed_mult=-p["r_slow"])], first=1)]
    lay = [line("r_lay", p["r_lay_speed"], k * p["r_seg"] + 1, 1000, "Ally", [], end=stretch, penetrate=True)
           for k in range(p["r_n"])]
    ride_t = p["r_steps"] * p["r_step"]
    jump_off = combine(*rm("riding"), w_now)
    step = combine(pick(p["r_off"], "EnemyChampion", flag("off", 1)),
                   sw("off", combine(*rm("off"), jump_off),
                      # RushTime: speed x tick toward the target and stops (MoveToTarget always goes all the way: a
                      # first ride with 8 short MoveToTargets carried her 125 px into them - champion-data section 4)
                      {"type": "RushTime", "speed": p["r_speed"], "tick": p["r_step"], "range": 12000,
                       "casting_target": "EnemyChampion", "penetrate": True, "applied_effects": []}))
    ride = combine(anim("ult_ride", p["r_ride_at"] + ride_t + 4), sfx("r_wall"),
                   refresh("riding", p["r_ride_at"] + ride_t + 2),
                   delayed(p["r_ride_at"] - 1, alive(surf_on, *marks("lay_up"), *lay)),
                   # the steps from one pulse laid on the target (its effects run with the target as theirs, so the
                   # MoveToTarget heads for it; written once, not r_steps times)
                   delayed(p["r_ride_at"] - 1, alive(casted(ride_t, p["r_step"], sw("riding", step)))),
                   delayed(p["r_ride_at"] - 1 + ride_t, alive(sw("riding", jump_off))))
    # near = an enemy champion within r_near, or she is already in a fight (`fight`: she hit a champion within f_t
    # ticks) - the AI casts R the moment a champion comes into r_range, so by distance alone she always rode in
    r_cast = combine(sfx("r"), voice("vo_r", p), pick(p["r_near"], "EnemyChampion", flag("near", 1)),
                     sw("fight", flag("near", 1)),
                     sw("near", combine(*rm("near"), upright), ride), *rm("near"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["w_dmg"] + p["e_dmg"], p["w_ap"] + p["e_ap"]), r_cast), key="ult")

    # ------------------------------------------------------------------ attack
    pebble = combine(sfx("a"), homing("a_rock", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"]),
                     homing("a_rock_c", "EnemyChampion", fight, p["a_speed"]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100, attack), sw("own", NONE, flag("own", None)),
                              sw("fight", NONE, sw("surf", NONE, surf)),
                              delayed(p["a_rel"] - 1, alive(pebble))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("a_rock"), Pj("q_rock"), Pj("q_boulder")]
    views_e = [E("a_hit"), E("q_hit"), E("q_big_hit"), E("q_ground", BIG, -2, False), E("w_hit"),
               E("w_erupt", BIG, 2, False), E("e_mines", BIG, -2, False), E("e_blast"), E("r_wall", BIG, -1, False),
               E("r_wall_h", BIG, -1, False), E("w_warn", BIG, -2, False)]
    views_b = [B_("q_slow", FX, -1, "slow"), B_("e_slow", FX, -1, "slow"), B_("r_stuck", FX, -1, "slow"),
               B_("surf", FX, -1, "surf"), B_("r_surf", FX, -1, "surf")]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_taliyah:wall", "params": {
            k: p[k] for k in ("r_t", "r_w", "r_h", "r_seg", "r_n", "r_lay_speed")}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"], **extra,
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
