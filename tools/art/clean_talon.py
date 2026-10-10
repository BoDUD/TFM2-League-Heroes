#!/usr/bin/env python3
"""Talon's clean-up after import_native.py's SHRINK (TIDY "clean_talon", step tidy_shrunk): a removed row or column
can run through a slanted outline and leave its corner open, or close a gap into a 1-2 px hole. Every frame gets the
same finish as fix_talon_strips.finish's last steps: every light edge outlined (close_all) and every enclosed hole /
1-px-open pocket filled (fill_holes; the run keeps its leg gaps)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fix_talon_strips as F  # noqa: E402

SOLES = 11          # the soles' row under the pivot (the frame is centred on the pivot)


def tidy_shrunk(tag, k, frame):
    a = frame.copy()
    if not a[..., 3].any():
        return a
    sole = a.shape[0] // 2 + SOLES
    a = F.close_all(a, sole)
    for _ in range(4):
        b = F.fill_holes(a, run=tag == "run", pocket_max=0 if tag == "run" else 40)
        if (b == a).all():
            break
        a = b
    return a
