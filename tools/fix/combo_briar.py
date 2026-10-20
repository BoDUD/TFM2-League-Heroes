#!/usr/bin/env python3
"""Briar's League combo Q -> W2: Head Rush stuns a champion, Snack Attack bites it on the very next attack.

    python tools/fix/combo_briar.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Briar recasts Blood Frenzy (Snack Attack) when she chooses - the
burst players open with is Head Rush's stun and the Snack at once, while the champion cannot step away. Here W is
folded into Q: Head Rush's landing starts Blood Frenzy and the caster flag `league_briar_snack_wait` (120 ticks), and
the first attack after it runs out is the Snack (30 + 130% AD + 4% max health, heals her; `snack_done` keeps it to
one per frenzy). So the Snack always came 2 s after the landing, long after the 0.5 s stun, whoever she had leapt on.

Design (pure data, one number in one branch): Head Rush is aimed twice - a `RandomTarget {47500, EnemyChampion}` that
leaps on a champion in reach, else the cast target (a minion or a monster). In the champion branch the landing's
`snack_wait` now lasts SNACK_FAST ticks: it runs out before her first attack (Q's action is 24 ticks, the landing at
most about tick 20, the attack's hit 6-8 ticks into it), so that attack is the Snack and it lands inside the stun.
On minions and monsters the 2 s wait stays (the end-of-frenzy bite that heals her while she clears a camp), and the
Snack of Total Frenzy (the ult) is untouched.
Why it is safe: no damage, heal or cooldown changes and no slot involved; still one Snack per Head Rush. The flag is
the kit's own (invisible, timed). Briar has no add-on copy (no addons/league_briar*) and no other script touches Q.
Idempotent: the value is set, not added, so a second run writes the same bytes; --check exits 1 when the file differs
from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_briar.data_champion")
N = "league_briar_"
WAIT = N + "snack_wait"
SNACK_SLOW = 120   # the kit's wait (2 s), kept on minions and monsters
SNACK_FAST = 6     # after a champion landing: the first attack is the Snack


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def frenzy_start(move):
    """The landing's Combine that starts Blood Frenzy, and its snack_wait buff."""
    assert move["type"] == "MoveToTarget"
    starts = [e for e in move["end_effects"] if e.get("type") == "Combine"
              and any(x.get("type") == "AddCasterBuff" and x["buff_state"]["name"] == WAIT for x in e["effects"])]
    assert len(starts) == 1, "Head Rush's frenzy start not found"
    waits = [x for x in starts[0]["effects"] if x.get("type") == "AddCasterBuff" and x["buff_state"]["name"] == WAIT]
    assert len(waits) == 1
    return waits[0]["buff_state"]["duration"]["Time"]


def apply(d):
    fx = d["skill"]["effect"]["effects"]
    assert [x["type"] for x in fx] == ["Sfx", "RandomTarget", "SwitchByBuff"], "Head Rush changed"
    champ, rest = fx[1], fx[2]
    assert champ["casting_target"] == "EnemyChampion" and rest["buff_name"] == N + "q_aim"
    fast = frenzy_start(champ["effects"][2])
    slow = frenzy_start(rest["effect_none"]["effects"][1])
    assert fast["tick"] in (SNACK_SLOW, SNACK_FAST) and slow["tick"] == SNACK_SLOW, (fast, slow)
    fast["tick"] = SNACK_FAST
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
        print("already done" if done else "Q -> W2 combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: after Head Rush on a champion the Snack waits {SNACK_FAST} ticks (minions / monsters "
          f"{SNACK_SLOW})")


if __name__ == "__main__":
    main()
