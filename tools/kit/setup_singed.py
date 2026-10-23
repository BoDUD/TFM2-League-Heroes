"""Singed's text (5 languages), sound_info files and their keys in the shared files, numbers from build_singed.P.

    python tools/kit/setup_singed.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_singed in every language, description + skill_name),
sound/sfx/league_singed_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Singed named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 辛吉德 (炼金术士): 剧毒冲流; 剧毒踪迹, 强力粘胶, 过肩摔, 疯狂药剂; zh_TW 辛吉德: 毒氣推進;
劇毒蹤跡, 強力粘膠, 過肩摔, 瘋狂藥劑; ja シンジド: スリップストリーム; 毒の軌跡, 強力粘着剤, すくい投げ, 狂人のポーション;
ko 신지드: 독성 급류; 맹독의 자취, 초강력 접착제, 던져넘기기, 광기의 물약.
Slots: skill = Fling, skill2 = Mega Adhesive, ult = Insanity Potion; Poison Trail and Noxious Slipstream in the attack's
text. The main pack's Fling roots while his glue lies anywhere (data reads no unit's place; the add-on league_singed
checks the landing, its own tooltip says so). No combo sentence in any text (the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_singed import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_singed"
VERSION = "0.205.0"     # the next free number above main 0.204.1 (Warwick 90 % #497, 2026-10-24)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
T = "<#e0e0e0ff>"      # true damage
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 3, "y": -31}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


def hl(x):
    return G + x + E


def tr(x):
    return T + x + E


TEXT = {
    "zh-hans": {
        "name": "辛吉德",
        "attack": "用盾板砸。" + n("剧毒踪迹") + "：一路在身后留下毒雾（" + t("{q_t}秒") + "），雾里的敌人每" + t("{q_p}秒") + "受" +
                  mag("q_dmg", "q_ap") + "魔法伤害。" + n("剧毒冲流") + "：经过敌方英雄身边时移速+{p_ms}%（" + t("{p_t}秒") + "）。",
        "skill": "抓住目标从肩膀上扔到身后，造成" + mag("e_dmg", "e_ap") + "魔法伤害和" + tr("最大生命{e_thp}%") + "真实伤害；"
                 "地上有" + n("强力粘胶") + "时，被扔的敌人" + cc("禁锢") + t("{e_root}秒") + "。",
        "skill2": "扔出一瓶粘胶，地上留下" + t("{w_t}秒") + "的一摊胶，里面的敌人" + cc("减速") + "{w_slow}%并" + cc("无法位移") + "。",
        "ult": "喝下药剂，" + t("{r_t}秒") + "内法强+{r_apw}、双抗+{r_def}、移速+{r_ms}%、每秒" + hl("回复{r_regen}") + "生命；" +
               n("剧毒踪迹") + "更大、伤害{r_q}%并附带" + cc("重伤") + "（治疗-{r_gw}%）。",
        "names": ("过肩摔", "强力粘胶", "疯狂药剂"),
    },
    "zh-hant": {
        "name": "辛吉德",
        "attack": "用盾板砸。" + n("劇毒蹤跡") + "：一路在身後留下毒霧（" + t("{q_t}秒") + "），霧裡的敵人每" + t("{q_p}秒") + "受" +
                  mag("q_dmg", "q_ap") + "魔法傷害。" + n("毒氣推進") + "：經過敵方英雄身邊時移速+{p_ms}%（" + t("{p_t}秒") + "）。",
        "skill": "抓住目標從肩膀上扔到身後，造成" + mag("e_dmg", "e_ap") + "魔法傷害和" + tr("最大生命{e_thp}%") + "真實傷害；"
                 "地上有" + n("強力粘膠") + "時，被扔的敵人" + cc("禁錮") + t("{e_root}秒") + "。",
        "skill2": "扔出一瓶粘膠，地上留下" + t("{w_t}秒") + "的一灘膠，裡面的敵人" + cc("緩速") + "{w_slow}%並" + cc("無法位移") + "。",
        "ult": "喝下藥劑，" + t("{r_t}秒") + "內魔攻+{r_apw}、雙抗+{r_def}、移速+{r_ms}%、每秒" + hl("回復{r_regen}") + "生命；" +
               n("劇毒蹤跡") + "更大、傷害{r_q}%並附帶" + cc("重傷") + "（治療-{r_gw}%）。",
        "names": ("過肩摔", "強力粘膠", "瘋狂藥劑"),
    },
    "en": {
        "name": "Singed",
        "attack": "A blow of his plate. " + n("Poison Trail") + ": he leaves poison clouds behind him (" + t("{q_t}s") +
                  "); enemies in them take " + mag("q_dmg", "q_ap") + " magic damage every " + t("{q_p}s") + ". " +
                  n("Noxious Slipstream") + ": passing an enemy champion gives him {p_ms}% move speed for " + t("{p_t}s") + ".",
        "skill": "Flings the target over his shoulder to behind him: " + mag("e_dmg", "e_ap") + " magic damage and " +
                 tr("{e_thp}% of its max health") + " true damage. While his " + n("Mega Adhesive") + " lies on the ground, "
                 "the target is " + cc("rooted") + " for " + t("{e_root}s") + ".",
        "skill2": "Throws a vial of glue: for " + t("{w_t}s") + " enemies in it are " + cc("slowed") + " {w_slow}% and " +
                  cc("grounded") + " (no dashes).",
        "ult": "Drinks the potion: for " + t("{r_t}s") + " +{r_apw} ability power, +{r_def} armor and magic resistance, "
               "+{r_ms}% move speed and " + hl("{r_regen} health") + " a second; " + n("Poison Trail") + " grows, deals "
               "{r_q}% and inflicts " + cc("Grievous Wounds") + " (-{r_gw}% healing).",
        "names": ("Fling", "Mega Adhesive", "Insanity Potion"),
    },
    "ko": {
        "name": "신지드",
        "attack": "방패판으로 내려침. " + n("맹독의 자취") + ": 지나간 자리에 독구름을 남김(" + t("{q_t}초") + "), 안의 적은 " +
                  t("{q_p}초") + "마다 " + mag("q_dmg", "q_ap") + " 마법 피해. " + n("독성 급류") + ": 적 챔피언 곁을 지나가면 " +
                  t("{p_t}초") + " 동안 이동 속도 {p_ms}% 증가.",
        "skill": "대상을 어깨 너머 뒤로 내던져 " + mag("e_dmg", "e_ap") + " 마법 피해와 " + tr("최대 체력의 {e_thp}%") +
                 " 고정 피해. " + n("초강력 접착제") + "가 바닥에 있으면 대상을 " + t("{e_root}초") + " " + cc("속박") + ".",
        "skill2": "접착제 병을 던짐: " + t("{w_t}초") + " 동안 안의 적은 {w_slow}% " + cc("둔화") + "되고 " + cc("이동기 사용 불가") + ".",
        "ult": "물약을 마심: " + t("{r_t}초") + " 동안 주문력 +{r_apw}, 방어력·마법 저항력 +{r_def}, 이동 속도 +{r_ms}%, 초당 " +
               hl("체력 {r_regen} 회복") + "; " + n("맹독의 자취") + "가 커지고 피해 {r_q}%에 " + cc("치유 감소") + "(-{r_gw}%).",
        "names": ("던져넘기기", "초강력 접착제", "광기의 물약"),
    },
    "ja": {
        "name": "シンジド",
        "attack": "盾板で殴る。" + n("毒の軌跡") + "：通った跡に毒の雲を残し（" + t("{q_t}秒") + "）、中の敵に" + t("{q_p}秒") + "ごと" +
                  mag("q_dmg", "q_ap") + "の魔法ダメージ。" + n("スリップストリーム") + "：敵英雄のそばを通ると" + t("{p_t}秒") +
                  "移動速度+{p_ms}%。",
        "skill": "対象を肩越しに背後へ投げ、" + mag("e_dmg", "e_ap") + "の魔法ダメージと" + tr("最大体力の{e_thp}%") + "の確定ダメージ。" +
                 n("強力粘着剤") + "が地面にあるとき対象を" + t("{e_root}秒") + cc("スネア") + "。",
        "skill2": "粘着剤の瓶を投げる：" + t("{w_t}秒") + "間、中の敵を{w_slow}%" + cc("スロウ") + "し" + cc("移動スキル封じ") + "。",
        "ult": "ポーションを飲み、" + t("{r_t}秒") + "間魔力+{r_apw}、物防・魔防+{r_def}、移動速度+{r_ms}%、毎秒" + hl("体力{r_regen}回復") +
               "。" + n("毒の軌跡") + "が広がり{r_q}%のダメージと" + cc("重傷") + "（回復-{r_gw}%）。",
        "names": ("すくい投げ", "強力粘着剤", "狂人のポーション"),
    },
}

C = "league_singed_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (the blow lower: it comes often), the poison's sizzle
# quiet (every cloud's tick on every enemy in it), the voice as the other heroes'
SOUNDS = {f"league_singed_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("e", 0.75), ("e_hit", 0.7), ("e_root", 0.8), ("q_hit", 0.3), ("w", 0.7),
    ("w_land", 0.75), ("r", 0.85), ("vo_e", 0.85), ("vo_w", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("q_dmg", "q_ap", "p_ms", "e_dmg", "e_ap", "e_thp", "w_slow", "r_apw", "r_def", "r_ms",
                           "r_regen", "r_q", "r_gw")}
    for k in ("q_t", "q_p", "p_t", "e_root", "w_t", "r_t"):
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
    for lang, tx in TEXT.items():
        d = {"name": tx["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = tx[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), tx["names"])))
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
        bad |= any(m > TOOLTIP_MAX[lang] for m in lens.values())
        print(lang, " ".join(f"{k}:{m}/{TOOLTIP_MAX[lang]}" for k, m in lens.items()))
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
    if "Singed" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Singed. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
