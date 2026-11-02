"""What a hero's kit still does while he is dead, on the classic SDK (trace.exe): pictures (EffectApplyed with his old
entity as caster), projectiles (ProjectileSpawnData) and his sounds (SfxEvent named <hero id>_...), counted per death
from the KillEvent to his respawn. A dead caster's flags freeze in both engines, so a zone or a casted effect that reads
one fires on and on (league_maokai's sapling, 2026-11-02: 「挂在蔚奥莱身上的一个技能触发了一直无限音效」).

    python -I tools/perf/dead_events.py SIM_DIR KITS_DIR --seeds 1-8 --shuffles 2 --secs 600 --jobs 8 --out result.jsonl
    python -I tools/perf/dead_aggregate.py result.jsonl

SIM_DIR is the folder of tools/perf/trace.rs built against the classic SDK (sim/trace.exe beside sim/assets/, docs/perf.md
section 8). KITS_DIR holds .data_champion files with their Native effects emptied (the classic engine runs no add-on
code; a copy whose damage is all native can make the AI divide by zero, battle.rs:1938, and that game fails); each game
takes 10 of them, no id twice. 2026-11-02, all 210 main-pack kits (336 games) and the add-on copies: league_azir's
soldiers stabbed on after his death (and league_maokai's sapling burst on); the rest of what runs on after a death is a
summon or a field living out its time. The SDK stops a dead caster's Delayed effects, which the game runs on:
tools/kit/scan_dead_links.py looks for those.
"""
import argparse
import concurrent.futures as cf
import json
import os
import random
import re
import subprocess
import sys

KILL = re.compile(r'^E (\d+) KillEvent\(KillEventData \{ killer: [^,]*, killed: "([^"]+)"')
SPAWN = re.compile(r'^E (\d+) EntitySpawnData\(EntitySpawnEventData \{ id: (\d+), [^}]*?, name: "([^"]+)"')
APPLY = re.compile(r'^E (\d+) EffectApplyed\(EffectApplyedEventData \{ name: "([^"]+)", caster_id: (\d+),')
PROJ = re.compile(r'^E (\d+) ProjectileSpawnData\(ProjectileSpawnEventData \{ id: \d+, caster_id: (\d+), name: "([^"]+)"')
SFX = re.compile(r'^E (\d+) SfxEvent\(SfxEventData \{ name: "([^"]+)"')


def game(sim_dir, kits, seed, secs):
    """One game of the 10 kits (paths): {hero id: [deaths: {t, until, n, ticks, names}]}."""
    ids = [json.load(open(k, encoding="utf-8"))["id"] for k in kits]
    env = dict(os.environ, TRACE_DUMP=f"0-{secs * 60}")
    p = subprocess.Popen([os.path.join(sim_dir, "sim", "trace.exe"), str(secs), str(seed), *kits], cwd=sim_dir, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    heroes = set(ids)
    entity = {}              # hero -> current entity id
    owner = {}               # entity id -> hero
    dead = {}                # hero -> the open death record
    deaths = {h: [] for h in ids}
    alive_sfx = {h: {} for h in ids}   # his own sounds while he lives
    prefixes = sorted(heroes, key=len, reverse=True)
    last = 0

    def note(h, tick, name):
        d = dead.get(h)
        if d is None:
            return
        d["n"] += 1
        d["ticks"].add(tick)
        d["names"][name] = d["names"].get(name, 0) + 1
        d["last"] = tick

    for line in p.stdout:
        if not line.startswith("E "):
            continue
        m = SPAWN.match(line)
        if m:
            tick, eid, name = int(m.group(1)), int(m.group(2)), m.group(3)
            if name in heroes:
                if name in dead:
                    d = dead.pop(name)
                    d["until"] = tick
                entity[name] = eid
                owner[eid] = name
            continue
        m = KILL.match(line)
        if m:
            tick, name = int(m.group(1)), m.group(2)
            if name in heroes and name not in dead:
                d = {"t": tick, "until": None, "n": 0, "ticks": set(), "names": {}, "last": tick,
                     "entity": entity.get(name)}
                dead[name] = d
                deaths[name].append(d)
            continue
        m = APPLY.match(line)
        if m:
            tick, name, caster = int(m.group(1)), m.group(2), int(m.group(3))
            h = owner.get(caster)
            if h and dead.get(h) and dead[h]["entity"] == caster:
                note(h, tick, "view:" + name)
            last = tick
            continue
        m = PROJ.match(line)
        if m:
            tick, caster, name = int(m.group(1)), int(m.group(2)), m.group(3)
            h = owner.get(caster)
            if h and dead.get(h) and dead[h]["entity"] == caster:
                note(h, tick, "proj:" + name)
            continue
        m = SFX.match(line)
        if m:
            tick, name = int(m.group(1)), m.group(2)
            for h in prefixes:
                if name.startswith(h + "_"):
                    if h in dead:
                        note(h, tick, "sfx:" + name)
                    else:
                        alive_sfx[h][name] = alive_sfx[h].get(name, 0) + 1
                    break
            last = max(last, tick)
    err = p.stderr.read()
    p.wait()
    out = {}
    for h, ds in deaths.items():
        out[h] = [{"t": d["t"], "until": d["until"], "n": d["n"], "ticks": len(d["ticks"]), "span": d["last"] - d["t"],
                   "names": d["names"]} for d in ds]
    return {"seed": seed, "kits": [os.path.basename(k) for k in kits], "ok": p.returncode == 0, "last": last,
            "err": err[-300:] if p.returncode else "", "deaths": out, "alive_sfx": alive_sfx}


def groups(kits, shuffle):
    """The kits in tens, no hero id twice in a game; the last group filled up from the start."""
    rng = random.Random(1000 + shuffle)
    order = kits[:]
    rng.shuffle(order)
    out = [order[i:i + 10] for i in range(0, len(order), 10)]
    if len(out[-1]) < 10:
        pool = [k for k in order if k not in out[-1]]
        out[-1] += pool[:10 - len(out[-1])]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sim_dir")
    ap.add_argument("kits_dir")
    ap.add_argument("--seeds", default="1-8")
    ap.add_argument("--shuffles", type=int, default=2)
    ap.add_argument("--secs", type=int, default=600)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", help="comma list of kit file names to test (with fillers from the rest)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    kits = sorted(os.path.join(a.kits_dir, f) for f in os.listdir(a.kits_dir) if f.endswith(".data_champion"))
    lo, hi = (int(x) for x in a.seeds.split("-"))
    games = []
    for s in range(a.shuffles):
        for g in groups(kits, s):
            if a.only and not any(os.path.basename(k) in a.only.split(",") for k in g):
                continue
            for seed in range(lo, hi + 1):
                games.append((g, seed))
    print(f"{len(kits)} kits, {len(games)} games", flush=True)
    done = 0
    with open(a.out, "w", encoding="utf-8") as f, cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(game, a.sim_dir, g, seed, a.secs) for g, seed in games]
        for fu in cf.as_completed(futs):
            r = fu.result()
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            done += 1
            if done % 25 == 0:
                print(f"{done}/{len(games)}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
