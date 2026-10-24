"""Build the add-on's copies of Blitzcrank, LeBlanc and Lissandra from the main pack (their low-health triggers).

    python addons/league_lowhp/make_override.py [--check]

Reads the main pack's kits and writes addons/league_lowhp/override/<hero>.data_champion and .../text/champion.i18n:
every SwitchByBuff that reads the hero's "two or more enemy champions round me" flag (<hero>_mb_n2 / _p_n2 / _r_n2,
raised by the counting the main pack runs before) reads src/lib.rs's <hero>_low instead, which the add-on's passive
league_lowhp:<name> holds while the hero is at or under the threshold; the counting stays (nobody reads its flag);
passive league_lowhp:<name>; the tooltip that names the trigger points to description.league_lowhp.<name>_<slot>.
Run it again whenever one of them changes in the main pack (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_lowhp")
MOD_ID = "league_lowhp"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
# hero -> (the counting flag read, how many reads, the tooltip slot, lang -> (main words, add-on words with {p}))
HEROES = {
    "league_blitzcrank": ("league_blitzcrank_mb_n2", 36, "attack", {
        "zh-hans": ("被围攻或被控制时获得", "生命低于" + Y + "{p}%" + E + "时获得"),
        "zh-hant": ("被圍攻或被控場時獲得", "生命低於" + Y + "{p}%" + E + "時獲得"),
        "en": ("when surrounded or crowd-controlled he gains", "at " + Y + "{p}%" + E + " health or below he gains"),
        "ko": ("포위되거나 군중 제어에 걸리면", "체력이 " + Y + "{p}%" + E + " 이하가 되면"),
        "ja": ("囲まれるか行動妨害を受けると", "体力が" + Y + "{p}%" + E + "以下になると")}),
    "league_leblanc": ("league_leblanc_p_n2", 2, "attack", {
        "zh-hans": ("两名以上敌方英雄贴近时", "生命低于" + Y + "{p}%" + E + "时"),
        "zh-hant": ("兩名以上敵方英雄貼近時", "生命低於" + Y + "{p}%" + E + "時"),
        "en": ("when two or more enemy champions close in, she turns", "at " + Y + "{p}%" + E + " health or below she turns"),
        "ko": ("적 챔피언 둘 이상이 다가오면", "체력이 " + Y + "{p}%" + E + " 이하가 되면"),
        "ja": ("敵チャンピオン2体以上が近づくと", "体力が" + Y + "{p}%" + E + "以下になると")}),
    "league_lissandra": ("league_lissandra_r_n2", 3, "ult", {
        "zh-hans": ("被两名以上敌方英雄围住时", "生命低于" + Y + "{p}%" + E + "时"),
        "zh-hant": ("被兩名以上敵方英雄包圍時", "生命低於" + Y + "{p}%" + E + "時"),
        "en": ("Surrounded by two or more enemy champions, she", "At " + Y + "{p}%" + E + " health or below she"),
        "ko": ("적 챔피언 둘 이상에게 둘러싸이면", "체력이 " + Y + "{p}%" + E + " 이하면"),
        "ja": ("敵チャンピオン2体以上に囲まれると", "体力が" + Y + "{p}%" + E + "以下だと")}),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def lib_heroes():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    return {h: (name, flag, int(p)) for h, name, flag, p in
            re.findall(r'\("(league_[a-z]+)", "([a-z]+)", "([a-z_]+)", (\d+)\)', src)}


def rename(o, old, new, n):
    if isinstance(o, dict):
        if o.get("type") == "SwitchByBuff" and o.get("buff_name") == old:
            n.append(1)
            o = dict(o, buff_name=new)
        return {k: rename(v, old, new, n) for k, v in o.items()}
    if isinstance(o, list):
        return [rename(v, old, new, n) for v in o]
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    lib = lib_heroes()
    if set(lib) != set(HEROES):
        sys.exit(f"src/lib.rs HEROES {sorted(lib)} differ from this script's: update one of them")
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {lang: {} for lang in main_text}
    files = {}
    for hero, (count_flag, reads, slot, swaps) in HEROES.items():
        name, flag, pct = lib[hero]
        with open(lp(os.path.join(ROOT, "league", "champion", hero + ".data_champion")), encoding="utf-8-sig") as f:
            d = json.load(f)
        n = []
        d = rename(d, count_flag, flag, n)
        if len(n) != reads:
            sys.exit(f"{hero}: {len(n)} reads of {count_flag}, expected {reads}: check the main pack and update this script")
        d["passive"] = {"passive_ref": f"{MOD_ID}:{name}", "params": {}}
        d[slot]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{name}_{slot}"
        files[os.path.join(ADDON, "override", hero + ".data_champion")] = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
        for lang, tab in main_text.items():
            old, new = swaps[lang]
            t = tab["description"][hero][slot]
            if old not in t:
                sys.exit(f"{lang} {hero}.{slot}: the main pack's text changed ({old!r} not found): update this script")
            t = LEAD[lang] + t.replace(old, new.format(p=pct))
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {hero}.{slot}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
            texts[lang][f"{name}_{slot}"] = t
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
