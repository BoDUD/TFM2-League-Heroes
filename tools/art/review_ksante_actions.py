#!/usr/bin/env python3
"""K'Sante's actions as the game shows them (the sheet's hd_ frames: tools/art/rig_ksante.py -> ppu_restyle.py ->
ppu_hd.py) beside League's own clips, in ONE GIF for the user's review (「动作帧请做到完美后喊我review」), then the showcase
(tools/art/preview_ksante.py).

    python tools/art/review_ksante_actions.py --out DIR [--z 2]

League's frames: tools/lol/pose_ref.py on the local client (Riot's model - local only, never committed), at the beat
each of our rig frames stands for (LOL: one clip@ms per frame of rig_ksante.MS), 3/4 and mirrored like the pose pack
(tools/art/pack_ksante_poses.py: yaw 35 base, 15 All Out); All Out's clips with the stone shells hidden and the blades
shown. An hd frame shows League's frame of the rig frame it falls in (the baked effects split frames); the idle reels
cycle League's idle. Every tag plays twice (the idle reels once) with its name over it; the hits have no League clip.
Writes DIR/ksante_review.gif.
"""
import argparse
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_ksante as K  # noqa: E402

STEM = os.path.join(ROOT, "league", "champions", "league_ksante")
SHOWCASE = os.path.join(ROOT, "docs", "preview", "league_ksante_showcase.gif")
CACHE = "C:/t/ks_work/review_lol"
BOX = (-95, -112, 95, 6)               # hd px round the standing point / the row under the soles
BG = (92, 98, 86)
LOL_BG = (232, 232, 232)
BASE_LOL = ["--submesh-texture", "Weapon=Weapons_TX", "--submesh-texture", "RWeaponShield=Weapons_TX",
            "--submesh-texture", "LWeaponShield=Weapons_TX"]
for _s in ("RWeaponShieldSmearTop", "RWeaponShieldSmearBot", "LWeaponShieldSmearTop", "LWeaponShieldSmearBot",
           "RWeaponBlade", "LWeaponBlade"):
    BASE_LOL += ["--hide-submesh", _s]
AO_LOL = ["--submesh-texture", "Weapon=Weapons_TX", "--submesh-texture", "RWeaponBlade=Weapons_TX",
          "--submesh-texture", "LWeaponBlade=Weapons_TX"]
for _s in ("RWeaponShield", "LWeaponShield", "RWeaponShieldSmearTop", "RWeaponShieldSmearBot", "LWeaponShieldSmearTop",
           "LWeaponShieldSmearBot"):
    AO_LOL += ["--hide-submesh", _s]

NAMES = {
    "idle": "待机（定格 + 小动作）", "run": "跑步", "attack": "普攻", "skill": "Q 无双陀斧 · 第一下", "skill_b": "Q 第二下",
    "skill_c": "Q 第三下（冲击波拉人）", "skill2": "W 辟路先锋 · 蓄力", "skill2_dash": "W 冲撞", "ult": "R 傲岸雄姿 · 踢击（破陀斧变全盛）",
    "ult_dash": "R 追击砸地", "hit": "受击", "dead": "阵亡",
    "ao_idle": "全盛 · 待机", "ao_run": "全盛 · 跑步", "ao_attack": "全盛 · 普攻横扫", "ao_skill": "全盛 · Q", "ao_skill_b": "全盛 · Q 第二下",
    "ao_skill_c": "全盛 · Q 第三下", "ao_skill2": "全盛 · W 蓄力", "ao_skill2_dash": "全盛 · W 冲撞", "ao_hit": "全盛 · 受击",
}
TAGS = list(NAMES)
# League's frame for each rig frame (rig_ksante.MS): clip@ms
LOL = {
    "idle": ["Idle1@0", "Idle1@600", "Idle1@1200", "Idle1@1800"],
    "run": ["Run1@0", "Run1@267", "Run1@533", "Run1@800"],
    "attack": ["attack1@0", "attack1@170", "attack1@350", "attack1@450", "attack1@1000"],
    "skill": ["Spell1_A@60", "Spell1_A@120", "Spell1_A@400", "Spell1_A@480", "Spell1_A@800"],
    "skill_b": ["Spell1_B@60", "Spell1_B@150", "Spell1_B@400", "Spell1_B@480", "Spell1_B@800"],
    "skill_c": ["Spell1_C@30", "Spell1_C@150", "Spell1_C@450", "Spell1_C@550", "Spell1_C@800"],
    "skill2": ["Spell2_Enter@200", "Spell2_Loop@300"],
    "skill2_dash": ["Spell2_Dash@100", "Spell2_Dash@200", "Spell2_Dash@300", "Spell2_Dash@400"],
    "ult": ["Spell4_A@200", "Spell4_A@600", "Spell4_A@1000", "Spell4_A@1300"],
    "ult_dash": ["Spell4_dash@100", "Spell4_dash@300", "Spell4_Attack_noWall@200"],
    "dead": ["Death@0", "Death@300", "Death@2000", "Death@2900"],
    "ao_idle": ["Idle1_AllOut@0", "Idle1_AllOut@600", "Idle1_AllOut@1200", "Idle1_AllOut@1800"],
    "ao_run": ["Run_AllOut@0", "Run_AllOut@267", "Run_AllOut@533", "Run_AllOut@800"],
    "ao_attack": ["Attack1_AllOut@200", "Attack1_AllOut@300", "Attack1_AllOut@450", "Attack1_AllOut@550",
                  "Attack1_AllOut@1200"],
    "ao_skill": ["Spell1_A_AllOut@100", "Spell1_A_AllOut@200", "Spell1_A_AllOut@600", "Spell1_A_AllOut@700",
                 "Spell1_A_AllOut@1200"],
    "ao_skill_b": ["Spell1_B_AllOut@100", "Spell1_B_AllOut@200", "Spell1_B_AllOut@600", "Spell1_B_AllOut@700",
                   "Spell1_B_AllOut@1200"],
    "ao_skill_c": ["Spell1_C_AllOut@100", "Spell1_C_AllOut@200", "Spell1_C_AllOut@600", "Spell1_C_AllOut@700",
                   "Spell1_C_AllOut@1200"],
    "ao_skill2": ["Spell2_Enter_AllOut@150", "Spell2_Enter_AllOut@300"],
    "ao_skill2_dash": ["Spell2_Dash_AllOut@0", "Spell2_Dash_AllOut@100", "Spell2_Dash_AllOut@200",
                       "Spell2_Dash_AllOut@300"],
}
REELS = ("idle", "ao_idle")


def hd_frames(tag):
    anims = json.load(open(K.lp(STEM + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = Image.open(K.lp(STEM + "#sheet.png")).convert("RGBA")
    out = []
    for f in anims["hd_" + tag]["frames"]:
        d = f["data"]
        out.append((sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"]))),
                    int(round(f["duration"] * 1000))))
    return out


def lol_strip(tag, w, h):
    """League's frames for a tag (pose_ref.py; Riot's model: local only), cached."""
    frames = LOL[tag]
    ao = tag.startswith("ao_") or tag == "ult_dash"
    os.makedirs(CACHE, exist_ok=True)
    name = f"{tag}_{w}x{h}"
    path = os.path.join(CACHE, name + ".png")
    if not os.path.isfile(path):
        cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--champ", "KSante", "--hq",
               "--mirror", "--yaw", "15" if ao else "35", "--size", str(h), "--width", f"{w / h:.4f}", "--fit", "0.55",
               "--ground", f"{-BOX[1] / (BOX[3] - BOX[1]):.4f}", "--no-labels", "--bg", ",".join(map(str, LOL_BG)),
               "--name", name, "--out", CACHE, *(AO_LOL if ao else BASE_LOL)]
        for f in frames:
            cmd += ["--frame", f]
        subprocess.run(cmd, check=True, capture_output=True)
    strip = Image.open(path).convert("RGB")
    cw = strip.width // len(frames)
    return [strip.crop((i * cw, 0, (i + 1) * cw, strip.height)).resize((w, h)) for i in range(len(frames))]


def ours(frame, z):
    """An hd frame (its pivot at its middle, the soles FEET x PPU under it) on the review box."""
    x0, y0, x1, y1 = BOX
    can = Image.new("RGBA", ((x1 - x0) * z, (y1 - y0) * z), (*BG, 255))
    big = frame.resize((frame.width * z, frame.height * z), Image.NEAREST)
    px = (-x0) * z - frame.width / 2 * z
    py = (-y0) * z - (frame.height / 2 + 11.5 * K.PPU) * z
    can.alpha_composite(big, (int(round(px)), int(round(py))))
    return can.convert("RGB")


def rig_index(tag, t):
    """The rig frame (rig_ksante.MS) an hd frame starting t ms into the tag falls in."""
    acc = 0
    for k, ms in enumerate(K.MS[tag]):
        acc += ms
        if t < acc:
            return k
    return len(K.MS[tag]) - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=int, default=2)
    ap.add_argument("--tags", help="only these (comma-separated)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    z = a.z
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
    small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 15)
    w, h = (BOX[2] - BOX[0]) * z, (BOX[3] - BOX[1]) * z
    frames, durs = [], []
    for tag in [t for t in TAGS if not a.tags or t in a.tags.split(",")]:
        hd = hd_frames(tag)
        lol = lol_strip(tag, w, h) if tag in LOL else None
        for rep in range(1 if tag in REELS else 2):
            t = 0
            for i, (fr, ms) in enumerate(hd):
                im = Image.new("RGB", (2 * w + 12, h + 58), (30, 30, 30))
                if lol:
                    k = i % len(lol) if tag in REELS else rig_index(tag, t)
                    im.paste(lol[k], (0, 58))
                else:
                    ImageDraw.Draw(im).text((20, 58 + h // 2), "（英雄联盟没有对应动作）", fill=(170, 170, 170), font=small)
                im.paste(ours(fr, z), (w + 12, 58))
                d = ImageDraw.Draw(im)
                d.text((12, 8), f"{NAMES[tag]}  {i + 1}/{len(hd)}", fill=(255, 240, 160), font=font)
                d.text((12, 34), "英雄联盟", fill=(200, 200, 200), font=small)
                d.text((w + 24, 34), "我们的（游戏里的高清帧）", fill=(200, 200, 200), font=small)
                frames.append(im)
                durs.append(max(20, ms))
                t += ms
    if os.path.isfile(K.lp(SHOWCASE)) and not a.tags:
        sc = Image.open(K.lp(SHOWCASE))
        W, H = frames[0].size
        title = Image.new("RGB", (W, H), (30, 30, 30))
        ImageDraw.Draw(title).text((20, H // 2 - 20), "实战演示：普攻、Q 三段拉人接 W、R 踢飞追击变全盛接 W", fill=(255, 240, 160),
                                   font=font)
        frames.append(title)
        durs.append(1200)
        k = W / sc.width
        for i in range(sc.n_frames):
            sc.seek(i)
            f = sc.convert("RGB").resize((W, int(round(sc.height * k))), Image.NEAREST)
            im = Image.new("RGB", (W, H), (30, 30, 30))
            im.paste(f, (0, (H - f.height) // 2))
            frames.append(im)
            durs.append(sc.info.get("duration", 40))
    pal = [f.quantize(255, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(a.out, "ksante_review.gif")
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durs, loop=0)
    print(path, len(frames), "frames")


if __name__ == "__main__":
    main()
