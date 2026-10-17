"""Build the add-on's copy of Gwen from the main pack (A Thousand Cuts as % max-health magic damage).

    python addons/league_gwen/make_override.py

Rebuilds Gwen with tools/kit/build_gwen.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_gwen.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
add-on's constants (src/lib.rs P_HP, P_HP_AP) are P's p_hp and p_hp_ap, and writes
addons/league_gwen/override/league_gwen.data_champion and .../text/champion.i18n: the build with native=1 -
  * every passive hit on an enemy champion: the true p_hp% max-health damage is the add-on's `Native` league_gwen:cuts
    (p_hp% + p_hp_ap / 100 % per 100 AP of the champion's maximum health as magic damage); the heal stays data;
  * the attack's tooltip (the passive) points to description.league_gwen.attack with a "test build" lead and the magic
    wording, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Gwen changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_gwen")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_gwen as kit  # noqa: E402
import setup_gwen as setup  # noqa: E402

MOD_ID = "league_gwen"
MAGIC = "<#a974ffff>"
# lang -> (the lead, the main pack's true-damage wording, the magic wording; {x} = p_hp_ap / 100)
NATIVE = {
    "zh-hans": ("【魔法伤害测试版】", "<#f5f5f5ff>{p_hp}%最大生命值真实伤害<>",
                MAGIC + "{p_hp}%（每100法强+{x}%）最大生命值魔法伤害<>"),
    "zh-hant": ("【魔法傷害測試版】", "<#f5f5f5ff>{p_hp}%最大生命值真實傷害<>",
                MAGIC + "{p_hp}%（每100法強+{x}%）最大生命值魔法傷害<>"),
    "en": ("[Magic test build] ", "<#f5f5f5ff>{p_hp}% max health true damage<>",
           MAGIC + "{p_hp}% (+{x}% per 100 AP) max health magic damage<>"),
    "ko": ("[마법 피해 테스트판] ", "<#f5f5f5ff>최대 체력의 {p_hp}% 고정 피해<>",
           MAGIC + "최대 체력의 {p_hp}%(주문력 100당 +{x}%) 마법 피해<>"),
    "ja": ("【魔法ダメージテスト版】", "<#f5f5f5ff>最大体力の{p_hp}%の確定ダメージ<>",
           MAGIC + "最大体力の{p_hp}%(魔力100毎に+{x}%)の魔法ダメージ<>"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_const(name):
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        m = re.search(rf"pub const {name}: \w+ = ([\d_]+);", f.read())
    if not m:
        sys.exit(f"src/lib.rs has no const {name}")
    return int(m.group(1).replace("_", ""))


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_gwen.data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_gwen differs from build_gwen.P: rebuild it first")
    for const, key in (("P_HP", "p_hp"), ("P_HP_AP", "p_hp_ap")):
        if rust_const(const) != p[key]:
            sys.exit(f"src/lib.rs {const} = {rust_const(const)} but P[{key!r}] = {p[key]}: make them agree")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    n = text.count(f'"effect_ref": "{MOD_ID}:cuts"')
    if not n or '"target_hp_ratio": %d' % p["p_hp"] in text:
        sys.exit("the copy still has the true max-health damage or no league_gwen:cuts: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = dict(setup.values(p), x=f"{p['p_hp_ap'] / 100:g}")
    texts = {}
    for lang, (lead, old, new) in NATIVE.items():
        attack = setup.TEXT[lang]["attack"]
        if attack.count(old) != 1:
            sys.exit(f"{lang}: the main pack's passive text changed ({old!r} not found once): update NATIVE")
        texts[lang] = (lead + attack.replace(old, new)).format(**values)
    long = {lang: setup.shown_length(t) for lang, t in texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", "league_gwen.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no test-build text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "-", n,
          "passive hits on champions are league_gwen:cuts")
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
