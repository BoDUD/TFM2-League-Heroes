"""列奥尼达斯的文本（五种语言）、sound_info 和 champion_view，数字取自 build_leonidas.P。

    python tools/kit/setup_leonidas.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_leonidas（说明和技能名）、sound/sfx/ragnarok_leonidas_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：列奥尼达斯 / 列奧尼達斯 / Leonidas / 레오니다스 / レオニダス；技能名照 Codex 的交付（盾击、链盾、举盾、方阵冲锋）；被动
「方阵」写在普攻说明里。图标照 Codex 的交付（assets/source/leonidas/runtime/icons：chain、guard、phalanx；bash 那张是普攻，
图标位只有三个，不装）。
声音：Codex 的交付（leonidas_packs/outputs/leonidas_assets_done.zip）：用到 15 条原创音效（挥盾和命中、链盾的起手、放出、命中、
回卷和接盾、举盾、反弹、收盾、换真理之盾、冲锋和命中、盾落地、着地）和六句官方日语原声（白熊寛嗣）；盾击蓄力那条没用上
（普攻的效果在砸到那一拍才放，蓄力在它前面）。音频不进仓库，tools/kit/seed_leonidas_audio.py 从交付复制到
ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_leonidas import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"

# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则（和联盟一样）：
# 待机第 1 帧的眼睛在脚底上 101 格、往前 9 格（PPU 2.75：-37、3）；百科中心照 --centers 的规则（实心顶 -41.3 -> -14）；
# 选人卡 y = -39 - 头顶（-31.3）-> -8
VIEW = {"face": {"x": 3, "y": -37}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -8}}

TEXT = {
    "zh-hans": {
        "name": "列奥尼达斯",
        "attack": "盾击，造成" + AD + O + "物理伤害" + E + "。" + O + "方阵" + E + "：每放一个技能，身边的友方英雄（含自己）" + A +
                  "{p_t}秒" + E + "内护甲和魔抗" + S + "+{p_res}" + E + "。",
        "skill": "甩出连着钢链的圆盾砸向目标，造成" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R + "眩晕{q_stun}秒" + E + "、" + R +
                 "减速{q_slow}%" + E + "，收链时把目标" + R + "拽近" + E + "。",
        "skill2": "举盾" + A + "{e_t}秒" + E + "：身边的友方英雄受到的伤害降低" + S + "{e_adr}%" + E + "，他自己再降低" + S +
                  "{e_self}%" + E + "，攻击他的敌人受到" + A + "{e_ref}%" + E + "反伤，身边的敌人被" + R +
                  "嘲讽{e_taunt}秒" + E + "。",
        "ult": "换上真理之盾冲向目标（不受控制、减伤" + A + "{r_dr}%" + E + "），撞上时身边的敌人受到" + phys("r_dmg", "r_ad") + O +
               "物理伤害" + E + "并被" + R + "击飞{r_up}秒" + E + "。",
        "names": ("链盾", "举盾", "方阵冲锋"),
    },
    "zh-hant": {
        "name": "列奧尼達斯",
        "attack": "盾擊，造成" + AD + O + "物理傷害" + E + "。" + O + "方陣" + E + "：每放一個技能，身邊的友方英雄（含自己）" + A +
                  "{p_t}秒" + E + "內護甲和魔抗" + S + "+{p_res}" + E + "。",
        "skill": "甩出連著鋼鏈的圓盾砸向目標，造成" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R + "暈眩{q_stun}秒" + E + "、" + R +
                 "減速{q_slow}%" + E + "，收鏈時把目標" + R + "拽近" + E + "。",
        "skill2": "舉盾" + A + "{e_t}秒" + E + "：身邊的友方英雄受到的傷害降低" + S + "{e_adr}%" + E + "，他自己再降低" + S +
                  "{e_self}%" + E + "，攻擊他的敵人受到" + A + "{e_ref}%" + E + "反傷，身邊的敵人被" + R +
                  "嘲諷{e_taunt}秒" + E + "。",
        "ult": "換上真理之盾衝向目標（不受控制、減傷" + A + "{r_dr}%" + E + "），撞上時身邊的敵人受到" + phys("r_dmg", "r_ad") + O +
               "物理傷害" + E + "並被" + R + "擊飛{r_up}秒" + E + "。",
        "names": ("鏈盾", "舉盾", "方陣衝鋒"),
    },
    "en": {
        "name": "Leonidas",
        "attack": "A shield bash: " + AD + " " + O + "physical damage" + E + ". " + O + "Phalanx" + E + ": each skill he casts "
                  "gives allied champions near him (himself too) " + S + "+{p_res}" + E + " armor and magic resist for " + A +
                  "{p_t}s" + E + ".",
        "skill": "He hurls his chained shield at the target: " + phys("q_dmg", "q_ad") + " " + O + "physical damage" + E + ", a " +
                 R + "{q_stun}s stun" + E + " and a " + R + "{q_slow}% slow" + E + ", then " + R + "drags it closer" + E +
                 " as he reels the chain in.",
        "skill2": "He raises his shield for " + A + "{e_t}s" + E + ": allied champions near him take " + S + "{e_adr}%" + E +
                  " less damage, he himself " + S + "{e_self}%" + E + " less again, enemies hitting him take " + A +
                  "{e_ref}%" + E + " back and enemies near him are " + R + "taunted for {e_taunt}s" + E + ".",
        "ult": "With the Shield of Truth he charges the target (unstoppable, " + A + "{r_dr}%" + E + " less damage): on impact "
               "enemies around him take " + phys("r_dmg", "r_ad") + " " + O + "physical damage" + E + " and are " + R +
               "knocked up for {r_up}s" + E + ".",
        "names": ("Chain Shield", "Raise Shield", "Phalanx Charge"),
    },
    "ko": {
        "name": "레오니다스",
        "attack": "방패 강타로 " + AD + " " + O + "물리 피해" + E + ". " + O + "팔랑크스" + E + ": 스킬을 쓸 때마다 주변 아군 챔피언(자신 포함)의 "
                  "방어력과 마법 저항력 " + S + "+{p_res}" + E + "(" + A + "{p_t}초" + E + ").",
        "skill": "사슬 달린 방패를 던져 대상에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E + ", " + R + "{q_stun}초 기절" + E + ", " + R +
                 "{q_slow}% 둔화" + E + ", 사슬을 거둘 때 대상을 " + R + "끌어당김" + E + ".",
        "skill2": "방패를 " + A + "{e_t}초" + E + " 들어 주변 아군 챔피언이 받는 피해 " + S + "{e_adr}%" + E + " 감소, 자신은 " + S +
                  "{e_self}%" + E + " 더 감소, 자신을 공격한 적은 " + A + "{e_ref}%" + E + " 반사 피해, 주변 적은 " + R +
                  "{e_taunt}초 도발" + E + ".",
        "ult": "진리의 방패로 대상에게 돌진(저지 불가, 피해 " + A + "{r_dr}%" + E + " 감소)해 부딪힐 때 주변 적에게 " +
               phys("r_dmg", "r_ad") + " " + O + "물리 피해" + E + "와 " + R + "{r_up}초 띄워 올림" + E + ".",
        "names": ("사슬 방패", "방패 들기", "팔랑크스 돌격"),
    },
    "ja": {
        "name": "レオニダス",
        "attack": "盾打ちで" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "ファランクス" + E + "：スキルを使うたび、周りの味方チャンピオン"
                  "（自分も）の物理防御と魔法防御" + S + "+{p_res}" + E + "（" + A + "{p_t}秒" + E + "）。",
        "skill": "鎖付きの盾を投げつけ、対象に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "、" + R + "{q_stun}秒スタン" + E + "、" + R +
                 "{q_slow}%スロウ" + E + "。鎖を引き戻すとき対象を" + R + "引き寄せる" + E + "。",
        "skill2": "盾を" + A + "{e_t}秒" + E + "構え、周りの味方チャンピオンの被ダメージを" + S + "{e_adr}%" + E + "軽減、自分はさらに" +
                  S + "{e_self}%" + E + "軽減し、自分を攻撃した敵に" + A + "{e_ref}%" + E + "反射、周りの敵を" + R +
                  "{e_taunt}秒挑発" + E + "。",
        "ult": "真理の盾で対象へ突撃（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）。ぶつかると周りの敵に" + phys("r_dmg", "r_ad") +
               "の" + O + "物理ダメージ" + E + "と" + R + "{r_up}秒打ち上げ" + E + "。",
        "names": ("鎖盾", "盾構え", "ファランクス突撃"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_leonidas 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "bash", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "bash_hit", 0.45, 0.0)],
    f"{ID}_q_wind": [(SFX + "chain_windup", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "chain_throw", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "disc_hit", 0.5, 0.0)],
    f"{ID}_q_back": [(SFX + "chain_retract", 0.45, 0.0)],
    f"{ID}_q_catch": [(SFX + "disc_catch", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "guard_raise", 0.5, 0.0)],
    f"{ID}_e_reflect": [(SFX + "arrow_reflect", 0.5, 0.0)],
    f"{ID}_e_fade": [(SFX + "guard_fade", 0.4, 0.0)],
    f"{ID}_r_show": [(SFX + "truth_shield", 0.55, 0.0)],
    f"{ID}_r": [(SFX + "phalanx_dash", 0.55, 0.0)],
    f"{ID}_r_hit": [(SFX + "phalanx_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/leonidas.rs）：死的时候盾落地、人着地（Codex 的 cues：0.501 / 0.846 秒）和配音
    f"{ID}_dead": [(SFX + "shield_land", 0.45, 0.501), (SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("challenge", "sparta", "apollo", "taunt", "chain", "charge")},
}


def values(p):
    v = {k: p[k] for k in ("p_res", "q_dmg", "q_ad", "q_slow", "e_adr", "e_self", "e_ref", "r_dr", "r_dmg", "r_ad")}
    for k in ("p_t", "q_stun", "e_t", "e_taunt", "r_up"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "leonidas", "tools/kit/seed_leonidas_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
