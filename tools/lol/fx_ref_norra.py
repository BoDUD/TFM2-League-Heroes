r"""Norra's own particle textures (TFT set 12) for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_norra.py [--out C:/t/nr_work/fxref]

The League client dropped set 12 (TFTSet12.wad.client is a stub), so they come from CommunityDragon's raw 14.15 tree
(assets/characters/tft12_norra/skins/base/particles/*.png, already converted from .tex). Each is written as
<out>/<name without .tft_set12>.png on black where it has alpha, so the grey shapes read.
"""
import argparse
import io
import os
import re
import urllib.request

from PIL import Image

BASE = "https://raw.communitydragon.org/14.15/game/assets/characters/tft12_norra/skins/base/particles/"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})   # urllib's own is refused
    with urllib.request.urlopen(req) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/nr_work/fxref")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = sorted(set(re.findall(r'href="([^"?/]+\.png)"', get(BASE).decode("utf-8", "replace"))))
    for name in names:
        im = Image.open(io.BytesIO(get(BASE + name))).convert("RGBA")
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.out, name.replace(".tft_set12", "")))
    print(len(names), "textures ->", a.out)


if __name__ == "__main__":
    main()
