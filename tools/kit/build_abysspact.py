#!/usr/bin/env python3
"""Abyss Pact (渊契) 10-champion skill kit & combo generator.

    python tools/kit/build_abysspact.py [--hero ...] [--plain] [--out file] [--set k=v ...] [--nodes]

Batch 1 Champions:
  1. abysspact_oathbreaker (断誓 · 上路战士 Melee)     - 血誓烧血增幅、W誓链→Q黑焰斩连招、R断誓6秒不死裁决
  2. abysspact_faceless    (无面 · 打野刺客 Assassin)   - 夺面换脸变身、W无相隐身→Q割影→A恐惧→R撕面25%斩杀连招
  3. abysspact_whisperer   (呓语 · 中路法师 Magician)   - 疯狂3层恐惧连锁爆炸、W睁眼→Q低语→R众口群疯连招
  4. abysspact_bonebow     (骸弦 · 下路射手 Range)      - 亡兵真实骷髅兵召唤、Q穿骨起兵/R亡军列阵→W葬礼全军自爆连招
  5. abysspact_corvus      (鸦医 · 辅助 Util)           - 传染疫雾蔓延回血、W渡鸦肩头护盾啄击、Q瘴瓶/R隔离区控场连招

Batch 2 Champions:
  6. abysspact_bloodmoon   (血月 · 上路战士 Melee)      - 月相人狼双形态随时切换、R血月1.3倍巨狼长嚎群体恐惧顺劈
  7. abysspact_undertaker  (入殓 · 打野坦克 Tank)       - 棺盾常驻普攻减伤+技能盾、W甩棺拽己、R把敌C装进棺材扛走2秒摔出
  8. abysspact_effigy      (替身 · 中路法师 Magician)   - 扎针1-3根、W同命线40%伤害互传&拉断双晕、R拆线全图拔针爆发
  9. abysspact_sevenfold   (七弹 · 下路射手 Range)      - 7发弹仓计数、第七颗深渊魔弹全图拐弯真伤、R七发齐射
 10. abysspact_vesper      (烛灵 · 辅助 Util)           - 烛冠0-5支烛火增幅奶盾、Q引路加速奶盾、R回魂唤回阵亡队友魂体再战8秒
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "abysspact"
OUT_DIR = os.path.join(REPO, MOD_ID, "champion")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


# ---------------------------------------------------------------------------
# Tunable parameter tables (initialized from design.txt; tuned via kd.py)
# ---------------------------------------------------------------------------
PARAMS = {
    "oathbreaker": {
        "hp": 1220, "hp_g": 112, "atk": 92, "atk_g": 16, "apw": 0, "apw_g": 0,
        "def": 37, "def_g": 7, "mr": 30, "mr_g": 5, "ms": 1050, "ms_g": 10,
        "atk_range": 28000, "atk_dur": 36, "atk_cd": 60, "atk_st": 17,
        "q_cd": 420, "q_range": 35000, "q_dur": 38, "q_go": 14, "q_hit": 19,
        "q_r": 38000, "q_cone": 350, "q_dmg": 72, "q_ad": 112,
        "q_slow": 30, "q_slow_t": 90, "q_heal": 44, "q_heal_r": 30,
        "q_combo_dmg": 20, "q_combo_ad": 20,
        "w_cd": 720, "w_range": 50000, "w_dur": 40, "w_go": 16,
        "w_speed": 7500, "w_w": 11000, "w_dmg": 60, "w_ad": 80,
        "w_grab_speed": 3200, "w_grab_t": 13, "w_bind": 30,
        "r_cd": 4200, "r_range": 35000, "r_dur": 42, "r_go": 16, "r_arm": 600,
        "r_t": 360, "r_vamp": 40, "r_as": 15, "r_burst_r": 28000,
        "r_burst_dmg": 48, "r_burst_ad": 42,
        "r_onhit_ap": 40, "r_onhit_ad": 30,
        "plain_ad_mult": 14, "plain_as_mult": 18,
    },
    "faceless": {
        "hp": 1000, "hp_g": 96, "atk": 100, "atk_g": 18, "apw": 0, "apw_g": 0,
        "def": 32, "def_g": 6, "mr": 30, "mr_g": 4, "ms": 1090, "ms_g": 11,
        "atk_range": 26000, "atk_dur": 34, "atk_cd": 56, "atk_st": 17,
        "q_cd": 390, "q_range": 40000, "q_dur": 34, "q_go": 10,
        "q_speed": 5600, "q_rad": 18000,
        "q_dmg": 90, "q_ad": 115, "q_slow": 30, "q_slow_t": 60,
        "w_cd": 660, "w_range": 45000, "w_dur": 28, "w_go": 12,
        "w_inv": 90, "w_ms": 20,
        "w_fear": 54, "w_bonus_dmg": 55, "w_bonus_ad": 50,
        "r_cd": 3300, "r_range": 45000, "r_dur": 42, "r_go": 17,
        "r_dmg": 290, "r_ad": 165, "r_plain_thp": 14,
        "s_melee_dmg": 160, "s_melee_ad": 70, "s_range_dmg": 180, "s_range_ad": 80,
        "s_mage_dmg": 200, "s_mage_ad": 80, "s_util_heal": 120, "s_util_dmg": 100, "s_util_ad": 40,
        "s_sin_dmg": 250, "s_sin_ad": 100,
        "plain_shroud_ad": 14, "plain_shroud_as": 18, "plain_shroud_t": 240,
    },
    "whisperer": {
        "hp": 880, "hp_g": 88, "atk": 66, "atk_g": 8, "apw": 60, "apw_g": 21,
        "def": 24, "def_g": 5, "mr": 30, "mr_g": 4, "ms": 950, "ms_g": 9,
        "atk_range": 52000, "atk_dur": 34, "atk_cd": 84, "atk_st": 16,
        "a_speed": 7500, "a_y": -10000,
        "q_cd": 360, "q_range": 60000, "q_dur": 36, "q_go": 15,
        "q_speed": 6800, "q_w": 11000, "q_dmg": 80, "q_ap": 70,
        "w_cd": 660, "w_range": 55000, "w_dur": 38, "w_go": 15,
        "w_r": 22000, "w_t": 180, "w_p": 60, "w_dmg": 28, "w_ap": 22,
        "w_slow": 22, "w_slow_t": 60,
        "r_cd": 3600, "r_range": 60000, "r_dur": 44, "r_go": 18,
        "r_r": 40000, "r_dmg": 215, "r_ap": 108, "r_fear": 66,
        "plain_burst_dmg": 85, "plain_burst_ap": 62, "plain_burst_r": 16000,
    },
    "bonebow": {
        "hp": 900, "hp_g": 88, "atk": 98, "atk_g": 18, "apw": 0, "apw_g": 0,
        "def": 22, "def_g": 6, "mr": 18, "mr_g": 3, "ms": 930, "ms_g": 9,
        "atk_range": 62500, "atk_dur": 36, "atk_cd": 58, "atk_st": 17,
        "a_speed": 9500, "a_y": -9500,
        "q_cd": 470, "q_range": 70000, "q_dur": 36, "q_go": 19,
        "q_speed": 9000, "q_w": 10000, "q_dmg": 75, "q_ad": 105,
        "w_cd": 600, "w_range": 65000, "w_dur": 32, "w_go": 13,
        "w_r": 16000, "w_base_dmg": 40, "w_base_ad": 38,
        "w_plain_dmg": 102, "w_plain_ad": 120,
        "w_slow": 30, "w_slow_t": 60,
        "r_cd": 3900, "r_range": 70000, "r_dur": 44, "r_go": 23,
        "r_travel": 12, "r_r": 35000, "r_dmg": 132, "r_ad": 88,
        "r_slow": 25, "r_slow_t": 90,
        "r_plain_tick_dmg": 47, "r_plain_tick_ad": 47, "r_plain_t": 240, "r_plain_p": 60,
        "plain_p_dmg": 34, "plain_p_ad": 37,
    },
    "corvus": {
        "hp": 1000, "hp_g": 95, "atk": 62, "atk_g": 8, "apw": 42, "apw_g": 15,
        "def": 30, "def_g": 6, "mr": 32, "mr_g": 5, "ms": 990, "ms_g": 10,
        "atk_range": 50000, "atk_dur": 36, "atk_cd": 84, "atk_st": 17,
        "a_speed": 7000, "a_y": -10000,
        "q_cd": 480, "q_range": 55000, "q_dur": 38, "q_go": 15,
        "q_travel": 14, "q_r": 20000, "q_dmg": 52, "q_ap": 42,
        "q_slow": 30, "q_slow_t": 90,
        "q_plain_dot": 28, "q_plain_dot_ap": 15, "q_plain_heal": 24,
        "w_cd": 700, "w_range": 55000, "w_dur": 36, "w_go": 15, "w_ally_r": 45000,
        "w_speed": 6500, "w_sh": 85, "w_sh_ap": 60, "w_t": 240,
        "w_plain_dmg": 48, "w_plain_ap": 30, "w_plain_r": 28000,
        "r_cd": 4200, "r_range": 50000, "r_dur": 44, "r_go": 18,
        "r_r": 40000, "r_t": 300, "r_p": 60,
        "r_init_dmg": 92, "r_init_ap": 65, "r_stun": 40,
        "r_tick_dmg": 35, "r_tick_ap": 25, "r_slow": 40, "r_slow_t": 60,
        "r_heal": 55, "r_heal_ap": 25,
    },
    # --- Batch 2 ---
    "bloodmoon": {
        "hp": 1188, "hp_g": 111, "atk": 95, "atk_g": 17, "apw": 0, "apw_g": 0,
        "def": 37, "def_g": 6, "mr": 30, "mr_g": 5, "ms": 1062, "ms_g": 10,
        # 普攻射程按狼形的近战算，人形的 1.9 万由 bloodmoon.rs 的 human_range 加（--plain 没有原生代码，直接加上）
        "atk_range": 26000, "human_range": 19000, "atk_dur": 36, "atk_cd": 60, "atk_st": 17,
        "a_speed": 9000, "a_y": -9500,
        "wolf_as": 30, "wolf_vamp": 10,
        "q_cd": 412, "q_range": 60000, "q_dur": 38, "q_go": 12,
        "q_speed": 9200, "q_w": 9500, "q_h_dmg": 34, "q_h_ad": 54,
        "q_h_slow": 20, "q_h_slow_t": 90,
        "q_w_dmg": 90, "q_w_ad": 116, "q_w_heal": 20, "q_w_heal_ad": 24,
        # 变身在出招最后一 tick 才换形态：整段变身动画按出手时的形态播完，不会播到一半换成另一个方向的变身
        "w_cd": 360, "w_range": 45000, "w_dur": 26, "w_go": 25,
        "w_slow_r": 30000, "w_slow": 30, "w_slow_t": 60,
        "w_back_spd": 2500, "w_back_t": 6,
        "r_cd": 4120, "r_range": 35000, "r_dur": 40, "r_go": 14,
        "r_t": 480, "r_dr": 25, "r_howl_r": 30000, "r_fear": 62,
        "r_dmg": 84, "r_ad": 72, "plain_cleave_ad": 76,
    },
    "undertaker": {
        "hp": 1366, "hp_g": 127, "atk": 83, "atk_g": 12, "apw": 0, "apw_g": 0,
        "def": 53, "def_g": 9, "mr": 37, "mr_g": 6, "ms": 1030, "ms_g": 10,
        "atk_range": 28000, "atk_dur": 40, "atk_cd": 71, "atk_st": 17,
        "q_cd": 494, "q_range": 28000, "q_dur": 38, "q_go": 15, "q_hit": 20,
        "q_r": 26000, "q_cone": 350, "q_dmg": 56, "q_hp": 6, "q_air": 29,
        "w_cd": 740, "w_range": 50000, "w_dur": 40, "w_go": 12,
        "w_speed": 7500, "w_w": 11000, "w_dmg": 50, "w_ad": 46,
        "w_r": 20000, "w_t": 180, "w_p": 30, "w_slow": 40, "w_slow_t": 45,
        "r_cd": 4540, "r_range": 32000, "r_dur": 42, "r_go": 14,
        "r_carry_t": 120, "r_ms": 20, "r_stun": 60, "r_slam_dmg": 150, "r_slam_thp": 8,
    },
    "effigy": {
        "hp": 877, "hp_g": 87, "atk": 63, "atk_g": 8, "apw": 60, "apw_g": 20,
        "def": 24, "def_g": 5, "mr": 30, "mr_g": 4, "ms": 950, "ms_g": 9,
        "atk_range": 52000, "atk_dur": 36, "atk_cd": 84, "atk_st": 17,
        "a_speed": 8200, "a_y": -9500,
        "q_cd": 374, "q_range": 55000, "q_dur": 36, "q_go": 13,
        "q_speed": 8500, "q_w": 10000, "q_cone": 450,
        "q_dmg": 52, "q_ap": 52, "q_bolt_dmg": 33, "q_bolt_ap": 30,
        "q_slow": 25, "q_slow_t": 60,
        "w_cd": 734, "w_range": 60000, "w_dur": 36, "w_go": 14,
        "w_t": 240, "w_dmg": 39, "w_ap": 31,
        "w_plain_r": 31000, "w_plain_dmg": 67, "w_plain_ap": 41, "w_plain_stun": 41,
        "r_cd": 3400, "r_range": 70000, "r_dur": 42, "r_go": 15,
        "r_r": 37000, "r_dmg": 168, "r_ap": 85, "r_slow": 50, "r_slow_t": 90,
    },
    "sevenfold": {
        "hp": 884, "hp_g": 86, "atk": 92, "atk_g": 16, "apw": 0, "apw_g": 0,
        "def": 22, "def_g": 6, "mr": 18, "mr_g": 3, "ms": 930, "ms_g": 9,
        "atk_range": 60000, "atk_dur": 26, "atk_cd": 59, "atk_st": 14,
        "a_speed": 9800, "a_y": -9500,
        "p_true_dmg": 135, "p_true_ad": 120, "p_range": 90000,
        "q_cd": 458, "q_range": 60000, "q_dur": 36, "q_go": 10,
        "q_dmg": 25, "q_ad": 42,
        "w_cd": 865, "w_range": 60000, "w_dur": 26, "w_go": 8,
        "w_back_spd": 3000, "w_back_t": 6,
        "r_cd": 3860, "r_range": 65000, "r_dur": 46, "r_go": 12,
        "r_dmg": 33, "r_ad": 51,
    },
    "vesper": {
        "hp": 980, "hp_g": 93, "atk": 58, "atk_g": 8, "apw": 48, "apw_g": 17,
        "def": 29, "def_g": 6, "mr": 32, "mr_g": 5, "ms": 992, "ms_g": 10,
        "atk_range": 50000, "atk_dur": 36, "atk_cd": 83, "atk_st": 17,
        "a_speed": 7400, "a_y": -10000,
        "q_cd": 560, "q_range": 55000, "q_dur": 34, "q_go": 13,
        "q_t": 180, "q_ms": 26, "q_heal": 35, "q_heal_ap": 23,
        "q_sh": 62, "q_sh_ap": 46, "q_sh_t": 180,
        "w_cd": 660, "w_range": 50000, "w_dur": 36, "w_go": 14,
        "w_speed": 6800, "w_w": 12000, "w_dmg": 50, "w_ap": 46, "w_fear": 49,
        # 原生版的 R 是 3 tick 的「备好」（敌方英雄 6 万内按），真正的回魂 / 护盾由 vesper.rs 在合适的时候放
        "r_cd": 5100, "r_range": 60000, "r_dur": 44, "r_go": 16, "r_arm_dur": 3,
        "r_r": 50000, "r_sh": 142, "r_sh_ap": 72, "r_sh_t": 300,
        "r_heal": 102, "r_heal_ap": 48, "r_dr": 28, "r_dr_t": 260,
    },
    # --- Batch 3 ---
    "carapace": {
        "hp": 1112, "hp_g": 103, "atk": 93, "atk_g": 17, "apw": 0, "apw_g": 0,
        "def": 34, "def_g": 6, "mr": 30, "mr_g": 5, "ms": 1015, "ms_g": 10,
        "atk_range": 25000, "atk_dur": 36, "atk_cd": 52, "atk_st": 18,
        "q_cd": 398, "q_range": 26000, "q_dur": 36, "q_go": 12,
        "q_speed": 4800, "q_t": 8, "q_rad": 14000, "q_dmg": 94, "q_ad": 123,
        "q_slow": 30, "q_slow_t": 60,
        "w_cd": 430, "w_range": 22000, "w_dur": 34, "w_go": 13,
        "w_r": 21000, "w_dmg": 83, "w_ad": 93, "w_heal": 56, "w_heal_ad": 39,
        # w_vamp：甲鸣按打出伤害的这么多 % 治疗自己（carapace.rs 在 on_attack 里算）
        "w_vamp": 30,
        # 蜕壳 R 的射程 3 万（旧壳在身边炸开，半径 3 万）；第三形态飞扑另加 3 万（carapace.rs 的 r_range）= 6 万
        "r_cd": 3950, "r_range": 30000, "r_dur": 40, "r_go": 14,
        "r_r": 30000, "r_dmg": 195, "r_ad": 127, "r_air": 45, "r_as": 40, "r_as_t": 240,
        "plain_def": 22, "plain_as": 23, "plain_hp_mult": 31,
    },
    "leech": {
        "hp": 1000, "hp_g": 94, "atk": 79, "atk_g": 13, "apw": 69, "apw_g": 23,
        "def": 29, "def_g": 6, "mr": 30, "mr_g": 5, "ms": 1038, "ms_g": 10,
        "atk_range": 25000, "atk_dur": 34, "atk_cd": 50, "atk_st": 17,
        "q_cd": 520, "q_range": 50000, "q_dur": 36, "q_go": 11,
        "q_dmg": 98, "q_ap": 75, "q_slow": 30, "q_slow_t": 180,
        "q_plain_drain": 120, "q_plain_ap": 55, "q_plain_heal": 148,
        "w_cd": 448, "w_range": 26000, "w_dur": 34, "w_go": 12,
        "w_dmg": 117, "w_ap": 85, "w_sil": 60, "w_sil_att": 105,
        "r_cd": 4020, "r_range": 85000, "r_dur": 42, "r_go": 14,
        "r_r": 42000, "r_dmg": 198, "r_ap": 108, "r_heal": 245, "r_heal_ap": 85,
    },
    "noctua": {
        "hp": 848, "hp_g": 83, "atk": 57, "atk_g": 7, "apw": 60, "apw_g": 20,
        "def": 22, "def_g": 5, "mr": 29, "mr_g": 4, "ms": 940, "ms_g": 9,
        "atk_range": 50000, "atk_dur": 34, "atk_cd": 61, "atk_st": 18,
        "a_speed": 8000, "a_y": -10000,
        "q_cd": 396, "q_range": 60000, "q_dur": 36, "q_go": 12,
        "q_dmg": 30, "q_ap": 26, "q_slow": 17, "q_slow_t": 180,
        "w_cd": 756, "w_range": 60000, "w_dur": 36, "w_go": 13,
        "w_dmg": 40, "w_ap": 31, "w_stun": 67, "w_heal": 59, "w_heal_ap": 20,
        "r_cd": 4680, "r_range": 55000, "r_dur": 44, "r_go": 14,
        "r_r": 28000, "r_t": 210, "r_p": 30, "r_tick_dmg": 39, "r_tick_ap": 16, "r_sil": 75,
    },
    "anchor": {
        "hp": 878, "hp_g": 86, "atk": 96, "atk_g": 18, "apw": 0, "apw_g": 0,
        "def": 22, "def_g": 6, "mr": 18, "mr_g": 3, "ms": 950, "ms_g": 9,
        "atk_range": 60000, "atk_dur": 30, "atk_cd": 58, "atk_st": 18,
        "a_speed": 9600, "a_y": -9500,
        "q_cd": 600, "q_range": 26000, "q_dur": 36, "q_go": 13,
        "q_r": 25000, "q_dmg": 64, "q_ad": 81, "q_kb_spd": 2500, "q_kb_t": 8,
        "w_cd": 420, "w_range": 60000, "w_dur": 30, "w_go": 12,
        "r_cd": 4280, "r_range": 95000, "r_dur": 48, "r_go": 14,
        "r_r": 21000, "r_dmg": 95, "r_ad": 58, "r_air": 24,
        "plain_splash_ad": 40,
    },
    "hourglass": {
        "hp": 996, "hp_g": 92, "atk": 54, "atk_g": 7, "apw": 56, "apw_g": 18,
        "def": 28, "def_g": 6, "mr": 33, "mr_g": 5, "ms": 980, "ms_g": 10,
        "atk_range": 50000, "atk_dur": 36, "atk_cd": 63, "atk_st": 18,
        "a_speed": 7800, "a_y": -10000,
        "q_cd": 710, "q_range": 70000, "q_dur": 36, "q_go": 13,
        "q_t": 180, "q_plain_heal": 192, "q_plain_ap": 70,
        "w_cd": 620, "w_range": 65000, "w_dur": 36, "w_go": 14,
        "w_r": 21000, "w_dmg": 80, "w_ap": 56, "w_stun": 66,
        "r_cd": 4820, "r_range": 80000, "r_dur": 44, "r_go": 16,
        "r_r": 75000, "r_plain_heal": 264, "r_plain_ap": 95, "r_plain_sh": 160, "r_plain_sh_ap": 65,
    },
    # --- Batch 4 ---
    "reprieve": {
        "hp": 1330, "hp_g": 121, "atk": 76, "atk_g": 12, "apw": 0, "apw_g": 0,
        "def": 43, "def_g": 7, "mr": 34, "mr_g": 5, "ms": 985, "ms_g": 10,
        "atk_range": 28000, "atk_dur": 38, "atk_cd": 61, "atk_st": 23,
        "q_cd": 580, "q_range": 60000, "q_dur": 38, "q_go": 14,
        "q_speed": 7800, "q_w": 11000, "q_dmg": 94, "q_thp": 7,
        "q_stun": 48, "q_grab_spd": 3200, "q_grab_t": 12,
        "w_cd": 710, "w_range": 30000, "w_dur": 34, "w_go": 12,
        "w_r": 30000, "w_taunt": 78, "w_plain_dr": 24,
        "r_cd": 4200, "r_range": 50000, "r_dur": 42, "r_go": 15,
        "r_r": 50000, "r_cone": 420, "r_dmg": 180, "r_thp": 9, "r_stun": 90,
        "plain_dr": 20,
    },
    "debtor": {
        "hp": 1160, "hp_g": 110, "atk": 94, "atk_g": 16, "apw": 0, "apw_g": 0,
        "def": 36, "def_g": 6, "mr": 32, "mr_g": 5, "ms": 1055, "ms_g": 10,
        "atk_range": 25000, "atk_dur": 32, "atk_cd": 46, "atk_st": 16,
        "q_cd": 360, "q_range": 45000, "q_dur": 34, "q_go": 10,
        "q_speed": 6800, "q_dmg": 102, "q_ad": 122, "q_note_t": 360,
        "w_cd": 460, "w_range": 26000, "w_dur": 34, "w_go": 12,
        "w_r": 25000, "w_dmg": 84, "w_ad": 95, "w_heal": 75, "w_heal_ad": 36,
        "r_cd": 3900, "r_range": 60000, "r_dur": 40, "r_go": 14,
        "r_plain_dmg": 210, "r_plain_thp": 20, "r_plain_heal": 300, "r_plain_ad": 95,
    },
    "traceless": {
        "hp": 968, "hp_g": 95, "atk": 93, "atk_g": 17, "apw": 0, "apw_g": 0,
        "def": 29, "def_g": 6, "mr": 32, "mr_g": 5, "ms": 1048, "ms_g": 10,
        "atk_range": 25000, "atk_dur": 28, "atk_cd": 44, "atk_st": 13,
        "q_cd": 340, "q_range": 46000, "q_dur": 32, "q_go": 10,
        "q_speed": 7000, "q_t": 8, "q_rad": 13000, "q_dmg": 110, "q_ad": 117,
        "w_cd": 680, "w_range": 44000, "w_dur": 26, "w_go": 8,
        "w_banish": 45, "w_inv": 60, "w_ms": 26, "w_ambush_t": 150,
        "w_ambush_dmg": 65, "w_ambush_ad": 67,
        "r_cd": 3560, "r_range": 55000, "r_dur": 40, "r_go": 12,
        "r_vanish": 90, "r_r": 55000, "r_dmg": 138, "r_ad": 104,
        "plain_edge_ad": 26,
    },
    "starfall": {
        "hp": 840, "hp_g": 80, "atk": 62, "atk_g": 9, "apw": 48, "apw_g": 15,
        "def": 20, "def_g": 4, "mr": 26, "mr_g": 4, "ms": 930, "ms_g": 8,
        "atk_range": 65000, "atk_dur": 34, "atk_cd": 68, "atk_st": 21,
        "a_delay": 30, "a_r": 15000, "a_ap": 20, "a_splash_ad": 52, "a_splash_ap": 12,
        "q_cd": 560, "q_range": 70000, "q_dur": 36, "q_go": 12,
        "q_r": 15000, "q_dmg": 38, "q_ap": 28, "q_slow": 30, "q_slow_t": 90,
        "w_cd": 780, "w_range": 32000, "w_dur": 30, "w_go": 10,
        "w_back_spd": 4000, "w_back_t": 10, "w_r": 22000,
        "w_dmg": 45, "w_ap": 32, "w_kb_spd": 2500, "w_kb_t": 6,
        "r_cd": 5100, "r_range": 100000, "r_dur": 42, "r_go": 14,
        "r_r": 40000, "r_t": 240, "r_p": 30, "r_dmg": 38, "r_ap": 28,
    },
    "knell": {
        "hp": 1335, "hp_g": 120, "atk": 65, "atk_g": 10, "apw": 0, "apw_g": 0,
        "def": 43, "def_g": 7, "mr": 37, "mr_g": 5, "ms": 995, "ms_g": 10,
        "atk_range": 25000, "atk_dur": 40, "atk_cd": 64, "atk_st": 24,
        "q_cd": 560, "q_range": 40000, "q_dur": 38, "q_go": 14,
        "q_r": 40000, "q_cone": 420, "q_dmg": 86, "q_hp": 7, "q_stun": 52,
        "w_cd": 690, "w_range": 60000, "w_dur": 34, "w_go": 12,
        "w_r": 60000, "w_sh": 180, "w_sh_t": 200, "w_ms": 24, "w_ms_t": 100,
        "r_cd": 4680, "r_range": 50000, "r_dur": 42, "r_go": 14,
        "r_speed": 6200, "r_r": 25000, "r_t": 150, "r_p": 30,
        "r_tick_dmg": 53, "r_tick_hp": 4, "r_air": 50,
        "plain_dr": 18,
    },
}


# ---------------------------------------------------------------------------
# Shared JSON node builders
# ---------------------------------------------------------------------------
def mk_helpers(cid):
    fx_path = f"asset/{MOD_ID}/effects/{cid}_fx"
    proj_path = f"asset/{MOD_ID}/effects/{cid}_proj"

    def n(x):
        return f"{cid}_{x}"

    def combine(*effects):
        return {"type": "Combine", "effects": [e for e in effects if e is not None]}

    def delayed(tick, *effects):
        return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}

    def flag(name, tick, **fields):
        dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
        return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields},
                "only_to_enemy": False}

    def unflag(name):
        return {"type": "RemoveCasterBuff", "name": n(name)}

    def buff(name, tick, **fields):
        return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}

    def when(name, has, none=None):
        return {"type": "SwitchByBuff", "buff_name": n(name),
                "effect_buff": has if has is not None else combine(),
                "effect_none": none if none is not None else combine()}

    def view(name):
        return {"type": "ViewEffect", "name": n(name)}

    def sfx(name):
        return {"type": "Sfx", "name": n(name)}

    def tsfx(name):
        return {"type": "TargetSfx", "name": n(name)}

    def attack(dmg, ratio, thp=0, hp_ratio=0):
        return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp_ratio,
                "target_hp_ratio": thp, "attack_effect_type": "Target"}

    def fixed(dmg, ratio=0, thp=0):
        return {"type": "FixedAttack", "damage": dmg, "attack_ratio": ratio, "target_hp_ratio": thp}

    def ap_atk(dmg, ratio, hp_ratio=0):
        return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp_ratio, "can_crit": False}

    def heal(amount, ad_ratio=0, ap_ratio=0, kind="Caster"):
        return {"type": "Heal", "amount": amount, "attack_ratio": ad_ratio, "ap_ratio": ap_ratio, "heal_type": kind}

    def shield(amount, ad_ratio=0, ap_ratio=0, tick=180):
        return {"type": "Shield", "amount": amount, "attack_ratio": ad_ratio, "ap_ratio": ap_ratio, "tick": tick}

    def fear(tick):
        return {"type": "Fear", "tick": tick}

    def stun(dur):
        return {"type": "Stun", "duration": dur}

    def airborne(dur):
        return {"type": "Airborne", "duration": dur}

    def silence(tick):
        return {"type": "BlockSkill", "tick": tick}

    def knockback(speed, tick):
        return {"type": "Knockback", "speed": speed, "tick": tick}

    def taunt(dur):
        return {"type": "Taunt", "duration": dur}

    def native_fx(ref):
        return {"type": "Native", "effect_ref": ref}

    def bind(dur):
        return {"type": "Bind", "duration": dur}

    def grab(speed, tick):
        return {"type": "Grab", "speed": speed, "tick": tick}

    def move_back(speed, tick):
        return {"type": "MoveBack", "speed": speed, "tick": tick}

    def move_to_target(speed, rng, end_effects=None):
        return {"type": "MoveToTarget", "speed": speed, "range": rng,
                "end_effects": [e for e in (end_effects or []) if e is not None]}

    def rand_target(rng, target, *effects):
        return {"type": "RandomTarget", "range": rng, "casting_target": target,
                "from_projectile": False, "effects": [e for e in effects if e is not None]}

    def circle(r):
        return {"Circle": {"radius": r}}

    def T(e):
        return {"casting_type": "Targeting", "effect": e}

    def search_self(*effects):
        return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf",
                "from_projectile": False, "effects": [e for e in effects if e is not None]}

    def alive_only(*effects):
        return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                       unflag("live"))

    def cone(radius, cos, effects, target="EnemyWithoutTower"):
        return {"type": "RangeEffect", "shape": {"DirDot": {"radius": radius, "range": cos}},
                "target": target, "apply_type": {"Forward": {"offset": 1000}},
                "effects": [e for e in effects if e is not None]}

    def around(radius, effects, target="EnemyWithoutTower"):
        return {"type": "RangeEffect", "shape": circle(radius), "target": target,
                "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}

    def homing(name, speed, effects, target="Enemy", y=0):
        return {"type": "TargetProjectile", "name": n(name), "speed": speed, "y_offset": y,
                "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None]}

    def linear(name, speed, rng, width, effects, target="EnemyWithoutTower", penetrate=False, end=None, y=0):
        return {"type": "LinearProjectile", "name": n(name), "speed": speed, "range": rng,
                "shape": circle(width), "penetrate": penetrate, "y_offset": y,
                "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None],
                "end_effects": list(end or [])}

    def lob(name, travel, end_effects, target="EnemyWithoutTower"):
        """Always wraps RangeProjectile / RangePeriodProjectile so Position context is guaranteed
        (works on both hero casts and Sylas stolen ults!)."""
        return {"type": "ParabolicProjectile", "name": n(name), "travel_time": travel, "range": 400000,
                "range_effect_name": "", "shape": circle(1), "applied_target": target,
                "applied_effects": [], "end_effects": [e for e in end_effects if e is not None]}

    def zone(name, radius, effects, target="EnemyWithoutTower"):
        return {"type": "RangeProjectile", "name": n(name), "shape": circle(radius), "delay": 1, "apply": 1,
                "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None]}

    def field(name, radius, tick, period, effects, first=1, target="EnemyWithoutTower"):
        return {"type": "RangePeriodProjectile", "name": n(name), "shape": circle(radius),
                "tick": tick, "period": period, "first_delay": first,
                "applied_target": target, "applied_effects": [T(e) for e in effects if e is not None],
                "end_effects": []}

    def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
        return {"action_name": name, "description": f"#asset/base/text/champion?description.{cid}.{name}",
                "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
                "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}

    def V_eff(name, tag, z=2, follow=True):
        return {"type": "Animation", "name": n(name), "anim": fx_path, "tag": tag, "z": z, "is_follow": follow}

    def V_buf(name, tag, z=2):
        return {"type": "Animated", "name": n(name), "anim": fx_path, "tag": tag, "repeat": True, "z": z}

    def V_proj(name, tag, z=2):
        return {"type": "Animated", "name": n(name), "anim": proj_path, "tag": tag, "repeat": True, "z": z}

    return dict(
        n=n, combine=combine, delayed=delayed, flag=flag, unflag=unflag, buff=buff, when=when,
        view=view, sfx=sfx, tsfx=tsfx, attack=attack, fixed=fixed, ap_atk=ap_atk, heal=heal, shield=shield,
        fear=fear, stun=stun, airborne=airborne, silence=silence, knockback=knockback, taunt=taunt,
        native_fx=native_fx, bind=bind, grab=grab, move_back=move_back,
        move_to_target=move_to_target, rand_target=rand_target, circle=circle, T=T, search_self=search_self,
        alive_only=alive_only, cone=cone, around=around, homing=homing, linear=linear, lob=lob,
        zone=zone, field=field, action=action, V_eff=V_eff, V_buf=V_buf, V_proj=V_proj,
    )


def wrap_kit(cid, category, tags, p, attack_a, skill, skill2, ult, views_p, views_e, views_b,
             is_native, passive_ref):
    kit = {
        "id": cid, "category": category, "tags": tags,
        "sprite": f"asset/{MOD_ID}/champions/{cid}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{cid}_skill",
                        f"asset/{MOD_ID}/icons/{cid}_skill2",
                        f"asset/{MOD_ID}/icons/{cid}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": views_b,
    }
    if is_native:
        kit = {"id": cid, "category": category, "tags": tags,
               "passive": {"passive_ref": passive_ref, "params": {}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


# ===========================================================================
# 1. 断誓 (abysspact_oathbreaker) · 上路战士
# ===========================================================================
def build_oathbreaker(p, is_native=True):
    cid = "abysspact_oathbreaker"
    H = mk_helpers(cid)
    burn_ask = H["flag"]("burn_ask", 3) if is_native else None
    plain_oath = None if is_native else H["when"](
        "p_on", H["combine"](),
        H["combine"](H["flag"]("p_on", None),
                     H["flag"]("p_oath", None, attack_mult=p["plain_ad_mult"], attack_speed_mult=p["plain_as_mult"])))

    # Auto: 断剑 (during R adds bonus 40 + 30% AD black-flame strike)
    r_bonus = H["combine"](H["ap_atk"](p["r_onhit_ap"], 0), H["attack"](0, p["r_onhit_ad"]), H["view"]("impact"))
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](plain_oath, H["attack"](0, 100),
                     H["when"]("r_undying", r_bonus),
                     H["sfx"]("a"), H["view"]("impact"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 黑焰斩 — 扇形斩击 + 减速 + 命中敌方英雄回血 + 命中W链目标额外爆发连招
    q_combo = H["when"]("w_chained", H["combine"](H["attack"](p["q_combo_dmg"], p["q_combo_ad"]),
                                                  H["unflag"]("w_chained"), H["view"]("impact")))
    q_hit = [H["attack"](p["q_dmg"], p["q_ad"]),
             H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
             H["view"]("impact"), H["tsfx"]("q_hit")]
    q_champ_heal = [H["heal"](p["q_heal"], ad_ratio=p["q_heal_r"], kind="Caster")]
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            burn_ask,
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_cast"), H["view"]("cleave"))),
            H["delayed"](p["q_hit"] - 1, H["alive_only"](
                H["cone"](p["q_r"], p["q_cone"], q_hit, "EnemyWithoutTower"),
                H["cone"](p["q_r"], p["q_cone"], q_champ_heal, "EnemyChampion"),
                q_combo)),
        ),
    )

    # W: 誓链 — 锁链直飞勾中首个敌方英雄拽回身前 + 定身 0.5s + 挂连招标记
    # 拽不给 tick：拉到他身前为止（给了 tick 近处的人会被拽过头）；定身从勾中算起，盖住拉过来的 w_grab_t（5 万拉到身前
    # 约 13 tick），到了身前还剩 w_bind（以前定身和拽同时开始，拽完只剩 0.3 秒）
    w_hit = [H["attack"](p["w_dmg"], p["w_ad"]),
             {"type": "Grab", "speed": p["w_grab_speed"]},
             H["bind"](p["w_grab_t"] + p["w_bind"]),
             H["flag"]("w_chained", 150),
             H["view"]("impact"), H["tsfx"]("w_pull")]
    w_chain = H["linear"]("w_chain", p["w_speed"], p["w_range"] + 6000, p["w_w"],
                          w_hit, target="EnemyChampion", penetrate=False, y=-8000)
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["combine"](
            burn_ask,
            H["delayed"](p["w_go"] - 1, H["alive_only"](H["sfx"]("w_cast"), w_chain)),
        ),
    )

    # R: 断誓 — 6秒不死 + 40%全能吸血 + 脚下黑火喷发 (Sylas也能完整偷到6秒不死+吸血+爆发!)
    r_buff = H["flag"]("r_undying", p["r_t"], undying=True, vamp=p["r_vamp"], attack_speed_mult=p["r_as"])
    r_burst = H["around"](p["r_burst_r"], [H["attack"](p["r_burst_dmg"], p["r_burst_ad"]),
                                           H["view"]("impact"), H["tsfx"]("q_hit")])
    if is_native:
        # 蛮王的做法：AI 一见敌方英雄就按 R，满血开掉 6 秒不死太浪费。他身上有本包被动挂的 p_self 时，R 只待命 r_arm tick
        # （3 tick 的 idle 动作，看不出放了），oathbreaker.rs 看到生命掉下去才断誓（插剑仰头的大招动作、不死、黑火）；
        # 没有 p_self 的（塞拉斯偷去的 R）当场断誓。
        ult = H["action"](
            "ult", 3, p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
            H["combine"](
                burn_ask,
                H["when"]("p_self", H["flag"]("r_armed", p["r_arm"]),
                          H["combine"](r_buff, H["sfx"]("r_erupt"), H["view"]("footfire"), r_burst)),
            ),
        )
        ult["action_name"] = "idle"
    else:
        ult = H["action"](
            "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
            H["combine"](
                burn_ask,
                H["sfx"]("r_plant"),
                H["delayed"](p["r_go"] - 1, H["alive_only"](
                    r_buff, H["sfx"]("r_erupt"), H["view"]("footfire"), r_burst)),
            ),
        )

    views_p = [H["V_proj"]("w_chain", "chain")]
    views_e = [
        H["V_eff"]("impact", "impact", 2),
        H["V_eff"]("cleave", "cleave", 2),
        H["V_eff"]("footfire", "footfire", -1),
    ]
    views_b = [
        H["V_buf"]("r_undying", "eruption", 2),
        H["V_buf"]("oath_low", "oath_low", 1),
        H["V_buf"]("oath_mid", "oath_mid", 1),
        H["V_buf"]("oath_high", "oath_high", 2),
    ]
    return wrap_kit(cid, "Melee", ["AD", "Melee", "CC", "Heal"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:blood")


# ===========================================================================
# 2. 无面 (abysspact_faceless) · 打野刺客
# ===========================================================================
def build_faceless(p, is_native=True):
    cid = "abysspact_faceless"
    H = mk_helpers(cid)

    # W ambush bonus proc: Fear 0.75s + bonus damage + empty porcelain mask VFX
    ambush_proc = H["combine"](
        H["attack"](p["w_bonus_dmg"], p["w_bonus_ad"]),
        H["fear"](p["w_fear"]),
        H["unflag"]("w_ambush"),
        H["view"]("fear"),
        H["tsfx"]("w_fear"),
    )

    # 夺面后的普攻：射手、法师、辅助类的脸变成飞出去的面具弹，射程由 faceless.rs 的原生效果 `reach`（range_adjust，
    # AI 的射程判断也读它）按类别加长，挂在普攻最后（CombineEffect 取各效果里最大的那个）；攻速由 faceless.rs 调成受害者的快慢
    ranged_bolt = H["homing"]("p_bolt", 8500, [H["attack"](0, 100), H["tsfx"]("a_hit")], target="Enemy", y=-9000)
    cls_auto = H["when"](
        "cls_range", ranged_bolt,
        H["when"]("cls_mage", ranged_bolt,
                  H["when"]("cls_util", ranged_bolt, H["attack"](0, 100))))
    base_hit = cls_auto if is_native else H["attack"](0, 100)

    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](
            base_hit,
            H["when"]("w_ambush", ambush_proc),
            H["sfx"]("a"), H["tsfx"]("a_hit"),
            H["native_fx"](f"{cid}:reach") if is_native else None,
        ),
        atype="BaseAttack", cancel=True,
    )

    # Q: 割影 — 化成黑影穿过目标冲到他身后（RushMoveToBack：冲到目标身后 1.5 万），碰到目标那一下身边 q_rad 内的
    # 敌人都挨刀、减速（以前是固定冲 10 tick × 5600 = 5.6 万，贴脸放会冲出去 4 万多）；隐身突袭连招可触发恐惧
    q_hit = [
        H["attack"](p["q_dmg"], p["q_ad"]),
        H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
        H["when"]("w_ambush", ambush_proc),
        H["tsfx"]("q_pass"),
    ]
    q_rush = {"type": "RushMoveToBack", "speed": p["q_speed"], "applied_effects": [H["around"](p["q_rad"], q_hit)]}
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_dash"), H["view"]("dash"), q_rush)),
        ),
    )

    # W: 无相 — 隐身 1.5s + 移速提升 + 武装下一次出手恐惧 0.75s
    # 武装只到隐身结束（加一次普攻出手的 atk_st：隐身里起手的那一下也算），不再拖到现身 1.5 秒以后
    w_cast = H["combine"](
        H["sfx"]("w_hide"),
        H["view"]("mist"),
        H["search_self"]({"type": "CasterInvisible", "tick": p["w_inv"]}),
        H["flag"]("w_haste", p["w_inv"], move_speed_mult=p["w_ms"]),
        H["flag"]("w_ambush", p["w_inv"] + p["atk_st"]),
    )
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["combine"](
            H["delayed"](p["w_go"] - 1, H["alive_only"](w_cast)),
        ),
    )

    # R: 撕面 — 大黑手按住撕面：高额爆发 + <=25%直接真伤撕死并立刻夺面!
    # 只对己方最近打过的敌方英雄放（EnemyChampionRecentlyAttacked：斩杀不该开在满血的人身上）
    r_exec_ask = H["buff"]("r_exec_ask", 4) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None
    plain_shroud = None if is_native else H["flag"](
        "shroud", p["plain_shroud_t"], attack_mult=p["plain_shroud_ad"], attack_speed_mult=p["plain_shroud_as"])
    r_return = H["homing"]("r_mask", 7500, [H["tsfx"]("r_return")], target="EnemyChampion", y=-9000)
    r_strike = H["combine"](
        H["attack"](p["r_dmg"], p["r_ad"], thp=0 if is_native else p["r_plain_thp"]),
        r_exec_ask,
        plain_shroud,
        H["view"]("grasp"),
        H["tsfx"]("r_grasp"),
        r_return,
    )
    r_main = r_strike
    if is_native:
        # 借来的大招（照塞拉斯附加包按类别偷大招的五套，伤害换成攻击力）：夺面时 faceless.rs 刷新 R 的冷却、挂上受害者的
        # 类别和 r_stolen，这 10 秒里放 R 就是那一类的大招，放过一次 r_stolen 拿掉，下一次回到撕面
        s_slow = H["buff"]("s_slow", 90, move_speed_mult=-40)
        melee_ult = H["combine"](   # 近战：跃到目标身上重砸，一圈眩晕
            H["view"]("dash"),
            H["move_to_target"](6000, 100000, [
                H["view"]("shards"), H["sfx"]("r_grasp"),
                H["around"](24000, [H["attack"](p["s_melee_dmg"], p["s_melee_ad"]), H["stun"](60), H["view"]("grasp")]),
            ]))
        range_ult = H["linear"]("r_lance", 7000, 90000, 9000,   # 射手：一道贯穿的长射，减速
                                [H["attack"](p["s_range_dmg"], p["s_range_ad"]), s_slow, H["view"]("grasp")],
                                target="EnemyWithoutTower", penetrate=True, y=-9000)
        mage_ult = H["lob"]("r_burst", 1, [   # 法师：目标处炸开，击飞
            H["view"]("shards"),
            H["zone"]("r_burst_z", 25000, [H["attack"](p["s_mage_dmg"], p["s_mage_ad"]), H["airborne"](45),
                                           H["view"]("grasp")]),
        ], target="EnemyChampion")
        util_ult = H["combine"](   # 辅助：身边友方英雄回血加盾，敌人挨打减速
            H["view"]("mist"),
            H["around"](45000, [H["heal"](p["s_util_heal"], ad_ratio=30, kind="Ally"),
                                H["shield"](100, ad_ratio=30, tick=180)], target="AllyChampion"),
            H["around"](45000, [H["attack"](p["s_util_dmg"], p["s_util_ad"]), s_slow, H["view"]("grasp")]),
        )
        assassin_ult = H["combine"](   # 刺客：闪到目标身上重击，隐身
            {"type": "Teleport"}, H["view"]("dash"),
            H["attack"](p["s_sin_dmg"], p["s_sin_ad"]), H["view"]("grasp"), H["sfx"]("r_grasp"),
            H["around"](1000, [{"type": "CasterInvisible", "tick": 60}], target="AllyOnlySelf"),
        )
        borrowed = H["when"]("cls_melee", melee_ult,
                             H["when"]("cls_range", range_ult,
                                       H["when"]("cls_mage", mage_ult,
                                                 H["when"]("cls_util", util_ult, assassin_ult))))
        r_main = H["when"]("r_stolen",
                           H["combine"](H["unflag"]("r_stolen"), H["view"]("shards"), H["sfx"]("mask_crack"), borrowed),
                           r_strike)
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
        H["combine"](
            r_voice,
            H["sfx"]("r_grasp"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_main)),
        ),
    )

    views_p = [
        H["V_proj"]("r_mask", "mask_return"),
        H["V_proj"]("p_bolt", "mask_return"),
        H["V_proj"]("r_lance", "mask_return"),
    ]
    views_e = [
        H["V_eff"]("dash", "dash", 2),
        H["V_eff"]("mist", "mist", 2),
        H["V_eff"]("fear", "fear", 3),
        H["V_eff"]("grasp", "grasp", 3),
        H["V_eff"]("shards", "shards", 3),
    ]
    views_b = [
        H["V_buf"]("shroud", "shroud", 1),
        H["V_buf"]("cracks", "cracks", 2),
    ]
    return wrap_kit(cid, "Assassin", ["AD", "Melee", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:mask")


# ===========================================================================
# 3. 呓语 (abysspact_whisperer) · 中路法师
# ===========================================================================
def build_whisperer(p, is_native=True):
    cid = "abysspact_whisperer"
    H = mk_helpers(cid)

    mad1 = H["buff"]("mad_ask1", 4) if is_native else None
    mad3 = H["buff"]("mad_ask3", 4) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None

    # In --plain mode, simulate 3-stack madness burst in data so kd.py reflects passive AoE output
    plain_mad_step = None if is_native else H["when"](
        "pm2",
        H["combine"](H["unflag"]("pm2"), H["unflag"]("pm1"),
                     H["ap_atk"](p["plain_burst_dmg"], p["plain_burst_ap"]),
                     H["fear"](50), H["view"]("burst"), H["tsfx"]("madness_burst")),
        H["when"]("pm1", H["flag"]("pm2", 240), H["flag"]("pm1", 240)),
    )

    # Auto: 念 (飞出念珠)
    a_bead = H["homing"]("a_bead", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_bead),
        atype="BaseAttack", cancel=True,
    )

    # Q: 低语 — 直线穿透紫色低语波 + 叠1层疯狂
    q_hit = [H["ap_atk"](p["q_dmg"], p["q_ap"]), mad1, plain_mad_step, H["view"]("haze"), H["tsfx"]("q_pass")]
    q_line = H["linear"]("q_wave", p["q_speed"], p["q_range"] + 6000, p["q_w"],
                         q_hit, target="EnemyWithoutTower", penetrate=True, y=-10000)
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_cast"), q_line)),
        ),
    )

    # W: 睁眼 — 1-tick lob 锚定目标脚下睁开巨眼3秒：每秒伤+减速+叠1层疯狂
    w_tick = [
        H["ap_atk"](p["w_dmg"], p["w_ap"]),
        H["buff"]("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
        mad1, plain_mad_step,
        H["tsfx"]("w_blink"),
    ]
    w_zone = H["lob"]("w_lob", 1, [
        H["view"]("ground_eye"),
        H["sfx"]("w_open"),
        H["field"]("w_eye", p["w_r"], p["w_t"], p["w_p"], w_tick, first=1, target="EnemyWithoutTower"),
    ], target="EnemyWithoutTower")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["w_go"] - 1, H["alive_only"](w_zone)),
        ),
    )

    # R: 众口 — 1-tick lob 锚定目标处裂开4万半径众口：巨额法伤 + 直接叠满3层集体发狂连锁炸!
    # Also includes data Fear + burst shockwave so Sylas stealing R gets full AoE fear & blast!
    r_hit = [
        H["ap_atk"](p["r_dmg"], p["r_ap"]),
        mad3,
        H["fear"](p["r_fear"]) if not is_native else None,
        H["ap_atk"](p["plain_burst_dmg"], p["plain_burst_ap"]) if not is_native else None,
        H["view"]("burst"),
        H["tsfx"]("madness_burst"),
    ]
    # Give Sylas & native-off clients a reliable fear even without DLL:
    # Actually in native mode, whisperer.rs applies 90-tick Fear + chain explosion on mad_ask3;
    # for Sylas stealing R, Sylas doesn't have WhispererPassive! So put a 45-tick baseline Fear in R directly
    # (in native mode whisperer.rs overlays the full 90-tick Fear + chain burst).
    r_hit_all = [
        H["ap_atk"](p["r_dmg"], p["r_ap"]),
        H["fear"](p["r_fear"]),
        mad3,
        H["ap_atk"](p["plain_burst_dmg"], p["plain_burst_ap"]) if not is_native else None,
        H["view"]("burst"),
        H["tsfx"]("madness_burst"),
    ]
    r_field = H["lob"]("r_lob", 1, [
        H["view"]("mouths"),
        H["sfx"]("r_pulse"),
        H["zone"]("r_mouths", p["r_r"], r_hit_all, target="EnemyWithoutTower"),
    ], target="EnemyChampion")
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_open"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_field)),
        ),
    )

    views_p = [
        H["V_proj"]("a_bead", "bead"),
        H["V_proj"]("q_wave", "whisper"),
    ]
    views_e = [
        H["V_eff"]("haze", "haze", 2),
        H["V_eff"]("burst", "burst", 3),
        H["V_eff"]("ground_eye", "ground_eye", -1, follow=False),
        H["V_eff"]("mouths", "mouths", -1, follow=False),
    ]
    views_b = [
        H["V_buf"]("madness_1", "madness_1", 3),
        H["V_buf"]("madness_2", "madness_2", 3),
        H["V_buf"]("madness_3", "madness_3", 3),
        H["V_buf"]("mad_runes", "runes", 3),
    ]
    return wrap_kit(cid, "Magician", ["AP", "Magic", "Range", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:madness")


# ===========================================================================
# 4. 骸弦 (abysspact_bonebow) · 下路射手
# ===========================================================================
def build_bonebow(p, is_native=True):
    cid = "abysspact_bonebow"
    H = mk_helpers(cid)

    # In --plain mode, every 4th auto triggers a bonus bone-soldier volley approximating skeleton DPS
    plain_4th = None if is_native else H["when"](
        "s3",
        H["combine"](H["unflag"]("s3"), H["unflag"]("s2"), H["unflag"]("s1"),
                     H["attack"](p["plain_p_dmg"], p["plain_p_ad"]), H["view"]("soul")),
        H["when"]("s2", H["flag"]("s3", 600),
                  H["when"]("s1", H["flag"]("s2", 600), H["flag"]("s1", 600))),
    )

    # Auto: 骨箭（打中时给她挂 a_arrow：bonebow.rs 按箭数，第 4 支拉起骷髅兵）
    a_proj = H["homing"]("a_arrow", p["a_speed"],
                         [H["attack"](0, 100), plain_4th, H["view"]("soul"), H["tsfx"]("a_hit"),
                          H["flag"]("a_arrow", 2) if is_native else None],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_proj),
        atype="BaseAttack", cancel=True,
    )

    # Q: 穿骨 — 直线穿透骨箭 + 每命中一名敌方英雄在其脚下爬出1名真实骷髅兵
    q_hit = [H["attack"](p["q_dmg"], p["q_ad"]), H["view"]("pierce_flash"), H["tsfx"]("q_hit")]
    q_champ_spawn = [H["buff"]("q_hit_ask", 4)] if is_native else [H["attack"](p["plain_p_dmg"], p["plain_p_ad"])]
    q_line = H["combine"](
        H["linear"]("q_piercer", p["q_speed"], p["q_range"] + 6000, p["q_w"],
                    q_hit, target="EnemyWithoutTower", penetrate=True, y=p["a_y"]),
        H["linear"]("q_raise", p["q_speed"], p["q_range"] + 6000, p["q_w"],
                    q_champ_spawn, target="EnemyChampion", penetrate=True, y=p["a_y"]),
    )
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["sfx"]("q_draw"),
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_release"), q_line,
                                                        H["flag"]("q_arrow", 3) if is_native else None)),
        ),
    )

    # W: 葬礼 — 命令所有活着的骷髅兵冲向目标并自爆 (+ 保底骨片炸圈确保无兵或连招时稳定生效)
    w_dmg = p["w_base_dmg"] if is_native else p["w_plain_dmg"]
    w_ad = p["w_base_ad"] if is_native else p["w_plain_ad"]
    w_blast = H["lob"]("w_lob", 1, [
        H["view"]("bone_burst"),
        H["sfx"]("funeral_burst"),
        H["zone"]("w_zone", p["w_r"], [
            H["attack"](w_dmg, w_ad),
            H["buff"]("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
            H["view"]("soul"),
        ], target="EnemyWithoutTower"),
    ], target="EnemyWithoutTower")
    # 只对敌方英雄放：骷髅兵是攒来炸人的，不该冲去炸一线小兵
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["combine"](
            H["buff"]("w_mark", 18) if is_native else None,
            H["delayed"](p["w_go"] - 1, H["alive_only"](
                H["flag"]("w_cmd", 4) if is_native else None,
                w_blast)),
        ),
    )

    # R: 亡军 — 朝天射箭，落下一片3.5万半径骨箭雨 + 地里爬出5个骷髅兵活8秒!
    # Also spawns a 4-tick follow-up arrow barrage in data when --plain or stolen by Sylas
    # 一次大招一批：放的时候给目标挂 r_aim（记下落点），箭射出去时给她挂 r_ask，bonebow.rs 在箭雨落地那一 tick
    # 在目标处拉起 5 个（以前箭雨打中的每个敌人身上也挂 r_ask，每个都拉一批）
    r_aim = H["buff"]("r_aim", 40) if is_native else None
    r_ask_self = H["flag"]("r_ask", 6) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None
    r_rain_hit = [
        H["attack"](p["r_dmg"], p["r_ad"]),
        H["buff"]("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
        H["view"]("soul"),
        H["tsfx"]("a_hit"),
    ]
    r_follow = H["field"]("r_barrage", p["r_r"], p["r_plain_t"], p["r_plain_p"], [
        H["attack"](p["r_plain_tick_dmg"], p["r_plain_tick_ad"]),
        H["view"]("soul"),
    ], first=p["r_plain_p"], target="EnemyWithoutTower") if not is_native else None
    r_lob = H["lob"]("r_lob", p["r_travel"], [
        H["view"]("rain"),
        H["view"]("army_ring"),
        H["sfx"]("r_rain"),
        H["zone"]("r_zone", p["r_r"], r_rain_hit, target="EnemyWithoutTower"),
        r_follow,
    ], target="EnemyChampion")
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            r_aim,
            H["sfx"]("r_launch"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_ask_self, r_lob)),
        ),
    )

    views_p = [
        H["V_proj"]("a_arrow", "arrow"),
        H["V_proj"]("q_piercer", "piercer"),
    ]
    views_e = [
        H["V_eff"]("soul", "soul", 2),
        H["V_eff"]("pierce_flash", "pierce_flash", 2),
        H["V_eff"]("crypt", "crypt", 1, follow=False),
        H["V_eff"]("bone_burst", "bone_burst", 3, follow=False),
        H["V_eff"]("rain", "rain", 3, follow=False),
        H["V_eff"]("army_ring", "army_ring", -1, follow=False),
    ]
    views_b = []
    return wrap_kit(cid, "Range", ["AD", "Range"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:skeletons")


# ===========================================================================
# 5. 鸦医 (abysspact_corvus) · 辅助
# ===========================================================================
def build_corvus(p, is_native=True):
    cid = "abysspact_corvus"
    H = mk_helpers(cid)

    plague_ask = H["buff"]("plague_ask", 4) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None

    # Auto: 药瓶
    a_vial = H["homing"]("a_vial", p["a_speed"],
                         [H["attack"](0, 100), H["view"]("break"), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_vial),
        atype="BaseAttack", cancel=True,
    )

    # Q: 瘴瓶 — 抛投大瘴气瓶，2万内造成法伤+减速30% 1.5s+全部染病!
    q_hit = [
        H["ap_atk"](p["q_dmg"], p["q_ap"]),
        H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
        plague_ask,
        H["view"]("break"),
    ]
    q_plain_dot = H["field"]("q_dot", p["q_r"], 240, 60, [
        H["ap_atk"](p["q_plain_dot"], p["q_plain_dot_ap"]),
    ], first=60, target="EnemyWithoutTower") if not is_native else None
    q_plain_heal = H["field"]("q_heal", p["q_r"] + 6000, 180, 60, [
        H["heal"](p["q_plain_heal"], ap_ratio=10, kind="Ally"),
    ], first=60, target="AllyChampion") if not is_native else None
    q_lob = H["lob"]("q_vial", p["q_travel"], [
        H["view"]("miasma"),
        H["sfx"]("q_ring"),
        H["zone"]("q_zone", p["q_r"], q_hit, target="EnemyWithoutTower"),
        q_plain_dot, q_plain_heal,
    ], target="EnemyWithoutTower")
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_cast"), q_lob)),
        ),
    )

    # W: 渡鸦 — 肩上乌鸦飞向队友停4秒：护盾 + 肩头乌鸦贴图 + 每秒自动啄击附近敌人染病
    w_plain_peel = H["lob"]("w_peel", 1, [
        H["zone"]("w_peck_z", p["w_plain_r"], [
            H["ap_atk"](p["w_plain_dmg"], p["w_plain_ap"]),
            H["buff"]("w_slow", 60, move_speed_mult=-20),
        ], target="EnemyWithoutTower"),
    ], target="AllyChampion") if not is_native else None
    w_land = [
        H["shield"](p["w_sh"], ap_ratio=p["w_sh_ap"], tick=p["w_t"]),
        H["buff"]("raven_perch", p["w_t"]),
        H["view"]("shield"),
        H["tsfx"]("w_wing"),
        w_plain_peel,
    ]
    w_raven = H["homing"]("w_raven", p["w_speed"], w_land, target="AllyChampion", y=-12000)
    # 珍娜 E 的做法：护盾放在友方身上，AI 冷却一好就放（多半放给自己、满血、身边没人）。现在等敌方英雄进到 w_range 才放
    # （None + EnemyChampion），乌鸦飞向他身边 w_ally_r 内随便一名友方英雄；身边没有队友才停在自己肩上
    w_self = H["around"](1000, [
        H["shield"](p["w_sh"], ap_ratio=p["w_sh_ap"], tick=p["w_t"]),
        H["buff"]("raven_perch", p["w_t"]),
        H["view"]("shield"),
        H["tsfx"]("w_wing"),
        w_plain_peel,
    ], target="AllyOnlySelf")
    w_cast = H["combine"](
        H["sfx"]("w_cast"),
        H["rand_target"](p["w_ally_r"], "AllyNotSelf", H["flag"]("w_lock", 3), w_raven),
        H["delayed"](1, H["when"]("w_lock", H["unflag"]("w_lock"), w_self)),
    )
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "None", "EnemyChampion",
        H["combine"](
            H["delayed"](p["w_go"] - 1, H["alive_only"](w_cast)),
        ),
    )

    # R: 隔离区 — 拐杖画4万半径粉笔圈5秒：落地瞬晕0.75s+开场瘴伤，每秒圈内敌人染病减速40%、队友回血!
    r_open_hit = [
        H["ap_atk"](p["r_init_dmg"], p["r_init_ap"]),
        H["stun"](p["r_stun"]),
        plague_ask,
        H["view"]("break"),
    ]
    r_enemy_tick = [
        H["ap_atk"](p["r_tick_dmg"], p["r_tick_ap"]),
        H["buff"]("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
        plague_ask,
    ]
    r_ally_tick = [
        H["heal"](p["r_heal"], ap_ratio=p["r_heal_ap"], kind="Ally"),
        H["view"]("heal"),
    ]
    r_lob = H["lob"]("r_lob", 1, [
        H["view"]("quarantine"),
        H["sfx"]("r_cast"),
        H["zone"]("r_stun_z", p["r_r"], r_open_hit, target="EnemyWithoutTower"),
        H["field"]("r_foe_f", p["r_r"], p["r_t"], p["r_p"], r_enemy_tick, first=p["r_p"], target="EnemyWithoutTower"),
        H["field"]("r_ally_f", p["r_r"], p["r_t"], p["r_p"], r_ally_tick, first=1, target="AllyChampion"),
    ], target="EnemyChampion")
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_cane"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_lob)),
        ),
    )

    views_p = [
        H["V_proj"]("a_vial", "vial"),
        H["V_proj"]("q_vial", "vial"),
        H["V_proj"]("w_raven", "raven_fly"),
    ]
    views_e = [
        H["V_eff"]("break", "break", 2),
        H["V_eff"]("miasma", "miasma", -1, follow=False),
        H["V_eff"]("transmit", "transmit", 2),
        H["V_eff"]("heal", "heal", 2),
        H["V_eff"]("shield", "shield", 2),
        H["V_eff"]("quarantine", "quarantine", -1, follow=False),
    ]
    views_b = [
        H["V_buf"]("plague", "bubbles", 2),
        H["V_buf"]("raven_perch", "raven_perch", 3),
    ]
    return wrap_kit(cid, "Util", ["AP", "Magic", "Heal", "Shield", "Dot", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:plague")


# ===========================================================================
# 6. 血月 (abysspact_bloodmoon) · 上路战士 · 月相双形态
# ===========================================================================
def build_bloodmoon(p, is_native=True):
    cid = "abysspact_bloodmoon"
    H = mk_helpers(cid)

    r_voice = H["flag"]("r_voice", 4) if is_native else None

    # Auto: 人形远程银弩 / 狼形近战撕咬 (巨狼期间在 --plain 模式下模拟 1.5万 顺劈)
    human_auto = H["combine"](
        H["sfx"]("a_silver"),
        H["homing"]("a_silver", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_silver_hit")],
                    target="Enemy", y=p["a_y"]),
    )
    plain_giant_cleave = None if is_native else H["when"](
        "giant", H["around"](15000, [H["attack"](0, p["plain_cleave_ad"]), H["view"]("giant_claw")]))
    wolf_auto = H["combine"](
        H["attack"](0, 100),
        plain_giant_cleave,
        H["sfx"]("a_wolf"),
        H["view"]("pounce"),
        H["tsfx"]("pounce_hit"),
    )
    # 射程按狼形近战算；人形的银弩由 human_range（官方 range_adjust，放在最外层 Combine 的最后）再加 1.9 万。
    # --plain 跑不了原生代码，射程直接按人形算。
    atk_range = p["atk_range"] if is_native else p["atk_range"] + p["human_range"]
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], atk_range, "Targeting", "Enemy",
        H["combine"](
            H["when"]("wolf", wolf_auto, H["when"]("giant", wolf_auto, human_auto)),
            H["native_fx"](f"{cid}:human_range") if is_native else None,
        ),
        atype="BaseAttack", cancel=True,
    )

    # Q: 人形「银矢」三连穿透银箭减速 / 狼形「扑杀」突进撕咬回血
    q_silver_hit = [
        H["attack"](p["q_h_dmg"], p["q_h_ad"]),
        H["buff"]("q_slow", p["q_h_slow_t"], move_speed_mult=-p["q_h_slow"]),
        H["view"]("silver"),
        H["tsfx"]("a_silver_hit"),
    ]
    q_bolt = H["linear"]("q_silver", p["q_speed"], p["q_range"] + 4000, p["q_w"],
                         q_silver_hit, target="EnemyWithoutTower", penetrate=True, y=p["a_y"])
    q_human = H["combine"](
        H["sfx"]("q_silver_volley"),
        q_bolt,
        H["delayed"](5, H["alive_only"](q_bolt)),
        H["delayed"](10, H["alive_only"](q_bolt)),
    )
    q_wolf = H["combine"](
        H["sfx"]("q_pounce"),
        H["move_to_target"](5800, p["q_range"], [
            H["attack"](p["q_w_dmg"], p["q_w_ad"]),
            H["heal"](p["q_w_heal"], ad_ratio=p["q_w_heal_ad"], kind="Caster"),
            H["view"]("fang_flash"),
            H["view"]("pounce"),
            H["tsfx"]("pounce_hit"),
        ]),
    )
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](
            H["when"]("wolf", q_wolf, H["when"]("giant", q_wolf, q_human)))),
    )

    # W: 「变身」人<->狼随时切换 (人变狼: 嚎叫3万减速30% 1s; 狼变人: 后翻1.5万)
    to_wolf = H["combine"](
        H["flag"]("wolf", None, attack_speed_mult=p["wolf_as"], vamp=p["wolf_vamp"]),
        H["view"]("transform"),
        H["view"]("howl"),
        H["sfx"]("w_transform"),
        H["around"](p["w_slow_r"], [H["buff"]("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"])]),
    )
    to_human = H["combine"](
        H["unflag"]("wolf"),
        H["view"]("transform"),
        H["view"]("rollback"),
        H["sfx"]("w_rollback"),
        H["move_back"](p["w_back_spd"], p["w_back_t"]),
    )
    # 巨狼期间不变身：身体还是巨狼，播一声狼嚎（狼形的大招动作）、照样把身边的人吓慢，不切形态。
    # 动作要在出手那一刻就换（变身动作会被显示钩子换成狼形的「变回人」），所以分支放在最前面。
    giant_howl = H["combine"](
        H["view"]("howl"),
        H["sfx"]("r_howl"),
        H["around"](p["w_slow_r"], [H["buff"]("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"])]),
    )
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["combine"](
            H["when"]("giant", {"type": "CasterAnimation", "name": "wf_ult", "tick": p["w_dur"]}),
            H["delayed"](p["w_go"] - 1, H["alive_only"](
                H["when"]("giant", giant_howl, H["when"]("wolf", to_human, to_wolf)))),
        ),
    )

    # R: 「血月」血月升起化身1.3倍巨狼8秒 (减伤25% + 狼形攻速吸血 + 3万群体恐惧1s + 顺劈)
    # 塞拉斯偷大也能获得8秒血月头顶光环、减伤25%、攻速吸血加成与3万群体恐惧长嚎!
    r_howl_hit = [
        H["attack"](p["r_dmg"], p["r_ad"]),
        H["fear"](p["r_fear"]),
        H["view"]("giant_claw"),
        H["tsfx"]("pounce_hit"),
    ]
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_moon"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                # 已经是狼形就不再挂一层（同名的 buff 会叠，攻速、吸血翻倍）
                H["when"]("wolf", None,
                          H["flag"]("wolf", None, attack_speed_mult=p["wolf_as"], vamp=p["wolf_vamp"])),
                H["flag"]("giant", p["r_t"], damaged_reduce=p["r_dr"]),
                H["view"]("transform"),
                H["view"]("howl"),
                H["sfx"]("r_howl"),
                H["around"](p["r_howl_r"], r_howl_hit, target="EnemyWithoutTower"),
            )),
        ),
    )

    views_p = [
        H["V_proj"]("a_silver", "silver"),
        H["V_proj"]("q_silver", "silver"),
    ]
    views_e = [
        H["V_eff"]("silver", "silver", 2),
        H["V_eff"]("pounce", "pounce", 2),
        H["V_eff"]("transform", "transform", 2),
        H["V_eff"]("howl", "howl", 2),
        H["V_eff"]("giant_claw", "giant_claw", 3),
        H["V_eff"]("rollback", "rollback", 2),
        H["V_eff"]("fang_flash", "fang_flash", 2),
    ]
    views_b = [
        H["V_buf"]("giant", "moon", 3),
    ]
    return wrap_kit(cid, "Melee", ["AD", "Melee", "CC", "Heal"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:phases")


# ===========================================================================
# 7. 入殓 (abysspact_undertaker) · 打野坦克 · 棺盾与扛棺绑架
# ===========================================================================
def build_undertaker(p, is_native=True):
    cid = "abysspact_undertaker"
    H = mk_helpers(cid)

    r_voice = H["flag"]("r_voice", 4) if is_native else None
    plain_shield = None if is_native else H["when"](
        "p_on", H["combine"](),
        H["combine"](
            H["flag"]("p_on", None),
            H["flag"]("p_coffin", None, base_attack_damaged_reduce=15, skill_damaged_reduce=10),
        ),
    )

    # Auto: 棺砸
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](plain_shield, H["attack"](0, 100), H["sfx"]("a"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 落葬 — 前方扇形2.5万砸地: 60 + 6%最大生命 + 击飞0.5秒
    q_hit = [
        H["attack"](p["q_dmg"], 0, hp_ratio=p["q_hp"]),
        H["airborne"](p["q_air"]),
        H["tsfx"]("q_crack"),
    ]
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_cast"), H["view"]("dust"), H["view"]("cracks"))),
            H["delayed"](p["q_hit"] - 1, H["alive_only"](
                H["cone"](p["q_r"], p["q_cone"], q_hit, "EnemyWithoutTower"))),
        ),
    )

    # W: 送行 — 铁链甩棺钉地并把自己拽过去，棺材立3秒周围2万减速40%
    w_chain_vis = H["linear"]("w_chain", p["w_speed"], p["w_range"] + 4000, p["w_w"],
                              [H["attack"](p["w_dmg"], p["w_ad"]), H["tsfx"]("w_anchor")],
                              target="EnemyWithoutTower", penetrate=False, y=-8000)
    w_coffin_zone = H["lob"]("w_lob", 1, [
        H["view"]("coffin"),
        H["sfx"]("w_anchor"),
        H["field"]("w_field", p["w_r"], p["w_t"], p["w_p"], [
            H["buff"]("w_slow", p["w_slow_t"], move_speed_mult=-p["w_slow"]),
        ], first=1, target="EnemyWithoutTower"),
    ], target="EnemyWithoutTower")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["w_go"] - 1, H["alive_only"](
            H["sfx"]("w_chain"),
            w_chain_vis,
            H["move_to_target"](5400, p["w_range"], [w_coffin_zone]),
        )),
    )

    # R: 入殓 — 把敌方英雄塞进棺材扛走2秒(+20%移速)，再摔出 150 + 8%目标最大生命 + 眩晕1秒!
    # 原生版（他身上有 coffin_shield）：数据只关棺、定住、挂 coffin_ask；undertaker.rs 把人放逐进棺材（看不见、选不中），
    # 给他自己挂 carrying（+20% 移速，棺缝里挣扎的影子画在他身上），扛着往自己人那边走，2 秒后摔到他身前。
    # 塞拉斯偷大 / --plain（没有 coffin_shield）：数据版拽过来、挂 carrying、1 秒后摔。
    r_coffin_ask = H["buff"]("coffin_ask", 4) if is_native else None
    r_fallback = H["when"](
        "coffin_shield", H["combine"](),
        H["combine"](
            H["grab"](3000, 12),
            H["buff"]("in_coffin", p["r_carry_t"]),
            H["flag"]("carrying", p["r_carry_t"], move_speed_mult=p["r_ms"]),
            H["delayed"](60, H["alive_only"](
                H["attack"](p["r_slam_dmg"], 0, thp=p["r_slam_thp"]),
                H["stun"](p["r_stun"]),
                H["view"]("drop"),
                H["tsfx"]("coffin_drop"),
            )),
        ),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_open"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                H["view"]("close"),
                H["stun"](p["r_stun"]),
                r_coffin_ask,
                r_fallback,
            )),
        ),
    )

    views_p = [H["V_proj"]("w_chain", "chain")]
    views_e = [
        H["V_eff"]("dust", "dust", -1, follow=False),
        H["V_eff"]("cracks", "cracks", -1, follow=False),
        # 棺材立 3 秒：图集里最后一帧（立着的棺材）停到 3 秒（abysspact_undertaker_fx#anim.fanim）
        H["V_eff"]("coffin", "coffin", 1, follow=False),
        H["V_eff"]("close", "close", 3),
        H["V_eff"]("drop", "drop", 3),
        H["V_eff"]("guard", "guard", 2),
    ]
    views_b = [
        H["V_buf"]("in_coffin", "struggle", 3),
        H["V_buf"]("carrying", "struggle", 3),
    ]
    # Note: sim3.exe 0.5.1 (--plain) does not recognize "Tank"; native uses "Tank"!
    cat = "Tank" if is_native else "Melee"
    return wrap_kit(cid, cat, ["Tank", "Melee", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:coffin")


# ===========================================================================
# 8. 替身 (abysspact_effigy) · 中路法师 · 扎针、同命线与拆线
# ===========================================================================
def build_effigy(p, is_native=True):
    cid = "abysspact_effigy"
    H = mk_helpers(cid)

    needle_ask = H["buff"]("needle_ask", 4) if is_native else None
    link_ask = H["buff"]("link_ask", 4) if is_native else None
    unpick_ask = H["flag"]("unpick_ask", 4) if is_native else None
    r_voice = H["flag"]("r_voice", 4) if is_native else None

    # Auto: 飞针
    a_proj = H["homing"]("a_needle", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_proj),
        atype="BaseAttack", cancel=True,
    )

    # Q: 缝 — 扇形甩出五根银针：扇形针雨 + 中心穿透针，减速25% 1秒并扎针!
    q_cone_hit = [
        H["ap_atk"](p["q_dmg"], p["q_ap"]),
        H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
        needle_ask,
        H["view"]("embedded"),
        H["tsfx"]("q_hit"),
    ]
    q_center_hit = [
        H["ap_atk"](p["q_bolt_dmg"], p["q_bolt_ap"]),
        needle_ask,
        H["tsfx"]("q_hit"),
    ]
    q_center = H["linear"]("q_needle", p["q_speed"], p["q_range"] + 4000, p["q_w"],
                           q_center_hit, target="EnemyWithoutTower", penetrate=True, y=p["a_y"])
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](
            H["sfx"]("q_fan"),
            H["view"]("fan"),
            H["cone"](p["q_range"], p["q_cone"], q_cone_hit, "EnemyWithoutTower"),
            q_center,
        )),
    )

    # W: 同命线 — 红线连起目标与4.5万内最近另一名敌方英雄4秒 (40%伤害互传，拉断双晕1s+80+50%AP)
    w_plain_link = None if is_native else H["lob"]("w_lob", 1, [
        H["view"]("snap"),
        H["zone"]("w_snap_z", p["w_plain_r"], [
            H["ap_atk"](p["w_plain_dmg"], p["w_plain_ap"]),
            H["stun"](p["w_plain_stun"]),
        ], target="EnemyChampion"),
    ], target="EnemyChampion")
    # 原生版的线团只在真连上两个人时由 effigy.rs 挂（一边一个），数据不再先挂一个
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["delayed"](p["w_go"] - 1, H["alive_only"](
            H["sfx"]("w_throw"),
            H["view"]("line"),
            H["ap_atk"](p["w_dmg"], p["w_ap"]),
            None if is_native else H["buff"]("knot", p["w_t"]),
            needle_ask,
            link_ask,
            H["tsfx"]("w_taut"),
            w_plain_link,
        )),
    )

    # R: 拆线 — 扯出7万内所有敌人身上的银针!
    # Native 走 effigy.rs 全图拔针每根 90+45%AP（针从每个人身上拖着红线飞回她手里）; 塞拉斯偷大 / --plain(无 native 标记)
    # 触发大范围拆线爆发+减速50%! 只对最近被己方打过的敌方英雄按（身上多半插着针）。
    r_return_proj = None if is_native else H["homing"](
        "r_return", 7800, [H["view"]("return"), H["tsfx"]("unpick_return")], target="EnemyChampion", y=p["a_y"])
    r_non_native = H["when"](
        "native", H["combine"](),
        H["lob"]("r_lob", 1, [
            H["view"]("withdraw"),
            H["zone"]("r_zone", p["r_r"], [
                H["ap_atk"](p["r_dmg"], p["r_ap"]),
                H["buff"]("r_slow", p["r_slow_t"], move_speed_mult=-p["r_slow"]),
                H["view"]("withdraw"),
                H["tsfx"]("unpick_return"),
            ], target="EnemyWithoutTower"),
        ], target="EnemyChampion"),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampionRecentlyAttacked",
        H["combine"](
            r_voice,
            H["sfx"]("r_unpick"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                unpick_ask,
                r_return_proj,
                r_non_native,
            )),
        ),
    )

    views_p = [
        H["V_proj"]("a_needle", "needle"),
        H["V_proj"]("q_needle", "needle"),
        H["V_proj"]("r_return", "return"),
        # 同命线的红线：特效图集里的红绳，effigy.rs 每 tick 在两人中间放一段（弹道图跟着方向转）
        {"type": "Animated", "name": H["n"]("thread"), "anim": f"asset/{MOD_ID}/effects/{cid}_fx",
         "tag": "line", "repeat": True, "z": 2},
    ]
    views_e = [
        H["V_eff"]("fan", "fan", 2),
        H["V_eff"]("line", "line", 2),
        H["V_eff"]("snap", "snap", 3),
        H["V_eff"]("embedded", "embedded", 2),
        H["V_eff"]("withdraw", "withdraw", 3),
        H["V_eff"]("return", "return", 2),
    ]
    views_b = [
        H["V_buf"]("needles_1", "needles_1", 3),
        H["V_buf"]("needles_2", "needles_2", 3),
        H["V_buf"]("needles_3", "needles_3", 3),
        H["V_buf"]("knot", "knot", 3),
    ]
    return wrap_kit(cid, "Magician", ["AP", "Magic", "Range", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:needles")


# ===========================================================================
# 9. 七弹 (abysspact_sevenfold) · 下路射手 · 第七颗深渊魔弹
# ===========================================================================
def build_sevenfold(p, is_native=True):
    cid = "abysspact_sevenfold"
    H = mk_helpers(cid)

    r_voice = H["flag"]("r_voice", 4) if is_native else None
    q_shots_ask = H["flag"]("q_shots", 4) if is_native else None
    w_load_ask = H["flag"]("w_load", 4) if is_native else None

    # 第七颗深渊魔弹（普攻的第七发、R 的最后一发、--plain 的计数、塞拉斯偷大都走这一份）：
    # 身后睁开深渊之眼，9 万内随机一个敌方英雄，追踪弹拐着弯飞过去，真实伤害。
    curse_shot_data = H["combine"](
        {"type": "CasterViewEffect", "name": H["n"]("abyss_eye")},
        H["sfx"]("abyss_eye"),
        H["sfx"]("r_curse_launch"),
        H["rand_target"](p["p_range"], "EnemyChampion",
                         H["homing"]("r_curse", 8800, [
                             H["fixed"](p["p_true_dmg"], p["p_true_ad"]),
                             H["view"]("curse_hit"),
                             H["tsfx"]("curse_burst"),
                         ], target="EnemyChampion", y=p["a_y"])),
    )

    # In --plain mode, track 6 shots -> 7th fires true-damage Abyss Bullet + 1.2s reload pause!
    plain_step = None if is_native else H["when"](
        "c6",
        H["combine"](H["unflag"]("c6"), H["unflag"]("c5"), H["unflag"]("c4"),
                     H["unflag"]("c3"), H["unflag"]("c2"), H["unflag"]("c1"),
                     H["flag"]("plain_reload", 72, attack_speed_mult=-70),
                     curse_shot_data),
        H["when"]("c5", H["flag"]("c6", 900),
                  H["when"]("c4", H["flag"]("c5", 900),
                            H["when"]("c3", H["flag"]("c4", 900),
                                      H["when"]("c2", H["flag"]("c3", 900),
                                                H["when"]("c1", H["flag"]("c2", 900),
                                                          H["flag"]("c1", 900)))))),
    )

    # Auto: 魔弹枪
    a_proj = H["homing"]("a_round", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    normal_shot = H["combine"](H["sfx"]("a"), H["view"]("recoil"), a_proj, plain_step)
    if is_native:
        # 原生版：sevenfold.rs 数普攻，轮到第七发时给他挂 seventh。这一发不打瞄的人，换成深渊魔弹，
        # 挂 fired7 让 sevenfold.rs 扣 8% 当前生命、装弹 1.2 秒。
        # 魔弹的伤害在随机目标的弹道里，AI 读不到；先放一个它读得到、出手时跳过的伤害（gangplank 的 decoy），
        # 不然 AI 的对战计划按普攻伤害做除法会除以零。
        decoy = H["combine"](
            H["flag"]("x7", 1),
            H["when"]("x7", H["unflag"]("x7"), H["attack"](p["p_true_dmg"], p["p_true_ad"])),
            H["unflag"]("x7"),
        )
        seventh_shot = H["combine"](H["unflag"]("seventh"), H["flag"]("fired7", 4), decoy, curse_shot_data)
        attack_eff = H["when"]("seventh", seventh_shot, normal_shot)
    else:
        attack_eff = normal_shot
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        attack_eff, atype="BaseAttack", cancel=True,
    )

    # Q: 连发 — 一口气连开三枪 (算3颗子弹加快轮到第七颗)
    q_shot = H["homing"]("q_round", p["a_speed"], [H["attack"](p["q_dmg"], p["q_ad"]), H["tsfx"]("a_hit")],
                         target="EnemyWithoutTower", y=p["a_y"])
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](
                H["sfx"]("q_triple"), H["view"]("burst"), q_shots_ask, q_shot, plain_step)),
            H["delayed"](p["q_go"] + 5, H["alive_only"](q_shot, plain_step)),
            H["delayed"](p["q_go"] + 11, H["alive_only"](q_shot, plain_step)),
        ),
    )

    # W: 装弹 — 后翻1.8万，顺手把下一发换成第七颗深渊魔弹!
    w_plain_prime = None if is_native else H["flag"]("c6", 900)
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["delayed"](p["w_go"] - 1, H["alive_only"](
            H["sfx"]("w_roll"),
            H["view"]("reload"),
            H["move_back"](p["w_back_spd"], p["w_back_t"]),
            w_load_ask,
            w_plain_prime,
        )),
    )

    # R: 七发齐射 — 前6发各自找敌人射击 + 第7发必为深渊拐弯真伤魔弹!
    # 第七发和普攻的第七发同一份数据；原生版另挂 r_fired7 让 sevenfold.rs 扣 8% 当前生命（R 不装弹、不动弹仓计数）。
    r_single = H["rand_target"](p["r_range"], "EnemyWithoutTower",
                                H["homing"]("r_round", p["a_speed"], [
                                    H["attack"](p["r_dmg"], p["r_ad"]),
                                    H["tsfx"]("a_hit"),
                                ], target="EnemyWithoutTower", y=p["a_y"]))
    r_seventh = H["combine"](H["flag"]("r_fired7", 4) if is_native else None, curse_shot_data)
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](H["sfx"]("r_salvo"), H["view"]("salvo"), r_single)),
            H["delayed"](p["r_go"] + 3, H["alive_only"](r_single)),
            H["delayed"](p["r_go"] + 7, H["alive_only"](r_single)),
            H["delayed"](p["r_go"] + 11, H["alive_only"](r_single)),
            H["delayed"](p["r_go"] + 15, H["alive_only"](r_single)),
            H["delayed"](p["r_go"] + 19, H["alive_only"](r_single)),
            H["delayed"](p["r_go"] + 23, H["alive_only"](r_seventh)),
        ),
    )

    views_p = [
        H["V_proj"]("a_round", "round"),
        H["V_proj"]("q_round", "round"),
        H["V_proj"]("r_round", "round"),
        H["V_proj"]("r_curse", "curse"),
    ]
    views_e = [
        H["V_eff"]("recoil", "recoil", 2),
        H["V_eff"]("burst", "burst", 2),
        H["V_eff"]("salvo", "salvo", 2),
        H["V_eff"]("reload", "reload", 2),
        H["V_eff"]("abyss_eye", "abyss_eye", 3),
        H["V_eff"]("curse_hit", "curse_hit", 3),
    ]
    views_b = [H["V_buf"](f"count_{k}", f"count_{k}", 3) for k in range(8)]
    return wrap_kit(cid, "Range", ["AD", "Range"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:bullets")


# ===========================================================================
# 10. 烛灵 (abysspact_vesper) · 辅助 · 烛冠增幅与回魂复活
# ===========================================================================
def build_vesper(p, is_native=True):
    cid = "abysspact_vesper"
    H = mk_helpers(cid)

    r_ask = H["flag"]("r_ask", 4) if is_native else None

    # Auto: 鬼火
    a_proj = H["homing"]("a_wisp", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_proj),
        atype="BaseAttack", cancel=True,
    )

    # Q: 引路 — 鬼火连队友3秒: 移速+25%、每秒回复30+20%AP、结束赋予50+40%AP护盾
    q_tick_heal = H["combine"](H["heal"](p["q_heal"], ap_ratio=p["q_heal_ap"], kind="Ally"),
                               H["view"]("warmth"), H["tsfx"]("q_heal"))
    q_end_shield = H["combine"](H["shield"](p["q_sh"], ap_ratio=p["q_sh_ap"], tick=p["q_sh_t"]),
                                H["view"]("shield"), H["tsfx"]("warm_shield"))
    q_land = [
        H["buff"]("guide", p["q_t"], move_speed_mult=p["q_ms"]),
        q_tick_heal,
        H["delayed"](60, q_tick_heal),
        H["delayed"](120, q_tick_heal),
        H["delayed"](p["q_t"], q_end_shield),
    ]
    # 设计是「连到一个队友身上」：不给自己放（AllyNotSelf）
    q_wisp = H["homing"]("q_wisp", 8000, q_land, target="AllyNotSelf", y=p["a_y"])
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "AllyNotSelf",
        H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_link"), q_wisp)),
    )

    # W: 惊魂 — 直线5万尖叫亡魂穿透恐惧0.75秒 + 40+40%AP魔法伤害
    w_hit = [
        H["ap_atk"](p["w_dmg"], p["w_ap"]),
        H["fear"](p["w_fear"]),
        H["view"]("scream"),
        H["tsfx"]("w_fade"),
    ]
    w_proj = H["linear"]("w_scream", p["w_speed"], p["w_range"] + 4000, p["w_w"],
                         w_hit, target="EnemyWithoutTower", penetrate=True, y=p["a_y"])
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["w_go"] - 1, H["alive_only"](H["sfx"]("w_launch"), w_proj)),
    )

    # R: 回魂 — 唤回10秒内阵亡队友化魂再战8秒(拿人头真复活)，无阵亡队友则全体加盾!
    # 原生版：R 只是 3 tick 的「备好」（敌方英雄 6 万内就按，和联盟包阿利斯塔、布里茨的大招一样），挂 r_ask；
    # vesper.rs 在备好的 6 秒里等：队友倒下就回魂（放大招动作、光柱、魂体），有队友残血就给身边加盾，
    # 都没有就把冷却退回来，下次打起来再备。以前 R 一好就被 AI 放掉，几乎从来等不到阵亡的队友。
    # 塞拉斯偷大 / --plain(无 native) 降下回魂光柱为5万内友军群盾+回血+25%减伤!
    r_zone_effects = [
        H["shield"](p["r_sh"], ap_ratio=p["r_sh_ap"], tick=p["r_sh_t"]),
        H["heal"](p["r_heal"], ap_ratio=p["r_heal_ap"], kind="Ally"),
        H["buff"]("spirit", p["r_dr_t"], damaged_reduce=p["r_dr"], move_speed_mult=15),
        H["view"]("rebirth"),
        H["tsfx"]("warm_shield"),
    ]
    if is_native:
        sylas_shield = H["when"]("native", H["combine"](), H["combine"](
            {"type": "CasterViewEffect", "name": H["n"]("pillar")},
            H["sfx"]("return_pillar"),
            H["around"](p["r_r"], r_zone_effects, "AllyChampion"),
        ))
        ult = H["action"](
            "idle", p["r_arm_dur"], p["r_cd"], 1, p["r_range"], "None", "EnemyChampion",
            H["combine"](r_ask, sylas_shield),
        )
    else:
        ult = H["action"](
            "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "AllyChampion",
            H["combine"](
                H["sfx"]("r_pointer"),
                H["delayed"](p["r_go"] - 1, H["alive_only"](
                    H["lob"]("r_lob", 1, [
                        H["view"]("pillar"),
                        H["sfx"]("return_pillar"),
                        H["zone"]("r_zone", p["r_r"], r_zone_effects, target="AllyChampion"),
                    ], target="AllyChampion"),
                )),
            ),
        )

    views_p = [
        H["V_proj"]("a_wisp", "wisp"),
        H["V_proj"]("q_wisp", "wisp"),
        H["V_proj"]("w_scream", "scream"),
    ]
    views_e = [
        H["V_eff"]("warmth", "warmth", 2),
        H["V_eff"]("scream", "scream", 2),
        H["V_eff"]("pillar", "pillar", 3, follow=False),
        H["V_eff"]("rebirth", "rebirth", 3),
        H["V_eff"]("shield", "shield", 2),
    ]
    views_b = [
        H["V_buf"]("guide", "guide", 2),
        H["V_buf"]("spirit", "spirit", 2),
    ] + [H["V_buf"](f"candle_{k}", f"candle_{k}", 3) for k in range(1, 6)]
    kit = wrap_kit(cid, "Util", ["AP", "Magic", "Heal", "Shield", "CC"], p,
                   attack_a, skill, skill2, ult, views_p, views_e, views_b,
                   is_native, f"{cid}:vigil")
    if is_native:
        # 烛冠每支让引路的回血和护盾 +10%：vesper.rs 照这几个数补上那一截
        kit["passive"]["params"] = {k: p[k] for k in ("q_heal", "q_heal_ap", "q_sh", "q_sh_ap", "q_sh_t")}
    return kit


# ===========================================================================
# 11. 蜕甲 (abysspact_carapace) · 上路战士 · 蜕壳三形态与空壳嘲讽自爆
# ===========================================================================
def build_carapace(p, is_native=True):
    cid = "abysspact_carapace"
    H = mk_helpers(cid)

    r_voice = H["flag"]("r_voice", 4) if is_native else None
    r_molt_ask = H["flag"]("r_molt", 4) if is_native else None
    plain_forms = None if is_native else H["when"](
        "p_on", H["combine"](),
        H["combine"](H["flag"]("p_on", None),
                     H["flag"]("p_shell", None, defence=p["plain_def"], attack_speed_mult=p["plain_as"], hp_mult=p["plain_hp_mult"])))

    # Auto: 虫刃
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](plain_forms, H["attack"](0, 100), H["sfx"]("a"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 刺螯 — 前冲穿刺造成70+100%AD与30%减速; 第三形态(羽)借 q_range 变 4万 飞扑!
    q_hit = [
        H["attack"](p["q_dmg"], p["q_ad"]),
        H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
        H["tsfx"]("a_hit"),
    ]
    q_rush = {
        "type": "RushTime", "speed": p["q_speed"], "tick": p["q_t"], "range": p["q_rad"],
        "casting_target": "EnemyWithoutTower", "penetrate": True,
        "applied_effects": [H["T"](e) for e in q_hit if e is not None],
    }
    q_dive = H["combine"](
        H["sfx"]("q_dive"), H["view"]("dive"),
        H["move_to_target"](6200, 42000, [
            H["attack"](p["q_dmg"], p["q_ad"]),
            H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
            H["view"]("wing_flecks"), H["tsfx"]("a_hit"),
        ]),
    )
    q_normal = H["combine"](H["sfx"]("q_thrust"), H["view"]("thrust"), q_rush)
    # 射程的原生效果放在最外层 Combine 的最后（游戏的平衡补丁读第一个效果）
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["when"]("form3", q_dive, q_normal))),
            H["native_fx"](f"{cid}:q_range") if is_native else None,
        ),
    )

    # W: 甲鸣 — 敲甲震波2万: 伤害 + 按打出伤害的 30% 治疗自己
    # 原生版先挂 3 tick 的 w_heal，carapace.rs 在 on_attack 里按每一下的伤害回血（小兵、野怪也算）；
    # --plain 跑不了原生代码，按打中的英雄个数回一笔固定的血。
    w_hit = [H["attack"](p["w_dmg"], p["w_ad"]), H["tsfx"]("a_hit")]
    w_heal = H["flag"]("w_heal", 3) if is_native else None
    w_heal_plain = None if is_native else H["around"](
        p["w_r"], [H["heal"](p["w_heal"], ad_ratio=p["w_heal_ad"], kind="Caster")], "EnemyChampion")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["w_go"] - 1, H["alive_only"](
            H["sfx"]("w_resonate"),
            H["view"]("resonate"),
            w_heal,
            H["around"](p["w_r"], w_hit, "EnemyWithoutTower"),
            w_heal_plain,
        )),
    )

    # R: 羽化 — 未满三态时主动蜕壳爆旧甲(3万击飞+150+100%AD+4s +40%AS); 第三形态张翅6万飞扑击飞!
    # 塞拉斯偷大 / --plain(无 native) 自动放原地旧甲爆裂3万击飞+4秒+40%攻速!
    r_f3_dive = H["combine"](
        H["sfx"]("q_dive"),
        H["view"]("wing_flecks"),
        H["move_to_target"](6800, 62000, [
            H["view"]("molt_burst"),
            H["sfx"]("shell_burst"),
            H["around"](p["r_r"], [
                H["attack"](p["r_dmg"], p["r_ad"]),
                H["airborne"](p["r_air"]),
            ], "EnemyWithoutTower"),
        ]),
    )
    r_burst_data = H["combine"](
        H["flag"]("r_haste", p["r_as_t"], attack_speed_mult=p["r_as"]),
        H["view"]("molt_burst"),
        H["sfx"]("shell_burst"),
        H["around"](p["r_r"], [
            H["attack"](p["r_dmg"], p["r_ad"]),
            H["airborne"](p["r_air"]),
            H["taunt"](36) if not is_native else None,
        ], "EnemyWithoutTower"),
    )
    # 第三形态的飞扑：射程另加 3 万（carapace.rs 的 r_range）= 6 万
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                H["when"]("form3", r_f3_dive,
                          H["when"]("native", r_molt_ask, r_burst_data)),
            )),
            H["native_fx"](f"{cid}:r_range") if is_native else None,
        ),
    )

    views_p = [
        H["V_proj"]("p_thrust", "thrust"),
        H["V_proj"]("p_dive", "dive"),
    ]
    views_e = [
        H["V_eff"]("molt_steel", "molt_steel", 3, follow=False),
        H["V_eff"]("molt_light", "molt_light", 3, follow=False),
        H["V_eff"]("thrust", "thrust", 2),
        H["V_eff"]("dive", "dive", 2),
        H["V_eff"]("resonate", "resonate", 2),
        H["V_eff"]("molt_burst", "molt_burst", 3, follow=False),
        H["V_eff"]("taunt_glint", "taunt_glint", 3, follow=False),
        H["V_eff"]("wing_flecks", "wing_flecks", 2),
        H["V_eff"]("shell_rattle", "shell_rattle", 1, follow=False),
        H["V_eff"]("shell_explode", "shell_explode", 3, follow=False),
    ]
    views_b = [
        H["V_buf"]("shells_0", "shells_0", 3),
        H["V_buf"]("shells_1", "shells_1", 3),
        H["V_buf"]("shells_2", "shells_2", 3),
    ]
    return wrap_kit(cid, "Melee", ["AD", "Melee", "CC", "Heal"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:molt")


# ===========================================================================
# 12. 附骨 (abysspact_leech) · 打野刺客 · 寄生吸血与万蛭分裂
# ===========================================================================
def build_leech(p, is_native=True):
    cid = "abysspact_leech"
    H = mk_helpers(cid)

    r_voice = H["flag"]("r_voice", 4) if is_native else None
    attach_ask = H["buff"]("attach_ask", 4) if is_native else None
    r_split_ask = H["flag"]("r_split", 4) if is_native else None

    # Auto: 钩爪
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["attack"](0, 100), H["sfx"]("a"), H["view"]("claw"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 扑附 — 扑到敌方英雄背上造成法伤并附着3秒持续吸血 (附着走 leech.rs; --plain 近似持续吸血)
    q_plain_drain = None if is_native else H["combine"](
        H["ap_atk"](p["q_plain_drain"], p["q_plain_ap"]),
        H["heal"](p["q_plain_heal"], ap_ratio=25, kind="Caster"),
        H["view"]("drain"),
    )
    # 宿主 -30% 移速：原生版由 leech.rs 的 host_mark 给（附着多久就慢多久），数据只在 --plain 里给，免得叠成 -60%
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](
            H["sfx"]("q_lunge"),
            H["move_to_target"](6500, p["q_range"], [
                H["ap_atk"](p["q_dmg"], p["q_ap"]),
                None if is_native else H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
                attach_ask,
                q_plain_drain,
                H["view"]("jump"),
                H["tsfx"]("q_attach"),
            ]),
        )),
    )

    # W: 蚀髓 — 注毒造成法伤并沉默1秒 (附着时沉默延长至1.75秒!)
    w_hit = H["combine"](
        H["ap_atk"](p["w_dmg"], p["w_ap"]),
        H["when"]("attached", H["silence"](p["w_sil_att"]), H["silence"](p["w_sil"])),
        H["view"]("venom"),
        H["tsfx"]("w_venom"),
    )
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["w_go"] - 1, H["alive_only"](H["sfx"]("w_bite"), w_hit)),
            H["native_fx"](f"{cid}:w_range") if is_native else None,
        ),
    )

    # R: 万蛭 — 裂成5只小水蛭扑向敌方英雄各附3秒群吸!
    # 原生版：leech.rs 把他放逐 3 秒（不在场上、选不中），给每只真正扑出去的小水蛭放一发弹道到它的宿主，3 秒后从每个宿主
    # 飞回来聚成他；塞拉斯偷大 / --plain 触发水蛭群吸法伤+回血（数据的三发小水蛭弹道只在这时放）!
    r_mini_vis = None if is_native else H["rand_target"](p["r_range"], "EnemyChampion",
                                                         H["homing"]("r_mini", 8200, [
                                                             H["view"]("drain"),
                                                             H["tsfx"]("r_cling"),
                                                         ], target="EnemyChampion", y=-9000))
    r_non_native = H["when"](
        "native", H["combine"](),
        H["lob"]("r_lob", 1, [
            H["view"]("split"),
            H["sfx"]("split"),
            H["zone"]("r_zone", p["r_r"], [
                H["ap_atk"](p["r_dmg"], p["r_ap"]),
                H["heal"](p["r_heal"], ap_ratio=p["r_heal_ap"], kind="Caster"),
                H["view"]("drain"),
                H["tsfx"]("drain"),
            ], target="EnemyChampion"),
            H["delayed"](60, H["alive_only"](H["view"]("rejoin"), H["sfx"]("rejoin"))),
        ], target="EnemyChampion"),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["sfx"]("r_lunge"),
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                r_split_ask,
                r_mini_vis,
                None if is_native else H["delayed"](3, H["alive_only"](r_mini_vis)),
                None if is_native else H["delayed"](6, H["alive_only"](r_mini_vis)),
                r_non_native,
            )),
        ),
    )

    views_p = [
        H["V_proj"]("r_mini", "mini_lunge"),
        H["V_proj"]("p_venom", "venom"),
        H["V_proj"]("p_jump", "jump"),
    ]
    views_e = [
        H["V_eff"]("drain", "drain", 2),
        H["V_eff"]("shared_hit", "shared_hit", 3),
        H["V_eff"]("venom", "venom", 2),
        H["V_eff"]("split", "split", 3),
        H["V_eff"]("rejoin", "rejoin", 3),
        H["V_eff"]("claw", "claw", 2),
        H["V_eff"]("jump", "jump", 2),
    ]
    views_b = [
        H["V_buf"]("host_mark", "host_mark", 3),
        H["V_buf"]("mini_cling", "mini_cling", 3),
    ]
    return wrap_kit(cid, "Assassin", ["AP", "Magic", "Melee", "Heal", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:parasite")


# ===========================================================================
# 13. 千蛾 (abysspact_noctua) · 中路法师 · 散身蛾群与万蛾风暴
# ===========================================================================
def build_noctua(p, is_native=True):
    cid = "abysspact_noctua"
    H = mk_helpers(cid)

    r_voice = H["flag"]("r_voice", 4) if is_native else None
    scale_ask = H["buff"]("scale_ask", 4) if is_native else None
    r_storm_ask = H["flag"]("r_storm", 4) if is_native else None

    # Auto: 扑火 (4帧扑扇飞蛾弹道)
    a_moth = H["homing"]("a_moth", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_hit")],
                         target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_moth),
        atype="BaseAttack", cancel=True,
    )

    # Q: 蛾群 — 放出6只飞蛾自动寻敌，造成法伤并叠加鳞粉减速!
    q_plain_slow = None if is_native else H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"])
    q_one = H["rand_target"](p["q_range"], "EnemyWithoutTower",
                             H["homing"]("q_moth", 8400, [
                                 H["ap_atk"](p["q_dmg"], p["q_ap"]),
                                 scale_ask,
                                 q_plain_slow,
                                 H["view"]("scales"),
                                 H["tsfx"]("scale_mark"),
                             ], target="EnemyWithoutTower", y=p["a_y"]))
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_swarm"), q_one, q_one)),
            H["delayed"](p["q_go"] + 4, H["alive_only"](q_one, q_one)),
            H["delayed"](p["q_go"] + 9, H["alive_only"](q_one, q_one)),
        ),
    )

    # W: 织茧 — 飞蛾裹茧眩晕1.25秒，破茧飞回治疗自身5%最大生命!
    w_proj = H["homing"]("w_cocoon", 8000, [
        H["ap_atk"](p["w_dmg"], p["w_ap"]),
        H["stun"](p["w_stun"]),
        H["view"]("cocoon"),
        H["tsfx"]("w_close"),
        H["delayed"](p["w_stun"], H["alive_only"](
            H["view"]("cocoon_break"),
            H["tsfx"]("w_break"),
            H["heal"](p["w_heal"], ap_ratio=p["w_heal_ap"], kind="Caster"),
        )),
    ], target="EnemyChampion", y=p["a_y"])
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["delayed"](p["w_go"] - 1, H["alive_only"](H["sfx"]("a"), w_proj)),
    )

    # R: 万蛾 — 化作3.5秒不可选中蛾群风暴持续灼烧叠鳞粉，聚身爆开鳞粉沉默3万内敌人1.25秒!
    # Native 走 noctua.rs 真实移动风暴+聚身沉默; 塞拉斯偷大 / --plain 展开3.5秒蛾群风暴+终点鳞粉群体沉默!
    r_non_native = H["when"](
        "native", H["combine"](),
        H["lob"]("r_lob", 1, [
            H["view"]("disperse"),
            H["sfx"]("storm_start"),
            H["field"]("r_storm_f", p["r_r"], p["r_t"], p["r_p"], [
                H["ap_atk"](p["r_tick_dmg"], p["r_tick_ap"]),
                H["buff"]("r_slow", 60, move_speed_mult=-20),
                H["view"]("scales"),
            ], first=1, target="EnemyWithoutTower"),
            H["delayed"](p["r_t"], H["alive_only"](
                H["view"]("dust_shock"),
                H["sfx"]("dust_shock"),
                H["zone"]("r_sil_z", p["r_r"] + 4000, [
                    H["silence"](p["r_sil"]),
                    H["view"]("reform"),
                ], target="EnemyWithoutTower"),
            )),
        ], target="EnemyChampion"),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_storm_ask, r_non_native)),
        ),
    )

    views_p = [
        H["V_proj"]("a_moth", "moth"),
        H["V_proj"]("q_moth", "moth"),
        H["V_proj"]("w_cocoon", "cocoon"),
    ]
    views_e = [
        H["V_eff"]("scales", "scales", 2),
        H["V_eff"]("disperse", "disperse", 3),
        H["V_eff"]("reform", "reform", 3),
        H["V_eff"]("cocoon", "cocoon", 3),
        H["V_eff"]("cocoon_break", "cocoon_break", 3),
        H["V_eff"]("dust_shock", "dust_shock", 3, follow=False),
    ]
    views_b = [
        H["V_buf"]("storm", "storm", 2),
        H["V_buf"]("scales_1", "scales_1", 3),
        H["V_buf"]("scales_2", "scales_2", 3),
        H["V_buf"]("scales_3", "scales_3", 3),
    ]
    return wrap_kit(cid, "Magician", ["AP", "Magic", "Range", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:scatter")


# ===========================================================================
# 14. 沉锚 (abysspact_anchor) · 下路射手 · 下锚9万炮台与六发沉船炮
# ===========================================================================
def build_anchor(p, is_native=True):
    cid = "abysspact_anchor"
    H = mk_helpers(cid)

    r_voice = H["flag"]("r_voice", 4) if is_native else None
    toggle_ask = H["flag"]("toggle", 4) if is_native else None
    r_siege_ask = H["flag"]("r_siege", 4) if is_native else None

    # Auto: 拖锚锚链弹 / 下锚深海炮弹 (Native 借 siege_range 6万->9万 + anchor.rs 1.5万 60%溅射!)
    drag_shot = H["combine"](
        H["sfx"]("a_chain"),
        H["homing"]("a_chain", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_water")],
                    target="Enemy", y=p["a_y"]),
    )
    plain_splash = None if is_native else H["lob"]("a_sp_lob", 1, [
        H["view"]("splash"),
        H["zone"]("a_sp_z", 15000, [H["attack"](0, p["plain_splash_ad"])], target="EnemyWithoutTower"),
    ], target="Enemy")
    siege_shot = H["combine"](
        H["sfx"]("a_siege"),
        H["homing"]("a_shell", p["a_speed"], [H["attack"](0, 100), plain_splash, H["tsfx"]("a_water")],
                    target="Enemy", y=p["a_y"]),
    )
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](
            H["native_fx"](f"{cid}:siege_range") if is_native else None,
            H["when"]("siege", siege_shot, drag_shot),
        ),
        atype="BaseAttack", cancel=True,
    )

    # Q: 横扫 — 抡锚链扫2.5万击退2万 + 65+82%AD 物理伤害!
    q_hit = [
        H["attack"](p["q_dmg"], p["q_ad"]),
        H["knockback"](p["q_kb_spd"], p["q_kb_t"]),
        H["tsfx"]("a_water"),
    ]
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](
            H["sfx"]("q_sweep"),
            H["view"]("chain_sweep"),
            H["around"](p["q_r"], q_hit, "EnemyWithoutTower"),
        )),
    )

    # W: 下锚/起锚 — 在拖锚(+10%移速)与下锚炮台(9万射程+溅射+压舱免疫位移)之间切换!
    w_plain_toggle = None if is_native else H["when"](
        "siege",
        H["combine"](H["unflag"]("siege"), H["sfx"]("raise")),
        H["combine"](H["flag"]("siege", 360, attack_speed_mult=-15), H["view"]("crack"),
                     H["view"]("stamp"), H["sfx"]("plant")),
    )
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["delayed"](p["w_go"] - 1, H["alive_only"](
            H["view"]("taut"),
            toggle_ask,
            w_plain_toggle,
        )),
    )

    # R: 沉船炮 — 2.4秒内往12万内连轰6发巨炮，每发2万范围高伤+0.4秒击飞! (塞拉斯偷大也能完整轰出6发沉船巨炮!)
    r_shell_drop = H["lob"]("r_salvo", 14, [
        H["view"]("salvo_blast"),
        H["view"]("foam"),
        H["sfx"]("r_impact"),
        H["zone"]("r_blast_z", p["r_r"], [
            H["attack"](p["r_dmg"], p["r_ad"]),
            H["airborne"](p["r_air"]),
        ], target="EnemyWithoutTower"),
    ], target="EnemyChampion")
    r_fire_one = H["combine"](
        H["sfx"]("r_fire"),
        H["rand_target"](p["r_range"], "EnemyChampion", r_shell_drop),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            r_siege_ask,
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_fire_one)),
            H["delayed"](p["r_go"] + 23, H["alive_only"](r_fire_one)),
            H["delayed"](p["r_go"] + 47, H["alive_only"](r_fire_one)),
            H["delayed"](p["r_go"] + 71, H["alive_only"](r_fire_one)),
            H["delayed"](p["r_go"] + 95, H["alive_only"](r_fire_one)),
            H["delayed"](p["r_go"] + 119, H["alive_only"](r_fire_one)),
        ),
    )

    views_p = [
        H["V_proj"]("a_chain", "chain"),
        H["V_proj"]("a_shell", "shell"),
        H["V_proj"]("r_salvo", "salvo_arc"),
    ]
    views_e = [
        H["V_eff"]("splash", "splash", 2, follow=False),
        H["V_eff"]("crack", "crack", -1, follow=False),
        H["V_eff"]("taut", "taut", 2),
        H["V_eff"]("stamp", "stamp", -1, follow=False),
        H["V_eff"]("chain_sweep", "chain_sweep", 2),
        H["V_eff"]("salvo_blast", "salvo_blast", 3, follow=False),
        H["V_eff"]("foam", "foam", 2, follow=False),
    ]
    views_b = []
    return wrap_kit(cid, "Range", ["AD", "Range", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:siege")


# ===========================================================================
# 15. 返照 (abysspact_hourglass) · 辅助 · 回光救死、全队倒流与老去白发
# ===========================================================================
def build_hourglass(p, is_native=True):
    cid = "abysspact_hourglass"
    H = mk_helpers(cid)

    r_voice = H["flag"]("r_voice", 4) if is_native else None
    q_mark_ask = H["buff"]("q_ask", 4) if is_native else None
    r_rewind_ask = H["flag"]("r_ask", 4) if is_native else None

    # Auto: 流沙
    a_spark = H["homing"]("a_spark", p["a_speed"], [H["attack"](0, 100), H["tsfx"]("a_hit")],
                          target="Enemy", y=p["a_y"])
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["sfx"]("a"), a_spark),
        atype="BaseAttack", cancel=True,
    )

    # Q: 回光 — 给友军打上3秒回光表盘印记(濒死免死倒回血量，3秒后倒回满血差)，老去+1层!
    q_plain_save = None if is_native else H["combine"](
        H["buff"]("clock", p["q_t"], undying=True),
        H["delayed"](90, H["alive_only"](
            H["heal"](p["q_plain_heal"], ap_ratio=p["q_plain_ap"], kind="Ally"),
            H["view"]("rewind"),
            H["tsfx"]("rewind_snap"),
        )),
    )
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "AllyChampion",
        H["delayed"](p["q_go"] - 1, H["alive_only"](
            H["sfx"]("q_mark"),
            H["view"]("sand_rise"),
            q_mark_ask,
            q_plain_save,
        )),
    )

    # W: 停摆 — 2万范围静止齿轮眩晕1秒 + 法伤!
    w_zone = H["lob"]("w_lob", 1, [
        H["view"]("gear"),
        H["sfx"]("w_stop"),
        H["zone"]("w_gear_z", p["w_r"], [
            H["ap_atk"](p["w_dmg"], p["w_ap"]),
            H["stun"](p["w_stun"]),
            H["view"]("sand_burst"),
        ], target="EnemyWithoutTower"),
    ], target="EnemyWithoutTower")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["w_go"] - 1, H["alive_only"](w_zone)),
    )

    # R: 倒流 — 翻转沙漏让10万内所有存活友军倒回3秒前的位置与血量(老去+3层)!
    # Native 走 hourglass.rs 真实3秒历史位置+血量倒流; 塞拉斯偷大 / --plain 翻转沙漏全队高额回血+护盾+残影特效!
    r_non_native = H["when"](
        "native", H["combine"](),
        H["lob"]("r_lob", 1, [
            H["view"]("hourglass"),
            H["sfx"]("flip"),
            H["zone"]("r_zone", p["r_r"], [
                H["heal"](p["r_plain_heal"], ap_ratio=p["r_plain_ap"], kind="Ally"),
                H["shield"](p["r_plain_sh"], ap_ratio=p["r_plain_sh_ap"], tick=180),
                H["view"]("echo"),
                H["view"]("rewind"),
                H["tsfx"]("rewind_snap"),
            ], target="AllyChampion"),
        ], target="AllyChampion"),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "AllyChampion",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_rewind_ask, r_non_native)),
        ),
    )

    views_p = [H["V_proj"]("a_spark", "sand_spark")]
    views_e = [
        H["V_eff"]("rewind", "rewind", 3),
        H["V_eff"]("gear", "gear", -1, follow=False),
        H["V_eff"]("hourglass", "hourglass", 3),
        H["V_eff"]("echo", "echo", 2, follow=False),
        H["V_eff"]("sand_rise", "sand_rise", 2),
        H["V_eff"]("sand_burst", "sand_burst", 3),
    ]
    views_b = [
        H["V_buf"]("clock", "clock", -1),
    ]
    return wrap_kit(cid, "Util", ["AP", "Magic", "Heal", "Shield", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:sands")


# ===========================================================================
# 16. 缓刑 (abysspact_reprieve) · 囚徒 · 上路坦克
# ===========================================================================
def build_reprieve(p, is_native=True):
    cid = "abysspact_reprieve"
    H = mk_helpers(cid)
    r_voice = H["flag"]("r_voice", 4) if is_native else None
    plain_dr = None if is_native else H["when"](
        "p_on", H["combine"](),
        H["combine"](H["flag"]("p_on", None),
                     H["flag"]("p_dr", None, base_attack_damaged_reduce=p["plain_dr"],
                               skill_damaged_reduce=p["plain_dr"])))

    # Auto: 铁球 (100% AD, 2.8万 melee)
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](plain_dr, H["attack"](0, 100), H["sfx"]("a"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 掷球 — 把大铁球甩向敌方英雄: 80 + 6% 目标最大生命物理伤害 + 眩晕 0.75s + 铁链拽回!
    q_hit = [
        H["attack"](p["q_dmg"], 0, thp=p["q_thp"]),
        H["stun"](p["q_stun"]),
        H["grab"](p["q_grab_spd"], p["q_grab_t"]),
        H["tsfx"]("q_pull"),
    ]
    q_proj = H["linear"]("q_chain", p["q_speed"], p["q_range"] + 8000, p["q_w"], q_hit,
                         target="EnemyWithoutTower", penetrate=False, y=-8000)
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_throw"), q_proj)),
    )

    # W: 认罪 — 仰头大吼: 3万内敌人被嘲讽 1.25s，期间缓刑记账比例从 50% 提到 70%!
    w_guilt = H["flag"]("guilt", p["w_taunt"],
                        **(dict() if is_native else {"base_attack_damaged_reduce": p["w_plain_dr"],
                                                     "skill_damaged_reduce": p["w_plain_dr"]}))
    w_aoe = H["around"](p["w_r"], [H["taunt"](p["w_taunt"])], target="EnemyWithoutTower")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["w_go"] - 1, H["alive_only"](
            H["sfx"]("w_roar"), H["view"]("roar"), w_guilt, w_aoe,
        )),
    )

    # R: 枷 — 前方扇形甩出三副巨枷，扣住 5万内敌方英雄: 眩晕 1.5s + 150 + 8% 目标最大生命物理伤害!
    r_hit = [
        H["attack"](p["r_dmg"], 0, thp=p["r_thp"]),
        H["stun"](p["r_stun"]),
        H["view"]("cangue_drop"),
        H["view"]("cangue_chips"),
        H["buff"]("cangue_hold", p["r_stun"]),
        H["tsfx"]("r_hold"),
        H["delayed"](p["r_stun"], H["view"]("cangue_break"), H["tsfx"]("r_break")),
    ]
    r_cone = H["cone"](p["r_r"], p["r_cone"], r_hit, target="EnemyWithoutTower")
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](H["sfx"]("r_drop"), r_cone)),
        ),
    )

    views_p = [H["V_proj"]("q_chain", "chain")]
    views_e = [
        H["V_eff"]("roar", "roar", 2),
        H["V_eff"]("tally", "tally", 2),
        H["V_eff"]("absolve", "absolve", 3),
        H["V_eff"]("cangue_drop", "cangue_drop", 3),
        H["V_eff"]("cangue_chips", "cangue_chips", 3),
        H["V_eff"]("cangue_break", "cangue_break", 3),
    ]
    views_b = [
        H["V_buf"]("tally_light", "tally_light", 2),
        H["V_buf"]("cangue_hold", "cangue_hold", 3),
    ]
    cat = "Tank" if is_native else "Melee"
    return wrap_kit(cid, cat, ["Tank", "Melee", "CC", "AD"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:sentence")


# ===========================================================================
# 17. 赊命 (abysspact_debtor) · 赊命剑客 · 打野战士
# ===========================================================================
def build_debtor(p, is_native=True):
    cid = "abysspact_debtor"
    H = mk_helpers(cid)
    r_voice = H["flag"]("r_voice", 4) if is_native else None
    q_hit_ask = H["buff"]("q_hit", 3) if is_native else None
    r_ask = H["buff"]("r_ask", 4) if is_native else None

    # Auto: 弯剑
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](H["attack"](0, 100), H["sfx"]("a"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 讨债 — 突刺冲向敌方英雄: 70 + 100% AD + 6秒欠条 (+30%以下+50%斩杀伤害由 debtor.rs 追加)
    q_land = [
        H["attack"](p["q_dmg"], p["q_ad"]),
        H["buff"]("debt_note", p["q_note_t"]),
        q_hit_ask,
        H["view"]("thrust"),
        H["tsfx"]("q_note"),
    ]
    q_dash = H["move_to_target"](p["q_speed"], p["q_range"] + 15000, q_land)
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_thrust"), q_dash)),
    )

    # W: 利息 — 原地横扫 2.5万: 50 + 70% AD + 每命中一个英雄回复生命并留欠条
    w_hit = [
        H["attack"](p["w_dmg"], p["w_ad"]),
        H["buff"]("debt_note", p["q_note_t"]),
        H["heal"](p["w_heal"], ad_ratio=p["w_heal_ad"], kind="Caster"),
        H["tsfx"]("q_note"),
    ]
    w_aoe = H["around"](p["w_r"], w_hit, target="EnemyWithoutTower")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["w_go"] - 1, H["alive_only"](H["sfx"]("w_sweep"), H["view"]("sweep"), w_aoe)),
    )

    # R: 换命 — Native 走 debtor.rs 真实对调血量比例 + 6秒到期换回/击杀吞并; 塞拉斯偷大/--plain 走高额吸命爆发!
    r_non_native = H["when"](
        "native", H["combine"](),
        H["combine"](
            H["attack"](p["r_plain_dmg"], 0, thp=p["r_plain_thp"]),
            H["heal"](p["r_plain_heal"], ad_ratio=p["r_plain_ad"], kind="Caster"),
            H["view"]("swap"),
            H["view"]("life_flame"),
            H["sfx"]("swap"),
        ),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_ask, r_non_native)),
        ),
    )

    views_p = []
    views_e = [
        H["V_eff"]("thrust", "thrust", 2),
        H["V_eff"]("sweep", "sweep", 2),
        H["V_eff"]("swap", "swap", 3),
        H["V_eff"]("swap_return", "swap_return", 3),
        H["V_eff"]("life_flame", "life_flame", 3),
        H["V_eff"]("absorb", "absorb", 3),
    ]
    views_b = [
        H["V_buf"]("debt_note", "debt_note", 3),
        H["V_buf"]("timer_ring", "timer_ring", 3),
        H["V_buf"]("flame_100", "flame_100", 2),
        H["V_buf"]("flame_50", "flame_50", 2),
        H["V_buf"]("flame_25", "flame_25", 2),
    ]
    return wrap_kit(cid, "Melee", ["AD", "Melee", "Heal"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:ledger")


# ===========================================================================
# 18. 无痕 (abysspact_traceless) · 白衣剑客 · 中路物理刺客
# ===========================================================================
def build_traceless(p, is_native=True):
    cid = "abysspact_traceless"
    H = mk_helpers(cid)
    r_voice = H["flag"]("r_voice", 4) if is_native else None
    q_cast_ask = H["flag"]("q_cast", 4) if is_native else None
    w_ask = H["flag"]("w_ask", 4) if is_native else None
    hit_ask = H["flag"]("hit_ask", 3) if is_native else None
    plain_edge = None if is_native else H["when"](
        "p_on", H["combine"](),
        H["combine"](H["flag"]("p_on", None), H["flag"]("p_edge", None, attack_mult=p["plain_edge_ad"])))

    ambush_proc = H["combine"](
        H["attack"](p["w_ambush_dmg"], p["w_ambush_ad"]),
        H["unflag"]("w_ambush"),
        H["view"]("stab"),
    )

    # Auto: 刺剑 (0.8s fast rapier thrust)
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](plain_edge, H["attack"](0, 100), H["when"]("w_ambush", ambush_proc),
                     H["sfx"]("a"), H["view"]("stab"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 一线 — 穿刺敌方英雄: 80 + 90% AD (击杀立刻刷新CD由 traceless.rs 实现)
    q_hit = [
        H["attack"](p["q_dmg"], p["q_ad"]),
        H["when"]("w_ambush", ambush_proc),
        hit_ask,
        H["view"]("line"),
        H["tsfx"]("a_hit"),
    ]
    q_rush = {
        "type": "RushTime", "speed": p["q_speed"], "tick": p["q_t"], "range": p["q_rad"],
        "casting_target": "EnemyWithoutTower", "penetrate": True,
        "applied_effects": [H["T"](e) for e in q_hit if e is not None],
    }
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](
            q_cast_ask, H["sfx"]("q_line"), H["view"]("line"), q_rush,
        )),
    )

    # W: 残影 — 原地留淡白残影，0.75s 不可选中 (Banish) 接 1.0s 隐身 + 移速，保住全部锋层!
    w_cast = H["combine"](
        w_ask,
        H["sfx"]("w_dodge"),
        H["view"]("afterimage"),
        H["search_self"]({"type": "Banish", "duration": p["w_banish"]}),
        H["delayed"](p["w_banish"],
                     H["search_self"]({"type": "CasterInvisible", "tick": p["w_inv"]}),
                     H["flag"]("w_haste", p["w_inv"], move_speed_mult=p["w_ms"]),
                     H["flag"]("w_ambush", p["w_ambush_t"])),
    )
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyChampion",
        H["delayed"](p["w_go"] - 1, H["alive_only"](w_cast)),
    )

    # R: 无影 — 消失 1.5s (不可选中)，在 5万内每个敌方英雄身上依次各划一剑 + 最终全亮爆发 + 停在目标身后!
    r_slash = H["around"](p["r_r"], [
        H["attack"](p["r_dmg"], p["r_ad"]),
        hit_ask,
        H["view"]("cut"),
        H["tsfx"]("r_cut"),
    ], target="EnemyChampion")
    r_finish = H["combine"](
        {"type": "Teleport"},
        H["around"](p["r_r"], [
            H["attack"](p["r_dmg"] // 2, p["r_ad"] // 2),
            H["view"]("cut_final"),
        ], target="EnemyChampion"),
        H["sfx"]("r_final"),
    )
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                H["sfx"]("r_vanish"),
                H["view"]("vanish"),
                H["search_self"]({"type": "Banish", "duration": p["r_vanish"]}),
                H["delayed"](18, r_slash),
                H["delayed"](50, r_slash),
                H["delayed"](p["r_vanish"], r_finish),
            )),
        ),
    )

    views_p = []
    views_e = [
        H["V_eff"]("stab", "stab", 2),
        H["V_eff"]("line", "line", 2),
        H["V_eff"]("afterimage", "afterimage", 1, follow=False),
        H["V_eff"]("vanish", "vanish", 3, follow=False),
        H["V_eff"]("cut", "cut", 3),
        H["V_eff"]("cut_final", "cut_final", 3),
        H["V_eff"]("ink", "ink", 3),
        H["V_eff"]("quench", "quench", 3),
    ]
    views_b = [
        H["V_buf"]("blade_glow", "blade_glow", 2),
        *[H["V_buf"](f"edge_{k}", f"edge_{k}", 3) for k in range(1, 9)],
    ]
    return wrap_kit(cid, "Assassin", ["AD", "Melee"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:spotless")


# ===========================================================================
# 19. 陨夜 (abysspact_starfall) · 观星少女 · 下路法术射手
# ===========================================================================
def build_starfall(p, is_native=True):
    cid = "abysspact_starfall"
    H = mk_helpers(cid)
    r_voice = H["flag"]("r_voice", 4) if is_native else None

    # Auto: 黑星 — 0.5秒(30 ticks)延迟从天而降砸中 1.5万范围 (100% AD + 25% AP 魔法/混合伤害，旁边 60% 溅射!)
    # 3万内最小射程代价由 starfall.rs 在 on_attack 中执行!
    a_drop = H["lob"]("a_star", p["a_delay"], [
        H["view"]("star_impact"),
        H["sfx"]("a_hit"),
        H["zone"]("a_zone", p["a_r"], [
            H["attack"](0, p["a_splash_ad"]),
            H["ap_atk"](0, p["a_splash_ap"]),
        ], target="Enemy"),
    ], target="Enemy")
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](
            H["sfx"]("a"),
            H["view"]("warning"),
            H["attack"](0, 40),
            H["ap_atk"](0, p["a_ap"] - p["a_splash_ap"]),
            H["delayed"](12, H["sfx"]("a_fall")),
            a_drop,
        ),
        atype="BaseAttack", cancel=True,
    )

    # Q: 星轨 — 依次落下 5 颗黑星 (间隔 6 ticks)，每颗 60 + 45% AP 魔法伤害，命中减速 30% 1.5s!
    def q_star_drop(delay_t):
        return H["delayed"](delay_t, H["lob"]("q_star", 18, [
            H["view"]("star_impact"),
            H["sfx"]("a_hit"),
            H["zone"]("q_z", p["q_r"], [
                H["ap_atk"](p["q_dmg"], p["q_ap"]),
                H["buff"]("q_slow", p["q_slow_t"], move_speed_mult=-p["q_slow"]),
            ], target="EnemyWithoutTower"),
        ], target="EnemyWithoutTower"))

    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](
            H["sfx"]("q_track"),
            H["view"]("warning"),
            q_star_drop(0),
            q_star_drop(8),
            q_star_drop(16),
            q_star_drop(24),
            q_star_drop(32),
        )),
    )

    # W: 遁星 — 敌人逼近 3.2万时立刻化作星光向后闪 4万，原地落下黑星把近身敌人击退 1.5万!
    w_blast = H["around"](p["w_r"], [
        H["ap_atk"](p["w_dmg"], p["w_ap"]),
        H["knockback"](p["w_kb_spd"], p["w_kb_t"]),
        H["view"]("push"),
    ], target="EnemyWithoutTower")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["w_go"] - 1, H["alive_only"](
            H["sfx"]("w_dash"),
            H["sfx"]("w_push"),
            H["view"]("dash"),
            H["view"]("star_impact"),
            w_blast,
            H["move_back"](p["w_back_spd"], p["w_back_t"]),
        )),
    )

    # R: 陨夜 — 抬杖指天裂开星空，4秒内持续在半径 4万倾泻黑星雨 (8轮高密度魔法打击，期间可自由移动)!
    r_rain = H["lob"]("r_lob", 1, [
        H["view"]("sky_rift"),
        H["sfx"]("r_rift"),
        H["field"]("r_field", p["r_r"], p["r_t"], p["r_p"], [
            H["ap_atk"](p["r_dmg"], p["r_ap"]),
            H["view"]("star_impact"),
            H["tsfx"]("r_rain"),
        ], first=12, target="EnemyWithoutTower"),
    ], target="EnemyWithoutTower")
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyWithoutTower",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](r_rain)),
        ),
    )

    views_p = [
        H["V_proj"]("a_star", "black_star"),
        H["V_proj"]("q_star", "black_star"),
    ]
    views_e = [
        H["V_eff"]("warning", "warning", -1, follow=False),
        H["V_eff"]("star_impact", "star_impact", 3, follow=False),
        H["V_eff"]("dash", "dash", 2),
        H["V_eff"]("push", "push", 2),
        H["V_eff"]("sky_rift", "sky_rift", 3, follow=False),
    ]
    views_b = [
        H["V_buf"]("star_ring", "star_ring", 2),
    ]
    return wrap_kit(cid, "Range", ["AP", "Magic", "Range", "CC"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:starfall")


# ===========================================================================
# 20. 丧钟 (abysspact_knell) · 守钟人 · 辅助坦克
# ===========================================================================
def build_knell(p, is_native=True):
    cid = "abysspact_knell"
    H = mk_helpers(cid)
    r_voice = H["flag"]("r_voice", 4) if is_native else None
    r_ask = H["flag"]("r_ask", 4) if is_native else None
    plain_dr = None if is_native else H["when"](
        "p_on", H["combine"](),
        H["combine"](H["flag"]("p_on", None),
                     H["flag"]("p_dr", None, base_attack_damaged_reduce=p["plain_dr"],
                               skill_damaged_reduce=p["plain_dr"])))

    # Auto: 钟锤
    attack_a = H["action"](
        "attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
        H["combine"](plain_dr, H["attack"](0, 100), H["sfx"]("a"), H["tsfx"]("a_hit")),
        atype="BaseAttack", cancel=True,
    )

    # Q: 撞钟 — 抡锤撞响背上的钟: 前方 4万扇形 60 + 5% 自身最大生命魔法伤害 + 眩晕 0.75s!
    q_cone = H["cone"](p["q_r"], p["q_cone"], [
        H["ap_atk"](p["q_dmg"], 0, hp_ratio=p["q_hp"]),
        H["stun"](p["q_stun"]),
        H["view"]("cone"),
    ], target="EnemyWithoutTower")
    skill = H["action"](
        "skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyWithoutTower",
        H["delayed"](p["q_go"] - 1, H["alive_only"](H["sfx"]("q_strike"), q_cone)),
    )

    # W: 回响 — 给 6万内友军加护盾(3s) + 20% 移速(1.5s)
    w_aoe = H["around"](p["w_r"], [
        H["shield"](p["w_sh"], tick=p["w_sh_t"]),
        H["buff"]("w_ms", p["w_ms_t"], move_speed_mult=p["w_ms"]),
        H["view"]("echo_shield"),
    ], target="AllyChampion")
    skill2 = H["action"](
        "skill2", p["w_dur"], p["w_cd"], 1, p["w_range"], "Targeting", "AllyChampion",
        H["delayed"](p["w_go"] - 1, H["alive_only"](H["sfx"]("w_shield"), w_aoe)),
    )

    # R: 丧钟 — 跳至敌阵扣下黑铁巨钟 2.5s!
    # Native 走 knell.rs 真实多目标放逐钟域 (钟里钟外互相打不着，每 0.5s 响钟法伤，2.5s 掀钟击飞)!
    # 塞拉斯偷大 / --plain 走巨钟落顶 2.5s 沉默持续震响 + 掀钟击飞!
    r_non_native = H["when"](
        "native", H["combine"](),
        H["lob"]("r_lob", 1, [
            H["view"]("bell_drop"),
            H["view"]("bell_dust"),
            H["sfx"]("giant_drop"),
            H["field"]("r_chimes", p["r_r"], p["r_t"], p["r_p"], [
                H["ap_atk"](p["r_tick_dmg"], 0, hp_ratio=p["r_tick_hp"]),
                H["silence"](p["r_p"] + 6),
                H["view"]("bell_chime"),
                H["tsfx"]("giant_chime"),
            ], first=p["r_p"], target="EnemyWithoutTower"),
            H["delayed"](p["r_t"],
                         H["view"]("bell_lift"),
                         H["view"]("bell_open_wave"),
                         H["sfx"]("lift"),
                         H["sfx"]("open_wave"),
                         H["zone"]("r_lift_z", p["r_r"], [
                             H["airborne"](p["r_air"]),
                         ], target="EnemyWithoutTower")),
        ], target="EnemyWithoutTower"),
    )
    r_leap = H["move_to_target"](p["r_speed"], p["r_range"] + 15000, [
        r_ask,
        r_non_native,
    ])
    ult = H["action"](
        "ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
        H["combine"](
            r_voice,
            H["delayed"](p["r_go"] - 1, H["alive_only"](
                H["sfx"]("r_shadow"),
                H["view"]("bell_shadow"),
                r_leap,
            )),
        ),
    )

    views_p = []
    views_e = [
        H["V_eff"]("cone", "cone", 2),
        H["V_eff"]("echo_shield", "echo_shield", 2),
        H["V_eff"]("bell_shadow", "bell_shadow", -1, follow=False),
        H["V_eff"]("bell_drop", "bell_drop", 3, follow=False),
        H["V_eff"]("bell_dust", "bell_dust", 2, follow=False),
        H["V_eff"]("bell_chime", "bell_chime", 3, follow=False),
        H["V_eff"]("bell_lift", "bell_lift", 3, follow=False),
        H["V_eff"]("bell_open_wave", "bell_open_wave", 3, follow=False),
    ]
    views_b = []
    cat = "Tank" if is_native else "Melee"
    return wrap_kit(cid, cat, ["Tank", "Melee", "CC", "Shield", "Magic"], p,
                    attack_a, skill, skill2, ult, views_p, views_e, views_b,
                    is_native, f"{cid}:bell_shell")


BUILDERS = {
    "oathbreaker": ("abysspact_oathbreaker", build_oathbreaker),
    "faceless":    ("abysspact_faceless",    build_faceless),
    "whisperer":   ("abysspact_whisperer",   build_whisperer),
    "bonebow":     ("abysspact_bonebow",     build_bonebow),
    "corvus":      ("abysspact_corvus",      build_corvus),
    "bloodmoon":   ("abysspact_bloodmoon",   build_bloodmoon),
    "undertaker":  ("abysspact_undertaker",  build_undertaker),
    "effigy":      ("abysspact_effigy",      build_effigy),
    "sevenfold":   ("abysspact_sevenfold",   build_sevenfold),
    "vesper":      ("abysspact_vesper",      build_vesper),
    "carapace":    ("abysspact_carapace",    build_carapace),
    "leech":       ("abysspact_leech",       build_leech),
    "noctua":      ("abysspact_noctua",      build_noctua),
    "anchor":      ("abysspact_anchor",      build_anchor),
    "hourglass":   ("abysspact_hourglass",   build_hourglass),
    "reprieve":    ("abysspact_reprieve",    build_reprieve),
    "debtor":      ("abysspact_debtor",      build_debtor),
    "traceless":   ("abysspact_traceless",   build_traceless),
    "starfall":    ("abysspact_starfall",    build_starfall),
    "knell":       ("abysspact_knell",       build_knell),
}


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


SFX_DIR = os.path.join(REPO, MOD_ID, "sound", "sfx")


def _front_sfx(effect):
    """动作最外层一开头就会响的 Sfx。"""
    if effect.get("type") == "Sfx":
        return [effect]
    if effect.get("type") == "Combine":
        return [e for e in effect["effects"] if e.get("type") == "Sfx"]
    return []


def _sure_sfx(effect):
    """不管走哪个分支都一定会响的 Sfx。"""
    kind = effect.get("type")
    if kind == "Sfx":
        return [effect["name"]]
    if kind == "Combine":
        return [n for e in effect["effects"] for n in _sure_sfx(e)]
    if kind == "SwitchByBuff":
        a, b = _sure_sfx(effect["effect_buff"]), _sure_sfx(effect["effect_none"])
        return sorted(set(a + b)) if a and b else []
    return []


def add_foley(kit):
    """出招音效：2026-11-24 那一轮直接改了生成好的技能文件（每个动作开头一定有一声，没有的补
    <id>_foley_q/w/r，已有的挪到最前面），这里照原样做一遍，免得重新生成时丢掉。
    只补 abysspact/sound/sfx 里已经有 .sound_info 的那几个。"""
    cid = kit["id"]
    for action, key in (("attack", "a"), ("skill", "q"), ("skill2", "w"), ("ult", "r")):
        a = kit[action]
        eff = a["effect"]
        front = _front_sfx(eff)
        if front:
            if eff["type"] == "Combine":
                eff["effects"] = [*front, *(e for e in eff["effects"] if e.get("type") != "Sfx")]
            continue
        if action == "attack" and _sure_sfx(eff):
            continue
        event = f"{cid}_foley_{key}"
        if not os.path.exists(os.path.join(SFX_DIR, event + ".sound_info")):
            continue
        sfx = {"type": "Sfx", "name": event}
        if eff["type"] == "Combine":
            eff["effects"].insert(0, sfx)
        else:
            a["effect"] = {"type": "Combine", "effects": [sfx, eff]}
    return kit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", choices=list(BUILDERS.keys()), help="Build one hero (default: all 5)")
    ap.add_argument("--plain", action="store_true", help="Plain data-only mode for classic balance sim (kd.py)")
    ap.add_argument("--out", help="Output path (only valid with --hero)")
    ap.add_argument("--set", nargs="*", default=[], help="Override parameters key=value (with --hero)")
    ap.add_argument("--nodes", action="store_true")
    args = ap.parse_args()

    targets = [args.hero] if args.hero else list(BUILDERS.keys())
    for key in targets:
        cid, fn = BUILDERS[key]
        p = dict(PARAMS[key])
        if args.hero:
            for kv in args.set:
                k, v = kv.split("=", 1)
                if k not in p:
                    sys.exit(f"unknown parameter {k} for {key}")
                p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
        kit = add_foley(fn(p, is_native=not args.plain))
        if args.nodes:
            print(cid, " ".join(f"{s}:{nodes(kit[s]['effect'])}" for s in ("attack", "skill", "skill2", "ult")))
        out_path = args.out if (args.hero and args.out) else os.path.join(OUT_DIR, f"{cid}.data_champion")
        os.makedirs(os.path.dirname(lp(out_path)), exist_ok=True)
        text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
        with open(lp(out_path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(f"wrote {out_path} ({len(text)} bytes)")


if __name__ == "__main__":
    main()
