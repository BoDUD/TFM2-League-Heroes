"""Build the step-0 pack for Codex (assets/source/irelia/PICTURE_PROMPT.md): League references and style pictures.

    python tools/art/pack_irelia_picture.py --out dist/irelia_packs/irelia_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders and the loading-screen art: Riot's, kept local, never
committed) and <out>/style/9..11 (this pack's approved Codex pictures), then <out>.zip.
Renders (tools/lol/pose_ref.py --hq, light grey ground, mirrored to face right): the base skin - long dark indigo hair
in a low ponytail, a silver tiara with a crest spike, silver shoulder guards with curled spikes, a crimson bodysuit and
tabard with silver plates and a cyan gem at the collar, crimson sleeves, navy leggings, crimson boots with silver knee
guards, and her floating BLADES (long curved navy-crimson-silver blades hovering round her). Version A = League's
irelia_idle_01 at 0 ms (the blades fanned out round her: one high behind her shoulder, two low at her sides; a hand
raised by her face), version B = irelia_idle_in_subtle at 500 ms (the blades folded into a compact column behind her
back: the narrow stance).
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
RENDERS = {  # clips: irelia_idle_01 / _02 / _in_subtle, run_base 0.6 s, attack_01, spell1 (Q), channel (W), spell3 (E), spell4
    "1_irelia_league_front": (["irelia_idle_01@0"], 30, True, 1000, 0.8, 0.92, 1.1, None),
    "2_irelia_league_frontal": (["irelia_idle_01@0"], 0, True, 1000, 0.8, 0.92, 1.1, None),
    "3_irelia_league_head": (["irelia_idle_01@0"], 15, True, 2000, 0.8, 0.92, 1.0, (0.38, 0.12, 0.66, 0.38)),
    "4_irelia_league_back": (["irelia_idle_01@0"], 150, True, 1000, 0.8, 0.92, 1.1, None),
    "6_irelia_league_run": (["irelia_run_base@0", "irelia_run_base@200", "irelia_run_base@400"], 30, True, 800, 0.8, 0.92,
                            1.2, None),
    "7_irelia_league_actions": (["irelia_attack_01@250", "irelia_spell1@200", "irelia_channel@300", "irelia_spell3@300",
                                 "irelia_spell4@400"], 30, True, 700, 0.75, 0.92, 1.3, None),
    "8_irelia_league_folded": (["irelia_idle_in_subtle@500"], 30, True, 1000, 0.8, 0.92, 1.1, None),
}
STYLE = {
    "9_style_seraphine.png": os.path.join(SRC, "seraphine", "codex_picture", "seraphine-model-A.png"),
    "10_style_samira.png": os.path.join(SRC, "samira", "codex_picture", "samira-model-A.png"),
    "11_style_syndra.png": os.path.join(SRC, "syndra", "codex_picture", "syndra-model-A.png"),
}


def render(lol, name, spec, out):
    frames, yaw, mirror, size, fit, ground, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Irelia",
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
    wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Irelia.wad.client"))
    splash = pose_ref.read_tex(wad.read_path("assets/characters/irelia/skins/base/irelialoadscreen.tex"))
    splash.convert("RGB").save(os.path.join(refs, "5_irelia_splash.png"))
    for name, src in STYLE.items():
        shutil.copyfile(src, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "irelia", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
