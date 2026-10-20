r"""League's particle textures for Zyra and renders of her plants, for the effects pack's reference sheet (Riot's art:
kept local, never committed).

    python tools/lol/fx_ref_zyra.py [--lol D:\WeGameApps\lol] [--out C:/t/zy_work/fxref]

Reads (never writes) Champions/Zyra.wad.client: every base-skin particle texture her bins name (Skins/Base/Particles/
*.tex) is written as <out>/<lowercase name>.png (on black where it has no alpha, so the grey shapes read), and her three
plants - ZyraThornPlant (the Thorn Spitter), ZyraGraspingPlant (the Vine Lasher), ZyraSeed - are rendered from the front
by pose_ref.py as <out>/plant_*.png.
"""
import argparse
import io
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

PLANTS = {"plant_thorn_spitter": "ZyraThornPlant", "plant_vine_lasher": "ZyraGraspingPlant", "plant_seed": "ZyraSeed"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--out", default="C:/t/zy_work/fxref")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Zyra.wad.client"))
    skin = w.read_path("data/characters/zyra/skins/skin0.bin")
    bins = sorted(set(m.decode() for m in re.findall(rb"DATA/Characters/Zyra[A-Za-z0-9_]*/[A-Za-z0-9_]*\.bin", skin)))
    names = set()
    for p in bins:
        try:
            d = w.read_path(p.lower())
        except Exception:
            continue
        names |= {m.decode() for m in re.findall(rb"ASSETS/Characters/Zyra/Skins/Base/Particles/[A-Za-z0-9_\.\-]+\.tex", d,
                                                  re.I)}
    n = 0
    for p in sorted(names):
        try:
            im = pose_ref.read_tex(w.read_path(p.lower())).convert("RGBA")
        except Exception as e:
            print("skip", p, e)
            continue
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.out, os.path.basename(p).lower().replace(".tex", ".png")))
        n += 1
    for name, champ in PLANTS.items():
        subprocess.run([sys.executable, os.path.join(HERE, "pose_ref.py"), "--lol", a.lol, "--champ", champ, "--wad", "Zyra",
                        "--hq", "--mirror", "--bg", "225,225,225", "--no-labels", "--size", "600", "--fit", "0.8",
                        "--ground", "0.92", "--width", "1.0", "--yaw", "0", "--name", name, "--out", a.out, "--anim", "idle",
                        "--frames", "1"], check=True, capture_output=True)
        made = [f for f in os.listdir(a.out) if f.lower().startswith("zyra_") and "idle" in f.lower()]
        for f in made:
            os.replace(os.path.join(a.out, f), os.path.join(a.out, name + ".png"))
    print(n, "textures and", len(PLANTS), "plants ->", a.out)


if __name__ == "__main__":
    main()
