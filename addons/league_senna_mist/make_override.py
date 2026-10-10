"""Build the add-on's copy of Senna from the main pack (her Mist kept through death, as in League).

    python addons/league_senna_mist/make_override.py

Rebuilds Senna with tools/kit/build_senna.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_senna.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_senna_mist/override/league_senna.data_champion and .../text/champion.i18n: the build with two changes -
  * passive = the add-on's league_senna_mist:keep (no params): every Mist layer she gathers comes back the moment death
    clears it (src/lib.rs), the odd/even switch league_senna_m_odd set to match;
  * the attack's tooltip (the passive) points to description.league_senna_mist.attack: the main text with its "lost on
    death" clause (setup_senna.DEATH) swapped for "kept (add-on)".
Every other champion stays untouched. Run it again whenever the main pack's Senna or her text changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_senna_mist")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_senna as kit  # noqa: E402
import setup_senna as setup  # noqa: E402

MOD_ID = "league_senna_mist"
HERO = "league_senna"
# lang -> the add-on's clause in place of setup.DEATH[lang] (no longer: the main text is at the panel's limit)
KEPT = {"zh-hans": "（扩展包保留）", "zh-hant": "（擴充包保留）", "en": " (kept: add-on)", "ja": "（拡張で保持）",
        "ko": "(확장팩: 유지)"}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_senna differs from build_senna.P: rebuild it first")
    champion = kit.build(p, native=True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":keep":
        sys.exit("the copy has no league_senna_mist:keep passive: update build_senna.py")
    for name in ("league_senna_mist", "league_senna_m_odd"):
        if f'"name": "{name}", "duration": "Permanent"' not in json.dumps(champion["attack"]):
            sys.exit(f"{name} is no longer a Permanent caster buff in the attack: update src/lib.rs")
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{MOD_ID}.attack"

    texts = {}
    for lang, (d, _) in setup.texts(p).items():
        old = setup.DEATH[lang]
        if d["attack"].count(old) != 1:
            sys.exit(f"{lang}: the main pack's passive text changed ({old!r} not found once): update KEPT")
        texts[lang] = d["attack"].replace(old, KEPT[lang])
    long = {lang: setup.shown_length(t) for lang, t in texts.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
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
          champion["passive"]["passive_ref"])
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
