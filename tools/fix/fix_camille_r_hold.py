#!/usr/bin/env python3
"""league_camille R: the hold on her target ends with the arena's picture.

    python tools/fix/fix_camille_r_hold.py [--check]

The user: 「青钢影大招的框消失后酒桶还被拉在原地动不了」. The tether (`r_tether`, run every tick by a 180-tick `AddCasted`
on the target) blocked dashes and dragged the target back while `r_on` (180 ticks on Camille) lasted, but the arena on
screen is six 30-tick pieces (`r_field` at the landing, then `r_floor` from the five clocks, section "A zone's picture
comes turned by its direction" in champion-data.md): nothing tied the two together, so a picture that ended early
left the target held inside an arena nobody could see.

Now every piece keeps a 3-tick caster flag `r_vis` up while it stands: each piece hits Camille every tick (a circle of
2000000 on `AllyOnlySelf`, like `r_field_c`; a zone's shape is never drawn) and the tether holds only while `r_vis`
is there too. When the last piece ends, or a piece never comes, the hold stops within 3 ticks (3 bridges the hand-over
from one piece to the next). The landing's reset list clears `r_vis` with the others.
Idempotent: --check reports whether the file is already patched.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_camille.data_champion")
N = "league_camille_"
VIS = N + "r_vis"
VIS_TICKS = 3
PIECES = (N + "r_field", N + "r_floor")


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in list(o.values()):
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def nothing():
    return {"type": "Combine", "effects": []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    raw = open(PATH, "rb").read().decode("utf-8-sig")
    d = json.loads(raw)
    if VIS in raw:
        print("already patched")
        return
    if a.check:
        sys.exit("not patched")
    ult = d["ult"]["effect"]

    # the pieces of the picture: r_field (the arena forming) and the five r_floor (the standing arena)
    pieces = []
    walk(ult, lambda o: pieces.append(o) if o.get("type") == "RangePeriodProjectile" and o.get("name") in PIECES
         else None)
    names = sorted(p["name"] for p in pieces)
    assert names == [N + "r_field"] + [N + "r_floor"] * 5, names
    for p in pieces:
        assert (p["tick"], p["period"], p["applied_effects"]) == (30, 30, []), p["name"]
        p["shape"] = {"Circle": {"radius": 2000000}}
        p["period"] = 1
        p["applied_target"] = "AllyOnlySelf"
        p["applied_effects"] = [{"casting_type": "Targeting", "effect": {
            "type": "AddCasterBuff", "buff_state": {"name": VIS, "duration": {"Time": {"tick": VIS_TICKS}}},
            "only_to_enemy": False}}]

    # the landing's reset list (RemoveCasterBuff r_on ... r_mk before r_on is added)
    resets = []
    walk(ult, lambda o: resets.append(o) if o.get("type") == "MoveToTarget" else None)
    assert len(resets) == 1
    ends = resets[0]["end_effects"]
    at = next(i for i, e in enumerate(ends) if e == {"type": "RemoveCasterBuff", "name": N + "r_mk"})
    ends.insert(at + 1, {"type": "RemoveCasterBuff", "name": VIS})

    # the tether's hold: SwitchByBuff r_live -> SwitchByBuff r_on -> the hold
    gates = []

    def gate(o):
        if o.get("type") == "SwitchByBuff" and o.get("buff_name") == N + "r_on":
            hold = json.dumps(o["effect_buff"])
            if "BlockMoveSkill" in hold:
                gates.append(o)

    walk(ult, gate)
    assert len(gates) == 1, len(gates)
    g = gates[0]
    g["effect_buff"] = {"type": "SwitchByBuff", "buff_name": VIS, "effect_buff": g["effect_buff"],
                        "effect_none": nothing()}

    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"patched: {len(pieces)} arena pieces keep {VIS} up, the tether's hold needs it")


if __name__ == "__main__":
    main()
