#!/usr/bin/env python3
"""Game-size pose references straight from League's animations (a native-size redraw in one round).

    python tools/lol/native_pose.py assets/source/leesin/poses.json --out DIR

The native-size redraw (assets/source/NATIVE_REDRAW.md) needed a first GPT round only to turn
League's poses into game frames. This renders the clips at game size instead: the chibi model
(pose_ref.py's --head / --legs / --hair) seen through one camera, scaled so the spec's `design`
pose is `height` px from the crown to the soles (hair chains hanging from the head not counted),
every game pixel the mean colour of one 8x8 block of an --hq render (a block at least half covered
is opaque). Per tag of the spec it writes
  <hero>_native_<tag>.png  the frames at game size, shown at 8x, in native_refs.py's grid of 56x64
                           cells read left to right, top to bottom (feet line 10 px above the bottom)
  <hero>_pose_<tag>.png    the same frames as the 8x render itself: same grid, same place
and <hero>_native_design.png (the design pose on a 128x128 canvas at 8x, feet line 28 px above the
bottom, like native_refs.py's <hero>_now_design.png), <hero>_pose_design.png (the same at 8x
render), and <hero>_cells.json: each frame's pivot in its cell and its duration, the table
tools/art/import_native.py cuts the redrawn frames out with, plus where League's head joint is in
the cell (tools/art/fit_native.py puts a redrawn frame's head there) and, when it leans past 45
degrees, which way its crown points ("tilt", degrees clockwise from up: a body lying on its back).
--alpha writes <hero>_pose_<tag>.png on a transparent background and --parts adds
<hero>_parts_<tag>.png, the same frames painted by part (head with its hair red, weapon green, body
blue), for tools/art/restyle_native.py, which recolours them into the design's palette.

Placement: the unit stands at the world origin. Every frame keeps League's height (jumps,
landings, the death fall) and one vertical offset puts the design pose's lowest point on the feet
line; the pivot is 11.5 px above its soles, so a prop hanging below them (Darius's axe) does not
lift the sprite in game.
Sideways, an action keeps `lunge` of League's travel around the design pose's head (the importers
kept 65-70%: League blends back to idle, a sprite snaps back), then each frame is centred across
its cell by its content and its pivot recorded. Per tag, "anchor": "first" measures that travel
from the tag's first frame instead and puts that frame's head where the design pose has it (Lee
Sin's death starts 140 units in front of the unit), and "flat": true puts every frame's lowest
point as high above the feet line as it is above League's floor: knocked back away from the camera,
a body lying diagonally in depth otherwise floats or sinks (the pitch turns depth into height),
while a sprite has one ground line. "head_like": "<clip@ms>" turns the head of every frame of the tag
to face the way it faces in that pose, the body untouched: Lee Sin's combat run looks at the
ground, and a chibi head seen from above shows only its crown, never the blindfold. "keep" in
"chibi" names head parts that ride on the head's skin weights but should stay League's size like
the hair (Soraka's horn: {"horn": 4.0}, see pose_ref.keep_parts); the crown is then measured
without them, as without the hair.

"rise" (per tag) keeps that share of League's height while the whole body is off the ground
(Darius's Noxian Guillotine leaps about five metres, three times his chibi height: 0.3).
"travel" (per tag) keeps that share of the root joint's way across the floor: Teemo's death throws him
about 320 units back, out of the render (0.3 keeps him near the unit, as a sprite's death should stay).

"hover": <px> (Janna floats) moves the pivot that many rows down, so the whole sprite stands that high above
the ground in game (the base ghost floats about 6 px); a frame's (or tag's) "sink": <px> moves that frame down
again, for the frames that come to the ground (her death: 1, 2, then 3 px as she lands). League's Janna floats
12 to 39 units above the floor in idle and glides along it in the run, which rises and falls 47 units over its 2 s
cycle: the run keeps "rise": 0 with "flat" (the lowest point of her legs on the feet line in every frame) and so
hovers the same 3 px as the idle drawing. Its frames are blended 85% toward the idle pose: League's glide leans
her body forward, and under her upright pasted head the user saw the body move while the head stayed put.

"weapon" is the regex naming the joint whose chain is the weapon part in --parts renders (default
"^weapon$"; Yasuo's katana hangs from "Sword"). "hide" lists joint regexes whose chains are left out
of every render: Yasuo's flute is scaled to nothing in idle but has no track in his attack and death
clips, where it floats beside him at full size. "hair_part": true paints the hair chains (the
pose_ref HAIR joints below the head: Yasuo's ponytail) yellow in --parts renders instead of red, so
restyle_native.py can colour them frame by frame while the design's head is pasted over the rest.

"parts": [{"name", "joints": "<regex>", ...}] paints up to two more joint chains of the body in their own
colours (cyan, magenta) in --parts renders, for restyle_native.py to vote and outline apart from the body
(Leona's shield, a mesh on its own root joint, read as one gold mass with her armour and cloth).

"crown": <y> measures the crown from the head's vertices at or below that height in the bind pose (League
units): Leona's crown spikes stand about 12 units above her hair, which doubled with the head and, counted
as the crown, shrank everything else (height 34 left her face six rows); with "crown": 165 the hair's top is
the crown and the spikes stand above it like a hat.

"face_track": {"offset": [dx, dy]} adds "face": [x, y, facing, side] to every frame in the cells table: the
point dx, dy game px from League's head joint in the design pose (the design's face), carried on the
head's up / forward plane through every pose, how far the face turns to the camera (1 straight at it,
below 0 turned away) and whether it looks to the screen's right (+1) or left (-1); restyle_native.py
draws the design's eyes and mouth there. A tag's "hide" leaves chains out of that tag only (Yasuo's
drawn sword has no track in his death clip and stands upright beside him), and a frame's "hide" out of that
frame only: Annie throws her teddy away as she dies and holds it up to summon Tibbers, and a bear flying
off across the cell, or held over her face, read as clutter at game size - it is gone once it leaves her.

Spec (JSON): {"hero", "champ", "camera": {"yaw", "pitch", "mirror"}, "chibi": {"head", "legs",
"hair", "keep": {"<joint>": <radius>}, "scale": {"<joint>": <factor>}}, "height", "cell": [w, h] or [w, h, feet] (optional, default 56x64, feet line 10 px above the bottom), "design": "<clip@ms>", "tags": {"<tag>": {"lunge": 1.0, "rise": 1.0, "anchor": "design",
"flat": false, "head_like": null, "frames": [["<clip@ms or clipA@ms>clipB@ms:w>", <ms>, {"turn": <deg>,
"head_like": "<clip@ms>", "hide": ["<joint regex>"]}], ...]}}} (the third item is optional; its "head_like"
and "hide" override the tag's for that frame, null turns them off). The renders show
Riot's model: keep them local, never commit them (the spec and the cells table are fine).
"""
import argparse
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
import pose_ref as P  # noqa: E402
from native_refs import CELL, FEET_ROW, Z, layout  # noqa: E402
from riot import Wad  # noqa: E402

BG = (225, 225, 225)
PARTS = [(0, 0, 255), (255, 0, 0), (0, 255, 0)]          # --parts colours: body, head (with its hair), weapon
HAIR_PART = (255, 255, 0)                                 # with "hair_part": the hair chains apart from the head
EXTRA_PARTS = [(0, 255, 255), (255, 0, 255)]              # the spec's "parts", in order: cyan, magenta
PART_TEX = Image.new("RGBA", (len(PARTS), 1))
for _k, _c in enumerate(PARTS):
    PART_TEX.putpixel((_k, 0), _c + (255,))
PIVOT_ROW = FEET_ROW - 12            # base sprites: pivot 11.5 px above the soles


def set_cell(w, h, feet=10):
    """A bigger cell than native_refs.py's 56x64 (Lee Sin's braid and flying kick need 64x72);
    the feet line `feet` px above the bottom (10; Darius's axe lands 16 px below his soles: 18)."""
    global CELL, FEET_ROW, PIVOT_ROW
    CELL, FEET_ROW = (w, h), h - feet
    PIVOT_ROW = FEET_ROW - 12


class Champ:
    """A champion's base skin: mesh, skeleton, texture and clips, read from the local client."""

    def __init__(self, lol, champ, keep=None, weapon=r"^weapon$", hide=(), hair_part=False, crown=None, extra=(),
                 hide_submeshes=False):
        w = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", f"{champ}.wad.client"))
        skin_bin = w.read_path(f"data/characters/{champ.lower()}/skins/skin0.bin")
        refs = lambda blob, ext: sorted(set(m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\." + ext, blob)))
        skn = [p for p in refs(skin_bin, rb"skn") if "/Base/" in p][0]
        skl = [p for p in refs(skin_bin, rb"skl") if "/Base/" in p][0]
        texs = P.diffuse_textures(refs(skin_bin, rb"(?:tex|dds)"), skin_bin, skn)
        skn_bytes = w.read_path(skn.lower())
        self.tris, self.verts = P.read_skn(skn_bytes)
        if hide_submeshes:   # the props the skin shows only in some clips (Teemo's mushroom and harmonica)
            subs = P.skn_submeshes(skn_bytes)
            self.tris = P.drop_submeshes(self.tris, subs, P.hidden_submeshes(skin_bin, {s[0] for s in subs}))
        self.joints, self.influences = P.read_skl(w.read_path(skl.lower()))
        self.influences, self.hair_re = P.keep_parts(self.joints, self.influences, self.verts, keep or {})
        for pat in hide:     # props the clips leave unanimated (Yasuo's flute floats beside him)
            gone = P.chain_vertices(self.joints, self.influences, self.verts, re.compile(pat, re.I))
            self.tris = self.tris[~gone[self.tris].any(1)]
        self.tex = P.read_tex(w.read_path(texs[0].lower()))
        bind = P.globals_(self.joints, [P.trs(j["t"], j["r"], j["s"]) for j in self.joints])
        self.bind_inv = [np.linalg.inv(m) for m in bind]
        anims = refs(w.read_path(f"data/characters/{champ.lower()}/animations/skin0.bin"), rb"anm")
        self.by_name = {os.path.splitext(os.path.basename(a))[0].lower(): a for a in anims}
        self.wad, self.loaded = w, {}
        self.legv = P.leg_vertices(self.joints, self.influences, self.verts)
        head = P.chain_vertices(self.joints, self.influences, self.verts, re.compile(r"^head$", re.I))
        hair = P.chain_vertices(self.joints, self.influences, self.verts, self.hair_re)
        self.headv = head & ~hair
        if crown is not None:      # spikes on the head (Leona's crown) do not count as its top
            self.headv &= self.verts["pos"][:, 1] <= crown
        self.head = next(i for i, j in enumerate(self.joints) if j["name"].lower() == "head")
        on = lambda pat: P.chain_vertices(self.joints, self.influences, self.verts, re.compile(pat, re.I))
        up = np.linalg.inv(bind[self.head][:3, :3]) @ np.array([0.0, 1.0, 0.0])
        self.head_up = up / np.linalg.norm(up)          # the head joint's axis that points up in the bind pose
        fwd = np.linalg.inv(bind[self.head][:3, :3]) @ np.array([0.0, 0.0, 1.0])
        fwd = fwd - fwd.dot(self.head_up) * self.head_up
        self.head_fwd = fwd / np.linalg.norm(fwd)       # and the one the face looks along (models face +Z)
        self.part = np.where(on(r"^head$"), 1, np.where(on(weapon), 2, 0))     # index into PARTS
        self.parts, self.part_tex = PARTS, PART_TEX
        if hair_part:      # Yasuo's ponytail swings on its own: a part of its own, voted like the body
            self.part = np.where((self.part == 1) & hair, 3, self.part)
            self.parts = PARTS + [HAIR_PART]
            self.part_tex = Image.new("RGBA", (len(self.parts), 1))
            for k, c in enumerate(self.parts):
                self.part_tex.putpixel((k, 0), c + (255,))
        if extra:          # Leona's shield: a prop of its own on the body, voted and outlined apart from it
            self.parts = list(self.parts)
            for k, ex in enumerate(extra):
                self.part = np.where(on(ex["joints"]) & (self.part == 0), len(self.parts), self.part)
                self.parts.append(EXTRA_PARTS[k])
            self.part_tex = Image.new("RGBA", (len(self.parts), 1))
            for k, c in enumerate(self.parts):
                self.part_tex.putpixel((k, 0), c + (255,))

    def clip(self, name):
        if name.lower() not in self.by_name:
            raise SystemExit(f"no clip {name!r}; clips: {', '.join(sorted(self.by_name))}")
        if name.lower() not in self.loaded:
            self.loaded[name.lower()] = P.read_anim(self.wad.read_path(self.by_name[name.lower()].lower()))
        return self.loaded[name.lower()]

    def local(self, spec, head_like=None):
        a, ta, b, tb, wgt = P.parse_frame(spec)
        local = P.local_pose(self.joints, self.clip(a), ta)
        local = P.blend_pose(local, P.local_pose(self.joints, self.clip(b), tb), wgt) if b else local
        return self.head_turned(local, head_like) if head_like else local

    def head_turned(self, local, spec):
        """`local` with the head joint turned to its world orientation in pose `spec`. The hair
        chains keep the world orientation the clip gives them (the braid still streams behind);
        everything else on the head turns with it."""
        want = unscaled(P.globals_(self.joints, [P.trs(*p) for p in self.local(spec)])[self.head][:3, :3])
        was = P.globals_(self.joints, [P.trs(*p) for p in local])
        t, _, s = local[self.head]
        out = list(local)
        out[self.head] = (t, quat(unscaled(was[self.joints[self.head]["parent"]][:3, :3]).T @ want), s)
        for i, j in enumerate(self.joints):
            if j["parent"] == self.head and P.HAIR.search(j["name"]):
                ti, _, si = local[i]
                out[i] = (ti, quat(want.T @ unscaled(was[i][:3, :3])), si)
        return out

    def posed(self, spec, chibi, turn=0.0, head_like=None, rise=1.0, travel=1.0):
        """World vertices of the chibi model in a pose, feet where League has them, and the chibi
        skeleton's global matrices; `turn` degrees about the vertical axis through the unit (a
        spin or a bent-over slam turned toward the camera so the chest shows, as animators cheat);
        `rise` the share of League's height above the floor kept when the whole body is off the
        ground (Darius's Noxian Guillotine leaps five metres: 0.3 keeps it inside the cell); `travel` the
        share of the root joint's way across the floor kept (Teemo's death throws him 320 units back,
        out of the render: 0.3)."""
        local = self.local(spec, head_like)
        glob = P.globals_(self.joints, [P.trs(*p) for p in P.chibi(self.joints, local, **chibi, hair_re=self.hair_re)])
        pv = P.skin(self.verts, self.influences, self.bind_inv, glob)
        adult = P.skin(self.verts, self.influences, self.bind_inv, P.globals_(self.joints, [P.trs(*p) for p in local]))
        lift = adult[self.legv, 1].min() - pv[self.legv, 1].min()
        pv[:, 1] += lift
        if rise != 1.0:
            drop = (1.0 - rise) * max(0.0, adult[self.legv, 1].min())
            pv[:, 1] -= drop
            glob = [np.vstack([np.c_[g[:3, :3], g[:3, 3] - np.array([0.0, drop, 0.0])], g[3]]) for g in glob]
        if travel != 1.0:
            away = (1.0 - travel) * np.array([glob[0][0, 3], 0.0, glob[0][2, 3]])
            pv = pv - away
            glob = [np.vstack([np.c_[g[:3, :3], g[:3, 3] - away], g[3]]) for g in glob]
        if turn:
            c, s = np.cos(np.radians(turn)), np.sin(np.radians(turn))
            r = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
            pv = pv @ r.T
            glob = [np.vstack([np.c_[r @ g[:3, :3], r @ g[:3, 3]], g[3]]) for g in glob]
        return pv, glob, lift


def unscaled(m):
    return m / np.linalg.norm(m, axis=0)


def quat(m):
    """Rotation matrix -> quaternion (x, y, z, w), the order pose_ref.qmat reads."""
    w = np.sqrt(max(0.0, 1 + m[0, 0] + m[1, 1] + m[2, 2])) / 2
    x = np.copysign(np.sqrt(max(0.0, 1 + m[0, 0] - m[1, 1] - m[2, 2])) / 2, m[2, 1] - m[1, 2])
    y = np.copysign(np.sqrt(max(0.0, 1 - m[0, 0] + m[1, 1] - m[2, 2])) / 2, m[0, 2] - m[2, 0])
    z = np.copysign(np.sqrt(max(0.0, 1 - m[0, 0] - m[1, 1] + m[2, 2])) / 2, m[1, 0] - m[0, 1])
    return np.array([x, y, z, w])


def camera(cam):
    yaw = -cam["yaw"] if cam.get("mirror") else cam["yaw"]
    cy, sy = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
    cp, sp = np.cos(np.radians(cam["pitch"])), np.sin(np.radians(cam["pitch"]))
    return np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])


def render(ch, pv, cam, scale, dy, tris=None, parts=False):
    """8x render two cells wide (RGBA float), the unit's origin at the centre of game column
    CELL[0] and dy px (8x) below the feet line; frames are cut out of it by their content.
    `tris` renders only those triangles (default: the whole model); `parts` paints each triangle
    flat in the PARTS colour of what most of its corners follow (the shading keeps the hue)."""
    W, H = 2 * CELL[0] * Z, CELL[1] * Z
    x0 = (CELL[0] + 0.5) * Z
    shift = x0 / W - 0.5
    yaw = cam["yaw"]
    tris = ch.tris if tris is None else tris
    uv, tex = ch.verts["uv"], ch.tex
    if parts:
        n = np.stack([(ch.part[tris] == k).sum(1) for k in range(len(ch.parts))], 1).argmax(1)
        pv, tris = pv[tris].reshape(-1, 3), np.arange(3 * len(tris)).reshape(-1, 3)
        uv, tex = np.c_[(np.repeat(n, 3) + 0.5) / len(ch.parts), np.full(len(pv), 0.5)], ch.part_tex
    if cam.get("mirror"):
        img = P.render_hq(pv, tris, uv, tex, -yaw, cam["pitch"], (W, H), scale,
                          FEET_ROW * Z + dy, -shift).transpose(Image.FLIP_LEFT_RIGHT)
    else:
        img = P.render_hq(pv, tris, uv, tex, yaw, cam["pitch"], (W, H), scale, FEET_ROW * Z + dy, shift)
    return np.asarray(img).astype(np.float32)


def blocks(img):
    """8x render -> game pixels: mean colour of the covered part of each 8x8 block, opaque when
    at least half covered."""
    h, w = img.shape[0] // Z, img.shape[1] // Z
    b = img.reshape(h, Z, w, Z, 4)
    a = (b[..., 3] >= 128).astype(np.float32)
    cov = a.mean((1, 3))
    col = (b[..., :3] * a[..., None]).sum((1, 3)) / np.maximum(a.sum((1, 3))[..., None], 1)
    out = np.zeros((h, w, 4), np.uint8)
    on = cov >= 0.5
    out[on, :3] = np.clip(np.round(col[on]), 0, 255)
    out[on, 3] = 255
    return out


def on_bg(a):
    img = Image.new("RGBA", (a.shape[1], a.shape[0]), BG + (255,))
    img.alpha_composite(Image.fromarray(a, "RGBA"))
    return img.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol", help="League install folder")
    ap.add_argument("--tag", action="append", help="only these tags (default: all, plus the design canvas)")
    ap.add_argument("--alpha", action="store_true",
                    help="write <hero>_pose_<tag>.png on a transparent background instead of grey (to recolour it)")
    ap.add_argument("--parts", action="store_true",
                    help="also write <hero>_parts_<tag>.png: the same frames painted by part (PARTS colours)")
    args = ap.parse_args()
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    hero, cam, chibi = spec["hero"], spec["camera"], dict(spec["chibi"])
    keep = chibi.pop("keep", None)
    set_cell(*spec.get("cell", CELL))
    ch = Champ(args.lol, spec["champ"], keep, spec.get("weapon", r"^weapon$"), spec.get("hide", ()),
               spec.get("hair_part", False), spec.get("crown"), spec.get("parts", ()), spec.get("hide_submeshes", False))
    rot = camera(cam)
    sign = -1.0 if cam.get("mirror") else 1.0
    os.makedirs(args.out, exist_ok=True)

    # scale: the design pose is `height` game px from the crown to the soles, seen through the camera
    pv, glob, _ = ch.posed(spec["design"], chibi)
    cv = pv @ rot.T
    unit = spec["height"] / (cv[ch.headv, 1].max() - cv[ch.legv, 1].min())       # game px per world unit
    scale = unit * Z

    def head_x(g):
        return sign * (rot @ g[ch.head][:3, 3])[0] * unit

    ref_head = head_x(glob)

    def face_axes(g):
        """The head's up and forward axes in camera space (scaled like the chibi head)."""
        m = g[ch.head][:3, :3]
        return rot @ (m @ ch.head_up), rot @ (m @ ch.head_fwd)

    def face_jacobian(g):
        """Game px on screen per unit along the head's up and forward axes (columns)."""
        u, f = face_axes(g)
        return np.array([[sign * u[0] * unit, sign * f[0] * unit], [-u[1] * unit, -f[1] * unit]])

    # "face_track": {"offset": [dx, dy]} - where the design's face point is from League's head joint in the
    # design pose (game px); held as a point on the head's up / forward plane, it follows the head
    track = None
    if "face_track" in spec:
        track = np.linalg.solve(face_jacobian(glob), np.array(spec["face_track"]["offset"], float))
    # one vertical offset for every frame: the design pose's lowest point on the feet line
    probe = blocks(render(ch, pv, cam, scale, 0.0))
    dy = (FEET_ROW - 1 - np.nonzero(probe[..., 3].any(1))[0].max()) * Z
    design = blocks(render(ch, pv, cam, scale, dy))
    rows = np.nonzero(design[..., 3].any(1))[0]
    # the pivot is 11.5 px above the soles, found in a render of the legs alone: Darius's axe hangs
    # 5 px below his, and a pivot counted from the axe tip left him floating 5 px in game
    global PIVOT_ROW
    legs = np.zeros(len(pv), bool)
    legs[ch.legv] = True
    soles = np.nonzero(blocks(render(ch, pv, cam, scale, dy, ch.tris[legs[ch.tris].all(1)]))[..., 3].any(1))[0].max()
    # "hover": the whole sprite floats that many px above the ground in game (the pivot moves down)
    PIVOT_ROW = int(soles) + 1 - 12 + int(spec.get("hover", 0))
    print(f"{hero}: {unit * 100:.3f} game px per 100 units; design pose {rows.max() - rows.min() + 1} px tall with "
          f"what hangs from the head, lowest point on row {rows.max()}, soles on row {soles}, offset {dy / Z:+.0f} px"
          + (f", hovering {spec['hover']} px" if spec.get("hover") else ""))

    def cell(frame_spec, lunge, base, flat, turn=0.0, head_like=None, rise=1.0, hide=None, travel=1.0, sink=0):
        pv, glob, _ = ch.posed(frame_spec, chibi, turn, head_like, rise, travel)
        tris = None
        if hide:           # a prop the clip leaves where it was bound (Yasuo's drawn sword stands up in death)
            gone = np.zeros(len(ch.verts), bool)
            for pat in hide:
                gone |= P.chain_vertices(ch.joints, ch.influences, ch.verts, re.compile(pat, re.I))
            tris = ch.tris[~gone[ch.tris].any(1)]
        hi = render(ch, pv, cam, scale, dy, tris)
        lo = blocks(hi)
        down = 0
        if flat:   # lowest point as high above the feet line as it is above League's floor
            lift = int(round(max(0.0, pv[:, 1].min()) * unit * np.cos(np.radians(cam["pitch"]))))
            down = (FEET_ROW - 1 - lift) - np.nonzero(lo[..., 3].any(1))[0].max()
        down += int(sink)  # a hovering hero's frames that come down to the ground (Janna's death)
        if down:
            hi = render(ch, pv, cam, scale, dy + down * Z, tris)
            lo = blocks(hi)
        hx = head_x(glob)
        head_y = FEET_ROW + dy / Z + down - (rot @ glob[ch.head][:3, 3])[1] * unit
        su = rot @ (glob[ch.head][:3, :3] @ ch.head_up)
        tilt = np.degrees(np.arctan2(sign * su[0], su[1]))      # where the crown points on screen, clockwise from up
        pivot = CELL[0] + int(round((1.0 - lunge) * (hx - base) + (base - ref_head)))
        ys, xs = np.nonzero(lo[..., 3])
        if len(xs) == 0:
            raise SystemExit(f"{frame_spec}: nothing in the cell")
        clipped = []
        if ys.min() == 0:
            clipped.append("top")
        if xs.max() - xs.min() + 1 > CELL[0] or xs.min() == 0 or xs.max() == lo.shape[1] - 1:
            clipped.append("sides")
        x0 = xs.min() - (CELL[0] - (xs.max() - xs.min() + 1)) // 2          # the cell's left edge
        x0 = min(max(x0, 0), lo.shape[1] - CELL[0])
        lo = lo[:, x0:x0 + CELL[0]]
        hi = np.clip(hi, 0, 255).astype(np.uint8)[:, x0 * Z:(x0 + CELL[0]) * Z]
        pa = None
        if args.parts:
            pa = np.clip(render(ch, pv, cam, scale, dy + down * Z, tris, parts=True), 0, 255).astype(np.uint8)
            pa = pa[:, x0 * Z:(x0 + CELL[0]) * Z]
        face = None
        if track is not None:     # the face point, how much the face looks at the camera, and which way (+1 right)
            off = face_jacobian(glob) @ track
            fz = face_axes(glob)[1]
            fz = fz / np.linalg.norm(fz)
            face = (CELL[0] + 0.5 + hx - x0 + off[0], head_y + off[1], float(fz[2]), float(np.sign(sign * fz[0]) or 1.0))
        return lo, hi, (pivot - x0, PIVOT_ROW), hx - ref_head, clipped, (CELL[0] + 0.5 + hx - x0, head_y, tilt), pa, face

    table = {}
    tags = args.tag or list(spec["tags"])
    for tag in tags:
        t = spec["tags"][tag]
        base = ref_head
        if t.get("anchor", "design") == "first":
            base = head_x(ch.posed(t["frames"][0][0], chibi, head_like=t.get("head_like"), travel=t.get("travel", 1.0))[1])
        opt = lambda f: f[2] if len(f) > 2 else {}
        frames = [cell(f[0], t.get("lunge", 1.0), base, t.get("flat", False), opt(f).get("turn", 0.0),
                       opt(f).get("head_like", t.get("head_like")), t.get("rise", 1.0), opt(f).get("hide", t.get("hide")),
                       t.get("travel", 1.0), opt(f).get("sink", t.get("sink", 0))) for f in t["frames"]]
        cols, nrows = layout(len(frames))
        lo_img = Image.new("RGB", (cols * CELL[0], nrows * CELL[1]), BG)
        hi_img = Image.new("RGBA" if args.alpha else "RGB", (cols * CELL[0] * Z, nrows * CELL[1] * Z),
                           (0, 0, 0, 0) if args.alpha else BG)
        for k, (lo, hi, *_) in enumerate(frames):
            cx, cy = k % cols, k // cols
            lo_img.paste(on_bg(lo), (cx * CELL[0], cy * CELL[1]))
            hi_img.paste(Image.fromarray(hi, "RGBA") if args.alpha else on_bg(hi), (cx * CELL[0] * Z, cy * CELL[1] * Z))
        lo_img.resize((lo_img.width * Z, lo_img.height * Z), Image.NEAREST).save(
            os.path.join(args.out, f"{hero}_native_{tag}.png"))
        hi_img.save(os.path.join(args.out, f"{hero}_pose_{tag}.png"))
        if args.parts:
            pa_img = Image.new("RGBA", hi_img.size, (0, 0, 0, 0))
            for k, fr in enumerate(frames):
                pa_img.paste(Image.fromarray(fr[6], "RGBA"), (k % cols * CELL[0] * Z, k // cols * CELL[1] * Z))
            pa_img.save(os.path.join(args.out, f"{hero}_parts_{tag}.png"))
        table[tag] = [{"pivot": list(map(int, p)), "ms": int(ms), "head": [round(float(h[0]), 1), round(float(h[1]), 1)],
                       "tilt": int(round(float(h[2]))),
                       **({"face": [round(float(fc[0]), 1), round(float(fc[1]), 1), round(float(fc[2]), 2), int(fc[3])]} if fc else {})}
                      for (_, _, p, _, _, h, _, fc), (_, ms, *_) in zip(frames, t["frames"])]
        colours = len(np.unique(np.concatenate([lo[lo[..., 3] > 0][:, :3] for lo, *_ in frames]), axis=0))
        print(f"{hero}_native_{tag}.png  {len(frames)} frames, {cols}x{nrows} cells, {colours} colours; head x from the "
              f"design pose " + " ".join(f"{fr[3]:+.1f}" for fr in frames) +
              "".join(f"\n  frame {k + 1} touches the cell's {' and '.join(fr[4])}" for k, fr in enumerate(frames) if fr[4]))

    if not args.tag:
        canvas = np.zeros((128, 128, 4), np.uint8)
        ys, xs = np.nonzero(design[..., 3])
        crop = design[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        top, left = 100 - crop.shape[0], (128 - crop.shape[1]) // 2
        canvas[top:100, left:left + crop.shape[1]] = crop
        on_bg(canvas).resize((128 * Z, 128 * Z), Image.NEAREST).save(os.path.join(args.out, f"{hero}_native_design.png"))
        hi = np.clip(render(ch, pv, cam, scale, dy), 0, 255).astype(np.uint8)
        big = np.zeros((128 * Z, 128 * Z, 4), np.uint8)
        y0, x0 = (top - ys.min()) * Z, (left - xs.min()) * Z
        sy0, sx0 = max(0, -y0), max(0, -x0)
        h = min(hi.shape[0] - sy0, big.shape[0] - max(0, y0))
        w = min(hi.shape[1] - sx0, big.shape[1] - max(0, x0))
        big[max(0, y0):max(0, y0) + h, max(0, x0):max(0, x0) + w] = hi[sy0:sy0 + h, sx0:sx0 + w]
        on_bg(big).save(os.path.join(args.out, f"{hero}_pose_design.png"))
        # "tilt" (where the crown points, degrees clockwise from up) only for a head leaning past 45 degrees:
        # a lying body, whose drawn head a restyle turns by quarter turns
        lines = [f'  "{tag}": [' + ", ".join(f'{{"pivot": [{r["pivot"][0]}, {r["pivot"][1]}], "ms": {r["ms"]}, '
                                             f'"head": [{r["head"][0]}, {r["head"][1]}]' +
                                             (f', "tilt": {r["tilt"]}' if abs(r["tilt"]) >= 45 else "") +
                                             (f', "face": {r["face"]}' if "face" in r else "") + "}"
                                             for r in rows_) + "]" for tag, rows_ in table.items()]
        text = f'{{"cell": [{CELL[0]}, {CELL[1]}], "scale": {Z}, "tags": {{\n' + ",\n".join(lines) + "\n}}\n"
        json.loads(text)
        with open(os.path.join(args.out, f"{hero}_cells.json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"{hero}_native_design.png, {hero}_pose_design.png, {hero}_cells.json")


if __name__ == "__main__":
    main()
