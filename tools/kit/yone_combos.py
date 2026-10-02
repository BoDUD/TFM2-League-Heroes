#!/usr/bin/env python3
"""Yone's combos (the user, 2026-10-02: "永恩也是", after Yasuo's).

    python tools/kit/yone_combos.py [--check]

Like tools/kit/leesin_combos.py, each combo is played by a slot, shaped by flags the slot before it left; no slot is
held. Yone's Q and W trees are the pack's largest and the game copies skill and skill2 whole every tick, so the
combos sit in R; Q only gains a twin of Q3's wave:
- Q3 -> R: Q3's wave knocking up an enemy champion opens a window (q3_up, from a champion-only twin of the wave).
  R cast in it skips the 15-tick wind-up: Q3's dash pose (q3) and the slash 7 ticks in, while they are still in the
  air - the same line, damage, knock-up and dash behind the target as the slow R.
- R -> Q: every enemy champion the slash hits gives Gathering Storm a stack (a champion-only twin of the hit line,
  Q's own stacking, once per cast), so the Q after an R is Q3 more often: the wind round his waist shows it.
The kit file was hand-built; the script refuses to run twice (q3_up marks a combo kit). --check only verifies.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_yone.data_champion")
P = "league_yone_"
AIR = 90                     # q3_up: Q3's knock-up (60) and half a second (the AI cast R 34-75 ticks after it)
FAST = 7                     # the quick R's slash: Q3's dash frame (the slow R waits 15)


def n(x):
    return P + x


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or combine()}


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None


def build(k):
    q, r = k["skill"], k["ult"]
    # ---- what the combos borrow
    thrust = find(q["effect"], lambda o: o.get("name") == n("q_thrust"))
    stack = thrust["applied_effects"][3]["effect"]
    assert stack["type"] == "SwitchByBuff" and stack["buff_name"] == n("q_lock")
    throw = find(q["effect"], lambda o: o.get("type") == "Delayed" and any(
        x.get("name") == n("q3_wave") for x in o.get("effects", [])))
    wave = throw["effects"][0]
    assert wave["type"] == "LinearProjectile" and wave["applied_target"] == "EnemyWithoutTower"
    effs = r["effect"]["effects"]
    assert [x["type"] for x in effs] == ["Sfx", "LineRangeProjectile", "Delayed"] and effs[2]["tick"] == 15
    slash = effs[2]["effects"]
    assert [x["type"] for x in slash] == ["LineRangeProjectile", "SwitchByBuff", "Sfx", "RushMoveToBack"]
    hit = slash[0]

    # ---- Q3 on a champion: the window (a champion-only twin on the wave's path, no picture)
    throw["effects"].append({"type": "LinearProjectile", "name": n("q3_mark"), "speed": wave["speed"],
                             "range": wave["range"], "shape": wave["shape"], "penetrate": True,
                             "y_offset": wave["y_offset"], "applied_target": "EnemyChampion",
                             "applied_effects": [{"casting_type": "Targeting", "effect": flag("q3_up", AIR)}],
                             "end_effects": []})
    # ---- R: a stack for the champions the slash hits; in the window the quick R
    slash.insert(1, {"type": "LineRangeProjectile", "name": n("r_mark"), "width": hit["width"], "length": hit["length"],
                     "delay": hit["delay"], "apply": hit["apply"], "applied_target": "EnemyChampion",
                     "applied_effects": [{"casting_type": "Targeting", "effect": stack}]})
    quick = combine(unflag("q3_up"), {"type": "CasterAnimation", "name": "q3", "tick": 30}, effs[0], effs[1],
                    delayed(FAST, *slash))
    r["effect"] = sw("q3_up", quick, r["effect"])
    return k


def has_combos(k):
    return n("q3_up") in json.dumps(k)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    k = json.loads(raw)
    if args.check:
        ok = has_combos(k)
        print("league_yone.data_champion:", "combos in" if ok else "NO combos")
        sys.exit(0 if ok else 1)
    if has_combos(k):
        sys.exit("league_yone.data_champion already has the combos")
    out = json.dumps(build(k), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_yone.data_champion with Q3 -> R and R -> Q")


if __name__ == "__main__":
    main()
