"""Build the add-on's copy of Udyr from the main pack (Iron Mantle by his health, the whole-body stances).

    python addons/league_udyr/make_override.py

Rebuilds Udyr with tools/kit/build_udyr.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_udyr.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_udyr/override/league_udyr.data_champion and .../text/champion.i18n: the build with native -
  * everything of the main pack's kit, but no ability lays Iron Mantle any more;
  * passive league_udyr:mantle (Iron Mantle when his health falls under w_hp%; params from P);
  * the attack's tooltip points to description.league_udyr_addon.attack with the add-on's wording, so the tooltip in
    game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Udyr changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_udyr")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_udyr as kit  # noqa: E402
import setup_udyr as setup  # noqa: E402

TEXT_ID = "league_udyr_addon"      # the text's key (the hero's own id is league_udyr)
HERO = "league_udyr"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, G, A, E = setup.O, setup.G, setup.A, setup.E
grn = setup.grn
# the attack's whole text in the add-on (Iron Mantle reads his health here)
ATTACK = {
    "zh-hans": "拳击目标。" + O + "众灵纽带" + E + "：放技能后两次攻击攻速+{p_as}%。" + O + "坚铁甲胄" + E + "：生命低于{w_hp}%时获得" +
               grn("w_sh", "w_sh_r") + "护盾，之后两次攻击各回复" + grn("w_heal", "w_heal_r") + "生命（每" + A + "{w_icd}秒" + E + "至多一次）。",
    "zh-hant": "拳擊目標。" + O + "人神一體" + E + "：施放技能後兩次攻擊攻速+{p_as}%。" + O + "鋼筋鐵骨" + E + "：生命低於{w_hp}%時獲得" +
               grn("w_sh", "w_sh_r") + "護盾，之後兩次攻擊各回復" + grn("w_heal", "w_heal_r") + "生命（每" + A + "{w_icd}秒" + E + "至多一次）。",
    "en": "A punch. " + O + "Bridge Between" + E + ": after each ability his next two attacks gain +{p_as}% attack speed. " + O +
          "Iron Mantle" + E + ": falling under {w_hp}% health shields him for " + grn("w_sh", "w_sh_r") + " and his next two attacks "
          "heal him " + grn("w_heal", "w_heal_r") + " each (once every " + A + "{w_icd}s" + E + " at most).",
    "ko": "주먹으로 공격. " + O + "가교" + E + ": 스킬 사용 후 다음 두 번의 공격 속도 +{p_as}%. " + O + "강철 갑옷" + E + ": 체력이 {w_hp}% "
          "미만이 되면 " + grn("w_sh", "w_sh_r") + " 보호막, 다음 두 번의 공격마다 체력 " + grn("w_heal", "w_heal_r") + " 회복 (" + A +
          "{w_icd}초" + E + "에 한 번).",
    "ja": "拳で攻撃。" + O + "精霊の繋ぎ手" + E + "：スキル後の2回の通常攻撃は攻撃速度+{p_as}%。" + O + "鉄の外皮" + E + "：体力が{w_hp}%未満に"
          "なると" + grn("w_sh", "w_sh_r") + "のシールド、続く2回の攻撃で体力" + grn("w_heal", "w_heal_r") + "回復（" + A + "{w_icd}秒" + E +
          "に1回まで）。",
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
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
        sys.exit("the main pack's league_udyr differs from build_udyr.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != "league_udyr:mantle":
        sys.exit("the copy does not call the add-on: update this script")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    v = {k: p[k] for k in ("p_as", "w_hp", "w_sh", "w_sh_r", "w_heal", "w_heal_r")}
    v["w_icd"] = setup.secs(p["w_icd"])
    texts = {lang: {"attack": (LEAD[lang] + ATTACK[lang]).format(**v)} for lang in LEAD}
    long = {f"{lang}.attack": setup.shown_length(LEAD[lang] + ATTACK[lang]) for lang in LEAD
            if setup.shown_length(LEAD[lang] + ATTACK[lang]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
