"""Hwei's text (5 languages), sound_info files and his keys in the shared files, numbers from build_hwei.P.

    python tools/kit/setup_hwei.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_hwei in every language, description + skill_name),
sound/sfx/league_hwei_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Hwei named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 彗 (异画师): 落款; 主题：灾 (没骨火, 攒聚雷, 连皴山), 主题：靖 (飞染, 渲浓), 主题：悚
(阴沉变意, 滞涩幽瞳, 双钩血喉), 焚心绚华绘; zh_TW 赫威: 筆仙真跡; 主題：厄禍筆法 (壞滅熾燄, 震顫轟雷, 熔岩裂隙), 主題：靜謐筆法
(川流湍急, 明鏡止水), 主題：苦惱筆法 (死神面影, 深淵凝視, 碎骨大顎), 絕望螺旋; ja フェイ: 夢想家の銘; 題材: 厄災 (荒廃の炎,
断ち切る稲妻, 沸き立つ大地), 題材: 静謐 (流るる蒼, 内省の泉), 題材: 苦悩 (恐怖の形相, 深淵の眼差し, 粉砕の牙), 絶望の渦; ko 흐웨이:
몽상가의 서명; 주제: 참사 (파멸의 화염, 절단의 번개, 녹아내린 균열), 주제: 평온 (쏜살같은 물살, 반사의 웅덩이), 주제: 고통 (암울한 형상,
심연의 응시, 파괴의 아귀), 절망의 소용돌이.
Slots: skill = Subject: Disaster (the pick by the situation), skill2 = Subject: Torment, ult = Spiraling Despair; the
signature and Serenity in the attack's text. No combo sentence in any text (the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hwei import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_hwei"
VERSION = "0.194.0"     # the next free number above main 0.193.0 (Qiyana #464) (2026-10-22)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card (set at export:
# tools/art/bp_card_audit.py)
VIEW = {"face": {"x": 4, "y": -31}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -10}}


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
        "name": "彗",
        "attack": "挥笔甩出一团墨。" + n("落款") + "：技能命中英雄后" + t("{sig_t}秒") + "内再命中则引爆，造成" + mag("sig_dmg", "sig_ratio") +
                  "魔法伤害。" + n("主题：靖") + "：画灾时加速{w_ms}%，画悚时为自己和附近队友加" + sh("护盾") + mag("w_sh", "w_sh_r") + "。",
        "skill": "依局势作画：被控制的英雄头上落" + n("攒聚雷") + mag("q_w_dmg", "q_w_ratio") + "，再加" + mag("q_w_cc", "q_w_cc_r") + "；否则向英雄掷" +
                 n("没骨火") + mag("q_q_dmg", "q_q_ratio") + "加{q_q_hp}%最大生命；没有英雄时画" + n("连皴山") + "，熔岩灼烧并减速{q_e_slow}%。"
                 "均为魔法伤害。",
        "skill2": "依局势作画：贴身的英雄被" + n("阴沉变意") + cc("恐惧") + t("{e_fear}秒") + "；否则轮流画" + n("滞涩幽瞳") + "（睁眼后" + cc("禁锢") +
                  t("{e_root}秒") + "）与" + n("双钩血喉") + "（咬住并减速{e_slow}%）。均造成" + mag("e_dmg", "e_ratio") + "魔法伤害。",
        "ult": "向英雄甩出颜料，命中后在其脚下展开画卷" + t("{r_t}秒") + "，持续造成魔法伤害并减速{r_slow}%，最后爆炸造成" + mag("r_dmg", "r_ratio") +
               "魔法伤害。",
        "names": ("主题：灾", "主题：悚", "焚心绚华绘"),
    },
    "zh-hant": {
        "name": "赫威",
        "attack": "揮筆甩出一團墨。" + n("筆仙真跡") + "：技能命中英雄後" + t("{sig_t}秒") + "內再命中則引爆，造成" + mag("sig_dmg", "sig_ratio") +
                  "魔法傷害。" + n("靜謐筆法") + "：施展厄禍時加速{w_ms}%，施展苦惱時為自己和附近隊友加" + sh("護盾") + mag("w_sh", "w_sh_r") + "。",
        "skill": "依局勢作畫：受控的英雄頭上落下" + n("震顫轟雷") + mag("q_w_dmg", "q_w_ratio") + "，再加" + mag("q_w_cc", "q_w_cc_r") + "；否則向英雄擲出" +
                 n("壞滅熾燄") + mag("q_q_dmg", "q_q_ratio") + "加{q_q_hp}%最大生命；沒有英雄時畫" + n("熔岩裂隙") + "，灼燒並緩速{q_e_slow}%。"
                 "皆為魔法傷害。",
        "skill2": "依局勢作畫：貼身的英雄被" + n("死神面影") + cc("恐懼") + t("{e_fear}秒") + "；否則輪流畫" + n("深淵凝視") + "（睜眼後" + cc("定身") +
                  t("{e_root}秒") + "）與" + n("碎骨大顎") + "（咬住並緩速{e_slow}%）。皆造成" + mag("e_dmg", "e_ratio") + "魔法傷害。",
        "ult": "向英雄甩出顏料，命中後在其腳下展開氣場" + t("{r_t}秒") + "，持續造成魔法傷害並緩速{r_slow}%，最後爆炸造成" + mag("r_dmg", "r_ratio") +
               "魔法傷害。",
        "names": ("主題：厄禍筆法", "主題：苦惱筆法", "絕望螺旋"),
    },
    "en": {
        "name": "Hwei",
        "attack": "A flick of ink. " + n("Signature of the Visionary") + ": a champion hit by his ability and hit again within " +
                  t("{sig_t}s") + " takes " + mag("sig_dmg", "sig_ratio") + " magic damage. " + n("Subject: Serenity") +
                  ": painting Disaster gives him +{w_ms}% move speed; painting Torment " + sh("shields") + " him and the allies near "
                  "for " + mag("w_sh", "w_sh_r") + ".",
        "skill": "Paints by the situation: " + n("Severing Bolt") + " on a crowd-controlled champion, " + mag("q_w_dmg", "q_w_ratio") +
                 " plus " + mag("q_w_cc", "q_w_cc_r") + "; else " + n("Devastating Fire") + " at a champion, " + mag("q_q_dmg", "q_q_ratio") +
                 " plus {q_q_hp}% of its max health; with no champion near, " + n("Molten Fissure") + ", lava that burns and slows "
                 "{q_e_slow}%. All magic damage.",
        "skill2": "Paints by the situation: " + n("Grim Visage") + " makes a champion on top of him " + cc("flee") + " for " +
                  t("{e_fear}s") + "; else in turn " + n("Gaze of the Abyss") + " (an eye that " + cc("roots") + " for " +
                  t("{e_root}s") + ") and " + n("Crushing Maw") + " (jaws that hold and slow {e_slow}%). Each deals " +
                  mag("e_dmg", "e_ratio") + " magic damage.",
        "ult": "Flings paint at a champion: a canvas spreads under it for " + t("{r_t}s") + ", burning and slowing the enemies on it "
               "{r_slow}%, then bursts for " + mag("r_dmg", "r_ratio") + " magic damage.",
        "names": ("Subject: Disaster", "Subject: Torment", "Spiraling Despair"),
    },
    "ko": {
        "name": "흐웨이",
        "attack": "붓으로 먹을 튕긴다. " + n("몽상가의 서명") + ": 스킬에 맞은 챔피언이 " + t("{sig_t}초") + " 안에 다시 맞으면 폭발해 " +
                  mag("sig_dmg", "sig_ratio") + " 마법 피해. " + n("주제: 평온") + ": 참사를 그리면 이동 속도 +{w_ms}%, 고통을 그리면 자신과 "
                  "주변 아군에게 " + sh("보호막") + " " + mag("w_sh", "w_sh_r") + ".",
        "skill": "상황에 맞게 그린다: 군중 제어된 챔피언에게 " + n("절단의 번개") + " " + mag("q_w_dmg", "q_w_ratio") + ", 추가 " +
                 mag("q_w_cc", "q_w_cc_r") + "; 아니면 챔피언에게 " + n("파멸의 화염") + " " + mag("q_q_dmg", "q_q_ratio") +
                 " + 최대 체력의 {q_q_hp}%; 챔피언이 없으면 " + n("녹아내린 균열") + ", 용암이 불태우고 {q_e_slow}% 둔화. 모두 마법 피해.",
        "skill2": "상황에 맞게 그린다: 붙은 챔피언은 " + n("암울한 형상") + "에 " + t("{e_fear}초") + " " + cc("공포") + "; 아니면 번갈아 " +
                  n("심연의 응시") + "(" + t("{e_root}초") + " " + cc("속박") + ")와 " + n("파괴의 아귀") + "(물고 {e_slow}% 둔화). 모두 " +
                  mag("e_dmg", "e_ratio") + " 마법 피해.",
        "ult": "챔피언에게 물감을 던져 발밑에 그림을 " + t("{r_t}초") + " 펼친다. 위의 적을 불태우고 {r_slow}% 둔화시킨 뒤 폭발해 " +
               mag("r_dmg", "r_ratio") + " 마법 피해.",
        "names": ("주제: 참사", "주제: 고통", "절망의 소용돌이"),
    },
    "ja": {
        "name": "フェイ",
        "attack": "筆で墨を飛ばす。" + n("夢想家の銘") + "：スキルが当たった英雄に" + t("{sig_t}秒") + "以内に再び当てると爆発し" +
                  mag("sig_dmg", "sig_ratio") + "の魔法ダメージ。" + n("題材: 静謐") + "：厄災で移動速度+{w_ms}%、苦悩で自身と周囲の味方に" +
                  sh("シールド") + mag("w_sh", "w_sh_r") + "。",
        "skill": "状況で描き分ける：行動妨害中の英雄に" + n("断ち切る稲妻") + mag("q_w_dmg", "q_w_ratio") + "＋" + mag("q_w_cc", "q_w_cc_r") +
                 "、なければ英雄へ" + n("荒廃の炎") + mag("q_q_dmg", "q_q_ratio") + "＋最大体力の{q_q_hp}%、英雄がいなければ" + n("沸き立つ大地") +
                 "で燃やし{q_e_slow}%スロウ。すべて魔法ダメージ。",
        "skill2": "状況で描き分ける：密着した英雄を" + n("恐怖の形相") + "で" + t("{e_fear}秒") + cc("恐怖") + "、それ以外は" + n("深淵の眼差し") +
                  "（" + t("{e_root}秒") + cc("スネア") + "）と" + n("粉砕の牙") + "（噛みつき{e_slow}%スロウ）を交互に。各" +
                  mag("e_dmg", "e_ratio") + "の魔法ダメージ。",
        "ult": "英雄へ絵の具を放ち、足元に絵画を" + t("{r_t}秒") + "広げて燃やし{r_slow}%スロウ、最後に爆発して" + mag("r_dmg", "r_ratio") +
               "の魔法ダメージ。",
        "names": ("題材: 厄災", "題材: 苦悩", "絶望の渦"),
    },
}

C = "league_hwei_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (attacks lower: they come often, the burn and the
# shield on every Torment cast low), the voice as the other heroes'
SOUNDS = {f"league_hwei_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("p_burst", 0.75), ("q_q", 0.8), ("q_q_hit", 0.75), ("q_w", 0.8), ("q_w_hit", 0.8),
    ("q_e", 0.8), ("q_e_hit", 0.75), ("q_e_burn", 0.5), ("e_q", 0.75), ("e_w", 0.75), ("e_e", 0.75), ("e_hit", 0.7),
    ("w_ww", 0.55), ("r", 0.85), ("r_canvas", 0.7), ("r_burst", 0.9), ("r_hit", 0.75), ("vo_q", 0.85),
    ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("sig_dmg", "sig_ratio", "w_ms", "w_sh", "w_sh_r", "q_w_dmg", "q_w_ratio", "q_w_cc",
                           "q_w_cc_r", "q_q_dmg", "q_q_ratio", "q_q_hp", "q_e_slow", "e_dmg", "e_ratio", "e_slow",
                           "r_slow", "r_dmg", "r_ratio")}
    for k in ("sig_t", "e_fear", "e_root", "r_t"):
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
    if "Hwei" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Hwei. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
