#!/usr/bin/env python3
"""The main pack's dense (PPU) frames in the preview clips, drawn as the battlefield draws them (addons/league_main: a
hero listed in hd.rs HEROES is drawn from its hd_<tag> frames, PPU sheet pixels a game pixel, at its SIZES size).

dense() gives a hero's hd_ frames scaled for a clip at zoom z (z x size / PPU of their sheet size: NEAREST from 1 up,
BOX below - Ashe's 5.46 sheet pixels a game pixel at z 3); put() draws a frame on such a clip: a dense frame centred
where its 1x frame's centre is, any other frame z times its size where drawing it at 1x and scaling the whole clip by
z put it (so a clip drawn at z with put() matches the old 1x-then-scaled one everywhere but the dense hero).
"""
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402
from preview_garen import frames_of  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))


def _sizes():
    """addons/league_main/src/hd.rs SIZES -> {hero: size} (league_gragas 0.80 -> gragas 0.8)."""
    with open(os.path.join(ROOT, "addons", "league_main", "src", "hd.rs"), encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"pub const SIZES[^=]*=\s*&\[(.*?)\];", src, re.S)
    return {h: float(v) for h, v in re.findall(r'\("(?:league|tft)_(\w+)",\s*([0-9.]+)\)', m.group(1))} if m else {}


SIZES = _sizes()


def dense(sp, tag, hero, z):
    """`hero`'s hd_<tag> frames for a clip at zoom z: [(frame, ms)], each z x size / PPU of its sheet size, with
    info["one"] = its 1x frame's (w, h) for put()."""
    k = z * SIZES.get(hero, 1.0) / P.PPU[hero]
    out = []
    for (a, _), (b, ms) in zip(frames_of(sp, tag), frames_of(sp, P.PREFIX + tag)):
        f = b.resize((max(1, round(b.width * k)), max(1, round(b.height * k))),
                     Image.NEAREST if k >= 1 else Image.BOX)
        f.info["one"] = (a.width, a.height)
        out.append((f, ms))
    return out


def put(img, f, px, py, z):
    """f on img, a clip at zoom z, at game pixel (px, py): a dense() frame centred where its 1x frame's centre is, any
    other frame z times its size with its top-left on (px - w // 2, py - h // 2) x z."""
    if "one" in f.info:
        w, h = f.info["one"]
        img.alpha_composite(f, (round((px - w // 2) * z + (w * z - f.width) / 2),
                                round((py - h // 2) * z + (h * z - f.height) / 2)))
    else:
        img.alpha_composite(f.resize((f.width * z, f.height * z), Image.NEAREST),
                            ((px - f.width // 2) * z, (py - f.height // 2) * z))


def dense_rows(sp):
    """contact() rows for a dense hero's frame sheet: its hd_ tags (league_zeri_frames.png's way, drawn at z 1)."""
    return [(sp, t["name"], t["name"]) for t in sp.tags if t["name"].startswith(P.PREFIX)]
