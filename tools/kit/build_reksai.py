"""Build league_reksai.data_champion (jungle, Melee) from the parameters P.

    python tools/kit/build_reksai.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-17: jungle, the add-on league_reksai, PPU 1.5, the recommended plan). TFM2 has three
active slots: Furious Bite (E) rides the attack at full Fury, Queen's Wrath / Prey Seeker share `skill`, Burrow /
Unburrow is `skill2`, Void Rush the `ult`. League's tunnels (E2) live on the map for minutes: only the add-on has them.
  passive Fury of the Xer'Sai (艾克塞之怒): f1..f4 caster stacks (fury_t ticks, renewed by each gain; League's 25 Fury a
          hit, 100 at most, decaying out of combat): a point for each attack, each Q and each Unburrow. Burrowing spends
          them for a heal (Burrow below).
  attack  The bite-swipe, the hit on tick a_hit. Queen's Wrath armed (q_1 / q_2): the hit splashes round the target
          (TargetSplashProjectile q_splash) for q_bonus% AD more. Full Fury and Furious Bite ready (no e_cd): the attack
          is Furious Bite (狂野之噬, the `bite` strip, hit on tick e_hit): League's max-Fury bite, e_dmg + e_ratio% AD as
          true damage (FixedAttack), then e_cd ticks before the next.
  skill   Q (`Targeting` on `EnemyWithoutTower`, q_range): an enemy within q_near of her -> Queen's Wrath (女王之怒): the
          first empowered swipe at once (splash, q_dmg + q_ratio% AD), q_as% attack speed for q_t ticks and the next two
          attacks empowered (q_1, q_2); none -> Prey Seeker (猎物搜寻): she dips into the ground and a void-charged burst
          of earth flies straight at where the target stands on tick q2_at (a LinearProjectile, the first unit it meets:
          dodgeable), q2_dmg + q2_ratio% AD.
  skill2  W Burrow / Unburrow (遁地 / 破土而出), `Targeting` on `EnemyWithoutTower` (w_range): she burrows (Fury spent for a
          heal: w_heal + w_heal_r% AD at full Fury, a quarter per point), tunnels under the target (MoveToTarget) and
          bursts up on arrival: w_dmg + w_ratio% AD round her (w_r) and every enemy knocked up w_up ticks.
          The moment (the user's rule 「看好时机」): the life-long watch (below) holds W (`w_hold`, an empty branch the
          AI scores as nothing) while three or more enemy champions stand within w_count of her and no allied champion
          within w_ally - she does not tunnel alone into a crowd. Camps and waves are never held.
  ult     R Void Rush (虚空猛冲), `Targeting` on `EnemyChampionRecentlyAttacked` (League's "Marked as Prey": a champion
          her team damaged lately; nothing reads her own marks) within r_range, armed by the watch (`r_ok`): an enemy
          champion in crowd control within r_range, or an allied champion within w_ally fighting with her. She drops
          underground (CasterInvisible + damaged_reduce 100 + cc_immune for r_hide ticks: League's untargetable 0.9 s),
          then lunges through the target: r_dmg + r_ratio% AD + r_hp% of its MAXIMUM health (League since V25.15).
  watch   A life-long `AddCasted` started by her first action of each life (`init`; buffs die with her), every
          watch_p ticks: counts enemy champions within w_count (c_e1..c_e3), allied champions within w_ally (c_a1, c_a2
          = one besides her) and looks for an enemy champion in CC within r_range (c_cc); then sets w_hold / r_ok for
          the next period.
The add-on copy (--native): the passive `league_reksai:fury` takes the burrowed body, the tunnels and R's real-health
pick; the data keeps every hit, picture and sound (see addons/league_reksai/README.md).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_reksai.data_champion")
ID = "league_reksai"
FX = "asset/league/effects/league_reksai_fx"
BIG = "asset/league/effects/league_reksai_big"

# Timings from the strips (tools/art/rig_reksai.py): the bite-swipe hits on tick 11 (attack frame 3), Queen's Wrath's
# slam on 10, Prey Seeker leaves on 8, Furious Bite on 12, the dash under the ground starts on 7 (skill2: into the
# ground by then, the mound for w_dig ticks; skill2_up, the burst, is played on arrival), Void Rush's leap (ult_hit) at
# the end of r_hide.
# Numbers = the 10-min classic-SDK simulations (jungle lane 1 against demon, circus_blade, hunter, inquisitor and ninja,
# three lineups, both sides, 2026-10-17): the draft r0 +0.67 (8 seeds; league_xinzhao +1.80, league_vi +2.73); attack
# 80 -> 86, Queen's Wrath 120 -> 140% + 35 -> 45%, Furious Bite 50 + 90% -> 70 + 110%, Unburrow 45 + 70% -> 60 + 90%:
# +2.17 over 16 seeds (league_xinzhao +0.95, league_vi +2.38); with W's cooldown 420 too +2.60, with hp 1060 +3.26.
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Rek'Sai:
    # 600 +99 hp, 62 AD +3, 35 armour +4.5, 340 move, 175 range, 0.667 attack speed
    "hp": 1000, "hp_g": 100, "atk": 86, "atk_g": 17, "def": 32, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000,
    "ms_g": 11, "regen": 2, "regen_g": 1,
    # attack
    "atk_range": 26000, "atk_dur": 26, "atk_cd": 60, "a_hit": 11,
    # Fury (League: 25 a hit, 100 at most, decays after 8 s out of combat)
    "fury_t": 480,
    # E Furious Bite folded into the attack (League: 70-170 + 60% bAD, at 100 Fury 120% of it as true damage, cd 6 s)
    "e_cd": 360, "e_dur": 28, "e_hit": 12, "e_dmg": 70, "e_ratio": 110,
    # skill: Q Queen's Wrath (League: next 3 attacks +30-50% AD round the target, 325 radius, +35% attack speed 3 s,
    # cd 4-2 s) / Prey Seeker (League: 1500 range, width 130, speed 1950, 50-170 + 25% bAD magic, cd 10 s)
    "q_cd": 330, "q_range": 60000, "q_near": 30000, "q_dur": 24, "q_hit": 10, "q_dmg": 15, "q_ratio": 140,
    "q_bonus": 45, "q_splash": 16000, "q_as": 35, "q_t": 180,
    "q2_dur": 22, "q2_at": 8, "q2_speed": 9000, "q2_len": 64000, "q2_rad": 4500, "q2_dmg": 40, "q2_ratio": 55,
    # skill2: W Burrow / Unburrow (League: burrowed +5-25 move; Unburrow 30-130 + 80% AP magic, knock-up 1 s, radius
    # 250; the burrow heals 9-21% max hp over 3 s at 100 Fury)
    "w_cd": 480, "w_range": 45000, "w_dur": 48, "w_dig": 28, "w_go": 7, "w_speed": 3500, "w_r": 17000, "w_up_t": 20,
    "w_dmg": 60, "w_ratio": 90,
    "w_up": 60, "w_heal": 50, "w_heal_r": 50,
    # ult: R Void Rush (League: 1500 range, untargetable 0.9 s, 150-350 + 100% bAD + 15/20/25% max hp, cd 120-80 s)
    "r_cd": 3600, "r_range": 70000, "r_dur": 30, "r_hide": 54, "r_speed": 9000, "r_dmg": 120, "r_ratio": 100,
    "r_hp": 15,
    # Marked as Prey: the picture's pieces (the add-on remembers a mark for prey_t)
    "mark_t": 60, "prey_t": 300,
    # the watch
    "watch_p": 12, "w_count": 60000, "w_ally": 45000,
    # her spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_reksai (its native passive)
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


def sw(buff, yes, no=None, raw=False):
    return {"type": "SwitchByBuff", "buff_name": buff if raw else n(buff), "effect_buff": yes,
            "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    """One instance of a caster buff, whoever adds it how often (same-name buffs add up)."""
    return combine(*rm(name), flag(name, tick, **fields))


def buff(name, tick, raw=False, **fields):
    return {"type": "AddBuff", "buff_state": {"name": name if raw else n(name), "duration": {"Time": {"tick": tick}},
                                              **fields}}


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


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def true_dmg(dmg, ratio):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on her alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def splash(name, radius, effects):
    return {"type": "TargetSplashProjectile", "name": n(name), "speed": 100000, "range": radius, "y_offset": 0,
            "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": [], "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def voice(name, p):
    """Her spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ Fury
    def gain():
        top = combine(*rm("f3"), refresh("f4", p["fury_t"]), sfx("p_full"))
        return sw("f4", refresh("f4", p["fury_t"]),
                  sw("f3", top, sw("f2", combine(*rm("f2"), refresh("f3", p["fury_t"])),
                                   sw("f1", combine(*rm("f1"), refresh("f2", p["fury_t"])),
                                      refresh("f1", p["fury_t"])))))

    spend = combine(*rm("f1", "f2", "f3", "f4"))

    # ------------------------------------------------------------------ the watch (W's hold, R's arming)
    tick = p["watch_p"]
    count = combine(*rm("c_e1", "c_e2", "c_e3", "c_a1", "c_a2", "c_cc"),
                    around(p["w_count"], "EnemyChampion",
                           [sw("c_e2", flag("c_e3", 3), sw("c_e1", flag("c_e2", 3), flag("c_e1", 3)))]),
                    around(p["w_ally"], "AllyChampion", [sw("c_a1", flag("c_a2", 3), flag("c_a1", 3))]),
                    pick(p["r_range"], "EnemyChampionInCC", flag("c_cc", 3)))
    arm = NONE if p["native"] else sw("c_cc", refresh("r_ok", tick + 2), sw("c_a2", sw("c_e1", refresh("r_ok", tick + 2))))
    decide = combine(sw("c_e3", sw("c_a2", NONE, refresh("w_hold", tick + 2))), arm)
    watch = on_me(casted(1000000, tick, count, delayed(1, decide)))
    life = sw("init", NONE, combine(flag("init", None), watch))

    # ------------------------------------------------------------------ attack (+ Queen's Wrath, Furious Bite)
    def wrath_hit(bonus_dmg, ratio):
        return [attack(bonus_dmg, ratio), view("q_hit"), tsfx("q_hit")]

    plain = combine(sfx("a_swing"), delayed(p["a_hit"] - 1,
                                            homing("a_hit", 100000, 0, "EnemyWithoutTower",
                                                   [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                                            gain()))

    def wrath_attack(nxt):
        return combine(sfx("a_swing"), *rm("q_1", "q_2"), *(flag(nxt, p["q_t"]),) if nxt else (),
                       delayed(p["a_hit"] - 1, splash("q_splash", p["q_splash"], wrath_hit(0, 100 + p["q_bonus"])),
                               gain()))

    bite = combine(anim("bite", p["e_dur"]), sfx("e"), voice("vo_e", p), flag("e_cd", p["e_cd"]),
                   delayed(p["e_hit"] - 1, homing("e_bite", 100000, 0, "EnemyWithoutTower",
                                                  [true_dmg(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")])))
    # one copy of the plain / Wrath branches (node budget): a 1-tick e_go picks the bite first
    choose = combine(sw("f4", sw("e_cd", NONE, flag("e_go", 1))),
                     sw("e_go", combine(*rm("e_go"), bite),
                        sw("q_1", wrath_attack("q_2"), sw("q_2", wrath_attack(None), plain))))
    # Marked as Prey: a champion she hits carries r_mark (its picture) - mark_t-tick pieces behind a caster gate so one
    # instance at a time (same-name buffs add up; league_amumu's curse); the add-on remembers a mark for prey_t
    mark = sw("p_mk", NONE, combine(flag("p_mk", p["mark_t"] - 5),
                                    homing("r_prey", 100000, 0, "EnemyChampion", [buff("r_mark", p["mark_t"])])))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, choose, delayed(p["a_hit"] - 1, mark)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Queen's Wrath / Prey Seeker
    wrath = combine(anim("skill", p["q_dur"]), sfx("q"), voice("vo_q", p),
                    *rm("q_as"), flag("q_as", p["q_t"], attack_speed_mult=p["q_as"]),
                    *rm("q_1", "q_2"), flag("q_1", p["q_t"]),
                    delayed(p["q_hit"] - 1, splash("q_splash", p["q_splash"], wrath_hit(p["q_dmg"], p["q_ratio"])),
                            gain()))
    seeker = combine(anim("skill_q2", p["q2_dur"]), sfx("q2"), voice("vo_q2", p),
                     delayed(p["q2_at"] - 1, cview("q2_cast"),
                             line("q2_shot", p["q2_speed"], p["q2_len"], p["q2_rad"], 2000, "EnemyWithoutTower", False,
                                  [attack(p["q2_dmg"], p["q2_ratio"]), view("q2_hit"), tsfx("q2_hit"),
                                   on_me(gain())])))
    probe = combine(*rm("q_nr"), around(p["q_near"], "EnemyWithoutTower", [refresh("q_nr", 3)]))
    skill = action("skill", max(p["q_dur"], p["q2_dur"]), p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(life, probe, delayed(1, sw("q_nr", wrath, seeker))))

    # ------------------------------------------------------------------ skill2: W Burrow / Unburrow
    def mend(k):
        return heal(p["w_heal"] * k // 4, p["w_heal_r"] * k // 4)

    burrow_heal = sw("f4", combine(mend(4), cview("w_heal")),
                     sw("f3", combine(mend(3), cview("w_heal")),
                        sw("f2", mend(2), sw("f1", mend(1)))))
    unburrow = [around(p["w_r"], "EnemyWithoutTower",
                       [attack(p["w_dmg"], p["w_ratio"]), {"type": "Airborne", "duration": p["w_up"]}, view("w_up"),
                        tsfx("w_hit")]),
                around(p["w_r"], "EnemyChampion", [buff("r_mark", p["mark_t"])]),
                cview("w_burst"), sfx("w_up"), gain(), anim("skill2_up", p["w_up_t"]), flag("w_land", 3)]
    dive = combine(flag("w_go", p["w_dig"]), anim("skill2", p["w_dig"]), sfx("w"), voice("vo_w", p), burrow_heal, spend, cview("w_dig"),
                   delayed(p["w_go"] - 1, {"type": "MoveToTarget", "speed": p["w_speed"], "range": p["w_range"] + 20000,
                                           "end_effects": unburrow}))
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                    combine(life, sw("w_hold", NONE, dive)))

    # ------------------------------------------------------------------ ult: R Void Rush
    hide = combine({"type": "CasterInvisible", "tick": p["r_hide"]},
                   refresh("r_hid", p["r_hide"], damaged_reduce=100, cc_immune=True))
    strike = [attack(p["r_dmg"], p["r_ratio"], p["r_hp"]), view("r_hit"), tsfx("r_hit")]
    rush = combine(anim("ult", p["r_hide"]), sfx("r"), voice("vo_r", p), hide, cview("r_dive"),
                   homing("r_tag", 100000, 0, "EnemyChampion", [buff("r_mark", p["r_hide"] + 20)]),
                   delayed(p["r_hide"] - 1, sfx("r_leap"), anim("ult_hit", p["r_dur"]), {"type": "MoveToTarget", "speed": p["r_speed"], "range": p["r_range"] + 30000,
                                             "end_effects": [homing("r_strike", 100000, 0, "EnemyChampion", strike),
                                                             cview("r_burst")]}))
    ult = action("ult", p["r_dur"] + p["r_hide"], p["r_cd"], 1, p["r_range"], "Targeting",
                 "EnemyChampionRecentlyAttacked", combine(life, sw("r_ok", rush)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, tag=None, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [{"type": "Animated", "name": n("q2_shot"), "anim": FX, "tag": "q2_shot", "repeat": True, "z": 2}]
    views_e = [E("a_hit"), E("q_hit"), E("e_hit"), E("q2_cast", FX, 2, False), E("q2_hit"),
               E("w_dig", BIG, -1, False), E("w_burst", BIG, -1, False), E("w_up"), E("w_heal", FX, 3),
               E("r_dive", BIG, -1, False), E("r_burst", BIG, 2, False), E("r_hit", BIG),
               # the add-on's tunnels (addons/league_reksai plays them at the entrances; nothing in the data does)
               E("e_tunnel", FX, -1, False), E("e_break", FX, 1, False)]
    views_b = [B_("f4", "p_full", FX, 4), B_("q_as", "q_buff", FX, -1), B_("r_mark", "r_mark", FX, 4)]
    extra = {}
    if p["native"]:
        extra["passive"] = {"passive_ref": "league_reksai:fury",
                            "params": {k: p[k] for k in ("w_heal", "w_heal_r", "r_dmg", "r_ratio", "r_hp", "r_range",
                                                         "prey_t", "w_dig")}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0,
                 "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": p["regen_g"], "stack": 0,
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
