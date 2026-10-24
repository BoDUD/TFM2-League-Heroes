"""Build the add-on's copy of Varus from the main pack (Blight stacks on each enemy apart).

    python addons/league_varus_blight/make_override.py [--check]

Reads the main pack's league/champion/league_varus.data_champion and writes
addons/league_varus_blight/override/league_varus.data_champion and .../text/champion.i18n: the same kit with -
  * the attack's Blight ladder (SwitchByBuff league_varus_b_3 .. 1 adding a caster buff) swapped for the native effect
    league_varus_blight:stack; Q's and E's pop ladders (FixedAttack target_hp_ratio 3 / 6 / 9) for :pop, R's for :pop_r;
    R's "fill to 3" block for :fill (the add-on keeps the stacks on the target, src/lib.rs);
  * the attack's tooltip pointing to description.league_varus_blight.attack with "on each champion" added.
Every other champion stays untouched. Run it again whenever the main pack's Varus changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_varus_blight")
MOD_ID = "league_varus_blight"
HERO = "league_varus"
B = "league_varus_b_"
SLOT = "attack"
TEXT_KEY = "description." + MOD_ID + "." + SLOT
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
SWAPS = {
    "zh-hans": ("（最多3层）", "（最多3层，每个英雄各算各的）"),
    "zh-hant": ("（最多3層）", "（最多3層，每個英雄各算各的）"),
    "en": ("a stack of <#ff9028ff>Blight<> (up to 3)", "a stack of <#ff9028ff>Blight<> on that champion (up to 3 each)"),
    "ko": ("중첩을 쌓습니다(최대 3)", "중첩을 그 챔피언에게 쌓습니다(각각 최대 3)"),
    "ja": ("を付与（最大3）", "をそのチャンピオンに付与（各最大3）"),
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


def native(name):
    return {"type": "Native", "effect_ref": MOD_ID + ":" + name}


def build():
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)

    def ladder(o):
        return o.get("type") == "SwitchByBuff" and o.get("buff_name") == B + "3"

    def is_stack(o):
        return ladder(o) and '"AddCasterBuff"' in json.dumps(o["effect_buff"])

    def is_pop(o):
        return ladder(o) and '"target_hp_ratio": 9' in json.dumps(o["effect_buff"])

    def is_fill(o):
        return o.get("type") == "Combine" and [e.get("type") for e in o["effects"]] ==             ["RemoveCasterBuff"] * 3 + ["AddCasterBuff", "ViewEffect"] and o["effects"][3]["buff_state"]["name"] == B + "3"

    counts = {}
    for slot, rules in (("attack", [(is_stack, "stack")]), ("skill", [(is_pop, "pop")]), ("skill2", [(is_pop, "pop")]),
                        ("ult", [(is_pop, "pop_r"), (is_fill, "fill")])):
        for match, name in rules:
            n = []
            champion[slot] = replace(champion[slot], match, lambda o, name=name: native(name), n)
            counts[(slot, name)] = len(n)
    if counts != {("attack", "stack"): 1, ("skill", "pop"): 4, ("skill2", "pop"): 1, ("ult", "pop_r"): 1, ("ult", "fill"): 1}:
        sys.exit(f"Varus's Blight ladders changed in the main pack {counts}: update this script")
    left = [x for x in re.findall(r'"buff_name": "(' + B + r'[123])"', json.dumps(champion))]
    if left:
        sys.exit(f"Blight checks left in the copy: {left}")
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
