"""Build the add-on's copy of Kindred from the main pack (Lamb's Respite only to save someone about to die).

    python addons/league_kindred/make_override.py

Rebuilds Kindred with tools/kit/build_kindred.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_kindred.data_champion byte for byte (so the copy never drifts from the shipped kit) and that
src/lib.rs's R numbers are the kit's (R_CAST_RANGE = r_arm_range, R_RADIUS = r_r, R_AT = r_at), and writes
addons/league_kindred/override/league_kindred.data_champion and .../text/champion.i18n: the build with r_now=1 - R saves
on the cast itself (the circle at r_at; no arming window, no refund, no danger check in the attack, Q or E), the AI hook
league_kindred:ult decides when - and R's tooltip pointing to description.league_kindred_respite.ult with the add-on's
wording (a lead that shows in game whether the override took). Every other champion stays untouched. Run it again
whenever the main pack's Kindred changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_kindred")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_kindred as kit  # noqa: E402
import setup_kindred as setup  # noqa: E402

TEXT_ID = "league_kindred_respite"      # the text's key (the hero's own id is league_kindred)
# the add-on copy's own numbers: R read from health saves more, and she came out at +2.09 / +1.96 against the jungle
# peers' +1.31 / +1.30 (hooked SDK simulation, Temp/kn_sim kn_hook.rs). The user kept the 4 s circle
# (「保留 4 秒法阵」): R's cooldown League's 120 s, its end heal 40 + 10% AD, attack 88 -> +1.29 / +1.16 (h12)
NUMBERS = {"r_cd": 7200, "r_heal": 40, "r_heal_ad": 10, "atk": 88}
HERO = "league_kindred"
A, G, O, E = setup.A, setup.G, setup.O, setup.E
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
# R's tooltip: the add-on's rule (src/lib.rs DANGER_HP 30 %, BURST 30 % in BURST_T 60 ticks, an enemy champion close)
ULT = {
    "zh-hans": "法阵范围内有友方英雄（队友或她自己）快要阵亡时（生命低于" + A + "30%" + E + "或" + A + "1秒" + E +
               "内被打掉三成，且敌方英雄在旁），祝福身边区域：" + A + "{r_t}秒" + E + "内其中的友方英雄不会阵亡，结束时回复" +
               setup.HEAL + "生命。",
    "zh-hant": "法陣範圍內有友方英雄（隊友或她自己）快要陣亡時（生命低於" + A + "30%" + E + "或" + A + "1秒" + E +
               "內被打掉三成，且敵方英雄在旁），祝福身邊區域：" + A + "{r_t}秒" + E + "內其中的友方英雄不會陣亡，結束時回復" +
               setup.HEAL + "生命。",
    "en": "When an allied champion in her circle - a teammate or herself - is about to die (below " + A + "30%" + E +
          " health, or 30% lost within " + A + "1s" + E + ", with an enemy champion close), she blesses the ground around "
          "her: for " + A + "{r_t}s" + E + " allied champions in it cannot die, and when it ends they heal " + setup.HEAL + ".",
    "ko": "원 안의 아군 챔피언(아군 또는 자신)이 죽기 직전일 때(체력 " + A + "30%" + E + " 미만이거나 " + A + "1초" + E +
          " 안에 30% 이상 잃고 적 챔피언이 가까이 있을 때) 주변을 축복: " + A + "{r_t}초" + E + " 동안 안의 아군 챔피언은 죽지 않고, "
          "끝날 때 " + setup.HEAL + " 회복.",
    "ja": "円の中の味方チャンピオン（味方か自身）が倒れそうな時（体力" + A + "30%" + E + "未満か" + A + "1秒" + E +
          "で30%以上失い、敵チャンピオンが近い時）周囲を祝福：" + A + "{r_t}秒" + E + "間、中の味方チャンピオンは倒れず、終了時に" +
          setup.HEAL + "回復。",
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def lib_consts():
    """src/lib.rs's R numbers: {name: value}."""
    with open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8") as f:
        src = f.read()
    out = {}
    for name in ("R_CAST_RANGE", "R_RADIUS", "R_AT"):
        m = re.search(r"pub const %s: (?:f64|usize) = ([0-9_.]+);" % name, src)
        if not m:
            sys.exit("no %s in src/lib.rs: update this script" % name)
        out[name] = float(m.group(1).replace("_", ""))
    return out


def main():
    p = dict(kit.P)
    if "r_now" not in p:
        sys.exit("build_kindred.P has no r_now: the kit cannot build the add-on's R yet")
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_kindred differs from build_kindred.P: rebuild it first")
    c = lib_consts()
    want = {"R_CAST_RANGE": p["r_arm_range"], "R_RADIUS": p["r_r"], "R_AT": p["r_at"]}
    off = {k: (c[k], v) for k, v in want.items() if abs(c[k] - v) > 1e-6}
    if off:
        sys.exit("src/lib.rs's R numbers are not the kit's (lib.rs, kit): %s" % off)
    champion = kit.build(dict(p, r_now=1, **NUMBERS))
    if json.dumps(champion["ult"]) == json.dumps(kit.build(p)["ult"]):
        sys.exit("r_now=1 left R as it was: update this script")
    champion["ult"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.ult"

    values = setup.values(dict(p, **NUMBERS))
    texts = {lang: {"ult": (LEAD[lang] + t).format(**values)} for lang, t in ULT.items()}
    long = {f"{lang}.ult": setup.shown_length(d["ult"]) for lang, d in texts.items()
            if setup.shown_length(d["ult"]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(champion))
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(tpath)), exist_ok=True)
    with open(lp(tpath), "w", encoding="utf-8", newline="") as f:
        f.write(dumps_main(i18n))
    for lang, d in texts.items():
        print(lang, f"ult:{setup.shown_length(d['ult'])}/{setup.TOOLTIP_MAX[lang]}")
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
