"""Aphelios's text (5 languages), sound_info files and his keys in the shared files, numbers from build_aphelios.P.

    python tools/kit/setup_aphelios.py [--params final.json] [--check] [--face X,Y] [--banpick Y]

Writes (in league/): text/champion.i18n (league_aphelios in every language, description + skill_name),
sound/sfx/league_aphelios_*.sound_info, mod.override_info (every sound and clip), style/champion_view (face, centre and
the ban/pick card's point once the sprite is in), mod.mod_info (0.124.0, Aphelios named). Only his keys change in the
shared files. JSON: indent 2, CRLF, UTF-8. --check only prints each text's shown length against lint_mod's TOOLTIP_MAX.
Names: Data Dragon 16.20.1 (zh_CN 残月之肃 / 厄斐琉斯 - the client swaps name and title: 厄斐琉斯; 传知者与真知者, 武器技能, 月相轮转,
清辉夜凝; the weapons 通碧, 断魄, 坠明, 荧焰, 折镜; zh_TW 亞菲利歐: 殺手與先知, 武器技能, 月相輪轉, 月夜守護, 月影步槍, 月鐮槍刃,
月殞重砲, 熾夜月燄, 月曲終章; ja アフェリオス: 殺す者と導く者, 武器ごとのスキル, フェーズ, 月光の祈り, キャリブラム, セヴェラム,
グラヴィタム, インファーナム, クレッシェンダム; ko 아펠리오스: 암살자와 예언자, 무기 스킬, 위상 변화, 월광포화, 만월총, 절단검, 중력포,
화염포, 반월검). Slots: skill = Q (the main weapon's), skill2 = W, ult = R; the passive, the weapons' shots and the
magazine are told in the attack's text. No combo sentence in any text (the user's rule). No `league_aphelios_attack`
sound: the engine would play it at the start of every attack; each weapon's shot plays from the tree.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_aphelios import P, WEAPONS, lp  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(REPO, "league")
ID = "league_aphelios"
VERSION = "0.124.0"
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
O = "<#ff9028ff>"      # names, physical
A = "<#ffb900ff>"      # durations, counts
R = "<#ef5350ff>"      # crowd control
E = "<>"
# the face at his hair's crown (tfm2_ase.py face: 43 px over the feet at the tuft, the head centre x -3.3) x 0.9 (he is
# drawn 90 %: hd.rs SIZES, the cards too); the idle's head tops 32 x 0.9 = 29 px over the pivot (Calibrum's tip 35: a
# thin prop, not measured) -> banpick_center y = -39 - (-29)
VIEW = {"face": {"x": -2, "y": -38}, "center": {"x": 0, "y": -12}, "banpick_center": {"x": 0, "y": -10}}


def phy(d, r):
    return f"{O}{{{d}}}{E} + {ADi}{O}{{{r}}}%{E}"


def named(*parts):
    return "".join(parts)


TEXT = {
    "zh-hans": {
        "name": "厄斐琉斯",
        "attack": named("用主手武器开火，每把", A, "{ammo}发", E, "，打空换下一把：", O, "通碧", E, "射程更远，", O, "断魄", E,
                        "吸血{sev_vamp}%、攻速+{sev_as}%，", O, "坠明", E, "减速{grav_slow}%，", O, "荧焰", E, "溅射，", O, "折镜", E,
                        "每次命中攻击+{cre_ad}%（{cre_t}秒，可叠加）。", O, "传知者与真知者", E, "：随等级额外成长。"),
        "skill": named("主手武器的技能，各自冷却：通碧狙击造成", phy("q_c_dmg", "q_c_ad"), O, "物理伤害", E, "并追射；断魄加速连射回血；坠明",
                       R, "定身", E, "被它减速的敌人{q_g_root}秒；荧焰扇形波后副手追击；折镜放下哨塔{q_r_t}秒。"),
        "skill2": "交换主手和副手武器：主手技能在冷却、副手技能已就绪且附近有敌方英雄时才交换。",
        "ult": named("爆点附近有2个以上敌方英雄或目标被控制时，射出月光，在第一个英雄处爆炸，造成", phy("r_dmg", "r_ad"), O, "物理伤害", E,
                     "，再按主手：通碧追射、断魄回血、坠明减速{r_g_slow}%、荧焰加伤、折镜叠{r_cre}层。"),
        "names": ("武器技能", "月相轮转", "清辉夜凝"),
    },
    "zh-hant": {
        "name": "亞菲利歐",
        "attack": named("用主武器開火，每把", A, "{ammo}發", E, "，打空換下一把：", O, "月影步槍", E, "射程更遠，", O, "月鐮槍刃", E,
                        "吸血{sev_vamp}%、攻速+{sev_as}%，", O, "月殞重砲", E, "緩速{grav_slow}%，", O, "熾夜月燄", E, "濺射，", O,
                        "月曲終章", E, "每次命中攻擊+{cre_ad}%（{cre_t}秒，可疊加）。", O, "殺手與先知", E, "：隨等級額外成長。"),
        "skill": named("主武器的技能，各自冷卻：步槍狙擊造成", phy("q_c_dmg", "q_c_ad"), O, "物理傷害", E, "並追射；槍刃加速連射回血；重砲",
                       R, "定身", E, "被它緩速的敵人{q_g_root}秒；月燄扇形波後副武器追擊；飛刃放下哨兵{q_r_t}秒。"),
        "skill2": "交換主武器和副武器：主武器技能冷卻中、副武器技能已就緒且附近有敵方英雄時才交換。",
        "ult": named("爆點附近有2個以上敵方英雄或目標被控制時，射出月光，在第一個英雄處爆炸，造成", phy("r_dmg", "r_ad"), O, "物理傷害", E,
                     "，再依主武器：步槍追射、槍刃回血、重砲緩速{r_g_slow}%、月燄加傷、飛刃疊{r_cre}層。"),
        "names": ("武器技能", "月相輪轉", "月夜守護"),
    },
    "en": {
        "name": "Aphelios",
        "attack": named("Fires his main weapon, ", A, "{ammo} shots", E, " each, then the next takes its place: ", O, "Calibrum", E,
                        " longer range, ", O, "Severum", E, " {sev_vamp}% lifesteal and +{sev_as}% attack speed, ", O, "Gravitum", E,
                        " {grav_slow}% slow, ", O, "Infernum", E, " splash, ", O, "Crescendum", E,
                        " +{cre_ad}% attack per hit ({cre_t}s, stacking). ", O, "The Hitman and the Seer", E, ": extra growth."),
        "skill": named("The main weapon's ability, each on its own cooldown: Calibrum snipes for ", phy("q_c_dmg", "q_c_ad"), " ",
                       O, "physical damage", E, " and follows up; Severum runs and fires, healing; Gravitum ", R, "roots", E,
                       " every enemy it slowed for {q_g_root}s; Infernum's wave, then off-hand shots; Crescendum a sentry for "
                       "{q_r_t}s."),
        "skill2": "Swaps the main and off-hand weapons, only when the main hand's ability is cooling down, the off hand's is "
                  "ready and an enemy champion is near.",
        "ult": named("With 2+ enemy champions round the blast or the target in crowd control, fires moonlight that bursts on the "
                     "first champion for ", phy("r_dmg", "r_ad"), " ", O, "physical damage", E, ", then by main weapon: Calibrum "
                     "follow-up shots, Severum heal, Gravitum {r_g_slow}% slow, Infernum more damage, Crescendum {r_cre} chakrams."),
        "names": ("Weapon Abilities", "Phase", "Moonlight Vigil"),
    },
    "ko": {
        "name": "아펠리오스",
        "attack": named("주 무기로 공격, 무기마다 ", A, "{ammo}발", E, ", 다 쓰면 다음 무기: ", O, "만월총", E, " 사거리 증가, ", O, "절단검", E,
                        " 생명력 흡수 {sev_vamp}%·공격 속도 +{sev_as}%, ", O, "중력포", E, " {grav_slow}% 둔화, ", O, "화염포", E,
                        " 범위 피해, ", O, "반월검", E, " 적중마다 공격력 +{cre_ad}%({cre_t}초, 중첩). ", O, "암살자와 예언자", E,
                        ": 추가 성장."),
        "skill": named("주 무기의 스킬(각자 재사용 대기시간): 만월총 저격 ", phy("q_c_dmg", "q_c_ad"), "의 ", O, "물리 피해", E,
                       " 후 추가 사격; 절단검 이동하며 연사·회복; 중력포 둔화된 적 ", R, "{q_g_root}초 속박", E,
                       "; 화염포 원뿔 공격 후 보조 무기 추격; 반월검 파수탑 {q_r_t}초."),
        "skill2": "주 무기와 보조 무기를 교체합니다. 주 무기 스킬이 재사용 대기 중이고 보조 무기 스킬이 준비되었으며 근처에 적 챔피언이 있을 때만.",
        "ult": named("폭발 지점 근처에 적 챔피언 2명 이상 또는 대상이 군중 제어 상태일 때 월광 발사, 첫 챔피언에서 폭발해 ", phy("r_dmg", "r_ad"),
                     "의 ", O, "물리 피해", E, ", 주 무기별: 만월총 추가 사격, 절단검 회복, 중력포 {r_g_slow}% 둔화, 화염포 추가 피해, "
                     "반월검 {r_cre}중첩."),
        "names": ("무기 스킬", "위상 변화", "월광포화"),
    },
    "ja": {
        "name": "アフェリオス",
        "attack": named("メイン武器で攻撃、各", A, "{ammo}発", E, "、撃ち尽くすと次の武器に：", O, "キャリブラム", E, "射程増加、", O,
                        "セヴェラム", E, "ライフスティール{sev_vamp}%・攻撃速度+{sev_as}%、", O, "グラヴィタム", E, "{grav_slow}%スロウ、",
                        O, "インファーナム", E, "範囲攻撃、", O, "クレッシェンダム", E, "命中ごとに攻撃力+{cre_ad}%（{cre_t}秒、累積）。",
                        O, "殺す者と導く者", E, "：追加成長。"),
        "skill": named("メイン武器のスキル（個別CD）：キャリブラム狙撃", phy("q_c_dmg", "q_c_ad"), "の", O, "物理ダメージ", E,
                       "と追撃；セヴェラム走りながら連射・回復；グラヴィタム スロウ中の敵を", R, "{q_g_root}秒スネア", E,
                       "；インファーナム扇状攻撃後オフハンド追撃；クレッシェンダム セントリー{q_r_t}秒。"),
        "skill2": "メインとオフハンドの武器を入れ替える。メインのスキルがCD中、オフハンドのスキルが使用可能で、近くに敵チャンピオンがいる時のみ。",
        "ult": named("爆発地点の近くに敵チャンピオン2体以上、または対象がCC中の時に月光を放ち、最初のチャンピオンで爆発して", phy("r_dmg", "r_ad"),
                     "の", O, "物理ダメージ", E, "、メイン武器別：キャリブラム追撃、セヴェラム回復、グラヴィタム{r_g_slow}%スロウ、"
                     "インファーナム追加ダメージ、クレッシェンダム{r_cre}スタック。"),
        "names": ("武器ごとのスキル", "フェーズ", "月光の祈り"),
    },
}

C = "league_aphelios_sfx_"
# sound name -> [(clip, volume, delay)]; clip names differ from the sound names (a clip named like its sound is not
# found in game)
SOUNDS = {}
for _w in WEAPONS:
    SOUNDS[f"league_aphelios_a_{_w}"] = [(C + f"a_{_w}", 0.4, 0.0)]
    SOUNDS[f"league_aphelios_a_{_w}_hit"] = [(C + f"a_{_w}_hit", 0.3, 0.0)]
    SOUNDS[f"league_aphelios_swap_{_w}"] = [(C + f"swap_{_w}", 0.45, 0.0)]
    SOUNDS[f"league_aphelios_q_{_w}"] = [(C + f"q_{_w}", 0.55, 0.0)]
    SOUNDS[f"league_aphelios_vo_q_{_w}"] = [(C + f"vo_q_{_w}", 0.85, 0.0)]
for _s, _v in (("q_c_hit", 0.5), ("q_c_pop", 0.5), ("q_g_hit", 0.5), ("q_r_land", 0.45), ("r", 0.6), ("r_shot", 0.6),
               ("r_boom", 0.65)):
    SOUNDS[f"league_aphelios_{_s}"] = [(C + _s, _v, 0.0)]
SOUNDS["league_aphelios_vo_w"] = [(C + "vo_w", 0.85, 0.0)]
SOUNDS["league_aphelios_vo_r"] = [(C + "vo_r", 0.9, 0.0)]
CLIPS = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def values(p):
    v = {k: p[k] for k in ("ammo", "sev_vamp", "sev_as", "grav_slow", "cre_ad", "q_c_dmg", "q_c_ad", "r_dmg", "r_ad",
                           "r_g_slow", "r_cre")}
    for k in ("cre_t", "q_g_root", "q_r_t"):
        v[k] = secs(p[k])
    return v


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def load(path):
    return json.loads(open(lp(path), "rb").read().decode("utf-8-sig"))


def save(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def texts(p):
    v = values(p)
    out = {}
    for lang, t in TEXT.items():
        d = {"name": t["name"]}
        for k in ("attack", "skill", "skill2", "ult"):
            d[k] = t[k].format(**v)
        out[lang] = (d, dict(zip(("skill1", "skill2", "ult"), t["names"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--face", help="X,Y from tfm2_ase.py face")
    ap.add_argument("--banpick", type=int, help="banpick_center y (-39 - the idle's top), when the top is above -28")
    a = ap.parse_args()
    p = dict(P)
    if a.params:
        p.update(json.load(open(a.params, encoding="utf-8")))
    tx = texts(p)
    bad = False
    for lang, (d, _) in tx.items():
        lens = {k: shown_length(TEXT[lang][k]) for k in ("attack", "skill", "skill2", "ult")}
        bad |= any(n > TOOLTIP_MAX[lang] for n in lens.values())
        print(lang, " ".join(f"{k}:{n}/{TOOLTIP_MAX[lang]}" for k, n in lens.items()))
    if a.check:
        sys.stdout.reconfigure(encoding="utf-8")
        for lang, (d, _) in tx.items():
            for k in ("attack", "skill", "skill2", "ult"):
                print(lang, k, re.sub(r"<[^>]*>", "", d[k]))
        return
    if bad:
        sys.exit("a text is longer than TOOLTIP_MAX")

    i18n = load(os.path.join(MOD, "text", "champion.i18n"))
    for lang, (d, names) in tx.items():
        i18n[lang]["description"][ID] = d
        i18n[lang]["skill_name"][ID] = names
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)

    for name, plays in SOUNDS.items():
        save(os.path.join(MOD, "sound", "sfx", name + ".sound_info"),
             {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})

    ov = load(os.path.join(MOD, "mod.override_info"))
    for k in [k for k in ov if ID in k]:      # his keys rebuilt (a renamed sound leaves none behind)
        del ov[k]
    for name in list(SOUNDS) + CLIPS:
        ov[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/league/sound/sfx/{name}", "type": "override"}
    save(os.path.join(MOD, "mod.override_info"), ov)

    view = json.loads(json.dumps(VIEW))
    if a.face:
        x, y = (int(v) for v in a.face.split(","))
        view["face"] = {"x": x, "y": y}
    if a.banpick is not None:
        if a.banpick > 0:
            sys.exit("never a positive banpick_center y (card-banpick rule)")
        view["banpick_center"] = {"x": 0, "y": a.banpick}
    cv = load(os.path.join(MOD, "style", "champion_view.champion_view"))
    cv["entries"][ID] = view
    save(os.path.join(MOD, "style", "champion_view.champion_view"), cv)

    mi = load(os.path.join(MOD, "mod.mod_info"))
    if tuple(int(x) for x in mi["version"].split(".")) < tuple(int(x) for x in VERSION.split(".")):
        mi["version"] = VERSION
    if "Aphelios" not in mi["description"]:
        mi["description"] = re.sub(r" and ([\w'. ]+?)\. Kits", r", \1 and Aphelios. Kits", mi["description"], count=1)
    save(os.path.join(MOD, "mod.mod_info"), mi)
    print("written")


if __name__ == "__main__":
    main()
