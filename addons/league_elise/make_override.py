"""Build the add-on's copy of Elise from the main pack (the Cocoon, Rappel and the hunt cast on the AI hook's target; the
whole-body spider needs nothing in the data).

    python addons/league_elise/make_override.py [--check]

Rebuilds Elise with tools/kit/build_elise.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_elise.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_elise/override/league_elise.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit plus passive league_elise:queen (params: the Cocoon's range and half width, Rappel's
    and the ult's reach - src/lib.rs Params::default must be the same, its test reads this copy);
  * skill2 and the ult cast on a target (`Targeting`): the Cocoon's aim lock, Rappel's drop and the hunt go at the cast's
    target - the one the add-on's AI hook picks - instead of a random champion in reach;
  * 0.2.0, the spiderlings as units (src/lib.rs; tools/art/unit_elise_spiderling.py draws their sheet): the spiderlings'
    riding bites on her spider attack's target play only without `SL_UNIT` (the passive spawns her stored spiderlings
    as units in Spider Form and keeps the flag on her while any is out, when the host gives units). The numbers the
    units use (SL_HIT, SL_HIT_AP, SL_COOL, SL_FZ, SL_ACT, SL_LANDS, the flags' names) are checked against P and the unit
    sheet's attack frames: change the main pack and this script stops until lib.rs follows;
  * 0.2.1, Neurotoxin by the target's current health and Venomous Bite by its missing health (League's, magic): the main
    pack's q_hp / cq_hp % of the maximum health as true damage (FixedAttack target_hp_ratio) goes from the bolt's hit,
    the bite's landing and the hunt's bite; a Native league_elise:neuro / :bite comes first in the same hit (src/lib.rs
    Q_CUR, CQ_MISS, QM_DMG, QM_AP; the tooltip reads them from there);
  * the attack's, skill's, skill2's and the ult's tooltips point to description.league_elise_queen.* with the add-on's
    wording, so the tooltips in game show whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Elise changes. --check: write nothing, exit 1
when the files on disk are not what this would write.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_elise")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_elise as kit  # noqa: E402
import setup_elise as setup  # noqa: E402

TEXT_ID = "league_elise_queen"      # the text's key (the hero's own id is league_elise)
HERO = "league_elise"
UNITS = os.path.join(ROOT, "league", "champions")
SLOTS = ("attack", "skill", "skill2", "ult")
# lang -> slot -> [(old text the main pack has, new text)] ; the lead marks the add-on's copy
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[애드온] ", "ja": "【アドオン】"}
A, M, E, HP, mag = setup.A, setup.M, setup.E, setup.HP, setup.mag
SWAP = {
    "zh-hans": {"attack": [("每只小蜘蛛撕咬", "变蜘蛛时小蜘蛛爬出来自己咬人（可被击杀），每口")],
                "skill": [("和" + HP("q") + "最大生命真实伤害。", "和目标当前生命" + A + "{q_cur}%" + E + "的" + M + "魔法伤害" + E + "。"),
                          ("和" + HP("cq") + "最大生命真实伤害。", "和目标已损生命" + A + "{cq_miss}%" + E + "的" + M + "魔法伤害" + E +
                           "；按生命算的部分对野怪最多" + mag("qm") + "。")],
                "skill2": [("人形：吐茧", "人形：向线上没被挡的英雄吐茧"), ("落到英雄身上", "落到血最少的英雄身上")],
                "ult": [("向英雄吐茧", "向被控住或血最少的英雄吐茧")]},
    "zh-hant": {"attack": [("每隻小蜘蛛撕咬", "變蜘蛛時小蜘蛛爬出來自己咬人（可被擊殺），每口")],
                "skill": [("和" + HP("q") + "最大生命真實傷害。", "和目標當前生命" + A + "{q_cur}%" + E + "的" + M + "魔法傷害" + E + "。"),
                          ("和" + HP("cq") + "最大生命真實傷害。", "和目標已損生命" + A + "{cq_miss}%" + E + "的" + M + "魔法傷害" + E +
                           "；按生命算的部分對野怪最多" + mag("qm") + "。")],
                "skill2": [("人形：吐繭", "人形：向線上沒被擋的英雄吐繭"), ("落到英雄身上", "落到血最少的英雄身上")],
                "ult": [("向英雄吐繭", "向被控住或血最少的英雄吐繭")]},
    "en": {"attack": [("each spiderling bites for", "in spider form they come out and bite on their own (killable), each")],
           "skill": [(" and " + HP("q") + " max health true damage. ",
                      " and " + A + "{q_cur}%" + E + " of the target's current health as " + M + "magic damage" + E + ". "),
                     (" and " + HP("cq") + " max health true damage.",
                      " and " + A + "{cq_miss}%" + E + " of its missing health as " + M + "magic damage" + E +
                      " (the health part at most " + mag("qm") + " on monsters).")],
           "skill2": [("Human: a cocoon", "Human: a cocoon at a champion with a clear line"),
                      ("drops on a champion", "drops on the lowest champion")],
           "ult": [("Spits a cocoon at a champion,", "Spits a cocoon at the held or lowest champion,")]},
    "ko": {"attack": [("새끼 거미마다", "거미 형태에서 새끼 거미가 나와 스스로 물어뜯음(처치 가능), 한 번에")],
           "skill": [("와 최대 체력 " + HP("q") + " 고정 피해. ", "와 대상 현재 체력 " + A + "{q_cur}%" + E + "의 " + M + "마법 피해" + E + ". "),
                     ("와 최대 체력 " + HP("cq") + " 고정 피해.", "와 잃은 체력 " + A + "{cq_miss}%" + E + "의 " + M + "마법 피해" + E +
                      "(체력 비례 부분은 몬스터에게 최대 " + mag("qm") + ").")],
           "skill2": [("인간: 고치로 ", "인간: 막히지 않은 챔피언에게 고치로 "), ("챔피언에게 내려옴", "체력이 가장 낮은 챔피언에게 내려옴")],
           "ult": [("챔피언에게 고치를 뱉고", "기절했거나 체력이 가장 낮은 챔피언에게 고치를 뱉고")]},
    "ja": {"attack": [("子蜘蛛ごとに", "蜘蛛形態で子蜘蛛が出て自ら噛みつく（倒せる）、1回")],
           "skill": [("と最大体力" + HP("q") + "の確定ダメージ。", "と対象の現在体力" + A + "{q_cur}%" + E + "の" + M + "魔法ダメージ" + E + "。"),
                     ("と最大体力" + HP("cq") + "の確定ダメージ。", "と失った体力" + A + "{cq_miss}%" + E + "の" + M + "魔法ダメージ" + E +
                      "（体力割合分はモンスターに最大" + mag("qm") + "）。")],
           "skill2": [("人間：繭で", "人間：遮られないチャンピオンへ繭で"), ("チャンピオンへ降下", "体力の最も低いチャンピオンへ降下")],
           "ult": [("チャンピオンへ繭を吐き", "拘束中か体力の最も低いチャンピオンへ繭を吐き")]},
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def consts(src):
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers, floats written `9_000.0`, strings, string arrays."""
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|u64|f64|&str|\[&str; \d+\]) = ([^;]+);", src):
        value = value.strip()
        if kind == "&str":
            out[name] = value.strip('"')
        elif kind.startswith("["):
            out[name] = re.findall(r'"([^"]+)"', value)
        else:
            out[name] = int(float(value.replace("_", "")))
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
    """0.2.0: the spiderlings' riding bites play only without SL_UNIT. The natives' numbers (c: src/lib.rs) checked
    against P and the unit sheet."""
    want = {"SL_HIT": p["sl_dmg"], "SL_HIT_AP": p["sl_ap"], "SL_COOL": p["atk_cd"], "SL_FZ": p["sl_fz"]}
    want["SL_ACT"], want["SL_LANDS"] = attack_ticks(c["SPIDERLING"])
    wrong = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"the spiderlings' numbers differ from src/lib.rs (lib, kit or sheet): {wrong}")
    if c["SL_FLAGS"] != [f"{HERO}_sl{k}" for k in (1, 2, 3)] or c["CW_ON"] != f"{HERO}_cw_on":
        sys.exit("src/lib.rs's SL_FLAGS / CW_ON are not the main pack's spiderling and frenzy flags: update it")
    text = json.dumps(champion)
    for flag in c["SL_FLAGS"] + [c["CW_ON"]]:
        if f'"{flag}"' not in text:
            sys.exit(f"the main pack's Elise no longer has the flag {flag}: update src/lib.rs")
    names = {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    names |= {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    if any(c[k] in names for k in ("SL_UNIT", "SL_FRENZY")) or any(str(b).startswith(c["SL_UID"]) for b in names):
        sys.exit("the main pack's Elise already uses one of the add-on's buff names: update src/lib.rs")
    # the spiderlings' bites on her spider attack's target (sw sl3 / sl2 / sl1): only without SL_UNIT
    found = []
    champion["attack"] = replace(
        champion["attack"],
        lambda o: o.get("type") == "SwitchByBuff" and o.get("buff_name") == c["SL_FLAGS"][2]
        and f"{HERO}_sl_bite3" in json.dumps(o.get("effect_buff")),
        lambda o: {"type": "SwitchByBuff", "buff_name": c["SL_UNIT"], "effect_buff": {"type": "Combine", "effects": []},
                   "effect_none": o}, found)
    if len(found) != 1:
        sys.exit(f"the spiderlings' bites are {len(found)} times in the attack, not once: update this script")
    return champion


def venom(champion, p):
    """0.2.1: Neurotoxin's and Venomous Bite's health share as the add-on's natives (League: % of the target's current /
    missing health, magic). The main pack deals q_hp / cq_hp % of the maximum health as true damage (FixedAttack
    target_hp_ratio; data reads no current health) in the bolt's hit, the bite's landing and the hunt's bite: each goes,
    and a Native league_elise:neuro / :bite comes first in the same hit (it reads the target's health before the flat
    magic part lands, as League deals the two as one)."""
    if p["q_hp"] == p["cq_hp"]:
        sys.exit("q_hp and cq_hp are the same: the two shares cannot be told apart - update this script")

    def share(o, pct):
        return (isinstance(o, dict) and o.get("type") == "FixedAttack" and o.get("target_hp_ratio") == pct
                and o.get("damage") == 0 and o.get("attack_ratio") == 0 and o.get("hp_ratio") == 0)

    found = {"neuro": 0, "bite": 0}

    def fix(o):
        if isinstance(o, dict):
            return {k: fix(v) for k, v in o.items()}
        if not isinstance(o, list):
            return o
        items = [fix(v) for v in o]
        for ref, pct in (("neuro", p["q_hp"]), ("bite", p["cq_hp"])):
            for i, e in enumerate(items):
                wrapped = isinstance(e, dict) and set(e) == {"casting_type", "effect"}
                if share(e["effect"] if wrapped else e, pct):
                    native = {"type": "Native", "effect_ref": f"{HERO}:{ref}"}
                    items.pop(i)
                    items.insert(0, {"casting_type": e["casting_type"], "effect": native} if wrapped else native)
                    found[ref] += 1
                    break
        return items

    for slot in ("skill", "ult"):
        champion[slot] = fix(champion[slot])
    if found != {"neuro": 1, "bite": 2}:
        sys.exit(f"Neurotoxin's / Venomous Bite's shares are not where this script expects them (neuro 1, bite 2): {found}")
    left = [x for x in walk(champion) if x.get("type") == "FixedAttack" and x.get("target_hp_ratio") in (p["q_hp"], p["cq_hp"])]
    if left:
        sys.exit(f"a % max health share of the main pack's Q is left in the copy: {left}")
    return champion


def main():
    check = "--check" in sys.argv[1:]
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_elise differs from build_elise.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != "league_elise:queen":
        sys.exit("the copy does not call the add-on: update this script")
    if champion["skill2"]["casting_type"] != "Targeting" or champion["ult"]["casting_type"] != "Targeting":
        sys.exit("the copy's skill2 / ult are not cast on a target: update build_elise.py")
    c = consts(open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read())
    champion = units(champion, p, c)
    champion = venom(champion, p)
    for slot in SLOTS:
        champion[slot]["description"] = f"#asset/base/text/champion?description.{TEXT_ID}.{slot}"

    values = dict(setup.values(p), q_cur=c["Q_CUR"], cq_miss=c["CQ_MISS"], qm_dmg=c["QM_DMG"], qm_ap=c["QM_AP"])
    texts = {}
    for lang, swaps in SWAP.items():
        texts[lang] = {}
        for slot in SLOTS:
            src = setup.TEXT[lang][slot]
            for old, new in swaps[slot]:
                if src.count(old) != 1:
                    sys.exit(f"{lang}.{slot}: {old!r} is not once in setup_elise.TEXT")
                src = src.replace(old, new)
            texts[lang][slot] = (LEAD[lang] + src).format(**values)
    lens = {f"{lang}.{slot}": setup.shown_length(LEAD[lang] + t) for lang, d in SWAP.items() for slot in SLOTS
            for t in [_swapped(setup.TEXT[lang][slot], d[slot])]}
    long = {k: n for k, n in lens.items() if n > setup.TOOLTIP_MAX[k.split(".")[0]]}
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
    print("passive", champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {k: f"{n}/{setup.TOOLTIP_MAX[k.split('.')[0]]}" for k, n in lens.items()})


def _swapped(src, pairs):
    for old, new in pairs:
        src = src.replace(old, new)
    return src


if __name__ == "__main__":
    main()
