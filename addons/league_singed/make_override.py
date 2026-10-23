"""Build the add-on's copy of Singed from the main pack (Fling as in League).

    python addons/league_singed/make_override.py [--draft]

Rebuilds Singed with tools/kit/build_singed.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_singed.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
add-on's constants (src/lib.rs E_FLY, E_BEHIND, E_ROOT, W_P) are P's, and writes
addons/league_singed/override/league_singed.data_champion and .../text/champion.i18n: the build with native=1 -
  * Fling's pull and its root while the glue lies become the native effect league_singed:fling (a knock-up over his
    shoulder, rooted only when it lands in the glue);
  * the skill's tooltip points to description.league_singed_addon.skill with the add-on's wording, so the tooltip in game
    shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Singed changes.
--draft: only the copy, without the main-pack check and the texts (before the main pack has Singed; the unit tests read
the copy).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_singed")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_singed as kit  # noqa: E402

TEXT_ID = "league_singed_addon"      # the texts' key (the hero's own id is league_singed)
HERO = "league_singed"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
CONSTS = {"E_FLY": "e_fly", "E_BEHIND": "e_behind", "E_ROOT": "e_root", "W_P": "w_p"}


def texts(setup):
    O, E, A = setup.O, setup.E, setup.A
    mag, tr = setup.mag, setup.tr
    return {
        "zh-hans": {"skill": O + "过肩摔" + E + "：抓住目标造成" + mag("e_dmg", "e_ap") + "魔法伤害和" + tr("最大生命{e_thp}%") +
                             "，把它击飞、从头顶扔到身后；落进" + O + "强力粘胶" + E + "里就禁锢" + A + "{e_root}秒" + E + "。"},
        "zh-hant": {"skill": O + "過肩摔" + E + "：抓住目標造成" + mag("e_dmg", "e_ap") + "魔法傷害和" + tr("最大生命{e_thp}%") +
                             "，把它擊飛、從頭頂扔到身後；落進" + O + "強力粘膠" + E + "裡就禁錮" + A + "{e_root}秒" + E + "。"},
        "en": {"skill": O + "Fling" + E + ": deals " + mag("e_dmg", "e_ap") + " magic damage and " + tr("{e_thp}% max health") +
                        ", knocks the target up and throws it over his shoulder; landing in " + O + "Mega Adhesive" + E +
                        " roots it for " + A + "{e_root}s" + E + "."},
        "ko": {"skill": O + "던져넘기기" + E + ": " + mag("e_dmg", "e_ap") + " 마법 피해와 " + tr("최대 체력의 {e_thp}%") +
                        ", 대상을 띄워 어깨 너머 뒤로 던짐; " + O + "초강력 접착제" + E + "에 떨어지면 " + A + "{e_root}초" + E +
                        " 속박."},
        "ja": {"skill": O + "すくい投げ" + E + "：" + mag("e_dmg", "e_ap") + "の魔法ダメージと" + tr("最大体力の{e_thp}%") +
                        "、対象を打ち上げ肩越しに背後へ投げる。" + O + "強力粘着剤" + E + "に落ちると" + A + "{e_root}秒" + E +
                        "スネア。"},
    }


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_consts(p):
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for const, key in CONSTS.items():
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != p[key]:
            sys.exit(f"src/lib.rs {const} is not P's {key} = {p[key]}: update the add-on")


def main():
    draft = "--draft" in sys.argv[1:]
    p = dict(kit.P)
    check_consts(p)
    champion = kit.build(dict(p, native=1))
    if "league_singed:fling" not in json.dumps(champion):
        sys.exit("the copy does not call the add-on: update this script")
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    if not draft:
        import setup_singed as setup  # noqa: E402
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_singed differs from build_singed.P: rebuild it first")
        champion["skill"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.skill"
        text = texts(setup)
        values = setup.values(p)
        done = {lang: {k: (LEAD[lang] + t[k]).format(**values) for k in t} for lang, t in text.items()}
        long = {f"{lang}.{k}": setup.shown_length(LEAD[lang] + text[lang][k]) for lang in text for k in text[lang]
                if setup.shown_length(LEAD[lang] + text[lang][k]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
        if long:
            sys.exit("tooltip too long for the details panel: %s" % long)
        i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in done.items()}
        tpath = os.path.join(ADDON, "text", "champion.i18n")
        os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
        with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
            f.write(dumps_main(i18n))
        print(tpath)
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    print(out, "(draft)" if draft else "")


if __name__ == "__main__":
    main()
