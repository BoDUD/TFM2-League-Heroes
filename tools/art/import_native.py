#!/usr/bin/env python3
"""Import a native-size redraw (assets/source/NATIVE_REDRAW.md) as the hero's game sprite.

    python tools/art/import_native.py [--hero lux --hero ashe] [--review DIR]

Source, assets/source/native/: <hero>_<tag>.png from the GPT/Codex run - every game pixel one exact
8x8 block, the frames in 56x64-pixel cells (or the size the cells table gives) read left to right,
top to bottom (native_refs.layout) - and <hero>_cells.json, written with the references by
native_refs.py (from round-1 game frames) or tools/lol/native_pose.py (straight from League's
clips): where each reference frame's pivot stood in its cell, and its duration. The redraw was drawn over those references, so each new
frame is cut out of its cell around that pivot and stands where the round-1 frame stood (head
tracks, lunges, the R wand inside the beam, the death knock-back), for the same time. The blocks are
read one pixel each: no resampling, no new palette, no added outline.
Two fixes for the loops, where every pixel of jitter shows:
  - idle and run: each frame moves sideways so its head sits at the strip's mean head column. The
    head is idle frame 1's top rows, found by exact match (Codex pasted one verified head into every
    frame); frames placed by their bounding box had it 1-2 px off.
  - ORDER: Lux's idle arrived breathing down, down, down, up, down, up; its frames 5 and 6 swap.
    Master Yi's raised sword is the top of every frame, so he is steadied on League's head joint, where
    his helmet was pasted (PASTED), and his one-frame idle on the frame it shows. Codex's Fiddlesticks
    (design B) holds his scythe over his head and redrew the head in every run frame: he is steadied on
    his eyes, the one colour nothing else uses (EYES; his run's eyes wandered 12 px about the pivot).
Then <hero>_retouch.json, when there is one, retouches single pixels of the cut frames (Lee Sin's mouth,
nose and face side; Lux's run, where her wand's gold end read as a gold foot): x, y from the pivot, the colour expected there and the new one. A pixel that no longer has
the expected colour stops the import, so edits made for one version of the strips never land on another.
Writes league/champions/league_<hero>. The effects still come from tools/art/import_<hero>.py, which
writes the round-1 body only with --body.
--review DIR writes <hero>_native.png: every frame at 4x around its pivot (pivot column, feet line).
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from native_refs import CELL, Z, layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
HEAD_ROWS = 12                  # idle frame 1's top rows: the head
SURE = 0.9                      # share of the head's pixels that must match exactly
STEADY = ("idle", "run")
ORDER = {("lux", "idle"): [0, 1, 2, 3, 5, 4],
         # League leans his upper body a square forward in idle 4-5 and back in 6, and every frame's head
         # is voted anew, so the face swung and changed shape as he breathed (the user). Frame 1 in every
         # slot, breathing through BOB instead.
         ("yasuo", "idle"): [0, 0, 0, 0, 0, 0],
         # the same one drawing for Leona (her face is pasted, and League's idle barely moves)
         ("leona", "idle"): [0, 0, 0, 0, 0, 0],
         # and for Teemo: his pasted head rode League's breath a row up and down while the body under it was
         # voted anew each frame (100-480 pixels changed between idle frames)
         ("teemo", "idle"): [0, 0, 0, 0, 0, 0],
         # and for Master Yi: one pasted helmet, and a body voted anew each frame would shimmer
         ("masteryi", "idle"): [0, 0, 0, 0, 0, 0],
         # and Annie, whose drawn head is pasted too
         ("annie", "idle"): [0, 0, 0, 0, 0, 0],
         # and Miss Fortune (a drawn head under a pasted tricorne)
         ("missfortune", "idle"): [0, 0, 0, 0, 0, 0],
         # and Janna (pasted head, a body restyled from League's idle)
         ("janna", "idle"): [0, 0, 0, 0, 0, 0],
         # and Malphite, whose drawn head sits on his shoulders (restyle "anchor")
         ("malphite", "idle"): [0, 0, 0, 0, 0, 0],
         # and Ekko (a drawn head pasted on League's crouch)
         ("ekko", "idle"): [0, 0, 0, 0, 0, 0],
         # and Yone (a drawn masked head, a body restyled from League's idle)
         ("yone", "idle"): [0, 0, 0, 0, 0, 0],
         # and Ezreal (a drawn head with goggles, a body restyled from League's idle)
         ("ezreal", "idle"): [0, 0, 0, 0, 0, 0],
         # and Thresh (a drawn skull pasted on a body restyled from League's idle)
         ("thresh", "idle"): [0, 0, 0, 0, 0, 0],
         # and Kayle (a drawn head pasted on League's hovering idle)
         ("kayle", "idle"): [0, 0, 0, 0, 0, 0],
         # and Fiddlesticks (Codex's redraw, design B: the six idle frames are one drawing)
         ("fiddlesticks", "idle"): [0, 0, 0, 0, 0, 0],
         # and Morgana (Codex's design B, which tools/art/tidy_morgana.py writes into all six)
         ("morgana", "idle"): [0, 0, 0, 0, 0, 0]}
# (hero, tag): (y, slots) - in those slots everything at or above pivot row y moves down a row (the row under
# it is covered): one frame breathing, the face the same drawing throughout. Leona's shield covers her from
# the chest to the ankles, so she sinks down to its tip and only the boots stay (a seam across the shield
# would cut it in two).
BOB = {("yasuo", "idle"): (-2, [2, 3, 4]),
       ("leona", "idle"): (8, [2, 3, 4]),
       # Teemo's boots are seven rows: the lowest five stay, the rest of him sinks (seam in the shins)
       ("teemo", "idle"): (6, [2, 3, 4]),
       ("masteryi", "idle"): (1, [2, 3, 4]),
       # Annie sinks down to her shins; the shoes and the lowest stripes of her leggings stay
       ("annie", "idle"): (6, [2, 3, 4]),
       # Miss Fortune's boots start four rows under the pivot: the seam runs through their shafts
       ("missfortune", "idle"): (6, [2, 3, 4]),
       # Janna floats: all of her, down to the soles 3 px above the ground, sinks a row and rises again
       ("janna", "idle"): (12, [2, 3, 4]),
       # Malphite's short legs: the seam across his shins, his rock feet stay
       ("malphite", "idle"): (6, [2, 3, 4]),
       # Ekko crouches: the seam across his shins, the boots stay
       ("ekko", "idle"): (6, [2, 3, 4]),
       # Yone's hakama reaches his ankles: the seam across its hem, his feet stay
       ("yone", "idle"): (6, [2, 3, 4]),
       # Ezreal: the seam across his shins, the boots stay
       ("ezreal", "idle"): (6, [2, 3, 4]),
       # Thresh's robe hangs to his shins: the seam across its hem, his boots stay
       ("thresh", "idle"): (6, [2, 3, 4]),
       # Kayle floats 3 px up like Janna and sinks a row down to her soles; only her sword's tip, on the
       # ground line, stays
       ("kayle", "idle"): (10, [2, 3, 4]),
       # Fiddlesticks: the seam across his stilts, the claw feet stay
       ("fiddlesticks", "idle"): (6, [2, 3, 4]),
       # Morgana's gown reaches the ground: the seam four rows over its hem, where two rows differ only in
       # shading; the hem and the train's lowest rows stay
       ("morgana", "idle"): (7, [2, 3, 4])}
CROWN = {"leesin"}              # heroes whose head template starts at the crown (a braid stands above it)
PASTED = {"masteryi", "janna", "ekko",   # steadied on the head restyle_native pasted: his raised sword is the top of every frame
          "thresh"}  # his hand-drawn head, pasted on League's head joint: steadied there
# heroes steadied on their eyes: (R, G, B) of a colour only the eyes use; the head column is the eyes' middle
EYES = {"fiddlesticks": (200, 224, 96),   # Codex's design B: the scythe's blade is the top of every frame
        "kayle": (226, 138, 8)}           # Codex's redraw: her wings rise above her head, the amber is the eyes'


def blocks(path):
    """The image read one pixel per 8x8 block; exits if a block is not one flat colour."""
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    H, W = a.shape[:2]
    if H % Z or W % Z:
        sys.exit(f"{path}: {W}x{H} is not a multiple of {Z}")
    b = a.reshape(H // Z, Z, W // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    out = b[:, 0, :, 0].copy()
    op = out[..., 3] >= 128
    out[~op] = 0
    out[op, 3] = 255
    return out


def cells(hero, tag, n, cell=CELL):
    """The n frames of a strip, one RGBA array per cell (56x64 px unless the hero's cells table
    says otherwise: Lee Sin's are 64x72)."""
    a = blocks(os.path.join(SRC, f"{hero}_{tag}.png"))
    cols, rows = layout(n)
    if a.shape[:2] != (rows * cell[1], cols * cell[0]):
        sys.exit(f"{hero}_{tag}.png: expected {cols}x{rows} cells of {cell[0]}x{cell[1]} px at {Z}x")
    return [a[k // cols * cell[1]:(k // cols + 1) * cell[1], k % cols * cell[0]:(k % cols + 1) * cell[0]]
            for k in range(n)]


def head_of(frame, crown=False):
    """The top HEAD_ROWS rows of the frame. crown=True starts at the crown instead - the first row
    at least half as wide as the widest of the rows below it - for a hero with a thin braid standing
    above the head (Lee Sin): its tip moves a pixel between idle frames and matched one frame 1 px
    off. (Lux and Ashe keep the old rule; the crown rule would move a Lux idle frame.)"""
    op = frame[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    top = ys[0]
    if crown:
        widths = [op[y].sum() for y in range(ys[0], min(ys[0] + 16, ys[-1] + 1))]
        top = ys[0] + next(i for i, w in enumerate(widths) if w >= 0.5 * max(widths))
    band = frame[top:top + HEAD_ROWS]
    xs = np.nonzero(band[..., 3].any(0))[0]
    return band[:, xs[0]:xs[-1] + 1]


def pasted_head(hero):
    """The head restyle_native.py pastes into every frame (the design sheet's head rect without its
    cut pixels), for a hero whose hair swings above it ("hair_part" in its poses.json: Yasuo's
    ponytail is the top of every frame and changes each time) or whose head is pasted on the torso
    (restyle "anchor": Malphite's back spikes, voted anew each frame, are the top of every frame); None
    for everyone else. A hero in PASTED
    is steadied on League's head joint, where its head was pasted (Master Yi's sword crosses his helmet
    in most run frames, so the helmet is not found whole)."""
    if hero in PASTED:
        return "joint"
    path = os.path.join(ROOT, "assets", "source", hero, "poses.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    if "restyle" not in spec or not (spec.get("hair_part") or spec["restyle"]["head"].get("anchor")):
        return None
    if spec["restyle"]["head"].get("mode") == "voted":
        return "joint"      # no two heads alike: steady on League's head joint from the cells table
    x0, y0, w, h = spec["restyle"]["head"]["rect"]
    tpl = blocks(os.path.join(SRC, f"{hero}_native.png"))[y0:y0 + h, x0:x0 + w].copy()
    for x, y in spec["restyle"]["head"].get("cut", []):
        tpl[y - y0, x - x0] = 0
    return tpl


def eye_column(frame, rgb):
    """The middle column of the pixels of colour rgb (a hero's eyes), rounded; None when there are none."""
    m = (frame[..., 3] > 0) & (frame[..., :3] == np.array(rgb, np.uint8)).all(-1)
    xs = np.nonzero(m)[1]
    return int(np.floor(xs.mean() + 0.5)) if len(xs) else None


def find(frame, tpl):
    """(share of tpl's pixels matched exactly, x, y) at the best spot."""
    th, tw = tpl.shape[:2]
    m = tpl[..., 3] > 0
    best = (0.0, 0, 0)
    for y in range(frame.shape[0] - th + 1):
        for x in range(frame.shape[1] - tw + 1):
            s = ((frame[y:y + th, x:x + tw] == tpl).all(-1) & m).sum() / m.sum()
            if s > best[0]:
                best = (s, x, y)
    return best


def build(hero):
    """{tag: [(frame centred on its pivot, ms)]} and {tag: [(head column from the pivot, moved)]}."""
    with open(os.path.join(SRC, f"{hero}_cells.json"), encoding="utf-8") as f:
        spec = json.load(f)
    table, cell = spec["tags"], tuple(spec.get("cell", CELL))
    head = pasted_head(hero)
    joint = isinstance(head, str)
    if head is None and hero not in EYES:
        head = head_of(cells(hero, "idle", len(table["idle"]), cell)[0], crown=hero in CROWN)
    sheet, report = {}, {}
    for tag, rows in table.items():
        fr = cells(hero, tag, len(rows), cell)
        if joint:
            hx = [int(np.floor(r["head"][0] + 0.5)) - r["pivot"][0] for r in rows]
        elif hero in EYES:
            cols = [eye_column(f, EYES[hero]) for f in fr]
            hx = [None if c is None else c - r["pivot"][0] for c, r in zip(cols, rows)]
        else:
            found = [find(f, head) for f in fr]
            hx = [x - r["pivot"][0] if s >= SURE else None for (s, x, _), r in zip(found, rows)]
        dx = [0] * len(fr)
        # a PASTED hero's idle is one frame (ORDER): steady on the frames shown, or it moves off its pivot
        used = sorted(set(ORDER.get((hero, tag), range(len(fr))))) if hero in PASTED else range(len(fr))
        sure = [hx[k] for k in used if hx[k] is not None]
        if tag in STEADY and sure:
            target = round(sum(sure) / len(sure))
            dx = [0 if h is None else target - h for h in hx]
        order = ORDER.get((hero, tag), range(len(fr)))
        sheet[tag] = [(G.centre_frame(fr[k], dx[k] - rows[k]["pivot"][0], -rows[k]["pivot"][1]), rows[slot]["ms"])
                      for slot, k in enumerate(order)]
        report[tag] = [(None if hx[k] is None else hx[k] + dx[k], dx[k]) for k in order]
    return sheet, report


def touch_up(hero, sheet):
    """Apply <hero>_retouch.json to the cut frames in place; the number of pixels changed."""
    path = os.path.join(SRC, f"{hero}_retouch.json")
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    pal = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in spec["palette"].items()}
    n = 0
    for tag, frames in spec["frames"].items():
        for k, pixels in enumerate(frames):
            a = sheet[tag][k][0]
            hh, hw = a.shape[0] // 2, a.shape[1] // 2
            for x, y, was, now in pixels:
                r, c = hh + y, hw + x
                p = a[r, c] if 0 <= r < a.shape[0] and 0 <= c < a.shape[1] else None
                if p is None or (p[3] != 0 if was == "." else p[3] == 0 or tuple(p[:3]) != pal[was]):
                    sys.exit(f"{os.path.basename(path)}: {tag} frame {k + 1} at ({x}, {y}) is not '{was}' any more")
                a[r, c] = (0, 0, 0, 0) if now == "." else pal[now] + (255,)
                n += 1
    return n


def breathe(hero, sheet):
    """BOB: move the upper body of the listed slots down a row (after the retouch, which is drawn on the frame
    before it moves)."""
    for (h, tag), (y0, slots) in BOB.items():
        if h != hero or tag not in sheet:
            continue
        for k in slots:
            a, ms = sheet[tag][k]
            cut = a.shape[0] // 2 + y0 + 1           # array rows before `cut` sit at pivot rows <= y0
            b = a.copy()
            b[1:cut + 1] = a[0:cut]
            b[0] = 0
            sheet[tag][k] = (b, ms)


def flatness(frames):
    """Share of opaque pixels whose right neighbour is opaque and the same colour."""
    same = n = 0
    for a in frames:
        op = a[..., 3] > 0
        pair = op[:, :-1] & op[:, 1:]
        same += (pair & (a[:, :-1, :3] == a[:, 1:, :3]).all(-1)).sum()
        n += op.sum()
    return same / n


def review(hero, sheet, out, z=4):
    hw = max(a.shape[1] // 2 for fr in sheet.values() for a, _ in fr)
    hh = max(a.shape[0] // 2 for fr in sheet.values() for a, _ in fr)
    W, H = 2 * hw + 1, 2 * hh + 1
    cols = max(len(fr) for fr in sheet.values())
    img = Image.new("RGBA", (cols * (W + 2) * z, len(sheet) * (H + 2) * z), (72, 76, 84, 255))
    for j, fr in enumerate(sheet.values()):
        for i, (a, _) in enumerate(fr):
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            guide = np.zeros((H, W, 4), np.uint8)
            guide[hh + 12, :] = (96, 160, 96, 255)          # the row under the soles
            guide[:, hw] = (96, 160, 96, 255)               # the pivot column
            c.alpha_composite(Image.fromarray(guide, "RGBA"))
            c.alpha_composite(Image.fromarray(a, "RGBA"), (hw - a.shape[1] // 2, hh - a.shape[0] // 2))
            img.alpha_composite(c.resize((W * z, H * z), Image.NEAREST), (i * (W + 2) * z, j * (H + 2) * z))
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, f"{hero}_native.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append", help="default: every <hero>_cells.json in assets/source/native")
    ap.add_argument("--review", help="write a frame sheet per hero to this folder")
    args = ap.parse_args()
    heroes = args.hero or sorted(os.path.basename(p)[:-len("_cells.json")]
                                 for p in glob.glob(os.path.join(SRC, "*_cells.json")))
    for hero in heroes:
        sheet, report = build(hero)
        touched = touch_up(hero, sheet)
        if touched:
            print(f"{hero}_retouch.json: {touched} pixels retouched")
        breathe(hero, sheet)
        w, h = G.write_sheet(os.path.join(MOD, "champions", f"league_{hero}"), sheet)
        frames = [a for fr in sheet.values() for a, _ in fr]
        colours = len(np.unique(np.concatenate([a[a[..., 3] > 0][:, :3] for a in frames]), axis=0))
        print(f"league/champions/league_{hero}#sheet.png {w}x{h}: {len(frames)} frames, {colours} colours, "
              f"{flatness(frames):.0%} of pixels match their right neighbour")
        for tag, r in report.items():
            moved = [d for _, d in r]
            print(f"  {tag:8s} head column " + " ".join("  ?" if c is None else f"{c:+3d}" for c, _ in r) +
                  (f"   moved {' '.join(f'{d:+d}' for d in moved)}" if any(moved) else "") +
                  (f"   order {ORDER[(hero, tag)]}" if (hero, tag) in ORDER else ""))
        if args.review:
            review(hero, sheet, args.review)


if __name__ == "__main__":
    main()
