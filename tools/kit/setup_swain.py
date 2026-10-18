"""Swain's text (5 languages), sound_info files and his keys in the shared files, numbers from build_swain.P.

    python tools/kit/setup_swain.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_swain in every language, description + skill_name),
sound/sfx/league_swain_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Swain named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8. --check
only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 斯维因 / 诺克萨斯统领: 狂食鸦群 (魂屑), 解脱之触, 帝国视界, 永不复行, 恶魔升华 (恶魔耀光);
zh_TW 斯溫: 群鴉盛宴 (靈魂碎片), 靈魂拷問, 真知魔眼, 影之爪, 魔君降生 (魔燄); ja スウェイン: 恐襲の魔鴉 (魂のかけら), 死の手, 帝国の眼,
束縛の爪, 魔帝戴冠 (悪魔の紅炎); ko 스웨인: 굶주린 새떼 (영혼 조각), 죽음의 손길, 제국의 눈, 속박명령, 악의 승천 (악의 불길).
Slots: skill = Q Death's Hand, skill2 = E Nevermove (its pull in its text), ult = R Demonic Ascension with Demonflare; the
passive and Vision of Empire (W, cast on its own) in the attack's text. No combo sentence in any text (the user's rule).
No `league_swain_attack` sound: the engine would play it at the start of every attack; the click plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_swain import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_swain"
VERSION = "0.132.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7ee787ff>"      # healing, health
E = "<>"
# champion_view: the face at his crown (tfm2_ase.py face: 39 px over the soles); no banpick_center - his idle tops at
# -27.5 game px, inside the card's -28 (like Orianna, Riven, Vayne)
# 2026-10-18 ban/pick card audit (frame centre, HD from lo_idle / 1.5; user: 「还有哪些英雄BP位置不对的一起改了」): none -> -9: the head stood 2 px over the card
VIEW = {"face": {"x": -1, "y": -39}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -9}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


HEAL = G + "{p_heal}" + E + " + " + APi + G + "{p_heal_ap}%" + E

TEXT = {
    "zh-hans": {
        "name": "斯维因",
        "attack": "恶魔手射出乌鸦弹。" + O + "狂食鸦群" + E + "：帝国视界、永不复行抓到英雄或他打过的英雄阵亡时得到魂屑，回复" + HEAL + G +
                  "生命" + E + "，最大生命+{p_hp}（死后清空）。" + O + "帝国视界" + E + "：每" + A + "{w_cd}秒" + E + "在远处交战的敌方英雄脚下睁眼，" +
                  A + "{w_delay}秒" + E + "后炸开造成" + mag("w_dmg", "w_ap") + M + "魔法伤害" + E + "并" + R + "减速" + E + "。",
        "skill": "恶魔手射出五道扇形散开的闪电，造成" + mag("q_dmg", "q_ap") + M + "魔法伤害" + E + "；近处的敌人被更多闪电打中，另受" +
                 mag("q_dmg2", "q_ap2") + M + "魔法伤害" + E + "。",
        "skill2": "恶魔之手飞出再飞回，回程打中的敌人受到" + mag("e_dmg", "e_ap") + M + "魔法伤害" + E + "并" + R + "禁锢{e_root}秒" + E +
                  "；被禁锢的英雄随后被拉近，留下一片魂屑。",
        "ult": "化身恶魔，吸取周围敌人的生命：每" + A + "{r_pulse}秒" + E + "造成" + mag("r_dmg", "r_ap") + M + "魔法伤害" + E + "，每名英雄回复" +
               G + "{r_heal}" + E + " + " + APi + G + "{r_heal_ap}%" + E + "；吸到英雄时形态延续。" + A + "{r_flare_at}秒" + E + "后放出" + O + "恶魔耀光" +
               E + "：" + mag("r_fl", "r_fl_ap") + M + "魔法伤害" + E + "并" + R + "减速" + E + "。2名敌方英雄在身边或有队友围攻被控者时才放。",
        "names": ("解脱之触", "永不复行", "恶魔升华"),
    },
    "zh-hant": {
        "name": "斯溫",
        "attack": "惡魔之手射出渡鴉彈。" + O + "群鴉盛宴" + E + "：真知魔眼、影之爪抓到英雄或他打過的英雄陣亡時得到靈魂碎片，回復" + HEAL + G +
                  "生命" + E + "，最大生命+{p_hp}（死後清空）。" + O + "真知魔眼" + E + "：每" + A + "{w_cd}秒" + E + "在遠處交戰的敵方英雄腳下睜眼，" +
                  A + "{w_delay}秒" + E + "後炸開造成" + mag("w_dmg", "w_ap") + M + "魔法傷害" + E + "並" + R + "緩速" + E + "。",
        "skill": "惡魔之手射出五道扇形散開的閃電，造成" + mag("q_dmg", "q_ap") + M + "魔法傷害" + E + "；近處的敵人被更多閃電擊中，另受" +
                 mag("q_dmg2", "q_ap2") + M + "魔法傷害" + E + "。",
        "skill2": "惡魔之手飛出再飛回，回程擊中的敵人受到" + mag("e_dmg", "e_ap") + M + "魔法傷害" + E + "並" + R + "定身{e_root}秒" + E +
                  "；被定身的英雄隨後被拉近，留下一片靈魂碎片。",
        "ult": "化身惡魔，汲取周圍敵人的生命：每" + A + "{r_pulse}秒" + E + "造成" + mag("r_dmg", "r_ap") + M + "魔法傷害" + E + "，每名英雄回復" +
               G + "{r_heal}" + E + " + " + APi + G + "{r_heal_ap}%" + E + "；汲取到英雄時型態延續。" + A + "{r_flare_at}秒" + E + "後放出" + O + "魔燄" +
               E + "：" + mag("r_fl", "r_fl_ap") + M + "魔法傷害" + E + "並" + R + "緩速" + E + "。2名敵方英雄在身邊或有隊友圍攻被控者時才施放。",
        "names": ("靈魂拷問", "影之爪", "魔君降生"),
    },
    "en": {
        "name": "Swain",
        "attack": "A raven bolt from his demon hand. " + O + "Ravenous Flock" + E + ": Soul Fragments from Vision of Empire, Nevermove's "
                  "pull and the deaths of champions he hurt heal " + HEAL + ", +{p_hp} max health (lost on death). " + O +
                  "Vision of Empire" + E + ": every " + A + "{w_cd}s" + E + " an eye opens under a far fighting enemy champion, bursting " + A +
                  "{w_delay}s" + E + " later for " + mag("w_dmg", "w_ap") + " " + M + "magic damage" + E + " and a " + R + "slow" + E + ".",
        "skill": "Five bolts of demonic lightning fan out from his hand for " + mag("q_dmg", "q_ap") + " " + M + "magic damage" + E +
                 "; a close enemy is struck by more of them for " + mag("q_dmg2", "q_ap2") + " " + M + "magic damage" + E + " more.",
        "skill2": "A demon hand flies out and back; on its way back it deals " + mag("e_dmg", "e_ap") + " " + M + "magic damage" + E + " and " +
                  R + "roots {e_root}s" + E + ". Rooted champions are then pulled closer and drop a Soul Fragment.",
        "ult": "He becomes the demon and drains nearby enemies: every " + A + "{r_pulse}s" + E + " " + mag("r_dmg", "r_ap") + " " + M +
               "magic damage" + E + ", healing " + G + "{r_heal}" + E + " + " + APi + G + "{r_heal_ap}%" + E + " per champion; draining "
               "champions keeps the form going. After " + A + "{r_flare_at}s" + E + ", " + O + "Demonflare" + E + ": " + mag("r_fl", "r_fl_ap") +
               " " + M + "magic damage" + E + " and a " + R + "slow" + E + ". Cast with 2 enemy champions close, or an ally on a controlled one.",
        "names": ("Death's Hand", "Nevermove", "Demonic Ascension"),
    },
    "ko": {
        "name": "스웨인",
        "attack": "악마의 손에서 까마귀 탄 발사. " + O + "굶주린 새떼" + E + ": 제국의 눈, 속박명령, 그가 공격한 챔피언의 죽음으로 "
                  "영혼 조각 획득: " + HEAL + " 회복, 최대 체력 +{p_hp}(사망 시 초기화). " + O + "제국의 눈" + E + ": " + A +
                  "{w_cd}초" + E + "마다 싸우는 먼 적 챔피언 발밑에 눈이 열려 " + A + "{w_delay}초" + E + " 후 폭발, " +
                  mag("w_dmg", "w_ap") + "의 " + M + "마법 피해" + E + "와 " + R + "둔화" + E + ".",
        "skill": "악마의 손에서 부채꼴로 퍼지는 번개 다섯 줄기가 " + mag("q_dmg", "q_ap") + "의 " + M + "마법 피해" + E +
                 "; 가까운 적은 더 많은 번개에 맞아 " + mag("q_dmg2", "q_ap2") + "의 " + M + "마법 피해" + E + "를 추가로 받습니다.",
        "skill2": "악마의 손이 날아갔다 돌아오며 돌아올 때 " + mag("e_dmg", "e_ap") + "의 " + M + "마법 피해" + E + "와 " + R +
                  "{e_root}초 속박" + E + ". 속박된 챔피언은 끌려오고 영혼 조각을 떨어뜨립니다.",
        "ult": "악마로 변신해 주변 적의 생명력을 흡수: " + A + "{r_pulse}초" + E + "마다 " + mag("r_dmg", "r_ap") + "의 " + M + "마법 피해" + E +
               ", 챔피언마다 " + G + "{r_heal}" + E + " + " + APi + G + "{r_heal_ap}%" + E + " 회복; 챔피언을 흡수하면 형태 유지. " + A +
               "{r_flare_at}초" + E + " 후 " + O + "악의 불길" + E + ": " + mag("r_fl", "r_fl_ap") + "의 " + M + "마법 피해" + E + "와 " + R +
               "둔화" + E + ". 적 챔피언 2명이 가까이 있거나 아군이 군중 제어된 적을 칠 때 사용.",
        "names": ("죽음의 손길", "속박명령", "악의 승천"),
    },
    "ja": {
        "name": "スウェイン",
        "attack": "悪魔の手から魔鴉弾。" + O + "恐襲の魔鴉" + E + "：帝国の眼、束縛の爪、攻撃したチャンピオンの死で「魂のかけら」を得て" + HEAL +
                  "回復、最大体力+{p_hp}（死亡で消える）。" + O + "帝国の眼" + E + "：" + A + "{w_cd}秒" + E +
                  "毎に戦う遠くの敵の足元に眼が開き、" + A + "{w_delay}秒" + E + "後に爆発し" + mag("w_dmg", "w_ap") + "の" + M +
                  "魔法ダメージ" + E + "と" + R + "スロウ" + E + "。",
        "skill": "悪魔の手から扇状に広がる稲妻を5本放ち" + mag("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "。近い敵は多くの稲妻を受け、さらに" +
                 mag("q_dmg2", "q_ap2") + "の" + M + "魔法ダメージ" + E + "。",
        "skill2": "悪魔の手が飛んで戻り、戻る途中で当たった敵に" + mag("e_dmg", "e_ap") + "の" + M + "魔法ダメージ" + E + "と" + R +
                  "{e_root}秒スネア" + E + "。スネアされたチャンピオンは引き寄せられ「魂のかけら」を落とす。",
        "ult": "悪魔に変身し周囲の敵から吸収：" + A + "{r_pulse}秒" + E + "毎に" + mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E +
               "、チャンピオン毎に" + G + "{r_heal}" + E + " + " + APi + G + "{r_heal_ap}%" + E + "回復。チャンピオンを吸収する間は持続。" + A +
               "{r_flare_at}秒" + E + "後「" + O + "悪魔の紅炎" + E + "」：" + mag("r_fl", "r_fl_ap") + "の" + M + "魔法ダメージ" + E + "と" + R +
               "スロウ" + E + "。敵2体が近いか、味方がCC中の敵を攻撃中に使う。",
        "names": ("死の手", "束縛の爪", "魔帝戴冠"),
    },
}

C = "league_swain_sfx_"
V = "league_swain_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_swain_a_cast": [(C + "a_cast", 0.35, 0.0)],
    "league_swain_a_launch": [(C + "a_launch", 0.4, 0.0)],
    "league_swain_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_swain_q": [(C + "q", 0.45, 0.0)],
    "league_swain_q_launch": [(C + "q_launch", 0.55, 0.0)],
    "league_swain_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_swain_e": [(C + "e", 0.45, 0.0)],
    "league_swain_e_launch": [(C + "e_launch", 0.55, 0.0)],
    "league_swain_e_back": [(C + "e_back", 0.5, 0.0)],
    "league_swain_e_hit": [(C + "e_hit", 0.55, 0.0)],
    "league_swain_e_pull": [(C + "e_pull", 0.55, 0.0)],
    "league_swain_w_open": [(C + "w_open", 0.55, 0.0)],
    "league_swain_w_hit": [(C + "w_hit", 0.45, 0.0)],
    "league_swain_p_frag": [(C + "p_frag", 0.5, 0.0)],
    "league_swain_r": [(C + "r", 0.6, 0.0)],
    "league_swain_r_rise": [(C + "r_rise", 0.6, 0.0)],
    "league_swain_r_flare": [(C + "r_flare", 0.65, 0.0)],
    "league_swain_r_fl_hit": [(C + "r_fl_hit", 0.45, 0.0)],
    "league_swain_vo_q": [(V + "q", 0.85, 0.0)],
    "league_swain_vo_e": [(V + "e", 0.85, 0.0)],
    "league_swain_vo_w": [(V + "w", 0.8, 0.0)],
    "league_swain_vo_r": [(V + "r", 0.9, 0.0)],
    "league_swain_vo_r2": [(V + "r2", 0.85, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_hp", "p_heal", "p_heal_ap", "w_dmg", "w_ap", "w_slow", "q_dmg", "q_ap", "q_dmg2", "q_ap2",
                           "e_dmg", "e_ap", "r_dmg", "r_ap", "r_heal", "r_heal_ap", "r_fl", "r_fl_ap")}
    for k in ("w_cd", "w_delay", "e_root", "r_pulse", "r_flare_at"):
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
    if "Swain" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Swain. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
