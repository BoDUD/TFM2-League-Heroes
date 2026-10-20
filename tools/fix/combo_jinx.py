#!/usr/bin/env python3
"""Jinx's League combo E -> W: a Flame Chompers bite on a champion opens a window, W cast inside it zaps at once.

    python tools/fix/combo_jinx.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Jinx throws the chompers and zaps the champion they root. Here the
two slots were unlinked: W (`skill`, a `Direction` cast) charges 23 ticks before the Zap! leaves, so the AI's W after
a bite left the champion a good part of its 1.5 s root to walk out of the line's path afterwards.

The design (league_mordekaiser's e_combo / league_braum's r_combo way, "Combos the slots play" in
.claude/skills/tfm2-hero-mod/references/champion-data.md: each combo is the slot it spends, no slot is held):
- E's bite (every trap check in skill2: 20 links x 2 slots, built by tools/fix/fix_jinx_trap.py) already queues
  `WithSelf -> Delayed 1 -> AddCasterBuff e_lock, e_spent<slot>` on her; the same Delayed now also adds the caster
  flag `league_jinx_w_combo` for W_COMBO ticks (90 = the root's length), so the window opens a tick after the bite.
- W branches on that flag: with it, the flag is taken off and the zap (the same sound, line, damage and slow) leaves
  on the action's tick 1, no charge; without it, the old `Delayed 23`. The zap goes where the AI aims W - in the
  window that is usually the rooted champion, the nearest enemy standing still in front of her.
Why it is safe: W's damage sits in both branches, so the AI, which scores the branch her flags pick, reads the same W
either way and never casts a no-op; nothing is held, so the slot spends its own cooldown as before. A dead Jinx adds no
flag (her buffs freeze), and death clears the flag before she casts again. The bite's Delayed only adds caster flags
(harmless if run after her death). Adding one flag to each of the 40 checks grows skill2 by about 4 KB; W itself
by its second line (~1 KB).

Run it after tools/fix/fix_jinx_trap.py (that script rebuilds the checks and drops the flag). Idempotent: running it
twice changes nothing; --check exits 1 while the combo is not applied. The JSON keeps the formatting the other
tools/fix scripts write (indent 2, ensure_ascii False, the file's own line ends).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_jinx.data_champion")
P = "league_jinx_"
W_COMBO = 90                # the window: the root's length (Bind 90)
W_CHARGE = 23               # W's normal charge (Delayed 23 on a tick-1 action)
CHECKS = 40                 # 20 links x 2 slots


def n(x):
    return P + x


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def walk(o, pred, out):
    if isinstance(o, dict):
        if pred(o):
            out.append(o)
        for v in o.values():
            walk(v, pred, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, pred, out)
    return out


def bite_delays(skill2):
    """The `Delayed 1` each bite queues on her (it adds e_lock), one per trap check."""
    checks = walk(skill2, lambda o: o.get("type") == "RangeProjectile" and o.get("name") == n("e_check"), [])
    out = []
    for c in checks:
        found = walk(c, lambda o: o.get("type") == "Delayed" and o.get("tick") == 1
                     and any(e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == n("e_lock")
                             for e in o.get("effects", [])), [])
        if len(found) != 1:
            sys.exit(f"an e_check holds {len(found)} bite Delayed effects - the trap changed, look again")
        out.append(found[0])
    if len(out) != CHECKS:
        sys.exit(f"{len(out)} trap checks, expected {CHECKS} - the trap changed, look again")
    return out


def has_flag(delay):
    return any(e.get("type") == "AddCasterBuff" and e["buff_state"]["name"] == n("w_combo") for e in delay["effects"])


def w_done(skill):
    e = skill["effect"]["effects"]
    return len(e) == 2 and e[1].get("type") == "SwitchByBuff" and e[1].get("buff_name") == n("w_combo")


def apply_w(skill):
    eff = skill["effect"]
    cast_sfx, charge = eff["effects"]
    assert cast_sfx == {"type": "Sfx", "name": n("w_cast")}, cast_sfx
    assert charge["type"] == "Delayed" and charge["tick"] == W_CHARGE, charge
    kinds = [x["type"] for x in charge["effects"]]
    assert kinds == ["Sfx", "LinearProjectile"] and charge["effects"][1]["name"] == n("zap"), kinds
    quick = {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": n("w_combo")},
                                            *json.loads(json.dumps(charge["effects"]))]}
    eff["effects"] = [cast_sfx, {"type": "SwitchByBuff", "buff_name": n("w_combo"), "effect_buff": quick,
                                 "effect_none": charge}]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with open(lp(PATH), "rb") as f:
        raw = f.read().decode("utf-8")
    k = json.loads(raw)
    delays = bite_delays(k["skill2"])
    left = [d for d in delays if not has_flag(d)]
    w_left = not w_done(k["skill"])
    if a.check:
        print(f"league_jinx: {len(delays) - len(left)} of {len(delays)} bites open the window; "
              f"W {'without' if w_left else 'with'} the quick branch")
        sys.exit(1 if left or w_left else 0)
    for d in left:
        d["effects"].append(flag("w_combo", W_COMBO))
    if w_left:
        apply_w(k["skill"])
    if left or w_left:
        nl = "\r\n" if "\r\n" in raw else "\n"
        text = json.dumps(k, ensure_ascii=False, indent=2).replace("\n", nl) + nl
        with open(lp(PATH), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    print(f"league_jinx: {len(left)} bites given w_combo ({W_COMBO} ticks), W quick branch "
          f"{'added' if w_left else 'already there'}; skill {len(json.dumps(k['skill']))} B, "
          f"skill2 {len(json.dumps(k['skill2']))} B")


if __name__ == "__main__":
    main()
