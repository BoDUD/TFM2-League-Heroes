"""Neeko's text (5 languages), sound_info files and her keys in the shared files, numbers from build_neeko.P.

    python tools/kit/setup_neeko.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_neeko in every language, description + skill_name),
sound/sfx/league_neeko_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Neeko named). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 妮蔻 (万花通灵): 天生幻魅, 盛开花种, 两生花影, 缠结倒刺, 怒放; zh_TW 妮可 (好奇變色龍):
原生模影, 爆裂艷花, 擬態分裂, 螺旋刺花, 萬紫千紅; ja ニーコ: 駆け巡る色彩, 弾ける花弁, シェイプスプリッター, からまれ！, ポップブロッサム;
ko 니코: 태고의 마력, 꽃망울 폭발, 형상 분리, 칭칭올가미, 만개.
Slots: skill = Q Blooming Burst, skill2 = E Tangle-Barbs, ult = R Pop Blossom; W Shapesplitter's passive is in the
attack's text. The passive Inherent Glamour is the add-on's (its own text there). No combo sentence in any text (the
user's rule).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_neeko import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_neeko"
VERSION = "0.189.0"     # provisional: above main 0.187.0 (Naafiri #426) and Heimerdinger's 0.188.0 (2026-10-21)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: provisional until the sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 1, "y": -30}, "center": {"x": 0, "y": -15}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


TEXT = {
    "zh-hans": {
        "name": "妮蔻",
        "attack": "发射一颗魔法弹。" + O + "两生花影" + E + "：每第三次攻击额外造成" + mag("w_dmg", "w_ratio") + "魔法伤害，并提高{w_ms}%移动速度" +
                  t("{w_ms_t}秒") + "。",
        "skill": "扔出一颗种子，落地炸开造成" + mag("q_dmg", "q_ratio") + "魔法伤害。炸到英雄时会再次盛开，最多两次，每次" +
                 mag("q2_dmg", "q2_ratio") + "魔法伤害。",
        "skill2": "投出一团贯穿的倒刺，路径上的敌人受到" + mag("e_dmg", "e_ratio") + "魔法伤害并被" + R + "禁锢" + E + t("{e_root}秒") +
                  "。穿过英雄后，后面的英雄多被禁锢" + t("{e_add}秒") + "。",
        "ult": "蓄力" + t("{r_charge}秒") + "，获得" + G + "护盾" + E + "（附近每个敌方英雄额外{r_sh_c}），然后跃起" + R + "击飞" + E +
               "周围敌人，落地造成" + mag("r_dmg", "r_ratio") + "魔法伤害并" + R + "晕眩" + E + t("{r_stun}秒") + "。",
        "names": ("盛开花种", "缠结倒刺", "怒放"),
    },
    "zh-hant": {
        "name": "妮可",
        "attack": "射出一顆魔法彈。" + O + "擬態分裂" + E + "：每第三次攻擊額外造成" + mag("w_dmg", "w_ratio") + "魔法傷害，並提高{w_ms}%移動速度" +
                  t("{w_ms_t}秒") + "。",
        "skill": "丟出一顆種子，落地炸開造成" + mag("q_dmg", "q_ratio") + "魔法傷害。炸到英雄時會再次綻放，最多兩次，每次" +
                 mag("q2_dmg", "q2_ratio") + "魔法傷害。",
        "skill2": "擲出一團貫穿的刺花，路徑上的敵人受到" + mag("e_dmg", "e_ratio") + "魔法傷害並被" + R + "定身" + E + t("{e_root}秒") +
                  "。穿過英雄後，後面的英雄多被定身" + t("{e_add}秒") + "。",
        "ult": "蓄力" + t("{r_charge}秒") + "，獲得" + G + "護盾" + E + "（附近每個敵方英雄額外{r_sh_c}），然後躍起" + R + "擊飛" + E +
               "周圍敵人，落地造成" + mag("r_dmg", "r_ratio") + "魔法傷害並" + R + "暈眩" + E + t("{r_stun}秒") + "。",
        "names": ("爆裂艷花", "螺旋刺花", "萬紫千紅"),
    },
    "en": {
        "name": "Neeko",
        "attack": "Fires a magic bolt. " + O + "Shapesplitter" + E + ": every third attack deals " + mag("w_dmg", "w_ratio") + " bonus " +
                  M + "magic damage" + E + " and grants {w_ms}% move speed for " + t("{w_ms_t}s") + ".",
        "skill": "Throws a seed that bursts for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + ". If it hits a champion "
                 "it blooms again, up to twice, for " + mag("q2_dmg", "q2_ratio") + " " + M + "magic damage" + E + " each.",
        "skill2": "Flings a piercing tangle of barbs, dealing " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + " and " + R +
                  "rooting" + E + " every enemy on the line for " + t("{e_root}s") + ". Champions past the first are rooted " +
                  t("{e_add}s") + " longer.",
        "ult": "Charges for " + t("{r_charge}s") + " behind a " + G + "shield" + E + " ({r_sh_c} more per nearby enemy champion), then "
               "leaps, " + R + "knocking up" + E + " enemies around her, and lands for " + mag("r_dmg", "r_ratio") + " " + M +
               "magic damage" + E + ", " + R + "stunning" + E + " them for " + t("{r_stun}s") + ".",
        "names": ("Blooming Burst", "Tangle-Barbs", "Pop Blossom"),
    },
    "ko": {
        "name": "니코",
        "attack": "마법 탄을 쏜다. " + O + "형상 분리" + E + ": 세 번째 공격마다 " + mag("w_dmg", "w_ratio") + " 추가 마법 피해, " +
                  t("{w_ms_t}초") + " 동안 이동 속도 {w_ms}% 증가.",
        "skill": "씨앗을 던져 터뜨려 " + mag("q_dmg", "q_ratio") + " 마법 피해. 챔피언에 맞으면 최대 두 번 다시 피어나 각각 " +
                 mag("q2_dmg", "q2_ratio") + " 마법 피해.",
        "skill2": "관통하는 가시 덩어리를 던져 직선상의 적에게 " + mag("e_dmg", "e_ratio") + " 마법 피해를 입히고 " + t("{e_root}초") + " " +
                  R + "속박" + E + ". 챔피언을 지난 뒤 맞은 챔피언은 " + t("{e_add}초") + " 더 속박.",
        "ult": t("{r_charge}초") + " 동안 힘을 모으며 " + G + "보호막" + E + "(주변 적 챔피언마다 {r_sh_c} 추가)을 얻고, 뛰어올라 주변 적을 " +
               R + "에어본" + E + "시킨 뒤 착지해 " + mag("r_dmg", "r_ratio") + " 마법 피해와 " + t("{r_stun}초") + " " + R + "기절" + E + ".",
        "names": ("꽃망울 폭발", "칭칭올가미", "만개"),
    },
    "ja": {
        "name": "ニーコ",
        "attack": "魔法弾を撃つ。" + O + "シェイプスプリッター" + E + "：3回目の通常攻撃ごとに" + mag("w_dmg", "w_ratio") + "の追加魔法ダメージ、" +
                  t("{w_ms_t}秒") + "移動速度{w_ms}%増加。",
        "skill": "種を投げて弾けさせ" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。チャンピオンに当たると最大2回再び咲き、各" +
                 mag("q2_dmg", "q2_ratio") + "の魔法ダメージ。",
        "skill2": "貫通するトゲの塊を投げ、直線上の敵に" + mag("e_dmg", "e_ratio") + "の魔法ダメージと" + t("{e_root}秒") + R + "移動不能" + E +
                  "。チャンピオンを通過した後は" + t("{e_add}秒") + "長くなる。",
        "ult": t("{r_charge}秒") + "力を溜めて" + G + "シールド" + E + "（周囲の敵チャンピオン1体ごとに{r_sh_c}追加）を得て跳び上がり、周囲の敵を" +
               R + "打ち上げ" + E + "、着地で" + mag("r_dmg", "r_ratio") + "の魔法ダメージと" + t("{r_stun}秒") + R + "スタン" + E + "。",
        "names": ("弾ける花弁", "からまれ！", "ポップブロッサム"),
    },
}

C = "league_neeko_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {f"league_neeko_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.3), ("a_hit", 0.35), ("w", 0.35), ("w_hit", 0.4), ("q", 0.4), ("q_burst", 0.5), ("q_bloom", 0.45),
    ("q_hit", 0.3), ("e", 0.4), ("e_hit", 0.45), ("r", 0.45), ("r_sh", 0.35), ("r_jump", 0.45), ("r_land", 0.55),
    ("r_hit", 0.4), ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("w_dmg", "w_ratio", "w_ms", "q_dmg", "q_ratio", "q2_dmg", "q2_ratio", "e_dmg", "e_ratio",
                           "r_sh_c", "r_dmg", "r_ratio")}
    for k in ("w_ms_t", "e_root", "e_add", "r_charge", "r_stun"):
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
    if "Neeko" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Neeko. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
