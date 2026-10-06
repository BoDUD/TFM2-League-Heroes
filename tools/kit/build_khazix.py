"""Build league_khazix.data_champion (jungle, Assassin) from the parameters P.

    python tools/kit/build_khazix.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-06, all the recommended options: Q / E -> W combo / isolation counted round the target /
evolutions by level Q -> E -> R / R stealth with recasts, the passive also ready out of combat; plus 「另外加入高手的连招」.
What the data cannot read - real vision, the exact isolation, his level - goes to a native add-on later, 「数据读不到就用rust
改写源码」; this pack is complete alone):
  passive Unseen Threat (无形威胁): `ut` (a permanent caster flag, its glow on him) makes his next attack on an enemy
          champion add ut_dmg + ut_ratio% AD magic damage and a ut_slow% slow for ut_slow_t. Nothing reads vision, so
          it readies when R hides him, at each life's start and after quiet ticks without an action of his
          (league_evelynn's shade: every action renews `fight` and queues a check on him that finds it gone only after
          the last one).
  evolve  Nothing reads a level but `SwitchByLevel3`, so his attacks probe his maximum health against the level table
          (league_kayle / league_kaisa, with ability power for the gauge: maximum health and attack grow with items -
          0 to 800 item health at level 8 in 16 simulated games - but no item he buys gives ability power, so he gains
          ap_g a level and nothing else reads it. Under 2 ticks of 99% less damage and full magic penetration, a
          3-tick shield halfway below the level, a 1-tick soak shield, his own magic hit of 10000 x his ability power
          (100 x after the cut); a broken probe shield = the level; a 100 shield against a 9900 hit guards against damage amplification; another
          shield on him = try later; two passes pr_twice ticks apart must agree). One probe every pr_gap ticks for
          the next stage; each life's first attack re-reads the stages silently (death clears caster buffs).
          Level lv_q: Reaper Claws (s1: attack range +q_evo_range, an isolated Q refunds q_ref of its cooldown);
          lv_e: Wings (s2: the leap reaches e_range_evo, a takedown resets it); lv_r: Adaptive Cloaking (s3: stealth
          r_inv_evo ticks, three casts).
  attack  A claw swing; the hit a_st ticks in. A champion-only twin carries the passive and the kill check.
  skill   Q Taste Their Fear (品尝恐惧): a `Targeting` cast on `EnemyWithoutTower` (q_range). On tick 1 a hidden 1-tick
          lob lands on the target and a zone of iso_r there counts the units of the target's side (league_kayle R's
          1-tick flags i1, i2: the target is the first); q_at ticks in the claw lands: q_dmg + q_ratio% AD, or
          isolated (no i2) q_iso_dmg + q_iso_ratio% AD (League's +110%) and, evolved, a 2-tick skill_cooldown_mult
          q_ref with ult_cooldown_mult -q_ref (league_sivir R: the ult keeps its cap).
  skill2  E Leap (跃击) -> W Void Spike (虚空突刺): a `Targeting` cast on `EnemyChampion` (e_range_evo). With an enemy
          champion within e_range (or evolved) he leaps onto the target (`MoveToTarget`), else as far as he can toward
          it (`RushTime` e_speed x e_short_t). Landing (e_t): e_dmg + e_ratio% AD round him (e_rad); w_at ticks later a
          spike at the target (w_dmg + w_ratio% AD, w_slow% slow for w_slow_t; it bursts within w_blast: he heals
          w_heal + w_heal_r% AD when he stands in it). Evolved Wings: his champion takedowns (league_jinx's kill check
          on every champion hit) reset E - a 2-tick skill_cooldown_mult with the ult's cap kept.
  ult     R Void Assault (虚空来袭): a 3-tick `Targeting` cast on `EnemyChampion` (r_range): `CasterInvisible` r_inv
          ticks, r_ms% move speed while hidden, the passive ready. Recasts: a first cast (r_c1) and, evolved, a second
          (r_c2) cap the ult's cooldown at r_recast (a 3-tick ult_cooldown_mult); the last use leaves the full cooldown.
  combos  (the user: 「另外加入高手的连招」; league_leesin's way: each combo is the slot it spends, no slot held)
          E -> Q A: Q cast within eq_t of a leap that landed by a champion runs straight into a claw swing (the attack's
          pose and hit, its cooldown untouched). Q -> R A: R cast within qr_t of a Q on a champion swings at once out
          of the stealth, the passive on it. R -> E W A: E cast in R's stealth (re_t) swings once the spike is thrown.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_khazix.data_champion")
ID = "league_khazix"
FX = "asset/league/effects/league_khazix_fx"
BIG = "asset/league/effects/league_khazix_big"

# Timings fitted to the strips (assets/source/native/khazix_cells.json): the claw's hit on tick 11 (attack frame 4),
# Q's stab on tick 12 (frame 4, the strip 25 ticks), E's landing on 14 (frames 1-4), W's throw 6 later (frame 6), R's
# flare 18 ticks (the strip's 300 ms).
# Numbers = candidate c2 of the 10-min classic-SDK simulations (tr_sim/sim/kd.py --lane 1 against demon, circus_blade,
# hunter, inquisitor and ninja, three lineups, both sides, 2026-10-06): +1.18 on seeds 1-24 and +1.11 on 25-48
# (league_kayn +1.38 / +1.33, league_xinzhao +1.02 / +1.54 on the same seeds). The draft c0 was +6.96 (15788 damage a
# game, twice Kayn's: 12 Qs on champions, 46 on camps, most of them isolated): attack 106 +25 -> 85 +16, Q 40 + 100%
# (isolated 84 + 200%) -> 25 + 65% (40 + 115%), E 40 + 50% -> 25 + 35%, W 50 + 80% -> 30 + 50% (heal 40 + 25% ->
# 30 + 15%), the passive 30 + 40% -> 15 + 25%, hp 920 +88 -> 880 +84 (c1, half way: +3.35; c3, a step further: +0.16).
P = {
    # stats (Assassin base: attack 120 +30, hp 900 +80, defence 25, mr 15, move 1100, range 23000, cooldown 50);
    # League's Kha'Zix: 643 +99 hp, 60 AD +3.1, 32 armour, 350 move, 125 range
    "hp": 880, "hp_g": 84, "atk": 85, "atk_g": 16, "def": 26, "def_g": 8, "mr": 18, "mr_g": 4, "ms": 1100, "ms_g": 13,
    # attack: the claw swing
    "atk_range": 23000, "atk_dur": 22, "atk_cd": 50, "a_st": 11,
    # passive: Unseen Threat (League: 14-150 by level + 40% bonus AD magic, 25% slow 2 s)
    "ut_dmg": 15, "ut_ratio": 25, "ut_slow": 25, "ut_slow_t": 120, "quiet": 240,
    # evolutions: the level probe (league_kaisa's soak; the hit is absorbed whole) and the levels
    "pr_gap": 120, "ap_g": 1, "soak": 1000000, "lv_q": 5, "lv_e": 8, "lv_r": 11, "pr_stagger": 8,
    "pr_twice": 30,
    # skill: Q Taste Their Fear (League: 325 range (evolved 375), 60-160 + 110% bonus AD, isolated +110%,
    # evolved isolated refund 45%, cd 4 s; isolation: no allied unit within 375)
    "q_cd": 240, "q_range": 26000, "q_dur": 24, "q_at": 12, "q_dmg": 25, "q_ratio": 65, "q_iso_dmg": 40,
    "q_iso_ratio": 115, "iso_r": 30000, "q_evo_range": 6000, "q_ref": 82,
    # skill2: E Leap (League: 700 range (evolved 900), 65-240 + 20% bonus AD, cd 22-12 s, evolved takedown reset)
    # -> W Void Spike (League: 1025 range, 1700 speed, 85-205 + 100% bonus AD, heal 55-155 within the blast, cd 9 s)
    "e_cd": 720, "e_range": 60000, "e_range_evo": 80000, "e_speed": 7000, "e_short_t": 8, "e_t": 14, "e_rad": 22000,
    "e_dmg": 25, "e_ratio": 35, "w_at": 6, "w_t": 18, "w_speed": 9000, "w_len": 70000, "w_rad": 6000, "w_y": 2000,
    "w_dmg": 30, "w_ratio": 50, "w_slow": 40, "w_slow_t": 120, "w_heal": 30, "w_heal_r": 15, "w_blast": 30000,
    "reset_mult": 10000,
    # ult: R Void Assault (League: stealth 1.25 s (evolved 2 s), +40% move speed, 2 casts (evolved 3), recast after 2 s,
    # cd 100-70 s)
    "r_cd": 3000, "r_range": 70000, "r_anim": 18, "r_inv": 75, "r_inv_evo": 120, "r_ms": 40, "r_recast": 120,
    # combos (the user: 「另外加入高手的连招」)
    "eq_t": 150, "qr_t": 150, "re_t": 120,
    "k_hold": 40, "k_read": 4,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_khazix: its native passive reads his level and the enemy's vision, so the probes
    # and the out-of-combat stand-in go (R's stealth still readies the passive)
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


def ap(dmg, ratio):
    """Magic damage: `ApAttack`'s attack_ratio reads ability power (his is 0), so League's AD-scaled magic damage of
    Unseen Threat is a flat magic part here plus a physical `Attack` for the AD part."""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def true_self(hp_ratio=0, dmg=0):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": hp_ratio, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def heal(amount, ratio, kind="Caster"):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": kind}


def shield(amount, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": 0, "tick": tick}


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


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lob(name, end):
    """A hidden 1-tick lob: it lands on the unit's spot the tick it is fired; `end` runs on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000, "shape": circle(1000),
            "range_effect_name": "", "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Unseen Threat
    ready = sw("ut", NONE, combine(flag("ut", None), cview("p_ready"), sfx("p_ready")))
    # an action of his renews `fight`; the check queued by the last one finds it gone (league_evelynn's shade)
    act = combine(refresh("fight", p["quiet"]), on_me(delayed(p["quiet"] + 2, sw("fight", NONE, ready))))         if not p["native"] else NONE
    proc = sw("ut", combine(*rm("ut"), ap(p["ut_dmg"], 0), attack(0, p["ut_ratio"]),
                            buff("p_slow", p["ut_slow_t"], move_speed_mult=-p["ut_slow"]), view("p_hit"),
                            tsfx("p_hit")))

    # ------------------------------------------------------------------ takedowns: league_jinx's kill check
    # Evolved Wings: a takedown resets E. A 2-tick skill_cooldown_mult caps every cooldown (Q's too); the ult keeps
    # its cap through ult_cooldown_mult -m (league_sivir R).
    reset = combine(refresh("e_reset", 2, skill_cooldown_mult=p["reset_mult"], ult_cooldown_mult=-p["reset_mult"]),
                    cview("e_reset"), sfx("e_reset"))

    def kill_check(src):
        """On a hit enemy champion, around its damage: the flag before, the living target's clear after, the read on
        him later (only once Wings evolved). Each source keeps its own flag (league_tristana W)."""
        k = f"k_{src}"
        return (sw("s2", refresh(k, p["k_hold"])),
                sw("s2", combine(casted(3, 1, *rm(k)), on_me(delayed(p["k_read"], sw(k, combine(*rm(k), reset)))))))

    # ------------------------------------------------------------------ evolutions: the level probe
    def threshold(level):
        """The probe hit is 100 x his ability power (ap_g a level, no item gives him any) once the 99% cut is applied:
        the shield sits halfway between the level below and `level`."""
        return int(round(100 * p["ap_g"] * (level - 1.5)))

    stages = {
        "s1": ("lv_q", dict(range=p["q_evo_range"]), "evo_q"),
        "s2": ("lv_e", {}, "evo_e"),
        "s3": ("lv_r", {}, "evo_r"),
    }

    def guard():
        """2 ticks of 99% less damage (league_kaisa's probes): a monster's or champion's hit in the window costs the
        probe shield 1% of itself, his own hit is 100 times the size it is measured at; a 2-tick undying keeps him.
        The hits come from a 1-run `AddCasted` on him (damage over time): straight in the attack they rolled his
        critical strikes (twice the hit, a stage early in the simulation once he bought crit chance)."""
        return [refresh("pr_red", 2, damaged_reduce=99, magic_resistance_penetration=100),
                refresh("pr_und", 2, undying=True)]

    def probe_pass(stage, then):
        amp = combine(on_me(*guard(), shield(100, 3), shield(p["soak"], 1), flag("pr_amp", "shield")),
                      on_me(casted(1, 1, true_self(dmg=9900))),
                      delayed(2, sw("pr_amp", then)))
        test = combine(on_me(*guard(), shield(threshold(p[stages[stage][0]]), 3), shield(p["soak"], 1),
                             flag("pr_lv", "shield")),
                       on_me(casted(1, 1, ap(0, 1000000))),
                       delayed(2, sw("pr_lv", NONE, amp)))
        # a WithShield flag with no shield of his own: someone else's shield is on him (it would hold the probe's flag)
        return combine(flag("pr_sh", "shield"), delayed(2, sw("pr_sh", NONE, test)))

    def probe(stage, loud):
        """Two passes pr_twice ticks apart must agree (league_evelynn's level gate)."""
        _, fields, name = stages[stage]
        gain = sw(stage, NONE, combine(flag(stage, None, **fields),
                                       *([cview("evo"), sfx("evo"), sfx(f"vo_{name}")] if loud else [])))
        return probe_pass(stage, on_me(delayed(p["pr_twice"], probe_pass(stage, gain))))

    step = sw("pr_cd", NONE, combine(flag("pr_cd", p["pr_gap"]),
                                     sw("s3", NONE, sw("s2", probe("s3", True), sw("s1", probe("s2", True),
                                                                                    probe("s1", True))))))
    if p["native"]:
        step = NONE
    life = NONE if p["native"] else sw("init", NONE, combine(flag("init", None), flag("pr_cd", p["pr_gap"]), ready,
                                    probe("s1", False), on_me(delayed(p["pr_stagger"], probe("s2", False))),
                                    on_me(delayed(2 * p["pr_stagger"], probe("s3", False)))))

    # ------------------------------------------------------------------ the claw swing (attack and the combos' weave)
    ka_set, ka_read = kill_check("a")

    def swing_hit():
        return [attack(0, 100), view("a_hit"), tsfx("a_hit")]

    champ_a = [ka_set, proc, ka_read]
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(life, act, step, sfx("a_swing"), *swing_hit(),
                              homing("a_twin", 100000, 0, "EnemyChampion", champ_a)),
                      atype="BaseAttack", cancel=True)

    def weave(lead):
        """A claw swing on the nearest champion in reach, the attack's pose and hit; its cooldown untouched."""
        return delayed(lead, anim("attack", p["atk_dur"]), sfx("a_swing"),
                       delayed(p["a_st"], pick(p["atk_range"] + 8000, "EnemyChampion", *swing_hit(), *champ_a)))

    # ------------------------------------------------------------------ skill: Q Taste Their Fear
    count = sw("i1", refresh("i2", 8), refresh("i1", 8))
    iso_probe = lob("q_lob", [zone("q_iso", p["iso_r"], 1, 1, "EnemyWithoutTower", [count])])
    refund = refresh("q_ref", 2, skill_cooldown_mult=p["q_ref"], ult_cooldown_mult=-p["q_ref"])
    kq_set, kq_read = kill_check("q")
    plain = [attack(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")]
    lonely = [attack(p["q_iso_dmg"], p["q_iso_ratio"]), view("q_iso_hit"), tsfx("q_iso_hit"), sw("s1", refund)]
    claw = sw("i2", homing("q_cut", 100000, 0, "EnemyWithoutTower", plain),
              sw("i1", homing("q_cut_iso", 100000, 0, "EnemyWithoutTower", lonely),
                 homing("q_cut", 100000, 0, "EnemyWithoutTower", plain)))
    q_champ = homing("q_twin", 100000, 0, "EnemyChampion", [kq_set, on_me(refresh("q_land", p["qr_t"])), kq_read])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(*rm("i1", "i2"), act, iso_probe, anim("skill", p["q_dur"]), sfx("q_swing"),
                           voice("vo_q", p),
                           delayed(p["q_at"], claw, q_champ),
                           sw("e_land", combine(*rm("e_land"), weave(p["q_dur"])))))

    # ------------------------------------------------------------------ skill2: E Leap -> W Void Spike
    ke_set, ke_read = kill_check("e")
    kw_set, kw_read = kill_check("w")
    leap_full = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range_evo"] + 20000, "end_effects": []}
    leap_short = {"type": "RushTime", "speed": p["e_speed"], "tick": p["e_short_t"], "range": 1000,
                  "casting_target": "EnemyChampion", "penetrate": True, "applied_effects": []}
    land = combine(cview("e_land"), sfx("e_land"),
                   around(p["e_rad"], "EnemyChampion", [ke_set, ke_read]),
                   around(p["e_rad"], "EnemyWithoutTower", [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"),
                                                           tsfx("e_hit")]),
                   pick(p["e_rad"], "EnemyChampion", on_me(refresh("e_land", p["eq_t"]))))
    spike = combine(sfx("w_throw"),
                    line("w_spike", p["w_speed"], p["w_len"], p["w_rad"], p["w_y"], "EnemyWithoutTower", False,
                         [pick(1000, "EnemyChampion", kw_set, fp=True),
                          attack(p["w_dmg"], p["w_ratio"]),
                          buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_hit"), tsfx("w_hit"),
                          pick(p["w_blast"], "AllyOnlySelf", heal(p["w_heal"], p["w_heal_r"]), cview("w_heal"), fp=True),
                          pick(1000, "EnemyChampion", kw_read, fp=True)]))
    combo = combine(*rm("e_ok"), act, anim("skill2", p["e_t"] + p["w_t"]), sfx("e_jump"), voice("vo_e", p),
                    pick(p["e_range"], "EnemyChampion", flag("e_ok", 2)),
                    sw("s2", leap_full, sw("e_ok", leap_full, leap_short)),
                    delayed(p["e_t"], land),
                    delayed(p["e_t"] + p["w_at"], spike),
                    sw("r_hide", combine(*rm("r_hide"), weave(p["e_t"] + p["w_t"]))))
    skill2 = action("skill2", p["e_t"] + 1, p["e_cd"], 1, p["e_range_evo"], "Targeting", "EnemyChampion", combo)

    # ------------------------------------------------------------------ ult: R Void Assault
    hide = combine(sw("s3", combine({"type": "CasterInvisible", "tick": p["r_inv_evo"]},
                                    refresh("r_on", p["r_inv_evo"], move_speed_mult=p["r_ms"]),
                                    refresh("r_hide", p["r_inv_evo"] + p["re_t"] - p["r_inv"])),
                         combine({"type": "CasterInvisible", "tick": p["r_inv"]},
                                 refresh("r_on", p["r_inv"], move_speed_mult=p["r_ms"]),
                                 refresh("r_hide", p["re_t"]))),
                   rm("ut")[0], flag("ut", None), cview("r_cast"), sfx("r_cast"), voice("vo_r", p))
    r_refund = delayed(1, refresh("r_ref", 3, ult_cooldown_mult=p["r_cd"] * 100 // p["r_recast"] - 100))
    casts = sw("r_c1",
               sw("s3", sw("r_c2", combine(*rm("r_c1", "r_c2")), combine(flag("r_c2", None), r_refund)),
                  combine(*rm("r_c1", "r_c2"))),
               combine(flag("r_c1", None), r_refund))
    ult = action("ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(act, anim("ult", p["r_anim"]), hide, casts,
                         sw("q_land", combine(*rm("q_land"), weave(p["r_anim"])))))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("w_spike")]
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("q_iso_hit", BIG), E("e_land", BIG, -1, False), E("e_hit"),
               E("w_hit"), E("w_heal", FX, 3, False), E("r_cast", BIG, 3), E("p_ready", FX, 3, False),
               E("e_reset", FX, 3, False), E("evo", BIG, 3, False)]
    slow = lambda name: {**B_(name, FX, -1), "tag": "slow"}     # one picture for both slows
    views_b = [B_("ut", FX, 3), slow("p_slow"), slow("w_slow"), B_("r_on", BIG, 2)]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": "league_khazix:void",
                            "params": {k: p[k] for k in ("lv_q", "lv_e", "lv_r", "q_evo_range")}}
    return {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["ap_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
