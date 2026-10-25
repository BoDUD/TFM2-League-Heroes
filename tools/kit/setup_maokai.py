"""Maokai's text (5 languages), sound_info files and his keys in the shared files, numbers from build_maokai.P.

    python tools/kit/setup_maokai.py [--params final.json] [--check]

Writes (in league/): text/champion.i18n (league_maokai in every language, description + skill_name),
sound/sfx/league_maokai_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Maokai named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 茂凯 (扭曲树精): 吸元秘术, 荆棘重击, 扭曲突刺, 树苗投掷, 自然之握; zh_TW 茂凱: 魔法樹液,
荊棘摧殘, 飛葉遁影, 扭曲樹精, 詭林之握; ja マオカイ: 魔樹液, 茨打ち, 樹人の進撃, 苗木投げ, 大地の捕縛; ko 마오카이: 마법 흡수,
덤불 주먹, 뒤틀린 전진, 묘목 던지기, 대자연의 마수.
Slots: skill = Q Bramble Smash, skill2 = W Twisted Advance, ult = R Nature's Grasp; the passive and the automatic E in
the attack's text. No combo sentence in any text (the user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_maokai import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_maokai"
VERSION = "0.141.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7dd87dff>"      # heals
E = "<>"
# champion_view: the face between the eyes of the face in his trunk (ppu_restyle face_to); the card's top at the moss
# crown (29.3 px over the frame centre on lo_idle at PPU 1.3, tools/art/bp_card_audit.py: banpick_center y = -39 + 29;
# -9 at 1.5)
# 2026-10-25: face (8,-28) - (8,-23) missed his eyes: mossy chin and hands only; kept equal to champion_view and ppu_restyle.py
VIEW = {"face": {"x": 8, "y": -28}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "茂凯",
        "attack": "巨臂砸击。" + O + "吸元秘术" + E + "：技能命中后下一次普攻额外造成" + M + "{p_hp}%最大生命" + E + "魔法伤害，" + G + "回复" + E +
                  mag("p_heal", "p_ap") + "生命（" + A + "{p_cd}秒" + E + "一次）。" + O + "树苗投掷" + E + "：每" + A + "{e_cd}秒" + E +
                  "自动向敌方英雄扔树苗，敌人靠近就爆炸：" + mag("e_dmg", "e_ap") + "魔法伤害，" + R + "减速{e_slow}%" + E + "。",
        "skill": "巨拳砸地，推开身边的敌人，冲击波对前方敌人造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "外加目标" + M + "{q_thp}%最大生命" + E +
                 "伤害，并" + R + "减速{q_slow}%" + E + "（很快减弱）。",
        "skill2": "化作树根冲向敌方英雄（途中免伤免控），到达后" + R + "禁锢{w_root}秒" + E + "，造成" + mag("w_dmg", "w_ap") + M + "魔法伤害" + E +
                  "。身边有友方英雄或正在交战时才放。",
        "ult": "召唤荆棘墙缓缓向前推进，碰到的敌人受到" + mag("r_dmg", "r_ap") + M + "魔法伤害" + E + "并被" + R + "禁锢{r_b1}~{r_b3}秒" + E +
               "（推得越远越久），撞到英雄后他加速。有2名敌方英雄或交战时才放。",
        "names": ("荆棘重击", "扭曲突刺", "自然之握"),
    },
    "zh-hant": {
        "name": "茂凱",
        "attack": "巨臂砸擊。" + O + "魔法樹液" + E + "：技能命中後下一次普攻額外造成" + M + "{p_hp}%最大生命" + E + "魔法傷害，" + G + "回復" + E +
                  mag("p_heal", "p_ap") + "生命（" + A + "{p_cd}秒" + E + "一次）。" + O + "扭曲樹精" + E + "：每" + A + "{e_cd}秒" + E +
                  "自動向敵方英雄扔樹苗，敵人靠近就爆炸：" + mag("e_dmg", "e_ap") + "魔法傷害，" + R + "緩速{e_slow}%" + E + "。",
        "skill": "巨拳砸地，推開身邊的敵人，衝擊波對前方敵人造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "外加目標" + M + "{q_thp}%最大生命" + E +
                 "傷害，並" + R + "緩速{q_slow}%" + E + "（很快減弱）。",
        "skill2": "化作樹根衝向敵方英雄（途中免傷免控），抵達後" + R + "禁錮{w_root}秒" + E + "，造成" + mag("w_dmg", "w_ap") + M + "魔法傷害" + E +
                  "。身邊有友方英雄或正在交戰時才施放。",
        "ult": "召喚荊棘牆緩緩向前推進，碰到的敵人受到" + mag("r_dmg", "r_ap") + M + "魔法傷害" + E + "並被" + R + "禁錮{r_b1}~{r_b3}秒" + E +
               "（推得越遠越久），撞到英雄後他加速。有2名敵方英雄或交戰時才施放。",
        "names": ("荊棘摧殘", "飛葉遁影", "詭林之握"),
    },
    "en": {
        "name": "Maokai",
        "attack": "A blow of the huge arm. " + O + "Sap Magic" + E + ": after his skills hit, his next attack deals " + M + "{p_hp}% of his max health" + E +
                  " more as magic damage and " + G + "heals him" + E + " " + mag("p_heal", "p_ap") + " (once every " + A + "{p_cd}s" + E + "). " + O +
                  "Sapling Toss" + E + ": every " + A + "{e_cd}s" + E + " he throws a sapling at an enemy champion; it bursts when an enemy comes near for " +
                  mag("e_dmg", "e_ap") + " " + M + "magic damage" + E + " and a " + R + "{e_slow}% slow" + E + ".",
        "skill": "Slams the ground: enemies next to him are knocked back and a shockwave deals " + mag("q_dmg", "q_ap") + " " + M + "magic damage" + E +
                 " plus " + M + "{q_thp}% of the target's max health" + E + " and a " + R + "{q_slow}% slow" + E + " that wears off fast.",
        "skill2": "Dashes to an enemy champion as a mass of roots (no damage or crowd control on the way), then " + R + "roots it {w_root}s" + E +
                  " for " + mag("w_dmg", "w_ap") + " " + M + "magic damage" + E + ". Cast only with an ally near him or in a fight.",
        "ult": "A wall of brambles slowly advances: enemies it meets take " + mag("r_dmg", "r_ap") + " " + M + "magic damage" + E + " and are " + R +
               "rooted {r_b1}-{r_b3}s" + E + " (longer the farther it went); a champion hit hastes him. Cast with 2 enemy champions near him or in a fight.",
        "names": ("Bramble Smash", "Twisted Advance", "Nature's Grasp"),
    },
    "ko": {
        "name": "마오카이",
        "attack": "거대한 팔로 내리치기. " + O + "마법 흡수" + E + ": 스킬 적중 후 다음 공격이 " + M + "최대 체력의 {p_hp}%" + E + " 마법 피해를 더하고 " + G + "체력" + E +
                  " " + mag("p_heal", "p_ap") + " 회복(" + A + "{p_cd}초" + E + "에 한 번). " + O + "묘목 던지기" + E + ": " + A + "{e_cd}초" + E +
                  "마다 적 챔피언에게 묘목을 던지고, 적이 다가오면 폭발해 " + mag("e_dmg", "e_ap") + "의 " + M + "마법 피해" + E + "와 " + R + "{e_slow}% 둔화" + E + ".",
        "skill": "땅을 내리쳐 가까운 적을 밀쳐내고, 충격파가 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E + "와 " + M + "대상 최대 체력의 {q_thp}%" + E +
                 " 피해, 빠르게 약해지는 " + R + "{q_slow}% 둔화" + E + ".",
        "skill2": "뿌리가 되어 적 챔피언에게 돌진(도중 피해·군중 제어 면역), 도착하면 " + R + "{w_root}초 속박" + E + "과 " + mag("w_dmg", "w_ap") + "의 " + M +
                  "마법 피해" + E + ". 주변에 아군이 있거나 교전 중일 때만 사용.",
        "ult": "가시덤불 벽이 천천히 전진해 닿은 적에게 " + mag("r_dmg", "r_ap") + "의 " + M + "마법 피해" + E + "와 " + R + "{r_b1}~{r_b3}초 속박" + E +
               "(멀리 갈수록 길게), 챔피언 적중 시 이동 속도 증가. 적 챔피언 2명이 가깝거나 교전 중일 때 사용.",
        "names": ("덤불 주먹", "뒤틀린 전진", "대자연의 마수"),
    },
    "ja": {
        "name": "マオカイ",
        "attack": "巨腕の一撃。" + O + "魔樹液" + E + "：スキル命中後の次の攻撃が" + M + "最大体力の{p_hp}%" + E + "の魔法ダメージを追加し" + G + "体力" + E +
                  mag("p_heal", "p_ap") + "回復（" + A + "{p_cd}秒" + E + "に1度）。" + O + "苗木投げ" + E + "：" + A + "{e_cd}秒" + E +
                  "ごとに敵チャンピオンへ苗木を投げ、敵が近づくと爆発：" + mag("e_dmg", "e_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "スロウ{e_slow}%" + E + "。",
        "skill": "地面を叩き近くの敵をノックバック、衝撃波が" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + M + "最大体力の{q_thp}%" + E +
                 "のダメージ、すぐ弱まる" + R + "スロウ{q_slow}%" + E + "。",
        "skill2": "根の塊となって敵チャンピオンへ突進（途中はダメージと行動妨害無効）、到着時に" + R + "{w_root}秒スネア" + E + "と" + mag("w_dmg", "w_ap") + "の" + M +
                  "魔法ダメージ" + E + "。味方が近いか交戦中のみ使う。",
        "ult": "茨の壁がゆっくり前進し、触れた敵に" + mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "{r_b1}~{r_b3}秒スネア" + E +
               "（遠いほど長い）、チャンピオン命中で移動速度上昇。敵2体が近いか交戦中に使う。",
        "names": ("茨打ち", "樹人の進撃", "大地の捕縛"),
    },
}

C = "league_maokai_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_maokai_a_swing": [(C + "a_swing", 0.3, 0.0)],
    "league_maokai_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_maokai_p_hit": [(C + "p_hit", 0.45, 0.0)],
    "league_maokai_p_heal": [(C + "p_heal", 0.45, 0.0)],
    "league_maokai_q": [(C + "q", 0.45, 0.0)],
    "league_maokai_q_land": [(C + "q_land", 0.55, 0.0)],
    "league_maokai_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_maokai_w": [(C + "w", 0.5, 0.0)],
    "league_maokai_w_land": [(C + "w_land", 0.55, 0.0)],
    "league_maokai_w_hit": [(C + "w_hit", 0.4, 0.0)],
    "league_maokai_e": [(C + "e", 0.45, 0.0)],
    "league_maokai_e_land": [(C + "e_land", 0.45, 0.0)],
    "league_maokai_e_burst": [(C + "e_burst", 0.5, 0.0)],
    "league_maokai_e_hit": [(C + "e_hit", 0.35, 0.0)],
    "league_maokai_r": [(C + "r", 0.5, 0.0)],
    "league_maokai_r_wall": [(C + "r_wall", 0.6, 0.0)],
    "league_maokai_r_hit": [(C + "r_hit", 0.4, 0.0)],
    "league_maokai_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_maokai_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_maokai_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_maokai_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_hp", "p_heal", "p_ap", "q_dmg", "q_ap", "q_thp", "w_dmg", "w_ap", "e_dmg", "e_ap", "e_slow",
                           "r_dmg", "r_ap")}
    v["q_slow"] = p["q_s1"] + p["q_s2"]
    for k in ("p_cd", "w_root", "e_cd", "r_b1", "r_b3"):
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

    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"))
    cv["entries"][ID] = json.loads(json.dumps(VIEW))
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    if "Maokai" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Maokai. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
