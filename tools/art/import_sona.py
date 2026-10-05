#!/usr/bin/env python3
"""Import Sona's effects (Codex's step-3 delivery in assets/source/sona/codex_fx) as game sheets.

    python tools/art/import_sona.py [--review OUT.png]

The body comes from tools/art/import_native.py. Codex drew the 20 effects of PROMPTS_FX.md as exact pixel art at
twice the asked sizes (codex_fx/logical-source, cut by manifest.json's `logical_rect`; its layout-size PNGs and
previews are not kept). So the effects are halved, each game pixel the brightest opaque pixel of its 2x2 block (the
white cores and the one-pixel staff lines stay); the slow's ring, the haste's wind and R's burst stay as drawn
(SCALE); the three Melody rings are scaled to the aura's radius (AURA, 1000 distance units a pixel), their ellipse
AURA * 2 px wide and, as drawn, half as tall.
The Power Chord's note (pc_note) is the attack's note in gold: each blue of the ramp swapped for the gold of the
same rank (League's chord is gold).
Placing (a frame's middle is drawn on the unit's pivot, 11 px over its feet; a caster's picture is mirrored when she
faces left): the projectiles centred on their box; the hits on the upper body (0, -8); the Power Chord's ready notes
round the etwahl at her waist (0, -3); the weakening and the stun over the crown (0, -31); the heal and the shield
on the feet (their lowest rows on the soles); the slow, the haste and the three rings round the feet (their
ellipse's middle 2 px over the soles: drawn behind the unit, the front half shows under it); R's burst on the
etwahl she throws over her head (0, -40 in R's frames 3-5).
Times (60 ticks a second): the loops 120 ms a frame (the Melody rings loop through their 3 s), the projectiles 80 ms,
the hits 70 ms, the heal and R's burst 80 ms, the stun 12 x 125 ms (its 90 ticks). Writes league/effects/
league_sona_fx and league_sona_big. --review draws every effect at 4x on the arena colour with the pivot and the
feet line.
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

SRC = os.path.join(ROOT, "assets", "source", "sona", "codex_fx")
MOD = os.path.join(ROOT, "league")
FEET = 11                      # a unit's pivot is 11 px over its feet
BODY = (0, -8)                 # a hit on the upper body of a 35-43 px hero
WAIST = (0, -3)                # the etwahl's middle in her idle
OVERHEAD = (0, -31)            # over a 35-40 px hero's crown
LIFT = (0, -40)                # the etwahl over her head in R's frames 3-5
GROUND = 9                     # a ring round the feet: its ellipse's middle 2 px over the soles
AURA = 45000                   # the Melody's radius (league_sona.data_champion)
AURA_TICKS = 180               # its life (league_sona.data_champion: the ApplyInProjectile's tick)
# name: factor other than 1/2. Halved, the slow's staff ring (21 px) and the haste's wind (19 px) hid behind a
# 34 px hero; R's burst (19 px) was smaller than the etwahl it bursts on (34 px)
SCALE = {"pc_tempo": 1, "e_ally": 1, "r_cast": 1}
RINGS = ("q_aura", "w_aura", "e_aura")
BLUE = ["#FFFFFF", "#CFF4FF", "#7FD8FF", "#36A6F0", "#1B5FC2"]
GOLD = ["#FFFFFF", "#FFF6C8", "#FFD95C", "#F0A830", "#B06A1A"]
ARENA = (104, 112, 72, 255)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def lum(c):
    c = c.astype(float)
    return 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]


def resample(c, fx, fy=None):
    """Scale by (fx, fy): each new pixel is the brightest opaque pixel of the source block it covers (a block with
    any pixel stays), so a shrink keeps white cores and one-pixel lines."""
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


def raw(name):
    """The logical frames of one effect, alpha made binary."""
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
    eff = {a["name"]: a for a in man["assets"]}[name]
    one = np.asarray(Image.open(lp(os.path.join(SRC, eff["logical_file"]))).convert("RGBA"))
    out = []
    for fr in eff["frames"]:
        x, y, w, h = fr["logical_rect"]
        c = one[y:y + h, x:x + w].copy()
        c[c[..., 3] < 128] = 0
        c[c[..., 3] > 0, 3] = 255
        out.append(c)
    return out


def box(frames):
    ys = np.concatenate([np.nonzero(c[..., 3])[0] for c in frames])
    xs = np.concatenate([np.nonzero(c[..., 3])[1] for c in frames])
    return xs.min(), ys.min(), xs.max(), ys.max()


def ellipse(frames):
    """A ring's middle row and width. Codex drew the rings 2 to 1 (107 x 57), notes rising over the back: the
    median frame's widest row is the width and its lowest row the front edge, so the middle is a quarter of the
    width over it (the notes would lift a box's middle; one frame's glow hangs 3 rows under the ring)."""
    lows, widths = [], []
    for c in frames:
        m = c[..., 3] > 0
        lows.append(np.nonzero(m.any(1))[0].max())
        widths.append(max(np.nonzero(r)[0][-1] - np.nonzero(r)[0][0] + 1 for r in m if r.any()))
    w = float(np.median(widths))
    return float(np.median(lows)) - w / 4, w


def belt(frames):
    """A flat mark's middle row: the middle of the rows at least 95% as wide as the widest (the median frame's;
    the slow's staff ring is 42 x 12, flatter than 2 to 1, its notes over the back)."""
    mids = []
    for c in frames:
        m = c[..., 3] > 0
        width = np.array([np.nonzero(r)[0][-1] - np.nonzero(r)[0][0] + 1 if r.any() else 0 for r in m])
        wide = np.nonzero(width >= 0.95 * width.max())[0]
        mids.append((wide.min() + wide.max()) / 2)
    return float(np.median(mids))


def ring(name):
    """A Melody ring scaled to the aura: AURA * 2 px wide (1000 distance units a pixel), as drawn 2 to 1."""
    frames = raw(name)
    mid, w = ellipse(frames)
    f = 2 * AURA / 1000 / w
    return [resample(c, f) for c in frames], mid * f


def cells(name):
    f = SCALE.get(name, 1 / 2)
    return [resample(c, f) for c in raw(name)]


def recolour(frames, src, dst):
    """Each colour of the `src` ramp to the `dst` colour of the same rank (nearest ramp colour for the rest)."""
    s = np.array([rgb(h) for h in src], float)
    d = np.array([rgb(h) for h in dst], np.uint8)
    out = []
    for c in frames:
        c = c.copy()
        m = c[..., 3] > 0
        px = c[m, :3].astype(float)
        k = np.argmin(((px[:, None, :] - s[None]) ** 2).sum(-1), 1)
        c[m, :3] = d[k]
        out.append(c)
    return out


def at(frames, point):
    """The middle of the common box on `point` (x, y from the pivot)."""
    x0, y0, x1, y1 = box(frames)
    cx, cy = int(round((x0 + x1) / 2)), int(round((y0 + y1) / 2))
    return [G.centre_frame(c, point[0] - cx, point[1] - cy) for c in frames]


def centred(frames):
    return at(frames, (0, 0))


def grounded(frames):
    """The lowest row of the common box on the soles, centred across."""
    x0, y0, x1, y1 = box(frames)
    cx = int(round((x0 + x1) / 2))
    return [G.centre_frame(c, -cx, FEET - y1) for c in frames]


def round_feet(frames, mid):
    """A ring: its ellipse's middle row `mid` on GROUND, centred across."""
    x0, y0, x1, y1 = box(frames)
    cx = int(round((x0 + x1) / 2))
    return [G.centre_frame(c, -cx, GROUND - int(round(mid))) for c in frames]


def seq(frames, ms):
    ms = ms if isinstance(ms, list) else [ms] * len(frames)
    return list(zip(frames, ms))


def build():
    note = cells("note")
    fx = {
        "note": seq(centred(note), 80),
        "pc_note": seq(centred(recolour(note, BLUE, GOLD)), 80),
        "q_note": seq(centred(cells("q_note")), 80),
        "hit": seq(at(cells("hit"), BODY), 70),
        "pc_q": seq(at(cells("pc_q"), BODY), 70),
        "pc_w": seq(at(cells("pc_w"), BODY), 70),
        "pc_e": seq(at(cells("pc_e"), BODY), 70),
        "q_hit": seq(at(cells("q_hit"), BODY), 70),
        "w_heal": seq(grounded(cells("w_heal")), 80),
        "r_hit": seq(at(cells("r_hit"), OVERHEAD), 125),
        "pc_glow": seq(at(cells("pc_glow"), WAIST), 120),
        "pc_tempo": seq(round_feet(cells("pc_tempo"), belt(cells("pc_tempo"))), 120),
        "pc_dim": seq(at(cells("pc_dim"), OVERHEAD), 120),
        "q_mel": seq(at(cells("q_mel"), BODY), 120),
        "w_mel": seq(grounded(cells("w_mel")), 120),
        "e_ally": seq(round_feet(cells("e_ally"), belt(cells("e_ally"))), 120),
    }
    big = {"r_wave": seq(centred(cells("r_wave")), 80), "r_cast": seq(at(cells("r_cast"), LIFT), 80)}
    for name in RINGS:
        frames, mid = ring(name)
        # the aura's picture rides on Sona as a CasterViewEffect played with the aura (2026-10-05: as its follow-zone's
        # view it was turned with the zone, upside down whenever the zone took a leftward direction): one play of the
        # tag covers the aura's 180 ticks, the loop's six frames repeated (25 x 120 ms), sharing their squares
        loop = round_feet(frames, mid)
        big[name] = seq([loop[k % len(loop)] for k in range(AURA_TICKS * 1000 // 60 // 120)], 120)
    return {"league_sona_fx": fx, "league_sona_big": big}


def review(sheets, out, z=4):
    """Every effect's frames in a row at z x on the arena colour; the pivot cross and the feet line in red."""
    rows = [(f"{s}:{t}", [a for a, _ in v]) for s, tags in sheets.items() for t, v in tags.items()]
    W = max(sum(a.shape[1] + 4 for a in fr) for _, fr in rows)
    H = sum(max(a.shape[0] for a in fr) + 14 for _, fr in rows)
    img = Image.new("RGBA", (W * z, H * z), (30, 34, 40, 255))
    d = ImageDraw.Draw(img)
    y = 0
    for label, fr in rows:
        h = max(a.shape[0] for a in fr)
        d.text((4, y * z + 2), label, fill=(230, 230, 230, 255))
        x = 0
        for a in fr:
            c = Image.new("RGBA", (a.shape[1], h), ARENA)
            c.alpha_composite(Image.fromarray(a, "RGBA"), (0, (h - a.shape[0]) // 2))
            big = c.resize((a.shape[1] * z, h * z), Image.NEAREST)
            bd = ImageDraw.Draw(big)
            px, py = a.shape[1] // 2, h // 2
            bd.line([(px * z, (py - 2) * z), (px * z, (py + 3) * z)], fill=(230, 40, 40, 255))
            bd.line([((px - 2) * z, py * z), ((px + 3) * z, py * z)], fill=(230, 40, 40, 255))
            if py + FEET < h:
                bd.line([(0, (py + FEET) * z), (a.shape[1] * z, (py + FEET) * z)], fill=(230, 40, 40, 160))
            img.alpha_composite(big, (x * z, (y + 12) * z))
            x += a.shape[1] + 4
        y += h + 14
    img.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write a sheet of every effect to this PNG")
    args = ap.parse_args()
    sheets = build()
    for sprite, tags in sheets.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags, share=True)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))
    if args.review:
        review(sheets, args.review)


if __name__ == "__main__":
    main()
