#!/usr/bin/env python3
"""Diana's League combo (Q ->) E -> R: Lunar Rush lands among champions, Moonfall pulls them in at once.

    python tools/fix/combo_diana.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Diana marks with Q, dashes in with E (the Moonlight reset gives a
second dash) and casts R the moment she lands, so Moonfall pulls everyone round her before they react. The kit already
had Q -> E (a Q hit within 3 s makes E dash twice); R was independent: cast after E's 26-tick action, it waited its own
16-tick wind-up before the pull (start_timing 16), and the champions she had landed on were walking away.

Design (pure data, the slot plays it: league_mordekaiser's r_combo / tools/fix/combo_malphite.py's landing check):
  * Each E landing - the first dash's `end_effects` and the second dash's champion branch (`RandomTarget
    EnemyChampion` -> `MoveToTarget`) - gets a champion-only check round her: a `RangeEffect {LAND_R, EnemyChampion,
    AroundCaster}` that sets the caster flag `league_diana_e_combo` for WINDOW ticks (removed first, so however many
    champions it finds, one flag). LAND_R is R's cast range: the AI casts R only with a champion that close.
  * R (ult) now starts at tick 1 and branches on the flag: inside the window the flag is taken off and Moonfall's
    whole effect (the pull, the slow, the champion count, the moon 40 ticks later and the crash 60 ticks later) starts
    at once; otherwise it waits in a `Delayed` R_AT - 1, on tick R_AT as before.
So after E lands among champions the AI's R (if ready) pulls them in on its first tick and the crash comes 15 ticks
sooner. A landing with no champion within LAND_R opens nothing.
Why it is safe: no damage, pull, slow or cooldown changes; R always fires (both branches carry it: the AI never casts a
no-op) and no slot is held; the flag is invisible (no `view_buffs` entry), timed and cleared by death. R's tree is
copied once (ult only: the game copies skill and skill2 every tick, not the ult, docs/perf.md); E gains 2 x 4 nodes.
Outside the window R's effect is now queued from tick 1 in a 15-tick `Delayed` (the repo's window way, as Leona's Q
and Amumu's E), well under the chains champion-data.md section 5 leaves unguarded. Diana has no add-on copy (no
addons/league_diana*) and no other script rebuilds E or R. Idempotent: R's tree and the two checks are rebuilt from
their parts on every run, so a second run writes the same bytes; --check exits 1 when the file differs from what this
script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_diana.data_champion")
N = "league_diana_"
FLAG = N + "e_combo"
WINDOW = 90     # ticks from the landing: E's action is 26 ticks, the second dash leaves 8 ticks after the first lands
LAND_R = 25000  # R's cast range
R_AT = 16       # R's original start_timing


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def copy(x):
    return json.loads(json.dumps(x))


def is_ours(x):
    return FLAG in json.dumps(x)


def landing_check():
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": LAND_R}}, "target": "EnemyChampion",
            "apply_type": "AroundCaster",
            "effects": [{"type": "RemoveCasterBuff", "name": FLAG},
                        {"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": WINDOW}}},
                         "only_to_enemy": False}]}


def checked(move):
    assert move["type"] == "MoveToTarget"
    ends = [x for x in move["end_effects"] if not (x.get("type") == "RangeEffect" and is_ours(x))]
    assert ends[0]["type"] == "ApAttack", "E's landing changed"
    move["end_effects"] = ends + [landing_check()]


def fix_e(d):
    fx = d["skill2"]["effect"]["effects"]
    assert [x["type"] for x in fx] == ["Sfx", "Combine", "SwitchByBuff", "CasterAnimation", "MoveToTarget"]
    first = fx[4]
    checked(first)
    again = [x for x in first["end_effects"] if x.get("type") == "Delayed"]
    assert len(again) == 1 and again[0]["effects"][0]["buff_name"] == N + "e_again", "the second dash moved"
    dash2 = again[0]["effects"][0]["effect_buff"]["effects"][1]["effects"]
    champ = dash2[1]
    assert champ["type"] == "RandomTarget" and champ["casting_target"] == "EnemyChampion"
    assert champ["effects"][2]["type"] == "MoveToTarget"
    checked(champ["effects"][2])


def fix_r(d):
    r = d["ult"]
    fx = r["effect"]["effects"]
    if r["start_timing"] == R_AT:
        assert not is_ours(fx), "a combo flag in R's original tree"
        body = fx
    else:
        assert r["start_timing"] == 1 and len(fx) == 1 and fx[0]["buff_name"] == FLAG, "unknown R tree"
        fast, wait = fx[0]["effect_buff"]["effects"], fx[0]["effect_none"]
        assert fast[0] == {"type": "RemoveCasterBuff", "name": FLAG}
        assert wait["type"] == "Delayed" and wait["tick"] == R_AT - 1 and wait["effects"] == fast[1:], "R differs"
        body = wait["effects"]
    pulls = [x for x in body if x.get("type") == "RangeEffect" and x["target"] == "EnemyChampion"]
    assert len(pulls) == 1 and any(e["type"] == "Grab" for e in pulls[0]["effects"]), "R's pull moved"
    r["start_timing"] = 1
    r["effect"]["effects"] = [{"type": "SwitchByBuff", "buff_name": FLAG,
                               "effect_buff": {"type": "Combine",
                                               "effects": [{"type": "RemoveCasterBuff", "name": FLAG}] + copy(body)},
                               "effect_none": {"type": "Delayed", "tick": R_AT - 1, "effects": copy(body)}}]


def apply(d):
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
        print("already done" if done else "E -> R combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: an E landing with a champion within {LAND_R} opens {FLAG} ({WINDOW} ticks); R cast in it "
          f"pulls at once (otherwise on tick {R_AT} as before)")


if __name__ == "__main__":
    main()
