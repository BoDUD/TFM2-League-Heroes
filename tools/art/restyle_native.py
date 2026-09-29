#!/usr/bin/env python3
"""Game strips straight from League's animation, drawn in the hero's own pixel style.

    python tools/lol/native_pose.py assets/source/darius/poses.json --out DIR --alpha --parts
    python tools/art/restyle_native.py assets/source/darius/poses.json --renders DIR

Darius's strips from Codex were assembled square by square and read as cut-outs (the body changed
size between frames, the cape was a red slab), so his frames come from League's model instead.
native_pose.py renders every tag at game size on a transparent background (<hero>_pose_<tag>.png,
8x) with a part map beside it (<hero>_parts_<tag>.png: head, weapon, body). This turns every 8x8
block into one pixel in the design sheet's palette and writes assets/source/native/<hero>_<tag>.png,
the strips import_native.py cuts, plus <hero>_cells.json copied from DIR (the same cells and pivots):
  - colour: each render pixel votes for a colour by part and hue - the weapon on the weapon ramp by
    brightness; on the body crimson (red hue), skin (tan) or steel, each on its ramp, bright steel as
    the trim colour - and a block takes the colour with the most weighted votes. A block is opaque
    when half covered, a weapon block already at 20 of its 64 pixels, so a thin handle stays whole.
  - cleanup: a pixel whose four neighbours share another colour takes theirs (twice).
  - outline: one outline pixel outside the silhouette (a thin limb keeps its colour) and on the body
    along the weapon; the frame then moves up a pixel, so the outline under the soles lies on League's
    sole row and the pivot stays 11.5 px above it.
  - head: League's head goes, and the design sheet's head (the spec's rect, minus the `cut` pixels
    that belong to the body) goes where League's head joint is, as far from the joint as League's
    head starts in the first idle frame, behind the weapon. A head whose crown points back past 60
    degrees (the cells' "tilt": lying on his back) turns a quarter; a bowed head stays upright.
    "turn" in the spec moves that limit, for all tags or per tag with "*" for the rest (Amumu lies
    at 52-64 degrees, while his jumps throw the head back 50-65: {"dead": 50, "*": 180}).
Spec, in the hero's poses.json: "restyle": {"head": {"rect": [x, y, w, h], "cut": [[x, y], ...], "dy": 0},
"outline": "<hex>", "weapon" / "steel" / "cloth" / "skin": [["<hex>", <up to brightness>], ...,
["<hex>"]], "trim": ["<hex>", <from brightness>], "weights": {"<hex>": <vote weight>},
"turn": 60 or {"<tag>": <degrees>, "*": <degrees>}}.
A hero without a weapon, red cloth or skin (Amumu, all bandages) gives every ramp the same colours.
The design sheet is assets/source/native/<hero>_native.png. The renders show Riot's model: keep them
local.
Yasuo (league_yasuo) has more than crimson, skin and steel, and a ponytail that swings: "materials":
[{"name", "hue": [lo, hi] (degrees; lo > hi wraps), "sat": [lo, hi], "val": [lo, hi], "ramp": [...]},
...] replaces cloth / skin / steel / trim - a body pixel takes the first class it fits (a class with
no conditions takes the rest) - and "hair": ramp colours the hair part of a "hair_part" render
(native_pose.py) by brightness, so the ponytail follows League's animation while the design's head
is pasted over the head. "head": {"dy": -1} pastes that head a row higher: the frame is lifted a pixel
for the outline under the soles, and a design drawn on the lifted body has its head a row up too.
"dx" moves it sideways the same way: the head of league_teemo is drawn with its outline and ears a little
past League's head part, so its block starts left of and above where League's head starts.
A pasted head is a sticker: Yasuo's stayed upright while League's head bowed in the run, turned away in
the spins and lay down in death, and the user saw a head apart from the body. "head": {"mode":
"voted", "materials": [...], "features": {"anchor": [x, y], "pixels": [[x, y], ...], "min_facing": 0.2}}
votes League's head and hair like the body (the head materials: gold tie, skin, the rest hair), turns
League's eyes and brows (not-skin pixels with three skin neighbours) into skin, and draws the design's
feature pixels at native_pose's "face" point ("face_track"): not when the face turns from the camera,
mirrored when it looks left, turned with the crown when he lies down.
After Yasuo's body went to 80% with the head kept, "features" gained "skip" (pixels of "rect" left out),
a colour on "pixels" ([x, y, least facing, "<hex>"]), "neck": "<hex>" (body skin within two squares of
the face, below the eye row: his scarf, where League's neck made the face a row longer), "trim_front":
rows (a one-square bump of the fringe past the face's front edge above the eyes, cut and outlined
again) and "hair_above": rows (the forehead's skin above the drawn fringe becomes hair).
Leona (league_leona) holds a big shield in front of her body, voted into one gold mass with her armour and
cloth: the spec's top-level "parts": [{"name", "joints", "outline": true, "materials": [...]}] (native_pose.py
paints those chains cyan, then magenta) votes each by its own materials, and an outlined one gets the outline
on whatever touches it, so the shield reads as a shield. Her small face under thick hair and a crown gave
too little voted skin to place the face on: "features" "profile" (the facing below which a face counts as
turned into profile, instead of fewer than five squares of skin in the eye row), "chin" (the block's rows
that far below the eye row may also paint over the body: her collar) and "fallback": "track" (the track's
point is the far eye where too little skin is voted).
Master Yi (league_masteryi) wears a rigid helmet: its voted gold trim and silver came out as a speckled blob
that changed every frame, so his head is pasted - drawn square by square after League's 2013 model, tilted
the way he holds it in idle (League's head tilts within 20 degrees of that in almost every frame).
"head": {"forward": true} also turns a pasted head a quarter the other way when the crown points forward
past the limit: he falls on his face in death (tilt +63 to +80), where only lying on the back was turned.
Janna (league_janna) is slender: at 28 px her arms, legs and the cloth strips of her skirt are one or two pixels
wide, and the outline drawn around each of them cut her into dark stripes (as many outline pixels as body
pixels). "cover": 0.3 makes a block opaque from 30% of its pixels instead of half (her limbs a pixel thicker,
the skirt one white shape); "close": <rounds> fills empty pixels between two body pixels (left and right, or
above and below) with the colour beside them before the outline. "weapon_materials": [...] votes weapon pixels
by hue like "materials" before the brightness ramp takes the rest: her staff is blue, its gems orange.
Her pasted head first carried two rows of the design's neck, drawn on the idle body with an outline down its
middle, and in Monsoon League turns her torso side-on, three pixels wide: in game the user saw a head on a pipe.
The rect now ends a row under the chin, "paint": [[x, y, "<hex>"], ...] recolours design pixels of the block
(that row's neck one piece of skin), "dy" puts the chin on the shoulders, and "shoulders": {"x": <column>,
"widths": [...]} widens the body under the block before the head goes on: row by row from the row under it,
round the block's column x (the neck), to at least those widths, each new pixel the colour of the nearest body
pixel in its row, the outline drawn round the new pixels. Not on a turned (lying) head.
Malphite (league_malphite) has a tiny head hanging in front of his chest, under his shoulders and back spikes;
voted or scaled up it melted into the chest's stone, so a drawn head (a horned rock snout) sits higher, between
his shoulders. "head": {"under": [materials]} keeps League's head, voted by those materials, as part of the
chest (dropped, it left a hole under the drawn head), and "anchor": true places the drawn head on native_pose's
"anchor" point (his shoulders) instead of League's head joint and turns it with the torso ("atilt"): on the
head joint, 19 rows below the drawn head, it floated off the body whenever League's head nodded or swung
(the wind-up of his attack, the landing of his R, lying in death).
Kayle (league_kayle) floats with her near arm held away from her waist, and at game size the gap between them
was a few empty pixels in an outline ring: a black hole in her armour. "fill_holes": <pixels> fills every empty
region the frame's edge cannot reach, up to that size, and its inner outline with the body colours beside it,
before the head goes on.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from native_refs import Z, layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
HEAD, WEAPON, BODY = 0, 1, 2      # the strongest channel of native_pose's part colours: red, green, blue
HAIR = 3                          # yellow (red and green) in a "hair_part" render
EXTRA = (4, 5)                    # the spec's "parts": cyan (green and blue), magenta (red and blue)
TURN = 60


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hsv(a):
    """Hue in degrees, saturation and value (0-1) of an RGB array in 0-1."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    return h * 60, np.where(mx > 0, d / np.maximum(mx, 1e-6), 0), mx


class Palette:
    def __init__(self, spec, parts=()):
        cols, self.ramps = [], {}
        self.materials = spec.get("materials")
        self.hair = "hair" in spec
        # "under": League's head stays, voted by these materials, below a drawn head pasted elsewhere
        self.head_under = spec.get("head", {}).get("under") is not None
        self.head_materials = spec.get("head", {}).get("under" if self.head_under else "materials")
        self.weapon_materials = spec.get("weapon_materials")
        self.close = int(spec.get("close", 0))
        self.cover = float(spec.get("cover", 0.5))
        self.extra = list(parts)
        if self.materials is None:
            ramps = [(name, spec[name]) for name in ("weapon", "steel", "cloth", "skin")]
        else:
            ramps = [("weapon", spec["weapon"])] + \
                    [("weapon:" + m["name"], m["ramp"]) for m in (self.weapon_materials or [])] + \
                    ([("hair", spec["hair"])] if self.hair else []) + \
                    [(m["name"], m["ramp"]) for m in self.materials] + \
                    [("head:" + m["name"], m["ramp"]) for m in (self.head_materials or [])] + \
                    [(f"part{k}:" + m["name"], m["ramp"]) for k, ex in enumerate(self.extra) for m in ex["materials"]]
        for name, ramp in ramps:
            for c in ramp:
                if c[0] not in cols:
                    cols.append(c[0])
            self.ramps[name] = ([cols.index(c[0]) for c in ramp], [c[1] for c in ramp[:-1]])
        self.trim = None
        if self.materials is None:
            if spec["trim"][0] not in cols:
                cols.append(spec["trim"][0])
            self.trim = (cols.index(spec["trim"][0]), spec["trim"][1])
        self.rgb = np.array([rgb(c) for c in cols], np.uint8)
        self.skin = sorted(set(self.ramps["head:skin"][0])) if "head:skin" in self.ramps else []
        self.weight = np.array([spec.get("weights", {}).get(c, 1.0) for c in cols])
        self.outline = rgb(spec["outline"])

    def classify(self, h, s, v, out, left, materials, prefix=""):
        """Vote the pixels in `left` by `materials`: the first class a pixel fits takes it."""
        left = left.copy()
        for m in materials:
            sel = left.copy()
            if "hue" in m:
                lo, hi = m["hue"]
                sel &= ((h >= lo) & (h <= hi)) if lo <= hi else ((h >= lo) | (h <= hi))
            if "sat" in m:
                sel &= (s >= m["sat"][0]) & (s <= m["sat"][1])
            if "val" in m:
                sel &= (v >= m["val"][0]) & (v <= m["val"][1])
            out[sel] = self.ramp(prefix + m["name"], v[sel])
            left &= ~sel

    def ramp(self, name, v):
        idx, cuts = self.ramps[name]
        return np.array(idx)[np.searchsorted(cuts, v)]

    def votes(self, px, part):
        """The colour index each render pixel votes for (-1: none)."""
        h, s, v = hsv(px / 255.0)
        out = np.full(v.shape, -1, np.int32)
        w = part == WEAPON
        out[w] = self.ramp("weapon", v[w])
        if self.weapon_materials:        # colours of the weapon apart from its ramp (Janna's orange gems)
            self.classify(h, s, v, out, w, self.weapon_materials, "weapon:")
        if self.materials is not None:
            if self.head_materials is not None:       # a voted head: head and hair by their own classes
                self.classify(h, s, v, out, (part == HEAD) | (part == HAIR), self.head_materials, "head:")
            elif self.hair:
                hr = part == HAIR
                out[hr] = self.ramp("hair", v[hr])
            self.classify(h, s, v, out, part == BODY, self.materials)
            for k, ex in enumerate(self.extra):
                self.classify(h, s, v, out, part == EXTRA[k], ex["materials"], f"part{k}:")
            return out
        b = part == BODY
        red = b & ((h < 20) | (h > 330)) & (s > 0.35) & (v > 0.08)
        tan = b & ~red & (h >= 10) & (h <= 50) & (s > 0.25) & (v > 0.22)
        steel = b & ~red & ~tan
        out[red] = self.ramp("cloth", v[red])
        out[tan] = self.ramp("skin", v[tan])
        out[steel] = self.ramp("steel", v[steel])
        out[steel & (v > self.trim[1])] = self.trim[0]
        return out


def per_block(a, w, h):
    """(h*Z, w*Z) -> (h, w, Z*Z): the render pixels of each game pixel."""
    return a.reshape(h, Z, w, Z).transpose(0, 2, 1, 3).reshape(h, w, Z * Z)


def lonely(a, rounds=2):
    """A pixel whose four neighbours share one other colour takes it."""
    for _ in range(rounds):
        c = a[..., :3].astype(np.int64)
        key = np.where(a[..., 3] > 0, (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2], -1)
        p = np.pad(key, 1, constant_values=-2)
        n = [p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]]
        swap = (n[0] == n[1]) & (n[1] == n[2]) & (n[2] == n[3]) & (n[0] >= 0) & (key >= 0) & (key != n[0])
        v = n[0][swap]
        a[swap, 0], a[swap, 1], a[swap, 2] = (v >> 16) & 255, (v >> 8) & 255, v & 255
    return a


def close_gaps(a, solid, rounds=1):
    """Fill empty pixels between two `solid` pixels (left and right, or above and below) with the colour of
    the left or upper one, `rounds` times: league_janna's skirt is thin cloth strips a pixel apart, and an
    outline drawn into every gap cut it into dark stripes. Returns the frame and the filled pixels."""
    filled = np.zeros(solid.shape, bool)
    for _ in range(rounds):
        s = solid | filled
        p = np.pad(s, 1)
        lr = p[1:-1, :-2] & p[1:-1, 2:]
        ud = p[:-2, 1:-1] & p[2:, 1:-1]
        new = ~s & (a[..., 3] == 0) & (lr | ud)
        if not new.any():
            break
        src = np.pad(a, ((1, 1), (1, 1), (0, 0)))
        left, up = src[1:-1, :-2], src[:-2, 1:-1]
        a[new & lr] = left[new & lr]
        a[new & ~lr] = up[new & ~lr]
        filled |= new
    return a, filled


def near(m):
    """Pixels with a 4-neighbour in mask m."""
    p = np.pad(m, 1)
    return p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]


def part_of(pa, hair, extra=0):
    """Each render pixel's part: the strongest channel of its part colour; with a hair ramp in the
    spec, yellow (red and green, no blue) is the hair; with "parts", cyan and magenta are those."""
    c = pa[..., :3]
    part = c.argmax(-1)
    top = c.max(-1)
    if hair:
        part = np.where((c[..., 0] > 0.5 * top) & (c[..., 1] > 0.5 * top) & (c[..., 2] < 0.5 * top), HAIR, part)
    if extra >= 1:
        part = np.where((c[..., 0] < 0.5 * top) & (c[..., 1] > 0.5 * top) & (c[..., 2] > 0.5 * top), EXTRA[0], part)
    if extra >= 2:
        part = np.where((c[..., 0] > 0.5 * top) & (c[..., 1] < 0.5 * top) & (c[..., 2] > 0.5 * top), EXTRA[1], part)
    return part


def clean_face(a, head, pal, rounds=2):
    """On the head, a pixel that is not skin but has three or four skin neighbours becomes the skin they
    share most: League's own eyes and brows, under the design's."""
    skin = [tuple(int(t) for t in pal.rgb[i]) for i in pal.skin]
    for _ in range(rounds):
        c = a[..., :3].astype(np.int64)
        key = np.where(a[..., 3] > 0, (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2], -1)
        skey = [(r << 16) | (g << 8) | b for r, g, b in skin]
        p = np.pad(key, 1, constant_values=-2)
        n = np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]], -1)
        counts = np.stack([(n == k).sum(-1) for k in skey], -1)
        change = head & (a[..., 3] > 0) & ~np.isin(key, skey) & (counts.sum(-1) >= 3)
        best = np.array(skey)[counts.argmax(-1)]
        v = best[change]
        a[change, 0], a[change, 1], a[change, 2] = (v >> 16) & 255, (v >> 8) & 255, v & 255
    return a


def flat_face(a, head, pal):
    """The voted face in the design's two tones: light inside, the middle tone along its edge. League's
    shading and stubble left Yasuo a dark jaw, like a mask, under the design's eyes."""
    idx = pal.ramps["head:skin"][0]
    c = a[..., :3].astype(np.int64)
    key = np.where(a[..., 3] > 0, (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2], -1)
    skey = [(int(r) << 16) | (int(g) << 8) | int(b) for r, g, b in pal.rgb[idx]]
    face = head & np.isin(key, skey)
    rim = face & near(~face)
    a[face & ~rim, :3] = pal.rgb[idx[-1]]
    a[rim, :3] = pal.rgb[idx[len(idx) // 2]]
    return a


def body(pal, hi, pa, w, h):
    """One frame without its head: (RGBA game pixels, weapon mask, League's head in the 8x render)."""
    op = (hi[..., 3] >= 128) & (pa[..., 3] >= 128)
    part = np.where(op, part_of(pa, pal.hair, len(pal.extra)), -1)
    bv, bp = per_block(pal.votes(hi[..., :3], part), w, h), per_block(part, w, h)
    count = np.stack([(bp == k).sum(-1) for k in (HEAD, WEAPON, BODY, HAIR) + EXTRA[:len(pal.extra)]], -1)
    main = count.argmax(-1)
    score = np.stack([(bv == k).sum(-1) * pal.weight[k] for k in range(len(pal.rgb))], -1)
    on = ((bp >= 0).mean(-1) >= pal.cover) | ((main == WEAPON) & (count[..., WEAPON] >= 20))
    voted = pal.head_materials is not None
    keep = on if voted else on & (main != HEAD)
    a = np.zeros((h, w, 4), np.uint8)
    a[keep, :3] = pal.rgb[score.argmax(-1)[keep]]
    a[keep, 3] = 255
    if pal.close:          # one-pixel gaps between thin cloth strips filled, so no outline runs through the skirt
        a, filled = close_gaps(a, keep & (main != WEAPON), pal.close)
        keep = keep | filled
        main = np.where(filled, BODY, main)
    a = lonely(a)
    if voted and not pal.head_under:
        a = clean_face(a, keep & (main == HEAD), pal)
        a = flat_face(a, keep & (main == HEAD), pal)
    weapon = keep & (main == WEAPON)
    o = a[..., 3] > 0
    ring = ~o & near(o)
    edge = o & ~weapon & near(weapon)
    for k, ex in enumerate(pal.extra):       # an outlined prop: the pixels around it that are not it
        if ex.get("outline"):
            prop = keep & (main == EXTRA[k])
            edge |= o & ~prop & ~weapon & near(prop)
    a[ring | edge, :3] = pal.outline
    a[ring, 3] = 255
    a = np.concatenate([a[1:], np.zeros((1, w, 4), np.uint8)])       # the outline under the soles on the sole row
    weapon = np.concatenate([weapon[1:], np.zeros((1, w), bool)])
    head_px = np.concatenate([(keep & (main == HEAD))[1:], np.zeros((1, w), bool)])
    body_px = np.concatenate([(keep & (main == BODY) & ~edge)[1:], np.zeros((1, w), bool)])
    return a, weapon, part == HEAD, head_px, body_px


def paste_head(a, weapon, head, joint, tilt, turn=TURN, dy=0, dx=0, forward=False):
    """Paste the head grid (list of rows of hex or None) with League's head joint at joint[0] (x, y), given
    as the joint's place inside the upright head: joint = (x, y, jx, jy). `forward`: also a quarter turn
    the other way when the crown points forward past `turn` (lying on his face)."""
    x, y, jx, jy = joint
    g = np.array([[c or "" for c in row] for row in head], dtype=object)
    H, W = g.shape
    if tilt <= -turn:                      # lying on his back: the crown points left, the face up
        # dx / dy move the block against the joint in the upright head: turn them with it, or the
        # quarter-turned head lands beside the neck (league_teemo's death: 3 px left, 2 px up)
        jx, jy = jx - dx, jy - dy
        g, (jx, jy) = np.rot90(g, 1), (jy, W - jx)
        dx = dy = 0
    elif forward and tilt >= turn:         # lying on his face: the crown points right
        # dx / dy stay on the screen here: league_masteryi's death frames were checked that way
        g, (jx, jy) = np.rot90(g, -1), (H - jy, jx)
    x0, y0 = int(round(x - jx)) + dx, int(round(y - jy)) + dy
    for j, row in enumerate(g):
        for i, c in enumerate(row):
            yy, xx = y0 + j, x0 + i
            if c and 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and not weapon[yy, xx]:
                a[yy, xx] = rgb(c) + (255,)


def shoulders(a, weapon, cx, top, widths, outline):
    """The body under a pasted head at least `widths` wide, row by row from `top` (the row under the head
    block), round column cx: a new pixel takes the colour of the nearest body pixel in its row, the outline
    goes round the new pixels. league_janna's torso is three pixels wide in Monsoon, under a 14 px head."""
    h, w = a.shape[:2]
    body = (a[..., 3] > 0) & ~(a[..., :3] == outline).all(-1) & ~weapon
    grown = np.zeros(body.shape, bool)
    for r, width in enumerate(widths):
        y = top + r
        if not 0 <= y < h:
            continue
        span = [x for x in range(int(cx) - 5, int(cx) + 6) if 0 <= x < w and body[y, x]]
        if not span:
            continue
        need = max(0, width - (max(span) - min(span) + 1))
        for x in range(max(0, min(span) - (need + 1) // 2), min(w, max(span) + need // 2 + 1)):
            if body[y, x] or weapon[y, x]:
                continue
            src = min(span, key=lambda s: (abs(x - s), s))
            a[y, x] = a[y, src]
            grown[y, x] = True
    solid = (a[..., 3] > 0) & ~(a[..., :3] == outline).all(-1)
    ring = near(grown) & ~solid
    a[ring, :3] = outline
    a[ring, 3] = 255


def fill_holes(a, weapon, outline, max_area):
    """Fill every empty region the frame's edge cannot reach, of at most `max_area` pixels, and the outline
    pixels round it, with the body colours beside them (the most common of the four neighbours, repeated
    inwards). league_kayle's idle holds her near arm away from her waist: at game size the gap between them
    was three empty pixels in an outline ring, a black hole in the middle of her armour."""
    h, w = a.shape[:2]
    empty = a[..., 3] == 0
    seen = np.zeros((h, w), bool)
    ol = np.array(outline, np.uint8)
    is_ol = lambda y, x: bool((a[y, x, :3] == ol).all()) and a[y, x, 3] > 0  # noqa: E731
    for y in range(h):
        for x in range(w):
            if not empty[y, x] or seen[y, x]:
                continue
            stack, region, edge = [(y, x)], [], False
            seen[y, x] = True
            while stack:
                cy, cx = stack.pop()
                region.append((cy, cx))
                edge |= cy in (0, h - 1) or cx in (0, w - 1)
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and empty[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            if edge or len(region) > max_area:
                continue
            todo = set(region)
            for cy, cx in region:
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if (ny, nx) not in todo and is_ol(ny, nx):
                        todo.add((ny, nx))
            while todo:
                done = set()
                for cy, cx in sorted(todo):
                    votes = {}
                    for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                        if (ny, nx) in todo or not (0 <= ny < h and 0 <= nx < w):
                            continue
                        if a[ny, nx, 3] and not is_ol(ny, nx) and not weapon[ny, nx]:
                            k = tuple(int(v) for v in a[ny, nx, :3])
                            votes[k] = votes.get(k, 0) + 1
                    if votes:
                        a[cy, cx, :3] = max(votes, key=lambda k: (votes[k], k))
                        a[cy, cx, 3] = 255
                        done.add((cy, cx))
                if not done:
                    break
                todo -= done
    return a


def paste_face(a, weapon, head_px, feats, cell, pal, min_facing, dy=-1, trim=0, hair_above=0, profile=None,
               body_px=None, chin=None, fallback=None):
    """The design's brows, eyes and mouth on the face this frame shows. native_pose's track (cells "face":
    x, y, facing, side) says whether a face shows (facing), which way it looks (side: mirrored to the
    left) and the eye row (y, kept a row inside the visible skin); the far eye goes on the face's front
    edge in that row, the near eye two columns behind it (one on a narrow face). Placed by the 3D point
    alone, the eyes of a bowed head landed in the fringe and a face turned half away got none. Not on a
    head leaning past 45 degrees (lying down). `feats`: (dx, dy, colour, least facing) from the design's
    anchor, the far eye. dy -1: the frame is lifted a row. `trim`: in that many rows above the eye row
    (and the three below it), head pixels one square past the face's front edge are cut and the outline
    redrawn round the cut: League's fringe stuck out a square past Yasuo's forehead in the idle, a bump
    the user found strange, and in idle 3 the jaw did, so the face changed shape as he breathed.
    `hair_above`: the head's skin more than that many rows above the eye row becomes hair (the ramp's
    darkest, the crown's own lower edge; the middle tone read as a lighter band that came and went
    in the idle): League's forehead showed as a band of skin over the design's fringe.
    `profile`: a face counts as turned into profile (front four columns only) when its facing is below this,
    instead of when fewer than five squares of skin were voted in the eye row: Leona's thick hair leaves four
    even on a three-quarter face, and her near eye was cut in half.
    `chin`: the block's rows that many or more below the eye row also paint over the body (`body_px`, not its
    outlines): League votes Leona's cheeks and chin into her collar, which left gold and magenta squares in
    the drawn face's lower edge.
    `fallback` "track": where too little skin is voted to find the eye row and the face's front edge (Leona's
    small face under her hair and crown: two squares or none in most run frames), the track's point is the
    far eye; where both exist they agreed within two squares."""
    if "face" not in cell or abs(cell.get("tilt", 0)) >= 45:
        return
    fx, fy, facing, side = cell["face"]
    if facing < min_facing:
        return
    idx = pal.ramps["head:skin"][0]
    c = a[..., :3].astype(np.int64)
    key = np.where(a[..., 3] > 0, (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2], -1)
    skin = head_px & np.isin(key, [(int(r) << 16) | (int(g) << 8) | int(b) for r, g, b in pal.rgb[idx]])
    ys, xs = np.nonzero(skin)
    er = row = None
    if len(ys) >= 8:
        top, bottom = ys.min(), ys.max()
        er = min(max(int(np.floor(fy + 0.5)) + dy, top + 1), bottom - 1)
        row = xs[ys == er]
    if row is None or len(row) < 3:
        if fallback != "track":
            return
        er, xe = int(np.floor(fy + 0.5)) + dy, int(np.floor(fx))
        narrow = facing < profile if profile is not None else False
    else:
        xe = row.max() if side > 0 else row.min()
        narrow = len(row) < 5 if profile is None else facing < profile
    for ox, oy, col, least, alt in feats:
        if facing < least:
            if alt is None:
                continue
            col = alt
        if narrow and ox < -3:
            continue          # a face in profile: the block's front four columns
        x, y = xe + (ox if side > 0 else -ox), er + oy
        if 0 <= y < a.shape[0] and 0 <= x < a.shape[1] and a[y, x, 3] and not weapon[y, x] and \
                (head_px[y, x] or (chin is not None and oy >= chin and body_px is not None and body_px[y, x])):
            a[y, x, :3] = col
    if hair_above:
        hi_ = pal.ramps["head:hair"][0]
        up = np.zeros(a.shape[:2], bool)
        up[:max(0, er - hair_above)] = True
        a[up & skin & ~weapon, :3] = pal.rgb[hi_[0]]           # the darkest: the crown's own edge there
    if trim:
        # only a one-square bump over a face that is the head's front edge in the eye row: where League's
        # hair hangs further in front of the face (ult 7), cutting it left a notch
        xs_ = np.arange(a.shape[1])
        past = (xs_ > xe) if side > 0 else (xs_ < xe)
        c = a[..., :3].astype(np.int64)
        key = np.where(a[..., 3] > 0, (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2], -1)
        hair = np.isin(key, [(int(r) << 16) | (int(g) << 8) | int(b) for r, g, b in pal.rgb[pal.ramps["head:hair"][0]]])
        head = head_px & (a[..., 3] > 0) & ~(a[..., :3] == pal.outline).all(-1)
        cut = np.zeros(a.shape[:2], bool)
        one = xe + (1 if side > 0 else -1)
        if not (hair[er] & head_px[er] & past).any():
            for y in range(er - 1, max(-1, er - trim - 1), -1):       # upwards from the brow row
                xs = np.nonzero(head[y] & past)[0]
                if len(xs) and (xs != one).any():
                    break                                            # the crown: wider than the face
                cut[y, xs] = True
            for y in range(er + 1, min(a.shape[0], er + 4)):          # and the jaw, downwards
                xs = np.nonzero(head[y] & past)[0]
                if len(xs) and (xs != one).any():
                    break
                cut[y, xs] = True
        if cut.any():
            a[cut, 3] = 0
            around = cut | near(cut) | near(near(cut))
            line = (a[..., 3] > 0) & (a[..., :3] == pal.outline).all(-1)
            solid = (a[..., 3] > 0) & ~line
            a[around & line & ~near(solid), 3] = 0              # the old outline past the cut
            ring = around & (a[..., 3] == 0) & near(solid)
            a[ring, :3] = pal.outline
            a[ring, 3] = 255


def scarf_neck(a, head_px, cell, pal, colour, min_facing, dy=-1):
    """Body skin within two pixels of the face's skin, below the eye row, in `colour`: the neck League
    shows under the chin made Yasuo's face a row longer (the user: a horse face); his scarf covers it."""
    if "face" not in cell or abs(cell.get("tilt", 0)) >= 45 or cell["face"][2] < min_facing:
        return
    idx = sorted(set(pal.ramps["head:skin"][0]) | set(pal.ramps.get("skin", ([], []))[0]))
    c = a[..., :3].astype(np.int64)
    key = np.where(a[..., 3] > 0, (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2], -1)
    skin = np.isin(key, [(int(r) << 16) | (int(g) << 8) | int(b) for r, g, b in pal.rgb[idx]])
    face = head_px & skin
    neck = skin & ~head_px & (near(face) | near(near(face)))
    neck[:int(np.floor(cell["face"][1] + 0.5)) + dy + 1] = False
    a[neck, :3] = colour


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--renders", required=True, help="native_pose.py --alpha --parts output folder")
    args = ap.parse_args()
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    hero, rs = spec["hero"], spec["restyle"]
    pal = Palette(rs, spec.get("parts", ()))
    cells_path = os.path.join(args.renders, f"{hero}_cells.json")
    with open(cells_path, encoding="utf-8") as f:
        table = json.load(f)
    w, h = table["cell"]
    design = np.asarray(Image.open(G.lp(os.path.join(SRC, f"{hero}_native.png"))).convert("RGBA"))[::Z, ::Z]
    voted = rs["head"].get("mode") == "voted"
    if voted:           # League's head voted like the body, the design's features drawn on its face
        fs = rs["head"]["features"]
        ax, ay = fs["anchor"]
        # the design's face block ("rect": forehead, brows, eyes, cheeks and mouth, as drawn), or single
        # "pixels"; [x, y, least facing, colour below it]: the mouth only on a face turned to the camera
        if "rect" in fs:
            rx, ry, rw, rh = fs["rect"]
            late = {(p[0], p[1]): p[2:] for p in fs.get("late", [])}
            skip = {tuple(p) for p in fs.get("skip", [])}
            feats = [(x - ax, y - ay, design[y, x, :3], late.get((x, y), [0.0])[0],
                      np.array(rgb(late[(x, y)][1]), np.uint8) if len(late.get((x, y), [])) > 1 else None)
                     for y in range(ry, ry + rh) for x in range(rx, rx + rw) if design[y, x, 3] and (x, y) not in skip]
        else:
            feats = []
        feats += [(p[0] - ax, p[1] - ay, np.array(rgb(p[3]), np.uint8) if len(p) > 3 else design[p[1], p[0], :3],
                   p[2] if len(p) > 2 else 0.0, None) for p in fs.get("pixels", [])]
        neck = np.array(rgb(fs["neck"]), np.uint8) if "neck" in fs else None
    else:
        x0, y0, hw, hh = rs["head"]["rect"]
        cut = {tuple(p) for p in rs["head"].get("cut", [])}
        paint = {(p[0], p[1]): p[2] for p in rs["head"].get("paint", [])}
        head = [[paint.get((x0 + i, y0 + j)) or ("%02X%02X%02X" % tuple(design[y0 + j, x0 + i, :3])
                 if design[y0 + j, x0 + i, 3] and (x0 + i, y0 + j) not in cut else None) for i in range(hw)]
                for j in range(hh)]

    def frames(tag):
        n = len(table["tags"][tag])
        cols, _ = layout(n)
        hi = np.asarray(Image.open(G.lp(os.path.join(args.renders, f"{hero}_pose_{tag}.png"))).convert("RGBA")).astype(np.float32)
        pa = np.asarray(Image.open(G.lp(os.path.join(args.renders, f"{hero}_parts_{tag}.png"))).convert("RGBA")).astype(np.float32)
        for k in range(n):
            sl = (slice(k // cols * h * Z, (k // cols + 1) * h * Z), slice(k % cols * w * Z, (k % cols + 1) * w * Z))
            yield (*body(pal, hi[sl], pa[sl], w, h), table["tags"][tag][k])

    # where the drawn head starts from League's head joint: where League's head starts in the first idle frame.
    # "anchor": true follows native_pose's "anchor" point (the torso) and turns with the torso ("atilt") instead
    at, tilt_key = ("anchor", "atilt") if rs["head"].get("anchor") else ("head", "tilt")
    if not voted:
        _, _, league_head, _, _, first = next(frames("idle"))
        ys, xs = np.nonzero(league_head)
        jx, jy = first[at][0] - xs.min() // Z, first[at][1] - ys.min() // Z
    for tag, rows in table["tags"].items():
        cols, nrows = layout(len(rows))
        sheet = np.zeros((nrows * h, cols * w, 4), np.uint8)
        for k, (a, weapon, _, head_px, body_px, cell) in enumerate(frames(tag)):
            turn = rs.get("turn", TURN)
            if isinstance(turn, dict):         # per tag, "*" for the rest
                turn = turn.get(tag, turn.get("*", TURN))
            if rs.get("fill_holes"):           # small gaps inside the body (league_kayle's arm and waist)
                a = fill_holes(a, weapon, pal.outline, rs["fill_holes"])
            if voted:
                paste_face(a, weapon, head_px, feats, cell, pal, fs.get("min_facing", 0.05), profile=fs.get("profile"),
                           body_px=body_px, chin=fs.get("chin"), fallback=fs.get("fallback"), trim=fs.get("trim_front", 0),
                           hair_above=fs.get("hair_above", 0))
                if neck is not None:
                    scarf_neck(a, head_px, cell, pal, neck, fs.get("min_facing", 0.05))
            else:
                tilt, sh = cell.get(tilt_key, 0), rs["head"].get("shoulders")
                if sh and -turn < tilt and not (rs["head"].get("forward", False) and tilt >= turn):
                    top = int(round(cell[at][1] - jy)) + rs["head"].get("dy", 0) + len(head)
                    left = int(round(cell[at][0] - jx)) + rs["head"].get("dx", 0)
                    shoulders(a, weapon, left + sh["x"], top, sh["widths"], pal.outline)
                paste_head(a, weapon, head, (cell[at][0], cell[at][1], jx, jy), tilt, turn,
                           rs["head"].get("dy", 0), rs["head"].get("dx", 0), rs["head"].get("forward", False))
            sheet[k // cols * h:(k // cols + 1) * h, k % cols * w:(k % cols + 1) * w] = a
        Image.fromarray(np.repeat(np.repeat(sheet, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"{hero}_{tag}.png")))
        colours = len(np.unique(sheet[sheet[..., 3] > 0][:, :3], axis=0))
        print(f"{hero}_{tag}.png  {len(rows)} frames, {colours} colours")
    shutil.copyfile(cells_path, os.path.join(SRC, f"{hero}_cells.json"))
    print(f"{hero}_cells.json copied" if voted else f"head joint {jx:.1f}, {jy:.1f} inside the drawn head; "
                                                     f"{hero}_cells.json copied")


if __name__ == "__main__":
    main()
