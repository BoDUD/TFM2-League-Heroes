"""Draven's text (5 languages), sound_info files and his keys in the shared files, numbers from build_draven.P.

    python tools/kit/setup_draven.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in dv/league): text/champion.i18n (league_draven in every language, description + skill_name),
sound/sfx/league_draven_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.88.0, Draven named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/dv/rst.py: 德莱文 / 德莱文联盟, 旋转飞斧, 血性冲刺, 开道利斧, 冷血追命) and Data
Dragon 16.19.1 (zh_TW 達瑞文 / 瑞文聯盟 / 迴旋飛斧 / 好戲上場 / 給我閃！ / 迴轉死神, ja ドレイヴン / リーグ・オブ・ドレイヴン / 回転斬斧 /
血の疼き / 薙ぎ払い / 死の車輪, ko 드레이븐 / 드레이븐의 리그 / 회전 도끼 / 광기의 피 / 비켜서라 / 죽음의 소용돌이).
The slot names: skill = Q, skill2 = E, ult = R; the passive and the automatic W are told in the attack's text. No combo
sentence in any text (the user's rule): the combos live in build_draven.py and the README.
No `league_draven_attack` sound: the engine would play it at the start of every attack; the throw plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_draven import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_draven"
VERSION = "0.88.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control, shred
T = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 6, "y": -32}, "center": {"x": 0, "y": -12}}  # placeholder until the sprite


def phy(k):
    return f"{O}{{{k}_dmg}}{E} + {ADi}{O}{{{k}_ratio}}%{E}"


def tru(k, r):
    return f"{T}{{{k}}}{E} + {ADi}{T}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "德莱文",
        "attack": O + "德莱文联盟" + E + "：每接住一把斧头+1层崇拜（最多{p_n}层，每层攻击+{p_atk}），用斧头击杀英雄时兑现：每层回复{p_heal}生命，" +
                  "攻速+{p_as}%" + A + "{p_t}秒" + E + "。" + O + "血性冲刺" + E + "（自动，" + A + "{w_cd}秒" + E + "）：对英雄出手时移速+{w_ms}%、" +
                  "攻速+{w_as}%，接住斧头即刷新。",
        "skill": "手中转起一把飞斧（最多2把），下次攻击额外造成" + phy("q") + "伤害。斧头弹回空中，" + A + "{q_fly}秒" + E +
                 "后落在他身边随机一处，他会跑进落点圈接住，继续旋转。",
        "skill2": "掷出一对贯穿的斧刃，造成" + phy("e") + "伤害，" + R + "击退" + E + "敌人并" + R + "减速{e_slow}%" + E + A + "{e_slow_t}秒" + E + "。",
        "ult": "向远处交战中的英雄掷出两把宽大的巨斧，飞得很远，贯穿路上的敌人造成" + phy("r") + "伤害；碰到第一个英雄（或飞到尽头）后折返，回程再造成一次伤害。",
        "names": ("旋转飞斧", "开道利斧", "冷血追命"),
    },
    "zh-hant": {
        "name": "達瑞文",
        "attack": O + "瑞文聯盟" + E + "：每接住一把斧頭+1層崇拜（最多{p_n}層，每層攻擊+{p_atk}），用斧頭擊殺英雄時兌現：每層回復{p_heal}生命，" +
                  "攻速+{p_as}%" + A + "{p_t}秒" + E + "。" + O + "好戲上場" + E + "（自動，" + A + "{w_cd}秒" + E + "）：對英雄出手時移速+{w_ms}%、" +
                  "攻速+{w_as}%，接住斧頭即刷新。",
        "skill": "手中轉起一把飛斧（最多2把），下次攻擊額外造成" + phy("q") + "傷害。斧頭彈回空中，" + A + "{q_fly}秒" + E +
                 "後落在他身邊隨機一處，他會跑進落點圈接住，繼續旋轉。",
        "skill2": "擲出一對貫穿的斧刃，造成" + phy("e") + "傷害，" + R + "擊退" + E + "敵人並" + R + "緩速{e_slow}%" + E + A + "{e_slow_t}秒" + E + "。",
        "ult": "向遠處交戰中的英雄擲出兩把寬大的巨斧，飛得很遠，貫穿路上的敵人造成" + phy("r") + "傷害；碰到第一個英雄（或飛到盡頭）後折返，回程再造成一次傷害。",
        "names": ("迴旋飛斧", "給我閃！", "迴轉死神"),
    },
    "en": {
        "name": "Draven",
        "attack": "Throws axes. " + O + "League of Draven" + E + ": each caught axe gives 1 Adoration (up to {p_n}, +{p_atk} attack each); an "
                  "axe kill on a champion cashes them in: {p_heal} health each and +{p_as}% attack speed for " + A + "{p_t}s" + E + ". " + O +
                  "Blood Rush" + E + " (automatic, " + A + "{w_cd}s" + E + "): attacking a champion gives +{w_ms}% move speed and +{w_as}% "
                  "attack speed; a catch resets it.",
        "skill": "Spins an axe in his hand (up to 2): his next attack deals " + phy("q") + " bonus damage. The axe bounces up and lands "
                 "at a random spot near him after " + A + "{q_fly}s" + E + "; he runs into the circle to catch it, still spinning.",
        "skill2": "Throws a pair of piercing axes for " + phy("e") + ", " + R + "knocking enemies back" + E + " and " + R + "slowing {e_slow}%" + E +
                  " for " + A + "{e_slow_t}s" + E + ".",
        "ult": "Hurls two huge, wide axes at a fighting champion far away; they fly a long way, dealing " + phy("r") + " to every "
               "enemy passed, turn at the first champion (or the end) and fly back, dealing it again.",
        "names": ("Spinning Axe", "Stand Aside", "Whirling Death"),
    },
    "ko": {
        "name": "드레이븐",
        "attack": O + "드레이븐의 리그" + E + ": 도끼를 받을 때마다 숭배 1중첩(최대 {p_n}, 중첩당 공격력 +{p_atk}). 도끼로 챔피언을 처치하면 소모: "
                  "중첩당 체력 {p_heal} 회복, " + A + "{p_t}초" + E + " 동안 공격 속도 +{p_as}%. " + O + "광기의 피" + E + "(자동, " + A + "{w_cd}초" + E +
                  "): 챔피언 공격 시 이동 속도 +{w_ms}%, 공격 속도 +{w_as}%, 도끼를 받으면 초기화.",
        "skill": "손에서 도끼를 회전시킴(최대 2개): 다음 공격이 " + phy("q") + "의 추가 피해. 도끼는 튕겨 올라 " + A + "{q_fly}초" + E +
                 " 뒤 주변 무작위 위치에 떨어지며, 원 안으로 달려가 받아서 계속 회전.",
        "skill2": "관통하는 도끼 한 쌍을 던져 " + phy("e") + "의 피해, " + R + "밀쳐내고" + E + " " + A + "{e_slow_t}초" + E + " 동안 " + R +
                  "{e_slow}% 둔화" + E + ".",
        "ult": "멀리 교전 중인 챔피언에게 넓고 거대한 도끼 두 개를 던져 멀리까지 날아가며 지나는 적에게 " + phy("r") + "의 피해. 첫 챔피언(또는 끝)에서 "
               "되돌아와 다시 피해.",
        "names": ("회전 도끼", "비켜서라", "죽음의 소용돌이"),
    },
    "ja": {
        "name": "ドレイヴン",
        "attack": O + "リーグ・オブ・ドレイヴン" + E + "：斧をキャッチするたび崇拝+1（最大{p_n}、1つにつき攻撃力+{p_atk}）。斧でチャンピオンを倒すと換金：" +
                  "1つにつき体力{p_heal}回復、" + A + "{p_t}秒" + E + "攻撃速度+{p_as}%。" + O + "血の疼き" + E + "（自動、" + A + "{w_cd}秒" + E +
                  "）：チャンピオン攻撃時に移動速度+{w_ms}%、攻撃速度+{w_as}%、キャッチでリセット。",
        "skill": "手の中で斧を回す（最大2本）：次の攻撃が" + phy("q") + "の追加ダメージ。斧は跳ね上がり" + A + "{q_fly}秒" + E +
                 "後に周囲のランダムな位置に落ち、円に走り込んでキャッチし回し続ける。",
        "skill2": "貫通する斧を2本投げ" + phy("e") + "のダメージ、" + R + "ノックバック" + E + "と" + A + "{e_slow_t}秒" + E + R + "{e_slow}%スロウ" + E + "。",
        "ult": "遠くで交戦中のチャンピオンへ幅広の巨大な斧を2本投げ、遠くまで飛んで通過した敵に" + phy("r") + "。最初のチャンピオン（または端）で"
               "折り返し、戻りでも同じダメージ。",
        "names": ("回転斬斧", "薙ぎ払い", "死の車輪"),
    },
}

C = "league_draven_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
S = "league_draven_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    S + "a_throw": [(C + "a_throw", 0.45, 0.0)],
    S + "a_hit": [(C + "a_hit", 0.35, 0.0)],
    S + "q": [(C + "q", 0.45, 0.0)],
    S + "q_throw": [(C + "q_throw", 0.5, 0.0)],
    S + "q_hit": [(C + "q_hit", 0.45, 0.0)],
    S + "q_catch": [(C + "q_catch", 0.5, 0.0)],
    S + "q_lost": [(C + "q_lost", 0.4, 0.0)],
    S + "w": [(C + "w", 0.5, 0.0)],
    S + "e": [(C + "e", 0.45, 0.0)],
    S + "e_throw": [(C + "e_throw", 0.5, 0.0)],
    S + "e_hit": [(C + "e_hit", 0.45, 0.0)],
    S + "r": [(C + "r", 0.5, 0.0)],
    S + "r_throw": [(C + "r_throw", 0.55, 0.0)],
    S + "r_hit": [(C + "r_hit", 0.5, 0.0)],
    S + "r_turn": [(C + "r_turn", 0.5, 0.0)],
    S + "p_cash": [(C + "p_cash", 0.55, 0.0)],
    S + "vo_q": [(C + "vo_q", 0.8, 0.0)],
    S + "vo_w": [(C + "vo_w", 0.8, 0.0)],
    S + "vo_e": [(C + "vo_e", 0.8, 0.0)],
    S + "vo_r": [(C + "vo_r", 0.8, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    keys = ("p_n", "p_atk", "p_heal", "p_as", "w_ms", "w_as", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_slow", "r_dmg",
            "r_ratio")
    v = {k: p[k] for k in keys}
    v.update({k: secs(p[k]) for k in ("p_t", "w_cd", "q_fly", "e_slow_t")})
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
    if "Draven" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Draven. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
