#!/usr/bin/env python3
"""Import Heimerdinger's effects (assets/source/heimerdinger/PROMPTS_FX.md, 27 pictures; the user had Gemini draw them,
brought to game size by tools/art/process_heimerdinger_fx.py) as the game sheets league_heimerdinger_fx,
league_heimerdinger_big, league_heimerdinger_turret and league_heimerdinger_apex.

    python tools/art/import_heimerdinger_fx.py [--src DIR] [--review out.png]

The fx and big sheets: each picture placed as the kit plays it (import_shyvana_fx.py's way): spots are game px from the
pivot (x forward, y down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5). The projectiles (the bolt, the
rockets, the grenades' lobs) loop behind a lead tick (import_jhin.flight); the buffs (the slow, the passive's haste)
loop; the rest play once. w_flash and dead_burst are drawn into his frames (rig_heimerdinger.py), the turrets' deploy,
muzzle and breaking pictures into the turrets' own tags here; t_shot, t_beam_line and x_shot (a native add-on's shots
from the turrets) go into the fx sheet unbound.
The turret sheets are dense (league_main hd.rs EFFECTS, PPU 1.5 like him: league_leblanc_clone's way; a dense effect
sheet holds only idle / hd_idle, so one sheet a turret): tag idle at 1x (ppu_rig.one_of, each frame centred on the
pivot) and hd_idle at PPU 1.5 - the
designs hd/turret.png (39 x 30) and hd/apex.png (37 x 45) standing on the ground under the pivot (the zone's point), the
effects' pixels made 1.5 times bigger (nearest). One life each, timed on the kit's zones (build_heimerdinger.P):
the Q turret rises out of the ground over its golden hexagon, fires its first shot at t_first (667 ms) and then every
t_per (833 ms) - the muzzle flashing, the turret kicking down a square - and breaks down in smoke at t_life (10 s); the
apex turret rises in its blue column, fires from x_first every x_per (500 ms) and breaks at x_life (8 s).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import ppu_rig as R  # noqa: E402
from build_heimerdinger import P as KIT  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "heimerdinger", "codex_fx", "heimerdinger_fx")
HD = os.path.join(ROOT, "assets", "source", "heimerdinger", "hd")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)
PPU = 1.5
FEET = 11.5


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FLYING = {"a_bolt", "w_rocket", "t_shot", "t_beam_line", "x_shot"}
ROUNDS = {"e_grenade", "re_grenade", "t_muzzle", "x_muzzle"}
FORWARD = {"w_flash"}
IN_FRAMES = {"w_flash", "dead_burst", "t_dust", "t_muzzle", "t_gone", "x_dust", "x_muzzle", "x_gone"}
BIG = {"e_blast", "re_blast", "r_up"}
HIT = (0, -12)                  # a hit on the upper body of a 36 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
LINE = (0, 0)                   # a projectile's point
HEAD = (0, -20)                 # r_up's middle: its cell's row 14 on his hair's top (36 px over his soles)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_bolt": ("a_bolt", "core", J.flight(4, 50, 320, lead=2), [LINE]),
    "a_hit": ("a_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    "w_rocket": ("w_rocket", "core", J.flight(3, 50, 600, lead=2), [LINE]),
    "w_hit": ("w_hit", "core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "t_hit": ("t_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    "t_beam": ("t_beam", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "t_shot": ("t_shot", "core", J.flight(2, 50, 400, lead=1), [LINE]),
    "t_beam_line": ("t_beam_line", "core", J.flight(3, 50, 300, lead=1), [LINE]),
    "x_shot": ("x_shot", "core", J.flight(3, 50, 400, lead=1), [LINE]),
    "e_grenade": ("e_grenade", "core", J.flight(4, 60, 1000, lead=1), [LINE]),
    "re_grenade": ("re_grenade", "core", J.flight(4, 60, 1000, lead=1), [LINE]),
    "e_blast": ("e_blast", ("feet", 6), seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    "e_hit": ("e_hit", "core", seq(range(3), [50, 60, 70]), [HIT]),
    "e_slow": ("e_slow", ("feet", 3), loop(4, 100), [SOLES]),
    "r_up": ("r_up", "core", seq(range(6), [50, 60, 70, 80, 90, 100]), [HEAD]),
    "re_blast": ("re_blast", ("feet", 7), seq(range(7), [50, 50, 60, 70, 80, 90, 100]), [SOLES]),
    "x_hit": ("x_hit", "core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "x_beam": ("x_beam", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "haste": ("haste", ("feet", 3), loop(3, 120), [SOLES]),
}


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    return {e["name"]: e for e in man["effects"]}


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, "pixel_1x", meta["file"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if name in FORWARD:
            continue
        checks = []
        if name in FLYING or name in ROUNDS:
            checks.append((c[::-1], "top to bottom"))
        if name not in FLYING:
            checks.append((c[:, ::-1], "left to right"))
        for mirror, how in checks:
            if not (c == mirror).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric {how}")
    return [odd(c, name) for c in out]


def odd(c, name):
    """An even width (height for the projectiles) gets its middle column (row) twice: the game turns and mirrors about
    the pivot's square, so only an odd size lies even about it."""
    if name in FORWARD:
        return c
    for ax in ((0,) if name in FLYING else (0, 1) if name in ROUNDS else (1,)):
        n = c.shape[ax]
        if n % 2 == 0:
            c = np.insert(c, n // 2, np.take(c, n // 2, axis=ax), axis=ax)
    return c


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


# ------------------------------------------------------------------------------------------------- the turrets
def dense(c):
    """A 1x effect cell at PPU (nearest: every 1x pixel kept)."""
    h, w = c.shape[:2]
    yy = np.minimum(((np.arange(round(h * PPU)) + 0.5) / PPU).astype(int), h - 1)
    xx = np.minimum(((np.arange(round(w * PPU)) + 0.5) / PPU).astype(int), w - 1)
    return c[yy][:, xx].copy()


def put(can, layer, x0, y0, clip_y=None):
    ys, xs = np.nonzero(layer[..., 3] > 0)
    H, W = can.shape[:2]
    ok = (ys + y0 >= 0) & (ys + y0 < (H if clip_y is None else clip_y)) & (xs + x0 >= 0) & (xs + x0 < W)
    can[ys[ok] + y0, xs[ok] + x0] = layer[ys[ok], xs[ok]]


def muzzle_of(t):
    """The muzzle's middle in a turret design (the dark hole inside the biggest red ring): the darkest squares' middle
    near the design's centre column."""
    lum = t[..., :3].astype(int).sum(-1)
    op = t[..., 3] > 0
    h, w = t.shape[:2]
    band = np.zeros_like(op)
    band[h // 4:3 * h // 4, w // 3:2 * w // 3] = True
    dark = op & band & (lum < 90)
    ys, xs = np.nonzero(dark)
    return (xs.mean(), ys.mean())


class Life:
    """One turret's life as dense canvases: the design standing on the canvas' ground row under the pivot."""

    def __init__(self, design, src_fx, deploy, flash, gone):
        self.t = np.asarray(Image.open(lp(os.path.join(HD, design))).convert("RGBA")).copy()
        th, tw = self.t.shape[:2]
        self.W = int(tw + 120)
        self.H = int(th + 80)
        self.px = self.W / 2.0
        self.ground = self.H - 20                     # the canvas row under the turret's feet
        self.py = self.ground - FEET * PPU            # the pivot (the zone's point) FEET game px over the ground
        self.fx = {k: [dense(c) for c in src_fx[k]] for k in (deploy, flash, gone)}
        self.deploy, self.flash, self.gone = deploy, flash, gone
        self.mz = muzzle_of(self.t)

    def frame(self, sink=0, kick=0, fx=()):
        can = np.zeros((self.H, self.W, 4), np.uint8)
        th, tw = self.t.shape[:2]
        x0 = int(round(self.px - tw / 2))
        y0 = self.ground - th + sink + kick
        for name, k, where in fx:
            if where != "under":
                continue
            c = self.fx[name][k]
            put(can, c, int(round(self.px - c.shape[1] / 2)), int(round(self.ground - c.shape[0] / 2 - 2)))
        put(can, self.t, x0, y0, clip_y=self.ground)
        for name, k, where in fx:
            if where == "under":
                continue
            c = self.fx[name][k]
            if where == "muzzle":
                cx, cy = x0 + self.mz[0], y0 + self.mz[1]
            else:                                       # "body": the turret's middle
                cx, cy = self.px, self.ground - th / 2
            put(can, c, int(round(cx - c.shape[1] / 2)), int(round(cy - c.shape[0] / 2)))
        return can


def life_frames(L, life_ms, first_ms, per_ms, rise, deploy_ms):
    """[(dense canvas, ms)]: rising over the deploy picture, still until the first shot, a shot every per_ms (the
    muzzle's three pictures, the turret kicked down a square on the second), breaking down at life_ms."""
    out = []
    nd = len(L.fx[L.deploy])
    for k in range(max(nd, len(rise))):
        out.append((L.frame(sink=rise[min(k, len(rise) - 1)], fx=[(L.deploy, min(k, nd - 1), "under")]), deploy_ms))
    t = deploy_ms * max(nd, len(rise))
    shots = [first_ms + i * per_ms for i in range(int(math.ceil((life_ms - first_ms) / per_ms)))]
    shots = [s for s in shots if s < life_ms]
    for s in shots:
        if s > t:
            out.append((L.frame(), s - t))
            t = s
        fl = len(L.fx[L.flash])
        for k in range(fl):
            out.append((L.frame(kick=1 if k == 1 else 0, fx=[(L.flash, k, "muzzle")]), 50))
        t += 50 * fl
    if life_ms > t:
        out.append((L.frame(), life_ms - t))
    ng = len(L.fx[L.gone])
    for k in range(ng):
        out.append((L.frame(sink=[1, 3, 8, 30][min(k, 3)], fx=[(L.gone, k, "body")]), 80))
    return out


def one_and_dense(L, canvases):
    """Each dense canvas as the 1x frame about the pivot and the same box at PPU (ppu_rig.Rig.export's way)."""
    ones, hds = [], []
    for can, ms in canvases:
        ys, xs = np.nonzero(can[..., 3] > 0)
        if not len(ys):
            ones.append((np.zeros((1, 1, 4), np.uint8), ms))
            hds.append((np.zeros((2, 2, 4), np.uint8), ms))
            continue
        hw = int(np.ceil(max(L.px - xs.min(), xs.max() + 1 - L.px) / PPU - 0.5))
        hh = int(np.ceil(max(L.py - ys.min(), ys.max() + 1 - L.py) / PPU - 0.5))
        hh = max(hh, int(np.ceil(FEET)) + 1)
        ones.append((R.one_of(can, L.px, L.py, hw, hh, PPU), ms))
        W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
        hds.append((R.crop_dense(can, L.px, L.py, W, H), ms))
    return ones, hds


def turret_tags(allc):
    t = Life("turret.png", allc, "t_dust", "t_muzzle", "t_gone")
    tl = life_frames(t, KIT["t_life"] * 1000 / 60, KIT["t_first"] * 1000 / 60, KIT["t_per"] * 1000 / 60,
                     rise=[24, 14, 6, 2, 0], deploy_ms=60)
    x = Life("apex.png", allc, "x_dust", "x_muzzle", "x_gone")
    xl = life_frames(x, KIT["x_life"] * 1000 / 60, KIT["x_first"] * 1000 / 60, KIT["x_per"] * 1000 / 60,
                     rise=[40, 30, 20, 12, 6, 2, 0, 0], deploy_ms=60)
    t1, th = one_and_dense(t, tl)
    x1, xh = one_and_dense(x, xl)
    # a dense effect sheet holds only idle / hd_idle (league_main src/lookup.rs densify_table): one sheet a turret
    return {"league_heimerdinger_turret": {"idle": t1, "hd_idle": th},
            "league_heimerdinger_apex": {"idle": x1, "hd_idle": xh}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest(a.src)
    allc = {n: cells(n, meta[n], a.src) for n in meta}
    want = {v[0] for v in FX.values()} | IN_FRAMES
    if set(meta) != want:
        sys.exit(f"delivered {sorted(meta)} against {sorted(want)}")
    tables = {"league_heimerdinger_fx": {}, "league_heimerdinger_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        used = [k for k, _ in frames if k != J.EMPTY]
        if used and len(cs) < 1 + max(used):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(used)}")
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == J.EMPTY:            # a projectile's lead tick: nothing drawn
                out.append((np.zeros((1, 1, 4), np.uint8), ms))
            else:
                out.append((J.place(cs[k], anc, spots), ms))
        tables["league_heimerdinger_big" if tag in BIG else "league_heimerdinger_fx"][tag] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    for sheet, tt in turret_tags(allc).items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tt, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tt.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name in sorted(allc):
            cs = allc[name]
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append((name, img))
        W = max(r.width for _, r in rows) + 120
        sheet = Image.new("RGB", (W, sum(r.height + 10 for _, r in rows)), (20, 20, 26))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(lp(a.review))
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
