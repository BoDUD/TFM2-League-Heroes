"""Build the add-on's copy of Poppy from the main pack (dash interrupt, wall stun, fountain-ward verdict, buckler shield).

    python addons/league_poppy/make_override.py

Rebuilds Poppy with tools/kit/build_poppy.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_poppy.data_champion byte for byte (so the copy never drifts from the shipped kit), and writes
addons/league_poppy/override/league_poppy.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit (the buckler, Hammer Shock, Steadfast Presence's flags, Heroic Charge's dash, the
    smart Keeper's Verdict);
  * passive = the add-on's league_poppy:steadfast (the dash interrupt inside her aura, the low-health armour, the wall
    slam's moment) with the numbers of P the add-on uses (checked against src/lib.rs's constants);
  * Steadfast Presence without the main pack's grounding pulses; Heroic Charge's push is league_poppy:charge (the wall
    check), Keeper's Verdict's knock-back league_poppy:verdict, the buckler's shield league_poppy:pick;
  * the attack's, skill2's and the ult's tooltips point to description.league_poppy.<slot> with the add-on's wording.
Every other champion stays untouched. Run it again whenever the main pack's Poppy changes.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_poppy")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_poppy as kit  # noqa: E402
import setup_poppy as setup  # noqa: E402

MOD_ID = "league_poppy"
HERO = "league_poppy"
SLOTS = ("attack", "skill2", "ult")
O, A, R, G, M, E = setup.O, setup.A, setup.R, setup.G, setup.M, setup.E
mag, phys, shield = setup.mag, setup.phys, setup.shield
TEXT = {
    "zh-hans": {
        "attack": "【扩展包】" + O + "钢铁大使" + E + "：每" + A + "{p_cd}秒" + E + "普攻远远扔出圆盾，多造成" + mag("p_dmg", "p_ap") + "魔法伤害；捡起圆盾得" + G +
                  "{p_sh_min}~{p_sh_max}%最大生命" + E + "护盾。" + O + "坚定风采" + E + "：双抗+{w_def}%（生命低于{w_low}%翻倍）；敌方英雄靠近时移速+{w_ms}%，" +
                  A + "{w_t}秒" + E + "内冲进她身边的敌人被" + R + "击飞并缚地" + E + "。",
        "skill2": "【扩展包】冲向敌方英雄，造成" + phys("e_dmg", "e_ratio") + "物理伤害并推着他走；撞到墙上再受一次伤害并" + R + "眩晕{e_stun}秒" + E + "。",
        "ult": "【扩展包】身边有2个以上敌方英雄时砸地：" + phys("r_tap_dmg", "r_tap_ratio") + "物理伤害并" + R + "击飞{r_up}秒" + E + "；否则蓄力抡锤推出冲击波，"
               "打中的英雄受" + phys("r_dmg", "r_ratio") + "物理伤害并" + R + "被打回他家泉水方向" + E + "。",
    },
    "zh-hant": {
        "attack": "【擴充包】" + O + "鋼鐵使者" + E + "：每" + A + "{p_cd}秒" + E + "普攻遠遠擲出圓盾，多造成" + mag("p_dmg", "p_ap") + "魔法傷害；撿起圓盾得" + G +
                  "{p_sh_min}~{p_sh_max}%最大生命" + E + "護盾。" + O + "堅定不移" + E + "：雙抗+{w_def}%（生命低於{w_low}%翻倍）；敵方英雄靠近時移速+{w_ms}%，" +
                  A + "{w_t}秒" + E + "內衝進她身邊的敵人被" + R + "擊飛並禁錮" + E + "。",
        "skill2": "【擴充包】衝向敵方英雄，造成" + phys("e_dmg", "e_ratio") + "物理傷害並推著他走；撞到牆上再受一次傷害並" + R + "暈眩{e_stun}秒" + E + "。",
        "ult": "【擴充包】身邊有2個以上敵方英雄時砸地：" + phys("r_tap_dmg", "r_tap_ratio") + "物理傷害並" + R + "擊飛{r_up}秒" + E + "；否則蓄力掄錘推出衝擊波，"
               "打中的英雄受" + phys("r_dmg", "r_ratio") + "物理傷害並" + R + "被打回他家泉水方向" + E + "。",
    },
    "en": {
        "attack": "[Add-on] " + O + "Iron Ambassador" + E + ": every " + A + "{p_cd}s" + E + " her attack throws her buckler for " +
                  mag("p_dmg", "p_ap") + " " + M + "magic damage" + E + " more; picking it up gives a " + G + "{p_sh_min}-{p_sh_max}% max health shield" +
                  E + ". " + O + "Steadfast Presence" + E + ": +{w_def}% armour and magic resist (doubled under {w_low}% health); near enemies "
                  "+{w_ms}% move speed, and for " + A + "{w_t}s" + E + " enemies dashing at her are " + R + "knocked up and grounded" + E + ".",
        "skill2": "[Add-on] Charges an enemy champion for " + phys("e_dmg", "e_ratio") + " physical damage and carries them; slammed into a wall "
                  "they take it again and are " + R + "stunned {e_stun}s" + E + ".",
        "ult": "[Add-on] With 2+ enemy champions close she slams the ground: " + phys("r_tap_dmg", "r_tap_ratio") + " physical damage and " + R +
               "knock-up {r_up}s" + E + ". Otherwise she charges and swings a shockwave: champions hit take " + phys("r_dmg", "r_ratio") +
               " physical damage and are " + R + "sent flying toward their fountain" + E + ".",
    },
    "ko": {
        "attack": "[확장] " + O + "강철의 외교관" + E + ": " + A + "{p_cd}초" + E + "마다 기본 공격이 방패를 멀리 던져 " + mag("p_dmg", "p_ap") + " 마법 피해 추가; "
                  "주우면 " + G + "최대 체력 {p_sh_min}~{p_sh_max}%" + E + " 보호막. " + O + "굳건한 태세" + E + ": 방어력·마법 저항력 +{w_def}%(체력 {w_low}% 미만 2배); "
                  "적 근처 이동 속도 +{w_ms}%, " + A + "{w_t}초" + E + " 동안 돌진해 오는 적 " + R + "에어본·이동 불가" + E + ".",
        "skill2": "[확장] 적 챔피언에게 돌진해 " + phys("e_dmg", "e_ratio") + " 물리 피해를 주고 밀고 나가며, 벽에 부딪히면 피해를 다시 주고 " + R +
                  "{e_stun}초 기절" + E + ".",
        "ult": "[확장] 주변에 적 챔피언 2명 이상이면 땅을 내리쳐 " + phys("r_tap_dmg", "r_tap_ratio") + " 물리 피해와 " + R + "{r_up}초 에어본" + E + "; 아니면 "
               "모았다 휘둘러 충격파: 맞은 챔피언은 " + phys("r_dmg", "r_ratio") + " 물리 피해를 입고 " + R + "자기 우물 쪽으로 날아감" + E + ".",
    },
    "ja": {
        "attack": "【拡張】" + O + "鋼鉄の大使" + E + "：" + A + "{p_cd}秒" + E + "ごとに通常攻撃で盾を遠くへ投げ" + mag("p_dmg", "p_ap") + "の魔法ダメージ追加；"
                  "拾うと" + G + "最大体力{p_sh_min}~{p_sh_max}%" + E + "のシールド。" + O + "ステッドファスト" + E + "：物防・魔防+{w_def}%（体力{w_low}%未満で2倍）；"
                  "敵が近いと移動速度+{w_ms}%、" + A + "{w_t}秒" + E + "突進してきた敵は" + R + "ノックアップ・移動阻害" + E + "。",
        "skill2": "【拡張】敵チャンピオンへ突進し" + phys("e_dmg", "e_ratio") + "の物理ダメージを与えて押し運ぶ；壁に叩きつけると再びダメージを与え" + R +
                  "{e_stun}秒スタン" + E + "。",
        "ult": "【拡張】近くに敵チャンピオン2体以上なら地面を叩き" + phys("r_tap_dmg", "r_tap_ratio") + "の物理ダメージと" + R + "{r_up}秒ノックアップ" +
               E + "；そうでなければ溜めて衝撃波：当たったチャンピオンは" + phys("r_dmg", "r_ratio") + "の物理ダメージで" + R + "自陣の泉の方へ吹き飛ぶ" +
               E + "。",
    },
}

CONSTS = {k: k.upper() for k in ("w_def", "w_low", "w_r", "w_dmg", "w_ap", "w_up", "w_ground", "w_slow", "e_dmg", "e_ratio",
                                  "e_kb_speed", "e_kb_t", "e_stun", "p_sh_min", "p_sh_max", "p_sh_t", "r_kb_speed",
                                  "r_kb_t", "r_air", "r_far", "r_far_speed")}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def main():
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_poppy differs from build_poppy.P: rebuild it first")
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    for key, const in CONSTS.items():
        m = re.search(rf"pub const {const}: usize = ([0-9_]+);", src)
        if not m or int(m.group(1).replace("_", "")) != p[key]:
            sys.exit(f"src/lib.rs {const} is not P[{key!r}] = {p[key]}: update the add-on")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":steadfast":
        sys.exit("the copy has no league_poppy:steadfast passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    values.update({k: p[k] for k in ("w_dmg", "w_ap", "w_slow", "w_low", "p_sh_min", "p_sh_max")})
    for k in ("w_up", "w_ground", "e_stun"):
        values[k] = setup.secs(p[k])
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in TEXT.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in TEXT.items() for k, t in d.items()
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
                              for lang, d in TEXT.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
