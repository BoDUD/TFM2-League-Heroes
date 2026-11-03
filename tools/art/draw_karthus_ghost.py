#!/usr/bin/env python3
"""league_karthus's spirit (Death Defied) as an effect picture: his own idle frames in League's spectral form.

    python tools/art/draw_karthus_ghost.py                     # writes league/effects/league_karthus_ghost
    python tools/art/draw_karthus_ghost.py --preview PNG [--gif GIF]   # + his idle beside the ghost, 4x on the map

Why a picture: the add-on (addons/league_karthus 0.5.0) banishes his spirit for the whole of it (p_t 420 ticks + 2,
untargetable, no health bar, rooted: League's), so his body is not drawn; the engine draws the banish's lock picture
in his place - league_karthus_p_ghost_r / _l (tools/kit/build_karthus.py), this sheet's ghost_r / ghost_l, the side
facing the nearest enemy champion (an effect picture is never mirrored), as league_zaahen's revive does
(tools/art/rig_zaahen.py --rise). A lock picture plays once, so a tag lasts 7680 ms, longer than the banish (7033 ms).

What is drawn, from his sheet (league/champions/league_karthus): idle_base / hd_idle_base - the idle loop as drawn (8 x
160 ms, the body set down a row onto the robe in frames 3-6; the played idle is hero_reels' reel, frame 0 held between
skill2 snippets) - frame for frame, three times:
- recoloured to League's spirit, a pale green-mint lit at its edge: every colour by its value (half its luminance, half
  its brightest channel, so the robe's crimson stays apart from its violet) to one of five tones (TONES, the near-black
  lines inside the darkest), the near-black squares on the silhouette's edge a glowing rim (OUTLINE), the cyan of his
  eyes, crystal and gems (and their white highlights) glowing (GLOW);
- translucent with partial alpha, nothing opaque: the body A_BODY (64 %, its lines A_LINE 59 %: about 67 % on average
  with the rim), the rim A_OUT (89 %), the glows A_GLOW (96 %) and a faint ring a square outside the rim (A_HALO 28 %;
  dense frames only - a 1x square is a whole game pixel). The game blends alpha: the base game's own effects
  (barrier_magician, shield_receive) and its shadowmancer sheet are drawn with it, so are league_ekko's r_ghost,
  league_camille's q2 bloom and league_nocturne_dark's veil;
- lifted LIFT game px off the ground and floating a row or two (BOB, over two idle loops: 2560 ms) - the breath folded
  in, so neither the robe nor the body ever moves more than a row a frame;
- the robe's last WISP game px fading to wisps (the alpha down to a fifth, then an ordered dither thinning it, its
  pattern drifting a column a frame);
- the first INTRO frames fading in as he rises to his height.
Frames are centred like the hero's own: an hd_ frame on hd_idle_base's centre (PPU 1.5, its soles 12 game px under
it), a 1x frame on idle_base's centre square, grown alike at both ends (each hd_ frame PPU times its 1x frame, rounded
to even: league.dll's check), ghost_r his idle's own facing (right: 3/4 front, the skull turned right), ghost_l its
mirror; idle / hd_idle = ghost_r / hd_ghost_r (league.dll tells a
dense effect sheet by its idle, rig_zaahen.write_rise's way; shared frames, no room taken). Registered in league_main's
hd.rs EFFECTS at PPU 1.5 and in DRAWN_EFFECTS (the effect draw shrinks it to 1 / PPU about its corner, so it covers its
own place; outside DRAWN_EFFECTS a dense effect is drawn a square a game pixel, 1.5 times too big).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts")
sys.path.insert(0, HERE)
sys.path.insert(0, SCRIPTS)
import ppu_rig as R  # noqa: E402
import strips as G  # noqa: E402

PPU = 1.5
HERO = os.path.join(ROOT, "league", "champions", "league_karthus")
OUT = os.path.join(ROOT, "league", "effects", "league_karthus_ghost")
POSE, POSE_HD = "idle_base", "hd_idle_base"

# League's spirit: pale green-mint, its edge lit (the near-black outline a glowing rim, a faint ring outside it), dark
# green lines inside, the eyes and the crystal glowing white
OUTLINE = (186, 255, 220)
TONES = [(30, 112, 86), (76, 180, 138), (122, 220, 172), (178, 246, 208), (232, 255, 240)]
CUTS = (30, 80, 120, 170)                 # value bounds between the tones (the near-black inside lines under 30)
GLOW = [(172, 255, 216), (246, 255, 249)]  # dim (the crystal's dark cyan), bright
# alpha: the inside lines (TONES[0]), the rest of the body, the rim, the glows, the ring outside
A_LINE, A_BODY, A_OUT, A_GLOW, A_HALO = 150, 164, 226, 245, 72

LIFT = 2                                  # game px off the ground (3 rows of a dense frame)
# the float over two idle loops (16 frames): rows up on top of LIFT, dense and 1x. The breath (frames 3-6 of each loop:
# the body set down a row) is folded in: the robe never moves more than a row a frame, nor the body above it
BOB_HD = [0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 0]
BOB_1X = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
LOOPS = 3                                 # float cycles: 3 x 16 x 160 ms = 7680 ms (the banish: 422 ticks, 7033 ms)
INTRO = [(0.35, 1), (0.6, 2), (0.85, 3)]  # the first frames: (alpha factor, dense rows up) as he rises to his height
WISP = 8                                  # game px of the robe's bottom fading to wisps
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])


def lp(path):
    return R.lp(path)


def tag_frames(stem, tag):
    """[(frame RGBA, ms)] of a tag of a sheet."""
    with open(lp(stem + "#anim.fanim"), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    px = np.asarray(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    out = []
    for fr in anims[tag]["frames"]:
        d = fr["data"]
        x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
        out.append((px[y:y + h, x:x + w].copy(), round(fr["duration"] * 1000)))
    return out


def ghost(fr, s, fade=1.0, phase=0):
    """One of his frames (RGBA, padded: nothing on its border) as the spirit: s squares a game pixel (PPU for hd_, 1
    for 1x), fade the whole picture's alpha factor, phase the wisps' dither drift."""
    rgb = fr[..., :3].astype(float)
    op = fr[..., 3] > 0
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    val = 0.5 * lum + 0.5 * rgb.max(-1)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    glow = op & (((b >= 140) & (g >= 140) & (r < g - 40)) | (lum > 235))
    edge = op & ~ndimage.binary_erosion(op, structure=R.CROSS, border_value=0)
    outline = edge & (lum < 24) & ~glow
    out = np.zeros_like(fr)
    alpha = np.zeros(op.shape)
    tone = np.digitize(val, CUTS)
    for k, c in enumerate(TONES):
        m = op & ~glow & ~outline & (tone == k)
        out[m, :3] = c
        alpha[m] = A_LINE if k == 0 else A_BODY
    for m, c in ((glow & (lum < 140), GLOW[0]), (glow & (lum >= 140), GLOW[1])):
        out[m, :3] = c
        alpha[m] = A_GLOW
    out[outline, :3] = OUTLINE
    alpha[outline] = A_OUT
    if s > 1:                                 # the glow ring a square outside the outline (dense frames)
        ring = ndimage.binary_dilation(op, structure=R.CROSS) & ~op
        out[ring, :3] = TONES[2]
        alpha[ring] = A_HALO
    # the robe's bottom fading to wisps: from WISP game px over the lowest row down to it
    shown = alpha > 0
    rows = np.nonzero(op.any(1))[0]
    bottom = rows.max()
    top = bottom - WISP * s
    yy, xx = np.indices(op.shape)
    t = np.clip((yy - top) / (bottom - top), 0, 1)
    alpha *= 1 - 0.8 * t ** 1.3
    thin = np.clip((t - 0.35) / 0.65, 0, 1) * 0.62 * 16
    drop = shown & (BAYER[yy % 4, (xx + phase) % 4] < thin)
    alpha[drop] = 0
    out[..., 3] = np.clip(np.round(alpha * fade), 0, 255).astype(np.uint8)
    out[out[..., 3] == 0] = 0
    return out


def padded(fr, m):
    big = np.zeros((fr.shape[0] + 2 * m, fr.shape[1] + 2 * m, 4), np.uint8)
    big[m:m + fr.shape[0], m:m + fr.shape[1]] = fr
    return big


def up(can, rows):
    out = np.zeros_like(can)
    out[:can.shape[0] - rows] = can[rows:]
    return out


def canvases():
    """The ghost facing right, frame by frame: [(dense canvas, 1x canvas, ms)] and the pivots - the dense one at its
    frame's centre (edge coordinates, as ppu_rig.crop_dense takes it), the 1x one at its frame's centre square."""
    hd = tag_frames(HERO, POSE_HD)
    one = tag_frames(HERO, POSE)
    if len(hd) != len(one) or len(BOB_HD) % len(one):
        sys.exit(f"{POSE}: {len(one)} frames, {POSE_HD}: {len(hd)}")
    m = 16
    (h0, _), (o0, _) = hd[0], one[0]
    piv_hd = (m + h0.shape[1] / 2.0, m + h0.shape[0] / 2.0)
    piv_1x = (m + o0.shape[1] // 2, m + o0.shape[0] // 2)
    lift_hd, lift_1x = round(LIFT * PPU), LIFT
    out = []
    n = len(BOB_HD)
    for k in range(LOOPS * n):
        (fh, ms), (f1, _) = hd[k % len(hd)], one[k % len(one)]
        fade, rise_hd = 1.0, lift_hd + BOB_HD[k % n]
        rise_1x = lift_1x + BOB_1X[k % n]
        if k < len(INTRO):
            fade, rise_hd = INTRO[k]
            rise_1x = round(rise_hd / PPU)
        phase = k % 4
        can_hd = up(ghost(padded(fh, m), PPU, fade, phase), rise_hd)
        can_1x = up(ghost(padded(f1, m), 1, fade, phase), rise_1x)
        out.append((can_hd, can_1x, ms))
    return out, piv_hd, piv_1x


def sizes(cans, piv_hd, piv_1x):
    """(hw, hh): every 1x frame 2hw+1 x 2hh+1 about its centre square, every dense one round((2hw+1) x PPU) x
    round((2hh+1) x PPU) about its centre - both holding everything drawn."""
    def reach(stack, at, dense):
        ys, xs = np.nonzero(stack[..., 3].max(0) > 0)
        if dense:                               # edge coordinates: a square's far side is its index + 1
            return max(at[0] - xs.min(), xs.max() + 1 - at[0]), max(at[1] - ys.min(), ys.max() + 1 - at[1])
        return max(at[0] - xs.min(), xs.max() - at[0]), max(at[1] - ys.min(), ys.max() - at[1])
    rx_hd, ry_hd = reach(np.stack([c for c, _, _ in cans]), piv_hd, True)
    rx_1x, ry_1x = reach(np.stack([c for _, c, _ in cans]), piv_1x, False)
    hw, hh = int(rx_1x), int(ry_1x)
    while round((2 * hw + 1) * PPU) / 2.0 < rx_hd:
        hw += 1
    while round((2 * hh + 1) * PPU) / 2.0 < ry_hd:
        hh += 1
    return hw, hh


def frames():
    """{tag: [(frame, ms)]} in the sheet's order."""
    cans, piv_hd, piv_1x = canvases()
    hw, hh = sizes(cans, piv_hd, piv_1x)
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    tags = {"ghost_r": [], "hd_ghost_r": [], "ghost_l": [], "hd_ghost_l": []}
    x1, y1 = piv_1x
    for can_hd, can_1x, ms in cans:
        one = can_1x[y1 - hh:y1 + hh + 1, x1 - hw:x1 + hw + 1].copy()
        hd = R.crop_dense(can_hd, piv_hd[0], piv_hd[1], W, H)
        tags["ghost_r"].append((one, float(ms)))
        tags["hd_ghost_r"].append((hd, float(ms)))
        tags["ghost_l"].append((one[:, ::-1].copy(), float(ms)))
        tags["hd_ghost_l"].append((hd[:, ::-1].copy(), float(ms)))
    return {"idle": tags["ghost_r"], "hd_idle": tags["hd_ghost_r"], **tags}


def write(tags):
    w, h = G.write_sheet(lp(OUT), tags, share=True)
    total = sum(ms for _, ms in tags["ghost_r"])
    print(f"league/effects/league_karthus_ghost#sheet.png {w}x{h}: "
          + ", ".join(f"{t} {len(v)}" for t, v in tags.items()) + f"; {total:.0f} ms a tag")
    one, hd = tags["ghost_r"][0][0], tags["hd_ghost_r"][0][0]
    al = np.concatenate([f[..., 3][f[..., 3] > 0] for f, _ in tags["hd_ghost_r"][len(INTRO):]]).astype(int)
    print(f"frames {one.shape[1]}x{one.shape[0]} (1x), {hd.shape[1]}x{hd.shape[0]} (hd_); hd_ alpha after the fade-in "
          f"{al.min()}-{al.max()}, {al.mean() / 2.55:.0f} % on average (the ring and the wisps too)")


# ------------------------------------------------------------------------------------------------- the preview
Z = 4                                     # preview pixels a game pixel
CELL = (60, 76)                           # game px a figure's cell
GROUND = 58                               # game px from a cell's top to the soles' line


# the 5v5 map's own ground (background_5v5 in the base game's bundle, its commonest colours): (colour, share), the
# blotches drawn darkest first
GROUNDS = {"grass": [((34, 51, 48), 0.35), ((39, 61, 50), 0.2), ((46, 67, 51), 0.25), ((58, 77, 46), 0.12),
                     ((76, 78, 56), 0.08)],
           "dirt": [((58, 77, 46), 0.06), ((74, 86, 47), 0.14), ((92, 91, 57), 0.8)]}


def map_ground(kind, w, h, seed=7):
    """A w x h game-pixel ground in the map's flat painted blotches: a smoothed random field cut at the colours'
    shares."""
    rng = np.random.default_rng(seed)
    f = (ndimage.gaussian_filter(rng.random((h, w)), 11, mode="wrap")
         + 0.1 * ndimage.gaussian_filter(rng.random((h, w)), 1.2, mode="wrap"))
    cols, shares = zip(*GROUNDS[kind])
    band = np.digitize(f, np.quantile(f, np.cumsum(shares)[:-1]))
    a = np.array(cols, np.uint8)[band]
    return Image.fromarray(np.dstack([a, np.full((h, w), 255, np.uint8)]), "RGBA")


def put(img, fr, cx, cy, s):
    """A frame drawn as the game draws it: s squares a game pixel, its centre on the game point (cx, cy), at Z x."""
    w, h = round(fr.shape[1] * Z / s), round(fr.shape[0] * Z / s)
    pic = Image.fromarray(fr).resize((w, h), Image.NEAREST)
    img.alpha_composite(pic, (round(cx * Z - w / 2.0), round(cy * Z - h / 2.0)))


LABELS = {"zh": (["待机（现在）", "灵体 ghost_r（朝右）", "灵体 ghost_l（朝左）"],
                  ["游戏里：高清帧 ÷ 1.5（league.dll 画的），草地", "游戏里：高清帧 ÷ 1.5，泥地",
                   "1x 帧（没有 league.dll 时），草地"]),
          "en": (["idle (now)", "ghost_r (right)", "ghost_l (left)"],
                 ["in game: hd frames / 1.5 (league.dll), grass", "in game: hd frames / 1.5, dirt",
                  "1x frames (without league.dll), grass"])}


def font(size):
    """(font, its labels): a CJK font with the Chinese labels, else the English ones."""
    fonts = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts")
    for name, lang in (("msyh.ttc", "zh"), ("simhei.ttf", "zh"), ("arial.ttf", "en")):
        try:
            return ImageFont.truetype(os.path.join(fonts, name), size), LABELS[lang]
        except OSError:
            continue
    return ImageFont.load_default(), LABELS["en"]


def preview(tags, path, frame=16):
    """His idle frame 0 beside the ghost (frame `frame`: the float's low point, his idle's own pose) facing right and
    left, at Z x on the map's grass and dirt: the hd_ frames drawn at 1 / PPU (what league.dll shows), then the 1x
    frames (the fallback)."""
    idle_hd = tag_frames(HERO, "hd_idle")[0][0]
    idle_1x = tag_frames(HERO, "idle")[0][0]
    f, (cols, names) = font(16)
    hd_figs = [idle_hd, tags["hd_ghost_r"][frame][0], tags["hd_ghost_l"][frame][0]]
    rows = [(names[0], "grass", PPU, hd_figs), (names[1], "dirt", PPU, hd_figs),
            (names[2], "grass", 1, [idle_1x, tags["ghost_r"][frame][0], tags["ghost_l"][frame][0]])]
    head, label = 30, 26
    W = CELL[0] * len(cols) * Z
    H = head + len(rows) * (label + CELL[1] * Z)
    img = Image.new("RGBA", (W, H), (24, 26, 30, 255))
    d = ImageDraw.Draw(img)
    for i, c in enumerate(cols):
        d.text((i * CELL[0] * Z + 8, 6), c, fill=(235, 235, 235, 255), font=f)
    y = head
    for name, ground, s, figs in rows:
        d.text((8, y + 2), name, fill=(200, 200, 200, 255), font=f)
        y += label
        bg = map_ground(ground, CELL[0] * len(cols), CELL[1]).resize((W, CELL[1] * Z), Image.NEAREST)
        row = Image.new("RGBA", (W, CELL[1] * Z))
        row.alpha_composite(bg)
        for i, fr in enumerate(figs):
            # the frame's centre is the unit's point: the soles 11.5 game px under it (ppu_rig.FEET)
            put(row, fr, i * CELL[0] + CELL[0] / 2.0, GROUND - R.FEET, s)
        img.alpha_composite(row, (0, y))
        y += CELL[1] * Z
    img.convert("RGB").save(lp(path))
    print(f"preview {path} ({W}x{H}): hd_ frames at {Z / PPU:.3g} px a square (= {Z} a game px), 1x at {Z}; "
          f"ghost frame {frame}")


def gif(tags, path):
    """The ghost facing right beside his idle on the grass, every frame at its own time (3x the game: a dense square
    2 px)."""
    z = 3
    idle_hd = tag_frames(HERO, "hd_idle")[0][0]
    w, h = CELL[0] * 2, CELL[1]
    bg = map_ground("grass", w, h).resize((w * z, h * z), Image.NEAREST)
    out, ms = [], []
    for fr, t in tags["hd_ghost_r"]:
        img = Image.new("RGBA", bg.size)
        img.alpha_composite(bg)
        for i, f_ in enumerate((idle_hd, fr)):
            pw, ph = round(f_.shape[1] * z / PPU), round(f_.shape[0] * z / PPU)
            pic = Image.fromarray(f_).resize((pw, ph), Image.NEAREST)
            img.alpha_composite(pic, (round((i * CELL[0] + CELL[0] / 2.0) * z - pw / 2.0),
                                      round((GROUND - R.FEET) * z - ph / 2.0)))
        out.append(img.convert("RGB"))
        ms.append(int(t))
    sample = out[::6]                       # the palette from frames all through the tag (the fade-in, the float)
    strip = Image.new("RGB", (out[0].width, out[0].height * len(sample)))
    for i, o in enumerate(sample):
        strip.paste(o, (0, i * o.height))
    pal = strip.quantize(255, dither=Image.Dither.NONE)
    q = [o.quantize(palette=pal, dither=Image.Dither.NONE) for o in out]
    q[0].save(lp(path), save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=False)
    print(f"gif {path}: {len(q)} frames, {sum(ms)} ms")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preview", help="also write his idle beside the ghost to this PNG")
    ap.add_argument("--gif", help="also write the ghost's whole tag beside his idle to this GIF")
    a = ap.parse_args()
    tags = frames()
    write(tags)
    if a.preview:
        preview(tags, a.preview)
    if a.gif:
        gif(tags, a.gif)


if __name__ == "__main__":
    main()
