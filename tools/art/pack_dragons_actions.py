"""Step-2 Codex pack for league_dragons' Rift monsters: their ACTIONS drawn in the designs Codex delivered in step 1
(outputs/dragons-models/<model>-A.png, 2026-11-09), every frame in LEAGUE'S OWN POSE at that moment (the user,
2026-11-09: 「codex交付了小龙和大龙的 攻击动作没有吧？你看看 如果没有的话继续补」「你要参考英雄联盟里面的攻击姿势啊」).

    python tools/art/pack_dragons_actions.py --designs <Codex outputs/dragons-models> --out <dir> --prompt <md>
        [--lol "D:/Riot Games/League of Legends"] [--only model ...]

What League plays (Map11.wad.client, the anim graphs read 2026-11-09):
- Drakes and the Elder (one animation set, one skeleton): the basic attack `attack1` is a MASKED clip (mask 1167440125:
  Spine4 0.4, Neck, Neck1, Head, Jaw, gills, Buffbone_Cstm_FireStart) laid over whatever the body plays - the head
  rears up and back (100-300 ms), swings down (500-600), thrusts down at the viewer with the jaws wide (700-1000: the
  spit), comes back (1100-1600). So the attack here = THE DESIGN'S BODY UNCHANGED + League's neck / head / jaw at that
  time (rendered with the mask over the stance, the design's own pose). `spell1` (BA2, the breath) is the same move.
  The six `aggro` clips of the idle selector (tail raised, wings spread) are fidgets of the aggro idle, not attacks;
  the unmasked `attack1` is meaningless alone (the body joints have no keys: it lies flat under the ground).
  `death` (8.47 s): launches up, twists in the air (0-750), crashes head first (900), sprawls on its side (1050-1350),
  writhes (1500-3000), lies still (from ~5600).
- Baron (sru_baron): `attack1` = a selector of two ParametricClipData over the target's angle (-90 / -45 / 0 / 45 / 90);
  the -90 child (key ef242363) turns the heads to the picture's LEFT, rears back (250 ms) and lunges down-left (375-500)
  - our attack_left; attack_right is its mirror (made by us, like Morgard's). `death` (5.03 s): rears back, the heads
  thrown up (500), lurches forward (1000-1500), slumps to its side (2250), the head rolls back to the sky (3000-5000).
The game's tags (pack_dragons.TAGS) stay: drakes / Elder idle 4 x 160, base, attack 5 x 80 (hit at tick 18 of 24 =
300 ms = the 4th frame), dead 8 x 80; Baron idle 4, base, attack_left 5 x 80 (hit in the 4th), attack_right = mirror,
attack_target_effect 7 x 60, dead 13 x 60. Codex draws: attack 1-5 and dead 1-6 of every drake and the Elder; Baron's
attack_left 1-5, the target effect (one sheet, 7 cells) and dead 1-8. Ours: idle (a breath made from the design), base
(the design), attack_right (mirror), the last dead frames (the drawn dissolve thinned out, then empty).

Writes <out>/design/<model>.png (Codex's step-1 picture), <out>/league/<model>/<tag>_<k>.png (League's rest pose and
this frame side by side at one scale, the head scaled up like our chibi designs - CHIBI), <out>/templates/<model>/
<tag>_<k>.png (the frame's canvas: the layout lines of step 1, attack frames the design faded = the body to keep, other
frames League's pose at the design's scale as a pale silhouette = where and how big; the label gives the frame, its
time in the game, its League time and the head's move in squares), <out>/overview/<model>.png (all of a model's League
poses in order), <out>/native/ (the game's Serpen and Morgard frames: timing), SPEC2.json, the prompt, then <out>.zip.
The League renders are Riot's: kept local, never committed.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack_dragons as D  # noqa: E402

P, G = D.P, D.G
GREY = D.GREY
ATTACK1, DEATH = G.fnv1a("attack1"), G.fnv1a("death")
BARON_LEFT = 0xEF242363              # sru_baron attack at -90 deg (ParametricClipData 10dca888): strikes to the left
MASK = 1167440125                    # the drakes' attack mask
CHIBI = {"drake": 1.45, "elder": 1.45, "baron": 1.0}   # League head scale for the references (our designs are chibi)
SILHOUETTE = (150, 160, 185)
# (tag, frame, clip, League ms, masked, what happens) - frames are 1-based, the game's own durations from TAGS
DRAKE_FRAMES = [
    ("attack", 1, ATTACK1, 200, True, "wind-up: the head rises and pulls back over the shoulders, the chin up, the jaws "
                                      "parting, the throat glowing"),
    ("attack", 2, ATTACK1, 300, True, "reared back at the top: the head highest and tipped back, the jaws open, the "
                                      "element gathering in the mouth"),
    ("attack", 3, ATTACK1, 600, True, "the strike begins: the head swings down and forward, the jaws opening wide, the "
                                      "element bursting out between the fangs"),
    ("attack", 4, ATTACK1, 900, True, "HIT: the head thrust down at the viewer at its lowest, the jaws WIDEST, the "
                                      "element blasting out of the mouth (the spit)"),
    ("attack", 5, ATTACK1, 1200, True, "recovery: the head coming back up, the jaws closing, the blast fading to wisps"),
    ("dead", 1, DEATH, 150, False, "struck: it rears up, the body upright, the wings swept down along its sides, the "
                                   "head lifted, roaring"),
    ("dead", 2, DEATH, 450, False, "twisting as it falls: the body curled sideways, the wings curling, the head turning "
                                   "down"),
    ("dead", 3, DEATH, 900, False, "the crash: it hits the ground head first, one wing flung up"),
    ("dead", 4, DEATH, 1200, False, "sprawled on its side on the ground, the wings spread flat, the tail stretched out"),
    ("dead", 5, DEATH, 5600, False, "lying still on its belly: the head down on the ground, the eyes shut, one wing half "
                                    "raised"),
    ("dead", 6, DEATH, 5600, False, "the same lying pose DISSOLVING into its element: about half of the body gone, the "
                                    "rest breaking up"),
]
BARON_FRAMES = [
    ("attack_left", 1, BARON_LEFT, 125, False, "the heads turn to the picture's LEFT and rear back, the jaws parting"),
    ("attack_left", 2, BARON_LEFT, 250, False, "reared back at the top: the neck coiled, all the jaws open (the side "
                                               "heads too)"),
    ("attack_left", 3, BARON_LEFT, 330, False, "lunging down to the LEFT, the neck arching"),
    ("attack_left", 4, BARON_LEFT, 420, False, "HIT: the heads at their farthest reach down-left, the jaws snapping shut"
                                               " on the target, the claw-legs splayed out"),
    ("attack_left", 5, BARON_LEFT, 625, False, "recoiling: the heads coming back up toward the centre"),
    ("dead", 1, DEATH, 250, False, "struck: rearing back, the heads thrown up roaring, the claw-legs lifting"),
    ("dead", 2, DEATH, 500, False, "the heads thrown back as far as they go, the claw-legs flung up and out"),
    ("dead", 3, DEATH, 1000, False, "lurching forward: the heads swinging down"),
    ("dead", 4, DEATH, 1500, False, "swaying: the heads forward and down, the claw-legs spread"),
    ("dead", 5, DEATH, 2250, False, "slumping to the picture's left: the heads drooping, the claw-legs curling in"),
    ("dead", 6, DEATH, 3000, False, "sagging: the head rolling up and back"),
    ("dead", 7, DEATH, 4000, False, "stiff: the head tipped back to the sky, the jaws open, the claw-legs curled up"),
    ("dead", 8, DEATH, 5000, False, "the same stiff pose BREAKING APART into purple void motes and magenta sparks: about"
                                    " half of it gone"),
]
# each element's spit (attack 2-5) and dissolve (dead 6)
ELEMENT = {
    "infernal": ("a gout of FIRE: an orange-yellow fireball with flame tongues and a few sparks",
                 "glowing EMBERS and ash flakes drifting up"),
    "mountain": ("a blast of STONE: pale rock shards and brown dust", "a heap of pale STONES and dust"),
    "ocean": ("a burst of WATER: a teal-blue water blast with white foam and droplets", "a splash of teal WATER and "
                                                                                         "droplets"),
    "cloud": ("a GUST: pale white and light-blue swirling wind curls", "pale wisps of MIST and swirling wind curls"),
    "hextech": ("crackling HEXTECH LIGHTNING: a bright blue-white energy orb with zig-zag arcs", "blue crystal shards "
                                                                                                  "and crackling SPARKS"),
    "chemtech": ("a spray of CHEMTECH GOO: bright toxic-green globs and green gas", "a puddle of toxic green GOO and gas"
                                                                                    " bubbles"),
    "elder": ("a burst of ELDER FLAME: cyan-white and violet ethereal fire", "violet and cyan ETHEREAL FLAME wisps"),
}
DESIGN_FILE = {"baron": "baron-A.png", "elder": "elder-A.png", **{d: f"drake_{d}-A.png" for d in D.DRAKES}}
EFFECT_CELL = (384, 512)             # Baron's target effect: 7 cells of a 4 x 2 grid on 1536 x 1024
EFFECT_MAX = 63                      # its widest / tallest in squares (42 game px at PPU 1.5; Morgard's 31-51 x 33-41)


def mask_weights(m):
    b = m.w.read_path(f"data/characters/{D.MODELS[m.name][0]}/animations/skin0.bin")
    for _cls, fields in G.parse_prop(b):
        for _k, v in fields.items():
            if isinstance(v, list) and v and isinstance(v[0], tuple) and isinstance(v[0][1], dict) \
                    and "#a3c80380" in v[0][1]:
                for key, mk in v:
                    if key == MASK:
                        return np.array(mk["#a3c80380"], float)
    raise SystemExit(f"{m.name}: attack mask {MASK} not found")


def pose(m, clip, ms, masked, chibi, w=None):
    """Skinned vertices of League's pose at ms: the clip alone, or (masked) the clip's masked joints over the stance
    (the design's pose) by the mask's weights; the head scaled by chibi. clip None = the rest pose."""
    def local(file, t):
        a = P.read_anim(m.w.read(file))
        return P.local_pose(m.joints, a, min(t / 1000.0, max(a["duration"] - 1e-3, 0.0)))
    if clip is None:
        # the rest pose = League's idle at 0 ms (the drakes' stance = our design's pose). Baron's design was drawn
        # from his BIND pose, but every clip of his rises higher out of the pit than the bind pose does (his attack's
        # head ~40 squares above the bind pose's at the design's scale): his idle is the size the actions keep
        loc = local(m.idle, 0.0)
    elif masked:
        base, over = local(m.idle, 0.0), local(m.clips[clip], ms)
        loc = []
        for i, (pb, po) in enumerate(zip(base, over)):
            wi = w[i] if i < len(w) else 0.0
            loc.append(po if wi >= 1 else pb if wi <= 0 else P.blend_pose([pb], [po], wi)[0])
    else:
        loc = local(m.clips[clip], ms)
    loc = P.chibi(m.joints, loc, head=chibi)
    glob = P.globals_(m.joints, [P.trs(*p) for p in loc])
    return P.skin(m.v, m.infl, m.bind_inv, glob)


def tris_of(m, pv):
    return m.tris[pv[m.tris].mean(1)[:, 1] >= 0.0] if m.name == "baron" else m.tris


def placement(m, kind, rest):
    """(scale, ground, shift) putting the rest pose on step 1's layout lines: drakes - the lowest point on the soles
    line, the projected height = the design's; Baron - his part above the pit (y >= 0) the same way, its lowest projected
    point on the pit line (step 1's guide)."""
    k, t = D.KINDS[kind], D.target(kind)
    v = D.rotated(rest, 0, D.PITCH)[np.unique(tris_of(m, rest))]
    lo = v[:, 1].min()                  # (Baron: the lowest projected point of the part above the pit, as step 1)
    scale = t["px_h"] / (v[:, 1].max() - lo)
    cw = k["canvas"][0]
    cx = (v[:, 0].min() + v[:, 0].max()) / 2
    return scale, k["sole_y"] + lo * scale, (k["centre_x"] - cx * scale) / cw - 0.5


def render_on(m, pv, place, size, dy=0.0):
    scale, ground, shift = place
    return P.render_hq(pv, tris_of(m, pv), m.v["uv"], m.tex, 0, D.PITCH, size, scale, ground + dy, shift=shift)


def head_box(m, pv, place, canvas):
    """The head's box on the canvas (px): its vertices (pack_dragons' head joints) projected with the placement."""
    scale, ground, shift = place
    v = D.rotated(pv[m.head], 0, D.PITCH)
    x = v[:, 0] * scale + canvas[0] * (0.5 + shift)
    y = ground - v[:, 1] * scale
    return x.min(), y.min(), x.max(), y.max()


def faded(design, alpha=0.38):
    can = Image.new("RGBA", design.size, GREY + (255,))
    d = design.copy()
    d.putalpha(design.getchannel("A").point(lambda a: int(a * alpha)))
    can.alpha_composite(d)
    return can


def lines(can, kind, label):
    k, t = D.KINDS[kind], D.target(kind)
    cw, ch = k["canvas"]
    d = ImageDraw.Draw(can)
    d.line([(0, k["sole_y"]), (cw, k["sole_y"])], fill=(110, 110, 110, 255), width=2)
    d.line([(0, t["top_y"]), (cw, t["top_y"])], fill=(190, 190, 190, 255), width=1)
    d.line([(k["centre_x"], 8), (k["centre_x"], ch - 8)], fill=(205, 205, 205, 255), width=1)
    try:                                   # big enough for Codex to read (PIL's default font is 11 px)
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 17)
    except OSError:
        font = None
    import textwrap
    y = 10
    for s in label:
        for part in textwrap.wrap(s, width=int(cw / 8.6)):
            d.text((14, y), part, fill=(45, 45, 45, 255), font=font)
            y += 21
    return can


def silhouette(im):
    a = im.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    sil = Image.new("RGBA", im.size, SILHOUETTE + (255,))
    sil.putalpha(a)
    return sil


def pair(m, rest, frame, box, label, cell=620):
    """League's rest pose and this frame side by side, one scale (the model's union box over all its frames)."""
    x0, x1, y0, y1 = box
    scale = cell * 0.92 / max(x1 - x0, y1 - y0)
    shift = -(x0 + x1) / 2 * scale / cell
    ground = cell / 2 + (y0 + y1) / 2 * scale
    out = Image.new("RGB", (cell * 2 + 12, cell + 24), (255, 255, 255))
    d = ImageDraw.Draw(out)
    restlab = "League: idle at 0 ms (= the design's " + ("place and size)" if m.name == "baron" else "pose)")
    for i, (pv, lab) in enumerate(((rest, restlab), (frame, label))):
        im = P.render_hq(pv, tris_of(m, pv), m.v["uv"], m.tex, 0, D.PITCH, (cell, cell), scale, ground, shift=shift)
        c = Image.new("RGBA", (cell, cell), GREY + (255,))
        c.alpha_composite(im)
        out.paste(c.convert("RGB"), (i * (cell + 12), 24))
        d.text((i * (cell + 12) + 6, 6), lab, fill=(0, 0, 0))
    return out


def effect_template(path, epic):
    """Baron's attack_target_effect: 7 cells (4 + 3) on 1536 x 1024, each with Morgard's frame at the design's density
    (1 game px = 1.5 squares = 9 px) faded as the size / timing guide, the target point as a cross."""
    cw, ch = EFFECT_CELL
    can = Image.new("RGBA", (cw * 4, ch * 2), GREY + (255,))
    d = ImageDraw.Draw(can)
    idx = epic.tag_frames("attack_target_effect")
    for i, fi in enumerate(idx):
        x0, y0 = (i % 4) * cw, (i // 4) * ch
        d.rectangle([x0 + 1, y0 + 1, x0 + cw - 2, y0 + ch - 2], outline=(200, 200, 200, 255))
        fr = epic.frames[fi]
        z = 9
        big = fr.resize((fr.width * z, fr.height * z), Image.NEAREST)
        big.putalpha(big.getchannel("A").point(lambda a: int(a * 0.35)))
        px, py = x0 + cw // 2, y0 + ch // 2 + 40          # the target point (Morgard's pivot = the frame centre)
        bx, by = px - (fr.width // 2) * z - z // 2, py - (fr.height // 2) * z - z // 2
        cx0, cy0 = max(bx, x0 + 2), max(by, y0 + 2)      # clipped to its own cell (frame 5 is wider than a cell)
        cx1, cy1 = min(bx + big.width, x0 + cw - 2), min(by + big.height, y0 + ch - 2)
        if cx1 > cx0 and cy1 > cy0:
            can.alpha_composite(big.crop((cx0 - bx, cy0 - by, cx1 - bx, cy1 - by)), (cx0, cy0))
        d.line([(px - 10, py), (px + 10, py)], fill=(150, 150, 150, 255))
        d.line([(px, py - 10), (px, py + 10)], fill=(150, 150, 150, 255))
        half = EFFECT_MAX * 6 // 2
        d.rectangle([px - half, py - half, px + half, py + half], outline=(185, 185, 185, 255))
        d.text((x0 + 8, y0 + 8), f"attack_target_effect {i + 1}/7  ({i * 60}-{i * 60 + 60} ms)", fill=(55, 55, 55, 255))
    d.text((cw * 3 + 12, ch + 12), "cell 8: leave empty", fill=(120, 120, 120, 255))
    d.text((cw * 3 + 12, ch + 30), "grey box = the most the effect may fill", fill=(120, 120, 120, 255))
    d.text((cw * 3 + 12, ch + 48), f"({EFFECT_MAX} squares of 6 px), cross = target", fill=(120, 120, 120, 255))
    can.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--designs", required=True, help="Codex's step-1 outputs/dragons-models folder")
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    for sub in ("design", "league", "templates", "overview", "native", "style"):
        os.makedirs(os.path.join(a.out, sub), exist_ok=True)
    spec = {"pitch": D.PITCH, "chibi": CHIBI, "models": {}}
    import tfm2_ase as T
    serpen = T.load_sprite("asset/base/aseprite_resources/ingame/serpen")
    epic = T.load_sprite("asset/base/aseprite_resources/ingame/epic")
    names = list(D.DRAKES) + ["elder", "baron"]
    for name in names:
        if a.only and name not in a.only:
            continue
        kind = D.KIND[name]
        k = D.KINDS[kind]
        canvas = k["canvas"]
        design = Image.open(os.path.join(a.designs, DESIGN_FILE[name])).convert("RGBA")
        assert design.size == canvas, (name, design.size)
        design.save(os.path.join(a.out, "design", f"{name}.png"))
        m = D.Model(a.lol, name)
        w = mask_weights(m) if kind != "baron" else None
        frames = BARON_FRAMES if kind == "baron" else DRAKE_FRAMES
        rest = pose(m, None, 0, False, CHIBI[kind])
        place = placement(m, kind, rest)
        poses = [pose(m, clip, ms, masked, CHIBI[kind], w) for _t, _k, clip, ms, masked, _x in frames]
        def ubox(pvs):                  # one framing for the League pictures of a tag (with the rest pose)
            b = []
            for pv in pvs:
                v = D.rotated(pv, 0, D.PITCH)[np.unique(tris_of(m, pv))]
                b.append((v[:, 0].min(), v[:, 0].max(), v[:, 1].min(), v[:, 1].max()))
            b = np.array(b)
            return b[:, 0].min(), b[:, 1].max(), b[:, 2].min(), b[:, 3].max()
        boxes = {tag: ubox([rest] + [pv for f, pv in zip(frames, poses) if f[0] == tag]) for tag in {f[0] for f in frames}}
        rh = head_box(m, rest, place, canvas)
        sq = k["sq"]
        tags = {t[0]: (t[1], t[2]) for t in D.TAGS[k["tags"]]}
        info = {"kind": kind, "canvas": list(canvas), "frames": []}
        for sub in ("league", "templates"):
            os.makedirs(os.path.join(a.out, sub, name), exist_ok=True)
        strip = []
        for (tag, fk, clip, ms, masked, what), pv in zip(frames, poses):
            n, dur = tags[tag]
            when = f"{(fk - 1) * dur}-{fk * dur} ms of {n * dur}"
            hit = " = THE HIT" if tag.startswith("attack") and fk == 4 else ""
            clipname = {ATTACK1: "attack1 (masked: neck / head / jaw)", DEATH: "death",
                        BARON_LEFT: "attack at -90 deg (toward the left)"}[clip]
            fn = f"{tag}_{fk}.png"
            pr = pair(m, rest, pv, boxes[tag], f"League {clipname} at {ms} ms (head x{CHIBI[kind]})")
            pr.save(os.path.join(a.out, "league", name, fn))
            strip.append((f"{tag} {fk}", pr.crop((pr.width // 2 + 6, 24, pr.width, pr.height))))
            label = [f"{name} {tag} {fk}/{n} ({when}{hit}): {what}", None]
            dy = 0.0
            if tag.startswith("attack") and kind != "baron":
                can = faded(design)
                label.append("PALE FIGURE = THE DESIGN: the body, the legs and the wings stay exactly on it; only the "
                             "neck, the head and the jaws move (image 2).")
            else:
                im = render_on(m, pv, place, canvas)
                bb = im.getbbox()
                if kind != "baron" and bb and bb[3] < k["sole_y"] - 2 * sq:
                    # League's drake launches itself into the air as it dies (up to ~110 squares at the design's
                    # scale): ours rears up IN PLACE - the pose lowered until its lowest point is on the ground line
                    dy = k["sole_y"] - bb[3]
                elif bb and bb[1] < 20:                     # keep the pose inside the canvas: lowered, not shrunk
                    dy = 20 - bb[1]
                if dy:
                    im = render_on(m, pv, place, canvas, dy=dy)
                can = Image.new("RGBA", canvas, GREY + (255,))
                sil = silhouette(im)
                sil.putalpha(sil.getchannel("A").point(lambda v: int(v * 0.55)))
                can.alpha_composite(sil)
                label.append("PALE FIGURE = League's pose at the design's scale (League's proportions, the head x"
                             f"{CHIBI[kind]}): where and how big; draw OUR design in this pose at the design's size."
                             + (f" (Lowered {dy / sq:.0f} squares: rearing in place, not flying up.)" if dy and
                                kind != "baron" and dy > 0 and bb[3] < k["sole_y"] else
                                f" (Lowered {dy / sq:.0f} squares to fit the canvas.)" if dy else ""))
            hb = head_box(m, pv, place, canvas)
            dtop, dbot = (hb[1] + dy - rh[1]) / sq, (hb[3] + dy - rh[3]) / sq
            dx = ((hb[0] + hb[2]) - (rh[0] + rh[2])) / 2 / sq
            label[1] = (f"League {clipname} at {ms} ms. Head vs the design's rest: top {dtop:+.0f}, lowest point "
                        f"{dbot:+.0f}, centre {dx:+.0f} squares (+ = down / right).")
            lines(can, kind, label).convert("RGB").save(os.path.join(a.out, "templates", name, fn))
            info["frames"].append({"tag": tag, "frame": fk, "ms_in_game": when, "league_clip": clipname,
                                   "league_ms": ms, "masked": masked, "what": what,
                                   "head_move_squares": [round(dtop, 1), round(dbot, 1), round(dx, 1)],
                                   "lowered_squares": round(dy / sq, 1)})
            print(name, tag, fk, "head", round(dtop, 1), round(dbot, 1), round(dx, 1), "lowered", dy)
        h = 300
        ims = [(lab, im.resize((round(im.width * h / im.height), h), Image.LANCZOS)) for lab, im in strip]
        ov = Image.new("RGB", (sum(im.width + 6 for _, im in ims), h + 20), (255, 255, 255))
        d = ImageDraw.Draw(ov)
        x = 0
        for lab, im in ims:
            ov.paste(im, (x, 20))
            d.text((x + 4, 4), lab, fill=(0, 0, 0))
            x += im.width + 6
        ov.save(os.path.join(a.out, "overview", f"{name}.png"))
        spec["models"][name] = info
    effect_template(os.path.join(a.out, "templates", "baron_attack_target_effect.png"), epic)
    D.native_sheet(serpen, ["idle", "base", "attack", "dead"], os.path.join(a.out, "native", "serpen_frames_4x.png"))
    D.native_sheet(epic, ["idle", "base", "attack_left", "attack_right", "attack_target_effect", "dead"],
                   os.path.join(a.out, "native", "morgard_frames_4x.png"))
    for fn, (pack, sheet, tag) in D.STYLE.items():     # step 1's style pictures (this pack's own sprites, 8x)
        D.sheet_frame(pack, sheet, tag, 8).save(os.path.join(a.out, "style", fn))
    spec["kinds"] = {kind: {**D.KINDS[kind], **D.target(kind), "tags": D.TAGS[D.KINDS[kind]["tags"]]}
                     for kind in D.KINDS}
    spec["element"] = ELEMENT
    json.dump(spec, open(os.path.join(a.out, "SPEC2.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    shutil.copyfile(a.prompt, os.path.join(a.out, os.path.basename(a.prompt)))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
