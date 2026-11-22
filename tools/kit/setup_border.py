"""边境巡团十二个英雄在包里共用文件中的键：五种语言的说明和技能名、九句配音的 .sound_info 和覆盖、champion_view。

    python tools/kit/setup_border.py [--hero cenlei ...] [--check-lengths]

数字都从各自 build_<hero>.py 的 P 读，改了数值重跑这个就行（说明框的长度上限在 border_pack.TOOLTIP_MAX）。配音的片段由
tools/kit/seed_border_audio.py 从 Codex 交的 zip 拷进 border/sound/sfx/（<id>_vo_<x>.mp3）。champion_view 的脸、身子中心、
选人卡中心照 tools/art/import_<hero>.py 出的 1 倍帧量的（VIEW）。
"""
import argparse
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import border_pack as B  # noqa: E402
from border_pack import ADi, APi, HPi, O, A, R, M, S, G, E  # noqa: E402

HEROES = ["cenlei", "xiaolun", "dengmi", "zhumo", "fusuo", "yanxi", "yindu", "lanti", "luxin", "jiyan", "zhongli",
          "wuling"]
VOICE = ["pick", "attack", "move", "hit", "skill", "skill2", "ult", "dead", "win"]

# champion_view（离脚底的游戏像素，往上是负）。2026-11-22 照 Codex v0.9.0 高清帧重出（PPU 2.5，七头身）的 1 倍待机第 1 帧量的：
#   face：眼睛那行 = 头顶往下头高（身高的 1/7）的 55%；x 是头顶那段的中点往前 2.5，夹在 1..4；
#   center：百科卡按头顶对齐：round(-身高 + 28.3)（联盟的「实心顶 - center」中位差 27.3，再低 1 格）。
#         tools/art/bp_card_audit.py 的规矩按 8 格宽的第一行算，七头身的头不到 8 格宽，会量到肩膀上（-7），不用；
#   banpick_center：选人卡画布 40 个游戏像素高，头到脚超过 40 的进 addons/border/src/hd.rs 的 UI_SIZES（39 / 身高，
#         和终末包一样），缩完最高一行还高过 -28 的照联盟的规矩 round(-39 - 最高一行)，其余用 -12。
VIEW = {
    "cenlei": {"face": (4, -38), "center": (0, -12), "banpick_center": (0, -12)},
    "xiaolun": {"face": (1, -40), "center": (0, -14), "banpick_center": (0, -12)},
    "dengmi": {"face": (1, -38), "center": (0, -13), "banpick_center": (0, -12)},
    "zhumo": {"face": (2, -40), "center": (0, -15), "banpick_center": (0, -11)},
    "fusuo": {"face": (2, -38), "center": (0, -13), "banpick_center": (0, -12)},
    "yanxi": {"face": (1, -40), "center": (0, -14), "banpick_center": (0, -12)},
    "yindu": {"face": (2, -38), "center": (0, -12), "banpick_center": (0, -12)},
    "lanti": {"face": (2, -38), "center": (0, -13), "banpick_center": (0, -12)},
    "luxin": {"face": (1, -40), "center": (0, -14), "banpick_center": (0, -12)},
    "jiyan": {"face": (4, -40), "center": (0, -14), "banpick_center": (0, -11)},
    "zhongli": {"face": (3, -40), "center": (0, -14), "banpick_center": (0, -12)},
    "wuling": {"face": (1, -40), "center": (0, -14), "banpick_center": (0, -11)},
}


def s(t):
    """拍 -> 秒（去掉多余的零）。"""
    return B.secs(t)


def texts(hero, p):
    """{语言: (description, skill_name)}。"""
    if hero == "cenlei":
        lv = p["p_res"] // 10
        return {
            "zh-hans": ({
                "name": "岑垒",
                "attack": f"盾击，造成{ADi}{O}100%{E} + {HPi}{O}{p['a_hp']}%{E}{O}物理伤害{E}。{O}背压{E}：接肩替队友挨的伤害攒成背压"
                          f"（最多最大生命的{A}{p['p_cap']}%{E}），每攒十分之一护甲和魔抗{A}+{lv}{E}，卸城时全部放出。",
                "skill": f"朝前方扇形扫击，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + {HPi}{O}{p['q_hp']}%{E}{O}物理伤害{E}"
                         f"并{R}减速{p['q_slow']}%{E}，扇形里的人{R}眩晕{s(p['q_stun_all'])}秒{E}；优先扫向正在施法的敌方英雄，"
                         f"{R}打断{E}施法（{R}眩晕{s(p['q_stun'])}秒{E}）。",
                "skill2": f"给身边最受威胁的队友贴上盾板（{A}{s(p['e_time'])}秒{E}）：他接下来{A}{p['e_hits']}{E}次受到的伤害降低"
                          f"{A}{p['e_share']}%{E}，少挨的部分由岑垒承受（不会因此倒下）并攒成背压。没人受威胁时自己减伤{A}{p['e_self']}%{E}。",
                "ult": f"起手不受控制、减伤{A}{p['r_dr']}%{E}，随后放出背压：前方扇形的敌人受到{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}"
                       f" + 背压{A}{p['r_p']}%{E}的{O}物理伤害{E}，被{R}推开{E}并{R}减速{p['r_slow']}%{E}；放出背压的{A}{p['r_sh']}%{E}化为{S}护盾{E}。",
            }, {"skill1": "横楔", "skill2": "接肩", "ult": "卸城"}),
            "zh-hant": ({
                "name": "岑壘",
                "attack": f"盾擊，造成{ADi}{O}100%{E} + {HPi}{O}{p['a_hp']}%{E}{O}物理傷害{E}。{O}背壓{E}：接肩替隊友挨的傷害攢成背壓"
                          f"（最多最大生命的{A}{p['p_cap']}%{E}），每攢十分之一護甲和魔抗{A}+{lv}{E}，卸城時全部放出。",
                "skill": f"朝前方扇形掃擊，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + {HPi}{O}{p['q_hp']}%{E}{O}物理傷害{E}"
                         f"並{R}緩速{p['q_slow']}%{E}，扇形裡的人{R}暈眩{s(p['q_stun_all'])}秒{E}；優先掃向正在施法的敵方英雄，"
                         f"{R}打斷{E}施法（{R}暈眩{s(p['q_stun'])}秒{E}）。",
                "skill2": f"給身邊最受威脅的隊友貼上盾板（{A}{s(p['e_time'])}秒{E}）：他接下來{A}{p['e_hits']}{E}次受到的傷害降低"
                          f"{A}{p['e_share']}%{E}，少挨的部分由岑壘承受（不會因此倒下）並攢成背壓。沒人受威脅時自己減傷{A}{p['e_self']}%{E}。",
                "ult": f"起手不受控制、減傷{A}{p['r_dr']}%{E}，隨後放出背壓：前方扇形的敵人受到{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}"
                       f" + 背壓{A}{p['r_p']}%{E}的{O}物理傷害{E}，被{R}推開{E}並{R}緩速{p['r_slow']}%{E}；放出背壓的{A}{p['r_sh']}%{E}化為{S}護盾{E}。",
            }, {"skill1": "橫楔", "skill2": "接肩", "ult": "卸城"}),
            "en": ({
                "name": "Cen Lei",
                "attack": f"Shield bash: {ADi}{O}100%{E} + {HPi}{O}{p['a_hp']}%{E} {O}physical damage{E}. {O}Back Pressure{E}: what he "
                          f"takes for an ally through Shoulder the Load is stored (up to {A}{p['p_cap']}%{E} of his max health); every "
                          f"tenth gives {A}+{lv}{E} armor and magic resist. Unload the Walls lets it all out.",
                "skill": f"Sweeps a cone ahead: {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + {HPi}{O}{p['q_hp']}%{E} {O}physical damage{E} "
                         f"and {R}{p['q_slow']}% slow{E}, {R}stunning{E} everyone in it {R}{s(p['q_stun_all'])}s{E}. Turns toward "
                         f"an enemy champion who is casting and {R}interrupts{E} it ({R}stun {s(p['q_stun'])}s{E}).",
                "skill2": f"Plates the most threatened nearby ally ({A}{s(p['e_time'])}s{E}): the next {A}{p['e_hits']}{E} hits deal "
                          f"{A}{p['e_share']}%{E} less, and Cen Lei takes that part himself (it cannot down him), storing it as Back "
                          f"Pressure. With nobody threatened he braces: {A}{p['e_self']}%{E} less damage.",
                "ult": f"Unstoppable and {A}{p['r_dr']}%{E} damage reduction while winding up, then releases Back Pressure: enemies "
                       f"in a cone take {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} + {A}{p['r_p']}%{E} of the pressure as "
                       f"{O}physical damage{E}, are {R}pushed away{E} and {R}slowed {p['r_slow']}%{E}; {A}{p['r_sh']}%{E} of "
                       f"the pressure becomes a {S}shield{E}.",
            }, {"skill1": "Cross Wedge", "skill2": "Shoulder the Load", "ult": "Unload the Walls"}),
            "ja": ({
                "name": "岑塁",
                "attack": f"盾打ち：{ADi}{O}100%{E} + {HPi}{O}{p['a_hp']}%{E}の{O}物理ダメージ{E}。{O}背圧{E}：肩代わりで受けたダメージを"
                          f"背圧として溜める（最大HPの{A}{p['p_cap']}%{E}まで）。1割ごとに物防・魔防{A}+{lv}{E}。城崩しで全て放つ。",
                "skill": f"前方扇形を薙ぎ払い{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + {HPi}{O}{p['q_hp']}%{E}の{O}物理ダメージ{E}と"
                         f"{R}{p['q_slow']}%鈍足{E}、範囲内の敵を{R}スタン{s(p['q_stun_all'])}秒{E}。詠唱中の敵チャンピオンを優先して狙い、"
                         f"{R}詠唱を中断{E}させる（{R}スタン{s(p['q_stun'])}秒{E}）。",
                "skill2": f"最も危険な味方に盾板を貼る（{A}{s(p['e_time'])}秒{E}）：次の{A}{p['e_hits']}{E}回の被ダメージを{A}{p['e_share']}%{E}"
                          f"軽減し、その分を岑塁が受けて背圧にする（これでは倒れない）。誰もいなければ自身が{A}{p['e_self']}%{E}軽減。",
                "ult": f"構え中はCC無効・被ダメージ{A}{p['r_dr']}%{E}軽減。背圧を解放し前方扇形に{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}"
                       f" + 背圧の{A}{p['r_p']}%{E}の{O}物理ダメージ{E}、{R}ノックバック{E}と{R}{p['r_slow']}%鈍足{E}。背圧の{A}{p['r_sh']}%{E}が{S}シールド{E}に。",
            }, {"skill1": "横楔", "skill2": "肩代わり", "ult": "城崩し"}),
            "ko": ({
                "name": "천레이",
                "attack": f"방패 가격: {ADi}{O}100%{E} + {HPi}{O}{p['a_hp']}%{E} {O}물리 피해{E}. {O}배압{E}: 어깨받이로 대신 받은 피해를 배압으로 "
                          f"모은다(최대 체력의 {A}{p['p_cap']}%{E}까지). 10%마다 방어력·마법 저항력 {A}+{lv}{E}. 성벽풀이로 모두 방출.",
                "skill": f"전방 부채꼴을 휩쓸어 {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + {HPi}{O}{p['q_hp']}%{E} {O}물리 피해{E}와 "
                         f"{R}{p['q_slow']}% 둔화{E}, 범위 안의 적은 {R}기절 {s(p['q_stun_all'])}초{E}. 시전 중인 적 챔피언을 우선 노려 "
                         f"{R}시전을 끊는다{E}({R}기절 {s(p['q_stun'])}초{E}).",
                "skill2": f"가장 위협받는 아군에게 방패판을 붙인다({A}{s(p['e_time'])}초{E}): 다음 {A}{p['e_hits']}{E}번 받는 피해가 "
                          f"{A}{p['e_share']}%{E} 줄고, 줄어든 만큼 천레이가 대신 받아 배압으로 모은다(이것으로 쓰러지지 않음). "
                          f"위협받는 아군이 없으면 자신이 피해 {A}{p['e_self']}%{E} 감소.",
                "ult": f"준비 중 군중 제어 면역, 받는 피해 {A}{p['r_dr']}%{E} 감소. 배압을 방출해 전방 부채꼴에 {O}{p['r_dmg']}{E} + "
                       f"{ADi}{O}{p['r_ad']}%{E} + 배압의 {A}{p['r_p']}%{E} {O}물리 피해{E}, {R}밀쳐내기{E}와 {R}{p['r_slow']}% 둔화{E}. "
                       f"방출한 배압의 {A}{p['r_sh']}%{E}가 {S}보호막{E}이 된다.",
            }, {"skill1": "가로쐐기", "skill2": "어깨받이", "ult": "성벽풀이"}),
        }
    if hero == "xiaolun":
        full_as = p["e_as"] + 10 * p["e_as_k"]
        return {
            "zh-hans": ({
                "name": "绡轮",
                "attack": f"弩箭造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}走弦{E}：按实际走过的路上弦，走满十层后弦绷紧，下一箭额外造成"
                          f"{O}{p['p_dmg']}{E} + {ADi}{O}{p['p_ad']}%{E}{O}物理伤害{E}并{R}减速{p['p_slow']}%{E}。",
                "skill": f"朝目标侧面短移（只走得通的路，撞墙即停），随后射出一箭，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}"
                         f"{O}物理伤害{E}。侧移的路也会上弦。",
                "skill2": f"放掉全部张力：{A}{s(p['e_t'])}秒{E}内攻速{A}+{p['e_as']}%{E}，每层张力再{A}+{p['e_as_k']}%{E}（满弦{A}+{full_as}%{E}）。",
                "ult": f"分三次射出星弧箭，每支在射出时重新选择目标（原目标优先，其次生命比例最低的敌方英雄），各造成{O}{p['r_dmg']}{E}"
                       f" + {ADi}{O}{p['r_ad']}%{E}{O}物理伤害{E}。被控制时停射。",
            }, {"skill1": "切角", "skill2": "放扣", "ult": "满弧"}),
            "zh-hant": ({
                "name": "綃輪",
                "attack": f"弩箭造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}走弦{E}：按實際走過的路上弦，走滿十層後弦繃緊，下一箭額外造成"
                          f"{O}{p['p_dmg']}{E} + {ADi}{O}{p['p_ad']}%{E}{O}物理傷害{E}並{R}緩速{p['p_slow']}%{E}。",
                "skill": f"朝目標側面短移（只走得通的路，撞牆即停），隨後射出一箭，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}"
                         f"{O}物理傷害{E}。側移的路也會上弦。",
                "skill2": f"放掉全部張力：{A}{s(p['e_t'])}秒{E}內攻速{A}+{p['e_as']}%{E}，每層張力再{A}+{p['e_as_k']}%{E}（滿弦{A}+{full_as}%{E}）。",
                "ult": f"分三次射出星弧箭，每支在射出時重新選擇目標（原目標優先，其次生命比例最低的敵方英雄），各造成{O}{p['r_dmg']}{E}"
                       f" + {ADi}{O}{p['r_ad']}%{E}{O}物理傷害{E}。被控制時停射。",
            }, {"skill1": "切角", "skill2": "放扣", "ult": "滿弧"}),
            "en": ({
                "name": "Xiao Lun",
                "attack": f"Crossbow bolt: {ADi}{O}100%{E} {O}physical damage{E}. {O}Walking String{E}: the distance she actually "
                          f"moves winds her string; at ten notches it is taut and her next bolt deals {O}{p['p_dmg']}{E} + "
                          f"{ADi}{O}{p['p_ad']}%{E} extra {O}physical damage{E} and {R}slows {p['p_slow']}%{E}.",
                "skill": f"Slides sideways from the target (only where she can walk; walls stop her), then shoots: "
                         f"{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} {O}physical damage{E}. The slide winds the string too.",
                "skill2": f"Releases all tension: {A}+{p['e_as']}%{E} attack speed for {A}{s(p['e_t'])}s{E}, {A}+{p['e_as_k']}%{E} more "
                          f"per notch ({A}+{full_as}%{E} when taut).",
                "ult": f"Looses three comet arrows, choosing a new target for each as it flies (her target first, else the "
                       f"weakest enemy champion): {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} {O}physical damage{E} each. "
                       f"Crowd control stops the volley.",
            }, {"skill1": "Cut the Corner", "skill2": "Loose the Latch", "ult": "Full Arc"}),
            "ja": ({
                "name": "綃輪",
                "attack": f"弩の矢：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}走弦{E}：実際に動いた距離で弦を巻き、10段で張り詰める。"
                          f"次の矢が{O}{p['p_dmg']}{E} + {ADi}{O}{p['p_ad']}%{E}の追加{O}物理ダメージ{E}と{R}{p['p_slow']}%鈍足{E}。",
                "skill": f"対象の横へ滑る（歩ける所だけ、壁で止まる）。その後に射撃し{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}の"
                         f"{O}物理ダメージ{E}。横移動でも弦が巻かれる。",
                "skill2": f"張力をすべて放つ：{A}{s(p['e_t'])}秒{E}間攻撃速度{A}+{p['e_as']}%{E}、1段ごとに{A}+{p['e_as_k']}%{E}"
                          f"（最大{A}+{full_as}%{E}）。",
                "ult": f"星弧の矢を3回放つ。1本ごとに放つ瞬間に対象を選び直す（元の対象優先、次にHP割合が最も低い敵）。各"
                       f"{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}の{O}物理ダメージ{E}。CC中は撃たない。",
            }, {"skill1": "角切り", "skill2": "留め金外し", "ult": "満弧"}),
            "ko": ({
                "name": "샤오룬",
                "attack": f"석궁 화살: {ADi}{O}100%{E} {O}물리 피해{E}. {O}걷는 시위{E}: 실제로 움직인 거리만큼 시위를 감아 10단계가 되면 "
                          f"팽팽해지고, 다음 화살이 {O}{p['p_dmg']}{E} + {ADi}{O}{p['p_ad']}%{E} 추가 {O}물리 피해{E}와 {R}{p['p_slow']}% 둔화{E}.",
                "skill": f"대상의 옆으로 짧게 이동한 뒤(걸을 수 있는 곳만, 벽에 막힘) 화살을 쏴 {O}{p['q_dmg']}{E} + "
                         f"{ADi}{O}{p['q_ad']}%{E} {O}물리 피해{E}. 옆걸음도 시위를 감는다.",
                "skill2": f"긴장을 모두 풀어 {A}{s(p['e_t'])}초{E} 동안 공격 속도 {A}+{p['e_as']}%{E}, 단계마다 {A}+{p['e_as_k']}%{E}"
                          f"(최대 {A}+{full_as}%{E}).",
                "ult": f"별호 화살을 세 번 쏜다. 화살마다 쏘는 순간 대상을 다시 고른다(원래 대상 우선, 다음은 체력 비율이 가장 "
                       f"낮은 적 챔피언). 각각 {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} {O}물리 피해{E}. 군중 제어 중에는 쏘지 않는다.",
            }, {"skill1": "모서리 베기", "skill2": "걸쇠 풀기", "ult": "만궁"}),
        }
    if hero == "dengmi":
        return {
            "zh-hans": ({
                "name": "灯弥",
                "attack": f"灯火造成{ADi}{O}100%{E}{O}物理伤害{E}和{APi}{M}{p['a_ap']}%{E}{M}魔法伤害{E}。{O}存光{E}：身边的友军（含自己）受到技能伤害时攒灯火，每损失{A}1%{E}"
                          f"生命攒{A}1{E}点，最多{A}100{E}点，强化收灯。",
                "skill": f"把灯递给身边最承压的友军，给予{S}{p['q_sh']}{E} + {APi}{M}{p['q_ap']}%{E} + 对方{HPi}{S}{p['q_hp']}%{E}的"
                         f"{S}护盾{E}，持续{A}{s(p['q_t'])}秒{E}；灯一亮，他身边的敌人被晃眼{R}减速{p['q_flare_slow']}%{E}"
                         f"{A}{s(p['q_flare_t'])}秒{E}。",
                "skill2": f"为生命比例最低的友军引路：移速{G}+{p['e_ms']}%{E}，持续{A}{s(p['e_t'])}秒{E}；对方生命低于{A}{p['e_low']}%{E}时再"
                          f"{G}+{p['e_ms_low']}%{E}。灯弥自己移速{G}+{p['e_self']}%{E}。",
                "ult": f"收回灯火化作两道脉冲：第一道{G}治疗{E}选中的友军{G}{p['r_heal']}{E} + {APi}{M}{p['r_ap']}%{E}，第二道{G}治疗{E}"
                       f"他身边生命比例最低的友军同样多；每点灯火使治疗{A}+{p['r_light'] // 100}%{E}（满灯火翻倍）。每道脉冲在受治疗"
                       f"的人身边炸开光：周围敌人受到{M}{p['r_burst']}{E} + {APi}{M}{p['r_burst_ap']}%{E}{M}魔法伤害{E}并"
                       f"{R}减速{p['r_burst_slow']}%{E}。",
            }, {"skill1": "递灯", "skill2": "引路", "ult": "收灯"}),
            "zh-hant": ({
                "name": "燈彌",
                "attack": f"燈火造成{ADi}{O}100%{E}{O}物理傷害{E}和{APi}{M}{p['a_ap']}%{E}{M}魔法傷害{E}。{O}存光{E}：身邊的友軍（含自己）受到技能傷害時攢燈火，每損失{A}1%{E}"
                          f"生命攢{A}1{E}點，最多{A}100{E}點，強化收燈。",
                "skill": f"把燈遞給身邊最承壓的友軍，給予{S}{p['q_sh']}{E} + {APi}{M}{p['q_ap']}%{E} + 對方{HPi}{S}{p['q_hp']}%{E}的"
                         f"{S}護盾{E}，持續{A}{s(p['q_t'])}秒{E}；燈一亮，他身邊的敵人被晃眼{R}減速{p['q_flare_slow']}%{E}"
                         f"{A}{s(p['q_flare_t'])}秒{E}。",
                "skill2": f"為生命比例最低的友軍引路：移速{G}+{p['e_ms']}%{E}，持續{A}{s(p['e_t'])}秒{E}；對方生命低於{A}{p['e_low']}%{E}時再"
                          f"{G}+{p['e_ms_low']}%{E}。燈彌自己移速{G}+{p['e_self']}%{E}。",
                "ult": f"收回燈火化作兩道脈衝：第一道{G}治療{E}選中的友軍{G}{p['r_heal']}{E} + {APi}{M}{p['r_ap']}%{E}，第二道{G}治療{E}"
                       f"他身邊生命比例最低的友軍同樣多；每點燈火使治療{A}+{p['r_light'] // 100}%{E}（滿燈火翻倍）。每道脈衝在受治療"
                       f"的人身邊炸開光：周圍敵人受到{M}{p['r_burst']}{E} + {APi}{M}{p['r_burst_ap']}%{E}{M}魔法傷害{E}並"
                       f"{R}減速{p['r_burst_slow']}%{E}。",
            }, {"skill1": "遞燈", "skill2": "引路", "ult": "收燈"}),
            "en": ({
                "name": "Deng Mi",
                "attack": f"Lantern mote: {ADi}{O}100%{E} {O}physical damage{E} and {APi}{M}{p['a_ap']}%{E} {M}magic damage{E}. "
                          f"{O}Stored Light{E}: when nearby allies (herself "
                          f"included) take spell damage she gathers light, {A}1{E} per {A}1%{E} health lost, up to {A}100{E}; it "
                          f"strengthens Gather the Lamps.",
                "skill": f"Hands a lamp to the ally under the most pressure: a {S}shield{E} of {S}{p['q_sh']}{E} + {APi}{M}{p['q_ap']}%{E}"
                         f" + {HPi}{S}{p['q_hp']}%{E} of their max health for {A}{s(p['q_t'])}s{E}; the flash "
                         f"{R}slows{E} enemies around them by {R}{p['q_flare_slow']}%{E} for {A}{s(p['q_flare_t'])}s{E}.",
                "skill2": f"Lights the way for the ally lowest on health: {G}+{p['e_ms']}%{E} move speed for {A}{s(p['e_t'])}s{E}, "
                          f"{G}+{p['e_ms_low']}%{E} more below {A}{p['e_low']}%{E} health. Deng Mi gains {G}+{p['e_self']}%{E}.",
                "ult": f"Gathers her lamps into two pulses: the first {G}heals{E} the chosen ally {G}{p['r_heal']}{E} + "
                       f"{APi}{M}{p['r_ap']}%{E}, the second heals the ally lowest on health near them as much. Each point of "
                       f"light adds {A}{p['r_light'] // 100}%{E} (full light doubles it). Each pulse bursts around the healed ally: "
                       f"{M}{p['r_burst']}{E} + {APi}{M}{p['r_burst_ap']}%{E} {M}magic damage{E} and a "
                       f"{R}{p['r_burst_slow']}% slow{E}.",
            }, {"skill1": "Pass the Lamp", "skill2": "Light the Way", "ult": "Gather the Lamps"}),
            "ja": ({
                "name": "灯弥",
                "attack": f"灯火：{ADi}{O}100%{E}の{O}物理ダメージ{E}と{APi}{M}{p['a_ap']}%{E}の{M}魔法ダメージ{E}。{O}灯溜め{E}：周囲の味方（自身含む）がスキルダメージを受けると、"
                          f"HP{A}1%{E}ごとに灯火を{A}1{E}溜める（最大{A}100{E}）。灯収めを強化する。",
                "skill": f"最も追い詰められた味方に灯を渡し、{S}{p['q_sh']}{E} + {APi}{M}{p['q_ap']}%{E} + 相手の{HPi}{S}{p['q_hp']}%{E}の"
                         f"{S}シールド{E}（{A}{s(p['q_t'])}秒{E}）。灯の光で周囲の敵を{R}{p['q_flare_slow']}%鈍足{E}"
                         f"（{A}{s(p['q_flare_t'])}秒{E}）。",
                "skill2": f"HP割合が最も低い味方を導く：移動速度{G}+{p['e_ms']}%{E}（{A}{s(p['e_t'])}秒{E}）、HP{A}{p['e_low']}%{E}未満なら"
                          f"さらに{G}+{p['e_ms_low']}%{E}。灯弥自身も{G}+{p['e_self']}%{E}。",
                "ult": f"灯を二つの脈動に変える：一つ目は選んだ味方を{G}{p['r_heal']}{E} + {APi}{M}{p['r_ap']}%{E}{G}回復{E}、二つ目は"
                       f"その近くでHP割合が最も低い味方を同量回復。灯火1点ごとに回復{A}+{p['r_light'] // 100}%{E}（満タンで2倍）。"
                       f"脈動は回復した味方の周りで弾け、敵に{M}{p['r_burst']}{E} + {APi}{M}{p['r_burst_ap']}%{E}の{M}魔法ダメージ{E}と"
                       f"{R}{p['r_burst_slow']}%鈍足{E}。",
            }, {"skill1": "灯渡し", "skill2": "道標", "ult": "灯収め"}),
            "ko": ({
                "name": "덩미",
                "attack": f"등불: {ADi}{O}100%{E} {O}물리 피해{E}와 {APi}{M}{p['a_ap']}%{E} {M}마법 피해{E}. {O}빛 모으기{E}: 주변 아군(자신 포함)이 스킬 피해를 받으면 잃은 체력 "
                          f"{A}1%{E}마다 등불 {A}1{E}을 모은다(최대 {A}100{E}). 등불 거두기를 강화한다.",
                "skill": f"가장 압박받는 아군에게 등불을 건네 {S}{p['q_sh']}{E} + {APi}{M}{p['q_ap']}%{E} + 대상 {HPi}{S}{p['q_hp']}%{E}의 "
                         f"{S}보호막{E}({A}{s(p['q_t'])}초{E}). 불빛에 주변 적이 {R}{p['q_flare_slow']}% 둔화{E}"
                         f"({A}{s(p['q_flare_t'])}초{E}).",
                "skill2": f"체력 비율이 가장 낮은 아군의 길을 밝혀 이동 속도 {G}+{p['e_ms']}%{E}({A}{s(p['e_t'])}초{E}), 체력 "
                          f"{A}{p['e_low']}%{E} 미만이면 {G}+{p['e_ms_low']}%{E} 더. 덩미 자신도 {G}+{p['e_self']}%{E}.",
                "ult": f"등불을 두 번의 파동으로 거둔다: 첫 파동은 선택한 아군을 {G}{p['r_heal']}{E} + {APi}{M}{p['r_ap']}%{E} {G}회복{E}, "
                       f"두 번째는 그 근처에서 체력 비율이 가장 낮은 아군을 같은 양 회복. 등불 1점마다 회복 "
                       f"{A}+{p['r_light'] // 100}%{E}(가득 차면 두 배). 파동은 회복한 아군 주변에서 터져 적에게 "
                       f"{M}{p['r_burst']}{E} + {APi}{M}{p['r_burst_ap']}%{E} {M}마법 피해{E}와 {R}{p['r_burst_slow']}% 둔화{E}.",
            }, {"skill1": "등불 건네기", "skill2": "길잡이", "ult": "등불 거두기"}),
        }
    if hero == "zhumo":
        full = p["e_dr"] + 10 * p["e_k"]
        return {
            "zh-hans": ({
                "name": "铸沫",
                "attack": f"锤击造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}余温{E}：每次普攻命中积攒热量（最多{A}10{E}层），每层攻速"
                          f"{A}+{p['p_as']}%{E}；{A}{s(p['p_idle'])}秒{E}没打中东西后逐渐散热。",
                "skill": f"落锤重击，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}{O}物理伤害{E}，每层热量再加{ADi}{O}{p['q_heat']}%{E}，"
                         f"并{R}减速{p['q_slow']}%{E}；热量{A}{p['q_stun_heat']}{E}层以上时{R}眩晕{s(p['q_stun'])}秒{E}。周围敌人受到"
                         f"{A}{p['q_splash_pct']}%{E}伤害。",
                "skill2": f"用掉全部热量回火：{A}{s(p['e_t'])}秒{E}内受到的伤害降低{A}{p['e_dr']}%{E}，每层热量再降低{A}{p['e_k']}%{E}"
                          f"（满热{A}{full}%{E}）。",
                "ult": f"开炉：脚下的敌人受到{O}{p['r_burst']}{E} + {ADi}{O}{p['r_burst_ad']}%{E}{O}物理伤害{E}；{A}{s(p['r_t'])}秒{E}内攻速"
                       f"{A}+{p['r_as']}%{E}，每秒热量{A}+{p['r_gain']}{E}层；危险时加快回火冷却，热量够且有敌人在旁时加快压坯冷却。",
            }, {"skill1": "压坯", "skill2": "回火", "ult": "开炉"}),
            "zh-hant": ({
                "name": "鑄沫",
                "attack": f"錘擊造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}餘溫{E}：每次普攻命中積攢熱量（最多{A}10{E}層），每層攻速"
                          f"{A}+{p['p_as']}%{E}；{A}{s(p['p_idle'])}秒{E}沒打中東西後逐漸散熱。",
                "skill": f"落錘重擊，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}{O}物理傷害{E}，每層熱量再加{ADi}{O}{p['q_heat']}%{E}，"
                         f"並{R}緩速{p['q_slow']}%{E}；熱量{A}{p['q_stun_heat']}{E}層以上時{R}暈眩{s(p['q_stun'])}秒{E}。周圍敵人受到"
                         f"{A}{p['q_splash_pct']}%{E}傷害。",
                "skill2": f"用掉全部熱量回火：{A}{s(p['e_t'])}秒{E}內受到的傷害降低{A}{p['e_dr']}%{E}，每層熱量再降低{A}{p['e_k']}%{E}"
                          f"（滿熱{A}{full}%{E}）。",
                "ult": f"開爐：腳下的敵人受到{O}{p['r_burst']}{E} + {ADi}{O}{p['r_burst_ad']}%{E}{O}物理傷害{E}；{A}{s(p['r_t'])}秒{E}內攻速"
                       f"{A}+{p['r_as']}%{E}，每秒熱量{A}+{p['r_gain']}{E}層；危險時加快回火冷卻，熱量夠且有敵人在旁時加快壓坯冷卻。",
            }, {"skill1": "壓坯", "skill2": "回火", "ult": "開爐"}),
            "en": ({
                "name": "Zhu Mo",
                "attack": f"Hammer blow: {ADi}{O}100%{E} {O}physical damage{E}. {O}Afterheat{E}: every basic attack that lands builds "
                          f"heat (up to {A}10{E} levels), {A}+{p['p_as']}%{E} attack speed each; after {A}{s(p['p_idle'])}s{E} "
                          f"without a hit the heat fades.",
                "skill": f"Brings the hammer down: {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} {O}physical damage{E}, "
                         f"{ADi}{O}+{p['q_heat']}%{E} per heat level, {R}{p['q_slow']}% slow{E}; at {A}{p['q_stun_heat']}{E}+ heat it also "
                         f"{R}stuns {s(p['q_stun'])}s{E}. Nearby enemies take {A}{p['q_splash_pct']}%{E}.",
                "skill2": f"Spends all heat to temper: {A}{p['e_dr']}%{E} less damage taken for {A}{s(p['e_t'])}s{E}, "
                          f"{A}{p['e_k']}%{E} more per heat level ({A}{full}%{E} at full heat).",
                "ult": f"Opens the furnace: enemies round his feet take {O}{p['r_burst']}{E} + {ADi}{O}{p['r_burst_ad']}%{E} "
                       f"{O}physical damage{E}; for {A}{s(p['r_t'])}s{E} {A}+{p['r_as']}%{E} attack speed and {A}+{p['r_gain']}{E} heat "
                       f"each second; in danger Temper comes back sooner, and when hot with an enemy close Press the Blank does.",
            }, {"skill1": "Press the Blank", "skill2": "Temper", "ult": "Open the Furnace"}),
            "ja": ({
                "name": "鋳沫",
                "attack": f"槌打ち：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}余熱{E}：通常攻撃が当たるたびに熱を溜める（最大{A}10{E}段）。"
                          f"1段ごとに攻撃速度{A}+{p['p_as']}%{E}。{A}{s(p['p_idle'])}秒{E}当てないと冷めていく。",
                "skill": f"槌を振り下ろし{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}の{O}物理ダメージ{E}、熱1段ごとに{ADi}{O}+{p['q_heat']}%{E}、"
                         f"{R}{p['q_slow']}%鈍足{E}。熱{A}{p['q_stun_heat']}{E}段以上で{R}スタン{s(p['q_stun'])}秒{E}。周囲の敵は{A}{p['q_splash_pct']}%{E}。",
                "skill2": f"熱をすべて使い焼き戻す：{A}{s(p['e_t'])}秒{E}間被ダメージ{A}{p['e_dr']}%{E}軽減、熱1段ごとにさらに"
                          f"{A}{p['e_k']}%{E}（最大{A}{full}%{E}）。",
                "ult": f"炉を開き足元の敵に{O}{p['r_burst']}{E} + {ADi}{O}{p['r_burst_ad']}%{E}の{O}物理ダメージ{E}。{A}{s(p['r_t'])}秒{E}間"
                       f"攻撃速度{A}+{p['r_as']}%{E}、毎秒熱{A}+{p['r_gain']}{E}段。危険なら焼き戻し、熱が十分で敵が近ければ鍛圧のCTを短縮。",
            }, {"skill1": "鍛圧", "skill2": "焼き戻し", "ult": "炉開き"}),
            "ko": ({
                "name": "주모",
                "attack": f"망치질: {ADi}{O}100%{E} {O}물리 피해{E}. {O}여열{E}: 기본 공격이 맞을 때마다 열을 모은다(최대 {A}10{E}단계). "
                          f"단계마다 공격 속도 {A}+{p['p_as']}%{E}. {A}{s(p['p_idle'])}초{E} 동안 맞히지 못하면 식는다.",
                "skill": f"망치를 내리쳐 {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} {O}물리 피해{E}, 열 단계마다 {ADi}{O}+{p['q_heat']}%{E}, "
                         f"{R}{p['q_slow']}% 둔화{E}. 열 {A}{p['q_stun_heat']}{E}단계 이상이면 {R}기절 {s(p['q_stun'])}초{E}. 주변 적은 "
                         f"{A}{p['q_splash_pct']}%{E} 피해.",
                "skill2": f"열을 모두 써서 담금질: {A}{s(p['e_t'])}초{E} 동안 받는 피해 {A}{p['e_dr']}%{E} 감소, 열 단계마다 "
                          f"{A}{p['e_k']}%{E} 더(최대 {A}{full}%{E}).",
                "ult": f"화로를 열어 발밑의 적에게 {O}{p['r_burst']}{E} + {ADi}{O}{p['r_burst_ad']}%{E} {O}물리 피해{E}. {A}{s(p['r_t'])}초{E} "
                       f"동안 공격 속도 {A}+{p['r_as']}%{E}, 매초 열 {A}+{p['r_gain']}{E}단계. 위험하면 담금질, 열이 충분하고 적이 "
                       f"가까우면 단조의 재사용 대기시간이 줄어든다.",
            }, {"skill1": "단조", "skill2": "담금질", "ult": "화로 열기"}),
        }
    if hero == "fusuo":
        return {
            "zh-hans": ({
                "name": "伏梭",
                "attack": f"一刀造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}数步{E}：离开队友、越走越远的敌方英雄会被盯上（{A}{s(p['p_keep'])}秒{E}），"
                          f"伏梭对其伤害{A}+{p['p_dmg']}%{E}。",
                "skill": f"冲向目标（附近有被盯上的敌方英雄时改冲向他），随后斩击，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}"
                         f"{O}物理伤害{E}，对被盯上的目标再{A}+{p['q_track']}%{E}。",
                "skill2": f"在原地留下回撤点，移速{G}+{p['e_ms']}%{E}；{A}{s(p['e_win'])}秒{E}内陷入危险时自动闪回回撤点，短暂减伤"
                          f"{A}{p['e_dr']}%{E}。",
                "ult": f"在自己和目标之间拉出一道延伸到目标身后的预告斩线，随即穿过目标；片刻后斩线结算：仍在线上的敌人受到"
                       f"{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}{O}物理伤害{E}。及时离开斩线就能躲开。",
            }, {"skill1": "掠阶", "skill2": "留扣", "ult": "错拍"}),
            "zh-hant": ({
                "name": "伏梭",
                "attack": f"一刀造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}數步{E}：離開隊友、越走越遠的敵方英雄會被盯上（{A}{s(p['p_keep'])}秒{E}），"
                          f"伏梭對其傷害{A}+{p['p_dmg']}%{E}。",
                "skill": f"衝向目標（附近有被盯上的敵方英雄時改衝向他），隨後斬擊，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}"
                         f"{O}物理傷害{E}，對被盯上的目標再{A}+{p['q_track']}%{E}。",
                "skill2": f"在原地留下回撤點，移速{G}+{p['e_ms']}%{E}；{A}{s(p['e_win'])}秒{E}內陷入危險時自動閃回回撤點，短暫減傷"
                          f"{A}{p['e_dr']}%{E}。",
                "ult": f"在自己和目標之間拉出一道延伸到目標身後的預告斬線，隨即穿過目標；片刻後斬線結算：仍在線上的敵人受到"
                       f"{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}{O}物理傷害{E}。及時離開斬線就能躲開。",
            }, {"skill1": "掠階", "skill2": "留扣", "ult": "錯拍"}),
            "en": ({
                "name": "Fu Suo",
                "attack": f"Blade: {ADi}{O}100%{E} {O}physical damage{E}. {O}Counting Steps{E}: an enemy champion who keeps walking "
                          f"away from their allies is tracked ({A}{s(p['p_keep'])}s{E}); Fu Suo deals {A}+{p['p_dmg']}%{E} to them.",
                "skill": f"Dashes at the target (or at a tracked enemy champion close by instead) and cuts: {O}{p['q_dmg']}{E} + "
                         f"{ADi}{O}{p['q_ad']}%{E} {O}physical damage{E}, {A}+{p['q_track']}%{E} against a tracked target.",
                "skill2": f"Leaves a recall clasp where he stands and gains {G}+{p['e_ms']}%{E} move speed; if he gets in danger within "
                          f"{A}{s(p['e_win'])}s{E} he snaps back to it with {A}{p['e_dr']}%{E} damage reduction for a moment.",
                "ult": f"Marks a slash line from himself through the target and beyond, then dashes through; a beat later the "
                       f"line strikes: enemies still on it take {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} "
                       f"{O}physical damage{E}. Step off the line in time to dodge it.",
            }, {"skill1": "Skim the Steps", "skill2": "Leave a Clasp", "ult": "Off-Beat"}),
            "ja": ({
                "name": "伏梭",
                "attack": f"一太刀：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}歩数読み{E}：味方から離れ続ける敵チャンピオンを追跡する"
                          f"（{A}{s(p['p_keep'])}秒{E}）。追跡中の敵へのダメージ{A}+{p['p_dmg']}%{E}。",
                "skill": f"対象へ突進（近くに追跡中の敵がいればそちらへ）して斬り、{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}の"
                         f"{O}物理ダメージ{E}。追跡中の対象には{A}+{p['q_track']}%{E}。",
                "skill2": f"その場に戻り点を残し移動速度{G}+{p['e_ms']}%{E}。{A}{s(p['e_win'])}秒{E}以内に危険になると自動で戻り点へ"
                          f"跳び、少しの間被ダメージ{A}{p['e_dr']}%{E}軽減。",
                "ult": f"自分から対象の背後まで斬線を予告し、対象を突き抜ける。一拍遅れて同じ線で斬撃：線上に残った敵に"
                       f"{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}の{O}物理ダメージ{E}。線から離れれば避けられる。",
            }, {"skill1": "掠め足", "skill2": "留め金", "ult": "拍外し"}),
            "ko": ({
                "name": "푸쒀",
                "attack": f"베기: {ADi}{O}100%{E} {O}물리 피해{E}. {O}걸음 세기{E}: 아군에게서 계속 멀어지는 적 챔피언을 추적한다"
                          f"({A}{s(p['p_keep'])}초{E}). 추적 중인 적에게 피해 {A}+{p['p_dmg']}%{E}.",
                "skill": f"대상에게 돌진(근처에 추적 중인 적 챔피언이 있으면 그쪽으로)해 베어 {O}{p['q_dmg']}{E} + "
                         f"{ADi}{O}{p['q_ad']}%{E} {O}물리 피해{E}. 추적 중인 대상에게는 {A}+{p['q_track']}%{E}.",
                "skill2": f"제자리에 회귀점을 남기고 이동 속도 {G}+{p['e_ms']}%{E}. {A}{s(p['e_win'])}초{E} 안에 위험해지면 회귀점으로 "
                          f"돌아가며 잠시 받는 피해 {A}{p['e_dr']}%{E} 감소.",
                "ult": f"자신에서 대상 뒤까지 이어지는 참격선을 예고하고 대상을 꿰뚫고 지나간다. 한 박자 뒤 같은 선에서 참격: "
                       f"선 위에 남은 적에게 {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} {O}물리 피해{E}. 제때 선을 벗어나면 피할 수 있다.",
            }, {"skill1": "계단 스치기", "skill2": "매듭 남기기", "ult": "엇박"}),
        }
    if hero == "yanxi":
        return {
            "zh-hans": ({
                "name": "盐汐",
                "attack": f"盐晶造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}析晶{E}：留在盐带里的敌人{R}减速{p['p_slow']}%{E}，每{A}{s(p['p_tick'])}秒{E}"
                          f"叠一层结晶（最多{A}{p['p_max']}{E}层）。",
                "skill": f"以目标为中心铺下一条盐带（{A}{s(p['q_t'])}秒{E}），带上的敌人受到{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}"
                         f"{M}魔法伤害{E}并叠一层结晶。",
                "skill2": f"引爆附近敌人的结晶：造成{M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E}{M}魔法伤害{E}，每层再加{M}{p['e_kdmg']}{E} + "
                          f"{APi}{M}{p['e_kap']}%{E}；结晶最多的敌方英雄被{R}定身{s(p['e_root'])}秒{E}。",
                "ult": f"让盐带朝自己退潮：晶浪扫过的敌人受到{M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E}{M}魔法伤害{E}，叠{A}{p['r_stack']}{E}层"
                       f"结晶并被{R}卷向盐汐{E}。没有盐带时先在目标处铺一条。",
            }, {"skill1": "撒线", "skill2": "凝结", "ult": "退潮"}),
            "zh-hant": ({
                "name": "鹽汐",
                "attack": f"鹽晶造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}析晶{E}：留在鹽帶裡的敵人{R}緩速{p['p_slow']}%{E}，每{A}{s(p['p_tick'])}秒{E}"
                          f"疊一層結晶（最多{A}{p['p_max']}{E}層）。",
                "skill": f"以目標為中心鋪下一條鹽帶（{A}{s(p['q_t'])}秒{E}），帶上的敵人受到{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}"
                         f"{M}魔法傷害{E}並疊一層結晶。",
                "skill2": f"引爆附近敵人的結晶：造成{M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E}{M}魔法傷害{E}，每層再加{M}{p['e_kdmg']}{E} + "
                          f"{APi}{M}{p['e_kap']}%{E}；結晶最多的敵方英雄被{R}定身{s(p['e_root'])}秒{E}。",
                "ult": f"讓鹽帶朝自己退潮：晶浪掃過的敵人受到{M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E}{M}魔法傷害{E}，疊{A}{p['r_stack']}{E}層"
                       f"結晶並被{R}捲向鹽汐{E}。沒有鹽帶時先在目標處鋪一條。",
            }, {"skill1": "撒線", "skill2": "凝結", "ult": "退潮"}),
            "en": ({
                "name": "Yan Xi",
                "attack": f"Salt shard: {ADi}{O}100%{E} {O}physical damage{E}. {O}Crystallize{E}: enemies who stay on her salt band "
                          f"are {R}slowed {p['p_slow']}%{E} and gain a crystal every {A}{s(p['p_tick'])}s{E} (up to {A}{p['p_max']}{E}).",
                "skill": f"Lays a salt band centred on the target for {A}{s(p['q_t'])}s{E}; enemies on it take {M}{p['q_dmg']}{E} + "
                         f"{APi}{M}{p['q_ap']}%{E} {M}magic damage{E} and gain a crystal.",
                "skill2": f"Shatters the crystals on nearby enemies: {M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E} {M}magic damage{E}, "
                          f"{M}{p['e_kdmg']}{E} + {APi}{M}{p['e_kap']}%{E} more per crystal; the enemy champion with the most is "
                          f"{R}rooted {s(p['e_root'])}s{E}.",
                "ult": f"Her band ebbs back toward her: the crystal wave deals {M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E} "
                       f"{M}magic damage{E}, adds {A}{p['r_stack']}{E} crystals and {R}drags enemies toward her{E}. Without a "
                       f"band she first lays one at the target.",
            }, {"skill1": "Salt Line", "skill2": "Congeal", "ult": "Ebb Tide"}),
            "ja": ({
                "name": "塩汐",
                "attack": f"塩晶：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}析晶{E}：塩の帯に留まる敵を{R}{p['p_slow']}%鈍足{E}にし、"
                          f"{A}{s(p['p_tick'])}秒{E}ごとに結晶を1つ重ねる（最大{A}{p['p_max']}{E}）。",
                "skill": f"対象を中心に塩の帯を敷く（{A}{s(p['q_t'])}秒{E}）。帯の上の敵に{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}の"
                         f"{M}魔法ダメージ{E}と結晶1つ。",
                "skill2": f"周囲の敵の結晶を砕き{M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E}の{M}魔法ダメージ{E}、1つごとに{M}{p['e_kdmg']}{E} + "
                          f"{APi}{M}{p['e_kap']}%{E}追加。最も多い敵チャンピオンを{R}{s(p['e_root'])}秒スネア{E}。",
                "ult": f"塩の帯を自分の方へ引かせる：結晶の波が当たった敵に{M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E}の"
                       f"{M}魔法ダメージ{E}、結晶{A}{p['r_stack']}{E}つ、{R}塩汐の方へ押し流す{E}。帯がなければ先に対象へ敷く。",
            }, {"skill1": "塩の線", "skill2": "凝結", "ult": "引き潮"}),
            "ko": ({
                "name": "옌시",
                "attack": f"소금 결정: {ADi}{O}100%{E} {O}물리 피해{E}. {O}결정 석출{E}: 소금띠 위에 머무는 적은 {R}{p['p_slow']}% 둔화{E}되고 "
                          f"{A}{s(p['p_tick'])}초{E}마다 결정이 1개 쌓인다(최대 {A}{p['p_max']}{E}개).",
                "skill": f"대상을 중심으로 소금띠를 깐다({A}{s(p['q_t'])}초{E}). 띠 위의 적은 {M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E} "
                         f"{M}마법 피해{E}를 입고 결정이 1개 쌓인다.",
                "skill2": f"주변 적의 결정을 터뜨려 {M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E} {M}마법 피해{E}, 결정마다 "
                          f"{M}{p['e_kdmg']}{E} + {APi}{M}{p['e_kap']}%{E} 추가. 결정이 가장 많은 적 챔피언은 {R}{s(p['e_root'])}초 속박{E}.",
                "ult": f"소금띠를 자신 쪽으로 썰물처럼 거둔다: 결정 파도에 휩쓸린 적은 {M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E} "
                       f"{M}마법 피해{E}, 결정 {A}{p['r_stack']}{E}개, {R}옌시 쪽으로 끌려온다{E}. 띠가 없으면 먼저 대상에 깐다.",
            }, {"skill1": "소금 줄", "skill2": "응결", "ult": "썰물"}),
        }
    if hero == "yindu":
        return {
            "zh-hans": ({
                "name": "殷渡",
                "attack": f"一拳造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}迎汐{E}：朝敌方英雄推进时攒潮势（最多{A}{p['p_max']}{E}层），下一次扣舷"
                          f"每层多{R}减速{p['q_slow_k']}%{E}。",
                "skill": f"朝目标短冲，被路上第一个敌人挡住就停下撞他：{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + {HPi}{O}{p['q_hp']}%{E}"
                         f"{O}物理伤害{E}，{R}眩晕{s(p['q_stun'])}秒{E}并{R}减速{p['q_slow']}%{E}。",
                "skill2": f"在目标那一群敌人中间插下航标（{A}{s(p['e_t'])}秒{E}），落下时身边的敌人受到{O}{p['e_dmg']}{E} + {HPi}{O}{p['e_hp']}%{E}"
                          f"{O}物理伤害{E}并{R}减速{p['e_slow']}%{E}。",
                "ult": f"从航标（没有就在目标脚下）两侧掀起潮墙往中间合拢：圈里的敌人被卷到汇合点，受到{O}{p['r_dmg']}{E} + "
                       f"{ADi}{O}{p['r_ad']}%{E} + {HPi}{O}{p['r_hp']}%{E}{O}物理伤害{E}并{R}眩晕{s(p['r_stun'])}秒{E}，每人只卷一次。",
            }, {"skill1": "扣舷", "skill2": "立标", "ult": "合汛"}),
            "zh-hant": ({
                "name": "殷渡",
                "attack": f"一拳造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}迎汐{E}：朝敵方英雄推進時攢潮勢（最多{A}{p['p_max']}{E}層），下一次扣舷"
                          f"每層多{R}緩速{p['q_slow_k']}%{E}。",
                "skill": f"朝目標短衝，被路上第一個敵人擋住就停下撞他：{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + {HPi}{O}{p['q_hp']}%{E}"
                         f"{O}物理傷害{E}，{R}暈眩{s(p['q_stun'])}秒{E}並{R}緩速{p['q_slow']}%{E}。",
                "skill2": f"在目標那一群敵人中間插下航標（{A}{s(p['e_t'])}秒{E}），落下時身邊的敵人受到{O}{p['e_dmg']}{E} + {HPi}{O}{p['e_hp']}%{E}"
                          f"{O}物理傷害{E}並{R}緩速{p['e_slow']}%{E}。",
                "ult": f"從航標（沒有就在目標腳下）兩側掀起潮牆往中間合攏：圈裡的敵人被捲到匯合點，受到{O}{p['r_dmg']}{E} + "
                       f"{ADi}{O}{p['r_ad']}%{E} + {HPi}{O}{p['r_hp']}%{E}{O}物理傷害{E}並{R}暈眩{s(p['r_stun'])}秒{E}，每人只捲一次。",
            }, {"skill1": "扣舷", "skill2": "立標", "ult": "合汛"}),
            "en": ({
                "name": "Yin Du",
                "attack": f"Punch: {ADi}{O}100%{E} {O}physical damage{E}. {O}Meeting Tide{E}: pushing toward enemy champions builds "
                          f"tide (up to {A}{p['p_max']}{E}); each stack adds {R}{p['q_slow_k']}% slow{E} to his next Bump the Gunwale.",
                "skill": f"Rams toward the target and stops at the first enemy in the way: {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + "
                         f"{HPi}{O}{p['q_hp']}%{E} {O}physical damage{E}, {R}stun {s(p['q_stun'])}s{E} and {R}{p['q_slow']}% slow{E}.",
                "skill2": f"Plants a beacon amid the target's group ({A}{s(p['e_t'])}s{E}); as it lands, nearby enemies take "
                          f"{O}{p['e_dmg']}{E} + {HPi}{O}{p['e_hp']}%{E} {O}physical damage{E} and are {R}slowed {p['e_slow']}%{E}.",
                "ult": f"Two tide walls close in from either side of his beacon (or the target): enemies inside are swept to the "
                       f"meeting point, take {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} + {HPi}{O}{p['r_hp']}%{E} {O}physical damage{E} "
                       f"and are {R}stunned {s(p['r_stun'])}s{E} - each swept once.",
            }, {"skill1": "Bump the Gunwale", "skill2": "Raise the Beacon", "ult": "Converging Tide"}),
            "ja": ({
                "name": "殷渡",
                "attack": f"拳：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}迎え潮{E}：敵チャンピオンへ押し進むと潮勢が溜まり（最大{A}{p['p_max']}{E}）、"
                          f"次の舷打ちの鈍足が1つごとに{R}+{p['q_slow_k']}%{E}。",
                "skill": f"対象へ突進し、途中の最初の敵で止まってぶつかる：{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + {HPi}{O}{p['q_hp']}%{E}の"
                         f"{O}物理ダメージ{E}、{R}スタン{s(p['q_stun'])}秒{E}、{R}{p['q_slow']}%鈍足{E}。",
                "skill2": f"対象の群れの中心に航標を立てる（{A}{s(p['e_t'])}秒{E}）。着地時に周囲の敵へ{O}{p['e_dmg']}{E} + {HPi}{O}{p['e_hp']}%{E}の"
                          f"{O}物理ダメージ{E}と{R}{p['e_slow']}%鈍足{E}。",
                "ult": f"航標（なければ対象）の両側から潮の壁が合わさる：中の敵を合流点へ巻き込み{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}"
                       f" + {HPi}{O}{p['r_hp']}%{E}の{O}物理ダメージ{E}、{R}スタン{s(p['r_stun'])}秒{E}。1人1回だけ。",
            }, {"skill1": "舷打ち", "skill2": "立標", "ult": "合わせ潮"}),
            "ko": ({
                "name": "인두",
                "attack": f"주먹: {ADi}{O}100%{E} {O}물리 피해{E}. {O}마중 물결{E}: 적 챔피언 쪽으로 밀고 나가면 조류가 쌓이고(최대 "
                          f"{A}{p['p_max']}{E}), 다음 뱃전 치기의 둔화가 중첩마다 {R}+{p['q_slow_k']}%{E}.",
                "skill": f"대상에게 돌진하다 처음 막아서는 적에서 멈춰 부딪친다: {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} + "
                         f"{HPi}{O}{p['q_hp']}%{E} {O}물리 피해{E}, {R}기절 {s(p['q_stun'])}초{E}, {R}{p['q_slow']}% 둔화{E}.",
                "skill2": f"대상 무리 한가운데 부표를 세운다({A}{s(p['e_t'])}초{E}). 떨어질 때 주변 적에게 {O}{p['e_dmg']}{E} + "
                          f"{HPi}{O}{p['e_hp']}%{E} {O}물리 피해{E}와 {R}{p['e_slow']}% 둔화{E}.",
                "ult": f"부표(없으면 대상) 양쪽에서 조류 벽이 모인다: 안의 적은 합류점으로 휩쓸려 {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}"
                       f" + {HPi}{O}{p['r_hp']}%{E} {O}물리 피해{E}와 {R}기절 {s(p['r_stun'])}초{E}. 한 명당 한 번.",
            }, {"skill1": "뱃전 치기", "skill2": "부표 세우기", "ult": "합류 조류"}),
        }
    if hero == "lanti":
        return {
            "zh-hans": ({
                "name": "澜缇",
                "attack": f"一拳造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}折纹{E}：只标记最近一个用技能伤到她的敌方英雄（{A}{s(p['p_t'])}秒{E}）。",
                "skill": f"连出两拳：{O}{p['q1_dmg']}{E} + {ADi}{O}{p['q1_ad']}%{E}，再{O}{p['q2_dmg']}{E} + {ADi}{O}{p['q2_ad']}%{E}"
                         f"{O}物理伤害{E}；第二拳打到带折纹的人时用掉折纹，这一拳{A}+{p['q_mark']}%{E}并{R}减速{p['q_slow']}%{E}。",
                "skill2": f"起架{A}{s(p['e_t'])}秒{E}：受到的技能伤害降低{A}{p['e_dr']}%{E}；架着挨了一下技能就算成功，双棱冷却刷新，挡下的伤害记进还响。",
                "ult": f"推出一道玻璃波：路上的敌人受到{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}{O}物理伤害{E}，加上最近挡下伤害的"
                       f"{A}{p['r_k']}%{E}（最多{A}+{p['r_cap']}{E}），并{R}减速{p['r_slow']}%{E}。",
            }, {"skill1": "双棱", "skill2": "候击", "ult": "还响"}),
            "zh-hant": ({
                "name": "瀾緹",
                "attack": f"一拳造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}折紋{E}：只標記最近一個用技能傷到她的敵方英雄（{A}{s(p['p_t'])}秒{E}）。",
                "skill": f"連出兩拳：{O}{p['q1_dmg']}{E} + {ADi}{O}{p['q1_ad']}%{E}，再{O}{p['q2_dmg']}{E} + {ADi}{O}{p['q2_ad']}%{E}"
                         f"{O}物理傷害{E}；第二拳打到帶折紋的人時用掉折紋，這一拳{A}+{p['q_mark']}%{E}並{R}緩速{p['q_slow']}%{E}。",
                "skill2": f"起架{A}{s(p['e_t'])}秒{E}：受到的技能傷害降低{A}{p['e_dr']}%{E}；架著挨了一下技能就算成功，雙稜冷卻刷新，擋下的傷害記進還響。",
                "ult": f"推出一道玻璃波：路上的敵人受到{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}{O}物理傷害{E}，加上最近擋下傷害的"
                       f"{A}{p['r_k']}%{E}（最多{A}+{p['r_cap']}{E}），並{R}緩速{p['r_slow']}%{E}。",
            }, {"skill1": "雙稜", "skill2": "候擊", "ult": "還響"}),
            "en": ({
                "name": "Lan Ti",
                "attack": f"Punch: {ADi}{O}100%{E} {O}physical damage{E}. {O}Fracture Mark{E}: marks only the latest enemy champion who "
                          f"hurt her with a spell ({A}{s(p['p_t'])}s{E}).",
                "skill": f"Two punches: {O}{p['q1_dmg']}{E} + {ADi}{O}{p['q1_ad']}%{E}, then {O}{p['q2_dmg']}{E} + {ADi}{O}{p['q2_ad']}%{E} "
                         f"{O}physical damage{E}; the second breaks a Fracture Mark for {A}+{p['q_mark']}%{E} and {R}{p['q_slow']}% slow{E}.",
                "skill2": f"Guards for {A}{s(p['e_t'])}s{E}: {A}{p['e_dr']}%{E} less spell damage. A spell caught in the guard resets "
                          f"Double Prism and the blocked damage feeds Returning Echo.",
                "ult": f"Sends a glass wave forward: {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} {O}physical damage{E} plus "
                       f"{A}{p['r_k']}%{E} of the damage she recently blocked (up to {A}+{p['r_cap']}{E}), and {R}{p['r_slow']}% slow{E}.",
            }, {"skill1": "Double Prism", "skill2": "Await the Strike", "ult": "Returning Echo"}),
            "ja": ({
                "name": "瀾緹",
                "attack": f"拳：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}折れ紋{E}：最後にスキルで彼女を傷つけた敵チャンピオン1人だけに"
                          f"紋を刻む（{A}{s(p['p_t'])}秒{E}）。",
                "skill": f"2連打：{O}{p['q1_dmg']}{E} + {ADi}{O}{p['q1_ad']}%{E}、続けて{O}{p['q2_dmg']}{E} + {ADi}{O}{p['q2_ad']}%{E}の"
                         f"{O}物理ダメージ{E}。2発目が紋を割ると{A}+{p['q_mark']}%{E}と{R}{p['q_slow']}%鈍足{E}。",
                "skill2": f"{A}{s(p['e_t'])}秒{E}構える：受けるスキルダメージ{A}{p['e_dr']}%{E}軽減。構え中にスキルを受けると成功、"
                          f"双稜のCTが戻り、防いだ分が返し響きに溜まる。",
                "ult": f"ガラスの波を放ち{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}の{O}物理ダメージ{E}、さらに最近防いだダメージの"
                       f"{A}{p['r_k']}%{E}（最大{A}+{p['r_cap']}{E}）と{R}{p['r_slow']}%鈍足{E}。",
            }, {"skill1": "双稜", "skill2": "待ち撃ち", "ult": "返し響き"}),
            "ko": ({
                "name": "란티",
                "attack": f"주먹: {ADi}{O}100%{E} {O}물리 피해{E}. {O}꺾인 무늬{E}: 마지막으로 스킬로 그녀를 다치게 한 적 챔피언 한 명만 "
                          f"표식한다({A}{s(p['p_t'])}초{E}).",
                "skill": f"두 번 친다: {O}{p['q1_dmg']}{E} + {ADi}{O}{p['q1_ad']}%{E}, 이어서 {O}{p['q2_dmg']}{E} + {ADi}{O}{p['q2_ad']}%{E} "
                         f"{O}물리 피해{E}. 두 번째 주먹이 표식을 깨면 {A}+{p['q_mark']}%{E}와 {R}{p['q_slow']}% 둔화{E}.",
                "skill2": f"{A}{s(p['e_t'])}초{E} 동안 자세를 잡아 받는 스킬 피해 {A}{p['e_dr']}%{E} 감소. 그동안 스킬을 맞으면 성공: 쌍능 "
                          f"재사용 대기시간 초기화, 막은 피해는 되울림에 쌓인다.",
                "ult": f"유리 파도를 내보내 {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} {O}물리 피해{E}에 최근 막은 피해의 "
                       f"{A}{p['r_k']}%{E}(최대 {A}+{p['r_cap']}{E})를 더하고 {R}{p['r_slow']}% 둔화{E}.",
            }, {"skill1": "쌍능", "skill2": "기다린 일격", "ult": "되울림"}),
        }
    if hero == "luxin":
        return {
            "zh-hans": ({
                "name": "鹭芯",
                "attack": f"一刀造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}追羽{E}：被她打过的敌方英雄继续逃远时，脚下留下羽迹（最多两段，"
                          f"{A}{s(p['p_t'])}秒{E}）。",
                "skill": f"顺着目标逃的方向追过去，贴近后切击，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}{O}物理伤害{E}。",
                "skill2": f"在目标脚下拉一道风线（{A}{s(p['e_t'])}秒{E}），之后穿过风线的敌人受到{O}{p['e_dmg']}{E} + {ADi}{O}{p['e_ad']}%{E}"
                          f"{O}物理伤害{E}并{R}减速{p['e_slow']}%{E}。",
                "ult": f"顺着目标的两段羽迹各穿过他切一刀，每刀{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}{O}物理伤害{E}，每段羽迹再"
                       f"{A}+{p['r_trail']}%{E}；第二刀按他已损失的生命最多{A}+{p['r_low']}%{E}。",
            }, {"skill1": "贴风", "skill2": "折鸢", "ult": "收线"}),
            "zh-hant": ({
                "name": "鷺芯",
                "attack": f"一刀造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}追羽{E}：被她打過的敵方英雄繼續逃遠時，腳下留下羽跡（最多兩段，"
                          f"{A}{s(p['p_t'])}秒{E}）。",
                "skill": f"順著目標逃的方向追過去，貼近後切擊，造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}{O}物理傷害{E}。",
                "skill2": f"在目標腳下拉一道風線（{A}{s(p['e_t'])}秒{E}），之後穿過風線的敵人受到{O}{p['e_dmg']}{E} + {ADi}{O}{p['e_ad']}%{E}"
                          f"{O}物理傷害{E}並{R}緩速{p['e_slow']}%{E}。",
                "ult": f"順著目標的兩段羽跡各穿過他切一刀，每刀{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}{O}物理傷害{E}，每段羽跡再"
                       f"{A}+{p['r_trail']}%{E}；第二刀按他已損失的生命最多{A}+{p['r_low']}%{E}。",
            }, {"skill1": "貼風", "skill2": "折鳶", "ult": "收線"}),
            "en": ({
                "name": "Lu Xin",
                "attack": f"Slash: {ADi}{O}100%{E} {O}physical damage{E}. {O}Chasing Feather{E}: an enemy champion she hit who keeps "
                          f"running leaves feather trails behind ({A}{s(p['p_t'])}s{E}, two at most).",
                "skill": f"Chases along the way the target flees and cuts when close: {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} "
                         f"{O}physical damage{E}.",
                "skill2": f"Draws a wind line at the target's feet ({A}{s(p['e_t'])}s{E}); enemies who cross it take {O}{p['e_dmg']}{E} + "
                          f"{ADi}{O}{p['e_ad']}%{E} {O}physical damage{E} and are {R}slowed {p['e_slow']}%{E}.",
                "ult": f"Cuts through the target along each of his two feather trails: {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} "
                       f"{O}physical damage{E} per cut, {A}+{p['r_trail']}%{E} per trail; the second cut deals up to "
                       f"{A}+{p['r_low']}%{E} by his missing health.",
            }, {"skill1": "Cling to the Wind", "skill2": "Folded Kite", "ult": "Reel In"}),
            "ja": ({
                "name": "鷺芯",
                "attack": f"斬撃：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}追い羽{E}：彼女が斬った敵チャンピオンが逃げ続けると羽の跡が残る"
                          f"（{A}{s(p['p_t'])}秒{E}、最大2つ）。",
                "skill": f"対象の逃げる方向へ追いすがり、近づいて斬る：{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}の{O}物理ダメージ{E}。",
                "skill2": f"対象の足元に風の線を張る（{A}{s(p['e_t'])}秒{E}）。線を越えた敵に{O}{p['e_dmg']}{E} + {ADi}{O}{p['e_ad']}%{E}の"
                          f"{O}物理ダメージ{E}と{R}{p['e_slow']}%鈍足{E}。",
                "ult": f"対象の2つの羽の跡に沿って貫き1太刀ずつ：各{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}の{O}物理ダメージ{E}、"
                       f"跡1つごとに{A}+{p['r_trail']}%{E}。2太刀目は失ったHPに応じ最大{A}+{p['r_low']}%{E}。",
            }, {"skill1": "風寄せ", "skill2": "折り鳶", "ult": "糸手繰り"}),
            "ko": ({
                "name": "루신",
                "attack": f"베기: {ADi}{O}100%{E} {O}물리 피해{E}. {O}쫓는 깃{E}: 그녀에게 맞은 적 챔피언이 계속 달아나면 깃 자국이 남는다"
                          f"({A}{s(p['p_t'])}초{E}, 최대 두 개).",
                "skill": f"대상이 달아나는 방향을 따라 쫓아가 가까이서 벤다: {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} {O}물리 피해{E}.",
                "skill2": f"대상의 발밑에 바람 줄을 긋는다({A}{s(p['e_t'])}초{E}). 줄을 넘는 적은 {O}{p['e_dmg']}{E} + {ADi}{O}{p['e_ad']}%{E} "
                          f"{O}물리 피해{E}와 {R}{p['e_slow']}% 둔화{E}.",
                "ult": f"대상의 두 깃 자국을 따라 꿰뚫으며 한 번씩 벤다: 각 {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} {O}물리 피해{E}, "
                       f"자국마다 {A}+{p['r_trail']}%{E}. 두 번째 베기는 잃은 체력에 따라 최대 {A}+{p['r_low']}%{E}.",
            }, {"skill1": "바람 붙기", "skill2": "접은 연", "ult": "실 감기"}),
        }
    if hero == "jiyan":
        return {
            "zh-hans": ({
                "name": "霁砚",
                "attack": f"星针造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}定标{E}：长刻打中的地方、照盘放的地方留下坐标（{A}{s(p['p_t'])}秒{E}，"
                          f"最多{A}{p['p_max']}{E}个）。",
                "skill": f"射出细长星束，线上的敌人受到{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}{M}魔法伤害{E}；星束经过她的坐标时坐标炸开，"
                         f"周围受到{M}{p['q_burst']}{E} + {APi}{M}{p['q_bap']}%{E}{M}魔法伤害{E}。",
                "skill2": f"在远处目标脚下放坐标，片刻后照亮：周围敌人受到{M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E}{M}魔法伤害{E}并"
                          f"{R}减速{p['e_slow']}%{E}。",
                "ult": f"沿目标方向挑三处错开的落点（有坐标就落在坐标上），各自先亮预警圈，再落下星刻：受到{M}{p['r_dmg']}{E} + "
                       f"{APi}{M}{p['r_ap']}%{E}{M}魔法伤害{E}并{R}减速{p['r_slow']}%{E}。",
            }, {"skill1": "长刻", "skill2": "照盘", "ult": "星历"}),
            "zh-hant": ({
                "name": "霽硯",
                "attack": f"星針造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}定標{E}：長刻打中的地方、照盤放的地方留下座標（{A}{s(p['p_t'])}秒{E}，"
                          f"最多{A}{p['p_max']}{E}個）。",
                "skill": f"射出細長星束，線上的敵人受到{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}{M}魔法傷害{E}；星束經過她的座標時座標炸開，"
                         f"周圍受到{M}{p['q_burst']}{E} + {APi}{M}{p['q_bap']}%{E}{M}魔法傷害{E}。",
                "skill2": f"在遠處目標腳下放座標，片刻後照亮：周圍敵人受到{M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E}{M}魔法傷害{E}並"
                          f"{R}緩速{p['e_slow']}%{E}。",
                "ult": f"沿目標方向挑三處錯開的落點（有座標就落在座標上），各自先亮預警圈，再落下星刻：受到{M}{p['r_dmg']}{E} + "
                       f"{APi}{M}{p['r_ap']}%{E}{M}魔法傷害{E}並{R}緩速{p['r_slow']}%{E}。",
            }, {"skill1": "長刻", "skill2": "照盤", "ult": "星曆"}),
            "en": ({
                "name": "Ji Yan",
                "attack": f"Star needle: {ADi}{O}100%{E} {O}physical damage{E}. {O}Set the Mark{E}: where Long Engraving hits and where "
                          f"Light the Chart lands she leaves a coordinate ({A}{s(p['p_t'])}s{E}, up to {A}{p['p_max']}{E}).",
                "skill": f"Fires a long thin star beam: {M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E} {M}magic damage{E} along it; a "
                         f"coordinate it crosses bursts for {M}{p['q_burst']}{E} + {APi}{M}{p['q_bap']}%{E} {M}magic damage{E} around it.",
                "skill2": f"Places a coordinate at a distant target's feet; a moment later it lights up: {M}{p['e_dmg']}{E} + "
                          f"{APi}{M}{p['e_ap']}%{E} {M}magic damage{E} and {R}{p['e_slow']}% slow{E} nearby.",
                "ult": f"Picks three staggered landings along the aim (on her coordinates when close), each with its own warning "
                       f"ring, then drops a star on each: {M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E} {M}magic damage{E} and "
                       f"{R}{p['r_slow']}% slow{E}.",
            }, {"skill1": "Long Engraving", "skill2": "Light the Chart", "ult": "Star Almanac"}),
            "ja": ({
                "name": "霽硯",
                "attack": f"星針：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}定標{E}：長刻の命中点と照盤の設置点に座標を残す"
                          f"（{A}{s(p['p_t'])}秒{E}、最大{A}{p['p_max']}{E}）。",
                "skill": f"細長い星の光線：線上の敵に{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}の{M}魔法ダメージ{E}。通った座標は弾け、"
                         f"周囲に{M}{p['q_burst']}{E} + {APi}{M}{p['q_bap']}%{E}。",
                "skill2": f"遠くの対象の足元に座標を置き、少し後に照らす：周囲の敵に{M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E}の"
                          f"{M}魔法ダメージ{E}と{R}{p['e_slow']}%鈍足{E}。",
                "ult": f"狙う方向にずらした3か所（近くに座標があればそこ）へ、それぞれ予告円を出してから星刻を落とす："
                       f"{M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E}の{M}魔法ダメージ{E}と{R}{p['r_slow']}%鈍足{E}。",
            }, {"skill1": "長刻", "skill2": "照盤", "ult": "星暦"}),
            "ko": ({
                "name": "지옌",
                "attack": f"별바늘: {ADi}{O}100%{E} {O}물리 피해{E}. {O}좌표 찍기{E}: 긴 새김이 맞은 곳과 반 비추기를 둔 곳에 좌표를 "
                          f"남긴다({A}{s(p['p_t'])}초{E}, 최대 {A}{p['p_max']}{E}개).",
                "skill": f"가늘고 긴 별빛을 쏴 선 위의 적에게 {M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E} {M}마법 피해{E}. 지나간 좌표는 "
                         f"터지며 주변에 {M}{p['q_burst']}{E} + {APi}{M}{p['q_bap']}%{E}.",
                "skill2": f"먼 대상의 발밑에 좌표를 두고 잠시 뒤 비춘다: 주변 적에게 {M}{p['e_dmg']}{E} + {APi}{M}{p['e_ap']}%{E} "
                          f"{M}마법 피해{E}와 {R}{p['e_slow']}% 둔화{E}.",
                "ult": f"조준 방향에 엇갈린 세 곳(근처에 좌표가 있으면 좌표)에 각각 경고 원을 띄운 뒤 별을 떨어뜨린다: "
                       f"{M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E} {M}마법 피해{E}와 {R}{p['r_slow']}% 둔화{E}.",
            }, {"skill1": "긴 새김", "skill2": "반 비추기", "ult": "성력"}),
        }
    if hero == "zhongli":
        full = p["p_as"] * p["p_levels"]
        return {
            "zh-hans": ({
                "name": "钟砾",
                "attack": f"弹丸造成{ADi}{O}100%{E}{O}物理伤害{E}。{O}定脚{E}：站稳{A}{s(p['p_still'])}秒{E}后攻速逐渐提高（最多{A}+{full}%{E}），"
                          f"明显走开就解除。",
                "skill": f"压上弹簧：下一发普攻额外造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}{O}物理伤害{E}，定脚时还无视{A}{p['q_pen']}%{E}护甲。",
                "skill2": f"架起支架：获得{S}{p['e_sh']}{E} + {HPi}{S}{p['e_hp']}%{E}的{S}护盾{E}（{A}{s(p['e_t'])}秒{E}），定脚直接满档；走开时支架收起。",
                "ult": f"朝出手方向连放四发，每发{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}{O}物理伤害{E}，最后一发{A}{p['r_last']}%{E}；"
                       f"被控制或离开原地就停。",
            }, {"skill1": "压簧", "skill2": "落架", "ult": "齐鸣"}),
            "zh-hant": ({
                "name": "鐘礫",
                "attack": f"彈丸造成{ADi}{O}100%{E}{O}物理傷害{E}。{O}定腳{E}：站穩{A}{s(p['p_still'])}秒{E}後攻速逐漸提高（最多{A}+{full}%{E}），"
                          f"明顯走開就解除。",
                "skill": f"壓上彈簧：下一發普攻額外造成{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}{O}物理傷害{E}，定腳時還無視{A}{p['q_pen']}%{E}護甲。",
                "skill2": f"架起支架：獲得{S}{p['e_sh']}{E} + {HPi}{S}{p['e_hp']}%{E}的{S}護盾{E}（{A}{s(p['e_t'])}秒{E}），定腳直接滿檔；走開時支架收起。",
                "ult": f"朝出手方向連放四發，每發{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}{O}物理傷害{E}，最後一發{A}{p['r_last']}%{E}；"
                       f"被控制或離開原地就停。",
            }, {"skill1": "壓簧", "skill2": "落架", "ult": "齊鳴"}),
            "en": ({
                "name": "Zhong Li",
                "attack": f"Pellet: {ADi}{O}100%{E} {O}physical damage{E}. {O}Planted Feet{E}: after standing still for "
                          f"{A}{s(p['p_still'])}s{E} his attack speed climbs (up to {A}+{full}%{E}); walking off ends it.",
                "skill": f"Compresses the spring: his next attack deals {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} extra "
                         f"{O}physical damage{E}, ignoring {A}{p['q_pen']}%{E} armor while planted.",
                "skill2": f"Deploys a stand: a {S}shield{E} of {S}{p['e_sh']}{E} + {HPi}{S}{p['e_hp']}%{E} for {A}{s(p['e_t'])}s{E} and "
                          f"Planted Feet at full; stepping away packs it up.",
                "ult": f"Fires four shots in the direction he aimed, {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} {O}physical damage{E} "
                       f"each, the last {A}{p['r_last']}%{E}; crowd control or leaving his spot stops the rest.",
            }, {"skill1": "Compress the Spring", "skill2": "Deploy the Stand", "ult": "Chorus"}),
            "ja": ({
                "name": "鐘礫",
                "attack": f"弾丸：{ADi}{O}100%{E}の{O}物理ダメージ{E}。{O}足固め{E}：{A}{s(p['p_still'])}秒{E}立ち止まると攻撃速度が上がっていく"
                          f"（最大{A}+{full}%{E}）。大きく動くと解除。",
                "skill": f"発条を込める：次の通常攻撃が{O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E}の追加{O}物理ダメージ{E}、足固め中は"
                         f"物防{A}{p['q_pen']}%{E}貫通。",
                "skill2": f"架台を展開：{S}{p['e_sh']}{E} + {HPi}{S}{p['e_hp']}%{E}の{S}シールド{E}（{A}{s(p['e_t'])}秒{E}）、足固めが即最大。"
                          f"離れると架台をたたむ。",
                "ult": f"狙った方向へ4連射、各{O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E}の{O}物理ダメージ{E}、最後の1発は"
                       f"{A}{p['r_last']}%{E}。CCを受けるかその場を離れると止まる。",
            }, {"skill1": "発条込め", "skill2": "架台展開", "ult": "斉鳴"}),
            "ko": ({
                "name": "중리",
                "attack": f"탄환: {ADi}{O}100%{E} {O}물리 피해{E}. {O}발 고정{E}: {A}{s(p['p_still'])}초{E} 동안 멈춰 서면 공격 속도가 점점 "
                          f"오른다(최대 {A}+{full}%{E}). 크게 움직이면 해제.",
                "skill": f"용수철을 눌러 다음 기본 공격이 {O}{p['q_dmg']}{E} + {ADi}{O}{p['q_ad']}%{E} 추가 {O}물리 피해{E}, 발 고정 중에는 "
                         f"방어력 {A}{p['q_pen']}%{E} 관통.",
                "skill2": f"거치대를 펼쳐 {S}{p['e_sh']}{E} + {HPi}{S}{p['e_hp']}%{E} {S}보호막{E}({A}{s(p['e_t'])}초{E})을 얻고 발 고정이 즉시 "
                          f"최대. 자리를 떠나면 거치대를 접는다.",
                "ult": f"조준한 방향으로 네 발을 쏜다. 각 {O}{p['r_dmg']}{E} + {ADi}{O}{p['r_ad']}%{E} {O}물리 피해{E}, 마지막 발은 "
                       f"{A}{p['r_last']}%{E}. 군중 제어를 받거나 자리를 떠나면 멈춘다.",
            }, {"skill1": "용수철 압축", "skill2": "거치대", "ult": "일제 울림"}),
        }
    if hero == "wuling":
        return {
            "zh-hans": ({
                "name": "雾绫",
                "attack": f"铃音造成{ADi}{O}100%{E}{O}物理伤害{E}和{APi}{M}{p['a_ap']}%{E}{M}魔法伤害{E}。{O}闻铃{E}：碰到她技能区域的敌人被挂铃"
                          f"（{A}{s(p['p_t'])}秒{E}），他掉血时身边的友军移速{G}+{p['p_ms']}%{E}。",
                "skill": f"在目标脚下放地铃（{A}{s(p['q_t'])}秒{E}），敌人靠近就响：周围敌人受到{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}"
                         f"{M}魔法伤害{E}并{R}减速{p['q_slow']}%{E}。",
                "skill2": f"在她与目标之间竖起短幕（{A}{s(p['e_t'])}秒{E}）：友军穿过移速{G}+{p['e_ms']}%{E}，敌人穿过被挂铃并{R}减速{p['e_slow']}%{E}。",
                "ult": f"在目标脚下两侧拉起纱幕往中间合拢：圈里的敌人受到{M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E}{M}魔法伤害{E}、"
                       f"{R}减速{p['r_slow']}%{E}再{R}定身{s(p['r_root'])}秒{E}，每人只触发一次。",
            }, {"skill1": "系铃", "skill2": "挪幕", "ult": "合幕"}),
            "zh-hant": ({
                "name": "霧綾",
                "attack": f"鈴音造成{ADi}{O}100%{E}{O}物理傷害{E}和{APi}{M}{p['a_ap']}%{E}{M}魔法傷害{E}。{O}聞鈴{E}：碰到她技能區域的敵人被掛鈴"
                          f"（{A}{s(p['p_t'])}秒{E}），他掉血時身邊的友軍移速{G}+{p['p_ms']}%{E}。",
                "skill": f"在目標腳下放地鈴（{A}{s(p['q_t'])}秒{E}），敵人靠近就響：周圍敵人受到{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}"
                         f"{M}魔法傷害{E}並{R}緩速{p['q_slow']}%{E}。",
                "skill2": f"在她與目標之間豎起短幕（{A}{s(p['e_t'])}秒{E}）：友軍穿過移速{G}+{p['e_ms']}%{E}，敵人穿過被掛鈴並{R}緩速{p['e_slow']}%{E}。",
                "ult": f"在目標腳下兩側拉起紗幕往中間合攏：圈裡的敵人受到{M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E}{M}魔法傷害{E}、"
                       f"{R}緩速{p['r_slow']}%{E}再{R}定身{s(p['r_root'])}秒{E}，每人只觸發一次。",
            }, {"skill1": "繫鈴", "skill2": "挪幕", "ult": "合幕"}),
            "en": ({
                "name": "Wu Ling",
                "attack": f"Bell chime: {ADi}{O}100%{E} {O}physical damage{E} and {APi}{M}{p['a_ap']}%{E} {M}magic damage{E}. "
                          f"{O}Hear the Bell{E}: enemies who touch her areas are belled ({A}{s(p['p_t'])}s{E}); when a belled enemy is "
                          f"hurt, nearby allies gain {G}+{p['p_ms']}%{E} move speed.",
                "skill": f"Places a ground bell at the target ({A}{s(p['q_t'])}s{E}) that rings when an enemy comes close: "
                         f"{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E} {M}magic damage{E} and {R}{p['q_slow']}% slow{E} around it.",
                "skill2": f"Raises a short curtain between her and the target ({A}{s(p['e_t'])}s{E}): allies passing through gain "
                          f"{G}+{p['e_ms']}%{E} move speed, enemies passing through are belled and {R}slowed {p['e_slow']}%{E}.",
                "ult": f"Two curtains close in round the target: enemies inside take {M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E} "
                       f"{M}magic damage{E}, are {R}slowed {p['r_slow']}%{E} and {R}rooted {s(p['r_root'])}s{E} - once each.",
            }, {"skill1": "Tie the Bell", "skill2": "Shift the Curtain", "ult": "Draw the Curtains"}),
            "ja": ({
                "name": "霧綾",
                "attack": f"鈴の音：{ADi}{O}100%{E}の{O}物理ダメージ{E}と{APi}{M}{p['a_ap']}%{E}の{M}魔法ダメージ{E}。{O}鈴聞き{E}：技の範囲に触れた敵に"
                          f"鈴を付け（{A}{s(p['p_t'])}秒{E}）、その敵が傷つくと近くの味方の移動速度{G}+{p['p_ms']}%{E}。",
                "skill": f"対象の足元に地鈴を置く（{A}{s(p['q_t'])}秒{E}）。敵が近づくと鳴り、周囲に{M}{p['q_dmg']}{E} + {APi}{M}{p['q_ap']}%{E}の"
                         f"{M}魔法ダメージ{E}と{R}{p['q_slow']}%鈍足{E}。",
                "skill2": f"自分と対象の間に短い幕を立てる（{A}{s(p['e_t'])}秒{E}）：くぐった味方は移動速度{G}+{p['e_ms']}%{E}、くぐった敵は"
                          f"鈴付きで{R}{p['e_slow']}%鈍足{E}。",
                "ult": f"対象の両側から幕を閉じる：中の敵に{M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E}の{M}魔法ダメージ{E}、"
                       f"{R}{p['r_slow']}%鈍足{E}のあと{R}{s(p['r_root'])}秒スネア{E}。1人1回だけ。",
            }, {"skill1": "鈴結び", "skill2": "幕移し", "ult": "幕引き"}),
            "ko": ({
                "name": "우링",
                "attack": f"방울 소리: {ADi}{O}100%{E} {O}물리 피해{E}와 {APi}{M}{p['a_ap']}%{E} {M}마법 피해{E}. {O}방울 소리{E}: 그녀의 "
                          f"스킬 범위에 닿은 적에게 방울을 단다({A}{s(p['p_t'])}초{E}). 그 적이 피해를 입으면 주변 아군 이동 속도 "
                          f"{G}+{p['p_ms']}%{E}.",
                "skill": f"대상 발밑에 땅방울을 둔다({A}{s(p['q_t'])}초{E}). 적이 다가오면 울려 주변에 {M}{p['q_dmg']}{E} + "
                         f"{APi}{M}{p['q_ap']}%{E} {M}마법 피해{E}와 {R}{p['q_slow']}% 둔화{E}.",
                "skill2": f"자신과 대상 사이에 짧은 장막을 세운다({A}{s(p['e_t'])}초{E}): 통과한 아군은 이동 속도 {G}+{p['e_ms']}%{E}, "
                          f"통과한 적은 방울이 달리고 {R}{p['e_slow']}% 둔화{E}.",
                "ult": f"대상 양쪽에서 장막을 닫는다: 안의 적은 {M}{p['r_dmg']}{E} + {APi}{M}{p['r_ap']}%{E} {M}마법 피해{E}, "
                       f"{R}{p['r_slow']}% 둔화{E} 후 {R}{s(p['r_root'])}초 속박{E}. 한 명당 한 번.",
            }, {"skill1": "방울 매기", "skill2": "장막 옮기기", "ult": "장막 닫기"}),
        }
    raise SystemExit(f"unknown hero {hero}")


def sounds(hid):
    """九句配音：事件 <id>_v_<x> 放片段 <id>_vo_<x>（Codex 的普通话试音）。"""
    return {f"{hid}_v_{v}": [(f"{hid}_vo_{v}", 0.8, 0.0)] for v in VOICE}


def view(hero):
    v = VIEW[hero]
    return {k: {"x": x, "y": y} for k, (x, y) in v.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append", choices=HEROES)
    ap.add_argument("--check-lengths", action="store_true", help="只看说明长度，不写文件")
    a = ap.parse_args()
    bad = False
    for hero in a.hero or HEROES:
        mod = importlib.import_module(f"build_{hero}")
        p = dict(mod.P)
        tx = texts(hero, p)
        print(f"== {hero}")
        bad |= B.check_lengths({lang: d for lang, (d, _) in tx.items()})
        if a.check_lengths:
            continue
        hid = f"border_{hero}"
        n, c = B.write_hero(hid, tx, sounds(hid), view(hero), hero, "tools/kit/seed_border_audio.py")
        print(f"   {n} sounds, {c} clips")
    if not a.check_lengths:
        B.write_mod_info()
    if bad:
        sys.exit("a text is longer than the tooltip box")


if __name__ == "__main__":
    main()
