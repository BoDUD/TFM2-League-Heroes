"""Build league_yorick.data_champion (top, Melee fighter-tank, AD: Yorick, the Shepherd of Souls) from the parameters P.

    python tools/kit/build_yorick.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-25: TOP, layout A - Q / E / R, Dark Procession (W) folded into the passive; combos all
four: E's mark -> the walkers pounce and Q is ready, W's cage -> E at once, R's Maiden -> Q ready, Q's graves -> walkers).
TFM2 has three active slots for League's four buttons: Last Rites (Q) is `skill`, Mourning Mist (E) `skill2`, Eulogy of
the Isles (R) the `ult`. Q and E keep their cooldowns in flags (`q_cd`, `e_cd`; league_sejuani's) so the combos can cast
them; a slot cast while its flag is up does nothing (a 3-tick idle). Flags die with him: a respawned Yorick has Q and E
ready - and no graves.
Summons cannot walk or attack in data (champion-data "A summon that follows its target"): the Mist Walkers and the
Maiden ride on the unit they are raised on (league_malzahar's voidlings): an `AddCasted` on it bites every k_p ticks and
plays their pictures there; its death ends them.
  passive Shepherd of Souls (牧魂人): graves - Q on a champion digs one, Q on anything else every second time (League:
          a kill or a large monster; the data cannot read a kill on the spot). They are counted on him (hidden caster
          buffs g1..g3, g_t ticks each, league_darius's Hemorrhage). With g_n (3) graves his next Q raises the walkers
          (Awakening, League's Q2; his `awaken` tag instead of `skill`): k_n walkers on the target for k_t ticks, each
          bite k_dmg + k_ratio% AD.
          Dark Procession (暗灵缠身, W) folded in: the Awakening also raises the wall round the target - every enemy
          champion within w_r is caged (`Bind` w_root ticks; League's wall blocks movement, the data has no walls).
  attack  A shovel blow (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; while the Maiden stands (`r_on`)
          its champion twin adds r_pct% of the champion's maximum health as true damage (League: on her target only).
  skill   Q Last Rites (临终仪式), `Targeting` on `EnemyWithoutTower` in melee reach (q_range, `q_cd`): on q_hit a heavy
          blow q_dmg + q_ratio% AD and he heals q_heal + q_heal_r% AD; the grave as above.
  skill2  E Mourning Mist (哀伤之雾), `Targeting` on `EnemyWithoutTower` (e_range, `e_cd`): on e_rel a globule of mist is
          lobbed at the target (e_fly ticks); every enemy within e_r of where it lands takes e_dmg + e_ratio% AD +
          e_hp% of its maximum health, e_arm% less defence for e_t ticks (the mark) and e_slow% slower for e_slow_t.
  ult     R Eulogy of the Isles (海屿悼词), `Targeting` on `EnemyChampion` within r_range: on r_rel the Maiden rises on
          the champion with r_n walkers: she claws every r_p ticks for r_t ticks (r_dmg + r_ratio% AD), and while she
          stands his attacks on champions deal the bonus above.
  combos  E -> walkers + Q: the mist on an enemy champion makes the walkers he has raised (`k_on`) pounce on it (k_jmp +
          k_jmp_r% AD) and takes `q_cd` off; the controller strikes Q at the first champion in reach (`q_go`, q_go_t ticks).
          W -> E: the cage takes `e_cd` off and the controller throws the mist at a caged champion (`e_go`).
          R -> Q: the Maiden's rising takes `q_cd` off (`q_go` for r_go_t ticks), and while she stands Q comes back in
          q_cd_r ticks instead of q_cd. Q -> walkers: the graves above.
  controller An AddCasted pulse on him every ctl_p ticks (league_sejuani's, hung by his attack and the ult, only for
          Yorick himself: `own`): the combos' casts.
The add-on copy (--native, addons/league_yorick): the Q blow raises `q_win` on him (q_win ticks) - the add-on digs a
grave for every unit that dies to it (League: a kill or a champion) instead of the main pack's every second blow; the
ult puts `maiden` on her champion and his attacks a 3-tick `hit` on the champions they strike while she stands - the
add-on deals r_pct% of its maximum health as true damage to her own target only (the main pack: any champion).
Timings: frames by tools/art/rig_yorick.py (attack 500 ms, Q / the Awakening 500, E 433, R 567 ms).
Numbers: League 16.21 read into the top fighter range (league_kled, league_darius, league_illaoi), balanced on the
classic-SDK simulations (kd.py --lane 0 against fighter, executioner, knight, berserker, lancer and pole_warrior,
C:/t/yo_sim, 2026-10-25; league_gnar --native the control: +0.01 / +0.59 on seeds 1-8 / 9-16): the draft (hp 1080,
attack 90, Q 40 + 140% every 300, walkers 8 + 12%, E 60 + 60%, R 40%) +0.05 / -0.98; hp 1140, attack 94, defence 36, Q 55
every 270, walkers 10 + 14%, E 70 + 70%, R 50% +1.70 (1-16); P (hp 1100, attack 91, defence 35, Q 45 every 285, walkers
9 + 13%, E 65 + 65%, R 45%) +0.44 (1-16; league_kled +0.29).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_yorick.data_champion")
ID = "league_yorick"
FX = "asset/league/effects/league_yorick_fx"
BIG = "asset/league/effects/league_yorick_big"

# League's Yorick (16.21): 650 +114 hp, 62 AD +5, 36 armour +4.5, 32 mr +2.05, 340 move, 175 range, 0.625 attack speed.
# Passive: graves from Q (champion / large monster / kill), max 4; walkers bite 2-100 + 15% AD, chase marked targets.
# Q: next attack 30-130 + 40% AD, heals 12-40 + 4% missing hp, cd 6-4; Awakening raises the walkers. W: a ring of
# spirits 4 s, blocks enemies, cd 20-12. E: mist 70-210 + 40% AP (15% current hp), 20% armour cut and slow 4 s, the
# walkers run at the marked. R: the Maiden + 2-4 walkers, his attacks on her target +3-7% max hp, cd 160-100.
P = {
    # stats (base fighters: attack 90 +12, hp 1000 +100, defence 35 +8; league_kled 1040 / 100, league_darius)
    "hp": 1100, "hp_g": 100, "atk": 91, "atk_g": 14, "apw": 10, "apw_g": 5, "def": 35, "def_g": 8, "mr": 26, "mr_g": 4,
    "ms": 1000, "ms_g": 10, "regen": 2, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 80, "a_hit": 12,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: graves and the walkers
    "g_t": 1800, "g_n": 3, "k_n": 3, "k_t": 360, "k_p": 60, "k_dmg": 9, "k_ratio": 13,
    "k_jmp": 20, "k_jmp_r": 30,
    # passive: W Dark Procession (the cage)
    "w_r": 18000, "w_root": 60,
    # skill: Q Last Rites
    "q_cd": 285, "q_cd_r": 150, "q_range": 25000, "q_dur": 30, "q_hit": 14, "q_dmg": 45, "q_ratio": 140,
    "q_heal": 30, "q_heal_r": 20, "q_go_t": 120,
    # skill2: E Mourning Mist
    "e_cd": 540, "e_range": 55000, "e_dur": 26, "e_rel": 12, "e_fly": 16, "e_r": 15000, "e_dmg": 65, "e_ratio": 65,
    "e_hp": 4, "e_arm": 25, "e_t": 240, "e_slow": 30, "e_slow_t": 90, "e_go_t": 60,
    # ult: R Eulogy of the Isles
    "r_cd": 4800, "r_range": 40000, "r_dur": 34, "r_rel": 16, "r_t": 600, "r_p": 60, "r_dmg": 20, "r_ratio": 45,
    "r_n": 2, "r_pct": 3, "r_go_t": 120,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_yorick (League's rules the data cannot read): its passive league_yorick:shepherd
    # digs a grave for every unit Last Rites kills (the `q_win` flag on him) instead of every second Q, and deals the
    # Maiden's bonus (r_pct% max health as true damage) on her own target only (`maiden` on it, `hit` from his attack)
    "native": 0, "q_win": 4,
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


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": hp,
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
            "applied_effects": [T(e) for e in effects]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def lob(name, travel, radius, target, effects, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def zone(name, radius, target, effects, delay=1):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    ctl_p = p["ctl_p"]

    # ------------------------------------------------------------------ the walkers (on the unit in hand)
    def walkers(k):
        """k Mist Walkers on this unit for k_t ticks: one bite of all of them every k_p ticks, their pictures on it."""
        return combine(refresh("k_on", p["k_t"]), view("k_spawn"), tsfx("k_spawn"),
                       casted(p["k_t"], p["k_p"], attack(p["k_dmg"] * k, p["k_ratio"] * k), view("k_bite"),
                              tsfx("k_bite"), kind="Fire"),
                       casted(p["k_t"], 60, view("k_swarm")))

    # ------------------------------------------------------------------ passive: graves (g1..g3, counted on him)
    grave = combine(view("q_grave"), tsfx("q_grave"),
                    sw("g2", refresh("g3", p["g_t"]), sw("g1", refresh("g2", p["g_t"]), refresh("g1", p["g_t"]))))
    # W Dark Procession: a ring of spirits round the unit in hand; the champions in it are caged, and E comes back
    cage = lob("w_drop", 1, 1000, "EnemyWithoutTower", [], end=[
        view("w_wall"), sfx("w_wall"),
        zone("w_cage", p["w_r"], "EnemyChampion", [{"type": "Bind", "duration": p["w_root"]}, view("w_hit"),
                                                     tsfx("w_hit"), *rm("e_cd"), refresh("e_go", p["e_go_t"])])])
    awaken = sw("g3", combine(*rm("g1", "g2", "g3"), sfx("q_awake"),
                              homing("q_raise", "EnemyWithoutTower", [walkers(p["k_n"]), cage])))

    # ------------------------------------------------------------------ Q Last Rites
    def q_cast():
        # a grave: on a champion always (its twin), on anything else every second Q (`q_half`); the check waits a tick
        # for the twin's `q_ch`
        champ = homing("q_tw", "EnemyChampion", [refresh("q_ch", 3), grave])
        other = sw("q_ch", NONE, sw("q_half", combine(*rm("q_half"), pick(p["q_range"], "EnemyWithoutTower", grave)),
                                   flag("q_half", None)))
        if p["native"]:      # the add-on digs a grave for each unit the blow kills (League), not every second blow
            other = refresh("q_win", p["q_win"])
        blow = combine(sfx("q_hit"), heal(p["q_heal"], p["q_heal_r"]),
                       homing("q_blow", "EnemyWithoutTower", [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"),
                                                              tsfx("q_hit")]),
                       awaken, champ, delayed(2, alive(other)))
        return combine(sw("r_on", refresh("q_cd", p["q_cd_r"]), refresh("q_cd", p["q_cd"])), *rm("q_go", "q_ch"),
                       sw("g3", anim("awaken", p["q_dur"]), anim("skill", p["q_dur"])), sfx("q"), voice("vo_q", p),
                       delayed(p["q_hit"] - 1, alive(blow)))

    # ------------------------------------------------------------------ E Mourning Mist
    def e_cast():
        # E -> walkers + Q: on a champion the walkers he has raised pounce on it, and Q is ready (`q_go`)
        champ = homing("e_tw", "EnemyChampion", [sw("e_lk", NONE, combine(
            flag("e_lk", p["e_fly"] + 4), sw("k_on", combine(attack(p["k_jmp"], p["k_jmp_r"]), view("k_leap"),
                                                            tsfx("k_leap"))),
            *rm("q_cd"), refresh("q_go", p["q_go_t"])))], speed=4000)
        hit = [attack(p["e_dmg"], p["e_ratio"], p["e_hp"]), buff("e_mark", p["e_t"], defence_mult=-p["e_arm"]),
               buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"), tsfx("e_hit")]
        mist = lob("e_mist", p["e_fly"], p["e_r"], "EnemyWithoutTower", hit, end=[view("e_cloud"), sfx("e_land")])
        return combine(refresh("e_cd", p["e_cd"]), *rm("e_go", "e_lk"), anim("skill2", p["e_dur"]), sfx("e"),
                       voice("vo_e", p), delayed(p["e_rel"] - 1, alive(mist, champ)))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not (league_zac):
    # his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Yorick
    # himself (`own`, a flag his attack raises: league_sylas's stolen ult hangs it too)
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        sw("q_go", sw("q_cd", NONE, pick(p["q_range"], "EnemyChampion", q_cast()))),
        sw("e_go", sw("e_cd", NONE, pick(p["e_range"], "EnemyChampion", e_cast()))))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Eulogy of the Isles
    maiden = [view("r_spawn"), tsfx("r_spawn"), walkers(p["r_n"]),
              casted(p["r_t"], p["r_p"], attack(p["r_dmg"], p["r_ratio"]), view("r_claw"), tsfx("r_claw"), kind="Fire"),
              casted(p["r_t"], 60, view("r_maiden")),
              sw("own", combine(*rm("q_cd"), refresh("q_go", p["r_go_t"])))]
    if p["native"]:
        maiden.append(buff("maiden", p["r_t"]))
    r_cast = combine(refresh("r_on", p["r_t"]), anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                     delayed(p["r_rel"] - 1, alive(homing("r_rise", "EnemyChampion", maiden))))

    # ------------------------------------------------------------------ attack
    bonus = [buff("hit", 3)] if p["native"] else [pct(p["r_pct"]), view("r_mark")]   # the add-on: on her target only
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   sw("r_on", homing("a_tw", "EnemyChampion", bonus)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("own", NONE, flag("own", None)), hang,
                              delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"] * 4, p["r_ratio"] * 4), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"]), sw("q_cd", NONE, q_cast())), key="skill")
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"]), sw("e_cd", NONE, e_cast())), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("e_mist")]
    views_e = [E("a_hit"), E("q_hit"), E("q_grave", FX, -1, False), E("k_spawn", FX, -1), E("k_swarm", FX, -1),
               E("k_bite"), E("k_leap"), E("w_wall", BIG, -1, False), E("w_hit"), E("e_hit"),
               E("e_cloud", BIG, -1, False), E("r_spawn", BIG, -1), E("r_maiden", BIG, -1), E("r_claw"), E("r_mark")]
    views_b = [B_("e_mark", FX, -1, "e_mark"), B_("e_slow", FX, -1, "slow")]
    extra = {}
    if p["native"]:   # addons/league_yorick: the League rules the data cannot read
        extra["passive"] = {"passive_ref": "league_yorick:shepherd",
                            "params": {k: p[k] for k in ("r_pct", "g_t")}}
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
