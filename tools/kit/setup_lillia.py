"""Lillia's text (5 languages), sound_info files and her keys in the shared files, numbers from build_lillia.P.

    python tools/kit/setup_lillia.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_lillia in every language, description + skill_name),
sound/sfx/league_lillia_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.75.0, Lillia named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (莉莉娅 / 含羞蓓蕾; 梦满枝, 飞花挞, 惊惶木, 流涡种, 夜阑谣; 梦尘, 困倦, 昏睡, 腾跃) and
Data Dragon 16.20.1 (zh_TW 莉莉亞 / 羞赧綻華, 夢沉枝枒, 盛綻之舞, 拽柯之擊, 飛旋種籽, 柔沉夢謠, 夢境之塵; ko 릴리아 / 수줍은 꽃,
꿈나무 지팡이, 뾰로롱 강타, 이익! 쿵!, 데굴데굴 씨앗, 감미로운 자장가, 꿈가루; ja リリア / はにかみ屋の花, 夢を集める大枝, 花開く風,
ひゃっ、あぶない！, コロコロの種, 夢見の子守唄, 夢のかけら). skill2 is named after E (Swirlseed; the icon is E's), W in the text.
No `league_lillia_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_lillia import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_lillia"
VERSION = "0.75.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
SPi = "<i#asset/base/ui/banpick/champion_stat_icon:speed_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
H = "<#6aff55ff>"      # heals
Wh = "<#ffffffff>"     # move speed
E = "<>"
# champion_view: placeholder until the sprite is in (tfm2_ase.py face)
VIEW = {"face": {"x": 0, "y": -38}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def hea(d, r):
    return f"{H}{{{d}}}{E} + {APi}{H}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "莉莉娅",
        "attack": "被动" + O + "梦满枝" + E + "：技能命中时附上" + O + "梦尘" + E + "，" + A + "{d_secs}秒" + E + "内造成" + A + "{runs}" + E +
                  "次" + mag("d_dmg", "d_ratio") + M + "魔法伤害" + E + "，对英雄另造成共{d_hp_total}%最大生命值真实伤害并回复她" +
                  hea("d_heal", "d_heal_ratio") + "生命。施法叠" + O + "腾跃" + E + "，每层" + SPi + Wh + "移速+{pr_ms}%" + E + "（最多" +
                  A + "4" + E + "层）。",
        "skill": "挥舞枝条，对周围敌人造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "并附上梦尘；外圈的敌人再受到同等的" +
                 "真实伤害。",
        "skill2": "抛出种子，对落点敌人造成" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "并" + R + "减速{e_slow}%" + E + "。接着" + O + "惊惶木" + E + "：蓄力重击目标所在处，造成" + mag("w_dmg", "w_ratio") + M + "魔法伤害" +
                  E + "，正中心受到" + A + "{w_sweet_x}" + E + "倍。",
        "ult": "所有带梦尘的敌方英雄" + R + "困倦" + E + A + "{r_drowsy}秒" + E + "（" + R + "减速{r_slow}%" + E + "），随后" + R + "昏睡" +
               E + A + "{r_sleep}秒" + E + "；她的技能叫醒昏睡者时额外造成" + mag("r_wake", "r_wake_ratio") + M + "魔法伤害" + E + "。",
        "names": ("飞花挞", "流涡种", "夜阑谣"),
    },
    "zh-hant": {
        "name": "莉莉亞",
        "attack": "被動" + O + "夢沉枝枒" + E + "：技能命中時附上" + O + "夢境之塵" + E + "，" + A + "{d_secs}秒" + E + "內造成" + A +
                  "{runs}" + E + "次" + mag("d_dmg", "d_ratio") + M + "魔法傷害" + E + "，對英雄另造成共{d_hp_total}%最大生命值真實傷害並" +
                  "回復她" + hea("d_heal", "d_heal_ratio") + "生命。施法疊加跑速，每層" + SPi + Wh + "移速+{pr_ms}%" + E + "（最多" + A +
                  "4" + E + "層）。",
        "skill": "揮舞枝枒，對周圍敵人造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "並附上夢境之塵；外圈的敵人再受到同等的" +
                 "真實傷害。",
        "skill2": "拋出種籽，對落點敵人造成" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "並" + R + "緩速{e_slow}%" + E + "。接著" + O + "拽柯之擊" + E + "：蓄力重擊目標所在處，造成" + mag("w_dmg", "w_ratio") + M + "魔法傷害" +
                  E + "，正中心受到" + A + "{w_sweet_x}" + E + "倍。",
        "ult": "所有帶夢境之塵的敵方英雄" + R + "疲倦" + E + A + "{r_drowsy}秒" + E + "（" + R + "緩速{r_slow}%" + E + "），隨後" + R +
               "沉睡" + E + A + "{r_sleep}秒" + E + "；她的技能喚醒沉睡者時額外造成" + mag("r_wake", "r_wake_ratio") + M + "魔法傷害" + E +
               "。",
        "names": ("盛綻之舞", "飛旋種籽", "柔沉夢謠"),
    },
    "en": {
        "name": "Lillia",
        "attack": "Passive " + O + "Dream-Laden Bough" + E + ": her ability hits leave " + O + "Dream Dust" + E + ": " + A + "{runs}" + E +
                  " pulses of " + mag("d_dmg", "d_ratio") + " " + M + "magic damage" + E + " over " + A + "{d_secs}s" + E + ", plus " +
                  "{d_hp_total}% of a champion's max health as true damage, and she heals " + hea("d_heal", "d_heal_ratio") +
                  ". Each cast stacks " + O + "Prance" + E + ": " + SPi + Wh + "+{pr_ms}% Move Speed" + E + " (up to " + A + "4" + E + ").",
        "skill": "Swings her bough: " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " and Dream Dust to nearby enemies; "
                 "those on the edge take the same again as true damage.",
        "skill2": "Lobs a seed: " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + " and a " + R + "{e_slow}% slow" + E +
                  ". Then " + O + "Watch Out! Eep!" + E + ": a wound-up strike where the target stood, " +
                  mag("w_dmg", "w_ratio") + " " + M + "magic damage" + E + ", " + A + "{w_sweet_x}x" + E + " in the center.",
        "ult": "Every enemy champion with Dream Dust turns " + R + "Drowsy" + E + " (" + R + "{r_slow}% slow" + E + ") for " + A +
               "{r_drowsy}s" + E + ", then falls " + R + "Asleep" + E + " for " + A + "{r_sleep}s" + E + "; her abilities wake sleepers "
               "for " + mag("r_wake", "r_wake_ratio") + " more " + M + "magic damage" + E + ".",
        "names": ("Blooming Blows", "Swirlseed", "Lilting Lullaby"),
    },
    "ko": {
        "name": "릴리아",
        "attack": "기본 지속 효과 " + O + "꿈나무 지팡이" + E + ": 스킬 적중 시 " + O + "꿈가루" + E + ": " + A + "{d_secs}초" + E + " 동안 " +
                  A + "{runs}" + E + "회 " + mag("d_dmg", "d_ratio") + "의 " + M + "마법 피해" + E + ", 챔피언에게는 최대 체력의 " +
                  "{d_hp_total}% 고정 피해, 릴리아는 " + hea("d_heal", "d_heal_ratio") + " 회복. 스킬마다 " + SPi + Wh +
                  "이동 속도 {pr_ms}%" + E + " 중첩(최대 " + A + "4" + E + ").",
        "skill": "지팡이를 휘둘러 주변 적에게 " + mag("q_dmg", "q_ratio") + "의 " + M + "마법 피해" + E + "와 꿈가루. 가장자리의 적은 같은 " +
                 "양의 고정 피해를 추가로 받습니다.",
        "skill2": "씨앗을 던져 " + mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E + "와 " + R + "{e_slow}% 둔화" + E + ". 이어서 " + O + "이익! 쿵!" + E + ": 대상 위치를 강타해 " + mag("w_dmg", "w_ratio") + "의 " + M + "마법 피해" +
                  E + ", 중심은 " + A + "{w_sweet_x}" + E + "배.",
        "ult": "꿈가루가 묻은 모든 적 챔피언이 " + A + "{r_drowsy}초" + E + " " + R + "졸음" + E + "(" + R + "{r_slow}% 둔화" + E + ") 후 " +
               A + "{r_sleep}초" + E + " " + R + "잠듭니다" + E + ". 릴리아의 스킬로 깨우면 " + mag("r_wake", "r_wake_ratio") + "의 " + M +
               "마법 피해" + E + " 추가.",
        "names": ("뾰로롱 강타", "데굴데굴 씨앗", "감미로운 자장가"),
    },
    "ja": {
        "name": "リリア",
        "attack": "パッシブ " + O + "夢を集める大枝" + E + "：スキル命中で" + O + "夢のかけら" + E + "、" + A + "{d_secs}秒" + E + "で" + A +
                  "{runs}" + E + "回" + mag("d_dmg", "d_ratio") + "の" + M + "魔法ダメージ" + E + "、チャンピオンには最大体力の" +
                  "{d_hp_total}%の確定ダメージ、リリアは" + hea("d_heal", "d_heal_ratio") + "回復。スキルごとに" + SPi + Wh +
                  "移動速度{pr_ms}%" + E + "（最大" + A + "4" + E + "）。",
        "skill": "大枝を振り、周囲の敵に" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "と夢のかけら。端の敵には同量の" +
                 "確定ダメージを追加。",
        "skill2": "種を投げ" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "と" + R + "{e_slow}%スロウ" + E + "。続けて" + O + "ひゃっ、あぶない！" + E + "：対象地点を強打し" + mag("w_dmg", "w_ratio") + "の" + M +
                  "魔法ダメージ" + E + "、中心は" + A + "{w_sweet_x}" + E + "倍。",
        "ult": "夢のかけらを受けた敵チャンピオン全員に" + R + "眠気" + E + A + "{r_drowsy}秒" + E + "（" + R + "{r_slow}%スロウ" + E +
               "）、その後" + R + "睡眠" + E + A + "{r_sleep}秒" + E + "。リリアのスキルで起こすと" + mag("r_wake", "r_wake_ratio") + "の" +
               M + "魔法ダメージ" + E + "追加。",
        "names": ("花開く風", "コロコロの種", "夢見の子守唄"),
    },
}

C = "league_lillia_sfx_"
V = "league_lillia_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_lillia_a_swing": [(C + "swing", 0.4, 0.0), (C + "hit", 0.4, 0.15)],
    "league_lillia_q_cast": [(C + "q_cast", 0.5, 0.0)],
    "league_lillia_q_hit": [(C + "q_hit", 0.45, 0.0), (C + "q_edge", 0.4, 0.03)],
    "league_lillia_e_cast": [(C + "e_cast", 0.5, 0.0)],
    "league_lillia_e_hit": [(C + "e_hit", 0.5, 0.0)],
    "league_lillia_w_cast": [(C + "w_cast", 0.5, 0.0)],
    "league_lillia_w_hit": [(C + "w_hit", 0.55, 0.0)],
    "league_lillia_w_sweet": [(C + "w_sweet", 0.55, 0.0)],
    "league_lillia_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_lillia_drowsy": [(C + "drowsy", 0.4, 0.0)],
    "league_lillia_sleep": [(C + "sleep", 0.45, 0.0)],
    "league_lillia_wake": [(C + "wake", 0.5, 0.0)],
    "league_lillia_vo_q": [(V + "q", 0.85, 0.0)],
    "league_lillia_vo_w": [(V + "w", 0.85, 0.0)],
    "league_lillia_vo_e": [(V + "e", 0.85, 0.0)],
    "league_lillia_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def values(p):
    v = {k: p[k] for k in ("d_dmg", "d_ratio", "d_heal", "d_heal_ratio", "pr_ms", "q_dmg", "q_ratio", "e_dmg", "e_ratio",
                           "e_slow", "w_dmg", "w_ratio", "w_sweet_x", "r_slow", "r_wake", "r_wake_ratio")}
    runs = (p["d_t"] - 1) // p["d_period"] + 1
    v["runs"] = runs
    v["d_hp_total"] = runs * p["d_hp"]
    for k in ("e_slow_t", "r_drowsy", "r_sleep"):
        v[k] = secs(p[k])
    v["d_secs"] = secs(p["d_t"] - 1)
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
    if "Lillia" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Lillia. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
