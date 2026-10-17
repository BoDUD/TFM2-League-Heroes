"""Shen's text (5 languages), sound_info files and his keys in the shared files, numbers from build_shen.P.

    python tools/kit/setup_shen.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in sn/league): text/champion.i18n (league_shen in every language, description + skill_name),
sound/sfx/league_shen_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.89.0, Shen named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: zh_CN from the client's string table (慎 / 忍法！气合盾 / 奥义！暮临 / 奥义！魂佑 / 奥义！影缚 / 秘奥义！慈悲度魂落),
Data Dragon 16.19.1 (zh_TW 慎 / 凝氣盾 / 暮光強襲 / 靈氣庇護 / 影襲 / 並肩作戰, ja シェン / 内気功 / 護刃招来 / 防人の帳 /
殺気駆け / 瞬身護法, ko 쉔 / 기 보호막 / 황혼 강습 / 의지의 결계 / 그림자 돌진 / 단결된 의지). The slot names: skill = Q,
skill2 = E, ult = R; the passive and the automatic W are told in the attack's and Q's texts. No combo sentence in any
text (the user's rule): E's blade pull is told as what the dash does.
No `league_shen_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_shen import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_shen"
VERSION = "0.89.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control, immunity
W = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 0, "y": -34}, "center": {"x": 0, "y": -12}}


def phy(k):
    return f"{O}{{{k}_dmg}}{E} + {ADi}{O}{{{k}_ratio}}%{E}"


def sh(k):
    return f"{A}{{{k}_sh}}{E} + {ADi}{A}{{{k}_sh_ratio}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "慎",
        "attack": O + "忍法！气合盾" + E + "：施放技能后获得" + sh("p") + "护盾" + A + "{p_sh_t}秒" + E + "（" + A + "{p_cd}秒" + E +
                  "一次，技能命中英雄则缩短）。强化普攻额外{q_a_dmg}伤害，对英雄再加其最大生命{q_a_hp}%（刀穿过英雄则{q_a_hp_big}%、攻速+{q_as}%）。",
        "skill": "召回灵魂之刃，从目标身后飞回，沿途造成" + phy("q") + "伤害并" + R + "减速{q_slow}%" + E + "，之后{q_n}次普攻强化。刀回手时附近有敌方英雄则施放" +
                 O + "奥义！魂佑" + E + "：" + A + "{w_t}秒" + E + "内区域中的友方英雄不受普攻伤害（" + A + "{w_cd}秒" + E + "冷却）。",
        "skill2": "向前突进，沿途敌人受到" + phy("e") + "伤害并被" + R + "嘲讽{e_taunt}秒" + E + "。嘲讽到英雄且暮临就绪时，灵魂之刃从突进起点飞回、穿过他们。",
        "ult": "全图有友方英雄被控，或与敌方英雄缠斗且离慎较远时：给他" + sh("r") + "护盾" + A + "{r_sh_t}秒" + E + "，慎引导" + A + "{r_ch}秒" + E +
               "后传送到他身边（被控则中断）。",
        "names": ("奥义！暮临", "奥义！影缚", "秘奥义！慈悲度魂落"),
    },
    "zh-hant": {
        "name": "慎",
        "attack": O + "凝氣盾" + E + "：施放技能後獲得" + sh("p") + "護盾" + A + "{p_sh_t}秒" + E + "（" + A + "{p_cd}秒" + E +
                  "一次，技能命中英雄則縮短）。強化普攻額外{q_a_dmg}傷害，對英雄再加其最大生命{q_a_hp}%（刀穿過英雄則{q_a_hp_big}%、攻速+{q_as}%）。",
        "skill": "召回靈魂之刃，從目標身後飛回，沿途造成" + phy("q") + "傷害並" + R + "緩速{q_slow}%" + E + "，之後{q_n}次普攻強化。刀回手時附近有敵方英雄則施放" +
                 O + "靈氣庇護" + E + "：" + A + "{w_t}秒" + E + "內區域中的友方英雄不受普攻傷害（" + A + "{w_cd}秒" + E + "冷卻）。",
        "skill2": "向前突進，沿途敵人受到" + phy("e") + "傷害並被" + R + "嘲諷{e_taunt}秒" + E + "。嘲諷到英雄且暮光強襲就緒時，靈魂之刃從突進起點飛回、穿過他們。",
        "ult": "全圖有友方英雄被控，或與敵方英雄纏鬥且離慎較遠時：給他" + sh("r") + "護盾" + A + "{r_sh_t}秒" + E + "，慎引導" + A + "{r_ch}秒" + E +
               "後傳送到他身邊（被控則中斷）。",
        "names": ("暮光強襲", "影襲", "並肩作戰"),
    },
    "en": {
        "name": "Shen",
        "attack": "Sword strike. " + O + "Ki Barrier" + E + ": every ability gives him a " + sh("p") + " shield for " + A + "{p_sh_t}s" + E +
                  " (once every " + A + "{p_cd}s" + E + ", sooner when abilities hit champions). Empowered attacks deal {q_a_dmg} more, "
                  "and to champions {q_a_hp}% of their max health ({q_a_hp_big}% and +{q_as}% attack speed if the blade passed one).",
        "skill": "Recalls his spirit blade from behind the target: " + phy("q") + " and " + R + "{q_slow}% slow" + E + " to enemies on its way; "
                 "his next {q_n} attacks are empowered. With an enemy champion near on its return, " + O + "Spirit's Refuge" + E + ": for " +
                 A + "{w_t}s" + E + " allied champions in the zone take no basic attack damage (" + A + "{w_cd}s" + E + " cooldown).",
        "skill2": "Dashes forward: " + phy("e") + " to enemies passed, " + R + "taunted {e_taunt}s" + E + ". Taunting a champion with "
                  "Twilight Assault ready also pulls the blade from where the dash began, through them.",
        "ult": "When an allied champion anywhere is crowd-controlled, or locked in a fight far from Shen: a " + sh("r") + " shield on "
               "it for " + A + "{r_sh_t}s" + E + "; Shen channels " + A + "{r_ch}s" + E + " and teleports to it (crowd control breaks it).",
        "names": ("Twilight Assault", "Shadow Dash", "Stand United"),
    },
    "ko": {
        "name": "쉔",
        "attack": O + "기 보호막" + E + ": 스킬 사용 시 " + sh("p") + " 보호막 " + A + "{p_sh_t}초" + E + "(" + A + "{p_cd}초" + E +
                  "마다, 스킬이 챔피언 적중 시 단축). 강화 기본 공격은 추가 {q_a_dmg} 피해, 챔피언에게 최대 체력 {q_a_hp}%(검이 챔피언을 관통했으면 {q_a_hp_big}%, 공격 속도 +{q_as}%).",
        "skill": "영혼의 검을 대상 뒤에서 회수해 지나는 적에게 " + phy("q") + " 피해와 " + R + "{q_slow}% 둔화" + E + ", 다음 기본 공격 {q_n}회 강화. 돌아올 때 "
                 "근처에 적 챔피언이 있으면 " + O + "의지의 결계" + E + ": " + A + "{w_t}초" + E + " 동안 범위 안 아군 챔피언은 기본 공격 피해를 받지 "
                 "않음(재사용 " + A + "{w_cd}초" + E + ").",
        "skill2": "앞으로 돌진해 지나간 적에게 " + phy("e") + " 피해, " + R + "{e_taunt}초 도발" + E + ". 챔피언을 도발했고 황혼 강습이 준비되어 "
                  "있으면 검이 돌진 시작점에서 날아와 그들을 관통.",
        "ult": "맵 어디서든 아군 챔피언이 군중 제어에 걸렸거나 쉔과 멀리서 교전 중이면: " + sh("r") + " 보호막 " + A + "{r_sh_t}초" + E +
               ", 쉔이 " + A + "{r_ch}초" + E + " 정신 집중 후 그 곁으로 순간이동(군중 제어 시 취소).",
        "names": ("황혼 강습", "그림자 돌진", "단결된 의지"),
    },
    "ja": {
        "name": "シェン",
        "attack": O + "内気功" + E + "：スキル使用後に" + sh("p") + "のシールド" + A + "{p_sh_t}秒" + E + "（" + A + "{p_cd}秒" + E +
                  "に1回、スキルがチャンピオンに当たると短縮）。強化通常攻撃は追加{q_a_dmg}ダメージ、チャンピオンには最大体力の{q_a_hp}%（刀が貫いたら{q_a_hp_big}%、攻撃速度+{q_as}%）。",
        "skill": "霊刃を対象の背後から呼び戻し、通過した敵に" + phy("q") + "と" + R + "{q_slow}%スロウ" + E + "、次の通常攻撃{q_n}回を強化。戻った時に敵チャンピオンが近くにいれば" +
                 O + "防人の帳" + E + "：" + A + "{w_t}秒" + E + "間、範囲内の味方チャンピオンは通常攻撃のダメージを受けない（" + A + "{w_cd}秒" + E + "毎）。",
        "skill2": "前方へ突進し、通過した敵に" + phy("e") + "と" + R + "{e_taunt}秒の挑発" + E + "。チャンピオンを挑発し護刃招来が使えるなら、霊刃が突進の起点から飛び戻り彼らを貫く。",
        "ult": "マップのどこかで味方チャンピオンが行動妨害を受けるか、シェンから遠くで交戦中なら：" + sh("r") + "のシールドを" + A + "{r_sh_t}秒" + E +
               "、シェンは" + A + "{r_ch}秒" + E + "詠唱後その傍へテレポート（行動妨害で中断）。",
        "names": ("護刃招来", "殺気駆け", "瞬身護法"),
    },
}

C = "league_shen_sfx_"
S = "league_shen_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S + k: [(C + k, vol, dl)] for k, vol, dl in [
    ("a_swing", 0.45, 0.0), ("a_hit", 0.35, 0.0), ("a_emp", 0.5, 0.0), ("q", 0.5, 0.0), ("q_hit", 0.4, 0.0),
    ("q_back", 0.45, 0.0), ("w", 0.55, 0.0), ("e", 0.5, 0.0), ("e_hit", 0.5, 0.0), ("p", 0.35, 0.0), ("r", 0.6, 0.0),
    ("r_ally", 0.5, 0.0), ("r_land", 0.6, 0.0), ("vo_q", 0.8, 0.0), ("vo_w", 0.8, 0.0), ("vo_e", 0.8, 0.0),
    ("vo_r", 0.9, 0.05)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_sh", "p_sh_ratio", "q_a_dmg", "q_a_hp", "q_a_hp_big", "q_as", "q_dmg", "q_ratio", "q_slow",
                           "q_n", "e_dmg", "e_ratio", "r_sh", "r_sh_ratio")}
    v.update({k: secs(p[k]) for k in ("p_sh_t", "p_cd", "w_t", "w_cd", "e_taunt", "r_sh_t", "r_ch")})
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
    if "Shen" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Shen. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
