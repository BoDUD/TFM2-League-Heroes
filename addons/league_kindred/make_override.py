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

0.2.0 (2026-11-11, the user: 「千珏印记是不是不能印记英雄啊 你看看 如果不能的话就要改了」): the copy is also built with
p_native=1 - the attack carries none of the data's takedown tracking - and gets the passive league_kindred:hunt
(src/hunt.rs: League's Lamb hunts, marks kept through death; params = the kit's mark: as / ap / show), the pictures
of a hunted champion (the add-on's effects/league_kindred_hunt, tools/art/fx_kindred_hunt.py: `wait` until the hunt
arms, `on` after; one pair of names a team) and the passive's tooltip (description.league_kindred_respite.attack).
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
import stack_nums  # noqa: E402  (the stack numbers' bindings stay last, as in the main pack)

TEXT_ID = "league_kindred_respite"      # the text's key (the hero's own id is league_kindred)
# the add-on copy's own numbers: R read from health saves more, and she came out at +2.09 / +1.96 against the jungle
# peers' +1.31 / +1.30 (hooked SDK simulation, Temp/kn_sim kn_hook.rs). The user kept the 4 s circle
# (「保留 4 秒法阵」): R's cooldown League's 120 s, its end heal 40 + 10% AD, attack 88 -> +1.29 / +1.16 (h12)
NUMBERS = {"r_cd": 7200, "r_heal": 40, "r_heal_ad": 10, "atk": 88}
HERO = "league_kindred"
A, G, O, E = setup.A, setup.G, setup.O, setup.E
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
HUNT_ANIM = "asset/league_kindred/effects/league_kindred_hunt"
# src/hunt.rs's names: the hunted champion's two pictures (a pair a team), her mark, its flag, picture and sound
HUNT_VIEWS = {"league_kindred_hunt_wait_b": "wait", "league_kindred_hunt_wait_r": "wait",
              "league_kindred_hunted_b": "on", "league_kindred_hunted_r": "on"}
HUNT_NAMES = ("league_kindred_p_mark", "league_kindred_p_has", "league_kindred_p_stack", "league_kindred_p")
# the passive's tooltip: League's Lamb hunts (src/hunt.rs PICK_EVERY 75 s, ARM_T 8 s, IMMUNE_T 240 s)
ATTACK = {
    "zh-hans": O + "千珏之印" + E + "：羊灵每" + A + "75秒" + E + "指名一名敌方英雄狩猎（头顶出现印记，" + A + "8秒" + E +
               "后生效）。参与击杀被狩猎的英雄获得一层印记，死亡不清空：射程+{p_range}、攻速+{p_as}%、" + O + "横生惧意" + E + "+" +
               setup.M + "{p_e}魔法伤害" + E + "。",
    "zh-hant": O + "鏡爪印記" + E + "：每" + A + "75秒" + E + "指名一名敵方英雄狩獵（頭頂出現印記，" + A + "8秒" + E +
               "後生效）。參與擊殺被狩獵的英雄獲得一層印記，陣亡不清空：射程+{p_range}、攻速+{p_as}%、" + O + "恐懼蔓延" + E + "+" +
               setup.M + "{p_e}魔法傷害" + E + "。",
    "en": O + "Mark of the Kindred" + E + ": every " + A + "75s" + E + " Lamb names an enemy champion to hunt (a mark over "
          "them, live after " + A + "8s" + E + "). A takedown on the hunted champion gives a mark, kept through death: "
          "+{p_range} range, +{p_as}% attack speed, " + O + "Mounting Dread" + E + " +" + setup.M + "{p_e} magic damage" + E + ".",
    "ko": O + "킨드레드의 표식" + E + ": " + A + "75초" + E + "마다 적 챔피언 하나를 사냥감으로 지목(머리 위 표식, " + A + "8초" + E +
          " 후 활성). 사냥감 처치에 관여하면 표식 획득(사망해도 유지): 사거리 +{p_range}, 공격 속도 +{p_as}%, " + O + "차오르는 공포" + E +
          " " + setup.M + "마법 피해 +{p_e}" + E + ".",
    "ja": O + "キンドレッドの刻印" + E + "：" + A + "75秒" + E + "ごとに敵チャンピオン1体を獲物に指名（頭上に刻印、" + A + "8秒" + E +
          "後に有効）。獲物のキルに関与すると刻印（死亡しても残る）：射程+{p_range}、攻撃速度+{p_as}%、" + O + "忍び寄る恐怖" + E + "の" +
          setup.M + "魔法ダメージ+{p_e}" + E + "。",
}
# R's tooltip: the add-on's rule (src/lib.rs DANGER_HP 30 %, BURST 30 % in BURST_T 60 ticks, an enemy champion close)
ULT = {
    "zh-hans": "法阵范围内有友方英雄（队友或她自己）快要阵亡时（生命低于" + A + "30%" + E + "或" + A + "1秒" + E +
               "内被打掉三成，且敌方英雄在旁），祝福身边区域：" + A + "{r_t}秒" + E + "内其中的英雄敌我都不会阵亡，结束时都回复" +
               setup.HEAL + "生命。",
    "zh-hant": "法陣範圍內有友方英雄（隊友或她自己）快要陣亡時（生命低於" + A + "30%" + E + "或" + A + "1秒" + E +
               "內被打掉三成，且敵方英雄在旁），祝福身邊區域：" + A + "{r_t}秒" + E + "內其中的英雄敵我都不會陣亡，結束時都回復" +
               setup.HEAL + "生命。",
    "en": "When an allied champion in her circle - a teammate or herself - is about to die (below " + A + "30%" + E +
          " health, or 30% lost within " + A + "1s" + E + ", with an enemy champion close), she blesses the ground around "
          "her: for " + A + "{r_t}s" + E + " nobody in it, ally or enemy, can die, and when it ends they all heal " + setup.HEAL + ".",
    "ko": "원 안의 아군 챔피언(아군 또는 자신)이 죽기 직전일 때(체력 " + A + "30%" + E + " 미만이거나 " + A + "1초" + E +
          " 안에 30% 이상 잃고 적 챔피언이 가까이 있을 때) 주변을 축복: " + A + "{r_t}초" + E + " 동안 안에서는 아군도 적도 죽지 않고, "
          "끝날 때 모두 " + setup.HEAL + " 회복.",
    "ja": "円の中の味方チャンピオン（味方か自身）が倒れそうな時（体力" + A + "30%" + E + "未満か" + A + "1秒" + E +
          "で30%以上失い、敵チャンピオンが近い時）周囲を祝福：" + A + "{r_t}秒" + E + "間、中では敵も味方も倒れず、終了時に全員" +
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
    champion = kit.build(dict(p, r_now=1, p_native=1, **NUMBERS))
    if json.dumps(champion["ult"]) == json.dumps(kit.build(p)["ult"]):
        sys.exit("r_now=1 left R as it was: update this script")
    if "league_kindred_k_a" in json.dumps(champion["attack"]):
        sys.exit("p_native=1 left the data's takedown tracking in the attack: update this script")
    if "passive" in champion:
        sys.exit("the main pack's Kindred has a passive now: update this script")
    # the names src/hunt.rs lays are the main kit's (in the copy only the native passive lays the mark)
    main_kit = json.dumps(kit.build(p))
    lost = [n for n in HUNT_NAMES if f'"{n}"' not in main_kit]
    if lost:
        sys.exit(f"src/hunt.rs's names are not in the kit any more: {lost}")
    # her marks' range is league.dll's league:range reading league_kindred_p_mark: the copy's data lays no mark any more,
    # so the node stays in the attack by force
    champion = kit.range_buffs.apply(champion, force=True)
    champion["passive"] = {"passive_ref": "league_kindred:hunt",
                           "params": {"ap": p["p_ap"], "as": p["p_as"], "show": p["p_show"]}}
    champion["view_buffs"] += [{"type": "Animated", "name": name, "anim": HUNT_ANIM, "tag": tag, "repeat": True, "z": 4}
                               for name, tag in HUNT_VIEWS.items()]
    champion = stack_nums.apply(champion)
    champion["ult"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.ult"
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"

    values = setup.values(dict(p, **NUMBERS))
    texts = {lang: {"attack": (LEAD[lang] + ATTACK[lang]).format(**values), "ult": (LEAD[lang] + t).format(**values)}
             for lang, t in ULT.items()}
    long = {f"{lang}.{k}": setup.shown_length(v) for lang, d in texts.items() for k, v in d.items()
            if setup.shown_length(v) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
        print(lang, " ".join(f"{k}:{setup.shown_length(v)}/{setup.TOOLTIP_MAX[lang]}" for k, v in d.items()))
    print(out)
    print(tpath)


if __name__ == "__main__":
    main()
