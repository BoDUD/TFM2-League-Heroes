"""Build the add-on's copy of Braum from the main pack (stacks per champion, the shield's side, the fissure's line).

    python addons/league_braum/make_override.py

Rebuilds Braum with tools/kit/build_braum.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_braum.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_braum/override/league_braum.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, minus the data's own stack ladder (his attacks and Q call league_braum:blow /
    league_braum:bite) and E's damage reduction for him and the allies near him (the add-on gives it by side);
  * passive league_braum:heart (params: the stack numbers, E's reductions and reach);
  * the attack's, skill2's and R's tooltips point to description.league_braum_heart.* with the add-on's wording, so the
    tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Braum changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_braum")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_braum as kit  # noqa: E402
import setup_braum as setup  # noqa: E402

TEXT_ID = "league_braum_heart"        # the text's key (the hero's own id is league_braum)
HERO = "league_braum"
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": [("普攻和寒冬之咬命中英雄叠一层", "普攻和寒冬之咬给英雄叠层，队友普攻也叠")],
                "skill2": [("受到伤害降低", "正面伤害降低"), ("身边友方英雄", "盾后的友方英雄")],
                "ult": [("冲向目标", "冲向敌方英雄最多的方向")]},
    "zh-hant": {"attack": [("普攻和凜冬衝擊命中英雄疊一層", "普攻和凜冬衝擊給英雄疊層，隊友普攻也疊")],
                "skill2": [("受到傷害降低", "正面傷害降低"), ("身邊友方英雄", "盾後的友方英雄")],
                "ult": [("衝向目標", "衝向敵方英雄最多的方向")]},
    "en": {"attack": [("attacks and Winter's Bite stack on champions", "his attacks and Winter's Bite stack on a champion, then his allies' attacks too")],
           "skill2": [("{e_red}% less damage", "{e_red}% less damage from the front"),
                      ("allied champions beside him", "allied champions behind it")],
           "ult": [("a fissure runs at the target", "a fissure runs along the line with the most enemy champions")]},
    "ko": {"attack": [("기본 공격과 동상이 챔피언에 중첩", "기본 공격과 동상이 챔피언에 중첩(아군 기본 공격도)")],
           "skill2": [("받는 피해", "정면에서 받는 피해"), ("곁의 아군 챔피언", "방패 뒤 아군 챔피언")],
           "ult": [("대상 쪽으로", "적 챔피언이 가장 많은 쪽으로")]},
    "ja": {"attack": [("通常攻撃と冬の凍瘡がチャンピオンにスタック", "通常攻撃と冬の凍瘡がスタック（味方の通常攻撃も）")],
           "skill2": [("被ダメージ", "正面からの被ダメージ"), ("傍の味方チャンピオン", "盾の後ろの味方チャンピオン")],
           "ult": [("対象へ", "敵チャンピオンが最も多い方へ")]},
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
        sys.exit("the main pack's league_braum differs from build_braum.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if "league_braum:blow" not in text or "league_braum:bite" not in text or "passive" not in champion:
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
                    sys.exit(f"{lang}.{slot}: {old!r} is not in setup_braum.TEXT")
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
