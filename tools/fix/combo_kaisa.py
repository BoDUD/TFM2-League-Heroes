#!/usr/bin/env python3
"""Kai'Sa's League combo W -> R: Void Seeker marks a champion with plasma, Killer Instinct launches at once.

    python tools/fix/combo_kaisa.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Kai'Sa can only cast R on a champion carrying plasma, so players
land W from afar (two stacks) and dash straight onto that champion. Here R targets any champion her team hit recently
(`EnemyChampionRecentlyAttacked`): a plasma gate made the AI waste 2 of its 4-5 Rs a game on an empty branch (README,
R row), so the gate stays out, and R ignored W: its launch always crouched 7 ticks first.

Design (pure data, the slot it spends plays it: league_mordekaiser's r_combo / league_leona's e_combo window):
  * W's bolt (non-penetrating, `EnemyChampion` only: its first champion) adds the caster flag `league_kaisa_w_combo`
    for WINDOW ticks on its hit, beside the damage and the plasma (the plasma's own 4 s).
  * R branches on that flag at its first tick: inside the window it launches at once - the launch burst, the dash
    pose and the dash onto the target with the landing shield, R's whole effect - and spends the window; otherwise
    the same effects wait in R's `Delayed 7` as before. The AI's R target is a champion her team hit recently: the
    one W just struck counts.
Why not the plasma gate: an R that does nothing without plasma is a no-op the AI still casts (measured before); this
way every R dashes and shields, and the W -> R chain is quicker. No number changes; nothing is held or emptied; the
flag has a timer and no `view_buffs` entry (invisible), and death clears it. The ult's tree is not copied every tick;
W's bolt gains 2 nodes. Kai'Sa has no add-on copy (no addons/league_kaisa*). Idempotent: R's tree is rebuilt from its
launch on every run, so a second run writes the same bytes; --check exits 1 when the file differs.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_kaisa.data_champion")
N = "league_kaisa_"
FLAG = N + "w_combo"
WINDOW = 240   # ticks from W's hit: the plasma stacks' own 4 s
R_AT = 7       # the launch's original Delayed


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def ours(x):
    return FLAG in json.dumps(x)


def launch_of(r):
    """R's launch effects, from the original kit (Delayed R_AT) or from this script's branch."""
    effects = r["effect"]["effects"]
    assert effects[0]["type"] == "Sfx" and len(effects) == 2, "unknown R tree"
    node = effects[1]
    if node["type"] == "Delayed":
        assert node["tick"] == R_AT and not ours(node), "R's launch moved"
        return node["effects"]
    assert node["type"] == "SwitchByBuff" and node["buff_name"] == FLAG, "unknown R tree"
    wait = node["effect_none"]
    assert wait["type"] == "Delayed" and wait["tick"] == R_AT, "R's waiting branch changed"
    fast = [e for e in node["effect_buff"]["effects"] if not ours(e)]
    assert fast == wait["effects"], "R's branches differ"
    return wait["effects"]


def w_bolt(d):
    found = []

    def walk(x):
        if isinstance(x, dict):
            if x.get("type") == "LinearProjectile" and x.get("name") == N + "w_bolt":
                found.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(d["skill2"]["effect"])
    assert len(found) == 1, f"W's bolt: {len(found)} found"
    return found[0]


def apply(d):
    bolt = w_bolt(d)
    assert bolt["applied_target"] == "EnemyChampion" and bolt["penetrate"] is False
    hit = [a for a in bolt["applied_effects"] if not ours(a)]
    bolt["applied_effects"] = hit + [T(rm(FLAG)), T({"type": "AddCasterBuff", "buff_state": {
        "name": FLAG, "duration": {"Time": {"tick": WINDOW}}}, "only_to_enemy": False})]

    r = d["ult"]
    launch = copy.deepcopy(launch_of(r))
    kinds = [e["type"] for e in launch]
    assert kinds == ["CasterViewEffect", "CasterAnimation", "MoveToTarget"], kinds
    r["effect"]["effects"] = [r["effect"]["effects"][0], {
        "type": "SwitchByBuff", "buff_name": FLAG,
        "effect_buff": {"type": "Combine", "effects": [rm(FLAG)] + copy.deepcopy(launch)},
        "effect_none": {"type": "Delayed", "tick": R_AT, "effects": launch}}]
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
        print("already done" if done else "W -> R combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: W's champion hit opens {FLAG} ({WINDOW} ticks); R cast in it launches at once")


if __name__ == "__main__":
    main()
