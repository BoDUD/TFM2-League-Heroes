"""league_jinx R: damage by the distance flown (League: 10% - 100%, the maximum after 1500 units; the missing-health part
is not scaled; enemies around the primary target take 80%).

    python tools/fix/parity_jinx_r.py [<worktree>] [--max-dmg 280 --max-ad 115] [--out file]

The kit is hand-written JSON. What changes, in the ult's `league_jinx_r_rocket`:
  * at the launch (the Delayed 17 that fires the rocket) the caster flags `league_jinx_r_d2..d9` are taken off and put
    on again, flag k lasting while the blast's share is 10k %; no flag left: the whole damage (also what the AI reads
    before a cast). The share is League's 10% + 90% x flown / 1500 units, at 100 of ours a unit: the rocket flies 4500
    a tick, and its wide hit circle (28000, League's is 70 units) touches a champion about 20000 sooner than League's
    would, so HITBOX is added to what it flew - a champion 52500 away (her minigun's reach, 525 in League) takes
    a third either way, one 100000 away 62%, from about 160000 the whole. The 10% step itself is never reached.
  * the blast (the zone the hidden lob's end_effects start; it hits LAG ticks after the rocket's hit) picks its
    damage by the shortest flag still up: 80% of that step's max_dmg + max_ad% AD to every enemy in it (+ 8% of its
    maximum health, the stand-in for League's missing-health part, never scaled); the unit the rocket struck takes
    the other 20% (+ 2% of its maximum health) from a Delayed LAG on it, read and dealt on the same tick.
Run again it rewrites the same nodes (idempotent).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import parity_jsonio as jsonio  # noqa: E402

ID = "league_jinx"
SPEED = 4500
FAR = 150000      # League: "The maximum damage is reached after traveling 1500 units"
STEPS = 10        # 10% .. 100%
HITBOX = 20000    # what the 28000 hit circle saves the rocket against League's 70-unit one (see above)
LAG = 2           # the blast hits two ticks after the rocket's hit (Delayed 1 -> the lob lands at once -> the zone hits a tick later)
THP = 10          # % of the target's maximum health (what the kit had; League: 25-35% of missing health)
SPLASH = 80       # League: "Enemies surrounding the primary target take 80% damage."


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in o.values():
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def share(e):
    """The share (%) for a blast read e ticks after the launch: the rocket flew about (e - LAG + 0.5) x SPEED."""
    return 10 + 90 * min(1.0, ((e - LAG + 0.5) * SPEED + HITBOX) / FAR)


def flag_ticks():
    """{k: ticks} - flag k is up while the blast's share rounds to 10k % or less; a step never reached has no flag."""
    out = {}
    for k in range(1, STEPS):
        es = [e for e in range(LAG, 200) if share(e) < 10 * k + 5]
        if es:
            out[k] = max(es) + 2   # added the tick the rocket spawns, seen on n - 1 ticks: up at the read e
    return out


def attack(dmg, ad, thp):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ad, "hp_ratio": 0, "target_hp_ratio": thp,
            "attack_effect_type": "Target"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("worktree", nargs="?", default=ROOT)
    ap.add_argument("--max-dmg", type=int, default=280)
    ap.add_argument("--max-ad", type=int, default=115)
    ap.add_argument("--out")
    a = ap.parse_args()
    path = f"{a.worktree}/league/champion/{ID}.data_champion"
    kit, meta = jsonio.load(path)
    rockets, launch = [], []

    def find(o):
        if o.get("type") == "LinearProjectile" and o.get("name") == f"{ID}_r_rocket":
            rockets.append(o)
        if o.get("type") == "Delayed" and any(isinstance(e, dict) and e.get("name") == f"{ID}_r_rocket"
                                              for e in o.get("effects", [])):
            launch.append(o)

    walk(kit["ult"], find)
    assert len(rockets) == 1 and len(launch) == 1, (len(rockets), len(launch))
    rocket, launch = rockets[0], launch[0]
    hit = rocket["applied_effects"][0]["effect"]
    assert hit["type"] == "Delayed" and hit["tick"] == 1, "the rocket's first applied effect is not the Delayed 1 lob"
    lob = hit["effects"][0]
    assert lob["type"] == "ParabolicProjectile" and lob["name"] == f"{ID}_r_drop"
    view = lob["end_effects"][0]
    assert view == {"type": "ViewEffect", "name": f"{ID}_r_blast"}
    old_zone = [e for e in lob["end_effects"] if e.get("type") == "RangeProjectile"][-1]
    radius = old_zone["shape"]["Circle"]["radius"]
    target = old_zone["applied_target"]

    def around(pct):
        return attack(round(a.max_dmg * pct * SPLASH / 10000), round(a.max_ad * pct * SPLASH / 10000), THP * SPLASH // 100)

    def prime(pct):
        return attack(round(a.max_dmg * pct / 100) - round(a.max_dmg * pct * SPLASH / 10000),
                      round(a.max_ad * pct / 100) - round(a.max_ad * pct * SPLASH / 10000), THP - THP * SPLASH // 100)

    ticks = flag_ticks()

    def ladder(make):
        node = make(100)
        for k in sorted(ticks, reverse=True):
            node = {"type": "SwitchByBuff", "buff_name": f"{ID}_r_d{k}", "effect_buff": make(10 * k), "effect_none": node}
        return node

    lob["end_effects"] = [view, {"type": "RangeProjectile", "name": f"{ID}_r_damage", "delay": 1, "apply": 1,
                                 "shape": {"Circle": {"radius": radius}}, "applied_target": target,
                                 "applied_effects": [{"casting_type": "Targeting", "effect": ladder(around)}]}]
    # the struck unit's own share, read on the blast's tick
    extra = {"casting_type": "Targeting", "effect": {"type": "Delayed", "tick": LAG, "effects": [ladder(prime)]}}
    rest = [e for e in rocket["applied_effects"][1:] if not (e["effect"].get("type") == "Delayed"
                                                               and e["effect"].get("tick") == LAG
                                                               and f"{ID}_r_d" in str(e["effect"]))]
    rocket["applied_effects"] = [rocket["applied_effects"][0], extra] + rest
    flags = [{"type": "RemoveCasterBuff", "name": f"{ID}_r_d{k}"} for k in sorted(ticks)]
    flags += [{"type": "AddCasterBuff", "buff_state": {"name": f"{ID}_r_d{k}", "duration": {"Time": {"tick": t}}},
               "only_to_enemy": False} for k, t in sorted(ticks.items())]
    keep = [e for e in launch["effects"] if not str(e.get("name", "")).startswith(f"{ID}_r_d")
            and not str(e.get("buff_state", {}).get("name", "")).startswith(f"{ID}_r_d")]
    at = next(i for i, e in enumerate(keep) if e.get("name") == f"{ID}_r_rocket")
    launch["effects"] = keep[:at] + flags + keep[at:]
    jsonio.save(a.out or path, kit, meta)
    print("flags (step: ticks)", ticks, "- shares by read tick:",
          {e: round(share(e)) for e in (2, 4, 6, 8, 10, 13, 17, 21, 24, 28, 29)})
    for pct in [10 * k for k in sorted(ticks)] + [100]:
        z, p = around(pct), prime(pct)
        print(f"  {pct:3d}%: around {z['damage']} + {z['attack_ratio']}% AD + {z['target_hp_ratio']}% max hp;"
              f" the struck unit + {p['damage']} + {p['attack_ratio']}% AD + {p['target_hp_ratio']}%"
              f" = {z['damage'] + p['damage']} + {z['attack_ratio'] + p['attack_ratio']}% AD")


if __name__ == "__main__":
    main()
