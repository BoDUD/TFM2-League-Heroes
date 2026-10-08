"""Rengar's text (5 languages), sound_info files and his keys in the shared files, numbers from build_rengar.P.

    python tools/kit/setup_rengar.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in rg/league): text/champion.i18n (league_rengar in every language, description + skill_name),
sound/sfx/league_rengar_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.81.0, Rengar named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/rg/rst.py: 雷恩加尔 / 无形掠食者, 残忍无情, 战争咆哮, 套索打击, 狩猎律动, 残暴)
and Data Dragon 16.19.1 (zh_TW 雷葛爾 / 潛行怒獅 / 兇殘打擊 / 怒獅戰吼 / 狩獵拋繩 / 血性獵殺, ko 렝가 / 보이지 않는 포식자 /
포악함 / 전투의 포효 / 올가미 투척 / 사냥의 전율, ja レンガー / 見えざる襲撃者 / 逆上 / 狩りの雄叫び / 鉄球の投げ縄 / 狩猟本能).
The slot names: skill = W, skill2 = E, ult = R; the passive, Ferocity and the automatic Q are told in the attack's text.
The Kha'Zix easter egg is left out of the tooltips (README tells it).
No `league_rengar_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_rengar import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_rengar"
VERSION = "0.81.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -30}, "center": {"x": 0, "y": -12}}


def phy(k):
    return f"{O}{{{k}_dmg}}{E} + {ADi}{O}{{{k}_ratio}}%{E}"


def grn(k):
    return f"{G}{{{k}_heal}}{E} + {ADi}{G}{{{k}_heal_r}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "雷恩加尔",
        "attack": O + "无形掠食者" + E + "：复活、脱战" + A + "{quiet}秒" + E + "或R后，下次攻击扑向目标造成" + phy("leap") +
                  "伤害。技能和扑击各得1点" + O + "残暴" + E + "，满4点强化下个技能。" + O + "残忍无情" + E + "（自动，" + A + "{q_cd}秒" + E + "）：攻击造成" +
                  phy("q") + "伤害，攻速+{q_as}%；强化时" + phy("qe") + "。" + O + "连招" + E + "：空中Q、三Q。",
        "skill": "咆哮，对周围敌人造成" + phy("w") + "伤害，回复" + grn("w") + "生命。" + O + "强化" + E + "：回复{we_heal}%，" + A + "{we_cc_t}秒" + E +
                 "内" + R + "免疫控制" + E + "。",
        "skill2": "掷出套索，命中首个敌人造成" + phy("e") + "伤害并" + R + "减速{e_slow}%" + E + A + "{e_slow_t}秒" + E + "。" + O + "强化" + E + "：" +
                  R + "禁锢{e_root_t}秒" + E + "。" + O + "连招扑脸定身" + E + "：扑击命中英雄后" + A + "{lp_t}秒" + E + "内的E必中，" + R +
                  "禁锢{e_combo_t}秒" + E + "。",
        "ult": "对交战中的英雄发动：伪装" + A + "{r_inv}秒" + E + "，移速+{r_ms}%，下次攻击为扑击，额外造成" + phy("r") + "伤害，" + R + "护甲-{r_shred}%" +
               E + A + "{r_shred_t}秒" + E + "。" + O + "连招R一套" + E + "：R→扑击→E禁锢→Q。",
        "names": ("战争咆哮", "套索打击", "狩猎律动"),
    },
    "zh-hant": {
        "name": "雷葛爾",
        "attack": O + "潛行怒獅" + E + "：復活、脫戰" + A + "{quiet}秒" + E + "或R後，下次攻擊撲向目標造成" + phy("leap") +
                  "傷害。技能和撲擊各得1點" + O + "兇殘" + E + "，滿4點強化下個技能。" + O + "兇殘打擊" + E + "（自動，" + A + "{q_cd}秒" + E + "）：攻擊造成" +
                  phy("q") + "傷害，攻速+{q_as}%；強化時" + phy("qe") + "。" + O + "連招" + E + "：空中Q、三Q。",
        "skill": "咆哮，對周圍敵人造成" + phy("w") + "傷害，回復" + grn("w") + "生命。" + O + "強化" + E + "：回復{we_heal}%，" + A + "{we_cc_t}秒" + E +
                 "內" + R + "免疫控場" + E + "。",
        "skill2": "擲出拋繩，命中首個敵人造成" + phy("e") + "傷害並" + R + "緩速{e_slow}%" + E + A + "{e_slow_t}秒" + E + "。" + O + "強化" + E + "：" +
                  R + "定身{e_root_t}秒" + E + "。" + O + "連招撲臉定身" + E + "：撲擊命中英雄後" + A + "{lp_t}秒" + E + "內的E必中，" + R +
                  "定身{e_combo_t}秒" + E + "。",
        "ult": "對交戰中的英雄發動：偽裝" + A + "{r_inv}秒" + E + "，跑速+{r_ms}%，下次攻擊為撲擊，額外造成" + phy("r") + "傷害，" + R + "護甲-{r_shred}%" +
               E + A + "{r_shred_t}秒" + E + "。" + O + "連招R一套" + E + "：R→撲擊→E定身→Q。",
        "names": ("怒獅戰吼", "狩獵拋繩", "血性獵殺"),
    },
    "en": {
        "name": "Rengar",
        "attack": "Blade swings. " + O + "Unseen Predator" + E + ": on respawn, after " + A + "{quiet}s" + E + " out of combat or after R, "
                  "his next attack leaps at a distant target for " + phy("leap") + ". Skills and leaps give 1 " + O + "Ferocity" + E +
                  "; at 4 his next skill is empowered. " + O + "Savagery" + E + " (automatic, " + A + "{q_cd}s" + E + "): an attack for " +
                  phy("q") + " and +{q_as}% attack speed; empowered " + phy("qe") + ". " + O + "Combos" + E + ": air Q, triple Q.",
        "skill": "Roars, dealing " + phy("w") + " to enemies around him and healing " + grn("w") + ". " + O + "Empowered" + E +
                 ": {we_heal}% heal and " + R + "immune to crowd control" + E + " for " + A + "{we_cc_t}s" + E + ".",
        "skill2": "Throws a bola: the first enemy hit takes " + phy("e") + " and is " + R + "slowed {e_slow}%" + E + " for " + A +
                  "{e_slow_t}s" + E + ". " + O + "Empowered" + E + ": " + R + "rooted {e_root_t}s" + E + ". " + O + "Combo leap-E" + E +
                  ": within " + A + "{lp_t}s" + E + " of a leap onto a champion the bola cannot miss and " + R + "roots {e_combo_t}s" + E + ".",
        "ult": "On a champion in a fight: camouflaged for " + A + "{r_inv}s" + E + ", +{r_ms}% move speed; his next attack is a leap for " +
               phy("r") + " more and " + R + "-{r_shred}% armour" + E + " for " + A + "{r_shred_t}s" + E + ". " + O + "Combo R one-shot" + E +
               ": R, leap, rooting E, Savagery.",
        "names": ("Battle Roar", "Bola Strike", "Thrill of the Hunt"),
    },
    "ko": {
        "name": "렝가",
        "attack": O + "보이지 않는 포식자" + E + ": 부활, " + A + "{quiet}초" + E + " 비전투 또는 R 후 다음 공격은 멀리 도약해 " +
                  phy("leap") + "의 피해. 스킬과 도약마다 " + O + "흉포" + E + " 1, 4가 되면 다음 스킬 강화. " + O + "포악함" + E + "(자동, " + A +
                  "{q_cd}초" + E + "): 공격이 " + phy("q") + "의 피해, 공격 속도 +{q_as}%; 강화 시 " + phy("qe") + ". " + O + "연계" + E +
                  ": 공중 Q, 트리플 Q.",
        "skill": "포효해 주변 적에게 " + phy("w") + "의 피해를 주고 " + grn("w") + " 회복. " + O + "강화" + E + ": 회복 {we_heal}%, " + A +
                 "{we_cc_t}초" + E + " 동안 " + R + "군중 제어 면역" + E + ".",
        "skill2": "올가미를 던져 처음 맞힌 적에게 " + phy("e") + "의 피해와 " + A + "{e_slow_t}초" + E + " " + R + "{e_slow}% 둔화" + E + ". " + O +
                  "강화" + E + ": " + R + "{e_root_t}초 속박" + E + ". " + O + "연계 도약-E" + E + ": 챔피언에게 도약한 뒤 " + A + "{lp_t}초" + E +
                  " 안의 E는 반드시 맞고 " + R + "{e_combo_t}초 속박" + E + ".",
        "ult": "교전 중인 챔피언에게: " + A + "{r_inv}초" + E + " 위장, 이동 속도 +{r_ms}%, 다음 공격은 도약으로 " + phy("r") + "의 추가 피해와 " + A +
               "{r_shred_t}초" + E + " " + R + "방어력 -{r_shred}%" + E + ". " + O + "연계 R 원콤" + E + ": R→도약→E 속박→Q.",
        "names": ("전투의 포효", "올가미 투척", "사냥의 전율"),
    },
    "ja": {
        "name": "レンガー",
        "attack": "刃で攻撃。" + O + "見えざる襲撃者" + E + "：復活時、" + A + "{quiet}秒" + E + "非戦闘またはR後、次の攻撃で遠くの敵に飛びかかり" + phy("leap") +
                  "。スキルと跳躍ごとに" + O + "獰猛" + E + "1、4で次のスキル強化。" + O + "逆上" + E + "（自動、" + A + "{q_cd}秒" + E + "）：攻撃が" +
                  phy("q") + "、攻撃速度+{q_as}%；強化時" + phy("qe") + "。" + O + "コンボ" + E + "：空中Q、トリプルQ。",
        "skill": "咆哮し周囲の敵に" + phy("w") + "、自身は" + grn("w") + "回復。" + O + "強化" + E + "：回復{we_heal}%、" + A + "{we_cc_t}秒" + E +
                 R + "行動妨害無効" + E + "。",
        "skill2": "投げ縄を投げ最初の敵に" + phy("e") + "と" + A + "{e_slow_t}秒" + E + R + "{e_slow}%スロウ" + E + "。" + O + "強化" + E + "：" + R +
                  "{e_root_t}秒スネア" + E + "。" + O + "コンボ跳躍E" + E + "：チャンピオンへの跳躍後" + A + "{lp_t}秒" + E + "以内のEは必中で" + R +
                  "{e_combo_t}秒スネア" + E + "。",
        "ult": "交戦中のチャンピオンに：" + A + "{r_inv}秒" + E + "カモフラージュ、移動速度+{r_ms}%、次の攻撃は跳躍で" + phy("r") + "追加、" + A +
               "{r_shred_t}秒" + E + R + "物理防御-{r_shred}%" + E + "。" + O + "コンボR一撃" + E + "：R→跳躍→Eスネア→Q。",
        "names": ("狩りの雄叫び", "鉄球の投げ縄", "狩猟本能"),
    },
}

C = "league_rengar_sfx_"
V = "league_rengar_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
S = "league_rengar_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    S + "a_swing": [(C + "attack", 0.45, 0.0)],
    S + "a_hit": [(C + "attack_hit", 0.35, 0.0)],
    S + "leap": [(C + "leap", 0.55, 0.0)],
    S + "leap_hit": [(C + "leap_hit", 0.55, 0.0)],
    S + "q": [(C + "q", 0.5, 0.0)],
    S + "q_hit": [(C + "q_hit", 0.45, 0.0)],
    S + "q_emp": [(C + "q_emp", 0.55, 0.0)],
    S + "w": [(C + "w", 0.6, 0.0)],
    S + "w_emp": [(C + "w_emp", 0.6, 0.0)],
    S + "e": [(C + "e", 0.5, 0.0)],
    S + "e_hit": [(C + "e_hit", 0.45, 0.0)],
    S + "e_emp_hit": [(C + "e_emp_hit", 0.5, 0.0)],
    S + "r": [(C + "r", 0.6, 0.0)],
    S + "r_hit": [(C + "r_hit", 0.55, 0.0)],
    S + "vo_q": [(V + "q", 0.8, 0.0)],
    S + "vo_w": [(V + "w", 0.8, 0.0)],
    S + "vo_e": [(V + "e", 0.8, 0.0)],
    S + "vo_r": [(V + "r", 0.9, 0.05)],
    S + "vo_fero": [(V + "fero", 0.7, 0.0)],
    S + "vo_khazix": [(V + "khazix", 0.9, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    keys = ("leap_dmg", "q_dmg", "q_ratio", "q_as", "qe_dmg", "qe_ratio", "w_dmg", "w_ratio", "w_heal", "w_heal_r",
            "we_heal", "e_dmg", "e_ratio", "e_slow", "r_ms", "r_dmg", "r_ratio", "r_shred")
    v = {k: p[k] for k in keys}
    v["leap_ratio"] = 100 + p["leap_ratio"]
    v.update({k: secs(p[k]) for k in ("quiet", "q_cd", "we_cc_t", "e_slow_t", "e_root_t", "lp_t", "e_combo_t", "r_inv",
                                       "r_shred_t")})
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
    if "Rengar" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Rengar. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
