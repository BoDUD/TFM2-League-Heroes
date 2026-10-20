#!/usr/bin/env python3
"""Garen's League combo Q -> E: Judgment cast with Decisive Strike still loaded opens on the silencing strike.

    python tools/fix/combo_garen.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Garen runs in with Q, silences the champion with the empowered hit
and spins (E) on him at once while he cannot answer. Here Q only loads the strike (`league_garen_decisive`, 270
ticks) for his next attack, and the spin's forced animation holds him 3 s: when the AI cast E before that attack
(both come in melee reach), the strike waited until after the spin, so the silence came at its end or was lost.

Design (pure data, the slot it spends plays it: league_leesin's QQAE / league_akali's E Q A way):
  * E (skill2) starts with `SwitchByBuff league_garen_decisive`: loaded, it looks for an enemy champion within
    REACH (his attack reach; the spin's own first ring uses the same 25000) and strikes him at once with Decisive
    Strike's hit, read from the attack's empowered branch (40 + 150% AD, `BlockSkill` 90 = the 1.5 s silence, its
    sound and spark), spending the strike. Then the spin runs as before, on a silenced champion. No champion in reach:
    the strike stays loaded for his next attack, as before.
Why not more: a refund cannot pick a slot (`skill_cooldown_mult` caps Q and E together, champion-data section 5), so
"E ready at once after the hit" would also bring Q back the moment it was spent (Q -> E -> Q -> E ...), and R's
falling sword is a picture timed to its 10-tick drop (a quicker R needs new art); R already lands on the silenced
champion. Nothing is held or emptied (E always spins), no number changes; the strike is dealt once either way. E's
tree gains 8 nodes (the game copies `skill2` every tick). Garen has no add-on copy (no addons/league_garen*).
tools/kit/garen_spin.py (the spin's rings) refuses a second run and does not touch this node. Idempotent: the node
is rebuilt from the attack's strike on every run; --check exits 1 when the file differs from what this script writes.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_garen.data_champion")
DECISIVE = "league_garen_decisive"
REACH = 25000   # his attack reach (the spin's first ring uses the same)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def is_ours(e):
    return e.get("type") == "SwitchByBuff" and e.get("buff_name") == DECISIVE


def strike_of(d):
    a = d["attack"]["effect"]
    assert a["type"] == "SwitchByBuff" and a["buff_name"] == DECISIVE, "the attack's Decisive Strike branch moved"
    hits = [e for e in a["effect_buff"]["effects"] if e.get("type") == "Delayed"]
    assert len(hits) == 1, "Decisive Strike's hit not found"
    hit = hits[0]["effects"]
    assert [e["type"] for e in hit] == ["Attack", "BlockSkill", "TargetSfx", "ViewEffect"], hit
    return copy.deepcopy(hit)


def apply(d):
    e = d["skill2"]
    top = e["effect"]
    assert top["type"] == "Combine", "E's effect is no longer a Combine"
    rest = [x for x in top["effects"] if not is_ours(x)]
    kinds = [x["type"] for x in rest[:3]]
    assert kinds == ["Sfx", "CasterAnimation", "Delayed"], kinds
    node = {"type": "SwitchByBuff", "buff_name": DECISIVE,
            "effect_buff": {"type": "RandomTarget", "range": REACH, "casting_target": "EnemyChampion",
                            "from_projectile": False,
                            "effects": [{"type": "RemoveCasterBuff", "name": DECISIVE}] + strike_of(d)},
            "effect_none": {"type": "Combine", "effects": []}}
    top["effects"] = rest[:2] + [node] + rest[2:]
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
    print(f"{a.path}: E cast with {DECISIVE} loaded strikes a champion within {REACH} at once (silence), then spins")


if __name__ == "__main__":
    main()
