"""Irelia's text (5 languages), sound_info files and her keys in the shared files, numbers from build_irelia.P.

    python tools/kit/setup_irelia.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_irelia in every language, description + skill_name),
sound/sfx/league_irelia_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (VERSION, Irelia named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (艾瑞莉娅 / 刀锋舞者 - the name and title slots are swapped there, as for Viktor;
艾欧尼亚热诚, 利刃冲击, 距破之舞, 比翼双刃, 先锋之刃) and Data Dragon 16.20.1 (zh_TW 伊瑞莉雅 / 舞劍靈使, 愛歐尼亞狂熱,
利刃衝擊, 不屈祕舞, 無瑕重刃, 護劍化形; ko 이렐리아 / 칼날 무희, 아이오니아의 열정, 칼날 쇄도, 저항의 춤, 쌍검협무, 선봉진격검;
ja イレリア / 飛刃の舞い手, アイオニアの熱情, 瞬刃, 不屈の舞, 無欠の連舞, 先陣の刃). The attack text carries the passive;
skill = Q, skill2 = E with W folded in, ult = R. No combo line in the texts (R -> E and E's mark for Q live in the kit
and the README).
No `league_irelia_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_irelia import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_irelia"
VERSION = "0.100.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: set from tfm2_ase.py face once the sprite is in
VIEW = {"face": {"x": 0, "y": -31}, "center": {"x": 0, "y": -12}}   # the dense idle (league.dll draws her at PPU 2)


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def hp(d, r):
    return f"{{{d}}} + {ADi}{{{r}}}%"


TEXT = {
    "zh-hans": {
        "name": "艾瑞莉娅",
        "attack": "被动" + O + "艾欧尼亚热诚" + E + "：Q命中或技能命中英雄时获得1层，每层攻速+{p_as}%，最多" + A + "{p_n}层{p_t}秒" + E +
                  "；满层时普攻额外造成" + phy("p_dmg", "p_ratio") + O + "物理伤害" + E + "。",
        "skill": "冲向目标造成" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "并回复" + hp("q_heal", "q_heal_r") + "生命。目标带" +
                 O + "印记" + E + "或被击杀时立刻再冲一次，一次最多" + A + "{q_n}段" + E + "。",
        "skill2": "两把飞刃合拢，路线上的敌人受到" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "并" + R + "眩晕{e_stun}秒" + E +
                  "，英雄被" + O + "印记" + E + "。冷却时贴身改用" + O + "距破之舞" + E + "：蓄力减免{w_dr}%普攻伤害，再斩出" +
                  phy("w_dmg", "w_ratio") + O + "物理伤害" + E + "。",
        "ult": "射出刃群，碰到英雄炸开，扇形内敌人受到" + phy("r_dmg", "r_ratio") + O + "物理伤害" + E + "、" + R + "减速{r_slow}%并缴械" +
               "{r_dis}秒" + E + "，英雄被" + O + "印记" + E + "；留下刃墙" + A + "{r_wall_t}秒" + E + "，墙内敌人减速{r_wslow}%。",
        "names": ("利刃冲击", "比翼双刃", "先锋之刃"),
    },
    "zh-hant": {
        "name": "伊瑞莉雅",
        "attack": "被動" + O + "愛歐尼亞狂熱" + E + "：Q命中或技能命中英雄時獲得1層，每層攻速+{p_as}%，最多" + A + "{p_n}層{p_t}秒" + E +
                  "；滿層時普攻額外造成" + phy("p_dmg", "p_ratio") + O + "物理傷害" + E + "。",
        "skill": "衝向目標造成" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "並回復" + hp("q_heal", "q_heal_r") + "生命。目標帶" +
                 O + "印記" + E + "或被擊殺時立刻再衝一次，一次最多" + A + "{q_n}段" + E + "。",
        "skill2": "兩把飛刃合攏，路線上的敵人受到" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "並" + R + "暈眩{e_stun}秒" + E +
                  "，英雄被" + O + "印記" + E + "。冷卻時貼身改用" + O + "不屈祕舞" + E + "：蓄力減免{w_dr}%普攻傷害，再斬出" +
                  phy("w_dmg", "w_ratio") + O + "物理傷害" + E + "。",
        "ult": "射出刃群，碰到英雄炸開，扇形內敵人受到" + phy("r_dmg", "r_ratio") + O + "物理傷害" + E + "、" + R + "緩速{r_slow}%並繳械" +
               "{r_dis}秒" + E + "，英雄被" + O + "印記" + E + "；留下刃牆" + A + "{r_wall_t}秒" + E + "，牆內敵人緩速{r_wslow}%。",
        "names": ("利刃衝擊", "無瑕重刃", "護劍化形"),
    },
    "en": {
        "name": "Irelia",
        "attack": "Passive " + O + "Ionian Fervor" + E + ": Bladesurge hits and spell hits on champions grant a stack of +{p_as}% "
                  "Attack Speed (max " + A + "{p_n}" + E + ", " + A + "{p_t}s" + E + "). At full stacks her attacks deal " +
                  phy("p_dmg", "p_ratio") + " " + O + "physical damage" + E + " more.",
        "skill": "Dashes to the target, dealing " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + " and healing " +
                 hp("q_heal", "q_heal_r") + ". If the target was " + O + "Marked" + E + " or dies, she dashes again at once, up to " +
                 A + "{q_n}" + E + " dashes a cast.",
        "skill2": "Two blades converge: enemies between take " + phy("e_dmg", "e_ratio") + " " + O + "physical damage" + E + " and are " +
                  R + "stunned {e_stun}s" + E + "; champions are " + O + "Marked" + E + ". On cooldown, up close she uses " + O +
                  "Defiant Dance" + E + ": a guard taking {w_dr}% less attack damage, then a strike for " + phy("w_dmg", "w_ratio") +
                  " " + O + "physical damage" + E + ".",
        "ult": "Fires blades that burst on the first champion: enemies in the cone take " + phy("r_dmg", "r_ratio") + " " + O +
               "physical damage" + E + ", are " + R + "slowed {r_slow}% and disarmed {r_dis}s" + E + ", champions " + O + "Marked" + E +
               ". A blade wall stays " + A + "{r_wall_t}s" + E + ", slowing enemies inside {r_wslow}%.",
        "names": ("Bladesurge", "Flawless Duet", "Vanguard's Edge"),
    },
    "ko": {
        "name": "이렐리아",
        "attack": "기본 지속 효과 " + O + "아이오니아의 열정" + E + ": 칼날 쇄도 적중, 스킬의 챔피언 적중마다 공격 속도 +{p_as}% 중첩(최대 " +
                  A + "{p_n}" + E + ", " + A + "{p_t}초" + E + "). 최대 중첩 시 기본 공격이 " + phy("p_dmg", "p_ratio") + "의 " + O +
                  "물리 피해" + E + "를 추가로.",
        "skill": "대상에게 돌진해 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + ", 체력 " + hp("q_heal", "q_heal_r") +
                 " 회복. 대상이 " + O + "표식" + E + " 상태거나 죽으면 즉시 다시 돌진(한 번에 최대 " + A + "{q_n}" + E + "회).",
        "skill2": "두 칼날이 모여 사이의 적에게 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + "와 " + R + "{e_stun}초 기절" + E +
                  ", 챔피언에 " + O + "표식" + E + ". 재사용 대기 중 근접하면 " + O + "저항의 춤" + E + ": 받는 기본 공격 피해 {w_dr}% 감소 후 " +
                  phy("w_dmg", "w_ratio") + "의 " + O + "물리 피해" + E + ".",
        "ult": "칼날이 첫 챔피언에서 터져 부채꼴의 적에게 " + phy("r_dmg", "r_ratio") + "의 " + O + "물리 피해" + E + ", " + R +
               "{r_slow}% 둔화·{r_dis}초 무장 해제" + E + ", 챔피언에 " + O + "표식" + E + ". 칼날 벽이 " + A + "{r_wall_t}초" + E +
               " 남아 안의 적 {r_wslow}% 둔화.",
        "names": ("칼날 쇄도", "쌍검협무", "선봉진격검"),
    },
    "ja": {
        "name": "イレリア",
        "attack": "パッシブ" + O + "アイオニアの熱情" + E + "：瞬刃の命中、スキルのチャンピオン命中ごとに攻撃速度+{p_as}%（最大" + A +
                  "{p_n}" + E + "、" + A + "{p_t}秒" + E + "）。最大時、通常攻撃が" + phy("p_dmg", "p_ratio") + "の" + O + "物理ダメージ" + E +
                  "を追加。",
        "skill": "対象へダッシュし" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "、体力" + hp("q_heal", "q_heal_r") +
                 "回復。対象が" + O + "マーク" + E + "付きか倒れると即座に再ダッシュ（1回で最大" + A + "{q_n}" + E + "回）。",
        "skill2": "2本の刃が合わさり間の敵に" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "と" + R + "{e_stun}秒スタン" + E +
                  "、チャンピオンに" + O + "マーク" + E + "。CD中、近くでは" + O + "不屈の舞" + E + "：通常攻撃のダメージ{w_dr}%軽減後、" +
                  phy("w_dmg", "w_ratio") + "の" + O + "物理ダメージ" + E + "。",
        "ult": "刃が最初のチャンピオンで炸裂、扇状の敵に" + phy("r_dmg", "r_ratio") + "の" + O + "物理ダメージ" + E + "、" + R +
               "{r_slow}%スロウと{r_dis}秒武装解除" + E + "、チャンピオンに" + O + "マーク" + E + "。刃の壁が" + A + "{r_wall_t}秒" + E +
               "残り、内側の敵に{r_wslow}%スロウ。",
        "names": ("瞬刃", "無欠の連舞", "先陣の刃"),
    },
}

C = "league_irelia_sfx_"
V = "league_irelia_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_irelia_swing": [(C + "swing", 0.35, 0.0)],
    "league_irelia_hit": [(C + "hit", 0.35, 0.0)],
    "league_irelia_p_max": [(C + "p_max", 0.45, 0.0)],
    "league_irelia_q_cast": [(C + "q_cast", 0.5, 0.0)],
    "league_irelia_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_irelia_q_reset": [(C + "q_reset", 0.55, 0.0)],
    "league_irelia_w_cast": [(C + "w_cast", 0.45, 0.0)],
    "league_irelia_w_slash": [(C + "w_slash", 0.55, 0.0)],
    "league_irelia_w_hit": [(C + "w_hit", 0.5, 0.0)],
    "league_irelia_e_cast": [(C + "e_cast", 0.5, 0.0)],
    "league_irelia_e_stop": [(C + "e_stop", 0.45, 0.0)],
    "league_irelia_e_hit": [(C + "e_hit", 0.55, 0.0)],
    "league_irelia_r_cast": [(C + "r_cast", 0.5, 0.0)],
    "league_irelia_r_launch": [(C + "r_launch", 0.55, 0.0)],
    "league_irelia_r_hit": [(C + "r_hit", 0.6, 0.0)],
    "league_irelia_r_wall": [(C + "r_wall", 0.4, 0.0)],
    "league_irelia_vo_q": [(V + "q", 0.85, 0.0)],
    "league_irelia_vo_w": [(V + "w", 0.85, 0.0)],
    "league_irelia_vo_e": [(V + "e", 0.85, 0.0)],
    "league_irelia_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def values(p):
    v = {k: p[k] for k in ("p_as", "p_n", "p_dmg", "p_ratio", "q_dmg", "q_ratio", "q_heal", "q_heal_r", "q_n", "e_dmg",
                           "e_ratio", "w_dr", "w_dmg", "w_ratio", "r_dmg", "r_ratio", "r_slow", "r_wslow")}
    for k in ("p_t", "e_stun", "r_dis", "r_wall_t"):
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
    if "Irelia" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Irelia. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
