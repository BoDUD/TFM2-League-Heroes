"""Dr. Mundo's text (5 languages), sound_info files and his keys in the shared files, numbers from build_drmundo.P.

    python tools/kit/setup_drmundo.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_drmundo in every language, description + skill_name),
sound/sfx/league_drmundo_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.120.0, Dr. Mundo named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 蒙多医生 / 祖安狂人 - Data Dragon swaps name and title; 想去哪就去哪, 病毒屠刀,
电击疗法, 大力行医, 极限剂量; zh_TW 蒙多醫生 / 想去哪就去哪 / 病毒骨鋸 / 心臟電擊器 / 鈍擊創傷 / 最大劑量, ja ドクター・ムンド /
気ままな往診 / 骨切りノコギリ / 心臓ビリビリ / 野蛮な痛み / マキシマム投与, ko 문도 박사 / 가고 싶은 데로 간다 / 오염된 뼈톱 /
심장 전기 충격 / 둔기에 의한 외상 / 최대 투여량).
Slots: skill = Q, skill2 = W, ult = R; the passive and E are told in the attack's text. No combo sentence in any text
(the user's rule). No `league_drmundo_attack` sound: the engine would play it at the start of every attack; the chop
plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_drmundo import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_drmundo"
VERSION = "0.120.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7dd87dff>"      # heals
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 4, "y": -34}, "center": {"x": 0, "y": -16}}

EB = O + "{e_dmg}" + E + " + " + ADi + O + "{e_ad}%" + E
WT = M + "{w_tick}" + E + " + " + ADi + O + "{w_ad}%" + E
WE = M + "{w_end}" + E + " + " + ADi + O + "{w_end_ad}%" + E
RH = G + "{r_heal}" + E + " + " + ADi + G + "{r_heal_ad}%" + E
PH = G + "{p_heal}" + E + " + " + ADi + G + "{p_heal_ad}%" + E

TEXT = {
    "zh-hans": {
        "name": "蒙多医生",
        "attack": O + "想去哪就去哪" + E + "：首次被控后免控" + A + "{p_imm}秒" + E + "并丢下药罐，捡起回复" + PH + "。" +
                  O + "大力行医" + E + "：每" + A + "{e_cd}秒" + E + "一次普攻额外造成" + EB + "伤害，打死的单位被打飞，撞伤身后的敌人。",
        "skill": "扔出骨锯，命中第一个单位造成" + M + "{q_dmg}" + E + M + "魔法伤害" + E + "，" + R + "减速{q_slow}%" + E + A + "{q_slow_t}秒" + E +
                 "并回复" + G + "{q_heal}" + E + "生命；命中英雄额外造成其最大生命{q_thp}%真实伤害、多回复" + G + "{q_heal_c}" + E + "。",
        "skill2": "电击身边的敌人" + A + "{w_t}秒" + E + "（每" + A + "{w_per}秒" + E + WT + "），挨打时积攒灰色生命；结束时电击造成" + WE +
                  "，命中英雄回复全部灰色生命，只命中小兵回复一半。",
        "ult": "被围攻时给自己注射：立即回复" + RH + "生命，" + A + "{r_t}秒" + E + "内最大生命+{r_hp}、每秒回复" + G + "{r_regen}" + E + "生命、移速+{r_ms}%。",
        "names": ("病毒屠刀", "电击疗法", "极限剂量"),
    },
    "zh-hant": {
        "name": "蒙多醫生",
        "attack": O + "想去哪就去哪" + E + "：首次被控後免控" + A + "{p_imm}秒" + E + "並丟下藥罐，撿起回復" + PH + "。" +
                  O + "鈍擊創傷" + E + "：每" + A + "{e_cd}秒" + E + "一次普攻額外造成" + EB + "傷害，打死的單位被打飛，撞傷身後的敵人。",
        "skill": "扔出骨鋸，命中第一個單位造成" + M + "{q_dmg}" + E + M + "魔法傷害" + E + "，" + R + "緩速{q_slow}%" + E + A + "{q_slow_t}秒" + E +
                 "並回復" + G + "{q_heal}" + E + "生命；命中英雄額外造成其最大生命{q_thp}%真實傷害、多回復" + G + "{q_heal_c}" + E + "。",
        "skill2": "電擊身邊的敵人" + A + "{w_t}秒" + E + "（每" + A + "{w_per}秒" + E + WT + "），挨打時累積灰色生命；結束時電擊造成" + WE +
                  "，命中英雄回復全部灰色生命，只命中小兵回復一半。",
        "ult": "被圍攻時替自己注射：立即回復" + RH + "生命，" + A + "{r_t}秒" + E + "內最大生命+{r_hp}、每秒回復" + G + "{r_regen}" + E + "生命、跑速+{r_ms}%。",
        "names": ("病毒骨鋸", "心臟電擊器", "最大劑量"),
    },
    "en": {
        "name": "Dr. Mundo",
        "attack": O + "Goes Where He Pleases" + E + ": after the first crowd control on him he is immune for " + A + "{p_imm}s" + E +
                  " and drops a chem-tank; picking it up heals " + PH + ". " + O + "Blunt Force Trauma" + E + ": every " + A + "{e_cd}s" + E +
                  " an attack deals " + EB + " more; a unit it kills is flung, hurting enemies behind it.",
        "skill": "Throws his bone saw at the first unit hit: " + M + "{q_dmg} magic damage" + E + ", a " + R + "{q_slow}% slow" + E + " for " + A +
                 "{q_slow_t}s" + E + " and " + G + "{q_heal}" + E + " health back. A champion also takes {q_thp}% of its max health as true damage and heals him " +
                 G + "{q_heal_c}" + E + " more.",
        "skill2": "Zaps nearby enemies for " + A + "{w_t}s" + E + " (" + WT + " every " + A + "{w_per}s" + E + "), storing grey health as he is hit. The final zap deals " +
                  WE + ": hitting a champion heals all the grey health, only minions half.",
        "ult": "Doses himself when cornered: heals " + RH + " at once and for " + A + "{r_t}s" + E + " gains {r_hp} max health, " + G + "{r_regen}" + E +
               " health a second and {r_ms}% move speed.",
        "names": ("Infected Bonesaw", "Heart Zapper", "Maximum Dosage"),
    },
    "ko": {
        "name": "문도 박사",
        "attack": O + "가고 싶은 데로 간다" + E + ": 처음 군중 제어를 받으면 " + A + "{p_imm}초" + E + " 면역, 화학 통을 떨어뜨려 주우면 " + PH + " 회복. " +
                  O + "둔기에 의한 외상" + E + ": " + A + "{e_cd}초" + E + "마다 기본 공격이 " + EB + " 추가 피해, 처치한 유닛을 날려 뒤의 적에게 피해.",
        "skill": "뼈톱을 던져 첫 대상에게 " + M + "{q_dmg} 마법 피해" + E + ", " + A + "{q_slow_t}초" + E + " " + R + "{q_slow}% 둔화" + E + ", " + G + "{q_heal}" + E +
                 " 회복. 챔피언이면 최대 체력 {q_thp}% 고정 피해와 " + G + "{q_heal_c}" + E + " 추가 회복.",
        "skill2": A + "{w_t}초" + E + " 동안 주변 적을 감전 (" + A + "{w_per}초" + E + "마다 " + WT + "), 맞을 때 회색 체력 저장. 마지막 감전 " + WE +
                  ": 챔피언 적중 시 회색 체력 전부, 미니언만 적중 시 절반 회복.",
        "ult": "포위되면 스스로 투약: 즉시 " + RH + " 회복, " + A + "{r_t}초" + E + " 동안 최대 체력 +{r_hp}, 초당 " + G + "{r_regen}" + E + " 회복, 이동 속도 +{r_ms}%.",
        "names": ("오염된 뼈톱", "심장 전기 충격", "최대 투여량"),
    },
    "ja": {
        "name": "ドクター・ムンド",
        "attack": O + "気ままな往診" + E + "：最初の行動妨害の後" + A + "{p_imm}秒" + E + "無効、薬缶を落とし拾うと" + PH + "回復。" +
                  O + "野蛮な痛み" + E + "：" + A + "{e_cd}秒" + E + "毎に通常攻撃が" + EB + "追加ダメージ、倒した敵を吹き飛ばし後ろの敵に当てる。",
        "skill": "骨ノコギリを投げ最初の敵に" + M + "{q_dmg}魔法ダメージ" + E + "と" + R + "{q_slow}%スロウ" + E + "（" + A + "{q_slow_t}秒" + E + "）、" + G +
                 "{q_heal}" + E + "回復。チャンピオンなら最大体力{q_thp}%の確定ダメージと" + G + "{q_heal_c}" + E + "追加回復。",
        "skill2": A + "{w_t}秒" + E + "周囲を感電（" + A + "{w_per}秒" + E + "毎に" + WT + "）、被弾でグレー体力を蓄積。最後の電撃" + WE +
                  "：チャンピオンに当たれば全回復、ミニオンのみなら半分。",
        "ult": "囲まれると自ら投与：即" + RH + "回復、" + A + "{r_t}秒" + E + "最大体力+{r_hp}、毎秒" + G + "{r_regen}" + E + "回復、移動速度+{r_ms}%。",
        "names": ("骨切りノコギリ", "心臓ビリビリ", "マキシマム投与"),
    },
}

C = "league_drmundo_sfx_"
S_ = "league_drmundo_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.45, 0.0), ("e", "e", 0.5, 0.0), ("e_hit", "e_hit", 0.55, 0.0),
    ("e_fling", "e_fling_hit", 0.5, 0.0), ("e_fling_hit", "e_fling_hit", 0.5, 0.0),
    ("q", "q", 0.55, 0.0), ("q_hit", "q_hit", 0.55, 0.0), ("q_heal", "q_heal", 0.4, 0.0),
    ("w", "w", 0.55, 0.0), ("w_end", "w_end", 0.6, 0.0), ("r", "r", 0.6, 0.0),
    ("p_shake", "p_shake", 0.55, 0.0), ("p_land", "p_land", 0.5, 0.0), ("p_pick", "p_pick", 0.55, 0.0),
    ("p_break", "p_break", 0.5, 0.0),
    ("vo_q", "vo_q", 0.8, 0.0), ("vo_w", "vo_w", 0.8, 0.0), ("vo_e", "vo_e", 0.8, 0.0), ("vo_r", "vo_r", 0.85, 0.0),
    ("vo_p", "vo_p", 0.8, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_heal", "p_heal_ad", "e_dmg", "e_ad", "q_dmg", "q_slow", "q_heal", "q_thp", "q_heal_c",
                           "w_tick", "w_ad", "w_end", "w_end_ad", "r_heal", "r_heal_ad", "r_hp", "r_regen", "r_ms")}
    v.update({k: secs(p[k]) for k in ("p_imm", "e_cd", "q_slow_t", "w_per", "r_t")})
    v["w_t"] = secs(p["w_n"] * p["w_per"])
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
    if "Dr. Mundo" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Dr. Mundo. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
