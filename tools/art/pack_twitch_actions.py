"""The Codex pack for league_twitch's actions drawn whole at PPU 2.2 (assets/source/twitch/ACTIONS_PROMPT_PPU.md):
every frame of his run, attack, Ambush (skill), Venom Cask (skill2), Contaminate (skill2_e), Spray and Pray (ult), hit
and death a new drawing of the approved design (hd/design.png, 109 x 71 squares) in the pose of his OLD sheet's same
frame - the motion the user approved before - the way Ahri's actions were redrawn (tools/art/pack_ahri_actions.py on
ahri-ppu22). The user, 2026-10-24: 「动作让 Codex 照旧版同一帧整帧重画，你修到设计图上，先做动作包」.

    python tools/art/pack_twitch_actions.py --out C:/t/tw_actions [--old-sheet PNG --old-fanim FANIM] [--lol DIR]

Each template sheet (templates/<tag>_<k>.png, 1536 x 1024) holds TWO frames in cells of 768 x 1024 on squares of SQ px
(one design square): the old 1x frame scaled to his height (PPU 2.2 squares a pixel), faded, as the pose to follow,
standing on the ground line at the standing point, and a bar as tall as he stands. refs/: the design at 8x and 1x,
its palette, each sheet's old frames in colour, and League's frames of that action (tools/lol/pose_ref.py on
assets/source/twitch/poses.json: Riot's model, local only, never committed) as the motion reference - oppi's pack has
no Twitch. The old sheet is main's (league/champions/league_twitch#sheet.png / #anim.fanim). Then <out>.zip.
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

SRC = os.path.join(REPO, "assets", "source", "twitch")
STEM = os.path.join(REPO, "league", "champions", "league_twitch")
TAGS = ["run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]
NAMES = {"run": "running (his move loop), hunched forward, the crossbow held in both hands",
         "attack": "basic attack, a crossbow bolt fired forward from the levelled crossbow, a small recoil",
         "skill": "Ambush: he crouches low and sneaks, the crossbow held close, ready to vanish",
         "skill2": "Venom Cask: the far hand swings a small poison cask up and throws it forward at the foe",
         "skill2_e": "Contaminate: a hop, the crossbow and the body jerked, the poison on the foes bursting",
         "ult": "Spray and Pray: the crossbow raised and fired hard forward, a big recoil",
         "hit": "struck, knocked back a little",
         "dead": "death: knocked back, he falls and lies on the ground, the crossbow dropped"}
RELEASE = {"attack": 2, "skill2": 2, "skill2_e": 3, "ult": 1}    # the frame the kit casts on (0-based)
SQ = 5                                   # px a design square in the templates
PPU = 2.2                                # design squares an old pixel
CELL = (768, 1024)
GROUND = 1024 - 200
PER_SHEET = 2
STAND = 71                               # design rows from his ear tips to his soles
OLD_SOLES = 11                           # old frames: the soles this many pixels under the frame's centre (its pivot)
GREY = (225, 225, 225)


def old_frames(sheet_png, fanim):
    px = np.asarray(Image.open(sheet_png).convert("RGBA"))
    with open(fanim, encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag in TAGS:
        fr = []
        for f_ in anims[tag]["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000)))
        out[tag] = fr
    return out


def placed(frame, x0):
    """The old frame scaled to his height in a cell starting at x0: its pivot (the frame's centre) on the standing
    point, kept inside the cell. -> (RGBA image, left, top)."""
    k = PPU * SQ
    h, w = frame.shape[:2]
    im = Image.fromarray(frame).resize((round(w * k), round(h * k)), Image.NEAREST)
    cx = x0 + CELL[0] / 2
    left = round(cx - (w / 2) * k)
    top = round(GROUND - OLD_SOLES * k - (h / 2) * k)
    bb = im.getbbox()
    if bb:
        lo, hi = left + bb[0], left + bb[2]
        if lo < x0 + 40:
            left += x0 + 40 - lo
        elif hi > x0 + CELL[0] - 14:
            left -= hi - (x0 + CELL[0] - 14)
    return im, left, top


def template(path, frames, k0, release):
    """TWO frames: per cell the old frame faded as the pose, ground, standing point, his height."""
    can = Image.new("RGBA", (CELL[0] * PER_SHEET, CELL[1]), (255, 255, 255, 255))
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * CELL[0])
        a = np.asarray(im).astype(float)
        faded = a.copy()
        faded[..., :3] = a[..., :3] * 0.35 + 255 * 0.65                  # a pale picture of the pose
        can.alpha_composite(Image.fromarray(faded.astype(np.uint8)), (left, top))
    dr = ImageDraw.Draw(can)
    f = PR.font(26)
    for i, (fr, ms) in enumerate(frames):
        x0 = i * CELL[0]
        cx = x0 + CELL[0] / 2
        dr.rectangle([x0, 0, x0 + CELL[0] - 1, CELL[1] - 1], outline=(60, 60, 60), width=2)
        dr.line([(x0, GROUND), (x0 + CELL[0] - 1, GROUND)], fill=(90, 90, 90), width=3)
        dr.line([(cx, GROUND - 12), (cx, GROUND + 12)], fill=(90, 90, 90), width=3)
        bx = x0 + 16
        dr.line([(bx, GROUND), (bx, GROUND - STAND * SQ)], fill=(160, 160, 160), width=4)
        dr.text((bx + 8, GROUND - STAND * SQ - 4), "his height standing (ear tips)", fill=(120, 120, 120),
                font=PR.font(16))
        note = "  (the shot leaves now)" if k0 + i == release else ""
        dr.text((x0 + 14, 12), f"frame {k0 + i + 1}, {ms} ms{note}", fill=(0, 0, 0), font=f)
    can.convert("RGB").save(path)


def old_ref(frames, k0, out):
    """The sheet's old frames in colour at the same scale, side by side."""
    can = Image.new("RGBA", (CELL[0] * len(frames), CELL[1]), GREY + (255,))
    dr = ImageDraw.Draw(can)
    for i, (fr, ms) in enumerate(frames):
        im, left, top = placed(fr, i * CELL[0])
        can.alpha_composite(im, (left, top))
        dr.text((i * CELL[0] + 14, 12), f"old frame {k0 + i + 1}", fill=(0, 0, 0), font=PR.font(26))
    can.convert("RGB").save(out)


def league_ref(lol, tag, out):
    """League's frames of the action (poses.json's for the tag), his head enlarged as the design's."""
    spec = json.load(open(PR.lp(os.path.join(SRC, "poses.json")), encoding="utf-8"))
    cam = spec["camera"]
    cmd = [sys.executable, os.path.join(REPO, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Twitch",
           "--hq", "--head", str(spec["chibi"]["head"]), "--yaw", str(cam["yaw"]), "--pitch", str(cam["pitch"]),
           "--hide-submeshes", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "420", "--width", "1.3",
           "--fit", "0.55", "--ground", "0.9", "--name", f"lol_{tag}", "--out", out]
    if cam.get("mirror"):
        cmd.append("--mirror")
    for clip, _ in spec["tags"][tag]["frames"]:
        cmd += ["--frame", clip]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-sheet", default=STEM + "#sheet.png")
    ap.add_argument("--old-fanim", default=STEM + "#anim.fanim")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    tpl, refs = os.path.join(a.out, "templates"), os.path.join(a.out, "refs")
    for d in (tpl, refs):
        os.makedirs(d, exist_ok=True)
    old = old_frames(a.old_sheet, a.old_fanim)
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 8, bg.height * 8), Image.NEAREST).save(os.path.join(refs, "design.png"))
    shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "design.png")), os.path.join(refs, "design_1x.png"))
    a_ = np.asarray(des)
    PR.palette(np.unique(a_[a_[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    sheets = []
    for tag in TAGS:
        frs = old[tag]
        for k0 in range(0, len(frs), PER_SHEET):
            part = frs[k0:k0 + PER_SHEET]
            name = f"{tag}_{k0 // PER_SHEET + 1}"
            template(os.path.join(tpl, name + ".png"), part, k0, RELEASE.get(tag, -1))
            old_ref(part, k0, os.path.join(refs, f"old_{name}.png"))
            sheets.append((tag, name, list(range(k0, k0 + len(part))), [ms for _, ms in part]))
        league_ref(a.lol, tag, refs)
        print(tag, len(frs), "frames")
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"square": SQ, "cell": CELL, "ground": GROUND, "per_sheet": PER_SHEET,
                   "sheets": [dict(tag=t, name=n, frames=[k + 1 for k in idx], action=NAMES[t], ms=ms)
                              for t, n, idx, ms in sheets]}, f, indent=1)
    shutil.copyfile(PR.lp(os.path.join(SRC, "ACTIONS_PROMPT_PPU.md")), os.path.join(a.out, "ACTIONS_PROMPT.md"))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print(len(sheets), "sheets; written", zp)


if __name__ == "__main__":
    main()
