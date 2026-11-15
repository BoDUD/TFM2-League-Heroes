#!/usr/bin/env python3
"""Port a champion's League spell VFX into its effect sheet as League draws them - true colour, not pixel art - sized
and timed by our kit (tools/lol/vfx_port_<champ>.json says how, tag by tag).

    python -I tools/lol/vfx_port.py tools/lol/vfx_port_caitlyn.json --review C:/t/par_work/caitlyn_vfx [--tags hit bolt]
    python -I tools/lol/vfx_port.py tools/lol/vfx_port_caitlyn.json --write          # into league/effects/<sheet>

The frames are drawn from Riot's art (the systems of the local client, tools/lol/vfx_render.py): a sheet written by
--write may go into a LOCAL build only - never commit it to a branch that is pushed (the port's own branch says so).

Per tag the spec gives the systems played (a scene of vfx_render), the camera (s: game px per League unit, chosen from
our kit - a line's width, an area's radius, a projectile's range - or at sprite scale for hits on a unit), where the
anchor is, and the timeline: each frame's time in the scene and how long it shows. A frame is rendered at PPU 2 (the
hd_ twin, 2 texels a game px) supersampled 4x, motion blurred over the time it shows, then:
  - light and matter apart: additive particles add up as light, alpha-blended ones as matter (vfx_render's canvas on
    transparency);
  - bloom: the light plus a blur of itself (`bloom`: [sigma in hd px, weight]) - the soft halo League's glow textures
    give on its dark ground, which our bright grass would wash out - and an exposure `gain`; light past 1 bleeds into
    white (hot cores);
  - straight alpha: light becomes a layer of its own colour at full brightness with alpha = its strength (exact on
    black, on any ground the light's colour over it), over the matter; alpha under `floor` fades out (no faint wash
    over a big box);
  - a projectile's trail ends in a fade `tail_px` behind its head (League's trails outlast our short flights);
  - every frame is cropped round the anchor (odd 1x sizes, the hd_ twin exactly twice: PPU 2), the 1x frame is the hd
    one averaged 2x2.
Projectiles are drawn from above (pitch 90) flying right with the head on the anchor (the engine turns the picture to
the flight); points at our camera (pitch 35) with the ground `ground_px` under the anchor (a unit's soles 11.5 px under
its pivot) and `at` placing the system (game px from the anchor: a hit on the upper body is (0, -8)).

--review writes, per tag, <tag>.gif: lanes at 4x (each texel of the hd_ frame 2 screen px) - ours now | ported on the
map's grounds | League's own render (exact blending on League's dark ground) - and <tag>.png: every frame at 1x and
4x on each ground; report.json with sizes and texels.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import vfx_render as R  # noqa: E402

PPU = 2                                   # hd_ texels a game px
SS = 4                                    # supersampling of the hd_ frame
TICK = 1000.0 / 60
# grounds to judge on: the map's grass (an in-game crop's commonest colour and the arena's), its dirt (the 5v5
# background's), a river blue (no map art in the repo: an estimate), League's own dark ground for its reference lane
GROUNDS = {"grass": (110, 140, 85), "grass2": (86, 125, 62), "dirt": (92, 91, 57), "river": (62, 98, 112)}
LEAGUE_GROUND = (40, 48, 38)
Z = 4                                     # review zoom: game px x 4


# ----------------------------------------------------------------------------- spec
def load_spec(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def timeline(t):
    """[(scene ms or None, ms, shutter ms)] of a tag: `frames` as given (each blurred over its own time, at most
    100 ms, or `shutter_ms`), or a projectile's lead-in / flight frames / loop / hold (blurred over a step)."""
    if "frames" in t:
        return [(None if a is None else float(a), float(b), float(t.get("shutter_ms", min(float(b), 100.0))))
                for a, b in t["frames"]]
    out = []
    if t.get("lead_ms"):
        out.append((None, float(t["lead_ms"]), 0.0))
    step, n = float(t["step_ms"]), int(t["count"])
    for k in range(n):
        out.append((k * step, step, step))
    if t.get("loop"):                     # [first, last] frame indices looped after the flight frames, to fill loop_ms
        a, b = t["loop"]
        k, filled = 0, 0.0
        seq = list(range(a, b + 1))
        while filled < float(t.get("loop_ms", 0)):
            idx = seq[k % len(seq)]
            out.append((idx * step, step, step))
            filled += step
            k += 1
    if t.get("hold_ms"):
        out[-1] = (out[-1][0], float(t["hold_ms"]), out[-1][2])
    return out


def scene_of(champ, t):
    """the vfx_render scene of a tag: its plays placed (`at`), a projectile's velocity from our speed, the camera."""
    cam = dict(t["camera"])
    s = float(cam["s"])
    proj = t.get("kind") == "projectile"
    cam.setdefault("pitch", 90.0 if proj else 35.0)
    cam.setdefault("ground_px", 0.0 if proj else 11.5)
    size = cam.get("size", [96, 64])
    cam["size"] = size
    cam["center"] = [size[0] // 2 + 0.5, size[1] // 2 + 0.5]
    cp = math.cos(math.radians(cam["pitch"]))
    plays = []
    for p in t["plays"]:
        p = dict(p)
        ax, ay = p.pop("at", t.get("at", (0.0, 0.0)))
        height = p.pop("height", None)
        lift = float(p.pop("lift", 0.0))          # League units added to the origin's height (a symbol drawn 250 up)
        if proj:
            p.setdefault("frame", "missile")
            if not t.get("tile_px"):                         # a stream's tile stands still: the beam through it
                v = float(t["speed"]) * 60.0 / s               # px a tick -> League units a second at this scale
                p["velocity"] = [v, 0.0, 0.0]
            p["origin"] = [ax / s, 100.0 if height is None else height, -ay / s]
        else:
            # a point: the system's ground under the anchor at `at` (x, y px), lifted to put its origin there
            y = height if height is not None else ((cam["ground_px"] - ay) / (cp * s) if cp > 1e-6 else 0.0)
            p.setdefault("origin", [ax / s, y + lift, 0.0])
        if "target_px" in p:
            tx, ty = p.pop("target_px")
            p["target"] = [tx / s, p["origin"][1], 0.0]
        plays.append(p)
    sc = {"champ": champ, "camera": cam, "plays": plays}
    if proj and not t.get("tile_px"):
        sc["follow"] = 0
    if t.get("warp"):
        sc["warp"] = t["warp"]
    return sc


# ----------------------------------------------------------------------------- frames
def _down(a, k):
    H, W = a.shape[:2]
    return a[:H // k * k, :W // k * k].reshape(H // k, k, W // k, k, *a.shape[2:]).mean((1, 3))


def blur(img, sigma):
    """a separable gaussian blur of (H, W, C) with zeros outside."""
    r = int(math.ceil(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    pad = np.pad(img, ((r, r), (r, r), (0, 0)))
    tmp = sum(k[i] * pad[:, i:i + img.shape[1] + 0] for i in range(2 * r + 1))[r:r + img.shape[0]]
    pad2 = np.pad(tmp, ((r, r), (0, 0), (0, 0)))
    return sum(k[i] * pad2[i:i + img.shape[0]] for i in range(2 * r + 1))


def finish(matter, light, bloom=(2.0, 0.3), gain=1.1, hot=0.2, floor=0.03, matter_gain=1.0):
    """(matter premultiplied RGBA, light RGB) at hd size -> straight RGBA float."""
    if matter_gain != 1.0:
        # alpha-blended parts made denser (League's grey net pieces, drawn for its dark ground, on our bright grass)
        a = np.clip(matter[..., 3:4], 0, 1)
        a2 = 1.0 - (1.0 - a) ** matter_gain
        matter = matter * np.where(a > 1e-6, a2 / np.maximum(a, 1e-6), 0.0)
    L = light * gain
    sig, w = bloom
    if w > 0 and sig > 0:
        L = L + w * blur(L, sig)
    ex = np.maximum(L.max(-1) - 1.0, 0.0)[..., None]
    L = np.clip(L + hot * ex, 0.0, None)
    aL = np.clip(L.max(-1), 0.0, 1.0)
    CL = np.clip(L / np.maximum(aL[..., None], 1e-6), 0.0, 1.0)
    pre = CL * aL[..., None] + matter[..., :3] * (1.0 - aL[..., None])
    a = aL + np.clip(matter[..., 3], 0, 1) * (1.0 - aL)
    rgb = np.where(a[..., None] > 1e-6, pre / np.maximum(a[..., None], 1e-6), 0.0)
    if floor > 0:
        k = np.clip((a - floor) / floor, 0.0, 1.0)
        a = a * k * k * (3 - 2 * k)
    return np.concatenate([np.clip(rgb, 0, 1), np.clip(a, 0, 1)[..., None]], -1)


def tail_fade(img, tail_px, centre_x):
    """a projectile frame: alpha faded to 0 over the last 40% of `tail_px` (game px) behind the head."""
    W = img.shape[1]
    x = (np.arange(W) + 0.5) / PPU - centre_x                  # game px from the head, negative behind
    k = np.clip((x + tail_px) / (0.4 * tail_px), 0, 1)
    k = k * k * (3 - 2 * k)
    out = img.copy()
    out[..., 3] *= k[None, :]
    return out


def to_u8(a):
    out = (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return out


def half(hd):
    """the 1x frame: the hd_ one averaged 2x2 (premultiplied)."""
    pre = hd.astype(np.float64) / 255.0
    pre[..., :3] *= pre[..., 3:4]
    d = _down(pre, PPU)
    a = d[..., 3:4]
    rgb = np.where(a > 1e-6, d[..., :3] / np.maximum(a, 1e-6), 0)
    return to_u8(np.concatenate([rgb, a], -1))


def crop_frames(hds, centre, min_half=(0, 0)):
    """crop hd_ frames (uint8, the anchor at game px `centre` of the canvas) round the anchor: per frame the smallest
    odd 1x box holding every texel (alpha > 0), the hd_ twin twice it -> [(hd, 1x)]."""
    cx, cy = int(math.floor(centre[0])), int(math.floor(centre[1]))   # the 1x pixel holding the anchor
    out = []
    for hq in hds:
        m = hq[..., 3] > 0
        if m.any():
            ys, xs = np.nonzero(m)
            ex = max(cx - xs.min() // PPU, xs.max() // PPU - cx)
            ey = max(cy - ys.min() // PPU, ys.max() // PPU - cy)
        else:
            ex = ey = 0
        ex, ey = max(ex, min_half[0]), max(ey, min_half[1])
        x0, y0 = cx - ex, cy - ey
        w, h = 2 * ex + 1, 2 * ey + 1
        c = np.zeros((h * PPU, w * PPU, 4), np.uint8)
        H, W = hq.shape[:2]
        sx0, sy0 = max(x0 * PPU, 0), max(y0 * PPU, 0)
        sx1, sy1 = min((x0 + w) * PPU, W), min((y0 + h) * PPU, H)
        c[sy0 - y0 * PPU:sy1 - y0 * PPU, sx0 - x0 * PPU:sx1 - x0 * PPU] = hq[sy0:sy1, sx0:sx1]
        if not m.any():
            c = np.zeros((PPU, PPU, 4), np.uint8)
        out.append((c, half(c)))
    return out


def edge_report(hq):
    """the strongest alpha on the frame's outermost texels (a clipped picture shows here)."""
    a = hq[..., 3]
    return int(max(a[0].max(), a[-1].max(), a[:, 0].max(), a[:, -1].max())) if a.size else 0


def render_tag(champ, name, t, vfxs, reference=False):
    """-> [(hd straight RGBA float or None, ms)] at the canvas size; with `reference` League's own look on its ground
    (exact blending, no bloom) instead."""
    sc = scene_of(champ, t)
    plan = timeline(t)
    t0 = float(t.get("t0_ms", 0.0))                       # the scene's time at the tag's start (a steady state)
    # one render per distinct (time, shutter): a loop's repeats share theirs
    keys = sorted(dict.fromkeys((a, sh) for a, _, sh in plan if a is not None))   # in time: the sim runs forward
    intervals = [((t0 + a) / 1000.0, (t0 + a + sh) / 1000.0) for a, sh in keys]
    if reference:
        frames = R.scene_frames(sc, intervals, bg=LEAGUE_GROUND, ppx=PPU * SS, vfxs=vfxs)
        imgs = [_down(f, SS) for f in frames]
    else:
        lay = R.scene_frames(sc, intervals, ppx=PPU * SS, vfxs=vfxs, layers=True)
        fin = t.get("finish", {})
        imgs = [finish(_down(m, SS), _down(L, SS), bloom=tuple(fin.get("bloom", (2.0, 0.3))),
                       gain=fin.get("gain", 1.1), hot=fin.get("hot", 0.2), floor=fin.get("floor", 0.03),
                       matter_gain=fin.get("matter_gain", 1.0))
                for m, L in lay]
        if t.get("tail_px"):
            imgs = [tail_fade(im, float(t["tail_px"]), sc["camera"]["center"][0]) for im in imgs]
        if t.get("top_px"):
            # a tall light (the trap's drop beam) fades out over the last third below top_px game px over the anchor
            H = imgs[0].shape[0]
            y = sc["camera"]["center"][1] - (np.arange(H) + 0.5) / PPU          # game px above the anchor
            top = float(t["top_px"])
            k = np.clip((top - y) / (top / 3.0), 0, 1)
            k = (k * k * (3 - 2 * k)).astype(np.float32)
            imgs = [np.concatenate([im[..., :3], im[..., 3:4] * k[:, None, None]], -1) for im in imgs]
        if t.get("tile_px"):
            # a stream's tile: the picture cut to tile_px along the flight round the anchor (the next projectile's
            # tile follows on, one tick of flight later)
            W = imgs[0].shape[1]
            x = (np.arange(W) + 0.5) / PPU - sc["camera"]["center"][0]
            keep = (np.abs(x) <= float(t["tile_px"]) / 2).astype(np.float32)
            imgs = [np.concatenate([im[..., :3], im[..., 3:4] * keep[None, :, None]], -1) for im in imgs]
    if t.get("fade"):                                     # per shown frame: its alpha times this (a fading trap)
        fades = iter(t["fade"])
    out = []
    for a, ms, sh in plan:
        if a is None:
            out.append((None, ms))
            continue
        im = imgs[keys.index((a, sh))]
        if t.get("fade"):
            f = float(next(fades))
            im = np.concatenate([im[..., :3], im[..., 3:4] * f], -1)
        out.append((im, ms))
    return out, sc


def port_tag(champ, name, t, vfxs):
    """-> {"hd": [(uint8, ms)], "one": [(uint8, ms)], "edges": [...]} for tag `name`."""
    frames, sc = render_tag(champ, name, t, vfxs)
    centre = sc["camera"]["center"]
    shown = [to_u8(f) for f, _ in frames if f is not None]
    cropped = iter(crop_frames(shown, centre, tuple(t.get("min_half", (0, 0)))))
    hd, one, edges = [], [], []
    for f, ms in frames:
        if f is None:
            hd.append((np.zeros((PPU, PPU, 4), np.uint8), ms))
            one.append((np.zeros((1, 1, 4), np.uint8), ms))
        else:
            h, o = next(cropped)
            hd.append((h, ms))
            one.append((o, ms))
            edges.append(edge_report(h))
    canvas_edges = [edge_report(to_u8(f)) for f, _ in frames if f is not None]
    return {"hd": hd, "one": one, "edges": edges, "canvas_edges": canvas_edges}


# ----------------------------------------------------------------------------- the sheet
def load_sheet(root, sheet):
    base = os.path.join(root, sheet)
    with open(base + "#anim.fanim", encoding="utf-8") as f:
        d = json.load(f)
    im = np.asarray(Image.open(base + "#sheet.png").convert("RGBA"))
    tags = {}
    for tag, a in d["anims"].items():
        fr = []
        for f in a["frames"]:
            r = f["data"]
            x, y, w, h = int(r["x"]), int(r["y"]), int(r["w"]), int(r["h"])
            fr.append((im[y:y + h, x:x + w].copy(), round(float(f["duration"]) * 1000.0, 3)))
        tags[tag] = fr
    return tags, im.shape[1] * im.shape[0]


def pack(tags, max_w=2048):
    """shelf-pack every distinct frame (tallest first) -> (sheet uint8, {tag: [(x, y, w, h, ms)]}); the narrowest width
    up to max_w whose area is smallest."""
    uniq, keyof = [], {}
    for frames in tags.values():
        for arr, _ in frames:
            k = (arr.shape, arr.tobytes())
            if k not in keyof:
                keyof[k] = len(uniq)
                uniq.append(arr)
    order = sorted(range(len(uniq)), key=lambda i: (-uniq[i].shape[0], -uniq[i].shape[1]))
    widest = max(a.shape[1] for a in uniq)
    best = None
    for W in sorted({w for w in (256, 384, 512, 768, 1024, 1280, 1536, 1792, 2048) if widest <= w <= max_w}):
        x = y = shelf = 0
        pos = {}
        for i in order:
            h, w = uniq[i].shape[:2]
            if x and x + w > W:
                x, y, shelf = 0, y + shelf + 1, 0
            pos[i] = (x, y)
            x += w + 1
            shelf = max(shelf, h)
        used_w = max(pos[i][0] + uniq[i].shape[1] for i in pos)
        H = y + shelf
        if H > max_w and W < max_w:
            continue                      # no side over max_w
        if best is None or used_w * H < best[0]:
            best = (used_w * H, used_w, H, pos)
    _, W, H, pos = best
    sheet = np.zeros((H, W, 4), np.uint8)
    for i, (x, y) in pos.items():
        h, w = uniq[i].shape[:2]
        sheet[y:y + h, x:x + w] = uniq[i]
    rects = {}
    for tag, frames in tags.items():
        rects[tag] = []
        for arr, ms in frames:
            i = keyof[(arr.shape, arr.tobytes())]
            x, y = pos[i]
            rects[tag].append((x, y, arr.shape[1], arr.shape[0], ms))
    return sheet, rects


def write_sheet(root, sheet_name, tags):
    sheet, rects = pack(tags)
    base = os.path.join(root, sheet_name)
    Image.fromarray(sheet, "RGBA").save(base + "#sheet.png", optimize=True)
    anims = {tag: {"frames": [{"duration": round(ms / 1000.0, 6),
                               "data": {"x": float(x), "y": float(y), "w": float(w), "h": float(h)}}
                              for x, y, w, h, ms in r]} for tag, r in rects.items()}
    with open(base + "#anim.fanim", "w", encoding="utf-8", newline="\n") as f:
        json.dump({"anims": anims}, f, ensure_ascii=False)          # the repo's fanims: one line, ", " / ": "
    return sheet.shape[1], sheet.shape[0]


# ----------------------------------------------------------------------------- review
def over(bg, img):
    """straight RGBA uint8 over an RGB colour -> RGB uint8."""
    a = img[..., 3:4].astype(np.float32) / 255.0
    return (img[..., :3] * a + np.asarray(bg, np.float32) * (1 - a) + 0.5).astype(np.uint8)


def _font_label(d, xy, text):
    d.text(xy, text, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))


def frame_at(frames, ms):
    """the frame showing at ms into a non-repeating animation (its last frame after the end)."""
    acc = 0.0
    for img, d in frames:
        if ms < acc + d:
            return img
        acc += d
    return frames[-1][0]


def outline_area(lane, t, proj, ms, lead, mw, lane_h):
    """the kit's hit area (white dots) on a lane at Z: a line's edges (+-radius about the flight) for a projectile, a
    ground ellipse (pitch 35: 0.57 as tall) round the soles' point for a point effect."""
    r = float(t["hit_area"]["radius_px"]) * Z
    H, W = lane.shape[:2]
    cy = lane_h // 2
    if proj:
        for y in (int(round(cy - r)), int(round(cy + r))):
            if 0 <= y < H:
                lane[y, ::6] = 255
        return
    gy = cy + float(t.get("camera", {}).get("ground_px", 11.5)) * Z
    for a in np.linspace(0, 2 * math.pi, 180, endpoint=False):
        x, y = int(round(W // 2 + r * math.cos(a))), int(round(gy + 0.574 * r * math.sin(a)))
        if 0 <= x < W and 0 <= y < H:
            lane[y, x] = 255


def review_tag(out_dir, name, t, ported, ours_hd, reference, sc):
    """<name>.gif (lanes at Z: ours now | ported on each ground | League) and <name>.png (each frame 1x and 4x)."""
    os.makedirs(out_dir, exist_ok=True)
    proj = t.get("kind") == "projectile"
    total = sum(ms for _, ms in ported["hd"])
    total = min(total, float(t.get("review_ms", 1200)))
    lanes = [("ours now", ours_hd, GROUNDS["grass"])]
    for g in t.get("grounds", ["grass", "dirt", "river"]):
        lanes.append((f"ported on {g}", ported["hd"], GROUNDS[g]))
    area = t.get("hit_area")              # {"radius_px": r}: the kit's hit area drawn over a grass lane
    ref = [(None if f is None else to_u8(f), ms) for f, ms in reference]
    lanes.append(("League", ref, LEAGUE_GROUND))
    # lane size: the biggest frame (hd) of any lane, plus the flight for projectiles
    flight = float(t.get("speed", 0)) * float(t.get("review_flight_ticks", 0)) if proj else 0.0
    mw = max((f.shape[1] for _, fr, _ in lanes for f, _ in fr if f is not None), default=2)
    mh = max((f.shape[0] for _, fr, _ in lanes for f, _ in fr if f is not None), default=2)
    lane_w = int(mw * Z / PPU + flight * Z) + 16
    lane_h = int(mh * Z / PPU) + 16
    step = TICK
    gif = []
    n = int(math.ceil(total / step))
    lead = float(t.get("lead_ms", 0)) if proj else 0.0
    stream = t.get("stream")              # {"ticks": n, "target_px": d}: one projectile a tick (R's laser sight)
    if stream:
        lane_w = int(float(stream["target_px"]) * Z) + 32
        n = int(stream["ticks"]) + int(float(stream["target_px"]) / float(t["speed"])) + 10

    def put(lane, f, cx, cy):
        big = np.repeat(np.repeat(f, Z // PPU, 0), Z // PPU, 1)
        x0, y0b = cx - big.shape[1] // 2, cy - big.shape[0] // 2
        xa, ya = max(x0, 0), max(y0b, 0)
        xb, yb = min(x0 + big.shape[1], lane.shape[1]), min(y0b + big.shape[0], lane.shape[0])
        if xb > xa and yb > ya:
            lane[ya:yb, xa:xb] = over(lane[ya:yb, xa:xb], big[ya - y0b:yb - y0b, xa - x0:xb - x0])

    for k in range(n):
        ms = k * step
        img = Image.new("RGB", (lane_w, (lane_h + 14) * len(lanes)), (0, 0, 0))
        d = ImageDraw.Draw(img)
        for li, (label, fr, bg) in enumerate(lanes):
            y0 = li * (lane_h + 14) + 14
            lane = np.zeros((lane_h, lane_w, 3), np.uint8) + np.asarray(bg, np.uint8)
            if stream:
                for j in range(min(k + 1, int(stream["ticks"]))):
                    dist = (k - j) * float(t["speed"])
                    f = frame_at(fr, (k - j) * step)
                    if dist < float(stream["target_px"]) and f is not None and f.shape[0] > PPU:
                        put(lane, f, 16 + int(round(dist * Z)), lane_h // 2)
            else:
                f = frame_at(fr, ms)
                if f is not None and f.shape[0] > PPU:
                    cx = lane_w // 2 if not proj else int(mw * Z / PPU / 2 + 8 + max(0.0, ms - lead) / TICK * float(
                        t.get("speed", 0)) * Z)
                    put(lane, f, cx, lane_h // 2)
            if area and li == 1:
                outline_area(lane, t, proj, ms, lead, mw, lane_h)
            img.paste(Image.fromarray(lane), (0, y0))
            _font_label(d, (4, y0 - 13), label + (" + hit area" if area and li == 1 else ""))
        _font_label(d, (lane_w - 60, 1), f"{ms:5.0f} ms")
        gif.append(img)
    gif[0].save(os.path.join(out_dir, f"{name}.gif"), save_all=True, append_images=gif[1:],
                duration=[int(round(step))] * len(gif), loop=0, disposal=1)
    # a still to read the lanes from: rows every `lanes_every` ticks, the lanes side by side
    every = int(t.get("lanes_every", 2))
    picks = gif[::every][:int(t.get("lanes_max", 12))]
    nl = len(lanes)
    lh = lane_h + 14
    grid = Image.new("RGB", ((lane_w + 4) * nl, len(picks) * (lh + 2)), (0, 0, 0))
    for r, g in enumerate(picks):
        for li in range(nl):
            cell = g.crop((0, li * lh, lane_w, (li + 1) * lh))
            grid.paste(cell, (li * (lane_w + 4), r * (lh + 2)))
    grid.save(os.path.join(out_dir, f"{name}_lanes.png"))
    # contact sheet: every ported frame at 1x (the 1x frame) and at 4x (the hd_ frame x2), on each ground
    rows = []
    for g in t.get("grounds", ["grass", "dirt", "river"]):
        bg = GROUNDS[g]
        cells = []
        for (h, ms), (o, _) in zip(ported["hd"], ported["one"]):
            if h.shape[0] <= PPU:
                continue
            big = Image.fromarray(over(bg, np.repeat(np.repeat(h, Z // PPU, 0), Z // PPU, 1)))
            small = Image.fromarray(over(bg, o))
            cells.append((big, small, ms))
        if cells:
            W = sum(c[0].width + 6 for c in cells) + 6
            H = max(c[0].height for c in cells) + max(c[1].height for c in cells) + 30
            row = Image.new("RGB", (W, H), bg)
            d = ImageDraw.Draw(row)
            x = 6
            for big, small, ms in cells:
                row.paste(small, (x, 14))
                row.paste(big, (x, 20 + small.height))
                _font_label(d, (x, 1), f"{ms:.0f}")
                x += big.width + 6
            rows.append(row)
    if rows:
        W = max(r.width for r in rows)
        sheet = Image.new("RGB", (W, sum(r.height + 4 for r in rows)), (0, 0, 0))
        y = 0
        for r in rows:
            sheet.paste(r, (0, y))
            y += r.height + 4
        sheet.save(os.path.join(out_dir, f"{name}.png"))


def review_sequence(out_dir, name, seq, ours, new):
    """<name>.gif: a skill's pictures as the kit plays them one after another (`seq`: events of tags at times and
    places, projectiles flying), lanes ours now | ported on each ground; ours / new: {tag: [(hd frame, ms)]}."""
    total = float(seq["ms"])
    width = float(seq.get("width_px", 220))
    lanes = [("ours now", ours, GROUNDS["grass"])] + [(f"ported on {g}", new, GROUNDS[g])
                                                     for g in seq.get("grounds", ["grass", "dirt"])]
    tall = max((f.shape[0] for tg in (ours, new) for ev in seq["events"] for f, _ in tg.get("hd_" + ev["tag"], [])),
               default=2)
    lane_w, lane_h = int(width * Z) + 64, int(tall * Z / PPU) + 16
    cy = lane_h // 2

    def put(lane, f, cx):
        big = np.repeat(np.repeat(f, Z // PPU, 0), Z // PPU, 1)
        x0, y0 = int(cx) - big.shape[1] // 2, cy - big.shape[0] // 2
        xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + big.shape[1], lane_w), min(y0 + big.shape[0], lane_h)
        if xb > xa and yb > ya:
            lane[ya:yb, xa:xb] = over(lane[ya:yb, xa:xb], big[ya - y0:yb - y0, xa - x0:xb - x0])

    events = []
    for ev in seq["events"]:
        starts = [float(ev["t"])]
        if ev.get("every"):
            starts = list(np.arange(float(ev["t"]), float(ev["until"]), float(ev["every"])))
        if ev.get("stream"):                      # one projectile a tick for `stream` ticks
            starts = [float(ev["t"]) + k * TICK for k in range(int(ev["stream"]))]
        events += [(st, ev) for st in starts]
    gif = []
    for k in range(int(math.ceil(total / TICK))):
        ms = k * TICK
        img = Image.new("RGB", (lane_w, (lane_h + 14) * len(lanes)), (0, 0, 0))
        d = ImageDraw.Draw(img)
        for li, (label, tg, bg) in enumerate(lanes):
            lane = np.zeros((lane_h, lane_w, 3), np.uint8) + np.asarray(bg, np.uint8)
            for st, ev in events:
                fr = tg.get("hd_" + ev["tag"])
                if not fr or ms < st:
                    continue
                age = ms - st
                if "x1" in ev:                    # a projectile: flies until it reaches x1
                    x = float(ev["x0"]) + age / TICK * float(ev["speed"])
                    if x >= float(ev["x1"]):
                        continue
                else:
                    x = float(ev["x"])
                    if age >= sum(m for _, m in fr) and not ev.get("hold"):
                        continue
                f = frame_at(fr, age)
                if f is not None and f.shape[0] > PPU:
                    put(lane, f, 32 + x * Z)
            y0 = li * (lane_h + 14) + 14
            img.paste(Image.fromarray(lane), (0, y0))
            _font_label(d, (4, y0 - 13), label)
        _font_label(d, (lane_w - 60, 1), f"{ms:5.0f} ms")
        gif.append(img)
    gif[0].save(os.path.join(out_dir, f"{name}.gif"), save_all=True, append_images=gif[1:],
                duration=[int(round(TICK))] * len(gif), loop=0, disposal=1)
    picks = gif[::int(seq.get("lanes_every", 6))][:16]
    strip = Image.new("RGB", (picks[0].width, sum(g.height + 4 for g in picks)), (0, 0, 0))
    y = 0
    for g in picks:
        strip.paste(g, (0, y))
        y += g.height + 4
    strip.save(os.path.join(out_dir, f"{name}_lanes.png"))


# ----------------------------------------------------------------------------- main
def texels(frames):
    return sum(int(f.shape[0] * f.shape[1]) for f, _ in frames)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--root", default=ROOT, help="the repository whose league/effects sheet is read (and written)")
    ap.add_argument("--tags", nargs="*", help="only these tags")
    ap.add_argument("--review", help="write review GIFs / PNGs here (LOCAL: drawn from Riot's art)")
    ap.add_argument("--write", action="store_true", help="write the sheet with the ported tags into --root")
    ap.add_argument("--no-reference", action="store_true", help="review without League's own lane (faster)")
    ap.add_argument("--ours", help="a repository holding the sheet as it was (the review's 'ours now' lanes and the "
                                   "texels before; default --root)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    spec = load_spec(a.spec)
    champ, sheet_name = spec["champ"], spec["sheet"]
    tags, _ = load_sheet(a.root, sheet_name)
    old, texels_before = load_sheet(a.ours or a.root, sheet_name)
    vfxs = {champ: R.Vfx(champ)}
    names = [n for n in spec["tags"] if not a.tags or n in a.tags]
    report = {}
    for name in names:
        t = spec["tags"][name]
        ported = port_tag(champ, name, t, vfxs)
        before = texels(old.get(name, [])) + texels(old.get("hd_" + name, []))
        tags[name] = ported["one"]
        tags["hd_" + name] = ported["hd"]
        after = texels(ported["one"]) + texels(ported["hd"])
        sizes = sorted({(f.shape[1], f.shape[0]) for f, _ in ported["one"] if f.shape[0] > 1})
        report[name] = {"frames": len(ported["one"]), "ms": round(sum(ms for _, ms in ported["one"]), 1),
                        "sizes_1x": sizes[:3] + (["..."] if len(sizes) > 3 else []) + sizes[-1:] * (len(sizes) > 3),
                        "texels_before": before, "texels_after": after,
                        "edge_alpha_max": max(ported["edges"], default=0),
                        "canvas_edge_alpha_max": max(ported["canvas_edges"], default=0)}
        print(f"{name}: {report[name]}")
        if a.review:
            ours = old.get("hd_" + name, [])
            ref = [] if a.no_reference else render_tag(champ, name, t, vfxs, reference=True)[0]
            sc = scene_of(champ, t)
            # League's lane: its canvas cut to the biggest ported frame round the anchor
            mw = max(f.shape[1] for f, _ in ported["hd"])
            mh = max(f.shape[0] for f, _ in ported["hd"])
            cx, cy = (int(math.floor(c)) * PPU + PPU // 2 for c in sc["camera"]["center"])
            ref = [(None if f is None else f[max(cy - mh // 2, 0):cy + mh // 2, max(cx - mw // 2, 0):cx + mw // 2], ms)
                   for f, ms in ref]
            review_tag(a.review, name, t, ported, ours, ref, sc)
    for tag in spec.get("prune", []):     # tags nothing plays (the kit's muzzles live in the hero's own sheet)
        tags.pop(tag, None)
        tags.pop("hd_" + tag, None)
    sheet_after = None
    if a.write:
        sheet_after = write_sheet(a.root, sheet_name, tags)
        print(f"wrote {sheet_name}: {sheet_after[0]}x{sheet_after[1]} = {sheet_after[0] * sheet_after[1]} texels "
              f"(before {texels_before})")
    else:
        sh, _ = pack(tags)
        sheet_after = (sh.shape[1], sh.shape[0])
        print(f"sheet would be {sheet_after[0]}x{sheet_after[1]} = {sheet_after[0] * sheet_after[1]} texels "
              f"(before {texels_before})")
    if a.review:
        for sname, seq in spec.get("sequences", {}).items():
            review_sequence(a.review, sname, seq, old, tags)
    if a.review:
        with open(os.path.join(a.review, "report.json"), "w", encoding="utf-8") as f:
            json.dump({"tags": report, "sheet_texels_before": texels_before,
                       "sheet_after": list(sheet_after)}, f, indent=1)


if __name__ == "__main__":
    main()
