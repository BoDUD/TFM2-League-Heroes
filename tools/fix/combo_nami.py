#!/usr/bin/env python3
"""Nami's League combo Q -> R: Tidal Wave rolls at once onto the champion Aqua Prison holds in the air.

    python tools/fix/combo_nami.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Nami traps a champion in the bubble and sends the wave straight at it
while it floats (the bubble's 1.25 s is longer than the wave's flight), so the wave cannot miss. Before this Q and R
were independent: R always stood through its 17-tick wind-up (start_timing 17) and rolled toward whatever enemy
champion the AI aimed at, bubbled or not.

Design (pure data, the slot plays it: league_mordekaiser's e_combo / league_leona's E -> Q window):
  * Q (skill2): beside each landing's zone (`league_nami_q_zone`, both the aimed and the fallback bubble) a
    champion-only twin (`league_nami_q_champ`, the same 22000 circle and tick, no picture, no damage) renews the caster
    flag `league_nami_q_combo` for WINDOW ticks (the bubble's knock-up) when the bubble traps a champion.
  * R (ult) now starts at tick 1 and branches on that flag: inside the window it releases at once (the cast sound,
    `r_near`, the wave and the allies' tide - R's own effects, unchanged) aimed at an enemy champion in crowd control
    within R's range (`RandomTarget EnemyChampionInCC` with a 1-tick `league_nami_r_aim`, league_morgana Q's aim: the
    bubbled one), else along the cast's direction; outside the window R's original effects wait in a `Delayed`
    R_AT - 1, i.e. release on tick R_AT exactly as before. The window is not consumed (R's 50 s cooldown allows one R
    in it).
Why it is safe: no damage, knock-up, slow or cooldown changes; every branch rolls the wave (the AI never casts a
no-op, and with the 1-tick flags off between ticks it reads the same wave as before); the flags have no `view_buffs`
entry (invisible) and timers, and death clears them. Q (skill2) grows from 20 to 28 nodes; R (13 nodes, the ult is not
copied every tick) to 45. Nami has no add-on copy (no addons/league_nami*) and no kit generator.
Idempotent: R's tree and the twins are rebuilt from the original on every run, so a second run writes the same bytes;
--check exits 1 when the file differs from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_nami.data_champion")
N = "league_nami_"
FLAG = N + "q_combo"
AIM = N + "r_aim"
TWIN = N + "q_champ"
WINDOW = 75   # ticks from the bubble's landing on a champion: its Airborne 75
R_AT = 17     # R's original start_timing: the release tick outside the window


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def copy(x):
    return json.loads(json.dumps(x))


def ours(entry):
    text = json.dumps(entry)
    return FLAG in text or AIM in text


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def wave_of(r):
    """R's original effects, from the kit (start_timing R_AT) or from this script's branch."""
    if r["start_timing"] == R_AT:
        effects = r["effect"]["effects"]
        assert not any(ours(e) for e in effects), "a combo flag in R's original tree"
        return effects
    effects = r["effect"]["effects"]
    assert r["start_timing"] == 1 and len(effects) == 1 and effects[0]["type"] == "SwitchByBuff", "unknown R tree"
    wait = effects[0]["effect_none"]
    assert effects[0]["buff_name"] == FLAG and wait["type"] == "Delayed" and wait["tick"] == R_AT - 1, "unknown R tree"
    return wait["effects"]


def fast(original, reach):
    """The release at once: the sound and r_near as before, the wave and the tide toward a champion in CC if any."""
    kinds = [e["type"] for e in original]
    assert kinds == ["Sfx", "AddCasterBuff", "LinearProjectile", "LinearProjectile"], kinds
    head, rolls = original[:2], original[2:]
    return {"type": "Combine", "effects": copy(head) + [
        rm(AIM),
        {"type": "RandomTarget", "range": reach, "casting_target": "EnemyChampionInCC", "from_projectile": False,
         "effects": [flag(AIM, 1)] + copy(rolls)},
        {"type": "SwitchByBuff", "buff_name": AIM, "effect_buff": {"type": "Combine", "effects": []},
         "effect_none": {"type": "Combine", "effects": copy(rolls)}},
        rm(AIM)]}


def twin_of(zone):
    return {"type": "RangeProjectile", "name": TWIN, "shape": copy(zone["shape"]), "delay": zone["delay"],
            "apply": zone["apply"], "applied_target": "EnemyChampion",
            "applied_effects": [{"casting_type": "Targeting",
                                 "effect": {"type": "Combine", "effects": [rm(FLAG), flag(FLAG, WINDOW)]}}]}


def add_twins(node, found):
    """Next to every bubble landing's zone, its champion-only twin (rebuilt: an old twin is dropped first)."""
    if isinstance(node, list):
        for x in node:
            add_twins(x, found)
        return
    if not isinstance(node, dict):
        return
    if node.get("type") == "ParabolicProjectile" and node.get("name") == N + "q_bubble":
        ends = [e for e in node["end_effects"] if e.get("name") != TWIN]
        zones = [i for i, e in enumerate(ends) if e.get("type") == "RangeProjectile" and e.get("name") == N + "q_zone"]
        assert len(zones) == 1, "a bubble without its zone"
        ends.insert(zones[0] + 1, twin_of(ends[zones[0]]))
        node["end_effects"] = ends
        found.append(node)
        return
    for v in node.values():
        add_twins(v, found)


def apply(d):
    r = d["ult"]
    original = copy(wave_of(r))
    r["start_timing"] = 1
    r["effect"] = {"type": "Combine", "effects": [
        {"type": "SwitchByBuff", "buff_name": FLAG,
         "effect_buff": fast(original, r["range"]),
         "effect_none": {"type": "Delayed", "tick": R_AT - 1, "effects": original}}]}

    found = []
    add_twins(d["skill2"]["effect"], found)
    assert len(found) == 2, f"expected the aimed and the fallback bubble, found {len(found)}"
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
        print("already done" if done else "Q -> R combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: a bubble trapping a champion opens {FLAG} ({WINDOW} ticks); R cast in it rolls at once "
          f"toward a champion in CC (otherwise on tick {R_AT} as before)")


if __name__ == "__main__":
    main()
