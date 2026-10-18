#!/usr/bin/env python3
"""league_tristana skill2: Rocket Jump onto the bomb written once instead of twice (skill-tree slimming, 2026-10-18).

    python tools/fix/tristana_w_once.py [--check]

W (skill2) jumps onto the champion carrying her Explosive Charge (`e_champ`) when the bomb has 2 or 3 stacks:
`SwitchByBuff e_2 (jump) (SwitchByBuff e_3 (jump) ())` - two equal copies of the 58-node jump, and the game copies
skill2 every tick (docs/perf.md). The attack's twin bolt holds the same test before its own jump.

The stacks are the hidden caster flags e_1 / e_2 / e_3 (no view_buffs entry, no stats; no add-on names them). Every
place that adds one is a stack ladder `SwitchByBuff e_3 (boom) (SwitchByBuff e_2 (e_2 -> e_3) (SwitchByBuff e_1
(e_1 -> e_2) (-> e_1)))` (the attack's bolt, every W landing in the attack and skill2, R's blasts), and every
RemoveCasterBuff e_3 sits beside a RemoveCasterBuff e_2 (the boom, E's plant, E's timed blast). So at most one of
them is on, and e_3 is only ever added by the e_2 -> e_3 step (RemoveCasterBuff e_2, AddCasterBuff e_3 250 ticks).

The step now also adds e_2 again with e_3's duration (RemoveCasterBuff e_2, AddCasterBuff e_3, AddCasterBuff e_2):
both come off together (same tick and duration, or removed side by side), so from now on e_2 is on exactly when the
old e_2 or e_3 was - "two or more stacks" - in every state, a dead caster's frozen buffs included. Every other read
of e_2 sits in the effect_none of a SwitchByBuff e_3 (the ladders, E's timed blast and its bomb picture), where e_3 is
off and e_2 reads as before; so `SwitchByBuff e_2 (jump) ()` runs and shows (the AI and enemies read the tree through
her buffs at any tick) exactly what the two copies did, in the attack too. skill (E) holds no e_2 -> e_3 step and is
left as it is. e_2's longer life changes only the buff lists (check: SAME_TRACE=trace2.exe
TRACE_HIDE=league_tristana_e_2). Idempotent: --check reports whether the file is already done.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_tristana.data_champion")
N = "league_tristana_"
NONE = {"type": "Combine", "effects": []}
SLOTS = ("attack", "skill", "skill2", "ult")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def key(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)


def nodes(x, parent=None, slot=None):
    """Every dict with a type, with its parent dict (the one whose value holds it) and the key it sits under."""
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(v, dict):
                if "type" in v:
                    yield v, x, k
                yield from nodes(v)
            elif isinstance(v, list):
                for it in v:
                    if isinstance(it, dict):
                        if "type" in it:
                            yield it, x, k
                        yield from nodes(it)


def is_add(o, name):
    return o.get("type") == "AddCasterBuff" and o["buff_state"]["name"] == N + name


def is_rm(o, name):
    return o == {"type": "RemoveCasterBuff", "name": N + name}


def is_jump_test(o):
    """SwitchByBuff e_2 (X) (SwitchByBuff e_3 (X) ()): "2 or 3 stacks"."""
    return (o.get("type") == "SwitchByBuff" and o["buff_name"] == N + "e_2"
            and o["effect_none"].get("type") == "SwitchByBuff" and o["effect_none"]["buff_name"] == N + "e_3"
            and o["effect_none"]["effect_none"] == NONE and key(o["effect_none"]["effect_buff"]) == key(o["effect_buff"]))


def step_lists(d):
    """The effect lists of the e_2 -> e_3 steps: [RemoveCasterBuff e_2, AddCasterBuff e_3, ...]."""
    out = []
    for slot in SLOTS:
        for o, _, _ in nodes(d[slot]):
            if o.get("type") == "Combine" and o["effects"] and is_rm(o["effects"][0], "e_2") \
                    and len(o["effects"]) > 1 and is_add(o["effects"][1], "e_3"):
                out.append(o["effects"])
    return out


def audit(d, done):
    """The facts the rewrite rests on (see the docstring), checked on the whole kit."""
    vb = {v["name"] for v in d.get("view_buffs", [])}
    assert N + "e_2" not in vb and N + "e_3" not in vb, "e_2 / e_3 have a picture now"
    steps = step_lists(d)
    adds3 = adds2 = 0
    for slot in SLOTS:
        for o, parent, k in nodes(d[slot]):
            if is_add(o, "e_3"):
                adds3 += 1
                assert set(o["buff_state"]) == {"name", "duration"}, "e_3 carries stats"
            if is_add(o, "e_2"):
                adds2 += 1
                assert set(o["buff_state"]) == {"name", "duration"}, "e_2 carries stats"
            if o.get("type") == "Combine" and any(is_rm(e, "e_3") for e in o["effects"]):
                assert any(is_rm(e, "e_2") for e in o["effects"]), f"{slot}: e_3 taken off without e_2"
            if o.get("type") == "SwitchByBuff" and o["buff_name"] == N + "e_2":
                under_e3_none = (parent.get("type") == "SwitchByBuff" and parent["buff_name"] == N + "e_3"
                                 and k == "effect_none")
                jump = is_jump_test(o) or (done and o["effect_none"] == NONE and not under_e3_none)
                assert under_e3_none or jump, f"{slot}: an e_2 read that is neither a ladder rung nor the jump test"
    assert adds3 == len(steps), "e_3 is added outside an e_2 -> e_3 step"
    for items in steps:
        e3 = items[1]
        again = len(items) > 2 and is_add(items[2], "e_2")
        assert again == done, "some steps add e_2 again and some do not"
        if again:
            assert items[2]["buff_state"]["duration"] == e3["buff_state"]["duration"]
    return steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8-sig")
    d = json.loads(raw)
    tests = [o for slot in SLOTS for o, _, _ in nodes(d[slot]) if is_jump_test(o)]
    steps = step_lists(d)
    done = not tests and steps and all(len(s) > 2 and is_add(s[2], "e_2") for s in steps)
    if a.check:
        print("already done" if done else f"{len(tests)} jump tests still hold two copies")
        sys.exit(0 if done else 1)
    if done:
        audit(d, True)
        print("already done")
        return
    audit(d, False)
    per_slot = {slot: sum(1 for o, _, _ in nodes(d[slot]) if is_jump_test(o)) for slot in SLOTS}
    assert per_slot == {"attack": 1, "skill": 0, "skill2": 1, "ult": 0}, per_slot
    for o in tests:
        o["effect_none"] = dict(NONE)
    steps = step_lists(d)
    for items in steps:
        e3 = items[1]
        items.insert(2, {"type": "AddCasterBuff", "buff_state": {"name": N + "e_2",
                                                                 "duration": json.loads(json.dumps(e3["buff_state"]["duration"]))},
                         "only_to_enemy": e3.get("only_to_enemy", False)})
    audit(d, True)
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: {len(tests)} jump tests written once, e_2 kept on through e_3 at {len(steps)} steps")


if __name__ == "__main__":
    main()
