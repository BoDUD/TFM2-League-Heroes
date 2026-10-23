#!/usr/bin/env python3
"""Azir's sand soldier from the side, spear to the right, standing and stabbing (the user, 2026-10-23: 「沙兵不攻击吗 也要面向敌人
啊 看大头炮台怎么做的」 -> 「沙兵没攻击动作 你想办法补吧 不让codex了 还有不面向敌人」: made here from League's model, no Codex,
league_heimerdinger's side turrets' way, design_heimerdinger_side_turrets.py).

    python tools/art/design_azir_side_soldier.py [--yaw 70] [--transfer 0.6] [--review DIR]
        # writes hd/soldier_side_<pose>.png and hd/soldier_side.json (PPU 1.5, the front soldier's)

League's AzirSoldier rendered at yaw `--yaw` (tools/lol/pose_ref.py, one strip: one camera, one ground line; its long
cape left out - the design's soldier wears none, and it hid his body) on black and on white - the two give each pixel's
alpha and colour - in POSES: its idle (the spear level at the enemy) and Attack1's wind, thrust, hold and recovery.
Every pose goes down by one factor (the idle's helmet crest to soles = the front design's 46 rows, hd/soldier.png) on
one grid laid from the soldier's root (the idle's feet), so the lunge moves the body forward and nothing jitters; a
square is drawn where half of it is covered.
The colours are the design's own (hd/soldier.png): League's soldier is bare-armed in dark leather, the design's wears
gold greaves, gold bracers, an olive skirt and a gold spear. Each part in PARTS is found where the picture changes when
it is rendered away (so a part behind the body never counts) and takes its family of the design's colours by
brightness rank (the part's darkest square the family's darkest colour); the rest goes `--transfer` of the way the front
render differs from the front design (Lab mean and spread) and takes the nearest design colour. The spear keeps one
unbroken line (in every column it crosses, its most covered square); the helmet's darkest squares are its face opening
(FACE, in the ink). Two majority passes clean the specks, a dark line goes round each gold piece (ARMOUR, on the skin
or cloth next to it) and the design's outline one square round it all.
hd/soldier_side.json: per pose its size and its root (the column between the feet, the soles' row: where the soldier
stands) - rig_azir.py lays the frames on it.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_heimerdinger_side_turrets as HS  # noqa: E402
import pixel_down as PD  # noqa: E402

LOL = r"D:\WeGameApps\lol"
WORK = "C:/t/az_work/soldier"
HD = os.path.join(ROOT, "assets", "source", "azir", "hd")
ROWS = 46                      # the front design's helmet crest to soles (hd/soldier.png, PPU 1.5: 30.7 game px)
SIZE, WIDTH, FIT, SHIFT, GROUND = 1000, 2.4, 0.5, -0.22, 0.88    # the renders' cell (the thrust's spear fits)
HIDE = "M_Cape"                # League's long cape left out (its own joints): the design's soldier wears none
POSES = {"stand": "azirsoldier_idle1@0", "wind": "azirsoldier_attack1@250", "thrust": "azirsoldier_attack1@330",
         "hold": "azirsoldier_attack1@700", "recover": "azirsoldier_attack1@1300"}
ARMOUR = ("bracer", "helmet", "greave")       # the gold pieces the design draws a dark line round
FACE = 0.15                    # the helmet's darkest share of squares: its face opening, in the ink
PARTS = [   # (part, its joints - each with all below it, the design's colours it takes): an earlier part wins
    ("spear", "Weapon", "gold"),
    ("hand", "R_Hand$|L_Hand$", "skin"),
    ("bracer", "R_Elbow|L_Elbow", "gold"),
    ("helmet", "^Head$", "gold"),
    ("greave", "R_Knee|L_Knee", "gold"),
    ("skirt", "R_Hip|L_Hip", "cloth"),
    ("waist", "^Pelvis$", "cloth"),
    ("body", "^Spine1$", "skin"),
]


def lp(path):
    return HS.lp(path)


def render(yaw, frames, stem, hide, bg):
    """pose_ref's strip of `frames` on `bg` with the joints `hide` matches left out -> RGB float (the whole strip); framed
    on every vertex (--fit-all), so leaving a part out never moves the camera."""
    path = os.path.join(WORK, f"{stem}_{yaw}_{bg.replace(',', '_')}.png")
    if not os.path.isfile(path):
        os.makedirs(WORK, exist_ok=True)
        cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", LOL, "--champ",
               "AzirSoldier", "--wad", "Azir", "--hq", "--yaw", str(yaw), "--size", str(SIZE), "--width", str(WIDTH),
               "--fit", str(FIT), "--shift", str(SHIFT), "--ground", str(GROUND), "--bg", bg, "--no-labels",
               "--hide-joints", hide, "--fit-all", "--name", os.path.splitext(os.path.basename(path))[0], "--out", WORK]
        for f in frames:
            cmd += ["--frame", f]
        subprocess.run(cmd, check=True, capture_output=True)
    return np.asarray(Image.open(path).convert("RGB")).astype(float) / 255.0


def cells_of(img, n):
    cw = img.shape[1] // n
    return [img[:, i * cw:(i + 1) * cw] for i in range(n)]


def matte(yaw, frames, stem):
    """The strip on black and on white -> [RGBA float cell] (straight alpha 0..1) and the black one's cells."""
    k, w = (render(yaw, frames, stem, HIDE, bg) for bg in ("0,0,0", "255,255,255"))
    a = np.clip(1.0 - (w - k).mean(-1), 0, 1)
    rgb = np.clip(k / np.maximum(a, 1e-3)[..., None], 0, 1)
    a[a < 0.03] = 0
    return [np.dstack([c, ca]) for c, ca in zip(cells_of(rgb, len(frames)), cells_of(a[..., None], len(frames)))], \
        cells_of(k, len(frames))


def root_of(cell):
    """The idle's root: the middle of its lowest rows' columns (between the feet) and its soles' row, render px."""
    ys, xs = np.nonzero(cell[..., 3] > 0.5)
    low = ys >= ys.max() - 6
    return (xs[low].min() + xs[low].max()) / 2.0, float(ys.max() + 1)


class Grid:
    """One grid of f render px a square laid from the root over every cell (the same camera for every strip)."""

    def __init__(self, cells, f, root):
        self.f, self.m = f, int(np.ceil(2 * f)) + 2         # a clear margin: the squares may reach past the cell
        rx, ry = root[0] + self.m, root[1] + self.m
        ys, xs = np.nonzero(np.max([c[..., 3] for c in cells], 0) > 0.03)
        self.left = int(np.ceil((rx - xs.min() - self.m) / f)) + 2
        self.right = int(np.ceil((xs.max() + 1 - rx + self.m) / f)) + 2
        self.up = int(np.ceil((ry - ys.min() - self.m) / f)) + 2
        self.box = (rx - self.left * f, ry - self.up * f, rx + self.right * f, ry)

    def mean(self, a):
        """The mean of a (render px, one channel) over each square."""
        a = np.pad(a.astype(np.float32), self.m)
        return np.asarray(Image.fromarray(a, "F").resize((self.left + self.right, self.up), Image.BOX, box=self.box))

    def colours(self, cell):
        """(rgb 0..1, coverage 0..1) a square each."""
        cov = self.mean(cell[..., 3])
        rgb = np.dstack([self.mean(cell[..., k] * cell[..., 3]) for k in range(3)]) / np.maximum(cov, 1e-4)[..., None]
        return rgb, cov


def families(front):
    """The design's colours by family, each darkest first: gold (the armour, the spear), skin, cloth (the olive skirt and
    its dark browns); and the ink (the outline)."""
    ink = np.array(PD.edge_colour(front)[:3], np.uint8)
    pal = np.unique(front[front[..., 3] > 0][:, :3], axis=0)
    pal = pal[np.abs(pal.astype(int) - ink.astype(int)).sum(1) > 0]
    f = pal.astype(float) / 255
    mx, mn = f.max(1), f.min(1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = f.T
    hue = (np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) + 360) % 360
    fam = {"gold": pal[(hue >= 30) & (hue <= 60) & (sat >= 0.55)],
           "skin": pal[(hue < 25) & (sat >= 0.55)],
           "cloth": pal[((hue > 45) & (hue < 70) & (sat < 0.55)) | ((hue < 25) & (sat < 0.5))]}
    lum = lambda c: c.astype(float) @ [0.299, 0.587, 0.114]
    return {k: v[np.argsort(lum(v))] for k, v in fam.items()}, pal, ink


def snap(rgb, pal):
    """Each colour (uint8) to the nearest of pal (Lab)."""
    lab = PD._lab(rgb.astype(float))
    plab = PD._lab(pal.astype(float))
    return pal[((lab[:, None] - plab[None]) ** 2).sum(-1).argmin(1)]


def outline(g, ink):
    """The design's outline: every clear square 4-next to the figure takes the ink (one square all round)."""
    op = np.pad(g[..., 3] > 0, 1)
    ring = (op[1:-1, :-2] | op[1:-1, 2:] | op[:-2, 1:-1] | op[2:, 1:-1]) & ~op[1:-1, 1:-1]
    out = g.copy()
    out[ring, :3] = ink
    out[ring, 3] = 255
    return out


def build(yaw, transfer):
    """{pose: (picture, root)} and render px a square."""
    names = list(POSES)
    frames = [POSES[n] for n in names]
    cells, blacks = matte(yaw, frames, "side_nocape")
    root = root_of(cells[0])
    f = (root[1] - np.nonzero(cells[0][..., 3] > 0.5)[0].min()) / ROWS
    G = Grid(cells, f, root)
    shape = (G.up, G.left + G.right)
    # each part where rendering it away changes the picture, as square coverage
    seen = {}
    for part, joints, _ in PARTS:
        gone = cells_of(render(yaw, frames, f"side_no_{part}", f"{HIDE}|{joints}", "0,0,0"), len(frames))
        seen[part] = [G.mean(np.abs(b - h).max(-1) > 0.06) for b, h in zip(blacks, gone)]
    front = np.asarray(Image.open(lp(os.path.join(HD, "soldier.png"))).convert("RGBA"))
    fam, pal, ink = families(front)
    fcells, _ = matte(0, [POSES["stand"]], "front_nocape")
    froot = root_of(fcells[0])
    FG = Grid(fcells, (froot[1] - np.nonzero(fcells[0][..., 3] > 0.5)[0].min()) / ROWS, froot)
    frgb, fcov = FG.colours(fcells[0])
    fsmall = np.zeros((*fcov.shape, 4), np.uint8)
    fsmall[fcov >= 0.5, :3] = np.clip(frgb[fcov >= 0.5] * 255, 0, 255).round().astype(np.uint8)
    fsmall[fcov >= 0.5, 3] = 255
    src, dst = HS.lab_stats(fsmall), HS.lab_stats(front)

    grids, owners, lums = [], [], {p: [] for p, _, _ in PARTS}
    for k, cell in enumerate(cells):
        rgb, cov = G.colours(cell)
        drawn = cov >= 0.5
        sp = seen["spear"][k]                               # the spear: its most covered square in every column
        line = np.zeros(shape, bool)
        cols = np.nonzero(sp.max(0) >= 0.08)[0]
        line[sp[:, cols].argmax(0), cols] = True
        line |= sp >= 0.35
        drawn |= line
        owner = np.full(shape, -1)
        for i, (part, _, _) in reversed(list(enumerate(PARTS))):
            owner[(seen[part][k] >= 0.35) & drawn] = i
        owner[line] = 0
        lum = rgb @ [0.299, 0.587, 0.114]
        for i, (part, _, _) in enumerate(PARTS):
            lums[part].append(lum[owner == i])
        grids.append((rgb, drawn, owner, lum))
        owners.append(owner)
    ranks = {p: np.sort(np.concatenate(v)) if any(len(x) for x in v) else np.zeros(1) for p, v in lums.items()}

    out = {}
    for name, (rgb, drawn, owner, lum) in zip(names, grids):
        g = np.zeros((*shape, 4), np.uint8)
        g[drawn, :3] = np.clip(rgb[drawn] * 255, 0, 255).round().astype(np.uint8)
        g[drawn, 3] = 255
        rest = drawn & (owner < 0)
        g[rest, :3] = snap(HS.toward(g, src, dst, transfer)[rest][:, :3], pal)
        for i, (part, _, family) in enumerate(PARTS):
            m = drawn & (owner == i)
            if m.any():
                ramp = fam[family]
                q = np.searchsorted(ranks[part], lum[m]) / max(1, len(ranks[part]))
                g[m, :3] = ramp[np.clip((q * len(ramp)).astype(int), 0, len(ramp) - 1)]
                if part == "helmet":
                    face = m & (lum <= np.quantile(ranks[part], FACE))
                    g[face, :3] = ink
        for _ in range(2):
            g = PD._majority(g, g[..., 3] > 0, np.zeros(shape, bool))
        # the design's dark line round each gold piece: on the skin / cloth square next to it
        armour = np.isin(owner, [i for i, (p, _, _) in enumerate(PARTS) if p in ARMOUR])
        soft = drawn & ~armour & (owner != 0)
        pa = np.pad(armour, 1)
        near = pa[1:-1, :-2] | pa[1:-1, 2:] | pa[:-2, 1:-1] | pa[2:, 1:-1]
        g[soft & near, :3] = ink
        g = outline(np.pad(g, ((1, 1), (1, 1), (0, 0))), ink)
        ys, xs = np.nonzero(g[..., 3] > 0)
        x0, y0 = xs.min(), ys.min()
        pic = g[y0:ys.max() + 1, x0:xs.max() + 1]
        out[name] = (pic, (G.left + 1 - x0, pic.shape[0]))   # the root: dense px from the picture's top left (soles)
    return out, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaw", type=int, default=70)
    ap.add_argument("--transfer", type=float, default=0.6)
    ap.add_argument("--review")
    a = ap.parse_args()
    poses, f = build(a.yaw, a.transfer)
    meta = {"ppu": 1.5, "yaw": a.yaw, "transfer": a.transfer, "render_px_a_square": round(f, 3)}
    for name, (pic, rootxy) in poses.items():
        Image.fromarray(pic).save(lp(os.path.join(HD, f"soldier_side_{name}.png")))
        meta[name] = {"size": [pic.shape[1], pic.shape[0]], "root": [int(rootxy[0]), int(rootxy[1])]}
        print(name, pic.shape[1], "x", pic.shape[0], "root", meta[name]["root"])
    with open(lp(os.path.join(HD, "soldier_side.json")), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1)
    if a.review:
        # each pose at 8x standing on its root, the front design first
        Z, gap = 8, 16
        front = np.asarray(Image.open(lp(os.path.join(HD, "soldier.png"))).convert("RGBA"))
        tiles = [(front, (front.shape[1] // 2, front.shape[0]))] + [poses[n] for n in POSES]
        H = max(p.shape[0] for p, _ in tiles) * Z + 10
        W = sum(p.shape[1] * Z + gap for p, _ in tiles)
        sheet = Image.new("RGB", (W, H), (96, 112, 96))
        x = 0
        for p, (rx, ry) in tiles:
            im = Image.fromarray(p).resize((p.shape[1] * Z, p.shape[0] * Z), Image.NEAREST)
            sheet.paste(im, (x, H - 5 - ry * Z), im)
            x += im.width + gap
        os.makedirs(a.review, exist_ok=True)
        out = os.path.join(a.review, f"soldier_side_yaw{a.yaw}_t{a.transfer}.png")
        sheet.save(out)
        print(out, sheet.size)


if __name__ == "__main__":
    main()
