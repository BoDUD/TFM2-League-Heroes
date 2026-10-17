#!/usr/bin/env python3
"""Import Vi's effects (Codex's step-3 delivery in assets/source/vi/codex_fx) as the game sheet league_vi_fx.

    python tools/art/import_vi.py [--review OUT.png]

The body comes from tools/art/import_native.py. Codex drew the 15 effects of PROMPTS.md as pixel art on 8 px squares
(2026-10-02 22:38, codex_fx/logical: one game pixel a square, cut by manifest.json's `frames[].rect_1x`; its 8x PNGs,
image-model drafts and previews are not kept), each drawing about 30 squares across whatever size PROMPTS.md asked.
So each effect is scaled by SCALE (each new pixel the brightest opaque pixel of the source block it covers: a shrink
keeps the white cores and one-pixel lines; a growth repeats pixels): the hits 0.7 (19-21 px; halved they were too
small for the user, PROMPTS.md asked 12-14), the fist glows halved (15-16 px), W's third hit and Q's stop a little
under the drawing (22, 26 as asked), the shield 1.5 x (36 x 45: round her 40 rows, as asked; Codex drew it 24 x 30),
R's slam crack 1.7 x across only (about 75 px: as drawn, 44 px, it hid under her slam pose, 53 px wide; the user:
"往两边延伸出去"), the rest as drawn.
Placing (a frame's middle is drawn on the unit's pivot, 11 px over its feet; a caster's picture is mirrored when she
faces left). Her spots are measured on league/champions/league_vi (x right, y down from the pivot; re-measure after a
strips redraw; these are the guard design's, tools/art/strips_vi.py): the Q charge on the near gauntlet pulled back
low beside her hip (its crystal (-7, -5), skill frames 2-4), the E glow on the far fist raised by her cheek (its crystal
(11, -15) in the idle: that fist does the E hammer), the R trail's right edge at her back (-4, -12), Q's dust at her
start (its right edge 4 px ahead, its foot on the soles). The E wave is the picture of a view-only line from her pivot
toward the target (the kit's league_vi_e_wave, WAVE px long; a line's picture is drawn centred on the line and turned to
it, league_briar E): its left middle 22 px along the line, where the smashing fist's crystal is (attack_e frame 4),
its middle row on the line. As a caster picture it only turned left or right and stood the wrong way on the red side
(the user, 2026-10-03: 「之前剑姬的问题 E技能的特效没有跟随人物 反方向的」); turned with the line it points where the cone
hits, upside down when she punches left (Codex's wave is about the same both ways up).
The hits, W's third hit, Q's stop and R's knock aside on the target's upper body (0, -8); R's uppercut column, the
shield and R's launch with their foot on the soles; R's slam crack round the feet (its middle 2 px over the soles).
Times (60 ticks a second, league_vi.data_champion): the Q charge 5 x 100 ms (its 30 ticks), Q's dust 6 x 70 ms (the
12-tick dash and after), the shield 3 + 25 + 2 frames = 3 s (its 180 ticks: frames 4-8 loop five times, then it
shatters), R's trail 6 x 70 ms (the dash, up to 28 ticks; it plays on the ult's first tick and waits the 7 ticks
before the dash in an empty first frame, as a following caster picture played from a Delayed is mirrored the wrong
way for a red-side caster), the slam 8 x 90 ms, the rest 60-80 ms. Writes
league/effects/league_vi_fx. --review draws every effect at 4x on her frame (or a target: her idle) on the arena
colour.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402
import tfm2_ase as TA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vi", "codex_fx")
MOD = os.path.join(ROOT, "league")
FEET = 11                      # a unit's pivot is 11 px over its feet
GROUND = 9                     # a ground mark's middle: 2 px over the soles
BODY = (0, -8)                 # a hit on the upper body
Q_FIST = (-7, -5)              # the near gauntlet pulled back by her hip, skill frames 2-4: its crystal
E_FIST = (11, -15)             # the far fist raised by her cheek in the idle (the E hammer's fist): its crystal
E_SMASH = (22, -1)             # that fist smashing down-forward, attack_e frame 4: the wave's left middle
WAVE = 68                      # the E wave's line (league_vi_e_wave's length / 1000): the frames centre on its middle
R_BACK = (-4, -12)             # the R trail's right edge, behind her
# name: factor, or (across, down)
SCALE = {"hit": 0.7, "q_hit": 0.7, "e_hit": 0.7, "r_side": 0.7, "q_charge": 1 / 2, "e_arm": 1 / 2,
         "w_proc": 0.7, "q_stop": 0.8, "bs_on": 1.5, "r_slam": (1.7, 1)}
ARENA = (104, 112, 72, 255)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def lum(c):
    c = c.astype(float)
    return 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]


def resample(c, fx, fy=None):
    """Scale by (fx, fy): each new pixel is the brightest opaque pixel of the source block it covers."""
    fy = fx if fy is None else fy
    H, W = c.shape[:2]
    H2, W2 = max(1, int(round(H * fy))), max(1, int(round(W * fx)))
    key = np.where(c[..., 3] > 0, lum(c[..., :3]), -1.0)
    out = np.zeros((H2, W2, 4), np.uint8)
    for y in range(H2):
        y0 = min(H - 1, int(y / fy))
        y1 = max(y0 + 1, min(H, int((y + 1) / fy)))
        for x in range(W2):
            x0 = min(W - 1, int(x / fx))
            x1 = max(x0 + 1, min(W, int((x + 1) / fx)))
            blk = key[y0:y1, x0:x1]
            if blk.max() < 0:
                continue
            iy, ix = np.unravel_index(int(blk.argmax()), blk.shape)
            out[y, x] = c[y0 + iy, x0 + ix]
    return out


def cells(name):
    """The logical frames of one effect, alpha binary, scaled by SCALE."""
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
    eff = {a["id"]: a for a in man["assets"]}["vi_fx_" + name]
    one = np.asarray(Image.open(lp(os.path.join(SRC, "logical", f"vi_fx_{name}_1x.png"))).convert("RGBA"))
    out = []
    for fr in eff["frames"]:
        x, y, w, h = fr["rect_1x"]
        c = one[y:y + h, x:x + w].copy()
        c[c[..., 3] < 128] = 0
        c[c[..., 3] > 0, 3] = 255
        f = SCALE.get(name, 1)
        f = f if isinstance(f, tuple) else (f, f)
        out.append(c if f == (1, 1) else resample(c, *f))
    return out


def box(frames):
    ys = np.concatenate([np.nonzero(c[..., 3])[0] for c in frames])
    xs = np.concatenate([np.nonzero(c[..., 3])[1] for c in frames])
    return xs.min(), ys.min(), xs.max(), ys.max()


def at(frames, point):
    """The middle of the common box on `point` (x, y from the pivot)."""
    x0, y0, x1, y1 = box(frames)
    cx, cy = int(round((x0 + x1) / 2)), int(round((y0 + y1) / 2))
    return [G.centre_frame(c, point[0] - cx, point[1] - cy) for c in frames]


def left_at(frames, point):
    """The common box's left middle on `point`."""
    x0, y0, x1, y1 = box(frames)
    return [G.centre_frame(c, point[0] - x0, point[1] - int(round((y0 + y1) / 2))) for c in frames]


def on_line(frames, start, length):
    """A line's picture: the common box's left middle `start` px along a line `length` px long from her pivot, the frame
    centred on the line's middle."""
    x0, y0, x1, y1 = box(frames)
    return [G.centre_frame(c, start - length // 2 - x0, -int(round((y0 + y1) / 2))) for c in frames]


def right_at(frames, point):
    """The common box's right middle on `point`."""
    x0, y0, x1, y1 = box(frames)
    return [G.centre_frame(c, point[0] - x1, point[1] - int(round((y0 + y1) / 2))) for c in frames]


def grounded(frames, dx=0, right=False):
    """The common box's lowest row on the soles; centred across (or its right edge `dx` ahead)."""
    x0, y0, x1, y1 = box(frames)
    ox = dx - x1 if right else dx - int(round((x0 + x1) / 2))
    return [G.centre_frame(c, ox, FEET - y1) for c in frames]


def round_feet(frames):
    """A ground mark: the common box's middle row on GROUND, centred across."""
    x0, y0, x1, y1 = box(frames)
    return [G.centre_frame(c, -int(round((x0 + x1) / 2)), GROUND - int(round((y0 + y1) / 2))) for c in frames]


def seq(frames, ms):
    ms = ms if isinstance(ms, list) else [ms] * len(frames)
    return list(zip(frames, ms))


def shield(frames):
    """3 s: frames 1-3 rise, 4-8 loop five times, 9-10 shatter (100 ms each)."""
    order = [0, 1, 2] + [3, 4, 5, 6, 7] * 5 + [8, 9]
    return [(frames[k], 100) for k in order]


def build():
    return {
        "hit": seq(at(cells("hit"), BODY), 60),
        "w_proc": seq(at(cells("w_proc"), BODY), 70),
        "bs_on": shield(grounded(cells("bs_on"))),
        "q_charge": seq(at(cells("q_charge"), Q_FIST), 100),
        "q_go": seq(grounded(cells("q_go"), 4, right=True), 70),
        "q_hit": seq(at(cells("q_hit"), BODY), 70),
        "q_stop": seq(at(cells("q_stop"), BODY), 70),
        "e_arm": seq(at(cells("e_arm"), E_FIST), 80),
        "e_wave": seq(on_line(cells("e_cone"), E_SMASH[0], WAVE), 60),
        "e_hit": seq(at(cells("e_hit"), BODY), 70),
        "r_cast": seq(grounded(cells("r_cast")), 80),
        # played on the ult's first tick (a following picture played later is mirrored the wrong way on the red
        # side): empty for the 7 ticks before the dash
        "r_trail": [(np.zeros((1, 1, 4), np.uint8), round(7 * 1000 / 60))] + seq(right_at(cells("r_trail"), R_BACK), 70),
        "r_side": seq(at(cells("r_side"), BODY), 80),
        "r_hit": seq(grounded(cells("r_hit")), 80),
        "r_slam": seq(round_feet(cells("r_slam")), 90),
    }


# effect: (her tag, frame index) it is drawn over in the review; None = on a target (her idle)
ON = {"q_charge": ("skill", 2), "q_go": ("skill_dash", 0), "e_arm": ("idle", 0), "e_wave": ("attack_e", 3),
      "bs_on": ("idle", 0), "r_cast": ("ult", 0), "r_trail": ("ult_dash", 0), "r_slam": ("ult_slam", 0)}
BEHIND = {"q_go", "r_trail", "r_slam"}
# effect: px its frame's middle stands ahead of her pivot in the review (a line's picture: the line's middle)
AHEAD = {"e_wave": WAVE // 2}


def review(fx, out, z=4):
    """Every effect's frames in a row at z x over her frame (or her idle as the target), the arena colour behind."""
    sp = TA.load_sprite(os.path.join(MOD, "champions", "league_vi"))

    def body(tag, k):
        t = sp.tag(tag)
        return np.asarray(sp.frames[t["frm"] + k].convert("RGBA"))

    rows = []
    for name, v in fx.items():
        tag, k = ON.get(name, ("idle", 0))
        b = body(tag, k)
        seen, cells_ = set(), []
        for a, _ in v:
            if id(a) in seen:
                continue
            seen.add(id(a))
            dx = AHEAD.get(name, 0)
            H = max(a.shape[0], b.shape[0])
            W = max(a.shape[1] + 2 * dx, b.shape[1])
            c = Image.new("RGBA", (W, H), ARENA)
            layers = [(a, 1), (b, 0)] if name in BEHIND else [(b, 0), (a, 1)]
            for arr, ahead in layers:
                c.alpha_composite(Image.fromarray(arr, "RGBA"),
                                  ((W - arr.shape[1]) // 2 + dx * ahead, (H - arr.shape[0]) // 2))
            cells_.append(c.resize((W * z, H * z), Image.NEAREST))
        h = max(c.height for c in cells_)
        row = Image.new("RGBA", (sum(c.width + 8 for c in cells_) + 8, h + 28), (30, 34, 40, 255))
        ImageDraw.Draw(row).text((6, 6), f"{name}  ({len(v)} frames shown {len(cells_)}, {sum(m for _, m in v)} ms)",
                                 fill=(230, 230, 230, 255))
        x = 8
        for c in cells_:
            row.alpha_composite(c, (x, 24 + (h - c.height) // 2))
            x += c.width + 8
        rows.append(row)
    W = max(r.width for r in rows)
    img = Image.new("RGBA", (W, sum(r.height for r in rows)), (30, 34, 40, 255))
    y = 0
    for r in rows:
        img.alpha_composite(r, (0, y))
        y += r.height
    img.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write a sheet of every effect on her to this PNG")
    args = ap.parse_args()
    fx = build()
    w, h = G.write_sheet(os.path.join(MOD, "effects", "league_vi_fx"), fx)
    print(f"league/effects/league_vi_fx#sheet.png {w}x{h}: " + ", ".join(
        f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in fx.items()))
    if args.review:
        review(fx, args.review)


if __name__ == "__main__":
    main()
