"""Build league_heimerdinger.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_heimerdinger.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-21: mid, layout A; all four spells and the passive; an add-on where data cannot).
TFM2 has three active slots: H-28G Evolution Turret (Q) is `skill`, CH-2 Electron Storm Grenade (E) `skill2`, UPGRADE!!!
(R) the `ult`; Hextech Micro-Rockets (W) ride the attack and Hextech Affinity (the passive) rides the turrets.
  turrets Data has no summons: a turret is zones on its spot for t_life ticks (league_zyra's plants), its picture one
          `ViewEffect` whose tag lasts that life. Three slots a / b / c (league_caitlyn's traps): Q takes the first
          whose `t<s>_busy` flag is gone, so at most three stand. A slot fires every t_per ticks at ONE enemy: three
          zones on the same spot, the first on `EnemyChampionInCC` (the beam, tb_dmg + tb_ratio% AP: League's charged
          beam, here at the champion E or R holds), then `EnemyChampion`, then `EnemyWithoutTower` (a cannon shot,
          t_dmg + t_ratio% AP); the first that reaches an enemy lays the slot's 1-tick `t<s>_shot`, the others read it.
  attack  a hextech bolt (100% AD) homing on `Enemy` (towers too), released on a_rel.
          W Hextech Micro-Rockets ride every third attack (flags a_one / a_two count them): w_n rockets w_gap ticks
          apart at the attack's target, w_dmg + w_ratio% AP each.
          Combo E -> W (the user: 「有连招要做连招」; League's Heimerdinger stuns with E and lands the whole W on the
          stunned champion): the grenade's champion-only twin opens the caster flag e_combo for e_combo ticks on a
          stun; the next attack inside it looks for a champion in crowd control within atk_range + 15000 (normally the
          one just stunned) and fires the rockets at him whatever the count (the count starts again).
  skill   Q H-28G Evolution Turret (H-28G 进化炮台), a `Direction` cast on `EnemyWithoutTower` (q_range): a hidden bolt
          flies q_place toward the target and the turret stands where it stops (t_first ticks to its first shot).
  skill2  E CH-2 Electron Storm Grenade (CH-2 电子风暴手雷), `Targeting` on `EnemyWithoutTower` (e_range): the grenade
          lands on the target's spot in e_travel ticks: e_dmg + e_ratio% AP and a e_slow% slow for e_slow_t ticks to
          every enemy within e_r, and a stun of e_stun ticks within e_sr (the direct hit).
  ult     R UPGRADE!!! (升级！！！), `Targeting` on `EnemyChampion` (r_range), by the situation round its target (a hidden
          zone counts the enemy champions within r_crowd of him, flags r_one / r_two):
          two or more - CH-3X Lightning Grenade: three grenades r_gap ticks apart on the target's spot, each
            re_dmg + re_ratio% AP and a re_slow% slow within re_r and a stun of re_stun ticks within re_sr;
          one - H-28Q Apex Turret: one big turret q_place in front of him for x_life ticks, firing every x_per ticks:
            x_dmg + x_ratio% AP and a x_slow% slow for x_slow_t ticks, the beam on a champion in crowd control.
  passive Hextech Affinity (海克斯科技亲和): every turret's aura (`AllyChampion` zone, radius p_r, every p_per ticks)
          asks `RandomTarget {AllyOnlySelf, from_projectile: true}` whether he stands in it (league_ekko's sphere) and
          gives him p_ms% move speed for p_t ticks.
The add-on copy (--native, addons/league_heimerdinger): the turrets keep their sounds and slots but lose their zones;
Q's `put` and R's apex run the add-on's `league_heimerdinger:q` / `:x` with the cast's input, which stand a native
turret where the hidden bolt stops (q_place toward it, q_place / q_speed ticks later) and lay `t_face_l` / `x_face_l`
on him when that is to his left: the bolt's end draws the turret from the side facing that way (TURRET_R / _L,
APEX_R / _L; the user: 「炮台改成侧面朝敌人」 - the main pack, which cannot tell the side, keeps the front ones). The add-on's passive
`league_heimerdinger:affinity` fires them on the zones' timing at the same targets (the beam on a champion in crowd
control, then the nearest champion, then the nearest unit) with visible shots flying from the muzzle (t_shot /
t_beam_line / x_shot at t_speed / b_speed / x_speed, the damage on arrival) and gives the haste near his turrets and
near his side's towers (p_tr) every p_per ticks.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_heimerdinger.data_champion")
ID = "league_heimerdinger"
FX = "asset/league/effects/league_heimerdinger_fx"
BIG = "asset/league/effects/league_heimerdinger_big"
TURRET = "asset/league/effects/league_heimerdinger_turret"   # Q's turret's life, dense (PPU 1.5, hd.rs EFFECTS; tag idle)
APEX = "asset/league/effects/league_heimerdinger_apex"       # R's apex turret's life, the same way
# the add-on's copy: the same lives seen from the side, muzzle right / left (PPU 3, hd.rs EFFECTS; tag idle)
TURRET_R, TURRET_L = TURRET + "_r", TURRET + "_l"
APEX_R, APEX_L = APEX + "_r", APEX + "_l"

# League units x 100 = ours (attack range 550 -> 55000 like every mid); radii count the unit's collision radius
# (~15000) on top. Timings from the frames (tools/art/rig_heimerdinger.py, after League's clips): the attack's jab
# 167 ms (a_rel 10), the crane firing W's rockets the same tick (attack_w, its own tag, played on the third attack and
# in the E -> W window), Q's turret set down and E's grenade flung at 267 ms (q_rel / e_rel 16) of 600 ms actions (36),
# R's gear bursting at 200 ms (r_up on tick 12), the upgrade on 14 of 40. Heights (a projectile starts 5000 - y_offset
# above the pivot, 1000 a game px; the pivot 11.5 px over the soles): the bolt leaves the wrench at the pivot's height
# (a_y), the rockets the crane's claw 41 px over it (w_y).
# Numbers = the 10-min classic-SDK simulations (mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and
# white_mage, three lineups, both sides, seeds 1-8, 2026-10-21): the draft (turrets 8 + 6% / beam 25 + 20%, E 80 + 60%
# with a 1.5 s stun, R cd 2100 with CH-3X 90 + 45% and the apex 25 + 15%) +4.03; single nerfs - turrets 6 + 4% / 18 +
# 14% +4.08, rockets 6 + 5% +4.01 (neither drives it), E 60 + 45% with a 1 s stun +2.76, R cd 3000 with 70 + 35% / 18 +
# 10% +3.24; the turret, E and R nerfs together +1.44 = P; on the frames' timings (Q / E 36 ticks releasing on 16, the
# rockets from the crane) +1.73 (+-0.46).
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's
    # Heimerdinger: 558 +105 hp, 19 armour, 30 mr, 340 move, 550 range, attack speed 0.658
    "hp": 860, "hp_g": 92, "atk": 58, "atk_g": 5, "apw": 40, "apw_g": 20, "def": 17, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 88, "a_rel": 10, "a_speed": 4500, "a_y": 5000, "w_y": -36000,
    # W Hextech Micro-Rockets on every third attack (League: 5 rockets, 50-150 + 55% AP, 90-270 on one champion)
    "w_n": 5, "w_gap": 3, "w_dmg": 10, "w_ratio": 7, "w_speed": 3500, "e_combo": 90, "w_reach": 15000,
    # Q turrets (League: 3 turrets, 525 range, 7-23 + 35% AP a shot, the beam 40-120 + 55% AP; placed within 350)
    "q_cd": 240, "q_range": 60000, "q_dur": 36, "q_rel": 16, "q_place": 20000, "q_speed": 4000,
    "t_life": 600, "t_per": 50, "t_first": 40, "t_r": 50000, "t_dmg": 6, "t_ratio": 4, "tb_dmg": 18, "tb_ratio": 14,
    # passive (League: 20% move speed near his turrets and allied towers)
    "p_r": 40000, "p_per": 20, "p_ms": 20, "p_t": 30,
    # E grenade (League: 970 range, 100-500... 60-220 + 60% AP, stun 1.5 s within 100, 35% slow 2 s within 210)
    "e_cd": 660, "e_range": 85000, "e_dur": 36, "e_rel": 16, "e_travel": 30, "e_r": 23000, "e_sr": 11000,
    "e_dmg": 60, "e_ratio": 45, "e_slow": 35, "e_slow_t": 120, "e_stun": 60,
    # R UPGRADE!!! (League: cd 100-70 s; CH-3X 150-500 + 60% AP, bounces three times; Apex Turret 8 s, 80-160 + 30%)
    "r_cd": 3000, "r_range": 75000, "r_dur": 40, "r_rel": 14, "r_up": 12, "r_crowd": 30000,
    "r_gap": 24, "re_r": 25000, "re_sr": 13000, "re_dmg": 70, "re_ratio": 35, "re_slow": 40, "re_slow_t": 90,
    "re_stun": 60,
    "x_life": 480, "x_per": 30, "x_first": 30, "x_r": 60000, "x_dmg": 18, "x_ratio": 10, "x_slow": 25, "x_slow_t": 45,
    "xb_dmg": 45, "xb_ratio": 30,
    "vo_gap": 600,
    # 1 = the copy for addons/league_heimerdinger; its shots' speeds (League: 1650 a turret's shot) and the towers' reach
    # for the passive
    "native": 0, "t_speed": 2800, "b_speed": 9000, "x_speed": 3500, "p_tr": 60000,
}
SLOTS = "abc"
# the numbers the add-on's passive reads (passive.params)
NATIVE_KEYS = ("q_place", "q_speed", "t_life", "t_per", "t_first", "t_r", "t_dmg", "t_ratio", "tb_dmg", "tb_ratio",
               "x_life", "x_per", "x_first", "x_r", "x_dmg", "x_ratio", "x_slow", "x_slow_t", "xb_dmg", "xb_ratio",
               "p_r", "p_tr", "p_per", "p_ms", "p_t", "t_speed", "b_speed", "x_speed")


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


def stun(tick):
    return {"type": "Stun", "duration": tick}


def pick(rng, target, *effects, here=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": here,
            "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def place(name, speed, rng, end):
    """A hidden bolt that flies rng toward the cast's direction and hits nothing: its end_effects run where it stops
    (league_caitlyn's traps b / c)."""
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": 0, "penetrate": True,
            "shape": circle(1), "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": list(end)}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, life, period, first, effects, target="EnemyWithoutTower"):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": life, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])

    def gun(shot, name, r, life, per, first, cannon, beam):
        """A turret's three zones (beam on a champion in crowd control, then a champion, then anything), one enemy
        a period: the first zone that reaches one lays `shot` for a tick and the others read it."""
        fire = lambda hit: sw(shot, NONE, combine(flag(shot, 1), *hit))
        return [field(name + "_cc", r, life, per, first, [fire(beam)], "EnemyChampionInCC"),
                field(name + "_ch", r, life, per, first, [fire(cannon)], "EnemyChampion"),
                field(name + "_all", r, life, per, first, [fire(cannon)]),
                field(name + "_aura", p["p_r"], life, p["p_per"], 0,
                      [pick(p["p_r"], "AllyOnlySelf", buff("haste", p["p_t"], move_speed_mult=p["p_ms"]), here=True)],
                      "AllyChampion")]

    cannon = [ap(p["t_dmg"], p["t_ratio"]), view("t_hit"), tsfx("t_hit")]
    beam = [ap(p["tb_dmg"], p["tb_ratio"]), view("t_beam"), tsfx("t_beam")]
    # the add-on's copy draws the turret from the side, facing where its native effect found the target (t_face_l)
    side = lambda k: sw(f"{k}_face_l", view(f"{k}_turret_l"), view(f"{k}_turret_r"))
    turret = lambda s: [side("t") if native else view("t_turret"), sfx("t_spawn"),
                        *([] if native else gun(f"t{s}_shot", f"t{s}", p["t_r"], p["t_life"], p["t_per"], p["t_first"],
                                                cannon, beam))]
    stand = (lambda k: [{"type": "Native", "effect_ref": f"league_heimerdinger:{k}"}]) if native else (lambda k: [])

    # ------------------------------------------------------------------ attack: the bolt, W's rockets every third
    def rockets(target):
        shots = [delayed(i * p["w_gap"], homing("w_rocket", target,
                                                 [ap(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")],
                                                 p["w_speed"], p["w_y"])) for i in range(p["w_n"])]
        return [sfx("w"), *shots]
    count = sw("a_two", combine(*rm("a_two"), *rockets("EnemyWithoutTower")),
               sw("a_one", combine(*rm("a_one"), flag("a_two", None)), flag("a_one", None)))
    # E -> W: inside e_combo the rockets go at a champion in crowd control (w_go: the search found him)
    combo = pick(p["atk_range"] + p["w_reach"], "EnemyChampionInCC", flag("w_go", 1), *rm("e_combo", "a_one", "a_two"),
                 *rockets("EnemyChampion"))
    bolt = combine(*rm("w_go"), sfx("a"), homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")],
                                                  p["a_speed"], p["a_y"]),
                   sw("e_combo", combo), sw("w_go", NONE, count))
    # the rockets' attack shows the crane (League's Spell2) from its first tick: the third attack (a_two), or the E -> W
    # window open
    crane = anim("attack_w", p["atk_dur"])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), sw("a_two", crane, sw("e_combo", crane)),
                              delayed(p["a_rel"] - 1, alive(bolt))), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q the turret, in the first free slot
    def slot(i):
        s = SLOTS[i]
        put = combine(flag(f"t{s}_busy", p["t_life"]), place("q_place", p["q_speed"], p["q_place"], turret(s)),
                      *stand("q"))
        return sw(f"t{s}_busy", NONE if i == len(SLOTS) - 1 else slot(i + 1), put)   # all three up: none
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(decoy(p["t_dmg"] * 4, p["t_ratio"] * 4, ap), sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive(slot(0)))))

    # ------------------------------------------------------------------ skill2: E the grenade
    blast = [view("e_blast"), sfx("e_land"),
             zone("e_storm", p["e_r"], [ap(p["e_dmg"], p["e_ratio"]),
                                        buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit")]),
             zone("e_core", p["e_sr"], [stun(p["e_stun"]), tsfx("e_stun")]),
             zone("e_hold", p["e_sr"], [refresh("e_combo", p["e_combo"])], "EnemyChampion")]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(lob("e_grenade", p["e_travel"], blast)))))

    # ------------------------------------------------------------------ ult: R UPGRADE!!! by the situation
    def storm(k):
        return [view("re_blast"), sfx("re_land"),
                zone(f"re_storm{k}", p["re_r"], [ap(p["re_dmg"], p["re_ratio"]),
                                                  buff("e_slow", p["re_slow_t"], move_speed_mult=-p["re_slow"]),
                                                  view("e_hit")]),
                zone(f"re_core{k}", p["re_sr"], [stun(p["re_stun"]), tsfx("e_stun")]),
                zone(f"re_hold{k}", p["re_sr"], [refresh("e_combo", p["e_combo"])], "EnemyChampion")]
    lightning = [sfx("re"), *(delayed(k * p["r_gap"], lob("re_grenade", p["e_travel"], storm(k), "EnemyChampion"))
                              for k in range(3))]
    xcannon = [ap(p["x_dmg"], p["x_ratio"]), buff("x_slow", p["x_slow_t"], move_speed_mult=-p["x_slow"]),
               view("x_hit"), tsfx("x_hit")]
    xbeam = [ap(p["xb_dmg"], p["xb_ratio"]), view("x_beam"), tsfx("t_beam")]
    apex = [sfx("rq"), place("q_place", p["q_speed"], p["q_place"],
                            [side("x") if native else view("x_turret"), sfx("x_spawn"),
                             *([] if native else gun("x_shot", "x", p["x_r"], p["x_life"], p["x_per"], p["x_first"],
                                                     xcannon, xbeam))]),
            *stand("x")]
    # the count: a lob onto the target starts a zone round him that adds r_one, then r_two (lob 1 tick + the zone's
    # delay 1); r_rel later two or more throw the storm
    count_r = zone("r_count", p["r_crowd"], [sw("r_one", flag("r_two", 6), flag("r_one", 6))], "EnemyChampion")
    choose = combine(sw("r_two", combine(*lightning), combine(*apex)), *rm("r_one", "r_two"))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["re_dmg"] * 2, p["re_ratio"] * 2, ap), sfx("r"), voice("vo_r", p),
                         delayed(p["r_up"], cview("r_up")),
                         *rm("r_one", "r_two"),
                         delayed(p["r_rel"] - 4, alive(lob("r_seek", 1, [count_r], "EnemyChampion"))),
                         delayed(p["r_rel"], alive(choose))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    views_p = [Pj("a_bolt"), Pj("w_rocket"), Pj("e_grenade"), Pj("re_grenade")] +         ([Pj("t_shot"), Pj("t_beam_line"), Pj("x_shot")] if native else [])
    # the turrets under the units (z -1) like the ground; the grenade's blasts there too
    views_e = [E("a_hit"), E("w_hit"), dict(E("t_turret", TURRET, -1, False), tag="idle"), E("t_hit"), E("t_beam"),
               E("e_blast", BIG, -1, False), E("e_hit"), E("re_blast", BIG, -1, False), E("r_up", BIG),
               dict(E("x_turret", APEX, -1, False), tag="idle"), E("x_hit"), E("x_beam")]
    if native:
        views_e += [dict(E(f"{k}_turret_{d}", sheet, -1, False), tag="idle")
                    for k, d, sheet in (("t", "r", TURRET_R), ("t", "l", TURRET_L), ("x", "r", APEX_R), ("x", "l", APEX_L))]
    views_b = [B_("e_slow", FX, -1), dict(B_("x_slow", FX, -1), tag="e_slow"), B_("haste", FX, -1)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_heimerdinger:affinity", "params": {
            k: int(p[k]) for k in NATIVE_KEYS}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"], **extra,
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
