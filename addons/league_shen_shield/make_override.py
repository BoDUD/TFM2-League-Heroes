"""Build the add-on's copy of Shen from the main pack (Stand United's shield from his maximum health).

    python addons/league_shen_shield/make_override.py

Rebuilds Shen with tools/kit/build_shen.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_shen.data_champion (so the copy never drifts from the shipped kit), and writes
addons/league_shen_shield/override/league_shen.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, but Stand United puts no data shield on the ally: the add-on's passive
    league_shen_shield:shield gives r_sh_base + r_sh_hp% of Shen's maximum health when league_shen_r_shield shows on
    him (a data Shield reads no health);
  * the ult's tooltip points to description.league_shen_shield.ult with the shield written that way, so the tooltip in
    game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Shen changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_shen_shield")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_shen as kit  # noqa: E402
import setup_shen as setup  # noqa: E402

MOD_ID = "league_shen_shield"
HERO = "league_shen"
HPi = setup.ADi.replace(":ad_0>", ":hp_0>")


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        shipped = json.load(f)
    if kit.build(p) != shipped:
        sys.exit("the main pack's league_shen differs from build_shen.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":shield":
        sys.exit("the copy has no league_shen_shield:shield passive: update this script")
    champion["ult"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".ult"

    values = dict(setup.values(p), r_sh_base=p["r_sh_base"], r_sh_hp=p["r_sh_hp"])
    old = setup.sh("r")
    new = f"{setup.A}{{r_sh_base}}{setup.E} + {HPi}{setup.A}{{r_sh_hp}}%{setup.E}"
    texts = {}
    for lang in setup.TEXT:
        t = setup.TEXT[lang]["ult"]
        if t.count(old) != 1:
            sys.exit(f"{lang} ult: the main pack's shield text changed: update this script")
        texts[lang] = {"ult": t.replace(old, new).format(**values)}
    long = {f"{lang}.ult": setup.shown_length(d["ult"]) for lang, d in texts.items()
            if setup.shown_length(d["ult"]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.ult": f"{setup.shown_length(d['ult'])}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in texts.items()})


if __name__ == "__main__":
    main()
