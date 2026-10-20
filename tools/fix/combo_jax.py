#!/usr/bin/env python3
"""Jax's League combo E -> Q: Leap Strike cast during Counter Strike ends the stance on landing - the stun on arrival.

    python tools/fix/combo_jax.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Jax starts Counter Strike, leaps onto the champion with Q and recasts
E as he lands, so the stun comes the moment he arrives. Here E (skill2) raises `league_jax_e_on` (92 ticks, the dodge)
and bursts by itself 90 ticks later; a Q cast during the stance leapt in and then waited for the timer, so the stun
came up to 1.5 s after the landing.

Design (pure data, the slot it spends plays it: league_leesin's way):
  * Q's landing (the MoveToTarget's end_effects, before the strike) gets `SwitchByBuff league_jax_e_on`: in the stance
    it runs Counter Strike's own burst, copied from E's timer branch (spend `e_on`, the burst pose, 4 ticks later the
    32000 burst: 60 + 100% AP, the 1 s stun, the 4% max-health hit on champions, its pictures and sounds), queued on
    Jax himself (`RandomTarget {range 1, AllyOnlySelf}`), so a strike that kills its target does not lose it (a
    `Delayed` queued on a unit that died runs only its pictures). E's own timer then finds no `e_on` and does
    nothing: one burst per E, as before. Outside the stance the landing is unchanged.
  * While the stance holds, the AI's reading of Q follows that branch (champion-data section 8: the reading follows
    the flags the caster has), so Q reads as the leap plus the burst and stun - the AI leans to Q during the stance.
Why it is safe: no number changes, the burst only comes sooner (and the dodge ends with it, as League's recast); no
slot is held or emptied (Q always leaps and strikes). Q's tree gains the burst's 16 nodes (the game copies `skill`
every tick: Q stays small, 20 -> 36 nodes). Jax has no add-on copy (no addons/league_jax*). Idempotent: the node is
rebuilt from E's burst on every run; --check exits 1 when the file differs from what this script writes.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_jax.data_champion")
E_ON = "league_jax_e_on"
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def is_ours(e):
    return e.get("type") == "SwitchByBuff" and e.get("buff_name") == E_ON


def burst_of(d):
    timers = [x for x in d["skill2"]["effect"]["effects"] if x.get("type") == "Delayed"]
    assert len(timers) == 1 and len(timers[0]["effects"]) == 1, "E's timer not found"
    sw = timers[0]["effects"][0]
    assert sw["type"] == "SwitchByBuff" and sw["buff_name"] == E_ON, "E's timer no longer reads e_on"
    burst = sw["effect_buff"]
    kinds = [x["type"] for x in burst["effects"]]
    assert kinds == ["RemoveCasterBuff", "CasterAnimation", "Delayed"], kinds
    return copy.deepcopy(burst)


def apply(d):
    q = d["skill"]["effect"]
    dives = [x for x in q["effects"] if x.get("type") == "MoveToTarget"]
    assert q["type"] == "Combine" and len(dives) == 1, "Q no longer has one MoveToTarget in its Combine"
    dive = dives[0]
    ends = [x for x in dive["end_effects"] if not is_ours(x)]
    assert ends[0]["type"] == "Attack", "Q's landing no longer starts with the strike"
    node = {"type": "SwitchByBuff", "buff_name": E_ON,
            "effect_buff": {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf",
                            "from_projectile": False, "effects": [burst_of(d)]},
            "effect_none": copy.deepcopy(NONE)}
    dive["end_effects"] = [node] + ends
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(apply(json.loads(raw)), ensure_ascii=False, indent=2).replace("\n", nl) + nl
    if a.check:
        done = text == raw
        print("already done" if done else "E -> Q combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: Q landing during {E_ON} bursts Counter Strike at once (stun on arrival)")


if __name__ == "__main__":
    main()
