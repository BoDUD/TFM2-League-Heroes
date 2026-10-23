"""Azir's text (5 languages), sound_info files and his keys in the shared files, numbers from build_azir.P.

    python tools/kit/setup_azir.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_azir in every language, description + skill_name),
sound/sfx/league_azir_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Azir named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 阿兹尔 (沙漠皇帝): 恕瑞玛的传承; 狂沙猛攻, 沙兵现身, 流沙移形, 禁军之墙; zh_TW 阿祈爾 (蘇瑞瑪砂皇):
蘇瑞瑪遺跡; 砂影霸者, 砂漠禁軍, 護砂瞬身, 空砂防壁; ja アジール: シュリーマの遺産; 征服の勅命, 目覚めよ！, 流砂の衝撃, 皇帝の分砂嶺;
ko 아지르: 슈리마의 유산; 사막의 맹습, 일어나라!, 신기루, 황제의 진영.
Slots: skill = Conquering Sands, skill2 = Shifting Sands, ult = Emperor's Divide; Arise! (the soldiers) in the attack's
text. The Sun Disc is the add-on's (addons/league_azir make_override.py adds its sentence). No combo sentence in any text
(the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_azir import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_azir"
VERSION = "0.201.0"     # the next free number above main 0.200.1 (Varus #481) (2026-10-23)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # shields
E = "<>"
# champion_view: the face point on his helmet's glowing eye (ppu_restyle.py RESTYLE face_to) and the ban/pick card (set at
# export: tools/art/bp_card_audit.py)
VIEW = {"face": {"x": 2, "y": -30}, "center": {"x": 0, "y": -18}, "banpick_center": {"x": 0, "y": -9}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def sh(d, r):
    return f"{G}{{{d}}}{E} + {APi}{G}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


TEXT = {
    "zh-hans": {
        "name": "阿兹尔",
        "attack": n("沙兵现身") + "：普攻每" + t("{p_cd}秒") + "在目标处召出一个黄沙士兵（最多" + t("3") + "个，存在" + t("{s_life}秒") +
                  "），士兵代他刺击，造成" + mag("s_dmg", "s_ap") + "魔法伤害；士兵都够不着时他自己射出沙光。",
        "skill": "所有黄沙士兵冲向目标，沿途造成" + mag("q_dmg", "q_ap") + "魔法伤害并" + cc("减速") + "{q_slow}%，落地马上刺击；没有士兵时在目标处召出一个。",
        "skill2": "身边有士兵才能施放：获得" + sh("e_sh", "e_ap") + "护盾，大招就绪时冲向敌方英雄，造成" + mag("e_dmg", "e_ratio") +
                  "魔法伤害并召出一个士兵；被敌方英雄贴身时改为后跳。",
        "ult": "一排禁军举盾冲锋，造成" + mag("r_dmg", "r_ratio") + "魔法伤害并" + cc("击退") + "敌人；刚用流沙移形冲到英雄身上时，先绕到他身后，再把他推回己方。",
        "names": ("狂沙猛攻", "流沙移形", "禁军之墙"),
    },
    "zh-hant": {
        "name": "阿祈爾",
        "attack": n("砂漠禁軍") + "：普攻每" + t("{p_cd}秒") + "在目標處召出一名砂兵（最多" + t("3") + "名，存在" + t("{s_life}秒") +
                  "），砂兵代他刺擊，造成" + mag("s_dmg", "s_ap") + "魔法傷害；砂兵都搆不著時他自己射出砂光。",
        "skill": "所有砂兵衝向目標，沿途造成" + mag("q_dmg", "q_ap") + "魔法傷害並" + cc("緩速") + "{q_slow}%，落地立刻刺擊；沒有砂兵時在目標處召出一名。",
        "skill2": "身邊有砂兵才能施放：獲得" + sh("e_sh", "e_ap") + "護盾，大絕就緒時衝向敵方英雄，造成" + mag("e_dmg", "e_ratio") +
                  "魔法傷害並召出一名砂兵；被敵方英雄貼身時改為後跳。",
        "ult": "一排禁軍舉盾衝鋒，造成" + mag("r_dmg", "r_ratio") + "魔法傷害並" + cc("擊退") + "敵人；剛用護砂瞬身衝到英雄身上時，先繞到他身後，再把他推回己方。",
        "names": ("砂影霸者", "護砂瞬身", "空砂防壁"),
    },
    "en": {
        "name": "Azir",
        "attack": n("Arise!") + ": every " + t("{p_cd}s") + " his attack raises a sand soldier at the target (" + t("3") + " at most, " +
                  t("{s_life}s") + "); his soldiers stab for him, " + mag("s_dmg", "s_ap") + " magic damage. With none in "
                  "reach he shoots a sand bolt himself.",
        "skill": "Every soldier charges at the target, " + mag("q_dmg", "q_ap") + " magic damage on the way and a {q_slow}% " +
                 cc("slow") + "; they stab at once on arrival. With none standing, one rises there.",
        "skill2": "Only with a soldier up: a shield of " + sh("e_sh", "e_ap") + ", then, with his ultimate ready, a dash onto an "
                  "enemy champion for " + mag("e_dmg", "e_ratio") + " magic damage and one more soldier. Dived by a champion, "
                  "he hops back instead.",
        "ult": "A wall of guards charges out: " + mag("r_dmg", "r_ratio") + " magic damage and " + cc("knocks back") +
               " the enemies. Right after Shifting Sands onto a champion he steps behind it first and drives it toward his team.",
        "names": ("Conquering Sands", "Shifting Sands", "Emperor's Divide"),
    },
    "ko": {
        "name": "아지르",
        "attack": n("일어나라!") + ": " + t("{p_cd}초") + "마다 기본 공격이 대상 위치에 모래 병사를 세운다(최대 " + t("3") + "명, " +
                  t("{s_life}초") + "). 병사가 대신 찔러 " + mag("s_dmg", "s_ap") + " 마법 피해; 닿는 병사가 없으면 직접 모래 빛을 쏜다.",
        "skill": "모든 병사가 대상에게 돌진해 지나는 길에 " + mag("q_dmg", "q_ap") + " 마법 피해와 {q_slow}% " + cc("둔화") +
                 ", 도착하자마자 찌른다. 병사가 없으면 그곳에 하나를 세운다.",
        "skill2": "병사가 있을 때만: " + sh("e_sh", "e_ap") + " 보호막, 궁극기가 준비되면 적 챔피언에게 돌진해 " + mag("e_dmg", "e_ratio") +
                  " 마법 피해와 병사 하나 추가. 챔피언이 붙으면 대신 뒤로 뛴다.",
        "ult": "근위대가 방패를 들고 돌격해 " + mag("r_dmg", "r_ratio") + " 마법 피해와 " + cc("밀쳐내기") +
               ". 신기루로 챔피언에게 막 붙었다면 먼저 그 뒤로 돌아가 아군 쪽으로 밀어 보낸다.",
        "names": ("사막의 맹습", "신기루", "황제의 진영"),
    },
    "ja": {
        "name": "アジール",
        "attack": n("目覚めよ！") + "：通常攻撃が" + t("{p_cd}秒") + "ごとに対象の所に砂兵を呼ぶ（最大" + t("3") + "体、" + t("{s_life}秒") +
                  "）。砂兵が代わりに突き" + mag("s_dmg", "s_ap") + "の魔法ダメージ、届く砂兵がいないと自ら砂光を放つ。",
        "skill": "全砂兵が対象へ突撃し、道中" + mag("q_dmg", "q_ap") + "の魔法ダメージと{q_slow}%" + cc("スロウ") + "、着くとすぐ突く。砂兵がいなければそこに1体呼ぶ。",
        "skill2": "砂兵がいる時だけ：" + sh("e_sh", "e_ap") + "のシールド、アルティメット準備時は敵英雄へ突進し" + mag("e_dmg", "e_ratio") +
                  "の魔法ダメージと砂兵1体。詰められると後ろへ跳ぶ。",
        "ult": "近衛兵の壁が突撃し" + mag("r_dmg", "r_ratio") + "の魔法ダメージと" + cc("ノックバック") + "。流砂の衝撃で英雄に寄った直後なら、背後へ回り味方側へ押し返す。",
        "names": ("征服の勅命", "流砂の衝撃", "皇帝の分砂嶺"),
    },
}

C = "league_azir_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (the attack and the stab lower: they come often), the
# voice as the other heroes'; d_rise / d_beam are the add-on's Sun Disc
SOUNDS = {f"league_azir_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("s_spawn", 0.6), ("s_stab", 0.5), ("q", 0.75), ("q_land", 0.7), ("q_hit", 0.65),
    ("e", 0.75), ("e_land", 0.8), ("e_hit", 0.7), ("r", 0.85), ("r_wall", 0.9), ("r_hit", 0.7), ("d_rise", 0.8),
    ("d_beam", 0.6), ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("s_dmg", "s_ap", "q_dmg", "q_ap", "q_slow", "e_sh", "e_ap", "e_dmg", "e_ratio", "r_dmg",
                           "r_ratio")}
    for k in ("p_cd", "s_life"):
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
    if "Azir" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'.& ]+?)\. Kits", r", \1 and Azir. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
