"""边境巡团包（mod_id border，border/）共用的文件和三个英雄的 setup_<hero>.py 用的工具（setup_cenlei.py 等）。

包自己的 mod.mod_info（VERSION、点了 HEROES 每个人名的介绍、contains_code / mod_type native 给 border.dll、键排好序）
和 mod.override_info 里文字、champion_view 的合并都在这里。每个英雄的 setup 只写自己的键（write_hero）：text/champion.i18n
里他的文字、sound/sfx/<id>_*.sound_info（一个声音两条覆盖：事件 -> 我们的 .sound_info，片段 -> 我们的音频）、
champion_view 里他那一条。JSON 照游戏的写法：缩进 2、CRLF、UTF-8。事件名不和片段同名：事件 <id>_<x> 放片段
<id>_vo_<...>。

和终末包（tools/kit/ragnarok_pack.py）不一样的地方：Codex 这批只交了普通话配音，没有技能音效，技能的音效借原版的
（BASE_SFX 里的名字，数据直接写原版的声音名，不用 .sound_info）。配音是 Codex 合成的试音，不是谁的录音，可以进仓库。
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "border"
MOD = os.path.join(REPO, MOD_ID)
VERSION = "0.1.0"
NAME = "Border Patrol: Mirror Sea"
HEROES = ["Cen Lei", "Xiao Lun", "Deng Mi", "Zhu Mo", "Fu Suo", "Yan Xi", "Yin Du", "Lan Ti", "Lu Xin", "Ji Yan",
          "Zhong Li", "Wu Ling"]
DESC = ("Border Patrol, the Mirror Sea chapter: twelve original heroes for Teamfight Manager 2 - {heroes}. "
        "Cen Lei takes the blows meant for a threatened ally and lets the stored Back Pressure out in one fan of waves; "
        "Xiao Lun winds her crossbow string as she runs and looses a Full Arc that picks a new target for every arrow; "
        "Deng Mi gathers light from the spells her friends take and hands out shield lamps and healing pulses; Zhu Mo "
        "heats up with every blow and opens his furnace to choose between guarding and smashing; Fu Suo counts the "
        "steps of whoever strays from their team and cuts an off-beat line a quick step can dodge; Yan Xi lays salt "
        "bands that crystallize whoever stays on them and pulls them back like an ebbing tide; Yin Du rams the first "
        "foe in his way and closes two tide walls on his beacon; Lan Ti marks the last caster who hurt her, catches the "
        "next spell in her guard and answers with an echo of what she blocked; Lu Xin follows the feather trails of "
        "the fleeing and reels them in with two cuts; Ji Yan charts coordinates that her star beam sets off and drops "
        "three warned stars along her aim; Zhong Li speeds up while he stands his ground and fires a four-shot chorus "
        "that stops if he is moved; Wu Ling rings bells on whoever touches her curtains and closes them on a crowd. "
        "Rules the data cannot play live in the pack's own code (border.dll), which also draws the heroes' sharper "
        "frames, with or without the League of Legends Heroes, Teamfight Tactics Heroes and Record of Ragnarok packs; "
        "Sylas, Viego, Neeko, Illaoi and Yuumi of the League pack work with them. Pixel art, effects, icons, "
        "illustrations and Mandarin trial voices made for this pack.")

# 游戏的说明框（lint_mod 的 TOOLTIP_MAX，和终末包一样）
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
HPi = "<i#asset/base/ui/banpick/champion_stat_icon:hp_0>"
O = "<#ff9028ff>"      # 名字、物理伤害
A = "<#ffb900ff>"      # 时长、数量
R = "<#ef5350ff>"      # 控制
M = "<#a974ffff>"      # 法术伤害、法强
S = "<#e8d44dff>"      # 护盾
G = "<#7ee08aff>"      # 治疗、移速
E = "<>"

# 借原版的技能音效（python .claude/skills/tfm2-hero-mod/scripts/bundle_tool.py sfx 列得出来的名字）：数据直接放，
# 不写 .sound_info，write_hero 不当成漏了的声音
BASE_SFX = {
    "shield_bearer_attack", "shield_bearer_skill2", "shield_bearer_ult", "knight_skill", "knight_skill2",
    "knight_ult", "fighter_skill_hit", "crossbowman_attack", "crossbowman_skill1", "crossbowman_skill2_hit",
    "crossbowman_ult", "crossbowman_ult_hit", "archer_attack", "gunner_skill2_on", "enchanter_attack",
    "enchanter_ult", "priest_skill", "priest_skill2", "priest_ult", "white_mage_skill", "bard_skill1",
    "spirit_caller_ult_shield", "monk_ult", "white_mage_ult_hit", "hammerer_attack", "hammerer_skill",
    "hammerer_skill2", "siege_breaker_ult", "dual_blader_attack", "ninja_skill2_dash", "hitman_skill2",
    "inquisitor_skill1_pre", "dual_blader_ult", "ice_mage_attack", "ice_mage_skill", "ice_mage_skill2", "ice_mage_ult",
    "knight_attack", "cavalry_knight_skill1", "gladiator_attack", "gladiator_attack_hit", "magic_knight_skill2",
    "gladiator_ult_hit", "ninja_attack", "whip_master_skill1", "ninja_ult_attack", "astrologer_attack",
    "astrologer_skill1_impact", "astrologer_skill2", "astrologer_ult_burst", "gunner_attack", "gunner_skill2",
    "gunner_ult", "bard_attack", "bard_skill1", "bard_skill2",
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path, default=None):
    if default is not None and not os.path.isfile(lp(path)):
        return default
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    os.makedirs(os.path.dirname(lp(path)), exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def kit_sounds(hid):
    """一个英雄的数据放的每个 Sfx / TargetSfx 名字（借原版的不算）。"""
    found = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") in ("Sfx", "TargetSfx") and o["name"] not in BASE_SFX:
                found.add(o["name"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(load(os.path.join(MOD, "champion", f"{hid}.data_champion")))
    return found


def dll_sounds(hid, module):
    """border.dll 给这个英雄放的声音：addons/border/src/<module>.rs 里 `vo("...")`，加上 common.rs 的配音（Cue::line 的
    "v_..."，六个人共用一套）。play_sfx 直接放的原版声音不算。"""
    src = open(lp(os.path.join(REPO, "addons", "border", "src", f"{module}.rs")), encoding="utf-8").read()
    common = open(lp(os.path.join(REPO, "addons", "border", "src", "common.rs")), encoding="utf-8").read()
    names = {f"{hid}_{x}" for x in re.findall(r'play_sfx\(&vo\("(\w+)"\)', src)}
    names |= {f"{hid}_{x}" for x in re.findall(r'"(v_\w+)"', src + common)}
    return names


def check_lengths(text):
    """每段说明显示出来多长，和 TOOLTIP_MAX 比；有超的返回 True。"""
    bad = False
    for lang, t in text.items():
        lens = {k: shown_length(t[k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(n > TOOLTIP_MAX[lang] for n in lens.values())
        print(lang, " ".join(f"{k}:{n}/{TOOLTIP_MAX[lang]}" for k, n in lens.items()))
    return bad


def write_hero(hid, tx, sounds, view, module, seed):
    """一个英雄在包里共用文件中的键：tx {语言: (description, skill_name)}，sounds {事件: [(片段, 音量, 延迟)]}（必须正好是
    数据和 DLL 放的全部自己的声音），view（champion_view 的一条）。"""
    played = kit_sounds(hid) | dll_sounds(hid, module)
    if played != set(sounds):
        sys.exit(f"the kit or the DLL plays {sorted(played - set(sounds))} without a sound_info, SOUNDS has unused "
                 f"{sorted(set(sounds) - played)}")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"), {})
    for lang, (d, names) in tx.items():
        i18n.setdefault(lang, {}).setdefault("description", {})[hid] = d
        i18n[lang].setdefault("skill_name", {})[hid] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    clips = set()
    for name, plays in sounds.items():
        for c, _, _ in plays:
            if c == name:
                sys.exit(f"{name}: plays a clip of its own name")
            if not any(os.path.isfile(lp(os.path.join(MOD, "sound", "sfx", c + ext))) for ext in (".mp3", ".wav")):
                print(f"warning: {c}.mp3 missing - run {seed}")
            clips.add(c)
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"), {})
    ov.setdefault("asset/base/text/champion", {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"})
    ov.setdefault("asset/base/style/champion_view",
                  {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"})
    for k in [k for k in ov if k.startswith(f"asset/base/sound/sfx/{hid}_")]:   # 这个英雄的声音键重写
        del ov[k]
    for name in list(sounds) + sorted(clips):
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{name}", "type": "override"}
    # 声音的键排好序：谁的 setup 最后跑，文件都一样
    snd = sorted(k for k in ov if k.startswith("asset/base/sound/sfx/"))
    ov = {**{k: v for k, v in ov.items() if not k.startswith("asset/base/sound/sfx/")}, **{k: ov[k] for k in snd}}
    save(os.path.join(MOD, "mod.override_info"), ov)

    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"), {"entries": {}})
    cv["entries"][hid] = json.loads(json.dumps(view))
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)
    return len(sounds), len(clips)


def write_mod_info():
    mi = load(os.path.join(MOD, "mod.mod_info"), {})
    if tuple(int(x) for x in mi.get("version", "0.0.0").split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    mi.update({"author": "BoDUD", "dependencies": [{"mod_id": "base", "version": ">=0.4.11"}], "mod_id": MOD_ID,
               "name": NAME, "description": DESC.format(heroes=", ".join(HEROES)), "contains_code": True,
               "mod_type": "native", "last_updated": "2026-11-22"})
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
