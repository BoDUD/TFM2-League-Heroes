"""Samira's text (5 languages), sound_info files and her keys in the shared files, numbers from build_samira.P.

    python tools/kit/setup_samira.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_samira in every language, description + skill_name),
sound/sfx/league_samira_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.65.0, Samira named). Only her keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (莎弥拉 / 沙漠玫瑰, 悍勇本色, 交火, 锋旋, 狂飙, 炼狱扳机) and Data Dragon 16.19.1
(zh_TW 煞蜜拉 / 荒漠薔薇, 敢死風采, 狂戰本能, 劍刃風暴, 狂野突進, 地獄火狂襲; ko 사미라 / 사막의 장미, 무모한 충동, 천부적 재능,
원형 검무, 거침없는 질주, 지옥불 난사; ja サミーラ / 砂漠の薔薇, デアデビルインパルス, フレア, ブレードワール, ワイルドラッシュ,
インフェルノトリガー). skill2 is named after E, which leads the combo (W in the text).
No `league_samira_attack` sound: the engine would play it at the start of every attack; the shot's and the swing's
sounds play from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_samira import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_samira"
VERSION = "0.65.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -38}, "center": {"x": 0, "y": -12}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def mag(d, r):
    return f"{M}{{{d}}}{E} + {ADi}{M}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "莎弥拉",
        "attack": "远处开枪，近身挥刀并附加" + mag("pm_dmg", "pm_ratio") + "魔法伤害。被动" + O + "悍勇本色" + E + "：用和上一次不同的招式命中英雄，"
                  "评价E→S升一级，每级移速+{g_ms}%，{g_t}秒没打到英雄清零。攻击被控制的英雄时冲上去" + R + "击飞{j_up}秒" + E + "。",
        "skill": "身边有敌人时挥刀斩击前方，否则开枪打中第一个敌人，造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "。",
        "skill2": O + "狂飙" + E + "：冲到敌方英雄身后，对周围敌人造成" + mag("e_dmg", "e_ratio") + M + "魔法伤害" + E + "，攻速+{e_as}%。随即" +
                  O + "锋旋" + E + "：旋转{w_t}秒砍两次，每次" + phy("w_dmg", "w_ratio") + "，期间受到的攻击伤害-{w_red}%。击杀英雄刷新冷却。",
        "ult": "评价到" + A + "S" + E + "时才会施放：原地旋转连射" + A + "{r_t}秒" + E + "，每{r_period}秒向周围所有敌人各开一枪，造成" +
               phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "，期间生命偷取{r_vamp}%。放完评价清零。",
        "names": ("交火", "狂飙", "炼狱扳机"),
    },
    "zh-hant": {
        "name": "煞蜜拉",
        "attack": "遠處開槍，近身揮刀並附加" + mag("pm_dmg", "pm_ratio") + "魔法傷害。被動" + O + "敢死風采" + E + "：用和上一次不同的招式命中英雄，"
                  "評價E→S升一級，每級跑速+{g_ms}%，{g_t}秒沒打到英雄清零。攻擊被控制的英雄時衝上去" + R + "擊飛{j_up}秒" + E + "。",
        "skill": "身邊有敵人時揮刀斬擊前方，否則開槍打中第一個敵人，造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "。",
        "skill2": O + "狂野突進" + E + "：衝到敵方英雄身後，對周圍敵人造成" + mag("e_dmg", "e_ratio") + M + "魔法傷害" + E + "，攻速+{e_as}%。隨即" +
                  O + "劍刃風暴" + E + "：旋轉{w_t}秒砍兩次，每次" + phy("w_dmg", "w_ratio") + "，期間受到的攻擊傷害-{w_red}%。擊殺英雄刷新冷卻。",
        "ult": "評價到" + A + "S" + E + "時才會施放：原地旋轉連射" + A + "{r_t}秒" + E + "，每{r_period}秒向周圍所有敵人各開一槍，造成" +
               phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "，期間生命偷取{r_vamp}%。放完評價清零。",
        "names": ("狂戰本能", "狂野突進", "地獄火狂襲"),
    },
    "en": {
        "name": "Samira",
        "attack": "Shoots from range; in melee range she slashes for " + mag("pm_dmg", "pm_ratio") + " bonus " + M + "magic damage" + E +
                  ". Passive " + O + "Daredevil Impulse" + E + ": a champion hit by a move unlike her last raises her Style a "
                  "grade, E to S, +{g_ms}% move speed each; it resets after {g_t}s without one. Attacking a champion in crowd "
                  "control dashes her to it and " + R + "knock it up" + E + " for {j_up}s.",
        "skill": "With an enemy beside her she slashes in front of her, otherwise she shoots the first enemy in line: " +
                 phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ".",
        "skill2": O + "Wild Rush" + E + ": dashes past an enemy champion, dealing " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  " around her and gaining {e_as}% attack speed. Then " + O + "Blade Whirl" + E + ": spins for {w_t}s, slashing twice "
                  "for " + phy("w_dmg", "w_ratio") + " each and taking {w_red}% less damage from attacks. A champion kill refreshes "
                  "the cooldown.",
        "ult": "Only at Style " + A + "S" + E + ": spins in place firing for " + A + "{r_t}s" + E + ", every {r_period}s a shot at every enemy "
               "around her for " + phy("r_dmg", "r_ratio") + " " + O + "physical damage" + E + ", with {r_vamp}% life steal. Spends "
               "her Style.",
        "names": ("Flair", "Wild Rush", "Inferno Trigger"),
    },
    "ko": {
        "name": "사미라",
        "attack": "멀리서는 사격, 근접하면 베어 " + mag("pm_dmg", "pm_ratio") + "의 추가 " + M + "마법 피해" + E + ". 기본 지속 효과 " + O +
                  "무모한 충동" + E + ": 직전과 다른 공격으로 챔피언을 맞히면 스타일 등급 E→S 상승, 등급당 이동 속도 +{g_ms}%, "
                  "{g_t}초간 챔피언을 못 맞히면 초기화. 군중 제어된 챔피언을 공격하면 돌진해 {j_up}초 " + R + "에어본" + E + ".",
        "skill": "곁에 적이 있으면 앞을 베고, 아니면 처음 맞는 적에게 사격해 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + ".",
        "skill2": O + "거침없는 질주" + E + ": 적 챔피언 뒤로 돌진해 주변 적에게 " + mag("e_dmg", "e_ratio") + "의 " + M + "마법 피해" + E +
                  ", 공격 속도 +{e_as}%. 이어서 " + O + "원형 검무" + E + ": {w_t}초간 회전하며 두 번 " + phy("w_dmg", "w_ratio") +
                  " 피해, 받는 공격 피해 -{w_red}%. 챔피언 처치 시 재사용 대기시간 초기화.",
        "ult": "스타일 " + A + "S" + E + "일 때만: 제자리에서 회전하며 " + A + "{r_t}초" + E + "간 {r_period}초마다 주변 모든 적을 쏴 " +
               phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + ", 생명력 흡수 {r_vamp}%. 스타일을 소모합니다.",
        "names": ("천부적 재능", "거침없는 질주", "지옥불 난사"),
    },
    "ja": {
        "name": "サミーラ",
        "attack": "遠くは射撃、近くは斬って" + mag("pm_dmg", "pm_ratio") + "の追加" + M + "魔法ダメージ" + E + "。パッシブ " + O +
                  "デアデビルインパルス" + E + "：直前と違う技でチャンピオンに当てるとスタイルE→S上昇、1段ごと移動速度+{g_ms}%、"
                  "{g_t}秒当てないとリセット。CC中のチャンピオンへの攻撃で突進し{j_up}秒" + R + "ノックアップ" + E + "。",
        "skill": "近くに敵がいれば前方を斬り、いなければ最初の敵を撃ち" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "。",
        "skill2": O + "ワイルドラッシュ" + E + "：敵チャンピオンの背後へ突進し周囲に" + mag("e_dmg", "e_ratio") + "の" + M + "魔法ダメージ" +
                  E + "、攻撃速度+{e_as}%。続けて" + O + "ブレードワール" + E + "：{w_t}秒回転し2回" + phy("w_dmg", "w_ratio") +
                  "、受ける攻撃ダメージ-{w_red}%。キルでクールダウン解消。",
        "ult": "スタイル" + A + "S" + E + "の時だけ：その場で回転し" + A + "{r_t}秒" + E + "、{r_period}秒ごとに周囲の全ての敵を撃ち" +
               phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "、ライフスティール{r_vamp}%。スタイルを消費。",
        "names": ("フレア", "ワイルドラッシュ", "インフェルノトリガー"),
    },
}

C = "league_samira_sfx_"
V = "league_samira_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_samira_a_shot": [(C + "shot", 0.45, 0.0)],
    "league_samira_a_hit": [(C + "hit", 0.3, 0.0)],
    "league_samira_a_swing": [(C + "swing", 0.4, 0.0)],
    "league_samira_a_slash_hit": [(C + "cut", 0.4, 0.0)],
    "league_samira_j_dash": [(C + "dash", 0.5, 0.0)],
    "league_samira_q_cock": [(C + "q_cock", 0.4, 0.0)],
    "league_samira_q_shot": [(C + "q_shot", 0.6, 0.0)],
    "league_samira_q_hit": [(C + "q_hit", 0.4, 0.0)],
    "league_samira_q_swing": [(C + "q_swing", 0.55, 0.0)],
    "league_samira_q_slash_hit": [(C + "q_cut", 0.45, 0.0)],
    "league_samira_e_cast": [(C + "e_cast", 0.55, 0.0)],
    "league_samira_e_hit": [(C + "e_hit", 0.45, 0.0)],
    "league_samira_e_reset": [(C + "style", 0.6, 0.0)],
    "league_samira_w_cast": [(C + "w_cast", 0.55, 0.0)],
    "league_samira_w_slash": [(C + "w_hit", 0.45, 0.0)],
    "league_samira_w_hit": [(C + "cut", 0.3, 0.0)],
    "league_samira_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_samira_r_loop": [(C + "r_loop", 0.5, 0.0)],
    "league_samira_r_shot": [(C + "r_shot", 0.3, 0.0)],
    "league_samira_r_hit": [(C + "hit", 0.15, 0.0)],
    "league_samira_g_up": [(C + "style", 0.35, 0.0)],
    "league_samira_g_s": [(C + "s", 0.6, 0.0)],
    "league_samira_vo_q": [(V + "q", 0.75, 0.0)],
    "league_samira_vo_q2": [(V + "q2", 0.75, 0.0)],
    "league_samira_vo_e": [(V + "e", 0.8, 0.0)],
    "league_samira_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("pm_dmg", "pm_ratio", "g_ms", "q_dmg", "q_ratio", "e_dmg", "e_ratio", "e_as", "w_dmg",
                           "w_ratio", "w_red", "r_dmg", "r_ratio", "r_vamp")}
    for k in ("g_t", "j_up", "w_t", "r_t", "r_period"):
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
    if "Samira" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Samira. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
