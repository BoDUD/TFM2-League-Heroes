"""Bel'Veth's text (5 languages), sound_info files and their keys in the shared files, numbers from build_belveth.P.

    python tools/kit/setup_belveth.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_belveth in every language, description + skill_name),
sound/sfx/league_belveth_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Bel'Veth named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 卑尔维斯 (虚空女皇): 溶烛化紫; 虚空激流, 上觐沉渊, 搠面皇锋, 万载豪筵; zh_TW 貝爾薇斯: 魂斷紫海;
虛空強襲, 尾棘鞭笞, 女皇風暴, 無盡盛宴; ja ベル＝ヴェス: 死のラベンダー; ヴォイドサージ, 天と地, ロイヤルストーム, 終わりなき晩餐;
ko 벨베스: 연보랏빛 죽음; 공허 쇄도, 위와 아래, 여제의 소용돌이, 끝없는 연회.
Slots: skill = Void Surge, skill2 = Above and Below, ult = Endless Banquet with Royal Maelstrom in its text (the true
form's storm); Death in Lavender in the attack's text. The main pack's storm starts when two enemy champions are on her
in the true form (data reads no health; the add-on league_belveth starts it on her real health, its own tooltip says
so). No combo sentence in any text (the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_belveth import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_belveth"
VERSION = "0.206.0"     # the next free number above main 0.205.0 (Singed #498, 2026-10-24)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 0, "y": -34}, "center": {"x": 0, "y": -17}, "banpick_center": {"x": 0, "y": -8}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


def hl(x):
    return G + x + E


TEXT = {
    "zh-hans": {
        "name": "卑尔维斯",
        "attack": "用翼刃劈砍，出手很快。" + n("溶烛化紫") + "：每放一个技能攻速+{p_as}%（" + t("{p_t}秒") + "）；"
                  "参与击杀敌方英雄后永久攻速+{l_as}%（最多" + t("{l_max}层") + "）。",
        "skill": "朝目标突进并穿过去，对途经的所有敌人造成" + phys("q_dmg", "q_ratio") + "物理伤害。",
        "skill2": "甩尾砸地，冲击沿直线向前，造成" + phys("w_dmg", "w_ratio") + "物理伤害，" + cc("击飞") + t("{w_up}秒") +
                  "并" + cc("减速") + "{w_slow}%（" + t("{w_slow_t}秒") + "）。",
        "ult": "吞下珊瑚爆开：周围敌人受" + phys("r_dmg", "r_ratio") + "物理伤害并" + cc("减速") + "{r_slow}%；化为真身" +
               t("{r_t}秒") + "：生命+{r_hp}%、攻击距离增加、攻速+{r_as}%、移速+{r_ms}%。真身被围攻时化为" + n("搠面皇锋") +
               "：原地" + t("{e_t}秒") + "减伤{e_dr}%、" + hl("吸血{e_vamp}%") + "。",
        "names": ("虚空激流", "上觐沉渊", "万载豪筵"),
    },
    "zh-hant": {
        "name": "貝爾薇斯",
        "attack": "用翼刃劈砍，出手很快。" + n("魂斷紫海") + "：每施放一個技能攻速+{p_as}%（" + t("{p_t}秒") + "）；"
                  "參與擊殺敵方英雄後永久攻速+{l_as}%（最多" + t("{l_max}層") + "）。",
        "skill": "朝目標突進並穿過去，對途經的所有敵人造成" + phys("q_dmg", "q_ratio") + "物理傷害。",
        "skill2": "甩尾砸地，衝擊沿直線向前，造成" + phys("w_dmg", "w_ratio") + "物理傷害，" + cc("擊飛") + t("{w_up}秒") +
                  "並" + cc("緩速") + "{w_slow}%（" + t("{w_slow_t}秒") + "）。",
        "ult": "吞下珊瑚爆開：周圍敵人受" + phys("r_dmg", "r_ratio") + "物理傷害並" + cc("緩速") + "{r_slow}%；化為真身" +
               t("{r_t}秒") + "：生命+{r_hp}%、攻擊距離增加、攻速+{r_as}%、移速+{r_ms}%。真身被圍攻時化為" + n("女皇風暴") +
               "：原地" + t("{e_t}秒") + "減傷{e_dr}%、" + hl("吸血{e_vamp}%") + "。",
        "names": ("虛空強襲", "尾棘鞭笞", "無盡盛宴"),
    },
    "en": {
        "name": "Bel'Veth",
        "attack": "Fast slashes of her wing-blades. " + n("Death in Lavender") + ": every spell gives {p_as}% attack speed for " +
                  t("{p_t}s") + "; each enemy champion takedown adds {l_as}% attack speed for good (up to " +
                  t("{l_max} stacks") + ").",
        "skill": "Dashes at the target and through it, dealing " + phys("q_dmg", "q_ratio") +
                 " physical damage to every enemy she passes.",
        "skill2": "Slams her tail: a shockwave runs along a line, dealing " + phys("w_dmg", "w_ratio") + " physical damage, " +
                  cc("knocking up") + " for " + t("{w_up}s") + " and " + cc("slowing") + " {w_slow}% for " +
                  t("{w_slow_t}s") + ".",
        "ult": "Eats the void coral: it bursts round her for " + phys("r_dmg", "r_ratio") + " physical damage and a {r_slow}% " +
               cc("slow") + "; she takes her true form for " + t("{r_t}s") + ": +{r_hp}% health, more attack range, "
               "+{r_as}% attack speed, +{r_ms}% move speed. Beset in the true form she becomes " + n("Royal Maelstrom") +
               ": rooted for " + t("{e_t}s") + ", {e_dr}% less damage taken and " + hl("{e_vamp}% life steal") + ".",
        "names": ("Void Surge", "Above and Below", "Endless Banquet"),
    },
    "ko": {
        "name": "벨베스",
        "attack": "날개 칼날로 빠르게 벤다. " + n("연보랏빛 죽음") + ": 스킬을 쓸 때마다 " + t("{p_t}초") + " 동안 공격 속도 +{p_as}%; "
                  "적 챔피언 처치 관여 시 공격 속도 영구 +{l_as}%(최대 " + t("{l_max}중첩") + ").",
        "skill": "대상에게 돌진해 꿰뚫고 지나가며 지나친 모든 적에게 " + phys("q_dmg", "q_ratio") + " 물리 피해.",
        "skill2": "꼬리로 내려쳐 직선으로 충격파를 보냄: " + phys("w_dmg", "w_ratio") + " 물리 피해, " + t("{w_up}초") + " " +
                  cc("에어본") + ", " + t("{w_slow_t}초") + " 동안 {w_slow}% " + cc("둔화") + ".",
        "ult": "공허 산호를 삼켜 터뜨림: 주변 적에게 " + phys("r_dmg", "r_ratio") + " 물리 피해와 {r_slow}% " + cc("둔화") +
               "; " + t("{r_t}초") + " 동안 진정한 모습: 체력 +{r_hp}%, 사거리 증가, 공격 속도 +{r_as}%, 이동 속도 +{r_ms}%. "
               "진정한 모습에서 포위되면 " + n("여제의 소용돌이") + ": " + t("{e_t}초") + " 동안 제자리에서 받는 피해 {e_dr}% 감소, " +
               hl("생명력 흡수 {e_vamp}%") + ".",
        "names": ("공허 쇄도", "위와 아래", "끝없는 연회"),
    },
    "ja": {
        "name": "ベル＝ヴェス",
        "attack": "翼の刃で素早く斬る。" + n("死のラベンダー") + "：スキルを使うたび" + t("{p_t}秒") + "攻撃速度+{p_as}%；"
                  "敵チャンピオンのキル/アシストで攻撃速度が永続+{l_as}%（最大" + t("{l_max}スタック") + "）。",
        "skill": "対象へ突進して貫き、通過したすべての敵に" + phys("q_dmg", "q_ratio") + "の物理ダメージ。",
        "skill2": "尾を叩きつけ衝撃波を直線に放つ：" + phys("w_dmg", "w_ratio") + "の物理ダメージ、" + t("{w_up}秒") +
                  cc("ノックアップ") + "、" + t("{w_slow_t}秒") + "{w_slow}%" + cc("スロウ") + "。",
        "ult": "ヴォイドコーラルを喰らい炸裂：周囲の敵に" + phys("r_dmg", "r_ratio") + "の物理ダメージと{r_slow}%" + cc("スロウ") +
               "。" + t("{r_t}秒") + "真の姿：体力+{r_hp}%、射程増加、攻撃速度+{r_as}%、移動速度+{r_ms}%。真の姿で囲まれると" +
               n("ロイヤルストーム") + "：" + t("{e_t}秒") + "その場で被ダメージ-{e_dr}%、" + hl("ライフスティール{e_vamp}%") + "。",
        "names": ("ヴォイドサージ", "天と地", "終わりなき晩餐"),
    },
}

C = "league_belveth_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (the blow lower: it comes often), the storm's slices
# quiet (one every e_p ticks), the voice as the other heroes'
SOUNDS = {f"league_belveth_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.5), ("q", 0.7), ("q_hit", 0.65), ("w", 0.7), ("w_slam", 0.8), ("w_hit", 0.65),
    ("e", 0.75), ("e_hit", 0.35), ("r", 0.85), ("r_burst", 0.8), ("r_hit", 0.65), ("c_eat", 0.7),
    ("vo_q", 0.85), ("vo_w", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_as", "l_as", "l_max", "q_dmg", "q_ratio", "w_dmg", "w_ratio", "w_slow", "r_dmg", "r_ratio",
                           "r_slow", "r_hp", "r_as", "r_ms", "e_dr", "e_vamp")}
    for k in ("p_t", "w_up", "w_slow_t", "r_t", "e_t"):
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
    if "Bel'Veth" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Bel'Veth. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
