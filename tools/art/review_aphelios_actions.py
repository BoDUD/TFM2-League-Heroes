#!/usr/bin/env python3
"""Aphelios's actions as the game shows them (the sheet's hd_ frames: tools/art/rig_aphelios.py -> ppu_restyle.py ->
ppu_hd.py) beside League's own clips, in ONE GIF for the user's review (memory one-gif-review).

    python tools/art/review_aphelios_actions.py --out DIR [--z 3]

League's frames (tools/lol/pose_ref.py, Riot's model - local only, never committed) are the moments each of our frames
stands for (REF), the clip's own weapon shown alone (A-E: Calibrum, Severum, Gravitum, Infernum, Crescendum; a weapon
form's W / R / death with that weapon), the weapon's stance (None) left blank. Every tag plays twice with its name over
it. Writes DIR/aphelios_review.gif.
"""
import argparse
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
STEM = os.path.join(ROOT, "league", "champions", "league_aphelios")
PRE = chr(92) * 2 + "?" + chr(92)
TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "aph_review")
BOX = (-48, -78, 72, 6)                # game px round the pivot: left, top, right, bottom (the soles at 11.5)
PPU = 1.5
BG = (92, 98, 86)
WEAPONS = ["calibrum", "severum", "gravitum", "infernum", "crescendum"]
LETTER = dict(zip("ABCDE", WEAPONS))
FORM = {"sev": "severum", "grav": "gravitum", "inf": "infernum", "cre": "crescendum"}
NAMES = {"run": "跑步", "a_cal": "普攻·通碧", "a_sev": "普攻·断魄", "a_grav": "普攻·坠明", "a_inf": "普攻·荧焰",
         "a_cre": "普攻·折镜", "q_cal": "Q·通碧（狙杀）", "q_sev": "Q·断魄（冲锋）", "q_grav": "Q·坠明（禁锢）",
         "q_inf": "Q·荧焰（波浪）", "q_cre": "Q·折镜（炮台）", "skill2": "W 换武器（通碧）",
         "sev_skill2": "W 换武器（断魄）", "ult": "R 清辉夜凝（通碧）", "inf_ult": "R 清辉夜凝（荧焰）",
         "dead": "阵亡（通碧）", "inf_dead": "阵亡（荧焰）", "grav_dead": "阵亡（坠明）",
         "flourish": "待机小动作（通碧）", "sev_flourish": "待机小动作（断魄）", "inf_flourish": "待机小动作（荧焰）"}
REF = {
    "run": [f"A_Run1@{t}" for t in (0, 133, 266, 399, 532, 665, 798, 931)],
    "a_cal": ["A_Attack1@99", "A_Attack1@198"] + ["A_Attack1@264"] * 3 + ["A_Attack1@297", "A_Attack1@363", None],
    "a_sev": ["B_Attack1@50", "B_Attack1@100"] + ["B_Attack1@150"] * 3 + ["B_Attack1@250", "B_Attack1@350", None],
    "a_grav": ["C_Attack1@66", "C_Attack1@165"] + ["C_Attack1@231"] * 3 + ["C_Attack1@297", "C_Attack1@363", None],
    "a_inf": ["D_Attack1@33", "D_Attack1@66"] + ["D_Attack1@165"] * 3 + ["D_Attack1@231", "D_Attack1@330", None],
    "a_cre": ["E_Attack1@100", "E_Attack1@200"] + ["E_Attack1@250"] * 3 + ["E_Attack1@350", "E_Attack1@450", None],
    "q_cal": ["A_Spell1_Activate@0", "A_Spell1_Activate@100", "A_Spell1_Activate@200", "A_Spell1_Activate@250",
              "A_Spell1_Activate@400", None],
    "q_sev": ["B_Spell1_Attack@67", "B_Spell1_Attack@134", "B_Spell1_Attack@335", "B_Spell1_Attack@469",
              "B_Spell1_Attack@603", None],
    "q_grav": ["C_Spell1@100", "C_Spell1@200", "C_Spell1@300", "C_Spell1@500", None],
    "q_inf": ["D_Spell1A@100", "D_Spell1A@200", "D_Spell1A@300", "D_Spell1A@350", "D_Spell1A@450", None],
    "q_cre": ["E_Spell1@0", "E_Spell1@100", "E_Spell1@200", "E_Spell1@300", None],
    "skill2": ["A_Spell2@0", "A_Spell2@100", "A_Spell2@150", "A_Spell2@250", "A_Spell2@450", None],
    "ult": ["spell4@300", "spell4@400", "spell4@600", "spell4@800", "spell4@1100", "spell4@1200", None],
    "dead": ["death@200", "death@400", "death@600", "death@700", "death@800", "death@900", "death@1200", "death@2000"],
}
TAGS = ["run", "a_cal", "a_sev", "a_grav", "a_inf", "a_cre", "q_cal", "q_sev", "q_grav", "q_inf", "q_cre", "skill2",
        "sev_skill2", "ult", "inf_ult", "dead", "inf_dead", "grav_dead", "flourish", "sev_flourish", "inf_flourish"]


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


def refs(tag):
    """(League keys a frame, the weapon shown) for a tag: a weapon form's W / R / death take the plain one's moments."""
    form = tag.split("_")[0]
    if form in FORM and tag not in REF:
        return REF.get(tag.split("_", 1)[1]), FORM[form]
    return REF.get(tag), None


def lol_cells(keys, weapon, size=300):
    """League's frames for keys (clip@ms; None: blank), the clip's weapon (or `weapon`) alone, cached in TMP."""
    by = {}
    for k in keys:
        if k:
            c, ms = k.split("@")
            by.setdefault(c, set()).add(int(ms))
    got = {}
    for c, mss in by.items():
        mss = sorted(mss)
        wpn = weapon or LETTER.get(c[0], "calibrum")
        d = os.path.join(TMP, f"{c}_{wpn}_{'_'.join(map(str, mss))}")
        png = os.path.join(d, f"aphelios_{c}.png")
        if not os.path.isfile(png):
            os.makedirs(d, exist_ok=True)
            cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--champ", "Aphelios",
                   "--anim", "aphelios_" + c, "--times", ",".join(map(str, mss)), "--size", str(size), "--no-labels",
                   "--bg", "232,232,232", "--out", d]
            for h in [x for x in WEAPONS if x != wpn] + ["recall", "scarf_recall", "flower"]:
                cmd += ["--hide-submesh", h]
            subprocess.run(cmd, check=True, capture_output=True)
        strip = Image.open(png).convert("RGB")
        w = strip.width // len(mss)
        for i, ms in enumerate(mss):
            got[f"{c}@{ms}"] = strip.crop((i * w, 0, (i + 1) * w, strip.height))
    return [got.get(k) if k else None for k in keys]


def hd_frames(tag, an, sheet):
    out = []
    for f in an["hd_" + tag]["frames"]:
        d = f["data"]
        out.append((sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"]))),
                    int(round(f["duration"] * 1000))))
    return out


def ours(frame, z):
    """An hd frame (its pivot at its middle, the soles 11.5 game px under it) on the review box."""
    x0, y0, x1, y1 = BOX
    can = Image.new("RGBA", ((x1 - x0) * z, (y1 - y0) * z), (*BG, 255))
    k = z / PPU
    big = frame.resize((round(frame.width * k), round(frame.height * k)), Image.NEAREST)
    can.alpha_composite(big, (int(round(-x0 * z - big.width / 2)), int(round(-y0 * z - big.height / 2))))
    ImageDraw.Draw(can).line([(0, int((11.5 - y0) * z)), (can.width, int((11.5 - y0) * z))], fill=(70, 74, 66))
    return can.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    z = a.z
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
    small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 15)
    an = json.load(open(lp(STEM + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = Image.open(lp(STEM + "#sheet.png")).convert("RGBA")
    w, h = (BOX[2] - BOX[0]) * z, (BOX[3] - BOX[1]) * z
    frames, durs = [], []
    for tag in TAGS:
        hd = hd_frames(tag, an, sheet)
        keys, wpn = refs(tag)
        cells = lol_cells(keys, wpn) if keys else [None] * len(hd)
        for rep in range(2):
            for i, (fr, ms) in enumerate(hd):
                im = Image.new("RGB", (2 * w + 12, h + 58), (30, 30, 30))
                c = cells[i] if i < len(cells) else None
                if c is not None:
                    t = c.resize((int(c.width * h / c.height), h))
                    im.paste(t, ((w - t.width) // 2, 58))
                else:
                    ImageDraw.Draw(im).text((20, 58 + h // 2), "（这一帧是武器的站姿）" if keys else "（英雄联盟没有对应动作）",
                                            fill=(170, 170, 170), font=small)
                im.paste(ours(fr, z), (w + 12, 58))
                d = ImageDraw.Draw(im)
                d.text((12, 8), f"{NAMES.get(tag, tag)}  {i + 1}/{len(hd)}", fill=(255, 240, 160), font=font)
                d.text((12, 34), "英雄联盟", fill=(200, 200, 200), font=small)
                d.text((w + 24, 34), "我们的（游戏里的高清帧）", fill=(200, 200, 200), font=small)
                frames.append(im)
                durs.append(max(20, ms))
    pal = [f.quantize(255, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(a.out, "aphelios_review.gif")
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durs, loop=0)
    print(path, len(frames), "frames")


if __name__ == "__main__":
    main()
