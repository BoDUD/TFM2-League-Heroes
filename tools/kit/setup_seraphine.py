"""Seraphine's text (5 languages), sound_info files and her keys in the shared files, numbers from build_seraphine.P.

    python tools/kit/setup_seraphine.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_seraphine in every language, description + skill_name),
sound/sfx/league_seraphine_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.72.0, Seraphine named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (萨勒芬妮 / 星籁歌姬; 星光漫射, 清籁穿云, 聚和心声, 增幅节拍, 炫音返场) and Data Dragon
16.20.1 (zh_TW 瑟菈紛 / 燦眸歌姬, 耀眼星光, 樂音高亢, 繞樑歌聲, 迷人節奏, 要不要來首安可曲; ko 세라핀 / 노래하는 별, 무대 장악, 고음,
소리 장막, 비트 발사, 앙코르; ja セラフィーン / 希望のメロディー, ステージプレゼンス, ハイノート, サラウンドサウンド, ビートドロップ,
アンコール). skill2 is named after E (Beat Drop; the icon is E's), W in the text.
No `league_seraphine_attack` sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_seraphine import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_seraphine"
VERSION = "0.72.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
SPi = "<i#asset/base/ui/banpick/champion_stat_icon:speed_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
S = "<#e8d44dff>"      # shields
H = "<#6aff55ff>"      # heals
Wh = "<#ffffffff>"     # move speed
E = "<>"
# champion_view: the face point tfm2_ase.py face suggests (the crown, 47 px over the stage's bottom); the idle's top is
# 40 over the pivot, so banpick_center 0 (-39 - top would be positive: never)
VIEW = {"face": {"x": 2, "y": -47}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def shd(d, r):
    return f"{S}{{{d}}}{E} + {APi}{S}{{{r}}}%{E}"


def hea(d, r):
    return f"{H}{{{d}}}{E} + {APi}{H}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "萨勒芬妮",
        "attack": "被动" + O + "星光漫射" + E + "：每第" + A + "3" + E + "个技能" + O + "回音" + E + "再放一次。放技能时得到一个音符，" +
                  "身边每个友方英雄再给一个（最多" + A + "4" + E + "个），下次普攻每个音符额外造成" + mag("note_dmg", "note_ratio") +
                  M + "魔法伤害" + E + "，有音符时射程更远。",
        "skill": "在目标处落下高音，对范围内敌人造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "；被控制的敌方英雄多受" +
                 "{q_amp}%。",
        "skill2": "声波对直线上的敌人造成" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "并" + R + "减速{e_slow}%" + E +
                  "；回音的声波" + R + "定身" + E + "被减速的英雄、" + R + "晕眩" + E + "被控制的英雄。接着" + O + "聚和心声" + E +
                  "：身边友方英雄获得" + shd("w_sh", "w_sh_ratio") + S + "护盾" + E + "和" + SPi + Wh + "移速+{w_ms}%" + E + "，" + A +
                  "{w_heal_delay}秒" + E + "后按身边友方英雄数各回复" + hea("w_heal", "w_heal_ratio") + "生命。",
        "ult": "放出一道音波，碰到友方英雄后传得更远，对敌方英雄造成" + mag("r_dmg", "r_ratio") + M + "魔法伤害" + E + "并" + R +
               "魅惑{r_charm}秒" + E + "。附近有两名敌方英雄时施放。",
        "names": ("清籁穿云", "增幅节拍", "炫音返场"),
    },
    "zh-hant": {
        "name": "瑟菈紛",
        "attack": "被動" + O + "耀眼星光" + E + "：每第" + A + "3" + E + "個技能" + O + "回音" + E + "再放一次。放技能時得到一個音符，" +
                  "身邊每個友方英雄再給一個（最多" + A + "4" + E + "個），下次普攻每個音符額外造成" + mag("note_dmg", "note_ratio") +
                  M + "魔法傷害" + E + "，有音符時射程更遠。",
        "skill": "在目標處落下高音，對範圍內敵人造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "；被控制的敵方英雄多受" +
                 "{q_amp}%。",
        "skill2": "聲波對直線上的敵人造成" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "並" + R + "緩速{e_slow}%" + E +
                  "；回音的聲波" + R + "定身" + E + "被緩速的英雄、" + R + "暈眩" + E + "被控制的英雄。接著" + O + "繞樑歌聲" + E +
                  "：身邊友方英雄獲得" + shd("w_sh", "w_sh_ratio") + S + "護盾" + E + "和" + SPi + Wh + "移速+{w_ms}%" + E + "，" + A +
                  "{w_heal_delay}秒" + E + "後按身邊友方英雄數各回復" + hea("w_heal", "w_heal_ratio") + "生命。",
        "ult": "放出一道音波，碰到友方英雄後傳得更遠，對敵方英雄造成" + mag("r_dmg", "r_ratio") + M + "魔法傷害" + E + "並" + R +
               "魅惑{r_charm}秒" + E + "。附近有兩名敵方英雄時施放。",
        "names": ("樂音高亢", "迷人節奏", "要不要來首安可曲"),
    },
    "en": {
        "name": "Seraphine",
        "attack": "Passive " + O + "Stage Presence" + E + ": every third spell " + O + "echoes" + E + " (cast again). Each spell "
                  "gives her a note, plus one for every allied champion near her (up to " + A + "4" + E + "); her next attack "
                  "deals " + mag("note_dmg", "note_ratio") + " " + M + "magic damage" + E + " per note, from a longer range.",
        "skill": "Drops a high note on the target: " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " to enemies in "
                 "the area, {q_amp}% more to crowd-controlled champions.",
        "skill2": "A sound wave deals " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + " in a line and " + R +
                  "slows {e_slow}%" + E + "; an echoed wave " + R + "roots" + E + " slowed champions and " + R + "stuns" + E +
                  " crowd-controlled ones. Then " + O + "Surround Sound" + E + ": allied champions near her gain a " +
                  shd("w_sh", "w_sh_ratio") + " " + S + "shield" + E + " and " + SPi + Wh + "{w_ms}% Move Speed" + E +
                  "; after " + A + "{w_heal_delay}s" + E + " each heals " + hea("w_heal", "w_heal_ratio") +
                  " per allied champion near.",
        "ult": "A sound wave that travels farther past an ally deals " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               " to enemy champions and " + R + "charms" + E + " them for " + A + "{r_charm}s" + E + ". Cast with two enemy "
               "champions near.",
        "names": ("High Note", "Beat Drop", "Encore"),
    },
    "ko": {
        "name": "세라핀",
        "attack": "기본 지속 효과 " + O + "무대 장악" + E + ": 세 번째 스킬마다 " + O + "메아리" + E + "로 한 번 더 사용. 스킬마다 음표 1개와 " +
                  "근처 아군 챔피언마다 1개(최대 " + A + "4" + E + "개), 다음 기본 공격이 음표마다 " + mag("note_dmg", "note_ratio") + "의 " +
                  M + "마법 피해" + E + ", 사거리 증가.",
        "skill": "대상 위치에 고음을 떨어뜨려 범위 안의 적에게 " + mag("q_dmg", "q_ratio") + "의 " + M + "마법 피해" + E + ". 군중 제어 " +
                 "상태의 챔피언에게 {q_amp}% 추가.",
        "skill2": "음파가 일직선의 적에게 " + mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E + ", " + R + "{e_slow}% 둔화" + E +
                  ". 메아리 음파는 둔화된 챔피언을 " + R + "속박" + E + ", 군중 제어 상태면 " + R + "기절" + E + ". 이어서 " + O + "소리 장막" +
                  E + ": 근처 아군 챔피언에게 " + shd("w_sh", "w_sh_ratio") + "의 " + S + "보호막" + E + "과 " + SPi + Wh +
                  "이동 속도 {w_ms}%" + E + ", " + A + "{w_heal_delay}초" + E + " 후 근처 아군 챔피언 수만큼 " +
                  hea("w_heal", "w_heal_ratio") + " 회복.",
        "ult": "아군을 지나면 더 멀리 가는 음파로 적 챔피언에게 " + mag("r_dmg", "r_ratio") + "의 " + M + "마법 피해" + E + "와 " + R +
               "매혹 {r_charm}초" + E + ". 적 챔피언 둘이 가까이 있을 때 사용.",
        "names": ("고음", "비트 발사", "앙코르"),
    },
    "ja": {
        "name": "セラフィーン",
        "attack": "パッシブ " + O + "ステージプレゼンス" + E + "：3つ目のスキルごとに" + O + "エコー" + E + "でもう一度発動。スキル時に音符1つ" +
                  "と近くの味方チャンピオン1体ごとに1つ（最大" + A + "4" + E + "）、次の通常攻撃が音符ごとに" + mag("note_dmg", "note_ratio") +
                  "の" + M + "魔法ダメージ" + E + "、射程も伸びる。",
        "skill": "対象地点に高音を落とし、範囲の敵に" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "。行動妨害中の" +
                 "チャンピオンには{q_amp}%増加。",
        "skill2": "音波が直線上の敵に" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "と" + R + "{e_slow}%スロウ" + E +
                  "。エコーの音波はスロウ中を" + R + "スネア" + E + "、行動妨害中を" + R + "スタン" + E + "。続けて" + O +
                  "サラウンドサウンド" + E + "：近くの味方チャンピオンに" + shd("w_sh", "w_sh_ratio") + "の" + S + "シールド" + E + "と" +
                  SPi + Wh + "移動速度{w_ms}%" + E + "、" + A + "{w_heal_delay}秒" + E + "後に近くの味方の数だけ" +
                  hea("w_heal", "w_heal_ratio") + "回復。",
        "ult": "味方を通るとさらに伸びる音波が敵チャンピオンに" + mag("r_dmg", "r_ratio") + "の" + M + "魔法ダメージ" + E + "と" + R +
               "魅了{r_charm}秒" + E + "。敵チャンピオン2体が近い時に使用。",
        "names": ("ハイノート", "ビートドロップ", "アンコール"),
    },
}

C = "league_seraphine_sfx_"
V = "league_seraphine_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_seraphine_a_shot": [(C + "shot", 0.4, 0.0)],
    "league_seraphine_a_note": [(C + "note", 0.45, 0.0)],
    "league_seraphine_q_cast": [(C + "q_cast", 0.5, 0.0)],
    "league_seraphine_q_throw": [(C + "q_throw", 0.5, 0.0)],
    "league_seraphine_q_hit": [(C + "q_hit", 0.55, 0.0)],
    "league_seraphine_e_wave": [(C + "e_cast", 0.55, 0.0)],
    "league_seraphine_e_stun": [(C + "e_stun", 0.5, 0.0)],
    "league_seraphine_w_cast": [(C + "w_cast", 0.5, 0.0), (C + "w_shield", 0.4, 0.1)],
    "league_seraphine_w_heal": [(C + "w_heal", 0.5, 0.0)],
    "league_seraphine_echo": [(C + "echo", 0.45, 0.0)],
    "league_seraphine_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_seraphine_r_wave": [(C + "r_wave", 0.6, 0.0)],
    "league_seraphine_r_charm": [(C + "r_charm", 0.45, 0.0)],
    "league_seraphine_vo_q": [(V + "q", 0.85, 0.0)],
    "league_seraphine_vo_w": [(V + "w", 0.85, 0.0)],
    "league_seraphine_vo_e": [(V + "e", 0.85, 0.0)],
    "league_seraphine_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def values(p):
    v = {k: p[k] for k in ("note_dmg", "note_ratio", "q_dmg", "q_ratio", "q_amp", "e_dmg", "e_ratio", "e_slow",
                           "w_sh", "w_sh_ratio", "w_ms", "w_heal", "w_heal_ratio", "r_dmg", "r_ratio")}
    for k in ("e_slow_t", "e_root", "e_stun", "w_t", "w_heal_delay", "r_charm"):
        v[k] = secs(p[k])
    return v


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


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
    if "Seraphine" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Seraphine. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
