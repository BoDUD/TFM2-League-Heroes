"""Build the add-on's copy of Corki from the main pack (missiles aimed, Valkyrie escaping).

    python addons/league_corki/make_override.py

Rebuilds Corki with tools/kit/build_corki.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_corki.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_corki/override/league_corki.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * R calls league_corki:aim (the Big One league_corki:big) instead of firing at the AI's target, W / the Package call
    league_corki:escape / league_corki:package instead of hopping straight away from the champion beside him;
  * R's and E's tooltips point to description.league_corki_aim.* with the add-on's wording, so the tooltip in game
    shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Corki changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_corki")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_corki as kit  # noqa: E402
import setup_corki as setup  # noqa: E402

MOD_ID = "league_corki"
TEXT_ID = "league_corki_aim"           # the text's key (the hero's own id is league_corki)
HERO = "league_corki"
# lang -> (the lead, the sentence added to R, the sentence added to E)
NATIVE = {
    "zh-hans": ("【智能】", "火箭瞄准能炸到最多敌人的地方，大火箭优先残血英雄。", "俯冲避开墙和敌方塔，朝队友飞。"),
    "zh-hant": ("【智能】", "火箭瞄準能炸到最多敵人的地方，大火箭優先殘血英雄。", "俯衝避開牆和敵方塔，朝隊友飛。"),
    "en": ("[Aimed] ", " Missiles aim where they hit the most, the Big One at low champions.",
           " The dash avoids walls and enemy towers and heads for his team."),
    "ko": ("[조준] ", " 미사일은 가장 많이 맞힐 곳을, 대형은 체력 낮은 챔피언을 노림.", " 돌진은 벽과 적 포탑을 피해 아군 쪽으로."),
    "ja": ("【狙い】", "ミサイルは最も多く当たる位置、大型は低体力の敵を狙う。", "突進は壁と敵タワーを避け味方の方へ。"),
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
        sys.exit("the main pack's league_corki differs from build_corki.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    for slot, call in (("ult", "league_corki:aim"), ("ult", "league_corki:big"), ("skill2", "league_corki:escape"),
                       ("skill2", "league_corki:package")):
        if call not in json.dumps(champion[slot]):
            sys.exit(f"the copy's {slot} does not call {call}: update this script")
    champion["ult"]["description"] = "#asset/base/text/champion?description." + TEXT_ID + ".ult"
    champion["skill2"]["description"] = "#asset/base/text/champion?description." + TEXT_ID + ".skill2"

    values = setup.values(p)
    texts = {}
    for lang, (lead, r_extra, w_extra) in NATIVE.items():
        texts[lang] = {"ult": (lead + setup.TEXT[lang]["ult"] + r_extra).format(**values),
                       "skill2": (lead + setup.TEXT[lang]["skill2"] + w_extra).format(**values)}
    long = {f"{lang}.{k}": setup.shown_length(v) for lang, d in texts.items() for k, v in d.items()
            if setup.shown_length(v) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
