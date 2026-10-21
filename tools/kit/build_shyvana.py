"""Build league_shyvana.data_champion (jungle, Melee: the Half-Dragon, human and dragon forms) from the parameters P.

    python tools/kit/build_shyvana.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (group F jungle, 2026-10-21; League 16.20's reworked Shyvana; layout A - Q / E / R, the passive and W in the
attack -; 「有连招要做连招」). TFM2 has three active slots: Emberstrike (Q) is `skill`, Molten Burst (E) `skill2`,
Dragon's Descent (R) the `ult`; Inferno Aegis (W) rides the attack every w_cd ticks. The forms work like league_gnar's:
every action reads the dragon buff `dg` first and plays the form's own tags (d_*, CasterAnimation; idle, run, hit and
death stay human in the main pack - a whole-body dragon needs an add-on's view code, league_gnar's way).
  passive Scalemail (龙鳞铁衣): League stacks armour and magic resistance on takedowns. No data effect sees a takedown
          cheaply (the kill trigger needs a champion twin on every hit), so the main pack folds it into the dragon:
          `dg` carries dg_def% armour and dg_mr% magic resistance next to dg_hp% health and dg_range more reach.
  fury    Dragon Fury (龙怒, R's passive): while human, each attack hit, each Emberstrike strike, each Molten Burst and
          each Aegis blast is one step of Fury (fy1 .. fy<fury_n - 1>, then `full`; each step lasts fury_t ticks, so
          out of a fight it drains). League drains the dragon's Fury over time: here the dragon lasts dg_t ticks.
  attack  Human: a sword-claw strike. Dragon: a claw (d_attack). Both 100% AD on `Enemy` plus Emberstrike's passive
          (League: 1% of the target's max health on-hit, magic; physical here - no magic effect reads max health).
          The attack is also Emberstrike's recast (below) and carries Inferno Aegis.
  W       Inferno Aegis (烈火圣盾), no slot of its own: the first attack after w_cd ticks wraps her in flames - a shield
          of w_sh + w_sh_r% AD and w_ms% move speed (`w_on`) for w_t ticks, then the flames blow up round her (w_r):
          w_dmg + w_hp% of her max health magic. In dragon form a blast that reaches an enemy champion heals her
          w_heal + w_heal_r% AD (League: base + 200% of the missing health; no data heal reads missing health). League
          also blows it up early when the shield breaks or on the recast: here only at the end.
  skill   Q Emberstrike (焚焰打击, one cooldown `q_cd`): a `Targeting` cast on `EnemyWithoutTower` (camps and waves too).
          The first strike cleaves ahead through the target (q_off / q_rad): q_dmg + q_ratio% AD. COMBO (League's
          recasts): for q_win ticks her next attack is the second strike instead - a slam round her (q2_r), q2_dmg +
          q2_ratio% AD (`q2`); in dragon form the second strike opens a third (`q3`): her next attack bites the target
          for q3_dmg + q3_ratio% AD true damage. Human: Spell1_Attack1 -> Spell1_Attack2; dragon: Spell1_Wing ->
          Spell1_Tail -> Spell1_Bite.
  skill2  E Molten Burst (爆炎吐息, one cooldown `e_cd`): a `Targeting` cast on `EnemyWithoutTower` (e_range). Human: a
          fireball that stops on the first enemy (or at e_range) and bursts (e_r): e_dmg + e_hp% of her max health
          magic and an e_slow% slow for e_slow_t. Dragon: bigger, flies through everyone (de_range, de_w) burning each
          enemy it passes, bursts at its end (de_r: de_dmg + de_hp% magic, the slow) and leaves the ground there
          burning for de_burn_t ticks (League's trail: the burn lies at the end, a zone cannot follow the path).
  ult     R Dragon's Descent (魔龙降世): a `Targeting` cast on `EnemyChampion` within r_cast; only at full Fury, as in
          League. Short of it she casts nothing and the ult comes back r_wait ticks later (ult_cooldown_mult caps its
          cooldown, league_gnar's empty cast). At full Fury she turns dragon (`dg` for dg_t ticks), is unstoppable
          (`cc_immune`) for r_imm ticks and flies onto the champion (`MoveToTarget`) breathing fire along the way: a
          line at her speed burning every enemy under it for r_dmg + r_hp% of her max health magic and making it flee
          (`Fear` r_fear). COMBO on the landing (the pros' R -> W -> Q): Inferno Aegis at once if it is ready, and the
          dragon's Emberstrike r_q ticks later if Q is ready (so Wing -> Tail -> Bite follows on her next attacks).
  combos  Q -> attack -> attack (焚焰打击三段：翼击 / 尾扫 / 撕咬), R -> W -> Q (魔龙降世接烈火圣盾接焚焰打击).
When `dg` runs out her next action turns her back (the attack plays `revert`) and an unfinished Q chain is dropped.
Timings: from the frames (tools/art/rig_shyvana.py MS; a frame's start in ticks = ms x 0.06), each form its own - the
hit, the strike or the release where its frame starts (a_hit / d_rel, q_at / d_q_at, q2_at / d_q2_at, q3_at, e_rel /
de_rel, r_at); numbers: drafts from Warwick's and Gnar's balanced kits (no simulation run yet: the classic-SDK sim
folders were all cleaned up).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_shyvana.data_champion")
ID = "league_shyvana"
FX = "asset/league/effects/league_shyvana_fx"
BIG = "asset/league/effects/league_shyvana_big"

# League's Shyvana (16.20, the rework; CommunityDragon shyvana.bin): 625 +95 hp, 62 AD, 35 +4 armour, 32 +2.05 mr, 350
# move, 150 range, attack speed 0.638. Q Emberstrike: on-hit 1% max health magic (cd -0.5 s an attack), the strike 5-35 +
# 110% AD (a 450 cleave), the recast 275 round her, the dragon's bite true damage; recasts within 4 s; cd 10-6 s.
# W Inferno Aegis: 2.5 s, shield 40-160 + 12% max health, 25% move speed (x1.75 toward champions), the blast 60-180
# magic in 350; the dragon heals on a champion hit; cd 13-10 s. E Molten Burst: 800 range, 35-125 + 5% max health magic,
# 30% slow 2 s; the dragon's x1.25, 300 burst, the trail 2 s; cd 12-8 s. R Dragon's Descent: 1050 range, 50-650 magic,
# 0.75 s fear, unstoppable; the dragon +50-650 health, size, +0-150 range; Fury drains 6.67 a second.
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30, mr 25, move 1000, range 25000, attack cd 65; the base
    # junglers 120 +30, hp 900 +80, move 1100 +14; league_warwick 92 +18, hp 1120 +105, def 36 +7)
    "hp": 1080, "hp_g": 100, "atk": 90, "atk_g": 18, "def": 34, "def_g": 7, "mr": 26, "mr_g": 4, "ms": 1050, "ms_g": 12,
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 62, "a_hit": 9, "a_speed": 20000,
    "p_hp": 1,
    # the dragon (Scalemail folded in)
    "dg_t": 900, "dg_hp": 30, "dg_def": 30, "dg_mr": 30, "dg_range": 10000,
    "d_atk_dur": 30, "d_rel": 14, "rv_dur": 26,
    # Dragon Fury
    "fury_n": 10, "fury_t": 360,
    # W Inferno Aegis (in the attack)
    "w_cd": 720, "w_t": 150, "w_sh": 70, "w_sh_r": 50, "w_ms": 25, "w_r": 33000, "w_dmg": 50, "w_hp": 4,
    "w_heal": 50, "w_heal_r": 50,
    # Q Emberstrike
    "s_cd": 60, "q_cd": 480, "q_range": 30000, "q_dur": 28, "q_at": 11, "d_q_at": 15, "q_off": 12000,
    "q_rad": 16000, "q_dmg": 25, "q_ratio": 90, "q_win": 240,
    "q2_dur": 30, "q2_at": 12, "d_q2_at": 16, "q2_r": 26000, "q2_dmg": 25, "q2_ratio": 90,
    "q3_dur": 32, "q3_at": 16, "q3_dmg": 40, "q3_ratio": 110,
    # E Molten Burst
    "s2_cd": 60, "e_cd": 600, "e_range": 70000, "e_dur": 28, "e_rel": 7, "de_rel": 16, "e_speed": 3000, "e_w": 6000,
    "e_r": 15000, "e_dmg": 50, "e_hp": 3, "e_slow": 30, "e_slow_t": 120,
    "de_range": 90000, "de_w": 10000, "de_r": 30000, "de_dmg": 65, "de_hp": 4, "de_burn_t": 120, "de_burn": 15,
    "de_burn_r": 15000,
    # R Dragon's Descent
    "r_cd": 1800, "r_cast": 90000, "r_dur": 36, "r_at": 10, "r_speed": 3500, "r_w": 18000, "r_imm": 40,
    "r_dmg": 100, "r_hp": 4, "r_fear": 45, "r_q": 20, "r_wait": 600,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
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


def attack(dmg, ratio, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def magic(dmg, hp=0):
    """Magic damage: dmg + hp% of HER max health (ApAttack's hp_ratio is the caster's; she has no ability power)."""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": hp, "can_crit": False}


def true(dmg, ratio):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0}


def heal(amount, ratio=0):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def ahead(offset, radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": {"Forward": {"offset": offset}},
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while she lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def zone(name, radius, delay, apply, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def form(dragon, human):
    """The dragon's version while `dg` holds, the human's otherwise."""
    return sw("dg", dragon, human)


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    slow = lambda name, pct, t: buff(name, t, move_speed_mult=-pct)

    # ------------------------------------------------------------------ Dragon Fury and the forms
    # fury_n steps to full Fury (fy1 .. fy<fury_n - 1>, then `full`), each a caster buff of fury_t ticks; written once
    # and carried by every hit that gains it (league_gnar's Rage ladder)
    steps = [f"fy{k}" for k in range(1, int(p["fury_n"]))]
    ladder = flag(steps[0], p["fury_t"])
    for k, name in enumerate(steps):
        nxt = combine(*rm(name), flag("full", p["fury_t"]), sfx("full")) if k == len(steps) - 1 else \
            combine(*rm(name), flag(steps[k + 1], p["fury_t"]))
        ladder = sw(name, nxt, ladder)
    gain = sw("dg", NONE, sw("full", NONE, ladder))
    to_dragon = combine(*rm("full", *steps), flag("was_dg", None),
                        flag("dg", p["dg_t"], hp_mult=p["dg_hp"], defence_mult=p["dg_def"],
                             magic_resistance_mult=p["dg_mr"], range=p["dg_range"]),
                        cview("tf_dragon"), sfx("tf_dragon"))
    # the dragon ran out: the next action turns her back (`rv` asks the attack to play it) and drops a Q chain left open
    restore = sw("dg", NONE, sw("was_dg", combine(*rm("was_dg", "q2", "q3"), flag("rv", 1), cview("tf_human"),
                                                  sfx("tf_human"))))
    revert = combine(*rm("rv"), anim("revert", p["rv_dur"]))

    # ------------------------------------------------------------------ W Inferno Aegis
    def aegis():
        blast = combine(around(p["w_r"], "EnemyWithoutTower", [magic(p["w_dmg"], p["w_hp"]), view("w_hit"),
                                                               tsfx("w_hit")]),
                        cview("w_blast"), sfx("w_blast"), gain,
                        form(pick(p["w_r"], "EnemyChampion", on_me(heal(p["w_heal"], p["w_heal_r"]), cview("w_heal"), sfx("w_heal"))),
                             None))
        return combine(refresh("w_cd", p["w_cd"]), on_me(shield(p["w_sh"], p["w_sh_r"], p["w_t"])),
                       refresh("w_on", p["w_t"], move_speed_mult=p["w_ms"]), sfx("w"),
                       delayed(p["w_t"], alive(blast)))
    w_part = sw("w_cd", NONE, aegis())

    # ------------------------------------------------------------------ Q Emberstrike: the first strike (the skill)
    def q1():
        cleave = ahead(p["q_off"], p["q_rad"], "EnemyWithoutTower",
                       [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")])
        return combine(refresh("q_cd", p["q_cd"]), *rm("q3"), refresh("q2", p["q_win"]),
                       form(combine(anim("d_skill", p["q_dur"]), sfx("d_q")), combine(anim("skill", p["q_dur"]), sfx("q"))),
                       voice("vo_q", p),
                       form(delayed(p["d_q_at"] - 1, cleave, gain), delayed(p["q_at"] - 1, cleave, gain)))

    # ------------------------------------------------------------------ attack (and Q's recasts)
    on_hit = [attack(0, 100, p["p_hp"]), gain, view("a_hit"), tsfx("a_hit")]
    human_atk = combine(sfx("a"), delayed(p["a_hit"] - 1, homing("a_claw", p["a_speed"], "Enemy", on_hit)))
    dragon_atk = combine(anim("d_attack", p["d_atk_dur"]), sfx("d_a"),
                         delayed(p["d_rel"] - 1, homing("d_claw", p["a_speed"], "Enemy", on_hit)))
    # the second strike: a slam round her; the dragon's opens the bite
    q2_slam = around(p["q2_r"], "EnemyWithoutTower", [attack(p["q2_dmg"], p["q2_ratio"]), view("q2_hit"), tsfx("q2_hit")])
    q2_atk = combine(*rm("q2"), form(combine(refresh("q3", p["q_win"]), anim("d_skill_b", p["q2_dur"]), sfx("d_q2")),
                                     combine(anim("skill_b", p["q2_dur"]), sfx("q2"))),
                     form(delayed(p["d_q2_at"] - 1, q2_slam, cview("d_q2_wave"), gain),
                          delayed(p["q2_at"] - 1, q2_slam, cview("q2_wave"), gain)))
    bite = homing("q_bite", 100000, "Enemy", [true(p["q3_dmg"], p["q3_ratio"]), view("q3_hit"), tsfx("q3_hit")])
    q3_atk = combine(*rm("q3"), anim("d_bite", p["q3_dur"]), sfx("q3"), voice("vo_q3", p),
                     delayed(p["q3_at"] - 1, bite))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(restore, w_part, sw("rv", revert, sw("q2", q2_atk, sw("q3", q3_atk,
                                                                                    form(dragon_atk, human_atk))))),
                      atype="BaseAttack", cancel=True)

    skill = action("idle", 3, p["s_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(restore, sw("q_cd", NONE, q1())), key="skill")

    # ------------------------------------------------------------------ skill2: E Molten Burst
    burst = [magic(p["e_dmg"], p["e_hp"]), slow("e_slow", p["e_slow"], p["e_slow_t"]), view("e_hit"), tsfx("e_hit")]
    human_e = combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                      delayed(p["e_rel"] - 1, line("e_ball", p["e_speed"], p["e_range"], p["e_w"], "EnemyWithoutTower",
                                                   False, [], [zone("e_boom", p["e_r"], 2, 1, "EnemyWithoutTower", burst),
                                                               view("e_blast"), sfx("e_land"), gain])))
    d_burst = [magic(p["de_dmg"], p["de_hp"]), slow("e_slow", p["e_slow"], p["e_slow_t"]), view("de_hit"), tsfx("e_hit")]
    dragon_end = [zone("de_boom", p["de_r"], 2, 1, "EnemyWithoutTower", d_burst), view("de_blast"), sfx("e_land"),
                  field("de_burn", p["de_burn_r"], p["de_burn_t"], 30, "EnemyWithoutTower",
                        [magic(p["de_burn"]), view("de_singe")])]
    dragon_e = combine(refresh("e_cd", p["e_cd"]), anim("d_skill2", p["e_dur"]), sfx("de"), voice("vo_e", p),
                       delayed(p["de_rel"] - 1, line("de_ball", p["e_speed"], p["de_range"], p["de_w"],
                                                    "EnemyWithoutTower", True,
                                                    [magic(p["de_dmg"] // 2), view("de_hit"), tsfx("e_hit")],
                                                    dragon_end)))
    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(restore, sw("e_cd", NONE, form(dragon_e, human_e))), key="skill2")

    # ------------------------------------------------------------------ ult: R Dragon's Descent -> W -> Q
    breath = line("r_breath", p["r_speed"], p["r_cast"], p["r_w"], "EnemyWithoutTower", True,
                  [magic(p["r_dmg"], p["r_hp"]), {"type": "Fear", "tick": p["r_fear"]}, view("r_hit"), tsfx("r_hit")])
    landing = [cview("r_land"), sfx("r_land"), alive(w_part, delayed(p["r_q"], sw("q_cd", NONE, q1())))]
    descent = combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                      refresh("r_fly", p["r_imm"], cc_immune=True),
                      delayed(p["r_at"] - 1, breath,
                              {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_cast"] + 30000,
                               "end_effects": landing}))
    # short of full Fury the cast does nothing and the ult comes back r_wait ticks later (ult_cooldown_mult for 2 ticks
    # caps the cooldown left; league_gnar's empty cast)
    wait_mult = -(-p["r_cd"] * 100 // p["r_wait"]) - 100
    not_yet = flag("r_back", 2, ult_cooldown_mult=wait_mult)
    r_go = combine(restore, form(descent, sw("full", combine(to_dragon, descent), not_yet)))
    ult = action("idle", 3, p["r_cd"], 1, p["r_cast"], "Targeting", "EnemyChampion", r_go, key="ult")

    # ------------------------------------------------------------------ views (the step-3 effects pack)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("e_ball"), P_("de_ball", BIG), P_("r_breath", BIG)]
    # Q's slashes point forward: drawn into her frames (rig_shyvana's bake, assets/source/native/shyvana_bake.json)
    views_e = [E("a_hit"), E("q_hit"), E("q2_wave", BIG, -1),
               E("d_q2_wave", BIG, -1), E("q2_hit"), E("q3_hit"), E("w_blast", BIG, -1), E("w_hit"), E("w_heal", FX, 3),
               E("e_hit"), E("e_blast", BIG, -1, False), E("de_hit"), E("de_blast", BIG, -1, False),
               E("de_singe"), E("r_hit"), E("r_land", BIG, -1), E("tf_dragon", BIG, 3), E("tf_human", BIG, 3)]
    views_b = [B_("w_on", BIG, 2, "w_aegis"), B_("full", FX, 3, "fury_full"), B_("e_slow", FX, 3)]
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "Shield", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
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
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
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
