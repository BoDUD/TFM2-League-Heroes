"""Build the add-on's copy of Xin Zhao from the main pack (Crescent Guard blocks the damage from afar).

    python addons/league_xinzhao_guard/make_override.py

Rebuilds Xin Zhao with tools/kit/build_xinzhao.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_xinzhao.data_champion byte for byte (so the copy never drifts from the shipped kit),
and writes addons/league_xinzhao_guard/override/league_xinzhao.data_champion and .../text/champion.i18n:
the same kit with three changes -
  * R's guard buff (league_xinzhao_r_guard, 3 s) loses its 40% damage reduction: it only keeps the glow and the timing;
  * passive = the add-on's league_xinzhao_guard:guard with {"far": r_far}: while the guard is on, the damage from an
    attacker farther than r_far (League's 450 units, R's own sweep radius) is given back as it lands;
  * R's tooltip points to description.league_xinzhao_guard.ult (a "test build" lead, so the tooltip in game shows
    whether the override took): the main pack's R text with the last sentence (the reduction) replaced.
Every other champion stays untouched. Run it again whenever the main pack's Xin Zhao changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_xinzhao_guard")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_xinzhao as kit  # noqa: E402
import setup_xinzhao as setup  # noqa: E402

MOD_ID = "league_xinzhao_guard"
TEXT_KEY = "description.league_xinzhao_guard.ult"
A, E = setup.A, setup.E
# lang -> (the lead, where the main pack's last sentence starts, the new last sentence)
NATIVE = {
    "zh-hans": ("【远程免伤测试版】", "之后", "之后" + A + "{r_t}秒" + E + "内，横扫范围外的敌人对他造成的伤害全部免疫。"),
    "zh-hant": ("【遠程免傷測試版】", "之後", "之後" + A + "{r_t}秒" + E + "內，橫掃範圍外的敵人對他造成的傷害全部免疫。"),
    "en": ("[Test build: far damage blocked] ", " For ", " For " + A + "{r_t}s" + E +
           " afterwards he ignores all damage from enemies beyond the sweep's reach."),
    "ko": ("[원거리 면역 테스트판] ", " 이후 ", " 이후 " + A + "{r_t}초" + E + " 동안 휩쓸기 범위 밖의 적에게서 받는 피해를 무시합니다."),
    "ja": ("【遠距離無効テスト版】", "その後", "その後" + A + "{r_t}秒" + E + "間、薙ぎ払いの範囲外の敵からのダメージを無効。"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_xinzhao.data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_xinzhao differs from build_xinzhao.P: rebuild it first")
    if p["r_far"] != p["r_rad"]:
        sys.exit("the tooltip says 'beyond the sweep's reach': r_far must equal r_rad, or reword NATIVE")
    champion = kit.build(p, native=True)
    if "damaged_reduce" in json.dumps(champion["ult"]):
        sys.exit("the guard still reduces the damage: update this script")
    if "league_xinzhao_r_guard" not in json.dumps(champion["ult"]):
        sys.exit("R no longer puts on league_xinzhao_r_guard (the buff the add-on looks for): update this script")
    champion["ult"]["description"] = "#asset/base/text/champion?" + TEXT_KEY

    values = setup.values(p)
    texts = {}
    for lang, (lead, cut, tail) in NATIVE.items():
        ult = setup.TEXT[lang]["ult"]
        if ult.count(cut) != 1:
            sys.exit(f"{lang}: the main pack's R text changed (cut {cut!r} not found once): update NATIVE")
        texts[lang] = (lead + ult.split(cut)[0] + tail).format(**values)
    long = {lang: setup.shown_length(t) for lang, t in texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_xinzhao.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no test-build text for %s" % sorted(missing))
    text = {lang: {"description": {MOD_ID: {"ult": texts[lang]}}} for lang in main_text}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- guard reduction dropped, passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
