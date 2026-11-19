"""Writing a dense hero's frames the way its pipeline makes them: hd_ is the master; a 1x frame is
pixel_down.pixelate(hd, 1 / PPU) on the 1x frame (checked 100 % on league_galio / league_xinzhao), a lo_ frame is
ppu_hd.add_lo's own computation (a replica, checked 100 %); the hd strips (assets/source/ppu[/orig]/<hero>_<tag>.png +
.json sizes, 1 px gaps) hold the hd_ frames. New frames go in rects added below the sheet.

    k = Kit(repo, pack, hero)        # hero: 'galio'
    k.cell(tag, i) / k.put(tag, i, pic) / k.add_tag(tag, [(pic, secs)]) / k.derive(tag, i) / k.strip(tag) / k.save()
"""
import json
import os
import sys

import numpy as np
from PIL import Image


class Kit:
    def __init__(self, repo, pack, hero):
        sys.path.insert(0, os.path.join(repo, "tools", "art"))
        import ppu_hd as P
        import pixel_down as D
        self.P, self.D = P, D
        self.repo, self.pack, self.hero = repo, pack, hero
        self.hid = f"{pack}_{hero}"
        self.base = os.path.join(repo, pack, "champions", self.hid)
        self.sheet = np.asarray(Image.open(self.base + "#sheet.png").convert("RGBA")).copy()
        self.anims = json.loads(open(self.base + "#anim.fanim", "rb").read().decode("utf-8-sig"))["anims"]
        self.ppu = P.PPU[hero]
        self.size = D.sizes_of().get(hero, 1.0)
        self.extra = []                      # (tag, i, pic) waiting for rects below the sheet

    def rect(self, tag, i):
        d = self.anims[tag]["frames"][i]["data"]
        return tuple(int(round(d[q])) for q in ("x", "y", "w", "h"))

    def cell(self, tag, i):
        x, y, w, h = self.rect(tag, i)
        return self.sheet[y:y + h, x:x + w].copy()

    def put(self, tag, i, pic):
        """pic into frame i's rect when it fits it, else a rect of its own below the sheet."""
        x, y, w, h = self.rect(tag, i)
        if pic.shape[:2] == (h, w):
            self.sheet[y:y + h, x:x + w] = pic
        else:
            self.extra.append((tag, i, pic))

    def _place(self, lo, px, py, H, W):
        f = np.zeros((H, W, 4), np.uint8)
        ox, oy = int(np.floor(W / 2 - px + 0.5)), int(np.floor(H / 2 - py + 0.5))
        ys, xs = np.nonzero(lo[..., 3] > 0)
        ok = (ys + oy >= 0) & (ys + oy < H) & (xs + ox >= 0) & (xs + ox < W)
        f[ys[ok] + oy, xs[ok] + ox] = lo[ys[ok], xs[ok]]
        return f

    def one_of(self, one_shape, b):
        D = self.D
        lo, (px, py) = D.pixelate(b, 1 / self.ppu, (b.shape[1] / 2, b.shape[0] / 2), D.edge_colour(b))
        return self._place(lo, px, py, one_shape[0], one_shape[1])

    def lo_of(self, one_shape, b):
        P, D = self.P, self.D
        outline = D.edge_colour(b) if (b[..., 3] > 0).any() else (0, 0, 0)
        f_ = P.UI_PPU * self.size / self.ppu
        if f_ > 1:
            lo, (px, py) = P.grow(b, f_, (b.shape[1] / 2, b.shape[0] / 2))
        else:
            lo, (px, py) = D.pixelate(b, f_, (b.shape[1] / 2, b.shape[0] / 2), outline)
        W, H = P.lo_size(one_shape[1], one_shape[0])
        ys, xs = np.nonzero(lo[..., 3] > 0)
        while W / 2 < max(px - xs.min(), xs.max() + 1 - px):
            W += 2
        while H / 2 < max(py - ys.min(), ys.max() + 1 - py):
            H += 2
        return self._place(lo, px, py, H, W)

    def derive(self, tag, i):
        """The 1x and lo_ frame i of a plain tag from its hd_ frame (as the sheet holds it now)."""
        hd = self.cell("hd_" + tag, i)
        one_shape = self.cell(tag, i).shape
        self.put(tag, i, self.one_of(one_shape, hd))
        self.put("lo_" + tag, i, self.lo_of(one_shape, hd))

    def add_tag(self, tag, frames, one_shape):
        """A new plain tag + hd_ / lo_ copies from hd pictures [(pic, secs)]; one_shape: the 1x frames' (h, w) - the
        frame they stand for (the idle's), so hd = PPU x 1x as ppu_hd.check wants."""
        n = len(frames)
        for pre in ("hd_", "", "lo_"):
            self.anims[pre + tag] = {"frames": [{"duration": round(s, 6), "data": {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}}
                                                for _, s in frames]}
        for i, (pic, _) in enumerate(frames):
            self.extra.append(("hd_" + tag, i, pic))
            self.extra.append((tag, i, self.one_of(one_shape[:2], pic)))
            self.extra.append(("lo_" + tag, i, self.lo_of(one_shape[:2], pic)))

    def strip(self, tag, pics=None):
        """The hd strip of a tag (main and orig/) rewritten from the sheet's hd_ frames (or pics)."""
        pics = pics if pics is not None else [self.cell("hd_" + tag, i) for i in range(len(self.anims["hd_" + tag]["frames"]))]
        H = max(p.shape[0] for p in pics)
        W = sum(p.shape[1] for p in pics) + len(pics) - 1
        st = np.zeros((H, W, 4), np.uint8)
        x = 0
        for p in pics:
            st[:p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1] + 1
        for sub in ("", "orig"):
            d = os.path.join(self.repo, "assets", "source", "ppu", sub)
            js = os.path.join(d, f"{self.hero}_{tag}.json")
            meta = json.load(open(js)) if os.path.isfile(js) else {}
            meta["sizes"] = [[p.shape[1], p.shape[0]] for p in pics]
            if sub == "orig":
                meta.setdefault("ppu", self.ppu)
            Image.fromarray(st).save(os.path.join(d, f"{self.hero}_{tag}.png"))
            json.dump(meta, open(js, "w"))

    def save(self):
        if self.extra:
            top = self.sheet.shape[0] + 1
            rows, x, y, rh = [], 0, top, 0
            W = self.sheet.shape[1]
            place = []
            for tag, i, pic in self.extra:
                if x + pic.shape[1] > W:
                    x, y, rh = 0, y + rh + 1, 0
                place.append((tag, i, pic, x, y))
                x += pic.shape[1] + 1
                rh = max(rh, pic.shape[0])
            H = y + rh
            big = np.zeros((H, W, 4), np.uint8)
            big[:self.sheet.shape[0]] = self.sheet
            for tag, i, pic, x, y in place:
                big[y:y + pic.shape[0], x:x + pic.shape[1]] = pic
                self.anims[tag]["frames"][i]["data"] = {"x": float(x), "y": float(y), "w": float(pic.shape[1]), "h": float(pic.shape[0])}
            self.sheet = big
            self.extra = []
        Image.fromarray(self.sheet).save(self.base + "#sheet.png")
        open(self.base + "#anim.fanim", "wb").write(json.dumps({"anims": self.anims}, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
