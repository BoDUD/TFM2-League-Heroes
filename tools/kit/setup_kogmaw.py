"""Kog'Maw's text (5 languages), sound_info files and his keys in the shared files, numbers from build_kogmaw.P.

    python tools/kit/setup_kogmaw.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in km/league): text/champion.i18n (league_kogmaw in every language, description + skill_name),
sound/sfx/league_kogmaw_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.83.0, Kog'Maw named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/km/rst.py: 克格莫 / 来自艾卡西亚的惊喜, 腐蚀唾液, 生化弹幕, 虚空淤泥, 活体大炮)
and Data Dragon 16.19.1 (zh_TW 寇格魔 / 來自伊卡西亞的驚喜 / 腐蝕唾液 / 生化彈幕 / 虛空淤泥 / 生化巨炮, ko 코그모 / 이케시아식
마무리 / 부식성 침 / 생체마법 폭격 / 공허의 분비물 / 살아있는 곡사포, ja コグ＝マウ / イカシアの自爆 / 腐食粘液 / 有機性魔力砲 /
ヴォイド分泌液 / 生体空撃砲).
The slot names: skill = Q, skill2 = E, ult = R; the passive and the automatic W are told in the attack's text.
No `league_kogmaw_attack` sound: the engine would play it at the start of every attack; the spit plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_kogmaw import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_kogmaw"
VERSION = "0.83.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control, shred
T = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 8, "y": -23}, "center": {"x": 0, "y": -10}}


def phy(k):
    return f"{O}{{{k}_dmg}}{E} + {ADi}{O}{{{k}_ratio}}%{E}"


def tru(k, r):
    return f"{T}{{{k}}}{E} + {ADi}{T}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "克格莫",
        "attack": O + "生化弹幕" + E + "（自动，" + A + "{w_cd}秒" + E + "）：攻击时开启" + A + "{w_t}秒" + E + "，射程+{w_range}，攻击附带目标" +
                  O + "{w_hp}%最大生命值" + E + "伤害。" + O + "来自艾卡西亚的惊喜" + E + "：死后虚空之力化身追向附近敌方英雄，爆炸造成" +
                  tru("p_dmg", "p_ratio") + "真实伤害。",
        "skill": "吐出腐蚀唾液，命中首个敌人造成" + phy("q") + "伤害，" + R + "护甲和魔抗-{q_shred}%" + E + A + "{q_shred_t}秒" + E +
                 "。被动：攻速+{q_as}%。" + O + "连招" + E + "：生化弹幕开启时自动补一发Q。",
        "skill2": "吐出贯穿的虚空淤泥，造成" + phy("e") + "伤害并" + R + "减速{e_slow}%" + E + "，留下" + A + "{e_trail}秒" + E + "的减速淤泥带。" +
                  O + "连招" + E + "：淤泥命中英雄后补一发活体大炮。",
        "ult": "炮击远处交战中的英雄，" + A + "{r_delay}秒" + E + "后落地造成" + phy("r") + "伤害；被炸后剩余生命不足" + tru("r_x", "r_x_ratio") +
               "的英雄直接被击杀。一轮最多" + A + "3发" + E + "，冷却" + A + "{r_lock}秒" + E + "。",
        "names": ("腐蚀唾液", "虚空淤泥", "活体大炮"),
    },
    "zh-hant": {
        "name": "寇格魔",
        "attack": O + "生化彈幕" + E + "（自動，" + A + "{w_cd}秒" + E + "）：攻擊時開啟" + A + "{w_t}秒" + E + "，射程+{w_range}，攻擊附帶目標" +
                  O + "{w_hp}%最大生命值" + E + "傷害。" + O + "來自伊卡西亞的驚喜" + E + "：死後虛空之力化身追向附近敵方英雄，爆炸造成" +
                  tru("p_dmg", "p_ratio") + "真實傷害。",
        "skill": "吐出腐蝕唾液，命中首個敵人造成" + phy("q") + "傷害，" + R + "護甲和魔抗-{q_shred}%" + E + A + "{q_shred_t}秒" + E +
                 "。被動：攻速+{q_as}%。" + O + "連招" + E + "：生化彈幕開啟時自動補一發Q。",
        "skill2": "吐出貫穿的虛空淤泥，造成" + phy("e") + "傷害並" + R + "緩速{e_slow}%" + E + "，留下" + A + "{e_trail}秒" + E + "的緩速淤泥帶。" +
                  O + "連招" + E + "：淤泥命中英雄後補一發生化巨炮。",
        "ult": "砲擊遠處交戰中的英雄，" + A + "{r_delay}秒" + E + "後落地造成" + phy("r") + "傷害；被炸後剩餘生命不足" + tru("r_x", "r_x_ratio") +
               "的英雄直接被擊殺。一輪最多" + A + "3發" + E + "，冷卻" + A + "{r_lock}秒" + E + "。",
        "names": ("腐蝕唾液", "虛空淤泥", "生化巨炮"),
    },
    "en": {
        "name": "Kog'Maw",
        "attack": "Spits acid. " + O + "Bio-Arcane Barrage" + E + " (automatic, " + A + "{w_cd}s" + E + "): an attack turns it on for " + A +
                  "{w_t}s" + E + ": +{w_range} range and attacks deal " + O + "{w_hp}% of the target's max health" + E + ". " + O +
                  "Icathian Surprise" + E + ": when he dies his void form chases a nearby enemy champion and bursts for " +
                  tru("p_dmg", "p_ratio") + " true damage.",
        "skill": "Spits caustic acid: the first enemy hit takes " + phy("q") + " and loses " + R + "{q_shred}% armour and magic resist" + E +
                 " for " + A + "{q_shred_t}s" + E + ". Passive: +{q_as}% attack speed. " + O + "Combo" + E +
                 ": when Bio-Arcane Barrage turns on, a Caustic Spittle follows.",
        "skill2": "Spews piercing void ooze for " + phy("e") + ", " + R + "slowing {e_slow}%" + E + ", and leaves a slowing trail for " + A +
                  "{e_trail}s" + E + ". " + O + "Combo" + E + ": an ooze that hits a champion calls a Living Artillery shell on it.",
        "ult": "Shells a fighting champion far away: after " + A + "{r_delay}s" + E + " it lands for " + phy("r") + "; champions left under " +
               tru("r_x", "r_x_ratio") + " health die. Up to " + A + "3 shells" + E + " a volley, then " + A + "{r_lock}s" + E + " cooldown.",
        "names": ("Caustic Spittle", "Void Ooze", "Living Artillery"),
    },
    "ko": {
        "name": "코그모",
        "attack": O + "생체마법 폭격" + E + "(자동, " + A + "{w_cd}초" + E + "): 공격 시 " + A + "{w_t}초" + E + " 동안 사거리 +{w_range}, 공격이 대상 " + O +
                  "최대 체력의 {w_hp}%" + E + " 피해. " + O + "이케시아식 마무리" + E + ": 죽으면 공허의 힘이 가까운 적 챔피언을 쫓아가 터져 " +
                  tru("p_dmg", "p_ratio") + "의 고정 피해.",
        "skill": "부식성 침을 뱉어 처음 맞힌 적에게 " + phy("q") + "의 피해, " + A + "{q_shred_t}초" + E + " 동안 " + R + "방어력과 마법 저항력 -{q_shred}%" +
                 E + ". 기본 지속 효과: 공격 속도 +{q_as}%. " + O + "연계" + E + ": 생체마법 폭격이 켜지면 Q가 이어서 나감.",
        "skill2": "관통하는 공허의 분비물로 " + phy("e") + "의 피해와 " + R + "{e_slow}% 둔화" + E + ", " + A + "{e_trail}초" + E + " 동안 둔화 자국을 남김. " +
                  O + "연계" + E + ": 분비물이 챔피언에게 맞으면 살아있는 곡사포가 이어서 떨어짐.",
        "ult": "교전 중인 먼 챔피언을 포격: " + A + "{r_delay}초" + E + " 뒤 떨어져 " + phy("r") + "의 피해, 남은 체력이 " + tru("r_x", "r_x_ratio") +
               " 이하인 챔피언은 처치. 한 번에 최대 " + A + "3발" + E + ", 재사용 대기 " + A + "{r_lock}초" + E + ".",
        "names": ("부식성 침", "공허의 분비물", "살아있는 곡사포"),
    },
    "ja": {
        "name": "コグ＝マウ",
        "attack": O + "有機性魔力砲" + E + "（自動、" + A + "{w_cd}秒" + E + "）：攻撃で" + A + "{w_t}秒" + E + "発動、射程+{w_range}、攻撃が対象の" + O +
                  "最大体力の{w_hp}%" + E + "のダメージ。" + O + "イカシアの自爆" + E + "：死ぬとヴォイドの力が近くの敵チャンピオンを追い爆発し" +
                  tru("p_dmg", "p_ratio") + "の確定ダメージ。",
        "skill": "腐食粘液を吐き最初の敵に" + phy("q") + "、" + A + "{q_shred_t}秒" + E + R + "物理防御と魔法防御-{q_shred}%" + E + "。自動効果：攻撃速度+{q_as}%。" +
                 O + "コンボ" + E + "：有機性魔力砲の発動時にQが続く。",
        "skill2": "貫通するヴォイド分泌液で" + phy("e") + "と" + R + "{e_slow}%スロウ" + E + "、" + A + "{e_trail}秒" + E + "スロウ地帯を残す。" + O + "コンボ" + E +
                  "：チャンピオンに当たると生体空撃砲が続く。",
        "ult": "交戦中の遠くのチャンピオンを砲撃：" + A + "{r_delay}秒" + E + "後に着弾し" + phy("r") + "、残り体力が" + tru("r_x", "r_x_ratio") +
               "以下のチャンピオンは倒れる。1回最大" + A + "3発" + E + "、クールダウン" + A + "{r_lock}秒" + E + "。",
        "names": ("腐食粘液", "ヴォイド分泌液", "生体空撃砲"),
    },
}

C = "league_kogmaw_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
S = "league_kogmaw_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    S + "a_shot": [(C + "attack", 0.45, 0.0)],
    S + "a_hit": [(C + "attack_hit", 0.35, 0.0)],
    S + "w_cast": [(C + "w", 0.55, 0.0)],
    S + "q_cast": [(C + "q", 0.45, 0.0)],
    S + "q_shot": [(C + "q_shot", 0.55, 0.0)],
    S + "q_hit": [(C + "q_splash", 0.45, 0.0)],
    S + "e_cast": [(C + "e", 0.45, 0.0)],
    S + "e_shot": [(C + "e_shot", 0.5, 0.0)],
    S + "e_hit": [(C + "e_splash", 0.45, 0.0)],
    S + "r_shot": [(C + "r", 0.55, 0.0)],
    S + "r_fall": [(C + "r_whistle", 0.5, 0.0)],
    S + "r_hit": [(C + "r_blast", 0.5, 0.0)],
    S + "p_wake": [(C + "p", 0.6, 0.0)],
    S + "p_boom": [(C + "p_burst", 0.6, 0.0)],
    S + "vo_q": [(C + "vo_q", 0.8, 0.0)],
    S + "vo_w": [(C + "vo_w", 0.8, 0.0)],
    S + "vo_e": [(C + "vo_e", 0.8, 0.0)],
    S + "vo_r": [(C + "vo_r", 0.8, 0.0)],
    S + "vo_p": [(C + "vo_death", 0.8, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    keys = ("w_hp", "p_dmg", "p_ratio", "q_dmg", "q_ratio", "q_shred", "q_as", "e_dmg", "e_ratio", "e_slow", "r_dmg",
            "r_ratio", "r_x", "r_x_ratio")
    v = {k: p[k] for k in keys}
    v["w_range"] = p["w_range"] // 100
    v.update({k: secs(p[k]) for k in ("w_cd", "w_t", "q_shred_t", "e_trail", "r_delay", "r_lock")})
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
    if "Kog'Maw" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Kog'Maw. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
