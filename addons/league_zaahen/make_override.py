"""Build the add-on's copy of Zaahen from the main pack (Determination counted per hit, the revive, Aureate Rush's own
slot, the glaive's heal by maximum health).

    python addons/league_zaahen/make_override.py [--draft] [--check]

Rebuilds Zaahen with tools/kit/build_zaahen.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_zaahen.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_zaahen/override/league_zaahen.data_champion and
.../text/champion.i18n: the build with native=1 (build_zaahen.py's docstring) -
  * passive = league_zaahen:darkin (params build_zaahen.NATIVE_KEYS);
  * no Determination ladder (the add-on counts the stacks and adds `det` / `full`, raises `fill`); no stand-in shield;
    no spin in W (the add-on's own E dashes and raises `e_go`: the data spins as skill3); Q's slashes mark `q_mark`
    (no flat heal); the revive's picture rv_rise among the views;
  * the attack's and the ult's tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game shows
    whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Zaahen changes.
--draft: only the copy, without the main-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_zaahen")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_zaahen as kit  # noqa: E402

MOD_ID = "league_zaahen"
HERO = "league_zaahen"
KEYS = kit.NATIVE_KEYS
SLOTS = ("attack", "skill", "skill2", "ult")   # every slot's rules differ from the main pack's
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import setup_zaahen as setup  # noqa: E402

phys, heal, t, n, cc = setup.phys, setup.heal, setup.t, setup.n, setup.cc
# lang -> the add-on's texts for every slot (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】长刀横扫。" + n("不落之志") + "：每次伤害打中英雄叠1层果决（攻击力+{det_pct}%，最多{det_n}层，叠满翻倍）；"
                  "叠满时受到致命伤害就倒下：" + t("{rv_rise}秒") + "无敌、选不中，回到最大生命{rv_hp}%再展翼站起，果决叠满（每" +
                  t("{rv_cd}秒") + "一次）。",
        "skill": "【附加包】两连斩，每斩" + phys("q_dmg", "q_ratio") + "物理伤害、打中英雄回复最大生命{q_hp}%（别的单位一半）。" +
                 t("{q_win}秒") + "内再按：上挑造成" + phys("q3_dmg", "q3_ratio") + "并" + cc("击飞") + t("{q_air}秒") + "。",
        "skill2": "【附加包】刺出长刀：" + phys("w_dmg", "w_ratio") + "物理伤害、" + cc("晕眩") + t("{w_stun}秒") + "并拽回身边。" +
                  n("赤金突袭") + "（每" + t("{e_cd}秒") + "）：冲向英雄绕身斩" + phys("e_dmg", "e_ratio") + "，外圈+{e_out}%并加最大生命"
                  "{e_pct}%魔法伤害。",
        "ult": "【附加包】展翼升空（免控、受到伤害-{r_dr}%），冲向敌方英雄插刀落地：周围敌人受到" + phys("r_dmg", "r_ratio") +
               "物理伤害，每打中一个英雄回复" + heal("r_heal", "r_heal_r") + "。被动：攻击无视{r_pen}%护甲。",
    },
    "zh-hant": {
        "attack": "【附加包】長刀橫掃。" + n("邪心修真") + "：每次傷害打中英雄疊1層決心（攻擊力+{det_pct}%，最多{det_n}層，疊滿翻倍）；"
                  "疊滿時受到致命傷害就倒下：" + t("{rv_rise}秒") + "無敵、選不中，回到最大生命{rv_hp}%再展翼站起，決心疊滿（每" +
                  t("{rv_cd}秒") + "一次）。",
        "skill": "【附加包】兩連斬，每斬" + phys("q_dmg", "q_ratio") + "物理傷害、打中英雄回復最大生命{q_hp}%（其他單位一半）。" +
                 t("{q_win}秒") + "內再按：上挑造成" + phys("q3_dmg", "q3_ratio") + "並" + cc("擊飛") + t("{q_air}秒") + "。",
        "skill2": "【附加包】刺出長刀：" + phys("w_dmg", "w_ratio") + "物理傷害、" + cc("暈眩") + t("{w_stun}秒") + "並拽回身邊。" +
                  n("偃月天衝") + "（每" + t("{e_cd}秒") + "）：衝向英雄繞身斬" + phys("e_dmg", "e_ratio") + "，外圈+{e_out}%並加最大生命"
                  "{e_pct}%魔法傷害。",
        "ult": "【附加包】展翼升空（免控、受到傷害-{r_dr}%），衝向敵方英雄插刀落地：周圍敵人受到" + phys("r_dmg", "r_ratio") +
               "物理傷害，每打中一個英雄回復" + heal("r_heal", "r_heal_r") + "。被動：攻擊無視{r_pen}%護甲。",
    },
    "en": {
        "attack": "[Add-on] Glaive sweeps. " + n("Cultivation of War") + ": every damage instance on a champion stacks "
                  "Determination (+{det_pct}% attack each, up to {det_n}, doubled when full); full, lethal damage fells him "
                  "instead: " + t("{rv_rise}s") + " invulnerable and untargetable, back to {rv_hp}% max health, he rises on "
                  "his wings with Determination full (once every " + t("{rv_cd}s") + ").",
        "skill": "[Add-on] Slashes twice, " + phys("q_dmg", "q_ratio") + " physical damage each, healing {q_hp}% max health "
                 "per slash on a champion (half on other units). Recast within " + t("{q_win}s") + ": an uppercut for " +
                 phys("q3_dmg", "q3_ratio") + " that " + cc("knocks up") + " for " + t("{q_air}s") + ".",
        "skill2": "[Add-on] Stabs the glaive forward: " + phys("w_dmg", "w_ratio") + " physical damage, " + cc("stuns") +
                  " for " + t("{w_stun}s") + " and pulls to him. " + n("Aureate Rush") + " (every " + t("{e_cd}s") +
                  "): he dashes at a champion and spins for " + phys("e_dmg", "e_ratio") + ", the outer edge {e_out}% more "
                  "and {e_pct}% max health magic damage.",
        "ult": "[Add-on] Rises on his wings (crowd-control immune, {r_dr}% less damage taken) and dives on an enemy "
               "champion, driving the glaive into the ground: enemies around take " + phys("r_dmg", "r_ratio") +
               " physical damage; he heals " + heal("r_heal", "r_heal_r") + " per champion hit. Passive: his hits ignore "
               "{r_pen}% armour.",
    },
    "ko": {
        "attack": "[확장] 글레이브 휩쓸기. " + n("전쟁 단련") + ": 챔피언에게 피해를 줄 때마다 결의 1중첩(공격력 +{det_pct}%, 최대 "
                  "{det_n}, 최대면 2배); 최대일 때 치명적인 피해를 받으면 쓰러져 " + t("{rv_rise}초") + " 무적·대상 지정 불가, "
                  "최대 체력 {rv_hp}%로 날개를 펴고 일어나 결의 최대(" + t("{rv_cd}초") + "마다).",
        "skill": "[확장] 두 번 벰: 한 번에 " + phys("q_dmg", "q_ratio") + " 물리 피해, 챔피언 적중 시 최대 체력 {q_hp}% 회복(다른 "
                 "유닛은 절반). " + t("{q_win}초") + " 안에 재사용: 올려 베기로 " + phys("q3_dmg", "q3_ratio") + " 피해와 " +
                 t("{q_air}초") + " " + cc("에어본") + ".",
        "skill2": "[확장] 글레이브로 찌름: " + phys("w_dmg", "w_ratio") + " 물리 피해, " + t("{w_stun}초") + " " + cc("기절") +
                  ", 끌어당김. " + n("찬란한 쇄도") + "(" + t("{e_cd}초") + "마다): 챔피언에게 돌진해 " + phys("e_dmg", "e_ratio") +
                  " 회전 베기, 바깥 가장자리 {e_out}% 추가와 최대 체력 {e_pct}% 마법 피해.",
        "ult": "[확장] 날개를 펴고 솟아올라(군중 제어 면역, 받는 피해 -{r_dr}%) 적 챔피언에게 내리꽂음: 주변 적에게 " +
               phys("r_dmg", "r_ratio") + " 물리 피해, 챔피언 적중마다 " + heal("r_heal", "r_heal_r") + " 회복. 기본 지속 효과: "
               "방어구 {r_pen}% 관통.",
    },
    "ja": {
        "attack": "【拡張】グレイヴで薙ぎ払う。" + n("戦威修養") + "：チャンピオンへのダメージ毎に決意1スタック（攻撃力+{det_pct}%、最大"
                  "{det_n}、最大で2倍）；最大時に致命傷を受けると倒れ" + t("{rv_rise}秒") + "無敵・対象不可、最大体力{rv_hp}%で翼を広げ"
                  "立ち上がり決意最大（" + t("{rv_cd}秒") + "毎）。",
        "skill": "【拡張】2回斬る：1回" + phys("q_dmg", "q_ratio") + "の物理ダメージ、チャンピオン命中で最大体力{q_hp}%回復（他は半分）。" +
                 t("{q_win}秒") + "内に再使用：斬り上げで" + phys("q3_dmg", "q3_ratio") + "と" + t("{q_air}秒") + cc("ノックアップ") +
                 "。",
        "skill2": "【拡張】グレイヴを突き出す：" + phys("w_dmg", "w_ratio") + "の物理ダメージ、" + t("{w_stun}秒") + cc("スタン") +
                  "して引き寄せる。" + n("絢爛たる進撃") + "（" + t("{e_cd}秒") + "毎）：チャンピオンへ突進し回転斬り" +
                  phys("e_dmg", "e_ratio") + "、外縁は{e_out}%増と最大体力{e_pct}%の魔法ダメージ。",
        "ult": "【拡張】翼を広げて舞い上がり（CC無効、被ダメージ-{r_dr}%）、敵チャンピオンへ降下して突き立てる：周囲の敵に" +
               phys("r_dmg", "r_ratio") + "の物理ダメージ、チャンピオン1体ごとに" + heal("r_heal", "r_heal_r") + "回復。"
               "自動効果：物理防御{r_pen}%貫通。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (det_n: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":darkin":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_zaahen differs from build_zaahen.P: rebuild it first")
        for slot in SLOTS:
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = dict(setup.values(p), det_pct=p["det_pct"], rv_rise=setup.secs(p["rv_rise"]), rv_hp=p["rv_hp"],
                      q_hp=p["q_hp"], e_cd=setup.secs(p["e_cd"]), e_out=p["e_out"], e_pct=p["e_pct"])
        texts = {lang: {k: tx.format(**values) for k, tx in d.items()} for lang, d in NATIVE.items()}
        long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in NATIVE.items() for k, tx in d.items()
                if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
        if long:
            sys.exit("tooltip too long for the details panel: %s" % long)
        with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
            main_text = json.load(f)
        missing = set(main_text) - set(texts)
        if missing:
            sys.exit("no add-on text for %s" % sorted(missing))
        out[os.path.join(ADDON, "text", "champion.i18n")] = dumps_main(
            {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text})
        print({f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}" for lang, d in NATIVE.items()
               for k, tx in d.items()})
    out[os.path.join(ADDON, "override", HERO + ".data_champion")] = dumps_main(champion)
    return out, champion


def main():
    draft = "--draft" in sys.argv[1:]
    out, champion = files(draft)
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
    print("(draft)" if draft else json.dumps(champion["passive"]["params"]))


if __name__ == "__main__":
    main()
