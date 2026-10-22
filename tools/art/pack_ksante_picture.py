"""Build the step-0 pack for Codex (assets/source/ksante/PICTURE_PROMPT.md): League references of both stances, layout
guides and style pictures.

    python tools/art/pack_ksante_picture.py --out C:/t/ks_work/ksante_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders of K'Sante in both stances, the loading-screen art and
the layout guides: Riot's, kept local, never committed) and <out>/style/11..14 (this pack's Braum, Volibear, Graves and
Galio, 8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
K'Sante (group G top, 2026-10-22) is the Pride of Nazumah: a huge broad-shouldered man with dark brown skin, short black
twists of hair, a trimmed black beard, a blue-violet scarf, a crimson padded coat with gold-and-violet diamond patterns,
big bronze-gold pauldrons, gauntlets and knee guards, thick gold ropes and gold medallion discs hung over his chest, a
violet tabard over dark plum trousers and brown boots, and his two ntofos: huge teal-grey stone shield-tonfas with gold
rims and inlaid crystal, taller than he is.
His skin bin hides every weapon submesh, so the renders name them: the shields (RWeaponShield / LWeaponShield) and the
handle part Weapon on the weapons map (KSante_Base_Weapons_TX), the motion smears and the thin blades left out.
Two stances, the same man (the user's pick: All Out is an action set of its own, ao_* tags):
  base    - idle1: upright, the two ntofos held upright beside him like a wall, their tops above his head.
  All Out - Idle1_AllOut: hunched forward, fists low, the ntofos swung out as long clubs reaching to the ground.
Four pictures: A = base idle 3/4 front facing right, SA = base side-on facing right, O = All Out idle 3/4, SO = All Out
side-on. Idle1_AllOut turns his body about 20 degrees off the root, so the All Out renders take yaw 15 (3/4) and 55
(side). A about 56 squares of 11 px from the ntofo tops to the soles; O on the same square size (measured from one
render of both, so they keep their sizes against each other). Yaw 0 front, 35 the 3/4 view, 75 the side.
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
BASE, ALLOUT = "idle1@0", "idle1_allout@0"
PARTS = ["--submesh-texture", "Weapon=Weapons_TX", "--submesh-texture", "RWeaponShield=Weapons_TX",
         "--submesh-texture", "LWeaponShield=Weapons_TX"]
for _s in ("RWeaponShieldSmearTop", "RWeaponShieldSmearBot", "LWeaponShieldSmearTop", "LWeaponShieldSmearBot",
           "RWeaponBlade", "LWeaponBlade"):
    PARTS += ["--hide-submesh", _s]
# name -> (frame, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_ksante_idle": (BASE, 35, 1600, 1.2, "box"),
    "2_ksante_frontal": (BASE, 0, 1600, 1.2, "box"),
    "3_ksante_head": (BASE, 35, 3200, 1.2, "head"),
    "4_ksante_side": (BASE, 75, 1600, 1.2, "box"),
    "5_allout_idle": (ALLOUT, 15, 1600, 1.6, "box"),
    "6_allout_side": (ALLOUT, 55, 1600, 1.6, "box"),
    "full_base": (BASE, 35, 1600, 1.6, "none"),
    "full_base_side": (BASE, 75, 1600, 1.6, "none"),
    "full_allout": (ALLOUT, 15, 1600, 1.6, "none"),
    "full_allout_side": (ALLOUT, 55, 1600, 1.6, "none"),
}
SQ = 11
A_SQUARES = 56
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, label); the squares tall come from the pair render
    "8a_layout_base.png": ("full_base", "A: K'Sante's idle, 3/4 front; ntofo tops to soles {px} px ({sq} squares of 11)"),
    "8b_layout_base_side.png": ("full_base_side", "SA: the same idle from the side, facing right; same size and ground"),
    "8c_layout_allout.png": ("full_allout", "O: All Out idle, 3/4 front; top to soles {px} px ({sq} squares of 11)"),
    "8d_layout_allout_side.png": ("full_allout_side", "SO: All Out from the side, facing right; same size and ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_braum.png": ("braum", "hd_idle"),
    "12_style_volibear.png": ("volibear", "hd_idle"),
    "13_style_graves.png": ("graves", "hd_idle"),
    "14_style_galio.png": ("galio", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def pose(lol, name, frames, yaw, size, width, out, labels=False):
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "KSante",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, *PARTS]
    if not labels:
        cmd.append("--no-labels")
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    return os.path.join(out, name + ".png")


def render(lol, name, spec, out):
    frame, yaw, size, width, crop = spec
    path = pose(lol, name, [frame], yaw, size, width, out)
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # his head between the ntofos: the hair, the face, the beard, the scarf
        w, h = x1 - x0, y1 - y0
        sub = _keyed(path).crop((x0 + w // 4, y0 + round(h * 0.1), x1 - w // 6, y0 + round(h * 0.4)))
        hx0, hy0, hx1, hy1 = sub.getbbox()
        ox, oy = x0 + w // 4, y0 + round(h * 0.1)
        cx = ox + (hx0 + hx1) // 2
        half = round(w * 0.22)
        im = im.crop((max(0, cx - half), oy, min(im.width, cx + half), oy + round(h * 0.3)))
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


def pair_ratio(lol, work):
    """O's height over A's, both stances in ONE render (one scale): from ntofo tops / the highest point to the soles."""
    path = pose(lol, "pair", [BASE, ALLOUT], 35, 1600, 1.6, work)
    full = _keyed(path)
    cw = full.width // 2
    hs = []
    for i in range(2):
        x0, y0, x1, y1 = full.crop((i * cw, 0, (i + 1) * cw, full.height)).getbbox()
        hs.append(y1 - y0)
    print("pair heights", hs)
    return hs[1] / hs[0]


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
    d.text((24, 24), label.format(px=squares * SQ, sq=squares), fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), squares, "squares, figure box", (x0, y0, x0 + fig.width, y0 + fig.height))


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "KSante.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/ksante/skins/base/ksanteloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "7_ksante_splash.png"))
    o_sq = round(A_SQUARES * pair_ratio(a.lol, work))
    for name, (src, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), A_SQUARES if "base" in src else o_sq, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "ksante", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
