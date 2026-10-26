//! 拉露恩附加包（用户 2026-10-26：「要做附加包的地方你就做附加包」）：金铲铲里拉露恩的规则，主包的数据做不到的三处。
//!
//! `mod.override_info` 把金铲铲包（mod_id tft）的拉露恩换成 `override/` 里的副本（tools/kit/build_alune.py --native）：
//! 数据和主包一样，只是这三处交给本包，被动挂本包的 `tft_alune:moon`。
//!
//! - **月之降临落在最近的敌人身上**：主包的碎片一枚落在目标身上、其余落在射程里随机的敌人身上（数据没有「最近」）。副本放技能时
//!   只给她挂 2 tick 的 `tft_alune_q_go`；被动看到它就去掉，挑离她最近的 `q_n` 个敌人（不含防御塔，射程 `q_range` 以内），
//!   在每个人当时站的地方放碎片落下的画面 `q_drop`，`q_fall` tick 后砸地：`q_hit` 画面和声音，`q_r` 以内的敌人受到
//!   `q_dmg` + `q_ratio`% 法强的魔法伤害、挂 `q_shred_t` tick 的月蚀印记（魔抗 -`q_shred`%，主包同名的画面）。
//! - **满月的伤害由命中的敌人分摊**：副本的满月砸下来只给范围里的敌人挂 2 tick 的 `tft_alune_r_mark<k>`（k = 砸下时的月相，
//!   0-3）和眩晕，不扣血。被动在同一 tick 收齐这些标记（去掉），算出整颗月亮的伤害：(`r_dmg` + `r_ratio`% 法强) × (100 +
//!   k × `r_ph`)% × `r_split`%，n 个人平分，每人最多 (`r_dmg` + `r_ratio`% 法强) × (100 + k × `r_ph`)% × `r_cap`%
//!   ——只砸中一个人时最痛。
//! - **月环飞回来**：副本的普攻打中时给目标挂 2 tick 的 `tft_alune_a_mark`；被动看到就去掉，从那人站的地方往她身上发一枚
//!   穿透的月环 `a_back`（直线，主包 a_ring 的画面），路上每个敌人（不含防御塔）受到 `a_back_r`% 攻击力的物理伤害
//!   （本包的效果 `tft_alune:ring_back`）。打中的那个人也在路上，回来时再挨一下：回旋镖就是这样的。
//!
//! 每个计时都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_alune.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_alune";
const HERO: &str = "tft_alune";
/// 同时最多记这么多枚还在落的碎片（一次 3 枚，4 秒多一次）。
const MOST: usize = 24;

fn al(x: &str) -> String {
    format!("{HERO}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_ALUNE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_alune.log");
        }
    }
    PathBuf::from("tft_alune.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the simulation thread in game, league_talon_vault)
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

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        _ => "unknown",
    };
    format!("[{kind} t={}] #{id}", sim.tick())
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 月之降临：碎片几枚、找人的射程、落下要几 tick、砸地的半径。
    pub q_n: usize,
    pub q_range: u64,
    pub q_fall: usize,
    pub q_r: u64,
    /// 每枚碎片的伤害：q_dmg + q_ratio% 法强；月蚀印记：魔抗 -q_shred%，q_shred_t tick。
    pub q_dmg: usize,
    pub q_ratio: usize,
    pub q_shred: i32,
    pub q_shred_t: usize,
    /// 满月：r_dmg + r_ratio% 法强，每个月相 +r_ph%；n 个人分 r_split%，每人最多 r_cap%。
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_ph: usize,
    pub r_split: usize,
    pub r_cap: usize,
    /// 月环回程：攻击力的 a_back_r%；飞行速度（世界单位 / tick，主包普攻弹道的速度）。
    pub a_back_r: usize,
    pub a_speed: u64,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            q_n: 3,
            q_range: 70000,
            q_fall: 20,
            q_r: 18000,
            q_dmg: 42,
            q_ratio: 32,
            q_shred: 20,
            q_shred_t: 360,
            r_dmg: 165,
            r_ratio: 72,
            r_ph: 20,
            r_split: 220,
            r_cap: 180,
            a_back_r: 30,
            a_speed: 4000,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        let u = v.max(0) as usize;
        match k {
            "q_n" => p.q_n = u,
            "q_range" => p.q_range = u as u64,
            "q_fall" => p.q_fall = u,
            "q_r" => p.q_r = u as u64,
            "q_dmg" => p.q_dmg = u,
            "q_ratio" => p.q_ratio = u,
            "q_shred" => p.q_shred = v as i32,
            "q_shred_t" => p.q_shred_t = u,
            "r_dmg" => p.r_dmg = u,
            "r_ratio" => p.r_ratio = u,
            "r_ph" => p.r_ph = u,
            "r_split" => p.r_split = u,
            "r_cap" => p.r_cap = u,
            "a_back_r" => p.a_back_r = u,
            "a_speed" => p.a_speed = u as u64,
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// 离 (x, y) 最近的 n 个（按距离，近的在前；距离一样按 id），只算 `reach` 以内的。
pub fn nearest(from: (u64, u64), units: &[(usize, (u64, u64))], reach: u64, n: usize) -> Vec<usize> {
    let mut v: Vec<(u128, usize)> = units
        .iter()
        .map(|&(id, p)| (dist_sq(from, p), id))
        .filter(|&(d, _)| d <= (reach as u128) * (reach as u128))
        .collect();
    v.sort();
    v.into_iter().take(n).map(|(_, id)| id).collect()
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// 满月整颗的伤害（月相 k 已算进去）。
pub fn moon_whole(p: &Params, ap: usize, k: usize) -> usize {
    (p.r_dmg + p.r_ratio * ap / 100) * (100 + k * p.r_ph) / 100
}

/// n 个人分满月时每人挨多少：整颗 × r_split% / n，最多整颗 × r_cap%。
pub fn moon_share(p: &Params, ap: usize, k: usize, n: usize) -> usize {
    if n == 0 {
        return 0;
    }
    let whole = moon_whole(p, ap, k);
    (whole * p.r_split / 100 / n).min(whole * p.r_cap / 100)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Shard {
    pub x: u64,
    pub y: u64,
    /// 砸地的 tick。
    pub land: usize,
}

// ===================== 被动 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| holds(&e, name))
}

fn holds(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 活着的、能打的敌方单位（不含防御塔）：(id, 位置)。
fn foes(sim: &StableSim<'_>, team: usize) -> Vec<(usize, (u64, u64))> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .map(|u| (u.id(), u.pos()))
        .collect()
}

#[derive(Clone, Default)]
struct Moon {
    p: Params,
    shards: Vec<Shard>,
    falls: usize,
    moons: usize,
    rings: usize,
}

impl Moon {
    /// 月之降临：最近的 q_n 个敌人，各落一枚。
    fn drop_shards(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, at: (u64, u64)) {
        let list = foes(sim, team);
        let picked = nearest(at, &list, self.p.q_range, self.p.q_n);
        let tick = sim.tick();
        for id in &picked {
            let Some(&(_, (x, y))) = list.iter().find(|(i, _)| i == id) else { continue };
            sim.play_view_effect(&al("q_drop"), me, &InputTargetV1::pos(x, y), 0, 0, 0);
            self.shards.push(Shard { x, y, land: tick + self.p.q_fall });
        }
        while self.shards.len() > MOST {
            self.shards.remove(0);
        }
        self.falls += 1;
        if self.falls <= 30 || self.falls % 50 == 0 {
            wlog(format!("{} MOONFALL #{}: {} shards on the nearest {:?}", head(sim, me), self.falls, picked.len(), picked));
        }
    }

    /// 砸地的碎片：画面、声音、伤害、月蚀印记。
    fn land_shards(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, ap: usize) {
        let tick = sim.tick();
        let (now, later): (Vec<Shard>, Vec<Shard>) = self.shards.iter().partition(|s| s.land <= tick);
        self.shards = later;
        if now.is_empty() {
            return;
        }
        let dmg = self.p.q_dmg + self.p.q_ratio * ap / 100;
        let mut mark = BuffV1::timed(&al("q_shred"), self.p.q_shred_t);
        mark.magic_resistance_mult = -self.p.q_shred;
        for s in now {
            let at = InputTargetV1::pos(s.x, s.y);
            sim.play_view_effect(&al("q_hit"), me, &at, 0, 0, 0);
            sim.play_sfx(&al("q_hit"), me, &at);
            let hit: Vec<usize> = foes(sim, team)
                .into_iter()
                .filter(|&(_, p)| dist_sq(p, (s.x, s.y)) <= (self.p.q_r as u128) * (self.p.q_r as u128))
                .map(|(id, _)| id)
                .collect();
            for id in hit {
                sim.deal_damage(me, id, 0, dmg, AttackTypeV1::Skill);
                sim.entity_remove_buff(id, &mark.name());
                sim.add_buff(id, &mark);
            }
        }
    }

    /// 满月：收齐这一 tick 的标记，分摊伤害。
    fn split_moon(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, ap: usize) {
        let mut marked: Vec<(usize, usize)> = Vec::new();   // (id, 月相)
        for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
            if u.team() == team {
                continue;
            }
            for k in 0..4 {
                if holds(&u, &al(&format!("r_mark{k}"))) {
                    marked.push((u.id(), k));
                }
            }
        }
        if marked.is_empty() {
            return;
        }
        let k = marked.iter().map(|&(_, k)| k).max().unwrap_or(0);
        let n = marked.len();
        let share = moon_share(&self.p, ap, k, n);
        for &(id, kk) in &marked {
            sim.entity_remove_buff(id, &al(&format!("r_mark{kk}")));
            sim.deal_damage(me, id, 0, share, AttackTypeV1::Skill);
        }
        self.moons += 1;
        wlog(format!(
            "{} MOON #{}: phase {k}, whole {} shared by {n} -> {share} each",
            head(sim, me),
            self.moons,
            moon_whole(&self.p, ap, k)
        ));
    }

    /// 月环飞回来：从打中的人那里往她身上发一枚穿透的月环。
    fn rings_back(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, at: (u64, u64)) {
        let mark = al("a_mark");
        let hit: Vec<(usize, (u64, u64))> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && holds(u, &mark))
            .map(|u| (u.id(), u.pos()))
            .collect();
        for (id, (x, y)) in hit {
            sim.entity_remove_buff(id, &mark);
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x,
                y,
                radius: 8_000,
                speed: self.p.a_speed,
                move_kind: ProjectileMoveKindV1::Linear.code(),
                target_id: 0,
                target_x: at.0,
                target_y: at.1,
                penetrate: true,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::EnemyWithoutTower.code(),
            };
            let flew = sim.spawn_projectile(&al("a_back"), &format!("{ID}:ring_back"), &spec);
            self.rings += 1;
            if self.rings <= 20 || self.rings % 100 == 0 {
                wlog(format!(
                    "{} RING #{} back from #{id}{}",
                    head(sim, me),
                    self.rings,
                    if flew { "" } else { " (spawn_projectile refused)" }
                ));
            }
        }
    }
}

impl StablePassive for Moon {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Alune (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((team, at, ap)) = sim.get_entity(me).map(|e| (e.team(), e.pos(), e.stat().magic_power)) else {
            return;
        };
        if has_buff(sim, me, &al("q_go")) {
            sim.entity_remove_buff(me, &al("q_go"));
            self.drop_shards(sim, me, team, at);
        }
        if !self.shards.is_empty() {
            self.land_shards(sim, me, team, ap);
        }
        self.split_moon(sim, me, team, ap);
        self.rings_back(sim, me, team, at);
    }
}

/// 月环回程打中的每个敌人：她攻击力的 a_back_r%（物理）。参数在注册时定下（同一局只有一个拉露恩的数字）。
struct RingBack {
    ratio: usize,
}

impl StableEffectType for RingBack {
    fn apply(&self, sim: &mut StableSim<'_>, _rng_seed: u64, caster_id: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let Some(ad) = sim.get_entity(caster_id).map(|e| e.stat().attack) else { return };
        sim.deal_damage(caster_id, input.target_id, ad * self.ratio / 100, 0, AttackTypeV1::Skill);
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        (caster_stat.attack * self.ratio / 100, 0)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`.
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Alune: Moonfall on the nearest enemies, the full moon's damage shared, the ring flies back) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:moon"), Moon::default());
    module.add_native_effect(format!("{ID}:ring_back"), RingBack { ratio: Params::default().a_back_r });
    host.log(LogLevel::Info, "tft_alune loaded (Moonfall nearest, shared full moon, the ring's way back).");
}

fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"a_back_r":30,"a_speed":4000,"q_dmg":42,"q_fall":20,"q_n":3,"q_r":18000,"q_range":70000,"q_ratio":32,"q_shred":20,"q_shred_t":360,"r_cap":180,"r_dmg":165,"r_ph":20,"r_ratio":72,"r_split":220}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_nearest_three_within_reach() {
        let units = [(1, (100, 0)), (2, (50, 0)), (3, (300, 0)), (4, (80, 60)), (5, (2000, 0))];
        assert_eq!(nearest((0, 0), &units, 1000, 3), vec![2, 1, 4]);
        assert_eq!(nearest((0, 0), &units, 90, 3), vec![2]);
        assert!(nearest((0, 0), &units, 10, 3).is_empty());
    }

    #[test]
    fn the_moon_hurts_most_alone() {
        let p = Params::default();
        let whole = moon_whole(&p, 100, 3);
        assert_eq!(whole, (165 + 72) * 160 / 100);
        assert_eq!(moon_share(&p, 100, 3, 1), whole * 180 / 100);   // capped
        assert_eq!(moon_share(&p, 100, 3, 2), whole * 220 / 100 / 2);
        assert!(moon_share(&p, 100, 3, 5) < moon_share(&p, 100, 3, 3));
        assert_eq!(moon_share(&p, 100, 3, 0), 0);
    }
}
