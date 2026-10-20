"""Build league_gnar.data_champion (top, Melee, Mini / Mega forms) from the parameters P.

    python tools/kit/build_gnar.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: top, layout A, with the add-on; 「有连招要做连招」). TFM2 has three active slots:
Boomerang Throw / Boulder Toss (Q) is `skill`, Hop / Crunch (E) with Mega's Wallop (W) `skill2`, GNAR! (R) the `ult`;
Mini's Hyper (W) rides the attack. The forms work like league_nidalee's: every action reads her form buffs first.
  forms   Mini Gnar (迷你纳尔, every life starts Mini): a ranged boomerang attack (atk_range + mini_add: the permanent
          caster buff `mi` - a range buff cannot be negative, so the bare reach is Mega's melee one). Mega Gnar (巨型纳尔):
          the caster buff `mg` for mega_t ticks (League: 15 s) with mg_hp% health, mg_def% armour, mg_mr% magic
          resistance and mg_atk% attack; every action plays Mega's own tags (m_*, CasterAnimation; idle, run, hit and
          death are Mega only with the add-on). When `mg` runs out the next action puts `mi` back - the attack plays
          the turn back (`revert`) instead of a swing - and Rage is locked for lock_t ticks (`rl`).
  passive Rage Gene (狂怒基因): while Mini and not locked, each attack hit, each enemy the boomerang hits and each Hop
          landing is one step of Rage (rg1 -> rg2 -> rg3 -> `full`, each step lasts rage_t ticks: out of a fight it
          drains). With `full` the next action turns him Mega: an attack plays the transform (`transform`, tf_dur
          ticks); a skill turns him at once and casts its Mega version (League's *_trans clips: the spell and the change
          in one); R at full Rage turns him and throws in the same cast.
  attack  Mini: the small boomerang thrown at the target (released on a_rel). Hyper (亢奋): every third throw adds w_dmg
          and, on a champion, w_hp% of its max health, and gives him w_ms% move speed for w_ms_t ticks. Mega: a punch
          (m_rel). Both 100% AD, on `Enemy` (towers too).
  skill   Q, one cooldown for both forms (`q_cd`). Boomerang Throw (投掷回力标, Mini): out q_range and back to him
          through everything: q_dmg + q_ratio% AD and a q_slow% slow each pass; caught on his return its cooldown
          becomes q_catch ticks (League: -40%). Out is a penetrating line, back a `BackToCasterLinearProjectile` from
          where it stopped (league_ekko Q's way: one started at him would fly from him to him). Boulder Toss (投掷顽石, Mega): the boulder stops on the first enemy (or at
          q2_range): q2_dmg + q2_ratio% AD and a q2_slow% slow round it (q2_r); it lies there pick_t ticks and he picks
          it up by walking over it (pick_r): its cooldown becomes q_pick ticks (League: -70%).
  skill2  Hop / Crunch (轻跳 / 猛踏, one cooldown `e_cd`) and Mega's Wallop (痛殴, `w_cd`). Hop (Mini): onto the target's
          head and on past it (League's bounce): e_dmg + e_hp% of his max health and an e_slow% slow on it. Crunch
          (Mega): a leap onto the target, c_dmg + c_hp% of his max health and a c_slow% slow round the landing (c_r) -
          then Wallop at once if it is ready (the pros' E -> W). Crunch cooling down and an enemy within w_reach:
          Wallop alone - he rears up and smashes the ground in front: w2_dmg + w2_ratio% AD and a w2_stun-tick stun.
  ult     GNAR! (呐啊！, level 5): `Targeting` on `EnemyChampion` within r_range; Mega's alone, as in League (the user:
          「放大招是攒满怒气吗 要和英雄联盟一样」) - Mini at full Rage turns first and throws them in the same cast, Mini short
          of it casts nothing: the ult comes back r_wait ticks later (ult_cooldown_mult for 2 ticks caps its cooldown),
          or at once when he turns Mega before that (r_arm: the empty cast would have spent a whole cooldown). He throws
          everything round him (r_r) away: r_dmg + r_ratio% AD, knocked back (r_kb speed, r_kb_t ticks), stunned r_stun
          ticks and slowed r_slow% for r_slow_t (the data cannot see walls: every target is stunned; the add-on stuns
          only those thrown into a wall, with r_wall% damage). Then Wallop if ready and Boulder Toss if ready at the
          champion (the pros' R -> W -> Q).
  combos  E -> W (猛踏接痛殴), R -> W -> Q (大招接痛殴接顽石), Q catch (接回力标) and the boulder pick-up (捡石头), the
          transform spell (满怒放技能直接变身放巨型技能).
The add-on copy (--native, addons/league_gnar): GNAR! throws everyone the same way, r_push far - the way that slams
most of them into a wall (league_gnar:wall) - and only those that hit a wall are stunned r_stun ticks and take r_wall% of
R's damage in all (its passive league_gnar:slam, the moment they arrive); the whole body Mega while `mg` holds (its view
code).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_gnar.data_champion")
ID = "league_gnar"
FX = "asset/league/effects/league_gnar_fx"
BIG = "asset/league/effects/league_gnar_big"

# League's Gnar (16.20): 540 +79 hp, 60 AD, 32 armour, 30 mr, 335 move, range 175 (Mini grows to ~400). Mega: +100-831
# hp, more armour and mr. Q Boomerang 5-165 + 115% AD, slow 15-35% 2 s, range 1100, catch -40% cd; Boulder 45-245 +
# 140% AD, slow 30-50%, pick-up -70% cd; cd 16-10. W Hyper: third hit 0-40 + 6-14% max hp; Wallop 25-145 + 100% AD,
# stun 1.25 s, cd 7. E Hop 50-190 + 6% max hp, slow 80% 0.5 s, 475 range, cd 22-12; Crunch the same round him. R GNAR!
# 200-400 + 50% bonus AD + 100% AP, 590 round him, slow 60%; into a wall stun 1.25-1.75 s and 150% damage; cd 90-30.
# Ticks from the frames (tools/art/rig_gnar.py MS, every action as long as its frames): Mini's attack 400 ms, the
# boomerang leaves on frame 3 (150 ms, a_rel 10); Mega's punch 500 ms, the fist lands on frame 4 (240 ms, m_rel 15); the
# transform 450 ms, the turn back 430 ms; Boomerang Throw 570 ms, the throw on frame 4 (230 ms, q_rel 15); Boulder Toss
# 550 ms, the throw on frame 4 (280 ms, q2_rel 18); Hop 520 ms, off on frame 2 (60 ms, e_go 4); Crunch 580 ms, off on
# frame 2 (70 ms, c_go 5), the landing slam on frame 6 (370 ms, c_land 22); Wallop 550 ms, the smash on frame 4 (270 ms,
# w_at 17); GNAR! 510 ms, the throw on frame 3 (160 ms, r_at 11).
# Numbers = the 10-min classic-SDK simulations (top lane 0 against fighter, executioner, lancer, pole_warrior, knight and
# berserker, three lineups, both sides, 2026-10-20; C:/t/gn_sim): the draft g0 +1.19 / +1.62 (seeds 1-8 / 9-16; base
# knight +0.39); on the frames' timings +1.22 / +0.11; Mega's attack +22% (was +15) +0.88 / +1.24 = P (Boomerang 38,
# Boulder 72, Crunch 72 instead: +0.62 / +0.33; attack +20% with Boomerang 36, Boulder 68: +1.29 / +0.40)). GNAR! made Mega's alone
# as in League (the user: 「放大招是攒满怒气吗 要和英雄联盟一样」): -0.22 / -0.09; Mini's empty cast waiting 10 s, armed
# on the turn: -0.53 / -0.31; Rage locked 4 s (was 8) +0.02 avg; with Mega's attack +30%: +0.64 / -0.05; Mega's attack
# +30% and health +40%: +0.88 / -0.17; all three: +0.24 / +0.22 (attack +34%: +0.04 / +0.08; R 210: -0.01 / +0.34;
# base attack 90: -0.33 / +0.34); on those, base attack 90 and health 1000 (was 86 / 960) = P: +0.77 / +0.90 (Mega 18 s:
# +0.61 / +0.51; Mega's armour and magic resist +55%: +0.96 / +0.10).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, def 30, mr 25, move 1000, range 25000, attack cd 65)
    "hp": 1000, "hp_g": 98, "atk": 90, "atk_g": 17, "mp": 0, "mp_g": 0, "def": 26, "def_g": 8, "mr": 22, "mr_g": 4,
    "ms": 1050, "ms_g": 12,
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 58, "a_rel": 10, "a_speed": 5000,
    # the forms
    "mini_add": 17000, "mega_t": 900, "mg_hp": 40, "mg_def": 40, "mg_mr": 40, "mg_atk": 30, "lock_t": 240,
    "tf_dur": 27, "rv_dur": 26, "m_atk_dur": 30, "m_rel": 15,
    # Rage Gene
    "rage_t": 420,
    # W Hyper (every third throw)
    "w_dmg": 20, "w_hp": 5, "w_ms": 25, "w_ms_t": 90, "hy_t": 210,
    # Q Boomerang Throw / Boulder Toss
    "q_cd": 540, "q_range": 70000, "q_dur": 34, "q_rel": 15, "q_speed": 3500, "q_w": 6000,
    "q_dmg": 30, "q_ratio": 70, "q_slow": 25, "q_slow_t": 120, "q_catch": 240,
    "q2_range": 65000, "q2_dur": 33, "q2_rel": 18, "q2_speed": 4000, "q2_w": 7000, "q2_r": 16000,
    "q2_dmg": 60, "q2_ratio": 120, "q2_slow": 40, "q2_slow_t": 120, "pick_t": 180, "pick_r": 9000, "q_pick": 120,
    # E Hop / Crunch, W Wallop
    "s2_cd": 60, "e_cd": 660, "e_range": 45000, "e_dur": 31, "e_go": 4, "e_speed": 3500,
    "e_dmg": 40, "e_hp": 4, "e_slow": 60, "e_slow_t": 30,
    "c_dur": 35, "c_go": 5, "c_land": 22, "c_speed": 3000, "c_r": 18000, "c_dmg": 60, "c_hp": 6, "c_slow": 60, "c_slow_t": 40,
    "w_cd": 420, "w_reach": 26000, "w_dur": 33, "w_at": 17, "w_off": 12000, "w_rad": 14000,
    "w2_dmg": 40, "w2_ratio": 100, "w2_stun": 72,
    # R GNAR!
    "r_cd": 2700, "r_range": 26000, "r_dur": 31, "r_at": 11, "r_r": 30000, "r_dmg": 170, "r_ratio": 60,
    "r_kb": 1500, "r_kb_t": 8, "r_stun": 70, "r_slow": 50, "r_slow_t": 90, "r_wall": 150,
    # the add-on's throw: everyone the same way (the way that slams most of them into a wall), r_push far at r_push_v
    "r_push": 30000, "r_push_v": 3000,
    # Mini short of full Rage: the empty cast's cooldown cut to r_wait ticks; turning Mega within them makes the ult
    # ready at once (r_arm: ult_cooldown_mult r_arm_mult for 2 ticks caps the cooldown left at a tick)
    "r_wait": 600, "r_arm_mult": 270000,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_gnar: R's stun only on a wall (native effect league_gnar:wall)
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


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


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


def attack(dmg, ratio, hp=0, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def ahead(offset, radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": {"Forward": {"offset": offset}},
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, from_projectile=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": from_projectile,
            "effects": [e for e in effects if e is not None]}


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def back(name, speed, rng, radius, target, effects, end=()):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius)}


def zone(name, radius, delay, apply, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    slow = lambda name, pct, t: buff(name, t, move_speed_mult=-pct)

    # ------------------------------------------------------------------ the forms and Rage Gene
    # one step of Rage (Mini, not locked); written once and carried by every hit that gains it
    gain = sw("mg", NONE, sw("rl", NONE, sw("full", NONE, sw(
        "rg3", combine(*rm("rg3"), flag("full", p["rage_t"]), sfx("full")), sw(
            "rg2", combine(*rm("rg2"), flag("rg3", p["rage_t"])), sw(
                "rg1", combine(*rm("rg1"), flag("rg2", p["rage_t"])), flag("rg1", p["rage_t"])))))))
    to_mega = combine(*rm("full", "rg1", "rg2", "rg3", "hy1", "hy2", "mi"), flag("was_mg", None),
                      flag("mg", p["mega_t"], hp_mult=p["mg_hp"], defence_mult=p["mg_def"],
                           magic_resistance_mult=p["mg_mr"], attack_mult=p["mg_atk"]),
                      sw("r_wait", combine(*rm("r_wait"), flag("r_arm", 2, ult_cooldown_mult=p["r_arm_mult"]))),
                      cview("tf_mega"), sfx("tf_mega"), voice("vo_mega", p))
    # Mega ran out (or a new life): Mini's reach back; after a Mega spell Rage is locked and `rv` asks the attack to
    # play the turn back
    restore = sw("mg", NONE, sw("mi", NONE, combine(flag("mi", None, range=p["mini_add"]),
                                                     sw("was_mg", combine(*rm("was_mg"), flag("rl", p["lock_t"]),
                                                                          flag("rv", 1), cview("tf_mini"),
                                                                          sfx("tf_mini"))))))
    revert = combine(*rm("rv"), anim("revert", p["rv_dur"]))
    # a spell at full Rage: he turns first and the same run casts the Mega spell (to_mega lays `mg` before it is read)
    rage_turn = sw("mg", NONE, sw("full", to_mega))

    # ------------------------------------------------------------------ attack
    mini_hit = [attack(0, 100), gain, view("a_hit"), tsfx("a_hit")]
    hyper_hit = [attack(p["w_dmg"], 100), gain, view("a_hyper"), tsfx("a_hyper")]
    hyper = combine(*rm("hy2"), on_me(refresh("hyper", p["w_ms_t"], move_speed_mult=p["w_ms"])),
                    delayed(p["a_rel"] - 1, homing("a_boom", p["a_speed"], "Enemy", hyper_hit),
                            homing("a_twin", p["a_speed"], "EnemyChampion", [attack(0, 0, target_hp=p["w_hp"])])))
    plain = combine(sw("hy1", combine(*rm("hy1"), flag("hy2", p["hy_t"])), flag("hy1", p["hy_t"])),
                    delayed(p["a_rel"] - 1, homing("a_boom", p["a_speed"], "Enemy", mini_hit)))
    mini_atk = combine(sfx("a"), sw("hy2", hyper, plain))
    mega_atk = combine(anim("m_attack", p["m_atk_dur"]), sfx("m_a"),
                       delayed(p["m_rel"] - 1, homing("m_fist", 100000, "Enemy",
                                                      [attack(0, 100), view("m_hit"), tsfx("m_hit")])))
    transform = combine(to_mega, anim("transform", p["tf_dur"]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(restore, sw("rv", revert, sw("mg", mega_atk, sw("full", transform, mini_atk)))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Boomerang Throw / Boulder Toss
    boomerang_hits = [attack(p["q_dmg"], p["q_ratio"]), slow("q_slow", p["q_slow"], p["q_slow_t"]), gain,
                      view("q_hit"), tsfx("q_hit")]
    catch = [refresh("q_cd", p["q_catch"]), cview("q_catch"), sfx("q_catch")]
    boomerang = combine(refresh("q_cd", p["q_cd"]), anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p),
                        delayed(p["q_rel"] - 1, line("q_boom", p["q_speed"], p["q_range"], p["q_w"],
                                                     "EnemyWithoutTower", True, boomerang_hits,
                                                     [back("q_back", p["q_speed"], p["q_range"], p["q_w"],
                                                           "EnemyWithoutTower", boomerang_hits, catch)])))
    # the pick-up: the rock's spot asks every few ticks whether he stands on it (league_ekko W's "is the caster in
    # this zone"); picked once (q_got), the cooldown left becomes q_pick
    pickup = pick(p["pick_r"], "AllyOnlySelf",
                  sw("q_got", NONE, combine(flag("q_got", p["pick_t"]), refresh("q_cd", p["q_pick"]), cview("q_pick"),
                                            sfx("q_pick"))), from_projectile=True)
    landing = [zone("q_smash", p["q2_r"], 2, 1, "EnemyWithoutTower",
                    [attack(p["q2_dmg"], p["q2_ratio"]), slow("q2_slow", p["q2_slow"], p["q2_slow_t"]),
                     view("q2_hit"), tsfx("q2_hit")]),
               view("q_rest"), sfx("q_land"),
               field("q_spot", 1000, p["pick_t"], 3, "AllyChampion", [pickup])]

    def boulder(tag):
        return combine(*rm("q_got"), refresh("q_cd", p["q_cd"]), anim(tag, p["q2_dur"]), sfx("q2"),
                       voice("vo_big", p),
                       delayed(p["q2_rel"] - 1, line("q_rock", p["q2_speed"], p["q2_range"], p["q2_w"],
                                                     "EnemyWithoutTower", False, [], landing)))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(restore, sw("q_cd", NONE, combine(rage_turn, sw("mg", boulder("m_skill"), boomerang)))),
                   key="skill")

    # ------------------------------------------------------------------ skill2: Hop / Crunch -> Wallop
    def wallop(at):
        """Wallop on an enemy within w_reach, its smash at+w_at ticks on (League's rectangle: a circle ahead)."""
        smash = ahead(p["w_off"], p["w_rad"], "EnemyWithoutTower",
                      [attack(p["w2_dmg"], p["w2_ratio"]), {"type": "Stun", "duration": p["w2_stun"]},
                       view("w_hit"), tsfx("w_hit")])
        return pick(p["w_reach"], "EnemyWithoutTower",
                    combine(refresh("w_cd", p["w_cd"]), delayed(at, anim("m_wallop", p["w_dur"]), sfx("w"),
                                                                voice("vo_big", p)),
                            delayed(at + p["w_at"] - 1, smash, cview("w_quake"), sfx("w_land"))))
    hop = combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                  delayed(p["e_go"] - 1, {"type": "RushMoveToBack", "speed": p["e_speed"],
                                          "applied_effects": [attack(p["e_dmg"], 0, hp=p["e_hp"]),
                                                              slow("e_slow", p["e_slow"], p["e_slow_t"]), gain,
                                                              view("e_hit"), tsfx("e_hit")]}))
    crunch_land = [around(p["c_r"], "EnemyWithoutTower",
                          [attack(p["c_dmg"], 0, hp=p["c_hp"]), slow("c_slow", p["c_slow"], p["c_slow_t"]),
                           view("c_hit"), tsfx("c_hit")]),
                   cview("c_slam"), sfx("c_land"), sw("w_cd", NONE, wallop(0))]
    # the leap carries him onto the target; the slam comes on the frames' landing (c_land), wherever the leap ended
    crunch = combine(refresh("e_cd", p["e_cd"]), anim("m_skill2", p["c_dur"]), sfx("c"), voice("vo_big", p),
                     delayed(p["c_go"] - 1, {"type": "MoveToTarget", "speed": p["c_speed"],
                                             "range": p["e_range"] + 30000, "end_effects": []}),
                     delayed(p["c_land"] - 1, *crunch_land))
    mega_s2 = sw("e_cd", sw("w_cd", NONE, wallop(0)), crunch)
    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(restore, rage_turn, sw("mg", mega_s2, sw("e_cd", NONE, hop))), key="skill2")

    # ------------------------------------------------------------------ ult: GNAR! -> Wallop -> Boulder
    # the add-on's copy throws them itself (the push, then a wall check: stun and r_wall% damage on a wall)
    thrown = ([{"type": "Native", "effect_ref": f"{ID}:wall"}] if p["native"] else
              [{"type": "Knockback", "speed": p["r_kb"], "tick": p["r_kb_t"]}, {"type": "Stun", "duration": p["r_stun"]}])
    r_hits = [attack(p["r_dmg"], p["r_ratio"]), *thrown, slow("r_slow", p["r_slow"], p["r_slow_t"]), view("r_hit"),
              tsfx("r_hit")]
    follow = combine(sw("w_cd", NONE, wallop(0)),
                     delayed(p["w_dur"], sw("q_cd", NONE, boulder("m_skill"))))
    gnar = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                   delayed(p["r_at"] - 1, around(p["r_r"], "EnemyWithoutTower", r_hits), cview("r_wave"),
                           sfx("r_land")),
                   delayed(p["r_dur"] - 1, pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", follow),
                           *rm("lives")))
    # League's GNAR! is Mega's alone: Mini at full Rage turns first and throws them in the same cast; Mini short of it
    # casts nothing and gets the ult back r_wait ticks later, or as he turns Mega (`r_wait` ends 10 ticks before the
    # cooldown does and every cast takes it off first, so it never cuts a real cooldown)
    wait_mult = -(-p["r_cd"] * 100 // p["r_wait"]) - 100
    not_yet = combine(flag("r_back", 2, ult_cooldown_mult=wait_mult), flag("r_wait", p["r_wait"] - 10))
    r_go = combine(restore, *rm("r_wait"), sw("mg", NONE, sw("full", to_mega, not_yet)), sw("mg", gnar))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", r_go, key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("a_boom"), P_("q_boom"), P_("q_back", FX, 1), P_("q_rock")]
    views_e = [E("a_hit"), E("a_hyper"), E("m_hit"), E("q_hit"), E("q_catch", FX, 3), E("q2_hit"),
               E("q_rest", FX, -1, False), E("q_pick", FX, 3), E("e_hit"), E("c_slam", BIG, -1, False), E("c_hit"),
               E("w_quake", BIG, -1), E("w_hit"), E("r_wave", BIG, -1, False), E("r_hit"), E("tf_mega", BIG, 3), E("tf_mini", BIG, 3)]
    views_b = [B_("full", FX, 3), B_("hyper", FX, -1), B_("q_slow", FX, 3), B_("q2_slow", FX, 3)]
    # the add-on's copy: its passive lands the wall slams (stun and the extra damage the moment a thrown enemy arrives)
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": f"{ID}:slam", "params": {
            k: p[k] for k in ("r_dmg", "r_ratio", "r_stun", "r_wall", "r_r", "r_push", "r_push_v")}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Range", "Tank", "CC"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
    ap_.add_argument("--native", action="store_true")
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
