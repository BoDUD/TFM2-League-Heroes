#!/usr/bin/env python3
"""薇古丝寒心波云的两段（2026-11-26，照英雄联盟 V26.13：波先慢、宽，再快、窄）。

    python -I tools/art/fx_vex_q.py                     # 往 league/effects/league_vex_fx 加 q_wave / q_dart（和 hd_）
    python -I tools/art/fx_vex_q.py --check             # 表里的就是这个脚本画的（CI）
    python -I tools/art/fx_vex_q.py --gif out.gif [--slow 3]   # 像素准确的飞行动图（1 倍一排、高清一排）

只用她自己已有的特效帧，不用 Codex、不用外面的图：
- `q_wave`：宽的慢波。英雄联盟这一段 360 宽、后一段 160 宽，判定半径 q_w1 = 18000 对 q_w = 8000，画面也大一倍：原来的
  `q_bolt`（17 x 17 的月牙）整张放大一倍。1 倍帧就是 `hd_q_bolt` 那几帧（它本来就是 q_bolt 的 scale2x），高清帧再 scale2x
  一次——同一张画，只是大，没有一个部件被拉长或挪开。
- `q_dart`：窄的快波，就是 `q_bolt` 的帧，只是开头空着几 tick：它晚一点从她身上出手，追上慢波之前藏着，从慢波的前沿
  冲出来才看得见（空几 tick 由 build_vex.P 的速度算）。
两张都和 q_bolt 一样朝右画（游戏按飞行方向转），帧时长照 build_vex.P 的飞行时间。表里别的 tag 和帧都不动（新的 tag 排在最后），
league.dll 的 fx_ppu.rs 用 include_str 读这张表，重新编过才认识新 tag。
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import densify_fx as D  # noqa: E402
import strips as G  # noqa: E402
from build_vex import P, q_timing  # noqa: E402

STEM = os.path.join(ROOT, "league", "effects", "league_vex_fx")
HERO = os.path.join(ROOT, "league", "champions", "league_vex")
TAGS = ("q_wave", "q_dart")
FRAME_MS = 60            # q_bolt 的帧长
TICK_MS = 1000 / 60


def load(stem):
    anims = json.load(open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sheet = np.asarray(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA"))
    return anims, sheet


def frames_of(anims, sheet, tag):
    out = []
    for f in anims[tag]["frames"]:
        d = f["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        out.append((sheet[y:y + h, x:x + w].copy(), f["duration"] * 1000))
    return out


def flight(cells, lead_ticks, fly_ticks):
    """开头空 lead_ticks（3 x 3 的空格子），然后四帧轮着放到飞完，最后一帧拿一秒（不会半路放完）。"""
    blank = np.zeros((3, 3, 4), np.uint8)
    out = [(blank, lead_ticks * 1000 / 60)]
    k = max(1, math.ceil(max(fly_ticks - lead_ticks, 1) * TICK_MS / FRAME_MS))
    for i in range(k):
        out.append((cells[i % len(cells)], FRAME_MS if i < k - 1 else 1000))
    return out


def dart_hidden(p):
    """窄的那条藏几 tick：它的前沿过了慢波画面的前沿才露出来（两张都按 1 倍画面的一半长算，1000 一个像素）。"""
    t1, lag, _, _ = q_timing(p)
    half_wave, half_dart = 17 * 1000, 17 * 1000 / 2
    for k in range(t1 - lag):
        dart = p["q_s2"] * (k + 1)
        wave = p["q_s1"] * (k + lag + 1)
        if dart + half_dart >= wave + half_wave:
            return k
    return t1 - lag


def q_tags(anims, sheet, p=P):
    """{tag: [(帧, ms)]}：q_wave、q_dart 和它们的 hd_。"""
    bolt = [a for a, _ in frames_of(anims, sheet, "q_bolt")[1:5]]
    hd_bolt = [a for a, _ in frames_of(anims, sheet, "hd_q_bolt")[1:5]]
    for a, b in zip(bolt, hd_bolt):
        if not np.array_equal(D.scale2x(a), b):
            sys.exit("hd_q_bolt is no longer q_bolt's scale2x: update this script")
    t1, lag, _, _ = q_timing(p)
    fly_dart = math.ceil(p["q_len"] / p["q_s2"])
    hide = dart_hidden(p)
    out = {
        "q_wave": flight(hd_bolt, 1, t1),
        "q_dart": flight(bolt, hide, fly_dart),
    }
    out["hd_q_wave"] = [(D.scale2x(a), ms) for a, ms in out["q_wave"]]
    out["hd_q_dart"] = [(D.scale2x(a), ms) for a, ms in out["q_dart"]]
    return out


def sheet_tags(anims, sheet, new):
    """表里每个 tag 照旧、照原来的顺序，新的排最后（先 1 倍的，再 hd_）。"""
    tags = {t: frames_of(anims, sheet, t) for t in anims if t not in new}
    for t in TAGS:
        tags[t] = new[t]
    for t in TAGS:
        tags["hd_" + t] = new["hd_" + t]
    return tags


def check(anims, sheet, new):
    for t, frames in new.items():
        got = frames_of(anims, sheet, t) if t in anims else []
        if len(got) != len(frames) or any(not np.array_equal(a, b) or abs(ma - mb) > 0.5
                                          for (a, ma), (b, mb) in zip(got, frames)):
            sys.exit(f"{t}: the sheet is not this script's drawing: python -I tools/art/fx_vex_q.py")
    print("league_vex_fx: q_wave / q_dart up to date")


# ------------------------------------------------------------------ review
def at_ms(frames, ms):
    """放了 ms 毫秒时的那一帧。"""
    for a, d in frames:
        if ms < d:
            return a
        ms -= d
    return frames[-1][0]


def gif(path, slow, anims, sheet, new, p=P):
    """像素准确：1 倍帧放大 4 倍、高清帧放大 2 倍（同样大），纯色地面，颜色不超过 256 个。上一排 1 倍、下一排高清；
    她的待机站在出手的地方，波往右飞。一 tick 一帧，每帧 20 x slow 毫秒。"""
    h_anims, h_sheet = load(HERO)
    idle1 = frames_of(h_anims, h_sheet, "idle")[0][0]
    idle2 = frames_of(h_anims, h_sheet, "hd_idle")[0][0]
    t1, lag, _, _ = q_timing(p)
    fly_dart = math.ceil(p["q_len"] / p["q_s2"])
    ticks = lag + fly_dart + 6
    Z = 4
    width = int((p["q_len"] / 1000 + 40) * Z)
    lane_h = 30 * Z
    bg = (58, 72, 48)
    frames = []
    for t in range(-4, ticks):
        can = Image.new("RGBA", (width, lane_h * 2 + 24), bg + (255,))
        d = ImageDraw.Draw(can)
        d.fontmode = "1"
        d.text((4, 2), f"tick {t}  (1x x{Z} / hd x{Z // 2})", fill=(255, 255, 0))
        for lane, (idle, zf, suf) in enumerate(((idle1, Z, ""), (idle2, Z // 2, "hd_"))):
            y0 = 24 + lane * lane_h + lane_h // 2
            x0 = 16 * Z
            im = Image.fromarray(idle).resize((idle.shape[1] * zf, idle.shape[0] * zf), Image.NEAREST)
            can.alpha_composite(im, (x0 - im.width // 2, y0 - im.height // 2))
            shots = []
            if 0 <= t < t1:
                pos = min(p["q_s1"] * (t + 1), p["q_l1"])
                shots.append((new[suf + "q_wave"], t, pos))
            if lag <= t < lag + fly_dart:
                k = t - lag
                pos = min(p["q_s2"] * (k + 1), p["q_len"])
                shots.append((new[suf + "q_dart"], k, pos))
            for fr, k, pos in shots:
                a = at_ms(fr, k * TICK_MS)
                im = Image.fromarray(a).resize((a.shape[1] * zf, a.shape[0] * zf), Image.NEAREST)
                cx = x0 + int(round(pos / 1000 * Z))
                can.alpha_composite(im, (cx - im.width // 2, y0 - im.height // 2))
        frames.append(can.convert("RGB"))
    cols = set()
    for f in frames:
        cols |= set(f.get_flattened_data() if hasattr(f, "get_flattened_data") else f.getdata())
    if len(cols) > 256:
        sys.exit(f"{len(cols)} colours: a GIF would merge some")
    pal = Image.new("RGB", (len(cols), 1))
    pal.putdata(list(cols))
    pal = pal.quantize(colors=len(cols), method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=20 * slow, loop=0, disposal=1)
    print("gif:", path, len(frames), "frames,", len(cols), "colours")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--gif")
    ap.add_argument("--slow", type=int, default=3)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    anims, sheet = load(STEM)
    new = q_tags(anims, sheet)
    if a.check:
        check(anims, sheet, new)
        return
    if a.gif:
        gif(a.gif, a.slow, anims, sheet, new)
        return
    tags = sheet_tags(anims, sheet, new)
    w, h = G.write_sheet(G.lp(STEM), tags, share=True)
    print(f"league/effects/league_vex_fx#sheet.png {w}x{h}: + " + ", ".join(
        f"{t} {len(new[t])}f {sum(ms for _, ms in new[t]):.0f}ms" for t in new))


if __name__ == "__main__":
    main()
