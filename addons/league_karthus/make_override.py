"""Build the add-on's copy of Karthus from the main pack (Death Defied's spirit).

    python addons/league_karthus/make_override.py

Rebuilds Karthus with tools/kit/build_karthus.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_karthus.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_karthus/override/league_karthus.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * passive league_karthus:death_defied (params: the spirit's p_t ticks) and the spirit's picture (view_buffs p_spirit);
  * the attack's tooltip points to description.league_karthus_spirit.attack with the add-on's wording (the main pack's
    Wall of Pain, then Death Defied), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Karthus changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_karthus")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_karthus as kit  # noqa: E402
import setup_karthus as setup  # noqa: E402

TEXT_ID = "league_karthus_spirit"      # the text's key (the hero's own id is league_karthus)
HERO = "league_karthus"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, E = setup.O, setup.A, setup.E
PASSIVE = {
    "zh-hans": O + "死亡契约" + E + "：受到致命伤害时化为灵体" + A + "{p_t}秒" + E + "，敌人选不中、不受伤害，照常放技能，之后倒下。",
    "zh-hant": O + "無視死亡！" + E + "：受到致命傷害時化為靈體" + A + "{p_t}秒" + E + "，敵人選不中、不受傷害，照常施放技能，之後倒下。",
    "en": O + "Death Defied" + E + ": a lethal blow turns him into a spirit for " + A + "{p_t}s" + E +
          " - untargetable, taking no damage, still casting - before he falls.",
    "ko": O + "죽음 극복" + E + ": 치명상을 입으면 " + A + "{p_t}초" + E + " 동안 영혼이 되어 대상 지정 불가, 피해 없음, 스킬 사용 가능. 이후 쓰러짐.",
    "ja": O + "怨嗟の叫び" + E + "：致命傷を受けると" + A + "{p_t}秒" + E + "霊体になり、対象指定不可・ダメージ無効でスキルを使い続け、その後倒れる。",
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
        sys.exit("the main pack's league_karthus differs from build_karthus.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_karthus:death_defied":
        sys.exit("the copy does not call the add-on: update this script")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    v = setup.values(p)
    v["p_t"] = setup.secs(p["p_t"])
    texts = {lang: {"attack": (LEAD[lang] + setup.TEXT[lang]["attack"] + t).format(**v)} for lang, t in PASSIVE.items()}
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
