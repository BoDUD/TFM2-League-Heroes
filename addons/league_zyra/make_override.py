"""Build the add-on's copy of Zyra from the main pack (seeds on the ground, the plants they grow, enraged by her R).

    python addons/league_zyra/make_override.py [--check]

Rebuilds Zyra with tools/kit/build_zyra.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_zyra.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_zyra/override/league_zyra.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the seed, Deadly Spines with its Thorn Spitter, Grasping Roots with its Vine
    Lasher, Stranglethorns enraging the plants);
  * passive = the add-on's league_zyra:garden with the numbers of P it uses (passive.params);
  * Q, E and R lay a 2-tick mark on their target as the lob leaves her (q_aim / e_aim / r_aim): where they land;
  * the views of the add-on's own pictures: the seeds on the ground (s_seed), the plants' spit (t_spit);
  * 0.2.0, the plants' bodies (src/lib.rs; tools/art/unit_zyra_plants.py draws their sheets): the plant the data grows
    where Q and E land (its picture, its sound, its zone) plays only without `P_UNIT`; with it the landing lays `Q_LAND`
    / `E_LAND` on her (3 ticks) and the add-on grows a plant of its own there (with a body). The bodies' strike timings
    (TP_ACT / TP_LANDS, VP_ACT / VP_LANDS) are checked against the unit sheets: change them and this script stops until
    lib.rs follows;
  * the attack's, skill's and skill2's tooltips point to description.league_zyra.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Zyra changes. --check: write nothing, exit 1
when the files on disk are not what this would write.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_zyra")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_zyra as kit  # noqa: E402
import setup_zyra as setup  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools", "art"))
import unit_zyra_plants as bodies  # noqa: E402

MOD_ID = "league_zyra"
HERO = "league_zyra"
SLOTS = ("attack", "skill", "skill2")
O, A, R, M, E = setup.O, setup.A, setup.R, setup.M, setup.E
mag, t = setup.mag, setup.t

TEXT = {
    "zh-hans": {
        "attack": "【扩展包】甩出一颗荆棘种子。" + O + "荆棘花园" + E + "：每" + t("{s_cd}秒") + "在身边掉一颗种子（留" + t("{s_life}秒") +
                  "），参与击杀时马上掉一颗；Q、E 落在种子旁边会让种子长成植物，植物先打英雄，伤害随等级成长，可被击杀。",
        "skill": "【扩展包】地面炸出棘刺，造成" + mag("q_dmg", "q_ratio") + "魔法伤害。落点和旁边的种子长成" + O + "荆棘喷射者" + E +
                 "，向敌人吐刺。",
        "skill2": "【扩展包】贯穿地面的藤蔓造成" + mag("e_dmg", "e_ratio") + "魔法伤害并" + R + "禁锢" + E + t("{e_root}秒") +
                  "。落点和藤蔓经过的种子长成" + O + "藤蔓鞭击者" + E + "，抽打并减速。",
    },
    "zh-hant": {
        "attack": "【擴充包】甩出一顆荊棘種子。" + O + "荊棘花園" + E + "：每" + t("{s_cd}秒") + "在身邊掉一顆種子（留" + t("{s_life}秒") +
                  "），參與擊殺時馬上掉一顆；Q、E 落在種子旁邊會讓種子長成植物，植物先打英雄，傷害隨等級成長，可被擊殺。",
        "skill": "【擴充包】地面炸出棘刺，造成" + mag("q_dmg", "q_ratio") + "魔法傷害。落點和旁邊的種子長成" + O + "棘刺噴吐草" + E +
                 "，向敵人吐刺。",
        "skill2": "【擴充包】貫穿地面的藤蔓造成" + mag("e_dmg", "e_ratio") + "魔法傷害並" + R + "定身" + E + t("{e_root}秒") +
                  "。落點和藤蔓經過的種子長成" + O + "棘蔓鞭笞草" + E + "，抽打並緩速。",
    },
    "en": {
        "attack": "[Add-on] Flings a thorn seed. " + O + "Garden of Thorns" + E + ": a seed falls near her every " + t("{s_cd}s") +
                  " (it lasts " + t("{s_life}s") + ") and one at once on a takedown; Q and E landing near seeds grow them into "
                  "plants that strike champions first, harder with her level; they can be killed.",
        "skill": "[Add-on] Spines burst from the ground for " + mag("q_dmg", "q_ratio") + " " + M + "magic damage" + E + ". The "
                 "seed there and the seeds near it grow " + O + "Thorn Spitters" + E + " that spit at enemies.",
        "skill2": "[Add-on] Vines run through the ground for " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E + ", " +
                  R + "rooting" + E + " for " + t("{e_root}s") + ". The seeds on their way grow " + O + "Vine Lashers" + E +
                  " that lash and slow.",
    },
    "ko": {
        "attack": "[확장] 가시 씨앗을 던진다. " + O + "가시 정원" + E + ": " + t("{s_cd}초") + "마다 주변에 씨앗이 떨어지고(" +
                  t("{s_life}초") + " 유지) 처치 관여 시 즉시 하나; Q와 E가 씨앗 근처에 떨어지면 식물로 자라 챔피언을 먼저 공격하며 레벨에 따라 강해진다(처치 가능).",
        "skill": "[확장] 지면에서 가시가 폭발해 " + mag("q_dmg", "q_ratio") + " 마법 피해. 그 자리와 근처의 씨앗이 " + O + "가시 발사 꽃" + E +
                 "으로 자라 적에게 가시를 쏜다.",
        "skill2": "[확장] 지면을 뚫는 덩굴로 " + mag("e_dmg", "e_ratio") + " 마법 피해와 " + t("{e_root}초") + " " + R + "속박" + E +
                  ". 지나간 자리의 씨앗이 " + O + "덩굴 채찍손" + E + "으로 자라 공격하며 둔화시킨다.",
    },
    "ja": {
        "attack": "【拡張】トゲの種を投げる。" + O + "茨の楽園" + E + "：" + t("{s_cd}秒") + "ごとに近くに種が落ち（" + t("{s_life}秒") +
                  "残る）、キル関与で即座に1つ；QとEが種の近くに当たると植物に育ち、チャンピオンを優先して攻撃し、レベルで強くなる（倒せる）。",
        "skill": "【拡張】地面からトゲが弾け" + mag("q_dmg", "q_ratio") + "の魔法ダメージ。その場と近くの種が" + O + "棘吹草" + E +
                 "に育ち、敵にトゲを吐く。",
        "skill2": "【拡張】地中を伸びるツタが" + mag("e_dmg", "e_ratio") + "の魔法ダメージと" + t("{e_root}秒") + R + "移動不能" + E +
                  "。通り道の種が" + O + "棘鞭草" + E + "に育ち、攻撃してスロウを与える。",
    },
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def consts(src):
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers and strings."""
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|&str) = ([^;]+);", src):
        value = value.strip()
        out[name] = value.strip('"') if kind == "&str" else int(value.replace("_", ""))
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


def lists(o):
    """every list of a tree"""
    if isinstance(o, dict):
        for v in o.values():
            yield from lists(v)
    elif isinstance(o, list):
        yield o
        for v in o:
            yield from lists(v)


def units(champion, c):
    """0.2.0: the plant the data grows where Q / E land plays only without P_UNIT; with it the landing marks her. The
    bodies' strike timings (c: src/lib.rs) checked against the unit sheets."""
    want = {}
    want["TP_ACT"], want["TP_LANDS"] = bodies.strike_lands(c["SPITTER"])
    want["VP_ACT"], want["VP_LANDS"] = bodies.strike_lands(c["LASHER"])
    wrong = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"the bodies' numbers differ from src/lib.rs (lib or sheet): {wrong}")
    names = {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    names |= {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    if any(c[k] in names for k in ("P_UNIT", "Q_LAND", "E_LAND", "P_FAIL")) or any(str(b).startswith(c["P_UID"]) for b in names):
        sys.exit("the main pack's Zyra already uses one of the add-on's buff names: update src/lib.rs")
    for pic, snd, zone, mark, n in (("t_plant", "t_grow", "t_spit", c["Q_LAND"], 2), ("v_plant", "v_grow", "v_lash", c["E_LAND"], 1)):
        found = 0
        for li in list(lists(champion)):
            at = [i for i, x in enumerate(li) if isinstance(x, dict) and x.get("type") == "ViewEffect" and x.get("name") == f"{HERO}_{pic}"]
            if not at:
                continue
            parts = [i for i, x in enumerate(li) if isinstance(x, dict) and (
                (x.get("type") == "ViewEffect" and x.get("name") == f"{HERO}_{pic}")
                or (x.get("type") == "Sfx" and x.get("name") == f"{HERO}_{snd}")
                or (x.get("type") == "RangePeriodProjectile" and x.get("name") == f"{HERO}_{zone}"))]
            if len(parts) != 3:
                sys.exit(f"the plant {pic} is no longer its picture, its sound and its zone in one list: update this script")
            plant = [li[i] for i in parts]
            sw = {"type": "SwitchByBuff", "buff_name": c["P_UNIT"],
                  "effect_buff": {"type": "AddCasterBuff", "buff_state": {"name": mark, "duration": {"Time": {"tick": 3}}},
                                  "only_to_enemy": False},
                  "effect_none": {"type": "Combine", "effects": plant}}
            li[parts[0]] = sw
            for i in reversed(parts[1:]):
                del li[i]
            found += 1
        if found != n:
            sys.exit(f"the data grows {pic} {found} times where Q / E land, not {n}: update this script")
    return champion


def main():
    check = "--check" in sys.argv[1:]
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_zyra differs from build_zyra.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":garden":
        sys.exit("the copy has no league_zyra:garden passive: update this script")
    champion = units(champion, consts(open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()))
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values["s_cd"] = setup.secs(p["s_cd"])
    values["s_life"] = setup.secs(p["s_life"])
    texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in TEXT.items() for k, tx in d.items()
            if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    out = os.path.join(ADDON, "override", HERO + ".data_champion")
    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    out_text = os.path.join(ADDON, "text", "champion.i18n")
    files = {out: json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
             out_text: json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                                  ensure_ascii=False, indent=2) + "\n"}
    if check:
        stale = [os.path.relpath(path, ROOT) for path, text in files.items()
                 if not os.path.isfile(lp(path)) or open(lp(path), encoding="utf-8").read() != text]
        if stale:
            sys.exit("not as make_override.py writes them: %s" % stale)
        print("ok")
        return
    for path, text in files.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print("wrote", os.path.relpath(out, ROOT), "and", os.path.relpath(out_text, ROOT), "- passive =",
          champion["passive"]["passive_ref"], json.dumps(champion["passive"]["params"]))
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in TEXT.items() for k, tx in d.items()})


if __name__ == "__main__":
    main()
