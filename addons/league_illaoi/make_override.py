"""Build the add-on's copy of Illaoi from the main pack (tentacles on the walls, the spirit's echo and leash, tentacles
after the marked).

    python addons/league_illaoi/make_override.py

Rebuilds Illaoi with tools/kit/build_illaoi.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_illaoi.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_illaoi/override/league_illaoi.data_champion and
.../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit but the tentacles: an attack's tentacle raises a 2-tick `league_illaoi_p_new` on
    her, Leap of Faith's landing a 2-tick `league_illaoi_r_new` (the add-on stands them by the walls); Harsh Lesson's
    target is marked as before, the add-on's tentacles lash it; the spirit is a plain mark (no damaged_amplify) and the
    Vessel the add-on's;
  * passive = league_illaoi:prophet (params: NATIVE_KEYS of the kit);
  * the attack's and Test of Spirit's tooltips (keys of the add-on's own id) say what the add-on changes, so the tooltip
    in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Illaoi changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_illaoi")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_illaoi as kit  # noqa: E402
import setup_illaoi as setup  # noqa: E402

MOD_ID = "league_illaoi"
HERO = "league_illaoi"
O, A, R, E = setup.O, setup.A, setup.R, setup.E
phys, t, n, cc, hl = setup.phys, setup.t, setup.n, setup.cc, setup.hl
# lang -> the add-on's attack and Test of Spirit texts
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】抡神像砸下。" + n("古神先知") + "：普攻时每" + t("{p_cd}秒") + "在她附近的墙边长出触手" + t("{t_life}秒") +
                  "（没墙就在身前），每" + t("{t_per}秒") + "抽一个敌人" + phys("t_dmg", "t_ratio") + "物理伤害，先抽被教训的和躯壳；抽中英雄" +
                  hl("回复") + phys("p_heal", "p_heal_r") + "生命。",
        "skill2": "【附加包】扯出敌方英雄的灵魂" + t("{e_t}秒") + "：她打他多造成{e_echo}%伤害，" + cc("减速") + "{e_slow}%；他走得离灵魂太远或灵魂到时，"
                  "变成躯壳" + t("{e_vt}秒") + "，身边长出触手。",
    },
    "zh-hant": {
        "attack": "【附加包】掄神像砸下。" + n("遠古預言") + "：普攻時每" + t("{p_cd}秒") + "在她附近的牆邊長出觸手" + t("{t_life}秒") +
                  "（沒牆就在身前），每" + t("{t_per}秒") + "抽一個敵人" + phys("t_dmg", "t_ratio") + "物理傷害，先抽被教訓的和軀殼；抽中英雄" +
                  hl("回復") + phys("p_heal", "p_heal_r") + "生命。",
        "skill2": "【附加包】扯出敵方英雄的靈魂" + t("{e_t}秒") + "：她打他多造成{e_echo}%傷害，" + cc("緩速") + "{e_slow}%；他走得離靈魂太遠或靈魂到時，"
                  "變成軀殼" + t("{e_vt}秒") + "，身邊長出觸手。",
    },
    "en": {
        "attack": "[Add-on] Swings her idol down. " + n("Prophet of an Elder God") + ": an attack grows a tentacle on the edge of "
                  "the walls near her every " + t("{p_cd}s") + " for " + t("{t_life}s") + " (before her in the open); it strikes an "
                  "enemy every " + t("{t_per}s") + " for " + phys("t_dmg", "t_ratio") + " physical damage, the lessoned and Vessels "
                  "first, and " + hl("heals") + " her " + phys("p_heal", "p_heal_r") + " when it hits a champion.",
        "skill2": "[Add-on] Rips the spirit out of an enemy champion for " + t("{e_t}s") + ": her hits on it deal {e_echo}% more "
                  "and it is " + cc("slowed") + " {e_slow}%; walking too far from its spirit, or when the spirit runs out, it "
                  "becomes a Vessel for " + t("{e_vt}s") + " and a tentacle grows by it.",
    },
    "ko": {
        "attack": "[확장] 신상을 내리친다. " + n("고대신의 예언자") + ": 기본 공격 시 " + t("{p_cd}초") + "마다 근처 벽 가장자리에 촉수가 " +
                  t("{t_life}초") + " 자라(벽이 없으면 앞에) " + t("{t_per}초") + "마다 적에게 " + phys("t_dmg", "t_ratio") +
                  " 물리 피해, 가르침 대상과 그릇을 먼저 친다. 챔피언 적중 시 " + phys("p_heal", "p_heal_r") + " " + hl("회복") + ".",
        "skill2": "[확장] 적 챔피언의 영혼을 " + t("{e_t}초") + " 끌어낸다: 그녀의 공격 피해 +{e_echo}%, {e_slow}% " + cc("둔화") +
                  "; 영혼에서 너무 멀어지거나 시간이 다 되면 " + t("{e_vt}초") + " 동안 그릇이 되어 곁에 촉수가 자란다.",
    },
    "ja": {
        "attack": "【拡張】神像を振り下ろす。" + n("旧神の預言者") + "：通常攻撃時" + t("{p_cd}秒") + "ごとに近くの壁際へ触手が" + t("{t_life}秒") +
                  "生え（壁がなければ前へ）、" + t("{t_per}秒") + "ごとに敵へ" + phys("t_dmg", "t_ratio") + "の物理ダメージ、教訓の対象と器を"
                  "優先。英雄に当たると" + phys("p_heal", "p_heal_r") + hl("回復") + "。",
        "skill2": "【拡張】敵英雄の魂を" + t("{e_t}秒") + "引き出す：彼女の攻撃ダメージ+{e_echo}%、{e_slow}%" + cc("スロウ") + "。魂から離れすぎるか時間"
                  "切れで" + t("{e_vt}秒") + "器となり、そばに触手が生える。",
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
    m = re.search(r"impl Default for Params \{.*?Self \{(.*?)\}", src, re.S)
    return {k.strip(): int(v.strip().rstrip(",")) for k, v in re.findall(r"(\w+): (\d+),?", m.group(1))}


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_illaoi differs from build_illaoi.P: rebuild it first")
    wrong = {k: (v, p[k]) for k, v in rust_defaults().items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs Params defaults differ from build_illaoi.P (rust, P): %s" % wrong)
    missing = set(kit.NATIVE_KEYS) - set(rust_defaults())
    if missing:
        sys.exit("src/lib.rs Params lacks %s" % sorted(missing))
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":prophet":
        sys.exit("the copy has no league_illaoi:prophet passive: update this script")
    text = json.dumps(champion)
    if '"league_illaoi_p_new"' not in text or '"league_illaoi_r_new"' not in text or '"league_illaoi_t' in text.replace(
            '"league_illaoi_tentacle"', ""):
        sys.exit("the copy still grows the data's tentacles or lacks p_new / r_new: update this script")
    if "damaged_amplify" in text:
        sys.exit("the copy's spirit still amplifies all damage: update this script")
    champion["attack"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".attack"
    champion["skill2"]["description"] = "#asset/base/text/champion?description." + MOD_ID + ".skill2"

    values = setup.values(p)
    texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
            if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, tx in d.items()})


if __name__ == "__main__":
    main()
