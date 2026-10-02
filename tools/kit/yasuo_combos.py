#!/usr/bin/env python3
"""Yasuo's combos (the user, 2026-10-02: "亚索也加点连招", after Lee Sin's and Akali's).

    python tools/kit/yasuo_combos.py [--check]

E then Q (the circle, EQ / EQ3) was already in the kit. Like tools/kit/leesin_combos.py, each new combo is played by
a slot, shaped by flags the slot before it left; no slot is held:
- R -> Q: after Last Breath's slash (its tick 25) Yasuo turns into Steel Tempest's circle (EQ's pose, its 25000
  cut) on the enemies he holds up.
- Q3 -> E -> Q: Q3's whirlwind knocking up an enemy champion opens a 2.5 s window (q3_up, from a champion-only twin
  of the whirlwind); E dashed in it cuts the circle on the way, 8 ticks in - the circle a Q cast during the dash
  would give, without a Q (Q3 has just been spent).
Neither circle spends Q, so both are lighter than Q's: 15 + 50% AD and no Gathering Storm stack. At Q's full
30 + 100% with the stack, Yasuo's kill difference in mid against base mages went from +2.30 to +3.16 (720 simulated
games; +2.79 without the stack), his damage up about 5%.
The kit file was hand-built; the script refuses to run twice (q3_up marks a combo kit). --check only verifies.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_yasuo.data_champion")
P = "league_yasuo_"
AFTER_R = 28                 # R's effects start on its tick 1, the slash lands on 25: the circle starts on 29
WINDOW = 150                 # q3_up: E this soon after Q3 knocked up a champion (the AI's next E came 85-131
                             # ticks later in a simulation, so the knock-up's 60 caught none)
DASH_CUT = 8                 # ticks after E's effects (its tick 2) before the circle
LIGHT = (15, 50)             # the combos' circle: half of Q's 30 + 100% AD


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
    q, e, r = k["skill"], k["skill2"], k["ult"]
    # ---- the circle: EQ's branch without Q3 (its first effect closes E's window, the rest is the cut)
    eq = find(q["effect"], lambda o: o.get("type") == "SwitchByBuff" and o.get("buff_name") == n("e_window"))
    plain = eq["effect_buff"]["effect_none"]["effects"]
    assert plain[0] == unflag("e_window") and [x["type"] for x in plain[1:]] == ["CasterAnimation", "Sfx", "Delayed"]
    circle = json.loads(json.dumps(plain[1:]))       # a copy, made lighter: half the hit, no stack
    cut = circle[2]["effects"][1]
    assert cut["type"] == "RangeEffect"
    hit = cut["effects"][0]
    assert hit["type"] == "Attack" and (hit["damage"], hit["attack_ratio"]) == (30, 100)
    hit["damage"], hit["attack_ratio"] = LIGHT
    assert cut["effects"][-1].get("buff_name") == n("q_lock")
    cut["effects"] = cut["effects"][:-1]
    # ---- Q3's whirlwind and the Delayed that throws it
    throw = find(q["effect"], lambda o: o.get("type") == "Delayed" and any(
        x.get("name") == n("q3_tornado") for x in o.get("effects", [])))
    wind = throw["effects"][0]
    assert wind["type"] == "LinearProjectile" and wind["applied_target"] == "EnemyWithoutTower"

    # ---- Q3 on a champion: the window (a champion-only twin on the whirlwind's path, no picture)
    throw["effects"].append({"type": "LinearProjectile", "name": n("q3_twin"), "speed": wind["speed"],
                             "range": wind["range"], "shape": wind["shape"], "penetrate": True,
                             "y_offset": wind["y_offset"], "applied_target": "EnemyChampion",
                             "applied_effects": [{"casting_type": "Targeting", "effect": flag("q3_up", WINDOW)}],
                             "end_effects": []})
    # ---- E in the window: the circle on the way
    e["effect"]["effects"].append(sw("q3_up", combine(unflag("q3_up"), delayed(DASH_CUT, *circle))))
    # ---- R: the circle after the slash
    r["effect"]["effects"].append(delayed(AFTER_R, *circle))
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
        print("league_yasuo.data_champion:", "combos in" if ok else "NO combos")
        sys.exit(0 if ok else 1)
    if has_combos(k):
        sys.exit("league_yasuo.data_champion already has the combos")
    out = json.dumps(build(k), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_yasuo.data_champion with R -> Q and Q3 -> E -> Q")


if __name__ == "__main__":
    main()
