"""Build league_viktor.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_viktor.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-07: Q alone / W -> E combo with the pros' combos / Glorious Evolution by level / E's ray
League's way, from a start point on the target sweeping on / R's storm riding a champion and moving on when he dies):
  passive Glorious Evolution (光荣进化): League upgrades a spell every 100 Hex Fragments; nothing in data counts them
          across deaths (death clears a mod's caster buffs), so the upgrades come by level, re-read every life
          (league_khazix's evolutions): his attacks probe his attack against the level table - mages buy only ability
          power (every base mage and league_brand in the simulation), so his attack is atk + atk_g a level and nothing
          else. Under 2 ticks of 99% less damage and full armour penetration, a 3-tick shield halfway below the level, a
          1-tick soak shield, a hit of 10000 x his attack from a 1-run `AddCasted` (damage over time never crits): a
          broken probe shield = the level; a 100 shield against a 9900 hit guards against damage amplification; another
          shield on him (his own Q's) = try later; two passes pr_twice ticks apart must agree. One probe every pr_gap
          ticks for the next stage; each life's first attack re-reads the stages silently.
          Level lv_e: E's aftershock (s1); lv_q: Q's Turbocharge (s2: shield x q_sh_evo%, +q_ms% move speed); lv_w: W's
          passive (s3: every hit of his spells slows evo_slow% for evo_slow_t); lv_r: R grows (s4: the storm's
          radius r_r_evo, and a move to the next champion lasts r_jump_evo runs instead of r_jump_runs).
  attack  A homing bolt from his staff (physical 100% AD). Q's charge: the next attack within q_buff_t ticks is a
          blast adding q_aa + q_aa_ratio% AP magic damage.
  skill   Q Siphon Power (虹吸能量): a `Targeting` cast on `EnemyWithoutTower` (q_range). A homing bolt: q_dmg + q_ratio%
          AP magic damage; on its hit he gains a q_sh + q_sh_ratio% AP shield for q_sh_t ticks and the charge above.
  skill2  W Gravity Field (重力场) -> E Hextech Ray (海克斯射线): a `Targeting` cast on `EnemyWithoutTower` (e_range).
          With W ready (the caster flag w_cd off) and an enemy champion within w_range (RandomTarget, league_morgana's
          aim) W goes to that champion, w_rel ticks in: a hidden 1-tick lob lays the field on his spot - a slow zone
          (w_r, w_t ticks, every w_period ticks w_slow% for w_period ticks: same-name buffs add up, so one at a time)
          and, w_stun_at ticks after it lands, a stun of w_stun on every enemy still inside (League: 1.25 s inside ->
          stunned 1.5 s; a field point keeps the circle where it landed). The field's picture is a `ViewEffect` on the
          point (a zone's view is turned with the cast). e_gap ticks after W the ray goes at the same champion; with W
          on cooldown or no champion in reach the ray goes at the cast target (it clears waves).
          E: League starts the ray at a point and sweeps it on. A hidden 1-tick lob onto the target; its end_effects
          start a `LineRangeProjectile` there, which points from the caster to the point (champion-data section 6):
          the ray starts on the target and runs e_len on away from him (League's start-on-the-first-enemy, drag through
          the rest); it hits e_apply ticks after it appears (the sweep's time): e_dmg + e_ratio% AP magic damage.
          Evolved (s1), e_after ticks later the aftershock on the same line (a `Delayed` in end_effects keeps the
          point): e_after_dmg + e_after_ratio% AP.
  ult     R Arcane Storm (奥术风暴): a 3-tick `Targeting` cast on `EnemyChampion` (r_slot). Armed like league_seraphine R:
          with two enemy champions within r_reach (or one held by crowd control - W's stun: the pros' W -> R) it fires,
          else it arms r_armed for r_arm ticks - his attacks look again, after r_hold ticks one champion in attack
          reach is enough - and refunds the cooldown when it lapses unused. The storm rides its champion (league_annie's
          Tibbers): a 1-tick lob bursts round him (r_r): r_dmg + r_ratio% AP, then an `AddCasted` on him runs r_runs
          times a second: its picture over him (a `ViewEffect` that walks with him) and a 1-tick lob whose circle deals
          r_tick + r_tick_ratio% AP to every enemy round him. League's storm moves on to the champions it hurt: each
          run's landing leaves a hidden zone (r_jump_r) that ends a tick after the next run; the next run renews the
          6-tick caster flag r_live, so a zone ending without it means its champion died since: the first enemy
          champion inside takes the storm (r_jump_runs more runs, r_jump_evo evolved; at most r_jumps moves) while the
          storm's window r_on lasts.
  combos  (the pros' order W -> E -> Q -> R): W's stun lands, then with Q's flag q_cd off Q goes to a stunned champion
          in Q's reach (no pose of its own, the bolt at once; his next attack is the charged blast); an armed R fires
          on a crowd-controlled champion (above).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_viktor.data_champion")
ID = "league_viktor"
FX = "asset/league/effects/league_viktor_fx"
BIG = "asset/league/effects/league_viktor_big"

# Numbers = the draft d0 (before the simulations).
P = {
    # stats (Magician base: attack 80 +6, magic power 40 +20, hp 900 +100, defence 20, mr 20, move 900, range 60000,
    # attack cooldown 90); League's Viktor: 525 range, 53 AD, 600 + 100 hp, 23 armour, 335 move speed.
    # atk_g is also the level gauge of the evolutions (7 a level: probe steps of 700)
    "hp": 880, "hp_g": 95, "atk": 78, "atk_g": 7, "mp": 40, "mp_g": 20, "def": 20, "def_g": 7, "mr": 20, "mr_g": 4,
    "ms": 920, "ms_g": 9,
    # attack (League 525 range); the bolt leaves the staff 8 px over the pivot
    "atk_range": 55000, "atk_dur": 28, "atk_cd": 90, "a_st": 10, "bolt_speed": 4500, "bolt_y": -3000,
    # passive: the evolutions' levels and the probe
    "lv_e": 3, "lv_q": 5, "lv_w": 7, "lv_r": 9, "pr_gap": 120, "pr_fast": 40, "pr_quiet": 900, "pr_twice": 30, "soak": 1000000,
    # skill: Q Siphon Power (League: 600 range, 45-135 + 40% AP, shield 2.5 s, next attack within 4 s -5..145 + 50% AP,
    # upgraded shield +60% and 30% move speed; cd 9-5 s)
    "q_cd": 480, "q_range": 60000, "q_anim": 24, "q_rel": 9, "q_speed": 5000, "q_dmg": 60, "q_ratio": 45,
    "q_sh": 40, "q_sh_ratio": 20, "q_sh_t": 150, "q_sh_evo": 160, "q_ms": 30, "q_buff_t": 240,
    "q_aa": 30, "q_aa_ratio": 45,
    # skill2: W Gravity Field (League: 800 range, radius 275-300, 4 s, slow 30-48%, 1.25 s inside -> 1.5 s stun,
    # cd 18-13 s; upgraded: his spells slow 20% for 1 s)
    "w_cd": 960, "w_range": 70000, "w_anim": 20, "w_rel": 9, "w_r": 30000, "w_t": 240, "w_period": 6, "w_slow": 35,
    "w_stun_at": 75, "w_stun": 75, "evo_slow": 20, "evo_slow_t": 60,
    # -> E Hextech Ray (League: start within 550, ray 700, 30-270 + 50% AP, aftershock after 1 s -10..170 + 80% AP,
    # cd 12-8 s)
    "e_cd": 600, "e_range": 75000, "e_anim": 26, "e_rel": 10, "e_gap": 18, "e_len": 70000, "e_w": 9000,
    "e_apply": 8, "e_fly": 1, "e_cos": 985, "e_dmg": 60, "e_ratio": 50, "e_after": 60, "e_after_dmg": 40, "e_after_ratio": 60,
    # ult: R Arcane Storm (League: 700 range, radius 325, 6.5 s, burst 100-400 + 50% AP, 65-265 + 35% AP a second,
    # follows the champions it hurt; upgraded: faster, grows and lasts 3 s more when one of them dies; cd 120-80 s)
    "r_cd": 4200, "r_slot": 70000, "r_reach": 60000, "r_arm": 600, "r_hold": 180, "r_poll": 10, "r_anim": 30, "r_rel": 12,
    "r_fall": 6, "r_r": 30000, "r_r_evo": 38000, "r_dmg": 100, "r_ratio": 50, "r_tick": 35, "r_tick_ratio": 20,
    "r_runs": 6, "r_jump_r": 45000, "r_jump_runs": 2, "r_jump_evo": 5, "r_jumps": 2,
    # combos
    "wq_wait": 4,
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


def true_self(dmg):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, radius, target, effects, end=()):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "shape": circle(radius), "range_effect_name": "", "applied_target": target,
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
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # W's upgraded passive: every hit of his spells slows (read on him: SwitchByBuff reads the caster)
    evo_slow = sw("s3", buff("evo_slow", p["evo_slow_t"], move_speed_mult=-p["evo_slow"]))

    # ------------------------------------------------------------------ passive: the evolutions by level
    def threshold(level):
        """The probe hit is 100 x his attack once the 99% cut is applied (atk_g a level, no item he buys gives any):
        the shield sits halfway between the level below and `level`."""
        return int(round(100 * (p["atk"] + p["atk_g"] * (level - 1.5))))

    stages = {"s1": "lv_e", "s2": "lv_q", "s3": "lv_w", "s4": "lv_r"}

    def guard():
        """2 ticks of 99% less damage and full armour penetration (league_khazix's probes); a 2-tick undying keeps him."""
        return [refresh("pr_red", 2, damaged_reduce=99, defence_penetration=100), refresh("pr_und", 2, undying=True)]

    def probe_pass(stage, then):
        amp = combine(on_me(*guard(), shield(100, 0, 3), shield(p["soak"], 0, 1), flag("pr_amp", "shield")),
                      on_me(casted(1, 1, true_self(9900))),
                      delayed(2, sw("pr_amp", then)))
        test = combine(on_me(*guard(), shield(threshold(p[stages[stage]]), 0, 3), shield(p["soak"], 0, 1),
                             flag("pr_lv", "shield")),
                       on_me(casted(1, 1, attack(0, 1000000))),
                       delayed(2, sw("pr_lv", NONE, amp)))
        # a WithShield flag with no shield of his own: a shield is on him already (Q's), it would hold the probe's flag
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

    # ------------------------------------------------------------------ Q Siphon Power
    def q_bolt():
        mine = [*rm("q_buff"), flag("q_buff", p["q_buff_t"]), sfx("q_shield"),
                sw("s2", combine(shield(p["q_sh"] * p["q_sh_evo"] // 100, p["q_sh_ratio"] * p["q_sh_evo"] // 100,
                                        p["q_sh_t"]),
                                 refresh("q_ms", p["q_sh_t"], move_speed_mult=p["q_ms"])),
                   shield(p["q_sh"], p["q_sh_ratio"], p["q_sh_t"])),
                cview("q_shield")]
        return homing("q_bolt", p["q_speed"], p["bolt_y"], "EnemyWithoutTower",
                      [magic(p["q_dmg"], p["q_ratio"]), evo_slow, view("q_hit"), tsfx("q_hit"), on_me(*mine)])

    q_slot = combine(refresh("q_cd", p["q_cd"]), sfx("q_cast"), voice("vo_q", p), anim("skill", p["q_anim"]),
                     delayed(p["q_rel"], q_bolt()))
    # the combo's Q: no pose of its own, the bolt at once
    q_combo = combine(refresh("q_cd", p["q_cd"]), sfx("q_cast"), q_bolt())

    # ------------------------------------------------------------------ skill2: W Gravity Field -> E Hextech Ray
    def field():
        stun = [{"type": "Stun", "duration": p["w_stun"]}, view("w_stun")]
        # W -> Q: a tick after the stun, Q on a stunned champion in reach
        w_q = on_me(delayed(p["w_stun_at"] + p["wq_wait"],
                            sw("q_cd", NONE, pick(p["q_range"], "EnemyChampionInCC", q_combo))))
        land = [view("w_field"), sfx("w_field"),
                zone("w_zone", p["w_r"], p["w_t"], p["w_period"], 0, "EnemyWithoutTower",
                     [buff("w_slow", p["w_period"], move_speed_mult=-p["w_slow"])]),
                delayed(p["w_stun_at"], view("w_burst"), sfx("w_stun"), burst("w_stun", p["w_r"], "EnemyWithoutTower", stun))]
        return combine(lob("w_lay", 1, 1000, "EnemyChampion", [], end=land), w_q)

    def beam(name, delay, apply, effects):
        """The ray's hit: a narrow cone on the landing point opening away from him (DirDot: within e_len of the point
        and at most acos(e_cos / 1000) off the direction from him to it). The unit standing on the point is inside
        it (the start of the ray); a circle there as well hit it twice in a quarter of the casts."""
        return {"type": "RangeProjectile", "name": n(name), "shape": {"DirDot": {"radius": p["e_len"], "range": p["e_cos"]}},
                "delay": delay, "apply": apply, "applied_target": "EnemyWithoutTower",
                "applied_effects": [T(e) for e in effects]}

    def hex_ray():
        hit = [magic(p["e_dmg"], p["e_ratio"]), evo_slow, view("e_hit")]
        after = [magic(p["e_after_dmg"], p["e_after_ratio"]), evo_slow, view("e_after_hit")]
        # the picture: a line that hits nothing, drawn on the landing point and turned from him to it (its canvas
        # centre is the point: the ray is drawn on the right half)
        land = [ray("e_ray", 2 * p["e_len"], p["e_w"], p["e_apply"] + 6, 1, "Ally", []),
                beam("e_beam", p["e_apply"] + 1, p["e_apply"], hit),
                sw("s1", delayed(p["e_after"], sfx("e_after"), ray("e_after", 2 * p["e_len"], p["e_w"], 14, 1, "Ally", []),
                                 beam("e_after_beam", 9, 8, after)))]
        return combine(sfx("e_ray"), lob("e_start", p["e_fly"], 1000, "EnemyWithoutTower", [], end=land))

    e_only = combine(anim("skill2_e", p["e_anim"]), voice("vo_e", p), delayed(p["e_rel"], hex_ray()))
    w_then_e = combine(refresh("w_cd", p["w_cd"]), refresh("w_aim", 1), anim("skill2", p["w_anim"] + p["e_gap"]),
                       sfx("w_cast"), voice("vo_w", p), delayed(p["w_rel"], field()),
                       delayed(p["e_gap"], anim("skill2_e", p["e_anim"]), delayed(p["e_rel"], hex_ray())))
    skill2 = action("skill2", p["e_gap"] + p["e_anim"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(*rm("w_aim"), sw("w_cd", NONE, pick(p["w_range"], "EnemyChampion", w_then_e)),
                            sw("w_aim", NONE, e_only)))

    # ------------------------------------------------------------------ R Arcane Storm
    def count():
        """2-tick flags u1 -> u2: two enemy champions within r_reach."""
        return combine(*rm("u1", "u2"),
                       around(p["r_reach"], "EnemyChampion", [sw("u1", refresh("u2", 2), refresh("u1", 2))]))

    def storm(big, runs, first, depth):
        """On the champion it rides (the effects run on him): the burst (first), then `runs` runs a second; each run's
        landing leaves the zone that moves the storm on when he dies (depth: moves left). big = evolved (s4, read at
        the cast: one branch at the top keeps the nested moves linear)."""
        r = p["r_r_evo"] if big else p["r_r"]
        jump = p["r_jump_evo"] if big else p["r_jump_runs"]
        landing = [burst("r_tick", r, "EnemyWithoutTower", [magic(p["r_tick"], p["r_tick_ratio"]), evo_slow, view("r_hit")]),
                   sfx("r_tick")]
        if depth > 0:
            # the lock is read back: on a dead caster nothing is added (his flags freeze), so no storm moves then
            nxt = sw("r_live", NONE, sw("r_on", sw("r_lock", NONE, combine(refresh("r_lock", 3), sw("r_lock", combine(
                sfx("r_storm"), refresh("r_on", 60 * jump + 30), storm(big, jump, False, depth - 1)))))))
            landing.append(zone("r_watch", p["r_jump_r"], 62, 1000, 1000, "EnemyChampion", [], end=[nxt]))
        run = [on_me(refresh("r_live", 6)), view("r_storm_big" if big else "r_storm"),
               lob("r_drop", 1, 1000, "EnemyChampion", [], end=landing)]
        out = [delayed(60, casted(60 * (runs - 1) + 1, 60, *run, kind="Fire"))]
        if first:
            hit = [magic(p["r_dmg"], p["r_ratio"]), evo_slow, view("r_hit")]
            out.insert(0, lob("r_fall", p["r_fall"], 1000, "EnemyChampion", [],
                              end=[view("r_land"), sfx("r_burst"), burst("r_burst", r, "EnemyWithoutTower", hit)]))
        return combine(*out)

    def fire(slot):
        rel = p["r_rel"] if slot else 0
        out = [*rm("r_armed"), sfx("r_cast"), voice("vo_r", p), refresh("r_on", rel + 60 * p["r_runs"] + 30),
               delayed(rel, sw("s4", storm(True, p["r_runs"], True, p["r_jumps"]),
                               storm(False, p["r_runs"], True, p["r_jumps"])))]
        if slot:
            out.append(anim("ult", p["r_anim"]))
        return combine(*out)

    # armed: a poll on him every r_poll ticks fires it on a crowd-controlled champion in reach, with two champions
    # near (at one in his attack's reach), or at one in his attack's reach once r_hold ticks have passed; it lapses
    # with a refund (a 3-tick ult_cooldown_mult 4900)
    near = pick(p["atk_range"] + 5000, "EnemyChampion", refresh("r_solo", 2))
    look = sw("r_armed", combine(
        *rm("r_solo", "r_cc"),
        pick(p["r_slot"], "EnemyChampionInCC", refresh("r_cc", 1), fire(False)),
        sw("r_cc", NONE, combine(count(), sw("u2", refresh("r_solo", 2), sw("r_wait", NONE, near)),
                                 sw("r_solo", pick(p["atk_range"] + 5000, "EnemyChampion", fire(False)))))))
    arm = combine(refresh("r_armed", p["r_arm"]), refresh("r_wait", p["r_hold"]),
                  on_me(casted(p["r_arm"] - 2, p["r_poll"], look)),
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                 flag("r_refund", 3, ult_cooldown_mult=4900)))))
    # the slot: two champions near fire it at the target, else it arms (the poll's first look, a tick later, fires it
    # on a crowd-controlled champion in reach)
    ult = action("ult", 3, p["r_cd"], 1, p["r_slot"], "Targeting", "EnemyChampion",
                 combine(count(), sw("u2", fire(True), arm)))

    # ------------------------------------------------------------------ the slots
    skill = action("skill", p["q_anim"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   sw("q_cd", NONE, q_slot))

    # ------------------------------------------------------------------ attack: the bolt, or Q's charged blast
    blast = combine(*rm("q_buff"), delayed(p["a_st"], sfx("q_blast"),
                                           homing("a_blast", p["bolt_speed"], p["bolt_y"], "Enemy",
                                                  [attack(0, 100), magic(p["q_aa"], p["q_aa_ratio"]), view("a_blast_hit")])))
    shoot = sw("q_buff", blast, delayed(p["a_st"], sfx("a_shot"),
                                         homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy",
                                                [attack(0, 100), view("a_hit")])))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, step, shoot), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ views
    # flying bolts are drawn top-bottom symmetric; the ray's picture is turned with its line (top-bottom symmetric);
    # the field, the stun burst and the storm are ViewEffects (never turned); late caster pictures don't follow him
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1, rep=True: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                                "repeat": rep, "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("a_bolt"), P_("a_blast"), P_("q_bolt"), P_("e_ray", BIG, 1, False), P_("e_after", BIG, 1, False)]
    views_e = [E("a_hit"), E("a_blast_hit"), E("q_hit"), E("q_shield", FX, 3, **LATE), E("w_field", BIG, -2, **LATE),
               E("w_burst", BIG, -1, **LATE), E("w_stun"), E("e_hit"), E("e_after_hit"), E("r_land", BIG, -1, **LATE),
               E("r_storm", BIG, 3), E("r_storm_big", BIG, 3), E("r_hit"), E("evo", FX, 3, **LATE)]
    views_b = [B_("w_slow", FX, -1), B_("evo_slow", FX, -1), B_("q_buff", FX, 3, tag="q_charged"),
               B_("q_ms", FX, -1)]
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "CC", "Shield"],
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
