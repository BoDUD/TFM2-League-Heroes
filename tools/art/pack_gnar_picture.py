"""Build the step-0 pack for Codex (assets/source/gnar/PICTURE_PROMPT.md): League references of both forms, layout
guides and style pictures.

    python tools/art/pack_gnar_picture.py --out C:/t/gn_work/gnar_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (League renders of Mini Gnar and Mega Gnar, the loading-screen art and
the layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's Ziggs, Yuumi, Volibear and
Cho'Gath, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Gnar (#141, 2026-10-20) is the Missing Link, two forms:
  Mini Gnar - a tiny orange furry yordle cub: huge pointed ears (orange fur, violet-pink inside, blue tips), big dark
  round eyes, a pink nose, a small fang, a bone skull cap worn on his head (a small animal skull with a crossed bone),
  a dark brown leather loincloth and shoulder fur wrap, an orange bushy tail fading to blue at its tip, small clawed
  feet; he carries a big bone boomerang wrapped with brown leather.
  Mega Gnar - the same Gnar grown into a huge hunched beast: deep crimson-red fur with spiky electric-blue fur crests
  along the back, head and arms, two big curved ivory tusks, a wide fanged mouth, glowing yellow-orange eyes, the small
  skull still on his brow, huge clawed fists with dark grey-violet knuckles and claws, a spiky blue-red tail.
Both are characters in Gnar.wad.client: Gnar and GnarBig (--champ GnarBig --wad Gnar). Four pictures: A = Mini's idle
3/4 front facing right, SA = Mini side-on facing right, M = Mega's idle 3/4 front facing right, SM = Mega side-on
facing right. Mini about 46 squares of 11 px from the top (the skull cap) to the soles, Mega about 66 (both forms on the same
square size, so they keep their sizes against each other). Yaw 0 front, 35 the 3/4 view, 75 the side.
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
MINI, MEGA = "gnar_idle1@0", "gnarbig_idle1_base@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_mini_idle": ("Gnar", MINI, 35, 1600, 1.4, "box"),
    "2_mini_frontal": ("Gnar", MINI, 0, 1600, 1.4, "box"),
    "3_mini_head": ("Gnar", MINI, 35, 3200, 1.4, "head"),
    "4_mini_side": ("Gnar", MINI, 75, 1600, 1.4, "box"),
    "5_mega_idle": ("GnarBig", MEGA, 35, 1600, 1.6, "box"),
    "6_mega_frontal": ("GnarBig", MEGA, 0, 1600, 1.6, "box"),
    "7_mega_head": ("GnarBig", MEGA, 35, 3200, 1.6, "head"),
    "8_mega_side": ("GnarBig", MEGA, 75, 1600, 1.6, "box"),
    "full_mini": ("Gnar", MINI, 35, 1600, 1.4, "none"),
    "full_mini_side": ("Gnar", MINI, 75, 1600, 1.4, "none"),
    "full_mega": ("GnarBig", MEGA, 35, 1600, 1.6, "none"),
    "full_mega_side": ("GnarBig", MEGA, 75, 1600, 1.6, "none"),
}
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall, label)
    "10a_layout_mini.png": ("full_mini", 46, "A: Mini Gnar's idle, 3/4 front; top to soles 506 px (46 squares of 11)"),
    "10b_layout_mini_side.png": ("full_mini_side", 46, "SA: Mini Gnar from the side, facing right; same size and ground"),
    "10c_layout_mega.png": ("full_mega", 66, "M: Mega Gnar's idle, 3/4 front; top to soles 726 px (66 squares of 11)"),
    "10d_layout_mega_side.png": ("full_mega_side", 66, "SM: Mega Gnar from the side, facing right; same size and ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_ziggs.png": ("ziggs", "hd_idle"),
    "12_style_yuumi.png": ("yuumi", "hd_idle"),
    "13_style_volibear.png": ("volibear", "hd_idle"),
    "14_style_chogath.png": ("chogath", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Gnar", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", str(size),
           "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name,
           "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":
        w, h = x1 - x0, y1 - y0
        if champ == "GnarBig":   # the head sits low at the front (image right): crest, skull, eyes, tusks, mouth
            im = im.crop((x0 + round(w * 0.42), max(0, y0 - h // 30), min(im.width, x1 + w // 30), y0 + round(h * 0.8)))
        else:                    # the ears, the skull cap, the face: the top half round the head
            half = round(max(w * 0.3, h * 0.35))
            cx = (x0 + x1) // 2
            im = im.crop((max(0, cx - half), max(0, y0 - h // 30), min(im.width, cx + half), y0 + round(h * 0.55)))
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


def guide(src, name, squares, label):
    """The whole figure scaled so its top to its soles is `squares` x SQ px, soles on SOLE, centred on CX."""
    full = _keyed(src)
    fig = full.crop(full.getbbox())
    k = squares * SQ / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    x0, y0 = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (x0, y0))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, SOLE - squares * SQ), (1536, SOLE - squares * SQ)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Gnar.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/gnar/skins/base/gnarloadscreen.tex")).convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "9_gnar_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "gnar", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
