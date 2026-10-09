"""Build league_olaf.data_champion (top, Melee) from the parameters P.

    python tools/kit/build_olaf.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-09: top, Melee, League's whole kit with the pros' play). TFM2 has three active slots:
Undertow is `skill`, Reckless Swing `skill2`, Ragnarok the `ult`; Tough It Out runs on its own inside the attack
(league_zed's Shadow Slash way).
  passive Berserker Rage (狂战之怒): League gives attack speed and life steal by missing health. Nothing reads health, so
          it counts the beating he takes (league_tryndamere's hit sensor: a 1-point shield and a `WithShield` flag; his
          attack finds it broken -> one Rage level more): levels p_1..p_n all on at once (league_jax's ladder: the top one
          p_top ticks, every lower one p_step more), each p_as% attack speed, the top p_vn levels p_vamp% life steal
          too; out of the fight they drain a level every p_step. Reckless Swing's own cost breaks the sensor as well.
          The add-on addons/league_olaf_rage (native=1) reads his health instead.
  attack  The axe swing, the hit on tick atk_st. Tough It Out (挺过去, automatic): with w_cd off and an enemy champion
          within w_r, the swing also roars - w_as% attack speed for w_t ticks and a shield of w_sh + w_sh_ratio% AD for
          w_sh_t. Under Ragnarok every hit on a champion holds it r_t ticks more (up to r_max). Ragnarok's passive
          armour: from level 3 (the only level the data reads) he keeps r_def armour and r_mr magic resistance while
          Ragnarok is not running.
  skill   Q Undertow (逆流投掷): a `Targeting` cast on `EnemyWithoutTower` (q_range). On tick q_at the axe is lobbed at the
          spot the target stands on (q_fly ticks: dodgeable), and a hidden blade flies the same way through everything:
          q_dmg + q_ratio% AD, q_slow% slow for q_slow_t, q_shred% armour for q_shred_t. The axe stays stuck there
          q_life ticks; walking over it (pick_r) picks it up: a 2-tick `skill_cooldown_mult` q_pick caps the skills'
          cooldowns at 100 / (100 + q_pick) of their cooltime (League's refund; Reckless Swing's too - League cuts it by
          his attacks), `ult_cooldown_mult` -q_pick keeps the ult's. Two axes may lie at once (flags axe_a / axe_b).
  skill2  E Reckless Swing (鲁莽挥击): a `Targeting` cast on `EnemyWithoutTower` (e_range): e_dmg + e_ratio% AD true
          damage; he takes e_self% of it himself (true damage), healed back when the blow kills (league_jinx's kill
          check).
  ult     R Ragnarok (诸神黄昏): a `None` cast when an enemy champion is within r_range: the roar, r_t ticks of crowd-control
          immunity, r_atk% attack and r_ms% move speed (the passive armour goes meanwhile); his hits on champions
          (attack, Reckless Swing) hold it on, at most r_max ticks in all. The pros' R-E-Q: he roars as he engages,
          walks in through the crowd control, swings, picks up the axe and throws again.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_olaf.data_champion")
ID = "league_olaf"
FX = "asset/league/effects/league_olaf_fx"
BIG = "asset/league/effects/league_olaf_big"

# Numbers = candidate c3 of the 10-min classic-SDK simulations (ol_sim/sim/kd.py, top lane against fighter, executioner,
# lancer, pole_warrior, knight and berserker, three lineups, both sides, 2026-10-09): +1.28 on seeds 1-12 (the same batch:
# league_tryndamere +1.34, league_darius +1.71). The draft c0 was -1.20 (attack 90, hp 1020, Rage 12% / 6%, E 70 + 60% at
# 6 s, Q 70, W shield 60, R +20%); c4 halfway +0.58.
# Timings provisional until the strips exist: the swing's hit on tick 12, the axe leaves on 12 (skill), Reckless Swing
# lands on 10 (skill2), the roar 20 ticks (ult).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Olaf: 645 +119
    # hp, 68 AD +4.7, 35 armour, 350 move, 125 range
    "hp": 1100, "hp_g": 108, "atk": 100, "atk_g": 18, "def": 34, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000, "ms_g": 11,
    # attack: the axes
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 64, "atk_st": 12,
    # passive Berserker Rage (League: attack speed and life steal by missing health)
    "p_n": 4, "p_as": 20, "p_vamp": 12, "p_vn": 2, "p_top": 180, "p_step": 90,
    # W Tough It Out (League: 40-80% attack speed 4 s, shield 2.5 s, cd 16-12 s)
    "w_cd": 780, "w_r": 30000, "w_as": 40, "w_t": 240, "w_sh": 100, "w_sh_ratio": 40, "w_sh_t": 150,
    # Q Undertow (League: 1000 range, 60-260 + 100% bonus AD, armour -20%, slow, picked up: cd refund; cd 9 s)
    "q_cd": 480, "q_range": 50000, "q_dur": 24, "q_at": 12, "q_fly": 10, "q_len": 55000, "q_speed": 5500,
    "q_rad": 7000, "q_y": 4000, "q_dmg": 100, "q_ratio": 100, "q_slow": 30, "q_slow_t": 90, "q_shred": 20,
    "q_shred_t": 240, "q_life": 300, "pick_r": 9000, "q_pick": 120, "axe_step": 15,
    # E Reckless Swing (League: 325 range, 70-250 + 50% AD true damage, 30% of it to himself, cd 9-5 s cut by attacks)
    "e_cd": 300, "e_range": 28000, "e_dur": 22, "e_st": 10, "e_dmg": 110, "e_ratio": 90, "e_self": 30,
    # R Ragnarok (League: 10-30 armour / mr passive; 3 s, extended by champion hits, CC immune, AD, haste; cd 100-80 s)
    "r_cd": 3000, "r_range": 40000, "r_dur": 20, "r_t": 180, "r_max": 600, "r_atk": 30, "r_ms": 20, "r_def": 12,
    "r_mr": 12,
    # his spoken lines, at most one every vo_gap ticks
    "vo_gap": 600,
    # 1 = the copy for addons/league_olaf_rage: its native passive reads health and sets the Rage levels (n_lo% health
    # missing or more: one level; every n_band% more: one more), the sensor goes
    "native": 0, "n_lo": 15, "n_band": 17,
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


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `WithSelf` would also hit the action's target)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def line(name, speed, rng, radius, y, target, penetrate, effects, end=()):
    return {"type": "LinearProjectile", "name": n(name), "penetrate": penetrate, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": list(end), "speed": speed, "range": rng,
            "shape": circle(radius), "y_offset": y}


def lob(name, travel, target, end):
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 1000000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def pzone(name, r, tick, period, target, effects):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(r), "tick": tick, "period": period,
            "first_delay": 0, "applied_target": target, "applied_effects": [T(e) for e in effects], "end_effects": []}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def kill_check(src, reward):
    """On a hit unit, around its damage: the flag before, the living target's clear after, the read on him later
    (league_jinx Get Excited!; a dead target's `Delayed` adds nothing, so the flag stays)."""
    k = f"k_{src}"
    return (combine(*rm(k), flag(k, 40)),
            combine(casted(3, 1, *rm(k)), on_me(delayed(4, sw(k, combine(*rm(k), reward))))))


def build(p):
    native = bool(p["native"])
    N = p["p_n"]
    rage = [f"p_{k}" for k in range(1, N + 1)]

    # ------------------------------------------------------------------ passive: Berserker Rage
    def rage_to(m):
        """Rage at m levels: p_1..p_m on, the top one p_top ticks, every lower one p_step more; the top p_vn levels
        of the ladder carry the life steal."""
        out = []
        for k in range(1, m + 1):
            fields = {"attack_speed_mult": p["p_as"]}
            if k > N - p["p_vn"]:
                fields["vamp"] = p["p_vamp"]
            out.append(flag(f"p_{k}", p["p_top"] + (m - k) * p["p_step"], **fields))
        return out

    def climb():
        """One level more (at most N): the highest level on is the count."""
        out = combine(*rm(*rage), *rage_to(1))
        for k in range(1, N + 1):
            out = sw(f"p_{k}", combine(*rm(*rage), *rage_to(min(N, k + 1))), out)
        return out

    arm_sensor = combine(on_me({"type": "Shield", "amount": 1, "attack_ratio": 0, "ap_ratio": 0, "tick": 36000}),
                         flag("sense", "shield"))
    # hit since the last check (the 1-point shield broke): one level more; re-armed either way
    sensor = NONE if native else sw("sense", NONE, combine(climb(), arm_sensor))

    # ------------------------------------------------------------------ R Ragnarok (on him) and its passive armour
    r_buff = dict(attack_mult=p["r_atk"], move_speed_mult=p["r_ms"], cc_immune=True)
    hold_r = sw("r_on", sw("r_cap", refresh("r_on", p["r_t"], **r_buff)))
    passive_armour = {"type": "SwitchByLevel3", "effect_start": NONE,
                      "effect_level3": sw("r_on", NONE, sw("r_pass", NONE, flag("r_pass", None, defence=p["r_def"],
                                                                                magic_resistance=p["r_mr"])))}

    # ------------------------------------------------------------------ attack (Tough It Out folded in)
    tough = combine(flag("w_cd", p["w_cd"]), refresh("w_on", p["w_t"], attack_speed_mult=p["w_as"]),
                    on_me({"type": "Shield", "amount": p["w_sh"], "attack_ratio": p["w_sh_ratio"], "ap_ratio": 0,
                           "tick": p["w_sh_t"]}),
                    cview("w_cast"), sfx("w"), voice("vo_w", p))
    w_near = {"type": "RandomTarget", "range": p["w_r"], "casting_target": "EnemyChampion", "from_projectile": False,
              "effects": [flag("w_go", 1)]}
    w_check = sw("w_cd", NONE, combine(w_near, sw("w_go", tough)))
    swing = combine(attack(0, 100), view("a_hit"), tsfx("a_hit"))
    twin = homing("a_twin", 100000, 0, "EnemyChampion", [on_me(hold_r)])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), sensor, passive_armour, w_check, swing, twin),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Undertow
    def axe(gen):
        """The axe lobbed at the target's spot; there it sticks q_life ticks (a picture every axe_step while its flag
        holds) and a zone picks it up when he walks over it."""
        g = f"axe_{gen}"
        pick = {"type": "RandomTarget", "range": p["pick_r"], "casting_target": "AllyOnlySelf", "from_projectile": True,
                "effects": [sw(g, combine(*rm(g), flag("q_ref", 2, skill_cooldown_mult=p["q_pick"],
                                                         ult_cooldown_mult=-p["q_pick"]),
                                          cview("q_pick"), sfx("q_pick")))]}
        stuck = [view("q_land"), sfx("q_land"), pzone("q_zone", p["pick_r"], p["q_life"], 3, "AllyChampion", [pick])]
        stuck += [delayed(t, sw(g, view("q_axe"))) for t in range(p["axe_step"], p["q_life"], p["axe_step"])]
        return combine(refresh(g, p["q_fly"] + p["q_life"]), lob("q_axe", p["q_fly"], "EnemyWithoutTower", stuck))

    blade = line("q_blade", p["q_speed"], p["q_len"], p["q_rad"], p["q_y"], "EnemyWithoutTower", True,
                 [attack(p["q_dmg"], p["q_ratio"]), buff("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                  buff("q_shred", p["q_shred_t"], defence_mult=-p["q_shred"]), view("q_hit"), tsfx("q_hit")])
    throw = sw("q_gen", combine(*rm("q_gen"), axe("b")), combine(flag("q_gen", None), axe("a")))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(anim("skill", p["q_dur"]), voice("vo_q", p),
                           delayed(p["q_at"] - 1, sfx("q"), blade, throw)))

    # ------------------------------------------------------------------ skill2: E Reckless Swing
    cost = combine(on_me(true_dmg(p["e_dmg"] * p["e_self"] // 100, p["e_ratio"] * p["e_self"] // 100)))
    k_set, k_read = kill_check("e", on_me(heal(p["e_dmg"] * p["e_self"] // 100, p["e_ratio"] * p["e_self"] // 100)))
    e_twin = homing("e_twin", 100000, 0, "EnemyChampion", [on_me(hold_r)])
    reckless = combine(k_set, true_dmg(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit"), k_read)
    skill2 = action("skill2", p["e_dur"], p["e_cd"], p["e_st"], p["e_range"], "Targeting", "EnemyWithoutTower",
                    combine(sfx("e"), voice("vo_e", p), reckless, cost, e_twin))

    # ------------------------------------------------------------------ ult: R Ragnarok
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "None", "EnemyChampion",
                 combine(anim("ult", p["r_dur"]), sfx("r"), voice("vo_r", p), cview("r_cast"), *rm("r_pass"),
                         refresh("r_on", p["r_t"], **r_buff), refresh("r_cap", p["r_max"])))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("q_axe")]
    views_e = [E("a_hit"), E("q_hit"), E("q_land", FX, -1, False), E("q_axe", FX, -1, False), E("q_pick", FX, 3),
               E("e_hit", BIG, 3), E("w_cast", FX, 3), E("r_cast", BIG, 3)]
    views_b = [B_("r_on", BIG, -1), B_("w_on", FX, -1), B_("q_slow", FX, -1), B_(f"p_{N}", FX, 3)]
    extra = {}
    if native:
        extra["passive"] = {"passive_ref": "league_olaf_rage:rage",
                            "params": {k: int(p[k]) for k in ("p_n", "p_as", "p_vamp", "p_vn", "n_lo", "n_band")}}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee"], **extra,
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
    ap_.add_argument("--native", action="store_true", help="the add-on's copy (health read natively)")
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
