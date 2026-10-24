"""Build the add-on's copies from the main pack (effects that ask whether the target carries a mark).

    python addons/league_marks/make_override.py [--check]

Reads the main pack's kits and writes addons/league_marks/override/<hero>.data_champion and .../text/champion.i18n:
  * league_diana: Lunar Rush's start no longer reads her own league_diana_moonlight (any Q hit); it marks its target
    with src/lib.rs's DIANA_ASK and, 2 ticks later, reads DIANA_YES (the add-on raises it when that target carries Q's
    league_diana_moon_mark) to queue the second dash (league_diana_e_again, as the main pack); passive league_marks:diana.
Changed tooltips point to description.league_marks.<name>_<slot>. Run it again whenever one of them changes in the main
pack (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_marks")
MOD_ID = "league_marks"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
M, E = "<#a974ffff>", "<>"
TEXT = {
    ("league_diana", "skill2"): {
        "zh-hans": ("有" + M + "月光" + E + "时立刻再冲一次（优先英雄）", "目标带" + M + "月光" + E + "时再冲一次"),
        "zh-hant": ("有" + M + "月光精華" + E + "時立刻再衝一次（優先英雄）", "目標帶" + M + "月光精華" + E + "時再衝一次"),
        "en": ("with " + M + "Moonlight" + E + " up she dashes", "if the target bears " + M + "Moonlight" + E + " she dashes"),
        "ko": (M + "달빛" + E + "이 있으면", "대상에게 " + M + "달빛" + E + "이 있으면"),
        "ja": (M + "月光" + E + "があれば", "対象に" + M + "月光" + E + "があれば"),
    },
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
    return {k: re.search(k + r': &str = "([^"]+)"', src).group(1) for k in ("DIANA_MOON", "DIANA_ASK", "DIANA_YES")}


def load(hero):
    with open(lp(os.path.join(ROOT, "league", "champion", hero + ".data_champion")), encoding="utf-8-sig") as f:
        return json.load(f)


def diana(c):
    d = load("league_diana")
    if c["DIANA_MOON"] not in json.dumps(d["skill"]):
        sys.exit("Diana's Q no longer marks league_diana_moon_mark: update src/lib.rs")
    eff = d["skill2"]["effect"]["effects"]
    old = [i for i, x in enumerate(eff) if x.get("type") == "SwitchByBuff" and x.get("buff_name") == "league_diana_moonlight"]
    if len(old) != 1:
        sys.exit("Lunar Rush's moonlight check moved in the main pack: update this script")
    again = old and eff[old[0]]["effect_buff"]
    if "league_diana_e_again" not in json.dumps(again):
        sys.exit("Lunar Rush's moonlight check no longer queues league_diana_e_again: update this script")
    ask = {"type": "AddBuff", "buff_state": {"name": c["DIANA_ASK"], "duration": {"Time": {"tick": 3}}}}
    read = {"type": "Delayed", "tick": 2, "effects": [{
        "type": "SwitchByBuff", "buff_name": c["DIANA_YES"],
        "effect_buff": {"type": "Combine", "effects": [{"type": "RemoveCasterBuff", "name": c["DIANA_YES"]}] + again["effects"]},
        "effect_none": {"type": "Combine", "effects": []}}]}
    eff[old[0]] = {"type": "Combine", "effects": [ask, read]}
    d["passive"] = {"passive_ref": MOD_ID + ":diana", "params": {}}
    return d, [("league_diana", "skill2")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    c = consts()
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: {} for lang in main_text}
    files = {}
    for make in (diana,):
        d, slots = make(c)
        hero = d["id"]
        for _, slot in slots:
            d[slot]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{hero[7:]}_{slot}"
            for lang, tab in main_text.items():
                old, new = TEXT[(hero, slot)][lang]
                t = tab["description"][hero][slot]
                if old not in t:
                    sys.exit(f"{lang} {hero}.{slot}: the main pack's text changed ({old!r} not found): update this script")
                t = LEAD[lang] + t.replace(old, new)
                if shown_length(t) > TOOLTIP_MAX[lang]:
                    sys.exit(f"{lang} {hero}.{slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
                texts[lang][f"{hero[7:]}_{slot}"] = t
        files[os.path.join(ADDON, "override", hero + ".data_champion")] = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
    files[os.path.join(ADDON, "text", "champion.i18n")] = json.dumps(
        {lang: {"description": {MOD_ID: k}} for lang, k in texts.items()}, ensure_ascii=False, indent=2) + "\n"
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
