"""Build the add-on's copy of Rengar from the main pack (Unseen Predator from the map's bushes).

    python addons/league_rengar_bush/make_override.py

Rebuilds Rengar with tools/kit/build_rengar.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_rengar.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_rengar_bush/override/league_rengar.data_champion and .../text/champion.i18n: the build with native=1 -
  * the main pack's readiness all kept: the respawn, R and the "ready after quiet ticks" check (`league_rengar_fight`,
    back since 0.2.0, 2026-11-03: without it a fight began with a leap only when the AI had just walked through a bush,
    the players: 「他的跳跃机制非常不稳定，有时候会跳，有时候不跳」);
  * passive = the add-on's league_rengar_bush:bush with {leap_range}: every tick it readies the pounce while he stands
    in a bush and, in a fight, takes that readiness back when he leaves it;
  * the attack runs the add-on's native league_rengar_bush:aim on its target just before it reads `ready`: at a tower or
    the nexus the readiness is set aside (the pounce's landing never hit one) and comes back for the next unit;
  * the attack's tooltip (the passive) points to description.league_rengar_bush.attack with a "bush build" lead and the
    bush wording, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Rengar changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_rengar_bush")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_rengar as kit  # noqa: E402
import setup_rengar as setup  # noqa: E402

MOD_ID = "league_rengar_bush"
HERO = "league_rengar"
# lang -> (the lead, the main pack's readiness wording, the same with the bush first). 0.2.0 keeps the out-of-combat
# readiness, so the wording grew and the leads shrank ("test build" -> "bush build"): zh-hans 130/130, en 334/334 and
# ja 147/147 sit at TOOLTIP_MAX
NATIVE = {
    "zh-hans": ("【草丛版】", "复活、脱战" + setup.A + "{quiet}秒" + setup.E + "或R后",
                "草丛里、复活、脱战" + setup.A + "{quiet}秒" + setup.E + "或R后"),
    "zh-hant": ("【草叢版】", "復活、脫戰" + setup.A + "{quiet}秒" + setup.E + "或R後",
                "草叢裡、復活、脫戰" + setup.A + "{quiet}秒" + setup.E + "或R後"),
    "en": ("[Bush] ", "on respawn, after " + setup.A + "{quiet}s" + setup.E + " out of combat or after R",
           "in brush, on respawn, " + setup.A + "{quiet}s" + setup.E + " out of combat or after R"),
    "ko": ("[수풀] ", "부활, " + setup.A + "{quiet}초" + setup.E + " 비전투 또는 R 후",
           "수풀 안, 부활, " + setup.A + "{quiet}초" + setup.E + " 비전투 또는 R 후"),
    "ja": ("【茂み版】", "復活時、" + setup.A + "{quiet}秒" + setup.E + "非戦闘またはR後",
           "茂みの中、復活時、" + setup.A + "{quiet}秒" + setup.E + "非戦闘またはR後"),
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", "league_rengar.data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_rengar differs from build_rengar.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    text = json.dumps(champion)
    if "league_rengar_fight" not in text:
        sys.exit("the copy lost the quiet-ticks check (league_rengar_fight, which src/lib.rs reads): update this script")
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":bush":
        sys.exit("the copy has no league_rengar_bush:bush passive: update this script")
    effects = champion["attack"]["effect"]["effects"]
    aim = [i for i, e in enumerate(effects) if e.get("effect_ref") == MOD_ID + ":aim"]
    reads = [i for i, e in enumerate(effects) if e.get("type") == "SwitchByBuff" and e.get("buff_name") == HERO + "_ready"]
    if len(aim) != 1 or len(reads) != 1 or aim[0] > reads[0]:
        sys.exit("the copy's attack must run league_rengar_bush:aim once, before it reads league_rengar_ready")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"

    values = setup.values(p)
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

    out = os.path.join(ADDON, "override", "league_rengar.data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no bush-build text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: {"attack": texts[lang]}}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {lang: f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}" for lang, t in texts.items()})


if __name__ == "__main__":
    main()
