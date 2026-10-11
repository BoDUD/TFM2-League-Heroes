"""Zeri's text (5 languages), sound_info files and her keys in the shared files, numbers from build_zeri.P.

    python tools/kit/setup_zeri.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_zeri in every language, description + skill_name),
sound/sfx/league_zeri_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (VERSION, Zeri named). Only her keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (泽丽 / 祖安花火 - the name and title slots are swapped there, as for Viktor;
内能迁转, 电火迸射, 强穿激光, 灿丽花火, 超限爆闪) and Data Dragon 16.20.1 (zh_TW 婕莉 / 佐恩電光, 人體蓄電池, 激電連彈,
超激爆電磁炮, 電光石火, 雷霆萬鈞; ko 제리 / 자운의 불꽃, 살아있는 배터리, 집중 사격, 초강력 레이저, 스파크 돌진, 번개 방출; ja ゼリ /
ゾウンの火花, 生体バッテリー, バーストファイア, ウルトラショックレーザー, スパークサージ, ライトニングクラッシュ). Q (Burst Fire) is her
attack and the passive shares its text; skill = W, skill2 = E, ult = R. No combo line in the texts (the pros' E -> W,
R -> E and W -> charged shot live in the kit and the README).
No `league_zeri_attack` sound: the engine would play it at the start of every attack; the shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_zeri import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_zeri"
VERSION = "0.93.0"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage / AP
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
Wh = "<#ffffffff>"     # true damage
E = "<>"
# champion_view: set from tfm2_ase.py face once the sprite is in
VIEW = {"face": {"x": 2, "y": -38}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": 0}}
# face: tfm2_ase.py face on the final sprite (crown 38 px above the feet); banpick_center: her idle tops at -40
# (bun tips, the rifle's electrodes), so by the card rule y = -39 - top would be +1 - 0 (as league_kayle) keeps
# the card from scaling and clips nothing


def mag(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "泽丽",
        "attack": "普攻" + O + "电火迸射" + E + "：7发连射打第一个敌人。被动" + O + "内能迁转" + E + "：每" + A + "{p_need}" + E +
                  "次攻击充满电，下一击为电击弹，额外造成" + mag("p_dmg", "p_ap") + M + "魔法伤害" + E + "并" + R + "减速" + E +
                  "，命中英雄再造成" + Wh + "{p_hp}%最大生命真实伤害" + E + "，自己获得护盾和移速。",
        "skill": "发射电脉冲，对第一个敌人造成" + phy("w_dmg", "w_ratio") + O + "物理伤害" + E + "并" + R + "减速{w_slow}%" + E +
                 "。先打中小兵或野怪时，从那里化为长激光，伤害并减速身后所有敌人。",
        "skill2": "短距冲刺（被贴身时后撤），之后" + A + "{e_t}秒" + E + "普攻贯穿：后面的敌人受到{e_pierce}%伤害，并额外造成" +
                  mag("e_dmg", "e_ap") + M + "魔法伤害" + E + "。命中英雄缩短冷却。",
        "ult": "电新星对周围敌人造成" + mag("r_dmg", "r_ap") + M + "魔法伤害" + E + "，超载" + A + "{r_t}秒" + E +
               "：攻速+{r_as}%、移速+{r_ms}%，命中英雄叠加移速并延长；普攻变为三连发，在敌人间连锁闪电。",
        "names": ("强穿激光", "灿丽花火", "超限爆闪"),
    },
    "zh-hant": {
        "name": "婕莉",
        "attack": "普攻" + O + "激電連彈" + E + "：7發連射打第一個敵人。被動" + O + "人體蓄電池" + E + "：每" + A + "{p_need}" + E +
                  "次攻擊充滿電，下一擊為電擊彈，額外造成" + mag("p_dmg", "p_ap") + M + "魔法傷害" + E + "並" + R + "緩速" + E +
                  "，命中英雄再造成" + Wh + "{p_hp}%最大生命真實傷害" + E + "，自己獲得護盾和移速。",
        "skill": "發射電脈衝，對第一個敵人造成" + phy("w_dmg", "w_ratio") + O + "物理傷害" + E + "並" + R + "緩速{w_slow}%" + E +
                 "。先打中小兵或野怪時，從那裡化為長雷射，傷害並緩速身後所有敵人。",
        "skill2": "短距衝刺（被貼身時後撤），之後" + A + "{e_t}秒" + E + "普攻貫穿：後面的敵人受到{e_pierce}%傷害，並額外造成" +
                  mag("e_dmg", "e_ap") + M + "魔法傷害" + E + "。命中英雄縮短冷卻。",
        "ult": "電新星對周圍敵人造成" + mag("r_dmg", "r_ap") + M + "魔法傷害" + E + "，超載" + A + "{r_t}秒" + E +
               "：攻速+{r_as}%、移速+{r_ms}%，命中英雄疊加移速並延長；普攻變為三連發，在敵人間連鎖閃電。",
        "names": ("超激爆電磁炮", "電光石火", "雷霆萬鈞"),
    },
    "en": {
        "name": "Zeri",
        "attack": "Attacks are " + O + "Burst Fire" + E + ": seven rounds at the first enemy hit. Passive " + O + "Living Battery" + E +
                  ": every " + A + "{p_need}" + E + " attacks charge her pack; the next is a charged shot dealing " +
                  mag("p_dmg", "p_ap") + " " + M + "magic damage" + E + " more and " + R + "slowing" + E + "; on a champion also " +
                  Wh + "{p_hp}% max health true damage" + E + ", and she gains a shield and Move Speed.",
        "skill": "Fires an electric pulse dealing " + phy("w_dmg", "w_ratio") + " " + O + "physical damage" + E + " to the first enemy hit, " +
                 R + "slowing {w_slow}%" + E + ". If a minion or monster stops it, it bursts into a long laser that hits and slows "
                 "every enemy behind.",
        "skill2": "Dashes a short way (back when an enemy is close), then for " + A + "{e_t}s" + E + " Burst Fire pierces: enemies after "
                  "the first take {e_pierce}% damage and " + mag("e_dmg", "e_ap") + " " + M + "magic damage" + E + ". Champion hits "
                  "lower the cooldowns.",
        "ult": "A nova deals " + mag("r_dmg", "r_ap") + " " + M + "magic damage" + E + " around her and overcharges her for " + A +
               "{r_t}s" + E + ": +{r_as}% Attack Speed, +{r_ms}% Move Speed that stacks and lasts longer with champion hits; Burst Fire "
               "becomes a triple shot that chains lightning between enemies.",
        "names": ("Ultrashock Laser", "Spark Surge", "Lightning Crash"),
    },
    "ko": {
        "name": "제리",
        "attack": "기본 공격 " + O + "집중 사격" + E + ": 처음 맞는 적에게 7연발. 기본 지속 효과 " + O + "살아있는 배터리" + E + ": 공격 " +
                  A + "{p_need}" + E + "번에 충전, 다음 공격은 충전탄으로 " + mag("p_dmg", "p_ap") + "의 " + M + "마법 피해" + E + "와 " +
                  R + "둔화" + E + ", 챔피언에게 " + Wh + "최대 체력 {p_hp}% 고정 피해" + E + ", 자신은 보호막과 이동 속도.",
        "skill": "전기 펄스로 처음 맞는 적에게 " + phy("w_dmg", "w_ratio") + "의 " + O + "물리 피해" + E + ", " + R + "{w_slow}% 둔화" + E +
                 ". 미니언이나 몬스터에 막히면 그 자리에서 긴 레이저가 되어 뒤의 모든 적을 맞히고 둔화.",
        "skill2": "짧게 돌진(적이 붙으면 뒤로), 이후 " + A + "{e_t}초" + E + " 동안 집중 사격 관통: 뒤의 적은 {e_pierce}% 피해와 " +
                  mag("e_dmg", "e_ap") + "의 " + M + "마법 피해" + E + ". 챔피언 적중 시 재사용 대기시간 감소.",
        "ult": "주변 적에게 " + mag("r_dmg", "r_ap") + "의 " + M + "마법 피해" + E + ", " + A + "{r_t}초" + E + " 과충전: 공격 속도 +{r_as}%, "
               "이동 속도 +{r_ms}%(챔피언 적중 시 중첩·연장), 집중 사격이 적 사이를 잇는 번개 3연발로.",
        "names": ("초강력 레이저", "스파크 돌진", "번개 방출"),
    },
    "ja": {
        "name": "ゼリ",
        "attack": "通常攻撃は" + O + "バーストファイア" + E + "：最初の敵に7連射。パッシブ" + O + "生体バッテリー" + E + "：" + A +
                  "{p_need}" + E + "回の攻撃で充電、次の攻撃はチャージ弾で" + mag("p_dmg", "p_ap") + "の" + M + "魔法ダメージ" + E + "と" +
                  R + "スロウ" + E + "、チャンピオンには" + Wh + "最大体力{p_hp}%の確定ダメージ" + E + "、自身にシールドと移動速度。",
        "skill": "電気パルスが最初の敵に" + phy("w_dmg", "w_ratio") + "の" + O + "物理ダメージ" + E + "と" + R + "{w_slow}%スロウ" + E +
                 "。ミニオンかモンスターに当たるとそこから長いレーザーになり、後ろの敵全員に命中。",
        "skill2": "短くダッシュ（敵が近いと後ろへ）、その後" + A + "{e_t}秒" + E + "バーストファイアが貫通：後ろの敵に{e_pierce}%と" +
                  mag("e_dmg", "e_ap") + "の" + M + "魔法ダメージ" + E + "。チャンピオン命中でCD短縮。",
        "ult": "周囲の敵に" + mag("r_dmg", "r_ap") + "の" + M + "魔法ダメージ" + E + "、" + A + "{r_t}秒" + E + "オーバーチャージ：攻撃速度+{r_as}%、"
               "移動速度+{r_ms}%（チャンピオン命中で累積・延長）、通常攻撃は敵間を連鎖する稲妻の3連射に。",
        "names": ("ウルトラショックレーザー", "スパークサージ", "ライトニングクラッシュ"),
    },
}

C = "league_zeri_sfx_"
V = "league_zeri_sfx_vo_"  # clip names differ from the sound names: a clip named like its sound is not found in game
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_zeri_shot": [(C + "shot", 0.35, 0.0)],
    "league_zeri_hit": [(C + "hit", 0.3, 0.0)],
    "league_zeri_charged": [(C + "charged", 0.5, 0.0)],
    "league_zeri_charged_hit": [(C + "charged_hit", 0.5, 0.0)],
    "league_zeri_ready": [(C + "ready", 0.4, 0.0)],
    "league_zeri_shield": [(C + "shield", 0.45, 0.0)],
    "league_zeri_w_cast": [(C + "w_cast", 0.5, 0.0)],
    "league_zeri_w_launch": [(C + "w_launch", 0.5, 0.0)],
    "league_zeri_w_beam": [(C + "w_beam", 0.55, 0.0)],
    "league_zeri_w_hit": [(C + "w_hit", 0.5, 0.0)],
    "league_zeri_e_cast": [(C + "e_cast", 0.5, 0.0)],
    "league_zeri_e_land": [(C + "e_land", 0.45, 0.0)],
    "league_zeri_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_zeri_r_buff": [(C + "r_buff", 0.45, 0.0)],
    "league_zeri_r_chain": [(C + "r_chain", 0.35, 0.0)],
    "league_zeri_vo_w": [(V + "w", 0.85, 0.0)],
    "league_zeri_vo_e": [(V + "e", 0.85, 0.0)],
    "league_zeri_vo_r": [(V + "r", 0.9, 0.05)],
    "league_zeri_vo_ready": [(V + "ready", 0.85, 0.0)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def values(p):
    v = {k: p[k] for k in ("p_need", "p_dmg", "p_ap", "p_hp", "w_dmg", "w_ratio", "w_slow", "e_pierce", "e_dmg", "e_ap",
                           "r_dmg", "r_ap", "r_as", "r_ms")}
    for k in ("e_t", "r_t"):
        v[k] = secs(p[k])
    return v




def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


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
    if "Zeri" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Zeri. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
