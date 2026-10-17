"""Build the add-on's copy of Jarvan IV from the main pack (Cataclysm's real rock ring).

    python addons/league_jarvaniv/make_override.py

Rebuilds Jarvan IV with tools/kit/build_jarvaniv.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_jarvaniv.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_jarvaniv/override/league_jarvaniv.data_champion and .../text/champion.i18n: the build with
native=1 -
  * passive league_jarvaniv:cataclysm (params: r_r, r_t);
  * no probe / Grab hold and no arena check after the landing (the add-on's walls keep everyone on their side);
  * the ult's tooltip points to description.league_jarvaniv_addon.ult with the add-on's wording, so the tooltip in
    game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Jarvan IV changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_jarvaniv")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_jarvaniv as kit  # noqa: E402
import setup_jarvaniv as setup  # noqa: E402

TEXT_ID = "league_jarvaniv_addon"       # the texts' key (the hero's own id is league_jarvaniv)
HERO = "league_jarvaniv"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, R, E = setup.O, setup.A, setup.R, setup.E
phy = setup.phy
TEXT = {
    "zh-hans": {
        "ult": "跃向敌方英雄砸下：周围敌人受到" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "，落点周围升起一圈" + R + "真的岩墙{r_t}秒" + E +
               "：圈里的出不去，圈外的进不来（两边都算，他自己也算）。有被击飞的敌人或2名敌方英雄在身边时才放。",
    },
    "zh-hant": {
        "ult": "躍向敵方英雄砸下：周圍敵人受到" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "，落點周圍升起一圈" + R + "真的岩牆{r_t}秒" + E +
               "：圈裡的出不去，圈外的進不來（兩邊都算，他自己也算）。有被擊飛的敵人或2名敵方英雄在身邊時才施放。",
    },
    "en": {
        "ult": "Leaps onto an enemy champion: " + phy("r_dmg", "r_ratio") + " " + O + "physical damage" + E + " around him, and " + R +
               "a real ring of rock walls rises for {r_t}s" + E + ": no one inside can leave and no one outside can enter (both "
               "teams, him too). Cast on a knocked-up enemy or with 2 enemy champions near him.",
    },
    "ko": {
        "ult": "적 챔피언에게 뛰어올라 주변에 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + ", " + R + "{r_t}초" + E +
               "간 진짜 바위 벽 고리: 안에서는 나갈 수 없고 밖에서는 들어올 수 없음(양 팀, 자신 포함). 띄워진 적이나 적 챔피언 2명이 가까울 때 사용.",
    },
    "ja": {
        "ult": "敵チャンピオンへ跳びかかり周囲に" + phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "、着地点の周りに" + R + "{r_t}秒本物の岩壁" + E +
               "：中からは出られず外からは入れない（両チーム、自分も）。打ち上げた敵か敵2体が近い時に使う。",
    },
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
        sys.exit("the main pack's league_jarvaniv differs from build_jarvaniv.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if champion.get("passive", {}).get("passive_ref") != "league_jarvaniv:cataclysm" or "r_probe" in text or "r_chk" in text:
        sys.exit("the copy does not call the add-on: update this script")
    champion["ult"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.ult"

    values = setup.values(p)
    texts = {lang: {k: (LEAD[lang] + t[k]).format(**values) for k in t} for lang, t in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(LEAD[lang] + TEXT[lang][k]) for lang in TEXT for k in TEXT[lang]
            if setup.shown_length(LEAD[lang] + TEXT[lang][k]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    for lang in TEXT:
        print(lang, " ".join(f"{k}:{setup.shown_length(LEAD[lang] + TEXT[lang][k])}/{setup.TOOLTIP_MAX[lang]}"
                             for k in TEXT[lang]))
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
