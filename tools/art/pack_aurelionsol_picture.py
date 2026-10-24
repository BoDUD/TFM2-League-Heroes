"""Build the step-0 pack for Codex (assets/source/aurelionsol/PICTURE_PROMPT.md): League references of Aurelion Sol,
layout guides and style pictures.

    python tools/art/pack_aurelionsol_picture.py --out C:/t/as_work/aurelionsol_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders of Aurelion Sol, the loading-screen art) and <out>/refs/9a..9b
(layout guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Shyvana's dragon, Smolder, Vel'Koz
and Zoe, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Aurelion Sol (group I, mid, 2026-10-24) is the Star Forger: a cosmic dragon floating upright, a pale blue-white bony face with
a gold crown-helm and gold horn sweeping back, a magenta-violet mane, a deep navy scaled body with cyan glowing lines and
gold studs, purple clawed arms with gold bracers. His mesh ends in a short spiked stub below the chest: the long tail is a
nebula drawn by particles (the loading-screen art, image 5), so the prompt describes it and the renders do not show it.
Two pictures: A = his hovering idle, B = his astral flight (W), both 3/4 front facing right. Every render frames on all
vertices (--fit-all), so the two guides share one scale: about 42 squares of 11 px from the crest top to the body stub in A;
the nebula tail adds below. Yaw 0 front, 35 the 3/4 view.
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
IDLE = "aurelionsol_idle1@0"
FLY = "aurelionsol_spell2_rgt90_2run@200"
PROPS = []
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none", props)
RENDERS = {
    "1_aurelionsol_idle": (IDLE, 35, 1600, 1.4, "box", PROPS),
    "2_aurelionsol_frontal": (IDLE, 0, 1600, 1.4, "box", PROPS),
    "3_aurelionsol_head": (IDLE, 35, 3200, 1.4, "head", PROPS),
    "4_aurelionsol_back": (IDLE, 200, 1600, 1.4, "box", PROPS),
    "6_aurelionsol_fly": (FLY, 35, 1600, 1.6, "box", PROPS),
    "7_aurelionsol_breath": ("aurelionsol_spell1_loop@1000", 35, 1600, 1.4, "box", PROPS),
    "8_aurelionsol_star": ("aurelionsol_spell4_calamity@900", 35, 1600, 1.4, "box", PROPS),
    "full_aurelionsol_idle": (IDLE, 35, 1600, 1.4, "none", PROPS),
    "full_aurelionsol_fly": (FLY, 35, 1600, 1.6, "none", PROPS),
}
HEAD_FRAC = 0.42   # the head close-up: the crown-helm and horn, the face and the mane
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label); both drawn at the scale that makes A's crest top to body stub ANCHOR squares
    "9a_layout_aurelionsol.png": ("full_aurelionsol_idle", "A: hovering idle, 3/4 front; crest top to body stub ~462 px (42 squares of 11); the nebula tail goes below/behind, its lowest curl on the grey line"),
    "9b_layout_aurelionsol_fly.png": ("full_aurelionsol_fly", "B: astral flight; the SAME scale as A; the nebula tail streams behind to the image left"),
}
ANCHOR = ("full_aurelionsol_idle", 42)
TAIL = 12   # A: squares between the body stub and the ground line, filled by the nebula tail
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_shyvana_dragon.png": ("shyvana", "hd_d_idle"),
    "11_style_smolder.png": ("smolder", "hd_idle"),
    "12_style_velkoz.png": ("velkoz", "hd_idle"),
    "13_style_zoe.png": ("zoe", "hd_idle"),
}
FIT, GROUND = 0.32, 0.72   # he floats high above his own ground: a smaller fit keeps the crest in the frame


def render(lol, name, spec, out):
    frame, yaw, size, width, crop, props = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "AurelionSol", "--fit-all",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame] + props
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the crown-helm, the face and the mane
        h = y1 - y0
        im = im.crop((max(0, x1 - round(h * 0.75)), max(0, y0 - h // 30), min(im.width, x1 + h // 30), y0 + round(h * HEAD_FRAC)))
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


def guide(src, name, k, label):
    """The render scaled by k (one scale for every guide), centred on CX. A: the body stub ends TAIL squares above SOLE
    (the nebula tail, not in the mesh, curls down to the line); B: the flight's lowest claw on the line."""
    full = _keyed(src)
    x0, y0, x1, y1 = full.getbbox()
    fig = full.crop((x0, y0, x1, y1))
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    px, py = round(CX - fig.width / 2), SOLE - fig.height - (TAIL * SQ if "idle" in os.path.basename(src) else 0)
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (px, py))
    d = ImageDraw.Draw(can)
    tail(d, np.asarray(fig)[..., 3] > 0, px, py, "idle" in os.path.basename(src))
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, py), (1536, py)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (px, py, px + fig.width, py + fig.height), "top", round((SOLE - py) / SQ, 1), "squares over the ground")


TAIL_FROM = {True: (0.33, 0.93), False: (0.19, 0.47)}   # the body's end in the figure box (A the stub's bottom, B its rear)


def tail(d, mask, px, py, idle):
    """Where the nebula tail goes (the mesh has none): violet rings tapering from the body's end (TAIL_FROM, measured on
    the renders: the lowest / leftmost point would be a claw). A: down from the stub in one S curl under the body, its
    last ring on SOLE; B: streaming back to the image left above the reaching arm."""
    h, w = mask.shape
    x0, y0 = px + TAIL_FROM[idle][0] * w, py + TAIL_FROM[idle][1] * h
    t = np.linspace(0, 1, 18)
    if idle:
        pts = list(zip(x0 - 70 * np.sin(np.pi * t) + 40 * t, y0 + (SOLE - 10 - y0) * t))
    else:
        pts = list(zip(x0 - 330 * t, y0 - 30 * np.sin(np.pi * t * 1.5)))
    for k, (x, y) in enumerate(pts):
        r = 24 * (1 - k / len(pts)) + 6
        d.ellipse([x - r, y - r, x + r, y + r], outline=(120, 80, 200, 255), width=3)
    x, y = pts[-1]
    d.text((x - 60, y - 50), "nebula tail (not in the 3D model)", fill=(120, 80, 200, 255))


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "AurelionSol.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/aurelionsol/skins/base/aurelionsolloadscreen.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_aurelionsol_splash.png"))
    anchor = _keyed(os.path.join(work, ANCHOR[0] + ".png"))
    x0, y0, x1, y1 = anchor.getbbox()
    k = ANCHOR[1] * SQ / (y1 - y0)
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), k, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "aurelionsol", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
