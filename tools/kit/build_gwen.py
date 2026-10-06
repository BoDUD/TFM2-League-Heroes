"""Build league_gwen.data_champion (top, Assassin) from the parameters P.

    python tools/kit/build_gwen.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's picks, 2026-10-06: Q / E -> W combo / the mist hides her from afar while she stands in it / R throws
its three volleys from one cast / the passive's % max-health magic damage goes to a native add-on - "这个可以改rust" -
and the data pack keeps the closest it can read):
  passive A Thousand Cuts (千穿百孔): her attacks and every snip of Q and R's needles add p_dmg + p_ratio% AP magic
          damage; on enemy champions also p_hp% of their maximum health as TRUE damage (`FixedAttack target_hp_ratio`:
          nothing magic reads max health; League's magic 1% + 0.6% per 100 AP) and she heals p_heal + p_heal_r% AP
          (League: 50% of the passive's damage to champions).
  attack  A melee snip (100% AD, the passive). Every hit on an enemy adds a Q stack (q_n stacks, each q_keep ticks,
          refreshed by the next hit: League's 6 s, 4 stacks). While E's buff holds, the hit adds e_dmg + e_ratio% AP.
  skill   Q Snip Snip! (快刀剪乱): a `Targeting` cast on `EnemyWithoutTower` (q_range). She snips 1 + stacks small
          cuts (q_mini + q_mini_r% AP, the passive each) in the cone in front (q_cone_r, `DirDot` q_cone), q_gap ticks
          apart, then the big one (q_dmg + q_ratio% AP, the passive): the units in its centre (q_c_r, q_c_off in
          front) take q_true more as TRUE damage (League turns the centre's damage true). The stacks are spent.
  skill2  E Skip 'n Slash (断续疾走) -> W Hallowed Mist (丝缕缠流): a `Targeting` cast on `EnemyChampion` (e_range).
          She dashes onto the target (`MoveToTarget`, e_speed) and for e_t ticks her attacks gain e_as% attack speed,
          e_rng range and E's on-hit damage. Where she lands the Hallowed Mist (圣霭) settles for w_t ticks (radius
          w_r): every w_period ticks while she stands inside it she is `CasterInvisible` and has +w_def armour and magic
          resistance for w_period + 2 ticks - enemies away from her lose sight of her and cannot pick her, the ones
          that come close still can (League: untargetable to enemies outside the mist). Leaving it ends both within
          w_period + 2 ticks. (league_akali's first shroud: Ekko's anchor -> a zone on `AllyChampion` -> a
          `RandomTarget AllyOnlySelf` from the zone.)
  ult     R Needlework (引针簇射): a `Direction` cast on `EnemyChampion` (r_range): three volleys r_gap ticks apart,
          1, 3 and 5 needles (a `LineRangeProjectile` fan: r_w1 / r_w2 / r_w3 wide, r_len long, the hit r_apply ticks
          after it appears), each r_dmg1 / r_dmg2 / r_dmg3 + r_ratio% AP magic damage, the passive, and a slow of
          r_slow% for r_slow_t ticks. The volleys keep the cast's direction (dodgeable, as League's needles fly).
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_gwen.data_champion")
ID = "league_gwen"
FX = "asset/league/effects/league_gwen_fx"
BIG = "asset/league/effects/league_gwen_big"

# Numbers = candidate g4 of the 10-min classic-SDK simulations (tr_sim's kd.py copied to Temp/gw_sim, top lane against
# fighter, executioner, lancer, pole_warrior, knight and berserker, three lineups, both sides, 24 seeds a batch,
# 2026-10-06): +1.41 on seeds 1-24, +1.24 on 25-48 (league_fiora +1.22 / +1.47, league_tryndamere +1.29 / +1.02). The
# draft g0 was +1.55 / +2.00: hp 980 -> 950, Q 90 + 50% -> 70 + 40%, E +40% -> +30% attack speed, W 25 -> 22 resists
# (also cutting the passive to 8 went +1.42 / +0.53). The combos (2026-10-06) took g4 to +3.39; d2 brought it back:
# E's landing snip 60% AD without E's on-hit, the centre 40 -> 25 true, hp 950 -> 880, attack 80 -> 74, Q 70 -> 60
# (minis 15 -> 12), E +30% -> +25% attack speed, R 60/70/90 -> 50/60/75: +1.33 on seeds 1-24. Timings from the strips (tools/art/rig_gwen.py MS): the attack's
# thrust frame 4 at 190 ms (tick 11), Q's shut frames 3 / 5 / 7 at ticks 7 / 14 / 22, R's throw frame 4 at tick 10.
P = {
    # stats (Assassin AP base like league_diana / league_akali: attack 80 +10, magic power 50 +20, hp 950 +95, defence
    # 28 +8, mr 20 +3, move 1100); League's Gwen: 620 +114 hp, 63 AD, 39 armour, 340 move, 150 range
    "hp": 880, "hp_g": 98, "atk": 74, "atk_g": 10, "mp": 50, "mp_g": 20, "def": 30, "def_g": 8, "mr": 24, "mr_g": 4,
    "ms": 1080, "ms_g": 11,
    # attack
    "atk_range": 24000, "atk_dur": 24, "atk_cd": 56, "a_hit": 11,
    # passive A Thousand Cuts
    "p_dmg": 10, "p_ratio": 8, "p_hp": 1, "p_heal": 10, "p_heal_r": 6,
    # the add-on's (addons/league_gwen, League's): magic damage of p_hp% + p_hp_ap / 100 % per 100 AP of the
    # champion's maximum health in place of the true p_hp%; 1 = the copy for the add-on (league_gwen:cuts)
    "p_hp_ap": 60, "native": 0,
    # skill: Q Snip Snip! (League: cd 6.5-3.5 s, final 35-185 + 35% AP, minis 20% of it, 2 + 4 stacks, 6 s stacks)
    "q_n": 4, "q_keep": 360, "q_cd": 330, "q_range": 30000, "q_dur": 30, "q_t0": 6, "q_gap": 3, "q_final": 22,
    "q_mini": 12, "q_mini_r": 8, "q_dmg": 60, "q_ratio": 40, "q_true": 25, "q_cone_r": 30000, "q_cone": 300,
    "q_c_off": 16000, "q_c_r": 6000,
    # skill2: E Skip 'n Slash (League: 350 dash, 4 s, +17.5-92.5% AS, +75 range, 15 + 20% AP on hit, cd 13-11 s) ->
    # W Hallowed Mist (League: 4 s, radius 370, +20-32 armour and MR, cd 22-18 s)
    "e_cd": 900, "e_range": 45000, "e_speed": 6000, "e_tick": 8, "e_t": 240, "e_as": 25, "e_rng": 7500,
    "e_dmg": 15, "e_ratio": 20,
    "w_t": 240, "w_r": 37000, "w_period": 6, "w_def": 22,
    # ult: R Needlework (League: 3 casts, 1/3/5 needles, 35-95 + 10% AP each needle, slow 30-90% for 1.5 s, cd 120 s)
    "r_cd": 2400, "r_range": 70000, "r_gap": 36, "r_t0": 10, "r_len": 80000, "r_w1": 5000, "r_w2": 15000, "r_w3": 25000,
    "r_apply": 4, "r_delay": 12, "r_dmg1": 50, "r_dmg2": 60, "r_dmg3": 75, "r_ratio": 25, "r_slow": 40, "r_slow_t": 90,
    "r_anim": 24,
    # combos (the user: 「另外加一点格温高手的连招逻辑进去」): E's landing snip, E -> Q's centre on the target, R woven
    # with attacks
    "e_cut": 1, "e_cut_ratio": 60, "e_cut_bonus": 0, "eq_t": 120, "r_weave": 1,
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


def ap(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def true(dmg, hp=0):
    return {"type": "FixedAttack", "damage": dmg, "attack_ratio": 0, "hp_ratio": 0, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def heal(amount, ratio):
    return {"type": "Heal", "amount": amount, "attack_ratio": 0, "ap_ratio": ratio, "heal_type": "Caster"}


def around(shape, target, effects, forward=None):
    return {"type": "RangeEffect", "shape": circle(shape) if isinstance(shape, int) else shape, "target": target,
            "apply_type": "AroundCaster" if forward is None else {"Forward": {"offset": forward}},
            "effects": list(effects)}


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, y, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def fan(name, width, length, delay, apply, target, effects):
    return {"type": "LineRangeProjectile", "name": n(name), "width": width, "length": length, "delay": delay,
            "apply": apply, "applied_target": target, "applied_effects": [T(e) for e in effects]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p):
    q_n = p["q_n"]
    stacks = [f"qs{k}" for k in range(1, q_n + 1)]

    # ------------------------------------------------------------------ passive: A Thousand Cuts
    def cuts():
        """On every enemy: the magic part."""
        return ap(p["p_dmg"], p["p_ratio"])

    def cuts_champ():
        """On enemy champions only: max-health true damage (the add-on's copy: its magic damage) and her heal."""
        hp_part = {"type": "Native", "effect_ref": f"{ID}:cuts"} if p["native"] else true(0, p["p_hp"])
        return [hp_part, heal(p["p_heal"], p["p_heal_r"])]

    # ------------------------------------------------------------------ Q stacks (league_varus Blight's ladder)
    # qs1..qsk all on at k stacks, each q_keep ticks: a hit adds one (at most q_n) and runs the timers again.
    def stack_up():
        out = combine(*rm(*stacks), flag("qs1", p["q_keep"]))
        for k in range(1, q_n):
            out = sw(f"qs{k}", combine(*rm(*stacks), *[flag(f"qs{j}", p["q_keep"]) for j in range(1, k + 2)]), out)
        return sw(f"qs{q_n}", combine(*rm(*stacks), *[flag(f"qs{j}", p["q_keep"]) for j in range(1, q_n + 1)]), out)

    # ------------------------------------------------------------------ attack
    hit = homing("a_cut", 100000, 0, "Enemy",
                 [attack(0, 100), cuts(), sw("e_on", ap(p["e_dmg"], p["e_ratio"])), view("a_hit"), tsfx("a_hit")])
    hit_c = homing("a_cut_c", 100000, 0, "EnemyChampion", cuts_champ())
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      combine(sfx("a_swing"), delayed(p["a_hit"], hit, hit_c, stack_up())),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Q Snip Snip!
    cone = {"DirDot": {"radius": p["q_cone_r"], "range": p["q_cone"]}}

    def snip(dmg, ratio, final=False):
        out = [sfx("q_final" if final else "q_snip"),
               around(cone, "EnemyWithoutTower", [ap(dmg, ratio), cuts(), view("q_hit"), tsfx("q_hit")], forward=1000),
               around(cone, "EnemyChampion", cuts_champ(), forward=1000)]
        if final:
            centre = around(p["q_c_r"], "EnemyWithoutTower", [true(p["q_true"]), view("q_true"), tsfx("q_true")],
                            forward=p["q_c_off"])
            # combo E -> Q: in the window E's landing opened, the centre is put on Q's target (pros dash so it lands
            # there; the AI cannot aim it)
            on_target = combine(homing("q_mark", 100000, 0, "EnemyWithoutTower",
                                       [true(p["q_true"]), view("q_true"), tsfx("q_true")]), *rm("eq"))
            out.append(sw("eq", on_target, centre) if p["e_cut"] else centre)
        return out

    t0, gap = p["q_t0"], p["q_gap"]
    minis = [delayed(t0, *snip(p["q_mini"], p["q_mini_r"]))]
    for k in range(1, q_n + 1):
        minis.append(sw(f"qs{k}", delayed(t0 + k * gap, *snip(p["q_mini"], p["q_mini_r"]))))
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(anim("skill", p["q_dur"]), sfx("q_open"), sfx("vo_q"), *minis,
                           delayed(p["q_final"], *snip(p["q_dmg"], p["q_ratio"], final=True)),
                           delayed(1, *rm(*stacks))))

    # ------------------------------------------------------------------ skill2: E Skip 'n Slash -> W Hallowed Mist
    # The mist: Ekko's anchor laid where she lands; its end_effects start the zone (league_akali's first shroud).
    inside = pick(p["w_r"], "AllyOnlySelf",
                  {"type": "CasterInvisible", "tick": p["w_period"] + 2},
                  refresh("w_in", p["w_period"] + 2, defence=p["w_def"], magic_resistance=p["w_def"]), fp=True)
    zone = {"type": "RangePeriodProjectile", "name": n("w_zone"), "shape": circle(p["w_r"]), "tick": p["w_t"],
            "period": p["w_period"], "first_delay": 0, "applied_target": "AllyChampion",
            "applied_effects": [T(inside)], "end_effects": []}
    anchor = {"type": "LinearProjectile", "name": n("w_anchor"), "speed": 1, "range": 1, "y_offset": 5000,
              "penetrate": True, "shape": circle(1000), "applied_target": "EnemyChampion", "applied_effects": [],
              "end_effects": [zone]}
    land = [cview("w_mist"), sfx("w_cast"), sfx("vo_w"), anchor,
            refresh("e_on", p["e_t"], attack_speed_mult=p["e_as"], range=p["e_rng"])]
    if p["e_cut"]:
        # combo E -> A: League's E resets her attack - she lands snipping the target (the attack's hit with E's on-hit
        # damage, a Q stack) - and opens eq_t ticks in which Q's centre snips Q's target (E -> Q, below)
        land += [sfx("a_swing"),
                 homing("e_cut", 100000, 0, "EnemyChampion",
                        [attack(0, p["e_cut_ratio"]), cuts(),
                         *([ap(p["e_dmg"], p["e_ratio"])] if p["e_cut_bonus"] else []), view("a_hit"), tsfx("a_hit"),
                         *cuts_champ()]),
                 stack_up(), refresh("eq", p["eq_t"])]
    combo = combine(anim("skill2", p["e_tick"] + 4), sfx("e_cast"), sfx("vo_e"),
                    {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"] + 10000, "end_effects": []},
                    delayed(p["e_tick"], *land))
    skill2 = action("skill2", p["e_tick"] + 4, p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion", combo)

    # ------------------------------------------------------------------ ult: R Needlework
    def volley(k, width, dmg):
        pose = [anim("ult", p["r_anim"])] if k == 1 or not p["r_weave"] else []
        return [*pose, sfx("r_throw"),
                fan(f"r_v{k}", width, p["r_len"], p["r_delay"], p["r_apply"], "EnemyWithoutTower",
                    [ap(dmg, p["r_ratio"]), cuts(), buff("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
                     view("r_hit"), tsfx("r_hit")]),
                fan(f"r_v{k}_c", width, p["r_len"], p["r_delay"], p["r_apply"], "EnemyChampion", cuts_champ())]

    t = p["r_t0"]
    # combo R -> A -> R -> A -> R: with r_weave the cast holds her for the first throw only; the later volleys fly
    # from where she is while she attacks between them (League's recasts, woven with attacks)
    hold = t + p["r_anim"] if p["r_weave"] else t + 2 * p["r_gap"] + p["r_anim"]
    ult = action("ult", hold, p["r_cd"], 1, p["r_range"], "Direction", "EnemyChampion",
                 combine(sfx("vo_r"), sfx("r_cast"),
                         delayed(t, *volley(1, p["r_w1"], p["r_dmg1"])),
                         delayed(t + p["r_gap"], *volley(2, p["r_w2"], p["r_dmg2"])),
                         delayed(t + 2 * p["r_gap"], *volley(3, p["r_w3"], p["r_dmg3"]))),
                 key="ult")

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    P_ = lambda name, anim_=FX, z=1, rep=False: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                                 "repeat": rep, "z": z}
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_p = [P_(f"r_v{k}", BIG) for k in (1, 2, 3)]
    views_e = [E("a_hit"), E("q_hit"), E("q_true"), E("r_hit"), E("w_mist", BIG, -1, **LATE)]   # e_dash: in her frames
    views_b = [B_(f"qs{k}", FX, 3) for k in range(1, q_n + 1)] + [B_("e_on", FX, 2), B_("w_in", FX, 2),
                                                                  B_("r_slow", FX, 2)]
    return {
        "id": ID, "category": "Assassin", "tags": ["AP", "Magic", "Melee", "Heal"],
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
