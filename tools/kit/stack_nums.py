"""Stack counts in the game's own champion panel, next to the skill icons, as in League (2026-11-11).

    python tools/kit/stack_nums.py --write   # every listed hero's `stack_skill_index` (league/, the add-ons' copies, tft/)
                                             # and the tables: league.dll's addons/league_main/src/stack_table.rs,
                                             # tft.dll's addons/tft/src/stack_table.rs
    python tools/kit/stack_nums.py --check   # (CI) both up to date, every row reads something in some copy
    python tools/kit/stack_nums.py --list    # the heroes, their rules and their icons

Why (the user, 2026-11-11): 「现在叠层数的技能英雄在游戏里看不到多少层 有没有办法在游戏里能看到？」. A number over the head came
first (「放头顶有点丑啊」), then 「不能放技能栏里面吗 和联盟一样」 -> 「技能栏层数格」.

The match's champion panel (`ingame.champion_tooltip`, bottom left: face, health, experience, the three skill icons)
has a `stack_info` - an icon and a number - right of the skill icons, hidden unless the champion's
`ChampionInfo::stack_skill_index()` is set (TeamfightManager2.exe 0.7.1, the panel's update at 0x8729a0): then it shows
that skill's icon and the champion's stat `stack`. A data champion's `stack_skill_index` is the .data_champion field of
that name (0 skill, 1 skill2, 2 ult). `apply` writes it for every hero of STACKS ("skill"), in league/champion/ and in
every add-on's copy of him; the kit scripts' `build = stack_nums.wrap(build)` keep it in a rebuild. It also drops the
over-head number bindings (`<hero>_sn_*` view_buffs) of the first version.

The data cannot count a stack (it only asks whether a buff is on a unit), so league.dll counts in the simulation and
writes `stack` (addons/league_main/src/stacks.rs): STACKS below is its table (stack_table.rs, generated).

2026-11-22（用户：「还有很多叠层的技能在技能列表里看不到层数 想个办法解决一下」）：表从 27 个英雄补到所有数得出来的。
- 新的三种数法：`most`（几个名字各对一个数，身上有的取最大）、`total`（身上有的加起来）、`prefix`（名字以它开头的有几个）；
- `"on": "foes"`：不数他自己，数每个活着的敌方英雄身上的，取最多的那个（附加包照英雄联盟把层数记在敌人身上）；
- 一个英雄可以有几行：主包的数据记在他自己身上、附加包记在敌人身上或者自己挂梯子，league.dll 取几行里最大的。每行只在
  挂得出它那些名字的那份英雄数据里读得出数，所以 `--check` 看每份带层数格的英雄数据里至少有一行「活着」：名字在这份数据里
  有人挂（AddCasterBuff / AddBuff），或者这份是 `native` 里那个附加包的副本（它的原生代码挂同样的名字），或者 `passive`
  对得上（附加包自己的梯子）；每一行也至少在一份数据里活着（改了名字就会报出来）。
- `charges`：技能的充能（提莫的蘑菇），读游戏自己的冷却；`per`（和 sum 一起）：一项数值除以一层的量。
- 云顶（tft 包）一张表 TFT_STACKS：tft.dll 用同一份 stacks.rs（`#[path]`）和自己的 addons/tft/src/stack_table.rs，
  数据是 tft/champion/ 里的。云顶英雄多半是 tft.dll 的原生被动在叠（`passive`）。
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEAGUE = os.path.join(ROOT, "league")
TABLE_RS = os.path.join(ROOT, "addons", "league_main", "src", "stack_table.rs")
TFT_TABLE_RS = os.path.join(ROOT, "addons", "tft", "src", "stack_table.rs")
FIELD = "stack_skill_index"

# ---------------------------------------------------------------------------------------------------------------- table
# hero -> how to read the number from his own buffs:
#   count:  the instances of one buff (a stack is one more instance)
#   sum:    one stat of those instances added up, when a stack is not always one (Veigar's champion stack is 5 ability
#           power: League counts it 5 stacks, the number is his ability power from it; Nasus's Siphoning Strike damage;
#           Sion's health from kills) - "stat" names the field (magic_power / hp / attack / defence / attack_speed_mult /
#           damaged_reduce); with "per" (a passive param of the hero's data: 一层的量) the sum divided by it, rounded
#   ladder: the highest k with <prefix><k> on him, k = 1..rungs, times "step" (default 1: Rumble's heat and Gnar's /
#           Shyvana's rage 10 a rung, Tryndamere's fury 20 - League's 0..100); with "full" (a flag buff: Darius's Noxian
#           Might, Gnar's full Rage) on him, the number is "top"
#   most:   {名字: 数}，身上有的里面取最大（亚索 q_stack 1 / q_ready 2；阿狸的第 6 级叫 et_ready）
#   total:  {名字: 数}，身上有的加起来，同名只算一次（厄斐琉斯的子弹是二进制 b0..b4；辛德拉四个各自到时的法球槽）
#   prefix: 名字以它开头的 buff 有几个（附加包挂在敌人身上的层数，名字后面带施法者的实体号）
#   charges: 技能格（0 技能、1 技能 2、2 大招）的充能还剩几次，读游戏自己的冷却（数据的 cooltime_use_count），不是 buff
# cap: the most the number shows; skill: whose icon the panel shows beside it (0 skill, 1 skill2, 2 ult - the ability
# the stacks feed, else the first); label: what the number is (for --list and the docs); passive: an add-on's own
# counter (its code writes the rungs, no data does) - only the copy whose passive is that native shows the box, the
# main pack's kit (no add-on, the number would stay 0) does not
# on: "foes" 数每个活着的敌方英雄身上的，取最多的那个；native: 这些附加包的原生代码挂同样的名字（它们的副本数据里没有，
# 只给 --check 看）。同一个英雄的几行：图标一样，league.dll 取最大的。
STACKS = [
    {"hero": "league_veigar", "sum": "league_veigar_p_stack", "stat": "magic_power", "cap": 999, "skill": 0,
     "label": "维迦「超凡邪力」叠的法术强度（英雄联盟的层数）"},
    {"hero": "league_nasus", "sum": "league_nasus_q_stack", "stat": "magic_power", "cap": 999, "skill": 0,
     "label": "内瑟斯「汲魂痛击」叠的伤害（英雄联盟的层数）"},
    {"hero": "league_chogath", "count": "league_chogath_r_stack", "cap": 999, "skill": 2, "label": "科加斯「盛宴」层数"},
    {"hero": "league_smolder", "count": "league_smolder_p_st", "cap": 999, "skill": 0, "label": "斯莫德「龙之研习」层数"},
    {"hero": "league_senna", "count": "league_senna_mist", "cap": 999, "skill": 0, "label": "赛娜「赦除」黑雾层数"},
    {"hero": "league_swain", "count": "league_swain_frag", "cap": 999, "skill": 2, "label": "斯维因「灵魂碎片」"},
    {"hero": "league_sion", "sum": "league_sion_k_hp", "stat": "hp", "cap": 999, "skill": 0, "native": ["league_sion"],
     "label": "赛恩「灵魂熔炉」击杀加的生命"},
    {"hero": "league_kindred", "count": "league_kindred_p_mark", "cap": 999, "skill": 0, "native": ["league_kindred"],
     "label": "千珏「千珏之印」印记"},
    {"hero": "league_aurelionsol", "ladder": "league_aurelionsol_d", "rungs": 30, "cap": 30, "skill": 2,
     "label": "奥瑞利安·索尔「星海焕然」星尘层数"},
    {"hero": "league_belveth", "ladder": "league_belveth_l", "rungs": 8, "cap": 8, "skill": 0,
     "label": "卑尔维斯「溶烛化紫」永久攻速层数"},
    # the capped counters League shows that had no picture, or one only when full (the user, 2026-11-11: 「加常见的那些」)
    {"hero": "league_caitlyn", "ladder": "league_caitlyn_hs_", "rungs": 5, "cap": 5, "skill": 0,
     "label": "凯特琳「爆头」计数（第 6 发爆头）"},
    {"hero": "league_darius", "ladder": "league_darius_hemo_", "rungs": 4, "full": "league_darius_might", "top": 5,
     "cap": 5, "skill": 2, "label": "德莱厄斯「出血」层数（5 = 诺克萨斯之力）"},
    {"hero": "league_pantheon", "ladder": "league_pantheon_m", "rungs": 4, "full": "league_pantheon_pw", "top": 5,
     "cap": 5, "skill": 0, "label": "潘森「矢志不退」层数（5 = 下一个技能强化）"},
    {"hero": "league_kennen", "ladder": "league_kennen_a_", "rungs": 4, "cap": 4, "skill": 0,
     "label": "凯南「电刃」普攻计数（第 5 下）"},
    {"hero": "league_jinx", "ladder": "league_jinx_revup_", "rungs": 3, "cap": 3, "skill": 0, "label": "金克丝「砰砰」攻速层数"},
    {"hero": "league_masteryi", "ladder": "league_masteryi_ds_", "rungs": 3, "cap": 3, "skill": 0, "label": "易「双重打击」计数"},
    {"hero": "league_twistedfate", "ladder": "league_twistedfate_e", "rungs": 3, "cap": 3, "skill": 0,
     "label": "崔斯特「卡牌骗术」计数（第 4 下）"},
    {"hero": "league_rumble", "ladder": "league_rumble_h", "rungs": 9, "step": 10, "full": "league_rumble_oh", "top": 100,
     "cap": 100, "skill": 0, "label": "兰博「机械重组」热量（100 = 过热）"},
    {"hero": "league_annie", "ladder": "league_annie_pyro_", "rungs": 3, "full": "league_annie_pyro_ready", "top": 4,
     "cap": 4, "skill": 0, "label": "安妮「嗜火」层数（4 = 下一个技能晕人）"},
    {"hero": "league_irelia", "ladder": "league_irelia_pv", "rungs": 4, "cap": 4, "skill": 0,
     "label": "艾瑞莉娅「艾欧尼亚热诚」层数"},
    {"hero": "league_kayle", "ladder": "league_kayle_zeal", "rungs": 5, "cap": 5, "skill": 0, "label": "凯尔「狂热」层数"},
    {"hero": "league_gnar", "ladder": "league_gnar_rg", "rungs": 9, "step": 10, "full": "league_gnar_full", "top": 100,
     "cap": 100, "skill": 2, "label": "纳尔「狂怒基因」怒气（100 = 满怒）"},
    {"hero": "league_shyvana", "ladder": "league_shyvana_fy", "rungs": 9, "step": 10, "full": "league_shyvana_full",
     "top": 100, "cap": 100, "skill": 2, "label": "希瓦娜「魔龙降世」龙怒（100 = 满）"},
    {"hero": "league_tryndamere", "ladder": "league_tryndamere_f_", "rungs": 5, "step": 20, "cap": 100, "skill": 0,
     "label": "泰达米尔「战斗狂怒」怒气"},
    # the Bonetooth Necklace's trophies (2026-11-14, with League's necklace itself): the main kit and league_rengar_bush
    # both hang league_rengar_bt1..bt5 one after another, so the highest rung on him is the count
    {"hero": "league_rengar", "ladder": "league_rengar_bt", "rungs": 5, "cap": 5, "skill": 2,
     "native": ["league_rengar_bush"], "label": "雷恩加尔「骨齿项链」战利品"},
    # the add-on's Silver Serpents in hand (2026-11-12, the user: 「船长银蛇币的系统能做吗」): league_gangplank writes
    # league_gangplank_sv_<n> (its unit test serpent_count_on_the_panel)
    {"hero": "league_gangplank", "ladder": "league_gangplank_sv_", "rungs": 9999, "cap": 9999, "skill": 2,
     "passive": "league_gangplank:scurvy", "label": "普朗克「银蛇币」（附加包）"},
    # the add-on's Hex Fragments in hand (2026-11-14, the user: 「吉格斯和维克托按照联盟的重做」): league_viktor writes
    # exactly one league_viktor_hex_<held> (none at 0); the main pack's level-based kit has no fragments, so no box
    {"hero": "league_viktor", "ladder": "league_viktor_hex_", "rungs": 999, "cap": 999, "skill": 0,
     "passive": "league_viktor:evolve", "label": "维克托「光荣进化」攒着的海克斯碎片（附加包）"},

    # ---- 2026-11-22 补的（用户：「还有很多叠层的技能在技能列表里看不到层数 想个办法解决一下」）----
    # 主包和附加包的副本都挂同一套名字的
    {"hero": "league_alistar", "ladder": "league_alistar_e", "rungs": 4, "full": "league_alistar_e_ready", "top": 5,
     "cap": 5, "skill": 0, "label": "阿利斯塔「践踏」踩中英雄的次数（5 = 下次普攻眩晕）"},
    {"hero": "league_aphelios", "total": {"league_aphelios_b0": 1, "league_aphelios_b1": 2, "league_aphelios_b2": 4,
                                          "league_aphelios_b3": 8, "league_aphelios_b4": 16},
     "cap": 31, "skill": 0, "label": "厄斐琉斯主手武器剩下的子弹（每把 20 发）"},
    {"hero": "league_aurora", "ladder": "league_aurora_s_", "rungs": 2, "cap": 2, "skill": 0,
     "label": "阿萝拉「驱灵奇术」层数（第 3 层抽出灵物）"},
    {"hero": "league_aurora", "ladder": "league_aurora_p", "rungs": 2, "on": "foes", "cap": 2, "skill": 0,
     "native": ["league_aurora"], "label": "阿萝拉敌人身上最多的「驱灵奇术」（附加包 0.4.0 起按敌人分别叠）"},
    {"hero": "league_diana", "ladder": "league_diana_ms_", "rungs": 2, "cap": 2, "skill": 0,
     "label": "黛安娜「月银之刃」普攻计数（第 3 下顺劈）"},
    {"hero": "league_draven", "ladder": "league_draven_p_", "rungs": 6, "cap": 6, "skill": 0,
     "label": "德莱文「德莱文联盟」崇拜层数"},
    {"hero": "league_ekko", "ladder": "league_ekko_z", "rungs": 2, "cap": 2, "skill": 0,
     "label": "艾克「Z型驱动共振」层数（第 3 层爆发）"},
    {"hero": "league_elise", "ladder": "league_elise_sl", "rungs": 3, "cap": 3, "skill": 0,
     "label": "伊莉丝「蜘蛛女皇」攒着的小蜘蛛"},
    {"hero": "league_ezreal", "ladder": "league_ezreal_rsf_", "rungs": 5, "cap": 5, "skill": 0,
     "label": "伊泽瑞尔「咒能高涨」攻速层数"},
    {"hero": "league_graves", "ladder": "league_graves_e_g", "rungs": 4, "cap": 4, "skill": 1,
     "label": "格雷福斯「纯爷们」层数"},
    {"hero": "league_gwen", "ladder": "league_gwen_qs", "rungs": 4, "cap": 4, "skill": 0, "label": "格温「剪刀层数」"},
    {"hero": "league_hecarim", "ladder": "league_hecarim_q", "rungs": 2, "cap": 2, "skill": 0,
     "label": "赫卡里姆「暴走」层数"},
    {"hero": "league_jax", "ladder": "league_jax_ra_", "rungs": 8, "cap": 8, "skill": 0, "label": "贾克斯「无情连打」攻速层数"},
    {"hero": "league_jhin", "ladder": "league_jhin_a_", "rungs": 3, "cap": 3, "skill": 0,
     "label": "烬「低语」打出的发数（第 4 发必暴击）"},
    {"hero": "league_kalista", "ladder": "league_kalista_h", "rungs": 3, "cap": 3, "skill": 1,
     "label": "卡莉丝塔插着的矛（插满 3 支自动拔出）"},
    {"hero": "league_kassadin", "ladder": "league_kassadin_r_s", "rungs": 3, "cap": 3, "skill": 2,
     "label": "卡萨丁「虚空行走」层数"},
    {"hero": "league_kled", "ladder": "league_kled_c", "rungs": 9, "step": 10, "cap": 100, "skill": 0,
     "label": "克烈下马时的勇气（满 100 上马）"},
    {"hero": "league_kogmaw", "most": {"league_kogmaw_r_vol": 1, "league_kogmaw_r_c1": 2}, "cap": 2, "skill": 2,
     "label": "克格莫「活体大炮」这一轮打了几发（第 3 发后进冷却）"},
    {"hero": "league_ksante", "ladder": "league_ksante_q_s", "rungs": 2, "cap": 2, "skill": 0,
     "label": "奎桑提 Q 层数（2 层时变冲击波）"},
    {"hero": "league_lillia", "ladder": "league_lillia_p", "rungs": 4, "cap": 4, "skill": 0, "label": "莉莉娅「腾跃」层数"},
    {"hero": "league_mel", "most": {"league_mel_p_3": 3, "league_mel_p_6": 6, "league_mel_p_9": 9}, "cap": 9,
     "skill": 0, "label": "梅尔「灼灼之光」下次普攻多射的光弹"},
    {"hero": "league_mordekaiser", "ladder": "league_mordekaiser_p_s", "rungs": 2, "full": "league_mordekaiser_p_on",
     "top": 3, "cap": 3, "skill": 0, "label": "莫德凯撒被动层数（3 = 黑暗之力开着）"},
    {"hero": "league_orianna", "ladder": "league_orianna_p", "rungs": 2, "cap": 2, "skill": 0,
     "label": "奥莉安娜「发条协奏」层数"},
    {"hero": "league_reksai", "ladder": "league_reksai_f", "rungs": 4, "step": 25, "cap": 100, "skill": 0,
     "label": "雷克塞「艾克塞之怒」怒气（100 = 狂野之噬）"},
    {"hero": "league_renekton", "ladder": "league_renekton_f", "rungs": 5, "step": 20, "cap": 100, "skill": 0,
     "label": "雷克顿「怒之领域」怒气（100 = 下一个技能强化）"},
    {"hero": "league_riven", "ladder": "league_riven_rune_", "rungs": 3, "cap": 3, "skill": 0,
     "label": "锐雯「符文之刃」层数"},
    {"hero": "league_samira", "ladder": "league_samira_g", "rungs": 6, "cap": 6, "skill": 2,
     "label": "莎弥拉「悍勇本色」评价（1 = E … 6 = S，S 才放大招）"},
    {"hero": "league_seraphine", "most": {"league_seraphine_c1": 1, "league_seraphine_echo": 2}, "cap": 2, "skill": 0,
     "label": "萨勒芬妮「星光漫射」计数（2 = 下一个技能回音）"},
    {"hero": "league_sett", "ladder": "league_sett_grit_", "rungs": 5, "cap": 5, "skill": 1, "label": "瑟提「豪意」层数"},
    {"hero": "league_shen", "ladder": "league_shen_q_", "rungs": 3, "cap": 3, "skill": 0,
     "label": "慎「暮临」剩下的强化普攻"},
    {"hero": "league_sona", "ladder": "league_sona_pc_", "rungs": 2, "full": "league_sona_pc_ready", "top": 3, "cap": 3,
     "skill": 0, "label": "娑娜「强音」计数（3 = 下次普攻强化）"},
    {"hero": "league_sylas", "ladder": "league_sylas_p_", "rungs": 2, "cap": 2, "skill": 0,
     "label": "塞拉斯「破敌禁法」层数"},
    {"hero": "league_syndra", "total": {"league_syndra_o1": 1, "league_syndra_o2": 1, "league_syndra_o3": 1,
                                        "league_syndra_o4": 1},
     "cap": 4, "skill": 2, "label": "辛德拉场上的法球（大招多发几颗）"},
    {"hero": "league_taric", "ladder": "league_taric_q_s", "rungs": 3, "cap": 3, "skill": 1,
     "label": "塔里克「星光之触」充能"},
    {"hero": "league_tristana", "ladder": "league_tristana_e_", "rungs": 3, "cap": 3, "skill": 0,
     "label": "崔丝塔娜「爆炸火花」炸弹层数（第 4 下引爆）"},
    {"hero": "league_vi", "ladder": "league_vi_d_", "rungs": 2, "cap": 2, "skill": 0,
     "label": "蔚「爆弹重拳」普攻计数（第 3 下）"},
    {"hero": "league_volibear", "ladder": "league_volibear_p", "rungs": 5, "cap": 5, "skill": 0,
     "label": "沃利贝尔「狂雷渐起」攻速层数"},
    {"hero": "league_wukong", "ladder": "league_wukong_s_", "rungs": 5, "cap": 5, "skill": 0,
     "label": "孙悟空「金刚不坏」层数"},
    {"hero": "league_xayah", "ladder": "league_xayah_p", "rungs": 5, "cap": 5, "skill": 0,
     "label": "霞「锐切」存着的穿透普攻"},
    {"hero": "league_xinzhao", "ladder": "league_xinzhao_p_", "rungs": 2, "cap": 2, "skill": 0,
     "label": "赵信「果决」普攻计数（第 3 下）"},
    {"hero": "league_yasuo", "most": {"league_yasuo_q_stack": 1, "league_yasuo_q_ready": 2}, "cap": 2, "skill": 0,
     "label": "亚索「旋风烈斩」层数（2 = 下一次放旋风）"},
    {"hero": "league_yone", "most": {"league_yone_q_stack": 1, "league_yone_q_ready": 2}, "cap": 2, "skill": 0,
     "label": "永恩「风暴聚集」层数（2 = 下一次冲刺击飞）"},
    {"hero": "league_yunara", "ladder": "league_yunara_u", "rungs": 3, "cap": 3, "skill": 0,
     "label": "芸阿娜「灵蕴」（满了自动开启）"},
    {"hero": "league_zeri", "ladder": "league_zeri_c", "rungs": 4, "step": 20, "full": "league_zeri_p_full", "top": 100,
     "cap": 100, "skill": 0, "label": "泽丽「内能迁转」电量（100 = 下一击电击弹）"},
    # 英雄联盟在图标上显示弹药的充能技能（2026-11-22）：游戏自己的技能格只画冷却秒数（ingame 布局 skill_slot 只有
    # #icon、#cooldown；0.7.3 面板在 RVA 0xc743dc 一带把剩余冷却除以每秒 tick 数写成文字、为 0 就藏），不画充能数。
    # 凯特琳 W、蔚 E 也有充能，但她们已经有层数行（爆头、爆弹重拳）；锐雯 Q、亚托克斯 Q 英雄联盟是三段施放，不是弹药
    {"hero": "league_teemo", "charges": 2, "cap": 3, "skill": 2, "label": "提莫「种蘑菇」存着的蘑菇（充能）"},
    {"hero": "league_corki", "charges": 2, "cap": 4, "skill": 2, "label": "库奇「火箭轰击」存着的导弹（充能）"},
    {"hero": "league_milio", "charges": 1, "cap": 2, "skill": 1, "label": "米利欧「融融情谊」充能"},
    # 附加包照英雄联盟改了数法、主包副本的名字不再挂：olaf_rage 照已损失生命挂同样的 p_1..p_4
    {"hero": "league_olaf", "ladder": "league_olaf_p_", "rungs": 4, "cap": 4, "skill": 0, "native": ["league_olaf_rage"],
     "label": "奥拉夫「狂战之怒」层数"},
    # 主包记在他自己身上（打谁都叠一个数），附加包记在每个敌人身上：两行，各在自己那份数据里读得出
    {"hero": "league_akshan", "ladder": "league_akshan_p_", "rungs": 2, "cap": 2, "skill": 0,
     "label": "阿克尚「无所不用」命中计数（第 3 下）"},
    {"hero": "league_akshan", "prefix": "league_akshan_p_s:", "on": "foes", "cap": 2, "skill": 0,
     "native": ["league_akshan"], "label": "阿克尚「无所不用」同一个敌人挨的下数（附加包）"},
    {"hero": "league_sejuani", "ladder": "league_sejuani_f", "rungs": 3, "cap": 3, "skill": 0,
     "label": "瑟庄妮霜冻层数（第 4 层冻住）"},
    {"hero": "league_sejuani", "count": "league_sejuani_frost", "on": "foes", "cap": 3, "skill": 0,
     "native": ["league_sejuani"], "label": "瑟庄妮敌人身上最多的霜冻（附加包）"},
    {"hero": "league_skarner", "ladder": "league_skarner_qk", "rungs": 2, "cap": 2, "skill": 0,
     "label": "斯卡纳「战栗」层数（第 3 层）"},
    {"hero": "league_skarner", "prefix": "league_skarner_qk_", "on": "foes", "cap": 3, "skill": 0,
     "native": ["league_skarner"], "label": "斯卡纳敌人身上最多的「战栗」（附加包）"},
    {"hero": "league_tahmkench", "ladder": "league_tahmkench_t", "rungs": 3, "cap": 3, "skill": 0,
     "label": "塔姆「培养品味」层数"},
    {"hero": "league_tahmkench", "count": "league_tahmkench_t_mark", "on": "foes", "cap": 3, "skill": 0,
     "native": ["league_tahmkench"], "label": "塔姆敌人身上最多的「培养品味」（附加包）"},
    {"hero": "league_talon", "ladder": "league_talon_p_", "rungs": 3, "cap": 3, "skill": 0,
     "label": "泰隆「刀锋之末」伤口层数（3 层后下次普攻流血）"},
    {"hero": "league_talon", "count": "league_talon_vault_w", "on": "foes", "cap": 3, "skill": 0,
     "native": ["league_talon_vault"], "label": "泰隆敌人身上最多的伤口（附加包）"},
    {"hero": "league_varus", "ladder": "league_varus_b_", "rungs": 3, "cap": 3, "skill": 0, "label": "韦鲁斯「枯萎」层数"},
    {"hero": "league_varus", "ladder": "league_varus_blight_", "rungs": 3, "on": "foes", "cap": 3, "skill": 0,
     "native": ["league_varus_blight"], "label": "韦鲁斯敌人身上最多的「枯萎」（附加包）"},
    {"hero": "league_vayne", "ladder": "league_vayne_sb", "rungs": 2, "cap": 2, "skill": 0,
     "label": "薇恩「圣银弩箭」计数（第 3 下）"},
    {"hero": "league_vayne", "count": "league_vayne_bolts_s", "on": "foes", "cap": 2, "skill": 0,
     "native": ["league_vayne_bolts"], "label": "薇恩同一个敌人身上的「圣银弩箭」（附加包）"},
    {"hero": "league_velkoz", "ladder": "league_velkoz_p_", "rungs": 2, "cap": 2, "skill": 0,
     "label": "维克兹「有机体解构」层数（第 3 层）"},
    {"hero": "league_velkoz", "prefix": "league_velkoz_pd_", "on": "foes", "cap": 3, "skill": 0,
     "native": ["league_velkoz"], "label": "维克兹敌人身上最多的「有机体解构」（附加包）"},
    # 附加包记在敌人身上、主包那份数法在附加包的副本里也读得出（布兰德的 b_1 附加包还在刷新、布隆的 p_mark 主包也挂在敌人
    # 身上当图、图奇的 h1..h4 两份都有）：只给附加包的副本层数格，主包的不给
    {"hero": "league_brand", "prefix": "league_brand_bz_", "on": "foes", "cap": 3, "skill": 0,
     "passive": "league_brand:watch", "label": "布兰德敌人身上最多的「炽热之焰」（附加包）"},
    {"hero": "league_braum", "count": "league_braum_p_mark", "on": "foes", "cap": 3, "skill": 0,
     "passive": "league_braum:heart", "label": "布隆敌人身上最多的「震荡猛击」（附加包，第 4 层眩晕）"},
    {"hero": "league_twitch", "ladder": "league_takedowns_tw_v", "rungs": 6, "on": "foes", "cap": 6, "skill": 1,
     "passive": "league_takedowns:twitch", "label": "图奇敌人身上最多的「死亡毒液」（附加包）"},
    # 附加包原生代码里才有的数：附加包自己在英雄身上挂梯子（照普朗克 / 维克托），主包的数据梯子留一行给不装附加包的
    {"hero": "league_ahri", "most": {"league_ahri_et1": 1, "league_ahri_et2": 2, "league_ahri_et3": 3,
                                     "league_ahri_et4": 4, "league_ahri_et5": 5, "league_ahri_et_ready": 6,
                                     "league_ahri_et7": 7, "league_ahri_et8": 8},
     "cap": 8, "skill": 0, "label": "阿狸「摄魂夺魄」精魄层数（第 9 层回血）"},
    {"hero": "league_ahri", "ladder": "league_ahri_es_", "rungs": 99, "cap": 99, "skill": 0,
     "passive": "league_ahri:essence", "label": "阿狸「摄魂夺魄」精魄层数（附加包）"},
    {"hero": "league_kaisa", "ladder": "league_kaisa_pl_", "rungs": 4, "cap": 4, "skill": 0,
     "label": "卡莎「体表活肤」电浆层数（第 5 层引爆）"},
    {"hero": "league_kaisa", "ladder": "league_kaisa_pn_", "rungs": 4, "cap": 4, "skill": 0,
     "passive": "league_marks:kaisa", "label": "卡莎敌人身上最多的电浆（附加包）"},
    {"hero": "league_locke", "ladder": "league_locke_r_s", "rungs": 3, "cap": 3, "skill": 2,
     "label": "洛克「万魔狱」封印层数"},
    {"hero": "league_locke", "ladder": "league_locke_sl_", "rungs": 3, "cap": 3, "skill": 2,
     "passive": "league_locke:exorcist", "label": "洛克「万魔狱」封印层数（附加包，整局都在）"},
    {"hero": "league_zaahen", "ladder": "league_zaahen_d", "rungs": 11, "full": "league_zaahen_full", "top": 12,
     "cap": 12, "skill": 0, "label": "亚恒「不落之志」果决层数（12 = 满）"},
    {"hero": "league_zaahen", "ladder": "league_zaahen_dn_", "rungs": 12, "cap": 12, "skill": 0,
     "passive": "league_zaahen:darkin", "label": "亚恒「不落之志」果决层数（附加包）"},
    # 约里克的坟（2026-11-22）：主包和附加包的副本都把 g1..g4 一起挂、一起计时（tools/kit/build_yorick.py），最高一级就是坟数
    {"hero": "league_yorick", "ladder": "league_yorick_g", "rungs": 4, "cap": 4, "skill": 0,
     "label": "约里克「牧魂人」坟数（3 座起唤醒雾行者）"},
]

# 云顶（tft 包，2026-11-22）：tft.dll 的表（addons/tft/src/stack_table.rs），数据在 tft/champion/。cap / per 写成字符串的是
# 那个英雄数据 passive.params 里的参数（tft.dll 按它们叠，表跟着数据走）。多半是 tft.dll 的原生被动在叠（passive）；
# 拉露恩、绯红树怪、希尔科是数据自己的梯子
TFT_STACKS = [
    {"hero": "tft_alune", "ladder": "tft_alune_ph", "rungs": 3, "cap": 3, "skill": 2,
     "label": "拉露恩「月相」（3 = 满月，大招砸得更重）"},
    {"hero": "tft_cinderling", "ladder": "tft_cinderling_p_", "rungs": 3, "full": "tft_cinderling_p_full", "top": 4,
     "cap": 4, "skill": 0, "label": "绯红树怪「绯红霸符」层数（4 = 满，普攻灼烧英雄）"},
    {"hero": "tft_silco", "ladder": "tft_silco_d", "rungs": 5, "cap": 5, "skill": 0, "label": "希尔科「主宰」法强层数"},
    {"hero": "tft_gromp", "count": "tft_gromp_p_ap", "cap": "p_max", "skill": 0, "passive": "tft_gromp:purple",
     "label": "魔沼蛙「紫霸符」法强层数"},
    {"hero": "tft_sohm", "count": "tft_sohm_p_tide", "cap": "p_max", "skill": 0, "passive": "tft_sohm:lagoon",
     "label": "索姆「碧波之力」潮水层数"},
    {"hero": "tft_raptor", "count": "tft_raptor_p_shred", "on": "foes", "cap": "p_max", "skill": 0,
     "passive": "tft_raptor:flock", "label": "深红锋喙鸟「橙霸符」敌人身上最多的碎甲层数"},
    {"hero": "tft_syfen", "sum": "tft_syfen_p_rage", "stat": "attack", "per": "p_ad", "cap": "p_max", "skill": 0,
     "passive": "tft_syfen:whisper", "label": "赛芬「幽影低语」怒气层数"},
    {"hero": "tft_maddie", "sum": "tft_maddie_p_bounty", "stat": "attack_speed_mult", "per": "w_as", "cap": "w_max",
     "skill": 1, "passive": "tft_maddie:sniper", "label": "麦迪「通缉令」领到的赏金（份）"},
    {"hero": "tft_zippy", "sum": "tft_zippy_p_guild", "stat": "defence", "per": "p_def", "cap": "p_max", "skill": 0,
     "passive": "tft_zippy:guild", "label": "呲呲「冒险家之魂」身边的队友"},
    {"hero": "tft_riftherald", "sum": "tft_riftherald_p_shell", "stat": "damaged_reduce", "cap": 90, "skill": 0,
     "passive": "tft_riftherald:shell", "label": "峡谷先锋「虚空甲壳」受到的伤害减少（%）"},
]
# 包 -> (表, 生成的 Rust 表, 表里英雄的前缀, 谁读它)
TABLES = {"league": (STACKS, TABLE_RS, "league_", "league.dll"), "tft": (TFT_STACKS, TFT_TABLE_RS, "tft_", "tft.dll")}
ALL = STACKS + TFT_STACKS


# --------------------------------------------------------------------------------------------------------- the data
RULES = ("count", "sum", "ladder", "most", "total", "prefix", "charges")
SLOTS = ("skill", "skill2", "ult")      # 技能格 0 / 1 / 2：stack_skill_index 和 charges 都这么数


def rows(hero):
    return [r for r in ALL if r["hero"] == hero]


def row(hero):
    """The hero's first row (or None)."""
    return next(iter(rows(hero)), None)


def passive_ref(champ):
    """The native passive a copy calls (an add-on's), or None."""
    p = champ.get("passive")
    return p.get("passive_ref") if isinstance(p, dict) else None


def applies(r, champ):
    """这一行给不给这份英雄数据层数格：带 passive 的只给调那个原生被动的副本，别的给每一份。"""
    return r["passive"] == passive_ref(champ) if "passive" in r else True


def apply(champ):
    """The champion with his panel icon (`stack_skill_index`) when he is listed, and without the over-head number
    bindings (`<hero>_sn_*`) of the first version; other keys and views keep their order."""
    hero = champ.get("id", "")
    prefix = f"{hero}_sn_"
    if any(str(v.get("name", "")).startswith(prefix) for v in champ.get("view_buffs", [])):
        champ["view_buffs"] = [v for v in champ["view_buffs"] if not str(v.get("name", "")).startswith(prefix)]
    mine = rows(hero)
    if not mine:
        return champ
    here = [r for r in mine if applies(r, champ)]
    if here:
        champ[FIELD] = here[0]["skill"]
    else:
        champ.pop(FIELD, None)      # an add-on's counter: not in a copy without its passive
    return champ


def wrap(build):
    """`build = stack_nums.wrap(build)` under a kit script's build(): every caller gets the kit with the field."""
    import functools

    @functools.wraps(build)
    def built(*a, **k):
        return apply(build(*a, **k))
    return built


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def copies():
    """Every data file of a hero: league/champion/, the add-ons' override/ copies and tft/champion/."""
    return sorted(glob.glob(os.path.join(LEAGUE, "champion", "*.data_champion")) +
                  glob.glob(os.path.join(ROOT, "addons", "*", "override", "*.data_champion")) +
                  glob.glob(os.path.join(ROOT, "tft", "champion", "*.data_champion")))


def main_data(hero):
    """这个英雄自己包里的那份数据（英雄联盟的在 league/，云顶的在 tft/）。"""
    pack = "tft" if hero.startswith("tft_") else "league"
    return load(os.path.join(ROOT, pack, "champion", hero + ".data_champion"))


def param(r, key):
    """cap / per：数字照写；字符串是这个英雄数据 passive.params 里的参数。"""
    v = r[key]
    if isinstance(v, str):
        p = main_data(r["hero"]).get("passive") or {}
        v = (p.get("params") or {}).get(v)
    return v


def addon_of(path):
    """这份数据是哪个附加包的副本（主包的是 None）。"""
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/").split("/")
    return rel[1] if rel[0] == "addons" else None


def load(path):
    return json.loads(open(path, "rb").read().decode("utf-8"))


def data_problems(write=False):
    out = []
    for path in copies():
        raw = open(path, "rb").read().decode("utf-8")
        champ = json.loads(raw)
        if champ.get("id") != os.path.basename(path).split(".")[0]:
            continue
        want = apply(json.loads(raw))
        if want == champ:
            continue
        if write:
            new = dumps_main(want)
            if "\r\n" not in raw:       # the add-ons' make_override.py write LF (git stores LF either way)
                new = new.replace("\r\n", "\n")
            if raw.count("\n") <= 1:    # 一行的紧凑副本（塞拉斯的带着所有人的大招）照原样写成一行
                new = json.dumps(want, ensure_ascii=False, separators=(",", ":")) + "\n"
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            out.append(f"wrote {os.path.relpath(path, ROOT)}")
        else:
            out.append(f"{os.path.relpath(path, ROOT)}: its {FIELD} is not up to date: python tools/kit/stack_nums.py --write")
    return out


# ------------------------------------------------------------------------------------------------------- league.dll
STATS = {"magic_power": "MagicPower", "hp": "Hp", "attack": "Attack", "defence": "Defence",
         "attack_speed_mult": "AttackSpeedMult", "damaged_reduce": "DamagedReduce"}


def pairs_rs(d):
    return "&[" + ", ".join(f'("{n}", {v})' for n, v in d.items()) + "]"


def rule_rs(r):
    if "count" in r:
        return f'Rule::Count("{r["count"]}")'
    if "sum" in r and "per" in r:
        return f'Rule::Per("{r["sum"]}", Stat::{STATS[r["stat"]]}, {param(r, "per")})'
    if "sum" in r:
        return f'Rule::Sum("{r["sum"]}", Stat::{STATS[r["stat"]]})'
    if "most" in r:
        return f'Rule::Most({pairs_rs(r["most"])})'
    if "total" in r:
        return f'Rule::Total({pairs_rs(r["total"])})'
    if "prefix" in r:
        return f'Rule::Prefix("{r["prefix"]}")'
    if "charges" in r:
        return f'Rule::Charges({r["charges"]})'
    full = f'Some(("{r["full"]}", {r["top"]}))' if "full" in r else "None"
    return (f'Rule::Ladder {{ prefix: "{r["ladder"]}", rungs: {r["rungs"]}, step: {r.get("step", 1)}, '
            f'full: {full} }}')


def table_rs(pack="league"):
    table, _, prefix, dll = TABLES[pack]
    name = "STACKS" if pack == "league" else "TFT_STACKS"
    head = "src/stacks.rs" if pack == "league" else "league_main's src/stacks.rs"
    lines = [f"//! The stack counts {dll} writes for the champion panel ({head}): generated by",
             f"//! tools/kit/stack_nums.py from its {name} - do not edit by hand.", "",
             "use super::stacks::{Rule, Stack, Stat};", "",
             "/// 表里的英雄都以它开头（stacks.rs 翻表前先比它，the_table_is_sound 也按它查）。",
             f'pub const PREFIX: &str = "{prefix}";', "",
             f"pub const STACKS: [Stack; {len(table)}] = ["]
    for r in sorted(table, key=lambda r: r["hero"]):       # stable: a hero's rows keep the table's order
        foes = "true" if r.get("on") == "foes" else "false"
        lines.append(f'    Stack {{ hero: "{r["hero"]}", rule: {rule_rs(r)}, cap: {param(r, "cap")}, foes: {foes}, '
                     f'skill: {r["skill"]} }},')
    lines += ["];", ""]
    return "\n".join(lines)


def table_problems():
    out = []
    for pack, (_, path, _, _) in TABLES.items():
        have = open(path, encoding="utf-8").read().replace("\r\n", "\n") if os.path.exists(path) else ""
        if have != table_rs(pack):
            out.append(f"{os.path.relpath(path, ROOT)} is out of date: python tools/kit/stack_nums.py --write")
    return out


def names(r):
    """The buff names a row reads (a ladder: its first and last rung and the flag; a prefix: the prefix itself)."""
    if "count" in r:
        return [r["count"]]
    if "sum" in r:
        return [r["sum"]]
    if "most" in r or "total" in r:
        return list(r.get("most") or r["total"])
    if "prefix" in r:
        return [r["prefix"]]
    if "charges" in r:
        return []
    return [f'{r["ladder"]}{k}' for k in (1, r["rungs"])] + ([r["full"]] if "full" in r else [])


def added(champ):
    """这份数据里挂过的 buff 名字（AddCasterBuff / AddBuff）。"""
    out = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") in ("AddCasterBuff", "AddBuff") and isinstance(o.get("buff_state"), dict):
                out.add(o["buff_state"].get("name"))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(champ)
    return out


def live(r, path, champ, have):
    """这一行在这份数据里读不读得出数：原生被动对得上、它是 native 那个附加包的副本，或者名字在这份数据里有人挂。"""
    if "passive" in r:
        return passive_ref(champ) == r["passive"]
    if addon_of(path) in r.get("native", ()):
        return True
    if "prefix" in r:
        return any(n and n.startswith(r["prefix"]) for n in have)
    if "charges" in r:     # 充能：这份数据里那个技能有不止 1 次的充能
        slot = champ.get(SLOTS[r["charges"]])
        return isinstance(slot, dict) and slot.get("cooltime_use_count", 0) > 1
    return all(n in have for n in names(r))


def rules_problems():
    """Every row reads something in some copy of its hero (a renamed buff would count nothing), every copy that shows
    the box has a row that reads something in it, every icon is one of his three, a hero's rows share their icon, and
    nothing still draws the old over-head numbers. An add-on's own counter ("passive"): some copy of the hero calls
    that passive (its code writes the rungs, its unit tests check the names)."""
    out = []
    by_hero = {}
    for path in copies():
        champ = load(path)
        if champ.get("id") == os.path.basename(path).split(".")[0]:
            by_hero.setdefault(champ["id"], []).append((path, champ))
    addons = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, "addons", "*", "Cargo.toml"))}
    for r in ALL:
        h = r["hero"]
        kinds = [k for k in RULES if k in r]
        if len(kinds) != 1:
            out.append(f"{h}: one rule of {RULES} a row, not {kinds}")
            continue
        if r["skill"] not in (0, 1, 2):
            out.append(f"{h}: skill {r['skill']} is not 0, 1 or 2")
        if r.get("on", "foes") != "foes":
            out.append(f"{h}: on {r['on']!r} (only \"foes\")")
        if not any(h.startswith(t[2]) and r in t[0] for t in TABLES.values()):
            out.append(f"{h}: not in the table of its pack (league_ in STACKS, tft_ in TFT_STACKS)")
        if not isinstance(param(r, "cap"), int) or param(r, "cap") <= 0:
            out.append(f"{h}: cap {r.get('cap')} ({param(r, 'cap')})")
        if "per" in r and ("sum" not in r or not isinstance(param(r, "per"), int) or param(r, "per") <= 0):
            out.append(f"{h}: per {r['per']} ({param(r, 'per')}) goes with sum and is a positive number")
        if "sum" in r and r["stat"] not in STATS:
            out.append(f"{h}: stat {r['stat']} is not one of {sorted(STATS)}")
        if "charges" in r and (r["charges"] not in (0, 1, 2) or r["charges"] != r["skill"] or "on" in r):
            out.append(f"{h}: charges {r['charges']} (0, 1 or 2, the icon's own slot, not on foes)")
        for a in r.get("native", ()):
            if a not in addons or not any(addon_of(p) == a for p, _ in by_hero.get(h, [])):
                out.append(f"{h}: native {a} is not an add-on with a copy of him")
        mine = by_hero.get(h, [])
        if not mine:
            out.append(f"{h}: no data of him")
            continue
        if "passive" in r and not any(passive_ref(c) == r["passive"] for _, c in mine):
            out.append(f"{h}: no copy of it calls {r['passive']}")
        elif not any(live(r, p, c, added(c)) for p, c in mine):
            what = (f"{SLOTS[r['charges']]}.cooltime_use_count > 1" if "charges" in r else
                    r.get("prefix") or ", ".join(names(r)))
            out.append(f"{h}: no copy of him hangs {what} ({r['label']})")
    for h in sorted({r["hero"] for r in ALL}):
        if len({r["skill"] for r in rows(h)}) > 1:
            out.append(f"{h}: his rows show different icons")
        for path, champ in by_hero.get(h, []):
            here = [r for r in rows(h) if applies(r, champ)]
            have = added(champ)
            if here and not any(live(r, path, champ, have) for r in here):
                out.append(f"{os.path.relpath(path, ROOT)}: shows the box but none of his rows reads anything in it")
    if os.path.exists(os.path.join(LEAGUE, "effects", "league_stack_num#sheet.png")):
        out.append("league/effects/league_stack_num is still there (the over-head numbers are gone)")
    return out


def what(r):
    if "count" in r:
        w = r["count"]
    elif "sum" in r:
        w = f'{r["sum"]} {r["stat"]}' + (f' / {r["per"]}={param(r, "per")}' if "per" in r else "")
    elif "most" in r or "total" in r:
        d = r.get("most") or r["total"]
        w = ("most " if "most" in r else "total ") + " ".join(f"{n.replace(r['hero'] + '_', '')}={v}" for n, v in d.items())
    elif "prefix" in r:
        w = r["prefix"] + "*"
    elif "charges" in r:
        w = f"charges of {SLOTS[r['charges']]}"
    else:
        w = f'{r["ladder"]}1..{r["rungs"]}'
    return ("foes: " if r.get("on") == "foes" else "") + w


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for r in sorted(ALL, key=lambda r: r["hero"]):
            print(f'{r["hero"]:20s} {what(r):48s} cap {param(r, "cap"):5d}  icon {r["skill"]}  {r["label"]}')
    if a.write:
        for pack, (_, path, _, _) in TABLES.items():
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(table_rs(pack))
            print("wrote", os.path.relpath(path, ROOT))
        for line in data_problems(write=True):
            print(line)
    if a.check:
        bad = rules_problems() + table_problems() + data_problems()
        for b in bad:
            print(b)
        if bad:
            sys.exit(f"{len(bad)} problem(s)")
        said = ", ".join(f"{dll} {len({r['hero'] for r in t})} heroes ({len(t)} rows)" for t, _, _, dll in TABLES.values())
        print(f"stack counts: {said}; {FIELD} and both tables up to date")


if __name__ == "__main__":
    main()
