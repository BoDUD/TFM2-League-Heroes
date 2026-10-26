"""Build the step-0 pack for Codex (assets/source/norra/PICTURE_PROMPT.md): TFT model references, layout guides and
style pictures.

    python tools/art/pack_norra_picture.py --out C:/t/nr_work/norra_pack0 [--lol D:/WeGameApps/lol] [--cd C:/t/nr_work/cd]

Writes <out>/PICTURE_PROMPT.md, <out>/refs/1..10 (no 8) (renders of TFT's own models, the unit art and the layout guides:
Riot's, kept local, never committed) and <out>/style/11..15 (this repo's Heimerdinger, Poppy, Ziggs, Powder and
Yuumi's ride picture, 8x, cut from their sheets), then <out>.zip.
Norra (the tft pack's second hero, 2026-10-26) is the yordle portal mage of Teamfight Tactics set 12 (Magic n' Mayhem),
the unit "Norra & Yuumi" (TFT12_Norra, Yuumi = TFT12_Yuumi). The League client dropped set 12 (TFTSet12.wad.client is a
272-byte stub), so the models come from CommunityDragon's raw 14.15 tree: Norra's .skn and colour map (no .skl, no
clips: her renders are the bind pose, an A-pose with the arms down) and Yuumi's .skn, body and book maps. TFT12_Yuumi's
mesh is skinned on League Yuumi's own skeleton (the bind pose matches Yuumi_base.skl to 1e-5), so League's local clips
would pose her, but the book bones differ and stretch the book, and League's attach clips leap rather than lie: the pose
of B is this repo's own league_yuumi_ride picture (style 15, the cat lying on her open book).
Two pictures at one square size: A = Norra standing, 3/4 front facing right (the design); B = TFT Yuumi lying on her
open book, the picture that rides on an ally's head (her passive).
"""
import argparse
import json
import os
import shutil
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "lol"))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

SRC = os.path.join(REPO, "assets", "source")
CHAMPS = os.path.join(REPO, "league", "champions")
EFFECTS = os.path.join(REPO, "league", "effects")
TFT = os.path.join(REPO, "tft", "champions")
GREY = (225, 225, 225)
CDRAGON = "https://raw.communitydragon.org/14.15/game/"
NORRA = "assets/characters/tft12_norra/"
YUUMI = "assets/characters/tft12_yuumi/"
FILES = [NORRA + "skins/base/tft12_norra.tft_set12.skn", NORRA + "skins/base/tft12_norra_base_tx_cm.tft_set12.png",
         NORRA + "skins/base/images/tft12_norra_mobile.tft_set12.png", NORRA + "hud/tft12_norra_square.tft_set12.png",
         YUUMI + "skins/base/tft12_yuumi.tft_set12.skn", YUUMI + "skins/base/tft12_yuumi_base_tx_cm.tft_set12.png",
         YUUMI + "skins/base/tft12_yuumi_base_book_tx_cm.tft_set12.png",
         YUUMI + "skins/base/images/tft12_yuumi_splash_centered_0.tft_set12.png"]
SQ = 11
SOLE = 1390
A_SQUARES = 56   # A: the top of the hat to the soles
B_SQUARES = 24   # B: the top of the orb on Yuumi's antenna to the bottom of the book
# name -> (model, yaw, crop: "box" / "head", pose clip@ms for Yuumi)
RENDERS = {
    "1_norra_34": ("norra", 35, "box", None),
    "2_norra_front": ("norra", 0, "box", None),
    "3_norra_head": ("norra", 35, "head", None),
    "4_norra_side": ("norra", 90, "box", None),
    "5_norra_back": ("norra", 200, "box", None),
    "7_yuumi_34": ("yuumi", 35, "box", None),
}
CUT = {  # style pictures cut from a sheet: name -> (folder, sheet, tag)
    "11_style_heimerdinger.png": (CHAMPS, "league_heimerdinger", "hd_idle"),
    "12_style_poppy.png": (CHAMPS, "league_poppy", "hd_idle"),
    "13_style_ziggs.png": (CHAMPS, "league_ziggs", "hd_idle"),
    "14_style_powder.png": (TFT, "tft_powder", "hd_idle"),
    "15_style_yuumi_ride.png": (EFFECTS, "league_yuumi_ride", "hd_idle"),
}


def fetch(cd):
    """CommunityDragon's copies of the set-12 files, once, into the local cache `cd` (never committed)."""
    for rel in FILES:
        path = os.path.join(cd, *rel.split("/"))
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            req = urllib.request.Request(CDRAGON + rel, headers={"User-Agent": "curl/8"})   # urllib's own is refused
            with urllib.request.urlopen(req) as r, open(path, "wb") as f:
                f.write(r.read())
    return lambda rel: os.path.join(cd, *rel.split("/"))


def model(name, local, lol):
    """(posed vertices for a clip or None, tris, uv, tri_tex). Norra: bind pose only; Yuumi: League's skeleton."""
    if name == "norra":
        b = open(local(NORRA + "skins/base/tft12_norra.tft_set12.skn"), "rb").read()
        tris, v = pose_ref.read_skn(b)
        tex = Image.open(local(NORRA + "skins/base/tft12_norra_base_tx_cm.tft_set12.png"))
        return (lambda clip: v["pos"].astype(np.float64)), tris, v["uv"], (np.zeros(len(tris), int), [tex])
    b = open(local(YUUMI + "skins/base/tft12_yuumi.tft_set12.skn"), "rb").read()
    tris, v = pose_ref.read_skn(b)
    tris = pose_ref.drop_submeshes(tris, pose_ref.skn_submeshes(b), {"Eye_Dilated"})
    maps = [Image.open(local(YUUMI + "skins/base/tft12_yuumi_base_tx_cm.tft_set12.png")),
            Image.open(local(YUUMI + "skins/base/tft12_yuumi_base_book_tx_cm.tft_set12.png"))]
    vmap = pose_ref.submesh_vertex_maps(b, len(v), [({"Book_Cover", "Book_Page"}, 1)])
    wad = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "Yuumi.wad.client"))
    joints, infl = pose_ref.read_skl(wad.read_path("assets/characters/yuumi/skins/base/yuumi_base.skl"))
    bind = pose_ref.globals_(joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in joints])
    bind_inv = [np.linalg.inv(m) for m in bind]

    def posed(clip):
        if clip is None:
            return v["pos"].astype(np.float64)
        name_, ms = clip.split("@")
        anim = pose_ref.read_anim(wad.read_path(f"assets/characters/yuumi/skins/base/animations/{name_.lower()}.anm"))
        local_ = pose_ref.local_pose(joints, anim, float(ms) / 1000.0)
        return pose_ref.skin(v, infl, bind_inv, pose_ref.globals_(joints, [pose_ref.trs(*p) for p in local_]))
    return posed, tris, v["uv"], (vmap[tris[:, 0]], maps)


def render(models, name, spec, out, size=1600):
    """A mirrored 3/4 render facing image right (pose_ref's --mirror), the figure 70% of the cell, on grey."""
    which, yaw, crop, clip = spec
    posed, tris, uv, tri_tex = models[which]
    pv = posed(clip).copy()
    pv[:, 1] -= pv[:, 1].min()
    h = pv[:, 1].max()
    if crop == "head":
        size *= 2
    im = pose_ref.render_hq(pv, tris, uv, None, -yaw, 12, (size, size), size * 0.7 / h, size * 0.86,
                            tri_tex=tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", im.size, GREY + (255,))
    can.alpha_composite(im)
    x0, y0, x1, y1 = im.getbbox()
    if crop == "head":   # the hat, the head wrap, the glasses and the ears: the top 55% of her
        hh = y1 - y0
        im2 = im.crop((0, y0, im.width, y0 + round(hh * 0.55)))
        hx0, _, hx1, _ = im2.getbbox()
        m = (hx1 - hx0) // 12
        can = can.crop((hx0 - m, max(0, y0 - m), hx1 + m, y0 + round(hh * 0.55)))
    else:
        m = max(x1 - x0, y1 - y0) // 12
        can = can.crop((max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m)))
    path = os.path.join(out, name + ".png")
    can.convert("RGB").save(path)
    print(name, can.size)
    return im


def guide(fig_full, name, squares, label):
    """The figure scaled to `squares` squares of SQ tall, the lowest point on SOLE, centred."""
    fig = fig_full.crop(fig_full.getbbox())
    k = squares * SQ / fig.height
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
    px, py = round(768 - fig.width / 2), SOLE - fig.height
    can = Image.new("RGBA", (1536, 1536), GREY + (255,))
    can.alpha_composite(fig, (px, py))
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE), (1536, SOLE)], fill=(150, 150, 150, 255), width=2)
    d.line([(0, py), (1536, py)], fill=(190, 190, 190, 255), width=1)
    d.text((24, 24), label, fill=(60, 60, 60, 255))
    can.convert("RGB").save(name)
    print(os.path.basename(name), "figure box", (px, py, px + fig.width, py + fig.height),
          "squares", round(fig.width / SQ, 1), "x", round(fig.height / SQ, 1))


def cut(folder, sheet_name, tag, out):
    """Frame 0 of a sheet tag at 8x (one square = one pixel of that tag's density)."""
    anims = json.load(open(os.path.join(folder, f"{sheet_name}#anim.fanim"), encoding="utf-8-sig"))["anims"]
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(os.path.join(folder, f"{sheet_name}#sheet.png")).convert("RGBA")
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
    ap.add_argument("--cd", default=r"C:\t\nr_work\cd", help="local cache of CommunityDragon's set-12 files")
    a = ap.parse_args()
    refs, style = os.path.join(a.out, "refs"), os.path.join(a.out, "style")
    for d in (refs, style):
        os.makedirs(d, exist_ok=True)
    local = fetch(a.cd)
    models = {m: model(m, local, a.lol) for m in ("norra", "yuumi")}
    full = {}
    for name, spec in RENDERS.items():
        full[name] = render(models, name, spec, refs)
    art = Image.open(local(NORRA + "skins/base/images/tft12_norra_mobile.tft_set12.png")).convert("RGB")
    art.resize((art.width * 2, art.height * 2), Image.LANCZOS).save(os.path.join(refs, "6_norra_art.png"))
    art = Image.open(local(YUUMI + "skins/base/images/tft12_yuumi_splash_centered_0.tft_set12.png")).convert("RGB")
    art.save(os.path.join(refs, "9_yuumi_art.png"))
    guide(full["1_norra_34"], os.path.join(refs, "10a_layout_A.png"), A_SQUARES,
          f"A: Norra, 3/4 front; hat top to soles ~{A_SQUARES * SQ} px ({A_SQUARES} squares of {SQ}); layout only")
    guide(full["7_yuumi_34"], os.path.join(refs, "10b_layout_B.png"), B_SQUARES,
          f"B: Yuumi on her book; orb top to the book's bottom ~{B_SQUARES * SQ} px ({B_SQUARES} squares); size only")
    for name, (folder, sheet_name, tag) in CUT.items():
        cut(folder, sheet_name, tag, os.path.join(style, name))
    shutil.copyfile(os.path.join(SRC, "norra", "PICTURE_PROMPT.md"), os.path.join(a.out, "PICTURE_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
