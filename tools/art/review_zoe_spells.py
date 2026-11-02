#!/usr/bin/env python3
"""Zoe's stolen summoner spells as the game shows them (tools/art/draw_zoe_spells.py's league_zoe_spells, the add-on
league_zoe playing them), in ONE GIF for the user's review: every spell cast as her W goes off beside Darius, then a
spell shard lying on the ground cycling its icons until she runs over it.

    python tools/art/review_zoe_spells.py --out DIR [--z 6]

Everything at its battlefield density: her hd_ frames (PPU 1.5), Darius's (1.45), the spells' (2), the shard's crystal
(league_zoe_fx, 1x), the icons' (3). Writes DIR/zoe_spells.gif.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import draw_zoe_spells as S  # noqa: E402

PRE = chr(92) * 2 + "?" + chr(92)
LEAGUE = os.path.join(ROOT, "league")
ARENA = (92, 98, 86)
FEET = 11.5                                  # a unit's soles under its position (game px)
STEP = 40
NAMES = {"flash": "闪现", "ignite": "点燃", "exhaust": "虚弱", "heal": "治疗", "barrier": "屏障", "ghost": "幽灵疾步",
         "cleanse": "净化"}


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


class Sheet:
    def __init__(self, stem, ppu):
        self.an = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
        self.img = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
        self.ppu = ppu
        self.cache = {}

    def frames(self, tag):
        if tag not in self.cache:
            out = []
            for f in self.an[tag]["frames"]:
                d = f["data"]
                x, y, w, h = (int(round(d[k])) for k in ("x", "y", "w", "h"))
                out.append((self.img.crop((x, y, x + w, y + h)), f["duration"] * 1000))
            self.cache[tag] = out
        return self.cache[tag]

    def at(self, tag, t, loop=False):
        fr = self.frames(tag)
        total = sum(ms for _, ms in fr)
        if t < 0 or (t >= total and not loop):
            return None
        t = t % total
        for im, ms in fr:
            if t < ms:
                return im
            t -= ms
        return fr[-1][0]


class Shot:
    """A picture (sheet, tag) from `start`, at a spot or following a unit; `until`: looped till then."""

    def __init__(self, sheet, tag, start, spot, until=None, layer=1, mirror=False):
        self.s, self.tag, self.start, self.spot, self.until, self.layer, self.mirror = sheet, tag, start, spot, until, layer, mirror

    def frame(self, t):
        if self.until is not None:
            if not self.start <= t < self.until:
                return None
            return self.s.at(self.tag, t - self.start, loop=True)
        return self.s.at(self.tag, t - self.start)


def put(img, im, ppu, x, y, z, mirror=False):
    """`im` centred on the game point (x, y), its squares ppu a game px."""
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    k = z / ppu
    big = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)
    img.alpha_composite(big, (round(x * z - big.width / 2), round(y * z - big.height / 2)))


def scene(z, zoe, dar, fx, sp, ic, spell, font):
    """One cast: her W, the spell; Darius across. Returns the frames."""
    W, H, gy = 150, 70, 60
    zx, dx0 = (85, 130) if spell == "flash" else (45, 105)     # Flash: room behind her for the blink
    shots = [Shot(ic, "sg_" + spell, 0, ("at", zx, gy - FEET), layer=-1)]
    blink = 45 if spell == "flash" else 0       # Flash: summon::FLASH_D 45000 back from the one on her (1000 a game px)
    if spell == "flash":
        # a starburst where she was and where she lands, the streak's puffs between them, the icon at both ends
        shots += [Shot(sp, "s_flash", 0, ("at", zx, gy - FEET)), Shot(sp, "s_flash", 0, ("at", zx - blink, gy - FEET)),
                  Shot(ic, "sg_flash", 0, ("at", zx - blink, gy - FEET), layer=-1)]
        shots += [Shot(sp, "s_flash_trail", 0, ("at", zx - blink * k / 5, gy - FEET)) for k in range(1, 5)]
    elif spell == "ignite":
        shots.append(Shot(sp, "s_ignite", 0, ("him",), until=1700))
    elif spell == "exhaust":
        shots.append(Shot(sp, "s_exhaust", 0, ("him",), until=1700))
    elif spell == "heal":
        shots.append(Shot(sp, "s_heal", 0, ("me",), until=1700))
    elif spell == "barrier":
        shots.append(Shot(sp, "s_barrier", 0, ("me",), until=1700))
    elif spell == "ghost":
        shots.append(Shot(sp, "s_ghost", 0, ("me",), until=1700, layer=-1))
    elif spell == "cleanse":
        shots.append(Shot(sp, "s_cleanse", 0, ("me",)))
    w_ms = sum(ms for _, ms in zoe.frames("hd_skill_w"))
    frames = []
    t = -400
    while t < 1700:
        img = Image.new("RGBA", (W * z, H * z), (*ARENA, 255))
        me_x = zx + (max(0, t - w_ms) * 0.03 if spell == "ghost" else 0) - (blink if t >= 0 else 0)
        him_x = dx0
        pos = {"me": (me_x, gy - FEET), "him": (him_x, gy - FEET)}

        def spot(s):
            return (s.spot[1], s.spot[2]) if s.spot[0] == "at" else pos[s.spot[0]]

        for s in shots:
            if s.layer < 0 and (f := s.frame(t)) is not None:
                put(img, f, s.s.ppu, *spot(s), z)
        if 0 <= t < w_ms:
            body = zoe.at("hd_skill_w", t)
        elif spell == "ghost" and t >= w_ms:
            body = zoe.at("hd_run", t - w_ms, loop=True)
        else:
            body = zoe.at("hd_idle_base", t % 800, loop=True)
        put(img, dar.at("hd_idle", t % 800 if t >= 0 else 0, loop=True), dar.ppu, *pos["him"], z, mirror=True)
        put(img, body, zoe.ppu, *pos["me"], z)
        for s in shots:
            if s.layer >= 0 and (f := s.frame(t)) is not None:
                put(img, f, s.s.ppu, *spot(s), z)
        d = ImageDraw.Draw(img)
        d.text((14, 8), f"窃法巧手 → {NAMES[spell]}", fill=(255, 240, 160), font=font)
        frames.append(img.convert("RGB"))
        t += STEP
    return frames


def shard_scene(z, zoe, fx, sp, ic, font):
    """A shard lying on the ground, its icon cycling every stamp (15 ticks); she runs over it and casts Heal."""
    W, H, gy = 150, 70, 60
    at = (95, gy - FEET)
    stamp = S.SHOW_MS
    frames = []
    t = 0
    pick = 2600
    while t < pick + 1200:
        img = Image.new("RGBA", (W * z, H * z), (*ARENA, 255))
        run_from = 1600
        me_x = 20 + max(0, min(t, pick) - run_from) * 0.075
        if t < pick:
            k = int(t // stamp)
            put(img, fx.at("w_shard", t - k * stamp), 1, *at, z)
            put(img, ic.at("ss_" + S.SPELLS[k % 7], t - k * stamp), ic.ppu, *at, z)
        else:
            if (f := ic.at("sg_heal", t - pick)) is not None:
                put(img, f, ic.ppu, me_x, gy - FEET, z)
        if run_from <= t < pick:
            body = zoe.at("hd_run", t - run_from, loop=True)
        elif pick <= t < pick + 317:
            body = zoe.at("hd_skill_w", t - pick)
        else:
            body = zoe.at("hd_idle_base", t % 800, loop=True)
        put(img, body, zoe.ppu, me_x, gy - FEET, z)
        if pick <= t < pick + 1000 and (f := sp.at("s_heal", t - pick, loop=True)) is not None:
            put(img, f, 2, me_x, gy - FEET, z)
        d = ImageDraw.Draw(img)
        d.text((14, 8), "地上的法术碎片：图标轮流闪，捡起来才定是哪个", fill=(255, 240, 160), font=font)
        frames.append(img.convert("RGB"))
        t += STEP
    return frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=int, default=6)
    ap.add_argument("--only")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
    zoe = Sheet(os.path.join(LEAGUE, "champions", "league_zoe"), 1.5)
    dar = Sheet(os.path.join(LEAGUE, "champions", "league_darius"), 1.45)
    fx = Sheet(os.path.join(LEAGUE, "effects", "league_zoe_fx"), 1)
    sp = Sheet(os.path.join(LEAGUE, "effects", "league_zoe_spells"), 2)
    ic = Sheet(os.path.join(LEAGUE, "effects", "league_zoe_spell_icons"), 3)
    for x in (sp, ic):              # the dense frames, as the battlefield draws them
        x.frames = (lambda f: lambda tag: f(tag if tag.startswith("hd_") else "hd_" + tag))(x.frames)
    frames = []
    for spell in (a.only.split(",") if a.only else S.SPELLS):
        frames += scene(a.z, zoe, dar, fx, sp, ic, spell, font)
    if not a.only:
        frames += shard_scene(a.z, zoe, fx, sp, ic, font)
    pal = [f.quantize(255, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(a.out, "zoe_spells.gif")
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=STEP, loop=0)
    print(path, len(frames), "frames")


if __name__ == "__main__":
    main()
