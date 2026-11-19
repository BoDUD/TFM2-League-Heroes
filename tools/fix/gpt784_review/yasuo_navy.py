"""league_yasuo's Nightbringer colours brought to League's in-game model (the user, 2026-11-19: 「亚索黑色使者皮肤颜色应该
不是紫色吧？」, then picked 「A dark navy」 of two mock-ups): GPT's frames drew his hair, trousers and sheath a bright
violet, and the blade-out frames (its ys_flare panel) a brighter blue still. Every blue / violet square (hue 205-300,
saturation > 0.18) of his sheet and his hd strips takes one dark navy: hue 228, saturation 0.75 x (at most 0.55),
value 0.10 + 0.62 v^1.15 (a square darker than 0.2 keeps its value: the outline stays as dark). Orange glow, skin,
sash and blade keep theirs; his effect sheets hold no blue (left). lo_ again from the dense frames
(tools/fix/xinzhao_galio_1119/sheetkit.py, ppu_hd.add_lo's replica).

    python tools/fix/gpt784_review/yasuo_navy.py            # once (refuses a sheet already navy)
    python tools/fix/gpt784_review/yasuo_navy.py --check
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402

HUE = 228.0


def hsv(a):
    a = a.astype(float) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a[..., :3].max(-1)
    mn = a[..., :3].min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = ((b - r)[gg] / d[gg]) + 2
    h[bb] = ((r - g)[bb] / d[bb]) + 4
    return h * 60.0, np.where(mx > 0, d / np.maximum(mx, 1e-6), 0), mx


def rgb(h, s, v):
    c = v * s
    x = c * (1 - np.abs((h / 60.0) % 2 - 1))
    m = v - c
    z = np.zeros_like(h)
    seg = (h // 60).astype(int) % 6
    r = np.choose(seg, [c, x, z, z, x, c])
    g = np.choose(seg, [x, c, c, x, z, z])
    b = np.choose(seg, [z, z, x, c, c, x])
    return np.stack([r + m, g + m, b + m], -1)


def cool(a):
    h, s, v = hsv(a[..., :3])
    return (a[..., 3] > 0) & (h >= 205) & (h <= 300) & (s > 0.18), h, s, v


def navy(a):
    out = a.copy()
    m, h, s, v = cool(a)
    V = np.where(v < 0.2, v, 0.10 + 0.62 * v ** 1.15)
    new = rgb(np.full_like(h, HUE), np.clip(s * 0.75, 0, 0.55), np.clip(V, 0, 1))
    out[m, :3] = np.clip(np.round(new[m] * 255), 0, 255).astype(np.uint8)
    return out


def done_share(a):
    """the share of the clearly blue squares (value >= 0.25: a dark square's hue moves a few degrees with 8-bit
    rounding) at the navy hue"""
    m, h, _, v = cool(a)
    m &= v >= 0.25
    return float((np.abs(h[m] - HUE) <= 3).mean()) if m.any() else 1.0


def strips():
    """his tags' hd strips (a .json of sizes beside each): not yasuo_codex.png / yasuo_head.png, the 2026-09 head
    picture ppu_hd.py's HEAD reads"""
    out = []
    for sub in ("", "orig"):
        d = os.path.join(ROOT, "assets", "source", "ppu", sub)
        out += [p for p in glob.glob(os.path.join(d, "yasuo_*.png")) if os.path.isfile(p[:-4] + ".json")]
    return sorted(out)


def main():
    k = Kit(ROOT, "league", "yasuo")
    plain = [t for t in k.anims if not t.startswith(("hd_", "lo_")) and t not in ("idle", "bp")]
    if "--check" in sys.argv:
        bad = 0
        for p in [k.base + "#sheet.png"] + strips():
            if done_share(np.asarray(Image.open(p).convert("RGBA"))) < 0.98:
                bad += 1
                print("not navy:", os.path.relpath(p, ROOT))
        for t in plain:
            for i in range(len(k.anims[t]["frames"])):
                if not np.array_equal(k.lo_of(k.cell(t, i).shape[:2], k.cell("hd_" + t, i)), k.cell("lo_" + t, i)):
                    bad += 1
        print("yasuo navy: OK" if not bad else f"yasuo navy: {bad} pictures / lo_ frames not as this tool leaves them")
        sys.exit(1 if bad else 0)
    if done_share(k.sheet) > 0.9:
        sys.exit("his sheet is navy already")
    k.sheet = navy(k.sheet)
    n = 0
    for t in plain:
        for i in range(len(k.anims[t]["frames"])):
            lo = k.lo_of(k.cell(t, i).shape[:2], k.cell("hd_" + t, i))
            if lo.shape != k.cell("lo_" + t, i).shape or (lo != k.cell("lo_" + t, i)).any():
                n += 1
                k.put("lo_" + t, i, lo)
    k.save()
    for p in strips():
        Image.fromarray(navy(np.asarray(Image.open(p).convert("RGBA")))).save(p)
    print(f"yasuo navy: sheet + {len(strips())} strips; {n} lo_ frames derived again")


if __name__ == "__main__":
    main()
