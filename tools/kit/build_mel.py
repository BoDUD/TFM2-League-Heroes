"""Build league_mel.data_champion (bottom lane stand-in, Magician: the Soul's Reflection) from the parameters P.

    python tools/kit/build_mel.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: layout A - Q / E / R, the passive and W in the attack -, bottom lane, an add-on;
「有连招要做连招」). League has no bottom-lane marksman left for the pack: Mel, a mage, stands in.
  passive Searing Brilliance (灼灼之光): every Q / E / R cast gives her next attack p_n more bolts (League: 3, up to 9;
          the stack ladder p_3 / p_6 / p_9), each p_dmg + p_ratio% AP magic.
          Overwhelm (夺命残影): every hit of hers on an enemy champion - the attack, each bolt, each of Q's blasts, E's
          orb - lays one stack: an `AddCasted` (Fire, m_t ticks) on the champion, so a champion really carries one per
          recent hit (no data effect counts a target's stacks; every hit adds its own instance, champion-data section
          4). League executes a champion whose stacks would deal more than its health: no data effect reads health, so
          the main pack has no execute (the stacks are spent by R alone); the add-on's copy executes (league_mel:overwhelm).
  W       Rebuttal (灵魂折镜), no slot of its own: the first attack hit on an enemy champion every w_cd ticks raises the
          barrier for w_t ticks - w_red% less damage taken (`damaged_reduce`), w_ref% of every hit sent back to its
          dealer (`damage_reflect`: League reflects projectiles only, the engine every hit) and w_ms% move speed. No
          effect blocks or turns a projectile (champion-data section 4); the add-on raises the barrier when an enemy
          projectile flies at her and fires a copy of it back at its caster.
  attack  a golden bolt (100% AD), homing on `Enemy`, released on a_rel; with the passive's bolts after a cast.
  skill   Q Radiant Volley (耀光齐射), `Targeting` on `EnemyWithoutTower` (q_range): the volley lands on the target's
          spot q_fly ticks after the release (a hidden lob) and its bolts burst there q_n times, q_gap ticks apart (a
          zone of radius q_r pulsing: League's bolts explode round the spot, each hit counting): q_dmg + q_ratio% AP
          and an Overwhelm stack on each champion every burst. One zone instead of q_n lobs keeps the slot small
          (the game copies skill each tick). COMBO E -> Q (League: Solar Snare's root holds the target in the
          volley): the orb's champion-only twin opens e_combo for e_combo ticks; a Q released inside it lands on a
          champion in crowd control within q_range + 10000 (the one just rooted) in q_fast ticks.
  skill2  E Solar Snare (阳炎涡旋), `Targeting` on `EnemyWithoutTower` (e_range): a radiant orb flies at the target and
          on to e_len. Its centre (e_w) roots (`Bind` e_root) and deals e_dmg + e_ratio% AP; the glow round it (e_rw)
          slows e_slow% for e_slow_t ticks and burns (e_dot + e_dot_r% AP every e_dper ticks, e_dn times).
  ult     R Golden Eclipse (鎏金蚀日), `Targeting` on `EnemyChampion` (r_range: in a fight). The caster flag r_go opens
          for r_win ticks; every Overwhelm stack on any enemy champion, anywhere on the map, checks it every m_per
          ticks and strikes once: r_st + r_ratio% AP (so the damage is per stack, as League's bonus is). r_win =
          m_per: the flag is seen on exactly r_win ticks from the tick it is added, by every unit, so a stack checking
          every m_per ticks finds it once (SDK trace, 2026-10-20: 1 / 10 / 3 stacks struck 1 / 10 / 3 times; a 1-tick
          flag with a check every tick struck some champions' stacks and missed others). COMBO stacks -> R: the
          add-on's AI hook presses R when the stacks would kill a champion, or hold them for a second champion.
The combos the AI cannot press from data (E before Q, R at a killing count, W on an incoming projectile) are the
add-on's AI hook league_mel:combo (addons/league_mel).
Timings: placeholders until tools/art/rig_mel.py's strips (a frame's start in ticks = ms x 0.06).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_mel.data_champion")
ID = "league_mel"
FX = "asset/league/effects/league_mel_fx"
BIG = "asset/league/effects/league_mel_big"

# League units x 100 = ours (attack range 550 -> 55000 like every ranged hero); radii count the unit's collision
# radius (~15000) on top.
# Numbers = the 10-min classic-SDK simulations (C:/t/ml_sim: kd.py 600 8 --lane 3 against archer, gunner,
# boomerang_hunter, poison_dart_hunter and bomber, three lineups, both sides).
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Mel:
    # 630 +99 hp, 54 AD, 21 +5.2 armour, 30 +1.3 mr, 330 move, 550 range, attack speed 0.625
    "hp": 920, "hp_g": 95, "atk": 72, "atk_g": 5, "apw": 40, "apw_g": 24, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 70, "a_rel": 10, "a_speed": 4500, "a_y": 0,
    # the passive's bolts (League: 3 a cast, up to 9, 2-8 +2.5% AP... each) and Overwhelm (League: unlimited stacks)
    "p_n": 3, "p_dmg": 12, "p_ratio": 5, "p_gap": 2, "p_speed": 4000,
    "m_t": 360, "m_per": 6,
    # W Rebuttal (League: 1.5 s, reflects projectiles, no damage taken, 35% move speed; cd 35-23 s)
    "w_cd": 1500, "w_t": 75, "w_red": 100, "w_ref": 40, "w_ms": 25,
    # Q Radiant Volley (League: 950 range, a volley of bolts round the spot, 13-... +8.5% AP each; cd 10-6)
    "q_cd": 360, "q_range": 85000, "q_dur": 33, "q_rel": 10, "q_n": 6, "q_gap": 6, "q_fly": 14, "q_r": 20000,
    "q_dmg": 30, "q_ratio": 15,
    # the E -> Q combo: the window after the orb roots a champion and the volley's quick lobs
    "e_combo": 75, "q_fast": 4,
    # E Solar Snare (League: 1000 range, root at the centre, slow + burn round it; cd 11-9)
    "e_cd": 600, "e_range": 80000, "e_dur": 33, "e_rel": 10, "e_speed": 2200, "e_len": 95000, "e_w": 6000,
    "e_rw": 17000, "e_dmg": 80, "e_ratio": 50, "e_root": 60, "e_slow": 30, "e_slow_t": 90,
    "e_dot": 10, "e_dot_r": 6, "e_dper": 30, "e_dn": 4,
    # R Golden Eclipse (League: every marked enemy anywhere, +x per stack; cd 120-80)
    "r_cd": 2100, "r_range": 70000, "r_dur": 33, "r_rel": 12, "r_win": 6, "r_st": 20, "r_ratio": 8,
    "vo_gap": 600,
    # the add-on (addons/league_mel): the execute (League: the stacks' worth >= the champion's health), the
    # barrier on an incoming projectile and the reflected copy
    "x_st": 20, "x_ratio": 8, "w_near": 30000, "w_back": 6000, "w_back_dmg": 60, "w_back_r": 40,
    "native": 0, "probe": 0,
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
    return {"type": "Combine", "effects": list(effects)}


NONE = {"type": "Combine", "effects": []}


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def is_champ(*effects):
    """Inside a projectile's applied effects: the unit it hit, when that is a champion (league_sivir Q)."""
    return pick(1, "EnemyChampion", *effects, fp=True)


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end=(), penetrate=False, y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": penetrate, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def lob(name, travel, end):
    """A hidden 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, life, period, first, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": life, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    # ------------------------------------------------------------------ Overwhelm: one stack a champion hit
    # The stack is an AddCasted on the champion: every m_per ticks it reads R's flag r_go on her and strikes once.
    # The add-on's copy also marks the champion with a plain m_mark buff per stack, which the native execute counts.
    strike = combine(ap(p["r_st"], p["r_ratio"]), view("r_hit"))
    stack_ = [{"type": "AddCasted", "casted_type": "Fire", "duration": p["m_t"], "period": p["m_per"],
               "effects": [sw("r_go", strike)]}]
    if p.get("probe"):
        stack_.append(view("m_probe"))
    if native:
        stack_ += [buff("m_mark", p["m_t"]), {"type": "Native", "effect_ref": "league_mel:overwhelm"}]
    mark = is_champ(*stack_)      # on a homing projectile's own target
    # a zone or a line runs a RandomTarget from its middle for every unit it hits (a champion beside a minion was
    # marked twice): those mark through a champion-only twin instead, the stack straight in its applied effects

    # ------------------------------------------------------------------ W Rebuttal: the first champion hit every w_cd
    barrier = sw("w_cd", NONE, combine(
        flag("w_cd", p["w_cd"]), flag("w_on", p["w_t"], damaged_reduce=p["w_red"], damage_reflect=p["w_ref"],
                                     move_speed_mult=p["w_ms"]),
        sfx("w"), voice("vo_w", p)))
    rebut = [] if native else [is_champ(barrier)]

    # ------------------------------------------------------------------ the passive's bolts (after a cast)
    def charge():
        """A Q / E / R cast: three more bolts on the next attack, nine at most."""
        return sw("p_6", combine(*rm("p_6"), flag("p_9", None)),
                  sw("p_3", combine(*rm("p_3"), flag("p_6", None)), sw("p_9", NONE, flag("p_3", None))))

    bolt = homing("p_bolt", "Enemy", [ap(p["p_dmg"], p["p_ratio"]), view("p_hit"), mark], p["p_speed"], p["a_y"])

    def volley(k):
        return [delayed(1 + i * p["p_gap"], alive(bolt)) for i in range(k)]

    extra = sw("p_9", combine(*rm("p_9"), *volley(3 * p["p_n"])),
               sw("p_6", combine(*rm("p_6"), *volley(2 * p["p_n"])),
                  sw("p_3", combine(*rm("p_3"), *volley(p["p_n"])))))

    # ------------------------------------------------------------------ attack: the golden bolt
    shot = homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit"), mark, *rebut], p["a_speed"],
                  p["a_y"])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), delayed(p["a_rel"] - 1, alive(sfx("a"), shot, extra))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Radiant Volley
    q_life = p["q_gap"] * (p["q_n"] - 1) + 1
    land = [view("q_volley"), sfx("q_hit"),
            field("q_burst", p["q_r"], q_life, p["q_gap"], 1, [ap(p["q_dmg"], p["q_ratio"]), view("q_hit")]),
            field("q_mark", p["q_r"], q_life, p["q_gap"], 1, stack_, "EnemyChampion")]
    quick = pick(p["q_range"] + 10000, "EnemyChampionInCC", flag("q_go", 1), *rm("e_combo"),
                 lob("q_aim", p["q_fast"], land))
    volley_q = combine(*rm("q_go"), sw("e_combo", quick), sw("q_go", NONE, lob("q_aim", p["q_fly"], land)))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"] * 4, p["q_ratio"] * 4, ap), sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive(charge(), volley_q))))

    # ------------------------------------------------------------------ skill2: E Solar Snare
    rooted = [ap(p["e_dmg"], p["e_ratio"]), {"type": "Bind", "duration": p["e_root"]}, buff("e_bound", p["e_root"]),
              tsfx("e_hit")]
    burned = [buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
              {"type": "AddCasted", "casted_type": "Fire", "duration": p["e_dper"] * (p["e_dn"] - 1) + 1,
               "period": p["e_dper"], "effects": [ap(p["e_dot"], p["e_dot_r"]), view("e_burn")]}]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(
                                charge(),
                                line("e_orb", p["e_speed"], p["e_len"], p["e_w"], "EnemyWithoutTower", rooted,
                                     penetrate=True),
                                line("e_glow", p["e_speed"], p["e_len"], p["e_rw"], "EnemyWithoutTower", burned,
                                     penetrate=True),
                                line("e_hold", p["e_speed"], p["e_len"], p["e_w"], "EnemyChampion",
                                     [refresh("e_combo", p["e_combo"]), *stack_], penetrate=True)))))

    # ------------------------------------------------------------------ ult: R Golden Eclipse
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_st"] * 6, p["r_ratio"] * 6, ap), sfx("r"), voice("vo_r", p),
                         delayed(p["r_rel"] - 1, alive(charge(), cview("r_cast"), sfx("r_hit"),
                                                       refresh("r_go", p["r_win"])))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True, "z": 2}
    views_p = [Pj("a_bolt"), Pj("p_bolt"), Pj("e_orb", BIG)]
    views_e = [E("a_hit"), E("p_hit"), E("q_volley", BIG, 3, False), E("q_hit"), E("e_burn"), E("r_cast", BIG),
               E("r_hit", BIG)]
    if native:      # the add-on's execute and its reflected bolt
        views_e.append(E("x_hit", BIG))
        views_p.append(Pj("w_back"))
    views_b = [B_("w_on", BIG, 3), B_("e_bound", FX, 3), B_("e_slow", FX, -1), B_("p_3"), B_("p_6"), B_("p_9")]
    extra_k = {}
    if native:
        views_b.append(B_("m_mark", FX, 3))
        extra_k["passive"] = {"passive_ref": "league_mel:reflect", "params": {
            k: int(p[k]) for k in ("x_st", "x_ratio", "w_cd", "w_t", "w_red", "w_ref", "w_ms", "w_near", "w_back",
                                   "w_back_dmg", "w_back_r", "atk_range", "q_range", "e_range", "r_range", "r_cd",
                                   "r_st", "r_ratio", "m_t")}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"], **extra_k,
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
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
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
