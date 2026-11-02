"""Build league_aurelionsol.data_champion (mid, Magician: Aurelion Sol, the Star Forger) from the parameters P.

    python tools/kit/build_aurelionsol.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-24: MID, layout A - Q / E / R, Astral Flight (W) folded into the passive; combos the
black hole -> the breath at once, the falling star's stun -> the black hole on the spot, stardust full -> The Skies
Descend, a takedown -> flight with the breath unbound; 「有连招要做连招」).
TFM2 has three active slots for League's four buttons: Breath of Light (Q) is `skill`, Singularity (E) `skill2`, Falling
Star / The Skies Descend (R) the `ult`. Q and E keep their cooldowns in flags (`q_cd`, `e_cd`; league_belveth's way) so
the combos can cast them; a slot cast while its flag is up does nothing (a 3-tick idle). Flags die with him.
  passive Cosmic Creator (星海焕然): his spells gather stardust - a champion in the breath (once every d_lk ticks), a
          champion caught in the black hole (the same), every champion the falling star hits. Each stardust is a
          Permanent stack (d1 .. d_max; the first d_ap_n d_ap% ability power each, so every spell grows); in the main
          pack the stacks end with his death (the add-on puts them back: League's stardust is permanent). Every sky_n
          stardust charge The Skies Descend (the flag `sky`, kept until the next R). Every grow_n stardust is a size
          step (League: stardust widens Falling Star, The Skies Descend and Singularity; the user 2026-10-31:
          「龙王的大招后期感觉没有英雄联盟那种感觉啊」「应该后期大招会很大吧」 - the cap went from 15 to 30, the 15 past
          the first size alone): the star, the Skies, the shockwave and the black hole's picture and pull grow to grow_x%
          at d_max (`sized`: the deepest d<step * grow_n> on him picks the step; each step's own pictures,
          tools/art/import_aurelionsol_fx.py).
          Astral Flight (星穹流丽, W), folded in: a takedown of an enemy champion he damaged (within p_win ticks of his
          last hit on it, by anyone's hand: league_viego's window, league_belveth's watch) lifts him into flight for
          w_t ticks: w_ms% move speed over walls, w_ap% ability power, and the breath's cooldown is q_cd_f (no cooldown
          but its own channel) with a channel of q_t_f (no maximum); then w_cd ticks before the next flight. A takedown
          while w_cd runs cuts it to w_cut (League: the cooldown refund).
  attack  A star bolt (homing on `Enemy`, 100% AD) released on a_rel; a champion-only twin keeps the takedown watch.
  skill   Breath of Light (星河冲荡, `q_cd`): a `Targeting` cast on `EnemyWithoutTower` (q_range). He channels q_t ticks
          (q_t_f in flight; crowd control breaks it): every q_p ticks the breath (a fast line through everything toward
          the target, q_rad wide: the first hit and the splash behind it; q_speed slow enough that the segments
          overlap into one stream, at his mouth's height q_y) deals q_dmg + q_ratio% AP, after q_sec ticks
          of channel q_sec_dmg more (League: the bonus for each second on one enemy).
  skill2  Singularity (星芒凝汇, `e_cd`): a `Targeting` cast on `EnemyWithoutTower` (e_range): the black hole lands on the
          target's spot for e_t ticks (e_r wide): every e_p ticks e_dmg + e_ratio% AP, a short pull toward its centre
          (a `Pull` in a zone heads for the zone) and e_slow% slower; its core (e_core) every e_cp ticks takes e_exec% of
          a champion's maximum health (true damage: the main pack's stand-in for League's execute, which needs the
          champion's health - the add-on's league_aurelionsol:singularity executes below e_low% (+ e_low_d per stardust
          tier) in the core instead).
  ult     Falling Star (星落): a `Targeting` cast on `EnemyChampion` (r_range): r_fall ticks later the star crashes on the
          target's spot: r_r wide, r_dmg + r_ratio% AP, stunned r_stun ticks.
          The Skies Descend (天瀑), with `sky` up: r_r2 wide, r_dmg2 + r_ratio2% AP, knocked up r_up ticks; r_wave_at
          ticks later the shockwave from its edge (r_wave wide): r_wdmg + r_wratio% AP and r_wslow% slower for r_wslow_t.
  combos  E -> Q: the black hole's first champion caught has the controller breathe at it at once (if `q_cd` is off);
          while a black hole lasts (`e_on`) he has e_ap% ability power (the pulled ones take more).
          R -> E: the star's impact drops the black hole on the same spot at once if `e_cd` is off (stunned, then pulled);
          only for Aurelion Sol himself (`own`: league_sylas's stolen ult brings the star alone).
          Stardust full -> The Skies Descend (sky_n stardust, above).
          Takedown -> flight with the breath unbound (above).
  controller An AddCasted pulse on him every ctl_p ticks (league_belveth's, hung by his attack and the ult, only for
          Aurelion Sol himself: `own`): the takedown watch, the stardust counting (`g_q`, `g_e`, `g_r1..3` raised by the
          hits), E -> Q.
The add-on copy (--native, addons/league_aurelionsol): the passive league_aurelionsol:stardust keeps the stardust stacks
through death and executes in the black hole's core by real health.
Action tags (the art): idle run attack hit dead skill skill2 ult.
Numbers: League 16.21 read into the Magician mid range (league_aurora, league_hwei); timings are drafts until the frames
exist. Balanced on the classic-SDK simulations (kd.py --lane 2 against the five base mid mages, C:/t/as_sim, 2026-10-24;
league_aurora +0.93 / +1.01 on seeds 1-8 / 9-16): the draft (Q 14 + 9% a pulse, E 8 + 5%, R 200 + 65%) -3.01; Q 22 + 15%,
E 14 + 8%, R 260 + 80%, 1000 health, 24 defence +0.35; Q 30 + 20%, E 18 + 10%, R 280 + 90% +1.74; between them (Q 26 + 17%
every 300 ticks, the held bonus 30, E 16 + 9% every 630, the core 4%, R 270 + 85% / Skies 350 + 105% every 2100)
+0.40 / +1.41; the breath slowed to 2500 a tick at his mouth's height (one stream on screen, its hits a little later) = P
+0.54 / +1.02. Traced (seeds 1-3): every combo fires - E -> Q 2-16 a game, R -> E 1-5, The Skies Descend 1-4, flights
1-3.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_aurelionsol.data_champion")
ID = "league_aurelionsol"
FX = "asset/league/effects/league_aurelionsol_fx"
BIG = "asset/league/effects/league_aurelionsol_big"

# League's Aurelion Sol (16.21): 620 +110 hp, 58 AD, 22 armour, 30 mr, 335 move, 550 range. Q: 750 range channel,
# 10-35 per 0.25 s + bonus per second on one target (+ stardust), cd 3 (none in flight). W: 1500 flight, cd 22-14,
# takedown refund. E: 750 range black hole 5 s, damage + pull, executes 5% (+ stardust) max health in the centre,
# cd 12. R: 1250 range, 150-350 + 65% AP, stun 1.25 s; The Skies Descend 187-437 + 81% AP, knock-up 1 s, shockwave
# 50% slow; cd 120-100.
P = {
    # stats (Magician mid: league_aurora 960 +90 hp, 68 +6 attack, 40 +20 ap, 21 +6 def)
    "hp": 1000, "hp_g": 92, "atk": 66, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 24, "def_g": 6, "mr": 26, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 90, "a_rel": 10, "a_speed": 4500, "a_y": -5000,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: stardust; Astral Flight folded in
    "d_max": 30, "d_ap": 3, "d_ap_n": 15, "d_lk": 60, "g_t": 30, "sky_n": 6, "p_win": 180,
    # stardust grows the star, the Skies, the shockwave and the black hole: a size step every grow_n, grow_x% at d_max
    "grow_n": 5, "grow_x": 200,
    "w_t": 240, "w_ms": 60, "w_ap": 20, "w_cd": 1200, "w_cut": 300,
    # skill: Breath of Light
    "q_cd": 300, "q_cd_f": 150, "q_range": 75000, "q_t": 90, "q_t_f": 150, "q_p": 10, "q_rel": 8,
    "q_len": 78000, "q_rad": 6000, "q_speed": 2500, "q_y": -13000, "q_dmg": 26, "q_ratio": 17, "q_sec": 60, "q_sec_dmg": 30,
    # skill2: Singularity
    "e_cd": 630, "e_range": 75000, "e_dur": 30, "e_rel": 12, "e_fly": 18, "e_r": 26000, "e_t": 300, "e_p": 15,
    "e_dmg": 16, "e_ratio": 9, "e_pull": 250, "e_pull_t": 4, "e_slow": 25, "e_core": 9000, "e_cp": 60, "e_exec": 4,
    "e_ap": 15, "e_low": 5, "e_low_d": 1, "e_low_n": 15,
    # ult: Falling Star / The Skies Descend
    "r_cd": 2100, "r_range": 125000, "r_dur": 36, "r_rel": 14, "r_fall": 30, "r_r": 22000, "r_dmg": 270,
    "r_ratio": 85, "r_stun": 60, "r_r2": 30000, "r_dmg2": 350, "r_ratio2": 105, "r_up": 50, "r_wave_at": 12,
    "r_wave": 45000, "r_wdmg": 80, "r_wratio": 30, "r_wslow": 50, "r_wslow_t": 90,
    # his spoken lines, at most one every vo_gap ticks
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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return {"type": "RangeEffect", "shape": circle(1000), "target": "AllyOnlySelf", "apply_type": "AroundCaster",
            "effects": list(effects)}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=ap):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, y=0):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A lob onto the target's spot (league_annie R's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def blast(name, radius, effects, target="EnemyWithoutTower"):
    """One hit on everything within radius of a lob's landing spot (a zone that strikes once, on its first tick)."""
    return field(name, radius, 2, 30, effects, target, first=0)


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def tiers(p):
    """The size steps stardust climbs: one every grow_n, the last at d_max."""
    return p["d_max"] // p["grow_n"]


def grown(p, t):
    """Step t's size (1 for none, grow_x% at the last)."""
    return 1 + (p["grow_x"] / 100 - 1) * t / tiers(p)


def tier_tag(name, t):
    """A picture's tag at size step t (tools/art/import_aurelionsol_fx.py draws each step's own, bigger)."""
    return name if t == 0 else f"{name}_{t}"


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    ctl_p = p["ctl_p"]

    # ------------------------------------------------------------------ passive: Cosmic Creator
    def track():
        """On an enemy champion he hit: keeps p_alive up while it lives (its own pulse, league_viego's window); his
        controller watches for it lapsing while `p_win_on` lasts (2 ticks shorter, so a window running out is never
        read as a death)."""
        return combine(casted(p["p_win"], 1, refresh("p_alive", 2)),
                       on_me(refresh("p_alive", 3), refresh("p_win_on", p["p_win"] - 2)))

    def d_flag(i):
        """Stardust stack i: d_ap% ability power for the first d_ap_n, size alone after them."""
        return flag(f"d{i}", None, **({"magic_power_mult": p["d_ap"]} if i <= p["d_ap_n"] else {}))

    def dust():
        """One more stardust: a Permanent stack (d_max at most) and one step of the Skies' charge (sky_n -> `sky`)."""
        stack = d_flag(1)
        for i in range(2, p["d_max"] + 1):
            stack = sw(f"d{i - 1}", d_flag(i), stack)
        stack = sw(f"d{p['d_max']}", NONE, stack)
        # the charge c1 .. c(sky_n - 1) fills in order (the deepest one present decides); the next one charges `sky`
        last = p["sky_n"] - 1
        full = combine(*rm(*[f"c{i}" for i in range(1, last + 1)]), flag("sky", None), cview("sky_ready"), sfx("sky"))
        ladder = flag("c1", None)
        for i in range(1, last + 1):
            ladder = sw(f"c{i}", flag(f"c{i + 1}", None) if i < last else full, ladder)
        return combine(stack, sw("sky", NONE, ladder), cview("d_gain"))

    def gain(g, lock):
        """A hit that gathers stardust: g raised for the controller, once every d_lk ticks per source."""
        return sw(lock, NONE, combine(flag(lock, p["d_lk"]), refresh(g, p["g_t"]), track()))

    # Astral Flight: a takedown lifts him (or cuts the flight's cooldown)
    fly = combine(flag("w_cd", p["w_cd"]), refresh("w_fly", p["w_t"], move_speed_mult=p["w_ms"],
                                                    magic_power_mult=p["w_ap"], ignore_wall=True),
                  cview("w_lift"), sfx("w"), voice("vo_w", p))
    takedown = combine(*rm("p_win_on"), refresh("p_lock", 6), sw("w_cd", refresh("w_cd", p["w_cut"]), fly))
    watch = sw("p_win_on", sw("p_alive", NONE, sw("p_lock", NONE, takedown)))

    # ------------------------------------------------------------------ Q Breath of Light
    cc_break = pick(1, "AllyChampionInCC", *rm("q_ch"))
    def q_cast():
        """The channel: an AddCasted on the target (league_caitlyn R's: projectiles from him to it every q_p ticks while
        `q_ch` holds), and from q_sec on a second one with the bonus for staying on it."""
        breath = line("q_beam", p["q_speed"], p["q_len"], p["q_rad"], "EnemyWithoutTower",
                      [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")], p["q_y"])
        twin = line("q_twin", p["q_speed"], p["q_len"], p["q_rad"], "EnemyChampion", [gain("g_q", "q_lk")], p["q_y"])
        held = homing("q_held", "EnemyWithoutTower", [ap(p["q_sec_dmg"], 0)])
        cd = sw("w_fly", combine(refresh("q_cd", p["q_cd_f"]), refresh("q_ch", p["q_t_f"])),
                combine(refresh("q_cd", p["q_cd"]), refresh("q_ch", p["q_t"])))
        return combine(cd, anim("skill", p["q_t"]), sfx("q"), voice("vo_q", p),
                       delayed(p["q_rel"] - 1, casted(p["q_t_f"], p["q_p"], alive(cc_break, sw("q_ch", combine(breath, twin))))),
                       delayed(p["q_rel"] - 1 + p["q_sec"], casted(p["q_t_f"] - p["q_sec"], p["q_p"],
                                                                   alive(sw("q_ch", held)))))

    def sized(make):
        """make(t) for the size step his stardust has reached (stack d<t * grow_n> on him; the deepest one decides)."""
        out = make(0)
        for t in range(1, tiers(p) + 1):
            out = sw(f"d{t * p['grow_n']}", make(t), out)
        return out

    # ------------------------------------------------------------------ E Singularity
    def hole():
        """The black hole where this runs (a lob's landing spot): pull, damage, the core, E -> Q. Its picture and its pull
        grow with his stardust (sized); the champions caught for stardust and E -> Q, and the core, keep e_r and e_core -
        the pull brings the outer ones in, and skill2's tree, which the game copies every tick, stays small."""
        hit = [ap(p["e_dmg"], p["e_ratio"]), {"type": "Pull", "speed": p["e_pull"], "tick": p["e_pull_t"]},
               buff("e_slow", p["e_p"] + 5, move_speed_mult=-p["e_slow"])]
        caught = [gain("g_e", "e_lk"), sw("eq_lk", NONE, combine(flag("eq_lk", p["e_t"]), refresh("q_go", ctl_p * 3)))]
        core = [pct(p["e_exec"]), view("e_core"), tsfx("e_core")] + ([native("core")] if p["native"] else [])
        return combine(sized(lambda t: combine(view(tier_tag("e_hole", t)),
                                               field("e_field", round(p["e_r"] * grown(p, t)), p["e_t"], p["e_p"], hit))),
                       sfx("e_hole"), on_me(refresh("e_on", p["e_t"], magic_power_mult=p["e_ap"])),
                       field("e_catch", p["e_r"], p["e_t"], p["e_p"], caught, "EnemyChampion"),
                       field("e_eye", p["e_core"], p["e_t"], p["e_cp"], core, "EnemyChampion"))

    def e_cast():
        return combine(refresh("e_cd", p["e_cd"]), *rm("eq_lk"), anim("skill2", p["e_dur"]), sfx("e"),
                       voice("vo_e", p), delayed(p["e_rel"] - 1, alive(lob("e_orb", p["e_fly"], [hole()]))))

    # ------------------------------------------------------------------ R Falling Star / The Skies Descend
    def r_gain():
        """Every champion the star hits: one stardust (g_r1 .. g_r3 for the controller)."""
        return combine(sw("g_r2", flag("g_r3", p["g_t"]), sw("g_r1", flag("g_r2", p["g_t"]), flag("g_r1", p["g_t"]))),
                       track())

    def star(t):
        k = grown(p, t)
        return combine(view(tier_tag("r_impact", t)), sfx("r_land"),
                       blast("r_blast", round(p["r_r"] * k), [ap(p["r_dmg"], p["r_ratio"]),
                                                              {"type": "Stun", "duration": p["r_stun"]},
                                                              view("r_hit"), tsfx("r_hit")]),
                       blast("r_tw", round(p["r_r"] * k), [r_gain()], "EnemyChampion"))

    wave_hit = [ap(p["r_wdmg"], p["r_wratio"]), buff("r_slow", p["r_wslow_t"], move_speed_mult=-p["r_wslow"]),
                view("r_hit")]

    def skies(t):
        k = grown(p, t)
        return combine(*rm("sky"), view(tier_tag("r_sky", t)), sfx("r_sky"),
                       blast("r_blast2", round(p["r_r2"] * k), [ap(p["r_dmg2"], p["r_ratio2"]),
                                                                {"type": "Airborne", "duration": p["r_up"]},
                                                                view("r_hit"), tsfx("r_hit")]),
                       blast("r_tw2", round(p["r_r2"] * k), [r_gain()], "EnemyChampion"),
                       delayed(p["r_wave_at"], view(tier_tag("r_wave", t)), sfx("r_wave"),
                               blast("r_shock", round(p["r_wave"] * k), wave_hit)))
    # R -> E: the black hole on the impact's spot at once, if Singularity is ready - only for Aurelion Sol himself (`own`,
    # raised by his attack: league_sylas's stolen ult brings the star alone)
    then_e = sw("own", sw("e_cd", NONE, combine(refresh("e_cd", p["e_cd"]), *rm("eq_lk"), sfx("e"), hole())))
    landing = [sw("sky", sized(skies), sized(star)), then_e]
    r_cast = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                     delayed(p["r_rel"] - 1, alive(cview("r_call"), view("r_fall"),
                                                   lob("r_star", p["r_fall"], landing, "EnemyChampion"))))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not (league_zac):
    # his attacks and the ult hang one unless `polling` says one runs; only for Aurelion Sol himself (`own`, a flag his
    # attack raises: league_sylas's stolen ult hangs it too, league_singed)
    # one stardust a pulse: the first gain raised (the star's g_r3 .. g_r1, the breath's, the black hole's), its flag
    # taken; the rest wait for the next pulses (each lasts g_t ticks)
    first = NONE
    for g in ("g_e", "g_q", "g_r1", "g_r2", "g_r3"):
        first = sw(g, combine(*rm(g), flag("dg", 1)), first)
    count = combine(first, sw("dg", combine(*rm("dg"), dust())))
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        watch, count,
        sw("q_go", combine(*rm("q_go"), sw("q_cd", NONE, pick(p["q_range"], "EnemyChampion", q_cast())))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ attack
    bolt = combine(sfx("a"), homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"],
                                    p["a_y"]),
                   homing("a_tw", "EnemyChampion", [track()], p["a_speed"], p["a_y"]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100, attack), sw("own", NONE, flag("own", None)), hang,
                              delayed(p["a_rel"] - 1, alive(bolt))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"]), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"] * 6, p["q_ratio"] * 6), sw("q_cd", NONE, q_cast())), key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"] * 10, p["e_ratio"] * 10), sw("e_cd", NONE, e_cast())), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("a_bolt"), Pj("q_beam"), Pj("e_orb")]   # r_star flies unseen: r_fall draws the star coming down
    views_e = [E("a_hit"), E("q_hit"), E("e_hole", BIG, -1, False), E("e_core"), E("r_call", FX, 3, False), E("r_fall", BIG, 3, False),
               E("r_impact", BIG, -1, False), E("r_sky", BIG, -1, False), E("r_wave", BIG, -1, False), E("r_hit"),
               E("w_lift", FX, 3, False), E("d_gain"), E("sky_ready")]
    views_e += [E(tier_tag(x, t), BIG, -1, False) for t in range(1, tiers(p) + 1)
                for x in ("e_hole", "r_impact", "r_sky", "r_wave")]
    views_b = [B_("e_slow", FX, -1, "slow"), B_("r_slow", FX, -1, "slow"), B_("w_fly", FX, -1, "w_trail"),
               B_("sky", FX, 3, "sky_glow")]
    extra = {}
    if p["native"]:   # addons/league_aurelionsol: stardust kept through death, the core's real execute
        extra["passive"] = {"passive_ref": f"{ID}:stardust",
                            "params": {k: p[k] for k in ("d_max", "e_low", "e_low_d", "e_low_n")}}
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
