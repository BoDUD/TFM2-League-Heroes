#!/usr/bin/env python3
"""league_rakan: Battle Dance (E) in its own slot, Grand Entrance (W) alone, Gleaming Quill (Q) in his attacks.

    python tools/fix/rakan_we_split.py [--check]

A player (2026-11-19, through the user): "rakan can't do his dashes unless he's trying to engage so he can't shield
his team until he w's enemies ... have the w and e kit within his abilities"; the user picked 「按 A 改」. Before, the
two basic slots were Q (skill, 5.5 s, EnemyWithoutTower 60000) and W then E (skill2, 7.5 s, EnemyChampion 45000): E
flew to an ally only after W's knock-up. Now:

  skill   Battle Dance alone, 7.5 s. Cast as `None` on `EnemyChampion` within E_CAST - a fight beside him. Not on an
          ally: a shield scores its full amount on anyone, so an ally-targeted cast goes out whenever it is ready,
          mostly out of fights (champion-data section 3: league_janna E, 46 casts in 10 minutes); Nocturne's shroud
          is wired this way. Who gets it: an allied champion in crowd control within E_CC first (league_leesin W's
          first tier), then W -> E's rings as they were (a random ally within 25000, 50000, 90000; 130000 with
          league_xayah_duo on him), else himself, now with his landing pose. Each pick is W -> E's E, moved as it
          was: the shield (90 + 70% AP, 180 ticks) and e_on on the ally before the flight (a stun in flight does not
          take it), the e_dash pose, the flight, the e_land pose and sound, Gleaming Quill's heal on touching the
          ally, the Xayah line. The slot's own pose is e_dash (3 ticks, then the branch's); the passive countdown
          check stays first.
  skill2  Grand Entrance alone: the dash, the spiral's knock-up and damage, the passive count. The flight that
          followed on tick 24 of the landing is gone (League: W and E are two casts).
  attack  Gleaming Quill every 5.5 s: an attack fired while the hidden caster flag q_cd (Q_CD ticks) is off sets it
          and also throws Q's quill - its flight, damage, heal arming and passive count as the Q slot had them, with
          Q's cast sound. The attack's own feather then flies unseen (league_rakan_a_quiet: no view entry, the same
          damage, towers included), so only the quill is drawn. a_twin (the attack's passive count) and Xayah's
          second feather stay as they were.

The R is untouched, every buff keeps its name (Xayah's kit reads e_on; league_sylas copies the R and the passive
flags). Also writes the five languages' texts (league/text/champion.i18n, Rakan's entries only: the quill's sentence
goes into the attack's, E's and W's halves become the two slots', the slot names follow). Idempotent; --check exits 1
while either part is not done.
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KIT = os.path.join(ROOT, "league", "champion", "league_rakan.data_champion")
TEXT = os.path.join(ROOT, "league", "text", "champion.i18n")
N = "league_rakan_"
Q_CD = 330          # ticks: the Q slot's cooldown, 5.5 s
E_CD = 450          # ticks: W -> E's cooldown, 7.5 s
E_CAST = 60000      # Battle Dance goes out when an enemy champion is this close (the Q slot's old reach)
E_CC = 90000        # the crowd-controlled ally's reach: W -> E's farthest ring without Xayah
NONE = {"type": "Combine", "effects": []}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def kit_done(d):
    return d["skill"].get("action_name") == "e_dash"


def split(d):
    """The kit in place: skill = E, skill2 = W, Q in the attack."""
    q, w, att = d["skill"], d["skill2"], d["attack"]
    qe, we, ae = q["effect"]["effects"], w["effect"]["effects"], att["effect"]["effects"]
    assert qe[0] == {"type": "RemoveCasterBuff", "name": N + "p_lq"} and qe[2] == {"type": "Sfx", "name": N + "q_cast"}
    quill = qe[3]
    assert len(qe) == 4 and quill["type"] == "LinearProjectile" and quill["name"] == N + "q_feather"
    assert we[0] == {"type": "RemoveCasterBuff", "name": N + "p_lw"} and we[1] == qe[1], "the passive check differs"
    dash = we[4]
    assert len(we) == 5 and dash["type"] == "MoveToTarget"
    at = [i for i, x in enumerate(dash["end_effects"]) if x["type"] == "Delayed"
          and x["effects"][0] == {"type": "RemoveCasterBuff", "name": N + "e_got"}]
    assert len(at) == 1, "W's landing has no single E"
    e_list = dash["end_effects"].pop(at[0])["effects"]
    ring = e_list[1]
    assert ring["type"] == "RandomTarget" and ring["range"] == 25000 and ring["casting_target"] == "AllyNotSelf"
    cc = copy.deepcopy(ring)
    cc["range"], cc["casting_target"] = E_CC, "AllyChampionInCC"
    posed = []

    def pose(o):        # himself when nobody was found: the shield and his landing pose
        if isinstance(o, dict):
            for k in ("effect_buff", "effect_none"):
                v = o.get(k)
                if isinstance(v, dict) and v.get("type") == "RangeEffect" and v.get("target") == "AllyOnlySelf" \
                        and any(x.get("type") == "AddBuff" and x["buff_state"]["name"] == N + "e_on" for x in v["effects"]):
                    o[k] = {"type": "Combine", "effects": [v, {"type": "CasterAnimation", "name": "e_land", "tick": 14}]}
                    posed.append(k)
            for v in o.values():
                pose(v)
        elif isinstance(o, list):
            for v in o:
                pose(v)
    pose(e_list)
    assert len(posed) == 2, posed       # with and without Xayah
    d["skill"] = {
        "action_name": "e_dash", "description": q["description"], "duration": 3, "cooltime": E_CD, "start_timing": 1,
        "cancelable": False, "range": E_CAST, "casting_type": "None", "casting_target": "EnemyChampion",
        "attack_type": "Skill",
        "effect": {"type": "Combine", "effects": [
            copy.deepcopy(we[1]), e_list[0], cc,
            {"type": "SwitchByBuff", "buff_name": N + "e_got", "effect_buff": dict(NONE),
             "effect_none": {"type": "Combine", "effects": e_list[1:]}}]}}
    assert [x.get("name") for x in ae[5:]] == [N + "a_cast", N + "a_feather", N + "a_twin"] and len(ae) == 8
    a_cast, feather, twin = ae[5:]
    quiet = copy.deepcopy(feather)
    quiet["name"] = N + "a_quiet"
    quiet["applied_effects"] = [x for x in quiet["applied_effects"] if x["effect"]["type"] == "Attack"]
    assert len(quiet["applied_effects"]) == 1
    flag = {"type": "AddCasterBuff", "buff_state": {"name": N + "q_cd", "duration": {"Time": {"tick": Q_CD}}},
            "only_to_enemy": False}
    ae[5:] = [{"type": "SwitchByBuff", "buff_name": N + "q_cd",
               "effect_buff": {"type": "Combine", "effects": [a_cast, feather, twin]},
               "effect_none": {"type": "Combine", "effects": [flag, qe[0], qe[2], quiet, copy.deepcopy(twin), quill]}}]
    names = {v.get("name") for v in d.get("view_projectiles", [])} | {v.get("name") for v in d.get("view_buffs", [])}
    assert N + "a_quiet" not in names and N + "q_cd" not in names


# Rakan's texts per language. The attack's is written out whole: the quill's sentence and Fey Feathers', kept within
# the longest base champion's skill text in each language (the skill details panel crams longer ones together;
# lint_mod.py TOOLTIP_MAX: zh 130, en 334, ja 147, ko 185 characters shown). E's and W's are W -> E's halves (W's
# head and the split as they were in the old text, E's edits for its new cast).
AP = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
LANGS = {
    "zh-hans": dict(
        names=("轻舞成双", "盛大登场"), att_old="掷出羽毛攻击。被动",
        attack=f"掷出羽毛攻击，每<#ffb900ff>5.5秒<>一次附带<#ff9028ff>微光飞翎<>：第一个敌人受到<#a974ffff>100<> + {AP}"
        f"<#a974ffff>80% 法强<><#a974ffff>魔法伤害<>，命中英雄则<#ffb900ff>3秒<>后或碰到队友时为自己和身边队友<#6aff55ff>回复<>"
        f"<#6aff55ff>70<> + {AP}<#6aff55ff>50% 法强<>生命。被动<#ff9028ff>异色羽裳<>：<#e8d44dff>70<> + {AP}<#e8d44dff>70% 法强<>"
        f"的<#e8d44dff>护盾<>，破掉<#ffb900ff>12秒<>后再生，每命中一名敌方英雄快<#ffb900ff>1秒<>。",
        w_head="<#ff9028ff>盛大登场<>：", cut="；随后<#ff9028ff>轻舞成双<>：", w_end="。",
        e_edits=[("飞到最近的友方英雄身边，给他", "附近有敌方英雄时，飞到一名友方英雄身边（先找被控制的，再找最近的），给他"),
                 ("（<#ffb900ff>3秒<>）。霞在附近时", "（<#ffb900ff>3秒<>）；身边没有友方英雄就给自己。霞在附近时")]),
    "zh-hant": dict(
        names=("戰鬥舞踊", "盛大登場"), att_old="擲出羽毛攻擊。被動",
        attack=f"擲出羽毛攻擊，每<#ffb900ff>5.5秒<>一次附帶<#ff9028ff>癒光飛翎<>：首個敵人受到<#a974ffff>100<> + {AP}"
        f"<#a974ffff>80% 魔法強度<><#a974ffff>魔法傷害<>，命中英雄<#ffb900ff>3秒<>後或碰到隊友時為自身和隊友<#6aff55ff>回復<>"
        f"<#6aff55ff>70<> + {AP}<#6aff55ff>50% 魔法強度<>生命。被動<#ff9028ff>奇異羽篷<>：<#e8d44dff>70<> + {AP}"
        f"<#e8d44dff>70% 魔法強度<>的<#e8d44dff>護盾<>，破掉<#ffb900ff>12秒<>後再生，每命中一名英雄快<#ffb900ff>1秒<>。",
        w_head="<#ff9028ff>盛大登場<>：", cut="；隨後<#ff9028ff>戰鬥舞踊<>：", w_end="。",
        e_edits=[("飛到最近的友方英雄身邊，提供", "附近有敵方英雄時，飛到一名友方英雄身邊（先找被控制的，再找最近的），提供"),
                 ("（<#ffb900ff>3秒<>）。剎雅在附近時", "（<#ffb900ff>3秒<>）；身邊沒有友方英雄就給自己。剎雅在附近時")]),
    "en": dict(
        names=("Battle Dance", "Grand Entrance"), att_old="Throws a feather. Passive ",
        attack=f"Throws a feather; every <#ffb900ff>5.5s<> an attack also flings <#ff9028ff>Gleaming Quill<>: "
        f"<#a974ffff>100<> + {AP}<#a974ffff>80% AP<> <#a974ffff>magic damage<> to the first enemy hit; on a champion hit he "
        f"<#6aff55ff>heals<> himself and nearby allies for <#6aff55ff>70<> + {AP}<#6aff55ff>50% AP<> after <#ffb900ff>3s<> or "
        f"when he touches an ally. Passive <#ff9028ff>Fey Feathers<>: a <#e8d44dff>70<> + {AP}<#e8d44dff>70% AP<> "
        f"<#e8d44dff>shield<>, back <#ffb900ff>12s<> after it breaks, <#ffb900ff>1s<> sooner per enemy champion hit.",
        w_head="<#ff9028ff>Grand Entrance<>: ", cut="; then <#ff9028ff>Battle Dance<>: ", w_end=".",
        e_edits=[("he flies to the nearest allied champion and gives him a", "With an enemy champion near, Rakan flies to "
                  "an allied champion (one under crowd control first, else the nearest) and gives them a"),
                 ("for <#ffb900ff>3s<>. With Xayah", "for <#ffb900ff>3s<>; with no ally around, he shields himself. "
                  "With Xayah")]),
    "ko": dict(
        names=("전쟁무도", "화려한 등장"), att_old="깃털을 던져 공격합니다. 기본 지속 효과 ",
        attack=f"깃털로 공격하며 <#ffb900ff>5.5초<>마다 <#ff9028ff>빛나는 깃털<>도 던져 처음 맞은 적에게 <#a974ffff>100<> + {AP}"
        f"<#a974ffff>주문력의 80%<>의 <#a974ffff>마법 피해<>를 입힙니다. 챔피언 적중 시 <#ffb900ff>3초<> 뒤나 아군에게 닿을 때 자신과 "
        f"아군을 <#6aff55ff>70<> + {AP}<#6aff55ff>주문력의 50%<> <#6aff55ff>회복<>. 지속 효과 <#ff9028ff>요술 망토<>: "
        f"<#e8d44dff>70<> + {AP}<#e8d44dff>주문력의 70%<>의 <#e8d44dff>보호막<>, 깨지면 <#ffb900ff>12초<> 뒤 재생, 적 챔피언 "
        f"적중마다 <#ffb900ff>1초<> 단축.",
        w_head="<#ff9028ff>화려한 등장<>: ", cut=" 이어서 <#ff9028ff>전쟁무도<>: ", w_end="",
        e_edits=[("가장 가까운 아군 챔피언에게 날아가 ", "근처에 적 챔피언이 있으면 아군 챔피언에게 날아가(군중 제어에 걸린 아군 먼저, "
                  "없으면 가장 가까운 아군) "),
                 ("<#e8d44dff>보호막<>을 씌웁니다. 자야가", "<#e8d44dff>보호막<>을 씌웁니다. 주변에 아군이 없으면 자신에게 씌웁니다. 자야가")]),
    "ja": dict(
        names=("バトルダンス", "華麗なる登場"), att_old="羽根を投げて攻撃。パッシブ",
        attack=f"羽根を投げて攻撃。<#ffb900ff>5.5秒<>ごとに<#ff9028ff>キラリ羽根<>も投げ、最初の敵に<#a974ffff>100<> + {AP}"
        f"<#a974ffff>魔力の80%<>の<#a974ffff>魔法ダメージ<>。チャンピオン命中で<#ffb900ff>3秒<>後か味方に触れた時、自身と味方を"
        f"<#6aff55ff>70<> + {AP}<#6aff55ff>魔力の50%<><#6aff55ff>回復<>。パッシブ<#ff9028ff>神秘の翼<>：<#e8d44dff>70<> + {AP}"
        f"<#e8d44dff>魔力の70%<>の<#e8d44dff>シールド<>、破壊後<#ffb900ff>12秒<>で再生、敵チャンピオン命中ごとに<#ffb900ff>1秒<>短縮。",
        w_head="<#ff9028ff>華麗なる登場<>：", cut="続いて<#ff9028ff>バトルダンス<>：", w_end="",
        e_edits=[("最も近い味方チャンピオンへ飛び、", "近くに敵チャンピオンがいると、味方チャンピオンへ飛び（行動妨害を受けている味方を優先、"
                  "いなければ最も近い味方）、"),
                 ("<#e8d44dff>シールド<>。ザヤが", "<#e8d44dff>シールド<>。周りに味方がいなければ自身に。ザヤが")]),
}
OLD_NAMES = {"zh-hans": ("微光飞翎", "盛大登场·轻舞成双"), "zh-hant": ("癒光飛翎", "盛大登場·戰鬥舞踊"),
             "en": ("Gleaming Quill", "Grand Entrance + Battle Dance"), "ko": ("빛나는 깃털", "화려한 등장 + 전쟁무도"),
             "ja": ("キラリ羽根", "華麗なる登場+バトルダンス")}


def texts(t):
    """[(old JSON fragment, new JSON fragment)] for Rakan's entries; [] when already done."""
    out = []
    for lang, c in LANGS.items():
        desc = t[lang]["description"]["league_rakan"]
        names = t[lang]["skill_name"]["league_rakan"]
        if names["skill1"] == c["names"][0]:
            continue
        assert (names["skill1"], names["skill2"]) == OLD_NAMES[lang], (lang, names)
        att, q, we = desc["attack"], desc["skill"], desc["skill2"]
        assert att.startswith(c["att_old"]) and we.startswith(c["w_head"]) and we.count(c["cut"]) == 1, lang
        w_part, e_part = we[len(c["w_head"]):].split(c["cut"])
        new_w = w_part + c["w_end"]
        new_e = e_part
        for old, new in c["e_edits"]:
            assert new_e.count(old) == 1, (lang, old)
            new_e = new_e.replace(old, new)
        js = lambda s: json.dumps(s, ensure_ascii=False)
        out += [(js(att), js(c["attack"])), (js(q), js(new_e)), (js(we), js(new_w)),
                (f'"skill1": {js(names["skill1"])}', f'"skill1": {js(c["names"][0])}'),
                (f'"skill2": {js(names["skill2"])}', f'"skill2": {js(c["names"][1])}')]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 while the kit or the texts are not done; write nothing")
    a = ap.parse_args()
    raw = open(lp(KIT), encoding="utf-8", newline="").read()
    d = json.loads(raw)
    traw = open(lp(TEXT), encoding="utf-8", newline="").read()
    edits = texts(json.loads(traw))
    if a.check:
        done = kit_done(d) and not edits
        print("done" if done else f"not done: kit {'done' if kit_done(d) else 'not split'}, {len(edits)} text edits left")
        sys.exit(0 if done else 1)
    changed = False
    if not kit_done(d):
        split(d)
        nl = "\r\n" if "\r\n" in raw else "\n"
        with open(lp(KIT), "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl)
        print(f"{os.path.relpath(KIT, ROOT)}: skill = Battle Dance, skill2 = Grand Entrance, Gleaming Quill in the attack")
        changed = True
    for old, new in edits:
        assert traw.count(old) == 1, old[:80]
        traw = traw.replace(old, new)
    if edits:
        with open(lp(TEXT), "w", encoding="utf-8", newline="") as f:
            f.write(traw)
        print(f"{os.path.relpath(TEXT, ROOT)}: {len(edits)} entries of league_rakan rewritten")
        changed = True
    if not changed:
        print("already done")


if __name__ == "__main__":
    main()
