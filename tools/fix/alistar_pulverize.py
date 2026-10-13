#!/usr/bin/env python3
"""Alistar's Pulverize once per its cooldown, Q or W -> Q (the user, 2026-10-13: 「牛头EQ后 还能释放一次Q」「改」).

    python tools/fix/alistar_pulverize.py [--check]

His Q (E -> Q) slammed and his W carried a slam of its own on its own cooldown, so a Q and a W a moment apart threw
everyone up twice. In League W -> Q is the one Q: the slam waits for Q's cooldown. Here both slams share a caster flag,
league_alistar_pq_cd, set for q_cd ticks (600, Q's cooldown) when either slams: while it holds, Q only tramples and W
only headbutts (no landing slam, no slam animation). Edits league/champion/league_alistar.data_champion in place (the
shipped kit carries the red-side pass's changes, so it is not rebuilt from tools/kit/build_alistar.py, which has the
same gate). Idempotent; --check only says whether it is there.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT = os.path.join(ROOT, "league", "champion", "league_alistar.data_champion")
FLAG = "league_alistar_pq_cd"
TICKS = 360                      # 6 s: a W five seconds after an EQ slams again, one right after does not
# the balance that came with it (classic-SDK simulations, support lane against the five base supports, 720 games a
# batch): the gate alone took him from +0.84 to -1.61 (half the knock-ups); with these he is +0.18 / +0.17 on two batches
NUMBERS = {(8, 6): (12, 9),      # each trample stomp
           (50, 50): (80, 80),   # Q's slam
           (40, 50): (100, 110)}  # W's headbutt (its landing slam stays 30 + 30%)
TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
SHARED = {"zh-hans": "（和大地粉碎共用：6秒内只砸一次）", "zh-hant": "（與大地粉碎共用：6秒內只砸一次）",
          "en": " (shares Pulverize: one slam every 6 s)", "ja": "（大地粉砕と共有：6秒に1回）", "ko": " (분쇄와 공유: 6초에 한 번)"}


def has_airborne(o):
    if isinstance(o, dict):
        if o.get("type") == "Airborne":
            return True
        return any(has_airborne(v) for v in o.values())
    if isinstance(o, list):
        return any(has_airborne(v) for v in o)
    return False


def gate(node):
    """node (one effect) played only with the flag off, the flag set as it plays."""
    return {"type": "SwitchByBuff", "buff_name": FLAG, "effect_buff": {"type": "Combine", "effects": []},
            "effect_none": {"type": "Combine", "effects": [
                {"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": TICKS}}},
                 "only_to_enemy": False},
                node]}}


def gated(o):
    return isinstance(o, dict) and o.get("type") == "SwitchByBuff" and o.get("buff_name") == FLAG


def wrap(o):
    """Top down: the first Delayed holding the knock-up on each path wrapped (nothing under it, nothing already
    wrapped). -> how many are wrapped now."""
    n = 0
    if isinstance(o, dict):
        for key, v in o.items():
            if gated(v):
                n += 1
            elif isinstance(v, dict) and v.get("type") == "Delayed" and has_airborne(v):
                o[key] = gate(v)
                n += 1
            else:
                n += wrap(v)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if gated(v):
                n += 1
            elif isinstance(v, dict) and v.get("type") == "Delayed" and has_airborne(v):
                o[i] = gate(v)
                n += 1
            else:
                n += wrap(v)
    return n


def renumber(o):
    """ApAttack damage / ratio pairs moved to NUMBERS (only the old pairs: a second run changes nothing)."""
    n = 0
    if isinstance(o, dict):
        if o.get("type") == "ApAttack" and (o.get("damage"), o.get("attack_ratio")) in NUMBERS:
            o["damage"], o["attack_ratio"] = NUMBERS[(o["damage"], o["attack_ratio"])]
            n += 1
        for v in o.values():
            n += renumber(v)
    elif isinstance(o, list):
        for v in o:
            n += renumber(v)
    return n


def texts():
    """His Q / W tooltips: the numbers, and W's shared slam. -> how many strings changed."""
    import re
    raw = open(TEXT, "rb").read().decode("utf-8-sig")
    t = json.loads(raw)
    n = 0
    for lang, root in t.items():
        d = root.get("description", {}).get("league_alistar")
        if not d:
            continue
        for slot, pairs in (("skill", [(8, 6), (50, 50)]), ("skill2", [(40, 50)])):
            v = d.get(slot)
            if not isinstance(v, str):
                continue
            new = v
            for a, b in pairs:
                c, e = NUMBERS[(a, b)]
                new = re.sub(r"(<#[0-9a-f]+>)%d(<> \+ <i#[^>]+>(?:<#[0-9a-f]+>)?)%d%%" % (a, b),
                             lambda m, c=c, e=e: f"{m.group(1)}{c}{m.group(2)}{e}%", new, count=1)
            if slot == "skill2" and lang in SHARED and SHARED[lang] not in new:
                new += SHARED[lang]
            if new != v:
                d[slot] = new
                n += 1
    text = json.dumps(t, ensure_ascii=False, indent=2).replace(chr(10), chr(13) + chr(10)) + chr(13) + chr(10)
    with open(TEXT, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return n


def count(o):
    if gated(o):
        return 1
    if isinstance(o, dict):
        return sum(count(v) for v in o.values())
    if isinstance(o, list):
        return sum(count(v) for v in o)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    raw = open(KIT, "rb").read().decode("utf-8-sig")
    k = json.loads(raw)
    if a.check:
        nq, nw = count(k["skill"]["effect"]), count(k["skill2"]["effect"])
        print(f"gated: Q {nq}, W {nw}")
        sys.exit(0 if nq and nw else 1)
    nq = wrap(k["skill"]["effect"])
    nw = wrap(k["skill2"]["effect"])
    assert nq >= 1 and nw >= 1, (nq, nw)
    for o in [k]:
        def retime(x):
            if isinstance(x, dict):
                if x.get("type") == "AddCasterBuff" and x.get("buff_state", {}).get("name") == FLAG:
                    x["buff_state"]["duration"] = {"Time": {"tick": TICKS}}
                for v in x.values():
                    retime(v)
            elif isinstance(x, list):
                for v in x:
                    retime(v)
        retime(o)
    nn = renumber(k["skill"]) + renumber(k["skill2"])   # not the attack: its stun punch is 50 + 50% too
    print(f"numbers changed: {nn}; tooltips changed: {texts()}")
    text = json.dumps(k, ensure_ascii=False, indent=2).replace(chr(10), chr(13) + chr(10)) + chr(13) + chr(10)
    with open(KIT, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{KIT}: Q slams gated {nq}, W slams gated {nw}")


if __name__ == "__main__":
    main()
