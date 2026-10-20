"""Build league_volibear.data_champion (top, Melee fighter-tank) from the parameters P.

    python tools/kit/build_volibear.py [--set key=value ...] [--out file] [--params json] [--nodes] [--native]

Kit (the user's picks, 2026-10-19: top, plan A with the add-on league_volibear). TFM2 has three active slots for
League's four buttons: Thundering Smash is `skill`, Sky Splitter `skill2`, Stormbringer the `ult`; Frenzied Maul (a
5-second empowered attack in League too) and the passive ride in his attack.
  passive The Relentless Storm (狂雷渐起): every attack hit, Q hit and E cast gives a stack (p1..p5, p_t ticks, all
          renewed together), p_as% attack speed each. With five his attacks also throw lightning: a splash from the
          target (p_r round it), p_dmg + p_ap% AP magic to every enemy it reaches (League: the target and 4 more;
          the add-on chains to the 4 nearest).
  W       Frenzied Maul (暴怒撕咬, in the attack): with w_cd off his next attack is the maul (the `attack_w` strip):
          w_dmg + w_ratio% AD more and w_hp% of his max health on top of the blow. On a champion the first maul marks
          (a caster flag `w_mark`, w_mark_t ticks - nothing reads a buff on a target; the mark picture rides on the
          champion); the next maul while it holds bites w2% harder and heals him w_heal + w_heal_ad% AD (League heals a
          share of his missing health: the add-on's).
  skill   Q Thundering Smash (擂首一击), `Targeting` on `EnemyChampion` (q_range): q_ms% move speed for q_t ticks and he
          charges on all fours (`skill_run`, MoveToTarget q_speed); on reaching the champion the smash (`skill`, the hit
          q_rel ticks in): his blow + q_dmg + q_ratio% AD and a q_stun-tick stun.
          Combo Q -> W (the user: 「有连招要做连招」「都要帮我补」; League's Volibear bites the champion he has just
          stunned): the smash also takes the maul's cooldown flag w_cd off, so his next attack - started on the
          stunned champion while the stun holds - is Frenzied Maul from its first tick (the bite on w_st).
  skill2  E Sky Splitter (霹天雳地), `Position` on `EnemyWithoutTower` (e_range): a storm mark on the point, e_delay
          ticks later the bolt (radius e_r): e_dmg + e_ap% AP magic, e_hp% of a champion's max health (true: ApAttack
          has no target-health field), e_slow% slow for e_slow_t; standing in it shields him e_sh + e_sh_ap% AP for
          e_sh_t ticks (League: 14% max health + 75% AP; a Shield has no health field).
  ult     R Stormbringer (天声震落), `Targeting` on `EnemyChampion` (r_range): he leaps (cc_immune, MoveToTarget r_speed)
          and lands on him: r_dmg + r_ratio% AD to every enemy within r_r, r_slow% slow for r_slow_t; for r_form ticks
          he keeps r_hp more health and r_range_add more attack range (League's transformation). League also disables
          the towers near the landing: the add-on's.
The add-on copy (--native, addons/league_volibear): the five-stack lightning is league_volibear:storm (the target and
the 4 nearest enemies), the maul's champion hit league_volibear:maul (the mark kept on the champion bitten, the second
bite healing by missing health), R's landing league_volibear:stormbringer (nearby enemy towers silenced).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_volibear.data_champion")
ID = "league_volibear"
FX = "asset/league/effects/league_volibear_fx"
BIG = "asset/league/effects/league_volibear_big"

# League units x 100 = ours for skill ranges (the pack's melee attack is 25000 against League's 150). Release ticks
# from the strips (rig_volibear.MS): the attack's rake on tick 12 (frame 3), the maul's bite on tick 10 (attack_w frame 3),
# Q's slam 17 ticks into the pounce (frame 4), E's warning when the claw is up (13, skill2 frame 3), R in the air for
# the ult tag's 60 ticks and its landing slam 4 ticks into ult_land. League 16.20 (Volibear.bin): Q 10-60 +... bonus AD,
# +8.5-59% ms toward champions for 4 s, stun 1 s, cd 14-10; W 5-130 +100% bonus AD +6% bonus hp, mark 8 s, the
# second x1.5 and heals 20-95 + 8-23% missing hp, cd 5; E 50-230 +70% AP +10-16% max hp magic, r 325, slow 40% 2 s,
# shield 14% max hp + 75% AP 3 s, cd 16, range 1200; R leap 700, 300-1300 +250% bonus AD +125% AP, r 550 (radius
# 300 on landing), +175-1050 hp and +50 range for 12 s, slow 50% 1 s, towers off 1-7 s, cd 160-110; passive 5% as a
# stack (x5, 6 s), lightning 11-60 +40% AP to the target and 4 more.
P = {
    "hp": 1100, "hp_g": 105, "atk": 88, "atk_g": 14, "mp": 20, "mp_g": 8, "def": 32, "def_g": 7, "mr": 26, "mr_g": 4,
    "ms": 1020, "ms_g": 10,
    "atk_range": 25000, "atk_dur": 30, "atk_cd": 72, "atk_st": 12,
    # passive The Relentless Storm
    "p_t": 360, "p_as": 6, "p_dmg": 30, "p_ap": 40, "p_r": 22000, "p_speed": 9000,
    # W Frenzied Maul (in the attack)
    "w_cd": 300, "w_dur": 28, "w_st": 10, "w_dmg": 30, "w_ratio": 40, "w_hp": 2, "w_mark_t": 480, "w2": 50, "w_heal": 40, "w_heal_ad": 50,
    # the add-on's heal (League: 8-23% of his missing health by rank)
    "w_heal_miss": 12,
    # Q Thundering Smash
    "q_cd": 720, "q_range": 60000, "q_ms": 40, "q_t": 240, "q_speed": 1600, "q_dur": 33, "q_rel": 17, "q_dmg": 40,
    "q_ratio": 60, "q_stun": 60, "q_run": 64,
    # E Sky Splitter
    "e_cd": 900, "e_range": 100000, "e_dur": 30, "e_rel": 13, "e_delay": 90, "e_r": 30000, "e_dmg": 80, "e_ap": 70,
    "e_hp": 6, "e_slow": 40, "e_slow_t": 120, "e_sh": 120, "e_sh_ap": 75, "e_sh_t": 180,
    # R Stormbringer
    "r_cd": 3600, "r_range": 70000, "r_speed": 2200, "r_up": 60, "r_land_t": 24, "r_rel": 4, "r_r": 32000,
    "r_dmg": 200, "r_ratio": 120, "r_slow": 50, "r_slow_t": 60, "r_form": 720, "r_hp": 350, "r_range_add": 5000,
    # the add-on's towers (League: 1-7 s by rank)
    "r_tower_r": 55000, "r_tower_t": 240,
    "vo_gap": 600,
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


def sw(buff_, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff_), "effect_buff": yes, "effect_none": no or NONE}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def refresh(name, tick, **fields):
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


def attack(dmg, ratio, hp=0, mine=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": mine, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def true_hp(pct):
    return {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": pct,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone, also from a projectile's hit (a `Delayed` here is queued on him)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def alive(*effects):
    """Run only while he lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def homing(name, target, effects, speed):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def splash(name, speed, rng, effects):
    return {"type": "TargetSplashProjectile", "name": n(name), "speed": speed, "range": rng, "y_offset": 5000,
            "applied_target": "EnemyWithoutTower", "applied_effects": [T(e) for e in effects]}


def zone(name, radius, effects, target="EnemyWithoutTower"):
    """A one-tick area where it is started (a projectile's end_effects, or a `Position` cast's point)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def voice(name, p):
    """His spoken line, at most one every vo_gap ticks."""
    return sw("vo_cd", NONE, combine(flag("vo_cd", p["vo_gap"]), sfx(name)))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def native(name):
    return {"type": "Native", "effect_ref": f"{ID}:{name}"}


def stacks(p):
    """A passive stack: the count read from the top (p4 .. p1), then all of them taken off and put back one more
    (p_t ticks each, p_as% attack speed each), so every stack is renewed as in League."""
    def put(k):
        return combine(*rm("p1", "p2", "p3", "p4", "p5"),
                       *[flag(f"p{i}", p["p_t"], attack_speed_mult=p["p_as"]) for i in range(1, k + 1)])
    ladder = put(1)
    for k in range(1, 5):
        ladder = sw(f"p{k}", put(k + 1), ladder)
    return ladder


def build(p):
    nat = bool(p["native"])
    stack = stacks(p)

    # ------------------------------------------------------------------ passive: the five-stack lightning
    bolt = [ap(p["p_dmg"], p["p_ap"]), view("p_hit"), tsfx("p_hit")]
    storm = sw("p5", combine(sfx("p_bolt"), native("storm") if nat else splash("p_bolt", p["p_speed"], p["p_r"], bolt)))

    # ------------------------------------------------------------------ attack + W Frenzied Maul
    blow = combine(sfx("a_swing"), homing("a_blow", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit"), stack],
                                          8000))
    heal = {"type": "Heal", "amount": p["w_heal"], "attack_ratio": p["w_heal_ad"], "ap_ratio": 0, "heal_type": "Caster"}
    second = combine(*rm("w_mark"), attack(p["w_dmg"] * p["w2"] // 100, p["w_ratio"] * p["w2"] // 100,
                                           mine=p["w_hp"] * p["w2"] // 100),
                     on_me(heal, cview("w_heal")), tsfx("w_heal"))
    first = combine(refresh("w_mark", p["w_mark_t"]), buff("w_mark", p["w_mark_t"]))
    maul = combine(flag("w_cd", p["w_cd"]), anim("attack_w", p["w_dur"]), sfx("w"), voice("vo_w", p),
                   delayed(p["w_st"] - 1,
                           homing("w_bite", "Enemy", [attack(p["w_dmg"], 100 + p["w_ratio"], mine=p["w_hp"]),
                                                      view("w_hit"), tsfx("w_hit"), stack], 8000),
                           homing("w_twin", "EnemyChampion", [native("maul") if nat else sw("w_mark", second, first)],
                                  8000), storm))
    # the maul is chosen as the attack starts, so its own strip (attack_w) plays from the first tick
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      sw("w_cd", delayed(p["atk_st"] - 1, blow, storm), maul), atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Thundering Smash
    # the Q -> W combo: the smash takes w_cd off, so his next attack - on the stunned champion - is the maul
    smash = [attack(p["q_dmg"], 100 + p["q_ratio"]), {"type": "Stun", "duration": p["q_stun"]},
             buff("q_stun", p["q_stun"]), view("q_hit"), tsfx("q_hit"), stack, *rm("w_cd")]
    reach = [anim("skill", p["q_dur"]), sfx("q_smash"), delayed(p["q_rel"], *smash)]
    skill = action("skill_run", 3, p["q_cd"], 1, p["q_range"], "Targeting", "EnemyChampion",
                   combine(refresh("q_ms", p["q_t"], move_speed_mult=p["q_ms"]), anim("skill_run", p["q_run"]),
                           sfx("q"), voice("vo_q", p),
                           {"type": "MoveToTarget", "speed": p["q_speed"], "range": p["q_range"] + 40000,
                            "end_effects": reach}), key="skill")

    # ------------------------------------------------------------------ skill2: E Sky Splitter
    struck = [ap(p["e_dmg"], p["e_ap"]), buff("e_slow", p["e_slow_t"], move_speed_mult=-p["e_slow"]), view("e_hit"),
              tsfx("e_hit")]
    shield = {"type": "Shield", "amount": p["e_sh"], "attack_ratio": 0, "ap_ratio": p["e_sh_ap"], "tick": p["e_sh_t"]}
    fall = [view("e_bolt"), sfx("e_bolt"), zone("e_z", p["e_r"], struck),
            zone("e_c", p["e_r"], [true_hp(p["e_hp"])], target="EnemyChampion"),
            zone("e_me", p["e_r"], [shield, flag("e_sh", p["e_sh_t"])], target="AllyOnlySelf")]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Position", "EnemyWithoutTower",
                    combine(sfx("e"), voice("vo_e", p), on_me(stack),
                            delayed(p["e_rel"] - 1, view("e_cloud"), sfx("e_cloud")),
                            delayed(p["e_rel"] - 1 + p["e_delay"], *fall)))

    # ------------------------------------------------------------------ ult: R Stormbringer
    hit = [attack(p["r_dmg"], p["r_ratio"]), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]), view("r_hit"),
           tsfx("r_hit")]
    towers = [native("stormbringer")] if nat else []
    land = [anim("ult_land", p["r_land_t"]), sfx("r_land"),
            delayed(p["r_rel"], cview("r_land"), around(p["r_r"], "EnemyWithoutTower", hit), *towers),
            refresh("r_form", p["r_form"], hp=p["r_hp"], range=p["r_range_add"]), on_me(stack)]
    leap = combine(anim("ult", p["r_up"]), sfx("r"), voice("vo_r", p), flag("r_air", p["r_up"], cc_immune=True),
                   {"type": "MoveToTarget", "speed": p["r_speed"], "range": 400000, "end_effects": land})
    ult = action("idle", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion", leap, key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=3: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    Pj = lambda name, anim_=FX: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                 "z": 2}
    views_p = [Pj("p_bolt")]
    views_e = [E("a_hit"), E("p_hit"), E("w_hit"), E("w_heal", BIG), E("q_hit"), E("e_cloud", BIG, -1, False),
               E("e_bolt", BIG, 3, False), E("e_hit"), E("r_land", BIG, -1), E("r_hit")]
    views_b = [B_("w_mark"), B_("q_ms", BIG, -1), B_("q_stun"), B_("e_slow"), B_("e_sh", BIG, 3), B_("r_form", BIG, -1)]
    if nat:
        # the add-on's buffs, shown by name: the chain lightning on each unit it strikes (p_hit's picture), the second
        # bite's heal on him (w_heal's), the silenced tower
        views_b += [dict(B_("p_zap"), tag="p_hit"), dict(B_("w_healed", BIG, 2), tag="w_heal"), B_("r_tower", BIG, 3)]
    extra = {}
    return {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "Tank", "CC"], **extra,
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
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
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
