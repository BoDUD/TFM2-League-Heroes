#!/usr/bin/env python3
"""Nocturne's League combo R -> E: Paranoia's landing on a champion makes Unspeakable Horror ready at once.

    python tools/fix/combo_nocturne.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Nocturne dives with R and tethers the champion he lands on with E
(Q's Duskbringer first, so the trail carries him: the main kit already has it - a champion Q hit trails a path that
counts within 15000 of him, so landing on that champion puts him on it within 6 ticks, +25% move speed, +15% attack).
Before this R and E were independent: E (11 s) was cast on minions and camps between fights and was often cooling
down when the dive landed, so the fear that follows the tether rarely came with the ult.

Design (pure data, the slots play it; champion-data.md section 5 "skill_cooldown_mult", section 7 "Combos the slots
play" and "Kill trigger"):
  * E (skill2) tracks its own cooldown: at its effect it sets the caster flag `league_nocturne_e_cd` for E's
    cooltime (660 ticks; removed first, so a flag never stacks). The flag outlasts the slot's real cooldown by at most
    E's 8-tick wind-up, so "no flag" always means E is ready.
  * R's landing (the MoveToTarget's end_effects, run on the champion with Nocturne as the caster) gets one more entry,
    a `Delayed 1`: on a living champion it asks `SwitchByBuff league_nocturne_e_cd`; with E cooling down it removes
    the flag and adds a 2-tick caster buff `league_nocturne_r_refund` with skill_cooldown_mult 10000 and
    ult_cooldown_mult -10000. The engine caps every remaining cooldown at cooltime x 100 / (100 + mult) while such a
    buff lasts (2 ticks are enough), so E's comes down to 6 ticks (Q's to 4, the price of a buff that cannot pick a
    slot); the ult's offset keeps R's own fresh 50 s (league_khazix / league_katarina's reset). The AI casts E as soon
    as it is ready, standing on the champion it just hit, so the tether (and, 2 s later, the fear) follows the dive.
    With E already ready nothing is refunded and Q keeps its cooldown.
  * The landing that kills its champion refunds nothing (League's combo needs a living target): a Delayed queued on a
    unit that died runs only its pictures and sounds, an AddCasterBuff from it is skipped (league_darius R's reset).
Why it is safe: E's own tree gains two nodes and is otherwise untouched (no second copy: the game copies `skill2`
every tick), R's landing gains five, no slot is ever held or emptied (the AI never casts a no-op: E always tethers),
both buffs have no `view_buffs` entry (invisible). addons/league_nocturne_dark copies this kit: rerun its
make_override.py afterwards (its checks look for R's landing Invisible and the top-level veils, both untouched).
Balance: at most one extra E and one extra Q per R (about 6 R a game; only the landings with E cooling down).
Idempotent: the entries are rebuilt from scratch on every run, so running it twice changes nothing; --check exits 1
when the data differs from what this script writes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_nocturne.data_champion")
E_CD = "league_nocturne_e_cd"
REFUND = "league_nocturne_r_refund"
MULT = 10000
NONE = {"type": "Combine", "effects": []}


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": tick}}, **fields},
            "only_to_enemy": False}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def ours(effect):
    text = json.dumps(effect)
    return E_CD in text or REFUND in text


def patched_skill2(skill2):
    top = skill2["effect"]
    if top.get("type") != "Combine":
        sys.exit("E's effect is no longer a Combine: update this script")
    rest = [e for e in top["effects"] if not ours(e)]
    return {**skill2, "effect": {**top, "effects": [rm(E_CD), flag(E_CD, skill2["cooltime"])] + rest}}


def landing_refund():
    refund = {"type": "Combine", "effects": [rm(E_CD), rm(REFUND),
                                             flag(REFUND, 2, skill_cooldown_mult=MULT, ult_cooldown_mult=-MULT)]}
    return {"type": "Delayed", "tick": 1, "effects": [
        {"type": "SwitchByBuff", "buff_name": E_CD, "effect_buff": refund, "effect_none": NONE}]}


def patched_ult(ult):
    top = ult["effect"]
    dives = [e for e in top.get("effects", []) if e.get("type") == "MoveToTarget"]
    if top.get("type") != "Combine" or len(dives) != 1:
        sys.exit("R no longer has one MoveToTarget in its Combine: update this script")
    dive = dives[0]
    ends = [e for e in dive["end_effects"] if not ours(e)] + [landing_refund()]
    new_dive = {**dive, "end_effects": ends}
    return {**ult, "effect": {**top, "effects": [new_dive if e is dive else e for e in top["effects"]]}}


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    new = dict(data, skill2=patched_skill2(data["skill2"]), ult=patched_ult(data["ult"]))
    if "--check" in sys.argv:
        same = new == data
        print("applied" if same else "not applied")
        sys.exit(0 if same else 1)
    if new == data:
        print("already applied:", os.path.relpath(PATH, ROOT))
        return
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(new, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(PATH, ROOT))


if __name__ == "__main__":
    main()
