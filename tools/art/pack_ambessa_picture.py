"""Build the step-0 pack for Codex (assets/source/ambessa/PICTURE_PROMPT.md): League references of Ambessa, layout
guides and style pictures.

    python tools/art/pack_ambessa_picture.py --out C:/t/am_work/ambessa_pack0 [--lol D:\\WeGameApps\\lol]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..8 (League renders, the loading-screen art), <out>/refs/9a..9b (layout
guides: Riot's, kept local, never committed) and <out>/style/10..13 (this pack's Darius, Illaoi, Riven and K'Sante,
8x, cut from their sheets), then <out>.zip. Render into a short folder (C:/t).
Ambessa (group J, top, 2026-10-25) is the Matriarch of War: a tall, broad, muscular Noxian warlord woman, Mel's
mother, with dark brown skin and short pale hair, heavy dark plate with crimson cloth, and twin blades she whips on
chains (E). No summon: the dashes (passive), the sweep and slam (Q), the brace (W), the chains (E) and the execution
(R) are frames and effects for later steps.
Two pictures: A = her idle 3/4 front facing right, SA = her side-on facing right. About 58 squares of 11 px from the
top of the figure to the soles (Illaoi's height: both tall women). Yaw 0 front, 35 the 3/4 view, 75 the side.
The pack was written in a session without the League client, so the clip names (idle, the spells) are looked up in
her animation bin at run time and written with the submeshes and textures her skin names to
assets/source/ambessa/lol_names.txt (names only, no Riot art): the later steps read it. Look at the renders before
zipping: a skin whose first colour map is a mask (Mel's DressMask) renders wrong colours - then pass
--submesh-texture pairs (--tex SUBMESH=TEXTURE, repeatable) after a look at lol_names.txt; a prop the skin hides
until a spell shows it can be hidden with --hide SUBMESH.
"""
import argparse
import json
import os
import re
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
SQ = 11
SOLE = 1390
CX = 768
FIT, GROUND = 0.5, 0.84
# clip roles -> name patterns in order of preference (a clip's .anm stem, lower case; newer champions drop the
# champion prefix: Mel's idle1)
CLIPS = {
    "idle": [r"(^|_)idle1$", r"(^|_)idle_?base$", r"(^|_)idle\d*$"],
    "q": [r"(^|_)spell1(_?a)?$", r"(^|_)spell1"],
    "q2": [r"(^|_)spell1_?b$", r"(^|_)spell1_?2$", r"(^|_)spell1_recast"],
    "w": [r"(^|_)spell2(_?a)?$", r"(^|_)spell2"],
    "e": [r"(^|_)spell3(_?a)?$", r"(^|_)spell3"],
    "r": [r"(^|_)spell4(_?a)?$", r"(^|_)spell4"],
}
# name -> (clip role, share of the clip, yaw, size, width, crop: "box" / "head" / "none")
RENDERS = {
    "1_ambessa_idle": ("idle", 0.0, 35, 1600, 1.6, "box"),
    "2_ambessa_frontal": ("idle", 0.0, 0, 1600, 1.6, "box"),
    "3_ambessa_head": ("idle", 0.0, 30, 3200, 1.6, "head"),
    "4_ambessa_back": ("idle", 0.0, 200, 1600, 1.6, "box"),
    "6_ambessa_side": ("idle", 0.0, 75, 1600, 1.6, "box"),
    "7_ambessa_q": ("q", 0.45, 35, 1600, 1.8, "box"),
    "8_ambessa_e": ("e", 0.45, 35, 1600, 1.8, "box"),
    "full_ambessa": ("idle", 0.0, 35, 1600, 1.6, "none"),
    "full_ambessa_side": ("idle", 0.0, 75, 1600, 1.6, "none"),
}
GUIDES = {  # name -> (render, squares tall, label)
    "9a_layout_ambessa.png": ("full_ambessa", 58, "A: Ambessa's idle, 3/4 front; top to soles ~640 px (58 squares of 11)"),
    "9b_layout_ambessa_side.png": ("full_ambessa_side", 58, "SA: Ambessa from the side, facing right; same size and ground"),
}
CUT = {  # style pictures cut from a sheet: name -> (hero, tag)
    "10_style_darius.png": ("darius", "hd_idle"),
    "11_style_illaoi.png": ("illaoi", "hd_idle"),
    "12_style_riven.png": ("riven", "hd_idle"),
    "13_style_ksante.png": ("ksante", "hd_idle"),
}
SPLASH = ["assets/characters/ambessa/skins/base/ambessaloadscreen_0.tex",
          "assets/characters/ambessa/skins/base/ambessaloadscreen.tex",
          "assets/characters/ambessa/skins/base/ambessaloadscreen_0.dds",
          "assets/characters/ambessa/skins/base/ambessaloadscreen.dds"]


def _keyed(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 12] = 0
    return Image.fromarray(a)


def names(wad):
    """Her clips (stem -> (path, seconds)), the submeshes of her base mesh, the ones the skin hides, her textures."""
    refs = lambda blob, ext: sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\." + ext, blob)))
    skin_bin = wad.read_path("data/characters/ambessa/skins/skin0.bin")
    skn = pose_ref.base_mesh(refs(skin_bin, rb"skn"))
    subs = [s[0] for s in pose_ref.skn_submeshes(wad.read_path(skn.lower()))]
    hidden = sorted(pose_ref.hidden_submeshes(skin_bin, set(subs)))
    texs = refs(skin_bin, rb"(?:tex|dds)")
    clips = {}
    for path in refs(wad.read_path("data/characters/ambessa/animations/skin0.bin"), rb"anm"):
        stem = os.path.splitext(os.path.basename(path))[0].lower()
        try:
            clips[stem] = (path, pose_ref.read_anim(wad.read_path(path.lower()))["duration"])
        except Exception as e:   # a clip the reader does not know: listed, never picked
            clips[stem] = (path, None)
            print("clip", stem, "not read:", e)
    return clips, skn, subs, hidden, texs


def roles(clips):
    """Clip role -> stem (the first pattern that matches a readable clip)."""
    out = {}
    for role, pats in CLIPS.items():
        for pat in pats:
            hit = sorted(s for s, (_, d) in clips.items() if d and re.search(pat, s))
            if hit:
                out[role] = hit[0]
                break
    if "idle" not in out:
        raise SystemExit("no idle clip; clips: " + ", ".join(sorted(clips)))
    return out


def render(lol, name, frame, spec, out, extra):
    _, _, yaw, size, width, crop = spec
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Ambessa",
           "--fit-all", "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", str(size), "--fit", str(FIT), "--ground", str(GROUND), "--width", str(width), "--yaw", str(yaw),
           "--name", name, "--out", out, "--frame", frame] + extra
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = _keyed(path).getbbox()
    if crop == "head":   # the hair, the face, the collar and the shoulders: from the top down 28%
        h = y1 - y0
        hx0, _, hx1, _ = _keyed(path).crop((0, y0, im.width, y0 + round(h * 0.28))).getbbox()
        m = (hx1 - hx0) // 10
        im = im.crop((max(0, hx0 - m), max(0, y0 - m), min(im.width, hx1 + m), y0 + round(h * 0.28)))
    elif crop == "box":
        m = max(x1 - x0, y1 - y0) // 12
        im = im.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    im.save(path)
    print(name, frame, im.size)
    return path


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
    print(os.path.basename(name), "figure box", (x0, y0, x0 + fig.width, y0 + fig.height),
          "squares", round(fig.width / SQ, 1), "x", round(fig.height / SQ, 1))


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
    ap.add_argument("--tex", action="append", default=[], metavar="SUBMESH=TEXTURE",
                    help="colour a submesh with this texture (pose_ref --submesh-texture), repeatable")
    ap.add_argument("--hide", action="append", default=[], metavar="SUBMESH", help="leave a submesh out, repeatable")
    a = ap.parse_args()
    refs, style, work = os.path.join(a.out, "refs"), os.path.join(a.out, "style"), a.out + "_measure"
    for d in (refs, style, work):
        os.makedirs(d, exist_ok=True)
    extra = [x for t in a.tex for x in ("--submesh-texture", t)] + [x for s in a.hide for x in ("--hide-submesh", s)]
    if not a.no_render:
        wad = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Ambessa.wad.client"))
        clips, skn, subs, hidden, texs = names(wad)
        pick = roles(clips)
        lines = ["# Ambessa's names in her League WAD (read by tools/art/pack_ambessa_picture.py; names only)",
                 f"mesh {skn}", "submeshes " + " ".join(subs), "hidden by the skin " + " ".join(hidden),
                 "picked " + " ".join(f"{r}={s}" for r, s in pick.items()), "", "## clips (stem, seconds)"]
        lines += [f"{s} {'?' if d is None else f'{d:.3f}'}" for s, (_, d) in sorted(clips.items())]
        lines += ["", "## textures"] + texs
        os.makedirs(os.path.join(SRC, "ambessa"), exist_ok=True)
        with open(os.path.join(SRC, "ambessa", "lol_names.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        print("picked", pick, "| hidden by the skin:", hidden or "-")
        for name, spec in RENDERS.items():
            role, share = spec[0], spec[1]
            if role not in pick:
                print("skip", name, "(no", role, "clip)")
                continue
            ms = round(clips[pick[role]][1] * share * 1000)
            render(a.lol, name, f"{pick[role]}@{ms}", spec, work if name.startswith("full_") else refs, extra)
        for path in SPLASH:
            try:
                splash = pose_ref.read_tex(wad.read_path(path)).convert("RGB")
            except Exception:
                continue
            k = 2 if splash.height > 800 else 3
            splash.resize((splash.width * k, splash.height * k), Image.LANCZOS).save(
                os.path.join(refs, "5_ambessa_splash.png"))
            print("splash", path)
            break
        else:
            print("no loading screen found at", SPLASH, "- put one in refs/5_ambessa_splash.png by hand")
    for name, (src, squares, label) in GUIDES.items():
        guide(os.path.join(work, src + ".png"), os.path.join(refs, name), squares, label)
    for name, (hero, tag) in CUT.items():
        cut(hero, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "ambessa", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
