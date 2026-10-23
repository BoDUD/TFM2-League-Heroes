"""Build the add-on's copy of Zac from the main pack (Cell Division's revive).

    python addons/league_zac/make_override.py

Rebuilds Zac with tools/kit/build_zac.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_zac.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_zac/override/league_zac.data_champion and .../text/champion.i18n: the build with native=1 -
  * passive league_zac:split (params: split_t, split_cd, split_hp);
  * the split shown by the data (split_go / split_end flags, a 2-tick watch hung once a life by his attack);
  * the attack's tooltip points to description.league_zac_addon.attack with the add-on's wording, so the tooltip in game
    shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Zac changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_zac")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_zac as kit  # noqa: E402
import setup_zac as setup  # noqa: E402

TEXT_ID = "league_zac_addon"         # the texts' key (the hero's own id is league_zac)
HERO = "league_zac"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
A, O, G, E = setup.A, setup.O, setup.G, setup.E
mag, tr = setup.mag, setup.tr
TEXT = {
    "zh-hans": {
        "attack": "拳击。" + O + "不稳定物质" + E + "：冷却好时普攻炸开，周围敌人受" + mag("w_dmg", "w_ap") + "魔法伤害，英雄再受" +
                  tr("最大生命{w_pct}%") + "。" + O + "细胞分裂" + E + "：吃掉掉下的黏液" + G + "回复" + E + mag("b_heal", "b_heal_ap") +
                  "；致命伤害时化成一滩" + A + "{split_t}秒" + E + "（最大生命{split_hp}%），被打掉才阵亡。冷却" + A + "{split_cd}秒" + E + "。",
    },
    "zh-hant": {
        "attack": "拳擊。" + O + "自體爆破" + E + "：冷卻好時普攻炸開，周圍敵人受" + mag("w_dmg", "w_ap") + "魔法傷害，英雄再受" +
                  tr("最大生命{w_pct}%") + "。" + O + "組織分裂" + E + "：吃掉掉下的黏液" + G + "回復" + E + mag("b_heal", "b_heal_ap") +
                  "；致命傷害時化成一灘" + A + "{split_t}秒" + E + "（最大生命{split_hp}%），被打掉才陣亡。冷卻" + A + "{split_cd}秒" + E + "。",
    },
    "en": {
        "attack": "A goo punch. " + O + "Unstable Matter" + E + ": a ready attack bursts for " + mag("w_dmg", "w_ap") +
                  " magic damage round him, " + tr("+{w_pct}% max health") + " to champions. " + O + "Cell Division" + E +
                  ": a shed blob " + G + "heals" + E + " " + mag("b_heal", "b_heal_ap") + "; lethal damage melts him into a "
                  "puddle for " + A + "{split_t}s" + E + " ({split_hp}% max health) - only destroying it kills him. Cooldown " +
                  A + "{split_cd}s" + E + ", kept through death.",
    },
    "ko": {
        "attack": "점액 주먹. " + O + "불안정 물질" + E + ": 준비되면 기본 공격이 터져 주변 적에게 " + mag("w_dmg", "w_ap") +
                  " 마법 피해, 챔피언은 " + tr("최대 체력의 {w_pct}%") + " 추가. " + O + "세포 분열" + E + ": 떨어진 점액을 먹으면 " +
                  mag("b_heal", "b_heal_ap") + " " + G + "회복" + E + "; 치명적인 피해를 받으면 " + A + "{split_t}초" + E +
                  " 동안 웅덩이가 됨(최대 체력의 {split_hp}%), 웅덩이가 파괴되어야 사망. 재사용 " + A + "{split_cd}초" + E + ".",
    },
    "ja": {
        "attack": "スライムの拳。" + O + "スライムクラッシュ" + E + "：通常攻撃が弾け周囲の敵に" + mag("w_dmg", "w_ap") +
                  "の魔法ダメージ、英雄にはさらに" + tr("最大体力の{w_pct}%") + "。" + O + "はぐれスライム" + E + "：拾ったスライムで" +
                  mag("b_heal", "b_heal_ap") + G + "回復" + E + "。致死ダメージで" + A + "{split_t}秒" + E + "水たまりになり（最大体力の"
                  "{split_hp}%）、壊されると死亡。CD" + A + "{split_cd}秒" + E + "。",
    },
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
        sys.exit("the main pack's league_zac differs from build_zac.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_zac:split" or "split_go" not in json.dumps(champion):
        sys.exit("the copy does not call the add-on: update this script")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    values = setup.values(p)
    values.update(split_t=setup.secs(p["split_t"]), split_cd=setup.secs(p["split_cd"]), split_hp=p["split_hp"])
    texts = {lang: {k: (LEAD[lang] + t[k]).format(**values) for k in t} for lang, t in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(LEAD[lang] + TEXT[lang][k]) for lang in TEXT for k in TEXT[lang]
            if setup.shown_length(LEAD[lang] + TEXT[lang][k]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    for lang in TEXT:
        print(lang, " ".join(f"{k}:{setup.shown_length(LEAD[lang] + TEXT[lang][k])}/{setup.TOOLTIP_MAX[lang]}"
                             for k in TEXT[lang]))
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
