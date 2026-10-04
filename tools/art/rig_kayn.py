#!/usr/bin/env python3
"""Kayn's action frames posed with the approved designs' own pixels (the Nocturne rig's way, tools/art/rig_nocturne.py).

    python tools/art/rig_kayn.py parts <form> [--out PNG]            # the cut: every part tinted, joints marked
    python tools/art/rig_kayn.py pose <posefile.json> [--frame k] [--out PNG]
    python tools/art/rig_kayn.py apply <posefile.json>               # write the posed frames into the repair strips

Why: Codex's strips drew Kayn a size bigger than the approved designs (body, scythe) and with broken parts; the repair
(work/ka/fixkit.py, 2026-10-04) brought every frame back to the design's body, but several actions lost League's
motion (the attack's lunge, W's leap, R's landing crouch, the Darkin's swing). The user picked "keep the repaired
bodies, bring the motion back" - so the stiff frames are posed again from the design's own parts after League's frame
and Codex's drawing of it.

Parts (assets/source/kayn/rig/<form>_parts.png + <form>_parts.json): a label picture the size of the design canvas
(128 x 128, 1 px = 1 game pixel) where each part has its own flat colour (the json maps colour -> part), the joints
(x, y on the canvas) each part turns about and is placed by, the drawing order, and "under" pixels: what a part shows
where another part covered it in the design (the trousers behind the shaft, the torso behind an arm) - kept in
<form>_under.png (RGBA, only those pixels). A part's design pixels that lie in front of a part drawn after it (the
shadow's tassel and obi end over the shaft) are listed in the json "front": [{"part", "over", "pixels"}]: they move with
their part and are drawn again right after "over", so "over" can stay whole (no sprite swap) and the identity holds.
Extra sprites (a bent leg, a crouching pair of legs ...) drawn once from
the design's own colours live in assets/source/kayn/rig/<form>_<name>.png with their joint in the json ("sprites").

A pose file (json) lists frames for one strip:
  {"tag": "attack", "frames": [ {"keep": true},
      {"move": [dx, dy], "lean": 0.08, "order": [...],
       "parts": {"near_arm": [["deg", 40], ["at", 1, -2]], "far_leg": [["sprite", "far_leg_bent"]], ...},
       "bridges": [{"from": [x, y], "to": [x, y], "colour": "#FEBF91", "width": 2}],
       "paint": [[x, y, "#hex"], ...], "erase": [[x, y], ...] } ... ]}
  ops, applied in order about the part's joint: ["at", dx, dy] (move), ["deg", a] (RotSprite, + = counter-clockwise),
  ["rot", q] (quarter turns ccw, lossless), ["flip"] (mirror left-right), ["shear", k] (rows over the joint move k px
  per row: + leans the top right), ["sprite", name] (use the named extra sprite instead of the part's own pixels).
  "move" shifts the whole figure; "lean" shears the whole figure about the pivot (+ leans forward = right); bridges
  draw a limb segment (colour core, outline round it); paint/erase are last touches in CELL coordinates.
Frames are built on the strip's cell (96 x 128) with the design's pivot on the frame's pivot (cells.json); nothing
below row 81 (the soles' row). "keep" leaves the repaired frame as it is.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WS = os.path.dirname(ROOT)
sys.path.insert(0, HERE)
import kayn_kit as K  # noqa: E402

RIG = os.path.join(ROOT, "assets", "source", "kayn", "rig")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN_FILE = {"base": "kayn_native.png", "darkin": "kayn_darkin_native.png", "shadow": "kayn_shadow_native.png"}
PIVOT = (64, 88)            # the designs' pivot on their 128 x 128 canvas
OUTLINE = (0x0B, 0x07, 0x10)
FEET_ROW = 81
FRONT = {}                  # form -> [(part, over, canvas mask)] from the json's "front" (see load_parts)
FRONT_KEY = (1, 254, 2)     # stand-in colour for the rest of a part while its front pixels are moved with it


def lp(p):
    return K.lp(p)


def design(form):
    a = np.asarray(Image.open(lp(os.path.join(NATIVE, DESIGN_FILE[form]))).convert("RGBA"))[4::8, 4::8].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_parts(form):
    """{part: (sprite RGBA, joint (x, y) in the sprite)}, the order, and extra sprites."""
    with open(lp(os.path.join(RIG, f"{form}_parts.json")), encoding="utf-8") as f:
        spec = json.load(f)
    lab = np.asarray(Image.open(lp(os.path.join(RIG, f"{form}_parts.png"))).convert("RGB"))
    under_path = os.path.join(RIG, f"{form}_under.png")
    under = np.asarray(Image.open(lp(under_path)).convert("RGBA")) if os.path.exists(lp(under_path)) else None
    d = design(form)
    parts = {}
    for colour, name in spec["labels"].items():
        m = (lab == np.array(hexrgb(colour), np.uint8)).all(-1) & (d[..., 3] > 0)
        img = np.zeros_like(d)
        img[m] = d[m]
        if under is not None and name in spec.get("under", []):
            # under pixels belong to the part named for them in the json ("under": [part, ...] with an "under_label"
            # picture of the same colours) - kept simple: <form>_under_<part>.png when present
            pass
        upath = os.path.join(RIG, f"{form}_under_{name}.png")
        if os.path.exists(lp(upath)):
            u = np.asarray(Image.open(lp(upath)).convert("RGBA"))
            um = (u[..., 3] > 0) & ~m
            img[um] = u[um]
        if not (img[..., 3] > 0).any():
            continue
        jx, jy = spec["joints"][name]
        parts[name] = (img, (jx, jy))
    # "front": [{"part": "torso", "over": "scythe", "pixels": [[x, y], ...]}] - design pixels of `part` that sit in
    # front of `over` although `part` is drawn first (the shadow's tassel over the shaft): `over` keeps its whole
    # shape (its under pixels there) and these pixels of `part`, moved with it, are drawn again right after `over`.
    FRONT[form] = []
    for fr in spec.get("front", []):
        if fr["part"] in parts:
            fm = np.zeros(d.shape[:2], bool)
            for x, y in fr["pixels"]:
                fm[y, x] = True
            FRONT[form].append((fr["part"], fr["over"], fm & (parts[fr["part"]][0][..., 3] > 0)))
    extra = {}
    for name, info in spec.get("sprites", {}).items():
        s = np.asarray(Image.open(lp(os.path.join(RIG, f"{form}_{name}.png"))).convert("RGBA")).copy()
        s[s[..., 3] < 128] = 0
        s[s[..., 3] > 0, 3] = 255
        extra[name] = (s, tuple(info["joint"]))
    return parts, spec["order"], extra


def crop_sprite(img, joint):
    ys, xs = np.nonzero(img[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return img[y0:y1, x0:x1].copy(), (joint[0] - x0, joint[1] - y0)


def op(s, j, o):
    """One transform of a sprite about its joint j: (sprite, joint)."""
    jx, jy = j
    kind = o[0]
    if kind == "deg":
        if o[1] % 360 == 0:
            return s, j
        return K.rotsprite(s, j, o[1])
    if kind == "rot":
        h, w = s.shape[:2]
        for _ in range(o[1] % 4):
            s = np.rot90(s)
            jx, jy = jy, w - 1 - jx
            h, w = w, h
        return s.copy(), (jx, jy)
    if kind == "flip":
        return s[:, ::-1].copy(), (s.shape[1] - 1 - jx, jy)
    if kind == "shear":
        h, w = s.shape[:2]
        sh = [int(round(o[1] * (jy - y))) for y in range(h)]
        lo, hi = min(sh + [0]), max(sh + [0])
        out = np.zeros((h, w + hi - lo, 4), np.uint8)
        for y in range(h):
            out[y, sh[y] - lo:sh[y] - lo + w] = s[y]
        return out, (jx - lo, jy)
    raise ValueError(o)


def render(form, fs, pivot, parts_cache=None):
    """One posed frame (96 x 128 RGBA) for frame spec fs with the design's pivot on `pivot` (cell x, y)."""
    parts, order, extra = parts_cache or load_parts(form)
    order = fs.get("order", order)
    dx0, dy0 = pivot[0] - PIVOT[0], pivot[1] - PIVOT[1]
    mx, my = fs.get("move", [0, 0])
    big = np.zeros((96 + 64, 128 + 64, 4), np.uint8)       # room round the cell for the lean
    P = 32
    drawn, pending = set(), {}      # front pixels (json "front") wait for the part they sit over
    for name in order:
        if name not in parts and not any(o[0] == "sprite" for o in fs.get("parts", {}).get(name, [])):
            continue
        if fs.get("hide") and name in fs["hide"]:
            continue
        ops = fs.get("parts", {}).get(name, [])
        if name in parts:
            img, joint = parts[name]
        else:
            img, joint = None, None
        s, j = (crop_sprite(img, joint) if img is not None else (None, None))
        canvas_joint = parts[name][1] if name in parts else None
        for o in ops:
            if o[0] == "sprite":
                s, j = extra[o[1]]
                s = s.copy()
                if canvas_joint is None:
                    canvas_joint = tuple(o[2]) if len(o) > 2 else PIVOT
        place_x = canvas_joint[0] + dx0 + mx
        place_y = canvas_joint[1] + dy0 + my
        fronts = []
        if img is not None and not any(o[0] == "sprite" for o in ops):
            for fpart, fover, fm in FRONT.get(form, []):
                if fpart == name and fover not in drawn:
                    k = img.copy()
                    k[(k[..., 3] > 0) & ~fm, :3] = FRONT_KEY
                    fronts.append([fover] + list(crop_sprite(k, joint)))
        for o in ops:
            if o[0] == "sprite":
                continue
            if o[0] == "at":
                place_x += o[1]
                place_y += o[2]
                continue
            s, j = op(s, j, o)
            for f in fronts:
                f[1], f[2] = op(f[1], f[2], o)
        _stamp_big(big, s, j, place_x, place_y, P)
        drawn.add(name)
        for fover, k, kj in fronts:
            # the front pixels' place in the transformed part: not the stand-in colour; colours from the part itself
            fm = (k[..., 3] > 0) & (k[..., :3] != np.array(FRONT_KEY, np.uint8)).any(-1)
            if fm.any():
                pending.setdefault(fover, []).append((s, j, place_x, place_y, fm))
        for s2, j2, px2, py2, fm in pending.pop(name, []):
            f = np.zeros_like(s2)
            hh, ww = min(s2.shape[0], fm.shape[0]), min(s2.shape[1], fm.shape[1])
            sel = np.zeros(s2.shape[:2], bool)
            sel[:hh, :ww] = fm[:hh, :ww]
            f[sel] = s2[sel]
            _stamp_big(big, f, j2, px2, py2, P)
    lean = fs.get("lean", 0)
    if lean:
        out = np.zeros_like(big)
        py = pivot[1] + P
        for y in range(big.shape[0]):
            sh = int(round(lean * (py - y)))
            row = big[y]
            if sh > 0:
                out[y, sh:] = row[:-sh]
            elif sh < 0:
                out[y, :sh] = row[-sh:]
            else:
                out[y] = row
        big = out
    frame = big[P:P + 96, P:P + 128].copy()
    for b in fs.get("bridges", []):
        draw_bridge(frame, b)
    for x, y, h in fs.get("paint", []):
        frame[y, x, :3] = hexrgb(h)
        frame[y, x, 3] = 255
    for x, y in fs.get("erase", []):
        frame[y, x] = 0
    frame[FEET_ROW + 1:] = 0
    return frame


def _stamp_big(big, s, j, place_x, place_y, P):
    m = s[..., 3] > 0
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        yy, xx = int(y - j[1] + place_y) + P, int(x - j[0] + place_x) + P
        if 0 <= yy < big.shape[0] and 0 <= xx < big.shape[1]:
            big[yy, xx] = s[y, x]


def draw_bridge(frame, b):
    """A limb segment from b['from'] to b['to'] (cell x, y): `width` px of colour with the outline round it."""
    col = hexrgb(b.get("colour", "#FEBF91"))
    w = b.get("width", 2)
    core = np.zeros(frame.shape[:2], np.uint8)
    tmp = np.zeros_like(frame)
    K.line(tmp, tuple(b["from"]), tuple(b["to"]), col, width=w)
    core = tmp[..., 3] > 0
    ring = np.zeros_like(core)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ring |= np.roll(np.roll(core, dy, 0), dx, 1)
    ring &= ~core
    keep = frame[..., 3] > 0
    frame[ring & ~keep, :3] = OUTLINE
    frame[ring & ~keep, 3] = 255
    frame[core, :3] = col
    frame[core, 3] = 255


def parts_preview(form, out):
    parts, order, extra = load_parts(form)
    d = design(form)
    ys, xs = np.nonzero(d[..., 3] > 0)
    y0, y1, x0, x1 = ys.min() - 3, ys.max() + 4, xs.min() - 3, xs.max() + 4
    z = 12
    tiles = []
    rng = np.random.RandomState(3)
    tint = np.zeros_like(d)
    for name in order:
        if name not in parts:
            continue
        img, joint = parts[name]
        c = rng.randint(60, 255, 3)
        m = img[..., 3] > 0
        tint[m, :3] = (img[m, :3] * 0.45 + c * 0.55).astype(np.uint8)
        tint[m, 3] = 255
    for pic, label in ((d, f"{form} design"), (tint, "parts (tinted), joints = white crosses")):
        c = pic[y0:y1, x0:x1]
        im = Image.new("RGB", (c.shape[1] * z, c.shape[0] * z + 20), K.OLIVE)
        t = Image.fromarray(np.ascontiguousarray(c)).resize((c.shape[1] * z, c.shape[0] * z), Image.NEAREST)
        im.paste(t, (0, 20), t)
        dr = ImageDraw.Draw(im)
        dr.text((4, 2), label, fill=(0, 0, 0), font=K.font(14))
        if pic is tint:
            for name, (img, (jx, jy)) in parts.items():
                cx, cy = (jx - x0) * z + z // 2, (jy - y0) * z + z // 2 + 20
                dr.line([(cx - 8, cy), (cx + 8, cy)], fill=(255, 255, 255), width=2)
                dr.line([(cx, cy - 8), (cx, cy + 8)], fill=(255, 255, 255), width=2)
                dr.text((cx + 6, cy - 16), name, fill=(255, 255, 255), font=K.font(12))
        tiles.append(im)
    un = [n for n in DESIGN_FILE if n]
    K._row(tiles).save(out)
    print(out, "parts:", ", ".join(f"{n}({int((parts[n][0][..., 3] > 0).sum())})" for n in order if n in parts))


def load_pose(path):
    with open(lp(path), encoding="utf-8") as f:
        return json.load(f)


def pose_frames(pose):
    tag = pose["tag"]
    form = K.form_of(tag)
    cache = load_parts(form)
    cur = K.load(tag, "work")
    out = []
    for k, fs in enumerate(pose["frames"]):
        if fs.get("keep", False):
            out.append(cur[k])
        else:
            out.append(render(form, fs, K.pivot(tag, k), cache))
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("parts")
    p.add_argument("form")
    p.add_argument("--out")
    p = sub.add_parser("pose")
    p.add_argument("posefile")
    p.add_argument("--frame", type=int)
    p.add_argument("--out")
    p.add_argument("--z", type=int, default=6)
    p = sub.add_parser("apply")
    p.add_argument("posefile")
    a = ap.parse_args()
    if a.cmd == "parts":
        parts_preview(a.form, a.out or os.path.join(K.VIEWS, f"rig_parts_{a.form}.png"))
    elif a.cmd == "pose":
        pose = load_pose(a.posefile)
        frames = pose_frames(pose)
        tag = pose["tag"]
        ks = [a.frame - 1] if a.frame else range(len(frames))
        sel = [K.outlined(frames[k]) for k in ks]
        y0, y1, x0, x1 = K._crop_box(sel)
        tiles = [K._tile(K.outlined(frames[k])[y0:y1, x0:x1], a.z, label=f"{tag} {k + 1} posed (crop x0={x0} y0={y0})")
                 for k in ks]
        out = a.out or os.path.join(K.VIEWS, f"rig_pose_{tag}.png")
        K._col([K._row(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]).save(out)
        print(out)
    elif a.cmd == "apply":
        pose = load_pose(a.posefile)
        K.save(pose["tag"], pose_frames(pose))
        print("saved", pose["tag"])


if __name__ == "__main__":
    main()
