"""Build the add-on's copy of Gragas from the main pack (Explosive Cask aimed behind the enemies).

    python addons/league_gragas/make_override.py

Rebuilds Gragas with tools/kit/build_gragas.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_gragas.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_gragas/override/league_gragas.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * R calls league_gragas:cask instead of lobbing the cask onto the target (the add-on picks the spot behind the enemy
    champions that flings the most of them toward him, flies the cask there and blows it up);
  * R's tooltip points to description.league_gragas_aim.ult with the add-on's wording, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Gragas changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_gragas")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_gragas as kit  # noqa: E402
import setup_gragas as setup  # noqa: E402

MOD_ID = "league_gragas"
TEXT_ID = "league_gragas_aim"          # the text's key (the hero's own id is league_gragas)
HERO = "league_gragas"
# lang -> (the lead, the sentence added to Q)
NATIVE = {
    "zh-hans": ("【智能落点】", "酒桶落在敌方英雄身后、能把最多敌人（后排优先）炸过来的地方。"),
    "zh-hant": ("【智能落點】", "酒桶落在敵方英雄身後、能把最多敵人（後排優先）炸過來的地方。"),
    "en": ("[Aimed] ", " The cask lands behind the enemy champions, where it flings the most of them (the back line first)."),
    "ko": ("[조준] ", " 술통은 적 챔피언 뒤, 가장 많은 적(후열 우선)을 날려 보낼 곳에 떨어짐."),
    "ja": ("【狙い撃ち】", "タルは敵チャンピオンの背後、最も多くの敵（後衛優先）を吹き飛ばせる位置に落ちる。"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_gragas differs from build_gragas.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if "league_gragas:cask" not in json.dumps(champion["ult"]):
        sys.exit("the copy's R does not call league_gragas:cask: update this script")
    champion["ult"]["description"] = "#asset/base/text/champion?description." + TEXT_ID + ".ult"

    values = setup.values(p)
    texts = {}
    for lang, (lead, extra) in NATIVE.items():
        texts[lang] = {"ult": (lead + setup.TEXT[lang]["ult"] + extra).format(**values)}
    long = {f"{lang}.ult": setup.shown_length(d["ult"]) for lang, d in texts.items()
            if setup.shown_length(d["ult"]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
