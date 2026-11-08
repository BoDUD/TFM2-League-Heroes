//! 赛恩附加包（用户选「主包数据 + 附加包复活」）：主包数据做不到的两件事。
//!
//! `mod.override_info` 把主包的赛恩换成 `override/` 里的副本（tools/kit/build_sion.py 的 native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_sion:glory`（参数在英雄数据的 `passive.params` 里）；
//! - 普攻不再自己查击杀加生命（本包按每一次击杀加，技能击杀也算）。
//!
//! - **死亡荣耀**：每条命第一次受到致命伤害时不倒下（本包一直给他挂着 `league_sion_p_guard`「不死」，生命停在 1 就触发），
//!   变成亡灵 `z_t` tick：生命回满，之后每 tick 均匀流失（`z_t` tick 后归零），攻速 +`z_as`%、吸血 `z_vamp`%，
//!   不能放技能（`BlockSkill`），身上挂 `league_sion_p_zombie`（画面）。时间到就倒下，击杀算最后打他的那个人；
//!   亡灵不是不死的（0.1.2）：血被打光就照常阵亡。
//!   别人给的「不死」（索拉卡 W、基兰符文、凯尔等）在身上时不触发：那段时间他本来就死不了。
//! - **灵魂熔炉（被动）**：每击杀一个单位永久 +`k_u` 最大生命，英雄 +`k_c`（英雄联盟：小兵 4、英雄和大型野怪 15）；
//!   技能击杀也算，阵亡后不丢（主包数据的版本只算普攻击杀，阵亡就没了）。
//!
//! - **亡灵不回城**（`zombie.rs`，0.1.1）：亡灵时 AI 要回城或撤退就改成普攻最近的敌人（用户：「塞恩的僵尸 死了还能跑回城的？」）。
//! - **大招的日志**（`ult.rs`，0.2.0，用户：「塞恩是不是也不太放大？」）：大招是主包的数据，本包只看他身上的标记记日志
//!   （`ARMED` / `LAPSED` / `CHARGE` / `HIT` / `MISS`，每条命一行小结）；变亡灵时摘掉上膛标记（亡灵不该冲出去）。
//! - **救人只救被硬控的**（0.3.0，2026-11-06 的日志：11 次冲撞全是「救人」）：游戏 0.7.0 起数据的 `AllyChampionInCC` 连施法
//!   动作也算。上膛时被动每 tick 找 `r_save` 内被硬控、身边有敌方英雄的队友（`ult::held_pick`），有就给他续 `league_sion_r_cc`；
//!   副本的轮询看到它才走「救人」，对每个队友调 `league_sion:held`，被选中的那个让他身上出现 1 tick 的 `league_sion_r_this`，
//!   探针飞向这个队友。`CHARGE` 行写出救的是谁、什么控制；`LAPSED` 行过 4 tick 再读冷却（看得到退还）。
//! - **冲撞的原因自己数**（0.3.1，2026-11-08 的日志检查：8 次冲撞的原因全是 unknown）：数数的标记 `r_n2` / `r_n3` 在轮询那一
//!   tick 挂上、下一 tick 冲出去时一起摘掉，被动看不到；前一 tick 的标记看不出原因时，`CHARGE` 行在冲出去这一 tick 自己数
//!   `R_NEAR` 内（加两个身体）的队友：2 名以上「团战」、1 名「开团 / 追击」、没有「哪条规则都不符」（`ult::counted_reason`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sion.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod ult;
pub mod zombie;

const ID: &str = "league_sion";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_sion") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 「不死」挂多久、多久续一次（一直挂着，复活用掉前不断）。
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;

fn sn(x: &str) -> String {
    format!("league_sion_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SION_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_sion.log");
        }
    }
    PathBuf::from("league_sion.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the game, 2026-10-12)
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 计算（单元测试用） =====================

/// 亡灵第 `k` tick（0 起）该剩多少生命：从 `max` 均匀降到 `z_t` tick 时的 0；至少 1（不死还在）。
pub fn zombie_hp(max: usize, k: usize, z_t: usize) -> usize {
    if k >= z_t {
        return 1;
    }
    (max * (z_t - k) / z_t).max(1)
}

/// 亡灵这一 tick 的流失：吸血回上来的不算进计划，所以按「每 tick 少 max / z_t」扣现在的生命。
pub fn decay_step(max: usize, z_t: usize) -> usize {
    (max / z_t.max(1)).max(1)
}

/// 灵魂熔炉一次击杀加多少最大生命。
pub fn kill_hp(victim_is_champion: bool, p: &Params) -> usize {
    if victim_is_champion { p.k_c } else { p.k_u }
}

/// 名字是不是本包的「不死」（别的「不死」在身上时不触发复活）。
pub fn ours(name: &str) -> bool {
    name == sn("p_guard") || name == sn("p_zombie")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

/// The player whose champion `id` is (None: a tower, a minion, a monster).
fn player_of(sim: &StableSim<'_>, id: usize) -> Option<usize> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find(|p| p.champion().is_some_and(|c| c.id() == id)).map(|p| p.id())
}

/// 倒下时算谁的击杀：最后打他的还在就是他；他在这期间死了又复活（新的实体），算他玩家现在的英雄；都没有就算最近的活着的
/// 敌方英雄——从不算赛恩自己（0.1.4，11-02 的日志：42 次倒下里 8 次「killed by league_sion」，敌方丢了这个人头）。
fn killer(sim: &StableSim<'_>, me: usize, last: Option<usize>, player: Option<usize>) -> usize {
    if let Some(a) = last.filter(|&a| sim.get_entity(a).is_some()) {
        return a;
    }
    if let Some(c) = player.and_then(|p| sim.get_player(p)).and_then(|p| p.champion()).filter(|c| c.is_alive()) {
        return c.id();
    }
    let Some(e) = sim.get_entity(me) else { return me };
    let (team, at) = (e.team(), e.pos());
    let foes: Vec<(usize, Option<EntityKindV1>, (u64, u64))> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive())
        .map(|u| (u.id(), if u.is_champion() { Some(EntityKindV1::Champion) } else { u.kind() }, u.pos()))
        .collect();
    fallback_killer(me, at, &foes)
}

/// The killer when neither the last hitter nor his player's champion is there: the nearest living enemy champion, else
/// the nearest living unit of the other side - a tower, a minion, a summon, the nexus (League's "executed"); Sion himself
/// only when nothing at all stands. `foes`: (id, kind, where) of the living units not on his team; neutral monsters do
/// not count. 0.1.5, the 11-03 night logs: `FALL #3: ... killed by league_sion#23` - the last hitter (Kalista) had died
/// to the zombie and no enemy champion was alive, so the kill went to him.
pub fn fallback_killer(me: usize, at: (u64, u64), foes: &[(usize, Option<EntityKindV1>, (u64, u64))]) -> usize {
    let d2 = |p: (u64, u64)| (p.0 as f64 - at.0 as f64).powi(2) + (p.1 as f64 - at.1 as f64).powi(2);
    let nearest = |kinds: &[EntityKindV1]| {
        foes.iter()
            .filter(|f| f.1.is_some_and(|k| kinds.contains(&k)))
            .min_by(|a, b| d2(a.2).total_cmp(&d2(b.2)))
            .map(|f| f.0)
    };
    nearest(&[EntityKindV1::Champion])
        .or_else(|| nearest(&[EntityKindV1::Tower, EntityKindV1::Minion, EntityKindV1::Summon, EntityKindV1::Nexus]))
        .unwrap_or(me)
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub k_u: usize,
    pub k_c: usize,
    pub z_t: usize,
    pub z_as: usize,
    pub z_vamp: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { k_u: 4, k_c: 15, z_t: 540, z_as: 60, z_vamp: 100 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "k_u" => p.k_u = v,
            "k_c" => p.k_c = v,
            "z_t" => p.z_t = v,
            "z_as" => p.z_as = v,
            "z_vamp" => p.z_vamp = v,
            _ => {}
        }
    }
    p
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

#[derive(Clone, Default)]
struct Glory {
    p: Params,
    me: usize,
    /// 灵魂熔炉攒下的最大生命（跨命保留）。
    stacks: usize,
    /// 这条命的复活还在。
    ready: bool,
    /// 亡灵开始的 tick（不在亡灵状态时 None）。
    zombie: Option<usize>,
    /// 最后一个打他的（倒下时算击杀）。
    last_hit: Option<usize>,
    /// 最后一个打他的英雄的玩家：那个英雄在亡灵期间死了又复活（新的实体），击杀算他的新英雄（`killer`）。
    last_player: Option<usize>,
    next_guard: usize,
    /// 这条命里见过他 1 血以上：游戏 0.6.4 开局第 0 tick 读到的血量还是 0，那不是致命伤（每局第一条命都在 0 tick 变成亡灵、
    /// 9 秒后倒下，用户：「塞恩有bug吧 开局血掉光？」）。
    alive_seen: bool,
    /// 大招的日志状态（`ult.rs`）。
    r: ult::Onslaught,
    /// 这一 tick 救人的对象（被硬控的队友、控制种类、离他多远；上膛时才找）：`CHARGE` 行用前一 tick 的。
    held: Option<Held>,
    /// 过期的窗口等 `ult::LAPSE_READ` tick 再读冷却：到哪一 tick、跑了多久、窗口里看到的。
    lapse: Option<(usize, usize, String)>,
}

/// 救人的对象（`ult::held_pick` 选的）。
#[derive(Clone, Debug, PartialEq)]
struct Held {
    id: usize,
    kinds: Vec<u32>,
    far: f64,
}

/// 他上膛时该救的队友：`r_save` 内被硬控、身边 `r_peel` 内有看得见的敌方英雄、离他最近的那个（`ult::held_pick`），附上控制
/// 种类和距离。被动和 `league_sion:held` 都用它，同一 tick 选出来的是同一个。
fn held_ally(sim: &StableSim<'_>, me: usize) -> Option<Held> {
    let e = sim.get_entity(me)?;
    let (team, at, my_r) = (e.team(), e.pos(), e.radius() as f64);
    let at = (at.0 as f64, at.1 as f64);
    let (mut mates, mut foes) = (Vec::new(), Vec::new());
    for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if !u.is_champion() || !u.is_alive() || u.id() == me {
            continue;
        }
        let pos = (u.pos().0 as f64, u.pos().1 as f64);
        if u.team() == team {
            if !u.is_targetable() {
                continue; // banished, carried, in stasis: the probe cannot reach him, nor can anyone hurt him
            }
            let mut hard: Vec<u32> = (0..u.cc_count()).filter_map(|i| u.cc_at(i)).map(|c| c.kind).filter(|&k| ult::is_hard_cc(k)).collect();
            hard.sort_unstable();
            hard.dedup();
            mates.push(ult::Mate { id: u.id(), at: pos, r: u.radius() as f64, hard });
        } else if u.is_targetable() && sim.is_visible(team, u.id()) {
            foes.push((pos, u.radius() as f64));
        }
    }
    let id = ult::held_pick(at, my_r, &mates, &foes)?;
    let m = mates.into_iter().find(|m| m.id == id)?;
    let far = ((m.at.0 - at.0).powi(2) + (m.at.1 - at.1).powi(2)).sqrt();
    Some(Held { id, kinds: m.hard, far })
}

/// `league_sion:held`：副本的轮询在 `r_cc` 在时对每个队友调它，`held_ally` 选中的那个让他身上出现 1 tick 的 `r_this`
/// （league_galio:entrance 的做法），救人的探针飞向这个队友。
struct HeldPick;

impl StableEffectType for HeldPick {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        if held_ally(sim, caster).is_some_and(|h| h.id == input.target_id) {
            sim.add_buff(caster, &BuffV1::timed(ult::R_THIS, 1));
        }
    }
}

/// 大招轮询会看到的：r_range 内的敌方英雄数、r_near 内的队友数（圆心距离）、最近的敌方英雄有多远、他的血量百分比。
fn r_context(sim: &StableSim<'_>, me: usize) -> String {
    let Some(e) = sim.get_entity(me) else { return String::new() };
    let (team, at) = (e.team(), e.pos());
    let (hp, max) = e.hp();
    let d = |p: (u64, u64)| (((p.0 as f64 - at.0 as f64).powi(2) + (p.1 as f64 - at.1 as f64).powi(2)).sqrt()) as u64;
    let (mut enemies, mut allies, mut nearest) = (0usize, 0usize, u64::MAX);
    for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if !u.is_champion() || !u.is_alive() || u.id() == me {
            continue;
        }
        let dist = d(u.pos());
        if u.team() == team {
            allies += (dist <= ult::R_NEAR) as usize;
        } else {
            nearest = nearest.min(dist);
            enemies += (dist <= ult::R_RANGE) as usize;
        }
    }
    let near = if nearest == u64::MAX { "-".to_string() } else { nearest.to_string() };
    format!("hp {}%, enemy champions in reach {enemies} (nearest {near}), allies near {allies}",
            if max > 0 { hp * 100 / max } else { 0 })
}

/// 他身边的队友数（`ult::allies_near`：`R_NEAR` 内，加两个身体），`CHARGE` 行认不出原因时用（0.3.1）。
fn mates_near(sim: &StableSim<'_>, me: usize) -> usize {
    let Some(e) = sim.get_entity(me) else { return 0 };
    let (team, at, my_r) = (e.team(), e.pos(), e.radius() as f64);
    let mates: Vec<((f64, f64), f64)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_champion() && u.is_alive() && u.id() != me && u.team() == team)
        .map(|u| ((u.pos().0 as f64, u.pos().1 as f64), u.radius() as f64))
        .collect();
    ult::allies_near((at.0 as f64, at.1 as f64), my_r, &mates)
}

impl Glory {
    /// 救人（0.3.0）：上膛时找被硬控的队友（`held_ally`），有就给他续 `r_cc`（副本的轮询读它）；记下来给 `CHARGE` 行。
    fn save_flag(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.held = None;
        if !buffs(sim, me).iter().any(|b| b.name() == sn("r_arm")) {
            return;
        }
        let Some(h) = held_ally(sim, me) else { return };
        sim.entity_remove_buff(me, ult::R_CC);
        sim.add_buff(me, &BuffV1::timed(ult::R_CC, ult::R_CC_T));
        self.held = Some(h);
    }

    /// 过期窗口的那一行（0.3.0）：过 `LAPSE_READ` tick 再读冷却，退还已经生效（过期那一 tick 读的还是 3002）；`early`：
    /// 等不到了（阵亡、变亡灵），现在读。
    fn lapse_line(&mut self, sim: &StableSim<'_>, me: usize, now: usize, early: bool) {
        let Some((due, ran, seen)) = self.lapse.take() else { return };
        if now < due && !early {
            self.lapse = Some((due, ran, seen));
            return;
        }
        if let Some(k) = counted("lapsed") {
            let cd = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Ult)).map_or(0, |c| c.remaining);
            let when = if now >= due { format!("{} ticks on", ult::LAPSE_READ) } else { "read early".to_string() };
            wlog(format!("{} R LAPSED #{k}: no charge in {ran} ticks, {seen}; ult cooldown left {cd} ticks ({when}; the refund caps it at 72)",
                         head(sim, me)));
        }
    }

    /// 每 tick 看大招的标记，记下上膛、过期、冲撞、撞中。`held`：前一 tick 救人的对象（救人的冲撞就是为了他）。
    fn watch_ult(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, held: Option<&Held>) {
        self.lapse_line(sim, me, now, false);
        let names: std::collections::HashSet<String> = buffs(sim, me).iter().map(|b| b.name().to_string()).collect();
        for ev in self.r.step(now, &names) {
            match ev {
                ult::Event::Armed => {
                    if let Some(k) = counted("armed") {
                        wlog(format!("{} R ARMED #{k}: window {} ticks; {}", head(sim, me), ult::R_ARM_T, r_context(sim, me)));
                    }
                }
                ult::Event::Poll => {
                    let ctx = r_context(sim, me);
                    let num = |key: &str| ctx.split(key).nth(1).and_then(|x| x.split(' ').next()).and_then(|x| x.parse().ok()).unwrap_or(0);
                    self.r.seen.add(num("in reach "), num("allies near "));
                }
                ult::Event::Lapsed(ran) => {
                    // 0.3.0 (11-06: "ult cooldown left 3002 ticks" x3, re-armed 188 / 756 ticks later): the refund's flag
                    // comes on this tick and caps the cooldown on the next ones - read it LAPSE_READ ticks on
                    self.lapse_line(sim, me, now, true);
                    self.lapse = Some((now + ult::LAPSE_READ, ran, self.r.seen.summary()));
                }
                ult::Event::Charge(why) => {
                    if let Some(k) = counted("charge") {
                        // 0.3.1 (the 11-08 logs: 8 of 8 "unknown"): the count flags never reach the snapshot - counted here
                        let why = if why == ult::UNKNOWN { ult::counted_reason(held.is_some(), mates_near(sim, me)) } else { why };
                        let whom = match (why, held) {
                            ("save", Some(h)) => format!(" {} in {} {:.0} away", who(sim, h.id), ult::cc_names(&h.kinds), h.far),
                            ("save", None) => " (the ally is no longer held)".to_string(),
                            _ => String::new(),
                        };
                        wlog(format!("{} R CHARGE #{k}: {why}{whom}; {}", head(sim, me), r_context(sim, me)));
                    }
                }
                ult::Event::Done(ran) => {
                    if let Some(k) = counted("done") {
                        wlog(format!("{} R {} #{k}", head(sim, me), ult::outcome(ran)));
                    }
                }
            }
        }
    }

    /// 一条命结束（阵亡或变亡灵）：这条命大招上膛了几次、冲了几次。
    fn r_life_line(&mut self, sim: &StableSim<'_>, me: usize, end: &str) {
        let now = sim.tick();
        self.lapse_line(sim, me, now, true);
        self.held = None;
        if self.r.armed > 0 || self.r.charged > 0 {
            if let Some(k) = counted("life") {
                wlog(format!("{} R this life #{k} ({end}): armed {}, charged {}", head(sim, me), self.r.armed, self.r.charged));
            }
        }
        self.r.reset();
    }

    fn stack_buff(&self, sim: &mut StableSim<'_>, me: usize) {
        sim.entity_remove_buff(me, &sn("k_hp"));
        if self.stacks > 0 {
            let mut b = BuffV1::named(&sn("k_hp"));
            b.hp = self.stacks as i32;
            sim.add_buff(me, &b);
        }
    }

    fn guard(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        if now < self.next_guard {
            return;
        }
        let mut g = BuffV1::timed(&sn("p_guard"), GUARD_T);
        g.undying = true;
        sim.entity_remove_buff(me, &sn("p_guard"));
        sim.add_buff(me, &g);
        self.next_guard = now + GUARD_EVERY;
    }

    fn rise(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        self.ready = false;
        self.zombie = Some(now);
        sim.entity_remove_buff(me, &sn("p_guard"));
        // the zombie casts nothing, but the kit's poll keeps running on him: an open window would still charge (0.2.0)
        if sim.entity_remove_buff(me, &sn("r_arm")) > 0 {
            if let Some(k) = counted("zombie_arm") {
                wlog(format!("{} R window closed #{k}: he rose as the zombie while R was armed", head(sim, me)));
            }
        }
        self.r_life_line(sim, me, "zombie");
        // mortal (0.1.2, the user 2026-10-25: 「塞恩得尸体太变态 死了比活着的时候还能扛」): the zombie was undying for all
        // its z_t ticks - full health, 100% life steal and nothing could kill it before the time ran out; League's zombie
        // dies to damage, its health running down meanwhile
        let mut z = BuffV1::timed(&sn("p_zombie"), self.p.z_t + 2);
        z.attack_speed_mult = self.p.z_as as i32;
        z.vamp = self.p.z_vamp as i32;
        sim.add_buff(me, &z);
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockSkill, self.p.z_t as u64));
        sim.entity_set_hp(me, max);
        sim.play_sfx(&sn("p_rise"), me, &InputTargetV1::target(me));
        sim.play_sfx(&sn("vo_p"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("rise") {
            wlog(format!("{} RISE #{k}: lethal damage caught at 1 hp (last hit by {}), zombie {} ticks from {max} hp",
                         head(sim, me), self.last_hit.map_or_else(|| "-".to_string(), |a| who(sim, a)), self.p.z_t));
        }
    }

    fn fall(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.zombie = None;
        sim.entity_remove_buff(me, &sn("p_zombie"));
        let (hp, _) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        let killer = killer(sim, me, self.last_hit, self.last_player);
        sim.deal_damage_typed(killer, me, hp + 1000, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        if let Some(k) = counted("fall") {
            wlog(format!("{} FALL #{k}: the zombie's time is up, killed by {}", head(sim, me), who(sim, killer)));
        }
    }
}

impl StablePassive for Glory {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.ready = true;
        self.zombie = None;
        self.last_hit = None;
        self.last_player = None;
        self.next_guard = 0;
        self.alive_seen = false;
        self.r.reset();
        self.held = None;
        self.lapse = None;
        self.stack_buff(sim, me);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Sion (player {player}, team {team}), {:?}, soul furnace +{} hp",
                         head(sim, me), self.p, self.stacks));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (hp, max) = e.hp();
        let now = sim.tick();
        if let Some(t0) = self.zombie {
            let k = now.saturating_sub(t0);
            if k >= self.p.z_t {
                self.fall(sim, me);
            } else if hp > 1 {
                // max / z_t a tick off what he has: untouched he reaches 1 at the end (zombie_hp), what the life steal
                // brings back stays
                sim.entity_set_hp(me, hp.saturating_sub(decay_step(max, self.p.z_t)).max(1));
            }
            return;
        }
        if !self.ready {
            return;
        }
        if hp > 1 {
            self.alive_seen = true;
        }
        // this tick's save first (its r_cc is in the names watch_ult keeps for the next tick's CHARGE reason); the
        // CHARGE line names the ally of the tick before, when the poll's probe went out
        let before = self.held.clone();
        self.save_flag(sim, me);
        self.watch_ult(sim, me, now, before.as_ref());
        self.guard(sim, me, now);
        if hp <= 1 && self.alive_seen {
            let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
            if !other_undying(&list) {
                self.rise(sim, me, now);
            }
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, _: usize, attacker: usize, damage: usize) {
        if damage > 0 && attacker != self.me && sim.get_entity(attacker).is_some() {
            self.last_hit = Some(attacker);
            self.last_player = player_of(sim, attacker);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        let champ = sim.get_entity(victim).is_some_and(|v| v.is_champion());
        self.stacks += kill_hp(champ, &self.p);
        self.stack_buff(sim, me);
        if champ {
            if let Some(k) = counted("furnace") {
                wlog(format!("{} FURNACE #{k}: {} killed, max health +{} in all", head(sim, me), who(sim, victim),
                             self.stacks));
            }
        }
    }

    /// 小兵、野怪的击杀（游戏 0.6.4 起才有这个回调；`on_kill` 只管英雄，所以之前附加包里打死小兵野怪一直没加生命）：
    /// 照说明「每击杀一个单位 +`k_u`」。大小龙等史诗野怪奖励全队，两个回调都不触发。
    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        let camp = sim.get_entity(victim).and_then(|v| v.kind()) == Some(EntityKindV1::Jungle);
        self.stacks += kill_hp(false, &self.p);
        self.stack_buff(sim, me);
        if let Some(k) = counted("unit") {
            wlog(format!("{} FURNACE unit kill #{k} ({}): max health +{} in all", head(sim, me),
                         if camp { "camp" } else { "minion" }, self.stacks));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.zombie = None;
        self.ready = false;
        let me = self.me;
        self.r_life_line(sim, me, "dead");
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sion: Glory in Death's zombie, Soul Furnace's health from every kill, R's save only for an ally in hard crowd control) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:glory"), Glory::default());
    module.add_native_effect(format!("{ID}:held"), HeldPick);
    module.add_player_input_ai(zombie::Zombie);
    host.log(LogLevel::Info, "league_sion loaded (Glory in Death's zombie, Soul Furnace from every kill, Unstoppable Onslaught saving only allies in hard crowd control).");
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
    fn the_zombie_drains_to_nothing() {
        assert_eq!(zombie_hp(2000, 0, 540), 2000);
        assert_eq!(zombie_hp(2000, 270, 540), 1000);
        assert_eq!(zombie_hp(2000, 539, 540), 3);
        assert_eq!(zombie_hp(2000, 540, 540), 1);
        assert_eq!(decay_step(2000, 540), 3);
        assert_eq!(decay_step(100, 540), 1);
    }

    #[test]
    fn soul_furnace_by_victim() {
        let p = Params::default();
        assert_eq!(kill_hp(false, &p), 4);
        assert_eq!(kill_hp(true, &p), 15);
    }

    #[test]
    fn only_someone_elses_undying_holds_the_rise_back() {
        let l = |v: &[(&str, bool)]| v.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        assert!(!other_undying(&l(&[("league_sion_p_guard", true)])));
        assert!(!other_undying(&l(&[("league_sion_p_guard", true), ("league_sion_k_hp", false)])));
        assert!(other_undying(&l(&[("league_sion_p_guard", true), ("league_soraka_w_guard", true)])));
        assert!(other_undying(&l(&[("league_zilean_r_rune", true)])));
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"k_c":15,"k_u":4,"z_as":60,"z_t":540,"z_vamp":100}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_zombie_never_credits_himself_while_an_enemy_unit_stands() {
        use EntityKindV1::*;
        let (me, at) = (23, (100_000, 100_000));
        let champ = (21, Some(Champion), (180_000, 100_000));
        let minion = (634, Some(Minion), (110_000, 100_000));
        let tower = (2, Some(Tower), (105_000, 100_000));
        let nexus = (1, Some(Nexus), (400_000, 400_000));
        let camp = (900, Some(Jungle), (100_500, 100_000));
        // an enemy champion first, even farther than the minions
        assert_eq!(fallback_killer(me, at, &[minion, champ, tower, camp]), 21);
        // the 11-03 night logs: the last hitter (Kalista) died to the zombie, no enemy champion alive - `killed by
        // league_sion#23`; now the nearest tower / minion / summon / nexus, never a neutral monster
        assert_eq!(fallback_killer(me, at, &[minion, tower, camp, nexus]), 2);
        assert_eq!(fallback_killer(me, at, &[minion, camp]), 634);
        assert_eq!(fallback_killer(me, at, &[camp, nexus]), 1);
        assert_eq!(fallback_killer(me, at, &[camp]), me);
        assert_eq!(fallback_killer(me, at, &[]), me);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_sion.py");
        let src = std::fs::read_to_string(path).expect("build_sion.py");
        let d = Params::default();
        for (key, v) in [("k_u", d.k_u), ("k_c", d.k_c), ("z_t", d.z_t), ("z_as", d.z_as), ("z_vamp", d.z_vamp)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_sion.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_guard", "p_zombie", "k_hp", "p_rise", "vo_p", "r_arm", "r_cc", "r_this"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
