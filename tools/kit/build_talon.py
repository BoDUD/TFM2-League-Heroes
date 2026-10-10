"""Build league_talon.data_champion (mid, Assassin) from the parameters P.

    python tools/kit/build_talon.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-10: mid, Assassin, League's whole kit with the pros' combos). TFM2 has three active slots:
Rake is `skill` (the combo opener), Noxian Diplomacy `skill2`, Shadow Assault the `ult`; Assassin's Path runs on its own.
  passive Blade's End (刀锋之末): League wounds a champion with each spell hit, three wounds and his next attack makes
          it bleed. Nothing reads a target's buffs, so the wounds are counted on him (league_zed's mark ladder): each
          spell of his that hits a champion (Rake out, Rake back, Noxian Diplomacy, the blades out and back) climbs
          p_1..p_3 (p_t ticks, renewed) and marks that champion (`p_wound`, the picture); with p_3 his next attack on a
          champion bleeds it - p_dmg + p_ratio% AD over p_bleed ticks - and starts p_cd.
  attack  The wrist-blade slash, the hit on tick a_st.
  skill   W Rake (斩草除根): on `EnemyWithoutTower` within w_range: a fan of blades flies w_len (w_dmg + w_ratio% AD to
          every enemy on the way), waits w_wait ticks and flies back to him (`BackToCasterLinearProjectile`: w2_dmg +
          w2_ratio% AD and a w_slow% slow for w_slow_t to everything it passes). With Noxian Diplomacy ready the cast
          goes straight on (the pros' W -> Q): he leaps on the target as the blades turn back - out, back and the leap
          make the three wounds, and his next attack bleeds.
  skill2  Q Noxian Diplomacy (诺克萨斯式外交): on `EnemyWithoutTower` within q_range: with an enemy within q_melee he stabs
          (a critical strike: q_crit% of q_dmg + q_ratio% AD), else he leaps onto the target (`MoveToTarget`) and hits
          for q_dmg + q_ratio% AD. A kill heals him q_heal and refunds the cooldown (League 50%: a 2-tick
          `skill_cooldown_mult` q_reset, the ult kept out by an equal negative `ult_cooldown_mult`).
  E       Assassin's Path (刺客之道, automatic): TFM2's arena has no walls, so the vault is League's way out after the
          all-in: when the blades come back or a Q kills, with e_crowd enemy champions within e_safe_r and e_cd off, he
          vaults away from one (`MoveBack` e_speed x e_tick) and runs e_haste% faster for e_haste_t.
  ult     R Shadow Assault (刀锋涌动): on `EnemyChampion` within r_range: a ring of blades flies out (r_dmg + r_ratio%
          AD to everything within r_r), he turns invisible (`CasterInvisible` r_inv) and runs r_haste% faster; the
          blades come back to him (the same damage round him) when the stealth ends - or at once on his next attack
          or Noxian Diplomacy hit, as League's attack / Q break the stealth (they raise r_brk, the ult polls it).
  combos  W -> Q (one cast, above); R -> Q -> attack (the stealthed leap converges the blades, the third wound bleeds);
          the vault out when outnumbered (E).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_talon.data_champion")
ID = "league_talon"
FX = "asset/league/effects/league_talon_fx"
BIG = "asset/league/effects/league_talon_big"

# Timings from the strips (assets/source/talon/poses.json): the stab hits on tick 7 (attack frame 3), Rake's blades
# leave on tick 6 (skill frame 3), the melee spin slash on tick 6 (skill2_stab frame 3), the blades fly out on tick 6
# (ult frame 3); the vault plays 20 ticks.
P = {
    # stats (Assassin base: attack 120 +30, hp 900 +80, defence 25, mr 15, move 1100, range 23000); League's Talon:
    # 658 +109 hp, 68 AD +3.1, 30 armour, 335 move, 125 range
    "hp": 930, "hp_g": 88, "atk": 122, "atk_g": 25, "def": 26, "def_g": 8, "mr": 18, "mr_g": 4, "ms": 1100, "ms_g": 13,
    # attack: the wrist blade
    "atk_range": 23000, "atk_dur": 25, "atk_cd": 55, "a_st": 7,
    # passive Blade's End (League: 75-160 + 210% bonus AD bleed over 2 s, 10 s per target)
    "p_t": 300, "p_dmg": 40, "p_ratio": 120, "p_bleed": 120, "p_period": 20, "p_cd": 600,
    # Q Noxian Diplomacy (League: 575 leap range, 65-165 + 110% bonus AD, melee crit, cd 8-6 s; a kill heals and
    # refunds 50%)
    "q_cd": 300, "q_dur": 18, "q_go": 5, "q_range": 40000, "q_melee": 26000, "q_speed": 6000, "q_dmg": 48,
    "q_ratio": 100, "q_crit": 150, "q_heal": 60, "q_reset": 100,
    # W Rake (League: 900 range, out 50-90 + 40% bonus AD, back 50-130 + 90% bonus AD, 40-60% slow 1 s, cd 9 s)
    "w_cd": 540, "w_dur": 18, "w_at": 6, "w_range": 50000, "w_len": 55000, "w_speed": 5000, "w_back_speed": 5000,
    "w_rad": 12000, "w_y": 3000, "w_wait": 6, "w_dmg": 30, "w_ratio": 40, "w2_dmg": 40, "w2_ratio": 70, "w_slow": 40,
    "w_slow_t": 60,
    # E Assassin's Path (League: a vault, cd 2 s per wall; here the way out)
    "e_on": 1, "e_cd": 600, "e_safe_r": 40000, "e_crowd": 2, "e_speed": 3000, "e_tick": 12, "e_anim": 20, "e_haste": 30,
    "e_haste_t": 90,
    # R Shadow Assault (League: 550 radius, 90-270 + 100% bonus AD out and back, 2.5 s stealth, 40-60% haste, cd 100 s)
    "r_cd": 3000, "r_dur": 20, "r_at": 6, "r_range": 30000, "r_r": 30000, "r_dmg": 55, "r_ratio": 75, "r_inv": 150,
    "r_haste": 40,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
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


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def heal(amount):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, radius, y, target, penetrate, effects):
    """y: kept for the call sites; the engine reads no y_offset on a returning projectile."""
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": 400000,
            "penetrate": penetrate, "shape": circle(radius), "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ Blade's End: the wounds
    climb = sw("p_3", refresh("p_3", p["p_t"]),
               sw("p_2", combine(*rm("p_2"), refresh("p_3", p["p_t"])),
                  sw("p_1", combine(*rm("p_1"), refresh("p_2", p["p_t"])), refresh("p_1", p["p_t"]))))

    def wound():
        """On a champion a spell of his hit: its mark, and a wound on his count."""
        return [buff("p_wound", p["p_t"]), on_me(climb)]

    k = p["p_bleed"] // p["p_period"]
    bleed = homing("p_hit", 100000, 0, "EnemyChampion",
                   [view("p_bleed"), tsfx("p_bleed"),
                    casted(p["p_bleed"] + 1, p["p_period"], attack(p["p_dmg"] // k, p["p_ratio"] // k), kind="Bleed"),
                    on_me(*rm("p_1", "p_2", "p_3"), flag("p_cd", p["p_cd"]))])
    blades_end = sw("p_3", sw("p_cd", NONE, bleed))

    # ------------------------------------------------------------------ E Assassin's Path (the way out)
    def vault():
        """With e_crowd enemy champions within e_safe_r and E ready, the vault away from one of them."""
        if not p["e_on"]:
            return NONE
        count = combine(*rm("en1", "en2"), around(p["e_safe_r"], "EnemyChampion",
                                                  [on_me(sw("en1", flag("en2", 2), flag("en1", 2)))]))
        hop = pick(p["e_safe_r"], "EnemyChampion",
                   {"type": "MoveBack", "speed": p["e_speed"], "tick": p["e_tick"]})
        go = combine(flag("e_cd", p["e_cd"]), anim("skill_e", p["e_anim"]), cview("e_vault"), sfx("e"),
                     voice("vo_e", p), hop, refresh("e_haste", p["e_haste_t"], move_speed_mult=p["e_haste"]))
        crowd = "en2" if p["e_crowd"] >= 2 else "en1"
        return sw("e_cd", NONE, combine(count, sw(crowd, go)))

    # ------------------------------------------------------------------ R: the blades come back
    converge = combine(*rm("r_on"), cview("r_back"), sfx("r_back"),
                       around(p["r_r"], "EnemyWithoutTower", [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"),
                                                              tsfx("r_hit")]),
                       around(p["r_r"], "EnemyChampion", wound()),
                       vault())
    # his attack / Q hit only raise r_brk; the ult polls it every 2 ticks (the ult's tree is not cloned each tick)
    break_r = refresh("r_brk", 3)

    # ------------------------------------------------------------------ the attack
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"),
                              delayed(p["a_st"] - 1, homing("a_hit", 100000, 0, "EnemyWithoutTower",
                                                           [attack(0, 100), view("a_hit"), tsfx("a_hit")]),
                                      blades_end, break_r)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q Noxian Diplomacy
    def q_blow(pct):
        """The blow on the target (the leap's end, or the stab's homing): damage, the wound, the kill check
        (league_darius R: q_kill set before the blow, cleared a tick later by a Delayed on the target - nothing but
        pictures runs on a dead one - and read on him 4 ticks after)."""
        reward = combine(*rm("q_kill", "q_cd"), refresh("q_reset", 2, skill_cooldown_mult=p["q_reset"],
                                                         ult_cooldown_mult=-p["q_reset"]),
                         heal(p["q_heal"]), cview("q_heal"), vault())
        return [*rm("q_kill"), flag("q_kill", 20),
                attack(p["q_dmg"] * pct // 100, p["q_ratio"] * pct // 100), view("q_hit"), tsfx("q_hit"),
                {"type": "Delayed", "tick": 1, "effects": [casted(3, 1, *rm("q_kill"))]},
                homing("q_twin", 100000, 0, "EnemyChampion", wound()),
                on_me(break_r, delayed(4, sw("q_kill", reward)))]

    def noxian(lead):
        """From tick lead: the stab when an enemy stands within q_melee, else the leap."""
        near = pick(p["q_melee"], "EnemyWithoutTower", flag("q_near", 2))
        stab = combine(anim("skill2_stab", p["q_dur"]), sfx("q_stab"),
                       delayed(p["q_go"], homing("q_stab", 100000, 0, "EnemyWithoutTower", q_blow(p["q_crit"]))))
        leap = combine(anim("skill2", p["q_dur"]), cview("q_leap"),
                       {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] + 20000,
                        "end_effects": q_blow(100)})
        return combine(delayed(lead, near),
                       delayed(lead + 1, voice("vo_q", p), sw("q_near", stab, combine(sfx("q"), leap))),
                       flag("q_cd", p["q_cd"]))

    # ------------------------------------------------------------------ W Rake
    def rake(lead):
        back_ = back("w_back", p["w_back_speed"], p["w_rad"], p["w_y"], "EnemyWithoutTower", True,
                     [attack(p["w2_dmg"], p["w2_ratio"]), buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
                      view("w_hit"), tsfx("w_hit2")])
        twin_back = back("w_twin2", p["w_back_speed"], p["w_rad"], p["w_y"], "EnemyChampion", False, wound())
        out = line("w_out", p["w_speed"], p["w_len"], p["w_rad"], p["w_y"], "EnemyWithoutTower", True,
                   [attack(p["w_dmg"], p["w_ratio"]), view("w_hit"), tsfx("w_hit")],
                   [delayed(p["w_wait"], sfx("w_back"), back_, twin_back)])
        twin = line("w_twin", p["w_speed"], p["w_len"], p["w_rad"], p["w_y"], "EnemyChampion", False, wound())
        return delayed(lead + p["w_at"] - 1, sfx("w"), out, twin)

    # the slots are 3-tick actions whose CasterAnimations hold him (league_zed), their cooltimes the real ones
    skill = action("skill", 3, p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
                   combine(anim("skill", p["w_dur"]), voice("vo_w", p), rake(0),
                           # the pros' W -> Q: the leap as the blades turn back
                           sw("q_cd", NONE, noxian(p["w_dur"] - 1))))

    skill2 = action("skill2", 3, p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                    sw("q_cd", NONE, noxian(0)))

    # ------------------------------------------------------------------ R Shadow Assault
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(anim("ult", p["r_dur"]), voice("vo_r", p),
                         delayed(p["r_at"] - 1, sfx("r"), cview("r_out"),
                                 around(p["r_r"], "EnemyWithoutTower", [attack(p["r_dmg"], p["r_ratio"]),
                                                                        view("r_hit"), tsfx("r_hit")]),
                                 around(p["r_r"], "EnemyChampion", wound())),
                         {"type": "CasterInvisible", "tick": p["r_inv"]},
                         refresh("r_on", p["r_inv"] + 2, move_speed_mult=p["r_haste"]),
                         on_me(*rm("r_brk"), casted(p["r_inv"], 2, sw("r_on", sw("r_brk", converge))),
                               delayed(p["r_inv"], sw("r_on", converge)))))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring); every
    # such picture here is left-right symmetric
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, tag=None, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": tag or name,
                                                "repeat": True, "z": z}
    views_p = [P_("w_out"), P_("w_back")]
    views_e = [E("a_hit"), E("q_hit"), E("q_leap", FX, -1, False), E("q_heal", FX, 3, False), E("w_hit"),
               E("e_vault", FX, -1, False), E("r_out", BIG, 3, False), E("r_back", BIG, 3, False), E("r_hit"),
               E("p_bleed", FX, 3)]
    views_b = [B_("p_wound", "p_wound", FX, 4), B_("w_slow", "w_slow", FX, 3), B_("e_haste", "e_haste", FX, -1),
               B_("r_on", "r_on", FX, -1)]
    return {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
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
