"""Build the add-on's copy of Naafiri from the main pack (the second dagger's execute, the pounce again on every
takedown, a smart ult, four hounds in the roar, the packmates units of their own).

    python addons/league_naafiri/make_override.py [--check]

Rebuilds Naafiri with tools/kit/build_naafiri.py (its parameter table P), checks that the plain build is the main
pack's league/champion/league_naafiri.data_champion byte for byte (so the copy never drifts from the shipped kit), checks
that the AI hook's constants in src/lib.rs are P's numbers, and writes addons/league_naafiri/override/
league_naafiri.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit;
  * the second dagger's damage is the Native league_naafiri:q2 (up to q_exec% more by the target's missing health);
  * no takedown window: the pounce arms `r_armed` and passive = league_naafiri:pack (the recast on every takedown);
  * 0.2.0, the packmates as units (src/lib.rs; tools/art/unit_naafiri_packmate.py draws their sheet): every pack bite
    (the homing pair league_naafiri_pk_c / pk_m on each hit) and the pack riding on the champion Q hits (the projectile
    league_naafiri_q_leap: its bites, its picture, its leap) play only without `SOLO` on her - the passive lays it while
    her packmates are units, so a host that gives no unit plays the main pack's pack as it is. The numbers the units use
    (HOUND_HIT / HOUND_HIT_AD = half the pack bite, ATK_CD, ATK_RANGE, ROAR_T, HOUND_ACT / HOUND_LANDS from the sheet)
    are checked against P and the unit sheet: change the main pack and this script stops until lib.rs follows;
  * the attack's, the skill's and the ult's tooltips (description.league_naafiri.*, keys of the add-on's own id) say
    what the add-on changes, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Naafiri changes. --check: write nothing, exit
1 when the files on disk are not what this would write.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_naafiri")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_naafiri as kit  # noqa: E402
import setup_naafiri as setup  # noqa: E402

MOD_ID = "league_naafiri"
HERO = "league_naafiri"
O, G, A, R, E = setup.O, setup.G, setup.A, setup.R, setup.E
phys, grn = setup.phys, setup.grn
# src/lib.rs constant -> P key
CONSTS = {"R_RANGE": "r_range", "R_DMG": "r_dmg", "R_RATIO": "r_ratio", "Q_DMG": "q_dmg", "Q_RATIO": "q_ratio",
          "Q_B_DMG": "q_b_dmg", "Q_B_RATIO": "q_b_ratio", "Q2_DMG": "q2_dmg", "Q2_RATIO": "q2_ratio", "E_DMG": "e_dmg",
          "E_RATIO": "e_ratio", "E2_DMG": "e2_dmg", "E2_RATIO": "e2_ratio", "PK_DMG": "pk_dmg", "PK_RATIO": "pk_ratio",
          "ROAR_AD": "roar_ad", "ATK_CD": "atk_cd", "ATK_RANGE": "atk_range", "ROAR_T": "roar_t"}
UNITS = os.path.join(ROOT, "league", "champions")
# lang -> the add-on's skill and ult texts
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】扑咬目标。" + O + "狂烈种群" + E + "：{pack_n}只伙伴跟着她自己追咬敌人（每口" + phys("hound_hit", "hound_ad") +
                  "，可被击杀，阵亡" + A + "{respawn}秒" + E + "后再来），和她一起阵亡。",
        "skill": "【附加包】掷出匕首，造成" + phys("q_dmg", "q_ratio") + "物理伤害并流血" + A + "{q_bleed}秒" + E + "。" + A +
                 "{q_win}秒" + E + "内下次普攻掷出第二把匕首，造成" + phys("q2_dmg", "q2_ratio") + "，目标每损失1%生命多{q_exec_pct}%伤害，"
                 "命中英雄回复" + grn("q_heal", "q_heal_r") + "生命。",
        "ult": "【附加包】" + O + "暴吼" + E + "：" + A + "{r_imm}秒" + E + "不可选取，狗群翻倍、攻击力+{roar_ad}%、移速+{roar_ms}%；随后扑向敌方英雄，造成" +
               phys("r_dmg", "r_ratio") + "物理伤害、" + R + "减速" + E + "并降低{r_shred}%护甲。" + A + "{r_win}秒" + E + "内每次参与击杀都可再扑一次，"
               "获得" + grn("r_sh", "r_sh_r") + "护盾。",
    },
    "zh-hant": {
        "attack": "【附加包】撲咬目標。" + O + "百犬齊聚" + E + "：{pack_n}隻夥伴跟著她自己追咬敵人（每口" + phys("hound_hit", "hound_ad") +
                  "，可被擊殺，陣亡" + A + "{respawn}秒" + E + "後再來），和她一起陣亡。",
        "skill": "【附加包】擲出匕首，造成" + phys("q_dmg", "q_ratio") + "物理傷害並流血" + A + "{q_bleed}秒" + E + "。" + A +
                 "{q_win}秒" + E + "內下次普攻擲出第二把匕首，造成" + phys("q2_dmg", "q2_ratio") + "，目標每損失1%生命多{q_exec_pct}%傷害，"
                 "命中英雄回復" + grn("q_heal", "q_heal_r") + "生命。",
        "ult": "【附加包】" + O + "獵犬嚎殺" + E + "：" + A + "{r_imm}秒" + E + "無法被選取，犬群加倍、攻擊力+{roar_ad}%、移速+{roar_ms}%；隨後撲向敵方英雄，造成" +
               phys("r_dmg", "r_ratio") + "物理傷害、" + R + "緩速" + E + "並降低{r_shred}%護甲。" + A + "{r_win}秒" + E + "內每次參與擊殺都可再撲一次，"
               "獲得" + grn("r_sh", "r_sh_r") + "護盾。",
    },
    "en": {
        "attack": "[Add-on] A lunging bite. " + O + "We Are More" + E + ": {pack_n} packmates follow her and hunt on their own (" +
                  phys("hound_hit", "hound_ad") + " a bite; they can be killed and come back " + A + "{respawn}s" + E + " later) and die "
                  "with her.",
        "skill": "[Add-on] Hurls a dagger for " + phys("q_dmg", "q_ratio") + " physical damage and a bleed over " + A + "{q_bleed}s" + E +
                 ". Within " + A + "{q_win}s" + E + " her next attack hurls the second dagger for " +
                 phys("q2_dmg", "q2_ratio") + ", {q_exec_pct}% more for every 1% of health the target has lost, healing her " +
                 grn("q_heal", "q_heal_r") + " on a champion.",
        "ult": "[Add-on] " + O + "The Call of the Pack" + E + ": untargetable for " + A + "{r_imm}s" + E + ", a pack twice as big, "
               "+{roar_ad}% attack and +{roar_ms}% move speed. Then she pounces on an enemy champion for " + phys("r_dmg", "r_ratio") +
               " physical damage, a " + R + "slow" + E + " and -{r_shred}% armour. Every takedown within " + A + "{r_win}s" + E +
               " lets her pounce again with a " + grn("r_sh", "r_sh_r") + " shield.",
    },
    "ko": {
        "attack": "[확장] 덤벼들어 물어뜯음. " + O + "우리는 무리다" + E + ": 동료 {pack_n}마리가 따라다니며 스스로 적을 물어뜯음(한 번에 " +
                  phys("hound_hit", "hound_ad") + ", 처치 가능, " + A + "{respawn}초" + E + " 뒤 다시 옴), 그녀와 함께 쓰러짐.",
        "skill": "[확장] 단검을 던져 " + phys("q_dmg", "q_ratio") + " 물리 피해와 " + A + "{q_bleed}초" + E + " 출혈. " +
                 A + "{q_win}초" + E + " 안에 다음 공격은 두 번째 단검으로 " + phys("q2_dmg", "q2_ratio") + ", 대상이 잃은 체력 1%당 피해 "
                 "{q_exec_pct}% 증가, 챔피언 적중 시 체력 " + grn("q_heal", "q_heal_r") + " 회복.",
        "ult": "[확장] " + O + "무리의 부름" + E + ": " + A + "{r_imm}초" + E + " 대상 지정 불가, 무리 두 배, 공격력 +{roar_ad}%, 이동 속도 +{roar_ms}%. "
               "이어서 적 챔피언에게 덮쳐 " + phys("r_dmg", "r_ratio") + " 물리 피해, " + R + "둔화" + E + ", 방어력 -{r_shred}%. " + A +
               "{r_win}초" + E + " 안에 처치 관여할 때마다 " + grn("r_sh", "r_sh_r") + " 보호막과 함께 다시 덮침.",
    },
    "ja": {
        "attack": "【拡張】飛びかかって噛みつく。" + O + "我らは群れ" + E + "：仲間{pack_n}匹が付き従い自ら敵に噛みつく（1回" +
                  phys("hound_hit", "hound_ad") + "、倒せる、" + A + "{respawn}秒" + E + "後に戻る）、彼女と共に倒れる。",
        "skill": "【拡張】短剣を投げ" + phys("q_dmg", "q_ratio") + "の物理ダメージと" + A + "{q_bleed}秒" + E + "の出血。" +
                 A + "{q_win}秒" + E + "以内の次の攻撃で二本目を投げ" + phys("q2_dmg", "q2_ratio") + "、対象の失った体力1%ごとに"
                 "{q_exec_pct}%増、チャンピオンなら体力" + grn("q_heal", "q_heal_r") + "回復。",
        "ult": "【拡張】" + O + "群れの呼び声" + E + "：" + A + "{r_imm}秒" + E + "対象指定不可、群れが倍、攻撃力+{roar_ad}%、移動速度+{roar_ms}%。"
               "続けて敵チャンピオンに飛びかかり" + phys("r_dmg", "r_ratio") + "の物理ダメージ、" + R + "スロウ" + E + "、物防-{r_shred}%。" + A +
               "{r_win}秒" + E + "以内のキル関与ごとに" + grn("r_sh", "r_sh_r") + "のシールドでもう一度。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def consts():
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    got = {m.group(1): int(m.group(2).replace("_", "")) for m in
           re.finditer(r"pub const ([A-Z0-9_]+): usize = ([0-9_]+);", src)}
    return {name: got.get(name) for name in CONSTS}


def units_consts():
    """src/lib.rs's `pub const NAME: usize = <n>;` and `pub const NAME: &str = "...";` (all of them)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    out = {m.group(1): int(m.group(2).replace("_", "")) for m in re.finditer(r"pub const ([A-Z0-9_]+): usize = ([0-9_]+);", src)}
    out.update({m.group(1): m.group(2) for m in re.finditer(r'pub const ([A-Z0-9_]+): &str = "([^"]*)";', src)})
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
    """0.2.0: the pack drawn on her and its bites play only without SOLO (her packmates as units); the units' numbers
    checked against P and the unit sheet."""
    act, lands = attack_ticks(c["PACKMATE"])
    want = {"HOUND_ACT": act, "HOUND_LANDS": lands}
    wrong = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    if wrong or 2 * c["HOUND_HIT"] != p["pk_dmg"] or 2 * c["HOUND_HIT_AD"] != p["pk_ratio"]:
        sys.exit(f"the packmates' numbers differ from src/lib.rs (lib, sheet): {wrong}; each bite is half the pack's "
                 f"({p['pk_dmg']} + {p['pk_ratio']}%)")
    names = {x["buff_state"]["name"] for x in walk(champion) if isinstance(x.get("buff_state"), dict)}
    names |= {x.get("buff_name") for x in walk(champion) if x.get("type") == "SwitchByBuff"}
    if c["SOLO"] in names or any(str(b).startswith(c["H_UID"]) for b in names):
        sys.exit("the main pack's Naafiri already uses one of the add-on's buff names: update src/lib.rs")

    def unless_solo(o):
        return {"type": "SwitchByBuff", "buff_name": c["SOLO"], "effect_buff": {"type": "Combine", "effects": []}, "effect_none": o}
    counts = {}
    for name, n in (("league_naafiri_pk_c", 9), ("league_naafiri_pk_m", 9), ("league_naafiri_q_leap", 3)):
        found = []
        champion = replace(champion, lambda o, name=name: o.get("type") == "TargetProjectile" and o.get("name") == name,
                           unless_solo, found)
        counts[name] = len(found)
        if len(found) != n:
            sys.exit(f"{name}: {len(found)} found, not {n} (the main pack changed): update this script")
    leap = json.dumps(champion)
    if "league_naafiri_pk_ride" not in leap:
        sys.exit("the riding pack (league_naafiri_pk_ride) is gone from the copy: update this script")
    return champion


def main():
    check = "--check" in sys.argv[1:]
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_naafiri differs from build_naafiri.P: rebuild it first")
    wrong = {name: (got, p[CONSTS[name]]) for name, got in consts().items() if got != p[CONSTS[name]]}
    if wrong:
        sys.exit("src/lib.rs constants differ from build_naafiri.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":pack":
        sys.exit("the copy has no league_naafiri:pack passive: update this script")
    text = json.dumps(champion)
    if '"league_naafiri_r_alive"' in text or '"league_naafiri:q2"' not in text:
        sys.exit("the copy still carries the takedown window or lacks the execute: update this script")
    c = units_consts()
    champion = units(champion, p, c)
    for slot in ("attack", "skill", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), q_exec_pct=f"{p['q_exec'] / 100:g}", pack_n=c["PACK_N"], hound_hit=c["HOUND_HIT"],
                  hound_ad=c["HOUND_HIT_AD"], respawn=setup.secs(c["HOUND_RESPAWN"]))
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in NATIVE.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
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
        stale = [os.path.relpath(path, ROOT) for path, text in files.items() if not os.path.isfile(lp(path))
                 or open(lp(path), encoding="utf-8", newline="").read().replace("\r\n", "\n") != text]
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
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
