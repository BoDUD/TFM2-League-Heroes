"""Level probes kept out of the game AI's view (league_kaisa, 2026-10-16: a player 「kaisa doesn't auto for some reason she
just spams abilities」).

    python tools/fix/hide_probes.py <hero.data_champion> [...]

A level probe (the stage checks of league_kaisa / league_kayle / league_tristana: a hit on herself under a 99% cut
against a probe shield, a 1-tick soak shield of 1000000 behind it - tools/fix/fix_kayle_probe.py) sits in the slot's
tree as `SwitchByBuff <id>_probe_shielded` whose `effect_none` runs the probe. Game 0.6.x reads every slot between ticks
(champion-data 8: Combine, Delayed, RangeEffect ... add their children up, SwitchByBuff takes the branch the caster's
buffs pick) and a shield is worth its full amount, so Kai'Sa's Q read as a 1000000 shield. The branch now runs in
`unseen` (league_viktor's way, tools/kit/build_viktor.py): Combine[AddCasterBuff <id>_pr_go 1 tick, SwitchByBuff
<id>_pr_go {probe}, RemoveCasterBuff <id>_pr_go] - applied at once, the flag never there between ticks. Run once; a
probe already wrapped is left as it is.
"""
import json
import os
import sys


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def unseen(go, effect):
    return {"type": "Combine", "effects": [
        {"type": "AddCasterBuff", "buff_state": {"name": go, "duration": {"Time": {"tick": 1}}}, "only_to_enemy": False},
        {"type": "SwitchByBuff", "buff_name": go, "effect_buff": effect, "effect_none": {"type": "Combine", "effects": []}},
        {"type": "RemoveCasterBuff", "name": go}]}


def wrapped(effect, go):
    e = effect.get("effects") if isinstance(effect, dict) else None
    return bool(e) and e[0].get("type") == "AddCasterBuff" and e[0].get("buff_state", {}).get("name") == go


def main():
    for path in sys.argv[1:]:
        with open(lp(path), encoding="utf-8", newline="") as f:
            raw = f.read()
        d = json.loads(raw)
        go = d["id"] + "_pr_go"
        done = already = 0

        def walk(node):
            nonlocal done, already
            if isinstance(node, dict):
                if node.get("type") == "SwitchByBuff" and str(node.get("buff_name", "")).endswith("_probe_shielded"):
                    if wrapped(node["effect_none"], go):
                        already += 1
                    else:
                        node["effect_none"] = unseen(go, node["effect_none"])
                        done += 1
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(d)
        if done:
            crlf = "\r\n" in raw
            text = json.dumps(d, ensure_ascii=False, indent=2)
            with open(lp(path), "w", encoding="utf-8", newline="") as f:
                f.write((text.replace("\n", "\r\n") + "\r\n") if crlf else text + "\n")
        print(f"{os.path.basename(path)}: {done} probes hidden, {already} already")


if __name__ == "__main__":
    main()
