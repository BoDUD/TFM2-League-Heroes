"""Build league_syndra.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_syndra.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-10: Q alone / W -> E combo with the pros' QE / spheres as ground zones + a count on her /
Transcendent by level / R armed until she has spheres):
  spheres Dark Spheres stay where they land for orb_t ticks: a `ViewEffect` picture on the point (never turned, it
          floats over its shadow) and a hidden zone of the same life (e_stun_r round the sphere, every 2 ticks) that
          waits for her E. Their count is on her: Q and W fill the first free slot o1..o4 (orb_t-tick caster flags;
          League's R throws at most 3 + 4). Nothing removes a picture or a zone early, so no spell consumes a sphere:
          W throws a sphere it made in her hand, E pushes the ones it reaches, R fires copies.
  passive Transcendent (卓尔不凡): League upgrades a spell at 40 / 60 / 80 / 100 Splinters of Wrath; death clears a mod's
          caster buffs, so the upgrades come by level, re-read every life (league_viktor's probe): her attacks probe
          her attack against the level table (mages buy only ability power, so her attack is atk + atk_g a level).
          lv_q: Q deals q_champ% more to champions (s1); lv_w: W adds w_true% of its damage as true damage (s2);
          lv_e: E's cone widens (e_cos_evo) and the spheres' stun circle grows (e_stun_evo) (s3); lv_r: R's spheres
          ignore magic resistance (s4; League's execute below 15% health reads a share of health no effect has).
  attack  A homing dark bolt from her hand (physical 100% AD).
  skill   Q Dark Sphere (暗黑法球): a `Targeting` cast on `EnemyWithoutTower` (q_range). A hidden lob lands q_fall ticks
          later where the target stood (dodgeable; the landing point shows q_form meanwhile): q_dmg + q_ratio% AP magic
          damage round it (q_r), and a sphere stays there. The pros' QE: with E ready (the caster flag e_cd off) and an
          enemy champion within q_range, Q goes at that champion and, a tick after the sphere lands, E goes at him: the
          new sphere is pushed into him (League's long-range stun).
  skill2  W Force of Will (驱使念力) -> E Scatter the Weak (弱者退散): a `Targeting` cast on `EnemyWithoutTower` (action
          range e_range, cooldown = W's). With an enemy champion within w_range (RandomTarget, league_viktor's aim) she
          lifts a sphere and throws it at him (a lob of w_fly ticks): w_dmg + w_ratio% AP magic damage and a w_slow%
          slow for w_slow_t ticks round the landing (w_r), where the sphere stays; e_gap ticks after the cast, with E
          ready, E goes at the same champion and pushes it into him. With no champion in reach: E alone at the target
          (it clears waves), or W at the target while E is on cooldown.
          E: a cone from her toward the target (`RangeEffect` Forward + DirDot, e_len, acos(e_cos / 1000) each side):
          e_dmg + e_ratio% AP magic damage and a knock-back; e_fly ticks later the caster flag e_go stands for 2 ticks,
          and every sphere within e_reach of her (the zone asks whether she is near: RandomTarget from_projectile on
          AllyOnlySelf) stuns every enemy within e_stun_r of it for e_stun ticks and deals e_orb + e_orb_ratio% AP.
  ult     R Unleashed Power (能量倾泻): a 3-tick `Targeting` cast on `EnemyChampion` (r_slot). Armed like league_viktor R:
          with r_min spheres counted (3 + r_min shots) or a crowd-controlled champion in reach (E's stun: the pros'
          QE -> R) it fires, else it arms r_armed for r_arm ticks - a poll on her every r_poll ticks looks again; after
          r_hold ticks it fires with what she has - and refunds the cooldown when it lapses unused. The volley: 3 + one
          per counted sphere homing spheres at the champion, r_gap ticks apart, each r_dmg + r_ratio% AP magic.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_syndra.data_champion")
ID = "league_syndra"
FX = "asset/league/effects/league_syndra_fx"
BIG = "asset/league/effects/league_syndra_big"

# Numbers: draft d0 (simulations pending).
P = {
    # stats (Magician base: attack 80 +6, magic power 40 +20, hp 900 +100, defence 20, mr 20, move 900, range 60000,
    # attack cooldown 90); League's Syndra: 550 range, 54 AD, 563 + 98 hp, 25 armour, 330 move speed.
    # atk_g is also the level gauge of the upgrades (7 a level: probe steps of 700)
    "hp": 860, "hp_g": 92, "atk": 76, "atk_g": 7, "mp": 40, "mp_g": 20, "def": 18, "def_g": 7, "mr": 20, "mr_g": 4,
    "ms": 910, "ms_g": 9,
    # attack (League 550 range); the bolt leaves her hand 8 px over the pivot
    "atk_range": 55000, "atk_dur": 28, "atk_cd": 90, "a_st": 10, "bolt_speed": 4500, "bolt_y": -3000,
    # passive: the upgrades' levels and the probe
    "lv_q": 3, "lv_w": 5, "lv_e": 7, "lv_r": 9, "pr_gap": 120, "pr_fast": 40, "pr_quiet": 900, "pr_twice": 30,
    "soak": 1000000,
    # spheres (League: 6 s; R throws 3 + at most 4)
    "orb_t": 360,
    # skill: Q Dark Sphere (League: 800 range, radius 180, 0.6 s, 55-265 + 65% AP, cd 7 s; upgraded +25% to champions)
    "q_cd": 420, "q_range": 80000, "q_anim": 24, "q_rel": 8, "q_fall": 30, "q_r": 20000, "q_dmg": 62, "q_ratio": 52,
    "q_champ": 25,
    # skill2: W Force of Will (League: 925 range, 40-220 + 70% AP, slow 25% 1.5 s, cd 12-8 s; upgraded true damage)
    "w_cd": 660, "w_range": 85000, "w_anim": 30, "w_rel": 12, "w_fly": 16, "w_r": 21000, "w_dmg": 55, "w_ratio": 55,
    "w_slow": 30, "w_slow_t": 90, "w_true": 20,
    # -> E Scatter the Weak (League: 700 cone of 56 deg (84 upgraded), 25-235 + 60% AP, spheres pushed stun 1.25 s,
    # cd 15 s)
    "e_cd": 840, "e_range": 70000, "e_anim": 24, "e_rel": 8, "e_gap": 30, "e_fly": 2, "e_len": 70000, "e_w": 9000,
    "e_cos": 880, "e_cos_evo": 740, "e_dmg": 45, "e_ratio": 45, "e_kb_speed": 1500, "e_kb_t": 8,
    "e_reach": 90000, "e_stun_r": 24000, "e_stun_evo": 30000, "e_stun": 75, "e_orb": 30, "e_orb_ratio": 30,
    # ult: R Unleashed Power (League: 675 range, 3 + spheres (max 7) x 90-170 + 17% AP, cd 120-80 s)
    "r_cd": 4200, "r_slot": 75000, "r_min": 2, "r_arm": 480, "r_hold": 180, "r_poll": 10, "r_anim": 40, "r_rel": 14,
    "r_gap": 5, "r_speed": 4200, "r_y": -3000, "r_dmg": 52, "r_ratio": 18,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
}
SLOTS = ("o1", "o2", "o3", "o4")


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


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else ("WithShield" if tick == "shield" else {"Time": {"tick": tick}})
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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "attack_effect_type": "Target"}


def true_magic(name, dmg, ratio):
    """AP damage through magic resistance (league_ahri Q's true damage): a 1-tick penetration flag around the hit."""
    return combine(refresh(name, 1, magic_resistance_penetration=100), magic(dmg, ratio), *rm(name))


def true_self(dmg):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit (a `Delayed` here is queued on her)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, radius, target, effects, end=(), mark=""):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(radius), "range_effect_name": n(mark) if mark else "", "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def burst(name, radius, target, effects):
    """A circle hitting once, the tick after it appears (in a lob's end_effects: round the landing point)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 2, "apply": 2,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def zone(name, radius, tick, period, first, target, effects, end=()):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": [T(e) for e in end]}


def ray(name, length, width, delay, apply, target, effects):
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: the upgrades by level
    def threshold(level):
        """The probe hit is 100 x her attack once the 99% cut is applied (atk_g a level, no item she buys gives any):
        the shield sits halfway between the level below and `level`."""
        return int(round(100 * (p["atk"] + p["atk_g"] * (level - 1.5))))

    stages = {"s1": "lv_q", "s2": "lv_w", "s3": "lv_e", "s4": "lv_r"}

    def guard():
        """2 ticks of 99% less damage and full armour penetration (league_khazix's probes); a 2-tick undying keeps her."""
        return [refresh("pr_red", 2, damaged_reduce=99, defence_penetration=100), refresh("pr_und", 2, undying=True)]

    def probe_pass(stage, then):
        amp = combine(on_me(*guard(), shield(100, 0, 3), shield(p["soak"], 0, 1), flag("pr_amp", "shield")),
                      on_me(casted(1, 1, true_self(9900))),
                      delayed(2, sw("pr_amp", then)))
        test = combine(on_me(*guard(), shield(threshold(p[stages[stage]]), 0, 3), shield(p["soak"], 0, 1),
                             flag("pr_lv", "shield")),
                       on_me(casted(1, 1, attack(0, 1000000))),
                       delayed(2, sw("pr_lv", NONE, amp)))
        # a WithShield flag with no shield of her own: a shield is on her already, it would hold the probe's flag
        return combine(flag("pr_sh", "shield"), delayed(2, sw("pr_sh", NONE, test)))

    def probe(stage):
        """Two passes pr_twice ticks apart must agree (league_evelynn's level gate); silent in a life's first re-read."""
        gain = sw(stage, NONE, combine(flag(stage, None), sw("pr_quiet", NONE, combine(cview("evo"), sfx("evo")))))
        return probe_pass(stage, on_me(delayed(p["pr_twice"], probe_pass(stage, gain))))

    # the next stage, every pr_gap ticks (pr_fast in the quiet re-read at a life's start: death cleared the stages)
    step = sw("pr_cd", NONE, combine(
        sw("pr_quiet", flag("pr_cd", p["pr_fast"]), flag("pr_cd", p["pr_gap"])),
        sw("s4", NONE, sw("s3", probe("s4"), sw("s2", probe("s3"), sw("s1", probe("s2"), probe("s1")))))))
    life = sw("init", NONE, combine(flag("init", None), refresh("pr_quiet", p["pr_quiet"]), *rm("pr_cd")))

    # ------------------------------------------------------------------ the spheres
    def pushed(radius):
        """A sphere's zone, every 2 ticks on the enemies round it: while e_go stands (2 ticks: one application) and she
        is within e_reach of the sphere, E has pushed it into them."""
        hit = [{"type": "Stun", "duration": p["e_stun"]}, magic(p["e_orb"], p["e_orb_ratio"]), view("e_stun"),
               tsfx("e_stun")]
        near = combine(*rm("e_near"), pick(p["e_reach"], "AllyOnlySelf", refresh("e_near", 1), fp=True),
                       sw("e_near", combine(*hit)), *rm("e_near"))
        return zone("orb", radius, p["orb_t"], 2, 2, "EnemyWithoutTower", [sw("e_go", near)])

    def count_in():
        """The first free slot of o1..o4 (all four full: the count stays 4, League's R throws at most 7)."""
        out = NONE
        for s in reversed(SLOTS):
            out = sw(s, out, flag(s, p["orb_t"]))
        return out

    def sphere():
        """A sphere where the lob landed: its picture, its zone and the count on her."""
        return [view("orb"), sw("s3", pushed(p["e_stun_evo"]), pushed(p["e_stun_r"])), count_in()]

    # ------------------------------------------------------------------ E Scatter the Weak
    def cone(cos):
        return {"type": "RangeEffect", "shape": {"DirDot": {"radius": p["e_len"], "range": cos}},
                "target": "EnemyWithoutTower", "apply_type": {"Forward": {"offset": 1000}},
                "effects": [magic(p["e_dmg"], p["e_ratio"]), {"type": "Knockback", "speed": p["e_kb_speed"],
                                                               "tick": p["e_kb_t"]}, view("e_hit")]}

    def e_fire():
        # the picture: a line that hits nothing, from her toward the target; its view is drawn at the line's middle
        # (the simulation's spawn event: x, y = the midpoint of from -> to), so a 1000-unit line puts the picture's
        # centre on her and the wave is drawn in the right half of its canvas
        return combine(sfx("e_cast"), ray("e_wave", 1000, p["e_w"], 14, 1, "Ally", []),
                       sw("s3", cone(p["e_cos_evo"]), cone(p["e_cos"])),
                       delayed(p["e_fly"], sfx("e_push"), refresh("e_go", 2)))

    def e_cast():
        return combine(refresh("e_cd", p["e_cd"]), anim("skill2_e", p["e_anim"]), delayed(p["e_rel"], e_fire()))

    # ------------------------------------------------------------------ Q Dark Sphere
    def q_fire():
        land = [view("q_blast"), sfx("q_blast"),
                burst("q_burst", p["q_r"], "EnemyWithoutTower", [magic(p["q_dmg"], p["q_ratio"]), view("q_hit")]),
                sw("s1", burst("q_champ", p["q_r"], "EnemyChampion",
                               [magic(p["q_dmg"] * p["q_champ"] // 100, p["q_ratio"] * p["q_champ"] // 100)])),
                *sphere()]
        return combine(sfx("q_cast"), lob("q_fall", p["q_fall"], 1000, "EnemyWithoutTower", [], end=land, mark="q_form"))

    q_plain = combine(anim("skill", p["q_anim"]), voice("vo_q", p), delayed(p["q_rel"], q_fire()))
    # the pros' QE: the sphere lands on the champion, a tick later E pushes it into him
    q_e = combine(refresh("q_aim", 1), anim("skill", p["q_anim"]), voice("vo_q", p), delayed(p["q_rel"], q_fire()),
                  refresh("e_cd", p["e_cd"]),
                  delayed(p["q_rel"] + p["q_fall"] + 1, anim("skill2_e", p["e_anim"]), delayed(p["e_rel"], e_fire())))
    skill = action("skill", p["q_anim"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(*rm("q_aim"), sw("e_cd", NONE, pick(p["q_range"], "EnemyChampion", q_e)),
                           sw("q_aim", NONE, q_plain)))

    # ------------------------------------------------------------------ skill2: W Force of Will -> E
    def w_fire():
        hit = [magic(p["w_dmg"], p["w_ratio"]),
               sw("s2", true_magic("w_pen", p["w_dmg"] * p["w_true"] // 100, p["w_ratio"] * p["w_true"] // 100)),
               buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_hit")]
        land = [view("w_land"), sfx("w_land"), burst("w_burst", p["w_r"], "EnemyWithoutTower", hit), *sphere()]
        return combine(sfx("w_throw"), lob("w_throw", p["w_fly"], 1000, "EnemyWithoutTower", [], end=land))

    w_cast = combine(anim("skill2", p["w_anim"]), sfx("w_grab"), voice("vo_w", p), delayed(p["w_rel"], w_fire()))
    w_then_e = combine(refresh("w_aim", 1), w_cast,
                       sw("e_cd", NONE, combine(refresh("e_cd", p["e_cd"]),
                                                delayed(p["e_gap"], anim("skill2_e", p["e_anim"]),
                                                        delayed(p["e_rel"], e_fire())))))
    skill2 = action("skill2", p["w_anim"], p["w_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(*rm("w_aim"), pick(p["w_range"], "EnemyChampion", w_then_e),
                            sw("w_aim", NONE, sw("e_cd", w_cast, combine(voice("vo_e", p), e_cast())))))

    # ------------------------------------------------------------------ R Unleashed Power
    def ladder():
        """One more sphere counted: the lowest c<i> not yet standing."""
        out = NONE
        for i in range(p["r_min"], 0, -1):
            out = sw(f"c{i}", out, refresh(f"c{i}", 2))
        return out

    def count():
        """2-tick flags c1 .. c<r_min>: how many spheres she holds, up to r_min (c<r_min> = enough)."""
        return combine(*rm(*[f"c{i}" for i in range(1, p["r_min"] + 1)]), *[sw(s, ladder()) for s in SLOTS])

    def shot():
        hit = [sw("s4", true_magic("r_pen", p["r_dmg"], p["r_ratio"]), magic(p["r_dmg"], p["r_ratio"])),
               view("r_hit"), tsfx("r_hit")]
        return combine(sfx("r_launch"), homing("r_orb", p["r_speed"], p["r_y"], "EnemyChampion", hit))

    def fire():
        volley = [delayed(i * p["r_gap"], shot()) for i in range(3)]
        volley += [sw(s, delayed((3 + k) * p["r_gap"], shot())) for k, s in enumerate(SLOTS)]
        return combine(*rm("r_armed"), sfx("r_cast"), voice("vo_r", p), anim("ult", p["r_anim"]),
                       cview("r_cast"), delayed(p["r_rel"], *volley))

    enough = f"c{p['r_min']}"
    # armed: a poll on her every r_poll ticks fires it on a crowd-controlled champion in reach, with r_min spheres
    # counted, or with what she has once r_hold ticks have passed; it lapses with a refund (a 3-tick
    # ult_cooldown_mult 4900)
    look = sw("r_armed", combine(
        *rm("r_cc"),
        pick(p["r_slot"], "EnemyChampionInCC", refresh("r_cc", 1), fire()),
        sw("r_cc", NONE, combine(count(), sw(enough, pick(p["r_slot"], "EnemyChampion", fire()),
                                             sw("r_wait", NONE, pick(p["r_slot"], "EnemyChampion", fire())))))))
    arm = combine(refresh("r_armed", p["r_arm"]), refresh("r_wait", p["r_hold"]),
                  on_me(casted(p["r_arm"] - 2, p["r_poll"], look)),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    ult = action("ult", 3, p["r_cd"], 1, p["r_slot"], "Targeting", "EnemyChampion",
                 combine(count(), sw(enough, fire(), arm)))

    # ------------------------------------------------------------------ attack: the bolt
    shoot = delayed(p["a_st"], sfx("shot"), homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy",
                                                   [attack(0, 100), view("a_hit"), tsfx("hit")]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, step, shoot), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    # flying spheres are drawn round (top-bottom symmetric); E's wave picture is turned with its line (top-bottom
    # symmetric); the sphere on the ground, the blasts and the landing marks are ViewEffects (never turned); late
    # caster pictures don't follow her
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1, rep=True: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                                "repeat": rep, "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("a_bolt"), P_("w_throw"), P_("r_orb"), P_("e_wave", BIG, 1, False)]
    views_e = [E("a_hit"), E("q_form", BIG, -2, **LATE), E("q_blast", BIG, -1, **LATE), E("q_hit"),
               E("orb", BIG, 1, **LATE), E("w_land", BIG, -1, **LATE), E("w_hit"), E("e_hit"), E("e_stun"),
               E("r_cast", BIG, 3), E("r_hit"), E("evo", FX, 3, **LATE)]
    views_b = [B_("w_slow", FX, -1)]
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "CC", "Range"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2",
                        f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
