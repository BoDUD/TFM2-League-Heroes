"""Build league_locke.data_champion (mid, Assassin, melee AP: Locke, the Ashen Exorcist) from the parameters P.

    python tools/kit/build_locke.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-26: MID, layout A - Q / E / R, Soul Ignition (W) folded into the passive; combos all
four: Q's nails on a champion -> E ready, E landing by a champion -> W at once, a takedown -> E reset (and a seal
gives the artifact back), R's mark -> Q ready).
TFM2 has three active slots for League's four buttons: Ritual Nails (Q) is `skill`, Ashen Pursuit (E) `skill2`,
Purgatory (R) the `ult`. Q and E keep their cooldowns in flags (`q_cd`, `e_cd`; league_trundle's) so the combos can
cast them; a slot cast while its flag is up does nothing (a 3-tick idle). Flags die with him: a respawned Locke has Q,
E and W ready.
  passive Silver Stake (圣银穿心): every attack adds p_dmg + p_ap% AP magic damage (League: more against missing
          health - the data reads no current health; the add-on does).
          Soul Ignition (灵焰仪式, W) folded in: E landing next to an enemy champion ignites it (once every w_cd ticks):
          for w_t ticks w_as% attack speed and w_ms% move speed fading in three steps, w_cost% of his maximum health
          as true damage every second (a `Fire` on him: the soul burning), and at the end a heal of w_heal + w_heal_ap%
          AP (League: back what he lost; the data cannot count it). His W look (the B colours) is the add-on's: it
          swaps his frames for the `w_` ones while `w_on` lasts.
  attack  A nail stab (physical 100% AD, the passive's magic on top) on `Enemy` at atk_st. On a champion it pops the
          nails his Q left (League: the marks on that enemy; here the caster's own count, league_diana's Moonlight):
          q_pop + q_pop_ap% AP magic damage a nail, x (100 + q_two)% for two, x (100 + q_three)% for three.
          After E the next attack is the pursuit: he dashes through the target (`RushMoveToBack`, the `dash` tag
          e_dash_t ticks), e_dash + e_dash_ap% AP magic damage to it.
  skill   Q Ritual Nails (伏魔三钉), `Targeting` on `EnemyWithoutTower` (q_range, `q_cd`): three nails q_gap ticks apart
          (homing), each q_dmg + q_ap% AP magic damage and a q_slow% slow for q_slow_t (three hits stack it); every
          nail on a champion adds one to the count (n1 -> n2 -> n3, q_mark_t ticks) and the first one readies E; the
          mark over the champion's head shows while he holds the count (a `Bleed` casted on it, a round of the
          picture every q_mark_p ticks), so it goes when his stab pops the nails.
  skill2  E Ashen Pursuit (灰猎无影), `Targeting` on e_tgt (e_range, `e_cd`): he blinks onto the champion
          (`Teleport`), e_dmg + e_ap% AP magic damage round him (e_r) on arrival, and his next attack within e_next
          ticks is the pursuit (above). With W ready the soul ignites at once.
  ult     R Purgatory (万魔狱), `Targeting` on `EnemyChampionRecentlyAttacked` within r_range: he swings the case and
          throws it at the champion's spot (a lob of r_travel ticks): r_dmg + r_ap% AP magic damage round it (r_r), a
          r_slow% slow fading over r_slow_t, and every champion there is marked for r_t ticks: every r_p ticks a mark
          takes the threshold T (r_ex + r_ex_ap% AP, + r_ex_step a seal held) as true damage and heals it back a tick
          later (league_pyke R): a champion below T dies - League's execute. A takedown while the marks last seals one
          (`r_s1`..`r_s3`, at most three, for as long as he lives - League's are for the game: the add-on keeps them):
          the threshold grows and the ult's cooldown is capped at r_cap% of the cooltime (League: the artifact picked
          up).
  combos  Q -> E: the first nail on a champion takes `e_cd` off and raises `e_go`; the controller blinks onto the first
          champion within e_range. E -> W: the arrival next to a champion with W ready raises `w_go`. Takedown -> E: the
          window (league_viego's) takes `e_cd` off. R -> Q: the mark takes `q_cd` off and raises `q_go`.
  controller An AddCasted pulse on him every ctl_p ticks (league_trundle's, hung by his attack and the ult, only for
          Locke himself: `own`): the combos' casts.
The add-on copy (--native, addons/league_locke): the passive league_locke:exorcist adds the missing-health part of Silver
Stake (p_miss% of the target's missing health), makes W cost w_cost% of his current health and heal back w_back% of
what it took, executes marked champions under r_exec% of their maximum health (+ r_exec_step a seal) for real, keeps
the seals for the whole game and drops the artifact where a champion was sealed for him to pick up; and swaps his
frames for the W look.
Timings: drafts until the frames exist (tools/art/rig_locke.py retimes them).
Numbers: League 16.21 read into the mid assassin range (league_katarina, league_talon), balanced on the classic-SDK
simulations (kd.py --lane 2 against the five base mages, C:/t/lk_sim, 2026-10-26; league_katarina the control: +1.73 /
+1.64 on seeds 1-8 / 9-16): the draft (hp 980, attack 100, an execute check every 20 ticks at 150 + 50% AP) +3.36 -
its execute pulses also counted their heal-back as his healing; checks every 30 ticks at 100 + 40% AP +3.27; Q / E
damage cut +3.04; hp 940 and W's heal 40 + 20% +2.08 (without the execute at all +0.74: it is worth ~1.3 kills); P =
hp 900, attack 92, W's heal 20 + 10% and attack speed 35%: +1.60 / +1.62 (R at 160 + 60% fell to +0.75); the shipped build
(the frames in: the pursuit's dash animation, the nail mark's casted) +1.11 / +1.76, within a standard error of it. The
add-on's rules cannot run in that engine (Native effects dropped).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_locke.data_champion")
ID = "league_locke"
FX = "asset/league/effects/league_locke_fx"
BIG = "asset/league/effects/league_locke_big"

# League's Locke (16.21): 620 +109 hp, 58 AD, 32 armour +4.2, 32 mr +2.05, 340 move, 125 range, 0.688 attack speed.
# Q: three nails (950), marks; attacks pop them (more for 2 and 3), cd 10-6. W: attack speed + decaying move speed,
# % current health true damage a second, heals back what he took, cd 18-14. E: a 425 blink, the next attack dashes,
# reset on takedowns, cd 10. R: an artifact (1000): damage, a decaying slow, marks; marked champions below the threshold
# are sealed (executed); picking it up adds threshold and refunds cooldown, cd 120-80.
P = {
    # stats (the pack's mid assassins: league_katarina hp 1020 +92, atk 112 +13, ap 40 +26, def 32 +8, mr 24 +4)
    "hp": 900, "hp_g": 92, "atk": 92, "atk_g": 12, "ap": 40, "ap_g": 24, "def": 30, "def_g": 8, "mr": 24, "mr_g": 4,
    "ms": 1100, "ms_g": 13,
    "atk_range": 23000, "atk_dur": 24, "atk_cd": 55, "atk_st": 8,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: Silver Stake (on-hit magic)
    "p_dmg": 15, "p_ap": 15,
    # passive: W Soul Ignition
    "w_cd": 960, "w_t": 240, "w_dur": 20, "w_as": 35, "w_ms": 40, "w_cost": 2, "w_heal": 20, "w_heal_ap": 10,
    # skill: Q Ritual Nails
    "q_cd": 480, "q_range": 50000, "q_dur": 30, "q_at": 8, "q_gap": 6, "q_speed": 6000, "q_y": -3000,
    "q_dmg": 35, "q_ap": 20, "q_slow": 15, "q_slow_t": 90, "q_mark_t": 240, "q_mark_p": 36,
    "q_pop": 25, "q_pop_ap": 12, "q_two": 25, "q_three": 50, "q_go_t": 120,
    # skill2: E Ashen Pursuit
    "e_cd": 600, "e_range": 45000, "e_tgt": "EnemyChampionRecentlyAttacked", "e_dur": 16, "e_at": 6, "e_r": 20000,
    "e_dmg": 50, "e_ap": 25, "e_next": 180, "e_dash": 55, "e_dash_ap": 30, "e_speed": 4000, "e_dash_t": 14,
    "e_go_t": 120,
    # the takedown window (league_viego's)
    "p_win": 180,
    # ult: R Purgatory
    "r_cd": 3600, "r_range": 50000, "r_dur": 30, "r_rel": 14, "r_travel": 18, "r_r": 25000, "r_dmg": 200, "r_ap": 80,
    "r_slow": 50, "r_slow_t": 90, "r_t": 240, "r_p": 30, "r_ex": 100, "r_ex_ap": 40, "r_ex_step": 40, "r_cap": 50,
    "r_go_t": 120,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_locke (League's rules the data cannot read, see the docstring); its parameters
    "native": 0, "p_miss": 8, "w_back": 70, "r_exec": 15, "r_exec_step": 3, "r_drop": 300, "pick_r": 9000,
}


# the numbers addons/league_locke reads from passive.params (its Params, in this order)
NATIVE_KEYS = ("p_miss", "w_t", "w_cost", "w_back", "r_t", "r_exec", "r_exec_step", "r_drop", "pick_r", "r_cap", "p_win")


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


def magic(dmg, ap):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap, "hp_ratio": 0, "can_crit": False}


def true_ap(dmg, ap):
    """True damage in AP terms (champion-data section 4): an ApAttack through a 1-tick 100% magic penetration."""
    return combine(flag("pen", 1, magic_resistance_penetration=100), magic(dmg, ap))


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


def heal(amount, ap, kind="Caster"):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": kind}


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
    return combine(flag("x", 1), sw("x", combine(*rm("x")), magic(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects if e is not None]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period,
            "effects": [e for e in effects if e is not None]}


def lob(name, travel, target, end):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1000), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, target, effects, delay=1):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": flat(effect)}


def build(p):
    ctl_p = p["ctl_p"]
    native = p["native"]

    # ------------------------------------------------------------------ the takedown window (E reset, the seals)
    def seal():
        """A takedown while R's marks last: one more seal (at most three) and the ult's cooldown capped."""
        cap = {"ult_cooldown_mult": round(100 * 100 / p["r_cap"]) - 100}
        more = sw("r_s2", sw("r_s3", NONE, flag("r_s3", None)), sw("r_s1", flag("r_s2", None), flag("r_s1", None)))
        return sw("r_live", combine(None if native else more, refresh("r_ref", 3, **cap), cview("r_seal"),
                                    sfx("r_seal")))

    def reset():
        """A takedown: E ready (League: Ashen Pursuit's cooldown reset); one per window."""
        return combine(refresh("p_lock", p["p_win"]), refresh("p_alive", p["p_win"]), *rm("e_cd"), cview("p_reset"),
                       sfx("reset"), seal())

    watch = sw("p_alive", NONE, sw("p_lock", NONE, reset()))

    def track():
        """On a champion he hit: keeps p_alive up while it lives; a watcher on him sees it lapse = a takedown (the
        add-on reads kills and assists natively instead)."""
        if native:
            return None
        return combine(casted(p["p_win"], 1, refresh("p_alive", 2)),
                       on_me(refresh("p_alive", 3), casted(p["p_win"] - 2, 1, watch)))

    # ------------------------------------------------------------------ passive: W Soul Ignition (on the controller)
    third = p["w_t"] // 3

    def w_cast():
        # the add-on burns his current health and heals back what it took; the data: max health, a fixed heal
        cost = None if native else casted(p["w_t"], 60, pct(p["w_cost"]), kind="Fire")
        back = None if native else delayed(p["w_t"], alive(on_me(heal(p["w_heal"], p["w_heal_ap"]), view("w_end"))))
        return combine(*rm("w_go"), refresh("w_cd", p["w_cd"]), refresh("w_on", p["w_t"], attack_speed_mult=p["w_as"]),
                       refresh("w_ms", third, move_speed_mult=p["w_ms"]),
                       delayed(third, refresh("w_ms", third, move_speed_mult=p["w_ms"] * 2 // 3)),
                       delayed(2 * third, refresh("w_ms", third, move_speed_mult=p["w_ms"] // 3)),
                       anim("w", p["w_dur"]), refresh("busy", p["w_dur"]), sfx("w"), voice("vo_w", p),
                       on_me(view("w_ign"), cost), back)

    # ------------------------------------------------------------------ the nails' count (on him) and the pop
    def count():
        """One more nail on a champion (n1 -> n2 -> n3, each q_mark_t ticks, exclusive)."""
        t = p["q_mark_t"]
        return sw("n2", combine(*rm("n2"), refresh("n3", t)),
                  sw("n1", combine(*rm("n1"), refresh("n2", t)), sw("n3", refresh("n3", t), refresh("n1", t))))

    def pop():
        """The attack on a champion spends the count: magic damage a nail, more for two and three."""
        one = (p["q_pop"], p["q_pop_ap"])
        hit = lambda k, bonus: combine(*rm("n1", "n2", "n3"), magic(one[0] * k * (100 + bonus) // 100,
                                                                    one[1] * k * (100 + bonus) // 100),
                                       view("q_pop"), tsfx("q_pop"))
        return sw("n3", hit(3, p["q_three"]), sw("n2", hit(2, p["q_two"]), sw("n1", hit(1, 0))))

    # ------------------------------------------------------------------ Q Ritual Nails
    def q_cast():
        def nail(k):
            # the mark over the head shows while he holds the count (a casted on the champion reads his flags every
            # q_mark_p ticks and plays one round of the mark): his stab pops the nails and the mark goes with them -
            # a buff's picture would stay its whole time (the data cannot take a buff off another unit); the plain
            # q_mark buff stays for the add-on (who he touched)
            seen = sw("n1", view("q_mark_v"), sw("n2", view("q_mark_v"), sw("n3", view("q_mark_v"))))
            champ = homing(f"q_tw{k}", "EnemyChampion",
                           [count(), buff("q_mark", p["q_mark_t"]), track(),
                            casted(p["q_mark_t"], p["q_mark_p"], seen, kind="Bleed") if k == 0 else None,
                            # Q -> E: the first nail on a champion readies E (Locke's own: `own`)
                            sw("own", combine(*rm("e_cd"), refresh("e_go", p["e_go_t"]))) if k == 0 else None],
                           speed=p["q_speed"], y=p["q_y"])
            hit = homing("q_nail", "EnemyWithoutTower", [
                magic(p["q_dmg"], p["q_ap"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                view("q_hit"), tsfx("q_hit")], speed=p["q_speed"], y=p["q_y"])
            return delayed(p["q_at"] - 1 + k * p["q_gap"], alive(sfx("q_throw"), hit, champ))
        return combine(refresh("q_cd", p["q_cd"]), refresh("busy", p["q_dur"]), *rm("q_go"), anim("skill", p["q_dur"]),
                       voice("vo_q", p), nail(0), nail(1), nail(2))

    # ------------------------------------------------------------------ E Ashen Pursuit
    def e_cast():
        """On the champion in hand: the blink, the arrival burst, the next attack armed, W at once when ready."""
        arrive = combine(around(p["e_r"], "EnemyWithoutTower", magic(p["e_dmg"], p["e_ap"]), view("e_hit")),
                         around(p["e_r"], "EnemyChampion", track(), sw("w_cd", NONE, refresh("w_go", 30))))
        return combine(refresh("e_cd", p["e_cd"]), refresh("busy", p["e_dur"]), *rm("e_go"), cview("e_out"),
                       sfx("e_blink"), voice("vo_e", p), {"type": "Teleport"},
                       on_me(cview("e_in"), anim("skill2", p["e_dur"]), refresh("e_next", p["e_next"]),
                             delayed(p["e_at"] - 1, alive(arrive))))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not (league_zac):
    # his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Locke
    # himself (`own`, a flag his attack raises: league_sylas's stolen ult hangs it too)
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        sw("w_go", sw("busy", NONE, sw("w_cd", combine(*rm("w_go")), w_cast()))),
        sw("e_go", sw("busy", NONE, sw("e_cd", NONE, pick(p["e_range"], "EnemyChampion", e_cast())))),
        sw("q_go", sw("busy", NONE, sw("q_cd", NONE, pick(p["q_range"], "EnemyChampion", q_cast())))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Purgatory
    def execute(k):
        """One check of a mark: the threshold as true damage, healed back a tick later (league_pyke R)."""
        t, t_ap = p["r_ex"] + k * p["r_ex_step"], p["r_ex_ap"]
        return combine(true_ap(t, t_ap), view("r_tick"), delayed(1, heal(t, t_ap, "Any")))

    if native:   # the add-on executes under r_exec% of maximum health and keeps the seals
        check = None
    else:
        check = sw("r_s3", execute(3), sw("r_s2", execute(2), sw("r_s1", execute(1), execute(0))))
    mark = [buff("r_mark", p["r_t"]), track(), casted(p["r_t"], p["r_p"], check, kind="Bleed") if check else None,
            # R -> Q: Locke's own (`own`)
            sw("own", combine(*rm("q_cd"), refresh("q_go", p["r_go_t"])))]
    third_r = p["r_slow_t"] // 3
    slow = [buff("r_slow", third_r, move_speed_mult=-p["r_slow"]),
            delayed(third_r, buff("r_slow", third_r, move_speed_mult=-p["r_slow"] * 2 // 3)),
            delayed(2 * third_r, buff("r_slow", third_r, move_speed_mult=-p["r_slow"] // 3))]
    land = [view("r_land"), sfx("r_land"),
            zone("r_blast", p["r_r"], "EnemyWithoutTower", [magic(p["r_dmg"], p["r_ap"]), view("r_hit"), tsfx("r_hit"),
                                                             *slow]),
            zone("r_seal_z", p["r_r"], "EnemyChampion", mark)]
    r_cast = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p), refresh("r_live", p["r_rel"] + p["r_travel"]
                                                                                  + p["r_t"] + p["p_win"]),
                     delayed(p["r_rel"] - 1, alive(sfx("r_throw"), lob("r_case", p["r_travel"], "EnemyChampion",
                                                                       land))))

    # ------------------------------------------------------------------ attack
    stake = magic(p["p_dmg"], p["p_ap"])
    # the add-on adds the missing-health part of Silver Stake on the unit marked `p_hit`
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), stake, buff("p_hit", 3) if native else None,
                                                        view("a_hit"), tsfx("a_hit")]),
                   homing("a_tw", "EnemyChampion", [pop(), track()]))
    # the pursuit: after E the next attack dashes through the target (League: to it, hitting all on the way)
    pursuit = combine(*rm("e_next"), anim("dash", p["e_dash_t"]), cview("e_dash"), sfx("e_dash"),
                      {"type": "RushMoveToBack", "speed": p["e_speed"],
                       "applied_effects": [magic(p["e_dash"], p["e_dash_ap"]), view("e_hit")]})
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("own", NONE, flag("own", None)), hang,
                              delayed(p["atk_st"] - 1, alive(sw("e_next", pursuit), blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(decoy(p["r_dmg"], p["r_ap"]), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"] * 3, p["q_ap"] * 3), sw("q_cd", NONE, q_cast())), key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", p["e_tgt"],
                    combine(decoy(p["e_dmg"], p["e_ap"]), sw("e_cd", NONE, e_cast())), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [B_("q_nail", FX, 2), B_("r_case", FX, 2)]
    views_e = [E("a_hit"), E("q_hit"), {"type": "Animation", "name": n("q_mark_v"), "anim": FX, "tag": "q_mark", "z": 3,
                                         "is_follow": True}, E("q_pop"), E("e_out", FX, 2, False), E("e_in", FX, 2, False), E("e_hit"),
               E("e_dash", FX, 2, False), E("w_ign"), E("w_end"), E("r_land", BIG, 1, False), E("r_hit"),
               E("r_tick"), E("r_seal"), E("p_reset")]
    views_b = [B_("q_slow", FX, -1, "slow"), B_("r_slow", FX, -1, "slow"), B_("r_mark", FX, 3),
               B_("w_on", FX, -1, "w_aura")]
    extra = {}
    if native:   # addons/league_locke: the League rules the data cannot read
        extra["passive"] = {"passive_ref": "league_locke:exorcist", "params": {k: p[k] for k in NATIVE_KEYS}}
    return {
        "id": ID, "category": "Assassin", "tags": ["AP", "Magic", "Melee"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
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
        p[k] = v if isinstance(p[k], str) else type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
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
