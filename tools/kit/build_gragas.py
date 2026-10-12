"""Build league_gragas.data_champion (jungle, Melee AP tank) from the parameters P.

    python tools/kit/build_gragas.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-12: jungle / Melee AP tank; Q on the attack slot's side as skill, E with W after it as
skill2, R behind the target, the passive in the main pack, the pros' combos, a native add-on for R's landing spot):
  passive Happy Hour (欢乐时光): every skill he casts first takes a swig - a heal of p_heal (p_heal3 from level 3) +
          p_ap% AP - then rests p_cd ticks (League: 5.5% max health every 12 s; no heal reads max health, so the amount
          is flat and stepped once by level).
  attack  A punch, the hit a_st ticks in. While Drunken Rage holds (w_on) the punch bursts: every enemy within w_r of
          the target takes w_dmg + w_ratio% AP magic, enemy champions also w_hp% of their max health (true: no magic
          damage reads max health), and the flag is spent.
  skill   Q Barrel Roll (滚动酒桶): a `Position` cast on `EnemyWithoutTower` (q_range): the barrel is lobbed (q_fly ticks)
          to where the unit stood, sits there q_wait ticks and bursts: every enemy within q_r takes q_dmg + q_ratio% AP
          and is slowed q_slow% for q_slow_t. Thrown while e_combo holds (his body slam stunned a champion), it bursts
          the tick it lands.
  skill2  E Body Slam (肉弹冲击): a `Targeting` cast on `EnemyWithoutTower` (e_range): he charges at the target
          (`RushTime`, e_speed a tick for at most e_tick ticks) and stops on the first enemy in his way: every enemy
          within e_r takes e_dmg + e_ratio% AP and is stunned e_stun ticks; a hit takes e_refund% off the cooldown
          (`skill_cooldown_mult`, Q too), a champion hit opens e_combo. Then W Drunken Rage (醉酒狂暴): he drinks
          (the strip's drink frames): w_dr% less damage for w_dr_t ticks and w_on (w_t ticks) on his next punch.
  ult     R Explosive Cask (爆破酒桶): a `Targeting` cast on `EnemyChampion` (r_range): the cask is lobbed (r_fly ticks)
          to where the champion stood and blows up: every enemy within r_r takes r_dmg + r_ratio% AP and is flung
          toward him (`Grab`: r_grab a tick for r_grab_t ticks) - the target and those behind it into his team, as the
          cask landing behind the target does in League. Data cannot put a point behind a unit (a line or a lob started
          from another projectile's `end_effects` still runs from the caster, measured 2026-10-12), so the main pack
          lands it on the target; with native=1 (the copy for addons/league_gragas) league_gragas:cask reads every
          enemy's position and lands it behind the spot that flings the most of them (back line first) toward his team.
  combos  E -> Q: Q thrown within e_combo bursts on landing. R -> E: the flung champions come to him, where the AI's
          next body slam (cast as soon as one stands in e_range) stuns them. The empowered punch is his next one,
          whoever it hits.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_gragas.data_champion")
ID = "league_gragas"
FX = "asset/league/effects/league_gragas_fx"
BIG = "asset/league/effects/league_gragas_big"

# Timings (placeholders until the strips are drawn): the punch lands on tick 10, the barrel leaves the hand on tick 12,
# the charge starts on tick 4 of skill2 and the drink is its tail, the cask is thrown on tick 14.
P = {
    # stats (Melee tank: attack 80 +6, hp 1100 +120, defence 40, mr 30); League's Gragas: 640 +115 hp, 64 AD +3.5,
    # 38 armour, 32 mr, 330 move, 125 range - an AP tank jungler like league_amumu and league_malphite
    "hp": 1100, "hp_g": 120, "atk": 72, "atk_g": 6, "mp": 30, "mp_g": 15, "def": 38, "def_g": 9, "mr": 30, "mr_g": 5,
    "ms": 1000, "ms_g": 10,
    # attack: a punch
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 70, "a_st": 10,
    # passive Happy Hour (League: 5.5% max health on a spell cast, 12 s)
    "p_heal": 55, "p_heal3": 85, "p_ap": 20, "p_cd": 720,
    # Q Barrel Roll (League: 850 range, radius 250, 80-240 + 70% AP, slow 40-60% 2 s, cooked 2 s at most, cd 11-6 s)
    "q_cd": 420, "q_range": 58000, "q_dur": 28, "q_at": 12, "q_fly": 22, "q_wait": 45, "q_r": 19000,
    "q_dmg": 80, "q_ratio": 70, "q_slow": 40, "q_slow_t": 120,
    # E Body Slam (League: 600 dash at 900, 80-260 + 60% AP, stun 1 s, cd 14-12 s, 40% back on a hit)
    "e_cd": 600, "e_range": 42000, "e_dur": 44, "e_at": 4, "e_speed": 3200, "e_tick": 12, "e_r": 20000,
    "e_dmg": 70, "e_ratio": 60, "e_stun": 60, "e_refund": 66, "e_combo": 120,
    # W Drunken Rage (League: 10-30% damage reduction 2.5 s; the next attack 7% max health + 20-170 + 70% AP, r 250)
    "w_at": 26, "w_dr": 20, "w_dr_t": 150, "w_t": 300, "w_r": 17000, "w_dmg": 40, "w_ratio": 50, "w_hp": 6,
    # R Explosive Cask (League: 1000 range, radius 350, 200-400 + 80% AP, knock-back 900, cd 100-70 s)
    "r_cd": 3000, "r_range": 70000, "r_dur": 36, "r_at": 14, "r_fly": 16,
    "r_r": 26000, "r_dmg": 160, "r_ratio": 80, "r_grab": 3000, "r_grab_t": 12,
    
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_gragas: the cask lands where league_gragas:cask says
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
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


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


def true_hp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def heal(amount, ap):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def alive(*effects):
    """Effects that run only while he lives (a dead caster's `Delayed` effects still run in the game)."""
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": list(effects)}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, fly, target, end):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": fly, "range": 400000,
            "shape": circle(1000), "range_effect_name": "", "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, apply, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": apply, "apply": apply,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


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
    # ------------------------------------------------------------------ passive Happy Hour: a swig on every skill
    swig = sw("p_cd", NONE, combine(flag("p_cd", p["p_cd"]), sfx("p"), cview("p_heal"),
                                    on_me({"type": "SwitchByLevel3", "effect_start": heal(p["p_heal"], p["p_ap"]),
                                           "effect_level3": heal(p["p_heal3"], p["p_ap"])})))

    # ------------------------------------------------------------------ attack (+ Drunken Rage's burst)
    rage = combine(*rm("w_on"), tsfx("w_hit"), view("w_hit"),
                   around(p["w_r"], "EnemyWithoutTower", [magic(p["w_dmg"], p["w_ratio"])]),
                   around(p["w_r"], "EnemyChampion", [true_hp(p["w_hp"])]))
    # the burst is centred on him (`AroundCaster`): he stands in melee range, so w_r reaches round the target
    punch = combine(sfx("a_swing"), attack(0, 100), view("a_hit"), tsfx("a_hit"), sw("w_on", rage))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy", punch,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Barrel Roll
    slow = buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"])
    burst_hits = [magic(p["q_dmg"], p["q_ratio"]), slow, view("q_hit")]

    def burst(wait):
        return [view("q_land" if wait > 1 else "q_boom"), sfx("q_boom") if wait == 1 else NONE,
                zone("q_blast", p["q_r"], wait, "EnemyWithoutTower", burst_hits),
                delayed(wait - 1, view("q_boom"), sfx("q_boom")) if wait > 1 else NONE]
    barrel = lob("q_barrel", p["q_fly"], "EnemyWithoutTower",
                 [sw("e_combo", combine(*burst(1)), combine(*burst(p["q_wait"])))])
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Position", "EnemyWithoutTower",
                   combine(swig, voice("vo_q", p), delayed(p["q_at"], sfx("q"), barrel)))

    # ------------------------------------------------------------------ skill2: E Body Slam, then W Drunken Rage
    def slam_hits(open_combo):
        return [tsfx("e_hit"), view("e_hit"),
                around(p["e_r"], "EnemyWithoutTower", [magic(p["e_dmg"], p["e_ratio"]),
                                                      {"type": "Stun", "duration": p["e_stun"]},
                                                      buff("e_stun", p["e_stun"])]),
                *([around(p["e_r"], "EnemyChampion", [on_me(refresh("e_combo", p["e_combo"]))])]
                  if open_combo else [])]
    slam = rush(p["e_speed"], p["e_tick"], "EnemyWithoutTower",
                [*slam_hits(True), on_me(flag("e_refund", 2, skill_cooldown_mult=p["e_refund"]))])
    drink = delayed(p["w_at"], alive(sfx("w"), voice("vo_w", p), cview("w_drink"), refresh("w_on", p["w_t"]),
                                     refresh("w_dr", p["w_dr_t"], damaged_reduce=p["w_dr"])))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(swig, voice("vo_e", p),
                            delayed(p["e_at"], sfx("e"), cview("e_dust"), slam), drink))

    # ------------------------------------------------------------------ ult: R Explosive Cask
    flung = [magic(p["r_dmg"], p["r_ratio"]), {"type": "Grab", "speed": p["r_grab"], "tick": p["r_grab_t"]},
             view("r_hit"), tsfx("r_hit")]
    blast = [view("r_boom"), sfx("r_boom"), zone("r_blast", p["r_r"], 1, "EnemyWithoutTower", flung)]
    cask = lob("r_cask", p["r_fly"], "EnemyChampion", blast)
    aim = [{"type": "Native", "effect_ref": "league_gragas:cask"}] if p["native"] else [cask]
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(swig, sfx("r"), voice("vo_r", p), delayed(p["r_at"], *aim)))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("q_barrel"), P_("r_cask", BIG)]
    views_e = [E("a_hit"), E("w_hit", BIG), E("q_hit"), E("q_land", FX, 1, False), E("q_boom", BIG, 2, False),
               E("e_hit"), E("e_dust", FX, -1, False), E("w_drink"), E("p_heal"), E("r_hit"),
               E("r_boom", BIG, 2, False)]
    views_b = [B_("q_slow", FX, -1), B_("e_stun", FX, 3), B_("w_on", FX, 3)]
    return {
        "id": ID, "category": "Melee", "tags": ["AP", "Magic", "Melee", "Tank", "CC", "Heal"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["mp"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["mp_g"], "hp": p["hp_g"], "defence": p["def_g"],
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
