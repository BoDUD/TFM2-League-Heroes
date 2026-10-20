"""Build the add-on's copy of Zyra from the main pack (seeds on the ground, the plants they grow, enraged by her R).

    python addons/league_zyra/make_override.py

Rebuilds Zyra with tools/kit/build_zyra.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_zyra.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_zyra/override/league_zyra.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the seed, Deadly Spines with its Thorn Spitter, Grasping Roots with its Vine
    Lasher, Stranglethorns enraging the plants);
  * passive = the add-on's league_zyra:garden with the numbers of P it uses (passive.params);
  * Q, E and R lay a 2-tick mark on their target as the lob leaves her (q_aim / e_aim / r_aim): where they land;
  * the views of the add-on's own pictures: the seeds on the ground (s_seed), the plants' spit (t_spit);
  * the attack's, skill's and skill2's tooltips point to description.league_zyra.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Zyra changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_zyra")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_zyra as kit  # noqa: E402
import setup_zyra as setup  # noqa: E402

MOD_ID = "league_zyra"
HERO = "league_zyra"
SLOTS = ("attack", "skill", "skill2")
O, A, R, M, E = setup.O, setup.A, setup.R, setup.M, setup.E
mag, t = setup.mag, setup.t

TEXT = {
    "zh-hans": {
        "attack": "【扩展包】甩出一颗荆棘种子。" + O + "荆棘花园" + E + "：每" + t("{s_cd}秒") + "在身边掉一颗种子（留" + t("{s_life}秒") +
                  "），参与击杀时马上掉一颗；Q、E 落在种子旁边会让种子长成植物，植物先打英雄，伤害随等级成长。",
        "skill": "【扩展包】地面炸出棘刺，造成" + mag("q_dmg", "q_ratio") + "魔法伤害。落点和旁边的种子长成" + O + "荆棘喷射者" + E +
                 "，向敌人吐刺。",
        "skill2": "【扩展包】贯穿地面的藤蔓造成" + mag("e_dmg", "e_ratio") + "魔法伤害并" + R + "禁锢" + E + t("{e_root}秒") +
                  "。落点和藤蔓经过的种子长成" + O + "藤蔓鞭击者" + E + "，抽打并减速。",
    },
    "zh-hant": {
        "attack": "【擴充包】甩出一顆荊棘種子。" + O + "荊棘花園" + E + "：每" + t("{s_cd}秒") + "在身邊掉一顆種子（留" + t("{s_life}秒") +
                  "），參與擊殺時馬上掉一顆；Q、E 落在種子旁邊會讓種子長成植物，植物先打英雄，傷害隨等級成長。",
        "skill": "【擴充包】地面炸出棘刺，造成" + mag("q_dmg", "q_ratio") + "魔法傷害。落點和旁邊的種子長成" + O + "棘刺噴吐草" + E +
                 "，向敵人吐刺。",
        "skill2": "【擴充包】貫穿地面的藤蔓造成" + mag("e_dmg", "e_ratio") + "魔法傷害並" + R + "定身" + E + t("{e_root}秒") +
                  "。落點和藤蔓經過的種子長成" + O + "棘蔓鞭笞草" + E + "，抽打並緩速。",
    },
    "en": {
        "attack": "[Add-on] Flings a thorn seed. " + O + "Garden of Thorns" + E + ": a seed falls near her every " + t("{s_cd}s") +
                  " (it lasts " + t("{s_life}s") + ") and one at once on a takedown; Q and E landing near seeds grow them into "
                  "plants that strike champions first, harder with her level.",
        "skill": "[Add-on] Spines burst from the ground for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + ". The "
                 "seed there and the seeds near it grow " + O + "Thorn Spitters" + E + " that spit at enemies.",
        "skill2": "[Add-on] Vines run through the ground for " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + ", " +
                  R + "rooting" + E + " for " + t("{e_root}s") + ". The seeds on their way grow " + O + "Vine Lashers" + E +
                  " that lash and slow.",
    },
    "ko": {
        "attack": "[확장] 가시 씨앗을 던진다. " + O + "가시 정원" + E + ": " + t("{s_cd}초") + "마다 주변에 씨앗이 떨어지고(" +
                  t("{s_life}초") + " 유지) 처치 관여 시 즉시 하나; Q와 E가 씨앗 근처에 떨어지면 식물로 자라 챔피언을 먼저 공격하며 레벨에 따라 강해진다.",
        "skill": "[확장] 지면에서 가시가 폭발해 " + mag("q_dmg", "q_ratio") + " 마법 피해. 그 자리와 근처의 씨앗이 " + O + "가시 발사 꽃" + E +
                 "으로 자라 적에게 가시를 쏜다.",
        "skill2": "[확장] 지면을 뚫는 덩굴로 " + mag("e_dmg", "e_ratio") + " 마법 피해와 " + t("{e_root}초") + " " + R + "속박" + E +
                  ". 지나간 자리의 씨앗이 " + O + "덩굴 채찍손" + E + "으로 자라 공격하며 둔화시킨다.",
    },
    "ja": {
        "attack": "【拡張】トゲの種を投げる。" + O + "茨の楽園" + E + "：" + t("{s_cd}秒") + "ごとに近くに種が落ち（" + t("{s_life}秒") +
                  "残る）、キル関与で即座に1つ；QとEが種の近くに当たると植物に育ち、チャンピオンを優先して攻撃し、レベルで強くなる。",
        "skill": "【拡張】地面からトゲが弾け" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。その場と近くの種が" + O + "棘吹草" + E +
                 "に育ち、敵にトゲを吐く。",
        "skill2": "【拡張】地中を伸びるツタが" + mag("e_dmg", "e_ratio") + "の魔法ダメージと" + t("{e_root}秒") + R + "移動不能" + E +
                  "。通り道の種が" + O + "棘鞭草" + E + "に育ち、攻撃してスロウを与える。",
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
        sys.exit("the main pack's league_zyra differs from build_zyra.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":garden":
        sys.exit("the copy has no league_zyra:garden passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values["s_cd"] = setup.secs(p["s_cd"])
    values["s_life"] = setup.secs(p["s_life"])
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
