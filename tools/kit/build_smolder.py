"""Build league_smolder.data_champion (bot lane, Range, ranged AD carry) from the parameters P.

    python tools/kit/build_smolder.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-14: a bot-lane AD carry; Q as skill on waves and camps too; W as skill2 with E on its own
flag when he is dived or chasing, Bard's way; R as ult; the passive as data stacks, Veigar's way, with all three Q tiers;
the add-on league_smolder - stacks kept through death, the tier-3 execute, a smart E over walls - builds its copy with
native=1, addons/league_smolder/make_override.py):
  passive Dragon Practice (龙之研习): every stack is one more instance of the `Permanent` caster buff p_st (+1 ability
          power: the gauge Q, W and E read for their per-stack damage, as league_veigar's and league_kindred's marks;
          nothing else of his reads ability power and he buys none). A champion Q hits (its champion-only twin, from tier
          1 the explosion's champion zone), each champion W's explosion hits, the first champion an E volley hits and a
          unit Q kills (league_jinx's kill check on the bolt's target) add one. Nothing reads a buff's count, so every
          stack also climbs a pending ladder pa1..pa<p_pend> (all on at k) that his next attack works off into a two-level
          counter - units u1..u<p_base - 1>, levels L1..L<t3 / p_base> (league_gwen's ladders: all on at k) - and the
          levels t1 / p_base, t2 / p_base and t3 / p_base raise the Permanent tier flags t1, t2, t3 (with the tier-up
          picture, sound and line). Death clears every data buff, so the stacks and tiers last one life here.
  attack  a small fireball spit (homing, physical); it also works off the pending stacks.
  skill   Q Super Scorcher Breath (超级灼热龙息): a `Targeting` cast on `EnemyWithoutTower` (q_range: waves and camps too)
          breathes a homing fireball on q_rel: q_dmg + q_ratio% AD physical + q_stack% AP (stacks) magic.
          Tier 1 (t1 stacks): the bolt itself deals nothing; a tick after its hit a hidden lob onto the target starts the
          explosion there (q_t1_r): the whole Q damage to the target and every enemy round it (League: the target once,
          its neighbours the same).
          Tier 2 (t2): the blowback - a hidden penetrating line flown with the bolt from the cast toward the target and on
          q_t2_len past it hits, from the bolt's hit on (league_missfortune Q's window: q_t2_win ticks, the first tick
          skipped so the target itself is spared), every enemy behind the target for q_t2_pct% of the Q damage; the
          three fireballs' picture is a hitless line laid from the explosion's spot away from him (league_viktor E).
          Tier 3 (t3): every unit the Q damage hits also burns (Fire, q_burn_t ticks, every q_burn_p: q_burn_dmg +
          q_burn_ratio% AD + q_burn_hp% of its maximum health as true damage). League's execute below 6.5% health reads
          health: the add-on's (not here).
  skill2  W Achooo! (阿嚏！) normally: a `Targeting` cast on w_target (`EnemyChampion`: on `EnemyWithoutTower` it went
          to waves and camps and blew up on a champion 5 times a game, against 8 - and +0.3 kills - on champions) within
          w_range, 3 ticks; the sneeze plays `CasterAnimation skill2` and leaves on w_rel (frame 4): a penetrating line
          (w_len, w_rad) - w_dmg + w_ratio% AD and a w_slow% slow for w_slow_t ticks to every enemy it passes - and its
          champion-only twin that stops on the first champion: a tick later the explosion there (w_x_r): w_x_dmg +
          w_x_ratio% AD + w_stack% AP (stacks).
          E Flap, Flap, Flap (扑棱，扑棱，扑棱！) instead when its own cooldown flag (e_cd, e_cd_t ticks) is off and he is
          dived - two enemy champions within e_near or one within e_close (league_bard E's count) - or chasing: no enemy
          champion within e_reach (his attack) and one his team hit lately (`EnemyChampionRecentlyAttacked`, the data's
          "wounded") within e_chase. `CasterAnimation skill2_e` (take-off 2 frames, flight 4, landing 2): the flight from
          e_wind for e_tick ticks - away from the nearest enemy champion (the first of the e_steps rings with one in it,
          MoveBack, e_speed a tick) or toward the wounded one (RushTime, e_fspeed a tick) - with ignore_wall (e_ghost)
          for the trip, e_ms% move speed for e_ms_t ticks, and e_n shots every e_gap ticks during the flight (an
          AddCasted on him) at a wounded enemy champion within e_r, else any enemy champion, else any enemy: e_dmg +
          e_ratio% AD + e_stack% AP (stacks) each; the first champion hit of a volley gives a stack. The smart vault
          over walls is the add-on's. In the simulation 5 E a game: 4.5 chases, 0.5 escapes (the slot is mostly on W's
          cooldown when he is dived).
  ult     R MMOOOMMMM! (妈----！): a `Direction` cast on r_target within r_range. He shouts on r_rel (frame 3); his
          mother's shadow flies over (r_mom, a picture on `Ally`) and r_lag ticks later her fire lies along the line from
          him (r_len long): r_dmg + r_ratio% AD to every enemy within r_w (+ the 15000 the line adds), the centre (r_cw)
          r_sweet% more and an r_slow% slow for r_slow_t ticks; if he still stands on the centre line when it lands he
          heals r_heal + r_heal_ad% AD (a line on `AllyOnlySelf`, League's sweet-spot heal). The fire comes from behind
          him in League (600 units); a line starts on him, so only the picture reaches back - and he stands on its start,
          so the heal lands on nearly every cast (4.8 of 4.8 a game in the simulation) unless he has walked 15000 off it.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_smolder.data_champion")
ID = "league_smolder"
FX = "asset/league/effects/league_smolder_fx"
BIG = "asset/league/effects/league_smolder_big"

# Timing from the sheet (league/champions/league_smolder#anim.fanim, assets/source/smolder/poses.json; ticks = ms x 0.06):
# attack 440 ms (26 ticks), the fireball leaves as frame 3 starts (140 ms: start_timing 8, the effect on tick 9); Q 480 ms
# (29), its breath on frame 3 (160 ms: start_timing 9, tick 10). skill2's 3-tick slot starts its CasterAnimation on its
# effect tick (2), so W's and E's moments count from there: W 460 ms (28), the sneeze on frame 4 (240 ms: w_rel 15 =
# 250 ms); E 1330 ms (80; the wing beat 3-6 twice, tools/art/import_smolder_strips.py FLAP), take-off frames 1-2
# (0-150 ms), the flight on the wing beats and frame 7 (150-1230 ms: the move from e_wind 8 for e_tick 64 ticks, the
# shots from e_shot0 9 every e_gap 12), landing frame 8 (1230-1330 ms); R 510 ms (31), the shout on
# frame 3 (170 ms: the effect on tick 2 + r_rel 8 = 10), the fire r_lag ticks later (League: 0.75 s cast + the flight).
# Projectile heights (5000 - y_offset over the pivot, 1000 units a px; his pivot is 13 px over the soles) are guesses at
# the mouth until the sheet is final.
# Numbers = candidate f2 of the 10-min classic-SDK simulations (Temp/sm_sim, sim/smkd.py --lane 3 against the base gunner,
# soldier, archer, gambler and whip master, three lineups, both sides, 2026-10-15): +1.98 on seeds 1-24, +1.41 on 25-48
# (league_zeri +1.70 / +1.49, league_twitch +1.60 / +1.96, league_draven +3.01 / +3.41, league_xayah +1.47 / +1.56 on the
# same seeds), damage dealt 12772 / 12519 (peers 11145-13789). The draft d1 (attack 96 +19 every 60, Q 40 + 100%, tiers
# 10 / 40 / 80, W on EnemyWithoutTower) was +0.24 on 1-24; W on EnemyChampion (d3) +0.56; then on seeds 1-12 from d3 (+0.47):
# Q 60 + 120% +0.90, tiers 10 / 25 / 40 +0.88, attack 100 +20 every 56 +0.44, R 150 + 100% +0.45; Q + tiers (f1) +1.01,
# f1 + the attack (f2) +1.75, f1 with Q 70 + 130% +1.46, f1 with Q every 270 +1.01. The tiers by the stacks per life:
# t1 in 99% of games (first at 2.3 min, median), t2 65% (4.8 min), t3 28% (7.3 min); summed over his lives (the add-on's
# count) the median game holds 25 stacks at 5:00 and 42 at 9:00.
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9, range 60000, cd 60); League's
    # Smolder: 575 +100 hp, 60 AD +2.3, 24 armour, 30 mr, 330 move, 550 range (55000 here, as league_twitch /
    # league_draven), attack speed 0.638
    "hp": 900, "hp_g": 90, "atk": 100, "atk_g": 20, "def": 22, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 26, "atk_cd": 56, "a_st": 8, "a_speed": 6000, "a_y": -1000,
    # passive Dragon Practice (League: a stack per champion hit by an ability and per Q kill; tiers 25 / 125 / 225 for a
    # 30-40 minute game; here a ~10-minute one): the counter's unit p_base (the tiers are multiples of it), the tiers, the
    # pending ladder's height (stacks gained between two attacks beyond it still add their ability power, not their count)
    "p_base": 5, "t1": 10, "t2": 25, "t3": 40, "p_pend": 6,
    # skill: Q Super Scorcher Breath (League: 550, 50-110 + 130% AD + 0.25 a stack, cd 5.5-3.5 s, missile 2200; tier 1
    # explosion r 285; tier 2 blowback 500 behind, 50%, r 150; tier 3 burn 3 s (1% true), execute 6.5%)
    "q_cd": 300, "q_range": 55000, "q_dur": 29, "q_st": 9, "q_speed": 7000, "q_y": -1000,
    "q_dmg": 60, "q_ratio": 120, "q_stack": 75,
    "q_t1_r": 22000,
    "q_t2_pct": 50, "q_t2_len": 45000, "q_t2_rad": 6000, "q_t2_win": 8, "q_t2_pic": 24,
    "q_burn_t": 180, "q_burn_p": 60, "q_burn_dmg": 10, "q_burn_ratio": 10, "q_burn_hp": 1,
    # skill2: W Achooo! (League: 1500, width 75, 50-110 + 60% AD (+0.55 a stack), explosion r 385 on champions,
    # slow 35% 1.5 s, cd 14-10 s)
    "w_cd": 600, "w_target": "EnemyChampion", "w_range": 80000, "w_anim": 28, "w_rel": 15, "w_speed": 8000,
    "w_len": 100000, "w_rad": 5000, "w_y": -1000, "w_dmg": 40, "w_ratio": 40, "w_slow": 35, "w_slow_t": 90,
    "w_x_r": 25000, "w_x_dmg": 40, "w_x_ratio": 40, "w_stack": 165,
    # E Flap, Flap, Flap (League: 1.25 s flight over walls, +75% move speed, 5 shots at the lowest-health enemy within
    # 700: 5-35 + 30% AD (+0.08 a stack) each, cd 24-16 s)
    "e_cd_t": 1200, "e_near": 40000, "e_close": 30000, "e_reach": 58000, "e_chase": 90000,
    # the flight (the user: 「小火龙好像不会飞？」 - 0.3 s in the air read as a hop): League's 1.25 s, e_tick 64 ticks
    # in the air after e_wind 8, e_speed x e_tick = 60000 away, the 5 shots spread over it
    "e_steps": [12000, 24000, 36000], "e_anim": 80, "e_wind": 8, "e_tick": 64, "e_speed": 940, "e_fspeed": 940,
    "e_ghost": 1, "e_ms": 40, "e_ms_t": 120, "e_n": 5, "e_gap": 12, "e_shot0": 9, "e_r": 70000, "e_sspeed": 7000,
    "e_y": -1000, "e_dmg": 10, "e_ratio": 30, "e_stack": 25,
    # ult: R MMOOOMMMM! (League: 4200, 50/150/250 + 100% bonus AD, the centre x1.5 and a 40% slow 2 s, heals him
    # 65-275 in the centre, mom 600 behind him, 0.75 s cast; cd 120-100 s)
    "r_cd": 3000, "r_target": "EnemyChampion", "r_range": 90000, "r_dur": 31, "r_rel": 8, "r_lag": 14, "r_apply": 16,
    "r_pic": 45, "r_len": 130000, "r_w": 12000, "r_cw": 0, "r_mom_speed": 6000, "r_mom_y": -10000,
    "r_dmg": 110, "r_ratio": 80, "r_sweet": 50, "r_slow": 40, "r_slow_t": 120, "r_heal": 80, "r_heal_ad": 30,
    # his spoken lines (Q, W, E), at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_smolder (its make_override.py): skill2 is the sneeze only, E is the add-on's passive
    # league_smolder:dragon (it also keeps the stacks through death), the tier-3 Q damage calls league_smolder:execute;
    # the passive's own numbers: the longest flight e_far (over a wall; e_plain without one) at e_fly a tick
    "native": 0, "e_far": 80000, "e_plain": 60000, "e_fly": 3000, "e_exec": 65,
    # test builds for the simulator's logs only: 1 = unbound ViewEffects (dbg_*) mark which branch ran
    "dbg": 0,
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


def flat(node):
    """The tree with every Combine that sits straight in a Combine's, a Delayed's or a RandomTarget's `effects`
    spliced into that list (the same effects in the same order, fewer nodes for the game's per-tick copy)."""
    if isinstance(node, list):
        return [flat(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {k: flat(v) for k, v in node.items()}
    if out.get("type") in ("Combine", "Delayed", "RandomTarget"):
        eff = []
        for x in out["effects"]:
            if isinstance(x, dict) and x.get("type") == "Combine":
                eff.extend(x["effects"])
            else:
                eff.append(x)
        out["effects"] = eff
    return out


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes or NONE, "effect_none": no or NONE}


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


def true_dmg(dmg, ratio, target_hp):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def heal_me(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": [e for e in effects if e is not None]}


def on_me(*effects):
    """Effects on him alone, also from a target's or a projectile's list (a `WithSelf` would also hit the target)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period,
            "effects": [e for e in effects if e is not None]}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": [e for e in effects if e is not None]}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects if e is not None]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects if e is not None], "end_effects": [e for e in end if e is not None],
            "speed": speed, "range": rng, "shape": circle(radius), "y_offset": y}


def band(name, width, length, delay, apply, target, effects):
    """A LineRangeProjectile: from the caster `length` along the cast; hits once on `apply` - 1, gone on `delay` - 1."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None]}


def drop(name, *end, target="EnemyWithoutTower"):
    """A hidden one-tick lob onto the unit in hand (league_annie R): its end_effects act on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": [e for e in end if e is not None]}


def zone(name, radius, target, effects):
    """A one-tick area on the lob's landing spot."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    dbg = (lambda name: view("dbg_" + name)) if p["dbg"] else (lambda name: None)
    b, n_pend = p["p_base"], p["p_pend"]
    levels = p["t3"] // b
    for k in ("t1", "t2", "t3"):
        if p[k] % b or p[k] <= 0:
            raise SystemExit(f"{k} = {p[k]} is not a positive multiple of p_base {b}")
    if not p["t1"] < p["t2"] < p["t3"]:
        raise SystemExit("the tiers must climb: t1 < t2 < t3")

    # ------------------------------------------------------------------ passive: Dragon Practice (the stacks)
    def gain():
        """One stack: the stat instance at once (+1 ability power), and one more step on the pending ladder."""
        up = flag("pa1", None)
        for k in range(2, n_pend + 1):
            up = sw(f"pa{k - 1}", flag(f"pa{k}", None), up)
        if n_pend >= 2:
            up = sw(f"pa{n_pend}", NONE, up)
        return combine(flag("p_st", None, magic_power=1), sw("p_has", NONE, flag("p_has", None)), up, dbg("p_gain"))

    def tier_up(k):
        """The level k * p_base reached: a tier flag, its picture, sound and line when it is one of the tiers."""
        for i, t in enumerate(("t1", "t2", "t3"), 1):
            if k * b == p[t]:
                return combine(flag(t, None), cview("p_up"), sfx(f"p_t{i}"), sfx("vo_up"), dbg(f"p_{t}"))
        return None

    def step():
        """Count one stack: units u1..u<b-1> (all on at k), the b-th clears them and climbs the levels L1..L<levels>."""
        lvl = combine(flag("L1", None), tier_up(1))
        for k in range(2, levels + 1):
            lvl = sw(f"L{k - 1}", combine(flag(f"L{k}", None), tier_up(k)), lvl)
        lvl = sw(f"L{levels}", NONE, lvl)
        if b == 1:
            return lvl
        units = flag("u1", None)
        for k in range(2, b):
            units = sw(f"u{k - 1}", flag(f"u{k}", None), units)
        return sw(f"u{b - 1}", combine(*rm(*[f"u{k}" for k in range(1, b)]), lvl), units)

    # his attack works the pending stacks off: with one pending, an AddCasted on him runs once a tick for p_pend ticks,
    # each run taking the top rung off and counting one (the counter written once; a second attack's runs only help)
    take = rm(f"pa{n_pend}")[0]
    for k in range(n_pend - 1, 0, -1):
        take = sw(f"pa{k + 1}", take, rm(f"pa{k}")[0])
    work = sw("pa1", on_me(casted(n_pend, 1, sw("pa1", combine(take, step())))))

    # ------------------------------------------------------------------ attack
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy", flat(combine(
        sfx("a_cast"), homing("a_bolt", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
        work)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Super Scorcher Breath
    burn = casted(p["q_burn_t"], p["q_burn_p"], true_dmg(p["q_burn_dmg"], p["q_burn_ratio"], p["q_burn_hp"]),
                  view("q_burn"), kind="Fire")

    # the add-on's execute below e_exec / 10 % health (the tier-3 hit; native code reads health)
    execute = {"type": "Native", "effect_ref": f"{ID}:execute"} if p["native"] else None

    def q_hit(pct=100, pic="q_hit"):
        """The Q damage on one unit (pct% of it), the stacks' part, the tier-3 burn."""
        return combine(attack(p["q_dmg"] * pct // 100, p["q_ratio"] * pct // 100),
                       sw("p_has", magic(0, p["q_stack"] * pct // 100)), view(pic), tsfx(pic),
                       sw("t3", combine(burn, tsfx("q_burn"), execute)) if pct == 100 else None)

    # tier 1+: the explosion round the target's spot (the target included), a tick after the bolt's hit; its champion
    # zone gives the stacks; tier 2 lays the blowback's picture from the same spot, away from him
    blow_pic = band("q_t2", 1000, p["q_t2_len"], p["q_t2_pic"], p["q_t2_pic"] + 1, "Ally", [])
    boom = delayed(1, drop("q_drop", view("q_t1"), sfx("q_boom"),
                           zone("q_boom", p["q_t1_r"], "EnemyWithoutTower", [q_hit()]),
                           zone("q_boomc", p["q_t1_r"], "EnemyChampion", [gain()]),
                           sw("t2", combine(blow_pic, sfx("q_back")))))
    # the kill check on the bolt's target (league_jinx R's timing: the damage lands by tick 1, the casted on a living
    # target clears the flag on tick 4, the read on tick 9)
    kill = combine(refresh("k_q", 12), delayed(4, casted(3, 1, *rm("k_q"), kind="Bleed")),
                   on_me(delayed(9, sw("k_q", combine(*rm("k_q"), gain(), dbg("q_kill"))))))
    bolt = homing("q_bolt", p["q_speed"], p["q_y"], "EnemyWithoutTower", [
        sw("t1", boom, q_hit()), sw("t2", combine(refresh("q_bw", p["q_t2_win"]), refresh("q_bwait", 1))), kill])
    twin = homing("q_twin", p["q_speed"], p["q_y"], "EnemyChampion", [sw("t1", NONE, gain())])
    # tier 2: the blowback, a hidden line flown with the bolt and on q_t2_len past the target; it hits only inside the
    # window the bolt's hit opens, its first tick skipped (the target)
    back = line("q_back", p["q_speed"], p["q_range"] + p["q_t2_len"] + 15000, p["q_t2_rad"], p["q_y"], "EnemyWithoutTower",
                True, [sw("q_bw", sw("q_bwait", NONE, combine(q_hit(p["q_t2_pct"], "q_t2_hit"), dbg("q_back"))))])
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Targeting", "EnemyWithoutTower", flat(combine(
        sfx("q_cast"), voice("vo_q", p), *rm("q_bw", "q_bwait"), twin, bolt, sw("t2", back))))

    # ------------------------------------------------------------------ skill2: W Achooo! / E Flap, Flap, Flap
    explosion = delayed(1, drop("w_drop", view("w_boom"), sfx("w_boom"), zone("w_x", p["w_x_r"], "EnemyWithoutTower", [
        attack(p["w_x_dmg"], p["w_x_ratio"]), sw("p_has", magic(0, p["w_stack"])), view("w_xhit")]),
        zone("w_xc", p["w_x_r"], "EnemyChampion", [gain()])))
    sneeze = combine(sfx("w_cast"), line("w_bolt", p["w_speed"], p["w_len"], p["w_rad"], p["w_y"], "EnemyWithoutTower", True,
                                         [attack(p["w_dmg"], p["w_ratio"]),
                                          buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
                                          view("w_hit"), tsfx("w_hit")]),
                     line("w_seek", p["w_speed"], p["w_len"], p["w_rad"], p["w_y"], "EnemyChampion", False, [explosion]))
    w_cast = combine(anim("skill2", p["w_anim"]), voice("vo_w", p), delayed(p["w_rel"], sneeze), dbg("w"))

    def shot_c():
        return homing("e_shot", p["e_sspeed"], p["e_y"], "EnemyChampion", [
            attack(p["e_dmg"], p["e_ratio"]), sw("p_has", magic(0, p["e_stack"])), view("e_hit"), tsfx("e_hit"),
            sw("e_got", NONE, combine(flag("e_got", p["e_anim"] + 20), gain()))])
    shot_m = homing("e_shotm", p["e_sspeed"], p["e_y"], "EnemyWithoutTower", [
        attack(p["e_dmg"], p["e_ratio"]), sw("p_has", magic(0, p["e_stack"])), view("e_hit"), tsfx("e_hit")])
    # one shot: a wounded enemy champion (his team hit it lately) first, else any enemy champion, else any enemy
    shot = combine(*rm("e_aim"),
                   pick(p["e_r"], "EnemyChampionRecentlyAttacked", flag("e_aim", 1), sfx("e_shot"), shot_c()),
                   sw("e_aim", NONE, pick(p["e_r"], "EnemyChampion", flag("e_aim", 1), sfx("e_shot"), shot_c())),
                   sw("e_aim", NONE, pick(p["e_r"], "EnemyWithoutTower", sfx("e_shot"), shot_m)))
    shots = delayed(p["e_shot0"], on_me(casted(p["e_gap"] * (p["e_n"] - 1) + 1, p["e_gap"], shot)))
    t = p["e_tick"]
    # away from the nearest enemy champion: the first ring of e_steps with one in it (league_bard E)
    away = combine(*rm("e_mv"), *[sw("e_mv", NONE, pick(r, "EnemyChampion", flag("e_mv", 1), delayed(
        p["e_wind"], {"type": "MoveBack", "speed": p["e_speed"], "tick": t}), dbg("e_away"))) for r in p["e_steps"]])
    # toward the wounded enemy champion out of his reach
    toward = pick(p["e_chase"], "EnemyChampionRecentlyAttacked", delayed(p["e_wind"], {
        "type": "RushTime", "speed": p["e_fspeed"], "tick": t, "range": 20000, "casting_target": "EnemyWithoutTower",
        "penetrate": True, "applied_effects": []}), dbg("e_toward"))
    ghost = flag("e_ghost", p["e_wind"] + t + 12, ignore_wall=True) if p["e_ghost"] else None
    e_cast = combine(flag("e_cd", p["e_cd_t"]), *rm("e_got"), anim("skill2_e", p["e_anim"]), sfx("e_cast"),
                     voice("vo_e", p), ghost, flag("e_haste", p["e_ms_t"], move_speed_mult=p["e_ms"]),
                     sw("e_fwd", toward, away), shots)
    # E now? dived (two enemy champions within e_near or one within e_close), else chasing (no enemy champion within
    # e_reach, a wounded one within e_chase); one-tick flags pick the branch first, so each cast is written once (the game
    # copies skill2 every tick)
    decide = combine(*rm("e_go", "e_fwd", "e_n1", "e_n2", "e_in"), sw("e_cd", NONE, combine(
        around(p["e_near"], "EnemyChampion", [sw("e_n1", flag("e_n2", 1), flag("e_n1", 1))]),
        pick(p["e_close"], "EnemyChampion", flag("e_n2", 1)),
        sw("e_n2", flag("e_go", 1), combine(
            pick(p["e_reach"], "EnemyChampion", flag("e_in", 1)),
            sw("e_in", NONE, pick(p["e_chase"], "EnemyChampionRecentlyAttacked", flag("e_go", 1), flag("e_fwd", 1))))))))
    # the add-on's copy: E is all the passive's (when, where - over walls - and the shots), skill2 the sneeze alone
    skill2 = action("idle", 3, p["w_cd"], 1, p["w_range"], "Targeting", p["w_target"],
                    flat(w_cast if p["native"] else combine(decide, sw("e_go", e_cast, w_cast))), key="skill2")

    # ------------------------------------------------------------------ ult: R MMOOOMMMM!
    sweet = p["r_sweet"]
    fire = combine(
        band("r_fire", p["r_w"], p["r_len"], p["r_pic"], p["r_apply"], "EnemyWithoutTower",
             [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]),
        band("r_core", p["r_cw"], p["r_len"], p["r_apply"], p["r_apply"], "EnemyWithoutTower",
             [attack(p["r_dmg"] * sweet // 100, p["r_ratio"] * sweet // 100),
              buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"])]),
        band("r_self", p["r_cw"], p["r_len"], p["r_apply"], p["r_apply"], "AllyOnlySelf",
             [heal_me(p["r_heal"], p["r_heal_ad"]), view("r_heal"), sfx("r_heal"), dbg("r_heal")]))
    mom = line("r_mom", p["r_mom_speed"], p["r_len"], 1000, p["r_mom_y"], "Ally", True, [])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Direction", p["r_target"], flat(combine(
        delayed(p["r_rel"], sfx("r_cast"), sfx("vo_r"), sfx("r_mom"), mom), delayed(p["r_rel"] + p["r_lag"], fire))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                             "tag": tag or name, "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1, tag=None, rep=True: {"type": "Animated", "name": n(name), "anim": anim_,
                                                           "tag": tag or name, "repeat": rep, "z": z}
    # the bands' pictures turn with the cast: the fire (r_fire) and the blowback's three fireballs (q_t2) are drawn
    # symmetric top to bottom, pointing right; mom's shadow (r_mom) is seen from above, symmetric about her flight
    views_p = [P_("a_bolt"), P_("q_bolt"), P_("q_t2", BIG, 2, rep=False), P_("w_bolt"), P_("e_shot"),
               P_("e_shotm", tag="e_shot"), P_("r_fire", BIG, -1, rep=False), P_("r_mom", BIG, 3, rep=False)]
    views_e = [E("a_hit"), E("q_hit"), E("q_t1", BIG, 2, False), E("q_t2_hit"), E("q_burn"), E("w_hit"),
               E("w_boom", BIG, 2, False), E("w_xhit", tag="w_hit"), E("e_hit"), E("r_hit"), E("r_heal"),
               E("p_up", FX, 3)]
    views_b = [P_("w_slow", tag="slow"), P_("r_slow", tag="slow"), P_("e_haste", z=-1)]
    extra = {}
    if p["native"]:
        keys = ("e_cd_t", "e_anim", "e_wind", "e_tick", "e_far", "e_plain", "e_fly", "e_near", "e_close", "e_reach",
                "e_chase", "e_ms", "e_ms_t", "e_n", "e_gap", "e_shot0", "e_r", "e_sspeed", "e_dmg", "e_ratio", "e_stack",
                "e_exec", "p_base", "p_pend", "t3", "vo_gap")
        extra["passive"] = {"passive_ref": f"{ID}:dragon", "params": {k: p[k] for k in keys}}
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "Dot"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b, **extra,
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
        if isinstance(p[k], str):
            p[k] = v
        elif isinstance(p[k], list):
            p[k] = [int(x) for x in v.split(",")]
        else:
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
