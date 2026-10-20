#!/usr/bin/env python3
"""Keep the champion-first half of an "aim" pair out of the 0.6.x AI's damage table.

    python tools/kit/hide_aim_twins.py [--hero ahri ...] [--check]

Many kits cast like this (the slot's Combine): a `RandomTarget` on a champion near the target that sets a 1-2 tick caster
flag and fires the skill at him, then a `SwitchByBuff` on that flag whose buff branch is empty and whose none branch
fires the same skill at the slot's own target (no champion found). Only one of the two ever fires, but the AI reads the
kit between ticks - no flag set - and adds both: the estimate is twice the hit (2026-10-20, classic expected_damage:
Sivir / Akshan / Jhin exactly x2, Syndra's W x3.2). Lane AIs sum those estimates over the enemies near them and recall
on them, so these heroes scared their lanes home at full health (league_recall_log SUSPECT) as league_kogmaw's passive
did. Each such `RandomTarget` is wrapped the way league_viktor's unseen() wraps his probe: a 1-tick caster flag
`<id>_ai_hide`, a `SwitchByBuff` on it holding the RandomTarget, the flag removed - added, read and removed in one go, so
in game it fires as before and the AI never sees it (it counts the fallback once). Idempotent: a wrapped one is no
longer a bare RandomTarget beside its fallback.

The build scripts of these heroes call hide() before writing (tools/kit/build_<id>.py); the others' data files are
patched in place here. Then every add-on copy of them is regenerated (its make_override.py), and league_sylas's.
Balance after it (10-min classic-SDK simulations, 8 seeds, each lane against its five base heroes; before -> after):
Fiora +1.28 -> +0.21, Briar +1.48 -> +0.23, Twisted Fate +2.24 -> +0.97, Xerath +2.16 -> +1.20, Lissandra +1.20 -> +0.64,
Nami +1.65 -> +0.97 (the AI, seeing half the damage, engaged less); the rest moved within the noise (Garen -0.49 -> +0.02,
Diana, Evelynn, Ahri, LeBlanc, Syndra, Akshan, Ezreal, Jhin, Tristana, Varus, Xayah, Morgana, Pyke, Taric). Brought
back by attack, AP and health (base and growth): Fiora +3% (+1.71), Briar +5% (+3%: +0.40, +6%: +2.27), Nami +3%,
Twisted Fate +6% (+1.61), Xerath +6% (+1.05), Lissandra +6% (+1.15).
"""
import argparse
import copy
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(REPO, "league", "champion")
# the heroes whose aim pairs doubled a slot's estimate (x1.3 and more; hide_aim_twins --check prints them all)
HEROES = ["ahri", "akshan", "briar", "diana", "evelynn", "ezreal", "fiora", "garen", "jhin", "leblanc", "lissandra",
          "morgana", "nami", "pyke", "syndra", "taric", "tristana", "twistedfate", "varus", "xayah", "xerath"]
SLOTS = ("attack", "skill", "skill2", "ult")
# Tristana's W: its fallback is no hit at all (the leap away), nothing is counted twice there
SKIP = {("league_tristana", "skill2")}


def _flags(o, out):
    if isinstance(o, dict):
        if o.get("type") == "AddCasterBuff":
            dur = o.get("buff_state", {}).get("duration")
            if isinstance(dur, dict) and dur.get("Time", {}).get("tick", 99) <= 2:
                out.add(o["buff_state"].get("name"))
        for v in o.values():
            _flags(v, out)
    elif isinstance(o, list):
        for v in o:
            _flags(v, out)


def _wrap(node, flag):
    return {"type": "Combine", "effects": [
        {"type": "AddCasterBuff", "buff_state": {"name": flag, "duration": {"Time": {"tick": 1}}},
         "only_to_enemy": False},
        {"type": "SwitchByBuff", "buff_name": flag, "effect_buff": {"type": "Combine", "effects": [node]},
         "effect_none": {"type": "Combine", "effects": []}},
        {"type": "RemoveCasterBuff", "name": flag}]}


def _hide(o, flag):
    n = 0
    if isinstance(o, dict):
        if o.get("type") == "Combine":
            effs = o.get("effects", [])
            falls = {e.get("buff_name") for e in effs if isinstance(e, dict) and e.get("type") == "SwitchByBuff"
                     and e.get("effect_buff", {}).get("effects") == []}
            for i, e in enumerate(effs):
                if isinstance(e, dict) and e.get("type") == "RandomTarget":
                    got = set()
                    _flags(e, got)
                    if got & falls:
                        effs[i] = _wrap(e, flag)
                        n += 1
        for v in o.values():
            n += _hide(v, flag)
    elif isinstance(o, list):
        for v in o:
            n += _hide(v, flag)
    return n


def hide(kit):
    """The kit with its aim pairs' champion-first halves kept from the AI (in place; returns it)."""
    flag = f"{kit['id']}_ai_hide"
    for slot in SLOTS:
        if (kit["id"], slot) not in SKIP:
            _hide(kit[slot], flag)
    return kit


def count(kit):
    v = copy.deepcopy(kit)
    flag = f"{kit['id']}_ai_hide"
    return {s: _hide(v[s], flag) for s in SLOTS if (kit["id"], s) not in SKIP}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", nargs="*")
    ap.add_argument("--check", action="store_true", help="only print how many pairs each would wrap")
    a = ap.parse_args()
    for h in a.hero or HEROES:
        path = os.path.join(DATA, f"league_{h}.data_champion")
        raw = io.open(path, encoding="utf-8-sig", newline="").read()
        kit = json.loads(raw)
        if a.check:
            print(h, count(kit))
            continue
        before = count(kit)
        hide(kit)
        text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
        io.open(path, "w", encoding="utf-8", newline="").write(text)
        print(h, {k: v for k, v in before.items() if v})


if __name__ == "__main__":
    main()
