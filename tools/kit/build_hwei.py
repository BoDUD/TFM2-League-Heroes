"""Build league_hwei.data_champion (mid, Magician: the Visionary) from the parameters P.

    python tools/kit/build_hwei.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-22: MID (the plan had him a bot stand-in), layout A - Subject: Disaster / Subject:
Torment / Spiraling Despair, Subject: Serenity folded into the passive; 「有连招要做连招」). TFM2 has three active slots:
Subject: Disaster (Q) is `skill`, Subject: Torment (E) `skill2`, Spiraling Despair (R) the `ult`. League's Hwei picks
one of three spells after each subject; here the cast picks it by the situation (all in data, no add-on):
  passive Signature of the Visionary (落款): a champion hit by a damaging ability is signed (the caster flag `sig`,
          sig_t ticks: SwitchByBuff reads only the caster); his next damaging ability on a champion within it
          finishes the signature on that champion - it bursts sig_at ticks later, sig_dmg + sig_ratio% AP (League:
          an area at the champion's feet; one champion here). One signature a cast (the 2-tick lock `sig_l`).
          Subject: Serenity (主题：靖), folded in: every Torment cast also paints Pool of Reflection (渲浓) - a shield
          of w_sh + w_sh_r% AP on him and w_ally% of it on allied champions within w_r for w_sh_t ticks - and every
          Disaster cast Fleeting Current (飞染), +w_ms% move speed for w_ms_t ticks.
  attack  A flick of ink (homing on `Enemy`, 100% AD), released on a_rel.
  skill   Subject: Disaster (主题：灾, cooldown q_cd, the flag `q_cd` the combos read): a `Targeting` cast on
          `EnemyWithoutTower` (q_range), which picks in tiers (q_go, a 1-tick flag, says one fired):
          1. a champion in crowd control within q_range -> QW Severing Bolt (攒聚雷): lightning strikes it q_w_at ticks
             later, q_w_dmg + q_w_ratio% AP and q_w_cc + q_w_cc_r% AP more (League: x2-2.75 on the immobile);
          2. else any champion within q_range -> QQ Devastating Fire (没骨火): a fireball at it, q_q_dmg + q_q_ratio% AP
             and q_q_hp% of its max health (League: 3-5% max health);
          3. else (waves, camps) -> QE Molten Fissure (连皴山): lava on the target's spot, q_e_dmg + q_e_ratio% AP, then
             a field (q_e_r) burning q_e_dps + q_e_dps_r% AP every q_e_per ticks for q_e_t and slowing q_e_slow%.
  skill2  Subject: Torment (主题：悚, cooldown e_cd): a `Targeting` cast on `EnemyChampion` (e_range):
          1. a champion within e_near of him -> EQ Grim Visage (阴沉变意): e_dmg + e_ratio% AP and Fear e_fear ticks
             (peel: the one on top of him runs);
          2. else, in turn (pointer flag `e_nx`): EW Gaze of the Abyss (滞涩幽瞳) - the eye opens e_w_setup ticks, then
             e_dmg + e_ratio% AP and a e_root-tick root; EE Crushing Maw (双钩血喉) - the jaws snap e_e_at ticks later,
             e_dmg + e_ratio% AP, held e_hold ticks (`Bind`) and slowed e_slow% for e_slow_t (League pulls to the maw's
             middle; a pull to the target's own spot is a hold here).
  ult     Spiraling Despair (焚心绚华绘): a `Targeting` cast on `EnemyChampion` (r_range). The paint flies straight
          (r_speed, r_len, width r_w) and stops on the first champion: there the canvas spreads (r_r) for r_t ticks,
          burning r_dps + r_dps_r% AP every r_per ticks and slowing r_slow%, then it bursts: r_dmg + r_ratio% AP
          (League: 200-450 + 80% AP burst, a stacking slow, 3 s; it bursts early when the centre dies - nothing reads that).
  combos  悚 -> 灾 (控住 -> 攒聚雷): every Torment hit on a champion (fear, root, hold) strikes Severing Bolt on it
          eq_gap ticks later if Disaster is ready (its cooldown flag taken), with the immobile bonus - the AI casts
          Torment and Disaster on their own timers, so the chain fires here instead.
          R -> 灾 (焚心绚华绘 -> 没骨火): the canvas's first champion gets Devastating Fire r_q_gap ticks later if Disaster is
          ready.
          Two damaging abilities on champions -> 落款 bursts (the passive), so every combo above also signs and bursts.
Action tags (the art): idle run attack hit dead; skill (QQ fire), skill_w (QW bolt), skill_e (QE lava); skill2 (EW eye),
skill2_q (EQ visage), skill2_e (EE maw); ult. The Disaster / Torment actions are 3-tick `idle` casts that play their
pick's tag (league_neeko's Q way).
Timings: drafts until the frames exist (a frame's start in ticks = ms x 0.06): a_rel, q_rel, e_rel, r_rel.
Numbers: League 16.20 (CommunityDragon hwei.bin) read into the Magician mid range (league_neeko); balanced on the
classic-SDK simulations (kd.py --lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage,
C:/t/hw_sim, 2026-10-22): the draft +1.90 on seeds 1-8 (league_neeko +1.50 on the same games); every pick fires in
traced games (seeds 3 / 5 / 7: Severing Bolt 4-9 a game, Devastating Fire 5-15, Molten Fissure 18-31, the eye and the maw
9-14 each, the signature bursting 21-38 times), Grim Visage once in three games at e_near 30000 -> 38000; that is P,
+1.44 on seeds 1-16.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_hwei.data_champion")
ID = "league_hwei"
FX = "asset/league/effects/league_hwei_fx"
BIG = "asset/league/effects/league_hwei_big"

# League's Hwei (16.20, CommunityDragon hwei.bin): 580 +109 hp, 54 AD, 21 +4.7 armour, 30 mr, 330 move, 550 range.
# Passive: 4 s to sign twice; the mark bursts. QQ 800 range 50-110 + % max health (3-5%, cap 250 vs monsters); QW 1900
# range, 1 s delay, 60-110, x2-2.75 on the immobile / isolated; QE 1200 range, 20-50 + 2.5 s field 20-50 dps, 35% slow;
# cd 10-9. WQ 30-35% haste, WW shield 100-180 + 60% AP (allies 85%), WE on-hit 20-40; cd 18-17.5. EQ 1100 range 70-150,
# fear 1-1.25 s; EW 900 range, 0.65 s setup, root 1.2-1.6 s; EE 800 range, 0.6 s delay, pull + 40-55% slow; cd 13-12.5.
# R 1300 range, 3 s field 10-30 dps, 10% slow a stack, burst 200-450; cd 120-100.
P = {
    # stats (Magician mid: league_neeko 960 +95 hp, 70 +6 attack, 40 +20 ap, 21 +7 def)
    "hp": 940, "hp_g": 94, "atk": 70, "atk_g": 6, "apw": 40, "apw_g": 20, "def": 20, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 9,
    "atk_range": 55000, "atk_dur": 27, "atk_cd": 92, "a_rel": 10, "a_speed": 4500, "a_y": -4000,
    # passive: the signature; Serenity folded in
    "sig_t": 240, "sig_at": 30, "sig_dmg": 45, "sig_ratio": 35,
    "w_sh": 60, "w_sh_r": 35, "w_ally": 85, "w_r": 35000, "w_sh_t": 120, "w_ms": 25, "w_ms_t": 60,
    # skill: Subject: Disaster
    "q_cd": 480, "q_range": 80000, "q_dur": 30, "q_rel": 12,
    "q_w_at": 45, "q_w_dmg": 70, "q_w_ratio": 45, "q_w_cc": 90, "q_w_cc_r": 60,
    "q_q_speed": 3000, "q_q_dmg": 90, "q_q_ratio": 60, "q_q_hp": 3,
    "q_e_travel": 15, "q_e_r": 20000, "q_e_dmg": 35, "q_e_ratio": 25, "q_e_t": 150, "q_e_per": 30, "q_e_dps": 15,
    "q_e_dps_r": 10, "q_e_slow": 35,
    # skill2: Subject: Torment
    "e_cd": 720, "e_range": 85000, "e_dur": 30, "e_rel": 12, "e_near": 38000, "e_dmg": 80, "e_ratio": 50,
    "e_speed": 4000, "e_fear": 60, "e_w_setup": 39, "e_root": 80, "e_e_at": 30, "e_hold": 30, "e_slow": 45,
    "e_slow_t": 90, "eq_gap": 6,
    # ult: Spiraling Despair
    "r_cd": 2100, "r_range": 80000, "r_dur": 36, "r_rel": 14, "r_speed": 3000, "r_len": 100000, "r_w": 6000,
    "r_r": 25000, "r_t": 180, "r_per": 20, "r_dps": 12, "r_dps_r": 8, "r_slow": 25, "r_dmg": 220, "r_ratio": 100,
    "r_q_gap": 10, "r_y": -4000,
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


def maxhp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): league_vex's 1-tick flag."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def decoy(dmg, ratio, kind=attack):
    """The damage the game's AI reads for this action (league_zoe's decoy): a flag he never has while it reads."""
    return combine(flag("x", 1), sw("x", combine(*rm("x")), kind(dmg, ratio)), *rm("x"))


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, effects, end, y=0):
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": y,
            "penetrate": False, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end)}


def lob(name, travel, end):
    """A 1-radius lob onto the target's spot (league_anivia's): its end_effects run on that spot."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, first, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": first, "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: the signature (on a champion only)
    burst = delayed(p["sig_at"], ap(p["sig_dmg"], p["sig_ratio"]), view("p_burst"), tsfx("p_burst"))
    sign = sw("sig_l", NONE, combine(flag("sig_l", 2),
                                     sw("sig", combine(*rm("sig"), burst), combine(flag("sig", p["sig_t"]),
                                                                                   buff("p_mark", p["sig_t"])))))

    # ------------------------------------------------------------------ attack: a flick of ink
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(decoy(0, 100), delayed(p["a_rel"] - 1, alive(
                          sfx("a"), homing("a_ink", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")],
                                           p["a_speed"], p["a_y"])))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Subject: Disaster
    def bolt(cc):
        """Severing Bolt on the unit the effects run on (cc: the immobile bonus)."""
        return [view("q_w_tell"), delayed(p["q_w_at"], ap(p["q_w_dmg"], p["q_w_ratio"]),
                                          ap(p["q_w_cc"], p["q_w_cc_r"]) if cc else None, view("q_w_hit"),
                                          tsfx("q_w_hit"), sign)]

    def fire():
        return homing("q_q_ball", "EnemyChampion", [ap(p["q_q_dmg"], p["q_q_ratio"]), maxhp(p["q_q_hp"]), view("q_q_hit"),
                                                     tsfx("q_q_hit"), sign], p["q_q_speed"], p["a_y"])

    lava = lob("q_e_lob", p["q_e_travel"], [
        view("q_e_lava"), sfx("q_e_hit"),
        zone("q_e_hit", p["q_e_r"], [ap(p["q_e_dmg"], p["q_e_ratio"]), tsfx("q_e_burn")]),
        field("q_e_field", p["q_e_r"], p["q_e_t"], p["q_e_per"], p["q_e_per"],
              [ap(p["q_e_dps"], p["q_e_dps_r"]), buff("q_e_slow", p["q_e_per"] + 5, move_speed_mult=-p["q_e_slow"])])])
    haste = on_me(refresh("w_haste", p["w_ms_t"], move_speed_mult=p["w_ms"]))
    picks = combine(
        *rm("q_go"),
        pick(p["q_range"], "EnemyChampionInCC", flag("q_go", 1), anim("skill_w", p["q_dur"]), sfx("q_w"), *bolt(True)),
        sw("q_go", NONE, pick(p["q_range"], "EnemyChampion", flag("q_go", 1), anim("skill", p["q_dur"]), sfx("q_q"),
                              delayed(p["q_rel"] - 1, alive(fire())))),
        sw("q_go", NONE, combine(anim("skill_e", p["q_dur"]), sfx("q_e"), delayed(p["q_rel"] - 1, alive(lava)))),
        *rm("q_go"))
    skill = action("idle", 3, p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(decoy(p["q_q_dmg"], p["q_q_ratio"], ap),
                           sw("q_cd", NONE, combine(refresh("q_cd", p["q_cd"]), voice("vo_q", p), haste, picks))),
                   key="skill")

    # ------------------------------------------------------------------ skill2: Subject: Torment
    def follow():
        """悚 -> 灾: Severing Bolt on this champion if Disaster is ready."""
        return delayed(p["eq_gap"], sw("q_cd", NONE, combine(refresh("q_cd", p["q_cd"]), sfx("q_w"), *bolt(True))))

    hit = [ap(p["e_dmg"], p["e_ratio"]), tsfx("e_hit"), sign]
    visage = homing("e_q_face", "EnemyChampion", [*hit, {"type": "Fear", "tick": p["e_fear"]}, view("e_q_hit"),
                                                  follow()], p["e_speed"], p["a_y"])
    eye = homing("e_w_eye", "EnemyChampion", [view("e_w_open"), delayed(p["e_w_setup"], *hit,
                                                                         {"type": "Bind", "duration": p["e_root"]},
                                                                         buff("e_bound", p["e_root"]), view("e_w_hit"),
                                                                         follow())], 20000)
    maw = homing("e_e_maw", "EnemyChampion", [view("e_e_open"), delayed(p["e_e_at"], *hit,
                                                                        {"type": "Bind", "duration": p["e_hold"]},
                                                                        buff("e_slow", p["e_slow_t"],
                                                                             move_speed_mult=-p["e_slow"]),
                                                                        view("e_e_hit"), follow())], 20000)
    shield_ = combine(on_me(shield(p["w_sh"], p["w_sh_r"], p["w_sh_t"]), view("w_pool")),
                      around(p["w_r"], "AllyNotSelf", [shield(p["w_sh"] * p["w_ally"] // 100,
                                                              p["w_sh_r"] * p["w_ally"] // 100, p["w_sh_t"]),
                                                       view("w_shield")]))
    torment = combine(
        *rm("e_go"),
        pick(p["e_near"], "EnemyChampion", flag("e_go", 1), anim("skill2_q", p["e_dur"]), sfx("e_q"),
             delayed(p["e_rel"] - 1, alive(visage))),
        sw("e_go", NONE, sw("e_nx",
                            combine(*rm("e_nx"), anim("skill2_e", p["e_dur"]), sfx("e_e"),
                                    delayed(p["e_rel"] - 1, alive(maw))),
                            combine(flag("e_nx", None), anim("skill2", p["e_dur"]), sfx("e_w"),
                                    delayed(p["e_rel"] - 1, alive(eye))))),
        *rm("e_go"))
    skill2 = action("idle", 3, p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(decoy(p["e_dmg"], p["e_ratio"], ap), voice("vo_e", p), sfx("w_ww"), shield_, torment),
                    key="skill2")

    # ------------------------------------------------------------------ ult: Spiraling Despair
    canvas = [view("r_canvas"), sfx("r_canvas"),
              field("r_field", p["r_r"], p["r_t"], p["r_per"], p["r_per"],
                    [ap(p["r_dps"], p["r_dps_r"]), buff("r_slow", p["r_per"] + 5, move_speed_mult=-p["r_slow"])]),
              field("r_blast", p["r_r"], p["r_t"] + 2, p["r_t"] + 10, p["r_t"],
                    [ap(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]),
              delayed(p["r_t"] - 1, view("r_burst"), sfx("r_burst"))]
    first = [sign, delayed(p["r_q_gap"], sw("q_cd", NONE, combine(refresh("q_cd", p["q_cd"]), sfx("q_q"),
                                                                  homing("q_q_ball2", "EnemyChampion",
                                                                         [ap(p["q_q_dmg"], p["q_q_ratio"]),
                                                                          maxhp(p["q_q_hp"]), view("q_q_hit"),
                                                                          tsfx("q_q_hit"), sign],
                                                                         p["q_q_speed"], p["a_y"]))))]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(decoy(p["r_dmg"], p["r_ratio"], ap), sfx("r"), voice("vo_r", p),
                         delayed(p["r_rel"] - 1, alive(line("r_paint", p["r_speed"], p["r_len"], p["r_w"],
                                                            "EnemyChampion", first, canvas, p["r_y"])))))

    # ------------------------------------------------------------------ views (the step-3 effects pack)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    Pj = lambda name, tag=None, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                           "repeat": True, "z": 2}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [Pj("a_ink"), Pj("q_q_ball"), Pj("q_q_ball2", "q_q_ball"), Pj("e_q_face"), Pj("r_paint")]
    views_e = [E("a_hit"), E("p_burst", BIG, 3), E("q_w_tell"), E("q_w_hit", BIG, 3), E("q_q_hit"),
               E("q_e_lava", BIG, -1, False), E("e_q_hit"), E("e_w_open"), E("e_w_hit"), E("e_e_open"), E("e_e_hit"),
               E("w_pool", BIG, -1), E("w_shield"), E("r_canvas", BIG, -1, False), E("r_burst", BIG, 3, False),
               E("r_hit")]
    views_b = [B_("p_mark", FX, -1), B_("e_bound", FX, 3), B_("w_haste", FX, -1), B_("q_e_slow", FX, -1),
               B_("e_slow", FX, -1), B_("r_slow", FX, -1)]
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range", "CC"],
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
