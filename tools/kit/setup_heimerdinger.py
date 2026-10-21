"""Heimerdinger's text (5 languages), sound_info files and his keys in the shared files, numbers from
build_heimerdinger.P.

    python tools/kit/setup_heimerdinger.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_heimerdinger in every language, description + skill_name),
sound/sfx/league_heimerdinger_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Heimerdinger named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 黑默丁格 (大发明家): 海克斯科技亲和, H-28 G 进化炮台, 海克斯科技微型导弹, CH-2电子风暴手雷,
升级！！！; zh_TW 漢默丁格: 海克斯親合性, H-28 G 進化砲臺, 高科技微型火箭, CH-2 暴風手雷, 升級！！！; ja ハイマーディンガー:
ヘクステックの親和性, H-28G革新砲, ヘクステック小型ロケット, CH-2超電磁グレネード, アップグレード！！！; ko 하이머딩거: 마법공학 전문가,
H-28 G 진화형 포탑, 마법공학 초소형 로켓, CH-2 전자폭풍 수류탄, 업그레이드!!!. R's two upgrades are described, not named
(CH-3X / H-28Q have no Data Dragon names in every language).
Slots: skill = Q the turret (with the passive Hextech Affinity), skill2 = E the grenade, ult = R UPGRADE!!!; W's rockets
are in the attack's text. No combo sentence in any text (the user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_heimerdinger import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_heimerdinger"
VERSION = "0.188.2"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: the face point between his goggles (ppu_restyle face_to: 19 game px over his soles, 4 ahead of his
# standing point), the centre as the other small heroes' (Vex, Ziggs); no banpick_center (36 px: the card holds him)
VIEW = {"face": {"x": 4, "y": -19}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


TEXT = {
    "zh-hans": {
        "name": "黑默丁格",
        "attack": "射出一道海克斯电光。" + O + "海克斯科技微型导弹" + E + "：每第3次普攻额外射出{w_n}枚导弹，每枚造成" +
                  mag("w_dmg", "w_ratio") + "魔法伤害。",
        "skill": "放下一座炮台（最多3座）" + t("{t_life}秒") + "，每" + t("{t_per}秒") + "攻击一个敌人，造成" + mag("t_dmg", "t_ratio") +
                 "魔法伤害；对受控制的英雄发射光束，造成" + mag("tb_dmg", "tb_ratio") + "。" + O + "海克斯科技亲和" + E +
                 "：在炮台旁移速+{p_ms}%。",
        "skill2": "掷出手雷，造成" + mag("e_dmg", "e_ratio") + "魔法伤害并减速{e_slow}%，正中的敌人被" + R + "眩晕" + E +
                  t("{e_stun}秒") + "。",
        "ult": "升级！敌人扎堆时连掷3颗强化手雷，每颗" + mag("re_dmg", "re_ratio") + "魔法伤害并" + R + "眩晕" + E + t("{re_stun}秒") +
               "；否则放下巨型炮台" + t("{x_life}秒") + "，每" + t("{x_per}秒") + "造成" + mag("x_dmg", "x_ratio") + "并减速{x_slow}%。",
        "names": ("H-28 G 进化炮台", "CH-2电子风暴手雷", "升级！！！"),
    },
    "zh-hant": {
        "name": "漢默丁格",
        "attack": "射出一道海克斯電光。" + O + "高科技微型火箭" + E + "：每第3次普攻額外射出{w_n}枚火箭，每枚造成" +
                  mag("w_dmg", "w_ratio") + "魔法傷害。",
        "skill": "放下一座砲臺（最多3座）" + t("{t_life}秒") + "，每" + t("{t_per}秒") + "攻擊一個敵人，造成" + mag("t_dmg", "t_ratio") +
                 "魔法傷害；對受控制的英雄發射光束，造成" + mag("tb_dmg", "tb_ratio") + "。" + O + "海克斯親合性" + E +
                 "：在砲臺旁跑速+{p_ms}%。",
        "skill2": "擲出手雷，造成" + mag("e_dmg", "e_ratio") + "魔法傷害並緩速{e_slow}%，正中的敵人被" + R + "暈眩" + E +
                  t("{e_stun}秒") + "。",
        "ult": "升級！敵人聚集時連擲3顆強化手雷，每顆" + mag("re_dmg", "re_ratio") + "魔法傷害並" + R + "暈眩" + E + t("{re_stun}秒") +
               "；否則放下巨型砲臺" + t("{x_life}秒") + "，每" + t("{x_per}秒") + "造成" + mag("x_dmg", "x_ratio") + "並緩速{x_slow}%。",
        "names": ("H-28 G 進化砲臺", "CH-2 暴風手雷", "升級！！！"),
    },
    "en": {
        "name": "Heimerdinger",
        "attack": "Fires a hextech bolt. " + O + "Hextech Micro-Rockets" + E + ": every third attack also fires {w_n} rockets, each "
                  "dealing " + mag("w_dmg", "w_ratio") + " " + M + "magic damage" + E + ".",
        "skill": "Sets down a turret (up to 3) for " + t("{t_life}s") + " that strikes one enemy every " + t("{t_per}s") + " for " +
                 mag("t_dmg", "t_ratio") + " " + M + "magic damage" + E + ", or beams a crowd-controlled champion for " +
                 mag("tb_dmg", "tb_ratio") + ". " + O + "Hextech Affinity" + E + ": +{p_ms}% move speed near his turrets.",
        "skill2": "Throws a grenade that deals " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + " and slows by {e_slow}%; "
                  "enemies at its centre are " + R + "stunned" + E + " for " + t("{e_stun}s") + ".",
        "ult": "UPGRADE! Against a crowd: three empowered grenades, each " + mag("re_dmg", "re_ratio") + " " + M + "magic damage" + E +
               " and a " + t("{re_stun}s") + " " + R + "stun" + E + ". Otherwise: an apex turret for " + t("{x_life}s") + ", every " +
               t("{x_per}s") + " " + mag("x_dmg", "x_ratio") + " and a {x_slow}% slow.",
        "names": ("H-28 G Evolution Turret", "CH-2 Electron Storm Grenade", "UPGRADE!!!"),
    },
    "ko": {
        "name": "하이머딩거",
        "attack": "마법공학 전격을 쏜다. " + O + "마법공학 초소형 로켓" + E + ": 세 번째 공격마다 로켓 {w_n}발을 추가로 쏘아 발당 " +
                  mag("w_dmg", "w_ratio") + " 마법 피해.",
        "skill": "포탑을 설치한다(최대 3개, " + t("{t_life}초") + "). " + t("{t_per}초") + "마다 적 하나에게 " + mag("t_dmg", "t_ratio") +
                 " 마법 피해, 군중 제어된 챔피언에게는 광선으로 " + mag("tb_dmg", "tb_ratio") + ". " + O + "마법공학 전문가" + E +
                 ": 포탑 근처에서 이동 속도 +{p_ms}%.",
        "skill2": "수류탄을 던져 " + mag("e_dmg", "e_ratio") + " 마법 피해와 {e_slow}% 둔화, 중심의 적은 " + t("{e_stun}초") + " " + R +
                  "기절" + E + ".",
        "ult": "업그레이드! 적이 모여 있으면 강화 수류탄 3개(각 " + mag("re_dmg", "re_ratio") + " 마법 피해, " + t("{re_stun}초") + " " + R +
               "기절" + E + "), 아니면 거대 포탑 " + t("{x_life}초") + ": " + t("{x_per}초") + "마다 " + mag("x_dmg", "x_ratio") +
               ", {x_slow}% 둔화.",
        "names": ("H-28 G 진화형 포탑", "CH-2 전자폭풍 수류탄", "업그레이드!!!"),
    },
    "ja": {
        "name": "ハイマーディンガー",
        "attack": "ヘクステックの電撃を撃つ。" + O + "ヘクステック小型ロケット" + E + "：3回目の通常攻撃ごとにロケット{w_n}発を追加で撃ち、1発" +
                  mag("w_dmg", "w_ratio") + "の魔法ダメージ。",
        "skill": "砲台を設置（最大3基、" + t("{t_life}秒") + "）。" + t("{t_per}秒") + "ごとに敵1体に" + mag("t_dmg", "t_ratio") +
                 "の魔法ダメージ、行動妨害中のチャンピオンにはビームで" + mag("tb_dmg", "tb_ratio") + "。" + O + "ヘクステックの親和性" + E +
                 "：砲台の近くで移動速度+{p_ms}%。",
        "skill2": "グレネードを投げ" + mag("e_dmg", "e_ratio") + "の魔法ダメージと{e_slow}%スロウ、中心の敵を" + t("{e_stun}秒") + R +
                  "スタン" + E + "。",
        "ult": "アップグレード！敵が密集していれば強化グレネード3個（各" + mag("re_dmg", "re_ratio") + "の魔法ダメージ、" + t("{re_stun}秒") +
               R + "スタン" + E + "）、でなければ巨大砲台" + t("{x_life}秒") + "：" + t("{x_per}秒") + "ごとに" + mag("x_dmg", "x_ratio") +
               "、{x_slow}%スロウ。",
        "names": ("H-28G革新砲", "CH-2超電磁グレネード", "アップグレード！！！"),
    },
}

C = "league_heimerdinger_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {f"league_heimerdinger_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.3), ("a_hit", 0.35), ("w", 0.4), ("w_hit", 0.25), ("q", 0.4), ("t_spawn", 0.4), ("t_hit", 0.25),
    ("t_beam", 0.4), ("e", 0.4), ("e_land", 0.5), ("e_stun", 0.4), ("r", 0.5), ("re", 0.45), ("re_land", 0.55),
    ("rq", 0.45), ("x_spawn", 0.45), ("x_hit", 0.35), ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("w_n", "w_dmg", "w_ratio", "t_dmg", "t_ratio", "tb_dmg", "tb_ratio", "p_ms", "e_dmg", "e_ratio",
                           "e_slow", "re_dmg", "re_ratio", "x_dmg", "x_ratio", "x_slow")}
    for k in ("t_life", "t_per", "e_stun", "re_stun", "x_life", "x_per"):
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
    if "Heimerdinger" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Heimerdinger. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
