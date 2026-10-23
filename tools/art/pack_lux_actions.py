"""The Codex pack for league_lux's cast frames drawn whole (assets/source/lux/ACTIONS_PROMPT_PPU.md): every frame of her
attack, Light Binding (skill), Lucent Singularity (skill2) and Final Spark (ult) a new drawing of the approved design
(hd/design.png, PPU 2.2) in League's pose of that frame, arms and staff swinging - the way league_caitlyn's actions were
redrawn (tools/art/pack_caitlyn_actions.py). Her idle, run, hit and death stay tools/art/rig_lux_hd.py's.

    python tools/art/pack_lux_actions.py --out C:/t/lx_actions [--lol D:/WeGameApps/lol] [--oppi DIR]

The user, 2026-10-23, on the rigged casts (arms never moved, the staff only turned half round): 「法杖一点动作都没有吗？」
「手和法杖一点动作都没有的 不奇怪？英雄联盟是这样的？」, then 「Codex 重画施法动作」.
She holds the staff in her near hand, so Codex draws it with her (straightened afterwards if it comes out bent). Each
template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds TWO frames in cells of 768 x 1024 (her staff is nearly as
long as she is tall) on squares of SQ px (one design square: the design is 64 x 81 of them): League's skeleton of that
frame (assets/source/lux/hd/lux_joints.json, tools/lol/league_joints.py on assets/source/lux/poses.json) fitted to her
build as a stick guide (near limbs blue, far grey), her hands as blue circles, the staff as a red line as long as the
design's with its crescent head a filled red circle (League's staff is double-ended; ours has the head at one end: at
rest it hangs behind her as in the design, when she casts it points at the foe), her head with the hair as a circle,
the ground line, the standing point and a bar as tall as she stands. refs/: the design at 8x and 1x, its palette, its
staff alone, each sheet's League frames rendered (tools/lol/native_pose.py, Riot's model - local only, never
committed), oppi's Lux for the same action (style only). Then <out>.zip.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import design_lux_hd as DL  # noqa: E402
import pack_riven_actions as PR  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "lux")
TAGS = ["attack", "skill", "skill2", "ult"]
NAMES = {"attack": "basic attack, the staff swung round over her and thrust at the foe (lux_attack1)",
         "skill": "Light Binding, the staff raised and thrust forward (lux_spell1)",
         "skill2": "Lucent Singularity, the staff swung back and forward to throw the orb (lux_spell3)",
         "ult": "Final Spark: she leaps, the staff floats ahead of her and fires, she lands (lux_spell4)"}
OPPI_TAG = {"attack": "attack", "skill": "skill", "skill2": "skill2", "ult": "ult"}
SQ = 6                                   # px a design square in the templates
CELL = (768, 1024)
GROUND = 1024 - 150
PER_SHEET = 2
STAND = 81                               # design rows from her hair's top to her soles
GREY = (225, 225, 225)
NEAR, FAR = (40, 120, 230), (150, 150, 150)
STAFF = (255, 0, 0)
# her build in design squares (hd/design.png: soles on row 81, hips about 29 over them, shoulders about 48, the head
# with the hair centred about 26 over League's chest bone with 16 squares round it, arms about 18) against League's
# design pose (lux_idle1@0: pelvis 19.2 game px up, shoulders 6.4 over it, arms 6.9)
K_LEG, K_UP, K_ARM = 1.5, 3.0, 2.2
HEAD_UP, HEAD_R = 26.0, 16.0
# the design's staff from her grip: 28 squares to the crescent head's tip, 42 to the other end's
HEAD_REACH, END_REACH = 28.0, 42.0
LUNGE = 0.5
BONES = PR.BONES


def her_joints(j):
    """League's joints of a frame on her design's build, in design squares from her standing point."""
    v = {n: np.array(x[:2], float) for n, x in j.items() if isinstance(x, list)}
    pel = v["pelvis"] * K_LEG * np.array((LUNGE, 1.0))
    out = {"pelvis": pel}
    for n in ("l_hip", "r_hip", "l_knee", "r_knee", "l_foot", "r_foot"):
        out[n] = pel + (v[n] - v["pelvis"]) * K_LEG
    for n in ("chest", "l_shoulder", "r_shoulder"):
        out[n] = pel + (v[n] - v["pelvis"]) * K_UP
    for s in "lr":
        for n in ("elbow", "hand"):
            out[f"{s}_{n}"] = out[f"{s}_shoulder"] + (v[f"{s}_{n}"] - v[f"{s}_shoulder"]) * K_ARM
    nk = v["head"] - v["chest"]
    out["head"] = out["chest"] + nk / (np.linalg.norm(nk) or 1) * HEAD_UP
    return out


def staff_heads(frames, release):
    """Per frame, which of League's two staff bones (w2 / w4) carries the crescent head: w2 at rest (the first and the
    last frame, as the design hangs it), the one ahead at the cast's release frame, else the one nearer the head's
    place in the frame before."""
    out, prev = [], None
    n = len(frames)
    for i, fr in enumerate(frames):
        J = fr["j"]
        w2, w4 = np.array(J["w2"][:2]), np.array(J["w4"][:2])
        if i in (0, n - 1):
            k = "w2"
        elif i == release:
            k = "w4" if w4[0] >= w2[0] else "w2"
        else:
            k = "w2" if np.linalg.norm(w2 - prev) <= np.linalg.norm(w4 - prev) else "w4"
        out.append(k)
        prev = w2 if k == "w2" else w4
    return out


def template(path, frames, heads, k0, grip, release):
    """TWO frames of one action: per cell the stick guide, hand circles, the staff's line and head, head circle,
    ground, standing point. grip: League's side whose hand holds the staff."""
    can = Image.new("RGB", (CELL[0] * PER_SHEET, CELL[1]), (255, 255, 255))
    dr = ImageDraw.Draw(can)
    f = PR.font(26)
    for i, (fr, head_bone) in enumerate(zip(frames, heads)):
        x0 = i * CELL[0]
        cx = x0 + CELL[0] / 2
        J = fr["j"]
        Q = her_joints(J)
        a, b = np.array(J[head_bone][:2]), np.array(J["w4" if head_bone == "w2" else "w2"][:2])
        u = (a - b) / (np.linalg.norm(a - b) or 1)              # towards the crescent head
        hand = Q[f"{grip}_hand"]
        # the staff at League's place: along its axis through League's grip when the hand holds it (League's staff
        # within 3 px of the hand), else (thrown ahead in Final Spark) centred where League's staff is
        mid = (a + b) / 2
        held = np.linalg.norm(np.array(J[f"{grip}_hand"][:2]) - mid) < 0.6 * np.linalg.norm(a - b) + 3
        if held:
            Q["staff_head"], Q["staff_end"] = hand + u * HEAD_REACH, hand - u * END_REACH
        else:
            c = Q["pelvis"] + (mid - np.array(J["pelvis"][:2])) * K_LEG
            half = u * (HEAD_REACH + END_REACH) / 2
            low = max(c[1] + abs(half[1]), 0.0)                 # never into the ground: 2 squares over it
            c = c - np.array((0.0, low + 2.0 if low > -2.0 else 0.0))
            Q["staff_head"], Q["staff_end"] = c + half, c - half
        body = [q for n, q in Q.items() if not n.startswith("staff")]
        xs = [q[0] for q in Q.values()]                         # the staff kept inside the cell too
        lo, hi = min(xs + [Q["head"][0] - HEAD_R]), max(xs + [Q["head"][0] + HEAD_R])
        shift = max(0.0, (x0 + 40 - (cx + lo * SQ)) / SQ) - max(0.0, ((cx + hi * SQ) - (x0 + CELL[0] - 14)) / SQ)
        low = max([q[1] for q in body] + [Q["head"][1] + HEAD_R])
        lift = max(0.0, low)
        P = {n: (cx + (q[0] + shift) * SQ, GROUND + (q[1] - lift) * SQ) for n, q in Q.items()}
        dr.rectangle([x0, 0, x0 + CELL[0] - 1, CELL[1] - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + CELL[0] - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing", fill=(120, 120, 120), font=PR.font(16))
        dr.line([P["staff_end"], P["staff_head"]], fill=STAFF, width=4)
        hx_, hy_ = P["staff_head"]
        dr.ellipse([hx_ - 16, hy_ - 16, hx_ + 16, hy_ + 16], fill=STAFF)
        for p, q in BONES:
            if p in P and q in P:
                sides = {n[0] for n in (p, q) if n[:2] in ("l_", "r_")}
                col = (60, 60, 60) if len(sides) != 1 else NEAR if sides == {grip} else FAR
                dr.line([P[p], P[q]], fill=col, width=4)
        hx, hy = P["head"]
        r = HEAD_R * SQ
        dr.ellipse([hx - r, hy - r, hx + r, hy + r], outline=(60, 60, 60), width=3)
        for s in "lr":
            fx, fy = P[f"{s}_hand"]
            dr.ellipse([fx - 12, fy - 12, fx + 12, fy + 12], outline=(0, 60, 255), width=4)
        note = "  (casts: the crescent points at the foe)" if k0 + i == release else ""
        dr.text((x0 + 14, 12), f"frame {k0 + i + 1}{note}", fill=(0, 0, 0), font=f)
    can.save(path)


def staff_ref(out):
    """The design's staff alone (8x on grey), the crescent head and the small end named."""
    d = np.asarray(Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")).copy()
    band, head, end = DL.staff_masks(d)
    keep = band | head | end
    for x, y in DL.GLOVE:
        keep[y, x] = False
    d[~keep] = 0
    for (x, y), c in DL.shaft(d.shape[:2]).items():            # the shaft under her glove too
        if (x, y) in DL.GLOVE:
            d[y, x, :3] = c
            d[y, x, 3] = 255
    im = Image.fromarray(d)
    im = im.crop(im.getbbox())
    bg = Image.new("RGBA", (im.width + 8, im.height + 8), GREY + (255,))
    bg.alpha_composite(im, (4, 4))
    big = bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    dr.text((12, big.height - 40), "crescent head (blue gem)", fill=(200, 0, 0), font=PR.font(22))
    dr.text((big.width - 220, 12), "small end", fill=(200, 0, 0), font=PR.font(22))
    big.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--oppi", default=r"D:\steam\steamapps\workshop\content\3009300\3774304166")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    work = a.out + "_work"
    for d in (tpl, refs, work):
        os.makedirs(d, exist_ok=True)
    with open(PR.lp(os.path.join(SRC, "hd", "lux_joints.json")), encoding="utf-8") as f:
        joints = json.load(f)
    d0 = joints["design"]
    grip = "l" if d0["l_shoulder"][2] >= d0["r_shoulder"][2] else "r"     # the nearer arm holds the staff
    with open(PR.lp(os.path.join(SRC, "poses.json")), encoding="utf-8") as f:
        spec = json.load(f)
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "native_pose.py"), os.path.join(SRC, "poses.json"),
           "--out", work, "--lol", a.lol] + sum((["--tag", t] for t in TAGS), [])
    if not all(os.path.isfile(os.path.join(work, f"lux_pose_{t}.png")) for t in TAGS):
        subprocess.run(cmd, check=True, capture_output=True)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    staff_ref(os.path.join(refs, "staff.png"))
    ase = os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts", "tfm2_ase.py")
    sheets = []
    for tag in TAGS:
        frs = joints["tags"][tag]
        release = RELEASE[tag]
        heads = staff_heads(frs, release)
        for k0 in range(0, len(frs), PER_SHEET):
            idx = list(range(k0, min(k0 + PER_SHEET, len(frs))))
            name = f"{tag}_{k0 // PER_SHEET + 1}"
            template(os.path.join(tpl, name + ".png"), [frs[k] for k in idx], [heads[k] for k in idx], k0, grip,
                     release)
            PR.league_frames(os.path.join(work, f"lux_pose_{tag}.png"), idx, os.path.join(refs, f"league_{name}.png"))
            sheets.append((tag, name, idx))
    for ot in sorted(set(OPPI_TAG.values())):
        subprocess.run([sys.executable, ase, "render", os.path.join(a.oppi, "champions", "lux.aseprite"),
                        "--out", os.path.join(refs, f"oppi_{ot}.png"), "--scale", "4", "--tag", ot],
                       check=True, capture_output=True)
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "cell": CELL, "ground": GROUND, "per_sheet": PER_SHEET, "grip": grip,
                   "sheets": [dict(tag=t, name=n, frames=[k + 1 for k in idx], oppi=OPPI_TAG[t], action=NAMES[t],
                                   ms=[spec["tags"][t]["frames"][k][1] for k in idx])
                              for t, n, idx in sheets]}, f, indent=1)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets, grip", grip, "; written", zp)


RELEASE = {"attack": 3, "skill": 2, "skill2": 4, "ult": 3}     # the frame the kit casts on (0-based)


if __name__ == "__main__":
    main()
