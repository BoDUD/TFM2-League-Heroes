#!/usr/bin/env python3
"""终末包换成 Q 版像素画：把 Codex 重画的像素写进每个英雄的图集，帧表、PPU 都不动。

    python tools/art/ragnarok_q_pixel.py                  # 写 ragnarok/champions/<英雄>#sheet.png
    python tools/art/ragnarok_q_pixel.py --check          # 和现在的图集不一样就退出 1
    python tools/art/ragnarok_q_pixel.py --hero thor      # 只做这几个（可以给多个 --hero）

用户 2026-11-23：「女武神换成了Q版像素风格 帮我整体更换一下 还有BP格子也是 现在这个系列的就用Q版像素风格就行了 但是还是要用PPU
保持高清」。Codex 交的（assets/source/q_pixel，交接说明 HANDOFF.md，每个文件对过 checksums.json）：18 个英雄连 6 套形态的战斗图集，
1 倍、hd_、lo_ 三档都重画成 Q 版，以用户认过的阿波罗试画为准。它交的是 0.11.0 发行版那一版图集（tools/package_mod.py 打过包的：
相同的帧合成一格、挨着排），每个 #anim.fanim 和发行版逐字节相同，只换了像素。

仓库里的图集没打包（import_<英雄>.py、ppu_hd.py、hero_reels.py、ragnarok_run_pace.py 写的），帧放的位置不一样；打包只挪 x、y，所以
每个动作的帧数、每帧的大小和时长两边都一样：按「同一个动作的第几帧」把 Q 版那一格的像素拷到仓库那一格。高清帧（hd_）还是高清帧、
PPU 照旧（hd.rs 的表不动），选人格子和百科的界面图是打包时从这些帧重新拼的（ui_sheets/），跟着变成 Q 版。特效图、弹道图、技能图标、
选人立绘不在这次重画里，照旧。
两边帧表对不上的动作（比如以后 hero_reels.py 重挑的待机、选人片段：它们只引用别的动作已有的格子）跳过；仓库里每一个被引用的格子都得
从对得上的动作拿到像素，拿不到、或者同一格拿到两份不一样的像素，都报错不写。
导入（import_<英雄>.py）写的还是 Codex 原来那一版的画：重新导入一个英雄以后按顺序跑 ppu_hd.py、hero_reels.py、ragnarok_run_pace.py，
最后跑这个。

修的一处（用户看了索尔：「应该是这个手的位置歪了」「其他帧数是对的」）：Q 版索尔待机第 0 帧扛锤的那只手举在脸前，挡住半张脸，锤子
也低了一截；第 1-7 帧手都在肩上握着锤柄。第 0 帧换成第 1 帧的画（循环里紧挨着；下半身和第 0 帧最像：1 倍帧只差 52 个像素），1 倍、
hd_、lo_ 三档都换，按格子的中心（脚底的中线）对齐。第 0 帧也是选人格子、百科和头像截图用的那一帧。
阿波罗待机第 0 帧也和别的帧不是同一版画（窄一圈，胸甲和腰带之间一道黑线），用户先说「阿波罗这里的黑线也处理下」，看了以后：「算了不用改了
就用黑线吧」——照 Codex 交的原样，不改。
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHEETS = os.path.join(ROOT, "ragnarok", "champions")
Q = os.path.join(ROOT, "assets", "source", "q_pixel", "champions")
# (英雄, 动作, 改哪一帧, 用哪一帧的画)：动作的 hd_ / lo_ 跟着一起改
FIX = [("ragnarok_thor", "idle_base", 0, 1)]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read(stem):
    sheet = np.asarray(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    return sheet, anims


def rect(f):
    d = f["data"]
    return tuple(int(round(d[k])) for k in ("x", "y", "w", "h"))


def same_shape(a, b):
    """两个动作的帧表除了位置都一样：帧数、每帧的大小和时长。"""
    fa, fb = a["frames"], b["frames"]
    return len(fa) == len(fb) and all(rect(x)[2:] == rect(y)[2:] and x["duration"] == y["duration"] for x, y in zip(fa, fb))


def q_sheet(hid):
    """一个英雄的仓库图集换成 Q 版的像素 -> (新图集, 用上的动作数, 跳过的动作)。"""
    sheet, anims = read(os.path.join(SHEETS, hid))
    qs, qa = read(os.path.join(Q, hid))
    out = np.zeros_like(sheet)
    got = {}
    used, skipped = 0, []
    for tag, a in anims.items():
        if tag not in qa or not same_shape(a, qa[tag]):
            skipped.append(tag)
            continue
        used += 1
        for f, g in zip(a["frames"], qa[tag]["frames"]):
            x, y, w, h = rect(f)
            u, v, _, _ = rect(g)
            px = qs[v:v + h, u:u + w]
            if (x, y, w, h) in got:
                if not np.array_equal(got[(x, y, w, h)], px):
                    raise SystemExit(f"{hid} {tag}: the cell at {(x, y, w, h)} gets two different Q pictures")
                continue
            got[(x, y, w, h)] = px
            out[y:y + h, x:x + w] = px
    for tag, a in anims.items():
        for f in a["frames"]:
            if rect(f) not in got:
                raise SystemExit(f"{hid} {tag}: the cell at {rect(f)} has no Q picture (no matching tag holds it)")
    for fid, tag, dst, src in FIX:
        if fid != hid:
            continue
        for pre in ("", "hd_", "lo_"):
            fr = anims[pre + tag]["frames"]
            x, y, w, h = rect(fr[dst])
            sx, sy, sw, sh = rect(fr[src])
            if (w - sw) % 2 or (h - sh) % 2:
                raise SystemExit(f"{hid} {pre}{tag}: frames {dst} and {src} do not share a centre ({w}x{h} / {sw}x{sh})")
            cell = np.zeros((h, w, 4), np.uint8)
            ox, oy = (w - sw) // 2, (h - sh) // 2
            if ox < 0 or oy < 0:
                raise SystemExit(f"{hid} {pre}{tag}: frame {src} is bigger than frame {dst}")
            cell[oy:oy + sh, ox:ox + sw] = out[sy:sy + sh, sx:sx + sw]
            out[y:y + h, x:x + w] = cell
    return out, used, skipped


def heroes(only):
    ids = sorted(os.path.basename(p).split("#")[0] for p in os.listdir(Q) if p.endswith("#sheet.png"))
    if only:
        want = {h if h.startswith("ragnarok_") else "ragnarok_" + h for h in only}
        missing = want - set(ids)
        if missing:
            raise SystemExit(f"no Q sheet for {sorted(missing)}")
        ids = [i for i in ids if i in want]
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--hero", action="append")
    a = ap.parse_args()
    bad = 0
    for hid in heroes(a.hero):
        new, used, skipped = q_sheet(hid)
        path = os.path.join(SHEETS, hid + "#sheet.png")
        old = np.asarray(Image.open(lp(path)).convert("RGBA"))
        if a.check:
            if not np.array_equal(old, new):
                print(f"{hid}: not the Q picture - run tools/art/ragnarok_q_pixel.py")
                bad += 1
            continue
        if not np.array_equal(old, new):
            Image.fromarray(new).save(lp(path))
        print(f"{hid}: {used} tags from the Q sheet" + (f", skipped {', '.join(skipped)}" if skipped else ""))
    if a.check:
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
