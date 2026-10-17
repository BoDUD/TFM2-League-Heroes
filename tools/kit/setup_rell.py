"""Rell's text (5 languages), sound_info files and her keys in the shared files, numbers from build_rell.P.

    python tools/kit/setup_rell.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_rell in every language, description + skill_name),
sound/sfx/league_rell_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.125.0, Rell named). Only her keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 + CommunityDragon (Mount Up) - zh_CN 芮尔 / 镕铁少女: 溃敌沉力, 裂阵, 驭铁术：轰落 / 驭铁术：驾临,
全速冲锋, 极涌; zh_TW 銳兒: 破鑄者, 鐵碎之擊, 馭鐵之術：解構 / 起駕, 全速突進, 磁能風暴; ja レル: 革新の鬨, 破鋼撃, フェロマンシー: 装着 /
騎馬, 重槍突貫, 磁気嵐流; ko 렐: 갑옷 파쇄, 파열의 일격, 철마술: 붕괴 / 탑승, 전속력, 자기 폭풍.
Slots: skill = Q (named) with E told in its text, skill2 = W Crash Down (named) with Mount Up in its text, ult = R; the
passive in the attack's text. No combo sentence in any text (the user's rule). No `league_rell_attack` sound: the engine
would play it at the start of every attack; the thrust plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_rell import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_rell"
VERSION = "0.125.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
M = "<#a974ffff>"      # magic damage
R = "<#ef5350ff>"      # crowd control
G = "<#4fc3f7ff>"      # shields, true damage
E = "<>"
# champion_view: the face at her crown (tfm2_ase.py face: 43 px over the hooves, x -2); the mounted idle tops 33 px over the
# pivot, at or above -28 -> banpick_center y = -39 - (-33) (the card rule)
VIEW = {"face": {"x": -2, "y": -43}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -6}}


def mag(k, ap="ap"):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_{ap}}}%{E}"


SHIELD = G + "{w_sh}" + E + " + " + APi + G + "{w_sh_ap}%" + E
R_ALL = M + "{r_all}" + E + " + " + APi + M + "{r_all_ap}%" + E

TEXT = {
    "zh-hans": {
        "name": "芮尔",
        "attack": "骑枪突刺，附带" + M + "{p_dmg}+最大生命{p_hp}%魔法伤害" + E + "。" + O + "溃敌沉力" + E + "：普攻和技能命中英雄，" + A + "{p_t}秒" + E +
                  "内削减其{p_shred}%护甲和魔抗，自己获得{p_steal}点护甲和魔抗（可叠加）。",
        "skill": "前冲一刺，对直线上的敌人造成" + mag("q") + M + "魔法伤害" + E + "并" + R + "晕眩{q_stun}秒" + E + "。" + O + "全速冲锋" + E +
                 "：与身边一名队友加速{e_ms1}%→{e_ms2}%，下次普攻或裂阵爆炸，额外造成英雄最大生命{e_pct}%" + G + "真实伤害" + E + "。",
        "skill2": "跃向敌方英雄砸下，造成" + mag("w") + M + "魔法伤害" + E + "并" + R + "击飞{w_up}秒" + E + "，获得" + SHIELD + "护盾，下马作战" + A +
                  "{w_foot}秒" + E + "（双抗、攻速提升）。" + O + "驾临" + E + "：上马冲锋，" + R + "晕眩{w2_stun}秒" + E + "并掀飞目标。",
        "ult": "把附近敌人猛地拉到身边，" + A + "{r_t}秒" + E + "内持续拖拽并共造成" + R_ALL + M + "魔法伤害" + E + "。等到身边有{r_need}个敌方英雄或有被控住的敌人时才放。",
        "names": ("裂阵", "驭铁术：轰落", "极涌"),
    },
    "zh-hant": {
        "name": "銳兒",
        "attack": "騎槍突刺，附帶" + M + "{p_dmg}+最大生命{p_hp}%魔法傷害" + E + "。" + O + "破鑄者" + E + "：普攻和技能命中英雄，" + A + "{p_t}秒" + E +
                  "內削減其{p_shred}%護甲和魔抗，自己獲得{p_steal}點護甲和魔抗（可疊加）。",
        "skill": "前衝一刺，對直線上的敵人造成" + mag("q") + M + "魔法傷害" + E + "並" + R + "暈眩{q_stun}秒" + E + "。" + O + "全速突進" + E +
                 "：與身邊一名隊友加速{e_ms1}%→{e_ms2}%，下次普攻或鐵碎之擊爆炸，額外造成英雄最大生命{e_pct}%" + G + "真實傷害" + E + "。",
        "skill2": "躍向敵方英雄砸下，造成" + mag("w") + M + "魔法傷害" + E + "並" + R + "擊飛{w_up}秒" + E + "，獲得" + SHIELD + "護盾，下馬作戰" + A +
                  "{w_foot}秒" + E + "（雙抗、攻速提升）。" + O + "起駕" + E + "：上馬衝鋒，" + R + "暈眩{w2_stun}秒" + E + "並掀飛目標。",
        "ult": "把附近敵人猛地拉到身邊，" + A + "{r_t}秒" + E + "內持續拖拽並共造成" + R_ALL + M + "魔法傷害" + E + "。等到身邊有{r_need}個敵方英雄或有被控住的敵人時才施放。",
        "names": ("鐵碎之擊", "馭鐵之術：解構", "磁能風暴"),
    },
    "en": {
        "name": "Rell",
        "attack": "Lance thrusts with " + M + "{p_dmg} + {p_hp}% max health magic damage" + E + ". " + O + "Break the Mold" + E +
                  ": attacks and abilities that hit a champion take {p_shred}% of its armour and magic resist for " + A + "{p_t}s" + E +
                  " and give her {p_steal} of each (stacking).",
        "skill": "Thrusts forward, dealing " + mag("q") + " " + M + "magic damage" + E + " and " + R + "stunning {q_stun}s" + E +
                 " along a line. " + O + "Full Tilt" + E + ": she and a nearby ally gain {e_ms1}% then {e_ms2}% speed; her next attack "
                 "or Shattering Strike explodes for " + G + "{e_pct}% of a champion's max health as true damage" + E + ".",
        "skill2": "Leaps onto an enemy champion and crashes down for " + mag("w") + " " + M + "magic damage" + E + ", " + R +
                  "knocking up {w_up}s" + E + ", gaining a " + SHIELD + " shield and fighting dismounted for " + A + "{w_foot}s" + E +
                  " (resists, attack speed). " + O + "Mount Up" + E + ": charges on her horse, " + R + "stunning {w2_stun}s" + E +
                  " and flinging the target.",
        "ult": "Violently pulls nearby enemies to her, then drags them in for " + A + "{r_t}s" + E + " dealing " + R_ALL + " " + M +
               "magic damage" + E + " in all. She waits for {r_need} enemy champions near her, or one in crowd control.",
        "names": ("Shattering Strike", "Ferromancy: Crash Down", "Magnet Storm"),
    },
    "ko": {
        "name": "렐",
        "attack": "창으로 찌르며 " + M + "{p_dmg} + 최대 체력 {p_hp}% 마법 피해" + E + ". " + O + "갑옷 파쇄" + E + ": 기본 공격과 스킬이 챔피언에 적중하면 " +
                  A + "{p_t}초" + E + " 동안 방어력과 마법 저항력 {p_shred}% 감소, 자신은 각각 {p_steal} 획득(중첩).",
        "skill": "앞으로 찔러 직선 위 적에게 " + mag("q") + "의 " + M + "마법 피해" + E + "와 " + R + "{q_stun}초 기절" + E + ". " + O + "전속력" + E +
                 ": 자신과 근처 아군 이동 속도 {e_ms1}%→{e_ms2}%, 다음 기본 공격이나 파열의 일격이 폭발해 챔피언 최대 체력 {e_pct}%의 " + G +
                 "고정 피해" + E + ".",
        "skill2": "적 챔피언에게 뛰어올라 내려찍어 " + mag("w") + "의 " + M + "마법 피해" + E + "와 " + R + "{w_up}초 에어본" + E + ", " + SHIELD +
                  " 보호막, " + A + "{w_foot}초" + E + " 하마 상태(저항력·공격 속도 증가). " + O + "탑승" + E + ": 말을 타고 돌진해 " + R +
                  "{w2_stun}초 기절" + E + "시키고 대상을 날립니다.",
        "ult": "근처 적을 자신에게 강하게 끌어당기고 " + A + "{r_t}초" + E + " 동안 계속 끌며 총 " + R_ALL + "의 " + M + "마법 피해" + E +
               ". 근처에 적 챔피언 {r_need}명 또는 군중 제어된 적이 있을 때 사용.",
        "names": ("파열의 일격", "철마술: 붕괴", "자기 폭풍"),
    },
    "ja": {
        "name": "レル",
        "attack": "騎槍で突き、" + M + "{p_dmg}+最大体力{p_hp}%の魔法ダメージ" + E + "。" + O + "革新の鬨" + E + "：通常攻撃とスキルがチャンピオンに当たると" +
                  A + "{p_t}秒" + E + "物理防御と魔法防御を{p_shred}%下げ、自身はそれぞれ{p_steal}得る（スタック）。",
        "skill": "前方へ突き、直線上の敵に" + mag("q") + "の" + M + "魔法ダメージ" + E + "と" + R + "{q_stun}秒スタン" + E + "。" + O + "重槍突貫" + E +
                 "：自身と近くの味方1人が移動速度{e_ms1}%→{e_ms2}%、次の通常攻撃か破鋼撃が爆発しチャンピオンの最大体力{e_pct}%の" + G + "確定ダメージ" + E + "。",
        "skill2": "敵チャンピオンへ跳んで叩きつけ" + mag("w") + "の" + M + "魔法ダメージ" + E + "と" + R + "{w_up}秒ノックアップ" + E + "、" + SHIELD +
                  "のシールド、" + A + "{w_foot}秒" + E + "下馬（防御・攻撃速度上昇）。" + O + "騎馬" + E + "：馬で突撃し" + R + "{w2_stun}秒スタン" + E + "、対象を弾く。",
        "ult": "近くの敵を自身へ強く引き寄せ、" + A + "{r_t}秒" + E + "引きずり続けて合計" + R_ALL + "の" + M + "魔法ダメージ" + E +
               "。敵チャンピオン{r_need}体かCC中の敵がいる時に使う。",
        "names": ("破鋼撃", "フェロマンシー: 装着", "磁気嵐流"),
    },
}

C = "league_rell_sfx_"
V = "league_rell_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_rell_a_swing": [(C + "a_swing", 0.4, 0.0)],
    "league_rell_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_rell_q": [(C + "q", 0.55, 0.0)],
    "league_rell_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_rell_e": [(C + "e", 0.55, 0.0)],
    "league_rell_e_boom": [(C + "e_boom", 0.55, 0.0)],
    "league_rell_w": [(C + "w", 0.55, 0.0)],
    "league_rell_w_land": [(C + "w_land", 0.65, 0.0)],
    "league_rell_w2": [(C + "w2", 0.55, 0.0)],
    "league_rell_w2_hit": [(C + "w2_hit", 0.6, 0.0)],
    "league_rell_r": [(C + "r", 0.65, 0.0)],
    "league_rell_r_hit": [(C + "r_hit", 0.35, 0.0)],
    "league_rell_vo_q": [(V + "q", 0.85, 0.0)],
    "league_rell_vo_e": [(V + "e", 0.85, 0.0)],
    "league_rell_vo_w": [(V + "w", 0.85, 0.0)],
    "league_rell_vo_w2": [(V + "w2", 0.85, 0.0)],
    "league_rell_vo_r": [(V + "r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_hp", "p_shred", "p_steal", "q_dmg", "q_ap", "e_ms1", "e_ms2", "e_pct", "w_dmg",
                           "w_ap", "w_sh", "w_sh_ap", "r_need")}
    for k in ("p_t", "q_stun", "w_up", "w_foot", "w2_stun"):
        v[k] = secs(p[k])
    v["r_t"] = secs(p["r_n"] * p["r_period"])
    v["r_all"] = p["r_n"] * p["r_tick"]
    v["r_all_ap"] = p["r_n"] * p["r_tick_ap"]
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
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top), when the top is at or above -28")
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
    if "Rell" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Rell. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
