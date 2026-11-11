//! 活体锻炉照英雄联盟（0.4.0，用户 2026-11-11：「奥恩锻造会强化所有装备 而不是和lol一样」「而且在4+6装备mod的情况下 还会强化符文
//! 创意工坊的mod 需要兼容」）。英雄联盟（V26.10 的 wiki）：
//!
//! - **大师工匠**：奥恩 13 级时自动把自己装备栏里第一件能锻造的传说装备升级成杰作；14–17 级每级给一名队友升级一件（每人一局一次），
//!   一共 5 件。杰作只升级那一件装备：它能升级的属性一共加 1000 金币的价值。
//! - **活体锻炉的属性**：他的额外护甲、额外魔抗、额外生命 +10%，每升级一件杰作再 +4%（5 件后 +30%）。
//!
//! 0.3.x 是对**全部装备**按百分比加：他自己的装备主属性一直 +20%（9 级、装备栏满了 +35%），装备栏满了的队友全部装备 +10%；
//! 4+6 装备 mod 的四个符文也在装备栏里（`item_keys`），一起被加、一起算进「满 6 件」，光晕也画在它们的图标上。
//!
//! 现在：
//! - 他自己的被动只加护甲、魔抗、生命：他的装备（开局就有的不算）这三项 +`P_ITEM`%，每锻造过一件杰作再 +`P_STEP`%（[`passive_bonus`]）。
//! - 杰作一共 [`UPGRADE_LV`] 件：TFM2 只有 12 级，英雄联盟的 13–17 级按 12/18 折算（向上取整）：他自己 9 级，队友 10、10、11、12 级。
//!   每人只锻造**一件**：装备栏里第一件传说装备（[`first_legendary`]），这一件的主属性 +`P_MASTER`%（1000 金币大约是一件传说装备
//!   属性的四成）；队友按分路的先后（[`ALLY_ORDER`]：下路、中路、打野、上路、辅助），轮到时手上还没有传说装备的先跳过，有了再锻造。
//!   这件升级成光辉版（Riot 装备 mod 的 `radiant_`）时杰作跟着它（还是装备栏里第一件传说装备）。
//! - **开局就有的东西不锻造**（[`START_T`] tick 内就在装备栏里的：4+6 装备 mod 的符文、出门装），也不算进被动。
//! - **什么是传说装备**（[`is_legendary`]，不锻造鞋、小件、符文）：引擎的装备表里有它就看阶——最高的两阶（传说、光辉；Riot 装备
//!   mod 的第 4、5 阶，游戏自带装备的第 4、5 阶），任何 mod 的装备都一样；装备表由装备构筑钩子 [`Watch`] 记下（只看不改）。Riot 装备
//!   mod 自己接管了出装（它的 DLL 里有 find_item_build_hook），引擎可能不再问钩子：这时查名单——游戏自带的第 4、5 阶
//!   [`BASE_LEGENDARY`]、Riot 装备 mod 的第 4 阶 [`RIOT_LEGENDARY`]，`radiant_` 开头的都算。

use std::collections::{HashMap, HashSet};
use std::sync::Mutex;

use mod_api_stable::*;

use super::{ITEMS, P_ITEM, P_MASTER, P_MASTER_LV, P_STEP};

/// 杰作的等级：第一件是他自己的，之后每件一名队友。英雄联盟 13、14、15、16、17 级，TFM2 的 12 级按 12/18 折算向上取整。
pub const UPGRADE_LV: [usize; 5] = [P_MASTER_LV, 10, 10, 11, 12];
/// 英雄联盟的大师工匠从 13 级开始、最高 18 级；TFM2 最高 12 级（测试核对 `UPGRADE_LV` 的折算）。
pub const LOL_FIRST_LV: usize = 13;
pub const LOL_MAX_LV: usize = 18;
pub const MAX_LV: usize = 12;
/// 队友锻造的先后（`LaneV1` 码：上 0、野 1、中 2、下 3、辅 4）：先下路、中路，再打野、上路，最后辅助。
pub const ALLY_ORDER: [u32; 5] = [3, 2, 1, 0, 4];
/// 开局这么多 tick 内就在装备栏里的东西（4+6 装备 mod 的符文、出门装）不锻造、不算进被动。
pub const START_T: usize = 300;
/// Riot 装备 mod 的光辉版：`radiant_` + 传说装备的 key（它的第 5 阶 104 件全是这样）。
pub const RADIANT: &str = "radiant_";

/// 游戏自带装备每条线的第 4、5 阶（`ITEMS` 的顺序；Riot 装备 mod 把它们改名成传说装备和光辉版：征服者大剑 = 饮血剑）。
pub const BASE_LEGENDARY: [&str; 12] = [
    "conquerors_greatsword", "warlords_final_judgement", "thunderclaw", "storm_sovereign", "eternal_iron_plate",
    "impregnable_fortress", "souls_edge", "veil_of_annihilation", "angels_fang", "prophet_of_the_abyss",
    "hourglass_of_eternity", "giants_horn_shard",
];

/// Riot 装备 mod（创意工坊 3739568852，1.0.9）的第 4 阶（传说装备）：它的 README 按阶列出、`text/item.i18n` 给出 key。
/// 引擎的装备表拿不到时才用。
pub const RIOT_LEGENDARY: [&str; 104] = [
    "abyssal_mask", "ardent_censer", "atmas_reckoning", "axiom_arc", "bandlepipes", "banshees_veil",
    "bastionbreaker", "black_cleaver", "blackfire_torch", "blade_of_the_ruined_king", "bloodletters_curse",
    "bloodsong", "celestial_opposition", "chempunk_chainsword", "chemtech_putrifier", "cloak_of_starry_night",
    "collector", "cosmic_drive", "dawncore", "dead_mans_plate", "deathblade", "deaths_dance", "diamond_tipped_spear",
    "dream_maker", "dusk_and_dawn", "echoes_of_helia", "eclipse", "edge_of_night", "endless_hunger",
    "essence_reaver", "experimental_hexplate", "feral_flare", "fiendhunter_bolts", "force_of_nature", "frozen_heart",
    "frozen_mallet", "grezs_spectral_lantern", "guardian_angel", "guinsoos_rageblade", "hamstringer", "heartsteel",
    "hexoptics_c44", "hextech_gunblade", "hollow_radiance", "hubris", "hullbreaker", "iceborn_gauntlet",
    "immortal_shieldbow", "imperial_mandate", "infinity_edge", "jaksho_the_protean", "kraken_slayer",
    "liandrys_torment", "lich_bane", "locket_of_the_iron_solari", "lord_dominiks_regards", "malignance",
    "mikaels_blessing", "mirage_blade", "moonstone_renewer", "morellonomicon", "mortal_reminder", "nashors_tooth",
    "navori_flickerblade", "night_harvester", "opportunity", "overlords_bloodmail", "philosophers_stone",
    "protectors_vow", "protoplasm_harness", "rabadons_deathcap", "randuins_omen", "rapid_firecannon",
    "ravenous_hydra", "riftmaker", "rite_of_ruin", "rod_of_ages", "runaans_hurricane", "rylais_crystal_scepter",
    "serpents_fang", "seryldas_grudge", "shadowflame", "solstice_sleigh", "spear_of_shojin", "spirit_visage",
    "staff_of_flowing_water", "statikk_shiv", "steraks_gage", "stormrazor", "stormsurge", "sundered_sky",
    "sword_of_blossoming_dawn", "terminus", "titanic_hydra", "trinity_force", "unending_despair", "void_staff",
    "voltaic_cyclosword", "warmogs_armor", "wits_end", "yun_tal_wildarrows", "zazzaks_realmspike", "zekes_herald",
    "zhonyas_hourglass",
];

// ===================== 引擎的装备表 =====================

/// 引擎的装备表：每件装备的阶（装备构筑钩子给的「每件能选的装备」），和那张表有几件装备（同一张表不再记）。
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Tiers {
    pub of: HashMap<String, usize>,
    pub top: usize,
    pub listed: usize,
}

impl Tiers {
    /// 至少三阶（基础装备、合成件、成装）才算数：都一样的表说明不了什么。
    pub fn from(keys: &[&str], tiers: &[Option<usize>]) -> Option<Tiers> {
        let of: HashMap<String, usize> =
            keys.iter().zip(tiers).filter_map(|(k, t)| t.map(|t| (k.to_string(), t))).collect();
        let top = of.values().copied().max()?;
        (top >= 2).then_some(Tiers { of, top, listed: keys.len() })
    }

    /// 表里有这件装备：在最高的两阶里（传说、光辉）就是 Some(true)；表里没有：None。
    pub fn legendary(&self, key: &str) -> Option<bool> {
        self.of.get(key).map(|&t| t + 1 >= self.top)
    }
}

static TIERS: Mutex<Option<Tiers>> = Mutex::new(None);

/// 现在知道的引擎装备表（钩子还没被问过就是 None）。
pub fn tiers() -> Option<Tiers> {
    TIERS.lock().ok().and_then(|t| t.clone())
}

/// 装备构筑钩子看到的装备表记下来（同样件数的表记过了就不再记）。-> 新记的：(件数, 最高阶, 每阶几件)
fn note(ctx: &StableItemBuildContext<'_>) -> Option<(usize, usize, Vec<usize>)> {
    let n = ctx.item_count();
    let mut g = TIERS.lock().ok()?;
    if g.as_ref().is_some_and(|t| t.listed == n) {
        return None;
    }
    let keys = ctx.item_keys();
    let tiers: Vec<Option<usize>> = (0..keys.len()).map(|i| ctx.item_tier(i)).collect();
    let t = Tiers::from(&keys, &tiers)?;
    let mut per = vec![0; t.top + 1];
    for &v in t.of.values() {
        per[v] += 1;
    }
    let out = (n, t.top, per);
    *g = Some(t);
    Some(out)
}

/// 装备构筑钩子：只记下引擎的装备表（每件装备的阶），不改任何人的出装（分数照旧、成装照旧）。引擎按优先级从小到大问每个钩子
/// （决定出装的里优先级最高的算数），它优先级最低、第一个被问，从不决定；最高优先级留给 league_unlock_guard 的闸门。
pub struct Watch;

impl Watch {
    fn look(ctx: &StableItemBuildContext<'_>) {
        if let Some((n, top, per)) = note(ctx) {
            if let Some(k) = super::counted("tiers") {
                super::wlog(format!("TIERS #{k}: the engine's item table has {n} items, tiers 0..={top} ({per:?} per tier): \
                                     the top two are the legendary ones a masterwork takes"));
            }
        }
    }
}

impl StableItemBuildHook for Watch {
    fn id(&self) -> String {
        format!("{}:tiers", super::ID)
    }

    fn priority(&self) -> i32 {
        i32::MIN
    }

    fn score_item(&self, ctx: &StableItemBuildContext<'_>, _candidate: usize, _base: f32) -> StableDraftDecision {
        Self::look(ctx);
        StableDraftDecision::Pass
    }

    fn decide_build(&self, ctx: &StableItemBuildContext<'_>) -> Vec<usize> {
        Self::look(ctx);
        Vec::new()
    }
}

// ===================== 计算（单元测试用） =====================

/// 是不是传说装备（杰作只锻造传说装备：鞋、小件、符文、出门装都不算）：引擎的装备表里有它就看阶；没有就查名单，`radiant_` 开头的都算。
pub fn is_legendary(tiers: Option<&Tiers>, key: &str) -> bool {
    if let Some(l) = tiers.and_then(|t| t.legendary(key)) {
        return l;
    }
    key.starts_with(RADIANT) || BASE_LEGENDARY.contains(&key) || RIOT_LEGENDARY.contains(&key)
}

/// 一个选手锻造哪一件：装备栏里（`keys` 的顺序）第一件传说装备，开局就有的（`start`）不算。-> (在装备栏里的位置, key)
pub fn first_legendary<'a>(keys: &'a [String], start: &HashSet<String>, legendary: impl Fn(&str) -> bool)
                           -> Option<(usize, &'a str)> {
    keys.iter().enumerate().find(|(_, k)| !start.contains(k.as_str()) && legendary(k)).map(|(i, k)| (i, k.as_str()))
}

/// 他这个等级能锻造几件杰作（他自己那件算第一件）。
pub fn upgrades_at(level: usize) -> usize {
    UPGRADE_LV.iter().filter(|&&l| level >= l).count()
}

/// 下一个锻造的队友：`cands` 是还没锻造过、手上有传说装备的 (玩家编号, 分路)；按 [`ALLY_ORDER`]，同一路取编号小的。
pub fn next_ally(cands: &[(usize, Option<u32>)]) -> Option<usize> {
    let rank = |lane: Option<u32>| lane.and_then(|l| ALLY_ORDER.iter().position(|&o| o == l)).unwrap_or(ALLY_ORDER.len());
    cands.iter().min_by_key(|&&(id, lane)| (rank(lane), id)).map(|&(id, _)| id)
}

/// 他自己活体锻炉的百分比：+`P_ITEM`%，每锻造过一件杰作再 +`P_STEP`%。
pub fn passive_pct(made: usize) -> usize {
    P_ITEM + P_STEP * made.min(UPGRADE_LV.len())
}

/// 他自己活体锻炉加的：装备（开局就有的不算）的护甲、魔抗、生命（`items` 是主属性：攻击、法强、护甲、生命、魔抗、攻速）。
pub fn passive_bonus(items: [i32; 6], made: usize) -> [i32; 6] {
    let pct = passive_pct(made) as i32;
    [0, 0, items[2] * pct / 100, items[3] * pct / 100, items[4] * pct / 100, 0]
}

/// 杰作加的：那一件装备的主属性 +`P_MASTER`%（向下取整）。
pub fn masterwork(item: [i32; 6]) -> [i32; 6] {
    item.map(|v| v * P_MASTER as i32 / 100)
}

/// 一件装备的主属性：他身上名字等于它的 key 的永久 buff（任何 mod 的装备都这样挂属性）；没有就查游戏的装备表 `ITEMS`。
pub fn key_stats(buffs: &[(String, bool, [i32; 6])], key: &str) -> Option<[i32; 6]> {
    buffs
        .iter()
        .find(|(name, permanent, _)| *permanent && name == key)
        .map(|&(_, _, s)| s)
        .or_else(|| ITEMS.iter().find(|(name, _)| *name == key).map(|&(_, s)| s))
}

/// 一个人这些装备的主属性加起来（`keys` 里每一件，开局就有的不算；同一件出了两件就算两次）。
pub fn sum_stats(buffs: &[(String, bool, [i32; 6])], keys: &[String], start: &HashSet<String>) -> [i32; 6] {
    let mut sum = [0; 6];
    // two copies of an item: two buffs of that name
    let mut used: HashMap<&str, usize> = HashMap::new();
    for k in keys.iter().filter(|k| !start.contains(k.as_str())) {
        let nth = used.entry(k.as_str()).or_insert(0);
        let s = buffs
            .iter()
            .filter(|(name, permanent, _)| *permanent && name == k)
            .nth(*nth)
            .map(|&(_, _, s)| s)
            .or_else(|| ITEMS.iter().find(|(name, _)| *name == k.as_str()).map(|&(_, s)| s));
        *nth += 1;
        if let Some(s) = s {
            for i in 0..6 {
                sum[i] += s[i];
            }
        }
    }
    sum
}

#[cfg(test)]
mod tests {
    use super::*;

    fn keys(v: &[&str]) -> Vec<String> {
        v.iter().map(|s| s.to_string()).collect()
    }

    #[test]
    fn the_masterwork_levels_are_leagues_13_to_17_on_twelve_levels() {
        let scaled: Vec<usize> = (0..UPGRADE_LV.len())
            .map(|k| ((LOL_FIRST_LV + k) * MAX_LV).div_ceil(LOL_MAX_LV))
            .collect();
        assert_eq!(scaled, UPGRADE_LV);
        assert_eq!(UPGRADE_LV[0], P_MASTER_LV);
        assert_eq!((upgrades_at(8), upgrades_at(9), upgrades_at(10), upgrades_at(11), upgrades_at(12)), (0, 1, 3, 4, 5));
    }

    #[test]
    fn one_legendary_item_is_forged_not_the_runes_boots_or_parts() {
        // 4+6 item mod: four runes from the start, then boots, a part and two legendary items
        let start: HashSet<String> = ["rune_a", "rune_b", "rune_c", "rune_d"].iter().map(|s| s.to_string()).collect();
        let ks = keys(&["rune_a", "rune_b", "rune_c", "rune_d", "berserkers_greaves", "bf_sword", "infinity_edge",
                        "radiant_terminus"]);
        let leg = |k: &str| is_legendary(None, k);
        assert_eq!(first_legendary(&ks, &start, leg), Some((6, "infinity_edge")));
        // the same with a legendary rune name: it was there from the start
        let ks2 = keys(&["heartsteel", "boots"]);
        let start2: HashSet<String> = ["heartsteel".to_string()].into();
        assert_eq!(first_legendary(&ks2, &start2, leg), None);
        // the game's own lines: tier 4 and 5 only
        assert!(is_legendary(None, "conquerors_greatsword") && is_legendary(None, "giants_horn_shard"));
        assert!(!is_legendary(None, "ruinous_blade") && !is_legendary(None, "ironsword"));
        assert!(!is_legendary(None, "sorcerers_shoes") && !is_legendary(None, "a_mods_rune"));
        // a legendary upgraded to its radiant version: still the first one
        let ks3 = keys(&["boots", "radiant_infinity_edge", "kraken_slayer"]);
        assert_eq!(first_legendary(&ks3, &HashSet::new(), leg), Some((1, "radiant_infinity_edge")));
    }

    #[test]
    fn the_engines_table_decides_when_it_is_known() {
        let t = Tiers::from(&["boots", "bf_sword", "a_mod_blade", "a_mod_radiant", "a_mod_rune", "infinity_edge"],
                            &[Some(0), Some(1), Some(3), Some(4), Some(0), Some(2)])
            .unwrap();
        assert_eq!(t.top, 4);
        assert!(is_legendary(Some(&t), "a_mod_blade") && is_legendary(Some(&t), "a_mod_radiant"));
        assert!(!is_legendary(Some(&t), "a_mod_rune") && !is_legendary(Some(&t), "bf_sword"));
        // the table outranks the list (here infinity_edge sits two below the top)
        assert!(!is_legendary(Some(&t), "infinity_edge"));
        // not in the table: the list
        assert!(is_legendary(Some(&t), "terminus") && !is_legendary(Some(&t), "something_else"));
        // a flat table says nothing
        assert_eq!(Tiers::from(&["a", "b"], &[Some(1), Some(1)]), None);
    }

    #[test]
    fn carries_are_forged_first() {
        // (player, lane): top 0, jungle 1, mid 2, bottom 3, support 4
        assert_eq!(next_ally(&[(1, Some(0)), (2, Some(4)), (3, Some(3)), (4, Some(2))]), Some(3));
        assert_eq!(next_ally(&[(1, Some(0)), (2, Some(4)), (4, Some(2))]), Some(4));
        assert_eq!(next_ally(&[(2, Some(4)), (1, Some(1))]), Some(1));
        assert_eq!(next_ally(&[(7, None), (2, Some(4))]), Some(2));
        assert_eq!(next_ally(&[]), None);
    }

    #[test]
    fn his_passive_is_armour_mr_and_health_plus_4_per_masterwork() {
        let items = [30, 40, 50, 1000, 20, 15];
        assert_eq!(passive_bonus(items, 0), [0, 0, 5, 100, 2, 0]);
        assert_eq!(passive_pct(5), 30);
        assert_eq!(passive_pct(9), 30, "five masterworks at most");
        assert_eq!(passive_bonus(items, 5), [0, 0, 15, 300, 6, 0]);
        // the masterwork: one item's main stats
        assert_eq!(masterwork([35, 0, 0, 250, 0, 15]), [14, 0, 0, 100, 0, 6]);
    }

    #[test]
    fn stats_come_from_the_item_buffs_and_skip_the_start() {
        let on = vec![
            ("rune_a".to_string(), true, [0, 0, 9, 0, 9, 0]),
            ("heartsteel".to_string(), true, [0, 0, 0, 600, 0, 0]),
            ("long_sword".to_string(), true, [10, 0, 0, 0, 0, 0]),
            ("long_sword".to_string(), true, [10, 0, 0, 0, 0, 0]),
            ("heartsteel".to_string(), false, [99, 0, 0, 0, 0, 0]),
        ];
        let start: HashSet<String> = ["rune_a".to_string()].into();
        let ks = keys(&["rune_a", "heartsteel", "long_sword", "long_sword", "steel_armor"]);
        // two long swords, the game's own steel armour from its table, not the rune
        assert_eq!(sum_stats(&on, &ks, &start), [20, 0, 20, 600, 0, 0]);
        assert_eq!(key_stats(&on, "heartsteel"), Some([0, 0, 0, 600, 0, 0]));
        assert_eq!(key_stats(&on, "nothing"), None);
    }
}
