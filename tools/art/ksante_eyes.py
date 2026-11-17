#!/usr/bin/env python3
"""league_ksante's eyes, crisp in every frame: each eye's white (234, 250, 251) and the pupil (49, 6, 11) his designs draw
(the user, 2026-11-16: 「奎桑提的眼睛需要用PPU调的高清点」, then on the mockup 「奎桑提要用新的眼睛 高清帧版本也是」).

    python -I tools/art/ksante_eyes.py                 # lay them: his sheet's hd_, 1x and lo_ frames, his strips and
                                                       # his drawn run's sources
    python -I tools/art/ksante_eyes.py --check         # exit 1 when a frame's eyes are not as this tool lays them (CI)
    python -I tools/art/ksante_eyes.py --review DIR    # every frame before / after (x8) and a list, nothing written

Why. His designs (assets/source/ksante/hd/idle.png, ao_idle.png: PPU 1.5) draw each eye as a white square beside a dark
pupil - All Out's two rows tall. Brought down to the 1.2 squares a game pixel the user picked (tools/art/ppu_restyle.py:
each dense square the commonest colour under it), a white square is outvoted by the skin round it in most frames: the
eyes came out a dark slit, or a blend of white and skin, a square further in or out from frame to frame. The 1x frames
(pixel_down at 1 / 1.5, tools/art/rig_ksante.py) kept the pupil and lost the whites the same way.

What it lays, on each frame's own face (found there, never pasted from another frame):
- the eye row: a dark eye square (outline black, the pupil, a lid brown) with a light one before it (the white, a blend,
  or the skin the white was lost to), the brow or a lid over the dark, cheek under it, and the face's own edge (its
  outline square) a few squares to the right; flashed frames (the hit's first, rig_ksante.hit_white) are read through
  the flash;
- the base stance's face (its dense frames, 5 squares from the first eye's white to the edge): the mockup the user took,
  locked on the edge - white, pupil, black, skin, white, the edge - the same five squares in every frame;
- All Out's face (and the base ult's, his R drawn with it): wider and turned a little from pose to pose, so its own
  geometry - the first eye's white two rows tall where the square over it is light or a lid, the second eye's white on
  the last square before the edge (two rows where the frame draws it so);
- 1x: the first eye's white before the pupil, the pupil, the second eye's white before the edge - one square each;
- lo_ (the UI's, ppu_hd.add_lo: the dense frames grown x1.125, an outline ring round them): every square grown from a
  dense eye square takes that square's colour, so lo_ stays the dense frames' own.
Nothing else changes: not the outline, the brow, the hair or a square outside the face. None of his frames is drawn
mirrored (every face looks right, as the designs); one that were would show no eye row and fail --check. The run tags are
tools/art/run_body_anim.py's: their sources get the eyes here (the drawn run, hd; the kept 1x and lo_ frames,
ksante_run_one*.png / ksante_run_lo*.png), run_body_anim.py --hero ksante lays them in. hero_reels' idle / bp reels are
rects of these frames and need nothing. Order: after rig_ksante.py / ppu_restyle.py / ppu_hd.py (they draw the eyes
again as they were), before run_body_anim.py; thin_outline.py touches no eye square (inside the face) either way.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402

HERO = "league_ksante"
RUN = ("run", "hd_run", "lo_run")
REELS = ("idle", "bp", "hd_idle", "hd_bp", "lo_idle", "lo_bp")
OUT = (2, 1, 1)
SKIN = (179, 96, 74)
WHITE = (234, 250, 251)
PUPIL = (49, 6, 11)
# his palette's squares round the eyes (design_ksante_model.py's): the outline, skin, white, pupil, lid / shade browns,
# the hair and beard grey, and the blends ppu_restyle.py left where a white was outvoted
CLS = {OUT: "#", SKIN: "s", WHITE: "W", PUPIL: "P", (83, 40, 18): "l", (137, 72, 30): "b", (116, 58, 25): "u",
       (54, 37, 21): "j", (44, 41, 40): "d", (185, 159, 154): "L", (188, 153, 135): "L", (127, 126, 106): "L",
       (150, 96, 123): "L"}
LIGHT = set("sWL")        # an eye's white as a frame has it
DARK = set("#Pbl")        # an eye's dark (not the ear's dark brown (54, 37, 21) beside it)
BROW = set("#Pbljud")     # over the eye: brow, lid, hair
FACE = set("sWL")
PAINT = {"W": WHITE, "P": PUPIL, "#": OUT, "s": SKIN}
FLASH_K = 0.45            # rig_ksante.hit_white
UI_PPU = 1.5              # ppu_hd.UI_PPU (ppu_hd.py needs scipy: CI runs this without it)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def flash(c):
    """rig_ksante.hit_white on one colour: the darks (luminance under 70) kept, the rest FLASH_K of the way to white."""
    a = np.array([[c]], np.uint8)
    lum = (0.299 * a[..., 0].astype(np.float32) + 0.587 * a[..., 1].astype(np.float32)
           + 0.114 * a[..., 2].astype(np.float32))
    if lum[0, 0] < 70:
        return tuple(int(v) for v in c)
    return tuple(int(v) for v in (a[0, 0, :3].astype(float) * (1 - FLASH_K) + 255 * FLASH_K).astype(np.uint8))


UNFLASH = {flash(c): c for c in CLS}


def classes(f):
    """-> (the frame's squares as CLS letters ('.' clear, '?' another colour), flashed or not)."""
    op = f[..., 3] > 0
    rgb = f[..., :3]
    flashed = (op & (rgb == flash(SKIN)).all(-1)).sum() > (op & (rgb == SKIN).all(-1)).sum()
    g = np.full(f.shape[:2], ".", "<U1")
    g[op] = "?"
    look = UNFLASH if flashed else {c: c for c in CLS}
    for seen, c in look.items():
        g[op & (rgb == seen).all(-1)] = CLS[c]
    return g, flashed


def at(g, y, x):
    return g[y, x] if 0 <= y < g.shape[0] and 0 <= x < g.shape[1] else "."


def interior(g, y, x, face):
    """A dark square inside the face on its row (the face over and under it, and not the frame's last on its row)."""
    return at(g, y - 1, x) in face and at(g, y + 1, x) in face and at(g, y, x + 1) != "."


def edge(g, ye, x, dense, face):
    """From x along row ye to the face's right edge (its outline square) -> the edge's column."""
    for _ in range(9):
        c = at(g, ye, x)
        if c in face or (dense and c in DARK and interior(g, ye, x, face)):
            x += 1
        elif c == "#" and at(g, ye, x + 1) in ("W", "L") and at(g, ye, x + 2) == "#":
            x += 1                                  # the brow's corner before a white the frame draws: '# W #'
        else:
            break
    return x


def candidates(g, dense, flashed):
    """-> [(score, ye, x1, xd, e)]: eye rows on the frame, x1 the first eye's white, xd its dark, e the face's edge."""
    H, W = g.shape
    out = []
    face = FACE | ({"u"} if flashed else set())     # (the flash turned a white's blend into the shade's)
    nd_max = 2 if dense else 3
    for ye in range(2, H - 1):
        row = g[ye]
        for xd in range(1, W - 2):
            if row[xd] not in DARK or row[xd - 1] not in LIGHT | face:
                continue
            x = xd
            while x < xd + nd_max and at(g, ye, x) in DARK:
                x += 1
            over = [at(g, ye - 1, xx) for xx in range(xd, x if dense else x + 1)]
            if (at(g, ye - 1, xd) not in BROW) if dense else not any(c in BROW for c in over):
                continue                                # the brow or a lid over the dark (1x: over any of it)
            after = at(g, ye, x)
            if not (after in ("s", "L", "u") and after in face or after == "W" and row[xd - 1] == "W"):
                continue                                # skin after the first eye's dark (not the second eye's white
                #                                         after its brow's corner, unless both whites are laid: a face
                #                                         too narrow for skin between them)
            e = edge(g, ye, x, dense, face)
            x1 = xd - 1
            if not dense and "P" in row[xd:x]:      # 1x: the white is the pupil's neighbour (a black square there)
                xd = xd + list(row[xd:x]).index("P")
                x1 = xd - 1
            sp = e - x1
            if at(g, ye, e) != "#" or not (4 <= sp <= 7 if dense else 3 <= sp <= 7):
                continue
            cheek = sum(at(g, ye + 1, xx) in face or at(g, ye + 1, xx) in ("u", "b") for xx in (x1, xd, xd + 1))
            if cheek < (2 if dense else 1):             # (1x: the mouth's line can be the next row)
                continue
            # (1x kept the pupil in most frames: it outweighs a brow row's skin and cheek)
            score = (2 if row[x1] in ("W", "L") else 1 if row[x1] in face else 0) \
                + (2 if at(g, ye, e - 1) in ("W", "L") else 0) + ((1 if dense else 3) if row[xd] == "P" else 0) \
                + (1 if at(g, ye - 1, xd) == "l" else 0) + cheek
            out.append((score, ye, x1, xd, e))
    return out


def lay(f, dense, ao):
    """-> ({(y, x): CLS letter} the eye squares of frame f, an info line). ao: All Out's face (and the ult's)."""
    g, flashed = classes(f)
    c = candidates(g, dense, flashed)
    if not c:
        return {}, "no eyes found"
    score, ye, x1, xd, e = max(c, key=lambda t: (t[0], t[1]))
    sq = {}
    if dense and not ao and e - x1 <= 5 and all(at(g, ye, x) in FACE | DARK | {"u", "W"} for x in range(e - 5, e)):
        for x, k in zip(range(e - 5, e), "WP#sW"):
            sq[(ye, x)] = k
        how = "base"
    elif dense:
        sq[(ye, x1)] = "W"
        if at(g, ye - 1, x1) in LIGHT | {"l", "b", "u", "j"} and at(g, ye - 2, x1) in BROW:
            sq[(ye - 1, x1)] = "W"
        if e - 1 > xd + 1:
            sq[(ye, e - 1)] = "W"
            if at(g, ye - 1, e - 1) in LIGHT and at(g, ye - 1, e) == "#":
                sq[(ye - 1, e - 1)] = "W"
        how = "ao"
    else:
        sq[(ye, x1)] = "W"
        if not ao:
            sq[(ye, xd)] = "P"
        if e - 1 > xd + 1:
            sq[(ye, e - 1)] = "W"
        how = "1x"
    return sq, f"{how} row {ye} white {x1} dark {xd} edge {e}{' flashed' if flashed else ''}"


def paint(f, sq):
    """f with the eye squares laid -> (frame, squares changed)."""
    flashed = classes(f)[1]
    b = f.copy()
    for (y, x), k in sq.items():
        c = PAINT[k]
        b[y, x, :3] = flash(c) if flashed else c
        b[y, x, 3] = 255
    return b, int((b != f).any(-1).sum())


# ------------------------------------------------------------------------------------------------- lo_ from hd_
def grow_src(hshape, lshape, k):
    """lo_ square -> the dense square ppu_hd.add_lo grew it from (k = UI_PPU x his hd.rs SIZES / his PPU, over 1:
    ppu_hd.grow about the frame's centre, nearest, centred on the lo_ rect): (sy, sx) per lo_ row / column, -1 where
    none."""
    H, W = hshape
    c = 1.0 / k
    px, py = W / 2, H / 2
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))
    nx1, ny1 = int(np.ceil((W - px) / c)), int(np.ceil((H - py) / c))
    sx = np.floor(px + (np.arange(nx0 + nx1) - nx0 + 0.5) * c).astype(int)
    sy = np.floor(py + (np.arange(ny0 + ny1) - ny0 + 0.5) * c).astype(int)
    LH, LW = lshape
    ox, oy = int(np.floor(LW / 2 - nx0 + 0.5)), int(np.floor(LH / 2 - ny0 + 0.5))
    ry = np.full(LH, -1)
    rx = np.full(LW, -1)
    for i, s in enumerate(sy):
        if 0 <= i + oy < LH and 0 <= s < H:
            ry[i + oy] = s
    for i, s in enumerate(sx):
        if 0 <= i + ox < LW and 0 <= s < W:
            rx[i + ox] = s
    return ry, rx


def lo_from(lo, hd_new, hd_sq, k):
    """lo with every square grown from a dense eye square in hd_sq given that square's colour -> (frame, changed)."""
    ry, rx = grow_src(hd_new.shape[:2], lo.shape[:2], k)
    b = lo.copy()
    for (y, x) in hd_sq:
        ys, xs = np.nonzero(ry == y)[0], np.nonzero(rx == x)[0]
        for yy in ys:
            for xx in xs:
                b[yy, xx] = hd_new[y, x]
    return b, int((b != lo).any(-1).sum())


# ------------------------------------------------------------------------------------------------- his frames
def form_of(tag):
    return "ao" if tag.split("_", 1)[-1].startswith("ao_") or tag.startswith("ao_") else "base"


def plain(tag):
    return tag[3:] if tag.startswith(("hd_", "lo_")) else tag


def ao_head(tag, f, dense):
    """All Out's face, or the base ult's (his R: the frames drawn with All Out's head, wider)."""
    if form_of(plain(tag)) == "ao":
        return True
    if not dense:
        return False
    g, flashed = classes(f)
    c = candidates(g, True, flashed)
    if not c:
        return False
    _, _, x1, _, e = max(c, key=lambda t: (t[0], t[1]))
    return e - x1 >= 6


def frames_of(anims):
    """[(tag, index, rect)] of every frame this tool looks after in the sheet, each rect once (the run tags and the
    reels left out: their frames are another tool's / other tags')."""
    out, seen = [], set()
    for tag, an in anims.items():
        if tag in RUN or tag in REELS:
            continue
        for i, fr in enumerate(an["frames"]):
            r = tuple(int(round(fr["data"][q])) for q in ("x", "y", "w", "h"))
            if r not in seen:
                seen.add(r)
                out.append((tag, i, r))
    return out


def strip_frames(path, sizes):
    s = np.array(Image.open(lp(path)).convert("RGBA"))
    out, x = [], 0
    for w, h in sizes:
        out.append((x, w, h))
        x += w + 1
    return s, out


def run_sources():
    """The run's sources run_body_anim.py reads: [(path, [(x, w, h)], density, index of its drawn frame per frame)]."""
    base = os.path.join(ROOT, "assets", "source", "ksante", "hd")
    with open(lp(os.path.join(base, "ksante_run_drawn.json")), encoding="utf-8") as f:
        meta = json.load(f)
    out = []

    def frames(sizes):
        x, fr = 0, []
        for w, h in sizes:
            fr.append((x, w, h))
            x += w + 1
        return fr
    n = len(meta["sizes"])
    out.append((os.path.join(base, "ksante_run_drawn.png"), frames(meta["sizes"]), "hd", list(range(n))))
    for suffix, k in (("", 1), ("2", 2)):
        one = os.path.join(base, f"ksante_run_one{suffix}.png")
        lo = os.path.join(base, f"ksante_run_lo{suffix}.png")
        if os.path.exists(lp(one)):
            out.append((one, frames([v for v in meta["one_sizes"] for _ in range(k)]), "one",
                        [i // k for i in range(n * k)]))
        if os.path.exists(lp(lo)):
            out.append((lo, frames([v for v in meta["lo_sizes"] for _ in range(k)]), "lo",
                        [i // k for i in range(n * k)]))
    return out


def run(check, review=None):
    hid, pack, ppu, size = T.resolve(HERO, T.all_heroes())
    grow = UI_PPU * size / ppu                      # ppu_hd.add_lo's factor (his: 1.5 x 0.9 / 1.2)
    if grow <= 1:
        sys.exit(f"{HERO}: lo_ frames averaged down (UI_PPU x size / PPU = {grow:.3f}), not grown - the eyes' lo_ rule "
                 "no longer holds")
    an, px = T.read(hid, pack)
    px2 = px.copy()
    bad, log, pics = [], [], []
    by_rect = {}
    for tag, i, (x, y, w, h) in frames_of(an):
        by_rect[(tag, i)] = (x, y, w, h)
    # dense and 1x frames: their own faces
    hd_eyes = {}
    for tag, i, (x, y, w, h) in frames_of(an):
        if tag.startswith("lo_"):
            continue
        f = px[y:y + h, x:x + w]
        dense = tag.startswith("hd_")
        sq, info = lay(f, dense, ao_head(tag, f, dense))
        b, n = paint(f, sq)
        if dense:
            hd_eyes[plain(tag), i] = (b, sq)
        log.append(f"{tag} {i}: {info}: {n} squares")
        if not sq:
            bad.append(f"{tag} {i}: no eyes found")
        if n:
            px2[y:y + h, x:x + w] = b
            pics.append((f"{tag} {i}", f, b))
    # lo_ frames: grown from the dense ones
    for tag, i, (x, y, w, h) in frames_of(an):
        if not tag.startswith("lo_"):
            continue
        if (plain(tag), i) not in hd_eyes:
            bad.append(f"{tag} {i}: no dense frame")
            continue
        hd_new, sq = hd_eyes[plain(tag), i]
        f = px[y:y + h, x:x + w]
        b, n = lo_from(f, hd_new, sq, grow)
        log.append(f"{tag} {i}: from hd_{plain(tag)} {i}: {n} squares")
        if n:
            px2[y:y + h, x:x + w] = b
            pics.append((f"{tag} {i}", f, b))
    changed = int((px2 != px).any(-1).sum())
    if changed:
        bad.append(f"sheet: {changed} squares")
    # his strips (assets/source/ppu/ksante_<tag>.png, the dense frames ppu_hd.py reads): each frame as its sheet frame
    for path in sorted(glob.glob(os.path.join(T.STRIPS, "ksante_*.png"))):
        tag = os.path.basename(path)[len("ksante_"):-4]
        if "." in tag or tag == "run":
            continue
        with open(lp(path[:-4] + ".json"), encoding="utf-8") as fh:
            sizes = json.load(fh)["sizes"]
        s, fr = strip_frames(path, sizes)
        s2 = s.copy()
        for k, (x, w, h) in enumerate(fr):
            f = s[:h, x:x + w]
            sq, info = lay(f, True, ao_head("hd_" + tag, f, True))
            b, n = paint(f, sq)
            if n:
                s2[:h, x:x + w] = b
        n = int((s2 != s).any(-1).sum())
        if n:
            bad.append(f"{os.path.relpath(path, ROOT)}: {n} squares")
            if not check and review is None:
                Image.fromarray(s2, "RGBA").save(lp(path), optimize=True)
    # the run's sources: the drawn run (dense), its kept 1x and lo_ frames
    srcs = run_sources()
    drawn = None
    for path, fr, dens, idx in srcs:
        s = np.array(Image.open(lp(path)).convert("RGBA"))
        s2 = s.copy()
        if dens == "hd":
            drawn = []
        for k, (x, w, h) in enumerate(fr):
            f = s[:h, x:x + w]
            if dens == "lo":
                hd_new, sq = drawn[idx[k]]
                b, n = lo_from(f, hd_new, sq, grow)
                info = f"from the drawn run's {idx[k]}"
            else:
                sq, info = lay(f, dens == "hd", False)
                b, n = paint(f, sq)
                if dens == "hd":
                    drawn.append((b, sq))
                if not sq:
                    bad.append(f"{os.path.basename(path)} {k}: no eyes found")
            log.append(f"{os.path.basename(path)} {k}: {info}: {n} squares")
            if n:
                s2[:h, x:x + w] = b
                pics.append((f"{os.path.basename(path)[:-4]} {k}", f, b))
        n = int((s2 != s).any(-1).sum())
        if n:
            bad.append(f"{os.path.relpath(path, ROOT)}: {n} squares")
            if not check and review is None:
                Image.fromarray(s2, "RGBA").save(lp(path), optimize=True)
    if review is not None:
        write_review(review, pics, log)
        print(f"{HERO}: {len(pics)} frames would change - {review}")
        return
    if check:
        if bad:
            print("\n".join(bad))
            sys.exit(f"{HERO}: eyes not laid - run tools/art/ksante_eyes.py, then tools/art/run_body_anim.py --hero ksante")
        print(f"ok: {HERO}'s eyes are laid on every frame")
        return
    if changed:
        Image.fromarray(px2, "RGBA").save(lp(T.stem(hid, pack) + "#sheet.png"), optimize=True)
    print(f"{HERO}: " + ("; ".join(bad) if bad else "nothing to change"))


def write_review(out_dir, pics, log):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "ksante_eyes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    S = 8
    for k in range(0, len(pics), 24):
        part = pics[k:k + 24]
        cells = []
        for name, a, b in part:
            d = (a != b).any(-1)
            ys, xs = np.nonzero(d)
            cy, cx = (int(ys.mean()), int(xs.mean())) if len(ys) else (a.shape[0] // 2, a.shape[1] // 2)
            win = []
            for im in (a, b):
                w_ = np.zeros((16, 20, 4), np.uint8)
                for yy in range(16):
                    for xx in range(20):
                        fy, fx = cy - 8 + yy, cx - 10 + xx
                        if 0 <= fy < im.shape[0] and 0 <= fx < im.shape[1]:
                            w_[yy, xx] = im[fy, fx]
                bg = np.zeros((16, 20, 3), np.uint8)
                bg[:] = (70, 70, 70)
                m = w_[..., 3] > 0
                bg[m] = w_[m][:, :3]
                win.append(np.repeat(np.repeat(bg, S, 0), S, 1))
            cells.append((name, np.concatenate([win[0], np.full((16 * S, 4, 3), 20, np.uint8), win[1]], 1)))
        cw = cells[0][1].shape[1] + 8
        ch = cells[0][1].shape[0] + 18
        cols = 4
        sheet = Image.new("RGB", (cols * cw, ((len(cells) + cols - 1) // cols) * ch), (20, 20, 20))
        from PIL import ImageDraw
        dr = ImageDraw.Draw(sheet)
        for j, (name, c) in enumerate(cells):
            X, Y = (j % cols) * cw, (j // cols) * ch
            dr.text((X + 2, Y + 2), name, fill=(255, 255, 0))
            sheet.paste(Image.fromarray(c), (X, Y + 16))
        sheet.save(os.path.join(out_dir, f"ksante_eyes_{k // 24:02d}.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", metavar="DIR")
    a = ap.parse_args()
    run(a.check, a.review)


if __name__ == "__main__":
    main()
