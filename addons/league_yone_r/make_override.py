"""Build the add-on's copy of Yone from the main pack (Fate Sealed lands behind the last champion struck, pulls them).

    python addons/league_yone_r/make_override.py [--check]

Reads the main pack's league/champion/league_yone.data_champion and writes
addons/league_yone_r/override/league_yone.data_champion and .../text/champion.i18n: the same kit with -
  * R's RushMoveToBack (both branches: wound up and after Q3) swapped for an AddCasterBuff of src/lib.rs's GO (3 ticks);
  * R's champion line (LineRangeProjectile league_yone_r_mark) also putting STRUCK (3 ticks) on every champion it hits;
  * the passive league_yone_r:dash (it dashes him behind the farthest one struck and pulls them);
  * R's tooltip pointing to description.league_yone_r.ult: the main pack's text with the landing swapped.
Every other champion stays untouched. Run it again whenever the main pack's Yone changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_yone_r")
MOD_ID = "league_yone_r"
HERO = "league_yone"
SLOT = "ult"
TEXT_KEY = "description." + MOD_ID + "." + SLOT
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
SWAPS = {
    "zh-hans": [("，永恩冲到目标身后。", "，永恩冲到最后斩中者身后并拉近。")],
    "zh-hant": [("，犽凝衝到目標身後。", "，犽凝衝到最後斬中者身後並拉近。")],
    "en": [("Yone appears behind his target", "Yone appears behind the last champion struck, pulling them in")],
    "ko": [("요네는 대상 뒤로 이동합니다", "요네는 마지막 적중 챔피언 뒤로 가 끌어옵니다"), (" 챔피언 적중 시 필멸의 검 중첩 +1(", " 적중 시 중첩 +1(")],
    "ja": [("ヨネは対象の背後に現れる", "ヨネは最後に斬った敵の背後に現れ引き寄せる"), ("チャンピオン命中で斬命刀スタック+1", "命中で斬命刀+1")],
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
    out = {k: re.search(r'pub const ' + k + r': &str = "([^"]+)";', src).group(1) for k in ("GO", "STRUCK")}
    out["SPEED"] = int(re.search(r"pub const SPEED: f64 = ([\d_]+)\.0;", src).group(1).replace("_", ""))
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

    rushes, lines = [], []
    go = {"type": "AddCasterBuff", "buff_state": {"name": c["GO"], "duration": {"Time": {"tick": 3}}}, "only_to_enemy": False}
    mark = {"casting_type": "Targeting",
            "effect": {"type": "AddBuff", "buff_state": {"name": c["STRUCK"], "duration": {"Time": {"tick": 3}}}}}
    u = replace(champion[SLOT], lambda o: o.get("type") == "RushMoveToBack", lambda o: go, rushes)
    u = replace(u, lambda o: o.get("type") == "LineRangeProjectile" and o.get("name") == "league_yone_r_mark",
                lambda o: dict(o, applied_effects=o["applied_effects"] + [mark]), lines)
    if len(rushes) != 2 or len(lines) != 2 or any(r.get("speed") != c["SPEED"] for r in rushes):
        sys.exit(f"R's dashes ({len(rushes)}) / champion lines ({len(lines)}) changed in the main pack: update this script")
    if champion.get("passive"):
        sys.exit("Yone has a passive in the main pack now: update this script")
    champion[SLOT] = u
    champion["passive"] = {"passive_ref": MOD_ID + ":dash", "params": {}}
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
