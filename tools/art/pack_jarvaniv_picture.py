"""Build the step-0 pack for Codex (assets/source/jarvaniv/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_jarvaniv_picture.py --out %TEMP%/jv_work/jarvaniv_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Garen, Pantheon and Swain at their dense frames, 8x,
cut from their sheets), then <out>.zip. Render into a short folder (%TEMP%).
Jarvan IV (the user's picks, 2026-10-17: jungle, layout A, add-on, PPU 1.5, pro combos - 「全按推荐做」) is the Demacian
prince: a gold winged helmet over a young face, gold plate with spiked pauldrons over dark navy-violet cloth, a blue
cape, and a very long silver lance with a gold-and-blue haft. League has no form change, so step 0 asks for two
pictures of the same prince for the user to pick the idle from: A = League's idle (the lance upright beside him, much
taller than he is), B = a ready stance with the lance held low and diagonally forward (the pack's spear heroes'
compact way). Helmet top to soles (the lance left out) about 72 squares of 11 px.
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
IDLE = "jarvanIV_idle1@0"
READY = "jarvanIV_attack1@444"
NO_LANCE = ["--hide-joints", "^Weapon"]
# name -> (frame, yaw, size, width, crop: "box" / "head" / (x0, y0, x1, y1) fractions of the figure's box, extra args)
RENDERS = {
    "1_jarvan_idle": (IDLE, 45, 1600, 1.2, "box", []),
    "2_jarvan_frontal": (IDLE, 0, 1600, 1.2, "box", []),
    "3_jarvan_head": (IDLE, 40, 3200, 1.0, "head", NO_LANCE),
    "4_jarvan_back": (IDLE, 200, 1600, 1.2, "box", []),
    "6_jarvan_ready": (READY, 45, 1600, 1.8, "box", []),
    "7_jarvan_lance": (IDLE, 90, 2400, 0.6, "box", ["--only-joints", "^Weapon"]),
    # uncropped, same frame and scale: the guides measure the body without the lance and place the whole figure
    "body_idle": (IDLE, 45, 1600, 1.2, "none", NO_LANCE),
    "body_ready": (READY, 45, 1600, 1.8, "none", NO_LANCE),
    "full_idle": (IDLE, 45, 1600, 1.2, "none", []),
    "full_ready": (READY, 45, 1600, 1.8, "none", []),
}
# helmet top to soles BODY_H px (72 squares of 11) on the 1536 square, soles on row SOLE, centred
BODY_H = 792
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": ("full_idle.png", "body_idle.png",
                        "A: League's idle, lance upright; helmet top to soles 792 px (72 squares of 11); layout only"),
    "8b_layout_B.png": ("full_ready.png", "body_ready.png",
                        "B: ready stance, the lance low and diagonal (shape only - hold it as the text says); layout only"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_garen.png": ("garen", "hd_idle"),
    "12_style_pantheon.png": ("pantheon", "hd_idle"),
    "13_style_swain.png": ("swain", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop, extra = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "JarvanIV",
           "--hq", "--fit-all", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame] + extra
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # helmet and face: the top 30% of the body (rendered without the lance)
        h = y1 - y0
        hx0, _, hx1, _ = _keyed(path).crop((0, y0, im.width, y0 + round(h * 0.3))).getbbox()
        m = (hx1 - hx0) // 6
        im = im.crop((hx0 - m, max(0, y0 - m), hx1 + m, y0 + round(h * 0.3)))
    elif crop == "none":
        pass
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


def guide(refs, name, spec):  # refs = the folder of the uncropped renders
    """The whole figure (lance too) scaled so the BODY (rendered without the lance at the same scale) is BODY_H tall,
    soles on SOLE, the body centred."""
    src, body, label = spec
    b = _keyed(os.path.join(refs, body))
    bb = b.getbbox()
    k = BODY_H / (bb[3] - bb[1])
    full = _keyed(os.path.join(refs, src))
    fb = full.getbbox()
    fig = full.crop(fb)
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    # the body's centre and soles inside the full figure (both crops share the render's frame up to the crop margin)
    bcx = ((bb[0] + bb[2]) / 2 - fb[0]) * k
    bsole = (bb[3] - fb[1]) * k
    x0 = round(768 - bcx)
    y0 = round(SOLE - bsole)
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - BODY_H), (1536, SOLE - BODY_H)], fill=(190, 190, 190, 255), width=1)
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
    refs, style, work = os.path.join(a.out, "refs"), os.path.join(a.out, "style"), a.out + "_measure"
    for d in (refs, style, work):
        os.makedirs(d, exist_ok=True)
    if not a.no_render:
        for name, spec in RENDERS.items():
            render(a.lol, name, spec, work if name.startswith(("body_", "full_")) else refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "JarvanIV.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/jarvaniv/skins/base/jarvanivloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_jarvan_splash.png"))
    for name, spec in GUIDES.items():
        guide(work, name, spec)
        shutil.move(os.path.join(work, name), os.path.join(refs, name))
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "jarvaniv", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
