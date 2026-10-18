"""league_riven's redrawn action frames, read back from Codex's raw sheets (hd/actions_raw/, the answer to
tools/art/pack_riven_actions.py): hd/actions/<tag>_<n>.png (n: League's frame, 1-based) + hd/actions/actions.json.

    python tools/art/actions_riven_hd.py [--review DIR]

Codex's exported sheets were resampled onto the template grid with stray light squares on the rims, so the raw
sheets are read instead (as tools/art/swords_riven_hd.py did): white ground flooded from the edges (her cream hair is
inside the outline), each cell read on Codex's own square phase but on a pitch SCALE times its own, so she stands
STAND rows tall as in the design (Codex drew her ~61), every square the nearest colour of the design's own palette
(the design without its sword).

Per frame actions.json keeps (in the frame's squares): "pivot" - the template's standing point (the cell's middle on
the ground line), "fist" - her sword fist: the small skin-coloured piece (a hand) nearest the template's blue circle
(FIST_FIX overrides one where that picks the wrong hand), "size".
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402
import pack_riven_actions as PA  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "riven", "hd")
NATIVE = (7.0, 12.5)                   # Codex's own squares lie in here
SCALE = 61.2 / 56                      # its standing figure (attack_1 frame 1) is 61.2 of them; hers is 56
SKIN = [(252, 181, 101), (244, 182, 108), (225, 152, 86)]
HAND_MAX = 45                          # squares: a hand, not the face or a leg
# "<tag>_<n>": (x, y) squares - her sword fist, picked by eye on every frame (the nearest skin piece was a knee or
# the other hand too often): the closed fist that does what League's sword hand does in that frame (Codex drew the
# sword fist on either side)
FIST_FIX = {
    "attack_1": (5, 21), "attack_2": (30, 18), "attack_3": (38, 36), "attack_4": (35, 30), "attack_5": (29, 30),
    "attack_6": (37, 26),
    "attack2_1": (3, 18), "attack2_2": (25, 25), "attack2_3": (35, 19), "attack2_4": (2, 17), "attack2_5": (3, 15),
    "attack2_6": (2, 19),
    "attack3_1": (2, 20), "attack3_2": (2, 4), "attack3_3": (44, 40), "attack3_4": (35, 32), "attack3_5": (38, 33),
    "attack3_6": (31, 25),
    "skill_1": (3, 21), "skill_2": (33, 25), "skill_3": (35, 32), "skill_4": (32, 30), "skill_5": (44, 28),
    "skill_6": (50, 22), "skill_7": (3, 19),
    "q2_1": (3, 21), "q2_2": (2, 24), "q2_3": (1, 26), "q2_4": (41, 25), "q2_5": (36, 30), "q2_6": (37, 39),
    "q2_7": (2, 19),
    "q3_1": (2, 18), "q3_2": (11, 7), "q3_3": (2, 11), "q3_4": (33, 11), "q3_5": (37, 34), "q3_6": (26, 44),
    "q3_7": (2, 24),
    "skill2_1": (14, 11), "skill2_2": (4, 11), "skill2_3": (3, 18), "skill2_4": (8, 19), "skill2_5": (33, 3),
    "skill2_6": (32, 4), "skill2_7": (40, 4), "skill2_8": (4, 20),
}


def lp(path):
    return FD.lp(path)


def cutout(a):
    mn, mx = a.min(2), a.max(2)
    white = (mn > 228) & (mx - mn < 18)
    lab, _ = nd.label(white)
    rim = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    fig = ~np.isin(lab, [v for v in np.unique(rim) if v])
    fig = nd.binary_opening(fig, iterations=1)
    return fig


def read_cell(c, op):
    FD.PITCH = NATIVE
    (px, phx), (py, phy) = FD.fit(c, op, 1), FD.fit(c, op, 0)
    p = (px + py) / 2 * SCALE
    xs, ys = np.arange(phx, c.shape[1], p), np.arange(phy, c.shape[0], p)
    out = np.zeros((len(ys) - 1, len(xs) - 1, 4), np.uint8)
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            y0, y1 = int(round(ys[j])), int(round(ys[j + 1]))
            x0, x1 = int(round(xs[i])), int(round(xs[i + 1]))
            win = c[y0:y1, x0:x1].reshape(-1, 3)
            m = op[y0:y1, x0:x1].reshape(-1)
            if m.sum() * 2 > len(m):
                out[j, i, :3] = np.median(win[m], axis=0)
                out[j, i, 3] = 255
    return out, (phx, phy, p)


def to_palette(d, pal):
    op = d[..., 3] > 0
    lab = V.srgb2lab(d[op][:, :3].astype(float))
    pl = V.srgb2lab(pal.astype(float))
    k = np.argmin(((lab[:, None, :] - pl[None]) ** 2).sum(-1), axis=1)
    out = d.copy()
    out[op, :3] = pal[k]
    return out


HAIR = [(251, 235, 215), (236, 234, 234), (210, 188, 174), (213, 209, 204), (192, 164, 144), (176, 172, 170),
        (173, 147, 134)]
DESIGN_HAIR = 164                      # squares of hair (its biggest piece) in hd/design.png


def hair_area(d):
    m = np.zeros(d.shape[:2], bool)
    for c in HAIR:
        m |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    lab, n = nd.label(m)
    return int(nd.sum(m, lab, range(1, n + 1)).max()) if n else 0


def find_fist(d, want):
    skin = np.zeros(d.shape[:2], bool)
    for c in SKIN:
        skin |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    hair = np.zeros(d.shape[:2], bool)
    for c in HAIR:
        hair |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    lab, n = nd.label(skin, structure=np.ones((3, 3)))
    best = None
    for k in range(1, n + 1):
        piece = lab == k
        ys, xs = np.nonzero(piece)
        if len(ys) > HAND_MAX or len(ys) < 3:
            continue
        if (nd.binary_dilation(piece, iterations=2) & hair).sum() >= 6:      # her face, framed by her hair
            continue
        dist = float(np.min(np.hypot(xs + 0.5 - want[0], ys + 0.5 - want[1])))
        if best is None or dist < best[0]:
            best = (dist, (float(xs.mean() + 0.5), float(ys.mean() + 0.5)))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    with open(lp(os.path.join(HD, "actions_raw", "sheets.json")), encoding="utf-8") as f:
        sheets = json.load(f)["sheets"]
    with open(lp(os.path.join(HD, "riven_joints.json")), encoding="utf-8") as f:
        joints = json.load(f)
    tmp = os.path.join(os.environ.get("TEMP", "."), "riven_no_sword.png")
    pal = PA.no_sword_design(tmp).astype(np.uint8)
    out_dir = os.path.join(HD, "actions")
    os.makedirs(lp(out_dir), exist_ok=True)
    info = {}
    global SCALE
    q0 = PA.her_joints(joints["design"])
    ground0 = max(q[1] for k_, q in q0.items() if not k_.startswith("weapon"))     # the idle's ankles, ~-3.7
    for sh in sheets:
        a_ = np.asarray(Image.open(lp(os.path.join(HD, "actions_raw", sh["name"] + ".png"))).convert("RGB")).astype(int)
        fig = cutout(a_)
        # the frames: the big pieces of figure left to right (Codex kept the three cells, but not always the
        # template's 1536 x 1024 nor its cell edges)
        lab, nl = nd.label(nd.binary_dilation(fig, iterations=6))
        sz = nd.sum(fig, lab, range(1, nl + 1))
        keep = [k + 1 for k in range(nl) if sz[k] > 0.02 * fig.sum()]
        keep.sort(key=lambda k: np.nonzero(lab == k)[1].min())
        if len(keep) < len(sh["frames"]):
            sys.exit(f"{sh['name']}: {len(keep)} figures for frames {sh['frames']}")
        keep = keep[:len(sh["frames"])]           # (a last sheet's empty cells Codex filled anyway)
        pieces = []
        for k in keep:
            m = (lab == k) & fig
            ys, xs = np.nonzero(m)
            sub = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
            pieces.append((a_[sub], m[sub]))
        # her size: Codex drew each sheet on its own squares and at its own size - the hair's area (the same in
        # every pose) against the design's sets the sheet's scale
        SCALE = 1.0
        areas = [hair_area(to_palette(read_cell(c, op)[0], pal)) for c, op in pieces]
        SCALE = float(np.sqrt(np.median(areas) / DESIGN_HAIR))
        for (c, op), n in zip(pieces, sh["frames"]):
            d, _ = read_cell(c, op)
            d = to_palette(d, pal)
            ys, xs = np.nonzero(d[..., 3] > 0)
            d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            # where League's frame (the template, its standing point at 0, 0) has her: grounded, her feet over the
            # template's feet; in the air (the leap, the somersault), her middle over the template's trunk
            Q = PA.her_joints(joints["tags"][sh["tag"]][n - 1]["j"])
            pts = [q for k_, q in Q.items() if not k_.startswith("weapon")]
            low = max([q[1] for q in pts] + [Q["head"][1] + PA.HEAD_R])
            # her lowest point, 0 on the ground: League's foot joints are ankles, so measured against the idle's
            y_low = min(0.0, max(q[1] for q in pts) - max(0.0, low) - ground0)
            op_ = d[..., 3] > 0
            ys, xs = np.nonzero(op_)
            if y_low > -3:
                feet_t = (Q["l_foot"][0] + Q["r_foot"][0]) / 2
                bot = ys >= d.shape[0] - 4
                px_ = float(xs[bot].mean() + 0.5) - feet_t
            else:
                px_ = float(xs.mean() + 0.5) - (Q["pelvis"][0] + Q["chest"][0]) / 2
            pivot = (px_, d.shape[0] - y_low)
            want = (pivot[0] + Q["r_hand"][0], pivot[1] + Q["r_hand"][1] - max(0.0, low))
            name = f"{sh['tag']}_{n}"
            fist = FIST_FIX.get(name)
            dist = None
            if fist is None:
                got = find_fist(d, want)
                dist, fist = (got if got else (None, want))
            Image.fromarray(d).save(lp(os.path.join(out_dir, name + ".png")))
            info[name] = dict(pivot=[round(v, 2) for v in pivot], fist=[round(v, 2) for v in fist],
                              want=[round(v, 2) for v in want], fist_off=None if dist is None else round(dist, 1),
                              size=[d.shape[1], d.shape[0]])
            print(name, info[name])
    with open(lp(os.path.join(out_dir, "actions.json")), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        z = 6
        for tag in PA.TAGS:
            names = [k for k in info if k.rsplit("_", 1)[0] == tag]
            names.sort(key=lambda k: int(k.rsplit("_", 1)[1]))
            ims = []
            for k in names:
                im = Image.open(lp(os.path.join(out_dir, k + ".png"))).convert("RGBA")
                bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
                bg.alpha_composite(im)
                big = bg.resize((im.width * z, im.height * z), Image.NEAREST)
                dr = ImageDraw.Draw(big)
                for (x, y), col in ((info[k]["pivot"], (255, 0, 0)), (info[k]["fist"], (0, 60, 255)),
                                    (info[k]["want"], (255, 0, 255))):
                    dr.ellipse([x * z - 9, y * z - 9, x * z + 9, y * z + 9], outline=col, width=3)
                ims.append((k, big))
            FD.strip(ims).convert("RGB").save(os.path.join(a.review, f"actions_{tag}.png"))
        print("review written to", a.review)


if __name__ == "__main__":
    main()
