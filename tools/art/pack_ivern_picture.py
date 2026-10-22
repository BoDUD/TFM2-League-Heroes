"""Build the step-0 pack for Codex (assets/source/ivern/PICTURE_PROMPT.md): League references of Ivern and Daisy,
layout guides and style pictures.

    python tools/art/pack_ivern_picture.py --out C:/t/iv_work/ivern_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders of Ivern and Daisy, the loading-screen art) and
<out>/refs/10a..10c (layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's Maokai,
Zyra, Lillia and Galio, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Ivern (group G, jungle at the user's pick, 2026-10-22) is the Green Father, a walking tree-man: a small round face of
pale bark with a big nose, a wide grin and small amber eyes, a huge beard of bright green leaves, two pale sage-green
ram's horns curling out to the sides, a red-capped mushroom on his crown; a brown wooden body with a leaf loincloth,
long thin branch arms (a twig with two leaves on one hand, a red apple in the other) and very long stilt legs of dark
red-brown bark that end in root feet, red berries growing on one shin. Daisy (R) is his rock golem: a big hunched body of
mossy green stones with violet-grey faces, carved spiral marks, white flowers and a green crystal on the chest, huge
stone fists, short thick legs and a clover sprout on her head; the character IvernMinion in Ivern's WAD (bind pose 236
tall against his 264, wide in the T-pose; she hunches in her idle).
Three pictures: A = his idle 3/4 front facing right, SA = his side-on facing right, D = Daisy from the front. Daisy stands
in the game as effect pictures riding on her target (league_annie's Tibbers way), which the client never mirrors (the
skill's rule "the client never mirrors an effect picture"), so she is drawn from the front. Ivern about 58 squares of
11 px from the top of his horns to the soles, Daisy about 46 (the same square size). His skin hides the brush wall and
the squirrel until an animation shows them: renders use --hide-submeshes. Yaw 0 front, 35 the 3/4 view, 75 the side.
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
HERO, DAISY = "ivern_idle1@0", "ivernminion_idle@0"
# name -> (champ, frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_ivern_idle": ("Ivern", HERO, 35, 1600, 1.2, "box"),
    "2_ivern_frontal": ("Ivern", HERO, 0, 1600, 1.2, "box"),
    "3_ivern_head": ("Ivern", HERO, 35, 3200, 1.2, "head"),
    "4_ivern_back": ("Ivern", HERO, 200, 1600, 1.2, "box"),
    "6_ivern_side": ("Ivern", HERO, 75, 1600, 1.2, "box"),
    "7_daisy_front": ("IvernMinion", DAISY, 0, 1600, 1.4, "box"),
    "8_daisy_34": ("IvernMinion", DAISY, 35, 1600, 1.4, "box"),
    "9_daisy_attack": ("IvernMinion", "ivernminion_attack1@400", 0, 1600, 1.4, "box"),
    "full_ivern": ("Ivern", HERO, 35, 1600, 1.2, "none"),
    "full_ivern_side": ("Ivern", HERO, 75, 1600, 1.2, "none"),
    "full_daisy": ("IvernMinion", DAISY, 0, 1600, 1.4, "none"),
}
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, squares tall, label)
    "10a_layout_ivern.png": ("full_ivern", 58, "A: Ivern's idle, 3/4 front; horn top to soles ~640 px (58 squares of 11)"),
    "10b_layout_ivern_side.png": ("full_ivern_side", 58, "SA: Ivern from the side, facing right; same size and ground"),
    "10c_layout_daisy.png": ("full_daisy", 46, "D: Daisy from the front; top to feet ~506 px (46 squares of 11)"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_maokai.png": ("maokai", "hd_idle"),
    "12_style_zyra.png": ("zyra", "hd_idle"),
    "13_style_lillia.png": ("lillia", "idle"),
    "14_style_galio.png": ("galio", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    champ, frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Ivern", "--hq", "--mirror", "--hide-submeshes", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the horns, the face, the leaf beard: the upper 30% of him, around the head
        h = y1 - y0
        cx = (x0 + x1) // 2
        im = im.crop((cx - round(h * 0.2), max(0, y0 - h // 30), cx + round(h * 0.2), y0 + round(h * 0.3)))
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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Ivern.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/ivern/skins/base/ivernloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_ivern_splash.png"))
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "ivern", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
