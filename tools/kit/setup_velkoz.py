"""Vel'Koz's text (5 languages), sound_info files and his keys in the shared files, numbers from build_velkoz.P.

    python tools/kit/setup_velkoz.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_velkoz in every language, description + skill_name),
sound/sfx/league_velkoz_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Vel'Koz named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 维克兹 (虚空之眼): 有机体解构, 等离子裂变, 虚空裂隙, 构造分解, 生命形态瓦解射线; zh_TW 威寇茲
(虛空魔眼): 結構毀滅, 分裂電漿, 虛空裂痕, 反物質瓦解, 生化射線; ja ヴェル＝コズ: 有機分解, 電離炸裂弾, ヴォイドの裂谷, 地殻砕裂,
生体破壊光線; ko 벨코즈: 유기물 분해, 플라즈마 분열, 공허 균열, 지각 붕괴, 생물 분해 광선.
Slots: skill = Q Plasma Fission, skill2 = E Tectonic Disruption, ult = R Life Form Disintegration Ray; the passive
Organic Deconstruction and W Void Rift (every third attack) are in the attack's text. No combo sentence in any text
(the user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_velkoz import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_velkoz"
VERSION = "0.184.0"     # the next free number above main 0.183.0 (Sylas #416, Mel #418, 2026-10-20)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
W = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: the face point on his big eye (ppu_restyle face_to), the body centre on the middle of his shell (he
# floats 4 squares up: hits and the health bar anchor there)
VIEW = {"face": {"x": 7, "y": -21}, "center": {"x": 0, "y": -18}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def tru(d, r):
    return f"{W}{{{d}}}{E} + {APi}{W}{{{r}}}%{E}"


def t(x):
    return A + x + E


TEXT = {
    "zh-hans": {
        "name": "维克兹",
        "attack": "发射虚空能量。每第3次普攻打开" + O + "虚空裂隙" + E + "，造成" + mag("w_dmg", "w_ratio") + "魔法伤害，随后爆炸再造成" +
                  mag("w_dmg2", "w_ratio2") + "。" + O + "有机体解构" + E + "：技能命中英雄叠层，3层时造成" + tru("p_dmg", "p_ratio") +
                  W + "真实伤害" + E + "。",
        "skill": "发射一束等离子，造成" + mag("q_dmg", "q_ratio") + "魔法伤害并减速{q_slow}%，持续" + t("{q_slow_t}秒") +
                 "。命中后一分为二，对周围敌人造成" + mag("q_sdmg", "q_sratio") + "魔法伤害和减速。",
        "skill2": "让目标区域爆炸，造成" + mag("e_dmg", "e_ratio") + "魔法伤害并" + R + "击飞" + E + "敌人" + t("{e_air}秒") + "。",
        "ult": "引导一束射线" + t("{r_t}秒") + "，共造成" + mag("r_dmg", "r_ratio") + "魔法伤害。对被" + O + "有机体解构" + E +
               "研究过的英雄改为" + W + "真实伤害" + E + "。",
        "names": ("等离子裂变", "构造分解", "生命形态瓦解射线"),
    },
    "zh-hant": {
        "name": "威寇茲",
        "attack": "發射虛空能量。每第3次普攻打開" + O + "虛空裂痕" + E + "，造成" + mag("w_dmg", "w_ratio") + "魔法傷害，隨後爆炸再造成" +
                  mag("w_dmg2", "w_ratio2") + "。" + O + "結構毀滅" + E + "：技能命中英雄疊層，3層時造成" + tru("p_dmg", "p_ratio") +
                  W + "真實傷害" + E + "。",
        "skill": "發射一束電漿，造成" + mag("q_dmg", "q_ratio") + "魔法傷害並緩速{q_slow}%，持續" + t("{q_slow_t}秒") +
                 "。命中後一分為二，對周圍敵人造成" + mag("q_sdmg", "q_sratio") + "魔法傷害和緩速。",
        "skill2": "讓目標區域爆炸，造成" + mag("e_dmg", "e_ratio") + "魔法傷害並" + R + "擊飛" + E + "敵人" + t("{e_air}秒") + "。",
        "ult": "引導一道射線" + t("{r_t}秒") + "，共造成" + mag("r_dmg", "r_ratio") + "魔法傷害。對被" + O + "結構毀滅" + E +
               "研究過的英雄改為" + W + "真實傷害" + E + "。",
        "names": ("分裂電漿", "反物質瓦解", "生化射線"),
    },
    "en": {
        "name": "Vel'Koz",
        "attack": "Fires void energy. Every third attack opens a " + O + "Void Rift" + E + ": " + mag("w_dmg", "w_ratio") + " " + M +
                  "magic damage" + E + ", then it detonates for " + mag("w_dmg2", "w_ratio2") + ". " + O + "Organic Deconstruction" +
                  E + ": spell hits on champions stack; the third deals " + tru("p_dmg", "p_ratio") + " " + W + "true damage" + E + ".",
        "skill": "Shoots a bolt of plasma that deals " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " and slows by "
                 "{q_slow}% for " + t("{q_slow_t}s") + ". On hit it splits in two, dealing " + mag("q_sdmg", "q_sratio") + " " + M +
                 "magic damage" + E + " and the slow to nearby enemies.",
        "skill2": "Causes an area to explode, dealing " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + " and " + R +
                  "knocking up" + E + " enemies for " + t("{e_air}s") + ".",
        "ult": "Channels a beam for " + t("{r_t}s") + " that deals " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               " in total. Champions researched by " + O + "Organic Deconstruction" + E + " take " + W + "true damage" + E +
               " instead.",
        "names": ("Plasma Fission", "Tectonic Disruption", "Life Form Disintegration Ray"),
    },
    "ko": {
        "name": "벨코즈",
        "attack": "공허 에너지를 발사한다. 3번째 공격마다 " + O + "공허 균열" + E + "을 열어 " + mag("w_dmg", "w_ratio") +
                  " 마법 피해, 이어서 폭발해 " + mag("w_dmg2", "w_ratio2") + ". " + O + "유기물 분해" + E + ": 스킬이 챔피언에게 적중하면 "
                  "중첩, 3회 중첩 시 " + tru("p_dmg", "p_ratio") + " " + W + "고정 피해" + E + ".",
        "skill": "플라즈마를 발사해 " + mag("q_dmg", "q_ratio") + " 마법 피해를 입히고 " + t("{q_slow_t}초") +
                 " 동안 {q_slow}% 둔화. 적중하면 둘로 분열해 주변 적에게 " + mag("q_sdmg", "q_sratio") + " 마법 피해와 둔화.",
        "skill2": "지역을 폭발시켜 " + mag("e_dmg", "e_ratio") + " 마법 피해를 입히고 적을 " + t("{e_air}초") + " " + R + "에어본" + E +
                  ".",
        "ult": t("{r_t}초") + " 동안 광선을 정신 집중해 총 " + mag("r_dmg", "r_ratio") + " 마법 피해. " + O + "유기물 분해" + E +
               "로 연구된 챔피언은 " + W + "고정 피해" + E + "를 입는다.",
        "names": ("플라즈마 분열", "지각 붕괴", "생물 분해 광선"),
    },
    "ja": {
        "name": "ヴェル＝コズ",
        "attack": "ヴォイドのエネルギーを放つ。3回目の通常攻撃ごとに" + O + "ヴォイドの裂谷" + E + "を開き" + mag("w_dmg", "w_ratio") +
                  "の魔法ダメージ、続いて爆発し" + mag("w_dmg2", "w_ratio2") + "。" + O + "有機分解" + E + "：スキルがチャンピオンに"
                  "命中するとスタック、3スタックで" + tru("p_dmg", "p_ratio") + "の" + W + "確定ダメージ" + E + "。",
        "skill": "電離弾を放ち" + mag("q_dmg", "q_ratio") + "の魔法ダメージと" + t("{q_slow_t}秒") + "の{q_slow}%スロウ。命中すると二つに"
                 "分裂し、周囲の敵に" + mag("q_sdmg", "q_sratio") + "の魔法ダメージとスロウ。",
        "skill2": "範囲を爆発させ" + mag("e_dmg", "e_ratio") + "の魔法ダメージを与え、敵を" + t("{e_air}秒") + R + "打ち上げ" + E + "。",
        "ult": t("{r_t}秒") + "光線を照射し合計" + mag("r_dmg", "r_ratio") + "の魔法ダメージ。" + O + "有機分解" + E +
               "で研究済みのチャンピオンには" + W + "確定ダメージ" + E + "。",
        "names": ("電離炸裂弾", "地殻砕裂", "生体破壊光線"),
    },
}

C = "league_velkoz_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {f"league_velkoz_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.3), ("a_hit", 0.35), ("q", 0.4), ("q_hit", 0.4), ("q_split", 0.35), ("q_split_hit", 0.35), ("w", 0.4),
    ("w_hit", 0.35), ("w_boom", 0.45), ("e", 0.4), ("e_boom", 0.5), ("e_air", 0.45), ("r", 0.45), ("r_beam", 0.55),
    ("r_hit", 0.25), ("r_true", 0.3), ("r_end", 0.4), ("p_1", 0.35), ("p_2", 0.35), ("p_full", 0.5), ("vo_q", 0.85),
    ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ratio", "w_dmg", "w_ratio", "w_dmg2", "w_ratio2", "q_dmg", "q_ratio", "q_slow",
                           "q_sdmg", "q_sratio", "e_dmg", "e_ratio", "r_dmg", "r_ratio")}
    for k in ("p_keep", "q_slow_t", "e_air", "r_t"):
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
    if "Vel'Koz" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Vel'Koz. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
