"""Build the add-on's copy of Ivern from the main pack (Brushmaker's brush a real brush: Rengar pounces from it, Qiyana
takes grass from it).

    python addons/league_ivern/make_override.py

Rebuilds Ivern with tools/kit/build_ivern.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_ivern.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_ivern/override/league_ivern.data_champion and
.../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * the brush's growing raises a 2-tick `league_ivern_w_new` on him instead of the allies' bonus at that moment (the
    add-on gives it to the allies standing in the brush, every tick);
  * passive = league_ivern:brush (params w_r, w_t, w_atk);
  * the attack's tooltip (description.league_ivern.attack, a key of the add-on's own id) says what the add-on changes,
    so the tooltip in game shows whether the override took;
  * R (0.2.0): Daisy a unit of her own - the drop marks its champion with src/daisy.rs's D_MARK (3 ticks), and the
    riding punches (the AddCasted count) and her wave at the end play only without D_UNIT on him, which the add-on lays
    when the host gives the unit; the numbers the natives use (daisy.rs: D_*) are checked against the kit, the drop's
    picture and the unit sheet here; R's tooltip (description.league_ivern.ult) says she is a unit.
Every other champion stays untouched. Run it again whenever the main pack's Ivern changes (--check: compare only).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_ivern")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_ivern as kit  # noqa: E402
import setup_ivern as setup  # noqa: E402

MOD_ID = "league_ivern"
HERO = "league_ivern"
O, A, E = setup.O, setup.A, setup.E
mag = setup.mag
# lang -> the add-on's attack text
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】扔出一颗种子。" + O + "揠苗助攻" + E + "：每次种豆得瓜都在脚下长出一片真正的草丛" + A + "{w_t}秒" + E +
                  "，站在里面的队友攻击+{w_atk}%，雷恩加尔能从里面扑出去，奇亚娜能从里面拿草元素；他自己的普攻追加" +
                  mag("w_dmg", "w_ratio") + "魔法伤害。",
    },
    "zh-hant": {
        "attack": "【附加包】扔出一顆種子。" + O + "茂林春生" + E + "：每次施放守護種子都在腳下長出一片真正的草叢" + A + "{w_t}秒" + E +
                  "，站在裡面的隊友攻擊+{w_atk}%，雷葛爾能從裡面撲出去，琪亞娜能從裡面取得草元素；他自己的普攻追加" +
                  mag("w_dmg", "w_ratio") + "魔法傷害。",
    },
    "en": {
        "attack": "[Add-on] Throws a seed. " + O + "Brushmaker" + E + ": each Triggerseed grows a real brush at his feet for " +
                  A + "{w_t}s" + E + ": allies standing in it gain +{w_atk}% attack, Rengar can pounce from it and Qiyana take "
                  "grass from it; his own attacks deal " + mag("w_dmg", "w_ratio") + " magic damage more.",
    },
    "ko": {
        "attack": "[확장] 씨앗을 던진다. " + O + "수풀 가꾸기" + E + ": 보호의 씨앗마다 발밑에 진짜 수풀이 " + A + "{w_t}초" + E +
                  " 자란다. 안에 선 아군 공격력 +{w_atk}%, 렝가는 그 안에서 도약하고 키아나는 풀숲 원소를 얻는다. 그의 기본 공격은 " +
                  mag("w_dmg", "w_ratio") + " 마법 피해 추가.",
    },
    "ja": {
        "attack": "【拡張】種を投げる。" + O + "シゲミヅクリ" + E + "：タネバクダンのたびに足元へ本物の茂みが" + A + "{w_t}秒" + E +
                  "生え、中に立つ味方は攻撃力+{w_atk}%、レンガーはそこから飛びかかれ、キヤナは草むらのエレメントを得る。自身の通常攻撃は" +
                  mag("w_dmg", "w_ratio") + "の魔法ダメージを追加。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def rust_defaults():
    """Params::default() in src/lib.rs as {field: value}."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (w_r: .*?) \}", src)
    return {k.strip(): int(v) for k, v in (kv.split(":") for kv in m.group(1).split(","))}


# R (0.2.0): per language (the main pack's words, the add-on's) applied in order to the main pack's ult text
ULT = {
    "zh-hans": [("之后", "之后她留在场上、能被击杀，"), ("每第三拳", "打同一个英雄每第三拳")],
    "zh-hant": [("之後", "之後她留在場上、能被擊殺，"), ("每第三拳", "打同一個英雄每第三拳")],
    "en": [("then a punch every second", "then she stays as a unit that can be killed and punches every second"),
           ("every third a slam", "every third on the same champion a slam")],
    "ko": [("이후 ", "이후 처치될 수 있는 유닛으로 남아 "), ("세 번째마다", "같은 챔피언에게 세 번째마다")],
    "ja": [("その後", "その後倒せるユニットとして残り"), ("3発ごとに", "同じ英雄へ3発ごとに")],
}
LEAD = {"zh-hans": "【附加包】", "zh-hant": "【附加包】", "en": "[Add-on] ", "ko": "[확장] ", "ja": "【拡張】"}


def walk(o):
    """every dict of a tree"""
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def consts(path):
    """a src file's `pub const NAME: <type> = <value>;` - integers, floats written `30_000.0`, strings."""
    out = {}
    src = open(lp(path), encoding="utf-8").read()
    for name, kind, value in re.findall(r"pub const (\w+): (usize|u64|f64|&str) = ([^;]+);", src):
        value = value.strip()
        out[name] = value.strip('"') if kind == "&str" else int(float(value.replace("_", "")))
    return out


def ticks_of(stem, tag):
    """a sheet's tag in ticks (60 a second)"""
    with open(lp(stem + "#anim.fanim"), encoding="utf-8-sig") as f:
        frames = json.load(f)["anims"][tag]["frames"]
    return round(sum(fr["duration"] for fr in frames) * 60)


def daisy(champion, c, p):
    """R's Daisy a unit (0.2.0): the natives' numbers (c: src/daisy.rs) checked, then the drop's mark and the riding part
    played only without D_UNIT."""
    ult = champion["ult"]

    def sw(none):
        return {"type": "SwitchByBuff", "buff_name": c["D_UNIT"], "effect_buff": {"type": "Combine", "effects": []},
                "effect_none": none}
    calls = [x for x in walk(ult) if x.get("type") == "TargetProjectile" and x.get("name") == HERO + "_r_call"]
    punches = [x for x in walk(ult) if x.get("type") == "AddCasted" and (x["duration"], x["period"]) == (p["r_t"], p["r_per"])]
    byes = [x for x in walk(ult) if x.get("type") == "AddCasted" and (x["duration"], x["period"]) == (p["r_t"] + 1, p["r_t"])]
    if len(calls) != 1 or len(punches) != 1 or len(byes) != 1 or len(punches[0]["effects"]) != 1 or len(byes[0]["effects"]) != 1:
        sys.exit("R's drop, its riding punches or her wave changed in the kit: update this script")
    effects = json.dumps(champion)
    views = {v["name"] for v in champion["view_effects"]}
    for k in ("SHOCK_VIEW", "HIT_VIEW", "BYE_VIEW"):
        if c[k] not in views:
            sys.exit(f"src/daisy.rs's {k} = {c[k]} is no view effect of Ivern")
    if '"type": "TargetSfx", "name": "' + c["SLAM_SFX"] + '"' not in effects:
        sys.exit(f"src/daisy.rs's SLAM_SFX = {c['SLAM_SFX']} is no sound Ivern's R plays")
    got = {"D_HIT": p["r_dmg"], "D_HIT_AP": p["r_ratio"], "D_COOL": p["r_per"], "D_LANDS": p["r_hit_at"], "D_SLAM": p["r_slam"],
           "D_SLAM_AP": p["r_slam_r"], "D_UP": p["r_up"], "D_LIFE": p["r_t"] - 1,
           "D_FIRST": ticks_of(os.path.join(ROOT, "league", "effects", HERO + "_daisy_drop"), "idle"),
           "D_ACT": ticks_of(os.path.join(ROOT, "league", "champions", c["D_NAME"]), "attack")}
    wrong = {k: (c.get(k), v) for k, v in got.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"Daisy's numbers differ from src/daisy.rs (daisy.rs, kit and sheets): {wrong}")
    names = {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    names |= {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    if any(c[k] in names for k in ("D_MARK", "D_UNIT")) or any(str(b).startswith(c["D_UID"]) for b in names):
        sys.exit("Ivern's kit already uses one of src/daisy.rs's buff names: update it")
    calls[0]["applied_effects"].append({"casting_type": "Targeting", "effect": {
        "type": "AddBuff", "buff_state": {"name": c["D_MARK"], "duration": {"Time": {"tick": 3}}}}})
    punches[0]["effects"] = [sw(punches[0]["effects"][0])]
    byes[0]["effects"] = [sw(byes[0]["effects"][0])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_ivern differs from build_ivern.P: rebuild it first")
    wrong = {k: (v, p[k]) for k, v in rust_defaults().items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from build_ivern.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":brush":
        sys.exit("the copy has no league_ivern:brush passive: update this script")
    text = json.dumps(champion)
    if '"league_ivern_w_new"' not in text or '"league_ivern_w_buff"' in json.dumps(champion["skill"]):
        sys.exit("the copy's brush still gives the allies' bonus in data or lacks w_new: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"
    daisy(champion, consts(os.path.join(ADDON, "src", "daisy.rs")), p)
    champion["ult"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".ult"

    values = setup.values(p)
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in NATIVE.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    for lang, swaps in ULT.items():
        t = main_text[lang]["description"][HERO]["ult"]
        for old, new in swaps:
            if t.count(old) != 1:
                sys.exit(f"{lang} {HERO}.ult: the main pack's text changed ({old!r} found {t.count(old)} times): update this script")
            t = t.replace(old, new)
        texts[lang]["ult"] = LEAD[lang] + t
        if setup.shown_length(texts[lang]["ult"]) > setup.TOOLTIP_MAX[lang]:
            long[f"{lang}.ult"] = setup.shown_length(texts[lang]["ult"])
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                                  ensure_ascii=False, indent=2) + "\n"}
    if a.check:
        stale = [os.path.relpath(f, ROOT) for f, t in files.items()
                 if not os.path.exists(lp(f)) or open(lp(f), encoding="utf-8").read().replace("\r\n", "\n") != t]
        print(MOD_ID + ":", "stale " + ", ".join(stale) if stale else "up to date")
        sys.exit(1 if stale else 0)
    for f, t in files.items():
        os.makedirs(lp(os.path.dirname(f)), exist_ok=True)
        with open(lp(f), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(t)
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in texts.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
