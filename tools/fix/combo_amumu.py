#!/usr/bin/env python3
"""Amumu's League combos Q -> E and Q -> R: the bandage holds a champion, Tantrum / the Curse follow at once.

    python tools/fix/combo_amumu.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Amumu lands Bandage Toss, flies to the champion it stunned and
stomps (E) or curses everyone round it (R) the moment he arrives, inside the 1 s stun. Before this Q, E and R were
independent: after Q's 44-tick action the AI's E waited its own 20-tick wind-up (start_timing 20) and R 18 ticks
(start_timing 2 + a Delayed 16), so much of the stun was gone before they hit.

Design (pure data, the slots play it: league_mordekaiser's e_combo / league_braum's r_combo window):
  * Q's bandage (champion-only, `league_amumu_q_bandage`) adds the caster flag `league_amumu_q_combo` for WINDOW ticks
    in the `Delayed 2` of its hit that starts the dash and the pull pose (a third entry there; tools/fix/fix_amumu_q.py
    checks only the hit's five entries and that the Delayed starts with the dash, so it still runs after this). A
    bandage whose hit kills its champion opens no window (a Delayed on a dead unit skips caster buffs).
  * E (skill2) now starts at tick 1. Its burst (sound, stomp picture, the 28000 magic ring) branches on the flag:
    inside the window at once, otherwise in a `Delayed` E_AT - 1, on tick E_AT as before. Despair's pulse train and
    the Tantrum armour flag stay in one `Delayed` E_AT - 1 placed first, so outside the window everything still
    happens on tick E_AT in the old order.
  * R (ult, start_timing 2) branches the same way inside: its blast (`league_amumu_r_window` - it keeps Despair's
    weaker curse off while R's curse lasts - and the 42000 ring: damage, stun, curse, pictures) at once in the window,
    otherwise in the old `Delayed 16`; Despair's train keeps a `Delayed 16` of its own after it (r_window still comes
    before the train, as before; in a combo Despair already runs from Q's landing).
  * The window is shared and not consumed: Q -> E -> R can all come inside it (E's cooldown 270 and R's 3600 allow
    one cast each).
Why it is safe: no damage, stun or cooldown changes; nothing holds or empties a slot (E and R always fire, the AI
never casts a no-op); the flag has no `view_buffs` entry (invisible) and a timer, and death clears it. Despair's
5462-character train is still written once per slot (no second copy: the game copies `skill2` every tick); the only
copies are E's 3-effect burst and R's 2-effect blast in their fast and waiting branches (the repo's window way; skill2
gains 9 nodes). The waiting Delayeds are 16-19 ticks, well under the chains champion-data.md section 5 leaves
unguarded. Amumu has no add-on copy (no addons/league_amumu*). Idempotent: the three places are rebuilt from their
parts on every run, so a second run writes the same bytes; --check exits 1 when the file differs from what this
script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_amumu.data_champion")
N = "league_amumu_"
FLAG = N + "q_combo"
WINDOW = 90   # ticks from the bandage's hit (+2): Q's action ends 44 ticks after its cast, the hit comes on tick 17-29
E_AT = 20     # E's original start_timing
R_WAIT = 16   # R's original Delayed (start_timing 2)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def copy(x):
    return json.loads(json.dumps(x))


def is_ours(x):
    return FLAG in json.dumps(x)


def window_flag():
    return {"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": WINDOW}}},
            "only_to_enemy": False}


def branch(effects, wait):
    """At once inside the window, else after `wait` ticks: the same effects in both."""
    return {"type": "SwitchByBuff", "buff_name": FLAG,
            "effect_buff": {"type": "Combine", "effects": copy(effects)},
            "effect_none": {"type": "Delayed", "tick": wait, "effects": copy(effects)}}


def split_branch(sw, wait):
    assert sw["type"] == "SwitchByBuff" and sw["buff_name"] == FLAG, sw.get("type")
    fast = sw["effect_buff"]["effects"]
    assert sw["effect_none"]["type"] == "Delayed" and sw["effect_none"]["tick"] == wait
    assert sw["effect_none"]["effects"] == fast, "the two branches differ"
    return fast


def is_despair(e):
    return e.get("type") == "SwitchByBuff" and e.get("buff_name") == N + "despair"


def is_tantrum(e):
    return e.get("type") == "SwitchByBuff" and e.get("buff_name") == N + "tantrum"


def fix_q(d):
    bandage = [e for e in d["skill"]["effect"]["effects"]
               if e.get("type") == "LinearProjectile" and e.get("name") == N + "q_bandage"]
    assert len(bandage) == 1, "Q's bandage not found"
    hit = bandage[0]["applied_effects"]
    assert bandage[0]["applied_target"] == "EnemyChampion"
    assert [a["effect"]["type"] for a in hit] == ["ApAttack", "Stun", "ViewEffect", "TargetSfx", "Delayed"], \
        "run tools/fix/fix_amumu_q.py first"
    later = hit[4]["effect"]["effects"]
    rest = [e for e in later if not is_ours(e)]
    assert [e["type"] for e in rest] == ["MoveToTarget", "CasterAnimation"], [e["type"] for e in rest]
    hit[4]["effect"]["effects"] = rest + [window_flag()]


def fix_e(d):
    e = d["skill2"]
    fx = e["effect"]["effects"]
    if e["start_timing"] == E_AT:
        assert not is_ours(fx), "a combo flag in E's original tree"
        assert [x["type"] for x in fx] == ["Sfx", "SwitchByBuff", "SwitchByBuff", "CasterViewEffect", "RangeEffect"]
        assert is_despair(fx[1]) and is_tantrum(fx[2])
        keep, burst = [fx[1], fx[2]], [fx[0], fx[3], fx[4]]
    else:
        assert e["start_timing"] == 1 and len(fx) == 2, "unknown E tree"
        assert fx[0]["type"] == "Delayed" and fx[0]["tick"] == E_AT - 1
        keep, burst = fx[0]["effects"], split_branch(fx[1], E_AT - 1)
    assert len(keep) == 2 and is_despair(keep[0]) and is_tantrum(keep[1])
    assert [x["type"] for x in burst] == ["Sfx", "CasterViewEffect", "RangeEffect"]
    assert burst[2]["shape"] == {"Circle": {"radius": 28000}}
    e["start_timing"] = 1
    e["effect"] = {"type": "Combine", "effects": [{"type": "Delayed", "tick": E_AT - 1, "effects": keep},
                                                  branch(burst, E_AT - 1)]}


def fix_r(d):
    r = d["ult"]
    assert r["start_timing"] == 2
    fx = r["effect"]["effects"]
    assert fx[0]["type"] == "Sfx" and is_tantrum(fx[1])
    if len(fx) == 3:
        assert fx[2]["type"] == "Delayed" and fx[2]["tick"] == R_WAIT and not is_ours(fx[2])
        inner = fx[2]["effects"]
        assert len(inner) == 3 and is_despair(inner[1]), "unknown R tree"
        despair, blast = inner[1], [inner[0], inner[2]]
    else:
        assert len(fx) == 4 and fx[3]["type"] == "Delayed" and fx[3]["tick"] == R_WAIT, "unknown R tree"
        assert len(fx[3]["effects"]) == 1
        despair, blast = fx[3]["effects"][0], split_branch(fx[2], R_WAIT)
    assert is_despair(despair)
    assert blast[0]["type"] == "AddCasterBuff" and blast[0]["buff_state"]["name"] == N + "r_window"
    assert blast[1]["type"] == "RangeEffect" and blast[1]["shape"] == {"Circle": {"radius": 42000}}
    r["effect"]["effects"] = [fx[0], fx[1], branch(blast, R_WAIT),
                              {"type": "Delayed", "tick": R_WAIT, "effects": [despair]}]


def apply(d):
    fix_q(d)
    fix_e(d)
    fix_r(d)
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
        print("already done" if done else "Q -> E / Q -> R combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: Q's champion hit opens {FLAG} ({WINDOW} ticks); E and R cast in it fire at once "
          f"(otherwise on tick {E_AT} / {2 + R_WAIT} as before)")


if __name__ == "__main__":
    main()
