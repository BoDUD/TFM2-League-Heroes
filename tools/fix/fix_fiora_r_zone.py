#!/usr/bin/env python3
"""league_fiora R: the Victory Zone lands on the challenged champion, not on whoever took the fourth Vital.

    python tools/fix/fix_fiora_r_zone.py [--check]

Players reported the zone appearing under another hero's feet. Nothing in the data tells which unit a hit is on
(league_vayne's Silver Bolts), so R's four Vitals are rung flags on Fiora (r_v4..r_v1) that any champion hit during R
takes - in 6 simulated games 16 of her 42 R Vital strikes were on a champion other than the challenged one - and the
fourth strike lobbed the zone (`league_fiora_r_lob`, a 1-tick ParabolicProjectile) onto the unit it struck.

Now (league_tristana E's charge): where R starts on its target - the ult slot's RandomTarget and the armed attack's
champion twin - an `AddCasted` poll rides on the challenged champion for R's 480 ticks (period 2, `Bleed`: the
duel's bleeding icon) and, when it finds the caster flag `r_won`, removes it and lobs the zone from there: a projectile
from an AddCasted flies from the caster to its carrier, so the zone lands under the challenged champion wherever the
fourth Vital was struck. The fourth Vital (5 places: the attack, Q's two dash strikes, W's two lines) sets `r_won` for 4
ticks instead of lobbing. The death watch (the target died after a Vital: the zone on Fiora's own spot) is unchanged.
Idempotent: --check reports whether the file is already patched.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_fiora.data_champion")
N = "league_fiora_"


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": N + name, "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in list(o.values()):
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    raw = open(PATH, "rb").read().decode("utf-8-sig")
    d = json.loads(raw)
    if N + "r_won" in raw:
        print("already patched")
        return
    if a.check:
        sys.exit("not patched")

    lob = None
    vital = []          # Delayed 1 { r_lob } under the r_v1 rung: the fourth Vital

    def find(o):
        nonlocal lob
        if o.get("type") == "SwitchByBuff" and o.get("buff_name") == N + "r_v1":
            for branch in (o.get("effect_buff"), o.get("effect_none")):
                def inner(x):
                    nonlocal lob
                    if x.get("type") == "Delayed" and any(isinstance(e, dict) and e.get("name") == N + "r_lob"
                                                          for e in x.get("effects", [])):
                        vital.append(x)
                        if lob is None:    # the fourth Vital's lob: the zone and its picture (a ViewEffect there)
                            lob = copy.deepcopy(next(e for e in x["effects"] if e.get("name") == N + "r_lob"))
                walk(branch, inner)

    for slot in ("attack", "skill", "skill2", "ult"):
        walk(d[slot]["effect"], find)
    assert any(e.get("type") == "ViewEffect" for e in lob["end_effects"]), "the zone's picture"
    vital = list({id(x): x for x in vital}.values())
    assert len(vital) == 5, len(vital)
    for x in vital:
        x["effects"] = [e for e in x["effects"] if e.get("name") != N + "r_lob"] + [flag("r_won", 4)]

    # where R starts: a Combine that adds r_on for 480 ticks (on the challenged champion)
    starts = []

    def start(o):
        if o.get("type") == "Combine" and any(
                e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == N + "r_on"
                and e["buff_state"]["duration"] == {"Time": {"tick": 480}} for e in o.get("effects", [])):
            starts.append(o)

    for slot in ("attack", "ult"):
        walk(d[slot]["effect"], start)
    starts = list({id(x): x for x in starts}.values())
    assert len(starts) == 2, len(starts)
    poll = {"type": "AddCasted", "casted_type": "Bleed", "duration": 481, "period": 2, "effects": [
        {"type": "SwitchByBuff", "buff_name": N + "r_won",
         "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": N + "r_won"}, lob]},
         "effect_none": {"type": "Combine", "effects": []}}]}
    for o in starts:
        o["effects"] = [{"type": "RemoveCasterBuff", "name": N + "r_won"}] + o["effects"] + [copy.deepcopy(poll)]

    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"patched: {len(vital)} fourth-Vital lobs -> r_won, {len(starts)} R starts carry the zone poll")


if __name__ == "__main__":
    main()
