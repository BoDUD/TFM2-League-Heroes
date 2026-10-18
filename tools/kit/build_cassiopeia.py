"""Build league_cassiopeia.data_champion (mid, Magician) from the parameters P.

    python tools/kit/build_cassiopeia.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's pick, 2026-10-18: plan A with the add-on league_cassiopeia). TFM2 has three active slots and League's
Twin Fang is cast every 0.75 s, faster than any skill slot can (none recasts under 60 ticks), so Twin Fang is her
attack; Noxious Blast is `skill`, Miasma `skill2`, Petrifying Gaze the `ult`.
  passive Serpentine Grace (优雅蛇行): League forbids boots and makes speed bonuses stronger. TFM2 sells no boots, so
          she gets a higher move-speed growth (ms_g) and Noxious Blast's speed is bigger than League's.
  attack  E Twin Fang (双生毒牙): a homing fang on `Enemy` (towers too), e_dmg + e_ratio% AP. Data cannot read a buff on
          the target (champion-data: SwitchByBuff reads the caster), so the main pack's "poisoned" is her own
          `venom` flag, raised for v_t ticks whenever her Q or W poisons something: while it is on, the fang deals
          e_bonus + e_bratio% AP more and heals her e_heal% AP (a champion-only twin carries the heal; a minion or
          monster heals her e_heal_m% AP - League 2.5-4% vs 10-16%). The add-on copy checks the fang's own target.
  skill   Q Noxious Blast (瘟毒爆炸), `Position` on `EnemyWithoutTower` (q_range): the aim is locked at the release, the
          blast lands q_delay ticks later (League 0.4 s, a telegraph on the spot meanwhile) in q_r and poisons every
          enemy there for q_t ticks (q_dmg + q_ratio% AP in all, every q_p ticks); a champion hit gives her q_ms%
          move speed fading in three steps over q_t (League 30-50% decaying over 3 s).
  skill2  W Miasma (剧毒迷雾), `Position` on `EnemyChampion` (w_range: a slowing zone, wasted on waves): a bolt lands in
          w_travel ticks and the cloud lies w_t ticks in w_r: every w_p ticks w_dmg + w_ratio% AP, a w_slow% slow and
          grounding (`BlockMoveSkill`, no dashes) for w_hold ticks, and her venom flag.
  ult     R Petrifying Gaze (石化凝视): the slot (a 3-tick `Targeting` on `EnemyChampion` within r_range) only arms the
          gaze for r_arm ticks (league_kayle / league_ziggs); her fangs check the moment while it lasts and gaze
          toward the fang's target: two or more enemy champions in the cone (r_range, r_cos = cos of half of League's
          80 degrees x 1000), one diving her (within r_dive), or - after r_wait ticks - one in the cone. Every enemy
          in the cone takes r_dmg + r_ratio% AP; League stuns those facing her and slows the rest - nothing in data
          reads where a unit faces, so the main pack stuns those within r_near (fighting her side) for r_stun and
          slows the farther ones r_slow% for r_stun (a stone crust, the buff `r_stone`, shows on the petrified); the
          wave flies out as a picture on a projectile (r_wave, r_fly ticks). The add-on copy decides by the enemy's
          real facing. Unused,
          the window ends with the cooldown capped at 60 ticks (`r_retry`).
The add-on copy (--native, addons/league_cassiopeia): poison also hangs the marker buff `poison` on the unit for its
length; the fang's bonus and heal are the Native effect league_cassiopeia:fang (only on a target carrying the marker);
the gaze's stun or slow is league_cassiopeia:gaze per enemy (facing her -> stun, back turned -> slow).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_cassiopeia.data_champion")
ID = "league_cassiopeia"
FX = "asset/league/effects/league_cassiopeia_fx"
BIG = "asset/league/effects/league_cassiopeia_big"

# League units x 100 = ours (attack range 550 -> 55000 like every mid; Twin Fang's 700 -> 60000 so she kites a little
# farther); radii count the unit's collision radius (~15000) on top. Release ticks from the strips (rig_cassiopeia.MS:
# the fang and Q leave on frame 3 at 140 ms, W at 150, the gaze at 250). Numbers = the 10-min classic-SDK simulations
# (mid lane 2 against pyromancer, ice_mage, lightning_mage, wind_mage and white_mage, three lineups, both sides, seeds
# 1-8 and 9-16, 2026-10-18; league_syndra +1.17 / +1.22): the draft (fang 22 + 18%, bonus 18 + 30%, hp 880) +2.45;
# fang -20% +0.83 / +2.18; -15% +1.86 / +1.23; the stun 90 ticks +1.20 / +1.74; fang -20% and hp 850 +1.03 (16 seeds at
# once) = P - League's 2 s petrify kept.
P = {
    # stats (Magician base: attack 76 +6, ap 40 +20, hp 860 +95, def 18 +7, mr 20 +4, move 900 +9); League's
    # Cassiopeia: 610 +98 hp, 18 armour, 32 mr, 335 move, 550 range, attack speed 0.647
    "hp": 850, "hp_g": 95, "atk": 60, "atk_g": 4, "apw": 40, "apw_g": 20, "def": 18, "def_g": 7, "mr": 22, "mr_g": 4,
    "ms": 900, "ms_g": 16,
    # E Twin Fang (League: 700 range, every 0.75 s, 50-120 +20% AP, +20-120 +45% AP poisoned, heal 10-16% AP)
    "atk_range": 60000, "atk_dur": 24, "atk_cd": 45, "a_rel": 8, "e_speed": 5000,
    "e_dmg": 18, "e_ratio": 14, "e_bonus": 14, "e_bratio": 24, "e_heal": 10, "e_heal_m": 3, "v_t": 180,
    # Q Noxious Blast (League: 850 range, r 200, lands 0.4 s, poison 3 s 65-205 +75% AP, +30-50% ms over 3 s, cd 3.5)
    "q_cd": 240, "q_range": 80000, "q_dur": 24, "q_rel": 8, "q_delay": 24, "q_r": 22000, "q_t": 180, "q_p": 30,
    "q_dmg": 75, "q_ratio": 60, "q_ms": 45,
    # W Miasma (League: 700 range, clouds 5 s, 20-40 +10% AP a second, slow 40-80%, grounded, cd 24-16)
    "w_cd": 900, "w_range": 65000, "w_dur": 27, "w_rel": 9, "w_travel": 12, "w_r": 30000, "w_t": 300, "w_p": 15,
    "w_dmg": 6, "w_ratio": 3, "w_slow": 50, "w_hold": 20, "w_show": 15,
    # R Petrifying Gaze (League: cone 80 deg r 850, 125-325 +75% AP, stun 2 s facing / slow 40% 2 s, cd 120-80)
    "r_cd": 3000, "r_range": 72000, "r_cos": 766, "r_near": 45000, "r_dive": 25000, "r_arm": 600, "r_wait": 240,
    "r_dur": 33, "r_rel": 15, "r_dmg": 160, "r_ratio": 70, "r_stun": 120, "r_slow": 40, "r_fly": 12, "r_y": 14000,
    "vo_gap": 600,
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
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower", seen=""):
    """A ParabolicProjectile: lands where its target stood when it left; end_effects run on that point; `seen` = the
    telegraph played on the landing point the whole flight."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": n(seen) if seen else "", "shape": circle(1), "applied_target": target,
            "applied_effects": [], "end_effects": list(end)}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def once(name, radius, tick, effects, target="EnemyWithoutTower"):
    """Each unit hit once over the zone's whole life, on the tick it first touches it (league_thresh R)."""
    return {"type": "ApplyInProjectile", "name": n(name), "shape": circle(radius), "tick": tick,
            "follow_caster": False, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def cone(radius, target, effects, cos):
    """A cone in front of her toward the action's target (league_darius E / league_annie W)."""
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def build(p):
    nat = bool(p["native"])
    venom = refresh("venom", p["v_t"])
    marker = [buff("poison", p["q_t"])] if nat else []

    # ------------------------------------------------------------------ ult: R Petrifying Gaze (fired by her fangs)
    if nat:
        hold = [native("gaze")]
    else:
        hold = [buff("r_slow", p["r_stun"], move_speed_mult=-p["r_slow"])]
    blast = [ap(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit"), *hold]
    stone = [] if nat else [cone(p["r_near"], "EnemyChampion", [{"type": "Stun", "duration": p["r_stun"]},
                                                                  buff("r_stone", p["r_stun"])], p["r_cos"])]
    # the gaze's wave points at them: a picture riding a projectile toward the fang's target (turned with its flight,
    # so the red side reads too - a caster picture is never mirrored)
    wave_ = {"type": "LinearProjectile", "name": n("r_wave"), "speed": max(1, p["r_range"] // p["r_fly"]),
             "range": p["r_range"], "y_offset": p["r_y"], "penetrate": True, "shape": circle(1000),
             "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": []}
    gaze = combine(*rm("r_arm", "r_late"), refresh("r_now", p["r_dur"]), anim("ult", p["r_dur"]), cview("r_cast"),
                   sfx("r"), voice("vo_r", p),
                   delayed(p["r_rel"] - 1, alive(wave_,
                                                 cone(p["r_range"], "EnemyChampion", blast, p["r_cos"]), *stone)))
    count = cone(p["r_range"], "EnemyChampion", [sw("n1", flag("n2", 3), flag("n1", 3))], p["r_cos"])
    dive = around(p["r_dive"], "EnemyChampion", [flag("r_dive", 3)])
    decide = sw("n2", gaze, sw("r_dive", gaze, sw("r_late", sw("n1", gaze))))
    check = sw("r_arm", combine(*rm("n1", "n2", "r_dive"), count, dive, delayed(1, decide)))

    # ------------------------------------------------------------------ attack: E Twin Fang
    if nat:
        boost, boost_c = [native("fang")], []
    else:
        boost = [sw("venom", combine(ap(p["e_bonus"], p["e_bratio"]),
                                     {"type": "Heal", "amount": 0, "attack_ratio": 0, "ap_ratio": p["e_heal_m"],
                                      "heal_type": "Caster"}))]
        boost_c = [sw("venom", {"type": "Heal", "amount": 0, "attack_ratio": 0,
                                "ap_ratio": p["e_heal"] - p["e_heal_m"], "heal_type": "Caster"})]
    fang = combine(sfx("a"), homing("a_fang", "Enemy", [ap(p["e_dmg"], p["e_ratio"]), *boost, view("a_hit"),
                                                         tsfx("a_hit")], p["e_speed"]),
                   *([homing("a_twin", "EnemyChampion", boost_c, p["e_speed"])] if boost_c else []))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(check, delayed(p["a_rel"] - 1, sw("r_now", NONE, fang))), atype="BaseAttack",
                      cancel=True)

    # ------------------------------------------------------------------ skill: Q Noxious Blast
    runs = p["q_t"] // p["q_p"]
    poison = casted(p["q_t"], p["q_p"], ap(round(p["q_dmg"] / runs), round(p["q_ratio"] / runs)), kind="Poison")
    third = p["q_t"] // 3
    step = p["q_ms"] // 3
    fast = on_me(refresh("q_f1", third, move_speed_mult=step), refresh("q_f2", 2 * third, move_speed_mult=step),
                 refresh("q_f3", p["q_t"], move_speed_mult=step))
    blast_q = [view("q_blast"), sfx("q_blast"),
               zone("q_zone", p["q_r"], [poison, *marker, venom, view("q_hit"), tsfx("q_hit")]),
               zone("q_champ", p["q_r"], [fast], target="EnemyChampion")]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(sfx("q"), voice("vo_q", p),
                           delayed(p["q_rel"] - 1, alive(lob("q_drop", p["q_delay"], blast_q, seen="q_warn")))))

    # ------------------------------------------------------------------ skill2: W Miasma
    cloud_hit = [ap(p["w_dmg"], p["w_ratio"]), buff("w_slow", p["w_hold"], move_speed_mult=-p["w_slow"]),
                 {"type": "BlockMoveSkill", "tick": p["w_hold"]}, refresh("venom", p["w_hold"] + p["w_p"]),
                 *([buff("poison", p["w_hold"] + p["w_p"])] if nat else [])]
    cloud = field("w_cloud", p["w_r"], p["w_t"], p["w_p"], cloud_hit, first=0)
    lying = [delayed(k, view("w_field")) for k in range(0, p["w_t"], p["w_show"])]
    bolt = lob("w_bolt", p["w_travel"], [sfx("w_land"), view("w_land"), cloud], target="EnemyChampion")
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Position", "EnemyChampion",
                    combine(sfx("w"), voice("vo_w", p), delayed(p["w_rel"] - 1, alive(bolt)),
                            delayed(p["w_rel"] - 1 + p["w_travel"], *lying)))

    # ------------------------------------------------------------------ ult slot: arms the gaze
    retry = p["r_cd"] * 100 // 60 - 100
    reset = sw("r_arm", combine(*rm("r_arm", "r_late"), flag("r_retry", 3, ult_cooldown_mult=retry)))
    arm_r = combine(refresh("r_arm", p["r_arm"]), on_me(delayed(p["r_wait"], sw("r_arm", refresh("r_late", 600))),
                                                        delayed(p["r_arm"], reset)))
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), arm_r), ap(p["r_dmg"], p["r_ratio"])), *rm("r_x"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", scored, key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                 "z": 2}
    # projectiles are turned with their flight: the fang and the wave are drawn pointing right, top-bottom symmetric
    views_p = [Pj("a_fang"), Pj("w_bolt"), Pj("r_wave", BIG)]
    views_e = [E("a_hit"), E("q_warn", BIG, -2, False), E("q_blast", BIG, 2, False), E("q_hit"),
               E("w_land", BIG, -1, False), E("w_field", BIG, -1, False), E("r_cast", BIG, 3), E("r_hit")]
    views_b = [B_("w_slow"), B_("r_slow"), B_("r_stone")]
    extra = {}
    if nat:
        extra["passive"] = {"passive_ref": f"{ID}:venom", "params": {
            "e_bonus": p["e_bonus"], "e_bratio": p["e_bratio"], "e_heal": p["e_heal"], "e_heal_m": p["e_heal_m"],
            "r_stun": p["r_stun"], "r_slow": p["r_slow"]}}
    return {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Range"], **extra,
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
