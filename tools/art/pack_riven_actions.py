"""The Codex pack for league_riven's action frames redrawn whole (assets/source/riven/ACTIONS_PROMPT_PPU.md): her
three basic attacks, Broken Wings' three strikes (skill, q2, q3) and Valor + Ki Burst (skill2), every frame a new
drawing of the approved design (hd/design.png, PPU 1.5) in League's pose of that frame, the way oppi's pack draws her.

    python tools/art/pack_riven_actions.py --out C:/t/rv_actions [--lol D:/WeGameApps/lol] [--oppi DIR]

The user, 2026-10-18, after the rigged frames (the design's parts turned and moved, the body itself never changing):
「E的冲刺也一个姿势？」「你去玩玩全全参考英雄联盟」「你看看隔壁oppi咋做的」, then 「让 Codex 按定稿设计图逐帧重画平A
三套、E、Q（参考英雄联盟关键帧和 oppi 画风），你做素材包」.

Codex draws her body only. Her sword is not drawn: the rig puts one of Codex's sword drawings (hd/swords/) in her
fist afterwards, so the R form's tags take the same frames with the reforged sword. Each template sheet
(templates/<tag>_<k>.png, 1536 x 1024) holds THREE frames in cells of 512 x 1024 on squares of SQ px (one design
square: the design is 68 x 61 of them): League's skeleton of that frame (riven_joints.json, scaled so League's
`height` is her standing height in the design) as a stick guide, her sword fist (League's weapon hand) as a blue
circle, the way the sword will point from it as a red line, the ground line, the standing point (the unit's origin,
League's travel kept) and a bar as tall as she stands. refs/: the design without its sword (8x), each sheet's League
frames rendered (tools/lol/native_pose.py, Riot's model - local only, never committed), oppi's Riven for the same
action (style only), the design's palette. Then <out>.zip.
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
SRC = os.path.join(REPO, "assets", "source", "riven")
TAGS = ["attack", "attack2", "attack3", "skill", "q2", "q3", "skill2"]
NAMES = {"attack": "basic attack 1 (riven_attack1)", "attack2": "basic attack 2 (riven_attack2)",
         "attack3": "basic attack 3 (riven_attack3)", "skill": "Broken Wings, 1st strike (riven_spell1a)",
         "q2": "Broken Wings, 2nd strike (riven_spell1b)", "q3": "Broken Wings, 3rd strike - the leap (riven_spell1c)",
         "skill2": "Valor dash then Ki Burst (riven_spell3 -> riven_spell2)"}
OPPI_TAG = {"attack": "attack", "attack2": "attack", "attack3": "attack", "skill": "skill", "q2": "skillp2",
            "q3": "flip", "skill2": "skill2"}
SQ = 8                                   # px a design square in the templates
CELL = (512, 1024)
GROUND = 1024 - 150                      # the ground line's row in a cell
PER_SHEET = 3
STAND = 56                               # design rows from her hair's top to her soles (rig_riven_hd BODY_ROWS * PPU)
GREY = (225, 225, 225)
BONES = [("pelvis", "chest"), ("chest", "head"), ("l_shoulder", "l_elbow"), ("l_elbow", "l_hand"),
         ("r_shoulder", "r_elbow"), ("r_elbow", "r_hand"), ("l_hip", "l_knee"), ("l_knee", "l_foot"),
         ("r_hip", "r_knee"), ("r_knee", "r_foot"), ("l_shoulder", "r_shoulder"), ("l_hip", "r_hip"),
         ("pelvis", "l_hip"), ("pelvis", "r_hip"), ("chest", "l_shoulder"), ("chest", "r_shoulder")]
NEAR, FAR = (40, 120, 230), (150, 150, 150)     # near limbs (League's left) blue-ish, far limbs grey
# her build in design squares (hd/design.png: soles on row 61, hips on 44.5, shoulders about 31, the head's middle about
# 15 with 11 squares of hair and face round it, arms about 8 long) against League's design pose (pelvis 18.1 game px up,
# shoulders about 7 over it, arms about 9)
K_LEG, K_UP, K_ARM = 0.91, 2.1, 0.95
HEAD_UP, HEAD_R = 21.0, 11.0
LUNGE = 0.5


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def font(n):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", n)
    except OSError:
        return ImageFont.load_default()


def her_joints(j):
    """League's joints of a frame (game px, x forward, y down from the floor) on her design's build, in design squares
    from her standing point: League's chibi keeps its big head on the neck joint and longer legs and arms, so a single
    scale made the stick figure a third shorter than she stands - the legs scaled to her hips' height (K_LEG), the
    trunk to her shoulders' (K_UP), the arms to her arms' length (K_ARM), the head HEAD_UP squares on from the chest
    along League's neck."""
    v = {n: np.array(x[:2], float) for n, x in j.items() if isinstance(x, list)}
    pel = v["pelvis"] * K_LEG * np.array((LUNGE, 1.0))     # half of League's travel (the rig kept 0.7 of it)
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
    for n in ("weapon", "weapon_tip"):
        out[n] = v[n]
    return out


def template(path, frames, k0):
    """THREE frames of one action: per cell the stick guide, fist circle, sword line, ground, standing point."""
    can = Image.new("RGB", (CELL[0] * PER_SHEET, CELL[1]), (255, 255, 255))
    dr = ImageDraw.Draw(can)
    f = font(28)
    for i, fr in enumerate(frames):
        x0 = i * CELL[0]
        cx = x0 + CELL[0] / 2
        Q = her_joints(fr["j"])
        xs = [q[0] for n, q in Q.items() if not n.startswith("weapon")]
        lo, hi = min(xs + [Q["head"][0] - HEAD_R]), max(xs + [Q["head"][0] + HEAD_R])
        # the whole figure inside its cell (the third attack's leap went out of it); the standing point stays
        shift = max(0.0, (x0 + 50 - (cx + lo * SQ)) / SQ) - max(0.0, ((cx + hi * SQ) - (x0 + CELL[0] - 14)) / SQ)
        # never under the ground: the third strike's somersault turned her head down past her feet (her big head
        # hangs far from the chest), so the whole figure goes up until its lowest point is on the ground
        low = max([q[1] for n, q in Q.items() if not n.startswith("weapon")] + [Q["head"][1] + HEAD_R])
        lift = max(0.0, low)
        P = {n: (cx + (q[0] + shift) * SQ, GROUND + (q[1] - lift) * SQ) for n, q in Q.items()}
        dr.rectangle([x0, 0, x0 + CELL[0] - 1, CELL[1] - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + CELL[0] - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 20                     # her standing height
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "her height standing", fill=(120, 120, 120), font=font(18))
        for a, b in BONES:
            if a in P and b in P:
                near = a.startswith("l_") or b.startswith("l_")
                far = a.startswith("r_") or b.startswith("r_")
                col = NEAR if near and not far else FAR if far and not near else (60, 60, 60)
                dr.line([P[a], P[b]], fill=col, width=5)
        hx, hy = P["head"]
        r = HEAD_R * SQ                  # her head with its hair, as big as in the design
        dr.ellipse([hx - r, hy - r, hx + r, hy + r], outline=(60, 60, 60), width=3)
        fx, fy = P["r_hand"]
        dr.ellipse([fx - 16, fy - 16, fx + 16, fy + 16], outline=(0, 60, 255), width=4)
        wa, wb = np.array(P["weapon"]), np.array(P["weapon_tip"])
        u = (wb - wa) / (np.linalg.norm(wb - wa) or 1)
        dr.line([tuple(np.array((fx, fy)) + u * 20), tuple(np.array((fx, fy)) + u * 31 * SQ * 0.8)],
                fill=(255, 0, 0), width=3)
        dr.text((x0 + 14, 12), f"frame {k0 + i + 1}", fill=(0, 0, 0), font=f)
    can.save(path)


def no_sword_design(out):
    import rig_riven_hd as RV
    import ppu_rig as R
    D = RV.design()
    rig = RV.make_rig(D)
    legs = {lg["name"]: RV.leg_piece(D, lg) for lg in (RV.FRONT, RV.BACK)}
    lay = [("arm", dict(angle=0, about=RV.SHOULDER))] + [(legs[lg["name"]], dict()) for lg in (RV.BACK, RV.FRONT)]
    lay += [("upper", dict()), ("forearm", dict(angle=0, about=RV.ELBOW))]
    can = rig.finish(R.compose(rig, lay))
    ys, xs = np.nonzero(can[..., 3] > 0)
    im = Image.fromarray(can[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    bg = Image.new("RGBA", (im.width + 4, im.height + 4), GREY + (255,))
    bg.alpha_composite(im, (2, 2))
    bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST).save(out)
    op = can[..., 3] > 0
    return np.unique(can[op][:, :3], axis=0)


def palette(cols, out):
    cols = sorted(cols.tolist(), key=lambda c: sum(c))
    n = len(cols)
    per = 8
    im = Image.new("RGB", (per * 150, (n + per - 1) // per * 60), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    f = font(16)
    for i, c in enumerate(cols):
        x, y = (i % per) * 150, (i // per) * 60
        dr.rectangle([x + 4, y + 4, x + 50, y + 50], fill=tuple(c), outline=(0, 0, 0))
        dr.text((x + 56, y + 20), "#%02X%02X%02X" % tuple(c), fill=(0, 0, 0), font=f)
    im.save(out)


def league_frames(pose_png, idx, out, cell=768):
    """Frames idx (0-based) of native_pose's 8x render grid (4 columns of `cell` px), trimmed, side by side."""
    im = Image.open(pose_png).convert("RGBA")
    cols = im.width // cell
    crops = []
    for k in idx:
        c = im.crop(((k % cols) * cell, (k // cols) * cell, (k % cols + 1) * cell, (k // cols + 1) * cell))
        bb = c.getbbox()
        crops.append(c.crop((max(0, bb[0] - 30), max(0, bb[1] - 30), min(cell, bb[2] + 30), min(cell, bb[3] + 30))))
    h = max(c.height for c in crops)
    can = Image.new("RGBA", (sum(c.width for c in crops) + 20 * len(crops), h + 50), GREY + (255,))
    dr = ImageDraw.Draw(can)
    x = 0
    for k, c in zip(idx, crops):
        can.alpha_composite(c, (x, 50 + h - c.height))
        dr.text((x + 10, 8), f"frame {k + 1}", fill=(0, 0, 0), font=font(28))
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
    with open(lp(os.path.join(SRC, "hd", "riven_joints.json")), encoding="utf-8") as f:
        joints = json.load(f)
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "native_pose.py"), os.path.join(SRC, "poses.json"),
           "--out", work, "--lol", a.lol] + sum((["--tag", t] for t in TAGS), [])
    if not all(os.path.isfile(os.path.join(work, f"riven_pose_{t}.png")) for t in TAGS):
        subprocess.run(cmd, check=True, capture_output=True)
    cols = no_sword_design(os.path.join(refs, "design_no_sword.png"))
    palette(cols, os.path.join(refs, "design_palette.png"))
    shutil.copyfile(lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    ase = os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts", "tfm2_ase.py")
    sheets = []
    for tag in TAGS:
        frs = joints["tags"][tag]
        for k0 in range(0, len(frs), PER_SHEET):
            idx = list(range(k0, min(k0 + PER_SHEET, len(frs))))
            name = f"{tag}_{k0 // PER_SHEET + 1}"
            template(os.path.join(tpl, name + ".png"), [frs[k] for k in idx], k0)
            league_frames(os.path.join(work, f"riven_pose_{tag}.png"), idx, os.path.join(refs, f"league_{name}.png"))
            sheets.append((tag, name, idx))
    for ot in sorted(set(OPPI_TAG.values())):
        subprocess.run([sys.executable, ase, "render", os.path.join(a.oppi, "champions", "wythm_riven.aseprite"),
                        "--out", os.path.join(refs, f"oppi_{ot}.png"), "--scale", "4", "--tag", ot],
                       check=True, capture_output=True)
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "cell": CELL, "ground": GROUND, "per_sheet": PER_SHEET,
                   "sheets": [dict(tag=t, name=n, frames=[k + 1 for k in idx], oppi=OPPI_TAG[t], action=NAMES[t])
                              for t, n, idx in sheets]}, f, indent=1)
    shutil.copyfile(lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets; written", zp)


if __name__ == "__main__":
    main()
