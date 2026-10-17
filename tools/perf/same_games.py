#!/usr/bin/env python3
"""Do two versions of a kit play the same games? Same seeds, every tick's events compared (tools/perf/trace.rs).

    python same_games.py hero <before.data_champion> <after.data_champion> [--lane 2] [--seeds 2] [--native]
    python same_games.py all <before dir> <after dir> [--seeds 3] [--shuffles 3]

Run from the folder that holds sim/ (sim/trace.exe built from tools/perf/trace.rs with the classic SDK's build.sh,
sim/assets/), like kd.py. `hero`: kd.py's games - the kit in --lane against each base opponent of that lane, three
lineups, both sides - once with each version. `all`: every <hero>.data_champion of the two folders dealt into
all-league 10-hero games (--shuffles deals). The after version is compared as tools/package_mod.py ships it
(tools/kit/slim.py applied) unless --as-is. --native: the kits are add-on copies - every Native effect becomes an
empty Combine in both (the classic simulator runs no add-on code). Two runs match when every tick's sorted event hash
is equal; TRACE_HIDE=<prefix>,... (passed to trace.exe) leaves hidden flags out of the buff lists, for versions that
name or time their caster flags differently. Prints each game that differs with its first differing tick
(TRACE_DUMP=<t>-<t> then shows both games' events there), then how many matched.
"""
import argparse
import concurrent.futures as cf
import json
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import slim  # noqa: E402

LINEUPS = [
    ["base:fighter", "base:ninja", "base:pyromancer", "base:archer", "base:priest"],
    ["base:knight", "base:demon", "base:lightning_mage", "base:gunner", "base:monk"],
    ["base:executioner", "base:hunter", "base:ice_mage", "base:boomerang_hunter", "base:bard"],
]
OPP = {0: "fighter,executioner,knight,berserker,lancer,pole_warrior", 1: "ninja,demon,hunter,werewolf,vampire",
       2: "pyromancer,ice_mage,lightning_mage,wind_mage,white_mage",
       3: "archer,gunner,boomerang_hunter,poison_dart_hunter", 4: "priest,monk,bard,enchanter,taoist"}
BASE10 = LINEUPS[0] + LINEUPS[1]


def denative(x):
    if isinstance(x, dict):
        if x.get("type") == "Native":
            return {"type": "Combine", "effects": []}
        return {k: denative(v) for k, v in x.items()}
    if isinstance(x, list):
        return [denative(v) for v in x]
    return x


def stage(src, dst, native, ship):
    d = slim._load(src)
    if native:
        d = denative(d)
    if ship:
        d = slim.slim_champion(d)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    return dst


def trace(secs, seed, files):
    out = subprocess.run([os.path.join("sim", "trace.exe"), str(secs), str(seed)] + files,
                         capture_output=True, text=True).stdout
    return {int(p[1]): (p[2], p[4]) for p in (line.split() for line in out.splitlines() if line.startswith("T "))}


def compare(job):
    secs, seed, fa, fb = job
    ta, tb = trace(secs, seed, fa), trace(secs, seed, fb)
    if not ta or not tb:
        return "no output"
    for t in sorted(set(ta) | set(tb)):
        if ta.get(t) != tb.get(t):
            return t
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=("hero", "all"))
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--lane", type=int, default=2)
    ap.add_argument("--opp")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--secs", type=int, default=600)
    ap.add_argument("--shuffles", type=int, default=1)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--native", action="store_true")
    ap.add_argument("--as-is", action="store_true", help="compare the after version as it is, not as shipped")
    x = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="same_")
    jobs, names = [], []
    if x.mode == "hero":
        fa = stage(x.a, os.path.join(tmp, "a.data_champion"), x.native, False)
        fb = stage(x.b, os.path.join(tmp, "b.data_champion"), x.native, not x.as_is)
        for o in (x.opp or OPP[x.lane]).split(","):
            for li, lineup in enumerate(LINEUPS):
                for side in (0, 1):
                    for s in range(x.first, x.first + x.seeds):
                        theirs = list(lineup)
                        theirs[x.lane] = "base:" + o
                        mine_a, mine_b = list(lineup), list(lineup)
                        mine_a[x.lane], mine_b[x.lane] = fa, fb
                        jobs.append((x.secs, s, mine_a + theirs if side == 0 else theirs + mine_a,
                                     mine_b + theirs if side == 0 else theirs + mine_b))
                        names.append(f"opp {o} lineup {li} side {side} seed {s}")
    else:
        heroes = sorted(f[:-len(".data_champion")] for f in os.listdir(x.a) if f.endswith(".data_champion"))
        for h in heroes:
            stage(os.path.join(x.a, h + ".data_champion"), os.path.join(tmp, h + "_a.data_champion"), x.native, False)
            stage(os.path.join(x.b, h + ".data_champion"), os.path.join(tmp, h + "_b.data_champion"), x.native,
                  not x.as_is)
        for sh in range(x.shuffles):
            order = list(heroes)
            random.Random(1000 + sh).shuffle(order)
            for i in range(0, len(order), 10):
                group = order[i:i + 10]
                group += order[:10 - len(group)] if len(group) < 10 <= len(order) else []
                slots = list(BASE10)
                for k, h in enumerate(group):
                    slots[k] = h
                fa = [s if s.startswith("base:") else os.path.join(tmp, s + "_a.data_champion") for s in slots]
                fb = [s if s.startswith("base:") else os.path.join(tmp, s + "_b.data_champion") for s in slots]
                for s in range(x.first, x.first + x.seeds):
                    jobs.append((x.secs, s, fa, fb))
                    names.append(f"seed {s}: {' '.join(slots)}")
    same = 0
    with cf.ThreadPoolExecutor(x.workers) as ex:
        for name, res in zip(names, ex.map(compare, jobs)):
            if res is None:
                same += 1
            else:
                print(f"differ at {res}: {name}", flush=True)
    print(f"{same} of {len(jobs)} games identical ({x.secs} s each)")


if __name__ == "__main__":
    main()
