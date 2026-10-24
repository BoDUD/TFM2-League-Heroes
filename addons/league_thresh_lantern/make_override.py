"""Build the add-on's copy of Thresh from the main pack (Dark Passage to the ally in danger, who is pulled to him).

    python addons/league_thresh_lantern/make_override.py [--check]

Reads the main pack's league/champion/league_thresh.data_champion and writes
addons/league_thresh_lantern/override/league_thresh.data_champion and .../text/champion.i18n: the same kit with -
  * the lantern's RandomTarget (AllyNotSelf, 50000, a TargetProjectile league_thresh_w_lantern with the shield) in Q
    swapped for the native effect league_thresh_lantern:throw (it picks the ally, flies the same lantern, gives the same
    shield and pulls him in danger; src/lib.rs's numbers are checked against the kit's);
  * Q's tooltip pointing to description.league_thresh_lantern.skill: the main pack's text with the lantern's ally swapped.
Every other champion stays untouched. Run it again whenever the main pack's Thresh changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_thresh_lantern")
MOD_ID = "league_thresh_lantern"
HERO = "league_thresh"
SLOT = "skill"
TEXT_KEY = "description." + MOD_ID + "." + SLOT
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
SWAPS = {
    "zh-hans": [("为自己和身边一名友方英雄提供", "为自己和最危险的队友提供"), ("持续<#ffb900ff>2.5秒<>。", "持续<#ffb900ff>2.5秒<>，有危险时把他拉到身边。")],
    "zh-hant": [("為自己和身邊一名友方英雄提供", "為自己和最危險的隊友提供"), ("持續<#ffb900ff>2.5秒<>。", "持續<#ffb900ff>2.5秒<>，有危險時把他拉到身邊。")],
    "en": [("he also throws his lantern, giving himself and a nearby allied champion a",
            "his lantern goes to the ally in most danger, pulled to him if threatened; both get a")],
    "ko": [("자신과 주변 아군 챔피언 하나에게", "자신과 가장 위험한 아군(위험하면 끌어옴)에게")],
    "ja": [("自身と近くの味方チャンピオン1体に", "自身と最も危険な味方（危なければ引き寄せる）に")],
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    out = {k: int(re.search(r"pub const " + k + r": \w+ = ([\d_.]+);", src).group(1).replace("_", "").split(".")[0])
           for k in ("REACH", "SPEED", "SHIELD", "SHIELD_AP", "SHIELD_TICKS")}
    out["LANTERN"] = re.search(r'pub const LANTERN: &str = "([^"]+)";', src).group(1)
    return out


def replace(o, match, make, count):
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def build():
    c = consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)

    def is_lantern(o):
        return (o.get("type") == "RandomTarget" and o.get("casting_target") == "AllyNotSelf"
                and c["LANTERN"] in json.dumps(o))

    found = []
    champion[SLOT] = replace(champion[SLOT], is_lantern, lambda o: {"type": "Native", "effect_ref": MOD_ID + ":throw"}, found)
    if len(found) != 1:
        sys.exit(f"Thresh's lantern ({len(found)} RandomTarget AllyNotSelf with {c['LANTERN']}) changed: update this script")
    lantern = found[0]
    shot = lantern["effects"][0]
    shield = [a["effect"] for a in shot["applied_effects"] if a["effect"].get("type") == "Shield"]
    if (lantern["range"], shot["speed"]) != (c["REACH"], c["SPEED"]) or             [(x["amount"], x["ap_ratio"], x["tick"]) for x in shield] != [(c["SHIELD"], c["SHIELD_AP"], c["SHIELD_TICKS"])]:
        sys.exit("the lantern's reach / speed / shield differ from src/lib.rs: update one of them")
    champion[SLOT]["description"] = "#asset/base/text/champion?" + TEXT_KEY
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        t = tab["description"][HERO][SLOT]
        for old, new in SWAPS[lang]:
            if old not in t:
                sys.exit(f"{lang} {HERO}.{SLOT}: the main pack's text changed ({old!r} not found): update this script")
            t = t.replace(old, new)
        texts[lang] = LEAD[lang] + t
        if shown_length(texts[lang]) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang}: tooltip too long ({shown_length(texts[lang])} > {TOOLTIP_MAX[lang]})")
    text = {lang: {"description": {MOD_ID: {SLOT: texts[lang]}}} for lang in main_text}
    return champion, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    champion, text = build()
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps(text, ensure_ascii=False, indent=2) + "\n"}
    if a.check:
        stale = [os.path.relpath(p, ROOT) for p, t in files.items()
                 if not os.path.exists(lp(p)) or open(lp(p), encoding="utf-8").read().replace("\r\n", "\n") != t]
        print(MOD_ID + ":", "stale " + ", ".join(stale) if stale else "up to date")
        sys.exit(1 if stale else 0)
    for p, t in files.items():
        os.makedirs(lp(os.path.dirname(p)), exist_ok=True)
        with open(lp(p), "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    print("wrote", ", ".join(os.path.relpath(p, ROOT) for p in files))


if __name__ == "__main__":
    main()
