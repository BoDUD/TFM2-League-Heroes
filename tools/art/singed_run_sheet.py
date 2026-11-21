#!/usr/bin/env python3
"""炼金跑步（Codex 重画 + 交叉步）写进他的贴图表：hd_run / run / lo_run 三套，8 帧 x 121 毫秒（英雄联盟 singed_run 一圈
0.967 秒）。用户 2026-11-21 看了「现在 vs 新」的动图：「装」。

    python tools/art/singed_run_sheet.py --frames <cross_singed_legs.py 的输出> --review <dir>   # 只出对照图，不写
    python tools/art/singed_run_sheet.py --frames <cross_singed_legs.py 的输出>                  # 写原帧条和贴图表

帧：cross_singed_legs.py 的 8 张（57 x 106，中心就是枢轴，和他别的高清帧一样站在待机的地面上）。后面照 run_league.py 的
export 走一遍：按枢轴裁成一样大（dense_frames）、描边补到他别的帧的粗细（outlined，thin_outline.json 的 keep）、
1 倍帧（one_frames，ppu_one 的缩法）、lo_ 帧（lo_frames，ppu_hd 的 add_lo）、高清原帧条写进 assets/source/ppu/
（write_strips，以后 ppu_restyle 从这里起），三套写进贴图表（write_sheet：旧跑步的格子清掉，别的动作原地不动）。
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_league as L  # noqa: E402

HERO = "singed"
PPU = 1.39                                # hd.rs 里 league_singed 的 PPU
MS = [121] * 8                            # 英雄联盟 singed_run：0.967 秒一圈，8 帧


def make(frames_dir):
    """-> {"run", "hd_run", "lo_run": 帧, "drawn": 描边前的高清帧, "outline_px": 描边补了几格}。"""
    frames = [np.array(Image.open(os.path.join(frames_dir, f"frame_{k}.png")).convert("RGBA")) for k in range(1, 9)]
    H, W = frames[0].shape[:2]
    if any(f.shape[:2] != (H, W) for f in frames):
        sys.exit("帧的大小不一样")
    drawn, size = L.dense_frames(frames, 0, (W / 2, H / 2), PPU)
    dense = L.outlined(HERO, drawn, "hd")
    grown = sum(int(((a[..., 3] > 0) != (b[..., 3] > 0)).sum()) for a, b in zip(drawn, dense))
    ones = L.one_frames(HERO, dense, size, PPU)
    lo = L.outlined(HERO, L.lo_frames(HERO, ones, dense, MS), "lo")
    if not L.pinholes(L.idle_frame(HERO)):
        lo = [L.filled(a) for a in lo]
        ones = [L.filled(a) for a in ones]
    return {"run": ones, "hd_run": dense, "lo_run": lo, "drawn": drawn, "outline_px": grown}


def review(out, d):
    """三套帧并排（各自 4 倍 / 2 倍），看缩下来的 1 倍和 lo_ 有没有走样。"""
    os.makedirs(d, exist_ok=True)
    for tag, s in (("hd_run", 4), ("run", 6), ("lo_run", 4)):
        fr = out[tag]
        h = max(f.shape[0] for f in fr)
        w = sum(f.shape[1] + 2 for f in fr)
        img = Image.new("RGBA", (w, h), (90, 110, 80, 255))
        x = 0
        for f in fr:
            img.alpha_composite(Image.fromarray(f), (x, h - f.shape[0]))
            x += f.shape[1] + 2
        img.resize((w * s, h * s), Image.NEAREST).save(os.path.join(d, f"{tag}.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--review", help="只出对照图到这个目录，不写原帧条和贴图表")
    a = ap.parse_args()
    out = make(a.frames)
    for t in L.TAGS:
        print(f"{t}: {len(out[t])} frames {out[t][0].shape[1]}x{out[t][0].shape[0]}")
    print(f"outline grown by {out['outline_px']} squares over the 8 hd frames")
    if a.review:
        review(out, a.review)
        return
    L.write_strips(HERO, out["hd_run"], PPU, orig=out["drawn"])
    w, h = L.write_sheet(HERO, {t: list(zip(out[t], MS)) for t in L.TAGS})
    print(f"league_{HERO}#sheet.png {w}x{h}: run / hd_run / lo_run 8 frames of {MS[0]} ms")


if __name__ == "__main__":
    main()
