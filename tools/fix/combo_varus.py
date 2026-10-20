#!/usr/bin/env python3
"""Varus's League combo R -> E / Q: Chain of Corruption roots a champion, Hail of Arrows and Piercing Arrow follow.

    python tools/fix/combo_varus.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Varus roots with R (which also gives the champion three Blight
stacks) and pops them at once with E and Q while he cannot move. Before this nothing tied them: Q (6.7 s) and E (8 s)
are also cast on minions and camps, so when the chain landed they were often cooling down and the 2 s root and the three
stacks went to waste.

Design (pure data; league_nocturne's R -> E refund, champion-data.md section 5 "skill_cooldown_mult"):
  * The tendril's champion hit (`league_varus_r_chain`, R's only projectile, `EnemyChampion`, not penetrating) gets one
    more entry, a `Delayed 1` queued on that champion: a 2-tick caster buff `league_varus_r_refund` with
    skill_cooldown_mult MULT and ult_cooldown_mult -MULT (removed first, so it never stacks). The engine caps every
    remaining cooldown at cooltime x 100 / (100 + mult) while it lasts, so Q's and E's come down to 3-4 ticks - ready
    before R's 30-tick action ends; the ult's offset keeps R's own fresh 60 s (the same pair league_varus's Blight
    refunds use since 0.170.2). The AI then casts E and Q on the rooted champion: E's rain lands 30 ticks after its
    cast and Q's full draw (a champion is in reach) releases 66 ticks in, both inside the 120-tick root; their hits pop
    the three stacks with Blight's own 64% refund as before.
  * A tendril that kills its champion refunds nothing (League's combo needs a living target): a `Delayed` queued on a
    unit that died runs only its pictures and sounds, an AddCasterBuff from it is skipped (league_darius R's reset).
With Q and E already ready nothing changes. Balance: at most one extra Q and one extra E per R that hits (about 4.4 R a
game, R 60 s); no damage, root or cooldown numbers change. Nothing holds or empties a slot (the AI never casts a no-op);
the buff has no `view_buffs` entry (invisible). R's tree gains 4 nodes. Varus has no add-on copy.
Why a fix script and not tools/kit/build_varus.py: the shipped data has since been reworked by later scripts (the
red-side caster pictures, the ult-cooldown offset), so a rebuild no longer matches it; this script patches the data in
place like those do. Idempotent: the entry is rebuilt from scratch on every run, so running it twice changes nothing;
--check exits 1 when the file differs from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_varus.data_champion")
REFUND = "league_varus_r_refund"
MULT = 10000


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def ours(entry):
    return f'"{REFUND}"' in json.dumps(entry)


def refund_entry():
    return {"casting_type": "Targeting", "effect": {"type": "Delayed", "tick": 1, "effects": [
        {"type": "RemoveCasterBuff", "name": REFUND},
        {"type": "AddCasterBuff",
         "buff_state": {"name": REFUND, "duration": {"Time": {"tick": 2}}, "skill_cooldown_mult": MULT,
                        "ult_cooldown_mult": -MULT},
         "only_to_enemy": False}]}}


def apply(d):
    chains = [e for e in d["ult"]["effect"]["effects"]
              if e.get("type") == "LinearProjectile" and e.get("name") == "league_varus_r_chain"]
    assert len(chains) == 1, "R's tendril not found"
    chain = chains[0]
    assert chain["applied_target"] == "EnemyChampion" and chain["penetrate"] is False, "R's tendril changed"
    hit = [a for a in chain["applied_effects"] if not ours(a)]
    assert any(a["effect"]["type"] == "Bind" for a in hit), "R's tendril no longer roots"
    chain["applied_effects"] = hit + [refund_entry()]
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
        print("already done" if done else "R -> E / Q combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: R's tendril hit on a living champion refunds Q and E ({REFUND}, 2 ticks, mult {MULT})")


if __name__ == "__main__":
    main()
