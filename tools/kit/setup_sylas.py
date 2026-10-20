"""Sylas's text (5 languages), sound_info files and his keys in the shared files, numbers from build_sylas.P.

    python tools/kit/setup_sylas.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_sylas in every language, description + skill_name),
sound/sfx/league_sylas_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Sylas named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 塞拉斯 (解脱者): 破敌禁法, 锁链鞭击, 弑君突刺, 潜掠/强掳, 其人之道; zh_TW 賽勒斯 (罪鍊術士):
反魔法英石衝擊, 鍊斬, 弒君之道, 逆罪突進 / 罪獄鍊罰, 盜技禁鍊; ja サイラス: ペトリサイトバースト, 鎖の鞭, 王殺し, 逃亡 / 拉致, 乗っ取り;
ko 사일러스: 페트리사이트 폭발, 사슬 후려치기, 국왕시해자, 도주 / 억압, 강탈.
Slots: skill = Q Chain Lash, skill2 = E Abscond / Abduct, ult = R Hijack; the passive Petricite Burst and W Kingslayer
in the attack's text. No combo sentence in any text (the user's rule); the README and the add-on league_sylas say them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sylas import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_sylas"
VERSION = "0.182.0"     # the next free number above main 0.181.0 (Gnar #415, 2026-10-20); retaken at merge time
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names
M = "<#a974ffff>"      # magic damage / AP
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: provisional until the sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 1, "y": -26}, "center": {"x": 0, "y": -13}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def hl(a, r):
    return f"{G}{{{a}}}{E} + {APi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "塞拉斯",
        "attack": "甩链。" + O + "破敌禁法" + E + "：每放一个技能存一层（最多2层），有层时攻速+{p_as}%，下次普攻挥链横扫周围，" + mag("p_dmg", "p_ratio") +
                  "魔法伤害。" + O + "弑君突刺" + E + "：每" + A + "{w_cd}秒" + E + "对英雄的普攻变成突刺，" + mag("w_dmg", "w_ratio") +
                  "魔法伤害，回复" + hl("w_heal", "w_heal_r") + "生命。",
        "skill": "甩出两条锁链交叉于目标处，沿途敌人受到" + mag("q_dmg", "q_ratio") + "魔法伤害并减速{q_slow}%；" + A + "{q_wait}秒" + E +
                 "后交叉点爆炸，造成" + mag("q2_dmg", "q2_ratio") + "魔法伤害。",
        "skill2": "朝敌方英雄突进，再甩出锁链：命中的第一个敌方英雄受到" + mag("e_dmg", "e_ratio") + "魔法伤害、被" + R + "击飞" + E + A +
                  "{e_up}秒" + E + "，塞拉斯把自己拉过去。",
        "ult": "锁链命中敌方英雄，" + R + "眩晕" + E + A + "{r_stun}秒" + E + "并夺走大招；" + A + "{r_keep}秒" + E + "内再放，在目标处爆发，" +
               mag("r2_dmg", "r2_ratio") + "魔法伤害并" + R + "击飞" + E + "周围敌人。",
        "names": ("锁链鞭击", "潜掠/强掳", "其人之道"),
    },
    "zh-hant": {
        "name": "賽勒斯",
        "attack": "甩鍊。" + O + "反魔法英石衝擊" + E + "：每放一個技能存一層（最多2層），有層時攻速+{p_as}%，下次普攻揮鍊橫掃周圍，" +
                  mag("p_dmg", "p_ratio") + "魔法傷害。" + O + "弒君之道" + E + "：每" + A + "{w_cd}秒" + E + "對英雄的普攻變成突刺，" +
                  mag("w_dmg", "w_ratio") + "魔法傷害，回復" + hl("w_heal", "w_heal_r") + "生命。",
        "skill": "甩出兩條鎖鍊交叉於目標處，沿途敵人受到" + mag("q_dmg", "q_ratio") + "魔法傷害並緩速{q_slow}%；" + A + "{q_wait}秒" + E +
                 "後交叉點爆炸，造成" + mag("q2_dmg", "q2_ratio") + "魔法傷害。",
        "skill2": "朝敵方英雄突進，再甩出鎖鍊：命中的第一個敵方英雄受到" + mag("e_dmg", "e_ratio") + "魔法傷害、被" + R + "擊飛" + E + A +
                  "{e_up}秒" + E + "，賽勒斯把自己拉過去。",
        "ult": "鎖鍊命中敵方英雄，" + R + "暈眩" + E + A + "{r_stun}秒" + E + "並奪走大招；" + A + "{r_keep}秒" + E + "內再放，在目標處爆發，" +
               mag("r2_dmg", "r2_ratio") + "魔法傷害並" + R + "擊飛" + E + "周圍敵人。",
        "names": ("鍊斬", "逆罪突進/罪獄鍊罰", "盜技禁鍊"),
    },
    "en": {
        "name": "Sylas",
        "attack": "A chain swing. " + O + "Petricite Burst" + E + ": each spell he casts stores a charge (2 at most); with one he attacks "
                  "{p_as}% faster and his next attack whirls his chains round him for " + mag("p_dmg", "p_ratio") + " magic damage. " +
                  O + "Kingslayer" + E + ": every " + A + "{w_cd}s" + E + " his attack on a champion becomes a stab for " +
                  mag("w_dmg", "w_ratio") + " magic damage, healing " + hl("w_heal", "w_heal_r") + ".",
        "skill": "Lashes two chains that cross at the target: enemies along them take " + mag("q_dmg", "q_ratio") + " magic damage and "
                 "are slowed {q_slow}%; after " + A + "{q_wait}s" + E + " the crossing explodes for " + mag("q2_dmg", "q2_ratio") +
                 " magic damage.",
        "skill2": "Dashes toward an enemy champion, then throws a chain: the first enemy champion hit takes " + mag("e_dmg", "e_ratio") +
                  " magic damage, is " + R + "knocked up" + E + " for " + A + "{e_up}s" + E + " and Sylas pulls himself to it.",
        "ult": "His chain hits an enemy champion, " + R + "stuns" + E + " it for " + A + "{r_stun}s" + E + " and steals its ultimate; cast "
               "again within " + A + "{r_keep}s" + E + " to unleash it at the target: " + mag("r2_dmg", "r2_ratio") + " magic damage and "
               "nearby enemies " + R + "knocked up" + E + ".",
        "names": ("Chain Lash", "Abscond / Abduct", "Hijack"),
    },
    "ko": {
        "name": "사일러스",
        "attack": "사슬 휘두르기. " + O + "페트리사이트 폭발" + E + ": 스킬을 쓸 때마다 1회 충전(최대 2), 충전 시 공격 속도 +{p_as}%, 다음 "
                  "기본 공격이 주변에 " + mag("p_dmg", "p_ratio") + " 마법 피해. " + O + "국왕시해자" + E + ": " + A + "{w_cd}초" + E +
                  "마다 챔피언 공격이 찌르기로 바뀌어 " + mag("w_dmg", "w_ratio") + " 마법 피해, 체력 " + hl("w_heal", "w_heal_r") + " 회복.",
        "skill": "사슬 두 개를 대상 위치에서 교차시켜 경로의 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해와 {q_slow}% 둔화, " + A +
                 "{q_wait}초" + E + " 후 교차점이 폭발해 " + mag("q2_dmg", "q2_ratio") + " 마법 피해.",
        "skill2": "적 챔피언 쪽으로 돌진한 뒤 사슬을 던져 처음 맞은 적 챔피언에게 " + mag("e_dmg", "e_ratio") + " 마법 피해, " + A +
                  "{e_up}초" + E + " " + R + "공중에 띄움" + E + ", 그쪽으로 자신을 끌어당김.",
        "ult": "사슬이 적 챔피언을 맞혀 " + A + "{r_stun}초" + E + " " + R + "기절" + E + "시키고 궁극기를 빼앗음. " + A + "{r_keep}초" + E +
               " 안에 다시 쓰면 대상 위치에서 폭발해 " + mag("r2_dmg", "r2_ratio") + " 마법 피해, 주변 적 " + R + "공중에 띄움" + E + ".",
        "names": ("사슬 후려치기", "도주 / 억압", "강탈"),
    },
    "ja": {
        "name": "サイラス",
        "attack": "鎖を振るう。" + O + "ペトリサイトバースト" + E + "：スキルごとに1チャージ（最大2）、チャージ中は攻撃速度+{p_as}%、次の通常攻撃で周囲に" +
                  mag("p_dmg", "p_ratio") + "の魔法ダメージ。" + O + "王殺し" + E + "：" + A + "{w_cd}秒" + E + "ごとにチャンピオンへの攻撃が突きになり" +
                  mag("w_dmg", "w_ratio") + "の魔法ダメージ、体力" + hl("w_heal", "w_heal_r") + "回復。",
        "skill": "2本の鎖を対象の位置で交差させ、経路の敵に" + mag("q_dmg", "q_ratio") + "の魔法ダメージと{q_slow}%スロウ。" + A + "{q_wait}秒" + E +
                 "後に交差点が爆発し" + mag("q2_dmg", "q2_ratio") + "の魔法ダメージ。",
        "skill2": "敵チャンピオンへ突進し、鎖を投げる：最初に当たった敵チャンピオンに" + mag("e_dmg", "e_ratio") + "の魔法ダメージ、" + A + "{e_up}秒" +
                  E + R + "ノックアップ" + E + "、自身を引き寄せる。",
        "ult": "鎖が敵チャンピオンに当たると" + A + "{r_stun}秒" + E + R + "スタン" + E + "させアルティメットを奪う。" + A + "{r_keep}秒" + E +
               "以内に再使用で対象の位置で炸裂、" + mag("r2_dmg", "r2_ratio") + "の魔法ダメージと周囲の敵を" + R + "ノックアップ" + E + "。",
        "names": ("鎖の鞭", "逃亡 / 拉致", "乗っ取り"),
    },
}

C = "league_sylas_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_sylas_a": [(C + "a", 0.4, 0.0)],
    "league_sylas_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_sylas_p": [(C + "p", 0.4, 0.0), (C + "p_hit", 0.3, 0.15)],
    "league_sylas_w": [(C + "w", 0.45, 0.0)],
    "league_sylas_w_hit": [(C + "w_hit", 0.45, 0.0)],
    "league_sylas_q": [(C + "q", 0.45, 0.0)],
    "league_sylas_q_hit": [(C + "q_hit", 0.35, 0.0)],
    "league_sylas_q_boom": [(C + "q_boom", 0.5, 0.55)],
    "league_sylas_e": [(C + "e", 0.45, 0.0)],
    "league_sylas_e2": [(C + "e2", 0.45, 0.0)],
    "league_sylas_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_sylas_r": [(C + "r", 0.5, 0.0)],
    "league_sylas_r_steal": [(C + "r_steal", 0.5, 0.0)],
    "league_sylas_r2": [(C + "r2", 0.5, 0.0)],
    "league_sylas_r2_boom": [(C + "r2_boom", 0.5, 0.0)],
    "league_sylas_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_sylas_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_sylas_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_sylas_vo_r": [(C + "vo_r", 0.9, 0.0)],
    "league_sylas_vo_r2": [(C + "vo_r2", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_as", "p_dmg", "p_ratio", "w_dmg", "w_ratio", "w_heal", "w_heal_r", "q_dmg", "q_ratio",
                           "q_slow", "q2_dmg", "q2_ratio", "e_dmg", "e_ratio", "r2_dmg", "r2_ratio")}
    for k in ("w_cd", "q_wait", "e_up", "r_stun", "r_keep"):
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
    if "Sylas" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Sylas. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
