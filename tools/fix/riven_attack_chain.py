#!/usr/bin/env python3
"""Riven's basic attacks take turns between League's three swings: attack -> attack2 -> attack3 -> attack ..., and in
her R form attack_r -> attack2_r -> attack3_r (tools/art/rig_riven_hd.py MORE_ATTACKS draws them from riven_attack1/2/3
and riven_attack1_ult / riven_attack2_ult / riven_attack3).

    python tools/fix/riven_attack_chain.py [--check]

The user, 2026-10-18: 「打的时候一套姿势吗？」「锐雯没有放技能时一直一个姿势吧」. Pure data, league_sett's grit chain
(champion-data: SwitchByBuff ladders): two short caster flags count the swings - with `league_riven_aa3` the attack plays
attack3 and clears it, with `league_riven_aa2` it plays attack2 and swaps it for aa3, with neither it plays the first
swing and sets aa2. The flags last HOLD ticks, so out of combat the chain starts again from the first swing. The
attack's first effect (its R-form animation switch) is replaced; everything after it (the hit) is kept. Idempotent.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_riven.data_champion")
R_BUFF, AA2, AA3 = "league_riven_r", "league_riven_aa2", "league_riven_aa3"
HOLD = 180
NONE = {"type": "Combine", "effects": []}


def flag(name):
    return {"type": "AddCasterBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": HOLD}}},
            "only_to_enemy": False}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def swing(normal, tick):
    """The animation of this swing: `normal`, or its `_r` form while her blade is reforged. The first swing is the
    action's own animation (attack), so in the normal form it plays nothing."""
    return {"type": "SwitchByBuff", "buff_name": R_BUFF, "effect_buff": anim(normal + "_r", tick),
            "effect_none": anim(normal, tick) if normal != "attack" else NONE}


def chain(tick):
    return {"type": "SwitchByBuff", "buff_name": AA3,
            "effect_buff": {"type": "Combine", "effects": [rm(AA3), swing("attack3", tick)]},
            "effect_none": {"type": "SwitchByBuff", "buff_name": AA2,
                            "effect_buff": {"type": "Combine", "effects": [rm(AA2), flag(AA3), swing("attack2", tick)]},
                            "effect_none": {"type": "Combine", "effects": [flag(AA2), swing("attack", tick)]}}}


def patched(attack):
    eff = attack["effect"]["effects"]
    first = eff[0]
    if first.get("type") != "SwitchByBuff" or first.get("buff_name") not in (R_BUFF, AA3):
        sys.exit("league_riven attack: its first effect is not the R-form switch")
    return {**attack, "effect": {**attack["effect"], "effects": [chain(attack["duration"])] + eff[1:]}}


def main():
    with open(PATH, encoding="utf-8-sig") as f:
        data = json.loads(f.read())
    new = dict(data, attack=patched(data["attack"]))
    out = json.dumps(new, ensure_ascii=False, indent=2) + "\n"
    if "--check" in sys.argv:
        print("same" if json.loads(out) == data else "differs")
        return
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("wrote", PATH)


if __name__ == "__main__":
    main()
