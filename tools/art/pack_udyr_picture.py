"""Build the step-0 pack for Codex (assets/source/udyr/PICTURE_PROMPT.md): League references of his plain look and
his three stances in the kit, layout guides and style pictures.

    python tools/art/pack_udyr_picture.py --out C:/t/ud_work/udyr_pack0 [--lol D:/WeGameApps/lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..9 (League renders of Udyr, the loading-screen art and the layout guides:
Riot's, kept local, never committed) and <out>/style/11..14 (this pack's Volibear, Graves, Sylas and Ornn, 8x, cut
from their sheets), then <out>.zip. Render into a short folder (C:/t).
Udyr (group G jungle, 2026-10-22) is the Spirit Walker: a big bare-chested man, tanned skin with dark red tattoos,
long dark brown dreadlocks, a dark beard, one blue feather braid by his face, white-wrapped fists with orange
bracers, a belt of big orange-red beads with a teal stone plaque, baggy brown trousers, teal stone knee guards over
grey-blue fur, dark teal leg wraps and sandals.
Kit (the user's pick, layout A): Q Wilding Claw (Bear), E Blazing Stampede (Ram), R Wingborne Storm (Phoenix); W Iron
Mantle (Boar) is folded into the passive. One action set per stance (q_* / e_* / r_*), the plain look for the rest.
His skin shows a stance by its arm meshes (hidden until the stance's animation shows them): BearArms (a bear pelt
with the bear's head over his fists), BoarArms, RamArms + RamHorns (two great curled ram horns from his back and
arms), PhoenixArms + HairUp (feather blades along his arms, the hair swept up). Each render keeps its stance's meshes
and hides the others.
Five pictures: A = the plain look in the guard idle (spell2_idle, his default) 3/4 front facing right, SA = A
side-on facing right, Q = the bear stance idle (spell1_idle), E = the ram stance idle (spell3_idle), R = the phoenix
stance idle (spell4_idle), all 3/4 front facing right. A about A_SQUARES squares of 11 px from his raised fists to
the soles; the stances on the same square size (measured from one render of all four, so they keep their sizes).
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
SPIRIT = ["BearArms", "BoarArms", "RamArms", "RamHorns", "PhoenixArms", "HairUp", "Arms", "NormalHair"]
STANCES = {  # stance -> (idle frame, the submeshes it shows)
    "A": ("spell2_idle@0", ["Arms", "NormalHair"]),
    "Q": ("spell1_idle@0", ["Arms", "BearArms", "NormalHair"]),
    "E": ("spell3_idle@0", ["Arms", "RamArms", "RamHorns", "NormalHair"]),
    "R": ("spell4_idle@0", ["Arms", "PhoenixArms", "HairUp"]),
}


def parts(stance):
    shown = STANCES[stance][1]
    out = []
    for s in SPIRIT:
        if s not in shown:
            out += ["--hide-submesh", s]
    return out


# name -> (stance, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_udyr_idle": ("A", 35, 1600, 1.0, "box"),
    "2_udyr_frontal": ("A", 0, 1600, 1.0, "box"),
    "3_udyr_head": ("A", 20, 3200, 1.0, "head"),
    "4_udyr_side": ("A", 75, 1600, 1.0, "box"),
    "5_bear_stance": ("Q", 35, 1600, 1.2, "box"),
    "6_ram_stance": ("E", 35, 1600, 1.2, "box"),
    "7_phoenix_stance": ("R", 35, 1600, 1.2, "box"),
    "full_A": ("A", 35, 1600, 1.6, "none"),
    "full_SA": ("A", 75, 1600, 1.6, "none"),
    "full_Q": ("Q", 35, 1600, 1.6, "none"),
    "full_E": ("E", 35, 1600, 1.6, "none"),
    "full_R": ("R", 35, 1600, 1.6, "none"),
}
SQ = 11
A_SQUARES = 46
SOLE = 1390
CX = 768
GUIDES = {  # name -> (render, stance, label); the squares tall come from the stance render
    "9a_layout_A.png": ("full_A", "A", "A: Udyr's guard idle, 3/4 front; fists to soles {px} px ({sq} squares of 11)"),
    "9b_layout_SA.png": ("full_SA", "A", "SA: the same idle from the side, facing right; same size and ground"),
    "9c_layout_Q.png": ("full_Q", "Q", "Q: bear stance, 3/4 front; top to soles {px} px ({sq} squares of 11)"),
    "9d_layout_E.png": ("full_E", "E", "E: ram stance, 3/4 front; horn tops to soles {px} px ({sq} squares of 11)"),
    "9e_layout_R.png": ("full_R", "R", "R: phoenix stance, 3/4 front; top to soles {px} px ({sq} squares of 11)"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "11_style_volibear.png": ("volibear", "hd_idle"),
    "12_style_graves.png": ("graves", "hd_idle"),
    "13_style_sylas.png": ("sylas", "hd_idle"),
    "14_style_ornn.png": ("ornn", "hd_idle"),
}
FIT, GROUND = 0.5, 0.84


def pose(lol, name, frames, yaw, size, width, out, extra, labels=False):
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Udyr",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--size", str(size), "--fit", str(FIT),
           "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw), "--name", name, "--out", out, *extra]
    if not labels:
        cmd.append("--no-labels")
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    return os.path.join(out, name + ".png")


def render(lol, name, spec, out):
    stance, yaw, size, width, crop = spec
    path = pose(lol, name, [STANCES[stance][0]], yaw, size, width, out, parts(stance))
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # his head between the raised fists: the hair, the face, the beard, the feather braid
        w, h = x1 - x0, y1 - y0
        cx = (x0 + x1) // 2
        half = round(w * 0.24)
        im = im.crop((max(0, cx - half), y0 + round(h * 0.08), min(im.width, cx + half), y0 + round(h * 0.42)))
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


def heights(lol, work):
    """Each stance's height over A's, every stance in ONE scale (fit to the tallest): top to soles."""
    hs = {}
    for st in STANCES:
        path = pose(lol, "h_" + st, [STANCES[st][0]], 35, 1600, 1.6, work, parts(st) + ["--fit-all"])
        x0, y0, x1, y1 = _keyed(path).getbbox()
        hs[st] = y1 - y0
    print("heights", hs)
    return {st: h / hs["A"] for st, h in hs.items()}


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
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Udyr.wad.client"))
        splash = pose_ref.read_tex(wad.read_path("assets/characters/udyr/skins/base/udyrloadscreen_0.tex"))
        splash = splash.convert("RGB")
        splash.resize((splash.width * 3, splash.height * 3), Image.LANCZOS).save(os.path.join(refs, "8_udyr_splash.png"))
    ratio = heights(a.lol, work)
    for name, (src, st, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), round(A_SQUARES * ratio[st]), label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "udyr", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
