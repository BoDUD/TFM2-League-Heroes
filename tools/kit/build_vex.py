"""Build league_vex.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_vex.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: mid, layout A - Q / E / R, W in the passive - with the add-on). TFM2 has three
active slots: Mistral Bolt (Q) is `skill`, Looming Darkness (E) `skill2`, Shadow Surge (R) the `ult`; Personal Space
(W) rides the attack: when an enemy champion stands within w_r as she attacks and W is ready, the attack becomes W.
  passive Doom 'n Gloom (终焉暮气): Doom is ready while the flag `p_wait` is off (at the start, and p_cd ticks after it
          was spent); her next Q, E or W spends it and that cast also fears every enemy it hits for p_fear ticks
          (League: the next basic ability fears and interrupts dashes, every 25-18 s). The Shadow's eyes flash on her
          (`p_ready`) when Doom is back.
          Gloom (暮气): Looming Darkness marks the enemies it lands on (`g_mark`, g_t ticks). League consumes the mark
          with her next damage on that enemy (g_dmg + g_ratio% AP) and shortens Doom's wait. Data reads no buff on
          the target, so here a champion caught by E lays the caster flag `g_win` and her first Q, W or R hit on a
          champion inside it deals the Gloom damage (`g_pop`) and ends it; the add-on does the real thing.
  attack  a little dark bolt (100% AD), homing on `Enemy` (towers too), released on a_rel.
  W       Personal Space (生人勿近), in the attack: when an enemy champion is within w_r and `w_cd` is off, the attack
          plays `skill_w`: a shield (w_sh + w_sh_ratio% AP for w_sh_t ticks) and a shock wave around her (w_dmg +
          w_ratio% AP to every enemy within w_r; with Doom also a fear).
  skill   Q Mistral Bolt (寒心波云), `Targeting` on `EnemyWithoutTower` (q_range): a wave flies straight at the target
          and through it (penetrating, q_len): q_dmg + q_ratio% AP to every enemy on the line. League's bolt slows down
          and then speeds up; one speed here.
  skill2  E Looming Darkness (溟濛渐染), `Targeting` on `EnemyWithoutTower` (e_range): the Shadow flies (a lob of
          e_fly ticks) to the target's spot and spreads there (radius e_r): e_dmg + e_ratio% AP, e_slow% slow for
          e_slow_t ticks and Gloom on every enemy.
  ult     R Shadow Surge (愁煞), `Targeting` on `EnemyChampion` (r_range): a missile flies at the champion (homing):
          r_dmg + r_ratio% AP and the mark (`r_mark`); r_wait ticks later she surges onto it (`ult_dash`, MoveToTarget)
          and strikes (`ult_hit`): r2_dmg + r2_ratio% AP. League resets R when the marked champion dies within 6 s:
          the add-on's.
The add-on copy (--native, addons/league_vex): the passive league_vex:gloom reads the hits - a real Gloom on each
enemy (E and any enemy who dashes within p_dash_r of her), consumed by her next damage on that enemy (g_dmg + g_ratio%
AP) and taking g_cut% off Doom's wait; Shadow Surge comes back when its marked champion dies within r_reset ticks.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_vex.data_champion")
ID = "league_vex"
FX = "asset/league/effects/league_vex_fx"
BIG = "asset/league/effects/league_vex_big"

# League units x 100 = ours (attack range 550 -> 55000 like every mid); radii count the unit's collision radius
# (~15000) on top. Timings from the strips (tools/art/rig_vex.py MS): the attack's fling frame 2 from 80 ms (a_rel 6), Q's
# lunge frame 3 from 150 ms (q_rel 10), Personal Space's slam frame 3 from 130 ms (w_rel 9), E's kick frame 2 from 80 ms
# (e_rel 6), R's throw frame 3 from 150 ms (r_rel 10); each action as long as its strip. Numbers = the 10-min classic-SDK simulations
# (mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both sides,
# 2026-10-20): the draft (hp 900, Q 70 + 60%, E 60 + 50% every 12 s, R 80 + 20% then a surge onto him 160 + 60% every
# 40 s) -4.69 (league_zoe +1.17 the same batch): the surge put her in the middle of the enemies (3.7 deaths a game; no
# surge -1.56, R only on champions hit lately -4.01). R landing with Personal Space and Q 95 + 70%, E 80 + 60%, the
# surge 200 + 70%, hp 960 -1.47 (no surge +0.48); the surge stopping r_stop short of the champion (league_zoe R's
# jump) 40000 +0.36, 48000 +0.77; + Gloom 60 + 30%, E every 10 s +0.65 / -0.02 (seeds 1-8 / 9-16); + R every 35 s
# +1.44 / +0.97 (about +1.2, league_zoe +1.17, league_volibear +1.39). Timed to the strips (the releases earlier, W's
# burst on its slam frame) +0.40 / +0.87; Q 105 +1.29 / +0.48, + the surge 230 +1.85 / +1.73, 215 +0.73 / +1.02, 225
# +0.97 / +1.17 (about +1.1) = P.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's Vex:
    # 590 +104 hp, 23 armour, 28 mr, 335 move, 550 range, attack speed 0.669
    "hp": 960, "hp_g": 95, "atk": 72, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 910, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 86, "a_rel": 6, "a_speed": 4500,
    # passive Doom 'n Gloom (League: Doom every 25-18 s, fear 0.75 s; Gloom 6 s, 30-140 +20% AP, Doom -25%)
    "p_cd": 900, "p_fear": 45, "g_t": 360, "g_dmg": 60, "g_ratio": 30,
    # W Personal Space (League: 475 radius, 80-200 +30% AP, shield 50-130 +75% AP for 2.5 s, cd 16-12)
    "w_r": 40000, "w_cd": 720, "w_dur": 27, "w_rel": 9, "w_dmg": 70, "w_ratio": 40, "w_sh": 60, "w_sh_ratio": 60,
    "w_sh_t": 150,
    # Q Mistral Bolt (League: 1200 range, 60-240 +60% AP, cd 8-4)
    "q_cd": 360, "q_range": 80000, "q_dur": 30, "q_rel": 10, "q_speed": 4000, "q_len": 95000, "q_w": 8000,
    "q_dmg": 105, "q_ratio": 70,
    # E Looming Darkness (League: 800 range, 50-170 +40-60% AP, slow 30-50% for 2 s, cd 13)
    "e_cd": 600, "e_range": 70000, "e_dur": 30, "e_rel": 6, "e_fly": 18, "e_r": 22000, "e_dmg": 80, "e_ratio": 60,
    "e_slow": 35, "e_slow_t": 120,
    # R Shadow Surge (League: 2000-3000 range, 75-175 +20% AP mark, 150-350 +50% AP surge, cd 140-100)
    "r_cd": 2100, "r_range": 110000, "r_dur": 27, "r_rel": 10, "r_speed": 5000, "r_dmg": 80, "r_ratio": 20,
    "r_wait": 8, "r_dash": 4500, "r_dash_anim": 24, "r2_dmg": 225, "r2_ratio": 70, "r_hit_dur": 24,
    "r_surge": 1, "r_recent": 0, "r_w": 1, "r_stop": 48000, "r_jspeed": 6000,
    "vo_gap": 600,
    # the add-on (addons/league_vex): Gloom on enemies who dash within p_dash_r, Doom's wait cut by g_cut% per Gloom
    # consumed, R back when its mark dies within r_reset ticks
    "p_dash_r": 60000, "g_cut": 25, "r_reset": 360,
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


def fear(tick):
    return {"type": "Fear", "tick": tick}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def around(r, target, effects):
    return {"type": "RangeEffect", "shape": circle(r), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag she never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
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


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])
    # Doom: spent by the cast that finds `p_wait` off; the Shadow's eyes flash on her when it is back
    spend = combine(sfx("p_fear"), flag("p_wait", p["p_cd"]), delayed(p["p_cd"], cview("p_ready"), sfx("p_ready")))
    # the add-on's copy: her hits (but E's) mark what they strike (`v_hit`, 2 ticks) for the add-on's Gloom, and the
    # add-on shows Doom coming back (it shortens the wait)
    vh = [buff("v_hit", 2)] if native else []
    if native:
        spend = combine(sfx("p_fear"), flag("p_wait", p["p_cd"]))

    def doomed(plain, feared):
        """`plain` normally; with Doom ready `feared` (the same cast with a fear) and Doom spent."""
        return sw("p_wait", plain, combine(spend, feared))

    # Gloom (data's stand-in): her first Q / W / R hit on a champion inside E's window deals the Gloom damage
    pop = NONE if native else sw("g_win", combine(*rm("g_win"), ap(p["g_dmg"], p["g_ratio"]), view("g_pop"),
                                                  tsfx("g_pop")))

    # ------------------------------------------------------------------ attack: the dark bolt / W Personal Space
    plain = combine(sfx("a"), homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")] + vh, p["a_speed"]))

    def wave(scared):
        hit = [ap(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")] + vh + ([fear(p["p_fear"])] if scared else [])
        return combine(around(p["w_r"], "EnemyWithoutTower", hit), around(p["w_r"], "EnemyChampion", [pop]))

    def space(*pose, at=0):
        """Personal Space: the shield and the wave `at` ticks after its pose starts (skill_w's slam, frame 3)."""
        burst = combine(sfx("w"), voice("vo_w", p),
                        # on her: a Shield goes to the action's target (an enemy here, league_annie W's lesson)
                        pick(1, "AllyOnlySelf", {"type": "Shield", "amount": p["w_sh"], "attack_ratio": 0,
                                                 "ap_ratio": p["w_sh_ratio"], "tick": p["w_sh_t"]}),
                        cview("w_shield"), cview("w_ring"),
                        doomed(wave(False), wave(True)))
        return combine(*pose, flag("w_cd", p["w_cd"]), delayed(at, alive(burst)) if at else burst)

    personal = space(anim("skill_w", p["w_dur"]), at=p["w_rel"] - 1)
    near = combine(pick(p["w_r"], "EnemyChampion", flag("w_near", 1)),
                   sw("w_near", combine(*rm("w_near"), sw("w_cd", plain, personal)), plain))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), delayed(p["a_rel"] - 1, alive(near))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Mistral Bolt
    def bolt(scared):
        hit = [ap(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")] + vh + ([fear(p["p_fear"])] if scared else [])
        out = [line("q_bolt", p["q_speed"], p["q_len"], p["q_w"], "EnemyWithoutTower", hit, penetrate=True)]
        if not native:      # the Gloom on a champion rides a hidden champion-only twin
            out.append(sw("g_win", line("q_twin", p["q_speed"], p["q_len"], p["q_w"], "EnemyChampion", [pop],
                                        penetrate=True, y=5000)))
        return combine(*out)

    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ratio"], ap), sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive(doomed(bolt(False), bolt(True)), sfx("q_fly")))))

    # ------------------------------------------------------------------ skill2: E Looming Darkness
    def darkness(scared):
        hit = [ap(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
               buff("g_mark", p["g_t"]), tsfx("e_hit")] + ([fear(p["p_fear"])] if scared else [])
        land = [view("e_land"), sfx("e_land"), zone("e_zone", p["e_r"], hit)]
        if not native:
            land.append(zone("e_gloom", p["e_r"], [refresh("g_win", p["g_t"])], "EnemyChampion"))
        return combine(cview("e_cast"), lob("e_fly", p["e_fly"], land))

    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(doomed(darkness(False), darkness(True))))))

    # ------------------------------------------------------------------ ult: R Shadow Surge
    # she lands with Personal Space when it is ready (League's R -> W)
    strike = [ap(p["r2_dmg"], p["r2_ratio"]), view("r_hit"), tsfx("r_hit"), pop] + vh + (
        [sw("w_cd", NONE, space())] if p["r_w"] else [])
    surge = {"type": "MoveToTarget", "speed": p["r_dash"], "range": p["r_range"] + 30000,
             "end_effects": [anim("ult_hit", p["r_hit_dur"])]}
    if p["r_stop"]:
        # she surges only to r_stop short of the first champion on the way (league_zoe R's jump: a hidden line whose
        # end teleports her) and strikes from there
        surge = line("r_surge", p["r_jspeed"], p["r_range"] + 30000, p["r_stop"], "EnemyChampion", [],
                     end=[{"type": "Teleport"}, anim("ult_hit", p["r_hit_dur"])], y=5000)
    marked = [ap(p["r_dmg"], p["r_ratio"]), buff("r_mark", p["r_wait"] + 30), tsfx("r_mark"), *vh,
              delayed(p["r_wait"], anim("ult_dash", p["r_dash_anim"]), sfx("r_dash"), surge,
                      delayed(p["r_dash_anim"] // 2, *strike)) if p["r_surge"] else delayed(p["r_wait"], *strike)]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting",
                 "EnemyChampionRecentlyAttacked" if p["r_recent"] else "EnemyChampion",
                 combine(decoy(p["r_dmg"] + p["r2_dmg"], p["r_ratio"] + p["r2_ratio"], ap), sfx("r"), voice("vo_r", p),
                         delayed(p["r_rel"] - 1, alive(homing("r_missile", "EnemyChampion", marked, p["r_speed"]),
                                                       sfx("r_fly")))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    views_p = [Pj("a_bolt"), Pj("q_bolt"), Pj("r_missile")]
    views_e = [E("a_hit"), E("q_hit"), E("w_hit"), E("w_ring", BIG, -1), E("w_shield", FX, 3), E("e_cast", FX, 3),
               E("e_land", BIG, -1, False), E("r_hit"), E("p_ready", FX, 3)]
    if not native:
        views_e.append(E("g_pop"))
    views_b = [B_("e_slow", FX, -1), B_("g_mark", FX, 3), B_("r_mark", FX, 3)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_vex:gloom", "params": {
            k: p[k] for k in ("p_cd", "p_dash_r", "g_t", "g_dmg", "g_ratio", "g_cut", "r_reset")}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC", "Shield"], **extra,
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
