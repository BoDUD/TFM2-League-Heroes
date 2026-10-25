"""Build the add-on's copy of Locke from the main pack (Silver Stake on missing health, Soul Ignition on current health,
Purgatory's execute and seals, takedown resets).

    python addons/league_locke/make_override.py [--draft] [--check]

Rebuilds Locke with tools/kit/build_locke.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_locke.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_locke/override/league_locke.data_champion and
.../text/champion.i18n: the build with native=1 (build_locke.py's docstring) -
  * passive = league_locke:exorcist (params build_locke.NATIVE_KEYS);
  * no takedown window (the add-on reads deaths and readies E itself); the attack marks `p_hit` (the add-on adds the
    missing-health part); W's `w_on` keeps its attack speed but neither burns nor heals (the add-on does, on current
    health); Purgatory's marks `r_mark` take no threshold checks (the add-on executes under r_exec% and keeps the seals);
  * every slot's tooltip (keys of the add-on's own id) says the League rules, so the tooltip in game shows whether the
    override took.
Every other champion stays untouched. Run it again whenever the main pack's Locke changes.
--draft: only the copy, without the main-pack check and the texts (until the integration writes tools/kit/setup_locke.py
and the texts below). --check: write nothing, exit 1 when the files on disk are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_locke")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_locke as kit  # noqa: E402

MOD_ID = "league_locke"
HERO = "league_locke"
KEYS = kit.NATIVE_KEYS
SLOTS = ("attack", "skill", "skill2", "ult")   # every slot's rules differ from the main pack's
# lang -> the add-on's texts for every slot: written at the integration, with tools/kit/setup_locke.py's helpers
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
    m = re.search(r"Self \{ (p_miss: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":exorcist":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        if not NATIVE:
            sys.exit("no add-on texts yet: run with --draft until the integration writes them")
        import setup_locke as setup   # noqa: E402 - written at the integration
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_locke differs from build_locke.P: rebuild it first")
        for slot in SLOTS:
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = dict(setup.values(p), **{k: p[k] for k in KEYS})
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
