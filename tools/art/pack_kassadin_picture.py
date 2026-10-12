"""Build the step-0 pack for Codex (assets/source/kassadin/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_kassadin_picture.py --out dist/kassadin_packs/kassadin_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..12 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the base skin - a tall void mage
with a horned dark-violet helmet-mask (two glowing orange eyes, dark tendrils hanging from its jaw like a beard),
cyan-teal bare muscular chest and arms, glowing pale-cyan hands, big silver-grey bone spikes over both shoulders, dark
canisters on his back, and a long layered violet robe with silver-grey trim that falls to the ground (no legs seen).
Version A = League's idle (both hands open low, the near one turned up), version B = his Nether Blade drawn (a violet
void blade grown from his near forearm, held forward).
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
    "1_kassadin_league_front": (["kassadin_idle1@0"], 30, True, 1000, 0.62, 0.92, 1.4, None),
    "2_kassadin_league_frontal": (["kassadin_idle1@0"], 0, True, 1000, 0.62, 0.92, 1.4, None),
    "3_kassadin_league_head": (["kassadin_idle1@0"], 15, True, 2400, 0.62, 0.92, 1.0, (0.36, 0.2, 0.66, 0.48)),
    "4_kassadin_league_back": (["kassadin_idle1@0"], 150, True, 1000, 0.62, 0.92, 1.4, None),
    "6_kassadin_league_run": (["kassadin_run@0", "kassadin_run@400", "kassadin_run@800"], 30, True, 800, 0.62, 0.92, 1.4,
                              None),
    "7_kassadin_league_actions": (["kassadin_attack1@300", "kassadin_spell1@330", "kassadin_spell3@330",
                                   "kassadin_spell4@200"], 30, True, 700, 0.6, 0.92, 1.5, None),
    "8_kassadin_league_blade": (["kassadin_attack2@300"], 30, True, 1000, 0.62, 0.92, 1.4, None),
    "9_kassadin_league_side": (["kassadin_idle1@0"], 70, True, 1000, 0.62, 0.92, 1.4, None),
}
SUBMESH = []
STYLE = {
    "10_style_gragas.png": os.path.join(SRC, "gragas", "codex_picture", "gragas-model-A.png"),
    "11_style_xerath.png": os.path.join(SRC, "xerath", "codex_picture", "xerath-model-A.png"),
    "12_style_viktor.png": os.path.join(SRC, "viktor", "codex_picture", "viktor-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Kassadin",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Kassadin.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/kassadin/skins/base/kassadinloadscreen_0.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_kassadin_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "kassadin", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
