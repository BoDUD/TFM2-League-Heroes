"""Lulu's text (5 languages), sound_info files and her keys in the shared files, numbers from build_lulu.P.

    python tools/kit/setup_lulu.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in lul/league): text/champion.i18n (league_lulu in every language, description + skill_name),
sound/sfx/league_lulu_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.79.0, Lulu named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/lul/lu_rst.py: 璐璐 / 仙灵女巫, 皮克斯，仙灵伙伴, 闪耀长枪, 奇思妙想,
帮忙，皮克斯！, 狂野生长) and Data Dragon 16.19.1 (zh_TW 露璐 / 皮克斯，守護妖精 / 閃耀雙重奏 / 幻想曲 / 帥啊小皮！ / 究極鍊化,
ko 룰루 / 요정 친구 픽스 / 반짝반짝 창 / 변덕쟁이 / 도와줘, 픽스! / 급성장, ja ルル / 仲良し妖精ピックス / ぴかぴかビーム / イタズラ /
ピックス、おねがい！ / おおきくなぁれ！). No `league_lulu_attack` sound: the engine would play it at the start of every
attack; the bolt sounds play from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_lulu import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_lulu"
VERSION = "0.79.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
S = "<#9fd8ffff>"      # shields
G = "<#7cfc00ff>"      # health
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
# 10-08 the sprite shrunk to 90% about the soles (stage_lu SHRINK): face 37 -> 33 px over the feet, centre 23 -> 21
VIEW = {"face": {"x": 2, "y": -22}, "center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def sh(d, r):
    return f"{S}{{{d}}}{E} + {APi}{S}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "璐璐",
        "attack": "射出魔弹。被动" + O + "皮克斯，仙灵伙伴" + E + "：皮克斯朝同一目标射出" + A + "{p_n}颗" + E + "飞弹，每颗造成" +
                  mag("p_dmg", "p_ap") + M + "魔法伤害" + E + "。",
        "skill": "璐璐和皮克斯各射出一道贯穿魔弹，直线上的敌人受到" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R +
                 "减速{q_slow}%" + E + "，" + A + "{q_t2}秒" + E + "内逐渐减弱。",
        "skill2": O + "奇思妙想" + E + "：把敌方英雄" + R + "变形{w_t}秒" + E + "（无法攻击和施法、减速），造成" + mag("e_dmg", "e_ap") +
                  M + "魔法伤害" + E + "；" + O + "帮忙，皮克斯！" + E + "：附近友方英雄获得" + sh("e_sh", "e_ap2") + S + "护盾" + E +
                  "和" + A + "{w_ms}%" + E + "移速、攻速（" + A + "{w_ht}秒" + E + "）。",
        "ult": "交战时让被控制或被敌人贴身的友方英雄（或自己）变大：" + G + "生命+{r_hp}" + E + "，周围敌人" + R + "击飞{r_up}秒" +
               E + "，" + A + "{r_t}秒" + E + "内身边敌人" + R + "减速{r_slow}%" + E + "。",
        "names": ("闪耀长枪", "奇思妙想", "狂野生长"),
    },
    "zh-hant": {
        "name": "露璐",
        "attack": "射出魔彈。被動" + O + "皮克斯，守護妖精" + E + "：皮克斯朝同一目標射出" + A + "{p_n}顆" + E + "飛彈，每顆造成" +
                  mag("p_dmg", "p_ap") + M + "魔法傷害" + E + "。",
        "skill": "露璐和皮克斯各射出一道貫穿魔彈，直線上的敵人受到" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R +
                 "緩速{q_slow}%" + E + "，" + A + "{q_t2}秒" + E + "內逐漸減弱。",
        "skill2": O + "幻想曲" + E + "：把敵方英雄" + R + "變形{w_t}秒" + E + "（無法攻擊和施法、緩速），造成" + mag("e_dmg", "e_ap") +
                  M + "魔法傷害" + E + "；" + O + "帥啊小皮！" + E + "：附近友方英雄獲得" + sh("e_sh", "e_ap2") + S + "護盾" + E +
                  "和" + A + "{w_ms}%" + E + "移速、攻速（" + A + "{w_ht}秒" + E + "）。",
        "ult": "交戰時讓被控制或被敵人貼身的友方英雄（或自己）變大：" + G + "生命+{r_hp}" + E + "，周圍敵人" + R + "擊飛{r_up}秒" +
               E + "，" + A + "{r_t}秒" + E + "內身邊敵人" + R + "緩速{r_slow}%" + E + "。",
        "names": ("閃耀雙重奏", "幻想曲", "究極鍊化"),
    },
    "en": {
        "name": "Lulu",
        "attack": "Fires a bolt. Passive " + O + "Pix, Faerie Companion" + E + ": Pix fires " + A + "{p_n} bolts" + E +
                  " at the same target, each dealing " + mag("p_dmg", "p_ap") + " " + M + "magic damage" + E + ".",
        "skill": "Lulu and Pix each fire a piercing bolt: enemies in the line take " + mag("q_dmg", "q_ap") + " " + M +
                 "magic damage" + E + " and are " + R + "slowed by {q_slow}%" + E + ", decaying over " + A + "{q_t2}s" + E + ".",
        "skill2": O + "Whimsy" + E + ": " + R + "polymorphs" + E + " an enemy champion for " + A + "{w_t}s" + E + " (no attacks "
                  "or spells, slowed) and deals " + mag("e_dmg", "e_ap") + " " + M + "magic damage" + E + "; " + O +
                  "Help, Pix!" + E + ": a nearby allied champion gets a " + sh("e_sh", "e_ap2") + " " + S + "shield" + E +
                  " and " + A + "{w_ms}%" + E + " move and attack speed for " + A + "{w_ht}s" + E + ".",
        "ult": "In a fight, an allied champion in crowd control or with enemies on him (or Lulu) grows: " + G +
               "+{r_hp} health" + E + ", nearby enemies are " + R + "knocked up for {r_up}s" + E + " and " + R +
               "slowed by {r_slow}%" + E + " around him for " + A + "{r_t}s" + E + ".",
        "names": ("Glitterlance", "Whimsy", "Wild Growth"),
    },
    "ko": {
        "name": "룰루",
        "attack": "마법탄을 쏩니다. 기본 지속 효과 " + O + "요정 친구 픽스" + E + ": 픽스가 같은 대상에게 " + A + "{p_n}발" + E +
                  "을 쏘아 한 발마다 " + mag("p_dmg", "p_ap") + "의 " + M + "마법 피해" + E + "를 입힙니다.",
        "skill": "룰루와 픽스가 관통하는 마법탄을 하나씩 쏩니다. 직선상의 적은 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" +
                 E + "를 입고 " + R + "{q_slow}% 둔화" + E + "되며, " + A + "{q_t2}초" + E + "에 걸쳐 약해집니다.",
        "skill2": O + "변덕쟁이" + E + ": 적 챔피언을 " + A + "{w_t}초" + E + " " + R + "변이" + E + "시키고(공격·스킬 불가, 둔화) " +
                  mag("e_dmg", "e_ap") + "의 " + M + "마법 피해" + E + "; " + O + "도와줘, 픽스!" + E + ": 근처 아군 챔피언에게 " +
                  sh("e_sh", "e_ap2") + "의 " + S + "보호막" + E + "과 " + A + "{w_ht}초" + E + " 동안 이동·공격 속도 " + A +
                  "{w_ms}%" + E + ".",
        "ult": "교전 중 군중 제어에 걸렸거나 적에게 붙잡힌 아군 챔피언(또는 룰루)을 키웁니다: " + G + "체력 +{r_hp}" + E +
               ", 주변 적 " + R + "{r_up}초 띄워 올림" + E + ", " + A + "{r_t}초" + E + " 동안 주변 적 " + R + "{r_slow}% 둔화" + E + ".",
        "names": ("반짝반짝 창", "변덕쟁이", "급성장"),
    },
    "ja": {
        "name": "ルル",
        "attack": "魔法弾を撃つ。パッシブ " + O + "仲良し妖精ピックス" + E + "：ピックスが同じ対象に" + A + "{p_n}発" + E +
                  "撃ち、1発ごとに" + mag("p_dmg", "p_ap") + "の" + M + "魔法ダメージ" + E + "。",
        "skill": "ルルとピックスが貫通弾を1発ずつ撃つ。直線上の敵に" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" +
                 R + "{q_slow}%スロウ" + E + "（" + A + "{q_t2}秒" + E + "で弱まる）。",
        "skill2": O + "イタズラ" + E + "：敵チャンピオンを" + A + "{w_t}秒" + E + R + "変身" + E + "させ（攻撃・スキル不可、スロウ）" +
                  mag("e_dmg", "e_ap") + "の" + M + "魔法ダメージ" + E + "。" + O + "ピックス、おねがい！" + E + "：近くの味方に" +
                  sh("e_sh", "e_ap2") + "の" + S + "シールド" + E + "と移動・攻撃速度" + A + "{w_ms}%" + E + "（" + A + "{w_ht}秒" +
                  E + "）。",
        "ult": "戦闘中、行動妨害中か敵に張り付かれた味方（またはルル）を巨大化：" + G + "体力+{r_hp}" + E + "、周囲の敵を" + R +
               "{r_up}秒ノックアップ" + E + "、" + A + "{r_t}秒" + E + "周囲の敵に" + R + "{r_slow}%スロウ" + E + "。",
        "names": ("ぴかぴかビーム", "イタズラ", "おおきくなぁれ！"),
    },
}

C = "league_lulu_sfx_"
V = "league_lulu_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_lulu_a_cast": [(C + "a", 0.4, 0.0), (C + "p", 0.3, 0.12)],
    "league_lulu_a_hit": [(C + "hit", 0.4, 0.0)],
    "league_lulu_q_cast": [(C + "q", 0.55, 0.0)],
    "league_lulu_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_lulu_w_cast": [(C + "w", 0.55, 0.0), (V + "w", 0.85, 0.05)],
    "league_lulu_w_hit": [(C + "w_hit", 0.6, 0.0)],
    "league_lulu_e_cast": [(C + "e", 0.5, 0.0)],
    "league_lulu_e_shield": [(C + "e_shield", 0.5, 0.0)],
    "league_lulu_r_cast": [(C + "r", 0.65, 0.0), (V + "r", 0.85, 0.05)],
    "league_lulu_r_grow": [(C + "r_grow", 0.65, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_n", "p_dmg", "p_ap", "q_dmg", "q_ap", "e_dmg", "e_ap", "e_sh", "e_ap2", "w_ms", "r_hp",
                           "r_slow")}
    v["q_slow"] = p["q_s1"] + p["q_s2"]
    v.update({k: secs(p[k]) for k in ("q_t2", "w_t", "w_ht", "r_up", "r_t")})
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
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top), when the top is above -28")
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
    for k in [k for k in ov if ID in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Lulu" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Lulu. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
