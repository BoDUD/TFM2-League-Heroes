#!/usr/bin/env python3
"""奥丁（终末包第二十四个英雄 ragnarok_odin，中路，Magician）的 .data_champion，数值在参数表 P 里。

    python tools/kit/build_odin.py [--set key=value ...] [--out file] [--params json] [--nodes] [--plain]

终末的女武神第十二回合的神方代表：北欧的最高神、「天界最强的战争神」，和坂田金时打的那个。武器是冈格尼尔（原本是戈尔尼尔用
世界树的枝做的项链，他立誓毁灭世界以后把它变成了枪），能用《至高者箴言》里记的十八首呪歌（Átján Galdor）。第十二回合用到的：
- 第五呪歌・神環封壁（Fimmti Galdor: Fafnir）：五面刻着古诺尔斯文的大盾绕身，什么都挡得住——只挡不住冈格尼尔；
- 第九呪歌・旋影風牙（Níundi Galdor: Vindskǫggull）：符文缠住冈格尼尔掷出去，一定打中，对手跑、闪都会追上去，无视防御和
  耐久，打中以后回到奥丁手里（第 114、116 话）；
- 第十四呪歌・心弦融歌（Fjórtándi Galdor: Harpalúðr）：枪尖一下下叩地，身上张开许多张嘴齐唱，再一叩，符文带扫过场上每个人：
  听到的人身体都听奥丁的（金时挥斧时右臂自己扭断了），唱得越久越绝对（第 120 话）；
- 第十五呪歌・波命湧出（Fimmdánti Galdor: Iðunnar Koppr）：冈格尼尔变回项链，链子化成光藤缝合伤口（第 117 话）；
- 胡金和雾尼两只渡鸦一直停在他身边。
美术、图标、音效是 Codex 的（assets/source/odin/，交接说明 assets/source/odin/HANDOFF.md；两句日语是速水奨在第三季官方预告里
说的「夙愿」「警告」）。位置是中路法师（用户 2026-11-27 定的）：呪歌都按法术强度（ApAttack 的 attack_ratio 是法强的百分比），
刺击是冈格尼尔的近战。
  被动    第十五呪歌・波命湧出（ragnarok.dll）：生命掉到 p_hp% 以下时，p_t 拍里回 p_heal + p_ap% 法强的生命，冷却 p_cd 拍。
          写在普攻说明里。
  attack  冈格尼尔刺击 `Enemy`（塔也打）：100% 攻击力的物理伤害，加 a_dmg + a_ap% 法强的魔法伤害，atk_st 拍（第 5 帧，
          0.381 秒）刺中，枪长（射程 atk_range）。
  skill   第九呪歌・旋影風牙：`Targeting` 敌方英雄（q_range）：q_go 拍（第 4 帧，0.375 秒）掷出冈格尼尔（TargetProjectile，
          每拍 q_speed，追着目标飞，一定打中）：q_dmg + q_ap% 法强的魔法伤害，无视魔抗（同一拍挂 100% 魔法穿透），目标的护盾
          先被穿透（ragnarok.dll：打中时目标带着 q_mark 的标记，护盾清零）。枪打中后化成黑色流光回到他手里（第 8 帧）。
  skill2  第五呪歌・神環封壁：`Targeting` 敌方英雄（e_range，英雄在身边才开：五面盾别挡小兵）：e_go 拍（第 3 帧，0.24 秒）五面盾升起，e_t 拍里
          每面完全挡下一次伤害（ragnarok.dll：挨打时把这一下的血补回去，挡满 e_n 次盾就没了；平衡模拟里换成 e_sh + e_sh_ap%
          法强的护盾）。
  ult     第十四呪歌・心弦融歌：`Targeting` 敌方英雄（r_range）：r_go 拍以前叩枪齐唱（不受控制），r_go 拍（第 6 帧，0.62 秒）
          再一叩，符文带扫过身边（半径 r_r）所有敌人：r_dmg + r_ap% 法强的魔法伤害，身体听奥丁的、不听自己的——缴械 r_disarm
          拍，r_t 拍里移速 -r_slow%；歌声钻进身体里，越唱越重：之后每 r_gap 拍各一下 r_p1 + r_p1_ap%、r_p2 + r_p2_ap%、
          r_p3 + r_p3_ap% 法强的魔法伤害。

时间按 Codex 的 frames.json（一秒 60 拍）：普攻第 4 帧 0.315 秒出枪、0.381 秒刺中，投枪 0.375 秒离手，开盾 0.24 秒，咒歌 0.14 秒
蓄力、0.62 秒顿地；动作长度普攻 0.79 秒、Q 56 拍、E 60 拍、R 61 拍。

ragnarok.dll（addons/ragnarok/src/odin.rs）：被动 ragnarok_odin:galdr（波命湧出、神環封壁的五面盾、冈格尼尔穿盾、双鸦、配音、
倒地声，参数 NATIVE_KEYS）。经典 SDK 跑不了 DLL：平衡模拟用 --plain（没有波命湧出和穿盾，五面盾换成护盾）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "ragnarok"
ID = "ragnarok_odin"
OUT = os.path.join(REPO, MOD_ID, "champion", f"{ID}.data_champion")
FX = f"asset/{MOD_ID}/effects/{ID}_fx"
PROJ = f"asset/{MOD_ID}/effects/{ID}_proj"

# 单位：近战射程 25000；范围按单位的碰撞半径（约 15000）另算。一秒 60 拍。
# 冈格尼尔的高度：Codex 的离手点在脚底上 29 逻辑格 = 58 / 2.4 = 24.2 个游戏像素，弹道画面在落点（脚底上 11.5）往北
# 5000 - y_offset：y_offset = 5000 - (24.2 - 11.5) x 1000 = -7700
# 数值：经典 SDK 模拟（C:/t/lb_sim，中路 lane 2，600 秒，对手是原版中单，32 个种子），洛基 +2.66、别西卜 +2.46 作对照。
# 2026-11-27 初版（Q 130 + 90%、R 150 + 80%、神環封壁对谁都开）+0.95；Q 170 + 120%、R 200 + 100%、普攻 20 + 30%、神環封壁只在
# 敌方英雄身边开 +3.58 太强；Q 150 + 100%、R 170 + 90% +2.01；Q 160 + 105%、R 180 + 95%（这份 P）+2.72。
P = {
    # 属性（近战法师）
    "hp": 1000, "hp_g": 92, "atk": 78, "atk_g": 9, "apw": 65, "apw_g": 24, "def": 28, "def_g": 5, "mr": 30,
    "mr_g": 4, "ms": 1050, "ms_g": 10,
    "atk_range": 32000, "atk_dur": 36, "atk_cd": 64, "atk_st": 17, "a_dmg": 15, "a_ap": 25,
    # 被动：第十五呪歌・波命湧出（ragnarok.dll）
    "p_hp": 35, "p_heal": 120, "p_ap": 60, "p_t": 120, "p_cd": 5400,
    # 第九呪歌・旋影風牙
    "q_cd": 480, "q_range": 60000, "q_dur": 56, "q_go": 22, "q_speed": 6000, "q_y": -7700, "q_dmg": 160, "q_ap": 105,
    # 第五呪歌・神環封壁
    "e_cd": 900, "e_range": 50000, "e_dur": 60, "e_go": 14, "e_t": 240, "e_n": 5, "e_sh": 250, "e_sh_ap": 50,
    # 第十四呪歌・心弦融歌
    "r_cd": 3000, "r_range": 40000, "r_dur": 61, "r_go": 37, "r_r": 48000, "r_dmg": 180, "r_ap": 95, "r_disarm": 75,
    "r_slow": 30, "r_t": 180, "r_gap": 60, "r_p1": 30, "r_p1_ap": 10, "r_p2": 60, "r_p2_ap": 20, "r_p3": 90,
    "r_p3_ap": 30,
}
# ragnarok.dll 读的那几个（addons/ragnarok/src/odin.rs 的 Params::default() 要和这里一样）
NATIVE_KEYS = ("p_hp", "p_heal", "p_ap", "p_t", "p_cd", "e_t", "e_n")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def n(x):
    return f"{ID}_{x}"


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def flag(name, tick, **fields):
    dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": dur, **fields}, "only_to_enemy": False}


def unflag(name):
    return {"type": "RemoveCasterBuff", "name": n(name)}


def when(name, has, none):
    return {"type": "SwitchByBuff", "buff_name": n(name), "effect_buff": has, "effect_none": none}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def view(name):
    return {"type": "ViewEffect", "name": n(name)}


def sfx(name):
    return {"type": "Sfx", "name": n(name)}


def tsfx(name):
    return {"type": "TargetSfx", "name": n(name)}


def attack(dmg, ratio):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "target_hp_ratio": 0,
            "attack_effect_type": "Target"}


def magic(dmg, ap):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ap, "hp_ratio": 0, "can_crit": False}


def debuff(name, tick, **fields):
    return {"type": "AddBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}, **fields}}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def on_self(*effects):
    """只给奥丁自己（WithSelf 会连目标一起给）。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": 1000}}, "target": "AllyOnlySelf",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def alive_only(*effects):
    """Delayed 里的效果只给活着的奥丁（同 build_lubu.alive_only）：等的时候被打死就什么都不做。"""
    return combine(search_self(flag("live", 1)), when("live", combine(*effects), search_self(*effects)),
                   unflag("live"))


def around(radius, effects):
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": radius}}, "target": "EnemyWithoutTower",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def action(name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{ID}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


def build(p, is_native=False):
    # ------------------------------------------------------------------ 普攻：冈格尼尔刺击（被动波命湧出在 ragnarok.dll）
    attack_a = action("attack", p["atk_dur"], p["atk_cd"], p["atk_st"], p["atk_range"], "Targeting", "Enemy",
                      combine(attack(0, 100), magic(p["a_dmg"], p["a_ap"]), sfx("a"), view("a_hit"), tsfx("a_hit")),
                      atype="BaseAttack", cancel=True)

    # ------------------------------------------------------------------ Q：第九呪歌・旋影風牙（必中的冈格尼尔）
    # q_mark 先挂上，同一拍的伤害里 ragnarok.dll 认出来，把护盾清零再打；同一拍 100% 魔法穿透 = 无视魔抗
    hit = [debuff("q_mark", 2), flag("q_pen", 1, magic_resistance_penetration=100), magic(p["q_dmg"], p["q_ap"]),
           view("q_hit"), tsfx("q_hit")]
    spear = {"type": "TargetProjectile", "name": n("q_spear"), "speed": p["q_speed"], "y_offset": p["q_y"],
             "applied_target": "EnemyChampion",
             "applied_effects": [{"casting_type": "Targeting", "effect": e} for e in hit]}
    skill = action("skill", p["q_dur"], p["q_cd"], 1, p["q_range"], "Targeting", "EnemyChampion",
                   combine(delayed(p["q_go"] - 1, alive_only(sfx("q"), spear))))

    # ------------------------------------------------------------------ E：第五呪歌・神環封壁（五面盾，每面挡一下）
    # 游戏里：e_ward 这个 buff 在的时候 ragnarok.dll 挡伤害、按盾的数量放五面盾的循环；平衡模拟里换成护盾
    if is_native:
        ward = combine(flag("e_ward", p["e_t"]), sfx("e"))
    else:
        ward = combine(on_self({"type": "Shield", "amount": p["e_sh"], "attack_ratio": 0, "ap_ratio": p["e_sh_ap"],
                                "tick": p["e_t"]}), sfx("e"))
    skill2 = action("skill2", p["e_dur"], p["e_cd"], 1, p["e_range"], "Targeting", "EnemyChampion",
                    combine(delayed(p["e_go"] - 1, alive_only(ward))))

    # ------------------------------------------------------------------ R：第十四呪歌・心弦融歌（叩枪齐唱，越唱越重）
    def pulse(k):
        return delayed(k * p["r_gap"] - 1, magic(p[f"r_p{k}"], p[f"r_p{k}_ap"]), view("r_mark"))
    song = around(p["r_r"], [magic(p["r_dmg"], p["r_ap"]), {"type": "BlockAttack", "tick": p["r_disarm"]},
                             debuff("r_slow", p["r_t"], move_speed_mult=-p["r_slow"]), view("r_mark"),
                             pulse(1), pulse(2), pulse(3)])
    ult = action("ult", p["r_dur"], p["r_cd"], 1, p["r_range"], "Targeting", "EnemyChampion",
                 combine(flag("r_guard", p["r_go"], cc_immune=True), sfx("r_chant"),
                         delayed(p["r_go"] - 1, alive_only(sfx("r"), song))))

    # ------------------------------------------------------------------ 画面
    # 出枪的光、咒歌的符文环、顿地的符文场画在他自己的帧里（tools/art/import_odin.py）；命中在目标身上；
    # 五面盾、双鸦、波命湧出是 ragnarok.dll 按状态放的（挂在他身上）；被歌声缠住的敌人身上挂符文环
    E = lambda name, tag, z=2, follow=True: {"type": "Animation", "name": n(name), "anim": FX, "tag": tag, "z": z,
                                             "is_follow": follow}
    views_e = [E("a_hit", "thrust_hit"), E("q_hit", "spear_hit", 3), E("e_ward", "ward", -1),
               E("r_mark", "chant", 2), E("p_ravens", "ravens", -1), E("p_heal", "chant", -1)]
    views_p = [{"type": "Animated", "name": n("q_spear"), "anim": PROJ, "tag": "spear_flight", "repeat": True, "z": 2}]
    kit = {
        "id": ID, "category": "Magician", "tags": ["AP", "Magic", "Melee", "Shield", "CC"],
        "sprite": f"asset/{MOD_ID}/champions/{ID}", "anim_prefix": "",
        "skill_icons": [f"asset/{MOD_ID}/icons/{ID}_skill", f"asset/{MOD_ID}/icons/{ID}_skill2",
                        f"asset/{MOD_ID}/icons/{ID}_ult"],
        "stat": {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
                 "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": 0, "stack": 0, "crit_chance": 0},
        "growth": {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
                   "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0,
                   "crit_chance": 0},
        "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
        "view_projectiles": views_p, "view_effects": views_e, "view_buffs": [],
    }
    if is_native:   # ragnarok.dll（addons/ragnarok/src/odin.rs）：波命湧出、五面盾、冈格尼尔穿盾、双鸦、配音、倒地声
        kit = {"id": ID, "category": kit["category"], "tags": kit["tags"],
               "passive": {"passive_ref": f"{ID}:galdr", "params": {k: p[k] for k in NATIVE_KEYS}},
               **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
    return kit


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--set", nargs="*", default=[], help="一个 --set 后面跟所有 key=value（第二个 --set 会顶掉第一个）")
    ap_.add_argument("--params", help="覆盖参数的 json 文件")
    ap_.add_argument("--out", default=OUT)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：不带 DLL 的被动")
    a = ap_.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k}")
        p[k] = type(p[k])(float(v)) if isinstance(p[k], int) else float(v)
    kit = build(p, not a.plain)
    if a.nodes:
        for s in ("attack", "skill", "skill2", "ult"):
            print(f"{s:7s} {nodes(kit[s]['effect']):4d} nodes")
    text = json.dumps(kit, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    os.makedirs(os.path.dirname(lp(a.out)), exist_ok=True)
    with open(lp(a.out), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(a.out, len(text))


if __name__ == "__main__":
    main()
