"""Build league_ambessa.data_champion (top, Melee fighter, AD: Ambessa, the Matriarch of War) from the parameters P.

    python tools/kit/build_ambessa.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (2026-10-25, the plan's group J: TOP; 「有连招要做连招」). The draft takes the defaults of the last heroes (layout A
- Q / E / R, the fourth button folded in): the user may still pick otherwise.
TFM2 has three active slots for League's four buttons: Cunning Sweep / Sundering Slam (Q) is `skill`, Lacerate (E)
`skill2`, Public Execution (R) the `ult`; Repudiation (W) is cast by the controller. Q, E and W keep their cooldowns
in flags (`q_cd`, `e_cd`, `w_cd`; league_sejuani's) so the combos can cast them; a slot cast while its flag is up does
nothing (a 3-tick idle). Flags die with her: a respawned Ambessa has every button ready.
  passive Drakehound's Step (龙犬之步): every ability ends in a short dash at its target (st_gap ticks after the cast,
          `MoveToTarget` st_speed, at most st_reach; the `step` tag) and readies `pw` (pw_t ticks): her attacks are
          pw_as% faster meanwhile and the next one hits for pw_dmg + pw_ratio% AD + pw_pct% of the target's maximum
          health more (League: +range, +attack speed, bonus damage and energy; the data has no energy).
  attack  Twin blades (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit.
  skill   Q Cunning Sweep (狡诈横扫), `Targeting` on `EnemyWithoutTower` (q_range, `q_cd`): on q_hit a half circle in
          front of her (`Forward` + `DirDot` range 0, q_r): q_dmg + q_ratio% AD + q_pct% of maximum health (League's
          bonus at the blade's edge, on everyone here). Anything hit readies Sundering Slam (`q2_go`, q2_win ticks,
          after q2_gap): the slot - or the controller, at once - casts it instead.
          Sundering Slam (裂地重击, the `slam` tag): a line from her through the target (q2_len long, half-width
          q2_w): q2_dmg + q2_ratio% AD; the target itself (League: the first enemy hit) q2_pct% of its maximum
          health more.
  skill2  E Lacerate (割裂), `Targeting` on `EnemyWithoutTower` (e_range, `e_cd`): on e_hit the chains lash round her
          (e_r): e_dmg + e_ratio% AD, e_slow% slower for e_slow_t; the step's dash ends in a second lash (League:
          the Drakehound's Step after Lacerate repeats it).
  W       Repudiation (拒斥), by the controller when an enemy champion is within w_trig and she is not in a cast
          (`busy`), `w_cd`: a shield (w_sh + w_ad% AD, w_t ticks) as she braces behind her blades, w_brace ticks
          later a slam round her (w_r): w_dmg + w_ratio% AD, champions w_pct% of their maximum health more (League:
          more when she was struck while braced - the data cannot read a hit on her, a champion close by stands in).
  ult     R Public Execution (公开处决), `Targeting` on `EnemyChampion` within r_range: on r_go she blinks onto the
          champion (`Teleport`) and pins it (`Stun` r_sup, League's suppression), r_slam ticks later slams it down:
          r_dmg + r_ratio% AD + r_pct% of its maximum health and `Stun` r_stun. The cast also gives her r_pen%
          defence penetration for good (League's passive on R: armour penetration; the flag dies with her and comes
          back with her next R).
  combos  Q sweep -> Sundering Slam (League's recast): the controller slams the nearest unit (q2_range) q2_gap ticks
          after a sweep that hit. Every ability -> the step -> the empowered attack (the passive). E -> the step ->
          a second lash at the dash's end. R's slam -> Q at once (`q_cd` off, the controller sweeps the champion:
          R -> Q -> Q2, League's all-in) and Repudiation ready (`w_cd` off).
  controller An AddCasted pulse on her every ctl_p ticks (league_sejuani's, hung by her attack and the ult, only for
          Ambessa herself: `own`): Sundering Slam, R's Q, Repudiation.
The add-on copy (--native, addons/league_ambessa: everything League does that the data cannot; the user: 「和原版不一样的
地方要做附加包」):
  Q   the sweep marks what it hits (`q_edge` on them, `q_on` on her) without the % max-health part; the add-on deals
      q_pct% of maximum health only to those at the blade's edge (q_tip% of q_r or farther from her).
  Q2  the line marks what it hits (`q2_first`, `q2_on` on her) and has no twin on the action's target; the add-on deals
      q2_pct% of maximum health to the first enemy on the line (the one nearest her).
  W   the brace raises `w_on` on her; the add-on raises `w_hit` when an enemy champion or monster strikes her
      meanwhile, and the slam deals w_pct% of maximum health to everyone it hits only then (main pack: champions,
      always).
  R   the cast marks its champion (`r_aim`) and raises `r_go` on her, nothing else on r_go: the add-on blinks her to the
      farthest enemy champion on the line from her through it (r_range long, r_w half-wide), pins it (r_sup), r_slam
      ticks later slams it (r_dmg + r_ratio% AD + r_pct% max health, r_stun) and fires the combos (Q -> Q2,
      Repudiation ready) and the empowered attack itself.
Sprite tags: idle run attack skill (the sweep) slam (Q2) skill2 (the lash) w (the brace and slam) ult step hit dead.
Timings: drafts until the frames exist.
Numbers: League's Ambessa (recalled in a session without the client: check them against her bins with the
extractor, then rebalance) read into the top fighter range (league_kled, league_yorick, league_darius); not yet
balanced on the classic-SDK simulations (kd.py --lane 0 against fighter, executioner, knight, berserker, lancer and
pole_warrior, league_gnar --native as the control).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_ambessa.data_champion")
ID = "league_ambessa"
FX = "asset/league/effects/league_ambessa_fx"
BIG = "asset/league/effects/league_ambessa_big"

# League's Ambessa (recalled, ~25.S1): 630 +110 hp, 63 AD +3, 35 armour +4.9, 32 mr +2.05, 335 move, 125 range,
# 0.625 attack speed, energy. Passive: after an ability her next move or attack command dashes her ~200 units; the
# attack after it has +50 range, +50% attack speed, bonus physical damage and restores energy. Q: Cunning Sweep, a
# half circle, more (% max hp) at the edge; a hit lets her recast Sundering Slam within 3 s, a line, the first enemy
# hit taking % max hp more. W: a shield as she braces ~0.5 s, then a slam round her, more if struck meanwhile. E: the
# chains lash round her, a slow; her next Step repeats it. R: blinks to the farthest champion in a line, suppresses
# it, slams it down (stun); passive armour penetration and ability lifesteal.
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, def 30, mr 25, move 1000; league_kled 1040 / 90)
    "hp": 1000, "hp_g": 92, "atk": 96, "atk_g": 16, "def": 32, "def_g": 8, "mr": 24, "mr_g": 4,
    "ms": 1050, "ms_g": 12, "regen": 2, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 70, "a_hit": 10,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: Drakehound's Step
    "st_gap": 2, "st_dur": 10, "st_speed": 3000, "st_reach": 45000,
    "pw_t": 180, "pw_as": 50, "pw_dmg": 20, "pw_ratio": 20, "pw_pct": 2,
    # skill: Q Cunning Sweep / Sundering Slam
    "q_cd": 480, "q_range": 30000, "q_dur": 24, "q_hit": 10, "q_r": 30000, "q_dmg": 45, "q_ratio": 70, "q_pct": 3,
    "q2_gap": 18, "q2_win": 180, "q2_range": 40000, "q2_dur": 24, "q2_hit": 12, "q2_len": 40000, "q2_w": 6000,
    "q2_dmg": 50, "q2_ratio": 80, "q2_pct": 5,
    # skill2: E Lacerate
    "e_cd": 540, "e_range": 25000, "e_dur": 24, "e_hit": 10, "e_r": 24000, "e_dmg": 40, "e_ratio": 55,
    "e_slow": 50, "e_slow_t": 60,
    # W Repudiation (the controller)
    "w_cd": 720, "w_trig": 30000, "w_dur": 36, "w_sh": 80, "w_ad": 80, "w_t": 90, "w_brace": 24, "w_r": 25000,
    "w_dmg": 50, "w_ratio": 60, "w_pct": 4,
    # ult: R Public Execution
    "r_cd": 5400, "r_range": 60000, "r_dur": 48, "r_go": 8, "r_sup": 36, "r_slam": 30, "r_dmg": 120,
    "r_ratio": 90, "r_pct": 6, "r_stun": 36, "r_pen": 15,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # the add-on's (addons/league_ambessa): the blade's edge, the line's half-width
    "q_tip": 60, "r_w": 8000,
    "native": 0,
}


# the numbers the add-on reads (passive.params; addons/league_ambessa/src/lib.rs's Params)
ADDON_KEYS = ("ctl_p", "pw_t", "pw_as", "q_r", "q_tip", "q_pct", "q2_pct", "r_range", "r_w", "r_sup", "r_slam",
              "r_dmg", "r_ratio", "r_pct", "r_stun")


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


def attack(dmg, ratio, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def ahead(radius, target, *effects):
    """The half circle in front of her, toward the effect's target (`DirDot` range 0 = 90 degrees each side)."""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": 0}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), attack(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def line(name, length, width, target, effects, delay=2):
    """A line from her through the action's target (a `LineRangeProjectile` in a `Targeting` cast points at it),
    hitting once a tick after it appears (league_chogath's)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": 1, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def build(p):
    ctl_p = p["ctl_p"]
    native = bool(p["native"])

    def busy(t):
        return refresh("busy", t)

    # ------------------------------------------------------------------ passive: Drakehound's Step
    def step(*end):
        """The dash at the target after an ability, and the empowered attack it readies."""
        dash = {"type": "MoveToTarget", "speed": p["st_speed"], "range": p["st_reach"],
                "end_effects": [cview("st_land"), *end]}
        return combine(refresh("pw", p["pw_t"], attack_speed_mult=p["pw_as"]),
                       delayed(p["st_gap"], alive(anim("step", p["st_dur"]), cview("st_dash"), sfx("st"), dash)))

    # ------------------------------------------------------------------ Q Cunning Sweep / Sundering Slam
    def q1_cast():
        # a hit readies the slam (q2_wait for the recast's gap, then q2_go for the slot and the controller)
        # the add-on: the % max-health part only at the blade's edge (`q_edge` marks, `q_on` asks it to look)
        hit = [attack(p["q_dmg"], p["q_ratio"], target_hp=0 if native else p["q_pct"]),
               buff("q_edge", 3) if native else None, view("q_hit"), tsfx("q_hit"),
               on_me(refresh("q2_wait", p["q2_gap"]), refresh("q2_go", p["q2_gap"] + p["q2_win"]))]
        sweep = combine(cview("q_sweep"), sfx("q_sweep"), refresh("q_on", 3) if native else None,
                        ahead(p["q_r"], "EnemyWithoutTower", *[h for h in hit if h is not None]))
        return combine(refresh("q_cd", p["q_cd"]), *rm("q_go", "q2_go", "q2_wait"), busy(p["q_dur"]),
                       anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p),
                       delayed(p["q_hit"] - 1, alive(sweep, step())))

    def q2_cast():
        # the add-on: the bonus on the first enemy on the line (`q2_first` marks, `q2_on` asks it to look); the main
        # pack gives it to the action's target
        first = refresh("q2_on", 4) if native else homing("q2_tw", "EnemyWithoutTower",
                                                         [attack(0, 0, target_hp=p["q2_pct"])])
        mark = [buff("q2_first", 4)] if native else []
        slam = combine(sfx("q2_hit"), first,
                       line("q2_crack", p["q2_len"], p["q2_w"], "EnemyWithoutTower",
                            [attack(p["q2_dmg"], p["q2_ratio"]), *mark, view("q2_hit"), tsfx("q2_hit")]))
        return combine(*rm("q2_go", "q2_wait"), busy(p["q2_dur"]), anim("slam", p["q2_dur"]), sfx("q2"),
                       voice("vo_q2", p), delayed(p["q2_hit"] - 1, alive(slam, step())))

    # ------------------------------------------------------------------ E Lacerate
    def lash():
        return combine(cview("e_lash"), sfx("e_lash"),
                       around(p["e_r"], "EnemyWithoutTower", attack(p["e_dmg"], p["e_ratio"]),
                              buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"),
                              tsfx("e_hit")))

    def e_cast():
        # the step's dash ends in a second lash (anim restarts the lash pose there)
        return combine(refresh("e_cd", p["e_cd"]), busy(p["e_dur"]), anim("skill2", p["e_dur"]), sfx("e"),
                       voice("vo_e", p),
                       delayed(p["e_hit"] - 1, alive(lash(), step(anim("skill2", p["e_dur"] - p["e_hit"]), lash()))))

    # ------------------------------------------------------------------ W Repudiation (the controller casts it)
    def w_cast():
        # the add-on: the bonus on everyone only when she was struck while braced (`w_on` -> `w_hit`); the main pack
        # gives it to the champions, always
        bonus = (sw("w_hit", combine(*rm("w_hit"), around(p["w_r"], "EnemyWithoutTower",
                                                          attack(0, 0, target_hp=p["w_pct"]), view("w_crit"))))
                 if native else around(p["w_r"], "EnemyChampion", attack(0, 0, target_hp=p["w_pct"])))
        slam = combine(cview("w_slam"), sfx("w_slam"),
                       around(p["w_r"], "EnemyWithoutTower", attack(p["w_dmg"], p["w_ratio"]), view("w_hit"),
                              tsfx("w_hit")),
                       bonus, *(rm("w_on") if native else []))
        return combine(refresh("w_cd", p["w_cd"]), busy(p["w_dur"]), anim("w", p["w_dur"]), sfx("w"),
                       *([refresh("w_on", p["w_brace"] + 2), *rm("w_hit")] if native else []),
                       voice("vo_w", p), on_me(shield(p["w_sh"], p["w_ad"], p["w_t"])), cview("w_brace"),
                       delayed(p["w_brace"], alive(slam, step())))

    # ------------------------------------------------------------------ the controller (a pulse on her)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on her is not (league_zac):
    # her attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Ambessa
    # herself (`own`, a flag her attack raises: league_sylas's stolen ult hangs it too)
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        sw("q2_go", sw("q2_wait", NONE, pick(p["q2_range"], "EnemyWithoutTower", q2_cast()))),
        sw("q_go", sw("q_cd", combine(*rm("q_go")), pick(p["q_range"], "EnemyChampion", q1_cast()))),
        sw("w_cd", NONE, sw("busy", NONE, pick(p["w_trig"], "EnemyChampion", w_cast()))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Public Execution
    # R -> Q -> Q2: q_cd off and the controller sweeps the champion (`q_go`); Repudiation ready (Ambessa's own: `own`)
    crash = combine(attack(p["r_dmg"], p["r_ratio"], target_hp=p["r_pct"]), {"type": "Stun", "duration": p["r_stun"]},
                    view("r_crash"), tsfx("r_crash"),
                    sw("own", on_me(*rm("q_cd", "w_cd"), refresh("q_go", ctl_p + 30))))
    pin = combine({"type": "Teleport"}, {"type": "Stun", "duration": p["r_sup"]}, view("r_pin"), tsfx("r_pin"),
                  delayed(p["r_slam"], alive(homing("r_slam", "EnemyChampion", [crash]), step())))
    # the add-on: the farthest champion on the line, the blink, the pin, the slam and the combos (`r_aim` on the
    # cast's champion, `r_go` on her)
    go = combine(buff("r_aim", 4), on_me(refresh("r_go", 4))) if native else pin
    r_cast = combine(on_me(refresh("r_pen", None, defence_penetration=p["r_pen"])), busy(p["r_dur"]),
                     anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                     delayed(p["r_go"] - 1, alive(cview("r_blink"), go)))

    # ------------------------------------------------------------------ attack (+ the empowered one)
    def blow(extra=()):
        return homing("a_blow", "Enemy", [attack(0, 100), *extra, view("a_hit"), tsfx("a_hit")])

    strong = combine(*rm("pw"), sfx("a_pw"),
                     blow([attack(p["pw_dmg"], p["pw_ratio"], target_hp=p["pw_pct"]), view("pw_hit")]))
    hit_now = delayed(p["a_hit"] - 1, alive(sfx("a"), sw("pw", strong, blow())))

    # ------------------------------------------------------------------ the slots
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("own", NONE, flag("own", None)), hang, hit_now),
                      atype="BaseAttack", cancel=True)
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"]), hang, r_cast), key="ult")
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"]),
                           sw("q2_go", sw("q2_wait", NONE, q2_cast()), sw("q_cd", NONE, q1_cast()))), key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"]), sw("e_cd", NONE, e_cast())), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("q2_crack", anim_=BIG)]
    views_e = [E("a_hit"), E("pw_hit"), E("st_dash", BIG, -1), E("st_land", FX, -1, False), E("q_sweep", BIG, 3),
               E("q_hit"), E("q2_hit"), E("e_lash", BIG, 3), E("e_hit"), E("w_brace", FX, 3), E("w_slam", BIG, -1),
               E("w_hit"), E("r_blink", BIG, 3, False), E("r_pin"), E("r_crash", BIG, -1, False)]
    views_b = [B_("e_slow", FX, -1, "slow"), B_("pw", FX, -1, "pw_aura")]
    extra = {}
    if native:   # addons/league_ambessa: the League rules the data cannot read
        views_e += [E("q_tip"), E("w_crit")]
        extra["passive"] = {"passive_ref": "league_ambessa:matriarch",
                            "params": {k: p[k] for k in ADDON_KEYS}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Shield", "CC"], **extra,
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
