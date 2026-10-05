"""Build league_varus.data_champion (ADC, Range) from the parameters P.

    python tools/kit/build_varus.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-05: all the recommended options):
  attack  An arrow (homing, physical 100% AD) with W Blighted Quiver's on-hit magic damage (w_on) on every unit.
          Blight: his hits on enemy champions climb b_1 -> b_2 -> b_3 (caster flags, b_t ticks, refreshed by every hit;
          nothing reads a stack on the target, so the count is his, as league_kaisa's Plasma), each hit showing the
          stack pips on the target. A champion-only twin of the arrow (same speed and height) carries the ladder.
  detonation  Q, E and R hits on a champion set the stacks off: d_hp% of the target's maximum health per stack as true
          damage (League's 2.5-5.5% magic: nothing magic reads max health) and, for Q and E, the basic cooldowns capped
          at (100 - 13 x stacks)% (a 2-tick skill_cooldown_mult: League's 13% refund per stack); then the count clears.
  passive Living Vengeance: his kill of an enemy champion (league_jinx's kill check on the arrow's, Q's, E's and R's
          champion twins) gives p_as_c% attack speed for p_t ticks; a minion or monster his arrow kills gives p_as_m%.
  skill   Q Piercing Arrow, smart charge: a `Direction` cast on `EnemyWithoutTower`. An enemy champion within q_aim_f at
          the cast -> the full draw (CasterAnimation skill, q_full_t ticks), else the quick draw (skill_quick,
          q_quick_t ticks, q_quick% damage and a shorter arrow). The action itself lasts 3 ticks and the animation holds
          him (league_aatrox Q's pacing). At the release an enemy champion within reach gets the arrow (a straight line
          at where he stands then: dodged by walking off it), else the cast's direction. The arrow pierces; each unit
          after the first takes less (q_fall: 100 / 80 / 60%, counted on caster flags for this arrow).
          W's active Blighted Arrow is folded in: a full draw with w_cd gone adds w_q_hp% max health to the champion it
          detonates on and starts w_cd (League's 40 s).
  skill2  E Hail of Arrows: a `Position` cast on `EnemyWithoutTower` (e_range): the arrows land e_land ticks after the
          release on the cast point (dodgeable): e_dmg + e_ratio% AD round it, then a field for e_field_t ticks that
          slows (e_slow%) and cuts healing (heal_reduce e_grievous) - re-applied every 15 ticks for 15, so it never adds up.
  ult     R Chain of Corruption: a `Targeting` cast on `EnemyChampion`; at the release a tendril flies at where he stands
          (passes minions, stops on the first enemy champion): r_dmg + r_ratio% AD, a r_root-tick root, the detonation
          (no refund) and three blight stacks; r_spread ticks later the corruption spreads round that spot (r_spread_r):
          every enemy champion there is rooted r_root2 ticks and shows the three pips.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_varus.data_champion")
ID = "league_varus"
FX = "asset/league/effects/league_varus_fx"
BIG = "asset/league/effects/league_varus_big"

# Numbers = candidate c6 of the 10-min classic-SDK simulations (vr_sim/sim/kd.py, bottom lane against gunner, soldier,
# archer and gambler, both sides, 2026-10-05): +1.63 on seeds 1-24, +1.91 on seeds 25-48 (the pack's league_jhin
# +1.43 / +2.08, league_sivir +2.50 / +1.83). The draft c0 was +0.82: the attack interval 62 -> 56 and hp 900 -> 950 (c3,
# +1.16 / +1.85), then Q 480 -> 400 and E 540 -> 480 ticks. A bigger Q (140 + 150%: +0.11 on 12 seeds), 4% blight
# (c2 +1.04) or attack 106 (+1.27) did less.
P = {
    # stats (Range base: attack 100 +20, hp 900 +90, defence 20 +7, mr 15 +3, move 900 +9); League's Varus: 575 range
    "hp": 950, "hp_g": 90, "atk": 100, "atk_g": 20, "def": 20, "def_g": 7, "mr": 15, "mr_g": 3, "ms": 900, "ms_g": 9,
    # attack: the arrow leaves the bow on atk_st
    "atk_range": 57500, "atk_dur": 24, "atk_cd": 56, "atk_st": 9, "arrow_speed": 7000, "arrow_y": -3000,
    # W Blighted Quiver: on-hit magic, stacks (b_t ticks), detonation (% max health per stack), refunds per stack count
    "w_on": 20, "b_t": 360, "d_hp": 3, "ref1": 15, "ref2": 35, "ref3": 64,
    # W active folded into Q
    "w_cd": 2400, "w_q_hp": 6,
    # passive
    "k_hold": 40, "k_read": 4, "p_t": 300, "p_as_c": 60, "p_as_m": 20,
    # skill: Q Piercing Arrow (League: 1.25 s charge, 10-430 + 120-150% bonus AD, 925 -> 1525 range, 1900/s, width 70,
    # -15% per unit hit down to 33%, cd 17-11 s)
    "q_cd": 400, "q_range": 95000, "q_full_t": 66, "q_quick_t": 24, "q_rec": 10, "q_aim_f": 130000,
    "q_reach_f": 140000, "q_reach_q": 100000, "q_speed": 6500, "q_rad": 6000, "q_y": -3000,
    "q_dmg": 110, "q_ratio": 130, "q_quick": 60, "q_fall": [100, 80, 60],
    # skill2: E Hail of Arrows (League: 925 range, radius 300, 30-210 + 90-110% bonus AD, slow 25-55% + grievous 40% for
    # 4 s, cd 18-10 s)
    "e_cd": 480, "e_range": 90000, "e_dur": 24, "e_st": 10, "e_land": 20, "e_r": 28000, "e_dmg": 70, "e_ratio": 90,
    "e_field_t": 240, "e_slow": 30, "e_grievous": 40,
    # ult: R Chain of Corruption (League: 1250 range at 1950/s, 150-350 + 100% AP, root 2 s, spreads 600, 3 stacks,
    # cd 100/80/60 s)
    "r_cd": 3600, "r_range": 100000, "r_dur": 30, "r_st": 15, "r_speed": 5500, "r_reach": 115000, "r_rad": 7000,
    "r_y": -3000, "r_dmg": 150, "r_ratio": 80, "r_root": 120, "r_spread": 30, "r_spread_r": 55000, "r_root2": 90,
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
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields},
            "only_to_enemy": False}


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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def true_hp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": 1, "applied_target": target, "applied_effects": [T(e) for e in effects],
            "end_effects": []}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Living Vengeance (kill checks)
    rage_c = combine(*rm("p_rage_m"), refresh("p_rage", p["p_t"], attack_speed_mult=p["p_as_c"]), cview("p_rage_on"),
                     sfx("p_rage"))
    rage_m = sw("p_rage", NONE, refresh("p_rage_m", p["p_t"], attack_speed_mult=p["p_as_m"]))

    def kill_check(src, reward):
        """On a hit unit, around its damage: the flag before, the living target's clear after, the read on him later."""
        k = f"k_{src}"
        return (refresh(k, p["k_hold"]),
                combine(casted(3, 1, *rm(k)), on_me(delayed(p["k_read"], sw(k, combine(*rm(k), reward))))))

    # ------------------------------------------------------------------ Blight: stacks and detonation
    def det(refund, extra=None):
        """On a champion hit by Q, E or R: the stacks go off (true % max health), the refund, the count clears."""
        def burst(k):
            out = [true_hp(p["d_hp"] * k), view(f"b_pop{k}"), tsfx("b_pop")]
            if refund:
                out.append(flag("refund", 2, skill_cooldown_mult=p[f"ref{k}"]))
            return combine(*out)
        return combine(sw("b_3", burst(3), sw("b_2", burst(2), sw("b_1", burst(1)))), *(extra or []),
                       *rm("b_1", "b_2", "b_3"))

    climb = sw("b_3", combine(refresh("b_3", p["b_t"]), view("b_v3")),
               sw("b_2", combine(*rm("b_2"), flag("b_3", p["b_t"]), view("b_v3")),
                  sw("b_1", combine(*rm("b_1"), flag("b_2", p["b_t"]), view("b_v2")),
                     combine(flag("b_1", p["b_t"]), view("b_v1")))))
    three = combine(*rm("b_1", "b_2", "b_3"), flag("b_3", p["b_t"]), view("b_v3"))

    # ------------------------------------------------------------------ attack: the arrow
    km_set, km_read = kill_check("m", rage_m)
    arrow = homing("a_arrow", p["arrow_speed"], p["arrow_y"], "Enemy",
                   [km_set, attack(0, 100), ap(p["w_on"], 0), view("a_hit"), tsfx("a_hit"), km_read])
    ka_set, ka_read = kill_check("a", rage_c)
    twin = homing("a_twin", p["arrow_speed"], p["arrow_y"], "EnemyChampion", [ka_set, climb, ka_read])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_shot"), cview("a_flash"), arrow, twin), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Piercing Arrow
    def q_arrow(full):
        """One release: the arrow (falloff per unit) and its champion twin (detonation, W's bonus, kill check)."""
        scale = 100 if full else p["q_quick"]
        reach = p["q_reach_f"] if full else p["q_reach_q"]
        # qh<k>: k units hit so far by this arrow (one flag at a time, 40 ticks); the k-th unit takes q_fall[k]
        last = len(p["q_fall"]) - 1
        hits = [f"qh{k}" for k in range(1, last + 1)]

        def dmg(k):
            pct = p["q_fall"][k] * scale // 100
            return attack(p["q_dmg"] * pct // 100, p["q_ratio"] * pct // 100)

        ladder = combine(dmg(0), flag("qh1", 40))
        for k in range(1, last + 1):
            step = combine(dmg(k), *rm(f"qh{k}"), flag(f"qh{k + 1}", 40)) if k < last else dmg(k)
            ladder = sw(f"qh{k}", step, ladder)
        hit = [ladder, view("q_hit"), tsfx("q_hit")]
        name = "q_arrow" if full else "q_arrow_s"
        shot = line(name, p["q_speed"], reach, p["q_rad"], p["q_y"], "EnemyWithoutTower", True, hit)
        kq_set, kq_read = kill_check("q", rage_c)
        bonus = [sw("w_cd", NONE, combine(true_hp(p["w_q_hp"]), flag("w_cd", p["w_cd"]), view("w_pop"), tsfx("w_pop")))] if full else []
        champ = line(name + "_twin", p["q_speed"], reach, p["q_rad"], p["q_y"], "EnemyChampion", True,
                     [kq_set, det(True, bonus), kq_read])
        return combine(*rm(*hits), shot, champ)

    def release(full):
        aim = p["q_reach_f"] - 10000 if full else p["q_reach_q"] - 10000
        tag = "q_go_f" if full else "q_go_q"
        fire = combine(cview("q_fire"), sfx("q_fire"))
        return combine(*rm(tag), fire, pick(aim, "EnemyChampion", flag(tag, 1), q_arrow(full)),
                       sw(tag, NONE, q_arrow(full)))

    full = combine(anim("skill", p["q_full_t"] + p["q_rec"]), cview("q_charge"), sfx("q_charge"),
                   sw("w_cd", NONE, cview("w_glow")), delayed(p["q_full_t"], release(True)))
    quick = combine(anim("skill_quick", p["q_quick_t"] + p["q_rec"]), cview("q_charge_s"), sfx("q_charge"),
                    delayed(p["q_quick_t"], release(False)))
    skill = action("skill", 3, p["q_cd"], 1, p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(*rm("q_full"), pick(p["q_aim_f"], "EnemyChampion", flag("q_full", 1)),
                           sw("q_full", full, quick)))

    # ------------------------------------------------------------------ skill2: E Hail of Arrows
    ke_set, ke_read = kill_check("e", rage_c)
    land = zone("e_land", p["e_r"], p["e_land"] + 1, p["e_land"] + 1, "EnemyWithoutTower",
                [attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")])
    land_c = zone("e_land_c", p["e_r"], p["e_land"] + 1, p["e_land"] + 1, "EnemyChampion", [ke_set, det(True), ke_read])
    ground = field("e_field", p["e_r"], p["e_field_t"], 15, "EnemyWithoutTower",
                   [buff("e_slow", 15, move_speed_mult=-p["e_slow"], heal_reduce=p["e_grievous"])])
    skill2 = action("skill2", p["e_dur"], p["e_cd"], p["e_st"], p["e_range"], "Position", "EnemyWithoutTower",
                    combine(cview("e_cast"), sfx("e_cast"), view("e_rain"), land, land_c,
                            delayed(p["e_land"], sfx("e_land"), ground)))

    # ------------------------------------------------------------------ ult: R Chain of Corruption
    kr_set, kr_read = kill_check("r", rage_c)
    spread = zone("r_spread", p["r_spread_r"], 2, 1, "EnemyChampion",
                  [{"type": "Bind", "duration": p["r_root2"]}, buff("r_bind", p["r_root2"]), view("r_spread_hit"),
                   view("b_v3"), tsfx("r_spread")])
    tendril = line("r_chain", p["r_speed"], p["r_reach"], p["r_rad"], p["r_y"], "EnemyChampion", False,
                   [kr_set, attack(p["r_dmg"], p["r_ratio"]), det(False), {"type": "Bind", "duration": p["r_root"]},
                    buff("r_bind", p["r_root"]), view("r_hit"), tsfx("r_hit"), three, flag("r_hit", 3), kr_read],
                   end=[sw("r_hit", combine(*rm("r_hit"), delayed(p["r_spread"], view("r_spread"), spread)))])
    ult = action("ult", p["r_dur"], p["r_cd"], p["r_st"], p["r_range"], "Targeting", "EnemyChampion",
                 combine(cview("r_cast"), sfx("r_cast"), tendril))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring)
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1, repeat=True: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                                    "repeat": repeat, "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_arrow"), P_("q_arrow"), P_("q_arrow_s"), P_("r_chain"), P_("e_field", BIG, -1)]
    views_e = [E("a_flash", FX, 2, **LATE), E("a_hit", FX, 2), E("b_v1", FX, 3), E("b_v2", FX, 3), E("b_v3", FX, 3),
               E("b_pop1", FX, 3), E("b_pop2", FX, 3), E("b_pop3", FX, 3), E("w_pop", FX, 3), E("w_glow"),
               E("q_charge"), E("q_charge_s"), E("q_fire", FX, 2, **LATE), E("q_hit", FX, 2),
               E("e_cast"), E("e_rain", BIG, 2, False), E("e_hit", FX, 2),
               E("r_cast"), E("r_hit", FX, 2), E("r_spread", BIG, 1, False), E("r_spread_hit", FX, 2),
               E("p_rage_on", FX, 2, **LATE)]
    views_b = [B_("e_slow", FX, -1), B_("r_bind", FX, 2), B_("p_rage", FX, -1)]
    return {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "CC"],
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
