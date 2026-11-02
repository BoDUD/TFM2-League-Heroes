"""Find Delayed effects that make a sound or deal damage behind a caster flag without asking first whether the caster
lives. In the game a dead caster's Delayed effects run on (champion-data.md: league_riven R) and his flags freeze, so a
chain of such links - league_teemo R's cloud every 15 ticks behind `boom` - repeats to its end after his death. The
classic SDK stops them at death, so tools/perf/dead_events.py cannot see these. A flag a search for him adds, or one this
same run adds for a tick or two, counts as a guard; a heartbeat (each link reading the flag the one before it set:
league_jinx E, league_yone E, league_zed's shadow) does not show here, so read what is left by hand.

    python -I tools/kit/scan_dead_links.py league/champion tft/champion ... [--min 6]
"""
import argparse
import collections
import os
import json

LOUD = {"Sfx", "TargetSfx"}
HARM = {"Attack", "ApAttack", "FixedAttack", "Bind", "Stun", "Airborne", "Knockback", "Grab", "Fear", "Silence",
        "Taunt", "Charm", "AddCasted", "TargetProjectile", "LinearProjectile", "ParabolicProjectile", "RangeProjectile",
        "RangePeriodProjectile", "Heal", "Shield", "MoveToTarget", "MoveTo", "Teleport"}


def children(node):
    for k, v in node.items():
        if k in ("buff_state", "shape"):
            continue
        for x in (v if isinstance(v, list) else [v]):
            if not isinstance(x, dict):
                continue
            if "type" in x:
                yield x
            elif isinstance(x.get("effect"), dict):
                yield x["effect"]


def walk(node):
    yield node
    for c in children(node):
        yield from walk(c)


def short(buff_state, most=2):
    d = buff_state.get("duration")
    return isinstance(d, dict) and "Time" in d and d["Time"].get("tick", 99) <= most


def guard_flags(effects):
    """Flags a search for him adds, and short flags this same run adds before reading them: a dead caster gets
    neither (champion-data: "a branch behind a caster flag the same run adds just before reading it")."""
    out = set()
    for e in effects:
        for n in walk(e):
            if n.get("type") == "AddCasterBuff" and short(n["buff_state"]):
                out.add(n["buff_state"]["name"])
            if n.get("type") == "RandomTarget" and n.get("casting_target") == "AllyOnlySelf":
                for m in walk(n):
                    if m.get("type") == "AddCasterBuff":
                        out.add(m["buff_state"]["name"])
    return out


def exposed(node, guards, gates, out):
    """(gates, kind) for every sound / harmful effect behind unguarded caster-flag gates, up to the next Delayed."""
    t = node.get("type")
    if t == "Delayed":
        return  # a link of its own, scanned on its own
    if t == "RandomTarget" and node.get("casting_target") == "AllyOnlySelf":
        return
    if gates and not (set(gates) & guards) and (t in LOUD or t in HARM):
        out.add((tuple(gates), "sound" if t in LOUD else "harm"))
    if t == "SwitchByBuff":
        for b in ("effect_buff", "effect_none"):
            if isinstance(node.get(b), dict):
                exposed(node[b], guards, gates + (node["buff_name"],), out)
        return
    for c in children(node):
        exposed(c, guards, gates, out)


def scan(path, label, least):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print("skip", label, e)
        return
    for action in ("attack", "skill", "skill2", "ult"):
        a = data.get(action)
        if not isinstance(a, dict) or not isinstance(a.get("effect"), dict):
            continue
        links = collections.Counter()
        kinds = collections.defaultdict(set)
        for d in walk(a["effect"]):
            if d.get("type") != "Delayed":
                continue
            effs = d.get("effects", [])
            guards = guard_flags(effs)
            out = set()
            for e in effs:
                exposed(e, guards, (), out)
            for gates, kind in out:
                key = gates[-1]  # the flag right before the effect
                links[key] += 1
                kinds[key].add(kind)
        for flag, n in sorted(links.items(), key=lambda kv: -kv[1]):
            if n >= least:
                print(f"{label}  {action}  {n:3d} links behind {flag}  ({', '.join(sorted(kinds[flag]))})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--min", type=int, default=3)
    a = ap.parse_args()
    for p in a.paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    if f.endswith(".data_champion"):
                        scan(os.path.join(root, f), os.path.relpath(os.path.join(root, f), p), a.min)
        else:
            scan(p, p, a.min)


if __name__ == "__main__":
    main()
