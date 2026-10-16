"""Lee Sin's W shields and dashes to allies only (the user, 2026-10-16: 「瞎子W会摸敌人 然后给敌人盾」).

    python tools/fix/fix_leesin_w.py <league_leesin.data_champion> [...]

W (folded into E, also checked by the attack and Q) went to an ally in a fight by two zones laid at each ally's feet by
a 1-tick lob `league_leesin_w_probe`: `league_leesin_w_contact` (an enemy champion within 25000 of him) and
`league_leesin_w_crowd` (two within 35000), whose applied effects - run on the ENEMY champion they hit - looked for the
ally again with `RandomTarget {range 3000, AllyNotSelf, from_projectile}` and shielded / dashed to what it found. The
classic SDK found the ally there (simulation: 6 of 6 W shields on allies and Lee Sin); game 0.6.4 shields the enemy and
Lee Sin dashes onto him. Now nothing looks for an ally from an enemy's effects:
  * contact: the lob onto each ally within 35000 hits that ally (`AllyNotSelf` within 3000 of where it lands) and its
    applied effects - on the ally - ask `RandomTarget {25000, EnemyChampion, from_projectile}` for a 1-tick flag
    `league_leesin_w_t`, read and taken off in the same list, then shield and dash to him;
  * crowd: the zone's second enemy only raises `league_leesin_w_go` (4 ticks) on Lee Sin; a second lob onto the same
    ally, landing 4 ticks later, reads it (and takes it off) and shields / dashes to the ally it hits.
The W effects themselves (cooldown flag, both shields, the flurry flags, the Q2 pose, the dash) are moved unchanged.
Run once; a kit already fixed is left as it is.
"""
import copy
import json
import os
import sys

ID = "league_leesin"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


NONE = {"type": "Combine", "effects": []}


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def sw(name, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": yes, "effect_none": no or copy.deepcopy(NONE)}


def lob(travel, effects):
    """A hidden 1-tick (travel) lob onto the ally's spot that hits the ally beside it (not Lee Sin)."""
    return {"type": "ParabolicProjectile", "name": n("w_probe"), "travel_time": travel, "range": 1000000,
            "range_effect_name": "", "shape": {"Circle": {"radius": 3000}}, "applied_target": "AllyNotSelf",
            "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in effects], "end_effects": []}


def zone_of(node, name):
    """The RangeProjectile `name` in a w_probe lob's end_effects, or None."""
    if not (isinstance(node, dict) and node.get("type") == "ParabolicProjectile" and node.get("name") == n("w_probe")):
        return None
    for e in node.get("end_effects", []):
        if isinstance(e, dict) and e.get("type") == "RangeProjectile" and e.get("name") == n(name):
            return e
    return None


def w_effects(zone):
    """The W effects in a zone: the effects of its RandomTarget {3000, AllyNotSelf, from_projectile}."""
    found = []

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "RandomTarget" and o.get("casting_target") == "AllyNotSelf" and o.get("from_projectile"):
                found.append(o)
                return
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(zone["applied_effects"])
    if len(found) != 1:
        raise SystemExit(f"{zone['name']}: {len(found)} ally searches, expected 1")
    return found[0]


def fix_contact(parent_list, i, zone):
    search = w_effects(zone)
    w = search["effects"]
    parent_list[i] = lob(1, [
        {"type": "RandomTarget", "range": 25000, "casting_target": "EnemyChampion", "from_projectile": True,
         "effects": [flag("w_t", 1)]},
        sw("w_t", {"type": "Combine", "effects": [rm("w_t"), sw("w_cd", copy.deepcopy(NONE),
                                                                 {"type": "Combine", "effects": w})]}),
        rm("w_t")])


def fix_crowd(parent_list, i, zone):
    search = w_effects(zone)
    w = search["effects"]
    # the zone's second enemy: only the flag (the search node replaced in place inside the zone's tree)
    search.clear()
    search.update(flag("w_go", 4))
    parent_list.insert(i + 1, lob(4, [sw("w_go", {"type": "Combine", "effects": [
        rm("w_go"), sw("w_cd", copy.deepcopy(NONE), {"type": "Combine", "effects": w})]})]))


def main():
    for path in sys.argv[1:]:
        with open(lp(path), encoding="utf-8", newline="") as f:
            raw = f.read()
        d = json.loads(raw)
        if f'"{n("w_t")}"' in raw:
            print(os.path.basename(path), "already fixed")
            continue
        counts = {"contact": 0, "crowd": 0}

        def walk(o):
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                i = 0
                while i < len(o):
                    x = o[i]
                    zc, zr = zone_of(x, "w_contact"), zone_of(x, "w_crowd")
                    if zc is not None:
                        fix_contact(o, i, zc)
                        counts["contact"] += 1
                    elif zr is not None:
                        fix_crowd(o, i, zr)
                        counts["crowd"] += 1
                        i += 1
                    else:
                        walk(x)
                    i += 1

        walk(d)
        crlf = "\r\n" in raw
        text = json.dumps(d, ensure_ascii=False, indent=2)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write((text.replace("\n", "\r\n") + "\r\n") if crlf else text + "\n")
        print(os.path.basename(path), counts)


if __name__ == "__main__":
    main()
