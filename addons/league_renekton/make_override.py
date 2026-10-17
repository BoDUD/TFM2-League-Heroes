"""Build the add-on's copy of Renekton from the main pack (Reign of Anger: +50% Fury below half health).

    python addons/league_renekton/make_override.py

Rebuilds Renekton with tools/kit/build_renekton.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_renekton.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_renekton/override/league_renekton.data_champion and .../text/champion.i18n: the same kit with
  * passive = the add-on's league_renekton:anger with the numbers from P as its params (f_n, f_t, low = n_low,
    every = n_every): below low% health every every-th rung of Fury he gains brings one more;
  * the attack's tooltip (the passive) points to description.league_renekton.attack with a "test build" lead and the
    below-half-health sentence, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Renekton changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_renekton")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_renekton as kit  # noqa: E402
import setup_renekton as setup  # noqa: E402

MOD_ID = "league_renekton"
A, E = setup.A, setup.E
# lang -> (the lead, the sentence added after the main pack's passive text)
NATIVE = {
    "zh-hans": ("【低血怒气测试版】", "生命低于" + A + "{low}%" + E + "时怒气积攒+50%。"),
    "zh-hant": ("【殘血怒氣測試版】", "生命低於" + A + "{low}%" + E + "時怒氣累積+50%。"),
    "en": ("[Low-health Fury test build] ", " Below " + A + "{low}%" + E + " health he builds Fury 50% faster."),
    "ko": ("[빈사 분노 테스트판] ", " 체력이 " + A + "{low}%" + E + " 미만이면 분노 획득 +50%."),
    "ja": ("【瀕死憤怒テスト版】", "体力" + A + "{low}%" + E + "未満で憤怒の蓄積+50%。"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_renekton.data_champion")), encoding="utf-8",
              newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_renekton differs from build_renekton.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != f"{MOD_ID}:anger":
        sys.exit("the native build has no league_renekton:anger passive: update this script")
    plain = kit.build(p)
    if {k: v for k, v in champion.items() if k != "passive"} != plain:
        sys.exit("the native build changes more than the passive: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = setup.values(p)
    texts = {}
    for lang, (lead, more) in NATIVE.items():
        texts[lang] = (lead + setup.TEXT[lang]["attack"] + more).format(low=p["n_low"], **values)
    long = {lang: setup.shown_length(t) for lang, t in texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_renekton.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no test-build text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
