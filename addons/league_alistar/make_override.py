"""Build the add-on's copy of Alistar from the main pack (Triumphant Roar's stacks from deaths near him, as in League).

    python addons/league_alistar/make_override.py [--check]

Reads the main pack's league/champion/league_alistar.data_champion (the shipped kit: tools/fix passes run over
tools/kit/build_alistar.py's output, so the copy starts from the file, not from a rebuild) and writes
addons/league_alistar/override/league_alistar.data_champion and .../text/champion.i18n: the same kit with -
  * every "his crowd control landed on a champion: one rung up the roar ladder, or the roar" (the SwitchByBuff on
    league_alistar_p1: Q's slam, W's headbutt and its slam, E's stun punch - four) replaced by the add-on's native effect
    league_alistar:cc (one Triumph stack);
  * the passive league_alistar:roar (src/lib.rs): stacks from his crowd control and from enemy minions, monsters,
    champions and epic monsters dying near him; the roar at NEED stacks with the main pack's heals;
  * the attack's tooltip (it carries the passive) pointing to description.league_alistar_addon.attack, the stacking
    rule rewritten.
src/lib.rs's numbers (P_CD, P_R, P_HEAL, P_AP, P_ALLY, P_ALLY_AP) must be tools/kit/build_alistar.py's P. Every other
champion stays untouched. Run it again whenever the main pack's Alistar changes (--check: compare only, CI).
"""
import argparse
import copy
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_alistar")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_alistar as kit  # noqa: E402  (its parameter table P only)

MOD_ID = "league_alistar"
HERO = "league_alistar"
TEXT_ID = "league_alistar_addon"      # the texts' key (the hero's own id is league_alistar)
SLOT = "attack"
LADDER = HERO + "_p1"                 # the top of the data's roar ladder (build_alistar.py p_stack)
NATIVE = {"type": "Native", "effect_ref": MOD_ID + ":cc"}
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
A, E = "<#ffb900ff>", "<>"
# the main pack's stacking rule (its p_need written in) ...
OLD = {
    "zh-hans": "控制命中敌方英雄" + A + "{need}次" + E + "后怒吼",
    "zh-hant": "控制命中敵方英雄" + A + "{need}次" + E + "後怒吼",
    "en": "after his crowd control lands on enemy champions " + A + "{need} times" + E + " he roars",
    "ko": "군중 제어를 적 챔피언에게 " + A + "{need}번" + E + " 적중시키면 포효해",
    "ja": "行動妨害を敵チャンピオンに" + A + "{need}回" + E + "当てると咆哮し",
}
# ... becomes League's
NEW = {
    "zh-hans": "控制命中敌方英雄、身边的敌方小兵或野怪阵亡各得" + A + "1层" + E + "，身边的敌方英雄或史诗野怪阵亡得" + A + "{big}层" + E + "，满" +
               A + "{need}层" + E + "后怒吼",
    "zh-hant": "控制命中敵方英雄、身邊的敵方小兵或野怪陣亡各得" + A + "1層" + E + "，身邊的敵方英雄或史詩野怪陣亡得" + A + "{big}層" + E + "，滿" +
               A + "{need}層" + E + "後怒吼",
    "en": "each enemy champion his crowd control lands on and each enemy minion or monster dying near him gives " + A + "1 stack" +
          E + ", an enemy champion or epic monster dying near him " + A + "{big}" + E + "; at " + A + "{need}" + E + " he roars",
    "ko": "적 챔피언에게 군중 제어를 적중시키거나 근처의 적 미니언·몬스터가 죽으면 " + A + "1중첩" + E + ", 근처의 적 챔피언·에픽 몬스터가 죽으면 " +
          A + "{big}중첩" + E + ", " + A + "{need}중첩" + E + "에 포효해",
    "ja": "行動妨害を敵チャンピオンに当てるか近くの敵ミニオン・モンスターが倒れると" + A + "1スタック" + E + "、近くの敵チャンピオン・エピックモンスターが"
          "倒れると" + A + "{big}スタック" + E + "、" + A + "{need}スタック" + E + "で咆哮し",
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
    out = {}
    for k in ("NEED", "BIG_STACKS", "P_CD", "P_R", "P_HEAL", "P_AP", "P_ALLY", "P_ALLY_AP"):
        out[k] = int(re.search(r"pub const %s: (?:usize|u64) = ([\d_]+);" % k, src).group(1).replace("_", ""))
    return out


def swap_ladders(node, n):
    """Replace every SwitchByBuff on LADDER (in effect lists and in applied_effects' wrappers) with NATIVE."""
    if isinstance(node, dict):
        for key, v in list(node.items()):
            if isinstance(v, dict) and v.get("type") == "SwitchByBuff" and v.get("buff_name") == LADDER:
                node[key] = dict(NATIVE)
                n[0] += 1
            else:
                swap_ladders(v, n)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, dict) and v.get("type") == "SwitchByBuff" and v.get("buff_name") == LADDER:
                node[i] = dict(NATIVE)
                n[0] += 1
            else:
                swap_ladders(v, n)


def build():
    k = rust_consts()
    p = kit.P
    want = {"P_CD": p["p_cd"], "P_R": p["p_r"], "P_HEAL": p["p_heal"], "P_AP": p["p_ap"], "P_ALLY": p["p_ally"],
            "P_ALLY_AP": p["p_ally_ap"]}
    bad = {key: (k[key], v) for key, v in want.items() if k[key] != v}
    if bad:
        sys.exit(f"src/lib.rs's numbers are not build_alistar.P's (src, P): {bad}")
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = copy.deepcopy(json.load(f))
    if champion.get("passive"):
        sys.exit("Alistar has a passive in the main pack now: update this script")
    n = [0]
    for s in ("attack", "skill", "skill2", "ult"):
        swap_ladders(champion[s], n)
    if n[0] != 4:
        sys.exit(f"the main pack's roar ladder is in {n[0]} places, not 4 (Q's slam, W's headbutt and slam, E's punch): "
                 "update this script")
    left = [x for x in (HERO + "_p1", HERO + "_p2", HERO + "_p_cd")
            if x in json.dumps([champion[s] for s in ("attack", "skill", "skill2", "ult")])]
    if left:
        sys.exit(f"the data's roar is still in the copy ({left}): update this script")
    champion["passive"] = {"passive_ref": MOD_ID + ":roar", "params": {}}
    champion[SLOT]["description"] = "#asset/base/text/champion?description." + TEXT_ID + "." + SLOT

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        t = tab["description"][HERO][SLOT]
        old = OLD[lang].format(need=p["p_need"])
        if t.count(old) != 1:
            sys.exit(f"{lang} {HERO}.{SLOT}: the main pack's stacking rule ({old!r}) is not in its text: update this script")
        t = LEAD[lang] + t.replace(old, NEW[lang].format(need=k["NEED"], big=k["BIG_STACKS"]))
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
