"""Amumu Q (Bandage Toss): a wider, faster, longer bandage; the dash after the stun, Lee Sin's way.

The user: "阿木木的Q技能，不知道为什么从来没有触发过眩晕，也不清楚有没有伤害 ... 贴脸q也没有触发过，只见过他靠大招控人".
In the SDK simulation the bandage held 4-6 of 8-15 throws a game and the champion it held stood still for 60 ticks; R's
stun (a RangeEffect) works in the game. What the game does differently with this projectile cannot be run here, so
the two parts no other hero in the game relies on are made like the ones that work:
- the bandage: radius 5000 -> 7000 and speed 5000 -> 6500 (the base nightmare's skillshot and league_morgana Q's
  width): the thinnest, slowest skillshot of the pack gets through less;
- the hit: damage, the stun, the wrap and its sound land at once; the dash and the pull pose start from a
  Delayed {tick: 2} in the same hit, as league_leesin Q2 does from Q1's hit (seen working in the game).
Then the user played it: "阿木木的确有点难Q中人 可以加宽一点绷带的宽度" and "长度也远一点". Radius 7000 -> 12000, cast range
62000 -> 75000 with the bandage flying 85000 (was 70000) and the dash reaching 110000 (was 90000): in 18 simulated
games 56% of the throws held a champion, now 73% (10000 and the same range: 67%); in the jungle against base
junglers (720 games) the kill difference went from -0.52 to +0.01 (+0.11 at 10000).

    python tools/fix/fix_amumu_q.py <league_amumu.data_champion>

Runs on the kit before the first fix or after it.
"""
import json
import os
import sys

RADIUS, SPEED, DASH_DELAY = 12000, 6500, 2
CAST_RANGE, LENGTH, DASH_RANGE = 75000, 85000, 110000


def main(path):
    lp = chr(92) * 2 + "?" + chr(92) + os.path.abspath(path)
    raw = open(lp, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    k = json.loads(raw)
    bandage = next(e for e in k["skill"]["effect"]["effects"]
                   if e.get("type") == "LinearProjectile" and e.get("name") == "league_amumu_q_bandage")
    applied = bandage["applied_effects"]
    kinds = [a["effect"]["type"] for a in applied]
    if kinds == ["ApAttack", "Stun", "ViewEffect", "TargetSfx", "MoveToTarget", "CasterAnimation"]:
        later = [a["effect"] for a in applied[4:]]
        applied[4:] = [{"casting_type": "Targeting", "effect": {"type": "Delayed", "tick": DASH_DELAY, "effects": later}}]
    assert [a["effect"]["type"] for a in applied] == ["ApAttack", "Stun", "ViewEffect", "TargetSfx", "Delayed"], kinds
    move = applied[4]["effect"]["effects"][0]
    assert move["type"] == "MoveToTarget"
    move["range"] = DASH_RANGE
    bandage["shape"] = {"Circle": {"radius": RADIUS}}
    bandage["speed"] = SPEED
    bandage["range"] = LENGTH
    k["skill"]["range"] = CAST_RANGE
    out = json.dumps(k, ensure_ascii=False, indent=2) + "\n"
    if nl == "\r\n":
        out = out.replace("\n", "\r\n")
    open(lp, "wb").write(out.encode("utf-8"))
    print(f"{path}: bandage radius {RADIUS}, speed {SPEED}, {LENGTH} long (cast at {CAST_RANGE}); "
          f"dash ({DASH_RANGE}) and pose {DASH_DELAY} ticks after the stun")


if __name__ == "__main__":
    main(sys.argv[1])
