# Xin Zhao / Galio, 2026-11-19 (PR #784)

One-off edits of the two heroes' sheets (each refuses a sheet it has already changed where it can tell), in the order run:

1. `xz_fix.py <tree> <out>` - Xin Zhao's spear made the attack frames' spear everywhere (the user: 「待机时候枪末尾是这样的 攻击时就
   不是这个模型了」): the ready stance (`redesign.py`: no crescent hook, butt = gold band + silver tip, slid in) and the run
   (`run_redesign.py`, frame by frame), the low thrust's blade slid in (`slide.py`); 1x / lo_ / strips as the pipeline
   makes them. `verify.py` checks lo_ = add_lo(hd_), 1x = pixelate(hd_), strips = hd_.
2. `xz_ribbon_tag.py <repo>` - Xin Zhao's ribbons flutter while he stands (「发带能动吗」): tag `idle_loop` (`ribbon.py`).
3. `galio_fix.py <repo>` - Galio's wings flap in the run and while he stands (「走路时翅膀不动 待机也是」, `wings.py`:
   RotSprite turn about the root, behind the body), his run legs cleaned (「腿部像素缺失」「不干净的黑边」, `legclean.py`),
   the tail left as drawn; tag `idle_loop`. `check2.py`: stray black pieces, stone pixels changed.
4. `python tools/art/hero_reels.py --hero league_galio,league_xinzhao` - their reels, the holds playing `idle_loop`
   (hero_reels.json "hold"); then the idle strips = idle_base (`sheetkit.Kit.strip`), `tools/art/illaoi_souls.py`,
   `addons/league_viego_soul/make_override.py`.

`sheetkit.py`: a dense hero's frames written the pipeline's way (hd_ master, 1x / lo_ derived, strips, new rects).
