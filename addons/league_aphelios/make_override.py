"""Build the add-on's copy of Aphelios from the main pack (the real weapon queue, Severum when low; the whole-body
weapon forms need nothing in the data).

    python addons/league_aphelios/make_override.py

Rebuilds Aphelios with tools/kit/build_aphelios.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_aphelios.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_aphelios/override/league_aphelios.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit plus passive league_aphelios:queue (params: the main weapons' stats, the low-health
    swap's threshold, reach and pause - src/lib.rs Params::default must be the same, its test reads this copy);
  * the native build: Moonshot's mark is shot off with the main weapon's on-hit (the add-on swaps the off hand in as
    Moonshot leaves - build_aphelios pop_gift);
  * the attack's, skill's and skill2's tooltips point to description.league_aphelios_queue.* with the add-on's wording, so the
    tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Aphelios changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_aphelios")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_aphelios as kit  # noqa: E402
import setup_aphelios as setup  # noqa: E402

TEXT_ID = "league_aphelios_queue"     # the text's key (the hero's own id is league_aphelios)
HERO = "league_aphelios"
SLOTS = ("attack", "skill", "skill2")
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
SWAP = {
    "zh-hans": {"attack": [("打空换下一把", "打空换队列最前的那把")],
                "skill": [("主手武器的技能，各自冷却：", "主手武器的技能，看局面放，各自冷却：")],
                "skill2": [("主手技能在冷却、副手技能已就绪且附近有敌方英雄时才交换。",
                            "看局面换上合适的武器：换手接技能、开大前换好、通碧射出后换手引爆、被贴脸换近身武器、残血换断魄。")]},
    "zh-hant": {"attack": [("打空換下一把", "打空換佇列最前的那把")],
                "skill": [("主武器的技能，各自冷卻：", "主武器的技能，看局面施放，各自冷卻：")],
                "skill2": [("主武器技能冷卻中、副武器技能已就緒且附近有敵方英雄時才交換。",
                            "看局面換上合適的武器：換手接技能、開大前換好、步槍射出後換手引爆、被貼身換近身武器、殘血換月鐮槍刃。")]},
    "en": {"attack": [("then the next takes its place", "then the next of the queue (first in, first out)")],
           "skill": [("The main weapon's ability, each on its own cooldown:",
                      "The main weapon's ability, used when the moment fits, each on its own cooldown:")],
           "skill2": [("only when the main hand's ability is cooling down, the off hand's is ready and an enemy champion is near.",
                       "by the situation: to chain abilities, the best gift before the ult, the off hand to pop Calibrum's "
                       "mark, a close weapon when dived, Severum when low.")]},
    "ko": {"attack": [("다 쓰면 다음 무기", "다 쓰면 대기열의 다음 무기")],
           "skill": [("주 무기의 스킬(각자 재사용 대기시간):", "주 무기의 스킬(상황에 맞게 사용, 각자 재사용 대기시간):")],
           "skill2": [("주 무기 스킬이 재사용 대기 중이고 보조 무기 스킬이 준비되었으며 근처에 적 챔피언이 있을 때만.",
                       "상황에 맞게: 스킬 연계, 궁극기 전 무기 선택, 만월총 표식 폭발, 근접 시 근접 무기, 체력이 낮으면 절단검.")]},
    "ja": {"attack": [("撃ち尽くすと次の武器に", "撃ち尽くすとキューの次の武器に")],
           "skill": [("メイン武器のスキル（個別CD）：", "メイン武器のスキル（状況を見て使用、個別CD）：")],
           "skill2": [("メインのスキルがCD中、オフハンドのスキルが使用可能で、近くに敵チャンピオンがいる時のみ。",
                       "状況を見て：スキル連携、ウルト前の武器選び、キャリブラムの印を別の武器で起爆、接近されたら近接武器、体力が低いとセヴェラム。")]},
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def _swapped(src, pairs):
    for old, new in pairs:
        src = src.replace(old, new)
    return src


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_aphelios differs from build_aphelios.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_aphelios:queue":
        sys.exit("the copy does not call the add-on: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = setup.values(p)
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot in SLOTS:
            src = setup.TEXT[lang][slot]
            for old, new in swaps[slot]:
                if src.count(old) != 1:
                    sys.exit(f"{lang}.{slot}: {old!r} is not once in setup_aphelios.TEXT")
                src = src.replace(old, new)
            texts[lang][slot] = (LEAD[lang] + src).format(**values)
    lens = {f"{lang}.{slot}": setup.shown_length(LEAD[lang] + _swapped(setup.TEXT[lang][slot], d[slot]))
            for lang, d in SWAP.items() for slot in SLOTS}
    long = {k: n for k, n in lens.items() if n > setup.TOOLTIP_MAX[k.split(".")[0]]}
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
    print("passive", champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {k: f"{n}/{setup.TOOLTIP_MAX[k.split('.')[0]]}" for k, n in lens.items()})


if __name__ == "__main__":
    main()
