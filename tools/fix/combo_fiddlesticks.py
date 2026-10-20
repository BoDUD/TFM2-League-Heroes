#!/usr/bin/env python3
"""Fiddlesticks' League combo R -> E (-> W): Crowstorm's landing on champions readies Reap + Bountiful Harvest.

    python tools/fix/combo_fiddlesticks.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Fiddlesticks channels Crowstorm, lands in the fight and silences
with E, then drains with W while the storm fears. Here skill2 already chains E -> W (the reap, then the drain channel),
but R and skill2 were independent: skill2 (8 s) was often spent on waves and camps before the ult and cooling down
when the storm landed.

Design (pure data, the slots play it: tools/fix/combo_nocturne.py's refund; champion-data.md section 5
"skill_cooldown_mult"):
  * skill2 tracks its own cooldown: at its effect it sets the caster flag `league_fiddlesticks_e_cd` for its cooltime
    (480 ticks; removed first, so it never stacks). The flag outlasts the slot's real cooldown by at most the 13-tick
    wind-up, so "no flag" always means skill2 is ready (if the engine started the cooldown at the 147-tick action's
    end instead, the flag would only lapse early and a combo would be missed - never a wrong refund).
  * R's landing fear (the RangeEffect on `EnemyChampion` within 45000 on tick 60, run only after the teleport, with
    the storm up) gets one more entry per champion it fears: `SwitchByBuff league_fiddlesticks_e_cd` -> remove the
    flag and add a 2-tick caster buff `league_fiddlesticks_r_refund` with skill_cooldown_mult 10000 and
    ult_cooldown_mult -10000. The engine caps every remaining skill cooldown at cooltime x 100 / (100 + mult) while it
    lasts, so skill2's comes down to 4 ticks (Q's too, the price of a buff that cannot pick a slot); the ult's offset
    keeps R's own 60 s untouched (league_nocturne / league_khazix). The AI casts skill2 as soon as R's landing pose
    ends, in the storm, on the champions it just feared: E's silence, then W's drain. The first feared champion spends
    the flag, so one landing refunds once. With skill2 already ready nothing is refunded and Q keeps its cooldown; a
    channel broken before the landing (no teleport, no storm) refunds nothing.
Why it is safe: skill2's tree gains two nodes and is otherwise untouched (no second copy: the game copies `skill2`
every tick), the landing gains five; no slot is held or emptied (skill2 always reaps); both buffs have no `view_buffs`
entry (invisible). Balance: at most one extra skill2 and one extra Q per landed R with champions in it (60 s
cooldown). Fiddlesticks has no add-on copy (no addons/league_fiddlesticks*). Idempotent: the entries are rebuilt from
scratch on every run, so running it twice changes nothing; --check exits 1 when the data differs.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_fiddlesticks.data_champion")
N = "league_fiddlesticks_"
E_CD = N + "e_cd"
REFUND = N + "r_refund"
STORM = N + "storm"
MULT = 10000
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": tick}}, **fields},
            "only_to_enemy": False}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def ours(effect):
    text = json.dumps(effect)
    return E_CD in text or REFUND in text


def refund():
    return {"type": "SwitchByBuff", "buff_name": E_CD,
            "effect_buff": {"type": "Combine", "effects": [
                rm(E_CD), rm(REFUND), flag(REFUND, 2, skill_cooldown_mult=MULT, ult_cooldown_mult=-MULT)]},
            "effect_none": dict(NONE, effects=[])}


def landing_fear(ult):
    """The RangeEffect on EnemyChampion in the tick-60 storm pulse (RandomTarget AllyOnlySelf -> SwitchByBuff storm)."""
    found = []
    for e in ult["effect"]["effects"]:
        if e.get("type") != "Delayed" or e.get("tick") != 60:
            continue
        for rt in e["effects"]:
            if rt.get("type") != "RandomTarget" or rt.get("casting_target") != "AllyOnlySelf":
                continue
            for sw in rt["effects"]:
                if sw.get("type") == "SwitchByBuff" and sw.get("buff_name") == STORM:
                    found += [x for x in sw["effect_buff"]["effects"]
                              if x.get("type") == "RangeEffect" and x.get("target") == "EnemyChampion"]
    assert len(found) == 1, f"R's landing fear: {len(found)} found"
    return found[0]


def apply(d):
    s2 = d["skill2"]
    top = s2["effect"]
    assert top["type"] == "Combine", "skill2's effect is no longer a Combine"
    rest = [e for e in top["effects"] if not ours(e)]
    top["effects"] = [rm(E_CD), flag(E_CD, s2["cooltime"])] + rest

    fear = landing_fear(d["ult"])
    kept = [e for e in fear["effects"] if not ours(e)]
    assert [e["type"] for e in kept] == ["Fear", "ViewEffect", "TargetSfx"], kept
    fear["effects"] = kept + [refund()]
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
        print("already done" if done else "R -> E combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: skill2 sets {E_CD}; R's landing fear on a champion refunds skill2 ({REFUND}, 2 ticks)")


if __name__ == "__main__":
    main()
