"""Taliyah's text (5 languages), sound_info files and their keys in the shared files, numbers from build_taliyah.P.

    python tools/kit/setup_taliyah.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_taliyah in every language, description + skill_name),
sound/sfx/league_taliyah_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Taliyah named). Only her keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 塔莉垭 (岩雀): 浮石冲; 石穿, 岩突, 撒石阵, 墙幔; zh_TW 塔莉雅: 馭石之術; 旋舞飛岩, 震地之擊,
碎裂地表, 編織者之牆; ja タリヤ: ロックサーフィン; スレッドボレー, サイズミックシャーブ, アンレイベルアース, ウィーバーウォール;
ko 탈리야: 바위타기; 파편 난사, 지각변동, 대지의 파동, 바위술사의 벽.
Slots: skill = Threaded Volley (Worked Ground and its boulder in its text), skill2 = Seismic Shove with Unraveled Earth
in it (the mines thrown first), ult = Weaver's Wall (the upright wall when an enemy champion is near or she is in a fight,
else the horizontal wall she rides); Rock Surfing in the attack's text. No combo sentence in any text (the user's rule:
R -> W and the wall slam are the README's).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_taliyah import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_taliyah"
VERSION = "0.207.0"     # the next free number above main 0.206.0 (Bel'Veth #501, 2026-10-24)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 1, "y": -28}, "center": {"x": 0, "y": -17}, "banpick_center": {"x": 0, "y": -10}}


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
        "name": "塔莉垭",
        "attack": "甩出一块石子。" + n("浮石冲") + "：脱战时移速+{p_ms}%；放出墙幔后踩石冲浪，移速+{r_ms}%（" + t("{r_surf}秒") +
                  "）。",
        "skill": "朝目标方向一颗接一颗扔出" + t("{q_n}颗") + "石头（扔出第一颗后可以移动），第一颗" + mag("q_dmg", "q_ap") +
                 "魔法伤害，之后每颗" + mag("q_dmg2", "q_ap2") + "；脚下留下掘石场（" + t("{q_gt}秒") + "），站在上面施放改为"
                 "一颗大石头：" + mag("q_b_dmg", "q_b_ap") + "并" + cc("减速") + "{q_b_slow}%。",
        "skill2": "在身前地上撒下石雷（" + cc("减速") + "{e_slow}%，" + t("{e_t}秒") + "），目标脚下裂开后隆起，造成" +
                  mag("w_dmg", "w_ap") + "魔法伤害并把敌人掀向自己；飞过石雷时石雷爆炸，造成" + mag("e_dmg", "e_ap") +
                  "魔法伤害并" + cc("眩晕") + t("{e_stun}秒") + "。",
        "ult": "敌人在附近或已在交战：在目标处竖起长石墙（" + t("{r_t}秒") + "），墙上的敌人被拖到她这一侧；敌人较远：从脚下拉出"
               "一道横墙，踩着石头沿墙冲刺，靠近敌人时跳下。碰到墙的敌人" + cc("减速") + "{r_slow}%。",
        "names": ("石穿", "岩突", "墙幔"),
    },
    "zh-hant": {
        "name": "塔莉雅",
        "attack": "甩出一塊石子。" + n("馭石之術") + "：脫戰時移速+{p_ms}%；放出編織者之牆後踩石衝浪，移速+{r_ms}%（" +
                  t("{r_surf}秒") + "）。",
        "skill": "朝目標方向一顆接一顆擲出" + t("{q_n}顆") + "石頭（擲出第一顆後可以移動），第一顆" + mag("q_dmg", "q_ap") +
                 "魔法傷害，之後每顆" + mag("q_dmg2", "q_ap2") + "；腳下留下碎石地（" + t("{q_gt}秒") + "），站在上面施放改為"
                 "一顆大石頭：" + mag("q_b_dmg", "q_b_ap") + "並" + cc("緩速") + "{q_b_slow}%。",
        "skill2": "在身前地上灑下石雷（" + cc("緩速") + "{e_slow}%，" + t("{e_t}秒") + "），目標腳下裂開後隆起，造成" +
                  mag("w_dmg", "w_ap") + "魔法傷害並把敵人掀向自己；飛過石雷時石雷爆炸，造成" + mag("e_dmg", "e_ap") +
                  "魔法傷害並" + cc("暈眩") + t("{e_stun}秒") + "。",
        "ult": "敵人在附近或已在交戰：在目標處豎起長石牆（" + t("{r_t}秒") + "），牆上的敵人被拖到她這一側；敵人較遠：從腳下拉出"
               "一道橫牆，踩著石頭沿牆衝刺，靠近敵人時跳下。碰到牆的敵人" + cc("緩速") + "{r_slow}%。",
        "names": ("旋舞飛岩", "震地之擊", "編織者之牆"),
    },
    "en": {
        "name": "Taliyah",
        "attack": "Flicks a pebble. " + n("Rock Surfing") + ": +{p_ms}% move speed out of a fight; after Weaver's Wall she "
                  "surfs a boulder, +{r_ms}% move speed for " + t("{r_surf}s") + ".",
        "skill": "Throws " + t("{q_n} rocks") + " one after another toward the target (she can move after the first): the first "
                 "deals " + mag("q_dmg", "q_ap") + " magic damage, each after it " + mag("q_dmg2", "q_ap2") + ". It leaves "
                 "Worked Ground under her for " + t("{q_gt}s") + "; cast on it, she throws one boulder instead: " +
                 mag("q_b_dmg", "q_b_ap") + " and a {q_b_slow}% " + cc("slow") + ".",
        "skill2": "Strews mines on the ground in front of her (" + cc("slowing") + " {e_slow}% for " + t("{e_t}s") + "); the "
                  "ground under the target cracks, then erupts for " + mag("w_dmg", "w_ap") + " magic damage, throwing "
                  "enemies toward her. A mine passed over blows up: " + mag("e_dmg", "e_ap") + " magic damage and a " +
                  t("{e_stun}s") + " " + cc("stun") + ".",
        "ult": "With an enemy champion near or a fight on: a long stone wall rises where the target stands for " +
               t("{r_t}s") + ", dragging enemies on it to her side. With the enemies far: a wall runs out from her feet and "
               "she surfs along its top on her boulder, jumping off once enemies are near. Enemies touching the wall are " +
               cc("slowed") + " {r_slow}%.",
        "names": ("Threaded Volley", "Seismic Shove", "Weaver's Wall"),
    },
    "ko": {
        "name": "탈리야",
        "attack": "돌멩이를 던진다. " + n("바위타기") + ": 전투 중이 아닐 때 이동 속도 +{p_ms}%; 바위술사의 벽 후 바위를 타고 " +
                  t("{r_surf}초") + " 동안 이동 속도 +{r_ms}%.",
        "skill": "대상 방향으로 돌 " + t("{q_n}개") + "를 차례로 던짐(첫 돌 후 이동 가능): 첫 돌 " + mag("q_dmg", "q_ap") +
                 " 마법 피해, 이후 각 " + mag("q_dmg2", "q_ap2") + ". 발밑에 " + t("{q_gt}초") + " 동안 다져진 땅을 남기고, "
                 "그 위에서 쓰면 큰 바위 하나: " + mag("q_b_dmg", "q_b_ap") + ", {q_b_slow}% " + cc("둔화") + ".",
        "skill2": "앞쪽 땅에 지뢰를 뿌림(" + t("{e_t}초") + " 동안 {e_slow}% " + cc("둔화") + "); 대상 발밑이 갈라진 뒤 솟아올라 " +
                  mag("w_dmg", "w_ap") + " 마법 피해를 주고 적을 자신 쪽으로 던짐. 지뢰 위를 지나면 폭발: " +
                  mag("e_dmg", "e_ap") + " 마법 피해와 " + t("{e_stun}초") + " " + cc("기절") + ".",
        "ult": "적 챔피언이 가깝거나 교전 중: 대상 위치에 " + t("{r_t}초") + " 동안 긴 돌벽을 세우고 벽 위의 적을 자신 쪽으로 끌어냄. "
               "적이 멀면: 발밑에서 벽을 뻗어 바위를 타고 벽 위를 달리다 적이 가까워지면 뛰어내림. 벽에 닿은 적은 {r_slow}% " +
               cc("둔화") + ".",
        "names": ("파편 난사", "지각변동", "바위술사의 벽"),
    },
    "ja": {
        "name": "タリヤ",
        "attack": "小石を投げる。" + n("ロックサーフィン") + "：戦闘外で移動速度+{p_ms}%；ウィーバーウォールの後は岩に乗り" +
                  t("{r_surf}秒") + "移動速度+{r_ms}%。",
        "skill": "対象の方向へ岩を" + t("{q_n}個") + "続けて投げる（1個目の後は移動可）：1個目" + mag("q_dmg", "q_ap") +
                 "の魔法ダメージ、以降各" + mag("q_dmg2", "q_ap2") + "。足元に" + t("{q_gt}秒") + "採掘場を残し、その上では"
                 "大岩1個：" + mag("q_b_dmg", "q_b_ap") + "と{q_b_slow}%" + cc("スロウ") + "。",
        "skill2": "前方の地面に地雷をまく（" + t("{e_t}秒") + "{e_slow}%" + cc("スロウ") + "）；対象の足元が割れて隆起し" +
                  mag("w_dmg", "w_ap") + "の魔法ダメージ、敵を自分の方へ投げる。地雷の上を飛ぶと爆発：" +
                  mag("e_dmg", "e_ap") + "の魔法ダメージと" + t("{e_stun}秒") + cc("スタン") + "。",
        "ult": "敵チャンピオンが近いか交戦中：対象の位置に" + t("{r_t}秒") + "長い石壁を立て、壁の上の敵を自分の側へ引き出す。"
               "敵が遠い：足元から壁を伸ばし岩に乗って壁の上を進み、敵が近づくと飛び降りる。壁に触れた敵に{r_slow}%" +
               cc("スロウ") + "。",
        "names": ("スレッドボレー", "サイズミックシャーブ", "ウィーバーウォール"),
    },
}

C = "league_taliyah_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the volley's rocks and their hits quiet (five a cast), the boulder and the
# eruption louder, the voice as the other heroes'
SOUNDS = {f"league_taliyah_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.5), ("q_rock", 0.45), ("q_hit", 0.4), ("q_big", 0.75), ("q_big_hit", 0.75),
    ("w", 0.7), ("w_erupt", 0.85), ("w_hit", 0.65), ("e_land", 0.7), ("e_blast", 0.7),
    ("r", 0.85), ("r_wall", 0.85), ("r_slam", 0.8),
    ("vo_q", 0.85), ("vo_w", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_ms", "r_ms", "q_n", "q_dmg", "q_ap", "q_dmg2", "q_ap2", "q_b_dmg", "q_b_ap", "q_b_slow",
                           "e_slow", "w_dmg", "w_ap", "e_dmg", "e_ap", "r_slow")}
    for k in ("r_surf", "q_gt", "e_t", "e_stun", "r_t"):
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
    if "Taliyah" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Taliyah. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
