"""从主包生成薇古丝附加包的副本（照英雄联盟 V26.13 的暮气、终焉、恐惧、愁煞）。

    python addons/league_vex/make_override.py

用 tools/kit/build_vex.py（参数表 P）重新生成薇古丝，先核对 native=0 的那份和主包 league/champion/league_vex.data_champion
一字不差（副本不会和主包走岔），再写 addons/league_vex/override/league_vex.data_champion 和 .../text/champion.i18n：
native=1 的那份——
  * 主包的整套技能（普攻里的生人勿近、两段的寒心波云、溟濛渐染、愁煞和落地的生人勿近）；
  * 被动换成本包的 league_vex:gloom，P 里它用的数字放进 passive.params（build_vex.NATIVE_PARAMS）；
  * 她的普攻、Q、W 打中的单位挂 v_hit（2 tick，本包引爆暮气）；E、R 不挂；数据里的替代做法（g_win 和只打英雄的同路弹）拿掉；
  * 终焉的恐惧换成标记 f_q / f_e（本包按等级放恐惧、减速），击倒照旧；E 出手时目标挂 e_aim（本包记落点）；
  * 愁煞冲不冲到他身上看本包挂的 r_in，冷却用 P 的 r_cd_c（本包能刷新它，比主包长）；终焉回来的画面由本包放；
  * 普攻、E、R 的说明指向 description.league_vex.<slot>，用本包的文字。
别的英雄都不动。主包的薇古丝改了就重跑。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADDON = os.path.join(ROOT, "addons", "league_vex")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import build_vex as kit  # noqa: E402
import setup_vex as setup  # noqa: E402

MOD_ID = "league_vex"
HERO = "league_vex"
SLOTS = ("attack", "skill2", "ult")
O, A, R, M, E = setup.O, setup.A, setup.R, setup.M, setup.E
mag, sh = setup.mag, setup.sh

def lvl_mag(lo, hi, r):
    """按等级的魔法伤害：{lo}–{hi} + 法强 r%。"""
    return M + "{" + lo + "}–{" + hi + "}" + E + " + " + setup.APi + M + "{" + r + "}%" + E


TEXT = {
    "zh-hans": {
        "attack": "【扩展包】射出暗影弹。" + O + "终焉暮气" + E + "：每" + A + "{p_cd}秒" + E + "（随等级缩短）下一个技能" + R + "击倒并恐惧" + E +
                  "命中的敌人" + A + "{p_fear}秒" + E + "起；她身边突进的敌人被施加" + O + "暮气" + E + "。" + O + "生人勿近" + E +
                  "：敌方英雄靠近时改为获得" + sh("w_sh", "w_sh_ratio") + "护盾并震伤周围" + mag("w_dmg", "w_ratio") + "。",
        "skill2": "【扩展包】影子飞到目标处扩散，造成" + mag("e_dmg", "e_ratio") + "魔法伤害、减速{e_slow}%，并施加" + O + "暮气" + E +
                  "：她的普攻、寒心波云或生人勿近再打中就引爆，造成" + lvl_mag("g_lo", "g_hi", "g_ratio") + "魔法伤害，终焉的等待缩短{g_cut}%。",
        "ult": "【扩展包】射出飞弹标记一名敌方英雄，造成" + mag("r_dmg", "r_ratio") + "魔法伤害，随后冲向他再造成" + mag("r2_dmg", "r2_ratio") +
               "魔法伤害，能击杀就冲到他身上。被标记的英雄" + A + "{r_reset}秒" + E + "内阵亡就刷新愁煞。",
    },
    "zh-hant": {
        "attack": "【擴充包】射出暗影彈。" + O + "無望厄障" + E + "：每" + A + "{p_cd}秒" + E + "（隨等級縮短）下一個技能" + R + "擊倒並恐懼" + E +
                  "命中的敵人" + A + "{p_fear}秒" + E + "起；她身邊突進的敵人被施加" + O + "陰霾" + E + "。" + O + "個人舒適圈" + E +
                  "：敵方英雄靠近時改為獲得" + sh("w_sh", "w_sh_ratio") + "護盾並震傷周圍" + mag("w_dmg", "w_ratio") + "。",
        "skill2": "【擴充包】影子飛到目標處擴散，造成" + mag("e_dmg", "e_ratio") + "魔法傷害、緩速{e_slow}%，並施加" + O + "陰霾" + E +
                  "：她的普攻、冷酷暗箭或個人舒適圈再打中就引爆，造成" + lvl_mag("g_lo", "g_hi", "g_ratio") + "魔法傷害，無望的等待縮短{g_cut}%。",
        "ult": "【擴充包】射出飛彈標記一名敵方英雄，造成" + mag("r_dmg", "r_ratio") + "魔法傷害，隨後衝向他再造成" + mag("r2_dmg", "r2_ratio") +
               "魔法傷害，能擊殺就衝到他身上。被標記的英雄" + A + "{r_reset}秒" + E + "內陣亡就刷新飛影急襲。",
    },
    "en": {
        "attack": "[Add-on] Fires a shadow bolt. " + O + "Doom" + E + ": every " + A + "{p_cd}s" + E + " (less with level) her next spell " + R +
                  "knocks down and fears" + E + " the enemies hit for " + A + "{p_fear}s" + E + " or more; enemies dashing near her get " + O +
                  "Gloom" + E + ". " + O + "Personal Space" + E + ": with an enemy champion close, she instead gains a " + sh("w_sh", "w_sh_ratio") +
                  " shield and blasts the enemies around her for " + mag("w_dmg", "w_ratio") + " " + M + "magic damage" + E + ".",
        "skill2": "[Add-on] Her Shadow flies to the target and spreads: " + mag("e_dmg", "e_ratio") + " " + M + "magic damage" + E +
                  ", slowed {e_slow}%, and " + O + "Gloom" + E + ": her next attack, Mistral Bolt or Personal Space hit on that enemy pops it for " +
                  lvl_mag("g_lo", "g_hi", "g_ratio") + " " + M + "magic damage" + E + " and takes {g_cut}% off Doom's wait.",
        "ult": "[Add-on] Fires a missile that marks an enemy champion for " + mag("r_dmg", "r_ratio") + " " + M + "magic damage" + E +
               ", then surges toward it for " + mag("r2_dmg", "r2_ratio") + " more, onto it when that kills. If the champion dies within " + A +
               "{r_reset}s" + E + ", Shadow Surge is ready again.",
    },
    "ko": {
        "attack": "[확장] 그림자 탄을 쏜다. " + O + "파멸" + E + ": " + A + "{p_cd}초" + E + "(레벨에 따라 감소)마다 다음 스킬이 맞힌 적을 " + R +
                  "넘어뜨리고" + E + " " + A + "{p_fear}초" + E + " 이상 " + R + "공포" + E + "; 근처에서 돌진한 적에게 " + O + "우울" + E + ". " + O +
                  "거리 두기" + E + ": 적 챔피언이 가까우면 대신 " + sh("w_sh", "w_sh_ratio") + " 보호막을 얻고 주변에 " + mag("w_dmg", "w_ratio") +
                  " 마법 피해.",
        "skill2": "[확장] 그림자가 대상 위치로 날아가 퍼지며 " + mag("e_dmg", "e_ratio") + " 마법 피해, {e_slow}% 둔화, " + O + "우울" + E +
                  " 부여: 기본 공격, 안개 화살, 거리 두기로 다시 맞히면 터져 " + lvl_mag("g_lo", "g_hi", "g_ratio") + " 마법 피해, 파멸 대기 {g_cut}% 단축.",
        "ult": "[확장] 투사체로 적 챔피언을 표식해 " + mag("r_dmg", "r_ratio") + " 마법 피해, 이어서 돌진해 " + mag("r2_dmg", "r2_ratio") +
               " 마법 피해(처치할 수 있으면 끝까지 돌진). 표식된 챔피언이 " + A + "{r_reset}초" + E + " 안에 죽으면 그림자 파동 재사용 가능.",
    },
    "ja": {
        "attack": "【拡張】影の弾を撃つ。" + O + "フコウ" + E + "：" + A + "{p_cd}秒" + E + "（レベルで短縮）ごとに次のスキルが当たった敵を" + R +
                  "ノックダウン" + E + "し" + A + "{p_fear}秒" + E + "以上" + R + "恐怖" + E + "；近くでダッシュした敵に" + O + "ユーウツ" + E + "。" + O +
                  "パーソナルスペース" + E + "：敵チャンピオンが近いと代わりに" + sh("w_sh", "w_sh_ratio") + "のシールドを得て周囲に" +
                  mag("w_dmg", "w_ratio") + "。",
        "skill2": "【拡張】影が目標地点へ飛んで広がり、" + mag("e_dmg", "e_ratio") + "の魔法ダメージ、{e_slow}%スロウ、" + O + "ユーウツ" + E +
                  "付与：通常攻撃、無気力ショットかパーソナルスペースで再び当てると弾けて" + lvl_mag("g_lo", "g_hi", "g_ratio") + "の魔法ダメージ、フコウの待ちが{g_cut}%短縮。",
        "ult": "【拡張】弾で敵チャンピオンにマークをつけ" + mag("r_dmg", "r_ratio") + "の魔法ダメージ、続いて突進して" +
               mag("r2_dmg", "r2_ratio") + "の魔法ダメージ（倒せるなら懐まで）。マークされたチャンピオンが" + A + "{r_reset}秒" + E +
               "以内に倒れると影法師が再使用可能。",
    },
}


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
        sys.exit("the main pack's league_vex differs from build_vex.P: rebuild it first")
    champion = kit.build(dict(p, native=1))
    if champion.get("passive", {}).get("passive_ref") != MOD_ID + ":gloom":
        sys.exit("the copy has no league_vex:gloom passive: update this script")
    for slot in SLOTS:
        champion[slot]["description"] = "#asset/base/text/champion?description." + MOD_ID + "." + slot

    values = setup.values(p)
    for k in ("g_cut", "g_lo", "g_hi", "g_ratio"):
        values[k] = p[k]
    values["r_reset"] = setup.secs(p["r_reset"])
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
