#!/usr/bin/env python3
"""Thresh's League combo Q -> E: Death Sentence hooks a champion, Flay pulls him in at once.

    python tools/fix/combo_thresh.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Thresh hooks with Q and flays the champion the moment the chain has
him, so the 1 s stun runs into Flay's pull and slow. The kit already reads the hook: Q's invisible twin
(`league_thresh_q_bind`, it only hits a champion in crowd control: one the hook really stunned) adds the caster flag
`league_thresh_q_hooked` for 120 ticks, and E cast while it holds always pulls. But E still waited its own wind-up -
start_timing 8 plus a `Delayed` 5, the hit on tick 13 - so after Q's 40-tick action the flay came 13 ticks later,
late in the stun.

Design (pure data, the slot plays it: league_mordekaiser's e_combo / league_leona's E -> Q window):
  * E (skill2) now starts at tick 1 and branches on `league_thresh_q_hooked`: inside the window the flay (E's cast
    sound, the sweep picture and the hooked branch's pull - damage, 40% slow, Pull - unchanged) lands at once;
    otherwise E's whole original effect waits in a `Delayed` 7, i.e. the sweep on tick 8 and the hit on tick 13 as
    before (push or pull chosen there exactly as before).
  * The window is the existing 120-tick flag; it is not consumed (E's 6 s cooldown allows one E in it).
Not added: a cooldown refund - `skill_cooldown_mult` caps every skill's remaining cooldown, so refunding E on the hook
would also hand back Q's fresh 8 s (champion-data.md section 5); E cooling down when the hook lands simply misses the
combo as before. League's Q2 dash to the hooked target is not added either: the pack's hook pulls the champion in
instead (the user-approved kit), and both moving at once would only shorten the pull.
Why it is safe: no damage, slow, stun or cooldown changes; nothing holds or empties a slot (E always flays, the AI never
casts a no-op); the only copy is the hooked branch's 6-node RangeEffect, `skill2` grows from 27 to 39 nodes. The
waiting `Delayed` (7 + 5 ticks) is well under the chains section 5 leaves unguarded. Thresh has no add-on copy.
Idempotent: E's tree is rebuilt from the original on every run, so a second run writes the same bytes; --check exits 1
when the file differs from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_thresh.data_champion")
FLAG = "league_thresh_q_hooked"
E_AT = 8      # E's original start_timing: the sweep's tick outside the window


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def original_of(e):
    """E's original effect (start_timing E_AT), from the shipped kit or from this script's branch."""
    if e["start_timing"] == E_AT:
        return e["effect"]
    assert e["start_timing"] == 1, "unknown E tree"
    top = e["effect"]
    assert top["type"] == "Combine" and len(top["effects"]) == 1, "unknown E tree"
    sw = top["effects"][0]
    assert sw["type"] == "SwitchByBuff" and sw["buff_name"] == FLAG, "unknown E tree"
    wait = sw["effect_none"]
    assert wait["type"] == "Delayed" and wait["tick"] == E_AT - 1 and len(wait["effects"]) == 1, "unknown E wait"
    return wait["effects"][0]


def apply(d):
    e = d["skill2"]
    orig = original_of(e)
    kinds = [x["type"] for x in orig["effects"]]
    assert kinds == ["Sfx", "CasterViewEffect", "Delayed"], kinds
    cast, sweep, later = orig["effects"]
    hooked = later["effects"][0]
    assert hooked["type"] == "SwitchByBuff" and hooked["buff_name"] == FLAG, "E's hooked check moved"
    pull = hooked["effect_buff"]
    assert pull["type"] == "RangeEffect" and [x["type"] for x in pull["effects"]] == [
        "ApAttack", "AddBuff", "Pull", "ViewEffect", "TargetSfx"], pull
    e["start_timing"] = 1
    e["effect"] = {"type": "Combine", "effects": [
        {"type": "SwitchByBuff", "buff_name": FLAG,
         "effect_buff": {"type": "Combine", "effects": json.loads(json.dumps([cast, sweep, pull]))},
         "effect_none": {"type": "Delayed", "tick": E_AT - 1, "effects": [orig]}}]}
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
        print("already done" if done else "Q -> E combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: E cast while {FLAG} holds flays at once (otherwise on tick {E_AT} / hit 13 as before)")


if __name__ == "__main__":
    main()
