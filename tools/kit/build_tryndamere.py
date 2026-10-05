"""Build league_tryndamere.data_champion (top, Melee) from the parameters P.

    python tools/kit/build_tryndamere.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-05: all the recommended options; "大招快没血的时候设置开也行" goes to the native
add-on addons/league_tryndamere_rage, which reads his health - the data pack keeps the danger it can see):
  passive Battle Fury: five Fury stacks f_1..f_5, each crit_chance +f_crit (League: 0.4% a Fury point, 40% at 100).
          His attack climbs one stack, every unit E passes one, his killing blow two (league_jinx's kill check on the
          attack). The stacks fall off one at a time (league_jax Relentless Assault: all of f_1..f_n are on, the top one
          f_top ticks, every lower one f_step more), so Fury lasts f_top ticks after his last hit and then drains a stack
          every f_step. A crit is the engine's: 2x on the attack (League 175%), never on E.
          Q Bloodlust's passive (attack damage by missing health: nothing reads health) is in his base attack.
  attack  A melee swing (100% AD, crits). It also runs the danger check while R is armed (league_kayle R): the hit
          sensor (league_sett's Grit: a 1-point shield and a `WithShield` flag; hit since the last check -> one level of
          h_1..h_n, each h_t ticks) and the count of enemy champions within d_near (two 3-tick flags, read a tick later).
          Danger = two or more champions on him, or hit at h_n checks in a row.
  skill   E Spinning Slash: a `Targeting` cast on `EnemyWithoutTower` (e_range): RushTime (e_speed x e_tick, penetrate,
          radius e_rad) toward the target and through it, e_dmg + e_ratio% AD to every enemy passed, a Fury stack each.
          League's crit refund is folded into the cooldown.
  skill2  W Mocking Shout: a `None` cast on `EnemyChampion` (w_range): enemy champions within w_r lose w_ad% attack for
          w_t ticks; the ones beyond w_near (turned away from him, as League slows - nothing reads facing; the far ones
          are the ones leaving) are slowed w_slow% for w_slow_t.
  ult     R Undying Rage, armed (league_kayle R): a 3-tick cast on the idle tag (`EnemyChampion` within r_arm_range) adds
          r_armed for r_window ticks; his attacks check the danger while it lasts. A save removes r_armed: full Fury,
          r_t ticks of `undying` (his health stops at 1), the roar pose, the voice; r_q_at ticks in Q Bloodlust heals by
          the Fury he holds and spends it (League's R -> Q). Unused, the window caps the cooldown at 60 ticks.
          With R on cooldown (or before level 5) the same danger drinks Q instead: Bloodlust's heal, every q_cd ticks.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_tryndamere.data_champion")
ID = "league_tryndamere"
FX = "asset/league/effects/league_tryndamere_fx"
BIG = "asset/league/effects/league_tryndamere_big"

# Numbers = candidate c9 of the 10-min classic-SDK simulations (tr_sim/sim/kd.py, top lane against fighter, executioner,
# lancer, pole_warrior, knight and berserker, three lineups, both sides, 2026-10-05): +1.34 on seeds 1-12, +1.24 on seeds
# 13-24 (base fighter +1.14 / +0.72, league_sett +1.08 / +1.24). The draft c0 was -0.62 and drank Q at full health (its
# danger check): Q only at R's end -0.03, E 70 + 120% -> 100 + 160% at 9 -> 8 s and hp 1000 -> 1050 for c9. Crit 10% a
# stack (c10, +1.46 / +1.31) did the same; 8% keeps League's 40% at full Fury. Placeholder timings (no sprite yet).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Tryndamere:
    # 66 AD (no growth: Bloodlust's passive), 696 +108 hp, 33 armour, 345 move, crits from Fury
    "hp": 1050, "hp_g": 105, "atk": 86, "atk_g": 17, "def": 30, "def_g": 8, "mr": 25, "mr_g": 4, "ms": 1000, "ms_g": 11,
    "regen": 2, "regen_g": 1,
    # attack
    "atk_range": 25000, "atk_dur": 24, "atk_cd": 62, "atk_st": 12,
    # passive Battle Fury
    "f_n": 5, "f_crit": 8, "f_top": 300, "f_step": 60,
    # danger check (data pack): two champions within d_near, or hit at h_n checks in a row
    "d_near": 30000, "d_two": 1, "h_n": 5, "h_t": 150, "q_drink": 0,
    # the native add-on (addons/league_tryndamere_rage) instead: R below n_r_hp% health (or n_burst% lost in n_burst_t
    # ticks, n_burst_left% left), Q below n_q_hp% with R not armed - an enemy champion within n_near
    "n_near": 50000, "n_r_hp": 15, "n_q_hp": 30, "n_burst": 35, "n_burst_left": 40, "n_burst_t": 60,
    # skill: E Spinning Slash (League: 660 dash, 75-155 + 130% bonus AD + 80% AP, cd 12-8 s minus crit refunds)
    "e_cd": 480, "e_range": 45000, "e_dur": 16, "e_st": 2, "e_speed": 4000, "e_tick": 12, "e_rad": 15000,
    "e_dmg": 100, "e_ratio": 160,
    # skill2: W Mocking Shout (League: 850 radius, -20/35/50/65/80 AD for 4 s, slow 30-60% on those facing away, cd 14 s)
    "w_cd": 840, "w_range": 40000, "w_dur": 24, "w_st": 10, "w_r": 40000, "w_near": 12000, "w_ad": 25, "w_t": 240,
    "w_slow": 40, "w_slow_t": 120,
    # ult: R Undying Rage (League: 5 s, 50-100 Fury, cd 120/100/80 s)
    "r_cd": 3000, "r_arm_range": 60000, "r_window": 900, "r_t": 300, "r_anim": 30, "r_q_at": 290,
    # Q Bloodlust (League: 30-110 + 1.3% AP, + 0.5-0.95 + 1.2% AP per Fury point; cd 12 s)
    "q_heal": 60, "q_heal_ratio": 30, "q_per": 50, "q_per_ratio": 10, "q_cd": 720, "q_anim": 24,
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


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": ratio, "ap_ratio": 0, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, native=False):
    """native: the add-on's copy - no data danger check, the add-on's passive reads his health."""
    F = p["f_n"]
    fury = [f"f_{k}" for k in range(1, F + 1)]

    # ------------------------------------------------------------------ passive: Battle Fury
    def fury_to(m):
        """Fury to m stacks: f_1..f_m on, the top one f_top ticks, every lower one f_step more."""
        return [flag(f"f_{k}", p["f_top"] + (m - k) * p["f_step"], crit_chance=p["f_crit"]) for k in range(1, m + 1)]

    def gain(add):
        """`add` stacks more (at most F): the highest stack on is the count."""
        out = combine(*rm(*fury), *fury_to(min(F, add)))
        for k in range(1, F + 1):
            out = sw(f"f_{k}", combine(*rm(*fury), *fury_to(min(F, k + add))), out)
        return out

    full = combine(*rm(*fury), *fury_to(F))

    def kill_check(src, reward):
        """On a hit unit, around its damage: the flag before, the living target's clear after, the read on him later
        (league_jinx Get Excited!)."""
        k = f"k_{src}"
        return (combine(*rm(k), flag(k, 40)),
                combine(casted(3, 1, *rm(k)), on_me(delayed(4, sw(k, combine(*rm(k), reward))))))

    # ------------------------------------------------------------------ Q Bloodlust: heal by the Fury held, spend it
    def bloodlust():
        def drink(m):
            return heal(p["q_heal"] + m * p["q_per"], p["q_heal_ratio"] + m * p["q_per_ratio"])
        chain = drink(0)
        for k in range(1, F + 1):
            chain = sw(f"f_{k}", drink(k), chain)
        return combine(on_me(chain), *rm(*fury), anim("skill_q", p["q_anim"]), cview("q_heal"), sfx("q_heal"))

    # ------------------------------------------------------------------ R Undying Rage (a save)
    rage = combine(*rm("r_armed"), flag("r_rage", p["r_t"], undying=True), full, anim("ult", p["r_anim"]),
                   cview("r_cast"), sfx("r_cast"),
                   delayed(p["r_q_at"], bloodlust(), sfx("r_end")))
    drink_q = combine(flag("q_cd", p["q_cd"]), bloodlust())
    save = sw("r_armed", rage, drink_q)      # the check runs only with R armed or Q ready

    # ------------------------------------------------------------------ danger check (in the attack)
    hurt = [f"h_{k}" for k in range(1, p["h_n"] + 1)]

    def hurt_up():
        """One more level, exclusive flags (league_kaisa's Plasma), the top one refreshed."""
        out = combine(flag("h_1", p["h_t"]))
        for k in range(1, p["h_n"] + 1):
            nxt = min(k + 1, p["h_n"])
            out = sw(f"h_{k}", combine(*rm(*hurt), flag(f"h_{nxt}", p["h_t"])), out)
        return out

    arm_sensor = combine(on_me({"type": "Shield", "amount": 1, "attack_ratio": 0, "ap_ratio": 0, "tick": 36000}),
                         flag("sense", "shield"))
    sensor = sw("sense", NONE, combine(hurt_up(), arm_sensor))
    count = around(p["d_near"], "EnemyChampion", [sw("n_1", flag("n_2", 3), flag("n_1", 3))])
    by_hurt = sw(f"h_{p['h_n']}", combine(*rm(*hurt), flag("go", 1)))
    danger = combine(*rm("n_1", "n_2"), count,
                     delayed(1, sw("n_2", flag("go", 1), by_hurt) if p["d_two"] else by_hurt, sw("go", save)))
    # the check only while he could use it: R armed, or Q ready; never while raging (1-tick flags: one copy of each)
    q_ready = sw("q_cd", NONE, flag("chk", 1)) if p["q_drink"] else NONE
    check = NONE if native else sw("r_rage", NONE, combine(sensor, sw("r_armed", flag("chk", 1), q_ready),
                                       sw("chk", danger)))

    # ------------------------------------------------------------------ attack
    k_set, k_read = kill_check("a", gain(2))
    swing = combine(k_set, attack(0, 100), view("a_hit"), tsfx("a_hit"), k_read)
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), check, gain(1), swing), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: E Spinning Slash
    ke_set, ke_read = kill_check("e", gain(2))
    rush = {"type": "RushTime", "speed": p["e_speed"], "tick": p["e_tick"], "range": p["e_rad"],
            "casting_target": "EnemyWithoutTower", "penetrate": True,
            "applied_effects": [T(e) for e in (ke_set, attack(p["e_dmg"], p["e_ratio"]), gain(1), view("e_hit"),
                                                tsfx("e_hit"), ke_read)]}
    skill = action("skill", p["e_dur"], p["e_cd"], p["e_st"], p["e_range"], "Targeting", "EnemyWithoutTower",
                   combine(anim("skill", p["e_tick"] + 4), cview("e_spin"), sfx("e_cast"), rush))

    # ------------------------------------------------------------------ skill2: W Mocking Shout
    shout = combine(
        around(p["w_r"], "EnemyChampion", [buff("w_weak", p["w_t"], attack_mult=-p["w_ad"]),
                                           buff("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]), view("w_hit")]),
        # the ones close to him are facing him: their slow is taken back (two buffs, summed)
        around(p["w_near"], "EnemyChampion", [buff("w_face", p["w_slow_t"], move_speed_mult=p["w_slow"])]))
    skill2 = action("skill2", p["w_dur"], p["w_cd"], p["w_st"], p["w_range"], "None", "EnemyChampion",
                    combine(cview("w_shout"), sfx("w_shout"), shout))

    # ------------------------------------------------------------------ ult: arm R
    retry = p["r_cd"] * 100 // 60 - 100
    ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion",
                 combine(*rm("r_armed"), flag("r_armed", p["r_window"]),
                         delayed(p["r_window"] - 1, sw("r_armed", combine(*rm("r_armed"),
                                                                       flag("r_retry", 3, ult_cooldown_mult=retry))))),
                 key="ult")

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring)
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_e = [E("a_hit", FX, 2), E("e_spin", BIG, 2), E("e_hit", FX, 2), E("w_shout", BIG, 2), E("w_hit", FX, 3),
               E("r_cast", BIG, 2, **LATE), E("q_heal", FX, 2, **LATE)]
    views_b = [B_(f"f_{F}", FX, -1), B_("r_rage", BIG, -1), B_("w_weak", FX, 3), B_("w_slow", FX, -1)]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee"],
        "sprite": f"asset/league/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/league/icons/{ID}_skill", f"asset/league/icons/{ID}_skill2", f"asset/league/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": 0, "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": p["regen"], "stack": 0,
                 "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": 0, "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": p["regen_g"], "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": [], "view_effects": views_e, "view_buffs": views_b,
    }
    if native:
        keys = ["f_n", "f_crit", "f_top", "f_step", "r_t", "r_q_at", "r_anim", "q_heal", "q_heal_ratio", "q_per",
                "q_per_ratio", "q_cd", "q_anim"]
        params = {k: int(p[k]) for k in keys}
        params.update({k[2:]: int(p[k]) for k in ("n_near", "n_r_hp", "n_q_hp", "n_burst", "n_burst_left", "n_burst_t")})
        kit["passive"] = {"passive_ref": "league_tryndamere_rage:guard", "params": params}
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
