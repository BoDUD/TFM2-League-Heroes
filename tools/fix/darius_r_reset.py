#!/usr/bin/env python3
"""Darius's Noxian Guillotine resets on a kill (League: it can be cast again after it kills a champion).

    python tools/fix/darius_r_reset.py [--check]

Pure data, so it works without any add-on: league_pyke's R reset (the skill's "Kill trigger", champion-data section 7).
At the blow (the ult's Delayed 22, on the target) Darius gets a flag `league_darius_r_kill`; a tick later a Delayed on
the target adds an AddCasted that clears the flag - on a living target it runs, on a dead one nothing but pictures runs
from a Delayed, so the flag stays; 4 ticks after the blow a check queued on Darius himself (RangeEffect AllyOnlySelf)
reads the flag and, when it is still there, caps the ult's cooldown (a 2-tick ult_cooldown_mult 10000: the ult is ready
about half a second later), plays his Noxian Might glow and its voice. Idempotent: run it again and nothing changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_darius.data_champion")
FLAG, RESET = "league_darius_r_kill", "league_darius_r_reset"
HOLD, READ = 40, 4
NONE = {"type": "Combine", "effects": []}


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": tick}}, **fields},
            "only_to_enemy": False}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def kill_check():
    reset = {"type": "Combine", "effects": [rm(FLAG), rm(RESET), flag(RESET, 2, ult_cooldown_mult=10000),
                                            {"type": "CasterViewEffect", "name": "league_darius_might"},
                                            {"type": "Sfx", "name": "league_darius_might_vo"}]}
    return [
        {"type": "Delayed", "tick": 1, "effects": [
            {"type": "AddCasted", "casted_type": "Heal", "duration": 3, "period": 1, "effects": [rm(FLAG)]}]},
        {"type": "RangeEffect", "shape": {"Circle": {"radius": 1000}}, "target": "AllyOnlySelf",
         "apply_type": "AroundCaster", "effects": [
             {"type": "Delayed", "tick": READ, "effects": [
                 {"type": "SwitchByBuff", "buff_name": FLAG, "effect_buff": reset, "effect_none": NONE}]}]},
    ]


def patched(ult):
    eff = ult["effect"]["effects"]
    blow = next(e for e in eff if e.get("type") == "Delayed" and e.get("tick") == 22)
    inner = [e for e in blow["effects"] if FLAG not in json.dumps(e)]
    return {**ult, "effect": {**ult["effect"], "effects": [
        e if e is not blow else {**blow, "effects": [rm(FLAG), flag(FLAG, HOLD)] + inner + kill_check()}
        for e in eff]}}


def main():
    with open(PATH, encoding="utf-8-sig") as f:
        text = f.read()
    data = json.loads(text)
    new = dict(data, ult=patched(data["ult"]))
    out = json.dumps(new, ensure_ascii=False, indent=2) + "\n"
    if "--check" in sys.argv:
        print("same" if json.loads(out) == data else "differs")
        return
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("wrote", PATH)


if __name__ == "__main__":
    main()
