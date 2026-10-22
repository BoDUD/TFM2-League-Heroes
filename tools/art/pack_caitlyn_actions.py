"""The Codex pack for league_caitlyn's action frames drawn whole (assets/source/caitlyn/ACTIONS_PROMPT_PPU.md): every
frame of her run, attack, Headshot, Piltover Peacemaker (skill), Yordle Snap Trap (skill2), 90 Caliber Net (e), Ace in
the Hole (ult), hit and death a new drawing of the approved design (hd/design.png, PPU 1.45) in League's pose of that
frame, the way league_riven's attacks were redrawn (tools/art/pack_riven_actions.py; her idle stays the design).

    python tools/art/pack_caitlyn_actions.py --out C:/t/ct_actions [--lol D:/WeGameApps/lol] [--oppi DIR]

The user, 2026-10-22/23: 「我们下一个英雄使用PPU重做凯特琳吧」, the design 「设计通过，用 PPU 1.45（和现在一样高）」.
She holds the rifle in both hands, so Codex draws it with her (unlike Riven's sword, pasted afterwards). Each
template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds THREE frames in cells of 512 x 1024 on squares of SQ px
(one design square: the design is 54 x 65 of them): League's skeleton of that frame (assets/source/caitlyn/hd/
caitlyn_joints.json) fitted to her build as a stick guide (near limbs blue, far grey), her two hands as blue circles,
the rifle as a red line (stock to muzzle, its length in the design), her head with the hat as a circle, the ground
line, the standing point (half of League's travel) and a bar as tall as she stands. refs/: the design at 8x, each
sheet's League frames rendered (tools/lol/native_pose.py, Riot's model - local only, never committed), oppi's
Caitlyn for the same kind of move (style only), the design's palette. Then <out>.zip.
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
import pack_riven_actions as PR  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "caitlyn")
TAGS = ["run", "attack", "passive", "skill", "skill2", "e", "ult", "hit", "dead"]
NAMES = {"run": "run (caitlyn run)", "attack": "basic attack, a shot from the hip (attack1)",
         "passive": "Headshot, the aimed shot (passive)", "skill": "Piltover Peacemaker, the long aimed shot (spell1)",
         "skill2": "Yordle Snap Trap, throwing a trap (spell2)",
         "e": "90 Caliber Net, a shot that kicks her back off the ground (spell3)",
         "ult": "Ace in the Hole, kneeling to aim and the big shot (spell4)", "hit": "hit, flinching (death's start)",
         "dead": "death, falling down"}
OPPI_TAG = {"run": "run", "attack": "attack", "passive": "attack", "skill": "skill", "skill2": "attack",
            "e": "skill2", "ult": "ult", "hit": "hit", "dead": "death"}
SQ = 6                                   # px a design square in the templates (her rifle is 59 squares long)
CELL = (512, 1024)
GROUND = 1024 - 150
PER_SHEET = 3
STAND = 65                               # design rows from her hat's top to her soles
GREY = (225, 225, 225)
NEAR, FAR = (40, 120, 230), (150, 150, 150)
# her build in design squares (hd/design.png: soles on row 65, hips about 22 over them, shoulders about 38, the head
# with the hat centred about 52 with 13 squares round it, arms about 10, the rifle 15 squares behind her trigger hand
# and 44 ahead of it) against League's design pose (pelvis 21.5 game px up, shoulders about 7 over it, arms about 7)
K_LEG, K_UP, K_ARM = 1.0, 2.3, 1.4
HEAD_UP, HEAD_R = 20.5, 13.0
RIFLE_BACK, RIFLE_AHEAD = 15.0, 44.0
LUNGE = 0.5
BONES = PR.BONES


def her_joints(j):
    """League's joints of a frame on her design's build, in design squares from her standing point (PR.her_joints with
    her own scales)."""
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
    w = v["weapon_tip"] - v["weapon"]
    out["rifle_u"] = w / (np.linalg.norm(w) or 1)
    return out


def template(path, frames, k0, near):
    """THREE frames of one action: per cell the stick guide, hand circles, rifle line, head circle, ground, standing
    point. near: "l" or "r", League's side nearer the camera."""
    can = Image.new("RGB", (CELL[0] * PER_SHEET, CELL[1]), (255, 255, 255))
    dr = ImageDraw.Draw(can)
    f = PR.font(26)
    for i, fr in enumerate(frames):
        x0 = i * CELL[0]
        cx = x0 + CELL[0] / 2
        Q = her_joints(fr["j"])
        u = Q.pop("rifle_u")
        grip = Q[f"{near}_hand"]
        Q["stock"], Q["muzzle"] = grip - u * RIFLE_BACK, grip + u * RIFLE_AHEAD
        body = [q for n, q in Q.items() if n not in ("stock", "muzzle")]
        xs = [q[0] for q in body]
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
        dr.line([P["stock"], P["muzzle"]], fill=(255, 0, 0), width=4)
        for a, b in BONES:
            if a in P and b in P:
                sides = {n[0] for n in (a, b) if n[:2] in ("l_", "r_")}
                col = (60, 60, 60) if len(sides) != 1 else NEAR if sides == {near} else FAR
                dr.line([P[a], P[b]], fill=col, width=4)
        hx, hy = P["head"]
        r = HEAD_R * SQ
        dr.ellipse([hx - r, hy - r, hx + r, hy + r], outline=(60, 60, 60), width=3)
        for s in "lr":
            fx, fy = P[f"{s}_hand"]
            dr.ellipse([fx - 12, fy - 12, fx + 12, fy + 12], outline=(0, 60, 255), width=4)
        dr.text((x0 + 14, 12), f"frame {k0 + i + 1}", fill=(0, 0, 0), font=f)
    can.save(path)


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
    with open(PR.lp(os.path.join(SRC, "hd", "caitlyn_joints.json")), encoding="utf-8") as f:
        joints = json.load(f)
    d0 = joints["design"]
    near = "l" if d0["l_hip"][2] >= d0["r_hip"][2] else "r"
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "native_pose.py"), os.path.join(SRC, "poses.json"),
           "--out", work, "--lol", a.lol] + sum((["--tag", t] for t in TAGS), [])
    if not all(os.path.isfile(os.path.join(work, f"caitlyn_pose_{t}.png")) for t in TAGS):
        subprocess.run(cmd, check=True, capture_output=True)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    ase = os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts", "tfm2_ase.py")
    sheets = []
    for tag in TAGS:
        frs = joints["tags"][tag]
        for k0 in range(0, len(frs), PER_SHEET):
            idx = list(range(k0, min(k0 + PER_SHEET, len(frs))))
            name = f"{tag}_{k0 // PER_SHEET + 1}"
            template(os.path.join(tpl, name + ".png"), [frs[k] for k in idx], k0, near)
            PR.league_frames(os.path.join(work, f"caitlyn_pose_{tag}.png"), idx, os.path.join(refs, f"league_{name}.png"))
            sheets.append((tag, name, idx))
    for ot in sorted(set(OPPI_TAG.values())):
        subprocess.run([sys.executable, ase, "render", os.path.join(a.oppi, "champions", "caitlyn2.aseprite"),
                        "--out", os.path.join(refs, f"oppi_{ot}.png"), "--scale", "4", "--tag", ot],
                       check=True, capture_output=True)
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "cell": CELL, "ground": GROUND, "per_sheet": PER_SHEET, "near": near,
                   "sheets": [dict(tag=t, name=n, frames=[k + 1 for k in idx], oppi=OPPI_TAG[t], action=NAMES[t])
                              for t, n, idx in sheets]}, f, indent=1)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets, near", near, "; written", zp)


if __name__ == "__main__":
    main()
