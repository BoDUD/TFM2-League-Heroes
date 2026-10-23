"""Build the step-0 pack for Codex (assets/source/belveth/PICTURE_PROMPT.md): League references of Bel'Veth, layout
guides and style pictures.

    python tools/art/pack_belveth_picture.py --out C:/t/bv_work/belveth_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders of Bel'Veth, the loading-screen art) and <out>/refs/9a..9b
(layout guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Kai'Sa, Kassadin, Rek'Sai and
Vel'Koz, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Bel'Veth (group I, jungle, 2026-10-24) is the Empress of the Void: a slim lavender woman's upper body in a small dark
violet face under a magenta crest, two tall spikes rising from her shoulders, a dark plated chest with ivory-gold spikes, and two HUGE bat-wing-like
arms (dark teal-black membranes, magenta edges) that she slashes with; below the waist a dark cape-like body, a long
tail and pink-magenta claw legs. No summon: the dash (Q), the tail slam (W) and the true form (R) are frames and
effects for later steps.
Two pictures: A = her relaxed idle (the wing-arms folded down round her like a cloak), B = her combat idle (the
wing-arms raised and half spread), both 3/4 front facing right. Both renders share one scale (the bind pose), so the
guides keep it: about 58 squares of 11 px from the shoulder-spike tips to the lowest claw in A; B's claws
are put down on the same ground line (in League she hovers higher in the combat idle). Yaw 0 front, 35 the 3/4 view.
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
IDLE = "idle1_combat@0"
RELAX = "idle1_relaxed_base@0"
SKIN = []
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_belveth_idle": (IDLE, 35, 1600, 1.2, "box"),
    "2_belveth_frontal": (IDLE, 0, 1600, 1.2, "box"),
    "3_belveth_head": (RELAX, 35, 3200, 1.2, "head"),
    "4_belveth_back": (IDLE, 200, 1600, 1.2, "box"),
    "6_belveth_relaxed": (RELAX, 35, 1600, 1.2, "box"),
    "7_belveth_run": ("runclosed@300", 35, 1600, 1.2, "box"),
    "8_belveth_tail": ("spell2_0@500", 35, 1600, 1.2, "box"),
    "full_belveth_relaxed": (RELAX, 35, 1600, 1.2, "none"),
    "full_belveth_combat": (IDLE, 35, 1600, 1.2, "none"),
}
HEAD_FRAC = 0.32   # the head close-up: the horns, the hooded helm, the face and the shoulders, the top third of the figure
SQ = 11
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label); both drawn at the scale that makes A's shoulder-spike tips to lowest claw ANCHOR squares
    "9a_layout_belveth.png": ("full_belveth_relaxed", "A: Bel'Veth relaxed, 3/4 front; shoulder-spike tips to lowest claw ~638 px (58 squares of 11)"),
    "9b_layout_belveth_combat.png": ("full_belveth_combat", "B: Bel'Veth combat idle, wing-arms raised; the SAME scale as A, claws on the ground line"),
}
ANCHOR = ("full_belveth_relaxed", 58)
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_kaisa.png": ("kaisa", "hd_idle"),
    "11_style_kassadin.png": ("kassadin", "hd_idle"),
    "12_style_reksai.png": ("reksai", "hd_idle"),
    "13_style_velkoz.png": ("velkoz", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Belveth",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame] + SKIN
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the horns, the helm, the face and the shoulders
        h = y1 - y0
        cx = (x0 + x1) // 2
        im = im.crop((cx - round(h * 0.33), max(0, y0 - h // 30), cx + round(h * 0.33), y0 + round(h * HEAD_FRAC)))
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
    """The render scaled by k (one scale for every guide), the figure's lowest claw on SOLE (she hovers above the
    model's own ground, higher in the combat idle: both are put down on the ground line), centred on CX."""
    full = _keyed(src)
    x0, y0, x1, y1 = full.getbbox()
    fig = full.crop((x0, y0, x1, y1))
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    px, py = round(CX - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (px, py))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, py), (1536, py)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (px, py, px + fig.width, py + fig.height), "top", round((SOLE - py) / SQ, 1), "squares over the ground")


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Belveth.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/belveth/skins/base/belvethloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "5_belveth_splash.png"))
    anchor = _keyed(os.path.join(work, ANCHOR[0] + ".png"))
    x0, y0, x1, y1 = anchor.getbbox()
    k = ANCHOR[1] * SQ / (y1 - y0)
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), k, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "belveth", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
