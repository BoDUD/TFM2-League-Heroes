#!/usr/bin/env python3
"""Baron Nashor's spider legs, step 1: Codex redraws only the legs of the idle picture.

2026-11-07, the user with a TFT screenshot: 「还有大龙的腿应该是这样的 我们现在做的不太对 你看看要不让codex重改一下」. On 11-03
Codex was asked to add legs (「画个腿，不然怎么看出来走动」) and drew two short hind legs with ivory three-toed feet, walked
with T-Hex's leg clips; TFT's Baron stands on a ring of thin, jointed, pointed spider legs splayed out round the base of
its body. Step 1 changes the idle only (two variants, the user picks); step 2 redoes the poses and the run with the
chosen legs.

    python tools/art/pack_baronnashor_legs.py <the user's screenshot> [--crop x0,y0,x1,y1] [--out <folder>]

Writes <out>/baronnashor_legs_pack.zip with assets/source/baronnashor/LEGS_PROMPT.md and:
  refs/1_reference.png          the user's screenshot as it is (TFT's Baron on its legs)
  refs/2_reference_baron.png    the Baron cut out of it (--crop), 3x
  base/3_idle_11px.png          the in-game idle (hd/idle.png, 58 x 94) at 11 px a square on the 1254 canvas: the picture
                                to edit - its squares sit on the canvas's 11 px grid
  base/4_hips_guide.png         the same with the hips line (row 70 of 94) in cyan: everything above it stays square for
                                square; below it only the new legs; the ground line (its base, row 94) in grey
  style/5_style_skarner_run.png league_skarner's run, 8x: thin dark legs in a walk cycle (style only)
  style/6_style_elise_legs.png  league_elise's idle, 8x: thin, jointed, pointed spider legs (style only)
"""
import argparse
import io
import json
import os
import zipfile

from PIL import Image, ImageDraw

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(REPO, "assets", "source", "baronnashor")
CANVAS = 1254
PX = 11
IDLE = os.path.join(SRC, "hd", "idle.png")
HIPS_ROW = 70            # design_baronnashor_model.py: hips at row 70, the legs rows 70-94
LEFT, TOP = 28 * PX, 10 * PX   # the idle's top-left on the canvas, on the grid (centred: (1254 - 58 * 11) / 2 = 308)
GREY = (60, 60, 70, 255)


def png(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return b.getvalue()


def sprite_frames(hero, tag, count=None):
    """The hero's frames of `tag` from the main pack's sheet, in order."""
    base = os.path.join(REPO, "league", "champions", f"league_{hero}")
    sheet = Image.open(base + "#sheet.png").convert("RGBA")
    anims = json.load(open(base + "#anim.fanim", encoding="utf-8"))["anims"]
    out = []
    for f in anims[tag]["frames"][:count]:
        d = f["data"]
        out.append(sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"]))))
    return out


def strip(frames, scale=8, gap=16):
    """Frames side by side, `scale` x, bottoms on one line, on the neutral grey (style sheets: one square a pixel)."""
    h = max(f.height for f in frames) * scale
    w = sum(f.width * scale for f in frames) + gap * (len(frames) + 1)
    out = Image.new("RGBA", (w, h + 2 * gap), GREY)
    x = gap
    for f in frames:
        big = f.resize((f.width * scale, f.height * scale), Image.NEAREST)
        out.alpha_composite(big, (x, gap + h - big.height))
        x += big.width + gap
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reference", help="the user's screenshot of TFT's Baron on its legs")
    ap.add_argument("--crop", default="150,20,323,348", help="the Baron in the screenshot: x0,y0,x1,y1")
    ap.add_argument("--out", default="D:/TFM2-Workshop/baronnashor_packs")
    a = ap.parse_args()

    ref = Image.open(a.reference).convert("RGB")
    box = tuple(int(v) for v in a.crop.split(","))
    baron = ref.crop(box)
    baron = baron.resize((baron.width * 3, baron.height * 3), Image.LANCZOS)

    idle = Image.open(IDLE).convert("RGBA")
    assert idle.size == (58, 94), idle.size
    base = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    base.alpha_composite(idle.resize((58 * PX, 94 * PX), Image.NEAREST), (LEFT, TOP))
    guide = base.copy()
    d = ImageDraw.Draw(guide)
    hips = TOP + HIPS_ROW * PX
    ground = TOP + 94 * PX
    d.rectangle((0, hips - 1, CANVAS, hips + 1), fill=(0, 220, 255, 255))
    d.rectangle((0, ground, CANVAS, ground + 2), fill=(150, 150, 150, 255))

    files = {
        "refs/1_reference.png": png(ref),
        "refs/2_reference_baron.png": png(baron),
        "base/3_idle_11px.png": png(base),
        "base/4_hips_guide.png": png(guide),
        "style/5_style_skarner_run.png": png(strip(sprite_frames("skarner", "hd_run"))),
        "style/6_style_elise_legs.png": png(strip(sprite_frames("elise", "hd_idle", 1))),
        "LEGS_PROMPT.md": open(os.path.join(SRC, "LEGS_PROMPT.md"), "rb").read(),
    }
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "baronnashor_legs_pack.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    print(path, f"{len(files)} files; hips line y={hips}, ground y={ground}, idle at ({LEFT}, {TOP}) on {CANVAS}x{CANVAS}")


if __name__ == "__main__":
    main()
