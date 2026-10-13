"""Build the add-on's copy of Mordekaiser from the main pack (Realm of Death on the carry's real stats, Indestructible
from the fight's damage).

    python addons/league_mordekaiser/make_override.py

Rebuilds Mordekaiser with tools/kit/build_mordekaiser.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_mordekaiser.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_mordekaiser/override/league_mordekaiser.data_champion and .../text/champion.i18n: the build with
native=1 -
  * everything of the main pack's kit (Darkness Rise, Q, E stay data);
  * passive league_mordekaiser:revenant (params: the tether, the kill's heal and keep, W's shares, cap and heal);
  * R calls league_mordekaiser:realm (the carry in reach, its real stats stolen, the taunt) in place of the data's curse;
  * W calls league_mordekaiser:indestructible (the shield stored from the damage) in place of the data's fixed shield;
  * E's (W's) and R's tooltips point to description.league_mordekaiser_realm.* with the add-on's wording, so the
    tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Mordekaiser changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_mordekaiser")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_mordekaiser as kit  # noqa: E402
import setup_mordekaiser as setup  # noqa: E402

TEXT_ID = "league_mordekaiser_realm"        # the text's key (the hero's own id is league_mordekaiser)
HERO = "league_mordekaiser"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
G_, E, APi, A = setup.G_, setup.E, setup.APi, setup.A
# lang -> slot -> (old text the main pack has, new text) ; the lead marks the add-on's copy
SWAP = {
    "zh-hans": {
        "skill2": ("获得" + G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}%护盾" + E + "，护盾仍在时回复" + G_ + "{w_heal}" + E +
                   " + " + APi + G_ + "{w_heal_ap}%生命" + E,
                   "获得按造成和受到的伤害攒起的" + G_ + "护盾" + E + "（至多最大生命30%），快结束时按剩余护盾回复" + G_ + "40%" + E),
        "ult": (None, "把射程内攻击+法强最高的敌方英雄拖进死亡领域" + A + "{r_t}秒" + E + "：两人离开战场单挑，偷取其{r_steal}%攻击、法强、护甲、魔抗和生命；其死在领域里则回复" + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%生命" + E + "。")},
    "zh-hant": {
        "skill2": ("獲得" + G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}%護盾" + E + "，護盾仍在時回復" + G_ + "{w_heal}" + E +
                   " + " + APi + G_ + "{w_heal_ap}%生命" + E,
                   "獲得按造成和受到的傷害攢起的" + G_ + "護盾" + E + "（至多最大生命30%），快結束時按剩餘護盾回復" + G_ + "40%" + E),
        "ult": (None, "把射程內攻擊+法強最高的敵方英雄拖進死亡領域" + A + "{r_t}秒" + E + "：兩人離開戰場單挑，偷取其{r_steal}%攻擊、法強、護甲、魔抗和生命；其死在領域裡則回復" + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%生命" + E + "。")},
    "en": {
        "skill2": ("a " + G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}% shield" + E + "; if it still holds, he heals " + G_ +
                   "{w_heal}" + E + " + " + APi + G_ + "{w_heal_ap}%" + E,
                   "a " + G_ + "shield" + E + " stored from the damage he dealt and took (up to 30% max health); near its end "
                   "he heals " + G_ + "40%" + E + " of what is left"),
        "ult": (None, "Drags the enemy champion in reach with the most attack + ability power into his realm for " + A + "{r_t}s" + E + ": the two leave the battlefield to duel, and he steals {r_steal}% of its attack, ability power, armour, magic resistance and health. If it dies in the realm he heals " + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%" + E + ".")},
    "ko": {
        "skill2": (G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}% 보호막" + E + ", 보호막이 남아 있으면 " + G_ + "{w_heal}" + E + " + " +
                   APi + G_ + "{w_heal_ap}%" + E + " 회복",
                   "준 피해와 받은 피해로 쌓인 " + G_ + "보호막" + E + "(최대 체력 30%까지), 끝날 때 남은 보호막의 " + G_ + "40%" + E + " 회복"),
        "ult": (None, "사거리 안 공격력+주문력이 가장 높은 적 챔피언을 " + A + "{r_t}초" + E + " 동안 죽음의 세계로 끌고 가 1:1, 공격력·주문력·방어력·마법 저항력·체력 {r_steal}% 강탈. 그 안에서 처치하면 " + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%" + E + " 회복.")},
    "ja": {
        "skill2": (G_ + "{w_sh}" + E + " + " + APi + G_ + "{w_ap}%のシールド" + E + "、残っていれば" + G_ + "{w_heal}" + E + " + " + APi +
                   G_ + "{w_heal_ap}%" + E + "回復",
                   "与えた・受けたダメージで溜めた" + G_ + "シールド" + E + "（最大体力30%まで）、終わり際に残量の" + G_ + "40%" + E + "回復"),
        "ult": (None, "射程内で攻撃力+魔力が最も高い敵チャンピオンを" + A + "{r_t}秒" + E + "死の国へ引きずり込み一騎打ち、攻撃力・魔力・物防・魔防・体力の{r_steal}%を奪う。中で倒すと" + G_ + "{r_kill}" + E + " + " + APi + G_ + "{r_kill_ap}%" + E + "回復。")},
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
        sys.exit("the main pack's league_mordekaiser differs from build_mordekaiser.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if "league_mordekaiser:realm" not in json.dumps(champion["ult"]) or "passive" not in champion:
        sys.exit("the copy does not call the add-on: update this script")
    for slot in ("skill2", "ult"):
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = setup.values(p)
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot, (old, new) in swaps.items():
            src = setup.TEXT[lang][slot]
            if old is None:                       # the whole text replaced
                old = src
            if old not in src:
                sys.exit(f"{lang}.{slot}: {old!r} is not in setup_mordekaiser.TEXT")
            texts[lang][slot] = (LEAD[lang] + src.replace(old, new)).format(**values)
    long = {f"{lang}.{slot}": setup.shown_length(t) for lang, d in texts.items() for slot, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
