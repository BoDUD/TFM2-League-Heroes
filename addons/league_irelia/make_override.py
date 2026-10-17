"""Build the add-on's copy of Irelia from the main pack (Bladesurge resets on the real mark or kill, wave hops).

    python addons/league_irelia/make_override.py

Rebuilds Irelia with tools/kit/build_irelia.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_irelia.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_irelia/override/league_irelia.data_champion: build(p, native=True) -
  * E's and R's champion hits put the real mark (league_irelia_mark) on the champion and no caster flag mk;
  * Q's landing lays only q_land (no kill trigger: the passive sees the kill), Q's cast spends no mk;
  * passive = league_irelia:surge with Q's numbers as its params.
The texts stay the main pack's (they already say: a marked or killed target - one more dash). Every other champion
stays untouched. Run it again whenever the main pack's Irelia changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_irelia")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_irelia as kit  # noqa: E402

MOD_ID = "league_irelia"
HERO = "league_irelia"


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_irelia differs from build_irelia.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":surge":
        sys.exit("the copy has no league_irelia:surge passive: update build_irelia.py")
    flat = json.dumps(champion)
    for name in ("league_irelia_q_dash", "league_irelia_q_again", "league_irelia_mark"):
        if name not in flat:
            sys.exit(f"{name} is no longer in the copy: update src/lib.rs")
    for name in ("league_irelia_mk", "league_irelia_q_kt"):
        if name in flat:
            sys.exit(f"{name} is still in the copy: the passive replaces it")
    if any(not isinstance(v, int) for v in champion["passive"]["params"].values()):
        sys.exit("passive params must be integers")

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "- passive =", champion["passive"]["passive_ref"],
          champion["passive"]["params"])


if __name__ == "__main__":
    main()
