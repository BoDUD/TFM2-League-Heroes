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
Walkers) and Dark Procession (the cage) in the attack's text. The texts say the main pack's rules (the add-on's copy has
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
        "attack": "抡铲。" + n("牧魂人") + "：临终仪式打英雄（打别的每两下）挖一座坟，满{g_n}座时下一铲唤醒{k_n}只" + n("雾行者") +
                  "咬目标" + t("{k_t}秒") + "（每只每口" + phys("k_dmg", "k_ratio") + "），同时" + n("暗灵缠身") + "把附近的敌方英雄" +
                  cc("定身") + t("{w_root}秒") + "。",
        "skill": "下一铲造成" + phys("q_dmg", "q_ratio") + "物理伤害，回复{q_heal} + " + ADi + "{q_heal_r}%生命。",
        "skill2": "扔出一团黑雾：范围内敌人受到" + phys("e_dmg", "e_ratio") + "+最大生命{e_hp}%，护甲-{e_arm}%持续" + t("{e_t}秒") +
                  "，" + cc("减速") + "{e_slow}%。",
        "ult": "在敌方英雄身后召唤" + n("迷雾室女") + "和{r_n}只雾行者，跟着它" + t("{r_t}秒") + "，" + t("每秒") + "抓" +
               phys("r_dmg", "r_ratio") + "；期间约里克普攻英雄额外造成最大生命{r_pct}%真实伤害。",
        "names": ("临终仪式", "哀伤之雾", "海屿悼词"),
    },
    "zh-hant": {
        "name": "約瑞科",
        "attack": "揮鏟。" + n("亡魂牧人") + "：臨終葬儀打英雄（打其他每兩下）挖一座墳，滿{g_n}座時下一鏟喚醒{k_n}隻" + n("霧行者") +
                  "咬目標" + t("{k_t}秒") + "（每隻每口" + phys("k_dmg", "k_ratio") + "），同時" + n("黯影屍陣") + "把附近的敵方英雄" +
                  cc("定身") + t("{w_root}秒") + "。",
        "skill": "下一鏟造成" + phys("q_dmg", "q_ratio") + "物理傷害，回復{q_heal} + " + ADi + "{q_heal_r}%生命。",
        "skill2": "丟出一團黑霧：範圍內敵人受到" + phys("e_dmg", "e_ratio") + "+最大生命{e_hp}%，護甲-{e_arm}%持續" + t("{e_t}秒") +
                  "，" + cc("緩速") + "{e_slow}%。",
        "ult": "在敵方英雄身後召喚" + n("迷霧少女") + "和{r_n}隻霧行者，跟著它" + t("{r_t}秒") + "，" + t("每秒") + "抓" +
               phys("r_dmg", "r_ratio") + "；期間約瑞科普攻英雄額外造成最大生命{r_pct}%真實傷害。",
        "names": ("臨終葬儀", "悲鳴瘴霧", "荒島輓歌"),
    },
    "en": {
        "name": "Yorick",
        "attack": "Shovel blows. " + n("Shepherd of Souls") + ": Last Rites on a champion (on anything else every second time) "
                  "digs a grave; with {g_n} graves the next one raises {k_n} " + n("Mist Walkers") + " that gnaw at the target for " +
                  t("{k_t}s") + " (" + phys("k_dmg", "k_ratio") + " a bite each), and " + n("Dark Procession") + " " +
                  cc("roots") + " the enemy champions near it for " + t("{w_root}s") + ".",
        "skill": "His next blow deals " + phys("q_dmg", "q_ratio") + " physical damage and heals him {q_heal} + " + ADi +
                 "{q_heal_r}%.",
        "skill2": "Throws a globule of Black Mist: enemies hit take " + phys("e_dmg", "e_ratio") + " + {e_hp}% max health, "
                  "lose {e_arm}% armour for " + t("{e_t}s") + " and are " + cc("slowed") + " {e_slow}%.",
        "ult": "Raises the " + n("Maiden of the Mist") + " and {r_n} walkers behind an enemy champion; she follows it for " +
               t("{r_t}s") + ", clawing for " + phys("r_dmg", "r_ratio") + " " + t("every second") + ", and his attacks on "
               "champions deal {r_pct}% max health more as true damage meanwhile.",
        "names": ("Last Rites", "Mourning Mist", "Eulogy of the Isles"),
    },
    "ko": {
        "name": "요릭",
        "attack": "삽 공격. " + n("영혼의 길잡이") + ": 최후의 의식으로 챔피언을 치면(그 외는 두 번마다) 무덤 생성, {g_n}개가 차면 "
                  "다음 일격에 " + n("안개 망령") + " {k_n}마리가 " + t("{k_t}초") + " 동안 대상을 물어뜯음(한 번에 " +
                  phys("k_dmg", "k_ratio") + "), " + n("망자의 진") + "이 주변 적 챔피언 " + t("{w_root}초") + " " + cc("속박") + ".",
        "skill": "다음 공격이 " + phys("q_dmg", "q_ratio") + " 물리 피해, 체력 {q_heal} + " + ADi + "{q_heal_r}% 회복.",
        "skill2": "검은 안개를 던짐: 범위 적에게 " + phys("e_dmg", "e_ratio") + " + 최대 체력 {e_hp}%, 방어력 -{e_arm}% " +
                  t("{e_t}초") + ", {e_slow}% " + cc("둔화") + ".",
        "ult": "적 챔피언 뒤에 " + n("안개 처녀") + "와 망령 {r_n}마리 소환, " + t("{r_t}초") + " 동안 따라다니며 " + t("매초") +
               " " + phys("r_dmg", "r_ratio") + "; 그동안 요릭의 챔피언 공격에 최대 체력 {r_pct}% 고정 피해 추가.",
        "names": ("최후의 의식", "애도의 안개", "군도의 장송곡"),
    },
    "ja": {
        "name": "ヨリック",
        "attack": "シャベル攻撃。" + n("魂の導き手") + "：葬送でチャンピオンを打つと（他は2回毎）墓を掘る、{g_n}つ溜まると次の一撃で" +
                  n("ミストウォーカー") + "{k_n}体が" + t("{k_t}秒") + "噛みつく（1回" + phys("k_dmg", "k_ratio") + "）、" +
                  n("屍の列") + "が周囲の敵チャンピオンを" + t("{w_root}秒") + cc("スネア") + "。",
        "skill": "次の攻撃が" + phys("q_dmg", "q_ratio") + "の物理ダメージ、体力{q_heal} + " + ADi + "{q_heal_r}%回復。",
        "skill2": "黒い霧を投げる：範囲の敵に" + phys("e_dmg", "e_ratio") + "+最大体力{e_hp}%、物理防御-{e_arm}%（" + t("{e_t}秒") +
                  "）、{e_slow}%" + cc("スロウ") + "。",
        "ult": "敵チャンピオンの背後に" + n("霧の乙女") + "とウォーカー{r_n}体を召喚、" + t("{r_t}秒") + "追従し" + t("毎秒") +
               phys("r_dmg", "r_ratio") + "；その間ヨリックのチャンピオンへの攻撃に最大体力{r_pct}%の確定ダメージ。",
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
    v = {k: p[k] for k in ("g_n", "k_n", "k_dmg", "k_ratio", "q_dmg", "q_ratio", "q_heal", "q_heal_r", "e_dmg", "e_ratio",
                           "e_hp", "e_arm", "e_slow", "r_n", "r_dmg", "r_ratio", "r_pct")}
    assert p["r_p"] == 60, "the ult texts say the Maiden claws every second"
    for k in ("k_t", "w_root", "e_t", "r_t"):
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
