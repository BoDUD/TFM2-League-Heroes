"""Build league_maokai.data_champion (support, Util) from the parameters P.

    python tools/kit/build_maokai.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-18: support, layout A, the add-on league_maokai, PPU 1.2, pro combos - 「全按推荐做」).
TFM2 has three active slots: Bramble Smash (Q) is `skill`, Twisted Advance (W) `skill2`, Nature's Grasp the `ult`;
Sapling Toss (E) has no slot - the watch throws it (league_jarvaniv's W the same way).
  passive Sap Magic (吸元秘术): any of his skills hitting an enemy readies `sap` (League: a 20 s cooldown cut by every
          cast); his next attack then heals him p_heal + p_ap% AP (data has no % max-health heal: the add-on heals
          League's 4.5-12% of max health) and deals p_hp% of his max health more as magic damage; p_cd ticks between two.
  attack  a sweep of the huge arm (100% AD) struck by a hidden homing hit on `Enemy` (towers too) on a_hit; its
          champion-only twin marks the fight (`fight`, f_t ticks).
  skill   Q Bramble Smash (荆棘重击), a 3-tick `Targeting` on `EnemyWithoutTower` (q_range) whose `CasterAnimation` holds
          him for the smash: on q_rel every enemy within q_kb is knocked back (away from him), and a short shockwave
          (q_len, q_w) deals q_dmg + q_ap% AP magic + q_thp% of the target's max health (true: ApAttack has no
          target-health part, league_amumu's way) and slows q_s1% for q_s1t ticks on top of q_s2% for q_s2t (a slow that
          decays, league_ahri W's two buffs). The slot reads `q_cd` (set by every smash, the slot's own cooldown) so a
          smash already thrown by W's combo leaves the AI's next press an empty 3-tick cast.
  skill2  W Twisted Advance (扭曲突刺), a 3-tick `Targeting` on `EnemyChampion` (w_range): only when an allied champion
          stands within w_ally of him (`ally`, counted by the watch), in a fight (`fight`), or right after his R rooted
          someone (`r_hit`) - else an empty 3-tick cast (the user's rule 「看好时机」). He sinks into roots and dashes
          (`MoveToTarget` w_speed, the roots w_trail running with him) with damaged_reduce 100 + cc_immune (League: untargetable;
          only Banish is, and it blinds his team - league_masteryi Q's way); on arrival the target is rooted (`Bind`
          w_root) and takes w_dmg + w_ap% AP. Pro combo W -> Q: with Q ready (no `q_cd`) the smash follows on landing.
  E       Sapling Toss (树苗投掷), thrown by the watch: e_cd off, nothing else being cast, an enemy champion within
          e_range - a lob to where it stood when the sapling left (walking off dodges it). The sapling arms after e_arm
          ticks and stands guard e_life ticks (League 30 s; the pack's traps live <= 12 s: league_teemo R); an enemy
          (minions too) within e_trig wakes it: it hops and bursts, e_dmg + e_ap% AP in e_r and a e_slow% slow for
          e_slow_t ticks (league_teemo R's trigger / blast flags). One at a time. Brush (stronger saplings) is data-blind:
          the add-on.
  ult     R Nature's Grasp (自然之握): the slot (a 3-tick `Targeting` on `EnemyChampion` within r_range) only arms the
          ult for r_arm ticks; the watch sends the wall once the moment is right (the user's rule 「看好时机」): two enemy
          champions within r_cnt, or a fight with one. Unused, the window ends with the cooldown capped (`r_retry`). The
          wall (a penetrating `LinearProjectile`, r_speed, r_len, radius r_w: league_nami R's tidal wave) roots every
          enemy it passes once (`Bind`) - longer the farther it went (League 0.8-2.6 s: three steps by caster flags
          r_d1 / r_d2 set at the cast, league_xerath E's way) - and deals r_dmg + r_ap% AP; a champion hit hastes him
          (r_ms% decaying over r_ms_t). Pro combo R -> W: a root opens W at once (`r_hit`).
  watch   A life-long `AddCasted` started by his first attack or R press of each life (`init`), every watch_p ticks:
          counts enemy champions within r_cnt (c_e1, c_e2) and allied champions within w_ally (`ally`); sends the wall
          when armed; throws a sapling.
The add-on copy (--native): the passive league_maokai:sap_magic heals League's % of max health on the readied attack
(its own cooldown, cut by his casts and by enemy skills hitting him) and empowers saplings standing in brush, so the copy
drops the data heal and marks saplings for it (addons/league_maokai).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_maokai.data_champion")
ID = "league_maokai"
FX = "asset/league/effects/league_maokai_fx"
BIG = "asset/league/effects/league_maokai_big"

# Timings from the strips (tools/art/rig_maokai.py MS): the attack's blow frame 3 from tick 10.2 (a_hit 11) of 30, Q's slam
# frame 3 from 11.4 (q_rel 12) of 32, W down 24 and up 20, E's throw frame 3 from 9.6 (e_rel 10) of 29, R's slam frame 4
# from 19.8 (r_rel 20) of 42.
P = {
    # stats (support tanks: league_braum 78 +6 attack, 25 +15 AP, 1300 +120 hp, 44 +8 armour); League's Maokai: 665 +109
    # hp, 64 AD, 35 +5.2 armour, 32 +2.05 mr, 335 move, range 125, attack speed 0.8
    "hp": 1420, "hp_g": 135, "atk": 72, "atk_g": 6, "ap": 25, "ap_g": 15, "def": 50, "def_g": 9, "mr": 36, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    # attack: the arm's sweep lands on a_hit
    "atk_range": 26000, "atk_dur": 30, "atk_cd": 75, "a_hit": 11, "f_t": 180,
    # passive Sap Magic (League: heal 4.5-12% max hp + bonus 5-65 + ..., cd 20 s minus 4 s a cast)
    "p_heal": 40, "p_ap": 60, "p_hp": 2, "p_cd": 240, "p_t": 300,
    # the add-on's Sap Magic: 4.5-12% of max health by level (permille), an enemy skill cast within p_win ticks counts as a
    # skill hit; a zone of his standing still e_stand ticks is a sapling
    "p_heal_lo": 45, "p_heal_hi": 120, "p_win": 90, "e_stand": 20,
    # skill: Q Bramble Smash (League: 65-245 + 40% AP + 2-4% max hp, knock-back, slow 99% decaying over 0.5 s, cd 7-5)
    "q_cd": 360, "q_range": 30000, "q_dur": 32, "q_rel": 12, "q_kb": 16000, "q_kb_s": 2000, "q_kb_t": 12,
    "q_len": 45000, "q_w": 10000, "q_speed": 6000, "q_dmg": 100, "q_ap": 40, "q_thp": 2,
    "q_s1": 50, "q_s1t": 20, "q_s2": 45, "q_s2t": 40,
    # skill2: W Twisted Advance (League: range 525, 70-170 + 40% AP, root 1-1.4 s, untargetable, cd 14-10)
    "w_cd": 600, "w_range": 45000, "w_ally": 70000, "w_speed": 2500, "w_dash": 24, "w_root": 78,
    "w_dmg": 100, "w_ap": 40, "w_land": 20,
    # E Sapling Toss (League: 1100 range, 55-155 + 40% AP + 5% bonus hp, slow 35% 2 s, 30 s life, cd 18-14)
    "e_cd": 600, "e_range": 60000, "e_dur": 29, "e_rel": 10, "e_travel": 20, "e_arm": 30, "e_life": 720,
    "e_trig": 14000, "e_r": 24000, "e_dmg": 100, "e_ap": 50, "e_slow": 35, "e_slow_t": 120, "e_link": 30,
    # the add-on's sapling in brush (League: a bigger blast, 2x damage over 2 s, a 45% slow)
    "e_br": 34000, "e_bdmg": 160, "e_bslow": 45, "e_bslow_t": 150,
    # ult: R Nature's Grasp (League: 3000 range, root 0.8-2.6 s by distance, 150-300 + 75% AP, haste 40-80% 2.5 s,
    # cd 130-90)
    "r_cd": 3600, "r_range": 70000, "r_arm": 600, "r_dur": 42, "r_rel": 20, "r_speed": 1500, "r_len": 200000,
    "r_w": 28000, "r_d1": 45, "r_d2": 95, "r_b1": 48, "r_b2": 96, "r_b3": 144, "r_dmg": 180, "r_ap": 75,
    "r_ms": 40, "r_ms_t": 150, "r_cnt": 60000, "r_open": 120,
    # the watch
    "watch_p": 12,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_maokai
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
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
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


def magic(dmg, ap, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap, "hp_ratio": hp}


def true_thp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def heal(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Caster"}


def bind(tick):
    return {"type": "Bind", "duration": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, target, effects, speed=40000):
    """A hidden blow: at this speed it reaches a melee target on the next tick."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def line(name, speed, rng, width, effects, target="EnemyWithoutTower", y=5000):
    """A penetrating line from his spot toward the action's point (or the picked unit)."""
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": True, "shape": circle(width), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


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
    native = bool(p["native"])
    marked = [refresh("fight", p["f_t"])]
    sap = [refresh("sap", p["p_t"])]          # Sap Magic readied by a skill hit

    # ------------------------------------------------------------------ Q: Bramble Smash (also W's combo)
    slow = [buff("q_s1", p["q_s1t"], move_speed_mult=-p["q_s1"]), buff("q_s2", p["q_s2t"], move_speed_mult=-p["q_s2"])]
    q_hit = [magic(p["q_dmg"], p["q_ap"]), true_thp(p["q_thp"]), *slow, view("q_hit"), tsfx("q_hit")]
    smash = combine(refresh("q_cd", p["q_cd"]), refresh("busy", p["q_dur"]), anim("skill", p["q_dur"]), sfx("q"),
                    voice("vo_q", p),
                    delayed(p["q_rel"] - 1, alive(
                        cview("q_cast"), sfx("q_land"),
                        around(p["q_kb"], "EnemyWithoutTower",
                               [{"type": "Knockback", "speed": p["q_kb_s"], "tick": p["q_kb_t"]}]),
                        line("q_wave", p["q_speed"], p["q_len"], p["q_w"], q_hit + sap, y=0),
                        line("q_twin", p["q_speed"], p["q_len"], p["q_w"], marked, target="EnemyChampion", y=0))))

    # ------------------------------------------------------------------ W: Twisted Advance
    w_land = [bind(p["w_root"]), buff("w_bound", p["w_root"]), magic(p["w_dmg"], p["w_ap"]), view("w_hit"), tsfx("w_hit")]
    arrive = [anim("skill2_land", p["w_land"]), sfx("w_land"), cview("w_land"),
              *w_land, *sap, *marked,
              sw("q_cd", NONE, delayed(p["w_land"], alive(smash)))]       # pro combo W -> Q
    # he sinks into the ground in his own frames (skill2), so no CasterInvisible (it would hide the sinking): while he
    # travels he takes no damage and no CC, and the mass of roots under the ground (w_trail) runs to the target with him
    trail = {"type": "TargetProjectile", "name": n("w_trail"), "speed": p["w_speed"], "y_offset": 0,
             "applied_target": "EnemyChampion", "applied_effects": []}
    dash = combine(refresh("busy", p["w_dash"] + p["w_land"]), anim("skill2", p["w_dash"]), sfx("w"),
                   voice("vo_w", p), trail,
                   flag("w_root_on", p["w_dash"], damaged_reduce=100, cc_immune=True),
                   {"type": "MoveToTarget", "speed": p["w_speed"], "range": 400000, "end_effects": arrive})
    # one copy of the dash behind a 1-tick `w_ok` (skill2 is copied every tick: league_maokai keeps it small)
    w_gate = sw("busy", NONE, combine(*rm("w_ok"), sw("r_hit", flag("w_ok", 1), sw("ally", flag("w_ok", 1),
                                                                                  sw("fight", flag("w_ok", 1)))),
                                      sw("w_ok", combine(*rm("w_ok"), dash))))

    # ------------------------------------------------------------------ E: Sapling Toss (thrown by the watch)
    blast = [magic(p["e_dmg"], p["e_ap"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
             view("e_hit"), tsfx("e_hit")]
    blast_b = [magic(p["e_dmg"] * p["e_bdmg"] // 100, p["e_ap"] * p["e_bdmg"] // 100),
               buff("e_slow", p["e_bslow_t"], move_speed_mult=-p["e_bslow"]), view("e_hit"), tsfx("e_hit")]
    life = p["e_life"]
    links = [delayed(t, sw("e_on", view("e_idle"))) for t in range(p["e_arm"], life, p["e_link"])]
    planted = [view("e_land"), sfx("e_land"), refresh("e_on", life + p["e_arm"]), *rm("e_boom"), *links,
               delayed(p["e_arm"],
                       # trigger: the first enemy near swaps `e_on` for `e_boom` (one burst)
                       # (the sapling hops onto it: the burst picture plays on that enemy)
                       field("e_trig", p["e_trig"], life, 1,
                             [sw("e_on", combine(*rm("e_on"), refresh("e_boom", 2), view("e_burst"),
                                                 sfx("e_burst")))], first=0),
                       # blast: checks every 2 ticks, so the 2-tick `e_boom` is seen once - every enemy in e_r hit once
                       *([field("e_blast", p["e_r"], life + 2, 2, [sw("e_boom", combine(*blast, *sap))], first=1)]
                         if not native else
                         # the add-on's copy: a sapling standing in brush (the add-on marks `e_brush` on him while his
                         # standing sapling is in a bush) bursts bigger, harder and slows more (League's empowered one)
                         [field("e_blast", p["e_r"], life + 2, 2,
                                [sw("e_boom", sw("e_brush", NONE, combine(*blast, *sap)))], first=1),
                          field("e_blast_b", p["e_br"], life + 2, 2,
                                [sw("e_boom", sw("e_brush", combine(*blast_b, *sap)))], first=1)]))]
    toss = combine(refresh("e_cd", p["e_cd"]), refresh("busy", p["e_dur"]), anim("skill_e", p["e_dur"]), sfx("e"),
                   voice("vo_e", p),
                   delayed(p["e_rel"] - 1, alive(pick(p["e_range"], "EnemyChampion",
                                                      lob("e_lob", p["e_travel"], planted, target="EnemyChampion")))))

    # ------------------------------------------------------------------ R: Nature's Grasp (sent by the watch)
    roots = sw("r_d1", combine(bind(p["r_b1"]), buff("r_bound", p["r_b1"])),
               sw("r_d2", combine(bind(p["r_b2"]), buff("r_bound", p["r_b2"])),
                  combine(bind(p["r_b3"]), buff("r_bound", p["r_b3"]))))
    haste = [refresh("r_h1", p["r_ms_t"] // 2, move_speed_mult=p["r_ms"] // 2),
             refresh("r_h2", p["r_ms_t"], move_speed_mult=p["r_ms"] - p["r_ms"] // 2)]
    r_hit = [magic(p["r_dmg"], p["r_ap"]), roots, view("r_hit"), tsfx("r_hit")]
    wall = [line("r_wall", p["r_speed"], p["r_len"], p["r_w"], r_hit + sap, y=0),
            line("r_twin", p["r_speed"], p["r_len"], p["r_w"], marked + haste + [refresh("r_hit", p["r_open"])],
                 target="EnemyChampion", y=0)]
    # the aim is locked by a hidden lob landing on r_rel (where the champion stood when he raised his arms); the wall
    # then starts from him toward that point (league_jarvaniv Q's way)
    send = combine(*rm("r_arm"), refresh("busy", p["r_dur"]), anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                   lob("r_lock", p["r_rel"], [alive(flag("r_d1", p["r_d1"]), flag("r_d2", p["r_d2"]), sfx("r_wall"),
                                                    cview("r_cast"), *wall)], target="EnemyChampion"))
    tick = p["watch_p"]
    count = combine(*rm("c_e1", "c_e2"),
                    around(p["r_cnt"], "EnemyChampion", [sw("c_e1", flag("c_e2", 3), flag("c_e1", 3))]),
                    around(p["w_ally"], "AllyNotSelf", [refresh("ally", tick + 1)]))
    ok = pick(p["r_range"], "EnemyChampion", send)
    arm = sw("r_arm", sw("busy", NONE, combine(*rm("r_ok"), sw("c_e2", flag("r_ok", 1), sw("c_e1", sw("fight", flag("r_ok", 1)))),
                                               sw("r_ok", combine(*rm("r_ok"), ok)))))
    throw = sw("e_cd", NONE, sw("busy", NONE, pick(p["e_range"], "EnemyChampion", toss)))
    watch = on_me(casted(1000000, tick, count, delayed(1, arm, throw)))
    init = sw("init", NONE, combine(flag("init", None), watch))

    # ------------------------------------------------------------------ attack: the arm's sweep (+ Sap Magic)
    sapped = [magic(0, 0, p["p_hp"]), view("p_hit"), tsfx("p_hit")]
    drink = sw("p_cd", NONE, sw("sap", combine(*rm("sap"), refresh("p_cd", p["p_cd"]),
                                               *([] if native else [on_me(heal(p["p_heal"], p["p_ap"]))]),
                                               *([refresh("sap_on", 3)] if native else []),
                                               cview("p_heal"), sfx("p_heal"),
                                               homing("p_blow", "Enemy", sapped))))
    blow = combine(sfx("a_swing"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   homing("a_twin", "EnemyChampion", marked), drink)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(init, delayed(p["a_hit"] - 1, blow)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    skill = action("idle", 3, p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_cd", NONE, sw("busy", NONE, smash)), key="skill")
    skill2 = action("idle", 3, p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion", w_gate, key="skill2")
    retry = p["r_cd"] * 100 // 60 - 100
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_retry", 3, ult_cooldown_mult=retry)))
    arm_r = combine(refresh("r_arm", p["r_arm"]), on_me(delayed(p["r_arm"], reset)))
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), arm_r), magic(100, 100)), *rm("r_x"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(init, scored),
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    # projectile pictures turn with the flight: all three are drawn top-bottom symmetric
    views_p = [Pj("e_lob"), Pj("q_wave", BIG, -1), Pj("w_trail", BIG, -1), Pj("r_wall", BIG, -1)]
    views_e = [E("a_hit"), E("p_hit"), E("p_heal", BIG), E("q_cast", BIG, -1), E("q_hit"), E("w_land", BIG, -1),
               E("w_hit"), E("e_land", FX, 0, False), E("e_idle", FX, 0, False), E("e_burst", BIG, 2, False),
               E("e_hit"), E("r_cast", BIG, -1), E("r_hit")]
    views_b = [B_("q_s1", tag="q_slow"), B_("e_slow"), B_("w_bound", tag="root"), B_("r_bound", tag="root"),
               B_("r_h2", BIG, -1, tag="r_haste")]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_maokai:sap_magic",
                            "params": {"heal_lo": p["p_heal_lo"], "heal_hi": p["p_heal_hi"], "p_t": p["p_t"],
                                       "window": p["p_win"], "stand": p["e_stand"]}}
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "CC", "Heal"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
    ap_.add_argument("--set", nargs="*", default=[], help="key=value ...; ONE --set with every key (the last wins)")
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
