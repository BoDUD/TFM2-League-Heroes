"""Kayle's stage probes (Divine Ascent at levels 5, 8 and 12) cost no health.

    python tools/fix/fix_kayle_probe.py <league_kayle.data_champion>

Each probe shields her for 3 ticks (123 / 151 / 189 against 10% of her maximum health, and 100 against a hit of 99
for the damage-amplification check) and hits herself; a hit that broke the shield spilled the rest into her health
(league_kaisa's probes did the same: 「卡莎的q有点bug 这么q消耗自己的血」; the user: 「小炮和天使一起修」, 2026-10-05).
A 1-tick soak shield of SOAK is added right after every probe shield: shields are spent in the order they are added
(SDK simulation: 23 against a 39 shield left 16, 43 cost no health with the soak behind it) and the soak is gone by
the end of the tick, so the WithShield flag read 2 ticks later sees the probe's shield alone. Kayle's hits keep their
size: her probes have no damage guard, so a smaller shield would be broken by an enemy's ordinary hit (a stage too
early). Run once; a kit that already has the soak is left as it is.
"""
import json
import sys

SOAK = 1000000
PROBE_SHIELDS = (100, 123, 151, 189)


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    d = json.loads(raw)
    added = 0
    already = 0

    def walk(node):
        nonlocal added, already
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            i = 0
            while i < len(node):
                x = node[i]
                if isinstance(x, dict) and x.get("type") == "Shield" and x.get("tick") == 3 \
                        and x.get("amount") in PROBE_SHIELDS:
                    nxt = node[i + 1] if i + 1 < len(node) else None
                    if isinstance(nxt, dict) and nxt.get("type") == "Shield" and nxt.get("amount") == SOAK:
                        already += 1
                    else:
                        node.insert(i + 1, {"type": "Shield", "amount": SOAK, "attack_ratio": 0, "ap_ratio": 0,
                                            "tick": 1})
                        added += 1
                    i += 1
                walk(x)
                i += 1

    for slot in ("attack", "skill", "skill2", "ult"):
        walk(d[slot])
    text = json.dumps(d, ensure_ascii=False, indent=2)
    if "\r\n" in raw:
        text = text.replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text + ("\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""))
    print(f"{path}: {added} soak shields added, {already} already there")


if __name__ == "__main__":
    main()
