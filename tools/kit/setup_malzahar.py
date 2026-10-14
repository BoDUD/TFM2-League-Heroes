"""Malzahar's text (5 languages), sound_info files and his keys in the shared files, numbers from build_malzahar.P.

    python tools/kit/setup_malzahar.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_malzahar in every language, description + skill_name),
sound/sfx/league_malzahar_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.111.0, Malzahar named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (玛尔扎哈 / 虚空先知; 虚空穿越, 虚空召唤, 虚空虫群, 煞星幻象, 冥府之握; the client swaps
name and title) and Data Dragon 16.20.1 (zh_TW 馬爾札哈 / 虛空象限 / 虛空召喚 / 召喚虛靈 / 煞星幻象 / 冥府之握, ja マルザハール /
ヴォイドシフト / ヴォイドコール / ヴォイドスワーム / 虚性侵蝕 / ネザーグラスプ, ko 말자하 / 공허 태세 / 공허의 부름 / 공허의 무리 /
재앙의 환상 / 황천의 손아귀).
Slots: skill = E + W (the voidlings ride the vision's target), skill2 = Q, ult = R; the passive (Void Shift) is told in
the attack's text. No combo sentence in any text (the user's rule). No `league_malzahar_attack` sound: the engine would
play it at the start of every attack; the attack plays its own from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_malzahar import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_malzahar"
VERSION = "0.111.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
G = "<#7cfc00ff>"      # heals
C = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face)
VIEW = {"face": {"x": 2, "y": -34}, "center": {"x": 0, "y": -14}}


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ap}}%{E}"


SH = A + "{p_sh}" + E + " + " + APi + A + "{p_ap}%" + E

TEXT = {
    "zh-hans": {
        "name": "玛尔扎哈",
        "attack": "射出虚空弹。被动" + O + "虚空穿越" + E + "：获得" + SH + "护盾，护盾存在时" + C + "免疫控制" + E + "；护盾被打破后" + A + "{p_cd}秒" + E + "重新获得。",
        "skill": O + "煞星幻象" + E + "：" + A + "{e_t}秒" + E + "内造成" + mag("e") + M + "魔法伤害" + E + "，目标死亡时跳到附近的敌人身上。" + O + "虚空虫群" + E +
                 "随之撕咬目标，每" + A + "{w_p}秒" + E + "造成" + mag("w") + M + "魔法伤害" + E + "。",
        "skill2": "在目标两侧打开虚空裂隙，裂隙合拢时对范围内的敌人造成" + mag("q") + M + "魔法伤害" + E + "并" + C + "沉默{q_sil}秒" + E + "。",
        "ult": "压制一名敌方英雄（优先煞星幻象的目标）：引导期间使其" + C + "眩晕" + E + "，" + A + "{r_t}秒" + E + "内造成" + mag("r") + M + "魔法伤害" + E +
               "，脚下留下持续伤害的虚空区域。玛尔扎哈被控制时引导中断。",
        "names": ("煞星幻象 / 虚空虫群", "虚空召唤", "冥府之握"),
    },
    "zh-hant": {
        "name": "馬爾札哈",
        "attack": "射出虛空彈。被動" + O + "虛空象限" + E + "：獲得" + SH + "護盾，護盾存在時" + C + "免疫控場" + E + "；護盾被打破後" + A + "{p_cd}秒" + E + "重新獲得。",
        "skill": O + "煞星幻象" + E + "：" + A + "{e_t}秒" + E + "內造成" + mag("e") + M + "魔法傷害" + E + "，目標死亡時跳到附近的敵人身上。" + O + "召喚虛靈" + E +
                 "隨之撕咬目標，每" + A + "{w_p}秒" + E + "造成" + mag("w") + M + "魔法傷害" + E + "。",
        "skill2": "在目標兩側打開虛空裂隙，裂隙合攏時對範圍內的敵人造成" + mag("q") + M + "魔法傷害" + E + "並" + C + "沉默{q_sil}秒" + E + "。",
        "ult": "壓制一名敵方英雄（優先煞星幻象的目標）：引導期間使其" + C + "暈眩" + E + "，" + A + "{r_t}秒" + E + "內造成" + mag("r") + M + "魔法傷害" + E +
               "，腳下留下持續傷害的虛空區域。馬爾札哈被控場時引導中斷。",
        "names": ("煞星幻象 / 召喚虛靈", "虛空召喚", "冥府之握"),
    },
    "en": {
        "name": "Malzahar",
        "attack": "Fires a void bolt. Passive " + O + "Void Shift" + E + ": a " + SH + " shield; while it holds he is " + C + "immune to crowd control" + E +
                  ". Broken, it returns after " + A + "{p_cd}s" + E + ".",
        "skill": O + "Malefic Visions" + E + ": deals " + mag("e") + " " + M + "magic damage" + E + " over " + A + "{e_t}s" + E +
                 "; if the target dies, the vision jumps to a nearby enemy. " + O + "Void Swarm" + E + ": voidlings bite the target, " + mag("w") + " " + M +
                 "magic damage" + E + " every " + A + "{w_p}s" + E + ".",
        "skill2": "Opens two void rifts beside the target; as they close, enemies in the area take " + mag("q") + " " + M + "magic damage" + E + " and are " + C +
                  "silenced for {q_sil}s" + E + ".",
        "ult": "Suppresses an enemy champion (the vision's target first): " + C + "stunned" + E + " while he channels, it takes " + mag("r") + " " + M +
               "magic damage" + E + " over " + A + "{r_t}s" + E + " and leaves a damaging void zone. Crowd control on Malzahar ends the channel.",
        "names": ("Malefic Visions / Void Swarm", "Call of the Void", "Nether Grasp"),
    },
    "ko": {
        "name": "말자하",
        "attack": "공허의 화살을 쏩니다. 기본 지속 효과 " + O + "공허 태세" + E + ": " + SH + " 보호막, 유지되는 동안 " + C + "군중 제어 면역" + E + ". 깨지면 " + A + "{p_cd}초" +
                  E + " 후 다시 생깁니다.",
        "skill": O + "재앙의 환상" + E + ": " + A + "{e_t}초" + E + "에 걸쳐 " + mag("e") + " " + M + "마법 피해" + E + ", 대상이 죽으면 근처 적에게 옮겨갑니다. " + O +
                 "공허의 무리" + E + ": 공허충이 대상을 물어 " + A + "{w_p}초" + E + "마다 " + mag("w") + " " + M + "마법 피해" + E + ".",
        "skill2": "대상 양옆에 공허의 균열을 열고, 닫힐 때 범위 안 적에게 " + mag("q") + " " + M + "마법 피해" + E + "와 " + C + "{q_sil}초 침묵" + E + ".",
        "ult": "적 챔피언 하나를 제압합니다(재앙의 환상 대상 우선): 정신 집중 동안 " + C + "기절" + E + ", " + A + "{r_t}초" + E + "에 걸쳐 " + mag("r") + " " + M +
               "마법 피해" + E + ", 발밑에 공허 지대를 남깁니다. 말자하가 군중 제어되면 끊깁니다.",
        "names": ("재앙의 환상 / 공허의 무리", "공허의 부름", "황천의 손아귀"),
    },
    "ja": {
        "name": "マルザハール",
        "attack": "ヴォイドの弾を放つ。自動効果" + O + "ヴォイドシフト" + E + "：" + SH + "のシールド、ある間は" + C + "行動妨害無効" + E + "。破られると" + A + "{p_cd}秒" +
                  E + "後に再び得る。",
        "skill": O + "虚性侵蝕" + E + "：" + A + "{e_t}秒" + E + "かけて" + mag("e") + "の" + M + "魔法ダメージ" + E + "、対象が倒れると近くの敵に移る。" + O +
                 "ヴォイドスワーム" + E + "：ヴォイドリングが対象に噛みつき" + A + "{w_p}秒" + E + "ごとに" + mag("w") + "の" + M + "魔法ダメージ" + E + "。",
        "skill2": "対象の両側にヴォイドの裂け目を開き、閉じる時に範囲内の敵に" + mag("q") + "の" + M + "魔法ダメージ" + E + "と" + C + "{q_sil}秒サイレンス" + E + "。",
        "ult": "敵チャンピオン1体をサプレッション（虚性侵蝕の対象を優先）：詠唱中" + C + "スタン" + E + "、" + A + "{r_t}秒" + E + "かけて" + mag("r") + "の" + M +
               "魔法ダメージ" + E + "、足元にヴォイドの領域を残す。行動妨害で中断。",
        "names": ("虚性侵蝕 / ヴォイドスワーム", "ヴォイドコール", "ネザーグラスプ"),
    },
}


S_ = "league_malzahar_"
CL = "league_malzahar_sfx_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(CL + k, vol, 0.0)] for k, vol in [
    ("a_cast", 0.4), ("a_hit", 0.4), ("p_shift", 0.45), ("e_cast", 0.5), ("e_hit", 0.45), ("e_jump", 0.45),
    ("w_spawn", 0.45), ("w_bite", 0.3), ("q_cast", 0.5), ("q_close", 0.55), ("q_hit", 0.5), ("r_cast", 0.6),
    ("r_tick", 0.3), ("r_pool", 0.5), ("vo_q", 0.7), ("vo_e", 0.7), ("vo_r", 0.75)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_sh", "p_ap", "e_dmg", "e_ap", "w_dmg", "w_ap", "q_dmg", "q_ap", "r_dmg", "r_ap")}
    v.update({k: secs(p[k]) for k in ("p_cd", "e_t", "w_p", "q_sil", "r_t")})
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
    if "Malzahar" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Malzahar. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
