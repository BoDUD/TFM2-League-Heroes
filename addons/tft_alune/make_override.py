"""Build the add-on's copy of Alune from the tft pack (Moonfall on the nearest enemies, the full moon shared, the ring's
way back) and its texts.

    python addons/tft_alune/make_override.py [--check]

Rebuilds Alune with tools/kit/build_alune.py (its parameter table P), checks that the plain build is the tft pack's
tft/champion/tft_alune.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/tft_alune/override/tft_alune.data_champion: the build
with native=1 (build_alune.py's docstring) - passive tft_alune:moon (params build_alune.NATIVE_KEYS); Moonfall only
flags q_go (the add-on drops the shards); the full moon marks r_mark<phase> and deals nothing (the add-on shares it);
the attack marks a_mark (the add-on flies the ring back, picture a_back) - and addons/tft_alune/text/champion.i18n: every
slot's tooltip with the add-on's rules (the tft pack's keys, merged over its text: the tooltip in game shows whether the
copy took), in every language the tft pack has.
Every other champion stays untouched. Run it again whenever the tft pack's Alune changes.
--check: write nothing, exit 1 when the files on disk are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "tft_alune")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_alune as kit  # noqa: E402
import setup_alune as setup  # noqa: E402

HERO = "tft_alune"
SLOTS = ("attack", "skill", "skill2", "ult")
M, O, A, R, E, ADi, APi, AD = setup.M, setup.O, setup.A, setup.R, setup.E, setup.ADi, setup.APi, setup.AD
mag = setup.mag

# lang -> the add-on's texts for every slot (the tft pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】甩出螺旋月环造成" + AD + O + "物理伤害" + E + "，月环飞回她手里，回程路上的敌人受到" + ADi + O + "{a_back_r}%" + E +
                  "物理伤害。" + O + "月相" + E + "：每放一次技能月亮长一档（最多" + A + "3" + E + "档），大招每档+" + A + "{r_ph}%" + E + "。",
        "skill": "【附加包】月光碎片落在离她最近的" + A + "{q_n}" + E + "个敌人身上，每枚造成" + mag("q_dmg", "q_ratio") + "魔法伤害，并使魔抗降低" +
                 A + "{q_shred}%" + E + "，持续" + A + "{q_shred_t}秒" + E + "。",
        "skill2": "【附加包】月光洒在她和身边的友方英雄身上，攻击速度提高" + A + "{e_as}%" + E + "，持续" + A + "{e_t}秒" + E + "。",
        "ult": "【附加包】满月砸在敌方英雄身上，" + mag("r_dmg", "r_ratio") + "魔法伤害（每档月相+{r_ph}%）由范围内的敌人分摊，只砸中一个人时为" +
               A + "{r_cap}%" + E + "；中心的敌人" + R + "眩晕" + E + A + "{r_stun}秒" + E + "。",
    },
    "zh-hant": {
        "attack": "【附加包】甩出螺旋月環造成" + AD + O + "物理傷害" + E + "，月環飛回她手裡，回程路上的敵人受到" + ADi + O + "{a_back_r}%" + E +
                  "物理傷害。" + O + "月相" + E + "：每施放一次技能月亮長一階（最多" + A + "3" + E + "階），大招每階+" + A + "{r_ph}%" + E + "。",
        "skill": "【附加包】月華碎片落在離她最近的" + A + "{q_n}" + E + "名敵人身上，每塊造成" + mag("q_dmg", "q_ratio") + "魔法傷害，並使魔抗降低" +
                 A + "{q_shred}%" + E + "，持續" + A + "{q_shred_t}秒" + E + "。",
        "skill2": "【附加包】月光灑在她和身邊的友方英雄身上，攻擊速度提高" + A + "{e_as}%" + E + "，持續" + A + "{e_t}秒" + E + "。",
        "ult": "【附加包】滿月砸在敵方英雄身上，" + mag("r_dmg", "r_ratio") + "魔法傷害（每階月相+{r_ph}%）由範圍內的敵人平均分攤，只砸中一人時為" +
               A + "{r_cap}%" + E + "；中心的敵人" + R + "暈眩" + E + A + "{r_stun}秒" + E + "。",
    },
    "en": {
        "attack": "[Add-on] Flings her spiral ring for " + AD + " " + O + "physical damage" + E + "; it flies back to her, dealing " +
                  ADi + O + "{a_back_r}%" + E + " physical damage to enemies on the way. " + O + "Moon Phase" + E + ": each skill "
                  "grows the moon a phase (up to " + A + "3" + E + "); her ultimate deals " + A + "{r_ph}%" + E + " more a phase.",
        "skill": "[Add-on] Moonshards rain on the " + A + "{q_n}" + E + " nearest enemies, each dealing " + mag("q_dmg", "q_ratio") + " " +
                 M + "magic damage" + E + " and lowering magic resistance by " + A + "{q_shred}%" + E + " for " + A + "{q_shred_t}s" + E +
                 ".",
        "skill2": "[Add-on] Moonlight falls on her and the allied champions near her: " + A + "{e_as}%" + E + " attack speed for " + A +
                  "{e_t}s" + E + ".",
        "ult": "[Add-on] The full moon crashes on an enemy champion: " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               " ({r_ph}% more a moon phase) split among the enemies in the area, " + A + "{r_cap}%" + E + " if it hits only one; "
               "those in the middle are " + R + "stunned" + E + " for " + A + "{r_stun}s" + E + ".",
    },
    "ko": {
        "attack": "[확장] 나선 고리를 던져 " + AD + " 물리 피해, 고리는 되돌아오며 길 위의 적에게 " + ADi + O + "{a_back_r}%" + E + " 물리 피해. " + O +
                  "달의 위상" + E + ": 스킬마다 달이 한 단계 차오른다(최대 " + A + "3" + E + "), 궁극기는 단계마다 +" + A + "{r_ph}%" + E + ".",
        "skill": "[확장] 가장 가까운 적 " + A + "{q_n}" + E + "명에게 달조각이 떨어져 각각 " + mag("q_dmg", "q_ratio") + " 마법 피해와 " + A +
                 "{q_shred_t}초" + E + " 동안 마법 저항력 -" + A + "{q_shred}%" + E + ".",
        "skill2": "[확장] 자신과 주변 아군 챔피언에게 달빛이 내려 " + A + "{e_t}초" + E + " 동안 공격 속도 +" + A + "{e_as}%" + E + ".",
        "ult": "[확장] 보름달이 적 챔피언에게 떨어진다: " + mag("r_dmg", "r_ratio") + " 마법 피해(위상마다 +{r_ph}%)를 범위의 적이 나누어 받고, 하나만 "
               "맞으면 " + A + "{r_cap}%" + E + "; 중심의 적은 " + A + "{r_stun}초" + E + " " + R + "기절" + E + ".",
    },
    "ja": {
        "attack": "【拡張】螺旋の輪を投げて" + AD + "の物理ダメージ、輪は戻ってきて途中の敵に" + ADi + O + "{a_back_r}%" + E + "の物理ダメージ。" + O +
                  "月相" + E + "：スキルごとに月が満ちる（最大" + A + "3" + E + "段階）、アルティメットは1段階ごとに+" + A + "{r_ph}%" + E + "。",
        "skill": "【拡張】最も近い敵" + A + "{q_n}" + E + "体に月の破片が降り、それぞれ" + mag("q_dmg", "q_ratio") + "の魔法ダメージと" + A +
                 "{q_shred_t}秒" + E + "の魔法防御-" + A + "{q_shred}%" + E + "。",
        "skill2": "【拡張】自分と周りの味方チャンピオンに月光が降り、" + A + "{e_t}秒" + E + "間攻撃速度+" + A + "{e_as}%" + E + "。",
        "ult": "【拡張】満月が敵チャンピオンに落ちる：" + mag("r_dmg", "r_ratio") + "の魔法ダメージ（月相1段階ごとに+{r_ph}%）を範囲の敵で分け合い、1体だけなら" +
               A + "{r_cap}%" + E + "；中心の敵は" + A + "{r_stun}秒" + E + R + "スタン" + E + "。",
    },
}


def dumps(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def lp(path):
    return kit.lp(path)


def rust_defaults():
    """Params::default() in src/lib.rs as {key: value}."""
    src = open(os.path.join(ADDON, "src", "lib.rs"), encoding="utf-8").read()
    body = src[src.index("impl Default for Params"):]
    body = body[body.index("Self {") + 6:body.index("}")]
    return {k: int(v) for k, v in re.findall(r"(\w+):\s*(-?\d+)", body)}


def files():
    """{path: text} this script writes."""
    p = dict(kit.P)
    plain = dumps(kit.build(p))
    shipped = open(lp(kit.OUT), "rb").read().decode("utf-8")
    if plain != shipped:
        sys.exit("tft/champion/tft_alune.data_champion is not build_alune.py's P: rebuild the tft pack first")
    rd = rust_defaults()
    bad = {k: (rd.get(k), p[k]) for k in kit.NATIVE_KEYS if rd.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params defaults differ from P (rust, P): {bad}")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != HERO + ":moon":
        sys.exit("the copy does not call the add-on: update this script")
    for slot in SLOTS:                     # the tft pack's keys (merged over by this add-on's text)
        if champion[slot]["description"] != "#asset/base/text/champion?description." + HERO + "." + slot:
            sys.exit(f"{slot}: the tooltip key changed - update this script")
    values = dict(setup.values(p), a_back_r=p["a_back_r"], r_cap=p["r_cap"])
    texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
            if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    with open(lp(os.path.join(ROOT, "tft", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    print({f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}" for lang, d in NATIVE.items()
           for k, tx in d.items()})
    return {os.path.join(ADDON, "override", HERO + ".data_champion"): dumps(champion),
            os.path.join(ADDON, "text", "champion.i18n"): dumps({lang: {"description": {HERO: texts[lang]}}
                                                                  for lang in main_text})}


def main():
    out = files()
    if "--check" in sys.argv[1:]:
        stale = [os.path.relpath(path, ROOT) for path, text in out.items()
                 if not os.path.isfile(lp(path)) or open(lp(path), encoding="utf-8", newline="").read() != text]
        if stale:
            sys.exit("not as make_override.py writes them: %s" % stale)
        print("ok")
        return
    for path, text in out.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
