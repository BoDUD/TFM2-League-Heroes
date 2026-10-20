"""Mel's text (5 languages), sound_info files and her keys in the shared files, numbers from build_mel.P.

    python tools/kit/setup_mel.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_mel in every language, description + skill_name),
sound/sfx/league_mel_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre,
banpick_center), mod.mod_info (VERSION, Mel named). Only her keys change in the shared files. JSON: indent 2, CRLF,
UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 梅尔 (流光镜影): 灼灼之光 (夺命残影), 耀光齐射, 灵魂折镜, 阳炎涡旋, 鎏金蚀日; zh_TW 梅爾
(映魂祕使): 炙灼耀輝 (奪目), 絢輝彈幕, 叱返金身, 烈陽羅網, 無垠天照; en Mel: Searing Brilliance (Overwhelm), Radiant Volley,
Rebuttal, Solar Snare, Golden Eclipse; ja メル: 灼熱の輝き (圧倒), 輝きの連撃, 反駁, 陽光の枷, 黄金蝕; ko 멜: 이글거리는 광휘 (압도),
빛의 세례, 반박, 태양 올가미, 황금 일식.
Slots: skill = Q Radiant Volley, skill2 = E Solar Snare, ult = R Golden Eclipse; the passive Searing Brilliance and W
Rebuttal in the attack's text. No combo sentence in any text (the user's rule); the README and the add-on league_mel
say them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_mel import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_mel"
VERSION = "0.183.0"     # the next free number above main 0.182.0 (Sylas #416, 2026-10-20); retaken at PR and merge time
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names
M = "<#a974ffff>"      # magic damage / AP
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between her eyes (ppu_restyle RESTYLE face_to: the design's eyes 45.5 rows over her soles at
# PPU 1.5, at her standing point's column); the ban/pick card: her idle drawn at 0.90 (league.dll UI_SIZES: 43.3 game
# rows bun top to soles) with its top 28.8 px over the frame centre at that size -> banpick_center -10
# (tools/art/bp_card_audit.py, Zyra's value)
VIEW = {"face": {"x": 0, "y": -30}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


TEXT = {
    "zh-hans": {
        "name": "梅尔",
        "attack": "射出金色光弹。" + O + "灼灼之光" + E + "：每放一个技能，下次普攻多射{p_n}枚光弹（最多{p_max}枚），每枚" +
                  mag("p_dmg", "p_ratio") + "魔法伤害；打中英雄叠一层" + O + "夺命残影" + E + "。" + O + "灵魂折镜" + E + "：每" +
                  t("{w_cd}秒") + "第一次打中英雄时张开屏障" + t("{w_t}秒") + "，受到的伤害减少{w_red}%并反弹{w_ref}%，移速+{w_ms}%。",
        "skill": "耀光飞弹落在目标处，连续爆炸" + t("{q_n}次") + "，每次对范围内的敌人造成" + mag("q_dmg", "q_ratio") + "魔法伤害。",
        "skill2": "射出阳炎法球，中心的敌人受到" + mag("e_dmg", "e_ratio") + "魔法伤害并被" + R + "禁锢" + E + t("{e_root}秒") +
                  "；周围的敌人减速{e_slow}%，" + t("{e_burn}秒") + "内受到" + mag("e_dot", "e_dot_r") + "×{e_dn}魔法伤害。",
        "ult": "无视距离打击所有带" + O + "夺命残影" + E + "的敌方英雄，每层残影造成" + mag("r_st", "r_ratio") + "魔法伤害。",
        "names": ("耀光齐射", "阳炎涡旋", "鎏金蚀日"),
    },
    "zh-hant": {
        "name": "梅爾",
        "attack": "射出金色光彈。" + O + "炙灼耀輝" + E + "：每施放一個技能，下次普攻多射{p_n}發射彈（最多{p_max}發），每發" +
                  mag("p_dmg", "p_ratio") + "魔法傷害；打中英雄疊一層" + O + "奪目" + E + "。" + O + "叱返金身" + E + "：每" +
                  t("{w_cd}秒") + "第一次打中英雄時張開屏障" + t("{w_t}秒") + "，受到的傷害減少{w_red}%並反彈{w_ref}%，移速+{w_ms}%。",
        "skill": "絢輝飛彈落在目標處，連續爆炸" + t("{q_n}次") + "，每次對範圍內的敵人造成" + mag("q_dmg", "q_ratio") + "魔法傷害。",
        "skill2": "射出烈陽法球，中心的敵人受到" + mag("e_dmg", "e_ratio") + "魔法傷害並被" + R + "禁錮" + E + t("{e_root}秒") +
                  "；周圍的敵人緩速{e_slow}%，" + t("{e_burn}秒") + "內受到" + mag("e_dot", "e_dot_r") + "×{e_dn}魔法傷害。",
        "ult": "無視距離打擊所有帶" + O + "奪目" + E + "堆層的敵方英雄，每層造成" + mag("r_st", "r_ratio") + "魔法傷害。",
        "names": ("絢輝彈幕", "烈陽羅網", "無垠天照"),
    },
    "en": {
        "name": "Mel",
        "attack": "A golden bolt. " + O + "Searing Brilliance" + E + ": each ability adds {p_n} bolts to her next attack (up to "
                  "{p_max}), each dealing " + mag("p_dmg", "p_ratio") + " magic damage; hitting a champion applies " + O +
                  "Overwhelm" + E + ". " + O + "Rebuttal" + E + ": every " + t("{w_cd}s") + ", her first champion hit raises a barrier "
                  "for " + t("{w_t}s") + ": {w_red}% less damage taken, {w_ref}% reflected, +{w_ms}% move speed.",
        "skill": "Bolts rain on the target's spot and burst " + t("{q_n} times") + ", each dealing " + mag("q_dmg", "q_ratio") +
                 " magic damage to enemies there.",
        "skill2": "Fires a radiant orb: enemies at its centre take " + mag("e_dmg", "e_ratio") + " magic damage and are " + R +
                  "rooted" + E + " for " + t("{e_root}s") + "; those around it are slowed {e_slow}% and burn for " +
                  mag("e_dot", "e_dot_r") + " x{e_dn} over " + t("{e_burn}s") + ".",
        "ult": "Strikes every enemy champion marked with " + O + "Overwhelm" + E + ", however far: " + mag("r_st", "r_ratio") +
               " magic damage per stack.",
        "names": ("Radiant Volley", "Solar Snare", "Golden Eclipse"),
    },
    "ko": {
        "name": "멜",
        "attack": "황금 투사체 발사. " + O + "이글거리는 광휘" + E + ": 스킬을 쓸 때마다 다음 기본 공격에 투사체 {p_n}개 추가(최대 "
                  "{p_max}개), 개당 " + mag("p_dmg", "p_ratio") + " 마법 피해; 챔피언 적중 시 " + O + "압도" + E + " 중첩. " + O + "반박" + E +
                  ": " + t("{w_cd}초") + "마다 처음 챔피언을 맞히면 " + t("{w_t}초") + " 동안 받는 피해 {w_red}% 감소, {w_ref}% 반사, 이동 "
                  "속도 +{w_ms}%.",
        "skill": "대상 위치에 투사체가 쏟아져 " + t("{q_n}번") + " 폭발, 매번 범위 내 적에게 " + mag("q_dmg", "q_ratio") + " 마법 피해.",
        "skill2": "태양 구체 발사: 중심의 적은 " + mag("e_dmg", "e_ratio") + " 마법 피해를 입고 " + t("{e_root}초") + " " + R + "속박" +
                  E + "; 주변 적은 {e_slow}% 둔화, " + t("{e_burn}초") + " 동안 " + mag("e_dot", "e_dot_r") + " x{e_dn} 마법 피해.",
        "ult": "거리와 관계없이 " + O + "압도" + E + " 중첩이 있는 모든 적 챔피언을 공격, 중첩당 " + mag("r_st", "r_ratio") + " 마법 피해.",
        "names": ("빛의 세례", "태양 올가미", "황금 일식"),
    },
    "ja": {
        "name": "メル",
        "attack": "黄金の弾を放つ。" + O + "灼熱の輝き" + E + "：スキルを使うたび次の通常攻撃で弾が{p_n}発増える（最大{p_max}発）、1発" +
                  mag("p_dmg", "p_ratio") + "の魔法ダメージ。チャンピオンに当たると" + O + "圧倒" + E + "1スタック。" + O + "反駁" + E +
                  "：" + t("{w_cd}秒") + "ごとに最初にチャンピオンに当てると" + t("{w_t}秒") + "障壁、被ダメージ{w_red}%減、{w_ref}%反射、"
                  "移動速度+{w_ms}%。",
        "skill": "対象の地点に弾が降り注ぎ" + t("{q_n}回") + "爆発、毎回範囲内の敵に" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。",
        "skill2": "陽光の球を放つ。中心の敵に" + mag("e_dmg", "e_ratio") + "の魔法ダメージと" + t("{e_root}秒") + R + "スネア" + E +
                  "、周囲の敵は{e_slow}%スロウと" + t("{e_burn}秒") + "で" + mag("e_dot", "e_dot_r") + "×{e_dn}の魔法ダメージ。",
        "ult": "距離に関係なく" + O + "圧倒" + E + "スタックを持つ全敵チャンピオンを打ち、1スタックごとに" + mag("r_st", "r_ratio") +
               "の魔法ダメージ。",
        "names": ("輝きの連撃", "陽光の枷", "黄金蝕"),
    },
}

C = "league_mel_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; w_reflect and x are the add-on's (the reflected bolt, the execute)
SOUNDS = {
    "league_mel_a": [(C + "a", 0.35, 0.0)],
    "league_mel_a_hit": [(C + "a_hit", 0.3, 0.0)],
    "league_mel_p_hit": [(C + "p_hit", 0.25, 0.0)],
    "league_mel_q": [(C + "q", 0.45, 0.0)],
    "league_mel_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_mel_w": [(C + "w", 0.45, 0.0)],
    "league_mel_w_reflect": [(C + "w_reflect", 0.45, 0.0)],
    "league_mel_e": [(C + "e", 0.45, 0.0)],
    "league_mel_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_mel_r": [(C + "r", 0.5, 0.0)],
    "league_mel_r_hit": [(C + "r_hit", 0.5, 0.0)],
    "league_mel_x": [(C + "x", 0.5, 0.0)],
    "league_mel_vo_q": [(C + "vo_q", 0.85, 0.0)],
    "league_mel_vo_w": [(C + "vo_w", 0.85, 0.0)],
    "league_mel_vo_e": [(C + "vo_e", 0.85, 0.0)],
    "league_mel_vo_r": [(C + "vo_r", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t_):
    return f"{t_ / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_n", "p_dmg", "p_ratio", "w_red", "w_ref", "w_ms", "q_n", "q_dmg", "q_ratio", "e_dmg",
                           "e_ratio", "e_slow", "e_dot", "e_dot_r", "e_dn", "r_st", "r_ratio")}
    v["p_max"] = 3 * p["p_n"]
    for k in ("w_cd", "w_t", "e_root"):
        v[k] = secs(p[k])
    v["e_burn"] = secs(p["e_dper"] * (p["e_dn"] - 1))
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
    if "Mel" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Mel. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
