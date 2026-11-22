"""哈迪斯的文本（五种语言）、sound_info 和 champion_view，数字取自 build_hades.P。

    python tools/kit/setup_hades.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_hades（说明和技能名）、sound/sfx/ragnarok_hades_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：哈迪斯 / 黑帝斯 / Hades / 하데스 / ハデス；技能名照终末的女武神和 Codex 的交付：珀耳塞福涅·风压斩（ペルセポネ・ロアイ）、
冥府重砸、伊科尔·德斯莫斯；被动「伊科尔」写在普攻说明里。图标照 Codex 的交付（assets/source/hades/runtime/icons：wind、earth、
desmos；bident 那张是普攻，图标位只有三个，不装）。
声音：Codex 的交付（hades_packs/outputs/hades_assets_done.zip）：14 条原创音效（出刺和命中、风压斩的运枪、释放和命中、重砸的
抬枪、砸地和命中、碎石、伊科尔强化枪头、德斯莫斯的出刺和命中、双叉枪落地、倒地）和七句官方日语原声（置鮎龍太郎）。音频不进
仓库，tools/kit/seed_hades_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_hades import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则（和联盟一样）：
# 待机第 1 帧的眼睛在脚底上 101 格、往前 5 格（PPU 2.75：-37、2）；百科中心照 bp_card_audit.py --centers 的规则（实心顶 -39.3
# -> -12）；选人卡照它的规则 y = -39 - 头顶，量头不量枪：头发顶在 -28.7（-32 那几行是双叉枪的护环）-> -10
VIEW = {"face": {"x": 2, "y": -37}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -10}}

TEXT = {
    "zh-hans": {
        "name": "哈迪斯",
        "attack": "双叉枪直刺，造成" + AD + O + "物理伤害" + E + "。" + O + "伊科尔" + E + "：放完技能后" + A + "{p_t}秒" + E +
                  "内，下一次普攻额外造成" + phys("p_dmg", "p_ad") + O + "物理伤害" + E + "。",
        "skill": "挥枪掀起珀耳塞福涅的风压，前方扇形内的敌人受到" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R +
                 "减速{q_slow}%" + E + "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "双叉枪砸向身前的地面，那一圈的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并被" + R +
                  "击飞{e_air}秒" + E + "。",
        "ult": "用神血把枪头锻成德斯莫斯（不受控制、减伤" + A + "{r_dr}%" + E + "），朝目标直线突刺，穿过的敌人受到" +
               phys("r_dmg", "r_ad") + "加最大生命" + O + "{r_thp}%" + E + "的" + O + "物理伤害" + E + "并" + R + "眩晕{r_stun}秒" +
               E + "。",
        "names": ("珀耳塞福涅·风压斩", "冥府重砸", "伊科尔·德斯莫斯"),
    },
    "zh-hant": {
        "name": "黑帝斯",
        "attack": "雙叉槍直刺，造成" + AD + O + "物理傷害" + E + "。" + O + "伊柯爾" + E + "：放完技能後" + A + "{p_t}秒" + E +
                  "內，下一次普攻額外造成" + phys("p_dmg", "p_ad") + O + "物理傷害" + E + "。",
        "skill": "揮槍掀起波瑟芬妮的風壓，前方扇形內的敵人受到" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R +
                 "減速{q_slow}%" + E + "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "雙叉槍砸向身前的地面，那一圈的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並被" + R +
                  "擊飛{e_air}秒" + E + "。",
        "ult": "用神血把槍頭鍛成德斯莫斯（不受控制、減傷" + A + "{r_dr}%" + E + "），朝目標直線突刺，穿過的敵人受到" +
               phys("r_dmg", "r_ad") + "加最大生命" + O + "{r_thp}%" + E + "的" + O + "物理傷害" + E + "並" + R + "暈眩{r_stun}秒" +
               E + "。",
        "names": ("波瑟芬妮·風壓斬", "冥府重砸", "伊柯爾·德斯莫斯"),
    },
    "en": {
        "name": "Hades",
        "attack": "A thrust of the bident: " + AD + " " + O + "physical damage" + E + ". " + O + "Ichor" + E + ": for " + A +
                  "{p_t}s" + E + " after a skill, his next attack deals " + phys("p_dmg", "p_ad") + " more " + O +
                  "physical damage" + E + ".",
        "skill": "He sweeps the wind of Persephone with his bident: enemies in a cone take " + phys("q_dmg", "q_ad") + " " + O +
                 "physical damage" + E + " and are " + R + "slowed {q_slow}%" + E + " for " + A + "{q_slow_t}s" + E + ".",
        "skill2": "He smashes the bident into the ground before him: enemies in the circle take " + phys("e_dmg", "e_ad") + " " +
                  O + "physical damage" + E + " and are " + R + "knocked up for {e_air}s" + E + ".",
        "ult": "He forges the Desmos spearhead with his own divine blood (unstoppable, " + A + "{r_dr}%" + E + " less damage) and "
               "thrusts straight through his target: enemies on the way take " + phys("r_dmg", "r_ad") + " + " + O + "{r_thp}%" +
               E + " max health " + O + "physical damage" + E + " and are " + R + "stunned for {r_stun}s" + E + ".",
        "names": ("Persephone Rhoai", "Hammer of the Underworld", "Ichor Desmos"),
    },
    "ko": {
        "name": "하데스",
        "attack": "쌍지창으로 찔러 " + AD + " " + O + "물리 피해" + E + ". " + O + "이코르" + E + ": 스킬을 쓴 뒤 " + A + "{p_t}초" +
                  E + " 안에 다음 기본 공격이 " + phys("p_dmg", "p_ad") + " " + O + "물리 피해" + E + "를 더 줌.",
        "skill": "창을 휘둘러 페르세포네의 풍압을 일으켜 부채꼴 안의 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E +
                 "와 " + R + "{q_slow}% 둔화" + E + "(" + A + "{q_slow_t}초" + E + ").",
        "skill2": "쌍지창으로 앞쪽 땅을 내리찍어 그 원 안의 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R +
                  "{e_air}초 띄워 올림" + E + ".",
        "ult": "신의 피로 창끝을 데스모스로 벼려(저지 불가, 피해 " + A + "{r_dr}%" + E + " 감소) 대상을 향해 일직선으로 찔러 지나간 적에게 " +
               phys("r_dmg", "r_ad") + " + 최대 체력 " + O + "{r_thp}%" + E + " " + O + "물리 피해" + E + "와 " + R +
               "{r_stun}초 기절" + E + ".",
        "names": ("페르세포네 로아이", "명부의 철퇴", "이코르 데스모스"),
    },
    "ja": {
        "name": "ハデス",
        "attack": "二叉槍で突き" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "イコル" + E + "：スキル使用後" + A + "{p_t}秒" + E +
                  "以内の次の通常攻撃が" + phys("p_dmg", "p_ad") + "の" + O + "物理ダメージ" + E + "を追加。",
        "skill": "槍を振ってペルセポネの風圧を起こし、扇形の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                 "{q_slow}%スロウ" + E + "（" + A + "{q_slow_t}秒" + E + "）。",
        "skill2": "二叉槍で前方の地面を叩き割り、円内の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                  "{e_air}秒打ち上げ" + E + "。",
        "ult": "神の血で槍頭をデスモスに鍛え（行動妨害無効、被ダメージ" + A + "{r_dr}%" + E + "軽減）対象へ一直線に突き抜け、通った敵に" +
               phys("r_dmg", "r_ad") + "＋最大体力" + O + "{r_thp}%" + E + "の" + O + "物理ダメージ" + E + "と" + R + "{r_stun}秒スタン" +
               E + "。",
        "names": ("ペルセポネ・ロアイ", "冥府の鉄槌", "イコル・デスモス"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_hades 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "thrust", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "thrust_hit", 0.45, 0.0)],
    f"{ID}_p_hit": [(SFX + "desmos_hit", 0.4, 0.0)],
    f"{ID}_q_load": [(SFX + "wind_prep", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "wind", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "wind_hit", 0.5, 0.0)],
    f"{ID}_e_lift": [(SFX + "slam_prep", 0.45, 0.0)],
    f"{ID}_e": [(SFX + "slam", 0.55, 0.0)],
    f"{ID}_e_hit": [(SFX + "slam_hit", 0.5, 0.0)],
    f"{ID}_e_dust": [(SFX + "dust", 0.45, 0.0)],
    f"{ID}_r_load": [(SFX + "ichor", 0.55, 0.0)],
    f"{ID}_r": [(SFX + "desmos", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "desmos_hit", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/hades.rs）：死的时候双叉枪落地、身子着地（Codex 的 cues：0.353 / 0.846 秒）和配音
    f"{ID}_dead": [(SFX + "spear_fall", 0.45, 0.353), (SFX + "fall", 0.5, 0.846)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("open", "brother", "eye", "earth", "thrust", "wind", "parry")},
}


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ad", "q_dmg", "q_ad", "q_slow", "e_dmg", "e_ad", "r_dr", "r_dmg", "r_ad", "r_thp")}
    for k in ("p_t", "q_slow_t", "e_air", "r_stun"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "hades", "tools/kit/seed_hades_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
