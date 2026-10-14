"""Build the add-on's copy of Bard from the main pack (Magical Journey's exit clear of the map's rocks).

    python addons/league_bard/make_override.py

Rebuilds Bard with tools/kit/build_bard.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_bard.data_champion (so the copy never drifts from the shipped kit), and writes
addons/league_bard/override/league_bard.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit but E: skill2 is the shrine only, and the add-on's passive league_bard:door
    opens the door itself, only on a wall (League's corridor through terrain) - away when dived or hurt, after a hurt
    enemy champion behind a wall - and moves him and the allies near the door through it;
  * skill2's tooltip points to description.league_bard.skill2 with the add-on's wording, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Bard changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_bard")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_bard as kit  # noqa: E402
import setup_bard as setup  # noqa: E402

MOD_ID = "league_bard"
HERO = "league_bard"
# lang -> (the lead, the main pack's Magical Journey rule in the skill2 text, the add-on's)
NATIVE = {
    "zh-hans": ("【穿墙门】", "被敌人近身时开门，带身边的友方英雄远离，",
                "在附近的墙上开门穿到另一边：被近身或残血时往己方撤，墙后有残血敌人就追，或去支援交战的队友，带上身边的友方英雄，"),
    "zh-hant": ("【穿牆門】", "被敵人近身時開門，帶身邊的友方英雄遠離，",
                "在附近的牆上開門穿到另一邊：被近身或殘血時往己方撤，牆後有殘血敵人就追，或去支援交戰的隊友，帶上身邊的友方英雄，"),
    "en": ("[Wall door] ", "when enemies close in, opens a door and takes nearby allied champions away with him,",
           "opens a door through a nearby wall: home when dived or hurt, after a hurt foe behind it, or to an ally "
           "in a fight, with nearby allies,"),
    "ko": ("[벽 문] ", "적이 붙으면 문을 열어 주변 아군 챔피언과 함께 멀어지고",
           "근처 벽에 문을 열어 넘어가: 붙거나 약하면 아군 쪽으로, 벽 뒤 약한 적은 추격, 싸우는 아군은 지원, 주변 아군과 함께하며"),
    "ja": ("【壁の扉】", "敵に詰められると扉を開き、近くの味方と離脱、",
           "近くの壁に扉を開け向こう側へ：詰められるか瀕死で自陣へ、壁裏の弱った敵は追い、交戦中の味方へ援護、近くの味方と共に、"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        shipped = json.load(f)
    if kit.build(p) != shipped:
        sys.exit("the main pack's league_bard differs from build_bard.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":door":
        sys.exit("the copy has no league_bard:door passive: update this script")
    champion["skill2"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".skill2"

    values = setup.values(p)
    texts = {}
    for lang, (lead, old, new) in NATIVE.items():
        t = setup.TEXT[lang]["skill2"]
        if t.count(old) != 1:
            sys.exit(f"{lang} skill2: the main pack's text changed ({old!r} not found once): update NATIVE")
        texts[lang] = {"skill2": (lead + t.replace(old, new)).format(**values)}
    long = {f"{lang}.skill2": setup.shown_length(d["skill2"]) for lang, d in texts.items()
            if setup.shown_length(d["skill2"]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.skill2": f"{setup.shown_length(d['skill2'])}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in texts.items()})


if __name__ == "__main__":
    main()
