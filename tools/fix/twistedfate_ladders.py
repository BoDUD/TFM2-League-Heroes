#!/usr/bin/env python3
"""league_twistedfate: the Loaded Dice ladder and the Pick a Card shuffle each written with their shared middle once
(skill-tree slimming, 2026-10-18).

    python tools/fix/twistedfate_ladders.py [--check]

The game copies skill and skill2 every tick (docs/perf.md), so both are rewritten with the same effects in the same
order for every state; the attack (not copied) keeps its own dice ladder as it is.

skill - Q's two card fans (champion first, else the cast direction: different targets, both stay) each carry the
Loaded Dice kill read: with `k_q` on, step the die counter d1..d5 (d5 -> none, d_k -> d_(k+1), none -> d1), take off
the six face pictures dice_1..dice_6, put on the new face, the dice sound and, for some faces, a dice_ap stack. The
six removals sat in all six rungs (77 nodes a read). Now: the counter step as a ladder on the old counter, the six
removals once, then the face / sound / stack as a ladder on the NEW counter (none <- d5, d1 <- none, d2 <- d1, ...).
d1..d5 are added and taken off only by the dice ladders (one in the attack, the two here; nothing in skill2, the ult
or any add-on names them) and death clears them, and every rung takes off the counter it read and adds at most one:
so at most one of d1..d5 is ever on, the step leaves exactly the rung's successor (or none), and the second ladder
picks the rung's own face - every state runs the same effects in the same order as before (a dead caster's frozen
buffs: neither ladder changes them, and the dice sound plays in every rung either way). Units read Q through his
current buffs: the kill read sits behind `k_q` (on only from a kill to its read 3 ticks later) and holds no damage,
heal, shield or crowd control in either form; while `k_q` is on, the second ladder shows the face picture and the
dice_ap amount of the rung before (neither is valued).

skill2 - W's shuffle (an AddCasted every 30 ticks while `w_shuffle` lasts) turned blue -> red -> gold -> blue: each
of the three rungs held the face step, the show-picture swap, the flip sound, the champion / unit-count probe (its
RandomTarget) and the lock decision for the new card. Now: the step as a ladder on the old card (w_cur_blue, else
w_cur_red, else gold), the shared middle once (three show removals; the new show picture by a ladder on the new card;
the flip sound; the probe), then the lock decision by a ladder on the new card. The new-card ladders test w_cur_red
(blue's successor), then w_cur_gold (red's), else blue (gold's): the step leaves w_cur_red on only after the blue
rung, w_cur_gold on with w_cur_red off only after the red rung (it read w_cur_red on and took it off) and both off
only after the gold rung (it read both off and took w_cur_gold off) - whatever else was on - and nothing between
the step and the decision names w_cur_*. Same effects, same order, the probe's random draw in the same runs; skill2
holds no damage, heal, shield or crowd control, so what units read in it is valued the same.

skill 184 -> 146 nodes (183 -> 141 packed), skill2 161 -> 140. Classic simulation (every tick's events, mid lane
against the five base mages, three lineups, both sides, seeds 1-4): 120 of 120 games identical; one logged game had 70
dice rolls (attack and Q kills) and 79 flips. Idempotent: --check reports whether the file is already done.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_twistedfate.data_champion")
N = "league_twistedfate_"
NONE = {"type": "Combine", "effects": []}
DICE = [{"type": "RemoveCasterBuff", "name": f"{N}dice_{k}"} for k in range(1, 7)]
SHOWS = [{"type": "RemoveCasterBuff", "name": f"{N}w_show_{c}"} for c in ("blue", "red", "gold")]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def key(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": N + buff, "effect_buff": yes,
            "effect_none": no if no is not None else dict(NONE, effects=[])}


def combine(items):
    return {"type": "Combine", "effects": list(items)}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": N + name}


def is_add(e, name):
    return e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == N + name


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in list(o.values()):
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def split(items, mid):
    """items = head + mid + tail -> (head, tail)"""
    k = len(mid)
    for i in range(len(items) - k + 1):
        if [key(x) for x in items[i:i + k]] == [key(x) for x in mid]:
            return items[:i], items[i + k:]
    raise AssertionError("shared middle not found")


# ---------------------------------------------------------------------------------------------- skill: dice ladder
def is_dice_read(o):
    """SwitchByBuff k_q -> [-k_q, ladder on d5..d1] (the old form)"""
    if o.get("type") != "SwitchByBuff" or o.get("buff_name") != N + "k_q":
        return False
    yes = o["effect_buff"]
    return (yes.get("type") == "Combine" and len(yes["effects"]) == 2 and yes["effects"][0] == rm("k_q")
            and yes["effects"][1].get("buff_name") == N + "d5")


def is_dice_done(o):
    if o.get("type") != "SwitchByBuff" or o.get("buff_name") != N + "k_q":
        return False
    yes = o["effect_buff"]
    return (yes.get("type") == "Combine" and len(yes["effects"]) == 9 and yes["effects"][0] == rm("k_q")
            and yes["effects"][2:8] == DICE)


def dice_once(read):
    ladder = read["effect_buff"]["effects"][1]
    rungs, node = {}, ladder
    for k in (5, 4, 3, 2, 1):
        assert node.get("type") == "SwitchByBuff" and node["buff_name"] == N + f"d{k}", node.get("buff_name")
        rungs[k] = node["effect_buff"]["effects"]
        node = node["effect_none"]
    assert node.get("type") == "Combine"
    rungs[0] = node["effects"]
    heads, tails = {}, {}
    for k, items in rungs.items():
        heads[k], tails[k] = split(items, DICE)
        if k == 5:
            assert [key(x) for x in heads[k]] == [key(rm("d5"))], heads[k]
        elif k == 0:
            assert len(heads[k]) == 1 and is_add(heads[k][0], "d1") and heads[k][0]["buff_state"]["duration"] == "Permanent"
        else:
            assert len(heads[k]) == 2 and heads[k][0] == rm(f"d{k}") and is_add(heads[k][1], f"d{k + 1}")
            assert heads[k][1]["buff_state"]["duration"] == "Permanent"
        t = tails[k]
        assert t and t[0]["type"] == "AddCasterBuff" and t[0]["buff_state"]["name"].startswith(N + "dice_"), t
        assert all(x["type"] in ("AddCasterBuff", "Sfx") for x in t), t
        assert not any(is_add(x, f"d{j}") or x == rm(f"d{j}") for x in t for j in range(1, 6))
    # the step on the old counter, the six face removals, the face on the new one (k's successor shows k's face)
    step = sw("d5", combine(heads[5]), sw("d4", combine(heads[4]), sw("d3", combine(heads[3]),
              sw("d2", combine(heads[2]), sw("d1", combine(heads[1]), combine(heads[0]))))))
    face = sw("d1", combine(tails[0]), sw("d2", combine(tails[1]), sw("d3", combine(tails[2]),
              sw("d4", combine(tails[3]), sw("d5", combine(tails[4]), combine(tails[5]))))))
    read["effect_buff"] = combine([rm("k_q"), step, *DICE, face])


# ---------------------------------------------------------------------------------------------- skill2: shuffle
def shuffle_node(d):
    found = []
    walk(d["skill2"], lambda o: found.append(o) if o.get("type") == "AddCasted" else None)
    assert len(found) == 1, len(found)
    eff = found[0]["effects"]
    assert len(eff) == 1 and eff[0].get("buff_name") == N + "w_shuffle"
    return eff[0]


def shuffle_done(node):
    yes = node["effect_buff"]
    return yes.get("type") == "Combine" and yes["effects"][0].get("buff_name") == N + "w_cur_blue" and \
        yes["effects"][1:4] == SHOWS


def shuffle_once(node):
    ladder = node["effect_buff"]
    assert ladder["buff_name"] == N + "w_cur_blue" and ladder["effect_none"]["buff_name"] == N + "w_cur_red"
    blue = ladder["effect_buff"]["effects"]
    red = ladder["effect_none"]["effect_buff"]["effects"]
    gold = ladder["effect_none"]["effect_none"]["effects"]
    flip = {"type": "Sfx", "name": N + "w_flip"}
    parts = {}
    for name, items, old, new in (("blue", blue, "blue", "red"), ("red", red, "red", "gold"),
                                  ("gold", gold, "gold", "blue")):
        head, rest = split(items, SHOWS)
        assert len(head) == 2 and head[0] == rm(f"w_cur_{old}") and is_add(head[1], f"w_cur_{new}"), (name, head)
        assert is_add(rest[0], f"w_show_{new}") and rest[1] == flip, (name, rest[:2])
        probe, decide = rest[2:-1], rest[-1]
        assert decide.get("type") == "SwitchByBuff" and decide["buff_name"] == N + "w_cn"
        assert [x.get("type") for x in probe] == ["RemoveCasterBuff"] * 3 + ["RandomTarget", "RangeEffect"]
        assert "w_cur_" not in json.dumps(probe) and "w_cur_" not in json.dumps(rest[0])
        parts[name] = (head, rest[0], probe, decide)
    probes = {key(p[2]) for p in parts.values()}
    assert len(probes) == 1, "the three probes differ"
    probe = parts["blue"][2]
    step = sw("w_cur_blue", combine(parts["blue"][0]),
              sw("w_cur_red", combine(parts["red"][0]), combine(parts["gold"][0])))
    show = sw("w_cur_red", parts["blue"][1], sw("w_cur_gold", parts["red"][1], parts["gold"][1]))
    decide = sw("w_cur_red", parts["blue"][3], sw("w_cur_gold", parts["red"][3], parts["gold"][3]))
    node["effect_buff"] = combine([step, *SHOWS, show, flip, *probe, decide])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8-sig")
    d = json.loads(raw)
    old, new = [], []
    walk(d["skill"], lambda o: (old.append(o) if is_dice_read(o) else new.append(o) if is_dice_done(o) else None))
    node = shuffle_node(d)
    done = not old and len(new) == 2 and shuffle_done(node)
    if a.check:
        print("already done" if done else "ladders still written per rung")
        sys.exit(0 if done else 1)
    if done:
        print("already done")
        return
    assert len(old) == 2 and not new, (len(old), len(new))
    names = [f"{N}d{k}" for k in range(1, 6)]
    for slot in ("skill2", "ult"):
        assert not any(nm in json.dumps(d[slot]) for nm in names), f"{slot} names d1..d5"
    for read in old:
        dice_once(read)
    if not shuffle_done(node):
        shuffle_once(node)
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: dice ladders and the shuffle written once")


if __name__ == "__main__":
    main()
