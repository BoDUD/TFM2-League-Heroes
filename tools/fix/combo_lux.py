#!/usr/bin/env python3
"""Lux's League combo E -> Q -> R: the slowing field lets the binding fly at once, the bind opens the ult's detonation.

    python tools/fix/combo_lux.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Lux slows with E, binds the slowed champion with Q and fires R onto
the bound one, R detonating the Illumination Q left on him. Before this the three were independent: Q waited its
13-tick wind-up whatever E had done, and R never detonated Illumination (only the next attack did).

Design (pure data, the slots play it: league_mordekaiser's e_combo / league_leona's e_combo window):
  * E -> Q: a champion-only twin of E's slowing field (`league_lux_e_seen`, the field's radius, life and period, no
    picture) keeps the caster flag `league_lux_e_combo` up while an enemy champion stands in the field (each period
    refreshes it for E_KEEP ticks). Q (skill) now starts at tick 1 and branches on that flag: inside the window the orb
    and the shield leave at once (the window closes); otherwise they wait in a `Delayed` Q_AT - 1, i.e. on tick Q_AT
    as before. Both branches hold Q's whole effect, so the AI never casts a no-op.
  * Q -> R: a champion-only twin of Q's orb (`league_lux_q_seen`, the orb's speed, reach and radius, no picture) adds
    the caster flag `league_lux_q_combo` for Q_KEEP ticks (the bind's 90) when it reaches a champion. R cast in that
    window detonates Illumination: a champion-only twin of R's damage line (`league_lux_r_det`, the same width,
    length and timing: it lands with the beam on tick 29, inside the bind) deals the passive's detonation (the
    attack's Illumination hit, read from the attack: 50 + 35% AP, its spark and sound) to every champion the beam
    hits; the window closes at the cast. R outside the window is unchanged; R keeps re-marking (the attack's
    Illumination as before).
Why it is safe: no slot is held or emptied; every flag has a timer and no `view_buffs` entry (invisible), and death
clears it. Damage only grows in the combo: at most one detonation per champion per R (60 s cooldown). Q's tree
holds two copies of its effects plus the switch, 13 -> 35 nodes (the game copies `skill` / `skill2` every tick:
still small); E
gains a 3-node twin. Lux has no add-on copy (no addons/league_lux*). Idempotent: the trees are rebuilt from the
original effects on every run, so a second run writes the same bytes; --check exits 1 when the file differs.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_lux.data_champion")
N = "league_lux_"
E_FLAG = N + "e_combo"
Q_FLAG = N + "q_combo"
E_SEEN = N + "e_seen"
Q_SEEN = N + "q_seen"
R_DET = N + "r_det"
E_KEEP = 20    # ticks each period of the field's twin keeps the E -> Q window (period 10: no gap while he stays)
Q_KEEP = 90    # the bind's length: R's beam (29 ticks) still lands inside it
Q_AT = 13      # Q's original start_timing
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def T(effect):
    return {"casting_type": "Targeting", "effect": effect}


def rm(name):
    return {"type": "RemoveCasterBuff", "name": name}


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": name, "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def ours(x):
    text = json.dumps(x)
    return any(k in text for k in (E_FLAG, Q_FLAG, E_SEEN, Q_SEEN, R_DET))


def q_core(q):
    """Q's original effects (orb, sounds, shield), from the original kit or from this script's branch."""
    effects = q["effect"]["effects"]
    if q["start_timing"] == Q_AT:
        assert not any(ours(e) for e in effects), "a combo node in Q's original tree"
        return effects
    assert q["start_timing"] == 1 and len(effects) == 1 and effects[0]["type"] == "SwitchByBuff", "unknown Q tree"
    sw = effects[0]
    assert sw["buff_name"] == E_FLAG
    wait = sw["effect_none"]
    assert wait["type"] == "Delayed" and wait["tick"] == Q_AT - 1, "Q's waiting branch changed"
    core = [e for e in wait["effects"] if not ours(e)]
    fast = [e for e in sw["effect_buff"]["effects"] if not ours(e)]
    assert fast == core, "Q's branches differ"
    return core


def apply(d):
    # ---- Q: the champion twin of the orb (opens Q -> R) and the E -> Q branch
    q = d["skill"]
    core = copy.deepcopy(q_core(q))
    assert [e["type"] for e in core] == ["Sfx", "LinearProjectile", "Sfx", "RangeEffect"], core
    orb = core[1]
    assert orb["name"] == N + "q_orb" and orb["applied_target"] == "EnemyWithoutTower"
    seen = {"type": "LinearProjectile", "name": Q_SEEN, "speed": orb["speed"], "range": orb["range"],
            "penetrate": orb["penetrate"], "y_offset": orb["y_offset"], "applied_target": "EnemyChampion",
            "shape": copy.deepcopy(orb["shape"]),
            "applied_effects": [T(rm(Q_FLAG)), T(flag(Q_FLAG, Q_KEEP))], "end_effects": []}
    full = core[:2] + [seen] + core[2:]
    q["start_timing"] = 1
    q["effect"] = {"type": "Combine", "effects": [
        {"type": "SwitchByBuff", "buff_name": E_FLAG,
         "effect_buff": {"type": "Combine", "effects": [rm(E_FLAG)] + copy.deepcopy(full)},
         "effect_none": {"type": "Delayed", "tick": Q_AT - 1, "effects": copy.deepcopy(full)}}]}

    # ---- E: the champion twin of the slowing field
    orb_e = [e for e in d["skill2"]["effect"]["effects"] if e.get("type") == "ParabolicProjectile"]
    assert len(orb_e) == 1, "E's orb not found"
    ends = [e for e in orb_e[0]["end_effects"] if not ours(e)]
    fields = [e for e in ends if e.get("name") == N + "e_field"]
    assert len(fields) == 1, "E's field not found"
    fld = fields[0]
    twin = {"type": "RangePeriodProjectile", "name": E_SEEN, "tick": fld["tick"], "period": fld["period"],
            "first_delay": fld["first_delay"], "shape": copy.deepcopy(fld["shape"]), "applied_target": "EnemyChampion",
            "applied_effects": [T(rm(E_FLAG)), T(flag(E_FLAG, E_KEEP))], "end_effects": []}
    i = ends.index(fld)
    orb_e[0]["end_effects"] = ends[:i + 1] + [twin] + ends[i + 1:]

    # ---- R: the detonation twin of the damage line, inside the Q -> R window
    lit = d["attack"]["effect"]
    assert lit["type"] == "SwitchByBuff" and lit["buff_name"] == N + "illumination", "the attack's Illumination moved"
    bolt = [e for e in lit["effect_buff"]["effects"] if e.get("type") == "TargetProjectile"][0]
    burst = [a["effect"] for a in bolt["applied_effects"] if a["effect"]["type"] in ("ApAttack", "ViewEffect",
                                                                                   "TargetSfx")]
    assert [e["type"] for e in burst] == ["ApAttack", "ViewEffect", "TargetSfx"], burst
    r = d["ult"]["effect"]
    rest = [e for e in r["effects"] if not ours(e)]
    hits = [e for e in rest if e.get("name") == N + "r_hit"]
    assert len(hits) == 1, "R's damage line not found"
    hit = hits[0]
    det = {"type": "LineRangeProjectile", "name": R_DET, "width": hit["width"], "length": hit["length"],
           "delay": hit["delay"], "apply": hit["apply"], "applied_target": "EnemyChampion",
           "applied_effects": [T(copy.deepcopy(e)) for e in burst]}
    i = rest.index(hit)
    r["effects"] = rest[:i + 1] + [{"type": "SwitchByBuff", "buff_name": Q_FLAG,
                                    "effect_buff": {"type": "Combine", "effects": [rm(Q_FLAG), det]},
                                    "effect_none": NONE}] + rest[i + 1:]
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
        print("already done" if done else "E -> Q -> R combo not applied")
        sys.exit(0 if done else 1)
    if text == raw:
        print("already done")
        return
    with open(lp(a.path), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{a.path}: a champion in E's field opens {E_FLAG} (Q at once); Q's bind opens {Q_FLAG} ({Q_KEEP} ticks: "
          f"R detonates Illumination)")


if __name__ == "__main__":
    main()
