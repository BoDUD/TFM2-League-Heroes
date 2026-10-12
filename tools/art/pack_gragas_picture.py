"""Build the step-0 pack for Codex (assets/source/gragas/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_gragas_picture.py --out dist/gragas_packs/gragas_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/10..12 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the base skin - a huge round-bellied
brawler, pale skin with scars, a long braided ginger beard, bald head, short dark-blue ragged shorts, bare feet, a thick
rope across his chest holding a big iron-banded wooden keg on his back. Version A = League's idle (the keg slung on his
back, its lid with the cork turned toward the viewer), version B = his W drink (the keg hoisted onto his shoulder, his
mouth at the bung).
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
    "1_gragas_league_front": (["gragas_idle1@0"], 30, True, 1000, 0.62, 0.92, 1.4, None),
    "2_gragas_league_frontal": (["gragas_idle1@0"], 0, True, 1000, 0.62, 0.92, 1.4, None),
    "3_gragas_league_head": (["gragas_idle1@0"], 15, True, 2400, 0.62, 0.92, 1.0, (0.36, 0.28, 0.66, 0.56)),
    "4_gragas_league_back": (["gragas_idle1@0"], 150, True, 1000, 0.62, 0.92, 1.4, None),
    "6_gragas_league_run": (["gragas_run@0", "gragas_run@187", "gragas_run@373"], 30, True, 800, 0.62, 0.92, 1.4, None),
    "7_gragas_league_actions": (["gragas_attack1@427", "gragas_spell1@400", "gragas_spell3@347", "gragas_spell4@600"],
                                30, True, 700, 0.6, 0.92, 1.5, None),
    "8_gragas_league_drink": (["gragas_spell2_loop@147"], 30, True, 1000, 0.62, 0.92, 1.4, None),
    "9_gragas_league_side": (["gragas_idle1@0"], 70, True, 1000, 0.62, 0.92, 1.4, None),
}
SUBMESH = []
STYLE = {
    "10_style_nautilus.png": os.path.join(SRC, "nautilus", "codex_picture", "nautilus-model-A.png"),
    "11_style_alistar.png": os.path.join(SRC, "alistar", "codex_picture", "alistar-model-A.png"),
    "12_style_tryndamere.png": os.path.join(SRC, "tryndamere", "codex_picture", "tryndamere-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Gragas",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Gragas.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/gragas/skins/base/gragasloadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_gragas_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "gragas", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
