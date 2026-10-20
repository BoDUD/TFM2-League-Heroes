#!/usr/bin/env python3
"""Leona's League combo E -> Q: Zenith Blade roots a champion and pulls her to it, Shield of Daybreak stuns at once.

    python tools/fix/combo_leona.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Leona throws E, dashes to the champion it roots and bashes it with Q
the moment she lands, so the 0.5 s root runs straight into the 1 s stun. Before this E and Q were independent: E's
root lasts 30 ticks from the hit and the E action 36 ticks, so the AI's Q came after E ended and then waited Q's own
11-tick wind-up (start_timing 11): the bash landed a few ticks after the root ran out, and the target could step away.

Design (pure data, the slot plays it: league_mordekaiser's e_combo / league_braum's r_combo window):
  * E's champion-only seeking blade (`league_leona_e_seek`, not penetrating, hits only the first enemy champion) adds
    the caster flag `league_leona_e_combo` for WINDOW ticks on its hit, beside the root and the dash
    (`{"casting_type": "Targeting", "effect": AddCasterBuff}`, the caster-flag-from-a-hit form of tools/fix/warp_beacon.py).
  * Q (skill) now starts at tick 1 and branches on that flag: inside the window the bash (its sound, the damage, the
    stun, Sunlight, its pictures - Q's whole effect, unchanged) lands at once; otherwise it waits in a `Delayed`
    Q_AT - 1, i.e. on tick Q_AT as before. The window is not consumed: Q's 300-tick cooldown allows one Q in it.
Why it is safe: no damage, stun or cooldown changes; nothing holds or empties a slot (Q always bashes, the AI never
casts a no-op); the flag has no `view_buffs` entry (invisible) and a timer, and death clears it (champion-data.md
section 5). The only copy is Q's 7-node bash (the fast and the waiting branch, the repo's window way); `skill` grows
from 8 to 18 nodes. The waiting `Delayed` is 10 ticks, well under the chains section 5 leaves unguarded. Leona has no
add-on copy (no addons/league_leona*). Idempotent: Q's tree and the seek's entry are rebuilt from the bash on every
run, so a second run writes the same bytes; --check exits 1 when the file differs from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_leona.data_champion")
N = "league_leona_"
FLAG = N + "e_combo"
WINDOW = 90   # ticks from the seek's hit: E ends 36 ticks after its cast, the hit comes on tick 10-20 of it
Q_AT = 11     # Q's original start_timing: the bash's tick outside the window


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def window_flag():
    return {"casting_type": "Targeting",
            "effect": {"type": "AddCasterBuff",
                       "buff_state": {"name": FLAG, "duration": {"Time": {"tick": WINDOW}}},
                       "only_to_enemy": False}}


def is_ours(entry):
    return FLAG in json.dumps(entry)


def bash_of(q):
    """Q's bash, from the original kit (the whole effect, start_timing Q_AT) or from this script's branch."""
    effects = q["effect"]["effects"]
    if q["start_timing"] == Q_AT:
        assert not any(is_ours(e) for e in effects), "a combo flag in Q's original tree"
        return effects
    assert q["start_timing"] == 1 and len(effects) == 1 and effects[0]["type"] == "SwitchByBuff", "unknown Q tree"
    sw = effects[0]
    assert sw["buff_name"] == FLAG
    fast = sw["effect_buff"]["effects"]
    wait = sw["effect_none"]
    assert wait["type"] == "Delayed" and wait["tick"] == Q_AT - 1 and wait["effects"] == fast, "Q's branches differ"
    return fast


def apply(d):
    q = d["skill"]
    bash = bash_of(q)
    kinds = [e["type"] for e in bash]
    assert kinds == ["Sfx", "Attack", "ApAttack", "Stun", "AddBuff", "ViewEffect", "TargetSfx"], kinds
    q["start_timing"] = 1
    q["effect"] = {"type": "Combine", "effects": [
        {"type": "SwitchByBuff", "buff_name": FLAG,
         "effect_buff": {"type": "Combine", "effects": json.loads(json.dumps(bash))},
         "effect_none": {"type": "Delayed", "tick": Q_AT - 1, "effects": json.loads(json.dumps(bash))}}]}

    seeks = [e for e in d["skill2"]["effect"]["effects"]
             if e.get("type") == "LinearProjectile" and e.get("name") == N + "e_seek"]
    assert len(seeks) == 1, "E's seeking blade not found"
    seek = seeks[0]
    assert seek["applied_target"] == "EnemyChampion" and seek["penetrate"] is False
    hit = [a for a in seek["applied_effects"] if not is_ours(a)]
    assert [a["effect"]["type"] for a in hit] == ["Bind", "ViewEffect", "TargetSfx", "MoveToTarget",
                                                   "CasterAnimation"], hit
    seek["applied_effects"] = hit + [window_flag()]
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
    print(f"{a.path}: E's champion hit opens {FLAG} ({WINDOW} ticks); Q cast in it bashes at once "
          f"(otherwise on tick {Q_AT} as before)")


if __name__ == "__main__":
    main()
