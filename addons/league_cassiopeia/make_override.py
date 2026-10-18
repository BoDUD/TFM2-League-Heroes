"""Build the add-on's copy of Cassiopeia from the main pack (Twin Fang on the poisoned target, Petrifying Gaze by facing).

    python addons/league_cassiopeia/make_override.py

Rebuilds Cassiopeia with tools/kit/build_cassiopeia.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_cassiopeia.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_cassiopeia/override/league_cassiopeia.data_champion and .../text/champion.i18n: the build with
native=1 -
  * everything of the main pack's kit (the fang, Noxious Blast, Miasma, the gaze and its moment);
  * passive = the add-on's league_cassiopeia:venom (it records which way each enemy champion faces) with the numbers of
    P the add-on uses (e_bonus, e_bratio, e_heal, e_heal_m, r_stun, r_slow - checked against src/lib.rs's constants);
  * Q and W also hang the marker league_cassiopeia_poison on what they poison; the fang's bonus and heal are the native
    effect league_cassiopeia:fang (only on a target carrying the marker); the gaze's stun or slow is
    league_cassiopeia:gaze for each enemy in the cone;
  * the attack's and the ult's tooltips point to description.league_cassiopeia.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Cassiopeia changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_cassiopeia")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_cassiopeia as kit  # noqa: E402
import setup_cassiopeia as setup  # noqa: E402

MOD_ID = "league_cassiopeia"
HERO = "league_cassiopeia"
SLOTS = ("attack", "ult")
O, A, R, G, M, E = setup.O, setup.A, setup.R, setup.G, setup.M, setup.E
mag, heal = setup.mag, setup.heal
TEXT = {
    "zh-hans": {
        "attack": "【扩展包】" + O + "双生毒牙" + E + "：甩出毒牙，造成" + mag("e_dmg", "e_ratio") + "魔法伤害；目标中毒时多造成" +
                  mag("e_bonus", "e_bratio") + "并" + G + "回复" + E + heal("e_heal") + "生命。" + O + "优雅蛇行" + E + "：移速成长更高。",
        "ult": "【扩展包】朝面前扇形石化凝视，造成" + mag("r_dmg", "r_ratio") + "魔法伤害：面朝她的敌人" + R + "石化{r_stun}秒" + E + "，背对她的" + R +
               "减速{r_slow}%" + E + "。前方有2个以上敌方英雄或被突进时才放。",
    },
    "zh-hant": {
        "attack": "【擴充包】" + O + "雙生毒牙" + E + "：甩出毒牙，造成" + mag("e_dmg", "e_ratio") + "魔法傷害；目標中毒時多造成" +
                  mag("e_bonus", "e_bratio") + "並" + G + "回復" + E + heal("e_heal") + "生命。" + O + "致命節奏" + E + "：移速成長更高。",
        "ult": "【擴充包】朝面前扇形石化凝視，造成" + mag("r_dmg", "r_ratio") + "魔法傷害：面朝她的敵人" + R + "石化{r_stun}秒" + E + "，背對她的" + R +
               "緩速{r_slow}%" + E + "。前方有2個以上敵方英雄或被突進時才放。",
    },
    "en": {
        "attack": "[Add-on] " + O + "Twin Fang" + E + ": flings a fang for " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  "; on a poisoned target it deals " + mag("e_bonus", "e_bratio") + " more and " + G + "heals her" + E + " " + heal("e_heal") +
                  ". " + O + "Serpentine Grace" + E + ": more move speed per level.",
        "ult": "[Add-on] Gazes in a cone in front of her: " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + "; enemies facing her "
               "are " + R + "petrified for {r_stun}s" + E + ", those turned away " + R + "slowed {r_slow}%" + E + ". Cast with 2+ enemy "
               "champions in front or when dived.",
    },
    "ko": {
        "attack": "[확장] " + O + "쌍독니" + E + ": 독니를 날려 " + mag("e_dmg", "e_ratio") + " 마법 피해; 중독된 대상에게 " +
                  mag("e_bonus", "e_bratio") + " 추가, " + G + "체력 회복" + E + " " + heal("e_heal") + ". " + O + "독사의 품격" + E +
                  ": 레벨당 이동 속도 증가.",
        "ult": "[확장] 앞쪽 부채꼴로 응시: " + mag("r_dmg", "r_ratio") + " 마법 피해; 그녀를 바라보는 적은 " + R + "{r_stun}초 석화" + E +
               ", 등을 돌린 적은 " + R + "{r_slow}% 둔화" + E + ". 앞에 적 챔피언 2명 이상이거나 돌진당할 때 사용.",
    },
    "ja": {
        "attack": "【拡張】" + O + "ツインファング" + E + "：毒牙を放ち" + mag("e_dmg", "e_ratio") + "の魔法ダメージ；毒状態の対象には" +
                  mag("e_bonus", "e_bratio") + "追加し" + G + "体力回復" + E + heal("e_heal") + "。" + O + "妖艶な蛇行" + E + "：移動速度の成長が高い。",
        "ult": "【拡張】前方の扇形に魔眼：" + mag("r_dmg", "r_ratio") + "の魔法ダメージ；こちらを向く敵は" + R + "{r_stun}秒石化" + E +
               "、背を向けた敵は" + R + "{r_slow}%スロウ" + E + "。前方に敵2体以上か突進された時に使う。",
    },
}
CONSTS = {"e_bonus": "E_BONUS", "e_bratio": "E_BRATIO", "e_heal": "E_HEAL", "e_heal_m": "E_HEAL_M", "r_stun": "R_STUN",
          "r_slow": "R_SLOW"}


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
        sys.exit("the main pack's league_cassiopeia differs from build_cassiopeia.P: rebuild it first")
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for key, const in CONSTS.items():
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != p[key]:
            sys.exit(f"src/lib.rs {const} is not P[{key!r}] = {p[key]}: update the add-on")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":venom":
        sys.exit("the copy has no league_cassiopeia:venom passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
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
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in TEXT.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
