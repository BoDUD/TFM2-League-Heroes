"""Zoe's text (5 languages), sound_info files and her keys in the shared files, numbers from build_zoe.P.

    python tools/kit/setup_zoe.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_zoe in every language, description + skill_name),
sound/sfx/league_zoe_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Zoe named). Only her keys change in the shared files. JSON: indent 2,
CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 佐伊 (暮光星灵): 烟火四射！, 飞星乱入！, 窃法巧手, 催眠气泡, 折返跃迁; zh_TW 柔依 (暮光星靈):
閃耀星火, 星迴百轉, 法術竊盜, 沉睡夢域, 星界躍動; ja ゾーイ: スパークル！, パドルスター, スペルシーフ, スリープバブル,
ポータルジャンプ; ko 조이: 반짝반짝!, 통통별, 주문도둑, 헤롱헤롱쿨쿨방울, 차원 넘기.
Slots: skill = Q Paddle Star, skill2 = E Sleepy Trouble Bubble, ult = R Portal Jump (its star and W Spell Thief's
missiles in the ult's text); the passive More Sparkles! is in the attack's text. No combo sentence in any text (the
user's rule). The main pack's rules are the ones written (the star's damage by distance tiers, the sleep a fixed stun
whose first star hit is doubled); the add-on league_zoe wakes on any damage and drops Spell Thief's shards, and says
so itself.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zoe import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_zoe"
VERSION = "0.165.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point between her eyes (23.7 px over the soles; tfm2_ase.py face finds her crown 33 px up:
# lint_mod allows 10 under the crown; ppu_restyle face_to the same)
VIEW = {"face": {"x": 1, "y": -24}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "佐伊",
        "attack": "射出一颗小星星。" + O + "烟火四射！" + E + "：每放一个技能，下一次普攻多造成" + mag("p_dmg", "p_ratio") + "魔法伤害。",
        "skill": "掷出一颗飞星，打中第一个敌人造成" + mag("q_dmg", "q_ratio") + "魔法伤害；飞得越远伤害越高，最远" + A + "{q_far}%" + E + "。",
        "skill2": "踢出气泡，打中敌方英雄造成" + mag("e_dmg", "e_ratio") + "魔法伤害，" + R + "困倦" + E + "（减速{e_slow}%）" + A + "{e_drowsy}秒" +
                  E + "后" + R + "昏睡" + E + A + "{e_sleep}秒" + E + "；没打中就留在原地。昏睡中第一次被飞星打中伤害翻倍。",
        "ult": "跳进传送门闪向敌方英雄，掷出飞星造成" + mag("r_dmg", "r_ratio") + "魔法伤害；" + O + "窃法巧手" + E + "：再射{w_n}颗飞弹，每颗" +
               mag("w_dmg", "w_ratio") + "，加速{w_ms}%。" + A + "{r_back}秒" + E + "后跳回原地。",
        "names": ("飞星乱入！", "催眠气泡", "折返跃迁"),
    },
    "zh-hant": {
        "name": "柔依",
        "attack": "射出一顆小星星。" + O + "閃耀星火" + E + "：每放一個技能，下一次普攻多造成" + mag("p_dmg", "p_ratio") + "魔法傷害。",
        "skill": "擲出一顆飛星，打中第一個敵人造成" + mag("q_dmg", "q_ratio") + "魔法傷害；飛得越遠傷害越高，最遠" + A + "{q_far}%" + E + "。",
        "skill2": "踢出泡泡，打中敵方英雄造成" + mag("e_dmg", "e_ratio") + "魔法傷害，" + R + "睏倦" + E + "（緩速{e_slow}%）" + A + "{e_drowsy}秒" +
                  E + "後" + R + "沉睡" + E + A + "{e_sleep}秒" + E + "；沒打中就留在原地。沉睡中第一次被飛星打中傷害加倍。",
        "ult": "跳進傳送門閃向敵方英雄，擲出飛星造成" + mag("r_dmg", "r_ratio") + "魔法傷害；" + O + "法術竊盜" + E + "：再射{w_n}顆飛彈，每顆" +
               mag("w_dmg", "w_ratio") + "，加速{w_ms}%。" + A + "{r_back}秒" + E + "後跳回原地。",
        "names": ("星迴百轉", "沉睡夢域", "星界躍動"),
    },
    "en": {
        "name": "Zoe",
        "attack": "Throws a little star. " + O + "More Sparkles!" + E + ": after each spell her next attack deals " + mag("p_dmg", "p_ratio") +
                  " " + M + "magic damage" + E + " more.",
        "skill": "Throws a star at the first enemy hit for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + "; the farther it flies "
                 "the harder it hits, up to " + A + "{q_far}%" + E + ".",
        "skill2": "Kicks a bubble: the enemy champion hit takes " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + ", turns " + R +
                  "drowsy" + E + " (slowed {e_slow}%) for " + A + "{e_drowsy}s" + E + ", then falls " + R + "asleep" + E + " for " + A +
                  "{e_sleep}s" + E + ". A miss leaves it lying as a trap. A sleeper's first star hit deals double.",
        "ult": "Jumps through a portal toward an enemy champion and throws a star for " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" +
               E + ". " + O + "Spell Thief" + E + ": {w_n} missiles follow, " + mag("w_dmg", "w_ratio") + " each, and she gains {w_ms}% "
               "move speed. After " + A + "{r_back}s" + E + " she pops back.",
        "names": ("Paddle Star!", "Sleepy Trouble Bubble", "Portal Jump"),
    },
    "ko": {
        "name": "조이",
        "attack": "작은 별을 던진다. " + O + "반짝반짝!" + E + ": 스킬을 쓸 때마다 다음 기본 공격이 " + mag("p_dmg", "p_ratio") + " 마법 피해 추가.",
        "skill": "별을 던져 처음 맞힌 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해. 멀리 날아갈수록 피해가 커져 최대 " + A + "{q_far}%" + E + ".",
        "skill2": "방울을 차서 맞힌 적 챔피언에게 " + mag("e_dmg", "e_ratio") + " 마법 피해, " + A + "{e_drowsy}초" + E + " " + R + "졸음" + E +
                  "({e_slow}% 둔화) 뒤 " + A + "{e_sleep}초" + E + " " + R + "수면" + E + ". 빗나가면 그 자리에 남는다. 잠든 적이 처음 맞는 별은 피해 2배.",
        "ult": "차원문을 넘어 적 챔피언 쪽으로 이동해 별을 던져 " + mag("r_dmg", "r_ratio") + " 마법 피해. " + O + "주문도둑" + E + ": 투사체 {w_n}개, "
               "개당 " + mag("w_dmg", "w_ratio") + ", 이동 속도 +{w_ms}%. " + A + "{r_back}초" + E + " 뒤 제자리로.",
        "names": ("통통별", "헤롱헤롱쿨쿨방울", "차원 넘기"),
    },
    "ja": {
        "name": "ゾーイ",
        "attack": "小さな星を投げる。" + O + "スパークル！" + E + "：スキルを使うたび次の通常攻撃に" + mag("p_dmg", "p_ratio") + "の魔法ダメージ追加。",
        "skill": "星を投げ、最初に当たった敵に" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。遠くまで飛ぶほど強く、最大" + A + "{q_far}%" + E + "。",
        "skill2": "泡を蹴り、当たった敵チャンピオンに" + mag("e_dmg", "e_ratio") + "の魔法ダメージ、" + A + "{e_drowsy}秒" + E + R + "まどろみ" + E +
                  "（{e_slow}%スロウ）の後" + A + "{e_sleep}秒" + E + R + "睡眠" + E + "。外れるとその場に残る。眠った敵に最初に当たる星は2倍。",
        "ult": "ポータルを抜けて敵チャンピオンの方へ跳び、星を投げて" + mag("r_dmg", "r_ratio") + "の魔法ダメージ。" + O + "スペルシーフ" + E +
               "：弾{w_n}発、1発" + mag("w_dmg", "w_ratio") + "、移動速度+{w_ms}%。" + A + "{r_back}秒" + E + "後に元の場所へ戻る。",
        "names": ("パドルスター", "スリープバブル", "ポータルジャンプ"),
    },
}

C = "league_zoe_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
# the sfx raised toward Lux's 0.8 (「佐伊的音效也照奥莉安娜的办法调响」; attacks lower: they come often), the voice as it was
SOUNDS = {f"league_zoe_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("p", 0.6), ("p_hit", 0.65), ("q", 0.8), ("q_fly", 0.75), ("q_hit", 0.85),
    ("e", 0.8), ("e_fly", 0.75), ("e_hit", 0.8), ("e_pop", 0.8), ("e_sleep", 0.8), ("e_wake", 0.9),
    ("r", 0.85), ("r_back", 0.8), ("w_shot", 0.7), ("w_hit", 0.75),
    ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ratio", "q_dmg", "q_ratio", "q_far", "e_dmg", "e_ratio", "e_slow", "r_dmg",
                           "r_ratio", "w_n", "w_dmg", "w_ratio", "w_ms")}
    for k in ("e_drowsy", "e_sleep", "r_back"):
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
    if "Zoe" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Zoe. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
