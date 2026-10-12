"""Kassadin's text (5 languages), sound_info files and his keys in the shared files, numbers from build_kassadin.P.

    python tools/kit/setup_kassadin.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_kassadin in every language, description + skill_name),
sound/sfx/league_kassadin_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.101.0, Kassadin named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (卡萨丁 / 虚空行者; 虚空之石, 虚无法球, 虚空之刃, 能量脉冲, 虚空行走; the client swaps
name and title) and Data Dragon 16.20.1 (zh_TW 卡薩丁 / 虛空之石 / 虛無法球 / 虛空之刃 / 能量脈衝 / 虛空行走, ja カサディン /
ヴォイドストーン / ヴォイドスフィア / ネザーブレード / ヴォイドパルス / リフトウォーク, ko 카사딘 / 공허석 / 무의 구체 / 황천의 검 /
힘의 파동 / 균열 이동). Slots: skill = Q, skill2 = E, ult = R; the passive and Nether Blade (W) are told in the attack's
text. No combo sentence in any text (the user's rule). No `league_kassadin_attack` sound: the engine would play it at
the start of every attack; the swipe plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_kassadin import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_kassadin"
VERSION = "0.101.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#7dd87dff>"      # heals
E = "<>"
# champion_view: set from the imported sprite (tfm2_ase.py face; banpick_center when the idle tops -28)
VIEW = {"face": {"x": 2, "y": -18}, "center": {"x": 0, "y": -12}}


def mag(k):
    return f"{M}{{{k}_dmg}}{E} + {APi}{M}{{{k}_ratio}}%{E}"


ONHIT = M + "{a_p}" + E + " + " + APi + M + "{a_p_ratio}%" + E
STACK = M + "{r_st}" + E + " + " + APi + M + "{r_st_ratio}%" + E
SHIELD = "{q_sh} + " + APi + "{q_sh_ap}%"

TEXT = {
    "zh-hans": {
        "name": "卡萨丁",
        "attack": O + "虚空之石" + E + "：受到的魔法伤害降低约10%。" + O + "虚空之刃" + E + "：普攻附带" + ONHIT + M + "魔法伤害" + E + "；每" +
                  A + "{w_cd}秒" + E + "强化一次普攻，额外造成" + mag("w") + M + "魔法伤害" + E + "。",
        "skill": "向目标发射虚无法球，造成" + mag("q") + M + "魔法伤害" + E + "，打断英雄的动作。自身获得" + SHIELD + "护盾" + A + "{q_sh_t}秒" + E + "。",
        "skill2": "向前方锥形释放能量脉冲，造成" + mag("e") + M + "魔法伤害" + E + "并" + R + "减速{e_slow}%" + E + A + "{e_slow_t}秒" + E +
                  "。每次施放虚无法球或虚空行走都会缩短它的冷却。",
        "ult": "闪现到附近一名敌方英雄身边，对周围敌人造成" + mag("r") + M + "魔法伤害" + E + "。" + A + "{r_stack_t}秒" + E + "内再次施放叠加一层" +
               "（最多" + A + "3层" + E + "），每层额外" + STACK + M + "魔法伤害" + E + "。",
        "names": ("虚无法球", "能量脉冲", "虚空行走"),
    },
    "zh-hant": {
        "name": "卡薩丁",
        "attack": O + "虛空之石" + E + "：受到的魔法傷害降低約10%。" + O + "虛空之刃" + E + "：普攻附帶" + ONHIT + M + "魔法傷害" + E + "；每" +
                  A + "{w_cd}秒" + E + "強化一次普攻，額外造成" + mag("w") + M + "魔法傷害" + E + "。",
        "skill": "向目標發射虛無法球，造成" + mag("q") + M + "魔法傷害" + E + "，打斷英雄的動作。自身獲得" + SHIELD + "護盾" + A + "{q_sh_t}秒" + E + "。",
        "skill2": "向前方錐形釋放能量脈衝，造成" + mag("e") + M + "魔法傷害" + E + "並" + R + "緩速{e_slow}%" + E + A + "{e_slow_t}秒" + E +
                  "。每次施放虛無法球或虛空行走都會縮短它的冷卻。",
        "ult": "閃現到附近一名敵方英雄身邊，對周圍敵人造成" + mag("r") + M + "魔法傷害" + E + "。" + A + "{r_stack_t}秒" + E + "內再次施放疊加一層" +
               "（最多" + A + "3層" + E + "），每層額外" + STACK + M + "魔法傷害" + E + "。",
        "names": ("虛無法球", "能量脈衝", "虛空行走"),
    },
    "en": {
        "name": "Kassadin",
        "attack": O + "Void Stone" + E + ": takes about 10% less magic damage. " + O + "Nether Blade" + E + ": attacks deal " + ONHIT + " " + M +
                  "magic damage" + E + "; every " + A + "{w_cd}s" + E + " one attack deals " + mag("w") + " " + M + "magic damage" + E + " more.",
        "skill": "Fires an orb at the target: " + mag("q") + " " + M + "magic damage" + E + ", interrupting a champion. He gains a " + SHIELD + " shield for " + A + "{q_sh_t}s" + E + ".",
        "skill2": "Releases a pulse in a cone ahead: " + mag("e") + " " + M + "magic damage" + E + " and a " + R + "{e_slow}% slow" + E + " for " + A +
                  "{e_slow_t}s" + E + ". Each Null Sphere or Riftwalk he casts shortens its cooldown.",
        "ult": "Blinks next to a nearby enemy champion: " + mag("r") + " " + M + "magic damage" + E + " round him. Cast again within " + A +
               "{r_stack_t}s" + E + " for a stack (at most " + A + "3" + E + "), each adding " + STACK + " " + M + "magic damage" + E + ".",
        "names": ("Null Sphere", "Force Pulse", "Riftwalk"),
    },
    "ko": {
        "name": "카사딘",
        "attack": O + "공허석" + E + ": 받는 마법 피해 약 10% 감소. " + O + "황천의 검" + E + ": 기본 공격에 " + ONHIT + " " + M + "마법 피해" + E +
                  " 추가, " + A + "{w_cd}초" + E + "마다 기본 공격 하나가 " + mag("w") + " " + M + "마법 피해" + E + " 추가.",
        "skill": "대상에게 구체를 발사해 " + mag("q") + " " + M + "마법 피해" + E + ", 챔피언의 동작을 끊음. 자신은 " + A + "{q_sh_t}초" + E + " 동안 " + SHIELD + " 보호막.",
        "skill2": "전방 원뿔로 파동을 방출해 " + mag("e") + " " + M + "마법 피해" + E + "와 " + A + "{e_slow_t}초" + E + " " + R + "{e_slow}% 둔화" + E +
                  ". 무의 구체나 균열 이동을 쓸 때마다 재사용 대기시간 감소.",
        "ult": "근처 적 챔피언 옆으로 순간이동해 주변 적에게 " + mag("r") + " " + M + "마법 피해" + E + ". " + A + "{r_stack_t}초" + E + " 안에 다시 쓰면 "
               "중첩 (최대 " + A + "3" + E + "), 중첩마다 " + STACK + " " + M + "마법 피해" + E + " 추가.",
        "names": ("무의 구체", "힘의 파동", "균열 이동"),
    },
    "ja": {
        "name": "カサディン",
        "attack": O + "ヴォイドストーン" + E + "：受ける魔法ダメージ約10%軽減。" + O + "ネザーブレード" + E + "：通常攻撃に" + ONHIT + "の" + M + "魔法ダメージ" +
                  E + "、" + A + "{w_cd}秒" + E + "ごとに1回" + mag("w") + "の" + M + "魔法ダメージ" + E + "追加。",
        "skill": "対象に球を放ち" + mag("q") + "の" + M + "魔法ダメージ" + E + "、チャンピオンの動作を中断。自身に" + A + "{q_sh_t}秒" + E + SHIELD + "のシールド。",
        "skill2": "前方の扇形に波動を放ち" + mag("e") + "の" + M + "魔法ダメージ" + E + "と" + A + "{e_slow_t}秒" + E + R + "{e_slow}%スロウ" + E +
                  "。ヴォイドスフィアかリフトウォークを使うたびCD短縮。",
        "ult": "近くの敵チャンピオンの傍へ瞬間移動し、周囲の敵に" + mag("r") + "の" + M + "魔法ダメージ" + E + "。" + A + "{r_stack_t}秒" + E +
               "以内の再使用でスタック（最大" + A + "3" + E + "）、1つごとに" + STACK + "の" + M + "魔法ダメージ" + E + "追加。",
        "names": ("ヴォイドスフィア", "ヴォイドパルス", "リフトウォーク"),
    },
}

C = "league_kassadin_sfx_"
S_ = "league_kassadin_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S_ + k: [(C + c, vol, dl)] for k, c, vol, dl in [
    ("a_swing", "a_swing", 0.45, 0.0), ("a_hit", "a_hit", 0.4, 0.0), ("q", "q", 0.55, 0.0), ("q_hit", "q_hit", 0.55, 0.0),
    ("w", "w", 0.5, 0.0), ("w_hit", "w_hit", 0.6, 0.0), ("e", "e", 0.6, 0.0), ("e_hit", "e_hit", 0.5, 0.0),
    ("r", "r", 0.6, 0.0), ("r_hit", "r_hit", 0.6, 0.0),
    ("vo_q", "vo_q", 0.8, 0.0), ("vo_w", "vo_w", 0.8, 0.0), ("vo_e", "vo_e", 0.8, 0.0), ("vo_r", "vo_r", 0.85, 0.0)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("a_p", "a_p_ratio", "w_dmg", "w_ratio", "q_dmg", "q_ratio", "q_sh", "q_sh_ap", "e_dmg",
                           "e_ratio", "e_slow", "r_dmg", "r_ratio", "r_st", "r_st_ratio")}
    v.update({k: secs(p[k]) for k in ("w_cd", "q_sil", "q_sh_t", "e_slow_t", "r_stack_t")})
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
    if "Kassadin" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Kassadin. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
