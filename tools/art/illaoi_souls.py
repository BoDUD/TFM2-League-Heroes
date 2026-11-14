#!/usr/bin/env python3
"""Every League champion's spirit for Illaoi's Test of Spirit (the user, 2026-10-23: 「灵魂能雕刻出每个英雄的形状吗」,
「只要做英雄联盟的」): its own idle (the first frame of `idle_base`, the 1x sheet - the game size the dense heroes are
drawn at too) turned into a pale ghost in the spirit's GHOST ramp (tools/art/pack_illaoi_fx.py).

    python tools/art/illaoi_souls.py [--review DIR]

  league/effects/league_illaoi_souls   two tags a champion: its id (facing right, as its sprite) and <id>_l (mirrored,
                                       facing left - an effect is never turned with the unit, so the add-on picks the side
                                       its body faces: 「相反问题解决了啊」), 3 shimmer frames of 200 ms each (SOUL_T,
                                       36 ticks: the add-on plays it again for as long as the spirit stands)
  addons/league_illaoi/src/souls.rs    the ids it holds (sorted): the add-on plays `league_illaoi_soul_<id>` for them,
                                       the plain e_soul for anyone else (a champion of another mod)
The ghost: the silhouette kept square for square; the outline (a square with an empty neighbour) the pale rim; inside,
the sprite's own light and shade mapped onto the ramp by brightness, its darkest two bands dithered half away (the
spirit reads see-through over the ground) - the dither's phase steps each frame, so it shimmers. No colour of the
champion survives: every spirit is the same ghost-teal, as League's.
League champions of this repo's other packs have theirs too (OTHER: Wild Rift's Norra in tft/, the user 2026-10-26:
「俄洛伊的幽灵图别忘了」; Alune, Aphelios's sister of TFT set 18: 「俄洛伊的幽灵图做了吧」); every hero of the tft pack
(2026-10-27, the user: 「tft里面 俄洛伊的幽灵图全的吧？」 - Powder, built before the spirits, had been left out).
Dense twins (2026-11-14, the user: 「还有哪些技能没高清化的也高清化一下」): every tag has an hd_ twin at PPU 2 (two
squares a game px) - the same ghost made from the champion's own dense idle (the first frame of hd_idle_base, else
hd_idle, at the PPU its hd.rs row gives - league_main's or tft's) area-resampled to PPU 2 round the frame's middle (the
pivot, as the 1x frame's), its edge kept where at least HD_CUT of a square is covered; a champion without dense frames
(Amumu, Bard, Malphite, Sion) has its 1x idle doubled by densify_fx.scale2x (guarded EPX) instead. Rim, bands and
dither are the 1x ghost's rules on the finer squares, so the spirit is as sharp as the dense champion beside it. Plus
the idle / hd_idle pair tools/art/fx_ppu_table.py lists a sheet by and reads its PPU from (hd_idle's width / idle's:
the first champion's 1x spirit and that picture doubled, exactly 2; no view plays them) - league_main's fx_ppu.rs then
has the game draw the hd_ frames.
"""
import argparse
import glob
import json
import re
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import densify_fx as D  # noqa: E402

LEAGUE = os.path.join(ROOT, "league")
SHEET = os.path.join(LEAGUE, "effects", "league_illaoi_souls")
SOULS_RS = os.path.join(ROOT, "addons", "league_illaoi", "src", "souls.rs")
GHOST = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in ("#FFFFFF", "#E0FFF8", "#A8F0E4", "#5CC8C0", "#2A7A80")]
FRAMES, MS = 3, 200
HD_CUT = 0.5              # a resampled square is the spirit's when at least this much of it was covered
# League champions in the repo's other packs (their sprite in <pack>/champions/, the pack = the id's prefix)
OTHER = ("tft_powder", "tft_alune", "tft_norra", "tft_silco", "tft_maddie", "tft_loris", "tft_kobuko", "tft_vander", "tft_violet", "tft_krug", "tft_aoshin", "tft_scar", "tft_renni", "tft_smeech", "tft_sevika", "tft_steb", "tft_nomsy", "tft_idas", "tft_daeja", "tft_shiohyu", "tft_syfen", "tft_sohm", "tft_terra", "tft_zippy", "tft_sentinel", "tft_brambleback", "tft_raptor", "tft_elderdragon", "tft_meepsie", "tft_murkwolf", "tft_scuttlecrab", "tft_gromp", "tft_sentry", "tft_brock", "tft_cinderling", "tft_riftherald", "tft_thex", "tft_baronnashor", "tft_mightymech")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def champions():
    """The League champions of the main pack (league/champion/league_*.data_champion) and OTHER, sorted."""
    main = [os.path.basename(f).split(".")[0] for f in glob.glob(os.path.join(LEAGUE, "champion", "league_*.data_champion"))]
    return sorted(main + list(OTHER))


def idle_of(hero):
    """The first frame of its 1x idle_base (else idle), the frame centred on the unit's pivot."""
    base = os.path.join(ROOT, hero.split("_")[0], "champions", hero)
    a = json.load(open(lp(base + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    tag = "idle_base" if "idle_base" in a else "idle"
    d = a[tag]["frames"][0]["data"]
    img = np.asarray(Image.open(lp(base + "#sheet.png")).convert("RGBA"))
    x, y, w, h = (int(round(d[k])) for k in ("x", "y", "w", "h"))
    return img[y:y + h, x:x + w].copy()


def ppus():
    """{champion: the PPU of its dense frames}: the HEROES rows of league_main's and tft's hd.rs"""
    out = {}
    for crate in ("league_main", "tft"):
        src = open(lp(os.path.join(ROOT, "addons", crate, "src", "hd.rs")), encoding="utf-8").read()
        for n, p in re.findall(r'\("((?:league|tft)_[a-z0-9_]+)",\s*([0-9.]+),\s*include_str!\("[^"]*champions/', src):
            out[n] = float(p)
    return out


def to_ppu2(frame, p):
    """a frame at PPU p area-resampled (Lanczos on premultiplied colour) to PPU 2 round its middle; a square is kept
    where at least HD_CUT of it was covered, its colour un-premultiplied (the ghost re-colours it anyway)"""
    h, w = frame.shape[:2]
    W, H = max(1, int(round(w * 2 / p))), max(1, int(round(h * 2 / p)))
    f = frame.astype(np.float32) / 255.0
    pre = np.concatenate([f[..., :3] * f[..., 3:4], f[..., 3:4]], axis=2)
    r = np.stack([np.asarray(Image.fromarray(pre[..., c]).resize((W, H), Image.LANCZOS)) for c in range(4)], axis=2)
    al = np.clip(r[..., 3], 0, 1)
    keep = al >= HD_CUT
    rgb = np.clip(r[..., :3] / np.maximum(al[..., None], 1e-6), 0, 1)
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = np.where(keep[..., None], rgb * 255 + 0.5, 0).astype(np.uint8)
    out[..., 3] = np.where(keep, 255, 0).astype(np.uint8)
    return out


def hd_idle_of(hero, ppu):
    """its idle at PPU 2, the frame centred on the unit's pivot (see the module's note)"""
    base = os.path.join(ROOT, hero.split("_")[0], "champions", hero)
    a = json.load(open(lp(base + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    tag = next((t for t in ("hd_idle_base", "hd_idle") if t in a), None)
    if tag is None:
        return D.scale2x(idle_of(hero))
    d = a[tag]["frames"][0]["data"]
    img = np.asarray(Image.open(lp(base + "#sheet.png")).convert("RGBA"))
    x, y, w, h = (int(round(d[k])) for k in ("x", "y", "w", "h"))
    frame = img[y:y + h, x:x + w].copy()
    p = ppu[hero]
    return frame if p == 2.0 else to_ppu2(frame, p)


def ghost(frame, phase):
    """The frame as a ghost (see the module's note); `phase` steps the dither."""
    a = frame[..., 3] > 0
    pad = np.pad(a, 1)
    inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    edge = a & ~inner
    rgb = frame[..., :3].astype(float)
    lum = rgb @ np.array([0.3, 0.59, 0.11])
    vals = lum[a & inner]
    out = np.zeros_like(frame)
    if vals.size:
        q = np.quantile(vals, [0.25, 0.5, 0.75])
    else:
        q = [0, 0, 0]
    ys, xs = np.nonzero(a)
    for yy, xx in zip(ys, xs):
        if edge[yy, xx]:
            col = GHOST[1]
        else:
            band = int(np.searchsorted(q, lum[yy, xx]))      # 0 darkest .. 3 lightest
            if band <= 1 and (xx + yy + phase) % 2 == 0:
                continue                                    # the darker inside dithered half away
            col = GHOST[[4, 3, 2, 1][band]]
        out[yy, xx, :3] = col
        out[yy, xx, 3] = 255
    h, w = frame.shape[:2]
    return G.centre_frame(out, -(w // 2), -(h // 2))


def build():
    """{tag: frames}: idle / hd_idle, then each champion's id and id_l, then their hd_ twins"""
    ppu = ppus()
    tags, hd = {}, {}
    for hero in champions():
        for out, key, f in ((tags, hero, idle_of(hero)), (hd, "hd_" + hero, hd_idle_of(hero, ppu))):
            out[key] = [(ghost(f, k), MS) for k in range(FRAMES)]
            out[key + "_l"] = [(np.ascontiguousarray(g[:, ::-1]), ms) for g, ms in out[key]]
    one = tags[champions()[0]][0][0]      # idle / hd_idle only tell fx_ppu_table.py the PPU (hd_idle's width / idle's):
    two = np.repeat(np.repeat(one, 2, axis=0), 2, axis=1)   # exactly 2 - no view plays them
    return {"idle": [(one, 100)], "hd_idle": [(two, 100)], **tags, **hd}


def write_rs(ids):
    lines = ["//! The League champions with their own spirit picture in league_illaoi_souls (tag = id), sorted.",
             "//! Generated by tools/art/illaoi_souls.py - do not edit by hand.", "",
             "pub const SOULS: &[&str] = &["]
    lines += [f'    "{i}",' for i in ids]
    lines += ["];", ""]
    with open(lp(SOULS_RS), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="a contact sheet of every spirit beside its champion, 3x")
    a = ap.parse_args()
    tags = build()
    ids = champions()
    w, h = G.write_sheet(lp(SHEET), tags, share=True)
    write_rs(ids)
    print(f"league/effects/league_illaoi_souls#sheet.png {w}x{h}: {len(ids)} champions, each both ways, 1x and hd_; "
          f"addons/league_illaoi/src/souls.rs")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Z, per_row = 4, 12
        cells = []
        for hero in ids:
            src, g, d = idle_of(hero), tags[hero][0][0], tags["hd_" + hero][0][0]
            H = max(src.shape[0], g.shape[0], (d.shape[0] + 1) // 2)
            cell = Image.new("RGBA", ((src.shape[1] + g.shape[1] + 8) * Z + (d.shape[1] * Z + 1) // 2, H * Z),
                             (104, 112, 72, 255))
            x = 0
            for pic, z2 in ((src, 2), (g, 2), (d, 1)):    # 1x pictures at Z, the hd_ one at Z / 2 a square: one size
                pw, ph = pic.shape[1] * Z * z2 // 2, pic.shape[0] * Z * z2 // 2
                cell.alpha_composite(Image.fromarray(pic).resize((pw, ph), Image.NEAREST), (x, H * Z - ph))
                x += pw + 4 * Z
            cells.append(cell)
        rows = [cells[i:i + per_row] for i in range(0, len(cells), per_row)]
        W = max(sum(c.width + 6 for c in r) for r in rows)
        Ht = sum(max(c.height for c in r) + 6 for r in rows)
        can = Image.new("RGBA", (W, Ht), (60, 64, 50, 255))
        y = 0
        for r in rows:
            x = 0
            for c in r:
                can.alpha_composite(c, (x, y))
                x += c.width + 6
            y += max(c.height for c in r) + 6
        can.save(os.path.join(a.review, "illaoi_souls.png"))


if __name__ == "__main__":
    main()
