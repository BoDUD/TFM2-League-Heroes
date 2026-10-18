#!/usr/bin/env python3
"""Twisted Fate's Destiny and Ryze's Realm Warp chase no longer warp into the enemy fountain (2026-10-18).

    python tools/fix/warp_beacon.py [--check]

The user: 「卡牌和流浪推水晶的时候会往泉水里传送」. Both chases send a hidden line (`<hero>_r_beacon`, a LinearProjectile
that stops on the first enemy champion) toward the champion picked, show the far portal where it stops and, at the end
of the channel, Teleport him there (the Teleport sits in the line's end_effects). A line is only tested where it stands
each tick: at 120000 a tick with a 25000 circle (Twisted Fate) it stepped over everyone 145000-215000 or 265000-335000
away, hit nothing and flew its whole 360000 - beyond the champion picked, through their nexus into the fountain,
clamped at the map's edge (classic sim, 24 games: 27 of ~75 Destinies flew the whole line, five ended within 70000 of
the enemy fountain, each time he died there within 2 s; Ryze's 50000 circle missed less, 10 of ~110).

The fix, for both:
* a step is at most the circle's width (speed = 2 x radius: Twisted Fate 50000, Ryze 100000), so no gaps;
* the line, touching an enemy champion, flags him `<hero>_r_hit` (applied_effects); only with the flag does it show
  the far portal and put him there - a line that touched nobody warps nowhere (he just ends the channel);
* the Teleport's delay is shortened by the longer flight (ceil(range / speed) ticks, was 3), so he still lands as the
  channel ends; `<hero>_r_hit` is cleared with `r_armed` / `r_cut` when a warp starts.
Ryze's kit script (tools/kit/build_ryze.py, r_step) builds the same. Idempotent: run it again and nothing changes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEROES = ("league_twistedfate", "league_ryze")
OLD_FLY = 3                      # the old line's flight: 360000 at 120000 a tick
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def path_of(hero):
    return os.path.join(ROOT, "league", "champion", hero + ".data_champion")


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in o.values():
            walk(v, fn)
    elif isinstance(o, list):
        fn(o)
        for v in o:
            walk(v, fn)


def fix(d, hero):
    hit, cut, armed = hero + "_r_hit", hero + "_r_cut", hero + "_r_armed"
    done = {"beacon": 0, "clear": 0}

    def rm(name):
        return {"type": "RemoveCasterBuff", "name": name}

    def on(o):
        if isinstance(o, list):
            # the warp's start: RemoveCasterBuff r_armed, r_cut, ... -> r_hit too, at the end of that run
            for i in range(len(o) - 1):
                if o[i] == rm(armed) and o[i + 1] == rm(cut):
                    j = i
                    while j < len(o) and isinstance(o[j], dict) and o[j].get("type") == "RemoveCasterBuff":
                        j += 1
                    if rm(hit) not in o[i:j]:
                        o.insert(j, rm(hit))
                    done["clear"] += 1
                    break
            return
        if o.get("type") != "LinearProjectile" or o.get("name") != hero + "_r_beacon":
            return
        done["beacon"] += 1
        radius = o["shape"]["Circle"]["radius"]
        step = min(o["speed"], 2 * radius)
        fly = -(-o["range"] // step)
        ends = o["end_effects"]
        teleport = [e for e in ends if e.get("type") == "Delayed"
                    and json.dumps(e).count('"Teleport"') and e["effects"][0].get("buff_name") != hit]
        if o["speed"] == step and not teleport:
            return                                                       # already fixed
        old_fly = -(-o["range"] // o["speed"])
        assert old_fly == OLD_FLY, (hero, o["speed"], o["range"])
        o["speed"] = step
        hold = None
        for e in ends:
            if e.get("type") == "Delayed" and e.get("tick", 0) > 1:
                hold = e["tick"] + OLD_FLY                               # the channel's length
                break
        assert hold, hero
        o["applied_effects"] = [{"casting_type": "Targeting", "effect": {"type": "AddCasterBuff", "buff_state": {
            "name": hit, "duration": {"Time": {"tick": hold + 2}}}, "only_to_enemy": False}}]
        pictures = [e for e in ends if e.get("type") in ("ViewEffect", "Sfx")]
        late = [e for e in ends if e.get("type") == "Delayed"]
        assert len(pictures) + len(late) == len(ends) and len(late) == 1, hero
        shown = pictures[0] if len(pictures) == 1 else {"type": "Combine", "effects": pictures}
        late[0]["tick"] = hold - fly
        late[0]["effects"] = [{"type": "SwitchByBuff", "buff_name": hit, "effect_buff": e, "effect_none": NONE}
                              for e in late[0]["effects"]]
        o["end_effects"] = [{"type": "Delayed", "tick": 1, "effects": [
            {"type": "SwitchByBuff", "buff_name": hit, "effect_buff": shown, "effect_none": NONE}]}, late[0]]

    walk(d["ult"], on)
    return done


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only say whether a file would change")
    a = ap.parse_args()
    changed = False
    for hero in HEROES:
        with open(lp(path_of(hero)), encoding="utf-8", newline="") as f:
            text = f.read()
        d = json.loads(text)
        if dumps(d) != text:
            sys.exit(f"{hero}: the file is not in the pack's JSON layout; nothing written")
        done = fix(d, hero)
        if done["beacon"] != 1 or not done["clear"]:
            sys.exit(f"{hero}: expected one r_beacon and a warp start, found {done}")
        new = dumps(d)
        print(hero, "changed" if new != text else "unchanged", done)
        if new != text:
            changed = True
            if not a.check:
                with open(lp(path_of(hero)), "w", encoding="utf-8", newline="") as f:
                    f.write(new)
    if a.check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
