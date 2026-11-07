"""Build the add-on's copy of Qiyana from the main pack (League V26.21's kit: W Terrashape of her own from the terrain,
Edge of Ixtal's line and thrown blade, Royal Privilege per enemy, Supreme Display of Talent by the terrain).

    python addons/league_qiyana/make_override.py [--check]

Rebuilds Qiyana with tools/kit/build_qiyana.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_qiyana.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's `params!` are P's numbers (build_qiyana.NATIVE_PARAMS, the same keys), and writes
addons/league_qiyana/override/league_qiyana.data_champion and .../text/champion.i18n: the build with native=1 -
  * everything of the main pack's kit but what strikes: Q's hit is the Native league_qiyana:q (the line, or the thrown
    blade and its blast with the element's effect), E's landing league_qiyana:e (the hit if the target is still in reach,
    then W when it is ready), the attack's on-hit league_qiyana:hit (the enchant's magic, Royal Privilege per enemy), R
    league_qiyana:r (the windblast and the shockwave along the terrain); Q's range is Elemental Wrath's (q2_range);
  * passive = league_qiyana:empress (it keeps the numbers for the natives, passive.params, and runs W Terrashape, the
    grass field and the element she respawns with);
  * the four tooltips (description.league_qiyana.<slot>, keys of the add-on's own id) say what the add-on plays, so the
    tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Qiyana changes. --check writes nothing and
fails when a file would change.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_qiyana")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_qiyana as kit  # noqa: E402
import range_buffs  # noqa: E402  (league.dll's league:range)
import setup_qiyana as setup  # noqa: E402

MOD_ID = "league_qiyana"
HERO = "league_qiyana"
O, M, A, R, E = setup.O, setup.M, setup.A, setup.R, setup.E
phys, mag = setup.phys, setup.mag
NATIVES = ("q", "e", "hit", "r")
# lang -> the add-on's attack, skill, skill2 and ult texts
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】挥环攻击。" + O + "凌人贵气" + E + "：普攻和Q、E对每个敌人" + A + "{rp_rest}秒" + E + "内的首次命中额外造成" +
                  phys("rp_dmg", "rp_ratio") + "物理伤害，换来别的元素时重置。附有元素时攻速+{w_as}%、攻击距离+{w_range}，普攻和Q、E额外"
                  "造成" + mag("w_on", "w_on_r") + "魔法伤害。",
        "skill": "【附加包】挥环斩向身前一条直线，造成" + phys("q_dmg", "q_ratio") + "物理伤害，第一个之后{q_far}%，野怪{q_mon}%。附有元素时"
                 "掷出环刃在第一个敌人处炸开：河流" + R + "定身" + E + A + "{q_root}秒" + E + "后减速{q_slow}%；岩石对生命低于{q_exec}%的多"
                 "{q_rock_pct}%；草丛留下草地，在里面伪装、加速{q_ms}%。",
        "skill2": "【附加包】突进到敌人身上，落地时他还在身边才造成" + phys("e_dmg", "e_ratio") + "物理伤害。" + O + "方圆塑令" + E +
                  "（自动，" + A + "{w_cd}秒" + E + "）：冲向身边的草丛、墙或河，拿到对应的元素并刷新以绪塔尔之锋；复活时带着岩石。",
        "ult": "【附加包】放出狂风" + R + "击退" + E + "路上的敌人，碰到墙就停；冲击波沿路过的草丛、河道和那面墙的边扩散，造成" +
               phys("r_dmg", "r_ratio") + "物理伤害和最大生命{r_hp}%，" + R + "晕眩" + E + A + "{r_stun_min}～{r_stun_max}秒" + E +
               "（越近越久）。",
    },
    "zh-hant": {
        "attack": "【附加包】揮環攻擊。" + O + "皇家特權" + E + "：普攻和Q、E對每個敵人" + A + "{rp_rest}秒" + E + "內的首次命中額外造成" +
                  phys("rp_dmg", "rp_ratio") + "物理傷害，換來別的元素時重置。附有元素時攻速+{w_as}%、攻擊距離+{w_range}，普攻和Q、E額外"
                  "造成" + mag("w_on", "w_on_r") + "魔法傷害。",
        "skill": "【附加包】揮環斬向身前一條直線，造成" + phys("q_dmg", "q_ratio") + "物理傷害，第一個之後{q_far}%，野怪{q_mon}%。附有元素時"
                 "擲出環刃在第一個敵人處炸開：河流" + R + "定身" + E + A + "{q_root}秒" + E + "後緩速{q_slow}%；岩石對生命低於{q_exec}%的多"
                 "{q_rock_pct}%；草叢留下草地，在裡面偽裝、加速{q_ms}%。",
        "skill2": "【附加包】突進到敵人身上，落地時他還在身邊才造成" + phys("e_dmg", "e_ratio") + "物理傷害。" + O + "元素之形" + E +
                  "（自動，" + A + "{w_cd}秒" + E + "）：衝向身邊的草叢、牆或河，拿到對應的元素並刷新伊克斯塔爾迴旋刀；復活時帶著岩石。",
        "ult": "【附加包】放出狂風" + R + "擊退" + E + "路上的敵人，碰到牆就停；衝擊波沿路過的草叢、河道和那面牆的邊擴散，造成" +
               phys("r_dmg", "r_ratio") + "物理傷害和最大生命{r_hp}%，" + R + "暈眩" + E + A + "{r_stun_min}～{r_stun_max}秒" + E +
               "（越近越久）。",
    },
    "en": {
        "attack": "[Add-on] A swing of her ring blade. " + O + "Royal Privilege" + E + ": her first attack, Q or E hit on each enemy "
                  "within " + A + "{rp_rest}s" + E + " deals " + phys("rp_dmg", "rp_ratio") + " physical damage more; another element "
                  "resets it. While her ring holds an element she has +{w_as}% attack speed and +{w_range} range, and her attacks, Q "
                  "and E deal " + mag("w_on", "w_on_r") + " magic damage more.",
        "skill": "[Add-on] Slashes a line before her for " + phys("q_dmg", "q_ratio") + " physical damage ({q_far}% beyond the first, "
                 "{q_mon}% to monsters). With an element she hurls the ring, bursting on the first enemy: river " + R + "roots" + E +
                 " " + A + "{q_root}s" + E + " then slows {q_slow}%; rock deals {q_rock_pct}% more under {q_exec}% health; grass "
                 "leaves a field camouflaging her with +{q_ms}% move speed.",
        "skill2": "[Add-on] Dashes at an enemy for " + phys("e_dmg", "e_ratio") + " physical damage if it is still beside her on "
                  "landing. " + O + "Terrashape" + E + " (by itself, every " + A + "{w_cd}s" + E + "): she dashes to the brush, wall or "
                  "river beside her for its element and refreshes Edge of Ixtal; she respawns holding rock.",
        "ult": "[Add-on] A windblast " + R + "knocks back" + E + " the enemies on its way and stops at the first wall; a shockwave runs "
               "along the brush and river it crossed and that wall's border: " + phys("r_dmg", "r_ratio") + " physical damage plus "
               "{r_hp}% of maximum health, " + R + "stunning" + E + " " + A + "{r_stun_min}-{r_stun_max}s" + E + " (nearer, longer).",
    },
    "ko": {
        "attack": "[확장] 고리 칼날로 공격. " + O + "왕가의 특권" + E + ": 기본 공격·Q·E가 적마다 " + A + "{rp_rest}초" + E + " 안의 첫 적중 시 " +
                  phys("rp_dmg", "rp_ratio") + " 물리 피해 추가, 다른 원소를 얻으면 초기화. 원소가 깃들면 공격 속도 +{w_as}%, 사거리 "
                  "+{w_range}, 기본 공격·Q·E가 " + mag("w_on", "w_on_r") + " 마법 피해 추가.",
        "skill": "[확장] 앞쪽 직선을 베어 " + phys("q_dmg", "q_ratio") + " 물리 피해(첫 대상 이후 {q_far}%, 몬스터 {q_mon}%). 원소가 있으면 "
                 "고리를 던져 첫 적에게서 터짐: 강 " + A + "{q_root}초" + E + " " + R + "속박" + E + " 후 {q_slow}% 둔화, 바위 체력 {q_exec}% "
                 "미만에 {q_rock_pct}% 추가, 풀숲은 위장과 이동 속도 +{q_ms}%의 풀밭.",
        "skill2": "[확장] 적에게 돌진해 착지 때 곁에 있으면 " + phys("e_dmg", "e_ratio") + " 물리 피해. " + O + "대지창조" + E + "(자동, " + A +
                  "{w_cd}초" + E + "): 주변 풀숲·벽·강으로 돌진해 그 원소를 얻고 이쉬탈의 칼날 초기화. 부활 시 바위.",
        "ult": "[확장] 돌풍이 경로의 적을 " + R + "밀쳐내고" + E + " 첫 벽에서 멈춤. 지나간 풀숲·강과 그 벽 가장자리를 따라 충격파: " +
               phys("r_dmg", "r_ratio") + " 물리 피해와 최대 체력 {r_hp}%, " + A + "{r_stun_min}~{r_stun_max}초" + E + " " + R + "기절" +
               E + "(가까울수록 길게).",
    },
    "ja": {
        "attack": "【拡張】リングで攻撃。" + O + "女帝の威風" + E + "：通常攻撃・Q・Eの敵ごと" + A + "{rp_rest}秒" + E + "以内の最初の命中が" +
                  phys("rp_dmg", "rp_ratio") + "の物理ダメージを追加、別のエレメントでリセット。エレメントがある間、攻撃速度+{w_as}%・"
                  "射程+{w_range}、通常攻撃・Q・Eが" + mag("w_on", "w_on_r") + "の魔法ダメージを追加。",
        "skill": "【拡張】前方の直線を薙ぎ" + phys("q_dmg", "q_ratio") + "の物理ダメージ（2体目以降{q_far}%、モンスター{q_mon}%）。エレメント"
                 "があればリングを投げ最初の敵で炸裂：川は" + A + "{q_root}秒" + E + R + "スネア" + E + "後{q_slow}%スロウ、岩は体力"
                 "{q_exec}%未満に{q_rock_pct}%追加、草むらは迷彩と移動速度+{q_ms}%の草地。",
        "skill2": "【拡張】敵へ突進し、着地時に近くにいれば" + phys("e_dmg", "e_ratio") + "の物理ダメージ。" + O + "大地の力" + E + "（自動、" +
                  A + "{w_cd}秒" + E + "）：近くの草むら・壁・川へ突進してそのエレメントを得て、イシュタルの切先を再使用可能に。復活時は岩。",
        "ult": "【拡張】突風で道中の敵を" + R + "ノックバック" + E + "し最初の壁で止まる。通った草むら・川とその壁の縁に衝撃波：" +
               phys("r_dmg", "r_ratio") + "の物理ダメージと最大体力の{r_hp}%、" + A + "{r_stun_min}～{r_stun_max}秒" + E + R + "スタン" +
               E + "（近いほど長い）。",
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
    """`params! { name = value, ... }` in src/lib.rs as {name: value}."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"^params! \{(.*?)^\}", src, re.S | re.M)
    if not m:
        sys.exit("src/lib.rs has no `params! { ... }` block: update this script")
    return {k: int(v.replace("_", "")) for k, v in re.findall(r"(\w+)\s*=\s*([\d_]+)", m.group(1))}


def outputs():
    """({path: text} of everything this script writes, the copy)."""
    p = dict(kit.P)
    with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
        shipped = f.read()
    if dumps_main(kit.build(p)) != shipped:
        sys.exit("the main pack's league_qiyana differs from build_qiyana.P: rebuild it first")
    rust = rust_defaults()
    if set(rust) != set(kit.NATIVE_PARAMS):
        sys.exit("src/lib.rs params! keys differ from build_qiyana.NATIVE_PARAMS: %s" % sorted(set(rust) ^ set(kit.NATIVE_PARAMS)))
    wrong = {k: (v, p[k]) for k, v in rust.items() if v != p[k]}
    if wrong:
        sys.exit("src/lib.rs params! defaults differ from build_qiyana.P (rust, P): %s" % wrong)
    champion = kit.build(dict(p, native=1))
    # the add-on's W lays el_on natively (no AddCasterBuff of it is left in the copy), so the attack carries
    # league:range whatever the data lays (tools/kit/range_buffs.py)
    range_buffs.apply(champion, force=True)
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":empress":
        sys.exit("the copy has no league_qiyana:empress passive: update this script")
    text = json.dumps(champion)
    for ref in NATIVES:
        if f'"{MOD_ID}:{ref}"' not in text:
            sys.exit(f"the copy lacks the Native {MOD_ID}:{ref}: update this script")
    for gone in ("league_qiyana_nx_w", "league_qiyana_rp_cd", "league_qiyana_r_wave_c", f"{MOD_ID}:element", f"{MOD_ID}:rock"):
        if f'"{gone}"' in text:
            sys.exit(f"the copy still carries {gone} (the main pack's element cycle, rest, line or an old native): update this script")
    if champion["skill"]["range"] != p["q2_range"]:
        sys.exit("the copy's Q range is not Elemental Wrath's")
    for slot in ("attack", "skill", "skill2", "ult"):
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = dict(setup.values(p), rp_rest=setup.secs(p["rp_rest"]), q_exec=p["q_exec"], q_rock_pct=p["q_rock_pct"],
                  q_mon=p["q_mon"], w_cd=setup.secs(p["w_cd"]), r_stun_min=setup.secs(p["r_stun_min"]),
                  r_stun_max=setup.secs(p["r_stun_max"]))
    texts = {lang: {k: t.format(**values) for k, t in d.items()} for lang, d in NATIVE.items()}
    long = {f"{lang}.{k}": setup.shown_length(t) for lang, d in NATIVE.items() for k, t in d.items()
            if setup.shown_length(t) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)

    with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
        main_text = json.load(f)
    missing = set(main_text) - set(texts)
    if missing:
        sys.exit("no add-on text for %s" % sorted(missing))
    return {
        os.path.join(ADDON, "override", HERO + ".data_champion"): json.dumps(champion, ensure_ascii=False, indent=2) + "\n",
        os.path.join(ADDON, "text", "champion.i18n"): json.dumps({lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text},
                                                                 ensure_ascii=False, indent=2) + "\n",
    }, champion


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="write nothing; fail when a file would change")
    a = ap.parse_args()
    outs, champion = outputs()
    if a.check:
        stale = []
        for path, text in outs.items():
            try:
                with open(lp(path), encoding="utf-8", newline="") as f:
                    have = f.read().replace("\r\n", "\n")
            except FileNotFoundError:
                have = None
            if have != text:
                stale.append(os.path.relpath(path, ROOT))
        if stale:
            sys.exit("out of date (run addons/league_qiyana/make_override.py): %s" % stale)
        print("league_qiyana copy up to date")
        return
    for path, text in outs.items():
        os.makedirs(lp(os.path.dirname(path)), exist_ok=True)
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print("wrote", ", ".join(os.path.relpath(p, ROOT) for p in outs), "- passive =", champion["passive"]["passive_ref"],
          len(champion["passive"]["params"]), "params")
    print("tooltip lengths", {f"{lang}.{k}": f"{setup.shown_length(t)}/{setup.TOOLTIP_MAX[lang]}"
                              for lang, d in NATIVE.items() for k, t in d.items()})


if __name__ == "__main__":
    main()
