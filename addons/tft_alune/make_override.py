"""Build the add-on's copy of Alune from the tft pack (Moonfall on the nearest enemies, the full moon shared, the ring's
way back).

    python addons/tft_alune/make_override.py [--check]

Rebuilds Alune with tools/kit/build_alune.py (its parameter table P), checks that the plain build is the tft pack's
tft/champion/tft_alune.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/tft_alune/override/tft_alune.data_champion: the build
with native=1 (build_alune.py's docstring) - passive tft_alune:moon (params build_alune.NATIVE_KEYS); Moonfall only
flags q_go (the add-on drops the shards); the full moon marks r_mark<phase> and deals nothing (the add-on shares it);
the attack marks a_mark (the add-on flies the ring back, picture a_back).
Every other champion stays untouched. Run it again whenever the tft pack's Alune changes.
--check: write nothing, exit 1 when the file on disk is not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "tft_alune")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_alune as kit  # noqa: E402


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_defaults():
    """Params::default() in src/lib.rs as {key: value}."""
    src = open(os.path.join(ADDON, "src", "lib.rs"), encoding="utf-8").read()
    body = src[src.index("impl Default for Params"):]
    body = body[body.index("Self {") + 6:body.index("}")]
    return {k: int(v) for k, v in re.findall(r"(\w+):\s*(-?\d+)", body)}


def main():
    check = "--check" in sys.argv
    p = dict(kit.P)
    plain = dumps(kit.build(p))
    shipped = open(kit.lp(kit.OUT), "rb").read().decode("utf-8")
    if plain != shipped:
        sys.exit("tft/champion/tft_alune.data_champion is not build_alune.py's P: rebuild the tft pack first")
    rd = rust_defaults()
    bad = {k: (rd.get(k), p[k]) for k in kit.NATIVE_KEYS if rd.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params defaults differ from P (rust, P): {bad}")
    p["native"] = 1
    text = dumps(kit.build(p))
    out = os.path.join(ADDON, "override", "tft_alune.data_champion")
    if check:
        have = open(out, "rb").read().decode("utf-8") if os.path.isfile(out) else ""
        sys.exit(0 if have == text else "override/tft_alune.data_champion is stale: run make_override.py")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(out, len(text))


if __name__ == "__main__":
    main()
