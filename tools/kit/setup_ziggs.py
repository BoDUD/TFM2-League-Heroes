"""Ziggs's text (5 languages), sound_info files and his keys in the shared files, numbers from build_ziggs.P.

    python tools/kit/setup_ziggs.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_ziggs in every language, description + skill_name),
sound/sfx/league_ziggs_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Ziggs named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 吉格斯 (爆破鬼才): 一触即发, 弹跳炸弹, 定点爆破, 海克斯爆破雷区, 科学的地狱火炮; zh_TW 希格斯:
即刻爆發, 彈跳炸彈, 技術性引爆, 海克斯詭雷, 煉獄炸彈; ja ジグス: ショートヒューズ, バウンドボム, エンジニアボム, ヘクステックマイン,
メガインフェルノボム; ko 직스: 짧은 도화선, 반동 폭탄, 휴대용 폭약, 마법공학 지뢰밭, 지옥 화염 폭탄.
Slots: skill = Q Bouncing Bomb, skill2 = E Hexplosive Minefield, ult = R Mega Inferno Bomb; the passive and the
automatic W in the attack's text. No combo sentence in any text (the user's rule). The main pack's rules are the ones
written; the add-on's tower hexplode is named as the add-on's.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_ziggs import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_ziggs"
VERSION = "0.140.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between his goggles (ppu_restyle face_to); his idle tops 20 px over the frame centre,
# under the card's -28 line, so no banpick_center (card-banpick rule)
# 2026-10-25: face (2,-27) - (2,-26) cut the top of his goggles; kept equal to champion_view and ppu_restyle.py
VIEW = {"face": {"x": 2, "y": -27}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "吉格斯",
        "attack": "扔小炸弹。" + O + "一触即发" + E + "：每" + A + "{p_t}秒" + E + "下次普攻多造成" + mag("p_dmg", "p_ratio") + M + "魔法伤害" + E +
                  "，每放一个技能冷却-" + A + "{p_cut}秒" + E + "。" + O + "定点爆破" + E + "：3级起，敌方英雄贴身时在脚下引爆，造成" +
                  mag("w_dmg", "w_ratio") + M + "魔法伤害" + E + "并" + R + "击退" + E + "，自己也被炸开。",
        "skill": "扔出炸弹沿直线弹跳，最多落地" + A + "3次" + E + "，落地时附近有敌人就爆炸：周围敌人受到" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "。",
        "skill2": "撒下雷区" + A + "{e_t}秒" + E + "：敌人第一次踩雷受到" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "，之后每" + A + "{e_p}秒" + E +
                  "受到其{e_low}%；每次踩雷" + R + "减速{e_slow}%" + E + "。",
        "ult": "把超大炸弹扔向远处的敌方英雄，落点先出现预警：范围内敌人受到" + mag("r_dmg", "r_ratio") + M + "魔法伤害" + E + "，中心共受到" +
               mag("r_tot", "r_tratio") + "。优先扔向被控制的敌方英雄。",
        "names": ("弹跳炸弹", "海克斯爆破雷区", "科学的地狱火炮"),
    },
    "zh-hant": {
        "name": "希格斯",
        "attack": "扔小炸彈。" + O + "即刻爆發" + E + "：每" + A + "{p_t}秒" + E + "下次普攻多造成" + mag("p_dmg", "p_ratio") + M + "魔法傷害" + E +
                  "，每施放一個技能冷卻-" + A + "{p_cut}秒" + E + "。" + O + "技術性引爆" + E + "：3級起，敵方英雄貼身時在腳下引爆，造成" +
                  mag("w_dmg", "w_ratio") + M + "魔法傷害" + E + "並" + R + "擊退" + E + "，自己也被炸開。",
        "skill": "扔出炸彈沿直線彈跳，最多落地" + A + "3次" + E + "，落地時附近有敵人就爆炸：周圍敵人受到" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "。",
        "skill2": "撒下雷區" + A + "{e_t}秒" + E + "：敵人第一次踩雷受到" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "，之後每" + A + "{e_p}秒" + E +
                  "受到其{e_low}%；每次踩雷" + R + "緩速{e_slow}%" + E + "。",
        "ult": "把超大炸彈扔向遠處的敵方英雄，落點先出現預警：範圍內敵人受到" + mag("r_dmg", "r_ratio") + M + "魔法傷害" + E + "，中心共受到" +
               mag("r_tot", "r_tratio") + "。優先扔向被控制的敵方英雄。",
        "names": ("彈跳炸彈", "海克斯詭雷", "煉獄炸彈"),
    },
    "en": {
        "name": "Ziggs",
        "attack": "Tosses a small bomb. " + O + "Short Fuse" + E + ": every " + A + "{p_t}s" + E + " his next attack deals " +
                  mag("p_dmg", "p_ratio") + " " + M + "magic damage" + E + " more; each spell he casts takes " + A + "{p_cut}s" + E + " off. " +
                  O + "Satchel Charge" + E + ": from level 3, when an enemy champion closes in, it blows up at his feet for " +
                  mag("w_dmg", "w_ratio") + " " + M + "magic damage" + E + ", " + R + "knocking enemies back" + E + " and blasting him away.",
        "skill": "A bomb that bounces along a line, landing up to " + A + "3 times" + E + "; it blows up on landing next to an enemy: " +
                 mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " around it.",
        "skill2": "Scatters mines for " + A + "{e_t}s" + E + ": an enemy's first mine deals " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  ", then {e_low}% of it every " + A + "{e_p}s" + E + " it stays; each mine " + R + "slows {e_slow}%" + E + ".",
        "ult": "Hurls a huge bomb at a far enemy champion, its landing spot marked first: " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               " in the blast, " + mag("r_tot", "r_tratio") + " at its centre. Thrown first at champions held by crowd control.",
        "names": ("Bouncing Bomb", "Hexplosive Minefield", "Mega Inferno Bomb"),
    },
    "ko": {
        "name": "직스",
        "attack": "작은 폭탄을 던진다. " + O + "짧은 도화선" + E + ": " + A + "{p_t}초" + E + "마다 다음 공격이 " + mag("p_dmg", "p_ratio") + "의 " + M +
                  "마법 피해" + E + " 추가, 스킬 사용 시 " + A + "{p_cut}초" + E + " 감소. " + O + "휴대용 폭약" + E + ": 3레벨부터 적 챔피언이 붙으면 발밑에서 터져 " +
                  mag("w_dmg", "w_ratio") + "의 " + M + "마법 피해" + E + "와 " + R + "밀쳐내기" + E + ", 자신도 튕겨 나감.",
        "skill": "직선으로 튀는 폭탄, 최대 " + A + "3번" + E + " 착지하며 근처에 적이 있으면 폭발해 주변에 " + mag("q_dmg", "q_ratio") + "의 " + M + "마법 피해" + E + ".",
        "skill2": A + "{e_t}초" + E + "간 지뢰를 뿌린다: 적이 처음 밟으면 " + mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E + ", 이후 " + A + "{e_p}초" + E +
                  "마다 {e_low}%, 밟을 때마다 " + R + "{e_slow}% 둔화" + E + ".",
        "ult": "먼 적 챔피언에게 거대한 폭탄을 던지고 낙하 지점을 먼저 표시: 범위에 " + mag("r_dmg", "r_ratio") + "의 " + M + "마법 피해" + E + ", 중심은 " +
               mag("r_tot", "r_tratio") + ". 군중 제어에 걸린 적 챔피언을 우선.",
        "names": ("반동 폭탄", "마법공학 지뢰밭", "지옥 화염 폭탄"),
    },
    "ja": {
        "name": "ジグス",
        "attack": "小さな爆弾を投げる。" + O + "ショートヒューズ" + E + "：" + A + "{p_t}秒" + E + "毎に次の通常攻撃が" + mag("p_dmg", "p_ratio") + "の" + M +
                  "魔法ダメージ" + E + "を追加、スキル使用で" + A + "{p_cut}秒" + E + "短縮。" + O + "エンジニアボム" + E + "：Lv3から敵チャンピオンが迫ると足元で爆発、" +
                  mag("w_dmg", "w_ratio") + "の" + M + "魔法ダメージ" + E + "と" + R + "ノックバック" + E + "、自分も吹き飛ぶ。",
        "skill": "直線に跳ねる爆弾、最大" + A + "3回" + E + "着地し近くに敵がいれば爆発、周囲に" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "。",
        "skill2": A + "{e_t}秒" + E + "地雷を撒く：最初に踏んだ敵に" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "、以後" + A + "{e_p}秒" + E +
                  "毎に{e_low}%、踏む度に" + R + "スロウ{e_slow}%" + E + "。",
        "ult": "遠くの敵チャンピオンへ巨大爆弾を投げ、着弾点を予告：範囲に" + mag("r_dmg", "r_ratio") + "の" + M + "魔法ダメージ" + E + "、中心は" +
               mag("r_tot", "r_tratio") + "。行動妨害中の敵を優先。",
        "names": ("バウンドボム", "ヘクステックマイン", "メガインフェルノボム"),
    },
}

C = "league_ziggs_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_ziggs_a": [(C + "a", 0.3, 0.0)],
    "league_ziggs_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_ziggs_p": [(C + "p", 0.4, 0.0)],
    "league_ziggs_p_hit": [(C + "p_hit", 0.45, 0.0)],
    "league_ziggs_q": [(C + "q", 0.45, 0.0)],
    "league_ziggs_q_bounce": [(C + "q_bounce", 0.35, 0.0)],
    "league_ziggs_q_blast": [(C + "q_blast", 0.5, 0.0)],
    "league_ziggs_q_hit": [(C + "q_hit", 0.3, 0.0)],
    "league_ziggs_e": [(C + "e", 0.45, 0.0)],
    "league_ziggs_e_land": [(C + "e_land", 0.45, 0.0)],
    "league_ziggs_e_hit": [(C + "e_hit", 0.35, 0.0)],
    "league_ziggs_w": [(C + "w", 0.45, 0.0)],
    "league_ziggs_w_blast": [(C + "w_blast", 0.6, 0.0)],
    "league_ziggs_w_hit": [(C + "w_hit", 0.3, 0.0)],
    "league_ziggs_r": [(C + "r", 0.55, 0.0)],
    "league_ziggs_r_boom": [(C + "r_boom", 0.7, 0.0)],
    "league_ziggs_r_hit": [(C + "r_hit", 0.3, 0.0)],
    "league_ziggs_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_ziggs_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_ziggs_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_ziggs_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ratio", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_low", "e_slow", "w_dmg", "w_ratio",
                           "r_dmg", "r_ratio")}
    v["r_tot"], v["r_tratio"] = p["r_dmg"] + p["r_cdmg"], p["r_ratio"] + p["r_cratio"]
    v["p_cut"] = secs(p["p_t"] // 3)
    for k in ("p_t", "e_t", "e_p"):
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
    if "Ziggs" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Ziggs. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
