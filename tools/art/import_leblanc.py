#!/usr/bin/env python3
"""Import LeBlanc's effects (Codex's step-3 delivery in assets/source/leblanc/codex_fx) as game sheets.

    python tools/art/import_leblanc.py

The body comes from tools/art/import_native.py. Codex drew the 19 base effects of PROMPTS_FX.md as exact 1x strips
(codex_fx/native, cut by manifest.json's rect_native) but 2-3 times the sizes the prompts asked for - its own
game-size copies (`*_game.png`, not kept) lost the sigil's eye, the circle's ring and the orb's trail. So each effect
is taken from the 1x strip and scaled by a whole factor (SCALE): halves and thirds keep, per block, the brightest of
its pixels (the white cores and the one-pixel threads stay), the blast is doubled; the magic circle and the sigil's
burst stay as drawn. The user: "有问题的地方你帮忙善后一下吧".
Placing (a frame's middle is drawn on the unit's pivot, 11 px over its feet; a caster's picture is mirrored when she
faces left and stands where it was played): projectiles centred on their box; the cast flashes on the staff's crystal
in the frame they play over (attack 4th: 37, -13; Q's release: 21, -25; E's throw: 32, -17); hits, the mark and the
burst on the upper body (0, -8); the root, the circle, the blast and the blink columns on the ground (their lowest
rows at the feet); the dash trail behind her at the middle of the body.
R repeats her spells with about double damage: its pictures are the base ones made brighter (every colour a third of
the way to white). The passive's clone is her idle (the design, all six breathing frames) standing where she was,
then sinking into the blink-out column.
Times (60 ticks a second): the mark 4 x 50 ms (replayed every 12 ticks), the root 12 x 125 ms (its 90 ticks), the circle
10 x 125 ms (until the return at 75 ticks), the loops 70 ms a frame, the bursts 50-70 ms. Writes
league/effects/league_leblanc_fx and league_leblanc_big.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "leblanc", "codex_fx")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
MOD = os.path.join(ROOT, "league")
FEET = 11                      # a unit's pivot is 11 px over its feet
SCALE = {"a_orb": 1 / 3, "a_cast": 1 / 2, "a_hit": 1 / 2, "q_orb": 1 / 2, "q_cast": 1 / 2, "q_hit": 1 / 2,
         "q_mark": 1 / 2, "q_pop": 1, "e_chain": 1 / 2, "e_tether": 1 / 3, "e_cast": 1 / 2, "e_hit": 1 / 2,
         "e_root": 1 / 2, "w_pad": 1, "w_trail": 1 / 2, "w_blast": 2, "w_hit": 1 / 2, "w_out": 1 / 2, "w_in": 1 / 2}
CRYSTAL = {"a": (37, -13), "q": (21, -25), "e": (32, -17)}   # the staff's crystal in the frame a cast flash plays over
BODY = (0, -8)                 # a hit on the upper body of a 35-43 px hero
MIX = 1 / 3                    # R's pictures: every colour this far toward white


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def lum(c):
    return 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]


def scale(c, f):
    """A whole-factor scale: halves/thirds keep each block's brightest pixel (a block with any pixel stays), doubles
    repeat each pixel."""
    if f == 1:
        return c.copy()
    if f > 1:
        n = int(round(f))
        return np.repeat(np.repeat(c, n, 0), n, 1)
    n = int(round(1 / f))
    H, W = c.shape[:2]
    H2, W2 = -(-H // n), -(-W // n)
    pad = np.zeros((H2 * n, W2 * n, 4), np.uint8)
    pad[:H, :W] = c
    blocks = pad.reshape(H2, n, W2, n, 4).transpose(0, 2, 1, 3, 4).reshape(H2, W2, n * n, 4)
    key = np.where(blocks[..., 3] > 0, lum(blocks.astype(float)), -1)
    pick = key.argmax(-1)
    out = np.take_along_axis(blocks, pick[..., None, None], 2)[:, :, 0]
    out[(blocks[..., 3] > 0).sum(-1) == 0] = 0
    return out


def cells(name):
    """The 1x frames of one effect, scaled."""
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
    eff = {a["name"]: a for a in man["assets"]}[f"leblanc_fx_{name}"]
    one = np.asarray(Image.open(lp(os.path.join(SRC, "native", f"leblanc_fx_{name}.png"))).convert("RGBA"))
    out = []
    for fr in eff["frames"]:
        x, y, w, h = fr["rect_native"]
        c = one[y:y + h, x:x + w].copy()
        c[c[..., 3] < 128] = 0
        c[c[..., 3] > 0, 3] = 255
        out.append(scale(c, SCALE[name]))
    return out


def box(frames):
    ys = np.concatenate([np.nonzero(c[..., 3])[0] for c in frames])
    xs = np.concatenate([np.nonzero(c[..., 3])[1] for c in frames])
    return xs.min(), ys.min(), xs.max(), ys.max()


def centred(frames):
    """Projectiles: the middle of the common box on the pivot."""
    x0, y0, x1, y1 = box(frames)
    cx, cy = int(round((x0 + x1) / 2)), int(round((y0 + y1) / 2))
    return [G.centre_frame(c, -cx, -cy) for c in frames]


def at(frames, point):
    """The middle of the common box on `point` (x, y from the pivot)."""
    x0, y0, x1, y1 = box(frames)
    cx, cy = int(round((x0 + x1) / 2)), int(round((y0 + y1) / 2))
    return [G.centre_frame(c, point[0] - cx, point[1] - cy) for c in frames]


def grounded(frames, dx=0):
    """The lowest row of the common box on the feet, centred across."""
    x0, y0, x1, y1 = box(frames)
    cx = int(round((x0 + x1) / 2))
    return [G.centre_frame(c, dx - cx, FEET - y1) for c in frames]


def trailing(frames):
    """The dash trail: its front (right end) just ahead of her middle, at the middle of her body."""
    x0, y0, x1, y1 = box(frames)
    cy = int(round((y0 + y1) / 2))
    return [G.centre_frame(c, 6 - x1, BODY[1] - cy) for c in frames]


def bright(frames):
    """R's copy: every colour MIX of the way to white."""
    out = []
    for c in frames:
        d = c.copy()
        m = d[..., 3] > 0
        d[m, :3] = np.clip(d[m, :3] + (255 - d[m, :3].astype(int)) * MIX, 0, 255).astype(np.uint8)
        out.append(d)
    return out


def seq(frames, ms):
    ms = ms if isinstance(ms, list) else [ms] * len(frames)
    return list(zip(frames, ms))


def clone():
    """The passive's picture: her idle's six frames where she stood, then sinking into the blink-out column."""
    spec = json.load(open(lp(os.path.join(NATIVE, "leblanc_cells.json")), encoding="utf-8"))
    cw, ch = spec["cell"]
    a = np.asarray(Image.open(lp(os.path.join(NATIVE, "leblanc_idle.png"))).convert("RGBA"))[4::8, 4::8]
    cols = a.shape[1] // cw
    body = []
    for k, fr in enumerate(spec["tags"]["idle"]):
        r, c = divmod(k, cols)
        f = a[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw]
        px, py = fr["pivot"]
        body.append(G.centre_frame(f, -px, -py))
    column = grounded(cells("w_out"))
    return seq(body, 100) + seq(column, [70, 70, 80, 90, 100])


def build():
    a_orb, q_orb, e_chain = (centred(cells(n)) for n in ("a_orb", "q_orb", "e_chain"))
    tether = centred(cells("e_tether"))
    a_cast = at(cells("a_cast"), CRYSTAL["a"])
    q_cast = at(cells("q_cast"), CRYSTAL["q"])
    e_cast = at(cells("e_cast"), CRYSTAL["e"])
    hits = {n: at(cells(n), BODY) for n in ("a_hit", "q_hit", "q_mark", "e_hit", "w_hit")}
    pop = at(cells("q_pop"), BODY)
    root = grounded(cells("e_root"))
    pad = grounded(cells("w_pad"))
    blast = grounded(cells("w_blast"))
    trail = trailing(cells("w_trail"))
    out_, in_ = grounded(cells("w_out")), grounded(cells("w_in"))
    fx = {
        "a_orb": seq(a_orb, 70), "a_cast": seq(a_cast, 50), "a_hit": seq(hits["a_hit"], 60),
        "q_orb": seq(q_orb, 70), "q_cast": seq(q_cast, 50), "q_hit": seq(hits["q_hit"], 60),
        "q_mark": seq(hits["q_mark"], 50),
        "rq_orb": seq(bright(q_orb), 70), "rq_cast": seq(bright(q_cast), 50), "rq_hit": seq(bright(hits["q_hit"]), 60),
        "rq_mark": seq(bright(hits["q_mark"]), 50),
        "e_chain": seq(e_chain, 70), "e_tether": seq(tether, 70), "e_cast": seq(e_cast, 50),
        "e_hit": seq(hits["e_hit"], 60), "e_root": seq(root, 125),
        "re_chain": seq(bright(e_chain), 70), "re_tether": seq(bright(tether), 70), "re_cast": seq(bright(e_cast), 50),
        "re_hit": seq(bright(hits["e_hit"]), 60), "re_root": seq(bright(root), 125),
        "w_trail": seq(trail, 60), "w_hit": seq(hits["w_hit"], 60),
        "rw_trail": seq(bright(trail), 60), "rw_hit": seq(bright(hits["w_hit"]), 60),
        "w_out": seq(out_, 70), "w_in": seq(in_, 70),
    }
    big = {
        "p_clone": clone(),
        "q_pop": seq(pop, 70), "rq_pop": seq(bright(pop), 70),
        "w_pad": seq(pad, 125),
        "w_blast": seq(blast, 70), "rw_blast": seq(bright(blast), 70),
    }
    return {"league_leblanc_fx": fx, "league_leblanc_big": big}


def main():
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
