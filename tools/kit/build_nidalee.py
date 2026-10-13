"""Build league_nidalee.data_champion (jungle, AP assassin, human / cougar forms) from the parameters P.

    python tools/kit/build_nidalee.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-13: jungle AP assassin; the forms switch like League's R from level 1 - the switch is in
the attack slot, the ult slot (level 5) is a hunt pounce; human Q javelin / cougar Q Takedown as skill, human E + W and
cougar W + E sharing skill2; the passive in the main pack, the brush speed and the whole-body cougar in the add-on
addons/league_nidalee; the pros' combos):
  forms   Human (default, after every respawn): a ranged javelin attack (atk_range + h_add: the permanent caster buff
          `hu` - a range buff cannot be negative, so the bare reach is the cougar's and every action puts `hu` back
          when she has neither form). Cougar: the caster buff `cg` (permanent, melee reach), every action plays the cougar's own tags (c_*, league_kayn's
          way: the data plays them with `CasterAnimation`; idle, run, hit and death are the cougar only with the add-on).
          Aspect of the Cougar (美洲狮形态, the switch): each attack's first tick, with the switch ready (no `r_cd`),
          checks the rules; a switch replaces that attack with the transform (tf_dur ticks, no hit) and starts r_cd
          (League: 3 s). Human -> cougar: a champion was hunted lately (`hunt`), or an enemy within c_near while the
          javelin is on cooldown. Cougar -> human: Takedown spent (on cooldown, not armed) and, from level 3 (skill2
          opens; `SwitchByLevel3`), Pounce and Swipe both on cooldown; and the javelin (or Primal Surge) ready.
  passive Prowl (寻觅): a javelin or trap hit on an enemy champion hunts it - the `hunted` mark on it for p_t ticks and
          `hunt` on her (p_ms% move speed, League's haste toward the hunted). While `hunt` lasts Pounce reaches
          cw_far (League: 750 against 375), comes back in cw_cd_h ticks and Takedown deals cq_h% more. The data reads
          only her own buffs, so `hunt` stands for "a champion near is hunted". With native=1 (the add-on's copy) the
          passive league_nidalee:prowl adds the brush speed: brush_ms% in a bush and brush_t ticks after it,
          brush_near_ms% with a visible enemy champion within brush_near.
  attack  Human: the javelin thrown at the target (released on a_st). Cougar: the claw (c_atk_st); with Takedown armed
          the bite (c_skill): cq_dmg + cq_ad% AD physical and cq_mdmg + cq_ap% AP magic, x cq_h% while hunting.
  skill   Human: Javelin Toss (标枪投掷), a line (the first unit it meets, a skillshot) toward the target on `EnemyWithoutTower`
          (q_range, camps too): more damage the farther it flew (League: up to 3.25x) - flags laid at the release tell
          the hit how long it flew (league_xerath E): under q_t1 ticks q_dmg + q_ap% AP, under q_t2 x q_mid%, beyond
          x q_far%. Cougar: Takedown (推倒) armed for cq_t ticks (no animation; the next attack bites).
  skill2  Human: Primal Surge (野性奔腾) first - a heal on an allied champion within e_range (e_heal + e_ap% AP) and
          e_as% attack speed e_as_t ticks; while it cools down, Bushwhack (丛林伏击): a trap lobbed under an enemy
          champion in crowd control, else under any enemy within w_range: magic every w_per ticks while it lasts
          (w_dmg + w_ap% AP a pulse, w_life ticks), a champion hit is hunted. Cougar: Pounce (猛扑) first - a leap onto an
          enemy within cw_r (cw_far while hunting), cw_dmg + cw_ap% AP round the landing, then Swipe at once if it is
          ready (the pros' W -> E); else Swipe (挥击): ce_dmg + ce_ap% AP round her (ce_r).
  ult     Hunt pounce (猛扑猎杀, level 5): on `EnemyChampionRecentlyAttacked` within r_range: in human form she turns at
          once, every cougar cooldown is reset, she leaps onto the champion: r_dmg + r_ap% AP round the landing,
          Swipe at once and Takedown armed (the pros' R -> W -> E -> Q).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_nidalee.data_champion")
ID = "league_nidalee"
FX = "asset/league/effects/league_nidalee_fx"
BIG = "asset/league/effects/league_nidalee_big"

# Timings from the strips (assets/source/nidalee/frames/frames.json, Codex's step 2 after League's clips): attack 440 ms, the
# javelin leaves on frame 3 (150 ms, tick 9); Javelin Toss 550 ms, released on frame 4 (230 ms, tick 14); the spell 400 ms
# (tick 10); the turns 260 / 270 ms; the claw 340 ms, the hit on frame 3 (tick 8); Takedown's bite 430 ms (tick 9);
# Pounce 400 ms, off the ground on frame 2 (tick 4); Swipe 350 ms, the sweep on frame 3 (tick 9).
# Numbers = candidate d10 of the 10-min classic-SDK simulations (Temp/nd_sim/sim/kd.py, jungle against the base demon,
# circus blade, hunter, inquisitor and ninja, three lineups, both sides, 2026-10-13): +0.95 on seeds 1-24, +1.67 on 25-48
# (league_evelynn +1.38 / +1.30, league_lillia +1.33 / +1.77, league_khazix +0.97 / +1.16). The draft d0 was -3.99 / -4.24:
# its attack (62 +6 every 62 ticks) was half the base junglers' (120 +30 every 50); human only -2.1, cougar only -3.0.
P = {
    # stats (the pack's AP junglers: league_evelynn hp 880 +85, atk 75, mp 50 +20; league_ekko / league_diana);
    # League's Nidalee: 610 +109 hp, 58 AD, 32 armour, 30 mr, 335 move, 525 range (cougar 125)
    "hp": 980, "hp_g": 100, "atk": 110, "atk_g": 25, "mp": 50, "mp_g": 20, "def": 28, "def_g": 7, "mr": 24, "mr_g": 4,
    "ms": 1100, "ms_g": 12,
    "atk_range": 23000, "atk_dur": 26, "atk_cd": 52, "a_st": 9, "a_speed": 5000,
    # cougar form
    "h_add": 27000, "c_atk_dur": 20, "c_atk_st": 8, "c_near": 32000, "tf_dur": 16, "r_cd_t": 180,
    # passive Prowl (League: hunted 4 s, +30% move speed toward the hunted, pounce 750, takedown +40%)
    "p_t": 240, "p_ms": 20,
    # Q Javelin Toss (League: 1500 range, speed 1300, 50-170 + 50% AP, up to 3.25x at 1300 flown, cd 6 s)
    "q_cd": 360, "q_range": 85000, "q_dur": 33, "q_at": 14, "q_speed": 3000, "q_w": 2500,
    "q_dmg": 88, "q_ap": 80, "q_t1": 10, "q_t2": 19, "q_mid": 160, "q_far": 220,
    # Takedown (League: next attack -20..130 + 75% AD + 40% AP, more on low health, 1.4x on the hunted, cd 6 s)
    "cq_cd": 300, "cq_t": 240, "cq_dur": 26, "cq_st": 9, "cq_dmg": 40, "cq_ad": 50, "cq_mdmg": 52, "cq_ap": 62,
    "cq_h": 140,
    # skill2 slot
    "s2_cd": 60, "s2_range": 55000,
    # E Primal Surge (League: heal 25-175 + AP (up to 2x on the hurt), 20-80% attack speed 7 s, cd 12 s)
    "e_cd": 720, "e_range": 55000, "e_heal": 45, "e_ap": 45, "e_as": 40, "e_as_t": 420, "e_anim": 24, "e_at": 10,
    # W Bushwhack (League: 900 range, 40-200 + AP magic over 4 s (% current health), cd 14-9 s)
    "w_cd": 660, "w_range": 55000, "w_anim": 24, "w_at": 10, "w_fly": 16, "w_r": 7000, "w_life": 240, "w_per": 30,
    "w_dmg": 18, "w_ap": 16,
    # Pounce (League: 375 (750 hunted), 10-280 + 30% AP, radius 235, cd 6 s (1.5-3.5 s hunted))
    "cw_cd": 300, "cw_cd_h": 150, "cw_r": 25000, "cw_far": 50000, "cw_anim": 24, "cw_go": 4, "cw_at": 14,
    "cw_speed": 4500, "cw_rad": 13000, "cw_dmg": 70, "cw_ap": 48,
    # Swipe (League: 310 cone 90 deg, 10-370 + 55% AP, cd 6 s)
    "ce_cd": 300, "ce_r": 20000, "ce_anim": 21, "ce_at": 9, "ce_dmg": 98, "ce_ap": 80,
    # ult: the hunt pounce
    "r_cd": 1200, "r_range": 65000, "r_dmg": 160, "r_ap": 90,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # Prowl's brush speed in the add-on (League: +10% 2 s out of brush, +30% toward a visible champion within 1400)
    "brush_ms": 10, "brush_near_ms": 30, "brush_t": 120, "brush_near": 93000,
    # 1 = the copy for addons/league_nidalee: passive league_nidalee:prowl (the brush speed); the whole-body cougar and
    # the javelin's / hunt pounce's targets need nothing in the data
    "native": 0,
    # test builds for the balance runs: 1 = human only, 2 = cougar from the first attack on
    "lock": 0,
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


def magic(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": 0}


def lob(name, fly, target, end):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": fly, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive Prowl: the hunt
    hunted = [buff("hunted", p["p_t"]), on_me(refresh("hunt", p["p_t"], move_speed_mult=p["p_ms"]))]

    # ------------------------------------------------------------------ the forms
    # the human's reach is a caster buff (`hu`, +h_add): ranges cannot be cut, so the cougar is the bare melee reach and
    # every action first puts `hu` back when she has neither form (each life starts human)
    human = sw("cg", NONE, sw("hu", NONE, flag("hu", None, range=p["h_add"])))
    to_cougar = combine(*rm("hu"), flag("cg", None), refresh("r_cd", p["r_cd_t"]), anim("transform", p["tf_dur"]),
                        cview("tf_cougar"), sfx("tf_cougar"), voice("vo_cougar", p))
    to_human = combine(*rm("cg"), flag("hu", None, range=p["h_add"]), refresh("r_cd", p["r_cd_t"]), anim("c_transform", p["tf_dur"]), cview("tf_human"),
                       sfx("tf_human"), voice("vo_human", p))
    instant_cougar = sw("cg", NONE, combine(*rm("hu"), flag("cg", None), refresh("r_cd", p["r_cd_t"]),
                                            cview("tf_cougar"), sfx("tf_cougar")))

    # ------------------------------------------------------------------ attack
    human_hit = [attack(0, 100), view("a_hit"), tsfx("a_hit")]
    human_atk = combine(sfx("a_throw"),
                        delayed(p["a_st"] - 1, homing("a_spear", p["a_speed"], "Enemy", human_hit)))
    hunt_x = lambda d, r: sw("hunt", combine(attack(d * p["cq_h"] // 100, r * p["cq_h"] // 100)), attack(d, r))
    hunt_m = lambda d, r: sw("hunt", magic(d * p["cq_h"] // 100, r * p["cq_h"] // 100), magic(d, r))
    bite = combine(*rm("cq_on"), anim("c_skill", p["cq_dur"]), sfx("cq"), voice("vo_cq", p),
                   delayed(p["cq_st"] - 1, homing("cq_bite", 100000, "Enemy",
                                                  [hunt_x(p["cq_dmg"], 100 + p["cq_ad"]),
                                                   hunt_m(p["cq_mdmg"], p["cq_ap"]), view("cq_hit"),
                                                   tsfx("cq_hit")])))
    claw = combine(anim("c_attack", p["c_atk_dur"]), sfx("c_swing"),
                   delayed(p["c_atk_st"] - 1, homing("c_claw", 100000, "Enemy",
                                                     [attack(0, 100), view("c_hit"), tsfx("c_hit")])))
    cougar_atk = sw("cq_on", bite, claw)
    # the switch's rules (only with r_cd gone) lay `tf`; one branch then plays the transform or the attack
    tf = flag("tf", 2)
    near = combine(*rm("near"), pick(p["c_near"], "EnemyWithoutTower", flag("near", 2)))
    go = combine(near, sw("hunt", tf, sw("near", sw("hq_cd", tf))))
    # back to human once Takedown is spent (and, from level 3 when skill2 opens, Pounce and Swipe too) with the javelin
    # or (level 3+) Primal Surge ready
    lv3 = lambda low, high: {"type": "SwitchByLevel3", "effect_start": low, "effect_level3": high}
    back = sw("cq_on", NONE, sw("cq_cd", lv3(sw("hq_cd", NONE, tf),
                                             sw("cw_cd", sw("ce_cd", sw("hq_cd", sw("e_cd", NONE, tf), tf))))))
    rules = combine(*rm("tf"), sw("r_cd", NONE, sw("cg", back, go)))
    if p["lock"] == 1:      # test builds only: never switch (human) / switch once and stay (cougar)
        rules = NONE
    elif p["lock"] == 2:
        rules = combine(*rm("tf"), sw("cg", NONE, tf))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(human, rules, sw("tf", sw("cg", to_human, to_cougar), sw("cg", cougar_atk, human_atk))),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Javelin Toss / Takedown
    def jav(mult):
        return [magic(p["q_dmg"] * mult // 100, p["q_ap"] * mult // 100), view("q_hit"), tsfx("q_hit")]
    q_hits = [sw("q_d1", combine(*jav(100)), sw("q_d2", combine(*jav(p["q_mid"])), combine(*jav(p["q_far"]))))]
    throw = combine(refresh("q_d1", p["q_t1"]), refresh("q_d2", p["q_t2"]), sfx("q"),
                    line("q_spear", p["q_speed"], p["q_range"] + 10000, p["q_w"], "EnemyWithoutTower", False, q_hits),
                    line("q_twin", p["q_speed"], p["q_range"] + 10000, p["q_w"], "EnemyChampion", False, hunted))
    javelin = combine(flag("hq_cd", p["q_cd"]), anim("skill", p["q_dur"]), voice("vo_q", p),
                      delayed(p["q_at"] - 1, throw))
    takedown = combine(flag("cq_cd", p["cq_cd"]), refresh("cq_on", p["cq_t"]), cview("cq_arm"), sfx("cq_arm"))
    skill = action("idle", 3, 60, 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(human, sw("cg", sw("cq_cd", NONE, sw("cq_on", NONE, takedown)), sw("hq_cd", NONE, javelin))), key="skill")

    # ------------------------------------------------------------------ skill2: Primal Surge + Bushwhack / Pounce + Swipe
    surge = pick(p["e_range"], "AllyChampion",
                 {"type": "Heal", "amount": p["e_heal"], "attack_ratio": 0, "ap_ratio": p["e_ap"], "heal_type": "Ally"},
                 buff("e_as", p["e_as_t"], attack_speed_mult=p["e_as"]), view("e_heal"), tsfx("e_heal"))
    e_cast = combine(flag("e_cd", p["e_cd"]), anim("skill2", p["e_anim"]), sfx("e"), voice("vo_e", p),
                     delayed(p["e_at"] - 1, surge))

    def trap_at(target):
        pulse = [magic(p["w_dmg"], p["w_ap"]), view("w_snap"), tsfx("w_snap")]
        land = [view("w_trap"), sfx("w_land"),
                field("w_field", p["w_r"], p["w_life"], p["w_per"], "EnemyWithoutTower", pulse),
                field("w_hunt", p["w_r"], p["w_life"], p["w_per"], "EnemyChampion", hunted)]
        return pick(p["w_range"], target, lob("w_lob", p["w_fly"], "EnemyWithoutTower", land))
    w_cast = combine(flag("w_cd", p["w_cd"]), anim("skill2", p["w_anim"]), sfx("w"), voice("vo_w", p),
                     delayed(p["w_at"] - 1, combine(*rm("w_cc"), pick(p["w_range"], "EnemyChampionInCC", flag("w_cc", 1)),
                                                    sw("w_cc", trap_at("EnemyChampionInCC"),
                                                       trap_at("EnemyWithoutTower")))))
    human_s2 = sw("e_cd", sw("w_cd", NONE, w_cast), e_cast)

    def swipe(at):
        hits = [magic(p["ce_dmg"], p["ce_ap"]), view("ce_hit"), tsfx("ce_hit")]
        return combine(flag("ce_cd", p["ce_cd"]), anim("c_swipe", p["ce_anim"]), sfx("ce"), cview("ce_swipe"),
                       voice("vo_ce", p), delayed(at + p["ce_at"] - 1, around(p["ce_r"], "EnemyWithoutTower", hits)))

    def pounce(rng, target, dmg, ap, land_extra=()):
        hits = [magic(dmg, ap), view("cw_hit"), tsfx("cw_hit")]
        landing = [around(p["cw_rad"], "EnemyWithoutTower", hits), cview("cw_land"), sfx("cw_land"),
                   sw("ce_cd", NONE, swipe(0)), *land_extra]
        go_ = combine(anim("c_pounce", p["cw_anim"]), sfx("cw"), cview("cw_dust"), voice("vo_cw", p),
                      delayed(p["cw_go"] - 1, {"type": "MoveToTarget", "speed": p["cw_speed"], "range": rng + 30000,
                                               "end_effects": landing}))
        return pick(rng, target, go_)
    w_hunt = combine(flag("cw_cd", p["cw_cd_h"]), pounce(p["cw_far"], "EnemyChampion", p["cw_dmg"], p["cw_ap"]))
    w_near = combine(flag("cw_cd", p["cw_cd"]), pounce(p["cw_r"], "EnemyWithoutTower", p["cw_dmg"], p["cw_ap"]))
    # a pounce is cast only on a target in reach: probe first, so the cooldown is not spent on nothing
    probe = combine(*rm("w_in", "w_far"), pick(p["cw_r"], "EnemyWithoutTower", flag("w_in", 1)),
                    pick(p["cw_far"], "EnemyChampion", flag("w_far", 1)))
    leap = combine(probe, sw("hunt", sw("w_far", w_hunt, sw("w_in", w_near)), sw("w_in", w_near)))
    in_swipe = combine(*rm("e_in"), pick(p["ce_r"], "EnemyWithoutTower", flag("e_in", 1)), sw("e_in", swipe(0)))
    cougar_s2 = sw("cw_cd", sw("ce_cd", NONE, in_swipe), leap)
    skill2 = action("idle", 3, p["s2_cd"], 1, p["s2_range"], "None", "EnemyWithoutTower",
                    combine(human, sw("cg", cougar_s2, human_s2)), key="skill2")

    # ------------------------------------------------------------------ ult: the hunt pounce
    r_go = combine(instant_cougar, *rm("cw_cd", "ce_cd", "cq_cd"), refresh("cq_on", p["cq_t"]), flag("cw_cd", p["cw_cd"]),
                   cview("r_roar"), sfx("r"), voice("vo_r", p),
                   pick(p["r_range"], "EnemyChampionRecentlyAttacked",
                        combine(anim("c_pounce", p["cw_anim"]), cview("cw_dust"),
                                delayed(p["cw_go"] - 1, {"type": "MoveToTarget", "speed": p["cw_speed"],
                                                         "range": p["r_range"] + 30000,
                                                         "end_effects": [around(p["cw_rad"], "EnemyWithoutTower",
                                                                                [magic(p["r_dmg"], p["r_ap"]),
                                                                                 view("r_hit"), tsfx("r_hit")]),
                                                                         cview("cw_land"), sfx("cw_land"),
                                                                         swipe(0)]}))))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked", r_go, key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("a_spear"), P_("q_spear"), P_("w_lob")]
    views_e = [E("a_hit"), E("c_hit"), E("cq_hit"), E("cq_arm", FX, 3), E("q_hit"), E("e_heal"), E("w_trap", FX, -1, False),
               E("w_snap"), E("cw_dust", FX, 1), E("cw_land", BIG, -1, False), E("cw_hit"), E("ce_swipe", BIG, 3),
               E("ce_hit"), E("tf_cougar", BIG, 3), E("tf_human", BIG, 3), E("r_roar", BIG, 3), E("r_hit")]
    views_b = [B_("hunted", FX, 3), B_("e_as", FX, -1), B_("hunt", FX, -1)]
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AP", "Magic", "Range", "Melee", "Heal"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if p["native"]:
        kit["passive"] = {"passive_ref": "league_nidalee:prowl",
                          "params": {"brush_ms": p["brush_ms"], "brush_near_ms": p["brush_near_ms"],
                                     "brush_t": p["brush_t"], "near": p["brush_near"]}}
        kit["view_buffs"].append(B_("brush", FX, -1))
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
