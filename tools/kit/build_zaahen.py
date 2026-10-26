"""Build league_zaahen.data_champion (top, Melee fighter, AD: Zaahen, the Unsundered) from the parameters P.

    python tools/kit/build_zaahen.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-26: TOP, layout A - Q / W / R, Aureate Rush (E) folded into W; combos all four: W's pull
on a champion -> Q ready, Q's knock-up on a champion -> R's cooldown cut, R's slam on a champion -> Determination up a
long way, Determination full -> Q and W ready; an add-on for every place that is not League's).
TFM2 has three active slots for League's four buttons: The Darkin Glaive (Q) is `skill`, Dreaded Return (W) `skill2`,
Grim Deliverance (R) the `ult`. Q and W keep their cooldowns in flags (`q_cd`, `w_cd`; league_trundle's) so the combos
can cast or refresh them; a slot cast while its flag is up does nothing (a 3-tick idle). Flags die with him.
  passive Cultivation of War (不落之志): every hit of his on an enemy champion (attack, both Q slashes, the knock-up, W,
          the folded E) raises `dh`; the controller turns it into one level of Determination - a ladder of det_n flags
          d1..dN, each det_ad% attack, all refreshed to det_t ticks by every new level (League: 5 s, refreshed per hit).
          R's slam on a champion raises `dh3`: det_r levels at once. The last level clears the ladder for `full`:
          full_ad% attack for full_t ticks, refreshed by every hit while it lasts. League's revive at full Determination
          cannot be read by the data: the main pack's stand-in is a shield (rv_sh + rv_sh_r% AD, rv_t ticks) when he
          fills up, at most once every rv_cd ticks.
  attack  A glaive sweep (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit.
  skill   Q The Darkin Glaive (暗裔长刀), `Targeting` on `EnemyWithoutTower` in his reach (q_range): the first cast (`q_cd`
          free) slashes twice (q_h1, q_h2: q_dmg + q_ratio% AD each) and heals him q_heal + q_heal_r% AD for every slash
          on a champion (half on other units); it opens the recast (`q2`, q_win ticks, usable after q_gap): the next cast
          strikes once more for q3_dmg + q3_ratio% AD and knocks the unit up for q_air ticks. q_cd starts at the first cast.
  skill2  W Dreaded Return (厄影回锋), `Targeting` on `EnemyWithoutTower` within w_range: on w_rel the glaive flies out
          w_len (a `LinearProjectile` through everyone): w_dmg + w_ratio% AD, a w_stun-tick stun and a pull to him
          (`Grab`, league_thresh's). Aureate Rush (E) folded in: on w_e he spins the glaive round him (e_r): e_dmg +
          e_ratio% AD - the pulled units stand there.
  ult     R Grim Deliverance (大赦), `Targeting` on `EnemyChampion` within r_range: he rises (cc immune and r_dr% less
          damage taken for r_dur ticks), on r_jump he dives at the champion (`MoveToTarget`) and on r_slam the glaive
          strikes the ground: r_dmg + r_ratio% AD round him (r_r), r_heal + r_heal_r% AD healed per champion hit.
  combos  W -> Q: the glaive pulling a champion takes `q_cd` and `q2` off; the controller casts Q's first slashes on the
          first champion in reach (`q_go`, q_go_t ticks). Q -> R: the knock-up on a champion adds a 3-tick caster buff
          with ult_cooldown_mult r_cut (the cap at cooltime x 100 / (100 + r_cut), champion-data section 5). R -> P: the
          slam on a champion adds det_r levels (`dh3`). P full -> Q + W: filling up takes `q_cd`, `q2` and `w_cd` off.
  controller An AddCasted pulse on him every ctl_p ticks (league_trundle's, hung by his attack and the ult, only for
          Zaahen himself: `own`): Determination, the combos' casts.
The add-on copy (--native, addons/league_zaahen: every place the data is not League's): the passive league_zaahen:darkin
counts Determination itself (League's 12 stacks from every damage instance on a champion, det_pct% attack each
and twice that at full, the decay after det_t ticks: 1 more stack every 30 ticks), revives him once filled (lethal
damage held at 1 health, rv_rise ticks invulnerable and unable to act while rv_hp% of his maximum health comes back,
then up with Determination full again; rv_cd ticks between revives; banished meanwhile, the revive drawn by its
picture `rv_rise`); gives Aureate
Rush its own slot back (every e_cd ticks, an enemy champion within e_reach and out of his reach: he dashes e_dash
toward it and the data spins on `e_go` - inner e_r0 / outer e_r ring, the outer edge e_out% more and e_pct% of the
unit's maximum health, all dealt by the add-on); and heals Q by League's share of his maximum health (q_hp% of it a
slash on a champion, half on other units: the data marks `q_mark`, its flat heal goes). Both packs: R's passive r_pen%
defence penetration on his `own` flag; R's heal per champion hit is League's (fixed + AD, not a share of the damage);
W's stun and pull are data (`Grab`), its two damage instances one.
Timings: drafts until the frames exist (tools/art/rig_zaahen.py retimes them).
Numbers: League 16.21 read into the top fighter range (league_darius, league_aatrox, league_ambessa); not balanced yet.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_zaahen.data_champion")
ID = "league_zaahen"
FX = "asset/league/effects/league_zaahen_fx"
BIG = "asset/league/effects/league_zaahen_big"

# League's Zaahen (16.21): 640 +114 hp, 63 AD +4, 36 armour +5, 32 mr +2.05, 345 move, 175 range, 0.625 attack speed.
# Passive: 12 Determination from damage on champions (5 s), 1.5-2.95% bonus AD each, doubled at full; full: lethal damage
# -> 4 s resurrection healing 30-75% max hp, cd 300-120. Q: two strikes 15-75 + 100% AD total, heals 5-9% max hp on
# champions; recast window 1.5 s after for 4 s: 30-150 + bonus AD and a 0.75 s knock-up; cd 10-6. W: 850 out, 70-230 +
# 80% bonus AD in two parts, a 225 pull and a 0.25 s stun, cd 14-12. E: dash 350, ring 375 (inner 200), the outer edge
# more + 4-6% max hp magic, cd 10-8. R: 600 range, 0.6 s slam, 550 radius, 250-550 + 200% bonus AD, heals 82-181 + 66%
# bonus AD per champion, cc immune + 50% less damage while casting, cd 110-80; passive 10-30% armour penetration.
P = {
    # stats (base fighters: attack 90 +12, hp 1000 +100, defence 35 +8; league_darius, league_aatrox)
    "hp": 1080, "hp_g": 110, "atk": 88, "atk_g": 13, "apw": 10, "apw_g": 5, "def": 34, "def_g": 9, "mr": 30, "mr_g": 4,
    "ms": 1000, "ms_g": 11, "regen": 2, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 72, "a_hit": 12,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: Determination
    "det_n": 12, "det_ad": 2, "det_t": 300, "det_r": 4, "full_ad": 30, "full_t": 300,
    "rv_sh": 120, "rv_sh_r": 100, "rv_t": 180, "rv_cd": 3600,
    # skill: Q The Darkin Glaive
    "q_cd": 420, "q_range": 27000, "q_dur": 34, "q_h1": 12, "q_h2": 22, "q_dmg": 20, "q_ratio": 70,
    "q_heal": 30, "q_heal_r": 15, "q_gap": 90, "q_win": 330,
    "q3_dur": 30, "q3_hit": 14, "q3_dmg": 60, "q3_ratio": 60, "q_air": 45, "q_go_t": 120,
    # skill2: W Dreaded Return (+ E Aureate Rush folded in)
    "w_cd": 780, "w_range": 52000, "w_dur": 30, "w_rel": 14, "w_len": 56000, "w_wid": 6000, "w_speed": 5000,
    "w_dmg": 70, "w_ratio": 60, "w_stun": 15, "w_grab": 3500,
    "w_e": 34, "w_e_dur": 56, "e_r": 20000, "e_dmg": 50, "e_ratio": 50,
    # ult: R Grim Deliverance
    "r_cd": 4800, "r_range": 40000, "r_dur": 60, "r_dr": 50, "r_jump": 26, "r_speed": 4000, "r_slam": 40,
    "r_r": 22000, "r_dmg": 160, "r_ratio": 150, "r_heal": 60, "r_heal_r": 40, "r_cut": 100,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_zaahen (League's rules the data cannot read, see the docstring); its parameters
    "native": 0, "det_pct": 1, "rv_rise": 240, "rv_hp": 50, "e_cd": 540, "e_reach": 48000, "e_dash": 22000,
    "e_r0": 11000, "e_out": 50, "e_pct": 5, "e_dur": 26, "e_hit": 14, "q_hp": 6,
    # R's passive armour penetration (League 10-30%; on his `own` flag, both packs)
    "r_pen": 20,
}


# the numbers addons/league_zaahen reads from passive.params (its Params, in this order)
NATIVE_KEYS = ("det_n", "det_pct", "det_t", "rv_rise", "rv_hp", "rv_cd", "e_cd", "e_reach", "e_dash", "e_r0", "e_r",
               "e_out", "e_pct", "e_dmg", "e_ratio", "e_hit", "q_hp", "atk_range")


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


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": [e for e in effects if e is not None]}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), attack(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects if e is not None]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def line(name, speed, length, width, target, effects, y=2000):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": length, "shape": circle(width),
            "penetrate": True, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects if e is not None], "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    ctl_p = p["ctl_p"]
    native = p["native"]
    dh = refresh("dh", ctl_p + 1)   # one hit on a champion, for the controller (Determination)

    # ------------------------------------------------------------------ passive: Determination (on the controller)
    # the levels d1..dN are permanent flags with det_ad% attack each; `det_live` (det_t ticks, renewed by every level)
    # keeps them: once it runs out the controller clears them all (League: 5 s from the last hit)
    levels = [f"d{k}" for k in range(1, p["det_n"] + 1)]

    def ladder():
        """One level up - the highest level held decides: d(N-1) held -> full, d(k) held -> d(k+1), none -> d1."""
        out = flag(levels[0], None, attack_mult=p["det_ad"])
        for k in range(1, len(levels)):     # the last test wrapped is the highest: it sits outermost
            nxt = filled() if k == len(levels) - 1 else flag(levels[k], None, attack_mult=p["det_ad"])
            out = sw(levels[k - 1], nxt, out)
        return combine(refresh("det_live", p["det_t"]), out)

    def level_up():
        """A hit on a champion: full renews itself, otherwise one level."""
        return sw("full", refresh("full", p["full_t"], attack_mult=p["full_ad"]), ladder())

    def filled():
        """The top level: the ladder cleared and `full` on at once; the rest of filling up (`fill`) once, after."""
        return combine(*rm(*levels), refresh("full", p["full_t"], attack_mult=p["full_ad"]), refresh("fill", 2))

    def fill():
        """Determination full: Q and W ready (the combo), the picture and the line, the stand-in shield."""
        shield = None
        if not native:
            shield = sw("rv_cd", NONE, combine(refresh("rv_cd", p["rv_cd"]),
                                               on_me({"type": "Shield", "amount": p["rv_sh"],
                                                      "attack_ratio": p["rv_sh_r"], "ap_ratio": 0,
                                                      "tick": p["rv_t"]}, view("p_shield"))))
        return combine(*rm("fill", "q_cd", "q2", "w_cd"), on_me(view("p_full")), sfx("p_full"), voice("vo_p", p),
                       shield)

    # ------------------------------------------------------------------ Q The Darkin Glaive
    def slash(name, hit_view):
        # half the heal on every unit, the other half on a champion (no target picks minions and monsters only)
        # (the add-on heals by League's share of his maximum health instead: `q_mark` on the unit, one a slash)
        half = buff("q_mark", 3) if native else heal(p["q_heal"] // 2, p["q_heal_r"] // 2)
        champ = None if native else homing(name + "c", "EnemyChampion", [half, dh])
        return combine(sfx("q_hit"), homing(name, "EnemyWithoutTower", [
            attack(p["q_dmg"], p["q_ratio"]), half, view(hit_view), tsfx("q_hit")]), champ)

    def q_first():
        return combine(refresh("q_cd", p["q_cd"]), refresh("q2", p["q_win"]), refresh("q_gap", p["q_gap"]),
                       refresh("busy", p["q_dur"]), *rm("q_go"), anim("skill", p["q_dur"]), sfx("q"),
                       voice("vo_q", p), delayed(p["q_h1"] - 1, alive(slash("q_s1", "q_hit"))),
                       delayed(p["q_h2"] - 1, alive(slash("q_s2", "q_hit2"))))

    def q_recast():
        # Q -> R: the knock-up on a champion caps R's cooldown (a 3-tick ult_cooldown_mult buff)
        champ = homing("q_upc", "EnemyChampion", [dh, refresh("r_cut", 3, ult_cooldown_mult=p["r_cut"])])
        up = combine(sfx("q_up"), homing("q_up", "EnemyWithoutTower", [
            attack(p["q3_dmg"], p["q3_ratio"]), {"type": "Airborne", "duration": p["q_air"]}, view("q_uphit"),
            tsfx("q_up")]), champ)
        return combine(*rm("q2", "q_go"), refresh("busy", p["q3_dur"]), anim("skill_up", p["q3_dur"]), sfx("q2"),
                       delayed(p["q3_hit"] - 1, alive(up)))

    def q_slot():
        return sw("q2", sw("q_gap", NONE, q_recast()), sw("q_cd", NONE, q_first()))

    # ------------------------------------------------------------------ W Dreaded Return (+ E folded in)
    def w_cast():
        # W -> Q: the glaive pulling a champion takes Q's cooldown and recast off (`q_go`: the controller slashes)
        champ = [dh, combine(*rm("q_cd", "q2"), refresh("q_go", p["q_go_t"]))]
        stab = line("w_glaive", p["w_speed"], p["w_len"], p["w_wid"], "EnemyWithoutTower", [
            attack(p["w_dmg"], p["w_ratio"]), {"type": "Stun", "duration": p["w_stun"]},
            {"type": "Grab", "speed": p["w_grab"]}, view("w_hit"), tsfx("w_hit")])
        stab_c = line("w_glaivec", p["w_speed"], p["w_len"], p["w_wid"], "EnemyChampion", champ)
        spin = None
        if not native:   # Aureate Rush folded in: the spin round him once the pulled units are there
            spin = delayed(p["w_e"] - 1, alive(sfx("e"), on_me(view("e_spin")), around(
                p["e_r"], "EnemyWithoutTower", attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")),
                around(p["e_r"], "EnemyChampion", dh)))
        return combine(refresh("w_cd", p["w_cd"]), refresh("busy", p["w_e_dur"] if not native else p["w_dur"]),
                       anim("skill2", p["w_e_dur"] if not native else p["w_dur"]), sfx("w"), voice("vo_w", p),
                       delayed(p["w_rel"] - 1, alive(stab, stab_c)), spin)

    # ------------------------------------------------------------------ E Aureate Rush (the add-on's own slot)
    def e_spin():
        """The add-on has dashed him (`e_go`): the spin; the outer ring and the % health are the add-on's (`e_ring`)."""
        return combine(*rm("e_go"), refresh("busy", p["e_dur"]), anim("skill3", p["e_dur"]), sfx("e"),
                       voice("vo_e", p), delayed(p["e_hit"] - 1, alive(
                           on_me(view("e_spin")), refresh("e_ring", 3),
                           around(p["e_r"], "EnemyChampion", dh, view("e_hit"), tsfx("e_hit")))))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not (league_zac):
    # his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Zaahen
    # himself (`own`, a flag his attack raises: league_sylas's stolen ult hangs it too)
    det = sw("fill", fill())   # the add-on fills him itself (its `fill` flag): the combo and the picture stay data
    if not native:   # R's slam on a champion: det_r levels at once (a buff added is seen by the next test, same tick)
        det = combine(sw("dh3", combine(*rm("dh3"), *[level_up() for _ in range(p["det_r"])])),
                      sw("dh", combine(*rm("dh"), level_up())), sw("fill", fill()),
                      sw("det_live", NONE, sw(levels[0], combine(*rm(*levels)))))
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        det,
        sw("e_go", sw("busy", NONE, e_spin())) if native else None,
        sw("q_go", sw("busy", NONE, sw("q_cd", NONE, pick(p["q_range"], "EnemyChampion", q_first())))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Grim Deliverance
    slam_c = [heal(p["r_heal"], p["r_heal_r"]), refresh("dh3", ctl_p + 1)]
    slam = combine(sfx("r_slam"), on_me(view("r_slam")),
                   around(p["r_r"], "EnemyWithoutTower", attack(p["r_dmg"], p["r_ratio"]), view("r_hit"),
                          tsfx("r_hit")),
                   around(p["r_r"], "EnemyChampion", *slam_c))
    r_cast = combine(refresh("r_guard", p["r_dur"], cc_immune=True, damaged_reduce=p["r_dr"]),
                     anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p), on_me(view("r_rise")),
                     delayed(p["r_jump"] - 1, alive({"type": "MoveToTarget", "speed": p["r_speed"],
                                                     "range": p["r_range"] + 20000, "end_effects": []})),
                     delayed(p["r_slam"] - 1, alive(slam)))

    # ------------------------------------------------------------------ attack
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   homing("a_c", "EnemyChampion", [dh]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("own", NONE, flag("own", None, defence_penetration=p["r_pen"])), hang,
                              delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"]), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"] * 2, p["q_ratio"] * 2), q_slot()), key="skill")
    skill2 = action("idle", 3, 60, 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["w_dmg"], p["w_ratio"]), sw("w_cd", NONE, w_cast())), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    P_ = lambda name, anim_=FX, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 3}
    views_e = [E("a_hit"), E("q_hit"), E("q_hit2"), E("q_uphit"), E("w_hit"), E("e_spin", BIG, 1, False),
               E("e_hit"), E("r_rise", BIG, 1, True), E("r_slam", BIG, -1, False), E("r_hit"), E("p_full")]
    if not native:
        views_e.append(E("p_shield"))
    views_b = [B_("full", FX, -1, "p_aura"), B_("r_guard", FX, 3, "r_guard")]
    views_p = [P_("w_glaive", FX, "w_glaive")]
    if native:   # the add-on's revive: its banish plays rv_rise (him rising again in its light) and ends on p_full
        views_e.append(E("rv_rise", BIG, 2, True))
    extra = {}
    if native:   # addons/league_zaahen: the League rules the data cannot read
        extra["passive"] = {"passive_ref": "league_zaahen:darkin",
                            "params": {k: p[k] for k in NATIVE_KEYS}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee"], **extra,
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
