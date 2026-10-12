"""Gragas's text (5 languages), sound_info files and his keys in the shared files, numbers from build_gragas.P.

    python tools/kit/setup_gragas.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_gragas in every language, description + skill_name),
sound/sfx/league_gragas_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.96.0, Gragas named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (古拉加斯 / 酒桶; 欢乐时光, 滚动酒桶, 醉酒狂暴, 肉弹冲击, 爆破酒桶; the client swaps
name and title) and Data Dragon 16.20.1 (zh_TW 古拉格斯 / 歡樂時光 / 滾動酒桶 / 醉酒狂暴 / 肉彈衝擊 / 爆破酒桶, ja グラガス /
ハッピーアワー / タル転がし / 飲みすぎ注意 / ボディスラム / ワシの奢りじゃ！, ko 그라가스 / 서비스 시간 / 술통 굴리기 / 취중 분노 /
몸통 박치기 / 술통 폭발). Slots: skill = Q, skill2 = E (Drunken Rage, W, told in its text), ult = R; the passive is told
in the attack's text. No combo sentence in any text (the user's rule). No `league_gragas_attack` sound: the engine would
play it at the start of every attack; the punch plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_gragas import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_gragas"
VERSION = "0.96.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7dd87dff>"      # heals
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 2, "y": -18}, "center": {"x": 0, "y": -12}}


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ratio}}%{E}"


HEAL = "{p_heal}/{p_heal3} + " + APi + "{p_ap}%"

TEXT = {
    "zh-hans": {
        "name": "古拉加斯",
        "attack": O + "欢乐时光" + E + "：每次施放技能先喝一口，回复" + G + HEAL + "生命" + E + "（3级起用后者），之后" + A + "{p_cd}秒" + E +
                  "内不再触发。",
        "skill": "扔出酒桶，落地" + A + "{q_wait}秒" + E + "后爆炸，周围敌人受到" + mag("q") + M + "魔法伤害" + E + "并" + R + "减速{q_slow}%" + E + A +
                 "{q_slow_t}秒" + E + "。",
        "skill2": "冲向敌人，撞到第一个敌人停下：周围敌人受到" + mag("e") + M + "魔法伤害" + E + "并" + R + "眩晕{e_stun}秒" + E + "，撞中返还部分冷却。" +
                  O + "醉酒狂暴" + E + "：随后喝酒，" + A + "{w_dr_t}秒" + E + "内受到伤害降低{w_dr}%，下次普攻对周围敌人造成" + mag("w") + M + "魔法伤害" +
                  E + "，英雄另受{w_hp}%最大生命真实伤害。",
        "ult": "向一名敌方英雄扔出爆破酒桶：周围敌人受到" + mag("r") + M + "魔法伤害" + E + "，并被" + R + "炸飞" + E + "到古拉加斯这边。",
        "names": ("滚动酒桶", "肉弹冲击", "爆破酒桶"),
    },
    "zh-hant": {
        "name": "古拉格斯",
        "attack": O + "歡樂時光" + E + "：每次施放技能先喝一口，回復" + G + HEAL + "生命" + E + "（3級起用後者），之後" + A + "{p_cd}秒" + E +
                  "內不再觸發。",
        "skill": "扔出酒桶，落地" + A + "{q_wait}秒" + E + "後爆炸，周圍敵人受到" + mag("q") + M + "魔法傷害" + E + "並" + R + "緩速{q_slow}%" + E + A +
                 "{q_slow_t}秒" + E + "。",
        "skill2": "衝向敵人，撞到第一個敵人停下：周圍敵人受到" + mag("e") + M + "魔法傷害" + E + "並" + R + "暈眩{e_stun}秒" + E + "，撞中返還部分冷卻。" +
                  O + "醉酒狂暴" + E + "：隨後喝酒，" + A + "{w_dr_t}秒" + E + "內受到傷害降低{w_dr}%，下次普攻對周圍敵人造成" + mag("w") + M + "魔法傷害" +
                  E + "，英雄另受{w_hp}%最大生命真實傷害。",
        "ult": "向一名敵方英雄扔出爆破酒桶：周圍敵人受到" + mag("r") + M + "魔法傷害" + E + "，並被" + R + "炸飛" + E + "到古拉格斯這邊。",
        "names": ("滾動酒桶", "肉彈衝擊", "爆破酒桶"),
    },
    "en": {
        "name": "Gragas",
        "attack": O + "Happy Hour" + E + ": every skill starts with a swig that heals " + G + HEAL + E + " (the second from level 3), "
                  "then rests " + A + "{p_cd}s" + E + ".",
        "skill": "Rolls a barrel that bursts " + A + "{q_wait}s" + E + " after it lands: " + mag("q") + " " + M + "magic damage" + E + " round it and a " +
                 R + "{q_slow}% slow" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "Charges and stops on the first enemy in his way: " + mag("e") + " " + M + "magic damage" + E + " round him and a " + R +
                  "{e_stun}s stun" + E + "; a hit returns part of the cooldown. " + O + "Drunken Rage" + E + ": then he drinks - {w_dr}% less "
                  "damage for " + A + "{w_dr_t}s" + E + ", and his next attack deals " + mag("w") + " " + M + "magic damage" + E + " round him, "
                  "champions also {w_hp}% max health as true damage.",
        "ult": "Hurls his cask at an enemy champion: " + mag("r") + " " + M + "magic damage" + E + " round it, and the enemies are " + R +
               "blown toward him" + E + ".",
        "names": ("Barrel Roll", "Body Slam", "Explosive Cask"),
    },
    "ko": {
        "name": "그라가스",
        "attack": O + "서비스 시간" + E + ": 스킬을 쓸 때마다 한 모금 마셔 " + G + HEAL + E + " 회복 (3레벨부터 뒤의 값). 이후 " + A + "{p_cd}초" + E +
                  " 동안 발동하지 않음.",
        "skill": "술통을 굴려 착지 " + A + "{q_wait}초" + E + " 후 폭발, 주변 적에게 " + mag("q") + " " + M + "마법 피해" + E + "와 " + A + "{q_slow_t}초" +
                 E + " " + R + "{q_slow}% 둔화" + E + ".",
        "skill2": "적에게 돌진해 처음 부딪힌 적에서 멈춤: 주변 적에게 " + mag("e") + " " + M + "마법 피해" + E + "와 " + R + "{e_stun}초 기절" + E +
                  ", 적중 시 재사용 대기시간 일부 반환. " + O + "취중 분노" + E + ": 이어서 술을 마셔 " + A + "{w_dr_t}초" + E + " 동안 받는 피해 {w_dr}% "
                  "감소, 다음 기본 공격이 주변 적에게 " + mag("w") + " " + M + "마법 피해" + E + ", 챔피언은 최대 체력 {w_hp}% 고정 피해 추가.",
        "ult": "적 챔피언에게 술통을 던져 주변 적에게 " + mag("r") + " " + M + "마법 피해" + E + "를 입히고 " + R + "그라가스 쪽으로 날려 보냄" + E + ".",
        "names": ("술통 굴리기", "몸통 박치기", "술통 폭발"),
    },
    "ja": {
        "name": "グラガス",
        "attack": O + "ハッピーアワー" + E + "：スキル使用時にひと口飲み、" + G + HEAL + E + "回復（レベル3から後者）。その後" + A + "{p_cd}秒" + E +
                  "は発動しない。",
        "skill": "タルを転がし、着地" + A + "{q_wait}秒" + E + "後に爆発。周囲の敵に" + mag("q") + "の" + M + "魔法ダメージ" + E + "と" + A + "{q_slow_t}秒" +
                 E + R + "{q_slow}%スロウ" + E + "。",
        "skill2": "敵に突進し最初に当たった敵で止まる：周囲の敵に" + mag("e") + "の" + M + "魔法ダメージ" + E + "と" + R + "{e_stun}秒スタン" + E +
                  "、命中時CD一部回復。" + O + "飲みすぎ注意" + E + "：続けて飲み、" + A + "{w_dr_t}秒" + E + "間被ダメージ{w_dr}%軽減、次の通常攻撃が"
                  "周囲の敵に" + mag("w") + "の" + M + "魔法ダメージ" + E + "、チャンピオンには最大体力の{w_hp}%確定ダメージ。",
        "ult": "敵チャンピオンにタルを投げつけ、周囲の敵に" + mag("r") + "の" + M + "魔法ダメージ" + E + "を与え、" + R + "グラガスの方へ吹き飛ばす" + E + "。",
        "names": ("タル転がし", "ボディスラム", "ワシの奢りじゃ！"),
    },
}

C = "league_gragas_sfx_"
S_ = "league_gragas_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.4, 0.0), ("p", "p", 0.45, 0.0), ("q", "q", 0.5, 0.0),
    ("q_boom", "q_boom", 0.6, 0.0), ("w", "w", 0.5, 0.0), ("w_hit", "w_hit", 0.6, 0.0), ("e", "e", 0.55, 0.0),
    ("e_hit", "e_hit", 0.6, 0.0), ("r", "r", 0.55, 0.0), ("r_boom", "r_boom", 0.7, 0.0), ("r_hit", "a_hit", 0.3, 0.0),
    ("vo_q", "vo_q", 0.85, 0.0), ("vo_w", "vo_w", 0.85, 0.0), ("vo_e", "vo_e", 0.85, 0.0), ("vo_r", "vo_r", 0.9, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_heal", "p_heal3", "p_ap", "q_dmg", "q_ratio", "q_slow", "e_dmg", "e_ratio", "w_dr", "w_dmg",
                           "w_ratio", "w_hp", "r_dmg", "r_ratio")}
    v.update({k: secs(p[k]) for k in ("p_cd", "q_wait", "q_slow_t", "e_stun", "w_dr_t")})
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
    if "Gragas" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Gragas. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
