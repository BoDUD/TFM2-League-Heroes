#!/usr/bin/env python3
"""league_ornn's action frames: the approved 3/4 design (idle) and Codex's skeleton poses (every action), timed after
League's own clips (the user, 2026-10-21: 3/4 only, 「Codex 照骨架画关键姿势」, 「有连招要做连招」).

    python tools/art/rig_ornn.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_ornn.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_ornn.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design (tools/art/design_ornn_model.py: Codex's step-1 take A-3 read back to 71 x 66 = 44 game px at PPU 1.5;
Codex's own face): League's idle seen 3/4 from the front-right - hunched, legs planted apart, the big steel hammer low
in the near hand, the smaller one in the molten far hand. The idle breathes on the design itself (the upper body sets
down a row onto the legs and comes back). Every action is Codex's poses (tools/art/design_ornn_poses.py: eighteen of
League's frames drawn on skeletons at the design's segment lengths, read back at the design's scale with the design's
own face) - but the run, drawn on the design itself (ornn_legs.py: his boots stepping under the design's own upper body) -
each placed with the middle between its feet on the design's (the folded, lunging and lying ones by the
middle of the plum apron) and its lowest row on the ground (or `lift` rows over it in the air), moved by whole squares
only.
The combos have their own frames (POSE_PROMPTS.md): Q -> E is `skill` (q_raise, q_slam: the fissure and the pillar)
then `skill2` (charge, the dash) and `skill2_hit` (impact: the pillar shattered, the quake); R1 -> R2 is `ult` (summon,
call: the ram summoned far away, held while it runs back to him) then `ult_butt` (butt_wind, headbutt: the ram sent
back). The kit's ticks (tools/kit/build_ornn.py) come from MS (a frame's start in ticks = ms x 0.06).
W's fire is drawn into his breath frames (with_fire: Codex's w_fire from league_ornn_big, import_ornn_fx.py) - the client
mirrors his frames, never an effect picture.
The in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」,
「动画你觉得少的地方就想办法补」, 「能改就想办法改 全都要改」): a pose with a hammer turned (inbetween.spin, any angle) about the
fist that holds it or, with the fist, about the shoulder (PARTS), its root going in under the rest of him; the design's
face and every square outside the part checked unchanged (inbetween.vary). The charge's hammers swing as he gallops,
the impact's hammers swing out and back, the attack's and the summon's big hammer is cocked further back and swung on
over his head, the call's raised hammer pumps.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inbetween as IB  # noqa: E402
import ornn_legs as GL  # noqa: E402
import ppu_rig as R  # noqa: E402
from rig_warwick import close_cracks  # noqa: E402
from rig_wukong import CutDesign as _Cut, P, pad  # noqa: E402

HERO = "ornn"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "ornn", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


STAND = 45                     # the column between his feet (under the apron's middle): the standing point
WAIST = 50                     # the last row of the upper body (the belt): the idle's breath sets it down


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    D.part("upper", D.box(0, WAIST, 0, D.W - 1))
    D.part("lower", D.rest())
    return D


def apron(d):
    """The plum leather apron's and boots' squares: dark red-purple, blue over green."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (d[..., 3] > 0) & (r > 45) & (r < 150) & (g < 45) & (b > g + 8) & (r > b + 15)


def apron_mid(d):
    """The middle column of a figure's apron (the lower 45% of the figure: the beard's red left out)."""
    m = apron(d)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    m[:ys.min() + int(0.55 * (ys.max() - ys.min()))] = False
    xs = np.nonzero(m)[1]
    if not len(xs):
        xs = np.nonzero(d[..., 3] > 0)[1]
    return float(np.median(xs))


def feet_mid(d, rows=5):
    """The middle between his outermost feet: the lowest `rows` rows of a standing figure without the steel hammers'
    squares (blue over red) - the apron is hidden behind a hammer in some poses (smash, call)."""
    rgb = d[..., :3].astype(int)
    op = (d[..., 3] > 0) & ~(rgb[..., 2] > rgb[..., 0] + 25)
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys.max() + 1 - rows:ys.max() + 1])[1]
    return (xs.min() + xs.max() + 1) / 2


class Form:
    def __init__(self, D, rig_pad=(70, 70, 70, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}

    def pose(self, whole=(0, 0), crouch=0):
        wx, wy = whole
        can = R.compose(self.rig, [(self.L["lower"], dict(dx=wx, dy=wy)), (self.L["upper"], dict(dx=wx, dy=wy + crouch))])
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def drawn(self, arr, pad):
        """A frame drawn on the design's own grid (`pad` = (columns, rows) of margin round the design in `arr`): placed
        exactly where the design stands."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        y0, x0 = P - pad[1], P - pad[0]
        lay[y0:y0 + arr.shape[0], x0:x0 + arr.shape[1]] = arr
        can = R.compose(self.rig, [(lay, dict(dx=0, dy=0))])
        can[self.rig.GY:] = 0
        return can

    def posed(self, name, whole=(0, 0), lift=0, turn=None):
        """A Codex pose (hd/pose_<name>.png) standing where the design stands: the middle of its apron on the design's,
        its lowest row on the ground - `lift` rows above it (in the air). turn {part: degrees}: the in-betweens - the
        pose's PARTS turned clockwise (varied()), the pose placed as it stands unturned."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        top = P + self.D.ground - (ys.max() + 1) - lift
        mid = apron_mid if name in APRON else feet_mid
        left = P + int(round(mid(self.D.d) - mid(d)))
        if turn:
            d = self.varied(name, d, turn)
            top, left = top - VPAD, left - VPAD
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        y0, y1 = max(0, top), min(lay.shape[0], top + d.shape[0])
        lay[y0:y1, x0:x1] = d[y0 - top:y1 - top, x0 - left:x1 - left]
        can = R.compose(self.rig, [(lay, dict(dx=whole[0], dy=whole[1]))])
        can[self.rig.GY:] = 0
        return can

    def posed_at(self, name, xy, whole=(0, 0), lift=0):
        """Where the point (x, y) of hd/pose_<name>.png (squares) lands on the canvas of posed(name, whole, lift)."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        mid = apron_mid if name in APRON else feet_mid
        left = int(round(mid(self.D.d) - mid(d)))
        top = self.D.ground - (ys.max() + 1) - lift
        return self.rig.ox + left + xy[0] + whole[0], self.rig.oy + top + xy[1] + whole[1]

    def varied(self, name, d, turn):
        """The pose picture with parts turned (turn {part: degrees clockwise}, PARTS[name]) by inbetween.vary on a
        canvas VPAD squares bigger on every side, each part's root under the rest of him; the design's face (where the
        pose carries it) and every square in no part checked unchanged."""
        parts, spins = {}, []
        for part, deg in turn.items():
            items, about, nofire = PARTS[name][part]
            m = IB.part_mask(d.shape, items) & (d[..., 3] > 0)
            if nofire:
                m &= ~molten(d)
            parts[part] = runs(m)
            spins.append((part, about, deg, "under"))
        head = face_on(name, d) if name in FACE_AT else None
        return IB.vary(d, parts, tuple(int(v) for v in self.D.outline), spins=spins, head=head, pad=VPAD,
                       name=f"{name} {turn}")


# poses whose feet are not under him (in the air, folded, lying, a foot lifted in the run): placed by the apron
APRON = {"charge", "headbutt", "kneel", "lie", "run1", "run2", "run3", "run4"}

# The in-betweens' parts (inbetween.vary): pose -> part -> (boxes / polygons in the pose's own squares, the point it
# turns about, whether the molten arm's colours in the box stay behind). "big": the steel hammer in his near hand,
# "small": the one in the molten far hand. A hammer held out in the air turns about the fist that holds it (charge,
# impact, call; the fist stays, the haft goes in under it); one raised over his shoulder turns with the fist and the haft
# about the shoulder guard's top (raise, summon). The design's face lies on each upright pose where design_ornn_poses
# laid it (its near eye on Codex's): FACE_AT, its top-left square (the turned-down heads - charge - keep Codex's face:
# no head check there, the body check holds).
VPAD = 30
PARTS = {
    "charge": {"big": ([[(0, 0), (23, 0), (23, 12), (17, 14), (15, 17), (0, 19)]], (18.0, 19.0), False),
               "small": ([[(0, 20), (11, 20), (13, 27), (13, 32), (10, 36), (0, 36)]], (13.0, 30.0), False)},
    "impact": {"big": ([(0, 26, 13, 42), (14, 49, 20, 54)], (14.5, 45.0), False),
               "small": ([(62, 28, 76, 40), (65, 47, 71, 53)], (67.0, 44.0), True)},
    "raise": {"big": ([(0, 0, 32, 19), (0, 20, 7, 26)], (11.0, 21.0), False)},
    "summon": {"big": ([(0, 0, 33, 21)], (10.0, 22.0), False)},
    "call": {"small": ([(55, 0, 72, 12)], (68.0, 14.0), True)},
    "q_raise": {"small": ([(52, 0, 66, 11)], (61.0, 12.0), True)},
    "stagger": {"big": ([(5, 54, 27, 71), (0, 46, 6, 53)], (12.0, 51.0), False),
                "small": ([(62, 54, 72, 67)], (63.0, 55.0), True)},
}
FACE_AT = {"raise": (33, 29), "smash": (32, 15), "q_raise": (29, 28), "q_slam": (40, 16), "breath": (37, 17),
           "impact": (34, 12), "summon": (28, 30), "call": (28, 27), "butt_wind": (33, 15), "stagger": (28, 12),
           "kneel": (37, 16)}


def face_tpl():
    """The design's face (design_ornn_poses.FACE_POLY on hd/idle.png) cut to its box: (picture, mask)."""
    import design_ornn_poses as DP
    d = load("idle.png")
    m = IB.cut(d.shape, polys=[DP.FACE_POLY]) & (d[..., 3] > 0)
    ys, xs = np.nonzero(m)
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def face_on(name, d):
    """The squares of the design's face that pose `name` carries unchanged at FACE_AT (a mask over d)."""
    tpl, tm = face_tpl()
    ox, oy = FACE_AT[name]
    h, w = tm.shape
    out = np.zeros(d.shape[:2], bool)
    out[oy:oy + h, ox:ox + w] = (d[oy:oy + h, ox:ox + w] == tpl).all(-1) & tm
    return out


def molten(d):
    """The molten arm's squares: reds, oranges and yellows far warmer than blue."""
    rgb = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (rgb[..., 0] > 150) & (rgb[..., 0] > rgb[..., 2] + 60)


def runs(m):
    """A mask as row runs (x0, y, x1, y) - boxes for inbetween.vary's parts."""
    out = []
    for y in range(m.shape[0]):
        xs = np.nonzero(m[y])[0]
        if not len(xs):
            continue
        cut = np.nonzero(np.diff(xs) > 1)[0]
        out += [(int(a), y, int(b), y) for a, b in zip(np.r_[xs[0], xs[cut + 1]], np.r_[xs[cut], xs[-1]])]
    return out


def form():
    F = Form(design())
    F.rig.idle_canvas = F.pose()
    return F


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame
MS = {"idle": [160] * 8, "run": [110] * 8,
      "attack": IB.spans((110, 1), (123, 2), (100, 1), (90, 1), (80, 1)),   # the smash from 233 ms: atk_st 14
      "skill_w": [150] * 5,                        # the breath held 750 ms (w_t 45), the fire to its last pulse
      "skill": IB.spans((100, 1), (100, 2), (120, 1), (100, 1), (80, 1)),   # the fissure from 200 ms: q_rel 12
      "skill2": IB.spans((200, 4)),                # the charge, looped while he runs (e_anim 20)
      "skill2_hit": IB.spans((233, 4)),            # the quake on contact: e_hit_t 14
      "ult": [100, 100, 200, 200, 200, 200],       # the call from 200 ms (r_rel 12), held while the ram runs back
      "ult_butt": [70, 63, 130, 137],              # the headbutt from 133 ms: r_butt_rel 8, r_butt_t 24
      "hit": [100, 100],
      "dead": [120, 140, 160, 200, 160, 600]}


def frames_all(F):
    p, q = F.pose, F.posed
    out = {}
    # idle (League's Ornn_Idle1: a slow heavy breath): the upper body sets down a row and back
    out["idle"] = [p(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # run (League's Ornn_Run: a heavy hunched trot, the hammers held): the design's upper body with his boots stepping in
    # eight phases (tools/art/ornn_legs.py - the user, 2026-10-21, on Codex's four run poses: 「奥恩走路是这样走的？」 then
    # 「跑步用定稿的上身，你自己画腿的跑步循环（像格雷福斯那样），大锤只轻微摆动」)
    out["run"] = [F.drawn(GL.frame(F.D.d, k), (4, 4)) for k in range(8)]
    # auto attack (League's Ornn_Attack1: the big hammer raised over his head, then smashed down ahead): raise, the
    # smash (the hit), held, back
    # (in-betweens: the raised hammer cocked further back as he leans back, then swung on over his head)
    out["attack"] = [q("raise"), q("raise", whole=(-1, 0), turn={"big": -15}), q("raise", turn={"big": 25}),
                     q("smash"), q("smash"), p()]
    # W Bellows Breath (League's Ornn_Spell2: leaning forward, breathing fire for 0.75 s): the breath, the head a square
    # forward and back (the fire laid on by with_fire)
    out["skill_w"] = [q("breath", whole=w) for w in BREATH]
    # Q Volcanic Rupture (League's Ornn_Spell1: the molten fist raised, then slammed into the ground) - the combo's start
    # (in-betweens: the raised hammer cocked back as he rises, then swung forward on its way down)
    out["skill"] = [q("q_raise"), q("q_raise", lift=1, turn={"small": -15}), q("q_raise", turn={"small": 25}),
                    q("q_slam"), q("q_slam"), p()]
    # E Searing Charge (League's Ornn_Spell3_Dash: low, horns first like a ram)
    # (in-betweens: the two hammers swinging against each other as he gallops; 4 x 50 ms, still 200 a loop)
    out["skill2"] = [q("charge"), q("charge", turn={"big": 12, "small": -10}), q("charge", lift=1),
                     q("charge", lift=1, turn={"big": -12, "small": 10})]
    # E's contact (League's Ornn_Spell3_Hit: rearing up after the crash) - the pillar shattered, the quake
    # (in-betweens: the hammers swung out and back in as he rears up)
    out["skill2_hit"] = [q("impact"), q("impact", turn={"big": -12, "small": 12}),
                         q("impact", whole=(-1, 0), turn={"big": 12, "small": -12}), q("impact", whole=(-1, 0))]
    # R Call of the Forge God (League's Ornn_Spell4_Windup / Spell4): the hammer raised, then the call; held while the
    # ram runs back to him
    # (in-betweens: the summoned hammer cocked further back as he rises; the call's raised hammer pumping while he holds
    # it - it was the call moved a square and back)
    out["ult"] = [q("summon"), q("summon", lift=1, turn={"big": -15}), q("call"), q("call", turn={"small": 12}),
                  q("call"), q("call", turn={"small": -10})]
    # R's second step (League's Ornn_Spell4_Charge / Spell4_Hit: drawn back, then the headbutt that sends the ram back)
    out["ult_butt"] = [q("butt_wind"), q("butt_wind", whole=(-1, 0)), q("headbutt"), q("headbutt", whole=(1, 0))]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Ornn_Death: struck back, down on his knees, then face down)
    # (in-between: the hammers sagging in his hands as he reels back)
    out["dead"] = [q("stagger"), q("stagger", whole=(-1, 0), turn={"big": 15, "small": 15}), q("kneel"), q("kneel"),
                   q("lie", lift=1), q("lie")]
    return out


# W's fire drawn into his breath frames (the client mirrors his frames, never an effect picture: the kit binds no view
# to it): the picture's mouth (its frame's centre, import_ornn_fx.py) on his mouth, its frames looped FIRE_MS each
BREATH = [(0, 0), (1, 0), (0, 0), (1, 0), (0, 0)]     # skill_w's breath frames: the head a square forward and back
MOUTH = (50, 30.5)          # on hd/pose_breath.png: the fire's left edge at the right end of his mouth, under the nose
FIRE_MS = 75
FX_SHEET = os.path.join(R.ROOT, "league", "effects", "league_ornn_big#sheet.png")


def fire_frames():
    """w_fire's frames from league_ornn_big brought to PPU (nearest, as Rig.bake), sparks under 4 squares dropped (as
    Rig.bake: ppu_hd's check, no specks on a frame); None before the effects are imported."""
    if not os.path.isfile(lp(FX_SHEET)):
        return None
    import tfm2_ase
    sp = tfm2_ase.load_sprite(FX_SHEET)
    out = []
    for i in sp.tag_frames("w_fire"):
        a = np.asarray(sp.frames[i].convert("RGBA"))
        h, w = a.shape[:2]
        yy = np.minimum(((np.arange(round(h * PPU)) + 0.5) / PPU).astype(int), h - 1)
        xx = np.minimum(((np.arange(round(w * PPU)) + 0.5) / PPU).astype(int), w - 1)
        b = a[yy][:, xx].copy()
        lbl, n = ndimage.label(b[..., 3] > 0, structure=np.ones((3, 3)))
        if n:
            sz = ndimage.sum(b[..., 3] > 0, lbl, range(1, n + 1))
            for j in range(1, n + 1):
                if sz[j - 1] < 4:
                    b[lbl == j] = 0
        out.append(b)
    return out


def with_fire(F, acts):
    """{tag: [(canvas or {"body", "over"}, ms)]}: each breath frame split into fire frames of FIRE_MS laid over it."""
    pics = fire_frames()
    if not pics:
        return acts
    out = dict(acts)
    parts, k = [], 0
    for (can, ms), whole in zip(acts["skill_w"], BREATH):
        mx, my = F.posed_at("breath", MOUTH, whole)
        left = ms
        while left > 0:
            t = min(FIRE_MS, left)
            pic = pics[k % len(pics)]
            k += 1
            over = F.rig.canvas()
            h, w = pic.shape[:2]
            y0, x0 = int(round(my - h / 2)), int(round(mx - w / 2))
            ys, xs = np.nonzero(pic[..., 3] > 0)
            ok = (ys + y0 >= 0) & (ys + y0 < over.shape[0]) & (xs + x0 >= 0) & (xs + x0 < over.shape[1])
            if not ok.all():
                sys.exit(f"the fire leaves the canvas by {int((~ok).sum())} squares")
            over[ys + y0, xs + x0] = pic[ys, xs]
            parts.append(({"body": can, "over": over}, t))
            left -= t
    out["skill_w"] = parts
    return out


def flat(c):
    """A frame as one canvas (the fire laid over its body)."""
    if not isinstance(c, dict):
        return c
    out = c["body"].copy()
    m = c["over"][..., 3] > 0
    out[m] = c["over"][m]
    return out


def frames(F, fire=True):
    a = frames_all(F)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = [(c, m) for c, m in zip(cans, ms)]
    return with_fire(F, out) if fire else out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    F = form()
    acts = frames(F)
    if a.audit:
        import rig_wukong as RW
        RW.HERO = HERO
        RW.audit(F, {t: [(flat(c), ms) for c, ms in fr] for t, fr in acts.items()}, a.audit)
    elif a.review:
        F.rig.review(acts, a.review)
    else:
        F.rig.export(acts)


if __name__ == "__main__":
    main()
