"""Build league_azir.data_champion (mid, Magician: the Emperor of the Sands) from the parameters P.

    python tools/kit/build_azir.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-23: MID, layout C - Conquering Sands / Shifting Sands / Emperor's Divide, Arise! and the
Sun Disc in the passive; combos E -> R, Q's landing -> the soldiers stab, R -> Q, E's hit -> one more soldier; R pushes
both ways: 「还有要会正会推和反面推 可以推回来英雄 大招」). TFM2 has three active slots: Conquering Sands (Q) is `skill`,
Shifting Sands (E) `skill2`, Emperor's Divide (R) the `ult`.
  passive Arise! (沙兵现身, W folded in): sand soldiers. Data has no summons: a soldier is a spot - a hidden lob's landing
          - holding a flat list of checkpoints every s_step ticks that re-stamp its picture (league_orianna's lying ball)
          and two stab zones (`RangePeriodProjectile`, champions first, league_illaoi's tentacles) for s_life ticks. Three
          slots a-c (`b<s>`, s_life ticks): a new soldier takes the first free one, so at most three stand. His attack
          raises `cmd` for cmd_t ticks: every soldier with an enemy within s_r stabs ONE of them then (the slot's lock
          `k<s>`), s_dmg + s_ap% AP; when no soldier stabbed (`stabbed`) his own sand bolt flies instead (100% AD;
          League: soldiers attack for him when the target is in their reach). Only the soldiers he stands within League's
          tether radius of stab (660, SoldierDeactivationRange: s_tie from the zone's centre plus his body; until
          2026-11-04 a soldier 169000 off stabbed too - 19 of 130 stabs in one classic game came from past 66000). An
          attack with p_cd off raises a soldier by the enemy (2026-11-17, the user's pick 「召兵位置和时长照联盟」, League's
          W: a spot within 500 of him, by the enemy, 10 s): a hidden bolt from his feet toward the target stops on the
          first enemy on its way, s_stop from it, else s_place (League's 500) out. Until 2026-11-17 it rose s_place
          30000 in front of him whatever stood there (behind a target closer than that), and lived 480 ticks (8 s); on
          the target's own spot (October's first draft) it stood inside it. League: W, two charges - not here (an
          auto-battler: the attacks raise them).
          Generations: every soldier belongs to the generation that was up when it rose - gA, gB, gC or none of them (D)
          - and its checkpoints and zones go on only while that generation is up. Q moves the soldiers by starting the
          next generation (A -> B -> C -> D -> A): the old ones stop at their next checkpoint and new ones rise where Q
          lands. A generation comes back after four Qs, at least 2 x q_cd apart (one may be refunded by R), and its old
          soldiers are gone by then while s_life <= 2 x q_cd + s_step (build() checks it; three generations until
          2026-11-17, when s_life 600 passed q_cd + s_step).
          2026-11-20（用户：「改成联盟的」）：Q 挪过去的沙兵不再重新算 10 秒。联盟的沙兵从召出来起就是 10 秒，挪到哪都不续。
          所以挪的时候不再把槽位的 b<s> 续满，挪过去的那一代沙兵只在 b<s> 还在的时候刺、盖画面，原来的 10 秒到了就没了。
          槽位空出来以后召的新兵会挂上 z<s>，老的那个不会跟着又活过来（它的区域还在，只是一直关着）。离 10 秒到头已经不够
          冲一次（w<s> 没了）的沙兵不挪，Q 换代时就没了。以前每挪一次都是新的 10 秒。
          The Sun Disc (太阳圆盘): the add-on's copy only (--native, the passive league_azir:disc - a tower ruin of his
          team; data cannot see towers).
  The controller. skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on the hero is not
          (league_orianna): his attacks hang one on him (ctl_t ticks, period ctl_p) unless `polling` says one runs. It
          runs Q's move (q_go) and E's soldier (e_go); the slots only raise those flags. With no controller yet in this
          life Q is the sand wave alone and E brings no soldier.
  attack  A sceptre point (`Targeting` on `Enemy`): the soldiers stab, else his bolt (a_rel).
  skill   Q Conquering Sands (狂沙猛攻, the slot's cooltime q_cd): a `Targeting` cast on `EnemyWithoutTower` (q_range). A
          sand wave flies at the target through everything, q_dmg + q_ap% AP and q_slow% for q_slow_t (League: the
          soldiers' paths, 25% slow 1 s). At an enemy champion the controller then moves every standing soldier to a
          champion's spot in Q's range (q_travel ticks; with none standing it raises one there), and they stab at once
          (Q -> stab). The main pack's controller cannot tell Q's target from the other units (the skill's tree, copied
          every tick, cannot hold the move): a random enemy champion within q_range, usually the one aimed at.
          The add-on's copy (0.3.0, the user's pick 「Q 沙兵真的冲过去」, 2026-11-17): the move goes to whatever enemy Q
          aimed at (league_azir:q_go records it; the controller offers every enemy within reach to league_azir:q_pick,
          which flags `qt` on that one, or the nearest to where it stood if it died) and the add-on draws each soldier
          sliding there from its spot (league_azir:q_fly when the hidden lob leaves, then dash_<s> every ss_dash ticks):
          every enemy within q_w (plus its body) of a soldier's path takes q_dmg + q_ap% AP and the slow as the soldier
          passes, once a cast however many paths cross it (League's Conquering Sands). With soldiers to move, no wave;
          with none (or no controller yet: Q before his first attack in a life) the wave as in the main pack. They stab
          on landing only where Q aimed at a champion (`qc`, hung by league_azir:q_pick until they land): the combo as
          it was (the main pack moves them onto champions only), no free stab into every minion wave Q aims at. A Q
          that skipped its wave and found nothing to move to deals its damage and slow on its target (`Q OWED`).
  skill2  E Shifting Sands (流沙移形, cooldown flag `e_cd`): a `Targeting` cast on `EnemyChampion` (e_range), only with
          a soldier standing (League: the dash goes to a soldier). A champion within e_self of him: he hops away
          (MoveBack) behind a shield. Else, with R ready (no `r_cd`), he dashes onto the champion behind e_sh + e_ap% AP of
          shield for e_t: e_dmg + e_ratio% AP round him on arrival, a soldier rises on the champion (E hit -> one more
          soldier) and `r_win` opens for win_r ticks (E -> R).
  ult     R Emperor's Divide (禁军之墙): a `Targeting` cast on `EnemyChampion` (r_range). A wall of guards charges from him
          toward the champion: r_dmg + r_ratio% AP and a Knockback (r_kb_speed x r_kb, away from him) on every enemy it
          meets. Two pushes: with `r_win` up (he just dashed onto the champion with E) he first rushes through it
          (`RushMoveToBack`, r_rush_at - league_leesin's insec) and the wall pushes it back toward his team (反推);
          otherwise the wall pushes them away from him (正推: peels a diver, or shoves a fight apart). Every champion the
          wall meets refunds Q (`q_ref`, skill_cooldown_mult q_refund for 2 ticks: R -> Q; ult_cooldown_mult -q_refund keeps
          R's own cooldown - without it the cap cut R's 40 s to 4, 2026-10-25).
The add-on copy (--native, addons/league_azir): the passive league_azir:disc raises the Sun Disc on a fallen tower of his;
the wall stands r_hold ticks where it stops (r_half either side) and enemy champions cannot walk through it (League's
Emperor's Divide; the data's wall is gone the tick it stops and they walk straight back), and every enemy the wall hits
is carried past where it stops (no Knockback, which goes r_kb_speed x r_kb from where it hits: 12 of 24 champion hits in
the classic sim ended short of the standing wall, on his side - the user, 2026-10-29: 「压根推不走人也推不回来人」): the
passive sweeps the wall's path (r_w round its centre, r_speed a tick, as the data's wall flies) and league_azir:r_carry
on the wall's hit is a second way in (0.1.5 had only that one, and it never ran in game); the insec's rush is
league_azir:r_behind - round the target to the side away from his team (his champions within reach, else his nearest
tower), r_behind past it - in place of RushMoveToBack (away from where he came from: E overshooting or coming from the
side kicked them sideways or away, 7 of 21 insecs in the user's games of 2026-10-28);
the soldiers' rise, checkpoints and stabs call league_azir:rise_<s> / sold_<s> / stab_<s> instead of the front pictures,
and the add-on draws each soldier from the side, facing the nearest enemy and stabbing when it strikes (the user:
「沙兵没攻击动作 ... 还有不面向敌人」; data cannot tell left from right, so the main pack keeps them facing the camera);
0.2.0: a soldier he leaves out of reach for 30 ticks, or one an enemy tower aged out (League: twice as fast in a turret's
range), crumbles - the add-on hangs `x<s>` on him and the copy's stabs, Q's move and E's need of a soldier skip it until
the slot's next soldier rises (`kept`);
0.3.0 (2026-11-17, the user's pick 「沙兵刺击穿透一条线」): a soldier's stab goes on through its target - every other enemy
within s_line (plus its body) of the line from the soldier through the one stabbed, s_r long, takes the stab too, each
once a stab (league_azir:stab_<s>: the data's stab on the one it picked unchanged); Conquering Sands' dash (skill, above).
Action tags (the art): idle run attack hit dead skill skill2 ult.
Numbers: League 16.20 (CommunityDragon azir.bin) read into the Magician mid range (league_hwei, league_orianna);
balanced on the classic-SDK simulations (kd.py --lane 2, C:/t/az_sim, 2026-10-23; league_hwei +1.16 on the same games): the
draft -3.77 (the soldiers stab, every slot casts, too little damage); without E -2.30 against -2.08 (E about even), without
R -2.88 (R worth ~0.8); the stab is the lever (25+45% -> 65+90% AP), then reach 36000, a soldier every 150 ticks, attacks
every 80, more health and armour: +0.45 seeds 1-8, +1.53 seeds 9-16. The soldiers then raised in front of him (s_place,
not on their target: they stood inside it) lost ~0.85 (the target walks out of a spear further off); their reach 42000,
the stab 75 + 100% AP and 1150 health: +1.18 on seeds 1-24 (league_hwei +1.16 / +1.38 on seeds 1-8 / 17-24).
2026-10-25: R's cooldown really runs now (R -> Q's refund capped it to a tenth, 10.6 casts a game -> 6.5); r_cd 2400 ->
1800: +1.34 / +0.92 -> +1.02 / +0.43 (seeds 1-8 / 9-16).
2026-11-17 (the user's picks 「Q 沙兵真的冲过去」「沙兵刺击穿透一条线」「召兵位置和时长照联盟」; the classic simulator rebuilt in
C:/t/azir_sim from the kept ks_sim, its map_setting from the game's bundle; kd.py --lane 2, 720 games a seed set): the main
pack before +0.14 on seeds 1-24 and on 25-48 (deal 9980 / 9809, the 11-04 figure again); with the soldiers by the target,
10 s and four generations +0.60 (deal 10420); then the stab s_dmg + s_ap% at 75 + 90 +0.61, 73 + 86 -0.28, 72 + 84
+0.02 (-0.12 on 25-48), 70 + 80 -0.15 (seeds 1-24; neighbours differ by ~0.3 of noise; 73 + 86 +0.21 on 25-48):
the stab 74 + 88%, +0.37 / -0.11 on seeds 1-24 / 25-48 (deal 9777 / 9926; their mean +0.13 against +0.14 before).
The add-on's copy, measured with the add-on emulated in the classic engine (sim3az: src/az_emul.rs runs the copy's line
stab, Q's aim and its paths' damage - all at once as the soldiers leave, where the add-on deals as each one passes - and
swaps the wall's natives back to the main pack's Knockback / RushMoveToBack; the 0.2.6 copy measured that way +0.06, deal
10008): +2.20 with the main pack's old numbers (deal 13274; Q moved the soldiers 39-41 times a game against the main
pack's ~13, each move a fresh 10 s on the target; without the line +2.25 - the line adds farming, cs 69 -> 75), +2.33 with
the landing's stab on champions only (`qc`: balance-neutral, the combo as it was) - so the copy has its own stab and Q
(n_*): 60 + 80 / 90 + 50 +1.08, 50 + 60 / 75 + 40 -0.43 (both before `qc`), 54 + 68 / 80 + 44 +0.10 (deal 10387; +0.33 on
seeds 25-48).
2026-11-20（Q 挪过去的沙兵不再重新算 10 秒，同一个模拟器 C:/t/azq_sim，每组 720 局）：改动前的副本重跑一遍还是 +0.10（和 11-17
一样，模拟器能原样复现）。改完数字不动：副本 +0.72，反而强了。挪过的兵不再一直占着槽位，普攻在眼前的目标旁边召新兵多了
（每局 49 -> 73 个），刺得更准。所以副本的刺击往下调：50 + 62% -0.09，52 + 65% +0.12 / +0.07（种子 1-24 / 25-48，伤害
10489 / 10362），定 52 + 65%（改动前两组的平均约 +0.22，差距在误差里）。主包的 Q 只挪向英雄（每局十几次），数字不动：
+0.20（种子 1-24，改动前 +0.37）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_azir.data_champion")
ID = "league_azir"
FX = "asset/league/effects/league_azir_fx"
BIG = "asset/league/effects/league_azir_big"
SOLDIER = "asset/league/effects/league_azir_soldier"   # a soldier: soldier_<s> standing, soldier_<s>_rise out of the sand
GUARD = "asset/league/effects/league_azir_guard"       # R's three guards from the side: charge_<r|l>_<a|b> (one hop each)
DISC = "asset/league/effects/league_azir_disc"         # the Sun Disc (the add-on's): disc_rise, disc
SIDE = "asset/league/effects/league_azir_soldier_side"  # the add-on's soldier from the side: stand / rise / stab, _r / _l

# League's Azir (16.20, CommunityDragon azir.bin): 575 +119 hp, 52 AD, 19 armour, 30 mr, 335 move, 525 range.
# W: soldiers 10 s, 2 charges, stab 50-170 + 55% AP (more soldiers on one target 25% each), reach 325. Q 740 range,
# 70-310 + 30% AP, 25% slow 1 s, cd 14-6. E 1100 dash, shield 80-320 + 70% AP 1.5 s, 60-260 + 40% AP, cd 22-16; a
# champion hit stops him and readies a soldier. R 200-600 + 75% AP, wall 600 wide pushed 250 forward, cd 120-90.
P = {
    # stats (Magician mid: league_hwei 940 +94 hp, league_orianna 860 +95, 76 +6 attack, 40 +20 ap)
    "hp": 1150, "hp_g": 92, "atk": 62, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 27, "def_g": 6, "mr": 28, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 52500, "atk_dur": 27, "atk_cd": 80, "a_rel": 10, "a_speed": 4500, "a_y": -3000,
    # passive: the soldiers
    "p_cd": 150, "s_life": 600, "s_step": 40, "s_r": 42000, "s_per": 2, "cmd_t": 2, "s_dmg": 74, "s_ap": 88,
    # where a soldier rises (2026-11-17, the user's pick 「召兵位置和时长照联盟」: League's W puts it at a spot within 500 of
    # him, by the enemy; s_life 480 -> 600, League's 10 s): a hidden bolt from his feet toward the attack's target stops on
    # the first enemy it meets, s_stop from that unit's centre (plus its body in the classic engine: 0.7.x's own data
    # projectiles measure the centre alone, akshan R 11-06), else at s_place (League's 500); until 11-17 s_place 30000
    # in front of him whatever stood there
    "s_place": 50000, "s_speed": 6000, "s_stop": 16000,
    # the add-on's line stab (League: a soldier attacks in a line through its target): every other enemy within s_line
    # (plus its body) of the line from the soldier through the one stabbed, s_r long, takes the stab too
    "s_line": 5000,
    # the add-on's copy's own stab and Q (0.3.0): there the soldiers stab through a line and every Q dashes them (at any
    # target, their paths dealing Q, a stab on landing), so each hit is lighter - balanced on the classic engine with the
    # add-on emulated (sim3az, the docstring); the main pack keeps s_dmg / s_ap / q_dmg / q_ap
    "n_s_dmg": 52, "n_s_ap": 65, "n_q_dmg": 80, "n_q_ap": 44,
    # s_ap 100 -> 106 with the tether (2026-11-04): the soldiers past 660 had dealt 6.5% of his damage (classic seeds 1-24,
    # 720 games: kill difference +0.14 -> +0.06, back to +0.14 at 106); s_dmg 75 -> 74, s_ap 106 -> 88 on 2026-11-17 (the
    # soldiers by the target for 10 s: +0.14 -> +0.60, back to +0.37 / -0.11 on seeds 1-24 / 25-48 - the docstring's Numbers)
    # League's tether radius (Arise!'s 660, azir.bin SoldierDeactivationRange; 1 League unit = 100): a soldier stabs only
    # while he stands within s_tie of its spot plus his body (the pick from the stab zone counts his radius, 10000:
    # 66000 centre to centre); the add-on draws the line and crumbles the soldier by the same distance
    "s_tie": 56000,
    # the add-on's soldiers from the side (addons/league_azir; tools/art/design_azir_side_soldier.py): ticks a standing
    # stamp, the rise and the stab last (a stamp every ss_stand ticks faces the nearest enemy; a stab starts on one); 0.3.0:
    # a dash stamp with Conquering Sands (a stamp every ss_dash ticks along its path: smooth at 30 a second)
    "ss_stand": 4, "ss_rise": 20, "ss_stab": 16, "ss_dash": 2,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # skill: Q Conquering Sands
    "q_cd": 480, "q_range": 75000, "q_dur": 24, "q_rel": 8, "q_speed": 5000, "q_w": 9000, "q_dmg": 110, "q_ap": 65,
    # q_travel: the soldiers' dash, 12 -> 18 ticks on 2026-11-17 (League's soldiers cross ~500 in 0.3 s; the add-on draws
    # them sliding all the way)
    "q_slow": 25, "q_slow_t": 60, "q_travel": 18,
    # skill2: E Shifting Sands
    "e_cd": 900, "e_range": 55000, "e_dur": 24, "e_go_at": 6, "e_speed": 5000, "e_self": 25000, "e_back": 3500,
    "e_back_t": 8, "e_sh": 80, "e_ap": 60, "e_t": 90, "e_r": 18000, "e_dmg": 90, "e_ratio": 55, "e_near": 20000,
    "win_r": 90,
    # ult: R Emperor's Divide
    "r_cd": 1800, "r_range": 40000, "r_dur": 36, "r_at": 16, "r_rush_at": 6, "r_rush": 8000, "r_speed": 3000,
    # r_hold: the add-on's wall stands 300 ticks where it stops (League's WallDuration 5 s since V10.1; 180 before 0.2.0)
    "r_len": 60000, "r_w": 20000, "r_behind": 15000, "r_hold": 300, "r_half": 30000, "r_dmg": 260, "r_ratio": 90, "r_kb_speed": 3000, "r_kb": 18, "r_stamps": 5,
    "q_refund": 900,
    "vo_gap": 600,
    # the Sun Disc (the add-on's passive league_azir:disc; League: Shurima's Legacy on a turret's ruins): with Azir within
    # d_near of a fallen tower - his, or the enemy's outside their base (0.2.0; before, his only) - it rises there for
    # d_life ticks and strikes the nearest enemy (champions first) within d_range every d_per ticks for d_dmg + d_ap% AP
    # magic damage; again d_cd ticks after it rose (League's 90-second cooldown; before 0.2.0 once a game)
    "d_life": 2700, "d_per": 60, "d_range": 45000, "d_dmg": 50, "d_ap": 35, "d_near": 60000, "d_cd": 5400,
    # 1 = the copy for addons/league_azir
    "native": 0,
}
SLOTS = "abc"
# four generations since 2026-11-17 (s_life 600 > q_cd + s_step: with three, a generation could come back after a Q, an R
# refund and a Q while its old soldiers still stood): one comes back after four Qs, at least 2 x q_cd apart (build())
GENS = "ABCD"
NATIVE_KEYS = ("d_life", "d_per", "d_range", "d_dmg", "d_ap", "d_near", "r_speed", "r_len", "r_stamps", "s_step",
               "ss_stand", "ss_rise", "ss_stab", "r_rush", "r_behind", "r_hold", "r_half", "r_w", "s_life", "s_tie", "d_cd",
               # 0.3.0 (2026-11-17): the line stab and Conquering Sands' dash are the add-on's
               "s_dmg", "s_ap", "s_r", "s_line", "q_dmg", "q_ap", "q_w", "q_slow", "q_slow_t", "q_travel", "ss_dash")


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


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, from_projectile=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": from_projectile,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*rm("lives"), *effects)),
                   *rm("lives"))


def tied(reach, *effects):
    """In a stab zone's applied effects: run only while he stands within `reach` of the zone's centre - the soldier's
    spot - plus his body (`RandomTarget AllyOnlySelf from_projectile`: champion-data, league_ekko W's measure). League's
    Arise! commands only the soldiers within its tether radius (660, `SoldierDeactivationRange`): one farther off does
    not attack."""
    return combine(pick(reach, "AllyOnlySelf", flag("tie", 1), from_projectile=True),
                   sw("tie", combine(*rm("tie"), *effects)), *rm("tie"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def nat(what):
    """The add-on's native effect `league_azir:<what>` (the --native copy only)."""
    return {"type": "Native", "effect_ref": f"{ID}:{what}"}


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end=(), y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": True, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def place(name, speed, rng, end):
    """A hidden bolt that flies rng toward the target and hits nothing: its end_effects run where it stops."""
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": 0, "penetrate": True,
            "shape": circle(1), "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": list(end)}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden 1-radius lob onto the target's spot: its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


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


FLAGGED = GENS[:-1]     # each generation but the last has its flag g<G>; the last is up when none is


def gate(g, effect):
    """Only while generation g is up: g<G>, or none of the flags for the last one."""
    if g in FLAGGED:
        return sw("g" + g, effect)
    out = effect
    for h in reversed(FLAGGED):
        out = sw("g" + h, NONE, out)
    return out


def by_gen(make):
    """make(g) for the generation up now."""
    out = make(GENS[-1])
    for g in reversed(FLAGGED):
        out = sw("g" + g, make(g), out)
    return out


NEXT = {g: GENS[(i + 1) % len(GENS)] for i, g in enumerate(GENS)}
# the add-on's copy offers Q's move every enemy this much past Q's reach (its target may have stepped on before the
# controller's next run)
Q_REACH = 20000


def to_gen(g):
    """Start generation g (the old one's soldiers stop at their next checkpoint)."""
    return combine(*rm(*("g" + h for h in FLAGGED)), *([flag("g" + g, None)] if g in FLAGGED else []))


def build(p):
    # a generation comes back after len(GENS) Qs: one of those cooldowns may be all but gone (R's refund, q_ref), the others
    # run q_cd each - its old soldiers (s_life, the last checkpoint s_step before) must be gone by then
    back = (len(GENS) - 2) * p["q_cd"] + p["s_step"]
    if p["s_life"] > back:
        raise SystemExit(f"s_life > {back} ((generations - 2) x q_cd + s_step): a generation could come back while its "
                         "old soldiers stand")

    # ------------------------------------------------------------------ passive: the soldiers
    # the stab's and Q's numbers: the copy's own with the add-on (its line stab, its dash: n_*), else the main pack's
    sd, sa, qd, qa = ((p["n_s_dmg"], p["n_s_ap"], p["n_q_dmg"], p["n_q_ap"]) if p["native"] else
                      (p["s_dmg"], p["s_ap"], p["q_dmg"], p["q_ap"]))
    stab = [ap(sd, sa), view("s_stab"), tsfx("s_stab"), refresh("stabbed", 6)]

    def kept(s, effect):
        """The add-on's copy: only while slot s's soldier has not crumbled (the add-on hangs `x<s>` on him when it does:
        out of his reach too long, or aged out by an enemy tower; the slot's next soldier takes it off as it rises)."""
        return sw(f"x{s}", NONE, effect) if p["native"] else effect

    def commanded(s, effect):
        """The add-on's copy (0.2.1): only while slot s's soldier stands within his reach this tick (the add-on hangs
        `o<s>` on him every tick it is out, off when it is back): the tied() pick below is looser in the game than the
        add-on's centre-to-centre measure (7 stabs a day at 67157-75253 from him, all in the window before the crumble)."""
        return sw(f"o{s}", NONE, effect) if p["native"] else effect

    # 能被 Q 挪的沙兵：离 10 秒到头至少还有一次冲刺加一点余量（w<s>，召兵时挂）
    movable_t = p["s_life"] - p["q_travel"] - 4

    def lives(s, effect):
        """挪过去的沙兵还活着：槽位的 b<s> 还在（从它最早召出来算的 10 秒），这个槽位之后也还没召过新兵（z<s>）。"""
        return sw(f"z{s}", NONE, sw(f"b{s}", effect))

    def soldier(s, g, moved=False):
        """Slot s's soldier of generation g on this spot (a landing's end_effects): its picture re-stamped every
        s_step ticks and two stab zones (champions first), all only while g is up. `moved`: one Conquering Sands brought
        there - the add-on's copy draws it arriving from its old spot (league_azir:dash_<s>), no sand pile."""
        # the add-on's copy draws the soldier itself, from the side (it faces the nearest enemy, it stabs): its natives
        # take the spot (the rise, every checkpoint) and the unit stabbed
        native = lambda what: {"type": "Native", "effect_ref": f"{ID}:{what}_{s}"}
        told = [native("stab")] if p["native"] else []
        # the zones come from the landing's end_effects and outlive him, and a dead caster's flags freeze: killed inside
        # the 2 ticks of `cmd` with a soldier that had nobody to stab, `k{s}` could not be set again and that soldier
        # stabbed everyone near it every 2 ticks to its end (classic engine 2026-11-02: 44 stabs after one death) - so
        # past the two flags it asks alive() (league_maokai's sapling); then whether he stands within League's tether
        # radius of it (tied: s_tie from the zone's centre plus his body = 660), and in the add-on's copy whether it
        # crumbled (kept) or stands out of his reach this tick (commanded)
        # 挪过去的沙兵还要过 lives()：原来的 10 秒到了，或者这个槽位后来召了新兵，就不再刺、不再盖画面
        own = (lambda e: lives(s, e)) if moved else (lambda e: e)
        poke = lambda: gate(g, own(sw("cmd", sw(f"k{s}", NONE, kept(s, commanded(s, alive(tied(p["s_tie"], flag(f"k{s}", p["cmd_t"] + 1),
                                                                                                 *stab, *told))))))))
        rise_, stand_ = ((native("rise"), native("sold")) if p["native"] else
                         (view(f"sold_{s}_rise"), view(f"sold_{s}")))
        # a new soldier in the slot takes the crumbled one's latch off (only when it does rise: generation g still up);
        # a crumbled one's checkpoints still call the add-on, which no longer draws it
        up_ = combine(*rm(f"x{s}"), rise_) if p["native"] else rise_
        if moved:
            # 落地就摘掉 z<s>：这个槽位现在就是它
            up_ = combine(*rm(f"z{s}"), up_)
        # out of the sand, then standing (one the copy's dash brings arrives standing: q_land's burst is its dust)
        out = ([] if moved and p["native"] else [view("s_spawn"), sfx("s_spawn")]) + [gate(g, up_)]
        out += [delayed(t, gate(g, own(stand_))) for t in range(p["s_step"], p["s_life"], p["s_step"])]
        out += [field(f"s{s}_ch", p["s_r"], p["s_life"], p["s_per"], 1, [poke()], "EnemyChampion"),
                field(f"s{s}_all", p["s_r"], p["s_life"], p["s_per"], 1, [poke()])]
        return out

    def put(s, g, where):
        # 新兵占这个槽位：b<s> 是它的 10 秒，w<s> 是还能被 Q 挪的那段，z<s> 让之前从这个槽位挪走、区域还没散的老兵别再醒
        return combine(refresh(f"b{s}", p["s_life"]), refresh(f"w{s}", movable_t), refresh(f"z{s}", None),
                       where(soldier(s, g)))

    def rise(where, g, i=0):
        """A soldier of generation g in the first free slot (all three up: none)."""
        s = SLOTS[i]
        return sw(f"b{s}", NONE if i == len(SLOTS) - 1 else rise(where, g, i + 1), put(s, g, where))

    def any_up(name):
        """`name` up for a tick when a soldier stands (in the add-on's copy: one that has not crumbled)."""
        return combine(*rm(name), *[sw(f"b{s}", kept(s, refresh(name, 1))) for s in SLOTS])

    def movable_up(name):
        """`name` 挂一 tick：有能被 Q 挪的沙兵（站着、没塌，离 10 秒到头还够冲一次）。"""
        return combine(*rm(name), *[sw(f"b{s}", kept(s, sw(f"w{s}", refresh(name, 1)))) for s in SLOTS])

    on_spot = lambda target: (lambda effects: lob("s_lob", 1, effects, target))

    # ------------------------------------------------------------------ the controller: Q's move, E's soldier
    def move(g):
        """Q at a champion from generation g: every standing soldier moves to its spot as generation NEXT[g] (none
        standing: one rises there), then they stab at once. The add-on's copy: at any enemy Q aimed at; the add-on reads
        the slots moving (`m<s>`, `qn` when none stood) as the hidden lob leaves (league_azir:q_fly) and draws each soldier
        sliding from its spot to the landing, its path dealing Q's damage and slow."""
        h = NEXT[g]
        land = [sw(f"m{s}", combine(*rm(f"m{s}"), *soldier(s, h, moved=True))) for s in SLOTS]
        # Q -> stab (the user's combo, 2026-10-23): they stab on landing. The main pack moves them only onto champions; the
        # copy moves them onto whatever Q aimed at, and stabs on landing only where that was a champion (`qc`, hung by
        # league_azir:q_pick for the landing) - the combo as it was, no free volley into every minion wave (League's
        # soldiers stab only when he attacks)
        volley = delayed(2, refresh("cmd", p["cmd_t"]))
        if p["native"]:
            volley = sw("qc", combine(*rm("qc"), volley))
        land += [view("q_land"), sfx("q_land"), volley]
        # a crumbled soldier (the add-on's copy) is gone: Q moves only the ones standing
        # 2026-11-20：挪的时候不再续 b<s>（挪过去还是原来那条命），快到头的（w<s> 没了）不挪；一个能挪的都没有就在那里召一个新的
        marks = [sw(f"b{s}", kept(s, sw(f"w{s}", refresh(f"m{s}", p["q_travel"] + 4)))) for s in SLOTS]
        none = combine(refresh("ma", p["q_travel"] + 4), refresh("ba", p["s_life"]), refresh("wa", movable_t),
                       *([refresh("qn", 2)] if p["native"] else []))
        fly = [nat("q_fly")] if p["native"] else []
        return combine(movable_up("up"), sw("up", combine(*rm("up"), *marks), none), to_gen(h), *fly,
                       lob("q_move", p["q_travel"], land, "EnemyWithoutTower" if p["native"] else "EnemyChampion"))

    if p["native"]:
        # the add-on's copy (0.3.0, the user's pick 「Q 沙兵真的冲过去」: whatever enemy Q targets): every enemy within
        # reach is offered and league_azir:q_pick flags `qt` on the one Q aimed at (or, gone, the nearest one to where it
        # stood) - the move goes there. The main pack cannot tell Q's target apart here: a random champion in range
        q_move = around(p["q_range"] + Q_REACH, "EnemyWithoutTower",
                        [combine(nat("q_pick"), sw("qt", combine(*rm("qt"), by_gen(move))))])
    else:
        q_move = pick(p["q_range"], "EnemyChampion", by_gen(move))
    e_soldier = pick(p["e_near"], "EnemyChampion", by_gen(lambda g: rise(on_spot("EnemyChampion"), g)))
    ctl = combine(refresh("polling", p["ctl_p"] + 2),
                  sw("q_go", combine(*rm("q_go"), q_move)),
                  sw("e_go", combine(*rm("e_go"), e_soldier)))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", p["ctl_p"] + 2), casted(p["ctl_t"], p["ctl_p"], ctl))))

    # ------------------------------------------------------------------ attack: the sceptre points
    # the soldier rises by the enemy (League's W: at a spot within 500 of him, the enemy in its spear's reach): a hidden
    # bolt from his feet (y_offset 5000) toward the target stops on the first enemy on the way, s_stop from it (so it
    # stands before it, not inside it), else at s_place
    def ahead(effects):
        return {"type": "LinearProjectile", "name": n("s_place"), "speed": p["s_speed"], "range": p["s_place"],
                "y_offset": 5000, "penetrate": False, "shape": circle(p["s_stop"]), "applied_target": "EnemyWithoutTower",
                "applied_effects": [], "end_effects": list(effects)}
    spawn = sw("p_cd", NONE, combine(flag("p_cd", p["p_cd"]), by_gen(lambda g: rise(ahead, g))))
    bolt = homing("a_bolt", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"], p["a_y"])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), hang, alive(spawn),
                              delayed(p["a_rel"] - 1, alive(sfx("a"), refresh("cmd", p["cmd_t"]))),
                              delayed(p["a_rel"] + p["cmd_t"] + 1, alive(sw("stabbed", NONE, bolt)))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Conquering Sands
    wave = line("q_wave", p["q_speed"], p["q_range"], p["q_w"], "EnemyWithoutTower",
                [ap(qd, qa), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                 view("q_hit"), tsfx("q_hit")])
    champ = combine(*rm("q_ch"), pick(p["q_range"], "EnemyChampion", flag("q_ch", 1)),
                    sw("q_ch", combine(*rm("q_ch"), sw("polling", refresh("q_go", 4)))))
    go = [wave, champ]
    if p["native"]:
        # the add-on's copy: Q aims the move at its own target whatever it is (league_azir:q_go records it, q_pick finds
        # it for the controller). With soldiers up and a controller to move them, their paths deal Q's damage and slow
        # (league_azir:q_fly / dash_<s>, each enemy once a cast; League: the soldiers' paths): no wave. With none (or no
        # controller yet in this life) the wave as in the main pack (league_azir:q_wave)
        go = [movable_up("q_up"), sw("polling", NONE, combine(*rm("q_up"))),
              sw("q_up", combine(*rm("q_up"), nat("q_go")), combine(wave, nat("q_wave"))),
              sw("polling", refresh("q_go", 4))]
    # the slot's own cooltime is Q's cooldown: R's refund (skill_cooldown_mult) shortens it
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(qd, qa, ap), voice("vo_q", p), sfx("q"),
                           delayed(p["q_rel"] - 1, alive(*go))))

    # ------------------------------------------------------------------ skill2: E Shifting Sands
    guard_ = combine(on_me(shield(p["e_sh"], p["e_ap"], p["e_t"])), cview("e_shield"))
    hop = combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), guard_,
                  {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_back_t"]})
    arrive = [cview("e_land"), sfx("e_land"),
              around(p["e_r"], "EnemyWithoutTower", [ap(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]),
              refresh("r_win", p["win_r"]), sw("polling", refresh("e_go", 4))]
    dash = combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p), guard_,
                   delayed(p["e_go_at"] - 1, alive({"type": "MoveToTarget", "speed": p["e_speed"],
                                                    "range": p["e_range"], "end_effects": arrive})))
    near = combine(*rm("e_me"), pick(p["e_self"], "EnemyChampion", flag("e_me", 1)))
    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap),
                            sw("e_cd", NONE, combine(any_up("e_up"), sw("e_up", combine(
                                *rm("e_up"), near,
                                sw("e_me", combine(*rm("e_me"), hop), sw("r_cd", NONE, dash))))))),
                    key="skill2")

    # ------------------------------------------------------------------ ult: R Emperor's Divide
    k = p["r_stamps"]
    # the guards: a hop's picture stamped where each hidden bolt stops (the wall's flight in k hops, two steps in turn);
    # the main pack's data cannot see the wall's direction, so they face right - the add-on's copy stamps them itself,
    # facing the way the wall goes (league_azir:r_wall gets the ult's target)
    stamps = [place(f"r_st{i}", p["r_speed"], p["r_len"] * i // k, [view("r_guards_" + "ab"[i % 2]), view("r_dust")])
              for i in range(1, k + 1)]
    if p["native"]:
        stamps = [{"type": "Native", "effect_ref": f"{ID}:r_wall"}]
    # the push: the main pack's Knockback goes r_kb_speed x r_kb from where it hits (half the champions it hits end short
    # of where the wall stops); the add-on's copy carries every enemy it hits past where its wall stops and stands: its
    # passive sweeps the wall's path itself every tick (league_azir:r_wall records it), and league_azir:r_carry on the
    # wall's hit is the second way in. The wall's native goes last, as before 0.1.5 (0.1.5 put it first: no carry at all
    # in the user's games of 2026-10-29)
    push = {"type": "Native", "effect_ref": f"{ID}:r_carry"} if p["native"] else \
        {"type": "Knockback", "speed": p["r_kb_speed"], "tick": p["r_kb"]}
    wall = combine(sfx("r_wall"), cview("r_rise"),
                   line("r_wall", p["r_speed"], p["r_len"], p["r_w"], "EnemyWithoutTower",
                        [ap(p["r_dmg"], p["r_ratio"]), push, view("r_hit"), tsfx("r_hit")]),
                   line("r_wall_ch", p["r_speed"], p["r_len"], p["r_w"], "EnemyChampion",
                        [refresh("q_ref", 2, skill_cooldown_mult=p["q_refund"], ult_cooldown_mult=-p["q_refund"])]),
                   *stamps)
    # the add-on's copy rushes round the target to the side away from his team (league_azir:r_behind); RushMoveToBack goes
    # to the side away from where he came from, which kicks them sideways or away when E overshot or came from the side
    rush = {"type": "Native", "effect_ref": f"{ID}:r_behind"} if p["native"] else \
        {"type": "RushMoveToBack", "speed": p["r_rush"], "applied_effects": []}
    behind = delayed(p["r_rush_at"] - 1, alive(rush))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), refresh("r_cd", p["r_cd"]), sfx("r"), voice("vo_r", p),
                         sw("r_win", combine(*rm("r_win"), behind)),
                         delayed(p["r_at"] - 1, alive(wall))))

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                            "tag": tag or name, "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("a_bolt"), Pj("q_wave")]
    # the sand wall he raises goes under the units: over them (z 1) it hid his ult poses; the geyser (a short burst)
    # stays over them - under them his body, Darius and the soldier rising there hid all of it
    views_e = [E("a_hit"), E("s_stab", FX, 3), E("s_spawn", FX, 1, False), E("q_land", FX, 1, False), E("q_hit"),
               E("e_shield", FX, 3), E("e_land", FX, 1, False), E("e_hit"), E("r_rise", BIG, -1, False),
               E("r_hit")]
    views_e += [E(f"sold_{s}", SOLDIER, 1, False, f"soldier_{s}") for s in SLOTS]
    views_e += [E(f"sold_{s}_rise", SOLDIER, 1, False, f"soldier_{s}_rise") for s in SLOTS]
    views_e += [E(f"r_guards_{side}{k_}", GUARD, 2, False, f"charge_{d_}_{k_}") for side, d_ in (("", "r"), ("l", "l"))
                for k_ in "ab"]
    if p["native"]:
        # one guard alone (league_azir 0.2.4): the add-on stands them in one line across the charge, whatever its
        # direction - its three stamps of three guards overlapped into three ranks (the user, 2026-11-11: 「沙皇R的大招推起来
        # 像是有三排士兵」); the main pack's own hops keep the three-guard stamps
        views_e += [E(f"r_one_{side}{k_}", GUARD, 2, False, f"one_{d_}_{k_}") for side, d_ in (("", "r"), ("l", "l"))
                    for k_ in "ab"]
    views_e += [E("r_dust", FX, 1, False)]
    # the Sun Disc's (the add-on plays them: the disc's rise and stamps, its ring, its solar ray)
    views_e += [E("disc_rise", DISC, 1, False, "disc_rise"), E("disc", DISC, 1, False, "disc"), E("d_rise", BIG, 1, False),
                E("d_glow", FX, -1, False), E("d_beam", BIG, 3)]
    # the add-on's soldier from the side (it stamps them: standing, rising, stabbing, facing right or left; 0.3.0 dashing
    # with Conquering Sands, a stamp every dash's ticks along its path)
    views_e += [E(f"ss_{t}_{d_}", SIDE, 1, False, f"{t}_{d_}") for t in ("stand", "rise", "stab", "dash") for d_ in "rl"]
    views_b = [B_("q_slow", FX, -1, "slow")]
    extra = {}
    if p["native"]:
        params = {k_: int(p[k_]) for k_ in NATIVE_KEYS}
        params.update(s_dmg=int(sd), s_ap=int(sa), q_dmg=int(qd), q_ap=int(qa))    # the copy's own (n_*)
        extra["passive"] = {"passive_ref": f"{ID}:disc", "params": params}
    return {
        "id": ID, "category": "Magician", **extra, "tags": ["AP", "Magic", "Range", "CC", "Shield"],
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (native=1)")
    a = ap_.parse_args()
    p = dict(P)
    if a.native:
        p["native"] = 1
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
