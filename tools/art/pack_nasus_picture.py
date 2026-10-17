"""Build the step-0 pack for Codex (assets/source/nasus/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_nasus_picture.py --out %TEMP%/nas_work/nasus_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..14 (this pack's PPU 1.5-1.8 humans at their dense frames, 8x, cut from
their sheets), then <out>.zip. Render into a short folder (%TEMP%).
Nasus (the user's picks, 2026-10-17: top, layout A, add-on, PPU 1.2, R as a bigger body - 「全按推荐」) is the jackal-headed
Ascended curator: tall ears, a gold headdress and armour with teal inlays, a dark-blue loincloth, dark fur, a long staff
with a gold crescent blade. Both pictures are needed (not a pick): A = League's idle (Nasus_Base_Idle1), B = Fury of the
Sands (R) for the add-on's whole-body swap and the R casts. League's R grows the same mesh (+30-40%) inside a sandstorm
(no body of its own), so B is the same Nasus on the same square size, 1.35x taller, eyes and inlays lit. Ear tips to soles
about 72 squares of 11 px (A), about 97 (B).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "Nasus_Base_Idle1@0"
# name -> (frame, yaw, size, width, crop: "box" / (x0, y0, x1, y1) fractions of the figure's box, extra pose_ref args)
RENDERS = {
    "1_nasus_idle": (IDLE, 45, 1600, 1.8, "box", []),
    "2_nasus_frontal": (IDLE, 0, 1600, 1.6, "box", []),
    "3_nasus_head": (IDLE, 40, 3200, 1.8, "head", []),
    "4_nasus_back": (IDLE, 200, 1600, 1.8, "box", []),
    "6_nasus_r_cast": ("Nasus_Base_Spell4_Full@600", 45, 1600, 1.4, "box", []),
    "7_nasus_q_strike": ("Nasus_Spell1@300", 45, 1600, 1.6, "box", []),
}
# hair top to soles HAIR_H px (72 squares of 11) on the 1536 square, soles on row SOLE, centred
HAIR_H = 792
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": ("1_nasus_idle.png", "A: League's idle; ear tips to soles 792 px (72 squares of 11); layout only", 1.0),
    "8b_layout_B.png": ("1_nasus_idle.png", "B: the SAME squares, 1.35x taller: ear tips to soles ~1070 px (97 squares); layout only",
                        1.35),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_tahmkench.png": ("tahmkench", "hd_idle"),
    "12_style_urgot.png": ("urgot", "hd_idle"),
    "13_style_swain.png": ("swain", "hd_idle"),
    "14_style_renekton.png": ("renekton", "idle"),
}
FIT, GROUND = 0.62, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop, extra = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Nasus",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame] + extra
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the head and ears: the top quarter of the body, the staff (low, to the left) left out
        h = y1 - y0
        hx0, _, hx1, _ = _keyed(path).crop((0, y0, im.width, y0 + h // 4)).getbbox()
        m = (hx1 - hx0) // 6
        im = im.crop((hx0 - m, max(0, y0 - m), hx1 + m, y0 + round(h * 0.3)))
    elif crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    else:
        fx0, fy0, fx1, fy1 = crop
        w, h = x1 - x0, y1 - y0
        im = im.crop((round(x0 + fx0 * w), round(y0 + fy0 * h), round(x0 + fx1 * w), round(y0 + fy1 * h)))
    im.save(path)
    print(name, im.size)
    return path


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def guide(refs, name, spec, k):
    src, label, grow = spec
    k *= grow
    full = _keyed(os.path.join(refs, src))
    fig = full.crop(full.getbbox())
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0 = (1536 - fig.width) // 2
    y0 = SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, max(0, y0)))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, y0), (1536, y0)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(os.path.join(refs, name))
    print(name, "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


def cut(hero, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density)."""
    anims = json.load(open(os.path.join(CHAMPS, f"league_{hero}#anim.fanim"), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(os.path.join(CHAMPS, f"league_{hero}#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    im = im.crop(im.getbbox())
    pad = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))   # on grey like the other style pictures
    pad.alpha_composite(im, (2, 2))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(out)
    print(os.path.basename(out), pad.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--no-render", action="store_true", help="reuse the renders already in <out>/refs")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Nasus.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/nasus/skins/base/nasusloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_nasus_splash.png"))
    idle = _keyed(os.path.join(refs, "1_nasus_idle.png"))
    k = HAIR_H / idle.crop(idle.getbbox()).height
    for name, spec in GUIDES.items():
        guide(refs, name, spec, k)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "nasus", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
