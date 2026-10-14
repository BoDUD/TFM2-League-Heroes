"""Sion's text (5 languages), sound_info files and his keys in the shared files, numbers from build_sion.P.

    python tools/kit/setup_sion.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_sion in every language, description + skill_name),
sound/sfx/league_sion_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.109.0, Sion named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (赛恩 / 亡灵战神; 死亡荣耀, 残虐猛击, 灵魂熔炉, 杀手怒吼, 蛮横冲撞; the client swaps
name and title) and Data Dragon 16.20.1 (zh_TW 賽恩 / 光榮戰死 / 巨幅毀滅 / 魂魄熔爐 / 殺戮怒吼 / 猛烈狂擊, ja サイオン /
名誉ある死 / 破滅の斧 / 魂の炉心 / 殺意の雄叫び / 猪突猛進, ko 사이온 / 영광스러운 죽음 / 대량 학살 강타 / 영혼의 용광로 /
학살자의 포효 / 멈출 수 없는 맹공).
Slots: skill = Q, skill2 = E (W told in its text), ult = R; W's kill stacks in the attack's text (the revive is the
add-on's own text). No combo sentence in any text (the user's rule). No `league_sion_attack` sound: the engine would
play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sion import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_sion"
VERSION = "0.109.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#6aff55ff>"      # health
Y = "<#e8d44dff>"      # shields
E = "<>"
# champion_view: tfm2_ase.py face on the sheet (2026-10-14: crown 41 px above the feet, head centre +2.8)
VIEW = {"face": {"x": 4, "y": -41}, "center": {"x": 0, "y": -14}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def mhp(d, h):
    return f"{M}{{{d}}}{E} + {HPi}{M}{{{h}}}%{E}"


SH = Y + "{w_sh}" + E + " + " + ADi + Y + "{w_ad}%" + E
RD = O + "{r_dmg1}-{r_dmg3}" + E + " + " + ADi + O + "{r_ratio}%" + E

TEXT = {
    "zh-hans": {
        "name": "赛恩",
        "attack": O + "灵魂熔炉" + E + "被动：普攻每击杀一个单位，永久获得" + G + "{k_hp}" + E + "点最大生命值（阵亡后重新累积）。",
        "skill": "蓄力" + A + "{q_ch}秒" + E + "后向前砸地，直线上的敌人受到" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "并" + R + "击飞{q_up}秒" + E +
                 "；蓄力时被控制会打断。",
        "skill2": "怒吼穿过小兵，造成" + mhp("e_dmg", "e_hp") + M + "魔法伤害" + E + "，" + R + "减速{e_slow}%" + E + "，护甲降低{e_shred}%。" + O + "灵魂熔炉" + E +
                  "：获得" + SH + "护盾，" + A + "{w_det}秒" + E + "后护盾仍在则爆炸，造成" + mhp("w_dmg", "w_hp") + M + "魔法伤害" + E + "。",
        "ult": "免疫控制冲向敌方英雄，撞到第一个英雄造成" + RD + O + "物理伤害" + E + "并" + R + "击飞{r_up1}-{r_up3}秒" + E + "（冲得越远越强），周围敌人" + R +
               "减速{r_slow}%" + E + "。",
        "names": ("残虐猛击", "杀手怒吼", "蛮横冲撞"),
    },
    "zh-hant": {
        "name": "賽恩",
        "attack": O + "魂魄熔爐" + E + "被動：普攻每擊殺一個單位，永久獲得" + G + "{k_hp}" + E + "點最大生命值（陣亡後重新累積）。",
        "skill": "蓄力" + A + "{q_ch}秒" + E + "後向前砸地，直線上的敵人受到" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "並" + R + "擊飛{q_up}秒" + E +
                 "；蓄力時被控制會打斷。",
        "skill2": "怒吼穿過小兵，造成" + mhp("e_dmg", "e_hp") + M + "魔法傷害" + E + "，" + R + "緩速{e_slow}%" + E + "，護甲降低{e_shred}%。" + O + "魂魄熔爐" + E +
                  "：獲得" + SH + "護盾，" + A + "{w_det}秒" + E + "後護盾仍在則爆炸，造成" + mhp("w_dmg", "w_hp") + M + "魔法傷害" + E + "。",
        "ult": "免疫控制衝向敵方英雄，撞到第一個英雄造成" + RD + O + "物理傷害" + E + "並" + R + "擊飛{r_up1}-{r_up3}秒" + E + "（衝得越遠越強），周圍敵人" + R +
               "緩速{r_slow}%" + E + "。",
        "names": ("巨幅毀滅", "殺戮怒吼", "猛烈狂擊"),
    },
    "en": {
        "name": "Sion",
        "attack": O + "Soul Furnace" + E + " passive: each unit his attack kills grants " + G + "{k_hp}" + E +
                  " maximum health for good (lost on death).",
        "skill": "Charges for " + A + "{q_ch}s" + E + ", then smashes the line in front: " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E +
                 " and " + R + "knocked up {q_up}s" + E + ". Crowd control on him breaks the charge.",
        "skill2": "Roars through minions: " + mhp("e_dmg", "e_hp") + " " + M + "magic damage" + E + ", " + R + "slowed {e_slow}%" + E + " and armour -{e_shred}%. " +
                  O + "Soul Furnace" + E + ": a " + SH + " shield; still holding it after " + A + "{w_det}s" + E + ", it blasts nearby enemies for " +
                  mhp("w_dmg", "w_hp") + " " + M + "magic damage" + E + ".",
        "ult": "Charges at an enemy champion, immune to crowd control: the first champion hit takes " + RD + " " + O + "physical damage" + E + " and is " + R +
               "knocked up {r_up1}-{r_up3}s" + E + " (the farther he ran, the more); nearby enemies are " + R + "slowed {r_slow}%" + E + ".",
        "names": ("Decimating Smash", "Roar of the Slayer", "Unstoppable Onslaught"),
    },
    "ko": {
        "name": "사이온",
        "attack": O + "영혼의 용광로" + E + " 기본 지속 효과: 기본 공격으로 처치한 대상마다 최대 체력 " + G + "{k_hp}" + E + " 영구 증가(사망 시 초기화).",
        "skill": A + "{q_ch}초" + E + " 충전 후 앞의 직선을 내려찍어 " + phy("q_dmg", "q_ratio") + " " + O + "물리 피해" + E + "와 " + R + "{q_up}초 에어본" + E +
                 ". 충전 중 군중 제어에 걸리면 취소.",
        "skill2": "미니언을 꿰뚫는 포효로 " + mhp("e_dmg", "e_hp") + " " + M + "마법 피해" + E + ", " + R + "{e_slow}% 둔화" + E + ", 방어력 {e_shred}% 감소. " + O +
                  "영혼의 용광로" + E + ": " + SH + " 보호막, " + A + "{w_det}초" + E + " 후 남아 있으면 폭발해 " + mhp("w_dmg", "w_hp") + " " + M + "마법 피해" + E + ".",
        "ult": "군중 제어 면역으로 적 챔피언에게 돌진, 처음 부딪힌 챔피언에게 " + RD + " " + O + "물리 피해" + E + "와 " + R + "{r_up1}-{r_up3}초 에어본" + E +
               "(멀리 달릴수록 강함), 주변 적 " + R + "{r_slow}% 둔화" + E + ".",
        "names": ("대량 학살 강타", "학살자의 포효", "멈출 수 없는 맹공"),
    },
    "ja": {
        "name": "サイオン",
        "attack": O + "魂の炉心" + E + "自動効果：通常攻撃でユニットを倒すたび最大体力が" + G + "{k_hp}" + E + "永続増加（死亡でリセット）。",
        "skill": A + "{q_ch}秒" + E + "溜めて前方の直線を叩きつけ、" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "と" + R + "{q_up}秒ノックアップ" + E +
                 "。溜め中に行動妨害を受けると中断。",
        "skill2": "ミニオンを貫く雄叫びで" + mhp("e_dmg", "e_hp") + "の" + M + "魔法ダメージ" + E + "、" + R + "{e_slow}%スロウ" + E + "、物理防御{e_shred}%低下。" + O +
                  "魂の炉心" + E + "：" + SH + "のシールド、" + A + "{w_det}秒" + E + "後に残っていれば爆発し" + mhp("w_dmg", "w_hp") + "の" + M + "魔法ダメージ" + E + "。",
        "ult": "行動妨害無効で敵チャンピオンへ突進、最初に当たったチャンピオンに" + RD + "の" + O + "物理ダメージ" + E + "と" + R + "{r_up1}-{r_up3}秒ノックアップ" +
               E + "（遠いほど強力）、周囲の敵に" + R + "{r_slow}%スロウ" + E + "。",
        "names": ("破滅の斧", "殺意の雄叫び", "猪突猛進"),
    },
}

C = "league_sion_sfx_"
S_ = "league_sion_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.5, 0.0), ("q", "q", 0.5, 0.0), ("q_hit", "q_hit", 0.65, 0.0),
    ("e", "e", 0.6, 0.0), ("e_hit", "e_hit", 0.5, 0.0), ("w", "w", 0.5, 0.0), ("w_hit", "w_hit", 0.6, 0.0),
    ("r", "r", 0.6, 0.0), ("r_hit", "r_hit", 0.7, 0.0), ("p_rise", "p_rise", 0.6, 0.0),
    ("vo_q", "vo_q", 0.8, 0.0), ("vo_w", "vo_w", 0.8, 0.0), ("vo_e", "vo_e", 0.8, 0.0), ("vo_r", "vo_r", 0.85, 0.0),
    ("vo_p", "vo_p", 0.85, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("k_hp", "q_dmg", "q_ratio", "e_dmg", "e_hp", "e_slow", "e_shred", "w_sh", "w_ad", "w_dmg",
                           "w_hp", "r_dmg1", "r_dmg3", "r_ratio", "r_slow")}
    v.update({k: secs(p[k]) for k in ("q_ch", "q_up", "w_det", "r_up1", "r_up3")})
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
    if "Sion" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Sion. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
