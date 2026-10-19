"""Build league_rammus.data_champion (jungle, Melee tank, AP) from the parameters P.

    python tools/kit/build_rammus.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-19: jungle, layout A, the add-on league_rammus). TFM2 has three active slots for League's
four buttons: Q Powerball is `skill`, E Frenzying Taunt `skill2`, R Soaring Slam the `ult`; W Defensive Ball Curl has no
slot - the watch curls him up in fights (league_jarvaniv's Golden Aegis the same way).
  passive Spiked Shell (锥刺甲壳): every attack adds p_dmg + p_ap% AP + p_hp% of his max health as magic damage (League:
          10 + 15% armour; data cannot read armour, so the tank stat it can read stands in - league_malphite's way; the
          add-on pays it from his real armour).
  attack  a claw swipe (100% AD) by a hidden homing hit on `Enemy` (towers too) on a_hit; its champion-only twin marks
          the fight (`fight`, f_t ticks).
  W       Defensive Ball Curl (尖刺防御), automatic: w_cd off, not busy, an enemy champion within w_go: he curls up
          (skill_w) and for w_t ticks has +w_def% armour and magic resistance and returns w_ref% of every hit taken
          (League: 15 + 10% armour + 10% MR magic damage to each attacker; the engine only has the percentage -
          league_annie's Molten Shield). w_cd counts from the cast (League's 7 s from the end: w_t + 7 s).
  skill   Q Powerball (动力冲刺), `Targeting` on `EnemyWithoutTower` (q_range): he curls into the ball (skill, q_curl
          ticks), then rolls at the target (`MoveToTarget` q_speed, skill_roll held) until he hits it: q_dmg + q_ap% AP
          to every enemy within q_r, knocked back (Knockback q_kb_speed x q_kb_t = League's 125 units) and slowed
          q_slow% for q_slow_t; he bounces out of the ball (skill_hit) and keeps `q_on` for r_link ticks. League's ball
          rolls for up to 6 s, accelerating, wherever the player steers it: data cannot change the walk or idle
          picture while he moves, so the main pack rolls only inside the skill; the add-on rolls League's way (the
          whole body a ball while he walks, speeding up, until he touches an enemy).
  skill2  E Frenzying Taunt (狂乱嘲讽), `Targeting` on `EnemyChampion` (e_range): on e_rel the target is taunted for e_taunt
          ticks (League 1.2-2.0 s; its damage to monsters is left out: the AI keeps E for champions).
  ult     R Soaring Slam (冲天猛撞), `Targeting` on `EnemyChampion` (r_range): he hops up and lands on the target
          (`MoveToTarget` r_speed, ult held): r_dmg + r_ap% AP to every enemy within r_r and r_slow% slow for r_slow_t;
          r_pulses aftershocks on the landing spot every r_pp ticks repeat the slow. Within r_link ticks of a Powerball
          hit (League: cast during Powerball) the centre (r_c) also takes Q's damage again and is knocked up r_up ticks.
  watch   A life-long `AddCasted` started by his first attack or cast of each life (`init`), every watch_p ticks: casts W.
The add-on copy (--native, addons/league_rammus): the passive league_rammus:shell pays Spiked Shell and W's return from
his armour and makes Powerball League's rolling ball (skill only curls him up and sets `q_ball`; the add-on shows the
ball and rolls him into the first enemy, then calls the impact `q_hit` itself).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_rammus.data_champion")
ID = "league_rammus"
FX = "asset/league/effects/league_rammus_fx"
BIG = "asset/league/effects/league_rammus_big"

# League units x 100 = ours for skill ranges (the pack's melee attack is 25000 against League's 125). Release ticks will
# come from the strips (tools/art/rig_rammus.py MS). League's Rammus (V25): 675 +105 hp, 55 +3.5 AD, 35 +4.3 armour,
# 32 +2.05 MR, 335 move, attack speed 0.656.
P = {
    # stats (base tanks: attack 80 +6, hp 1100 +120, defence 40 +10, mr 30 +5; his armour is his trademark)
    "hp": 1100, "hp_g": 120, "atk": 72, "atk_g": 6, "mp": 30, "mp_g": 15, "def": 44, "def_g": 11, "mr": 30, "mr_g": 5,
    "ms": 1000, "ms_g": 11,
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 70, "a_hit": 9, "f_t": 180,
    # passive Spiked Shell (League: 10 + 15% armour magic on every attack)
    "p_dmg": 10, "p_ap": 20, "p_hp": 1,
    # W Defensive Ball Curl (League: +22-52 armour +22.5-67.5% bonus armour, the same in MR, 7 s, returns 15 + 10% armour
    # + 10% MR magic to attackers, cd 7 s after it ends)
    "w_cd": 840, "w_go": 30000, "w_dur": 16, "w_t": 420, "w_def": 40, "w_ref": 15,
    # Q Powerball (League: rolls up to 6 s, 155-? move speed accelerating, 80-240 + 100% AP r 250 on impact, knock-back
    # 125, slow 40-80% 1 s, cd 12-6)
    "q_cd": 480, "q_range": 45000, "q_curl": 12, "q_speed": 4000, "q_roll": 120, "q_end": 14, "q_r": 18000,
    "q_dmg": 70, "q_ap": 100, "q_slow": 40, "q_slow_t": 60, "q_kb_speed": 2500, "q_kb_t": 5,
    # E Frenzying Taunt (League: 325 range, taunt 1.2-2.0 s, cast 0.25 s, cd 12)
    "e_cd": 720, "e_range": 32500, "e_dur": 20, "e_rel": 8, "e_taunt": 75,
    # R Soaring Slam (League: 800 range (+ move speed), 100-300 + 60% AP r 400, slow 40-80% 1.5 s, 3 aftershocks over
    # 3.5 s; during Powerball the centre r 200 takes Q's damage and is knocked up 0.75 s; cd 120-90)
    "r_cd": 3600, "r_range": 60000, "r_dur": 36, "r_speed": 4000, "r_end": 14, "r_r": 36000, "r_c": 18000,
    "r_dmg": 100, "r_ap": 60, "r_slow": 40, "r_slow_t": 90, "r_up": 45, "r_pulses": 3, "r_pp": 70, "r_link": 90,
    # the watch
    "watch_p": 12,
    # his sounds, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_rammus
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


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def ap(dmg, ratio, hp=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "can_crit": False}


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


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def anchor(name, *end):
    """League_ekko's anchor: a 1-unit line that ends on his own spot the tick it starts; its end_effects act there."""
    return {"type": "LinearProjectile", "name": n(name), "speed": 1, "range": 1, "y_offset": 5000, "penetrate": True,
            "shape": circle(1000), "applied_target": "EnemyChampion", "applied_effects": [], "end_effects": list(end)}


def voice(name, p):
    """His sound, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def build(p):
    nat = bool(p["native"])
    marked = [refresh("fight", p["f_t"])]
    slow = lambda name, pct, t: buff(name, t, move_speed_mult=-pct)

    # ------------------------------------------------------------------ W: Defensive Ball Curl (cast by the watch)
    curl = combine(flag("w_cd", p["w_cd"]), refresh("busy", p["w_dur"]), anim("skill_w", p["w_dur"]), sfx("w"),
                   voice("vo_w", p), cview("w_cast"),
                   refresh("w_on", p["w_t"], defence_mult=p["w_def"], magic_resistance_mult=p["w_def"],
                           **({} if nat else {"damage_reflect": p["w_ref"]})))
    watch = on_me(casted(1000000, p["watch_p"],
                         sw("w_cd", NONE, sw("busy", NONE, pick(p["w_go"], "EnemyChampion", on_me(curl))))))
    life = sw("init", NONE, combine(flag("init", None), watch))

    # ------------------------------------------------------------------ attack: the claw swipe + Spiked Shell
    shell = native("shell") if nat else ap(p["p_dmg"], p["p_ap"], p["p_hp"])
    blow = combine(sfx("a_swing"), homing("a_blow", "Enemy", [attack(0, 100), shell, view("a_hit"), tsfx("a_hit")]),
                   homing("a_twin", "EnemyChampion", marked))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(life, delayed(p["a_hit"] - 1, blow)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Powerball
    q_hit = [anim("skill_hit", p["q_end"]), *rm("q_ball"), refresh("q_on", p["r_link"]), sfx("q_hit"),
             cview("q_burst"),
             around(p["q_r"], "EnemyWithoutTower", [ap(p["q_dmg"], p["q_ap"]),
                                                     {"type": "Knockback", "speed": p["q_kb_speed"],
                                                      "tick": p["q_kb_t"]},
                                                     slow("q_slow", p["q_slow"], p["q_slow_t"]), view("q_hit")]),
             around(p["q_r"], "EnemyChampion", marked)]
    if nat:
        # the add-on rolls him (the ball while he walks) and runs q_hit itself through a 1-tick `q_go` flag it lays
        roll = [refresh("q_ball", p["q_roll"] * 3)]
    else:
        roll = [refresh("q_ball", p["q_roll"]), anim("skill_roll", p["q_roll"]), sfx("q_roll"),
                {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] + 60000, "end_effects": q_hit}]
    skill = action("skill", p["q_curl"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(life, refresh("busy", p["q_curl"] + 10), sfx("q"), voice("vo_q", p),
                           delayed(p["q_curl"] - 1, alive(*roll))))

    # ------------------------------------------------------------------ skill2: E Frenzying Taunt
    taunt = [{"type": "Taunt", "duration": p["e_taunt"]}, buff("e_taunt", p["e_taunt"]), view("e_hit"),
             tsfx("e_hit")] + marked
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(life, refresh("busy", p["e_dur"]), sfx("e"), voice("vo_e", p),
                            delayed(p["e_rel"] - 1, alive(homing("e_taunt", "EnemyChampion", taunt)))))

    # ------------------------------------------------------------------ ult: R Soaring Slam
    shock = [slow("r_slow", p["r_slow"], p["r_slow_t"]), view("r_hit")]
    after = anchor("r_anchor", field("r_after", p["r_r"], p["r_pulses"] * p["r_pp"], p["r_pp"], shock),
                   *[delayed(k * p["r_pp"], view("r_shock")) for k in range(1, p["r_pulses"] + 1)])
    centre = sw("q_on", around(p["r_c"], "EnemyWithoutTower", [ap(p["q_dmg"], p["q_ap"]),
                                                                {"type": "Airborne", "duration": p["r_up"]}]))
    land = [anim("ult_land", p["r_end"]), sfx("r_land"), view("r_land"),
            around(p["r_r"], "EnemyWithoutTower", [ap(p["r_dmg"], p["r_ap"]), *shock, tsfx("r_hit")]),
            around(p["r_r"], "EnemyChampion", marked), centre, *rm("q_on"), after]
    ult = action("ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(life, refresh("busy", p["r_dur"] + p["r_end"]), anim("ult", p["r_dur"]), sfx("r"),
                         voice("vo_r", p), flag("r_air", p["r_dur"], cc_immune=True),
                         {"type": "MoveToTarget", "speed": p["r_speed"], "range": 400000, "end_effects": land}))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_e = [E("a_hit"), E("q_hit"), E("q_burst", BIG, -1), E("e_hit"), E("w_cast", BIG, 2),
               E("r_land", BIG, -1, False), E("r_shock", BIG, -1, False), E("r_hit")]
    views_b = [B_("w_on", FX, 3), B_("e_taunt", FX, 3), B_("q_slow", FX, 3), B_("r_slow", FX, 3)]
    extra = {}
    if nat:
        extra["passive"] = {"passive_ref": f"{ID}:shell", "params": {
            k: p[k] for k in ("p_dmg", "w_ref", "q_speed", "q_roll", "q_r")}}
        skill["effect"]["effects"].append(sw("q_go", combine(*rm("q_go"), *q_hit)))
    return {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Tank", "CC"], **extra,
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
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
