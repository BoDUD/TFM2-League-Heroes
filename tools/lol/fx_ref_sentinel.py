r"""The Blue Sentinel's particle references for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_sentinel.py [--out C:/t/bg_work/fxref] [--lol "D:/Riot Games/League of Legends"]

Its set-18 bins name no texture of their own (the skin borrows the Rift's SRU_Blue particles), so the references are
the Rift's Blue Sentinel (Map11.wad.client: its fist slams, spawn ground slam, debris, the blue buff) and the ones its
borrowed sounds come from (tools/lol/extract_sentinel.py): Malphite, Ornn and Ryze from Champions/<name>.wad.client.
Every .tex path their base skin bins name, each written as <out>/<file stem>.png on black where it has alpha, so the
grey shapes read.
"""
import argparse
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

FINAL = ("Game", "DATA", "FINAL")
SOURCES = (  # (wad below FINAL, skin bin)
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_blue/skins/skin0.bin"),
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_blue/animations/skin0.bin"),
    (("Champions", "Malphite.wad.client"), "data/characters/malphite/skins/skin0.bin"),
    (("Champions", "Ornn.wad.client"), "data/characters/ornn/skins/skin0.bin"),
    (("Champions", "Ryze.wad.client"), "data/characters/ryze/skins/skin0.bin"),
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/bg_work/fxref")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    n = 0
    for wad, b in SOURCES:
        w = Wad(os.path.join(a.lol, *FINAL, *wad))
        try:
            blob = w.read_path(b)
        except KeyError:
            print("no", b)
            continue
        for p in sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.tex", blob))):
            try:
                im = pose_ref.read_tex(w.read_path(p.lower())).convert("RGBA")
            except Exception as e:   # textures the WAD does not hold
                print("skip", p, type(e).__name__)
                continue
            bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
            bg.alpha_composite(im)
            bg.convert("RGB").save(os.path.join(a.out, os.path.splitext(os.path.basename(p))[0].lower() + ".png"))
            n += 1
    print(n, "textures ->", a.out)


if __name__ == "__main__":
    main()
