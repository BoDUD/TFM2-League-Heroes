"""Viktor's text (5 languages), sound_info files and his keys in the shared files, numbers from build_viktor.P.

    python tools/kit/setup_viktor.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_viktor in every language, description + skill_name),
sound/sfx/league_viktor_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (VERSION, Viktor named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (维克托 / 奥术先驱 - the name and title slots are swapped there, as for Renekton;
光荣进化, 虹吸能量, 重力场, 海克斯射线, 奥术风暴) and Data Dragon 16.20.1 (zh_TW 維克特 / 奧術預示者, 榮光進化, 能量守恆,
萬有引力產生裝置, 海克斯科技射線, 奧術風暴; ko 빅토르 / 아케인의 전령관, 영광스러운 진화, 힘의 흡수, 중력장, 마법공학 광선,
아케인 폭풍; ja ビクター / アーケインの先触れ, グロリアス・エヴォリューション, パワーブラスト, グラビティフィールド, ヘクステック レイ,
アーケインストーム). skill2 is named after E (Hextech Ray; the icon is E's), W in the text.
No `league_viktor_attack` sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_viktor import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_viktor"
VERSION = "0.75.0"
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
# champion_view: set from tfm2_ase.py face once the sprite is in (run with --face / --banpick)
VIEW = {"face": {"x": 0, "y": -30}, "center": {"x": 0, "y": -12}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def shd(d, r):
    return f"{S}{{{d}}}{E} + {APi}{S}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "维克托",
        "attack": "被动" + O + "光荣进化" + E + "：" + A + "{lv_e}" + E + "级E附带余波，" + A + "{lv_q}" + E + "级Q护盾更强并" + SPi + Wh +
                  "加速{q_ms}%" + E + "，" + A + "{lv_w}" + E + "级技能命中" + R + "减速{evo_slow}%" + E + "，" + A + "{lv_r}" + E +
                  "级风暴变大、转移后持续更久。",
        "skill": "能量弹造成" + mag("q_dmg", "q_ratio") + M + "魔法伤害" + E + "，获得" + shd("q_sh", "q_sh_ratio") + S + "护盾" + E +
                 "；" + A + "{q_buff_t}秒" + E + "内下次普攻额外造成" + mag("q_aa", "q_aa_ratio") + M + "魔法伤害" + E + "。",
        "skill2": "先在敌方英雄脚下放" + O + "重力场" + E + "：" + R + "减速{w_slow}%" + E + "，" + A + "{w_stun_at}秒" + E +
                  "后场内敌人" + R + "晕眩{w_stun}秒" + E + "。再从目标处向后方射出海克斯射线，造成" + mag("e_dmg", "e_ratio") + M +
                  "魔法伤害" + E + "。",
        "ult": "风暴落在敌方英雄身上，造成" + mag("r_dmg", "r_ratio") + M + "魔法伤害" + E + "，之后" + A + "{r_runs}秒" + E +
               "每秒对周围敌人造成" + mag("r_tick", "r_tick_ratio") + M + "魔法伤害" + E + "，目标阵亡就转移到附近英雄。",
        "names": ("虹吸能量", "海克斯射线", "奥术风暴"),
    },
    "zh-hant": {
        "name": "維克特",
        "attack": "被動" + O + "榮光進化" + E + "：" + A + "{lv_e}" + E + "級E附帶餘波，" + A + "{lv_q}" + E + "級Q護盾更強並" + SPi + Wh +
                  "加速{q_ms}%" + E + "，" + A + "{lv_w}" + E + "級技能命中" + R + "緩速{evo_slow}%" + E + "，" + A + "{lv_r}" + E +
                  "級風暴變大、轉移後持續更久。",
        "skill": "能量彈造成" + mag("q_dmg", "q_ratio") + M + "魔法傷害" + E + "，獲得" + shd("q_sh", "q_sh_ratio") + S + "護盾" + E +
                 "；" + A + "{q_buff_t}秒" + E + "內下次普攻額外造成" + mag("q_aa", "q_aa_ratio") + M + "魔法傷害" + E + "。",
        "skill2": "先在敵方英雄腳下放" + O + "萬有引力產生裝置" + E + "：" + R + "緩速{w_slow}%" + E + "，" + A + "{w_stun_at}秒" + E +
                  "後場內敵人" + R + "暈眩{w_stun}秒" + E + "。再從目標處向後方射出海克斯科技射線，造成" + mag("e_dmg", "e_ratio") +
                  M + "魔法傷害" + E + "。",
        "ult": "風暴落在敵方英雄身上，造成" + mag("r_dmg", "r_ratio") + M + "魔法傷害" + E + "，之後" + A + "{r_runs}秒" + E +
               "每秒對周圍敵人造成" + mag("r_tick", "r_tick_ratio") + M + "魔法傷害" + E + "，目標陣亡就轉移到附近英雄。",
        "names": ("能量守恆", "海克斯科技射線", "奧術風暴"),
    },
    "en": {
        "name": "Viktor",
        "attack": "Passive " + O + "Glorious Evolution" + E + ": at level " + A + "{lv_e}" + E + " Hextech Ray leaves an aftershock, at " +
                  A + "{lv_q}" + E + " Siphon Power's shield grows and gives " + SPi + Wh + "{q_ms}% Move Speed" + E + ", at " + A +
                  "{lv_w}" + E + " his spells " + R + "slow {evo_slow}%" + E + ", at " + A + "{lv_r}" + E + " the storm grows and "
                  "lasts longer when it moves on.",
        "skill": "A bolt deals " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + " and gives him a " + shd("q_sh", "q_sh_ratio") +
                 " " + S + "shield" + E + "; his next attack within " + A + "{q_buff_t}s" + E + " deals " + mag("q_aa", "q_aa_ratio") +
                 " bonus " + M + "magic damage" + E + ".",
        "skill2": "First a " + O + "Gravity Field" + E + " under an enemy champion " + R + "slows {w_slow}%" + E + " and " + R +
                  "stuns" + E + " enemies still inside after " + A + "{w_stun_at}s" + E + " for " + A + "{w_stun}s" + E + ". Then a "
                  "Hextech Ray from the target on away from him deals " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + ".",
        "ult": "A storm lands on an enemy champion for " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E + ", then deals " +
               mag("r_tick", "r_tick_ratio") + " " + M + "magic damage" + E + " a second round him for " + A + "{r_runs}s" + E +
               ", moving on to a champion near when he dies.",
        "names": ("Siphon Power", "Hextech Ray", "Arcane Storm"),
    },
    "ko": {
        "name": "빅토르",
        "attack": "기본 지속 효과 " + O + "영광스러운 진화" + E + ": " + A + "{lv_e}" + E + "레벨 E에 여진, " + A + "{lv_q}" + E +
                  "레벨 Q 보호막 강화와 " + SPi + Wh + "이동 속도 {q_ms}%" + E + ", " + A + "{lv_w}" + E + "레벨 스킬 적중 시 " + R +
                  "{evo_slow}% 둔화" + E + ", " + A + "{lv_r}" + E + "레벨 폭풍이 커지고 옮겨 가면 더 오래 유지.",
        "skill": "에너지 탄이 " + mag("q_dmg", "q_ratio") + "의 " + M + "마법 피해" + E + ", " + shd("q_sh", "q_sh_ratio") + "의 " + S +
                 "보호막" + E + ". " + A + "{q_buff_t}초" + E + " 안의 다음 기본 공격이 " + mag("q_aa", "q_aa_ratio") + "의 추가 " + M +
                 "마법 피해" + E + ".",
        "skill2": "먼저 적 챔피언 발밑에 " + O + "중력장" + E + ": " + R + "{w_slow}% 둔화" + E + ", " + A + "{w_stun_at}초" + E +
                  " 뒤 안에 남은 적 " + R + "기절 {w_stun}초" + E + ". 이어서 대상에서 뒤쪽으로 마법공학 광선이 " +
                  mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E + ".",
        "ult": "적 챔피언에게 폭풍을 떨어뜨려 " + mag("r_dmg", "r_ratio") + "의 " + M + "마법 피해" + E + ", 이후 " + A + "{r_runs}초" +
               E + " 동안 매초 주변 적에게 " + mag("r_tick", "r_tick_ratio") + "의 " + M + "마법 피해" + E + ". 대상이 죽으면 근처 " +
               "챔피언에게 옮겨 감.",
        "names": ("힘의 흡수", "마법공학 광선", "아케인 폭풍"),
    },
    "ja": {
        "name": "ビクター",
        "attack": "パッシブ " + O + "グロリアス・エヴォリューション" + E + "：" + A + "{lv_e}" + E + "レベルでEに余波、" + A + "{lv_q}" + E +
                  "レベルでQのシールド強化と" + SPi + Wh + "移動速度{q_ms}%" + E + "、" + A + "{lv_w}" + E + "レベルでスキルが" + R +
                  "{evo_slow}%スロウ" + E + "、" + A + "{lv_r}" + E + "レベルで嵐が大きく、移ると長持ち。",
        "skill": "エネルギー弾が" + mag("q_dmg", "q_ratio") + "の" + M + "魔法ダメージ" + E + "、" + shd("q_sh", "q_sh_ratio") + "の" + S +
                 "シールド" + E + "。" + A + "{q_buff_t}秒" + E + "以内の次の通常攻撃が" + mag("q_aa", "q_aa_ratio") + "の追加" + M +
                 "魔法ダメージ" + E + "。",
        "skill2": "まず敵チャンピオンの足元に" + O + "グラビティフィールド" + E + "：" + R + "{w_slow}%スロウ" + E + "、" + A +
                  "{w_stun_at}秒" + E + "後に中の敵を" + R + "{w_stun}秒スタン" + E + "。続けて対象から奥へレイが" +
                  mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" + E + "。",
        "ult": "敵チャンピオンに嵐を落とし" + mag("r_dmg", "r_ratio") + "の" + M + "魔法ダメージ" + E + "、その後" + A + "{r_runs}秒" + E +
               "毎秒周囲の敵に" + mag("r_tick", "r_tick_ratio") + "の" + M + "魔法ダメージ" + E + "。対象が倒れると近くのチャンピオンへ移る。",
        "names": ("パワーブラスト", "ヘクステック レイ", "アーケインストーム"),
    },
}

C = "league_viktor_sfx_"
V = "league_viktor_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_viktor_a_shot": [(C + "shot", 0.4, 0.0)],
    "league_viktor_q_cast": [(C + "q_cast", 0.5, 0.0)],
    "league_viktor_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_viktor_q_shield": [(C + "q_shield", 0.4, 0.0), (C + "q_ready", 0.35, 0.05)],
    "league_viktor_q_blast": [(C + "q_blast", 0.5, 0.0)],
    "league_viktor_w_cast": [(C + "w_cast", 0.5, 0.0)],
    "league_viktor_w_field": [(C + "w_field", 0.45, 0.0)],
    "league_viktor_w_stun": [(C + "w_stun", 0.5, 0.0)],
    "league_viktor_e_ray": [(C + "e_ray", 0.55, 0.0)],
    "league_viktor_e_after": [(C + "e_after", 0.5, 0.0)],
    "league_viktor_r_cast": [(C + "r_cast", 0.55, 0.0)],
    "league_viktor_r_burst": [(C + "r_burst", 0.6, 0.0)],
    "league_viktor_r_tick": [(C + "r_tick", 0.35, 0.0)],
    "league_viktor_r_storm": [(C + "r_storm", 0.45, 0.0)],
    "league_viktor_evo": [(C + "evo", 0.55, 0.0)],
    "league_viktor_vo_q": [(V + "q", 0.85, 0.0)],
    "league_viktor_vo_w": [(V + "w", 0.85, 0.0)],
    "league_viktor_vo_e": [(V + "e", 0.85, 0.0)],
    "league_viktor_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def values(p):
    v = {k: p[k] for k in ("lv_e", "lv_q", "lv_w", "lv_r", "q_ms", "evo_slow", "q_dmg", "q_ratio", "q_sh", "q_sh_ratio",
                           "q_aa", "q_aa_ratio", "w_slow", "e_dmg", "e_ratio", "r_dmg", "r_ratio", "r_tick", "r_tick_ratio",
                           "r_runs")}
    for k in ("q_buff_t", "q_sh_t", "w_stun_at", "w_stun"):
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
    if "Viktor" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Viktor. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
