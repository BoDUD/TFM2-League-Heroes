#!/usr/bin/env python3
"""Malphite's League combo R -> E (-> Q): Unstoppable Force landing on champions readies Ground Slam, which slams at once.

    python tools/fix/combo_malphite.py [--check]

The user: 「有连招要做连招」「都要帮我补」. League's Malphite lands his ult and slams the ground (then throws the
shard) while the champions are in the air. Here R and E were independent casts: E (`skill2`, 7 s) was often still
cooling down when R landed, and its slam came 11 ticks into the action. The kit has no generator, so this script
edits the shipped JSON.

The design (league_galio's r_reset refund and league_mordekaiser's r_combo window, "Combos the slots play" in
.claude/skills/tfm2-hero-mod/references/champion-data.md):
- R's landing (the `Delayed 4` in MoveToTarget's end_effects) gets a champion-only twin of the crater: a `RangeEffect`
  on `EnemyChampion` round him (the same radius, 30000) that adds two caster flags, once however many it finds:
  - `league_malphite_r_refund` for REFUND_T ticks with `skill_cooldown_mult` REFUND: every tick it lasts it caps each
    remaining basic-ability cooldown at cooltime x 100 / (100 + REFUND) - E at 9 ticks, Q at 8 - so both are ready
    before his 28-tick slam pose ends; `ult_cooldown_mult` -REFUND on the same buff keeps R's own cap unchanged (the
    engine caps the ult with the sum: tools/fix/ult_cooldown_offset.py);
  - `league_malphite_r_combo` for R_COMBO ticks (75 = the knock-up's length).
- E branches on `r_combo` at its new `start_timing` 1: with it, the flag is taken off, R's slam pose (`ult_slam`, its
  impact on tick 4, as in R) plays and the slam lands 3 ticks later, on tick 4; without it, the old slam in a
  `Delayed 10`, still on its tick 11. The passive's shield check stays once, outside the branch.
So after R hits a champion the AI finds E (and Q) ready with the knocked-up champions round him and slams while they
are still in the air, then throws the shard. A miss (no champion within 30000 at the landing) changes nothing.
Why it is safe: E's damage sits in both branches, so the AI scores the same E either way and never casts a no-op; no
slot is held; the refund costs at most one early E and Q per landed R (60 s cooldown); the flags are added by the
landing only, a dead Malphite adds none, and death clears them. E grows by about 0.5 KB.

Idempotent: running it twice changes nothing; --check exits 1 while the combo is not applied. The JSON keeps the
formatting the other tools/fix scripts write (indent 2, ensure_ascii False, the file's own line ends).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "league", "champion", "league_malphite.data_champion")
P = "league_malphite_"
R_COMBO = 75                # the window: the knock-up's length (Airborne 75)
REFUND = 4900               # skill_cooldown_mult: caps at 2% of the cooltime (E 420 -> 9, Q 360 -> 8)
REFUND_T = 3                # a 1-tick buff changes nothing, 2 are enough
R_RADIUS = 30000
E_AT = 11                   # E's slam tick
QUICK_AT = 4                # ult_slam's impact frame (R's Delayed 4)


def n(x):
    return P + x


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def rm(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def flag(name, tick, **fields):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields},
            "only_to_enemy": False}


def landing(ult):
    move = [x for x in ult["effect"]["effects"] if x.get("type") == "MoveToTarget"]
    assert len(move) == 1, "R has no single MoveToTarget - the kit changed, look again"
    d = [x for x in move[0]["end_effects"] if x.get("type") == "Delayed"]
    assert len(d) == 1 and d[0]["tick"] == 4, "R's landing changed, look again"
    return d[0]["effects"]


def is_twin(x):
    return x.get("type") == "RangeEffect" and x.get("target") == "EnemyChampion"


def r_done(ult):
    return any(is_twin(x) for x in landing(ult))


def apply_r(ult):
    eff = landing(ult)
    crater = [x for x in eff if x.get("type") == "RangeEffect" and x.get("target") == "EnemyWithoutTower"]
    assert len(crater) == 1 and crater[0]["shape"] == {"Circle": {"radius": R_RADIUS}}, crater
    eff.append({"type": "RangeEffect", "shape": {"Circle": {"radius": R_RADIUS}}, "target": "EnemyChampion",
                "apply_type": "AroundCaster",
                "effects": [rm("r_combo"), flag("r_combo", R_COMBO), rm("r_refund"),
                            flag("r_refund", REFUND_T, skill_cooldown_mult=REFUND, ult_cooldown_mult=-REFUND)]})


def e_done(skill2):
    e = skill2["effect"]["effects"]
    return (skill2["start_timing"] == 1 and len(e) == 2 and e[1].get("type") == "SwitchByBuff"
            and e[1].get("buff_name") == n("r_combo"))


def apply_e(skill2):
    assert skill2["start_timing"] == E_AT, skill2["start_timing"]
    eff = skill2["effect"]["effects"]
    granite, slam = eff[0], eff[1:]
    assert granite["type"] == "SwitchByBuff" and granite["buff_name"] == n("granite"), granite
    kinds = [x["type"] for x in slam]
    assert kinds == ["Sfx", "CasterViewEffect", "RangeEffect", "RemoveCasterBuff", "AddCasterBuff"], kinds
    quick = {"type": "Combine", "effects": [
        rm("r_combo"), {"type": "CasterAnimation", "name": "ult_slam", "tick": skill2["duration"]},
        {"type": "Delayed", "tick": QUICK_AT - 1, "effects": json.loads(json.dumps(slam))}]}
    normal = {"type": "Delayed", "tick": E_AT - 1, "effects": slam}
    skill2["start_timing"] = 1
    skill2["effect"]["effects"] = [granite, {"type": "SwitchByBuff", "buff_name": n("r_combo"), "effect_buff": quick,
                                             "effect_none": normal}]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with open(lp(PATH), "rb") as f:
        raw = f.read().decode("utf-8")
    k = json.loads(raw)
    r_left, e_left = not r_done(k["ult"]), not e_done(k["skill2"])
    if a.check:
        print(f"league_malphite: R landing {'without' if r_left else 'with'} the refund + window, "
              f"E {'without' if e_left else 'with'} the quick branch")
        sys.exit(1 if r_left or e_left else 0)
    if r_left:
        apply_r(k["ult"])
    if e_left:
        apply_e(k["skill2"])
    if r_left or e_left:
        nl = "\r\n" if "\r\n" in raw else "\n"
        text = json.dumps(k, ensure_ascii=False, indent=2).replace("\n", nl) + nl
        with open(lp(PATH), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    print(f"league_malphite: R landing {'patched' if r_left else 'already patched'}, E quick branch "
          f"{'added' if e_left else 'already there'}; skill2 {len(json.dumps(k['skill2']))} B, "
          f"ult {len(json.dumps(k['ult']))} B")


if __name__ == "__main__":
    main()
