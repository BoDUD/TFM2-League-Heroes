"""Sum dead_events.py results per hero: deaths, after-death events, the worst death, and the names behind them.

    python -I tools/perf/dead_aggregate.py result.jsonl [--top 40] [--hero league_x]
"""
import argparse
import collections
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--hero")
    a = ap.parse_args()
    rows = [json.loads(line) for f in a.files for line in open(f, encoding="utf-8")]
    failed = [r for r in rows if not r["ok"]]
    per = collections.defaultdict(lambda: {"games": 0, "deaths": 0, "events": 0, "worst": None, "names": collections.Counter(),
                                           "late": 0})
    for r in rows:
        for h, ds in r["deaths"].items():
            p = per[h]
            p["games"] += 1
            for d in ds:
                p["deaths"] += 1
                p["events"] += d["n"]
                # events later than 3 s after the death (a projectile in flight or a short chain is over by then)
                if d["span"] > 180:
                    p["late"] += 1
                p["names"].update(d["names"])
                key = (d["ticks"], d["n"])
                if p["worst"] is None or key > (p["worst"]["ticks"], p["worst"]["n"]):
                    p["worst"] = dict(d, seed=r["seed"], kits=r["kits"])
    print(f"{len(rows)} games, {len(failed)} failed")
    for r in failed[:10]:
        print("  FAILED", r["seed"], r["kits"], r["err"][-160:].replace("\n", " "))
    if a.hero:
        p = per[a.hero]
        print(json.dumps({k: (v if k != "names" else v.most_common(20)) for k, v in p.items()}, ensure_ascii=False,
                         indent=1, default=str)[:4000])
        return
    order = sorted(per.items(), key=lambda kv: -(kv[1]["worst"]["ticks"] if kv[1]["worst"] else 0))
    print(f"{'hero':28s} games deaths events late  worst(ticks/n/span)  top names")
    for h, p in order[:a.top]:
        w = p["worst"]
        if not w or w["ticks"] == 0:
            continue
        names = ", ".join(f"{n}x{c}" for n, c in p["names"].most_common(3))
        print(f"{h:28s} {p['games']:5d} {p['deaths']:6d} {p['events']:6d} {p['late']:4d}  {w['ticks']:4d}/{w['n']:4d}/{w['span']:5d}"
              f"  {names}")


if __name__ == "__main__":
    main()
