#!/usr/bin/env python3
"""league_ahri: Essence Theft's hit counter with the count kept in place (skill-tree slimming, 2026-10-18).

    python tools/fix/ahri_essence_count.py [--check]

Essence Theft counts one hit per cast (the et_lock_q / w / e / r flags) with three Permanent caster flags: et1 -> et2
-> et_ready (the essence picture, her only view buff of the three). The counter was

    SwitchByBuff et_ready (nothing) (SwitchByBuff et2 ([-et2, +et_ready]) (SwitchByBuff et1 ([-et1, +et2]) (+et1)))

(11 nodes) in 18 hits: Q's two (out and back) and the nine Fox-Fire projectiles of skill (W is folded into Q), the
Charm of skill2, the six bolts of the ult - and the game copies skill and skill2 every tick (docs/perf.md). The hidden
et1 and et2 now stay on as the count grows, so the counter reads

    SwitchByBuff et2 (SwitchByBuff et_ready (nothing) (+et_ready)) (SwitchByBuff et1 (+et2) (+et1))

(7 nodes), and the three casts that spend the essence (Q, E and R: take et_ready off, open the heal window et_heal)
also take et1 and et2 off. Every add, removal and read of the three flags is in those 18 counters and 3 casts
(asserted below; no add-on names them - addons/*/src, addons/*/override and the other kits checked), all three are
Permanent and death clears a mod's buffs, so the reachable states map one to one: {} -> {}, {et1} -> {et1},
{et2} -> {et1, et2}, {et_ready} -> {et1, et2, et_ready}. Each hit and each cast makes the same move as before, so
et_ready (the picture) comes and goes on the same ticks; the two counters and the spending branch hold flags only,
nothing the AI values, so every unit reads the same values from the trees in every state, at any tick. Only
EntityInfo's buff lists change (hidden flags): check with SAME_TRACE=trace2.exe TRACE_HIDE=league_ahri_et1,league_ahri_et2.

Fox-Fire's three volleys also lose a wrapper: SwitchByBuff w_pick (nothing) ([search EnemyChampion -> +w_pick, orb;
SwitchByBuff w_pick (nothing) (search EnemyWithoutTower -> orb)]) becomes the two checks one after the other - the
second reads the 1-tick flag right after the first, so the same searches run in the same order, and with w_pick on or
off both forms read the same orbs.

skill 378 -> 333 nodes (skill2 38 -> 36, ult 212 -> 190). Idempotent: --check reports whether the file is done.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_ahri.data_champion")
N = "league_ahri_"
NONE = {"type": "Combine", "effects": []}
SLOTS = ("attack", "skill", "skill2", "ult")
COUNTERS = {"skill": 11, "skill2": 1, "ult": 6}     # hits that count, per slot
SPENDS = {"skill": 1, "skill2": 1, "ult": 1}        # casts that spend the essence


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def key(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)


def sw(buff, yes, no):
    return {"type": "SwitchByBuff", "buff_name": N + buff, "effect_buff": yes, "effect_none": no}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": N + name}


def add(name):
    return {"type": "AddCasterBuff", "buff_state": {"name": N + name, "duration": "Permanent"}, "only_to_enemy": False}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


OLD_COUNTER = sw("et_ready", NONE, sw("et2", combine(rm("et2"), add("et_ready")),
                                      sw("et1", combine(rm("et1"), add("et2")), add("et1"))))
NEW_COUNTER = sw("et2", sw("et_ready", NONE, add("et_ready")), sw("et1", add("et2"), add("et1")))


def is_old_spend(o):
    return (o.get("type") == "SwitchByBuff" and o.get("buff_name") == N + "et_ready" and o["effect_none"] == NONE
            and o["effect_buff"].get("type") == "Combine" and len(o["effect_buff"]["effects"]) == 2
            and o["effect_buff"]["effects"][0] == rm("et_ready")
            and o["effect_buff"]["effects"][1].get("type") == "AddCasterBuff"
            and o["effect_buff"]["effects"][1]["buff_state"]["name"] == N + "et_heal")


def is_new_spend(o):
    return (o.get("type") == "SwitchByBuff" and o.get("buff_name") == N + "et_ready" and o["effect_none"] == NONE
            and o["effect_buff"].get("type") == "Combine" and len(o["effect_buff"]["effects"]) == 4
            and o["effect_buff"]["effects"][:3] == [rm("et_ready"), rm("et1"), rm("et2")]
            and o["effect_buff"]["effects"][3].get("type") == "AddCasterBuff"
            and o["effect_buff"]["effects"][3]["buff_state"]["name"] == N + "et_heal")


def find(o, pred, acc):
    if isinstance(o, dict):
        if pred(o):
            acc.append(o)
        for v in o.values():
            find(v, pred, acc)
    elif isinstance(o, list):
        for v in o:
            find(v, pred, acc)
    return acc


def uses(o, names, acc):
    """Every add / removal / read of the named flags: (kind, name)."""
    if isinstance(o, dict):
        t = o.get("type")
        if t == "SwitchByBuff" and o["buff_name"] in names:
            acc.append(("read", o["buff_name"]))
        elif t in ("AddCasterBuff", "AddBuff") and o["buff_state"]["name"] in names:
            acc.append((t, o["buff_state"]["name"]))
        elif t == "RemoveCasterBuff" and o["name"] in names:
            acc.append(("rm", o["name"]))
        for v in o.values():
            uses(v, names, acc)
    elif isinstance(o, list):
        for v in o:
            uses(v, names, acc)
    return acc


def volleys(d):
    """Fox-Fire's three Delayed volleys inside Q (skill): W is the w_cd switch's branch."""
    w = [x for x in d["skill"]["effect"]["effects"] if x.get("type") == "SwitchByBuff" and x["buff_name"] == N + "w_cd"]
    assert len(w) == 1, "skill: no single w_cd switch"
    out = [x for x in w[0]["effect_none"]["effects"] if x.get("type") == "Delayed"]
    assert [x["tick"] for x in out] == [8, 12, 16], [x["tick"] for x in out]
    return out


def nested_pick(v):
    """The volley's last effect while still nested: SW w_pick (nothing) ([search, SW w_pick (nothing) (search)])."""
    last = v["effects"][-1]
    if last.get("type") != "SwitchByBuff" or not last["buff_name"].startswith(N + "w_pick"):
        return None
    inner = last["effect_none"]
    if inner.get("type") != "Combine":
        return None
    return last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8-sig")
    d = json.loads(raw)
    old = {s: find(d[s]["effect"], lambda o: o == OLD_COUNTER, []) for s in SLOTS}
    new = {s: find(d[s]["effect"], lambda o: o == NEW_COUNTER, []) for s in SLOTS}
    nested = [v for v in volleys(d) if nested_pick(v)]
    todo = sum(len(v) for v in old.values()) + len(nested)
    if a.check:
        print("already done" if not todo else f"{sum(len(v) for v in old.values())} old counters, "
              f"{len(nested)} nested volleys left")
        sys.exit(1 if todo else 0)
    if not todo:
        print("already done")
        return
    for s in SLOTS:
        assert len(old[s]) + len(new[s]) == COUNTERS.get(s, 0), f"{s}: {len(old[s])} + {len(new[s])} counters"
        assert not new[s], f"{s}: half done"
        spends = find(d[s]["effect"], is_old_spend, [])
        assert len(spends) == SPENDS.get(s, 0), f"{s}: {len(spends)} spending casts"
        # the counters (3 reads, 2 removals, 3 adds) and the spending casts (a read, a removal) are every use
        names = {N + "et1", N + "et2", N + "et_ready"}
        u = uses(d[s]["effect"], names, [])
        assert len(u) == 8 * len(old[s]) + 2 * len(spends), f"{s}: et1 / et2 / et_ready used elsewhere"
        for o in old[s]:
            o.clear()
            o.update(copy.deepcopy(NEW_COUNTER))
        for o in spends:
            items = o["effect_buff"]["effects"]
            o["effect_buff"]["effects"] = [items[0], rm("et1"), rm("et2"), items[1]]
    for v in nested:
        last = v["effects"][-1]
        flag = last["buff_name"]
        second, third = last["effect_none"]["effects"]
        assert second.get("type") == "RandomTarget" and second["casting_target"] == "EnemyChampion"
        assert second["effects"][0]["buff_state"]["name"] == flag
        assert third.get("type") == "SwitchByBuff" and third["buff_name"] == flag and third["effect_buff"] == NONE
        assert third["effect_none"].get("type") == "RandomTarget"
        assert third["effect_none"]["casting_target"] == "EnemyWithoutTower"
        assert last["effect_buff"] == NONE
        v["effects"][-1:] = [sw(flag[len(N):], {"type": "Combine", "effects": []}, second), third]
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: {sum(len(v) for v in old.values())} counters rewritten, {len(nested)} volleys flattened")


if __name__ == "__main__":
    main()
