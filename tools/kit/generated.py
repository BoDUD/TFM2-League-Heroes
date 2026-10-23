"""`make_override.py --check` of the add-ons that copy a main-pack hero (league_sylas, league_viego_soul, league_neeko,
league_kayn_form): their outputs rebuilt from the main pack and compared with the committed files, so CI (no game on
the runner) tells a copy left behind by a change to the main pack - Sylas's stolen ults after a hero's R changed, Viego's
or Kayn's copy after their kit changed - from one that was rebuilt. The tables that need the base game's champion sheet
(bundle.game_data: classes.rs, souls.rs, ranges.rs) are not rebuilt here; the add-ons' own tests check this pack's
heroes in them.

Line ends are not compared: the files are committed with LF and checked out with CRLF on Windows.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def stale(outs):
    """The paths of `outs` ([(path, text)]) whose file is missing or holds other text."""
    bad = []
    for path, text in outs:
        try:
            with open(_lp(path), encoding="utf-8", newline="") as f:
                have = f.read()
        except OSError:
            have = None
        if have is None or have.replace("\r\n", "\n") != text.replace("\r\n", "\n"):
            bad.append(path)
    return bad


def check(name, outs, need_game=()):
    """Exit 1 naming the out-of-date files of add-on `name`, else print that they are up to date."""
    rel = lambda p: os.path.relpath(p, ROOT).replace(os.sep, "/")
    bad = stale(outs)
    if bad:
        sys.exit(f"{name}: out of date - run addons/{name}/make_override.py (the game installed) and commit: "
                 + ", ".join(rel(p) for p in bad))
    note = f" ({', '.join(need_game)}: need the game, checked by the add-on's tests)" if need_game else ""
    print(f"{name}: {', '.join(rel(p) for p, _ in outs)} up to date{note}")
