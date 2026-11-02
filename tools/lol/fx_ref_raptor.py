r"""The Crimson Raptor's particle references for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_raptor.py [--out C:/t/rp_work/fxref] [--lol "D:/Riot Games/League of Legends"]

Its set-18 bins name no texture of their own (the skin borrows the Rift's SRU_Razorbeak particles), so the references
are the Rift's raptors (Map11.wad.client: the big one's feather shot and impact, the little ones' hits) and the ones its
borrowed sounds come from (tools/lol/extract_raptor.py): Xayah, Quinn, Vayne and Jarvan IV from
Champions/<name>.wad.client. Every .tex path their base skin bins name, each written as <out>/<file stem>.png on black
where it has alpha, so the grey shapes read.
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
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_razorbeak/sru_razorbeak.bin"),
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_razorbeakmini/sru_razorbeakmini.bin"),
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_razorbeak/skins/skin0.bin"),
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_razorbeakmini/skins/skin0.bin"),
    (("Champions", "Xayah.wad.client"), "data/characters/xayah/skins/skin0.bin"),
    (("Champions", "Quinn.wad.client"), "data/characters/quinn/skins/skin0.bin"),
    (("Champions", "Vayne.wad.client"), "data/characters/vayne/skins/skin0.bin"),
    (("Champions", "JarvanIV.wad.client"), "data/characters/jarvaniv/skins/skin0.bin"),
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/rp_work/fxref")
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
