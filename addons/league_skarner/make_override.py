"""Build the add-on's copy of Skarner from the main pack (Quaking per champion, the wall stun, Impale's first three dragged).

    python addons/league_skarner/make_override.py [--draft] [--check]

Rebuilds Skarner with tools/kit/build_skarner.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_skarner.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
constants in src/lib.rs are P's numbers, and writes addons/league_skarner/override/league_skarner.data_champion and
.../text/champion.i18n: the build with native=1 (build_skarner.py's docstring) -
  * passive = league_skarner:sovereign (params build_skarner.NATIVE_KEYS);
  * Quaking's climb = league_skarner:quake (Impale's native quakes its own champions), no ladder on him; E's contact =
    league_skarner:impact (no Knockback, no slam of its own); Impale's hit = league_skarner:impale (no damage, Stun or
    Grab of its own);
  * the slots' tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game shows whether the
    override took.
Every other champion stays untouched. Run it again whenever the main pack's Skarner changes.
--draft: only the copy, without the main-pack check and the texts (before tools/kit/setup_skarner.py exists).
--check: write nothing, exit 1 when the files on disk are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_skarner")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_skarner as kit  # noqa: E402

MOD_ID = "league_skarner"
HERO = "league_skarner"
KEYS = kit.NATIVE_KEYS
SLOTS = ("attack", "skill", "skill2", "ult")   # every slot's rules differ from the main pack's


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_consts(p):
    """src/lib.rs's constants (P_N, E_STUN, ...) hold P's numbers."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    got = {k.lower(): int(v.replace("_", "")) for k, v in re.findall(r"pub const ([A-Z_0-9]+): usize = ([0-9_]+);", src)}
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs constants differ from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_consts(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":sovereign":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        import setup_skarner as setup  # noqa: E402  (the main pack's texts; exists from the integration on)
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_skarner differs from build_skarner.P: rebuild it first")
        for slot in SLOTS:
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        texts = setup.native_texts(p)
        with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
            main_text = json.load(f)
        missing = set(main_text) - set(texts)
        if missing:
            sys.exit("no add-on text for %s" % sorted(missing))
        out[os.path.join(ADDON, "text", "champion.i18n")] = dumps_main(
            {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text})
    out[os.path.join(ADDON, "override", HERO + ".data_champion")] = dumps_main(champion)
    return out, champion


def main():
    draft = "--draft" in sys.argv[1:]
    out, champion = files(draft)
    if "--check" in sys.argv[1:]:
        stale = [os.path.relpath(path, ROOT) for path, text in out.items()
                 if not os.path.isfile(lp(path)) or open(lp(path), encoding="utf-8", newline="").read() != text]
        if stale:
            sys.exit("not as make_override.py writes them: %s" % stale)
        print("ok")
        return
    for path, text in out.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("wrote", os.path.relpath(path, ROOT))
    print("(draft)" if draft else json.dumps(champion["passive"]["params"]))


if __name__ == "__main__":
    main()
