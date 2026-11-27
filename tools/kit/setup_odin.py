"""奥丁的文本（五种语言）、sound_info 和 champion_view，数字取自 build_odin.P。

    python tools/kit/setup_odin.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）。--check 只打印
每段说明的显示长度和全文。

名字：奥丁 / 奧丁 / Odin / 오딘 / オーディン；技能名照原作（漫画第十二回合的呪歌）：第九呪歌・旋影風牙（Vindskǫggull）、
第五呪歌・神環封壁（Fafnir）、第十四呪歌・心弦融歌（Harpalúðr）；被动第十五呪歌・波命湧出（Iðunnar Koppr）写在普攻说明里。
图标照 Codex 的交付（assets/source/odin/icons）。
声音：Codex 的交付（odin_packs/outputs/odin_final_assets.zip）：10 条原创音效和速水奨在第三季官方预告里的两句（「夙愿」「警告」）。
音频不进仓库，tools/kit/seed_odin_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_odin import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"


def magic(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


def heal(d, r):
    return f"{A}{{{d}}}{E} + {APi}{A}{{{r}}}%{E}"


# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则：待机第 1 帧的眼睛在脚底上 39 逻辑格、
# 往前 5 格（放大两倍、PPU 2.4：-33、4）；百科中心照 --centers 的规则（实心顶 -41.0 -> -14）；选人卡 y = -39 - 头顶（量头发 -29.5，
# 冈格尼尔的枪尖比头高 3 格，量头不量枪）-> -10
VIEW = {"face": {"x": 4, "y": -33}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -10}}

TEXT = {
    "zh-hans": {
        "name": "奥丁",
        "attack": "以冈格尼尔刺击，造成" + AD + O + "物理伤害" + E + "加" + magic("a_dmg", "a_ap") + M + "魔法伤害" + E + "。" + O +
                  "波命涌出" + E + "：生命低于" + A + "{p_hp}%" + E + "时项链化作光藤缝合伤口，" + A + "{p_t}秒" + E + "内回复" +
                  heal("p_heal", "p_ap") + "生命（冷却" + A + "{p_cd}秒" + E + "）。",
        "skill": "符文缠住冈格尼尔掷出，追着敌方英雄飞、一定打中：" + magic("q_dmg", "q_ap") + M + "魔法伤害" + E +
                 "，无视魔抗，护盾挡不住。",
        "skill2": "五面刻着古诺尔斯文的盾绕身旋转" + A + "{e_t}秒" + E + "，每面完全挡下一次伤害。",
        "ult": "叩枪齐唱（不受控制），符文扫过周围敌人：" + magic("r_dmg", "r_ap") + M + "魔法伤害" + E + "，身体只听奥丁的：" + R +
               "缴械{r_disarm}秒" + E + "、" + A + "{r_t}秒" + E + "内" + R + "减速{r_slow}%" + E + "，之后三秒每秒受到越来越重的" + M + "魔法伤害" + E + "。",
        "names": ("旋影风牙", "神环封壁", "心弦融歌"),
    },
    "zh-hant": {
        "name": "奧丁",
        "attack": "以岡格尼爾刺擊，造成" + AD + O + "物理傷害" + E + "加" + magic("a_dmg", "a_ap") + M + "魔法傷害" + E + "。" + O +
                  "波命湧出" + E + "：生命低於" + A + "{p_hp}%" + E + "時項鍊化作光藤縫合傷口，" + A + "{p_t}秒" + E + "內回復" +
                  heal("p_heal", "p_ap") + "生命（冷卻" + A + "{p_cd}秒" + E + "）。",
        "skill": "符文纏住岡格尼爾擲出，追著敵方英雄飛、一定打中：" + magic("q_dmg", "q_ap") + M + "魔法傷害" + E +
                 "，無視魔抗，護盾擋不住。",
        "skill2": "五面刻著古諾爾斯文的盾繞身旋轉" + A + "{e_t}秒" + E + "，每面完全擋下一次傷害。",
        "ult": "叩槍齊唱（不受控制），符文掃過周圍敵人：" + magic("r_dmg", "r_ap") + M + "魔法傷害" + E + "，身體只聽奧丁的：" + R +
               "繳械{r_disarm}秒" + E + "、" + A + "{r_t}秒" + E + "內" + R + "緩速{r_slow}%" + E + "，之後三秒每秒受到越來越重的" + M + "魔法傷害" + E + "。",
        "names": ("旋影風牙", "神環封壁", "心弦融歌"),
    },
    "en": {
        "name": "Odin",
        "attack": "A thrust of Gungnir: " + AD + " " + O + "physical damage" + E + " plus " + magic("a_dmg", "a_ap") + " " + M +
                  "magic damage" + E + ". " + O + "Iðunnar Koppr" + E + ": below " + A + "{p_hp}%" + E + " health the spear "
                  "turns back into a necklace whose light vines stitch his wounds, healing " + heal("p_heal", "p_ap") +
                  " over " + A + "{p_t}s" + E + " (every " + A + "{p_cd}s" + E + ").",
        "skill": "Vindskǫggull: runes wrap Gungnir and he hurls it at an enemy champion; it chases its target and always "
                 "hits, dealing " + magic("q_dmg", "q_ap") + " " + M + "magic damage" + E + " that ignores magic resist "
                 "and goes through shields.",
        "skill2": "Fafnir, the Divine Ring Barrier: five shields carved in Old Norse circle him for " + A + "{e_t}s" + E +
                  ", each blocking one hit entirely.",
        "ult": "Harpalúðr: tapping Gungnir, he sings with many mouths (unstoppable) and runes sweep every foe around him: " +
               magic("r_dmg", "r_ap") + " " + M + "magic damage" + E + "; their bodies obey him, not themselves - " + R +
               "disarmed {r_disarm}s" + E + ", " + R + "slowed {r_slow}%" + E + " for " + A + "{r_t}s" + E + " - and the song bites harder each second "
               "for three seconds.",
        "names": ("Vindskǫggull", "Fafnir", "Harpalúðr"),
    },
    "ko": {
        "name": "오딘",
        "attack": "궁니르로 찔러 " + AD + " " + O + "물리 피해" + E + "와 " + magic("a_dmg", "a_ap") + " " + M + "마법 피해" + E +
                  ". " + O + "파명용출" + E + ": 체력이 " + A + "{p_hp}%" + E + " 아래로 떨어지면 목걸이가 빛의 덩굴이 되어 상처를 "
                  "꿰매 " + A + "{p_t}초" + E + " 동안 " + heal("p_heal", "p_ap") + " 회복(재사용 " + A + "{p_cd}초" + E + ").",
        "skill": "룬이 감긴 궁니르를 던진다. 적 챔피언을 쫓아가 반드시 맞혀 " + magic("q_dmg", "q_ap") + " " + M + "마법 피해" + E +
                 ", 마법 저항력을 무시하고 보호막을 꿰뚫는다.",
        "skill2": "고대 노르드 문자가 새겨진 방패 다섯 개가 " + A + "{e_t}초" + E + " 동안 몸을 돌며 하나가 공격 한 번을 완전히 막는다.",
        "ult": "창끝으로 땅을 두드리며 여러 입으로 노래한다(저지 불가). 룬이 주변 적을 훑어 " + magic("r_dmg", "r_ap") + " " + M +
               "마법 피해" + E + ", 몸이 오딘을 따른다: " + R + "{r_disarm}초 무장 해제" + E + ", " + A + "{r_t}초" + E + " 동안 " + R + "{r_slow}% 둔화" + E +
               ", 이후 3초 동안 매초 점점 더 큰 " + M + "마법 피해" + E + ".",
        "names": ("선영풍아", "신환봉벽", "심현융가"),
    },
    "ja": {
        "name": "オーディン",
        "attack": "グングニルで突き" + AD + "の" + O + "物理ダメージ" + E + "と" + magic("a_dmg", "a_ap") + "の" + M + "魔法ダメージ" +
                  E + "。" + O + "波命湧出" + E + "：体力" + A + "{p_hp}%" + E + "未満で首飾りが光の蔦となり傷を縫い、" + A +
                  "{p_t}秒" + E + "で" + heal("p_heal", "p_ap") + "回復（" + A + "{p_cd}秒" + E + "ごと）。",
        "skill": "ルーンを纏うグングニルを投げる。敵チャンピオンを追って必ず当たり、" + magic("q_dmg", "q_ap") + "の" + M +
                 "魔法ダメージ" + E + "、魔法防御を無視しシールドを貫く。",
        "skill2": "古ノルド文字を刻んだ五枚の盾が" + A + "{e_t}秒" + E + "身を巡り、一枚が一撃を完全に防ぐ。",
        "ult": "槍で地を叩き多くの口で歌う（行動妨害無効）。ルーンが周りの敵を貫き" + magic("r_dmg", "r_ap") + "の" + M +
               "魔法ダメージ" + E + "、体はオーディンに従う：" + R + "{r_disarm}秒攻撃不能" + E + "・" + A + "{r_t}秒" + E + R + "{r_slow}%鈍足" + E +
               "、その後3秒毎秒より重い" + M + "魔法ダメージ" + E + "。",
        "names": ("旋影風牙", "神環封壁", "心弦融歌"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_odin 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "thrust", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "thrust_hit", 0.4, 0.0)],
    f"{ID}_q": [(SFX + "spear_cast", 0.55, 0.0)],
    f"{ID}_q_hit": [(SFX + "spear_hit", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "ward", 0.5, 0.0)],
    f"{ID}_r_chant": [(SFX + "chant", 0.5, 0.0)],
    f"{ID}_r": [(SFX + "field", 0.6, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/odin.rs）：盾挡下一下、双鸦、波命湧出、配音、死的时候倒地（第 6 帧 0.6 秒）
    f"{ID}_e_block": [(SFX + "ward_hit", 0.45, 0.0)],
    f"{ID}_p_ravens": [(SFX + "ravens", 0.4, 0.0)],
    f"{ID}_p_heal": [(SFX + "chant", 0.45, 0.0)],
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.6)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("ambition", "warning")},
}


def values(p):
    v = {k: p[k] for k in ("a_dmg", "a_ap", "p_hp", "p_heal", "p_ap", "q_dmg", "q_ap", "r_dmg", "r_ap", "r_slow")}
    for k in ("p_t", "p_cd", "e_t", "r_disarm", "r_t"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "odin", "tools/kit/seed_odin_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
