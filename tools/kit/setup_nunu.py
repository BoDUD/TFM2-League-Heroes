"""Nunu & Willump's text (5 languages), sound_info files and their keys in the shared files, numbers from build_nunu.P.

    python tools/kit/setup_nunu.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_nunu in every language, description + skill_name),
sound/sfx/league_nunu_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre),
mod.mod_info (VERSION, Nunu & Willump named). Only their keys change in the shared files. JSON: indent 2, CRLF, UTF-8.
--check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 - zh_CN 努努和威朗普 (雪原双子): 弗雷尔卓德的召唤; 吞噬, 史上最大雪球！, 雪球飞射, 绝对零度; zh_TW
努努和威朗普: 弗雷爾卓德之喚; 吞噬, 巨無霸雪球！, 雪球連擊, 絕對零度; ja ヌヌ＆ウィルンプ: フレヨルドの呼び声; 丸かじり, 超特大の雪玉！,
雪玉連射, アブソリュート・ゼロ; ko 누누와 윌럼프: 프렐요드의 부름; 잡아먹기, 데굴데굴 눈덩이!, 눈덩이 팡팡팡, 절대 영도.
Slots: skill = Biggest Snowball Ever!, skill2 = Snowball Barrage, ult = Absolute Zero; the passive (Consume folded in) in
the attack's text. No combo sentence in any text (the user's rule); the README says them.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_nunu import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_nunu"
VERSION = "0.200.0"     # the next free number above main 0.199.0 (Aurora #479) (2026-10-23)
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical damage
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing, shields
E = "<>"
# champion_view: the face point between Nunu's eyes (ppu_restyle.py RESTYLE face_to: the cards and portraits show the
# boy, league_gnar's Mini the same way) and the ban/pick card (bp_card_audit.py: at UI size 0.85, hd.rs UI_SIZES, the
# rule's -7 keeps the pompom under the canvas top and the soles on its bottom)
VIEW = {"face": {"x": 3, "y": -36}, "center": {"x": 0, "y": -19}, "banpick_center": {"x": 0, "y": -7}}


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


TEXT = {
    "zh-hans": {
        "name": "努努和威朗普",
        "attack": "爪击。每第3次普攻是" + n("吞噬") + "：额外" + mag("q_dmg", "q_ap") + "魔法伤害（小兵野怪再受{q_mon}真实伤害），" +
                  hl("回复") + mag("q_heal", "q_heal_ap") + "生命；随后" + t("{p_t}秒") + "内自己和一名队友攻速+{p_as}%、移速+{p_ms}%，"
                  "普攻溅射周围{p_spl}%。",
        "skill": "推着雪球冲向目标，撞上造成" + mag("w_dmg", "w_ap") + "魔法伤害并" + cc("击飞") + t("{w_up}秒") + "；滚得越久越大，最多" +
                 "{w_k2}%伤害、" + cc("击飞") + t("{w_up2}秒") + "。",
        "skill2": "连扔{e_n}个雪球，每个" + mag("e_dmg", "e_ap") + "魔法伤害并" + cc("减速") + "{e_slow}%；扔完" + cc("禁锢") +
                  "被打中的英雄" + t("{e_root}秒") + "，造成" + mag("e_rdmg", "e_rap") + "魔法伤害。",
        "ult": "引导暴风雪" + t("{r_t}秒") + "，获得" + hl("护盾") + mag("r_sh", "r_sh_ap") + "，周围敌人" + cc("减速") +
               "{r_slow0}%到{r_slow1}%；结束时爆发造成" + mag("r_dmg", "r_ap") + "魔法伤害（被打断按已引导的时间计算）。",
        "names": ("史上最大雪球！", "雪球飞射", "绝对零度"),
    },
    "zh-hant": {
        "name": "努努和威朗普",
        "attack": "爪擊。每第3次普攻是" + n("吞噬") + "：額外" + mag("q_dmg", "q_ap") + "魔法傷害（小兵野怪再受{q_mon}真實傷害），" +
                  hl("回復") + mag("q_heal", "q_heal_ap") + "生命；之後" + t("{p_t}秒") + "內自己和一名隊友攻速+{p_as}%、移速+{p_ms}%，"
                  "普攻濺射周圍{p_spl}%。",
        "skill": "推著雪球衝向目標，撞上造成" + mag("w_dmg", "w_ap") + "魔法傷害並" + cc("擊飛") + t("{w_up}秒") + "；滾得越久越大，最多" +
                 "{w_k2}%傷害、" + cc("擊飛") + t("{w_up2}秒") + "。",
        "skill2": "連扔{e_n}顆雪球，每顆" + mag("e_dmg", "e_ap") + "魔法傷害並" + cc("緩速") + "{e_slow}%；扔完" + cc("禁錮") +
                  "被擊中的英雄" + t("{e_root}秒") + "，造成" + mag("e_rdmg", "e_rap") + "魔法傷害。",
        "ult": "引導暴風雪" + t("{r_t}秒") + "，獲得" + hl("護盾") + mag("r_sh", "r_sh_ap") + "，周圍敵人" + cc("緩速") +
               "{r_slow0}%到{r_slow1}%；結束時爆發造成" + mag("r_dmg", "r_ap") + "魔法傷害（被打斷按已引導的時間計算）。",
        "names": ("巨無霸雪球！", "雪球連擊", "絕對零度"),
    },
    "en": {
        "name": "Nunu & Willump",
        "attack": "Claw swipe. Every 3rd attack is " + n("Consume") + ": " + mag("q_dmg", "q_ap") + " more magic damage ("
                  "{q_mon} true damage more to minions and monsters) and " + hl("heals") + " " + mag("q_heal", "q_heal_ap") +
                  "; then for " + t("{p_t}s") + " they and an ally gain {p_as}% attack speed and {p_ms}% move speed, and "
                  "attacks splash {p_spl}% around.",
        "skill": "Rolls a snowball into the target: " + mag("w_dmg", "w_ap") + " magic damage and a " + cc("knock-up") +
                 " of " + t("{w_up}s") + "; the longer it rolls the bigger it grows, up to {w_k2}% damage and a " +
                 t("{w_up2}s") + " " + cc("knock-up") + ".",
        "skill2": "Throws {e_n} snowballs, each dealing " + mag("e_dmg", "e_ap") + " magic damage and " + cc("slowing") +
                  " {e_slow}%; then the champions hit are " + cc("rooted") + " for " + t("{e_root}s") + " and take " +
                  mag("e_rdmg", "e_rap") + " magic damage.",
        "ult": "Channels a blizzard for " + t("{r_t}s") + " under a " + hl("shield") + " of " + mag("r_sh", "r_sh_ap") +
               ", " + cc("slowing") + " nearby enemies {r_slow0}% rising to {r_slow1}%; at the end it bursts for " +
               mag("r_dmg", "r_ap") + " magic damage (a broken channel bursts for the share channelled).",
        "names": ("Biggest Snowball Ever!", "Snowball Barrage", "Absolute Zero"),
    },
    "ko": {
        "name": "누누와 윌럼프",
        "attack": "할퀴기. 3번째 기본 공격마다 " + n("잡아먹기") + ": " + mag("q_dmg", "q_ap") + " 마법 피해 추가(미니언·몬스터 {q_mon} "
                  "고정 피해 추가), " + mag("q_heal", "q_heal_ap") + " " + hl("회복") + "; 이후 " + t("{p_t}초") +
                  " 동안 자신과 아군 하나 공격 속도 +{p_as}%, 이동 속도 +{p_ms}%, 기본 공격이 주변에 {p_spl}% 튄다.",
        "skill": "눈덩이를 굴려 대상에 부딪쳐 " + mag("w_dmg", "w_ap") + " 마법 피해와 " + t("{w_up}초") + " " + cc("에어본") +
                 "; 오래 굴릴수록 커져 최대 {w_k2}% 피해, " + t("{w_up2}초") + " " + cc("에어본") + ".",
        "skill2": "눈덩이 {e_n}개를 던져 각각 " + mag("e_dmg", "e_ap") + " 마법 피해와 {e_slow}% " + cc("둔화") +
                  "; 이후 맞은 챔피언을 " + t("{e_root}초") + " " + cc("속박") + "하고 " + mag("e_rdmg", "e_rap") + " 마법 피해.",
        "ult": t("{r_t}초") + " 동안 눈보라를 정신 집중하며 " + mag("r_sh", "r_sh_ap") + " " + hl("보호막") + ", 주변 적 {r_slow0}%에서 "
               "{r_slow1}%까지 " + cc("둔화") + "; 끝나면 폭발해 " + mag("r_dmg", "r_ap") + " 마법 피해(끊기면 집중한 만큼).",
        "names": ("데굴데굴 눈덩이!", "눈덩이 팡팡팡", "절대 영도"),
    },
    "ja": {
        "name": "ヌヌ＆ウィルンプ",
        "attack": "爪で攻撃。3回目ごとの通常攻撃は" + n("丸かじり") + "：" + mag("q_dmg", "q_ap") + "の魔法ダメージ追加（ミニオン・モンスターは" +
                  "さらに{q_mon}の確定ダメージ）、" + mag("q_heal", "q_heal_ap") + hl("回復") + "。その後" + t("{p_t}秒") +
                  "自身と味方1体の攻撃速度+{p_as}%・移動速度+{p_ms}%、通常攻撃が周囲に{p_spl}%拡散。",
        "skill": "雪玉を転がして対象にぶつけ" + mag("w_dmg", "w_ap") + "の魔法ダメージと" + t("{w_up}秒") + cc("ノックアップ") +
                 "。長く転がすほど大きくなり最大{w_k2}%ダメージ・" + t("{w_up2}秒") + cc("ノックアップ") + "。",
        "skill2": "雪玉を{e_n}個投げ、それぞれ" + mag("e_dmg", "e_ap") + "の魔法ダメージと{e_slow}%" + cc("スロウ") +
                  "。投げ終わると当たった英雄を" + t("{e_root}秒") + cc("スネア") + "し" + mag("e_rdmg", "e_rap") + "の魔法ダメージ。",
        "ult": t("{r_t}秒") + "吹雪を詠唱し" + mag("r_sh", "r_sh_ap") + "の" + hl("シールド") + "、周囲の敵を{r_slow0}%から{r_slow1}%" +
               cc("スロウ") + "。終わると爆発し" + mag("r_dmg", "r_ap") + "の魔法ダメージ（中断時は詠唱した分）。",
        "names": ("超特大の雪玉！", "雪玉連射", "アブソリュート・ゼロ"),
    },
}

C = "league_nunu_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]; the sfx toward Lux's 0.8 (the swipe, the bite and the barrage's snowballs lower:
# they come often), the voice as the other heroes'
SOUNDS = {f"league_nunu_{k}": [(C + k, v, 0.0)] for k, v in (
    ("a", 0.5), ("a_hit", 0.55), ("q", 0.65), ("q_hit", 0.6), ("w", 0.75), ("w_hit", 0.85), ("e", 0.7),
    ("e_throw", 0.45), ("e_hit", 0.5), ("r", 0.85), ("r_boom", 0.9), ("r_hit", 0.6), ("vo_q", 0.85), ("vo_w", 0.85),
    ("vo_e", 0.85), ("vo_r", 0.9))}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(tk):
    return f"{tk / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("q_dmg", "q_ap", "q_mon", "q_heal", "q_heal_ap", "p_as", "p_ms", "p_spl", "w_dmg", "w_ap",
                           "w_k2", "e_n", "e_dmg", "e_ap", "e_slow", "e_rdmg", "e_rap", "r_sh", "r_sh_ap", "r_slow0",
                           "r_slow1", "r_dmg", "r_ap")}
    for k in ("p_t", "w_up", "w_up2", "e_root", "r_t"):
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
    for k in [k for k in ov if ID + "_" in k]:      # their keys rebuilt (a renamed sound leaves none behind)
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
    if "Nunu" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. &]+?)\. Kits", r", \1 and Nunu & Willump. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
