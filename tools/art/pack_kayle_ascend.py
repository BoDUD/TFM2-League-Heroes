#!/usr/bin/env python3
"""Build kayle_ascend_pack.zip: Kayle's ascension pictures for Codex - the wings that grow at her stages (levels 5 / 8 /
12) and the transcendent versions of her effects at level 12 (the user, 2026-10-08: 「天使可不可以在到达特定的等级变身呢？
还有特效强化」, then 「做第一种吧」: the data-only way - idle, run, hit and death are picked by the engine, so the change shows
as wing pictures riding on her, and as stronger effect pictures).

    python tools/art/pack_kayle_ascend.py [--out dist/kayle_packs]

The pack (zipped next to its folder): PROMPTS.md (also written to assets/source/kayle/PROMPTS_ASCEND.md),
design/kayle_idle.png (her idle at 8x on the arena colour, the pivot marked), design/kayle_size.png (4x with a 10-px
ruler and the base fighter), now/league_kayle_effects.png (her effects as they are in the game: the base versions the
level-12 ones upgrade), refs/lol_kayle_wings.png (League's Kayle with one and with three wing pairs: Riot's render, local
only), refs/lol_fx_ref.png (League's particle textures for her wings, fire and swords; local only).
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ky_work")
DOC = os.path.join(ROOT, "assets", "source", "kayle", "PROMPTS_ASCEND.md")
ARENA = (104, 112, 72, 255)
REFS = ["Kayle_Base_Wing_Fire_Gradient", "Kayle_Base_Flame_Ring_Gold", "Kayle_Base_Fire_tile_Gold", "Kayle_Base_Light",
        "Kayle_Base_R_SkyBeam", "Kayle_Base_R_Glow_sword", "Kayle_Q_Mis_SharpHead", "Kayle_Base_E_beam_mis",
        "Kayle_Base_BA_Flare_Yellow", "Kayle_Base_Q_Flare", "Kayle_BeamswordShapes_Orange", "Kayle_Base_Radial_LensFlare"]


def idle_frame():
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_kayle"))
    f = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    return f, (f.shape[1] // 2, f.shape[0] // 2)       # the frames are centred on her pivot


def design(out):
    f, (px, py) = idle_frame()
    ys, xs = np.nonzero(f[..., 3] > 0)
    x0, x1, y0, y1 = xs.min() - 12, xs.max() + 13, ys.min() - 10, ys.max() + 4
    c = f[y0:y1, x0:x1]
    z = 8
    img = Image.new("RGBA", (c.shape[1] * z, c.shape[0] * z), ARENA)
    img.alpha_composite(Image.fromarray(np.ascontiguousarray(c)).resize((c.shape[1] * z, c.shape[0] * z), Image.NEAREST))
    d = ImageDraw.Draw(img)
    cx, cy = (px - x0) * z + z // 2, (py - y0) * z + z // 2
    d.line([(cx - 30, cy), (cx + 30, cy)], fill=(0, 220, 255, 255), width=3)
    d.line([(cx, cy - 30), (cx, cy + 30)], fill=(0, 220, 255, 255), width=3)
    img.convert("RGB").save(os.path.join(out, "design", "kayle_idle.png"))
    return (int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)), (int(px - xs.min()), int(ys.max() - py))


def size_sheet(out):
    f, _ = idle_frame()
    ys, xs = np.nonzero(f[..., 3] > 0)
    fig = f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    base = pad + max(fig.shape[0], kn.shape[0])
    img = Image.new("RGBA", (max(W * Z, 420), (base + 4) * Z + 64), ARENA)
    img.alpha_composite(Image.fromarray(fig).resize((fig.shape[1] * Z, fig.shape[0] * Z), Image.NEAREST),
                        (pad * Z, (base - fig.shape[0]) * Z + 64))
    img.alpha_composite(Image.fromarray(kn).resize((kn.shape[1] * Z, kn.shape[0] * Z), Image.NEAREST),
                        ((2 * pad + fig.shape[1]) * Z, (base - kn.shape[0]) * Z + 64))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fig.shape[1] + 1, 10):
        x = (pad + i) * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"凯尔 {fig.shape[1]}×{fig.shape[0]} 格（连头后的小翅膀），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(os.path.join(out, "design", "kayle_size.png"))


def refs(out):
    wings = os.path.join(TMP, "pose", "wings_cmp.png")
    if os.path.exists(wings):
        shutil.copyfile(wings, os.path.join(out, "refs", "lol_kayle_wings.png"))
    S = 180
    tiles = [n for n in REFS if os.path.exists(os.path.join(TMP, "fxref", n + ".png"))]
    sheet = Image.new("RGBA", (6 * S, -(-len(tiles) // 6) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for i, n in enumerate(tiles):
        im = Image.open(os.path.join(TMP, "fxref", n + ".png")).convert("RGBA")
        im.thumbnail((S - 12, S - 22))
        x, y = (i % 6) * S, (i // 6) * (S + 16)
        sheet.alpha_composite(im, (x + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
        d.text((x + 4, y + 2), n.replace("Kayle_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(os.path.join(out, "refs", "lol_fx_ref.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "kayle_packs"))
    a = ap.parse_args()
    pack = os.path.join(a.out, "kayle_ascend_pack")
    if os.path.exists(pack):
        shutil.rmtree(pack)
    for sub in ("design", "now", "refs"):
        os.makedirs(os.path.join(pack, sub))
    size, (half, soles) = design(pack)
    size_sheet(pack)
    shutil.copyfile(os.path.join(ROOT, "docs", "preview", "league_kayle_effects.png"),
                    os.path.join(pack, "now", "league_kayle_effects.png"))
    refs(pack)
    shutil.copyfile(DOC, os.path.join(pack, "PROMPTS.md"))
    zp = shutil.make_archive(pack, "zip", pack)
    print("written", zp, "figure", size, "pivot from left", half, "soles under pivot", soles)


if __name__ == "__main__":
    main()
