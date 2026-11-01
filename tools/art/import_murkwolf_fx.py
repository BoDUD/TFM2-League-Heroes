#!/usr/bin/env python3
"""Import Murk Wolf's effects (assets/source/murkwolf/PROMPTS_FX.md: 9 pictures and 3 skill icons) as the tft pack's
sheets tft_murkwolf_fx and tft_murkwolf_big and its icons.

    python tools/art/import_murkwolf_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/murkwolf/codex_fx/murkwolf_fx: pixel_1x/murkwolf_fx_<name>.png,
one row of equal frames at game size; manifest.json's assets list each one's frames, cell_1x and its raw draft's
source_cells; raw/ its drafts; the ramps it drew with in manifest.json's palette; 64 px icons). Every frame is cut from
pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it (import_raptor_fx.py's way): spots are game px from
the pivot (x forward, y down); a unit's soles are 11 under it. Every picture is checked symmetric left to right.
RECUT: the small hits were asked too small (p_hit 16 x 16, r_bite 10 x 10, a_hit 14 x 14): Codex's sharp star, fangs
and drops voted down into blobs (r_bite's second frame a solid dark-red square). They are cut again from their raw 2 x 2
drafts into the bigger cells RECUT gives (mirrored about each tile's middle column, the drawings' shared box centred
and fitted; each square the commonest colour of the delivered strip's palette and the ramps among its raw pixels,
alpha by majority, the left half mirrored onto the right).
PACK: the pack's two pups (r_pack): Codex's 100 x 40 cut squashed its raw pups (each about 164 x 195 raw px, taller
than wide) into 14 x 13. Each frame's left pup is read again from the raw 2 x 3 draft at PUP_K raw px a square (about
16 x 19 game px), standing on the cell's bottom row with its middle PUP_X columns from the cell's left edge, and
mirrored onto the right (the wolf's 50 x 36 body stays clear between them).
Anchors: the hits on the struck body (the cell's middle, HIT); the landing murk on the ground where it lands (SOLES);
the claws' glint, the howl's smoke and the pups stand on its soles under the middle of its body (BODY: the design's
middle is 3 game px ahead of its standing point).
LIGHTER: the landing murk (q_land) was drawn in the murk ramp's darkest shades and all but vanished under the wolf on the
ground (preview_murkwolf.py): every one of its squares on a ramp of pack_murkwolf_fx (MURK, CYAN) takes the next lighter
shade of that ramp.
Icons: Codex's 64 px icons were its 1254 px tiles voted down into mud; brought to 64 x 64 again from the raw tiles with
LANCZOS (the Raptor, Sohm, Terra and Sentinel way).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import pack_murkwolf_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "murkwolf", "codex_fx", "murkwolf_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
BODY = (3, 11)                  # under the middle of its body (3 game px ahead of its standing point), on its soles
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
EDGE_STRIP = 3                  # and parts within this many columns of a side and narrower than it
EDGE_KEEP = {"q_emp", "e_howl", "r_pack", "r_hit", "r_bite"}   # drawn out at the cell's sides on purpose (the drops)
# name -> the cell (game px) to cut again from the raw draft
RECUT = {"p_hit": (22, 22), "r_bite": (14, 14), "a_hit": (16, 16)}
LIGHTER = {"q_land"}
PUP_K = 10.3                    # raw px a square for the pups
PUP_X = 14                      # the left pup's middle column in the 100-wide cell


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core", "foot" or a row, frames with ms, spots)
FX = {
    # Twin Bite: the snap on the bitten
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Gray Buff: a skill's crit on the struck
    "p_hit": ("core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    # Rending Claws: the landing murk where it lands, the claw X on the rent, the glint while its 3 attacks last
    "q_land": ("foot", seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_emp": ("foot", loop(6, 90), [BODY]),
    # Slayer's Howl: the smoke round it (e_t 300 ticks)
    "e_howl": ("foot", loop(6, 100), [BODY]),
    # Pack Attack: the two pups beside it (r_t 360 ticks), their pounce, their bites
    "r_pack": ("foot", loop(6, 110), [BODY]),
    "r_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r_bite": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
}
ICONS = {"icon_skill": "tft_murkwolf_skill", "icon_skill2": "tft_murkwolf_skill2", "icon_ult": "tft_murkwolf_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        m = json.load(f)
    ramps = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in m["palette"]], float)
    return {e["file"][len("murkwolf_fx_"):-4]: e for e in m["assets"] if e["file"].startswith("murkwolf_fx_")}, ramps


def palette(strip, ramps):
    return np.unique(np.concatenate([strip[strip[..., 3] >= 128][:, :3].astype(float), ramps]), axis=0)


def tiles_of(name, e):
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"murkwolf_fx_{name}.png"))).convert("RGBA"))
    return [raw[y0:y1, x0:x1] for x0, y0, x1, y1 in e["source_cells"][:e["frames"]]]


def vote(t, ox, oy, k, w, h, pal):
    """A w x h read of tile t from (ox, oy) at k raw px a square: the commonest palette colour, alpha by majority."""
    n = max(1, int(k))
    out = np.zeros((h, w, 4), np.uint8)
    lab_p = pal
    for j in range(h):
        for i in range(w):
            ya, xa = int(oy + j * k), int(ox + i * k)
            if ya + n <= 0 or xa + n <= 0:
                continue
            win = t[max(0, ya):max(0, ya) + n, max(0, xa):max(0, xa) + n].reshape(-1, 4)
            if len(win) == 0:
                continue
            on = win[win[:, 3] >= 128]
            if len(on) * 2 < len(win):
                continue
            idx = np.argmin(((on[:, None, :3].astype(float) - lab_p[None]) ** 2).sum(-1), axis=1)
            out[j, i, :3] = pal[np.bincount(idx).argmax()]
            out[j, i, 3] = 255
    return out


def recut(name, strip, e, ramps):
    """An effect cut again from its raw draft into RECUT[name]'s cell, mirrored about the tiles' middle column, the
    drawings' shared box centred and fitted. -> a new strip."""
    w, h = RECUT[name]
    tiles = tiles_of(name, e)
    pal = palette(strip, ramps)
    boxes = [np.nonzero(t[..., 3] >= 128) for t in tiles]
    xc = tiles[0].shape[1] / 2
    y1 = max(b[0].max() for b in boxes) + 1
    y0 = min(b[0].min() for b in boxes)
    half = max(max(abs(b[1].min() - xc), abs(b[1].max() + 1 - xc)) for b in boxes)
    k = max(2 * half / w, (y1 - y0) / h)
    ym = (y0 + y1) / 2
    out = np.zeros((h, w * len(tiles), 4), np.uint8)
    for f, t in enumerate(tiles):
        c = vote(t, xc - w / 2 * k, ym - h / 2 * k, k, w, h, pal)
        c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]
        out[:, f * w:(f + 1) * w] = c
    return out


def pack(strip, e, ramps):
    """The two pups: each frame's left pup read from the raw draft at PUP_K and mirrored onto the right of a cell as
    wide and tall as delivered."""
    w, h = e["cell_1x"]
    tiles = tiles_of("r_pack", e)
    pal = palette(strip, ramps)
    out = np.zeros((h, w * len(tiles), 4), np.uint8)
    for f, t in enumerate(tiles):
        op = t[..., 3] >= 128
        lb, n = ndimage.label(ndimage.binary_closing(op, iterations=3))
        sizes = ndimage.sum(op, lb, range(1, n + 1))
        big = [int(j) + 1 for j in np.argsort(-sizes)[:2]]
        left = min(big, key=lambda j: np.nonzero(lb == j)[1].mean())
        m = (lb == left) & op
        ys, xs = np.nonzero(m)
        pw, ph = int(np.ceil((np.ptp(xs) + 1) / PUP_K)), int(np.ceil((np.ptp(ys) + 1) / PUP_K))
        pup = vote(np.where(m[..., None], t, 0).astype(np.uint8),
                   (xs.min() + xs.max() + 1) / 2 - pw / 2 * PUP_K, ys.max() + 1 - ph * PUP_K, PUP_K, pw, ph, pal)
        c = np.zeros((h, w, 4), np.uint8)
        x0 = PUP_X - pw // 2
        c[h - ph:, x0:x0 + pw] = pup
        c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]
        out[:, f * w:(f + 1) * w] = c
    print(f"r_pack pups {pw}x{ph}")
    return out


def lighter(a):
    """Every square on the murk or cyan ramp one shade lighter (the ramps run lightest first)."""
    out = a.copy()
    for ramp in (PK.MURK, PK.CYAN):
        cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in ramp.split(", ")]
        for k in range(1, len(cols)):
            m = (a[..., 3] > 0) & (a[..., :3] == cols[k]).all(-1)
            out[m, :3] = cols[k - 1]
    return out


def cells(name, m, ramps):
    """The frames of an effect, symmetry checked."""
    e = m[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"murkwolf_fx_{name}.png"))).convert("RGBA")).copy()
    if name in LIGHTER:
        a = lighter(a)
    w, h = e["cell_1x"]
    if name in RECUT:
        a = recut(name, a, e, ramps)
        w, h = RECUT[name]
    elif name == "r_pack":
        a = pack(a, e, ramps)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    if a.shape[0] != h or a.shape[1] != w * e["frames"]:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {e['frames']} cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(e["frames"])]
    for c in ([] if name in EDGE_KEEP else out):   # bits of a neighbour at the cell's sides
        op = c[..., 3] > 0
        lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            part = lb == j
            side = part[:, :EDGE_STRIP].any() or part[:, -EDGE_STRIP:].any()
            thin = np.ptp(np.nonzero(part.any(0))[0]) < EDGE_STRIP
            if side and (part.sum() < EDGE_SPECK or thin):
                c[part] = 0
    for k, c in enumerate(out):
        if not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "foot":
        return [(w - 1) / 2, h - 1]
    return [(w - 1) / 2, kind]


def icon(name):
    """Codex's raw 1254 px icon tile -> 64 x 64 (LANCZOS): its own 64 px cut voted into mud."""
    im = Image.open(lp(os.path.join(SRC, "raw", f"murkwolf_{name}.png"))).convert("RGB")
    return im.resize((64, 64), Image.LANCZOS).convert("RGBA")


def review(allc, path):
    Z = 6
    rows = []
    for cs in allc.values():
        W = sum(c.shape[1] + 2 for c in cs)
        H = max(c.shape[0] for c in cs)
        img = Image.new("RGBA", (W * Z, H * Z), (104, 112, 72, 255))
        x = 0
        for c in cs:
            img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                (x * Z, (H - c.shape[0]) * Z))
            x += c.shape[1] + 2
        rows.append(img)
    sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (24, 24, 30, 255))
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y))
        y += r.height + 8
    sheet.convert("RGB").save(path)
    icons = Image.new("RGB", (3 * 202, 192), (24, 24, 30))
    for i, src in enumerate(ICONS):
        icons.paste(icon(src).convert("RGB").resize((192, 192), Image.NEAREST), (i * 202, 0))
    icons.save(path.replace(".png", "_icons.png"))
    print(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here (nothing else written)")
    a = ap.parse_args()
    m, ramps = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m, ramps) for n in FX}
    if a.review:
        review(allc, a.review)
        return
    tables = {"tft_murkwolf_fx": {}, "tft_murkwolf_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_murkwolf_big" if tag in BIG else "tft_murkwolf_fx"][tag] = out
        print(f"{tag:8s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        icon(src).save(lp(os.path.join(MOD, "icons", dst + ".png")))
        print(f"tft/icons/{dst}.png")


if __name__ == "__main__":
    main()
