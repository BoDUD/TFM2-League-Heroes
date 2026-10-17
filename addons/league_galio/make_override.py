"""Build the add-on's copy of Galio from the main pack (Shield of Durand's passive shield, the taunt, Hero's Entrance's ally).

    python addons/league_galio/make_override.py

Rebuilds Galio with tools/kit/build_galio.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_galio.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_galio/override/league_galio.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, minus the attack's passive shield (the add-on gives it after 12 s untouched),
    W's fixed taunt (league_galio:taunt) and R's own choice of ally (league_galio:entrance asks every ally);
  * passive league_galio:colossus (params: the shield, W's reach and taunt, R's reaches);
  * the attack's, skill2's and R's tooltips point to description.league_galio_colossus.* with the add-on's wording, so
    the tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Galio changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_galio")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_galio as kit  # noqa: E402
import setup_galio as setup  # noqa: E402

TEXT_ID = "league_galio_colossus"        # the text's key (the hero's own id is league_galio)
HERO = "league_galio"
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": [("普攻时获得", "{w_ps_cd}秒没受伤获得"), ("护盾，每" + setup.A + "{w_ps_cd}秒" + setup.E + "一次。", "护盾。")],
                "skill2": [("随后" + setup.R + "嘲讽{w_taunt}秒" + setup.E, "随后" + setup.R + "嘲讽" + setup.E + "（身边英雄越多越久）")],
                "ult": [("给陷入苦战的友方英雄", "给苦战中血量最低的友方英雄")]},
    "zh-hant": {"attack": [("普攻時獲得", "{w_ps_cd}秒沒受傷獲得"), ("護盾，每" + setup.A + "{w_ps_cd}秒" + setup.E + "一次。", "護盾。")],
                "skill2": [("隨後" + setup.R + "嘲諷{w_taunt}秒" + setup.E, "隨後" + setup.R + "嘲諷" + setup.E + "（身邊英雄越多越久）")],
                "ult": [("給陷入苦戰的友方英雄", "給苦戰中血量最低的友方英雄")]},
    "en": {"attack": [("attacking grants", "{w_ps_cd}s without damage grants"),
                      (" shield, once every " + setup.A + "{w_ps_cd}s" + setup.E + ".", " shield.")],
           "skill2": [(setup.R + "taunts" + setup.E + " nearby enemies for " + setup.R + "{w_taunt}s" + setup.E,
                       setup.R + "taunts" + setup.E + " nearby enemies (longer the more champions are near)")],
           "ult": [("an allied champion in a fight", "the allied champion lowest on health in a fight")]},
    "ko": {"attack": [("기본 공격 시", "{w_ps_cd}초 동안 피해를 받지 않으면"), (" 보호막, " + setup.A + "{w_ps_cd}초" + setup.E + "마다 한 번.", " 보호막.")],
           "skill2": [(setup.R + "{w_taunt}초 도발" + setup.E, setup.R + "도발" + setup.E + "(주변 챔피언이 많을수록 길게)")],
           "ult": [("싸우는 아군 챔피언에게", "싸우는 아군 중 체력이 가장 낮은 챔피언에게")]},
    "ja": {"attack": [("通常攻撃で", "{w_ps_cd}秒被弾しないと"), ("のシールド（" + setup.A + "{w_ps_cd}秒" + setup.E + "毎）。", "のシールド。")],
           "skill2": [(setup.R + "{w_taunt}秒挑発" + setup.E, setup.R + "挑発" + setup.E + "（周囲のチャンピオンが多いほど長く）")],
           "ult": [("戦う味方チャンピオンに", "戦う味方で体力が最も低いチャンピオンに")]},
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
        sys.exit("the main pack's league_galio differs from build_galio.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if "league_galio:taunt" not in text or "league_galio:entrance" not in text or "passive" not in champion:
        sys.exit("the copy does not call the add-on: update this script")
    for slot in ("attack", "skill2", "ult"):
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = setup.values(p)
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot, pairs in swaps.items():
            src = setup.TEXT[lang][slot]
            for old, new in pairs:
                if old not in src:
                    sys.exit(f"{lang}.{slot}: {old!r} is not in setup_galio.TEXT")
                src = src.replace(old, new)
            texts[lang][slot] = (LEAD[lang] + src).format(**values)
    long = {f"{lang}.{slot}": setup.shown_length(t) for lang, d in texts.items() for slot, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
