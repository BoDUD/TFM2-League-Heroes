#!/usr/bin/env python3
"""League VFX -> our effect frames, per scene of tools/lol/vfx_scenes.json: render League's particle systems
(vfx_render.py), pixelate them (vfx_pixel.py) to the tag's frames, and compare.

    python -I tools/lol/vfx_pilot.py --out C:/t/par_work/vfx_pilot [--scenes lux_e_zone lux_r_beam ...]
        [--root <repo with league/effects>] [--oppi <oppi's workshop folder>] [--palette ours|own]

Writes under --out (LOCAL ONLY: everything there is drawn from Riot's art):
  <scene>/league_*.png    the League render frames (true colour, on grass) and the pixel frames (hd_ and 1x strips)
  <scene>.gif             lanes at game size x4 on grass: League (true colour, 30 fps) | pixel-art frames at PPU 2
                          (the tag's own timing) | ours now (the hd_ twin) | oppi's picture when his mod has one
  sheets/<sheet>#sheet.png + #anim.fanim   the sheet with the scene's tag (and its hd_ twin) replaced - a candidate,
                          never installed by this tool
  report.json             per tag: frames, sizes, texels now and new
Nothing is written into the repository.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import vfx_pixel as X  # noqa: E402
import vfx_render as R  # noqa: E402

GRASS = (86, 125, 62)
OPPI = r"D:\steam\steamapps\workshop\content\3009300\3774304166"
Z = 4                                     # display: game px x 4


def load_fanim(root, sheet):
    base = os.path.join(root, "league", "effects", sheet)
    d = json.load(open(base + "#anim.fanim", encoding="utf-8"))
    im = np.asarray(Image.open(base + "#sheet.png").convert("RGBA"))
    return d, im


def tag_frames(d, im, tag):
    out = []
    for f in d["anims"][tag]["frames"]:
        r = f["data"]
        x, y, w, h = int(r["x"]), int(r["y"]), int(r["w"]), int(r["h"])
        out.append((im[y:y + h, x:x + w].copy(), float(f["duration"])))
    return out


def oppi_frames(spec, oppi):
    """[(RGBA array, seconds)] of oppi's picture: {"path": "fx/luxskill.aseprite", "tag": "skill"}."""
    try:
        import tfm2_ase
    except ImportError:
        return None
    path = os.path.join(oppi, spec["path"])
    if not os.path.exists(path) and not os.path.exists(path + "#sheet.png"):
        return None
    sp = tfm2_ase.load_sprite(path)
    idx = sp.tag_frames(spec["tag"]) or list(range(len(sp.frames)))
    return [(np.asarray(sp.frames[i].convert("RGBA")), sp.durations[i] / 1000.0) for i in idx]


def over(bg, img):
    """straight RGBA uint8 over an RGB background block (same size) -> RGB uint8."""
    a = img[..., 3:4].astype(np.float64) / 255
    return (img[..., :3] * a + bg * (1 - a)).astype(np.uint8)


def shift(img, dx, dy):
    """move an image by whole pixels, the uncovered part grass (np.roll would wrap a trail round to the front)."""
    out = np.empty_like(img)
    out[..., :3] = GRASS
    if img.shape[-1] == 4:
        out[..., 3] = 255
    H, W = img.shape[:2]
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = img[ys, xs]
    return out


def frame_at(frames, t, loop=True):
    total = sum(d for _, d in frames)
    if total <= 0:
        return frames[0][0]
    t = t % total if loop else min(t, total - 1e-6)
    acc = 0.0
    for img, d in frames:
        acc += d
        if t < acc:
            return img
    return frames[-1][0]


def place(canvas, img, ax, ay, scale):
    """paste img (uint8 RGBA, its centre on the anchor) scaled `scale` x nearest onto canvas (RGB uint8) at (ax, ay)."""
    if img is None or img.size == 0:
        return
    if scale != 1:
        img = np.repeat(np.repeat(img, scale, 0), scale, 1)
    h, w = img.shape[:2]
    x0, y0 = int(round(ax - w / 2)), int(round(ay - h / 2))
    H, W = canvas.shape[:2]
    sx0, sy0, sx1, sy1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    blk = canvas[sy0:sy1, sx0:sx1]
    canvas[sy0:sy1, sx0:sx1] = over(blk.astype(np.float64), img[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0])


def label_img(text, scale=2):
    im = Image.new("RGB", (8 * len(text) + 8, 14), (24, 24, 24))
    ImageDraw.Draw(im).text((3, 1), text, fill=(255, 235, 140))
    return np.asarray(im.resize((im.width * scale, im.height * scale), Image.NEAREST))


def extent(frames, scale):
    """half sizes (display px) round the anchor that hold every frame."""
    hw = max((f.shape[1] * scale) / 2 for f, _ in frames)
    hh = max((f.shape[0] * scale) / 2 for f, _ in frames)
    return hw, hh


class Block:
    """one scene's lanes side by side (or stacked when wide), drawn at any time t (each lane loops its frames)."""

    def __init__(self, title, lanes, vertical):
        self.title, self.lanes, self.vertical = title, lanes, vertical
        boxes = [(int(math.ceil(hw)) * 2 + 8, int(math.ceil(hh)) * 2 + 8) for _, _, _, (hw, hh) in lanes]
        self.lw = max(b[0] for b in boxes)
        self.lh = max(b[1] for b in boxes)
        self.labels = [label_img(t) for t, _, _, _ in lanes]
        self.lab_h = max(lb.shape[0] for lb in self.labels)
        self.head = label_img(title)
        n = len(lanes)
        self.W = self.lw if vertical else self.lw * n
        self.H = self.head.shape[0] + ((self.lh + self.lab_h) * n if vertical else self.lh + self.lab_h)

    def draw(self, canvas, t):
        canvas[:] = GRASS
        hh = self.head.shape[0]
        canvas[:hh] = 12
        canvas[:hh, :min(self.W, self.head.shape[1])] = self.head[:, :min(self.W, self.head.shape[1])]
        lw, lh, lab_h = self.lw, self.lh, self.lab_h
        for i, (title, frames, scale, _) in enumerate(self.lanes):
            ox, oy = (0, hh + i * (lh + lab_h)) if self.vertical else (i * lw, hh)
            canvas[oy:oy + lab_h, ox:ox + lw] = 24
            lb = self.labels[i]
            canvas[oy:oy + lb.shape[0], ox:ox + min(lw, lb.shape[1])] = lb[:, :min(lw, lb.shape[1])]
            if frames:
                place(canvas[oy + lab_h:oy + lab_h + lh, ox:ox + lw], frame_at(frames, t), lw / 2, lh / 2, scale)
            if not self.vertical and i:
                canvas[hh:, ox] = 20


def write_gif(path, blocks, total, step=0.02):
    """blocks stacked top to bottom, `total` seconds in `step`s."""
    W = max(b.W for b in blocks)
    H = sum(b.H for b in blocks) + 6 * (len(blocks) - 1)
    out = []
    for k in range(max(1, int(round(total / step)))):
        canvas = np.zeros((H, W, 3), np.uint8)
        y = 0
        for b in blocks:
            sub = canvas[y:y + b.H, :b.W]
            b.draw(sub, k * step)
            y += b.H + 6
        out.append(Image.fromarray(canvas))
    pal = [im.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in out]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=int(step * 1000), loop=0, disposal=1)


def strip_png(path, frames, scale, bg=GRASS):
    w = sum(f.shape[1] * scale for f, _ in frames) + 4 * len(frames)
    h = max(f.shape[0] * scale for f, _ in frames)
    canvas = np.empty((h, w, 3), np.uint8)
    canvas[:] = bg
    x = 0
    for f, _ in frames:
        g = np.repeat(np.repeat(f, scale, 0), scale, 1)
        blk = canvas[(h - g.shape[0]) // 2:(h - g.shape[0]) // 2 + g.shape[0], x:x + g.shape[1]]
        blk[:] = over(blk.astype(np.float64), g)
        x += g.shape[1] + 4
        canvas[:, x - 4:x] = 20
    Image.fromarray(canvas).save(path)


def texels(frames):
    return int(sum(f.shape[0] * f.shape[1] for f, _ in frames))


def run_scene(name, sc, a, vfxs, sheets, report, blocks):
    sheet, tag = sc["tag"]
    d, im = load_fanim(a.root, sheet)
    now = tag_frames(d, im, tag)
    hd_tag = "hd_" + tag
    now_hd = tag_frames(d, im, hd_tag) if hd_tag in d["anims"] else None
    durs = sc.get("frames") or [dur for _, dur in now]
    starts = np.r_[0, np.cumsum(durs)[:-1]]
    intervals = [(float(s), float(s + dd)) for s, dd in zip(starts, durs)]
    total = float(sum(durs))
    out_dir = os.path.join(a.out, name)
    os.makedirs(out_dir, exist_ok=True)
    print(f"{name}: {sheet}:{tag} {len(durs)} frames, {total:.2f} s", flush=True)
    # 1. pixel frames from renders on transparency (8 canvas px a game px)
    # the pixel frames leave out a play's `pixel_skip` emitters too: dark contrast layers League lays on its map under
    # a bright effect (Lux R's scorch, Q's dark trail) turn into opaque brown bands on our sprites
    sc_px = json.loads(json.dumps(sc))
    for ps in sc_px["plays"]:
        ps["skip"] = list(ps.get("skip", [])) + list(ps.get("pixel_skip", []))
    hi = R.scene_frames(sc_px, intervals, ppx=8, vfxs=vfxs, layers=True)    # (matter, light) per frame
    cam = sc["camera"]
    center = cam.get("center") or [cam["size"][0] // 2 + 0.5, cam["size"][1] // 2 + 0.5]
    anchor = sc.get("anchor") or center
    ours_pal = np.concatenate([f.reshape(-1, 4) for f, _ in (now_hd or now)])
    ours_pal = np.unique(ours_pal[ours_pal[:, 3] > 0][:, :3], axis=0)
    px = dict(dict(k=14, gain=2.5, maxmix=0.4), **sc.get("pixel", {}))
    hd, one, pal = X.pixelate(hi, 8, tuple(anchor), palette=ours_pal if a.palette == "ours" else None, **px)
    new_hd = [(f, dd) for f, dd in zip(hd, durs)]
    new_one = [(f, dd) for f, dd in zip(one, durs)]
    # the same frames snapped to the colours of our present picture (the hero's effect palette)
    hd2, _one2, _ = X.pixelate(hi, 8, tuple(anchor), palette=ours_pal, **px)
    alt_hd = [(f, dd) for f, dd in zip(hd2, durs)]
    # 2. League lane: 30 fps, true colour, on grass, game size x4
    n30 = max(1, int(round(total * 30)))
    lg_iv = [(k / 30.0, (k + 1) / 30.0) for k in range(n30)]
    lg = R.scene_frames(sc, lg_iv, bg=GRASS, ppx=Z, vfxs=vfxs, shutter=2)
    ax, ay = anchor[0] * Z, anchor[1] * Z
    league = []
    for f in lg:
        u8 = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
        league.append((u8, 1 / 30.0))
    # the League lane's frames are whole canvases: re-centre them on the anchor
    H, W = lg[0].shape[:2]
    cx, cy = W / 2, H / 2
    dx, dy = int(round(ax - cx)), int(round(ay - cy))
    league = [(shift(f, -dx, -dy), t) for f, t in league]
    # 3. strips for review
    strip_png(os.path.join(out_dir, "league_frames.png"), [(np.asarray(R.to_image(f)), dd) for f, dd in zip(
        R.scene_frames(sc, intervals, bg=GRASS, ppx=Z, vfxs=vfxs), durs)], 1)
    strip_png(os.path.join(out_dir, "pixel_hd_x2.png"), new_hd, 2)
    strip_png(os.path.join(out_dir, "pixel_1x_x4.png"), new_one, 4)
    strip_png(os.path.join(out_dir, "pixel_hd_ourpalette_x2.png"), alt_hd, 2)
    if now_hd:
        strip_png(os.path.join(out_dir, "ours_hd_x2.png"), now_hd, 2)
    Image.fromarray(np.repeat(np.repeat(pal[None], 24, 0), 24, 1)).save(os.path.join(out_dir, "palette.png"))
    # 4. lanes
    lanes = []
    box_l = (W / 2, H / 2)
    lanes.append(("League render (true colour)", league, 1, box_l))
    lanes.append(("pixel PPU 2 (new)", new_hd, Z // 2, extent(new_hd, Z // 2)))
    lanes.append(("same, our palette", alt_hd, Z // 2, extent(alt_hd, Z // 2)))
    if now_hd:
        lanes.append(("ours now (hd_)", now_hd, Z // 2, extent(now_hd, Z // 2)))
    else:
        lanes.append(("ours now (1x)", now, Z, extent(now, Z)))
    op = sc.get("oppi")
    ofr = oppi_frames(op, a.oppi) if op else None
    if ofr:
        lanes.append((f"oppi ({os.path.basename(op['path'])})", ofr, Z, extent(ofr, Z)))
    # every lane boxed alike: the biggest of the drawn lanes, the League lane cropped to it
    bw = max(b[0] for _, _, _, b in lanes[1:])
    bh = max(b[1] for _, _, _, b in lanes[1:])
    bw, bh = max(bw, 40), max(bh, 40)
    lanes = [(t, fr, sc_, (min(b[0], bw + 8) if i == 0 else bw, min(b[1], bh + 8) if i == 0 else bh))
             for i, (t, fr, sc_, b) in enumerate(lanes)]
    hw0, hh0 = lanes[0][3]
    lanes[0] = (lanes[0][0], [(f[int(cy - hh0):int(cy + hh0), int(cx - hw0):int(cx + hw0)], t) for f, t in lanes[0][1]],
                1, lanes[0][3])
    league_rgba = []
    for f, t in lanes[0][1]:
        g = np.concatenate([f[..., :3], np.full(f.shape[:2] + (1,), 255, np.uint8)], -1)
        league_rgba.append((g, t))
    lanes[0] = (lanes[0][0], league_rgba, 1, lanes[0][3])
    vertical = bw > 1.6 * bh
    reps = max(1, int(round(1.2 / total))) if total < 0.6 else 1
    block = Block(f"{name}: {sheet}:{tag}  ({len(durs)} frames, {total:.2f} s)", lanes, vertical)
    write_gif(os.path.join(a.out, f"{name}.gif"), [block], total * reps)
    blocks[name] = (block, total)
    # 5. candidate sheet: the tag and its hd_ twin replaced
    tags = sheets.setdefault(sheet, {t: tag_frames(d, im, t) for t in d["anims"]})
    tags[tag] = [(f, dd) for f, dd in new_one]
    tags[hd_tag] = [(f, dd) for f, dd in new_hd]
    report[name] = {
        "tag": f"{sheet}:{tag}", "frames": len(durs), "seconds": round(total, 3),
        "new_sizes_1x": sorted({(int(f.shape[1]), int(f.shape[0])) for f, _ in new_one}),
        "now_sizes_1x": sorted({(int(f.shape[1]), int(f.shape[0])) for f, _ in now}),
        "texels_now": texels(now) + (texels(now_hd) if now_hd else 0),
        "texels_new": texels(new_one) + texels(new_hd),
        "colours": int(len(pal)),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scenes", nargs="*")
    here = os.path.isdir(os.path.join(ROOT, "league", "effects"))
    ap.add_argument("--root", default=ROOT if here else r"C:\t\inst_bv", help="a tree with league/effects")
    ap.add_argument("--oppi", default=OPPI)
    ap.add_argument("--palette", default="own", choices=["own", "ours"])
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    scenes = json.load(open(os.path.join(HERE, "vfx_scenes.json"), encoding="utf-8"))["scenes"]
    names = a.scenes or list(scenes)
    vfxs, sheets, report, blocks = {}, {}, {}, {}
    for name in names:
        run_scene(name, scenes[name], a, vfxs, sheets, report, blocks)
    spells = json.load(open(os.path.join(HERE, "vfx_scenes.json"), encoding="utf-8")).get("spells", {})
    for spell, members in spells.items():
        have = [blocks[m] for m in members if m in blocks]
        if len(have) == len(members):
            total = max(t for _, t in have)
            total = total * max(1, int(round(1.2 / total))) if total < 0.6 else total
            write_gif(os.path.join(a.out, f"{spell}.gif"), [b for b, _ in have], total)
    import strips
    for sheet, tags in sheets.items():
        ms = {t: [(f, dd * 1000) for f, dd in fr] for t, fr in tags.items()}
        strips.write_sheet(os.path.join(a.out, "sheets", sheet), ms, share=True)
    with open(os.path.join(a.out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    for k, v in report.items():
        print(k, v)


if __name__ == "__main__":
    main()
