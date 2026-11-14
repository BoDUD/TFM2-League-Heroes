"""Build the add-on's copy of Leona from the main pack (Sunlight detonated by allied champions, as in League).

    python addons/league_leona/make_override.py [--check]

Reads the main pack's league/champion/league_leona.data_champion and writes
addons/league_leona/override/league_leona.data_champion and .../text/champion.i18n: the same kit with -
  * every league_leona_sunlight her abilities add (Q, the solar blade, Eclipse's burst, the ult's zone) a plain mark of
    MARK_T ticks (League's 2.5 s) without the main pack's +10% damage taken;
  * the passive league_leona:sunlight (src/lib.rs): an allied champion's attack or ability on a marked enemy detonates
    the mark for magic damage by her level;
  * the attack's tooltip (it carries the passive) pointing to description.league_leona_addon.attack, its passive part
    rewritten.
Every other champion stays untouched. Run it again whenever the main pack's Leona changes (--check: compare only, CI).
"""
import argparse
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_leona")
MOD_ID = "league_leona"
HERO = "league_leona"
TEXT_ID = "league_leona_addon"        # the texts' key (the hero's own id is league_leona)
SLOT = "attack"
MARK = "league_leona_sunlight"
MAIN_MARK = {"tick": 90, "damaged_amplify": 10}     # what the main pack's mark is (stops the script when it changes)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, M, E = "<#ff9028ff>", "<#ffb900ff>", "<#a974ffff>", "<>"
# the passive part of the main pack's attack text starts here ...
PASSIVE = {"zh-hans": "被动 ", "zh-hant": "被動 ", "en": "Passive ", "ko": "기본 지속 효과 ", "ja": "パッシブ "}
# ... and becomes this
NEW = {
    "zh-hans": "被动 " + O + "日光" + E + "：蕾欧娜的技能命中的敌人挂上日光（" + A + "{t}秒" + E + "），友方英雄的攻击或技能打中它时引爆，造成" +
               M + "{lo}～{hi}" + E + "（随她的等级）" + M + "魔法伤害" + E + "。",
    "zh-hant": "被動 " + O + "烈陽之力" + E + "：雷歐娜的技能命中的敵人掛上烈陽（" + A + "{t}秒" + E + "），友方英雄的攻擊或技能打中它時引爆，造成" +
               M + "{lo}～{hi}" + E + "（隨她的等級）" + M + "魔法傷害" + E + "。",
    "en": "Passive " + O + "Sunlight" + E + ": enemies hit by Leona's abilities are marked for " + A + "{t}s" + E + "; an allied "
          "champion's attack or ability on them detonates it for " + M + "{lo}-{hi}" + E + " (by her level) " + M + "magic damage" + E + ".",
    "ko": "기본 지속 효과 " + O + "햇빛" + E + ": 레오나의 스킬에 맞은 적에게 " + A + "{t}초" + E + " 동안 햇빛이 남고, 아군 챔피언의 공격이나 스킬이 "
          "맞으면 터져 " + M + "{lo}~{hi}" + E + "(레오나 레벨 비례) " + M + "마법 피해" + E + "를 입힙니다.",
    "ja": "パッシブ " + O + "サンライト" + E + "：レオナのスキルが命中した敵に" + A + "{t}秒" + E + "間サンライトが付き、味方チャンピオンの攻撃か"
          "スキルが当たると爆発して" + M + "{lo}～{hi}" + E + "（彼女のレベルに比例）の" + M + "魔法ダメージ" + E + "を与える。",
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
    return {k: int(re.search(r"pub const %s: usize = (\d+);" % k, src).group(1)) for k in ("MARK_T", "DMG_MIN", "DMG_MAX")}


def marks(node, out):
    """Every AddBuff of the Sunlight mark."""
    if isinstance(node, dict):
        if node.get("type") == "AddBuff" and node.get("buff_state", {}).get("name") == MARK:
            out.append(node["buff_state"])
        for v in node.values():
            marks(v, out)
    elif isinstance(node, list):
        for v in node:
            marks(v, out)
    return out


def secs(ticks):
    return ("%.2f" % (ticks / 60)).rstrip("0").rstrip(".")


def build():
    k = rust_consts()
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = copy.deepcopy(json.load(f))
    if champion.get("passive"):
        sys.exit("Leona has a passive in the main pack now: update this script")
    found = marks([champion[s] for s in ("attack", "skill", "skill2", "ult")], [])
    if len(found) != 4:
        sys.exit(f"the main pack adds {MARK} in {len(found)} places, not 4 (Q, E, W's burst, R): update this script")
    for b in found:
        if (b.get("duration", {}).get("Time", {}).get("tick"), b.get("damaged_amplify")) != (MAIN_MARK["tick"], MAIN_MARK["damaged_amplify"]):
            sys.exit(f"the main pack's Sunlight changed ({b}): update this script")
        b.pop("damaged_amplify")
        b["duration"] = {"Time": {"tick": k["MARK_T"]}}
    champion["passive"] = {"passive_ref": MOD_ID + ":sunlight", "params": {}}
    champion[SLOT]["description"] = "#asset/base/text/champion?description." + TEXT_ID + "." + SLOT

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        t = tab["description"][HERO][SLOT]
        at = t.find(PASSIVE[lang])
        if at < 0:
            sys.exit(f"{lang} {HERO}.{SLOT}: no passive part ({PASSIVE[lang]!r}) in the main pack's text: update this script")
        t = LEAD[lang] + t[:at] + NEW[lang].format(t=secs(k["MARK_T"]), lo=k["DMG_MIN"], hi=k["DMG_MAX"])
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
