r"""Kobuko's own particle textures (TFT sets 15 and 14) for the effects pack's reference sheet (Riot's art: kept local,
never committed).

    python tools/lol/fx_ref_kobuko.py [--out C:/t/kb_work/fxref] [--lol "D:/Riot Games/League of Legends"]

Read from the Riot client's TFTSet15.wad.client and TFTSet14.wad.client: every .tex path his skin bins (data/characters/
tft15_kobuko/skins/skin0.bin: the mentor's shield, stun, knock-up and slam; tft14_kobuko: the boss's second phase, his
leap and big hit) name; shared particle textures they borrow come from TFTCommon.wad.client when the set's own WAD lacks
them. Each is written as <out>/<file stem>.png on black where it has alpha, so the grey shapes read.
"""
import argparse
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

BINS = (("15", "data/characters/tft15_kobuko/skins/skin0.bin"), ("14", "data/characters/tft14_kobuko/skins/skin0.bin"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/kb_work/fxref")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    wads = {s: Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", f"TFTSet{s}.wad.client")) for s, _ in BINS}
    common = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "TFTCommon.wad.client"))
    paths = {}
    for s, b in BINS:
        try:
            blob = wads[s].read_path(b)
        except KeyError:
            print("no", b)
            continue
        for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.tex", blob):
            paths.setdefault(m.decode("latin1"), wads[s])
    n = 0
    for p, w in sorted(paths.items()):
        try:
            src = w if w.has(p.lower()) else common
            im = pose_ref.read_tex(src.read_path(p.lower())).convert("RGBA")
        except Exception as e:   # textures neither WAD holds
            print("skip", p, type(e).__name__)
            continue
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.out, os.path.splitext(os.path.basename(p))[0].lower() + ".png"))
        n += 1
    print(n, "textures ->", a.out)


if __name__ == "__main__":
    main()
