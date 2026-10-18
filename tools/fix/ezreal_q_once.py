#!/usr/bin/env python3
"""league_ezreal skill: Mystic Shot (Q) written once instead of twice (skill-tree slimming, 2026-10-18).

    python tools/fix/ezreal_q_once.py [--check]

skill is Q with W folded in: with W on cooldown (`w_cd`) it is Q; otherwise a search for an enemy champion within
110000 throws W at him (W's cooldown, the 1-tick flag `w_thrown`, the W orb and a Q on the champion after it), and
without one (`w_thrown` off) Q again. The two plain Q casts were equal copies (39 nodes each; the game copies skill
every tick, docs/perf.md). `w_thrown` is added by that search alone (the attack, skill2 and ult never name it) and
lasts 1 tick, and skill casts are 26 ticks apart at the least (its action), so `w_thrown` is off whenever a cast
starts - with W on cooldown too. So:

    SwitchByBuff w_cd (Q) (search -> w_thrown; SwitchByBuff w_thrown () (Q))
 -> search unless w_cd (it sets w_thrown); SwitchByBuff w_thrown () (Q); w_thrown off

runs the same effects in the same order in every case and draws the search's random number in the same casts. Units
read the tree through her buffs at any tick (the AI before a cast, enemies weighing her): `w_thrown` is taken off at
the end of the run that read it, so it is never on when anyone reads, and with it off both forms hold Q, plus the
search when W is ready - also in the tick of a throw, when the old form read Q through the just-added `w_cd`.
The flag's removal changes only the buff list of that tick (check: SAME_TRACE=trace2.exe
TRACE_HIDE=league_ezreal_w_thrown). Idempotent: --check reports whether the file is already done.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_ezreal.data_champion")
N = "league_ezreal_"
NONE = {"type": "Combine", "effects": []}


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
    e = d["skill"]["effect"]
    done = (e.get("type") == "Combine" and len(e["effects"]) == 3
            and e["effects"][2] == {"type": "RemoveCasterBuff", "name": N + "w_thrown"})
    if a.check:
        print("already done" if done else "Q still written twice")
        sys.exit(0 if done else 1)
    if done:
        print("already done")
        return
    assert e["type"] == "SwitchByBuff" and e["buff_name"] == N + "w_cd", "skill is not the w_cd switch"
    q = e["effect_buff"]
    assert e["effect_none"]["type"] == "Combine"
    search, choice = e["effect_none"]["effects"]
    assert search["type"] == "RandomTarget" and search["casting_target"] == "EnemyChampion"
    thrown = {"type": "AddCasterBuff", "buff_state": {"name": N + "w_thrown", "duration": {"Time": {"tick": 1}}},
              "only_to_enemy": False}
    assert thrown in search["effects"], "the search no longer adds w_thrown for 1 tick"
    assert choice["type"] == "SwitchByBuff" and choice["buff_name"] == N + "w_thrown"
    assert choice["effect_buff"] == NONE
    assert key(choice["effect_none"]) == key(q), "the two Q casts differ"
    assert json.dumps(d["skill"]).count(N + "w_thrown") == 2, "skill names w_thrown elsewhere"
    for slot in ("attack", "skill2", "ult"):
        assert N + "w_thrown" not in json.dumps(d[slot]), f"{slot} names w_thrown too"
    assert d["skill"]["duration"] >= 2 and d["skill"]["cooltime"] >= 2
    d["skill"]["effect"] = {"type": "Combine", "effects": [
        {"type": "SwitchByBuff", "buff_name": N + "w_cd", "effect_buff": dict(NONE), "effect_none": search},
        choice,
        {"type": "RemoveCasterBuff", "name": N + "w_thrown"}]}
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: skill's Q written once")


if __name__ == "__main__":
    main()
