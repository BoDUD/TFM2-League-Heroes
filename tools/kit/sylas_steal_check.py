#!/usr/bin/env python3
"""Does a League champion's ult still do something when league_sylas's add-on steals it? One traced classic-engine game
per champion (league_sylas 0.2.0's real Hijack, addons/league_sylas/make_override.py).

    python tools/kit/sylas_steal_check.py --sim C:/t/sy_sim2 [hero ...]      # default: every league_* but Sylas

--sim is a folder holding sim/trace.exe (tools/perf/trace.rs built with the classic SDK's build.sh, as for
tools/perf/same_games.py) and sim/assets. For each champion a test copy of the add-on's Sylas
(addons/league_sylas/override, so run make_override.py first with the champion NOT in its BY_CLASS) whose steal chain
lays steal_<hero> and r_real itself - the add-on's passive does that in game, and the classic engine runs no native
code; the copy's Native effects are swapped for a plain heal and its passive dropped. Sylas plays mid in a 5v5
against base heroes; the trace counts the events naming the champion's own pictures and projectiles. A champion with
none (its R slot only arms a flag its own attacks or watchers fire, or it needs a state only it has: league_mel's
stacks, league_orianna's ball, league_gnar's Mega form) belongs in make_override.py's BY_CLASS (stolen by class).
"""
import argparse
import collections
import concurrent.futures as cf
import glob
import json
import os
import subprocess

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PROJ = ("ViewEffect", "CasterViewEffect", "TargetProjectile", "LinearProjectile", "RangeProjectile", "RangePeriodProjectile",
        "ParabolicProjectile", "LineRangeProjectile", "ApplyInProjectile", "BackToCasterLinearProjectile",
        "AutoTargetProjectile", "TargetSplashProjectile")


def walk(o, fn):
    if isinstance(o, dict):
        for v in o.values():
            walk(v, fn)
        fn(o)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def test_copy(base, hero):
    k = json.loads(json.dumps(base))
    k.pop("passive", None)

    def fix(d):
        effs = d.get("effects")
        if not isinstance(effs, list):
            return
        for i, e in enumerate(effs):
            if isinstance(e, dict) and e.get("type") == "Native":
                effs[i] = {"type": "Heal", "amount": 60, "attack_ratio": 0, "ap_ratio": 35, "heal_type": "Caster"}
        if any(isinstance(e, dict) and e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == "league_sylas_r_have"
               for e in effs):
            for n in ("league_sylas_steal_" + hero, "league_sylas_r_real"):
                effs.append({"type": "AddCasterBuff", "buff_state": {"name": n, "duration": {"Time": {"tick": 600}}},
                             "only_to_enemy": False})
    walk(k, fix)
    return k


def check(sim, base, hero, seed=3):
    path = os.path.join(sim, f"steal_{hero}.data_champion")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(test_copy(base, hero), f)
    own = json.load(open(os.path.join(ROOT, "league", "champion", f"league_{hero}.data_champion"), encoding="utf-8-sig"))
    names = set()
    walk(own["ult"]["effect"], lambda d: names.add(d["name"]) if d.get("type") in PROJ and isinstance(d.get("name"), str)
         else None)
    team = ["base:fighter", "base:ninja", path, "base:archer", "base:priest"]
    foes = ["base:knight", "base:demon", "base:pyromancer", "base:gunner", "base:monk"]
    out = subprocess.run([os.path.join(sim, "sim", "trace.exe"), "600", str(seed)] + team + foes, capture_output=True,
                         text=True, encoding="utf-8", errors="replace", cwd=sim,
                         env=dict(os.environ, TRACE_DUMP="0-36000")).stdout
    seen = collections.Counter()
    for line in out.splitlines():
        if line.startswith("E "):
            for n in names:
                if f'"{n}"' in line:
                    seen[n] += 1
    os.remove(path)
    return hero, seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("heroes", nargs="*")
    a = ap.parse_args()
    base = json.load(open(os.path.join(ROOT, "addons", "league_sylas", "override", "league_sylas.data_champion"),
                          encoding="utf-8-sig"))
    heroes = a.heroes or sorted(os.path.basename(p)[len("league_"):-len(".data_champion")]
                                for p in glob.glob(os.path.join(ROOT, "league", "champion", "league_*.data_champion")))
    heroes = [h for h in heroes if h != "sylas"]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for hero, seen in ex.map(lambda h: check(a.sim, base, h), heroes):
            flag = "" if seen else "   <-- nothing of its own: BY_CLASS?"
            print(f"{hero:14s} {sum(seen.values()):5d} {sorted(seen)[:4]}{flag}", flush=True)


if __name__ == "__main__":
    main()
