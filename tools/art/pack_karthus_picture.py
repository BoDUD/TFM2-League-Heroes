"""Build the step-0 pack for Codex (assets/source/karthus/PICTURE_PROMPT.md): League references, layout guides and
style pictures.

    python tools/art/pack_karthus_picture.py --out C:/t/ka_work/karthus_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..13 (this pack's Malzahar, Swain and Xerath, 8x, cut from their
sheets), then <out>.zip. Render into a short folder (C:/t).
Karthus (#137, 2026-10-20) is the Deathsinger: a tall gaunt lich with grey-green dead skin drawn tight over a skull
face, glowing cyan eyes and an open singing jaw, under a tall pointed dark-steel mitre crown with crimson inlays; huge
curved dark-steel pauldrons studded with glowing cyan gems; long robes of deep crimson over layers of torn dark violet
cloth that hang to the ground in ragged strips, two violet stoles down the front, a belt with a small skull; bony
pale-green clawed hands; bare skeletal feet under the robe; in one hand a tall dark-steel staff with a cyan crystal
spear-head and a crimson collar, taller than he is.
Four pictures for the user to pick from: A = League's idle, 3/4 front facing right, the staff at full League length
(its tip far above the crown); B = the same idle with the staff SHORTENED (its tip a few squares above the crown, so
the sprite stays compact); SA / SB = A and B seen from the SIDE facing right (the base of the actions). Crown tip to
soles about 64 squares of 11 px. His model: yaw 0 is the front, 35 the 3/4 view, 75 the side.
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
IDLE = "Karthus_Idle01@0"
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_karthus_idle": (IDLE, 35, 1600, 1.4, "box"),
    "2_karthus_frontal": (IDLE, 0, 1600, 1.4, "box"),
    "3_karthus_head": (IDLE, 30, 3200, 1.4, "head"),
    "4_karthus_back": (IDLE, 200, 1600, 1.4, "box"),
    "7_karthus_side": (IDLE, 75, 1600, 1.4, "box"),
    "full_idle": (IDLE, 35, 1600, 1.4, "none"),
    "full_side": (IDLE, 75, 1600, 1.4, "none"),
}
# crown tip to soles BODY_H px (64 squares of 11) on the 1536 square, soles on row SOLE, centred on CX
BODY_H = 704
SOLE = 1390
CX = 740
GUIDES = {  # name -> (render, label)
    "8a_layout_front.png": ("full_idle", "A / B: League's idle, 3/4 front; crown tip to soles 704 px (64 squares of 11); "
                                         "B: the staff tip only a few squares above the crown"),
    "8b_layout_side.png": ("full_side", "SA / SB: the same idle from the side, facing right; same size and ground line; "
                                        "SB: the staff shortened as in B"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_malzahar.png": ("malzahar", "hd_idle"),
    "12_style_swain.png": ("swain", "hd_idle"),
    "13_style_xerath.png": ("xerath", "idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Karthus",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the crown, the face, the pauldrons' tops: from the crown tip down 36% of the body
        top = _crown(_keyed(path))
        h = y1 - top
        hx0, _, hx1, _ = _keyed(path).crop((0, top, im.width, top + round(h * 0.36))).getbbox()
        sx = _staff_x(_keyed(path))
        hx1 = min(hx1, sx - 70) if sx > (hx0 + hx1) / 2 else hx1   # leave the staff out of the close-up
        m = (hx1 - hx0) // 10
        im = im.crop((hx0 - m, max(0, top - m), hx1 + m, top + round(h * 0.36)))
    elif crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    im.save(path)
    print(name, im.size)
    return path


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def _staff_x(keyed):
    """Column of the staff: the middle of the figure's top 30 rows (only the staff reaches that high)."""
    a = np.asarray(keyed)[..., 3] > 0
    ys, xs = np.nonzero(a)
    top = ys.min()
    return int(xs[ys < top + 30].mean())


def _crown(keyed):
    """Row of the crown tip: the first row with figure pixels away from the staff."""
    a = np.asarray(keyed)[..., 3] > 0
    sx = _staff_x(keyed)
    cols = np.ones(a.shape[1], bool)
    cols[max(0, sx - 70):sx + 70] = False   # the staff and its crimson collar
    rows = np.nonzero(a[:, cols].any(axis=1))[0]
    return int(rows.min())


def guide(src, name, label):
    """The whole figure scaled so crown tip to soles is BODY_H, soles on SOLE, the body centred on CX."""
    full = _keyed(src)
    box = full.getbbox()
    crown = _crown(full)
    fig = full.crop(box)
    k = BODY_H / (box[3] - crown)
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0, y0 = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - BODY_H), (1536, SOLE - BODY_H)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (x0, y0, x0 + fig.width, y0 + fig.height),
          "staff tip above the crown", round((crown - box[1]) * k), "px")


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
            render(a.lol, name, spec, work if name.startswith("full_") else refs)
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Karthus.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/karthus/skins/base/karthusloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_karthus_splash.png"))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "karthus", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
