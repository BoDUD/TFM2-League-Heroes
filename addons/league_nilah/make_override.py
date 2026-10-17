"""Build the add-on's copy of Nilah from the main pack (Joy Unending's heals and shields; Jubilant Veil, Slipstream and
Apotheosis need nothing in the data).

    python addons/league_nilah/make_override.py

Rebuilds Nilah with tools/kit/build_nilah.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_nilah.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_nilah/override/league_nilah.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit plus passive league_nilah:joy (params: amp p_amp, near p_r);
  * the attack's, skill2's and R's tooltips point to description.league_nilah_joy.* with the add-on's wording, so the
    tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Nilah changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_nilah")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_nilah as kit  # noqa: E402
import setup_nilah as setup  # noqa: E402

TEXT_ID = "league_nilah_joy"      # the text's key (the hero's own id is league_nilah)
HERO = "league_nilah"
SLOTS = ("attack", "skill2", "ult")
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": [("鞭刃近战攻击。", "鞭刃近战攻击；她和附近友方英雄受到的回复、护盾+{p_amp}%。")],
                "skill2": [("穿过敌方英雄冲刺", "穿过血量比例最低的敌方英雄冲刺"), ("用完时放", "用完后被敌方英雄攻击时放")],
                "ult": [("旋转鞭刃", "等到能卷进多名敌方英雄时旋转鞭刃")]},
    "zh-hant": {"attack": [("鞭刃近戰攻擊。", "鞭刃近戰攻擊；她和附近友方英雄受到的回復、護盾+{p_amp}%。")],
                "skill2": [("穿過敵方英雄衝刺", "穿過血量比例最低的敵方英雄衝刺"), ("用完時放", "用完後被敵方英雄攻擊時放")],
                "ult": [("旋轉鞭刃", "等到能捲進多名敵方英雄時旋轉鞭刃")]},
    "en": {"attack": [("melee whip-blade attacks.", "melee whip-blade attacks; heals and shields on her and nearby allied "
                                                    "champions are {p_amp}% stronger.")],
           "skill2": [("dashes through an enemy champion", "dashes through the lowest enemy champion"),
                      ("With both spent, ", "With both spent and an enemy champion hitting her, ")],
           "ult": [("Spins her whip-blade", "Once it can catch several enemy champions, spins her whip-blade")]},
    "ko": {"attack": [("채찍검 근접 공격.", "채찍검 근접 공격; 자신과 주변 아군 챔피언이 받는 회복·보호막 +{p_amp}%.")],
           "skill2": [("적 챔피언을 관통해 돌진", "체력 비율이 가장 낮은 적 챔피언을 관통해 돌진"),
                      ("모두 쓰면 ", "모두 쓰고 적 챔피언에게 공격받으면 ")],
           "ult": [(" 동안 채찍검을 돌려 ", " 동안 (적 챔피언 여럿이 들어올 때) 채찍검을 돌려 ")]},
    "ja": {"attack": [("鞭刃の近接攻撃。", "鞭刃の近接攻撃；自身と周囲の味方チャンピオンが受ける回復・シールド+{p_amp}%。")],
           "skill2": [("敵チャンピオンを突き抜けて", "体力割合が最も低い敵チャンピオンを突き抜けて"),
                      ("使い切ると", "使い切って敵チャンピオンに攻撃されると")],
           "ult": [("鞭刃を回し", "複数の敵チャンピオンを巻き込める時に鞭刃を回し")]},
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_nilah differs from build_nilah.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_nilah:joy":
        sys.exit("the copy does not call the add-on: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = dict(setup.values(p), p_amp=p["p_amp"])
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot, pairs in swaps.items():
            src = setup.TEXT[lang][slot]
            for old, new in pairs:
                if old not in src:
                    sys.exit(f"{lang}.{slot}: {old!r} is not in setup_nilah.TEXT")
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
    for lang, d in texts.items():
        print(lang, " ".join(f"{s}:{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for s, t in d.items()))
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
