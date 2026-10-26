"""Locke's text (5 languages), sound_info files and his keys in the shared files, numbers from build_locke.P
(setup_trundle.py's way).

    python tools/kit/setup_locke.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_locke in every language, description + skill_name),
sound/sfx/league_locke_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre, the
ban/pick card), mod.mod_info (VERSION, Locke named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 洛克 (灰烬驱魔人): 圣银穿心; 伏魔三钉, 灵焰仪式, 灰猎无影, 万魔狱; zh_TW 洛克: 銀樁咒殺;
咒釘簪命, 燃魂回元, 瞬影追命, 芻靈疆域; ja ロック: シルバー・ステイク; リチュアル・ネイル, ソウル・イグニッション, 灰塵の追撃, 煉獄;
ko 로크: 은빛 말뚝; 의식용 대못, 영혼 점화, 잿빛 추격, 연옥.
Slots: skill = Ritual Nails, skill2 = Ashen Pursuit, ult = Purgatory; Silver Stake and Soul Ignition in the attack's
text. The texts say the main pack's rules (the add-on's copy has its own: addons/league_locke/make_override.py). No combo
sentence in any text (the user's rule: the combos are the README's) - Ashen Pursuit landing by a champion is how W is
cast at all and the takedown reset is League's own E, so both are said.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_locke import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_locke"
VERSION = "0.225.0"     # above main 0.223.1 (#544 Samira) and Skarner's 0.224.0 (integrated in parallel), 2026-10-26
SEALS = 3               # build_locke's r_s1..r_s3
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names
M = "<#a974ffff>"      # magic damage / AP
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
T = "<#f5f5f5ff>"      # true damage, the execute
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to), the body's middle (44 game px hair to
# soles, Talon's / Graves's -14) and the ban/pick card (bp_card_audit.py at hd.rs UI_SIZES 0.85: -11 puts his hair 0.7 px
# under the canvas top and his soles 0.8 px over its bottom; only the nails raised in the idle reel's Q snippet reach
# over the top - Yorick's shovel tip)
VIEW = {"face": {"x": 4, "y": -37}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -11}}


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


def tr(x):
    return T + x + E


TEXT = {
    "zh-hans": {
        "name": "洛克",
        "attack": n("圣银穿心") + "：攻击附带" + mag("p_dmg", "p_ap") + "魔法伤害。" + n("灵焰仪式") +
                  "：灰猎无影落到敌方英雄身边时点燃（每" + t("{w_cd}秒") + "一次）：" + t("{w_t}秒") + "内攻速+{w_as}%、"
                  "移速+{w_ms}%（递减），" + t("每秒") + "受到最大生命{w_cost}%" + tr("真实伤害") + "，结束时回复{w_heal} + " +
                  APi + "{w_heal_ap}%生命。",
        "skill": "接连掷出三枚咒钉，每枚造成" + mag("q_dmg", "q_ap") + "魔法伤害并" + cc("减速") + "{q_slow}%" +
                 t("{q_slow_t}秒") + "（可叠加）。钉中英雄后" + t("{q_mark_t}秒") + "内，他的攻击引爆钉子：每枚" +
                 mag("q_pop", "q_pop_ap") + "魔法伤害，两枚+{q_two}%，三枚+{q_three}%。",
        "skill2": "瞬移到敌方英雄身边，对周围敌人造成" + mag("e_dmg", "e_ap") + "魔法伤害；" + t("{e_next}秒") +
                  "内下一次攻击冲穿目标，造成" + mag("e_dash", "e_dash_ap") + "魔法伤害。被他打过的英雄" + t("{p_win}秒") +
                  "内阵亡时冷却刷新。",
        "ult": "法器箱砸向敌方英雄：周围敌人受到" + mag("r_dmg", "r_ap") + "魔法伤害并" + cc("减速") + "{r_slow}%（递减）；"
               "英雄被标记" + t("{r_t}秒") + "，生命低于{r_ex} + " + APi + "{r_ex_ap}%即被" + tr("处决") + "。标记期间参与击杀得一层"
               "封印（最多{seals}层，阵亡清空）：处决线+{r_ex_step}，大招冷却最多剩{r_cap}%。",
        "names": ("伏魔三钉", "灰猎无影", "万魔狱"),
    },
    "zh-hant": {
        "name": "洛克",
        "attack": n("銀樁咒殺") + "：攻擊附帶" + mag("p_dmg", "p_ap") + "魔法傷害。" + n("燃魂回元") +
                  "：瞬影追命落到敵方英雄身邊時點燃（每" + t("{w_cd}秒") + "一次）：" + t("{w_t}秒") + "內攻速+{w_as}%、"
                  "移速+{w_ms}%（遞減），" + t("每秒") + "受到最大生命{w_cost}%" + tr("真實傷害") + "，結束時回復{w_heal} + " +
                  APi + "{w_heal_ap}%生命。",
        "skill": "接連擲出三枚咒釘，每枚造成" + mag("q_dmg", "q_ap") + "魔法傷害並" + cc("緩速") + "{q_slow}%" +
                 t("{q_slow_t}秒") + "（可疊加）。釘中英雄後" + t("{q_mark_t}秒") + "內，他的攻擊引爆咒釘：每枚" +
                 mag("q_pop", "q_pop_ap") + "魔法傷害，兩枚+{q_two}%，三枚+{q_three}%。",
        "skill2": "瞬移到敵方英雄身邊，對周圍敵人造成" + mag("e_dmg", "e_ap") + "魔法傷害；" + t("{e_next}秒") +
                  "內下一次攻擊衝穿目標，造成" + mag("e_dash", "e_dash_ap") + "魔法傷害。被他打過的英雄" + t("{p_win}秒") +
                  "內陣亡時冷卻重置。",
        "ult": "法器箱砸向敵方英雄：周圍敵人受到" + mag("r_dmg", "r_ap") + "魔法傷害並" + cc("緩速") + "{r_slow}%（遞減）；"
               "英雄被標記" + t("{r_t}秒") + "，生命低於{r_ex} + " + APi + "{r_ex_ap}%即被" + tr("處決") + "。標記期間參與擊殺得一層"
               "封印（最多{seals}層，陣亡清空）：處決線+{r_ex_step}，大招冷卻最多剩{r_cap}%。",
        "names": ("咒釘簪命", "瞬影追命", "芻靈疆域"),
    },
    "en": {
        "name": "Locke",
        "attack": n("Silver Stake") + ": attacks deal " + mag("p_dmg", "p_ap") + " bonus magic damage. " + n("Soul Ignition") +
                  ": landing Ashen Pursuit by an enemy champion ignites him (" + t("{w_cd}s") + " cooldown): " + t("{w_t}s") +
                  " of +{w_as}% attack speed and +{w_ms}% decaying move speed; he takes {w_cost}% max health as " +
                  tr("true damage") + " " + t("each second") + ", then heals {w_heal} + " + APi + "{w_heal_ap}%.",
        "skill": "Throws three nails in a row, each dealing " + mag("q_dmg", "q_ap") + " magic damage and " + cc("slowing") +
                 " {q_slow}% for " + t("{q_slow_t}s") + " (stacking). For " + t("{q_mark_t}s") + " after nailing a champion, "
                 "his attack pops the nails: " + mag("q_pop", "q_pop_ap") + " magic damage each, +{q_two}% for two, "
                 "+{q_three}% for three.",
        "skill2": "Blinks next to an enemy champion, dealing " + mag("e_dmg", "e_ap") + " magic damage around him; his next "
                  "attack within " + t("{e_next}s") + " dashes through the target for " + mag("e_dash", "e_dash_ap") +
                  " magic damage. Resets when a champion he hit dies within " + t("{p_win}s") + ".",
        "ult": "Hurls his case at an enemy champion: " + mag("r_dmg", "r_ap") + " magic damage around it and a {r_slow}% "
               "decaying " + cc("slow") + "; champions there are marked for " + t("{r_t}s") + " and " + tr("executed") +
               " below {r_ex} + " + APi + "{r_ex_ap}% health. A takedown while marked grants a seal (up to {seals}, lost on "
               "death): the line +{r_ex_step}, the ult's cooldown at most {r_cap}% left.",
        "names": ("Ritual Nails", "Ashen Pursuit", "Purgatory"),
    },
    "ko": {
        "name": "로크",
        "attack": n("은빛 말뚝") + ": 공격 시 " + mag("p_dmg", "p_ap") + " 추가 마법 피해. " + n("영혼 점화") +
                  ": 잿빛 추격이 적 챔피언 곁에 착지하면 발동(" + t("{w_cd}초") + "마다): " + t("{w_t}초") + " 동안 공격 속도 "
                  "+{w_as}%, 이동 속도 +{w_ms}%(점차 감소), " + t("매초") + " 최대 체력 {w_cost}% " + tr("고정 피해") +
                  ", 끝나면 체력 {w_heal} + " + APi + "{w_heal_ap}% 회복.",
        "skill": "대못 세 개를 연달아 던져 각각 " + mag("q_dmg", "q_ap") + " 마법 피해, " + t("{q_slow_t}초") + " 동안 {q_slow}% " +
                 cc("둔화") + "(중첩). 챔피언을 맞히면 " + t("{q_mark_t}초") + " 안에 그의 공격이 대못을 터뜨림: 개당 " +
                 mag("q_pop", "q_pop_ap") + " 마법 피해, 두 개 +{q_two}%, 세 개 +{q_three}%.",
        "skill2": "적 챔피언 곁으로 순간이동해 주변 적에게 " + mag("e_dmg", "e_ap") + " 마법 피해; " + t("{e_next}초") +
                  " 안의 다음 공격은 대상을 꿰뚫고 돌진해 " + mag("e_dash", "e_dash_ap") + " 마법 피해. 그가 때린 챔피언이 " +
                  t("{p_win}초") + " 안에 죽으면 재사용 대기시간 초기화.",
        "ult": "법구 상자를 적 챔피언에게 던짐: 주변 적에게 " + mag("r_dmg", "r_ap") + " 마법 피해, {r_slow}% " + cc("둔화") +
               "(점차 감소); 챔피언은 " + t("{r_t}초") + " 동안 표식, 체력이 {r_ex} + " + APi + "{r_ex_ap}% 미만이면 " +
               tr("처형") + ". 표식 중 처치 관여 시 봉인 1개(최대 {seals}개, 사망 시 사라짐): 처형선 +{r_ex_step}, 궁극기 "
               "재사용 대기시간은 최대 {r_cap}%만 남음.",
        "names": ("의식용 대못", "잿빛 추격", "연옥"),
    },
    "ja": {
        "name": "ロック",
        "attack": n("シルバー・ステイク") + "：攻撃に" + mag("p_dmg", "p_ap") + "の魔法ダメージ追加。" +
                  n("ソウル・イグニッション") + "：灰塵の追撃で敵チャンピオンの側に着地で発動（" + t("{w_cd}秒") + "毎）：" +
                  t("{w_t}秒") + "間攻撃速度+{w_as}%、移動速度最大+{w_ms}%、" + t("毎秒") + "最大体力{w_cost}%の" +
                  tr("確定ダメージ") + "、終了時に体力{w_heal} + " + APi + "{w_heal_ap}%回復。",
        "skill": "釘を3本続けて投げ、それぞれ" + mag("q_dmg", "q_ap") + "の魔法ダメージと" + t("{q_slow_t}秒") + "{q_slow}%" +
                 cc("スロウ") + "（重複）。チャンピオンに刺さると" + t("{q_mark_t}秒") + "以内の攻撃で釘が炸裂：1本" +
                 mag("q_pop", "q_pop_ap") + "の魔法ダメージ、2本+{q_two}%、3本+{q_three}%。",
        "skill2": "敵チャンピオンの側へ瞬間移動し周囲の敵に" + mag("e_dmg", "e_ap") + "の魔法ダメージ；" + t("{e_next}秒") +
                  "以内の次の攻撃は対象を突き抜けて" + mag("e_dash", "e_dash_ap") + "の魔法ダメージ。攻撃したチャンピオンが" +
                  t("{p_win}秒") + "以内に倒れるとクールダウン解消。",
        "ult": "ケースを敵チャンピオンに投げつけ、周囲の敵に" + mag("r_dmg", "r_ap") + "の魔法ダメージと{r_slow}%" +
               cc("スロウ") + "（減衰）；チャンピオンに" + t("{r_t}秒") + "の印、体力が{r_ex} + " + APi + "{r_ex_ap}%未満なら" +
               tr("処刑") + "。印の間のキル関与で封印1つ（最大{seals}、死亡で消える）：処刑ライン+{r_ex_step}、"
               "アルティメットのCDは最大{r_cap}%に。",
        "names": ("リチュアル・ネイル", "灰塵の追撃", "煉獄"),
    },
}

C = "league_locke_sfx_"     # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; three nails a cast and three checks a second: those a little softer
SOUNDS = {f"league_locke_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.55), ("q_throw", 0.5), ("q_hit", 0.55), ("q_pop", 0.7), ("e_blink", 0.65), ("e_dash", 0.6),
    ("reset", 0.55), ("w", 0.7), ("r", 0.75), ("r_throw", 0.65), ("r_land", 0.8), ("r_hit", 0.6), ("r_seal", 0.7),
    ("vo_q", 0.85), ("vo_w", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "w_as", "w_ms", "w_cost", "w_heal", "w_heal_ap", "q_dmg", "q_ap", "q_slow",
                           "q_pop", "q_pop_ap", "q_two", "q_three", "e_dmg", "e_ap", "e_dash", "e_dash_ap", "r_dmg", "r_ap",
                           "r_slow", "r_ex", "r_ex_ap", "r_ex_step", "r_cap")}
    for k in ("w_cd", "w_t", "q_slow_t", "q_mark_t", "e_next", "p_win", "r_t"):
        v[k] = secs(p[k])
    v["seals"] = SEALS
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
    if "Locke" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Locke. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
