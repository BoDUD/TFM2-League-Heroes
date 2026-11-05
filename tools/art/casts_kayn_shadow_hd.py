#!/usr/bin/env python3
"""Kayn's Shadow form (his sheet's sh_ tags) read back from Codex's whole-frame redraw:
tools/art/casts_kayn_hd.py on assets/source/kayn_shadow/hd/casts (pack_kayn_shadow_actions.py's pack).

    python tools/art/casts_kayn_shadow_hd.py --fits C:/t/kayn_shadow_actions/templates
    python tools/art/casts_kayn_shadow_hd.py --review DIR
    python tools/art/casts_kayn_shadow_hd.py --heads
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import casts_kayn_hd as K  # noqa: E402

if __name__ == "__main__":
    K.main("kayn_shadow")
