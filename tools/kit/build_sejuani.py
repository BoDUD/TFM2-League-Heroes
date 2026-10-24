"""Build league_sejuani.data_champion (jungle, Melee tank, AP: Sejuani, the Fury of the North) from the parameters P.

    python tools/kit/build_sejuani.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-24: JUNGLE, layout A - Q / W / R, Permafrost (E) folded into the passive; combos Q's
knock-up on a champion -> W at once, W filling the Frost -> the freeze, any stun -> the shatter, R's stun -> Q ready
again and cast at it).
TFM2 has three active slots for League's four buttons: Arctic Assault (Q) is `skill`, Winter's Wrath (W) `skill2`,
Glacial Prison (R) the `ult`. Q and W keep their cooldowns in flags (`q_cd`, `w_cd`; league_belveth's) so the combos
can cast them; a slot cast while its flag is up does nothing (a 3-tick idle). Flags die with her: a respawned Sejuani
has Q and W ready.
  passive Fury of the North (北地之怒): Frost Armour - while she has not attacked or cast for fa_out ticks (`fight`)
          the controller keeps fa_def% defence, fa_mr% magic resistance and fa_tough tenacity on her (the game has no
          slow immunity: tenacity stands in), and it lingers fa_keep ticks into a fight.
          Permafrost (永冻领域, E) folded in: her attacks and each of W's two swings add a Frost stack on the champion
          they hit; the fourth freezes it - e_stun ticks stunned, e_dmg + e_ap% AP. The stacks are counted on her
          (hidden caster buffs f1..f3, f_t ticks each, league_darius's Hemorrhage: the kit cannot read a target's
          buffs), so stacks from two champions add up.
          The shatter: a champion she stunned (the freeze, Q's knock-up, R) is open to it for sh_win ticks (`sh_on`):
          her next hit on a champion (an attack, W) adds sh_dmg + sh_ap% AP + sh_pct% of its maximum health as true
          damage, at most once every sh_cd ticks. Stuns by her allies: the add-on (it reads crowd control natively).
  attack  A flail blow (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; its champion twin checks the
          shatter, then adds a Frost stack.
  skill   Q Arctic Assault (极寒突袭), `Targeting` on `EnemyWithoutTower` (q_range, `q_cd`): on q_go Bristle charges at
          the target and through (`RushTime`, q_speed x q_t, penetrate): q_dmg + q_ap% AP and knocked up q_up ticks to
          every enemy passed. League's charge stops at the first champion: here the charge ends at the target.
  skill2  W Winter's Wrath (凛冬之怒), `Targeting` on `EnemyWithoutTower` (w_range, `w_cd`): on w_rel1 the flail sweeps
          round her (w_r1): w1_dmg + w1_ap% AP, w_slow% slower for w_slow_t; on w_rel2 it slams a line toward the
          target (w_len long, w_rad wide): w2_dmg + w2_ap% AP and the slow. Each swing adds one Frost stack (once a
          swing, on the first champion it hits).
  ult     R Glacial Prison (极冰寒狱), `Targeting` on `EnemyChampion` within r_range: on r_rel the bola flies (a line
          stopping on the first champion, r_speed, r_len): r_stun ticks stunned, r_dmg + r_ap% AP; where it stops an
          ice storm (r_sr) slows every enemy r_slow% for r_storm ticks.
  combos  Q -> W: a charge through an enemy champion takes `w_cd` off and has the controller swing W at the first
          champion in reach (once she has cast W herself this life, `w_lv`). W -> freeze: W's two swings bring the Frost to four. Stun ->
          shatter (above). R -> Q: the bola's stun takes `q_cd` off and the controller charges Q at a
          champion in reach while the stun lasts (`q_go`, r_stun ticks).
  controller An AddCasted pulse on her every ctl_p ticks (league_belveth's, hung by her attack and the ult, only for
          Sejuani herself: `own`): the Frost Armour, the combos' casts.
The add-on copy (--native, addons/league_sejuani: everything League does that the data cannot): the passive
league_sejuani:frost keeps the Frost stacks on each champion (the data adds a `frost` buff to it, f_n of them freeze
it: stunned e_stun ticks, e_dmg + e_ap% AP), shatters every champion she hits while it is stunned or knocked up by
anyone (her allies too: a 3-tick `hit` mark from her attack and W; sh_cd ticks a champion), clears every slow off her
while the Frost Armour lasts (no tenacity stand-in) and puts her in combat (`fight`) when she takes damage, and stops
Arctic Assault at the first enemy champion (`q_stop`: she is held where she hit it for the rest of the charge).
Timings: drafts until the frames exist (tools/art/rig_sejuani.py retimes them).
Numbers: League 16.21 read into the jungle tank range (league_zac, league_nunu, league_rammus), balanced on the
classic-SDK simulations (kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/se_sim, 2026-10-24).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_sejuani.data_champion")
ID = "league_sejuani"
FX = "asset/league/effects/league_sejuani_fx"
BIG = "asset/league/effects/league_sejuani_big"

# League's Sejuani (16.21): 630 +114 hp, 66 AD +4, 34 armour +5.45, 32 mr +2.05, 340 move, 150 range, 0.688 attack
# speed. Passive: Frost Armour out of combat (armour / mr, slow immunity), shatter = 10% max hp magic on a stunned
# enemy. Q: 650 charge, 90-290 + 60% AP, knock-up 0.5 s, stops on the first champion, cd 18-12. W: two swings, 20-60 +
# 20% AP +2% max hp, then 30-250 + 60% AP +6% max hp, slow 50%, Frost each, cd 9-5. E: 4 Frost -> stun 1-1.5 s,
# 55-255 + 60% AP. R: bola 1300, 125-325 + 80% AP, stun 1-1.5 s, storm slows 30% (a later blast), cd 120-90.
P = {
    # stats (base tanks: attack 80 +6, hp 1100 +120, defence 40 +10, mr 30 +5; league_zac 1150 / 72, apw 30 +15)
    "hp": 1150, "hp_g": 120, "atk": 70, "atk_g": 6, "apw": 30, "apw_g": 15, "def": 40, "def_g": 10, "mr": 30,
    "mr_g": 5, "ms": 1000, "ms_g": 11, "regen": 2, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 70, "a_hit": 11,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: Frost Armour
    "fa_out": 300, "fa_keep": 120, "fa_def": 40, "fa_mr": 40, "fa_tough": 30,
    # passive: Permafrost (Frost stacks -> freeze) and the shatter
    "f_t": 300, "f_n": 4, "e_stun": 60, "e_dmg": 40, "e_ap": 40,
    "sh_win": 90, "sh_cd": 300, "sh_dmg": 20, "sh_ap": 40, "sh_pct": 6,
    # skill: Q Arctic Assault
    "q_cd": 480, "q_range": 45000, "q_dur": 24, "q_go": 6, "q_speed": 6000, "q_t": 8, "q_dmg": 60, "q_ap": 60,
    "q_up": 30,
    # skill2: W Winter's Wrath
    "w_cd": 360, "w_range": 30000, "w_dur": 40, "w_rel1": 10, "w_rel2": 26, "w_r1": 22000, "w_len": 45000,
    "w_rad": 7000, "w_speed": 30000, "w1_dmg": 30, "w1_ap": 30, "w2_dmg": 50, "w2_ap": 50, "w_slow": 40,
    "w_slow_t": 90,
    # ult: R Glacial Prison
    "r_cd": 4200, "r_range": 70000, "r_dur": 30, "r_rel": 14, "r_speed": 12000, "r_len": 80000, "r_dmg": 120,
    "r_ap": 80, "r_stun": 75, "r_sr": 26000, "r_slow": 35, "r_storm": 120,
    # her spoken lines, at most one every vo_gap ticks
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


def stun(tick):
    return {"type": "Stun", "duration": tick}


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


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def line(name, speed, rng, radius, target, effects, penetrate=True, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def build(p):
    ctl_p = p["ctl_p"]

    # ------------------------------------------------------------------ passive: Fury of the North
    def fight():
        """She attacked or cast: the Frost Armour stops being renewed (it lingers fa_keep ticks)."""
        return refresh("fight", p["fa_out"])

    # the add-on clears slows off her while `fa` lasts (no tenacity stand-in) and renews `fight` when she is hurt
    fa = dict(defence_mult=p["fa_def"], magic_resistance_mult=p["fa_mr"])
    if not p["native"]:
        fa["toughness"] = p["fa_tough"]
    armour = sw("fight", NONE, refresh("fa", p["fa_keep"], **fa))

    def open_shatter(tick):
        """A champion she just stunned (in its hit's context) is open to the shatter."""
        return refresh("sh_on", tick)

    # the shatter, in a champion hit's context: her next hit on a stunned champion
    shatter = sw("sh_on", sw("sh_cd", NONE, combine(*rm("sh_on"), flag("sh_cd", p["sh_cd"]),
                                                    ap(p["sh_dmg"], p["sh_ap"]), pct(p["sh_pct"]),
                                                    view("sh_hit"), tsfx("sh_hit"))))
    # Permafrost: one Frost stack (counted on her, f1..f3), the fourth freezes the champion hit
    freeze = combine(*rm("f1", "f2", "f3"), stun(p["e_stun"]), ap(p["e_dmg"], p["e_ap"]), view("e_freeze"),
                     tsfx("e_freeze"), open_shatter(p["e_stun"] + p["sh_win"]))
    frost = sw("f3", freeze, sw("f2", flag("f3", p["f_t"]), sw("f1", flag("f2", p["f_t"]), flag("f1", p["f_t"]))))
    if p["native"]:   # the add-on: a Frost stack on the champion itself (it freezes at four) and a hit mark (the shatter)
        frost = combine(buff("frost", p["f_t"]), buff("hit", 3))
        shatter = NONE

    # ------------------------------------------------------------------ Q Arctic Assault
    def q_cast():
        # Q -> W: through a champion (once a cast: `q_lk`), the controller swings W (once she has cast W: `w_lv`)
        champ = homing("q_tw", "EnemyChampion", [sw("q_lk", NONE, combine(
            flag("q_lk", p["q_t"] + 4), open_shatter(p["q_up"] + p["sh_win"]), flag("q_stop", 2) if p["native"] else None,
            sw("w_lv", combine(*rm("w_cd"), refresh("w_go", ctl_p + p["q_t"] + 3))), view("f_mark")))])
        hit = [ap(p["q_dmg"], p["q_ap"]), {"type": "Airborne", "duration": p["q_up"]}, view("q_hit"), tsfx("q_hit"),
               champ]
        rush = {"type": "RushTime", "speed": p["q_speed"], "tick": p["q_t"], "range": 1000,
                "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": [T(e) for e in hit]}
        return combine(refresh("q_cd", p["q_cd"]), *rm("q_lk"), fight(), anim("skill", p["q_dur"]), sfx("q"),
                       voice("vo_q", p), delayed(p["q_go"] - 1, alive(cview("q_dash"), rush)))

    # ------------------------------------------------------------------ W Winter's Wrath
    def w_cast():
        def swing(lk, dmg, ratio):
            once = frost if p["native"] else sw(f"w_lk{lk}", NONE, combine(flag(f"w_lk{lk}", 6), frost))
            champ = homing(f"w_tw{lk}", "EnemyChampion", [shatter, once])
            return [ap(dmg, ratio), buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_hit"),
                    tsfx("w_hit"), champ]
        sweep = around(p["w_r1"], "EnemyWithoutTower", *swing(1, p["w1_dmg"], p["w1_ap"]))
        slam = line("w_line", p["w_speed"], p["w_len"], p["w_rad"], "EnemyWithoutTower",
                    swing(2, p["w2_dmg"], p["w2_ap"]))
        return combine(refresh("w_cd", p["w_cd"]), *rm("w_lk1", "w_lk2"), fight(), anim("skill2", p["w_dur"]),
                       sfx("w"), voice("vo_w", p),
                       delayed(p["w_rel1"] - 1, alive(cview("w_sweep"), sfx("w_sweep"), sweep)),
                       delayed(p["w_rel2"] - 1, alive(cview("w_slam"), sfx("w_slam"), slam)))

    # ------------------------------------------------------------------ the controller (a pulse on her)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on her is not (league_zac):
    # her attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Sejuani
    # herself (`own`, a flag her attack raises: league_sylas's stolen ult hangs it too, league_singed)
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        armour,
        sw("q_go", sw("q_cd", combine(*rm("q_go")), pick(p["q_range"], "EnemyChampion", combine(*rm("q_go"), q_cast())))),
        sw("w_go", combine(*rm("w_go"), sw("w_cd", NONE, pick(p["w_range"], "EnemyChampion", w_cast())))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Glacial Prison
    # R -> Q: the frozen champion takes q_cd off her and the controller charges at it (Sejuani's own: `own`)
    prison = [stun(p["r_stun"]), ap(p["r_dmg"], p["r_ap"]), view("r_hit"), tsfx("r_hit"),
              open_shatter(p["r_stun"] + p["sh_win"]), sw("own", combine(*rm("q_cd"), refresh("q_go", p["r_stun"])))]
    storm = [view("r_storm"), sfx("r_storm"),
             field("r_ice", p["r_sr"], p["r_storm"], 10,
                   [buff("r_slow", 20, move_speed_mult=-p["r_slow"])], first=1)]
    bola = line("r_bola", p["r_speed"], p["r_len"], 2000, "EnemyChampion", prison, penetrate=False, end=storm)
    r_cast = combine(fight(), anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                     delayed(p["r_rel"] - 1, alive(sfx("r_throw"), bola)))

    # ------------------------------------------------------------------ attack
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   homing("a_tw", "EnemyChampion", [shatter, frost]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100, attack), sw("own", NONE, flag("own", None)), hang, fight(),
                              delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ap"]), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ap"]), sw("q_cd", NONE, q_cast())), key="skill")
    skill2 = action("idle", 3, 60, 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["w1_dmg"] + p["w2_dmg"], p["w1_ap"] + p["w2_ap"]),
                            sw("w_cd", NONE, combine(sw("w_lv", NONE, flag("w_lv", None)), w_cast()))), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("w_line"), Pj("r_bola")]
    views_e = [E("a_hit"), E("q_dash", FX, -1, False), E("q_hit"), E("f_mark"), E("w_sweep", BIG, -1, False),
               E("w_slam", BIG, -1, False), E("w_hit"), E("e_freeze"), E("sh_hit"), E("r_hit"),
               E("r_storm", BIG, -1, False)]
    views_b = [B_("fa", FX, -1, "fa_armour"), B_("w_slow", FX, -1, "slow"), B_("r_slow", FX, -1, "slow")]
    extra = {}
    if p["native"]:   # addons/league_sejuani: the League rules the data cannot read
        views_b.append(B_("frost", FX, 3, "frost"))
        extra["passive"] = {"passive_ref": "league_sejuani:frost",
                            "params": {k: p[k] for k in ("f_n", "e_stun", "e_dmg", "e_ap", "sh_cd", "sh_dmg", "sh_ap",
                                                         "sh_pct", "q_t", "fa_out")}}
    return {
        "id": ID, "category": "Melee", "tags": ["AP", "Melee", "CC", "Tank"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0,
                 "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
