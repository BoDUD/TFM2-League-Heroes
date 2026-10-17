"""Yone's R without its telegraph line, so the game's AI casts it (the user, 2026-10-17: 「永恩的确不放大」).

    python tools/fix/fix_yone_r_line.py <league_yone.data_champion> [...]

In game 0.6.4 his R was never cast. A read-only observer of the game AI's own input (2026-10-17) saw the ult ready with an
enemy champion within 80000 for ~3600 ticks a game, the AI choosing it 0 times, while an Ult on the nearest enemy was a
valid input 17843 of 17880 times; the classic SDK casts it 3.7 (jungle) to 5.4 (mid) times a game. Test builds in game,
each a few presimulated games:
  the R as a plain hit on the target                                  cast 2-17 a game (16 games)
  only the Delayed 15 line hit (damage + knock-up)                    10 in 1 game
  + the telegraph `league_yone_r_line` + the dash behind the target   0 in 12 games
  the whole R minus the telegraph (Q3 combo, marks, twin, dash kept)  24 in 4 games
  the whole R, the telegraph on `Ally` instead of enemies             0 in 3 games
  a scoring branch (league_orianna's q_x) round the whole R           0 in 4 games
The telegraph is a LineRangeProjectile with no effects (delay 34, apply 999) that only drew the line on the ground; while
an ult holds it the 0.6.4 AI does not pick the ult, whatever it targets. It goes from both branches of the R (plain and
after Q3); the picture's view_projectiles entry goes with it. Everything that hits, moves or counts is unchanged. Run once.
"""
import json
import os
import sys

NAME = "league_yone_r_line"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def main():
    for path in sys.argv[1:]:
        with open(lp(path), encoding="utf-8", newline="") as f:
            raw = f.read()
        d = json.loads(raw)
        removed = 0

        def walk(o):
            nonlocal removed
            if isinstance(o, dict):
                effs = o.get("effects")
                if isinstance(effs, list):
                    keep = [e for e in effs if not (isinstance(e, dict) and e.get("name") == NAME)]
                    removed += len(effs) - len(keep)
                    o["effects"] = keep
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(d["ult"]["effect"])
        views = d.get("view_projectiles", [])
        d["view_projectiles"] = [v for v in views if v.get("name") != NAME]
        if NAME in json.dumps(d):
            sys.exit(f"{os.path.basename(path)}: {NAME} still used outside the ult - check by hand")
        if not removed:
            print(os.path.basename(path), "already fixed")
            continue
        crlf = "\r\n" in raw
        text = json.dumps(d, ensure_ascii=False, indent=2)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write((text.replace("\n", "\r\n") + "\r\n") if crlf else text + "\n")
        print(os.path.basename(path), f"telegraph removed from {removed} place(s), {len(views) - len(d['view_projectiles'])} view")


if __name__ == "__main__":
    main()
