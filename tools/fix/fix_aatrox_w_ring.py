#!/usr/bin/env python3
"""Aatrox's W ring on the ground whatever the chain hits first.

    python tools/fix/fix_aatrox_w_ring.py [--check]

Infernal Chains played its ground ring (league_aatrox_w_ring, and the snap 1.5 s later) only when the chain's first
hit was an enemy champion - the tether, as League's ties only champions and large monsters. But the chain stops on the
first enemy and lanes are full of minions: in four simulated games W hit 57 times and a champion once, so the ring was
almost never seen (the user, 2026-10-05: 「剑魔的w应该是释放了地面上就有的吧 ... 现在释放了会地面上没有」; of the
offered fixes the user picked the ring on every hit). Now a hit on any enemy adds a 30-tick caster flag w_any next to
the champion flag, and the chain's end_effects play the ring, its sound and the snap for either flag; only a champion is
pulled back (that stays in the applied effects). A chain that hits nothing plays no ring. Both flags are cleared when
W is cast and when the ring plays. Run once; --check only verifies.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_aatrox.data_champion")
P = "league_aatrox_"
ANY = P + "w_any"
CHAMP = P + "w_champ"


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None


def build(k):
    w = k["skill2"]["effect"]
    chain = find(w, lambda o: o.get("type") == "LinearProjectile" and o.get("name") == P + "w_chain")
    # the flag on every hit (the applied effects run on the unit hit; AddCasterBuff puts it on Aatrox)
    chain["applied_effects"].insert(0, {"casting_type": "Targeting", "effect": {
        "type": "AddCasterBuff", "buff_state": {"name": ANY, "duration": {"Time": {"tick": 30}}},
        "only_to_enemy": False}})
    # cleared with the champion flag when W is cast
    first = w["effects"]
    i = next(n for n, e in enumerate(first) if e == {"type": "RemoveCasterBuff", "name": CHAMP})
    first.insert(i + 1, {"type": "RemoveCasterBuff", "name": ANY})
    # end_effects: the champion branch as it was (and it clears w_any); otherwise the ring for any hit
    sw = chain["end_effects"][0]["effects"][0]
    assert sw["type"] == "SwitchByBuff" and sw["buff_name"] == CHAMP and sw["effect_none"] == {"type": "Combine", "effects": []}
    ring = sw["effect_buff"]["effects"]
    assert ring[0] == {"type": "RemoveCasterBuff", "name": CHAMP}
    ring.insert(1, {"type": "RemoveCasterBuff", "name": ANY})
    sw["effect_none"] = {"type": "SwitchByBuff", "buff_name": ANY,
                         "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": ANY}] +
                                         json.loads(json.dumps(ring[2:]))},
                         "effect_none": {"type": "Combine", "effects": []}}
    return k


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    k = json.loads(raw)
    done = ANY in raw
    if args.check:
        print("league_aatrox.data_champion:", "W ring on every hit" if done else "W ring on champions only")
        sys.exit(0 if done else 1)
    if done:
        sys.exit("league_aatrox.data_champion already plays the W ring on every hit")
    out = json.dumps(build(k), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_aatrox.data_champion: W's ring on every hit")


if __name__ == "__main__":
    main()
