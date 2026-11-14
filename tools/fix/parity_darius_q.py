"""league_darius Q Decimate: the blade and the handle (League: "Enemies within the inner radius take 35% damage" and "do
not gain a Hemorrhage stack"; he heals by the "number of targets hit by the outer radius", at most three).

    python tools/fix/parity_darius_q.py [<worktree>] [--out file] [--handle 10000] [--heal 25 --heal-ad 30]

The kit is hand-written JSON. Until now everything within 32000 took the whole swing, bled, and every champion healed
him. In the swing (skill's Delayed 26):
  * each unit the swing's circle finds (`EnemyWithoutTower`, 32000 as before) is no longer struck by the area itself:
    the area throws a hidden homing bolt at it (`league_darius_q_edge`, EDGE_SPEED a tick: there on the next tick),
    and the bolt's hit asks where he stands - `RandomTarget {from_projectile, AllyOnlySelf, range HANDLE}` finds him
    only within HANDLE of the unit struck (both bodies add about 20000, as for the circle; measured, tmp/darius_probe2)
    and raises `league_darius_q_haft` for that one hit: up -> the handle, SHARE% of the damage and nothing else; not
    up -> the blade, what the swing did before (the damage, the hit sound, the bleed and its picture);
  * each champion gets a second bolt (`league_darius_q_edge_c`, its own flag `q_haft_c`) for what only champions give:
    on the blade the heal (at most CAP a swing: `q_b1` -> `q_b2` -> `q_b3` on him, taken off as the swing starts) and
    the count toward Noxian Might (the tree that was there, unchanged); on the handle nothing.
HANDLE 10000: with the bodies a centre distance of about 30000 of the swing's 52000 - League's 305 of 525 (inner
radius 240 and outer 460, each plus the target's 65).
  * --pen N: Apprehend's passive, "Armor Penetration: 20 / 25 / 30 / 35 / 40%" - a Permanent caster buff
    `league_darius_e_pen` (defence_penetration N) that Q and E each put on him when it is not there (death clears
    a mod's buffs: back with the next cast). Not in the attack (its tree stays as it is) nor in the ult (league_sylas
    steals that tree: he would keep the penetration).
Run again it changes nothing.
"""
import argparse
import copy
import os
import sys
from collections import OrderedDict as OD

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import parity_jsonio as jsonio  # noqa: E402

ID = "league_darius"
EDGE_SPEED = 60000
SHARE = 35
CAP = 3


def n(x):
    return f"{ID}_{x}"


def combine(*effects):
    return OD([("type", "Combine"), ("effects", list(effects))])


def sw(name, yes, no=None):
    return OD([("type", "SwitchByBuff"), ("buff_name", n(name)), ("effect_buff", yes), ("effect_none", no or combine())])


def flag(name, tick):
    return OD([("type", "AddCasterBuff"),
               ("buff_state", OD([("name", n(name)), ("duration", OD([("Time", OD([("tick", tick)]))]))])),
               ("only_to_enemy", False)])


def rm(name):
    return OD([("type", "RemoveCasterBuff"), ("name", n(name))])


def bolt(name, target, handle_r, mark, on_handle, on_blade):
    near = OD([("type", "RandomTarget"), ("range", handle_r), ("casting_target", "AllyOnlySelf"), ("from_projectile", True),
               ("effects", [flag(mark, 1)])])
    return OD([("type", "TargetProjectile"), ("name", n(name)), ("speed", EDGE_SPEED), ("y_offset", 0),
               ("applied_target", target),
               ("applied_effects", [OD([("casting_type", "Targeting"),
                                        ("effect", combine(near, sw(mark, combine(rm(mark), *on_handle), combine(*on_blade))))])])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree", nargs="?", default=ROOT)
    ap.add_argument("--out")
    ap.add_argument("--handle", type=int, default=10000)
    ap.add_argument("--heal", type=int)
    ap.add_argument("--heal-ad", type=int)
    ap.add_argument("--dmg", type=int)
    ap.add_argument("--dmg-ad", type=int)
    ap.add_argument("--pen", type=int, default=0)
    a = ap.parse_args()
    path = f"{a.worktree}/league/champion/{ID}.data_champion"
    kit, meta = jsonio.load(path)
    swing = kit["skill"]["effect"]["effects"][1]
    assert swing["type"] == "Delayed" and swing["tick"] == 26
    if "q_edge" in str(swing):
        print("already done")
        return
    kinds = [(e["type"], e.get("target")) for e in swing["effects"]]
    assert kinds == [("Sfx", None), ("CasterViewEffect", None), ("RangeEffect", "EnemyWithoutTower"),
                     ("RangeEffect", "EnemyChampion")], kinds
    hit, champ = swing["effects"][2], swing["effects"][3]
    blade = hit["effects"]
    assert [e["type"] for e in blade] == ["Attack", "TargetSfx", "AddCasted", "ViewEffect"]
    full = blade[0]
    if a.dmg is not None:
        full["damage"] = a.dmg
    if a.dmg_ad is not None:
        full["attack_ratio"] = a.dmg_ad
    haft = OD([("type", "Attack"), ("damage", round(full["damage"] * SHARE / 100)),
               ("attack_ratio", round(full["attack_ratio"] * SHARE / 100))])
    hit["effects"] = [bolt("q_edge", "EnemyWithoutTower", a.handle, "q_haft", [haft, copy.deepcopy(blade[1])], blade)]
    heal, heal_view, count = champ["effects"]
    assert heal["type"] == "Heal" and heal_view["type"] == "CasterViewEffect" and count["type"] == "SwitchByBuff"
    if a.heal is not None:
        heal["amount"] = a.heal
    if a.heal_ad is not None:
        heal["attack_ratio"] = a.heal_ad
    ks = [f"q_b{i}" for i in range(1, CAP + 1)]
    climb = flag(ks[0], 4)
    for prev, nxt in zip(ks, ks[1:]):
        climb = sw(prev, flag(nxt, 4), climb)
    champ["effects"] = [bolt("q_edge_c", "EnemyChampion", a.handle, "q_haft_c", [],
                             [sw(ks[-1], combine(), combine(climb, heal, heal_view)), count])]
    swing["effects"] = swing["effects"][:2] + [rm(k) for k in ks] + [hit, champ]
    if a.pen:
        for slot in ("skill", "skill2"):    # not the ult: league_sylas steals it
            top = kit[slot]["effect"]
            assert top["type"] == "Combine" and "e_pen" not in str(top)
            top["effects"].append(sw("e_pen", combine(), OD([
                ("type", "AddCasterBuff"),
                ("buff_state", OD([("name", n("e_pen")), ("duration", "Permanent"), ("defence_penetration", a.pen)])),
                ("only_to_enemy", False)])))
    jsonio.save(a.out or path, kit, meta)
    print(f"written {a.out or path}: blade {full['damage']} + {full['attack_ratio']}% AD, handle {haft['damage']} + "
          f"{haft['attack_ratio']}% AD within {a.handle}, heal {heal['amount']} + {heal['attack_ratio']}% AD x up to {CAP}"
          f", armour penetration {a.pen}%")


if __name__ == "__main__":
    main()
