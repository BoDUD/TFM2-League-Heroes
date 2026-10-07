"""Build the step-0 pack for Codex (assets/source/twitch/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_twitch_picture.py --out D:\\TFM2-Workshop\\twitch_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, --hide-submeshes: the venom cask the skin shows only in W).
Version A = League's idle (Twitch_Base_Idle1: hunched forward, the crossbow levelled at chest height, the tail behind);
version B = the more upright stance League's attack starts from (Twitch_Base_Attack1 at 0 ms: the crossbow at the hip).
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
HEAD = (0.38, 0.12, 0.86, 0.52)   # head and shoulders in the 2000 px idle render
# name -> (frames, yaw, mirror, size, fit, ground, width, crop box as fractions or None)
RENDERS = {
    "1_twitch_league_idle": (["twitch_base_idle1@0"], 30, True, 1000, 0.75, 0.92, 1.3, None),
    "2_twitch_league_side": (["twitch_base_idle1@0"], 70, True, 1000, 0.75, 0.92, 1.3, None),
    "3_twitch_league_head": (["twitch_base_idle1@0"], 40, True, 2000, 0.8, 0.92, 1.0, HEAD),
    "4_twitch_league_back": (["twitch_base_idle1@0"], 150, True, 1000, 0.75, 0.92, 1.3, None),
    "6_twitch_league_upright": (["twitch_base_attack1@0"], 30, True, 1000, 0.75, 0.92, 1.3, None),
    "7_twitch_league_upright_side": (["twitch_base_attack1@0"], 70, True, 1000, 0.75, 0.92, 1.3, None),
    "8_twitch_league_actions": (["twitch_base_attack1@600", "twitch_base_spell4@611", "twitch_base_spell3@167",
                                 "twitch_base_run@133", "twitch_base_run@533"], 30, True, 600, 0.6, 0.88, 1.2, None),
}
STYLE = {
    "9_style_khazix.png": os.path.join(SRC, "khazix", "codex_picture", "khazix-model-B.png"),
    "10_style_pyke.png": os.path.join(SRC, "pyke", "codex_picture", "pyke-model-A.png"),
    "11_style_varus.png": os.path.join(SRC, "varus", "codex_picture", "varus-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Twitch", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", str(fit), "--ground", str(ground),
           "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, "--hide-submeshes"]
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Twitch.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("ASSETS/Characters/Twitch/Skins/Base/TwitchLoadScreen.tex".lower()))
    splash.convert("RGB").save(os.path.join(refs, "5_twitch_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "twitch", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
