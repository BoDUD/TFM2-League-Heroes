"""Build the add-on's copy of Sejuani from the main pack (Frost, the shatter, the Frost Armour and Arctic Assault as in League).

    python addons/league_sejuani/make_override.py [--draft]

Rebuilds Sejuani with tools/kit/build_sejuani.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_sejuani.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_sejuani/override/league_sejuani.data_champion
(and, at integration, .../text/champion.i18n): the build with native=1 -
  * passive = league_sejuani:frost (params f_n e_stun e_dmg e_ap sh_cd sh_dmg sh_ap sh_pct q_t fa_out);
  * the attack and W put a `frost` stack and a 3-tick `hit` mark on the champion they hit (the add-on freezes at f_n
    stacks and shatters a champion stunned by anyone), instead of the main pack's count on her;
  * the Frost Armour without the tenacity stand-in (the add-on clears slows off her);
  * Arctic Assault raises `q_stop` on its first champion (the add-on holds her there).
Every other champion stays untouched. Run it again whenever the main pack's Sejuani changes.
--draft: only the copy, without the main-pack check and the texts (before the main pack has Sejuani).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_sejuani")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_sejuani as kit  # noqa: E402

HERO = "league_sejuani"
KEYS = ("f_n", "e_stun", "e_dmg", "e_ap", "sh_cd", "sh_dmg", "sh_ap", "sh_pct", "q_t", "fa_out")


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (f_n: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def main():
    draft = "--draft" in sys.argv[1:]
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if "league_sejuani:frost" not in json.dumps(champion):
        sys.exit("the copy does not call the add-on: update this script")
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_sejuani differs from build_sejuani.P: rebuild it first")
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    print(out, "(draft)" if draft else "")


if __name__ == "__main__":
    main()
