"""Braum's text (5 languages), sound_info files and his keys in the shared files, numbers from build_braum.P.

    python tools/kit/setup_braum.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_braum in every language, description + skill_name),
sound/sfx/league_braum_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.103.0, Braum named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (布隆 / 弗雷尔卓德之心; 震荡猛击, 寒冬之咬, 挺身而出, 坚不可摧, 冰川裂隙; the client swaps
name and title) and Data Dragon 16.20.1 (zh_TW 布郎姆 / 震盪冰封 / 凜冬衝擊 / 壁壘守護 / 雄心重盾 / 冰河裂隙, ja ブラウム /
漢の拳 / 冬の凍瘡 / ワシに任せとけ！ / 不破の盾 / 氷河の裂溝, ko 브라움 / 뇌진탕 펀치 / 동상 / 내가 지킨다 / 불굴 / 빙하 균열).
Slots: skill = Q, skill2 = E (W told in its text), ult = R; the passive is told in the attack's text. No combo sentence
in any text (the user's rule). No `league_braum_attack` sound: the engine would play it at the start of every attack;
the punch plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_braum import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_braum"
VERSION = "0.103.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7dd87dff>"      # heals
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 2, "y": -30}, "center": {"x": 0, "y": -12}}   # placeholder until the sprite


def mag(k, ap="ap"):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_{ap}}}%{E}"


PROC = M + "{p_dmg}" + E + " + " + APi + M + "{p_ap}%" + E
EXTRA = M + "{p_extra}" + E + " + " + APi + M + "{p_extra_ap}%" + E
SHIELD = "{e_sh} + " + APi + "{e_sh_ap}%"

TEXT = {
    "zh-hans": {
        "name": "布隆",
        "attack": O + "震荡猛击" + E + "：普攻和寒冬之咬命中英雄叠一层，第" + A + "4层" + E + R + "眩晕{p_stun}秒" + E + "并造成" + PROC + M + "魔法伤害" + E +
                  "；之后" + A + "{p_lock}秒" + E + "不再叠层，普攻额外造成" + EXTRA + M + "魔法伤害" + E + "。",
        "skill": "从盾中甩出寒冰，造成" + mag("q") + "+最大生命{q_hp}%" + M + "魔法伤害" + E + "，" + R + "减速{q_slow1}%" + E + "，" + A + "{q_slow_t}秒" + E +
                 "内渐弱到{q_slow2}%。",
        "skill2": "举盾" + A + "{e_t}秒" + E + "：受到伤害降低{e_red}%，获得" + SHIELD + "护盾，身边友方英雄伤害降低{e_ally_red}%。" + O + "挺身而出" + E +
                  "：冲到友方英雄身边，两人护甲和魔抗+{w_def}，持续" + A + "{w_t}秒" + E + "。",
        "ult": "猛砸地面，冰川裂隙冲向目标，造成" + mag("r") + M + "魔法伤害" + E + "并" + R + "击飞{r_up}秒" + E + "（第一个英雄{r_up1}秒），留下" + A +
               "{r_zone}秒" + E + "的裂隙，" + R + "减速{r_slow}%" + E + "。",
        "names": ("寒冬之咬", "坚不可摧", "冰川裂隙"),
    },
    "zh-hant": {
        "name": "布郎姆",
        "attack": O + "震盪冰封" + E + "：普攻和凜冬衝擊命中英雄疊一層，第" + A + "4層" + E + R + "暈眩{p_stun}秒" + E + "並造成" + PROC + M + "魔法傷害" + E +
                  "；之後" + A + "{p_lock}秒" + E + "不再疊層，普攻額外造成" + EXTRA + M + "魔法傷害" + E + "。",
        "skill": "從盾中甩出寒冰，造成" + mag("q") + "+最大生命{q_hp}%" + M + "魔法傷害" + E + "，" + R + "緩速{q_slow1}%" + E + "，" + A + "{q_slow_t}秒" + E +
                 "內漸弱到{q_slow2}%。",
        "skill2": "舉盾" + A + "{e_t}秒" + E + "：受到傷害降低{e_red}%，獲得" + SHIELD + "護盾，身邊友方英雄傷害降低{e_ally_red}%。" + O + "壁壘守護" + E +
                  "：衝到友方英雄身邊，兩人護甲和魔抗+{w_def}，持續" + A + "{w_t}秒" + E + "。",
        "ult": "猛砸地面，冰河裂隙衝向目標，造成" + mag("r") + M + "魔法傷害" + E + "並" + R + "擊飛{r_up}秒" + E + "（第一個英雄{r_up1}秒），留下" + A +
               "{r_zone}秒" + E + "的裂隙，" + R + "緩速{r_slow}%" + E + "。",
        "names": ("凜冬衝擊", "雄心重盾", "冰河裂隙"),
    },
    "en": {
        "name": "Braum",
        "attack": O + "Concussive Blows" + E + ": attacks and Winter's Bite stack on champions; the " + A + "4th" + E + " " + R + "stuns {p_stun}s" + E +
                  " and deals " + PROC + " " + M + "magic damage" + E + ", then for " + A + "{p_lock}s" + E + " no stacks and attacks deal " + EXTRA +
                  " " + M + "magic damage" + E + " more.",
        "skill": "Hurls ice from his shield: " + mag("q") + " + {q_hp}% max health " + M + "magic damage" + E + " and a " + R + "{q_slow1}% slow" + E +
                 " fading to {q_slow2}% over " + A + "{q_slow_t}s" + E + ".",
        "skill2": "Raises his shield for " + A + "{e_t}s" + E + ": {e_red}% less damage, a " + SHIELD + " shield, allied champions beside him {e_ally_red}% less. " +
                  O + "Stand Behind Me" + E + ": leaps to an allied champion; both gain {w_def} armour and magic resist for " + A + "{w_t}s" + E + ".",
        "ult": "Slams the ground: a fissure runs at the target, dealing " + mag("r") + " " + M + "magic damage" + E + " and " + R + "knocking up {r_up}s" + E +
               " (the first champion {r_up1}s); the fissure " + R + "slows {r_slow}%" + E + " for " + A + "{r_zone}s" + E + ".",
        "names": ("Winter's Bite", "Unbreakable", "Glacial Fissure"),
    },
    "ko": {
        "name": "브라움",
        "attack": O + "뇌진탕 펀치" + E + ": 기본 공격과 동상이 챔피언에 중첩, " + A + "4중첩" + E + "에 " + R + "{p_stun}초 기절" + E + "과 " + PROC + " " + M +
                  "마법 피해" + E + ", 이후 " + A + "{p_lock}초" + E + " 동안 중첩 없이 기본 공격에 " + EXTRA + " " + M + "마법 피해" + E + " 추가.",
        "skill": "방패에서 얼음을 날려 " + mag("q") + " + 최대 체력 {q_hp}% " + M + "마법 피해" + E + "와 " + R + "{q_slow1}% 둔화" + E + ", " + A + "{q_slow_t}초" +
                 E + "에 걸쳐 {q_slow2}%로 감소.",
        "skill2": A + "{e_t}초" + E + " 동안 방패를 들어 받는 피해 {e_red}% 감소, " + SHIELD + " 보호막, 곁의 아군 챔피언 피해 {e_ally_red}% 감소. " + O +
                  "내가 지킨다" + E + ": 아군 챔피언에게 도약, 둘 다 " + A + "{w_t}초" + E + " 동안 방어력과 마법 저항력 +{w_def}.",
        "ult": "땅을 내리쳐 대상 쪽으로 균열을 일으켜 " + mag("r") + " " + M + "마법 피해" + E + "와 " + R + "{r_up}초 에어본" + E + " (첫 챔피언 {r_up1}초), 균열은 " +
               A + "{r_zone}초" + E + " 동안 " + R + "{r_slow}% 둔화" + E + ".",
        "names": ("동상", "불굴", "빙하 균열"),
    },
    "ja": {
        "name": "ブラウム",
        "attack": O + "漢の拳" + E + "：通常攻撃と冬の凍瘡がチャンピオンにスタック、" + A + "4" + E + "で" + R + "{p_stun}秒スタン" + E + "と" + PROC + "の" + M +
                  "魔法ダメージ" + E + "、その後" + A + "{p_lock}秒" + E + "スタックせず通常攻撃に" + EXTRA + "の" + M + "魔法ダメージ" + E + "追加。",
        "skill": "盾から氷を放ち" + mag("q") + "+最大体力の{q_hp}%の" + M + "魔法ダメージ" + E + "と" + R + "{q_slow1}%スロウ" + E + "（" + A + "{q_slow_t}秒" + E +
                 "で{q_slow2}%まで減衰）。",
        "skill2": A + "{e_t}秒" + E + "盾を構え被ダメージ{e_red}%軽減、" + SHIELD + "のシールド、傍の味方チャンピオンも{e_ally_red}%軽減。" + O + "ワシに任せとけ！" + E +
                  "：味方チャンピオンへ跳び、両者の物防と魔防+{w_def}（" + A + "{w_t}秒" + E + "）。",
        "ult": "地面を叩き対象へ裂溝を走らせ" + mag("r") + "の" + M + "魔法ダメージ" + E + "と" + R + "{r_up}秒ノックアップ" + E + "（最初のチャンピオン{r_up1}秒）、裂溝は" +
               A + "{r_zone}秒" + E + R + "{r_slow}%スロウ" + E + "。",
        "names": ("冬の凍瘡", "不破の盾", "氷河の裂溝"),
    },
}

C = "league_braum_sfx_"
S_ = "league_braum_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.45, 0.0), ("p_proc", "p_proc", 0.6, 0.0),
    ("q", "q", 0.55, 0.0), ("q_hit", "q_hit", 0.55, 0.0), ("e", "e", 0.6, 0.0), ("w", "w", 0.55, 0.0),
    ("w_land", "w_land", 0.55, 0.0), ("r", "r", 0.6, 0.0), ("r_hit", "r_hit", 0.65, 0.0),
    ("vo_q", "vo_q", 0.8, 0.0), ("vo_w", "vo_w", 0.8, 0.0), ("vo_e", "vo_e", 0.8, 0.0), ("vo_r", "vo_r", 0.85, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "p_extra", "p_extra_ap", "q_dmg", "q_ap", "q_hp", "q_slow1", "q_slow2",
                           "e_red", "e_sh", "e_sh_ap", "e_ally_red", "w_def", "r_dmg", "r_ap", "r_slow")}
    v.update({k: secs(p[k]) for k in ("p_stun", "p_lock", "e_t", "w_t", "r_up", "r_up1", "r_zone")})
    v["q_slow_t"] = secs(p["q_slow1_t"] + p["q_slow2_t"])
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
    for k in [k for k in ov if ID in k]:      # his keys rebuilt (a renamed sound leaves none behind)
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
    if "Braum" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Braum. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
