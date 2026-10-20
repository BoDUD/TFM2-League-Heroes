#!/usr/bin/env python3
"""Miss Fortune's League combo E -> R: Bullet Time opens at once on champions Make It Rain is slowing.

    python tools/fix/combo_missfortune.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Miss Fortune drops Make It Rain on the enemy team and channels Bullet
Time into the champions it slows (40% here), so they cannot walk out of the cone. Before this E and R were independent:
R always stood through its 8-tick wind-up (start_timing 8) before the first wave, whatever came before it.

Design (pure data, the slot plays it: league_mordekaiser's e_combo / league_leona's E -> Q window):
  * E (skill2) gets a champion-only twin of its rain (`league_missfortune_e_champ`: the same 30000 circle, 120 ticks,
    a pulse every 15 from tick 0, on `EnemyChampion`, no picture, no damage). Each pulse that finds a champion renews
    the caster flag `league_missfortune_e_combo` for WINDOW ticks (removed first, so one instance).
  * R (ult) now starts at tick 1 and branches on that flag: inside the window Bullet Time's whole tree (the cast sound,
    `bullet_time`, the channel's animation, the 12 guarded waves and the end) runs at once; otherwise the same tree
    waits in a `Delayed` R_AT - 1, i.e. starts on tick R_AT as before. The window is not consumed (R's 50 s cooldown
    allows one R in it).
Why it is safe: no damage, slow, cooldown or wave count changes; the R slot always channels (the AI never casts a
no-op), both branches hold the waves, so the AI and the enemies read the same damage as before; the flag has no
`view_buffs` entry (invisible) and a timer, and death clears it. The second copy is R's tree (355 -> 712 nodes): the
game copies only skill and skill2 every tick (docs/perf.md), so the ult's size costs nothing per tick; E (skill2) grows
from 8 to 12 nodes. The waves keep their own guards (the `lives` search, champion-data.md section 5), so a dead Miss
Fortune fires nothing. Miss Fortune has no add-on copy (no addons/league_missfortune*) and no kit generator.
Idempotent: R's tree and the twin are rebuilt from the original on every run, so a second run writes the same bytes;
--check exits 1 when the file differs from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_missfortune.data_champion")
N = "league_missfortune_"
FLAG = N + "e_combo"
TWIN = N + "e_champ"
WINDOW = 60   # ticks after the last rain pulse that found a champion (the rain lasts 120 ticks, pulses every 15)
R_AT = 8      # R's original start_timing: the first wave's tick outside the window


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def ours(entry):
    return FLAG in json.dumps(entry)


def window_flag():
    return {"casting_type": "Targeting",
            "effect": {"type": "Combine", "effects": [
                {"type": "RemoveCasterBuff", "name": FLAG},
                {"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": WINDOW}}},
                 "only_to_enemy": False}]}}


def channel_of(r):
    """Bullet Time's tree, from the original kit (start_timing R_AT) or from this script's branch."""
    effects = r["effect"]["effects"]
    if r["start_timing"] == R_AT:
        assert not any(ours(e) for e in effects), "a combo flag in R's original tree"
        return effects
    assert r["start_timing"] == 1 and len(effects) == 1 and effects[0]["type"] == "SwitchByBuff", "unknown R tree"
    sw = effects[0]
    assert sw["buff_name"] == FLAG
    fast = sw["effect_buff"]["effects"]
    wait = sw["effect_none"]
    assert wait["type"] == "Delayed" and wait["tick"] == R_AT - 1 and wait["effects"] == fast, "R's branches differ"
    return fast


def apply(d):
    r = d["ult"]
    channel = channel_of(r)
    kinds = [e["type"] for e in channel]
    assert kinds[:3] == ["Sfx", "AddCasterBuff", "CasterAnimation"] and set(kinds[3:]) == {"Delayed"}, kinds
    r["start_timing"] = 1
    r["effect"] = {"type": "Combine", "effects": [
        {"type": "SwitchByBuff", "buff_name": FLAG,
         "effect_buff": {"type": "Combine", "effects": json.loads(json.dumps(channel))},
         "effect_none": {"type": "Delayed", "tick": R_AT - 1, "effects": json.loads(json.dumps(channel))}}]}

    effects = [e for e in d["skill2"]["effect"]["effects"] if e.get("name") != TWIN]
    rains = [i for i, e in enumerate(effects)
             if e.get("type") == "RangePeriodProjectile" and e.get("name") == N + "e_zone"]
    assert len(rains) == 1, "E's rain not found"
    rain = effects[rains[0]]
    assert rain["applied_target"] == "EnemyWithoutTower" and not ours(rain)
    twin = {"type": "RangePeriodProjectile", "name": TWIN, "shape": rain["shape"], "tick": rain["tick"],
            "period": rain["period"], "first_delay": rain["first_delay"], "applied_target": "EnemyChampion",
            "applied_effects": [window_flag()], "end_effects": []}
    effects.insert(rains[0] + 1, json.loads(json.dumps(twin)))
    d["skill2"]["effect"]["effects"] = effects
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
    print(f"{a.path}: E's rain on a champion opens {FLAG} ({WINDOW} ticks); R cast in it fires its first wave at "
          f"once (otherwise on tick {R_AT} as before)")


if __name__ == "__main__":
    main()
