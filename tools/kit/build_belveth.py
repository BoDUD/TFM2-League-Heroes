"""Build league_belveth.data_champion (jungle, Melee fighter, AD: Bel'Veth, the Empress of the Void) from the parameters P.

    python tools/kit/build_belveth.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-24: JUNGLE, layout A - Q / W / R, Royal Maelstrom (E) folded into the true form; combos
W's knock-up on a champion -> Q ready again, Q's landing -> W at once, an enemy champion's death -> she eats its coral,
the true form -> a stronger Q and faster attacks).
TFM2 has three active slots for League's four buttons: Void Surge (Q) is `skill`, Above and Below (W) `skill2`, Endless
Banquet (R) the `ult`. Q and W keep their cooldowns in flags (`q_cd`, `w_cd`; league_singed's E and W) so the combos can
cast them; a slot cast while its flag is up does nothing (a 3-tick idle). Flags die with her: a respawned Bel'Veth has Q
and W ready.
  passive Death in Lavender (溶烛化紫): every spell (Q, W, R, the maelstrom) gives p_as% attack speed for p_t ticks. A
          takedown of an enemy champion she damaged (within p_win ticks of her last hit on it, by anyone's hand:
          league_viego's window - the champion keeps a 2-tick flag `p_alive` up while it lives, the controller sees it
          lapse) adds a lavender stack: l_as% attack speed each, l_max at most; stacks are buffs and end with her death
          in the main pack. League's large-monster stacks need the add-on (data cannot tell a camp's big monster).
  attack  A slash of a wing-arm (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; she attacks fast for
          little (atk_cd, atk), League's attack-speed fighter.
  skill   Q Void Surge (虚空激流), `Targeting` on `EnemyWithoutTower` (q_range, `q_cd`): on q_go she dashes toward the
          target and through it (`RushTime`, q_speed x q_t, penetrate): q_dmg + q_ratio% AD to every enemy she passes.
  skill2  W Above and Below (上觐沉渊), `Targeting` on `EnemyWithoutTower` (w_range, `w_cd`): on w_rel her tail slams
          the ground in a line toward the target (a fast line, w_len long, w_rad wide, through everything): w_dmg +
          w_ratio% AD, knocked up w_up ticks, w_slow% slower for w_slow_t.
  ult     R Endless Banquet (万载豪筵), `Targeting` on `EnemyChampion` within r_range: on r_hit the void coral bursts round
          her (r_r): r_dmg + r_ratio% AD and r_slow% slower for r_slow_t; she takes her true form for r_t ticks:
          r_hp% more maximum health, r_rng more attack range, r_as% attack speed, r_ms% move speed.
          Royal Maelstrom (搠面皇锋, E) in the true form: with `e_cd` off and two enemy champions within e_near (the
          main pack's stand-in for "low health"; the add-on raises `low` from her real health) she roots herself in a
          storm of slashes for e_t ticks: e_dr% less damage taken, e_vamp% life steal, every e_p ticks a slash at an
          enemy champion her team hit lately (League: the lowest-health one) within e_r: e_dmg + e_ratio% AD.
  combos  W -> Q: a tail slam knocking up an enemy champion takes `q_cd` off and the controller dashes Q at it at once.
          Q -> W: a dash through an enemy champion has the controller slam W at the first champion in reach (once she
          has cast W herself this life, `w_lv`: no W before level 3). Coral: a takedown (above) in the true form renews
          it (r_t again); out of it, it cuts R's cooldown to c_cut% (`ult_cooldown_mult` for 2 ticks). True form: Q
          on q_cd_r instead of q_cd and q_t_r ticks of dash instead of q_t (farther), r_as% attack speed.
  controller An AddCasted pulse on her every ctl_p ticks (league_singed's, hung by her attack and the ult, only for
          Bel'Veth herself: `own`): the takedown watch, the combos' casts, the maelstrom's check.
Timings: drafts until the frames exist (tools/art/rig_belveth.py retimes them).
Numbers: League 16.21 read into the jungle range (league_reksai, league_graves), balanced on the classic-SDK
simulations (kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/bv_sim).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_belveth.data_champion")
ID = "league_belveth"
FX = "asset/league/effects/league_belveth_fx"
BIG = "asset/league/effects/league_belveth_big"

# League's Bel'Veth (16.21): 610 +105 hp, 60 AD +1.5, 32 armour +4.7, 32 mr, 340 move, 150 range, 0.85 attack speed
# (low AD, high attack speed; her bonus attack speed counts less). Q: 400 dash in four directions, 10-70 + 110% AD,
# cd 16-8 s a direction. W: 660 line, 70-210 + 100% bAD + 125% AP, knock-up 1-1.25 s, slow, cd 12-8; a champion hit
# cuts that Q direction's cooldown. E: 1.5 s channel, 70% less damage, 27% life steal, slashes at the lowest-health
# enemy, cd 24-12. R: true form 60 s (+range 75, +attack speed, +move speed, +max health); eating a champion's coral
# bursts round her (true damage + 25% missing health, slow). Passive: a lavender stack per champion / large-monster
# takedown; 40-?% attack speed after each spell for 2 attacks.
P = {
    # stats (base jungle fighters: league_reksai 1000 / 86, attack every 60 ticks; she attacks every atk_cd for less)
    "hp": 1000, "hp_g": 100, "atk": 70, "atk_g": 12, "def": 30, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000,
    "ms_g": 11, "regen": 2, "regen_g": 1,
    "atk_range": 24000, "atk_dur": 22, "atk_cd": 50, "a_hit": 9,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # passive: attack speed after a spell; lavender stacks from takedowns (the window)
    "p_as": 40, "p_t": 240, "p_win": 180, "l_as": 6, "l_max": 8,
    # skill: Q Void Surge
    "q_cd": 300, "q_cd_r": 150, "q_range": 40000, "q_dur": 18, "q_go": 3, "q_speed": 6000, "q_t": 7, "q_t_r": 10,
    "q_dmg": 50, "q_ratio": 110,
    # skill2: W Above and Below
    "w_cd": 600, "w_range": 45000, "w_dur": 30, "w_rel": 12, "w_len": 55000, "w_rad": 7000, "w_speed": 30000,
    "w_dmg": 60, "w_ratio": 100, "w_up": 50, "w_slow": 40, "w_slow_t": 90,
    # ult: R Endless Banquet
    "r_cd": 4800, "r_range": 35000, "r_dur": 40, "r_hit": 20, "r_r": 22000, "r_dmg": 100, "r_ratio": 80,
    "r_slow": 40, "r_slow_t": 90, "r_t": 900, "r_hp": 20, "r_rng": 6000, "r_as": 40, "r_ms": 15,
    # the coral: R's cooldown cut on a takedown out of the true form (ult_cooldown_mult for 2 ticks: 100 / (100 + c))
    "c_ult": 150,
    # E Royal Maelstrom in the true form
    "e_cd": 720, "e_near": 30000, "e_t": 90, "e_p": 10, "e_r": 30000, "e_dr": 50, "e_vamp": 30, "e_dmg": 20,
    "e_ratio": 50,
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


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


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
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def anchor(name, end):
    """A 1-unit line whose end_effects start zones where he stands (league_gwen's mist)."""
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": "Ally",
            "applied_effects": [], "end_effects": list(end), "speed": 1, "range": 1, "shape": circle(1000),
            "y_offset": 0}


def lob(name, travel, end, target="EnemyChampion"):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def line(name, speed, rng, radius, target, effects):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def build(p):
    ctl_p = p["ctl_p"]

    # ------------------------------------------------------------------ passive: Death in Lavender
    def frenzy():
        """Attack speed after a spell."""
        return refresh("p_as", p["p_t"], attack_speed_mult=p["p_as"])

    def track():
        """On an enemy champion she hit: keeps p_alive up while it lives (its own pulse, league_viego's window); her
        controller watches for it lapsing while `p_win_on` lasts (2 ticks shorter, so a window running out is never
        read as a death)."""
        return combine(casted(p["p_win"], 1, refresh("p_alive", 2)),
                       on_me(refresh("p_alive", 3), refresh("p_win_on", p["p_win"] - 2)))

    def lavender():
        """One more lavender stack (a Permanent caster buff each, l_max at most)."""
        e = flag("l1", None, attack_speed_mult=p["l_as"])
        for i in range(2, p["l_max"] + 1):
            e = sw(f"l{i - 1}", flag(f"l{i}", None, attack_speed_mult=p["l_as"]), e)
        return sw(f"l{p['l_max']}", NONE, e)

    def true_form():
        return refresh("r_on", p["r_t"], hp_mult=p["r_hp"], range=p["r_rng"], attack_speed_mult=p["r_as"],
                       move_speed_mult=p["r_ms"])

    # a takedown: a lavender stack, and the coral - the true form renewed, or R's cooldown cut
    coral = sw("r_on", true_form(), refresh("c_cdr", 2, ult_cooldown_mult=p["c_ult"]))
    takedown = combine(*rm("p_win_on"), refresh("p_lock", 6), lavender(), coral, cview("c_eat"), sfx("c_eat"))
    watch = sw("p_win_on", sw("p_alive", NONE, sw("p_lock", NONE, takedown)))

    # ------------------------------------------------------------------ Q Void Surge
    def q_cast():
        hit = [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit"),
               homing("q_tw", "EnemyChampion", [track(), on_me(refresh("q_ch", p["q_t_r"] + 4))])]

        def rush(t):
            return {"type": "RushTime", "speed": p["q_speed"], "tick": t, "range": 1000,
                    "casting_target": "EnemyWithoutTower", "penetrate": True, "applied_effects": [T(e) for e in hit]}
        cd = sw("r_on", refresh("q_cd", p["q_cd_r"]), refresh("q_cd", p["q_cd"]))
        # Q -> W: through a champion, the controller slams W at once (once she has cast W herself: `w_lv`)
        land = sw("q_ch", combine(*rm("q_ch"), sw("w_lv", refresh("w_go", ctl_p + 3))))
        return combine(cd, *rm("q_ch"), anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p), frenzy(),
                       delayed(p["q_go"] - 1, alive(cview("q_dash"), sw("r_on", rush(p["q_t_r"]), rush(p["q_t"])))),
                       delayed(p["q_go"] + p["q_t_r"], alive(land)))

    # ------------------------------------------------------------------ W Above and Below
    def w_cast():
        # W -> Q: a champion knocked up takes q_cd off and the controller dashes Q at it
        hit = [attack(p["w_dmg"], p["w_ratio"]), {"type": "Airborne", "duration": p["w_up"]},
               buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_hit"), tsfx("w_hit"),
               homing("w_tw", "EnemyChampion", [track(), on_me(*rm("q_cd"), refresh("q_go", ctl_p + 3))])]
        return combine(refresh("w_cd", p["w_cd"]), anim("skill2", p["w_dur"]), sfx("w"), voice("vo_w", p), frenzy(),
                       delayed(p["w_rel"] - 1, alive(cview("w_slam"), sfx("w_slam"),
                                                     line("w_tail", p["w_speed"], p["w_len"], p["w_rad"],
                                                          "EnemyWithoutTower", hit))))

    # ------------------------------------------------------------------ E Royal Maelstrom (in the true form)
    slash = homing("e_slash", "EnemyChampionRecentlyAttacked",
                   [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")])
    storm = combine(refresh("e_cd", p["e_cd"]), anim("skill_e", p["e_t"]), sfx("e"), voice("vo_e", p), frenzy(),
                    refresh("e_on", p["e_t"], damaged_reduce=p["e_dr"], vamp=p["e_vamp"]),
                    on_me(casted(p["e_t"], p["e_p"], alive(pick(p["e_r"], "EnemyChampionRecentlyAttacked", slash)))))
    if p["native"]:   # the add-on raises `low` from her real health
        maelstrom = sw("low", storm)
    else:             # two enemy champions on her
        maelstrom = combine(*rm("c_e1", "c_e2"),
                            around(p["e_near"], "EnemyChampion", sw("c_e1", flag("c_e2", 3), flag("c_e1", 3))),
                            sw("c_e2", storm), *rm("c_e1", "c_e2"))
    maelstrom = sw("r_on", sw("e_cd", NONE, maelstrom))

    # ------------------------------------------------------------------ the controller (a pulse on her)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on her is not (league_zac):
    # her attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling` says one runs; only for Bel'Veth
    # herself (`own`, a flag her attack raises: league_sylas's stolen ult hangs it too, league_singed)
    ctl = combine(refresh("polling", ctl_p + 2), sw("own", combine(
        watch,
        sw("q_go", combine(*rm("q_go"), sw("q_cd", NONE, pick(p["q_range"], "EnemyChampion", q_cast())))),
        sw("w_go", combine(*rm("w_go"), sw("w_cd", NONE, pick(p["w_range"], "EnemyChampion", w_cast())))),
        maelstrom)))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", ctl_p + 2), casted(p["ctl_t"], ctl_p, ctl))))

    # ------------------------------------------------------------------ R Endless Banquet
    burst = around(p["r_r"], "EnemyWithoutTower", attack(p["r_dmg"], p["r_ratio"]),
                   buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]), view("r_hit"), tsfx("r_hit"))
    r_cast = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p), frenzy(),
                     delayed(p["r_hit"] - 1, alive(cview("r_burst"), sfx("r_burst"), burst, true_form())))

    # ------------------------------------------------------------------ attack
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   homing("a_tw", "EnemyChampion", [track()]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100, attack), sw("own", NONE, flag("own", None)), hang,
                              delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"], attack), hang, r_cast))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], attack), sw("q_cd", NONE, q_cast())), key="skill")
    skill2 = action("idle", 3, 60, 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["w_dmg"], p["w_ratio"], attack),
                            sw("w_cd", NONE, combine(sw("w_lv", NONE, flag("w_lv", None)), w_cast()))), key="skill2")

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("w_tail")]
    views_e = [E("a_hit"), E("q_dash", FX, -1, False), E("q_hit"), E("w_slam", BIG, -1, False), E("w_hit"),
               E("r_burst", BIG, -1, False), E("r_hit"), E("e_hit"), E("c_eat")]
    views_b = [B_("p_as", FX, -1, "p_as"), B_("w_slow", FX, -1, "slow"), B_("r_slow", FX, -1, "slow"),
               B_("r_on", FX, -1, "r_aura"), B_("e_on", BIG, 3, "e_storm")]
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
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
