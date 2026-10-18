#!/usr/bin/env python3
"""league_yone skill2: Spirit Cleave (W) written once instead of twice (skill-tree slimming, 2026-10-18).

    python tools/fix/yone_w_once.py [--check]

skill2 is E with W folded in: with E on cooldown (`e_cd`) it is W; otherwise a search for an enemy champion within
50000 sets the 2-tick flag `e_near`, and with it E dashes (its own W at the end of the dash), without it W again. The
two plain W casts were equal copies (143 nodes each; the game copies skill2 every tick, docs/perf.md). `e_near` is set
by that search alone and read right after it, nowhere else. So:

    SwitchByBuff e_cd (W) (search -> e_near; SwitchByBuff e_near (E) (W))
 -> search unless e_cd (it sets e_near); SwitchByBuff e_near (E) (W); e_near off

runs the same effects in the same order in every case and draws the search's random number in the same casts.
Units read skill2 through her buffs at any tick (the AI before a cast, enemies at other times): before, they always
read W (`e_near` is only ever on just after an E, when `e_cd` is on too); taking `e_near` off in the same run keeps
it so (it never lasts past the cast now, so the 2-tick flag no longer shows in her buff list). Idempotent: --check
reports whether the file is already done.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_yone.data_champion")
N = "league_yone_"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def key(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8-sig")
    d = json.loads(raw)
    e = d["skill2"]["effect"]
    done = e.get("type") == "Combine" and e["effects"][-1] == {"type": "RemoveCasterBuff", "name": N + "e_near"}
    if a.check:
        print("already done" if done else "W still written twice")
        sys.exit(0 if done else 1)
    if done:
        print("already done")
        return
    assert e["type"] == "SwitchByBuff" and e["buff_name"] == N + "e_cd", "skill2 is not the e_cd switch"
    w = e["effect_buff"]
    search, choice = e["effect_none"]["effects"]
    assert search["type"] == "RandomTarget" and choice["buff_name"] == N + "e_near"
    assert search["effects"] == [{"type": "AddCasterBuff", "buff_state": {"name": N + "e_near",
                                  "duration": {"Time": {"tick": 2}}}, "only_to_enemy": False}]
    assert key(choice["effect_none"]) == key(w), "the two W casts differ"
    for slot in ("attack", "skill", "ult"):
        assert N + "e_near" not in json.dumps(d[slot]), f"{slot} reads e_near too"
    d["skill2"]["effect"] = {"type": "Combine", "effects": [
        {"type": "SwitchByBuff", "buff_name": N + "e_cd", "effect_buff": {"type": "Combine", "effects": []},
         "effect_none": search},
        choice,
        {"type": "RemoveCasterBuff", "name": N + "e_near"}]}
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: skill2's W written once")


if __name__ == "__main__":
    main()
