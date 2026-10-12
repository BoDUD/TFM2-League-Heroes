"""Build the step-0 pack for Codex (assets/source/nautilus/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_nautilus_picture.py --out dist/nautilus_packs/nautilus_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the base skin - the rusty bronze
diving suit (a round helmet with glowing red portholes, a broad hunched chest, thick arms and legs, sea-green glowing
seams), the chain wound round his near arm and the huge stone anchor. Version A = League's idle (the anchor carried on
his back, its flukes arching over his helmet), version B = his fourth idle at 1.875 s (the anchor planted upright on the
ground in front of him, his hands on its shank).
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
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_nautilus_league_front": (["Nautilus_idle1@0"], 30, True, 1000, 0.62, 0.92, 1.4, None),
    "2_nautilus_league_frontal": (["Nautilus_idle1@0"], 0, True, 1000, 0.62, 0.92, 1.4, None),
    "3_nautilus_league_head": (["Nautilus_idle1@0"], 15, True, 2400, 0.62, 0.92, 1.0, (0.38, 0.57, 0.62, 0.81)),
    "4_nautilus_league_back": (["Nautilus_idle1@0"], 150, True, 1000, 0.62, 0.92, 1.4, None),
    "6_nautilus_league_run": (["Nautilus_Run@0", "Nautilus_Run@233", "Nautilus_Run@467"], 30, True, 800, 0.62, 0.92, 1.4,
                              None),
    "7_nautilus_league_actions": (["nautilus_attack3@533", "Nautilus_spell1@300", "nautilus_spell3@300",
                                   "Nautilus_spell4@475"], 30, True, 700, 0.6, 0.92, 1.5, None),
    "8_nautilus_league_idle4": (["nautilus_idle4@1875"], 60, True, 1000, 0.62, 0.88, 1.4, None),
}
SUBMESH = []
STYLE = {
    "9_style_viego.png": os.path.join(SRC, "viego", "codex_picture", "viego-model-A.png"),
    "10_style_pyke.png": os.path.join(SRC, "pyke", "codex_picture", "pyke-model-A.png"),
    "11_style_alistar.png": os.path.join(SRC, "alistar", "codex_picture", "alistar-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Nautilus",
           "--hq", "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground",
           str(ground), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out] + SUBMESH
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Nautilus.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/nautilus/skins/base/nautilusloadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_nautilus_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "nautilus", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
