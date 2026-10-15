"""Build the add-on's copy of Katarina from the main pack (smart Shunpo, Voracity on every takedown).

    python addons/league_katarina/make_override.py

Rebuilds Katarina with tools/kit/build_katarina.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_katarina.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_katarina/override/league_katarina.data_champion and .../text/champion.i18n: the build with
native=1 -
  * everything of the main pack's kit (Q's Shunpo onto its dagger, W's Shunpo in, the daggers, the spin, R);
  * no takedown window (the passive resets on every kill and assist natively);
  * passive = the add-on's league_katarina:blades with the numbers of P;
  * the attack's tooltip (it carries Voracity) points to description.league_katarina.attack with the add-on's wording
    (a key of the add-on's own id), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Katarina changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_katarina")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_katarina as kit  # noqa: E402
import setup_katarina as setup  # noqa: E402

MOD_ID = "league_katarina"
HERO = "league_katarina"
O, M, A, E = setup.O, setup.M, setup.A, setup.E
mag = setup.mag
# lang -> the add-on's attack text (the main pack's Voracity window replaced, the daggers' sentence kept)
NATIVE = {
    "zh-hans": "【附加包】" + O + "贪婪" + E + "：她参与击杀的每个敌方英雄都让Q、W冷却刷新、瞬步就绪。瞬步就绪时自己跳到有敌人的匕首旁（残血时跳到远离敌人的）。"
               "捡起匕首旋斩周围敌人，造成" + mag("p") + M + "魔法伤害" + E + "，瞬步冷却降为" + A + "{e_short}秒" + E + "。",
    "zh-hant": "【附加包】" + O + "貪婪" + E + "：她參與擊殺的每個敵方英雄都讓Q、W冷卻刷新、瞬步就緒。瞬步就緒時自己跳到有敵人的匕首旁（殘血時跳到遠離敵人的）。"
               "撿起匕首旋斬周圍敵人，造成" + mag("p") + M + "魔法傷害" + E + "，瞬步冷卻降為" + A + "{e_short}秒" + E + "。",
    "en": "[Add-on] " + O + "Voracity" + E + ": every enemy champion she takes down refreshes Q and W and readies Shunpo. With Shunpo "
          "ready she blinks to a dagger with an enemy beside it (when low, to one away from them). Picking a dagger up slashes "
          "nearby enemies for " + mag("p") + " " + M + "magic damage" + E + " and cuts Shunpo's cooldown to " + A + "{e_short}s" + E + ".",
    "ko": "[확장] " + O + "탐욕" + E + ": 그녀가 관여한 적 챔피언 처치마다 Q, W 초기화, 순보 준비. 순보가 준비되면 적이 있는 단검으로 스스로 순보(체력이 낮으면 "
          "적에게서 먼 단검으로). 단검을 주우면 주변 적에게 " + mag("p") + " " + M + "마법 피해" + E + ", 순보 대기시간 " + A + "{e_short}초" + E + ".",
    "ja": "【拡張】" + O + "貪欲なる暗殺者" + E + "：彼女が関わった敵チャンピオンの撃破ごとにQ・WのCD解消、瞬歩使用可能。瞬歩が使えると敵のそばの短剣へ"
          "自ら瞬歩（瀕死なら敵から遠い短剣へ）。拾うと周囲に" + mag("p") + "の" + M + "魔法ダメージ" + E + "、瞬歩CD" + A + "{e_short}秒" + E + "。",
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
        sys.exit("the main pack's league_katarina differs from build_katarina.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":blades":
        sys.exit("the copy has no league_katarina:blades passive: update this script")
    if '"league_katarina_p_alive"' in json.dumps(champion):
        sys.exit("the copy still carries the takedown window: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = setup.values(p)
    texts = {lang: {"attack": t.format(**values)} for lang, t in NATIVE.items()}
    long = {f"{lang}.attack": setup.shown_length(NATIVE[lang]) for lang in texts
            if setup.shown_length(NATIVE[lang]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.attack": f"{setup.shown_length(NATIVE[lang])}/{setup.TOOLTIP_MAX[lang]}"
                              for lang in texts})


if __name__ == "__main__":
    main()
