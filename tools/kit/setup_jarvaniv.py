"""Jarvan IV's text (5 languages), sound_info files and his keys in the shared files, numbers from build_jarvaniv.P.

    python tools/kit/setup_jarvaniv.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_jarvaniv in every language, description + skill_name),
sound/sfx/league_jarvaniv_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Jarvan IV named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 嘉文四世 (德玛西亚皇子): 战争律动, 巨龙撞击, 黄金圣盾, 德邦军旗, 天崩地裂; zh_TW 嘉文四世:
戰爭律動, 滅龍一擊, 光盾庇護, 帝國戰旗, 浩劫降臨; ja ジャーヴァンⅣ: 武魂の律動, ドラゴンストライク, ゴールデンイージス, デマーシアの旗印,
決戦場; ko 자르반 4세: 전장의 군가, 용의 일격, 황금빛 방패, 데마시아의 깃발, 대격변.
Slots: skill = E Demacian Standard and the Dragon Strike to it, skill2 = Q Dragon Strike alone, ult = R Cataclysm; the
passive, E's attack speed and the automatic W in the attack's text. No combo sentence in any text (the user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_jarvaniv import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_jarvaniv"
VERSION = "0.139.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face between his eyes under the helmet's brim (ppu_restyle face_to); the card's top at the
# helmet's crown (28.5 px over the pivot: banpick_center y = -39 + 28.5), the lance's tip above it clipped
VIEW = {"face": {"x": 1, "y": -32}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -10}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "嘉文四世",
        "attack": "骑枪刺击，攻速+{e_as}%。" + O + "战争律动" + E + "：对每名英雄每" + A + "{p_rest}秒" + E + "的第一下额外造成其" + O + "{p_pct}%最大生命" +
                  E + "伤害。" + O + "黄金圣盾" + E + "：交战时自动获得" + phy("w_sh", "w_ratio") + "护盾" + A + "{w_t}秒" + E + "（身边每名敌方英雄+{w_per}），" +
                  "身边敌人" + R + "减速{w_slow}%" + E + "。",
        "skill": "掷出军旗：造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "，军旗立" + A + "{fl_t}秒" + E + "，附近友方英雄攻速+{f_as}%。随后冲向军旗：" +
                 "沿途和落点的敌人" + R + "击飞{q_up}秒" + E + "，受到" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "，护甲-{q_shred}%。",
        "skill2": "骑枪向前刺出：直线上的敌人受到" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "，护甲" + R + "-{q_shred}%" + E + "，持续" + A +
                  "{q_shred_t}秒" + E + "。",
        "ult": "跃向敌方英雄砸下：周围敌人受到" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "，升起岩墙环将敌方英雄" + R + "困住{r_t}秒" + E +
               "，想跑出去会被拉回。有被击飞的敌人或2名敌方英雄在身边时才放。",
        "names": ("德邦军旗", "巨龙撞击", "天崩地裂"),
    },
    "zh-hant": {
        "name": "嘉文四世",
        "attack": "騎槍刺擊，攻速+{e_as}%。" + O + "戰爭律動" + E + "：對每名英雄每" + A + "{p_rest}秒" + E + "的第一下額外造成其" + O + "{p_pct}%最大生命" +
                  E + "傷害。" + O + "光盾庇護" + E + "：交戰時自動獲得" + phy("w_sh", "w_ratio") + "護盾" + A + "{w_t}秒" + E + "（身邊每名敵方英雄+{w_per}），" +
                  "身邊敵人" + R + "緩速{w_slow}%" + E + "。",
        "skill": "擲出軍旗：造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "，軍旗立" + A + "{fl_t}秒" + E + "，附近友方英雄攻速+{f_as}%。隨後衝向軍旗：" +
                 "沿途和落點的敵人" + R + "擊飛{q_up}秒" + E + "，受到" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "，護甲-{q_shred}%。",
        "skill2": "騎槍向前刺出：直線上的敵人受到" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "，護甲" + R + "-{q_shred}%" + E + "，持續" + A +
                  "{q_shred_t}秒" + E + "。",
        "ult": "躍向敵方英雄砸下：周圍敵人受到" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "，升起岩牆環將敵方英雄" + R + "困住{r_t}秒" + E +
               "，想跑出去會被拉回。有被擊飛的敵人或2名敵方英雄在身邊時才施放。",
        "names": ("帝國戰旗", "滅龍一擊", "浩劫降臨"),
    },
    "en": {
        "name": "Jarvan IV",
        "attack": "A lance thrust, +{e_as}% attack speed. " + O + "Martial Cadence" + E + ": his first hit on a champion every " + A + "{p_rest}s" + E +
                  " deals " + O + "{p_pct}% of its max health" + E + " more. " + O + "Golden Aegis" + E + ": in fights, a shield of " +
                  phy("w_sh", "w_ratio") + " (+{w_per} per enemy champion near) for " + A + "{w_t}s" + E + " and a " + R + "{w_slow}% slow" + E +
                  " to enemies near him.",
        "skill": "Throws his standard for " + phy("e_dmg", "e_ratio") + " " + O + "physical damage" + E + "; it stands " + A + "{fl_t}s" + E +
                 " giving allied champions near it +{f_as}% attack speed. Then he charges to it: enemies on the way and where he lands are " + R +
                 "knocked up {q_up}s" + E + ", take " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + " and lose {q_shred}% armour.",
        "skill2": "A lance thrust down a line: " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + " and " + R + "-{q_shred}% armour" + E +
                  " for " + A + "{q_shred_t}s" + E + ".",
        "ult": "Leaps onto an enemy champion: " + phy("r_dmg", "r_ratio") + " " + O + "physical damage" + E + " around him, and a ring of rock " + R +
               "traps enemy champions {r_t}s" + E + " - those leaving are pulled back. Cast on a knocked-up enemy or with 2 enemy champions near him.",
        "names": ("Demacian Standard", "Dragon Strike", "Cataclysm"),
    },
    "ko": {
        "name": "자르반 4세",
        "attack": "창 찌르기, 공격 속도 +{e_as}%. " + O + "전장의 군가" + E + ": 챔피언마다 " + A + "{p_rest}초" + E + "에 한 번 첫 공격이 " + O +
                  "최대 체력의 {p_pct}%" + E + " 추가 피해. " + O + "황금빛 방패" + E + ": 교전 중 " + phy("w_sh", "w_ratio") + " 보호막(주변 적 챔피언당 +{w_per}) " +
                  A + "{w_t}초" + E + ", 주변 적 " + R + "{w_slow}% 둔화" + E + ".",
        "skill": "깃발을 던져 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + ", 깃발은 " + A + "{fl_t}초" + E + "간 서서 주변 아군 챔피언 공격 속도 +{f_as}%. " +
                 "이어 깃발로 돌진: 경로와 착지 지점의 적은 " + R + "{q_up}초 띄워지고" + E + " " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + ", 방어력 -{q_shred}%.",
        "skill2": "직선으로 창을 찔러 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + "와 " + A + "{q_shred_t}초" + E + "간 " + R + "방어력 -{q_shred}%" + E + ".",
        "ult": "적 챔피언에게 뛰어올라 주변에 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + ", 바위 고리가 적 챔피언을 " + R + "{r_t}초" + E +
               " 가두고 빠져나가면 끌어당김. 띄워진 적이나 적 챔피언 2명이 가까울 때 사용.",
        "names": ("데마시아의 깃발", "용의 일격", "대격변"),
    },
    "ja": {
        "name": "ジャーヴァンⅣ",
        "attack": "槍の突き、攻撃速度+{e_as}%。" + O + "武魂の律動" + E + "：チャンピオンごとに" + A + "{p_rest}秒" + E + "に1度、最初の攻撃が" + O +
                  "最大体力の{p_pct}%" + E + "のダメージを追加。" + O + "ゴールデンイージス" + E + "：交戦中" + phy("w_sh", "w_ratio") + "のシールド" + A + "{w_t}秒" + E +
                  "（周囲の敵チャンピオン毎+{w_per}）、周囲の敵に" + R + "スロウ{w_slow}%" + E + "。",
        "skill": "旗を投げ" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "、旗は" + A + "{fl_t}秒" + E + "立ち周囲の味方の攻撃速度+{f_as}%。" +
                 "続けて旗へ突進：経路と着地点の敵を" + R + "{q_up}秒打ち上げ" + E + "、" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "と物理防御-{q_shred}%。",
        "skill2": "直線に槍を突き出し" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "、" + A + "{q_shred_t}秒" + E + R + "物理防御-{q_shred}%" + E + "。",
        "ult": "敵チャンピオンへ跳びかかり周囲に" + phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "、岩の輪が敵チャンピオンを" + R + "{r_t}秒閉じ込め" + E +
               "、出ようとすると引き戻す。打ち上げた敵か敵2体が近い時に使う。",
        "names": ("デマーシアの旗印", "ドラゴンストライク", "決戦場"),
    },
}

C = "league_jarvaniv_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_jarvaniv_a_swing": [(C + "a_swing", 0.3, 0.0)],
    "league_jarvaniv_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_jarvaniv_p_hit": [(C + "p_hit", 0.45, 0.0)],
    "league_jarvaniv_e": [(C + "e", 0.45, 0.0)],
    "league_jarvaniv_e_flag": [(C + "e_flag", 0.55, 0.0)],
    "league_jarvaniv_e_hit": [(C + "e_hit", 0.4, 0.0)],
    "league_jarvaniv_q": [(C + "q", 0.45, 0.0)],
    "league_jarvaniv_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_jarvaniv_q_dash": [(C + "q_dash", 0.5, 0.0)],
    "league_jarvaniv_q_land": [(C + "q_land", 0.5, 0.0)],
    "league_jarvaniv_w": [(C + "w", 0.5, 0.0)],
    "league_jarvaniv_r": [(C + "r", 0.5, 0.0)],
    "league_jarvaniv_r_land": [(C + "r_land", 0.6, 0.0)],
    "league_jarvaniv_r_hit": [(C + "r_hit", 0.3, 0.0)],
    "league_jarvaniv_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_jarvaniv_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_jarvaniv_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_jarvaniv_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_pct", "e_as", "e_dmg", "e_ratio", "f_as", "q_dmg", "q_ratio", "q_shred", "w_sh", "w_ratio",
                           "w_per", "w_slow", "r_dmg", "r_ratio")}
    for k in ("p_rest", "fl_t", "q_up", "q_shred_t", "w_t", "r_t"):
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
    if "Jarvan IV" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Jarvan IV. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
