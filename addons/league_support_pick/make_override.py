"""Build the add-on's copies of Janna, Sona and Lulu from the main pack (their gift to the ally who needs it).

    python addons/league_support_pick/make_override.py [--check]

Reads the main pack's kits and writes addons/league_support_pick/override/<hero>.data_champion and .../text/champion.i18n:
  * league_janna: E's RandomTarget AllyNotSelf 50000 (lock, 150 + 75% AP shield 240 t, +15% AD with it) swapped for
    the native effect league_support_pick:janna_e;
  * league_sona: W's RandomTarget AllyNotSelf 60000 (100 + 40% AP heal) swapped for :sona_w;
  * league_lulu: E's two RandomTarget AllyNotSelf (30000, then 60000: Pix with the 110 + 50% AP shield and the haste)
    swapped for :lulu_e30 / :lulu_e60;
  * their skill2 tooltips point to description.league_support_pick.<hero>_skill2 with the ally's words swapped.
The native effects use the main pack's numbers; this script checks them (src/lib.rs). Run it again whenever one of the
three changes in the main pack (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_support_pick")
MOD_ID = "league_support_pick"
SLOT = "skill2"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
# hero -> [(range, the RandomTarget's effects' fingerprint, native effect)]
SWAPS_DATA = {
    "league_janna": [(50000, [("AddCasterBuff", "league_janna_e_lock"), ("Shield", (150, 75, 240)), ("AddBuff", "league_janna_e_storm")],
                      "janna_e")],
    "league_sona": [(60000, [("Heal", (100, 40)), ("ViewEffect", "league_sona_w_heal")], "sona_w")],
    "league_lulu": [(30000, [("AddCasterBuff", "league_lulu_e_got"), ("Sfx", "league_lulu_e_cast"), ("TargetProjectile", "league_lulu_e_pix")],
                     "lulu_e30"),
                    (60000, [("AddCasterBuff", "league_lulu_e_got"), ("Sfx", "league_lulu_e_cast"), ("TargetProjectile", "league_lulu_e_pix")],
                     "lulu_e60")],
}
TEXT = {
    "league_janna": {
        "zh-hans": ("为身边一名友方英雄提供", "为最需要的队友提供"),
        "zh-hant": ("為身邊一名友方英雄提供", "為最需要的隊友提供"),
        "en": ("gives a nearby allied champion a", "gives the nearby ally who needs it most (in danger, else fighting) a"),
        "ko": ("주변 아군 챔피언 하나에게", "가장 필요한 아군에게"),
        "ja": ("近くの味方チャンピオン1体に", "最も必要な近くの味方（危険か交戦中）に"),
    },
    "league_sona": {
        "zh-hans": ("为自己和一名附近的友方英雄回复", "为自己和附近损失生命最多的队友回复"),
        "zh-hant": ("為自身和一名附近的友方英雄回復", "為自身和附近損失生命最多的隊友回復"),
        "en": ("heals herself and a nearby allied champion", "heals herself and the most wounded nearby ally"),
        "ko": ("자신과 근처 아군 챔피언 한 명의", "자신과 근처에서 가장 많이 다친 아군의"),
        "ja": ("自身と近くの味方チャンピオン1体の", "自身と近くで最も傷ついた味方の"),
    },
    "league_lulu": {
        "zh-hans": ("：附近友方英雄获得", "：附近最需要的队友获得"),
        "zh-hant": ("：附近友方英雄獲得", "：附近最需要的隊友獲得"),
        "en": ("a nearby allied champion gets", "the nearby ally who needs it most gets"),
        "ko": ("근처 아군 챔피언에게", "가장 필요한 근처 아군에게"),
        "ja": ("近くの味方に", "最も必要な近くの味方に"),
    },
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def load(hero):
    with open(lp(os.path.join(ROOT, "league", "champion", hero + ".data_champion")), encoding="utf-8-sig") as f:
        return json.load(f)


def fingerprint(effects):
    out = []
    for e in effects:
        t = e.get("type")
        if t == "Shield":
            out.append((t, (e["amount"], e["ap_ratio"], e["tick"])))
        elif t == "Heal":
            out.append((t, (e["amount"], e["ap_ratio"])))
        elif t in ("AddCasterBuff", "AddBuff"):
            out.append((t, e["buff_state"]["name"]))
        else:
            out.append((t, e.get("name")))
    return out


def lulu_pix_ok(effects):
    pix = [e for e in effects if e.get("type") == "TargetProjectile"][0]
    inner = json.dumps(pix["applied_effects"])
    return pix["speed"] == 4500 and all(k in inner for k in ('"amount": 110', '"ap_ratio": 50', '"tick": 150',
                                                             '"league_lulu_e_on"', '"league_lulu_w_haste"', '"tick": 210',
                                                             '"move_speed_mult": 25', '"attack_speed_mult": 25'))


def replace(o, match, make, count):
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def build(hero):
    d = load(hero)
    for reach, fp, name in SWAPS_DATA[hero]:
        def is_it(o, reach=reach):
            return o.get("type") == "RandomTarget" and o.get("casting_target") == "AllyNotSelf" and o.get("range") == reach
        found = []
        d[SLOT] = replace(d[SLOT], is_it, lambda o, name=name: {"type": "Native", "effect_ref": MOD_ID + ":" + name}, found)
        if len(found) != 1 or fingerprint(found[0]["effects"]) != fp:
            sys.exit(f"{hero}'s RandomTarget AllyNotSelf {reach} changed in the main pack: update src/lib.rs and this script")
        if hero == "league_lulu" and not lulu_pix_ok(found[0]["effects"]):
            sys.exit("Lulu's Pix (shield / haste numbers) changed: update src/lib.rs")
    if '"casting_target": "AllyNotSelf"' in json.dumps(d[SLOT]):
        sys.exit(f"{hero}: another RandomTarget AllyNotSelf left in {SLOT}: update this script")
    d[SLOT]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.{hero[7:]}_{SLOT}"
    return d


def texts():
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main = json.load(f)
    out = {}
    for lang, tab in main.items():
        keys = {}
        for hero, swaps in TEXT.items():
            old, new = swaps[lang]
            t = tab["description"][hero][SLOT]
            if old not in t:
                sys.exit(f"{lang} {hero}.{SLOT}: the main pack's text changed ({old!r} not found): update this script")
            t = LEAD[lang] + t.replace(old, new)
            if shown_length(t) > TOOLTIP_MAX[lang]:
                sys.exit(f"{lang} {hero}.{SLOT}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
            keys[f"{hero[7:]}_{SLOT}"] = t
        out[lang] = {"description": {MOD_ID: keys}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    files = {os.path.join(ADDON, "override", hero + ".data_champion"): json.dumps(build(hero), ensure_ascii=False, indent=2) + "\n"
             for hero in SWAPS_DATA}
    files[os.path.join(ADDON, "text", "champion.i18n")] = json.dumps(texts(), ensure_ascii=False, indent=2) + "\n"
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
