//! 婕拉附加包：照英雄联盟做主包数据做不到的种子和植物（用户 2026-10-20：技能方案 A、中单、做附加包）。
//!
//! 主包保持纯数据：数据不能在地上留东西，所以主包里每次 Q、E 都当场种一颗种子、马上长成植物（英雄联盟 W + Q / W + E 的连招）；
//! 植物是落点上的周期区域，每秒打区域里先轮到的一个敌人（小兵也可能排在英雄前面），伤害不随等级变。`mod.override_info` 把
//! 主包的婕拉换成 `override/` 里的副本（`tools/kit/build_zyra.py --native`），被动 `league_zyra:garden`：
//!
//! - **荆棘花园（种子留在地上）**：她活着时每 `s_cd` tick 在身边掉一颗种子（有敌方英雄在 `s_seek` 内就掉在朝他的方向
//!   `s_near` 远处，否则在她身边绕一圈的位置），种子在地上留 `s_life` tick，最多 `s_max` 颗（多了最早的那颗枯掉）；
//!   她参与击杀敌方英雄（击杀或助攻）时马上掉一颗（英雄联盟：击杀缩短狂野生长的充能）。
//! - **Q / E 落在种子旁边**：副本里 Q、E 出手那一 tick 给目标挂 2 tick 的 `league_zyra_q_aim` / `league_zyra_e_aim`
//!   （落点就是目标那时站的地方）；Q 落点 `s_r` 内的种子长成**荆棘喷射者**，E 的藤蔓经过的线（她到落点、再往前 `e_over`）
//!   `s_r` 内的种子长成**藤蔓鞭击者**。主包数据在落点长的那一株照旧，种子长的是本包的植物。
//! - **本包的植物**：活 `t_life` tick，每 `t_per` tick 打一次，**先打范围内最近的敌方英雄**，没有英雄才打最近的小兵、野怪
//!   （防御塔不打）；伤害随她的等级成长（英雄联盟 20–100：1 级 `pl_lo`、18 级 `pl_hi`，中间按等级线性）+ `pl_ratio`% 法强。
//!   荆棘喷射者从植物身上吐出一根看得见的刺（`league_zyra_t_spit`，飞到才扣血），藤蔓鞭击者近身抽打并减速 `v_slow`%。
//! - **绞杀之藤激怒植物**：副本里 R 出手时给目标挂 `league_zyra_r_aim`；落点 `r_r` 内本包的植物 `r_rage` tick 内出手间隔减半
//!   （英雄联盟：密林里的植物攻速提高）。主包数据的植物照主包（伤害提高）。
//!
//! 游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列，下一次 on_update 之前才扣血（莉莉娅 0.1.2 的教训）。
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个婕拉自己的被动实例里，
//! 服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zyra.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `SEED`（掉种子）、`GROW`（种子长成植物）、`STRIKE`（植物出手）、`RAGE`（激怒）、`TAKEDOWN`（参与击杀掉种子）、
//! `WATCH`（每 30 秒的计数），都限了条数。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_zyra";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";
/// 荆棘喷射者吐的刺从植物身上多高的地方出来（植物图的嘴）。
const SPIT_UP: u64 = 9_000;

/// 主包婕拉的名字（buff、声音、画面都以它开头）。
fn zy(x: &str) -> String {
    format!("league_zyra_{x}")
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZYRA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_zyra.log");
        }
    }
    PathBuf::from("league_zyra.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    // the file stays open (league_lillia's log_open_once fix: opening it for every line stalled the simulation thread)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 种子：掉落间隔、在地上留多久、最多几颗、朝敌方英雄掉多远、多远内的英雄算「朝他」、Q / E 长出种子的半径、
    /// 种子的画面多久重放一次（它的图一轮的长度）、E 的藤蔓越过落点多远。
    pub s_cd: usize,
    pub s_life: usize,
    pub s_max: usize,
    pub s_near: usize,
    pub s_seek: usize,
    pub s_r: usize,
    pub s_show: usize,
    pub e_over: usize,
    /// 植物：活多久、出手间隔、荆棘喷射者 / 藤蔓鞭击者的射程、刺飞多快、减速 % 和 tick。
    pub t_life: usize,
    pub t_per: usize,
    pub t_r: usize,
    pub v_r: usize,
    pub spit_speed: usize,
    pub v_slow: usize,
    pub v_slow_t: usize,
    /// 植物一下的伤害：1 级、18 级（中间按等级线性）、法强 %。
    pub pl_lo: usize,
    pub pl_hi: usize,
    pub pl_ratio: usize,
    /// 绞杀之藤：半径、激怒多久。
    pub r_r: usize,
    pub r_rage: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            s_cd: 600,
            s_life: 1800,
            s_max: 4,
            s_near: 30000,
            s_seek: 90000,
            s_r: 24000,
            s_show: 60,
            e_over: 20000,
            t_life: 300,
            t_per: 60,
            t_r: 50000,
            v_r: 32000,
            spit_speed: 3000,
            v_slow: 30,
            v_slow_t: 60,
            pl_lo: 20,
            pl_hi: 100,
            pl_ratio: 12,
            r_r: 44000,
            r_rage: 300,
        }
    }
}

/// `{"s_cd":600,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "s_cd" => &mut p.s_cd,
            "s_life" => &mut p.s_life,
            "s_max" => &mut p.s_max,
            "s_near" => &mut p.s_near,
            "s_seek" => &mut p.s_seek,
            "s_r" => &mut p.s_r,
            "s_show" => &mut p.s_show,
            "e_over" => &mut p.e_over,
            "t_life" => &mut p.t_life,
            "t_per" => &mut p.t_per,
            "t_r" => &mut p.t_r,
            "v_r" => &mut p.v_r,
            "spit_speed" => &mut p.spit_speed,
            "v_slow" => &mut p.v_slow,
            "v_slow_t" => &mut p.v_slow_t,
            "pl_lo" => &mut p.pl_lo,
            "pl_hi" => &mut p.pl_hi,
            "pl_ratio" => &mut p.pl_ratio,
            "r_r" => &mut p.r_r,
            "r_rage" => &mut p.r_rage,
            _ => continue,
        };
        *slot = v;
    }
    p.s_cd = p.s_cd.max(1);
    p.s_show = p.s_show.max(1);
    p.t_per = p.t_per.max(2);
    p.spit_speed = p.spit_speed.max(1);
    p.v_slow = p.v_slow.min(95);
    p
}

// ===================== 计算 =====================

/// 植物一下的魔法伤害（减免前）：等级 1 是 `pl_lo`、18 是 `pl_hi`，中间线性，加 `pl_ratio`% 法强。
pub fn plant_damage(p: &Params, level: usize, ap: usize) -> usize {
    let lv = level.clamp(1, 18);
    p.pl_lo + (p.pl_hi.saturating_sub(p.pl_lo)) * (lv - 1) / 17 + p.pl_ratio * ap / 100
}

/// 出手间隔：被激怒时减半。
pub fn strike_period(p: &Params, enraged: bool) -> usize {
    if enraged {
        (p.t_per / 2).max(1)
    } else {
        p.t_per
    }
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 点 `p` 到线段 `a`-`b` 的距离。
pub fn seg_dist(p: (f64, f64), a: (f64, f64), b: (f64, f64)) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let l2 = dx * dx + dy * dy;
    if l2 <= 0.0 {
        return dist(p, a);
    }
    let t = (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / l2).clamp(0.0, 1.0);
    dist(p, (a.0 + t * dx, a.1 + t * dy))
}

/// 掉种子的位置：朝 `toward`（有的话）`near` 远处、最多到一半的路；没有就在她身边按 `turn`（0..8）绕一圈。
pub fn seed_spot(me: (f64, f64), toward: Option<(f64, f64)>, near: f64, turn: usize) -> (f64, f64) {
    match toward {
        Some(t) => {
            let d = dist(me, t).max(1.0);
            let k = near.min(d / 2.0) / d;
            (me.0 + (t.0 - me.0) * k, me.1 + (t.1 - me.1) * k)
        }
        None => {
            let a = (turn % 8) as f64 * std::f64::consts::FRAC_PI_4;
            (me.0 + near / 2.0 * a.cos(), me.1 + near / 2.0 * a.sin())
        }
    }
}

fn at(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

// ===================== 被动 =====================

#[derive(Clone, Copy, Debug, PartialEq)]
enum Kind {
    Spitter,
    Lasher,
}

#[derive(Clone, Debug)]
struct Seed {
    pos: (f64, f64),
    until: usize,
    next_show: usize,
}

#[derive(Clone, Debug)]
struct Plant {
    kind: Kind,
    pos: (f64, f64),
    until: usize,
    next: usize,
    rage_until: usize,
}

/// 刺在飞：到了 `due` 再扣血。
#[derive(Clone, Debug)]
struct Spit {
    target: usize,
    due: usize,
    dmg: usize,
}

/// 每个婕拉一份。
#[derive(Clone, Default)]
struct Garden {
    p: Params,
    player: usize,
    seeds: Vec<Seed>,
    plants: Vec<Plant>,
    spits: Vec<Spit>,
    next_seed: usize,
    turn: usize,
    /// 上一 tick 身上有她的 q_aim / e_aim / r_aim 的单位（一个标记只算一次）。
    aim_seen: Vec<(usize, u8)>,
    kills_seen: usize,
    n_seeds: usize,
    n_grow: usize,
    n_strike: usize,
    n_rage: usize,
    n_take: usize,
    next_report: usize,
}

struct Unit {
    id: usize,
    pos: (f64, f64),
    champion: bool,
}

/// 能打的敌方单位（英雄、小兵、野怪；塔、水晶不算）。
fn enemies(sim: &StableSim<'_>, team: usize) -> Vec<Unit> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || !e.is_alive() || !e.is_targetable() {
            continue;
        }
        let ok = matches!(
            e.kind(),
            Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen)
        );
        if ok {
            out.push(Unit { id: e.id(), pos: fpos(e.pos()), champion: e.kind() == Some(EntityKindV1::Champion) });
        }
    }
    out
}

/// 植物打谁：范围内最近的敌方英雄，没有就最近的其他单位。
fn choose(units: &[Unit], from: (f64, f64), reach: f64) -> Option<&Unit> {
    let near = |u: &&Unit| dist(u.pos, from) <= reach;
    let by = |a: &&Unit, b: &&Unit| dist(a.pos, from).total_cmp(&dist(b.pos, from));
    units.iter().filter(|u| u.champion).filter(near).min_by(by).or_else(|| units.iter().filter(near).min_by(by))
}

impl Garden {
    fn drop_seed(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (f64, f64), why: &str) {
        let tick = sim.tick();
        let toward = enemies(sim, team)
            .into_iter()
            .filter(|u| u.champion && dist(u.pos, pos) <= self.p.s_seek as f64)
            .min_by(|a, b| dist(a.pos, pos).total_cmp(&dist(b.pos, pos)))
            .map(|u| u.pos);
        let spot = seed_spot(pos, toward, self.p.s_near as f64, self.turn);
        self.turn += 1;
        if self.seeds.len() >= self.p.s_max.max(1) {
            self.seeds.remove(0);
        }
        self.seeds.push(Seed { pos: spot, until: tick + self.p.s_life, next_show: tick });
        sim.play_sfx(&zy("s_drop"), me, &at(spot));
        self.n_seeds += 1;
        if self.n_seeds <= 8 || self.n_seeds % 25 == 0 {
            wlog(format!("{} SEED #{} ({why}) at ({:.0}, {:.0}), {} on the ground", head(sim, me), self.n_seeds, spot.0,
                         spot.1, self.seeds.len()));
        }
    }

    /// 种子的画面（一轮 `s_show` tick）重放，过期的枯掉。
    fn seeds(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        self.seeds.retain(|s| s.until > tick);
        for s in &mut self.seeds {
            if tick >= s.next_show {
                s.next_show = tick + self.p.s_show;
                sim.play_view_effect(&zy("s_seed"), me, &at(s.pos), 0, 0, 0);
            }
        }
    }

    fn grow(&mut self, sim: &mut StableSim<'_>, me: usize, kind: Kind, hit: impl Fn((f64, f64)) -> bool) {
        let tick = sim.tick();
        let (grown, keep): (Vec<Seed>, Vec<Seed>) = std::mem::take(&mut self.seeds).into_iter().partition(|s| hit(s.pos));
        self.seeds = keep;
        for s in grown {
            let (pic, snd, life) = match kind {
                Kind::Spitter => ("t_plant", "t_grow", self.p.t_life),
                Kind::Lasher => ("v_plant", "v_grow", self.p.t_life),
            };
            sim.play_view_effect(&zy(pic), me, &at(s.pos), 0, 0, 0);
            sim.play_sfx(&zy(snd), me, &at(s.pos));
            // the first strike as the data's plants: a third of a period after it grows
            self.plants.push(Plant { kind, pos: s.pos, until: tick + life, next: tick + self.p.t_per / 3, rage_until: 0 });
            self.n_grow += 1;
            if self.n_grow <= 10 || self.n_grow % 25 == 0 {
                wlog(format!("{} GROW #{}: a {kind:?} on a seed at ({:.0}, {:.0})", head(sim, me), self.n_grow, s.pos.0, s.pos.1));
            }
        }
    }

    /// 她的 Q / E / R 的标记（副本在出手那一 tick 挂在目标身上）。
    fn casts(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (f64, f64)) {
        let tags = [(zy("q_aim"), 0u8), (zy("e_aim"), 1u8), (zy("r_aim"), 2u8)];
        let mut now = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.team() == team {
                continue;
            }
            for (name, k) in &tags {
                if (0..e.buff_count()).filter_map(|j| e.buff_at(j)).any(|b| b.name() == name.as_str()) {
                    now.push((e.id(), *k, fpos(e.pos())));
                }
            }
        }
        let fresh: Vec<_> = now.iter().filter(|(id, k, _)| !self.aim_seen.contains(&(*id, *k))).cloned().collect();
        self.aim_seen = now.iter().map(|(id, k, _)| (*id, *k)).collect();
        let tick = sim.tick();
        for (id, k, land) in fresh {
            match k {
                0 => {
                    let r = self.p.s_r as f64;
                    self.grow(sim, me, Kind::Spitter, |s| dist(s, land) <= r);
                }
                1 => {
                    let d = dist(pos, land).max(1.0);
                    let over = self.p.e_over as f64 / d;
                    let end = (land.0 + (land.0 - pos.0) * over, land.1 + (land.1 - pos.1) * over);
                    let r = self.p.s_r as f64;
                    self.grow(sim, me, Kind::Lasher, |s| seg_dist(s, pos, end) <= r);
                }
                _ => {
                    let r = self.p.r_r as f64;
                    let mut n = 0;
                    for pl in self.plants.iter_mut().filter(|pl| dist(pl.pos, land) <= r) {
                        pl.rage_until = tick + self.p.r_rage;
                        pl.next = pl.next.min(tick + 1);
                        n += 1;
                    }
                    if n > 0 {
                        self.n_rage += 1;
                        if self.n_rage <= 8 {
                            wlog(format!("{} RAGE #{}: {n} of her seed plants round #{id}'s spot", head(sim, me), self.n_rage));
                        }
                    }
                }
            }
        }
    }

    fn strike(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, level: usize, ap: usize) {
        let tick = sim.tick();
        self.plants.retain(|pl| pl.until > tick);
        if self.plants.iter().all(|pl| pl.next > tick) {
            return;
        }
        let units = enemies(sim, team);
        let dmg = plant_damage(&self.p, level, ap);
        let mut spits = Vec::new();
        for pl in &mut self.plants {
            if pl.next > tick {
                continue;
            }
            let reach = match pl.kind {
                Kind::Spitter => self.p.t_r,
                Kind::Lasher => self.p.v_r,
            } as f64;
            pl.next = tick + strike_period(&self.p, pl.rage_until > tick);
            let Some(u) = choose(&units, pl.pos, reach) else { continue };
            self.n_strike += 1;
            if self.n_strike <= 10 || self.n_strike % 100 == 0 {
                wlog(format!("{} STRIKE #{}: {:?} -> #{} ({}) for {dmg}{}", head(sim, me), self.n_strike, pl.kind, u.id,
                             if u.champion { "champion" } else { "unit" }, if pl.rage_until > tick { ", enraged" } else { "" }));
            }
            match pl.kind {
                Kind::Spitter => {
                    let spec = ProjectileSpawnV1 {
                        caster_id: me,
                        team,
                        x: pl.pos.0.round().max(0.0) as u64,
                        y: (pl.pos.1 - SPIT_UP as f64).round().max(0.0) as u64,
                        radius: 1_000,
                        speed: self.p.spit_speed as u64,
                        move_kind: ProjectileMoveKindV1::Target.code(),
                        target_id: u.id,
                        target_x: 0,
                        target_y: 0,
                        penetrate: false,
                        attack_type: AttackTypeV1::Skill.code(),
                        casting_type: CastingTypeV1::Targeting.code(),
                        casting_target: CastingTargetV1::None.code(),
                    };
                    sim.spawn_projectile(&zy("t_spit"), &format!("{ID}:noop"), &spec);
                    let fly = (dist(pl.pos, u.pos) / self.p.spit_speed as f64).ceil() as usize;
                    spits.push(Spit { target: u.id, due: tick + fly.max(1), dmg });
                }
                Kind::Lasher => {
                    sim.deal_damage_typed(me, u.id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    let mut slow = BuffV1::timed(&zy("v_slow"), self.p.v_slow_t);
                    slow.move_speed_mult = -(self.p.v_slow as i32);
                    sim.add_buff(u.id, &slow);
                    let hit = InputTargetV1::target(u.id);
                    sim.play_view_effect(&zy("v_hit"), me, &hit, 0, 0, 0);
                    sim.play_sfx(&zy("v_hit"), me, &hit);
                }
            }
        }
        self.spits.extend(spits);
    }

    /// 飞到的刺扣血。
    fn land(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let (due, wait): (Vec<Spit>, Vec<Spit>) = std::mem::take(&mut self.spits).into_iter().partition(|s| s.due <= tick);
        self.spits = wait;
        for s in due {
            if !sim.get_entity(s.target).is_some_and(|e| e.is_alive()) {
                continue;
            }
            sim.deal_damage_typed(me, s.target, s.dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            let hit = InputTargetV1::target(s.target);
            sim.play_view_effect(&zy("t_hit"), me, &hit, 0, 0, 0);
            sim.play_sfx(&zy("t_hit"), me, &hit);
        }
    }

    /// 她参与击杀敌方英雄：马上掉一颗种子。
    fn takedowns(&mut self, sim: &mut StableSim<'_>) -> bool {
        let n = sim.kill_log_count();
        if self.kills_seen > n {
            self.kills_seen = 0; // a new match in a reused passive
        }
        let Some(mine) = sim.get_player(self.player) else { return false };
        let (team, lane) = (mine.team(), mine.lane().map(|l| l.code()));
        let mut took = false;
        while self.kills_seen < n {
            let Some(k) = sim.kill_log_at(self.kills_seen) else { break };
            self.kills_seen += 1;
            if k.killer_team != team || lane.is_none() {
                continue;
            }
            let lane = lane.unwrap_or(u32::MAX);
            let assist = k.assist_positions.iter().take(k.assist_count.min(4) as usize).any(|&a| a == lane);
            if k.killer_position == lane || assist {
                took = true;
            }
        }
        took
    }
}

impl StablePassive for Garden {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.player = player;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if self.next_seed == 0 {
            self.next_seed = sim.tick() + self.p.s_cd;
        }
        wlog(format!("{} SPAWN: the add-on's Zyra (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, ap, level, pos, alive) = (e.team(), e.stat().magic_power, e.level(), fpos(e.pos()), e.is_alive());
        let tick = sim.tick();
        if self.takedowns(sim) && alive {
            self.n_take += 1;
            if self.n_take <= 6 {
                wlog(format!("{} TAKEDOWN #{}: a seed now", head(sim, me), self.n_take));
            }
            self.drop_seed(sim, me, team, pos, "takedown");
            self.next_seed = tick + self.p.s_cd;
        }
        if alive && tick >= self.next_seed {
            self.next_seed = tick + self.p.s_cd;
            self.drop_seed(sim, me, team, pos, "timer");
        }
        // her seeds and plants stay after her death (League's)
        self.seeds(sim, me);
        self.casts(sim, me, team, pos);
        self.land(sim, me);
        self.strike(sim, me, team, level, ap);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: seeds {} ({} on the ground), grown {}, strikes {}, rages {}, takedowns {}",
                             head(sim, me), self.n_seeds, self.seeds.len(), self.n_grow, self.n_strike, self.n_rage,
                             self.n_take));
            }
        }
    }
}

struct NoopFx;
impl StableEffectType for NoopFx {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Zyra's seeds on the ground, seed plants striking champions first) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:noop"), NoopFx);
    module.add_native_passive(format!("{ID}:garden"), Garden::default());
    host.log(LogLevel::Info, "league_zyra v1 loaded (Zyra's seeds on the ground, seed plants striking champions first).");
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
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"s_cd":480,"pl_hi":90,"x":1}"#);
        assert_eq!((p.s_cd, p.pl_hi), (480, 90));
        assert_eq!(p.t_per, Params::default().t_per);
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"t_per":0,"v_slow":200}"#).t_per, 2);
        assert_eq!(parse_params(r#"{"v_slow":200}"#).v_slow, 95);
    }

    #[test]
    fn plants_grow_stronger_with_her_level() {
        let p = Params::default();
        assert_eq!(plant_damage(&p, 1, 0), 20);
        assert_eq!(plant_damage(&p, 18, 0), 100);
        assert_eq!(plant_damage(&p, 30, 0), 100);
        assert_eq!(plant_damage(&p, 1, 100), 32); // + 12 % of 100 AP
        assert!(plant_damage(&p, 9, 0) > 50 && plant_damage(&p, 9, 0) < 60);
    }

    #[test]
    fn enraged_plants_strike_twice_as_often() {
        let p = Params::default();
        assert_eq!(strike_period(&p, false), 60);
        assert_eq!(strike_period(&p, true), 30);
    }

    #[test]
    fn seeds_fall_toward_the_nearest_champion() {
        let s = seed_spot((0.0, 0.0), Some((100_000.0, 0.0)), 30_000.0, 0);
        assert!((s.0 - 30_000.0).abs() < 1.0 && s.1.abs() < 1.0);
        let s = seed_spot((0.0, 0.0), Some((20_000.0, 0.0)), 30_000.0, 0);
        assert!((s.0 - 10_000.0).abs() < 1.0); // at most half way
        let a = seed_spot((50_000.0, 50_000.0), None, 30_000.0, 0);
        let b = seed_spot((50_000.0, 50_000.0), None, 30_000.0, 2);
        assert!(dist(a, b) > 10_000.0);
    }

    #[test]
    fn grasping_roots_reach_seeds_along_the_line() {
        assert!(seg_dist((50.0, 10.0), (0.0, 0.0), (100.0, 0.0)) < 10.5);
        assert!((seg_dist((150.0, 0.0), (0.0, 0.0), (100.0, 0.0)) - 50.0).abs() < 1e-6);
    }

    #[test]
    fn champions_come_first() {
        let units = [
            Unit { id: 1, pos: (1_000.0, 0.0), champion: false },
            Unit { id: 2, pos: (40_000.0, 0.0), champion: true },
            Unit { id: 3, pos: (90_000.0, 0.0), champion: true },
        ];
        assert_eq!(choose(&units, (0.0, 0.0), 50_000.0).map(|u| u.id), Some(2));
        assert_eq!(choose(&units, (0.0, 0.0), 10_000.0).map(|u| u.id), Some(1));
        assert!(choose(&units, (200_000.0, 0.0), 10_000.0).is_none());
    }

    #[test]
    fn buff_names_fit() {
        for x in ["q_aim", "e_aim", "r_aim", "v_slow", "s_seed", "t_spit", "t_plant", "v_plant"] {
            assert!(zy(x).len() <= BUFF_NAME_CAP);
        }
    }
}
