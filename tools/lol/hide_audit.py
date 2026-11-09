"""Which submeshes each skin really hides at first, and what pose_ref's old guess hid on top of them.

pose_ref --hide-submeshes (and poses.json "hide_submeshes": true) used to take every skin-bin string made only of
submesh names for the hide list. But a skin's material overrides name one submesh each, next to its own texture, so
parts the game draws were dropped too: Milio's backpack (the user, 2026-11-09: 「现在我们做的背后没有葫芦」), Skarner's
pincers, Volibear's leg ice, Kai'Sa's membrane, Swain's arm (and Zoe's hair, Zeri's gun, were they rendered that way).
pose_ref.hidden_submeshes now reads the bin's initialSubmeshToHide field itself. This lists, per champion, that list
and what the old guess hid beyond it, and marks the heroes here that were rendered with the guess (poses.json true,
or a tools/art script passing "--hide-submeshes"): pictures drawn from those renders may lack the parts.

    python tools/lol/hide_audit.py [--lol D:/WeGameApps/lol] [--all] [CHAMP ...]

Without --all, only the champions this repo rendered with the guess; League's renders stay local (nothing written).
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pose_ref as P  # noqa: E402
from riot import Wad  # noqa: E402


def old_guess(skin_bin, names):
    """pose_ref's hide list before 2026-11-09: every bin string made only of submesh names."""
    hide = set()
    for m in re.finditer(rb"[A-Za-z0-9_ ,]{3,}", skin_bin):
        words = [w for w in re.split(r"[ ,]+", m.group(0).decode("latin1")) if w]
        if words and all(w in names for w in words):
            hide.update(words)
    return hide


def guess_users():
    """champion (lower case) -> where this repo rendered it with the guess."""
    uses = {}
    for pj in glob.glob(os.path.join(REPO, "assets", "source", "*", "poses.json")):
        try:
            d = json.load(open(pj, encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        if d.get("hide_submeshes") is True and d.get("champ"):
            uses.setdefault(d["champ"].lower(), []).append(os.path.relpath(pj, REPO).replace("\\", "/"))
    for f in sorted(glob.glob(os.path.join(REPO, "tools", "art", "*.py"))):
        text = open(f, encoding="utf-8", errors="replace").read()
        if '"--hide-submeshes"' not in text:       # the flag itself, not a comment about it
            continue
        for champ in set(re.findall(r'"--champ",\s*"([A-Za-z]+)"', text)):
            uses.setdefault(champ.lower(), []).append("tools/art/" + os.path.basename(f))
    return uses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol", help="League install folder")
    ap.add_argument("--all", action="store_true", help="every champion whose old guess differs, rendered here or not")
    ap.add_argument("champs", nargs="*", help="only these champions (WAD names, e.g. Milio)")
    a = ap.parse_args()
    uses = guess_users()
    final = os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions")
    wads = sorted(glob.glob(os.path.join(final, "*.wad.client")))
    rows = 0
    for wad_path in wads:
        base = os.path.basename(wad_path)
        champ = base.split(".")[0]
        if base.count(".") != 2 or (a.champs and champ.lower() not in {c.lower() for c in a.champs}):
            continue                                # locale WADs (Milio.zh_CN.wad.client)
        used = uses.get(champ.lower(), [])
        if not (a.all or a.champs or used):
            continue
        try:
            w = Wad(wad_path)
            skin_bin = w.read_path(f"data/characters/{champ.lower()}/skins/skin0.bin")
            skns = sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.skn", skin_bin)))
            names = {s[0] for s in P.skn_submeshes(w.read_path(P.base_mesh(skns).lower()))}
        except Exception:  # noqa: BLE001 - a WAD without a playable skin (practice tool dummies)
            continue
        real = P.hidden_submeshes(skin_bin, names)
        old = old_guess(skin_bin, names)
        if old == real and not a.champs:
            continue
        rows += 1
        line = f"{champ}: hides {sorted(real)}"
        if old - real:
            line += f"; the old guess also hid {sorted(old - real)}"
        if real - old:
            line += f"; the old guess missed {sorted(real - old)}"
        if used:
            line += f"  <- rendered with the guess: {', '.join(used)}"
        print(line)
    print(rows, "champion(s)")


if __name__ == "__main__":
    main()
