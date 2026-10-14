"""Build the add-on's copy of Sion from the main pack (Glory in Death's zombie, Soul Furnace from every kill).

    python addons/league_sion/make_override.py

Rebuilds Sion with tools/kit/build_sion.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_sion.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_sion/override/league_sion.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, minus the attack's own kill check (the add-on counts every kill);
  * passive league_sion:glory (params: k_u / k_c health a kill, the zombie's z_t ticks, z_as attack speed, z_vamp);
  * the attack's tooltip points to description.league_sion_glory.attack with the add-on's wording (Glory in Death and
    Soul Furnace as League has them), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Sion changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_sion")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_sion as kit  # noqa: E402
import setup_sion as setup  # noqa: E402

TEXT_ID = "league_sion_glory"          # the text's key (the hero's own id is league_sion)
HERO = "league_sion"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, G, E = setup.O, setup.A, setup.G, setup.E
ATTACK = {
    "zh-hans": O + "死亡荣耀" + E + "：每条命第一次受到致命伤害时变成亡灵" + A + "{z_t}秒" + E + "，生命回满后持续流失，攻速+{z_as}%、吸血{z_vamp}%，不能放技能。" +
               O + "灵魂熔炉" + E + "被动：每击杀一个单位永久+" + G + "{k_u}" + E + "最大生命值，英雄+" + G + "{k_c}" + E + "，阵亡不丢。",
    "zh-hant": O + "光榮戰死" + E + "：每條命第一次受到致命傷害時變成亡靈" + A + "{z_t}秒" + E + "，生命回滿後持續流失，攻速+{z_as}%、吸血{z_vamp}%，不能施放技能。" +
               O + "魂魄熔爐" + E + "被動：每擊殺一個單位永久+" + G + "{k_u}" + E + "最大生命值，英雄+" + G + "{k_c}" + E + "，陣亡不丟。",
    "en": O + "Glory in Death" + E + ": the first lethal blow of each life raises him as a zombie for " + A + "{z_t}s" + E +
          " - full health draining away, +{z_as}% attack speed, {z_vamp}% life steal, no abilities. " + O + "Soul Furnace" + E +
          " passive: each kill grants " + G + "{k_u}" + E + " maximum health for good, a champion " + G + "{k_c}" + E + ", kept through death.",
    "ko": O + "영광스러운 죽음" + E + ": 목숨마다 처음 치명상을 입으면 " + A + "{z_t}초" + E + " 동안 좀비로 부활 - 체력이 가득 찬 뒤 줄어들며 공격 속도 +{z_as}%, 생명력 흡수 {z_vamp}%, 스킬 사용 불가. " +
          O + "영혼의 용광로" + E + " 기본 지속 효과: 처치마다 최대 체력 " + G + "{k_u}" + E + " 영구 증가, 챔피언 " + G + "{k_c}" + E + ", 사망해도 유지.",
    "ja": O + "名誉ある死" + E + "：命ごとに最初の致命傷で" + A + "{z_t}秒" + E + "ゾンビとして復活、体力全快後に減り続け攻撃速度+{z_as}%、ライフスティール{z_vamp}%、スキル不可。" +
          O + "魂の炉心" + E + "自動効果：キルごとに最大体力+" + G + "{k_u}" + E + "（チャンピオン+" + G + "{k_c}" + E + "）、死亡後も維持。",
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
        sys.exit("the main pack's league_sion differs from build_sion.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_sion:glory" or "k_a" in json.dumps(champion["attack"]):
        sys.exit("the copy does not call the add-on: update this script")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    values = {k: p[k] for k in ("k_u", "k_c", "z_as", "z_vamp")}
    values["z_t"] = setup.secs(p["z_t"])
    texts = {lang: {"attack": (LEAD[lang] + t).format(**values)} for lang, t in ATTACK.items()}
    long = {f"{lang}.attack": setup.shown_length(d["attack"]) for lang, d in texts.items()
            if setup.shown_length(d["attack"]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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


if __name__ == "__main__":
    main()
