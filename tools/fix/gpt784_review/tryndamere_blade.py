"""league_tryndamere's scimitar 1.25x in every dense frame (the user, 2026-11-19: 「蛮王的刀做的太小了吧？」, then of a
mock-up at 1.25x / 1.4x / 1.6x: 「用这个就行」 for 1.25x, 「可以，全部做」).

GPT's frames are generations, not a body + a blade layer: each draws its own blade, in the body's own colours (48 of the
blade's 49 colours are the body's too; only the bright edge's are the blade's alone), so no colour or layer tells the
blade apart. A first pass drew one standard blade into every frame: the run's long thin blade turned into the idle's
broad one (the user: 「刀变形了吧 1.25的」). So each frame keeps the blade it drew, 1.25x:

- where the blade is: idle_base[0]'s blade (opaque, left of x 29 and below y 46, not skin: the largest piece, with the
  dark outline squares next to it outside) is the probe; per frame (tryndamere_blade.json, read off by matching it,
  turned and mirrored, against each frame) the mirror, the angle and length it fits the drawn blade at and the grip;
- the drawn blade: the probe's squares at that grip / length, the fitted angle +-2, widened by one, not skin; the bright
  edge squares within 3 of them; the dark outline squares next to that which touch clear (tight: a looser one took
  the boot beside skill_q's blade tip and the fire beside ult[7]'s along);
- that blade, alone on a clear layer, x 1.25 about the grip (turned by "turn" degrees where it would go more than 3
  squares below the feet and the drawn blade), sampled from an 8x EPX (scale2x) picture of the layer (edges stay one
  colour, no new colours), drawn in only on clear squares and on the drawn blade's (the fist stays over the hilt); old
  bright-edge squares (the blade's alone) it did not cover go; squares of the drawn blade it does not cover go clear,
  or take the nearest figure colour inside the figure; the old outline left in the air (dark squares that had a
  coloured square within 2 and have none now) goes, so do pieces of up to 12 squares cut off near the blade; new
  pinholes are closed, new one-square-wide dark strokes go;
- ult[5] and ult[6] hold the blade up over the fire: their own blade (the box over the guard) is scaled 1.25x about the
  guard; ult[1..4] are left: the blade is inside the fire there;
- the effect bakes (skill_fx1 = skill + e_spin, skill_q_fx1 = skill_q + q_heal; tryndamere_bake.json) are made again:
  each frame's own effect squares (where it differs from the base frame it was baked on, at the offset given) over the
  new base frame.

The 1x and lo_ frames get only the squares that differ between the sheetkit derivation of the old and the new dense
frame (tools/fix/xinzhao_galio_1119/sheetkit.py); the strips (assets/source/ppu[/orig]/tryndamere_<tag>.png, the
idle_base frames in tryndamere_idle.png) are rewritten from the dense frames.

    python tools/fix/gpt784_review/tryndamere_blade.py --from 32af55934     # the frames before the change
    python -I tools/art/thin_outline.py --hero league_tryndamere             # evens the outline (a few squares)
    python tools/fix/gpt784_review/tryndamere_blade.py --check              # the sheet's frames = this tool's from REV,
                                                                             # but for outline squares
"""
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

STEM = "league/champions/league_tryndamere"
PARAMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tryndamere_blade.json")
REV = "32af55934"
SCALE = 1.25
PAD = 24
KEEP = 2
GRIP = (29.0, 48.0)
FX = {"skill_fx1": "skill", "skill_q_fx1": "skill_q"}
REELS = ("idle", "bp")


# ---- pixel-art scaling / rotation (EPX to 8x, nearest back)

def scale2x(a):
    H, W = a.shape[:2]
    key = (a[..., 0].astype(np.int64) << 24) | (a[..., 1].astype(np.int64) << 16) | (a[..., 2].astype(np.int64) << 8) | a[..., 3]
    p = np.pad(key, 1, mode="edge")
    P = key
    A, D, C, B = p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]
    out = np.zeros((2 * H, 2 * W), np.int64)
    out[0::2, 0::2] = np.where((C == A) & (C != D) & (A != B), A, P)
    out[0::2, 1::2] = np.where((A == B) & (A != C) & (B != D), B, P)
    out[1::2, 0::2] = np.where((D == C) & (D != B) & (C != A), C, P)
    out[1::2, 1::2] = np.where((B == D) & (B != A) & (D != C), D, P)
    res = np.zeros((2 * H, 2 * W, 4), np.uint8)
    for k, sh in enumerate((24, 16, 8, 0)):
        res[..., k] = (out >> sh) & 255
    return res


def transform(big, pivot, scale, angle, mirror, out_shape, out_pivot):
    """the 8x EPX picture `big` of a sprite: scaled / turned (degrees, y down) / mirrored about pivot into out_shape with
    the pivot at out_pivot"""
    H8, W8 = big.shape[:2]
    oh, ow = out_shape
    Y, X = np.mgrid[0:oh, 0:ow]
    u = X + 0.5 - out_pivot[0]
    v = Y + 0.5 - out_pivot[1]
    t = np.deg2rad(angle)
    cu = (np.cos(t) * u + np.sin(t) * v) / scale
    cv = (-np.sin(t) * u + np.cos(t) * v) / scale
    if mirror:
        cu = -cu
    ix = np.floor((pivot[0] + cu) * 8).astype(int)
    iy = np.floor((pivot[1] + cv) * 8).astype(int)
    ok = (ix >= 0) & (ix < W8) & (iy >= 0) & (iy < H8)
    out = np.zeros((oh, ow, 4), np.uint8)
    out[ok] = big[iy[ok], ix[ok]]
    return out


# ---- colours

def skinlike(p):
    r, g, b = p[..., 0].astype(int), p[..., 1].astype(int), p[..., 2].astype(int)
    return (r > 150) & (g > 100) & (b > 70) & (r - g < 80)


def bright_edge(p):
    r, g, b = p[..., 0].astype(int), p[..., 1].astype(int), p[..., 2].astype(int)
    return (r >= 150) & (r - g >= 60) & (r - b >= 50)


def dark(p):
    return p[..., :3].max(-1) < 45


# ---- the sprite

def sprite(idle):
    H, W = idle.shape[:2]
    a = idle[..., 3] > 0
    yy, xx = np.mgrid[0:H, 0:W]
    m = a & (xx < 29) & (yy > 46) & ~skinlike(idle[..., :3])
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    sz = ndimage.sum(m, lab, range(1, n + 1))
    m = lab == (int(np.argmax(sz)) + 1)
    pad = np.pad(a, 1)
    clear_nb = ~pad[:-2, 1:-1] | ~pad[2:, 1:-1] | ~pad[1:-1, :-2] | ~pad[1:-1, 2:]
    ring = ndimage.binary_dilation(m, iterations=2) & a & dark(idle) & clear_nb & ~m
    spr = np.zeros_like(idle)
    spr[m | ring] = idle[m | ring]
    return spr


def footprint_offsets(big, scale, angle, mirror, R=60):
    img = transform(big, GRIP, scale, angle, mirror, (2 * R, 2 * R), (R, R))
    ys, xs = np.nonzero(img[..., 3] > 0)
    return np.stack([xs - R, ys - R], 1)


# ---- one base frame

def tight_blade(f, big, p):
    H, W = f.shape[:2]
    foot = np.zeros((H, W), bool)
    for da in (-2, 0, 2):
        off = footprint_offsets(big, p["scale"], p["fit"] + da, p["mirror"])
        x = p["grip"][0] + off[:, 0]
        y = p["grip"][1] + off[:, 1]
        ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
        foot[y[ok], x[ok]] = True
    a = f[..., 3] > 0
    M = ndimage.binary_dilation(foot, iterations=1) & a & ~skinlike(f[..., :3])
    near = ndimage.binary_dilation(M, iterations=3) & a & ~M
    M = M | (near & bright_edge(f[..., :3]))
    pa = np.pad(a, 1)
    clear_nb = ~pa[:-2, 1:-1] | ~pa[2:, 1:-1] | ~pa[1:-1, :-2] | ~pa[1:-1, 2:]
    ring = ndimage.binary_dilation(M, iterations=1) & a & dark(f) & clear_nb & ~M
    return M | ring


def edge_leftovers(old, new, MM, nbm):
    left = (old[..., 3] > 0) & bright_edge(old[..., :3]) & ~nbm & ~MM & (new == old).all(-1)
    left &= ndimage.binary_dilation(nbm | MM, iterations=3)
    if not left.any():
        return new
    out = new.copy()
    a = out[..., 3] > 0
    pa = np.pad(a, 1)
    clear_nb = ~pa[:-2, 1:-1] | ~pa[2:, 1:-1] | ~pa[1:-1, :-2] | ~pa[1:-1, 2:]
    out[left & clear_nb] = 0
    rest = left & ~clear_nb
    if rest.any():
        src = (out[..., 3] > 0) & ~bright_edge(out[..., :3])
        idx = ndimage.distance_transform_edt(~src, return_distances=False, return_indices=True)
        out[rest] = out[idx[0][rest], idx[1][rest]]
    return out


def finish(base, old, MM, nbm):
    """after the old blade is out and the new one in: inner holes filled, orphan outline and cut-off pieces cleared"""
    hole = MM & (base[..., 3] == 0)
    if hole.any():
        fig = ndimage.binary_fill_holes(base[..., 3] > 0)
        inner = hole & fig
        if inner.any():
            idx = ndimage.distance_transform_edt(~(base[..., 3] > 0), return_distances=False, return_indices=True)
            base[inner] = base[idx[0][inner], idx[1][inner]]
    a = base[..., 3] > 0
    dk = dark(base)
    dist = ndimage.distance_transform_cdt(~(a & ~dk), metric="taxicab")
    oa = old[..., 3] > 0
    odist = ndimage.distance_transform_cdt(~(oa & ~dark(old)), metric="taxicab")
    zone = ndimage.binary_dilation(MM | nbm, iterations=4)
    base[a & dk & zone & (dist > KEEP) & (odist <= KEEP)] = 0
    return base, zone


def drop_islands(base, zone):
    lab, n = ndimage.label(base[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        keep = int(np.argmax(sizes)) + 1
        for k in range(1, n + 1):
            if k != keep and sizes[k - 1] <= 12 and (zone & (lab == k)).any():
                base[lab == k] = 0
    return base


def with_own_blade(f, big, p):
    """the frame's own blade (tight_blade) x SCALE about the grip, turned by p["turn"]"""
    H, W = f.shape[:2]
    M = tight_blade(f, big, p)
    layer = np.zeros_like(f)
    layer[M] = f[M]
    lbig = scale2x(scale2x(scale2x(layer)))
    base = np.zeros((H + 2 * PAD, W + 2 * PAD, 4), np.uint8)
    base[PAD:PAD + H, PAD:PAD + W] = f
    old = base.copy()
    MM = np.zeros(base.shape[:2], bool)
    MM[PAD:PAD + H, PAD:PAD + W] = M
    g = (p["grip"][0] + 0.5, p["grip"][1] + 0.5)
    nb = transform(lbig, g, SCALE, p["turn"], False, base.shape[:2], (g[0] + PAD, g[1] + PAD))
    base[MM] = 0
    put = (nb[..., 3] > 0) & ((old[..., 3] == 0) | MM)
    base[put] = nb[put]
    base = edge_leftovers(old, base, MM, nb[..., 3] > 0)
    base, zone = finish(base, old, MM, nb[..., 3] > 0)
    return drop_islands(base, zone)


def with_own(f, box, grip):
    """the frame's own blade (the box) x SCALE about grip"""
    H, W = f.shape[:2]
    x0, y0, x1, y1 = box
    M = np.zeros((H, W), bool)
    M[y0:y1, x0:x1] = True
    M &= f[..., 3] > 0
    base = np.zeros((H + 2 * PAD, W + 2 * PAD, 4), np.uint8)
    base[PAD:PAD + H, PAD:PAD + W] = f
    old = base.copy()
    MM = np.zeros(base.shape[:2], bool)
    MM[PAD:PAD + H, PAD:PAD + W] = M
    Y, X = np.mgrid[0:H + 2 * PAD, 0:W + 2 * PAD]
    ix = np.floor((X - PAD - grip[0]) / SCALE + grip[0] + 0.5).astype(int)
    iy = np.floor((Y - PAD - grip[1]) / SCALE + grip[1] + 0.5).astype(int)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    sel = np.zeros_like(ok)
    sel[ok] = M[iy[ok], ix[ok]]
    nb = np.zeros_like(base)
    nb[sel] = f[iy[sel], ix[sel]]
    base[MM] = 0
    put = (nb[..., 3] > 0) & ((old[..., 3] == 0) | MM)
    base[put] = nb[put]
    base, zone = finish(base, old, MM, nb[..., 3] > 0)
    return base


def strokes_and_pins(c):
    a = c[..., 3] > 0
    dk = a & dark(c)
    pa = np.pad(a, 1)
    thin = dk & ((~pa[1:-1, :-2] & ~pa[1:-1, 2:]) | (~pa[:-2, 1:-1] & ~pa[2:, 1:-1]))
    pin = ~a & pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:]
    return thin, pin


def clean(old, new):
    out = new.copy()
    for _ in range(3):
        to, po = strokes_and_pins(old)
        tn, pn = strokes_and_pins(out)
        addp, addt = pn & ~po, tn & ~to
        if not addp.any() and not addt.any():
            break
        for y, x in np.argwhere(addp):
            nb = [out[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))]
            out[y, x] = min(nb, key=lambda q: int(q[0]) + int(q[1]) + int(q[2]))
        out[addt] = 0
    return out


def rebake(fx, base_old, base_new_padded, ox, oy):
    Hf, Wf = fx.shape[:2]
    Hb, Wb = base_old.shape[:2]
    canvas_old = np.zeros_like(fx)
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(Wf, ox + Wb), min(Hf, oy + Hb)
    canvas_old[y0:y1, x0:x1] = base_old[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    effect = (fx[..., 3] > 0) & ~((fx == canvas_old).all(-1))
    out = np.zeros((Hf + 2 * PAD, Wf + 2 * PAD, 4), np.uint8)
    Hn, Wn = base_new_padded.shape[:2]
    X0, Y0 = max(0, ox), max(0, oy)
    X1, Y1 = min(Wf + 2 * PAD, ox + Wn), min(Hf + 2 * PAD, oy + Hn)
    out[Y0:Y1, X0:X1] = base_new_padded[Y0 - oy:Y1 - oy, X0 - ox:X1 - ox]
    inner = out[PAD:PAD + Hf, PAD:PAD + Wf]
    inner[effect] = fx[effect]
    return out


# ---- the whole sheet

def frames_of(sheet, anims):
    """{rect: (tag, i)} for the dense frames (first name of each rect; reels left out) and the picture of each"""
    first, pics = {}, {}
    for t in anims:
        if not t.startswith("hd_") or t[3:] in REELS:
            continue
        for i, fr in enumerate(anims[t]["frames"]):
            d = fr["data"]
            r = tuple(int(round(d[q])) for q in ("x", "y", "w", "h"))
            if r not in first:
                first[r] = (t[3:], i)
                x, y, w, h = r
                pics[r] = sheet[y:y + h, x:x + w].copy()
    return first, pics


def build(sheet, anims):
    """{rect: new dense picture} from a sheet as it was before the change"""
    params = json.load(open(PARAMS, encoding="utf-8"))
    first, pics = frames_of(sheet, anims)
    by_name = {f"{t}[{i}]": r for r, (t, i) in first.items()}
    idle = pics[by_name["idle_base[0]"]]
    big = scale2x(scale2x(scale2x(sprite(idle))))
    out, padded = {}, {}

    def rect(tag, i):
        d = anims["hd_" + tag]["frames"][i]["data"]
        return tuple(int(round(d[q])) for q in ("x", "y", "w", "h"))

    for r, (t, i) in first.items():
        if t in FX:
            continue
        p = params[f"{t}[{i}]"]
        f = pics[r]
        if "skip" in p:
            out[r] = f.copy()
            padded[r] = np.pad(f, ((PAD, PAD), (PAD, PAD), (0, 0)))
            continue
        o = with_own(f, p["own"], p["grip"]) if "own" in p else with_own_blade(f, big, p)
        H, W = f.shape[:2]
        pic = clean(f, o[PAD:PAD + H, PAD:PAD + W].copy())
        o[PAD:PAD + H, PAD:PAD + W] = pic
        if (o[..., 3] > 0).sum() != (pic[..., 3] > 0).sum():
            sys.exit(f"{t}[{i}]: the new blade leaves the frame")
        out[r], padded[r] = pic, o
    for r, (t, i) in first.items():
        if t not in FX:
            continue
        b, j, ox, oy = params[f"{t}[{i}]"]["bake"]
        rb = rect(b, j)
        fx = pics[r]
        o = rebake(fx, pics[rb], padded[rb], ox, oy)
        H, W = fx.shape[:2]
        out[r] = clean(fx, o[PAD:PAD + H, PAD:PAD + W].copy())
    return first, out


def show(rev, path):
    return subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout


def strip_name(t):
    return "idle" if t == "idle_base" else t


def write_strip(k, t):
    n = len(k.anims["hd_" + t]["frames"])
    pics = [k.cell("hd_" + t, i) for i in range(n)]
    H = max(p.shape[0] for p in pics)
    W = sum(p.shape[1] for p in pics) + len(pics) - 1
    st = np.zeros((H, W, 4), np.uint8)
    x = 0
    for p in pics:
        st[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1] + 1
    for sub in ("", "orig"):
        d = os.path.join(ROOT, "assets", "source", "ppu", sub)
        js = os.path.join(d, f"tryndamere_{strip_name(t)}.json")
        if not os.path.isfile(js):
            continue
        meta = json.load(open(js))
        meta["sizes"] = [[p.shape[1], p.shape[0]] for p in pics]
        Image.fromarray(st).save(os.path.join(d, f"tryndamere_{strip_name(t)}.png"))
        json.dump(meta, open(js, "w"))


def main():
    rev = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else REV
    sheet = np.asarray(Image.open(io.BytesIO(show(rev, STEM + "#sheet.png"))).convert("RGBA"))
    anims = json.loads(show(rev, STEM + "#anim.fanim").decode("utf-8-sig"))["anims"]
    first, new = build(sheet, anims)
    k = Kit(ROOT, "league", "tryndamere")
    if "--check" in sys.argv:
        # thin_outline.py --hero league_tryndamere evens the outline after this tool: a square may differ only
        # between the outline colour and clear
        oc = json.load(open(os.path.join(ROOT, "tools", "art", "thin_outline.json"), encoding="utf-8"))["league_tryndamere"]
        outline = [tuple(c) for c in oc["outline"]]
        bad = []
        for r, (t, i) in first.items():
            have, want = k.cell("hd_" + t, i), new[r]
            if have.shape != want.shape:
                bad.append(f"{t}[{i}]")
                continue
            diff = (have != want).any(-1)
            for y, x in np.argwhere(diff):
                ok = all(px[3] == 0 or tuple(int(v) for v in px[:3]) in outline for px in (have[y, x], want[y, x]))
                if not ok:
                    bad.append(f"{t}[{i}]")
                    break
        print("tryndamere blade: OK" if not bad else f"tryndamere blade: {len(bad)} frames not as this tool leaves them: {bad[:8]}")
        sys.exit(1 if bad else 0)
    touched = set()
    moved = 0
    for r, (t, i) in first.items():
        old_hd = k.cell("hd_" + t, i)
        if old_hd.shape != new[r].shape:
            sys.exit(f"{t}[{i}]: the sheet's frame is not REV's")
        if np.array_equal(old_hd, new[r]):
            continue
        shape = k.cell(t, i).shape[:2]
        for pre, make in (("", k.one_of), ("lo_", k.lo_of)):
            small = k.cell(pre + t, i)
            a, b = make(shape, old_hd), make(shape, new[r])
            if a.shape != small.shape or b.shape != small.shape:
                sys.exit(f"{t}[{i}] {pre or '1x'}: derived {a.shape} / {b.shape} vs the sheet's {small.shape}")
            diff = (a != b).any(-1)
            small[diff] = b[diff]
            k.put(pre + t, i, small)
        k.put("hd_" + t, i, new[r])
        moved += 1
        touched.add(t)
    k.save()
    for t in sorted(touched):
        write_strip(k, t)
    print(f"tryndamere blade: {moved} dense frames changed ({', '.join(sorted(touched))})")


if __name__ == "__main__":
    main()
