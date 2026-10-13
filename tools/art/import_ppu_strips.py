#!/usr/bin/env python3
"""A Codex delivery of dense (PPU) action strips -> assets/source/ppu/<hero>_<tag>.png, the drawn strips ppu_hd.py uses.

The user, 2026-10-12: 「接下来使用PPU修复吸血鬼和卡尔玛和艾希 做到所有动作帧一致 待机一致」. tools/art/pack_ppu_strips.py
made the pack (every 1x frame scaled by PPU as a skeleton in a cell, cells.json); Codex drew the design over every cell
at the pack's square size. This reads every image back square for square (each block's most common colour, clear
included), maps the colours to the design's, and puts each cell into its frame by the pivot: the frame is
round(PPU x the 1x frame) and its centre is the pivot, as in the game. A cell that starts above the frame
(frame_top < 0: room for the design's head) grows the frame by as much at the top and the bottom, so the pivot stays
its centre; the grown sizes go to <hero>_<tag>.json next to the strip. The idle is the design itself, still in every
frame (「待机一致」; an importer's breathing deforms the body: memory rig-deformation-checks), standing where the 1x idle
stands (its soles on the 1x soles, across where it overlaps the scaled 1x idle most).

    python tools/art/import_ppu_strips.py --hero vladimir --delivery <outputs>/vladimir-ppu-strips
    python tools/art/import_ppu_strips.py --hero yasuo --delivery <...> --scale 2     # pack PPU 1.5 -> game PPU 3

Then: python tools/art/ppu_hd.py --hero <hero> (the hd_ tags into the sheet) and the hero in
addons/league_main/src/hd.rs.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ppu", "orig")  # the dense frames as drawn; tools/art/ppu_restyle.py makes the strips ppu_hd.py reads from them (2026-10-13)
PACKS = os.path.join(ROOT, "dist", "ppu_packs")


def squares(path, px):
    """The image read back one pixel per drawn px x px square: each block's most common colour (clear counts)."""
    a = np.asarray(Image.open(path).convert("RGBA"))
    H, W = a.shape[0] // px, a.shape[1] // px
    b = a[:H * px, :W * px].reshape(H, px, W, px, 4).transpose(0, 2, 1, 3, 4).reshape(H, W, px * px, 4).copy()
    b[b[..., 3] < 128] = 0
    b[..., 3] = np.where(b[..., 3] > 0, 255, 0)
    out = np.zeros((H, W, 4), np.uint8)
    mixed = 0
    keys = b.astype(np.uint32)
    keys = (keys[..., 0] << 24) | (keys[..., 1] << 16) | (keys[..., 2] << 8) | keys[..., 3]
    for y in range(H):
        for x in range(W):
            v, n = np.unique(keys[y, x], return_counts=True)
            if len(v) > 1:
                mixed += 1
            k = int(v[n.argmax()])
            out[y, x] = ((k >> 24) & 255, (k >> 16) & 255, (k >> 8) & 255, k & 255)
    return out, mixed


def to_palette(a, pal):
    """Every opaque pixel to its nearest design colour. -> (image, pixels changed)."""
    op = a[..., 3] > 0
    rgb = a[op][:, :3].astype(int)
    d = ((rgb[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
    near = pal[d.argmin(axis=1)]
    out = a.copy()
    out[op, :3] = near
    return out, int((near != rgb).any(axis=1).sum())


def place_idle(design, idle1, k):
    """The design in a frame of round(k x the 1x idle): soles on the 1x soles, across at the most overlap."""
    H, W = round(idle1.shape[0] * k), round(idle1.shape[1] * k)
    sk = P.scale_any(idle1, k)[..., 3] > 0
    sole = np.nonzero(sk.any(axis=1))[0].max()
    dh, dw = design.shape[:2]
    y0 = sole - dh + 1
    if dw > W:
        sys.exit(f"the design ({dw}x{dh}) is wider than the idle frame {W}x{H}")
    if y0 < 0:
        # taller than the frame (karma's jade ring over her head): the frame grown alike at the top and the bottom
        g = -y0
        H, y0 = H + 2 * g, 0
        sk = np.pad(sk, ((g, g), (0, 0)))
    dm = design[..., 3] > 0
    best = max(range(0, W - dw + 1), key=lambda x0: int((sk[y0:y0 + dh, x0:x0 + dw] & dm).sum()))
    out = np.zeros((H, W, 4), np.uint8)
    out[y0:y0 + dh, best:best + dw] = design
    return out, (best, y0)


def orig_frames(hero, tag):
    """The frames drawn before (assets/source/ppu/orig/<hero>_<tag>.png and its size list), or None. Not the sheet's
    dense frames: those are ppu_restyle.py's, at the game's PPU."""
    png, side = os.path.join(SRC, f"{hero}_{tag}.png"), os.path.join(SRC, f"{hero}_{tag}.json")
    if not (os.path.isfile(png) and os.path.isfile(side)):
        return None
    s = np.asarray(Image.open(png).convert("RGBA"))
    with open(side, encoding="utf-8") as fh:
        sizes = json.load(fh)["sizes"]
    out, x = [], 0
    for W, H in sizes:
        out.append(s[:H, x:x + W].copy())
        x += W + 1
    return out


def write_strip(hero, tag, frames, want):
    """frames left to right, 1 px apart, top-aligned; <hero>_<tag>.json lists the sizes when any is not `want`."""
    h = max(f.shape[0] for f in frames)
    w = sum(f.shape[1] for f in frames) + len(frames) - 1
    s = np.zeros((h, w, 4), np.uint8)
    x = 0
    for f in frames:
        s[:f.shape[0], x:x + f.shape[1]] = f
        x += f.shape[1] + 1
    Image.fromarray(s).save(os.path.join(SRC, f"{hero}_{tag}.png"))
    side = os.path.join(SRC, f"{hero}_{tag}.json")
    sizes = [[int(f.shape[1]), int(f.shape[0])] for f in frames]
    # always the size list (ppu_restyle.py reads it: a 1x idle it padded no longer gives the drawn size)
    with open(side, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"sizes": sizes}, fh)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--delivery", required=True, action="append",
                    help="Codex's folder: cells.json and the <hero>_<tag>_<n>.png images (repeatable: a later delivery's "
                         "frames replace an earlier one's - a completion pack). An image not delivered takes its frames "
                         "from the folder's frames_1x/<tag>_<nn>.png (one pixel per square) where those exist")
    ap.add_argument("--fill-from-sheet", action="store_true",
                    help="frames no delivery has keep the dense frames the sheet has now (yasuo's partial delivery: "
                         "eq 5, ult 0-2 and the death were never drawn)")
    ap.add_argument("--head-region", metavar="R0-R1:C0-C1+...",
                    help="with --paste-head: the head only inside these boxes (design squares; yasuo's pauldron touches "
                         "his hair - 0-17:0-67+18-26:49-67)")
    ap.add_argument("--design", help="the design, 1 px per square (default: the pack's design/<hero>_design_1x.png)")
    ap.add_argument("--scale", type=int, default=1, help="game pixels per drawn square (yasuo: 2)")
    ap.add_argument("--head-rows", type=int, default=0,
                    help="the design's top rows Codex pasted whole into the frames (vladimir: 35, head and collar): "
                         "where a frame holds them pixel for pixel, the outline of the head Codex drew first and "
                         "pasted over is cleared - parts next to the block in its rows that never reach more than 4 "
                         "pixels from it (「吸血鬼走路有残影？没清理干净吧」); an arm or a claw reaches far")
    ap.add_argument("--design-run", action="store_true",
                    help="the run is the design itself, its legs stepping (RUN_LEGS; Codex's run bodies changed width "
                         "and arm length frame to frame: 「吸血鬼走路时模型变形」)")
    ap.add_argument("--paste-head", type=int, default=0, metavar="ROWS",
                    help="paste the design's head (its part above ROWS joined to the face: karma 59, the head and the "
                         "jade ring) into every frame (one face in all frames): placed where the 1x frame holds the 1x "
                         "idle's head, x PPU, then moved up to --head-search pixels onto Codex's head; what is left of "
                         "Codex's head round it is cleared (as --head-rows), and pieces of Codex's ring above it")
    ap.add_argument("--head-match", metavar="R0-R1:C0-C1",
                    help="with --paste-head: place the head by this part of it only (design squares; yasuo's face "
                         "11-26:45-62 - Codex's ponytail flows another way frame to frame and outvoted the face)")
    ap.add_argument("--sole-fix", action="store_true",
                    help="a pack from before 2026-10-12 15:20 cut each cell 1-2 rows above the soles (rounding): every "
                         "cell's drawing moved down onto the idle's soles (ashe: her actions stood 2 rows over the idle)")
    ap.add_argument("--clear-ring", action="store_true",
                    help="with --paste-head: Codex's own ring goes - the largest part in the colours of the head's upper "
                         "part (karma's jade ring); never for a hero whose head shares its colours with the body (ashe's "
                         "hood is her cape's navy and gold: it took her body)")
    ap.add_argument("--clear-hair-above", action="store_true",
                    help="with --paste-head: above the face, parts mostly in the head's colours go (yasuo's ponytail "
                         "drawn higher by Codex)")
    ap.add_argument("--head-search", type=int, default=8,
                    help="pixels round the 1x head's place to look for Codex's head; 0: the whole frame, each way "
                         "round (yasuo: Codex drew the E-Q spin away from the 1x frames, frame 0 facing left)")
    ap.add_argument("--no-head", action="append", default=[], metavar="TAG:I,J",
                    help="frames that keep Codex's head (lying, turned: karma dead:1,2,3,4,5,6,7)")
    ap.add_argument("--props", action="append", default=[], metavar="TAG:I=J",
                    help="frame I's parts apart from the body (a dropped ring, fans) replaced by frame J's, on the "
                         "same ground - they lie still once fallen (karma dead:2=7)")
    ap.add_argument("--settle", action="append", default=[], metavar="TAG",
                    help="every frame of TAG moved whole so its soles (the lowest row) are on the idle's and their "
                         "middle on the idle's feet middle, the frame grown evenly where it must (its centre, the pivot, "
                         "kept): garen spin - Codex's frames stood up to 18 hd px apart, one 9 rows up, and a turn on the "
                         "spot drifted (「盖伦放E的时候模型不会旋转了？」)")
    ap.add_argument("--same", action="append", default=[], metavar="TAG:I=J",
                    help="frame I of TAG is frame J's drawing, its lowest row on frame I's skeleton's lowest row (a "
                         "drawing that does not match its neighbours; vladimir dead:5=4 dead:6=4 dead:7=4 - Codex drew "
                         "the last three lying frames apart, a different crumpled body from frames 3-4)")
    a = ap.parse_args()
    hero, s = a.hero, a.scale
    deliveries = []
    for folder in a.delivery:
        with open(os.path.join(folder, "cells.json"), encoding="utf-8") as f:
            deliveries.append((folder, json.load(f)))
    cells = deliveries[0][1]
    px, k = cells["px_per_square"], cells["ppu"] * s
    for folder, c in deliveries[1:]:
        if (c["px_per_square"], c["ppu"]) != (px, cells["ppu"]):
            sys.exit(f"{folder}: px {c['px_per_square']} PPU {c['ppu']}, the first delivery's px {px} PPU {cells['ppu']}")
    # the frames go to assets/source/ppu/orig at the pack's PPU; ppu_restyle.py brings them to the game's (ORIG_PPU)
    import ppu_restyle as RS
    drawn_at = RS.ORIG_PPU.get(hero, P.PPU.get(hero))
    if drawn_at is None or abs(drawn_at - k) > 1e-3:
        sys.exit(f"{hero}: the PPU its frames are drawn at (ppu_restyle.py ORIG_PPU, else ppu_hd.py PPU) must be {k:g} "
                 f"(the pack's {cells['ppu']:g} x --scale {s})")
    dpath = a.design or os.path.join(PACKS, hero, "design", f"{hero}_design_1x.png")
    design = np.asarray(Image.open(dpath).convert("RGBA")).copy()
    design[..., 3] = np.where(design[..., 3] > 0, 255, 0)
    pal = np.unique(design[design[..., 3] > 0][:, :3], axis=0).astype(int)
    sheet = P.read_sheet(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    got = {}
    for folder, dcells in deliveries:
      for im in dcells["images"]:
        p = os.path.join(folder, im["file"])
        if os.path.isfile(p):
            sq, mixed = squares(p, px)
        else:
            # not delivered: the frames Codex did draw, one pixel per square, into a sheet of the pack's size
            sq, mixed = np.zeros((im["squares"][1], im["squares"][0], 4), np.uint8), 0
            found = []
            for m in im["cells"]:
                f1 = os.path.join(folder, "frames_1x", f"{m['tag']}_{m['frame']:02d}.png")
                x, y, w, h = m["rect"]
                if os.path.isfile(f1):
                    one = np.asarray(Image.open(f1).convert("RGBA"))
                    if one.shape[:2] != (h, w):
                        sys.exit(f"{f1}: {one.shape[1]}x{one.shape[0]}, its cell {w}x{h}")
                    sq[y:y + h, x:x + w] = one
                    found.append(m["frame"])
            print(f"{im['file']}: not delivered; frames_1x has {im['cells'][0]['tag']} {found or 'none'}")
            im = dict(im, cells=[m for m in im["cells"] if m["frame"] in found])
        sq[sq[..., 3] < 128] = 0
        sq[..., 3] = np.where(sq[..., 3] > 0, 255, 0)
        sq, recoloured = to_palette(sq, pal)
        if tuple(sq.shape[1::-1]) != tuple(im["squares"]):
            sys.exit(f"{im['file']}: {sq.shape[1]}x{sq.shape[0]} squares, the pack's {im['squares']}")
        inside = np.zeros(sq.shape[:2], bool)
        for m in im["cells"]:
            x, y, w, h = m["rect"]
            inside[y:y + h, x:x + w] = True
        lost = int((sq[..., 3] > 0)[~inside].sum())
        print(f"{im['file']}: {mixed} mixed squares, {recoloured} recoloured, {lost} drawn outside the cells (dropped)")
        for m in im["cells"]:
            x, y, w, h = m["rect"]
            cell = up(sq[y:y + h, x:x + w], s)
            fw, fh = m["frame_size"]
            one = sheet[m["tag"]][m["frame"]][0]
            FW, FH = round(one.shape[1] * k), round(one.shape[0] * k)
            g = max(0, -m["frame_top"] * s)
            FH += 2 * g
            # the cell's origin so that its pivot (fw/2 - left, fh/2 - top in squares) is the frame's centre (packs
            # from before frame_left: the cell spans the frame's whole width)
            ox = round(FW / 2 - (fw / 2 - m.get("frame_left", 0)) * s)
            oy = round(FH / 2 - (fh / 2 - m["frame_top"]) * s)
            fr = np.zeros((FH, FW, 4), np.uint8)
            cy0, cx0 = max(0, -oy), max(0, -ox)
            cy1, cx1 = min(cell.shape[0], FH - oy), min(cell.shape[1], FW - ox)
            cut = int((cell[..., 3] > 0).sum()) - int((cell[cy0:cy1, cx0:cx1, 3] > 0).sum())
            if cut:
                print(f"  {m['tag']}[{m['frame']}]: {cut} pixels past the frame (dropped)")
            fr[oy + cy0:oy + cy1, ox + cx0:ox + cx1] = cell[cy0:cy1, cx0:cx1]
            if a.sole_fix:
                # the cell's bottom against the idle's soles (bottom edges, from the frame's centre)
                si = P.scale_any(sheet["idle"][0][0], k)
                idle_sole = np.nonzero(si[..., 3].any(axis=1))[0].max() + 1 - si.shape[0] / 2
                down = int(round(idle_sole - (oy + cell.shape[0] - FH / 2)))
                if 0 < down <= int(np.ceil(k)):
                    fr[down:] = fr[:FH - down].copy()
                    fr[:down] = 0
            specks = drop_specks(fr)
            if specks:
                print(f"  {m['tag']}[{m['frame']}]: specks of {specks} pixels apart from the figure (dropped)")
            got.setdefault(m["tag"], {})[m["frame"]] = fr
    for spec in a.same:
        tag, ij = spec.split(":")
        i, j = (int(v) for v in ij.split("="))
        got[tag][i] = same_as(got[tag][j], got[tag][i].shape[:2], sheet[tag][i][0], k, sheet["idle"][0][0])
        print(f"{tag}[{i}]: frame {j}'s drawing, on its own skeleton's lowest row")
    for spec in a.props:
        tag, ij = spec.split(":")
        i, j = (int(v) for v in ij.split("="))
        n_ = swap_props(got[tag][i], got[tag][j], sheet[tag][i][0], sheet[tag][j][0], k)
        print(f"{tag}[{i}]: {n_} pixels apart from the body taken from frame {j}")
    design_s = up(design, s)
    if a.paste_head:
        skip = set()
        for spec in a.no_head:
            tag, ids = spec.split(":")
            skip |= {(tag, int(v)) for v in ids.split(",")}
        region = None
        if a.head_region:
            region = np.zeros(design_s.shape[:2], bool)
            for box in a.head_region.split("+"):
                rr, cc = box.split(":")
                r0, r1 = (int(v) * s for v in rr.split("-"))
                c0, c1 = (int(v) * s for v in cc.split("-"))
                region[r0:r1 + s, c0:c1 + s] = True
        core = head_core(design_s, a.paste_head * s, region)
        match = None
        if a.head_match:
            rr, cc = a.head_match.split(":")
            r0, r1 = (int(v) * s for v in rr.split("-"))
            c0, c1 = (int(v) * s for v in cc.split("-"))
            match = np.zeros_like(core)
            match[r0:r1 + s, c0:c1 + s] = True
            match &= core
        idle1 = sheet["idle"][0][0]
        base, (x0, y0) = place_idle(design_s, idle1, k)
        tpl = idle1_head(idle1, int(np.ceil(a.paste_head * s / k)))
        at1 = find_1x(idle1, tpl)
        for tag in got:
            if tag == "idle":
                continue
            for i in sorted(got[tag]):
                if (tag, i) in skip:
                    continue
                f1 = sheet[tag][i][0]
                hit = find_1x(f1, tpl)
                fr = got[tag][i]
                H, W = fr.shape[:2]
                # the design's top-left: the idle's place against the centre, moved as the 1x head moved (x PPU)
                gx = x0 - base.shape[1] / 2 + W / 2 + k * ((hit[1] - f1.shape[1] / 2) - (at1[1] - idle1.shape[1] / 2))
                gy = y0 - base.shape[0] / 2 + H / 2 + k * ((hit[2] - f1.shape[0] / 2) - (at1[2] - idle1.shape[0] / 2))
                res = paste_head(fr, design_s, core, (int(round(gx)), int(round(gy))), a.head_search, match=match,
                                 ring=a.clear_ring, hair_above=a.clear_hair_above)
                print(f"{tag}[{i}]: head at {res['at']}{' mirrored' if res['mirrored'] else ''} (from the 1x: "
                      f"{res['guess']}, {res['match']}% of its pixels on Codex's), {res['cleared']} pixels of Codex's "
                      f"head and ring cleared")
    if a.head_rows:
        for tag in got:
            for i in got[tag]:
                n = clear_head_ghost(got[tag][i], design_s, a.head_rows * s)
                if n:
                    print(f"{tag}[{i}]: {n} pixels of the old head's outline round the pasted head (cleared)")
    idle = sheet["idle"]
    if a.design_run:
        run = design_run(design_s, RUN_LEGS[hero], len(sheet["run"]), s)
        base, (x0, y0) = place_idle(design_s, idle[0][0], k)
        for i, f in enumerate(run):
            H, W = got["run"][i].shape[:2]
            # the idle's place against the frame's centre: the same in the run (no sway); the frame grown alike at
            # both sides when the design is wider than it
            reach = max(base.shape[1] / 2 - x0, x0 + f.shape[1] - base.shape[1] / 2)
            while W < 2 * reach:
                W += 2
            cx = x0 - base.shape[1] / 2 + W / 2
            cy = y0 - base.shape[0] / 2 + H / 2
            out = np.zeros((H, W, 4), np.uint8)
            fy, fx = round(cy), round(cx)
            out[fy:fy + f.shape[0], fx:fx + f.shape[1]] = f
            got["run"][i] = out
        print(f"run: the design with its legs stepping, {len(run)} frames")
    fr, at = place_idle(design_s, idle[0][0], k)
    got["idle"] = {i: fr for i in range(len(idle))}
    print(f"idle: the design ({design_s.shape[1]}x{design_s.shape[0]}) at {at} in every one of {len(idle)} frames")
    def feet_of(f):
        ys, xs = np.nonzero(f[..., 3])
        low = ys >= ys.max() - 6
        return (xs[low].min() + xs[low].max() + 1) / 2 - f.shape[1] / 2, ys.max() + 1 - f.shape[0] / 2
    ix, iy = feet_of(got["idle"][0])
    for tag in a.settle:
        for i, f in got[tag].items():
            fx, fy = feet_of(f)
            dx, dy = int(round(ix - fx)), int(round(iy - fy))
            H, W = f.shape[:2]
            ys, xs = np.nonzero(f[..., 3])
            gx = max(0, -(xs.min() + dx), xs.max() + dx - (W - 1))
            gy = max(0, -(ys.min() + dy), ys.max() + dy - (H - 1))
            g = np.zeros((H + 2 * gy, W + 2 * gx, 4), np.uint8)
            g[ys + dy + gy, xs + dx + gx] = f[ys, xs]
            got[tag][i] = g
            print(f"{tag}[{i}]: moved {dx}, {dy} onto the idle's feet" + (f", frame grown by {2 * gx} x {2 * gy}" if gx or gy else ""))
    os.makedirs(SRC, exist_ok=True)
    for tag, frames in sheet.items():
        if not P.plain(tag):
            continue
        have = got.get(tag, {})
        if sorted(have) != list(range(len(frames))):
            lost = [i for i in range(len(frames)) if i not in have]
            kept = orig_frames(hero, tag)
            if not a.fill_from_sheet or kept is None or len(kept) != len(frames):
                sys.exit(f"{tag}: frames {lost} not delivered (--fill-from-sheet keeps the ones drawn before, "
                         f"assets/source/ppu/orig/{hero}_{tag}.png)")
            for i in lost:
                have[i] = kept[i]
            print(f"{tag}: frames {lost} not delivered - the ones drawn before kept")
        want = [(round(f.shape[1] * k), round(f.shape[0] * k)) for f, _ in frames]
        write_strip(hero, tag, [have[i] for i in range(len(frames))], want)
        print(f"assets/source/ppu/{hero}_{tag}.png: {len(frames)} frames")


def head_core(design, rows, region=None):
    """The design's head: its opaque part above `rows` joined side by side to the face (the largest part there; an
    ornament only touching it corner to corner - karma's fans - is not in it) -> bool mask in design coordinates."""
    from scipy import ndimage
    op = design[..., 3] > 0
    op[rows:] = False
    if region is not None:
        op &= region
    lab, n = ndimage.label(op)
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    return lab == (int(np.argmax(sizes)) + 1)


def idle1_head(idle1, rows):
    """The 1x idle's top `rows` (from its first opaque row): the head the 1x frames carry -> (rows, cols, colours)."""
    top = np.nonzero(idle1[..., 3] > 0)[0].min()
    ty, tx = np.nonzero(idle1[top:top + rows, ..., 3] > 0)
    ty = ty + top
    return ty, tx, idle1[ty, tx].astype(int)


def find_1x(f, tpl):
    """Where the 1x frame holds the 1x idle's head best: (wrong pixels, dx, dy) - the idle's head moved by (dx, dy)."""
    ty, tx, want = tpl
    H, W = f.shape[:2]
    best = None
    g = f.astype(int)
    for dy in range(-ty.min(), H - ty.max()):
        for dx in range(-tx.min(), W - tx.max()):
            bad = int((np.abs(g[ty + dy, tx + dx] - want).max(axis=1) > 0).sum())
            if best is None or bad < best[0]:
                best = (bad, dx, dy)
    return best


def jade_mask(fr):
    """Pixels of a jade green (karma's ring): green above red, blue at most a little above green."""
    r, gg, b = (fr[..., c].astype(int) for c in range(3))
    return (fr[..., 3] > 0) & (gg > r + 20) & (b < gg + 30)


def colour_set(img, mask, least=10):
    """The colours of img's pixels under mask that appear at least `least` times -> set of (r, g, b)."""
    from collections import Counter
    c = Counter(tuple(int(v) for v in p[:3]) for p in img[mask])
    return {k for k, n in c.items() if n >= least}


def in_colours(fr, cols):
    m = np.zeros(fr.shape[:2], bool)
    for c in cols:
        m |= (fr[..., 0] == c[0]) & (fr[..., 1] == c[1]) & (fr[..., 2] == c[2])
    return m & (fr[..., 3] > 0)


def best_place(fr, design, core, guess, search, match=None):
    """Where the head (`core` of `design`, top-left of the design near `guess`) falls best on Codex's drawing: the
    most of its pixels on pixels of their colour family (distance under 60), a little against the distance from the
    guess; within `search` pixels of it, or anywhere in the frame and each way round - mirrored too (a spin's frame
    facing left: yasuo eq 0) - when `search` is 0 (coarse steps, then fine). -> (score, dx, dy, close, mirrored)."""
    H, W = fr.shape[:2]
    g = fr.astype(int)
    best = None
    if match is not None:
        core = match
    for mirrored in ((False, True) if not search else (False,)):
        c = core[:, ::-1] if mirrored else core
        d = design[:, ::-1] if mirrored else design
        cy, cx = np.nonzero(c)
        want = d[cy, cx, :3].astype(int)
        # with a match part (the face) its skin counts three times: a dark ponytail drawn elsewhere must not outvote
        # the face (yasuo q3 4-5)
        r_, g_, b_ = want[:, 0], want[:, 1], want[:, 2]
        weight = np.where((match is not None) & (r_ > 120) & (r_ > g_) & (g_ > b_) & (r_ - b_ > 50) & (g_ > 60), 3, 1)

        def score(dx, dy):
            y, x = cy + guess[1] + dy, cx + guess[0] + dx
            ok = (y >= 0) & (y < H) & (x >= 0) & (x < W)
            if ok.mean() < 0.9:
                return None
            got = g[y[ok], x[ok]]
            hit = (got[:, 3] > 0) & (np.abs(got[:, :3] - want[ok]).sum(axis=1) < 60)
            close = int(hit.sum())
            return int((hit * weight[ok]).sum()) - (0.15 if not search else 0.5) * (abs(dx) + abs(dy)), close

        if search:
            spots = [(dx, dy) for dy in range(-search, search + 1) for dx in range(-search, search + 1)]
        else:
            spots = [(dx, dy) for dy in range(-H, H, 3) for dx in range(-W, W, 3)]
        top = None
        for dx, dy in spots:
            r = score(dx, dy)
            if r and (top is None or r[0] > top[0]):
                top = (r[0], dx, dy, r[1])
        if top and not search:
            for dy in range(top[2] - 2, top[2] + 3):
                for dx in range(top[1] - 2, top[1] + 3):
                    r = score(dx, dy)
                    if r and r[0] > top[0]:
                        top = (r[0], dx, dy, r[1])
        if top and (best is None or top[0] > best[0]):
            best = top + (mirrored,)
    return best


def paste_head(fr, design, core, guess, search, far=4, allow=5, match=None, ring=True, hair_above=True):
    """The design's head (`core`, design coordinates) pasted into `fr` with the design's top-left near `guess`: at the
    place within `search` pixels where most of its pixels fall on pixels of their colour family in Codex's drawing
    (colour distance under 60), nearer the guess on a tie. Then Codex's head round it goes: in its rows, the parts
    beside it that never reach more than `far` pixels from it (an arm reaches far), and above its face the bits under
    30 pixels (Codex's ring's outline) or mostly of the head's own colours (Codex's ponytail drawn higher: yasuo);
    and Codex's own ring (the
    largest part in the colours of the design's ring - the head's upper part) wherever the pasted one does not
    cover it, except next to the fans (their teal stripes and outline share the ring's colours)."""
    from scipy import ndimage
    H, W = fr.shape[:2]
    _, dx, dy, close, mirrored = best_place(fr, design, core, guess, search, match)
    n_match = int((match if match is not None else core).sum())
    if mirrored:
        # the head facing the other way: the design and its head mirrored, the guess kept for the same place
        design, core = design[:, ::-1], core[:, ::-1]
    cy, cx = np.nonzero(core)
    upper = core.copy()
    upper[cy.min() + int(0.55 * (cy.max() - cy.min())):] = False
    ring_cols = colour_set(design, upper)
    others = design[..., 3] > 0
    others[cy.max() + 1:] = False
    fan_cols = {c for c in colour_set(design, others & ~core) - ring_cols if sum(c) > 150}   # their light colours
    ring_px = in_colours(fr, ring_cols)
    lab_r, n_r = ndimage.label(ring_px, structure=np.ones((3, 3)))
    old_ring = np.zeros((H, W), bool)
    if n_r and ring:
        sizes = ndimage.sum(ring_px, lab_r, range(1, n_r + 1))
        old_ring = lab_r == int(np.argmax(sizes)) + 1
        old_ring &= ~ndimage.binary_dilation(in_colours(fr, fan_cols), structure=np.ones((3, 3)))
    ox, oy = guess[0] + dx, guess[1] + dy
    y, x = cy + oy, cx + ox
    ok = (y >= 0) & (y < H) & (x >= 0) & (x < W)
    M = np.zeros((H, W), bool)
    M[y[ok], x[ok]] = True
    fr[y[ok], x[ok]] = design[cy[ok], cx[ok]]
    ring_gone = old_ring & ~M
    fr[ring_gone] = 0
    band = np.zeros((H, W), bool)
    band[:cy.max() + oy + 1] = True        # from the frame's top: Codex's ring may stand higher than the pasted one
    rest = (fr[..., 3] > 0) & ~M & band
    lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
    dist = ndimage.distance_transform_edt(~M)
    face_top = cy.min() + oy + int(0.55 * (cy.max() - cy.min()))
    head_px = in_colours(fr, colour_set(design, core, least=3))
    gone = np.zeros((H, W), bool)
    for v in range(1, n + 1):
        z = lab == v
        if int((dist[z] > far).sum()) <= allow:
            gone |= z
        elif not z[face_top:].any() and (z.sum() < 30 or (hair_above and head_px[z].mean() > 0.6)):
            gone |= z          # a bit of Codex's ring's outline, or its own head's (ponytail) edge, above the face
    fr[gone] = 0
    # what is left of Codex's head as pieces apart from the figure (under 60 pixels, in the head's rows)
    op = fr[..., 3] > 0
    lab2, n2 = ndimage.label(op, structure=np.ones((3, 3)))
    for v in range(1, n2 + 1):
        z = lab2 == v
        if z.sum() < 60 and not (z & M).any() and not z[cy.max() + oy + 1:].any():
            fr[z] = 0
            gone |= z
    return {"at": (int(ox), int(oy)), "guess": tuple(int(v) for v in guess), "match": round(100 * close / n_match),
            "cleared": int(gone.sum() + ring_gone.sum()), "mirrored": mirrored}


def swap_props(dst, src, one_dst, one_src, k):
    """dst's parts apart from its largest part (the body) replaced by src's, both frames' ground (the lowest row of
    the 1x frame x k, the frame grown alike at both ends) on one row, their centres on one column. -> pixels put."""
    from scipy import ndimage

    def apart(fr):
        op = fr[..., 3] > 0
        lab, n = ndimage.label(op, structure=np.ones((3, 3)))
        sizes = ndimage.sum(op, lab, range(1, n + 1))
        return op & (lab != int(np.argmax(sizes)) + 1)

    def ground(fr, one):
        sk = P.scale_any(one, k)
        return np.nonzero(sk[..., 3].any(axis=1))[0].max() + (fr.shape[0] - sk.shape[0]) // 2

    dst[apart(dst)] = 0
    m = apart(src)
    dy = ground(dst, one_dst) - ground(src, one_src)
    dx = (dst.shape[1] - src.shape[1]) // 2
    ys, xs = np.nonzero(m)
    ok = (ys + dy >= 0) & (ys + dy < dst.shape[0]) & (xs + dx >= 0) & (xs + dx < dst.shape[1])
    dst[ys[ok] + dy, xs[ok] + dx] = src[ys[ok], xs[ok]]
    return int(ok.sum())


def clear_head_ghost(fr, design, rows, far=4, allow=5):
    """Where `fr` holds the design's top `rows` (its opaque pixels) exactly: clear the other parts in those rows
    that keep within `far` pixels of the block (at most `allow` pixels beyond). -> pixels cleared."""
    from scipy import ndimage
    ys, xs = np.nonzero(design[..., 3] > 0)
    t = design[ys.min():ys.min() + rows]
    ty, tx = np.nonzero(t[..., 3] > 0)
    want = t[ty, tx].astype(int)
    H, W = fr.shape[:2]
    at = None
    for dy in range(-ty.min(), H - ty.max()):
        for dx in range(-tx.min(), W - tx.max()):
            if (fr[ty + dy, tx + dx].astype(int) == want).all():
                at = (dx, dy)
                break
        if at:
            break
    if at is None:
        return 0
    dx, dy = at
    M = np.zeros((H, W), bool)
    M[ty + dy, tx + dx] = True
    band = np.zeros((H, W), bool)
    band[max(0, dy):dy + rows] = True
    rest = (fr[..., 3] > 0) & ~M & band
    lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
    dist = ndimage.distance_transform_edt(~M)
    gone = np.zeros((H, W), bool)
    for v in range(1, n + 1):
        z = lab == v
        if int((dist[z] > far).sum()) <= allow:
            gone |= z
    fr[gone] = 0
    return int(gone.sum())


# The run legs drawn from the design (--design-run): per leg the design's own pixels, row -> (first, last column) -
# the shin (swung about the knee row: each row moved in proportion) and the boot (from `boot` down, moved whole);
# `dx` = the foot's range forward and back (the near foot never reaches the far one: 「那走路时候脚也变形了啊」),
# `phase` = where in the cycle it starts. `lining` = the coat's inside colour left behind the shins inside the coat.
RUN_LEGS = {
    "vladimir": {
        "knee": 69, "boot": 75, "lift": 2, "inside_to": 72, "lining": (0x42, 0x00, 0x12),
        # the body (everything but the legs) rows down per frame: lowest as a foot lands, as the 1x run (frames 0
        # and 4 one 1x row down), passing through 1 between (「有点僵硬啊吸血鬼」)
        "bob": [2, 1, 0, 1, 2, 1, 0, 1],
        # the coat's inside behind the legs (row -> columns between the front flaps); the rest of the body is in
        # front of them - the legs are inside the coat
        "back": {69: (16, 36), 70: (16, 36), 71: (15, 36), 72: (16, 35), 73: (22, 34)},
        # the hands (bell cuff and claws, row -> columns), each moved whole within `dx` (columns), forward as the
        # leg on its side goes back; only ever to where it covers (the near hand back, or the far hand forward,
        # would open a slit of ground next to the coat); the near one over everything, the far one behind the body
        "hands": [
            {"name": "far", "leg": 0, "dx": (-1, 0), "behind": True,
             "rows": {47: (33, 40), 48: (33, 45), 49: (33, 44), 50: (33, 44), 51: (33, 43), 52: (33, 43),
                      53: (34, 45), 54: (35, 46), 55: (35, 47), 56: (35, 48), 57: (35, 48), 58: (36, 44),
                      59: (38, 45), 60: (39, 45), 61: (39, 46), 62: (40, 46), 63: (40, 46), 64: (45, 46),
                      65: (46, 46)}},
            {"name": "near", "leg": 1, "dx": (0, 1), "behind": False,
             "rows": {46: (8, 15), 47: (3, 15), 48: (3, 15), 49: (4, 15), 50: (5, 15), 51: (6, 15), 52: (5, 15),
                      53: (3, 15), 54: (2, 15), 55: (1, 15), 56: (0, 15), 57: (0, 15), 58: (4, 15), 59: (3, 15),
                      60: (3, 15), 61: (3, 13), 62: (3, 13), 63: (9, 13), 64: (10, 12)}},
        ],
        "legs": [
            {"name": "far", "phase": 0.5, "dx": (-1, 3),
             "rows": {70: (27, 31), 71: (27, 31), 72: (28, 32), 73: (29, 31), 74: (29, 31), 75: (28, 32),
                      76: (28, 33), 77: (27, 34), 78: (27, 37), 79: (27, 38), 80: (27, 39), 81: (27, 39)}},
            {"name": "near", "phase": 0.0, "dx": (-3, 1),
             "rows": {70: (17, 22), 71: (18, 22), 72: (18, 22), 73: (18, 21), 74: (18, 21), 75: (17, 21),
                      76: (17, 21), 77: (16, 22), 78: (16, 22), 79: (15, 23), 80: (15, 23), 81: (15, 23)}},
        ],
    },
}


def design_run(design, spec, n, s=1):
    """`n` run frames of the design: the body as it is (no part of it moves), the legs of `spec` (RUN_LEGS) stepping
    half a cycle apart. A foot slides back on the ground (dx from its front to its back end) and swings forward in
    the air (lifted up to `lift`); its shin leans from the knee to it, rows moved in proportion, and shortens as the
    foot lifts (rows dropped, its top and its bottom kept) - the boot is never drawn over the shin, never cut, never
    sheared. The coat's inside (`back`) first, then the far leg, the near leg and the rest of the body over them (the
    legs are inside the coat); where a shin was inside the coat the coat's lining shows. The body
    moves down `bob` rows as a whole (nothing of it reshaped); the shins take it up, from the knee (with the body)
    to the boot (on the ground)."""
    H, W = design.shape[:2]
    knee, boot, lift = spec["knee"] * s, spec["boot"] * s, spec["lift"] * s
    body = design.copy()
    back_m = np.zeros((H, W), bool)
    for r, (c0, c1) in spec.get("back", {}).items():
        for k in range(s):
            back_m[r * s + k, c0 * s:(c1 + 1) * s] = True
    masks = []
    for leg in spec["legs"]:
        m = np.zeros((H, W), bool)
        for r, (c0, c1) in leg["rows"].items():
            for k in range(s):
                m[r * s + k, c0 * s:(c1 + 1) * s] = True
        m &= design[..., 3] > 0
        masks.append(m)
        inside = m.copy()
        inside[(spec["inside_to"] + 1) * s:] = False
        body[m] = 0
        body[inside] = spec["lining"] + (255,)
        back_m |= inside
    back_m &= body[..., 3] > 0
    back = np.where(back_m[..., None], body, 0).astype(np.uint8)
    hands = []
    for hand in spec.get("hands", []):
        m = np.zeros((H, W), bool)
        for r, (c0, c1) in hand["rows"].items():
            for k in range(s):
                m[r * s + k, c0 * s:(c1 + 1) * s] = True
        m &= (body[..., 3] > 0) & ~back_m
        hands.append((hand, np.where(m[..., None], body, 0).astype(np.uint8)))
        body[m] = 0
    front = np.where(back_m[..., None], 0, body).astype(np.uint8)
    from scipy import ndimage
    op0 = design[..., 3] > 0
    holes0 = ndimage.binary_fill_holes(op0) & ~op0
    frames = []
    for i in range(n):
        by = spec.get("bob", [0] * n)[i % len(spec.get("bob", [0]))] * s
        down = lambda a: np.concatenate([np.zeros((by,) + a.shape[1:], a.dtype), a[:H - by]]) if by else a
        out = down(back).copy()
        for leg, m in zip(spec["legs"], masks):
            a = 2 * np.pi * (i / n + leg["phase"])
            lo, hi = leg["dx"]
            dx = ((lo + hi) / 2 + (hi - lo) / 2 * np.cos(a)) * s
            up_ = lift * max(0.0, -np.sin(a))
            lay = np.zeros_like(design)
            for y in range(H):
                xs = np.nonzero(m[y])[0]
                if not len(xs):
                    continue
                t = min(1.0, max(0.0, (y - knee + 1) / (boot - knee + 1)))
                ny = y + int(np.floor(by * (1 - t) - up_ * t + 0.5))
                sh = int(np.floor(dx * t + 0.5))
                ok = (xs + sh >= 0) & (xs + sh < W)
                if 0 <= ny < H:
                    lay[ny, xs[ok] + sh] = design[y, xs[ok]]
            out[lay[..., 3] > 0] = lay[lay[..., 3] > 0]
        def put_hand(hand, img):
            leg = spec["legs"][hand["leg"]]
            # the hand forward (+) while the leg on its side goes back
            lo, hi = hand["dx"]
            hx = int(np.floor((lo + (hi - lo) * (1 - np.cos(2 * np.pi * (i / n + leg["phase"]))) / 2) * s + 0.5))
            sh = np.zeros_like(img)
            if hx >= 0:
                sh[:, hx:] = img[:, :W - hx]
            else:
                sh[:, :hx] = img[:, -hx:]
            sh = down(sh)
            out[sh[..., 3] > 0] = sh[sh[..., 3] > 0]
        for hand, img in hands:
            if hand["behind"]:
                put_hand(hand, img)
        fr_ = down(front)
        out[fr_[..., 3] > 0] = fr_[fr_[..., 3] > 0]
        for hand, img in hands:
            if not hand["behind"]:
                put_hand(hand, img)
        # ground shut in between a moved boot or shin and the coat that the design does not have (a crack, memory
        # gap-check) takes the lining's shade
        from scipy import ndimage
        o = out[..., 3] > 0
        own = np.zeros_like(holes0)
        own[by:] = holes0[:H - by]
        pockets, n_ = ndimage.label(ndimage.binary_fill_holes(o) & ~o & ~own)
        for v in range(1, n_ + 1):
            z = pockets == v
            if z.sum() <= 8 * s * s:
                out[z] = spec["lining"] + (255,)
        frames.append(out)
    return frames


def same_as(src, shape, one, k, idle1=None):
    """`src` (a frame) in a frame of `shape`, centred across, its lowest opaque row on the lowest row of the 1x
    frame `one` scaled by k (the frame grown alike at both ends: the 1x frame centred in it) - never below the 1x
    idle's soles (a prop falling past the ground in the 1x frame: karma dead 2). A drawing that does not fit grows
    the frame alike at both ends (its centre, the pivot, kept)."""
    H, W = shape
    sk = P.scale_any(one, k)
    ys, xs = np.nonzero(src[..., 3] > 0)
    while True:
        want = np.nonzero(sk[..., 3].any(axis=1))[0].max() + (H - sk.shape[0]) // 2
        if idle1 is not None:
            si = P.scale_any(idle1, k)
            sole = np.nonzero(si[..., 3].any(axis=1))[0].max() - si.shape[0] / 2      # below the centre
            want = min(want, int(round(H / 2 + sole)))
        dy, dx = want - ys.max(), (W - src.shape[1]) // 2
        if (xs + dx).min() < 0 or (xs + dx).max() >= W:
            W += 2
        elif (ys + dy).min() < 0:
            H += 2
        else:
            break
    out = np.zeros((H, W, 4), np.uint8)
    out[ys + dy, xs + dx] = src[ys, xs]
    return out


def drop_specks(fr, below=4, at_edge=12):
    """Clear the parts of fewer than `below` pixels (8-connected) - a dot left floating by the image model
    (「别留多余的像素」) - and of fewer than `at_edge` within 3 pixels of the frame's side (a sliver cut from a drawing).
    -> their sizes."""
    from scipy import ndimage
    op = fr[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    edge = set(np.unique(np.concatenate([lab[:, :3].ravel(), lab[:, -3:].ravel(), lab[:3].ravel()]))) - {0}
    small = [v + 1 for v, z in enumerate(sizes) if z < below or (z < at_edge and v + 1 in edge)]
    fr[np.isin(lab, small)] = 0
    return [int(sizes[v - 1]) for v in small]


def up(a, s):
    return a if s == 1 else np.repeat(np.repeat(a, s, axis=0), s, axis=1)


if __name__ == "__main__":
    main()
