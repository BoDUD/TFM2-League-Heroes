"""Build the add-on's copy of Syndra from the main pack (Force of Will lifts a minion or monster when no sphere is counted).

    python addons/league_syndra/make_override.py

Rebuilds Syndra with tools/kit/build_syndra.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_syndra.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_syndra/override/league_syndra.data_champion and .../text/champion.i18n: build(p, native=True) -
  * W marks the cast for the passive (league_syndra_w_grab on her, league_syndra_w_at on the unit thrown at) and, when
    the passive lifted a minion or monster (league_syndra_w_unit on her), throws a hidden lob that leaves no sphere;
  * passive = league_syndra:grab with w_rel, w_fly, w_grab_r and w_lift_speed as its params;
  * skill2's tooltip (description.league_syndra.skill2, merged over the main text) names the lifted minion or monster.
Every other champion stays untouched. Run it again whenever the main pack's Syndra or her text changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_syndra")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_syndra as kit  # noqa: E402
import setup_syndra as setup  # noqa: E402

MOD_ID = "league_syndra"
HERO = "league_syndra"
# lang -> (the main text's words, the add-on's)
LIFT = {
    "zh-hans": ("把法球掷向敌方英雄", "把法球（没有时举起附近的小兵或野怪，大小龙除外）掷向敌方英雄"),
    "zh-hant": ("把星體擲向敵方英雄", "把星體（沒有時舉起附近的小兵或野怪，大小龍除外）擲向敵方英雄"),
    "en": ("throws a sphere at an enemy champion",
           "throws a sphere (with none, the nearest minion or monster - never a dragon) at an enemy champion"),
    "ko": ("적 챔피언에게 구체를 던져", "적 챔피언에게 구체(없으면 근처 미니언·몬스터, 용 제외)를 던져"),
    "ja": ("スフィアを敵チャンピオンに投げ", "スフィア（なければ近くのミニオンかモンスター、ドラゴン除く）を敵チャンピオンに投げ"),
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
        sys.exit("the main pack's league_syndra differs from build_syndra.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":grab":
        sys.exit("the copy has no league_syndra:grab passive: update build_syndra.py")
    flat = json.dumps(champion["skill2"])
    for name in ("league_syndra_w_grab", "league_syndra_w_at", "league_syndra_w_unit"):
        if name not in flat:
            sys.exit(f"{name} is no longer in the copy's W: update src/lib.rs")
    for slot in ("o1", "o2", "o3", "o4"):
        if f'"name": "league_syndra_{slot}"' not in json.dumps(champion["skill"]):
            sys.exit(f"the sphere count league_syndra_{slot} changed: update src/lib.rs (SLOTS)")

    texts = {}
    for lang, (d, _) in setup.texts(p).items():
        old, new = LIFT[lang]
        if d["skill2"].count(old) != 1:
            sys.exit(f"{lang}: the main pack's W text changed ({old!r} not found once): update LIFT")
        texts[lang] = d["skill2"].replace(old, new)
    long = {lang: setup.shown_length(t) for lang, t in texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {HERO: {"skill2": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], champion["passive"]["params"])
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
