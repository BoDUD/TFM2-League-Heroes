"""Graves's text (5 languages), sound_info files and his keys in the shared files, numbers from build_graves.P.

    python tools/kit/setup_graves.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_graves in every language, description + skill_name),
sound/sfx/league_graves_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Graves named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 格雷福斯 (法外狂徒): 新命运, 穷途末路, 烟幕弹, 快速拔枪, 终极爆弹; zh_TW 葛雷夫 (亡命之徒):
命運, 人在江湖, 隻手遮天, 猛龍過江, 龍爭虎鬥; ja グレイブス: ニュー・デスティニー, エンドライン, スモークスクリーン, クイックドロー,
コラテラルダメージ; ko 그레이브즈: 새로운 운명, 화약 역류, 연막탄, 빨리 뽑기, 무고한 희생자.
Slots: skill = Q End of the Line, skill2 = E Quickdraw, ult = R Collateral Damage; the passive New Destiny and W Smoke
Screen in the attack's text. No combo sentence in any text (the user's rule). The add-on league_graves says its own.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_graves import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_graves"
VERSION = "0.176.0"     # provisional: the next free number above main 0.175.0 (2026-10-20); re-check before the PR
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
M = "<#a974ffff>"      # magic damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: provisional until the sheet exists (tfm2_ase.py face, bp_card_audit.py)
VIEW = {"face": {"x": 3, "y": -30}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -8}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def adp(r):
    return f"{ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "格雷福斯",
        "attack": "霰弹枪每次朝前方一扇开火：目标" + adp("a_ratio2") + "，扇形里的其他敌人{a_cone}%攻击；两发后装弹" + A + "{a_reload}秒" + E + "。" +
                  O + "烟幕弹" + E + "：每" + A + "{w_cd}秒" + E + "朝英雄扔一颗，" + M + "{w_dmg}" + E + "魔法伤害、" + R + "减速{w_slow}%、致盲" + E + A + "{w_blind}秒" + E + "。",
        "skill": "射出榴弹，穿过的敌人受到" + phys("q_dmg", "q_ratio") + "物理伤害；榴弹落地" + A + "{q_fuse}秒" + E + "后爆炸，再造成" +
                 phys("q2_dmg", "q2_ratio") + "物理伤害。",
        "skill2": "冲刺一段（身边有敌方英雄时往后翻滚），得到一层" + O + "纯爷们" + E + "（附近有敌方英雄时两层，最多4层）：每层护甲+{e_def}、魔抗+{e_mr}，" +
                  A + "{e_t}秒" + E + "，普攻打中刷新。",
        "ult": "后坐力把自己往后推，射出爆弹，对第一个敌方英雄造成" + phys("r_dmg", "r_ratio") + "物理伤害并爆炸，周围敌人受到" +
               phys("r2_dmg", "r2_ratio") + "物理伤害。",
        "names": ("穷途末路", "快速拔枪", "终极爆弹"),
    },
    "zh-hant": {
        "name": "葛雷夫",
        "attack": "散彈槍每次朝前方一扇開火：目標" + adp("a_ratio2") + "，扇形裡的其他敵人{a_cone}%攻擊；兩發後裝彈" + A + "{a_reload}秒" + E + "。" +
                  O + "隻手遮天" + E + "：每" + A + "{w_cd}秒" + E + "朝英雄丟一顆，" + M + "{w_dmg}" + E + "魔法傷害、" + R + "緩速{w_slow}%、致盲" + E + A + "{w_blind}秒" + E + "。",
        "skill": "射出榴彈，穿過的敵人受到" + phys("q_dmg", "q_ratio") + "物理傷害；榴彈落地" + A + "{q_fuse}秒" + E + "後爆炸，再造成" +
                 phys("q2_dmg", "q2_ratio") + "物理傷害。",
        "skill2": "衝刺一段（身邊有敵方英雄時往後翻滾），獲得一層增益（附近有敵方英雄時兩層，最多4層）：每層護甲+{e_def}、魔抗+{e_mr}，" +
                  A + "{e_t}秒" + E + "，普攻打中刷新。",
        "ult": "後座力把自己往後推，射出爆彈，對第一個敵方英雄造成" + phys("r_dmg", "r_ratio") + "物理傷害並爆炸，周圍敵人受到" +
               phys("r2_dmg", "r2_ratio") + "物理傷害。",
        "names": ("人在江湖", "猛龍過江", "龍爭虎鬥"),
    },
    "en": {
        "name": "Graves",
        "attack": "His shotgun fires a spread: the target takes " + adp("a_ratio2") + ", other enemies in the cone {a_cone}% AD; "
                  "after two shells he reloads for " + A + "{a_reload}s" + E + ". " + O + "Smoke Screen" + E + ": every " + A + "{w_cd}s" + E +
                  " he also throws a canister at a champion: " + M + "{w_dmg}" + E + " magic damage, " + R + "{w_slow}% slow and blind" + E + " for " +
                  A + "{w_blind}s" + E + ".",
        "skill": "Fires a shell dealing " + phys("q_dmg", "q_ratio") + " physical damage to enemies it passes; it lies where it stops and blows "
                 "up after " + A + "{q_fuse}s" + E + " for " + phys("q2_dmg", "q2_ratio") + " physical damage.",
        "skill2": "Dashes (rolls back when an enemy champion is close) and gains a stack of " + O + "True Grit" + E + " (two with an enemy "
                  "champion near, up to 4): +{e_def} armour and +{e_mr} magic resist each for " + A + "{e_t}s" + E + ", refreshed by his attack hits.",
        "ult": "The recoil knocks him back as he fires a shell that deals " + phys("r_dmg", "r_ratio") + " physical damage to the first enemy "
               "champion and explodes, dealing " + phys("r2_dmg", "r2_ratio") + " physical damage around it.",
        "names": ("End of the Line", "Quickdraw", "Collateral Damage"),
    },
    "ko": {
        "name": "그레이브즈",
        "attack": "산탄총이 부채꼴로 발사: 대상 " + adp("a_ratio2") + ", 부채꼴 안 다른 적 공격력 {a_cone}%. 두 발 뒤 " + A + "{a_reload}초" + E +
                  " 재장전. " + O + "연막탄" + E + ": " + A + "{w_cd}초" + E + "마다 챔피언에게 던져 " + M + "{w_dmg}" + E + " 마법 피해, " + R +
                  "{w_slow}% 둔화, " + E + A + "{w_blind}초" + E + " 실명.",
        "skill": "포탄을 쏴 지나간 적에게 " + phys("q_dmg", "q_ratio") + " 물리 피해. 멈춘 자리에서 " + A + "{q_fuse}초" + E + " 뒤 폭발해 " +
                 phys("q2_dmg", "q2_ratio") + " 물리 피해.",
        "skill2": "돌진(가까이 적 챔피언이 있으면 뒤로 구름)하고 1중첩(근처 적 챔피언이 있으면 2, 최대 4): 중첩당 방어력 +{e_def}, "
                  "마법 저항력 +{e_mr}, " + A + "{e_t}초" + E + ". 기본 공격 적중 시 갱신.",
        "ult": "반동으로 뒤로 밀리며 폭발탄 발사. 첫 적 챔피언에게 " + phys("r_dmg", "r_ratio") + " 물리 피해 후 폭발해 주변 적에게 " +
               phys("r2_dmg", "r2_ratio") + " 물리 피해.",
        "names": ("화약 역류", "빨리 뽑기", "무고한 희생자"),
    },
    "ja": {
        "name": "グレイブス",
        "attack": "ショットガンは扇状に撃つ：対象" + adp("a_ratio2") + "、扇内の他の敵は攻撃力{a_cone}%。2発撃つと" + A + "{a_reload}秒" + E +
                  "リロード。" + O + "スモークスクリーン" + E + "：" + A + "{w_cd}秒" + E + "ごとにチャンピオンへ投げ、" + M + "{w_dmg}" + E + "の魔法ダメージ、" +
                  R + "{w_slow}%スロウ、" + E + A + "{w_blind}秒" + E + "ブラインド。",
        "skill": "砲弾を撃ち、通過した敵に" + phys("q_dmg", "q_ratio") + "の物理ダメージ。止まった地点で" + A + "{q_fuse}秒" + E + "後に爆発し" +
                 phys("q2_dmg", "q2_ratio") + "の物理ダメージ。",
        "skill2": "ダッシュ（近くに敵チャンピオンがいれば後ろへ転がる）し、スタックを1つ（敵チャンピオンが近くにいれば2、最大4）："
                  "スタックごとに物理防御+{e_def}、魔法防御+{e_mr}、" + A + "{e_t}秒" + E + "。通常攻撃で更新。",
        "ult": "反動で後ろへ下がりつつ爆裂弾を撃ち、最初の敵チャンピオンに" + phys("r_dmg", "r_ratio") + "の物理ダメージ、爆発で周囲の敵に" +
               phys("r2_dmg", "r2_ratio") + "の物理ダメージ。",
        "names": ("エンドライン", "クイックドロー", "コラテラルダメージ"),
    },
}

C = "league_graves_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_graves_a_shot": [(C + "a", 0.4, 0.0), (C + "a_pump", 0.3, 0.25)],
    "league_graves_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_graves_a_reload": [(C + "a_open", 0.35, 0.0), (C + "a_close", 0.35, 0.55)],
    "league_graves_w_cast": [(C + "w", 0.4, 0.0)],
    "league_graves_w_boom": [(C + "w_bang", 0.45, 0.0)],
    "league_graves_w_hit": [(C + "a_hit", 0.2, 0.0)],
    "league_graves_q_cast": [(C + "q", 0.4, 0.0)],
    "league_graves_q_hit": [(C + "q_hit", 0.35, 0.0)],
    "league_graves_q_fuse": [(C + "q_hit", 0.2, 0.0)],
    "league_graves_q_boom": [(C + "q_bang", 0.5, 0.0)],
    "league_graves_q_hit2": [(C + "a_hit", 0.25, 0.0)],
    "league_graves_e_cast": [(C + "e", 0.45, 0.0)],
    "league_graves_r_cast": [(C + "r", 0.45, 0.0)],
    "league_graves_r_fire": [(C + "r_fire", 0.6, 0.0)],
    "league_graves_r_hit": [(C + "r_hit", 0.5, 0.0)],
    "league_graves_r_boom": [(C + "q_bang", 0.4, 0.0)],
    "league_graves_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_graves_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_graves_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("a_cone", "w_dmg", "w_slow", "q_dmg", "q_ratio", "q2_dmg", "q2_ratio", "e_def", "e_mr",
                           "r_dmg", "r_ratio", "r2_dmg", "r2_ratio")}
    v["a_ratio2"] = p["a_ratio"] + p["a_cone"]
    for k in ("a_reload", "w_cd", "w_blind", "q_fuse", "e_t"):
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
    if "Graves" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Graves. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
