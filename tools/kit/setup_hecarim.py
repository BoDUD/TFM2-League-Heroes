"""Hecarim's text (5 languages), sound_info files and his keys in the shared files, numbers from build_hecarim.P.

    python tools/kit/setup_hecarim.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in hc/league): text/champion.i18n (league_hecarim in every language, description + skill_name),
sound/sfx/league_hecarim_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.86.0, Hecarim named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/hc/rst.py: 赫卡里姆 / 战争之影, 征战之路, 暴走, 恐惧之灵, 毁灭冲锋, 暗影冲击)
and Data Dragon 16.19.1 (zh_TW 赫克林 / 刃馬合一 / 逸騎刃擊 / 靈魂恐懼 / 毀滅衝刺 / 暗影的逆襲, ko 헤카림 / 출정 / 회오리 베기 /
공포의 망령 / 파멸의 돌격 / 그림자의 맹습, ja ヘカリム / ウォーパス / ランページ / ソウルドレイン / チャージ / スペクターズ・オンスロート).
The slot names: skill = Q, skill2 = E, ult = R; the passive and the automatic W are told in the attack's text.
No `league_hecarim_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hecarim import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_hecarim"
VERSION = "0.86.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
M = "<#a974ffff>"      # magic damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 8, "y": -33}, "center": {"x": 0, "y": -14}}


def phy(k):
    return f"{O}{{{k}_dmg}}{E} + {ADi}{O}{{{k}_ratio}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "赫卡里姆",
        "attack": "挥戟攻击。" + O + "征战之路" + E + "：冲锋时攻击力提升。" + O + "恐惧之灵" + E + "（自动，" + A + "{w_cd}秒" + E +
                  "）：放Q、E、R时身边有敌方英雄就开启，" + A + "{w_t}秒" + E + "内双抗+{w_def}，每秒对周围敌人造成" + M + "{w_dmg}魔法伤害" + E +
                  "，每命中一个回复" + G + "{w_heal}" + E + "生命。",
        "skill": "回旋横扫，周围敌人受到" + phy("q") + "伤害。命中后获得一层" + O + "暴走" + E + "（最多2层，" + A + "{q_stk_t}秒" + E +
                 "），每层伤害+{q_stk}%。刷野叠的层数可以带进团战。",
        "skill2": "冲向目标，冲得越久伤害越高（最多{e_max}%），造成" + phy("e") + "伤害并" + R + "击退" + E + "，之后移速+{e_haste}%。",
        "ult": "带幽灵骑兵冲向敌方英雄，沿途敌人受到" + phy("r") + "伤害；落地使周围敌人" + R + "恐惧{r_fear}秒" + E + "（冲得远" + R +
               "{r_fear_far}秒" + E + "），顺势" + O + "暴走" + E + "一圈并开启" + O + "恐惧之灵" + E + "。",
        "names": ("暴走", "毁灭冲锋", "暗影冲击"),
    },
    "zh-hant": {
        "name": "赫克林",
        "attack": "揮戟攻擊。" + O + "刃馬合一" + E + "：衝鋒時攻擊力提升。" + O + "靈魂恐懼" + E + "（自動，" + A + "{w_cd}秒" + E +
                  "）：放Q、E、R時身邊有敵方英雄就開啟，" + A + "{w_t}秒" + E + "內雙抗+{w_def}，每秒對周圍敵人造成" + M + "{w_dmg}魔法傷害" + E +
                  "，每命中一個回復" + G + "{w_heal}" + E + "生命。",
        "skill": "迴旋橫掃，周圍敵人受到" + phy("q") + "傷害。命中後獲得一層" + O + "逸騎刃擊" + E + "（最多2層，" + A + "{q_stk_t}秒" + E +
                 "），每層傷害+{q_stk}%。打野疊的層數可以帶進團戰。",
        "skill2": "衝向目標，衝得越久傷害越高（最多{e_max}%），造成" + phy("e") + "傷害並" + R + "擊退" + E + "，之後跑速+{e_haste}%。",
        "ult": "帶幽靈騎兵衝向敵方英雄，沿途敵人受到" + phy("r") + "傷害；落地使周圍敵人" + R + "恐懼{r_fear}秒" + E + "（衝得遠" + R +
               "{r_fear_far}秒" + E + "），順勢" + O + "逸騎刃擊" + E + "一圈並開啟" + O + "靈魂恐懼" + E + "。",
        "names": ("逸騎刃擊", "毀滅衝刺", "暗影的逆襲"),
    },
    "en": {
        "name": "Hecarim",
        "attack": "Glaive strikes. " + O + "Warpath" + E + ": more attack while he charges. " + O + "Spirit of Dread" + E +
                  " (automatic, " + A + "{w_cd}s" + E + "): starts on his Q, E or R with an enemy champion near: " + A + "{w_t}s" + E +
                  " of +{w_def} armour and magic resist, " + M + "{w_dmg} magic damage" + E + " to enemies around him every "
                  "second, healing " + G + "{w_heal}" + E + " for each one hit.",
        "skill": "Spins the glaive: enemies around take " + phy("q") + " damage. A hit gives a " + O + "Rampage" + E + " stack (up "
                 "to 2, " + A + "{q_stk_t}s" + E + "), each +{q_stk}% damage - stacks built on camps carry into a gank.",
        "skill2": "Charges the target, harder the longer he rides (up to {e_max}%): " + phy("e") + " damage and a " + R +
                  "knockback" + E + ", then +{e_haste}% move speed.",
        "ult": "Rides at an enemy champion with spectral riders: enemies in the path take " + phy("r") + " damage; on landing "
               "enemies around are " + R + "feared {r_fear}s" + E + " (" + R + "{r_fear_far}s" + E + " after a long ride), and he "
               "spins a " + O + "Rampage" + E + " and starts " + O + "Spirit of Dread" + E + ".",
        "names": ("Rampage", "Devastating Charge", "Onslaught of Shadows"),
    },
    "ko": {
        "name": "헤카림",
        "attack": "언월도로 공격합니다. " + O + "출정" + E + ": 돌격 중 공격력 증가. " + O + "공포의 망령" + E + "(자동, " + A + "{w_cd}초" +
                  E + "): Q·E·R 사용 시 주변에 적 챔피언이 있으면 발동, " + A + "{w_t}초" + E + " 동안 방어력·마법 저항력 +{w_def}, 매초 주변 적에게 " + M +
                  "{w_dmg}의 마법 피해" + E + ", 맞힌 적 하나마다 체력 " + G + "{w_heal}" + E + " 회복.",
        "skill": "언월도를 휘둘러 주변 적에게 " + phy("q") + "의 피해. 적중 시 " + O + "회오리 베기" + E + " 중첩(최대 2, " + A +
                 "{q_stk_t}초" + E + "), 중첩당 피해 +{q_stk}%. 정글에서 쌓은 중첩을 갱킹에 가져갑니다.",
        "skill2": "대상에게 돌격하며 오래 달릴수록 강해집니다(최대 {e_max}%): " + phy("e") + "의 피해와 " + R + "밀어내기" + E +
                  ", 이후 이동 속도 +{e_haste}%.",
        "ult": "유령 기병과 함께 적 챔피언에게 돌진: 경로의 적에게 " + phy("r") + "의 피해, 착지 시 주변 적 " + R + "{r_fear}초 공포" + E +
               "(멀리 달리면 " + R + "{r_fear_far}초" + E + "), 이어서 " + O + "회오리 베기" + E + "와 " + O + "공포의 망령" + E + ".",
        "names": ("회오리 베기", "파멸의 돌격", "그림자의 맹습"),
    },
    "ja": {
        "name": "ヘカリム",
        "attack": "グレイブで攻撃。" + O + "ウォーパス" + E + "：突進中は攻撃力上昇。" + O + "ソウルドレイン" + E + "（自動、" + A + "{w_cd}秒" + E +
                  "）：Q・E・R使用時に敵チャンピオンが近くにいると発動、" + A + "{w_t}秒" + E + "間物防魔防+{w_def}、毎秒周囲の敵に" + M +
                  "{w_dmg}の魔法ダメージ" + E + "、1体ごとに" + G + "{w_heal}" + E + "回復。",
        "skill": "グレイブを振り回し周囲の敵に" + phy("q") + "のダメージ。命中で" + O + "ランページ" + E + "スタック（最大2、" + A +
                 "{q_stk_t}秒" + E + "）、1つごとにダメージ+{q_stk}%。",
        "skill2": "対象へ突進、長く走るほど強力（最大{e_max}%）：" + phy("e") + "のダメージと" + R + "ノックバック" + E + "、その後移動速度+{e_haste}%。",
        "ult": "亡霊騎兵と共に敵チャンピオンへ突撃：経路の敵に" + phy("r") + "のダメージ、着地で周囲の敵に" + R + "{r_fear}秒フィアー" + E +
               "（遠くからなら" + R + "{r_fear_far}秒" + E + "）、続けて" + O + "ランページ" + E + "と" + O + "ソウルドレイン" + E + "。",
        "names": ("ランページ", "チャージ", "スペクターズ・オンスロート"),
    },
}

C = "league_hecarim_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
S_ = "league_hecarim_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    S_ + "a_swing": [(C + "a_swing", 0.4, 0.0)],
    S_ + "a_hit": [(C + "a_hit", 0.35, 0.0)],
    S_ + "q": [(C + "q", 0.5, 0.0)],
    S_ + "q_hit": [(C + "q_hit", 0.4, 0.0)],
    S_ + "w": [(C + "w", 0.45, 0.0)],
    S_ + "e": [(C + "e", 0.5, 0.0)],
    S_ + "e_hit": [(C + "e_hit", 0.55, 0.0)],
    S_ + "r": [(C + "r", 0.55, 0.0)],
    S_ + "r_hit": [(C + "r_hit", 0.55, 0.0)],
    S_ + "r_pass": [(C + "r_pass", 0.3, 0.0)],
    S_ + "vo_q": [(C + "vo_q", 0.8, 0.0)],
    S_ + "vo_w": [(C + "vo_w", 0.8, 0.0)],
    S_ + "vo_r": [(C + "vo_r", 0.8, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    keys = ("q_dmg", "q_ratio", "q_stk", "w_def", "w_dmg", "w_heal", "e_dmg", "e_ratio", "e_max", "e_haste",
            "r_dmg", "r_ratio")
    v = {k: p[k] for k in keys}
    v.update({k: secs(p[k]) for k in ("w_cd", "w_t", "q_stk_t", "r_fear", "r_fear_far")})
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
    if "Hecarim" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Hecarim. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
