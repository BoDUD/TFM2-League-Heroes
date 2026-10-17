"""Build the step-0 pack for Codex (assets/source/xinzhao/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_xinzhao_picture.py --out D:\\TFM2-Workshop\\xinzhao_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..7 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/8..10 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground): League's idle seen 3/4 from the front facing right (his left
side, mirrored: the chest shows), the same more from the front, a head-and-shoulders close-up, the back (the topknot's
ribbons and the spear), the loading screen, Three Talon Strike's overhead hold (Spell1_AA_03 at 700 ms: version B) and
Audacious Charge's leap (Spell3).
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
# name -> (frame, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_xinzhao_league_front": ("Idlebase@0", 60, True, 1000, 0.66, 0.9, 1.75, None),
    "2_xinzhao_league_frontal": ("Idlebase@0", 25, True, 1000, 0.66, 0.9, 1.75, None),
    "3_xinzhao_league_head": ("Idlebase@0", 40, True, 2000, 1.7, 1.55, 1.0, (0.1, 0.0, 0.9, 0.7)),
    "4_xinzhao_league_side": ("Idlebase@0", 120, False, 1000, 0.66, 0.9, 1.75, None),
    "6_xinzhao_league_q3": ("Spell1_AA_03@700", 60, True, 1000, 0.66, 0.9, 1.75, None),
    "7_xinzhao_league_e": ("Spell3@50", 60, True, 1000, 0.66, 0.9, 1.75, None),
}
STYLE = {
    "8_style_kayn.png": os.path.join(SRC, "kayn", "codex_picture", "kayn-model-A.png"),
    "9_style_twistedfate.png": os.path.join(SRC, "twistedfate", "codex_picture", "twistedfate-model-A.png"),
    "10_style_varus.png": os.path.join(SRC, "varus", "codex_picture", "varus-model-A.png"),
}


def render(lol, name, spec, out):
    frame, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "XinZhao", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", str(ground),
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, "--frame", frame]
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "XinZhao.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("ASSETS/Characters/XinZhao/Skins/Base/XinZhaoReworkLoadScreen_0.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_xinzhao_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "xinzhao", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
