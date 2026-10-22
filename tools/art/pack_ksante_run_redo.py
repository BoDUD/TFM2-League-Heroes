#!/usr/bin/env python3
"""K'Sante's run redo for Codex (assets/source/ksante/RUN_REDO_PROMPTS.md): three run frames to draw again with the legs
exchanged. Codex's runs (assets/source/ksante/codex_poses, 2026-10-22) never step with the second leg: base run1 and
run3 both plant the same leg forward with the other trailing, All Out run1 / run3 the same, All Out run2 / run4 both
swing the same knee up - played in a cycle he limps on one leg. Each redo is its partner frame drawn again, body, arms
and weapons as they are, the two legs exchanged.

    python tools/art/pack_ksante_run_redo.py [--out C:/t/ks_work/ksante_run_redo_pack]

Writes <out>/ (and <out>.zip): RUN_REDO_PROMPTS.md, for each redo the partner frame (Codex's own, the picture to copy),
its skeleton and League's frame from the pose pack, the stance's design and head.
"""
import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_ksante_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ksante")
PACK = "C:/t/ks_work/ksante_pose_pack"      # pack_ksante_poses.py's output (skeletons, League frames, designs, heads)
# redo -> (partner frame Codex drew, pose pack number of the redo, stance)
REDO = {"run3": ("run1", 18, "base"), "ao_run3": ("ao_run1", 28, "ao"), "ao_run4": ("ao_run2", 29, "ao")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/ks_work/ksante_run_redo_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for st in ("base", "ao"):
        for kind in ("2_design", "1_head", "0_design_skeleton"):
            shutil.copyfile(os.path.join(PACK, f"{kind}_{st}.png"), os.path.join(out, f"{kind}_{st}.png"))
    for redo, (partner, k, st) in REDO.items():
        dash = partner.replace("_", "-")
        shutil.copyfile(lp(os.path.join(SRC, "codex_poses", f"ksante-pose-{dash}.png")),
                        os.path.join(out, f"partner_for_{redo}.png"))
        for kind in ("skeleton", "league"):
            shutil.copyfile(os.path.join(PACK, f"{k}_{redo}_{kind}.png"), os.path.join(out, f"{redo}_{kind}.png"))
    shutil.copyfile(lp(os.path.join(SRC, "RUN_REDO_PROMPTS.md")), os.path.join(out, "RUN_REDO_PROMPTS.md"))
    print(shutil.make_archive(out, "zip", out))


if __name__ == "__main__":
    main()
