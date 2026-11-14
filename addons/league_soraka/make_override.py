"""Build the add-on's copy of Soraka from the main pack (Wish heals 50% more on allies below 40% health).

    python addons/league_soraka/make_override.py [--check]

Reads the main pack's league/champion/league_soraka.data_champion and writes
addons/league_soraka/override/league_soraka.data_champion and .../text/champion.i18n: the same kit with -
  * the add-on's native effect league_soraka:wish put FIRST in Wish's circle round the map (before the main pack's
    Heal, so it reads each ally's health before he is healed): an ally below LOW_HP% of his maximum health gets
    BONUS% of the main pack's heal more (src/lib.rs; HEAL / HEAL_AP there must be the main pack's numbers);
  * the ult's tooltip pointing to description.league_soraka_addon.ult: the main pack's text with one sentence added.
Every other champion stays untouched. Run it again whenever the main pack's Soraka changes (--check: compare only, CI).
"""
import argparse
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_soraka")
MOD_ID = "league_soraka"
HERO = "league_soraka"
TEXT_ID = "league_soraka_addon"       # the texts' key (the hero's own id is league_soraka)
SLOT = "ult"
NATIVE = {"type": "Native", "effect_ref": MOD_ID + ":wish"}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
A, G, E = "<#ffb900ff>", "<#6aff55ff>", "<>"
MORE = {
    "zh-hans": "生命低于" + A + "{low}%" + E + "的多回复" + G + "{bonus}%" + E + "。",
    "zh-hant": "生命低於" + A + "{low}%" + E + "的多回復" + G + "{bonus}%" + E + "。",
    "en": " Those below " + A + "{low}%" + E + " health are healed " + G + "{bonus}%" + E + " more.",
    "ko": " 체력이 " + A + "{low}%" + E + " 미만인 대상은 " + G + "{bonus}%" + E + " 더 회복합니다.",
    "ja": "体力" + A + "{low}%" + E + "未満の対象は" + G + "{bonus}%" + E + "多く回復。",
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    return {k: int(re.search(r"pub const %s: usize = (\d+);" % k, src).group(1)) for k in ("HEAL", "HEAL_AP", "LOW_HP", "BONUS")}


def heal_circles(node, out):
    """Every RangeEffect whose own effects hold a Heal on allies."""
    if isinstance(node, dict):
        if node.get("type") == "RangeEffect" and any(isinstance(e, dict) and e.get("type") == "Heal"
                                                     for e in node.get("effects", [])):
            out.append(node)
        for v in node.values():
            heal_circles(v, out)
    elif isinstance(node, list):
        for v in node:
            heal_circles(v, out)
    return out


def build():
    k = rust_consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Soraka has a passive in the main pack now: update this script")
    champion = copy.deepcopy(champion)
    circles = heal_circles(champion[SLOT]["effect"], [])
    if len(circles) != 1 or circles[0].get("target") != "AllyChampion":
        sys.exit("the main pack's Wish is no longer one circle of heals on allied champions: update this script")
    heal = next(e for e in circles[0]["effects"] if e.get("type") == "Heal")
    if (heal.get("amount"), heal.get("ap_ratio")) != (k["HEAL"], k["HEAL_AP"]):
        sys.exit(f"the main pack's Wish heals {heal.get('amount')} + {heal.get('ap_ratio')}% AP, src/lib.rs says "
                 f"{k['HEAL']} + {k['HEAL_AP']}%: update HEAL / HEAL_AP")
    circles[0]["effects"].insert(0, NATIVE)
    champion[SLOT]["description"] = "#asset/base/text/champion?description." + TEXT_ID + "." + SLOT

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        t = LEAD[lang] + tab["description"][HERO][SLOT] + MORE[lang].format(low=k["LOW_HP"], bonus=k["BONUS"])
        if shown_length(t) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
        texts[lang] = t
    for lang, t in texts.items():
        print(f"{lang} {SLOT}:{shown_length(t)}/{TOOLTIP_MAX[lang]}")
    i18n = {lang: {"description": {TEXT_ID: {SLOT: texts[lang]}}} for lang in main_text}
    return [(os.path.join(ADDON, "override", HERO + ".data_champion"), dumps(champion)),
            (os.path.join(ADDON, "text", "champion.i18n"), dumps(i18n))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="only compare the copy with the files (CI)")
    a = ap.parse_args()
    out = build()
    if a.check:
        bad = []
        for path, text in out:
            try:
                with open(lp(path), encoding="utf-8", newline="") as f:
                    have = f.read()
            except FileNotFoundError:
                have = None
            if have is None or have.replace("\r\n", "\n") != text.replace("\r\n", "\n"):
                bad.append(os.path.relpath(path, ROOT))
        if bad:
            sys.exit(f"out of date (python addons/{MOD_ID}/make_override.py): " + ", ".join(bad))
        print(f"{MOD_ID}: the copy is up to date")
        return
    for path, text in out:
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(path)


if __name__ == "__main__":
    main()
