"""Yunara's text (5 languages), sound_info files and her keys in the shared files, numbers from build_yunara.P.

    python tools/kit/setup_yunara.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_yunara in every language, description + skill_name),
sound/sfx/league_yunara_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point), mod.mod_info (0.131.0, Yunara named). Only her keys change in the shared files. JSON:
indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 不破之誓 / 芸阿娜 - the client swaps name and title: 芸阿娜; 初生之誓, 灵蕴拳, 善恶轮 /
寂灭掌, 明踪步 / 夜影翻, 定圣诀; zh_TW 尤娜拉, 淨土之誓, 靈心修真, 審判靈珠 / 毀滅弧光, 感銘迅步 / 追風躡影, 超逸絕塵; ja
ユナラ, 始まりの地への誓い, 精神修養, 裁きの弧 / 滅びの弧, カンメイの歩み / 触れ得ぬ影, 自己超越; ko 유나라, 최초의 땅의 맹세,
영혼 단련, 심판의 궤적 / 파멸의 궤적, 칸메이의 발자취 / 닿지 않는 그림자, 자기 초월).
Slots: skill = W, skill2 = E, ult = R; the passive and Q (folded into the attack) are told in the attack's text. No
combo sentence in any text (the user's rule). No `league_yunara_attack` sound: the engine would play it at the start of
every attack; the bead's sound plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_yunara import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_yunara"
VERSION = "0.131.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
M = "<#a974ffff>"      # magic
A = "<#ffb900ff>"      # durations, counts
E = "<>"
# champion_view: the face at her ornaments' crown (tfm2_ase.py face: 39 px over the feet); the idle tops 31 px over the
# pivot, above -28 -> banpick_center y = -39 - (-31) (the card rule)
VIEW = {"face": {"x": 1, "y": -39}, "center": {"x": 0, "y": -11}, "banpick_center": {"x": 0, "y": -8}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "芸阿娜",
        "attack": "念珠普攻附带" + mag("p_dmg", "p_ap") + M + "魔法伤害" + E + "。" + O + "初生之誓" + E + "：这段伤害也会暴击（基础暴击" +
                  A + "{crit}%" + E + "）。" + O + "灵蕴拳" + E + "：普攻攒灵蕴，满了自动开启" + A + "{q_t}秒" + E + "：攻速+" + A +
                  "{q_as}%" + E + "，多附带" + mag("q_dmg", "p_ap") + M + "魔法伤害" + E + "，并溅射周围敌人" + ADi + O + "{q_sp}%" + E + O + "物理伤害" + E + "。",
        "skill": "掷出旋转念珠，对路径上的敌人造成" + phy("w_dmg", "w_ratio") + O + "物理伤害" + E + "和衰减减速，终点再旋转" + A +
                 "{w_linger}秒" + E + "。" + O + "超凡形态" + E + "：改为射线，造成" + phy("rw_dmg", "rw_ratio") + O + "物理伤害" + E + "。",
        "skill2": "附近有敌方英雄时，移速+" + A + "{e_ms}%" + E + "（追击时+" + A + "{e_ms2}%" + E + "），持续" + A + "{e_t}秒" + E + "。" +
                  O + "超凡形态" + E + "：敌方英雄贴近时改为向后冲刺。",
        "ult": "附近有2个以上敌方英雄或目标被控制时，进入超凡形态" + A + "{r_t}秒" + E + "：灵蕴拳持续开启，善恶轮变为射线，明踪步变为冲刺，" +
               "两者冷却立刻减少80%。",
        "names": ("善恶轮", "明踪步", "定圣诀"),
    },
    "zh-hant": {
        "name": "尤娜拉",
        "attack": "念珠普攻附帶" + mag("p_dmg", "p_ap") + M + "魔法傷害" + E + "。" + O + "淨土之誓" + E + "：這段傷害也會暴擊（基礎暴擊" +
                  A + "{crit}%" + E + "）。" + O + "靈心修真" + E + "：普攻累積靈蘊，滿了自動開啟" + A + "{q_t}秒" + E + "：攻速+" + A +
                  "{q_as}%" + E + "，多附帶" + mag("q_dmg", "p_ap") + M + "魔法傷害" + E + "，並濺射周圍敵人" + ADi + O + "{q_sp}%" + E + O + "物理傷害" + E + "。",
        "skill": "擲出旋轉念珠，對路徑上的敵人造成" + phy("w_dmg", "w_ratio") + O + "物理傷害" + E + "和衰減緩速，終點再旋轉" + A +
                 "{w_linger}秒" + E + "。" + O + "超凡形態" + E + "：改為射線，造成" + phy("rw_dmg", "rw_ratio") + O + "物理傷害" + E + "。",
        "skill2": "附近有敵方英雄時，跑速+" + A + "{e_ms}%" + E + "（追擊時+" + A + "{e_ms2}%" + E + "），持續" + A + "{e_t}秒" + E + "。" +
                  O + "超凡形態" + E + "：敵方英雄貼近時改為向後衝刺。",
        "ult": "附近有2個以上敵方英雄或目標被控制時，進入超凡形態" + A + "{r_t}秒" + E + "：靈心修真持續開啟，審判靈珠變為射線，感銘迅步變為衝刺，" +
               "兩者冷卻立刻減少80%。",
        "names": ("審判靈珠", "感銘迅步", "超逸絕塵"),
    },
    "en": {
        "name": "Yunara",
        "attack": "Her bead attacks add " + mag("p_dmg", "p_ap") + " " + M + "magic damage" + E + ". " + O + "Vow of the First "
                  "Lands" + E + ": that damage can crit too (base crit " + A + "{crit}%" + E + "). " + O + "Cultivation of Spirit" + E +
                  ": attacks build Unleash; when full she gains " + A + "{q_as}%" + E + " attack speed for " + A + "{q_t}s" + E +
                  ", adds " + mag("q_dmg", "p_ap") + " " + M + "magic damage" + E + " and her attacks spread " + ADi + O + "{q_sp}%" + E + " " + O + "physical damage" + E + " to nearby enemies.",
        "skill": "Lets rip a spinning bead: " + phy("w_dmg", "w_ratio") + " " + O + "physical damage" + E + " and a decaying slow "
                 "to every enemy on its path; it keeps spinning for " + A + "{w_linger}s" + E + " where it stops. " + O +
                 "Transcendent" + E + ": a laser instead, " + phy("rw_dmg", "rw_ratio") + " " + O + "physical damage" + E + ".",
        "skill2": "With an enemy champion near, gains " + A + "{e_ms}%" + E + " move speed (" + A + "{e_ms2}%" + E + " when "
                  "chasing) for " + A + "{e_t}s" + E + ". " + O + "Transcendent" + E + ": dashes back when an enemy champion "
                  "closes in.",
        "ult": "With 2+ enemy champions near or the target in CC, enters her Transcendent State for " + A + "{r_t}s" + E +
               ": Cultivation of Spirit stays on, Arc of Judgment becomes a laser, Kanmei's Steps a dash, and both cooldowns "
               "drop by 80%.",
        "names": ("Arc of Judgment", "Kanmei's Steps", "Transcend One's Self"),
    },
    "ko": {
        "name": "유나라",
        "attack": "염주 기본 공격에 " + mag("p_dmg", "p_ap") + "의 " + M + "마법 피해" + E + " 추가. " + O + "최초의 땅의 맹세" + E +
                  ": 이 피해도 치명타 가능(기본 치명타 " + A + "{crit}%" + E + "). " + O + "영혼 단련" + E + ": 공격으로 기운을 모아 가득 "
                  "차면 " + A + "{q_t}초" + E + " 동안 공격 속도 +" + A + "{q_as}%" + E + ", " + mag("q_dmg", "p_ap") + "의 " + M +
                  "마법 피해" + E + " 추가, 주변 적에게 " + ADi + O + "{q_sp}%" + E + "의 " + O + "물리 피해" + E + ".",
        "skill": "회전하는 염주를 던져 경로의 적에게 " + phy("w_dmg", "w_ratio") + "의 " + O + "물리 피해" + E + "와 점점 약해지는 둔화. "
                 "멈춘 곳에서 " + A + "{w_linger}초" + E + " 더 회전. " + O + "초월 상태" + E + ": 광선으로 " + phy("rw_dmg", "rw_ratio") +
                 "의 " + O + "물리 피해" + E + ".",
        "skill2": "근처에 적 챔피언이 있으면 " + A + "{e_t}초" + E + " 동안 이동 속도 +" + A + "{e_ms}%" + E + "(추격 시 +" + A +
                  "{e_ms2}%" + E + "). " + O + "초월 상태" + E + ": 적 챔피언이 다가오면 뒤로 돌진.",
        "ult": "적 챔피언 2명 이상이 근처에 있거나 대상이 군중 제어 상태면 " + A + "{r_t}초" + E + " 동안 초월 상태: 영혼 단련 유지, 심판의 "
               "궤적은 광선, 칸메이의 발자취는 돌진으로 바뀌고 두 재사용 대기시간 80% 감소.",
        "names": ("심판의 궤적", "칸메이의 발자취", "자기 초월"),
    },
    "ja": {
        "name": "ユナラ",
        "attack": "数珠の通常攻撃に" + mag("p_dmg", "p_ap") + "の" + M + "魔法ダメージ" + E + "。" + O + "始まりの地への誓い" + E +
                  "：これもクリティカル（基本" + A + "{crit}%" + E + "）。" + O + "精神修養" + E + "：攻撃で気を溜め、満タンで" + A +
                  "{q_t}秒" + E + "攻撃速度+" + A + "{q_as}%" + E + "、" + mag("q_dmg", "p_ap") + "の" + M + "魔法ダメージ" + E +
                  "追加、周囲に" + ADi + O + "{q_sp}%" + E + "の" + O + "物理ダメージ" + E + "。",
        "skill": "回転する数珠を放ち、通り道の敵に" + phy("w_dmg", "w_ratio") + "の" + O + "物理ダメージ" + E + "と減衰スロウ。止まった"
                 "所で" + A + "{w_linger}秒" + E + "回転。" + O + "超越状態" + E + "：光線になり" + phy("rw_dmg", "rw_ratio") + "の" + O +
                 "物理ダメージ" + E + "。",
        "skill2": "近くに敵チャンピオンがいると" + A + "{e_t}秒" + E + "移動速度+" + A + "{e_ms}%" + E + "（追撃時+" + A + "{e_ms2}%" +
                  E + "）。" + O + "超越状態" + E + "：敵チャンピオンが迫ると後方へダッシュ。",
        "ult": "敵チャンピオンが2体以上近くにいるか対象が行動妨害中なら" + A + "{r_t}秒" + E + "超越状態：精神修養が続き、裁きの弧は光線、"
               "カンメイの歩みはダッシュになり、両方のCDが80%短縮。",
        "names": ("裁きの弧", "カンメイの歩み", "自己超越"),
    },
}

C = "league_yunara_sfx_"
# sound name -> [(clip, volume, delay)] (clip names differ from the sound names: a clip named like its sound is not
# found in game)
SOUNDS = {
    "league_yunara_a": [(C + "a", 0.4, 0.0)],
    "league_yunara_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_yunara_q_on": [(C + "q_on", 0.55, 0.0)],
    "league_yunara_q_a": [(C + "q_a", 0.45, 0.0)],
    "league_yunara_q_hit": [(C + "q_hit", 0.35, 0.0)],
    "league_yunara_w": [(C + "w", 0.55, 0.0)],
    "league_yunara_w_fly": [(C + "w_fly", 0.45, 0.0)],
    "league_yunara_w_hit": [(C + "w_hit", 0.5, 0.0)],
    "league_yunara_w_end": [(C + "w_hit", 0.35, 0.0)],
    "league_yunara_rw": [(C + "rw", 0.6, 0.0)],
    "league_yunara_rw_beam": [(C + "rw_beam", 0.6, 0.0)],
    "league_yunara_rw_hit": [(C + "rw_hit", 0.55, 0.0)],
    "league_yunara_e": [(C + "e", 0.5, 0.0)],
    "league_yunara_re": [(C + "re", 0.55, 0.0)],
    "league_yunara_r": [(C + "r", 0.6, 0.0)],
    "league_yunara_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_yunara_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_yunara_vo_rw": [(C + "vo_rw", 0.85, 0.0)],
    "league_yunara_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_yunara_vo_r": [(C + "vo_r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "crit", "q_as", "q_dmg", "w_dmg", "w_ratio", "rw_dmg", "rw_ratio", "e_ms",
                           "e_ms2")}
    v["q_sp"] = p["q_sp"]
    for k in ("q_t", "w_linger", "e_t", "r_t"):
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
    for k in [k for k in ov if ID in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Yunara" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' .]+?)\. Kits", r", \1 and Yunara. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
