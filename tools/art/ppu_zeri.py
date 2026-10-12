#!/usr/bin/env python3
"""Zeri's dense frames (PPU 3): assets/source/ppu/zeri_<tag>.png, the drawn strips tools/art/ppu_hd.py (branch ppu)
puts in as the `hd_<tag>` tags of her sheet.

    python tools/art/ppu_zeri.py                  # write the strips (after tools/art/import_native.py --hero zeri)
    python tools/art/ppu_zeri.py --check          # compare with the written strips
    python tools/art/ppu_zeri.py --review DIR     # zeri_hd_frames.png and zeri_hd_actions.gif

The user, 2026-10-12: 「用PPU的方法重做泽丽 刀妹亚索都重做了」, PPU 3 in the picture's own proportions. Every frame is
posed from the dense design (tools/art/design_zeri_hd.py: ppu3/idle.txt, Codex's picture A read on 120 rows with the face
drawn square by square; ppu3/level.txt, picture B's body with the rifle level in both hands under the same head), the
way tools/art/rig_zeri.py poses the 1x frames, three times as fine: the same actions, timing and standing point.
An hd frame is three times its 1x frame round the same centre (the canvas point (64, 88): hd canvas pixel (3x + i, 3y + j)
lies in 1x pixel (x, y)), so it shows the same size in game at three times the density; nothing may stand outside it.
"""
import argparse
import colorsys
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_zeri_hd as D  # noqa: E402
import rigkit as K  # noqa: E402
import strips as G  # noqa: E402

PPU = 3
OUT = os.path.join(ROOT, "assets", "source", "ppu")
STEM = os.path.join(ROOT, "league", "champions", "league_zeri")
CENTRE = (64, 88)
SIZE = 128 * PPU
SOLES = PPU * 99 + PPU - 1                 # the soles' row on the hd canvas (the 1x soles row 99)
TOP = SOLES - (D.ROWS - 1)                 # the tables' row 0
X0 = {"idle": 163, "level": 162}           # the tables' column 0: the feet's middle on the 1x column 63 (the level
                                           # table's head is one column right in it)
SPLIT = 74                                 # table rows from here down are the legs (columns from LEG_COL on)
LEG_COL = 12
LEG_ALL = 75                               # table rows from here down are the legs in every column (the coat's panels
                                           # end above it; left of LEG_COL the near shin and boot sank with the breath)
BREATH = [0, 1, 3, 3, 3, 3, 2, 1]          # hd rows the upper body sinks in the idle (the 1x frames 3-6 a row down)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_back", "ult", "hit", "dead"]
SCALE = 1.10                               # league.dll draws her this much bigger, about her pivot (addons/league_main
                                           # hd.rs SIZES; the user: 「等等泽丽感觉游戏里有点小」, 105% from the size sheet;
                                           # then 「感觉泽丽可以略微放大一点吧」「太小了点」, 110% from the next one)
RAISE = round(34.5 * (1 - 1 / SCALE))      # so every frame is drawn this many hd rows higher and the soles stay on the
                                           # ground (34.5: the soles' bottom edge under the frame's centre, 11.5 1x px)
STRIP_SCALE = 1.10                         # the SCALE the written run strip was made at (read back without the renders,
                                           # it is lowered by that one's RAISE; set it to SCALE after a size change)
STRIP_RAISE = round(34.5 * (1 - 1 / STRIP_SCALE))

# the run, League's (「跑步全部重画 还原LOL的」「不要腿部有任何变形」「你不会自己做一个自然一点的？」): the legs are
# League's own legs in its run, every frame - rendered from League's model nearly from the side with the coat, the
# backpack and the rifle left out (RUN_SPEC; tools/lol/native_pose.py --alpha --parts, the near and the far leg painted
# apart; tools/lol/pose_joints.py --json for the hips and knees), at the design's leg length (League's hips 45 hd squares
# over the soles, as the design's are), so a knee bends, a calf swells and a boot points as the 3D leg does - and drawn
# in the design's own colours square by square: every 8x8 block of the render is one hd square, voting by material (the
# leggings' two shades by brightness, the boots' brown ramp, the sock's orange and yellow, the buckles' greys), a
# speckle with four neighbours of one other colour taking theirs, a square thicker all round (the design's legs are
# fuller than League's), one outline ring; the design's knee pad on the near knee; the far leg (League's left) a shade
# darker. The upper body is picture B's - the rifle level in both hands, as League's Zeri runs - leant forward on an even
# line (two squares every three rows up from the hips, the band of the rifle and both hands one block, the head one
# block: RUN_LEAN), never resampled, its hips on League's hips. Without the renders (they show Riot's model and stay
# local) the run is read back from the written strip.
RUN_SPEC = os.path.join(ROOT, "assets", "source", "zeri", "ppu3", "run_legs.json")
RUN_HIP_ROW = 69                  # level-table row: the coat's hem; below it only the coat's two panels stay
RUN_PANELS = [(0, 12), (40, 66)]  # level-table columns of the coat's panels kept under RUN_HIP_ROW (to row 73)
RUN_BAND = (44, 54)               # level-table rows of the rifle and both hands: moved as one block
RUN_LEAN = 28                     # most hd squares a row goes ahead of the hips
RUN_SLOPE = (2, 3)                # the lean: this many squares forward every this many rows up (League leans 40-50 deg)
RUN_HEAD_LOW = 33                 # level-table row: the chin; the head above it moves as one block
RUN_HIPS = (64, 30)               # level-table row and column of the hips' middle (put on League's)
RUN_PIVOT = 190                   # hd column of the render's standing point
KNEE_PAD = (75, 82, 12, 20)       # idle-table box of the near knee's pad (its tan squares)
RUN_HIP_R, RUN_HIP_FILL = 5.5, 9  # the hip's disc radius, rows under the hip where the thigh's outline is closed round
LEG_LIT, LEG_DARK = (131, 51, 86), (99, 37, 71)          # the design's leggings
FAR_SHADE = 0.72                  # the far leg and boot: every colour this much darker
SHIN_LOW = 90                     # idle-table row: the shins' last row above the boots (the kneel takes rows out up from it)
LYING = (46, 94)                  # the 1x lying frames' columns (rig_zeri.lying with the rifle beside her)


def table(name):
    pal = D.load_palette()
    return D.to_rgba(D.read_table(os.path.join(D.OUT, name + ".txt")), pal)


def on_canvas(a, x0, y0=TOP):
    c = np.zeros((SIZE, SIZE, 4), np.uint8)
    K.put(c, a, x0, y0)
    return c


class Rig:
    def __init__(self, renders=None):
        self.renders = renders                   # League's legs-only run renders (RUN_SPEC), or None: the strip
        self.out = D.OUTLINE
        self.parts = {}
        for name in ("idle", "level"):
            a = table(name)
            legs = np.zeros(a.shape[:2], bool)
            legs[SPLIT:, LEG_COL:] = True
            legs[LEG_ALL:] = True
            legs &= a[..., 3] > 0
            up = a.copy()
            up[legs] = 0
            lo = a.copy()
            lo[~legs] = 0
            self.parts[name] = (on_canvas(up, X0[name]), on_canvas(lo, X0[name]))

    def pose(self, rifle="up", dx=0, dy=0, low=0):
        """The design (rifle 'up': picture A; 'level': picture B) with the upper body `low` hd rows down over the
        legs, moved dx, dy hd pixels."""
        up, lo = self.parts["idle" if rifle == "up" else "level"]
        c = lo.copy()
        K.put(c, up, 0, low)
        return K.shifted(c, dx, dy)

    # ------------------------------------------------------------------------------------------------ the run
    def run_shift(self, r):
        """hd squares a level-table row moves forward in the lean: one square every two rows up from the hips, the band
        of the rifle and both hands as one block by its middle row's amount, the head by its lowest row's."""
        b0, b1 = RUN_BAND
        even = lambda q: ((RUN_HIP_ROW - q) * RUN_SLOPE[0] + RUN_SLOPE[1] - 1) // RUN_SLOPE[1] if q < RUN_HIP_ROW else 0
        if b0 <= r <= b1:
            return even((b0 + b1) // 2)
        return min(RUN_LEAN, even(max(r, RUN_HEAD_LOW)))

    def run_upper(self):
        if getattr(self, "_upper", None) is not None:
            return self._upper
        a = table("level")
        keep = np.zeros(a.shape[:2], bool)
        keep[:RUN_HIP_ROW] = True
        for c0, c1 in RUN_PANELS:
            keep[RUN_HIP_ROW:SPLIT + 1, c0:c1 + 1] = True
        a = np.where(keep[..., None], a, 0).astype(np.uint8)
        a = np.pad(a, ((0, 0), (0, RUN_LEAN + 2), (0, 0)))      # room on the right: a row moved on must not wrap round
        up = np.zeros_like(a)
        for r in range(a.shape[0]):
            s = self.run_shift(r)
            up[r] = np.roll(a[r], s, 0) if s else a[r]
        self._upper = on_canvas(up, X0["level"])
        return self._upper

    def knee_pad(self):
        a = table("idle")
        y0, y1, x0, x1 = KNEE_PAD
        box = a[y0:y1 + 1, x0:x1 + 1].copy()
        tan = np.array([[tuple(q[:3]) not in (LEG_LIT, LEG_DARK, D.OUTLINE) and q[3] > 0 for q in row] for row in box])
        box[~tan] = 0
        ys, xs = np.nonzero(box[..., 3])
        return K.Part(box, ((xs.min() + xs.max() + 1) / 2.0, (ys.min() + ys.max() + 1) / 2.0))

    def material(self, px):
        """A League leg pixel -> the design's colour: leggings, boot, sock or buckle."""
        h, s_, v = colorsys.rgb_to_hsv(*(px[:3] / 255.0))
        h *= 360
        P_ = self.pal
        if s_ < 0.18:
            return (P_["i"], P_["n"], P_["s"], P_["w"])[min(3, int((v - 0.3) / 0.08))] if v > 0.3 else LEG_DARK
        if (h <= 45 or h >= 350) and s_ > 0.3 and v > 0.2:
            if 22 <= h <= 45 and s_ > 0.6 and v > 0.5:
                return P_["l"] if v < 0.62 else P_["p"]
            return P_["a"] if v < 0.28 else P_["e"] if v < 0.42 else P_["h"] if v < 0.55 else P_["m"]
        return LEG_DARK if v < 0.17 else LEG_LIT

    def run_from_renders(self, renders):
        """The eight run frames from League's legs (see the run's comment)."""
        spec = json.load(open(RUN_SPEC, encoding="utf-8"))
        cw, ch, _ = spec["cell"]
        z = 8
        pose = np.asarray(Image.open(os.path.join(renders, "zeri_pose_run.png")).convert("RGBA"))
        parts = np.asarray(Image.open(os.path.join(renders, "zeri_parts_run.png")).convert("RGBA")).astype(int)
        cells = json.load(open(os.path.join(renders, "zeri_cells.json")))["tags"]["run"]
        joints = json.load(open(os.path.join(renders, "joints_run.json")))
        self.pal = dict(zip(json.load(open(os.path.join(D.OUT, "palette.json")))["letters"], D.load_palette()))
        pad = self.knee_pad()
        upper = self.run_upper()
        ink = np.array(D.OUTLINE, np.uint8)
        frames = []
        for k in range(8):
            cx0, cy0 = (k % 4) * cw * z, (k // 4) * ch * z
            cp = pose[cy0:cy0 + ch * z, cx0:cx0 + cw * z]
            pp = parts[cy0:cy0 + ch * z, cx0:cx0 + cw * z]
            opq = cp[..., 3] > 128
            masks = {"far": opq & (pp[..., 0] < 60) & (pp[..., 1] > 100) & (pp[..., 2] > 100),
                     "near": opq & (pp[..., 0] > 100) & (pp[..., 1] < 60) & (pp[..., 2] > 100)}
            px_, py_ = cells[k]["pivot"]
            j = joints[k]["joints"]
            legs = {}
            for name, m in masks.items():
                side = "R" if name == "near" else "L"
                hipx, hipy = RUN_PIVOT + j[side + "_Hip"][0], SOLES - 12 + j[side + "_Hip"][1]
                kneey = SOLES - 12 + j[side + "_KneeLower"][1]
                g = np.zeros((SIZE, SIZE, 4), np.uint8)
                for by in range(ch):
                    for bx in range(cw):
                        blk = m[by * z:(by + 1) * z, bx * z:(bx + 1) * z]
                        if blk.sum() < z * z // 2:
                            continue
                        votes = {}
                        for q in cp[by * z:(by + 1) * z, bx * z:(bx + 1) * z][blk][::3]:
                            c = self.material(q.astype(float))
                            votes[c] = votes.get(c, 0) + 1
                        # a row up: the outline under the soles goes on the soles' row (restyle_native's way)
                        X, Y = RUN_PIVOT + bx - px_, SOLES - 1 + by - (py_ + 11)
                        if 0 <= X < SIZE and 0 <= Y < SOLES:
                            c = max(votes, key=votes.get)
                            if Y < kneey and c not in (LEG_LIT, LEG_DARK):
                                c = LEG_LIT                      # above the knee only the leggings (a strap's glint)
                            g[Y, X] = (*c, 255)
                # the thigh full from the hip: League's leg narrows where it meets the pelvis and, cut there, showed a
                # neck under the coat's panel (「这里有点变形」): a disc round the hip, the thigh's top closed round it
                # (filled across row by row it made a corner)
                yy, xx = np.ogrid[:SIZE, :SIZE]
                disc = ((xx - hipx) ** 2 + (yy - hipy) ** 2 <= RUN_HIP_R ** 2) & (yy >= hipy - 2)
                top = np.zeros(g.shape[:2], bool)
                top[int(hipy) - 3:int(hipy) + RUN_HIP_FILL] = True
                m_ = (g[..., 3] > 0) | disc
                closed = ndimage.binary_closing(m_, structure=np.ones((5, 5)), iterations=1) & top
                g[(disc | closed) & (g[..., 3] == 0)] = (*LEG_LIT, 255)
                for _ in range(2):                      # speckles
                    op = g[..., 3] > 0
                    for y, x in list(zip(*np.nonzero(op))):
                        nb = [tuple(g[y + a, x + b, :3]) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)) if g[y + a, x + b, 3]]
                        if len(nb) == 4 and len(set(nb)) == 1 and nb[0] != tuple(g[y, x, :3]):
                            g[y, x, :3] = nb[0]
                op = g[..., 3] > 0                       # a square thicker all round, the edge's own colour (not
                grow = ndimage.binary_dilation(op) & ~op  # onto the soles' row: the outline goes there)
                grow[SOLES:] = False
                for y, x in zip(*np.nonzero(grow)):
                    nb = [(y + a, x + b) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)) if op[y + a, x + b]]
                    g[y, x] = g[nb[0]]
                if name == "near":                       # the design's knee pad on League's near knee
                    tmp = np.zeros_like(g)
                    K.place(tmp, pad, (RUN_PIVOT + j["R_KneeLower"][0] + 1.0, SOLES - 12 + j["R_KneeLower"][1]))
                    sel = (tmp[..., 3] > 0) & (g[..., 3] > 0)
                    g[sel] = tmp[sel]
                m2 = g[..., 3] > 0
                p = np.pad(m2, 1)
                g[~m2 & (p[2:, 1:-1] | p[:-2, 1:-1] | p[1:-1, 2:] | p[1:-1, :-2])] = (*D.OUTLINE, 255)
                if name == "far":
                    col = (g[..., 3] > 0) & ~(g[..., :3] == ink).all(-1)
                    g[col, :3] = (g[col, :3].astype(float) * FAR_SHADE).astype(np.uint8)
                legs[name] = g
            c = np.zeros((SIZE, SIZE, 4), np.uint8)
            K.put(c, legs["far"], 0, 0)
            K.put(c, legs["near"], 0, 0)
            hx, hy = (j["L_Hip"][0] + j["R_Hip"][0]) / 2, (j["L_Hip"][1] + j["R_Hip"][1]) / 2
            dx = int(round(RUN_PIVOT + hx - (X0["level"] + RUN_HIPS[1])))
            dy = int(round(SOLES - 12 + hy - (TOP + RUN_HIPS[0])))
            K.put(c, K.shifted(upper, dx, dy), 0, 0)
            c[SOLES + 1:] = 0
            frames.append(c)
        sizes = sheet_sizes()["run"]
        for k, (w, h) in enumerate(sizes):           # a flight frame leaving its box comes down until it fits
            while cut(frames[k], w, h)[1]:
                frames[k] = K.shifted(frames[k], 0, 1)
                frames[k][SOLES + 1:] = 0
        return self.finished(frames)

    def run_from_strip(self):
        """The written run strip back on the canvas (the renders are not here)."""
        s = np.asarray(Image.open(os.path.join(OUT, "zeri_run.png")).convert("RGBA"))
        frames, x = [], 0
        for w, h in sheet_sizes()["run"]:
            c = np.zeros((SIZE, SIZE, 4), np.uint8)
            x0, y0 = CENTRE[0] - (w - 1) // 2, CENTRE[1] - (h - 1) // 2
            c[PPU * y0:PPU * y0 + PPU * h, PPU * x0:PPU * x0 + PPU * w] = s[:PPU * h, x:x + PPU * w]
            frames.append(K.shifted(c, 0, STRIP_RAISE))  # back down: raised() lifts every frame again
            x += PPU * w + 1
        return frames

    def run_frame(self, k):
        if getattr(self, "_run", None) is None:
            self._run = self.run_from_renders(self.renders) if self.renders else self.run_from_strip()
        return self._run[k].copy()

    # ------------------------------------------------------------------------------------------------ the death
    def kneel(self, n, dx=0):
        """Sinking to her knees (rig_zeri.kneel): n hd rows of the shins out, the boots kept, all above down n."""
        up, lo = self.parts["idle"]
        r_hi = TOP + SHIN_LOW
        cut0 = r_hi - n + 1
        top = lo.copy()
        top[cut0:] = 0
        boots = lo.copy()
        boots[:r_hi + 1] = 0
        c = boots.copy()
        K.put(c, top, 0, n)
        K.put(c, up, 0, n)
        return K.shifted(c, dx, 0)

    def lying(self):
        """Down on her face (rig_zeri.lying): the design a quarter turn clockwise, its soles' side back, lying on the
        ground where the 1x figure lies (LYING: its 1x columns), the rifle still in her hand."""
        a = table("idle")
        turned = np.rot90(a, -1)
        c = np.zeros((SIZE, SIZE, 4), np.uint8)
        x0 = (PPU * LYING[0] + PPU * LYING[1] + PPU - turned.shape[1]) // 2
        K.put(c, turned, x0, SOLES + 1 - turned.shape[0])
        return c

    def build(self, tag):
        P = self.pose
        k = PPU
        if tag == "dead":
            return [P(dx=-k), P(dx=-k, low=k), self.kneel(2 * k, dx=-k), self.kneel(3 * k, dx=-k)] + \
                [self.lying() for _ in range(4)]
        if tag == "run":
            return [self.run_frame(i) for i in range(8)]
        R = lambda i, dx, dy: K.shifted(self.run_frame(i), dx, dy)
        if tag == "skill2":
            return [P(low=k), R(0, 2 * k, -k), R(1, k, 0), P()]
        if tag == "ult":
            return [P(low=k), R(3, 0, -k), P(low=k, rifle="level", dx=-k), P()]
        if tag == "idle":
            return [P(low=n) for n in BREATH]
        if tag == "attack":
            return [P(), P(rifle="level"), P(rifle="level", dx=-k), P(rifle="level"), P()]
        if tag == "skill":
            return [P(low=k), P(rifle="level", low=k), P(rifle="level", low=k, dx=-k),
                    P(rifle="level", dx=-2 * k, low=k), P()]
        if tag == "skill2_back":
            return [P(low=k), P(dx=-2 * k, dy=-2 * k), P(dx=-k, low=k), P()]
        if tag == "hit":
            return [P(dx=-2 * k), P(dx=-k)]
        raise KeyError(tag)

    def finished(self, frames):
        """The outline closed (complete_outline), and the design's ring all round: a coloured square meeting the
        ground (a dark one the picture's read left at the edge, a turned leg's) gets the outline outside it; stray
        outline squares go."""
        ink = np.array(self.out, np.uint8)
        out = []
        for f in frames:
            g, _, _ = G.complete_outline(f, color=self.out, feet=SOLES)
            op = g[..., 3] > 0
            col = op & ~(g[..., :3] == ink).all(-1)
            p = np.pad(col, 1)
            add = ~op & (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
            add[SOLES + 1:] = False
            g[add] = (*self.out, 255)
            # a pinhole of ground shut inside the figure (between two strands the picture's read left, between the
            # legs' tops under the coat): the outline; a gap of five squares or more is the drawing's own (under the arm)
            for h in K.holes(g):
                if len(h) <= 4:
                    for y, x in h:
                        g[y, x] = (*self.out, 255)
            g[K.orphan_outline(g, self.out)] = 0
            out.append(g)
        return out


def sheet_sizes():
    with open(K.lp(STEM + "#anim.fanim"), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    return {t: [(int(fr["data"]["w"]), int(fr["data"]["h"])) for fr in a["frames"]] for t, a in anims.items()}


def cut(frame, w, h):
    """The hd frame of a 1x frame w x h: three times its box round the same centre. -> (frame, pixels left outside)."""
    x0, y0 = CENTRE[0] - (w - 1) // 2, CENTRE[1] - (h - 1) // 2
    X0, Y0 = PPU * x0, PPU * y0
    inside = frame[Y0:Y0 + PPU * h, X0:X0 + PPU * w].copy()
    lost = int((frame[..., 3] > 0).sum() - (inside[..., 3] > 0).sum())
    return inside, lost


def raised(frame, w, h):
    """The frame RAISE rows up (SCALE); a frame in the air with no room over it in its box only as far as it fits."""
    g = K.shifted(frame, 0, -RAISE)
    while cut(g, w, h)[1]:
        g = K.shifted(g, 0, 1)
    return g


def strip(frames):
    W = sum(f.shape[1] for f in frames) + len(frames) - 1
    H = max(f.shape[0] for f in frames)
    s = np.zeros((H, W, 4), np.uint8)
    x = 0
    for f in frames:
        s[:f.shape[0], x:x + f.shape[1]] = f
        x += f.shape[1] + 1
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--tags", default=",".join(TAGS))
    ap.add_argument("--renders", help="League's legs-only run renders (RUN_SPEC) with joints_run.json: remake the run")
    a = ap.parse_args()
    rig = Rig(a.renders)
    sizes = sheet_sizes()
    built = {}
    for tag in a.tags.split(","):
        try:
            # the run is finished already (made from the renders, or read back from its strip)
            frs = rig.build(tag) if tag == "run" else rig.finished(rig.build(tag))
        except KeyError:
            print(f"{tag:12s} not made yet")
            continue
        cuts = [cut(raised(f, w, h), w, h) for f, (w, h) in zip(frs, sizes[tag])]
        assert len(frs) == len(sizes[tag]), (tag, len(frs), len(sizes[tag]))
        built[tag] = [c for c, _ in cuts]
        print(f"{tag:12s}", " ".join(f"{i + 1}:{c.shape[1]}x{c.shape[0]}" + (f" LOST {n}" if n else "")
                                      for i, (c, n) in enumerate(cuts)))
    os.makedirs(OUT, exist_ok=True)
    for tag, frs in built.items():
        path = os.path.join(OUT, f"zeri_{tag}.png")
        s = strip(frs)
        if a.check:
            same = os.path.exists(path) and np.array_equal(np.asarray(Image.open(path).convert("RGBA")), s)
            print(tag, "identical" if same else "DIFFERS")
        else:
            Image.fromarray(s).save(path)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        review(built, sizes, a.review)


def review(built, sizes, out):
    """Every hd frame at 2x on the arena colour, the frames of a tag in a row."""
    z = 2
    rows = []
    for tag, frs in built.items():
        h = max(f.shape[0] for f in frs) * z
        w = sum(f.shape[1] * z + 8 for f in frs)
        row = Image.new("RGB", (w + 120, h + 8), (92, 98, 86))
        x = 120
        for f in frs:
            im = Image.fromarray(f).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST)
            row.paste(im, (x, 4 + h - im.height), im)
            x += im.width + 8
        from PIL import ImageDraw
        ImageDraw.Draw(row).text((4, 4), tag, fill=(255, 255, 255))
        rows.append(row)
    W = max(r.width for r in rows)
    Hh = sum(r.height for r in rows)
    sheet = Image.new("RGB", (W, Hh), (40, 40, 40))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(os.path.join(out, "zeri_hd_frames.png"))


if __name__ == "__main__":
    main()
