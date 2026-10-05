"""Build league_alistar.data_champion (support, Util, tank) from the parameters P.

    python tools/kit/build_alistar.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-05: all the recommended options, plus 「EQ二连也要做吧」 = E -> Q):
  passive Triumphant Roar: every champion his crowd control lands on (Q / W->Q knock-ups, W's headbutt, E's stun)
          climbs a p1 -> p2 ladder; the p_need-th, with p_cd off, roars: he heals p_heal + p_ap% AP and every allied
          champion within p_r heals p_ally + p_ally_ap% AP. (League also counts nearby minion deaths - not built.)
  E       Trample, folded into Q and W->Q: with e_cd off a cast starts the trample - one AddCasted on himself (period
          e_period, e_t ticks): each stomp deals e_dmg + e_ap% AP round him (EnemyWithoutTower within e_r) and, when it
          touches an enemy champion, climbs the e1..e4 ladder; the fifth such stomp arms e_ready: his next basic attack
          on a champion (a hidden champion-only twin of the punch) stuns e_stun ticks and deals e_proc + e_proc_ap% AP.
  skill   Q Pulverize, E -> Q: a `None` cast on `EnemyWithoutTower` (q_range). The trample starts at the cast (its first
          stomp on the wind-up), the slam on q_st: q_dmg + q_ap% AP and q_up ticks airborne on every enemy within q_r;
          each champion it throws up also counts a stomp (League's E Q: the stomps land on them in the air).
  skill2  W Headbutt -> Q Pulverize on an enemy champion (w_range): he charges (MoveToTarget w_speed), the headbutt
          (w_dmg + w_ap%) knocks back the champions in front of him (Knockback w_kb_speed x w_kb_t), and w_land ticks
          later he slams where he stands - the same Pulverize ring, catching the champion where the push left him.
          Starts the trample too.
  ult     R Unbreakable Will, armed like league_blitzcrank R: a 3-tick `None` cast on `EnemyChampion` (r_arm_range) arms
          r_armed for r_arm ticks; every action and a pulse every 15 ticks fire it when an enemy champion is within r_r
          or he is crowd-controlled himself: r_imm ticks of crowd-control immunity (League's cleanse), r_red% less damage
          for r_t ticks, the roar. Unused, the cooldown is refunded.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_alistar.data_champion")
ID = "league_alistar"
FX = "asset/league/effects/league_alistar_fx"
BIG = "asset/league/effects/league_alistar_big"

# Numbers = candidate c5 of the 10-min classic-SDK simulations (al_sim/sim/kd.py, support lane against the five base
# supports, both sides, 2026-10-05): +1.65 on seeds 1-24, +1.47 on seeds 25-48 (league_leona +0.78 / +1.23 on the same
# seeds). The draft c0 was +6.08 (deal 9254 against Leona's 3705): Q and W->Q every few seconds, each a 1 s knock-up on
# everything round him. Cut: Q 80+80% -> 50+50% and cd 360 -> 600, W's landing slam its own 30+30%, W 70+80% -> 40+50%
# and cd 480 -> 720, the stomps 15+12% -> 8+6% and trample cd 600 -> 1080, the roar's heals, R 60% -> 50%. League's 1 s
# knock-up kept (0.75 s, c3, was +0.85).
P = {
    # stats (the pack's tank supports: Leona hp 1100 +120, def 40, mr 30, atk 80, interval 80, range 25000)
    "hp": 1100, "hp_g": 120, "atk": 80, "atk_g": 6, "mp": 25, "mp_g": 15, "def": 38, "def_g": 8, "mr": 28, "mr_g": 4,
    "ms": 1000, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 26, "atk_cd": 80, "atk_st": 12,
    # passive: Triumphant Roar (League: 7 stacks, 3 s cooldown, self 5% max hp, allies x1.4)
    "p_need": 3, "p_cd": 300, "p_r": 40000, "p_heal": 40, "p_ap": 20, "p_ally": 50, "p_ally_ap": 30,
    # E: Trample (League: radius 350, 80-230 + 70% AP over 5 s, 5 stomps on champions -> stun 1 s, cd 12.5-9.5 s)
    "e_cd": 1080, "e_t": 180, "e_period": 30, "e_r": 24000, "e_dmg": 8, "e_ap": 6, "e_hold": 300,
    "e_stun": 60, "e_proc": 50, "e_proc_ap": 50,
    # skill: Q Pulverize (League: radius 375, 60-260 + 80% AP, knock-up 1 s, cd 14-10 s)
    "q_cd": 600, "q_range": 24000, "q_r": 28000, "q_dur": 30, "q_st": 14, "q_dmg": 50, "q_ap": 50, "q_up": 60,
    # skill2: W Headbutt -> Q (League: range 650, 55-330 + 100% AP, knock-back 700, cd 15-10 s)
    "w_cd": 720, "w_range": 55000, "w_speed": 3500, "w_dmg": 40, "w_ap": 50, "w_hit_r": 8000, "w_kb_speed": 2500,
    "w_kb_t": 8, "wq_dmg": 30, "wq_ap": 30, "w_land": 6, "w_slam": 6, "w_dash_anim": 12, "w_dur": 14,
    # ult: R Unbreakable Will (League: cleanse, 55-75% less damage 7 s, cd 120/100/80 s)
    "r_cd": 3600, "r_arm": 600, "r_arm_range": 70000, "r_r": 32000, "r_t": 420, "r_red": 50, "r_imm": 60,
    "r_anim": 30,
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
    duration = tick if isinstance(tick, (str, dict)) else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": duration, **fields},
            "only_to_enemy": False}


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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def heal(amount, ap_ratio, kind="Caster"):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ap_ratio, "heal_type": kind}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit."""
    return around(1000, "AllyOnlySelf", effects)


def casted(duration, period, *effects, kind="Heal"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    # ------------------------------------------------------------------ passive: Triumphant Roar
    roar = combine(flag("p_cd", p["p_cd"]), cview("p_roar"), sfx("p_roar"),
                   on_me(heal(p["p_heal"], p["p_ap"]), view("p_heal")),
                   around(p["p_r"], "AllyNotSelf", [heal(p["p_ally"], p["p_ally_ap"], "Ally"), view("p_heal")]))
    hold = {"Time": {"tick": 1800}}

    def p_stack():
        """A champion his crowd control landed on: one step up the roar ladder (or the roar)."""
        names = [f"p{i}" for i in range(1, p["p_need"])]
        eff = sw("p_cd", NONE, combine(*rm(*names), roar))          # all steps there: roar
        for i in range(len(names), 0, -1):                         # p_i there -> go on; missing -> add it
            eff = sw(names[i - 1], eff, flag(names[i - 1], hold)) if i == 1 else \
                sw(names[i - 1], eff, sw(names[i - 2], flag(names[i - 1], hold), NONE))
        return eff

    # ------------------------------------------------------------------ E: Trample
    e_names = ["e1", "e2", "e3", "e4"]

    def e_count():
        """A stomp (or the slam) that touched an enemy champion: one step up to e_ready."""
        e_hold = {"Time": {"tick": p["e_hold"]}}
        eff = combine(*rm(*e_names), *rm("e_ready"), flag("e_ready", p["e_hold"]), cview("e_ready"), sfx("e_ready"))
        for i in range(len(e_names), 0, -1):
            add = {"type": "AddCasterBuff", "buff_state": {"name": n(e_names[i - 1]), "duration": e_hold},
                   "only_to_enemy": False}
            eff = sw(e_names[i - 1], eff, add) if i == 1 else sw(e_names[i - 1], eff, sw(e_names[i - 2], add, NONE))
        return eff

    stomp = combine(cview("e_stomp"), sfx("e_step"), *rm("e_champ"),
                    around(p["e_r"], "EnemyChampion", [flag("e_champ", 1)]),
                    around(p["e_r"], "EnemyWithoutTower", [ap(p["e_dmg"], p["e_ap"]), view("e_hit")]),
                    sw("e_champ", e_count()))
    trample = sw("e_cd", NONE, combine(flag("e_cd", p["e_cd"]), flag("e_on", p["e_t"]), stomp,
                                       on_me(casted(p["e_t"] + 1, p["e_period"], stomp))))

    # ------------------------------------------------------------------ ult check (armed)
    fire_r = combine(*rm("r_armed"), flag("r_imm", p["r_imm"], cc_immune=True),
                     flag("r_on", p["r_t"], damaged_reduce=p["r_red"]), anim("ult", p["r_anim"]),
                     cview("r_cast"), sfx("r_cast"))
    r_check = sw("r_armed", combine(*rm("r_go"), pick(p["r_r"], "EnemyChampion", flag("r_go", 1)),
                                    pick(1, "AllyChampionInCC", flag("r_go", 1)), sw("r_go", fire_r)))

    # ------------------------------------------------------------------ Pulverize (Q, and W's landing)
    def pulverize(name, dmg, ratio):
        return combine(cview(name), sfx("q_hit"),
                       around(p["q_r"], "EnemyWithoutTower", [ap(dmg, ratio),
                                                             {"type": "Airborne", "duration": p["q_up"]},
                                                             view("q_up")]),
                       around(p["q_r"], "EnemyChampion", [p_stack(), e_count()]))

    # ------------------------------------------------------------------ attack (E's stun punch on champions)
    punch = homing("e_punch", 30000, 0, "EnemyChampion",
                   [*rm("e_ready"), ap(p["e_proc"], p["e_proc_ap"]), {"type": "Stun", "duration": p["e_stun"]},
                    buff("e_stun", p["e_stun"]), view("e_hit_stun"), tsfx("e_stun"), p_stack()])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(r_check, attack(0, 100), view("a_hit"), tsfx("a_hit"), sw("e_ready", punch)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: E -> Q
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "None", "EnemyWithoutTower",
                   combine(r_check, sfx("q_cast"), trample, delayed(p["q_st"] - 1, pulverize("q_slam", p["q_dmg"], p["q_ap"]))))

    # ------------------------------------------------------------------ skill2: W -> Q
    butt = around(p["w_hit_r"], "EnemyChampion",
                  [ap(p["w_dmg"], p["w_ap"]), {"type": "Knockback", "speed": p["w_kb_speed"], "tick": p["w_kb_t"]},
                   view("w_hit"), tsfx("w_hit"), p_stack()])
    land = [cview("w_butt"), sfx("w_hit"), butt,
            delayed(p["w_land"], anim("skill", p["q_dur"] - p["q_st"] + p["w_slam"]),
                    delayed(p["w_slam"], pulverize("w_slam", p["wq_dmg"], p["wq_ap"])))]
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
                    combine(r_check, sfx("w_cast"), cview("w_dash"), anim("skill2", p["w_dash_anim"]), trample,
                            {"type": "MoveToTarget", "speed": p["w_speed"], "range": p["w_range"] + 40000,
                             "end_effects": land}))

    # ------------------------------------------------------------------ ult: arms Unbreakable Will
    pulses = [delayed(t, sw("r_armed", r_check)) for t in range(15, p["r_arm"], 15)]
    ult = action("idle", 3, p["r_cd"], 1, p["r_arm_range"], "None", "EnemyChampion", combine(
        *rm("r_armed"), flag("r_armed", p["r_arm"]), r_check, *pulses,
        delayed(p["r_arm"], sw("r_armed", combine(*rm("r_armed"), flag("r_refund", 3, ult_cooldown_mult=4900))))),
        key="ult")

    # ------------------------------------------------------------------ views
    # a caster picture played after the action's first tick must not follow him (the red side's mirroring)
    E = lambda name, anim_=FX, z=1, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    P_ = lambda name, anim_=FX, z=1: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                      "repeat": True, "z": z}
    views_p = []  # e_punch: a hidden twin of the punch
    views_e = [E("a_hit", FX, 2), E("q_slam", BIG, -1, False), E("w_slam", BIG, -1, False), E("q_up", FX, 2),
               E("w_dash", BIG, 1), E("w_butt", FX, 2, False), E("w_hit", FX, 2), E("e_stomp", BIG, -1, False),
               E("e_hit", FX, 2), E("e_ready", FX, 2, False), E("e_hit_stun", FX, 2),
               E("p_roar", BIG, 1, False), E("p_heal", FX, 2), E("r_cast", BIG, 1, False)]
    views_b = [P_("e_stun", FX, 2), P_("r_on", BIG, -1)]   # the rage aura behind him: its flames stand round him
    return {
        "id": ID, "category": "Util", "tags": ["AP", "Magic", "Melee", "Tank", "CC", "Heal"],
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
        p[k] = v if isinstance(p[k], str) else type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
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
