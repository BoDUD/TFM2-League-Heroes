"""Build league_jarvaniv.data_champion (jungle, Melee) from the parameters P.

    python tools/kit/build_jarvaniv.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-17: jungle, layout A, the add-on league_jarvaniv, PPU 1.5, pro combos - 「全按推荐做」).
TFM2 has three active slots: the E -> Q combo is `skill`, Dragon Strike alone `skill2`, Cataclysm the `ult`; Golden Aegis
(W) has no slot - the watch casts it in fights (league_swain's / league_nasus's W the same way).
  passive Martial Cadence (战争律动): an attack on a champion after a p_rest-tick rest deals p_pct% of its max health more
          (League: 8% of current health, per target every 6-3 s: nothing reads current health or a target's own timer,
          so the rest is his - league_ekko's Z-Drive way).
  attack  a lance thrust (100% AD) struck by a hidden homing hit on `Enemy` (towers too) on a_hit; its champion-only twin
          marks the fight (`fight`, f_t ticks) and carries the passive.
  E passive: +e_as% attack speed (a Permanent caster buff laid at each life's first attack or R press).
  skill   E Demacian Standard -> Q Dragon Strike (德邦军旗 -> 巨龙撞击), `Targeting` on `EnemyWithoutTower` (e_range): on
          e_rel the flag is thrown - a hidden lob landing where the target stood when it left (walking off dodges the
          drag): e_dmg + e_ratio% AD in e_r (League's magic 80% AP: he has no AP); the standard stands fl_t ticks giving
          every allied champion within f_r (him too) f_as% attack speed. q_gap ticks after the landing the lance
          flies at the flag (q_dmg + q_ratio% AD, armour -q_shred% for q_shred_t) and he dashes after it (`MoveTo` in the
          lob's end_effects: ForceMove steps onto the point), knocking up for q_up ticks every enemy the lance passes and
          every enemy within q_up_r of the flag when he lands.
  skill2  Q Dragon Strike (巨龙撞击) alone, `Targeting` on `EnemyWithoutTower` (q_range): the aim is locked by a hidden lob
          (q_lock ticks before the thrust), then the lance flies to that point: q_dmg + q_ratio% AD, armour -q_shred%.
          League's Q also drags him to a standard already standing on its line: data can't tell where a standard
          stands, so only the combo drags him.
  W       Golden Aegis (黄金圣盾), automatic: in a fight (`fight`), w_cd off, an enemy champion within w_r: a shield of
          w_sh + w_ratio% AD for w_t ticks plus w_per for each enemy champion within w_r, and every enemy there slowed
          w_slow% for w_slow_t.
  ult     R Cataclysm (天崩地裂): the slot (a 3-tick `Targeting` on `EnemyChampion` within r_range) only arms the ult for
          r_arm ticks; the watch leaps once the moment is right (the user's rule 「看好时机」): two enemy champions within
          r_cnt, or a fight with one, or one knocked up by his E -> Q (the pro combo EQ -> R). Unused, the window ends
          with the cooldown capped at 60 ticks (`r_retry`). The leap (`MoveToTarget`, r_speed, cc_immune in the air)
          lands on an enemy champion in the fight (`EnemyChampionRecentlyAttacked`): r_dmg + r_ratio% AD within r_r, and
          the arena rises for r_t ticks: every enemy champion within r_r is held - a probe every r_lp ticks and, when it
          stands farther than r_leash from him, a Grab back to him (league_camille R's way, for each of them); if he
          himself leaves the arena (r_r round the landing point) it falls (League: terrain; data can't build walls - the
          add-on builds the real ring).
  watch   A life-long `AddCasted` started by his first attack or R press of each life (`init`), every watch_p ticks:
          counts enemy champions within r_cnt (c_e1, c_e2); leaps when the window is open and the moment holds; casts W.
The add-on copy (--native): the passive league_jarvaniv:cataclysm raises a real rock ring where he lands (r_r, r_t), so
the copy has no probe / Grab hold and no arena check (addons/league_jarvaniv).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_jarvaniv.data_champion")
ID = "league_jarvaniv"
FX = "asset/league/effects/league_jarvaniv_fx"
BIG = "asset/league/effects/league_jarvaniv_big"

# Timings from the strips (tools/art/rig_jarvaniv.py MS): the thrust's frame 3 from tick 8.4 (a_hit 9), the throw's
# frame 3 from 7.8 (e_rel 8), Q's thrust frame 4 from 10.8 (q_rel 11), W's frame 3 from 7.2 (w_rel 7), the ult 30.
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Jarvan IV:
    # 64 AD +3, 640 +104 hp, 36 armour, 340 move, attack speed 0.658 +2.5%
    "hp": 1000, "hp_g": 104, "atk": 84, "atk_g": 18, "def": 34, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000, "ms_g": 11,
    # attack: the thrust lands on a_hit
    "atk_range": 26000, "atk_dur": 26, "atk_cd": 60, "a_hit": 9, "f_t": 180,
    # passive Martial Cadence (League: 8% current health, min 20, per target every 6-3 s)
    "p_rest": 180, "p_pct": 8,
    # E passive (League: +20-30% attack speed)
    "e_as": 20,
    # skill: E -> Q (League: E 860 range, 80-240 + 80% AP, flag 8 s, aura +20-30% attack speed, cd 12-10;
    # Q 770 range, 90-250 + 145% bonus AD, armour -10-26% 3 s, knock-up 0.75 s, cd 10-6)
    "e_cd": 660, "e_range": 55000, "e_dur": 34, "e_rel": 8, "e_travel": 8, "e_r": 16000, "e_dmg": 50, "e_ratio": 40,
    "fl_t": 480, "f_r": 40000, "f_as": 20, "f_p": 30,
    "q_gap": 2, "q_speed": 4000, "q_line": 6000, "q_w": 9000, "q_up": 45, "q_up_r": 16000,
    "q_dmg": 40, "q_ratio": 90, "q_shred": 20, "q_shred_t": 180,
    # skill2: Q alone
    "q_cd": 480, "q_range": 50000, "q_dur": 26, "q_rel": 11, "q_lock": 8, "q_len": 50000,
    # W Golden Aegis (League: 60-140 + 70% bonus AD shield 4 s, +1.3% max hp a champion, slow 15-35% 2 s, r 600, cd 9)
    "w_cd": 600, "w_r": 30000, "w_dur": 18, "w_rel": 7, "w_sh": 60, "w_ratio": 40, "w_per": 25, "w_t": 240,
    "w_slow": 25, "w_slow_t": 120,
    # ult: R Cataclysm (League: 650 range leap, 200-450 + 180% bonus AD, ring r 350 for 3.5 s, cd 120-90)
    "r_cd": 3600, "r_range": 60000, "r_arm": 600, "r_dur": 30, "r_speed": 4500, "r_r": 36000, "r_t": 210,
    "r_dmg": 120, "r_ratio": 120, "r_lp": 3, "r_leash": 28000, "r_gs": 2500, "r_gt": 5, "r_cnt": 45000,
    # the watch
    "watch_p": 12,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_jarvaniv
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


def attack(dmg, ratio, thp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def shield(amount, ratio, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "tick": tick}


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


def homing(name, target, effects, speed=40000):
    """A hidden blow: at this speed it reaches a melee target on the next tick."""
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden ParabolicProjectile: lands where its target stood when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def line(name, speed, rng, width, effects, target="EnemyWithoutTower"):
    """A penetrating lance line from his spot (y_offset 5000) toward the action's point."""
    return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": 5000,
            "penetrate": True, "shape": circle(width), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def anchor(name, *end):
    """League_ekko's anchor: a 1-unit line that ends on his own spot the tick it starts; its end_effects act there."""
    return {"type": "LinearProjectile", "name": n(name), "speed": 1, "range": 1, "y_offset": 5000, "penetrate": True,
            "shape": circle(1000), "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": list(end)}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])
    marked = [refresh("fight", p["f_t"])]
    shred = buff("q_shred", p["q_shred_t"], defence_mult=-p["q_shred"])
    up = {"type": "Airborne", "duration": p["q_up"]}

    # ------------------------------------------------------------------ W: Golden Aegis (cast by the watch)
    aegis = combine(flag("w_cd", p["w_cd"]), anim("skill_w", p["w_dur"]), sfx("w"), voice("vo_w", p),
                    delayed(p["w_rel"] - 1, alive(
                        cview("w_cast"),
                        on_me(shield(p["w_sh"], p["w_ratio"], p["w_t"]), refresh("w_on", p["w_t"])),
                        around(p["w_r"], "EnemyWithoutTower",
                               [buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_hit")]),
                        around(p["w_r"], "EnemyChampion", [on_me(shield(p["w_per"], 0, p["w_t"]))]))))

    # ------------------------------------------------------------------ ult: R Cataclysm
    hold = homing("r_probe", "EnemyChampion", [
        pick(p["r_leash"], "AllyOnlySelf", flag("near", 1)) | {"from_projectile": True},
        sw("near", NONE, sw("r_on", combine({"type": "Grab", "speed": p["r_gs"], "tick": p["r_gt"]}, view("r_zap")))),
        *rm("near")])
    trap = casted(p["r_t"], p["r_lp"], alive(sw("r_on", hold)))
    arena = anchor("r_anchor",
                   field("r_area", p["r_r"], p["r_t"], 1, [refresh("r_in", 2)], target="AllyOnlySelf", first=0),
                   field("r_chk", 2000000, p["r_t"], 1, [sw("r_in", NONE, combine(*rm("r_on")))],
                         target="AllyOnlySelf", first=1))
    land = [*rm("r_on", "r_in"), refresh("r_on", p["r_t"]), refresh("r_in", 6), sfx("r_land"), cview("r_ring"),
            around(p["r_r"], "EnemyWithoutTower", [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]),
            *([around(p["r_r"], "EnemyChampion", marked)] if native else
              [around(p["r_r"], "EnemyChampion", [trap] + marked), arena])]
    leap = combine(*rm("r_arm"), refresh("busy", p["r_dur"]), anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p),
                   flag("r_air", p["r_dur"], cc_immune=True),
                   {"type": "MoveToTarget", "speed": p["r_speed"], "range": 400000, "end_effects": land})
    tick = p["watch_p"]
    count = combine(*rm("c_e1", "c_e2"),
                    around(p["r_cnt"], "EnemyChampion", [sw("c_e1", flag("c_e2", 3), flag("c_e1", 3))]))
    # onto a champion in the fight (the window stays open while none is in reach)
    ok = pick(p["r_range"], "EnemyChampionRecentlyAttacked", leap)
    arm = sw("r_arm", sw("c_e2", ok, sw("c_e1", sw("fight", ok, sw("eq_up", ok)))))
    cast_w = sw("w_cd", NONE, sw("busy", NONE, sw("fight", sw("c_e1", aegis))))
    watch = on_me(casted(1000000, tick, count, delayed(1, arm, cast_w)))
    life = sw("init", NONE, combine(flag("init", None), flag("e_as", None, attack_speed_mult=p["e_as"]), watch))

    # ------------------------------------------------------------------ attack: the lance thrust
    cadence = sw("p_cd", NONE, combine(flag("p_cd", p["p_rest"]), attack(0, 0, p["p_pct"]), view("p_hit"),
                                       tsfx("p_hit")))
    blow = combine(sfx("a_swing"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                   homing("a_twin", "EnemyChampion", marked + [cadence]))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, delayed(p["a_hit"] - 1, blow)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: E -> Q
    q_hit = [attack(p["q_dmg"], p["q_ratio"]), shred, view("q_hit"), tsfx("q_hit")]
    drag = [refresh("busy", 30), anim("skill_dash", 40), sfx("q_dash"),
            line("eq_line", p["q_speed"] + p["q_line"], p["e_range"] + 20000, p["q_w"], q_hit + [up]),
            line("eq_twin", p["q_speed"] + p["q_line"], p["e_range"] + 20000, p["q_w"],
                 marked + [refresh("eq_up", 90)], target="EnemyChampion"),
            {"type": "MoveTo", "speed": p["q_speed"], "range": 400000, "end_effects": [
                anim("skill_land", 10), sfx("q_land"), view("q_land"),
                around(p["q_up_r"], "EnemyWithoutTower", [up])]}]
    planted = [view("e_flag"), sfx("e_flag"),
               zone("e_hit", p["e_r"], [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")]),
               field("e_aura", p["f_r"], p["fl_t"], p["f_p"],
                     [buff("f_as", p["f_p"], attack_speed_mult=p["f_as"])], target="AllyChampion", first=1),
               delayed(p["q_gap"], alive(*drag))]
    skill = action("skill", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                   combine(refresh("busy", p["e_dur"] + 20), anim("skill", p["e_dur"]), sfx("e"), voice("vo_e", p),
                           delayed(p["e_rel"] - 1, lob("e_lob", p["e_travel"], planted))))

    # ------------------------------------------------------------------ skill2: Q alone
    thrust = [line("q_line", p["q_speed"] + p["q_line"], p["q_len"], p["q_w"], q_hit),
              line("q_twin", p["q_speed"] + p["q_line"], p["q_len"], p["q_w"], marked, target="EnemyChampion")]
    skill2 = action("skill2", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                    combine(refresh("busy", p["q_dur"]), anim("skill2", p["q_dur"]), sfx("q"), voice("vo_q", p),
                            delayed(p["q_rel"] - p["q_lock"] - 1, lob("q_lock", p["q_lock"], [alive(*thrust)]))))

    # ------------------------------------------------------------------ ult: the slot arms the window
    retry = p["r_cd"] * 100 // 60 - 100
    reset = sw("r_arm", combine(*rm("r_arm"), flag("r_retry", 3, ult_cooldown_mult=retry)))
    arm_r = combine(refresh("r_arm", p["r_arm"]), on_me(delayed(p["r_arm"], reset)))
    scored = combine(flag("r_x", 1), sw("r_x", combine(*rm("r_x"), arm_r), attack(100, 100)), *rm("r_x"))
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", combine(life, scored),
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = []
    views_e = [E("a_hit"), E("p_hit"), E("q_hit"), E("q_land", BIG, -1, False), E("e_flag", BIG, 1, False),
               E("e_hit"), E("w_cast", BIG, 2), E("w_hit"), E("r_ring", BIG, -1, False), E("r_hit"), E("r_zap")]
    views_b = [B_("w_slow", FX, 3), B_("w_on", FX, 3), B_("q_shred", FX, 3), B_("f_as", FX, 3)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_jarvaniv:cataclysm", "params": {"r_r": p["r_r"], "r_t": p["r_t"]}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC", "Tank"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
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
