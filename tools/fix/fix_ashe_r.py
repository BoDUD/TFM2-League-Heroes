"""Ashe R: the Enchanted Crystal Arrow fast enough to arrive, cast at champions near enough to be there.

The user, 2026-10-21: 「还有寒冰的大招是不是有点问题 没打中过人」. The arrow left 22 ticks into the cast at 4200 a tick
(radius 9000: no gap a champion slips through - champion-data.md, speed <= 2 x radius) at champions up to 150000
away: up to 58 ticks from the press to the hit, and the aimed champion walks off the line. Classic SDK simulation,
2026-10-21 (/c/t/on_sim trace.exe, 24 ten-minute games each, Ashe bot on three base lineups against three, both sides;
an arrow struck when league_ashe_r_hit was applied within 40 ticks of its spawn):
- as it was (4200 a tick, cast within 150000): 116 arrows, 30 struck (26 %);
- 8400 a tick: 50 %; cast within 90000: 48 %; 8400 with radius 12000: 61 %;
- 8400 a tick, cast within 100000: 109 arrows, 85 struck (78 %) - this fix.
kd.py (lane 3, seeds 1-8): her K/D/A 3.29/1.51/4.14 -> 3.31/1.80/4.21, the opponents' 2.31/1.87/2.86 -> 2.14/1.79/2.96 -
the arrow lands, she does not get stronger with it. The line still flies its 150000 (a champion stepping into it on the
way is struck).

    python tools/fix/fix_ashe_r.py <league folder>

Runs on the kit before the fix or after it.
"""
import json
import os
import sys

HERO = "league_ashe"
ARROW = "league_ashe_crystal"
SPEED = 8400                 # a tick (was 4200); radius 9000, so <= 2 x radius
CAST = 100000                # the ult's cast range (was 150000)


def arrows(o, out):
    if isinstance(o, dict):
        if o.get("type") == "LinearProjectile" and o.get("name") == ARROW:
            out.append(o)
        for v in o.values():
            arrows(v, out)
    elif isinstance(o, list):
        for v in o:
            arrows(v, out)
    return out


def main(league):
    path = os.path.join(league, "champion", HERO + ".data_champion")
    lp = chr(92) * 2 + "?" + chr(92) + os.path.abspath(path) if os.name == "nt" else path
    raw = open(lp, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    k = json.loads(raw.lstrip("﻿"))
    found = arrows(k["ult"], [])
    assert len(found) == 1, len(found)
    radius = found[0]["shape"]["Circle"]["radius"]
    assert SPEED <= 2 * radius, (SPEED, radius)
    found[0]["speed"] = SPEED
    k["ult"]["range"] = CAST
    out = json.dumps(k, ensure_ascii=False, indent=2) + "\n"
    if nl == "\r\n":
        out = out.replace("\n", "\r\n")
    open(lp, "wb").write(("﻿" if raw.startswith("﻿") else "").encode("utf-8") + out.encode("utf-8"))
    print(f"{HERO}: ult cast range {k['ult']['range']}, {ARROW} speed {found[0]['speed']} (radius {radius})")


if __name__ == "__main__":
    main(sys.argv[1])
