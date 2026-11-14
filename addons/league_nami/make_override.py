"""Build the add-on's copy of Nami from the main pack (Tidecaller's Blessing on the blessed one's next 3 hits).

    python addons/league_nami/make_override.py [--check]

Reads the main pack's league/champion/league_nami.data_champion and writes
addons/league_nami/override/league_nami.data_champion and .../text/champion.i18n: the same kit with -
  * every league_nami_e_blessing Ebb and Flow gives (an ally or herself, then the bounce) a plain mark of BLESS_T ticks
    (League's 6 s) without the main pack's +15% attack and ability power;
  * the stream's own slow (league_nami_e_slow on the enemies it hits) taken out: the blessed one's hits slow instead;
  * the passive league_nami:tide (src/lib.rs): the blessed champion's next CHARGES attacks or abilities deal bonus magic
    damage and slow;
  * Ebb and Flow's tooltip pointing to description.league_nami_addon.skill, the blessing's sentence rewritten.
Every other champion stays untouched. Run it again whenever the main pack's Nami changes (--check: compare only, CI).
"""
import argparse
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_nami")
MOD_ID = "league_nami"
HERO = "league_nami"
TEXT_ID = "league_nami_addon"         # the texts' key (the hero's own id is league_nami)
SLOT = "skill"
BLESS = "league_nami_e_blessing"
SLOW = "league_nami_e_slow"
MAIN_BLESS = {"tick": 240, "attack_mult": 15, "magic_power_mult": 15}   # the main pack's blessing (stops the script when it changes)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, M, R, E = "<#ff9028ff>", "<#ffb900ff>", "<#a974ffff>", "<#ef5350ff>", "<>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
# the blessing's sentence of the main pack's text starts here ...
BLESSING = {"zh-hans": O + "唤潮之佑" + E, "zh-hant": O + "深海恩賜" + E, "en": O + "Tidecaller's Blessing" + E,
            "ko": O + "파도 소환사의 축복" + E, "ja": O + "潮使いの祝福" + E}
# ... and becomes this
NEW = {
    "zh-hans": "：被治疗者" + A + "{t}秒" + E + "内" + A + "{n}次" + E + "命中各多造成" + M + "{d}" + E + "+" + APi + M + "{ap}%" + E + M + "魔法伤害" + E +
               "并" + R + "减速{s}%" + E + "（" + A + "{st}秒" + E + "）。",
    "zh-hant": "：被治療者" + A + "{t}秒" + E + "內" + A + "{n}次" + E + "命中各多造成" + M + "{d}" + E + "+" + APi + M + "{ap}%" + E + M + "魔法傷害" + E +
               "並" + R + "緩速{s}%" + E + "（" + A + "{st}秒" + E + "）。",
    "en": ": the healed one's next " + A + "{n}" + E + " hits in " + A + "{t}s" + E + " deal " + M + "{d}" + E + " + " + APi + M + "{ap}%" + E +
          " more " + M + "magic damage" + E + ", " + R + "slowing" + E + " {s}% for " + A + "{st}s" + E + ".",
    "ko": ": 회복된 아군의 " + A + "{t}초" + E + "간 " + A + "{n}회" + E + " 적중이 " + M + "{d}" + E + "+" + APi + M + "{ap}%" + E + " 추가 " + M +
          "마법 피해" + E + "와 " + R + "{s}% 둔화" + E + "(" + A + "{st}초" + E + ").",
    "ja": "：回復した味方の" + A + "{t}秒" + E + "間の" + A + "{n}回" + E + "の命中が" + M + "{d}" + E + "+" + APi + M + "{ap}%" + E + "の追加" + M +
          "魔法ダメージ" + E + "と" + R + "{s}%スロウ" + E + "（" + A + "{st}秒" + E + "）。",
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    out = {k: int(re.search(r"pub const %s: usize = (\d+);" % k, src).group(1))
           for k in ("BLESS_T", "CHARGES", "DMG", "DMG_AP", "SLOW_T")}
    out["SLOW"] = int(re.search(r"pub const SLOW: i32 = (\d+);", src).group(1))
    return out


def is_buff(e, name):
    return isinstance(e, dict) and e.get("type") == "AddBuff" and e.get("buff_state", {}).get("name") == name


def patch(node, k, seen):
    """Blessings to plain marks, the stream's slows out (in effect lists and in applied_effects' wrappers)."""
    if isinstance(node, dict):
        if is_buff(node, BLESS):
            b = node["buff_state"]
            got = {"tick": b.get("duration", {}).get("Time", {}).get("tick"), "attack_mult": b.get("attack_mult"),
                   "magic_power_mult": b.get("magic_power_mult")}
            if got != MAIN_BLESS:
                sys.exit(f"the main pack's blessing changed ({b}): update this script")
            b.pop("attack_mult")
            b.pop("magic_power_mult")
            b["duration"] = {"Time": {"tick": k["BLESS_T"]}}
            seen["bless"] += 1
        for key, v in node.items():
            if isinstance(v, list):
                keep = []
                for e in v:
                    if is_buff(e, SLOW) or (isinstance(e, dict) and is_buff(e.get("effect"), SLOW)):
                        seen["slow"] += 1
                        continue
                    keep.append(e)
                node[key] = keep
            patch(node[key], k, seen)
    elif isinstance(node, list):
        for v in node:
            patch(v, k, seen)


def secs(ticks):
    return ("%.2f" % (ticks / 60)).rstrip("0").rstrip(".")


def build():
    k = rust_consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = copy.deepcopy(json.load(f))
    if champion.get("passive"):
        sys.exit("Nami has a passive in the main pack now: update this script")
    seen = {"bless": 0, "slow": 0}
    for s in ("attack", "skill2", "ult"):
        if BLESS in json.dumps(champion[s]) or SLOW in json.dumps(champion[s]):
            sys.exit(f"the main pack's {s} uses the blessing or its slow now: update this script")
    patch(champion[SLOT], k, seen)
    if seen != {"bless": 4, "slow": 4}:
        sys.exit(f"Ebb and Flow changed ({seen} blessings / slows, not 4 / 4): update this script")
    champion["passive"] = {"passive_ref": MOD_ID + ":tide", "params": {}}
    champion[SLOT]["description"] = "#asset/base/text/champion?description." + TEXT_ID + "." + SLOT

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        t = tab["description"][HERO][SLOT]
        at = t.find(BLESSING[lang])
        if at < 0:
            sys.exit(f"{lang} {HERO}.{SLOT}: no blessing sentence ({BLESSING[lang]!r}) in the main pack's text: update this script")
        t = LEAD[lang] + t[:at + len(BLESSING[lang])] + NEW[lang].format(
            t=secs(k["BLESS_T"]), n=k["CHARGES"], d=k["DMG"], ap=k["DMG_AP"], s=k["SLOW"], st=secs(k["SLOW_T"]))
        if shown_length(t) > TOOLTIP_MAX[lang]:
            sys.exit(f"{lang}: tooltip too long ({shown_length(t)} > {TOOLTIP_MAX[lang]})")
        texts[lang] = t
    for lang, t in texts.items():
        print(f"{lang} {SLOT}:{shown_length(t)}/{TOOLTIP_MAX[lang]}")
    i18n = {lang: {"description": {TEXT_ID: {SLOT: texts[lang]}}} for lang in main_text}
    return [(os.path.join(ADDON, "override", HERO + ".data_champion"), dumps(champion)),
            (os.path.join(ADDON, "text", "champion.i18n"), dumps(i18n))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="only compare the copy with the files (CI)")
    a = ap.parse_args()
    out = build()
    if a.check:
        bad = []
        for path, text in out:
            try:
                with open(lp(path), encoding="utf-8", newline="") as f:
                    have = f.read()
            except FileNotFoundError:
                have = None
            if have is None or have.replace("\r\n", "\n") != text.replace("\r\n", "\n"):
                bad.append(os.path.relpath(path, ROOT))
        if bad:
            sys.exit(f"out of date (python addons/{MOD_ID}/make_override.py): " + ", ".join(bad))
        print(f"{MOD_ID}: the copy is up to date")
        return
    for path, text in out:
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(path)


if __name__ == "__main__":
    main()
