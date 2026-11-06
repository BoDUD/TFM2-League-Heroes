#!/usr/bin/env python3
"""Kayn's actions in his three forms from Codex's whole-frame redraw - the base Kayn (assets/source/kayn/hd/casts:
tools/art/pack_kayn_actions.py's pack), the Darkin (assets/source/kayn_darkin/hd/casts: pack_kayn_darkin_actions.py,
his sheet's rh_ tags) and the Shadow Assassin (assets/source/kayn_shadow/hd/casts: pack_kayn_shadow_actions.py, the
sh_ tags), delivered 2026-11-06 (Documents/Codex/2026-11-05/new-chat/outputs/<form>-actions/raw: each sheet its raw
generation byte for byte; the top-level sheets there are Codex's own grid clean-up, not used) - read onto each form's
design squares the way tools/art/casts_khazix_hd.py reads Kha'Zix (casts_rengar_hd's keying, cells and palette
sampling), pointed at the form's design (the user, 2026-11-06: 「Codex全都交付了 你做到完美后喊我review」).

One module for the three forms (casts_kayn_darkin_hd.py and casts_kayn_shadow_hd.py run it on theirs): casts_rengar_hd's
reading works on module globals (the design, its head, its palette), so Form.bind() points them at a form before it is
read - the rig reads all three in one process.

Each frame's zoom (Codex's px a design square) is the one its fit over its template's pale figure gives (--fits: the
drawing's mask scaled until it overlaps the pale old frame Codex drew it on best, FFT correlation); where it overlaps
under 0.65 (another pose) the median of that and the zoom its HEIGHT gives against the old body's. The fits and the
pivot column are kept in assets/source/<form>/hd/casts/read.json (--fits writes them). Each frame is then placed where
the old body stood: its box's middle on the old box's middle and its bottom on the old box's bottom, from the pivot,
on the design's grid; he stands on the ground (no hover). The pivot column (--pivot) is where the design lies best
over the old idle_base of the form (its silhouette scaled by PPU, the soles on the ground line).

    python tools/art/casts_kayn_hd.py --fits C:/t/kayn_actions/templates   # zooms + the pivot -> read.json
    python tools/art/casts_kayn_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_kayn_hd.py --heads           # each placed frame's head against the design's (1.0: its size)
    (the same with casts_kayn_darkin_hd.py / casts_kayn_shadow_hd.py and their packs' templates)
"""
import argparse
import importlib
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.signal import fftconvolve
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_rengar_hd as CS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
OLD_HD = os.path.join(ROOT, "assets", "source", "kayn", "hd", "old")    # Kayn's old 1x sheet: all three forms' tags
# form -> (its pack, its 1x rows, the design's head box (rows r0-r1, cols c0-c1): the hair spikes to the chin, the
# horns to the jaw, the hair top to the chin)
SPEC = {
    "kayn": ("pack_kayn_actions", 40, (0, 25, 26, 58)),
    "kayn_darkin": ("pack_kayn_darkin_actions", 43, (0, 26, 10, 66)),
    "kayn_shadow": ("pack_kayn_shadow_actions", 40, (0, 21, 38, 64)),
}
FIT_OK = 0.65                   # a fit this good gives the zoom alone


class Form:
    def __init__(self, name):
        pack, rows_1x, head = SPEC[name]
        self.name = name
        self.PK = importlib.import_module(pack)
        self.HD = os.path.join(ROOT, "assets", "source", name, "hd")
        self.SRC = os.path.join(self.HD, "casts")
        self.TAGS = self.PK.TAGS
        self.D0 = np.asarray(Image.open(CS.lp(os.path.join(self.HD, "design.png"))).convert("RGBA"))
        self.PPU = self.D0.shape[0] / rows_1x
        self.GROUND = int(np.nonzero(self.D0[..., 3].any(1))[0].max()) + 1
        self.HEAD = head
        self.PAL = np.unique(self.D0[self.D0[..., 3] > 0][:, :3], axis=0)
        self.PAL_LAB = color.rgb2lab(self.PAL[None].astype(float) / 255.0)[0]
        self.HEAD_MASK = self._head_mask()
        self.OLD = self.PK.old_frames(CS.lp(os.path.join(OLD_HD, "sheet.png")), CS.lp(os.path.join(OLD_HD, "anim.fanim")))
        idle = self.PK.idle_sheet()
        runs = [f[0] for f in self.OLD[self.PK.RUN_TAG]]
        self.BODY_PAL = np.unique(np.concatenate([f[f[..., 3] > 0][:, :3] for f in runs + [idle]]), axis=0).astype(int)
        self.read_json = os.path.join(self.SRC, "read.json")
        self.data = {}
        if os.path.isfile(self.read_json):
            with open(self.read_json, encoding="utf-8") as f:
                self.data = json.load(f)

    # -- casts_rengar_hd's globals pointed at this form
    def bind(self):
        CS.D0, CS.HEAD, CS.HEAD_MASK = self.D0, self.HEAD, self.HEAD_MASK
        CS.PAL, CS.PAL_LAB = self.PAL, self.PAL_LAB

    def _head_mask(self):
        """The head in HEAD's box: its largest opaque piece, holes filled."""
        r0, r1, c0, c1 = self.HEAD
        op = self.D0[r0:r1, c0:c1, 3] > 0
        lbl, n = ndimage.label(op)
        m = lbl == int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1)))) + 1
        return ndimage.binary_fill_holes(m)

    def sheets(self):
        with open(CS.lp(os.path.join(self.SRC, "sheets.json")), encoding="utf-8") as f:
            return json.load(f)["sheets"]

    @property
    def PIVOT(self):
        return self.data["pivot"]

    def zoom_of(self, frame, sheet):
        """The frame's zoom: its fit where it overlaps FIT_OK up, else the median of the fit and its height's; a frame
        without a fit (none) the sheet's mean."""
        fits, hts = self.data.get("fits", {}), self.data.get("heights", {})
        if frame in fits:
            z, ov = fits[frame]
            if ov >= FIT_OK or frame not in hts:
                return z
            return float(np.median([z, hts[frame]]))
        zs = [self.zoom_of(f, sheet) for f, s in self.data.get("sheet_of", {}).items() if s == sheet and f in fits]
        return float(np.mean(zs))

    # -- the old frames
    def old_body(self, fr):
        """An old frame's body: its pixels in the body's colours (within 40) and within two pixels of the dark outline
        (the baked effects have none), the largest 8-connected piece and any of 30 pixels up."""
        op = fr[..., 3] > 0
        d = np.abs(fr[..., :3].astype(int)[:, :, None, :] - self.BODY_PAL[None, None]).sum(-1).min(-1)
        m = op & (d <= 40) & ndimage.binary_dilation(op & (fr[..., :3].max(-1) < 90), structure=np.ones((3, 3)),
                                                     iterations=2)
        lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
        sz = ndimage.sum(m, lbl, range(1, n + 1))
        return np.isin(lbl, [int(np.argmax(sz)) + 1] + [i + 1 for i in range(n) if sz[i] >= 30])

    def old_box(self, tag, k):
        """The old frame's body box from its pivot, in 1x pixels: (left, top, right, bottom); y up negative."""
        fr, _, (pvx, pvy) = self.OLD[tag][k - 1]
        ys, xs = np.nonzero(self.old_body(fr))
        return xs.min() - pvx, ys.min() - pvy, xs.max() + 1 - pvx, ys.max() + 1 - pvy

    # -- Codex's drawings
    def frame_masks(self, s):
        a = np.asarray(Image.open(CS.lp(os.path.join(self.SRC, s["name"] + ".png"))).convert("RGBA"))
        return a, CS.cells(s, CS.figure(a))

    def at_zoom(self, a, m, zoom):
        self.bind()
        ys, xs = np.nonzero(m)
        gh, gw = ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min()
        sq = CS.sample(a, m, round(gh / zoom), round(gw / zoom))
        yy, xx = np.nonzero(sq[..., 3] > 0)
        return sq[yy.min():yy.max() + 1, xx.min():xx.max() + 1]

    def read_all(self):
        """{"<tag>_<frame>": (squares, the old box's middle and bottom from the pivot in design squares, the zoom)}."""
        out = {}
        for s in self.sheets():
            a, ms = self.frame_masks(s)
            for k, m in ms:
                n = f"{s['tag']}_{k}"
                L, T, R, B = self.old_box(s["tag"], k)
                z = self.zoom_of(n, s["name"])
                out[n] = (self.at_zoom(a, m, z), (L + R) / 2 * self.PPU, B * self.PPU, z)
        for tag, m in self.PK.SAME.items():
            for k, src in m.items():
                if src == self.PK.DESIGN:
                    continue
                L, T, R, B = self.old_box(tag, k)
                sq, _, _, z = out[f"{src[0]}_{src[1]}"]
                out[f"{tag}_{k}"] = (sq, (L + R) / 2 * self.PPU, B * self.PPU, z)
        return out

    def placed(self):
        """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)}: the box's middle on the old box's
        middle and its bottom on the old box's bottom, from the design's pivot; nothing under the soles' row; loose
        specks (under 80 squares) off."""
        out = {}
        for n, (sq, mid, bottom, zoom) in self.read_all().items():
            ys, xs = np.nonzero(sq[..., 3] > 0)
            pic = sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            x = int(round(self.PIVOT + mid - pic.shape[1] / 2))
            y = min(int(round(self.GROUND + bottom - pic.shape[0])), self.GROUND - pic.shape[0])
            out[n] = (body_only(pic), x, y)
        return out

    # -- measures
    def fits(self, templates):
        """{"<tag>_<frame>": (zoom, overlap)} from each frame's fit over its template's pale figure
        (casts_khazix_hd.fits)."""
        def small(m):
            hh, ww = m.shape[0] // 3 * 3, m.shape[1] // 3 * 3
            return m[:hh, :ww].reshape(hh // 3, 3, ww // 3, 3).mean((1, 3)) >= 0.5

        def crop(m):
            ys, xs = np.nonzero(m)
            return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

        out, sheet_of = {}, {}
        for s in self.sheets():
            a, ms = self.frame_masks(s)
            t = np.asarray(Image.open(CS.lp(os.path.join(templates, s["name"] + ".png"))).convert("RGB")).astype(int)
            pale = (t.min(-1) >= 165) & (t.min(-1) < 250)
            cw = 1536 // s["cells"]
            sq = self.PK.SQ_OF.get(s["tag"], self.PK.SQ)
            for c, (k, m) in enumerate(ms):
                T = pale.copy()
                T[:, :c * cw] = False
                T[:, (c + 1) * cw:] = False
                T, M = crop(small(T)).astype(float), crop(small(m))
                best = (0.0, 1.0)
                for sc in np.arange(0.78, 1.30, 0.01):
                    cs = np.asarray(Image.fromarray(M.astype(np.uint8) * 255).resize(
                        (max(1, round(M.shape[1] * sc)), max(1, round(M.shape[0] * sc))), Image.NEAREST)) > 127
                    inter = fftconvolve(T, cs[::-1, ::-1].astype(float), mode="full").max()
                    iou = inter / (T.sum() + cs.sum() - inter)
                    if iou > best[0]:
                        best = (iou, sc)
                n = f"{s['tag']}_{k}"
                out[n] = [round(float(sq / best[1]), 2), round(float(best[0]), 2)]
                sheet_of[n] = s["name"]
                print(self.name, s["name"], k, *out[n], flush=True)
        return out, sheet_of

    def heights(self):
        """{"<tag>_<frame>": zoom} from each drawing's box height over the old body's box height in design squares."""
        out = {}
        for s in self.sheets():
            a, ms = self.frame_masks(s)
            for k, m in ms:
                L, T, R, B = self.old_box(s["tag"], k)
                ys = np.nonzero(m.any(1))[0]
                out[f"{s['tag']}_{k}"] = round(float((ys.max() + 1 - ys.min()) / ((B - T) * self.PPU)), 2)
        return out

    def pivot_search(self):
        """(column, overlap): the design's column under the old idle_base's pivot where the design lies best over the
        old silhouette (scaled by PPU, nearest; the soles on the design's ground line)."""
        a = self.PK.idle_sheet()
        h, w = a.shape[:2]
        pvx, pvy = w / 2, h / 2 + self.PK.OLD_SOLES
        k = self.PPU
        big = np.asarray(Image.fromarray(a).resize((round(w * k), round(h * k)), Image.NEAREST))[..., 3] > 0
        D = self.D0[..., 3] > 0
        H, W = D.shape
        top = int(round(self.GROUND - pvy * k))
        best = (0.0, 0)
        for col in range(0, W):
            left = int(round(col - pvx * k))
            can = np.zeros((H + 2 * big.shape[0], W + 2 * big.shape[1]), bool)
            oy, ox = big.shape[0], big.shape[1]
            can[oy + top:oy + top + big.shape[0], ox + left:ox + left + big.shape[1]] = big
            o = can[oy:oy + H, ox:ox + W]
            iou = (o & D).sum() / max(1, (o | D).sum() + (big.sum() - o.sum()))
            if iou > best[0]:
                best = (float(iou), col)
        return best[1], round(best[0], 2)

    def heads(self):
        """{"<tag>_<frame>": [head scale, error, turn]}: the design's head (HEAD_MASK, scaled by s, nearest) placed
        anywhere over each placed frame, its mean squared colour error (a square off the frame or on a hole 300 away)
        found for every place at once by FFT (casts_rengar_hd.match's measure, squared), the best s in 0.80-1.25
        then +-0.02 round it; the death also tried turned a quarter each way. 1.0 is the design's size."""
        self.bind()
        out = {}
        for n, (pic, _, _) in self.placed().items():
            turns = (0, 1, 3) if "dead" in n else (0,)
            best = None
            for turn in turns:
                for sc in np.arange(0.80, 1.251, 0.05):
                    e = head_err(pic, *CS.head_tpl(sc, turn))
                    if best is None or e < best[0]:
                        best = (e, sc, turn)
            e, sc, turn = best
            for s2 in np.arange(sc - 0.04, sc + 0.041, 0.02):
                e2 = head_err(pic, *CS.head_tpl(s2, turn))
                if e2 < e:
                    e, sc = e2, s2
            out[n] = [round(float(sc), 2), round(float(np.sqrt(e)), 1), int(turn)]
            print(self.name, n, *out[n], flush=True)
        return out

    def save(self):
        with open(self.read_json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.data, f, indent=1, sort_keys=True)

    def review(self, out_dir):
        fr = self.placed()
        os.makedirs(out_dir, exist_ok=True)
        D0, G = self.D0, self.GROUND
        tags = sorted({n.rsplit("_", 1)[0] for n in fr}, key=lambda t: self.TAGS.index(t) if t in self.TAGS else 99)
        for t in tags:
            names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
            x0 = min(min(fr[n][1] for n in names), 0) - 2
            x1 = max(max(fr[n][1] + fr[n][0].shape[1] for n in names), D0.shape[1]) + 2
            y0 = min(min(fr[n][2] for n in names), 0) - 2
            y1 = max(G, max(fr[n][2] + fr[n][0].shape[0] for n in names)) + 2
            Z, W, Hh = 2, x1 - x0, y1 - y0
            tiles = [("design", (D0, 0, 0))] + [(n, fr[n]) for n in names]
            can = Image.new("RGB", (len(tiles) * (W * Z + 4), Hh * Z), (40, 40, 40))
            for i, (n, (pic, x, y)) in enumerate(tiles):
                tile = Image.new("RGBA", (W, Hh), (150, 165, 150, 255))
                tile.alpha_composite(Image.fromarray(pic), (x - x0, y - y0))
                can.paste(tile.convert("RGB").resize((W * Z, Hh * Z), Image.NEAREST), (i * (W * Z + 4), 0))
            can.save(os.path.join(out_dir, f"placed_{self.name}_{t}.png"))
        print("written", out_dir)


def head_err(pic, rgb, m):
    """The least mean squared colour error of the template (rgb, mask m) over every place on pic (FFT)."""
    th, tw = m.shape
    H, W = pic.shape[:2]
    pad = np.zeros((H + 2 * th, W + 2 * tw, 4), np.float64)
    pad[th:th + H, tw:tw + W] = pic
    op = (pad[..., 3] > 0).astype(float)
    w = pad[..., :3]
    mf = m.astype(float)[::-1, ::-1]
    t = rgb[::-1, ::-1] * mf[..., None]

    def cv(a, k):
        return fftconvolve(a, k, mode="valid")
    tot = cv(op * (w ** 2).sum(-1), mf)
    for c in range(3):
        tot -= 2 * cv(op * w[..., c], t[..., c])
    tot += cv(op, ((rgb ** 2).sum(-1) * m)[::-1, ::-1])
    tot += 300.0 ** 2 * (m.sum() - cv(op, mf))
    return max(0.0, float(tot.min() / m.sum()))


def body_only(pic):
    """The picture with its loose pieces (8-connected, under 80 squares: stray specks) taken off."""
    lbl, n = ndimage.label(pic[..., 3] > 0, structure=np.ones((3, 3)))
    if n < 2:
        return pic
    sz = ndimage.sum(np.ones(lbl.shape), lbl, range(1, n + 1))
    out = pic.copy()
    out[np.isin(lbl, [i + 1 for i in range(n) if sz[i] < 80])] = 0
    return out


_FORMS = {}


def form(name):
    if name not in _FORMS:
        _FORMS[name] = Form(name)
    return _FORMS[name]


def main(name="kayn"):
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--fits", help="the pack's templates folder: each frame's zoom from its fit, the heights, the pivot")
    ap.add_argument("--heads", action="store_true", help="each placed frame's head against the design's")
    a = ap.parse_args()
    F = form(name)
    F.bind()
    if a.fits:
        fits, sheet_of = F.fits(a.fits)
        col, ov = F.pivot_search()
        F.data.update(fits=fits, sheet_of=sheet_of, heights=F.heights(), pivot=col, pivot_overlap=ov)
        F.save()
        print(name, "pivot", col, "overlap", ov, "->", F.read_json)
        return
    if a.heads:
        F.data["heads"] = F.heads()
        F.save()
        return
    fr = F.placed()
    print(name, "frames", len(fr))
    if a.review:
        F.review(a.review)


if __name__ == "__main__":
    main()
