"""Amumu Q (Bandage Toss): a wider, faster bandage; the dash after the stun, Lee Sin's way.

The user: "阿木木的Q技能，不知道为什么从来没有触发过眩晕，也不清楚有没有伤害 ... 贴脸q也没有触发过，只见过他靠大招控人".
In the SDK simulation the bandage held 4-6 of 8-15 throws a game and the champion it held stood still for 60 ticks; R's
stun (a RangeEffect) works in the game. What the game does differently with this projectile cannot be run here, so
the two parts no other hero in the game relies on are made like the ones that work:
- the bandage: radius 5000 -> 7000 and speed 5000 -> 6500 (the base nightmare's skillshot and league_morgana Q's
  width): the thinnest, slowest skillshot of the pack gets through less;
- the hit: damage, the stun, the wrap and its sound land at once; the dash and the pull pose start from a
  Delayed {tick: 2} in the same hit, as league_leesin Q2 does from Q1's hit (seen working in the game).

    python tools/fix/fix_amumu_q.py <league_amumu.data_champion>
"""
import json
import os
import sys

RADIUS, SPEED, DASH_DELAY = 7000, 6500, 2


def main(path):
    lp = chr(92) * 2 + "?" + chr(92) + os.path.abspath(path)
    raw = open(lp, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    k = json.loads(raw)
    bandage = next(e for e in k["skill"]["effect"]["effects"]
                   if e.get("type") == "LinearProjectile" and e.get("name") == "league_amumu_q_bandage")
    applied = bandage["applied_effects"]
    kinds = [a["effect"]["type"] for a in applied]
    assert kinds == ["ApAttack", "Stun", "ViewEffect", "TargetSfx", "MoveToTarget", "CasterAnimation"], kinds
    now = applied[:4]
    later = [a["effect"] for a in applied[4:]]
    bandage["shape"] = {"Circle": {"radius": RADIUS}}
    bandage["speed"] = SPEED
    bandage["applied_effects"] = now + [{"casting_type": "Targeting",
                                         "effect": {"type": "Delayed", "tick": DASH_DELAY, "effects": later}}]
    out = json.dumps(k, ensure_ascii=False, indent=2) + "\n"
    if nl == "\r\n":
        out = out.replace("\n", "\r\n")
    open(lp, "wb").write(out.encode("utf-8"))
    print(f"{path}: bandage radius {RADIUS}, speed {SPEED}; dash and pose {DASH_DELAY} ticks after the stun")


if __name__ == "__main__":
    main(sys.argv[1])
