#!/usr/bin/env python3
"""Kayn's Darkin form (his sheet's rh_ tags) read back from Codex's whole-frame redraw:
tools/art/casts_kayn_hd.py on assets/source/kayn_darkin/hd/casts (pack_kayn_darkin_actions.py's pack).

    python tools/art/casts_kayn_darkin_hd.py --fits C:/t/kayn_darkin_actions/templates
    python tools/art/casts_kayn_darkin_hd.py --review DIR
    python tools/art/casts_kayn_darkin_hd.py --heads
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import casts_kayn_hd as K  # noqa: E402

if __name__ == "__main__":
    K.main("kayn_darkin")
