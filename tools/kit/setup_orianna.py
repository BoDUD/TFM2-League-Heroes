"""Orianna's text (5 languages), sound_info files and her keys in the shared files, numbers from build_orianna.P.

    python tools/kit/setup_orianna.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_orianna in every language, description + skill_name),
sound/sfx/league_orianna_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.122.0, Orianna named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 发条魔灵 / 奥莉安娜 - the client swaps name and title: 奥莉安娜; 发条协奏, 指令：攻击,
指令：杂音, 指令：防卫, 指令：冲击波; zh_TW 奧莉安娜 / 發條少女, 魔法發條, 指令：貫穿, 指令：失衡, 指令：守護, 終極指令：脈衝;
ja オリアナ / 時計仕掛けの舞姫, ぜんまい仕掛け, オーダー: 攻撃, オーダー: 乱磁場, オーダー: 防御, オーダー: ショックウェーブ;
ko 오리아나 / 시계태엽 소녀, 시계태엽 감기, 명령: 공격, 명령: 불협화음, 명령: 보호, 명령: 충격파).
Slots: skill = Q (named) with W told in its text (W has no slot: it fires by itself at the ball), skill2 = E, ult = R; the
passive is told in the attack's text. No combo sentence in any text (the user's rule). No `league_orianna_attack` sound:
the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_orianna import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_orianna"
VERSION = "0.122.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7ee787ff>"      # shields, haste
E = "<>"
# champion_view: face from tfm2_ase.py face; no banpick_center - her idle tops at -27.5 game px (lo_ -27.3), inside the
# card's -28 like Riven / Vayne / Akali (the card rule sets it only above -28)
VIEW = {"face": {"x": -4, "y": -37}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "奥莉安娜",
        "attack": "发射发条弹。" + O + "发条协奏" + E + "：普攻附带" + mag("p_dmg", "p_ap") + M + "魔法伤害" + E + "，" + A + "{p_t}秒" + E +
                  "内连续普攻再叠加，最多" + A + "2层" + E + "。",
        "skill": "把球扔到敌方英雄脚下并停留，造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "。" + O + "指令：杂音" + E +
                 "：球附近有敌人时自动放电，造成" + mag("w_dmg", "w_ap") + M + "魔法伤害" + E + "，" + R + "减速{w_slow}%" + E + "，队友" +
                 G + "加速{w_haste}%" + E + "。",
        "skill2": "把球送给离敌人最近的队友（被贴身时给自己），提供" + G + "{e_sh}" + E + " + " + APi + G + "{e_ap}%护盾" + E + "，路过的敌人受到" +
                  mag("e_dmg", "e_dap") + M + "魔法伤害" + E + "。带球者+{e_def}护甲和魔抗。",
        "ult": "待命" + A + "{r_arm}秒" + E + "，球附近有" + A + "2个" + E + "敌方英雄或1个落单目标时放出冲击波：造成" + mag("r_dmg", "r_ap") +
               M + "魔法伤害" + E + "并把敌人" + R + "甩向球" + E + "。",
        "names": ("指令：攻击", "指令：防卫", "指令：冲击波"),
    },
    "zh-hant": {
        "name": "奧莉安娜",
        "attack": "發射發條彈。" + O + "魔法發條" + E + "：普攻附帶" + mag("p_dmg", "p_ap") + M + "魔法傷害" + E + "，" + A + "{p_t}秒" + E +
                  "內連續普攻再疊加，最多" + A + "2層" + E + "。",
        "skill": "把球擲到敵方英雄腳下並停留，造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "。" + O + "指令：失衡" + E +
                 "：球附近有敵人時自動放電，造成" + mag("w_dmg", "w_ap") + M + "魔法傷害" + E + "，" + R + "緩速{w_slow}%" + E + "，隊友" +
                 G + "加速{w_haste}%" + E + "。",
        "skill2": "把球送給離敵人最近的隊友（被貼身時給自己），提供" + G + "{e_sh}" + E + " + " + APi + G + "{e_ap}%護盾" + E + "，路過的敵人受到" +
                  mag("e_dmg", "e_dap") + M + "魔法傷害" + E + "。帶球者+{e_def}護甲和魔抗。",
        "ult": "待命" + A + "{r_arm}秒" + E + "，球附近有" + A + "2個" + E + "敵方英雄或1個落單目標時放出脈衝：造成" + mag("r_dmg", "r_ap") +
               M + "魔法傷害" + E + "並把敵人" + R + "甩向球" + E + "。",
        "names": ("指令：貫穿", "指令：守護", "終極指令：脈衝"),
    },
    "en": {
        "name": "Orianna",
        "attack": "Fires a clockwork bolt. " + O + "Clockwork Windup" + E + ": attacks deal " + mag("p_dmg", "p_ap") + " " + M +
                  "magic damage" + E + " more; attacks within " + A + "{p_t}s" + E + " of each other stack it, up to " + A + "2" + E + ".",
        "skill": "Throws the Ball at an enemy champion's feet, where it stays, dealing " + mag("q_dmg", "q_ap") + " " + M +
                 "magic damage" + E + ". " + O + "Command: Dissonance" + E + ": with enemies near the Ball it pulses by itself for " +
                 mag("w_dmg", "w_ap") + " " + M + "magic damage" + E + ", " + R + "slowing enemies {w_slow}%" + E + " and " + G +
                 "hasting allies {w_haste}%" + E + ".",
        "skill2": "Sends the Ball to the ally nearest the enemy (to herself when an enemy is on her), shielding them for " + G +
                  "{e_sh}" + E + " + " + APi + G + "{e_ap}%" + E + " and dealing " + mag("e_dmg", "e_dap") + " " + M +
                  "magic damage" + E + " to enemies on the way. Its holder gains {e_def} Armor and Magic Resist.",
        "ult": "Waits up to " + A + "{r_arm}s" + E + " for " + A + "2" + E + " enemy champions near the Ball, or one isolated target, "
               "then the Ball sends out a shockwave: " + mag("r_dmg", "r_ap") + " " + M + "magic damage" + E + ", enemies " + R +
               "flung toward the Ball" + E + ".",
        "names": ("Command: Attack", "Command: Protect", "Command: Shockwave"),
    },
    "ko": {
        "name": "오리아나",
        "attack": "태엽 탄환을 쏩니다. " + O + "시계태엽 감기" + E + ": 기본 공격이 " + mag("p_dmg", "p_ap") + "의 " + M + "마법 피해" + E +
                  "를 추가로 입히며, " + A + "{p_t}초" + E + " 안에 연속 공격하면 중첩(최대 " + A + "2" + E + ").",
        "skill": "공을 적 챔피언 발밑에 던져 남겨 두고 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + ". " + O + "명령: 불협화음" + E +
                 ": 공 근처에 적이 있으면 저절로 " + mag("w_dmg", "w_ap") + "의 " + M + "마법 피해" + E + ", 적 " + R + "{w_slow}% 둔화" +
                 E + ", 아군 " + G + "{w_haste}% 가속" + E + ".",
        "skill2": "적에게 가장 가까운 아군에게 공을 보내(적이 붙으면 자신) " + G + "{e_sh}" + E + " + " + APi + G + "{e_ap}% 보호막" + E +
                  ", 지나가는 적에게 " + mag("e_dmg", "e_dap") + "의 " + M + "마법 피해" + E + ". 공을 가진 자는 방어력·마법 저항력 +{e_def}.",
        "ult": "최대 " + A + "{r_arm}초" + E + " 동안 공 근처에 적 챔피언 " + A + "2명" + E + " 또는 고립된 대상이 생기면 충격파: " +
               mag("r_dmg", "r_ap") + "의 " + M + "마법 피해" + E + ", 적을 공 쪽으로 " + R + "날려 보냅니다" + E + ".",
        "names": ("명령: 공격", "명령: 보호", "명령: 충격파"),
    },
    "ja": {
        "name": "オリアナ",
        "attack": "ぜんまい弾を撃つ。" + O + "ぜんまい仕掛け" + E + "：通常攻撃が" + mag("p_dmg", "p_ap") + "の" + M + "魔法ダメージ" + E +
                  "を追加、" + A + "{p_t}秒" + E + "以内の連続攻撃でスタック（最大" + A + "2" + E + "）。",
        "skill": "ボールを敵チャンピオンの足元へ投げて残し、" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "。" + O +
                 "オーダー: 乱磁場" + E + "：ボールの近くに敵がいると自動で放電し" + mag("w_dmg", "w_ap") + "の" + M + "魔法ダメージ" + E +
                 "、敵を" + R + "{w_slow}%スロウ" + E + "、味方は" + G + "{w_haste}%加速" + E + "。",
        "skill2": "敵に最も近い味方へボールを送り（敵に詰められたら自分）、" + G + "{e_sh}" + E + " + " + APi + G + "{e_ap}%のシールド" + E +
                  "、通り道の敵に" + mag("e_dmg", "e_dap") + "の" + M + "魔法ダメージ" + E + "。持ち主は物理・魔法防御+{e_def}。",
        "ult": "最大" + A + "{r_arm}秒" + E + "待機し、ボールの近くに敵チャンピオン" + A + "2体" + E + "か孤立した対象がいれば衝撃波：" +
               mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E + "、敵をボールへ" + R + "引き寄せる" + E + "。",
        "names": ("オーダー: 攻撃", "オーダー: 防御", "オーダー: ショックウェーブ"),
    },
}

C = "league_orianna_sfx_"
V = "league_orianna_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_orianna_a_shot": [(C + "a_shot", 0.4, 0.0)],
    "league_orianna_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_orianna_q": [(C + "q", 0.5, 0.0)],
    "league_orianna_q_land": [(C + "q_land", 0.5, 0.0)],
    "league_orianna_q_hit": [(C + "q_hit", 0.45, 0.0)],
    "league_orianna_w": [(C + "w", 0.55, 0.0)],
    "league_orianna_e": [(C + "e", 0.5, 0.0)],
    "league_orianna_e_shield": [(C + "e_shield", 0.45, 0.0)],
    "league_orianna_r": [(C + "r", 0.65, 0.0)],
    "league_orianna_r_hit": [(C + "r_hit", 0.5, 0.0)],
    "league_orianna_vo_q": [(V + "q", 0.85, 0.0)],
    "league_orianna_vo_w": [(V + "w", 0.85, 0.0)],
    "league_orianna_vo_e": [(V + "e", 0.85, 0.0)],
    "league_orianna_vo_r": [(V + "r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "q_dmg", "q_ap", "w_dmg", "w_ap", "w_slow", "w_haste", "e_sh", "e_ap",
                           "e_dmg", "e_dap", "e_def", "r_dmg", "r_ap")}
    for k in ("p_t", "r_arm"):
        v[k] = secs(p[k])
    return v


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path):
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def texts(p):
    v = values(p)
    out = {}
    for lang, t in TEXT.items():
        d = {"name": t["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = t[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), t["names"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--face", help="X,Y from tfm2_ase.py face")
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top), when the top is above -28")
    a = ap.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    tx = texts(p)
    bad = False
    for lang, (d, _) in tx.items():
        lens = {k: shown_length(TEXT[lang][k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(n > TOOLTIP_MAX[lang] for n in lens.values())
        print(lang, " ".join(f"{k}:{n}/{TOOLTIP_MAX[lang]}" for k, n in lens.items()))
    if a.check:
        sys.stdout.reconfigure(encoding="utf-8")
        for lang, (d, _) in tx.items():
            for k in ("attack", "skill", "skill2", "ult"):
                print(lang, k, re.sub(r"<[^>]*>", "", d[k]))
        return
    if bad:
        sys.exit("a text is longer than TOOLTIP_MAX")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"))
    for lang, (d, names) in tx.items():
        i18n[lang]["description"][ID] = d
        i18n[lang]["skill_name"][ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    for name, plays in SOUNDS.items():
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"))
    for k in [k for k in ov if ID in k]:      # her keys rebuilt (a renamed sound leaves none behind)
        del ov[k]
    for name in list(SOUNDS) + CLIPS:
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/league/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    view = json.loads(json.dumps(VIEW))
    if a.face:
        x, y = (int(v) for v in a.face.split(","))
        view["face"] = {"x": x, "y": y}
    if a.banpick is not None:
        if a.banpick > 0:
            sys.exit("never a positive banpick_center y (card-banpick rule)")
        view["banpick_center"] = {"x": 0, "y": a.banpick}
    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"))
    cv["entries"][ID] = view
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    if "Orianna" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Orianna. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
