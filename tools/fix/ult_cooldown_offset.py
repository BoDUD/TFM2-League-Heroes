#!/usr/bin/env python3
"""Basic-ability cooldown cuts that cut the ult too: the same buff now carries ult_cooldown_mult = -skill_cooldown_mult.

    python tools/fix/ult_cooldown_offset.py [--check]

The engine caps every remaining cooldown at cooltime x 100 / (100 + mult) while a buff with `skill_cooldown_mult`
lasts, and caps the ult with skill_cooldown_mult + ult_cooldown_mult (.claude/skills/tfm2-hero-mod/references/
champion-data.md, "skill_cooldown_mult does not make cooldowns run faster"). So a buff meant for Q / W / E caps the
ult as well - a 2-tick refund on a hit takes the ult's remaining cooldown down with it, and a buff the ult adds itself
caps its own fresh cooldown (league_yunara, 2026-10-19: her R came back 14 s after it was cast, three transcendences in
46 s in the user's match; PR #388). `ult_cooldown_mult` is an i32: -skill_cooldown_mult on the same buff leaves the
ult as it was and the basic abilities' cut as it is.

The hand-kept kits (no tools/kit generator) whose buff is meant for the basic abilities only (README / League):
  league_fiora        league_fiora_r_cdr          R's Vitals cap Q's and W's remaining cooldowns at half; R's too
  league_twistedfate  league_twistedfate_wb_cdr   the blue card refunds Q and W; it halved R's 90 s as well
  league_kaisa        league_kaisa_w_refund       the evolved Void Seeker refunds 75% of its own cooldown
  league_masteryi     league_masteryi_highlander  R: Q and skill2 40% faster; it shortened R's own cooldown
  league_vayne        league_vayne_r              R: both skills' cooldowns halved; R's own fresh cooldown halved too
  league_varus        league_varus_refund         Blight's detonation: 13% per stack off the basic abilities (League)
                                                  - build_varus.py carries the offset too, but the shipped JSON was
                                                  post-processed after it (tools/fix/bake_caster_fx.py, varus_bake.json),
                                                  so a rebuild would undo that: the offset goes onto the JSON here
The other generated kits carry the offset in their generators (build_gragas / build_kassadin / build_nasus);
league_ezreal (League's Mystic Shot cuts every cooldown, R included) and league_samira (the takedown reset of all
three, a choice written in build_samira.py) keep theirs. Add-on copies built from these kits are rebuilt after this
(addons/league_fiora_duel, addons/league_vayne_bolts: make_override.py). Idempotent: --check exits 0 when every
listed buff already carries its offset.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEROES = {
    "league_fiora": ["league_fiora_r_cdr"],
    "league_twistedfate": ["league_twistedfate_wb_cdr"],
    "league_kaisa": ["league_kaisa_w_refund"],
    "league_masteryi": ["league_masteryi_highlander"],
    "league_vayne": ["league_vayne_r"],
    "league_varus": ["league_varus_refund"],
}
SLOTS = ("attack", "skill", "skill2", "ult")


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def buffs(o, names, out):
    """Every buff_state named in `names` with a positive skill_cooldown_mult, depth first."""
    if isinstance(o, dict):
        bs = o.get("buff_state")
        if isinstance(bs, dict) and bs.get("name") in names and bs.get("skill_cooldown_mult", 0) > 0:
            out.append(o)
        for v in o.values():
            buffs(v, names, out)
    elif isinstance(o, list):
        for v in o:
            buffs(v, names, out)
    return out


def offset(holder):
    """The buff_state with ult_cooldown_mult = -skill_cooldown_mult right after skill_cooldown_mult (keys in order)."""
    bs = holder["buff_state"]
    want = -bs["skill_cooldown_mult"]
    out = {}
    for k, v in bs.items():
        if k == "ult_cooldown_mult":
            continue
        out[k] = v
        if k == "skill_cooldown_mult":
            out["ult_cooldown_mult"] = want
    holder["buff_state"] = out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    todo = 0
    for hero, names in HEROES.items():
        path = os.path.join(ROOT, "league", "champion", f"{hero}.data_champion")
        with open(lp(path), "rb") as f:
            raw = f.read().decode("utf-8-sig")
        d = json.loads(raw)
        found = [h for slot in SLOTS for h in buffs(d[slot], set(names), [])]
        if not found:
            sys.exit(f"{hero}: no {names} buff with skill_cooldown_mult - the kit changed, look again")
        left = [h for h in found if h["buff_state"].get("ult_cooldown_mult") != -h["buff_state"]["skill_cooldown_mult"]]
        todo += len(left)
        if a.check:
            print(f"{hero}: {len(found)} buffs, {len(left)} without the offset")
            continue
        for h in left:
            offset(h)
        if left:
            nl = "\r\n" if "\r\n" in raw else "\n"
            text = json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl
            with open(lp(path), "w", encoding="utf-8", newline="") as f:
                f.write(text)
        print(f"{hero}: {len(left)} of {len(found)} buffs given ult_cooldown_mult = -skill_cooldown_mult")
    if a.check:
        sys.exit(1 if todo else 0)


if __name__ == "__main__":
    main()
