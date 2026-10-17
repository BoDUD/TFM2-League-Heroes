"""Jayce's text (5 languages), sound_info files and his keys in the shared files, numbers from build_jayce.P.

    python tools/kit/setup_jayce.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_jayce in every language, description + skill_name),
sound/sfx/league_jayce_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.114.0, Jayce named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (杰斯 / 未来守护者 - the client swaps name and title; 海克斯科技电容, 苍穹之跃 /
电能震荡, 闪电领域 / 超能电荷, 雷霆一击 / 加速之门, 墨丘利之炮 / 墨丘利之锤) and Data Dragon 16.20.1 (zh_TW 杰西 / 海克斯電容器 /
浩瀚無垠／電磁脈衝 / 離子領域／超頻導體 / 風馳電掣／中子加速裝置 / 水星加農／水星戰鎚, ja ジェイス / ヘクステック・コンデンサー /
スカイバスター/ショックブラスト / ライトニング/ハイパーチャージ / サンダーブロー/アクセルゲート / マーキュリーキャノン/マーキュリーハンマー,
ko 제이스 / 마법공학 축전기 / 하늘로! / 전격 폭발 / 전류 역장 / 초전하 / 천둥 강타 / 가속 관문 / 머큐리 캐논 / 머큐리 해머).
Slots: skill = Q (both forms), skill2 = hammer E + W / cannon W, ult = the gate and its shot (E's name, 加速之门); the
passive and the form switch are told in the attack's text. No combo sentence in any text (the user's rule). No
`league_jayce_attack` sound: the engine would play it at the start of every attack; the swing and the shot play from the
tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_jayce import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_jayce"
VERSION = "0.114.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # physical damage, AD, names
M = "<#a974ffff>"      # magic damage / AP
A = "<#ffb900ff>"      # durations, counts
C = "<#ef5350ff>"      # crowd control
W = "<#ffffffff>"      # move speed
S = "<#ceff99ff>"      # attack speed
R = "<#ffdd8eff>"      # armour / magic resistance
T = "<#f5f5f5ff>"      # true damage
E = "<>"
# champion_view: the face as ppu_restyle.py sets it (RESTYLE face_to), the centre from the idle
VIEW = {"face": {"x": 0, "y": -38}, "center": {"x": 0, "y": -12}}


def phys(k):
    return f"{O}{{{k}_dmg}}{E}+{ADi}{O}{{{k}_ad}}%{E}"


def mag(k):
    return f"{M}{{{k}_dmg}}{E}+{APi}{M}{{{k}_ap}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "杰斯",
        "attack": O + "海克斯科技电容" + E + "：出手前按战况切换锤（近战）和炮（远程），间隔" + A + "{r_cd}秒" + E + "，每次" + W + "移速+{p_ms}%" + E +
                  "。变炮后下次攻击使目标" + R + "护甲和魔抗-{p_sh}%" + E + "（" + A + "{p_sh_t}秒" + E + "）；变锤获得" + R + "护甲和魔抗+{p_arm}%" + E + "（" + A + "{p_arm_t}秒" + E + "）。",
        "skill": "锤：跃向敌人，对周围造成" + phys("q") + O + "物理伤害" + E + "并" + C + "减速{q_slow}%" + E + "。" + O + "电能震荡" + E + "：发射电能球，命中首个敌人后爆炸，造成" +
                 phys("cq") + O + "物理伤害" + E + "。",
        "skill2": "锤：击退敌人，造成" + mag("e") + M + "魔法伤害" + E + "，对英雄另加" + T + "{e_hp}%最大生命值真实伤害" + E + "；冷却时" + O + "闪电领域" + E + "每" + A +
                  "{w_per}秒" + E + "造成" + mag("w") + M + "魔法伤害" + E + "。炮：之后3次攻击" + S + "攻速+{hc_as}%" + E + "，造成" + O + "{hc_ad}%" + E + "攻击力伤害。",
        "ult": "变为炮形态，放置加速之门（" + W + "移速+{g_ms}%" + E + "，" + A + "{g_t}秒" + E + "），向敌方英雄射出加速电能球，造成" + phys("r") + O + "物理伤害" + E +
               "，爆炸范围更大。",
        "names": ("苍穹之跃 / 电能震荡", "雷霆一击 / 超能电荷", "加速之门"),
    },
    "zh-hant": {
        "name": "杰西",
        "attack": O + "海克斯電容器" + E + "：出手前依戰況切換錘（近戰）和砲（遠程），間隔" + A + "{r_cd}秒" + E + "，每次" + W + "跑速+{p_ms}%" + E +
                  "。變砲後下次攻擊使目標" + R + "物防和魔防-{p_sh}%" + E + "（" + A + "{p_sh_t}秒" + E + "）；變錘獲得" + R + "物防和魔防+{p_arm}%" + E + "（" + A + "{p_arm_t}秒" + E + "）。",
        "skill": "錘：躍向敵人，對周圍造成" + phys("q") + O + "物理傷害" + E + "並" + C + "緩速{q_slow}%" + E + "。" + O + "電磁脈衝" + E + "：發射電能球，命中首個敵人後爆炸，造成" +
                 phys("cq") + O + "物理傷害" + E + "。",
        "skill2": "錘：擊退敵人，造成" + mag("e") + M + "魔法傷害" + E + "，對英雄另加" + T + "{e_hp}%最大生命真實傷害" + E + "；冷卻時" + O + "離子領域" + E + "每" + A +
                  "{w_per}秒" + E + "造成" + mag("w") + M + "魔法傷害" + E + "。砲：之後3次攻擊" + S + "攻速+{hc_as}%" + E + "，造成" + O + "{hc_ad}%" + E + "攻擊力傷害。",
        "ult": "變為砲形態，放置中子加速裝置（" + W + "跑速+{g_ms}%" + E + "，" + A + "{g_t}秒" + E + "），向敵方英雄射出加速電能球，造成" + phys("r") + O + "物理傷害" + E +
               "，爆炸範圍更大。",
        "names": ("浩瀚無垠／電磁脈衝", "風馳電掣／超頻導體", "中子加速裝置"),
    },
    "en": {
        "name": "Jayce",
        "attack": O + "Hextech Capacitor" + E + ": before an attack he switches between hammer (melee) and cannon (ranged) as the fight needs, every " + A +
                  "{r_cd}s" + E + " at most, gaining " + W + "{p_ms}% move speed" + E + ". After turning cannon his next attack cuts the target's " + R +
                  "armour and magic resist by {p_sh}%" + E + " for " + A + "{p_sh_t}s" + E + "; turning hammer gives him " + R + "+{p_arm}% armour and magic resist" + E +
                  " for " + A + "{p_arm_t}s" + E + ".",
        "skill": "Hammer: leaps at an enemy, dealing " + phys("q") + " " + O + "physical damage" + E + " around him and " + C + "slowing by {q_slow}%" + E + ". " + O +
                 "Shock Blast" + E + ": fires an orb that bursts on the first enemy hit for " + phys("cq") + " " + O + "physical damage" + E + " around it.",
        "skill2": "Hammer: knocks an enemy back for " + mag("e") + " " + M + "magic damage" + E + ", plus " + T + "{e_hp}% of a champion's max health as true damage" + E +
                  "; on cooldown " + O + "Lightning Field" + E + " deals " + mag("w") + " " + M + "magic damage" + E + " around him every " + A + "{w_per}s" + E + ". Cannon: " + O +
                  "Hyper Charge" + E + " - his next 3 attacks gain " + S + "{hc_as}% attack speed" + E + " and deal " + O + "{hc_ad}%" + E + " AD.",
        "ult": "Turns into the cannon, places the Acceleration Gate (" + W + "{g_ms}% move speed" + E + " for " + A + "{g_t}s" + E + ") and fires an accelerated orb at a "
               "champion: faster and farther, " + phys("r") + " " + O + "physical damage" + E + " in a larger burst.",
        "names": ("To the Skies! / Shock Blast", "Thundering Blow / Hyper Charge", "Acceleration Gate"),
    },
    "ko": {
        "name": "제이스",
        "attack": O + "마법공학 축전기" + E + ": 공격 전에 상황에 따라 해머(근접)와 캐논(원거리)을 바꾸며, 전환 대기시간 " + A + "{r_cd}초" + E + ", 전환 시 " + W +
                  "이동 속도 +{p_ms}%" + E + ". 캐논 전환 후 다음 공격은 " + A + "{p_sh_t}초" + E + " 동안 대상의 " + R + "방어력과 마법 저항력 -{p_sh}%" + E +
                  ", 해머 전환 시 " + A + "{p_arm_t}초" + E + " 동안 " + R + "방어력과 마법 저항력 +{p_arm}%" + E + ".",
        "skill": "해머: 적에게 도약해 주변에 " + phys("q") + " " + O + "물리 피해" + E + "와 " + C + "{q_slow}% 둔화" + E + ". " + O + "전격 폭발" + E +
                 ": 구체를 발사해 처음 맞힌 적 주변에 " + phys("cq") + " " + O + "물리 피해" + E + ".",
        "skill2": "해머: 적을 밀쳐내며 " + mag("e") + " " + M + "마법 피해" + E + ", 챔피언에게 " + T + "최대 체력 {e_hp}% 고정 피해" + E + " 추가; 대기 중이면 " + O +
                  "전류 역장" + E + "이 " + A + "{w_per}초" + E + "마다 " + mag("w") + " " + M + "마법 피해" + E + ". 캐논: 다음 공격 3회 " + S + "공격 속도 +{hc_as}%" + E +
                  ", 공격력의 " + O + "{hc_ad}%" + E + " 피해.",
        "ult": "캐논으로 변해 가속 관문을 설치하고(" + W + "이동 속도 +{g_ms}%" + E + " " + A + "{g_t}초" + E + ") 챔피언에게 가속된 구체를 발사해 " + phys("r") + " " + O +
               "물리 피해" + E + ", 폭발 범위 증가.",
        "names": ("하늘로! / 전격 폭발", "천둥 강타 / 초전하", "가속 관문"),
    },
    "ja": {
        "name": "ジェイス",
        "attack": O + "ヘクステック・コンデンサー" + E + "：攻撃の前に戦況でハンマー（近接）とキャノン（遠隔）を切り替え、間隔" + A + "{r_cd}秒" + E + "、" + W +
                  "移動速度+{p_ms}%" + E + "。キャノン後の次の攻撃は対象の" + R + "物理防御と魔法防御-{p_sh}%" + E + "（" + A + "{p_sh_t}秒" + E + "）、ハンマーで" + R +
                  "物理防御と魔法防御+{p_arm}%" + E + "（" + A + "{p_arm_t}秒" + E + "）。",
        "skill": "ハンマー：敵へ跳び、周囲に" + phys("q") + "の" + O + "物理ダメージ" + E + "と" + C + "{q_slow}%スロウ" + E + "。" + O + "ショックブラスト" + E +
                 "：最初の敵で爆発する球を放ち" + phys("cq") + "の" + O + "物理ダメージ" + E + "。",
        "skill2": "ハンマー：敵をノックバックし" + mag("e") + "の" + M + "魔法ダメージ" + E + "、チャンピオンに" + T + "最大体力{e_hp}%の確定ダメージ" + E + "；CD中は" + O +
                  "ライトニング" + E + "が" + A + "{w_per}秒" + E + "ごとに" + mag("w") + "の" + M + "魔法ダメージ" + E + "。キャノン：次の3回の攻撃は" + S + "攻撃速度+{hc_as}%" + E +
                  "、攻撃力の" + O + "{hc_ad}%" + E + "。",
        "ult": "キャノンに変形しアクセルゲートを設置（" + W + "移動速度+{g_ms}%" + E + "、" + A + "{g_t}秒" + E + "）、チャンピオンへ加速した球を放ち" + phys("r") + "の" + O +
               "物理ダメージ" + E + "、爆発範囲拡大。",
        "names": ("スカイバスター/ショックブラスト", "サンダーブロー/ハイパーチャージ", "アクセルゲート"),
    },
}

S_ = "league_jayce_"
CL = "league_jayce_sfx_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(CL + k, vol, 0.0)] for k, vol in [
    ("a_swing", 0.4), ("a_hit", 0.45), ("c_shot", 0.4), ("c_hit", 0.4), ("h_shot", 0.45), ("shred", 0.45),
    ("q_leap", 0.5), ("q_land", 0.6), ("q_hit", 0.35), ("cq", 0.5), ("cq_boom", 0.55), ("cq_hit", 0.35), ("gate", 0.55),
    ("gq", 0.55), ("gq_boom", 0.6), ("e_cast", 0.45), ("e_blow", 0.55), ("w_field", 0.5), ("hyper", 0.5),
    ("tf_c", 0.5), ("tf_h", 0.5),
    ("vo_q", 0.8), ("vo_cq", 0.75), ("vo_e", 0.8), ("vo_tf_c", 0.8), ("vo_tf_h", 0.8), ("vo_r", 0.85)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("p_ms", "p_sh", "p_arm", "q_dmg", "q_ad", "q_slow", "cq_dmg", "cq_ad", "e_dmg", "e_ap", "e_hp",
                           "w_dmg", "w_ap", "hc_as", "hc_ad", "g_ms")}
    v.update({k: secs(p[k]) for k in ("p_sh_t", "p_arm_t", "w_per", "g_t")})
    v["r_cd"] = secs(p["r_cd_t"])
    v["r_dmg"] = p["cq_dmg"] * p["r_amp"] // 100
    v["r_ad"] = p["cq_ad"] * p["r_amp"] // 100
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
    if "Jayce" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Jayce. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
