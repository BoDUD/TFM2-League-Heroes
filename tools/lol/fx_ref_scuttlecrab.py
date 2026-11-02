r"""The Scuttle Crab's particle references for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_scuttlecrab.py [--out C:/t/sc_work/fxref] [--lol "D:/Riot Games/League of Legends"]

TFT ships no skin bin for set 18's crab, so League's river crab (Map11.wad.client sru_crab: its speed shrine, its shield
and the shield breaking) and the ones its borrowed sounds come from (tools/lol/extract_scuttlecrab.py): Rek'Sai's burrow
and unburrow, Rammus's shell, Soraka's heal, Sona's haste, from Champions/<name>.wad.client.
Every .tex path their skin bins name, each written as <out>/<file stem>.png on black where it has alpha, so the grey
shapes read.
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
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_crab/skins/skin0.bin"),
    (("Champions", "RekSai.wad.client"), "data/characters/reksai/skins/skin0.bin"),
    (("Champions", "Rammus.wad.client"), "data/characters/rammus/skins/skin0.bin"),
    (("Champions", "Soraka.wad.client"), "data/characters/soraka/skins/skin0.bin"),
    (("Champions", "Sona.wad.client"), "data/characters/sona/skins/skin0.bin"),
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/sc_work/fxref")
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
