#!/usr/bin/env python3
"""Jayce's step-1 redo pack for Codex (assets/source/jayce/SIDE_PROMPTS.md): the side-on views drawn by the IMAGE MODEL
at the step-0 takes' own density.

    python tools/art/pack_jayce_side.py --out dist/jayce_packs/jayce_side_pack [--no-render]

Why: Codex's first step-1 delivery (assets/source/jayce/codex_model, 2026-10-15) was written cell by cell by a Python
script, not drawn: clean grid and one head, but the look of the picked takes lost (coat tails, emblem, fur collar gone,
the hammer shaft a blade, the cannon form's chest a gold block). The user chose Milio's route: the fronts stay Codex's
step-0 takes A2 (hammer) and B2 (cannon) as drawn (squares ~10 / ~8 px, read back on their own grid), the side-on views
come from the image model at the SAME scale as those takes, and every frame is brought to PPU 1.5 only at the end
(ppu_restyle crisp). The side angle: the user picked three quarters toward the side (take B of the script delivery).
  1_hammer_A2.png / 2_cannon_B2.png      the approved fronts (the look, square for square detail, size)
  3_hammer_layout.png / 4_cannon_layout.png   League's idle at yaw 60 scaled onto the canvas with A2's / B2's crown and
                                            soles lines (local render, never committed): where the side view goes
  5_league_side.png                       League's Jayce at yaw 60 and 75, both forms (local render)
  6_face.png                              A2's head 4x: the one face every frame keeps
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "jayce")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "jy_work", "side")
GREY = (225, 225, 225)
HAMMER, CANNON = "jayce_melee_idle1@0", "jayce_ranged_idle1@0"
# form -> (take, canvas, crown row, soles row of the take, feet middle x on the canvas, frame index in the yaw-60 render)
FORMS = {
    "hammer": ("hammer-A2", (1024, 1536), 490, 1497, 512, 0),
    "cannon": ("cannon-B2", (1536, 1024), 103, 966, 640, 1),
}
FACE = (420, 470, 740, 820)   # A2's head box in its 1024x1536 picture


def render():
    os.makedirs(WORK, exist_ok=True)
    pr = os.path.join(ROOT, "tools", "lol", "pose_ref.py")
    for yaw in (60, 75):
        cmd = [sys.executable, pr, "--champ", "Jayce", "--hq", "--bg", "225,225,225", "--no-labels", "--size", "1000",
               "--fit", "0.62", "--ground", "0.94", "--width", "1.4", "--yaw", str(yaw), "--name", f"sd{yaw}",
               "--frame", HAMMER, "--frame", CANNON, "--out", WORK]
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


def layout(form):
    take, size, crown, sole, mid, k = FORMS[form]
    strip = Image.open(os.path.join(WORK, "sd60.png"))
    cw = strip.width // 2
    fig = keyed(strip.crop((k * cw, 0, (k + 1) * cw, strip.height)))
    fig = fig.crop(fig.getbbox())
    # the man's own crown: the render's figure top is the hammer head for the hammer, the hair for the cannon
    body = fig.height * (0.80 if form == "hammer" else 1.0)
    s = (sole - crown) / body
    fig = fig.resize((round(fig.width * s), round(fig.height * s)), Image.LANCZOS)
    can = Image.new("RGBA", size, GREY + (255,))
    can.alpha_composite(fig, (mid - fig.width // 2, sole - fig.height))
    d = ImageDraw.Draw(can)
    d.line([(0, sole), (size[0], sole)], fill=(230, 30, 30, 255), width=3)
    d.line([(0, crown), (size[0], crown)], fill=(30, 170, 60, 255), width=3)
    d.text((20, 20), f"{form}: hair top on the green line (y {crown}), soles on the red line (y {sole}) - layout only",
           fill=(40, 40, 40, 255))
    return can.convert("RGB")


def take_img(name):
    pic = Image.open(os.path.join(SRC, "codex_picture", f"jayce-{name}.png")).convert("RGBA")
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
    take_img("hammer-A2").save(os.path.join(out, "1_hammer_A2.png"))
    take_img("cannon-B2").save(os.path.join(out, "2_cannon_B2.png"))
    layout("hammer").save(os.path.join(out, "3_hammer_layout.png"))
    layout("cannon").save(os.path.join(out, "4_cannon_layout.png"))
    s60, s75 = Image.open(os.path.join(WORK, "sd60.png")), Image.open(os.path.join(WORK, "sd75.png"))
    both = Image.new("RGB", (s60.width, s60.height + s75.height), GREY)
    both.paste(s60, (0, 0))
    both.paste(s75, (0, s60.height))
    both.save(os.path.join(out, "5_league_side.png"))
    face = take_img("hammer-A2").crop(FACE)
    face.resize((face.width * 4, face.height * 4), Image.NEAREST).save(os.path.join(out, "6_face.png"))
    shutil.copyfile(os.path.join(SRC, "SIDE_PROMPTS.md"), os.path.join(out, "SIDE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()
