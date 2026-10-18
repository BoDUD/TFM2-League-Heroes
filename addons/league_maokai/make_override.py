"""Build the add-on's copy of Maokai from the main pack (Sap Magic healing % max health and readied by enemy skills,
saplings in brush).

    python addons/league_maokai/make_override.py

Rebuilds Maokai with tools/kit/build_maokai.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_maokai.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_maokai/override/league_maokai.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (Q, W, the sapling, R and their moments);
  * passive = the add-on's league_maokai:sap_magic with the numbers of P;
  * the readied attack lays league_maokai_sap_on (3 ticks) instead of the data heal (the add-on heals % max health);
  * the sapling's blast has a second, bigger one read while league_maokai_e_brush (the add-on: the sapling in brush);
  * the attack's tooltip points to description.league_maokai.attack with the add-on's wording, a key of the add-on's own
    id, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Maokai changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_maokai")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_maokai as kit  # noqa: E402
import setup_maokai as setup  # noqa: E402

MOD_ID = "league_maokai"
HERO = "league_maokai"
SLOTS = ("attack",)
M, O, A, R, G, E = setup.M, setup.O, setup.A, setup.R, setup.G, setup.E
# the add-on's attack text (the main pack's wording with the % max-health heal, the enemy-skill readiness, brush)
ATTACK = {
    "zh-hans": "【扩展包】巨臂砸击。" + O + "吸元秘术" + E + "：技能命中或被敌方技能打中后，下一次普攻额外造成" + M + "{p_hp}%最大生命" + E +
               "魔法伤害，" + G + "回复{lo}%~{hi}%最大生命" + E + "（随等级）。" + O + "树苗投掷" + E + "：每" + A + "{e_cd}秒" + E +
               "扔一棵，敌人靠近就爆炸：" + setup.mag("e_dmg", "e_ap") + "魔法伤害，" + R + "减速{e_slow}%" + E + "；在草丛里更强。",
    "zh-hant": "【擴充包】巨臂砸擊。" + O + "魔法樹液" + E + "：技能命中或被敵方技能打中後，下一次普攻額外造成" + M + "{p_hp}%最大生命" + E +
               "魔法傷害，" + G + "回復{lo}%~{hi}%最大生命" + E + "（隨等級）。" + O + "扭曲樹精" + E + "：每" + A + "{e_cd}秒" + E +
               "扔一棵，敵人靠近就爆炸：" + setup.mag("e_dmg", "e_ap") + "魔法傷害，" + R + "緩速{e_slow}%" + E + "；在草叢裡更強。",
    "en": "[Add-on] Arm blow. " + O + "Sap Magic" + E + ": after his skills hit or an enemy skill hits him, his next attack deals " +
          M + "{p_hp}% of his max health" + E + " more as magic damage and " + G + "heals {lo}-{hi}% of his max health" + E + " (by level). " +
          O + "Sapling Toss" + E + ": every " + A + "{e_cd}s" + E + " a sapling that bursts when an enemy comes near for " +
          setup.mag("e_dmg", "e_ap") + " " + M + "magic damage" + E + " and a " + R + "{e_slow}% slow" + E + "; stronger in brush.",
    "ko": "[확장] 거대한 팔로 내리치기. " + O + "마법 흡수" + E + ": 스킬 적중 또는 적 스킬에 맞은 뒤 다음 공격이 " + M + "최대 체력의 {p_hp}%" + E +
          " 마법 피해를 더하고 " + G + "최대 체력의 {lo}~{hi}% 회복" + E + "(레벨 비례). " + O + "묘목 던지기" + E + ": " + A + "{e_cd}초" + E +
          "마다 묘목, 적이 다가오면 폭발해 " + setup.mag("e_dmg", "e_ap") + "의 " + M + "마법 피해" + E + "와 " + R + "{e_slow}% 둔화" + E +
          ", 수풀에서 더 강함.",
    "ja": "【拡張】巨腕の一撃。" + O + "魔樹液" + E + "：スキル命中か敵スキルを受けた後の次の攻撃が" + M + "最大体力の{p_hp}%" + E +
          "の魔法ダメージを追加し" + G + "最大体力の{lo}~{hi}%回復" + E + "（レベル比例）。" + O + "苗木投げ" + E + "：" + A + "{e_cd}秒" + E +
          "ごとに苗木、敵が近づくと爆発：" + setup.mag("e_dmg", "e_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "スロウ{e_slow}%" + E +
          "、茂みでより強力。",
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
        sys.exit("the main pack's league_maokai differs from build_maokai.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":sap_magic":
        sys.exit("the copy has no league_maokai:sap_magic passive: update this script")
    if '"heal_type": "Caster"' in json.dumps(champion):
        sys.exit("the copy still heals in data: update build_maokai.build(native=1)")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), lo=f"{p['p_heal_lo'] / 10:g}", hi=f"{p['p_heal_hi'] / 10:g}")
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
