r"""The Ancient Krug's particle references for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_krug.py [--out C:/t/kr_work/fxref] [--lol "D:/Riot Games/League of Legends"]

Set 18's DA_Krug18 skin bin names no texture (TFTSet18.wad.client: only his mesh), so the references are the ones his
sounds come from (tools/lol/extract_krug.py): the Rift's own Krug (Map11.wad.client, sru_krug / sru_krugmini: the
golden krug impact, dust, stone), Rammus (his Powerball roll, Defensive Ball Curl, the Soaring Slam) and Malphite (the
Granite Shield, Unstoppable Force's landing, Seismic Shard) from Champions/<name>.wad.client. Every .tex path their base
skin bins name, each written as <out>/<file stem>.png on black where it has alpha, so the grey shapes read.
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
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_krug/skins/skin0.bin"),
    (("Maps", "Shipping", "Map11.wad.client"), "data/characters/sru_krugmini/skins/skin0.bin"),
    (("Champions", "Rammus.wad.client"), "data/characters/rammus/skins/skin0.bin"),
    (("Champions", "Malphite.wad.client"), "data/characters/malphite/skins/skin0.bin"),
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/kr_work/fxref")
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
