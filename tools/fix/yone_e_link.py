#!/usr/bin/env python3
"""Yone's Soul Unbound draws a straight tether from the body he leaves behind to him while his spirit walks (the
user, 2026-10-11: 「另外永恩的E帮我加个连接线特效」, then 「你这个线弄直啊」).

    python tools/fix/yone_e_link.py            # (re)writes the links into league/champion/league_yone.data_champion
    python tools/fix/yone_e_link.py --check    # only verifies they are there and current

The body is the end of his anchor (league_yone_e_anchor, a LinearProjectile of range 1 that ends where he cast).
Only a BackToCasterLinearProjectile started in a projectile's end_effects - also behind a Delayed there - leaves from
that point (champion-data "Leave the body", league_ekko Q), and it flies back to him wherever he walked (a zone on
the body reaching him every few ticks spawns none: SDK, 2026-10-11). So the anchor's end_effects send one
(league_yone_e_link: 15000 a tick, range 300000, no radius, no effects) every 2 ticks from the first tick until
the return (tick 239): 120 links, 30000 apart, each drawn 40 px behind its head and 15 px ahead (tools/art/
yone_e_link.py: why so fast and so many - slower or sparser links bend after him); each is removed when it reaches
him. The first version (2000 a tick every 16 ticks, 40 px links) bent after him and stepped where the links met
(「你这个线弄直啊」). Cost: skill2 660 -> 1175 nodes; 4 games of 600 s with one Yone ran about 10% longer in the
SDK (60 links: about 3%).
In the game a dead caster's Delayed effects run and fire projectiles (champion-data "A dead caster"), so the links go
in four groups of 64 ticks, each behind the guard league_ekko R's rewind uses in the same place: RandomTarget
AllyOnlySelf (range 1) adds a 1-tick league_yone_e_lives, SwitchByBuff reads it (the links carry nothing a unit
reacts to, so its effect_none stays empty), RemoveCasterBuff takes it off. A dead Yone sends at most the rest of a
group (under a second). Written once per group, not per link (docs/perf.md: skill2 is copied every tick).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PATH = os.path.join(ROOT, "league", "champion", "league_yone.data_champion")
P = "league_yone_"
ANCHOR = P + "e_anchor"
LINK = P + "e_link"
LIVES = P + "e_lives"
SPEED, RANGE = 15000, 300000
PERIOD, GROUP, LAST = 2, 64, 239                  # a link every 2 ticks, a guard every 64, none from the return on
VIEW = {"type": "Animated", "name": LINK, "anim": "asset/league/effects/league_yone_link", "tag": "e_link",
        "repeat": False, "z": 1}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def one_link():
    return {"type": "BackToCasterLinearProjectile", "name": LINK, "speed": SPEED, "range": RANGE, "penetrate": True,
            "shape": {"Circle": {"radius": 0}}, "applied_target": "AllyOnlySelf", "applied_effects": [],
            "end_effects": []}


def group(start):
    links = []
    for t in range(start, min(start + GROUP, LAST), PERIOD):
        links.append(one_link() if t == start else {"type": "Delayed", "tick": t - start, "effects": [one_link()]})
    body = [
        {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
         "effects": [{"type": "AddCasterBuff", "buff_state": {"name": LIVES, "duration": {"Time": {"tick": 1}}},
                      "only_to_enemy": False}]},
        {"type": "SwitchByBuff", "buff_name": LIVES, "effect_buff": {"type": "Combine", "effects": links},
         "effect_none": {"type": "Combine", "effects": []}},
        {"type": "RemoveCasterBuff", "name": LIVES},
    ]
    return body if start == 0 else [{"type": "Delayed", "tick": start, "effects": body}]


def links():
    out = []
    for start in range(0, LAST, GROUP):
        out += group(start)
    return out


def is_ours(e):
    text = json.dumps(e)
    return LINK in text or LIVES in text


def find_anchor(o):
    if isinstance(o, dict):
        if o.get("type") == "LinearProjectile" and o.get("name") == ANCHOR:
            return o
        for v in o.values():
            r = find_anchor(v)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_anchor(v)
            if r is not None:
                return r
    return None


def nodes(o):
    if isinstance(o, dict):
        return 1 + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    with open(lp(PATH), encoding="utf-8", newline="") as f:
        raw = f.read()
    d = json.loads(raw.lstrip("﻿"))
    before = nodes(d["skill2"])
    anchor = find_anchor(d["skill2"])
    if anchor is None:
        sys.exit(f"{ANCHOR} not found in skill2")
    kept = [e for e in anchor["end_effects"] if not is_ours(e)]
    if LIVES in json.dumps(d["skill2"]).replace(json.dumps(anchor["end_effects"]), ""):
        sys.exit(f"{LIVES} is used outside the links: rename it")
    anchor["end_effects"] = kept + links()
    views = [v for v in d["view_projectiles"] if v.get("name") != LINK] + [VIEW]
    d["view_projectiles"] = views
    out = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    if raw.startswith("﻿"):
        out = "﻿" + out
    n = sum(json.dumps(e).count('"' + LINK + '"') for e in anchor["end_effects"])
    if args.check:
        print("current" if out == raw else "out of date: run without --check", f"({n} links)")
        sys.exit(0 if out == raw else 1)
    with open(lp(PATH), "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print(f"{n} links in {ANCHOR}'s end_effects; skill2 {before} -> {nodes(d['skill2'])} nodes")


if __name__ == "__main__":
    main()
