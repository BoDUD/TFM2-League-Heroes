"""Build the add-on's copy of Malzahar from the main pack (Void Shift as in League, Malefic Visions jumping on deaths, the
voidlings units of their own).

    python -X utf8 addons/league_malzahar/make_override.py [--check]

Rebuilds Malzahar with tools/kit/build_malzahar.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_malzahar.data_champion byte for byte (so the copy never drifts from the shipped kit), and
writes addons/league_malzahar/override/league_malzahar.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit, minus the data passive (the Granite-Shield ladder) and the vision's data death
    watch (its one jump);
  * passive league_malzahar:void (params: p_cd / p_linger / p_dr for Void Shift, e_t / e_p / e_dmg / e_ap / e_jump for
    the visions it moves) and the native effect league_malzahar:vision on every unit the vision's bolt hits;
  * 0.2.0, the voidlings as units (src/lib.rs; tools/art/unit_malzahar_voidling.py draws their sheet): E's cast takes
    `V_UNIT` off him and lays `V_ASK` (3 ticks) on its target, and the swarm riding with the vision (its bites, its
    pictures, its rift) plays only without `V_UNIT` (the passive spawns the voidlings as units and lays the flag when the
    host gives units). The numbers the units use (V_HIT, V_HIT_AP, W_T, W_P, E_LAG, VOID_ACT, VOID_LANDS) are checked
    against P and the unit sheet's attack frames: change the main pack and this script stops until lib.rs follows;
  * the attack's and the skill's tooltips point to description.league_malzahar_void.* with the add-on's wording (Void
    Shift and the jumps as League has them, the voidlings units), so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Malzahar changes. --check: write nothing, exit
1 when the files on disk are not what this would write.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_malzahar")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_malzahar as kit  # noqa: E402
import setup_malzahar as setup  # noqa: E402

TEXT_ID = "league_malzahar_void"          # the text's key (the hero's own id is league_malzahar)
UNITS = os.path.join(ROOT, "league", "champions")
HERO = "league_malzahar"
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
O, A, C, M, E = setup.O, setup.A, setup.C, setup.M, setup.E
mag = setup.mag
ATTACK = {
    "zh-hans": "射出虚空弹。被动" + O + "虚空穿越" + E + "：受到的伤害减少{p_dr}%并" + C + "免疫控制" + E + "；被非小兵单位打中" + A + "{p_linger}秒" + E +
               "后消失，" + A + "{p_cd}秒" + E + "内未受到英雄伤害时重新获得。",
    "zh-hant": "射出虛空彈。被動" + O + "虛空象限" + E + "：受到的傷害減少{p_dr}%並" + C + "免疫控場" + E + "；被非小兵單位打中" + A + "{p_linger}秒" + E +
               "後消失，" + A + "{p_cd}秒" + E + "內未受到英雄傷害時重新獲得。",
    "en": "Fires a void bolt. Passive " + O + "Void Shift" + E + ": takes {p_dr}% less damage and is " + C + "immune to crowd control" + E +
          "; it fades " + A + "{p_linger}s" + E + " after a non-minion hit and returns after " + A + "{p_cd}s" + E + " without champion damage.",
    "ko": "공허의 화살을 쏩니다. 기본 지속 효과 " + O + "공허 태세" + E + ": 받는 피해 {p_dr}% 감소, " + C + "군중 제어 면역" + E + "; 미니언이 아닌 적에게 맞고 " + A +
          "{p_linger}초" + E + " 뒤 사라지며, " + A + "{p_cd}초" + E + " 동안 챔피언 피해를 받지 않으면 다시 생깁니다.",
    "ja": "ヴォイドの弾を放つ。自動効果" + O + "ヴォイドシフト" + E + "：受けるダメージ{p_dr}%減少、" + C + "行動妨害無効" + E + "；ミニオン以外の攻撃を受けて" + A +
          "{p_linger}秒" + E + "後に消え、" + A + "{p_cd}秒" + E + "チャンピオンのダメージを受けないと再び得る。",
}
SKILL = {
    "zh-hans": O + "煞星幻象" + E + "：" + A + "{e_t}秒" + E + "内造成" + mag("e") + M + "魔法伤害" + E + "，目标死亡时立刻跳到最近的敌人身上（优先英雄），可以一直跳。" + O +
               "虚空虫群" + E + "：目标两边钻出{v_n}只虚空蜂，自己追咬敌人" + A + "{v_t}秒" + E + "（每口" + mag("w") + "，可被击杀）。",
    "zh-hant": O + "煞星幻象" + E + "：" + A + "{e_t}秒" + E + "內造成" + mag("e") + M + "魔法傷害" + E + "，目標死亡時立刻跳到最近的敵人身上（優先英雄），可以一直跳。" + O +
               "召喚虛靈" + E + "：目標兩邊鑽出{v_n}隻虛靈，自己追咬敵人" + A + "{v_t}秒" + E + "（每口" + mag("w") + "，可被擊殺）。",
    "en": O + "Malefic Visions" + E + ": deals " + mag("e") + " " + M + "magic damage" + E + " over " + A + "{e_t}s" + E +
          "; whenever the target dies, the vision jumps at once to the nearest enemy, champions first. " + O + "Void Swarm" + E + ": {v_n} voidlings "
          "come out beside the target and hunt on their own for " + A + "{v_t}s" + E + " (" + mag("w") + " a bite; they can be killed).",
    "ko": O + "재앙의 환상" + E + ": " + A + "{e_t}초" + E + "에 걸쳐 " + mag("e") + " " + M + "마법 피해" + E + ", 대상이 죽을 때마다 가장 가까운 적(챔피언 우선)에게 바로 옮겨갑니다. " +
          O + "공허의 무리" + E + ": 대상 양옆에 공허충 {v_n}마리가 나와 " + A + "{v_t}초" + E + " 동안 스스로 적을 물어뜯음(한 번에 " + mag("w") + ", 처치 가능).",
    "ja": O + "虚性侵蝕" + E + "：" + A + "{e_t}秒" + E + "かけて" + mag("e") + "の" + M + "魔法ダメージ" + E + "、対象が倒れるたびに最も近い敵（チャンピオン優先）へすぐ移る。" + O +
          "ヴォイドスワーム" + E + "：対象の両脇にヴォイドリング{v_n}体が現れ" + A + "{v_t}秒" + E + "自ら噛みつく（1回" + mag("w") + "、倒せる）。",
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def consts(src):
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers, floats written `30_000.0`, strings."""
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|u64|f64|&str) = ([^;]+);", src):
        value = value.strip()
        out[name] = value.strip('"') if kind == "&str" else int(float(value.replace("_", "")))
    return out


def walk(o):
    """every dict of a tree"""
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def replace(o, match, make, count):
    """the tree with every dict `match` takes replaced by `make` of it (counted in `count`)"""
    if isinstance(o, dict):
        if match(o):
            count.append(o)
            return make(o)
        return {k: replace(v, match, make, count) for k, v in o.items()}
    if isinstance(o, list):
        return [replace(v, match, make, count) for v in o]
    return o


def attack_ticks(name):
    """a unit sheet's attack: (ticks long, the tick its third frame starts - the bite)"""
    with open(lp(os.path.join(UNITS, name + "#anim.fanim")), encoding="utf-8-sig") as f:
        frames = json.load(f)["anims"]["attack"]["frames"]
    secs = [fr.get("duration", fr["data"].get("duration")) for fr in frames]
    return round(sum(secs) * 60), round(sum(secs[:2]) * 60)


def units(champion, p, c):
    """0.2.0: E asks for its voidlings as units; the swarm riding with the vision plays only without V_UNIT. The natives'
    numbers (c: src/lib.rs) checked against P and the unit sheet."""
    want = {"W_T": p["w_t"], "W_P": p["w_p"], "V_HIT": p["w_dmg"], "V_HIT_AP": p["w_ap"], "E_LAG": p["e_lag"]}
    want["VOID_ACT"], want["VOID_LANDS"] = attack_ticks(c["VOIDLING"])
    wrong = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"the voidlings' numbers differ from src/lib.rs (lib, kit or sheet): {wrong}")
    if c["VOID_COOL"] != 2 * p["w_p"] or c["V_N"] != 2:
        sys.exit("two voidlings bite as often as the riding swarm (VOID_COOL = 2 x w_p): update src/lib.rs")
    views = {v["name"] for v in champion["view_effects"]}
    if c["W_SPAWN_VIEW"] not in views or not re.search(
            r'"type": "(Target)?Sfx", "name": "' + re.escape(c["W_SPAWN_VIEW"]) + '"', json.dumps(champion)):
        sys.exit(f"src/lib.rs's W_SPAWN_VIEW = {c['W_SPAWN_VIEW']} is no view effect or sound of the main pack's Malzahar")
    names = {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    names |= {x.get("name") for x in walk(champion) if x.get("type") == "RemoveCasterBuff"}
    names |= {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    if any(c[k] in names for k in ("V_ASK", "V_UNIT")) or any(str(b).startswith(c["V_UID"]) for b in names):
        sys.exit("the main pack's Malzahar already uses one of the add-on's buff names: update src/lib.rs")
    # E's cast: the flag off, the ask on its target
    skill = champion["skill"]
    skill["effect"] = dict(skill["effect"], effects=[
        {"type": "RemoveCasterBuff", "name": c["V_UNIT"]},
        {"type": "AddBuff", "buff_state": {"name": c["V_ASK"], "duration": {"Time": {"tick": 3}}}}] + skill["effect"]["effects"])

    # the swarm riding with the vision (its bites, its picture, its rift and sound): only without V_UNIT
    def swarm(x):
        s = json.dumps(x)
        return (x.get("type") == "AddCasted" and x.get("duration") == p["w_t"] and
                ("league_malzahar_w_bite" in s or "league_malzahar_w_swarm" in s)) or \
            (x.get("type") in ("ViewEffect", "TargetSfx") and x.get("name") == c["W_SPAWN_VIEW"])

    def bolt(o):
        effs = o["applied_effects"]
        inner = effs[0]["effect"] if len(effs) == 1 else {}
        parts = inner.get("effects", [])
        riding = [x for x in parts if swarm(x)]
        if inner.get("type") != "Combine" or len(riding) != 4:
            sys.exit("the swarm riding with the vision (league_malzahar_e_bolt) changed in the main pack: update this script")
        at = parts.index(riding[0])
        sw = {"type": "SwitchByBuff", "buff_name": c["V_UNIT"], "effect_buff": {"type": "Combine", "effects": []},
              "effect_none": {"type": "Combine", "effects": riding}}
        kept = [x for x in parts if not swarm(x)]
        return dict(o, applied_effects=[dict(effs[0], effect=dict(inner, effects=kept[:at] + [sw] + kept[at:]))])
    found = []
    champion["skill"] = replace(skill, lambda o: o.get("type") == "TargetProjectile" and o.get("name") == "league_malzahar_e_bolt",
                                bolt, found)
    if len(found) != 2:
        sys.exit(f"E throws its vision {len(found)} times, not twice (with and without Q's combo): update this script")
    return champion


def main():
    check = "--check" in sys.argv[1:]
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_malzahar differs from build_malzahar.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    s = json.dumps(champion)
    if (champion.get("passive", {}).get("passive_ref") != "league_malzahar:void" or "league_malzahar:vision" not in s
            or "league_malzahar_e_watch" in s or "league_malzahar_p_init" in s):
        sys.exit("the copy does not call the add-on: update this script")
    c = consts(open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read())
    champion = units(champion, p, c)
    champion["attack"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.attack"
    champion["skill"]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.skill"

    values = setup.values(p)
    values.update({"p_dr": p["p_dr"], "p_linger": setup.secs(p["p_linger"]), "v_n": c["V_N"], "v_t": setup.secs(c["VOID_LIFE"])})
    texts = {lang: {"attack": (LEAD[lang] + ATTACK[lang]).format(**values),
                    "skill": (LEAD[lang] + SKILL[lang]).format(**values)} for lang in ATTACK}
    long = {f"{lang}.{k}": setup.shown_length(d[k]) for lang, d in texts.items() for k in d
            if setup.shown_length(d[k]) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    i18n = {lang: {"description": {TEXT_ID: d}} for lang, d in texts.items()}
    tpath = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: dumps_main(champion), tpath: dumps_main(i18n)}
    if check:
        stale = [os.path.relpath(path, ROOT) for path, text in files.items()
                 if not os.path.isfile(lp(path)) or open(lp(path), encoding="utf-8", newline="").read() != text]
        if stale:
            sys.exit("not as make_override.py writes them: %s" % stale)
        print("ok")
        return
    for path, text in files.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(path)


if __name__ == "__main__":
    main()
