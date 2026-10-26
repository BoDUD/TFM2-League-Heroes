r"""Silco's own particle textures (TFT set 13) and his monstrosity for the effects pack's reference sheet (Riot's art:
kept local, never committed).

    python tools/lol/fx_ref_silco.py [--out C:/t/sc_work/fxref] [--lol "D:/Riot Games/League of Legends"]

Read from the Riot client's TFTSet13.wad.client: every .tex path his skin bin (data/characters/tft13_silco/skins/
skin0.bin, which also holds his particle systems) and his monstrosity's (TFT13_Silco_Monstrosity, the little horror his
canister lets out) name. Each is written as <out>/<file stem>.png on black where it has alpha, so the grey shapes read.
The monstrosity's own model is rendered too (<out>/monstrosity_<yaw>.png, its idle clip's first frame, textured with its
skin's map when the WAD holds one).
"""
import argparse
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

BINS = ("data/characters/tft13_silco/skins/skin0.bin", "data/characters/tft13_silco_monstrosity/skins/skin0.bin")
MON = "assets/characters/tft13_silco_monstrosity/skins/base/tft13_silco_monstrosity_base"
MON_TEX = ("assets/characters/tft13_silco_monstrosity/skins/base/tft13_silco_monstrosity_base_tx_cm.tex",
           "assets/characters/tft13_silco_monstrosity/skins/base/tft13_silco_monstrosity_tx_cm.tex")
MON_IDLE = 5517890294354197059   # 1.33 s, its first clip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/sc_work/fxref")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "TFTSet13.wad.client"))
    paths = set()
    for b in BINS:
        try:
            blob = w.read_path(b)
        except KeyError:
            print("no", b)
            continue
        paths |= {m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.tex", blob)}
    n = 0
    for p in sorted(paths):
        try:
            im = pose_ref.read_tex(w.read_path(p.lower())).convert("RGBA")
        except Exception as e:   # textures another WAD holds (TFTCommon)
            print("skip", p, type(e).__name__)
            continue
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.out, os.path.splitext(os.path.basename(p))[0].lower() + ".png"))
        n += 1
    print(n, "textures ->", a.out)
    monstrosity(w, a.out)


def monstrosity(w, out):
    """The monstrosity's model, posed by its first clip, at three angles on grey."""
    import numpy as np
    skn = w.read_path(MON + ".skn")
    tris, v = pose_ref.read_skn(skn)
    tex = next((pose_ref.read_tex(w.read_path(p)) for p in MON_TEX if w.has(p)), None)
    joints, infl = pose_ref.read_skl(w.read_path(MON + ".skl"))
    bind = pose_ref.globals_(joints, [pose_ref.trs(j["t"], j["r"], j["s"]) for j in joints])
    binv = [np.linalg.inv(m) for m in bind]
    anim = pose_ref.read_anim(w.read(MON_IDLE))
    glob = pose_ref.globals_(joints, [pose_ref.trs(*p) for p in pose_ref.local_pose(joints, anim, 0.0)])
    pv = pose_ref.skin(v, infl, binv, glob).copy()
    pv[:, 1] -= pv[:, 1].min()
    h = max(pv[:, 1].max(), 1e-3)
    for yaw in (35, 90, 0):
        im = pose_ref.render_hq(pv, tris, v["uv"], tex, -yaw, 20, (800, 800), 800 * 0.5 / h, 700)
        bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
        bg.alpha_composite(im.transpose(Image.FLIP_LEFT_RIGHT))
        bg.crop(bg.getbbox()).convert("RGB").save(os.path.join(out, f"monstrosity_{yaw}.png"))
    print("monstrosity rendered", "textured" if tex is not None else "untextured")


if __name__ == "__main__":
    main()
