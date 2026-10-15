"""Build league_milio.data_champion (support, Util, ranged AP enchanter) from the parameters P.

    python tools/kit/build_milio.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-15: Q in skill, E + W in skill2, R the ult; the passive a buff on every ally his spells
touch; an add-on addons/league_milio will make the burn and R's timing exact later):
  passive Fired Up! (League: his abilities enchant the allies they touch - their next damaging hit burns for 20-100 over
          1.5 s - and Milio gains move speed): nothing in data runs on another unit's attacks, so every ally E, W or R
          touches gets `league_milio_fired` for p_t ticks (attack_mult and magic_power_mult p_atk / p_ap %,
          league_nami E's way; same-name buffs add up, so a second enchant inside p_t doubles it) and Milio himself
          `p_haste` (move_speed_mult p_ms for p_mt ticks, one instance).
  attack  a small fireball (homing, physical).
  skill   Q Ultra Mega Fire Kick: a `Direction` cast on `EnemyWithoutTower` (q_range: lanes and camps too). The ball (a
          non-penetrating LinearProjectile, the first enemy stops it) knocks that unit back (q_kb_speed x q_kb_t, straight
          away from Milio: League 140, minions 340) and q_fall ticks after the hit falls on the spot the knock-back left it
          on (a hidden lob, the falling ball its landing telegraph): q_dmg + q_ap% AP magic damage and q_slow% slower for
          q_slow_t ticks to every enemy within q_r. Aim (the user's pro combo, league_morgana Q's way): first an enemy
          champion within q_dive of an allied champion within q_ally_r of Milio (the one diving his carry: a hidden lob
          onto that ally looks round it), else any enemy champion within q_reach, else the cast's own way.
  skill2  E Warm Hugs (2 charges) + W Cozy Campfire: a `Targeting` cast on `EnemyChampion` (e_range: only in fights; a
          shield cast on an ally goes out on cooldown out of fights, champion-data section 3). The hug flies to an ally
          (League's E is instant; here a homing flame): first one within e_near of that enemy champion (the ally being
          hit: a hidden lob onto the enemy looks round him), else one within e_ally_r of Milio, else Milio himself. It
          shields e_sh + e_ap% AP for e_t ticks and adds e_ms% move speed for e_t. With W's own cooldown flag `w_cd` off
          the same hug lights Cozy Campfire on that ally: w_t ticks of a fire that follows him (a buff picture under his
          feet) and every w_p ticks heals every allied champion within w_r of him by w_h + w_hap% AP and adds w_rng attack
          range for w_p ticks (League: 70-150 + 15% AP over 6 s, +10-20% range).
  ult     R Breath of Life, armed like league_alistar R (a 3-tick `None` cast on `EnemyChampion` within r_arm_range arms
          `r_armed` for r_arm ticks; unused, ult_cooldown_mult refunds it). Every action and a pulse every 15 ticks fire
          it when (a) an allied champion within r_r is crowd-controlled (Milio too), (b) an enemy champion is within
          r_dive of Milio, or (c) r_need enemy champions stand within r_near of a random allied champion within r_r (a
          probe lob, league_lulu R; the pulses check (a) and (b) only). Data reads no health, so "allies low" is this
          danger instead (the add-on's job).
          The fire plays `ult` for R_ANIM ticks and R_REL ticks in heals every allied champion within r_r (him too)
          r_heal + r_hap% AP, gives `cc_immune` for r_imm ticks (League's cleanse) and toughness r_ten % for r_tt ticks
          (League: 65% tenacity 3 s), and Fired Up!.
          r_now 1 = the add-on copy: the slot fires Breath of Life on the cast itself (the add-on decides when).
Seen in 8 logged games of d9 (dbg=1, 2026-10-15), a game: 43 kicks - 21 aimed at a champion in reach (blocked by his
wave mostly), 1 at one diving an ally, 21 the cast's way - kicking 6 champions, 22 minions and 5 monsters; 32 landings,
0.41 champions caught each (28% of them caught one). 30 hugs - 4 to the ally beside the enemy champion, 20 to one near
Milio, 5 to himself (mid 7, bot 6, jungle 6, top 5); 10.5 campfires (114 heal-pulse hits, 40 on Milio). R armed 2.8
times, fired 1.4 times on 3.0 champions each. `cc_immune` did not end a stun already on the ally (1 case: still stunned
27 ticks after the heal) - League's cleanse is the add-on's job.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_milio.data_champion")
ID = "league_milio"
FX = "asset/league/effects/league_milio_fx"
BIG = "asset/league/effects/league_milio_fx_big"

# Release ticks, checked against the final frames (tools/art/rig_milio.py TIMING, 2026-10-15): the fireball leaves in
# attack frame 3 (ticks 10-16, the ball drawn at his palm), the kick in skill frame 4 (13-18, the ball at his foot), the
# hug in skill2 frame 3 (11-17, the flame leaving his raised palm), the heal in ult frame 4 (17-25, the arms thrown
# open). Heights from the same frames (a projectile starts 5000 - y_offset above the pivot, 1000 a game px): the palm
# 6 px up (a_y -1000), the kicking foot 12 (q_y -7000), the raised palm 23 (e_y -18000).
ATK_DUR, ATK_REL = 26, 14
Q_DUR, Q_REL = 28, 17
E_DUR, E_REL = 24, 15
R_ANIM, R_REL = 36, 20

# Numbers = candidate d9 of the 10-min classic-SDK simulations (%LOCALAPPDATA%/Temp/mi_sim, sim/kd2.py --lane 4 against
# the five base supports priest / monk / bard / pythoness / spirit_caller, both sides, 3 lineups, 2026-10-15): +0.28 on
# seeds 1-12, -0.25 on seeds 13-24 (mean +0.02); the pack's supports on the same seeds: league_sona +0.31, league_braum
# +0.28, league_nami +0.04, league_seraphine 0.00, league_lulu -0.07, league_bard -0.30, league_soraka -1.07,
# league_janna -1.15, league_karma -1.71 (means of both batches). The draft d0 (hp 880, atk 75, Q 90 + 60% / 8 s,
# Fired Up! 10% / 4 s, R on two enemies round an ally) was -2.02; Fired Up! 20% -> -1.23, R on one enemy within 25000
# of an ally -> -0.97, both + 30% / 5 s -> -0.76, + hp 950 / atk 85 -> d9 (hp 920 / atk 80: -1.00 on seeds 13-24).
# q_thru 1 (aimed kicks past the wave, league_kennen Q) was no better: -2.01 against -1.23 for the same numbers.
P = {
    # stats (the pack's ranged supports: Janna/Lulu/Nami/Sona/Seraphine hp 880-950 +80-95, atk 75-80 +6, ap 30 +15,
    # def 20-24, mr 20-24, range 55000-60000, attack cooldown 90; League 525 range -> 53000 next to Bard's 52000)
    "hp": 950, "hp_g": 88, "atk": 85, "atk_g": 6, "ap": 30, "ap_g": 15, "def": 20, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 53000, "atk_dur": ATK_DUR, "atk_cd": 90, "atk_st": ATK_REL, "a_speed": 4500, "a_y": -1000,
    # passive: Fired Up!
    "p_t": 300, "p_atk": 30, "p_ap": 30, "p_ms": 15, "p_mt": 90,
    # skill: Q Ultra Mega Fire Kick (League: 1200 range, width 45, knock-back 140 / 340, fall 0.8 s r 250, 80-320 + AP,
    # slow 40-60% 1.5 s, cd 12-8 s)
    "q_cd": 420, "q_range": 75000, "q_dur": Q_DUR, "q_st": Q_REL, "q_speed": 6000, "q_reach": 85000, "q_rad": 5000,
    "q_y": -7000, "q_kb_speed": 2000, "q_kb_t": 7, "q_fall": 36, "q_r": 25000, "q_dmg": 120, "q_ap": 70, "q_slow": 40,
    "q_slow_t": 90, "q_ally_r": 60000, "q_dive": 30000, "q_thru": 0,
    # skill2: E Warm Hugs (League: 650, shield 45-165 + AP 2.5 s, +12-20% move speed, 2 charges) + W Cozy Campfire
    # (League: 650, 6 s, r 350, 70-150 + 15% AP, +10-20% range, cd 29-21 s)
    "e_cd": 1080, "e_uses": 2, "e_range": 90000, "e_dur": E_DUR, "e_st": E_REL, "e_near": 30000, "e_ally_r": 65000,
    "e_speed": 6000, "e_y": -18000, "e_sh": 80, "e_ap": 40, "e_t": 150, "e_ms": 16,
    "w_cd": 1500, "w_t": 360, "w_p": 60, "w_r": 35000, "w_h": 22, "w_hap": 4, "w_rng": 7000,
    # ult: R Breath of Life (League: r 800 round him, heal 150-350 + AP, cleanse, 65% tenacity 3 s; cd 160-130 s)
    "r_cd": 3600, "r_arm": 600, "r_arm_range": 75000, "r_r": 75000, "r_dive": 30000, "r_near": 25000, "r_need": 1,
    "r_anim": R_ANIM, "r_rel": R_REL, "r_heal": 150, "r_hap": 50, "r_imm": 60, "r_ten": 65, "r_tt": 180,
    "r_now": 0,
    # 1 = simulation probes: every branch plays its own sound (q_kick_dive / _champ / _cast, e_send_near / _ring / _self)
    "dbg": 0,
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


def flat(node):
    """The tree with every Combine that sits straight in a Combine's, a Delayed's or a RandomTarget's `effects`
    spliced into that list (the same effects in the same order, fewer nodes for the game's per-tick copy)."""
    if isinstance(node, list):
        return [flat(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {k: flat(v) for k, v in node.items()}
    if out.get("type") in ("Combine", "Delayed", "RandomTarget"):
        eff = []
        for x in out["effects"]:
            if isinstance(x, dict) and x.get("type") == "Combine":
                eff.extend(x["effects"])
            else:
                eff.append(x)
        out["effects"] = eff
    return out


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def dur(tick):
    return tick if isinstance(tick, (str, dict)) else {"Time": {"tick": tick}}


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur(tick), **fields},
            "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": dur(tick), **fields}}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


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


def magic(dmg, ap):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap, "hp_ratio": 0, "can_crit": False}


def heal_ally(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Ally"}


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a target's or a projectile's list (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def alive(*effects):
    """Only while he lives (a dead caster's Delayed effects run in the game; the search finds no dead caster)."""
    return pick(1, "AllyOnlySelf", *effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, target, *end, telegraph=None):
    """A hidden lob onto the unit in hand (league_annie R): it lands where he stood when it left, its end_effects act
    on that spot; `telegraph` plays there for the whole flight (range_effect_name)."""
    p = {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
         "shape": circle(1000), "applied_target": target, "applied_effects": [], "end_effects": list(end)}
    if telegraph:
        p["range_effect_name"] = n(telegraph)
    return p


def zone(name, radius, target, effects):
    """A one-tick area on a lob's landing spot."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur_, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None, uses=None):
    a = {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
         "duration": dur_, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
         "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}
    if uses:
        a["cooltime_use_count"] = uses
    return a


def build(p):
    def fired():
        """Fired Up! on the ally in hand, Milio's own haste."""
        return combine(buff("fired", p["p_t"], attack_mult=p["p_atk"], magic_power_mult=p["p_ap"]), tsfx("p_fired"),
                       on_me(refresh("p_haste", p["p_mt"], move_speed_mult=p["p_ms"])))

    # ------------------------------------------------------------------ ult: R Breath of Life (armed)
    breath = around(p["r_r"], "AllyChampion", [heal_ally(p["r_heal"], p["r_hap"]),
                                                buff("r_free", p["r_imm"], cc_immune=True),
                                                buff("r_ten", p["r_tt"], toughness=p["r_ten"]),
                                                buff("fired", p["p_t"], attack_mult=p["p_atk"], magic_power_mult=p["p_ap"]),
                                                view("r_hit"), tsfx("r_hit")])
    fire_r = combine(*rm("r_armed"), anim("ult", p["r_anim"]), sfx("r_cast"), sfx("vo_r"),
                     delayed(p["r_rel"], alive(breath, refresh("p_haste", p["p_mt"], move_speed_mult=p["p_ms"]))))
    # the probe (league_lulu R): a hidden lob onto a random allied champion in reach counts the enemy champions round
    # him (r_n1, r_n2 on Milio); two ticks later, on him, enough of them -> Breath of Life
    need = "r_n2" if p["r_need"] >= 2 else "r_n1"
    probe = pick(p["r_r"], "AllyNotSelf", combine(
        lob("r_probe", 1, "AllyChampion", zone("r_count", p["r_near"], "EnemyChampion",
                                                [sw("r_n1", flag("r_n2", 4), flag("r_n1", 4))])),
        delayed(3, sw("r_armed", sw(need, fire_r)))))

    def r_test(with_probe):
        return sw("r_armed", combine(
            *rm("r_go", "r_n1", "r_n2"), pick(p["r_r"], "AllyChampionInCC", flag("r_go", 1)),
            pick(p["r_dive"], "EnemyChampion", flag("r_go", 1)), sw("r_go", fire_r, probe if with_probe else NONE)))
    # every action runs the whole check; the pulses on the armed slot (crowd control on him stops his actions) only
    # (a) and (b) - the probe's lobs stay with his actions (the tree stays small)
    r_check = NONE if p["r_now"] else r_test(True)

    # ------------------------------------------------------------------ attack: the fireball
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy", flat(combine(
        r_check, sfx("a_cast"),
        homing("a_ball", p["a_speed"], p["a_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]))),
        atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Ultra Mega Fire Kick
    land = zone("q_land", p["q_r"], "EnemyWithoutTower",
                [magic(p["q_dmg"], p["q_ap"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                 view("q_burn")])
    ball_hit = [{"type": "Knockback", "speed": p["q_kb_speed"], "tick": p["q_kb_t"]}, view("q_hit"), tsfx("q_hit"),
                delayed(p["q_kb_t"], lob("q_drop", p["q_fall"] - p["q_kb_t"], "EnemyWithoutTower",
                                         view("q_land"), sfx("q_land"), land, telegraph="q_fall"))]

    def kick(tag):
        # q_thru 1: a kick aimed at a champion flies past minions and monsters to the first champion on its line
        # (league_kennen Q's aimed throw); 0: the first enemy of any kind stops it, as in League
        aimed = p["q_thru"] and tag != "cast"
        return combine(flag("q_aim", 3), sfx("q_kick"), *([sfx("q_kick_" + tag)] if p["dbg"] else []),
                       line("q_ball", p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"],
                            "EnemyChampion" if aimed else "EnemyWithoutTower", False, ball_hit))
    # first the champion diving his carry (round an ally near him), then any champion in reach, else the cast's way
    dive = pick(p["q_ally_r"], "AllyNotSelf", lob("q_look", 1, "AllyChampion",
                                                  pick(p["q_dive"], "EnemyChampion", sw("q_aim", NONE, kick("dive")), fp=True)))
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"] - 2, p["q_range"], "Direction", "EnemyWithoutTower", flat(combine(
        r_check, *rm("q_aim"), sfx("vo_q"), dive,
        delayed(2, sw("q_aim", NONE, pick(p["q_reach"], "EnemyChampion", kick("champ"))),
                sw("q_aim", NONE, kick("cast"))))))

    # ------------------------------------------------------------------ skill2: E Warm Hugs + W Cozy Campfire
    campfire = combine(
        flag("w_cd", p["w_cd"]), tsfx("w_fire"), buff("w_fire", p["w_t"]),
        casted(p["w_t"], p["w_p"], lob("w_spot", 1, "AllyChampion", zone(
            "w_heal", p["w_r"], "AllyChampion",
            [heal_ally(p["w_h"], p["w_hap"]), buff("w_range", p["w_p"], range=p["w_rng"]), view("w_heal")])),
            tsfx("w_pulse")))
    hug = [shield(p["e_sh"], p["e_ap"], p["e_t"]), buff("e_on", "WithShield"),
           buff("e_haste", p["e_t"], move_speed_mult=p["e_ms"]), view("e_hug"), tsfx("e_hug"), fired(),
           sw("w_cd", NONE, campfire)]

    def send(tag):
        return combine(flag("e_lock", 3), *([sfx("e_send_" + tag)] if p["dbg"] else []),
                       homing("e_ball", p["e_speed"], p["e_y"], "AllyChampion", hug))
    # first the ally beside the enemy champion (the one being hit), then one near Milio, else himself
    beside = lob("e_look", 1, "EnemyChampion", pick(p["e_near"], "AllyNotSelf", sw("e_lock", NONE, send("near")), fp=True))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], p["e_st"] - 2, p["e_range"], "Targeting", "EnemyChampion", flat(combine(
        r_check, *rm("e_lock"), sw("w_cd", sfx("vo_e"), sfx("vo_w")), beside,
        delayed(2, sw("e_lock", NONE, pick(p["e_ally_r"], "AllyNotSelf", send("ring"))),
                sw("e_lock", NONE, on_me(*hug, delayed(p["e_t"], *rm("e_on")),
                                         *([sfx("e_send_self")] if p["dbg"] else [])))))), uses=p["e_uses"])

    # ------------------------------------------------------------------ ult action: arms Breath of Life
    if p["r_now"]:
        ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion", flat(fire_r), key="ult")
    else:
        pulses = [delayed(t, alive(r_test(False))) for t in range(15, p["r_arm"], 15)]
        ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion", flat(combine(
            *rm("r_armed"), flag("r_armed", p["r_arm"]), r_check, *pulses,
            delayed(p["r_arm"], sw("r_armed", combine(*rm("r_armed"), flag("r_refund", 3, ult_cooldown_mult=4900)))))),
            key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                      "repeat": True, "z": z}
    # q_fall: the ball dropping onto the landing spot, upright (a ViewEffect is never turned), the lob's telegraph for
    # its whole flight; q_land the burst there; w_fire the campfire riding under the ally (a buff picture, z -1)
    views_p = [P_("a_ball"), P_("q_ball"), P_("e_ball")]
    views_e = [E("a_hit", FX, 2), E("q_hit", FX, 2), E("q_fall", BIG, 2, False), E("q_land", BIG, 1, False),
               E("q_burn", FX, 2), E("e_hug", FX, 2), E("w_heal", FX, 2), E("r_hit", FX, 2)]
    views_b = [P_("fired", FX, 2), P_("e_on", FX, 2), P_("w_fire", BIG, -1), P_("q_slow", FX, 1)]
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Range", "Heal", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["ap"], "hp": p["hp"], "defence": p["def"],
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
        p[k] = v if isinstance(p[k], str) else type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
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
