#!/usr/bin/env python3
"""Xerath's step 0 pack for Codex: a pixel-art picture of him (A League's idle, B League's Arcanopulse charge).

    python tools/art/pack_xerath_picture.py --render --tmp <folder> --zip <xerath_picture_pack.zip>

--render first renders League's Xerath (skin 0) into --tmp with tools/lol/pose_ref.py --hq --mirror: front34
(Xerath_Idle1 at 0 ms, 3/4 front), frontal (more from the front: the hood, the chains and the gold seal), side
(profile: the depth of the plates and the pointed leg tips), q_charge (Xerath_Spell1 at 700 ms), chan (Xerath_channel at
300 ms, the Rite of the Arcane channel) and the load-screen art. The renders are Riot's material: they go into the zip
only (the zip goes to the user's Codex session), never into git.
Pack: refs/1-7 = League's model and art (look only), style/8-10 = the user's earlier Codex pictures (Lissandra A: a
floating mage without feet, Zilean A: a mage, Tryndamere A: the latest approved picture), PROMPT.md =
assets/source/xerath/PICTURE_PROMPT.md (Chinese summary + the English prompts for A and B). Codex delivers
outputs/xerath-picture/xerath-model-A.png and xerath-model-B.png (1024x1536 each) and a HANDOFF.md last.
"""
import argparse
import os
import subprocess
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source")
PROMPT = os.path.join(SRC, "xerath", "PICTURE_PROMPT.md")
STYLE = [(os.path.join(SRC, "lissandra", "codex_picture", "lissandra-model-A.png"), "style/8_style_lissandra.png"),
         (os.path.join(SRC, "zilean", "codex_picture", "zilean-model-A.png"), "style/9_style_zilean.png"),
         (os.path.join(SRC, "tryndamere", "codex_picture", "tryndamere-model-A.png"), "style/10_style_tryndamere.png")]
BG = np.array([225, 225, 225])
COMMON = ["--champ", "Xerath", "--hq", "--mirror", "--fit", "0.62", "--ground", "0.9", "--bg", "225,225,225",
          "--no-labels", "--width", "1.0", "--pitch", "8"]
RENDERS = [  # name, frame, extra pose_ref arguments (yaws are before --mirror's flip)
    ("front34", "Xerath_Idle1@0", ["--size", "1600", "--yaw", "45"]),
    ("frontal", "Xerath_Idle1@0", ["--size", "1600", "--yaw", "15"]),
    ("side", "Xerath_Idle1@0", ["--size", "1400", "--yaw", "100"]),
    ("q_charge", "Xerath_Spell1@700", ["--size", "1400", "--yaw", "45", "--width", "1.3"]),
    ("chan", "Xerath_channel@300", ["--size", "1400", "--yaw", "45", "--width", "1.3"]),
]
HEAD_BOX = (0.25, 0.0, 0.75, 0.22)  # fractions of the frontal render's figure box: the hood, the face, the seal


def render(tmp):
    os.makedirs(tmp, exist_ok=True)
    for name, frame, extra in RENDERS:
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py")] + COMMON +
                       ["--name", name, "--frame", frame, "--out", tmp] + extra, check=True)
    sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
    from pose_ref import read_tex  # noqa: E402
    from riot import Wad  # noqa: E402
    wad = Wad(r"D:\WeGameApps\lol\Game\DATA\FINAL\Champions\Xerath.wad.client")
    splash = read_tex(wad.read_path("ASSETS/Characters/Xerath/Skins/Base/XerathLoadScreen.tex")).convert("RGB")
    splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(tmp, "splash.png"))


def mask(im):
    a = np.asarray(im.convert("RGB")).astype(int)
    return np.abs(a - BG).sum(2) > 12


def figure(im, pad=24):
    """Crop a render to the drawn figure plus a margin."""
    ys, xs = np.nonzero(mask(im))
    return im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0),
                    min(xs.max() + pad, im.width), min(ys.max() + pad, im.height)))


def part(im, x0, y0, x1, y1):
    """A box given as fractions of the figure's bounding box."""
    ys, xs = np.nonzero(mask(im))
    w, h = xs.max() - xs.min(), ys.max() - ys.min()
    return im.crop((xs.min() + int(x0 * w), ys.min() + int(y0 * h), xs.min() + int(x1 * w), ys.min() + int(y1 * h)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--tmp", required=True, help="folder for League's renders (kept out of git)")
    ap.add_argument("--zip", required=True)
    a = ap.parse_args()
    if a.render:
        render(a.tmp)
    T = lambda n: Image.open(os.path.join(a.tmp, n + ".png"))
    full = figure(T("front34"))
    frontal = T("frontal")
    head = part(frontal, *HEAD_BOX)
    splash = T("splash")
    files = {
        "refs/1_xerath_league_front.png": full,
        "refs/2_xerath_league_frontal.png": figure(frontal),
        "refs/3_xerath_league_head.png": head.resize((head.width * 2, head.height * 2), Image.LANCZOS),
        "refs/4_xerath_league_side.png": figure(T("side")),
        "refs/5_xerath_splash.png": splash,
        "refs/6_xerath_league_q_charge.png": figure(T("q_charge")),
        "refs/7_xerath_league_r_channel.png": figure(T("chan")),
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.zip)), exist_ok=True)
    with zipfile.ZipFile(a.zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(PROMPT, "xerath_picture_pack/PROMPT.md")
        for name, im in files.items():
            path = os.path.join(a.tmp, "pack_" + os.path.basename(name))
            im.convert("RGB").save(path)
            z.write(path, "xerath_picture_pack/" + name)
        for src, name in STYLE:
            z.write(src, "xerath_picture_pack/" + name)
    print(a.zip, os.path.getsize(a.zip))
    with zipfile.ZipFile(a.zip) as z:
        for i in z.infolist():
            print(f"  {i.filename:60s} {i.file_size:>9}")


if __name__ == "__main__":
    main()
