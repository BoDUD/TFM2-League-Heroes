"""Build the step-0 pack for Codex (assets/source/braum/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_braum_picture.py --out dist/braum_packs/braum_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground; 1-3 and 6-8 mirrored, 4 not): the base skin - a huge, broad
Freljord strongman, bald, with a big dark-brown handlebar moustache, dark brows, a teal pendant on a cord, pink skin with
mauve tribal tattoo bands, a white fur mantle over one blue-steel pauldron, a gold-rimmed steel belt disc with a ram
emblem, steel-blue bracers, dark-brown trousers, grey fur at the knees, dark boots - and his vault-door shield: a slate
slab framed in gold (a Celtic key pattern on the top bar), a dark-steel ram's head with curled horns and glowing cyan
eyes and forehead gem on the front, a wooden door with iron hinges on the back.
Version A = the shield planted on the ground in front of him (image right), version B = the shield lifted off the
ground on his far arm, ready.
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
    "1_braum_league_front": (["braum_idle_01_loop@0"], 30, True, 1000, 0.62, 0.92, 1.6, None),
    "2_braum_league_shield": (["braum_idle_01_loop@0"], 60, True, 1000, 0.62, 0.92, 1.6, None),
    "3_braum_league_head": (["braum_idle_01_loop@0"], -30, True, 2400, 0.62, 0.92, 1.0, (0.42, 0.30, 0.62, 0.50)),
    "4_braum_league_body": (["braum_idle_01_loop@0"], 30, False, 1000, 0.62, 0.92, 1.6, None),
    "6_braum_league_run": (["braum_run_02@0", "braum_run_02@267", "braum_run_02@533"], 30, True, 800, 0.62, 0.92, 1.6,
                           None),
    "7_braum_league_actions": (["braum_attack_01@425", "braum_spell1@330", "braum_spell2@300", "braum_spell4@700"], 30,
                               True, 700, 0.6, 0.92, 1.7, None),
    "8_braum_league_unbreakable": (["braum_spell3_idle0@0"], 30, True, 1000, 0.62, 0.92, 1.6, None),
}
SUBMESH = []
STYLE = {
    "9_style_kassadin.png": os.path.join(SRC, "kassadin", "codex_picture", "kassadin-model-A.png"),
    "10_style_gragas.png": os.path.join(SRC, "gragas", "codex_picture", "gragas-model-A.png"),
    "11_style_corki.png": os.path.join(SRC, "corki", "user_picture", "corki-picture-2.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Braum",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Braum.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/braum/skins/base/braumloadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_braum_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "braum", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
