#!/usr/bin/env python3
"""league_urgot's action frames posed from the approved design's own squares (league_tahmkench / league_aphelios's way:
「动作帧的话可以学习塔姆那种方法做 不依赖codex 但是要做完美 做完美了后再喊我review」).

    python tools/art/rig_urgot.py --review DIR      # every tag on the canvas, 4x sheets + a GIF per tag + checks
    python tools/art/rig_urgot.py                   # the PPU frames -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero urgot && python tools/art/ppu_hd.py --hero urgot

The design (assets/source/urgot/hd/design.png, 68 x 63 squares at the final PPU 1.5: Codex's step-1 take 2 with whole
rows and columns deleted, tools/art/design_urgot_cut.py; the user: 「造型用第 2 稿删行列的版本」) is posed without
rescaling. Its parts are told by fixed square ranges: the cannon arm (the spiked drum over the head and the barrel), the
upper body (head, torso, hood, the coiled drum, the hoses), the chassis, and six legs told by columns below LEG_ROW
(their claws). Moves are lossless (memory no-deformation-lossless-poses): whole-part translation, layering. What is new
is drawn from the design's own colours: the pillar he rises on in R (League's Spell4: the torso lifted on a column
out of the chassis), the shut eye of the death.
The muzzle flashes are drawn into his own frames (the client never mirrors an effect picture: SKILL.md "Both sides"),
in the 1x frames as drawn, in the PPU frames as orig/urgot_<tag>.over.png laid on after the outline by ppu_restyle.py
(fx=True).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


SRC = os.path.join(ROOT, "assets", "source", "urgot")
STEM = os.path.join(ROOT, "league", "champions", "league_urgot")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
PPU = 1.5
FEET = 11                         # 1x rows from the pivot down to the ground row
DESIGN = load(os.path.join(SRC, "hd", "design.png"))
DH, DW = DESIGN.shape[:2]         # 63 x 68
OUTLINE = (9, 5, 13)
OP = DESIGN[..., 3] > 0
R_, C_ = np.mgrid[0:DH, 0:DW]

# ------------------------------------------------------------------------------------------------- the canvas
CW, CH = 130, 104
SOLE = 94                         # the canvas row of the design's last row (the leg tips)
BODY_X = 34                       # the design column over the pivot: the chassis' middle (league_drmundo's lesson)
PIV_X = 56                        # the pivot column on the canvas
OX, OY = PIV_X - BODY_X, SOLE - (DH - 1)
CORNER = (PIV_X + 0.5, SOLE + 1)

# ------------------------------------------------------------------------------------------------- parts
# the spiked ring over the head (rows 0-7, its lower left edge on rows 8-9) and the barrel with its upper arm (columns
# 45 on, down to row 17); the hood's bronze plate and crimson lining behind the head stay with the upper body
CANNON = OP & (((R_ <= 7) & (C_ >= 27)) | ((R_ >= 8) & (R_ <= 9) & (C_ >= 23) & (C_ <= 31)) |
               ((R_ <= 17) & (C_ >= 45)))
# the six legs left to right, (first column, last column, top row): the side legs whole with their tall shields, the
# middle ones from below the chassis' rim (their claws and the shields over them)
LEG_BOX = [(0, 8, 29), (7, 16, 44), (17, 31, 50), (32, 47, 46), (48, 58, 46), (59, 67, 28)]


def leg_masks():
    out, taken = [], ~OP | CANNON
    for a, b, top in LEG_BOX:
        m = (C_ >= a) & (C_ <= b) & (R_ >= top) & ~taken
        out.append(m)
        taken = taken | m
    return out


LEGS = leg_masks()
CLAW = 5                          # a leg's last rows (the claw) are not laid under it when it moves
CHASSIS_ROW = 33                  # the upper body is everything above it but the cannon
UPPER = OP & ~CANNON & ((R_ < 28) | ((R_ < CHASSIS_ROW) & (C_ >= 11) & (C_ <= 51)))   # not the side legs' shields
LEGS = [m & ~UPPER for m in LEGS]
WAIST = 26                        # the upper body's rows from here down also stay put under it when it moves
LOWER = OP & ~UPPER & ~CANNON & ~np.any(LEGS, axis=0)


def blank():
    return np.zeros((CH, CW, 4), np.uint8)


def put(dst, src, mask, dx, dy, under=False):
    """src's squares under mask, moved (dx, dy), onto dst (under: only where dst is empty)."""
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
    if under:
        free = dst[ty, tx, 3] == 0
        ys, xs, ty, tx = ys[free], xs[free], ty[free], tx[free]
    dst[ty, tx] = src[ys, xs]


def pose(dx=0, bob=0, up=0, upper=(0, 0), cannon=(0, 0), legs=None, src=None, pillar=False, shut=False):
    """One frame: the whole figure dx columns on; the chassis bob rows down over the legs; the upper body `upper`
    (dx, dy) more and the cannon `cannon` (dx, dy) more on top of it; legs: [(dx, lift)] for L1..L6 (claws moved
    dx columns, lifted rows); up: the whole figure lifted (a hop)."""
    src = DESIGN if src is None else src
    if shut:
        src = src.copy()
        src[EYE] = (*OUTLINE, 255)
    can = blank()
    x0, y0 = OX + dx, OY - up
    legs = legs or [(0, 0)] * 6
    # each leg's upper part as it stands, under the moved legs (no hole opens where a lifted leg was), then the legs
    for m in LEGS:
        put(can, src, m & (R_ < np.nonzero(m.any(1))[0].max() - CLAW), x0, y0)
    for m, (ldx, lift) in zip(LEGS, legs):
        put(can, src, m, x0 + ldx, y0 - lift)
    put(can, src, LOWER, x0, y0 + bob)
    if pillar:            # R: the column he rises on, from the chassis to the lifted torso
        draw_pillar(can, x0, y0 + bob, -upper[1])
    elif upper != (0, 0):   # the torso's lower rows as they stand, under the moved upper body (no gap at the waist)
        put(can, src, UPPER & (R_ >= WAIST), x0, y0 + bob)
    put(can, src, UPPER, x0 + upper[0], y0 + bob + upper[1])
    if cannon[1] < 0:     # the ring's lower rows as they sat, under the lifted cannon (it never floats off the hood)
        put(can, src, CANNON & (R_ >= 5) & (C_ <= 52), x0 + upper[0], y0 + bob + upper[1], under=True)
    put(can, src, CANNON, x0 + upper[0] + cannon[0], y0 + bob + upper[1] + cannon[1])
    return can


EYE = OP & (DESIGN[..., 0] > 200) & (DESIGN[..., 1] < 60) & (DESIGN[..., 2] < 60) & (R_ < 20) & (C_ < 45)
STEEL_D, STEEL, STEEL_L = (34, 40, 66), (63, 77, 115), (118, 142, 186)
GOLD, GOLD_L = (206, 130, 40), (252, 208, 67)
PILLAR_COLS = (24, 41)            # the column's columns (under the torso), design squares


def draw_pillar(can, x0, y0, rise):
    """The column of R (League's Spell4): `rise` rows of dark steel from the chassis' rim (design row CHASSIS_ROW) up to
    the lifted torso, lit on its left, a gold band every 4 rows, outlined - in the design's own colours."""
    a, b = PILLAR_COLS
    top, bot = CHASSIS_ROW - 2 - rise, CHASSIS_ROW + 1
    for r in range(top, bot + 1):
        for c in range(a, b + 1):
            y, x = y0 + r, x0 + c
            if c in (a, b):
                v = OUTLINE
            elif (r - top) % 4 == 2:
                v = GOLD_L if c < a + 4 else GOLD
            else:
                v = STEEL_L if c < a + 3 else STEEL_D if c > b - 4 else STEEL
            can[y, x] = (*v, 255)


FLASH = ["..oo...",
         ".oyyo.o",
         "oywwyo.",
         "oywwyyo",
         ".oyyyo.",
         "o.oyo..",
         "...o..."]
FLASH_COL = {"w": (255, 250, 222), "y": (252, 208, 67), "o": (230, 120, 36)}


def flash_at(can, x, y, k=1.0):
    """The muzzle flash (FLASH, k = its size) with its middle on canvas square (x, y): an overlay of its own."""
    ov = np.zeros_like(can)
    h, w = len(FLASH), len(FLASH[0])
    n = max(3, int(round(h * k)))
    for j in range(n):
        for i in range(n):
            ch = FLASH[int(j * h / n)][int(i * w / n)]
            if ch in FLASH_COL:
                yy, xx = y - n // 2 + j, x - n // 2 + i
                if 0 <= yy < can.shape[0] and 0 <= xx < can.shape[1]:
                    ov[yy, xx] = (*FLASH_COL[ch], 255)
    return ov


MUZZLE = (66, 19)                 # design square just under the cannon's mouth (it hooks down at the barrel's end)


def muzzle(dx=0, cannon=(0, 0), upper=(0, 0), bob=0, up=0):
    return OX + dx + upper[0] + cannon[0] + MUZZLE[0], OY - up + bob + upper[1] + cannon[1] + MUZZLE[1]


def cut_ground(can):
    out = can.copy()
    out[SOLE + 1:] = 0
    return out


def flash(can, k=0.55):
    out = can.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


def tidy(a, hole=10, speck=4):
    """The outline closed round moved edges (strips.complete_outline), small enclosed holes filled with their
    commonest neighbour, loose specks off, nothing under the ground."""
    out = G.complete_outline(a, color=OUTLINE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > hole:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < speck:
                out[lbl == k] = 0
    out[SOLE + 1:] = 0
    return out


# ------------------------------------------------------------------------------------------------- the actions
IDLE_MS = 150
BREATH = [0, 0, 1, 1, 2, 2, 1, 1]          # the upper body's rise and fall (the BP idle rule: >= 2 rows)
RUN_MS = 120
GROUP_A, GROUP_B = (0, 2, 4), (1, 3, 5)   # two tripods (League's Urgot_RunSlow: the legs step in two sets)
# per frame: (A's (dx, lift), B's (dx, lift), chassis bob)
RUN = [((1, 2), (-1, 0), 0), ((2, 3), (-1, 0), 1), ((1, 1), (0, 0), 1), ((0, 0), (1, 0), 0),
       ((-1, 0), (1, 2), 0), ((-1, 0), (2, 3), 1), ((0, 0), (1, 1), 1), ((1, 0), (0, 0), 0)]


def legs_of(a, b):
    out = [(0, 0)] * 6
    for k in GROUP_A:
        out[k] = a
    for k in GROUP_B:
        out[k] = b
    return out


def frames():
    out = {}
    out["idle"] = [(pose(upper=(0, -b), cannon=(0, [0, 0, 0, 1, 1, 1, 0, 0][i])), IDLE_MS)
                   for i, b in enumerate(BREATH)]
    out["run"] = [(pose(bob=bob, upper=(0, bob), legs=legs_of(a, b)), RUN_MS) for a, b, bob in RUN]
    # the shot (League's Urgot_Attack1: the cannon dips at the target, kicks up as it fires; release ~130 ms in)
    out["attack"] = [(pose(upper=(1, 0), cannon=(1, 1)), 130, None),
                     (pose(cannon=(-1, -3)), 60, flash_at(blank(), *muzzle(cannon=(-1, -3)), 1.0)),
                     (pose(cannon=(-1, -1)), 60, flash_at(blank(), *muzzle(cannon=(-1, -1)), 0.6)),
                     (pose(cannon=(0, -1)), 90, None), (pose(), 90, None)]
    # Purge's machine gun: a small kick and flash each shot (10 ticks)
    out["attack_w"] = [(pose(cannon=(0, -1)), 80, flash_at(blank(), *muzzle(cannon=(0, -1)), 0.6)),
                       (pose(), 87, None)]
    # Q Corrosive Charge: the cannon raised to lob, the charge leaves at ~100 ms
    out["skill"] = [(pose(upper=(-1, 0), cannon=(0, -4)), 100, None),
                    (pose(upper=(-1, 0), cannon=(-1, -5)), 80,
                     flash_at(blank(), *muzzle(upper=(-1, 0), cannon=(-1, -5)), 1.0)),
                    (pose(cannon=(0, -2)), 80, None), (pose(), 73, None)]
    # E Disdain: a crouch, the charge (legs gathered), the catch (the upper body thrown forward), the fling over him
    out["skill2"] = [(pose(bob=1, upper=(0, 1)), 80, None),
                     (pose(dx=2, upper=(2, 0), legs=legs_of((1, 2), (1, 2))), 100, None),
                     (pose(dx=3, upper=(3, 1), cannon=(1, 0)), 100, None),
                     (pose(dx=1, upper=(-2, -2), cannon=(-1, -1)), 100, None), (pose(), 53, None)]
    # R Fear Beyond Death: the torso rises on its column, the drill fires from the chest (~130 ms), it sinks back
    out["ult"] = [(pose(upper=(0, -4), pillar=True), 70, None), (pose(upper=(0, -7), pillar=True), 60, None),
                  (pose(upper=(0, -7), cannon=(0, -1), pillar=True), 100, flash_at(blank(), OX + 46, OY - 7 + 24, 1.0)),
                  (pose(upper=(0, -7), pillar=True), 100, None), (pose(upper=(0, -4), pillar=True), 90, None),
                  (pose(), 80, None)]
    # death: the blow, the legs giving (the chassis sinking over them), the cannon drooping, down, still
    out["dead"] = [(pose(dx=-2, upper=(0, 1)), 100, None),
                   (pose(dx=-2, bob=3, upper=(0, 1), cannon=(1, 2)), 120, None),
                   (cut_ground(pose(dx=-2, bob=7, upper=(0, 1), cannon=(2, 4))), 120, None),
                   (cut_ground(pose(dx=-2, bob=11, upper=(0, 1), cannon=(2, 6), shut=True)), 150, None),
                   (cut_ground(pose(dx=-2, bob=13, upper=(0, 1), cannon=(2, 7), shut=True)), 400, None)]
    out["hit"] = [(pose(dx=-2), 90), (pose(dx=-1), 120)]
    return out


def actions():
    """{tag: [(frame, ms, flash overlay or None)]}: every frame tidied, the hit's first frame flashed after it."""
    acts = {}
    for t, fr in frames().items():
        acts[t] = [(tidy(f[0]), f[1], f[2] if len(f) > 2 else None) for f in fr]
    acts["hit"][0] = (flash(acts["hit"][0][0]), *acts["hit"][0][1:])
    return acts


def shown(f):
    """A frame with its flash on top (the review)."""
    can, _, ov = f
    if ov is None:
        return can
    out = can.copy()
    m = ov[..., 3] > 0
    out[m] = ov[m]
    return out


# ------------------------------------------------------------------------------------------------- checks and review
def stats(can):
    op = can[..., 3] > 0
    n = ndimage.label(op, structure=np.ones((3, 3)))[1]
    holes = int((ndimage.binary_fill_holes(op) & ~op).sum())
    return n, holes, int(op.sum())


def checks(acts):
    base = tidy(pose())
    _, bh, ba = stats(base)
    pal = {tuple(int(v) for v in c) for c in DESIGN[OP][:, :3]}
    for tag, fr in acts.items():
        rep = []
        for j, (can, _, _) in enumerate(fr):
            op = can[..., 3] > 0
            n, holes, area = stats(can)
            extra = len({tuple(int(v) for v in c) for c in can[op][:, :3]} - pal)
            bad = n != 1 or holes > bh or (extra and tag != "hit")
            rep.append(f"{j + 1}:{'!' if bad else ''}p{n} h{holes - bh:+d} c{extra} a{100 * area // ba}%")
        print(f"{tag:8s} " + "  ".join(rep))


def review(acts, out_dir, z=4):
    os.makedirs(out_dir, exist_ok=True)
    for tag, fr in acts.items():
        allc = np.stack([shown(f) for f in fr])
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = ys.min() - 2, SOLE + 3, xs.min() - 2, xs.max() + 3
        tiles = []
        for f in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(shown(f)[y0:y1, x0:x1]))
            tiles.append(bg.convert("RGB"))
        big = [t.resize((t.width * z, t.height * z), Image.NEAREST) for t in tiles]
        sheet = Image.new("RGB", (len(big) * (big[0].width + 6), big[0].height), (60, 60, 60))
        for i, t in enumerate(big):
            sheet.paste(t, (i * (t.width + 6), 0))
        sheet.save(os.path.join(out_dir, f"urgot_{tag}.png"))
        small = [t.resize((t.width * 3, t.height * 3), Image.NEAREST) for t in tiles]
        pal_src = Image.new("RGB", (small[0].width, small[0].height * len(small)))
        for i, t in enumerate(small):
            pal_src.paste(t, (0, i * t.height))
        pal = pal_src.quantize(255, dither=Image.Dither.NONE)
        q = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in small]
        q[0].save(os.path.join(out_dir, f"urgot_{tag}.gif"), save_all=True, append_images=q[1:],
                  duration=[f[1] for f in fr], loop=0, optimize=False)
    print("review ->", out_dir)


# ------------------------------------------------------------------------------------------------- the game's frames
ORDER = ["idle", "run", "attack", "attack_w", "skill", "skill2", "ult", "hit", "dead"]


def one_of(can, px, py, hw, hh, need=0.5):
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_hd(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


def down(can, ov=None):
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot, the flash's PPU frame
    cut alike or None). The pivot: the pivot column, FEET 1x rows above the ground line. A flash (an overlay on the
    canvas) is in the box too; the 1x frame gets its 1x picture on top (no outline round the light)."""
    px, py = CORNER[0], CORNER[1] - FEET * PPU
    both = can[..., 3] > 0
    if ov is not None:
        both = both | (ov[..., 3] > 0)
    ys, xs = np.nonzero(both)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh), color=OUTLINE)[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    if ov is None:
        return one, crop_hd(can, px, py, W, H), None
    f1 = one_of(ov, px, py, hw, hh, need=0.3)
    m = f1[..., 3] > 0
    one[m] = f1[m]
    return one, crop_hd(can, px, py, W, H), crop_hd(ov, px, py, W, H)


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def export(acts):
    sheet = {}
    os.makedirs(lp(ORIG), exist_ok=True)
    for tag in ORDER:
        ones, hds, ovs = [], [], []
        for can, t, ov in acts[tag]:
            one, hd, o = down(can, ov)
            ones.append((one, float(t)))
            hds.append(hd)
            ovs.append(o if o is not None else np.zeros_like(hd))
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"urgot_{tag}.png")))
        over_png = lp(os.path.join(ORIG, f"urgot_{tag}.over.png"))
        if any(ov is not None for _, _, ov in acts[tag]):
            Image.fromarray(strip_of(ovs)).save(over_png)
        elif os.path.isfile(over_png):
            os.remove(over_png)
        with open(lp(os.path.join(ORIG, f"urgot_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_urgot#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="the frames at 4x and a GIF per tag here (nothing written to the repo)")
    a = ap.parse_args()
    acts = actions()
    checks(acts)
    if a.review:
        review(acts, a.review)
        return
    export(acts)


if __name__ == "__main__":
    main()
