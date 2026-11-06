//! 卡西奥佩娅附加包（用户 2026-10-18：「技能方案按 A 做（带扩展包 league_cassiopeia）」）。主包保持纯数据；`mod.override_info`
//! 把主包的卡西奥佩娅换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_cassiopeia.py 的 `native=1` 生成：技能一字
//! 不改，只有下面两处换成本包的原生效果），本包补数据做不到的两件事：
//!
//! - **双生毒牙看目标本人有没有中毒**（英雄联盟的规则）：数据只读得到施法者自己身上的 buff，主包只能用“她的 Q、W 刚毒到人”
//!   （她身上的 `venom`）来近似；副本里 Q、W 毒到的单位身上挂标记 `league_cassiopeia_poison`（和毒一样长），毒牙打中时
//!   `league_cassiopeia:fang` 看**这个目标**身上有没有标记：有才多造成 `E_BONUS` + `E_BRATIO`% 法强魔法伤害并给她回复
//!   `E_HEAL`% 法强生命（打小兵野怪只回 `E_HEAL_M`%）。
//! - **石化凝视看敌人的真实朝向**：数据看不到单位朝哪边，主包把近处（交战中）的石化、远处的减速；副本里凝视扫到的每个敌方英雄
//!   由 `league_cassiopeia:gaze` 判定：**面朝她的石化**（眩晕 `R_STUN` tick + 石壳 `league_cassiopeia_r_stone`），背对她的减速
//!   `R_SLOW`%（`league_cassiopeia_r_slow`）。朝向由她的被动 `league_cassiopeia:venom` 记录：每 `FACE_EVERY` tick 看一次每个敌方
//!   英雄，横向走了至少 `MOVE_MIN` 就按走的方向记朝向；站着不动 `STILL` tick 以上就记成朝向离他最近的对手英雄（站着打人时
//!   人物转向目标）。朝向记在那个英雄身上的隐藏 buff `league_cassiopeia_face_l`（朝左；没有 = 朝右）。
//!
//! - **优雅蛇行：蛇女不需要鞋**（0.1.2，用户 2026-11-05 的彩蛋「蛇女不需要鞋」）：英雄联盟的卡西奥佩娅没有脚、不能买鞋，
//!   移速随等级成长（主包早就照这个给了更高的移速成长 `ms_g`）。游戏本身不卖鞋，鞋来自第三方装备 mod（日志里见过 `boots`、
//!   `berserkers_greaves`、`plated_steelcaps`、`sorcerers_shoes`、`ionian_boots_of_lucidity`、`gluttonous_greaves`）。本包的装备
//!   构筑钩子（`StableItemBuildHook`，游戏给每个 AI 选手定这一局要出的成装时调用）只管她：鞋（[`is_boots`] 按名字认）的分数压到
//!   最低，引擎挑的成装里还是有鞋就换成同一档里还没出的别的装备（法强的先，[`without_boots`]）。被动每 `ITEMS_EVERY` tick 看她
//!   身上的装备，还是买了鞋（钩子被别的 mod 盖掉了）就把鞋的属性 buff（名字就是装备的 key，league_ornn 认装备的办法）摘掉
//!   ——没有脚穿不上；鞋还在装备栏里，钱也花了。第一次记一行 `BOOTS`。
//!
//! 数字是主包参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_cassiopeia.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `FANG`（毒牙加成）、`GAZE`（石化或减速、朝向）、`BUILD`（她的成装里的鞋换掉了）、`BOOTS`（她还是买了鞋，属性摘掉了），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_cassiopeia";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_cassiopeia") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 毒牙打中中毒目标多造成的固定伤害、法强加成 %（e_bonus、e_bratio）。
pub const E_BONUS: usize = 14;
pub const E_BRATIO: usize = 24;
/// 打中中毒的英雄回复法强的 %（e_heal），打小兵野怪回复法强的 %（e_heal_m）。
pub const E_HEAL: usize = 10;
pub const E_HEAL_M: usize = 3;
/// 石化（眩晕）和减速的 tick、减速 %（r_stun、r_slow）。
pub const R_STUN: usize = 120;
pub const R_SLOW: usize = 40;
/// 朝向：每这么多 tick 看一次；横向至少走这么远才算转向；站着不动这么多 tick 后朝向最近的对手英雄；离她这么近（横向）算正对。
pub const FACE_EVERY: usize = 3;
pub const MOVE_MIN: u64 = 300;
pub const STILL: usize = 30;
pub const FRONT_SLACK: u64 = 3_000;
/// 优雅蛇行：装备的名字里有这些就是鞋（英雄联盟的鞋：草鞋、狂战士胫甲、轻灵之靴、明朗之靴、水银之靴、铁板靴、法师之靴、
/// 共生之靴，S14 的三级鞋，第三方装备 mod 的 `gluttonous_greaves`；`radiant_` 开头的升级版也算）。
pub const BOOTS: [&str; 11] = [
    "boots",
    "greaves",
    "shoes",
    "treads",
    "steelcaps",
    "soles",
    "lucidity",
    "swiftmarch",
    "armored_advance",
    "chainlaced_crushers",
    "forever_forward",
];
/// 她的成装里鞋的分数（引擎按分数挑成装；替换成这个就挑不上）。
pub const BOOTS_SCORE: f32 = -1.0e6;
/// 构筑钩子的优先级：只对她做决定，排在别的装备 mod 前面。
pub const BUILD_PRIORITY: i32 = 100;
/// 被动多久看一次她身上的装备（还是买了鞋：鞋的属性 buff 摘掉，第一次记一行）。
pub const ITEMS_EVERY: usize = 30;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_CASSIOPEIA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_cassiopeia.log");
        }
    }
    PathBuf::from("league_cassiopeia.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 规则（单元测试用） =====================

fn n(name: &str) -> String {
    format!("{ID}_{name}")
}

/// 毒牙对中毒目标多造成的魔法伤害（减免前）。
pub fn fang_bonus(magic_power: usize) -> usize {
    E_BONUS + E_BRATIO * magic_power / 100
}

/// 毒牙打中中毒目标给她回复的生命（英雄 / 别的单位）。
pub fn fang_heal(magic_power: usize, champion: bool) -> usize {
    (if champion { E_HEAL } else { E_HEAL_M }) * magic_power / 100
}

/// 横向走了 `dx`（正 = 往右）以后的朝向：`Some(true)` 朝左，`Some(false)` 朝右，`None` 走得太少、不变。
pub fn facing_after(dx: i64) -> Option<bool> {
    if dx.unsigned_abs() < MOVE_MIN {
        None
    } else {
        Some(dx < 0)
    }
}

/// 朝向 `left` 的单位站在 `at_x`，她在 `her_x`：他是不是面朝她（横向离得很近也算）。
pub fn faces(left: bool, at_x: u64, her_x: u64) -> bool {
    if at_x.abs_diff(her_x) <= FRONT_SLACK {
        return true;
    }
    if left {
        her_x < at_x
    } else {
        her_x > at_x
    }
}

/// 这件装备是不是鞋（按名字，大小写不论）。
pub fn is_boots(key: &str) -> bool {
    let k = key.to_ascii_lowercase();
    BOOTS.iter().any(|b| k.contains(b))
}

/// 引擎给她挑的成装 `base`（`keys` 的下标）里有鞋：去掉鞋，每双换成一件同档（成装里最高那一档）、还没在成装里的别的装备，
/// 法强的先，其余按引擎的顺序；找不到就少一件。没有鞋：`None`（照引擎的）。
pub fn without_boots(
    keys: &[&str],
    cats: &[Option<ItemCategoryV1>],
    tiers: &[Option<usize>],
    base: &[usize],
) -> Option<Vec<usize>> {
    let boots = |i: usize| keys.get(i).is_some_and(|k| is_boots(k));
    let n_boots = base.iter().filter(|&&i| boots(i)).count();
    if n_boots == 0 {
        return None;
    }
    let mut out: Vec<usize> = base.iter().copied().filter(|&i| !boots(i)).collect();
    let tier = |i: usize| tiers.get(i).copied().flatten();
    let top = out.iter().filter_map(|&i| tier(i)).max();
    for _ in 0..n_boots {
        let pick = (0..keys.len())
            .filter(|&i| !boots(i) && !out.contains(&i) && (top.is_none() || tier(i) == top))
            .min_by_key(|&i| (cats.get(i).copied().flatten() != Some(ItemCategoryV1::Magic), i));
        match pick {
            Some(i) => out.push(i),
            None => break,
        }
    }
    Some(out)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn magic_power(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| e.stat().magic_power)
}

// ===================== 原生效果 =====================

/// 毒牙打中一个单位：他本人中毒才加伤害、回血。
fn fang(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let Some(champion) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.is_champion()) else { return };
    if !has_buff(sim, target, &n("poison")) {
        return;
    }
    let ap = magic_power(sim, me);
    let bonus = fang_bonus(ap);
    sim.deal_damage_typed(me, target, bonus, DamageTypeV1::Ap, AttackTypeV1::BaseAttack);
    let heal = fang_heal(ap, champion);
    if heal > 0 && sim.get_entity(me).is_some_and(|e| e.is_alive()) {
        sim.heal(me, me, heal);
    }
    if let Some(k) = counted("fang") {
        wlog(format!("{} FANG #{target} poisoned (champion {champion}): +{bonus} magic, heal {heal} #{k}", head(sim, me)));
    }
}

/// 凝视扫到一个敌方英雄：面朝她的石化，背对她的减速。
fn gaze(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let Some(at) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
    let Some(her) = sim.get_entity(me).map(|e| e.pos()) else { return };
    let left = has_buff(sim, target, &n("face_l"));
    let facing = faces(left, at.0, her.0);
    if facing {
        sim.apply_cc(target, &CcV1::stun(R_STUN as u64));
        sim.add_buff(target, &BuffV1::timed(&n("r_stone"), R_STUN));
    } else {
        let mut slow = BuffV1::timed(&n("r_slow"), R_STUN);
        slow.move_speed_mult = -(R_SLOW as i32);
        sim.entity_remove_buff(target, &n("r_slow"));
        sim.add_buff(target, &slow);
    }
    if let Some(k) = counted("gaze") {
        wlog(format!(
            "{} GAZE #{target} at x {} (she at {}), facing {}: {} #{k}",
            head(sim, me),
            at.0,
            her.0,
            if left { "left" } else { "right" },
            if facing { "petrified" } else { "slowed" }
        ));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 优雅蛇行：不买鞋 =====================

/// 装备构筑钩子：只管卡西奥佩娅（别的英雄照引擎的）。
struct NoBoots;

impl StableItemBuildHook for NoBoots {
    fn id(&self) -> String {
        format!("{ID}:no_boots")
    }

    fn priority(&self) -> i32 {
        BUILD_PRIORITY
    }

    fn score_item(&self, ctx: &StableItemBuildContext<'_>, candidate: usize, _base: f32) -> StableDraftDecision {
        if ctx.champion_key() == ID && ctx.item_key(candidate).is_some_and(is_boots) {
            StableDraftDecision::Replace(BOOTS_SCORE)
        } else {
            StableDraftDecision::Pass
        }
    }

    fn decide_build(&self, ctx: &StableItemBuildContext<'_>) -> Vec<usize> {
        if ctx.champion_key() != ID {
            return Vec::new();
        }
        let keys = ctx.item_keys();
        let cats: Vec<_> = (0..keys.len()).map(|i| ctx.item_category(i)).collect();
        let tiers: Vec<_> = (0..keys.len()).map(|i| ctx.item_tier(i)).collect();
        let base = ctx.base_build();
        let Some(out) = without_boots(&keys, &cats, &tiers, base) else { return Vec::new() };
        if let Some(k) = counted("build") {
            let names = |v: &[usize]| v.iter().filter_map(|&i| keys.get(i).copied()).collect::<Vec<_>>();
            wlog(format!("BUILD team {} lane {:?}: the engine's build {:?} had boots -> {:?} #{k}", ctx.team(), ctx.lane(),
                         names(base), names(&out)));
        }
        out
    }
}

// ===================== 被动：记录敌方英雄的朝向 =====================

#[derive(Clone, Copy, Default)]
struct Track {
    x: u64,
    y: u64,
    /// 最后一次移动（超过 MOVE_MIN 的那一次）在第几 tick。
    moved: usize,
}

#[derive(Clone, Default)]
struct Venom {
    seen: HashMap<usize, Track>,
    /// 摘鞋的属性已经记过一行 `BOOTS`（每份模拟里的她一次）。
    boots_told: bool,
}

impl Venom {
    fn set_face(sim: &mut StableSim<'_>, id: usize, left: bool) {
        let name = n("face_l");
        let has = has_buff(sim, id, &name);
        if left && !has {
            sim.add_buff(id, &BuffV1::timed(&name, 1_000_000));
        } else if !left && has {
            sim.entity_remove_buff(id, &name);
        }
    }
}

impl StablePassive for Venom {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.seen.clear();
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let t = sim.tick();
        if t % ITEMS_EVERY == 0 {
            // boots she owns anyway (another mod's build won over the hook): their stats come off her (no feet to wear them)
            let boots: Vec<String> =
                sim.get_player(player).map(|p| p.item_keys()).unwrap_or_default().into_iter().filter(|k| is_boots(k)).collect();
            let worn: Vec<&String> = boots.iter().filter(|k| has_buff(sim, me, k)).collect();
            for k in &worn {
                sim.entity_remove_buff(me, k);
            }
            if !worn.is_empty() && !self.boots_told {
                self.boots_told = true;
                if let Some(k) = counted("boots") {
                    wlog(format!("{} BOOTS: she owns {boots:?} - the build hook was overridden; their stats taken off her #{k}",
                                 head(sim, me)));
                }
            }
        }
        if t % FACE_EVERY != 0 {
            return;
        }
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let champs: Vec<(usize, usize, (u64, u64), bool)> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| sim.get_entity(id).map(|e| (id, e.team(), e.pos(), e.is_alive())))
            .collect();
        for &(id, team, (x, y), alive) in &champs {
            if team == my_team || !alive {
                continue;
            }
            let tr = self.seen.entry(id).or_insert(Track { x, y, moved: t });
            let dx = x as i64 - tr.x as i64;
            let dy = y as i64 - tr.y as i64;
            if let Some(left) = facing_after(dx) {
                Self::set_face(sim, id, left);
                tr.moved = t;
            } else if dy.unsigned_abs() >= MOVE_MIN {
                tr.moved = t;
            } else if t >= tr.moved + STILL {
                // standing: turned to the nearest champion of the other side (whom he is fighting)
                let near = champs
                    .iter()
                    .filter(|c| c.1 != team && c.3)
                    .min_by_key(|c| {
                        let (ex, ey) = (c.2 .0 as i128 - x as i128, c.2 .1 as i128 - y as i128);
                        ex * ex + ey * ey
                    })
                    .map(|c| c.2 .0);
                if let Some(nx) = near {
                    if nx.abs_diff(x) >= MOVE_MIN {
                        Self::set_face(sim, id, nx < x);
                    }
                }
            }
            tr.x = x;
            tr.y = y;
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Cassiopeia: Twin Fang on the poisoned target, Petrifying Gaze by facing, no boots) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:fang"), Step(fang));
    module.add_native_effect(format!("{ID}:gaze"), Step(gaze));
    module.add_native_passive(format!("{ID}:venom"), Venom::default());
    module.add_item_build_hook(NoBoots);
    host.log(LogLevel::Info, "league_cassiopeia loaded (Twin Fang on the poisoned target, Petrifying Gaze by facing, no boots).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fang_numbers() {
        assert_eq!(fang_bonus(0), E_BONUS);
        assert_eq!(fang_bonus(200), E_BONUS + E_BRATIO * 2);
        assert_eq!(fang_heal(200, true), E_HEAL * 2);
        assert_eq!(fang_heal(200, false), E_HEAL_M * 2);
    }

    #[test]
    fn facing_from_moves() {
        assert_eq!(facing_after(0), None);
        assert_eq!(facing_after(MOVE_MIN as i64 - 1), None);
        assert_eq!(facing_after(-(MOVE_MIN as i64)), Some(true));
        assert_eq!(facing_after(5_000), Some(false));
    }

    #[test]
    fn who_faces_her() {
        // facing right toward her on his right
        assert!(faces(false, 100_000, 150_000));
        assert!(!faces(true, 100_000, 150_000));
        // facing left toward her on his left
        assert!(faces(true, 100_000, 50_000));
        assert!(!faces(false, 100_000, 50_000));
        // right on top of her: in front either way
        assert!(faces(true, 100_000, 101_000));
    }

    #[test]
    fn boots_by_name() {
        // the third-party item mod's keys seen in the 11-04 logs, League's other boots, the radiant upgrades
        for k in ["boots", "berserkers_greaves", "plated_steelcaps", "sorcerers_shoes", "ionian_boots_of_lucidity",
                  "gluttonous_greaves", "mercurys_treads", "symbiotic_soles", "boots_of_swiftness", "swiftmarch",
                  "crimson_lucidity", "radiant_plated_steelcaps", "Sorcerers_Shoes"] {
            assert!(is_boots(k), "{k} is boots");
        }
        // what she builds, the base game's items, the rest of the mod's
        for k in ["rylais_crystal_scepter", "liandrys_torment", "needlessly_large_rod", "rejuvenation_bead", "ironsword",
                  "giants_horn_shard", "radiant_zhonyas_hourglass", "seekers_armguard", "spirit_visage", "steel_sigil",
                  "runic_compass", "staff_of_rapture", "world_atlas", "bamis_cinder"] {
            assert!(!is_boots(k), "{k} is not boots");
        }
    }

    #[test]
    fn boots_in_her_build_become_a_mage_item_of_the_same_tier() {
        use ItemCategoryV1::{Ad, Hp, Magic};
        let keys = ["ironsword", "boots", "sorcerers_shoes", "arcane_crystal", "rylais_crystal_scepter", "liandrys_torment",
                    "zhonyas_hourglass", "infinity_edge", "sunfire"];
        let cats = [Some(Ad), None, None, Some(Magic), Some(Magic), Some(Magic), Some(Magic), Some(Ad), Some(Hp)];
        let tiers = [Some(1), Some(1), Some(2), Some(1), Some(3), Some(3), Some(3), Some(3), Some(3)];
        // no boots: the engine's build stays
        assert_eq!(without_boots(&keys, &cats, &tiers, &[4, 5]), None);
        // boots out, the first top-tier mage item she has not got in
        assert_eq!(without_boots(&keys, &cats, &tiers, &[4, 2, 5]), Some(vec![4, 5, 6]));
        // every top-tier mage item in already: the next top-tier one in the engine's order
        assert_eq!(without_boots(&keys, &cats, &tiers, &[4, 2, 5, 6]), Some(vec![4, 5, 6, 7]));
        // two pairs out (a mod forcing them), two in
        assert_eq!(without_boots(&keys, &cats, &tiers, &[1, 2, 4]), Some(vec![4, 5, 6]));
        // nothing else to build: one item fewer rather than boots
        assert_eq!(without_boots(&keys[..3], &cats[..3], &tiers[..3], &[0, 2]), Some(vec![0]));
    }

    #[test]
    fn names_fit_a_buff() {
        for s in ["poison", "face_l", "r_stone", "r_slow"] {
            assert!(n(s).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn the_copy_uses_the_natives_and_the_numbers() {
        let copy = include_str!("../override/league_cassiopeia.data_champion");
        for r in ["league_cassiopeia:fang", "league_cassiopeia:gaze", "league_cassiopeia:venom"] {
            assert!(copy.contains(r), "the copy never uses {r}");
        }
        for (k, v) in [("e_bonus", E_BONUS), ("e_bratio", E_BRATIO), ("e_heal", E_HEAL), ("e_heal_m", E_HEAL_M),
                       ("r_stun", R_STUN), ("r_slow", R_SLOW)] {
            assert!(copy.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(copy.contains("\"name\": \"league_cassiopeia_poison\""), "the copy never marks the poisoned");
    }
}
