#!/usr/bin/env python3
"""Build kayn_wall_pack.zip: the Shadow Step through a wall, drawn by Codex (assets/source/kayn/PROMPTS_WALL.md).

    python tools/art/pack_kayn_wall.py [--out DIR]

The pack holds PROMPTS_WALL.md, design/kayn_design.png, kayn_darkin_design.png, kayn_shadow_design.png (the three form
designs, 8x), refs/kayn_fx_ghost.png (the shadow step's pool as it is, 8x) and refs/kayn_wall_bodies.png (each form's
idle as usual and as the in-wall shadow the add-on draws him with, 4x on the arena colour). Written to --out (default
D:/TFM2-Workshop), local only.
"""
import argparse
import os
import shutil
import sys
import tempfile
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from preview_garen import ARENA, frames_of, load  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "kayn")
SHEETS = [("league_kayn", "league_kayn_wall"), ("league_kayn_darkin", "league_kayn_darkin_wall"),
          ("league_kayn_shadow", "league_kayn_shadow_wall")]


def bodies(path, z=4):
    W, H = 80, 64
    img = Image.new("RGBA", (W * 2, H * len(SHEETS)), ARENA)
    for r, pair in enumerate(SHEETS):
        for c, name in enumerate(pair):
            f = frames_of(load(os.path.join(ROOT, "league", "champions", name)), "idle")[0][0]
            img.alpha_composite(f, (c * W + W // 2 - f.width // 2, r * H + H // 2 - f.height // 2))
    img.resize((img.width * z, img.height * z), Image.NEAREST).save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="D:/TFM2-Workshop")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        pack = os.path.join(tmp, "kayn_wall_pack")
        os.makedirs(os.path.join(pack, "design"))
        os.makedirs(os.path.join(pack, "refs"))
        shutil.copy(os.path.join(SRC, "PROMPTS_WALL.md"), pack)
        for src, dst in (("kayn_native.png", "kayn_design.png"), ("kayn_darkin_native.png", "kayn_darkin_design.png"),
                         ("kayn_shadow_native.png", "kayn_shadow_design.png")):
            shutil.copy(os.path.join(NATIVE, src), os.path.join(pack, "design", dst))
        shutil.copy(os.path.join(SRC, "kayn_fx_ghost.png"), os.path.join(pack, "refs", "kayn_fx_ghost.png"))
        bodies(os.path.join(pack, "refs", "kayn_wall_bodies.png"))
        os.makedirs(a.out, exist_ok=True)
        out = os.path.join(a.out, "kayn_wall_pack.zip")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for d, _, files in os.walk(pack):
                for f in files:
                    p = os.path.join(d, f)
                    z.write(p, os.path.relpath(p, tmp))
        print(out)


if __name__ == "__main__":
    main()
