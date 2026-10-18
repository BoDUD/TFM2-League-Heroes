"""Wukong's text (5 languages), sound_info files and his keys in the shared files, numbers from build_wukong.P.

    python tools/kit/setup_wukong.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_wukong in every language, description + skill_name),
sound/sfx/league_wukong_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Wukong named). Only his keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 孙悟空 (齐天大圣): 金刚不坏, 粉碎打击, 真假猴王, 腾云突击, 大闹天宫; zh_TW 悟空 (齊天大聖):
仙山石猴, 定海神兵, 分身術, 筋斗突擊, 無極風暴; ja ウーコン: 岩の皮膚, 強棒打, 戦士の幻惑, 乱像猿技, 旋風猿舞; ko 오공: 바위 피부,
파쇄격, 분신 전사, 근두운 급습, 회전격.
Slots: skill = E Nimbus Strike, skill2 = W Warrior Trickster, ult = R Cyclone; the passive and Q Crushing Blow in the
attack's text. No combo sentence in any text (the user's rule). The main pack's rules are the ones written (Stone Skin's
regeneration a flat amount a stack; the add-on league_wukong makes it a share of his max health and says so itself).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_wukong import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_wukong"
VERSION = "0.146.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face point between his green eyes (ppu_restyle face_to); banpick_center -12 by the card rule on his
# head (tools/art/bp_card_audit.py: the tail tip at -35.3 is a prop over it, the hair 8 game px lower: -39 + 27.3)
VIEW = {"face": {"x": 0, "y": -27}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -12}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def ad(r):
    return f"{ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "孙悟空",
        "attack": "金箍棒横扫。" + O + "金刚不坏" + E + "：打中英雄叠1层（最多5层）：每层护甲+{p_def}、每秒" + G + "回复{p_regen}" + E + "生命。" +
                  O + "粉碎打击" + E + "：每" + A + "{q_t}秒" + E + "下一次普攻伸长棒子，多造成" + phys("q_dmg", "q_ratio") + "物理伤害，目标" + R +
                  "护甲-{q_shred}%" + E + "，持续" + A + "{q_shred_t}秒" + E + "。",
        "skill": "腾云冲向目标，分身打中目标和附近最多" + A + "2个" + E + "敌人，各造成" + phys("e_dmg", "e_ratio") + "物理伤害；之后攻击速度+{e_as}%，"
                 "持续" + A + "{e_as_t}秒" + E + "。",
        "skill2": "隐身" + A + "{w_inv}秒" + E + "冲到敌方英雄身后，原地留下分身" + A + "{w_t}秒" + E + "：每秒打身边一个敌人（英雄优先），造成" + ad("w_ratio") +
                  "物理伤害；他放大招时分身也跟着转。",
        "ult": "伸长金箍棒旋转" + A + "{r_t}秒" + E + "，每" + A + "{r_every}秒" + E + "造成" + phys("r_dmg", "r_ratio") + "外加英雄{r_hp}%最大生命的物理伤害，"
               "第一下" + R + "击飞{r_up}秒" + E + "；" + A + "8秒" + E + "内可再转一次。2个以上敌方英雄、目标被控制或刚突进时才放。",
        "names": ("腾云突击", "真假猴王", "大闹天宫"),
    },
    "zh-hant": {
        "name": "悟空",
        "attack": "金箍棒橫掃。" + O + "仙山石猴" + E + "：打中英雄疊1層（最多5層）：每層護甲+{p_def}、每秒" + G + "回復{p_regen}" + E + "生命。" +
                  O + "定海神兵" + E + "：每" + A + "{q_t}秒" + E + "下一次普攻伸長棒子，多造成" + phys("q_dmg", "q_ratio") + "物理傷害，目標" + R +
                  "護甲-{q_shred}%" + E + "，持續" + A + "{q_shred_t}秒" + E + "。",
        "skill": "騰雲衝向目標，分身打中目標和附近最多" + A + "2個" + E + "敵人，各造成" + phys("e_dmg", "e_ratio") + "物理傷害；之後攻擊速度+{e_as}%，"
                 "持續" + A + "{e_as_t}秒" + E + "。",
        "skill2": "隱身" + A + "{w_inv}秒" + E + "衝到敵方英雄身後，原地留下分身" + A + "{w_t}秒" + E + "：每秒打身邊一個敵人（英雄優先），造成" + ad("w_ratio") +
                  "物理傷害；他放大招時分身也跟著轉。",
        "ult": "伸長金箍棒旋轉" + A + "{r_t}秒" + E + "，每" + A + "{r_every}秒" + E + "造成" + phys("r_dmg", "r_ratio") + "外加英雄{r_hp}%最大生命的物理傷害，"
               "第一下" + R + "擊飛{r_up}秒" + E + "；" + A + "8秒" + E + "內可再轉一次。2個以上敵方英雄、目標被控制或剛突進時才放。",
        "names": ("筋斗突擊", "分身術", "無極風暴"),
    },
    "en": {
        "name": "Wukong",
        "attack": "Staff strikes. " + O + "Stone Skin" + E + ": each hit on a champion adds a stack (5 at most): +{p_def} armour and " + G +
                  "{p_regen} health" + E + " a second each. " + O + "Crushing Blow" + E + ": every " + A + "{q_t}s" + E + " his next attack reaches "
                  "farther and deals " + phys("q_dmg", "q_ratio") + " physical damage more, " + R + "-{q_shred}% armour" + E + " on the target for " +
                  A + "{q_shred_t}s" + E + ".",
        "skill": "Dashes to the target on his cloud; images strike it and up to " + A + "2" + E + " enemies near it for " + phys("e_dmg", "e_ratio") +
                 " physical damage each, then he gains {e_as}% attack speed for " + A + "{e_as_t}s" + E + ".",
        "skill2": "Turns invisible for " + A + "{w_inv}s" + E + " and dashes behind an enemy champion, leaving a clone for " + A + "{w_t}s" + E +
                  ": each second it hits one enemy near it (champions first) for " + ad("w_ratio") + " physical damage, and spins when he does.",
        "ult": "Spins his lengthened staff for " + A + "{r_t}s" + E + ": every " + A + "{r_every}s" + E + " " + phys("r_dmg", "r_ratio") +
               " physical damage plus {r_hp}% of a champion's max health; the first hit " + R + "knocks up for {r_up}s" + E + ". A second spin within " +
               A + "8s" + E + ". Cast with 2+ enemy champions near, a target in crowd control or right after a dash.",
        "names": ("Nimbus Strike", "Warrior Trickster", "Cyclone"),
    },
    "ko": {
        "name": "오공",
        "attack": "여의봉 공격. " + O + "바위 피부" + E + ": 챔피언 적중 시 중첩(최대 5): 중첩당 방어력 +{p_def}, 초당 " + G + "체력 {p_regen} 회복" + E + ". " +
                  O + "파쇄격" + E + ": " + A + "{q_t}초" + E + "마다 다음 공격의 사거리가 늘고 " + phys("q_dmg", "q_ratio") + " 물리 피해 추가, 대상 " + R +
                  "방어력 -{q_shred}%" + E + " " + A + "{q_shred_t}초" + E + ".",
        "skill": "근두운을 타고 대상에게 돌진, 분신이 대상과 주변 최대 " + A + "2명" + E + "에게 각각 " + phys("e_dmg", "e_ratio") + " 물리 피해, 이후 " +
                 A + "{e_as_t}초" + E + "간 공격 속도 +{e_as}%.",
        "skill2": A + "{w_inv}초" + E + "간 투명해져 적 챔피언 뒤로 돌진하고 " + A + "{w_t}초" + E + "간 분신을 남김: 매초 주변 적 하나(챔피언 우선)에게 " +
                  ad("w_ratio") + " 물리 피해, 궁극기 때 함께 회전.",
        "ult": A + "{r_t}초" + E + "간 늘어난 여의봉을 회전: " + A + "{r_every}초" + E + "마다 " + phys("r_dmg", "r_ratio") + " + 챔피언 최대 체력 {r_hp}% 물리 피해, "
               "첫 타격 " + R + "{r_up}초 공중에 띄움" + E + ". " + A + "8초" + E + " 안에 한 번 더. 적 챔피언 2명 이상, 군중 제어된 대상, 돌진 직후 사용.",
        "names": ("근두운 급습", "분신 전사", "회전격"),
    },
    "ja": {
        "name": "ウーコン",
        "attack": "如意棒で攻撃。" + O + "岩の皮膚" + E + "：チャンピオンに命中で1スタック（最大5）：スタック毎に物理防御+{p_def}、毎秒" + G + "体力{p_regen}回復" + E +
                  "。" + O + "強棒打" + E + "：" + A + "{q_t}秒" + E + "毎に次の通常攻撃が伸び" + phys("q_dmg", "q_ratio") + "の物理ダメージを追加、対象の" +
                  R + "物理防御-{q_shred}%" + E + "（" + A + "{q_shred_t}秒" + E + "）。",
        "skill": "觔斗雲で対象へ突進、分身が対象と周囲の敵最大" + A + "2体" + E + "に各" + phys("e_dmg", "e_ratio") + "の物理ダメージ、その後" + A + "{e_as_t}秒" +
                 E + "攻撃速度+{e_as}%。",
        "skill2": A + "{w_inv}秒" + E + "透明になり敵チャンピオンの背後へ、" + A + "{w_t}秒" + E + "分身を残す：毎秒近くの敵1体（チャンピオン優先）に" +
                  ad("w_ratio") + "の物理ダメージ、アルティメット中は一緒に回転。",
        "ult": "伸びた如意棒を" + A + "{r_t}秒" + E + "回転：" + A + "{r_every}秒" + E + "毎に" + phys("r_dmg", "r_ratio") + "+最大体力{r_hp}%の物理ダメージ、"
               "初撃は" + R + "{r_up}秒打ち上げ" + E + "。" + A + "8秒" + E + "以内にもう一度。敵2体以上・行動妨害中・突進直後に使う。",
        "names": ("乱像猿技", "戦士の幻惑", "旋風猿舞"),
    },
}

C = "league_wukong_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_wukong_a_swing": [(C + "a", 0.3, 0.0)],
    "league_wukong_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_wukong_q_swing": [(C + "q", 0.45, 0.0)],
    "league_wukong_q_hit": [(C + "q_hit", 0.45, 0.0)],
    "league_wukong_e_cast": [(C + "e", 0.45, 0.0), (C + "vo_e", 0.85, 0.0)],
    "league_wukong_e_hit": [(C + "e_hit", 0.35, 0.0)],
    "league_wukong_w_cast": [(C + "w", 0.45, 0.0), (C + "vo_w", 0.85, 0.0)],
    "league_wukong_w_hit": [(C + "w_hit", 0.25, 0.0)],
    "league_wukong_r_cast": [(C + "r", 0.55, 0.0), (C + "vo_r", 0.9, 0.0)],
    "league_wukong_r_whoosh": [(C + "r_spin", 0.25, 0.0)],
    "league_wukong_r_up": [(C + "r_up", 0.45, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_def", "q_dmg", "q_ratio", "q_shred", "e_dmg", "e_ratio", "e_as", "w_ratio", "r_dmg", "r_ratio",
                           "r_hp")}
    v["p_regen"] = p["p_regen"]
    for k in ("q_t", "q_shred_t", "e_as_t", "w_inv", "w_t", "r_t", "r_every", "r_up"):
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
    if "Wukong" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Wukong. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
