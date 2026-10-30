#!/usr/bin/env python3
"""league_volibear in R's storm form: his frames in electric blue (2026-10-30, the user: 「沃利贝尔开大是不是得搞个变色啊」;
of three drafts - electric blue, the same with a blue outline, a dark storm with a blue outline - 「2 雷电蓝+描边」).

For the 12 s after Stormbringer lands (the main pack's buff `league_volibear_r_form`, +350 health and range) only the
storm cloud behind him (view_buffs r_form) showed it; he looked as he always does. League's own R form is a bluer him
(its body map Volibear_Base_R_Avatar_Blend_01 next to volibear_base_TX_CM) under a lightning mane, the cloud's colours
(dark blue cloud, white-cored cyan lightning). Here every action he can play in the form gets a twin `r_<tag>`
(`TAGS`), his own frame square for square in other colours - nothing moved, so the twins keep their frames' sizes,
pivots and times and the add-on swaps them in mid-action (addons/league_volibear view.rs: idle, run, ... -> r_*
while the buff lasts; the main pack alone stays as it was, the cloud only, rather than flicker between the two looks
from one action to the next):

- his body (white fur, its blue shading, the purple-grey of his legs and back): by the colour's luminance onto `BODY`,
  a ramp from deep navy to a pale electric blue - the shading kept, every hue made the storm's;
- the crystal claws, the runes on his arms and his eyes (strong cyans, `kind` "accent"): onto `ACCENT`, a brighter
  cyan to white, so they glow against the bluer fur;
- the outline and the iron rings on his braids: kept;
- after the outline is grown (tools/art/ppu_restyle.py RESTYLE volibear `rim`): the outermost outline squares, the
  ones touching air, `RIM` electric blue - the draft's 「描边」. `rim()` here is the same rule, for the previews.

tools/art/rig_volibear.py lays the twins out (`recolour` on each finished canvas; the hit's flash after it) and
`twin_ones` makes their 1x frames his own 1x ones recoloured, ppu_restyle puts the rim on, ppu_hd makes their hd_ /
lo_ frames, hero_reels makes r_idle the idle's own reel (hero_reels.json league_volibear "r_idle": "idle"). Every
twin is its tag square for square (sizes, drawn squares, times): only colours differ.

    python tools/art/volibear_storm.py --sheet DIR     # every tag beside its storm twin, from the built sheet (4x)
"""
import argparse
import colorsys
import json
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PREFIX = "r_"
# everything he plays in the form: R's own leap and landing too (the buff starts as he lands, part way through them);
# not the death (the buff is gone by then: he falls as himself)
TAGS = ("idle", "run", "skill_run", "attack", "attack_w", "skill", "skill2", "ult", "ult_land", "hit")
OUTLINE_MAX = 60       # r + g + b at or under this: the outline (and near black), kept
# luminance of his body colours (0.2126 r + 0.7152 g + 0.0722 b, 0-1) -> colour: (36,24,39) is 0.10, (80,61,96) 0.25,
# (109,98,150) 0.40, (150,176,236) 0.67, (193,220,252) 0.85, white 0.99
BODY = [(0.08, (12, 16, 52)), (0.25, (22, 34, 96)), (0.34, (30, 52, 136)), (0.45, (40, 82, 182)),
        (0.56, (50, 114, 220)), (0.70, (70, 156, 246)), (0.80, (104, 190, 255)), (0.88, (150, 216, 255)),
        (1.00, (210, 238, 255))]
ACCENT = [(0.00, (0, 150, 255)), (0.35, (0, 205, 255)), (0.55, (90, 245, 255)), (1.00, (230, 255, 255))]
RIM = (24, 110, 255)


def lum(c):
    r, g, b = (v / 255 for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kind(c):
    """"outline", "accent" (the claws, runes and eyes: strong cyans), "metal" (the rings: greys) or "body"."""
    r, g, b = (int(v) for v in c)
    if r + g + b <= OUTLINE_MAX:
        return "outline"
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if s >= 0.45 and 0.48 <= h <= 0.60:          # 173-216 degrees
        return "accent"
    if s < 0.10 and v < 0.70:
        return "metal"
    return "body"


def ramp(anchors, x):
    xs = [a for a, _ in anchors]
    x = min(max(x, xs[0]), xs[-1])
    for (x0, c0), (x1, c1) in zip(anchors, anchors[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return tuple(int(round(a * (1 - t) + b * t)) for a, b in zip(c0, c1))
    return tuple(anchors[-1][1])


def storm(c):
    """One colour of his -> its colour in the storm form."""
    k = kind(c)
    if k in ("outline", "metal"):
        return tuple(int(v) for v in c)
    return ramp(ACCENT if k == "accent" else BODY, lum(c))


def recolour(a):
    """An RGBA frame (uint8) -> the same frame in the storm form's colours (alpha untouched)."""
    out = a.copy()
    op = out[..., 3] > 0
    cols, inv = np.unique(out[op][:, :3], axis=0, return_inverse=True)
    new = np.array([storm(tuple(c)) for c in cols], np.uint8).reshape(-1, 3)
    out[op, :3] = new[inv.reshape(-1)]
    return out


def rim(a, colour=RIM, outline=None):
    """The outline squares on the outer edge (4-touching air) -> colour; outline: the outline's exact colour (default:
    any square of r + g + b <= OUTLINE_MAX)."""
    op = a[..., 3] > 0
    rgb = a[..., :3].astype(int)
    line = np.all(rgb == outline, -1) if outline is not None else rgb.sum(-1) <= OUTLINE_MAX
    edge = op & line & ndimage.binary_dilation(~op, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    out = a.copy()
    out[edge, :3] = colour
    return out


def twin_ones():
    """league_volibear's sheet as rig_volibear's export wrote it (1x tags only, before ppu_hd), its 1x twins made his own
    1x frames recoloured. The export closes each 1x frame's outline next to light squares (strips.complete_outline, the
    commonest colour of the dense squares under each): a twin's dark navy where his mid purples are left a square or two
    open that his frame closes. The game draws the hd_ frames (league.dll), which match square for square anyway."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import strips as G
    stem = os.path.join(ROOT, "league", "champions", "league_volibear")
    an = json.load(open(stem + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    if any(t.startswith(("hd_", "lo_")) for t in an):
        raise SystemExit("twin_ones: the sheet already has hd_ / lo_ tags - run it right after rig_volibear's export")
    px = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA"))
    tags = {}
    for tag, v in an.items():
        fr = []
        for f in v["frames"]:
            d = f["data"]
            x, y, w, h = (int(round(d[k])) for k in "xywh")
            fr.append((px[y:y + h, x:x + w].copy(), f["duration"] * 1000.0))
        tags[tag] = fr
    for t in TAGS:
        tags[PREFIX + t] = [(recolour(a), ms) for (a, _), (_, ms) in zip(tags[t], tags[PREFIX + t])]
    G.write_sheet(stem, tags)


def sheet_frames(prefix=""):
    """{tag: [RGBA frame]} of league_volibear's built sheet (prefix "" 1x, "hd_", "lo_")."""
    cdir = os.path.join(ROOT, "league", "champions")
    an = json.load(open(os.path.join(cdir, "league_volibear#anim.fanim"), encoding="utf-8-sig"))["anims"]
    px = np.asarray(Image.open(os.path.join(cdir, "league_volibear#sheet.png")).convert("RGBA"))
    out = {}
    for tag, v in an.items():
        if not tag.startswith(prefix) or (not prefix and tag.startswith(("hd_", "lo_"))):
            continue
        fr = []
        for f in v["frames"]:
            d = f["data"]
            x, y, w, h = (int(round(d[k])) for k in "xywh")
            fr.append(px[y:y + h, x:x + w])
        out[tag[len(prefix):]] = fr
    return out


def review(out_dir, z=4):
    """Every storm tag's hd_ frames under the plain ones (4x, the battlefield's green) -> out_dir/volibear_storm.png."""
    os.makedirs(out_dir, exist_ok=True)
    fr = sheet_frames("hd_")
    bg = (92, 120, 76, 255)
    rows = []
    for t in TAGS:
        if PREFIX + t not in fr:
            raise SystemExit(f"hd_{PREFIX}{t} is not in the sheet: run rig_volibear, ppu_restyle, ppu_hd first")
        pair = []
        for row in (fr[t], fr[PREFIX + t]):
            w = sum(f.shape[1] for f in row) + 2 * (len(row) - 1)
            h = max(f.shape[0] for f in row)
            im = Image.new("RGBA", (w, h), bg)
            x = 0
            for f in row:
                im.alpha_composite(Image.fromarray(f), (x, h - f.shape[0]))
                x += f.shape[1] + 2
            pair.append(im.resize((w * z, h * z), Image.NEAREST))
        cell = Image.new("RGBA", (max(p.width for p in pair) + 70, pair[0].height + pair[1].height + 6), (24, 24, 28, 255))
        cell.paste(pair[0], (70, 0))
        cell.paste(pair[1], (70, pair[0].height + 6))
        d = ImageDraw.Draw(cell)
        d.text((4, 4), t, fill=(255, 236, 160, 255))
        d.text((4, pair[0].height + 10), PREFIX + t, fill=(140, 210, 255, 255))
        rows.append(cell)
    s = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 10 for r in rows)), (16, 16, 18, 255))
    y = 0
    for r in rows:
        s.paste(r, (0, y))
        y += r.height + 10
    path = os.path.join(out_dir, "volibear_storm.png")
    s.convert("RGB").save(path)
    print(path, s.size)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True, help="write volibear_storm.png here")
    review(ap.parse_args().sheet)
