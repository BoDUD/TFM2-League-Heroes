#!/usr/bin/env python3
"""Katarina's step-1 pack for Codex (assets/source/katarina/MODEL_PROMPTS.md): the side-on views drawn by the IMAGE
MODEL at the step-0 take's own density (league_jayce's redo route, pack_jayce_side.py).

    python tools/art/pack_katarina_side.py --out <dir>/katarina_model_pack [--no-render]

The user picked K1 (2026-10-15) at 38 game rows (PPU 1.5). The front stays Codex's K1 as drawn (squares ~12 px, read
back on its own grid); the side-on views come from the image model at the SAME scale, and every frame is brought to
PPU 1.5 only at the end (ppu_restyle crisp). Jayce's first step 1 - written cell by cell by a script - lost the look,
so this pack asks for image_gen drawings only.
  1_front_K1.png        the approved front (the look, square for square detail, size)
  2_layout.png          League's idle at yaw 75 scaled onto the canvas with K1's crown and soles lines (local render,
                        never committed): where the side view goes
  3_league_side.png     League's Katarina: the idle at yaw 75 and 90, a run frame at 80 (local render)
  4_face.png            K1's head 4x: the one face every frame keeps
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "katarina")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "kt_packs", "side_work")
GREY = (225, 225, 225)
IDLE, RUN = "katarina_idle1@0", "katarina_run@200"
CANVAS, CROWN, SOLE, MID = (1024, 1536), 699, 1509, 560   # K1: hair top, soles, the feet's middle
FACE = (440, 690, 700, 950)   # K1's head box in its 1024x1536 picture


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def render():
    """The idle mirrored (without it she shows her back) at yaw 75 and 90; the run unmirrored (mirrored she runs left)."""
    os.makedirs(WORK, exist_ok=True)
    pr = os.path.join(ROOT, "tools", "lol", "pose_ref.py")
    base = [sys.executable, pr, "--champ", "Katarina", "--hq", "--bg", "225,225,225", "--no-labels", "--size", "1000",
            "--fit", "0.62", "--ground", "0.94", "--width", "1.1", "--out", WORK]
    for name, frame, yaw, mirror in (("sd75", IDLE, 75, True), ("sd90", IDLE, 90, True), ("run80", RUN, 80, False)):
        cmd = base + ["--yaw", str(yaw), "--name", name, "--frame", frame] + (["--mirror"] if mirror else [])
        subprocess.run(cmd, check=True, capture_output=True)


def keyed(im):
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - GREY[0]) + abs(g - GREY[1]) + abs(b - GREY[2]) < 12:
                px[x, y] = (0, 0, 0, 0)
    return im


def layout():
    fig = keyed(Image.open(os.path.join(WORK, "sd75.png")))
    fig = fig.crop(fig.getbbox())
    s = (SOLE - CROWN) / fig.height
    fig = fig.resize((round(fig.width * s), round(fig.height * s)), Image.LANCZOS)
    can = Image.new("RGBA", CANVAS, GREY + (255,))
    can.alpha_composite(fig, (MID - fig.width // 2, SOLE - fig.height))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (CANVAS[0], SOLE)], fill=(230, 30, 30, 255), width=3)
    d.line([(0, CROWN), (CANVAS[0], CROWN)], fill=(30, 170, 60, 255), width=3)
    d.text((20, 20), f"hair top on the green line (y {CROWN}), soles on the red line (y {SOLE}) - layout only",
           fill=(40, 40, 40, 255))
    return can.convert("RGB")


def take_img():
    pic = Image.open(lp(os.path.join(SRC, "codex_picture", "katarina-K1.png"))).convert("RGBA")
    pic.putalpha(pic.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    can = Image.new("RGBA", pic.size, GREY + (255,))
    can.alpha_composite(pic)
    return can.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    if not a.no_render:
        render()
    take_img().save(os.path.join(out, "1_front_K1.png"))
    layout().save(os.path.join(out, "2_layout.png"))
    ims = [Image.open(os.path.join(WORK, f + ".png")) for f in ("sd75", "sd90", "run80")]
    both = Image.new("RGB", (sum(i.width for i in ims), max(i.height for i in ims)), GREY)
    x = 0
    for i in ims:
        both.paste(i, (x, 0))
        x += i.width
    both.save(os.path.join(out, "3_league_side.png"))
    face = take_img().crop(FACE)
    face.resize((face.width * 4, face.height * 4), Image.NEAREST).save(os.path.join(out, "4_face.png"))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()
