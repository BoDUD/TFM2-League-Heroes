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
    so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Ivern changes.
"""
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


def main():
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

    values = setup.values(p)
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in NATIVE.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    os.makedirs(lp(os.path.dirname(out)), exist_ok=True)
    with open(lp(out), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(champion, ensure_ascii=False, indent=2) + "\n")

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    os.makedirs(lp(os.path.dirname(out_text)), exist_ok=True)
    with open(lp(out_text), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                           ensure_ascii=False, indent=2) + "\n")
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
