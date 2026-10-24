"""Build the add-on's copy of Samira from the main pack (she walks while Inferno Trigger spins).

    python addons/league_samira_r/make_override.py [--check]

Reads the main pack's league/champion/league_samira.data_champion and writes
addons/league_samira_r/override/league_samira.data_champion and .../text/champion.i18n: the same kit with -
  * the passive league_samira_r:walk (it walks her while src/lib.rs's R_ON is on her; R itself is the main pack's);
  * R's tooltip pointing to description.league_samira_r.ult: the main pack's text with "spins in place" swapped.
Every other champion stays untouched. Run it again whenever the main pack's Samira changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_samira_r")
MOD_ID = "league_samira_r"
HERO = "league_samira"
TEXT_KEY = "description." + MOD_ID + ".ult"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
SWAPS = {
    "zh-hans": ("原地旋转连射", "旋转连射并走向残血的敌人"),
    "zh-hant": ("原地旋轉連射", "旋轉連射並走向殘血的敵人"),
    "en": ("spins in place firing", "spins firing as she walks at the weakest enemy"),
    "ko": ("제자리에서 회전하며", "가장 약한 적에게 걸어가며 회전해"),
    "ja": ("その場で回転し", "弱った敵へ歩きながら回転し"),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def build():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    r_on = re.search(r'pub const R_ON: &str = "([^"]+)";', src).group(1)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Samira has a passive in the main pack now: update this script")
    ult = json.dumps(champion["ult"])
    if f'"name": "{r_on}"' not in ult or '"name": "ult", "tick": 120' not in ult:
        sys.exit(f"R no longer spins 120 ticks with {r_on} on her: update src/lib.rs")
    champion["passive"] = {"passive_ref": MOD_ID + ":walk", "params": {}}
    champion["ult"]["description"] = "#asset/base/text/champion?" + TEXT_KEY
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        old, new = SWAPS[lang]
        t = tab["description"][HERO]["ult"]
        if old not in t:
            sys.exit(f"{lang} {HERO}.ult: the main pack's text changed ({old!r} not found): update this script")
        texts[lang] = LEAD[lang] + t.replace(old, new)
        if shown_length(texts[lang]) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang}: tooltip too long ({shown_length(texts[lang])} > {TOOLTIP_MAX[lang]})")
    text = {lang: {"description": {MOD_ID: {"ult": texts[lang]}}} for lang in main_text}
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
