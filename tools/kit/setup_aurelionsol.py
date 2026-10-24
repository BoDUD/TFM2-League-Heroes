"""Aurelion Sol's text (5 languages), sound_info files and their keys in the shared files, numbers from
build_aurelionsol.P (setup_taliyah.py's way).

    python tools/kit/setup_aurelionsol.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_aurelionsol in every language, description + skill_name),
sound/sfx/league_aurelionsol_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Aurelion Sol named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 奥瑞利安·索尔 (铸星龙王): 星海焕然, 星穹流丽; 星河冲荡, 星芒凝汇, 星天落瀑 (星落 / 天瀑);
zh_TW 翱銳龍獸: 宇宙創世, 星界翱翔; 星光吐息, 宇宙奇點, 降世星辰／天界殞落; ja オレリオン・ソル: 宇宙の創造者, 天空への飛翔;
星炎の息吹, 特異点, 星の邂逅／崩れ落つ天穹; ko 아우렐리온 솔: 우주의 창조자, 별의 비행; 빛의 숨결, 특이점, 유성 / 천상 강림.
Slots: skill = Breath of Light, skill2 = Singularity, ult = Falling Star / The Skies Descend; Cosmic Creator (stardust)
and Astral Flight (the flight after a takedown) in the attack's text. No combo sentence in any text (the user's rule:
the combos are the README's).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_aurelionsol import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_aurelionsol"
VERSION = "0.208.0"     # the next free number above main 0.207.0 (Taliyah #503, 2026-10-24)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 5, "y": -35}, "center": {"x": 0, "y": -20}, "banpick_center": {"x": 0, "y": -3}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


TEXT = {
    "zh-hans": {
        "name": "奥瑞利安·索尔",
        "attack": "甩出一颗星星。" + n("星海焕然") + "：技能命中英雄收集星尘（每层法强+{d_ap}%，最多{d_max}层），每{sky_n}层"
                  "下一次大招变为天瀑。" + n("星穹流丽") + "：击杀英雄后起飞" + t("{w_t}秒") + "，移速+{w_ms}%、法强+{w_ap}%。",
        "skill": "引导龙息" + t("{q_t}秒") + "，每" + t("{q_p}秒") + "对一线上的敌人造成" + mag("q_dmg", "q_ratio") +
                 "魔法伤害，喷同一目标" + t("1秒") + "后每次额外{q_sec_dmg}；被控制打断。飞行中无冷却、引导更久。",
        "skill2": "在目标处召唤黑洞（" + t("{e_t}秒") + "），每" + t("{e_p}秒") + "造成" + mag("e_dmg", "e_ratio") +
                  "魔法伤害，把敌人拉向中心并" + cc("减速") + "{e_slow}%；中心每秒造成英雄最大生命值{e_exec}%的真实伤害。",
        "ult": n("星落") + "：星星坠落在目标处，造成" + mag("r_dmg", "r_ratio") + "魔法伤害并" + cc("眩晕") + t("{r_stun}秒") +
               "。" + n("天瀑") + "：范围更大，" + mag("r_dmg2", "r_ratio2") + "并" + cc("击飞") + t("{r_up}秒") +
               "，外圈冲击波再造成" + mag("r_wdmg", "r_wratio") + "并" + cc("减速") + "{r_wslow}%。",
        "names": ("星河冲荡", "星芒凝汇", "星天落瀑"),
    },
    "zh-hant": {
        "name": "翱銳龍獸",
        "attack": "甩出一顆星星。" + n("宇宙創世") + "：技能命中英雄收集星塵（每層魔攻+{d_ap}%，最多{d_max}層），每{sky_n}層"
                  "下一次大絕變為天界殞落。" + n("星界翱翔") + "：擊殺英雄後起飛" + t("{w_t}秒") + "，移速+{w_ms}%、魔攻+{w_ap}%。",
        "skill": "引導吐息" + t("{q_t}秒") + "，每" + t("{q_p}秒") + "對一線上的敵人造成" + mag("q_dmg", "q_ratio") +
                 "魔法傷害，噴同一目標" + t("1秒") + "後每次額外{q_sec_dmg}；被控制打斷。飛行中無冷卻、引導更久。",
        "skill2": "在目標處召喚奇點（" + t("{e_t}秒") + "），每" + t("{e_p}秒") + "造成" + mag("e_dmg", "e_ratio") +
                  "魔法傷害，把敵人拉向中心並" + cc("緩速") + "{e_slow}%；中心每秒造成英雄最大生命{e_exec}%的真實傷害。",
        "ult": n("降世星辰") + "：星辰墜落在目標處，造成" + mag("r_dmg", "r_ratio") + "魔法傷害並" + cc("暈眩") +
               t("{r_stun}秒") + "。" + n("天界殞落") + "：範圍更大，" + mag("r_dmg2", "r_ratio2") + "並" + cc("擊飛") +
               t("{r_up}秒") + "，外圈衝擊波再造成" + mag("r_wdmg", "r_wratio") + "並" + cc("緩速") + "{r_wslow}%。",
        "names": ("星光吐息", "宇宙奇點", "降世星辰"),
    },
    "en": {
        "name": "Aurelion Sol",
        "attack": "Flings a star. " + n("Cosmic Creator") + ": his spells hitting champions gather Stardust (+{d_ap}% ability "
                  "power a stack, {d_max} at most); every {sky_n} make his next ult The Skies Descend. " +
                  n("Astral Flight") + ": after a takedown he flies for " + t("{w_t}s") + ", +{w_ms}% move speed and "
                  "+{w_ap}% ability power.",
        "skill": "Channels his breath for " + t("{q_t}s") + ": every " + t("{q_p}s") + " it deals " + mag("q_dmg", "q_ratio") +
                 " magic damage to the enemies in a line, {q_sec_dmg} more after " + t("1s") + " on one target; crowd "
                 "control breaks it. In flight it has no cooldown and channels longer.",
        "skill2": "Summons a black hole at the target for " + t("{e_t}s") + ": every " + t("{e_p}s") + " " +
                  mag("e_dmg", "e_ratio") + " magic damage, pulling enemies toward its centre and " + cc("slowing") +
                  " them {e_slow}%; its centre deals {e_exec}% of a champion's maximum health as true damage each second.",
        "ult": n("Falling Star") + ": a star crashes on the target for " + mag("r_dmg", "r_ratio") + " magic damage and a " +
               t("{r_stun}s") + " " + cc("stun") + ". " + n("The Skies Descend") + ": a wider impact, " +
               mag("r_dmg2", "r_ratio2") + " and a " + t("{r_up}s") + " " + cc("knock-up") + ", then a shockwave from its "
               "edge for " + mag("r_wdmg", "r_wratio") + " and a {r_wslow}% " + cc("slow") + ".",
        "names": ("Breath of Light", "Singularity", "Falling Star"),
    },
    "ko": {
        "name": "아우렐리온 솔",
        "attack": "별을 던진다. " + n("우주의 창조자") + ": 스킬이 챔피언을 맞히면 별무리 획득(중첩당 주문력 +{d_ap}%, 최대 "
                  "{d_max}), {sky_n}개마다 다음 궁극기가 천상 강림이 됨. " + n("별의 비행") + ": 처치 관여 후 " +
                  t("{w_t}초") + " 동안 비행, 이동 속도 +{w_ms}%, 주문력 +{w_ap}%.",
        "skill": t("{q_t}초") + " 동안 숨결을 정신 집중: " + t("{q_p}초") + "마다 일직선의 적에게 " + mag("q_dmg", "q_ratio") +
                 " 마법 피해, 한 대상에 " + t("1초") + " 이상 시 매번 {q_sec_dmg} 추가; 군중 제어에 끊김. 비행 중 재사용 대기시간 없음.",
        "skill2": "대상 위치에 " + t("{e_t}초") + " 동안 블랙홀 소환: " + t("{e_p}초") + "마다 " + mag("e_dmg", "e_ratio") +
                  " 마법 피해, 적을 중심으로 끌어당기고 {e_slow}% " + cc("둔화") + "; 중심은 매초 챔피언 최대 체력의 {e_exec}% 고정 피해.",
        "ult": n("유성") + ": 대상 위치에 별이 떨어져 " + mag("r_dmg", "r_ratio") + " 마법 피해와 " + t("{r_stun}초") + " " +
               cc("기절") + ". " + n("천상 강림") + ": 더 넓게 " + mag("r_dmg2", "r_ratio2") + "와 " + t("{r_up}초") + " " +
               cc("에어본") + ", 이어서 가장자리 충격파 " + mag("r_wdmg", "r_wratio") + "와 {r_wslow}% " + cc("둔화") + ".",
        "names": ("빛의 숨결", "특이점", "유성"),
    },
    "ja": {
        "name": "オレリオン・ソル",
        "attack": "星を投げる。" + n("宇宙の創造者") + "：スキルがチャンピオンに当たると星屑獲得（1スタックにつき魔力+{d_ap}%、"
                  "最大{d_max}）、{sky_n}個ごとに次のアルティメットが崩れ落つ天穹に。" + n("天空への飛翔") +
                  "：キル関与後" + t("{w_t}秒") + "飛行、移動速度+{w_ms}%、魔力+{w_ap}%。",
        "skill": t("{q_t}秒") + "息吹を詠唱：" + t("{q_p}秒") + "ごとに直線上の敵に" + mag("q_dmg", "q_ratio") +
                 "の魔法ダメージ、同じ対象に" + t("1秒") + "以上で毎回+{q_sec_dmg}；行動妨害で中断。飛行中はクールダウンなし。",
        "skill2": "対象の位置に" + t("{e_t}秒") + "ブラックホールを召喚：" + t("{e_p}秒") + "ごとに" + mag("e_dmg", "e_ratio") +
                  "の魔法ダメージ、敵を中心へ引き寄せ{e_slow}%" + cc("スロウ") + "；中心は毎秒チャンピオンの最大体力{e_exec}%の確定ダメージ。",
        "ult": n("星の邂逅") + "：対象の位置に星が落ち" + mag("r_dmg", "r_ratio") + "の魔法ダメージと" + t("{r_stun}秒") +
               cc("スタン") + "。" + n("崩れ落つ天穹") + "：範囲が広く" + mag("r_dmg2", "r_ratio2") + "と" + t("{r_up}秒") +
               cc("ノックアップ") + "、続いて外縁の衝撃波" + mag("r_wdmg", "r_wratio") + "と{r_wslow}%" + cc("スロウ") + "。",
        "names": ("星炎の息吹", "特異点", "星の邂逅"),
    },
}

C = "league_aurelionsol_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the breath's burn quiet (one every 167 ms), the stars' impacts loud, the voice as
# the other heroes'
SOUNDS = {f"league_aurelionsol_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.5), ("q", 0.7), ("q_hit", 0.3), ("e", 0.7), ("e_hole", 0.75), ("e_core", 0.6),
    ("r", 0.85), ("r_land", 0.9), ("r_hit", 0.6), ("r_sky", 0.95), ("r_wave", 0.75), ("w", 0.7), ("sky", 0.75),
    ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9), ("vo_w", 0.85))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("d_ap", "d_max", "sky_n", "w_ms", "w_ap", "q_dmg", "q_ratio", "q_sec_dmg", "e_dmg", "e_ratio",
                           "e_slow", "e_exec", "r_dmg", "r_ratio", "r_dmg2", "r_ratio2", "r_wdmg", "r_wratio", "r_wslow")}
    for k in ("w_t", "q_t", "q_p", "e_t", "e_p", "r_stun", "r_up"):
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
    if "Aurelion Sol" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Aurelion Sol. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
