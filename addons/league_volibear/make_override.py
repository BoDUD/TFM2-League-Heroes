"""Build the add-on's copy of Volibear from the main pack (chain lightning, marked maul, tower silence).

    python addons/league_volibear/make_override.py

Rebuilds Volibear with tools/kit/build_volibear.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_volibear.data_champion byte for byte (so the copy never drifts from the shipped kit),
checks src/lib.rs's constants against P, and writes addons/league_volibear/override/league_volibear.data_champion and
.../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the stacks, the maul's timing, Thundering Smash, Sky Splitter, Stormbringer);
  * the five-stack lightning is league_volibear:storm, the maul's champion hit league_volibear:maul, R's landing also
    runs league_volibear:stormbringer;
  * the attack's and the ult's tooltips point to description.league_volibear.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Volibear changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_volibear")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_volibear as kit  # noqa: E402
import setup_volibear as setup  # noqa: E402

MOD_ID = "league_volibear"
HERO = "league_volibear"
SLOTS = ("attack", "ult")
O, A, R, G, M, E = setup.O, setup.A, setup.R, setup.G, setup.M, setup.E
mag, phys, heal = setup.mag, setup.phys, setup.heal
TEXT = {
    "zh-hans": {
        "attack": "【扩展包】" + O + "狂雷渐起" + E + "：命中叠攻速，5层后攻击放闪电，目标和最近{p_n}个敌人受" +
                  mag("p_dmg", "p_ap") + "魔法伤害。" + O + "暴怒撕咬" + E + "：每" + A + "{w_cd}秒" + E + "攻击变撕咬，造成" + phys("w_dmg", "w_ratio") +
                  "物理伤害并标记；再咬同一人+{w2}%，回复" + heal("w_heal", "w_heal_ad") + "+" + G + "{w_heal_miss}%已损生命" + E + "。",
        "ult": "【扩展包】跃向敌方英雄砸地，周围敌人受" + phys("r_dmg", "r_ratio") + "物理伤害并" + R + "减速{r_slow}%" + E + "，附近敌方防御塔" + R +
               "失效{r_tower_t}秒" + E + "；之后" + A + "{r_form}秒" + E + "内生命+{r_hp}、攻击距离增加。",
    },
    "zh-hant": {
        "attack": "【擴充包】" + O + "無情風暴" + E + "：命中疊攻速，5層後攻擊放閃電，目標和最近{p_n}個敵人受" +
                  mag("p_dmg", "p_ap") + "魔法傷害。" + O + "狂熊撕咬" + E + "：每" + A + "{w_cd}秒" + E + "攻擊變撕咬，造成" + phys("w_dmg", "w_ratio") +
                  "物理傷害並標記；再咬同一人+{w2}%，回復" + heal("w_heal", "w_heal_ad") + "+" + G + "{w_heal_miss}%已損生命" + E + "。",
        "ult": "【擴充包】躍向敵方英雄砸地，周圍敵人受" + phys("r_dmg", "r_ratio") + "物理傷害並" + R + "緩速{r_slow}%" + E + "，附近敵方防禦塔" + R +
               "失效{r_tower_t}秒" + E + "；之後" + A + "{r_form}秒" + E + "內生命+{r_hp}、攻擊距離增加。",
    },
    "en": {
        "attack": "[Add-on] " + O + "The Relentless Storm" + E + ": hits stack attack speed; at 5 his attacks strike the "
                  "target and the {p_n} nearest enemies for " + mag("p_dmg", "p_ap") + " " + M + "magic damage" +
                  E + ". " + O + "Frenzied Maul" + E + ": every " + A + "{w_cd}s" + E + " an attack is a maul for " + phys("w_dmg", "w_ratio") +
                  " physical damage, marking; a second on him deals {w2}% more, heals " + heal("w_heal", "w_heal_ad") + " + " + G +
                  "{w_heal_miss}% missing health" + E + ".",
        "ult": "[Add-on] Leaps onto an enemy champion: enemies around take " + phys("r_dmg", "r_ratio") + " physical damage and are " + R +
               "slowed {r_slow}%" + E + ", nearby enemy towers are " + R + "disabled {r_tower_t}s" + E + "; for " + A + "{r_form}s" + E +
               " he has +{r_hp} health and more attack range.",
    },
    "ko": {
        "attack": "[확장] " + O + "무자비한 폭풍" + E + ": 공격과 스킬이 공격 속도 중첩(중첩당 {p_as}%, 5회); 5회면 번개가 대상과 가장 가까운 적 {p_n}명에게 " +
                  mag("p_dmg", "p_ap") + " 마법 피해. " + O + "광란의 상처" + E + ": " + A + "{w_cd}초" + E + "마다 할퀴기 " + phys("w_dmg", "w_ratio") +
                  " 물리 피해와 표식; 같은 대상 재공격 시 피해 {w2}% 증가, " + heal("w_heal", "w_heal_ad") + "+" + G + "잃은 체력 {w_heal_miss}%" + E + " 회복.",
        "ult": "[확장] 적 챔피언에게 도약해 주변 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해와 " + R + "{r_slow}% 둔화" + E + ", 근처 적 포탑 " + R +
               "{r_tower_t}초 무력화" + E + "; " + A + "{r_form}초" + E + " 동안 체력 +{r_hp}, 사거리 증가.",
    },
    "ja": {
        "attack": "【拡張】" + O + "無慈悲の嵐" + E + "：攻撃・スキルで攻速+{p_as}%（5つまで）；5つで稲妻が対象と最寄りの敵{p_n}体に" +
                  mag("p_dmg", "p_ap") + "の魔法ダメージ。" + O + "激昂の斬撃" + E + "：" + A + "{w_cd}秒" + E + "毎に噛みつき" + phys("w_dmg", "w_ratio") +
                  "の物理ダメージとマーク；同じ相手は{w2}%増し、" + heal("w_heal", "w_heal_ad") + "+" + G + "失った体力の{w_heal_miss}%" + E + "回復。",
        "ult": "【拡張】敵チャンピオンへ跳びかかり周りの敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージと" + R + "{r_slow}%スロウ" + E + "、近くの敵タワーは" +
               R + "{r_tower_t}秒無力化" + E + "；" + A + "{r_form}秒" + E + "体力+{r_hp}、射程増加。",
    },
}

CONSTS = {k: k.upper() for k in ("p_dmg", "p_ap", "p_r", "w_dmg", "w_ratio", "w_hp", "w2", "w_mark_t", "w_heal", "w_heal_ad",
                                  "w_heal_miss", "r_tower_r", "r_tower_t", "r_range", "r_r")}
P_N = 4                         # src/lib.rs P_N: the lightning's targets besides the one attacked (League: 4)


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
        sys.exit("the main pack's league_volibear differs from build_volibear.P: rebuild it first")
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for key, const in list(CONSTS.items()) + [("p_n", "P_N")]:
        want = P_N if key == "p_n" else p[key]
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != want:
            sys.exit(f"src/lib.rs {const} is not {key} = {want}: update the add-on")
    champion = kit.build(dict(p, native=1))
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values.update({"p_n": P_N, "w_heal_miss": p["w_heal_miss"], "r_tower_t": setup.secs(p["r_tower_t"])})
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in TEXT.items() for k, t in d.items()
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
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in TEXT.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
