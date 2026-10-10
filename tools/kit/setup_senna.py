"""Senna's text (5 languages), sound_info files and her keys in the shared files, numbers from build_senna.P.

    python tools/kit/setup_senna.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in se/league): text/champion.i18n (league_senna in every language, description + skill_name),
sound/sfx/league_senna_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.90.0, Senna named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (work/se/rst.py: 赛娜 / 赦除, 黑暗洞灭, 无尽厮守, 黑雾咒附, 暗影燎原) and Data Dragon
16.19.1 (zh_TW 姍娜 / 赦罪 / 刺骨幽闇 / 終末之擁 / 黯霧詛咒 / 黎明之影, ja セナ / 魂の赦し / ピアシングダークネス / 最期の抱擁 /
黒き霧の呪い / ドーニングシャドウ, ko 세나 / 면죄 / 꿰뚫는 어둠 / 마지막 포옹 / 검은 안개의 저주 / 여명의 그림자).
The slot names: skill = Q, skill2 = W, ult = R; the passive and the automatic E are told in the attack's text. No combo
sentence in any text (the user's rule): the combos live in build_senna.py and the README.
DEATH[lang] is the attack text's "Mist lost on death" clause, which addons/league_senna_mist/make_override.py swaps.
`league_senna_attack` is the cannon's shot: the engine plays it by itself on every attack.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_senna import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_senna"
VERSION = "0.90.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7cfc00ff>"      # heals
S = "<#9fd8ffff>"      # shields
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 4, "y": -30}, "center": {"x": 0, "y": -12}}  # placeholder until the sprite
DEATH = {"zh-hans": "（死亡清空）", "zh-hant": "（死亡清空）", "en": " (lost on death)", "ja": "（デスで失う）",
         "ko": "(사망 시 소멸)"}


def phy(k, r=None):
    return f"{O}{{{k}}}{E} + {ADi}{O}{{{r or k + '_r'}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "赛娜",
        "attack": O + "赦除" + E + "：技能和普攻标记敌方英雄，下次普攻吸走：额外{p_hp}%最大生命伤害+1层黑雾；每" + A + "{p_wave}秒" + E +
                  "一次普攻和击杀英雄也+1层。每层攻击+{p_atk}、射程略增，每2层暴击+1%" + DEATH["zh-hans"] + "。" + O + "黑雾咒附" + E +
                  "（自动）：英雄贴近时，她和身边队友隐身" + A + "{e_t}秒" + E + "、移速+{e_ms}%。",
        "skill": "遗物炮射出穿透目标的暗影光束：直线上的敌人受到" + phy("q_dmg", "q_ratio") + "物理伤害并" + R + "减速{q_slow}%" + E + A +
                 "{q_slow_t}秒" + E + "，队友英雄回复" + G + "{q_heal}" + E + " + " + ADi + G + "{q_hratio}%" + E + "生命。",
        "skill2": "射出黑雾，附着在首个命中的敌人身上并造成" + phy("w_dmg", "w_ratio") + "物理伤害；" + A + "{w_wait}秒" + E +
                  "后黑雾扩散，" + R + "禁锢" + E + "它和周围的敌人" + A + "{w_root}秒" + E + "。",
        "ult": "蓄力后朝远方交战中的英雄射出横贯战场的光束：中心对敌方英雄造成" + phy("r_dmg", "r_ratio") + "物理伤害，两侧宽阔的光芒给她和沿途队友英雄" +
               S + "{r_sh}" + E + " + " + ADi + S + "{r_sratio}%护盾" + E + A + "{r_sh_t}秒" + E + "。",
        "names": ("黑暗洞灭", "无尽厮守", "暗影燎原"),
    },
    "zh-hant": {
        "name": "姍娜",
        "attack": O + "赦罪" + E + "：技能和普攻標記敵方英雄，下次普攻吸走：額外{p_hp}%最大生命傷害+1層黑霧；每" + A + "{p_wave}秒" + E +
                  "一次普攻和擊殺英雄也+1層。每層攻擊+{p_atk}、射程略增，每2層暴擊+1%" + DEATH["zh-hant"] + "。" + O + "黯霧詛咒" + E +
                  "（自動）：英雄貼近時，她和身邊隊友隱形" + A + "{e_t}秒" + E + "、移速+{e_ms}%。",
        "skill": "聖物砲射出穿透目標的暗影光束：直線上的敵人受到" + phy("q_dmg", "q_ratio") + "物理傷害並" + R + "緩速{q_slow}%" + E + A +
                 "{q_slow_t}秒" + E + "，隊友英雄回復" + G + "{q_heal}" + E + " + " + ADi + G + "{q_hratio}%" + E + "生命。",
        "skill2": "射出黑霧，附著在首個命中的敵人身上並造成" + phy("w_dmg", "w_ratio") + "物理傷害；" + A + "{w_wait}秒" + E +
                  "後黑霧擴散，" + R + "定身" + E + "它和周圍的敵人" + A + "{w_root}秒" + E + "。",
        "ult": "蓄力後朝遠方交戰中的英雄射出橫貫戰場的光束：中心對敵方英雄造成" + phy("r_dmg", "r_ratio") + "物理傷害，兩側寬闊的光芒給她和沿途隊友英雄" +
               S + "{r_sh}" + E + " + " + ADi + S + "{r_sratio}%護盾" + E + A + "{r_sh_t}秒" + E + "。",
        "names": ("刺骨幽闇", "終末之擁", "黎明之影"),
    },
    "en": {
        "name": "Senna",
        "attack": O + "Absolution" + E + ": her hits mark an enemy champion; the next attack takes it: +{p_hp}% max health "
                  "damage, 1 Mist. +1 Mist per attack every " + A + "{p_wave}s" + E + " and per champion kill. Mist: +{p_atk} attack, "
                  "some range, +1% crit per 2" + DEATH["en"] + ". " + O + "Curse of the Black Mist" + E + " (auto): an enemy champion "
                  "near, she and nearby allies are invisible " + A + "{e_t}s" + E + ", +{e_ms}% speed.",
        "skill": "The relic cannon fires a shadow beam through its target: enemies in the line take " + phy("q_dmg", "q_ratio") +
                 " physical damage and are " + R + "slowed {q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + "; allied champions in it "
                 "heal " + G + "{q_heal}" + E + " + " + ADi + G + "{q_hratio}%" + E + ".",
        "skill2": "Fires the Black Mist: it clings to the first enemy hit, dealing " + phy("w_dmg", "w_ratio") + " physical damage, and "
                  "after " + A + "{w_wait}s" + E + " spreads, " + R + "rooting" + E + " it and the enemies around it for " + A + "{w_root}s" +
                  E + ".",
        "ult": "Charges, then fires a beam of light across the battlefield at a fighting champion far away: its core deals " +
               phy("r_dmg", "r_ratio") + " physical damage to enemy champions; its wide light gives her and the allied champions "
               "along it a " + S + "{r_sh}" + E + " + " + ADi + S + "{r_sratio}% shield" + E + " for " + A + "{r_sh_t}s" + E + ".",
        "names": ("Piercing Darkness", "Last Embrace", "Dawning Shadow"),
    },
    "ko": {
        "name": "세나",
        "attack": O + "면죄" + E + ": 스킬·공격이 적 챔피언에 표식, 다음 공격이 거둠: 최대 체력 {p_hp}% 추가 피해, 안개 1. " + A +
                  "{p_wave}초" + E + "마다 공격 1회·처치도 안개 1. 안개당 공격력 +{p_atk}, 사거리↑, 2개마다 치명타 +1%" +
                  DEATH["ko"] + ". " + O + "검은 안개의 저주" + E + "(자동): 적 챔피언 접근 시 자신과 주변 아군 " + A + "{e_t}초" + E +
                  " 투명, 이속 +{e_ms}%.",
        "skill": "렐릭 캐논이 대상을 관통하는 어둠의 광선을 발사: 직선의 적은 " + phy("q_dmg", "q_ratio") + "의 물리 피해를 입고 " + A +
                 "{q_slow_t}초" + E + " 동안 " + R + "{q_slow}% 둔화" + E + ", 아군 챔피언은 " + G + "{q_heal}" + E + " + " + ADi + G +
                 "{q_hratio}%" + E + " 회복.",
        "skill2": "검은 안개를 발사해 처음 맞힌 적에게 달라붙어 " + phy("w_dmg", "w_ratio") + "의 물리 피해. " + A + "{w_wait}초" + E +
                  " 뒤 퍼지며 그 적과 주변 적을 " + A + "{w_root}초" + E + " 동안 " + R + "속박" + E + ".",
        "ult": "기를 모은 뒤 멀리 교전 중인 챔피언에게 전장을 가로지르는 광선 발사: 중심은 적 챔피언에게 " + phy("r_dmg", "r_ratio") +
               "의 물리 피해, 넓은 빛은 자신과 경로의 아군 챔피언에게 " + A + "{r_sh_t}초" + E + " 동안 " + S + "{r_sh}" + E + " + " + ADi + S +
               "{r_sratio}% 보호막" + E + ".",
        "names": ("꿰뚫는 어둠", "마지막 포옹", "여명의 그림자"),
    },
    "ja": {
        "name": "セナ",
        "attack": O + "魂の赦し" + E + "：スキルと攻撃で敵チャンピオンに印、次の攻撃で回収：最大体力{p_hp}%追加ダメージと霧1。" + A +
                  "{p_wave}秒" + E + "毎の攻撃1回とキルでも霧1。霧1つで攻撃力+{p_atk}、射程微増、2つ毎にクリ+1%" + DEATH["ja"] +
                  "。" + O + "黒き霧の呪い" + E + "（自動）：敵接近で自身と味方が" + A + "{e_t}秒" + E + "インビジブル、移速+{e_ms}%。",
        "skill": "レリックキャノンが対象を貫く闇の光線を放つ：直線上の敵に" + phy("q_dmg", "q_ratio") + "の物理ダメージと" + A + "{q_slow_t}秒" +
                 E + R + "{q_slow}%スロウ" + E + "、味方チャンピオンは" + G + "{q_heal}" + E + " + " + ADi + G + "{q_hratio}%" + E + "回復。",
        "skill2": "黒き霧を放ち、最初に当たった敵に取り憑いて" + phy("w_dmg", "w_ratio") + "の物理ダメージ。" + A + "{w_wait}秒" + E +
                  "後に広がり、その敵と周りの敵を" + A + "{w_root}秒" + E + R + "スネア" + E + "。",
        "ult": "力を溜め、遠くで交戦中のチャンピオンへ戦場を貫く光線を放つ：中心は敵チャンピオンに" + phy("r_dmg", "r_ratio") +
               "の物理ダメージ、幅広い光は自身と通り道の味方チャンピオンに" + A + "{r_sh_t}秒" + E + S + "{r_sh}" + E + " + " + ADi + S +
               "{r_sratio}%のシールド" + E + "。",
        "names": ("ピアシングダークネス", "最期の抱擁", "ドーニングシャドウ"),
    },
}

C = "league_senna_sfx_"   # clip names differ from the sound names: a clip named like its sound is not found in game
N = "league_senna_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    N + "attack": [(C + "attack", 0.45, 0.0)],
    N + "a_hit": [(C + "a_hit", 0.35, 0.0)],
    N + "p_take": [(C + "p_take", 0.5, 0.0)],
    N + "p_gain": [(C + "p_gain", 0.4, 0.0)],
    N + "q": [(C + "q", 0.5, 0.0)],
    N + "q_hit": [(C + "q_hit", 0.45, 0.0)],
    N + "q_heal": [(C + "q_heal", 0.4, 0.0)],
    N + "w": [(C + "w", 0.5, 0.0)],
    N + "w_hit": [(C + "w_hit", 0.45, 0.0)],
    N + "w_root": [(C + "w_root", 0.5, 0.0)],
    N + "e": [(C + "e", 0.5, 0.0)],
    N + "r_cast": [(C + "r_cast", 0.55, 0.0)],
    N + "r_fire": [(C + "r_fire", 0.6, 0.0)],
    N + "r_hit": [(C + "r_hit", 0.5, 0.0)],
    N + "r_sh": [(C + "r_sh", 0.45, 0.0)],
    N + "vo_q": [(C + "vo_q", 0.8, 0.0)],
    N + "vo_w": [(C + "vo_w", 0.8, 0.0)],
    N + "vo_e": [(C + "vo_e", 0.8, 0.0)],
    N + "vo_r": [(C + "vo_r", 0.8, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    keys = ("p_hp", "p_atk", "e_ms", "q_dmg", "q_ratio", "q_slow", "q_heal", "q_hratio", "w_dmg", "w_ratio", "r_dmg",
            "r_ratio", "r_sh", "r_sratio")
    v = {k: p[k] for k in keys}
    v.update({k: secs(p[k]) for k in ("p_wave", "e_t", "q_slow_t", "w_wait", "w_root", "r_sh_t")})
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
    for k in [k for k in ov if ID in k]:      # her keys rebuilt (a renamed sound leaves none behind)
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
    if "Senna" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Senna. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
