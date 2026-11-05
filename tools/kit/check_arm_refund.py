"""Guard: a caster flag read by a `Delayed` effect must still be up on the tick that reads it.

    python -X utf8 tools/kit/check_arm_refund.py            # every league/champion and addons/*/override kit
    python -X utf8 tools/kit/check_arm_refund.py <file>...  # the given .data_champion files

Engine rule (champion-data.md section 8, classic-SDK probe 2026-11-05 lr1105/fix_j/probe.py: 24 games, 148 of 148 at every
offset up to n - 1, 0 at n and n + 1, the same through a RangeEffect on the caster): a flag of n ticks set at tick t is
seen by a `Delayed` at t + k for k <= n - 1 and never at k >= n. The armed ults (r_arm / r_armed) relied on exactly that
read for their cooldown refund (`ult_cooldown_mult`): `delayed(n, sw("r_arm", ... refund))` found the flag gone every time,
so a lapsed window cost the full cooldown (Sion: lapse-to-rearm 3558 ticks against 877 once read at n - 3).

Nor is the last visible tick safe: league_wukong read at n - 1 and refunded 46 of 53 lapsed windows in 48 traced games,
the other 7 found the flag gone; every kit reads at n - 3 (MARGIN), which refunded 177 of 177 (league_anivia).

The check walks every action tree of a kit, summing the ticks of nested `Delayed`s (not through AddCasted, projectiles
or zones, whose timing the data does not state) and, for each `SwitchByBuff` whose on-branch adds a caster buff with a
cooldown multiplier, compares its tick with the longest same-tree caster flag of that name set earlier: a read later
than n - MARGIN ticks after a flag of n ticks fails. A flag refreshed elsewhere (a poll) can make the check too strict,
never too lax. Exit 1 on any failure.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLOTS = ("attack", "skill", "skill2", "ult")
MARGIN = 3                  # the read sits this many ticks before the flag's end (read at n - MARGIN)
STOP = {"AddCasted"}        # periodic: its children run at unknown ticks
PROJ_KEYS = {"applied_effects", "end_effects", "hit_effects"}   # projectile / zone children fly first


def walk(node, tick, flags, reads, path):
    """flags: name -> list of (tick set, duration); reads: list of (name, tick, path) for refund reads."""
    if isinstance(node, list):
        for i, x in enumerate(node):
            walk(x, tick, flags, reads, path)
        return
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "Delayed":
        tick += int(node.get("tick", 0))
    if t == "AddCasterBuff":
        st = node.get("buff_state", {})
        dur = st.get("duration")
        if isinstance(dur, dict) and "Time" in dur:
            flags.setdefault(st.get("name"), []).append((tick, int(dur["Time"]["tick"])))
        return
    if t == "SwitchByBuff":
        yes = node.get("effect_buff")
        if has_cooldown_mult(yes):
            reads.append((node.get("buff_name"), tick, path))
        walk(yes, tick, flags, reads, path + f"/{node.get('buff_name')}")
        walk(node.get("effect_none"), tick, flags, reads, path)
        return
    if t in STOP:
        return
    for k, v in node.items():
        if k in PROJ_KEYS or not isinstance(v, (dict, list)):
            continue
        walk(v, tick, flags, reads, path + (f"/{t}" if t else ""))


def has_cooldown_mult(node):
    if isinstance(node, list):
        return any(has_cooldown_mult(x) for x in node)
    if not isinstance(node, dict):
        return False
    if node.get("type") == "AddCasterBuff":
        st = node.get("buff_state", {})
        return any(k.endswith("cooldown_mult") for k in st)
    if node.get("type") in ("SwitchByBuff", "Delayed", "RangeEffect", "RandomTarget"):
        pass
    return any(has_cooldown_mult(v) for k, v in node.items() if isinstance(v, (dict, list)) and k not in PROJ_KEYS)


def check_file(path):
    d = json.load(open(path, encoding="utf-8"))
    bad = []
    for slot in SLOTS:
        act = d.get(slot)
        if not isinstance(act, dict):
            continue
        tree = act.get("effect", act.get("effects"))
        flags, reads = {}, []
        walk(tree, 0, flags, reads, slot)
        for name, at, where in reads:
            sets = [(t0, n) for t0, n in flags.get(name, []) if t0 < at]
            if not sets:
                continue        # set elsewhere (another slot, a poll): nothing to compare with
            best = max(n - (at - t0) for t0, n in sets)        # ticks of margin: 1 = read on the last visible tick
            if best < MARGIN:
                t0, n = max(sets, key=lambda s: s[1] - (at - s[0]))
                state = "gone" if best == 0 else f"gone {-best} ticks before" if best < 0 else f"only {best} tick(s) left"
                bad.append(f"{os.path.relpath(path, ROOT)}: {slot}: {name} ({n} ticks from tick {t0}) read at tick {at}"
                           f" - {state}; read it at tick {t0 + n - MARGIN} or earlier")
    return bad


def main(argv):
    files = argv or sorted(glob.glob(os.path.join(ROOT, "league", "champion", "*.data_champion"))
                           + glob.glob(os.path.join(ROOT, "addons", "*", "override", "*.data_champion")))
    bad = []
    for f in files:
        bad += check_file(f)
    for line in bad:
        print(line)
    print(f"{len(files)} kits checked, {len(bad)} refund reads with less than {MARGIN} ticks of margin")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
