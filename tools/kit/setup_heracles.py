"""赫拉克勒斯的文本（五种语言）、sound_info 和 champion_view，数字取自 build_heracles.P。

    python tools/kit/setup_heracles.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）：
text/champion.i18n 里每种语言的 ragnarok_heracles（说明和技能名）、sound/sfx/ragnarok_heracles_*.sound_info 和它们的覆盖项、
style/champion_view（头像点、百科中心、选人卡中心）。--check 只打印每段说明的显示长度和全文。

名字：赫拉克勒斯 / 赫拉克勒斯 / Heracles / ヘラクレス / 헤라클레스；技能名照神话里的十二项功业：涅墨亚之狮（第一项，他的
棍棒头就是那头狮子）、克里特公牛（第七项）、刻耳柏洛斯（第十二项，终末的女武神里和冥府的看门犬订约变身），图标照
Codex 的交付（assets/source/heracles/runtime/icons：lion、slam、cerberus；justice 那张是被动，不装）。被动「十二御业的
刻印」写在普攻说明里。
声音：Codex 的交付（heracles_packs/outputs/heracles_assets_done.zip）：12 条原创音效（巨棒挥击、命中、砸地、落地，狮子御业，
御业起势、变身、护势，空手的拳风、命中、重拳落地，身子着地）和六句官方日语原声（小西克幸）。音频不进仓库，
tools/kit/seed_heracles_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时 package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_heracles import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, E, phys, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
# champion_view（离脚底点的游戏像素，往上是负）：待机第 1 帧的眼睛在脚底上约 106 格 = 32 个游戏像素、往前 3 格 = 1；
# 百科中心照小次郎、波塞冬（1 倍待机的实心顶上方 22 格左右）：实心顶 -29 -> -7；选人卡用默认的 -12
VIEW = {"face": {"x": 1, "y": -32}, "center": {"x": 0, "y": -7}, "banpick_center": {"x": 0, "y": -12}}

TEXT = {
    "zh-hans": {
        "name": "赫拉克勒斯",
        "attack": "巨棒一击，造成" + AD + O + "物理伤害" + E + "。" + O + "十二御业的刻印" + E + "：每放一个技能刻印爬一格（大招两格，最多" +
                  A + "{p_max}格" + E + "），每格攻击力" + A + "+{p_atk}%" + E + "、护甲和魔抗" + A + "+{p_res}" + E + "；死后消退。",
        "skill": "巨棒前顶，狮头冲出：前方扇形里的敌人受到" + phys("q_dmg", "q_ad") + O + "物理伤害" + E + "并" + R + "减速{q_slow}%" +
                 E + "。刻耳柏洛斯形态：一拳砸地，身前的敌人受到" + phys("cq_dmg", "cq_ad") + O + "物理伤害" + E + "并被" + R + "击飞" +
                 E + "。",
        "skill2": "巨棒砸地，身前的敌人受到" + phys("e_dmg", "e_ad") + O + "物理伤害" + E + "并" + R + "眩晕{e_stun}秒" + E +
                  "。刻耳柏洛斯形态：护势，" + A + "{ce_t}秒" + E + "内受到的伤害降低" + A + "{ce_dr}%" + E + "并反弹" + A + "{ce_ref}%" +
                  E + "，" + R + "嘲讽" + E + "身边的敌人" + R + "{ce_taunt}秒" + E + "。",
        "ult": "与冥府的看门犬订约，变成刻耳柏洛斯形态" + A + "{r_t}秒" + E + "：攻击力" + A + "+{r_atk}%" + E + "、攻速" + A + "+{r_as}%" +
               E + "、移速" + A + "+{r_ms}%" + E + "、受到的伤害降低" + A + "{r_dr}%" + E + "、吸血" + A + "{r_vamp}%" + E +
               "；结束时一拳砸地，身边的敌人受到" + phys("r_end_dmg", "r_end_ad") + O + "物理伤害" + E + "并被" + R + "击飞" + E + "。",
        "names": ("涅墨亚之狮", "克里特公牛", "刻耳柏洛斯"),
    },
    "zh-hant": {
        "name": "赫拉克勒斯",
        "attack": "巨棒一擊，造成" + AD + O + "物理傷害" + E + "。" + O + "十二御業的刻印" + E + "：每放一個技能刻印爬一格（大招兩格，最多" +
                  A + "{p_max}格" + E + "），每格攻擊力" + A + "+{p_atk}%" + E + "、護甲和魔抗" + A + "+{p_res}" + E + "；死後消退。",
        "skill": "巨棒前頂，獅頭衝出：前方扇形裡的敵人受到" + phys("q_dmg", "q_ad") + O + "物理傷害" + E + "並" + R + "減速{q_slow}%" +
                 E + "。刻耳柏洛斯形態：一拳砸地，身前的敵人受到" + phys("cq_dmg", "cq_ad") + O + "物理傷害" + E + "並被" + R + "擊飛" +
                 E + "。",
        "skill2": "巨棒砸地，身前的敵人受到" + phys("e_dmg", "e_ad") + O + "物理傷害" + E + "並" + R + "暈眩{e_stun}秒" + E +
                  "。刻耳柏洛斯形態：護勢，" + A + "{ce_t}秒" + E + "內受到的傷害降低" + A + "{ce_dr}%" + E + "並反彈" + A + "{ce_ref}%" +
                  E + "，" + R + "嘲諷" + E + "身邊的敵人" + R + "{ce_taunt}秒" + E + "。",
        "ult": "與冥府的看門犬訂約，變成刻耳柏洛斯形態" + A + "{r_t}秒" + E + "：攻擊力" + A + "+{r_atk}%" + E + "、攻速" + A + "+{r_as}%" +
               E + "、移速" + A + "+{r_ms}%" + E + "、受到的傷害降低" + A + "{r_dr}%" + E + "、吸血" + A + "{r_vamp}%" + E +
               "；結束時一拳砸地，身邊的敵人受到" + phys("r_end_dmg", "r_end_ad") + O + "物理傷害" + E + "並被" + R + "擊飛" + E + "。",
        "names": ("涅墨亞之獅", "克里特公牛", "刻耳柏洛斯"),
    },
    "en": {
        "name": "Heracles",
        "attack": "A blow of the club for " + AD + " " + O + "physical damage" + E + ". " + O + "Brand of the Twelve Labors" + E +
                  ": every skill spreads the brand one step (the ultimate two, up to " + A + "{p_max}" + E + "), each step " + A +
                  "+{p_atk}%" + E + " attack and " + A + "+{p_res}" + E + " armour and magic resistance. It fades when he dies.",
        "skill": "Thrusts the club and a lion's head charges out: enemies in a cone take " + phys("q_dmg", "q_ad") + " " + O +
                 "physical damage" + E + " and are " + R + "slowed {q_slow}%" + E + ". Cerberus form: a fist into the ground "
                 "ahead for " + phys("cq_dmg", "cq_ad") + " " + O + "physical damage" + E + ", " + R + "knocking up" + E + ".",
        "skill2": "Slams the club down: enemies before him take " + phys("e_dmg", "e_ad") + " " + O + "physical damage" + E +
                  " and are " + R + "stunned for {e_stun}s" + E + ". Cerberus form: a guard - for " + A + "{ce_t}s" + E +
                  " he takes " + A + "{ce_dr}%" + E + " less damage, reflects " + A + "{ce_ref}%" + E + " and " + R + "taunts" +
                  E + " enemies around him for " + R + "{ce_taunt}s" + E + ".",
        "ult": "Makes his pact with the hound of Hades, Cerberus form for " + A + "{r_t}s" + E + ": " + A + "+{r_atk}%" + E +
               " attack, " + A + "+{r_as}%" + E + " attack speed, " + A + "+{r_ms}%" + E + " move speed, " + A + "{r_dr}%" + E +
               " less damage taken, " + A + "{r_vamp}%" + E + " life steal. At its end a fist into the ground: " +
               phys("r_end_dmg", "r_end_ad") + " " + O + "physical damage" + E + " around him, " + R + "knocking up" + E + ".",
        "names": ("Nemean Lion", "Cretan Bull", "Cerberus"),
    },
    "ko": {
        "name": "헤라클레스",
        "attack": "곤봉으로 내려쳐 " + AD + " " + O + "물리 피해" + E + ". " + O + "열두 과업의 각인" + E + ": 스킬을 쓸 때마다 각인이 한 칸 "
                  "번진다(궁극기는 두 칸, 최대 " + A + "{p_max}칸" + E + "). 칸마다 공격력 " + A + "+{p_atk}%" + E + ", 방어력과 마법 "
                  "저항력 " + A + "+{p_res}" + E + ". 죽으면 사라짐.",
        "skill": "곤봉을 내지르자 사자 머리가 뛰쳐나가 앞쪽 부채꼴의 적에게 " + phys("q_dmg", "q_ad") + " " + O + "물리 피해" + E +
                 "와 " + R + "{q_slow}% 둔화" + E + ". 케르베로스 형태: 땅을 내리찍는 주먹으로 " + phys("cq_dmg", "cq_ad") + " " + O +
                 "물리 피해" + E + "와 " + R + "에어본" + E + ".",
        "skill2": "곤봉으로 땅을 내리쳐 앞의 적에게 " + phys("e_dmg", "e_ad") + " " + O + "물리 피해" + E + "와 " + R + "{e_stun}초 기절" +
                  E + ". 케르베로스 형태: 방어 자세로 " + A + "{ce_t}초" + E + " 동안 받는 피해 " + A + "{ce_dr}%" + E + " 감소, " + A +
                  "{ce_ref}%" + E + " 반사, 주변의 적 " + R + "{ce_taunt}초 도발" + E + ".",
        "ult": "명계의 문지기 개와 계약해 " + A + "{r_t}초" + E + " 동안 케르베로스 형태: 공격력 " + A + "+{r_atk}%" + E + ", 공격 속도 " +
               A + "+{r_as}%" + E + ", 이동 속도 " + A + "+{r_ms}%" + E + ", 받는 피해 " + A + "{r_dr}%" + E + " 감소, 흡혈 " + A +
               "{r_vamp}%" + E + ". 끝날 때 땅을 내리찍어 주변에 " + phys("r_end_dmg", "r_end_ad") + " " + O + "물리 피해" + E + "와 " +
               R + "에어본" + E + ".",
        "names": ("네메아의 사자", "크레타의 황소", "케르베로스"),
    },
    "ja": {
        "name": "ヘラクレス",
        "attack": "棍棒の一撃で" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "十二の御業の刻印" + E + "：スキルのたびに刻印が一つ"
                  "広がり（奥義は二つ、最大" + A + "{p_max}" + E + "）、一つごとに攻撃力" + A + "+{p_atk}%" + E + "、物理・魔法防御" + A +
                  "+{p_res}" + E + "。倒れると消える。",
        "skill": "棍棒を突き出し獅子の頭が飛び出す：前方扇形の敵に" + phys("q_dmg", "q_ad") + "の" + O + "物理ダメージ" + E + "と" + R +
                 "{q_slow}%スロウ" + E + "。ケルベロス形態：地面への拳で" + phys("cq_dmg", "cq_ad") + "の" + O + "物理ダメージ" + E +
                 "と" + R + "打ち上げ" + E + "。",
        "skill2": "棍棒を叩きつけ前方の敵に" + phys("e_dmg", "e_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "{e_stun}秒スタン" + E +
                  "。ケルベロス形態：構え、" + A + "{ce_t}秒" + E + "間被ダメージ" + A + "{ce_dr}%" + E + "軽減・" + A + "{ce_ref}%" + E +
                  "反射、周囲の敵を" + R + "{ce_taunt}秒挑発" + E + "。",
        "ult": "冥府の番犬と契約し" + A + "{r_t}秒" + E + "ケルベロス形態：攻撃力" + A + "+{r_atk}%" + E + "、攻撃速度" + A + "+{r_as}%" +
               E + "、移動速度" + A + "+{r_ms}%" + E + "、被ダメージ" + A + "{r_dr}%" + E + "軽減、吸血" + A + "{r_vamp}%" + E +
               "。終わりに地面へ拳：周囲に" + phys("r_end_dmg", "r_end_ad") + "の" + O + "物理ダメージ" + E + "と" + R + "打ち上げ" +
               E + "。",
        "names": ("ネメアの獅子", "クレタの雄牛", "ケルベロス"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_heracles 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "club_swing", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "club_hit", 0.45, 0.0)],
    f"{ID}_ca": [(SFX + "fist_whoosh", 0.45, 0.0)],
    f"{ID}_ca_hit": [(SFX + "fist_hit", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "lion_wave", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "club_hit", 0.5, 0.0)],
    f"{ID}_cq": [(SFX + "fist_slam", 0.5, 0.0)],
    f"{ID}_e": [(SFX + "club_slam", 0.55, 0.0)],
    f"{ID}_ce": [(SFX + "guard", 0.5, 0.0)],
    f"{ID}_r1": [(SFX + "awakening", 0.55, 0.0)],
    f"{ID}_r2": [(SFX + "form_change", 0.6, 0.0)],
    # 形态结束的重拳：拳风在 c_ult 第 4 帧（0.329 秒），砸地在第 5 帧（0.401 秒）
    f"{ID}_r_end": [(SFX + "fist_whoosh", 0.5, 0.329), (SFX + "fist_slam", 0.6, 0.401)],
    # ragnarok.dll（addons/ragnarok/src/heracles.rs）：死的时候巨棒落地、身子着地（Codex 的 cues：0.349 秒、0.829 秒）和配音
    f"{ID}_dead": [(SFX + "club_drop", 0.45, 0.349), (SFX + "body_drop", 0.5, 0.829)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)]
       for x in ("entry", "representative", "ragnarok", "determination", "principle", "humanity")},
}


def values(p):
    v = {k: p[k] for k in ("p_max", "p_atk", "p_res", "q_dmg", "q_ad", "q_slow", "cq_dmg", "cq_ad", "e_dmg", "e_ad",
                           "ce_dr", "ce_ref", "r_atk", "r_as", "r_ms", "r_dr", "r_vamp", "r_end_dmg", "r_end_ad")}
    for k in ("e_stun", "ce_t", "ce_taunt", "r_t"):
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "heracles", "tools/kit/seed_heracles_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
