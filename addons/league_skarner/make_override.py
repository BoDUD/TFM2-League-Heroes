"""Build the add-on's copy of Skarner from the main pack (Quaking per champion, the wall stun, Impale's first three dragged).

    python addons/league_skarner/make_override.py [--draft] [--check]

Rebuilds Skarner with tools/kit/build_skarner.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_skarner.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
constants in src/lib.rs are P's numbers, and writes addons/league_skarner/override/league_skarner.data_champion and
.../text/champion.i18n: the build with native=1 (build_skarner.py's docstring) -
  * passive = league_skarner:sovereign (params build_skarner.NATIVE_KEYS);
  * Quaking's climb = league_skarner:quake (Impale's native quakes its own champions), no ladder on him; E's contact =
    league_skarner:impact (no Knockback, no slam of its own); Impale's hit = league_skarner:impale (no damage, Stun or
    Grab of its own);
  * the slots' tooltips (keys of the add-on's own id) say the League rules, so the tooltip in game shows whether the
    override took.
Every other champion stays untouched. Run it again whenever the main pack's Skarner changes.
--draft: only the copy, without the main-pack check and the texts (before tools/kit/setup_skarner.py exists).
--check: write nothing, exit 1 when the files on disk are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_skarner")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_skarner as kit  # noqa: E402

MOD_ID = "league_skarner"
HERO = "league_skarner"
KEYS = kit.NATIVE_KEYS
SLOTS = ("attack", "skill", "skill2", "ult")   # every slot's tooltip says the add-on (Q's rules are the main pack's)


def native_texts(p):
    """lang -> {slot: text}: the main pack's texts with the add-on's rules (setup_skarner's helpers and numbers)."""
    import setup_skarner as setup  # noqa: E402  (the main pack's texts; exists from the integration on)
    phys, t, n, cc = setup.phys, setup.t, setup.n, setup.cc
    main = setup.TEXT
    v = dict(setup.values(p), e_wall_dmg=p["e_wall_dmg"], e_wall_hp=p["e_wall_hp"], r_n=p["r_n"])
    ewall = lambda: phys("e_wall_dmg", "e_ratio")      # the wall's blow (+ max health in each text)
    T = {
        "zh-hans": {
            "attack": "【附加包】毒刺扎击。" + n("战栗") + "：普攻、巨石、毒刺在敌方英雄身上叠层，满{p_n}层它" + t("{p_t}秒") +
                      "内每秒受到最大生命{p_pct}%魔法伤害。" + n("震地壁垒") + "：冲锋停下时得" + phys("w_sh", "w_sh_r") + "护盾" +
                      t("{w_sh_t}秒") + "，震伤周围" + phys("w_dmg", "w_ratio") + "、" + cc("减速") + "{w_slow}%。",
            "skill": "【附加包】" + main["zh-hans"]["skill"],
            "skill2": "【附加包】冲锋时穿过地形，撞上敌方英雄后拖着走；拖到墙上才造成" + ewall() + "+最大生命{e_wall_hp}%物理伤害并" +
                      cc("晕眩") + t("{e_stun}秒") + "。",
            "ult": "【附加包】三根毒刺往前扎：最先碰到的{r_n}个敌方英雄受到" + phys("r_dmg", "r_ratio") + "魔法伤害，被" + cc("压制") +
                   t("{r_sup}秒") + "并拖到身边跟着走；扎中后移速+{r_ms}%" + t("{r_ms_t}秒") + "。",
        },
        "zh-hant": {
            "attack": "【附加包】毒刺扎擊。" + n("震動餘波") + "：普攻、巨石、毒刺在敵方英雄身上疊層，滿{p_n}層它" + t("{p_t}秒") +
                      "內每秒受到最大生命{p_pct}%魔法傷害。" + n("壁壘波動") + "：衝鋒停下時得" + phys("w_sh", "w_sh_r") + "護盾" +
                      t("{w_sh_t}秒") + "，震傷周圍" + phys("w_dmg", "w_ratio") + "、" + cc("緩速") + "{w_slow}%。",
            "skill": "【附加包】" + main["zh-hant"]["skill"],
            "skill2": "【附加包】衝鋒時穿過地形，撞上敵方英雄後拖著走；拖到牆上才造成" + ewall() + "+最大生命{e_wall_hp}%物理傷害並" +
                      cc("暈眩") + t("{e_stun}秒") + "。",
            "ult": "【附加包】三根毒刺往前扎：最先碰到的{r_n}個敵方英雄受到" + phys("r_dmg", "r_ratio") + "魔法傷害，被" + cc("壓制") +
                   t("{r_sup}秒") + "並拖到身邊跟著走；扎中後移速+{r_ms}%" + t("{r_ms_t}秒") + "。",
        },
        "en": {
            "attack": "[Add-on] Stinger strikes. " + n("Threads of Vibration") + ": his attacks, the boulder and Impale stack "
                      "Quaking on each enemy champion; at {p_n} it takes {p_pct}% max health as magic damage a second for " +
                      t("{p_t}s") + ". " + n("Seismic Bastion") + ": when his charge stops he gains a " + phys("w_sh", "w_sh_r") +
                      " shield for " + t("{w_sh_t}s") + " and quakes the ground for " + phys("w_dmg", "w_ratio") + ", " +
                      cc("slowing") + " {w_slow}%.",
            "skill": "[Add-on] " + main["en"]["skill"],
            "skill2": "[Add-on] Charges through terrain at an enemy champion and carries it along; only slammed into a wall "
                      "it takes " + ewall() + " + {e_wall_hp}% max health physical damage and is " + cc("stunned") + " for " +
                      t("{e_stun}s") + ".",
            "ult": "[Add-on] His three tails lash forward: the first {r_n} enemy champions hit take " + phys("r_dmg", "r_ratio") +
                   " magic damage, are " + cc("suppressed") + " for " + t("{r_sup}s") + " and dragged along beside him; on a hit "
                   "he gains {r_ms}% move speed for " + t("{r_ms_t}s") + ".",
        },
        "ko": {
            "attack": "[확장] 독침 공격. " + n("진동의 가닥") + ": 기본 공격, 바위, 꿰뚫기가 적 챔피언마다 진동 중첩, {p_n}중첩이면 " +
                      t("{p_t}초") + " 동안 매초 최대 체력 {p_pct}% 마법 피해. " + n("대지의 수호자") + ": 돌진이 멈추면 " +
                      phys("w_sh", "w_sh_r") + " 보호막 " + t("{w_sh_t}초") + ", 주변에 " + phys("w_dmg", "w_ratio") + " 피해, "
                      "{w_slow}% " + cc("둔화") + ".",
            "skill": "[확장] " + main["ko"]["skill"],
            "skill2": "[확장] 지형을 통과해 적 챔피언에게 돌진해 끌고 감; 벽에 부딪혀야 " + ewall() + " + 최대 체력 {e_wall_hp}% 물리 "
                      "피해와 " + t("{e_stun}초") + " " + cc("기절") + ".",
            "ult": "[확장] 세 꼬리로 앞을 꿰뚫음: 처음 맞은 적 챔피언 {r_n}명에게 " + phys("r_dmg", "r_ratio") + " 마법 피해, " +
                   t("{r_sup}초") + " " + cc("제압") + "하고 곁으로 끌고 다님; 적중하면 이동 속도 +{r_ms}% " + t("{r_ms_t}초") + ".",
        },
        "ja": {
            "attack": "【拡張】毒針で攻撃。" + n("響振動") + "：通常攻撃・岩・インペイルが敵チャンピオンごとに振動を付与、{p_n}スタックで" +
                      t("{p_t}秒") + "間毎秒最大体力{p_pct}%の魔法ダメージ。" + n("激震の砦") + "：突進が止まるとシールド" +
                      phys("w_sh", "w_sh_r") + "を" + t("{w_sh_t}秒") + "得て周囲に" + phys("w_dmg", "w_ratio") + "、{w_slow}%" +
                      cc("スロウ") + "。",
            "skill": "【拡張】" + main["ja"]["skill"],
            "skill2": "【拡張】地形を抜けて敵チャンピオンに突進して引きずる；壁にぶつけた時だけ" + ewall() + "+最大体力{e_wall_hp}%の"
                      "物理ダメージと" + t("{e_stun}秒") + cc("スタン") + "。",
            "ult": "【拡張】三本の尾で前方を貫く：最初の{r_n}体の敵チャンピオンに" + phys("r_dmg", "r_ratio") + "の魔法ダメージ、" +
                   t("{r_sup}秒") + cc("サプレッション") + "して引きずる；命中すると移動速度+{r_ms}%を" + t("{r_ms_t}秒") + "。",
        },
    }
    out = {lang: {k: tx.format(**v) for k, tx in d.items()} for lang, d in T.items()}
    long = {f"{lang}.{k}": setup.shown_length(tx) for lang, d in T.items() for k, tx in d.items()
            if setup.shown_length(tx) > setup.TOOLTIP_MAX.get(lang, 10 ** 6)}
    if long:
        sys.exit("tooltip too long for the details panel: %s" % long)
    print({f"{lang}.{k}": f"{setup.shown_length(tx)}/{setup.TOOLTIP_MAX[lang]}" for lang, d in T.items()
           for k, tx in d.items()})
    return out


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def check_consts(p):
    """src/lib.rs's constants (P_N, E_STUN, ...) hold P's numbers."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    got = {k.lower(): int(v.replace("_", "")) for k, v in re.findall(r"pub const ([A-Z_0-9]+): usize = ([0-9_]+);", src)}
    bad = {k: (got.get(k), p[k]) for k in KEYS if got.get(k) != p[k]}
    if bad:
        sys.exit(f"src/lib.rs constants differ from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_consts(p)
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":sovereign":
        sys.exit("the copy does not call the add-on: update this script")
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(kit.build(p)) != shipped:
            sys.exit("the main pack's league_skarner differs from build_skarner.P: rebuild it first")
        for slot in SLOTS:
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        texts = native_texts(p)
        with open(lp(os.path.join(ROOT, "league", "text", "champion.i18n")), encoding="utf-8-sig") as f:
            main_text = json.load(f)
        missing = set(main_text) - set(texts)
        if missing:
            sys.exit("no add-on text for %s" % sorted(missing))
        out[os.path.join(ADDON, "text", "champion.i18n")] = dumps_main(
            {lang: {"description": {MOD_ID: texts[lang]}} for lang in main_text})
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
