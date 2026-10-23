"""The Codex pack for league_ahri's cast frames drawn whole (assets/source/ahri/ACTIONS_PROMPT_PPU.md): every frame of her
attack, Orb of Deception (skill), Charm (skill2) and Spirit Rush (ult) a new drawing of the approved design
(hd/design.png, PPU 2.2) in League's pose of that frame, arms, body and tails moving - the way league_lux's casts were
redrawn (tools/art/pack_lux_actions.py) and then mended onto the design (tools/art/casts_lux_hd.py's way). Her idle,
run, hit and death are rigged from the design's own squares (the user, 2026-10-24: 「按这个分工做：跑步/受击/死亡你来摆，
平A/Q/E/R 出 Codex 整帧重画包」).

    python tools/art/pack_ahri_actions.py --out C:/t/ar_actions [--lol D:/WeGameApps/lol] [--oppi DIR]

Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds TWO frames in cells of 768 x 1024 on squares of SQ px
(one design square: the design is 78 x 88 of them): League's skeleton of that frame (hd/ahri_joints.json,
tools/lol/league_joints.py on assets/source/ahri/poses.json) fitted to her build as a stick guide (near limbs blue,
far grey), her hands as blue circles, her head with the ears as a circle, her tails' line (violet: League's tail
bones; the tails themselves stay the design's big fan, swinging with the motion), the ground line, the standing point
and a bar as tall as she stands. refs/: the design at 8x and 1x, its palette, each sheet's League frames rendered
(tools/lol/native_pose.py, Riot's model - local only, never committed), oppi's Ahri (style only). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "ahri")
TAGS = ["attack", "skill", "skill2", "ult"]
NAMES = {"attack": "basic attack, a spirit orb flicked from her hand at the foe (Ahri_Attack1)",
         "skill": "Orb of Deception, the orb thrown forward with a sweep of the arm (Ahri_Spell1)",
         "skill2": "Charm, a heart blown from her hand with a kiss (Ahri_Spell3)",
         "ult": "Spirit Rush, a quick dash forward, the tails streaming behind (Ahri_Spell4)"}
OPPI_TAG = {"attack": "attack", "skill": "skill", "skill2": "skill2", "ult": "ult"}
RELEASE = {"attack": 3, "skill": 3, "skill2": 3, "ult": 2}      # the frame the kit casts on (0-based)
SQ = 6                                   # px a design square in the templates
CELL = (768, 1024)
GROUND = 1024 - 150
PER_SHEET = 2
STAND = 88                               # design rows from her ear tips to her soles
GREY = (225, 225, 225)
NEAR, FAR = (40, 120, 230), (150, 150, 150)
TAIL = (150, 90, 210)
# her build in design squares (hd/design.png: soles on row 88, hips about 28 over them, the chest 16 over the hips, the
# head with the hair and ears centred 22 over the chest with 19 squares round it, the near arm about 17 long) against
# League's design pose (Idle1@0: pelvis 22.4 game px up, the chest 3.3 over it, the near arm 10.4)
K_LEG, K_UP, K_ARM = 1.25, 4.8, 1.6
HEAD_UP, HEAD_R = 22.0, 19.0
K_TAIL = 1.6
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
    for k in range(1, 6):
        out[f"tail{k}"] = pel + (v[f"tail{k}"] - v["pelvis"]) * K_TAIL
    return out


def template(path, frames, k0, near, release):
    """TWO frames of one action: per cell the stick guide, hand circles, head circle, the tails' line, ground,
    standing point."""
    can = Image.new("RGB", (CELL[0] * PER_SHEET, CELL[1]), (255, 255, 255))
    dr = ImageDraw.Draw(can)
    f = PR.font(26)
    for i, fr in enumerate(frames):
        x0 = i * CELL[0]
        cx = x0 + CELL[0] / 2
        Q = her_joints(fr["j"])
        xs = [q[0] for q in Q.values()]
        lo, hi = min(xs + [Q["head"][0] - HEAD_R]), max(xs + [Q["head"][0] + HEAD_R])
        shift = max(0.0, (x0 + 40 - (cx + lo * SQ)) / SQ) - max(0.0, ((cx + hi * SQ) - (x0 + CELL[0] - 14)) / SQ)
        low = max([q[1] for n, q in Q.items() if not n.startswith("tail")] + [Q["head"][1] + HEAD_R])
        lift = max(0.0, low)
        P = {n: (cx + (q[0] + shift) * SQ, GROUND + (q[1] - lift) * SQ) for n, q in Q.items()}
        dr.rectangle([x0, 0, x0 + CELL[0] - 1, CELL[1] - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + CELL[0] - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing (ear tips)", fill=(120, 120, 120),
                font=PR.font(16))
        dr.line([P[f"tail{k}"] for k in range(1, 6)], fill=TAIL, width=6)
        dr.text((P["tail5"][0] - 30, P["tail5"][1] + 8), "tails", fill=TAIL, font=PR.font(18))
        for p, q in BONES:
            if p in P and q in P:
                sides = {n[0] for n in (p, q) if n[:2] in ("l_", "r_")}
                col = (60, 60, 60) if len(sides) != 1 else NEAR if sides == {near} else FAR
                dr.line([P[p], P[q]], fill=col, width=4)
        hx, hy = P["head"]
        r = HEAD_R * SQ
        dr.ellipse([hx - r, hy - r, hx + r, hy + r], outline=(60, 60, 60), width=3)
        for s in "lr":
            fx, fy = P[f"{s}_hand"]
            dr.ellipse([fx - 12, fy - 12, fx + 12, fy + 12], outline=(0, 60, 255), width=4)
        note = "  (casts: the hand flicks toward the foe)" if k0 + i == release else ""
        dr.text((x0 + 14, 12), f"frame {k0 + i + 1}{note}", fill=(0, 0, 0), font=f)
    can.save(path)


def league_frames(pose_png, idx, out, cell):
    """Frames idx (0-based) of native_pose's 8x render grid (4 columns of cells `cell` = (w, h) px: poses.json's
    "cell" x 8), trimmed, side by side."""
    im = Image.open(pose_png).convert("RGBA")
    cw, ch = cell
    cols = im.width // cw
    crops = []
    for k in idx:
        c = im.crop(((k % cols) * cw, (k // cols) * ch, (k % cols + 1) * cw, (k // cols + 1) * ch))
        bb = c.getbbox() or (0, 0, cw, ch)
        crops.append(c.crop((max(0, bb[0] - 30), max(0, bb[1] - 30), min(cw, bb[2] + 30), min(ch, bb[3] + 30))))
    h = max(c.height for c in crops)
    can = Image.new("RGBA", (sum(c.width for c in crops) + 20 * len(crops), h + 50), GREY + (255,))
    dr = ImageDraw.Draw(can)
    x = 0
    for k, c in zip(idx, crops):
        can.alpha_composite(c, (x, 40))
        dr.text((x + 6, 8), f"League frame {k + 1}", fill=(0, 0, 0), font=PR.font(22))
        x += c.width + 20
    can.convert("RGB").save(out)


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
    with open(PR.lp(os.path.join(SRC, "hd", "ahri_joints.json")), encoding="utf-8") as f:
        joints = json.load(f)
    d0 = joints["design"]
    near = "l" if d0["l_shoulder"][2] >= d0["r_shoulder"][2] else "r"
    with open(PR.lp(os.path.join(SRC, "poses.json")), encoding="utf-8") as f:
        spec = json.load(f)
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "native_pose.py"), os.path.join(SRC, "poses.json"),
           "--out", work, "--lol", a.lol] + sum((["--tag", t] for t in TAGS), [])
    if not all(os.path.isfile(os.path.join(work, f"ahri_pose_{t}.png")) for t in TAGS):
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
            template(os.path.join(tpl, name + ".png"), [frs[k] for k in idx], k0, near, RELEASE[tag])
            league_frames(os.path.join(work, f"ahri_pose_{tag}.png"), idx, os.path.join(refs, f"league_{name}.png"),
                          (spec["cell"][0] * 8, spec["cell"][1] * 8))
            sheets.append((tag, name, idx))
    for ot in sorted(set(OPPI_TAG.values())):
        r = subprocess.run([sys.executable, ase, "render", os.path.join(a.oppi, "champions", "cf_ahri.aseprite"),
                            "--out", os.path.join(refs, f"oppi_{ot}.png"), "--scale", "4", "--tag", ot],
                           capture_output=True)
        if r.returncode:
            print("oppi: no tag", ot)
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "cell": CELL, "ground": GROUND, "per_sheet": PER_SHEET, "near": near,
                   "sheets": [dict(tag=t, name=n, frames=[k + 1 for k in idx], oppi=OPPI_TAG[t], action=NAMES[t],
                                   ms=[spec["tags"][t]["frames"][k][1] for k in idx])
                              for t, n, idx in sheets]}, f, indent=1)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets, near arm", near, "; written", zp)


if __name__ == "__main__":
    main()
