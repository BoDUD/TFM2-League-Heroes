"""佐佐木小次郎的文本（五种语言）、sound_info 和 champion_view，数字取自 build_kojiro.P。

    python tools/kit/setup_kojiro.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_kojiro（说明和技能名）、sound/sfx/ragnarok_kojiro_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：终末的女武神里的叫法，佐佐木小次郎 / 佐佐木小次郎 / Sasaki Kojiro / 佐々木小次郎 / 사사키 코지로；技能名照 Codex 的交接
（assets/source/kojiro/HANDOFF.md）和他的图标：燕返、千手无双、二天岩流，被动预判写在普攻说明里。
声音：Codex 的交付（kojiro_packs/outputs/kojiro_assets_done.zip）：12 条原创音效（两组刀风、两组金属命中、燕返的下斩和
上撩、预判、侧避、二天岩流的两刀、刀落地、身子着地）和八句官方日语原声（山路和弘）。音频不进仓库，
tools/kit/seed_kojiro_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_kojiro import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧的眼睛在脚底上约 86 格 = 26 个游戏像素、往前 6 格 = 2；
# 站高 112 格 = 34 个游戏像素，百科中心按 bp_card_audit 的规矩是 -8；选人卡用默认的 -12
VIEW = {"face": {"x": 2, "y": -26}, "center": {"x": 0, "y": -8}, "banpick_center": {"x": 0, "y": -12}}

TEXT = {
    "zh-hans": {
        "name": "佐佐木小次郎",
        "attack": "长刀一斩，造成" + AD + O + "物理伤害" + E + "。" + O + "预判" + E + "：每打中一个敌方英雄一次就记下他一招（每人最多" +
                  A + "{p_max}招" + E + "），之后对他的伤害每招" + A + "+{p_per}%" + E + "；死后重新记。",
        "skill": "往前斩下，前方扇形里的敌人受到" + phys("q1_dmg", "q1_ad") + O + "物理伤害" + E + "；随即反刃上撩，再造成" +
                 phys("q2_dmg", "q2_ad") + O + "物理伤害" + E + "并" + R + "减速{q_slow}%" + E + "。",
        "skill2": "预判对手的一千种走法，侧身让开：" + A + "{e_t}秒" + E + "内受到的伤害降低" + A + "{e_dr}%" + E + "，攻速" + A +
                  "+{e_as}%" + E + "。",
        "ult": "拔出第二把刀，双刀斩下造成" + phys("r1_dmg", "r1_ad") + O + "物理伤害" + E + "，再交错一刀造成" + phys("r2_dmg", "r2_ad") +
               O + "物理伤害" + E + "并" + R + "眩晕{r_stun}秒" + E + "；之后" + A + "{r_form}秒" + E + "双刀：攻速" + A + "+{r_as}%" + E +
               "，普攻多一刀" + A + "{r_extra}%" + E + "。",
        "names": ("燕返", "千手无双", "二天岩流"),
    },
    "zh-hant": {
        "name": "佐佐木小次郎",
        "attack": "長刀一斬，造成" + AD + O + "物理傷害" + E + "。" + O + "預判" + E + "：每打中一個敵方英雄一次就記下他一招（每人最多" +
                  A + "{p_max}招" + E + "），之後對他的傷害每招" + A + "+{p_per}%" + E + "；死後重新記。",
        "skill": "往前斬下，前方扇形裡的敵人受到" + phys("q1_dmg", "q1_ad") + O + "物理傷害" + E + "；隨即反刃上撩，再造成" +
                 phys("q2_dmg", "q2_ad") + O + "物理傷害" + E + "並" + R + "減速{q_slow}%" + E + "。",
        "skill2": "預判對手的一千種走法，側身讓開：" + A + "{e_t}秒" + E + "內受到的傷害降低" + A + "{e_dr}%" + E + "，攻速" + A +
                  "+{e_as}%" + E + "。",
        "ult": "拔出第二把刀，雙刀斬下造成" + phys("r1_dmg", "r1_ad") + O + "物理傷害" + E + "，再交錯一刀造成" + phys("r2_dmg", "r2_ad") +
               O + "物理傷害" + E + "並" + R + "暈眩{r_stun}秒" + E + "；之後" + A + "{r_form}秒" + E + "雙刀：攻速" + A + "+{r_as}%" + E +
               "，普攻多一刀" + A + "{r_extra}%" + E + "。",
        "names": ("燕返", "千手無雙", "二天岩流"),
    },
    "en": {
        "name": "Sasaki Kojiro",
        "attack": "A long-sword cut for " + AD + " " + O + "physical damage" + E + ". " + O + "Prediction" + E + ": each hit on an "
                  "enemy champion learns one of his moves (up to " + A + "{p_max}" + E + " a foe); every move learned adds " + A +
                  "{p_per}%" + E + " to Kojiro's damage against him. Forgotten when Kojiro dies.",
        "skill": "Cuts down through a cone ahead for " + phys("q1_dmg", "q1_ad") + " " + O + "physical damage" + E + ", then turns "
                 "the blade back up for " + phys("q2_dmg", "q2_ad") + " " + O + "physical damage" + E + " and a " + R +
                 "{q_slow}% slow" + E + ".",
        "skill2": "Reads a thousand ways the fight can go and steps aside: for " + A + "{e_t}s" + E + " he takes " + A + "{e_dr}%" +
                  E + " less damage and attacks " + A + "{e_as}%" + E + " faster.",
        "ult": "Draws a second sword: a double cut for " + phys("r1_dmg", "r1_ad") + " " + O + "physical damage" + E + ", then a "
               "cross for " + phys("r2_dmg", "r2_ad") + " " + O + "physical damage" + E + " that " + R + "stuns for {r_stun}s" + E +
               ". For " + A + "{r_form}s" + E + " after, two swords: " + A + "{r_as}%" + E + " attack speed and a second cut of " +
               A + "{r_extra}%" + E + " on every attack.",
        "names": ("Swallow Return", "Senju Muso", "Niten Ganryu"),
    },
    "ko": {
        "name": "사사키 코지로",
        "attack": "장검으로 베어 " + AD + " " + O + "물리 피해" + E + ". " + O + "예측" + E + ": 적 챔피언을 맞힐 때마다 그 수를 하나 "
                  "익혀(한 명당 최대 " + A + "{p_max}수" + E + ") 그 적에게 주는 피해가 수마다 " + A + "+{p_per}%" + E + ". 죽으면 "
                  "처음부터.",
        "skill": "앞쪽 부채꼴을 내려베어 " + phys("q1_dmg", "q1_ad") + " " + O + "물리 피해" + E + ", 곧바로 칼날을 되돌려 올려베어 " +
                 phys("q2_dmg", "q2_ad") + " " + O + "물리 피해" + E + "와 " + R + "{q_slow}% 둔화" + E + ".",
        "skill2": "천 가지 수를 미리 읽고 몸을 비켜 " + A + "{e_t}초" + E + " 동안 받는 피해 " + A + "{e_dr}%" + E + " 감소, 공격 속도 " +
                  A + "+{e_as}%" + E + ".",
        "ult": "두 번째 검을 뽑아 쌍검으로 베어 " + phys("r1_dmg", "r1_ad") + " " + O + "물리 피해" + E + ", 엇갈려 베어 " +
               phys("r2_dmg", "r2_ad") + " " + O + "물리 피해" + E + "와 " + R + "{r_stun}초 기절" + E + ". 이후 " + A + "{r_form}초" +
               E + " 쌍검: 공격 속도 " + A + "+{r_as}%" + E + ", 평타마다 " + A + "{r_extra}%" + E + " 추가 베기.",
        "names": ("츠바메가에시", "센주무소", "니텐간류"),
    },
    "ja": {
        "name": "佐々木小次郎",
        "attack": "長刀の一太刀で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "予測" + E + "：敵チャンピオンに当てるたびに"
                  "その技を一つ覚え（一人" + A + "{p_max}つ" + E + "まで）、以後その敵へのダメージが一つごとに" + A + "+{p_per}%" + E +
                  "。倒れると覚え直し。",
        "skill": "前方扇形に斬り下ろし" + phys("q1_dmg", "q1_ad") + "の" + O + "物理ダメージ" + E + "、返す刃で斬り上げ" +
                 phys("q2_dmg", "q2_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{q_slow}%スロウ" + E + "。",
        "skill2": "千の手を読み身をかわす：" + A + "{e_t}秒" + E + "間被ダメージ" + A + "{e_dr}%" + E + "軽減、攻撃速度" + A + "+{e_as}%" +
                  E + "。",
        "ult": "二本目の刀を抜き、二刀で斬り" + phys("r1_dmg", "r1_ad") + "の" + O + "物理ダメージ" + E + "、交差の一太刀で" +
               phys("r2_dmg", "r2_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{r_stun}秒スタン" + E + "。以後" + A + "{r_form}秒" +
               E + "二刀：攻撃速度" + A + "+{r_as}%" + E + "、通常攻撃に" + A + "{r_extra}%" + E + "の追い太刀。",
        "names": ("燕返し", "千手無双", "二天岩流"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_kojiro 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "cut_1", 0.45, 0.0)],
    f"{ID}_a2": [(SFX + "cut_2", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "hit_1", 0.45, 0.0)],
    f"{ID}_a_hit2": [(SFX + "hit_2", 0.45, 0.0)],
    f"{ID}_q1": [(SFX + "tsubame_down", 0.5, 0.0)],
    f"{ID}_q2": [(SFX + "tsubame_up", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "hit_2", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "prediction", 0.5, 0.0)],
    f"{ID}_e_dodge": [(SFX + "dodge", 0.5, 0.0)],
    f"{ID}_r1": [(SFX + "niten_first", 0.55, 0.0)],
    f"{ID}_r2": [(SFX + "niten_cross", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "hit_1", 0.55, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/kojiro.rs）：死的时候刀落地、身子着地（Codex 的 cues：0.33 秒、0.805 秒）和配音
    f"{ID}_dead": [(SFX + "sword_drop", 0.45, 0.33), (SFX + "body_drop", 0.5, 0.805)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)]
       for x in ("entry", "challenge", "focus", "defeats", "witness", "victory", "charge", "idle")},
}


def values(p):
    v = {k: p[k] for k in ("p_per", "p_max", "q1_dmg", "q1_ad", "q2_dmg", "q2_ad", "q_slow", "e_dr", "e_as", "r1_dmg",
                           "r1_ad", "r2_dmg", "r2_ad", "r_as", "r_extra")}
    for k in ("e_t", "r_stun", "r_form"):
        v[k] = secs(p[k])
    return v


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
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    tx = texts(dict(P))
    bad = check_lengths(TEXT)
    if a.check:
        print_texts(tx)
        return
    if bad:
        sys.exit("a text is longer than TOOLTIP_MAX")
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "kojiro", "tools/kit/seed_kojiro_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
