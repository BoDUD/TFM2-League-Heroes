#!/usr/bin/env python3
"""Annie's League combo: Pyromania's stun is saved for Tibbers while the ult is ready (stun -> R, then W, Q).

    python tools/fix/combo_annie.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Annie holds the fourth-spell stun and opens with R (or Flash R):
Tibbers lands stunning everyone round the champion, then W and Q follow on the stunned group. Before this the stun went
to whichever damaging spell came first - mostly Q (4 s cooldown) on one champion, so the ult hardly ever stunned.

Design (pure data, caster flags only; champion-data.md section 7 "Combos the slots play"):
  * R tracks its own cooldown: at its effect it sets `league_annie_r_cd` for R's cooltime (3600) and
    `league_annie_r_open` for the cooltime + HOLD ticks (both removed first, so a flag never stacks). R starts its
    cooldown at the cast and sets them on its tick 12, so "r_open without r_cd" is the HOLD-tick span after the slot
    is ready again (12 ticks later than the slot, never earlier).
  * Q and W compute `league_annie_r_hold` (HOLD_T ticks, removed first) right before their Pyromania check: r_open
    on and r_cd off. With it, a stun-ready Q / W deals its usual damage but leaves the stun twin out (Q's
    `league_annie_q_stun` projectile, W's champion-only stun cone, each wrapped in `SwitchByBuff r_hold`), so
    pyro_ready stays and the glow keeps burning; the AI's R (cast on a champion within 62500 as soon as it is ready)
    then stuns everyone Tibbers lands on. HOLD_T 6 covers W's `Delayed 4` stun.
  * The hold ends by itself: when R goes out (r_cd again), after HOLD ticks of the ult unused (r_open runs out: R was
    cut short, or no champion came near - the stun goes back to the next Q / W), or with Annie's death (it clears
    every mod flag; the first R of each life is cast with whatever the spells left, as before).
Why it is safe: no damage, stun length or cooldown changes and no slot is held (Q and W always deal their damage: the
AI never casts a no-op); only the stun's owner moves from Q / W to R while the ult waits. The four flags have no
`view_buffs` entry (invisible). Q gains 7 nodes, W 7, R 4; nothing is copied. Annie has no add-on copy (no
addons/league_annie*). Idempotent: the inserted entries are found by their flag names and rebuilt, so a second run
writes the same bytes; --check exits 1 when the file differs from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_annie.data_champion")
N = "league_annie_"
R_CD, R_OPEN, HOLD_FLAG = N + "r_cd", N + "r_open", N + "r_hold"
HOLD = 600     # ticks the stun waits for a ready ult (10 s), then goes back to Q / W
HOLD_T = 6     # r_hold's life: W reads it in its Delayed 4
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def copy(x):
    return json.loads(json.dumps(x))


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def sw(name, yes, no):
    return {"type": "SwitchByBuff", "buff_name": name, "effect_buff": yes, "effect_none": no}


def ours(x):
    text = json.dumps(x)
    return R_CD in text or R_OPEN in text or HOLD_FLAG in text


def hold_check():
    """r_hold on while the ult is ready (r_open without r_cd)."""
    return [rm(HOLD_FLAG), sw(R_OPEN, sw(R_CD, copy(NONE), flag(HOLD_FLAG, HOLD_T)), copy(NONE))]


def held(stun):
    return sw(HOLD_FLAG, copy(NONE), stun)


def unheld(x):
    """The stun inside this script's wrapper, or the bare one."""
    if x.get("type") == "SwitchByBuff" and x.get("buff_name") == HOLD_FLAG:
        assert x["effect_buff"] == NONE
        return x["effect_none"]
    return x


def pyro_switch(effects):
    """The Pyromania check (SwitchByBuff pyro_ready) after this script's hold check, which is dropped."""
    rest = [x for x in effects if not (x.get("type") == "RemoveCasterBuff" and x["name"] == HOLD_FLAG)
            and not (x.get("type") == "SwitchByBuff" and x["buff_name"] == R_OPEN)]
    at = [i for i, x in enumerate(rest) if x.get("type") == "SwitchByBuff" and x["buff_name"] == N + "pyro_ready"]
    assert len(at) == 1, "no single Pyromania check"
    return rest, at[0]


def fix_q(q):
    rest, at = pyro_switch(q["effect"]["effects"])
    ready = rest[at]["effect_buff"]["effects"]
    stun = unheld(ready[-1])
    assert stun.get("type") == "TargetProjectile" and stun["name"] == N + "q_stun", "Q's stun twin moved"
    assert stun["applied_target"] == "EnemyChampion"
    ready[-1] = held(stun)
    q["effect"]["effects"] = rest[:at] + hold_check() + rest[at:]


def fix_w(w):
    rest, at = pyro_switch(w["effect"]["effects"])
    ready = rest[at]["effect_buff"]["effects"]
    burn = ready[-1]
    assert burn.get("type") == "Delayed" and burn["tick"] == 4, "W's burst moved"
    assert HOLD_T > burn["tick"]
    stun = unheld(burn["effects"][-1])
    assert stun.get("type") == "RangeEffect" and stun["target"] == "EnemyChampion", "W's stun cone moved"
    assert any(e.get("type") == "Stun" for e in stun["effects"])
    burn["effects"][-1] = held(stun)
    w["effect"]["effects"] = rest[:at] + hold_check() + rest[at:]


def fix_r(r):
    effects = [x for x in r["effect"]["effects"] if not ours(x)]
    track = [rm(R_CD), flag(R_CD, r["cooltime"]), rm(R_OPEN), flag(R_OPEN, r["cooltime"] + HOLD)]
    r["effect"]["effects"] = track + effects


def apply(d):
    fix_q(d["skill"])
    fix_w(d["skill2"])
    fix_r(d["ult"])
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args()
    with open(lp(a.path), "rb") as f:
        raw = f.read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(apply(json.loads(raw)), ensure_ascii=False, indent=2).replace("\n", nl) + nl
    if a.check:
        done = text == raw
        print("already done" if done else "stun -> R combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: Q / W keep Pyromania's stun for R while the ult is ready (at most {HOLD} ticks)")


if __name__ == "__main__":
    main()
