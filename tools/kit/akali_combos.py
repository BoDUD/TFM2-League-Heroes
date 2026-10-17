#!/usr/bin/env python3
"""Akali's combos (the user, 2026-10-02: "阿卡丽也帮我加点连招逻辑", after Lee Sin's).

    python tools/kit/akali_combos.py [--check]

Like tools/kit/leesin_combos.py, each combo is played by the slot whose skill it spends, shaped by flags the slot
before it left; no slot is held by a flag (the AI casts a held slot anyway, empty):
- E Q A (Shuriken Flip, Five Point Strike, Assassin's Mark): when E's dash (E2) lands on an enemy champion, Akali opens
  a window (e2_on, 120 ticks). Q cast in it throws the kunai and, 5 ticks after the fan, flings the empowered kama
  at a champion in its reach (48000) - the passive's throw at once instead of on her next attack (the attack's
  attack_p pose; Q and E2 light the ring, so it is ready; without it nothing follows).
- R E E R (Perfect Execution's all-in): E2 landing on an enemy champion between R's two dashes (r_window) sends the
  second dash through that champion 6 ticks later, instead of at the end of the 2.5 s; the window closes, so R's own
  second dash does not come again. It still counts the hits since the first dash (+25% each), the E2 hit included.
Both hang on E2's champion-only twin (its applied effects run only when E2's target is a champion). The kit file
was hand-built; the script refuses to run twice (e2_on marks a combo kit). --check only verifies the combos are in.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(ROOT, "league", "champion", "league_akali.data_champion")
P = "league_akali_"
WINDOW = 120                 # e2_on: Q cast this long after E2 lands on a champion flings the kama too
THROW = 5                    # ticks after the fan (Q's tick 10) before attack_p starts
HIT = 7                      # attack_p's throw lands 7 ticks in (the attack's own Delayed)
REACH = 48000                # the empowered attack's range (twice her 24000)
R2_AFTER = 6                 # ticks after E2's twin (E2's landing + 1) before the second dash


def n(x):
    return P + x


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


def sw(buff, yes, no=None):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no or combine()}


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": list(effects)}


def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None


def build(k):
    q, e, r, a = k["skill"], k["skill2"], k["ult"], k["attack"]
    # ---- what the combos borrow, read before anything changes
    emp = a["effect"]["effect_buff"]["effects"]       # the attack with the ring: drop it, the pose, the hit 7 later
    assert [x["type"] for x in emp] == ["RemoveCasterBuff", "CasterAnimation", "Delayed"] and emp[2]["tick"] == HIT
    pose, hit = emp[1], emp[2]["effects"]
    assert pose["name"] == "attack_p" and [x["type"] for x in hit] == ["Attack", "ApAttack", "ViewEffect", "TargetSfx",
                                                                        "SwitchByBuff"]
    second = find(r["effect"], lambda o: o.get("type") == "Combine" and any(
        x.get("type") == "CasterAnimation" and x.get("name") == "ult2" for x in o.get("effects", [])))
    assert [x["type"] for x in second["effects"]] == ["AddCasterBuff", "Sfx", "CasterAnimation", "CasterViewEffect",
                                                      "RushTime"]
    e2 = find(e["effect"], lambda o: o.get("type") == "MoveToTarget")
    twin = find(e2["end_effects"], lambda o: o.get("type") == "TargetProjectile" and o.get("name") == n("e2_twin"))
    assert twin["applied_target"] == "EnemyChampion"
    on_champ = twin["applied_effects"][0]["effect"]["effects"]
    assert [x["type"] for x in on_champ] == ["ViewEffect", "SwitchByBuff", "SwitchByBuff"]   # ring, passive, R count
    assert q["start_timing"] == 10 and q["effect"]["type"] == "Combine"

    # ---- E2 on a champion: the window for Q, and the second dash at once while R's window is open
    on_champ += [flag("e2_on", WINDOW),
                 sw("r_window", combine(unflag("r_window"), delayed(R2_AFTER, *second["effects"])))]

    # ---- Q in the window: after the fan, the kama at a champion in reach (the ring is spent)
    fling = {"type": "RandomTarget", "range": REACH, "casting_target": "EnemyChampion", "from_projectile": False,
             "effects": [unflag("p_ready"), pose, delayed(HIT, *hit)]}
    q["effect"]["effects"].append(sw("e2_on", combine(unflag("e2_on"), delayed(THROW, sw("p_ready", fling)))))
    return k


def has_combos(k):
    return n("e2_on") in json.dumps(k)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw = open(lp(KIT), "rb").read().decode("utf-8")
    k = json.loads(raw)
    if args.check:
        ok = has_combos(k)
        print("league_akali.data_champion:", "combos in" if ok else "NO combos")
        sys.exit(0 if ok else 1)
    if has_combos(k):
        sys.exit("league_akali.data_champion already has the combos")
    out = json.dumps(build(k), ensure_ascii=False, indent=2) + "\n"
    if "\r\n" in raw:
        out = out.replace("\n", "\r\n")
    open(lp(KIT), "wb").write(out.encode("utf-8"))
    print("wrote league/champion/league_akali.data_champion with E Q A and R E E R")


if __name__ == "__main__":
    main()
