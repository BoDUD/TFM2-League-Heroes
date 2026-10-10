"""Viego's text (5 languages), sound_info files and his keys in the shared files, numbers from build_viego.P.

    python tools/kit/setup_viego.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_viego in every language, description + skill_name),
sound/sfx/league_viego_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.92.0, Viego named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: zh_CN from the client's string table (佛耶戈 / 君命已决 / 破败王剑 / 千载幽咽 / 茫茫焦土 / 痛贯天灵; the client
swaps name and title: 破败之王 is the title), Data Dragon 16.20.1 (zh_TW 維爾戈 / 王權統御 / 殞落王者之劍 / 冥魂之噬 /
幽影之徑 / 破心者, ja ヴィエゴ / 王の支配 / 滅びの王剣 / 亡霊の嘆き / 彷徨える苦悶 / ハートブレイカー, ko 비에고 / 군주의
지배 / 몰락한 왕의 검 / 망령의 나락 / 안개의 길 / 심장 파괴자). The slot names: skill = Q, skill2 = W (E's mist is told in
its text), ult = R; the passive is told in the attack's text. No combo sentence in any text (the user's rule).
No `league_viego_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_viego import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_viego"
VERSION = "0.92.0"
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


def hl(k):
    return f"{A}{{{k}_heal}}{E} + {ADi}{A}{{{k}_heal_ratio}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "佛耶戈",
        "attack": O + "君命已决" + E + "：他伤过的敌方英雄{p_win}秒内阵亡则附身其灵魂" + A + "{p_t}秒" + E + "：" + R + "{p_inv}秒无敌" + E + "，回复" + hl("p") +
                  "，攻击+{p_ad}%、攻速+{p_as}%、移速+{p_ms}%，Q、W刷新。普攻附加英雄最大生命{a_pct}%。",
        "skill": "向前刺出，造成" + phy("q") + "伤害。刺中的英雄被标记" + A + "{q_mark}秒" + E + "，下次普攻对其斩两下：再造成" + phy("d") + "伤害并回复" + hl("d") + "。",
        "skill2": O + "茫茫焦土" + E + "：黑雾升起，" + A + "{e_t}秒" + E + "内移速+{e_ms}%、攻速+{e_as}%，蓄力时隐身。随后冲刺并吐出亡魂，第一个被击中的敌人受到" +
                  phy("w") + "伤害并" + R + "眩晕{w_stun}秒" + E + "。",
        "ult": "跃向队伍正在交手的敌方英雄并" + R + "减速{r_slow}%" + E + "，落地刺穿它，造成" + phy("r") + "+其最大生命{r_hp}%伤害，击退周围其他敌人。结束附身。",
        "names": ("破败王剑", "千载幽咽", "痛贯天灵"),
    },
    "zh-hant": {
        "name": "維爾戈",
        "attack": O + "王權統御" + E + "：他傷過的敵方英雄{p_win}秒內陣亡則附身其靈魂" + A + "{p_t}秒" + E + "：" + R + "{p_inv}秒無敵" + E + "，回復" + hl("p") +
                  "，攻擊+{p_ad}%、攻速+{p_as}%、移速+{p_ms}%，Q、W刷新。普攻附加英雄最大生命{a_pct}%。",
        "skill": "向前刺出，造成" + phy("q") + "傷害。刺中的英雄被標記" + A + "{q_mark}秒" + E + "，下次普攻對其斬兩下：再造成" + phy("d") + "傷害並回復" + hl("d") + "。",
        "skill2": O + "幽影之徑" + E + "：黑霧升起，" + A + "{e_t}秒" + E + "內移速+{e_ms}%、攻速+{e_as}%，蓄力時隱身。隨後衝刺並吐出亡魂，第一個被擊中的敵人受到" +
                  phy("w") + "傷害並" + R + "暈眩{w_stun}秒" + E + "。",
        "ult": "躍向隊伍正在交手的敵方英雄並" + R + "緩速{r_slow}%" + E + "，落地刺穿它，造成" + phy("r") + "+其最大生命{r_hp}%傷害，擊退周圍其他敵人。結束附身。",
        "names": ("殞落王者之劍", "冥魂之噬", "破心者"),
    },
    "en": {
        "name": "Viego",
        "attack": O + "Sovereign's Domination" + E + ": an enemy champion he damaged dies within {p_win}s - he possesses its soul for " + A + "{p_t}s" + E +
                  ": " + R + "untouchable {p_inv}s" + E + ", heals " + hl("p") + ", +{p_ad}% attack, +{p_as}% attack speed, +{p_ms}% move speed, "
                  "Q and W refreshed. Attacks deal {a_pct}% of a champion's max health.",
        "skill": "Thrusts forward: " + phy("q") + ". A champion hit is marked for " + A + "{q_mark}s" + E + ": his next attack on it strikes twice, "
                 + phy("d") + " more, and heals " + hl("d") + ".",
        "skill2": O + "Harrowed Path" + E + ": mist rises - " + A + "{e_t}s" + E + " of +{e_ms}% move speed and +{e_as}% attack speed, hidden while "
                  "charging. Then he dashes and looses a wraith: the first enemy hit takes " + phy("w") + " and is " + R + "stunned {w_stun}s" + E + ".",
        "ult": "Leaps at an enemy champion his team is fighting, " + R + "slowing it {r_slow}%" + E + ", and pierces it on landing: " + phy("r") +
               " + {r_hp}% of its max health; other enemies near are knocked back. Ends a possession.",
        "names": ("Blade of the Ruined King", "Spectral Maw", "Heartbreaker"),
    },
    "ko": {
        "name": "비에고",
        "attack": O + "군주의 지배" + E + ": 피해를 입힌 적 챔피언이 {p_win}초 안에 죽으면 영혼에 빙의 " + A + "{p_t}초" + E + ": " + R + "{p_inv}초 무적" + E +
                  ", " + hl("p") + " 회복, 공격력 +{p_ad}%, 공격 속도 +{p_as}%, 이동 속도 +{p_ms}%, Q·W 초기화. 기본 공격은 챔피언 최대 체력 {a_pct}% 추가.",
        "skill": "앞으로 찔러 " + phy("q") + " 피해. 맞은 챔피언은 " + A + "{q_mark}초" + E + " 표식: 다음 기본 공격이 두 번 베어 " + phy("d") + " 추가 피해, " + hl("d") + " 회복.",
        "skill2": O + "안개의 길" + E + ": 안개가 일어 " + A + "{e_t}초" + E + " 동안 이동 속도 +{e_ms}%, 공격 속도 +{e_as}%, 충전 중 은신. 이어서 돌진하며 망령을 "
                  "날려 처음 맞은 적에게 " + phy("w") + " 피해와 " + R + "{w_stun}초 기절" + E + ".",
        "ult": "아군이 교전 중인 적 챔피언에게 도약해 " + R + "{r_slow}% 둔화" + E + ", 착지하며 꿰뚫어 " + phy("r") + " + 최대 체력 {r_hp}% 피해, 주변의 다른 적은 "
               "밀쳐냄. 빙의 종료.",
        "names": ("몰락한 왕의 검", "망령의 나락", "심장 파괴자"),
    },
    "ja": {
        "name": "ヴィエゴ",
        "attack": O + "王の支配" + E + "：ダメージを与えた敵チャンピオンが{p_win}秒以内に倒れると魂に憑依" + A + "{p_t}秒" + E + "：" + R + "{p_inv}秒無敵" + E +
                  "、" + hl("p") + "回復、攻撃力+{p_ad}%・攻撃速度+{p_as}%・移動速度+{p_ms}%、QとWが再使用可能。通常攻撃はチャンピオンに最大体力の{a_pct}%を追加。",
        "skill": "前方へ突き、" + phy("q") + "のダメージ。当たったチャンピオンに" + A + "{q_mark}秒" + E + "の刻印：次の通常攻撃が2回斬り、" + phy("d") + "の追加ダメージと" + hl("d") + "回復。",
        "skill2": O + "彷徨える苦悶" + E + "：霧が立ちのぼり" + A + "{e_t}秒" + E + "移動速度+{e_ms}%・攻撃速度+{e_as}%、溜め中は透明。続けて突進し亡霊を放ち、"
                  "最初に当たった敵に" + phy("w") + "のダメージと" + R + "{w_stun}秒スタン" + E + "。",
        "ult": "味方が交戦中の敵チャンピオンへ跳び" + R + "{r_slow}%スロウ" + E + "、着地で貫き" + phy("r") + "+最大体力の{r_hp}%のダメージ、周囲の他の敵はノックバック。憑依を終える。",
        "names": ("滅びの王剣", "亡霊の嘆き", "ハートブレイカー"),
    },
}

C = "league_viego_sfx_"
S = "league_viego_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not found)
SOUNDS = {S + k: [(C + k, vol, dl)] for k, vol, dl in [
    ("a_swing", 0.45, 0.0), ("a_hit", 0.35, 0.0), ("a_double", 0.5, 0.0), ("q", 0.5, 0.0), ("q_hit", 0.4, 0.0),
    ("w_charge", 0.4, 0.0), ("w", 0.55, 0.0), ("w_hit", 0.5, 0.0), ("e", 0.5, 0.0), ("e_mist", 0.4, 0.0),
    ("p", 0.55, 0.0), ("p_hit", 0.45, 0.1), ("p_end", 0.45, 0.0), ("r", 0.6, 0.0), ("r_land", 0.6, 0.0),
    ("r_hit", 0.6, 0.0), ("vo_q", 0.8, 0.0), ("vo_w", 0.8, 0.0), ("vo_e", 0.8, 0.0), ("vo_r", 0.9, 0.05),
    ("vo_p", 0.9, 0.1)]}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("a_pct", "d_dmg", "d_ratio", "d_heal", "d_heal_ratio", "q_dmg", "q_ratio", "e_ms", "e_as",
                           "w_dmg", "w_ratio", "r_slow", "r_dmg", "r_ratio", "r_hp", "p_heal", "p_heal_ratio", "p_ad",
                           "p_as", "p_ms")}
    v.update({k: secs(p[k]) for k in ("q_mark", "e_t", "w_stun", "p_win", "p_t", "p_inv")})
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
    if "Viego" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Viego. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
