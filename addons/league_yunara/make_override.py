"""Build the add-on's copy of Yunara from the main pack (the dash's way, E toward a champion, R by real health).

    python addons/league_yunara/make_override.py

Rebuilds Yunara with tools/kit/build_yunara.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_yunara.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_yunara/override/league_yunara.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (every hit, picture and sound);
  * R's E reads the add-on's re_f / re_b and raises re_go for it to move her (no flag: the main pack's rule);
  * E gives e_ms% only: the add-on adds the rest while she runs at an enemy champion (e_toward);
  * R also fires on the add-on's r_ok (real health);
  * passive = the add-on's league_yunara:faith with the numbers of P;
  * skill2's and the ult's tooltips point to description.league_yunara.skill2 / .ult with the add-on's wording (keys of
    the add-on's own id), so the tooltip in game shows whether the override took.
The Transcendent body needs no data: the main pack's league_yunara_r_on is what the add-on's display hook reads.
Every other champion stays untouched. Run it again whenever the main pack's Yunara changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_yunara")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_yunara as kit  # noqa: E402
import setup_yunara as setup  # noqa: E402

MOD_ID = "league_yunara"
HERO = "league_yunara"
O, A, E = setup.O, setup.A, setup.E
phy = setup.phy
SLOTS = ("skill2", "ult")
# lang -> the add-on's skill2 and ult texts
NATIVE = {
    "zh-hans": {
        "skill2": "【附加包】附近有敌方英雄时，移速+" + A + "{e_ms}%" + E + "，朝敌方英雄跑时+" + A + "{e_ms2}%" + E + "，持续" + A + "{e_t}秒" + E + "。" +
                  O + "超凡形态" + E + "：冲刺，被贴身或残血时往后，追残血时往前。",
        "ult": "【附加包】附近有2个以上敌方英雄、目标被控制、有敌方英雄残血（40%以下）或她自己残血（50%以下）被近身时，进入超凡形态" + A +
               "{r_t}秒" + E + "：灵蕴拳持续开启，善恶轮变为射线，明踪步变为冲刺，两者冷却立刻减少80%；站着跑着都是金光中的她。",
    },
    "zh-hant": {
        "skill2": "【擴充包】附近有敵方英雄時，跑速+" + A + "{e_ms}%" + E + "，朝敵方英雄跑時+" + A + "{e_ms2}%" + E + "，持續" + A + "{e_t}秒" + E + "。" +
                  O + "超凡形態" + E + "：衝刺，被貼身或殘血時往後，追殘血時往前。",
        "ult": "【擴充包】附近有2個以上敵方英雄、目標被控制、有敵方英雄殘血（40%以下）或她自己殘血（50%以下）被近身時，進入超凡形態" + A +
               "{r_t}秒" + E + "：靈心修真持續開啟，審判靈珠變為射線，感銘迅步變為衝刺，兩者冷卻立刻減少80%；站著跑著都是金光中的她。",
    },
    "en": {
        "skill2": "[Add-on] With an enemy champion near, gains " + A + "{e_ms}%" + E + " move speed, " + A + "{e_ms2}%" + E +
                  " while running at one, for " + A + "{e_t}s" + E + ". " + O + "Transcendent" + E + ": a dash - back when "
                  "an enemy champion closes in or she is low, forward after a low one slipping away.",
        "ult": "[Add-on] With 2+ enemy champions near, the target in CC, an enemy champion below 40% health, or herself below 50% "
               "with one in range, enters her Transcendent State for " + A + "{r_t}s" + E + ": Cultivation of Spirit stays on, Arc "
               "of Judgment becomes a laser, Kanmei's Steps a dash, both cooldowns drop by 80%; she glows gold standing and running.",
    },
    "ko": {
        "skill2": "[확장] 근처에 적 챔피언이 있으면 " + A + "{e_t}초" + E + " 동안 이동 속도 +" + A + "{e_ms}%" + E + ", 적 챔피언에게 달려가면 +" +
                  A + "{e_ms2}%" + E + ". " + O + "초월 상태" + E + ": 돌진 - 붙거나 체력이 낮으면 뒤로, 도망치는 빈사의 적에게는 앞으로.",
        "ult": "[확장] 적 챔피언 2명 이상, 대상이 군중 제어 상태, 체력 40% 이하인 적 챔피언, 또는 자신이 50% 이하로 근접당하면 " + A + "{r_t}초" +
               E + " 동안 초월 상태: 영혼 단련 유지, 심판의 궤적은 광선, 칸메이의 발자취는 돌진, 두 재사용 대기시간 80% 감소; 서 있거나 달릴 때 금빛.",
    },
    "ja": {
        "skill2": "【拡張】近くに敵チャンピオンがいると" + A + "{e_t}秒" + E + "移動速度+" + A + "{e_ms}%" + E + "、敵チャンピオンへ走ると+" + A +
                  "{e_ms2}%" + E + "。" + O + "超越状態" + E + "：ダッシュ。迫られたか瀕死なら後方、逃げる瀕死の敵には前方。",
        "ult": "【拡張】敵チャンピオン2体以上、対象が行動妨害中、体力40%以下の敵チャンピオン、または自身50%以下で接近されたら" + A + "{r_t}秒" + E +
               "超越状態：精神修養が続き、裁きの弧は光線、カンメイの歩みはダッシュ、両方のCDが80%短縮。立ち姿と走りも金色に輝く。",
    },
}


def lp(path):
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
        sys.exit("the main pack's league_yunara differs from build_yunara.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":faith":
        sys.exit("the copy has no league_yunara:faith passive: update this script")
    text = json.dumps(champion)
    for flag in ("league_yunara_re_f", "league_yunara_re_b", "league_yunara_re_go", "league_yunara_r_ok"):
        if flag not in text:
            sys.exit(f"the copy has no {flag}: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in NATIVE.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
