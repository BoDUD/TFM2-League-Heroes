"""Sejuani's text (5 languages), sound_info files and their keys in the shared files, numbers from build_sejuani.P
(setup_aurelionsol.py's way).

    python tools/kit/setup_sejuani.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_sejuani in every language, description + skill_name),
sound/sfx/league_sejuani_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Sejuani named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 瑟庄妮 (北地之怒): 北地之怒; 极寒突袭, 凛冬之怒, 永冻领域, 极冰寒狱; zh_TW 史瓦妮: 北境之怒;
極地衝刺, 凜冬狂怒, 永恆凍土, 冰河籠牢; ja セジュアニ: 極北の激憤; 猪突凍進, 氷河の怒り, 永久凍土, グレイシャルプリズン; ko 세주아니:
혹한의 분노; 혹한의 맹습, 혹한의 서릿발, 만년 서리, 빙하 감옥.
Slots: skill = Arctic Assault, skill2 = Winter's Wrath, ult = Glacial Prison; Fury of the North (the Frost Armour, the
shatter) and Permafrost (four Frost stacks freeze) in the attack's text. The texts say the main pack's rules (the add-on's
copy has its own: addons/league_sejuani/make_override.py). No combo sentence in any text (the user's rule: the combos
are the README's).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sejuani import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_sejuani"
VERSION = "0.211.0"     # above main 0.209.0 (Aurelion Sol #505) and Ahri PPU 2.2's 0.210.0 (#504, open), 2026-10-24
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 3, "y": -28}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


TEXT = {
    "zh-hans": {
        "name": "瑟庄妮",
        "attack": "链枷抽打。" + n("北地之怒") + "：脱战后冰霜护甲，护甲、魔抗+{fa_def}%。普攻和凛冬之怒叠霜冻，满{f_n}层" +
                  cc("冻住") + t("{e_stun}秒") + "并造成" + mag("e_dmg", "e_ap") + "；打中被她晕住的敌人再造成其最大生命{sh_pct}%。",
        "skill": "钢鬃冲向目标，路上的敌人受到" + mag("q_dmg", "q_ap") + "魔法伤害并被" + cc("击飞") + t("{q_up}秒") + "。",
        "skill2": "链枷先横扫一圈造成" + mag("w1_dmg", "w1_ap") + "，再往前砸出一道冰造成" + mag("w2_dmg", "w2_ap") +
                  "魔法伤害，都" + cc("减速") + "{w_slow}%" + t("{w_slow_t}秒") + "。",
        "ult": "甩出冰套索，第一个敌方英雄受到" + mag("r_dmg", "r_ap") + "魔法伤害并被" + cc("眩晕") + t("{r_stun}秒") +
               "；落点冰风暴" + cc("减速") + "周围敌人{r_slow}%，持续" + t("{r_storm}秒") + "。",
        "names": ("极寒突袭", "凛冬之怒", "极冰寒狱"),
    },
    "zh-hant": {
        "name": "史瓦妮",
        "attack": "鏈枷抽打。" + n("北境之怒") + "：脫戰後冰霜護甲，護甲、魔防+{fa_def}%。普攻和凜冬狂怒疊霜凍，滿{f_n}層" +
                  cc("冰凍") + t("{e_stun}秒") + "並造成" + mag("e_dmg", "e_ap") + "；打中被她暈眩的敵人再造成其最大生命{sh_pct}%。",
        "skill": "坐騎衝向目標，路上的敵人受到" + mag("q_dmg", "q_ap") + "魔法傷害並被" + cc("擊飛") + t("{q_up}秒") + "。",
        "skill2": "鏈枷先橫掃一圈造成" + mag("w1_dmg", "w1_ap") + "，再往前砸出一道冰造成" + mag("w2_dmg", "w2_ap") +
                  "魔法傷害，都" + cc("緩速") + "{w_slow}%" + t("{w_slow_t}秒") + "。",
        "ult": "甩出冰套索，第一個敵方英雄受到" + mag("r_dmg", "r_ap") + "魔法傷害並被" + cc("暈眩") + t("{r_stun}秒") +
               "；落點冰風暴" + cc("緩速") + "周圍敵人{r_slow}%，持續" + t("{r_storm}秒") + "。",
        "names": ("極地衝刺", "凜冬狂怒", "冰河籠牢"),
    },
    "en": {
        "name": "Sejuani",
        "attack": "Flail blows. " + n("Fury of the North") + ": out of combat her Frost Armour gives +{fa_def}% armour and "
                  "magic resist. Her attacks and Winter's Wrath add Frost; {f_n} " + cc("freeze") + " the target for " +
                  t("{e_stun}s") + " and deal " + mag("e_dmg", "e_ap") + "; hitting an enemy she stunned deals {sh_pct}% "
                  "of its maximum health more.",
        "skill": "Bristle charges at the target: the enemies in the way take " + mag("q_dmg", "q_ap") + " magic damage and "
                 "are " + cc("knocked up") + " for " + t("{q_up}s") + ".",
        "skill2": "Her flail sweeps round her for " + mag("w1_dmg", "w1_ap") + ", then slams a line of ice ahead for " +
                  mag("w2_dmg", "w2_ap") + " magic damage, each " + cc("slowing") + " {w_slow}% for " + t("{w_slow_t}s") + ".",
        "ult": "Throws her ice bola: the first enemy champion takes " + mag("r_dmg", "r_ap") + " magic damage and is " +
               cc("stunned") + " for " + t("{r_stun}s") + "; an ice storm there " + cc("slows") + " the enemies round it "
               "{r_slow}% for " + t("{r_storm}s") + ".",
        "names": ("Arctic Assault", "Winter's Wrath", "Glacial Prison"),
    },
    "ko": {
        "name": "세주아니",
        "attack": "철퇴 공격. " + n("혹한의 분노") + ": 비전투 시 서리 갑옷, 방어력·마법 저항력 +{fa_def}%. 기본 공격과 혹한의 "
                  "서릿발이 서리 중첩, {f_n}중첩 시 " + t("{e_stun}초") + " " + cc("빙결") + ", " + mag("e_dmg", "e_ap") +
                  "; 그녀가 기절시킨 적을 치면 최대 체력의 {sh_pct}% 추가.",
        "skill": "브리슬이 대상에게 돌진: 경로의 적에게 " + mag("q_dmg", "q_ap") + " 마법 피해와 " + t("{q_up}초") + " " +
                 cc("에어본") + ".",
        "skill2": "철퇴로 주변을 휩쓸어 " + mag("w1_dmg", "w1_ap") + ", 이어서 앞으로 얼음을 내리쳐 " + mag("w2_dmg", "w2_ap") +
                  " 마법 피해, 각각 " + t("{w_slow_t}초") + " 동안 {w_slow}% " + cc("둔화") + ".",
        "ult": "얼음 볼라를 던져 첫 적 챔피언에게 " + mag("r_dmg", "r_ap") + " 마법 피해와 " + t("{r_stun}초") + " " +
               cc("기절") + "; 그 자리의 얼음 폭풍이 " + t("{r_storm}초") + " 동안 주변 적 {r_slow}% " + cc("둔화") + ".",
        "names": ("혹한의 맹습", "혹한의 서릿발", "빙하 감옥"),
    },
    "ja": {
        "name": "セジュアニ",
        "attack": "フレイルで打つ。" + n("極北の激憤") + "：非戦闘時フロストアーマー、物理・魔法防御+{fa_def}%。通常攻撃と"
                  "氷河の怒りでフロスト付与、{f_n}つで" + t("{e_stun}秒") + cc("凍結") + "し" + mag("e_dmg", "e_ap") +
                  "；彼女がスタンさせた敵を打つと最大体力{sh_pct}%追加。",
        "skill": "ブリッスルが対象へ突進：進路の敵に" + mag("q_dmg", "q_ap") + "の魔法ダメージと" + t("{q_up}秒") +
                 cc("ノックアップ") + "。",
        "skill2": "フレイルで周囲を薙ぎ" + mag("w1_dmg", "w1_ap") + "、続けて前方へ氷を叩きつけ" + mag("w2_dmg", "w2_ap") +
                  "の魔法ダメージ、それぞれ" + t("{w_slow_t}秒") + "{w_slow}%" + cc("スロウ") + "。",
        "ult": "氷のボーラを投げ、最初の敵チャンピオンに" + mag("r_dmg", "r_ap") + "の魔法ダメージと" + t("{r_stun}秒") +
               cc("スタン") + "；その場の氷嵐が" + t("{r_storm}秒") + "周囲の敵を{r_slow}%" + cc("スロウ") + "。",
        "names": ("猪突凍進", "氷河の怒り", "グレイシャルプリズン"),
    },
}

C = "league_sejuani_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the impacts loud, the voice as the other heroes'
SOUNDS = {f"league_sejuani_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.5), ("q", 0.7), ("q_hit", 0.65), ("w", 0.6), ("w_sweep", 0.5), ("w_slam", 0.75),
    ("w_hit", 0.5), ("e_freeze", 0.75), ("sh_hit", 0.8), ("r", 0.8), ("r_throw", 0.7), ("r_hit", 0.85), ("r_storm", 0.75),
    ("vo_q", 0.85), ("vo_w", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("fa_def", "f_n", "e_dmg", "e_ap", "sh_pct", "q_dmg", "q_ap", "w1_dmg", "w1_ap", "w2_dmg",
                           "w2_ap", "w_slow", "r_dmg", "r_ap", "r_slow")}
    for k in ("e_stun", "q_up", "w_slow_t", "r_stun", "r_storm"):
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
    for lang, tx in TEXT.items():
        d = {"name": tx["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = tx[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), tx["names"])))
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
        bad |= any(m > TOOLTIP_MAX[lang] for m in lens.values())
        print(lang, " ".join(f"{k}:{m}/{TOOLTIP_MAX[lang]}" for k, m in lens.items()))
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
    for k in [k for k in ov if ID + "_" in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Sejuani" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Sejuani. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
