"""Build the add-on's copy of Xayah from the main pack (three feathers on one enemy root him).

    python addons/league_xayah_feathers/make_override.py [--check]

Reads the main pack's league/champion/league_xayah.data_champion and writes
addons/league_xayah_feathers/override/league_xayah.data_champion and .../text/champion.i18n: the same kit with -
  * every recall hit's counting ladder (SwitchByBuff league_xayah_rh2 -> Bind 75 / rh1 -> rh2 / rh1, counted on Xayah)
    swapped for the native effect league_xayah_feathers:hit (it counts on the champion struck, src/lib.rs);
  * Q's tooltip pointing to description.league_xayah_feathers.skill with the root rule swapped.
Every other champion stays untouched. Run it again whenever the main pack's Xayah changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_xayah_feathers")
MOD_ID = "league_xayah_feathers"
HERO = "league_xayah"
SLOT = "skill"
TEXT_KEY = "description." + MOD_ID + "." + SLOT
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
SWAPS = {
    "zh-hans": ("一次收回命中英雄第3次起", "同一个英雄被一次收回的3根羽毛打中时"),
    "zh-hant": ("一次收回命中英雄第3次起", "同一個英雄被一次收回的3根羽毛打中時"),
    "en": ("From the third champion hit of one recall, <#ef5350ff>roots<>", "A champion struck by 3 Feathers of one recall is <#ef5350ff>rooted<>"),
    "ko": ("한 번의 회수에서 세 번째 챔피언 적중부터", "한 번의 회수에서 깃털 3개에 맞은 챔피언은"),
    "ja": ("1回の回収で3回目以降のチャンピオン命中は", "1回の回収で羽根3本に当たったチャンピオンは"),
}


def replace(o, match, make, count):
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def build():
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)

    def is_count(o):
        if not (o.get("type") == "SwitchByBuff" and o.get("buff_name") == "league_xayah_rh2"):
            return False
        hit, rest = o["effect_buff"], o["effect_none"]
        return ([e.get("type") for e in hit.get("effects", [])][:1] == ["Bind"] and rest.get("buff_name") == "league_xayah_rh1")

    n = []
    for slot in ("attack", "skill", "skill2", "ult"):
        champion[slot] = replace(champion[slot], is_count, lambda o: {"type": "Native", "effect_ref": MOD_ID + ":hit"}, n)
    if len(n) != 27 or any(o["effect_buff"]["effects"][0]["duration"] != 75 for o in n):
        sys.exit(f"Xayah's recall counters ({len(n)}, roots 75 ticks) changed in the main pack: update this script")
    left = re.findall(r'"buff_name": "(league_xayah_rh[12])"', json.dumps(champion))
    if left:
        sys.exit(f"recall counters left in the copy: {left}")
    champion[SLOT]["description"] = "#asset/base/text/champion?" + TEXT_KEY
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        old, new = SWAPS[lang]
        t = tab["description"][HERO][SLOT]
        if old not in t:
            sys.exit(f"{lang} {HERO}.{SLOT}: the main pack's text changed ({old!r} not found): update this script")
        texts[lang] = LEAD[lang] + t.replace(old, new)
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
