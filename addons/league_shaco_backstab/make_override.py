"""Build the add-on's copy of Shaco from the main pack (Backstab from behind, by where the target faces).

    python addons/league_shaco_backstab/make_override.py [--check]

Reads the main pack's league/champion/league_shaco.data_champion and writes
addons/league_shaco_backstab/override/league_shaco.data_champion and .../text/champion.i18n: the same kit with -
  * the attack's and the shiv's backstab twins (TargetProjectile league_shaco_a_bs / league_shaco_e_bs on
    EnemyChampionInCC, 15 + 25% AD) aimed at every enemy champion and only marking him with src/lib.rs's ASK (3 ticks);
  * the passive league_shaco_backstab:backstab (it deals the backstab when Shaco is behind; params = the twins' numbers);
  * the attack's tooltip pointing to description.league_shaco_backstab.attack, "crowd-controlled" swapped for "from behind".
Every other champion stays untouched. Run it again whenever the main pack's Shaco changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_shaco_backstab")
MOD_ID = "league_shaco_backstab"
HERO = "league_shaco"
TWINS = ("league_shaco_a_bs", "league_shaco_e_bs")
SLOT = "attack"
TEXT_KEY = "description." + MOD_ID + "." + SLOT
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
SWAPS = {
    "zh-hans": ("攻击被控制的敌方英雄时", "从背后攻击敌方英雄时"),
    "zh-hant": ("攻擊被控制的敵方英雄時", "從背後攻擊敵方英雄時"),
    "en": ("attacks on crowd-controlled enemy champions", "attacks on enemy champions from behind"),
    "ko": ("군중 제어된 적 챔피언을 공격하면", "적 챔피언을 뒤에서 공격하면"),
    "ja": ("行動妨害中の敵チャンピオンへの攻撃は", "敵チャンピオンの背後からの攻撃は"),
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
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    ask = re.search(r'pub const ASK: &str = "([^"]+)";', src).group(1)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if champion.get("passive"):
        sys.exit("Shaco has a passive in the main pack now: update this script")
    mark = {"casting_type": "Targeting", "effect": {"type": "AddBuff", "buff_state": {"name": ask, "duration": {"Time": {"tick": 3}}}}}
    twins = []
    champion[SLOT] = replace(champion[SLOT], lambda o: o.get("type") == "TargetProjectile" and o.get("name") in TWINS,
                             lambda o: dict(o, applied_target="EnemyChampion", applied_effects=[mark]), twins)
    hits = {(e["effect"]["damage"], e["effect"]["attack_ratio"]) for t in twins for e in t["applied_effects"]
            if e["effect"].get("type") == "Attack"}
    if sorted(t["name"] for t in twins) != sorted(TWINS) or any(t["applied_target"] != "EnemyChampionInCC" for t in twins)             or len(hits) != 1:
        sys.exit("Shaco's backstab twins changed in the main pack: update this script")
    (base, ad), = hits
    champion["passive"] = {"passive_ref": MOD_ID + ":backstab", "params": {"base": base, "ad": ad}}
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
