#!/usr/bin/env python3
"""Daisy as a unit of her own: league/champions/league_ivern_daisy#sheet.png + #anim.fanim.

    python tools/art/unit_ivern_daisy.py [--check] [--preview <png>]

The add-on league_ivern spawns Daisy through the mod API's spawn_unit under the name league_ivern_daisy; the game draws a
unit of that name from asset/base/aseprite_resources/champions/league_ivern_daisy (the add-on's mod.override_info sends
that here) with the tags a champion has. The engine's own summons (base `ghoul`) carry idle, run, attack, hit and dead,
so those five, each twice: the 1x frame (a square a game pixel) and its dense `hd_` twin at PPU 1.333 - the scale of the
four effect sheets she is drawn from today (league_ivern_daisy_drop / _punch / _bye, tools/art/rig_ivern.py; league.dll
hd.rs EFFECTS + DRAWN_EFFECTS draw them dense, 57 game px from her sprout to her feet). Until league.dll registers this
sheet the game draws the 1x frames: the same size, a square a game pixel.

  idle    her standing frame (the drop's last) four times, the last two everything above her shins a pixel lower;
  attack  her punch as rig_ivern drew it - the punch sheet's first four frames (wind, punch, hold) - 0.7 s; the fist
          lands 0.35 s in (the kit's r_hit_at, 21 ticks: the add-on's unit attack lands at tick 21 of 42);
  run     no such drawing exists: four frames made here from the standing frame by whole-pixel moves - seen from the
          front, she sinks a row on both feet, then lifts one shin (two game px; three dense px) and leans her body a
          pixel over the other leg, sinks again, lifts the other one; the outline is closed again where a move opened it;
  hit     the standing frame, everything above her shins a pixel higher;
  dead    her wave and sinking into the ground (the four frames of the bye sheet) and an empty frame, as base's dead
          tags end.

Every frame is the effect sheets' own pixels, moved 9 game px down (12 dense px): on the effects her feet stand
DAISY_BACK (9) game px behind the champion she rides on, 2 under the frame's centre; a unit's are FEET (11) under it like
every hero's. --check: exit 1 when the sheet in the repo is not what this writes. --preview: the frames at 6x / 4.5x on
their ground line.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "league", "effects", "league_ivern_daisy_")
OUT = os.path.join(ROOT, "league", "champions", "league_ivern_daisy")
D_PPU = 1.333               # rig_ivern.py's: her dense frames are this many pixels a game pixel
FEET = 11                   # a unit's soles: this many game px under the pivot
BACK = 9                    # rig_ivern.py DAISY_BACK: her soles on the effects are FEET - BACK game px under the pivot


class Scale:
    """One of the two frame sizes: the 1x frames (tag `idle` of the effect sheets) or the dense ones (`hd_idle`)."""

    def __init__(self, tag, ppu, canvas, knee, leg_mid, lift, sway):
        self.tag, self.ppu, self.S = tag, ppu, canvas
        self.C = canvas // 2
        self.down = int(round(BACK * ppu))        # 9 game px: 9 rows at 1x, 12 dense
        self.feet = int(round(FEET * ppu))
        # her shins on the standing frame (rows from the pivot, as on the effect sheet): from `knee` down, on each row
        # the runs of pixels that reach into the leg's middle columns `leg_mid` (left, right) - the fists hang beside them
        # on the same rows and never reach that far in
        self.knee, self.leg_mid = knee, leg_mid
        self.lift, self.sway = lift, sway

    def frames(self, sheet_tag):
        sheet = np.array(Image.open(G.lp(SRC + sheet_tag + "#sheet.png")).convert("RGBA"))
        with open(G.lp(SRC + sheet_tag + "#anim.fanim"), encoding="utf-8-sig") as fh:
            anim = json.load(fh)["anims"]
        out = []
        for f in anim[self.tag]["frames"]:
            d = f["data"]
            x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
            c = np.zeros((self.S, self.S, 4), np.uint8)
            cx, cy = (w - 1) // 2, (h - 1) // 2
            top, left = self.C - cy + self.down, self.C - cx
            c[top:top + h, left:left + w] = sheet[y:y + h, x:x + w]
            out.append(c)
        return out

    def shins(self, stand):
        """(left shin, right shin) masks of the standing frame, checked against its pixels"""
        op = stand[..., 3] > 0
        masks = []
        for lo, hi in self.leg_mid:
            m = np.zeros_like(op)
            for r in range(self.knee, self.S - self.C - self.down):
                row = self.C + self.down + r
                xs = np.nonzero(op[row])[0]
                runs = []
                for c in xs:
                    if runs and c == runs[-1][1] + 1:
                        runs[-1][1] = c
                    else:
                        runs.append([c, c])
                for a, b in runs:
                    if a - self.C <= hi and b - self.C >= lo:
                        m[row, a:b + 1] = True
            masks.append(m)
        left, right = masks
        if (left & right).any() or not left.any() or not right.any():
            sys.exit("%s: the shins of the standing frame are not two apart: read the frame again" % self.tag)
        # nothing but the shins and the two fists from the knee row down: the fists are wider out than either shin
        rows = np.arange(self.S)[:, None] - self.C - self.down + np.zeros((1, self.S), int)
        cols = np.arange(self.S)[None, :] - self.C + np.zeros((self.S, 1), int)
        rest = op & (rows >= self.knee) & ~left & ~right
        lmin = cols[left].min()
        rmax = cols[right].max()
        if (rest & (cols > lmin) & (cols < rmax)).any():
            sys.exit("%s: pixels between her shins that are no shin: read the frame again" % self.tag)
        return left, right


def cut(f, mask):
    p = np.zeros_like(f)
    p[mask] = f[mask]
    return p


def shift(part, dx, dy):
    out = np.zeros_like(part)
    h, w = part.shape[:2]
    ys, xs = np.nonzero(part[..., 3])
    out[np.clip(ys + dy, 0, h - 1), np.clip(xs + dx, 0, w - 1)] = part[ys, xs]
    return out


def over(under, top):
    out = under.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def close(sc, f, open_=None, dx=0, dy=0):
    """the outline closed where a move opened it; light pixels on the ground row stay as drawn, and so do the few spots
    the drawing itself leaves open (`open_`: the standing frame's, carried with her body's move dx, dy)"""
    rows = np.arange(sc.S)[:, None] - sc.C + np.zeros((1, sc.S), int)
    light = (f[..., 3] > 0) & (G.lum(f[..., :3]) >= 70)
    keep = light & (rows >= sc.feet)
    if open_ is not None:
        ys, xs = np.nonzero(open_)
        keep[np.clip(ys + dy, 0, sc.S - 1), np.clip(xs + dx, 0, sc.S - 1)] = True
    out, added, darkened = G.complete_outline(f, feet=sc.C + sc.feet, keep=keep)
    return out, added + darkened


def drawn_open(sc, stand):
    """the spots the outline pass would change on the standing frame as drawn (a petal, the sprout): left as they are
    in every frame made from it; a handful at most, or the frame was read wrong"""
    out, _ = close(sc, stand)
    spots = (out != stand).any(-1)
    if spots.sum() > 8:
        sys.exit("%s: the standing frame's outline is open in %d places: read the frame again" % (sc.tag, spots.sum()))
    return spots


def body_of(stand, left, right):
    return cut(stand, (stand[..., 3] > 0) & ~left & ~right)


def run_frame(sc, stand, k):
    """frame k (0-3) of the waddle seen from the front"""
    left, right = sc.shins(stand)
    body = body_of(stand, left, right)
    lift = [(0, 0), (sc.lift, 0), (0, 0), (0, sc.lift)][k]       # rows each shin is lifted
    sink = 1 if k in (0, 2) else 0                                # both feet down: the knees give a row
    lean = [0, sc.sway, 0, -sc.sway][k]                           # her weight over the standing leg
    f = np.zeros_like(stand)
    for shin, up in ((cut(stand, right), lift[1]), (cut(stand, left), lift[0])):
        f = over(f, shift(shin, 0, -up))
    f = over(f, shift(body, lean, sink))
    f[sc.C + sc.feet + 1:] = 0                                    # nothing under the ground row
    return close(sc, f, drawn_open(sc, stand), lean, sink)


def idle_frame(sc, stand, k):
    if k < 2:
        return stand
    left, right = sc.shins(stand)
    return over(cut(stand, left | right), shift(body_of(stand, left, right), 0, 1))


def hit_frame(sc, stand):
    left, right = sc.shins(stand)
    return close(sc, over(cut(stand, left | right), shift(body_of(stand, left, right), 0, -1)), drawn_open(sc, stand), 0, -1)


IDLE_MS = 160
RUN_MS = 120
HIT_MS = 100


def build():
    # (frame tag, canvas, the knee row, the shins' middle columns, a lifted shin's rows, the lean's columns)
    scales = [Scale("idle", 1, 200, -5, ((-15, -4), (4, 15)), 2, 1),
              Scale("hd_idle", D_PPU, 270, -7, ((-20, -5), (5, 20)), 3, 1)]
    tags, report = {}, []
    for sc in scales:
        pre = "" if sc.ppu == 1 else "hd_"
        stand = sc.frames("drop")[-1]
        drawn_open(sc, stand)
        run = []
        for k in range(4):
            f, fixed = run_frame(sc, stand, k)
            report.append(("%srun %d" % (pre, k), fixed))
            run.append((f, RUN_MS))
        hit, fixed = hit_frame(sc, stand)
        report.append(("%shit" % pre, fixed))
        punch = sc.frames("punch")
        bye = sc.frames("bye")
        with open(G.lp(SRC + "punch#anim.fanim"), encoding="utf-8-sig") as fh:
            punch_ms = [round(f["duration"] * 1000) for f in json.load(fh)["anims"][sc.tag]["frames"]]
        with open(G.lp(SRC + "bye#anim.fanim"), encoding="utf-8-sig") as fh:
            bye_ms = [round(f["duration"] * 1000) for f in json.load(fh)["anims"][sc.tag]["frames"]]
        blank = np.zeros((sc.S, sc.S, 4), np.uint8)
        tags[pre + "idle"] = [(idle_frame(sc, stand, k), IDLE_MS) for k in range(4)]
        tags[pre + "run"] = run
        tags[pre + "attack"] = list(zip(punch[:4], punch_ms[:4]))
        tags[pre + "hit"] = [(hit, HIT_MS)]
        tags[pre + "dead"] = list(zip(bye, bye_ms)) + [(blank, 100)]
    # the 1x tags first, then their hd_ twins (a hero sheet's order)
    order = ["idle", "run", "attack", "hit", "dead"]
    return {t: tags[t] for t in order + ["hd_" + t for t in order]}, report, scales


def centred(tags, scales):
    out = {}
    for tag, frames in tags.items():
        sc = scales[1] if tag.startswith("hd_") else scales[0]
        out[tag] = [(G.centre_frame(f, -sc.C, -sc.C) if f[..., 3].any() else np.zeros((3, 3, 4), np.uint8), ms)
                    for f, ms in frames]
    return out


def preview(tags, scales, path):
    cells = [(tag, i, f) for tag, frames in tags.items() for i, (f, _) in enumerate(frames)]
    per_row = 6
    W, H = 6 * 80, 6 * 90 + 14
    rows = (len(cells) + per_row - 1) // per_row
    img = Image.new("RGBA", (per_row * W, rows * H), (58, 70, 58, 255))
    dr = ImageDraw.Draw(img)
    for n, (tag, i, f) in enumerate(cells):
        sc = scales[1] if tag.startswith("hd_") else scales[0]
        z = 6 / sc.ppu
        ox, oy = (n % per_row) * W, (n // per_row) * H + 14
        half_w, up, down = int(38 * sc.ppu), int(76 * sc.ppu), int(13 * sc.ppu)
        crop = Image.fromarray(f[sc.C - up:sc.C + down + 1, sc.C - half_w:sc.C + half_w + 1], "RGBA")
        img.alpha_composite(crop.resize((int(crop.width * z), int(crop.height * z)), Image.NEAREST), (ox, oy))
        gy = oy + int((up + sc.feet + 1) * z)
        dr.line([(ox, gy), (ox + W - 2, gy)], fill=(0, 255, 255, 255))
        dr.text((ox + 3, oy - 13), "%s %d" % (tag, i), fill=(255, 255, 0, 255))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview")
    a = ap.parse_args()
    tags, report, scales = build()
    if a.preview:
        preview(tags, scales, a.preview)
        print("preview", a.preview)
    out = centred(tags, scales)
    if a.check:
        import tempfile
        tmp = os.path.join(tempfile.mkdtemp(prefix="daisy_"), "league_ivern_daisy")
        G.write_sheet(tmp, out)

        def read(stem):
            with open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig") as fh:
                return np.array(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA")), json.load(fh)

        same = False
        if os.path.exists(G.lp(OUT + "#sheet.png")) and os.path.exists(G.lp(OUT + "#anim.fanim")):
            (px, an), (px2, an2) = read(OUT), read(tmp)
            same = an == an2 and px.shape == px2.shape and bool((px == px2).all())
        print("league_ivern_daisy:", "up to date" if same else "stale")
        sys.exit(0 if same else 1)
    w, h = G.write_sheet(OUT, out)
    print("wrote %s#sheet.png (%d x %d) and #anim.fanim: %s" % (
        os.path.relpath(OUT, ROOT), w, h, ", ".join("%s %d frames %.2f s" % (t, len(fr), sum(ms for _, ms in fr) / 1000.0)
                                                    for t, fr in out.items())))
    print("outline pixels closed after the moves: " + ", ".join("%s %d" % r for r in report))


if __name__ == "__main__":
    main()
