"""Build league_jayce.data_champion (top, AD fighter, Mercury Hammer / Mercury Cannon forms) from the parameters P.

    python tools/kit/build_jayce.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-15: top lane melee/ranged AD fighter; the forms switch like League's R from level 1 - the
switch is in the attack slot (league_nidalee's way), the ult slot (level 5) is 「加速电炮」, the gate and its shot (E -> Q);
hammer Q / cannon Q as skill, hammer E + W and cannon W sharing skill2; the whole passive in the main pack; the whole-body
cannon idle / run / hit / dead, a smarter gate aim and the knock-back's direction in the add-on addons/league_jayce later;
the pros' combos):
  forms   Mercury Hammer (default, after every respawn: death clears every data buff): the bare melee reach (atk_range).
          Mercury Cannon: the permanent caster buff `cn` (range +c_add: a range buff cannot be negative, so the bare reach is
          the hammer's), every action plays the cannon's own tags (c_*, league_kayn's way, `CasterAnimation`; idle, run,
          hit and death are the cannon only with the add-on).
          Transform (墨丘利之炮 / 墨丘利之锤, the switch): each attack's first tick, with the switch ready (no `r_cd`),
          checks the rules; a switch replaces that attack with the transform (tf_dur ticks, no hit) and starts r_cd (League:
          6 s). Hammer -> cannon (the pros' Q -> E -> cannon to kite): To the Skies on cooldown and, from level 3 (skill2
          opens; `SwitchByLevel3`), Thundering Blow too. Cannon -> hammer (never with Hyper Charge's shots left): a hammer
          spell ready (To the Skies, or from level 3 Thundering Blow) and either an enemy champion within d_near (dived) or
          every cannon spell on cooldown (Shock Blast, from level 3 Hyper Charge).
  passive Hextech Capacitor (海克斯科技电容), with the transforms' own effects: every switch (the ult's too) gives `haste`
          (p_ms% move speed, p_mt ticks; League +30 for 0.75 s). To cannon: `shred_on` (p_sh_on ticks) - the next cannon shot
          puts `shred` on its target (armour and magic resistance -p_sh% for p_sh_t ticks; League's 10-35% for 5 s). To
          hammer: `guard` (armour and magic resistance +p_arm% for p_arm_t ticks).
  attack  Hammer: the swing (released on a_st). Cannon: the bolt (c_attack, released on c_st), with Hyper Charge armed the
          charged bolt (hc_ad% AD).
  skill   Hammer: To the Skies (苍穹之跃) - a `Targeting` cast on `EnemyWithoutTower` (waves and camps too): with an enemy
          within q_rng he leaps onto the cast target (`MoveToTarget`), q_dmg + q_ad% AD physical round the landing (q_r) and
          q_slow% slower for q_slow_t ticks; from level 3 Thundering Blow follows at once if ready (the pros' Q -> E).
          Cannon: Shock Blast (电能震荡) - an orb at the cast target (a non-penetrating line on `EnemyWithoutTower`); where it
          stops (the first enemy, or its range) it bursts: cq_dmg + cq_ad% AD physical within cq_r. The plain shot never
          goes through the gate.
  skill2  Hammer: Thundering Blow (雷霆一击) first - on an enemy within e_r (champions first): e_dmg + e_ap% AP magic, a
          knock-back straight away from him (e_kb_speed x e_kb_t) and, on champions only (a champion-only twin, so camps and
          the epic monster are spared like League's monster cap), e_hp% of the target's maximum health as true damage (the
          data has no % max health magic damage: `ApAttack` has no target_hp_ratio). While it cools down, with an enemy
          champion within w_near, Lightning Field (闪电领域): w_n pulses every w_per ticks round him (w_r), w_dmg + w_ap% AP
          magic each. Cannon: Hyper Charge (超能电荷) with an enemy champion within cw_near (champions only: data cannot tell
          a jungle camp from a minion wave): the next 3 cannon shots within hc_t ticks deal hc_ad% AD, attack speed
          +hc_as%.
  ult     「加速电炮」 (Acceleration Gate -> Shock Blast, level 5): `Targeting` an `EnemyChampion` within r_range: in hammer
          form he turns into the cannon at once (the transform's passive, r_cd started), places the gate (g_ms% move speed,
          g_t ticks; League 30-60% 3 s) and fires the accelerated orb at the champion: r_speed, flying past minions to the
          first champion on its line (a 25-s ult a minion must not eat), bursting within r_rad for r_amp% of Shock Blast's
          damage (League x1.4, faster and longer).
Add-on (later, addons/league_jayce, not built here): native=1 adds the passive league_jayce:hextech (params below); the
add-on reads `league_jayce_cn` (the cannon form, the view swap), `league_jayce_r_cd`, `league_jayce_hyper`,
`league_jayce_shred_on`, and finds the knock-back and the gate shot by their names (`league_jayce_e_blow`,
`league_jayce_gq_orb`).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_jayce.data_champion")
ID = "league_jayce"
FX = "asset/league/effects/league_jayce_fx"
BIG = "asset/league/effects/league_jayce_big"

# Placeholder timings (no strips yet; retime from the frames later): attack 24 ticks, the hammer lands on tick 12; the
# cannon shot 20, the bolt leaves on tick 8; To the Skies 30, off the ground on tick 6, the leap at q_speed; Shock Blast 24,
# the orb on tick 10; Thundering Blow 24, the blow on tick 10; Lightning Field 20, the first pulse on tick 8; Hyper Charge
# 20; the ult 30, the orb on tick 14; the turns 14.
# Numbers = candidate d5 of the 10-min classic-SDK simulations (%LOCALAPPDATA%/Temp/jy_sim, sim/kd.py --lane 0 against
# the base fighter, executioner, lancer, pole_warrior, knight and berserker, three lineups, both sides, 2026-10-15): +0.89
# on seeds 1-24, +0.81 on 25-48; the pack's top laners on the same seeds: league_darius +1.73 / +1.36, league_renekton
# +1.78 / +1.07, league_aatrox +1.32 / +1.16, league_garen -1.05 / -1.57 (their mean +0.95 / +0.51). The draft d0 (hp 1000
# +102, armour 30, mr 26, Q 60 + 100%, Shock Blast 70 + 110%, E 6%) was -0.10 / -0.29; its bulk alone (d1) +0.73 on seeds
# 1-24; d2 (Q 80 + 110%, Shock Blast 90 + 120%, E 8%) +1.47 / +1.16. q_probe 0 (the leap always onto the cast target) was
# no different (+0.75 against d1's +0.73). Rerun once the strips set the timings.
P = {
    # stats (the pack's top fighters: league_darius 90 +18 / 1080 +105, league_garen 88 +17 / 1100 +110, league_riven,
    # league_fiora 85-88 +18 / 950-980 +100); League's Jayce: 590 +109 hp, 59 AD, 22 armour, 30 mr, 335 move, 125 / 500
    # range. A little ability power (league_jax's way) so Thundering Blow and Lightning Field grow with his level.
    "hp": 1080, "hp_g": 106, "atk": 88, "atk_g": 18, "mp": 20, "mp_g": 8, "def": 34, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 1000, "ms_g": 12,
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 64, "a_st": 12,
    # cannon form: reach atk_range + c_add (League 500 against 125); the bolt
    "c_add": 25000, "c_atk_dur": 20, "c_st": 8, "c_speed": 6000, "c_y": 0,
    # the switch (League R: cd 6 s), the rules' reach for "dived"
    "tf_dur": 14, "r_cd_t": 360, "d_near": 30000,
    # passive Hextech Capacitor + the transforms (League: +30 move speed 0.75 s; shred 10-35% 5 s)
    "p_ms": 25, "p_mt": 60, "p_sh": 20, "p_sh_t": 300, "p_sh_on": 360, "p_arm": 25, "p_arm_t": 240,
    # skill slot (both forms; the forms' own cooldowns are caster flags)
    "s_cd": 60, "s_range": 75000,
    # hammer Q To the Skies (League: 600, 10-310 + 120% bonus AD r ~275, slow 30-60% 2 s, cd 18-6 s)
    "q_cd": 480, "q_rng": 48000, "q_anim": 30, "q_go": 6, "q_speed": 4000, "q_r": 18000, "q_dmg": 70, "q_ad": 105,
    "q_slow": 40, "q_slow_t": 120, "q_probe": 1,
    # cannon Q Shock Blast (League: 1050, speed 1450, 39-285 + 130% bonus AD, r 210, cd 8 s)
    "cq_cd": 420, "cq_anim": 24, "cq_at": 10, "cq_speed": 5500, "cq_len": 80000, "cq_w": 3000, "cq_y": 0, "cq_r": 15000,
    "cq_dmg": 80, "cq_ad": 115,
    # skill2 slot
    "s2_cd": 60, "s2_range": 55000,
    # hammer E Thundering Blow (League: 240, 8-24% max hp + 100% bonus AD magic, knock-back 600 in 0.35 s, cd 20-10 s)
    "e_cd": 540, "e_r": 28000, "e_anim": 24, "e_at": 10, "e_dmg": 40, "e_ap": 60, "e_hp": 7, "e_kb_speed": 2500,
    "e_kb_t": 14,
    # hammer W Lightning Field (League: r 285, 80-440 + 100% AP magic over 4 s, cd 10 s)
    "w_cd": 600, "w_near": 30000, "w_anim": 20, "w_at": 8, "w_r": 20000, "w_n": 8, "w_per": 30, "w_dmg": 14, "w_ap": 12,
    # cannon W Hyper Charge (League: 3 shots in 3.6 s at 62-110% AD, attack speed to the maximum, cd 14.6-5 s)
    "cw_cd": 600, "cw_near": 55000, "cw_anim": 20, "hc_t": 216, "hc_as": 120, "hc_ad": 120,
    # ult 「加速电炮」 (League E -> Q: gate ms 30-60% 3 s, the orb at 2350 to 2000 range, x1.4 damage)
    "r_cd": 1500, "r_range": 90000, "r_anim": 30, "r_at": 14, "r_speed": 9000, "r_len": 115000, "r_w": 3500, "r_y": 0,
    "r_rad": 21000, "r_amp": 140, "g_ms": 40, "g_t": 180,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_jayce: passive league_jayce:hextech (the add-on's knock-back direction and gate aim)
    "native": 0,
    # test builds for the balance runs: 1 = hammer only, 2 = cannon from the first attack on
    "lock": 0,
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


def lv3(low, high):
    return {"type": "SwitchByLevel3", "effect_start": low, "effect_level3": high}


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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def true_hp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def alive(*effects):
    """Only while he lives (a dead caster's Delayed effects run in the game; the search finds no dead caster)."""
    return pick(1, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def burst(name, radius, target, effects):
    """A one-tick area where a line stopped (its end_effects run on that point)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ the forms + passive Hextech Capacitor
    haste = refresh("haste", p["p_mt"], move_speed_mult=p["p_ms"])
    cannon_on = [flag("cn", None, range=p["c_add"]), refresh("r_cd", p["r_cd_t"]), haste,
                 refresh("shred_on", p["p_sh_on"])]
    to_cannon = combine(*cannon_on, anim("tf_c", p["tf_dur"]), cview("tf_spark"), sfx("tf_c"), voice("vo_tf_c", p))
    to_hammer = combine(*rm("cn", "shred_on"), refresh("r_cd", p["r_cd_t"]), haste,
                        refresh("guard", p["p_arm_t"], defence_mult=p["p_arm"], magic_resistance_mult=p["p_arm"]),
                        anim("tf_h", p["tf_dur"]), cview("tf_spark"), sfx("tf_h"), voice("vo_tf_h", p))
    instant_cannon = sw("cn", NONE, combine(*cannon_on, cview("tf_spark"), sfx("tf_c")))

    # ------------------------------------------------------------------ attack
    hammer_atk = combine(sfx("a_swing"), delayed(p["a_st"] - 1, homing("a_swing", 100000, 0, "Enemy",
                                                                        [attack(0, 100), view("a_hit"), tsfx("a_hit")])))

    def bolt(ratio, shred):
        hit = [attack(0, ratio), view("c_hit"), tsfx("c_hit")]
        if shred:
            hit += [buff("shred", p["p_sh_t"], defence_mult=-p["p_sh"], magic_resistance_mult=-p["p_sh"]), tsfx("shred")]
        return homing("c_bolt", p["c_speed"], p["c_y"], "Enemy", hit)

    def shot(ratio):
        go = lambda s: delayed(p["c_st"] - 1, bolt(ratio, s))
        return sw("shred_on", combine(*rm("shred_on"), go(True)), go(False))
    # Hyper Charge's three shots: hc1 / hc2 count the first two, the third ends it
    hyper_step = sw("hc2", combine(*rm("hyper", "hc1", "hc2")), sw("hc1", flag("hc2", p["hc_t"]), flag("hc1", p["hc_t"])))
    cannon_atk = combine(anim("c_attack", p["c_atk_dur"]),
                         sw("hyper", combine(hyper_step, sfx("h_shot"), shot(p["hc_ad"])),
                            combine(sfx("c_shot"), shot(100))))

    # the switch's rules (only with r_cd gone) lay `tf`; one branch then plays the transform or the attack
    tf = flag("tf", 2)
    # hammer -> cannon: To the Skies spent and (level 3+) Thundering Blow spent
    go_c = sw("hq_cd", lv3(tf, sw("he_cd", tf)))

    def hammer_ready(x):
        return sw("hq_cd", lv3(NONE, sw("he_cd", NONE, x)), x)
    cannon_down = sw("cq_cd", lv3(tf, sw("cw_cd", tf)))
    near = combine(*rm("near"), pick(p["d_near"], "EnemyChampion", flag("near", 2)))
    go_h = sw("hyper", NONE, combine(near, hammer_ready(sw("near", tf, cannon_down))))
    rules = combine(*rm("tf"), sw("r_cd", NONE, sw("cn", go_h, go_c)))
    if p["lock"] == 1:      # test builds only: never switch (hammer) / switch once and stay (cannon)
        rules = NONE
    elif p["lock"] == 2:
        rules = combine(*rm("tf"), sw("cn", NONE, tf))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(rules, sw("tf", sw("cn", to_hammer, to_cannon), sw("cn", cannon_atk, hammer_atk))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill2's pieces (Q's landing plays the blow too)
    def blow(target):
        hits = [magic(p["e_dmg"], p["e_ap"]), {"type": "Knockback", "speed": p["e_kb_speed"], "tick": p["e_kb_t"]},
                view("e_blow"), tsfx("e_blow")]
        return pick(p["e_r"], target, homing("e_blow", 100000, 0, "EnemyWithoutTower", hits),
                    homing("e_twin", 100000, 0, "EnemyChampion", [true_hp(p["e_hp"])]))

    def thunder(at):
        """Thundering Blow on an enemy within e_r, champions first (probe flags: no cast on nothing)."""
        hit = combine(*rm("e_c", "e_in"), pick(p["e_r"], "EnemyChampion", flag("e_c", 1)),
                      pick(p["e_r"], "EnemyWithoutTower", flag("e_in", 1)),
                      sw("e_c", blow("EnemyChampion"), sw("e_in", blow("EnemyWithoutTower"))))
        return combine(flag("he_cd", p["e_cd"]), anim("skill2", p["e_anim"]), sfx("e_cast"), voice("vo_e", p),
                       delayed(at + p["e_at"] - 1, alive(hit)))

    # ------------------------------------------------------------------ skill: To the Skies / Shock Blast
    land_hits = [attack(p["q_dmg"], p["q_ad"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                 view("q_hit"), tsfx("q_hit")]
    e_in_reach = combine(*rm("e_in"), pick(p["e_r"], "EnemyWithoutTower", flag("e_in", 1)), sw("e_in", thunder(0)))
    landing = [around(p["q_r"], "EnemyWithoutTower", land_hits), cview("q_land"), sfx("q_land"),
               lv3(NONE, sw("he_cd", NONE, e_in_reach))]
    leap = combine(flag("hq_cd", p["q_cd"]), anim("skill", p["q_anim"]), sfx("q_leap"), voice("vo_q", p),
                   delayed(p["q_go"] - 1, {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["s_range"] + 30000,
                                           "end_effects": landing}))
    # q_probe 1: only with an enemy within q_rng (the slot's range is Shock Blast's); 0: always onto the cast target
    q_probe = combine(*rm("q_in"), pick(p["q_rng"], "EnemyWithoutTower", flag("q_in", 1)), sw("q_in", leap))         if p["q_probe"] else leap

    cq_hits = [attack(p["cq_dmg"], p["cq_ad"]), view("cq_hit"), tsfx("cq_hit")]
    blast = combine(flag("cq_cd", p["cq_cd"]), anim("c_skill", p["cq_anim"]), sfx("cq"), voice("vo_cq", p),
                    delayed(p["cq_at"] - 1, line("cq_orb", p["cq_speed"], p["cq_len"], p["cq_w"], p["cq_y"],
                                                 "EnemyWithoutTower", False, [],
                                                 [burst("cq_area", p["cq_r"], "EnemyWithoutTower", cq_hits),
                                                  view("cq_boom"), sfx("cq_boom")])))
    skill = action("idle", 3, p["s_cd"], 1, p["s_range"], "Targeting", "EnemyWithoutTower",
                   sw("cn", sw("cq_cd", NONE, blast), sw("hq_cd", NONE, q_probe)), key="skill")

    # ------------------------------------------------------------------ skill2: Thundering Blow + Lightning Field / Hyper Charge
    pulse = around(p["w_r"], "EnemyWithoutTower", [magic(p["w_dmg"], p["w_ap"]), view("w_zap")])
    field = combine(flag("hw_cd", p["w_cd"]), anim("w_cast", p["w_anim"]), sfx("w_field"), cview("w_field"),
                    *[delayed(p["w_at"] - 1 + i * p["w_per"], alive(pulse)) for i in range(p["w_n"])])
    w_probe = combine(*rm("w_c"), pick(p["w_near"], "EnemyChampion", flag("w_c", 1)), sw("w_c", field))
    hammer_s2 = sw("he_cd", sw("hw_cd", NONE, w_probe), e_in_reach)

    hyper = combine(flag("cw_cd", p["cw_cd"]), anim("c_skill2", p["cw_anim"]), sfx("hyper"), *rm("hc1", "hc2"),
                    refresh("hyper", p["hc_t"], attack_speed_mult=p["hc_as"]))
    cw_probe = combine(*rm("w_c"), pick(p["cw_near"], "EnemyChampion", flag("w_c", 1)), sw("w_c", hyper))
    cannon_s2 = sw("cw_cd", NONE, cw_probe)
    skill2 = action("idle", 3, p["s2_cd"], 1, p["s2_range"], "None", "EnemyWithoutTower",
                    sw("cn", cannon_s2, hammer_s2), key="skill2")

    # ------------------------------------------------------------------ ult: the gate and its shot
    r_mult = lambda x: x * p["r_amp"] // 100
    r_hits = [attack(r_mult(p["cq_dmg"]), r_mult(p["cq_ad"])), view("gq_hit"), tsfx("cq_hit")]
    r_go = combine(instant_cannon, anim("ult", p["r_anim"]), cview("gate"), sfx("gate"), voice("vo_r", p),
                   refresh("g_haste", p["g_t"], move_speed_mult=p["g_ms"]),
                   delayed(p["r_at"] - 1, sfx("gq"),
                           line("gq_orb", p["r_speed"], p["r_len"], p["r_w"], p["r_y"], "EnemyChampion", False, [],
                                [burst("gq_area", p["r_rad"], "EnemyWithoutTower", r_hits), view("gq_boom"),
                                 sfx("gq_boom")])))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", r_go, key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("c_bolt"), P_("cq_orb"), P_("gq_orb", BIG)]
    views_e = [E("a_hit"), E("c_hit"), E("q_land", BIG, -1, False), E("q_hit"), E("e_blow"), E("w_field", BIG, -1),
               E("w_zap"), E("cq_hit"), E("cq_boom", BIG, 2, False), E("gate", BIG, 1, False), E("gq_hit"),
               E("gq_boom", BIG, 2, False), E("tf_spark", FX, 3)]
    views_b = [B_("q_slow", FX, 1), B_("hyper", FX, 2), B_("shred", FX, 2), B_("haste", FX, -1),
               B_("g_haste", FX, -1, "haste"), B_("guard", FX, 2)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Range", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if p["native"]:
        kit["passive"] = {"passive_ref": "league_jayce:hextech",
                          "params": {"kb_speed": p["e_kb_speed"], "kb_t": p["e_kb_t"], "gate_range": p["r_range"]}}
    return kit


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
