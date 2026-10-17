#!/usr/bin/env python3
"""Yasuo's Q3 whirlwind stands upright whichever way it flies.

    python tools/fix/fix_yasuo_q3_stamps.py [--check]

A projectile's picture is turned to its flight (SDK 0.5.1 game_view: a data `Animated` projectile view is built
with its turn on and no spin; `Sprite` and `ThreePhase` turn too), so Codex's upright funnel flew upside down to the
left - the red side, mostly - and lay on its side flying up or down. A `ViewEffect` on a point is never turned (its
view is built with `is_rot` off). The user kept the funnel (「亚索的旋风特效还是用这个 右边的话你想办法处理一下」,
2026-10-05), so the whirlwind flies without a picture and the funnel is stamped where it is:
- the whirlwind (`league_yasuo_q3_tornado`) loses its `view_projectiles` entry and keeps everything else;
- next to it, in the same `Delayed`, hidden projectiles `league_yasuo_q3_step` fly its path at its speed, no
  radius, no effects, one stopping where the whirlwind is on every odd tick of its flight (1, 3, ... 31);
- each one's `end_effects` play `league_yasuo_q3_tornado_<i>` on its stop point: the loop's frame showing at that
  tick (6 frames of 60 ms) alone, held 34 ms (league_yasuo_big tornado_<i>, tools/art/import_yasuo.py), so each
  stamp covers its 2 ticks and the funnel moves in steps of 5000 (5 px) 30 times a second.
Where a `LinearProjectile` is on a tick (SDK simulation, 2026-10-05: hidden projectiles of every range from 1 to
80000 at speed 2500, each playing a `ViewEffect` where it stopped): it stops on the first tick its travel reaches its
range and plays its `end_effects` there, on its range exactly; its travel is speed x (tick + 1) from the third tick on
(range 2500 stopped on tick 1, 5000 on 2, 7500 and 10000 on 3, 12500 on 4, then 2500 x m on tick m - 1, the
whirlwind's 80000 on 31). So the stamp for tick t has range speed x (t + 1), the first (tick 1) speed.
Run once; --check only verifies.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_yasuo.data_champion")
FANIM = os.path.join(ROOT, "league", "effects", "league_yasuo_big#anim.fanim")
P = "league_yasuo_"
WIND = P + "q3_tornado"
STEP = P + "q3_step"
STAMP = P + "q3_tornado_"
EVERY = 2                    # ticks between stamps
FIRST = 1                    # the first stamp's tick of the flight
TICK_MS = 1000.0 / 60


def reach(speed, tick):
    """The range a projectile at `speed` has covered when it stops on `tick` (module docstring)."""
    return speed * (tick + 1) if tick >= 3 else speed * tick


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


def frame_at(ms, durations):
    """The loop's frame showing `ms` after it started."""
    t = ms % sum(durations)
    for i, d in enumerate(durations):
        if t < d:
            return i
        t -= d
    return len(durations) - 1


def stamps(wind, durations):
    out = []
    tick = FIRST
    while reach(wind["speed"], tick) <= wind["range"]:
        out.append({"type": "LinearProjectile", "name": STEP, "speed": wind["speed"],
                    "range": reach(wind["speed"], tick),
                    "shape": {"Circle": {"radius": 0}}, "penetrate": True, "y_offset": wind["y_offset"],
                    "applied_target": "EnemyChampion", "applied_effects": [],
                    "end_effects": [{"type": "ViewEffect", "name": STAMP + str(frame_at(tick * TICK_MS, durations))}]})
        tick += EVERY
    return out


def build(k, durations):
    throw = find(k["skill"]["effect"], lambda o: o.get("type") == "Delayed" and any(
        x.get("name") == WIND for x in o.get("effects", [])))
    wind = throw["effects"][0]
    assert wind["type"] == "LinearProjectile" and wind["name"] == WIND
    throw["effects"].extend(stamps(wind, durations))
    view = [v for v in k["view_projectiles"] if v["name"] == WIND]
    assert len(view) == 1 and view[0]["tag"] == "tornado"
    k["view_projectiles"].remove(view[0])
    for i in range(len(durations)):
        k["view_effects"].append({"type": "Animation", "name": STAMP + str(i), "anim": view[0]["anim"],
                                  "tag": "tornado_" + str(i), "z": view[0]["z"]})
    return k


def done(k):
    return STEP in json.dumps(k)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    k = json.loads(raw)
    if args.check:
        ok = done(k)
        print("league_yasuo.data_champion:", "Q3 stamped" if ok else "Q3 NOT stamped")
        sys.exit(0 if ok else 1)
    if done(k):
        sys.exit("league_yasuo.data_champion already stamps Q3")
    fanim = json.load(open(lp(FANIM), encoding="utf-8"))["anims"]
    durations = [f["duration"] * 1000 for f in fanim["tornado"]["frames"]]
    assert all("tornado_%d" % i in fanim for i in range(len(durations))), "run tools/art/import_yasuo.py first"
    out = json.dumps(build(k, durations), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_yasuo.data_champion: Q3's funnel stamped every %d ticks" % EVERY)


if __name__ == "__main__":
    main()
