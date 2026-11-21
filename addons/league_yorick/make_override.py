"""Build the add-on's copy of Yorick from the main pack (League's rules the data cannot read: graves from kills and deaths
near him, the real Dark Procession wall, Last Rites by missing health, the haste toward the mist's mark, the Maiden
following him with her bolts and mark; the walkers and the Maiden units of their own).

    python addons/league_yorick/make_override.py [--draft] [--check]

Rebuilds Yorick with tools/kit/build_yorick.py (its parameter table P), checks that the plain build is the main pack's
league/champion/league_yorick.data_champion byte for byte (so the copy never drifts from the shipped kit) and that the
defaults in src/lib.rs's Params are P's numbers, and writes addons/league_yorick/override/league_yorick.data_champion and
.../text/champion.i18n: the build with native=1 (0.3.0: build_yorick.py writes every native change itself - the asks,
the flags, the riding pictures behind K_UNIT / M_UNIT, no data heal, no data haste, the wall's W_ASK / W_UP; see its
docstring). This script checks the copy against src/lib.rs: the units' numbers (WALK_*, LEAP_*, MAID_*, K_N, R_N ...)
against P and the unit sheets' attack frames, every name the natives read or lay present in the copy (and none of the
add-on's own in the main pack), the pictures and sounds the natives play among the kit's - change the main pack and this
script stops until lib.rs follows. The attack's, Q's, E's and R's tooltips (keys of the add-on's own id) say the League
rules, so the tooltip in game shows whether the override took.
Every other champion stays untouched. Run it again whenever the main pack's Yorick changes.
--draft: only the copy, without the main-pack check and the texts. --check: write nothing, exit 1 when the files on disk
are not what this would write (the CI's check).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_yorick")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_yorick as kit  # noqa: E402
import setup_yorick as setup  # noqa: E402

MOD_ID = "league_yorick"
HERO = "league_yorick"
KEYS = ("r_pct", "g_t", "w_r", "w_half", "w_t", "w_delay")
UNITS = os.path.join(ROOT, "league", "champions")
SLOTS = ("attack", "skill", "skill2", "ult")
phys, t, n, cc = setup.phys, setup.t, setup.n, setup.cc
# lang -> the add-on's texts (the main pack's with the add-on's rules)
NATIVE = {
    "zh-hans": {
        "attack": "【附加包】抡铲。" + n("牧魂人") + "：临终仪式打英雄或打死单位挖坟，附近每死几个敌人也挖一座（最多4座）；满{g_n}座时" +
                  "下一铲每座坟唤醒1只" + n("雾行者") + "，自己追咬" + t("{walk_t}秒") + "（每口" + phys("k_dmg", "k_ratio") +
                  "，可被击杀）。" + n("暗灵缠身") + "：自动施放，" + t("{w_delay}秒") + "后立起一圈真正的墙" + t("{w_t}秒") + "，只挡敌人。",
        "skill": "【附加包】下一铲造成" + phys("q_dmg", "q_ratio") + "物理伤害，回复10–76 + 已损失生命6–10%（按等级；打英雄以外减半）。",
        "skill2": "【附加包】扔出一团黑雾：范围内敌人受到" + phys("e_dmg", "e_ratio") + "+最大生命{e_hp}%物理伤害，护甲-{e_arm}%持续" +
                  t("{e_t}秒") + "，" + cc("减速") + "{e_slow}%；约里克、雾行者、室女朝被标记的英雄走时移速+18–30%，附近的雾行者扑过去。",
        "ult": "【附加包】召唤可被击杀的" + n("迷雾室女") + "和2–4只雾行者：室女跟着约里克" + t("{maid_t}秒") + "，" + t("每秒") +
               "向最近的敌人放魂弹（" + phys("r_dmg", "r_ratio") + "魔法），打中英雄留下标记，约里克普攻或黑雾打中这名英雄时额外造成最大生命" +
               "2–3%魔法伤害；她附近有敌人阵亡就拉起雾行者。",
    },
    "zh-hant": {
        "attack": "【附加包】揮鏟。" + n("亡魂牧人") + "：臨終葬儀打英雄或打死單位挖墳，附近每死幾個敵人也挖一座（最多4座）；滿{g_n}座時" +
                  "下一鏟每座墳喚醒1隻" + n("霧行者") + "，自己追咬" + t("{walk_t}秒") + "（每口" + phys("k_dmg", "k_ratio") +
                  "，可被擊殺）。" + n("黯影屍陣") + "：自動施放，" + t("{w_delay}秒") + "後立起一圈真正的牆" + t("{w_t}秒") + "，只擋敵人。",
        "skill": "【附加包】下一鏟造成" + phys("q_dmg", "q_ratio") + "物理傷害，回復10–76 + 已損失生命6–10%（按等級；打英雄以外減半）。",
        "skill2": "【附加包】丟出一團黑霧：範圍內敵人受到" + phys("e_dmg", "e_ratio") + "+最大生命{e_hp}%物理傷害，護甲-{e_arm}%持續" +
                  t("{e_t}秒") + "，" + cc("緩速") + "{e_slow}%；約瑞科、霧行者、少女朝被標記的英雄走時移速+18–30%，附近的霧行者撲過去。",
        "ult": "【附加包】召喚可被擊殺的" + n("迷霧少女") + "和2–4隻霧行者：少女跟著約瑞科" + t("{maid_t}秒") + "，" + t("每秒") +
               "向最近的敵人放魂彈（" + phys("r_dmg", "r_ratio") + "魔法），打中英雄留下標記，約瑞科普攻或黑霧打中這名英雄時額外造成最大生命" +
               "2–3%魔法傷害；她附近有敵人陣亡就拉起霧行者。",
    },
    "en": {
        "attack": "[Add-on] Shovel blows. " + n("Shepherd of Souls") + ": graves (up to 4) from units Last Rites kills or "
                  "champions it hits, and every few deaths near him; with {g_n}+ the next raises a " + n("Mist Walker") +
                  " a grave, hunting on its own " + t("{walk_t}s") + " (" + phys("k_dmg", "k_ratio") + " a bite, killable). " +
                  n("Dark Procession") + " (auto): after " + t("{w_delay}s") + " a real wall ring stands " + t("{w_t}s") +
                  ", blocking enemies only.",
        "skill": "[Add-on] His next blow deals " + phys("q_dmg", "q_ratio") + " physical damage and heals him 10-76 + 6-10% of his "
                 "missing health (by level; half on anything but a champion).",
        "skill2": "[Add-on] Throws a globule of Black Mist: enemies hit take " + phys("e_dmg", "e_ratio") + " + {e_hp}% max health "
                  "physical damage, lose {e_arm}% armour for " + t("{e_t}s") + " and are " + cc("slowed") + " {e_slow}%; he, his "
                  "walkers and the Maiden move 18-30% faster toward a marked champion, and walkers near it leap at it.",
        "ult": "[Add-on] Raises the killable " + n("Maiden of the Mist") + " and 2-4 walkers: she follows him for " +
               t("{maid_t}s") + ", firing " + t("every second") + " at the nearest enemy (" + phys("r_dmg", "r_ratio") + " magic) "
               "and marking champions; his attack or mist on a marked one deals 2-3% of its max health as magic damage. Enemies "
               "dying near her rise as walkers.",
    },
    "ko": {
        "attack": "[확장] 삽 공격. " + n("영혼의 길잡이") + ": 최후의 의식이 챔피언을 치거나 유닛을 처치하면, 주변 적이 몇 번 죽을 때마다 "
                  "무덤 생성(최대 4개), {g_n}개 이상이면 다음 일격에 무덤마다 " + n("안개 망령") + "이 " + t("{walk_t}초") +
                  " 동안 스스로 물어뜯음(" + phys("k_dmg", "k_ratio") + ", 처치 가능). " + n("망자의 진") + ": 자동 시전, " +
                  t("{w_delay}초") + " 후 진짜 벽 " + t("{w_t}초") + ", 적만 막음.",
        "skill": "[확장] 다음 공격이 " + phys("q_dmg", "q_ratio") + " 물리 피해, 체력 10-76 + 잃은 체력 6-10% 회복(레벨 비례; 챔피언 외 절반).",
        "skill2": "[확장] 검은 안개: 범위 적에게 " + phys("e_dmg", "e_ratio") + " + 최대 체력 {e_hp}% 물리 피해, 방어력 -{e_arm}% " +
                  t("{e_t}초") + ", {e_slow}% " + cc("둔화") + "; 요릭·망령·처녀가 표식 챔피언 쪽으로 이동 속도 +18-30%, 근처 망령이 덮침.",
        "ult": "[확장] 처치 가능한 " + n("안개 처녀") + "와 망령 2-4마리 소환: 처녀는 " + t("{maid_t}초") + " 동안 요릭을 따라다니며 " +
               t("매초") + " 가장 가까운 적에게 영혼탄(" + phys("r_dmg", "r_ratio") + " 마법), 맞은 챔피언에 표식: 요릭의 공격이나 안개가 "
               "닿으면 최대 체력 2-3% 마법 피해; 그녀 근처에서 죽은 적은 망령이 됨.",
    },
    "ja": {
        "attack": "【拡張】シャベル攻撃。" + n("魂の導き手") + "：葬送でチャンピオンを打つかユニットを倒す、近くの敵が数体倒れるたびに墓（最大4）、" +
                  "{g_n}つ以上で次の一撃は墓1つに" + n("ミストウォーカー") + "1体が" + t("{walk_t}秒") + "自ら噛みつく（" +
                  phys("k_dmg", "k_ratio") + "、倒せる）。" + n("屍の列") + "：自動、" + t("{w_delay}秒") + "後に本物の壁の輪が" +
                  t("{w_t}秒") + "、敵だけ阻む。",
        "skill": "【拡張】次の攻撃が" + phys("q_dmg", "q_ratio") + "の物理ダメージ、体力10–76 + 失った体力の6–10%回復（レベル比例；チャンピオン以外は半分）。",
        "skill2": "【拡張】黒い霧：範囲の敵に" + phys("e_dmg", "e_ratio") + "+最大体力{e_hp}%の物理ダメージ、物理防御-{e_arm}%（" +
                  t("{e_t}秒") + "）、{e_slow}%" + cc("スロウ") + "；ヨリック・ウォーカー・乙女は印の敵へ向かうと移動速度+18–30%、近くのウォーカーが飛びかかる。",
        "ult": "【拡張】倒せる" + n("霧の乙女") + "とウォーカー2–4体を召喚：乙女は" + t("{maid_t}秒") + "ヨリックに付き従い" + t("毎秒") +
               "最寄りの敵へ魂弾（" + phys("r_dmg", "r_ratio") + "魔法）、当たったチャンピオンに印：ヨリックの攻撃か霧で最大体力2–3%の魔法ダメージ；" +
               "近くで倒れた敵はウォーカーになる。",
    },
}


def lp(path):
    """Windows long-path form: the repo can sit deep under the user's profile."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def consts(src):
    """src/lib.rs's `pub const NAME: <type> = <value>;` - integers, floats written `30_000.0`, strings."""
    out = {}
    for name, kind, value in re.findall(r"pub const (\w+): (usize|u64|f64|&str) = ([^;]+);", src):
        value = value.strip()
        if kind == "&str":
            out[name] = value.strip('"')
        elif re.fullmatch(r"[0-9_]+(\.[0-9_]*)?", value):     # a literal (HELD_TICKS = Q_HIT - 4 and the like are left out)
            out[name] = int(float(value.replace("_", "")))
    return out


def attack_ticks(name):
    """a unit sheet's attack: (ticks long, the tick its third frame starts - the bite / the claws)"""
    with open(lp(os.path.join(UNITS, name + "#anim.fanim")), encoding="utf-8-sig") as f:
        frames = json.load(f)["anims"]["attack"]["frames"]
    secs = [fr.get("duration", fr["data"].get("duration")) for fr in frames]
    return round(sum(secs) * 60), round(sum(secs[:2]) * 60)


def names_in(champion):
    """every buff / flag / projectile / view / sound name the kit uses"""
    text = json.dumps(champion)
    return set(re.findall(r'"(?:name|buff_name)": "(league_yorick_[a-z0-9_]+)"', text))


def check_units(copy, main, p, c):
    """The natives' numbers (c: src/lib.rs) against P and the unit sheets; the names they read and lay against the copy."""
    want = {"K_N": p["g_n"], "WALK_HIT": p["k_dmg"], "WALK_HIT_AD": p["k_ratio"], "WALK_COOL": p["k_p"], "K_T": p["k_t"],
            "LEAP_HIT": p["k_jmp"], "LEAP_HIT_AD": p["k_jmp_r"], "R_N": p["r_n"], "MAID_HIT": p["r_dmg"],
            "MAID_HIT_AD": p["r_ratio"], "MAID_COOL": p["r_p"], "R_T": p["r_t"], "Q_HIT": p["q_hit"], "R_REL": p["r_rel"],
            "MARK_T": p["r_mk_t"], "BOLT_SPEED": p["r_bolt"], "MAID_RANGE": p["r_reach"]}
    for name, act, lands in ((c["WALKER"], "WALK_ACT", "WALK_LANDS"), (c["MAIDEN_UNIT"], "MAID_ACT", "MAID_LANDS")):
        want[act], want[lands] = attack_ticks(name)
    wrong = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    if wrong:
        sys.exit(f"the units' numbers differ from src/lib.rs (lib, kit or sheet): {wrong}")
    have, plain = names_in(copy), names_in(main)
    read = ("Q_WIN", "Q_HL", "Q_CH", "HIT", "K_ASK", "K_ASK4", "K_UNIT", "M_ASK", "M_UNIT", "E_ASK", "W_ASK", "W_UP", "W_DOWN", "R_ON",
            "E_MARK", "R_MKV", "R_BOLT", "R_CLAW", "R_MARK_VIEW", "Q_GRAVE", "K_LEAP_VIEW", "K_SPAWN_SFX", "R_SPAWN_SFX")
    missing = [k for k in read if c[k] not in have]
    if missing:
        sys.exit(f"src/lib.rs names {missing} the copy does not use: update src/lib.rs or build_yorick.py")
    if "league_yorick_g4" not in have or any(f"league_yorick_g{k}" not in have for k in range(1, 5)):
        sys.exit("the copy has no grave ladder g1..g4: src/lib.rs's GRAVES reads it")
    own = ("Q_WIN", "Q_HL", "HIT", "K_ASK", "K_ASK4", "K_UNIT", "M_ASK", "M_UNIT", "E_ASK", "W_ASK", "W_UP", "W_DOWN")
    if any(c[k] in plain for k in own) or any(b.startswith((c["W_UID"], c["M_UID"])) for b in plain):
        sys.exit("the main pack's Yorick uses one of the add-on's own names: update src/lib.rs")
    if c["E_MS"] in have:
        sys.exit("the copy still has the data's haste (E_MS): the add-on lays it by direction")
    views = {v["name"] for v in copy["view_effects"]}
    if not {c["R_CLAW"], c["R_MARK_VIEW"], c["K_LEAP_VIEW"], c["Q_GRAVE"]} <= views:
        sys.exit("a picture src/lib.rs plays is no view effect of the kit")
    if c["R_BOLT"] not in {v["name"] for v in copy["view_projectiles"]}:
        sys.exit("the Maiden's bolt (R_BOLT) has no projectile picture in the kit")
    if c["R_MKV"] not in {v["name"] for v in copy["view_buffs"]}:
        sys.exit("the Maiden's mark (R_MKV) has no buff picture in the kit")
    kit_text = json.dumps(copy)
    for k in ("K_SPAWN_SFX", "R_SPAWN_SFX", "R_CLAW", "K_LEAP_VIEW"):
        if not re.search(r'"type": "(Target)?Sfx", "name": "' + re.escape(c[k]) + '"', kit_text):
            sys.exit(f"src/lib.rs's {k} = {c[k]} is no sound the kit plays")
    if copy.get("passive", {}).get("passive_ref") != MOD_ID + ":shepherd":
        sys.exit("the copy does not call the add-on: update this script")


def check_defaults(p):
    """src/lib.rs's Params::default() holds P's numbers (the add-on reads passive.params; the defaults are its fallback)."""
    src = open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read()
    m = re.search(r"Self \{ (r_pct: .*?) \}", src, re.S)
    got = dict((k.strip(), int(v)) for k, v in (kv.split(":") for kv in m.group(1).replace("\n", " ").split(",")))
    want = dict(p, w_t=p["w_tn"])      # the copy's wall time is the add-on's own (build_yorick.py w_tn)
    bad = {k: (got.get(k), want[k]) for k in KEYS if got.get(k) != want[k]}
    if bad:
        sys.exit(f"src/lib.rs Params::default() differs from P (lib.rs, P): {bad}")


def files(draft):
    """{path: text} this script writes."""
    p = dict(kit.P)
    check_defaults(p)
    champion = kit.build(dict(p, native=1))
    main = kit.build(p)
    c = consts(open(lp(os.path.join(ADDON, "src", "lib.rs")), encoding="utf-8").read())
    check_units(champion, main, p, c)
    out = {}
    if not draft:
        with open(lp(os.path.join(ROOT, "league", "champion", HERO + ".data_champion")), encoding="utf-8", newline="") as f:
            shipped = f.read()
        if dumps_main(main) != shipped:
            sys.exit("the main pack's league_yorick differs from build_yorick.P: rebuild it first")
        for slot in SLOTS:
            champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot
        values = dict(setup.values(p), walk_t=setup.secs(c["WALK_LIFE"]), maid_t=setup.secs(c["MAID_LIFE"]),
                      w_t=setup.secs(p["w_tn"]))      # 附加包的墙最多立 2 秒（英雄联盟 4 秒；能打塌）
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
