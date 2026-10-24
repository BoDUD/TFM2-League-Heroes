"""Kled's text (5 languages), sound_info files and their keys in the shared files, numbers from build_kled.P
(setup_sejuani.py's way).

    python tools/kit/setup_kled.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_kled in every language, description + skill_name),
sound/sfx/league_kled_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Kled named). Only his keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.21.1 - zh_CN 克烈 (暴怒骑士): 怯战蜥蜴斯嘎尔; 飞索捕熊器, 暴烈秉性, 比武, 冲啊——！！; zh_TW 克雷德:
膽小的小嘎; 飛射夾夾, 生性暴戾, 比武角逐, 衝啊！！！; ja クレッド: 弱虫トカゲ「スカール」; トラバサミロープ, 狂暴の宴, ジャウスト,
チャァァァァァァァジ！！！; ko 클레드: 겁쟁이 도마뱀 스칼; 덫날리기, 버럭버럭, 이랴!, 돌겨어어억!!!.
Slots: skill = Bear Trap on a Rope (on foot Pocket Pistol), skill2 = Jousting, ult = Chaaaaaaaarge!!!; Skaarl (the
dismount, courage, the remount) and Violent Tendencies in the attack's text. The texts say the main pack's rules (the
add-on's copy has its own: addons/league_kled/make_override.py). No combo sentence in any text (the user's rule: the
combos are the README's).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_kled import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_kled"
VERSION = "0.216.0"     # above main 0.215.4 (#518), no open PR above it, 2026-10-25
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# champion_view: the face point between his eyes (ppu_restyle.py RESTYLE face_to) and the ban/pick card
# (bp_card_audit.py with hd.rs UI_SIZES)
VIEW = {"face": {"x": 2, "y": -28}, "center": {"x": 0, "y": -16}, "banpick_center": {"x": 0, "y": -12}}


def phys(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def sh(d, r):
    """A shield: an amount and an AD ratio, uncoloured."""
    return f"{{{d}}} + {ADi}{{{r}}}%"


def t(x):
    return A + x + E


def n(x):
    return O + x + E


def cc(x):
    return R + x + E


TEXT = {
    "zh-hans": {
        "name": "克烈",
        "attack": "挥斧。" + n("斯嘎尔") + "替他挡伤害（" + sh("sk_hp", "sk_ad") + "），没了就下马：攻击-{dm_atk}%，不能比武、冲锋；"
                  "打人攒勇气，满了上马。" + n("暴烈秉性") + "：每" + t("{w_cd}秒") + "四下快攻，第四下多" + phys("w_dmg", "w_ratio") +
                  "+最大生命{w_pct}%。",
        "skill": "扔捕熊夹造成" + phys("q_dmg", "q_ratio") + "；夹住英雄" + cc("减速") + "{q_slow}%，" + t("{q_teth}秒") + "后再造成" +
                 phys("q2_dmg", "q2_ratio") + "并" + cc("拽过来") + "。下马时是" + n("随身手枪") + "：" + phys("p_dmg", "p_ratio") +
                 "，自己往后跳。",
        "skill2": "斯嘎尔冲过目标造成" + phys("e_dmg", "e_ratio") + "物理伤害，加速{e_ms}%；穿过英雄还会再冲回来一次。",
        "ult": "带护盾（" + sh("r_sh", "r_sh_ad") + "）冲向敌方英雄，撞上造成" + phys("r_dmg", "r_ratio") + "+最大生命{r_pct}%并" +
               cc("击退") + "；身边队友加速{r_ms}%。",
        "names": ("飞索捕熊器", "比武", "冲啊——！！"),
    },
    "zh-hant": {
        "name": "克雷德",
        "attack": "揮斧。" + n("小嘎") + "替他擋傷害（" + sh("sk_hp", "sk_ad") + "），沒了就下馬：攻擊-{dm_atk}%，不能比武、衝鋒；"
                  "打人攢勇氣，滿了上馬。" + n("生性暴戾") + "：每" + t("{w_cd}秒") + "四下快攻，第四下多" + phys("w_dmg", "w_ratio") +
                  "+最大生命{w_pct}%。",
        "skill": "丟出捕獸夾造成" + phys("q_dmg", "q_ratio") + "；夾住英雄" + cc("緩速") + "{q_slow}%，" + t("{q_teth}秒") + "後再造成" +
                 phys("q2_dmg", "q2_ratio") + "並" + cc("拉過來") + "。下馬時是" + n("隨身手槍") + "：" + phys("p_dmg", "p_ratio") +
                 "，自己往後跳。",
        "skill2": "小嘎衝過目標造成" + phys("e_dmg", "e_ratio") + "物理傷害，加速{e_ms}%；穿過英雄還會再衝回來一次。",
        "ult": "帶護盾（" + sh("r_sh", "r_sh_ad") + "）衝向敵方英雄，撞上造成" + phys("r_dmg", "r_ratio") + "+最大生命{r_pct}%並" +
               cc("擊退") + "；身邊隊友加速{r_ms}%。",
        "names": ("飛射夾夾", "比武角逐", "衝啊！！！"),
    },
    "en": {
        "name": "Kled",
        "attack": "Axe blows. " + n("Skaarl") + " takes his damage (" + sh("sk_hp", "sk_ad") + "); when he flees Kled fights "
                  "on foot: -{dm_atk}% attack, no Jousting, no charge; hitting enemies builds courage to remount. " +
                  n("Violent Tendencies") + ": every " + t("{w_cd}s") + " four fast attacks, the fourth dealing " +
                  phys("w_dmg", "w_ratio") + " + {w_pct}% max health more.",
        "skill": "Throws a bear trap for " + phys("q_dmg", "q_ratio") + "; a champion caught is " + cc("slowed") +
                 " {q_slow}%, then after " + t("{q_teth}s") + " takes " + phys("q2_dmg", "q2_ratio") + " and is " +
                 cc("yanked") + " to him. On foot it is " + n("Pocket Pistol") + ": " + phys("p_dmg", "p_ratio") +
                 ", knocking him back.",
        "skill2": "Skaarl dashes through the target for " + phys("e_dmg", "e_ratio") + " physical damage and +{e_ms}% speed; "
                  "through a champion he dashes back once more.",
        "ult": "Charges an enemy champion with a shield (" + sh("r_sh", "r_sh_ad") + "): the ram deals " +
               phys("r_dmg", "r_ratio") + " + {r_pct}% max health and " + cc("knocks it back") + "; allies near him "
               "+{r_ms}% speed.",
        "names": ("Bear Trap on a Rope", "Jousting", "Chaaaaaaaarge!!!"),
    },
    "ko": {
        "name": "클레드",
        "attack": "도끼 공격. " + n("스칼") + "이 피해를 대신 받음(" + sh("sk_hp", "sk_ad") + "), 도망가면 걸어서 싸움: "
                  "공격력 -{dm_atk}%, 이랴!·돌격 불가; 적을 치면 용기가 쌓여 다시 탑승. " + n("버럭버럭") + ": " + t("{w_cd}초") +
                  "마다 빠른 4회 공격, 4번째 " + phys("w_dmg", "w_ratio") + " + 최대 체력 {w_pct}%.",
        "skill": "덫을 던져 " + phys("q_dmg", "q_ratio") + "; 걸린 챔피언 {q_slow}% " + cc("둔화") + ", " + t("{q_teth}초") +
                 " 뒤 " + phys("q2_dmg", "q2_ratio") + " 후 " + cc("끌어옴") + ". 걸어서는 " + n("주머니 권총") + ": " +
                 phys("p_dmg", "p_ratio") + ", 뒤로 밀려남.",
        "skill2": "스칼이 대상을 관통 돌진해 " + phys("e_dmg", "e_ratio") + " 물리 피해, 이동 속도 +{e_ms}%; 챔피언을 지나면 "
                  "한 번 더 돌진.",
        "ult": "보호막(" + sh("r_sh", "r_sh_ad") + ")을 두르고 적 챔피언에게 돌격, 부딪히면 " + phys("r_dmg", "r_ratio") +
               " + 최대 체력 {r_pct}%와 " + cc("넉백") + "; 주변 아군 이동 속도 +{r_ms}%.",
        "names": ("덫날리기", "이랴!", "돌겨어어억!!!"),
    },
    "ja": {
        "name": "クレッド",
        "attack": "斧で攻撃。" + n("スカール") + "がダメージを肩代わり（" + sh("sk_hp", "sk_ad") + "）、逃げると徒歩で戦う："
                  "攻撃-{dm_atk}%、ジャウスト・突撃不可；敵を打つと勇気が溜まり再騎乗。" + n("狂暴の宴") + "：" + t("{w_cd}秒") +
                  "毎に4回の速攻、4回目" + phys("w_dmg", "w_ratio") + "+最大体力{w_pct}%。",
        "skill": "トラバサミを投げ" + phys("q_dmg", "q_ratio") + "；捕えたチャンピオンを{q_slow}%" + cc("スロウ") + "、" +
                 t("{q_teth}秒") + "後に" + phys("q2_dmg", "q2_ratio") + "で" + cc("引き寄せ") + "。徒歩時は" +
                 n("ポケットピストル") + "：" + phys("p_dmg", "p_ratio") + "、自分は後ろへ跳ぶ。",
        "skill2": "スカールが対象を貫いて突進し" + phys("e_dmg", "e_ratio") + "の物理ダメージ、移動速度+{e_ms}%；チャンピオンを"
                  "貫くともう一度突進。",
        "ult": "シールド（" + sh("r_sh", "r_sh_ad") + "）を張って敵チャンピオンへ突撃、衝突で" + phys("r_dmg", "r_ratio") +
               "+最大体力{r_pct}%と" + cc("ノックバック") + "；周囲の味方の移動速度+{r_ms}%。",
        "names": ("トラバサミロープ", "ジャウスト", "チャァァァァァァァジ！！！"),
    },
}

C = "league_kled_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the impacts loud, the voice as the other heroes'
SOUNDS = {f"league_kled_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.45), ("a_hit", 0.5), ("w", 0.6), ("w_last", 0.55), ("w_hit", 0.7), ("q", 0.65), ("q_hit", 0.7),
    ("q_yank", 0.7), ("p", 0.75), ("p_hit", 0.55), ("e", 0.65), ("e2", 0.65), ("e_hit", 0.6), ("r", 0.8),
    ("r_crash", 0.85), ("r_hit", 0.7), ("dismount", 0.75), ("remount", 0.75), ("vo_q", 0.85), ("vo_w", 0.85),
    ("vo_e", 0.85), ("vo_r", 0.9), ("vo_p", 0.85), ("vo_off", 0.9), ("vo_mount", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("sk_hp", "sk_ad", "dm_atk", "w_dmg", "w_ratio", "w_pct", "q_dmg", "q_ratio", "q_slow", "q2_dmg",
                           "q2_ratio", "p_dmg", "p_ratio", "e_dmg", "e_ratio", "e_ms", "r_sh", "r_sh_ad", "r_dmg", "r_ratio",
                           "r_pct", "r_ms")}
    for k in ("w_cd", "q_teth"):
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
    if "Kled" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Kled. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
