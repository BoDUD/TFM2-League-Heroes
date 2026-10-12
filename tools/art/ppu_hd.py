#!/usr/bin/env python3
"""High-density (PPU) frames inside a hero's own sheet: `hd_<tag>` next to every `<tag>`.

The user, 2026-10-12: 「PPU 可以先改一版亚索试试」「这个要装进主包里 不是附加包」. The main pack's DLL (addons/league_main,
league.dll) swaps a registered hero's playing animation `<tag>` for `hd_<tag>` on the battlefield and sets the display
entity's draw scale (+0x1b4) to its base / PPU, so a frame drawn PPU times denser shows at the same size, its squares
PPU times finer. The hd tags sit in the hero's own sheet the way Kayn's form tags do (`rh_idle` ...: the anim-name swap
proven on game 0.6.3); the cards, the encyclopedia and the face icons draw `idle` and stay 1x. Without the hook (another
game version, the DLL not loaded) nothing plays the hd tags: the 1x hero as before.

    python tools/art/ppu_hd.py                 # every hero in PPU: rewrite its hd_ tags
    python tools/art/ppu_hd.py --hero yasuo --check

A frame is centred on its pivot (odd 1x sizes), so the hd frame is exactly PPU x the 1x frame (an even size, the same
centre). Its pixels: `assets/source/ppu/<hero>_<tag>.png` (a strip of the hd frames, PPU x each 1x frame, left to
right with 1 px gaps) when drawn, else the TEST frames - the 1x frame scaled by PPU (nearest) with its outer outline
cut to one hd square: drawn at 1/PPU that line is finer than any 1x pixel could be, the visible proof the dense frame is
on the screen (too small: the scale written, the swap not; too big: the swap, not the scale).
tools/art/import_native.py calls add_hd() for the heroes listed here after writing their sheets.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MOD = os.path.join(ROOT, "league")
SRC = os.path.join(ROOT, "assets", "source", "ppu")
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

# hero -> pixels per 1x square; the DLL's table (addons/league_main/src/hd.rs) must list the same
PPU = {"yasuo": 2}
PREFIX = "hd_"
DARK = 70          # an outline square: opaque, max channel at most this, next to the outside


def read_sheet(stem):
    """stem#sheet.png + stem#anim.fanim -> {tag: [(frame array, ms), ...]} in the fanim's order."""
    px = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA"))
    with open(stem + "#anim.fanim", encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag, a in anims.items():
        fr = []
        for f_ in a["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000, 3)))
        out[tag] = fr
    return out


def thin_outline(a, k):
    """The 1x frame `a` scaled by k (nearest), its outer outline one hd square wide: an hd square of an outline square
    that does not touch the outside takes the colour of the 1x neighbour inside on its side."""
    h, w = a.shape[:2]
    op = a[..., 3] > 0
    pad = np.pad(op, 1)
    outside_next = ~pad[:-2, 1:-1] | ~pad[2:, 1:-1] | ~pad[1:-1, :-2] | ~pad[1:-1, 2:]
    line = op & outside_next & (a[..., :3].max(axis=2) <= DARK)
    big = np.repeat(np.repeat(a, k, axis=0), k, axis=1)
    bop = big[..., 3] > 0
    bpad = np.pad(bop, 1)
    touches = ~bpad[:-2, 1:-1] | ~bpad[2:, 1:-1] | ~bpad[1:-1, :-2] | ~bpad[1:-1, 2:]
    inner = op & ~line
    for y, x in zip(*np.nonzero(line)):
        for dy in range(k):
            for dx in range(k):
                Y, X = y * k + dy, x * k + dx
                if touches[Y, X]:
                    continue
                sy = 1 if dy >= k / 2 else -1
                sx = 1 if dx >= k / 2 else -1
                for ny, nx in ((y, x + sx), (y + sy, x), (y + sy, x + sx), (y, x - sx), (y - sy, x)):
                    if 0 <= ny < h and 0 <= nx < w and inner[ny, nx]:
                        big[Y, X] = a[ny, nx]
                        break
    return big


def drawn_strip(hero, tag, sizes, k):
    """The drawn hd frames of `tag` (None when there is no strip)."""
    p = os.path.join(SRC, f"{hero}_{tag}.png")
    if not os.path.isfile(p):
        return None
    s = np.asarray(Image.open(p).convert("RGBA"))
    out, x = [], 0
    for w, h in sizes:
        W, H = w * k, h * k
        if x + W > s.shape[1] or H > s.shape[0]:
            sys.exit(f"{p}: too small for {len(sizes)} frames of {k}x the 1x sizes")
        out.append(s[:H, x:x + W].copy())
        x += W + 1
    return out


def add_hd(hero, sheet):
    """Replace `sheet`'s hd_ tags ({tag: [(array, ms)]}) with fresh ones from its 1x tags. -> {source: tags}."""
    k = PPU[hero]
    for t in [t for t in sheet if t.startswith(PREFIX)]:
        del sheet[t]
    made = {"drawn": [], "test": []}
    for tag in list(sheet):
        frames = sheet[tag]
        drawn = drawn_strip(hero, tag, [(a.shape[1], a.shape[0]) for a, _ in frames], k)
        if drawn is not None:
            sheet[PREFIX + tag] = [(b, ms) for b, (_, ms) in zip(drawn, frames)]
            made["drawn"].append(tag)
        else:
            sheet[PREFIX + tag] = [(thin_outline(a, k), ms) for a, ms in frames]
            made["test"].append(tag)
    return made


def check(hero, sheet):
    """Every 1x tag has its hd_ tag: as many frames, the same timing, PPU x each size. -> list of problems."""
    k, bad = PPU[hero], []
    for tag, frames in sheet.items():
        if tag.startswith(PREFIX):
            if tag[len(PREFIX):] not in sheet:
                bad.append(f"{tag} has no 1x {tag[len(PREFIX):]}")
            continue
        hd = sheet.get(PREFIX + tag)
        if hd is None:
            bad.append(f"{tag} has no {PREFIX}{tag}")
            continue
        if len(hd) != len(frames):
            bad.append(f"{PREFIX}{tag}: {len(hd)} frames, {tag} {len(frames)}")
            continue
        for i, ((a, ms), (b, ms2)) in enumerate(zip(frames, hd)):
            if b.shape[:2] != (a.shape[0] * k, a.shape[1] * k) or abs(ms - ms2) > 1e-6:
                bad.append(f"{PREFIX}{tag}[{i}]: {b.shape[1]}x{b.shape[0]} {ms2} ms, want "
                           f"{a.shape[1] * k}x{a.shape[0] * k} {ms} ms")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append", help="default: every hero in PPU")
    ap.add_argument("--check", action="store_true", help="only check the sheets, write nothing")
    a = ap.parse_args()
    bad = 0
    for hero in a.hero or sorted(PPU):
        if hero not in PPU:
            sys.exit(f"{hero}: not in PPU (tools/art/ppu_hd.py and addons/league_main/src/hd.rs)")
        stem = os.path.join(MOD, "champions", f"league_{hero}")
        sheet = read_sheet(stem)
        if not a.check:
            made = add_hd(hero, sheet)
            w, h = G.write_sheet(stem, sheet)
            print(f"league/champions/league_{hero}#sheet.png {w}x{h}: hd_ tags at PPU {PPU[hero]} - drawn: "
                  f"{', '.join(made['drawn']) or 'none'}; test (scaled, outline cut to one hd square): "
                  f"{', '.join(made['test']) or 'none'}")
        problems = check(hero, sheet)
        for p in problems:
            print(f"league_{hero}: {p}")
        bad += len(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
