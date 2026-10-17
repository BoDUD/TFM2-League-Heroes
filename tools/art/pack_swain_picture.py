"""Build the step-0 pack for Codex (assets/source/swain/PICTURE_PROMPT.md): League references, layout guides and style
pictures.

    python tools/art/pack_swain_picture.py --out %TEMP%/swa_work/swain_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders, the loading-screen art and the layout guides: Riot's,
kept local, never committed) and <out>/style/11..14 (this pack's PPU 1.5-1.8 humans at their dense frames, 8x, cut from
their sheets), then <out>.zip. Render into a short folder (%TEMP%).
Swain (the user's picks, 2026-10-17: mid, add-on, PPU 1.5) is a tall Noxian general: swept-back white hair, a long
near-black greatcoat with a crimson lining and grey trim, dark plate on the chest, a demon arm that glows crimson when he
casts. Both pictures are needed (not a pick): A = League's idle (Swain_Idle; the cane and the demon-arm overlay are
hidden submeshes there), B = Demonic Ascension (R) for the add-on's whole-body swap and the R casts. League draws B with
particles on the same mesh (no body of its own), so B is described in words, on the same scale, from his idle pose and
the cast pose Swain_DemonLand (the arm overlay shown). Hair top to soles about 72 squares of 11 px.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
GREY = (225, 225, 225)
IDLE = "Swain_Idle@0"
# name -> (frame, yaw, size, width, crop: "box" / (x0, y0, x1, y1) fractions of the figure's box, extra pose_ref args)
HIDE_ALL = ["--hide-submeshes"]            # the skin's own hidden list: the cane and the demon-arm overlay
HIDE_CANE = ["--hide-submesh", "cane"]     # the cane lies on the ground apart from him in every clip
RENDERS = {
    "1_swain_idle": (IDLE, 45, 1600, 1.0, "box", HIDE_ALL),
    "2_swain_frontal": (IDLE, 0, 1600, 1.0, "box", HIDE_ALL),
    "3_swain_head": (IDLE, 40, 3200, 1.0, (0.25, 0.0, 0.95, 0.3), HIDE_ALL),
    "4_swain_back": (IDLE, 200, 1600, 1.0, "box", HIDE_ALL),
    "6_swain_demon_cast": ("Swain_DemonLand@900", 45, 1600, 1.6, "box", HIDE_CANE),
    "7_swain_demon_arm": ("Swain_Spell1@250", 45, 1600, 1.4, "box", HIDE_CANE),
}
# hair top to soles HAIR_H px (72 squares of 11) on the 1536 square, soles on row SOLE, centred
HAIR_H = 792
SOLE = 1390
GUIDES = {
    "8a_layout_A.png": ("1_swain_idle.png", "A: League's idle; hair top to soles 792 px (72 squares of 11); layout only"),
    "8b_layout_B.png": ("1_swain_idle.png", "B: the same man on the same scale; the wings spread out round him; layout only"),
}
WING_W, WING_UP = 1250, 220
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_vladimir.png": ("vladimir", "hd_idle"),
    "12_style_pantheon.png": ("pantheon", "hd_idle"),
    "13_style_morgana.png": ("morgana", "hd_idle"),
    "14_style_katarina.png": ("katarina", "hd_idle"),
}
FIT, GROUND = 0.62, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop, extra = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Swain",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out,
           "--frame", frame] + extra
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "box":
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
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - GREY[0]) + abs(g - GREY[1]) + abs(b - GREY[2]) < 12:
                px[x, y] = (0, 0, 0, 0)
    return im


def guide(refs, name, spec, k):
    src, label = spec
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
    if name.startswith("8b"):   # where the wings may reach: WING_W wide, WING_UP above the hair, down to the soles
        cx = 768
        box = (cx - WING_W // 2, y0 - WING_UP, cx + WING_W // 2, SOLE)
        for i in range(box[0], box[2], 24):
            d.line([(i, box[1]), (i + 12, box[1])], fill=(120, 120, 120, 255), width=2)
        for j in range(box[1], box[3], 24):
            d.line([(box[0], j), (box[0], j + 12)], fill=(120, 120, 120, 255), width=2)
            d.line([(box[2], j), (box[2], j + 12)], fill=(120, 120, 120, 255), width=2)
        d.text((box[0] + 8, box[1] + 8), "wings reach at most this box (1250 px wide, 220 px above the hair)",
               fill=(60, 60, 60, 255))
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Swain.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/swain/skins/base/swainloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 2, splash.height * 2), Image.LANCZOS).save(os.path.join(refs, "5_swain_splash.png"))
    idle = _keyed(os.path.join(refs, "1_swain_idle.png"))
    k = HAIR_H / idle.crop(idle.getbbox()).height
    for name, spec in GUIDES.items():
        guide(refs, name, spec, k)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "swain", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
