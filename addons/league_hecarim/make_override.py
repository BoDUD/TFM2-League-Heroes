"""Build the add-on's copy of Hecarim from the main pack (Rampage's cooldown shorter for each stack, as in League).

    python addons/league_hecarim/make_override.py [--check]

Rebuilds Hecarim with tools/kit/build_hecarim.py (its parameter table P), checks that the build is the main pack's
league/champion/league_hecarim.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_hecarim/override/league_hecarim.data_champion and .../text/champion.i18n: the same kit with -
  * the passive league_hecarim:rampage (src/lib.rs): when he casts Rampage, CUT ticks off its cooldown for each stack he
    holds (the main pack's flags league_hecarim_q1 / q2), the skill slot alone;
  * Rampage's tooltip pointing to description.league_hecarim_addon.skill, one clause added.
Every other champion stays untouched. Run it again whenever the main pack's Hecarim changes (--check: compare only, CI).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_hecarim")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_hecarim as kit  # noqa: E402

MOD_ID = "league_hecarim"
HERO = "league_hecarim"
TEXT_ID = "league_hecarim_addon"      # the texts' key (the hero's own id is league_hecarim)
SLOT = "skill"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
A, E = "<#ffb900ff>", "<>"
# the main pack's per-stack damage clause (its q_stk written in) -> the same with the cooldown cut
SWAPS = {
    "zh-hans": ("每层伤害+{stk}%。", "每层伤害+{stk}%、Q的冷却缩短" + A + "{cut}秒" + E + "。"),
    "zh-hant": ("每層傷害+{stk}%。", "每層傷害+{stk}%、Q的冷卻縮短" + A + "{cut}秒" + E + "。"),
    "en": ("each +{stk}% damage", "each +{stk}% damage and " + A + "{cut}s" + E + " off Rampage's cooldown"),
    "ko": ("중첩당 피해 +{stk}%.", "중첩당 피해 +{stk}%, 재사용 대기시간 " + A + "{cut}초" + E + " 감소."),
    "ja": ("1つごとにダメージ+{stk}%。", "1つごとにダメージ+{stk}%、クールダウン" + A + "{cut}秒" + E + "短縮。"),
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


def secs(ticks):
    return ("%.2f" % (ticks / 60)).rstrip("0").rstrip(".")


def build():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    cut = int(re.search(r"pub const CUT: usize = (\d+);", src).group(1))
    p = dict(kit.P)
    timing = {k: int(re.search(r"pub const %s: usize = (\d+);" % k, src).group(1)) for k in ("Q_ACTION", "Q_HIT")}
    if timing != {"Q_ACTION": p["q_dur"], "Q_HIT": p["q_at"]}:
        sys.exit(f"src/lib.rs's {timing} are not build_hecarim.P's q_dur {p['q_dur']} / q_at {p['q_at']}: update them")
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps(kit.build(p)) != shipped:
        sys.exit("the main pack's league_hecarim differs from build_hecarim.P: rebuild it first")
    champion = kit.build(p)
    if champion.get("passive"):
        sys.exit("Hecarim has a passive in the main pack now: update this script")
    for f in ("q1", "q2"):
        if f'"name": "{HERO}_{f}"' not in json.dumps(champion[SLOT]):
            sys.exit(f"Rampage no longer stacks with {HERO}_{f}: update src/lib.rs (STACK_1 / STACK_2)")
    champion["passive"] = {"passive_ref": MOD_ID + ":rampage", "params": {}}
    champion[SLOT]["description"] = "#asset/base/text/champion?description." + TEXT_ID + "." + SLOT

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    texts = {}
    for lang, tab in main_text.items():
        t = tab["description"][HERO][SLOT]
        old, new = (x.format(stk=p["q_stk"], cut=secs(cut)) for x in SWAPS[lang])
        if t.count(old) != 1:
            sys.exit(f"{lang} {HERO}.{SLOT}: the main pack's text changed ({old!r} not found once): update this script")
        t = LEAD[lang] + t.replace(old, new)
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
