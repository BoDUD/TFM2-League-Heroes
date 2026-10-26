#!/usr/bin/env python3
"""Lee Sin's run (and Tempest's last frame) for Codex again (assets/source/leesin/RUN_REDO_PROMPT.md). Codex's first
delivery (assets/source/leesin/hd/casts, 2026-10-26) drew all 8 run frames as open strides with the same leg in front:
the old run's passing frames (2-3 and 6-7, the legs together under the hips, one passing the other) are gone and the
near leg never leads - played in a loop he limps on one leg (its own HANDOFF says the swap is unclear). And E's last
frame came back a deep crouch where the old frame stands back up in his guard.

    python tools/art/pack_leesin_run_redo.py --out C:/t/ls_redo [--lol D:/WeGameApps/lol]

Writes <out>/ (and <out>.zip): the same templates as the actions pack (run_1-4, skill2_4: the old frame as the pale
figure), legs/run_<k>.png - League's own run frame (Run_Base, the clip the old run was traced from; Riot's, kept local)
with his NEAR leg painted magenta and his FAR leg cyan (tools/lol/native_pose.py --parts, the hips L_Hip / R_Hip as
parts), refs/ (the design, its palette, the old frames in colour) and prev/ (Codex's own first drawing of each sheet:
the look to keep).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import pack_leesin_actions as PA  # noqa: E402
import pack_riven_actions as PR  # noqa: E402

SRC = os.path.join(REPO, "assets", "source", "leesin")
SHEETS = ["run_1", "run_2", "run_3", "run_4", "skill2_4"]
GREY = (225, 225, 225)


def legs(lol, out):
    """League's run frames with the two legs painted apart -> [8 RGBA crops], near leg magenta, far leg cyan."""
    with open(PR.lp(os.path.join(SRC, "poses.json")), encoding="utf-8") as f:
        spec = json.load(f)
    spec["tags"] = {"run": spec["tags"]["run"]}
    spec["parts"] = [{"name": "far_leg", "joints": "^L_Hip$"}, {"name": "near_leg", "joints": "^R_Hip$"}]
    tmp = os.path.join(out, "_render")
    os.makedirs(tmp, exist_ok=True)
    sp = os.path.join(tmp, "poses_run_legs.json")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(spec, f)
    subprocess.run([sys.executable, os.path.join(REPO, "tools", "lol", "native_pose.py"), sp, "--out", tmp,
                    "--lol", lol, "--parts", "--alpha"], check=True, capture_output=True)
    im = Image.open(os.path.join(tmp, "leesin_parts_run.png")).convert("RGBA")
    cw, ch = im.width // 4, im.height // 2
    out_ = []
    for i in range(8):
        t = im.crop(((i % 4) * cw, (i // 4) * ch, (i % 4 + 1) * cw, (i // 4 + 1) * ch))
        out_.append(t.crop(t.getbbox()))
    shutil.rmtree(tmp)
    return out_


def leg_card(pic, k, path):
    """League's frame k at a readable size on grey, with the colours named."""
    z = 560 / pic.height
    big = pic.resize((round(pic.width * z), 560), Image.NEAREST)
    can = Image.new("RGBA", (big.width + 80, 660), GREY + (255,))
    can.alpha_composite(big, (40, 70))
    d = ImageDraw.Draw(can)
    d.text((16, 12), f"run frame {k}: LEGS ONLY - magenta = his NEAR leg, cyan = his FAR leg", fill=(0, 0, 0),
           font=PR.font(20))
    can.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    if os.path.isdir(a.out):
        shutil.rmtree(a.out)
    tpl, refs, prev, lg = (os.path.join(a.out, d) for d in ("templates", "refs", "prev", "legs"))
    for d in (tpl, refs, prev, lg):
        os.makedirs(d)
    old = PA.old_frames(os.path.join(SRC, "hd", "old", "sheet.png"), os.path.join(SRC, "hd", "old", "anim.fanim"))
    with open(PR.lp(os.path.join(SRC, "hd", "casts", "sheets.json")), encoding="utf-8") as f:
        sheets = {s["name"]: s for s in json.load(f)["sheets"]}
    for name in SHEETS:
        s = sheets[name]
        part = [old[s["tag"]][k - 1] for k in s["frames"]]
        PA.template(os.path.join(tpl, name + ".png"), part, s["frames"])
        PA.old_ref(part, s["frames"], os.path.join(refs, f"old_{name}.png"))
        shutil.copyfile(PR.lp(os.path.join(SRC, "hd", "casts", name + ".png")), os.path.join(prev, name + ".png"))
    for k, pic in enumerate(legs(a.lol, a.out), 1):
        leg_card(pic, k, os.path.join(lg, f"run_{k}.png"))
    des = Image.open(PR.lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")
    bg = Image.new("RGBA", (des.width + 4, des.height + 4), GREY + (255,))
    bg.alpha_composite(des, (2, 2))
    bg.convert("RGB").resize((bg.width * 6, bg.height * 6), Image.NEAREST).save(os.path.join(refs, "design.png"))
    import numpy as np
    d = np.asarray(des)
    PR.palette(np.unique(d[d[..., 3] > 0][:, :3], axis=0), os.path.join(refs, "design_palette.png"))
    with open(os.path.join(a.out, "sheets.json"), "w", encoding="utf-8") as f:
        json.dump({"sheets": [sheets[n] for n in SHEETS]}, f, indent=1, ensure_ascii=False)
    shutil.copyfile(PR.lp(os.path.join(SRC, "RUN_REDO_PROMPT.md")), os.path.join(a.out, "RUN_REDO_PROMPT.md"))
    print(shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()
