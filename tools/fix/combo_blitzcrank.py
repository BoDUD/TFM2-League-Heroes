#!/usr/bin/env python3
"""Blitzcrank's League combo Q -> E: Rocket Grab drags a champion in, Power Fist knocks it up at once.

    python tools/fix/combo_blitzcrank.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Blitzcrank hooks a champion and punches it into the air the moment
it lands at his feet. Before this Q and E were linked only by range: after the 40-tick grab the AI's E (a `Targeting`
cast within 25000) waited its own 12-tick wind-up (start_timing 12), and the hooked champion's 40-tick stun was over
before the fist came.

Design (pure data, the slot plays it: league_mordekaiser's e_combo / league_braum's r_combo window, the way
tools/fix/combo_leona.py and combo_amumu.py wrote it):
  * Q's champion-only twin (`league_blitzcrank_q_twin`, on `EnemyChampionInCC`: it lands on the champion the claw
    has just stunned, beside `q_held` and the pull) adds the caster flag `league_blitzcrank_q_combo` for WINDOW ticks.
  * E (skill2) now starts at tick 1. Its punch (the sound, the champion-first `RandomTarget` and the cast target's
    fall-back: 20 + 100% AD and Airborne 60) branches on the flag: inside the window the flag is taken off and the
    punch lands at once; otherwise it waits in a `Delayed` E_AT - 1, on tick E_AT as before. Mana Barrier's check and
    the armed ult's release stay together in one `Delayed` E_AT - 1 placed first, so outside the window everything
    still happens on tick E_AT in the old order.
So after a hook the AI's E (ready: its 14 s cooldown against Q's 20 s) knocks the champion up as it arrives, inside
the claw's stun. A miss, or a hook on a minion, opens nothing.
Why it is safe: no damage, knock-up or cooldown changes; E always punches (both branches carry it: the AI never casts a
no-op) and no slot is held; the flag is invisible (no `view_buffs` entry), timed and cleared by death. The only copy
is the 13-node punch (skill2 296 -> 315 nodes; the 280-node Mana Barrier / armed-ult block is moved, not copied). The
waiting `Delayed`s are 11 ticks, well under the chains champion-data.md section 5 leaves unguarded. Blitzcrank has no
add-on copy (no addons/league_blitzcrank*) and no other script rebuilds these parts. Idempotent: E's tree and the
twin's entry are rebuilt from their parts on every run, so a second run writes the same bytes; --check exits 1 when
the file differs from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_blitzcrank.data_champion")
N = "league_blitzcrank_"
FLAG = N + "q_combo"
WINDOW = 90   # ticks from the twin's hit (= q_held): the pull takes up to 39 of them, Q's action 40 from its cast
E_AT = 12     # E's original start_timing: the punch's tick outside the window


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def copy(x):
    return json.loads(json.dumps(x))


def is_ours(x):
    return FLAG in json.dumps(x)


def window_flag():
    return {"casting_type": "Targeting",
            "effect": {"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": WINDOW}}},
                       "only_to_enemy": False}}


def parts_of(e):
    """(the passive / armed-ult block, the punch) from the original E or from this script's tree."""
    fx = e["effect"]["effects"]
    if e["start_timing"] == E_AT:
        assert not is_ours(fx), "a combo flag in E's original tree"
        return fx[0], fx[1:]
    assert e["start_timing"] == 1 and len(fx) == 2, "unknown E tree"
    keep, sw = fx
    assert keep["type"] == "Delayed" and keep["tick"] == E_AT - 1 and len(keep["effects"]) == 1
    assert sw["type"] == "SwitchByBuff" and sw["buff_name"] == FLAG
    fast = sw["effect_buff"]["effects"]
    assert fast[0] == {"type": "RemoveCasterBuff", "name": FLAG}
    wait = sw["effect_none"]
    assert wait["type"] == "Delayed" and wait["tick"] == E_AT - 1 and wait["effects"] == fast[1:], "E's branches differ"
    return keep["effects"][0], wait["effects"]


def fix_e(d):
    e = d["skill2"]
    block, punch = parts_of(e)
    assert block["type"] == "Combine" and any(x.get("buff_name") == N + "r_armed" for x in block["effects"])
    assert [x["type"] for x in punch] == ["Sfx", "RandomTarget", "SwitchByBuff"], [x["type"] for x in punch]
    assert punch[2]["buff_name"] == N + "e_aim"
    assert any(x["type"] == "Airborne" for x in punch[1]["effects"])
    e["start_timing"] = 1
    e["effect"]["effects"] = [
        {"type": "Delayed", "tick": E_AT - 1, "effects": [block]},
        {"type": "SwitchByBuff", "buff_name": FLAG,
         "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": FLAG}] + copy(punch)},
         "effect_none": {"type": "Delayed", "tick": E_AT - 1, "effects": copy(punch)}}]


def fix_q(d):
    twins = [x for x in d["skill"]["effect"]["effects"]
             if x.get("type") == "LinearProjectile" and x.get("name") == N + "q_twin"]
    assert len(twins) == 1, "Q's twin not found"
    twin = twins[0]
    assert twin["applied_target"] == "EnemyChampionInCC" and twin["penetrate"] is False
    hit = [a for a in twin["applied_effects"] if not is_ours(a)]
    assert [a["effect"]["type"] for a in hit] == ["AddCasterBuff", "ViewEffect", "CasterAnimation", "SwitchByBuff"]
    assert hit[0]["effect"]["buff_state"]["name"] == N + "q_held"
    twin["applied_effects"] = hit + [window_flag()]


def apply(d):
    fix_q(d)
    fix_e(d)
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
        print("already done" if done else "Q -> E combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: the hook's champion hit opens {FLAG} ({WINDOW} ticks); E cast in it punches at once "
          f"(otherwise on tick {E_AT} as before)")


if __name__ == "__main__":
    main()
