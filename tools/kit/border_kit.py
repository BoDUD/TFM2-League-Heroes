"""边境巡团三个英雄的 build_<hero>.py 共用的小件：效果、动作、命令行。一个英雄一个 Kit（他的 id 和特效图）。

写法照终末包（tools/kit/build_raiden.py 那几个函数），区别只是 id 从 Kit 里来。一秒 60 拍；距离单位和游戏一样（近战
普攻约 25000，英雄碰撞半径约 10000）。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "border"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def combine(*effects):
    return {"type": "Combine", "effects": [e for e in effects if e is not None]}


def delayed(tick, *effects):
    return {"type": "Delayed", "tick": tick, "effects": [e for e in effects if e is not None]}


def anim(name, tick):
    return {"type": "CasterAnimation", "name": name, "tick": tick}


def attack(dmg, ratio, hp=0, target_hp=0):
    return {"type": "Attack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": hp, "target_hp_ratio": target_hp,
            "attack_effect_type": "Target"}


def ap_attack(dmg, ratio):
    return {"type": "ApAttack", "damage": dmg, "attack_ratio": ratio, "hp_ratio": 0, "can_crit": False}


def stun(tick):
    return {"type": "Stun", "duration": tick}


def knockback(speed, tick):
    return {"type": "Knockback", "speed": speed, "tick": tick}


def search_self(*effects):
    return {"type": "RandomTarget", "range": 1, "casting_target": "AllyOnlySelf", "from_projectile": False,
            "effects": [e for e in effects if e is not None]}


def on_self(*effects):
    """只给他自己（RangeEffect 圈 1000 的 AllyOnlySelf：WithSelf 会连目标一起给，champion-data 第 4 节）。"""
    return {"type": "RangeEffect", "shape": {"Circle": {"radius": 1000}}, "target": "AllyOnlySelf",
            "apply_type": "AroundCaster", "effects": [e for e in effects if e is not None]}


def native(ref):
    return {"type": "Native", "effect_ref": ref}


def action(hid, name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
    return {"action_name": name, "description": f"#asset/base/text/champion?description.{hid}.{name}",
            "duration": dur, "cooltime": cd, "start_timing": st, "cancelable": cancel, "range": rng,
            "casting_type": ctype, "casting_target": ctarget, "attack_type": atype, "effect": effect}


class Kit:
    """一个英雄的名字空间：buff、特效、声音都叫 <id>_<x>。"""

    def __init__(self, hid):
        self.id = hid
        self.fx = f"asset/{MOD_ID}/effects/{hid}_fx"
        self.proj = f"asset/{MOD_ID}/effects/{hid}_proj"

    def n(self, x):
        return f"{self.id}_{x}"

    def flag(self, name, tick, **fields):
        dur = "Permanent" if tick is None else {"Time": {"tick": tick}}
        return {"type": "AddCasterBuff", "buff_state": {"name": self.n(name), "duration": dur, **fields},
                "only_to_enemy": False}

    def unflag(self, name):
        return {"type": "RemoveCasterBuff", "name": self.n(name)}

    def when(self, name, has, none):
        return {"type": "SwitchByBuff", "buff_name": self.n(name), "effect_buff": has, "effect_none": none}

    def buff(self, name, tick, **fields):
        """给目标的 buff。"""
        return {"type": "AddBuff", "buff_state": {"name": self.n(name), "duration": {"Time": {"tick": tick}}, **fields}}

    def slow(self, name, pct, tick):
        return self.buff(name, tick, move_speed_mult=-pct)

    def view(self, name):
        return {"type": "ViewEffect", "name": self.n(name)}

    def lob(self, name, *end, travel=1):
        """数据版的「目标脚下」：一个看不见的抛物弹，travel 拍后落在出手那一刻目标站的地方，end 在落点上放。
        RangeProjectile 直接写在招式里是生成在施法者脚下的（引擎的范围只有 AroundCaster 和 Forward），
        所以圈要放在目标那里就得这样丢过去（league_zyra、league_brand 的 lob）。不用登记画面。"""
        return {"type": "ParabolicProjectile", "name": self.n(name), "travel_time": travel, "range": 400000,
                "range_effect_name": "", "shape": {"Circle": {"radius": 1}}, "applied_target": "EnemyWithoutTower",
                "applied_effects": [], "end_effects": list(end)}

    def sfx(self, name):
        """自己的声音（<id>_<name>，有 .sound_info）。"""
        return {"type": "Sfx", "name": self.n(name)}

    def native(self, name):
        return native(f"{self.id}:{name}")

    def alive_only(self, *effects):
        """Delayed 里的效果只给活着的他（同 build_raiden.alive_only）：等的时候被打死就什么都不做。"""
        return combine(search_self(self.flag("live", 1)), self.when("live", combine(*effects), search_self(*effects)),
                       self.unflag("live"))

    def action(self, name, dur, cd, st, rng, ctype, ctarget, effect, atype="Skill", cancel=False):
        return action(self.id, name, dur, cd, st, rng, ctype, ctarget, effect, atype, cancel)

    def views(self, names, follow=True, z=2):
        """view_effects：每个 (名字, 特效图的标签)。"""
        return [{"type": "Animation", "name": self.n(name), "anim": self.fx, "tag": tag, "z": z, "is_follow": follow}
                for name, tag in names]

    def projectile_views(self, names, once=()):
        """view_projectiles：飞出去的东西（画面跟着弹道转，类型是 Animated，champion-data 第 6 节）。`once` 里的只放一遍
        （斩线、盐带：帧时就是它活多久），别的循环。"""
        return [{"type": "Animated", "name": self.n(name), "anim": self.proj, "tag": tag, "repeat": name not in once,
                 "z": 2} for name, tag in names]

    def shell(self, category, tags, stat, growth, attack_a, skill, skill2, ult, views_e, views_p=(), passive=None,
              params=None):
        kit = {"id": self.id, "category": category, "tags": tags,
               "sprite": f"asset/{MOD_ID}/champions/{self.id}", "anim_prefix": "",
               "skill_icons": [f"asset/{MOD_ID}/icons/{self.id}_skill", f"asset/{MOD_ID}/icons/{self.id}_skill2",
                               f"asset/{MOD_ID}/icons/{self.id}_ult"],
               "stat": stat, "growth": growth,
               "attack": attack_a, "skill": skill, "skill2": skill2, "ult": ult,
               "view_projectiles": list(views_p), "view_effects": list(views_e), "view_buffs": []}
        if passive:
            kit = {"id": self.id, "category": category, "tags": tags,
                   "passive": {"passive_ref": f"{self.id}:{passive}", "params": params or {}},
                   **{k: v for k, v in kit.items() if k not in ("id", "category", "tags")}}
        return kit


def stats(p, regen=0):
    stat = {"attack": p["atk"], "magic_power": p["apw"], "hp": p["hp"], "defence": p["def"],
            "magic_resistance": p["mr"], "move_speed": p["ms"], "hp_regen": regen, "stack": 0, "crit_chance": 0}
    growth = {"attack": p["atk_g"], "magic_power": p["apw_g"], "hp": p["hp_g"], "defence": p["def_g"],
              "magic_resistance": p["mr_g"], "move_speed": p["ms_g"], "hp_regen": 0, "stack": 0, "crit_chance": 0}
    return stat, growth


def nodes(o):
    if isinstance(o, dict):
        return (1 if "type" in o else 0) + sum(nodes(v) for v in o.values())
    if isinstance(o, list):
        return sum(nodes(v) for v in o)
    return 0


def main(P, build, out, doc):
    """命令行：--set key=value ... 改参数，--plain 出给平衡模拟用的纯数据版（没有 border.dll）。"""
    ap_ = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap_.add_argument("--set", nargs="*", default=[], help="一个 --set 后面跟所有 key=value（第二个 --set 会顶掉第一个）")
    ap_.add_argument("--params", help="覆盖参数的 json 文件")
    ap_.add_argument("--out", default=out)
    ap_.add_argument("--nodes", action="store_true")
    ap_.add_argument("--plain", action="store_true", help="给平衡模拟用：border.dll 的部分换成数据近似，分类 Tank 写 Melee")
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
