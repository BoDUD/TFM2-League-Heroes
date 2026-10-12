"""Build league_kassadin.data_champion (mid, Melee AP assassin) from the parameters P.

    python tools/kit/build_kassadin.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-12: mid / Melee AP assassin; Q as skill, E Force Pulse as skill2 with Nether Blade's
active on its own cooldown, R Riftwalk to the back line restacking, the passive in the main pack, the pros' combos, a
native add-on addons/league_kassadin for the passive's exact 10%, Force Pulse's real charge and R's landing spot):
  passive Void Stone (虚空之石): a `Permanent` caster buff (p_mr flat + p_mrm% magic resistance, added by any action that
          finds it missing - death clears it) takes about 10% off the magic damage he takes (magic damage is
          x 100 / (100 + resistance); +p_mr and +p_mrm% make it 10-11% at his resistances). League's "ignores unit
          collision" has no field in the data nor in the native API and is left out. With native=1 the add-on's
          passive league_kassadin:void_stone keeps the reduction at exactly 10% (items included) instead.
  attack  A swipe, the hit a_st ticks in; Nether Blade's passive adds a_p + a_p_ratio% AP magic on every hit. Nether
          Blade's active (虚空之刃) rides the attack on its own cooldown (league_jax's Empower way): when w_cd is gone the
          attack plays attack_w and its hit adds w_dmg + w_ratio% AP magic, then w_cd runs again.
  skill   Q Null Sphere (虚无法球): a `Targeting` cast on `EnemyWithoutTower` (q_range, waves and camps too): the orb flies
          (q_speed) and deals q_dmg + q_ratio% AP; a champion it hits is interrupted (a q_int-tick stun) and, inside
          e_combo (his Force Pulse hit a champion), silenced q_sil ticks. He gets a q_sh + q_sh_ap% AP shield for q_sh_t
          ticks at the cast (League: a magic-only shield - the data's shields take every kind of damage, so it is smaller).
  skill2  E Force Pulse (能量脉冲): a `Targeting` cast on `EnemyWithoutTower` (e_range): a cone toward the target (e_r long,
          acos(e_cos/1000) to each side) deals e_dmg + e_ratio% AP and slows e_slow% for e_slow_t; a champion hit opens
          e_combo. League charges it with every spell cast near him; the data reads no one else's casts, so his own Q
          and R casts each take a e_cut refund (`skill_cooldown_mult`, which caps Q's remaining cooldown as well). With
          native=1 the add-on's passive counts every cast within its reach (cooldowns that jump) and cuts E for each.
  ult     R Riftwalk (虚空行走): a `Targeting` cast on `EnemyChampion` (r_range): at r_at he vanishes and appears on a
          random enemy champion within r_reach (the back line about as often as the front; with native=1
          league_kassadin:rift picks the spot - a champion the blast kills, else the most champions in the blast, the
          back line first - and keeps him out of enemy towers' reach); a tick later every enemy within r_r takes r_dmg +
          r_ratio% AP plus r_st + r_st_ratio% AP for each stack. Every cast within r_stack_t of the last adds a stack (at
          most 3 more: League's 4) and refreshes them all. r_cd is short (League: 5 / 3.5 / 2 s).
  combos  R -> E: an E cast within r_combo of the landing pulses on its first tick (no wind-up). E -> Q: the orb silences
          a champion the cone hit (e_combo). The empowered attack is his next one, whoever it hits.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_kassadin.data_champion")
ID = "league_kassadin"
FX = "asset/league/effects/league_kassadin_fx"
BIG = "asset/league/effects/league_kassadin_big"

# Timings are placeholders until the strips (step 2): hits on tick 8 of 24.
P = {
    # stats (Melee AP assassin like league_fizz / league_diana / league_ekko: attack 80 +10, mp 50 +20, hp 920-950);
    # League's Kassadin: 646 +113 hp, 59 AD, 21 armour, 30 mr, 335 move, 150 range
    "hp": 940, "hp_g": 92, "atk": 80, "atk_g": 10, "mp": 50, "mp_g": 20, "def": 26, "def_g": 8, "mr": 22, "mr_g": 4,
    "ms": 1100, "ms_g": 10,
    # attack + Nether Blade's passive (League: +25 (+10% AP) magic on hit)
    "atk_range": 24000, "atk_dur": 24, "atk_cd": 55, "a_st": 8, "a_p": 15, "a_p_ratio": 10,
    # passive Void Stone (League: 10% less magic damage)
    "p_mr": 12, "p_mrm": 11,
    # W Nether Blade active (League: 50-200 + 80% AP on the next attack, cd 7 s)
    "w_cd": 420, "w_dmg": 60, "w_ratio": 70,
    # Q Null Sphere (League: 650 range, 1400 speed, 70-250 + 70% AP, magic shield 50-230 + 40% AP 1.5 s, cd 9-7 s)
    "q_cd": 360, "q_range": 50000, "q_dur": 24, "q_at": 8, "q_speed": 3000, "q_dmg": 90, "q_ratio": 70,
    "q_int": 6, "q_sil": 60, "q_sh": 50, "q_sh_ap": 40, "q_sh_t": 90,
    # E Force Pulse (League: cone 600 / 80 degrees, 45-255 + 75% AP? (data 70%), slow 50-75% 1 s, cd 21-17 s, -1.5 s
    # a spell cast nearby)
    "e_cd": 900, "e_range": 40000, "e_dur": 24, "e_at": 8, "e_r": 42000, "e_cos": 766,
    "e_dmg": 90, "e_ratio": 70, "e_slow": 50, "e_slow_t": 60, "e_combo": 120, "e_cut": 20,
    # R Riftwalk (League: 500 blink, radius 270, 70-110 + 50% AP (+ mana) and 35-55 + 7% AP a stack, 4 stacks 15 s,
    # cd 5 / 3.5 / 2 s)
    "r_cd": 480, "r_range": 48000, "r_reach": 56000, "r_dur": 24, "r_at": 6, "r_r": 20000,
    "r_dmg": 80, "r_ratio": 50, "r_st": 40, "r_st_ratio": 10, "r_stack_t": 900, "r_combo": 120,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_kassadin: native passive (exact 10%, real Force Pulse charge) and R's landing
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


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def cone(radius, cos, target, effects):
    return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}}, "target": target,
            "apply_type": {"Forward": {"offset": 1000}}, "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def orb(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def sweep(name, width, length):
    """The cone's picture: a line zone with no effects, turned toward the target (league_darius E's way)."""
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": 20,
            "apply": 1, "applied_target": "EnemyWithoutTower", "applied_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    native = bool(p["native"])
    # ------------------------------------------------------------------ passive Void Stone (data: a resistance buff)
    stone = None if native else sw("p_on", NONE, flag("p_on", None, magic_resistance=p["p_mr"],
                                                       magic_resistance_mult=p["p_mrm"]))
    # his own casts charge Force Pulse (the add-on counts everyone's instead)
    charge = None if native else on_me(flag("e_charge", 2, skill_cooldown_mult=p["e_cut"]))

    # ------------------------------------------------------------------ attack (+ Nether Blade)
    def hit(empowered):
        return combine(attack(0, 100), magic(p["a_p"], p["a_p_ratio"]), view("a_hit"), tsfx("a_hit"),
                       *([magic(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")] if empowered else []))
    plain = combine(sfx("a_swing"), delayed(p["a_st"] - 1, hit(False)))
    blade = combine(flag("w_cd", p["w_cd"]), anim("attack_w", p["atk_dur"]), sfx("w"), voice("vo_w", p),
                    delayed(p["a_st"] - 1, hit(True)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(stone, sw("w_cd", plain, blade)), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Null Sphere
    q_hits = [magic(p["q_dmg"], p["q_ratio"]), view("q_hit"), tsfx("q_hit")]
    q_champ = [{"type": "Stun", "duration": p["q_int"]},
               sw("e_combo", combine({"type": "BlockSkill", "tick": p["q_sil"]}, buff("q_sil", p["q_sil"])))]
    shield = on_me({"type": "Shield", "amount": p["q_sh"], "attack_ratio": 0, "ap_ratio": p["q_sh_ap"],
                    "tick": p["q_sh_t"]})
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(stone, voice("vo_q", p),
                           delayed(p["q_at"] - 1, sfx("q"), shield, cview("q_shield"), charge,
                                   orb("q_orb", p["q_speed"], "EnemyWithoutTower", q_hits),
                                   orb("q_twin", p["q_speed"], "EnemyChampion", q_champ))))

    # ------------------------------------------------------------------ skill2: E Force Pulse
    e_hits = [magic(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
              view("e_hit")]
    pulse = combine(sfx("e"), voice("vo_e", p), sweep("e_cone", 12000, p["e_r"]),
                    cone(p["e_r"], p["e_cos"], "EnemyWithoutTower", e_hits),
                    cone(p["e_r"], p["e_cos"], "EnemyChampion", [on_me(refresh("e_combo", p["e_combo"]))]))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(stone, sw("r_combo", combine(*rm("r_combo"), pulse), delayed(p["e_at"] - 1, pulse))))

    # ------------------------------------------------------------------ ult: R Riftwalk
    def blast(k):
        return around(p["r_r"], "EnemyWithoutTower",
                      [magic(p["r_dmg"] + k * p["r_st"], p["r_ratio"] + k * p["r_st_ratio"]), view("r_hit")])

    def stacks(k):
        """After a cast at k stacks: k + 1 stacks (at most 3), all refreshed."""
        return [refresh(f"r_s{i}", p["r_stack_t"]) for i in range(1, min(k + 1, 3) + 1)]
    ladder = sw("r_s3", combine(blast(3), *stacks(3)),
                sw("r_s2", combine(blast(2), *stacks(2)),
                   sw("r_s1", combine(blast(1), *stacks(1)), combine(blast(0), *stacks(0)))))
    land = delayed(1, cview("r_in"), sfx("r_hit"), ladder, refresh("r_combo", p["r_combo"]))
    jump = ({"type": "Native", "effect_ref": "league_kassadin:rift"} if native else
            {"type": "RandomTarget", "range": p["r_reach"], "casting_target": "EnemyChampion",
             "from_projectile": False, "effects": [{"type": "Teleport"}]})
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(stone, voice("vo_r", p),
                         delayed(p["r_at"] - 1, sfx("r"), cview("r_out"), charge, jump, land)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("q_orb"), P_("e_cone", BIG, 2)]
    views_e = [E("a_hit"), E("w_hit"), E("q_hit"), E("q_shield"), E("e_hit"), E("r_out", BIG, 2, False),
               E("r_in", BIG, 2, False), E("r_hit")]
    views_b = [B_("e_slow", FX, -1), B_("q_sil", FX, 3)]
    kit = {
        "id": ID, "category": "Assassin", "tags": ["AP", "Magic", "Melee", "CC", "Shield"],
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
        kit["passive"] = {"passive_ref": "league_kassadin:void_stone",
                          "params": {"cool": p["e_cd"], "cut": 90, "reach": 32000, "dr": 10}}
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
