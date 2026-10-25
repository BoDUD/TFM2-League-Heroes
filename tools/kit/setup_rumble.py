"""Rumble's text (5 languages), sound_info files and their keys in the shared files, numbers from build_rumble.P
(setup_yorick.py's way).

    python tools/kit/setup_rumble.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_rumble in every language, description + skill_name),
sound/sfx/league_rumble_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Rumble named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 兰博 (机械公敌): 机械重组; 纵火盛宴, 破碎护盾, 电子鱼叉, 恒温灼烧 (热量, 危险温度, 过热);
zh_TW 藍寶: 泰坦熱能; 火焰噴射器, 鐵屑電磁盾, 高壓電魚叉, 等離子飛彈 (熱能, 危險禁區, 系統過熱); ja ランブル: ポンコツタイタン;
スピットファイア, ジャンクシールド, エレクトロハープーン, イコライザー (ヒート, デンジャーゾーン, オーバーヒート); ko 럼블:
고철장 거인; 화염방사기, 고철 방패, 전기 작살, 이퀄라이저 미사일 (열기, 위험 상태, 과열).
Slots: skill = Flamespitter, skill2 = Electro Harpoon, ult = The Equalizer; the heat (Junkyard Titan: the Danger Zone,
Overheat) and Scrap Shield (cast by itself) in the attack's text. No combo sentence in any text (the user's rule: the
combos are the README's).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_rumble import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_rumble"
VERSION = "0.221.0"     # above main 0.220.0 (Ambessa #527), 2026-10-25
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
M = "<#a974ffff>"      # magic damage / AP
R = "<#ef5350ff>"      # crowd control
G = "<#7ee0ffff>"      # shields
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py)
VIEW = {"face": {"x": 4, "y": -26}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


def sh(x):
    return G + x + E


TEXT = {
    "zh-hans": {
        "name": "兰博",
        "attack": "抡铁球。" + n("机械重组") + "：放技能攒热量，过半进入" + n("危险温度") + "（技能效果+{dz_pct}%），满了" +
                  n("过热") + t("{oh_t}秒") + "：不能放技能，攻速+{oh_as}%，普攻附加" + mag("oh_dmg", "oh_ap") +
                  "魔法伤害（英雄再加最大生命{oh_thp}%）。" + n("破碎护盾") + "：敌方英雄靠近时自动套上" + sh("{w_sh}") + "+" + APi +
                  sh("{w_ap}%") + "护盾" + t("{w_sh_t}秒") + "。",
        "skill": "端起喷火炮往前喷火" + t("{q_t}秒") + "：锥形范围内的敌人每" + t("{q_gap}秒") + "受到" + mag("q_dmg", "q_ap") +
                 "魔法伤害。",
        "skill2": "射出电子鱼叉：" + mag("e_dmg", "e_ap") + "魔法伤害，" + cc("减速") + "{e_slow}%" + t("{e_slow_t}秒") +
                  "；射中英雄后再射第二发，伤害+{e2_pct}%，减速{e2_slow}%。",
        "ult": "火箭在敌方英雄脚下砸出一条火线（横着或竖着，挑罩住敌人多的一边），燃烧" + t("{r_t}秒") + "：每" + t("{r_p}秒") +
               mag("r_dmg", "r_ap") + "魔法伤害，" + cc("减速") + "{r_slow}%。",
        "names": ("纵火盛宴", "电子鱼叉", "恒温灼烧"),
    },
    "zh-hant": {
        "name": "藍寶",
        "attack": "揮鐵球。" + n("泰坦熱能") + "：放技能累積熱能，過半進入" + n("危險禁區") + "（技能效果+{dz_pct}%），滿了" +
                  n("系統過熱") + t("{oh_t}秒") + "：無法施放技能，攻速+{oh_as}%，普攻附加" + mag("oh_dmg", "oh_ap") +
                  "魔法傷害（英雄再加最大生命{oh_thp}%）。" + n("鐵屑電磁盾") + "：敵方英雄靠近時自動套上" + sh("{w_sh}") + "+" + APi +
                  sh("{w_ap}%") + "護盾" + t("{w_sh_t}秒") + "。",
        "skill": "端起噴火炮往前噴火" + t("{q_t}秒") + "：錐形範圍內的敵人每" + t("{q_gap}秒") + "受到" + mag("q_dmg", "q_ap") +
                 "魔法傷害。",
        "skill2": "射出高壓電魚叉：" + mag("e_dmg", "e_ap") + "魔法傷害，" + cc("緩速") + "{e_slow}%" + t("{e_slow_t}秒") +
                  "；射中英雄後再射第二發，傷害+{e2_pct}%，緩速{e2_slow}%。",
        "ult": "飛彈在敵方英雄腳下砸出一條火線（橫著或豎著，挑罩住敵人多的一邊），燃燒" + t("{r_t}秒") + "：每" + t("{r_p}秒") +
               mag("r_dmg", "r_ap") + "魔法傷害，" + cc("緩速") + "{r_slow}%。",
        "names": ("火焰噴射器", "高壓電魚叉", "等離子飛彈"),
    },
    "en": {
        "name": "Rumble",
        "attack": "Mace blows. " + n("Junkyard Titan") + ": abilities build heat; past half, the " + n("Danger Zone") +
                  " (abilities +{dz_pct}%); full, he " + n("Overheats") + " for " + t("{oh_t}s") + ": no abilities, "
                  "+{oh_as}% attack speed, attacks deal " + mag("oh_dmg", "oh_ap") + " magic damage more (+{oh_thp}% max "
                  "health on champions). " + n("Scrap Shield") + ": an enemy champion near raises a " + sh("{w_sh}") +
                  " + " + APi + sh("{w_ap}%") + " shield for " + t("{w_sh_t}s") + " by itself.",
        "skill": "Sprays fire ahead for " + t("{q_t}s") + ": enemies in the cone take " + mag("q_dmg", "q_ap") +
                 " magic damage every " + t("{q_gap}s") + ".",
        "skill2": "Fires a harpoon: " + mag("e_dmg", "e_ap") + " magic damage and " + cc("slows") + " {e_slow}% for " +
                  t("{e_slow_t}s") + "; through a champion it fires a second one, +{e2_pct}% damage, {e2_slow}% slow.",
        "ult": "His rockets come down in a burning line on an enemy champion (across or up and down, whichever covers more "
               "enemies), burning for " + t("{r_t}s") + ": " + mag("r_dmg", "r_ap") + " magic damage every " +
               t("{r_p}s") + " and a {r_slow}% " + cc("slow") + ".",
        "names": ("Flamespitter", "Electro Harpoon", "The Equalizer"),
    },
    "ko": {
        "name": "럼블",
        "attack": "철퇴 공격. " + n("고철장 거인") + ": 스킬로 열기 축적, 절반을 넘으면 " + n("위험 상태") + "(스킬 효과 +{dz_pct}%), "
                  "가득 차면 " + t("{oh_t}초") + " " + n("과열") + ": 스킬 사용 불가, 공격 속도 +{oh_as}%, 기본 공격에 " +
                  mag("oh_dmg", "oh_ap") + " 마법 피해 추가(챔피언은 최대 체력 {oh_thp}%). " + n("고철 방패") +
                  ": 적 챔피언이 가까우면 " + sh("{w_sh}") + " + " + APi + sh("{w_ap}%") + " 보호막 " + t("{w_sh_t}초") + " 자동.",
        "skill": "화염방사기로 " + t("{q_t}초") + " 동안 전방에 불을 뿜음: 부채꼴 안의 적에게 " + t("{q_gap}초") + "마다 " +
                 mag("q_dmg", "q_ap") + " 마법 피해.",
        "skill2": "작살 발사: " + mag("e_dmg", "e_ap") + " 마법 피해, " + t("{e_slow_t}초") + " 동안 {e_slow}% " + cc("둔화") +
                  "; 챔피언에 맞으면 두 번째 작살, 피해 +{e2_pct}%, 둔화 {e2_slow}%.",
        "ult": "적 챔피언 발밑에 로켓이 불길 한 줄을 만듦(가로 또는 세로, 적이 더 많은 쪽), " + t("{r_t}초") + " 동안 " +
               t("{r_p}초") + "마다 " + mag("r_dmg", "r_ap") + " 마법 피해, {r_slow}% " + cc("둔화") + ".",
        "names": ("화염방사기", "전기 작살", "이퀄라이저 미사일"),
    },
    "ja": {
        "name": "ランブル",
        "attack": "鉄球攻撃。" + n("ポンコツタイタン") + "：スキルでヒート上昇、半分で" + n("デンジャーゾーン") +
                  "（効果+{dz_pct}%）、満タンで" + n("オーバーヒート") + t("{oh_t}秒") + "：スキル不可、攻撃速度+{oh_as}%、"
                  "攻撃に" + mag("oh_dmg", "oh_ap") + "（対チャンピオン+最大体力{oh_thp}%）。" + n("ジャンクシールド") +
                  "：敵チャンピオン接近で" + sh("{w_sh}") + "+" + APi + sh("{w_ap}%") + "シールド" + t("{w_sh_t}秒") + "。",
        "skill": "火炎放射器で" + t("{q_t}秒") + "前方に火を噴く：扇形内の敵に" + t("{q_gap}秒") + "毎" + mag("q_dmg", "q_ap") +
                 "の魔法ダメージ。",
        "skill2": "銛を発射：" + mag("e_dmg", "e_ap") + "の魔法ダメージ、" + t("{e_slow_t}秒") + "{e_slow}%" + cc("スロウ") +
                  "；チャンピオンに当たると2発目、ダメージ+{e2_pct}%、スロウ{e2_slow}%。",
        "ult": "敵チャンピオンの足元にロケットで炎の列（横か縦、敵の多い方）、" + t("{r_t}秒") + "燃えて" + t("{r_p}秒") + "毎" +
               mag("r_dmg", "r_ap") + "の魔法ダメージ、{r_slow}%" + cc("スロウ") + "。",
        "names": ("スピットファイア", "エレクトロハープーン", "イコライザー"),
    },
}

C = "league_rumble_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the impacts loud, the voice as the other heroes'
SOUNDS = {f"league_rumble_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.5), ("oh_hit", 0.55), ("q", 0.6), ("q_hit", 0.35), ("e", 0.6), ("e2", 0.65),
    ("e_hit", 0.55), ("w", 0.6), ("dz", 0.6), ("oh", 0.75), ("r", 0.8), ("r_fall", 0.75), ("r_hit", 0.4),
    ("vo_q", 0.85), ("vo_e", 0.85), ("vo_w", 0.85), ("vo_oh", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("oh_as", "oh_dmg", "oh_ap", "oh_thp", "w_sh", "w_ap", "q_dmg", "q_ap", "e_dmg", "e_ap",
                           "e_slow", "e2_slow", "r_dmg", "r_ap", "r_slow")}
    v["dz_pct"] = p["dz_k"] - 100
    v["e2_pct"] = p["e2_k"] - 100
    for k in ("oh_t", "w_sh_t", "q_t", "q_gap", "e_slow_t", "r_t", "r_p"):
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
    if "Rumble" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Rumble. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
