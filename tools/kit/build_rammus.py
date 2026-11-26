"""Build league_rammus.data_champion (jungle, Melee tank, AP) from the parameters P.

    python tools/kit/build_rammus.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-19: jungle, layout A, the add-on league_rammus). TFM2 has three active slots for League's
four buttons: Q Powerball is `skill`, E Frenzying Taunt `skill2`, R Soaring Slam the `ult`; W Defensive Ball Curl has no
slot - the watch curls him up in fights (league_jarvaniv's Golden Aegis the same way). League V26.21 (2026-11-21, the
user: 「龙龟好像也没完全还原吧」, 「按照你的建议直接改就行了」): the passive is bonus attack damage from his armour and
magic resistance, W returns a flat hit to basic attackers and ends when he casts Q or R, Q rolls up to 6 s speeding up
from +0 and no E can be cast in the ball.
  passive Spiked Shell (锥刺甲壳): every attack adds p_dmg + p_ap% AP + p_hp% of his max health as magic damage (League
          since V25.12: bonus attack damage = 15% of his armour + 15% of his magic resistance; data reads neither, so
          the tank stat it can read stands in - league_malphite's way; the add-on gives League's attack damage).
  attack  a claw swipe (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; its champion-only twin marks
          the fight (`fight`, f_t ticks).
  W       Defensive Ball Curl (尖刺防御), automatic: w_cd off, not busy, not rolling (`q_ball`), an enemy champion within
          w_go: he curls up (skill_w) and for w_t ticks has +w_arm armour and +w_arm_p% armour, +w_mr magic resistance
          and +w_mr_p% magic resistance (League: 25-45 + 30-50% of his armour, 20-40 + 30-50% of his MR), and returns
          w_ref% of every hit taken (League: 15 + 10% armour + 10% MR magic damage to each basic attacker; the engine only
          has the percentage - league_annie's Molten Shield). w_cd counts from the cast (League's 7 s from the end: w_t +
          7 s); casting Q or R ends the curl (League) and its cooldown runs w_cd - w_t from then. With w_gate (the main
          pack) the watch curls only while Q is on cooldown (`q_cd`, q_cd ticks from Q's cast): the AI throws Q whenever
          it is up, so a curl before it would be cut short (League's Rammus curls after the roll). The copy has no gate:
          its AI hook keeps Q for a run-up (the AI's point-blank Q at a champion becomes an attack), so gated it would
          hardly ever curl; there the AI's Q ends the curl when it comes.
  skill   Q Powerball (动力冲刺), `Targeting` on `EnemyWithoutTower` (q_range): he curls into the ball (skill, q_curl
          ticks), then rolls at the target (`MoveToTarget` q_speed, skill_roll held) until he hits it: q_dmg + q_ap% AP
          to every enemy within q_r, knocked back (Knockback q_kb_speed x q_kb_t = League's 125 units), stunned
          q_stun ticks (League: "stunned and revealed for 0.4 seconds"; added 2026-11-14) and slowed
          q_slow% for q_slow_t; he bounces out of the ball (skill_hit) and keeps `q_on` for r_link ticks. League's ball
          rolls for up to 6 s, accelerating, wherever the player steers it: data cannot change the walk or idle
          picture while he moves, so the main pack rolls only inside the skill; the add-on rolls League's way (the
          whole body a ball while he walks, speeding up, until he touches an enemy).
  skill2  E Frenzying Taunt (狂乱嘲讽), `Targeting` on `EnemyChampion` (e_range): on e_rel the target is taunted for e_taunt
          ticks (League 1.2-2.0 s, no attack speed since V25.12; its damage to monsters is left out: the AI keeps E for
          champions).
  ult     R Soaring Slam (冲天猛撞), `Targeting` on `EnemyChampion` (r_range): he hops up and lands on the target
          (`MoveToTarget` r_speed, ult held): r_dmg + r_ap% AP to every enemy within r_r and r_slow% slow for r_slow_t;
          r_pulses aftershocks on the landing spot every r_pp ticks repeat the slow (League V25.12: the slow only).
          Within r_link ticks of a Powerball hit (League: cast during Powerball) the centre (r_c) also takes Q's damage
          again and is knocked up r_up ticks.
  watch   A life-long `AddCasted` started by his first attack or cast of each life (`init`), every watch_p ticks: casts W.
The add-on copy (--native, addons/league_rammus 0.2.0): the attack has no Spiked Shell magic - the passive
league_rammus:shell gives him p_ad_arm% of his armour + p_ad_mr% of his MR as attack damage (a buff kept up to date);
the curl has no percentage reflect - the passive returns w_hit + w_hit_arm% armour + w_hit_mr% MR magic damage to each
basic attacker while `w_on` is up; skill only curls him up and sets `q_ball` for q_ball_t ticks (League's 6 s) - the
passive speeds him up from +0 by q_acc0..q_acc1 (1/100 % a second, level 1..12) and, the moment his body comes within
q_touch of an enemy's (the gap between the two bodies; 26000 from his centre before 2026-11-05 - the ball never
rolled), lays the 1-tick `q_go` that a 1-tick watch of the cast turns into the impact (q_hit); the Q's target carries
`q_aim` so that enemies already against him as he curls up are no hit until they have been off him; his attack while
rolling is the impact too, and the add-on's AI hook turns the AI's E in the ball into that attack; the add-on's display
hook draws him as the ball (b_*) while `q_ball` is on and curled (c_*) while `w_on` is.
In both packs R cast while rolling (`q_ball`) ends the ball and counts as right after an impact (League: R during
Powerball).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_rammus.data_champion")
ID = "league_rammus"
FX = "asset/league/effects/league_rammus_fx"
BIG = "asset/league/effects/league_rammus_big"

# League units x 100 = ours for skill ranges (the pack's melee attack is 25000 against League's 125). Ticks from the
# strips (tools/art/rig_rammus.py MS): the tumble lands upside down on frame 3 at 180 ms (a_hit 11), Q curls in 200 ms
# (q_curl 12) and uncurls in 233 (q_end 14), E rears up on frame 2 at 70 ms (e_rel 5), W curls in 267 (w_dur 16), R's
# leap is 600 ms (r_dur 36) and its landing 233 (r_end 14). League's Rammus (V25): 675 +105 hp, 55 +3.5 AD, 35 +4.3 armour,
# 32 +2.05 MR, 335 move, attack speed 0.656.
# Numbers = the 10-min classic-SDK simulations (jungle lane 1 against demon, circus_blade, hunter, inquisitor and ninja,
# three lineups, both sides, seeds 1-8 and 9-16, 2026-10-19; league_jarvaniv +2.57 on seeds 1-8): the draft (hp 1100,
# atk 72, Q 70 +100%, R 100 +60%, shell 10 +20% +1% hp, W 40% / 15%) -0.82; Q 90 +110%, R 150 +80%, shell 15 +30% +2%,
# atk 78 +0.00; + hp 1200, W return 25%, Q cd 7 s +0.33; + Q 110, atk 84, hp 1250, taunt 1.5 s +1.30 / +1.82;
# + R 200 +90%, W 60% = P: +1.67 / +2.77 (about +2.2, Rek'Sai's +2.17).
P = {
    # stats (base tanks: attack 80 +6, hp 1100 +120, defence 40 +10, mr 30 +5; his armour is his trademark)
    "hp": 1250, "hp_g": 120, "atk": 84, "atk_g": 6, "mp": 30, "mp_g": 15, "def": 44, "def_g": 11, "mr": 30, "mr_g": 5,
    "ms": 1000, "ms_g": 11,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 70, "a_hit": 11, "f_t": 180,
    # passive Spiked Shell (the main pack: magic on every attack; League since V25.12: attack damage = 15% armour + 15% MR)
    "p_dmg": 15, "p_ap": 30, "p_hp": 2,
    # the add-on's Spiked Shell: League's attack damage from his armour and MR (League 15% each; this game's tanks have far
    # less armour and MR - his ~165 over a 10-minute game - so 15% gave ~25 attack against 0.1.x's ~59 magic a hit and
    # took the copy from +3.80 to +2.40 kills in the classic simulator; 35% gives ~60 and +3.85)
    "p_ad_arm": 35, "p_ad_mr": 35,
    # the add-on's rolling Powerball (League V26.21: rolls up to 6 s, its bonus move speed growing from +0 by 25% ->
    # 40.83% a second over levels 1-18 = ours 1-12, in 1/100 %; the touch is the gap between the two bodies)
    "q_ball_t": 360, "q_touch": 3000, "q_acc0": 2500, "q_acc1": 4083,
    # W Defensive Ball Curl (League V26.21: 7 s, +25-45 armour + 30-50% of his armour, +20-40 MR + 30-50% of his MR,
    # returns 15 + 10% armour + 10% MR magic damage to each basic attacker, ends on Q or R, cd 7 s after it ends).
    # The main pack returns w_ref% of every hit (data has no basic-attack hook); the add-on League's flat hit
    "w_cd": 840, "w_go": 30000, "w_dur": 16, "w_t": 420, "w_arm": 30, "w_arm_p": 40, "w_mr": 20, "w_mr_p": 40,
    "w_ref": 25, "w_hit": 20, "w_hit_arm": 10, "w_hit_mr": 10,
    # 1 = the main pack's watch curls only while Q is on cooldown (q_cd ticks from the cast): the AI throws Q whenever it
    # is up and Q ends the curl, so a curl before the Q is lost (League's Rammus curls after the roll). The copy keeps Q
    # for a run-up (the add-on's AI hook holds the AI's point-blank Q at a champion): gated it would hardly ever curl
    "w_gate": 1,
    # Q Powerball (League V26.21: rolls up to 6 s, its move speed growing, 80-240 + 100% AP r 250 on impact, knock-back
    # 125, stun 0.4 s, slow 40-80% 1 s, no E while rolling, ends W, cd 12-6)
    "q_cd": 420, "q_range": 45000, "q_far": 100000, "q_cd_far": 600, "q_curl": 12, "q_speed": 4000, "q_roll": 120, "q_end": 14, "q_r": 18000,
    "q_dmg": 110, "q_ap": 110, "q_slow": 40, "q_slow_t": 60, "q_kb_speed": 2500, "q_kb_t": 5,
    # League's Powerball also stuns what it hits: "stunned and revealed for 0.4 seconds" (the user, 2026-11-14, on the
    # list of differences from League: 「全改吧」; before: the knock-back and the slow only)
    "q_stun": 24,
    # E Frenzying Taunt (League: 325 range, taunt 1.2-2.0 s, cast 0.25 s, cd 12)
    "e_cd": 720, "e_range": 32500, "e_dur": 20, "e_rel": 5, "e_taunt": 90,
    # R Soaring Slam (League V26.21: 800 range (+ move speed), 150-350 + 60% AP r 400, slow 30-50% 1.5 s, 3 aftershocks
    # over 3.5 s that only renew the slow (V25.12); during Powerball the centre r 200 takes Q's damage and is knocked up
    # 0.75 s; ends W; cd 120-90)
    "r_cd": 3600, "r_range": 60000, "r_dur": 36, "r_speed": 4000, "r_end": 14, "r_r": 36000, "r_c": 18000,
    "r_dmg": 200, "r_ap": 90, "r_slow": 40, "r_slow_t": 90, "r_up": 45, "r_pulses": 3, "r_pp": 70, "r_link": 90,
    # the watch
    "watch_p": 12,
    # his sounds, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_rammus
    "native": 0,
}


# the numbers the add-on reads from the copy's passive.params (league_rammus::Params; make_override.py checks its
# defaults against these)
NATIVE_KEYS = ("p_ad_arm", "p_ad_mr", "q_acc0", "q_acc1", "q_ball_t", "q_touch", "w_hit", "w_hit_arm", "w_hit_mr", "w_t")


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


def ap(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def decoy(dmg, ratio):
    """The damage the game's AI reads for this action (build_gangplank.py's way): its estimate follows a SwitchByBuff by
    the flags he has while it reads, and its battle plan divides an enemy's health by his attack's estimate - in the
    copy his attack while rolling was the impact flag alone and read 0 (classic simulator, 2026-11-21: "attempt to
    divide by zero" at game_core plan_legacy/sub_plan/battle.rs:1938 while he rolled, the 0.1.x copies too). A flag he
    never has while it reads; on the cast the flag is up and the hit is skipped, so nothing he does changes."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), attack(dmg, ratio)), *rm("x"))


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


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def anchor(name, *end):
    """League_ekko's anchor: a 1-unit line that ends on his own spot the tick it starts; its end_effects act there."""
    return {"type": "LinearProjectile", "name": n(name), "speed": 1, "range": 1, "y_offset": 5000, "penetrate": True,
            "shape": circle(1000), "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": list(end)}


def voice(name, p):
    """His sound, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def build(p):
    nat = bool(p["native"])
    marked = [refresh("fight", p["f_t"])]
    slow = lambda name, pct, t: buff(name, t, move_speed_mult=-pct)

    # ------------------------------------------------------------------ W: Defensive Ball Curl (cast by the watch)
    # the copy's curl returns League's flat hit from the add-on (no share of every hit)
    reflect = {} if nat else {"damage_reflect": p["w_ref"]}
    curl = combine(flag("w_cd", p["w_cd"]), refresh("busy", p["w_dur"]), anim("skill_w", p["w_dur"]), sfx("w"),
                   voice("vo_w", p), cview("w_cast"),
                   refresh("w_on", p["w_t"], defence=p["w_arm"], defence_mult=p["w_arm_p"], magic_resistance=p["w_mr"],
                           magic_resistance_mult=p["w_mr_p"], **reflect))
    # not while rolling (League: W in the ball ends the ball; here the ball goes on)
    gate = bool(p["w_gate"]) and not nat
    look = pick(p["w_go"], "EnemyChampion", on_me(curl))
    if gate:
        look = sw("q_cd", look)
    watch = on_me(casted(1000000, p["watch_p"], sw("w_cd", NONE, sw("busy", NONE, sw("q_ball", NONE, look)))))
    life = sw("init", NONE, combine(flag("init", None), watch))
    # League: casting Q or R ends the curl, and its cooldown (7 s after it ends) runs from then
    end_w = sw("w_on", combine(*rm("w_on", "w_cd"), flag("w_cd", p["w_cd"] - p["w_t"])))

    # ------------------------------------------------------------------ attack: the claw swipe + Spiked Shell
    # the copy's Spiked Shell is attack damage the add-on keeps on him: no magic on the attack
    shell = [] if nat else [ap(p["p_dmg"], p["p_ap"], p["p_hp"])]
    blow = combine(sfx("a_swing"), homing("a_blow", "Enemy", [attack(0, 100), *shell, view("a_hit"), tsfx("a_hit")]),
                   homing("a_twin", "EnemyChampion", marked))
    if nat:
        # rolling, his attack is the ball's impact (League: Powerball stops on the first enemy it meets); the decoy keeps
        # the AI's reading of it from 0 (0.2.0: the classic simulator's battle plan divided by it while he rolled)
        blow = sw("q_ball", combine(refresh("q_go", 2), decoy(0, 100)), blow)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, delayed(p["a_hit"] - 1, blow)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Powerball
    q_hit = [anim("skill_hit", p["q_end"]), *rm("q_ball"), refresh("q_on", p["r_link"]), sfx("q_hit"),
             cview("q_burst"),
             around(p["q_r"], "EnemyWithoutTower", [ap(p["q_dmg"], p["q_ap"]),
                                                     {"type": "Knockback", "speed": p["q_kb_speed"],
                                                      "tick": p["q_kb_t"]},
                                                     {"type": "Stun", "duration": p["q_stun"]},
                                                     slow("q_slow", p["q_slow"], p["q_slow_t"]), view("q_hit")]),
             around(p["q_r"], "EnemyChampion", marked)]
    if nat:
        # the add-on rolls him (the ball while he walks) and lays a 1-tick `q_go` when he touches an enemy: a 1-tick
        # watch of this cast turns it into the impact
        roll = [refresh("q_ball", p["q_ball_t"]), cview("q_dust"),
                on_me(casted(p["q_ball_t"] + 2, 1, sw("q_go", combine(*rm("q_go"), *q_hit))))]
    else:
        roll = [refresh("q_ball", p["q_roll"]), anim("skill_roll", p["q_roll"]), cview("q_dust"),
                {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] + 60000, "end_effects": q_hit}]
    # the add-on: the target carries q_aim through the curl (the passive reads it on the ball's first tick)
    aim = [buff("q_aim", p["q_curl"] + 2)] if nat else []
    # 附加包副本的 Q 射程放到 q_far（2026-11-21，用户：「改，滚久一点」）：AI 钩子从这么远就开球滚过去，游戏的 AI 自己也会从远处按；
    # 冷却跟着从 7 秒拉到 q_cd_far 10 秒（英雄联盟 12-8.8 秒）：滚得久了在经典引擎里击杀差 +3.97 -> +5.02（种子 1-12），10 秒两批合起来 +4.18 -> +4.50。
    # 主包的 Q 是一次冲到目标的冲刺，射程、冷却都不变
    skill = action("skill", p["q_curl"], p["q_cd_far"] if nat else p["q_cd"], 1, p["q_far"] if nat else p["q_range"], "Targeting",
                   "EnemyWithoutTower",
                   combine(life, end_w, *([refresh("q_cd", p["q_cd"])] if gate else []), refresh("busy", p["q_curl"] + 10),
                           sfx("q"), voice("vo_q", p), *aim,
                           delayed(p["q_curl"] - 1, alive(*roll))))

    # ------------------------------------------------------------------ skill2: E Frenzying Taunt
    taunt = [{"type": "Taunt", "duration": p["e_taunt"]}, buff("e_taunt", p["e_taunt"]), view("e_hit"),
             tsfx("e_hit")] + marked
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(life, refresh("busy", p["e_dur"]), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(homing("e_taunt", "EnemyChampion", taunt)))))

    # ------------------------------------------------------------------ ult: R Soaring Slam
    shock = [slow("r_slow", p["r_slow"], p["r_slow_t"]), view("r_hit")]
    after = anchor("r_anchor", field("r_after", p["r_r"], p["r_pulses"] * p["r_pp"], p["r_pp"], shock),
                   *[delayed(k * p["r_pp"], view("r_shock")) for k in range(1, p["r_pulses"] + 1)])
    centre = sw("q_on", around(p["r_c"], "EnemyWithoutTower", [ap(p["q_dmg"], p["q_ap"]),
                                                                {"type": "Airborne", "duration": p["r_up"]}]))
    land = [anim("ult_land", p["r_end"]), sfx("r_land"), view("r_land"),
            around(p["r_r"], "EnemyWithoutTower", [ap(p["r_dmg"], p["r_ap"]), *shock, tsfx("r_hit")]),
            around(p["r_r"], "EnemyChampion", marked), centre, *rm("q_on"), after]
    ult = action("ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(life, end_w, sw("q_ball", combine(*rm("q_ball"), refresh("q_on", p["r_link"]))),
                         refresh("busy", p["r_dur"] + p["r_end"]), anim("ult", p["r_dur"]), sfx("r"),
                         voice("vo_r", p), flag("r_air", p["r_dur"], cc_immune=True),
                         {"type": "MoveToTarget", "speed": p["r_speed"], "range": 400000, "end_effects": land}))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_e = [E("a_hit"), E("q_dust", FX, -1), E("q_hit"), E("q_burst", BIG, -1), E("e_hit"), E("w_cast", BIG, 2),
               E("r_land", BIG, -1, False), E("r_shock", BIG, -1, False), E("r_hit")]
    views_b = [B_("w_on", FX, 3), B_("e_taunt", FX, 3), B_("q_slow", FX, 3), B_("r_slow", FX, 3)]
    extra = {}
    if nat:
        extra["passive"] = {"passive_ref": f"{ID}:shell", "params": {k: p[k] for k in NATIVE_KEYS}}
    return {
        "id": ID, "category": "Tank", "tags": ["AP", "Magic", "Melee", "Tank", "CC"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
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
