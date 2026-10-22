"""league_caitlyn's redrawn action frames, read back from Codex's raw sheets (hd/actions_raw/, the answer to
tools/art/pack_caitlyn_actions.py): hd/actions/<tag>_<n>.png (n: League's frame, 1-based) + hd/actions/actions.json.

    python tools/art/actions_caitlyn_hd.py [--review DIR]

tools/art/actions_riven_hd.py's way: the white ground flooded from the edges, the frames = the sheet's big pieces left
to right, each read on Codex's own square phase on a pitch that makes her the design's size, every square the nearest
colour of the design's palette. Her size: only her face shows skin (gloves, stockings), so the face's area (its
biggest skin piece) against the design's sets each FRAME's scale (Codex drew the sheets and even the frames of one
sheet at different sizes). Placed as in League's frame of the template: grounded, her feet over League's feet; in the
air or lying, her middle over League's trunk. RAW_PICK names the raw file Codex kept for a sheet when it redrew it.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import actions_riven_hd as AR  # noqa: E402
import design_fiora_hd as FD  # noqa: E402
import pack_caitlyn_actions as PA  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "caitlyn", "hd")
SKIN = [(252, 207, 174), (244, 162, 125)]
RAW_PICK = {"run_3": "run_3-repair", "dead_3": "dead_3-repair3"}     # Codex's HANDOFF: the redrawn ones it kept
MIN_PIECE = 0.02                       # of a sheet's figure pixels: smaller pieces are specks


def lp(path):
    return FD.lp(path)


HAT = [(87, 36, 144), (64, 49, 168), (59, 16, 86), (74, 25, 111), (49, 41, 137), (47, 12, 65)]
HAT_ONLY = [HAT[0], HAT[2], HAT[3], HAT[5]]
NATIVE = (5.5, 8.0)                     # Codex's squares here (6-7.5 px): a wider range locked onto their doubles
SCALE_SPREAD = 0.12                     # a frame's own head scale within this of its sheet's median, else the median


def head_height(d):
    """Squares from her hat's top to her chin (the face's lowest skin square), the hat being the purple piece that
    holds the topmost purple square; None when the face is not under the hat (lying, turned)."""
    hat = np.zeros(d.shape[:2], bool)
    for c in HAT:
        hat |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    skin = np.zeros(d.shape[:2], bool)
    for c in SKIN:
        skin |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    if not hat.any() or not skin.any():
        return None
    lab, n = nd.label(skin)
    face = lab == (np.argmax(nd.sum(skin, lab, range(1, n + 1))) + 1)
    ys, xs = np.nonzero(hat)
    fy, fx = np.nonzero(face)
    top = ys.min()
    if not (fy.mean() > top + 4 and abs(fx.mean() - xs[ys == top].mean()) < 12):
        return None
    return float(fy.max() - top + 1)


GOLD = [(251, 204, 74), (238, 175, 49), (217, 152, 38), (201, 132, 29), (186, 119, 29), (160, 97, 29),
        (247, 237, 206), (242, 221, 175), (9, 185, 249), (8, 158, 237), (97, 212, 241), (6, 111, 206)]


def body_height(d):
    """Squares from her hat's top (the topmost hat-purple square) to her lowest square that is not the rifle's
    gold, ivory or lens colours (a lowered barrel reaches past her feet)."""
    hat = np.zeros(d.shape[:2], bool)
    for c in HAT:
        hat |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    rifle = np.zeros(d.shape[:2], bool)
    for c in GOLD:
        rifle |= (d[..., :3] == c).all(-1)
    body = (d[..., 3] > 0) & ~rifle
    if not hat.any() or not body.any():
        return None
    return float(np.nonzero(body)[0].max() - np.nonzero(hat)[0].min() + 1)


def template_height(j, ground0):
    """Her hat-top-to-lowest-point height in League's frame fitted to her build (pack_caitlyn_actions.her_joints)."""
    Q = PA.her_joints(j)
    Q.pop("rifle_u")
    top = Q["head"][1] - PA.HEAD_R
    bottom = max(q[1] for k, q in Q.items() if k != "head") - ground0
    return bottom - top


def hat_area(d):
    """Squares of the hat's purples in the piece holding the topmost one (the hair's blue-purples left out)."""
    m = np.zeros(d.shape[:2], bool)
    for c in HAT_ONLY:
        m |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    lab, n = nd.label(nd.binary_dilation(m, iterations=1))
    if not n:
        return 0
    ys, xs = np.nonzero(m)
    top = lab[ys.min(), xs[ys == ys.min()][0]]
    return int(((lab == top) & m).sum())


def face_area(d):
    m = np.zeros(d.shape[:2], bool)
    for c in SKIN:
        m |= (d[..., :3] == c).all(-1) & (d[..., 3] > 0)
    lab, n = nd.label(m)
    return int(nd.sum(m, lab, range(1, n + 1)).max()) if n else 0


def pieces_of(a, fig, count):
    """The sheet's `count` figures left to right: its big pieces (a muzzle reaching the next figure joins them, so a
    piece wider than a cell is cut at the cell edges)."""
    lab, nl = nd.label(nd.binary_dilation(fig, iterations=6))
    sz = nd.sum(fig, lab, range(1, nl + 1))
    keep = [k + 1 for k in range(nl) if sz[k] > MIN_PIECE * fig.sum()]
    keep.sort(key=lambda k: np.nonzero(lab == k)[1].min())
    out = []
    for k in keep:
        m = (lab == k) & fig
        ys, xs = np.nonzero(m)
        out.append(m)
    if len(out) < count:                 # merged: split by the template's cells
        out = []
        for i in range(count):
            m = fig.copy()
            m[:, :i * PA.CELL[0]] = False
            m[:, (i + 1) * PA.CELL[0]:] = False
            out.append(m)
    return out[:count]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    AR.NATIVE = NATIVE
    with open(lp(os.path.join(HD, "actions_raw", "sheets.json")), encoding="utf-8") as f:
        sheets = json.load(f)["sheets"]
    with open(lp(os.path.join(HD, "caitlyn_joints.json")), encoding="utf-8") as f:
        joints = json.load(f)
    des = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    pal = np.unique(des[des[..., 3] > 0][:, :3], axis=0).astype(np.uint8)
    q0 = PA.her_joints(joints["design"])
    q0.pop("rifle_u")
    ground0 = max(q[1] for q in q0.values())
    # the stick figure's own height in the design pose against the design's: the template's proportions -> hers
    face0, head0, hat0 = face_area(des), head_height(des), hat_area(des)
    q0 = PA.her_joints(joints["design"])
    q0.pop("rifle_u")
    ground0 = max(q[1] for q in q0.values())
    out_dir = os.path.join(HD, "actions")
    os.makedirs(lp(out_dir), exist_ok=True)
    info = {}
    for sh in sheets:
        raw = RAW_PICK.get(sh["name"], sh["name"])
        a_ = np.asarray(Image.open(lp(os.path.join(HD, "actions_raw", raw + ".png"))).convert("RGB")).astype(int)
        fig = AR.cutout(a_)
        cuts = []
        for m in pieces_of(a_, fig, len(sh["frames"])):
            ys, xs = np.nonzero(m)
            sub = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
            cuts.append((a_[sub], m[sub]))
        # her size: three measures of her head on Codex's own squares against the design's (they agree within
        # ~10 %): the face's area, the head's height (hat top to chin), the hat's area; their median
        AR.SCALE = 1.0
        scales = []
        for c, op in cuts:
            d1 = AR.to_palette(AR.read_cell(c, op)[0], pal)
            hh = head_height(d1)
            cues = [np.sqrt(face_area(d1) / face0), np.sqrt(hat_area(d1) / hat0)] + ([hh / head0] if hh else [])
            scales.append(float(np.median(cues)) if max(cues) - min(cues) <= 0.25 * np.median(cues) else None)
        med = float(np.median([v for v in scales if v])) if any(scales) else 1.0
        scales = [v if v and abs(v / med - 1) <= 0.25 else med for v in scales]   # lying, the head unreadable
        for (c, op), n, scale in zip(cuts, sh["frames"], scales):
            AR.SCALE = scale
            d = AR.to_palette(AR.read_cell(c, op)[0], pal)
            ys, xs = np.nonzero(d[..., 3] > 0)
            d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            Q = PA.her_joints(joints["tags"][sh["tag"]][n - 1]["j"])
            Q.pop("rifle_u")
            pts = list(Q.values())
            low = max([q[1] for q in pts] + [Q["head"][1] + PA.HEAD_R])
            y_low = min(0.0, max(q[1] for q in pts) - max(0.0, low) - ground0)
            ys, xs = np.nonzero(d[..., 3] > 0)
            if y_low > -3 and sh["tag"] != "dead":
                feet_t = (Q["l_foot"][0] + Q["r_foot"][0]) / 2
                px_ = float(xs[ys >= d.shape[0] - 4].mean() + 0.5) - feet_t
            else:
                px_ = float(xs.mean() + 0.5) - (Q["pelvis"][0] + Q["chest"][0]) / 2
            name = f"{sh['tag']}_{n}"
            Image.fromarray(d).save(lp(os.path.join(out_dir, name + ".png")))
            info[name] = dict(pivot=[round(px_, 2), round(d.shape[0] - y_low, 2)], scale=round(scale, 3),
                              face=face_area(d), size=[d.shape[1], d.shape[0]])
            print(name, info[name])
    with open(lp(os.path.join(out_dir, "actions.json")), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        for tag in PA.TAGS:
            names = sorted([k for k in info if k.rsplit("_", 1)[0] == tag], key=lambda k: int(k.rsplit("_", 1)[1]))
            cells = []
            for k in names:
                im = Image.open(lp(os.path.join(out_dir, k + ".png"))).convert("RGBA")
                can = Image.new("RGBA", (120, 110), (200, 205, 195, 255))
                px, py = info[k]["pivot"]
                can.alpha_composite(im, (int(round(60 - px)), int(round(100 - py))))
                cells.append((k, FD.shown(can, 1, 4)))
            FD.strip(cells, gap=6).convert("RGB").save(os.path.join(a.review, f"actions_{tag}.png"))
        print("review written to", a.review)


if __name__ == "__main__":
    main()
