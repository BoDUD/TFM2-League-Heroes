"""Build the add-on's copy of Wukong from the main pack (Stone Skin regenerating a share of his max health).

    python addons/league_wukong/make_override.py

Rebuilds Wukong with tools/kit/build_wukong.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_wukong.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_wukong/override/league_wukong.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (Crushing Blow, Nimbus Strike, the clone, Cyclone and their moments);
  * passive = the add-on's league_wukong:stone with the numbers of P (p_pct, p_every);
  * Stone Skin's five stacks keep their armour but carry no data regeneration (the add-on heals % max health);
  * the attack's tooltip points to description.league_wukong.attack with the add-on's wording, a key of the add-on's own
    id, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Wukong changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_wukong")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_wukong as kit  # noqa: E402
import setup_wukong as setup  # noqa: E402

MOD_ID = "league_wukong"
HERO = "league_wukong"
SLOTS = ("attack",)
O, A, R, G, E = setup.O, setup.A, setup.R, setup.G, setup.E
# the add-on's attack text (the main pack's wording with Stone Skin's % max-health regeneration)
ATTACK = {
    "zh-hans": "【扩展包】金箍棒横扫。" + O + "金刚不坏" + E + "：打中英雄叠1层（最多5层），每层护甲+{p_def}；每5秒" + G + "回复{pct}%最大生命" + E +
               "，每层再多{pct}%（叠满{top}%）。" + O + "粉碎打击" + E + "：每" + A + "{q_t}秒" + E + "下一次普攻伸长棒子，多造成" +
               setup.phys("q_dmg", "q_ratio") + "物理伤害，目标" + R + "护甲-{q_shred}%" + E + "，持续" + A + "{q_shred_t}秒" + E + "。",
    "zh-hant": "【擴充包】金箍棒橫掃。" + O + "仙山石猴" + E + "：打中英雄疊1層（最多5層），每層護甲+{p_def}；每5秒" + G + "回復{pct}%最大生命" + E +
               "，每層再多{pct}%（疊滿{top}%）。" + O + "定海神兵" + E + "：每" + A + "{q_t}秒" + E + "下一次普攻伸長棒子，多造成" +
               setup.phys("q_dmg", "q_ratio") + "物理傷害，目標" + R + "護甲-{q_shred}%" + E + "，持續" + A + "{q_shred_t}秒" + E + "。",
    "en": "[Add-on] Staff strikes. " + O + "Stone Skin" + E + ": each hit on a champion adds a stack (5 at most), +{p_def} armour each; every 5s "
          "he " + G + "regenerates {pct}% of his max health" + E + ", {pct}% more a stack ({top}% at five). " + O + "Crushing Blow" + E + ": every " +
          A + "{q_t}s" + E + " his next attack reaches farther and deals " + setup.phys("q_dmg", "q_ratio") + " physical damage more, " + R +
          "-{q_shred}% armour" + E + " on the target for " + A + "{q_shred_t}s" + E + ".",
    "ko": "[확장] 여의봉 공격. " + O + "바위 피부" + E + ": 챔피언 적중 시 중첩(최대 5), 중첩당 방어력 +{p_def}; 5초마다 " + G + "최대 체력의 {pct}% 회복" + E +
          ", 중첩당 {pct}% 추가(5중첩 {top}%). " + O + "파쇄격" + E + ": " + A + "{q_t}초" + E + "마다 다음 공격의 사거리가 늘고 " +
          setup.phys("q_dmg", "q_ratio") + " 물리 피해 추가, 대상 " + R + "방어력 -{q_shred}%" + E + " " + A + "{q_shred_t}초" + E + ".",
    "ja": "【拡張】如意棒で攻撃。" + O + "岩の皮膚" + E + "：チャンピオン命中でスタック（最大5）、毎スタック物理防御+{p_def}；5秒毎に" + G +
          "最大体力の{pct}%回復" + E + "、スタック毎に{pct}%追加。" + O + "強棒打" + E + "：" + A + "{q_t}秒" + E +
          "毎に次の通常攻撃が伸び" + setup.phys("q_dmg", "q_ratio") + "の物理ダメージを追加、対象の" + R + "物理防御-{q_shred}%" + E + "（" + A +
          "{q_shred_t}秒" + E + "）。",
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
        sys.exit("the main pack's league_wukong differs from build_wukong.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":stone":
        sys.exit("the copy has no league_wukong:stone passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), pct=f"{p['p_pct'] / 100:g}", top=f"{p['p_pct'] * 6 / 100:g}")
    texts = {lang: {"attack": t.format(**values)} for lang, t in ATTACK.items()}
    long = {f"{lang}.attack": setup.shown_length(ATTACK[lang]) for lang in ATTACK
            if setup.shown_length(ATTACK[lang]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.attack": f"{setup.shown_length(ATTACK[lang])}/{setup.TOOLTIP_MAX[lang]}"
                              for lang in ATTACK})


if __name__ == "__main__":
    main()
