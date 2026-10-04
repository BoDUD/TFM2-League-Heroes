#!/usr/bin/env python3
"""Sett (瑟提, the Boss): his whole kit is written from this file - league/champion/league_sett.data_champion and his
text in league/text/champion.i18n (five languages, every number taken from the constants below).

    python tools/kit/sett_kit.py            # write both
    python tools/kit/sett_kit.py --check    # exit 1 if either differs from what this file writes

League's kit in TFM2's four slots (porting-heroes "League of Legends specifics"):
  attack  Pit Grit: the punches alternate left and right (the right one is the `attack2` tag, forced with
          CasterAnimation like league_masteryi's Double Strike); the right one lands sooner and hits harder, and after
          2 s without a punch the next one is a left again (League's reset). League's regeneration per missing health
          cannot be written (nothing reads current health, champion-data section 3), so he has a high flat hp_regen.
  skill   Facebreaker (E) with Knuckle Down (Q) folded in: he grabs every enemy round him and pulls them in (Grab
          without `tick`, league_darius E: they stop at him). No area can be put behind him (`Forward` is unsigned) and
          no shape tells front from back, so League's "enemies on both sides" becomes "two or more pulled in" (a 1-tick
          count, league_blitzcrank's way): then all of them are stunned, else the one is slowed. His next two punches
          are Knuckle Down (+ flat + AD + % of the target's maximum health) and he runs faster for 1.5 s.
  skill2  Haymaker (W). Grit is stored as he is hurt: no effect hears damage, so a 1-hit-point shield on him is the
          sensor (league_sivir E's way), with a `WithShield` buff that is gone 2 ticks after a hit breaks it (champion-data
          section 5; the pattern "Damage taken as a resource"). Each
          attack and the ult look at it: a broken sensor is one more Grit level (1-5, exclusive buffs of 4 s, the
          step removing the one before it, the top one refreshed) and is armed again. The check stays out of skill
          and skill2, which the game copies every tick (champion-data section 8). W spends the levels on a shield
          and on the true damage of the punch's middle line; the whole fist deals physical damage. Its lines are laid
          at the cast and hit 27 ticks later, so a target can step out (League's wind-up); the fist's picture is a
          separate line on `Ally`, so the enemy AI does not dodge the picture itself.
  ult     The Show Stopper (R): he grabs an enemy champion (stunned until just after the slam), heaves it forward
          (Knockback), leaps after it at the same speed (MoveToTarget homes on it, so he lands on it once it has
          landed) and slams (league_malphite R's landing): damage and a slow round him, more on the champion he threw.
          League scales the slam with the thrown champion's bonus health; the data reads only each target's own
          maximum health, so everyone hit takes a share of his own and the thrown champion more of its own.

Art, icons and sounds still to come: the sprite (asset/league/champions/league_sett: idle run attack attack2 skill
skill2 ult ult_dash ult_slam hit dead) and the effect sheets league_sett_fx / league_sett_big from Codex
(assets/source/sett/), the ability icons and League's sounds from the client in a local session
(tools/lol/extract_<hero>.py). Until then the sounds are base placeholders (SFX). The numbers are a first guess
inside the base ranges, not yet balanced on the SDK simulator (porting-heroes "Balance check"). The localized ability
names in zh-hant, ko and ja were written without the client and still need checking against it.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_sett.data_champion")
TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
ID = "league_sett"
FX = "asset/league/effects/league_sett_fx"
BIG = "asset/league/effects/league_sett_big"

STAT = {"attack": 90, "magic_power": 0, "hp": 1100, "defence": 34, "magic_resistance": 26, "move_speed": 1000,
        "hp_regen": 5, "stack": 0, "crit_chance": 0}
GROWTH = {"attack": 18, "magic_power": 0, "hp": 110, "defence": 8, "magic_resistance": 4, "move_speed": 11,
          "hp_regen": 2, "stack": 0, "crit_chance": 0}

# Pit Grit (attack). Ticks: 60 a second.
ATTACK_DURATION, ATTACK_COOLTIME, ATTACK_START, ATTACK_RANGE = 24, 64, 3, 25000
LEFT_HIT = 9                     # after start_timing: the left jab lands on tick 12
RIGHT_HIT = 6                    # the right punch is quicker: tick 9
ATTACK2_TICKS = 21               # the right punch's strip, forced from tick 3 to the action's end
RIGHT_WINDOW = 120               # 2 s without a punch: the next one is a left again
RIGHT_DAMAGE, RIGHT_RATIO = 15, 120

# Knuckle Down (Q, armed by Facebreaker): two punches
Q_TICKS = 300
Q_DAMAGE, Q_RATIO, Q_HP = 20, 20, 3          # added to the punch: + 20 + 20% AD + 3% of the target's max health
Q_HASTE, Q_HASTE_TICKS = 30, 90

# Facebreaker (E) - skill
E_DURATION, E_COOLTIME, E_START, E_RANGE = 30, 480, 2, 30000
E_GRAB = 10                      # tick his hands close on them (the damage, the pull and the stun)
E_SMASH = 18                     # tick of the clap picture, when the pulled ones reach him
E_RADIUS = 24000                 # + both bodies
E_DAMAGE, E_RATIO = 40, 70
E_GRAB_SPEED = 3000
E_STUN = 60
E_SLOW, E_SLOW_TICKS = -50, 30

# Haymaker (W) - skill2
W_DURATION, W_COOLTIME, W_START, W_RANGE = 54, 540, 2, 42000
W_APPLY = 28                     # the lines hit 27 ticks after the cast: tick 29
W_LENGTH = 50000
W_SIDE_WIDTH, W_TRUE_WIDTH = 20000, 4000    # a line hits within width + ~15000 of its middle (champion-data section 7)
W_SIDE, W_SIDE_R = 40, 70                   # physical, the whole fist
W_TRUE, W_TRUE_R = 30, 30                   # true damage, the middle line
W_TRUE_K, W_TRUE_KR = 10, 8                 # + per Grit level
W_SHIELD, W_SHIELD_R = 50, 20
W_SHIELD_K, W_SHIELD_KR = 30, 25            # + per Grit level
W_SHIELD_TICKS = 180
W_VIEW_TICKS = 46                # the fist's picture: the wind-up, the punch on its tick 27, the fade

# Grit. GRIT_MAX = 0 drops the sensor: W is then a fixed shield and fixed true damage (the plan at the hero's pick)
GRIT_MAX, GRIT_TICKS = 5, 240

# The Show Stopper (R) - ult
R_DURATION, R_COOLTIME, R_START, R_RANGE = 40, 3000, 2, 30000
R_TOSS = 8                       # tick he heaves the champion forward and leaps
R_TOSS_SPEED, R_TOSS_TICKS = 3000, 8         # 24000 forward
R_LEAP_SPEED, R_LEAP_RANGE = 3000, 120000    # as fast as the throw: he lands on it after it has landed
R_STUN = 34                      # from the grab (tick 2) to just after the latest slam
R_UNSTOP = 40
R_DASH_ANIM = 30
R_SLAM_ANIM, R_SLAM_HIT = 24, 4
R_RADIUS = 26000
R_DAMAGE, R_RATIO, R_HP = 120, 100, 4
R_TARGET_HP = 6                  # the thrown champion: + 6% of its max health
R_SLOW, R_SLOW_TICKS = -99, 30

# Sounds: League's, from tools/lol/extract_sett.py (the clips are not in git; league/sound/sfx/league_sett_*.sound_info
# say what each one plays, mod.override_info maps them)
SFX = {k: f"{ID}_{k}" for k in ("a_hit", "a2_hit", "q_hit", "e_cast", "e_hit", "w_cast", "w_hit", "r_cast", "r_slam")}


def n(s):
    return f"{ID}_{s}"


def comb(*e):
    return {"type": "Combine", "effects": list(e)}


def sw(buff, yes, no):
    return {"type": "SwitchByBuff", "buff_name": buff, "effect_buff": yes, "effect_none": no}


def delayed(tick, *e):
    return {"type": "Delayed", "tick": tick, "effects": list(e)}


def state(name, tick=None, **fields):
    s = {"name": name, "duration": {"Time": {"tick": tick}} if tick is not None else "Permanent"}
    s.update(fields)
    return s


def add(name, tick=None, **fields):
    return {"type": "AddCasterBuff", "buff_state": state(name, tick, **fields), "only_to_enemy": False}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": state(name, tick, **fields)}


def attack(damage, ratio, target_hp=0):
    e = {"type": "Attack", "damage": damage, "attack_ratio": ratio}
    if target_hp:
        e["target_hp_ratio"] = target_hp
    return e


def fixed(damage, ratio):
    return {"type": "FixedAttack", "damage": damage, "attack_ratio": ratio}


def stun(tick):
    return {"type": "Stun", "duration": tick}


def around(radius, target, *e):
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": target,
            "apply_type": "AroundCaster", "effects": list(e)}


def self_only(*e):
    return around(1000, "AllyOnlySelf", *e)


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


def view(name):
    return {"type": "ViewEffect", "name": name}


def cview(name):
    return {"type": "CasterViewEffect", "name": name}


def sfx(name):
    return {"type": "Sfx", "name": name}


def tsfx(name):
    return {"type": "TargetSfx", "name": name}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def line(name, width, length, apply, delay, target, *effects):
    return {"type": "LineRangeProjectile", "name": name, "width": width, "length": length, "delay": delay,
            "apply": apply, "applied_target": target,
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in effects]}


def action(slot, duration, cooltime, start, cancelable, rng, casting_type, target, attack_type, effect):
    return {"action_name": slot, "description": f"#asset/base/text/champion?description.{ID}.{slot}",
            "duration": duration, "cooltime": cooltime, "start_timing": start, "cancelable": cancelable, "range": rng,
            "casting_type": casting_type, "casting_target": target, "attack_type": attack_type, "effect": effect}


# --- Grit -------------------------------------------------------------------------------------------------------

def grit_sensor():
    """A 1-hit-point shield and the buff that lives while a shield holds: the first hit after it is armed breaks it."""
    return [self_only(shield(1, 0, 36000)),
            {"type": "AddCasterBuff", "buff_state": {"name": n("grit_sense"), "duration": "WithShield"},
             "only_to_enemy": False}]


def grit_climb():
    node = add(n("grit_1"), GRIT_TICKS)
    for k in range(1, GRIT_MAX + 1):
        node = sw(n(f"grit_{k}"), comb(rm(n(f"grit_{k}")), add(n(f"grit_{min(k + 1, GRIT_MAX)}"), GRIT_TICKS)), node)
    return node


def grit_check():
    """First action of a life: arm the sensor. Later: a broken sensor means he was hit - one more level, arm again.
    Returns a list (empty without Grit) to splice into an action's Combine."""
    if not GRIT_MAX:
        return []
    return [sw(n("grit_init"),
               sw(n("grit_sense"), comb(), comb(grit_climb(), *grit_sensor())),
               comb(*grit_sensor(), add(n("grit_init"))))]


def grit_levels(branch):
    node = branch(0)
    for k in range(1, GRIT_MAX + 1):
        node = sw(n(f"grit_{k}"), branch(k), node)
    return node


# --- the four actions -------------------------------------------------------------------------------------------

def punch(right):
    dmg, ratio = (RIGHT_DAMAGE, RIGHT_RATIO) if right else (0, 100)
    side = "a2_hit" if right else "a_hit"

    def knuckle(charge):
        return comb(attack(dmg + Q_DAMAGE, ratio + Q_RATIO, Q_HP), view(n("q_hit")), tsfx(SFX["q_hit"]), rm(n(charge)))

    hit = sw(n("q_2"), knuckle("q_2"),
             sw(n("q_1"), knuckle("q_1"), comb(attack(dmg, ratio), view(n(side)), tsfx(SFX[side]))))
    if right:
        return comb(anim("attack2", ATTACK2_TICKS), rm(n("right")), delayed(RIGHT_HIT, hit))
    return comb(add(n("right"), RIGHT_WINDOW), delayed(LEFT_HIT, hit))


def attack_action():
    return action("attack", ATTACK_DURATION, ATTACK_COOLTIME, ATTACK_START, True, ATTACK_RANGE, "Targeting", "Enemy",
                  "BaseAttack", comb(*grit_check(), sw(n("right"), punch(True), punch(False))))


def facebreaker():
    def pulled(cc):
        return around(E_RADIUS, "EnemyWithoutTower", attack(E_DAMAGE, E_RATIO), {"type": "Grab", "speed": E_GRAB_SPEED},
                      cc, view(n("e_hit")), tsfx(SFX["e_hit"]))

    grab = delayed(
        E_GRAB - E_START,
        around(E_RADIUS, "EnemyWithoutTower", sw(n("e_one"), add(n("e_two"), 1), add(n("e_one"), 1))),
        sw(n("e_two"), pulled(stun(E_STUN)), pulled(debuff(n("e_slow"), E_SLOW_TICKS, move_speed_mult=E_SLOW))),
        rm(n("q_2")), rm(n("q_1")), add(n("q_2"), Q_TICKS), add(n("q_1"), Q_TICKS),
        add(n("q_haste"), Q_HASTE_TICKS, move_speed_mult=Q_HASTE))
    return action("skill", E_DURATION, E_COOLTIME, E_START, False, E_RANGE, "None", "EnemyWithoutTower", "Skill",
                  comb(sfx(SFX["e_cast"]), grab, delayed(E_SMASH - E_START, cview(n("e_smash")))))


def haymaker():
    def level(k):
        e = [self_only(shield(W_SHIELD + k * W_SHIELD_K, W_SHIELD_R + k * W_SHIELD_KR, W_SHIELD_TICKS)),
             line(n(f"w_true_{k}"), W_TRUE_WIDTH, W_LENGTH, W_APPLY, W_APPLY + 2, "EnemyWithoutTower",
                  fixed(W_TRUE + k * W_TRUE_K, W_TRUE_R + k * W_TRUE_KR), view(n("w_true")))]
        return comb(rm(n(f"grit_{k}")), *e) if k else comb(*e)

    effect = comb(
        sfx(SFX["w_cast"]),
        line(n("w_fist"), W_SIDE_WIDTH, W_LENGTH, W_VIEW_TICKS, W_VIEW_TICKS, "Ally"),
        line(n("w_side"), W_SIDE_WIDTH, W_LENGTH, W_APPLY, W_APPLY + 2, "EnemyWithoutTower",
             attack(W_SIDE, W_SIDE_R), view(n("w_hit")), tsfx(SFX["w_hit"])),
        add(n("w_shield"), W_SHIELD_TICKS),
        grit_levels(level))
    return action("skill2", W_DURATION, W_COOLTIME, W_START, False, W_RANGE, "Direction", "EnemyWithoutTower", "Skill",
                  effect)


def show_stopper():
    slam = delayed(R_SLAM_HIT,
                   cview(n("r_slam")), sfx(SFX["r_slam"]),
                   attack(0, 0, R_TARGET_HP),
                   around(R_RADIUS, "EnemyWithoutTower", attack(R_DAMAGE, R_RATIO, R_HP),
                          debuff(n("r_slow"), R_SLOW_TICKS, move_speed_mult=R_SLOW), view(n("r_hit"))))
    leap = {"type": "MoveToTarget", "speed": R_LEAP_SPEED, "range": R_LEAP_RANGE,
            "end_effects": [{"type": "RemoveCasterAnimation", "name": "ult_dash"}, anim("ult_slam", R_SLAM_ANIM), slam]}
    effect = comb(
        *grit_check(),
        add(n("r_unstop"), R_UNSTOP, cc_immune=True),
        sfx(SFX["r_cast"]),
        stun(R_STUN),
        view(n("r_grab")),
        delayed(R_TOSS - R_START, {"type": "Knockback", "speed": R_TOSS_SPEED, "tick": R_TOSS_TICKS},
                anim("ult_dash", R_DASH_ANIM), leap))
    return action("ult", R_DURATION, R_COOLTIME, R_START, False, R_RANGE, "Targeting", "EnemyChampion", "Skill", effect)


def kit():
    def ve(name, sheet, z, follow):
        return {"type": "Animation", "name": n(name), "anim": sheet, "tag": name, "z": z, "is_follow": follow}

    return {
        "id": ID,
        "category": "Melee",
        "tags": ["AD", "Melee", "Tank", "CC", "Shield"],
        "sprite": f"asset/league/champions/{ID}",
        "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2",
                        f"asset/league/icons/{ID}_ult"],
        "stat": STAT,
        "growth": GROWTH,
        "attack": attack_action(),
        "skill": facebreaker(),
        "skill2": haymaker(),
        "ult": show_stopper(),
        "view_projectiles": [{"type": "Animated", "name": n("w_fist"), "anim": BIG, "tag": "w_fist", "repeat": False,
                              "z": 1}],
        "view_effects": [ve("a_hit", FX, 2, True), ve("a2_hit", FX, 2, True), ve("q_hit", FX, 2, True),
                         ve("e_hit", FX, 2, True), ve("e_smash", BIG, 1, False), ve("w_hit", FX, 2, True),
                         ve("w_true", FX, 3, True), ve("r_grab", FX, 2, True), ve("r_slam", BIG, -1, False),
                         ve("r_hit", FX, 2, True)],
        "view_buffs": [{"type": "Animated", "name": n("q_1"), "anim": FX, "tag": "q_glow", "repeat": True, "z": 1},
                       {"type": "ThreePhase", "name": n("w_shield"), "anim": FX, "pre_tag": "w_pre",
                        "loop_tag": "w_loop", "remove_tag": "w_remove", "z": 1}]
        # the top two Grit levels show a heat haze: W is about full
        + [{"type": "Animated", "name": n(f"grit_{k}"), "anim": FX, "tag": "grit", "repeat": True, "z": -1}
           for k in range(max(1, GRIT_MAX - 1), GRIT_MAX + 1) if GRIT_MAX],
    }


# --- text -------------------------------------------------------------------------------------------------------

AD_ICON = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
ORANGE, AMBER, RED, GREEN, YELLOW, WHITE = "ff9028ff", "ffb900ff", "ef5350ff", "6aff55ff", "e8d44dff", "f5f5f5ff"


def c(colour, s):
    return f"<#{colour}>{s}<>"


def sec(ticks):
    s = ticks / 60
    return f"{s:g}"


def texts():
    """{lang: (name, {slot: text}, (skill1, skill2, ult))}. AD ratios as the stat icon and a number (league_aatrox)."""
    def ad(r, colour=ORANGE, unit="%"):
        return f"{AD_ICON}{c(colour, f'{r}{unit}')}"

    def en_ad(r, colour=ORANGE):
        return f"{AD_ICON}{c(colour, f'{r}% AD')}"

    def grit(s, without=""):
        return s if GRIT_MAX else without

    rd, rr = RIGHT_DAMAGE, RIGHT_RATIO - 100
    win, stun_s, slow = sec(RIGHT_WINDOW), sec(E_STUN), -E_SLOW
    q_haste = Q_HASTE
    grit_s, r_slow, r_slow_s = sec(GRIT_TICKS), -R_SLOW, sec(R_SLOW_TICKS)
    out = {}

    out["zh-hans"] = ("瑟提", {
        "attack": f"被动{c(ORANGE, '沙场豪情')}：左右拳交替出击，右拳出手更快，额外造成{c(ORANGE, rd)} + {ad(rr)}的"
                  f"{c(ORANGE, '物理伤害')}；{c(AMBER, win + '秒')}不出拳就从左拳重新开始。瑟提的{c(GREEN, '生命回复')}很高。",
        "skill": f"把周围的敌人全部{c(RED, '拉')}到面前对撞，造成{c(ORANGE, E_DAMAGE)} + {ad(E_RATIO)}的{c(ORANGE, '物理伤害')}；"
                 f"拉到两个及以上时全部{c(RED, '眩晕')}{c(AMBER, stun_s + '秒')}，否则{c(RED, '减速')}{c(AMBER, f'{slow}%')}。"
                 f"之后两拳为{c(ORANGE, '屈人之威')}：额外{c(ORANGE, Q_DAMAGE)} + {ad(Q_RATIO)} + {c(AMBER, f'{Q_HP}%')}"
                 f"最大生命值伤害，移速+{c(AMBER, f'{q_haste}%')}。",
        "skill2": grit(f"受伤积攒{c(YELLOW, '豪意')}（最多{c(AMBER, GRIT_MAX)}层，{c(AMBER, grit_s + '秒')}消散）。消耗豪意")
                  + f"获得{c(YELLOW, W_SHIELD)} + {ad(W_SHIELD_R, YELLOW)}{c(YELLOW, '护盾')}，蓄力前轰一拳："
                  f"{c(ORANGE, W_SIDE)} + {ad(W_SIDE_R)}{c(ORANGE, '物理伤害')}，正中的敌人再受{c(WHITE, W_TRUE)} + "
                  f"{ad(W_TRUE_R, WHITE)}{c(WHITE, '真实伤害')}。" + grit(f"每层豪意护盾+{c(YELLOW, W_SHIELD_K)} + "
                  f"{ad(W_SHIELD_KR, YELLOW)}，真伤+{c(WHITE, W_TRUE_K)} + {ad(W_TRUE_KR, WHITE)}。"),
        "ult": f"抓住一名敌方英雄{c(RED, '眩晕')}并扔向前方，再跃起追上砸地：周围敌人受到{c(ORANGE, R_DAMAGE)} + {ad(R_RATIO)}"
               f" + {c(AMBER, f'{R_HP}%')}最大生命值的{c(ORANGE, '物理伤害')}并{c(RED, '减速')}{c(AMBER, f'{r_slow}%')}，"
               f"被扔的英雄再受{c(AMBER, f'{R_TARGET_HP}%')}最大生命值伤害。",
    }, ("强手裂颅", "蓄意轰拳", "叹为观止"))

    out["zh-hant"] = ("賽特", {
        "attack": f"被動{c(ORANGE, '恆毅之泉')}：左右拳交替出擊，右拳出手更快，額外造成{c(ORANGE, rd)} + {ad(rr)}的"
                  f"{c(ORANGE, '物理傷害')}；{c(AMBER, win + '秒')}不出拳就從左拳重新開始。賽特的{c(GREEN, '生命回復')}很高。",
        "skill": f"把周圍的敵人全部{c(RED, '拉')}到面前對撞，造成{c(ORANGE, E_DAMAGE)} + {ad(E_RATIO)}的{c(ORANGE, '物理傷害')}；"
                 f"拉到兩個以上時全部{c(RED, '暈眩')}{c(AMBER, stun_s + '秒')}，否則{c(RED, '緩速')}{c(AMBER, f'{slow}%')}。"
                 f"之後兩拳為{c(ORANGE, '懾人猛拳')}：額外{c(ORANGE, Q_DAMAGE)} + {ad(Q_RATIO)} + {c(AMBER, f'{Q_HP}%')}"
                 f"最大生命傷害，移速+{c(AMBER, f'{q_haste}%')}。",
        "skill2": grit(f"受傷累積{c(YELLOW, '拳皇恆毅')}（最多{c(AMBER, GRIT_MAX)}層，{c(AMBER, grit_s + '秒')}消散）。消耗拳皇恆毅")
                  + f"獲得{c(YELLOW, W_SHIELD)} + {ad(W_SHIELD_R, YELLOW)}{c(YELLOW, '護盾')}，蓄力前轟一拳："
                  f"{c(ORANGE, W_SIDE)} + {ad(W_SIDE_R)}{c(ORANGE, '物理傷害')}，正中的敵人再受{c(WHITE, W_TRUE)} + "
                  f"{ad(W_TRUE_R, WHITE)}{c(WHITE, '真實傷害')}。" + grit(f"每層拳皇恆毅護盾+{c(YELLOW, W_SHIELD_K)} + "
                  f"{ad(W_SHIELD_KR, YELLOW)}，真傷+{c(WHITE, W_TRUE_K)} + {ad(W_TRUE_KR, WHITE)}。"),
        "ult": f"抓住一名敵方英雄{c(RED, '暈眩')}並扔向前方，再躍起追上砸地：周圍敵人受到{c(ORANGE, R_DAMAGE)} + {ad(R_RATIO)}"
               f" + {c(AMBER, f'{R_HP}%')}最大生命的{c(ORANGE, '物理傷害')}並{c(RED, '緩速')}{c(AMBER, f'{r_slow}%')}，"
               f"被扔的英雄再受{c(AMBER, f'{R_TARGET_HP}%')}最大生命傷害。",
    }, ("強手裂顱", "蓄意轟拳", "嘆為觀止"))

    out["en"] = ("Sett", {
        "attack": f"Passive {c(ORANGE, 'Pit Grit')}: Sett's punches alternate left and right. The right punch lands sooner "
                  f"and deals {c(ORANGE, rd)} + {en_ad(rr)} more {c(ORANGE, 'physical damage')}; after "
                  f"{c(AMBER, win + 's')} without a punch he starts again with the left. He has high "
                  f"{c(GREEN, 'health regeneration')}.",
        "skill": f"Sett grabs every enemy around him and smashes them together, dealing {c(ORANGE, E_DAMAGE)} + "
                 f"{en_ad(E_RATIO)} {c(ORANGE, 'physical damage')}. If he pulls in two or more, all are "
                 f"{c(RED, 'stunned')} for {c(AMBER, stun_s + 's')}, otherwise {c(RED, 'slowed')} by "
                 f"{c(AMBER, f'{slow}%')}. His next two punches are {c(ORANGE, 'Knuckle Down')}: "
                 f"{c(ORANGE, Q_DAMAGE)} + {en_ad(Q_RATIO)} + {c(AMBER, f'{Q_HP}%')} of the target's max health more "
                 f"damage, and he gains {c(AMBER, f'{q_haste}%')} move speed.",
        "skill2": grit(f"Passive: Sett gains a level of {c(YELLOW, 'Grit')} while taking damage (up to "
                       f"{c(AMBER, GRIT_MAX)}, lost after {c(AMBER, grit_s + 's')}). He spends it on a ",
                       "Sett gains a ")
                  + f"{c(YELLOW, W_SHIELD)} + {en_ad(W_SHIELD_R, YELLOW)} {c(YELLOW, 'shield')} and winds up a punch: "
                  f"{c(ORANGE, W_SIDE)} + {en_ad(W_SIDE_R)} {c(ORANGE, 'physical damage')}; enemies in the middle also "
                  f"take {c(WHITE, W_TRUE)} + {en_ad(W_TRUE_R, WHITE)} {c(WHITE, 'true damage')}."
                  + grit(f" Each level of Grit adds {c(YELLOW, W_SHIELD_K)} + {en_ad(W_SHIELD_KR, YELLOW)} shield and "
                         f"{c(WHITE, W_TRUE_K)} + {en_ad(W_TRUE_KR, WHITE)} true damage."),
        "ult": f"Sett grabs an enemy champion, {c(RED, 'stuns')} it and hurls it forward, then leaps after it and slams "
               f"it down: enemies nearby take {c(ORANGE, R_DAMAGE)} + {en_ad(R_RATIO)} + {c(AMBER, f'{R_HP}%')} of their "
               f"max health as {c(ORANGE, 'physical damage')} and are {c(RED, 'slowed')} by {c(AMBER, f'{r_slow}%')} "
               f"for {c(AMBER, r_slow_s + 's')}. The thrown champion takes another {c(AMBER, f'{R_TARGET_HP}%')} of "
               f"its max health.",
    }, ("Facebreaker", "Haymaker", "The Show Stopper"))

    out["ko"] = ("세트", {
        "attack": f"기본 지속 효과 {c(ORANGE, '투기장의 투지')}: 왼손과 오른손으로 번갈아 주먹을 날립니다. 오른손은 더 빠르고 "
                  f"{c(ORANGE, rd)} + {ad(rr)} {c(ORANGE, '물리 피해')}를 추가로 입힙니다. {c(AMBER, win + '초')} 동안 "
                  f"치지 않으면 왼손부터 다시 시작합니다. {c(GREEN, '체력 재생')}이 높습니다.",
        "skill": f"주변 적을 모두 {c(RED, '끌어당겨')} 맞부딪쳐 {c(ORANGE, E_DAMAGE)} + {ad(E_RATIO)} {c(ORANGE, '물리 피해')}"
                 f"를 입힙니다. 둘 이상 끌어오면 모두 {c(AMBER, stun_s + '초')} {c(RED, '기절')}, 아니면 "
                 f"{c(AMBER, f'{slow}%')} {c(RED, '둔화')}. 다음 두 주먹은 {c(ORANGE, '주먹다짐')}: {c(ORANGE, Q_DAMAGE)} + "
                 f"{ad(Q_RATIO)} + 최대 체력의 {c(AMBER, f'{Q_HP}%')} 추가 피해, 이동 속도 +{c(AMBER, f'{q_haste}%')}.",
        "skill2": grit(f"피해를 받으면 {c(YELLOW, '투지')}가 쌓입니다(최대 {c(AMBER, GRIT_MAX)}, {c(AMBER, grit_s + '초')} "
                       f"후 소멸). 투지를 소모해 ")
                  + f"{c(YELLOW, W_SHIELD)} + {ad(W_SHIELD_R, YELLOW)} {c(YELLOW, '보호막')}을 얻고 기를 모아 "
                  f"주먹을 날립니다: {c(ORANGE, W_SIDE)} + {ad(W_SIDE_R)} {c(ORANGE, '물리 피해')}, 중앙의 적은 "
                  f"{c(WHITE, W_TRUE)} + {ad(W_TRUE_R, WHITE)} {c(WHITE, '고정 피해')} 추가."
                  + grit(f" 투지 1당 보호막 +{c(YELLOW, W_SHIELD_K)} + {ad(W_SHIELD_KR, YELLOW)}, 고정 피해 "
                         f"+{c(WHITE, W_TRUE_K)} + {ad(W_TRUE_KR, WHITE)}."),
        "ult": f"적 챔피언을 붙잡아 {c(RED, '기절')}시키고 앞으로 내던진 뒤 뛰어올라 내리찍습니다. 주변 적은 "
               f"{c(ORANGE, R_DAMAGE)} + {ad(R_RATIO)} + 최대 체력의 {c(AMBER, f'{R_HP}%')} {c(ORANGE, '물리 피해')}를 입고 "
               f"{c(AMBER, f'{r_slow}%')} {c(RED, '둔화')}되며, 던져진 챔피언은 최대 체력의 {c(AMBER, f'{R_TARGET_HP}%')} "
               f"피해를 추가로 입습니다.",
    }, ("얼굴 깨기", "강펀치", "회심의 일격"))

    out["ja"] = ("セト", {
        "attack": f"パッシブ {c(ORANGE, 'ファイティングスピリット')}：左右の拳で交互に殴る。右の拳は素早く、{c(ORANGE, rd)} + {ad(rr)}の"
                  f"{c(ORANGE, '物理ダメージ')}を追加。{c(AMBER, win + '秒')}殴らないと左から。{c(GREEN, '体力自動回復')}が高い。",
        "skill": f"周囲の敵を全員{c(RED, '引き寄せ')}てぶつけ、{c(ORANGE, E_DAMAGE)} + {ad(E_RATIO)}の{c(ORANGE, '物理ダメージ')}。"
                 f"2体以上なら全員{c(RED, 'スタン')}{c(AMBER, stun_s + '秒')}、1体なら{c(AMBER, f'{slow}%')}{c(RED, 'スロウ')}。"
                 f"次の2発は{c(ORANGE, 'ナックルダウン')}：{c(ORANGE, Q_DAMAGE)} + {ad(Q_RATIO)} + 最大体力の"
                 f"{c(AMBER, f'{Q_HP}%')}を追加、移動速度+{c(AMBER, f'{q_haste}%')}。",
        "skill2": grit(f"被ダメージで{c(YELLOW, '闘魂')}を蓄積（最大{c(AMBER, GRIT_MAX)}、{c(AMBER, grit_s + '秒')}"
                       f"で消滅）。消費して")
                  + f"{c(YELLOW, W_SHIELD)} + {ad(W_SHIELD_R, YELLOW)}の{c(YELLOW, 'シールド')}、溜めて殴り{c(ORANGE, W_SIDE)} + "
                  f"{ad(W_SIDE_R)}の{c(ORANGE, '物理ダメージ')}、中央の敵には{c(WHITE, W_TRUE)} + {ad(W_TRUE_R, WHITE)}の"
                  f"{c(WHITE, '確定ダメージ')}も。" + grit(f"闘魂1につきシールド+{c(YELLOW, W_SHIELD_K)} + "
                  f"{ad(W_SHIELD_KR, YELLOW)}、確定+{c(WHITE, W_TRUE_K)} + {ad(W_TRUE_KR, WHITE)}。"),
        "ult": f"敵チャンピオンを掴んで{c(RED, 'スタン')}させ前方へ投げ、跳びかかって叩きつける。周囲の敵に{c(ORANGE, R_DAMAGE)} + "
               f"{ad(R_RATIO)} + 最大体力の{c(AMBER, f'{R_HP}%')}の{c(ORANGE, '物理ダメージ')}と{c(AMBER, f'{r_slow}%')}"
               f"{c(RED, 'スロウ')}、投げた相手には最大体力の{c(AMBER, f'{R_TARGET_HP}%')}を追加。",
    }, ("フェイスブレイカー", "ヘイメーカー", "ショーストッパー"))
    return out


def merged_text(raw):
    data = json.loads(raw)
    for lang, (name, desc, skills) in texts().items():
        data[lang]["description"][ID] = {"name": name, **desc}
        data[lang]["skill_name"][ID] = dict(zip(("skill1", "skill2", "ult"), skills))
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def nodes(e):
    if isinstance(e, dict):
        return (1 if "type" in e else 0) + sum(nodes(v) for v in e.values())
    if isinstance(e, list):
        return sum(nodes(v) for v in e)
    return 0


def shown(s):
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only compare the files with what this script writes")
    args = ap.parse_args()
    k = kit()
    kit_out = json.dumps(k, ensure_ascii=False, indent=2) + "\n"
    with open(TEXT, encoding="utf-8") as f:
        text_raw = f.read()
    text_out = merged_text(text_raw)
    if args.check:
        old = open(KIT, encoding="utf-8").read() if os.path.exists(KIT) else ""
        bad = [p for p, a, b in ((KIT, old, kit_out), (TEXT, text_raw, text_out)) if a != b]
        for p in bad:
            print("differs:", os.path.relpath(p, ROOT))
        sys.exit(1 if bad else 0)
    with open(KIT, "w", encoding="utf-8", newline="\n") as f:
        f.write(kit_out)
    with open(TEXT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text_out)
    print("wrote", os.path.relpath(KIT, ROOT), "and the league_sett text in", os.path.relpath(TEXT, ROOT))
    print("effect nodes:", {s: nodes(k[s]["effect"]) for s in ("attack", "skill", "skill2", "ult")})
    for lang, (_, desc, _) in texts().items():
        print(f"{lang:8s}", {s: shown(t) for s, t in desc.items()})


if __name__ == "__main__":
    main()
