"""Zed's text (5 languages), sound_info files and his keys in the shared files, numbers from build_zed.P.

    python tools/kit/setup_zed.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in zd/league): text/champion.i18n (league_zed in every language, description + skill_name),
sound/sfx/league_zed_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.82.0, Zed named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/zd/rst.py: 劫 / 影忍法！灭魂劫, 影奥义！诸刃, 影奥义！分身, 影奥义！鬼斩,
禁奥义！瞬狱影杀阵) and Data Dragon 16.19.1 (zh_TW 劫 / 強者特權 / 風魔手裡劍 / 疾風殘影 / 影斬 / 死亡印記, ko 제드 / 약자 멸시 /
예리한 표창 / 살아있는 그림자 / 그림자 베기 / 죽음의 표식, ja ゼド / 弱者必衰 / 風魔手裏剣 / 影分身 / 影薙ぎ / 死の刻印).
The slot names: skill = W, skill2 = Q, ult = R; the passive and the automatic E are told in the attack's text.
No `league_zed_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zed import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_zed"
VERSION = "0.82.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control, untargetable
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
# 10-10 design C at 85% (rig_zed SCALE): the crown 37 over the feet; the idle top -28 fits the ban/pick card's canvas
# (base's rule sets banpick_center only above -28, as for Riven, Vayne and Akali at -28)
VIEW = {"face": {"x": -1, "y": -37}, "center": {"x": 0, "y": -12}}


def phy(k):
    return f"{O}{{{k}_dmg}}{E} + {ADi}{O}{{{k}_ratio}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "劫",
        "attack": O + "影忍法！灭魂劫" + E + "：技能命中英雄后，下次攻击英雄附加其{cw_pct}%最大生命真实伤害（" + A + "{cw_cd}秒" + E + "）。" +
                  O + "影奥义！鬼斩" + E + "（自动，" + A + "{e_cd}秒" + E + "）：旋斩周围，造成" + phy("e") + "伤害，" + R + "减速{e_slow}%" + E + "。",
        "skill": "影子落到敌方英雄脚下（" + A + "{w_life}秒" + E + "），接着鬼斩和诸刃；影子在时模仿他的每次诸刃和鬼斩。" + O + "连招" + E +
                 "：三影齐发，随后影子旁只有一名敌人时换位追击。",
        "skill2": "掷出手里剑，贯穿一条直线：首个敌人受到" + phy("q") + "伤害，之后的受到{q_pen}%。",
        "ult": "对交战中的英雄发动：" + R + "无法选中" + E + "，突进穿过并留下影子（模仿诸刃和鬼斩）与印记，" + A + "{r_pop}秒" + E + "后爆发" + phy("r") +
               "，期间每次命中+" + O + "{r_per}" + E + "（最多3次）。击杀、被包围或被控时换回影子。" + O + "连招" + E + "：R→W→E→Q。",
        "names": ("影奥义！分身", "影奥义！诸刃", "禁奥义！瞬狱影杀阵"),
    },
    "zh-hant": {
        "name": "劫",
        "attack": O + "強者特權" + E + "：技能命中英雄後，下次攻擊英雄附加其{cw_pct}%最大生命真實傷害（" + A + "{cw_cd}秒" + E + "）。" +
                  O + "影斬" + E + "（自動，" + A + "{e_cd}秒" + E + "）：旋斬周圍，造成" + phy("e") + "傷害，" + R + "緩速{e_slow}%" + E + "。",
        "skill": "影子落到敵方英雄腳下（" + A + "{w_life}秒" + E + "），接著影斬和風魔手裡劍；影子在時模仿他的每次手裡劍和影斬。" + O + "連招" + E +
                 "：三影齊發，隨後影子旁只有一名敵人時換位追擊。",
        "skill2": "擲出手裡劍，貫穿一條直線：首個敵人受到" + phy("q") + "傷害，之後的受到{q_pen}%。",
        "ult": "對交戰中的英雄發動：" + R + "無法選取" + E + "，突進穿過並留下影子（模仿手裡劍和影斬）與印記，" + A + "{r_pop}秒" + E + "後爆發" + phy("r") +
               "，期間每次命中+" + O + "{r_per}" + E + "（最多3次）。擊殺、被包圍或被控時換回影子。" + O + "連招" + E + "：R→W→E→Q。",
        "names": ("疾風殘影", "風魔手裡劍", "死亡印記"),
    },
    "en": {
        "name": "Zed",
        "attack": "Wrist blades. " + O + "Contempt for the Weak" + E + ": after his spells hit a champion, his next attack on a champion "
                  "adds {cw_pct}% of its max health as true damage (" + A + "{cw_cd}s" + E + "). " + O + "Shadow Slash" + E +
                  " (automatic, " + A + "{e_cd}s" + E + "): a spin for " + phy("e") + " around him, " + R + "slowing champions {e_slow}%" +
                  E + ".",
        "skill": "Sends his shadow onto an enemy champion (" + A + "{w_life}s" + E + "), then Shadow Slash and Razor Shuriken if ready; while it "
                 "stands it copies every shuriken and slash of his. " + O + "Combo" + E + ": the triple strike; then, with one enemy near the shadow, he swaps to it to "
                 "chase.",
        "skill2": "Throws a shuriken through a line: " + phy("q") + " to the first enemy, {q_pen}% to the rest.",
        "ult": "On a champion in a fight: " + R + "untargetable" + E + ", he dashes through him, leaving a shadow (it copies his shuriken and slash) and a mark that bursts "
               "after " + A + "{r_pop}s" + E + " for " + phy("r") + " plus " + O + "{r_per}" + E + " per hit meanwhile (up to 3). "
               "On a kill, outnumbered or crowd-controlled, he swaps back to the shadow. " + O + "Combo" + E + ": R, W, E, Q.",
        "names": ("Living Shadow", "Razor Shuriken", "Death Mark"),
    },
    "ko": {
        "name": "제드",
        "attack": O + "약자 멸시" + E + ": 스킬이 챔피언에게 적중한 뒤 다음 챔피언 공격은 대상 최대 체력의 {cw_pct}% 고정 피해(" + A + "{cw_cd}초" +
                  E + "). " + O + "그림자 베기" + E + "(자동, " + A + "{e_cd}초" + E + "): 주변을 베어 " + phy("e") + "의 피해, " + R +
                  "{e_slow}% 둔화" + E + ".",
        "skill": "그림자를 적 챔피언 발밑에 보내고(" + A + "{w_life}초" + E + ") 그림자 베기와 예리한 표창을 이어서, 그림자가 있는 동안 표창과 베기를 따라 함. " + O +
                 "연계" + E + ": 삼중 공격, 그림자 곁에 적이 하나면 위치를 바꿔 추격.",
        "skill2": "표창을 던져 직선을 관통: 처음 적에게 " + phy("q") + "의 피해, 이후 적에게 {q_pen}%.",
        "ult": "교전 중인 챔피언에게: " + R + "대상 지정 불가" + E + ", 관통 돌진해 그림자(표창·베기 따라 함)와 표식을 남김. " + A + "{r_pop}초" + E + " 뒤 " +
               phy("r") + " 폭발, 그동안 적중마다 +" + O + "{r_per}" + E + "(최대 3). 처치·포위·군중 제어 시 그림자로 복귀. " + O + "연계" + E +
               ": R→W→E→Q.",
        "names": ("살아있는 그림자", "예리한 표창", "죽음의 표식"),
    },
    "ja": {
        "name": "ゼド",
        "attack": O + "弱者必衰" + E + "：スキルがチャンピオンに命中後、次のチャンピオンへの攻撃が最大体力の{cw_pct}%確定ダメージ（" + A + "{cw_cd}秒" +
                  E + "）。" + O + "影薙ぎ" + E + "（自動、" + A + "{e_cd}秒" + E + "）：周囲を斬り" + phy("e") + "、" + R + "{e_slow}%スロウ" +
                  E + "。",
        "skill": "影を敵チャンピオンの足元に送り（" + A + "{w_life}秒" + E + "）、影薙ぎと手裏剣を続け、影がいる間は手裏剣と影薙ぎを毎回真似る。" + O + "コンボ" + E +
                 "：三連撃、影の近くの敵が一人なら入れ替わって追撃。",
        "skill2": "手裏剣を投げ直線を貫通：最初の敵に" + phy("q") + "、以降の敵に{q_pen}%。",
        "ult": "交戦中のチャンピオンに：" + R + "対象指定不可" + E + "で突き抜け、影（手裏剣と影薙ぎを真似る）と刻印を残す。" + A + "{r_pop}秒" + E + "後" + phy("r") +
               "炸裂、その間の命中ごとに+" + O + "{r_per}" + E + "（最大3）。撃破・包囲・行動妨害で影に戻る。" + O + "コンボ" + E + "：R→W→E→Q。",
        "names": ("影分身", "風魔手裏剣", "死の刻印"),
    },
}

C = "league_zed_sfx_"
V = "league_zed_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
S = "league_zed_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    S + "a_swing": [(C + "attack", 0.45, 0.0)],
    S + "a_hit": [(C + "attack_hit", 0.35, 0.0)],
    S + "cw_hit": [(C + "cw_hit", 0.5, 0.0)],
    S + "q": [(C + "q", 0.45, 0.0), (C + "q_fly", 0.4, 0.05)],
    S + "q_hit": [(C + "q_hit", 0.4, 0.0)],
    S + "w": [(C + "w", 0.5, 0.0)],
    S + "w_land": [(C + "w_land", 0.45, 0.0)],
    S + "w2": [(C + "w2", 0.55, 0.0)],
    S + "e": [(C + "e", 0.5, 0.0)],
    S + "e_hit": [(C + "e_hit", 0.35, 0.0)],
    S + "r": [(C + "r", 0.6, 0.0)],
    S + "r_hit": [(C + "r_hit", 0.55, 0.0), (C + "r_mark", 0.45, 0.1)],
    S + "r_pop": [(C + "r_pop", 0.6, 0.0)],
    S + "vo_q": [(V + "q", 0.8, 0.0)],
    S + "vo_w": [(V + "w", 0.8, 0.0)],
    S + "vo_e": [(V + "e", 0.8, 0.0)],
    S + "vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("cw_pct", "e_dmg", "e_ratio", "e_slow", "q_dmg", "q_ratio", "q_pen", "r_dmg", "r_ratio", "r_per")}
    v.update({k: secs(p[k]) for k in ("cw_cd", "e_cd", "w_life", "r_pop")})
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
    if "Zed" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Zed. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
