"""Build the add-on's copy of Orianna from the main pack (the Ball from where it is, Protect to the ally in danger, Shockwave
for a kill).

    python addons/league_orianna/make_override.py

Rebuilds Orianna with tools/kit/build_orianna.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_orianna.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_orianna/override/league_orianna.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the Ball's three places, W and R where it is, the leash, the controller);
  * Q's throws and E's sends calling league_orianna:q / :e first, E on herself league_orianna:back, the data's own lob and
    homing flying hidden (the add-on draws the Ball from where it is), E's line from her only while the Ball is beside her
    (the add-on hits the line from the Ball, league_orianna:e_hit);
  * E's ally asked of league_orianna:e_pick (each ally in range; the one picked raises league_orianna_e_this);
  * R asking league_orianna:r_kill for each enemy champion near the Ball (a kill raises league_orianna_c2; R fires for
    any enemy champion near the Ball anyway since 0.124.2, so it is the log's R-ARMED / KILL lines);
  * passive = the add-on's league_orianna:ball with the numbers of P;
  * the skills' tooltips point to description.league_orianna.skill / .skill2 / .ult with the add-on's wording
    (keys of the add-on's own id), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Orianna changes.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_orianna")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_orianna as kit  # noqa: E402
import setup_orianna as setup  # noqa: E402

MOD_ID = "league_orianna"
HERO = "league_orianna"
O, A, M, R, G, E = setup.O, setup.A, setup.M, setup.R, setup.G, setup.E
APi = setup.APi
mag = setup.mag
REFS = ("q", "e", "e_hit", "back", "e_pick", "r_kill", "e_cast", "e_try")
# lang -> the add-on's skill, skill2 and ult texts
NATIVE = {
    "zh-hans": {
        "skill": "【附加包】球从它所在的位置飞到敌方英雄脚下并停留，造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "。" + O +
                 "指令：杂音" + E + "：球附近有敌人时自动放电，造成" + mag("w_dmg", "w_ap") + M + "魔法伤害" + E + "，" + R +
                 "减速{w_slow}%" + E + "，队友" + G + "加速{w_haste}%" + E + "。",
        "skill2": "【附加包】球从它所在的位置飞向最危险的队友（自己更危险时回到身边），提供" + G + "{e_sh}" + E + " + " + APi + G +
                  "{e_ap}%护盾" + E + "，路过的敌人受到" + mag("e_dmg", "e_dap") + M + "魔法伤害" + E + "。带球者+{e_def}护甲和魔抗。",
        "ult": "【附加包】待命" + A + "{r_arm}秒" + E + "，球附近有敌方英雄时放出冲击波：造成" +
               mag("r_dmg", "r_ap") + M + "魔法伤害" + E + "并把敌人" + R + "甩向球" + E + "。",
    },
    "zh-hant": {
        "skill": "【擴充包】球從它所在的位置飛到敵方英雄腳下並停留，造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "。" + O +
                 "指令：失衡" + E + "：球附近有敵人時自動放電，造成" + mag("w_dmg", "w_ap") + M + "魔法傷害" + E + "，" + R +
                 "緩速{w_slow}%" + E + "，隊友" + G + "加速{w_haste}%" + E + "。",
        "skill2": "【擴充包】球從它所在的位置飛向最危險的隊友（自己更危險時回到身邊），提供" + G + "{e_sh}" + E + " + " + APi + G +
                  "{e_ap}%護盾" + E + "，路過的敵人受到" + mag("e_dmg", "e_dap") + M + "魔法傷害" + E + "。帶球者+{e_def}護甲和魔抗。",
        "ult": "【擴充包】待命" + A + "{r_arm}秒" + E + "，球附近有敵方英雄時放出脈衝：造成" +
               mag("r_dmg", "r_ap") + M + "魔法傷害" + E + "並把敵人" + R + "甩向球" + E + "。",
    },
    "en": {
        "skill": "[Add-on] The Ball flies from where it is to an enemy champion's feet and stays, dealing " +
                 mag("q_dmg", "q_ap") + " " + M + "magic damage" + E + ". " + O + "Command: Dissonance" + E +
                 ": with enemies near the Ball it pulses by itself for " + mag("w_dmg", "w_ap") + " " + M + "magic damage" +
                 E + ", " + R + "slowing enemies {w_slow}%" + E + " and " + G + "hasting allies {w_haste}%" + E + ".",
        "skill2": "[Add-on] The Ball flies from where it is to the ally in the most danger (back to her when she is in more), "
                  "shielding them for " + G + "{e_sh}" + E + " + " + APi + G + "{e_ap}%" + E + " and dealing " +
                  mag("e_dmg", "e_dap") + " " + M + "magic damage" + E + " to enemies on the way. Its holder gains {e_def} "
                  "Armor and Magic Resist.",
        "ult": "[Add-on] Waits up to " + A + "{r_arm}s" + E + " for an enemy champion near the Ball, then the Ball"
               " sends out a shockwave: " + mag("r_dmg", "r_ap") + " " + M + "magic damage" + E +
               ", enemies " + R + "flung toward the Ball" + E + ".",
    },
    "ko": {
        "skill": "[확장] 공이 있는 곳에서 적 챔피언 발밑으로 날아가 남고 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + ". " + O +
                 "명령: 불협화음" + E + ": 공 근처에 적이 있으면 저절로 " + mag("w_dmg", "w_ap") + "의 " + M + "마법 피해" + E + ", 적 " +
                 R + "{w_slow}% 둔화" + E + ", 아군 " + G + "{w_haste}% 가속" + E + ".",
        "skill2": "[확장] 공이 있는 곳에서 가장 위험한 아군에게 날아가(자신이 더 위험하면 자신) " + G + "{e_sh}" + E + " + " + APi + G +
                  "{e_ap}% 보호막" + E + ", 지나가는 적에게 " + mag("e_dmg", "e_dap") + "의 " + M + "마법 피해" + E +
                  ". 공을 가진 자는 방어력·마법 저항력 +{e_def}.",
        "ult": "[확장] 최대 " + A + "{r_arm}초" + E + " 동안 공 근처에 적 챔피언이 오면 충격파: " +
               mag("r_dmg", "r_ap") + "의 " + M + "마법 피해" + E + ", 적을 공 쪽으로 " + R + "날려 보냅니다" + E + ".",
    },
    "ja": {
        "skill": "【拡張】ボールが今ある場所から敵チャンピオンの足元へ飛んで残り、" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E +
                 "。" + O + "オーダー: 乱磁場" + E + "：ボールの近くに敵がいると自動で放電し" + mag("w_dmg", "w_ap") + "の" + M +
                 "魔法ダメージ" + E + "、敵を" + R + "{w_slow}%スロウ" + E + "、味方は" + G + "{w_haste}%加速" + E + "。",
        "skill2": "【拡張】ボールが今ある場所から最も危険な味方へ飛び（自分の方が危険なら自分）、" + G + "{e_sh}" + E + " + " + APi + G +
                  "{e_ap}%のシールド" + E + "、通り道の敵に" + mag("e_dmg", "e_dap") + "の" + M + "魔法ダメージ" + E +
                  "。持ち主は物理・魔法防御+{e_def}。",
        "ult": "【拡張】最大" + A + "{r_arm}秒" + E + "待機し、ボールの近くに敵チャンピオンがいれば衝撃波：" +
               mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E + "、敵をボールへ" + R + "引き寄せる" + E + "。",
    },
}


def lp(path):
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
        sys.exit("the main pack's league_orianna differs from build_orianna.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":ball":
        sys.exit("the copy has no league_orianna:ball passive: update this script")
    text = json.dumps(champion)
    for ref in REFS:
        if f'"{MOD_ID}:{ref}"' not in text and ref != "e_hit":   # e_hit: the add-on's own line calls it
            sys.exit(f"the copy does not call {MOD_ID}:{ref}: update this script")
    for gone in ('"league_orianna_q_ball"', '"league_orianna_e_ball"', '"league_orianna_r_ra"'):
        if gone in text.replace('"name": "league_orianna_q_ball", "anim"', "").replace(
                '"name": "league_orianna_e_ball", "anim"', ""):
            sys.exit(f"the copy still uses {gone} in its effects: update this script")
    for slot in ("skill", "skill2", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in NATIVE.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
