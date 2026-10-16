"""Build the add-on's copy of Tahm Kench from the main pack (stacks per champion, grey health, Devour and the dive's timing).

    python addons/league_tahmkench/make_override.py

Rebuilds Tahm Kench with tools/kit/build_tahmkench.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_tahmkench.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_tahmkench/override/league_tahmkench.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, minus the data's own stack ladder (his attacks and W call league_tahmkench:taste,
    Q league_tahmkench:lash), Thick Skin's flat reduction and shield (the add-on stores the real damage), the gates of W
    and R in data (the add-on's AI hook picks and holds them); R's swallow stays data, one probe for an ally, one for an
    enemy champion, both calling league_tahmkench:devour;
  * passive league_tahmkench:skin (params: the stack hold, the stun, the devour times, Thick Skin's numbers);
  * the attack's, skill2's and R's tooltips point to description.league_tahmkench_skin.* with the add-on's wording, so
    the tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Tahm Kench changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_tahmkench")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_tahmkench as kit  # noqa: E402
import setup_tahmkench as setup  # noqa: E402

TEXT_ID = "league_tahmkench_skin"        # the text's key (the hero's own id is league_tahmkench)
HERO = "league_tahmkench"
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": [("普攻、Q、W命中英雄叠一层", "普攻、Q、W给每个英雄各自叠层"),
                           ("受到伤害降低{e_red}%，", "受到伤害的{store}%存为灰色生命、脱战回血，")],
                "skill2": [("潜入地下", "看准时机潜入地下")],
                "ult": [("吞下被控制、身陷敌群的队友", "吞下残血、掉血快或被控住的队友")]},
    "zh-hant": {"attack": [("普攻、Q、W命中英雄疊一層", "普攻、Q、W給每個英雄各自疊層"),
                           ("受到傷害降低{e_red}%，", "受到傷害的{store}%存為灰色生命、脫戰回血，")],
                "skill2": [("潛入地下", "看準時機潛入地下")],
                "ult": [("吞下被控制、身陷敵群的隊友", "吞下殘血、掉血快或被控住的隊友")]},
    "en": {"attack": [("attacks, Q and W stack on champions", "attacks, Q and W stack on each champion"),
                      ("{e_red}% less damage taken;", "{store}% of the damage taken is stored as grey health, healed back out of combat;")],
           "skill2": [("Dives underground", "At the right moment, dives underground")],
           "ult": [("Swallows an ally caught in crowd control among enemies", "Swallows an ally who is low, losing health fast or held among enemies")]},
    "ko": {"attack": [("기본 공격·Q·W가 챔피언에 중첩", "기본 공격·Q·W가 챔피언마다 중첩"),
                      ("받는 피해 {e_red}% 감소", "받는 피해의 {store}%를 회색 체력으로 저장")],
           "skill2": [("동안 땅속으로 잠수", "동안 때를 봐서 땅속으로 잠수")],
           "ult": [("군중 제어에 걸려 적에게 둘러싸인 아군을", "위험한 아군을")]},
    "ja": {"attack": [("通常攻撃・Q・Wがチャンピオンにスタック", "通常攻撃・Q・Wがチャンピオンごとにスタック"),
                      ("被ダメージ{e_red}%軽減", "被ダメージの{store}%をグレー体力として蓄積")],
           "skill2": [("地中に潜り", "好機に地中に潜り")],
           "ult": [("敵に囲まれ行動妨害を受けた味方を", "危険な味方を")]},
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
        sys.exit("the main pack's league_tahmkench differs from build_tahmkench.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if any(f"league_tahmkench:{x}" not in text for x in ("taste", "lash", "devour")) or "passive" not in champion:
        sys.exit("the copy does not call the add-on: update this script")
    for slot in ("attack", "skill2", "ult"):
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = dict(setup.values(p), store=p["e_store"])
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot, pairs in swaps.items():
            src = setup.TEXT[lang][slot]
            for old, new in pairs:
                if old not in src:
                    sys.exit(f"{lang}.{slot}: {old!r} is not in setup_tahmkench.TEXT")
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
