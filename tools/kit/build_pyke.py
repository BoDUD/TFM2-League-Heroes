"""Build league_pyke.data_champion (support, Assassin) from the parameters P.

    python tools/kit/build_pyke.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-06, all the recommended options: Q / W -> E combo / R an X-shaped execute that can be
cast again after a kill / grey health and health turned into attack; category Assassin. The exact execute - it needs
the target's current health, which the data cannot read - goes to a native add-on, 「这个读不到的话就改rust原码」):
  passive Gift of the Drowned Ones (溺水之幸): grey health. A 1-point shield on him is the hit sensor (league_sett W's
          Grit): his attack and his ult look at it, and a broken sensor is one more grey level (g1..g{p_lv}, exclusive
          flags of p_keep ticks) and a `hurt` flag for p_calm ticks. The grey levels come back as health
          (p_heal + p_heal_r% AD a level, over p_pulse_n pulses) when he goes into W's camouflage or when nothing hit
          him for p_calm ticks after an attack (a `Delayed` queued by every attack checks the sensor and `hurt`).
          League's "no bonus health, bonus health becomes AD" is the stat line: little health and growth, more AD
          growth.
  attack  A harpoon swing on the target, the hit a_st ticks in.
  skill   Q Bone Skewer (透骨尖钉), smart: a `Direction` cast on `EnemyWithoutTower`. An enemy champion within q_close
          -> the tap: a stab (skill_stab, q_stab_t ticks) on that champion at q_stab_at: q_dmg + q_ratio% AD and a
          q_slow% slow for q_slow_t. Else the hold: he charges q_hold ticks (skill) and throws the harpoon at an enemy
          champion within reach then (where he stands then: dodged by walking off the line; the throw passes minions,
          as league_thresh Q - the AI cannot aim round them), else along the cast at the first enemy on the line (a
          minion, a monster). The hit: the damage, the slow and `Grab` (dragged to him); the harpoon comes back.
  skill2  W Ghostwater Dive (幽潭潜行) -> E Phantom Undertow (魅影浪洄): a `Targeting` cast on `EnemyChampion`
          (c_range). W: camouflage (`CasterInvisible` w_camo), w_ms% move speed fading over w_ms_t, the grey health
          comes back. c_lead ticks later E: he dashes through the target (`RushMoveToBack`); where the dash started a
          drowned phantom stays (league_ekko's anchor) and e_ret ticks later it rushes back to him
          (`BackToCasterLinearProjectile`), every enemy champion on its way: e_dmg + e_ratio% AD and a e_stun-tick stun.
  ult     R Death from Below (涌泉之恨): a `Targeting` cast on `EnemyChampionRecentlyAttacked` (r_range). An X marks the
          target's spot (a 1-tick lob, league_xerath R's shells: dodgeable) and r_delay ticks later it strikes round
          it (r_rad): enemy champions take the threshold T = r_dmg + r_ratio% AD as true damage - below T they die,
          League's execute - and a tick later the survivors are healed back half of T (`Heal` heal_type Any: a dead
          unit stays dead), so they lose half as in League; other enemies take half of T physical. A champion dying in
          the X (league_jinx's kill check) blinks him onto it and takes the ult's cooldown off: he can cast it again.
          League's gold for the assisting ally cannot be given from data.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_pyke.data_champion")
ID = "league_pyke"
FX = "asset/league/effects/league_pyke_fx"
BIG = "asset/league/effects/league_pyke_big"

# Numbers = candidate c6a of the 10-min classic-SDK simulations (tr_sim/sim/kd.py --lane 4 against priest, bard,
# enchanter, monk and taoist, both sides, three lineups, 2026-10-06): +1.12 on seeds 1-24 and +1.24 on 25-48
# (league_leona +0.78 / +1.23, league_rakan +0.84 / +0.41 on the same seeds; c5 with attack 74 +8 was +1.67 / +1.44
# with the final timings, c6b with R 170 + 55% every 50 s +1.41 / +1.25). The draft c1 was +3.80 (8825 damage a game,
# twice Leona's; R 6 casts a game): attack 90 +16 -> 72 +7, R 220 + 90% every 25 s -> 180 + 60% every 45 s, Q 60 + 100% -> 35 + 60% every 7 s, E 70 + 90% -> 50 + 60%,
# grey health 22 + 12% -> 15 + 8% a stack (c2 +1.53, c3 +2.82, c4 with less health and a shorter stun +0.56).
# E's phantom comes back 12 ticks after the dash at 12000 a tick (25 hits in 32 casts; 3 in 37 at 40 ticks).
P = {
    # stats (Assassin base: move 1100); League's Pyke: 600 +110 hp, 62 AD +2, 45 armour, 330 move, melee 150 range;
    # no bonus health (it becomes AD): the pack's lowest support health, an assassin's attack growth
    "hp": 900, "hp_g": 82, "atk": 72, "atk_g": 7, "def": 26, "def_g": 8, "mr": 18, "mr_g": 4, "ms": 1100, "ms_g": 12,
    # attack: the harpoon swing
    "atk_range": 24000, "atk_dur": 24, "atk_cd": 55, "a_st": 12,
    # passive: grey health (League: 10% + lethality of champion damage taken in the last 4 s, healed while unseen)
    "p_lv": 5, "p_keep": 480, "p_calm": 180, "p_heal": 15, "p_heal_r": 8, "p_pulse_n": 4, "p_pulse": 12,
    # skill: Q Bone Skewer (League: tap 100-? + 60% bonus AD stab; hold 0.5-1 s, 1100 range, 70 width, 2000 speed,
    # pull 500, slow 90% 1 s, cd 10-7.5 s)
    "q_cd": 420, "q_range": 100000, "q_close": 26000, "q_stab_t": 22, "q_stab_at": 13, "q_hold": 36, "q_throw_t": 14,
    "q_speed": 6000, "q_reach": 95000, "q_rad": 6000, "q_y": 0, "q_dmg": 35, "q_ratio": 60, "q_slow": 60,
    "q_slow_t": 60, "q_grab": 1500,
    # skill2: W Ghostwater Dive (League: camouflage 5 s, +45% fading over 1.5 s, cd 12-8 s) -> E Phantom Undertow
    # (League: dash 550, the phantom back after 1 s, 100-350 + 100% bonus AD to champions, stun 1.25 s, cd 15-11 s)
    "c_cd": 660, "c_range": 70000, "c_lead": 15, "w_camo": 150, "w_ms": 40, "w_ms_t": 90, "e_t": 14, "e_speed": 9000,
    "e_ret": 12, "e_ph_speed": 12000, "e_ph_rad": 12000, "e_ph_range": 120000, "e_dmg": 50, "e_ratio": 60, "e_stun": 60,
    # ult: R Death from Below (League: range 750, X after 0.5 s, threshold 250-850 + 80% bonus AD (+150% lethality),
    # 50% to the rest, recast 20 s after a champion dies in it, cd 120-80 s)
    "r_cd": 2700, "r_range": 75000, "r_delay": 30, "r_rad": 28000, "r_dmg": 180, "r_ratio": 60, "r_anim": 40,
    "k_hold": 40, "k_read": 4,
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
    dur = "Permanent" if tick is None else ("WithShield" if tick == "shield" else {"Time": {"tick": tick}})
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


def true_dmg(dmg, ratio):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def heal(amount, ratio, kind="Caster"):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": kind}


def shield(amount, tick):
    return {"type": "Shield", "amount": amount, "attack_ratio": 0, "ap_ratio": 0, "tick": tick}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def back(name, speed, rng, radius, target, effects):
    """A projectile from where it is thrown back to his pivot (its y_offset is ignored)."""
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": rng,
            "shape": circle(radius), "penetrate": True, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def lob(name, end):
    """A hidden 1-tick lob: it lands on the unit's spot the tick it is fired; `end` runs on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": 1, "range": 400000, "shape": circle(1000),
            "range_effect_name": "", "applied_target": "EnemyWithoutTower", "applied_effects": [],
            "end_effects": list(end)}


def anchor(end):
    """league_ekko's anchor: a projectile that ends the tick it appears; `end` runs where he stands."""
    return {"type": "LinearProjectile", "name": n("anchor"), "penetrate": True, "applied_target": "Enemy",
            "applied_effects": [], "end_effects": list(end), "speed": 1, "range": 1, "shape": circle(1000),
            "y_offset": 5000}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    lv = p["p_lv"]
    greys = [f"g{k}" for k in range(1, lv + 1)]

    # ------------------------------------------------------------------ passive: grey health
    def sensor():
        """A 1-hit-point shield and the flag that lives while a shield holds: the first hit after it breaks it."""
        return [on_me(shield(1, 36000)), flag("sense", "shield")]

    def climb():
        e = flag("g1", p["p_keep"])
        for k in range(1, lv + 1):
            e = sw(f"g{k}", combine(*rm(f"g{k}"), flag(f"g{min(k + 1, lv)}", p["p_keep"])), e)
        return e

    def grey_heal():
        """The grey levels back as health, over a few pulses; the levels are spent."""
        def pulses(k):
            amount, ratio = p["p_heal"] * k // p["p_pulse_n"], p["p_heal_r"] * k // p["p_pulse_n"]
            return combine(*rm(*greys), cview("p_heal"), sfx("p_heal"),
                           on_me(casted(p["p_pulse"] * (p["p_pulse_n"] - 1) + 1, p["p_pulse"], heal(amount, ratio))))
        e = NONE
        for k in range(1, lv + 1):
            e = sw(f"g{k}", pulses(k), e)
        return e

    # unhit for p_calm ticks after an attack: the sensor still whole and no hit found since (`hurt`)
    calm = on_me(delayed(p["p_calm"], sw("sense", sw("hurt", NONE, grey_heal()))))
    check = sw("init",
               sw("sense", NONE, combine(climb(), refresh("hurt", p["p_calm"]), *sensor())),
               combine(*sensor(), flag("init", None)))

    # ------------------------------------------------------------------ attack: the harpoon swing
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["a_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(check, calm, sfx("a_swing"), attack(0, 100), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Bone Skewer
    slow = buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"])
    stab = combine(anim("skill_stab", p["q_stab_t"]), sfx("q_stab"), voice("vo_q2", p),
                   delayed(p["q_stab_at"], pick(p["q_close"] + 6000, "EnemyChampion",
                                                attack(p["q_dmg"], p["q_ratio"]), slow, view("q_stab_hit"),
                                                tsfx("q_stab_hit"))))
    q_hit = [attack(p["q_dmg"], p["q_ratio"]), slow, {"type": "Grab", "speed": p["q_grab"]}, view("q_hit"),
             tsfx("q_hit")]
    q_back = back("q_return", p["q_grab"], p["q_reach"], 1000, "EnemyChampion", [])

    def hook(name, target):
        return line(name, p["q_speed"], p["q_reach"], p["q_rad"], p["q_y"], target, False, q_hit, [q_back])

    release = combine(*rm("q_go"), sfx("q_throw"),
                      pick(p["q_reach"] - 10000, "EnemyChampion", flag("q_go", 1), hook("q_hook_c", "EnemyChampion")),
                      sw("q_go", NONE, hook("q_hook", "EnemyWithoutTower")))
    # the charge glow is drawn into his own skill frames (assets/source/native/pyke_bake.json: the red side's mirroring)
    hold = combine(anim("skill", p["q_hold"] + p["q_throw_t"]), sfx("q_charge"), voice("vo_q", p),
                   delayed(p["q_hold"], release))
    skill = action("skill", 3, p["q_cd"], 1, p["q_range"], "Direction", "EnemyWithoutTower",
                   combine(*rm("q_tap"), pick(p["q_close"], "EnemyChampion", flag("q_tap", 1)),
                           sw("q_tap", stab, hold)))

    # ------------------------------------------------------------------ skill2: W Ghostwater Dive -> E Phantom Undertow
    phantom = back("e_phantom", p["e_ph_speed"], p["e_ph_range"], p["e_ph_rad"], "EnemyChampion",
                   [attack(p["e_dmg"], p["e_ratio"]), {"type": "Stun", "duration": p["e_stun"]},
                    buff("e_stun", p["e_stun"]), view("e_hit"), tsfx("e_hit")])
    dive = combine(anim("skill2", p["e_t"]), sfx("e_dash"), voice("vo_e", p),
                   anchor([view("e_left"), delayed(p["e_ret"], sfx("e_return"), phantom)]),
                   *[delayed(k, cview("e_trail")) for k in range(1, p["e_t"], 2)],   # the wake, puddle to landing
                   {"type": "RushMoveToBack", "speed": p["e_speed"], "applied_effects": []})
    camo = combine({"type": "CasterInvisible", "tick": p["w_camo"]}, refresh("w_camo", p["w_camo"]),
                   refresh("w_ms", p["w_ms_t"] // 2, move_speed_mult=p["w_ms"] // 2),
                   refresh("w_ms2", p["w_ms_t"], move_speed_mult=p["w_ms"] // 2),
                   cview("w_cast"), sfx("w_cast"), grey_heal())
    skill2 = action("skill2", 3, p["c_cd"], 1, p["c_range"], "Targeting", "EnemyChampion",
                    combine(camo, delayed(p["c_lead"], dive)))

    # ------------------------------------------------------------------ ult: R Death from Below
    k_set = refresh("k_r", p["k_hold"])
    reset = combine(*rm("k_r"), refresh("r_reset", 2, ult_cooldown_mult=10000), cview("r_reset"), sfx("r_reset"),
                    sfx("vo_r"))
    r_t = p["r_delay"] + 1
    execute = [k_set, true_dmg(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit"),
               casted(3, 1, *rm("k_r")),
               delayed(1, heal(p["r_dmg"] // 2, p["r_ratio"] // 2, "Any")),
               delayed(p["k_read"] - 1, sw("k_r", {"type": "Teleport"})),
               on_me(delayed(p["k_read"], sw("k_r", reset)))]
    x = lob("r_lob", [
        view("r_mark"),
        zone("r_x_c", p["r_rad"], r_t, r_t, "EnemyChampion", execute),
        zone("r_x", p["r_rad"], r_t, r_t, "Enemy",
             [attack(p["r_dmg"] // 2, p["r_ratio"] // 2), view("r_hit"), tsfx("r_hit")]),
        delayed(p["r_delay"] - 6, view("r_strike"), sfx("r_strike"))])
    ult = action("ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(*rm("k_r"), check, anim("ult", p["r_anim"]), sfx("r_cast"), x))

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring)
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("q_hook"), P_("q_hook_c", FX), P_("q_return"), P_("e_phantom", BIG)]
    views_e = [E("a_hit"), E("q_stab_hit"), E("q_hit"), E("w_cast"), E("e_left", BIG, 1, False), E("e_trail", FX, -1, False),
               E("e_hit"), E("r_mark", BIG, -1, False), E("r_strike", BIG, 2, False), E("r_hit"),
               E("r_reset", FX, 3, False), E("p_heal", FX, 3, False)]
    views_b = [B_("q_slow", FX, -1), B_("e_stun", FX, 3)]
    return {
        "id": ID, "category": "Assassin", "tags": ["AD", "Melee", "CC"],
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
