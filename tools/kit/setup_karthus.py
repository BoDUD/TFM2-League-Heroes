"""Karthus's text (5 languages), sound_info files and his keys in the shared files, numbers from build_karthus.P.

    python tools/kit/setup_karthus.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_karthus in every language, description + skill_name),
sound/sfx/league_karthus_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Karthus named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 卡尔萨斯 (死亡颂唱者): 死亡契约, 荒芜, 痛苦之墙, 亵渎, 安魂曲; zh_TW 卡爾瑟斯 (死亡頌唱者):
無視死亡！, 荒蕪, 痛苦之牆, 汙染, 安魂曲; ja カーサス: 怨嗟の叫び, 根絶やし, 嘆きの壁, 冒涜, 鎮魂歌; ko 카서스: 죽음 극복, 황폐화, 고통의 벽,
부패, 진혼곡.
Slots: skill = Q Lay Waste, skill2 = E Defile, ult = R Requiem; W Wall of Pain is in the attack's text. No combo sentence
in any text (the user's rule). Death Defied is the add-on's (league_karthus), which says so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_karthus import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_karthus"
VERSION = "0.175.0"     # the next free number above main 0.174.0 (2026-10-20)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point on his skull (the 9x9 face crop shows the eyes, the teeth and the crown's gem; the
# crown tip 40 px over his soles, the staff's crystal 44); banpick_center by base's rule on the crown (-39 + 28.5), the
# staff's thin tip clipped (tools/art/bp_card_audit.py)
VIEW = {"face": {"x": 1, "y": -30}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "卡尔萨斯",
        "attack": O + "痛苦之墙" + E + "：每" + A + "{w_cd}秒" + E + "，身边有敌方英雄时，攻击在那名英雄脚下立起一道墙（" + A + "{w_t}秒" + E +
                  "），墙里的敌人" + R + "减速{w_slow}%" + E + "，魔抗-{w_mr}%（" + A + "{w_mr_t}秒" + E + "）。",
        "skill": "目标处" + A + "{q_delay}秒" + E + "后爆炸，造成" + mag("q_dmg", "q_ratio") + "魔法伤害；只炸到一个敌人时伤害翻倍。",
        "skill2": A + "{e_t}秒" + E + "内灵魂环绕自身，每" + A + "{e_per}秒" + E + "对身边敌人造成" + mag("e_dmg", "e_ratio") + "魔法伤害。",
        "ult": "引导" + A + "{r_ch}秒" + E + "（被控制会打断），然后对全图所有敌方英雄造成" + mag("r_dmg", "r_ratio") + "魔法伤害。",
        "names": ("荒芜", "亵渎", "安魂曲"),
    },
    "zh-hant": {
        "name": "卡爾瑟斯",
        "attack": O + "痛苦之牆" + E + "：每" + A + "{w_cd}秒" + E + "，身邊有敵方英雄時，攻擊在那名英雄腳下立起一道牆（" + A + "{w_t}秒" + E +
                  "），牆裡的敵人" + R + "緩速{w_slow}%" + E + "，魔抗-{w_mr}%（" + A + "{w_mr_t}秒" + E + "）。",
        "skill": "目標處" + A + "{q_delay}秒" + E + "後爆炸，造成" + mag("q_dmg", "q_ratio") + "魔法傷害；只炸到一個敵人時傷害翻倍。",
        "skill2": A + "{e_t}秒" + E + "內靈魂環繞自身，每" + A + "{e_per}秒" + E + "對身邊敵人造成" + mag("e_dmg", "e_ratio") + "魔法傷害。",
        "ult": "引導" + A + "{r_ch}秒" + E + "（被控制會打斷），然後對全圖所有敵方英雄造成" + mag("r_dmg", "r_ratio") + "魔法傷害。",
        "names": ("荒蕪", "汙染", "安魂曲"),
    },
    "en": {
        "name": "Karthus",
        "attack": O + "Wall of Pain" + E + ": every " + A + "{w_cd}s" + E + ", with an enemy champion near, his attack raises a wall "
                  "at that champion for " + A + "{w_t}s" + E + ": enemies in it are " + R + "slowed {w_slow}%" + E + " and lose "
                  "{w_mr}% magic resist for " + A + "{w_mr_t}s" + E + ".",
        "skill": "After " + A + "{q_delay}s" + E + " the target spot blasts for " + mag("q_dmg", "q_ratio") + " magic damage, "
                 "doubled when it hits a single enemy.",
        "skill2": "For " + A + "{e_t}s" + E + " souls whirl round him, dealing " + mag("e_dmg", "e_ratio") + " magic damage to "
                  "nearby enemies every " + A + "{e_per}s" + E + ".",
        "ult": "Channels " + A + "{r_ch}s" + E + " (crowd control breaks it), then deals " + mag("r_dmg", "r_ratio") +
               " magic damage to every enemy champion on the map.",
        "names": ("Lay Waste", "Defile", "Requiem"),
    },
    "ko": {
        "name": "카서스",
        "attack": O + "고통의 벽" + E + ": " + A + "{w_cd}초" + E + "마다 근처에 적 챔피언이 있으면 공격이 그 챔피언 위치에 " + A + "{w_t}초" + E +
                  " 동안 벽을 세움. 벽 안의 적은 " + R + "{w_slow}% 둔화" + E + ", 마법 저항력 -{w_mr}% (" + A + "{w_mr_t}초" + E + ").",
        "skill": A + "{q_delay}초" + E + " 뒤 대상 위치가 폭발해 " + mag("q_dmg", "q_ratio") + " 마법 피해. 적 하나만 맞으면 피해 2배.",
        "skill2": A + "{e_t}초" + E + " 동안 영혼이 주위를 돌며 " + A + "{e_per}초" + E + "마다 근처 적에게 " + mag("e_dmg", "e_ratio") + " 마법 피해.",
        "ult": A + "{r_ch}초" + E + " 정신 집중(군중 제어에 끊김) 후 맵의 모든 적 챔피언에게 " + mag("r_dmg", "r_ratio") + " 마법 피해.",
        "names": ("황폐화", "부패", "진혼곡"),
    },
    "ja": {
        "name": "カーサス",
        "attack": O + "嘆きの壁" + E + "：" + A + "{w_cd}秒" + E + "ごとに、近くに敵チャンピオンがいると通常攻撃でその位置に壁を" + A + "{w_t}秒" + E +
                  "立てる。壁の中の敵は" + R + "{w_slow}%スロウ" + E + "、魔法防御-{w_mr}%（" + A + "{w_mr_t}秒" + E + "）。",
        "skill": A + "{q_delay}秒" + E + "後に対象地点が爆発し" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。敵1体だけに当たると2倍。",
        "skill2": A + "{e_t}秒" + E + "間、魂が周囲を巡り" + A + "{e_per}秒" + E + "ごとに近くの敵へ" + mag("e_dmg", "e_ratio") + "の魔法ダメージ。",
        "ult": A + "{r_ch}秒" + E + "詠唱（行動妨害で中断）した後、マップ上のすべての敵チャンピオンに" + mag("r_dmg", "r_ratio") + "の魔法ダメージ。",
        "names": ("根絶やし", "冒涜", "鎮魂歌"),
    },
}

C = "league_karthus_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_karthus_a": [(C + "a", 0.35, 0.0)],
    "league_karthus_a_hit": [(C + "a_hit", 0.35, 0.0)],
    "league_karthus_w_cast": [(C + "w_cast", 0.4, 0.0)],
    "league_karthus_w": [(C + "w", 0.45, 0.0)],
    "league_karthus_q": [(C + "q", 0.35, 0.0)],
    "league_karthus_q_mark": [(C + "q_mark", 0.35, 0.0)],
    "league_karthus_q_boom": [(C + "q_boom", 0.4, 0.0)],
    "league_karthus_q_hit": [(C + "q_boom", 0.25, 0.0)],
    "league_karthus_q_lone": [(C + "q_lone", 0.45, 0.0)],
    "league_karthus_e": [(C + "e", 0.4, 0.0)],
    "league_karthus_e_loop": [(C + "e_loop", 0.3, 0.0)],
    "league_karthus_r": [(C + "r", 0.55, 0.0)],
    "league_karthus_r_boom": [(C + "r_boom", 0.6, 0.0)],
    "league_karthus_r_hit": [(C + "r_hit", 0.45, 0.0)],
    "league_karthus_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_karthus_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_karthus_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_karthus_vo_r": [(C + "vo_r", 0.9, 0.0)],
    # the add-on's Death Defied (addons/league_karthus): shipped with the main pack like every sound of his
    "league_karthus_p": [(C + "p", 0.5, 0.0)],
    "league_karthus_vo_p": [(C + "vo_p", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("w_slow", "w_mr", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "r_dmg", "r_ratio")}
    for k in ("w_cd", "w_t", "w_mr_t", "q_delay", "e_t", "e_per", "r_ch"):
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
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 + the idle's top over the frame centre)")
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
    for k in [k for k in ov if ID + "_" in k]:      # his keys rebuilt (a renamed sound leaves none behind)
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
    if "Karthus" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Karthus. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
