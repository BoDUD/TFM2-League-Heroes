#!/usr/bin/env python3
"""league_fiora R: when the challenged champion dies, the Victory Zone opens where he died, not under Fiora.

    python tools/fix/fix_fiora_r_deathzone.py [--check]

The user: 「剑姬的回血阵会乱放位置？」, then 「修剑姬的治疗区落点，落在被挑战的人死的地方」. The data cannot read a dead
unit's spot, so the death watch (a check on Fiora every 60 ticks: the 20-tick Vital marks on the challenged champion no
longer reach her) lobbed the zone onto her own feet. In 6 classic-SDK games 10 of 18 zones came from that watch,
21000-83000 from where he died and up to 6 s late; the fourth Vital's zone landed under him (~1000). A fourth Vital
that killed him opened no zone at all: its `r_won` flag is set by a Delayed queued on the struck champion.

Now the 2-tick poll that already rides on the challenged champion (tools/fix/fix_fiora_r_zone.py: an `AddCasted` from
the ult slot's RandomTarget and from the armed attack's champion twin) also keeps a dead man's switch:
  * every poll refreshes the caster flag `r_seen` (SEEN ticks); while R is on with a Vital struck (`r_on`, `r_struck`)
    it refreshes `r_owed` (OWED ticks) - a zone is owed if he dies now - and so does every Vital strike itself (a Vital
    that kills him leaves no poll after it);
  * at most every EVERY ticks (`r_dm`) it lobs an invisible marker (`league_fiora_r_last`) onto his feet that lands FLY
    ticks later (it lands FLY - 1 ticks after it shows up: the last marker may be thrown 2 ticks before the last poll,
    so FLY - 1 must pass that poll's SEEN - 1 visible ticks). While he lives the next polls keep `r_seen` up and the
    marker lands on nothing; when he dies the poll stops with him, `r_seen` runs out, and the last marker - thrown a few
    ticks before his death - lands where he stood: with `r_owed` up it opens the zone there (R's cleanup, the heal
    sound, the heal zone and its picture);
  * the poll lasts EXTRA ticks past R so that R's natural end (no more `r_owed`) is not taken for a death;
  * the fourth Vital's own zone (`r_won`) clears `r_owed`, so a death right after it opens no second zone.
The death watch is removed. Idempotent; --check reports whether the file is already patched.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_fiora.data_champion")
N = "league_fiora_"
SEEN, OWED, EVERY, FLY, EXTRA = 4, 10, 4, 8, 20
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": N + name, "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": N + x} for x in names]


def sw(name, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": N + name, "effect_buff": yes, "effect_none": no or copy.deepcopy(NONE)}


def walk(o, fn, parent=None):
    if isinstance(o, dict):
        fn(o, parent)
        for v in list(o.values()):
            walk(v, fn, o)
    elif isinstance(o, list):
        for v in list(o):
            walk(v, fn, o)


def is_poll(o):
    return (o.get("type") == "AddCasted" and o.get("period") == 2
            and N + "r_won" in json.dumps(o.get("effects", [])))


def is_death_watch(o):
    """The RangeEffect on Fiora whose children are the 60-tick checks of r_alive that lob the zone onto her."""
    if o.get("type") != "RangeEffect" or o.get("target") != "AllyOnlySelf":
        return False
    kids = o.get("effects", [])
    return bool(kids) and all(k.get("type") == "Delayed" and k.get("effects")
                              and k["effects"][0].get("type") == "SwitchByBuff"
                              and k["effects"][0].get("buff_name") == N + "r_alive"
                              and N + "r_lob" in json.dumps(k) for k in kids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    raw = open(lp(PATH), "rb").read().decode("utf-8-sig")
    if N + "r_last" in raw:
        print("already patched")
        return
    if a.check:
        sys.exit("not patched")
    d = json.loads(raw)

    polls, watches = [], []

    def find(o, parent):
        if is_poll(o):
            polls.append(o)
        elif is_death_watch(o):
            watches.append((o, parent))

    for slot in ("attack", "ult"):
        walk(d[slot]["effect"], find)
    assert len(polls) == 2, f"expected the two zone polls (ult, armed attack), found {len(polls)}"
    assert len(watches) == 2, f"expected the two death watches (ult, armed attack), found {len(watches)}"

    for poll in polls:
        won = next(e for e in poll["effects"] if e.get("type") == "SwitchByBuff" and e.get("buff_name") == N + "r_won")
        lob = next(e for e in won["effect_buff"]["effects"] if e.get("type") == "ParabolicProjectile")
        heal, picture = lob["end_effects"][0], lob["end_effects"][1]
        assert heal.get("type") == "RangePeriodProjectile" and picture.get("type") == "ViewEffect", lob["end_effects"]
        # the fourth Vital's zone pays what is owed: no second zone if he dies just after it
        won["effect_buff"]["effects"][:0] = rm("r_owed")
        zone = {"type": "Combine", "effects": [
            *rm("r_owed", "r_on", "r_struck", "r_v1", "r_v2", "r_v3", "r_v4", "v_cd"), flag("v_cd", 180),
            {"type": "Sfx", "name": N + "r_heal"}, copy.deepcopy(heal), copy.deepcopy(picture)]}
        marker = copy.deepcopy(lob)
        marker.update({"name": N + "r_last", "travel_time": FLY, "end_effects": [sw("r_owed", sw("r_seen", NONE, zone))]})
        poll["effects"] += [
            *rm("r_seen"), flag("r_seen", SEEN),
            sw("r_on", sw("r_struck", {"type": "Combine", "effects": [*rm("r_owed"), flag("r_owed", OWED)]})),
            sw("r_dm", NONE, {"type": "Combine", "effects": [flag("r_dm", EVERY), marker]}),
        ]
        poll["duration"] = poll["duration"] + EXTRA

    for watch, parent in watches:
        parent.remove(watch)

    # every Vital strike (r_struck goes up) owes the zone at once: a Vital that kills him leaves no poll after it
    strikes = []

    def find_strikes(o, parent):
        if isinstance(parent, list) and o.get("type") == "AddCasterBuff" and o["buff_state"]["name"] == N + "r_struck":
            strikes.append((o, parent))

    for slot in ("attack", "skill", "skill2", "ult"):
        walk(d[slot]["effect"], find_strikes)
    assert strikes, "no Vital strikes found"
    for o, parent in strikes:
        i = next(j for j, x in enumerate(parent) if x is o)
        parent[i + 1:i + 1] = [*rm("r_owed"), flag("r_owed", OWED)]

    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(PATH), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"patched: 2 polls (+ dead man's switch, {EXTRA} ticks longer), 2 death watches removed, "
          f"{len(strikes)} Vital strikes owe the zone")


if __name__ == "__main__":
    main()
