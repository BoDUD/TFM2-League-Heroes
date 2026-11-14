"""Gangplank's Silver Serpents pictures (the add-on league_gangplank 0.3.0, 2026-11-12).

    python tools/art/gangplank_sv_fx.py                    # league/effects/league_gangplank_sv#sheet.png / #anim.fanim
    python tools/art/gangplank_sv_fx.py --check            # (tests) the sheet is what this script draws
    python tools/art/gangplank_sv_fx.py --preview out.gif  # a look at them in a mock barrage (x3)
    python tools/art/gangplank_sv_fx.py --strip out.png    # six moments of it side by side

The user (2026-11-12): 「船长银蛇币的系统能做吗」 -> 「开始做」. The add-on's copy of Gangplank (tools/kit/build_gangplank.py with
native) buys Cannon Barrage's three upgrades with the serpents its Parrrley kills plunder, and draws from this sheet:

- `r_dd_warn` (z -2, 0.5 s): Death's Daughter's mark where the mega-cannonball comes down - a gold ring of its reach
  (r_dd_r, 25 game px, flattened like the kegs' scorch), an inner ring closing in, blinking at the end, the ball's
  shadow growing;
- `r_dd_fall` (z 2, 0.5 s): the mega-cannonball dropping on the barrage's middle, a flame trail behind it;
- `r_dd_boom` (z 2): it lands - the kegs' own blast (league_gangplank_big `e_boom`, as drawn) over a gold shockwave and a
  white-gold flash;
- `r_rm` (z -1, looped): Raise Morale on an ally in the barrage - a turning gold ring at the feet, sparks rising;
- `sv_coin` (z 3, over him): a Parrrley kill's plunder - a silver serpent coin spinning up over his head, fading.

Since 2026-11-14 each tag has its hd_ twin (PPU 2, fx_vector.redraw_tag - dense()), so the sheet is drawn dense.
The ball, the rings and the coin are drawn here (no source art) in the colours of the kegs' blast and the barrage's balls.
1 sheet px = 1 game px, like league_gangplank_fx / _big (the barrage's r_r of 58 game px is r_wave's 117 px); a frame is
drawn with its centre on the effect's position.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIG = os.path.join(ROOT, "league", "effects", "league_gangplank_big")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_vector as V  # noqa: E402  (the dense twins, 2026-11-14)
OUT = os.path.join(ROOT, "league", "effects", "league_gangplank_sv")
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# the kegs' blast and the barrage's balls (league_gangplank_big), the orange's gold ring (league_gangplank_fx w_imm)
FIRE = [rgb(c) for c in ("#fff6c0", "#ffd25a", "#ff9a28", "#e2541a", "#8e2410")]
IRON = [rgb(c) for c in ("#e8e8ec", "#a8aab2", "#6e727c", "#464a52", "#2a2c32", "#141418")]
GOLD = [rgb(c) for c in ("#ffffff", "#fff2b0", "#ffd04a", "#ff9e1e", "#e06a10", "#b86a18")]
SILVER = [rgb(c) for c in ("#ffffff", "#e8e8ec", "#b4b7c2", "#8c909e", "#555965", "#3d3e47")]
SCORCH = rgb("#1e120a")

DD_R = 25           # Death's Daughter's reach (build_gangplank.P r_dd_r 25000), game px
FLAT = 0.32         # ground ellipses: ry = FLAT x rx (the kegs' scorch, e_boom's last frame: 53 x 17)
FALL = 96           # the mega-cannonball starts this high over the ground
DD_FRAMES, DD_MS = 10, 50   # r_dd_warn / r_dd_fall: 0.5 s, the kit's r_dd_t (30 ticks)
COIN_Y = (40, 52)   # the coin rises over his position (his face is 29 px up, Kindred's hunt mark 47)
FEET = 10           # a unit's feet under its position (its buff pictures at the feet: league_gangplank_fx p_ms 9-11 px)


# ------------------------------------------------------------------------------------------------------------- drawing
def canvas(half_w, half_h):
    """An empty frame whose centre pixel is the effect's position."""
    return np.zeros((2 * half_h + 1, 2 * half_w + 1, 4), np.uint8)


def put(a, x, y, color, alpha=255):
    """One pixel (frame coordinates from the centre), straight alpha over what is there."""
    h, w = a.shape[:2]
    px, py = int(round(x)) + w // 2, int(round(y)) + h // 2
    if not (0 <= px < w and 0 <= py < h) or alpha <= 0:
        return
    src = alpha / 255.0
    dst = a[py, px, 3] / 255.0
    out = src + dst * (1 - src)
    if out <= 0:
        return
    for c in range(3):
        a[py, px, c] = int(round((color[c] * src + a[py, px, c] * dst * (1 - src)) / out))
    a[py, px, 3] = int(round(out * 255))


def ring(a, rx, ry, color, alpha=255, dashes=0, phase=0.0, cy=0, half=None):
    """An ellipse's outline; with dashes, that many dashes (and as many gaps), turned by phase (in dashes); half "back"
    (its far side, up the screen) or "front" only."""
    steps = max(64, int(8 * (rx + ry)))
    seen = set()
    for k in range(steps):
        th = 2 * math.pi * k / steps
        if dashes and int(math.floor(th / (2 * math.pi) * 2 * dashes + 2 * phase)) % 2:
            continue
        if half is not None and (math.sin(th) < 0) != (half == "back"):
            continue
        p = (int(round(rx * math.cos(th))), int(round(cy + ry * math.sin(th))))
        if p not in seen:
            seen.add(p)
            put(a, p[0], p[1], color, alpha)


def blob(a, rx, ry, color, alpha, cx=0, cy=0):
    """A filled ellipse."""
    for y in range(-int(ry) - 1, int(ry) + 2):
        for x in range(-int(rx) - 1, int(rx) + 2):
            if rx > 0 and ry > 0 and (x / rx) ** 2 + (y / ry) ** 2 <= 1.0:
                put(a, cx + x, cy + y, color, alpha)


def ball(a, cy, r):
    """The mega-cannonball: iron, lit from the upper left, outlined."""
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            d = math.hypot(x, y)
            if d > r + 0.35:
                continue
            if d > r - 0.65:
                c = IRON[5]
            else:
                lit = (-x - y) / (r * 1.414)            # -1 .. 1 towards the light
                c = IRON[1] if lit > 0.55 else IRON[2] if lit > 0.15 else IRON[3] if lit > -0.35 else IRON[4]
                if (x, y) == (-r // 2, -r // 2):
                    c = IRON[0]
            put(a, x, cy + y, c)


def trail(a, cy, r, length, flicker):
    """The flame over the falling ball: widest at the ball, white-hot there, red at its tip."""
    for k in range(length):
        f = k / max(1, length - 1)                     # 0 at the ball, 1 at the tip
        half = (r + 1) * (1 - f) ** 0.7
        y = cy - r + 1 - k
        sway = flicker if f > 0.6 else 0
        col = FIRE[min(4, int(f * 5))]
        for x in range(-int(half), int(half) + 1):
            edge = abs(x) >= int(half) and half >= 1
            put(a, x + sway, y, FIRE[min(4, int(f * 5) + 1)] if edge else col, 230 if edge else 255)


# --------------------------------------------------------------------------------------------------------- the frames
def dd_warn():
    out = []
    ry = round(DD_R * FLAT)
    for i in range(DD_FRAMES):
        t = (i + 0.5) / DD_FRAMES
        a = canvas(DD_R + 2, ry + 2)
        sr = 2 + 6 * t * t
        blob(a, sr, sr * FLAT * 1.4, SCORCH, int(70 + 90 * t))
        late = i >= DD_FRAMES - 4
        bright = late and i % 2 == 0
        ring(a, DD_R, ry, GOLD[1] if bright else GOLD[2] if not late else GOLD[4], 255, dashes=12, phase=i * 0.25)
        inner = DD_R - (DD_R - 6) * t
        ring(a, inner, inner * FLAT, GOLD[3], int(140 + 115 * t))
        for sx, sy in ((-1, 0), (1, 0)):
            for k in range(2):
                put(a, sx * (DD_R - 2 - k), 0, GOLD[1] if bright else GOLD[2])
        for sy in (-1, 1):
            put(a, 0, sy * (ry - 1), GOLD[1] if bright else GOLD[2])
        out.append((a, DD_MS))
    return out


def dd_fall():
    out = []
    r = 5
    for i in range(DD_FRAMES):
        t = (i + 0.5) / DD_FRAMES
        y = -FALL * (1 - t * t)
        a = canvas(r + 3, FALL + r + 24)
        trail(a, round(y), r, int(6 + 16 * t), (-1, 1)[i % 2])
        ball(a, round(y), r)
        out.append((a, DD_MS))
    return out


def e_boom():
    """The kegs' blast frames as drawn (league_gangplank_big), each with its duration."""
    anims = json.load(open(BIG + "#anim.fanim", encoding="utf-8"))["anims"]
    sheet = np.asarray(Image.open(BIG + "#sheet.png").convert("RGBA"))
    out = []
    for fr in anims["e_boom"]["frames"]:
        d = fr["data"]
        x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
        out.append((sheet[y:y + h, x:x + w].copy(), round(fr["duration"] * 1000)))
    return out


def shockwave(a, i, half):
    """The mega-cannonball's gold shockwave, i frames after it lands: its far side under the blast, its near side over."""
    wr, wa = [(8, 255), (17, 255), (24, 230), (29, 170), (32, 110), (34, 50), (0, 0)][min(i, 6)]
    if wr:
        ring(a, wr, wr * FLAT, GOLD[2], wa, half=half)
        ring(a, wr - 1, (wr - 1) * FLAT, GOLD[1], wa * 3 // 4, half=half)
        if wr > 12:
            ring(a, wr - 3, (wr - 3) * FLAT, GOLD[4], wa // 2, dashes=10, phase=i * 0.5, half=half)


def dd_boom():
    src = e_boom()
    half_w = max(DD_R + 9, max(f.shape[1] // 2 for f, _ in src))
    half_h = max(f.shape[0] // 2 for f, _ in src)
    flash = [(11, 210), (17, 130), (12, 60)]
    out = []
    for i, (f, ms) in enumerate(src):
        a = canvas(half_w, half_h)
        if i < len(flash):
            fr, fa = flash[i]
            blob(a, fr, fr * FLAT * 1.2, GOLD[1], fa)
            blob(a, fr * 0.55, fr * 0.55 * FLAT * 1.2, GOLD[0], fa)
        shockwave(a, i, "back")
        h, w = f.shape[:2]
        top, left = a.shape[0] // 2 - h // 2, a.shape[1] // 2 - w // 2
        part = a[top:top + h, left:left + w]
        for yy, xx in zip(*np.nonzero(f[..., 3])):
            px = f[yy, xx]
            put(part, xx - w // 2, yy - h // 2, tuple(int(c) for c in px[:3]), int(px[3]))
        shockwave(a, i, "front")
        out.append((a, ms))
    return out


def rm():
    out = []
    rx, ry = 10, 3
    for i in range(4):
        a = canvas(rx + 2, FEET + ry + 2)
        ring(a, rx, ry, GOLD[3], 200, cy=FEET)
        ring(a, rx, ry, GOLD[1], 255, dashes=6, phase=i * 0.5, cy=FEET)
        for k in range(3):
            th = 2 * math.pi * (k / 3 + i / 12)
            x, y = rx * math.cos(th), FEET + ry * math.sin(th)
            put(a, x, y - 1 - i, GOLD[1], 255 - 50 * i)
            put(a, x, y - i, GOLD[3], 180 - 40 * i)
        out.append((a, 120))
    return out


def coin_face():
    """The serpent coin, 9 x 9: silver, an S of a serpent, lit from the upper left."""
    face = np.zeros((9, 9, 4), np.uint8)
    s = ["  ###  ", " #     ", "  ##   ", "    #  ", " ###   "]
    for y in range(9):
        for x in range(9):
            dx, dy = x - 4, y - 4
            d = math.hypot(dx, dy)
            if d > 4.4:
                continue
            if d > 3.5:
                c = SILVER[5]
            else:
                lit = (-dx - dy) / 5.0
                c = SILVER[1] if lit > 0.35 else SILVER[2] if lit > -0.25 else SILVER[3]
                if (dx, dy) in ((-2, -2), (-1, -3)):
                    c = SILVER[0]
            face[y, x] = (*c, 255)
    for y, row in enumerate(s):
        for x, ch in enumerate(row):
            if ch == "#":
                face[2 + y, 1 + x] = (*SILVER[4], 255)
    return face


def coin():
    face = coin_face()
    widths = [9, 7, 3, 7, 9, 7, 3, 7]
    fades = [255, 255, 255, 255, 255, 255, 170, 85]
    out = []
    for i, (w, al) in enumerate(zip(widths, fades)):
        t = (i + 0.5) / len(widths)
        y = -(COIN_Y[0] + (COIN_Y[1] - COIN_Y[0]) * (1 - (1 - t) ** 2))
        a = canvas(6, COIN_Y[1] + 6)
        cols = [int(round((k + 0.5) * 9 / w - 0.5)) for k in range(w)]
        for k, cx in enumerate(cols):
            for yy in range(9):
                px = face[yy, cx]
                if px[3]:
                    c = tuple(int(v) for v in px[:3]) if w > 3 or k == w // 2 else SILVER[3]
                    put(a, k - w // 2, round(y) + yy - 4, c, al * int(px[3]) // 255)
        if i in (1, 2):
            sx, sy = 5, round(y) - 4
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                put(a, sx + dx - 1, sy + dy, GOLD[0] if (dx, dy) == (0, 0) else SILVER[1], 255 if i == 1 else 160)
        out.append((a, 60))
    return out


def tags():
    return {"r_dd_warn": dd_warn(), "r_dd_fall": dd_fall(), "r_dd_boom": dd_boom(), "r_rm": rm(), "sv_coin": coin()}


def dense(t):
    """the sheet as written: these 1x tags, each with its hd_ twin (PPU 2) redrawn twice finer by fx_vector.redraw_tag (the
    effects' hand redraws; the user, 2026-11-14: 「还有哪些技能没高清化的也高清化一下」), and the idle / hd_idle pair
    league.dll's PPU lookup reads (densify_fx's way: the first tag's first frame), so fx_ppu_table.py lists the sheet"""
    hd = {k: V.redraw_tag([a for a, _ in fr], P=2) for k, fr in t.items()}
    first = next(iter(t))
    out = {"idle": [(t[first][0][0], 100)], "hd_idle": [(hd[first][0], 100)]}
    out.update(t)
    for k, fr in t.items():
        out["hd_" + k] = [(d, ms) for d, (_, ms) in zip(hd[k], fr)]
    return out


# ------------------------------------------------------------------------------------------------------------ preview
STRIP_MS = (80, 480, 680, 840, 920, 1040)


def preview(path, t, strip=False):
    """A mock barrage at x3: Gangplank plunders (the coin), an ally in it gets Raise Morale, the mega-cannonball's mark,
    fall and blast; then the coin again on its own. strip: STRIP_MS side by side in a PNG instead of the GIF."""
    S, W, H = 3, 170, 150
    champ = os.path.join(ROOT, "league", "champions")
    fig = {}
    for hero in ("league_gangplank", "league_garen"):
        an = json.load(open(os.path.join(champ, hero + "#anim.fanim"), encoding="utf-8"))["anims"]
        sh = Image.open(os.path.join(champ, hero + "#sheet.png")).convert("RGBA")
        d = an["idle"]["frames"][0]["data"]
        fig[hero] = sh.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"])))
    gp, ally, mid = (32, 118), (118, 112), (96, 112)

    def at(tag, ms):
        frames, acc = t[tag], 0
        if ms < 0:
            return None
        for a, d in frames:
            if ms < acc + d:
                return Image.fromarray(a)
            acc += d
        return None

    def loop(tag, ms):
        total = sum(d for _, d in t[tag])
        return at(tag, ms % total)

    def stamp(img, pic, pos):
        if pic is not None:
            img.alpha_composite(pic, (pos[0] - pic.width // 2, pos[1] - pic.height // 2))

    def scene(ms):
        img = Image.new("RGBA", (W, H), (58, 84, 52, 255))
        stamp(img, at("r_dd_warn", ms - 300), mid)                      # z -2
        stamp(img, loop("r_rm", ms), ally)                              # z -1
        stamp(img, fig["league_garen"], ally)
        stamp(img, fig["league_gangplank"], gp)
        stamp(img, at("r_dd_fall", ms - 300), mid)                      # z 2
        stamp(img, at("r_dd_boom", ms - 800), mid)
        stamp(img, at("sv_coin", ms) or at("sv_coin", ms - 1100), gp)   # z 3
        return img.resize((W * S, H * S), Image.NEAREST)

    if strip:
        out = Image.new("RGB", (W * S * 3, H * S * 2))
        for k, ms in enumerate(STRIP_MS):
            out.paste(scene(ms).convert("RGB"), ((k % 3) * W * S, (k // 3) * H * S))
        out.save(path)
        print("wrote", path, "at", ", ".join(f"{ms} ms" for ms in STRIP_MS))
        return
    frames = [scene(ms).convert("P", palette=Image.ADAPTIVE) for ms in range(0, 1700, 40)]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=40, loop=0, disposal=2)
    print("wrote", path, len(frames), "frames")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview")
    ap.add_argument("--strip")
    a = ap.parse_args()
    t = tags()
    if a.preview or a.strip:
        preview(a.preview or a.strip, t, strip=bool(a.strip))
        return
    t = dense(t)
    if a.check:
        anims = json.load(open(OUT + "#anim.fanim", encoding="utf-8"))["anims"]
        sheet = np.asarray(Image.open(OUT + "#sheet.png").convert("RGBA"))
        if sorted(anims) != sorted(t):
            sys.exit(f"tags {sorted(anims)}, want {sorted(t)}: python tools/art/gangplank_sv_fx.py")
        for name, frames in t.items():
            got = anims[name]["frames"]
            if len(got) != len(frames):
                sys.exit(f"{name}: {len(got)} frames, want {len(frames)}: python tools/art/gangplank_sv_fx.py")
            for g, (arr, ms) in zip(got, frames):
                d = g["data"]
                x, y, w, h = int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"])
                if not np.array_equal(sheet[y:y + h, x:x + w], arr) or abs(g["duration"] * 1000 - ms) > 0.5:
                    sys.exit(f"{name}: the sheet is not this script's drawing: python tools/art/gangplank_sv_fx.py")
        print("league_gangplank_sv: up to date")
        return
    import strips
    w, h = strips.write_sheet(OUT, t, share=True)
    print(f"wrote {os.path.relpath(OUT, ROOT)}#sheet.png ({w}x{h}), tags {', '.join(f'{k}:{len(v)}' for k, v in t.items())}")


if __name__ == "__main__":
    main()
