"""Build the step-0 pack for Codex (assets/source/viktor/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_viktor_picture.py --out dist/viktor_packs/viktor_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the current (Arcane) base skin - the
blue steel beaked mask, the gold crown, the blue shawl, the crimson cape, the twisted staff in one hand and the
mechanical arm rising from his back with its three-pronged gold claw high over his head. Version A = League's idle
(the arm raised high), version B = the arm folded close behind his shoulders (a smaller figure in the game's cell).
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
    "1_viktor_league_front": (["Idle1@0"], 30, True, 1000, 0.8, 0.92, 1.1, None),
    "2_viktor_league_frontal": (["Idle1@0"], 0, True, 1000, 0.8, 0.92, 1.1, None),
    "3_viktor_league_head": (["Idle1@0"], 15, True, 2000, 0.8, 0.92, 1.0, (0.30, 0.12, 0.72, 0.50)),
    "4_viktor_league_back": (["Idle1@0"], 150, True, 1000, 0.8, 0.92, 1.1, None),
    "6_viktor_league_run": (["Run@0", "Run@300", "Run@600"], 30, True, 800, 0.8, 0.92, 1.2, None),
    "7_viktor_league_actions": (["Attack1_B@150", "Spell1@250", "Spell2@250", "Spell3_0@300", "Spell4@400"], 30, True,
                                700, 0.75, 0.92, 1.3, None),
    "8_viktor_league_arm_low": (["Spell4_Idle@0"], 30, True, 1000, 0.8, 0.92, 1.1, None),
}
STYLE = {
    "9_style_renekton.png": os.path.join(SRC, "renekton", "codex_picture", "renekton-model-A.png"),
    "10_style_brand.png": os.path.join(SRC, "brand", "codex_picture", "brand-model-A.png"),
    "11_style_xerath.png": os.path.join(SRC, "xerath", "codex_picture", "xerath-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Viktor",
           "--hq", "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground",
           str(ground), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out]
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Viktor.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/viktor/skins/base/viktorloadscreen_0.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_viktor_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "viktor", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
