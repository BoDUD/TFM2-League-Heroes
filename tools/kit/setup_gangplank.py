"""Gangplank's text (5 languages), sound_info files and his keys in the shared files, numbers from build_gangplank.P.

    python tools/kit/setup_gangplank.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_gangplank in every language, description + skill_name),
sound/sfx/league_gangplank_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Gangplank named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 普朗克 (海洋之灾): 烈火审讯, 枪火谈判, 坏血病疗法, 火药桶, 加农炮幕; zh_TW 剛普朗克:
烈火審判, 槍火談判, 壞血症療法, 火藥桶, 加農炮幕; ja ガングプランク: 背水の銃剣, 偽りの発砲, 壊血病治癒, 火薬樽, 一斉砲撃;
ko 갱플랭크: 불의 심판, 혀어어어업상, 괴혈병 치료, 화약통, 포탄 세례.
Slots: skill = Q Parrrley, skill2 = E Powder Keg, ult = R Cannon Barrage; the passive and the automatic W in the
attack's text. No combo sentence in any text (the user's rule). The main pack's rules are the ones written (the add-on's
cleanse of a stun already on him and its keg chain are the README's).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_gangplank import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_gangplank"
VERSION = "0.145.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
T = "<#f5f5f5ff>"      # true damage
G = "<#7dd87dff>"      # heals
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle face_to); banpick_center from tools/art/bp_card_audit.py
VIEW = {"face": {"x": 2, "y": -29}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -12}}  # 10-18 PPU 1.2 at 90%


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def tru(d, r):
    return f"{T}{{{d}}}{E} + {ADi}{T}{{{r}}}%{E}"


HEAL = G + "{w_heal}" + E + " + " + ADi + G + "{w_ratio}%" + E

TEXT = {
    "zh-hans": {
        "name": "普朗克",
        "attack": "弯刀砍击。" + O + "烈火审讯" + E + "：每" + A + "{p_t}秒" + E + "下次攻击或枪火谈判点燃目标，" + A + "{p_burn}秒" + E + "内造成" +
                  tru("p_dmg", "p_ratio") + T + "真实伤害" + E + "，自己加速{p_ms}%；火药桶爆炸时刷新。" + O + "坏血病疗法" + E +
                  "：3级起被控制或被围攻时吃橘子，回复" + HEAL + "生命，" + R + "免控" + E + A + "{w_imm}秒" + E + "。",
        "skill": "开枪射击：造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "，可暴击，会触发烈火审讯。打中后" + A + "{e_arm}秒" + E +
                 "内，引线已点燃、桶边有敌人的火药桶都会被引爆。",
        "skill2": "向敌方英雄扔火药桶（最多" + A + "{e_slots}个" + E + "，留" + A + "{e_t}秒" + E + "），" + A + "{e_arm}秒" + E + "后引线点燃。被枪火谈判、贴身攻击"
                  "或另一个桶的爆炸引爆：范围内敌人受到" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "（英雄再加{e_champ}），无视{e_pen}%护甲，" +
                  R + "减速{e_slow}%" + E + A + "{e_slow_t}秒" + E + "。",
        "ult": "朝天打出信号：" + A + "{r_call}秒" + E + "后炮弹砸向敌方英雄所在区域，共" + A + "{r_waves}波" + E + "，每" + A + "{r_p}秒" + E +
               "一波，每波造成" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "并" + R + "减速{r_slow}%" + E + "。全图可放，优先打向被控制的敌方英雄。",
        "names": ("枪火谈判", "火药桶", "加农炮幕"),
    },
    "zh-hant": {
        "name": "剛普朗克",
        "attack": "彎刀砍擊。" + O + "烈火審判" + E + "：每" + A + "{p_t}秒" + E + "下次攻擊或槍火談判點燃目標，" + A + "{p_burn}秒" + E + "內造成" +
                  tru("p_dmg", "p_ratio") + T + "真實傷害" + E + "，自己加速{p_ms}%；火藥桶爆炸時刷新。" + O + "壞血症療法" + E +
                  "：3級起被控制或被圍攻時吃橘子，回復" + HEAL + "生命，" + R + "免控" + E + A + "{w_imm}秒" + E + "。",
        "skill": "開槍射擊：造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "，可暴擊，會觸發烈火審判。打中後" + A + "{e_arm}秒" + E +
                 "內，引線已點燃、桶邊有敵人的火藥桶都會被引爆。",
        "skill2": "向敵方英雄扔火藥桶（最多" + A + "{e_slots}個" + E + "，留" + A + "{e_t}秒" + E + "），" + A + "{e_arm}秒" + E + "後引線點燃。被槍火談判、貼身攻擊"
                  "或另一個桶的爆炸引爆：範圍內敵人受到" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "（英雄再加{e_champ}），無視{e_pen}%護甲，" +
                  R + "緩速{e_slow}%" + E + A + "{e_slow_t}秒" + E + "。",
        "ult": "朝天打出信號：" + A + "{r_call}秒" + E + "後砲彈砸向敵方英雄所在區域，共" + A + "{r_waves}波" + E + "，每" + A + "{r_p}秒" + E +
               "一波，每波造成" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "並" + R + "緩速{r_slow}%" + E + "。全圖可放，優先打向被控制的敵方英雄。",
        "names": ("槍火談判", "火藥桶", "加農炮幕"),
    },
    "en": {
        "name": "Gangplank",
        "attack": "Cutlass slashes. " + O + "Trial by Fire" + E + ": every " + A + "{p_t}s" + E + " his next attack or Parrrley sets the "
                  "target ablaze for " + tru("p_dmg", "p_ratio") + " " + T + "true damage" + E + " over " + A + "{p_burn}s" + E + " and speeds him "
                  "{p_ms}%; a Powder Keg blowing up resets it. " + O + "Remove Scurvy" + E + ": from level 3, when crowd-controlled or "
                  "crowded he eats an orange: heals " + HEAL + " and is " + R + "immune to crowd control" + E + " for " + A + "{w_imm}s" + E + ".",
        "skill": "Fires his pistol: " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ", can critically strike, applies Trial by "
                 "Fire. For " + A + "{e_arm}s" + E + " after the hit, every lit Powder Keg with an enemy beside it blows up.",
        "skill2": "Lobs a keg at an enemy champion (up to " + A + "{e_slots}" + E + ", lasting " + A + "{e_t}s" + E + "); its fuse is lit after " + A +
                  "{e_arm}s" + E + ". A lit keg blows up on Parrrley, his attack next to it or the other keg's blast: " + phy("e_dmg", "e_ratio") +
                  " " + O + "physical damage" + E + " around it ({e_champ} more to champions), ignoring {e_pen}% armour, " + R + "slowing "
                  "{e_slow}%" + E + " for " + A + "{e_slow_t}s" + E + ".",
        "ult": "Signals his ship: after " + A + "{r_call}s" + E + " cannonballs rain on an enemy champion's area in " + A + "{r_waves} waves" + E +
               ", one every " + A + "{r_p}s" + E + ", each " + phy("r_dmg", "r_ratio") + " " + O + "physical damage" + E + " and " + R + "slowing "
               "{r_slow}%" + E + ". Anywhere on the map, champions held by crowd control first.",
        "names": ("Parrrley", "Powder Keg", "Cannon Barrage"),
    },
    "ko": {
        "name": "갱플랭크",
        "attack": "칼로 벤다. " + O + "불의 심판" + E + ": " + A + "{p_t}초" + E + "마다 다음 공격이나 혀어어어업상이 대상을 불태워 " + A + "{p_burn}초" + E +
                  "간 " + tru("p_dmg", "p_ratio") + "의 " + T + "고정 피해" + E + ", 자신은 {p_ms}% 가속, 화약통 폭발 시 초기화. " + O + "괴혈병 치료" + E +
                  ": 3레벨부터 군중 제어나 포위 시 오렌지를 먹어 " + HEAL + " 회복, " + A + "{w_imm}초" + E + " " + R + "군중 제어 면역" + E + ".",
        "skill": "총을 쏜다: " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + ", 치명타 가능, 불의 심판 적용. 적중 후 " + A + "{e_arm}초" + E +
                 " 안에 심지가 타는 화약통 중 적이 곁에 있는 것은 모두 폭발.",
        "skill2": "적 챔피언에게 화약통을 던진다(최대 " + A + "{e_slots}개" + E + ", " + A + "{e_t}초" + E + "), " + A + "{e_arm}초" + E + " 후 심지 점화. 혀어어어업상, "
                  "곁에서의 공격, 다른 통의 폭발로 터져 주변 적에게 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + "(챔피언 +{e_champ}), 방어력 "
                  "{e_pen}% 무시, " + A + "{e_slow_t}초" + E + " " + R + "{e_slow}% 둔화" + E + ".",
        "ult": "배에 신호를 보낸다: " + A + "{r_call}초" + E + " 후 적 챔피언이 있는 지역에 포탄 " + A + "{r_waves}번" + E + "(" + A + "{r_p}초" + E +
               "마다), 매번 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + "와 " + R + "{r_slow}% 둔화" + E + ". 맵 어디든, 군중 제어된 적 우선.",
        "names": ("혀어어어업상", "화약통", "포탄 세례"),
    },
    "ja": {
        "name": "ガングプランク",
        "attack": "カトラスで斬る。" + O + "背水の銃剣" + E + "：" + A + "{p_t}秒" + E + "毎に次の通常攻撃か偽りの発砲が対象を燃やし" + A + "{p_burn}秒" + E +
                  "で" + tru("p_dmg", "p_ratio") + "の" + T + "確定ダメージ" + E + "、自身{p_ms}%加速、火薬樽の爆発で再使用可能。" + O + "壊血病治癒" + E +
                  "：Lv3から行動妨害や包囲時にオレンジを食べ" + HEAL + "回復、" + A + "{w_imm}秒" + E + R + "行動妨害無効" + E + "。",
        "skill": "銃を撃つ：" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "、クリティカル可、背水の銃剣が発動。命中から" + A + "{e_arm}秒" + E +
                 "以内、導火線に火が付き敵がそばにいる火薬樽はすべて爆発。",
        "skill2": "敵チャンピオンへ火薬樽を投げる（最大" + A + "{e_slots}個" + E + "、" + A + "{e_t}秒" + E + "）、" + A + "{e_arm}秒" + E + "後に点火。偽りの発砲・"
                  "そばでの通常攻撃・別の樽の爆発で爆発し周囲に" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "（チャンピオン+{e_champ}）、"
                  "物理防御{e_pen}%無視、" + A + "{e_slow_t}秒" + E + R + "スロウ{e_slow}%" + E + "。",
        "ult": "船に合図：" + A + "{r_call}秒" + E + "後に敵チャンピオンのいる範囲へ砲弾" + A + "{r_waves}波" + E + "（" + A + "{r_p}秒" + E + "毎）、毎回" +
               phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "と" + R + "スロウ{r_slow}%" + E + "。マップ全域、行動妨害中の敵を優先。",
        "names": ("偽りの発砲", "火薬樽", "一斉砲撃"),
    },
}

C = "league_gangplank_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_gangplank_a_swing": [(C + "a_swing", 0.3, 0.0)],
    "league_gangplank_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_gangplank_p_hit": [(C + "p_hit", 0.4, 0.0)],
    "league_gangplank_q_shot": [(C + "q_shot", 0.5, 0.0)],
    "league_gangplank_q_hit": [(C + "q_hit", 0.3, 0.0)],
    "league_gangplank_e": [(C + "e", 0.45, 0.0)],
    "league_gangplank_e_land": [(C + "e_land", 0.4, 0.0)],
    "league_gangplank_e_boom": [(C + "e_boom", 0.65, 0.0)],
    "league_gangplank_e_hit": [(C + "e_hit", 0.3, 0.0)],
    "league_gangplank_w": [(C + "w", 0.45, 0.0)],
    "league_gangplank_w_eat": [(C + "w_eat", 0.5, 0.0)],
    "league_gangplank_r": [(C + "r", 0.55, 0.0)],
    "league_gangplank_r_call": [(C + "r_call", 0.6, 0.0)],
    "league_gangplank_r_wave": [(C + "r_wave", 0.45, 0.0)],
    "league_gangplank_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_gangplank_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_gangplank_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_gangplank_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ratio", "p_ms", "w_heal", "w_ratio", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_champ",
                           "e_pen", "e_slow", "e_slots", "r_waves", "r_dmg", "r_ratio", "r_slow")}
    for k in ("p_t", "p_burn", "w_imm", "e_t", "e_arm", "e_slow_t", "r_call", "r_p"):
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
    if "Gangplank" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Gangplank. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
