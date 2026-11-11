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
//! - **4+6 装备 mod 按它自己的 key 认**（0.4.3，[`alele_tier`] / [`is_rune`]，用户 11-11 把游戏 0.7.2 版的 4+6 装进了游戏）：它的
//!   装备 key 是 `item_t<阶>_…`，只有第 5 阶是成装（传说装备），第 4 阶还是合成到一半的部件；符文 `runes…` 在引擎的装备表里也排在
//!   第 5 阶，而且符文是一阶一阶换上来的、不一定开局就在——所以它既不能查名单（名单里没有），也不能照「最高的两阶」，符文也不能
//!   只靠 [`START_T`]：符文什么时候到手都当开局就有的东西（不锻造、不算进被动）。2026-11-11 游戏 0.7.2 的日志里引擎一次都
//!   没有问过装备构筑钩子（没有 `TIERS`，131 行 `ITEMS` 全是 `by the list`），而它的成装不在名单里：0.4.3 以前在 4+6 下锻造不出杰作。
//! - **4+6 的装备属性从哪里读**（0.4.4，[`item_stats`]）：0.4.3 装进游戏后的第一局（2026-11-11 21:2x）五件杰作都锻造了、光晕也
//!   画对了格，可是整份日志没有一行 `FORGE`——杰作和他自己的被动加的都是 0：4+6 的装备身上没有「名字等于 key 的永久 buff」。
//!   它的 DLL 里每件装备另有一个名字 `item_owned_<mod id>_<key>_<8 位十六进制>`（buff 名最长 64 字节，key 放不下就只留开头
//!   一段，[`owned_buff_of`]），405 件里 392 件有。所以一件装备的主属性依次从这几处读：名字等于 key 的永久 buff（游戏自带的、
//!   数据 mod 的、Riot 装备 mod 的）→ 4+6 的 `item_owned_…` 永久 buff（主属性不全是 0 才算）→ 4+6 自带的装备目录
//!   `mods/alele_runes_and_items/item-catalog.json` 里这件的属性（[`catalog`]，只读它的文件，不随我们的 mod 发）→ 游戏的装备表
//!   `ITEMS`。`item_owned_…` 是不是真的带着属性是从它的 DLL 的字符串推的，没在游戏里看过：日志 `SOURCE` 记下每件装备的属性
//!   是从哪一处读到的，读不到 buff 的还记下这个人身上的永久 buff。

use std::collections::{HashMap, HashSet};
use std::path::PathBuf;
use std::sync::{Mutex, OnceLock};

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
/// alele 的 4+6 符文装备 mod（创意工坊 3785335066，游戏 0.7.2 版是 `alele_runes_and_items`；key 见它的 item-catalog.json）的
/// 装备：`item_t<阶>_…`，331 件。第 1–4 阶是部件和合成到一半的（第 4 阶 99 件，「净蚀 + 十字镐」这种），第 5 阶 143 件是成装
/// （黑色切割者 `item_t5_134_1_2_101_0_0_0`）。
pub const ALELE_ITEM: &str = "item_t";
/// 4+6 装备 mod 从这一阶起是成装（传说装备）。
pub const ALELE_LEGENDARY_TIER: usize = 5;
/// 4+6 装备 mod 的符文：70 个 `runes<系>_…`、4 个换阶用的 `runes_transition_t<阶>`（引擎的装备表里符文也是第 5 阶）。
pub const ALELE_RUNE: &str = "runes";
/// 4+6 装备 mod 给每件装备（符文也是）起的 buff 名的开头：`item_owned_<mod id>_<key>_<8 位十六进制>`。
pub const OWNED: &str = "item_owned_";
/// 这种名字最长这么多个字符（buff 名最长 64 字节）：key 放不下时只留开头的一段——`alele_runes_and_items` 留 20 个字符：
/// `item_owned_alele_runes_and_items_item_t5_134_1_2_101__8c2bbef1` 是 `item_t5_134_1_2_101_0_0_0` 的。
pub const OWNED_NAME_MAX: usize = 62;
/// key（和它截短后留下的那一段）至少这么多个字符才认：mod id 里也有下划线，短了分不清哪里是 mod id、哪里是 key
/// （它的 key 最短的是 12 个字符的符文 `runes0_0_0_0`）。
pub const OWNED_STEM_MIN: usize = 8;
/// 4+6 装备 mod 的文件夹名（mod id）和它的装备目录；目录也可以用这个环境变量指到别处（开发、测试用）。
pub const ALELE_MOD: &str = "alele_runes_and_items";
pub const ALELE_CATALOG: &str = "item-catalog.json";
pub const ALELE_CATALOG_ENV: &str = "LEAGUE_ALELE_CATALOG";
/// 装备目录里主属性的名字，顺序和 `main_stats` 一样（攻击、法强、护甲、生命、魔抗、攻速 %）。
pub const CATALOG_STATS: [&str; 6] = ["attack", "magic_power", "defence", "hp", "magic_resistance", "attack_speed_mult"];

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

/// 4+6 装备 mod 的符文（`runes` 后面跟着数字或下划线）：什么时候到手都当开局就有的东西——不锻造、不算进他的被动、玩家栏里
/// 排在装备前面。
pub fn is_rune(key: &str) -> bool {
    key.strip_prefix(ALELE_RUNE)
        .and_then(|rest| rest.chars().next())
        .is_some_and(|c| c.is_ascii_digit() || c == '_')
}

/// 4+6 装备 mod 的装备 key 里写着的阶（`item_t5_…` -> 5）；不是它的 key：None。
pub fn alele_tier(key: &str) -> Option<usize> {
    let (tier, _) = key.strip_prefix(ALELE_ITEM)?.split_once('_')?;
    tier.parse().ok()
}

/// 是不是传说装备（杰作只锻造传说装备：鞋、小件、符文、出门装都不算）：4+6 装备 mod 的 key 自己写着阶（第 5 阶才是成装，
/// 符文不算）；别的装备引擎的装备表里有它就看阶；没有就查名单，`radiant_` 开头的都算。
pub fn is_legendary(tiers: Option<&Tiers>, key: &str) -> bool {
    if is_rune(key) {
        return false;
    }
    if let Some(t) = alele_tier(key) {
        return t >= ALELE_LEGENDARY_TIER;
    }
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

/// 一个英雄身上的 buff：名字、永久不永久、主属性（攻击、法强、护甲、生命、魔抗、攻速 %）。
pub type Buffs = [(String, bool, [i32; 6])];
/// 4+6 装备 mod 的装备目录：key -> 主属性。
pub type Catalog = HashMap<String, [i32; 6]>;

/// 一件装备的主属性是从哪里读到的（日志 `SOURCE`）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source {
    /// 名字等于 key 的永久 buff：游戏自带的、数据 mod 的、Riot 装备 mod 的装备。
    Named,
    /// 4+6 装备 mod 的 `item_owned_…` 永久 buff。
    Owned,
    /// 4+6 装备 mod 的装备目录。
    Catalog,
    /// 游戏的装备表 `ITEMS`。
    Table,
}

/// buff `name` 是不是装备 `key` 的 `item_owned_<mod id>_<key>_<8 位十六进制>`：`<mod id>_` 后面是整个 key，或者——名字已经是
/// 最长（[`OWNED_NAME_MAX`]）时——key 开头放得下的那一段。key 开头一样长到放不下的几件（`item_t5_213456_0_0_101…` 到
/// `…104…`）分不开：都算。
pub fn owned_buff_of(name: &str, key: &str) -> bool {
    let Some((body, hash)) = name.strip_prefix(OWNED).and_then(|rest| rest.rsplit_once('_')) else { return false };
    if key.len() < OWNED_STEM_MIN || hash.len() != 8 || !hash.bytes().all(|b| b.is_ascii_hexdigit()) {
        return false;
    }
    // "<mod id>_<stem>": something, an underscore, then the stem
    let ends = |stem: &str| body.strip_suffix(stem).is_some_and(|m| m.len() > 1 && m.ends_with('_'));
    ends(key)
        || (name.len() == OWNED_NAME_MAX
            && (OWNED_STEM_MIN..key.len()).rev().any(|n| key.is_char_boundary(n) && ends(&key[..n])))
}

/// 一件装备的主属性，和它是从哪里读到的、用的是哪个 buff（`buffs` 里的位置）：名字等于 key 的永久 buff；4+6 的
/// `item_owned_…` 永久 buff（主属性不全是 0 才算数）；4+6 的装备目录；`item_owned_…` 是全 0 的也认（只有副属性的装备）；
/// 最后是游戏的装备表 `ITEMS`。`taken` 是已经算给别的装备的 buff（同一件出了两件：两个 buff 各算一次）。
pub fn item_stats(buffs: &Buffs, key: &str, taken: &[usize], catalog: Option<&Catalog>)
                  -> Option<([i32; 6], Source, Option<usize>)> {
    let find = |named: bool| {
        (0..buffs.len()).find(|i| {
            let (name, permanent, _) = &buffs[*i];
            *permanent && !taken.contains(i) && if named { name == key } else { owned_buff_of(name, key) }
        })
    };
    if let Some(i) = find(true) {
        return Some((buffs[i].2, Source::Named, Some(i)));
    }
    let owned = find(false);
    if let Some(i) = owned.filter(|&i| buffs[i].2 != [0; 6]) {
        return Some((buffs[i].2, Source::Owned, Some(i)));
    }
    if let Some(&s) = catalog.and_then(|c| c.get(key)) {
        // its buff without main stats (if there is one) goes with it: a second copy of the item finds its own
        return Some((s, Source::Catalog, owned));
    }
    if let Some(i) = owned {
        return Some((buffs[i].2, Source::Owned, Some(i)));
    }
    ITEMS.iter().find(|(name, _)| *name == key).map(|&(_, s)| (s, Source::Table, None))
}

/// 一件装备的主属性（[`item_stats`]）。
pub fn key_stats(buffs: &Buffs, key: &str, catalog: Option<&Catalog>) -> Option<[i32; 6]> {
    item_stats(buffs, key, &[], catalog).map(|(s, _, _)| s)
}

/// 一个人这些装备的主属性加起来（`keys` 里每一件，开局就有的不算；同一件出了两件就算两次）。
pub fn sum_stats(buffs: &Buffs, keys: &[String], start: &HashSet<String>, catalog: Option<&Catalog>) -> [i32; 6] {
    let mut sum = [0; 6];
    // two copies of an item: two buffs, each counted once
    let mut taken = Vec::new();
    for k in keys.iter().filter(|k| !start.contains(k.as_str())) {
        if let Some((s, _, used)) = item_stats(buffs, k, &taken, catalog) {
            taken.extend(used);
            for i in 0..6 {
                sum[i] += s[i];
            }
        }
    }
    sum
}

// ===================== 4+6 装备 mod 的装备目录 =====================

/// `: "…"` 开头的那个字符串（它的 key 里没有转义）。
fn string_value(text: &str) -> Option<&str> {
    let t = text.trim_start().strip_prefix(':')?.trim_start().strip_prefix('"')?;
    t.find('"').map(|end| &t[..end])
}

/// `text` 里 `name` 后面那个 `{ … }` 里面的字（值是对象才有，`null` 就是 None；里面没有再套对象）。
fn object_of<'a>(text: &'a str, name: &str) -> Option<&'a str> {
    let t = &text[text.find(name)? + name.len()..];
    let t = t.trim_start().strip_prefix(':')?.trim_start().strip_prefix('{')?;
    t.find('}').map(|end| &t[..end])
}

/// `{ … }` 里 `"name": 数字` 的那个数字。
fn number_of(object: &str, name: &str) -> Option<f64> {
    let quoted = format!("\"{name}\"");
    let t = &object[object.find(&quoted)? + quoted.len()..];
    let t = t.trim_start().strip_prefix(':')?.trim_start();
    let end = t.find(|c: char| !(c.is_ascii_digit() || matches!(c, '-' | '+' | '.' | 'e' | 'E'))).unwrap_or(t.len());
    t[..end].parse().ok()
}

/// 4+6 装备 mod 的装备目录（它的 `item-catalog.json`，405 件）里每件装备的主属性。每件是 `"gameKey": "<key>"`，后面跟着
/// `"packageValues": { … "stats": { "attack": 25, … } }`（它出厂的数值；符文的 `stats` 是空的，`runtimeEffective` 的是
/// `null`）。附加包没有 JSON 库，照这个样子找。
pub fn parse_catalog(json: &str) -> Catalog {
    const KEY: &str = "\"gameKey\"";
    let mut out = Catalog::new();
    let mut rest = json;
    while let Some(i) = rest.find(KEY) {
        rest = &rest[i + KEY.len()..];
        // this item's text: up to the next one's key
        let item = &rest[..rest.find(KEY).unwrap_or(rest.len())];
        let Some(key) = string_value(item) else { continue };
        let Some(stats) = item.find("\"packageValues\"").and_then(|p| object_of(&item[p..], "\"stats\"")) else { continue };
        let mut s = [0; 6];
        for (slot, name) in s.iter_mut().zip(CATALOG_STATS) {
            *slot = number_of(stats, name).map_or(0, |v| v.round() as i32);
        }
        out.insert(key.to_string(), s);
    }
    out
}

/// 装备目录可能在哪里：环境变量 [`ALELE_CATALOG_ENV`]，再是游戏 EXE 旁边的 `mods/alele_runes_and_items/item-catalog.json`。
pub fn catalog_paths() -> Vec<PathBuf> {
    let mut out = Vec::new();
    if let Some(p) = std::env::var_os(ALELE_CATALOG_ENV).filter(|p| !p.is_empty()) {
        out.push(PathBuf::from(p));
    }
    if let Some(game) = std::env::current_exe().ok().and_then(|exe| exe.parent().map(|d| d.to_path_buf())) {
        out.push(game.join("mods").join(ALELE_MOD).join(ALELE_CATALOG));
    }
    out
}

static CATALOG: OnceLock<Option<Catalog>> = OnceLock::new();

/// 4+6 装备 mod 的装备目录：第一次用到时读一次（记一行 `CATALOG`）；没装它、读不到就是 None。只读它的文件，不随我们的 mod 发。
pub fn catalog() -> Option<&'static Catalog> {
    CATALOG
        .get_or_init(|| {
            for p in catalog_paths() {
                let Ok(text) = std::fs::read_to_string(&p) else { continue };
                let c = parse_catalog(&text);
                if !c.is_empty() {
                    let with = c.values().filter(|s| **s != [0; 6]).count();
                    super::wlog(format!("CATALOG {}: {} items of the 4+6 item pack, {with} of them with main stats",
                                        p.display(), c.len()));
                    return Some(c);
                }
            }
            None
        })
        .as_ref()
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
    fn the_4_plus_6_packs_keys_say_what_they_are() {
        // its finished items are tier 5; tier 4 is still a part on the way (item-catalog.json: 99 of them)
        assert_eq!(alele_tier("item_t5_134_1_2_101_0_0_0"), Some(5));
        assert_eq!(alele_tier("item_t4_0_0_0_0_0_0_2"), Some(4));
        assert_eq!((alele_tier("item_tome_of_x"), alele_tier("item_t5"), alele_tier("infinity_edge")), (None, None, None));
        assert!(is_legendary(None, "item_t5_134_1_2_101_0_0_0") && is_legendary(None, "item_t5_0_0_0_0_0_0_2"));
        assert!(!is_legendary(None, "item_t4_0_0_0_0_0_0_2") && !is_legendary(None, "item_t1_0_0_0_0_0_0_0"));
        // its runes, the ones a slot is upgraded through as well
        assert!(is_rune("runes0_0_0_0") && is_rune("runes3_1_0_1") && is_rune("runes_transition_t4"));
        assert!(!is_rune("runaans_hurricane") && !is_rune("runes") && !is_rune("runestone") && !is_rune("item_t5_7_0_0_101_0_0_3"));
        assert!(!is_legendary(None, "runes0_0_0_0") && !is_legendary(None, "runes_transition_t4"));
        // the engine's table puts the runes on its top tier and the tier-4 parts one below: the keys still decide,
        // the game's own items in the same table go by the table
        let t = Tiers::from(&["ironsword", "item_t3_0_0_0_1_0_0_0", "item_t4_0_0_0_0_0_0_2", "item_t5_134_1_2_101_0_0_0",
                              "runes2_0_0_1", "conquerors_greatsword"],
                            &[Some(1), Some(3), Some(4), Some(5), Some(5), Some(4)])
            .unwrap();
        assert_eq!(t.top, 5);
        assert!(is_legendary(Some(&t), "item_t5_134_1_2_101_0_0_0") && is_legendary(Some(&t), "conquerors_greatsword"));
        assert!(!is_legendary(Some(&t), "item_t4_0_0_0_0_0_0_2") && !is_legendary(Some(&t), "runes2_0_0_1"));
        assert!(!is_legendary(Some(&t), "ironsword"));
        // a 4+6 item bar: four runes, a part, a half-built item, then his first finished one - with nothing noted
        // from the start (a rune slot filled late)
        let ks = keys(&["runes2_0_0_1", "runes2_1_0_2", "runes4_0_0_2", "runes_transition_t3", "item_t3_0_0_0_1_0_0_0",
                        "item_t4_0_0_0_0_0_0_2", "item_t5_134_1_2_101_0_0_0", "item_t5_13_0_0_101_0_0_0"]);
        let leg = |k: &str| is_legendary(None, k);
        assert_eq!(first_legendary(&ks, &HashSet::new(), leg), Some((6, "item_t5_134_1_2_101_0_0_0")));
        // parts only: nothing to forge yet
        assert_eq!(first_legendary(&ks[..6], &HashSet::new(), leg), None);
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
        assert_eq!(sum_stats(&on, &ks, &start, None), [20, 0, 20, 600, 0, 0]);
        assert_eq!(key_stats(&on, "heartsteel", None), Some([0, 0, 0, 600, 0, 0]));
        assert_eq!(key_stats(&on, "nothing", None), None);
        assert_eq!(item_stats(&on, "heartsteel", &[], None), Some(([0, 0, 0, 600, 0, 0], Source::Named, Some(1))));
        assert_eq!(item_stats(&on, "steel_armor", &[], None).map(|(_, source, at)| (source, at)), Some((Source::Table, None)));
    }

    /// The names are the 4+6 item pack's own (read out of its DLL, 0.10.6-python.1).
    const CLEAVER: &str = "item_owned_alele_runes_and_items_item_t5_134_1_2_101__8c2bbef1";
    const BOOTS_PART: &str = "item_owned_alele_runes_and_items_item_t1_4_0_0_50_0_0_d8a6e90b";
    const RUNE: &str = "item_owned_alele_runes_and_items_runes1_0_0_2_12e07535";
    const RUNE_STEP: &str = "item_owned_alele_runes_and_items_runes_transition_t1_cb081e99";

    #[test]
    fn the_4_plus_6_packs_buffs_are_named_item_owned() {
        // the key cut to what fits a 64-byte buff name, then a hash
        assert_eq!(CLEAVER.len(), OWNED_NAME_MAX);
        assert!(owned_buff_of(CLEAVER, "item_t5_134_1_2_101_0_0_0"));
        assert!(owned_buff_of(BOOTS_PART, "item_t1_4_0_0_50_0_0_0"));
        // a key that fits is there whole
        assert!(owned_buff_of(RUNE, "runes1_0_0_2") && owned_buff_of(RUNE_STEP, "runes_transition_t1"));
        // another item's, another rune's
        assert!(!owned_buff_of(CLEAVER, "item_t5_134_1_2_102_0_0_0") && !owned_buff_of(CLEAVER, "item_t5_13_0_0_101_0_0_0"));
        assert!(!owned_buff_of(RUNE, "runes1_0_0_20") && !owned_buff_of(RUNE, "runes1_0_0") && !owned_buff_of(RUNE, "0_0_2"));
        // a short name only for the whole key: `runes1_0_0_2…` cut short is not a thing
        assert!(!owned_buff_of(RUNE, "runes1_0_0_2_1"));
        // not such a name: no hash, the key itself, an empty key
        assert!(!owned_buff_of("item_owned_alele_runes_and_items_runes1_0_0_2", "runes1_0_0_2"));
        assert!(!owned_buff_of("runes1_0_0_2", "runes1_0_0_2") && !owned_buff_of(RUNE, ""));
        assert!(!owned_buff_of("item_owned_runes1_0_0_2_12e07535", "runes1_0_0_2"), "no mod id in front");
        // any mod id: the same maker's names under another pack's id
        assert!(owned_buff_of("item_owned_some_item_pack_long_sword_0a1b2c3d", "long_sword"));
        // four of its finished items start alike for longer than fits: one name stands for each of them
        let shared = "item_owned_alele_runes_and_items_item_t5_213456_0_0_1_aaaaaaaa";
        assert_eq!(shared.len(), OWNED_NAME_MAX);
        assert!(owned_buff_of(shared, "item_t5_213456_0_0_101_0_0_0") && owned_buff_of(shared, "item_t5_213456_0_0_104_0_0_5"));
    }

    #[test]
    fn a_4_plus_6_items_stats_come_from_its_buff_else_its_catalog() {
        let key = "item_t5_134_1_2_101_0_0_0";
        let catalog: Catalog = [(key.to_string(), [40, 0, 0, 400, 0, 0])].into();
        // its buff carries the stats: the buff's (what the unit really has), not the catalog's
        let on = vec![(RUNE.to_string(), true, [0; 6]), (CLEAVER.to_string(), true, [44, 0, 0, 440, 0, 0])];
        assert_eq!(item_stats(&on, key, &[], Some(&catalog)), Some(([44, 0, 0, 440, 0, 0], Source::Owned, Some(1))));
        assert_eq!(key_stats(&on, key, None), Some([44, 0, 0, 440, 0, 0]));
        // its buff is only a mark (no main stats on it): the catalog's, the mark still taken with it
        let mark = vec![(CLEAVER.to_string(), true, [0; 6])];
        assert_eq!(item_stats(&mark, key, &[], Some(&catalog)), Some(([40, 0, 0, 400, 0, 0], Source::Catalog, Some(0))));
        // no buff of it at all (13 of its 405 have no such name): the catalog's
        assert_eq!(item_stats(&[], key, &[], Some(&catalog)), Some(([40, 0, 0, 400, 0, 0], Source::Catalog, None)));
        // neither: a mark without main stats says zero, nothing at all says nothing
        assert_eq!(item_stats(&mark, key, &[], None), Some(([0; 6], Source::Owned, Some(0))));
        assert_eq!(item_stats(&[], key, &[], None), None);
        // a buff that is not permanent is not the item's
        let timed = vec![(CLEAVER.to_string(), false, [44, 0, 0, 440, 0, 0])];
        assert_eq!(item_stats(&timed, key, &[], None), None);
        // his passive: his items' buffs, each once (two copies: two buffs), the runes left out
        let two = vec![
            (RUNE.to_string(), true, [0, 0, 9, 90, 9, 0]),
            (CLEAVER.to_string(), true, [40, 0, 0, 400, 0, 0]),
            (CLEAVER.to_string(), true, [40, 0, 0, 400, 0, 0]),
            ("eternal_iron_plate".to_string(), true, [0, 0, 60, 300, 0, 0]),
        ];
        let start: HashSet<String> = ["runes1_0_0_2".to_string()].into();
        let ks = keys(&["runes1_0_0_2", key, key, "eternal_iron_plate"]);
        assert_eq!(sum_stats(&two, &ks, &start, None), [80, 0, 60, 1100, 0, 0]);
        // a third copy with no buff left: nothing more without the catalog, the catalog's with it
        let ks3 = keys(&[key, key, key]);
        assert_eq!(sum_stats(&two, &ks3, &start, None), [80, 0, 0, 800, 0, 0]);
        assert_eq!(sum_stats(&two, &ks3, &start, Some(&catalog)), [120, 0, 0, 1200, 0, 0]);
    }

    #[test]
    fn the_4_plus_6_packs_catalog_gives_each_items_main_stats() {
        // the shape of its item-catalog.json: an item, a rune (no stats), an item with only side stats
        let json = r#"{
  "version": 2,
  "counts": { "total": 3 },
  "items": [
    {
      "id": "item_t5_134_1_2_101_0_0_0",
      "gameKey": "item_t5_134_1_2_101_0_0_0",
      "oldIds": ["item_t5_0_0_0_0_0_0_2"],
      "name": "黑色切割者",
      "tier": 5,
      "previousIds": ["item_t4_0_0_0_0_0_0_2"],
      "packageValues": {
        "status": "generated-package",
        "price": 1025,
        "stats": {
          "attack": 40,
          "hp": 400,
          "skill_cooldown_mult": 20,
          "attack_speed_mult": 12.5
        }
      },
      "runtimeEffective": { "status": "not_deployed", "price": null, "stats": null }
    },
    {
      "id": "runes1_0_0_2",
      "gameKey": "runes1_0_0_2",
      "packageValues": { "status": "generated-package", "price": 0, "stats": {} },
      "runtimeEffective": { "status": "not_deployed", "stats": null }
    },
    {
      "id": "item_t5_0_1_1_105_0_0_1",
      "gameKey": "item_t5_0_1_1_105_0_0_1",
      "packageValues": { "status": "generated-package", "price": 900, "stats": {"skill_cooldown_mult": 20, "defence": 25, "magic_resistance": -5} },
      "runtimeEffective": { "status": "deployed", "stats": {"defence": 99} }
    },
    { "id": "no_package", "gameKey": "no_package", "runtimeEffective": { "stats": {"attack": 7} } }
  ]
}"#;
        let c = parse_catalog(json);
        assert_eq!(c.len(), 3, "an item without packaged stats is left out");
        assert_eq!(c["item_t5_134_1_2_101_0_0_0"], [40, 0, 0, 400, 0, 13]);
        assert_eq!(c["runes1_0_0_2"], [0; 6]);
        assert_eq!(c["item_t5_0_1_1_105_0_0_1"], [0, 0, 25, 0, -5, 0], "its packaged stats, not the run-time block's");
        assert!(parse_catalog("{}").is_empty() && parse_catalog("not json at all \"gameKey\"").is_empty());
        // the file names are where the pack keeps it
        let paths = catalog_paths();
        assert!(paths.iter().any(|p| p.ends_with(std::path::Path::new("mods").join(ALELE_MOD).join(ALELE_CATALOG))));
    }

    /// The pack's real file when the developer points at it (`LEAGUE_ALELE_CATALOG`); skipped elsewhere (CI has none).
    #[test]
    fn the_real_catalog_reads() {
        let Some(path) = std::env::var_os(ALELE_CATALOG_ENV).filter(|p| !p.is_empty()) else { return };
        let c = parse_catalog(&std::fs::read_to_string(&path).expect("LEAGUE_ALELE_CATALOG names a file"));
        // 0.10.6-python.1: 405 items = 331 pieces of equipment + 74 runes; a finished item has main stats
        assert!(c.len() >= 300, "{} items", c.len());
        let equipment = c.keys().filter(|k| alele_tier(k).is_some()).count();
        let runes = c.keys().filter(|k| is_rune(k)).count();
        assert_eq!(equipment + runes, c.len(), "every key is the pack's");
        // (a rune may carry a main stat - 蛹化 `runes3_1_2_3` has 60 health - which is why runes are left out by key)
        let finished: Vec<_> = c.iter().filter(|(k, _)| alele_tier(k) == Some(ALELE_LEGENDARY_TIER)).collect();
        let with = finished.iter().filter(|(_, s)| **s != [0; 6]).count();
        assert!(with * 10 >= finished.len() * 9, "{with} of {} finished items have main stats", finished.len());
        if let Some(cleaver) = c.get("item_t5_134_1_2_101_0_0_0") {
            assert_eq!((cleaver[0], cleaver[3]), (40, 400), "the Black Cleaver: attack 40, health 400");
        }
        println!("{} items, {equipment} equipment, {runes} runes, {with} of {} finished with main stats", c.len(), finished.len());
    }
}
