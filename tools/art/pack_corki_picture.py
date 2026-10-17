"""Build the step-0 pack for Codex (assets/source/corki/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_corki_picture.py --out dist/corki_packs/corki_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..12 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the base skin - a yordle pilot (brown
leather helmet with yellow goggles, a spike and a red plume on top, a huge white handlebar moustache, a red scarf, a
green flight suit) sitting in a steel-blue gyrocopter shaped like a toothed monster head (gold lamp eyes, a gatling gun
in its mouth), two wooden propellers on poles above, swept steel wings, red-tipped thrusters behind and two
yellow-and-red bombs with fins hanging under it; he never walks. Version A = League's idle at 3/4 front (the nose and
the gun toward image right), version B = the same nearer the side (the plane's profile, the base of every action).
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
    "1_corki_league_front": (["corki_idle1@0"], 30, True, 1000, 0.62, 0.92, 1.4, None),
    "2_corki_league_frontal": (["corki_idle1@0"], 0, True, 1000, 0.62, 0.92, 1.4, None),
    "3_corki_league_head": (["corki_idle1@0"], 15, True, 2400, 0.62, 0.92, 1.0, (0.36, 0.2, 0.68, 0.52)),
    "4_corki_league_back": (["corki_idle1@0"], 150, True, 1000, 0.62, 0.92, 1.4, None),
    "6_corki_league_run": (["corki_run@0", "corki_run@333", "corki_run@666"], 30, True, 800, 0.62, 0.92, 1.4, None),
    "7_corki_league_actions": (["corki_attack1@300", "corki_spell1@330", "corki_spell3@300", "corki_spell4@200"], 30,
                               True, 700, 0.5, 0.95, 1.5, None),
    "8_corki_league_side_b": (["corki_idle1@0"], 55, True, 1000, 0.62, 0.92, 1.4, None),
    "9_corki_league_side": (["corki_idle1@0"], 75, True, 1000, 0.62, 0.92, 1.4, None),
}
SUBMESH = []
STYLE = {
    "10_style_gragas.png": os.path.join(SRC, "gragas", "codex_picture", "gragas-model-A.png"),
    "11_style_viktor.png": os.path.join(SRC, "viktor", "codex_picture", "viktor-model-A.png"),
    "12_style_zeri.png": os.path.join(SRC, "zeri", "codex_picture", "zeri-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Corki",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Corki.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/corki/skins/base/corkiloadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_corki_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "corki", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
