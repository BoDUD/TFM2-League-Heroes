"""Skin-swap packs for Codex (2026-10-18): every action of a hero as Codex's skin swap over an oppi hero's sheet
(the way Akshan's and Swain's walks were accepted, memory swain-session):

- akshan_actions: the picked slim design (assets/source/akshan/hd/slim2.png, 61 rows hair to soles) over oppi's Lucian
  (a long-coated gunslinger): idle, run, attack, skill1 (Q throw), skill2 (E dash), ult (R volley), hit, dead.
- wukong_actions: the picked new design (assets/source/wukong/hd/redo2.png, 49 rows hair tuft to soles) over oppi's Jax
  (a hooded fighter with a long pole): idle, run, attack, skill (Q), skill2 (E leap), ult (W), hit, dead.
- gangplank_run2: Gangplank's walk again over oppi's Lucian run (the user: 「没有明显换腿的感觉？」 - oppi's Swain run, the first
  skeleton, barely moves its legs under the coat; every read-back frame had one boot ~20 squares behind the hips and one
  under them).

    python tools/art/pack_swap_1018.py [--only akshan|wukong|gangplank]

Each skeleton sheet: oppi's frames of one tag scaled (nearest) so oppi's idle body matches the design's hair-to-soles rows,
up to 4 a row, soles on one line per row, on #00FF00 at Z x; image 2 the design at the same scale. Writes
ak/dist/redo_packs/<pack>.zip; oppi's frames never go into the repo.
"""
import argparse
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
AK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(AK, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase as T  # noqa: E402

OPPI = "D:/steam/steamapps/workshop/content/3009300/3774304166/champions/{}.aseprite"
SRC = os.path.join(AK, "assets", "source")
DIST = os.path.join(AK, "dist", "redo_packs")
TMP = "C:/t/ak_work/swap"
KEY = (0, 255, 0)
Z = 5
PADC = 6                    # free squares round the widest frame in a cell

PACKS = {
    "akshan": dict(pack="akshan_actions", oppi="lucian", oppi_body=34, design="akshan/hd/slim2.png", rows=61,
                   tags=["idle", "run", "attack", "skill1", "skill2", "ult", "hit", "dead"], prompt="AKSHAN_ACTIONS_PROMPT.md"),
    "wukong": dict(pack="wukong_actions", oppi="jax", oppi_body=33, design="wukong/hd/redo2.png", rows=49,
                   tags=["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"], prompt="WUKONG_ACTIONS_PROMPT.md"),
    "gangplank": dict(pack="gangplank_run2", oppi="lucian", oppi_body=34, design="gangplank/hd/design.png", rows=62,
                      tags=["run"], prompt="GANGPLANK_RUN2_PROMPT.md"),
}


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def on_key(a):
    o = np.zeros(a.shape[:2] + (3,), np.uint8)
    o[:] = KEY
    m = a[..., 3] > 0
    o[m] = a[m][:, :3]
    return o


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def tag_frames(s, name):
    t = s.tag(name)
    return [np.asarray(s.frames[i].convert("RGBA")) for i in range(t["frm"], t["to"] + 1)]


def sheet(frames, k, soles):
    """Frames scaled by k, cut to the tag's union box, up to 4 a row; the soles row of every cell at the same height."""
    allm = np.zeros(frames[0].shape[:2], bool)
    for f in frames:
        allm |= f[..., 3] > 0
    ys, xs = np.nonzero(allm)
    y0, y1, x0, x1 = ys.min(), max(ys.max(), soles), xs.min(), xs.max() + 1
    sc = [np.asarray(Image.fromarray(f[y0:y1 + 1, x0:x1]).resize((round((x1 - x0) * k), round((y1 - y0 + 1) * k)),
                                                                 Image.NEAREST)) for f in frames]
    h, w = sc[0].shape[:2]
    cw, ch = w + 2 * PADC, h + 2 * PADC
    cols = min(4, len(sc))
    rows = (len(sc) + cols - 1) // cols
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for n, f in enumerate(sc):
        Y, X = (n // cols) * ch + PADC, (n % cols) * cw + PADC
        m = f[..., 3] > 0
        out[Y:Y + h, X:X + w][m] = f[m]
    return out, (cw, ch, cols, rows, round((soles - y0 + 1) * k) + PADC)


def build(cfg):
    out = os.path.join(TMP, cfg["pack"])
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    s = T.load_sprite(OPPI.format(cfg["oppi"]))
    soles = int(np.nonzero(tag_frames(s, "idle")[0][..., 3].any(1))[0].max())
    k = cfg["rows"] / cfg["oppi_body"]
    notes = []
    for i, tag in enumerate(cfg["tags"], 1):
        sh, (cw, ch, cols, rows, sy) = sheet(tag_frames(s, tag), k, soles)
        up(on_key(sh)).save(os.path.join(out, f"1_{i}_骨架_{tag}.png"))
        notes.append(f"{tag}: {len(tag_frames(s, tag))} frames, {cols} x {rows}, cell {cw} x {ch} squares ({cw * Z} x {ch * Z} px), "
                     f"soles {sy} squares down a cell")
    d = np.asarray(Image.open(lp(os.path.join(SRC, cfg["design"]))).convert("RGBA"))
    ys, xs = np.nonzero(d[..., 3])
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    cell = np.zeros((d.shape[0] + 2 * PADC, d.shape[1] + 2 * PADC, 4), np.uint8)
    m = d[..., 3] > 0
    cell[PADC:PADC + d.shape[0], PADC:PADC + d.shape[1]][m] = d[m]
    up(on_key(cell)).save(os.path.join(out, "2_角色定稿.png"))
    shutil.copyfile(os.path.join(SRC, "redo_1018", cfg["prompt"]), os.path.join(out, "PROMPT.md"))
    with open(os.path.join(out, "sheets.txt"), "w", encoding="utf-8") as f:
        f.write(f"oppi {cfg['oppi']} x {k:.3f}, {Z} px a square\n" + "\n".join(notes) + "\n")
    os.makedirs(lp(DIST), exist_ok=True)
    zp = os.path.join(DIST, cfg["pack"] + ".zip")
    with zipfile.ZipFile(lp(zp), "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(out)):
            z.write(os.path.join(out, n), cfg["pack"] + "/" + n)
    print(zp, f"scale {k:.3f}")
    print("\n".join(notes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list(PACKS))
    a = ap.parse_args()
    for name, cfg in PACKS.items():
        if not a.only or a.only == name:
            build(cfg)


if __name__ == "__main__":
    main()
