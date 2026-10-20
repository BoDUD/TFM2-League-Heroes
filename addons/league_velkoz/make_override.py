"""Build the add-on's copy of Vel'Koz from the main pack (stacks per champion, the split at right angles, the ray's research).

    python addons/league_velkoz/make_override.py

Rebuilds Vel'Koz with tools/kit/build_velkoz.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_velkoz.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_velkoz/override/league_velkoz.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the bolt and the rift every third attack, Plasma Fission, Tectonic Disruption,
    the ray with its picture from his eye, the combo windows);
  * passive = the add-on's league_velkoz:research with the numbers of P it uses (passive.params);
  * every passive stack = league_velkoz:deconstruct (counted on the champion hit), Q's split = league_velkoz:fission
    (two bolts at right angles, q_split_bolt), R's damage lines = league_velkoz:ray;
  * the attack's, skill's and ult's tooltips point to description.league_velkoz.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Vel'Koz changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_velkoz")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_velkoz as kit  # noqa: E402
import setup_velkoz as setup  # noqa: E402

MOD_ID = "league_velkoz"
HERO = "league_velkoz"
SLOTS = ("attack", "skill", "ult")
O, A, R, M, W, E = setup.O, setup.A, setup.R, setup.M, setup.W, setup.E
mag, tru, t = setup.mag, setup.tru, setup.t

TEXT = {
    "zh-hans": {
        "attack": "【扩展包】发射虚空能量。每第3次普攻打开" + O + "虚空裂隙" + E + "，造成" + mag("w_dmg", "w_ratio") + "魔法伤害，随后爆炸再造成" +
                  mag("w_dmg2", "w_ratio2") + "。" + O + "有机体解构" + E + "：技能命中英雄时在他身上叠层，3层时造成" +
                  tru("p_dmg", "p_ratio") + W + "真实伤害" + E + "。",
        "skill": "【扩展包】发射一束等离子，造成" + mag("q_dmg", "q_ratio") + "魔法伤害并减速{q_slow}%。命中后向左右两边分裂，" +
                 "分裂弹造成" + mag("q_sdmg", "q_sratio") + "魔法伤害和减速。",
        "ult": "【扩展包】引导一束射线" + t("{r_t}秒") + "，共造成" + mag("r_dmg", "r_ratio") + "魔法伤害。被他" + O + "有机体解构" + E +
               "研究过的英雄受到" + W + "真实伤害" + E + "。",
    },
    "zh-hant": {
        "attack": "【擴充包】發射虛空能量。每第3次普攻打開" + O + "虛空裂痕" + E + "，造成" + mag("w_dmg", "w_ratio") + "魔法傷害，隨後爆炸再造成" +
                  mag("w_dmg2", "w_ratio2") + "。" + O + "結構毀滅" + E + "：技能命中英雄時在他身上疊層，3層時造成" +
                  tru("p_dmg", "p_ratio") + W + "真實傷害" + E + "。",
        "skill": "【擴充包】發射一束電漿，造成" + mag("q_dmg", "q_ratio") + "魔法傷害並緩速{q_slow}%。命中後向左右兩邊分裂，" +
                 "分裂彈造成" + mag("q_sdmg", "q_sratio") + "魔法傷害和緩速。",
        "ult": "【擴充包】引導一道射線" + t("{r_t}秒") + "，共造成" + mag("r_dmg", "r_ratio") + "魔法傷害。被他" + O + "結構毀滅" + E +
               "研究過的英雄受到" + W + "真實傷害" + E + "。",
    },
    "en": {
        "attack": "[Add-on] Fires void energy. Every third attack opens a " + O + "Void Rift" + E + ": " + mag("w_dmg", "w_ratio") + " " +
                  M + "magic damage" + E + ", then " + mag("w_dmg2", "w_ratio2") + " as it detonates. " + O + "Organic Deconstruction" +
                  E + ": spell hits stack on the champion hit; the third deals " + tru("p_dmg", "p_ratio") + " " + W + "true damage" +
                  E + ".",
        "skill": "[Add-on] Shoots a bolt of plasma for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " and a {q_slow}% "
                 "slow. On hit it splits into two bolts flying off to the sides, each dealing " + mag("q_sdmg", "q_sratio") + " " +
                 M + "magic damage" + E + " and the slow.",
        "ult": "[Add-on] Channels a beam for " + t("{r_t}s") + " that deals " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" +
               E + " in total. Champions he has researched with " + O + "Organic Deconstruction" + E + " take " + W + "true damage" +
               E + ".",
    },
    "ko": {
        "attack": "[확장] 공허 에너지를 발사한다. 3번째 공격마다 " + O + "공허 균열" + E + "을 열어 " + mag("w_dmg", "w_ratio") +
                  " 마법 피해, 폭발하며 " + mag("w_dmg2", "w_ratio2") + ". " + O + "유기물 분해" + E + ": 스킬이 적중한 챔피언에게 "
                  "중첩, 3회 중첩 시 " + tru("p_dmg", "p_ratio") + " " + W + "고정 피해" + E + ".",
        "skill": "[확장] 플라즈마를 발사해 " + mag("q_dmg", "q_ratio") + " 마법 피해와 {q_slow}% 둔화. 적중하면 양옆으로 분열해 각각 " +
                 mag("q_sdmg", "q_sratio") + " 마법 피해와 둔화.",
        "ult": "[확장] " + t("{r_t}초") + " 동안 광선을 정신 집중해 총 " + mag("r_dmg", "r_ratio") + " 마법 피해. " + O + "유기물 분해" +
               E + "로 연구한 챔피언은 " + W + "고정 피해" + E + "를 입는다.",
    },
    "ja": {
        "attack": "【拡張】ヴォイドのエネルギーを放つ。3回目の通常攻撃ごとに" + O + "ヴォイドの裂谷" + E + "を開き" + mag("w_dmg", "w_ratio") +
                  "の魔法ダメージ、爆発で" + mag("w_dmg2", "w_ratio2") + "。" + O + "有機分解" + E + "：スキルが当たったチャンピオンに"
                  "スタック、3スタックで" + tru("p_dmg", "p_ratio") + "の" + W + "確定ダメージ" + E + "。",
        "skill": "【拡張】電離弾を放ち" + mag("q_dmg", "q_ratio") + "の魔法ダメージと{q_slow}%スロウ。命中すると左右に分裂し、それぞれ" +
                 mag("q_sdmg", "q_sratio") + "の魔法ダメージとスロウ。",
        "ult": "【拡張】" + t("{r_t}秒") + "光線を照射し合計" + mag("r_dmg", "r_ratio") + "の魔法ダメージ。" + O + "有機分解" + E +
               "で研究したチャンピオンには" + W + "確定ダメージ" + E + "。",
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
        sys.exit("the main pack's league_velkoz differs from build_velkoz.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":research":
        sys.exit("the copy has no league_velkoz:research passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in TEXT.items() for k, tx in d.items()
            if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in TEXT.items() for k, tx in d.items()})


if __name__ == "__main__":
    main()
