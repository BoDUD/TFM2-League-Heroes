"""Build league_zac.data_champion (jungle, Melee tank, AP: Zac, the Secret Weapon) from the parameters P.

    python tools/kit/build_zac.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-23: JUNGLE, layout A - Q / E / R, W folded into the passive, the revive in the add-on;
combos E's landing -> W, E's knock-up -> Q, Q's fling -> R, R's end -> W). TFM2 has three active slots for League's
four buttons: Stretching Strikes (Q) is `skill`, Elastic Slingshot (E) `skill2`, Let's Bounce! (R) the `ult`; Unstable
Matter (W) rides on his attack and the combos. Damaging skills go on `EnemyWithoutTower`, so he clears camps with them.
Q and R keep their cooldowns in flags (`q_cd`, `r_cd`; league_nunu's E) so the combos can cast them; a slot cast while
its flag is up does nothing (a 3-tick idle). Flags die with him: a respawned Zac has Q and R ready. The combos cast R
only after the ult slot (open from level 5) has fired once this life (the flag `r_open` it lays; it dies with him too,
and the slot lays it again its first try): without it Q -> R bounced him from level 1 (the user, 2026-10-24).
  passive Cell Division (细胞分裂): every skill hit on an enemy champion sheds a blob (at most one every b_gap ticks): a
          hidden line from him toward that champion, b_far long, lands b_fly ticks later where the blob lies for b_lie
          ticks (a picture stamped every 15 ticks, league_poppy's buckler); walking within b_catch of it absorbs it -
          b_heal + b_heal_ap% AP health (a zone on himself, once per blob). Three blob slots (`bs1`..`bs3`): a blob
          takes the first free one. The revive is the add-on's (league_anivia's egg way; the main pack's tooltip says
          so): with the add-on the lethal hit leaves him at 1 health, he splits into a puddle for split_t ticks holding
          split_hp% of his maximum health, armour and magic resistance -split_def, rooted, no attacks or skills; the
          puddle destroyed is his death (the killer's), whole he reforms with what it kept. Once every split_cd ticks,
          kept across deaths.
  W       Unstable Matter (不稳定物质): with `w_cd` off his attack bursts round him (w_r): w_dmg + w_ap% AP to every enemy
          and w_pct% of each enemy champion's maximum health more (true damage: `ApAttack` has no target_hp_ratio,
          league_amumu); w_cd ticks of cooldown.
  attack  A slam of the goo fist (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit.
  skill   Q Stretching Strikes (延伸打击), `Targeting` on `EnemyWithoutTower` (q_range, `q_cd`): the arm stretches at
          the target (a homing fist, q_dmg + q_ap% AP + q_hp% of his maximum health, q_slow% for q_slow_t). A champion
          caught (a champion-only twin) is held q_hold ticks (League: the hand sticks), then flung to him (`Grab`) and
          slammed into whoever stands round him: q_dmg + q_ap% AP + q_hp% again and a q_up-tick knock-up within q_sr
          (League throws the two caught enemies into each other).
  skill2  E Elastic Slingshot (橡筋弹弓), `Targeting` on `EnemyWithoutTower` (e_range): he plants his arms and stretches
          back for e_wind ticks, then flings himself onto the target (`MoveToTarget` e_speed, league_malphite R): on
          landing e_dmg + e_ap% AP + e_hp% of his maximum health and an e_up-tick knock-up within e_r.
  ult     R Let's Bounce! (动感弹球), `Targeting` on `EnemyChampion` (r_range, `r_cd`): r_n bounces r_gap ticks apart,
          unstoppable (`cc_immune`); each lands r_air ticks after it starts for r_dmg + r_ap% AP (later bounces x r_k%)
          and r_slow% for r_slow_t within r_r. The first dashes through an enemy champion within r_range + 25000 (the
          AI casts from its range plus both bodies) to 15000 beyond it (`RushMoveToBack` r_rush from r_rush_at,
          league_leesin's insec) and its landing kicks them back away from him (`Knockback` r_kb x r_kb_t), toward
          where he came from - League's first bounce, the carry back to his team (the user, 2026-10-24: 「大招应该也能
          抱一个人回来」); the others hop onto an enemy champion within r_hop (or in place) for an r_up-tick knock-up, so
          he follows the one he kicked.
  combos  E -> W: the landing bursts Unstable Matter at once (its cooldown starting over). E -> Q: a champion knocked up by
          the landing is caught by Q at once when `q_cd` is off. Q -> R: the slam of a flung champion starts R on it
          when `r_cd` and `r_open` allow. R -> W: the last bounce bursts Unstable Matter and leaves W ready again.
The add-on copy (--native, addons/league_zac): the passive league_zac:split decides the split (the copy shows it:
`split_go` / `split_end` flags, a 2-tick watch hung once a life by his attack: the melt, the puddle held every 30 ticks,
the reform).
Timings: tools/art/rig_zac.py's frames (a frame's start in ticks = ms x 0.06): the attack's punch at a_hit 11 of
atk_dur 28; Q's grab leaves at q_rel 8 of q_dur 24, the slam lands q_slam_at 8 into skill_slam's 18; E's wind-up is
e_wind 36 (the arms planted, the pull), skill2_fly held while he flies, skill2_land e_land 16; R's hop r_air 25 (the
crouch, up, balled, down: the move from r_move_at 5), ult_land r_land 12, a bounce every r_gap 37.
Numbers: League 16.20 (CommunityDragon zac.bin) read into the jungle tank range (league_nunu, league_rammus), balanced
on the classic-SDK simulations (kd.py --lane 1 against ninja, demon, hunter, werewolf and vampire, C:/t/za_sim,
2026-10-23; league_nunu +2.00 on the same seeds 1-8): the draft +1.51; retimed to the frames (every bounce lands) +3.65;
the knock-ups shorter (R 20, E 30 ticks) +1.98; R 90 and E 60 damage = P +1.73 (seeds 9-16: +1.03, league_nunu
+2.42 on them - the jungle's range, kept); with 1080 health and 36 armour +0.44. The blobs first lay 12 game px off
him, under his own 58-px-wide body (unseen: 「这个也要改」): b_far 32000 (past his body) with b_catch 16000 +0.92 / +1.23
(fewer absorbed), b_catch 20000 +1.21 / +1.17, and b_heal 55 = P +1.58 / +1.30 (heal 1803 / 1612, as before).
The combos in a traced game (seed 3): every E landing bursts W, R's last landing bursts W, Q after an E knock-up and R
after a Q slam whenever their cooldowns allow.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_zac.data_champion")
ID = "league_zac"
FX = "asset/league/effects/league_zac_fx"
BIG = "asset/league/effects/league_zac_big"

# League's Zac (16.20): 685 +109 hp, 60 AD, 33 armour, 32 mr, 340 move, 175 range. Passive: blobs heal 4-7.5% max health;
# the revive splits him into four bloblets, 5 min. Q 800 range: 40-100 + 30% AP + 4% max health, 40% slow; attacking
# a second enemy throws both into each other (the same damage again), 0.5 s knock-up. W: 35-115 + (4% + 4% per 100 AP)
# of the targets' maximum health round him, cd 5. E: a 0.9-1.3 s charge, 1200-1800 range, 60-200 + 80% AP, knock-up
# 0.5-1 s, cd 22-10. R: four bounces, 140-280 + 40% AP (later hits 50%), knock-up 1 s, 20-30% slow, cd 120-90.
P = {
    # stats (base tanks: attack 80 +6, hp 1100 +120, defence 40 +10, mr 30 +5; league_nunu 1150 / 72)
    # hp 1150 -> 1250, q_dmg 40 -> 55, e_dmg 60 -> 85 (2026-10-24): R gated to level 5 cost his early game - kd.py
    # --lane 1 seeds 1-8 +1.58 -> -0.22 (the gate alone; the first bounce's kick -0.21, no change); with these +1.66 / +1.48
    # on seeds 1-8 / 9-16 (before: +1.58 / +1.30)
    "hp": 1250, "hp_g": 120, "atk": 72, "atk_g": 6, "apw": 30, "apw_g": 15, "def": 40, "def_g": 10, "mr": 30, "mr_g": 5,
    "ms": 1000, "ms_g": 11,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 70, "a_hit": 11,
    # passive: Cell Division's blobs
    "b_gap": 40, "b_find": 30000, "b_far": 32000, "b_fly": 10, "b_lie": 300, "b_catch": 20000, "b_heal": 55, "b_heal_ap": 15,
    # the controller
    "ctl_t": 3600, "ctl_p": 3,
    # W Unstable Matter (in the attack)
    "w_cd": 300, "w_r": 24000, "w_dmg": 25, "w_ap": 30, "w_pct": 4,
    # skill: Q Stretching Strikes
    "q_cd": 600, "q_range": 50000, "q_dur": 24, "q_rel": 8, "q_speed": 8000, "q_y": -6000, "q_dmg": 55, "q_ap": 30,
    "q_hp": 2, "q_slow": 40, "q_slow_t": 60, "q_hold": 24, "q_grab": 2500, "q_drag": 10, "q_sr": 22000, "q_up": 30,
    "q_slam": 18, "q_slam_at": 8,
    # skill2: E Elastic Slingshot
    "e_cd": 900, "e_range": 75000, "e_wind": 36, "e_speed": 4000, "e_r": 26000, "e_dmg": 85, "e_ap": 60, "e_hp": 3,
    "e_up": 30, "e_land": 16, "e_w_at": 2, "e_q_at": 8,
    # ult: R Let's Bounce!
    "r_cd": 3600, "r_range": 40000, "r_n": 4, "r_gap": 37, "r_hop": 30000, "r_speed": 3000, "r_r": 26000,
    "r_dmg": 90, "r_ap": 50, "r_k": 50, "r_up": 20, "r_slow": 25, "r_slow_t": 60, "r_land": 12, "r_air": 25,
    "r_move_at": 5, "r_rush": 7000, "r_rush_at": 12, "r_kb": 2000, "r_kb_t": 12,
    # Cell Division's revive, the add-on's (League: 4 bloblets, revive with 10-50% health, cd 300 s)
    "split_t": 360, "split_cd": 18000, "split_hp": 40, "split_def": 20, "split_in": 18, "split_out": 18,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
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


def ap(dmg, ratio, hp=0):
    """Magic damage: dmg + ratio% AP + hp% of HIS maximum health."""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False}


def pct(ratio):
    """True damage of ratio% of the target's maximum health."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": ratio,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Caster"}


def around(radius, target, *effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", *effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=ap):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed=40000, y=0):
    """speed 40000 reaches a melee target on the next tick (a hidden blow)."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=(), y=5000):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


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
    # ------------------------------------------------------------------ passive: Cell Division's blobs
    def blob_in(s):
        """A blob into slot s: thrown toward the champion the effect is on, absorbed once when he walks over it."""
        got = f"g{s}"
        absorb = sw(got, NONE, combine(flag(got, p["b_lie"]), heal(p["b_heal"], p["b_heal_ap"]), cview("b_pick"),
                                       sfx("b_pick")))
        lying = [delayed(k, sw(got, NONE, view("b_lie"))) for k in range(0, p["b_lie"], 15)]
        lands = [field("b_ground", p["b_catch"], p["b_lie"], 3, [absorb], target="AllyOnlySelf", first=0), *lying]
        return combine(*rm(got), flag(f"bs{s}", p["b_lie"] + p["b_fly"]),
                       line("b_fly", -(-p["b_far"] // p["b_fly"]), p["b_far"], 1000, "EnemyWithoutTower", True, [],
                            end=lands))

    # a hit on a champion only asks for a blob (`b_due`, one every b_gap ticks); the controller throws it
    shed = sw("b_gap", NONE, combine(flag("b_gap", p["b_gap"]), refresh("b_due", p["ctl_p"] + 2)))
    drop = pick(p["b_find"], "EnemyChampion", sw("bs1", sw("bs2", sw("bs3", NONE, blob_in(3)), blob_in(2)), blob_in(1)))

    # ------------------------------------------------------------------ W Unstable Matter
    burst = combine(*rm("w_cd"), flag("w_cd", p["w_cd"]), sfx("w"), cview("w_burst"),
                    around(p["w_r"], "EnemyWithoutTower", ap(p["w_dmg"], p["w_ap"]), view("w_hit"), tsfx("w_hit")),
                    around(p["w_r"], "EnemyChampion", pct(p["w_pct"]), shed))

    # ------------------------------------------------------------------ R Let's Bounce! (the ult and the controller)
    # A pulse on him every r_gap ticks is one bounce; the ladder h1..h3 counts them, `r_fin` marks the last.
    land = [anim("ult_land", p["r_land"]), sfx("r_land"), cview("r_land"),
            # the first landing kicks them back (away from him: he landed beyond them, so toward where he came from),
            # the others knock them up
            sw("r_first",
               around(p["r_r"], "EnemyWithoutTower", {"type": "Knockback", "speed": p["r_kb"], "tick": p["r_kb_t"]}),
               around(p["r_r"], "EnemyWithoutTower", {"type": "Airborne", "duration": p["r_up"]})),
            sw("r_first", combine(*rm("r_first"), around(p["r_r"], "EnemyWithoutTower", ap(p["r_dmg"], p["r_ap"]))),
               around(p["r_r"], "EnemyWithoutTower", ap(p["r_dmg"] * p["r_k"] // 100, p["r_ap"] * p["r_k"] // 100))),
            around(p["r_r"], "EnemyWithoutTower",
                   buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]), view("r_hit"), tsfx("r_hit")),
            around(p["r_r"], "EnemyChampion", shed),
            # R -> W: the last bounce bursts Unstable Matter and leaves W ready
            sw("r_fin", combine(*rm("r_fin"), burst, *rm("w_cd")))]
    # each bounce: the hop's frames (crouched, up, balled at the top, coming down) for r_air ticks, the move onto an enemy
    # champion within r_hop while he is up (from r_move_at; MoveToTarget alone, so the landing never waits on it), the
    # landing at r_air wherever he is - in reach of nobody, in place
    hop = {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_hop"] + 20000, "end_effects": []}
    # the first bounce (`r_first` lives until its landing) dashes through an enemy champion within r_range to 15000
    # beyond it (league_leesin's insec), so its landing kicks the champion back toward his side - League's carry
    rush = {"type": "RushMoveToBack", "speed": p["r_rush"], "applied_effects": []}
    # (late and fast, r_rush_at at r_rush: a fresh aim the target can't walk out of before the landing; from r_move_at
    # at 3500 the landing came short of a fleeing champion and kicked it on away from him)
    leap = sw("r_first", NONE, pick(p["r_hop"], "EnemyChampion", hop))
    lunge = sw("r_first", pick(p["r_range"] + 25000, "EnemyChampion", rush))
    count = sw("h3", combine(*rm("h3"), flag("r_fin", 60)),
               sw("h2", combine(*rm("h2"), flag("h3", 60)), sw("h1", combine(*rm("h1"), flag("h2", 60)), flag("h1", 60))))
    bounce = combine(anim("ult", p["r_air"]), sfx("r_hop"), count,
                     delayed(p["r_move_at"], alive(leap)), delayed(p["r_rush_at"], alive(lunge)),
                     delayed(p["r_air"], alive(combine(*land))))
    t_r = p["r_n"] * p["r_gap"]
    # the first bounce at once, the others r_gap ticks apart (a pulse on him: AddCasted runs first a period in)
    r_cast = combine(*rm("h1", "h2", "h3", "r_fin"), flag("r_first", t_r + 60), refresh("r_cd", p["r_cd"]),
                     voice("vo_r", p), sfx("r"), bounce,
                     on_me(buff("r_on", t_r + 2, cc_immune=True),
                           casted((p["r_n"] - 1) * p["r_gap"] + 1, p["r_gap"], bounce)))

    # ------------------------------------------------------------------ Q Stretching Strikes (the skill and the controller)
    def q_cast(target):
        hit = [ap(p["q_dmg"], p["q_ap"], p["q_hp"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
               view("q_hit"), tsfx("q_hit")]
        # the slam: the flung champion lands on him, everyone round him goes up; Q -> R (the controller casts it)
        slam = combine(anim("skill_slam", p["q_slam"]), delayed(p["q_slam_at"], alive(
            sfx("q_slam"), cview("q_slam"),
            around(p["q_sr"], "EnemyWithoutTower", ap(p["q_dmg"], p["q_ap"], p["q_hp"]),
                   {"type": "Airborne", "duration": p["q_up"]}, view("q_hit"), tsfx("q_hit")),
            sw("r_open", sw("r_cd", NONE, refresh("r_go", p["ctl_p"] + 2))))))
        caught = [buff("q_held", p["q_hold"] + p["q_drag"]), shed,
                  delayed(p["q_hold"], {"type": "Grab", "speed": p["q_grab"], "tick": p["q_drag"]}),
                  delayed(p["q_hold"] + p["q_drag"], alive(slam))]
        return combine(refresh("q_cd", p["q_cd"]), anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p),
                       delayed(p["q_rel"] - 1, alive(
                           homing("q_fist", target, hit, p["q_speed"], p["q_y"]),
                           homing("q_twin", "EnemyChampion", caught, p["q_speed"], p["q_y"]))))

    # ------------------------------------------------------------------ the controller (a pulse on him)
    # skill and skill2 are cloned every tick (champion-data 8), a periodic AddCasted hung on him is not
    # (league_azir / league_orianna): his attacks and the ult hang one (ctl_t ticks, period ctl_p) unless `polling`
    # says one runs. It throws the blobs, E -> Q (`q_go`) and Q -> R (`r_go`).
    ctl = combine(refresh("polling", p["ctl_p"] + 2),
                  sw("b_due", combine(*rm("b_due"), drop)),
                  sw("q_go", combine(*rm("q_go"), sw("q_cd", NONE, pick(p["e_r"] + 5000, "EnemyChampion",
                                                                        q_cast("EnemyChampion"))))),
                  sw("r_go", combine(*rm("r_go"), sw("r_cd", NONE, pick(p["r_range"], "EnemyChampion", r_cast)))))
    hang = on_me(sw("polling", NONE, combine(refresh("polling", p["ctl_p"] + 2), casted(p["ctl_t"], p["ctl_p"], ctl))))

    # ------------------------------------------------------------------ the split (the add-on copy only)
    # The main pack has no revive (data reads no health and nothing fires on a death). The add-on's passive
    # league_zac:split catches the lethal hit (league_anivia's egg), leaves him split_hp% of his health as the puddle's
    # and raises `split_go`; the puddle destroyed is his death. The data shows it: split_go -> `split_on` (armour and
    # magic resistance -split_def, split_t ticks), the melt (Unstable Matter's splash), the puddle held by its loop every
    # 30 ticks; `split_end` (the add-on, split_t ticks later with him alive) -> the reform. A watch on him every 2 ticks,
    # hung once a life by his attack (`init`, a flag a death clears).
    native = bool(p["native"])
    life = None                     # combine() leaves it out: the main pack's attack as without the add-on
    if native:
        t_ = p["split_t"]
        start = sw("split_go", combine(*rm("split_go"), refresh("split_on", t_, defence=-p["split_def"],
                                                                magic_resistance=-p["split_def"]),
                                       refresh("split_hold", p["split_in"]), anim("split_in", p["split_in"] + 2),
                                       cview("w_burst"), sfx("p_split"), voice("vo_p", p)))
        hold = sw("split_on", sw("split_hold", NONE, combine(flag("split_hold", 30), anim("split", 32))))
        out = sw("split_end", combine(*rm("split_end", "split_on", "split_hold"), anim("reform", p["split_out"]),
                                      cview("b_pick"), sfx("p_reform")))
        life = sw("init", NONE, combine(flag("init", None), on_me(casted(1000000, 2, start, hold, out))))

    # ------------------------------------------------------------------ attack
    blow = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   sw("w_cd", NONE, burst))
    # every hit sits behind the alive guard: a decoy the AI can read (champion-data "alive guard", league_gangplank)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100, attack), hang, life, delayed(p["a_hit"] - 1, alive(blow))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ the slots
    ult = action("idle", 3, 90, 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ap"]), hang, sw("r_open", NONE, flag("r_open", None)),
                         sw("r_cd", NONE, r_cast)), key="ult")
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_dmg"], p["q_ap"]), sw("q_cd", NONE, q_cast("EnemyWithoutTower"))), key="skill")
    landing = [anim("skill2_land", p["e_land"]), sfx("e_land"), cview("e_land"),
               around(p["e_r"], "EnemyWithoutTower", ap(p["e_dmg"], p["e_ap"], p["e_hp"]),
                      {"type": "Airborne", "duration": p["e_up"]}, view("e_hit"), tsfx("e_hit")),
               # E -> Q on a champion it knocked up (the controller casts it), E -> W
               around(p["e_r"], "EnemyChampion", shed, refresh("q_go", p["e_q_at"] + p["ctl_p"] + 2)),
               delayed(p["e_w_at"], alive(burst))]
    fling = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 60000, "end_effects": landing}
    skill2 = action("skill2", p["e_wind"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"], p["e_ap"]), sfx("e"), voice("vo_e", p),
                            delayed(p["e_wind"] - 1, alive(anim("skill2_fly", 60), fling))))

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("q_fist"), Pj("b_fly")]
    views_e = [E("a_hit"), E("q_hit"), E("q_slam", BIG, 2, False), E("w_burst", BIG, 2, False), E("w_hit"),
               E("e_land", BIG, -1, False), E("e_hit"), E("r_land", BIG, -1, False), E("r_hit"),
               E("b_lie", FX, 2, False), E("b_pick")]
    views_b = [B_("q_slow", FX, -1, "slow"), B_("q_held", FX, 3), B_("r_slow", FX, -1, "slow")]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_zac:split", "params": {
            "split_t": p["split_t"], "split_cd": p["split_cd"], "split_hp": p["split_hp"]}}
    return {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Tank", "CC"], **extra,
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
    ap_.add_argument("--set", nargs="*", default=[])
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
