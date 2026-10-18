"""Build league_wukong.data_champion (jungle, Melee) from the parameters P.

    python tools/kit/build_wukong.py [--set key=value ...] [--out file] [--params json] [--nodes]

Kit (the user's pick, 2026-10-18: layout A with the add-on league_wukong - 「技能方案按 A 做（带扩展包 league_wukong）」):
  passive Stone Skin (金刚不坏): his base armour carries League's innate part; every hit on an enemy champion (the
          attack's champion-only twin, each spin pulse) adds a stack, five at most (league_jax's Relentless ladder:
          s_1..s_5, each p_def armour + p_regen health a second, the top one p_t ticks and every lower one p_drop more,
          so they fall off one a second like League's). League's regeneration is a share of max health: the main pack
          gives p_regen a stack, the add-on adds the share (Heal has no max-health field).
  attack  A staff swing (100% AD). Q Crushing Blow folded in on its own cooldown (league_jax's Empower): with no `q_cd`
          the attack is the crushing blow - q_dmg + (100 + q_ratio)% AD and the target's armour -q_shred% for
          q_shred_t, then `q_cd` for q_t (League's 8-6 s with its 0.5 s off per hit is about 4 s in a fight). League's
          extra reach: once `q_cd2` (q_t - q_pre) is gone a plain attack adds the `q_rng` range buff (q_range, the
          Akali way; replaced, never stacked), which the blow spends - the AI starts the blow from farther away.
          While R is armed (or its second cast is open) the attack first counts the enemy champions round him and
          may become the spin instead (below).
  skill   E Nimbus Strike: a `Targeting` cast on `EnemyWithoutTower` (e_range): `MoveToTarget` onto the target; on
          arrival the cloud clones strike up to three enemies within e_rad (champions first, the entity-id order; the
          target is one of them when it is in), e_dmg + e_ratio% AD each (League's magic 100% AP: he has no AP here),
          and he gains e_as% attack speed for e_as_t. Landing on a champion leaves `e_in` (R's single-champion check).
  skill2  W Warrior Trickster: a `Targeting` cast on `EnemyChampion` (w_range, only in a fight): `CasterInvisible` w_inv,
          an anchor at his feet (league_ekko R's range-1 projectile) and a dash through the target to its back
          (`RushMoveToBack`). The clone stands at the anchor for w_t ticks (League's clone does not walk): its
          pictures play in w_slot-tick slots there, and a zone (w_rad, period w_period) strikes one enemy a period
          (champions first) for w_ratio% AD. While R spins (`r_on`) the clone spins too: each slot is a spin pulse
          round it (r_dmg/r_ratio/r_hp at w_spin%), the first one knocking up (`r_ck`).
  ult     R Cyclone: the slot only arms it (league_kayle R: the AI casts an `EnemyChampion` ult on the approach) - a
          3-tick action adds `r_armed` (r_arm ticks; unused, a 3-tick ult_cooldown_mult refunds it). While armed every
          attack counts the enemy champions within r_rad: two or more, or one in crowd control, or one right after E
          landed on a champion or with the clone out -> the spin. The spin: `CasterAnimation spin` for r_t, a pulse every
          r_every ticks (league_garen E: each pulse damages everyone within r_rad, r_dmg + r_ratio% AD + r_hp% of a
          champion's max health, and moves him at r_speed toward a champion / the units round him / the next group);
          the first pulse knocks up r_up ticks. The first spin opens `r_two` (r_two_t from the cast, after r_gap): the
          next attack with an enemy champion within r_rad spins again (League's second cast within 8 s).
Timings from the strips (tools/art/rig_wukong.py MS): the attack's and the crushing blow's hits on their frame 3 (170 ms,
8 ticks after the 2-tick decision), E 300 ms (4 frames), W 200 ms, the spin a 240 ms loop held r_t.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "league", "champion", "league_wukong.data_champion")
ID = "league_wukong"
FX = "asset/league/effects/league_wukong_fx"
BIG = "asset/league/effects/league_wukong_big"

# Numbers = the 10-min classic-SDK simulations (jungle against demon, circus_blade, hunter, inquisitor and ninja, three
# lineups, both sides, 8 seeds a batch, 2026-10-18, placeholder timings): the draft (attack 84, Q 40%, E 60%, R 1% max
# health a pulse) +0.07; R 2% alone -0.16, attack 90 / Q 60% / E 80% alone +0.45, both +1.94 / +1.92; attack 88, Q 50%,
# E 70%, R 2% +1.12 / +1.15 (league_xinzhao +1.10 / +1.29, league_kayn +1.12 / +1.72).
P = {
    # stats (Melee base: attack 95 +19, hp 1000 +100, defence 30 +8, mr 25 +4, move 1000 +11); League's Wukong:
    # 66 AD +3.5, 610 +99 hp, 31 +4.7 armour (+6-10 innate from Stone Skin), 28 mr, 340 move, attack speed 0.69 +3%
    "hp": 960, "hp_g": 100, "atk": 88, "atk_g": 18, "def": 36, "def_g": 9, "mr": 25, "mr_g": 4, "ms": 1000, "ms_g": 11,
    "regen": 2, "regen_g": 1,
    # attack
    "atk_range": 26000, "atk_dur": 26, "atk_cd": 60, "a_hit": 8,
    # passive Stone Skin (League: +6-10 armour and +0.35% max hp / 5 s a stack, 5 stacks, 5 s, one a second off)
    "p_def": 4, "p_regen": 2, "p_t": 300, "p_drop": 60,
    # Q Crushing Blow (League: +20-120 +50% bonus AD, armour -10-30% 3 s, +135-175 range, cd 8-6 s, -0.5 s a hit)
    "q_t": 240, "q_pre": 60, "q_dmg": 30, "q_ratio": 50, "q_shred": 20, "q_shred_t": 180, "q_range": 12000,
    "q_hit": 8, "q_anim": 26,
    # skill: E Nimbus Strike (League: 650 range, 80-240 +100% AP to the target and two more within 187.5, +40-60% AS
    # 5 s, cd 10-7 s)
    "e_cd": 480, "e_range": 50000, "e_dur": 18, "e_anim": 18, "e_speed": 3500, "e_rad": 22000, "e_n": 3,
    "e_dmg": 40, "e_ratio": 70, "e_as": 40, "e_as_t": 300, "e_in_t": 120,
    # skill2: W Warrior Trickster (League: invisible 1 s, dash 300, clone 4 s at 40-60% damage, range 275, cd 22-18 s)
    "w_cd": 1200, "w_range": 30000, "w_dur": 12, "w_inv": 60, "w_dash": 6000, "w_t": 240, "w_slot": 20,
    "w_rad": 30000, "w_period": 60, "w_ratio": 50, "w_spin": 50,
    # ult: R Cyclone (League: r 315, 2 s, +20% ms, 8-16% max hp +275% AD a cast (ticks every 0.25 s), knock-up 0.6 s
    # once, second cast within 8 s after 1 s, cd 130-90 s)
    "r_cd": 3600, "r_range": 60000, "r_arm": 900, "r_rad": 28000, "r_t": 120, "r_every": 15, "r_speed": 1200,
    "r_dmg": 10, "r_ratio": 35, "r_hp": 2, "r_up": 36, "r_gap": 180, "r_two_t": 480,
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


def attack(dmg, ratio, hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": hp,
            "attack_effect_type": "Target"}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def on_me(*effects):
    """Effects on him alone (a `WithSelf` would also hit the action's target, champion-data section 4)."""
    return around(1000, "AllyOnlySelf", effects)


def pick(rng, target, *effects, fp=False):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": fp,
            "effects": list(effects)}


def homing(name, speed, target, effects):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": 0, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def burst(name, radius, target, effects):
    """A one-tick circle where it is started (a point's `Delayed` keeps the point)."""
    return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
            "applied_target": target, "applied_effects": [T(e) for e in effects]}


def field(name, radius, tick, period, effects, target="EnemyWithoutTower", first=None):
    return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius), "tick": tick, "period": period,
            "first_delay": period if first is None else first, "applied_target": target,
            "applied_effects": [T(e) for e in effects], "end_effects": []}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False, key=None):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{key or name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, native=False):
    """native: the add-on's copy (addons/league_wukong) - Stone Skin's regeneration as a share of his max health."""
    # ------------------------------------------------------------------ passive: Stone Skin stacks
    def stacks():
        """One more stack (at most five), all refreshed: the top one p_t, every lower one p_drop more."""
        def to(k):
            return combine(*rm(*[f"s_{i}" for i in range(1, 6)]),
                           *[flag(f"s_{i}", p["p_t"] + p["p_drop"] * (k - i), defence=p["p_def"],
                                  hp_regen=0 if native else p["p_regen"]) for i in range(1, k + 1)])
        node = to(1)
        for k in range(2, 6):
            node = sw(f"s_{k - 1}", to(k), node)
        return sw("s_5", to(5), node)

    stone = on_me(stacks())
    twin = homing("a_twin", 1000000, "EnemyChampion", [stone])

    # ------------------------------------------------------------------ R Cyclone: the spin (one copy, in the attack)
    def rings(end):
        """league_garen E: a champion he is on, else the units round him, else the next group - one dash a pulse."""
        spec = [(25000, "EnemyChampion"), (30000, "EnemyWithoutTower"), (45000, "EnemyWithoutTower")]
        node = None
        for i in range(len(spec) - 1, -1, -1):
            rng, target = spec[i]
            dash = {"type": "MoveToTarget", "speed": p["r_speed"], "range": rng, "end_effects": list(end)}
            r = pick(rng, target, *([] if node is None else [flag("r_found", 1)]), dash)
            node = r if node is None else combine(r, sw("r_found", NONE, node))
        return node

    pulses = []
    for k, t in enumerate(range(1, p["r_t"], p["r_every"])):
        hit = [attack(p["r_dmg"], p["r_ratio"]), view("r_hit")]
        if k == 0:
            hit.append({"type": "Airborne", "duration": p["r_up"]})
        pulses.append(delayed(t, around(p["r_rad"], "EnemyWithoutTower", hit),
                              around(p["r_rad"], "EnemyChampion", [attack(0, 0, p["r_hp"])] + ([stone] if k % 2 == 0 else [])),
                              sfx("r_whoosh"), rings([anim("spin", p["r_t"] - t)])))
    spin = combine(
        sw("r_two", combine(*rm("r_two")), combine(*rm("r_armed"), flag("r_two", p["r_two_t"]))),
        *rm("r_on", "r_gap", "r_ck"), flag("r_on", p["r_t"]), flag("r_gap", p["r_gap"]),
        anim("spin", p["r_t"]), sfx("r_cast"), *pulses)

    # ------------------------------------------------------------------ attack: swing / Crushing Blow / the spin
    swing = combine(sfx("a_swing"), delayed(p["a_hit"], attack(0, 100), view("a_hit"), tsfx("a_hit"), twin))
    plain = sw("q_cd2", swing, combine(*rm("q_rng"), flag("q_rng", 1200, range=p["q_range"]), swing))
    blow = combine(*rm("q_rng"), flag("q_cd", p["q_t"]), flag("q_cd2", p["q_t"] - p["q_pre"]),
                   anim("q_attack", p["q_anim"]), sfx("q_swing"),
                   delayed(p["q_hit"], attack(p["q_dmg"], 100 + p["q_ratio"]),
                           buff("q_shred", p["q_shred_t"], defence_mult=-p["q_shred"]),
                           view("q_hit"), tsfx("q_hit"), twin))
    normal = sw("q_cd", plain, blow)
    count = [around(p["r_rad"], "EnemyChampion", [sw("c_1", flag("c_2", 3), flag("c_1", 3))]),
             pick(p["r_rad"], "EnemyChampionInCC", flag("c_cc", 3))]
    go = flag("r_go", 3)
    first = sw("c_2", go, sw("c_cc", go, sw("c_1", sw("e_in", go, sw("w_live", go)))))
    second = sw("r_gap", NONE, sw("c_1", go))
    decide = sw("r_two", second, sw("r_armed", first))
    # the count runs only while R is armed or its second cast open; every attack decides two ticks in (a_hit / q_hit
    # count from there)
    counted = combine(*count, delayed(1, decide))
    root = combine(sw("r_armed", counted, sw("r_two", counted)),
                   delayed(2, sw("r_go", combine(*rm("r_go"), spin), normal)))
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy", root,
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: E Nimbus Strike
    hits = around(p["e_rad"], "EnemyWithoutTower", [
        sw("e_3", NONE, combine(sw("e_2", flag("e_3", 2), sw("e_1", flag("e_2", 2), flag("e_1", 2))),
                                attack(p["e_dmg"], p["e_ratio"]), view("e_hit"), tsfx("e_hit")))])
    land = [*rm("e_1", "e_2", "e_3"), hits, cview("e_land"), sfx("e_hit"),
            around(p["e_rad"], "EnemyChampion", [on_me(flag("e_in", p["e_in_t"]))]),
            *rm("e_as"), flag("e_as", p["e_as_t"], attack_speed_mult=p["e_as"])]
    charge = {"type": "MoveToTarget", "speed": p["e_speed"], "range": p["e_range"], "end_effects": land}
    skill = action("skill", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyWithoutTower",
                   combine(anim("skill", p["e_anim"]), cview("e_cloud"), sfx("e_cast"), charge))

    # ------------------------------------------------------------------ skill2: W Warrior Trickster (the clone)
    nslot = p["w_t"] // p["w_slot"]
    spin_c = [attack(p["r_dmg"] * p["w_spin"] // 100, p["r_ratio"] * p["w_spin"] // 100), view("r_hit")]
    slots = []
    for k in range(nslot):
        idle_pic = view("w_clone_atk" if k % (p["w_period"] // p["w_slot"]) == 0 else "w_clone")
        spin_slot = combine(view("w_clone_spin"),
                            sw("r_ck", burst("w_spin", p["r_rad"], "EnemyWithoutTower", spin_c),
                               combine(flag("r_ck", p["r_t"]),
                                       burst("w_spin_up", p["r_rad"], "EnemyWithoutTower",
                                             spin_c + [{"type": "Airborne", "duration": p["r_up"]}]))))
        slots.append(delayed(k * p["w_slot"] + 1, sw("w_live", sw("r_on", spin_slot, idle_pic))))
    strike = field("w_zone", p["w_rad"], p["w_t"], p["w_period"],
                   [sw("w_one", NONE, combine(flag("w_one", 2), attack(0, p["w_ratio"]), view("w_hit"),
                                             tsfx("w_hit")))], first=1)
    anchor = {"type": "LinearProjectile", "name": n("w_anchor"), "speed": 1, "range": 1, "y_offset": 5000,
              "penetrate": True, "shape": circle(1000), "applied_target": "EnemyChampion", "applied_effects": [],
              "end_effects": [strike, *slots]}
    skill2 = action("skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
                    combine(*rm("w_live"), flag("w_live", p["w_t"]), {"type": "CasterInvisible", "tick": p["w_inv"]},
                            cview("w_poof"), sfx("w_cast"), anchor,
                            delayed(1, {"type": "RushMoveToBack", "speed": p["w_dash"], "applied_effects": []})))

    # ------------------------------------------------------------------ ult: arm R Cyclone
    ult = action("ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(*rm("r_armed", "r_two"), flag("r_armed", p["r_arm"]), sfx("r_arm"),
                         delayed(p["r_arm"] - 1, sw("r_armed", flag("r_refund", 3, ult_cooldown_mult=4900)))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    LATE = dict(follow=False)
    B_ = lambda name, anim_=FX, z=2: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name, "repeat": True,
                                      "z": z}
    views_e = [E("a_hit"), E("q_hit"), E("e_cloud", BIG), E("e_land", BIG, -1, **LATE), E("e_hit"),
               E("w_poof", BIG, 2, **LATE), E("w_clone", BIG, 1), E("w_clone_atk", BIG, 1), E("w_clone_spin", BIG, 1),
               E("w_hit"), E("r_hit")]
    views_b = [B_("q_shred", FX, 3), B_("r_on", BIG, -1),
               # Stone Skin at five stacks: the stone chips round him (the top stack's buff carries the picture)
               {"type": "Animated", "name": n("s_5"), "anim": FX, "tag": "p_stone", "repeat": True, "z": 2}]
    kit = {
        "id": ID, "category": "Melee", "tags": ["AD", "Melee", "CC"],
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
        kit["passive"] = {"passive_ref": "league_wukong:stone", "params": {}}
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
