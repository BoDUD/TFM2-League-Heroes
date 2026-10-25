"""Build the add-on's copy of Trundle from the main pack (King's Tribute, a fixed domain, terrain pillars, League's Chomp
and Subjugate).

    python addons/league_trundle/make_override.py [--draft] [--check]

Rebuilds Trundle with tools/kit/build_trundle.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_trundle.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_trundle/override/league_trundle.data_champion and
.../text/champion.i18n: the build with native=1 (build_trundle.py's docstring) -
  * passive = league_trundle:troll (params build_trundle.NATIVE_KEYS);
  * no kill trigger (the add-on heals for every enemy dying near him); `w_on` a plain mark (the add-on's `w_in` holds the
    domain's stats while he stands in it); the pillar marks its champions `e_at` (no hold); Chomp marks `q_mark` (no sap,
    no `q_ad`); Subjugate marks `r_drain` (no true damage, heal or stat cut of its own);
  * the attack's and the ult's tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Trundle changes.
--draft: only the copy, without the main-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_trundle")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_trundle as kit  # noqa: E402

MOD_ID = "league_trundle"
HERO = "league_trundle"
KEYS = kit.NATIVE_KEYS
# lang -> the add-on's attack and ult texts (the main pack's with the add-on's rules): written at integration with
# tools/kit/setup_trundle.py's helpers (setup.phys / t / n / cc); until then --draft only
NATIVE = {}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (p_pct: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":troll":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        import setup_trundle as setup  # noqa: E402 (the main pack's texts, at integration)
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_trundle differs from build_trundle.P: rebuild it first")
        for slot in ("attack", "ult"):
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = setup.values(p)
        texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
        long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
                if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
        if long:
            sys.exit("tooltip too long for the details panel: %s" % long)
        with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
            main_text = json.load(f)
        missing = set(main_text) - set(texts)
        if missing:
            sys.exit("no add-on text for %s" % sorted(missing))
        out[os.path.join(ADDON, "text", "champion.i18n")] = dumps_main(
            {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text})
        print({f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}" for lang, d in NATIVE.items()
               for k, tx in d.items()})
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
