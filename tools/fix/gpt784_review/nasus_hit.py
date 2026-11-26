"""league_nasus's hit, both forms: frame 0 was Codex/GPT's cast picture (n_cast 7: the staff planted upright) and frame 1
the stance (n_hit 8: the staff held across him), so the staff jumped from upright to across inside a 0.2 s flinch, and
from the idle's across to upright going in. Frame 0 is now the braced guard his attack already plays (attack[4] /
b_attack[4]: n_hit 7, the staff across, the body pulled back): the same rects (1x, hd_, lo_), no pixel drawn; the hd
strips (assets/source/ppu[/orig]/nasus_[b_]hit.png + .json sizes) rewritten from the new hd_ frames. Since
nasus_actions.py the attack plays other pictures: the guard's rects are its table's "hit0" (what attack[4] was).

    python tools/fix/gpt784_review/nasus_hit.py [--check]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
STEM = os.path.join(ROOT, "league", "champions", "league_nasus")
PPU_DIR = os.path.join(ROOT, "assets", "source", "ppu")


def main():
    check = "--check" in sys.argv
    raw = open(STEM + "#anim.fanim", "rb").read().decode("utf-8-sig")
    doc = json.loads(raw)
    an = doc["anims"]
    sheet = np.asarray(Image.open(STEM + "#sheet.png").convert("RGBA"))
    bad = 0
    guard = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nasus_actions.json"),
                           encoding="utf-8"))["hit0"]
    for form in ("", "b_"):
        for pre, key in (("", "1x"), ("hd_", "hd_"), ("lo_", "lo_")):
            hit = an[f"{pre}{form}hit"]["frames"]
            want = {k: float(v) for k, v in zip(("x", "y", "w", "h"), guard[form][key])}
            if hit[0]["data"] != want:
                bad += 1
                hit[0]["data"] = want
        # the strips: the hit's hd_ frames as the sheet now holds them
        pics = []
        for f in an[f"hd_{form}hit"]["frames"]:
            d = f["data"]
            x, y, w, h = (int(round(d[k])) for k in ("x", "y", "w", "h"))
            pics.append(sheet[y:y + h, x:x + w])
        H = max(p.shape[0] for p in pics)
        W = sum(p.shape[1] for p in pics) + len(pics) - 1
        st = np.zeros((H, W, 4), np.uint8)
        x = 0
        for p in pics:
            st[:p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1] + 1
        for sub in ("", "orig"):
            png = os.path.join(PPU_DIR, sub, f"nasus_{form}hit.png")
            js = os.path.join(PPU_DIR, sub, f"nasus_{form}hit.json")
            meta = json.load(open(js))
            sizes = [[p.shape[1], p.shape[0]] for p in pics]
            same = meta.get("sizes") == sizes and np.array_equal(np.asarray(Image.open(png).convert("RGBA")), st)
            if not same:
                bad += 1
                if not check:
                    meta["sizes"] = sizes
                    Image.fromarray(st).save(png)
                    json.dump(meta, open(js, "w"))
    if check:
        print("nasus hit: OK" if not bad else f"nasus hit: {bad} parts not as this tool leaves them")
        sys.exit(1 if bad else 0)
    open(STEM + "#anim.fanim", "wb").write(json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    print(f"nasus hit: {bad} parts written")


if __name__ == "__main__":
    main()
