"""Build league_galio.data_champion (mid, Melee AP tank mage) from the parameters P.

    python tools/kit/build_galio.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-13: mid / melee AP tank mage; Q as skill, E Justice Punch with W Shield of Durand after it
as skill2, R Hero's Entrance armed like league_shen R, the passive in the main pack plus a native add-on
addons/league_galio, the pros' combos):
  passive Colossal Smash (巨像重击): every p_cd ticks his next attack is a smash: the target takes the attack and every
          enemy within p_r of him (he stands in melee range, so it reaches round the target) p_dmg + p_ap% AP magic
          (League: every 5 s, 15-200 + AD + 50% AP + 60% bonus MR in an area; abilities that hit cut the wait - a caster
          flag cannot be shortened without restarting it, so the wait here is a flat p_cd).
  W passive Shield of Durand: League shields him against magic (6-15% max health) once he has gone 12 s without
          damage. The data reads neither, so his attack refreshes a w_ps + w_ps_ap% AP shield for w_ps_t ticks at most
          once every w_ps_cd ticks; with native=1 the add-on gives the shield after 12 s untouched and lets it take only
          magic damage.
  attack  A stone punch, the hit on tick atk_st (the smash: attack2, its own tag).
  skill   Q Winds of War (战争罡风): a `Position` cast on `EnemyWithoutTower` (q_range, waves and camps too): on q_at the
          two windblasts fly (a lob, q_fly ticks) to where the unit stood and burst - every enemy within q_r takes
          q_dmg + q_ap% AP - and a tornado stays there q_t ticks, every enemy inside taking q_tdmg + q_tap% AP every
          q_tp ticks (League: 4 ticks over 2 s of % max health). The pros' E -> Q and W -> Q: thrown while q_fast holds
          (his punch knocked up or his taunt caught a champion), the winds land at once.
  skill2  E Justice Punch (正义冲拳) and W Shield of Durand (杜朗护盾) share the slot, each on its own cooldown (caster flags
          e_cd and w_cd; the slot itself waits only s2_cd). A `Targeting` cast on `EnemyChampion` (e_range):
          - E ready: he steps back, then charges at the champion (`RushTime`, e_speed a tick for at most e_tick ticks)
            and stops on the first enemy champion in his way: e_dmg + e_ap% AP magic and a knock-up of e_up ticks
            (League: 0.75 s); a hit opens q_fast;
          - else W ready and an enemy champion within w_trig: he braces for w_ch ticks - w_dr% less damage (lingering
            w_lin ticks after) and slowed - then bursts: every enemy within w_r takes w_dmg + w_ap% AP and is taunted
            w_taunt ticks (League: 0.5-1.5 s by the charge; the add-on's charge lasts by how many enemy champions stand
            near); a taunted champion opens q_fast.
  ult     R Hero's Entrance (英雄登场): League's lands him on an ally anywhere; the data reads no health, so the slot only
          arms it (league_shen R): a 3-tick `None` action, then while r_arm lasts a poll every r_poll ticks looks for an
          allied champion (a) in crowd control, else (b) with an enemy champion within r_sur two polls in a row - and
          at least r_far from him. That ally gets r_sh + r_sh_ap% AP of shield for r_sh_t; he channels r_ch ticks
          (crowd control on him every r_brk ticks breaks it), flies onto the ally and lands: every enemy within r_r
          takes r_dmg + r_ap% AP and is knocked up r_up ticks (r_up_c within r_rc, the centre), allied champions round
          him get the shield too. The pros' R -> W: W ready, he braces on landing. Unused, the window ends with the
          cooldown capped. With native=1 the add-on picks the ally by health and how many enemies would be thrown up.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_galio.data_champion")
ID = "league_galio"
FX = "asset/league/effects/league_galio_fx"
BIG = "asset/league/effects/league_galio_big"

# Timings are placeholders until the strips (attack 26 / hit 12, Q 30 / 12, E 36 / charge 10, W charge + release 18,
# R wind 20).
P = {
    # stats (the pack's melee AP tanks: league_malphite hp 1100 +120, def 40, mr 30, atk 80, mp 30; mid mages mp 40-42);
    # League's Galio: 600 +126 hp, 59 AD, 24 armour +4.7, 32 mr +2.05, 340 move, 150 range - tank stats, mage scaling,
    # magic resistance his own
    "hp": 1100, "hp_g": 115, "atk": 78, "atk_g": 6, "mp": 40, "mp_g": 18, "def": 34, "def_g": 7, "mr": 36, "mr_g": 6,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 72, "atk_st": 12,
    # passive Colossal Smash (League: every 5 s, 15-200 + 100% AD + 50% AP + 60% bonus MR, radius ~300)
    "p_cd": 300, "p_r": 16000, "p_dmg": 50, "p_ap": 50,
    # W passive (League: magic shield 6-15% max hp after 12 s without damage)
    "w_ps": 90, "w_ps_ap": 30, "w_ps_t": 300, "w_ps_cd": 720,
    # Q Winds of War (League: 825 range, 70-210 + 75% AP, tornado 2 s 4 ticks of 2% max hp + AP, cd 11-7 s)
    "q_cd": 480, "q_range": 55000, "q_dur": 30, "q_at": 12, "q_fly": 24, "q_r": 15000, "q_dmg": 80, "q_ap": 60,
    "q_tr": 13000, "q_t": 120, "q_tp": 30, "q_tdmg": 15, "q_tap": 12, "q_fast": 120,
    # skill2 slot: E Justice Punch + W Shield of Durand
    "s2_cd": 60,
    # E Justice Punch (League: 650 dash, 90-250 + 90% AP, knock-up 0.75 s, cd 12-8 s)
    "e_cd": 600, "e_range": 43000, "e_dur": 36, "e_at": 10, "e_speed": 3600, "e_tick": 12, "e_dmg": 90, "e_ap": 70,
    "e_up": 45,
    # W Shield of Durand (League: 20-40% DR (half vs physical) while charging up to 2 s + 2 s after, taunt 0.5-1.5 s,
    # 20-140 + 30% AP in 400 units, cd 18-14 s)
    "w_cd": 900, "w_trig": 24000, "w_r": 26000, "w_ch": 50, "w_dr": 40, "w_lin": 60, "w_slow": 15, "w_taunt": 70,
    "w_dmg": 60, "w_ap": 50, "w_rel": 18,
    # R Hero's Entrance (League: 4000-5500 range, 2.75 s channel, allies 5 s W shield, 150-450 + 70% AP, knock-up
    # 0.75 s (1.5 s... at the centre in the data) radius 325, cd 180-140 s)
    "r_cd": 4200, "r_arm": 900, "r_poll": 10, "r_reset": 4900, "r_sur": 25000, "r_far": 60000, "r_seen": 25,
    "r_sh": 150, "r_sh_ap": 50, "r_sh_t": 300, "r_ch": 120, "r_brk": 15, "r_wind": 20,
    "r_r": 22000, "r_dmg": 160, "r_ap": 70, "r_up": 45, "r_rc": 10000, "r_up_c": 70,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_galio: its passive gives the magic shield and picks R's ally
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


def shield(amount, ap, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, proj=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": proj,
            "effects": [e for e in effects if e is not None]}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, fly, target, end):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": fly, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, apply, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": apply, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def pzone(name, r, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(r), "tick": tick, "period": period,
            "first_delay": 0, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def rush(speed, tick, target, effects):
    return {"type": "RushTime", "speed": speed, "tick": tick, "range": 12000, "casting_target": target,
            "penetrate": False, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])
    fast = on_me(refresh("q_fast", p["q_fast"]))

    # ------------------------------------------------------------------ attack (+ Colossal Smash, + W's passive shield)
    ward = NONE if native else sw("w_ps_cd", NONE, on_me(flag("w_ps_cd", p["w_ps_cd"]),
                                                         shield(p["w_ps"], p["w_ps_ap"], p["w_ps_t"]),
                                                         cview("w_ps")))
    smash = combine(anim("attack2", p["atk_dur"]), flag("p_cd", p["p_cd"]), sfx("p"),
                    delayed(p["atk_st"] - 1, attack(0, 100), view("p_hit"), tsfx("p_hit"),
                            around(p["p_r"], "EnemyWithoutTower", [magic(p["p_dmg"], p["p_ap"])]), cview("p_ring")))
    punch = combine(sfx("a_swing"), delayed(p["atk_st"] - 1, attack(0, 100), view("a_hit"), tsfx("a_hit")))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(ward, sw("p_cd", punch, smash)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Winds of War
    def winds(fly):
        burst = [view("q_burst"), sfx("q_hit"),
                 zone("q_blast", p["q_r"], 1, "EnemyWithoutTower", [magic(p["q_dmg"], p["q_ap"]), view("q_hit")]),
                 zone("q_twin", p["q_r"], 1, "EnemyChampion", [fast]),
                 view("q_tornado"),
                 pzone("q_tornado_zone", p["q_tr"], p["q_t"], p["q_tp"], "EnemyWithoutTower",
                       [magic(p["q_tdmg"], p["q_tap"])])]
        return lob("q_wind", fly, "EnemyWithoutTower", burst)

    cast_q = sw("q_fast", combine(*rm("q_fast"), winds(4)), winds(p["q_fly"]))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(voice("vo_q", p), sfx("q"), delayed(p["q_at"] - 1, cast_q)))

    # ------------------------------------------------------------------ skill2: E Justice Punch / W Shield of Durand
    e_hits = [magic(p["e_dmg"], p["e_ap"]), {"type": "Airborne", "duration": p["e_up"]}, view("e_hit"), tsfx("e_hit"),
              fast]
    punch_e = combine(flag("e_cd", p["e_cd"]), anim("skill2", p["e_dur"]), sfx("e"), voice("vo_e", p),
                      delayed(p["e_at"], cview("e_dash"), rush(p["e_speed"], p["e_tick"], "EnemyChampion", e_hits)))

    def brace():
        burst = combine(anim("w_burst", p["w_rel"]), cview("w_burst"), sfx("w_hit"),
                        around(p["w_r"], "EnemyWithoutTower",
                               [magic(p["w_dmg"], p["w_ap"]), {"type": "Taunt", "duration": p["w_taunt"]},
                                buff("w_taunt", p["w_taunt"])]),
                        around(p["w_r"], "EnemyChampion", [fast]))
        return combine(flag("w_cd", p["w_cd"]), anim("w_charge", p["w_ch"]), cview("w_charge"), sfx("w"),
                       voice("vo_w", p),
                       refresh("w_dr", p["w_ch"] + p["w_lin"], damaged_reduce=p["w_dr"]),
                       refresh("w_slow", p["w_ch"], move_speed_mult=-p["w_slow"]),
                       delayed(p["w_ch"], burst))

    near = combine(*rm("w_near"), pick(p["w_trig"], "EnemyChampion", flag("w_near", 1)))
    w_try = sw("w_cd", NONE, combine(near, sw("w_near", combine(*rm("w_near"), brace()))))
    skill2 = action("idle", 3, p["s2_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    sw("e_cd", w_try, punch_e), key="skill2")

    # ------------------------------------------------------------------ ult: R Hero's Entrance
    breaks = [delayed(t, pick(1, "AllyChampionInCC", *rm("r_ch"))) for t in range(p["r_brk"], p["r_ch"], p["r_brk"])]
    land = combine(view("r_land"), sfx("r_land"),
                   around(p["r_r"], "EnemyWithoutTower", [magic(p["r_dmg"], p["r_ap"]),
                                                         {"type": "Airborne", "duration": p["r_up"]}, view("r_hit")]),
                   around(p["r_rc"], "EnemyWithoutTower", [{"type": "Airborne", "duration": p["r_up_c"]}]),
                   around(p["r_r"], "AllyChampion", [shield(p["r_sh"], p["r_sh_ap"], p["r_sh_t"]),
                                                     buff("r_shield", p["r_sh_t"])]),
                   anim("ult_land", 24), w_try)

    def save():
        """On the ally (the probe's hit): the shield now, the channel on him, the flight onto it at the end."""
        return combine(*rm("r_arm", "r_seen"), refresh("r_ch", p["r_ch"] + 2),
                       shield(p["r_sh"], p["r_sh_ap"], p["r_sh_t"]), buff("r_shield", p["r_sh_t"]), sfx("r_ally"),
                       on_me(anim("ult", p["r_wind"]), delayed(p["r_wind"], anim("ult_loop", p["r_ch"] - p["r_wind"])),
                             cview("r_cast"), sfx("r"), voice("vo_r", p), *breaks),
                       delayed(p["r_ch"], sw("r_ch", combine(*rm("r_ch"), {"type": "Teleport"},
                                                              on_me(delayed(1, land))))))

    def probe(cc):
        """A homing probe at the ally picked: far enough from him, and in crowd control or held in a fight."""
        far = pick(p["r_far"], "AllyOnlySelf", flag("r_near", 1), proj=True)
        if cc:
            go = sw("r_near", combine(*rm("r_near")), save())
        else:
            fight = pick(p["r_sur"], "EnemyChampion", flag("r_e", 1), proj=True)
            go = combine(fight, sw("r_near", combine(*rm("r_near", "r_e")),
                                   sw("r_e", combine(*rm("r_e"), sw("r_seen", save(), refresh("r_seen", p["r_seen"]))))))
        return homing("r_probe", 1000000, "AllyChampion", [far, go])

    if native:  # the add-on marks the ally to land on (lowest health, most enemies round it) with r_pick on him
        look = sw("r_pick", pick(960000, "AllyNotSelf", probe(True)))
    else:
        look = combine(pick(960000, "AllyChampionInCC", flag("r_cc", 1)),
                       sw("r_cc", combine(*rm("r_cc"), pick(960000, "AllyChampionInCC", probe(True))),
                          pick(960000, "AllyNotSelf", probe(False))))
    poll = combine(pick(1, "AllyChampionInCC", flag("r_me", 1)),
                   sw("r_me", combine(*rm("r_me")), sw("r_arm", sw("r_ch", NONE, look))))
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_reset", 3, ult_cooldown_mult=p["r_reset"])))
    ult = action("idle", 3, p["r_cd"], 1, 960000, "None", "EnemyChampion",
                 combine(refresh("r_arm", p["r_arm"]),
                         on_me(casted(p["r_arm"], p["r_poll"], poll), delayed(p["r_arm"], reset))), key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2, tag=None: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("q_wind")]
    views_e = [E("a_hit"), E("p_hit"), E("p_ring", BIG, -1, False), E("w_ps", FX, 3), E("q_burst", BIG, 2, False),
               E("q_hit"), E("q_tornado", BIG, 2, False), E("e_dash", FX, 1), E("e_hit"), E("w_charge", BIG, 3),
               E("w_burst", BIG, 2, False), E("r_cast", FX, 3), E("r_land", BIG, 2, False), E("r_hit")]
    views_b = [B_("w_taunt", FX, 3), B_("r_shield", FX, 3)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Tank", "CC", "Shield"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_galio:colossus",
                          "params": {"ps": p["w_ps"], "ps_ap": p["w_ps_ap"], "ps_t": p["w_ps_t"],
                                     "w_ch": p["w_ch"], "w_taunt": p["w_taunt"], "r_far": p["r_far"]}}
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
