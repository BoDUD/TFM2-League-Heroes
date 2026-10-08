"""Xayah's text (5 languages), sound_info files and her keys in the shared files, numbers from build_xayah.P.

    python tools/kit/setup_xayah.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in xy/league): text/champion.i18n (league_xayah in every language, description + skill_name),
sound/sfx/league_xayah_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.78.0, Xayah named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/xy/rst_full.py: 霞 / 逆羽, 锐切, 双刃, 致死羽衣, 倒钩, 暴风羽刃) and
Data Dragon 16.19.1 (zh_TW 剎雅 / 一翦兩斷 / 赤落連匕 / 奪命疾翼 / 漫天血刃 / 驟羽暴風, ko 자야 / 관통상 / 깃털 연타 /
죽음의 깃 / 깃부르미 / 저항의 비상, ja ザヤ / クリーンカット / ダブルダガー / デッドリープルーム / ブレードコーラー /
フェザーストーム). The slot names: skill = Q then E (both names), skill2 = W, ult = R.
No `league_xayah_attack` sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_xayah import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_xayah"
VERSION = "0.78.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": -1, "y": -37}, "center": {"x": 0, "y": -12}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "霞",
        "attack": "甩出羽刃攻击。被动" + O + "锐切" + E + "：每放一个技能，之后" + A + "3次" + E + "普攻（最多存5次）穿透直线，"
                  "其他目标受到{a_pierce}%伤害，并在目标身后留下一根" + O + "羽毛" + E + "（{f_life}秒）。",
        "skill": "扔出两把穿透匕首，各造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "（后续目标{q_fall}%），各留一根羽毛；随后" +
                 O + "倒钩" + E + "收回所有羽毛，每根对路过的敌人造成" + phy("e_dmg", "e_ratio") + "伤害，一次收回命中英雄第3次起" + R +
                 "禁锢{e_root}秒" + E + "。",
        "skill2": "攻速+" + A + "{w_as}%" + E + "，持续{w_t}秒；期间每次普攻再甩出一片{w_pct}%伤害的羽刃，命中英雄时移速+{w_ms}%。",
        "ult": "跃向空中，" + A + "{r_air}秒" + E + "内不受伤害和控制，再向前方降下匕首雨，造成" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E +
               "，留下一排羽毛并随即收回。",
        "names": ("双刃·倒钩", "致死羽衣", "暴风羽刃"),
    },
    "zh-hant": {
        "name": "剎雅",
        "attack": "甩出羽刃攻擊。被動" + O + "一翦兩斷" + E + "：每施放一個技能，之後" + A + "3次" + E + "普攻（最多存5次）貫穿直線，"
                  "其他目標受到{a_pierce}%傷害，並在目標身後留下一根" + O + "羽毛" + E + "（{f_life}秒）。",
        "skill": "擲出兩把貫穿匕首，各造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "（後續目標{q_fall}%），各留一根羽毛；隨後" +
                 O + "漫天血刃" + E + "收回所有羽毛，每根對經過的敵人造成" + phy("e_dmg", "e_ratio") + "傷害，一次收回命中英雄第3次起" + R +
                 "定身{e_root}秒" + E + "。",
        "skill2": "攻速+" + A + "{w_as}%" + E + "，持續{w_t}秒；期間每次普攻再甩出一片{w_pct}%傷害的羽刃，命中英雄時跑速+{w_ms}%。",
        "ult": "躍向空中，" + A + "{r_air}秒" + E + "內不受傷害和控制，再向前方降下匕首雨，造成" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E +
               "，留下一排羽毛並隨即收回。",
        "names": ("赤落連匕·漫天血刃", "奪命疾翼", "驟羽暴風"),
    },
    "en": {
        "name": "Xayah",
        "attack": "Flings blades. Passive " + O + "Clean Cuts" + E + ": after each spell her next " + A + "3" + E + " attacks (up to 5 "
                  "stored) pierce in a line, {a_pierce}% to other targets, and leave a " + O + "Feather" + E + " behind the target "
                  "for {f_life}s.",
        "skill": "Throws two piercing daggers, each " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + " ({q_fall}% after the "
                 "first target), each leaving a Feather; then " + O + "Bladecaller" + E + " calls every Feather back, each dealing " +
                 phy("e_dmg", "e_ratio") + " to enemies it passes. From the third champion hit of one recall, " + R + "roots" + E +
                 " for " + A + "{e_root}s" + E + ".",
        "skill2": "Gains " + A + "{w_as}%" + E + " attack speed for {w_t}s; each attack throws a second blade for {w_pct}% damage, "
                  "and a champion hit gives {w_ms}% move speed.",
        "ult": "Leaps up, taking no damage or crowd control for " + A + "{r_air}s" + E + ", then rains daggers ahead for " +
               phy("r_dmg", "r_ratio") + " " + O + "physical damage" + E + ", leaving a row of Feathers she calls back at once.",
        "names": ("Double Daggers + Bladecaller", "Deadly Plumage", "Featherstorm"),
    },
    "ko": {
        "name": "자야",
        "attack": "깃날을 던져 공격합니다. 기본 지속 효과 " + O + "관통상" + E + ": 스킬을 쓸 때마다 다음 " + A + "3회" + E + " 공격(최대 5회 "
                  "저장)이 직선으로 관통해 다른 대상에게 {a_pierce}% 피해를 주고, 대상 뒤에 " + O + "깃털" + E + "을 남깁니다({f_life}초).",
        "skill": "관통하는 단검 두 개를 던져 각각 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + "(다음 대상 {q_fall}%), "
                 "깃털을 남깁니다. 이어서 " + O + "깃부르미" + E + "로 깃털을 모두 회수해 지나가는 적에게 " + phy("e_dmg", "e_ratio") +
                 "의 피해, 한 번의 회수에서 세 번째 챔피언 적중부터 " + A + "{e_root}초" + E + " " + R + "속박" + E + ".",
        "skill2": "공격 속도 " + A + "+{w_as}%" + E + " ({w_t}초). 공격마다 {w_pct}% 피해의 깃날을 하나 더 던지고, 챔피언 적중 시 이동 속도 "
                  "+{w_ms}%.",
        "ult": "공중으로 도약해 " + A + "{r_air}초" + E + " 동안 피해와 군중 제어를 받지 않고, 앞쪽에 단검 비를 내려 " + phy("r_dmg", "r_ratio") +
               "의 " + O + "물리 피해" + E + "를 입히며 깃털 한 줄을 남겨 바로 회수합니다.",
        "names": ("깃털 연타·깃부르미", "죽음의 깃", "저항의 비상"),
    },
    "ja": {
        "name": "ザヤ",
        "attack": "羽刃を投げて攻撃。パッシブ " + O + "クリーンカット" + E + "：スキル使用後の" + A + "3回" + E + "の攻撃（最大5回）が直線を貫通し、"
                  "他の対象に{a_pierce}%、対象の後ろに" + O + "羽根" + E + "を残す（{f_life}秒）。",
        "skill": "貫通する短剣を2本投げ、各" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "（後続{q_fall}%）、羽根を残す。続けて" +
                 O + "ブレードコーラー" + E + "で全羽根を回収、通過した敵に" + phy("e_dmg", "e_ratio") + "、1回の回収で3回目以降のチャンピオン命中は" +
                 A + "{e_root}秒" + E + R + "スネア" + E + "。",
        "skill2": "攻撃速度" + A + "+{w_as}%" + E + "（{w_t}秒）。攻撃ごとに{w_pct}%ダメージの羽刃をもう1本投げ、チャンピオン命中で移動速度+{w_ms}%。",
        "ult": "空中に跳び" + A + "{r_air}秒" + E + "ダメージと行動妨害を受けず、前方に短剣の雨で" + phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E +
               "、羽根の列を残してすぐ回収。",
        "names": ("ダブルダガー・ブレードコーラー", "デッドリープルーム", "フェザーストーム"),
    },
}

C = "league_xayah_sfx_"
V = "league_xayah_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_xayah_a_shot": [(C + "attack", 0.5, 0.0)],
    "league_xayah_a_shot_p": [(C + "attack_p", 0.55, 0.0)],
    "league_xayah_a_hit": [(C + "attack_hit", 0.35, 0.0)],
    "league_xayah_f_drop": [(C + "feather", 0.3, 0.0)],
    "league_xayah_q_cast": [(C + "q", 0.55, 0.0), (V + "q", 0.85, 0.05)],
    "league_xayah_q_throw": [(C + "q", 0.4, 0.0)],
    "league_xayah_q_hit": [(C + "attack_hit", 0.4, 0.0)],
    "league_xayah_e_cast": [(C + "e", 0.55, 0.0), (V + "e", 0.8, 0.05)],
    "league_xayah_e_hit": [(C + "e_hit", 0.35, 0.0)],
    "league_xayah_e_root": [(C + "e_root", 0.55, 0.0), (V + "root", 0.8, 0.1)],
    "league_xayah_w_cast": [(C + "w", 0.55, 0.0)],
    "league_xayah_w_blade": [(C + "w_blade", 0.35, 0.0)],
    "league_xayah_r_cast": [(C + "r", 0.6, 0.0), (V + "r", 0.9, 0.05)],
    "league_xayah_r_rain": [(C + "r_rain", 0.6, 0.0)],
    "league_xayah_r_hit": [(C + "attack_hit", 0.45, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("a_pierce", "q_dmg", "q_ratio", "q_fall", "e_dmg", "e_ratio", "w_as", "w_pct", "w_ms", "r_dmg",
                           "r_ratio")}
    v.update({k: secs(p[k]) for k in ("f_life", "e_root", "w_t", "r_air")})
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
    if "Xayah" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Xayah. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
