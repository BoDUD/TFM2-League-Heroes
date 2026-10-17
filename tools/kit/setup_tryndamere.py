"""Tryndamere's text (5 languages), sound_info files and his keys in the shared files, numbers from build_tryndamere.P.

    python tools/kit/setup_tryndamere.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_tryndamere in every language, description + skill_name),
sound/sfx/league_tryndamere_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.62.0, Tryndamere named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.19.1 (zh_CN 泰达米尔 / 战斗狂怒, 嗜血杀戮, 蔑视, 旋风斩, 无尽怒火; zh_TW 泰達米爾 / 戰鬥狂怒, 嗜血殺戮,
嘲諷, 旋風斬, 無盡怒火; ko 트린다미어 / 격노, 피의 갈망, 조롱의 외침, 회전 베기, 불사의 분노; ja トリンダメア / 戦場の咆哮,
血の欲望, 嘲りの叫び, スピンスラッシュ, 不死の憤激).
No `league_tryndamere_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_tryndamere import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_tryndamere"
VERSION = "0.62.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control, debuffs
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -36}, "center": {"x": 0, "y": -12}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def hl(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "泰达米尔",
        "attack": "挥剑攻击。被动" + O + "战斗狂怒" + E + "：普攻和旋风斩每命中一个敌人得1层怒气，击杀得2层，最多{f_n}层，每层暴击率+" + A +
                  "{f_crit}%" + E + "（暴击造成2倍伤害）；停手{f_top}秒后每秒掉一层。",
        "skill": "旋转着冲过目标，对路径上的所有敌人造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "，每命中一个敌人得1层怒气。",
        "skill2": "向周围的敌方英雄发出蔑视的怒吼，攻击力降低" + R + "{w_ad}%" + E + "，持续" + A + "{w_t}秒" + E + "；离他较远、正要逃开的敌人还会" + R +
                  "减速{w_slow}%" + E + "，持续{w_slow_t}秒。",
        "ult": "被两名以上敌方英雄贴身或连续挨打时爆发：怒气全满，" + A + "{r_t}秒" + E + "内生命不会降到1以下。结束时施放" + O + "嗜血杀戮" + E +
               "，消耗怒气回复" + hl("q_heal", "q_heal_ratio") + "生命，每层怒气再加" + hl("q_per", "q_per_ratio") + "。",
        "names": ("旋风斩", "蔑视", "无尽怒火"),
    },
    "zh-hant": {
        "name": "泰達米爾",
        "attack": "揮劍攻擊。被動" + O + "戰鬥狂怒" + E + "：普攻和旋風斬每命中一個敵人得1層怒氣，擊殺得2層，最多{f_n}層，每層暴擊率+" + A +
                  "{f_crit}%" + E + "（暴擊造成2倍傷害）；停手{f_top}秒後每秒掉一層。",
        "skill": "旋轉著衝過目標，對路徑上的所有敵人造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "，每命中一個敵人得1層怒氣。",
        "skill2": "向周圍的敵方英雄發出輕蔑的怒吼，攻擊力降低" + R + "{w_ad}%" + E + "，持續" + A + "{w_t}秒" + E + "；離他較遠、正要逃開的敵人還會" + R +
                  "緩速{w_slow}%" + E + "，持續{w_slow_t}秒。",
        "ult": "被兩名以上敵方英雄貼身或連續挨打時爆發：怒氣全滿，" + A + "{r_t}秒" + E + "內生命不會降到1以下。結束時施放" + O + "嗜血殺戮" + E +
               "，消耗怒氣回復" + hl("q_heal", "q_heal_ratio") + "生命，每層怒氣再加" + hl("q_per", "q_per_ratio") + "。",
        "names": ("旋風斬", "嘲諷", "無盡怒火"),
    },
    "en": {
        "name": "Tryndamere",
        "attack": "Sword strikes. Passive " + O + "Battle Fury" + E + ": each enemy his attacks and Spinning Slash hit gives a "
                  "stack of Fury, a kill two, up to {f_n}; each stack is " + A + "+{f_crit}%" + E + " critical strike chance "
                  "(crits deal double). Fury drains a stack a second once he stops for {f_top}s.",
        "skill": "Spins through the target, dealing " + phy("e_dmg", "e_ratio") + " " + O + "physical damage" + E + " to every "
                 "enemy in his path and gaining a stack of Fury for each.",
        "skill2": "Mocks the enemy champions around him: " + R + "-{w_ad}%" + E + " attack for " + A + "{w_t}s" + E + ". Those "
                  "farther off, turning to run, are also " + R + "slowed" + E + " by {w_slow}% for {w_slow_t}s.",
        "ult": "When two enemy champions are on him or the blows keep coming: full Fury, and for " + A + "{r_t}s" + E + " his "
               "health cannot fall below 1. As it ends he casts " + O + "Bloodlust" + E + ", spending his Fury to heal " +
               hl("q_heal", "q_heal_ratio") + ", plus " + hl("q_per", "q_per_ratio") + " per stack.",
        "names": ("Spinning Slash", "Mocking Shout", "Undying Rage"),
    },
    "ko": {
        "name": "트린다미어",
        "attack": "검으로 공격합니다. 기본 지속 효과 " + O + "격노" + E + ": 기본 공격과 회전 베기가 적을 맞힐 때마다 분노 1, 처치 시 2 (최대 "
                  "{f_n}). 중첩당 치명타 확률 " + A + "+{f_crit}%" + E + " (치명타는 2배 피해). {f_top}초간 공격하지 않으면 1초마다 1씩 줄어듭니다.",
        "skill": "대상을 지나 회전하며 돌진해 경로의 모든 적에게 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E +
                 "를 입히고, 적중한 적마다 분노 1을 얻습니다.",
        "skill2": "주변 적 챔피언을 조롱해 공격력을 " + A + "{w_t}초" + E + " 동안 " + R + "{w_ad}%" + E + " 낮춥니다. 멀리서 등을 돌린 적은 "
                  "{w_slow_t}초 동안 {w_slow}% " + R + "둔화" + E + "됩니다.",
        "ult": "적 챔피언 둘 이상에게 붙잡히거나 계속 맞으면 발동: 분노가 가득 차고 " + A + "{r_t}초" + E + " 동안 체력이 1 아래로 떨어지지 "
               "않습니다. 끝날 때 " + O + "피의 갈망" + E + "으로 분노를 소모해 " + hl("q_heal", "q_heal_ratio") + ", 중첩당 " +
               hl("q_per", "q_per_ratio") + " 회복합니다.",
        "names": ("회전 베기", "조롱의 외침", "불사의 분노"),
    },
    "ja": {
        "name": "トリンダメア",
        "attack": "剣で攻撃。パッシブ " + O + "戦場の咆哮" + E + "：通常攻撃とスピンスラッシュが敵に当たるたびフューリー1、キルで2（最大{f_n}）。"
                  "1つにつきクリティカル率" + A + "+{f_crit}%" + E + "（クリティカルは2倍）。{f_top}秒攻撃しないと毎秒1つ減る。",
        "skill": "対象を突き抜けて回転斬りし、通り道の全ての敵に" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E +
                 "、当たった敵1体ごとにフューリー1。",
        "skill2": "周囲の敵チャンピオンを嘲り、攻撃力" + R + "-{w_ad}%" + E + "（" + A + "{w_t}秒" + E + "）。離れて背を向けた敵は{w_slow}%の" +
                  R + "スロウ" + E + "（{w_slow_t}秒）。",
        "ult": "敵チャンピオン2体以上に囲まれるか攻撃を受け続けると発動：フューリー最大、" + A + "{r_t}秒" + E + "間体力が1未満にならない。"
               "終わりに" + O + "血の欲望" + E + "でフューリーを消費し" + hl("q_heal", "q_heal_ratio") + "、1つにつき" +
               hl("q_per", "q_per_ratio") + "回復。",
        "names": ("スピンスラッシュ", "嘲りの叫び", "不死の憤激"),
    },
}

C = "league_tryndamere_sfx_"
V = "league_tryndamere_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_tryndamere_a_swing": [(C + "swing", 0.5, 0.0)],
    "league_tryndamere_a_hit": [(C + "hit", 0.4, 0.0)],
    "league_tryndamere_e_cast": [(C + "e", 0.55, 0.0), (V + "e", 0.85, 0.05)],
    "league_tryndamere_e_hit": [(C + "e_hit", 0.35, 0.0)],
    "league_tryndamere_w_shout": [(C + "w", 0.55, 0.0), (V + "w", 0.85, 0.05)],
    "league_tryndamere_r_cast": [(C + "r", 0.6, 0.0), (V + "r", 0.9, 0.05)],
    "league_tryndamere_r_end": [(C + "r_end", 0.5, 0.0)],
    "league_tryndamere_q_heal": [(C + "q", 0.55, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("f_n", "f_crit", "e_dmg", "e_ratio", "w_ad", "w_slow", "q_heal", "q_heal_ratio", "q_per",
                           "q_per_ratio")}
    v.update({k: secs(p[k]) for k in ("f_top", "w_t", "w_slow_t", "r_t")})
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
    if "Tryndamere" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Tryndamere. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
