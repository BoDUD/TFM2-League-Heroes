"""Stack counts in the game's own champion panel, next to the skill icons, as in League (2026-11-11).

    python tools/kit/stack_nums.py --write   # every listed hero's `stack_skill_index` (league/ and the add-ons' copies)
                                             # and league.dll's table addons/league_main/src/stack_table.rs
    python tools/kit/stack_nums.py --check   # (CI) both up to date
    python tools/kit/stack_nums.py --list    # the heroes, their rules and their icons

Why (the user, 2026-11-11): 「现在叠层数的技能英雄在游戏里看不到多少层 有没有办法在游戏里能看到？」. A number over the head came
first (「放头顶有点丑啊」), then 「不能放技能栏里面吗 和联盟一样」 -> 「技能栏层数格」.

The match's champion panel (`ingame.champion_tooltip`, bottom left: face, health, experience, the three skill icons)
has a `stack_info` - an icon and a number - right of the skill icons, hidden unless the champion's
`ChampionInfo::stack_skill_index()` is set (TeamfightManager2.exe 0.7.1, the panel's update at 0x8729a0): then it shows
that skill's icon and the champion's stat `stack`. A data champion's `stack_skill_index` is the .data_champion field of
that name (0 skill, 1 skill2, 2 ult). `apply` writes it for every hero of STACKS ("skill"), in league/champion/ and in
every add-on's copy of him; the kit scripts' `build = stack_nums.wrap(build)` keep it in a rebuild. It also drops the
over-head number bindings (`<hero>_sn_*` view_buffs) of the first version.

The data cannot count a stack (it only asks whether a buff is on a unit), so league.dll counts in the simulation and
writes `stack` (addons/league_main/src/stacks.rs): STACKS below is its table (stack_table.rs, generated).
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEAGUE = os.path.join(ROOT, "league")
TABLE_RS = os.path.join(ROOT, "addons", "league_main", "src", "stack_table.rs")
FIELD = "stack_skill_index"

# ---------------------------------------------------------------------------------------------------------------- table
# hero -> how to read the number from his own buffs:
#   count:  the instances of one buff (a stack is one more instance)
#   sum:    one stat of those instances added up, when a stack is not always one (Veigar's champion stack is 5 ability
#           power: League counts it 5 stacks, the number is his ability power from it; Nasus's Siphoning Strike damage;
#           Sion's health from kills) - "stat" names the field (magic_power / hp / attack)
#   ladder: the highest k with <prefix><k> on him, k = 1..rungs, times "step" (default 1: Rumble's heat and Gnar's /
#           Shyvana's rage 10 a rung, Tryndamere's fury 20 - League's 0..100); with "full" (a flag buff: Darius's Noxian
#           Might, Gnar's full Rage) on him, the number is "top"
# cap: the most the number shows; skill: whose icon the panel shows beside it (0 skill, 1 skill2, 2 ult - the ability
# the stacks feed, else the first); label: what the number is (for --list and the docs); passive: an add-on's own
# counter (its code writes the rungs, no data does) - only the copy whose passive is that native shows the box, the
# main pack's kit (no add-on, the number would stay 0) does not
STACKS = [
    {"hero": "league_veigar", "sum": "league_veigar_p_stack", "stat": "magic_power", "cap": 999, "skill": 0,
     "label": "维迦「超凡邪力」叠的法术强度（英雄联盟的层数）"},
    {"hero": "league_nasus", "sum": "league_nasus_q_stack", "stat": "magic_power", "cap": 999, "skill": 0,
     "label": "内瑟斯「汲魂痛击」叠的伤害（英雄联盟的层数）"},
    {"hero": "league_chogath", "count": "league_chogath_r_stack", "cap": 999, "skill": 2, "label": "科加斯「盛宴」层数"},
    {"hero": "league_smolder", "count": "league_smolder_p_st", "cap": 999, "skill": 0, "label": "斯莫德「龙之研习」层数"},
    {"hero": "league_senna", "count": "league_senna_mist", "cap": 999, "skill": 0, "label": "赛娜「赦除」黑雾层数"},
    {"hero": "league_swain", "count": "league_swain_frag", "cap": 999, "skill": 2, "label": "斯维因「灵魂碎片」"},
    {"hero": "league_sion", "sum": "league_sion_k_hp", "stat": "hp", "cap": 999, "skill": 0,
     "label": "赛恩「灵魂熔炉」击杀加的生命"},
    {"hero": "league_kindred", "count": "league_kindred_p_mark", "cap": 999, "skill": 0, "label": "千珏「千珏之印」印记"},
    {"hero": "league_aurelionsol", "ladder": "league_aurelionsol_d", "rungs": 30, "cap": 30, "skill": 2,
     "label": "奥瑞利安·索尔「星海焕然」星尘层数"},
    {"hero": "league_belveth", "ladder": "league_belveth_l", "rungs": 8, "cap": 8, "skill": 0,
     "label": "卑尔维斯「溶烛化紫」永久攻速层数"},
    # the capped counters League shows that had no picture, or one only when full (the user, 2026-11-11: 「加常见的那些」)
    {"hero": "league_caitlyn", "ladder": "league_caitlyn_hs_", "rungs": 5, "cap": 5, "skill": 0,
     "label": "凯特琳「爆头」计数（第 6 发爆头）"},
    {"hero": "league_darius", "ladder": "league_darius_hemo_", "rungs": 4, "full": "league_darius_might", "top": 5,
     "cap": 5, "skill": 2, "label": "德莱厄斯「出血」层数（5 = 诺克萨斯之力）"},
    {"hero": "league_pantheon", "ladder": "league_pantheon_m", "rungs": 4, "full": "league_pantheon_pw", "top": 5,
     "cap": 5, "skill": 0, "label": "潘森「矢志不退」层数（5 = 下一个技能强化）"},
    {"hero": "league_kennen", "ladder": "league_kennen_a_", "rungs": 4, "cap": 4, "skill": 0,
     "label": "凯南「电刃」普攻计数（第 5 下）"},
    {"hero": "league_jinx", "ladder": "league_jinx_revup_", "rungs": 3, "cap": 3, "skill": 0, "label": "金克丝「砰砰」攻速层数"},
    {"hero": "league_masteryi", "ladder": "league_masteryi_ds_", "rungs": 3, "cap": 3, "skill": 0, "label": "易「双重打击」计数"},
    {"hero": "league_twistedfate", "ladder": "league_twistedfate_e", "rungs": 3, "cap": 3, "skill": 0,
     "label": "崔斯特「卡牌骗术」计数（第 4 下）"},
    {"hero": "league_rumble", "ladder": "league_rumble_h", "rungs": 9, "step": 10, "full": "league_rumble_oh", "top": 100,
     "cap": 100, "skill": 0, "label": "兰博「机械重组」热量（100 = 过热）"},
    {"hero": "league_annie", "ladder": "league_annie_pyro_", "rungs": 3, "full": "league_annie_pyro_ready", "top": 4,
     "cap": 4, "skill": 0, "label": "安妮「嗜火」层数（4 = 下一个技能晕人）"},
    {"hero": "league_irelia", "ladder": "league_irelia_pv", "rungs": 4, "cap": 4, "skill": 0,
     "label": "艾瑞莉娅「艾欧尼亚热诚」层数"},
    {"hero": "league_kayle", "ladder": "league_kayle_zeal", "rungs": 5, "cap": 5, "skill": 0, "label": "凯尔「狂热」层数"},
    {"hero": "league_gnar", "ladder": "league_gnar_rg", "rungs": 9, "step": 10, "full": "league_gnar_full", "top": 100,
     "cap": 100, "skill": 2, "label": "纳尔「狂怒基因」怒气（100 = 满怒）"},
    {"hero": "league_shyvana", "ladder": "league_shyvana_fy", "rungs": 9, "step": 10, "full": "league_shyvana_full",
     "top": 100, "cap": 100, "skill": 2, "label": "希瓦娜「魔龙降世」龙怒（100 = 满）"},
    {"hero": "league_tryndamere", "ladder": "league_tryndamere_f_", "rungs": 5, "step": 20, "cap": 100, "skill": 0,
     "label": "泰达米尔「战斗狂怒」怒气"},
    # the Bonetooth Necklace's trophies (2026-11-14, with League's necklace itself): the main kit and league_rengar_bush
    # both hang league_rengar_bt1..bt5 one after another, so the highest rung on him is the count
    {"hero": "league_rengar", "ladder": "league_rengar_bt", "rungs": 5, "cap": 5, "skill": 2,
     "label": "雷恩加尔「骨齿项链」战利品"},
    # the add-on's Silver Serpents in hand (2026-11-12, the user: 「船长银蛇币的系统能做吗」): league_gangplank writes
    # league_gangplank_sv_<n> (its unit test serpent_count_on_the_panel)
    {"hero": "league_gangplank", "ladder": "league_gangplank_sv_", "rungs": 9999, "cap": 9999, "skill": 2,
     "passive": "league_gangplank:scurvy", "label": "普朗克「银蛇币」（附加包）"},
]


# --------------------------------------------------------------------------------------------------------- the data
def row(hero):
    return next((r for r in STACKS if r["hero"] == hero), None)


def passive_ref(champ):
    """The native passive a copy calls (an add-on's), or None."""
    p = champ.get("passive")
    return p.get("passive_ref") if isinstance(p, dict) else None


def apply(champ):
    """The champion with his panel icon (`stack_skill_index`) when he is listed, and without the over-head number
    bindings (`<hero>_sn_*`) of the first version; other keys and views keep their order."""
    hero = champ.get("id", "")
    prefix = f"{hero}_sn_"
    if any(str(v.get("name", "")).startswith(prefix) for v in champ.get("view_buffs", [])):
        champ["view_buffs"] = [v for v in champ["view_buffs"] if not str(v.get("name", "")).startswith(prefix)]
    r = row(hero)
    if r is not None and r.get("passive", passive_ref(champ)) != passive_ref(champ):
        champ.pop(FIELD, None)      # an add-on's counter: not in a copy without its passive
        r = None
    if r is not None:
        champ[FIELD] = r["skill"]
    return champ


def wrap(build):
    """`build = stack_nums.wrap(build)` under a kit script's build(): every caller gets the kit with the field."""
    import functools

    @functools.wraps(build)
    def built(*a, **k):
        return apply(build(*a, **k))
    return built


def dumps_main(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"


def copies():
    """Every data file of a hero: league/champion/ and the add-ons' override/ copies."""
    return sorted(glob.glob(os.path.join(LEAGUE, "champion", "*.data_champion")) +
                  glob.glob(os.path.join(ROOT, "addons", "*", "override", "*.data_champion")))


def data_problems(write=False):
    out = []
    for path in copies():
        raw = open(path, "rb").read().decode("utf-8")
        champ = json.loads(raw)
        if champ.get("id") != os.path.basename(path).split(".")[0]:
            continue
        want = apply(json.loads(raw))
        if want == champ:
            continue
        if write:
            new = dumps_main(want)
            if "\r\n" not in raw:       # the add-ons' make_override.py write LF (git stores LF either way)
                new = new.replace("\r\n", "\n")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            out.append(f"wrote {os.path.relpath(path, ROOT)}")
        else:
            out.append(f"{os.path.relpath(path, ROOT)}: its {FIELD} is not up to date: python tools/kit/stack_nums.py --write")
    return out


# ------------------------------------------------------------------------------------------------------- league.dll
STATS = {"magic_power": "MagicPower", "hp": "Hp", "attack": "Attack"}


def rule_rs(r):
    if "count" in r:
        return f'Rule::Count("{r["count"]}")'
    if "sum" in r:
        return f'Rule::Sum("{r["sum"]}", Stat::{STATS[r["stat"]]})'
    full = f'Some(("{r["full"]}", {r["top"]}))' if "full" in r else "None"
    return (f'Rule::Ladder {{ prefix: "{r["ladder"]}", rungs: {r["rungs"]}, step: {r.get("step", 1)}, '
            f'full: {full} }}')


def table_rs():
    lines = ["//! The stack counts league.dll writes for the champion panel (src/stacks.rs): generated by",
             "//! tools/kit/stack_nums.py from its STACKS - do not edit by hand.", "",
             "use super::stacks::{Rule, Stack, Stat};", "",
             f"pub const STACKS: [Stack; {len(STACKS)}] = ["]
    for r in sorted(STACKS, key=lambda r: r["hero"]):
        lines.append(f'    Stack {{ hero: "{r["hero"]}", rule: {rule_rs(r)}, cap: {r["cap"]} }},')
    lines += ["];", ""]
    return "\n".join(lines)


def table_problems():
    have = open(TABLE_RS, encoding="utf-8").read().replace("\r\n", "\n") if os.path.exists(TABLE_RS) else ""
    if have != table_rs():
        return [f"{os.path.relpath(TABLE_RS, ROOT)} is out of date: python tools/kit/stack_nums.py --write"]
    return []


def rules_problems():
    """Every counted buff / ladder rung exists in the hero's own data (a renamed buff would count nothing), every icon
    is one of his three, and nothing still draws the old over-head numbers. An add-on's own counter ("passive"): some
    copy of the hero calls that passive (its code writes the rungs, its unit tests check the names)."""
    out = []
    for r in STACKS:
        if "passive" in r:
            mine = [p for p in copies() if os.path.basename(p) == r["hero"] + ".data_champion"
                    and passive_ref(json.loads(open(p, "rb").read().decode("utf-8"))) == r["passive"]]
            if not mine:
                out.append(f"{r['hero']}: no copy of it calls {r['passive']}")
            names = []
        else:
            raw = open(os.path.join(LEAGUE, "champion", r["hero"] + ".data_champion"), encoding="utf-8").read()
            names = ([r["count"]] if "count" in r else [r["sum"]] if "sum" in r else
                     [f'{r["ladder"]}{k}' for k in (1, r["rungs"])] + ([r["full"]] if "full" in r else []))
        if "sum" in r and f'"{r["stat"]}"' not in raw:
            out.append(f"{r['hero']}: no buff of it carries {r['stat']}")
        for n in names:
            if f'"{n}"' not in raw:
                out.append(f"{r['hero']}: {n} is not in its data")
        if r["skill"] not in (0, 1, 2):
            out.append(f"{r['hero']}: skill {r['skill']} is not 0, 1 or 2")
    if os.path.exists(os.path.join(LEAGUE, "effects", "league_stack_num#sheet.png")):
        out.append("league/effects/league_stack_num is still there (the over-head numbers are gone)")
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for r in STACKS:
            what = r.get("count") or (f'{r["sum"]} {r["stat"]}' if "sum" in r else f'{r["ladder"]}1..{r["rungs"]}')
            print(f'{r["hero"]:22s} {what:34s} cap {r["cap"]:5d}  icon {r["skill"]}  {r["label"]}')
    if a.write:
        with open(TABLE_RS, "w", encoding="utf-8", newline="\n") as f:
            f.write(table_rs())
        print("wrote", os.path.relpath(TABLE_RS, ROOT))
        for line in data_problems(write=True):
            print(line)
    if a.check:
        bad = rules_problems() + table_problems() + data_problems()
        for b in bad:
            print(b)
        if bad:
            sys.exit(f"{len(bad)} problem(s)")
        print(f"stack counts: {len(STACKS)} heroes, {FIELD} and league.dll's table up to date")


if __name__ == "__main__":
    main()
