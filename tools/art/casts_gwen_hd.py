#!/usr/bin/env python3
"""Gwen's actions from Codex's whole-frame redraw (assets/source/gwen/hd/casts: tools/art/pack_gwen_actions.py's pack,
delivered 2026-10-25 as Codex's own expanded frames, the raw generations left in Codex's outputs folder
new-chat-2/outputs/gwen-actions/raw), read onto the design's squares:

1. read back square for square: Codex exported every frame (frames/<tag>_<nn>.png, 1536 x 1024) on 5.5-px logical
   squares drawn as 5- and 6-px blocks in the design's 48 colours, so each frame is read at that pitch, the grid's
   phase per frame the one whose lines carry its colour changes (read). Codex scaled every frame to her height (the
   face 19-22 squares wide in every standing frame, the design's 21) with her soles on one row: no rescale here;
2. her scissors back in her RIGHT hand where Codex put them in the left (RIGHT_HAND: raised by her head for the
   attack's wind-up and swing back, Snip Snip!'s swing back and the dash, and in Needlework's throw, where her right
   hand flicks - the user, 2026-10-25: 「怎么一会儿左手拿剪刀 一会儿右手 不应该都是右手拿吗」; the old Gwen carries them
   on her shoulder in all of these): the design's upper body (its rows over WAIST: head, ringlets, both arms, the pair
   carried in her right hand) on Codex's skirt and legs, placed where Codex drew her head (head_at); Codex's skirt
   kept over the seam where it flutters out beside her (the dash), its outline closed (right_hand);
3. her scissors made full size wherever Codex drew them small (tools/art/scissors_gwen_hd.py, its SPECS); in every
   frame the gaps of 1-3 squares walled in on all sides (between her hand and the pair's handle, the swap's seams)
   filled (pinholes);
4. placed on the design's grid: the soles' row on the design's (GROUND); along the ground (Codex centred each frame
   anew, 40 squares apart between attack frames) the run keeps her face in one column (its mean shoes on the pivot),
   the death keeps her front shoe where it stood (she falls back off her feet), every other tag starts with her shoes
   where the design has them and keeps the rear shoe planted while both stand, the frames between run straight from
   shift to shift (placed). Frames that repeat an earlier pose (animation-index.json `same_as`) take its result.

    python tools/art/casts_gwen_hd.py --review DIR      # every tag placed, at 3x
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scissors_gwen_hd as SC  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "gwen", "hd")
SRC = os.path.join(HD, "casts")
P = 5.5                         # Codex's logical square, px
TAGS = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
SKIN = SC.SKIN


def lp(p):
    return SC.lp(p)


def rgb24(a):
    return SC.rgb24(a)


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


def read(path):
    """A frame on Codex's 5.5-px squares -> its squares (the grid's phase fitted per axis)."""
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    op = a[..., 3] > 0
    phase = []
    for axis in (0, 1):
        if axis == 0:
            ch = (a[1:, :, :3] != a[:-1, :, :3]).any(-1) & (op[1:] | op[:-1])
            prof = ch.sum(1)
        else:
            ch = (a[:, 1:, :3] != a[:, :-1, :3]).any(-1) & (op[:, 1:] | op[:, :-1])
            prof = ch.sum(0)
        best = None
        for ph in np.arange(0, P, 0.25):
            lines = np.round(np.arange(ph, a.shape[axis] + P, P)).astype(int)
            lines = lines[(lines > 0) & (lines < a.shape[axis])]
            sc = prof[lines - 1].sum()
            if best is None or sc > best[0]:
                best = (sc, ph)
        phase.append(best[1])
    phy, phx = phase
    ny, nx = int((a.shape[0] - phy) // P), int((a.shape[1] - phx) // P)
    ys = (phy + P * (np.arange(ny) + 0.5)).astype(int)
    xs = (phx + P * (np.arange(nx) + 0.5)).astype(int)
    return a[ys][:, xs].copy()


def index():
    with open(lp(os.path.join(SRC, "animation-index.json")), encoding="utf-8") as f:
        return json.load(f)


def read_all():
    """{"<tag>_<frame>": squares} for every frame Codex drew once (not the `same_as` copies)."""
    out = {}
    for tag, fr in index().items():
        for f in fr:
            if f.get("same_as"):
                continue
            out[f"{tag}_{f['frame']}"] = read(os.path.join(SRC, f["file"]))
    return out


def soles(d, excl=None):
    """The lowest row of her (not the scissors)."""
    op = (d[..., 3] > 0) if excl is None else (d[..., 3] > 0) & ~excl
    return int(np.nonzero(op.any(1))[0].max())


def shoes(d, excl=None):
    """The middles of her shoes on the ground: the groups of her squares (not the scissors) in the 3 rows over her
    lowest. -> ([x, ...], the lowest row)."""
    op = (d[..., 3] > 0) if excl is None else (d[..., 3] > 0) & ~excl
    low = int(np.nonzero(op.any(1))[0].max())
    xs = np.nonzero(op[low - 3:low + 1].any(0))[0]
    groups = [g for g in np.split(xs, np.where(np.diff(xs) > 2)[0] + 1) if g.max() - g.min() + 1 >= 4]
    return [(g.min() + g.max() + 1) / 2.0 for g in groups], [(g.min(), g.max()) for g in groups], low


def face_x(d):
    """The middle column of her face (the largest piece of skin in her top 75 rows)."""
    op = d[..., 3] > 0
    top = np.nonzero(op.any(1))[0].min()
    sk = op & np.isin(rgb24(d), SKIN)
    sk[top + 75:] = False
    lbl, n = ndimage.label(sk, structure=np.ones((3, 3)))
    sz = ndimage.sum(sk, lbl, range(1, n + 1))
    xs = np.nonzero(lbl == int(np.argmax(sz)) + 1)[1]
    return (xs.min() + xs.max() + 1) / 2.0


D0 = design()
_mids, _, _ = shoes(D0)
PIVOT_COL = (_mids[0] + _mids[-1]) / 2.0        # between the design's shoes
GROUND = soles(D0)                              # the design's soles' row
DY = GROUND - SC.GROUND                         # Codex's soles' row -> the design's

RIGHT_HAND = ["attack_1", "attack_8", "skill_14", "skill2_1", "skill2_2", "skill2_3", "skill2_4", "ult_4", "ult_5"]
WAIST = 75                  # the design's rows over this: her upper body (its skirt's top rows with it)
BAND = 24                   # Codex's skirt kept up to this many rows over the seam
H_ = lambda s: [int(h, 16) for h in s.split()]  # noqa: E731
DRESS = H_("183282 0D1E5B 091441 1A3CB0 174C9D 304A85 2C395D F1F1F3 C7CCE0 B4B4D9 9598C4 6D7199 F7CA6A DFAA4F BB8740 "
           "976A3A 7C5739 5C4232 A98C67 8E746B 483B45 5A5F65 AABD9E")   # the skirt's colours but the outline's


def head_at(d):
    """(dx, dy): where the design's head lies in frame d - the shift at which most of its face and hair squares (rows
    8-52, the scissors' colours left out) find the same colour."""
    rgb = rgb24(D0)
    reg = np.zeros(D0.shape[:2], bool)
    reg[8:53, 25:80] = True
    reg &= (D0[..., 3] > 0) & ~np.isin(rgb, SC.SC)
    ys, xs = np.nonzero(reg)
    vals = rgb[ys, xs]
    A, op = rgb24(d), d[..., 3] > 0
    best = None
    for dy in range(-ys.min(), d.shape[0] - ys.max()):
        for dx in range(-xs.min(), d.shape[1] - xs.max()):
            sc = int(((A[ys + dy, xs + dx] == vals) & op[ys + dy, xs + dx]).sum())
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
    return best[1], best[2]


def upper():
    """The design's upper body: its rows over WAIST, and the bottom of the rings (a row or two lower)."""
    u = D0.copy()
    u[WAIST:] = 0
    lo = np.zeros(D0.shape[:2], bool)
    lo[WAIST:WAIST + 3, 70:] = True
    lo &= (D0[..., 3] > 0) & np.isin(rgb24(D0), SC.SC)
    u[lo] = D0[lo]
    return u


def pinholes(a, most=3):
    """Gaps of up to `most` squares walled in on every side (the seam's: the design's own are 4 and more) filled with
    the colour most of their neighbours have."""
    op = a[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out, rgb = a.copy(), rgb24(a)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > most:
            continue
        cols, cnt = np.unique(rgb[ndimage.binary_dilation(m, structure=np.ones((3, 3))) & ~m & op], return_counts=True)
        c = int(cols[np.argmax(cnt)])
        out[m] = ((c >> 16) & 255, (c >> 8) & 255, c & 255, 255)
    return out


def right_hand(d):
    """Frame d with the design's upper body (the pair in her right hand) on its skirt and legs (see the notes)."""
    dx, dy = head_at(d)
    cut = WAIST + dy
    u = upper()
    ys, xs = np.nonzero(u[..., 3] > 0)
    um = np.zeros(d.shape[:2], bool)
    um[ys + dy, xs + dx] = True
    cover = ndimage.binary_dilation(ndimage.binary_fill_holes(ndimage.binary_closing(um, iterations=2)))
    op = d[..., 3] > 0
    below = op.copy()
    below[:cut] = False
    lbl, n = ndimage.label(below, structure=np.ones((3, 3)))
    if n > 1:
        below = lbl == int(np.argmax(ndimage.sum(below, lbl, range(1, n + 1)))) + 1
    rgb = rgb24(d)
    ink = op & np.isin(rgb, SC.INK)
    dress = op & np.isin(rgb, DRESS) & ~ink & ~cover
    dress[:cut - BAND] = False
    dress[cut:] = False
    keep = below.copy()
    while True:                                     # the skirt over the seam, through its colours (not its outline)
        nxt = keep | (ndimage.binary_dilation(keep, structure=np.ones((3, 3))) & dress)
        if (nxt == keep).all():
            break
        keep = nxt
    keep |= ink & ~cover & ndimage.binary_dilation(keep & ~below, structure=np.ones((3, 3)))   # and its own outline
    out = d.copy()
    out[~keep] = 0
    out[ys + dy, xs + dx] = u[ys, xs]
    op = out[..., 3] > 0
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    ring = ndimage.binary_dilation(op & ~np.isin(rgb24(out), SC.INK), structure=cross) & ~op
    ring[:cut - BAND - 2] = False
    ring[cut + 3:] = False
    out[ring] = (*SC.OUTLINE, 255)
    return SC.drop_specks(out, SC.SPECK)


def offsets(raw, old):
    """{name: dx}: each frame's column on the design's grid = its own + dx (see the module's notes). old: the old
    scissors' squares per swapped frame (never her shoes)."""
    tags = {}
    for n in sorted(raw, key=lambda n: int(n.rsplit("_", 1)[1])):
        tags.setdefault(n.rsplit("_", 1)[0], []).append(n)
    out = {}
    for tag, names in tags.items():
        known = {}
        if tag == "run":
            lead = np.mean([np.mean(shoes(raw[n], old.get(n))[0]) - face_x(raw[n]) for n in names])
            for i, n in enumerate(names):
                known[i] = PIVOT_COL - lead - face_x(raw[n])
        elif tag == "dead":
            mids, grp, _ = shoes(raw[names[0]], old.get(names[0]))
            known[0] = PIVOT_COL - (mids[0] + mids[-1]) / 2.0
            front = grp[-1][1] + known[0]
            for i, n in enumerate(names[1:], 1):
                op = (raw[n][..., 3] > 0) & ~(old.get(n) if n in old else False)
                known[i] = front - np.nonzero(op.any(0))[0].max()
        else:
            rear = None
            for i, n in enumerate(names):
                mids, grp, low = shoes(raw[n], old.get(n))
                if len(mids) < 2 or low < SC.GROUND - 2:
                    continue
                if rear is None:
                    known[i] = PIVOT_COL - (mids[0] + mids[-1]) / 2.0
                    rear = mids[0] + known[i]
                else:
                    known[i] = rear - mids[0]
            if not known:
                mids, _, _ = shoes(raw[names[0]], old.get(names[0]))
                known[0] = PIVOT_COL - np.mean(mids)
        for i, n in enumerate(names):
            if i in known:
                v = known[i]
            else:
                lo, hi = [k for k in known if k < i], [k for k in known if k > i]
                if lo and hi:
                    a, b = max(lo), min(hi)
                    v = known[a] + (known[b] - known[a]) * (i - a) / (b - a)
                else:
                    v = known[max(lo)] if lo else known[min(hi)]
            out[n] = int(round(v))
    return out


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], int(xs.min()), int(ys.min())


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)} for all 56 frames."""
    raw = read_all()
    for n in RIGHT_HAND:
        raw[n] = right_hand(raw[n])
    old = {}
    for n, (piv, deg, op_, opts) in SC.SPECS.items():
        kw = {k: v for k, v in opts.items() if k in ("handle_deg", "r_blade", "r_handle")}
        old[n] = SC.old_mask(raw[n], piv, deg, open_deg=op_, **kw)[0]
    dx = offsets(raw, old)
    done, ends = {}, {}
    for n, d in raw.items():
        x0 = y0 = 0
        if n in SC.SPECS:
            piv, deg, op_, opts = SC.SPECS[n]
            opts = dict(opts)
            src = opts.pop("at_from", None)
            if src:
                ex, ey = ends[src]
                opts["at"] = (ex + dx[src] - dx[n], ey)
            pad = 110
            d, _, info = SC.replace(d, piv, deg, op_, pad=pad, **opts)
            ends[n] = info["end"]
            x0 = y0 = -pad
        pic, cx, cy = crop(pinholes(d))         # no pinhole between her hand and the pair
        done[n] = (pic, x0 + cx + dx[n], y0 + cy + DY)
    out = {}
    for tag, fr in index().items():
        for f in fr:
            n = f"{tag}_{f['frame']}"
            out[n] = done[f"{tag}_{f['same_as']}"] if f.get("same_as") else done[n]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    fr = placed()
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        import pickle
        pickle.dump(fr, open(os.path.join(a.review, "frames.pkl"), "wb"))
        for t in TAGS:
            names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
            x0 = min(fr[n][1] for n in names + ["design"] if n in fr) if False else min(min(fr[n][1] for n in names), 0)
            x1 = max(max(fr[n][1] + fr[n][0].shape[1] for n in names), D0.shape[1])
            y0 = min(min(fr[n][2] for n in names), 0)
            y1 = GROUND + 3
            Z, W, Hh = 3, x1 - x0 + 4, y1 - y0 + 4
            can = Image.new("RGB", ((len(names) + 1) * (W * Z + 4), Hh * Z), (40, 40, 40))
            for i, (n, (pic, x, y)) in enumerate([("design", (D0, 0, 0))] + [(n, fr[n]) for n in names]):
                tile = Image.new("RGBA", (W, Hh), (96, 112, 96, 255))
                for gx in range(W):
                    tile.putpixel((gx, GROUND + 1 - y0 + 2), (60, 70, 60, 255))
                tile.putpixel((int(PIVOT_COL) - x0 + 2, GROUND + 2 - y0 + 2), (255, 0, 0, 255))
                tile.alpha_composite(Image.fromarray(pic), (x - x0 + 2, y - y0 + 2))
                can.paste(tile.convert("RGB").resize((W * Z, Hh * Z), Image.NEAREST), (i * (W * Z + 4), 0))
            can.save(os.path.join(a.review, f"read_{t}.png"))
        print("written", a.review)


if __name__ == "__main__":
    main()
