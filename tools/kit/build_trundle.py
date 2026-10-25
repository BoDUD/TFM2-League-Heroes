"""Build league_trundle.data_champion (jungle, Melee fighter-tank, AD: Trundle, the Troll King) from the parameters P.

    python tools/kit/build_trundle.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-25: JUNGLE, layout A - Q / E / R, Frozen Domain (W) folded into the passive; combos all
four: E's pillar on a champion -> Q ready, Q's bite on a champion -> the domain at once, R -> Q ready + a pillar on the
target, a kill on the domain -> King's Tribute heals double).
TFM2 has three active slots for League's four buttons: Chomp (Q) is `skill`, Pillar of Ice (E) `skill2`, Subjugate (R)
the `ult`. Q and E keep their cooldowns in flags (`q_cd`, `e_cd`; league_sejuani's) so the combos can cast them; a slot
cast while its flag is up does nothing (a 3-tick idle). Flags die with him: a respawned Trundle has Q, E and W ready.
  passive King's Tribute (国王的贡品): a unit his attack or Q kills heals him p_heal + p_heal_r% AD (the kill trigger,
          league_jinx's: a twin on the unit hit, a 3-tick casted that clears a flag while it lives), twice as much while
          the domain is on (`w_on`).
          Frozen Domain (冰封领域, W) folded in: Q biting an enemy champion freezes the ground (his `w` hop, once every w_cd
          ticks): for w_t ticks he has w_as% attack speed, w_ms% move speed and w_regen health regeneration (League:
          more healing from every source; the data has no healing amplifier).
  attack  A club blow (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; its twin is the kill trigger.
  skill   Q Chomp (利齿撕咬), `Targeting` on `EnemyWithoutTower` in melee reach (q_range, `q_cd`): on q_hit he bites for
          q_dmg + q_ratio% AD, the unit is q_slow% slower for q_slow_t ticks and q_sap% weaker (attack) for q_t ticks, he
          is q_gain% stronger for q_t ticks; on a champion the domain (above) when W is ready.
  skill2  E Pillar of Ice (寒冰之柱), `Targeting` on `EnemyChampion` (e_range, `e_cd`): on e_rel the pillar rises on the
          target (a 1-tick lob, league_annie R): every enemy within e_r is e_slow% slower while the pillar stands (e_t
          ticks); with e_root the champions at it are held that long (`Bind`, a stand-in for League's terrain that
          blocks their way: the data has no walls; 0 in P, the balance below).
  ult     R Subjugate (强权至上), `Targeting` on `EnemyChampion` within r_range: on r_rel he drains the champion - at once
          r_pct0% of its maximum health as true damage and he heals r_heal + r_heal_r% AD, then r_pct% and the heal every
          r_p ticks for r_t ticks; it has r_arm% less defence and magic resistance for r_t + r_keep ticks, he r_arm% more.
  combos  E -> Q: the pillar holding an enemy champion takes `q_cd` off; the controller bites the first champion in
          reach (`q_go`, q_go_t ticks). Q -> W: the bite on a champion with W ready raises `w_go`; the controller freezes
          the ground once the bite's animation is over (`busy`). R -> Q + E: the drain takes `q_cd` off (`q_go`) and
          raises a pillar on the target (not E's cooldown). Domain -> King's Tribute: the kill heal doubles under `w_on`.
  controller An AddCasted pulse on him every ctl_p ticks (league_sejuani's, hung by his attack and the ult, only for
          Trundle himself: `own`): the combos' casts.
The add-on copy (--native, addons/league_trundle: every place the data is not League's): the passive league_trundle:troll
heals him for p_pct% of the maximum health of every enemy unit that dies within p_r of him, whoever killed it (the main
pack: the units he kills), and twice that on the domain; keeps the domain on the ground where it froze (w_r round that
spot: the buff `w_on` holds only while he stands in it) and makes every heal on him there w_amp% bigger; makes the pillar
terrain (enemies pushed out of e_wall round it while it stands, no `Bind`); turns Chomp's sap into League's flat steal
(he gains q_flat% of the unit's attack, it loses half that); and Subjugate into League's (r_steal% of the champion's own
defence and magic resistance moved to him, the drain as magic damage, every point drained healing him).
Timings: drafts until the frames exist (tools/art/rig_trundle.py retimes them).
Numbers: League 16.21 read into the jungle fighter range (league_sejuani, league_warwick, league_volibear), balanced on the
classic-SDK simulations (kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/tr_sim, 2026-10-25;
league_warwick the control: +0.57 / +0.52 on seeds 1-8 / 9-16): the draft (hp 1150, attack 88, pillar 40% slow 6 s over
20000 + a 30-tick hold every 480) +9.46 (1-8) - its slow field stacked two 40% slows (a 20-tick buff every 10 ticks,
fixed: one 10-tick buff); with one slow +5.29 (1-4); the pillar at 25% for 4 s over 16000 every 540 with a 20-tick hold
+3.02, with hp 1080 / attack 84 +1.68 (1-4); hp 1080, attack 82, defence 34, R 25% and the heals cut (tribute 12 + 8%,
R 20 + 10%, domain regen 6) +1.60 (1-8), without the hold +0.05, a 10-tick hold +0.12; P (no hold, hp 1120) +0.70 /
+0.51 (1-8 / 9-16; mean +0.61). The add-on's rules cannot run in that engine (Native effects dropped).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_trundle.data_champion")
ID = "league_trundle"
FX = "asset/league/effects/league_trundle_fx"
BIG = "asset/league/effects/league_trundle_big"

# League's Trundle (16.21): 650 +110 hp, 68 AD +4, 37 armour +3.9, 32 mr +2.05, 350 move, 175 range, 0.67 attack speed.
# Passive: a unit dying near him heals 2-7% of its max hp. Q: 20-100 + 15-35% AD, a 75% slow, he gains 20-40 AD and the
# target loses half for 4 s, cd 3.5. W: a 750 domain 8 s, +30-70% attack speed, +20% move speed, +25% healing, cd 18-14.
# E: a pillar 6 s, impassable, slows 34-50% round it, cd 21-15. R: 20-35% max hp magic (half at once, half over 4 s),
# steals 40% armour / mr (held 4 s, then decays), he heals what he drains, cd 120-80.
P = {
    # stats (base fighters: attack 90 +12, hp 1000 +100, defence 35 +8; league_warwick, league_volibear)
    "hp": 1120, "hp_g": 110, "atk": 82, "atk_g": 13, "apw": 10, "apw_g": 5, "def": 34, "def_g": 9, "mr": 28, "mr_g": 4,
    "ms": 1000, "ms_g": 11, "regen": 2, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 72, "a_hit": 11,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: King's Tribute (the kill heal)
    "p_heal": 12, "p_heal_r": 8,
    # passive: W Frozen Domain
    "w_cd": 720, "w_t": 480, "w_dur": 14, "w_as": 50, "w_ms": 15, "w_regen": 6,
    # skill: Q Chomp
    "q_cd": 300, "q_range": 25000, "q_dur": 28, "q_hit": 12, "q_dmg": 40, "q_ratio": 130, "q_slow": 60, "q_slow_t": 20,
    "q_t": 240, "q_sap": 15, "q_gain": 20, "q_go_t": 120,
    # skill2: E Pillar of Ice
    "e_cd": 540, "e_range": 50000, "e_dur": 24, "e_rel": 10, "e_r": 16000, "e_t": 240, "e_slow": 25, "e_root": 0,
    # ult: R Subjugate
    "r_cd": 4800, "r_range": 40000, "r_dur": 30, "r_rel": 14, "r_pct0": 10, "r_pct": 3, "r_p": 60, "r_t": 240,
    "r_heal": 20, "r_heal_r": 10, "r_arm": 25, "r_keep": 240, "r_go_t": 120,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_trundle (League's rules the data cannot read, see the docstring); its parameters
    "native": 0, "p_pct": 5, "p_r": 50000, "w_r": 24000, "w_amp": 25, "e_wall": 9000, "q_flat": 20, "r_steal": 40,
}


# the numbers addons/league_trundle reads from passive.params (its Params, in this order)
NATIVE_KEYS = ("p_pct", "p_r", "w_as", "w_ms", "w_regen", "w_r", "w_amp", "e_t", "e_wall", "q_t", "q_flat", "r_steal",
               "r_pct0", "r_pct", "r_p", "r_t", "r_keep")


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


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


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


def lob(name, travel, radius, target, effects, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def zone(name, radius, target, effects, delay=1):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


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

    # ------------------------------------------------------------------ passive: King's Tribute (the kill trigger)
    # in a hit's twin on the unit: `kl` on him, cleared a tick later by a casted on the unit while it lives; a dead unit
    # leaves it, and the check 4 ticks on (queued on him and the unit: the first run takes the flag) heals him
    tribute = combine(*rm("kl"), view("p_heal"), sfx("p_heal"),
                      sw("w_on", heal(p["p_heal"] * 2, p["p_heal_r"] * 2), heal(p["p_heal"], p["p_heal_r"])))

    def kill_check(name):
        if native:   # the add-on heals for every enemy unit dying near him, whoever killed it
            return None
        return homing(name, "EnemyWithoutTower", [flag("kl", 6), casted(3, 1, *rm("kl")),
                                                 {"type": "WithSelf", "effects": [delayed(4, sw("kl", tribute))]}])

    # ------------------------------------------------------------------ passive: W Frozen Domain (on the controller)
    def w_cast():
        # the add-on keeps the domain on the ground: `w_on` only marks it, its 2-tick `w_in` holds the stats inside
        dom = {} if native else dict(attack_speed_mult=p["w_as"], move_speed_mult=p["w_ms"], hp_regen=p["w_regen"])
        return combine(*rm("w_go"), refresh("w_cd", p["w_cd"]), refresh("w_on", p["w_t"], **dom),
                       anim("w", p["w_dur"]), sfx("w"), voice("vo_w", p),
                       on_me(view("w_domain"), view("w_hop")))

    # ------------------------------------------------------------------ Q Chomp
    def q_cast():
        # Q -> W: the bite on a champion with W ready (`w_go`); the controller freezes the ground after the bite (`busy`)
        champ = homing("q_tw", "EnemyChampion", [sw("w_cd", NONE, refresh("w_go", p["q_dur"] + 30))])
        sap = buff("q_mark", 3) if native else buff("q_sap", p["q_t"], attack_mult=-p["q_sap"])
        bite = combine(sfx("q_hit"), None if native else refresh("q_ad", p["q_t"], attack_mult=p["q_gain"]),
                       homing("q_bite", "EnemyWithoutTower", [
                           attack(p["q_dmg"], p["q_ratio"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                           sap, view("q_hit"), tsfx("q_hit")]),
                       champ, kill_check("q_kl"))
        return combine(refresh("q_cd", p["q_cd"]), refresh("busy", p["q_dur"]), *rm("q_go"), anim("skill", p["q_dur"]),
                       sfx("q"), voice("vo_q", p), delayed(p["q_hit"] - 1, alive(bite)))

    # ------------------------------------------------------------------ E Pillar of Ice
    def pillar(combo):
        """The pillar on the unit in hand: the champions at it held (E -> Q when `combo`), a slowing field round it."""
        # the add-on makes the pillar terrain instead of the hold: `e_at` on the champions there shows it where
        hold = [buff("e_at", 3) if native else {"type": "Bind", "duration": p["e_root"]} if p["e_root"] else None,
                view("e_hit"), tsfx("e_hit")]
        hold = [h for h in hold if h is not None]
        if combo:
            hold.append(sw("own", combine(*rm("q_cd"), refresh("q_go", p["q_go_t"]))))
        # the add-on plays the pillar's picture where its pillar stands (behind the champion), not here
        return lob("e_drop", 1, 1000, "EnemyWithoutTower", [], end=[
            *([] if native else [view("e_pillar")]), sfx("e_rise"),
            zone("e_hold", 9000, "EnemyChampion", hold),
            field("e_cold", p["e_r"], p["e_t"], 10, [buff("e_slow", 10, move_speed_mult=-p["e_slow"])], first=1)])

    def e_cast():
        return combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                       delayed(p["e_rel"] - 1, alive(homing("e_aim", "EnemyChampion", [pillar(True)]))))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not (league_zac):
    # his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Trundle
    # himself (`own`, a flag his attack raises: league_sylas's stolen ult hangs it too)
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        sw("w_go", sw("busy", NONE, sw("w_cd", combine(*rm("w_go")), w_cast()))),
        sw("q_go", sw("busy", NONE, sw("q_cd", NONE, pick(p["q_range"], "EnemyChampion", q_cast())))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Subjugate
    if native:   # the add-on: League's steal (r_steal% of the champion's own stats) and drain (magic, heals as much)
        drain = [buff("r_drain", p["r_t"] + p["r_keep"]), view("r_hit"), tsfx("r_hit")]
        mine = None
    else:
        tick_ = [pct(p["r_pct"]), heal(p["r_heal"], p["r_heal_r"]), view("r_tick")]
        drain = [pct(p["r_pct0"]), heal(p["r_heal"], p["r_heal_r"]), view("r_hit"), tsfx("r_hit"),
                 buff("r_sap", p["r_t"] + p["r_keep"], defence_mult=-p["r_arm"], magic_resistance_mult=-p["r_arm"]),
                 casted(p["r_t"], p["r_p"], *tick_, kind="Fire")]
        mine = refresh("r_gain", p["r_t"] + p["r_keep"], defence_mult=p["r_arm"], magic_resistance_mult=p["r_arm"])
    # R -> Q + E: Q ready and a pillar on the champion (Trundle's own: `own`)
    drain += [casted(p["r_t"], 60, view("r_chain")), sw("own", combine(*rm("q_cd"), refresh("q_go", p["r_go_t"]))),
              pillar(False)]
    r_cast = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                     delayed(p["r_rel"] - 1, alive(mine, homing("r_grab", "EnemyChampion", drain))))

    # ------------------------------------------------------------------ attack
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   kill_check("a_kl"))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("own", NONE, flag("own", None)), hang,
                              delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(150, 100), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"]), sw("q_cd", NONE, q_cast())), key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(decoy(40, 60), sw("e_cd", NONE, e_cast())), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_e = [E("a_hit"), E("p_heal"), E("q_hit"), E("w_hop", FX, -1, False), E("w_domain", BIG, -1, False),
               E("e_pillar", BIG, 1, False), E("e_hit"), E("r_hit"), E("r_tick"), E("r_chain")]
    views_b = [B_("q_slow", FX, -1, "slow"), B_("e_slow", FX, -1, "slow"),
               B_("q_take" if native else "q_ad", FX, 3, "q_buff")]
    if not native:   # the domain under him while it lasts (it follows him)
        views_b.insert(0, B_("w_on", FX, -1, "w_aura"))
    else:            # the add-on plays the frozen field where it froze, a second at a time (w_field), and the pillar
        views_e.append(E("w_field", FX, -1, False))
    if native:
        views_b += [B_("q_lose", FX, 3, "q_sap"), B_("r_drain", FX, 3, "r_sap")]
    else:
        views_b += [B_("q_sap", FX, 3, "q_sap"), B_("r_sap", FX, 3, "r_sap")]
    extra = {}
    if native:   # addons/league_trundle: the League rules the data cannot read
        extra["passive"] = {"passive_ref": "league_trundle:troll",
                            "params": {k: p[k] for k in NATIVE_KEYS}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0,
                 "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": p["regen_g"], "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
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
