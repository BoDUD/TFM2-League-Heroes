"""Talon's text (5 languages), sound_info files and his keys in the shared files, numbers from build_talon.P.

    python tools/kit/setup_talon.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in tl/league): text/champion.i18n (league_talon in every language, description + skill_name),
sound/sfx/league_talon_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.87.0, Talon named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/tl/rst.py: 泰隆 / 刀锋之影, 刀锋之末, 诺克萨斯式外交, 斩草除根, 刺客之道, 暗影突袭)
and Data Dragon 16.19.1 (zh_TW 塔隆 / 終焉殘刃 / 諾城王道 / 迴力匕首 / 刺客身法 / 暗影突襲, ko 탈론 / 검의 최후 / 녹서스식 외교 /
갈퀴손 / 암살자의 길 / 그림자 공격, ja タロン / 血塗られし慈悲 / ノクサスの刃 / 飛燕手裏剣 / 暗殺者の跳躍 / シャドウアサルト).
The slot names: skill = W, skill2 = Q, ult = R; the passive and the automatic E are told in the attack's text.
No combo sentence in any text (the user's rule): the combos live in build_talon.py and the README.
No `league_talon_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_talon import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_talon"
VERSION = "0.87.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -34}, "center": {"x": 0, "y": -14}}


def phy(k):
    return f"{O}{{{k}_dmg}}{E} + {ADi}{O}{{{k}_ratio}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "泰隆",
        "attack": "腕刃攻击。" + O + "刀锋之末" + E + "：技能命中英雄叠一层伤口，叠满3层后下次普攻使其" + O + "流血" + E + "，" + A +
                  "{p_bleed}秒" + E + "内受到" + phy("p") + "伤害。" + O + "刺客之道" + E + "（自动，" + A + "{e_cd}秒" + E +
                  "）：收刀或Q击杀时身边有{e_crowd}名敌方英雄，就翻身跃开并加速。",
        "skill": "扇形掷出飞刀造成" + phy("w") + "伤害，随后飞刀收回，造成" + phy("w2") + "伤害并" + R + "减速{w_slow}%" + E + "。",
        "skill2": "跃向目标造成" + phy("q") + "伤害；目标就在身边时改为原地捅刺，造成{q_crit}%暴击伤害。击杀目标回复" + G + "{q_heal}" + E +
                  "生命并返还冷却。",
        "ult": "向四周甩出一圈飞刀造成" + phy("r") + "伤害，随后" + O + "隐身" + E + A + "{r_inv}秒" + E + "、移速+{r_haste}%；隐身结束或攻击时"
               "飞刀收回，再次造成同样伤害。",
        "names": ("斩草除根", "诺克萨斯式外交", "暗影突袭"),
    },
    "zh-hant": {
        "name": "塔隆",
        "attack": "腕刃攻擊。" + O + "終焉殘刃" + E + "：技能命中英雄疊一層傷口，疊滿3層後下次普攻使其" + O + "流血" + E + "，" + A +
                  "{p_bleed}秒" + E + "內受到" + phy("p") + "傷害。" + O + "刺客身法" + E + "（自動，" + A + "{e_cd}秒" + E +
                  "）：收刀或Q擊殺時身邊有{e_crowd}名敵方英雄，就翻身躍開並加速。",
        "skill": "扇形擲出飛刀造成" + phy("w") + "傷害，隨後飛刀收回，造成" + phy("w2") + "傷害並" + R + "緩速{w_slow}%" + E + "。",
        "skill2": "躍向目標造成" + phy("q") + "傷害；目標就在身邊時改為原地捅刺，造成{q_crit}%暴擊傷害。擊殺目標回復" + G + "{q_heal}" + E +
                  "生命並返還冷卻。",
        "ult": "向四周甩出一圈飛刀造成" + phy("r") + "傷害，隨後" + O + "隱形" + E + A + "{r_inv}秒" + E + "、跑速+{r_haste}%；隱形結束或攻擊時"
               "飛刀收回，再次造成同樣傷害。",
        "names": ("迴力匕首", "諾城王道", "暗影突襲"),
    },
    "en": {
        "name": "Talon",
        "attack": "Wrist-blade strikes. " + O + "Blade's End" + E + ": his spells wound champions they hit; at 3 wounds his "
                  "next attack makes it " + O + "bleed" + E + " for " + phy("p") + " over " + A + "{p_bleed}s" + E + ". " + O +
                  "Assassin's Path" + E + " (automatic, " + A + "{e_cd}s" + E + "): when his blades return or his Q kills with "
                  "{e_crowd} enemy champions near, he vaults away and runs faster.",
        "skill": "Throws a fan of blades for " + phy("w") + " damage; they fly back for " + phy("w2") + " damage and a " + R +
                 "{w_slow}% slow" + E + ".",
        "skill2": "Leaps at the target for " + phy("q") + " damage; next to it he stabs instead, a {q_crit}% critical strike. "
                  "A kill heals " + G + "{q_heal}" + E + " and refunds the cooldown.",
        "ult": "Sends a ring of blades out for " + phy("r") + " damage, then turns " + O + "invisible" + E + " for " + A +
               "{r_inv}s" + E + " with +{r_haste}% move speed; the blades return when it ends or he attacks, dealing the "
               "same again.",
        "names": ("Rake", "Noxian Diplomacy", "Shadow Assault"),
    },
    "ko": {
        "name": "탈론",
        "attack": "손목 칼날로 공격합니다. " + O + "검의 최후" + E + ": 스킬이 챔피언에게 적중하면 상처 1중첩, 3중첩이면 다음 기본 공격이 " +
                  O + "출혈" + E + "을 일으켜 " + A + "{p_bleed}초" + E + "에 걸쳐 " + phy("p") + "의 피해. " + O + "암살자의 길" + E +
                  "(자동, " + A + "{e_cd}초" + E + "): 칼날이 돌아오거나 Q로 처치할 때 적 챔피언 {e_crowd}명이 가까이 있으면 뛰어올라 "
                  "벗어나고 빨라집니다.",
        "skill": "칼날을 부채꼴로 던져 " + phy("w") + "의 피해, 칼날이 돌아오며 " + phy("w2") + "의 피해와 " + R + "{w_slow}% 둔화" + E + ".",
        "skill2": "대상에게 도약해 " + phy("q") + "의 피해, 바로 옆이면 대신 찔러 {q_crit}% 치명타. 처치하면 체력 " + G + "{q_heal}" + E +
                  " 회복, 재사용 대기시간 반환.",
        "ult": "칼날을 원형으로 뿌려 " + phy("r") + "의 피해, 이후 " + A + "{r_inv}초" + E + " 동안 " + O + "투명" + E +
               ", 이동 속도 +{r_haste}%. 투명이 끝나거나 공격하면 칼날이 돌아와 같은 피해.",
        "names": ("갈퀴손", "녹서스식 외교", "그림자 공격"),
    },
    "ja": {
        "name": "タロン",
        "attack": "手首の刃で攻撃。" + O + "血塗られし慈悲" + E + "：スキルがチャンピオンに命中すると傷を1つ、3つで次の通常攻撃が" + O + "出血" + E +
                  "させ" + A + "{p_bleed}秒" + E + "で" + phy("p") + "のダメージ。" + O + "暗殺者の跳躍" + E + "（自動、" + A + "{e_cd}秒" + E +
                  "）：刃が戻る時かQで倒した時に敵チャンピオン{e_crowd}体が近いと跳んで離脱し加速。",
        "skill": "刃を扇状に投げ" + phy("w") + "のダメージ、刃が戻って" + phy("w2") + "のダメージと" + R + "{w_slow}%スロウ" + E + "。",
        "skill2": "対象へ跳びかかり" + phy("q") + "のダメージ、隣にいれば代わりに刺して{q_crit}%クリティカル。倒すと" + G + "{q_heal}" + E +
                  "回復しクールダウン返還。",
        "ult": "刃を円状に放ち" + phy("r") + "のダメージ、その後" + A + "{r_inv}秒" + E + O + "インビジブル" + E + "、移動速度+{r_haste}%。終了時か"
               "攻撃時に刃が戻り同じダメージ。",
        "names": ("飛燕手裏剣", "ノクサスの刃", "シャドウアサルト"),
    },
}

C = "league_talon_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
S_ = "league_talon_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    S_ + "a_swing": [(C + "a_swing", 0.4, 0.0)],
    S_ + "a_hit": [(C + "a_hit", 0.35, 0.0)],
    S_ + "p_bleed": [(C + "p_bleed", 0.45, 0.0)],
    S_ + "q": [(C + "q", 0.5, 0.0)],
    S_ + "q_stab": [(C + "q_stab", 0.5, 0.0)],
    S_ + "q_hit": [(C + "q_hit", 0.45, 0.0)],
    S_ + "w": [(C + "w", 0.45, 0.0)],
    S_ + "w_hit": [(C + "w_hit", 0.3, 0.0)],
    S_ + "w_back": [(C + "w_back", 0.4, 0.0)],
    S_ + "w_hit2": [(C + "w_hit2", 0.35, 0.0)],
    S_ + "e": [(C + "e", 0.5, 0.0)],
    S_ + "r": [(C + "r", 0.55, 0.0)],
    S_ + "r_hit": [(C + "r_hit", 0.4, 0.0)],
    S_ + "r_back": [(C + "r_back", 0.5, 0.0)],
    S_ + "vo_q": [(C + "vo_q", 0.8, 0.0)],
    S_ + "vo_w": [(C + "vo_w", 0.8, 0.0)],
    S_ + "vo_e": [(C + "vo_e", 0.8, 0.0)],
    S_ + "vo_r": [(C + "vo_r", 0.8, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    keys = ("p_dmg", "p_ratio", "q_dmg", "q_ratio", "q_crit", "q_heal", "w_dmg", "w_ratio", "w2_dmg", "w2_ratio",
            "w_slow", "e_crowd", "r_dmg", "r_ratio", "r_haste")
    v = {k: p[k] for k in keys}
    v.update({k: secs(p[k]) for k in ("p_bleed", "e_cd", "r_inv")})
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
    if "Talon" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Talon. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
