r"""The Rift Herald's (峡谷先锋) particle references for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_riftherald.py [--out C:/t/rh_work/fxref] [--lol "D:/Riot Games/League of Legends"]

Its own: set 16's TFT16_RiftHerald particles (TFTSet16.wad.client: the fist swipe, the slam's crack glows and ground
decal) and the Rift's Herald (Map11.wad.client: SRU_RiftHerald's charge, eye and void), the sources of its sounds
(tools/lol/extract_riftherald.py); and Cho'Gath's void (Champions/Chogath.wad.client) for the purple void shapes.
Their skin bins name few textures (the particles sit in other bins), so every bin (PROP) in each WAD is read and every
.tex path in it whose name holds one of the source's KEYS is kept; each written as <out>/<file stem>.png on black where
it has alpha, so the grey shapes read.
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
SOURCES = (  # (wad below FINAL, keys a kept texture path holds)
    (("TFTSet16.wad.client",), ("tft16_riftherald",)),
    (("Maps", "Shipping", "Map11.wad.client"), ("riftherald",)),
    (("Champions", "Chogath.wad.client"), ("chogath_base",)),
)


def bins(w):
    """Every bin in the WAD (its PROP / PTCH magic), read."""
    for h, (_off, _cs, _size, typ) in w.entries.items():
        if typ & 0xF == 2:
            continue
        try:
            b = w.read(h)
        except Exception:
            continue
        if b[:4] in (b"PROP", b"PTCH"):
            yield b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/rh_work/fxref")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    n = 0
    for wad, keys in SOURCES:
        w = Wad(os.path.join(a.lol, *FINAL, *wad))
        paths = set()
        for blob in bins(w):
            paths |= {m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.tex", blob)}
        for p in sorted(x for x in paths if any(k in x.lower() for k in keys)):
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
