"""Zac's text (5 languages), sound_info files and their keys in the shared files, numbers from build_zac.P.

    python tools/kit/setup_zac.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_zac in every language, description + skill_name),
sound/sfx/league_zac_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Zac named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 扎克 (生化魔人): 细胞分裂; 延伸打击, 不稳定物质, 橡筋弹弓, 动感弹球; zh_TW 札克: 組織分裂;
橡膠飛拳, 自體爆破, 必殺黏星, 活蹦亂跳！; ja ザック: はぐれスライム; スライムパンチ, スライムクラッシュ, ブッ飛びスライム, レッツバウンス！;
ko 자크: 세포 분열; 탄성 주먹, 불안정 물질, 새총 발사, 바운스!.
Slots: skill = Stretching Strikes, skill2 = Elastic Slingshot, ult = Let's Bounce!; Unstable Matter and the passive's blobs
in the attack's text (the revive is league_zac's add-on: the text says so). No combo sentence in any text (the user's
rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zac import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_zac"
VERSION = "0.202.0"     # the next free number above main 0.200.1 (Varus #481) and Azir's 0.201.0 (2026-10-23)
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
T = "<#e0e0e0ff>"      # true damage
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to: his head sits forward between the
# shoulders, league_warwick's the same) and the ban/pick card (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 11, "y": -28}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -10}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


def hl(x):
    return G + x + E


def tr(x):
    return T + x + E


TEXT = {
    "zh-hans": {
        "name": "扎克",
        "attack": "拳击。" + n("不稳定物质") + "：冷却好时普攻炸开，周围敌人受" + mag("w_dmg", "w_ap") + "魔法伤害，英雄再受" +
                  tr("最大生命{w_pct}%") + "真实伤害（冷却" + t("{w_cd}秒") + "）。" + n("细胞分裂") + "：技能打中英雄掉下黏液，"
                  "吃掉" + hl("回复") + mag("b_heal", "b_heal_ap") + "生命（复活需扩展包）。",
        "skill": "伸长手臂抓向目标，造成" + mag("q_dmg", "q_ap") + " + 自身最大生命{q_hp}%魔法伤害并" + cc("减速") + "{q_slow}%；"
                 "抓住的英雄" + t("{q_hold}秒") + "后被甩到身边砸地，再受同样伤害，周围敌人" + cc("击飞") + t("{q_up}秒") + "。",
        "skill2": "蓄力" + t("{e_wind}秒") + "后把自己弹向目标，落地造成" + mag("e_dmg", "e_ap") + " + 自身最大生命{e_hp}%魔法伤害并" +
                  cc("击飞") + "周围敌人" + t("{e_up}秒") + "。",
        "ult": "不可阻挡地连跳{r_n}次，每次落地造成" + mag("r_dmg", "r_ap") + "魔法伤害（之后每次{r_k}%），" + cc("击飞") +
               t("{r_up}秒") + "并" + cc("减速") + "{r_slow}%。",
        "names": ("延伸打击", "橡筋弹弓", "动感弹球"),
    },
    "zh-hant": {
        "name": "札克",
        "attack": "拳擊。" + n("自體爆破") + "：冷卻好時普攻炸開，周圍敵人受" + mag("w_dmg", "w_ap") + "魔法傷害，英雄再受" +
                  tr("最大生命{w_pct}%") + "真實傷害（冷卻" + t("{w_cd}秒") + "）。" + n("組織分裂") + "：技能擊中英雄掉下黏液，"
                  "吃掉" + hl("回復") + mag("b_heal", "b_heal_ap") + "生命（復活需擴充包）。",
        "skill": "伸長手臂抓向目標，造成" + mag("q_dmg", "q_ap") + " + 自身最大生命{q_hp}%魔法傷害並" + cc("緩速") + "{q_slow}%；"
                 "抓住的英雄" + t("{q_hold}秒") + "後被甩到身邊砸地，再受同樣傷害，周圍敵人" + cc("擊飛") + t("{q_up}秒") + "。",
        "skill2": "蓄力" + t("{e_wind}秒") + "後把自己彈向目標，落地造成" + mag("e_dmg", "e_ap") + " + 自身最大生命{e_hp}%魔法傷害並" +
                  cc("擊飛") + "周圍敵人" + t("{e_up}秒") + "。",
        "ult": "無法阻擋地連跳{r_n}次，每次落地造成" + mag("r_dmg", "r_ap") + "魔法傷害（之後每次{r_k}%），" + cc("擊飛") +
               t("{r_up}秒") + "並" + cc("緩速") + "{r_slow}%。",
        "names": ("橡膠飛拳", "必殺黏星", "活蹦亂跳！"),
    },
    "en": {
        "name": "Zac",
        "attack": "A goo punch. " + n("Unstable Matter") + ": when ready, an attack bursts for " + mag("w_dmg", "w_ap") +
                  " magic damage round him, champions also taking " + tr("{w_pct}% of their max health") + " true damage "
                  "(cooldown " + t("{w_cd}s") + "). " + n("Cell Division") + ": skills hitting a champion shed a blob; "
                  "absorbing it " + hl("heals") + " " + mag("b_heal", "b_heal_ap") + " (the revive needs the add-on).",
        "skill": "Stretches an arm at the target for " + mag("q_dmg", "q_ap") + " + {q_hp}% of his max health magic damage, " +
                 cc("slowing") + " {q_slow}%; a champion caught is flung to him after " + t("{q_hold}s") + " and slammed for "
                 "the same damage again, " + cc("knocking up") + " enemies round him for " + t("{q_up}s") + ".",
        "skill2": "Charges for " + t("{e_wind}s") + ", then flings himself at the target, landing for " + mag("e_dmg", "e_ap") +
                  " + {e_hp}% of his max health magic damage and a " + t("{e_up}s") + " " + cc("knock-up") + " round him.",
        "ult": "Bounces {r_n} times, unstoppable: each landing deals " + mag("r_dmg", "r_ap") + " magic damage (the later "
               "ones {r_k}%), a " + t("{r_up}s") + " " + cc("knock-up") + " and a {r_slow}% " + cc("slow") + ".",
        "names": ("Stretching Strikes", "Elastic Slingshot", "Let's Bounce!"),
    },
    "ko": {
        "name": "자크",
        "attack": "점액 주먹. " + n("불안정 물질") + ": 준비되면 기본 공격이 터져 주변 적에게 " + mag("w_dmg", "w_ap") +
                  " 마법 피해, 챔피언은 " + tr("최대 체력의 {w_pct}%") + " 고정 피해 추가(재사용 " + t("{w_cd}초") + "). " +
                  n("세포 분열") + ": 스킬이 챔피언을 맞히면 점액이 떨어지고, 먹으면 " + mag("b_heal", "b_heal_ap") + " " +
                  hl("회복") + "(부활은 확장 팩 필요).",
        "skill": "팔을 늘여 대상을 잡아 " + mag("q_dmg", "q_ap") + " + 자신 최대 체력의 {q_hp}% 마법 피해와 {q_slow}% " + cc("둔화") +
                 "; 잡힌 챔피언은 " + t("{q_hold}초") + " 후 끌려와 내리꽂혀 같은 피해를 다시 받고, 주변 적은 " + t("{q_up}초") +
                 " " + cc("에어본") + ".",
        "skill2": t("{e_wind}초") + " 동안 힘을 모은 뒤 대상에게 날아가 착지하며 " + mag("e_dmg", "e_ap") +
                  " + 자신 최대 체력의 {e_hp}% 마법 피해와 주변 적 " + t("{e_up}초") + " " + cc("에어본") + ".",
        "ult": "저지 불가 상태로 {r_n}번 튀어 오르며, 착지할 때마다 " + mag("r_dmg", "r_ap") + " 마법 피해(이후 {r_k}%), " +
               t("{r_up}초") + " " + cc("에어본") + ", {r_slow}% " + cc("둔화") + ".",
        "names": ("탄성 주먹", "새총 발사", "바운스!"),
    },
    "ja": {
        "name": "ザック",
        "attack": "スライムの拳。" + n("スライムクラッシュ") + "：使用可能なとき通常攻撃が弾け、周囲の敵に" + mag("w_dmg", "w_ap") +
                  "の魔法ダメージ、英雄にはさらに" + tr("最大体力の{w_pct}%") + "の確定ダメージ（クールダウン" + t("{w_cd}秒") + "）。" +
                  n("はぐれスライム") + "：スキルが英雄に当たるとスライムが落ち、拾うと" + mag("b_heal", "b_heal_ap") + hl("回復") +
                  "（復活は拡張パック）。",
        "skill": "腕を伸ばして対象をつかみ" + mag("q_dmg", "q_ap") + "+自身の最大体力の{q_hp}%の魔法ダメージと{q_slow}%" + cc("スロウ") +
                 "。つかんだ英雄は" + t("{q_hold}秒") + "後に引き寄せて叩きつけ、同じダメージを再び与え周囲の敵を" + t("{q_up}秒") +
                 cc("ノックアップ") + "。",
        "skill2": t("{e_wind}秒") + "力をためて対象へ飛び、着地で" + mag("e_dmg", "e_ap") + "+自身の最大体力の{e_hp}%の魔法ダメージと周囲の敵を" +
                  t("{e_up}秒") + cc("ノックアップ") + "。",
        "ult": "阻止不能で{r_n}回跳ね、着地ごとに" + mag("r_dmg", "r_ap") + "の魔法ダメージ（2回目以降{r_k}%）、" + t("{r_up}秒") +
               cc("ノックアップ") + "と{r_slow}%" + cc("スロウ") + "。",
        "names": ("スライムパンチ", "ブッ飛びスライム", "レッツバウンス！"),
    },
}

C = "league_zac_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (the punch and the bounces lower: they come often), the
# voice as the other heroes'
SOUNDS = {f"league_zac_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("q", 0.7), ("q_hit", 0.65), ("q_slam", 0.85), ("w", 0.7), ("w_hit", 0.5),
    ("e", 0.75), ("e_land", 0.9), ("e_hit", 0.6), ("r", 0.85), ("r_hop", 0.55), ("r_land", 0.7), ("r_hit", 0.55),
    ("b_pick", 0.7), ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9),
    ("p_split", 0.85), ("p_reform", 0.85), ("vo_p", 0.9))}     # the last three: the add-on's revive
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("w_dmg", "w_ap", "w_pct", "b_heal", "b_heal_ap", "q_dmg", "q_ap", "q_hp", "q_slow", "e_dmg",
                           "e_ap", "e_hp", "r_n", "r_dmg", "r_ap", "r_k", "r_slow")}
    for k in ("w_cd", "q_hold", "q_up", "e_wind", "e_up", "r_up"):
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
    for lang, tx in TEXT.items():
        d = {"name": tx["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = tx[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), tx["names"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--face", help="X,Y from tfm2_ase.py face")
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 + the idle's top over the frame centre)")
    a = ap.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    tx = texts(p)
    bad = False
    for lang, (d, _) in tx.items():
        lens = {k: shown_length(TEXT[lang][k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(m > TOOLTIP_MAX[lang] for m in lens.values())
        print(lang, " ".join(f"{k}:{m}/{TOOLTIP_MAX[lang]}" for k, m in lens.items()))
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
    for k in [k for k in ov if ID + "_" in k]:      # his keys rebuilt (a renamed sound leaves none behind)
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
    if "Zac" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Zac. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
