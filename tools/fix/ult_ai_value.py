"""An armed ult the game's AI can see a value in (league_riven; the user, 2026-10-17: 「瑞文、莎弥拉、崔斯特 有问题的话也修复」).

    python tools/fix/ult_ai_value.py <hero.data_champion> [...]

league_riven's R slot only arms a window (10 s; Blade of the Exile when an enemy champion is close or at her first hit on
one, the cooldown refunded unused) and was worth nothing to game 0.6.4's AI: a read-only observer of its inputs saw 0 ults
in 6 games, while most ults go 4-12 times a game. The slot now starts with a 1-tick shield on the caster (SHIELD,
RangeEffect AllyOnlySelf): a shield is worth its full amount to the AI (champion-data 3), it lasts one tick, and the
window, the checks and the refund stay as they were. In game: 18 ults in 4 games (3.3 every 10 minutes); the classic SDK
plays her identically. league_samira and league_twistedfate (armed slots too) did not respond to it, at 200 or 1000 -
not applied to them. Not for a slot whose casting target is often missing (league_kogmaw, champion-data 8). Run once;
a slot that already has it is left alone.
"""
import json
import os
import sys

SHIELD = 200
MARK = "ai_value"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def value():
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": 1000}}, "target": "AllyOnlySelf",
            "apply_type": "AroundCaster", "effects": [
                {"type": "Shield", "amount": SHIELD, "attack_ratio": 0, "ap_ratio": 0, "tick": 1},
                {"type": "AddCasterBuff", "buff_state": {"name": "", "duration": {"Time": {"tick": 1}}},
                 "only_to_enemy": False}]}


def main():
    for path in sys.argv[1:]:
        with open(lp(path), encoding="utf-8", newline="") as f:
            raw = f.read()
        d = json.loads(raw)
        mark = f"{d['id']}_{MARK}"
        if f'"{mark}"' in raw:
            print(os.path.basename(path), "already has the AI value")
            continue
        v = value()
        v["effects"][1]["buff_state"]["name"] = mark      # a 1-tick marker: lets a re-run see the fix
        e = d["ult"]["effect"]
        if e.get("type") == "Combine":
            e["effects"].insert(0, v)
        else:
            d["ult"]["effect"] = {"type": "Combine", "effects": [v, e]}
        crlf = "\r\n" in raw
        text = json.dumps(d, ensure_ascii=False, indent=2)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write((text.replace("\n", "\r\n") + "\r\n") if crlf else text + "\n")
        print(os.path.basename(path), f"ult starts with a 1-tick {SHIELD} shield on the caster")


if __name__ == "__main__":
    main()
