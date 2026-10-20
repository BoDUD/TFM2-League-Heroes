"""Build the add-on's copy of Warwick from the main pack (Eternal Hunger and Blood Hunt by health, the combos).

    python addons/league_warwick/make_override.py

Rebuilds Warwick with tools/kit/build_warwick.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_warwick.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_warwick/override/league_warwick.data_champion and .../text/champion.i18n: the build with native -
  * everything of the main pack's kit;
  * every claw strike (the attack, Q's bite, R's three) calls league_warwick:hunger (the heal by his health) instead of
    the main pack's flat heal, and the attack no longer adds the main pack's w_hunt;
  * passive league_warwick:hunt (Blood Hunt by the champions' health; params from P);
  * the attack's tooltip points to description.league_warwick_addon.attack with the add-on's wording, so the tooltip in
    game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Warwick changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_warwick")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_warwick as kit  # noqa: E402
import setup_warwick as setup  # noqa: E402

TEXT_ID = "league_warwick_addon"      # the text's key (the hero's own id is league_warwick)
HERO = "league_warwick"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, M, A, E = setup.O, setup.M, setup.A, setup.E
# the attack's whole text in the add-on (the passive and W read health here)
ATTACK = {
    "zh-hans": "挥爪。" + O + "血之饥渴" + E + "：爪击附带" + M + "{p_dmg}" + E + "魔法伤害；生命低于{p_half}%时回复同样多的生命，低于{p_quarter}%时三倍。" +
               O + "鲜血追猎" + E + "：附近有生命低于{w_half}%的敌方英雄时攻速+{w_as}%、移速+{w_ms}%，低于{w_quarter}%时三倍。",
    "zh-hant": "揮爪。" + O + "永恆飢渴" + E + "：爪擊附帶" + M + "{p_dmg}" + E + "魔法傷害；生命低於{p_half}%時回復同樣多的生命，低於{p_quarter}%時三倍。" +
               O + "血跡獵蹤" + E + "：附近有生命低於{w_half}%的敵方英雄時攻速+{w_as}%、移速+{w_ms}%，低於{w_quarter}%時三倍。",
    "en": "A claw swipe. " + O + "Eternal Hunger" + E + ": his claws deal " + M + "{p_dmg}" + E + " bonus magic damage and heal that much "
          "below {p_half}% health, three times below {p_quarter}%. " + O + "Blood Hunt" + E + ": with an enemy champion under "
          "{w_half}% health near, +{w_as}% attack speed and +{w_ms}% move speed, three times under {w_quarter}%.",
    "ko": "할퀴기. " + O + "끝없는 허기" + E + ": 할퀴기가 " + M + "{p_dmg}" + E + " 추가 마법 피해, 체력 {p_half}% 미만이면 그만큼 회복, "
          "{p_quarter}% 미만이면 3배. " + O + "피의 사냥" + E + ": 체력 {w_half}% 미만 적 챔피언이 근처에 있으면 공격 속도 +{w_as}%, "
          "이동 속도 +{w_ms}%, {w_quarter}% 미만이면 3배.",
    "ja": "爪で引き裂く。" + O + "永遠の渇き" + E + "：爪が" + M + "{p_dmg}" + E + "の追加魔法ダメージ、体力{p_half}%未満なら同量回復、"
          "{p_quarter}%未満なら3倍。" + O + "血の追跡" + E + "：体力{w_half}%未満の敵チャンピオンが近くにいると攻撃速度+{w_as}%、"
          "移動速度+{w_ms}%、{w_quarter}%未満なら3倍。",
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
        sys.exit("the main pack's league_warwick differs from build_warwick.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != "league_warwick:hunt":
        sys.exit("the copy does not call the add-on: update this script")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    v = {k: p[k] for k in ("p_dmg", "p_half", "p_quarter", "w_as", "w_ms", "w_half", "w_quarter")}
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
