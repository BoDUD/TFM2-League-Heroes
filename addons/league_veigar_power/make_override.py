"""Build the add-on's copy of Veigar from the main pack (Phenomenal Evil Power kept through death).

    python addons/league_veigar_power/make_override.py

Copies league/champion/league_veigar.data_champion to addons/league_veigar_power/override/league_veigar.data_champion
with two changes: passive = the add-on's league_veigar_power:keep (no params), which puts back every ability power stack
death clears (src/lib.rs), and the attack's tooltip (the passive) points to description.league_veigar_power.attack -
the main text with its "lost on death" clause swapped for "kept (add-on)". Checks first that every stack the main pack
adds is a Permanent league_veigar_p_stack carrying magic power only (the add-on copies the stacks it saw, whatever
their amount). Run it again whenever the main pack's Veigar or his text changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_veigar_power")
MOD_ID = "league_veigar_power"
HERO = "league_veigar"
STACK = "league_veigar_p_stack"
# lang -> (the main pack's clause, the add-on's)
SWAP = {
    "zh-hans": ("死亡时清空。", "【扩展包】死后保留。"),
    "zh-hant": ("死亡時清空。", "【擴充包】死後保留。"),
    "en": ("Lost on death.", "[Add-on] Kept through death."),
    "ko": ("사망하면 사라집니다.", "[확장팩] 사망해도 유지됩니다."),
    "ja": ("デスで失う。", "【拡張】デスでも失わない。"),
}
# the skill details panel's limits (lint_mod.TOOLTIP_MAX)
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def shown_length(text):
    text = re.sub(r"<i#[^>]*>", "*", text)
    return len(re.sub(r"<[^>]*>", "", text))


def buff_states(node, out):
    if isinstance(node, dict):
        if node.get("type") in ("AddCasterBuff", "AddBuff"):
            out.append(node["buff_state"])
        for v in node.values():
            buff_states(v, out)
    elif isinstance(node, list):
        for v in node:
            buff_states(v, out)
    return out


def main():
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    if "passive" in champion:
        sys.exit("the main pack's Veigar has a passive now: update this script")
    stacks = [b for b in buff_states([champion[s] for s in ("attack", "skill", "skill2", "ult")], []) if b["name"] == STACK]
    if not stacks:
        sys.exit(f"no {STACK} in the main pack: update src/lib.rs")
    for b in stacks:
        if b.get("duration") != "Permanent" or set(b) != {"name", "duration", "magic_power"}:
            sys.exit(f"{STACK} is {b} in the main pack: the add-on expects Permanent magic power stacks")
    champion["passive"] = {"passive_ref": f"{MOD_ID}:keep", "params": {}}
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.attack"

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, (old, new) in SWAP.items():
        attack = main_text[lang]["description"][HERO]["attack"]
        if attack.count(old) != 1:
            sys.exit(f"{lang}: the main pack's passive text changed ({old!r} not found once): update SWAP")
        texts[lang] = attack.replace(old, new)
    long = {lang: shown_length(t) for lang, t in texts.items() if shown_length(t) > TOOLTIP_MAX[lang]}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], "-", len(stacks), "stack adds checked")
    print("tooltip lengths", {lang: f"{shown_length(t)}/{TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
