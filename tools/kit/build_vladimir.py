"""Build league_vladimir.data_champion (top, Magician) from the parameters P.

    python tools/kit/build_vladimir.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's pick A, 2026-10-08; W 「危险信号 + 现在就做扩展包」; 「还要加入高手的连招」):
  passive Crimson Pact: his maximum health adds to every skill's damage (`hp_ratio`, a share of the caster's max
          health, champion-data section 3) - League's bonus health <-> ability power, the one tank stat data can read.
  attack  a homing blood bolt, 100% AD physical (League's), like every mage's attack in the pack.
  skill   Q Transfusion: a `Targeting` cast on `EnemyWithoutTower` (q_range): q_dmg + q_ap% AP + q_hp% max health magic
          damage, and the blood flies back (a hidden lob lands on the target, a `BackToCasterLinearProjectile` returns
          from there, league_xayah's feathers) and heals him q_heal + q_heal_ap% AP when it reaches him.
          Every second Q is Crimson Rush (League: the bar fills over two casts): q_rush% damage, the heal doubled and
          q_ms% move speed for q_ms_t ticks. `q1` is the half-full bar (its picture q_ready under him: the next one is
          empowered).
  skill2  E Tides of Blood: a `None` cast on `EnemyWithoutTower` within e_r: he charges e_rel ticks (the blood sphere
          round him), then the nova - a homing bolt to every enemy within e_r: e_dmg + e_ap% AP + e_hp% max health,
          e_slow% slow for e_slow_t ticks (League's full charge). `e_cd` marks E on cooldown for the combos.
  W       Sanguine Pool (automatic, no slot: League's W has none here): the pool is a data tree started from a poll that
          runs every 3 ticks on him (an `AddCasted` on himself, re-armed by every attack and spell) while the flag
          `w_go` is on. Main pack: his attack's danger check sets it (league_tryndamere's: two enemy champions within
          d_near, or hit at h_n checks in a row; League players pool to dodge a burst). The native add-on
          (addons/league_vladimir_pool, `--native`): its passive reads his health and sets `w_go` below n_hp% with an
          enemy champion near - the attack's check is left out of that copy.
          The pool: w_cost% max health (a `FixedAttack` on himself, a 2-tick `undying` so it never kills), then w_t ticks
          of CasterInvisible + damaged_reduce 100 + cc_immune (league_xayah R: a self-Banish blinds the team), w_n pulses
          on the enemies within w_r: w_dmg + w_ap% AP + w_hp% max health each, w_slow% slow, a heal of w_heal + w_heal_ap%
          AP each; w_cd ticks before the next.
  ult     R Hemoplague: a `Targeting` cast on `EnemyChampionRecentlyAttacked` (r_range; league_xayah's 「别乱放」 rule):
          a hidden lob lands on the target's spot, the cloud there, every enemy within r_rad takes r_amp% more damage
          for r_t ticks, then the burst: r_dmg + r_ap% AP + r_hp% max health; each champion hit heals him r_heal +
          r_heal_ap% AP.
  combos (the pros' Vladimir, slot-played like league_leesin's: a combo never spends another slot's cooldown)
          E -> Q: an E bolt on an enemy champion opens `eq` (eq_t ticks); a Q in it is Crimson Rush at once, the bar
                  untouched.
          E-W:    the pool ends with E ready (no `e_cd`): he rises out of it with a full nova (combo_pct% damage) - League's
                  charge-E-then-pool.
          Flash R E: R with E ready: he blinks (a mist blink, League's Flash) up to r_blink toward the target, stopping
                  r_stop short of the first enemy champion on the way, and r_ring ticks after the cloud the nova
                  (combo_pct%), under Hemoplague's +r_amp%.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_vladimir.data_champion")
ID = "league_vladimir"
FX = "asset/league/effects/league_vladimir_fx"
BIG = "asset/league/effects/league_vladimir_big"

# Numbers = candidate c5 of the 10-min classic-SDK simulations (vl_sim/sim/kd.py, top lane against fighter, executioner,
# knight, berserker, lancer and pole_warrior, three lineups, both sides, 2026-10-08): the draft was -2.63 on seeds 1-12
# (league_kennen +1.43, league_teemo +1.20); Q 100 + 75% + 5% hp at 4 s, E 90 + 70% + 5% hp at 8 s, R 200 + 80% + 6% hp
# and hp 1000 (c1) +1.24 on seeds 1-12, +0.64 on seeds 25-36; the E -> Q window 1.5 -> 2.5 s (c5) +1.44 on seeds 25-36
# (league_kennen +1.47 in the same batch). A 30 s pool (+1.22) or three hit checks (+1.31) changed little; more healing
# (+1.58) was too strong.
P = {
    # stats (Magician base: attack 80 +6, ability power 40 +20, hp 900 +100, defence 20 +7, mr 20 +3, move 900);
    # League's Vladimir: 450 range, a battle mage who drinks through the fight, 607 +110 hp
    "hp": 1000, "hp_g": 105, "atk": 72, "atk_g": 5, "mp": 40, "mp_g": 20, "def": 22, "def_g": 7, "mr": 22, "mr_g": 3,
    "ms": 910, "ms_g": 10,
    # attack: the bolt leaves the raised hand on atk_st (attack frame 4)
    "atk_range": 48000, "atk_dur": 25, "atk_cd": 85, "atk_st": 12, "bolt_speed": 5000, "bolt_y": -3000,
    # skill: Q Transfusion (League: 600 range, 80-220 + 60% AP, heal 20-120 + 35% AP; Crimson Rush +85% damage,
    # double heal, +10% move speed; cd 9-5 s)
    "q_cd": 240, "q_range": 55000, "q_dur": 26, "q_st": 11, "q_dmg": 100, "q_ap": 75, "q_hp": 5, "q_heal": 40,
    "q_heal_ap": 30, "q_rush": 180, "q_ms": 30, "q_ms_t": 60, "q1_t": 1800, "orb_speed": 4500,
    # skill2: E Tides of Blood (League: 600 radius, full charge 1 s: 60-180 + 80% AP + 6% bonus hp, slow 40% 0.5 s,
    # cd 13-9 s)
    "e_cd": 480, "e_dur": 68, "e_rel": 58, "e_r": 32000, "e_dmg": 90, "e_ap": 70, "e_hp": 5, "e_slow": 40,
    "e_slow_t": 30, "e_speed": 4500, "e_y": -3000,
    # W Sanguine Pool (League: 2 s, 300 radius, 80-280 + 10% bonus hp over 2 s, slow 40%, heal 15% of it, costs 20%
    # current hp, cd 28-12 s)
    "w_cd": 1200, "w_t": 120, "w_n": 4, "w_r": 22000, "w_dmg": 25, "w_ap": 10, "w_hp": 2, "w_slow": 40,
    "w_heal": 15, "w_heal_ap": 8, "w_cost": 5, "poll": 3, "poll_t": 36000,
    # the main pack's danger check (in his attack): two enemy champions within d_near, or hit at h_n checks in a row
    "d_near": 30000, "h_n": 2, "h_t": 150,
    # the native add-on (addons/league_vladimir_pool): the pool below n_hp% health with an enemy champion within n_near;
    # it pays League's cost itself, n_cost% of his current health (the data reads only max health: w_cost% of it, which
    # took a 3% Vladimir to 1 health in the add-on's first log, 2026-10-08)
    "n_hp": 35, "n_near": 60000, "n_cost": 20,
    # ult: R Hemoplague (League: 700 range, 375 radius, +10% damage taken 4 s, then 150-350 + 70% AP, heal 150-250
    # (+ per champion), cd 120-80 s)
    "r_cd": 3600, "r_range": 60000, "r_dur": 26, "r_st": 11, "r_rad": 26000, "r_amp": 10, "r_t": 180, "r_dmg": 200,
    "r_ap": 80, "r_hp": 6, "r_heal": 70, "r_heal_ap": 30,
    # the combos
    "eq_t": 150, "combo_pct": 70, "r_blink": 30000, "r_stop": 22000, "blink_speed": 10000, "r_ring": 18,
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
    dur = "WithShield" if tick == "shield" else {"Time": {"tick": tick}}
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


def ap(dmg, ratio, hp=0, pct=100):
    """Magic damage; `hp` = % of his max health (Crimson Pact); pct scales all three (Crimson Rush, the combos)."""
    return {"type": "ApAttack", "damage": dmg * pct // 100, "attack_ratio": ratio * pct // 100,
            "hp_ratio": hp * pct // 100, "can_crit": False}


def heal(amount, ap_ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap_ratio, "heal_type": "Caster"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
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


def back(name, speed, rng, end=()):
    return {"type": "BackToCasterLinearProjectile", "name": n(name), "speed": speed, "range": rng,
            "shape": circle(1000), "penetrate": True, "applied_target": "Enemy", "applied_effects": [],
            "end_effects": list(end)}


def lob(name, travel, end, target="EnemyWithoutTower"):
    """A hidden ParabolicProjectile: lands where its target stood when it left; end_effects run on that point."""
    return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
            "range_effect_name": "", "shape": circle(1), "applied_target": target, "applied_effects": [],
            "end_effects": list(end)}


def zone(name, radius, delay, apply_, target, effects):
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": delay, "apply": apply_,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, native=False, pay=None):
    """native: the add-on's copy - no danger check in the attack, the add-on's passive sets `w_go` by his health and
    pays the pool's cost (pay: the data's w_cost% of max health, default: not native)."""
    pay = not native if pay is None else pay
    # ------------------------------------------------------------------ E's nova (E, and the E-W / R E combos)
    def nova(pct, pic):
        hit = [ap(p["e_dmg"], p["e_ap"], p["e_hp"], pct), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]),
               view("e_hit"), tsfx("e_hit")]
        return combine(cview(pic), sfx("e_cast"),
                       around(p["e_r"], "EnemyWithoutTower", [homing("e_bolt", p["e_speed"], p["e_y"], "Enemy", hit)]),
                       # E -> Q: a bolt on a champion opens the window (a champion-only twin, nothing to see)
                       around(p["e_r"], "EnemyChampion", [homing("e_mark", p["e_speed"], p["e_y"], "EnemyChampion",
                                                                 [refresh("eq", p["eq_t"])])]))

    # ------------------------------------------------------------------ W Sanguine Pool (from the poll)
    def pulse():
        return combine(around(p["w_r"], "EnemyWithoutTower", [ap(p["w_dmg"], p["w_ap"], p["w_hp"]),
                                                              buff("w_drain", 30, move_speed_mult=-p["w_slow"])]),
                       on_me(heal(p["w_heal"], p["w_heal_ap"])))

    step = p["w_t"] // p["w_n"]
    pool = combine(
        *rm("w_go"), flag("w_cd", p["w_cd"]),
        *([flag("w_pay", 2, undying=True),
           on_me({"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": p["w_cost"], "target_hp_ratio": 0,
                  "attack_effect_type": "Target"})] if pay else []),
        {"type": "CasterInvisible", "tick": p["w_t"]},
        flag("w_in", p["w_t"], damaged_reduce=100, cc_immune=True),
        anim("skill_w", p["w_t"]), cview("w_splash"), sfx("w_cast"),
        *[delayed(step * k + step // 2, pulse()) for k in range(p["w_n"])],
        # E-W: out of the pool with a full nova when E is ready
        delayed(p["w_t"] - 6, cview("w_splash"), sfx("w_out"), sw("e_cd", NONE, nova(p["combo_pct"], "e_burst"))))
    # the poll: every `poll` ticks while it runs; its own flag lives a little longer than one period, so a poll that
    # died with him (an AddCasted ends with its target) is started again by his next attack or spell
    poll = sw("polling", NONE, combine(
        flag("polling", p["poll"] + 2),
        on_me(casted(p["poll_t"], p["poll"], refresh("polling", p["poll"] + 2), sw("w_cd", NONE, sw("w_go", pool))))))

    # ------------------------------------------------------------------ the main pack's danger check (in the attack)
    hurt = [f"h_{k}" for k in range(1, p["h_n"] + 1)]

    def hurt_up():
        out = combine(flag("h_1", p["h_t"]))
        for k in range(1, p["h_n"] + 1):
            nxt = min(k + 1, p["h_n"])
            out = sw(f"h_{k}", combine(*rm(*hurt), flag(f"h_{nxt}", p["h_t"])), out)
        return out

    arm_sensor = combine(on_me({"type": "Shield", "amount": 1, "attack_ratio": 0, "ap_ratio": 0, "tick": 36000}),
                         flag("sense", "shield"))
    sensor = sw("sense", NONE, combine(hurt_up(), arm_sensor))
    count = around(p["d_near"], "EnemyChampion", [sw("n_1", flag("n_2", 3), flag("n_1", 3))])
    by_hurt = sw(f"h_{p['h_n']}", combine(*rm(*hurt), refresh("w_go", 30)))
    danger = combine(*rm("n_1", "n_2"), count, delayed(1, sw("n_2", refresh("w_go", 30), by_hurt)))
    check = NONE if native else sw("w_cd", NONE, combine(sensor, danger))

    # ------------------------------------------------------------------ attack
    bolt = homing("a_bolt", p["bolt_speed"], p["bolt_y"], "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_shot"), bolt, check, poll), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Transfusion (+ Crimson Rush)
    def drink(rush):
        k = 2 if rush else 1
        orb = "q_rush" if rush else "q_orb"
        ret = back(orb, p["orb_speed"], 200000, end=[on_me(heal(p["q_heal"] * k, p["q_heal_ap"] * k)), cview("q_heal"),
                                                    sfx("q_heal")]
                   + ([refresh("q_haste", p["q_ms_t"], move_speed_mult=p["q_ms"])] if rush else []))
        pct = p["q_rush"] if rush else 100
        return combine(ap(p["q_dmg"], p["q_ap"], p["q_hp"], pct), view("q_drain"), tsfx("q_rush" if rush else "q_hit"),
                       lob("q_link", 1, [ret]))

    plain_q = sw("q1", combine(*rm("q1"), drink(True)), combine(flag("q1", p["q1_t"]), drink(False)))
    q_tree = sw("eq", combine(*rm("eq"), drink(True)), plain_q)          # E -> Q: Crimson Rush at once
    skill = action("skill", p["q_dur"], p["q_cd"], p["q_st"], p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(sfx("q_cast"), q_tree, poll))

    # ------------------------------------------------------------------ skill2: E Tides of Blood
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_r"], "None", "EnemyWithoutTower",
                    combine(anim("skill2", p["e_dur"]), flag("e_cd", p["e_cd"]), flag("e_chg", p["e_rel"]),
                            sfx("e_charge"), poll, delayed(p["e_rel"], nova(100, "e_burst"))))

    # ------------------------------------------------------------------ ult: R Hemoplague (+ Flash R E)
    plague = [buff("r_mark", p["r_t"], damaged_amplify=p["r_amp"]),
              delayed(p["r_t"], ap(p["r_dmg"], p["r_ap"], p["r_hp"]), view("r_burst"), tsfx("r_burst"))]
    drink_r = [delayed(p["r_t"], heal(p["r_heal"], p["r_heal_ap"]), view("r_heal_on"))]
    land = [view("r_cloud"), sfx("r_land"),
            zone("r_zone", p["r_rad"], 2, 1, "EnemyWithoutTower", plague),
            zone("r_zone_c", p["r_rad"], 2, 1, "EnemyChampion", drink_r)]
    cloud = lob("r_lob", 1, land, target="EnemyChampion")
    hop = line("r_path", p["blink_speed"], p["r_blink"], p["r_stop"], 0, "EnemyChampion", False, [],
               [{"type": "Teleport"}, cview("c_blink"), sfx("c_blink")])
    flash = combine(cview("c_blink"), hop, delayed(p["r_st"] + p["r_ring"], nova(p["combo_pct"], "e_burst")))
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
                 combine(sw("e_cd", NONE, flash), sfx("r_cast"), poll, delayed(p["r_st"] - 1, cloud)))

    # ------------------------------------------------------------------ views (every picture on a unit or the ground is
    # left-right symmetric, every flying one top-bottom symmetric: tools/art/import_vladimir.py FLIP_LR / FLIP_TB)
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_("a_bolt"), P_("q_orb"), P_("q_rush"), P_("e_bolt")]
    views_e = [E("a_hit", FX, 2), E("q_drain", FX, 2), E("q_heal", FX, 2, False), E("e_hit", FX, 2),
               E("e_burst", BIG, 2, False), E("w_splash", BIG, 2, False), E("r_cloud", BIG, 2, False),
               E("r_burst", FX, 2), E("r_heal_on", FX, 2), E("c_blink", FX, 2, False)]
    views_b = [B_("q1", FX, -1), B_("e_chg", FX, 2), B_("w_in", BIG, -1), B_("w_drain", FX, 2),
               B_("r_mark", FX, 2)]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Heal"],
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
        kit["passive"] = {"passive_ref": "league_vladimir_pool:guard",
                          "params": {"hp": int(p["n_hp"]), "near": int(p["n_near"]),
                                     "cost": int(p["n_cost"])}}
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
