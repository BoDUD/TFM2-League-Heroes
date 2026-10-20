#!/usr/bin/env python3
"""Twisted Fate's League combo Gold Card -> Q: the stun lands, Wild Cards fly at the stunned champion at once.

    python tools/fix/combo_twistedfate.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Twisted Fate stuns with the Gold Card and throws Wild Cards at the
champion standing still. Before this the two were independent: Q (`Direction` on `EnemyWithoutTower`) aimed at a random
enemy champion within 105000 and left on tick 12, whoever the card had stunned.

Design (pure data, the slot plays it: league_leona's E -> Q window, league_mordekaiser's e_combo):
  * Both Gold Card projectiles of the attack (`league_twistedfate_wg_card`, the plain one and the one with Stacked
    Deck's bonus; both thrown only at an enemy champion) add the caster flag `league_twistedfate_gq` for WINDOW ticks
    on their hit, next to the stun (refreshed: removed first).
  * Q (skill) now starts at tick 1. Inside the window it looks for a champion in crowd control within REACH
    (`RandomTarget EnemyChampionInCC`, normally the one the card just stunned): found, the window closes and Q's cast
    sound and its card fan (one more copy of Q's champion-aimed `LinearProjectile`, unchanged: damage, falloff-free
    pierce, the Loaded Dice kill ladder) fly at him at once. Otherwise - no window, or the stun was blocked or ran out -
    Q's whole original effect waits in a `Delayed` Q_AT - 1, i.e. on tick Q_AT as before (random champion, else the
    cast's direction).
Not added: a cooldown refund - `skill_cooldown_mult` caps every skill's remaining cooldown, so refunding Q would also
hand back W's (another Pick a Card); a Q still cooling down when the card lands misses the combo, as before.
Why it is safe: no stun or cooldown change, and the window's fan deals COMBO_PCT% of Q's damage (it always lands); nothing holds or empties a slot (Q always throws, the AI never casts
a no-op); the flag has no `view_buffs` entry (invisible) and a timer, and death clears it. `skill` grows from 146 to
226 nodes (one card-fan copy, ~70 with its dice ladder; league_yone's skills are ~280). The waiting `Delayed` is
11 ticks, well under the chains champion-data.md section 5 leaves unguarded. Twisted Fate has no add-on copy (only
league_ult_press presses his R). Idempotent: Q's tree and the cards' entries are rebuilt from the original on every
run, so a second run writes the same bytes; --check exits 1 when the file differs from what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_twistedfate.data_champion")
N = "league_twistedfate_"
FLAG = N + "gq"         # the window, from a Gold Card hit
GO = N + "gq_go"        # 1 tick: this Q found the stunned champion
WINDOW = 100            # ticks from the card's hit: its stun's length (Stun 100)
REACH = 105000          # Q's own champion search
Q_AT = 12               # Q's original start_timing: the throw's tick outside the window
COMBO_PCT = 60          # the window's fan deals this % of Q's damage: it lands on the stunned champion every time
                        # (classic-SDK sim, mid vs 3 base mages, 2 x 16 seeds: full damage +1.27 / +0.71 -> +2.52 /
                        # +2.02, far above the rest of the pack)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def ours(entry):
    text = json.dumps(entry)
    return f'"{FLAG}"' in text or f'"{GO}"' in text


def window_flag():
    return {"casting_type": "Targeting", "effect": {"type": "Combine", "effects": [
        {"type": "RemoveCasterBuff", "name": FLAG},
        {"type": "AddCasterBuff", "buff_state": {"name": FLAG, "duration": {"Time": {"tick": WINDOW}}},
         "only_to_enemy": False}]}}


def gold_cards(node, out):
    if isinstance(node, dict):
        if node.get("type") == "TargetProjectile" and node.get("name") == N + "wg_card":
            out.append(node)
        for v in node.values():
            gold_cards(v, out)
    elif isinstance(node, list):
        for v in node:
            gold_cards(v, out)
    return out


def original_of(q):
    """Q's original effect (start_timing Q_AT), from the shipped kit or from this script's branch."""
    if q["start_timing"] == Q_AT:
        assert not ours(q["effect"]), "a combo flag in Q's original tree"
        return q["effect"]
    assert q["start_timing"] == 1, "unknown Q tree"
    effects = q["effect"]["effects"]
    assert [e["type"] for e in effects] == ["RemoveCasterBuff", "SwitchByBuff", "SwitchByBuff"], "unknown Q tree"
    wait = effects[2]["effect_none"]
    assert wait["type"] == "Delayed" and wait["tick"] == Q_AT - 1 and len(wait["effects"]) == 1, "unknown Q wait"
    return wait["effects"][0]


def apply(d):
    q = d["skill"]
    orig = original_of(q)
    cast, aim = orig["effects"]
    assert cast["type"] == "Sfx" and aim["type"] == "Combine", "Q's tree changed"
    pick = aim["effects"][1]
    assert pick["type"] == "RandomTarget" and pick["casting_target"] == "EnemyChampion", "Q's champion aim moved"
    fans = [e for e in pick["effects"] if e["type"] == "LinearProjectile"]
    assert len(fans) == 1 and fans[0]["name"] == N + "q_cards", "Q's card fan moved"
    fan = json.loads(json.dumps(fans[0]))
    hits = [x["effect"] for x in fan["applied_effects"] if x["effect"]["type"] == "ApAttack"]
    assert len(hits) == 1, "Q's card damage moved"
    hits[0]["damage"] = hits[0]["damage"] * COMBO_PCT // 100
    hits[0]["attack_ratio"] = hits[0]["attack_ratio"] * COMBO_PCT // 100
    fast = {"type": "RandomTarget", "range": REACH, "casting_target": "EnemyChampionInCC", "from_projectile": False,
            "effects": [{"type": "AddCasterBuff", "buff_state": {"name": GO, "duration": {"Time": {"tick": 1}}},
                         "only_to_enemy": False},
                        {"type": "RemoveCasterBuff", "name": FLAG}, json.loads(json.dumps(cast)), fan]}
    none = {"type": "Combine", "effects": []}
    q["start_timing"] = 1
    q["effect"] = {"type": "Combine", "effects": [
        {"type": "RemoveCasterBuff", "name": GO},
        {"type": "SwitchByBuff", "buff_name": FLAG, "effect_buff": fast, "effect_none": none},
        {"type": "SwitchByBuff", "buff_name": GO, "effect_buff": none,
         "effect_none": {"type": "Delayed", "tick": Q_AT - 1, "effects": [orig]}}]}

    cards = gold_cards(d["attack"], [])
    assert len(cards) == 2, f"{len(cards)} Gold Cards in the attack (2 expected)"
    for card in cards:
        assert card["applied_target"] == "Enemy"
        hit = [a for a in card["applied_effects"] if not ours(a)]
        assert any(a["effect"]["type"] == "Stun" for a in hit), "a Gold Card without its stun"
        card["applied_effects"] = hit + [window_flag()]
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
        print("already done" if done else "Gold Card -> Q combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: a Gold Card hit opens {FLAG} ({WINDOW} ticks); Q cast in it throws at once at the champion in "
          f"crowd control (otherwise on tick {Q_AT} as before)")


if __name__ == "__main__":
    main()
