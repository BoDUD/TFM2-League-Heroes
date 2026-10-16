"""Yone's R gets a scoring branch the game's AI reads (the user, 2026-10-17: 「永恩的确不放大」).

    python tools/fix/fix_yone_r_score.py <league_yone.data_champion> [...]

In game 0.6.4 his R was never cast: a read-only observer (the AI's own input every tick, 2026-10-17) saw 5 games, 0 ults,
the ult ready with an enemy champion within 80000 for ~3600 ticks a game, the AI choosing it 0 times while the engine
called an Ult on the nearest enemy a valid input 17843 of 17880 times - the AI does not want it; the classic SDK casts it
3.7 (jungle) to 5.4 (mid) times a game. Other ults with damage only inside Delayed (Zed, Kassadin) or a line telegraph
(Akali Q) are cast, so the cause in his tree is not known. The fix does not depend on it: league_orianna's q_x / e_x
way (champion-data 8, the AI scores the branch the flags pick between ticks) -
  Combine[AddCasterBuff league_yone_r_x 1 tick, SwitchByBuff league_yone_r_x {RemoveCasterBuff r_x + the whole R as it
  was} {the R's hit straight on the target: Attack 70 + 50%, FixedAttack 50 + 35%}, RemoveCasterBuff r_x]
r_x is never there between ticks, so the AI reads the plain hit; when the slot runs the flag is up and the real R goes
(dash, line, Q3 combo, stacks, twin - unchanged). The numbers are read from the R's own first hit. The knock-up is left
out of the scoring branch: with it the classic SDK's AI cast R 7.3 times a game and died 2.7-2.8 times (kd +1.58 / +1.48
on seeds 1-16 / 17-32), with damage only 7.0-7.1 R, 2.4-2.5 deaths, +2.42 / +2.42 (unchanged kit +2.33 / +1.44, 5.0-5.2
R). Run once.
"""
import json
import os
import sys

ID = "league_yone"
X = f"{ID}_r_x"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def first_hit(effect):
    """The applied effects of the R's damaging line (LineRangeProjectile league_yone_r_hit) in the plain branch."""
    found = []

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "LineRangeProjectile" and o.get("name") == f"{ID}_r_hit":
                found.append(o)
                return
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(effect.get("effect_none", effect))
    if not found:
        raise SystemExit("no league_yone_r_hit line in the R")
    keep = ("Attack", "FixedAttack")
    return [a["effect"] for a in found[0]["applied_effects"] if a.get("effect", {}).get("type") in keep]


def main():
    for path in sys.argv[1:]:
        with open(lp(path), encoding="utf-8", newline="") as f:
            raw = f.read()
        d = json.loads(raw)
        ult = d["ult"]
        if f'"{X}"' in raw:
            print(os.path.basename(path), "already fixed")
            continue
        real = ult["effect"]
        score = first_hit(real)
        ult["effect"] = {"type": "Combine", "effects": [
            {"type": "AddCasterBuff", "buff_state": {"name": X, "duration": {"Time": {"tick": 1}}}, "only_to_enemy": False},
            {"type": "SwitchByBuff", "buff_name": X,
             "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": X}, real]},
             "effect_none": {"type": "Combine", "effects": score}},
            {"type": "RemoveCasterBuff", "name": X}]}
        crlf = "\r\n" in raw
        text = json.dumps(d, ensure_ascii=False, indent=2)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write((text.replace("\n", "\r\n") + "\r\n") if crlf else text + "\n")
        print(os.path.basename(path), "R scoring branch:", json.dumps(score))


if __name__ == "__main__":
    main()
