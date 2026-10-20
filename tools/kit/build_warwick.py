"""Build league_warwick.data_champion (jungle, Melee: the werewolf of Zaun) from the parameters P.

    python tools/kit/build_warwick.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-20: layout A - Q / E / R, the passive and W in the attack -, jungle, an add-on; 「有连招要做连招」):
  passive Eternal Hunger (血之饥渴): every attack hit deals p_dmg bonus magic damage and heals him p_heal (League heals
          only below 50% health, three times below 25%: no data effect reads health, so the add-on's copy heals by his
          health - league_warwick:hunger - and the main pack heals a little on every hit).
  W       Blood Hunt (鲜血追猎), no slot of its own: League's hunt of wounded champions. The main pack: every attack hit
          on an enemy champion refreshes `w_hunt` (w_t ticks: w_as% attack speed, w_ms% move speed) - he hunts whoever
          he bites. The add-on reads health: the bonuses only toward champions under 50% health (three times under 25%),
          and the AI hook runs him at them.
  attack  The claw swipe: a hidden homing strike (so the hit knows whether it struck a champion) with the passive.
  skill   Q Jaws of the Beast (野兽之口): a `Targeting` cast on `EnemyWithoutTower` (q_range; camps and waves too). He
          lunges onto the target (`MoveToTarget`) and bites: q_dmg + q_ratio% AD + q_hp% of its max health (physical:
          `ApAttack` has no max-health part) and the passive's on-hit; he heals q_heal + q_heal_r% AD (League heals a
          share of the damage dealt; `Heal` reads no damage). COMBO E -> Q -> howl: bitten while Primal Howl's guard
          is up, he howls at once (League recasts E after the bite) - the fear lands where he lands.
  skill2  E Primal Howl (远祖嗥叫): a `Targeting` cast on `EnemyChampion` (e_range: only in a fight). For e_t ticks he
          takes e_red% less damage (`damaged_reduce`), then howls: every enemy within e_r flees (`Fear` e_fear) - or
          sooner, when Q bites (above).
  ult     R Infinite Duress (无尽束缚): a `Direction` cast on `EnemyChampion` (r_cast). He leaps (League: a leap as far
          as 2.5 x his move speed) - a hidden line flies r_range and stops on the FIRST enemy champion, suppressing it
          (`Stun` r_sup) and flying him onto it (`MoveToTarget` from the line's hit, league_briar R); there he holds
          (`CasterAnimation` ult_hold for r_sup ticks: no walking) and claws three times r_gap apart: r_dmg + r_ratio%
          AD, the passive's on-hit and r_heal healing each (League: 3 on-hits, heals 100% of the damage). A leap that
          hits no champion lands nowhere (League leaps the full length anyway; a data leap needs a unit to fly to).
The combos the AI cannot press from data (E before the dive, R -> Q, the hunt of a fleeing champion) are the add-on's
AI hook league_warwick:combo (addons/league_warwick).
Timings: placeholders until tools/art/rig_warwick.py's strips (a frame's start in ticks = ms x 0.06).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_warwick.data_champion")
ID = "league_warwick"
FX = "asset/league/effects/league_warwick_fx"
BIG = "asset/league/effects/league_warwick_big"

# Numbers = the 10-min classic-SDK simulations (C:/t/ww_sim: kd.py 600 8 --lane 1 against the base junglers demon,
# circus blade, hunter, inquisitor and ninja, three lineups, both sides).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30, mr 25, move 1000, range 25000, attack cd 65; the base
    # junglers 120 +30, hp 900 +80, move 1100 +14); League's Warwick: 620 +99 hp, 65 AD, 33 +4.4 armour, 32 +2 mr,
    # 335 move, 125 range, attack speed 0.638
    "hp": 1050, "hp_g": 105, "atk": 92, "atk_g": 18, "def": 32, "def_g": 7, "mr": 25, "mr_g": 4, "ms": 1050, "ms_g": 12,
    # attack (the claw swipe) + the passive Eternal Hunger (League: 12-46 magic on-hit, heals that much below 50%
    # health, three times below 25%)
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 60, "a_hit": 9, "a_speed": 20000,
    "p_dmg": 20, "p_heal": 8,
    # W Blood Hunt (League: 70-110% attack speed against champions under 50%, 35-55% move speed toward them out of
    # combat, three times under 25%)
    "w_as": 30, "w_ms": 12, "w_t": 120,
    # skill: Q Jaws of the Beast (League: 365 range, 120% AD + 6-10% max health magic, heals 25-45% of it; cd 6 s)
    "q_cd": 360, "q_range": 40000, "q_dur": 30, "q_at": 4, "q_speed": 3000, "q_bite": 12,
    "q_dmg": 30, "q_ratio": 110, "q_hp": 5, "q_heal": 30, "q_heal_r": 40,
    # skill2: E Primal Howl (League: 35-55% damage reduction 2.5 s, then 1 s fear within 375; cd 15-11 s)
    "e_cd": 720, "e_range": 35000, "e_dur": 20, "e_at": 4, "e_red": 40, "e_t": 150, "e_r": 40000, "e_fear": 60,
    "e_howl": 24,
    # ult: R Infinite Duress (League: a leap of 2.5 x move speed, 1.5 s suppression, 175-525 +167% bonus AD magic over 3
    # on-hits, heals 100% of it; cd 110-70 s)
    "r_cd": 3600, "r_cast": 90000, "r_dur": 24, "r_at": 8, "r_range": 95000, "r_speed": 9000, "r_w": 10000,
    "r_fly": 5000, "r_sup": 90, "r_gap": 30, "r_dmg": 50, "r_ratio": 55, "r_heal": 40,
    # the add-on (addons/league_warwick): the passive's heal below 50% / 25% health (League: x1 / x3 of the damage),
    # Blood Hunt's thresholds and its bonuses (x3 under 25%), the hunt's reach
    "p_half": 50, "p_quarter": 25, "p_triple": 3, "w_half": 50, "w_quarter": 25, "w_reach": 150000,
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
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
    return combine(*rm(name), flag(name, tick, **fields))


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


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def magic(dmg, ratio=0):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def heal(amount, ratio=0):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def is_champ(*effects):
    """Inside a projectile's applied effects: the unit it hit, when that is a champion (league_sivir Q)."""
    return pick(1, "EnemyChampion", *effects, fp=True)


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_vex)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, width, target, effects, end=(), penetrate=True):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(width)}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, native=False):
    """native: the add-on's copy (addons/league_warwick) - the passive's heal and Blood Hunt read health there."""
    # ------------------------------------------------------------------ the passive and W, on every strike
    def hunger():
        """Eternal Hunger on the unit struck (inside the strike's applied effects)."""
        if native:
            return [magic(p["p_dmg"]), {"type": "Native", "effect_ref": "league_warwick:hunger"}]
        return [magic(p["p_dmg"]), on_me(heal(p["p_heal"]))]

    hunt = [] if native else [is_champ(refresh("w_hunt", p["w_t"], attack_speed_mult=p["w_as"],
                                               move_speed_mult=p["w_ms"]))]

    # ------------------------------------------------------------------ attack: the claw swipe
    swipe = homing("a_claw", p["a_speed"], "Enemy",
                   [attack(0, 100), *hunger(), *hunt, view("a_hit"), tsfx("a_hit")])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), delayed(p["a_hit"], swipe)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill2's howl (E, or Q's bite under the guard)
    def howl():
        return combine(*rm("e_on"), anim("skill2_howl", p["e_howl"]), sfx("e_howl"), cview("e_howl"),
                       around(p["e_r"], "EnemyWithoutTower", [{"type": "Fear", "tick": p["e_fear"]}, view("e_fear")]))

    # ------------------------------------------------------------------ skill: Q Jaws of the Beast
    bite = [attack(p["q_dmg"], p["q_ratio"], p["q_hp"]), *hunger(), *hunt, view("q_hit"), tsfx("q_hit"),
            on_me(heal(p["q_heal"], p["q_heal_r"]), cview("q_heal"))]
    lunge = {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] + 30000,
             "end_effects": [anim("skill_bite", p["q_dur"] - p["q_bite"])]}
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower", combine(
        anim("skill", p["q_bite"]), sfx("q_cast"), sfx("vo_q"), delayed(p["q_at"], lunge),
        delayed(p["q_bite"], alive(homing("q_jaw", p["a_speed"], "EnemyWithoutTower", bite), sw("e_on", howl())))))

    # ------------------------------------------------------------------ skill2: E Primal Howl
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion", combine(
        anim("skill2", p["e_dur"]), sfx("e_cast"), sfx("vo_e"),
        delayed(p["e_at"], refresh("e_on", p["e_t"], damaged_reduce=p["e_red"])),
        delayed(p["e_at"] + p["e_t"] - 1, alive(sw("e_on", howl())))))

    # ------------------------------------------------------------------ ult: R Infinite Duress
    def claw(i):
        return delayed(i * p["r_gap"] + 1, attack(p["r_dmg"], p["r_ratio"]), *hunger(), view("r_hit"), tsfx("r_hit"),
                       on_me(heal(p["r_heal"])))

    land = [anim("ult_hold", p["r_sup"]), sfx("r_land"), *[claw(i) for i in range(3)]]
    leap = line("r_leap", p["r_speed"], p["r_range"], p["r_w"], "EnemyChampion",
                [{"type": "Stun", "duration": p["r_sup"]}, view("r_bind"), tsfx("r_hit"),
                 anim("ult_dash", 20), {"type": "MoveToTarget", "speed": p["r_fly"], "range": p["r_range"] + 30000,
                                        "end_effects": land}],
                penetrate=False)
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_cast"], "Direction", "EnemyChampion", combine(
        anim("ult", p["r_dur"]), sfx("r_cast"), sfx("vo_r"), delayed(p["r_at"], leap)))

    # ------------------------------------------------------------------ views (tools/art/pack_warwick_fx.py)
    E = lambda name, anim_=FX, z=2, follow=True, tag=None: {"type": "Animation", "name": n(name), "anim": anim_,
                                                            "tag": tag or name, "z": z, "is_follow": follow}
    views_e = [E("a_hit"), E("q_hit"), E("q_heal"), E("e_howl", BIG, -1), E("e_fear"), E("r_bind"), E("r_hit")]
    views_p = []
    views_b = [{"type": "Animated", "name": n("e_on"), "anim": FX, "tag": "e_guard", "repeat": True, "z": 2},
               {"type": "Animated", "name": n("w_hunt"), "anim": FX, "tag": "w_hunt", "repeat": True, "z": -1}]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Heal", "CC"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        kit["passive"] = {"passive_ref": "league_warwick:hunt",
                          "params": {k: int(p[k]) for k in ("p_dmg", "p_half", "p_quarter", "p_triple", "w_as", "w_ms",
                                                            "w_half", "w_quarter", "w_reach", "atk_range", "q_range",
                                                            "e_range", "e_r", "e_t", "r_cast", "r_range", "r_w",
                                                            "r_sup", "r_cd", "r_dur")}}
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
    kit = build(p, native=a.native)
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
