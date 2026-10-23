#!/usr/bin/env python3
"""CI: the UI sheets (tools/package_mod.py ui_sheets, league.dll src/ui.rs) - every champion of league/ and tft/ gets
both, pixel for pixel (package_mod checks each UI frame against its source frame and its clear pads), and the screens
that show every hero at once stay well inside the game's 256 MiB image cache. 589 MiB of battle sheets on those screens
made the BP grid and the hero screen decode every frame (2026-10-24, docs/perf.md section 9: 「PPU导致页面卡 特别是英雄界面
还有BP界面非常的卡」).

    python -I tools/ci/ui_sheets.py

Exit 1 when a champion has no UI sheet of a kind or a kind's sheets together pass its limit. Past a limit: drop the lo_
frames the UI no longer reads from the battle sheets, or cut the ban/pick reels' unique frames (docs/perf.md section 9).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import package_mod as pm  # noqa: E402

# MiB once decoded, every hero's together: the BP grid keeps every hero's bp sheet, the hero screen every idle sheet, each
# beside the screen's own pictures - three quarters and a quarter of the 256 MiB cache
LIMITS = {"bp": 192, "idle": 64}


def main():
    t0 = time.time()
    total = {k: 0.0 for k in pm.UI_KINDS}
    sizes, bad, heroes_n = [], [], 0
    for pack in ("league", "tft"):
        src = os.path.join(pm.REPO, pack)
        heroes = pm.hero_ids(src)
        heroes_n += len(heroes)
        pkg, _ = pm.build(src, heroes, everything=True, workers=os.cpu_count() or 4)
        for h in heroes:
            for kind in pm.UI_KINDS:
                name = f"{pm.UI_DIR}/{kind}/{h}"
                if name + "#sheet.png" not in pkg or name + "#anim.fanim" not in pkg:
                    bad.append(f"{h}: no {pm.UI_DIR}/{kind} sheet - the BP grid / hero screen would draw its whole battle sheet")
                    continue
                w, hgt = pm.png_size(pkg[name + "#sheet.png"])
                mib = 4 * w * hgt / 2 ** 20
                total[kind] += mib
                sizes.append((mib, kind, h))
    print(f"{heroes_n} champions, UI sheets checked in {time.time() - t0:.0f} s")
    for kind, limit in LIMITS.items():
        top = sorted((s for s in sizes if s[1] == kind), reverse=True)[:5]
        print(f"  {kind:5s} {total[kind]:6.1f} MiB of {limit} (largest: " + ", ".join(f"{h} {m:.1f}" for m, _, h in top) + ")")
        if total[kind] > limit:
            bad.append(f"{pm.UI_DIR}/{kind}: {total[kind]:.0f} MiB together, past {limit} MiB - the screens showing every "
                       f"hero near the game's 256 MiB image cache again (docs/perf.md section 9)")
    if bad:
        print("\n".join(["FAILED:"] + bad))
        sys.exit(1)
    print("ok")


if __name__ == "__main__":
    main()
