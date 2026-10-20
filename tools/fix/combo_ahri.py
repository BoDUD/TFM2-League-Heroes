#!/usr/bin/env python3
"""Ahri's League combo E -> Q: Orb of Deception goes to the champion Charm just walked toward her.

    python tools/fix/combo_ahri.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Ahri lands Charm and throws Q straight through the champion it
holds: the charmed champion walks to her, cannot dodge, and takes both ways of the orb. Before this Fox-Fire (W, folded
into Q) already hunted the charmed champion first, but Q itself is a `Direction` cast on `EnemyWithoutTower` and flew
wherever the AI aimed - often at a minion beside the charmed champion (champion-data.md section 7, "Aim at a champion,
cast at anything").

Design (pure data, the slots play it: league_morgana Q's aim and league_leona's window):
  * E's kiss (`league_ahri_e_kiss`, champion-only, not penetrating) adds the caster flag `league_ahri_e_combo` for
    WINDOW ticks on its hit, beside the charm (the caster-flag-from-a-hit form of tools/fix/combo_leona.py).
  * Q's orb (`league_ahri_q_out` with its way back in `end_effects`) is now fired by two checks one after the other,
    still on Q's tick 10: inside the window `RandomTarget {AIM, EnemyChampionInCC}` throws it at the charmed (any
    crowd-controlled) champion in reach and sets the 1-tick flag `league_ahri_q_aim`; then `SwitchByBuff q_aim` throws
    it the cast's way when nothing was picked (the window closed, or the champion already out of reach) - Fox-Fire's
    w_pick way (tools/fix/ahri_essence_count.py), so the second check reads the flag on the same tick.
Why it is safe: no damage, cooldown or timing changes; Q always throws exactly one orb (the AI never casts a no-op);
both flags are invisible (no `view_buffs` entry) and timed, death clears them; Q (360) and E (600) allow one Q per
window. The only copy is the orb itself (out and back, about 45 nodes; skill was 333): a `Direction` projectile can
only be aimed by a `RandomTarget` around it. Ahri has no add-on copy (no addons/league_ahri*).
Order: run tools/fix/ahri_essence_count.py first (it only acts on the old counters and reports "already done" on a
file this script wrote: its asserts sit behind that check). Idempotent: the orb's checks and the kiss's flag are
rebuilt from the orb on every run, so a second run writes the same bytes; --check exits 1 when the file differs from
what this script writes.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_ahri.data_champion")
N = "league_ahri_"
FLAG = N + "e_combo"
AIM_FLAG = N + "q_aim"
WINDOW = 75   # ticks from the kiss's hit: the charm's length (Charm 75)
AIM = 70000   # the orb flies 75000 with a 9000 radius: the picked champion must be inside its reach
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def copy(x):
    return json.loads(json.dumps(x))


def is_ours(x):
    text = json.dumps(x)
    return FLAG in text or AIM_FLAG in text


def is_orb(x):
    return x.get("type") == "LinearProjectile" and x.get("name") == N + "q_out"


def window_flag():
    return {"casting_type": "Targeting",
            "effect": {"type": "AddCasterBuff",
                       "buff_state": {"name": FLAG, "duration": {"Time": {"tick": WINDOW}}},
                       "only_to_enemy": False}}


def aimed(orb):
    """The orb at the charmed champion inside the window, else the cast's way: [check 1, check 2]."""
    pick = {"type": "RandomTarget", "range": AIM, "casting_target": "EnemyChampionInCC", "from_projectile": False,
            "effects": [{"type": "AddCasterBuff", "buff_state": {"name": AIM_FLAG, "duration": {"Time": {"tick": 1}}},
                         "only_to_enemy": False}, copy(orb)]}
    return [{"type": "SwitchByBuff", "buff_name": FLAG, "effect_buff": pick, "effect_none": copy(NONE)},
            {"type": "SwitchByBuff", "buff_name": AIM_FLAG, "effect_buff": copy(NONE), "effect_none": copy(orb)}]


def orb_of(effects):
    """Q's orb: the bare one of the original kit, or the cast-way one inside this script's second check."""
    bare = [i for i, x in enumerate(effects) if is_orb(x)]
    if bare:
        assert len(bare) == 1 and not any(is_ours(x) for x in effects), "Q: half-patched"
        return bare[0], 1, effects[bare[0]]
    ours = [i for i, x in enumerate(effects) if is_ours(x)]
    assert len(ours) == 2 and ours[1] == ours[0] + 1, "Q: unknown tree"
    first, second = effects[ours[0]], effects[ours[1]]
    assert first["buff_name"] == FLAG and second["buff_name"] == AIM_FLAG
    orb = second["effect_none"]
    assert is_orb(orb) and first["effect_buff"]["effects"][1] == orb, "Q: the two orbs differ"
    return ours[0], 2, orb


def apply(d):
    q = d["skill"]
    assert q["start_timing"] == 10 and q["casting_type"] == "Direction", "Q changed"
    effects = q["effect"]["effects"]
    at, width, orb = orb_of(effects)
    assert orb["applied_target"] == "EnemyWithoutTower" and orb["penetrate"] is True
    effects[at:at + width] = aimed(orb)

    kisses = [x for x in d["skill2"]["effect"]["effects"]
              if x.get("type") == "LinearProjectile" and x.get("name") == N + "e_kiss"]
    assert len(kisses) == 1, "E's kiss not found"
    kiss = kisses[0]
    assert kiss["applied_target"] == "EnemyChampion" and kiss["penetrate"] is False
    hit = [a for a in kiss["applied_effects"] if not is_ours(a)]
    kinds = [x["type"] for x in hit[0]["effect"]["effects"]] if len(hit) == 1 else None
    assert kinds and "Charm" in kinds, kinds
    kiss["applied_effects"] = hit + [window_flag()]
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
        print("already done" if done else "E -> Q combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: the kiss's hit opens {FLAG} ({WINDOW} ticks); Q's orb in it flies at the charmed champion "
          f"(within {AIM}), otherwise the cast's way as before")


if __name__ == "__main__":
    main()
