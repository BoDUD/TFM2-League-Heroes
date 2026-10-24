"""Build the add-on's copy of Jhin from the main pack (his bonus attack speed into attack damage).

    python addons/league_jhin_whisper/make_override.py [--check]

Reads the main pack's league/champion/league_jhin.data_champion and writes
addons/league_jhin_whisper/override/league_jhin.data_champion and .../text/champion.i18n: the same kit with -
  * the passive league_jhin_whisper:whisper (it cancels his bonus attack speed and adds 0.25% AD per 1%);
  * the attack's tooltip (it carries Whisper) pointing to description.league_jhin_whisper.attack, one sentence added.
Every other champion stays untouched. Run it again whenever the main pack's Jhin changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_jhin_whisper")
MOD_ID = "league_jhin_whisper"
HERO = "league_jhin"
SLOT = "attack"
TEXT_KEY = "description." + MOD_ID + "." + SLOT
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
SWAPS = {
    "zh-hans": ("绽放莲花。", "绽放莲花。额外攻速不加快开枪，每" + Y + "1%" + E + "换成" + Y + "0.25%" + E + "攻击力。"),
    "zh-hant": ("綻放蓮花。", "綻放蓮花。額外攻速不加快開槍，每" + Y + "1%" + E + "換成" + Y + "0.25%" + E + "攻擊力。"),
    "en": ("bloom a lotus where they fall.", "bloom a lotus where they fall. Bonus attack speed does not speed his shots: each " + Y + "1%" + E +
           " becomes " + Y + "0.25%" + E + " AD."),
    "ko": ("연꽃이 핍니다.", "연꽃이 핍니다. 추가 공격 속도 " + Y + "1%" + E + "당 공격력 " + Y + "0.25%" + E + "로 전환."),
    "ja": ("蓮が咲く。", "蓮が咲く。追加攻撃速度は" + Y + "1%" + E + "ごとに攻撃力" + Y + "0.25%" + E + "に変換。"),
}


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
    if champion.get("passive"):
        sys.exit("Jhin has a passive in the main pack now: update this script")
    champion["passive"] = {"passive_ref": MOD_ID + ":whisper", "params": {}}
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
