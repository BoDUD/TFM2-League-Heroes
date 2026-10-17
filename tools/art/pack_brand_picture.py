"""Build the step-0 pack for Codex (assets/source/brand/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_brand_picture.py --out D:/TFM2-Workshop/brand_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..6 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/7..9 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground): League's idle 3/4 from the front facing right (mirrored: his
chest faces his right), the same from the front, a head-and-shoulders close-up, the back, and a strip of his attack
and spells (the raised hand of version B in the attack and W). His head flames are particles, not in the mesh: the
loading-screen art (5) shows them.
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
MESH = []
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_brand_league_front": (["brand_idle1@0"], 30, True, 1000, 0.6, 0.92, 1.2, None),
    "2_brand_league_frontal": (["brand_idle1@0"], 0, True, 1000, 0.6, 0.92, 1.2, None),
    "3_brand_league_head": (["brand_idle1@0"], 20, True, 2000, 0.8, 0.92, 1.0, (0.30, 0.10, 0.70, 0.46)),
    "4_brand_league_back": (["brand_idle1@0"], 150, True, 1000, 0.6, 0.92, 1.2, None),
    "6_brand_league_actions": (["brand_attack1@250", "brand_spell1@250", "brand_spell2@300", "brand_spell3@250",
                               "brand_spell4@350"], 30, True, 600, 0.55, 0.88, 0.8, None),
}
STYLE = {
    "7_style_xerath.png": os.path.join(SRC, "xerath", "codex_picture", "xerath-model-A.png"),
    "8_style_pyke.png": os.path.join(SRC, "pyke", "codex_picture", "pyke-model-A.png"),
    "9_style_tryndamere.png": os.path.join(SRC, "tryndamere", "codex_picture", "tryndamere-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Brand", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", str(ground),
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, *MESH]
    for f in frames:
        cmd += ["--frame", f]
    if mirror:
        cmd.append("--mirror")
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop:
        im = Image.open(path)
        w, h = im.size
        im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h))).save(path)
    print(name, Image.open(path).size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    os.makedirs(refs, exist_ok=True)
    os.makedirs(style, exist_ok=True)
    for name, spec in RENDERS.items():
        render(a.lol, name, spec, refs)
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Brand.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("ASSETS/Characters/Brand/Skins/Base/BrandLoadScreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_brand_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "brand", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
