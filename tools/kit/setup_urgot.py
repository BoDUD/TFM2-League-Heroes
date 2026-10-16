"""Urgot's text (5 languages), sound_info files and his keys in the shared files, numbers from build_urgot.P.

    python tools/kit/setup_urgot.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_urgot in every language, description + skill_name),
sound/sfx/league_urgot_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point), mod.mod_info (0.126.0, Urgot named). Only his keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 无畏战车 / 厄加特 - the client swaps name and title: 厄加特; 回响烈焰, 腐蚀电荷, 净除, 鄙弃,
超越死亡的恐惧; zh_TW 烏爾加特 / 重裝無畏, 振盪火砲, 酸性榴彈, 殺戮射擊, 恐怖襲擊, 索命虐殺; ja アーゴット / ドレッドノート,
エコーフレイム, コラプトシェル, パージ, ディスデイン, デスグラインダー; ko 우르곳 / 살상 병기, 화염의 메아리, 부식성 폭약, 심판의 원,
경멸, 불사의 공포).
Slots: skill = Q (named) with W told in its text, skill2 = E, ult = R; the passive is told in the attack's text. No combo
sentence in any text (the user's rule). No `league_urgot_attack` sound: the engine would play it at the start of every
attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_urgot import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_urgot"
VERSION = "0.126.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
T = "<#ffffffff>"      # true damage
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face at his bald crown (ppu_restyle face_to (3, -24)); the idle tops 32 px over the pivot (lo_idle
# -48 / 1.5), above -28 -> banpick_center y = -39 - (-32) (the card rule)
VIEW = {"face": {"x": 3, "y": -24}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -7}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "厄加特",
        "attack": "炮臂霰弹。" + O + "回响烈焰" + E + "：普攻和净除的子弹会让腿上的霰弹轮流朝目标喷扇形火焰，造成{p_ratio}%攻击力+目标{p_hp}%最大生命的" +
                  O + "物理伤害" + E + "（每{leg_t}秒一次，3级前{leg_t0}秒）。",
        "skill": "抛出电荷，落地后爆炸，造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "并减速{q_slow}%。命中后开启" + O + "净除" + E +
                 A + "{w_t}秒" + E + "：普攻换成机枪连射，每发" + phy("w_dmg", "w_ratio") + "。",
        "skill2": "获得" + phy("e_sh", "e_sh_ratio") + "护盾，冲向敌方英雄，撞上后造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E +
                  "、" + R + "晕眩{e_stun}秒" + E + "并把他甩到身后，开启" + O + "净除" + E + "。",
        "ult": "缠斗中连续打中英雄{r_hits}下时，朝他发射钻头钉住第一个敌方英雄，造成" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "并减速，" + A + "{r_t}秒" + E +
               "后拽回来处决：造成其{r_ex}%最大生命的" + T + "真实伤害" + E + "；处决成功时周围敌人" + R + "恐惧{r_fear}秒" + E + "。",
        "names": ("腐蚀电荷", "鄙弃", "超越死亡的恐惧"),
    },
    "zh-hant": {
        "name": "烏爾加特",
        "attack": "砲臂霰彈。" + O + "振盪火砲" + E + "：普攻和殺戮射擊的子彈會讓腿上的霰彈輪流朝目標噴扇形火焰，造成{p_ratio}%攻擊力+目標{p_hp}%最大生命的" +
                  O + "物理傷害" + E + "（每{leg_t}秒一次，3級前{leg_t0}秒）。",
        "skill": "拋出榴彈，落地後爆炸，造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "並緩速{q_slow}%。命中後開啟" + O + "殺戮射擊" + E +
                 A + "{w_t}秒" + E + "：普攻換成機槍連射，每發" + phy("w_dmg", "w_ratio") + "。",
        "skill2": "獲得" + phy("e_sh", "e_sh_ratio") + "護盾，衝向敵方英雄，撞上後造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E +
                  "、" + R + "暈眩{e_stun}秒" + E + "並把他甩到身後，開啟" + O + "殺戮射擊" + E + "。",
        "ult": "纏鬥中連續打中英雄{r_hits}下時，朝他發射鑽頭釘住第一個敵方英雄，造成" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "並緩速，" + A + "{r_t}秒" + E +
               "後拽回來處決：造成其{r_ex}%最大生命的" + T + "真實傷害" + E + "；處決成功時周圍敵人" + R + "恐懼{r_fear}秒" + E + "。",
        "names": ("酸性榴彈", "恐怖襲擊", "索命虐殺"),
    },
    "en": {
        "name": "Urgot",
        "attack": "Shotgun blasts from his cannon arm. " + O + "Echoing Flames" + E + ": attacks and Purge's shots make his leg "
                  "shotguns take turns blasting a cone at the target for {p_ratio}% AD + {p_hp}% of its max health as " + O +
                  "physical damage" + E + " (once every {leg_t}s, {leg_t0}s below level 3).",
        "skill": "Fires a charge that explodes where it lands, dealing " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E +
                 " and slowing {q_slow}%. A hit starts " + O + "Purge" + E + " for " + A + "{w_t}s" + E +
                 ": his attacks become machine-gun shots of " + phy("w_dmg", "w_ratio") + ".",
        "skill2": "Gains a " + phy("e_sh", "e_sh_ratio") + " shield and charges an enemy champion: on contact " + phy("e_dmg", "e_ratio") +
                  " " + O + "physical damage" + E + ", a " + R + "{e_stun}s stun" + E + ", and he hurls it behind him, starting " + O +
                  "Purge" + E + ".",
        "ult": "On his {r_hits}th hit in a row on champions, fires a drill that impales the first enemy champion for " + phy("r_dmg", "r_ratio") + " " + O + "physical damage" + E +
               " and a slow; after " + A + "{r_t}s" + E + " he reels it in and executes it for {r_ex}% of its max health as " + T +
               "true damage" + E + ". An execution makes nearby enemies " + R + "flee for {r_fear}s" + E + ".",
        "names": ("Corrosive Charge", "Disdain", "Fear Beyond Death"),
    },
    "ko": {
        "name": "우르곳",
        "attack": "포신 팔로 산탄을 쏩니다. " + O + "화염의 메아리" + E + ": 기본 공격과 심판의 원 탄환마다 다리의 산탄총이 번갈아 대상에게 "
                  "부채꼴로 발사해 공격력의 {p_ratio}% + 대상 최대 체력의 {p_hp}% " + O + "물리 피해" + E + "({leg_t}초마다, 3레벨 전 {leg_t0}초).",
        "skill": "폭약을 던져 떨어진 곳에서 폭발, " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + "와 {q_slow}% 둔화. 적중 시 " + O +
                 "심판의 원" + E + " " + A + "{w_t}초" + E + ": 기본 공격이 기관총 연사로 바뀌어 발당 " + phy("w_dmg", "w_ratio") + ".",
        "skill2": phy("e_sh", "e_sh_ratio") + "의 보호막을 얻고 적 챔피언에게 돌진, 충돌 시 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" +
                  E + ", " + R + "{e_stun}초 기절" + E + " 후 뒤로 던지며 " + O + "심판의 원" + E + " 시작.",
        "ult": "챔피언을 연속 {r_hits}회 맞히면 드릴을 쏘아 첫 적 챔피언을 꿰뚫어 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + "와 둔화, " + A + "{r_t}초" + E +
               " 후 끌어당겨 처형: 최대 체력의 {r_ex}% " + T + "고정 피해" + E + ". 처형 성공 시 주변 적 " + R + "{r_fear}초 공포" + E + ".",
        "names": ("부식성 폭약", "경멸", "불사의 공포"),
    },
    "ja": {
        "name": "アーゴット",
        "attack": "砲腕で散弾を撃つ。" + O + "エコーフレイム" + E + "：通常攻撃とパージの弾ごとに脚のショットガンが交代で対象へ扇状に撃ち、"
                  "攻撃力の{p_ratio}%+対象の最大体力の{p_hp}%の" + O + "物理ダメージ" + E + "（{leg_t}秒に1回、レベル3未満は{leg_t0}秒）。",
        "skill": "炸裂弾を放ち、着弾地点で爆発して" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "と{q_slow}%スロウ。命中すると" + O +
                 "パージ" + E + "が" + A + "{w_t}秒" + E + "発動：通常攻撃が機関銃の連射になり1発" + phy("w_dmg", "w_ratio") + "。",
        "skill2": phy("e_sh", "e_sh_ratio") + "のシールドを得て敵チャンピオンへ突進、衝突で" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" +
                  E + "と" + R + "{e_stun}秒スタン" + E + "、背後へ投げ飛ばし" + O + "パージ" + E + "発動。",
        "ult": "チャンピオンに{r_hits}回連続で命中させるとドリルを撃ち最初の敵チャンピオンを貫き" + phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "とスロウ、" + A + "{r_t}秒" + E +
               "後に引き寄せて処刑：最大体力の{r_ex}%の" + T + "確定ダメージ" + E + "。処刑成功で周囲の敵が" + R + "{r_fear}秒恐怖" + E + "。",
        "names": ("コラプトシェル", "ディスデイン", "デスグラインダー"),
    },
}

C = "league_urgot_sfx_"
V = "league_urgot_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_urgot_a_shot": [(C + "a_shot", 0.45, 0.0)],
    "league_urgot_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_urgot_p_leg": [(C + "p_leg", 0.4, 0.0)],
    "league_urgot_w_on": [(C + "w_on", 0.5, 0.0)],
    "league_urgot_w_shot": [(C + "w_shot", 0.25, 0.0)],
    "league_urgot_q": [(C + "q", 0.5, 0.0)],
    "league_urgot_q_land": [(C + "q_land", 0.55, 0.0)],
    "league_urgot_e": [(C + "e", 0.55, 0.0)],
    "league_urgot_e_hit": [(C + "e_hit", 0.55, 0.0)],
    "league_urgot_r": [(C + "r", 0.6, 0.0)],
    "league_urgot_r_fire": [(C + "r_fire", 0.6, 0.0)],
    "league_urgot_r_hit": [(C + "r_hit", 0.6, 0.0)],
    "league_urgot_r_ex": [(C + "r_ex", 0.65, 0.0)],
    "league_urgot_vo_q": [(V + "q", 0.85, 0.0)],
    "league_urgot_vo_e": [(V + "e", 0.85, 0.0)],
    "league_urgot_vo_r": [(V + "r", 0.9, 0.0)],
    "league_urgot_vo_r_kill": [(V + "r_kill", 0.9, 0.0), (C + "r_fear", 0.6, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_ratio", "p_hp", "q_dmg", "q_ratio", "q_slow", "w_dmg", "w_ratio", "e_sh", "e_sh_ratio",
                           "e_dmg", "e_ratio", "r_dmg", "r_ratio", "r_ex", "r_hits")}
    for k in ("leg_t", "leg_t0", "w_t", "e_stun", "r_t", "r_fear"):
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
    if "Urgot" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Urgot. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
