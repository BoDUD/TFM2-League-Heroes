"""Build the add-on's copy of Nautilus from the main pack (Dredge Line hooks the map's walls).

    python addons/league_nautilus/make_override.py

Rebuilds Nautilus with tools/kit/build_nautilus.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_nautilus.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_nautilus/override/league_nautilus.data_champion and .../text/champion.i18n: the build with
native=1 -
  * everything of the main pack's kit;
  * Q's anchor also calls league_nautilus:hook as it flies (a wall on its line before any enemy champion: pulled to the
    wall, half the cooldown back);
  * Q's tooltip points to description.league_nautilus_wall.skill with the add-on's wording, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Nautilus changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_nautilus")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_nautilus as kit  # noqa: E402
import setup_nautilus as setup  # noqa: E402

MOD_ID = "league_nautilus"
TEXT_ID = "league_nautilus_wall"          # the text's key (the hero's own id is league_nautilus)
HERO = "league_nautilus"
# lang -> (the lead, the sentence added to Q)
NATIVE = {
    "zh-hans": ("【钩墙版】", "锚先撞到墙时把自己拉到墙边，返还一半冷却。"),
    "zh-hant": ("【鉤牆版】", "錨先撞到牆時把自己拉到牆邊，返還一半冷卻。"),
    "en": ("[Wall build] ", " If the anchor strikes a wall first, he pulls himself to it and gets half the cooldown back."),
    "ko": ("[벽 갈고리] ", " 닻이 먼저 벽에 박히면 벽으로 끌려가고 재사용 대기시간의 절반을 돌려받음."),
    "ja": ("【壁フック】", "錨が先に壁に刺さると壁まで自分を引き寄せ、クールダウンの半分が戻る。"),
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
        sys.exit("the main pack's league_nautilus differs from build_nautilus.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if "league_nautilus:hook" not in json.dumps(champion["skill"]):
        sys.exit("the copy's Q does not call league_nautilus:hook: update this script")
    champion["skill"]["description"] = "#asset/base/text/champion?description." + TEXT_ID + ".skill"

    values = setup.values(p)
    texts = {}
    for lang, (lead, extra) in NATIVE.items():
        texts[lang] = {"skill": (lead + setup.TEXT[lang]["skill"] + extra).format(**values)}
    long = {f"{lang}.skill": setup.shown_length(d["skill"]) for lang, d in texts.items()
            if setup.shown_length(d["skill"]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
