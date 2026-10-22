"""Build league_drmundo.data_champion (top, Melee tank) from the parameters P.

    python tools/kit/build_drmundo.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-16: top lane, League's layout, a native add-on addons/league_drmundo; 「方案可以，全按推荐做」):
League's Mundo reads health everywhere (current, missing, bonus); the data reads none of it, so the main pack stands in
with fixed numbers, maximum-health shares and his own hit count, and the add-on (native=1) does the real thing.
  passive Goes Where He Pleases (走自己想去的地方): health regeneration (stat hp_regen, its growth) and, with p_cd gone,
          the first crowd control on him is shaken off: every life starts a 3-tick self check (an AddCasted on him,
          `RandomTarget {range 1, AllyChampionInCC}` finds only him while he is stunned, rooted, airborne, pulled,
          feared or charmed) that gives him p_imm ticks of `cc_immune`, lays p_cd and drops a chem-tank where he
          stands (a hidden lob, the canister lands p_fly ticks later): a zone (p_can_t ticks, armed after p_arm) that he
          picks up by walking over it - p_heal + p_heal_ad% AD health and the passive's cooldown cut to p_cut% - and an
          enemy champion stepping on it breaks it. League blocks the control and costs 7% current health; the data
          can only end it (at most 3 ticks late) and cannot take a share of current health, so it costs nothing.
          With native=1 the add-on blocks it on the tick it lands, takes 7% of current health and walks him to the tank.
  attack  A cleaver chop (atk_st). E Blunt Force Trauma (钝器创伤) is folded in: League's passive AD from bonus health is
          in his AD growth; with e_cd gone his next attack is the bat swing (attack_e): e_dmg + e_hp% of his maximum health more (2026-10-22, the user: 「蒙多加成怎么是攻击力不是生命值」 - the damage
          ratios read his maximum health, `hp_ratio`; the heals stay on AD, no heal effect has a health part), and a
          minion or monster it kills is flung (League: the corpse damages what it passes): the kill check of
          league_jinx (a caster flag the target's 1-tick casted clears while it lives) read by a hidden lob onto its
          spot - a dead target -> the corpse flies on away from him (e_fling_l), e_fling + e_fling_hp% of his maximum health to every
          enemy unit on its way. With native=1 the swing
          adds up to e_miss% more by his real missing health, and his AD grows by e_bonus per mille of his bonus health
          (items: his maximum health above the level's own).
  skill   Q Infected Bonesaw (感染之锯): a `Targeting` cast on `EnemyWithoutTower` (q_range, waves and camps too); on q_at
          the saw leaves for where the target stood 8 ticks before (dodgeable, league_tahmkench Q's lock) and stops on
          the first unit: q_dmg + q_ap% AP magic, slow q_slow% for q_slow_t, he heals q_heal; on a champion (a twin
          on the same line) q_thp% of its maximum health more as true damage (League: 20% of current health, magic) and
          q_heal_c more health. With native=1 the add-on deals q_pct% of the champion's real current health (at
          least q_dmg) instead of q_thp.
  skill2  W Heart Zapper (心脏电击器): cast with an enemy unit within w_rad: w_n pulses w_per ticks apart zap every enemy
          unit round him (w_tick + w_hp% of his maximum health, magic); every g_per ticks a check that finds his 1-point hit sensor broken
          (any damage since the last check, league_sett's sensor) queues a grey-health heal of w_g for the end; at the end the
          final zap (w_end + w_end_hp% of his maximum health, magic) - a champion in it pays every queued heal in full, only minions or monsters
          half, nothing in it nothing. With native=1 the add-on stores w_store% of the real damage taken and heals it.
  ult     R Maximum Dosage (极限剂量), cast at the right moment (the user's rule 「看好时机」): the slot arms it (r_arm ticks);
          each of his actions while armed fires it when his damage count reached h{r_need} and an enemy champion stands
          within r_n: a shield of h_sens points with a WithShield flag, read on his attacks, Q and W - broken, he
          took h_sens damage since it was armed: the read takes those points from him as true damage (the shield
          gives nothing away), climbs h1 -> h2 -> h3 (h_hold ticks each) and arms it again - 3 x h_sens taken with
          no gap of h_hold ticks, the danger the data can see. It heals r_heal + r_heal_ad% AD at once and for r_t ticks gives r_hp maximum
          health, r_regen health a second and r_ms% move speed. An unused window caps the cooldown at 60 ticks.
          With native=1 the add-on fires it by his real health (below r_low% or r_burst% lost within a second) and
          (r_low 60 / r_burst 15 since 2026-10-19, the user: 「蒙多开大次数也挺少的」 - at 40 / 25 most games had no R at
          all: held at 68-85% while he took a fight, or cast as he died) and
          heals r_miss% of his missing health.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_drmundo.data_champion")
ID = "league_drmundo"
FX = "asset/league/effects/league_drmundo_fx"
BIG = "asset/league/effects/league_drmundo_big"

# Balance (classic SDK, top lane against fighter / executioner / lancer / pole_warrior / knight / berserker, 3 lineups,
# both sides, 12 seeds): the first draft -2.94 (damage half of league_garen's); d4c (atk 96 + 20, Q 140 + 9%, E 80 +
# 60%, W 18 / 90) -0.21 but R at full health (the 1-point hit sensor); the damage sensor (h_sens 150, r_need 3,
# h_hold 300: ~2 R a game at ~62% health) -0.73, with hp 1350 / def 38 -0.22 (league_garen -1.15, league_sion +0.78).
# 2026-10-22 (「蒙多加成怎么是攻击力不是生命值」): the damage ratios on his maximum health (`hp_ratio`) - E 80 + 60% AD ->
# 80 + 8%, the flung corpse 40 + 60% AD -> 40 + 6%, W 18 + 6% AD -> 10 + 1% a zap, the final zap 90 + 30% AD -> 90 + 4%;
# seeds 1-8: before -0.12 (+-0.41), 7% / 3% -0.38, the kept 8% / 4% +0.37 (+-0.36), damage dealt 9450 -> 9637.
# Timings from the frames (tools/art/import_drmundo_strips.py, league/champions/league_drmundo#anim.fanim): the chop
# 400 ms, the saw down on frame 3 (tick 10-11); Blunt Force Trauma 433 ms, the bag out on frame 3 (tick 9-10); the
# Bonesaw 433 ms, the throw on frame 4 (tick 11); Heart Zapper on 233 ms, its discharge 200 ms; Maximum Dosage 500 ms.
P = {
    # stats (League's Dr. Mundo: 640 +103 hp, 61 AD +2.5 (+ 2.5% bonus hp from E), 32 armour, 29 mr, 345 move, 125
    # range, 0.67 attacks a second; passive regen 0.4-2.5% max hp / 5 s ~ 1-4 hp a second at 1300-2500 hp)
    "hp": 1350, "hp_g": 125, "atk": 96, "atk_g": 20, "def": 38, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 1000, "ms_g": 10, "regen": 6, "regen_g": 1,
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 68, "atk_st": 11,
    # passive Goes Where He Pleases (League: cd 60-30 s, 7% current hp, the tank heals 4% max hp and cuts the cd 40%)
    "p_cd": 2400, "p_imm": 90, "p_fly": 20, "p_arm": 60, "p_can_t": 600, "p_link": 120, "p_can_r": 9000,
    "p_heal": 60, "p_heal_ad": 60, "p_cut": 60,
    # E Blunt Force Trauma folded into the attack (League: 5-45 + up to 100% more by missing hp, cd 9-5 s; a killed
    # unit flung, its damage to units hit)
    "e_cd": 420, "e_dur": 26, "e_st": 10, "e_dmg": 80, "e_hp": 8, "e_fling": 40, "e_fling_hp": 6, "e_fling_r": 5000, "e_fling_v": 4000, "e_fling_l": 70000,
    "e_miss": 100, "e_bonus": 25,
    # Q Infected Bonesaw (League: 1050 range, speed 2000, 20% current hp magic, min 80-280, max 350-550 to monsters,
    # slow 40% 2 s, cost 50 hp refunded 50% / 100% on a champion; cd 4 s)
    "q_cd": 260, "q_range": 70000, "q_dur": 26, "q_at": 11, "q_speed": 6500, "q_w": 3200, "q_dmg": 140, "q_ap": 0,
    "q_thp": 9, "q_pct": 20, "q_slow": 40, "q_slow_t": 120, "q_heal": 20, "q_heal_c": 40,
    # W Heart Zapper (League: 4 s, 20-80 + 7% bonus hp... a second round him, 75% of damage taken stored as grey
    # health, healed 100% if the end zap hits a champion, else 50%; cd 17-13 s)
    "w_cd": 900, "w_rad": 22000, "w_anim": 14, "w_n": 12, "w_per": 20, "g_per": 30, "w_tick": 10, "w_hp": 1,
    "w_end": 90, "w_end_hp": 4, "w_g": 30, "w_end_anim": 12, "w_store": 75,
    # the damage count R reads (a shield of h_sens read on his attack, Q and W, its points paid back)
    "h_sens": 150, "h_hold": 300, "r_need": 3,
    # R Maximum Dosage (League: 20-30% missing hp at once, 20-40% max hp over 10 s, 15-35% move speed; cd 110-80 s)
    "r_cd": 4800, "r_range": 50000, "r_arm": 900, "r_anim": 30, "r_n": 40000, "r_t": 600,
    "r_heal": 200, "r_heal_ad": 100, "r_hp": 200, "r_regen": 40, "r_ms": 25, "r_low": 60, "r_burst": 15, "r_miss": 25,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_drmundo: real current / missing / bonus health
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


def attack(dmg, ratio, hp=0):
    """dmg + ratio% of his AD + hp% of his maximum health, physical."""
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def magic(dmg, ratio, hp=0):
    """dmg + ratio% AP + hp% of his maximum health as magic damage."""
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False,
            "attack_effect_type": "Target"}


def maxhp(pct):
    """pct% of the target's maximum health as true damage (no magic effect has a target-health part)."""
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct}


def heal(amount, ad=0):
    return {"type": "Heal", "amount": amount, "attack_ratio": ad, "ap_ratio": 0, "heal_type": "Caster"}


def shield(amount, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": 0, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def lob(name, travel, rng, target, end):
    """A ParabolicProjectile onto the target's spot as it is now: its end_effects start there."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": rng,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, target, effects):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def pzone(name, radius, tick, period, first, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": first, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def casted(duration, period, effects):
    return {"type": "AddCasted", "casted_type": "Heal", "duration": duration, "period": period,
            "effects": list(effects)}


def native(ref):
    return {"type": "Native", "effect_ref": f"league_drmundo:{ref}"}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_target": ctarget, "casting_type": ctype, "attack_type": atype, "effect": effect}


LIFE = 36000    # a life's self checks run this long (re-armed by the next action after that)


def build(p):
    nat = bool(p["native"])

    # ------------------------------------------------------------------ the hit sensor (R reads h1..h3)
    # an h_sens-point shield and a WithShield flag: the flag gone = he took h_sens damage since it was armed; the read
    # takes those h_sens points from him as true damage (the shield gave none away) and climbs the ladder
    arm_sensor = combine(on_me(shield(p["h_sens"], LIFE)), flag("hs", "shield"))
    h = p["h_hold"]
    climb = sw("h2", combine(refresh("h3", h), refresh("h2", h), refresh("h1", h)),
               sw("h1", combine(refresh("h2", h), refresh("h1", h)), refresh("h1", h)))
    repay = on_me({"type": "FixedAttack", "damage": p["h_sens"], "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": 0})
    sense = sw("hs", NONE, combine(repay, climb, arm_sensor))
    if nat:     # the add-on reads his real health: no sensor
        arm_sensor = sense = None

    # ------------------------------------------------------------------ passive: shake off the first crowd control
    can_pick = sw("can", combine(*rm("can", "p_cd"), heal(p["p_heal"], p["p_heal_ad"]), view("p_pick"), sfx("p_pick"),
                                 flag("p_cd", p["p_cd"] * p["p_cut"] // 100)))
    can_break = sw("can", combine(*rm("can"), view("p_break"), sfx("p_break")))
    # the tank lies in links of p_link ticks, the next one laid on the same spot while `can` holds: a zone cannot be
    # taken away, so a tank in one p_can_t-long zone stayed drawn after he picked it up or an enemy broke it
    # the tank's picture is a ground ViewEffect played by each link (a zone's own picture turns with it: on the red side
    # the tank stood on its head over the ground line)
    # FIX 2026-10-16: the links were chained through each zone's end_effects, which a RangePeriodProjectile never runs
    # (sim: one link a tank, gone 120 ticks after landing while `can` lasted 600 - the add-on's AI walked him to an empty
    # spot and he stood there). Now the lob's end_effects lay every link up front, each a Delayed of k * p_link.
    def link(first):
        return [pzone("p_tank_z", p["p_can_r"], p["p_link"], 6, first, "AllyOnlySelf", [can_pick]),
                pzone("p_tank_e", p["p_can_r"], p["p_link"], 6, first, "EnemyChampion", [can_break])]
    links = [delayed(k * p["p_link"], sw("can", combine(view("p_tank"), *link(0))))
             for k in range(1, p["p_can_t"] // p["p_link"])]
    canister = [refresh("can", p["p_can_t"]), view("p_land"), view("p_tank"), sfx("p_land"), *link(p["p_arm"]), *links]
    shake = combine(flag("p_cd", p["p_cd"]), flag("p_imm", p["p_imm"], cc_immune=True), cview("p_shake"), sfx("p_shake"),
                    voice("vo_p", p), lob("p_drop", p["p_fly"], 30000, "AllyOnlySelf", canister))
    checker = casted(LIFE, 3, [pick(1, "AllyChampionInCC", sw("p_cd", NONE, shake))])
    if nat:     # the add-on clears the control on the tick it lands, takes 7% of current health and lays p_drop_n:
        # the same 3-tick check drops the tank (the zones, the pickup and the cooldown cut stay data)
        checker = casted(LIFE, 3, [sw("p_drop_n", combine(*rm("p_drop_n"), shake))])
    life = sw("life", NONE, combine(flag("life", LIFE), arm_sensor, on_me(checker)))

    # ------------------------------------------------------------------ ult: R Maximum Dosage (armed, checked)
    dose = combine(*rm("r_armed"), flag("r_lock", 6), anim("ult", p["r_anim"]), cview("r_cast"), sfx("r"),
                   voice("vo_r", p), heal(p["r_heal"], p["r_heal_ad"]) if not nat else native("dose"),
                   refresh("r_on", p["r_t"], hp=p["r_hp"], hp_regen=p["r_regen"], move_speed_mult=p["r_ms"]))
    count = combine(*rm("r_e"), around(p["r_n"], "EnemyChampion", [flag("r_e", 3)]))
    r_check = sw("r_armed", sw("r_lock", NONE, sw(f"h{p['r_need']}", combine(count, delayed(1, sw("r_e", sw("r_armed", dose)))))))
    if nat:     # the add-on's AI hook fires the slot itself by his real health
        r_check = NONE
    pre = combine(life, sense, r_check)
    pre_light = combine(sense, r_check)          # W and R: the passive's setup (life) rides on the attack and Q

    # ------------------------------------------------------------------ attack (+ E Blunt Force Trauma)
    plain = combine(sfx("a_swing"),
                    delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit")))
    # the corpse flies on from where it fell, away from him (a line started in a lob's end_effects leaves from him
    # toward the landing spot), hitting every enemy unit on its way
    fling = [line("e_fling", p["e_fling_v"], p["e_fling_l"], p["e_fling_r"], "EnemyWithoutTower", True,
                  [attack(p["e_fling"], 0, p["e_fling_hp"]), view("e_fling_hit"), tsfx("e_fling_hit")]), sfx("e_fling")]
    # the kill check: e_k on him, a casted on the target from a tick later clears it while it lives (its first run is
    # at once: added with the blow it cleared the flag before the blow), a lob onto its spot reads it
    kill_check = lambda hit: [lob("e_corpse", 9, 60000, "EnemyWithoutTower", [sw("e_k", combine(*rm("e_k"), *fling))]),
                              flag("e_k", 12), *hit, delayed(1, casted(3, 1, rm("e_k")))]
    bonk = combine(flag("e_cd", p["e_cd"]), anim("attack_e", p["e_dur"]), sfx("e"), voice("vo_e", p),
                   delayed(p["e_st"] - 1, *kill_check([attack(p["e_dmg"], 100, p["e_hp"])]),
                           native("bonk") if nat else None, view("e_hit"), tsfx("e_hit")))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(pre, sw("e_cd", plain, bonk)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Infected Bonesaw
    on_champ = combine(maxhp(p["q_thp"]) if not nat else native("saw"),
                       on_me(heal(p["q_heal_c"]), cview("q_heal")), sfx("q_heal"))
    q_hits = [magic(p["q_dmg"], p["q_ap"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
              on_me(heal(p["q_heal"])), view("q_hit"), tsfx("q_hit")]
    rng = p["q_range"] + 10000
    saw = combine(line("q_saw", p["q_speed"], rng, p["q_w"], "EnemyWithoutTower", False, q_hits),
                  line("q_twin", p["q_speed"], rng, p["q_w"], "EnemyChampion", False, [on_champ]))
    aim = lob("q_aim", 8, rng, "EnemyWithoutTower", [saw])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(pre, sfx("q"), voice("vo_q", p), delayed(p["q_at"] - 9, aim)))

    # ------------------------------------------------------------------ skill2: W Heart Zapper
    # each pulse: zap round him; his W sensor broken since the last pulse -> a grey heal queued for the end
    w_end_t = p["w_n"] * p["w_per"]
    paid = lambda: sw("w_full", heal(p["w_g"]), sw("w_half", heal(p["w_g"] // 2)))
    w_arm = combine(on_me(shield(1, w_end_t + 10)), flag("ws", "shield"))

    def pulse(i):
        rem = w_end_t - i * p["g_per"] + 2
        return delayed(i * p["g_per"], sw("w_on", sw("ws", NONE, combine(w_arm, delayed(rem, paid())))))
    zaps = on_me(casted(w_end_t - 1, p["w_per"], [around(p["w_rad"], "EnemyWithoutTower",
                                                         [magic(p["w_tick"], 0, p["w_hp"]), view("w_zap")])]))
    greys = [] if nat else [pulse(i) for i in range(1, w_end_t // p["g_per"])]
    final = delayed(w_end_t, sw("w_on", combine(
        *rm("w_full", "w_half", "w_ch", "w_any"), anim("skill2_end", p["w_end_anim"]), cview("w_burst"), sfx("w_end"),
        around(p["w_rad"], "EnemyWithoutTower", [magic(p["w_end"], 0, p["w_end_hp"]), view("w_end_hit"),
                                                 flag("w_any", 4)]),
        around(p["w_rad"], "EnemyChampion", [flag("w_ch", 4)]),
        delayed(1, sw("w_ch", flag("w_full", 4), sw("w_any", flag("w_half", 4))),
                native("zap_end") if nat else None))))
    # the pulses and the end are queued on him (on_me): queued on the cast's target, a minion that died meanwhile
    # dropped the end's own 1-tick check and the full heal never came
    zap = combine(pre_light, refresh("w_on", w_end_t + 2), anim("skill2", p["w_anim"]), cview("w_start"), sfx("w"),
                  voice("vo_w", p), w_arm, native("zap") if nat else None,
                  zaps, on_me(*greys, final))
    skill2 = action("skill2", p["w_anim"], p["w_cd"], 1, p["w_rad"], "Targeting", "EnemyWithoutTower", zap)

    # ------------------------------------------------------------------ ult: arm (and check at once)
    retry = p["r_cd"] * 100 // 60 - 100      # cooltime x 100 / (100 + mult) = 60 ticks
    arm = combine(life, refresh("r_armed", p["r_arm"]), r_check,
                  delayed(p["r_arm"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                flag("r_retry", 3, ult_cooldown_mult=retry)))))
    if nat:     # the hook casts it when his real health calls for it
        ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(life, dose), key="ult")
    else:
        ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", arm, key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("q_saw"), P_("e_fling")]
    views_e = [E("a_hit"), E("e_hit"), E("e_fling_hit"), E("q_hit"), E("q_heal", FX, 3),
               E("w_start", BIG, 1), E("w_zap"), E("w_burst", BIG, 1), E("w_end_hit"), E("r_cast", BIG, 3),
               E("p_shake", FX, 3), E("p_land", FX, 0, False), E("p_tank", FX, 0, False), E("p_pick", FX, 3, False), E("p_break", FX, 2, False)]
    views_b = [B_("q_slow", FX, -1), B_("w_on", BIG, -1), B_("r_on", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "Heal"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": p["regen_g"], "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if nat:
        kit["passive"] = {"passive_ref": "league_drmundo:pleases",
                          "params": {k: p[k] for k in ("p_cd", "q_dmg", "q_pct", "e_dmg", "e_hp", "e_miss", "e_bonus",
                                                       "hp", "hp_g", "w_store", "r_low", "r_burst", "r_miss")}}
    return kit


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
