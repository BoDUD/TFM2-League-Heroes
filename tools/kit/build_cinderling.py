"""Build tft_cinderling.data_champion (a tft pack hero: the Cinderling, bottom lane, Range) from the parameters P.

    python tools/kit/build_cinderling.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

The Cinderling (绯红树怪; en Cinderling) is Teamfight Tactics set 18's 1-cost Rift Monster / Hunter (DA_Cinderling18,
range 4, 500 health, 40 AD, 0.70 attack speed, 25 armour and magic resistance, 0/50 mana): Razor Leaves / 刃叶 - five
razor-sharp leaves converge on its target: physical damage, Wound and Burn; Scarlet Buff: Attack Damage each cast. The
Red camp's little sapling critter with a wooden mask. The kit is our own design from that (the user's OK, 2026-11-02:
bottom lane, the proposed kit). All data; tft.dll's `tft_cinderling:scarlet` (addons/tft/src/cinderling.rs) only plays
its death sound and logs Scarlet Buff's full stacks (--plain: no passive, for the balance sims):
  passive Scarlet Buff (绯红霸符): each cast (Q, E, R) climbs a ladder of caster flags p_1 -> p_2 -> p_3 -> p_full
          (league_talon's wound ladder: one level at a time, renewed to p_t ticks on each cast, all gone p_t after the
          last), level k p_ad x k more attack; at p_full (its view: embers on its leaf tips) its attacks also Burn.
  Burn    a Fire `AddCasted` of `FixedAttack {target_hp_ratio: p_burn}` (true damage, % of the target's maximum health)
          every p_every for p_burn_t, and the p_burn picture; only on champions (a twin homing projectile on
          `EnemyChampion` carries it: % maximum health would melt the epic monsters).
  attack  Ember Leaf (余烬叶) on `Enemy` (towers too): a homing leaf, 100% AD; at p_full the Burn twin beside it.
  skill   Razor Leaves (刃叶, TFT's), `Targeting` on `EnemyWithoutTower` (q_range: waves and camps too): five homing
          razor leaves leave q_gap ticks apart from five heights (a fan converging on the target), together q_dmg +
          q_ratio% AD physical; the middle one also Wounds (heal_reduce q_wound for q_wound_t) and Burns (champions).
  skill2  Burrow (钻土突袭), `Targeting` on `EnemyChampion` (e_range: one is close): it digs in where it stands (e_dig
          on the ground: on e_kick every enemy within e_r - the ones chasing it - takes e_dmg + e_ratio% AD and is
          e_slow% slower for e_hold), moves away from the target underground (MoveBack e_back x e_move, e_dr% less
          damage taken while under; the sprite shows only its leaf tips) and bursts out (e_pop) out of their reach.
  ult     Wildfire Leafstorm (燎原叶暴), `Targeting` on `EnemyChampion` (r_range, only in fights): it rears up, its mane
          catches fire (r_cast), and for r_t ticks it is r_as% faster attacking (r_blaze) while every r_p ticks r_n
          burning leaves fly at random enemies within r_r (r_dmg + r_ratio% AD physical each, champions Burn): an
          AddCasted on itself, so the storm ends with its life.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "tft"
ID = "tft_cinderling"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
BIG = f"asset/{MOD_ID}/effects/{ID}_big"

# Units: attack range 60000 like the pack's bottoms (tft_sentry, tft_raptor, the base archer); radii count the unit's
# collision radius (~15000) on top. Timings from the frames (tools/art/rig_cinderling.py MS): the leaf leaves on a_rel 11
# (167 ms: a_fling showing) inside the 400 ms attack (atk_dur 24); the razor leaves from q_rel 13 (200 ms: q_throw); the
# dig 12 ticks (e_dig, 200 ms), under the ground e_move 12 (the sunk frame), out at 400 ms (e_pop) of 800 (e_dur 48);
# the fire on r_rel 13 (200 ms: r_roar) of 500 (r_dur 30). Heights (a projectile starts 5000 - y_offset above the pivot,
# 1000 a game px; the pivot is 11 px over the ground): its leaf mane is about 21 px over the ground, 10 over the pivot:
# a_y -5000, the razor leaves fanned round it (Q_Y).
# Stats from the Range base (attack 100 +20, hp 900 +90, def 20 +7, mr 15 +3, move 900 +9), all physical like
# tft_raptor: a small, frail hunter. Numbers = the 10-min classic-SDK simulations (C:/t/cf_sim with C:/t/al_sim/kd.py:
# bottom lane 3 against the base archer, gunner, boomerang and poison-dart hunters, three lineups, both sides;
# 2026-11-02), all --plain: the draft (atk 96, p_ad 8, Q 100 + 130%, E's blow on the pop) +0.95 / +1.15 on seeds 1-8 /
# 9-16; E's blow moved to the dig (it hits the chasers) +1.71; Q 80 + 110%, E 30 + 35% +0.94 / +1.33 (tft_raptor's,
# a 3-cost: +0.69 / +1.47); + atk 92, p_ad 6 -0.11 / +1.22 = P: the 1-cost by tft_sentry (+0.24 / +0.47).
P = {
    # stats (Range, an AD carry)
    "hp": 820, "hp_g": 85, "atk": 92, "atk_g": 18, "apw": 0, "apw_g": 0, "def": 20, "def_g": 7, "mr": 18, "mr_g": 3,
    "ms": 920, "ms_g": 9,
    "atk_range": 60000, "atk_dur": 24, "atk_cd": 70, "a_rel": 11, "a_speed": 5500, "a_y": -5000,
    # passive Scarlet Buff (TFT: Attack Damage each cast) and the Burn
    "p_ad": 6, "p_t": 480, "p_burn": 1, "p_every": 60, "p_burn_t": 120,
    # Razor Leaves (TFT: physical, Wound, Burn)
    "q_cd": 360, "q_range": 60000, "q_dur": 24, "q_rel": 13, "q_gap": 2, "q_speed": 4500, "q_dmg": 80,
    "q_ratio": 110, "q_wound": 40, "q_wound_t": 180,
    # Burrow
    "e_cd": 600, "e_range": 35000, "e_dur": 48, "e_dig": 12, "e_kick": 6, "e_move": 12, "e_back": 2500, "e_dr": 70,
    "e_r": 30000,
    "e_dmg": 30, "e_ratio": 35, "e_slow": 35, "e_hold": 90,
    # Wildfire Leafstorm
    "r_cd": 2400, "r_range": 60000, "r_dur": 30, "r_rel": 13, "r_t": 240, "r_p": 30, "r_n": 3, "r_r": 65000,
    "r_speed": 5000, "r_dmg": 20, "r_ratio": 25, "r_as": 40,
}
Q_Y = (-9000, -7000, -5000, -3000, -1000)   # the five leaves' heights (y_offset): a fan converging on the target


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


NONE = combine()


def sw(name, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": yes, "effect_none": no or NONE}


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
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def cview(name):
    return {"type": "CasterViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def circle(r):
    return {"Circle": {"radius": r}}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def homing(name, target, effects, speed, y=0):
    return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y, "applied_target": target,
            "applied_effects": [T(e) for e in effects]}


def around(radius, target, effects):
    return {"type": "RangeEffect", "shape": circle(radius), "target": target, "apply_type": "AroundCaster",
            "effects": list(effects)}


def pick(rng, target, *effects):
    return {"type": "RandomTarget", "range": rng, "casting_target": target, "from_projectile": False,
            "effects": list(effects)}


def casted(duration, period, *effects, kind="Fire"):
    return {"type": "AddCasted", "casted_type": kind, "duration": duration, "period": period, "effects": list(effects)}


def alive(*effects):
    """Run only while it lives (a dead caster's `Delayed` effects run in the game): a 1-tick flag from a search that
    finds no dead caster, read and taken off at once (league_velkoz)."""
    return combine(pick(1, "AllyOnlySelf", flag("lives", 1)), sw("lives", combine(*effects)), *rm("lives"))


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=True):
    # ------------------------------------------------------------------ Scarlet Buff: the ladder, and the Burn
    lv = lambda k: {"attack": p["p_ad"] * k}
    climb = sw("p_full", refresh("p_full", p["p_t"], **lv(4)),
               sw("p_3", combine(*rm("p_3"), flag("p_full", p["p_t"], **lv(4)), sfx("p")),
                  sw("p_2", combine(*rm("p_2"), flag("p_3", p["p_t"], **lv(3))),
                     sw("p_1", combine(*rm("p_1"), flag("p_2", p["p_t"], **lv(2))), flag("p_1", p["p_t"], **lv(1))))))
    burn = [casted(p["p_burn_t"] + 1, p["p_every"],
                   {"type": "FixedAttack", "damage": 0, "attack_ratio": 0, "hp_ratio": 0,
                    "target_hp_ratio": p["p_burn"]}),
            buff("p_burn", p["p_burn_t"])]

    def ignite(speed, y):
        """The Burn's twin: an unseen homing projectile beside a hit that lands only on a champion."""
        return homing("ignite", "EnemyChampion", burn, speed, y)

    # ------------------------------------------------------------------ attack: Ember Leaf
    leaf = homing("a_leaf", "Enemy", [attack(0, 100), view("a_hit"), tsfx("a_hit")], p["a_speed"], p["a_y"])
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], 1, p["atk_range"], "Targeting", "Enemy",
                      delayed(p["a_rel"] - 1, sfx("a"),
                              sw("p_full", combine(leaf, tsfx("p_burn"), ignite(p["a_speed"], p["a_y"])), leaf)),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ skill: Razor Leaves
    each = [attack(round(p["q_dmg"] / len(Q_Y)), round(p["q_ratio"] / len(Q_Y)))]
    mid = len(Q_Y) // 2
    leaves = [delayed(p["q_rel"] - 1 + abs(k - mid) * p["q_gap"],
                      homing("q_leaf", "EnemyWithoutTower",
                             each + ([buff("q_wound", p["q_wound_t"], heal_reduce=p["q_wound"]), view("q_hit"),
                                      tsfx("q_hit"), tsfx("q_burn")] if k == mid else []), p["q_speed"], y),
                      ignite(p["q_speed"], y) if k == mid else None)
              for k, y in enumerate(Q_Y)]
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
                   combine(climb, sfx("q"), sfx("q_vo"), *leaves))

    # ------------------------------------------------------------------ skill2: Burrow
    popped = [attack(p["e_dmg"], p["e_ratio"]), buff("e_slow", p["e_hold"], move_speed_mult=-p["e_slow"])]
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(climb, sfx("e"), cview("e_dig"),
                            refresh("e_under", p["e_dig"] + p["e_move"] + 2, damaged_reduce=p["e_dr"]),
                            delayed(p["e_kick"] - 1, around(p["e_r"], "EnemyWithoutTower", popped)),
                            delayed(p["e_dig"] - 1, {"type": "MoveBack", "speed": p["e_back"], "tick": p["e_move"]}),
                            delayed(p["e_dig"] + p["e_move"], alive(sfx("e_out"), sfx("e_vo"), cview("e_pop")))))

    # ------------------------------------------------------------------ ult: Wildfire Leafstorm
    shot = [attack(p["r_dmg"], p["r_ratio"]), view("r_hit"), tsfx("r_hit")]
    wave = combine(*[pick(p["r_r"], "EnemyWithoutTower", homing("r_leaf", "EnemyWithoutTower", shot, p["r_speed"],
                                                                p["a_y"]),
                          ignite(p["r_speed"], p["a_y"])) for _ in range(p["r_n"])], sfx("r_shot"))
    # the waves: an AddCasted on itself (league_aphelios Q's way), so they stop when it dies
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(climb, sfx("r_vo"), cview("r_cast"),
                         delayed(p["r_rel"] - 1, sfx("r"), refresh("r_blaze", p["r_t"], attack_speed_mult=p["r_as"]),
                                 around(1000, "AllyOnlySelf", [casted(p["r_t"], p["r_p"], wave, kind="Heal")]))))

    # ------------------------------------------------------------------ views
    E = lambda name, anim_=FX, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": anim_, "tag": name,
                                                   "z": z, "is_follow": follow}
    B_ = lambda name, anim_=FX, z=2, rep=True: {"type": "Animated", "name": n(name), "anim": anim_, "tag": name,
                                                "repeat": rep, "z": z}
    # the leaves fly laid along their flight, top-bottom symmetric (turned with it); the ignite twin flies unseen; the
    # hits are ViewEffects on the struck; e_dig / e_pop stay on the ground where they happen (not following); r_cast
    # rides it; p_full and r_blaze are its own buffs (BIG), p_burn / q_wound / e_slow the struck's
    views_p = [B_("a_leaf"), B_("q_leaf"), B_("r_leaf")]
    views_e = [E("a_hit"), E("q_hit", FX, 3), E("e_dig", FX, -1, False), E("e_pop", FX, -1, False),
               E("r_cast", BIG, 3), E("r_hit", FX, 3)]
    views_b = [B_("p_full", BIG, 3), B_("p_burn", FX, 4), B_("q_wound", FX, 3), B_("e_slow", FX, 3),
               B_("r_blaze", BIG, -1)]   # behind it: in front the arc hid its body
    kit = {
        "id": ID, "category": "Range", "tags": ["AD", "Range", "Dot"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:   # tft.dll (addons/tft/src/cinderling.rs): the death sound, the full-stack log
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:scarlet", "params": {}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
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
    ap_.add_argument("--set", nargs="*", default=[], help="every key=value after ONE --set (a second --set replaces it)")
    ap_.add_argument("--params", help="json file with overrides")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="no tft.dll passive (for the balance sims)")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, not a.plain)
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
