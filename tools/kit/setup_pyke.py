"""Pyke's text (5 languages), sound_info files and his keys in the shared files, numbers from build_pyke.P.

    python tools/kit/setup_pyke.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_pyke in every language, description + skill_name),
sound/sfx/league_pyke_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.67.0, Pyke named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (派克 / 血港鬼影, 溺水之幸, 透骨尖钉, 幽潭潜行, 魅影浪洄, 涌泉之恨) and Data Dragon
16.19.1 (zh_TW 派克 / 血港開膛手, 血港淹禮, 刺骨串叉, 幽海深潛, 溺流鬼影, 汪洋死域; ko 파이크 / 핏빛 항구의 학살자, 가라앉은 자들의
축복, 뼈 작살, 유령 잠수, 망자의 물살, 깊은 바다의 처형; ja パイク / ブラッドハーバーの殺戮鬼, 沈みし者の力, ボーンスキューア,
ゴーストウォーター, 亡者の引き波, 水底の急襲). skill2 is named after E (its dash and stun; the icon is E's), W in the text.
No `league_pyke_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_pyke import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_pyke"
VERSION = "0.67.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
W = "<#ffffffff>"      # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
# face: the bald crown 40 px over the feet, 1.5 px ahead of the head centre (x +8.5; tfm2_ase.py face took the
# harpoon over his head for the crown); banpick: the card's canvas shows 40 px, -40 - y to -y round the pivot; at 0
# (base's -39 - top rule for the harpoon's tip) his legs were all under it (「派克在bp界面腿都看不到了」): -11 shows
# him whole, the harpoon's tip at -28 to the soles at +11 (after rig_pyke.SHRINK)
VIEW = {"face": {"x": 8, "y": -26}, "center": {"x": 0, "y": -6}, "banpick_center": {"x": 0, "y": -11}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def grn(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


def tru(d, r):
    return f"{W}{{{d}}}{E} + {ADi}{W}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "派克",
        "attack": "鱼叉挥砍。被动" + O + "溺水之幸" + E + "：挨打积攒灰血（最多{p_lv}层），潜行或{p_calm}秒没挨打时每层回复" +
                  grn("p_heal", "p_heal_r") + G + "生命" + E + "。无法靠生命成长，攻击力成长更高。",
        "skill": "英雄贴身时戳刺，否则蓄力扔出鱼叉，命中第一个敌人：" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "，" +
                 "减速{q_slow}%，鱼叉命中的会被" + R + "拉回" + E + "。",
        "skill2": O + "幽潭潜行" + E + "：潜行并加速，回复灰血。随即" + O + "魅影浪洄" + E + "：冲过敌方英雄，魅影随后飞回他身边，" +
                  "途经的英雄受到" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "并" + R + "晕眩{e_stun}秒" + E + "。",
        "ult": "X形打击：英雄受到" + tru("r_dmg", "r_ratio") + W + "真实伤害" + E + "，低于此值" + R + "被处决" + E +
               "，否则只受一半；其他敌人受一半物理伤害。有英雄死在X里时派克闪到其身上并" + A + "刷新大招" + E + "。",
        "names": ("透骨尖钉", "魅影浪洄", "涌泉之恨"),
    },
    "zh-hant": {
        "name": "派克",
        "attack": "魚叉揮砍。被動" + O + "血港淹禮" + E + "：挨打累積灰血（最多{p_lv}層），潛行或{p_calm}秒沒挨打時每層回復" +
                  grn("p_heal", "p_heal_r") + G + "生命" + E + "。無法靠生命成長，攻擊力成長更高。",
        "skill": "英雄貼身時戳刺，否則蓄力擲出魚叉，命中第一個敵人：" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "，" +
                 "緩速{q_slow}%，魚叉命中的會被" + R + "拉回" + E + "。",
        "skill2": O + "幽海深潛" + E + "：潛行並加速，回復灰血。隨即" + O + "溺流鬼影" + E + "：衝過敵方英雄，鬼影隨後飛回他身邊，" +
                  "途經的英雄受到" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "並" + R + "暈眩{e_stun}秒" + E + "。",
        "ult": "X形打擊：英雄受到" + tru("r_dmg", "r_ratio") + W + "真實傷害" + E + "，低於此值" + R + "被處決" + E +
               "，否則只受一半；其他敵人受一半物理傷害。有英雄死在X裡時派克閃到其身上並" + A + "刷新大招" + E + "。",
        "names": ("刺骨串叉", "溺流鬼影", "汪洋死域"),
    },
    "en": {
        "name": "Pyke",
        "attack": "Harpoon slashes. Passive " + O + "Gift of the Drowned Ones" + E + ": hits store grey health (up to {p_lv} "
                  "stacks); camouflaged or unhit for {p_calm}s he heals " + grn("p_heal", "p_heal_r") + " " + G + "health" + E +
                  " a stack. Little health growth, more attack damage growth.",
        "skill": "Stabs a champion beside him, otherwise charges and throws his harpoon at the first enemy: " +
                 phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ", a {q_slow}% slow, and the harpoon " + R +
                 "pulls" + E + " it to him.",
        "skill2": O + "Ghostwater Dive" + E + ": camouflage and a burst of speed, grey health healed. Then " + O +
                  "Phantom Undertow" + E + ": dashes through an enemy champion; a phantom rushes back to him, dealing " +
                  phy("e_dmg", "e_ratio") + " " + O + "physical damage" + E + " to champions on its way and " + R +
                  "stunning" + E + " them for {e_stun}s.",
        "ult": "Strikes an X: champions take " + tru("r_dmg", "r_ratio") + " " + W + "true damage" + E + " - below that "
               "they are " + R + "executed" + E + ", otherwise they take half; other enemies take half as physical damage. "
               "A champion dying in the X blinks him to it and " + A + "refreshes the ult" + E + ".",
        "names": ("Bone Skewer", "Phantom Undertow", "Death From Below"),
    },
    "ko": {
        "name": "파이크",
        "attack": "작살 공격. 기본 지속 효과 " + O + "가라앉은 자들의 축복" + E + ": 피격 시 회색 체력 축적(최대 {p_lv}중첩), 위장 중이거나 "
                  "{p_calm}초간 피격되지 않으면 중첩당 " + grn("p_heal", "p_heal_r") + " " + G + "체력 회복" + E +
                  ". 체력 성장 낮음, 공격력 성장 높음.",
        "skill": "곁의 챔피언은 찌르고, 아니면 충전 후 작살을 던져 첫 적에게 " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" +
                 E + ", {q_slow}% 둔화, 작살에 맞은 적을 " + R + "끌어옵니다" + E + ".",
        "skill2": O + "유령 잠수" + E + ": 위장하고 가속, 회색 체력 회복. 이어서 " + O + "망자의 물살" + E + ": 적 챔피언을 지나 돌진, "
                  "유령이 돌아오며 지나는 챔피언에게 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + ", {e_stun}초 " +
                  R + "기절" + E + ".",
        "ult": "X자 타격: 챔피언에게 " + tru("r_dmg", "r_ratio") + "의 " + W + "고정 피해" + E + ", 그 이하면 " + R + "처형" + E +
               ", 아니면 절반만. 다른 적은 절반의 물리 피해. X 안에서 챔피언이 죽으면 그 위치로 점멸하고 " + A + "궁극기 초기화" +
               E + ".",
        "names": ("뼈 작살", "망자의 물살", "깊은 바다의 처형"),
    },
    "ja": {
        "name": "パイク",
        "attack": "銛で斬る。パッシブ " + O + "沈みし者の力" + E + "：被弾でグレー体力を蓄積（最大{p_lv}）、ステルス中か{p_calm}秒被弾"
                  "なしで1つごとに" + grn("p_heal", "p_heal_r") + G + "回復" + E + "。体力成長は低く攻撃力成長は高い。",
        "skill": "隣のチャンピオンは突き、いなければ溜めて銛を投げ最初の敵に" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" +
                 E + "、{q_slow}%スロウ、銛が当たると" + R + "引き寄せ" + E + "。",
        "skill2": O + "ゴーストウォーター" + E + "：ステルスと加速、グレー体力回復。続けて" + O + "亡者の引き波" + E +
                  "：敵チャンピオンを突き抜け、戻る幻影が通過したチャンピオンに" + phy("e_dmg", "e_ratio") + "の" + O +
                  "物理ダメージ" + E + "と{e_stun}秒" + R + "スタン" + E + "。",
        "ult": "X字の斬撃：チャンピオンに" + tru("r_dmg", "r_ratio") + "の" + W + "確定ダメージ" + E + "、それ以下なら" + R + "処刑" +
               E + "、それ以外は半分。他の敵は半分の物理ダメージ。X内でチャンピオンが死ぬとその場所へ移動し" + A + "R再使用可" + E + "。",
        "names": ("ボーンスキューア", "亡者の引き波", "水底の急襲"),
    },
}

C = "league_pyke_sfx_"
V = "league_pyke_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_pyke_a_swing": [(C + "swing", 0.4, 0.0)],
    "league_pyke_a_hit": [(C + "hit", 0.35, 0.0)],
    "league_pyke_q_stab": [(C + "q_stab", 0.5, 0.0)],
    "league_pyke_q_stab_hit": [(C + "q_stab_hit", 0.45, 0.0)],
    "league_pyke_q_charge": [(C + "q_charge", 0.4, 0.0)],
    "league_pyke_q_throw": [(C + "q_throw", 0.55, 0.0)],
    "league_pyke_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_pyke_w_cast": [(C + "w_cast", 0.5, 0.0)],
    "league_pyke_e_dash": [(C + "e_dash", 0.55, 0.0)],
    "league_pyke_e_return": [(C + "e_return", 0.45, 0.0)],
    "league_pyke_e_hit": [(C + "e_hit", 0.5, 0.0)],
    "league_pyke_r_cast": [(C + "r_cast", 0.55, 0.0)],
    "league_pyke_r_strike": [(C + "r_strike", 0.6, 0.0)],
    "league_pyke_r_hit": [(C + "hit", 0.25, 0.0)],
    "league_pyke_r_reset": [(C + "r_reset", 0.6, 0.0)],
    "league_pyke_p_heal": [(C + "p_heal", 0.35, 0.0)],
    "league_pyke_vo_q": [(V + "q", 0.8, 0.0)],
    "league_pyke_vo_q2": [(V + "q2", 0.8, 0.0)],
    "league_pyke_vo_e": [(V + "e", 0.8, 0.0)],
    "league_pyke_vo_r": [(V + "r", 0.9, 0.05)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_lv", "p_heal", "p_heal_r", "q_dmg", "q_ratio", "q_slow", "e_dmg", "e_ratio", "r_dmg",
                           "r_ratio")}
    for k in ("p_calm", "e_stun"):
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
    if "Pyke" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Pyke. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
