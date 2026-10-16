"""Armed ults the game's AI can see a value in (the user, 2026-10-17: 「瑞文、莎弥拉、崔斯特 有问题的话也修复」).

    python tools/fix/ult_ai_value.py <hero.data_champion> [...]

Some ult slots only arm a window and the real ult goes later from other trees: league_riven (R armed 10 s, Blade of the
Exile when an enemy champion is close or at her first hit on one, the cooldown refunded unused), league_samira (R only at
S style, else armed 330 ticks and refunded), league_twistedfate (Destiny armed 10 s, the gate only when he is alone and an
ally far away is fighting). The slot itself is worth nothing to game 0.6.4's AI, which almost never picks it - a read-only
observer of its inputs (2026-10-17): Riven 0 ults in 6 games, Samira 0.3 and Twisted Fate 0.7 every 10 minutes, while most
ults go 4-12 times a game. Each slot now starts with a 1-tick shield on the caster (SHIELD, RangeEffect AllyOnlySelf): a
shield is worth its full amount to the AI (champion-data 3; league_kaisa's probe shield made her Q its favourite), it lasts
one tick, and the window, the checks and the refunds stay as they were. Run once; a slot that already has it is left alone.
league_kogmaw gets the same shield from its builder (tools/kit/build_kogmaw.py, r_ai): his R (a 1-tick lob with no
applied effects, the blast in its end_effects) was cast 0.7 times every 10 minutes after level 5.
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
