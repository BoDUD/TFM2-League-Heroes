"""Kha'Zix's text (5 languages), sound_info files and his keys in the shared files, numbers from build_khazix.P.

    python tools/kit/setup_khazix.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_khazix in every language, description + skill_name),
sound/sfx/league_khazix_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and the
ban/pick card's point once the sprite is in), mod.mod_info (0.69.0, Kha'Zix named). Only his keys change in the shared
files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: the client's zh_CN string table (the Chinese client swaps name and title: 卡兹克 / 虚空掠夺者; 无形威胁, 品尝恐惧,
虚空突刺, 跃击, 虚空来袭; evolutions 收割利爪 / 刺鞘 / 虫翼 / 动态遮蔽, 孤立无援) and Data Dragon 16.19.1 (zh_TW 卡力斯 /
虛空掠食者, 暗影殺機, 孤獨的恐懼, 虛空尖刺, 掠翅飛躍, 虛空突襲, 孤立; ko 카직스 / 공허의 약탈자, 보이지 않는 위협, 공포 감지,
공허의 가시, 도약, 공허의 습격, 고립; ja カ＝ジックス / ヴォイドの捕食者, 見えざる脅威, 甘美なる恐怖, ヴォイドの刺棘, リープ,
捕食の本能, 孤立). skill2 is named after E (the leap; the icon is E's), W in the text.
No `league_khazix_attack` sound: the engine would play it at the start of every attack; the swing plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_khazix import P, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_khazix"
VERSION = "0.69.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
M = "<#a974ffff>"      # magic damage
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
G = "<#66bb6aff>"      # healing
E = "<>"
# champion_view: the face at the top of the blue face plate, the centre on the chest - where those squares landed when
# fix_khazix_strips.py shrank him (「螳螂可以整体缩小一点」; before: face (9, -33), centre (2, -16)); banpick: 37 rows
# now, the top at -25, so the card holds him whole and no banpick_center is set (the card rule: only tops above -28;
# 45 rows needed -8)
VIEW = {"face": {"x": 8, "y": -26}, "center": {"x": 1, "y": -11}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def mag(d, r):
    return f"{M}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def grn(d, r):
    return f"{G}{{{d}}}{E} + {ADi}{G}{{{r}}}%{E}"


TEXT = {
    "zh-hans": {
        "name": "卡兹克",
        "attack": "利爪攻击。被动" + O + "无形威胁" + E + "：隐身或{quiet}秒没出手后，下次攻击英雄附加" + mag("ut_dmg", "ut_ratio") +
                  M + "伤害" + E + "并减速{ut_slow}%。" + A + "{lv_q}/{lv_e}/{lv_r}级" + E + "依次进化Q、E、R。",
        "skill": "爪击：" + phy("q_dmg", "q_ratio") + O + "物理伤害" + E + "；目标身边没有友军（" + A + "孤立无援" + E + "）时改为" +
                 phy("q_iso_dmg", "q_iso_ratio") + "。" + O + "进化收割利爪" + E + "：攻击距离变长，对孤立目标返还冷却。",
        "skill2": "跃向敌方英雄，落地造成" + phy("e_dmg", "e_ratio") + O + "物理伤害" + E + "，再射出" + O + "虚空突刺" + E + "：" +
                  phy("w_dmg", "w_ratio") + "并减速{w_slow}%，身在爆炸中回复" + grn("w_heal", "w_heal_r") + G + "生命" + E +
                  "。" + O + "进化虫翼" + E + "：跳得更远，击杀英雄刷新。",
        "ult": A + "隐身{r_inv}秒" + E + "并加速{r_ms}%，" + O + "无形威胁" + E + "就绪，可再用1次。" + O + "进化动态遮蔽" + E + "：" +
               A + "隐身{r_inv_evo}秒" + E + "，共可用3次。",
        "names": ("品尝恐惧", "跃击", "虚空来袭"),
    },
    "zh-hant": {
        "name": "卡力斯",
        "attack": "利爪攻擊。被動" + O + "暗影殺機" + E + "：隱形或{quiet}秒沒出手後，下次攻擊英雄附加" + mag("ut_dmg", "ut_ratio") +
                  M + "傷害" + E + "並緩速{ut_slow}%。" + A + "{lv_q}/{lv_e}/{lv_r}級" + E + "依次進化Q、E、R。",
        "skill": "爪擊：" + phy("q_dmg", "q_ratio") + O + "物理傷害" + E + "；目標身邊沒有友軍（" + A + "孤立" + E + "）時改為" +
                 phy("q_iso_dmg", "q_iso_ratio") + "。" + O + "進化死神之爪" + E + "：攻擊距離變長，對孤立目標返還冷卻。",
        "skill2": "躍向敵方英雄，落地造成" + phy("e_dmg", "e_ratio") + O + "物理傷害" + E + "，再射出" + O + "虛空尖刺" + E + "：" +
                  phy("w_dmg", "w_ratio") + "並緩速{w_slow}%，身在爆炸中回復" + grn("w_heal", "w_heal_r") + G + "生命" + E +
                  "。" + O + "進化飛翅" + E + "：跳得更遠，擊殺英雄重置。",
        "ult": A + "隱形{r_inv}秒" + E + "並加速{r_ms}%，" + O + "暗影殺機" + E + "就緒，可再用1次。" + O + "進化自適應化形" + E + "：" +
               A + "隱形{r_inv_evo}秒" + E + "，共可用3次。",
        "names": ("孤獨的恐懼", "掠翅飛躍", "虛空突襲"),
    },
    "en": {
        "name": "Kha'Zix",
        "attack": "Claw strikes. Passive " + O + "Unseen Threat" + E + ": after stealth or {quiet}s without acting, his next "
                  "attack on a champion deals " + mag("ut_dmg", "ut_ratio") + " " + M + "bonus damage" + E + " and slows "
                  "{ut_slow}%. Evolves Q, E, R at " + A + "levels {lv_q}/{lv_e}/{lv_r}" + E + ".",
        "skill": "Slashes for " + phy("q_dmg", "q_ratio") + " " + O + "physical damage" + E + ", or " +
                 phy("q_iso_dmg", "q_iso_ratio") + " to a target with no allies nearby (" + A + "Isolated" + E + "). " +
                 O + "Reaper Claws" + E + ": longer attack range; refunds cooldown on Isolated targets.",
        "skill2": "Leaps at an enemy champion, dealing " + phy("e_dmg", "e_ratio") + " " + O + "physical damage" + E +
                  " on landing, then fires a " + O + "Void Spike" + E + ": " + phy("w_dmg", "w_ratio") + ", a {w_slow}% "
                  "slow, and heals him " + grn("w_heal", "w_heal_r") + " if he is in the blast. " + O + "Wings" + E +
                  ": longer leap, reset on champion kills.",
        "ult": "Becomes " + A + "invisible for {r_inv}s" + E + " with {r_ms}% move speed and " + O + "Unseen Threat" + E +
               " ready; can be cast once more. " + O + "Adaptive Cloaking" + E + ": " + A + "{r_inv_evo}s" + E +
               ", three casts.",
        "names": ("Taste Their Fear", "Leap", "Void Assault"),
    },
    "ko": {
        "name": "카직스",
        "attack": "발톱 공격. 기본 지속 효과 " + O + "보이지 않는 위협" + E + ": 은신 후 또는 {quiet}초간 행동하지 않으면 다음 챔피언 공격이 " +
                  mag("ut_dmg", "ut_ratio") + "의 " + M + "추가 피해" + E + ", {ut_slow}% 둔화. " + A + "{lv_q}/{lv_e}/{lv_r}레벨" + E +
                  "에 Q, E, R 진화.",
        "skill": "베기: " + phy("q_dmg", "q_ratio") + "의 " + O + "물리 피해" + E + ", 주변에 아군이 없는(" + A + "고립" + E + ") 대상에게는 " +
                 phy("q_iso_dmg", "q_iso_ratio") + ". " + O + "거대 갈고리" + E + ": 사거리 증가, 고립 대상에게 재사용 대기시간 반환.",
        "skill2": "적 챔피언에게 도약해 착지 시 " + phy("e_dmg", "e_ratio") + "의 " + O + "물리 피해" + E + ", 이어서 " + O + "공허의 가시" +
                  E + ": " + phy("w_dmg", "w_ratio") + ", {w_slow}% 둔화, 폭발 범위 안이면 " + grn("w_heal", "w_heal_r") + " " + G +
                  "회복" + E + ". " + O + "날개" + E + ": 사거리 증가, 챔피언 처치 시 초기화.",
        "ult": A + "{r_inv}초 은신" + E + ", 이동 속도 {r_ms}%, " + O + "보이지 않는 위협" + E + " 준비, 한 번 더 사용 가능. " + O +
               "활성 보호색" + E + ": " + A + "{r_inv_evo}초" + E + ", 3회 사용.",
        "names": ("공포 감지", "도약", "공허의 습격"),
    },
    "ja": {
        "name": "カ＝ジックス",
        "attack": "爪で攻撃。パッシブ " + O + "見えざる脅威" + E + "：インビジブル後か{quiet}秒行動しないと、次のチャンピオンへの攻撃が" +
                  mag("ut_dmg", "ut_ratio") + "の" + M + "追加ダメージ" + E + "と{ut_slow}%スロウ。" + A + "Lv{lv_q}/{lv_e}/{lv_r}" + E +
                  "でQ・E・Rが進化。",
        "skill": "斬撃：" + phy("q_dmg", "q_ratio") + "の" + O + "物理ダメージ" + E + "、近くに味方がいない（" + A + "孤立" + E + "）対象には" +
                 phy("q_iso_dmg", "q_iso_ratio") + "。" + O + "死鎌" + E + "：射程延長、孤立対象でCD返還。",
        "skill2": "敵チャンピオンへ跳躍し着地で" + phy("e_dmg", "e_ratio") + "の" + O + "物理ダメージ" + E + "、続けて" + O + "ヴォイドの刺棘" +
                  E + "：" + phy("w_dmg", "w_ratio") + "と{w_slow}%スロウ、爆発内なら" + grn("w_heal", "w_heal_r") + G + "回復" + E +
                  "。" + O + "翅" + E + "：飛距離延長、キルでCD解消。",
        "ult": A + "{r_inv}秒インビジブル" + E + "、移動速度{r_ms}%、" + O + "見えざる脅威" + E + "発動、もう1回使用可。" + O + "適応擬態" +
               E + "：" + A + "{r_inv_evo}秒" + E + "、3回使用。",
        "names": ("甘美なる恐怖", "リープ", "捕食の本能"),
    },
}

C = "league_khazix_sfx_"
V = "league_khazix_vo_"
# sound name -> [(clip, volume, delay)]
SOUNDS = {
    "league_khazix_a_swing": [(C + "swing", 0.4, 0.0)],
    "league_khazix_a_hit": [(C + "hit", 0.35, 0.0)],
    "league_khazix_p_hit": [(C + "p_hit", 0.5, 0.0)],
    "league_khazix_p_ready": [(C + "p_ready", 0.4, 0.0)],
    "league_khazix_q_swing": [(C + "q_swing", 0.5, 0.0)],
    "league_khazix_q_hit": [(C + "q_hit", 0.5, 0.0)],
    "league_khazix_q_iso_hit": [(C + "q_iso_hit", 0.6, 0.0)],
    "league_khazix_e_jump": [(C + "e_jump", 0.55, 0.0)],
    "league_khazix_e_land": [(C + "e_land", 0.55, 0.0)],
    "league_khazix_e_hit": [(C + "hit", 0.3, 0.0)],
    "league_khazix_e_reset": [(C + "e_reset", 0.55, 0.0)],
    "league_khazix_w_throw": [(C + "w_throw", 0.5, 0.0)],
    "league_khazix_w_hit": [(C + "w_hit", 0.5, 0.0)],
    "league_khazix_r_cast": [(C + "r_cast", 0.6, 0.0)],
    "league_khazix_evo": [(C + "evo", 0.6, 0.0)],
    "league_khazix_vo_q": [(V + "q", 0.8, 0.0)],
    "league_khazix_vo_e": [(V + "e", 0.8, 0.0)],
    "league_khazix_vo_r": [(V + "r", 0.9, 0.05)],
    "league_khazix_vo_evo_q": [(V + "evo_q", 0.9, 0.3)],
    "league_khazix_vo_evo_e": [(V + "evo_e", 0.9, 0.3)],
    "league_khazix_vo_evo_r": [(V + "evo_r", 0.9, 0.3)],
}
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("ut_dmg", "ut_ratio", "ut_slow", "lv_q", "lv_e", "lv_r", "q_dmg", "q_ratio", "q_iso_dmg",
                           "q_iso_ratio", "e_dmg", "e_ratio", "w_dmg", "w_ratio", "w_slow", "w_heal", "w_heal_r",
                           "r_ms")}
    for k in ("quiet", "r_inv", "r_inv_evo"):
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
    if "Kha'Zix" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w' ]+?)\. Kits", r", \1 and Kha'Zix. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
