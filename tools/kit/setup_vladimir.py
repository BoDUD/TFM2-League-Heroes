"""Vladimir's text (5 languages), sound_info files and his keys in the shared files, numbers from build_vladimir.P.

    python tools/kit/setup_vladimir.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in vl/league): text/champion.i18n (league_vladimir in every language, description + skill_name),
sound/sfx/league_vladimir_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.80.0, Vladimir named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/vl/rst.py: 弗拉基米尔 / 血色契约, 鲜血转换, 猩红冲刺, 血之潮汐, 血红之池,
血之瘟疫) and Data Dragon 16.19.1 (zh_TW 弗拉迪米爾 / 血色契約 / 鮮血轉換 / 血紅之池 / 血之潮汐 / 血之瘟疫, ko 블라디미르 /
핏빛 계약 / 수혈 / 피의 웅덩이 / 선혈의 파도 / 혈사병, ja ブラッドミア / 真紅の盟約 / 吸血 / 紅血の沼 / 血液奔流 / 呪血の渦).
The slot names: skill = Q, skill2 = E, ult = R; the passive and the automatic W are told in the attack's text.
No `league_vladimir_attack` sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_vladimir import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_vladimir"
VERSION = "0.80.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7cfc00ff>"      # heals
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -39}, "center": {"x": 0, "y": -12}}


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ap}}%{E} + {HPi}{M}{{{k}_hp}}%{E}"


def hl(k):
    return f"{G}{{{k}_heal}}{E} + {APi}{G}{{{k}_heal_ap}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "弗拉基米尔",
        "attack": "射出血弹攻击。被动" + O + "血色契约" + E + "：技能伤害附带最大生命值加成。" + O + "血红之池" + E + "（自动）：危急时化为血池" +
                  A + "{w_t}秒" + E + "，不可选取，脚下敌人每次受到" + mag("w") + "伤害并" + R + "减速{w_slow}%" + E + "，自己回复" + hl("w") +
                  "；消耗{w_cost}%最大生命值。",
        "skill": "抽取目标的血，造成" + mag("q") + M + "魔法伤害" + E + "，血回到身上时回复" + hl("q") + "生命。每第2次为" + O + "猩红冲刺" + E +
                 "：伤害{q_rush}%、回血翻倍、移速+{q_ms}%。" + O + "连招E→Q" + E + "：潮汐命中英雄后" + A + "{eq_t}秒" + E + "内的Q直接为猩红冲刺。",
        "skill2": "蓄力" + A + "{e_rel}秒" + E + "，向周围每个敌人射出血弹，造成" + mag("e") + M + "魔法伤害" + E + "并" + R + "减速{e_slow}%" + E + "。" +
                  O + "连招E-W" + E + "：血池结束时若E已就绪，钻出时放出一圈{combo_pct}%伤害的潮汐。",
        "ult": "在敌方英雄中降下瘟疫：范围内敌人" + A + "{r_t}秒" + E + "内受到伤害+{r_amp}%，随后爆发" + mag("r") + M + "魔法伤害" + E +
               "，每命中一名英雄回复" + hl("r") + "生命。" + O + "连招闪R E" + E + "：若E已就绪，先化作血雾闪入敌群，再放出一圈{combo_pct}%伤害的潮汐。",
        "names": ("鲜血转换", "血之潮汐", "血之瘟疫"),
    },
    "zh-hant": {
        "name": "弗拉迪米爾",
        "attack": "射出血彈攻擊。被動" + O + "血色契約" + E + "：技能傷害附帶最大生命值加成。" + O + "血紅之池" + E + "（自動）：危急時化為血池" +
                  A + "{w_t}秒" + E + "，無法被選取，腳下敵人每次受到" + mag("w") + "傷害並" + R + "緩速{w_slow}%" + E + "，自己回復" + hl("w") +
                  "；消耗{w_cost}%最大生命值。",
        "skill": "抽取目標的血，造成" + mag("q") + M + "魔法傷害" + E + "，血回到身上時回復" + hl("q") + "生命。每第2次為" + O + "猩紅衝刺" + E +
                 "：傷害{q_rush}%、回血加倍、跑速+{q_ms}%。" + O + "連招E→Q" + E + "：潮汐命中英雄後" + A + "{eq_t}秒" + E + "內的Q直接為猩紅衝刺。",
        "skill2": "蓄力" + A + "{e_rel}秒" + E + "，向周圍每個敵人射出血彈，造成" + mag("e") + M + "魔法傷害" + E + "並" + R + "緩速{e_slow}%" + E + "。" +
                  O + "連招E-W" + E + "：血池結束時若E已就緒，鑽出時放出一圈{combo_pct}%傷害的潮汐。",
        "ult": "在敵方英雄中降下瘟疫：範圍內敵人" + A + "{r_t}秒" + E + "內受到傷害+{r_amp}%，隨後爆發" + mag("r") + M + "魔法傷害" + E +
               "，每命中一名英雄回復" + hl("r") + "生命。" + O + "連招閃R E" + E + "：若E已就緒，先化作血霧閃入敵群，再放出一圈{combo_pct}%傷害的潮汐。",
        "names": ("鮮血轉換", "血之潮汐", "血之瘟疫"),
    },
    "en": {
        "name": "Vladimir",
        "attack": "Fires blood bolts. Passive " + O + "Crimson Pact" + E + ": his skills also scale with his max health. " + O +
                  "Sanguine Pool" + E + " (automatic): in danger he becomes a pool for " + A + "{w_t}s" + E + ", untargetable; enemies on it "
                  "take " + mag("w") + " per pulse and are " + R + "slowed {w_slow}%" + E + ", he heals " + hl("w") + ". Costs {w_cost}% "
                  "max health.",
        "skill": "Drains the target for " + mag("q") + " " + M + "magic damage" + E + "; the blood heals him " + hl("q") + " when it "
                 "returns. Every 2nd cast is " + O + "Crimson Rush" + E + ": {q_rush}% damage, double heal, +{q_ms}% move speed. " + O +
                 "Combo E-Q" + E + ": a Q within " + A + "{eq_t}s" + E + " of Tides hitting a champion is Crimson Rush at once.",
        "skill2": "Charges for " + A + "{e_rel}s" + E + ", then fires a bolt at every enemy around for " + mag("e") + " " + M +
                  "magic damage" + E + " and a " + R + "{e_slow}% slow" + E + ". " + O + "Combo E-W" + E + ": if E is ready when "
                  "Sanguine Pool ends, he rises with a {combo_pct}% Tides of Blood.",
        "ult": "Infects enemy champions' area: enemies take {r_amp}% more damage for " + A + "{r_t}s" + E + ", then burst for " +
               mag("r") + " " + M + "magic damage" + E + "; each champion hit heals him " + hl("r") + ". " + O + "Combo Flash-R-E" + E +
               ": with E ready he first blinks into them as a blood mist, then casts a {combo_pct}% Tides of Blood.",
        "names": ("Transfusion", "Tides of Blood", "Hemoplague"),
    },
    "ko": {
        "name": "블라디미르",
        "attack": "피의 탄환으로 공격합니다. 기본 지속 효과 " + O + "핏빛 계약" + E + ": 스킬 피해가 최대 체력에 비례해 증가합니다. " + O + "피의 웅덩이" + E +
                  "(자동): 위험할 때 " + A + "{w_t}초" + E + " 동안 웅덩이가 되어 지정 불가, 위의 적에게 " + mag("w") + "의 피해와 " + R +
                  "{w_slow}% 둔화" + E + ", 자신은 " + hl("w") + " 회복. 최대 체력 {w_cost}% 소모.",
        "skill": "대상의 피를 빨아 " + mag("q") + "의 " + M + "마법 피해" + E + ", 피가 돌아오면 " + hl("q") + " 회복. 두 번째마다 " + O + "진홍빛 쇄도" +
                 E + ": 피해 {q_rush}%, 회복 2배, 이동 속도 +{q_ms}%. " + O + "연계 E→Q" + E + ": 파도가 챔피언에게 적중한 후 " + A + "{eq_t}초" + E +
                 " 안의 Q는 바로 진홍빛 쇄도.",
        "skill2": A + "{e_rel}초" + E + " 충전 후 주변 모든 적에게 피의 탄환을 쏘아 " + mag("e") + "의 " + M + "마법 피해" + E + "와 " + R +
                  "{e_slow}% 둔화" + E + ". " + O + "연계 E-W" + E + ": 웅덩이가 끝날 때 E가 준비되어 있으면 {combo_pct}% 피해의 파도를 일으킵니다.",
        "ult": "적 챔피언 무리에 역병을 퍼뜨려 " + A + "{r_t}초" + E + " 동안 받는 피해 +{r_amp}%, 이후 " + mag("r") + "의 " + M + "마법 피해" + E +
               ", 맞힌 챔피언마다 " + hl("r") + " 회복. " + O + "연계 점멸-R-E" + E + ": E가 준비되면 피안개로 점멸해 들어간 뒤 {combo_pct}% 파도.",
        "names": ("수혈", "선혈의 파도", "혈사병"),
    },
    "ja": {
        "name": "ブラッドミア",
        "attack": "血の弾で攻撃。パッシブ" + O + "真紅の盟約" + E + "：スキルダメージが最大体力に比例して増加。" + O + "紅血の沼" + E + "（自動）：危険時" +
                  A + "{w_t}秒" + E + "沼となり対象不可、上の敵に" + mag("w") + "と" + R + "{w_slow}%スロウ" + E + "、自身は" + hl("w") +
                  "回復。最大体力の{w_cost}%を消費。",
        "skill": "対象から吸血し" + mag("q") + "の" + M + "魔法ダメージ" + E + "、血が戻ると" + hl("q") + "回復。2回ごとに" + O + "真紅の奔流" + E +
                 "：ダメージ{q_rush}%、回復2倍、移動速度+{q_ms}%。" + O + "コンボE→Q" + E + "：血液奔流がチャンピオンに当たって" + A + "{eq_t}秒" + E +
                 "以内のQは即奔流。",
        "skill2": A + "{e_rel}秒" + E + "溜めた後、周囲の敵全員に血の弾を放ち" + mag("e") + "の" + M + "魔法ダメージ" + E + "と" + R +
                  "{e_slow}%スロウ" + E + "。" + O + "コンボE-W" + E + "：沼の終わりにEが使えれば{combo_pct}%の血液奔流を放つ。",
        "ult": "敵チャンピオンの群れに呪いを放ち、" + A + "{r_t}秒" + E + "被ダメージ+{r_amp}%、その後" + mag("r") + "の" + M + "魔法ダメージ" + E +
               "、命中したチャンピオンごとに" + hl("r") + "回復。" + O + "コンボ閃光R E" + E + "：Eが使えれば血霧で飛び込み、{combo_pct}%の血液奔流。",
        "names": ("吸血", "血液奔流", "呪血の渦"),
    },
}

C = "league_vladimir_sfx_"
V = "league_vladimir_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_vladimir_a_shot": [(C + "attack", 0.45, 0.0)],
    "league_vladimir_a_hit": [(C + "attack_hit", 0.35, 0.0)],
    "league_vladimir_q_cast": [(C + "q", 0.55, 0.0), (V + "q", 0.8, 0.05)],
    "league_vladimir_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_vladimir_q_rush": [(C + "q_rush", 0.6, 0.0)],
    "league_vladimir_q_heal": [(C + "q_heal", 0.4, 0.0)],
    "league_vladimir_e_charge": [(C + "e_charge", 0.5, 0.0), (V + "e", 0.8, 0.1)],
    "league_vladimir_e_cast": [(C + "e", 0.6, 0.0)],
    "league_vladimir_e_hit": [(C + "e_hit", 0.25, 0.0)],
    "league_vladimir_w_cast": [(C + "w", 0.6, 0.0)],
    "league_vladimir_w_out": [(C + "w_out", 0.5, 0.0), (V + "w", 0.8, 0.1)],
    "league_vladimir_r_cast": [(C + "r", 0.55, 0.0), (V + "r", 0.9, 0.05)],
    "league_vladimir_r_land": [(C + "r_land", 0.55, 0.0)],
    "league_vladimir_r_burst": [(C + "r_burst", 0.5, 0.0)],
    "league_vladimir_c_blink": [(C + "blink", 0.5, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    keys = ("w_dmg", "w_ap", "w_hp", "w_slow", "w_heal", "w_heal_ap", "w_cost", "q_dmg", "q_ap", "q_hp", "q_heal",
            "q_heal_ap", "q_rush", "q_ms", "e_dmg", "e_ap", "e_hp", "e_slow", "combo_pct", "r_amp", "r_dmg", "r_ap", "r_hp",
            "r_heal", "r_heal_ap")
    v = {k: p[k] for k in keys}
    v.update({k: secs(p[k]) for k in ("w_t", "eq_t", "e_rel", "r_t")})
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
    if "Vladimir" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Vladimir. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
