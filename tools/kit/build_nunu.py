"""Build league_nunu.data_champion (jungle, Melee tank, AP: Nunu & Willump) from the parameters P.

    python tools/kit/build_nunu.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-23: JUNGLE, layout A - W / E / R, Q folded into the passive; 「有连招要做连招」). TFM2 has
three active slots for League's four buttons: Biggest Snowball Ever! (W) is `skill`, Snowball Barrage (E) `skill2`,
Absolute Zero (R) the `ult`; Consume (Q) rides on the attack. Damaging skills go on `EnemyWithoutTower`, so he clears
camps with the snowball and the barrage too.
  passive Call of the Freljord + Consume (弗雷尔卓德的召唤 + 吞噬): every third attack is Willump's bite (attack_bite):
          100% AD + q_dmg + q_ap% AP, healing him q_heal + q_heal_ap% AP; minions and monsters take q_mon true damage
          more (League's Consume deals far more to them; a champion-only twin lays a 2-tick `q_ch` flag that skips it,
          league_lucian's Lightslinger way). The bite calls the Freljord: for p_t ticks he and one allied champion
          within p_ally get p_as% attack speed and p_ms% move speed, and his attacks splash p_spl% AD to the enemies
          round him (League: Willump's attacks splash while the passive runs).
  attack  Willump's claw swipe (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit.
  skill   W Biggest Snowball Ever! (史上最大雪球！), `Targeting` on `EnemyWithoutTower` (w_range): Willump packs the snowball
          (skill, w_in ticks), then rolls it at the target (`MoveToTarget` w_speed, skill_roll held) until it hits: the
          longer the roll, the bigger the ball - `w1` after w_g1 ticks and `w2` after w_g2 of rolling - so the impact
          deals w_dmg + w_ap% AP (x w_k1% / w_k2% grown) to every enemy within w_r (w_r2 grown) and knocks them up
          w_up ticks (w_up2 grown). League's ball is steered for up to 10 s; data cannot steer, so it rolls straight at
          the target.
  skill2  E Snowball Barrage (雪球飞射), `Targeting` on `EnemyWithoutTower` (e_range; cooldown flag `e_cd`, so W can cast it;
          the flag goes up the tick E is decided - set with the throw e_rel ticks later, the AI pressed E again in between
          and threw twice, the user 2026-10-25: 「有时候会在一技能释放之后连放两次」):
          Nunu throws e_n snowballs, one every e_per ticks, each at a random enemy within e_range: e_dmg + e_ap% AP and
          an e_slow% slow; a champion hit is marked (`e_mark`, a champion-only twin), and at e_t ticks from the cast
          Willump roots every marked champion for e_root ticks (League: the champions and large monsters hit).
  ult     R Absolute Zero (绝对零度), `Targeting` on `EnemyChampion` (r_range): they channel a blizzard round them
          (`r_ch`, ult held r_t ticks) under a shield of r_sh + r_sh_ap% AP; every r_pp ticks the enemies within r_r
          are slowed (r_slow0% rising to r_slow1%), and at the end the blizzard bursts: r_dmg + r_ap% AP to every enemy
          within r_r. Crowd control breaks the channel at the next pulse (league_karthus R's check); a broken channel
          bursts for its share so far (League: damage grows with the time channelled).
  combos  W -> E (雪球 -> 雪球飞射): the snowball's impact throws the barrage at once if E is ready - from level 3 only,
          when E's slot opens (「1级二技能还没解锁的时候也能在一技能释放之后触发」). A roll whose target dies ends at once
          (`w_tgt`, a flag the target keeps up on him while it lives; he stood out w_max: 「1技能在目标死亡…原地发呆」). E -> R (雪球飞射 ->
          绝对零度): within r_link ticks of a root, R channels faster (r_tf ticks, the full burst; League: the rooted can't
          leave the blizzard). R -> Q (绝对零度 -> 吞噬): the burst is followed by Willump's bite on an enemy champion
          within reach, his attack count starting over.
Timings: drafts until the frames exist (a frame's start in ticks = ms x 0.06).
Numbers: League 16.20 (CommunityDragon nunu.bin) read into the jungle range (league_rammus, league_warwick), balanced on
the classic-SDK simulations (kd.py --lane 1 against demon, circus_blade, hunter, inquisitor and ninja, C:/t/nu_sim,
2026-10-23; league_rammus +1.90 on seeds 1-8 the same day). The draft panicked the AI (every hit behind the alive guard:
the decoys) and stood 10 s in a roll that never met its target (the roll held w_max); then +5.75 (bite heal 50 + 50%,
splash 40%); halved heals and splash, W 50 + 40%, E 10 + 6% x6 and root 40, R 180 + 100% +0.27; P between them:
+2.14 on seeds 1-8, +2.11 on 9-16.
2026-10-25 (the user: 「雪人的二技能释放逻辑有问题而且冷却太短」): W -> E only from level 3, E's flag up the tick it is decided,
a roll whose target dies ends: those early free barrages were part of his strength (+2.00 -> +0.54 with e_cd 900);
e_cd 660 -> 780 (13 s, League's 14-10): +1.86 (seeds 1-8; 780 with E 14 + 9% +1.56, 900 with E 16 + 10% +1.48).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_nunu.data_champion")
ID = "league_nunu"
FX = "asset/league/effects/league_nunu_fx"
BIG = "asset/league/effects/league_nunu_big"

# League's Nunu & Willump (16.20): 610 +90 hp, 61 AD, 29 armour, 32 mr, 345 move, 125 range. Q Consume: 340-1500 true to
# minions and monsters, 60-220 + 65% AP to champions, heals 75-195 + 60% AP (x1.5 below half health), cd 12-8. W: the
# ball grows for up to 10 s, 36-180 + 30% AP up to 180-900 + 150% AP, knock-up 0.5-1.5 s, cd 14. E: three volleys of
# snowballs over 3 s, 16-48 + 6% AP each, 30% slow; after them the champions hit are rooted 0.5-1.5 s and take
# 16-80 + 80% AP, cd 14-10. R: a 3 s channel, slows 50% -> 95%, shield 65-175 + 150% AP, bursts for up to
# 625-1875 + 300% AP over 650 units, cd 110-90.
P = {
    # stats (base tanks: attack 80 +6, hp 1100 +120, defence 40 +10, mr 30 +5; league_rammus 1250 / 84)
    "hp": 1150, "hp_g": 120, "atk": 72, "atk_g": 6, "apw": 30, "apw_g": 15, "def": 40, "def_g": 10, "mr": 30, "mr_g": 5,
    "ms": 1000, "ms_g": 11,
    "atk_range": 25000, "atk_dur": 28, "atk_cd": 70, "a_hit": 11, "b_dur": 30, "b_hit": 14,
    # passive: Call of the Freljord + Consume
    "q_dmg": 50, "q_ap": 50, "q_mon": 120, "q_heal": 25, "q_heal_ap": 25,
    "p_t": 240, "p_ally": 60000, "p_as": 30, "p_ms": 15, "p_spl": 20, "p_r": 30000,
    # skill: W Biggest Snowball Ever!
    "w_cd": 720, "w_range": 70000, "w_in": 18, "w_speed": 3000, "w_end": 14, "w_g1": 20, "w_g2": 40, "w_max": 90,
    "w_dmg": 55, "w_ap": 42, "w_k1": 140, "w_k2": 170, "w_r": 18000, "w_r2": 26000, "w_up": 30, "w_up2": 60,
    # skill2: E Snowball Barrage
    "e_cd": 780, "e_range": 60000, "e_dur": 40, "e_rel": 6, "e_n": 6, "e_per": 6, "e_speed": 5000, "e_y": -30000,
    "e_dmg": 11, "e_ap": 7, "e_slow": 30, "e_slow_t": 60, "e_t": 66, "e_root": 45, "e_rdmg": 25, "e_rap": 30,
    # ult: R Absolute Zero
    "r_cd": 3600, "r_range": 60000, "r_r": 55000, "r_t": 150, "r_tf": 100, "r_pp": 15, "r_link": 120,
    "r_sh": 120, "r_sh_ap": 80, "r_slow0": 40, "r_slow1": 80, "r_dmg": 190, "r_ap": 105, "r_end": 18,
    # his spoken lines, at most one every vo_gap ticks
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


def unanim(name):
    return {"type": "RemoveCasterAnimation", "name": name}


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


def fixed(dmg):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Caster"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


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


def casted(kind, tick, period, *effects):
    return {"type": "AddCasted", "casted_type": kind, "duration": tick, "period": period,
            "effects": [e for e in effects if e is not None]}


def voice(name, p):
    """Their spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Consume's bite + the Freljord's call
    def call():
        """The bite calls the Freljord: haste for him and one allied champion near, his attacks splash."""
        return combine(refresh("p_on", p["p_t"], attack_speed_mult=p["p_as"], move_speed_mult=p["p_ms"]),
                       pick(p["p_ally"], "AllyNotSelf", buff("p_buff", p["p_t"], attack_speed_mult=p["p_as"],
                                                             move_speed_mult=p["p_ms"])))

    def bite(target):
        """Willump's bite on the unit `target` names (a hidden blow): damage, heal, more to minions and monsters."""
        return combine(sfx("q"), voice("vo_q", p), call(),
                       homing("q_bite", target, [attack(0, 100), ap(p["q_dmg"], p["q_ap"]), heal(p["q_heal"], p["q_heal_ap"]),
                                                 view("q_hit"), tsfx("q_hit")]),
                       homing("q_twin", "EnemyChampion", [flag("q_ch", 2)]),
                       homing("q_mon", "EnemyWithoutTower", [delayed(1, sw("q_ch", NONE, fixed(p["q_mon"])))]))

    splash = sw("p_on", around(p["p_r"], "EnemyWithoutTower", attack(0, p["p_spl"]), view("p_hit")))
    swipe = combine(sfx("a"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]), splash)
    # the count of his attacks lives on him (c1, c2): swipe, swipe, bite
    # every hit sits behind the alive guard: a decoy the AI can read (champion-data "alive guard", league_gangplank)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy", combine(
                      decoy(0, 100, attack), sw("c2", combine(*rm("c1", "c2"), anim("attack_bite", p["b_dur"]),
                                       delayed(p["b_hit"] - 1, alive(bite("Enemy"), splash))),
                         combine(sw("c1", combine(*rm("c1"), flag("c2", None)), flag("c1", None)),
                                 delayed(p["a_hit"] - 1, alive(swipe))))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill2: E Snowball Barrage (before W: W casts it)
    def e_cast():
        balls = []
        for k in range(p["e_n"]):
            rest = p["e_t"] - (p["e_rel"] + k * p["e_per"])       # ticks from this ball's throw to the root
            hit = [ap(p["e_dmg"], p["e_ap"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"),
                   tsfx("e_hit")]
            mark = [buff("e_mark", rest), flag("e_any", rest + 2),
                    casted("Fire", rest + 1, rest, {"type": "Bind", "duration": p["e_root"]}, buff("e_root", p["e_root"]),
                           ap(p["e_rdmg"], p["e_rap"]), view("e_root_hit"))]
            balls.append(delayed(k * p["e_per"], alive(pick(p["e_range"], "EnemyWithoutTower", sfx("e_throw"), homing(
                "e_ball", "EnemyWithoutTower", hit, p["e_speed"], p["e_y"])))))
            # the champion-only twin flies beside each ball at a champion within reach (its mark and root)
            balls.append(delayed(k * p["e_per"], alive(pick(p["e_range"], "EnemyChampion", homing(
                "e_twin", "EnemyChampion", mark, p["e_speed"], p["e_y"])))))
        # E -> R: a root opens R's quick channel
        win = delayed(p["e_t"] - p["e_rel"] + 1, alive(sw("e_any", combine(*rm("e_any"), refresh("e_win", p["r_link"])))))
        return combine(refresh("e_cd", p["e_cd"]), sfx("e"), *rm("e_any"), *balls, win)

    skill2 = action("idle", 3, 60, 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(decoy(p["e_dmg"] * p["e_n"], p["e_ap"] * p["e_n"]),
                            sw("e_cd", NONE, combine(refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]),
                                                     voice("vo_e", p), delayed(p["e_rel"] - 1, alive(e_cast()))))),
                    key="skill2")

    # ------------------------------------------------------------------ skill: W Biggest Snowball Ever!
    def impact(k, r, up):
        return around(r, "EnemyWithoutTower", ap(p["w_dmg"] * k // 100, p["w_ap"] * k // 100),
                      {"type": "Airborne", "duration": up}, view("w_hit"), tsfx("w_hit"))
    hit = [anim("skill_hit", p["w_end"]), *rm("w_roll"), sfx("w_hit"),
           sw("w2", combine(impact(p["w_k2"], p["w_r2"], p["w_up2"]), cview("w_big")),
              sw("w1", combine(impact(p["w_k1"], p["w_r2"], p["w_up"]), cview("w_big")),
                 combine(impact(100, p["w_r"], p["w_up"]), cview("w_burst")))),
           *rm("w1", "w2"),
           {"type": "SwitchByLevel3", "effect_start": NONE, "effect_level3": sw("e_cd", NONE, combine(   # W -> E
               refresh("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), delayed(p["e_rel"] - 1, alive(e_cast()))))}]
    stop = combine(*rm("w_roll", "w1", "w2", "w_tgt"), unanim("skill_roll"))
    watch = on_me(delayed(3, casted("Heal", p["w_max"], 1, sw("w_roll", sw("w_tgt", NONE, stop)))))
    roll = [refresh("w_roll", p["w_max"]), anim("skill_roll", p["w_max"]), cview("w_dust"),
            casted("Heal", p["w_max"], 1, refresh("w_tgt", 3)), watch,
            delayed(p["w_g1"], sw("w_roll", refresh("w1", 600))), delayed(p["w_g2"], sw("w_roll", refresh("w2", 600))),
            {"type": "MoveToTarget", "speed": p["w_speed"], "range": p["w_range"] + 60000, "end_effects": hit}]
    skill = action("skill", p["w_in"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["w_dmg"], p["w_ap"]), *rm("w1", "w2", "w_roll"), sfx("w"), voice("vo_w", p), delayed(p["w_in"] - 1, alive(*roll))))

    # ------------------------------------------------------------------ ult: R Absolute Zero
    def channel(t):
        pulses = list(range(p["r_pp"], t, p["r_pp"]))
        slow = lambda k: around(p["r_r"], "EnemyWithoutTower", buff(
            "r_slow", p["r_pp"] + 2, move_speed_mult=-(p["r_slow0"] + (p["r_slow1"] - p["r_slow0"]) * k // len(pulses))))
        burst = lambda share: combine(*rm("r_ch"), unanim("ult"), anim("ult_end", p["r_end"]), sfx("r_boom"),
                                      cview("r_burst"),
                                      around(p["r_r"], "EnemyWithoutTower", ap(p["r_dmg"] * share // 100,
                                                                               p["r_ap"] * share // 100),
                                             view("r_hit"), tsfx("r_hit")))
        # crowd control breaks it at the next pulse: the burst for the share channelled so far
        steps = [delayed(at, alive(sw("r_ch", combine(
            pick(1, "AllyChampionInCC", burst(100 * at // t)), sw("r_ch", slow(k)))))) for k, at in enumerate(pulses)]
        # R -> Q: Willump's bite after the full burst
        end = delayed(t, alive(sw("r_ch", combine(burst(100), *rm("c1", "c2"),
                                                 pick(p["atk_range"] + 5000, "EnemyChampion", flag("r_q", 2)),
                                                 sw("r_q", delayed(p["r_end"] - 4, alive(anim("attack_bite", p["b_dur"]),
                                                                                         delayed(p["b_hit"] - 1, alive(
                                                                                             bite("EnemyChampion"))))))))))
        return combine(refresh("r_ch", t + 2), anim("ult", t), cview("r_storm"),
                       on_me(shield(p["r_sh"], p["r_sh_ap"], t), buff("r_shield", t)), *steps, end)

    ult = action("ult", p["r_t"] + 4, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ap"]), sfx("r"), voice("vo_r", p),
                         sw("e_win", combine(*rm("e_win"), channel(p["r_tf"])), channel(p["r_t"]))))

    # ------------------------------------------------------------------ views (the step-3 effects pack; drafts)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=3, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [Pj("e_ball")]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("e_hit"), E("e_root_hit"), E("w_hit"),
               E("w_dust", FX, -1, False), E("w_burst", BIG, 2, False), E("w_big", BIG, 2, False),
               E("r_storm", BIG, -1), E("r_burst", BIG, 2, False), E("r_hit")]
    views_b = [B_("p_on", FX, -1), B_("p_buff", FX, -1), B_("e_slow", FX, 3), B_("e_mark", FX, 3),
               B_("e_root", FX, 3), B_("r_slow", FX, 3), B_("r_shield", FX, 3)]
    return {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Tank", "CC"],
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
