"""Yorick's text (5 languages), sound_info files and their keys in the shared files, numbers from build_yorick.P
(setup_kled.py's way).

    python tools/kit/setup_yorick.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_yorick in every language, description + skill_name),
sound/sfx/league_yorick_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Yorick named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 约里克 (牧魂人): 牧魂人; 临终仪式, 暗灵缠身, 哀伤之雾, 海屿悼词; zh_TW 約瑞科: 亡魂牧人;
臨終葬儀, 黯影屍陣, 悲鳴瘴霧, 荒島輓歌; ja ヨリック: 魂の導き手; 葬送, 屍の列, 悲嘆の霧, 嘆きの墓標; ko 요릭: 영혼의 길잡이;
최후의 의식, 망자의 진, 애도의 안개, 군도의 장송곡.
Slots: skill = Last Rites, skill2 = Mourning Mist, ult = Eulogy of the Isles; the Shepherd of Souls (graves, the Mist
Walkers) and Dark Procession (W, no slot: the ring of wall the controller casts) in the attack's text. The texts say the main pack's rules (the add-on's copy has
its own: addons/league_yorick/make_override.py). No combo sentence in any text (the user's rule: the combos are the
README's).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_yorick import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_yorick"
VERSION = "0.217.0"     # above main 0.216.0 (#520 Kled), no open PR, 2026-10-25
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 3, "y": -31}, "center": {"x": 0, "y": -18}, "banpick_center": {"x": 0, "y": -11}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


TEXT = {
    "zh-hans": {
        "name": "约里克",
        "attack": "抡铲。" + n("牧魂人") + "：临终仪式打英雄（打别的每两下）挖一座坟，最多4座；满{g_n}座时下一铲每座坟唤醒1只" +
                  n("雾行者") + "咬目标" + t("{k_t}秒") + "（每口" + phys("k_dmg", "k_ratio") + "）。" + n("暗灵缠身") +
                  "：自动对附近敌方英雄施放，" + t("{w_delay}秒") + "后立起一圈墙" + t("{w_t}秒") + "，圈里的敌方英雄出不去、圈外的进不来。",
        "skill": "下一铲造成" + phys("q_dmg", "q_ratio") + "物理伤害，回复{q_heal} + " + ADi + "{q_heal_r}%生命。",
        "skill2": "扔出一团黑雾：范围内敌人受到" + phys("e_dmg", "e_ratio") + "+最大生命{e_hp}%物理伤害，护甲-{e_arm}%持续" +
                  t("{e_t}秒") + "，" + cc("减速") + "{e_slow}%；打中英雄时约里克移速+{e_ms}%持续" + t("{e_t}秒") + "。",
        "ult": "召唤" + n("迷雾室女") + "跟着约里克" + t("{r_t}秒") + "，" + t("每秒") + "向附近敌人放魂弹（" + phys("r_dmg", "r_ratio") +
               "），打中英雄留下标记：约里克下一次普攻或黑雾打中英雄时额外造成最大生命{r_pct}%真实伤害；另有{r_n}只" + n("雾行者") +
               "扑向目标。",
        "names": ("临终仪式", "哀伤之雾", "海屿悼词"),
    },
    "zh-hant": {
        "name": "約瑞科",
        "attack": "揮鏟。" + n("亡魂牧人") + "：臨終葬儀打英雄（打其他每兩下）挖一座墳，最多4座；滿{g_n}座時下一鏟每座墳喚醒1隻" +
                  n("霧行者") + "咬目標" + t("{k_t}秒") + "（每口" + phys("k_dmg", "k_ratio") + "）。" + n("黯影屍陣") +
                  "：自動對附近敵方英雄施放，" + t("{w_delay}秒") + "後立起一圈牆" + t("{w_t}秒") + "，圈內的敵方英雄出不去、圈外的進不來。",
        "skill": "下一鏟造成" + phys("q_dmg", "q_ratio") + "物理傷害，回復{q_heal} + " + ADi + "{q_heal_r}%生命。",
        "skill2": "丟出一團黑霧：範圍內敵人受到" + phys("e_dmg", "e_ratio") + "+最大生命{e_hp}%物理傷害，護甲-{e_arm}%持續" +
                  t("{e_t}秒") + "，" + cc("緩速") + "{e_slow}%；打中英雄時約瑞科移速+{e_ms}%持續" + t("{e_t}秒") + "。",
        "ult": "召喚" + n("迷霧少女") + "跟著約瑞科" + t("{r_t}秒") + "，" + t("每秒") + "向附近敵人放魂彈（" + phys("r_dmg", "r_ratio") +
               "），打中英雄留下標記：約瑞科下一次普攻或黑霧打中英雄時額外造成最大生命{r_pct}%真實傷害；另有{r_n}隻" + n("霧行者") +
               "撲向目標。",
        "names": ("臨終葬儀", "悲鳴瘴霧", "荒島輓歌"),
    },
    "en": {
        "name": "Yorick",
        "attack": "Shovel blows. " + n("Shepherd of Souls") + ": Last Rites digs a grave on a champion (else every 2nd time), "
                  "up to 4; with {g_n}+ the next raises a " + n("Mist Walker") + " a grave to gnaw the target for " +
                  t("{k_t}s") + " (" + phys("k_dmg", "k_ratio") + " a bite). " + n("Dark Procession") + " (cast by itself): "
                  "after " + t("{w_delay}s") + " a ring of spirits stands " + t("{w_t}s") + " round an enemy champion; enemy "
                  "champions can't cross it.",
        "skill": "His next blow deals " + phys("q_dmg", "q_ratio") + " physical damage and heals him {q_heal} + " + ADi +
                 "{q_heal_r}%.",
        "skill2": "Throws a globule of Black Mist: enemies hit take " + phys("e_dmg", "e_ratio") + " + {e_hp}% max health "
                  "physical damage, lose {e_arm}% armour for " + t("{e_t}s") + " and are " + cc("slowed") + " {e_slow}%; on a "
                  "champion he gains {e_ms}% move speed for " + t("{e_t}s") + ".",
        "ult": "Raises the " + n("Maiden of the Mist") + " to follow him for " + t("{r_t}s") + ", firing a bolt " +
               t("every second") + " at an enemy near him (" + phys("r_dmg", "r_ratio") + "); a champion hit is marked: his next "
               "attack or mist on a champion deals {r_pct}% max health more as true damage. {r_n} " + n("Mist Walkers") +
               " fall on the target.",
        "names": ("Last Rites", "Mourning Mist", "Eulogy of the Isles"),
    },
    "ko": {
        "name": "요릭",
        "attack": "삽 공격. " + n("영혼의 길잡이") + ": 최후의 의식이 챔피언을 치면(그 외는 두 번마다) 무덤 생성(최대 4개), {g_n}개 "
                  "이상이면 다음 일격에 무덤마다 " + n("안개 망령") + "이 " + t("{k_t}초") + " 동안 물어뜯음(한 번에 " +
                  phys("k_dmg", "k_ratio") + "). " + n("망자의 진") + ": 자동 시전, " + t("{w_delay}초") + " 후 적 챔피언 주위에 벽 " +
                  t("{w_t}초") + ": 적 챔피언은 넘을 수 없음.",
        "skill": "다음 공격이 " + phys("q_dmg", "q_ratio") + " 물리 피해, 체력 {q_heal} + " + ADi + "{q_heal_r}% 회복.",
        "skill2": "검은 안개를 던짐: 범위 적에게 " + phys("e_dmg", "e_ratio") + " + 최대 체력 {e_hp}% 물리 피해, 방어력 -{e_arm}% " +
                  t("{e_t}초") + ", {e_slow}% " + cc("둔화") + "; 챔피언 적중 시 요릭 이동 속도 +{e_ms}% " + t("{e_t}초") + ".",
        "ult": n("안개 처녀") + "가 " + t("{r_t}초") + " 동안 요릭을 따라다니며 " + t("매초") + " 주변 적에게 영혼탄(" +
               phys("r_dmg", "r_ratio") + "), 맞은 챔피언에 표식: 요릭의 다음 공격이나 안개가 챔피언에 적중하면 최대 체력 {r_pct}% "
               "고정 피해 추가; " + n("안개 망령") + " {r_n}마리가 대상을 덮침.",
        "names": ("최후의 의식", "애도의 안개", "군도의 장송곡"),
    },
    "ja": {
        "name": "ヨリック",
        "attack": "シャベル攻撃。" + n("魂の導き手") + "：葬送でチャンピオンを打つと（他は2回毎）墓を掘る（最大4）、{g_n}つ以上で次の一撃は" +
                  "墓1つに" + n("ミストウォーカー") + "1体が" + t("{k_t}秒") + "噛みつく（1回" + phys("k_dmg", "k_ratio") + "）。" +
                  n("屍の列") + "：自動で使い、" + t("{w_delay}秒") + "後に敵チャンピオンの周りに壁の輪が" + t("{w_t}秒") +
                  "立つ：敵チャンピオンは越えられない。",
        "skill": "次の攻撃が" + phys("q_dmg", "q_ratio") + "の物理ダメージ、体力{q_heal} + " + ADi + "{q_heal_r}%回復。",
        "skill2": "黒い霧を投げる：範囲の敵に" + phys("e_dmg", "e_ratio") + "+最大体力{e_hp}%の物理ダメージ、物理防御-{e_arm}%（" +
                  t("{e_t}秒") + "）、{e_slow}%" + cc("スロウ") + "；チャンピオンに当たるとヨリックの移動速度+{e_ms}%（" +
                  t("{e_t}秒") + "）。",
        "ult": n("霧の乙女") + "が" + t("{r_t}秒") + "ヨリックに付き従い" + t("毎秒") + "近くの敵へ魂弾（" + phys("r_dmg", "r_ratio") +
               "）、当たったチャンピオンに印：ヨリックの次の攻撃か霧がチャンピオンに当たると最大体力{r_pct}%の確定ダメージ；" +
               n("ミストウォーカー") + "{r_n}体が対象を襲う。",
        "names": ("葬送", "悲嘆の霧", "嘆きの墓標"),
    },
}

C = "league_yorick_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the impacts loud, the voice as the other heroes'
SOUNDS = {f"league_yorick_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.5), ("q", 0.6), ("q_hit", 0.7), ("q_grave", 0.6), ("q_awake", 0.75), ("k_spawn", 0.7),
    ("k_bite", 0.45), ("k_leap", 0.55), ("w_wall", 0.75), ("w_hit", 0.55), ("e", 0.6), ("e_land", 0.65), ("e_hit", 0.55),
    ("r", 0.8), ("r_spawn", 0.85), ("r_claw", 0.6), ("vo_q", 0.85), ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("g_n", "k_dmg", "k_ratio", "q_dmg", "q_ratio", "q_heal", "q_heal_r", "e_dmg", "e_ratio",
                           "e_hp", "e_arm", "e_slow", "e_ms", "r_n", "r_dmg", "r_ratio", "r_pct")}
    assert p["r_p"] == 60, "the ult texts say the Maiden fires every second"
    for k in ("k_t", "w_delay", "w_t", "e_t", "r_t"):
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
    if "Yorick" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Yorick. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
