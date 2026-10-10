"""Build the step-0 pack for Codex (assets/source/syndra/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_syndra_picture.py --out dist/syndra_packs/syndra_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the base skin - the violet helmet with
two tall curved horns and a glowing magenta visor, long silver-white hair, violet pauldrons with gold trim, the dark
corset, clawed violet gauntlets, the long violet skirt panels and the thigh-high dark boots; she floats, toes pointing
down. Version A = League's idle1 (both arms spread low, claws open, one knee bent), version B = idle3 at 972 ms (the
near hand raised beside her head as if holding a sphere, the far arm bent in front, legs together: a narrower figure).
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
RENDERS = {  # clips: Syndra_idle1 1.97 s, Syndra_idle3 5.83 s, Syndra_run 1.87 s, spells 1-4
    "1_syndra_league_front": (["Syndra_idle1@0"], 30, True, 1000, 0.8, 0.92, 1.1, None),
    "2_syndra_league_frontal": (["Syndra_idle1@0"], 0, True, 1000, 0.8, 0.92, 1.1, None),
    "3_syndra_league_head": (["Syndra_idle1@0"], 15, True, 2000, 0.8, 0.92, 1.0, (0.32, 0.0, 0.70, 0.30)),
    "4_syndra_league_back": (["Syndra_idle1@0"], 150, True, 1000, 0.8, 0.92, 1.1, None),
    "6_syndra_league_run": (["Syndra_run@0", "Syndra_run@600", "Syndra_run@1200"], 30, True, 800, 0.8, 0.92, 1.2, None),
    "7_syndra_league_actions": (["Syndra_Attack1@400", "Syndra_spell1@300", "Syndra_spell2_pull@400",
                                 "Syndra_spell3_cast@200", "Syndra_spell4_cast@500"], 30, True, 700, 0.75, 0.92, 1.3,
                                None),
    "8_syndra_league_hand_up": (["Syndra_idle3@972"], 30, True, 1000, 0.8, 0.92, 1.1, None),
}
STYLE = {
    "9_style_seraphine.png": os.path.join(SRC, "seraphine", "codex_picture", "seraphine-model-A.png"),
    "10_style_xayah.png": os.path.join(SRC, "xayah", "codex_picture", "xayah-model-A.png"),
    "11_style_viktor.png": os.path.join(SRC, "viktor", "codex_picture", "viktor-model-B.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Syndra",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Syndra.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/syndra/skins/base/syndraloadscreen_0.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_syndra_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "syndra", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
