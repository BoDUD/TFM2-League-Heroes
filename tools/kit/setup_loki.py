"""洛基的文本（五种语言）、sound_info 和 champion_view，数字取自 build_loki.P。

    python tools/kit/setup_loki.py [--check]

只写 ragnarok/ 里他自己的键（tools/kit/ragnarok_pack.py 写共用的 mod.mod_info 和 mod.override_info 的合并）。--check 只打印
每段说明的显示长度和全文。

名字：洛基 / 洛基 / Loki / 로키 / ロキ；技能名照原作（漫画第十一回合）：锁链钩（掌心的门里伸出的双链钩，原作没有招式名）、
欺瞒之种·回生之门（从黑雾里造复制体、和复制体换位置）、道化师之环（海姆斯克林拉，复制大军）；被动「虚伪之神影」（满力的分身）
写在普攻说明里。图标照 Codex 的交付（assets/source/loki/icons：skill、skill2、ult）。
声音：Codex 的交付（loki_packs/outputs/loki_final_assets.zip）：11 条原创音效和 6 句动画洛基声优松冈禎丞的原声（官方宣传片截的，
audio/sources.json 写着出处和剪辑区间）。音频不进仓库，tools/kit/seed_loki_audio.py 从交付复制到 ragnarok/sound/sfx/，安装时
package_mod 挪到 sound/bgm/。
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_loki import P, ID  # noqa: E402
from ragnarok_pack import (MOD, lp, ADi, AD, O, A, R, M, S, E, phys, ratio, secs, check_lengths,  # noqa: E402,F401
                           print_texts, write_hero, write_mod_info)

SFX, VO = f"{ID}_sfx_", f"{ID}_vo_"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"


def magic(d, r):
    return f"{M}{{{d}}}{E} + {APi}{M}{{{r}}}%{E}"


# champion_view（离脚底点的游戏像素，往上是负），照 tools/art/bp_card_audit.py 的规则：待机第 1 帧的眼睛在脚底上 45 逻辑格、
# 往前 5 格（放大两倍、PPU 8/3：-34、4）；百科中心照 --centers 的规则（实心顶 -42.0 -> -15）；选人卡 y = -39 - 头顶（-30.7）-> -8
VIEW = {"face": {"x": 4, "y": -34}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -8}}

TEXT = {
    "zh-hans": {
        "name": "洛基",
        "attack": "弹出幻刃，造成" + AD + O + "物理伤害" + E + "。" + O + "虚伪之神影" + E + "：满力的分身照着他出招，锁链钩打中的"
                  "敌人再挨分身一钩，" + magic("p_dmg", "p_ap") + M + "魔法伤害" + E + "。",
        "skill": "掌心开门甩出钩刃，造成" + magic("q_dmg", "q_ap") + M + "魔法伤害" + E + "并" + R + "减速{q_slow}%" + E + "。",
        "skill2": "黑雾里造出复制体留在原地，自己和远处的复制体换位，" + A + "隐身{e_inv}秒" + E + "，移速提高" + A + "{e_ms}%" +
                  E + "。",
        "ult": "目标周围冒出复制来的神兵大军（不受控制），" + A + "{r_n}轮" + E + "各造成" + magic("r_dmg", "r_ap") + M + "魔法伤害" +
               E + "并" + R + "减速{r_slow}%" + E + "。",
        "names": ("锁链钩", "欺瞒之种·回生之门", "道化师之环"),
    },
    "zh-hant": {
        "name": "洛基",
        "attack": "彈出幻刃，造成" + AD + O + "物理傷害" + E + "。" + O + "虛偽之神影" + E + "：滿力的分身照著他出招，鎖鏈鉤打中的"
                  "敵人再挨分身一鉤，" + magic("p_dmg", "p_ap") + M + "魔法傷害" + E + "。",
        "skill": "掌心開門甩出鉤刃，造成" + magic("q_dmg", "q_ap") + M + "魔法傷害" + E + "並" + R + "緩速{q_slow}%" + E + "。",
        "skill2": "黑霧裡造出複製體留在原地，自己和遠處的複製體換位，" + A + "隱身{e_inv}秒" + E + "，移速提高" + A + "{e_ms}%" +
                  E + "。",
        "ult": "目標周圍冒出複製來的神兵大軍（不受控制），" + A + "{r_n}輪" + E + "各造成" + magic("r_dmg", "r_ap") + M + "魔法傷害" +
               E + "並" + R + "緩速{r_slow}%" + E + "。",
        "names": ("鎖鏈鉤", "欺瞞之種·回生之門", "道化師之環"),
    },
    "en": {
        "name": "Loki",
        "attack": "A flicked phantom blade: " + AD + " " + O + "physical damage" + E + ". " + O + "Hveðrung" + E +
                  ": his full-power double copies his moves; an enemy hit by his chained hook is hooked again for " +
                  magic("p_dmg", "p_ap") + " " + M + "magic damage" + E + ".",
        "skill": "A hook lashes from the gate in his palm: " + magic("q_dmg", "q_ap") + " " + M + "magic damage" + E +
                 " and a " + R + "{q_slow}% slow" + E + ".",
        "skill2": "Seed of Trickery: a copy rises from black mist where he stood, and Endurlífa swaps him with a copy further "
                  "back: " + A + "invisible for {e_inv}s" + E + ", " + A + "{e_ms}%" + E + " more move speed.",
        "ult": "Heimskringla: an army of copied gods' weapons rises round the target (unstoppable while he casts), " + A +
               "{r_n} waves" + E + " of " + magic("r_dmg", "r_ap") + " " + M + "magic damage" + E + " and a " + R +
               "{r_slow}% slow" + E + ".",
        "names": ("Chained Hook", "Seed of Trickery", "Heimskringla"),
    },
    "ko": {
        "name": "로키",
        "attack": "환영 칼날을 튕겨 " + AD + " " + O + "물리 피해" + E + ". " + O + "거짓된 신영" + E + ": 전력의 분신이 따라 "
                  "하여, 사슬 갈고리에 맞은 적에게 한 번 더 " + magic("p_dmg", "p_ap") + " " + M + "마법 피해" + E + ".",
        "skill": "손바닥의 문에서 갈고리를 휘둘러 " + magic("q_dmg", "q_ap") + " " + M + "마법 피해" + E + "와 " + R +
                 "{q_slow}% 둔화" + E + ".",
        "skill2": "검은 안개로 복제체를 남기고 먼 복제체와 자리를 바꿈: " + A + "{e_inv}초 은신" + E + ", 이동 속도 " + A +
                  "{e_ms}%" + E + " 증가.",
        "ult": "대상 주위에 복제한 신들의 무기 군세가 솟아(저지 불가) " + A + "{r_n}번" + E + " 각 " + magic("r_dmg", "r_ap") +
               " " + M + "마법 피해" + E + "와 " + R + "{r_slow}% 둔화" + E + ".",
        "names": ("사슬 갈고리", "기만의 씨앗", "광대의 고리"),
    },
    "ja": {
        "name": "ロキ",
        "attack": "幻の刃を弾き" + AD + "の" + O + "物理ダメージ" + E + "。" + O + "偽りの神影" + E + "：全力の分身が真似をし、"
                  "鎖鉤に当たった敵へもう一撃" + magic("p_dmg", "p_ap") + "の" + M + "魔法ダメージ" + E + "。",
        "skill": "掌の門から鉤刃を振るい" + magic("q_dmg", "q_ap") + "の" + M + "魔法ダメージ" + E + "と" + R + "{q_slow}%スロウ" +
                 E + "。",
        "skill2": "黒い霧から複製体を残し、遠くの複製体と入れ替わる：" + A + "{e_inv}秒透明" + E + "、移動速度" + A + "{e_ms}%" +
                  E + "上昇。",
        "ult": "対象の周りに複製した神々の武器の軍勢が湧き（行動妨害無効）、" + A + "{r_n}回" + E + "各" + magic("r_dmg", "r_ap") +
               "の" + M + "魔法ダメージ" + E + "と" + R + "{r_slow}%スロウ" + E + "。",
        "names": ("鎖鉤", "誑かしの種", "道化師の環"),
    },
}

# 声音事件 -> [(音频, 音量, 延迟)]：数据（build_loki 的 sfx / tsfx）和 ragnarok.dll 放的每一个
SOUNDS = {
    f"{ID}_a": [(SFX + "flick", 0.45, 0.0)],
    f"{ID}_a_hit": [(SFX + "flick_hit", 0.4, 0.0)],
    f"{ID}_q_wind": [(SFX + "hook_windup", 0.45, 0.0)],
    f"{ID}_q": [(SFX + "hook", 0.5, 0.0)],
    f"{ID}_q_hit": [(SFX + "hook_hit", 0.5, 0.0)],
    f"{ID}_p_hit": [(SFX + "hook_hit", 0.4, 0.0)],
    f"{ID}_e": [(SFX + "shadow_veil", 0.5, 0.0)],
    f"{ID}_e_decoy": [(SFX + "decoy", 0.5, 0.0)],
    f"{ID}_r_load": [(SFX + "phantom_charge", 0.5, 0.0)],
    f"{ID}_r": [(SFX + "phantom_field", 0.6, 0.0)],
    f"{ID}_r_hit": [(SFX + "phantom_hit", 0.55, 0.0)],
    # ragnarok.dll（addons/ragnarok/src/loki.rs）：死的时候落地（Codex 的 cues：0.902 秒）和配音
    f"{ID}_dead": [(SFX + "fall", 0.5, 0.902)],
    **{f"{ID}_v_{x}": [(VO + x, 0.8, 0.0)] for x in ("select", "delight", "laugh", "taunt", "reaction", "buddha_rival")},
}


def values(p):
    v = {k: p[k] for k in ("p_dmg", "p_ap", "q_dmg", "q_ap", "q_slow", "e_ms", "r_n", "r_dmg", "r_ap", "r_slow")}
    v["e_inv"] = secs(p["e_inv"])
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
    n, c = write_hero(ID, tx, SOUNDS, VIEW, "loki", "tools/kit/seed_loki_audio.py")
    write_mod_info()
    print(n, "sounds,", c, "clips; texts, champion_view and mod_info written")


if __name__ == "__main__":
    main()
