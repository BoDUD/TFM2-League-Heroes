"""Build the add-on's copy of Shyvana from the main pack (Scalemail stacks on takedowns, as in League).

    python addons/league_shyvana/make_override.py [--check]

Reads the main pack's league/champion/league_shyvana.data_champion and writes
addons/league_shyvana/override/league_shyvana.data_champion and .../text/champion.i18n: the same kit with -
  * the dragon (the ult's league_shyvana_dg) keeping only its health: the main pack folds Scalemail into it as +30%
    armour and magic resistance, the copy drops those two (League's dragon form gives health, size and range);
  * the passive league_shyvana:scalemail (src/lib.rs): 3 stacks a champion takedown or epic monster, 1 a camp, 0.3
    armour and magic resistance a stack (params: champion, epic, large, per10);
  * the ult's tooltip pointing to description.league_shyvana_addon.ult: the Scalemail clause swapped for the stacks.
Her attack is not touched (another session measures it; src/lib.rs's test compares it with the main pack's byte for
byte). Every other champion stays untouched. Run it again whenever the main pack's Shyvana changes (--check: compare
only, for CI).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_shyvana")
MOD_ID = "league_shyvana"
HERO = "league_shyvana"
TEXT_ID = "league_shyvana_addon"       # the texts' key (the hero's own id is league_shyvana too)
PARAMS = {"champion": 3, "epic": 3, "large": 1, "per10": 3}
DRAGON = "league_shyvana_dg"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
O, Y, E = "<#ff9028ff>", "<#ffb900ff>", "<>"
# the ult's text: lang -> (the main pack's Scalemail clause, the add-on's); {c} {e} {l} {a}: stacks a champion / epic /
# large monster, armour a stack
SWAPS = {
    "zh-hans": ("，" + O + "龙鳞铁衣" + E + "使护甲和魔抗+{old}%。",
                "。" + O + "龙鳞铁衣" + E + "：参与击杀英雄、击杀史诗野怪+" + Y + "{c}" + E + "层，大型野怪+" + Y + "{l}" + E +
                "层，每层护甲和魔抗+" + Y + "{a}" + E + "，永久。"),
    "zh-hant": ("，" + O + "真龍鱗甲" + E + "使護甲和魔抗+{old}%。",
                "。" + O + "真龍鱗甲" + E + "：參與擊殺英雄、擊殺史詩野怪+" + Y + "{c}" + E + "層，大型野怪+" + Y + "{l}" + E +
                "層，每層護甲和魔抗+" + Y + "{a}" + E + "，永久。"),
    "en": ("; " + O + "Scalemail" + E + " gives +{old}% armour and magic resist.",
           ". " + O + "Scalemail" + E + ": champion takedowns and epic monsters give " + Y + "{c}" + E + " stacks, large monsters " +
           Y + "{l}" + E + "; each stack is +" + Y + "{a}" + E + " armour and magic resist for good."),
    "ko": (", " + O + "미늘갑옷" + E + "으로 방어력과 마법 저항력 +{old}%.",
           ". " + O + "미늘갑옷" + E + ": 챔피언 처치 관여·에픽 몬스터 " + Y + "{c}" + E + "중첩, 대형 몬스터 " + Y + "{l}" + E +
           "중첩, 중첩당 방어력과 마법 저항력 +" + Y + "{a}" + E + "(영구)."),
    "ja": ("、" + O + "スケールメイル" + E + "で物防と魔防+{old}%。",
           "。" + O + "スケールメイル" + E + "：キル関与・エピックモンスターで" + Y + "{c}" + E + "、大型モンスターで" + Y + "{l}" + E +
           "スタック、各物防と魔防+" + Y + "{a}" + E + "（永続）。"),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def dragons(o, out):
    """Every buff_state of the dragon buff in `o`."""
    if isinstance(o, dict):
        if isinstance(o.get("buff_state"), dict) and o["buff_state"].get("name") == DRAGON:
            out.append(o["buff_state"])
        for v in o.values():
            dragons(v, out)
    elif isinstance(o, list):
        for v in o:
            dragons(v, out)
    return out


def build():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    passive = re.search(r'pub const PASSIVE: &str = "([^"]+)";', src).group(1)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Shyvana has a passive in the main pack now: update this script")
    attack = json.dumps(champion["attack"], sort_keys=True)
    states = dragons(champion["ult"], [])
    others = sum(len(dragons(champion[s], [])) for s in ("attack", "skill", "skill2"))
    if len(states) != 1 or others:
        sys.exit("the dragon buff (%s) is added %d times in the ult and %d elsewhere: update this script" % (DRAGON, len(states), others))
    dg = states[0]
    old = dg.get("defence_mult")
    if not old or dg.get("magic_resistance_mult") != old or not dg.get("hp_mult"):
        sys.exit("the dragon's armour / magic resistance / health changed: update this script")
    del dg["defence_mult"], dg["magic_resistance_mult"]
    if json.dumps(champion["attack"], sort_keys=True) != attack:
        sys.exit("the attack changed: it must stay the main pack's")
    champion["passive"] = {"passive_ref": passive, "params": PARAMS}
    champion["ult"]["description"] = "#asset/base/text/champion?description." + TEXT_ID + ".ult"
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    armour = PARAMS["per10"] / 10
    texts = {}
    for lang, tab in main_text.items():
        cut, new = SWAPS[lang]
        cut = cut.format(old=old)
        t = tab["description"][HERO]["ult"]
        if t.count(cut) != 1 or not t.endswith(cut):
            sys.exit(f"{lang} {HERO}.ult: the main pack's text changed: update this script")
        texts[lang] = LEAD[lang] + t[:-len(cut)] + new.format(c=PARAMS["champion"], e=PARAMS["epic"], l=PARAMS["large"],
                                                               a="%g" % armour)
        if PARAMS["champion"] != PARAMS["epic"]:
            sys.exit("the texts say champions and epic monsters give the same stacks: update them")
        if shown_length(texts[lang]) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang}: tooltip too long ({shown_length(texts[lang])} > {TOOLTIP_MAX[lang]})")
    text = {lang: {"description": {TEXT_ID: {"ult": texts[lang]}}} for lang in main_text}
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
