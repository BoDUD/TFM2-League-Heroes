"""坂田金时的文本（五种语言）、sound_info 和 champion_view，数字取自 build_kintoki.P。

    python tools/kit/setup_kintoki.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）。--check 只打印
每段说明的显示长度和全文。

名字：坂田金时 / 坂田金時 / Sakata Kintoki / 사카타 킨토키 / 坂田金時；技能名照原作（漫画第十二回合）：金光雷斧・烈煌閃、
鬼剛閃・供犠、絶技・金光轟雷斧；被动「鬼之血」（「我身上流着老妈的鬼之血，还没完呢！」）和接住冈格尼尔写在普攻说明里。
图标照 Codex 的交付（assets/source/kintoki/icons）。
声音：Codex 的交付（kintoki_packs/outputs/kintoki_final_assets.zip）：9 条原创音效，没有配音（官方日语的找不到）。音频不进仓库，
tools/kit/seed_kintoki_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_kintoki import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX = f"{ID}_sfx_"

# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则：待机第 1 帧的眼睛在脚底上 34 逻辑格、
# 正上方（放大两倍、PPU 2.4：-28、0）；百科中心照 --centers 的规则（实心顶 -37.0 -> -10）；选人卡 y = -39 - 头顶（量头发 -26.5，
# 斧头比头高 2 格，量头不量斧）-> -12
VIEW = {"face": {"x": 0, "y": -28}, "center": {"x": 0, "y": -10}, "banpick_center": {"x": 0, "y": -12}}

TEXT = {
    "zh-hans": {
        "name": "坂田金时",
        "attack": "横扫一斧，造成" + AD + O + "物理伤害" + E + "。" + O + "鬼之血" + E + "：每损失1%生命，攻击力提高" + A +
                  "{p_pct}%" + E + "（最多" + A + "{p_max}%" + E + "）。被奥丁的冈格尼尔打中时徒手接住，只受" + A + "{k_take}%" + E +
                  "伤害并把枪掷回去。",
        "skill": "斧刃伸出巨大的斧形光刃，一斧劈出，一路造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "；斧落地时身前的敌人再受" +
                 phys("q2_dmg", "q2_ad") + O + "物理伤害" + E + "。",
        "skill2": "踏稳前脚，一下窜到敌方英雄身后，途中横斩，造成" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R +
                  "减速{e_slow}%" + E + "，持续" + A + "{e_slow_t}秒" + E + "。",
        "ult": "右手的神性之证亮起（不受控制），金光大斧砸地：前方敌人受到" + phys("r_dmg", "r_ad") + O + "物理伤害" + E + "并被" + R +
               "击飞{r_up}秒" + E + "，护盾先被击碎（连奥丁的神环封壁）。",
        "names": ("金光雷斧·烈煌闪", "鬼刚闪·供牺", "绝技·金光轰雷斧"),
    },
    "zh-hant": {
        "name": "坂田金時",
        "attack": "橫掃一斧，造成" + AD + O + "物理傷害" + E + "。" + O + "鬼之血" + E + "：每損失1%生命，攻擊力提高" + A +
                  "{p_pct}%" + E + "（最多" + A + "{p_max}%" + E + "）。被奧丁的岡格尼爾打中時徒手接住，只受" + A + "{k_take}%" + E +
                  "傷害並把槍擲回去。",
        "skill": "斧刃伸出巨大的斧形光刃，一斧劈出，一路造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "；斧落地時身前的敵人再受" +
                 phys("q2_dmg", "q2_ad") + O + "物理傷害" + E + "。",
        "skill2": "踏穩前腳，一下竄到敵方英雄身後，途中橫斬，造成" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R +
                  "緩速{e_slow}%" + E + "，持續" + A + "{e_slow_t}秒" + E + "。",
        "ult": "右手的神性之證亮起（不受控制），金光大斧砸地：前方敵人受到" + phys("r_dmg", "r_ad") + O + "物理傷害" + E + "並被" + R +
               "擊飛{r_up}秒" + E + "，護盾先被擊碎（連奧丁的神環封壁）。",
        "names": ("金光雷斧·烈煌閃", "鬼剛閃·供犧", "絕技·金光轟雷斧"),
    },
    "en": {
        "name": "Sakata Kintoki",
        "attack": "An axe sweep: " + AD + " " + O + "physical damage" + E + ". " + O + "Oni's Blood" + E + ": his mother's "
                  "demon blood won't let him go down - " + A + "{p_pct}%" + E + " more attack for every 1% health lost (up to " +
                  A + "{p_max}%" + E + "). He catches Odin's Gungnir barehanded, takes only " + A + "{k_take}%" + E +
                  " and throws it back.",
        "skill": "Golden Lightning Axe - Furious Flash: a giant axe of light grows from his blade and one swing sends it "
                 "flying, dealing " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + " along its path; where "
                 "the axe lands, foes before him take " + phys("q2_dmg", "q2_ad") + " more.",
        "skill2": "Demon's Might Slash - Sacrifice: planting his lead foot, he springs past an enemy champion to its back "
                  "with a heavy sweep, dealing " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E + " and " + R +
                  "slowing {e_slow}%" + E + " for " + A + "{e_slow_t}s" + E + ".",
        "ult": "Golden Light Roaring Thunder Axe: the divine rune on his right hand blazes (unstoppable) and the golden axe "
               "crashes down, dealing " + phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + " in front of him and " +
               R + "knocking up for {r_up}s" + E + "; shields shatter first - Odin's Fafnir too.",
        "names": ("Furious Flash", "Demon's Might Slash", "Golden Light Thunder Axe"),
    },
    "ko": {
        "name": "사카타 킨토키",
        "attack": "도끼로 휩쓸어 " + AD + " " + O + "물리 피해" + E + ". " + O + "귀신의 피" + E + ": 잃은 체력 1%마다 공격력 " + A +
                  "{p_pct}%" + E + " 증가(최대 " + A + "{p_max}%" + E + "). 오딘의 궁니르에 맞으면 맨손으로 잡아 " + A +
                  "{k_take}%" + E + "만 받고 되던진다.",
        "skill": "도끼날에서 거대한 빛의 도끼가 뻗어 나가 날아가며 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E +
                 ", 도끼가 땅에 닿을 때 앞의 적에게 " + phys("q2_dmg", "q2_ad") + " 추가.",
        "skill2": "앞발을 디디고 적 챔피언의 뒤로 순식간에 파고들며 베어 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E +
                  ", " + A + "{e_slow_t}초" + E + " 동안 " + R + "{e_slow}% 둔화" + E + ".",
        "ult": "오른손의 신성의 증표가 빛나고(저지 불가) 금빛 도끼를 내리쳐 앞의 적에게 " + phys("r_dmg", "r_ad") + " " + O +
               "물리 피해" + E + "를 주고 " + R + "{r_up}초 띄운다" + E + ". 보호막을 먼저 부순다(오딘의 신환봉벽도).",
        "names": ("금광뇌부·열황섬", "귀강섬·공희", "절기·금광굉뇌부"),
    },
    "ja": {
        "name": "坂田金時",
        "attack": "斧で薙ぎ払い" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "鬼の血" + E + "：失った体力1%ごとに攻撃力" + A +
                  "{p_pct}%" + E + "上昇（最大" + A + "{p_max}%" + E + "）。オーディンのグングニルを素手で受け止め、" + A +
                  "{k_take}%" + E + "だけ受けて投げ返す。",
        "skill": "斧刃から巨大な光の斧が伸び、振り抜いて飛ばす。通り道の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E +
                 "、斧が地に着くとき前方の敵に" + phys("q2_dmg", "q2_ad") + "追加。",
        "skill2": "前足を踏みしめ、敵チャンピオンの背後へ一瞬で抜けながら薙ぐ。" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" +
                  E + "と" + A + "{e_slow_t}秒" + E + R + "{e_slow}%鈍足" + E + "。",
        "ult": "右手の神性の証が光り（行動妨害無効）、金光の大斧を叩きつける。前方の敵に" + phys("r_dmg", "r_ad") + "の" + O +
               "物理ダメージ" + E + "と" + R + "{r_up}秒打ち上げ" + E + "、シールドは先に砕く（オーディンの神環封壁も）。",
        "names": ("金光雷斧・烈煌閃", "鬼剛閃・供犠", "絶技・金光轟雷斧"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_kintoki 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "sweep", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "sweep_hit", 0.4, 0.0)],
    f"{ID}_q": [(SFX + "cleave_cast", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "cleave_hit", 0.35, 0.0)],
    f"{ID}_q_land": [(SFX + "cleave_hit", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "rush_trail", 0.5, 0.0)],
    f"{ID}_e_hit": [(SFX + "rush_hit", 0.5, 0.0)],
    f"{ID}_r_rune": [(SFX + "divinity", 0.55, 0.0)],
    f"{ID}_r": [(SFX + "final_hit", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "rush_hit", 0.4, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/kintoki.rs）：击碎护盾、接住冈格尼尔、掷回去、打中奥丁、死的时候倒地（第 6 帧 0.57 秒）
    f"{ID}_r_shatter": [(SFX + "cleave_hit", 0.55, 0.0)],
    f"{ID}_k_catch": [(SFX + "rush_hit", 0.55, 0.0)],
    f"{ID}_k_throw": [(SFX + "sweep", 0.55, 0.0)],
    f"{ID}_k_back_hit": [(SFX + "final_hit", 0.5, 0.0)],
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.57)],
}


def values(p):
    v = {k: p[k] for k in ("p_max", "q_dmg", "q_ad", "q2_dmg", "q2_ad", "e_dmg", "e_ad", "e_slow", "r_dmg", "r_ad")}
    v["p_pct"] = f"{p['p_per'] / 10:g}"
    v["k_take"] = 100 - p["k_catch"]
    for k in ("e_slow_t", "r_up"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "kintoki", "tools/kit/seed_kintoki_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
