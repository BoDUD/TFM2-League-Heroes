#!/usr/bin/env python3
"""Aatrox's Q1-Q3 and R transformation from Codex's redo, and the wings loop the ult's aura plays (2026-10-04).

    python tools/art/import_redo_aatrox.py

The user, after the Q / R / legs analysis: 「让codex重画」. The pack (assets/source/aatrox/REDO.md) asked for League's
full-body Q casts with the blow on frame 6 (600 ms), League's long dark-crimson wings for the transformation, and a
symmetric wings loop; Codex's delivery is kept in assets/source/aatrox/codex_redo/ (six 8x strips, manifest.json,
HANDOFF.md). Here:
- Codex drew on the guide's red line, one row under the idle's soles (cell row 82 against 81): every frame goes up a
  row, so the figure stands where the idle stands.
- squares apart from the figure (pieces of up to LOOSE squares: a toe tip, a speck) go.
- the strips keep their cells and timings (the pack's aatrox_cells.json: the game's cells with these four tags
  replaced) -> assets/source/native/aatrox_<tag>.png at 8x; rig_aatrox.py leaves these tags alone (CODEX).
- the wings loop -> assets/source/aatrox/aatrox_fx_r_aura.png, cropped round all six frames, its anchor the standing
  point (the aura is a view_buffs picture drawn on the unit's spot, behind him) -> import_aatrox.py's r_aura.
- the blade's tip on the blow (frame 6) of each Q, from the pivot, for the slashes' anchors (printed).
- the transformation's burst (aatrox_fx_r_transform.png, the first effects pack) drew a pair of orange fire bat wings
  that the user found unlike League (「大招的效果也和原本LOL里面不一样吧」) and that would now stand over the new wings:
  aatrox_fx_r_burst.png keeps its first flash whole and, after it, only the ground ring and the low flames (rows from
  BURST_CUT of its cell down).
Codex's run is not taken (one foot stood still in all eight frames); the run stays rig_aatrox.py's.
The second redo (assets/source/aatrox/codex_redo2/, REDO2.md, 2026-10-04: 「开大招后没动作吗？」 -> 「请Codex补画」): World
Ender's forms of the attack, the empowered attack and the three Q casts - the approved frames with League's wings added
behind (every frame's base pixels kept, the soles already on the idle's row) - become the tags <tag>_r with the base
tag's cells and timings (R_FORMS); build_aatrox.py plays them while World Ender runs.
"""
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aatrox")
REDO = os.path.join(SRC, "codex_redo")
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["skill", "q2", "q3", "ult"]
UP = 1                      # Codex's soles on row 82, the idle's on 81
LOOSE = 12                  # pieces this small and apart from the figure go
BLOW = 5                    # frame 6: the blow
BURST_CUT = 55              # r_transform's cell rows kept from here down (its feet on row 66: the ring, low flames)
REDO2 = os.path.join(SRC, "codex_redo2")
R_FORMS = ["attack", "attack_p", "skill", "q2", "q3"]


def load(path):
    return np.asarray(Image.open(G.lp(path)).convert("RGBA"))


def cut(a, cw, ch, n):
    cols = a.shape[1] // (cw * Z)
    out = []
    for i in range(n):
        x, y = (i % cols) * cw * Z, (i // cols) * ch * Z
        b = a[y:y + ch * Z, x:x + cw * Z].reshape(ch, Z, cw, Z, 4)
        if not (b == b[:, :1, :, :1]).all():
            sys.exit(f"frame {i} is not made of flat {Z}x{Z} blocks")
        out.append(b[:, 0, :, 0].copy())
    return out


def pieces(f):
    op = f[..., 3] > 0
    lab = np.zeros(op.shape, int)
    sizes = [0]
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        k = len(sizes)
        lab[y, x] = k
        q, n = deque([(y, x)]), 0
        while q:
            cy, cx = q.popleft()
            n += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = k
                        q.append((ny, nx))
        sizes.append(n)
    return lab, sizes


def tidy(f, keep_all=False):
    """Up a row, loose squares out."""
    g = np.zeros_like(f)
    g[:-UP] = f[UP:]
    if keep_all:
        return g, 0
    lab, sizes = pieces(g)
    big = max(range(1, len(sizes)), key=lambda k: sizes[k])
    gone = 0
    for k in range(1, len(sizes)):
        if k != big and sizes[k] <= LOOSE:
            g[lab == k] = 0
            gone += sizes[k]
    return g, gone


def sheet(frames, cw, ch):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(len(frames), 4)
    rows = -(-len(frames) // cols)
    a = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for i, f in enumerate(frames):
        X, Y = (i % cols) * cw, (i // cols) * ch
        a[Y:Y + ch, X:X + cw] = f
    return np.repeat(np.repeat(a, Z, 0), Z, 1)


def tip(f, pivot):
    """The blade's farthest square ahead of the pivot on the blow (blade colours: plum, reds, orange)."""
    rgb = f[..., :3].astype(int)
    blade = (f[..., 3] > 0) & (rgb[..., 0] > 60) & (rgb[..., 2] < 140) & (rgb[..., 0] > rgb[..., 1] + 30)
    ys, xs = np.nonzero(blade)
    k = int(np.argmax(xs))
    return int(xs[k]) - pivot[0], int(ys[k]) - pivot[1]


def main():
    with open(G.lp(os.path.join(REDO, "aatrox_cells.json")), encoding="utf-8") as f:
        redo = json.load(f)
    cpath = os.path.join(OUT, "aatrox_cells.json")
    with open(G.lp(cpath), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    assert redo["cell"] == [cw, ch]
    for tag in TAGS:
        rows = redo["tags"][tag]
        fr = cut(load(os.path.join(REDO, f"aatrox_{tag}.png")), cw, ch, len(rows))
        done = [tidy(f) for f in fr]
        Image.fromarray(sheet([g for g, _ in done], cw, ch)).save(G.lp(os.path.join(OUT, f"aatrox_{tag}.png")))
        cells["tags"][tag] = [{"pivot": r["pivot"], "ms": r["ms"]} for r in rows]
        low = [int(np.nonzero(g[..., 3].any(1))[0].max()) for g, _ in done]
        print(f"{tag:5s} {len(done)} frames, loose squares removed {[n for _, n in done]}, lowest rows {low}"
              + (f", blade tip on the blow {tip(done[BLOW][0], rows[BLOW]['pivot'])}" if tag != "ult" else ""))
    for tag in R_FORMS:
        rows = cells["tags"][tag]
        fr = cut(load(os.path.join(REDO2, f"aatrox_{tag}_r.png")), cw, ch, len(rows))
        Image.fromarray(sheet(fr, cw, ch)).save(G.lp(os.path.join(OUT, f"aatrox_{tag}_r.png")))
        cells["tags"][f"{tag}_r"] = [{"pivot": r["pivot"], "ms": r["ms"]} for r in rows]
        print(f"{tag}_r {len(fr)} frames (World Ender, Codex's wings)")
    with open(G.lp(cpath), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)

    # the wings loop: one cell round all six frames, anchored on the standing point
    rows = redo["tags"]["rwings"]
    fr = [tidy(f, keep_all=True)[0] for f in cut(load(os.path.join(REDO, "aatrox_rwings.png")), cw, ch, len(rows))]
    pv = rows[0]["pivot"]
    assert all(r["pivot"] == pv for r in rows)
    op = np.any([f[..., 3] > 0 for f in fr], axis=0)
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    strip = np.concatenate([f[y0:y1, x0:x1] for f in fr], axis=1)
    Image.fromarray(np.repeat(np.repeat(strip, Z, 0), Z, 1)).save(G.lp(os.path.join(SRC, "aatrox_fx_r_aura.png")))
    apath = os.path.join(SRC, "aatrox_fx_anchors.json")
    with open(G.lp(apath), encoding="utf-8") as f:
        anchors = json.load(f)
    anchors["r_aura"] = {"cell": [int(x1 - x0), int(y1 - y0)], "anchor": [int(pv[0] - x0), int(pv[1] - y0)],
                         "frames": len(fr)}
    with open(G.lp(apath), "w", encoding="utf-8", newline="\n") as f:
        json.dump(anchors, f, indent=1)
    print("r_aura", anchors["r_aura"])

    # the burst without the fire wings
    t = anchors["r_transform"]
    bw, bh = t["cell"]
    burst = cut(load(os.path.join(SRC, "aatrox_fx_r_transform.png")), bw, bh, t["frames"])
    for f in burst[1:]:
        f[:BURST_CUT] = 0
    strip = np.concatenate(burst, axis=1)
    Image.fromarray(np.repeat(np.repeat(strip, Z, 0), Z, 1)).save(G.lp(os.path.join(SRC, "aatrox_fx_r_burst.png")))
    anchors["r_burst"] = dict(t)
    with open(G.lp(apath), "w", encoding="utf-8", newline="\n") as f:
        json.dump(anchors, f, indent=1)
    print("r_burst", anchors["r_burst"])


if __name__ == "__main__":
    main()
