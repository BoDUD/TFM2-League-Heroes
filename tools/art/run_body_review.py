#!/usr/bin/env python3
"""Review sets for tools/art/run_body_anim.py (`run_body_anim.py --batch H1 H2 ... --out DIR`), nothing written to the
tree. Per hero, into DIR:

  <hero>_lanes_move.gif     its runs side by side moving over the map's grass at its move speed, game size x3
  <hero>_lanes_inplace.gif  the same in place: game size x3 above, the dense squares x3 below
  <hero>_still.png          every frame at game size x3 on the grass, one row a run
  <hero>/frames_x4_a.png, frames_x4_b.png   the frames x4: each run, the layers, what changed
  <hero>/part_<layer>_x8.png                each laid layer across the frames (and the legs), x8
  <hero>/metrics.json
The runs: the tree's (when it is not the drawn run the tool starts from: league_jinx's re-posed one), the drawn run,
the new one. GIF frames are 20 ms (each one labelled with its time, so none is merged).

And for the batch: batch_sheet.png (every hero, each run, game size x3), batch_inplace.gif (every hero in place, each
run, game size x3) and summary.md / summary.json - per hero:
- legs changed: squares of the drawn frame from its waist down, not under the laid body, that are not as drawn (0);
- locked layers alike: squares of each laid layer that are not frame `from`'s (outline the thinning pass took off
  counted apart); a chain's squares are its columns moved whole;
- weapon by the face: the fewest squares between each part and her face's skin, new against drawn (never less);
- head path: the body's place per frame (columns: one; rows: its steps);
- outline band, pinhole squares (clear squares she shuts in), colours, against the drawn run.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

import run_body_anim as R

T = R.T
BG = (88, 110, 72, 255)
STEP = 20
GROUNDS = {"grass": [((34, 51, 48), 0.35), ((39, 61, 50), 0.2), ((46, 67, 51), 0.25), ((58, 77, 46), 0.12),
                     ((76, 78, 56), 0.08)],
           "dirt": [((58, 77, 46), 0.06), ((74, 86, 47), 0.14), ((92, 91, 57), 0.8)]}


def font(sz):
    for name in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", name), sz)
        except OSError:
            pass
    return ImageFont.load_default()


F14, F16, F20 = font(14), font(16), font(20)


def map_ground(kind, w, h, seed=7):
    rng = np.random.default_rng(seed)
    f = (ndimage.gaussian_filter(rng.random((h, w)), 11, mode="wrap")
         + 0.1 * ndimage.gaussian_filter(rng.random((h, w)), 1.2, mode="wrap"))
    cols, shares = zip(*GROUNDS[kind])
    band = np.digitize(f, np.quantile(f, np.cumsum(shares)[:-1]))
    a = np.array(cols, np.uint8)[band]
    return Image.fromarray(np.dstack([a, np.full((h, w), 255, np.uint8)]), "RGBA")


def paste(dst, im, x, y):
    x, y = int(round(x)), int(round(y))
    sx, sy = max(0, -x), max(0, -y)
    if sx >= im.width or sy >= im.height:
        return
    if sx or sy:
        im = im.crop((sx, sy, im.width, im.height))
    x, y = x + sx, y + sy
    if x >= dst.width or y >= dst.height:
        return
    w, h = min(im.width, dst.width - x), min(im.height, dst.height - y)
    if (w, h) != im.size:
        im = im.crop((0, 0, w, h))
    dst.alpha_composite(im, (x, y))


def game(a, k, z=1):
    h, w = a.shape[:2]
    return Image.fromarray(a).resize((max(1, round(w * k * z)), max(1, round(h * k * z))), Image.LANCZOS)


def at(frames, t):
    total = sum(ms for _, ms in frames)
    t %= total
    for i, (_, ms) in enumerate(frames):
        if t < ms:
            return i
        t -= ms
    return len(frames) - 1


def quantize_all(imgs):
    sample = Image.new("RGB", (imgs[0].width, imgs[0].height * 4))
    for j, i in enumerate(range(0, len(imgs), max(1, len(imgs) // 4))):
        if j < 4:
            sample.paste(imgs[i].convert("RGB"), (0, j * imgs[0].height))
    pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    return [im.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]


def extent(frames):
    t, b, w = 0, 0, 0
    for a in frames:
        op = a[..., 3] > 0
        ys, xs = np.nonzero(op.any(1))[0], np.nonzero(op.any(0))[0]
        t = min(t, ys.min() - a.shape[0] / 2.0)
        b = max(b, ys.max() + 1 - a.shape[0] / 2.0)
        w = max(w, abs(xs.min() - a.shape[1] / 2.0), abs(xs.max() + 1 - a.shape[1] / 2.0))
    return t, b, w


def save_gif(path, frames, durations):
    q = quantize_all(frames)
    q[0].save(path, save_all=True, append_images=q[1:], duration=durations, loop=0, disposal=1)


class Hero:
    """One hero's runs and what the tool makes of it."""

    def __init__(self, name):
        self.name = R.short(name)
        self.cfg = R.load(self.name)
        self.hid, self.pack, self.ppu, self.size = T.resolve(self.name, T.all_heroes())
        self.k = self.size / self.ppu
        self.drawn, _ = R.drawn(self.cfg)
        self.new, self.info, self.mov = R.make(self.name, self.cfg)
        an, px = T.read(self.hid, self.pack)
        tag = self.cfg["tag"]
        self.tree = R.frames_of(an, px, "hd_" + tag)
        same = len(self.tree) == len(self.drawn) and all(
            np.array_equal(a, b) for (a, _), (b, _) in zip(self.tree, self.drawn))
        new_d = self.new["hd_" + tag]
        is_new = len(self.tree) == len(new_d) and all(np.array_equal(a, b) for (a, _), (b, _) in zip(self.tree, new_d))
        self.lanes = []
        if not same and not is_new:
            self.lanes.append(("已安装", self.tree))
        self.lanes.append(("原画" if not same and not is_new else "现在", self.drawn))
        self.lanes.append(("新", new_d))
        with open(R.lp(os.path.join(R.ROOT, self.pack, "champion", self.hid + ".data_champion")),
                  encoding="utf-8-sig") as f:
            sp = float(json.load(f).get("stat", {}).get("move_speed") or 600)
        self.v = sp / 1000.0 * 60 / 1000.0                # game px a ms (60 ticks a second)

    # ----------------------------------------------------------------------------------------- pictures
    def lanes_move(self, path, Z=3, LW=130):
        t0, b0, _ = extent([a for _, fr in self.lanes for a, _ in fr])
        top = -t0 * self.k + 4
        LH = int(np.ceil(top + b0 * self.k + 6))
        span = int(round((LW + 20) / self.v / STEP)) * STEP
        pics = [[game(a, self.k, Z) for a, _ in fr] for _, fr in self.lanes]
        ground = map_ground("grass", LW, LH, seed=3).resize((LW * Z, LH * Z), Image.NEAREST)
        hd = 22
        out = []
        for t in range(0, span, STEP):
            can = Image.new("RGBA", (LW * Z, (LH * Z + hd) * len(self.lanes) + 4), (30, 30, 30, 255))
            x = -10 + self.v * t
            for li, (name, fr) in enumerate(self.lanes):
                lane = ground.copy()
                im = pics[li][at(fr, t)]
                paste(lane, im, x * Z - im.width / 2.0, top * Z - im.height / 2.0)
                y0 = li * (LH * Z + hd + 4)
                cyc = sum(m for _, m in fr)
                ImageDraw.Draw(can).text((6, y0 + 2), f"{self.name}  {name}  {len(fr)} 帧 {cyc} ms" +
                                         (f"  {t} ms" if li == 0 else ""), font=F14, fill=(255, 255, 255, 255))
                can.alpha_composite(lane, (0, y0 + hd))
            out.append(can)
        save_gif(path, out, STEP)
        return {"frames": len(out), "frame_ms": STEP}

    def inplace_frames(self, Z=3, dense=True, label=True):
        t0, b0, hw = extent([a for _, fr in self.lanes for a, _ in fr])
        colw = int(np.ceil(2 * hw * self.k + 8)) * Z
        top = -t0 * self.k + 3
        LH = int(np.ceil(top + b0 * self.k + 4))
        rowg = LH * Z
        cyd = (-t0 + 4) * 2
        rowd = int(np.ceil(b0 - t0 + 8)) * 2 if dense else 0
        colw = max(colw, int(np.ceil(2 * hw + 8)) * 2 if dense else 0)
        cycles = [sum(m for _, m in fr) for _, fr in self.lanes]
        span = int(np.lcm.reduce(cycles)) if max(cycles) * 3 >= int(np.lcm.reduce(cycles)) else max(cycles)
        gpics = [[game(a, self.k, Z) for a, _ in fr] for _, fr in self.lanes]
        dpics = [[Image.fromarray(a).resize((a.shape[1] * 2, a.shape[0] * 2), Image.NEAREST) for a, _ in fr]
                 for _, fr in self.lanes] if dense else None
        ground = map_ground("grass", colw // Z + 1, LH, seed=5).resize(((colw // Z + 1) * Z, LH * Z), Image.NEAREST)
        head = 26 if label else 0
        out = []
        for t in range(0, span, STEP):
            can = Image.new("RGBA", (colw * len(self.lanes) + 6 * (len(self.lanes) - 1), head + rowg + rowd + 4),
                            (30, 30, 30, 255))
            for li, (name, fr) in enumerate(self.lanes):
                i = at(fr, t)
                x0 = li * (colw + 6)
                if label:
                    ImageDraw.Draw(can).text((x0 + 6, 4), f"{name} 帧{i}" + (f"  {t} ms" if li == 0 else ""),
                                             font=F14, fill=(255, 255, 255, 255))
                cell = Image.new("RGBA", (colw, rowg), (30, 30, 30, 255))
                cell.alpha_composite(ground.crop((0, 0, colw, rowg)), (0, 0))
                im = gpics[li][i]
                paste(cell, im, colw / 2.0 - im.width / 2.0, top * Z - im.height / 2.0)
                can.alpha_composite(cell, (x0, head))
                if dense:
                    cell = Image.new("RGBA", (colw, rowd), BG)
                    im = dpics[li][i]
                    paste(cell, im, colw / 2.0 - im.width / 2.0, cyd - im.height / 2.0)
                    can.alpha_composite(cell, (x0, head + rowg + 4))
            out.append(can)
        return out

    def lanes_inplace(self, path):
        out = self.inplace_frames()
        save_gif(path, out, STEP)
        return {"frames": len(out), "frame_ms": STEP}

    def still(self, path, Z=3):
        """Every frame at game size x Z on the grass, a row a run."""
        allf = [a for _, fr in self.lanes for a, _ in fr]
        top = max(a.shape[0] / 2.0 * self.k for a in allf) + 3
        cw = int(np.ceil(max(a.shape[1] * self.k for a in allf))) + 3
        bot = max(extent(allf)[1], 0)
        RH = int(np.ceil(top + bot * self.k + 4))
        n = max(len(fr) for _, fr in self.lanes)
        W = cw * n + 4
        row = map_ground("grass", W, RH, seed=11)
        img = Image.new("RGBA", (W * Z, (RH * Z + 24) * len(self.lanes)), (30, 30, 30, 255))
        d = ImageDraw.Draw(img)
        for li, (name, fr) in enumerate(self.lanes):
            lane = row.copy()
            for j, (a, _) in enumerate(fr):
                im = game(a, self.k)
                paste(lane, im, 2 + j * cw + cw / 2.0 - im.width / 2.0, top - im.height / 2.0)
            y0 = li * (RH * Z + 24)
            d.text((6, y0 + 3), f"{self.name}  {name}（游戏里的大小 x{Z}）", font=F16, fill=(255, 255, 255, 255))
            img.alpha_composite(lane.resize((W * Z, RH * Z), Image.NEAREST), (0, y0 + 24))
        img.convert("RGB").save(path)

    def frames_x4(self, out_dir):
        Z = 4
        lanes = self.lanes
        t, b, hw = extent([a for _, fr in lanes for a, _ in fr])
        cw = int(np.ceil(2 * hw + 6)) * Z
        rh = int(np.ceil(b - t + 6)) * Z
        cy_ = (-t + 3) * Z
        head = 30
        rows = [n for n, _ in lanes] + ["图层", "和原画比"]
        n = len(self.drawn)
        palette = [(255, 60, 220), (60, 200, 255), (120, 255, 120), (200, 120, 255), (255, 90, 90), (90, 255, 220)]
        others = [nm for nm in R.layer_names(self.cfg) if nm != "body"]
        cols = {nm: palette[j % len(palette)] for j, nm in enumerate(others)}
        cols["body"] = (255, 140, 0)
        for part, idx in (("a", range(0, (n + 1) // 2)), ("b", range((n + 1) // 2, n))):
            idx = list(idx)
            img = Image.new("RGBA", (cw * len(idx) + 120, head + len(rows) * (rh + 26) + 56), (30, 30, 30, 255))
            d = ImageDraw.Draw(img)
            for ci, col in enumerate(idx):
                lab = f"帧 {col}  起伏 {self.mov['body'][col]}"
                for p in self.cfg.get("parts", []):
                    lab += f"  {p['name']} {self.mov[p['name']][col]:+d}"
                d.text((120 + ci * cw + 4, 6), lab, font=F14, fill=(255, 255, 255, 255))
            for ri, name in enumerate(rows):
                y0 = head + ri * (rh + 26)
                d.text((6, y0 + rh // 2), name, font=F20, fill=(255, 255, 255, 255))
                for ci, col in enumerate(idx):
                    if ri < len(lanes):
                        fr = lanes[ri][1]
                        if col >= len(fr):
                            continue
                        a = fr[col][0]
                    else:
                        a1 = self.new["hd_" + self.cfg["tag"]][col][0]
                        a0 = self.drawn[col][0]
                        a = a1.copy()
                        op = a[..., 3] > 0
                        grey = a[..., :3].astype(int).mean(-1, keepdims=True)
                        a[..., :3] = np.where(op[..., None], (grey * 0.35 + 70).astype(np.uint8), a[..., :3])
                        if ri == len(lanes):
                            inf = self.info[col]
                            for nm in R.layer_names(self.cfg):
                                m = inf[nm]
                                a[m, :3] = (np.array(cols[nm]) * 0.75 + a[m, :3] * 0.25).astype(np.uint8)
                            a[inf["joined"] & op, :3] = (255, 255, 0)
                        else:
                            if a0.shape == a1.shape:
                                dif = (a1 != a0).any(-1)
                                a[dif & op, :3] = (255, 140, 0)
                                a[dif & ~op, :3] = (255, 255, 255)
                                a[dif, 3] = 255
                    cell = Image.new("RGBA", (cw, rh), BG)
                    im = Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST)
                    paste(cell, im, cw / 2.0 - im.width / 2.0, cy_ - im.height / 2.0)
                    img.alpha_composite(cell, (120 + ci * cw, y0))
            names_ = {(255, 60, 220): "粉", (60, 200, 255): "蓝", (120, 255, 120): "绿", (200, 120, 255): "紫",
                      (255, 90, 90): "红", (90, 255, 220): "青", (255, 140, 0): "橙"}
            leg = "图层：" + "　".join(f"{names_[cols[nm]]} = {nm}" for nm in R.layer_names(self.cfg)) +                 "　黄 = 接缝（补色、描边）　灰 = 腿（原画不动）"
            d.text((6, img.height - 52), leg, font=F14, fill=(255, 255, 255, 255))
            d.text((6, img.height - 26), "和原画比：橙 = 不同的格子　白 = 清掉的", font=F14, fill=(255, 255, 255, 255))
            img.convert("RGB").save(os.path.join(out_dir, f"frames_x4_{part}.png"))

    def strips(self, out_dir):
        dense = [a for a, _ in self.new["hd_" + self.cfg["tag"]]]
        res = {}
        for name in R.layer_names(self.cfg) + ["legs"]:
            ms = [inf[name] if name != "legs" else inf["legs"] & ~self._laid(inf) for inf in self.info]
            strip(dense, ms, 8, os.path.join(out_dir, f"part_{name.replace(' ', '_')}_x8.png"))
            res[name] = [int(m.sum()) for m in ms]
        return res

    def _laid(self, inf):
        m = np.zeros(inf["legs"].shape, bool)
        for nm in R.layer_names(self.cfg):
            m |= inf[nm]
        return m

    # ----------------------------------------------------------------------------------------- checks
    def metrics(self):
        cfg, tag = self.cfg, self.cfg["tag"]
        dense = [a for a, _ in self.new["hd_" + tag]]
        drawn = [a for a, _ in self.drawn]
        i0 = cfg["from"]
        src = drawn[i0]
        layers = {"head": R.head_of(src, cfg)} if cfg.get("lock") == "head" else R.pieces(src, cfg, i0)
        m = {"hero": self.hid, "ppu": self.ppu, "sizes": self.size, "game_px_a_square": round(self.k, 4),
             "frames": len(dense), "ms": [x for _, x in self.new["hd_" + tag]], "from": i0,
             "bob": self.mov["body"], "bob_game_px": round((max(self.mov["body"]) - min(self.mov["body"])) * self.k, 2)}
        for p in cfg.get("parts", []):
            m[f"part {p['name']} rows"] = self.mov[p["name"]]
        # legs as drawn
        legs = []
        for a, b, inf in zip(drawn, dense, self.info):
            vis = inf["legs"] & ~self._laid(inf) & (b[..., 3] > 0) & ~inf.get("kept", np.zeros(b.shape[:2], bool))
            # (kept squares - a vine swung in the drawing - moved with the body are not legs; counted apart)
            legs.append(int(((b != a).any(-1) & vis).sum()))
        m["legs_changed"] = legs
        m["kept_squares"] = [int(inf.get("kept", np.zeros(1, bool)).sum()) for inf in self.info]
        if cfg.get("lock") != "head":
            m["own_pieces_taken_under_the_waist"] = [int((inf["own"] & self._below(a, inf)).sum())
                                                     for a, inf in zip(drawn, self.info)]
        else:
            m["own_head_squares_cleared"] = [int(inf["own"].sum()) for inf in self.info]
            m["head_drawn_at_from_centre"] = [[int(inf["drawn_at"][0] - (a.shape[0] // 2 - src.shape[0] // 2)),
                                                int(inf["drawn_at"][1] - (a.shape[1] // 2 - src.shape[1] // 2))]
                                               for a, inf in zip(drawn, self.info)]
        # laid layers against frame `from`
        alike = {}
        for name in R.layer_names(cfg):
            src_m = layers[name]
            diffs, thinned = [], []
            for i, (b, inf) in enumerate(zip(dense, self.info)):
                dy, dx = inf["at"]
                ys, xs = np.nonzero(src_m)
                ty = ys + dy
                if name in [p["name"] for p in cfg.get("parts", [])]:
                    ty = ty + self.mov[name][i]
                elif name in [c["name"] for c in cfg.get("chains", [])]:
                    ty = ty + np.array([self.mov[name][i].get(int(x), 0) for x in xs], int)
                tx = xs + dx
                ok = (ty >= 0) & (ty < b.shape[0]) & (tx >= 0) & (tx < b.shape[1])
                ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
                vis = inf[name][ty, tx]
                later = np.zeros(len(ty), bool)
                names = R.layer_names(cfg)
                for nm in names[names.index(name) + 1:]:
                    later |= inf[nm][ty, tx]
                dif = (b[ty, tx] != src[ys, xs]).any(-1) & ~later
                th = inf["thinned"][ty, tx]
                diffs.append(int((dif & vis & ~th).sum()))
                thinned.append(int((dif & th).sum()))
            alike[name] = {"squares_not_as_frame_from": diffs, "outline_thinned": thinned}
        m["locked_layers"] = alike
        # parts by the face
        FACE_MIN = {}
        for name in [p["name"] for p in cfg.get("parts", [])]:
            g_new = []
            for b, inf in zip(dense, self.info):
                g_new.append(self._gap(b, inf["body"], inf[name]))
            g_drawn = self._gap(src, layers["body"], layers[name])
            # (closer than in the drawing only matters by the face: within 4 squares)
            FACE_MIN[name] = {"new": g_new, "drawn_frame_from": g_drawn,
                              "ok": all(g is None or g_drawn is None or g >= g_drawn or g >= 4 for g in g_new)}
        m["parts_to_face_squares"] = FACE_MIN
        # head path
        at_ = [inf["at"] for inf in self.info]
        xs_ = [dx - (b.shape[1] // 2) for (dy, dx), b in zip(at_, dense)]
        ys_ = [dy - (b.shape[0] // 2) for (dy, dx), b in zip(at_, dense)]
        m["head_path"] = {"cols": sorted(set(xs_)), "row_steps": [ys_[(i + 1) % len(ys_)] - ys_[i] for i in range(len(ys_))]}
        # outline, pinholes, colours
        oc = [list(cfg["outline"])]
        m["outline_band"] = {"drawn": T.measure(drawn, oc), "new": T.measure(dense, oc)}
        m["pinhole_squares"] = {"drawn": [sum(holes(a)) for a in drawn], "new": [sum(holes(a)) for a in dense]}
        cd, cn = colours(drawn), colours(dense)
        m["colours_not_in_drawn"] = sorted(map(list, cn - cd))
        m["one_x_squares_off"] = [inf["one_lost"] for inf in self.info]
        return m

    def _below(self, a, inf):
        H = a.shape[0]
        i = [x is inf for x in self.info].index(True)
        wr = H // 2 + self.cfg["waist"][i]
        m = np.zeros(a.shape[:2], bool)
        m[wr:] = True
        return m

    def _gap(self, b, body, part):
        """Fewest squares between the part and the skin of the face (skin in the top third of the laid body)."""
        ys = np.nonzero(body.any(1))[0]
        if not len(ys):
            return None
        top = ys.min()
        band = np.zeros(body.shape, bool)
        band[top:top + max(4, (ys.max() - top) // 3)] = True
        face = np.zeros(body.shape, bool)
        for y, x in zip(*np.nonzero(body & band)):
            if skin(b[y, x]):
                face[y, x] = True
        if not face.any() or not part.any():
            return None
        dist = ndimage.distance_transform_cdt(~face, metric="chessboard")
        return int(dist[part & ~face].min()) - 1


def skin(c):
    r, g, b = (int(v) for v in c[:3])
    return r > g > b and r - b >= 40 and r >= 150 and g >= 90


def holes(a):
    tr = a[..., 3] == 0
    lab, n = ndimage.label(tr)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist())
    return [int((lab == j).sum()) for j in range(1, n + 1) if j not in edge]


def colours(fr):
    s = set()
    for a in fr:
        s |= set(map(tuple, a[a[..., 3] > 0][:, :3].tolist()))
    return s


def strip(frames, ms, z, path, bg=(70, 90, 60)):
    crops = []
    for f, m in zip(frames, ms):
        if not m.any():
            crops.append(np.zeros((4, 4, 3), np.uint8))
            continue
        f = np.pad(f, ((1, 1), (1, 1), (0, 0)))
        m = np.pad(m, 1)
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
        c = f[y0:y1, x0:x1].copy()
        c[~m[y0:y1, x0:x1]] = 0
        o = np.zeros(c.shape[:2] + (3,), np.uint8)
        o[:] = bg
        al = c[..., 3:4] / 255.0
        crops.append((c[..., :3] * al + o * (1 - al)).astype(np.uint8))
    H = max(c.shape[0] for c in crops)
    W = sum(c.shape[1] + 3 for c in crops)
    s = np.zeros((H, W, 3), np.uint8)
    s[:] = (30, 30, 30)
    x = 0
    for c in crops:
        s[H - c.shape[0]:, x:x + c.shape[1]] = c
        x += c.shape[1] + 3
    Image.fromarray(s).resize((W * z, H * z), Image.NEAREST).save(path)


def batch(heroes, out):
    os.makedirs(out, exist_ok=True)
    done, summary = [], {}
    for name in heroes:
        h = Hero(name)
        hd = os.path.join(out, h.name)
        os.makedirs(hd, exist_ok=True)
        m = h.metrics()
        m["move_gif"] = h.lanes_move(os.path.join(out, f"{h.name}_lanes_move.gif"))
        m["inplace_gif"] = h.lanes_inplace(os.path.join(out, f"{h.name}_lanes_inplace.gif"))
        h.still(os.path.join(out, f"{h.name}_still.png"))
        h.frames_x4(hd)
        m["layer_squares"] = h.strips(hd)
        with open(os.path.join(hd, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=1)
        summary[h.name] = m
        done.append(h)
        print(f"{h.name}: legs changed {m['legs_changed']}, layers not as frame {h.cfg['from']}: "
              f"{ {k: v['squares_not_as_frame_from'] for k, v in m['locked_layers'].items()} }")
    # the batch sheet: every hero, each run, game size x3
    rows = []
    for h in done:
        allf = [a for _, fr in h.lanes for a, _ in fr]
        top = max(a.shape[0] / 2.0 * h.k for a in allf) + 2
        cw = int(np.ceil(max(a.shape[1] * h.k for a in allf))) + 2
        RH = int(np.ceil(top + max(extent(allf)[1], 0) * h.k + 3))
        for name, fr in h.lanes:
            lane = map_ground("grass", cw * len(fr) + 4, RH, seed=11)
            for j, (a, _) in enumerate(fr):
                im = game(a, h.k)
                paste(lane, im, 2 + j * cw + cw / 2.0 - im.width / 2.0, top - im.height / 2.0)
            rows.append((f"{h.name} {name}", lane.resize((lane.width * 3, lane.height * 3), Image.NEAREST)))
    W = max(r.width for _, r in rows) + 150
    H = sum(r.height + 6 for _, r in rows)
    sheet = Image.new("RGB", (W, H), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    y = 0
    for lab, r in rows:
        d.text((6, y + r.height // 2 - 8), lab, font=F16, fill=(255, 255, 255))
        sheet.paste(r.convert("RGB"), (150, y))
        y += r.height + 6
    sheet.save(os.path.join(out, "batch_sheet.png"))
    # every hero in place (game size x3), each run, one GIF
    per = [h.inplace_frames(dense=False) for h in done]
    span = max(len(p) for p in per)
    Wg = max(p[0].width for p in per)
    Hg = sum(p[0].height + 4 for p in per)
    gif = []
    for t in range(span):
        can = Image.new("RGBA", (Wg, Hg), (30, 30, 30, 255))
        y = 0
        for p in per:
            can.alpha_composite(p[t % len(p)], (0, y))
            y += p[0].height + 4
        gif.append(can)
    save_gif(os.path.join(out, "batch_inplace.gif"), gif, STEP)
    # the summary
    lines = ["| hero | legs changed | locked layers not as frame `from` (thinned apart) | parts by the face (new >= drawn) |"
             " head path cols / row steps | outline band drawn -> new | pinhole squares | new colours | 1x squares off |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, m in summary.items():
        lay = "; ".join(f"{k} {max(v['squares_not_as_frame_from'])}" for k, v in m["locked_layers"].items())
        face = "; ".join(f"{k} {'ok' if v['ok'] else 'CLOSER'} ({min([g for g in v['new'] if g is not None] or [-1])} vs "
                         f"{v['drawn_frame_from']})" for k, v in m["parts_to_face_squares"].items()) or "-"
        lines.append(f"| {name} | {max(m['legs_changed'])} | {lay} | {face} | {m['head_path']['cols']} / "
                     f"{m['head_path']['row_steps']} | {m['outline_band']['drawn']} -> {m['outline_band']['new']} | "
                     f"{sum(m['pinhole_squares']['drawn'])} -> {sum(m['pinhole_squares']['new'])} | {len(m['colours_not_in_drawn'])} | "
                     f"{m['one_x_squares_off']} |")
    with open(os.path.join(out, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print("\n".join(lines))
