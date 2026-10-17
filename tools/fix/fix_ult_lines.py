"""Jinx R and Ezreal R: lines short enough to stay on the map, so they fly where they were aimed.

The engine sends a `LinearProjectile` from 5000 north of the caster to its goal, his pivot + the cast direction x
`range`, and cuts that goal into the 960000 x 960000 map one coordinate at a time; the spawn event's `dir` is the cut
goal minus the start. With `range` 1000000 (more than the map) nearly every goal fell off the map, so the lines turned
toward an edge or a corner (959999 x 0) and missed. SDK simulation, 2026-10-10, 240 logged games each (the ult
action's aimed direction against the line it spawned; hits against the logged enemy positions):
- league_jinx R (cast on champions anywhere): 1336 rockets turned 7.5 degrees in the median, 23 at the 90th
  percentile, up to 45; 56% struck an enemy champion, 23% the one aimed at.
- league_ezreal R (cast within 120000): 1280 waves turned 8.9 / 27 / 56 degrees; 24% struck an enemy champion, 11%
  the one aimed at.
Now Jinx fires at champions within JINX_CAST and the rocket flies JINX_LINE; Ezreal's two waves fly EZREAL_LINE (cast
range unchanged). A line is then cut only when the caster stands near an edge (one cast in seven).

Jinx's blast used to be the rocket's end effects, so it went off where the rocket stopped even when it struck nobody:
harmless on the map's edge, but at 300000 that is in the middle of the fight, and League's rocket explodes only on a
champion. A flag set by the hit and read by the end effects would do it, but the enemy AI then stops dodging the
rocket: it judges a projectile by the branch the caster's buffs pick while it flies, which holds no damage (SDK: the
aimed champion stepped 4000-4400 off the line instead of 15700, 80% of the rockets struck). So the blast now starts
from the hit itself - a `Delayed` 1 hidden lob (`travel_time` 1, league_brand's passive) onto the champion struck,
carrying the old end effects - and the rocket's own end does nothing: in the SDK one blast per champion struck, a
tick after the hit, none for a miss, the rocket dodged as before. The blast's damage lands a tick later than it did,
so Get Excited's kill check waits 2 ticks longer (flag 10 -> 12 ticks, the target's clearing effect from tick 2 -> 4,
the check at 7 -> 9): 56 of 58 rocket kills rewarded in 240 games (the other two died 7-8 ticks after the hit,
later than the blast).

    python tools/fix/fix_ult_lines.py <league folder>

Runs on the kit before the fix or after it.
"""
import json
import os
import sys

JINX_CAST, JINX_LINE = 250000, 300000
EZREAL_LINE = 300000
LOB = "league_jinx_r_drop"
KC_FLAG, KC_CLEAR, KC_CHECK = 12, 4, 9      # were 10, 2, 7
# hero: (line names, line range, cast range or None to keep it, blast from the hit)
LINES = {"league_jinx": (["league_jinx_r_rocket"], JINX_LINE, JINX_CAST, True),
         "league_ezreal": (["league_ezreal_r_wave", "league_ezreal_r_champ"], EZREAL_LINE, None, False)}


def lines(o, names, out):
    if isinstance(o, dict):
        if o.get("type") == "LinearProjectile" and o.get("name") in names:
            out.append(o)
        for v in o.values():
            lines(v, names, out)
    elif isinstance(o, list):
        for v in o:
            lines(v, names, out)
    return out


def retime_kill_check(o):
    if isinstance(o, dict):
        if o.get("type") == "AddCasterBuff" and o["buff_state"]["name"] == "league_jinx_kc_r":
            o["buff_state"]["duration"]["Time"]["tick"] = KC_FLAG
        if o.get("type") == "Delayed" and any(e.get("type") == "AddCasted" for e in o["effects"]):
            o["tick"] = KC_CLEAR
        if o.get("type") == "Delayed" and any(e.get("type") == "SwitchByBuff" and e.get("buff_name") == "league_jinx_kc_r"
                                              for e in o["effects"]):
            o["tick"] = KC_CHECK
        for v in o.values():
            retime_kill_check(v)
    elif isinstance(o, list):
        for v in o:
            retime_kill_check(v)


def blast_from_hit(rocket):
    """Move the blast from the rocket's end effects to a hidden lob onto the champion it struck."""
    first = rocket["applied_effects"][0]["effect"]
    if first.get("type") == "Delayed" and first["effects"][0].get("name") == LOB:
        return False
    ends = rocket["end_effects"]
    assert [e["type"] for e in ends] == ["ViewEffect", "RangeProjectile"], [e["type"] for e in ends]
    lob = {"type": "ParabolicProjectile", "name": LOB, "travel_time": 1, "range": 400000,
           "shape": {"Circle": {"radius": 1000}}, "range_effect_name": "", "applied_target": "EnemyWithoutTower",
           "applied_effects": [], "end_effects": ends}
    rocket["applied_effects"].insert(0, {"casting_type": "Targeting",
                                         "effect": {"type": "Delayed", "tick": 1, "effects": [lob]}})
    rocket["end_effects"] = []
    retime_kill_check(rocket["applied_effects"])
    return True


def main(league):
    for hero, (names, length, cast, from_hit) in LINES.items():
        path = os.path.join(league, "champion", hero + ".data_champion")
        lp = chr(92) * 2 + "?" + chr(92) + os.path.abspath(path)
        raw = open(lp, "rb").read().decode("utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        k = json.loads(raw)
        found = lines(k["ult"], names, [])
        assert sorted(o["name"] for o in found) == sorted(names), [o["name"] for o in found]
        for o in found:
            o["range"] = length
        if cast is not None:
            k["ult"]["range"] = cast
        moved = ""
        if from_hit:
            moved = ", blast from the hit" + ("" if blast_from_hit(found[0]) else " (already)")
        out = json.dumps(k, ensure_ascii=False, indent=2) + "\n"
        if nl == "\r\n":
            out = out.replace("\n", "\r\n")
        open(lp, "wb").write(out.encode("utf-8"))
        print(f"{hero}: ult cast range {k['ult']['range']}, "
              + ", ".join(f"{o['name']} {o['range']}" for o in found) + moved)


if __name__ == "__main__":
    main(sys.argv[1])
