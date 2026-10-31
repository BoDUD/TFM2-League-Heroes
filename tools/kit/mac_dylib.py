#!/usr/bin/env python3
"""The packs' Mac code: league.dylib, league_addons.dylib, tft.dylib (2026-10-31, the user: 「想个办法主包和附加包能兼容mac吧」).

The game picks a native mod's code by platform from the files in its folder (<game>/mod-sdk-stable/README.txt):
<mod_id>.dll on Windows, <mod_id>.dylib on a Mac; a folder without its platform's file is a mod that "has no version
for your operating system". A .dylib links only on a Mac (Apple's SDK cannot be redistributed), so CI's `mac` job
(.github/workflows/ci.yml) builds the three for every commit, Apple silicon and Intel in one file each, and uploads
them as the artifact mac-dylibs-<commit>. tools/package_mod.py and addons/league_addons/assemble.py put the ones of the
commit they pack into the package, fetched here with `gh` (logged in, as for the PRs) into dist/mac/<commit>/:

    python tools/kit/mac_dylib.py                  # HEAD's three
    python tools/kit/mac_dylib.py --commit <sha>

A .dylib is the same source as the .dll beside it only when the code under addons/ is the commit's: with uncommitted
changes there, or no artifact for the commit (not pushed yet, CI still running or red, older than 90 days), the
package goes out without it and the scripts say so.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NAMES = ("league.dylib", "league_addons.dylib", "tft.dylib")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8")


def fetch(commit=None):
    """-> (the folder holding the commit's .dylib files, None) or (None, why there are none)."""
    if commit is None:
        r = git("rev-parse", "HEAD")
        if r.returncode:
            return None, "not a git checkout"
        commit = r.stdout.strip()
        dirty = git("status", "--porcelain", "--untracked-files=no", "--", "addons").stdout.splitlines()
        if dirty:
            return None, f"uncommitted changes under addons/ ({len(dirty)}: {dirty[0].strip()} ...): CI built the commit, not them"
    folder = os.path.join(REPO, "dist", "mac", commit)
    if all(os.path.isfile(os.path.join(folder, n)) for n in NAMES):
        return folder, None
    tmp = tempfile.mkdtemp(prefix="mac_dylib_")
    try:
        r = subprocess.run(["gh", "run", "download", "-n", f"mac-dylibs-{commit}", "-D", tmp],
                           cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        shutil.rmtree(tmp, ignore_errors=True)
        return None, "no `gh` (GitHub CLI) to fetch CI's artifact"
    if r.returncode or not all(os.path.isfile(os.path.join(tmp, n)) for n in NAMES):
        shutil.rmtree(tmp, ignore_errors=True)
        why = (r.stderr or r.stdout).strip().splitlines()
        return None, (f"no artifact mac-dylibs-{commit[:9]} on GitHub ({why[-1] if why else 'not all three in it'}): "
                      f"is the commit pushed and its CI mac job green?")
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(os.path.dirname(folder), exist_ok=True)
    shutil.move(tmp, folder)
    return folder, None


def dylib(name, explicit=None):
    """-> (the bytes of `name`, where they came from) or (None, why not): --dylib's file, else HEAD's CI build."""
    if explicit:
        with open(explicit, "rb") as f:
            return f.read(), explicit
    folder, why = fetch()
    if folder is None:
        return None, why
    with open(os.path.join(folder, name), "rb") as f:
        return f.read(), f"CI's Mac build of {os.path.basename(folder)[:9]}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--commit", help="this commit's build instead of HEAD's (no check of the working tree)")
    a = ap.parse_args()
    folder, why = fetch(a.commit)
    if folder is None:
        sys.exit(why)
    for n in NAMES:
        print(f"{os.path.join(folder, n)}: {os.path.getsize(os.path.join(folder, n)) / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
