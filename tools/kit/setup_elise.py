"""Elise's text (5 languages), sound_info files and her keys in the shared files, numbers from build_elise.P.

    python tools/kit/setup_elise.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_elise in every language, description + skill_name),
sound/sfx/league_elise_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.115.0, Elise named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 伊莉丝 / 蜘蛛女皇 - the client swaps name and title; 蜘蛛女皇, 神经毒素 / 剧毒之蜇, 自爆蜘蛛 /
掠行狂暴, 结茧 / 盘丝, 蜘蛛形态; zh_TW 伊莉絲 / 蜘蛛女王, 神經毒素／毒咬, 爆裂毒蛛／掠食者的狂喜, 盤纏蛛絲／韌絲飛躍, 蜘蛛型態;
ja エリス / 蜘蛛の女帝, 神経毒/毒牙, 子蜘蛛爆弾/猛食, 繭化/蜘蛛の糸, 蜘蛛形態; ko 엘리스 / 거미 여왕, 신경독 / 독이빨, 위험한 새끼 거미 /
광란의 질주, 고치 / 줄타기, 거미 형태).
Slots: skill = Q (both forms), skill2 = E + W (both forms), ult = the cocoon hunt (R's name); the passive and the form
switch are told in the attack's text. No combo sentence in any text (the user's rule). No `league_elise_attack` sound:
the engine would play it at the start of every attack; the spit plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_elise import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_elise"
VERSION = "0.115.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts, shares
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
# 2026-10-18 ban/pick card audit (frame centre, HD from lo_idle / 1.5; user: 「还有哪些英雄BP位置不对的一起改了」): -3 -> -2: 1 px of the top cut
VIEW = {"face": {"x": 3, "y": -36}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -2}}   # placeholder until the sprite is in


def mag(k):
    return f"{M}{{{k}_dmg}}{E}+{APi}{M}{{{k}_ap}}%{E}"


def HP(k):
    return A + "{" + k + "_hp}%" + E


TEXT = {
    "zh-hans": {
        "name": "伊莉丝",
        "attack": O + "蜘蛛女皇" + E + "：人形技能命中积攒小蜘蛛（最多3只）。出手前按战况切换人形（远程）和蜘蛛（近战），冷却" + A + "{r_cd}秒" + E +
                  "。蜘蛛普攻额外造成" + mag("c") + M + "魔法伤害" + E + "并回血，每只小蜘蛛撕咬" + mag("sl") + "。",
        "skill": "人形：射出毒液造成" + mag("q") + M + "魔法伤害" + E + "和" + HP("q") + "最大生命真实伤害。" + O + "剧毒之蜇" + E + "：扑向敌人造成" +
                 mag("cq") + M + "魔法伤害" + E + "和" + HP("cq") + "最大生命真实伤害。",
        "skill2": "人形：吐茧造成" + mag("e") + M + "魔法伤害" + E + "并晕眩" + A + "{e_stun}秒" + E + "；冷却时放" + O + "自爆蜘蛛" + E + "，" + mag("w") +
                  M + "魔法伤害" + E + "。" + O + "盘丝" + E + "：升空不可选中，落到英雄身上；冷却时" + O + "掠行狂暴" + E + "，攻速+{cw_as}%。",
        "ult": "向英雄吐茧，立即化身蜘蛛并重置蜘蛛技能，盘丝落到其身上造成" + mag("r") + M + "魔法伤害" + E + "，再施放剧毒之蜇。",
        "names": ("神经毒素 / 剧毒之蜇", "结茧 / 盘丝", "蜘蛛形态"),
    },
    "zh-hant": {
        "name": "伊莉絲",
        "attack": O + "蜘蛛女王" + E + "：人形技能命中累積小蜘蛛（最多3隻）。出手前依戰況切換人形（遠程）和蜘蛛（近戰），冷卻" + A + "{r_cd}秒" + E +
                  "。蜘蛛普攻額外造成" + mag("c") + M + "魔法傷害" + E + "並回血，每隻小蜘蛛撕咬" + mag("sl") + "。",
        "skill": "人形：射出毒液造成" + mag("q") + M + "魔法傷害" + E + "和" + HP("q") + "最大生命真實傷害。" + O + "毒咬" + E + "：撲向敵人造成" +
                 mag("cq") + M + "魔法傷害" + E + "和" + HP("cq") + "最大生命真實傷害。",
        "skill2": "人形：吐繭造成" + mag("e") + M + "魔法傷害" + E + "並暈眩" + A + "{e_stun}秒" + E + "；冷卻時放" + O + "爆裂毒蛛" + E + "，" + mag("w") +
                  M + "魔法傷害" + E + "。" + O + "韌絲飛躍" + E + "：升空無法選取，落到英雄身上；冷卻時" + O + "掠食者的狂喜" + E + "，攻速+{cw_as}%。",
        "ult": "向英雄吐繭，立即化身蜘蛛並重置蜘蛛技能，韌絲飛躍落到其身上造成" + mag("r") + M + "魔法傷害" + E + "，再施放毒咬。",
        "names": ("神經毒素／毒咬", "盤纏蛛絲／韌絲飛躍", "蜘蛛型態"),
    },
    "en": {
        "name": "Elise",
        "attack": O + "Spider Queen" + E + ": human ability hits gather spiderlings (up to 3). Before each attack she switches between human "
                  "(ranged) and spider (melee) as the fight needs, every " + A + "{r_cd}s" + E + " at most. Spider attacks deal " + mag("c") +
                  " " + M + "magic damage" + E + " more and heal her; each spiderling bites for " + mag("sl") + ".",
        "skill": "Human: a venom bolt for " + mag("q") + " " + M + "magic damage" + E + " and " + HP("q") + " max health true damage. " + O +
                 "Venomous Bite" + E + ": lunges for " + mag("cq") + " " + M + "magic damage" + E + " and " + HP("cq") +
                 " max health true damage.",
        "skill2": "Human: a cocoon for " + mag("e") + " " + M + "magic damage" + E + " that stuns " + A + "{e_stun}s" + E + "; on cooldown a " + O +
                  "Volatile Spiderling" + E + " for " + mag("w") + ". " + O + "Rappel" + E + ": rises out of reach and drops on a champion; "
                  "on cooldown " + O + "Skittering Frenzy" + E + ", +{cw_as}% attack speed.",
        "ult": "Spits a cocoon at a champion, turns into the spider at once with her spider abilities reset, rappels onto it for " +
               mag("r") + " " + M + "magic damage" + E + " and bites.",
        "names": ("Neurotoxin / Venomous Bite", "Cocoon / Rappel", "Spider Form"),
    },
    "ko": {
        "name": "엘리스",
        "attack": O + "거미 여왕" + E + ": 인간 스킬 적중 시 새끼 거미 축적 (최대 3). 공격 전에 상황에 따라 인간(원거리)과 거미(근접) 형태를 바꾸며, 전환 대기시간 " +
                  A + "{r_cd}초" + E + ". 거미 공격은 " + mag("c") + " " + M + "마법 피해" + E + " 추가와 회복, 새끼 거미마다 " + mag("sl") + ".",
        "skill": "인간: 독을 쏘아 " + mag("q") + " " + M + "마법 피해" + E + "와 최대 체력 " + HP("q") + " 고정 피해. " + O + "독이빨" + E + ": 달려들어 " +
                 mag("cq") + " " + M + "마법 피해" + E + "와 최대 체력 " + HP("cq") + " 고정 피해.",
        "skill2": "인간: 고치로 " + mag("e") + " " + M + "마법 피해" + E + "와 " + A + "{e_stun}초" + E + " 기절; 대기 중이면 " + O + "위험한 새끼 거미" + E +
                  " " + mag("w") + ". " + O + "줄타기" + E + ": 대상 지정 불가로 올라가 챔피언에게 내려옴; 대기 중이면 " + O + "광란의 질주" + E +
                  ", 공격 속도 +{cw_as}%.",
        "ult": "챔피언에게 고치를 뱉고 즉시 거미로 변해 거미 스킬을 초기화, 줄타기로 내려와 " + mag("r") + " " + M + "마법 피해" + E + " 후 독이빨.",
        "names": ("신경독 / 독이빨", "고치 / 줄타기", "거미 형태"),
    },
    "ja": {
        "name": "エリス",
        "attack": O + "蜘蛛の女帝" + E + "：人間のスキル命中で子蜘蛛を蓄積（最大3）。攻撃の前に戦況で人間（遠隔）と蜘蛛（近接）を切り替え、間隔" + A +
                  "{r_cd}秒" + E + "。蜘蛛の通常攻撃は" + mag("c") + "の" + M + "魔法ダメージ" + E + "追加と回復、子蜘蛛ごとに" + mag("sl") + "。",
        "skill": "人間：毒を放ち" + mag("q") + "の" + M + "魔法ダメージ" + E + "と最大体力" + HP("q") + "の確定ダメージ。" + O + "毒牙" + E + "：飛びかかり" +
                 mag("cq") + "の" + M + "魔法ダメージ" + E + "と最大体力" + HP("cq") + "の確定ダメージ。",
        "skill2": "人間：繭で" + mag("e") + "の" + M + "魔法ダメージ" + E + "、" + A + "{e_stun}秒" + E + "スタン；クールダウン中は" + O + "子蜘蛛爆弾" + E +
                  "で" + mag("w") + "。" + O + "蜘蛛の糸" + E + "：対象不可で上昇しチャンピオンへ降下；クールダウン中は" + O + "猛食" + E +
                  "、攻撃速度+{cw_as}%。",
        "ult": "チャンピオンへ繭を吐き、即座に蜘蛛に変身して蜘蛛のスキルをリセット、蜘蛛の糸で降下し" + mag("r") + "の" + M + "魔法ダメージ" + E +
               "、毒牙を放つ。",
        "names": ("神経毒/毒牙", "繭化/蜘蛛の糸", "蜘蛛形態"),
    },
}

C = "league_elise_sfx_"
S_ = "league_elise_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + k, vol, 0.0)] for k, vol in [
    ("a_spit", 0.45), ("a_hit", 0.45), ("c_swing", 0.45), ("c_hit", 0.45), ("sl_bite", 0.4), ("q", 0.55),
    ("q_hit", 0.55), ("w", 0.5), ("w_boom", 0.55), ("e", 0.55), ("e_hit", 0.55), ("cq", 0.5), ("cq_hit", 0.55),
    ("cw", 0.5), ("ce", 0.5), ("ce_hit", 0.5), ("ce_land", 0.55), ("r", 0.6), ("tf_spider", 0.55), ("tf_human", 0.55),
    ("vo_q", 0.8), ("vo_w", 0.8), ("vo_e", 0.8), ("vo_human", 0.8), ("vo_spider", 0.8), ("vo_cq", 0.75),
    ("vo_cw", 0.75), ("vo_ce", 0.75), ("vo_r", 0.85)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("c_dmg", "c_ap", "sl_dmg", "sl_ap", "q_dmg", "q_ap", "q_hp", "cq_dmg", "cq_ap", "cq_hp", "e_dmg",
                           "e_ap", "w_dmg", "w_ap", "cw_as", "r_dmg", "r_ap")}
    v["e_stun"] = secs(p["e_stun"])
    v["r_cd"] = secs(p["r_cd_t"])
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
    if "Elise" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Elise. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
