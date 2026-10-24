"""Build the add-on's copy of Annie from the main pack (Disintegrate refunds half its cooldown on a kill).

    python addons/league_annie_q/make_override.py [--check]

Reads the main pack's league/champion/league_annie.data_champion and writes
addons/league_annie_q/override/league_annie.data_champion and .../text/champion.i18n: the same kit with -
  * both Q fireballs (TargetProjectile league_annie_q, 70 + 65% AP) calling the native effect league_annie_q:refund after
    their damage (it cuts Q's cooldown when the one struck died);
  * Q's tooltip pointing to description.league_annie_q.skill with one sentence added.
Every other champion stays untouched. Run it again whenever the main pack's Annie changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_annie_q")
MOD_ID = "league_annie_q"
HERO = "league_annie"
SLOT = "skill"
TEXT_KEY = "description." + MOD_ID + "." + SLOT
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}
Y, E = "<#ffb900ff>", "<>"
SWAPS = {
    "zh-hans": ("的<#a974ffff>魔法伤害<>。", "的<#a974ffff>魔法伤害<>。击杀目标时返还一半冷却。"),
    "zh-hant": ("的<#a974ffff>魔法傷害<>。", "的<#a974ffff>魔法傷害<>。擊殺目標時返還一半冷卻。"),
    "en": ("<#a974ffff>magic damage<>.", "<#a974ffff>magic damage<>. A kill refunds half its cooldown."),
    "ko": ("<#a974ffff>마법 피해<>를 입힙니다.", "<#a974ffff>마법 피해<>를 입힙니다. 대상을 처치하면 재사용 대기시간 절반을 돌려받습니다."),
    "ja": ("<#a974ffff>魔法ダメージ<>を与える。", "<#a974ffff>魔法ダメージ<>を与える。倒すとCDが半分戻る。"),
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
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8-sig") as f:
        champion = json.load(f)
    call = {"casting_type": "Targeting", "effect": {"type": "Native", "effect_ref": MOD_ID + ":refund"}}

    def is_ball(o):
        return o.get("type") == "TargetProjectile" and o.get("name") == "league_annie_q"

    def add(o):
        hits = [a["effect"] for a in o["applied_effects"] if a["effect"].get("type") == "ApAttack"]
        if [(h["damage"], h["attack_ratio"]) for h in hits] != [(70, 65)]:
            sys.exit("Annie's Q damage changed: update this script")
        return dict(o, applied_effects=o["applied_effects"] + [call])

    n = []
    champion[SLOT] = replace(champion[SLOT], is_ball, add, n)
    if len(n) != 2 or champion[SLOT]["cooltime"] != 240:
        sys.exit(f"Annie's Q ({len(n)} fireballs, cooldown {champion[SLOT]['cooltime']}) changed: update src/lib.rs's REFUND")
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
