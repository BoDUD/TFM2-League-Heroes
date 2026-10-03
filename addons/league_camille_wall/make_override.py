"""Build the add-on's copy of Camille from the main pack (test build v0).

    python addons/league_camille_wall/make_override.py

Reads league/champion/league_camille.data_champion and league/text/champion.i18n and writes
addons/league_camille_wall/override/league_camille.data_champion and .../text/champion.i18n:
the same kit with two changes -
  * E's tooltip points to description.league_camille_wall.skill2 (the main text with a
    "wall-hook test build" lead), so the tooltip in game shows whether the override took;
  * each E throw (engage and escape) first calls the add-on's native probe, which only logs.
Run it again whenever the main pack's Camille changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_camille_wall")
MOD_ID = "league_camille_wall"
TEXT_KEY = "description.league_camille_wall.skill2"
LEADS = {
    "zh-hans": "【钩墙测试版】",
    "zh-hant": "【鉤牆測試版】",
    "en": "[Wall-hook test build] ",
    "ko": "[벽 갈고리 테스트판] ",
    "ja": "【壁フック試験版】",
}


def walk(node, out):
    """Every effect list in the tree, depth first."""
    if isinstance(node, dict):
        for value in node.values():
            walk(value, out)
    elif isinstance(node, list):
        if node and all(isinstance(x, dict) and "type" in x for x in node):
            out.append(node)
        for value in node:
            walk(value, out)


def contains(node, effect_type):
    return json.dumps(node).find('"type": "%s"' % effect_type) >= 0


def throw_lists(skill2):
    """The effect lists that start E's throw: they play CasterAnimation skill2."""
    lists = []
    walk(skill2["effect"], lists)
    return [
        effects
        for effects in lists
        if any(e.get("type") == "CasterAnimation" and e.get("name") == "skill2" for e in effects)
    ]


def main():
    src = os.path.join(ROOT, "league", "champion", "league_camille.data_champion")
    with open(src, encoding="utf-8") as f:
        champion = json.load(f)
    skill2 = champion["skill2"]
    skill2["description"] = "#asset/base/text/champion?" + TEXT_KEY

    probes = {"engage": 0, "escape": 0}
    for effects in throw_lists(skill2):
        if contains(effects, "MoveBack"):
            kind = "escape"
        elif contains(effects, "Stun"):
            kind = "engage"
        else:
            sys.exit("a throw that neither stuns nor flees: the main pack's E changed, update this script")
        effects.insert(0, {"type": "Native", "effect_ref": "%s:probe_%s" % (MOD_ID, kind)})
        probes[kind] += 1
    if probes != {"engage": 1, "escape": 1}:
        sys.exit("expected one engage and one escape throw, found %s" % probes)

    out = os.path.join(ADDON, "override", "league_camille.data_champion")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(os.path.join(ROOT, "league", "text", "champion.i18n"), encoding="utf-8") as f:
        main_text = json.load(f)
    text = {}
    for lang, lead in LEADS.items():
        original = main_text[lang]["description"]["league_camille"]["skill2"]
        text[lang] = {"description": {MOD_ID: {"skill2": lead + original}}}
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(os.path.dirname(out_text), exist_ok=True)
    with open(out_text, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(text, ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), probes)


if __name__ == "__main__":
    main()
