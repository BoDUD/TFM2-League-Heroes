//! 特朗德尔附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做。
//!
//! `mod.override_info` 把主包的特朗德尔换成 `override/` 里的副本（tools/kit/build_trundle.py --native），`passive` 换成本包的
//! `league_trundle:troll`：
//!
//! - **国王的贡品照英雄联盟回血**：主包只能在他自己打死的单位上回一口（击杀检测），回固定的数。本包每拍记下他身边 `p_r` 内的敌方
//!   单位，谁倒下了（不管是谁打死的）就回它最大生命 `p_pct`% 的血，站在冰面上时翻倍。
//! - **冰封领域留在地上**：主包的冰面跟着他走（一个加攻速、移速、回血的 buff）。副本只给他挂一个不带属性的 `league_trundle_w_on`
//!   当记号；本包在记号出现（或被刷新）时记下他脚下的位置，他站在那一圈（`w_r`）里时每拍挂 2 拍的 `league_trundle_w_in`（攻速、
//!   移速、回血），并且他每拍多回的血放大 `w_amp`%（英雄联盟：受到的所有治疗加成）。
//! - **寒冰之柱是地形**：主包的冰柱只减速（副本连定身也不要）。副本给冰柱旁的英雄挂 3 拍 `league_trundle_e_at`；本包看到它，就在
//!   那个英雄身后（背对特朗德尔的一侧）立一根半径 `e_wall` 的冰柱，立 `e_t` 拍，期间敌方英雄和小兵走不进去（每拍推到圈外）。
//! - **利齿撕咬偷固定的攻击力**：主包按百分比改双方攻击力。副本给被咬的单位挂 3 拍 `league_trundle_q_mark`；本包按它当时的攻击力，
//!   给特朗德尔加 `q_flat`%（`league_trundle_q_take`），它减一半（`league_trundle_q_lose`），各 `q_t` 拍。
//! - **强权至上照英雄联盟偷**：主包按百分比改双方护甲魔抗、伤害是真实伤害、回固定的血。副本给目标挂 `league_trundle_r_drain`；本包
//!   读它当时的护甲和魔抗，偷 `r_steal`%（`league_trundle_r_lose` / `league_trundle_r_take`，`r_t + r_keep` 拍），并且立刻造成它最大
//!   生命 `r_pct0`% 的魔法伤害、之后每 `r_p` 拍 `r_pct`%（`r_t` 拍内），每一下打掉多少血就给特朗德尔回多少（冰面上再放大）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_trundle.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_trundle";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// On him while the domain lasts (the data's W; no stats in the add-on's copy).
const W_ON: &str = "league_trundle_w_on";
/// On him while he stands in the domain (2 ticks, renewed): its attack speed, move speed and regeneration.
const W_IN: &str = "league_trundle_w_in";
/// On the champions at a pillar the tick it rises (3 ticks).
const E_AT: &str = "league_trundle_e_at";
/// On a unit Chomp bit (3 ticks).
const Q_MARK: &str = "league_trundle_q_mark";
/// Chomp's steal: his attack up, the unit's down.
const Q_TAKE: &str = "league_trundle_q_take";
const Q_LOSE: &str = "league_trundle_q_lose";
/// On Subjugate's champion while the steal lasts (the data's ult).
const R_DRAIN: &str = "league_trundle_r_drain";
/// Subjugate's steal: his defence and magic resistance up, the champion's down.
const R_TAKE: &str = "league_trundle_r_take";
const R_LOSE: &str = "league_trundle_r_lose";
/// A pillar stands this far behind its champion beyond its own radius (squares of 1000: the champion's body).
const PILLAR_GAP: u64 = 3000;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TRUNDLE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_trundle.log");
        }
    }
    PathBuf::from("league_trundle.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
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

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"))
}

/// Logs the first 40 of a kind, then every 100th.
fn often(n: usize) -> bool {
    n <= 40 || n % 100 == 0
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，build_trundle.NATIVE_KEYS）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 附近的敌方单位倒下时回它最大生命的这么多百分比。
    pub p_pct: usize,
    /// 「附近」：离他多远以内（距离单位）。
    pub p_r: u64,
    /// 冰面上的攻速、移速（百分比）和回血。
    pub w_as: usize,
    pub w_ms: usize,
    pub w_regen: usize,
    /// 冰面的半径。
    pub w_r: u64,
    /// 冰面上治疗放大的百分比。
    pub w_amp: usize,
    /// 冰柱立多少拍。
    pub e_t: usize,
    /// 冰柱的半径（走不进去的那一圈）。
    pub e_wall: u64,
    /// 利齿撕咬偷来的攻击力留多少拍。
    pub q_t: usize,
    /// 利齿撕咬：他加被咬者攻击力的这么多百分比（被咬者减一半）。
    pub q_flat: usize,
    /// 强权至上：偷走目标护甲、魔抗的这么多百分比。
    pub r_steal: usize,
    /// 强权至上：立刻打掉最大生命的百分比，之后每 r_p 拍的百分比。
    pub r_pct0: usize,
    pub r_pct: usize,
    pub r_p: usize,
    /// 强权至上持续吸取多少拍，偷来的护甲魔抗再多留多少拍。
    pub r_t: usize,
    pub r_keep: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_pct: 5, p_r: 50000, w_as: 50, w_ms: 15, w_regen: 6, w_r: 50000, w_amp: 25, e_t: 240, e_wall: 9000, q_t: 240, q_flat: 20, r_steal: 40, r_pct0: 10, r_pct: 3, r_p: 60, r_t: 240, r_keep: 240 }
    }
}

/// `{"p_pct":5,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        let u = v as usize;
        match k {
            "p_pct" => p.p_pct = u,
            "p_r" => p.p_r = v,
            "w_as" => p.w_as = u,
            "w_ms" => p.w_ms = u,
            "w_regen" => p.w_regen = u,
            "w_r" => p.w_r = v,
            "w_amp" => p.w_amp = u,
            "e_t" => p.e_t = u,
            "e_wall" => p.e_wall = v,
            "q_t" => p.q_t = u,
            "q_flat" => p.q_flat = u,
            "r_steal" => p.r_steal = u,
            "r_pct0" => p.r_pct0 = u,
            "r_pct" => p.r_pct = u,
            "r_p" => p.r_p = u,
            "r_t" => p.r_t = u,
            "r_keep" => p.r_keep = u,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

/// `pct`% of `of`, at least 1 when `of` is not 0.
pub fn share(of: usize, pct: usize) -> usize {
    if of == 0 { 0 } else { (of * pct / 100).max(1) }
}

/// A heal on the domain: `w_amp`% bigger.
pub fn amped(heal: usize, on_domain: bool, amp: usize) -> usize {
    if on_domain { heal + heal * amp / 100 } else { heal }
}

/// King's Tribute for a unit of `max_hp`: p_pct% of it, twice on the domain (the main pack's combo), amplified there.
pub fn tribute(p: &Params, max_hp: usize, on_domain: bool) -> usize {
    let h = share(max_hp, p.p_pct) * if on_domain { 2 } else { 1 };
    amped(h, on_domain, p.w_amp)
}

/// Chomp's steal from a unit's attack: (what he gains, what it loses).
pub fn chomp(p: &Params, attack: usize) -> (i32, i32) {
    let gain = share(attack, p.q_flat) as i32;
    (gain, (gain / 2).max(if gain > 0 { 1 } else { 0 }))
}

fn dist2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0);
    let dy = a.1.abs_diff(b.1);
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

/// Where a pillar rises: behind the champion as seen from Trundle, its edge `gap` past the champion's centre.
pub fn pillar_spot(me: (u64, u64), champ: (u64, u64), radius: u64, gap: u64) -> (u64, u64) {
    let (dx, dy) = (champ.0 as f64 - me.0 as f64, champ.1 as f64 - me.1 as f64);
    let d = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if d < 1.0 { (1.0, 0.0) } else { (dx / d, dy / d) };
    let off = (radius + gap) as f64;
    ((champ.0 as f64 + ux * off).max(0.0) as u64, (champ.1 as f64 + uy * off).max(0.0) as u64)
}

/// A unit inside a pillar is put on its edge, straight out from its centre (from the side Trundle is on when it stands
/// on the very centre: away from where he stood).
pub fn push_out(centre: (u64, u64), at: (u64, u64), radius: u64) -> Option<(u64, u64)> {
    if dist2(centre, at) >= radius.saturating_mul(radius) {
        return None;
    }
    let (dx, dy) = (at.0 as f64 - centre.0 as f64, at.1 as f64 - centre.1 as f64);
    let d = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if d < 1.0 { (1.0, 0.0) } else { (dx / d, dy / d) };
    let r = radius as f64 + 1.0;
    Some(((centre.0 as f64 + ux * r).max(0.0) as u64, (centre.1 as f64 + uy * r).max(0.0) as u64))
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// What a buff on him or a unit holds (a stat change on top of the base).
fn stat_buff(name: &str, ticks: usize, f: impl FnOnce(&mut BuffV1)) -> BuffV1 {
    let mut b = BuffV1::timed(name, ticks);
    f(&mut b);
    b
}

// ===================== 被动 =====================

/// One Subjugate: whom, when it started, the next drain tick.
#[derive(Clone, Debug)]
struct Drain {
    id: usize,
    start: usize,
    next: usize,
}

/// 每个特朗德尔一份：参数、冰面、冰柱、吸取，和日志计数。
#[derive(Clone, Default)]
struct Troll {
    p: Params,
    /// The domain's centre while `w_on` lasts, and `w_on`'s remaining ticks last tick (a renewal = a new domain).
    domain: Option<(u64, u64)>,
    w_left: usize,
    /// His health at the end of last tick (the domain's heal amplifier reads the rise).
    last_hp: usize,
    /// Enemy units near him last tick: (id, max health).
    near: Vec<(usize, usize)>,
    /// Standing pillars: (centre, the tick it falls).
    pillars: Vec<((u64, u64), usize)>,
    drains: Vec<Drain>,
    n_tribute: usize,
    n_domain: usize,
    n_pillar: usize,
    n_push: usize,
    n_chomp: usize,
    n_drain: usize,
}

impl Troll {
    fn on_domain(&self, sim: &StableSim<'_>, me: usize) -> bool {
        let (Some(c), Some(e)) = (self.domain, sim.get_entity(me)) else { return false };
        dist2(c, e.pos()) <= self.p.w_r.saturating_mul(self.p.w_r)
    }

    /// A heal on him (amplified on the domain), counted into last_hp so the amplifier does not take it twice.
    fn heal_me(&mut self, sim: &mut StableSim<'_>, me: usize, amount: usize, on_domain: bool) -> usize {
        let h = amped(amount, on_domain, self.p.w_amp);
        if h > 0 {
            sim.heal(me, me, h);
        }
        h
    }

    /// Frozen Domain: where `w_on` appeared (or was renewed) it stays; inside it the stats and the heal amplifier.
    fn domain(&mut self, sim: &mut StableSim<'_>, me: usize) -> bool {
        let Some(e) = sim.get_entity(me) else { return false };
        let left = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == W_ON).map(|b| b.duration_tick);
        let pos = e.pos();
        match left {
            None => {
                self.domain = None;
                self.w_left = 0;
            }
            Some(l) => {
                if self.domain.is_none() || l > self.w_left {
                    self.domain = Some(pos);
                    self.n_domain += 1;
                    if often(self.n_domain) {
                        wlog(format!("{} DOMAIN frozen at ({}, {}) for {l} ticks ({} in all)", head(sim, me), pos.0, pos.1,
                                     self.n_domain));
                    }
                }
                self.w_left = l;
            }
        }
        let inside = self.on_domain(sim, me);
        if inside {
            let (a, m, r) = (self.p.w_as as i32, self.p.w_ms as i32, self.p.w_regen as i32);
            sim.entity_remove_buff(me, W_IN);
            sim.add_buff(me, &stat_buff(W_IN, 2, |b| {
                b.attack_speed_mult = a;
                b.move_speed_mult = m;
                b.hp_regen = r;
            }));
        }
        inside
    }

    /// The enemy units around him: King's Tribute for those that fell since last tick, Chomp's steal on the bitten.
    fn around(&mut self, sim: &mut StableSim<'_>, me: usize, inside: bool) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, at, attack) = (e.team(), e.pos(), e.stat().attack);
        for (id, max_hp) in std::mem::take(&mut self.near) {
            if sim.get_entity(id).is_some_and(|u| u.is_alive()) {
                continue;
            }
            let h = tribute(&self.p, max_hp, inside);
            let h = if h > 0 { sim.heal(me, me, h); h } else { 0 };
            self.n_tribute += 1;
            if often(self.n_tribute) {
                wlog(format!("{} TRIBUTE {} fell near him: +{h}{} ({} in all)", head(sim, me), name_of(sim, id),
                             if inside { " (on the domain)" } else { "" }, self.n_tribute));
            }
        }
        let r2 = self.p.p_r.saturating_mul(self.p.p_r);
        let mut bitten = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() {
                continue;
            }
            match u.kind() {
                Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Epic
                     | EntityKindV1::Summon) => {}
                _ => continue,
            }
            if dist2(at, u.pos()) <= r2 {
                self.near.push((u.id(), u.hp().1));
            }
            if has(&u, Q_MARK) {
                bitten.push((u.id(), u.stat().attack));
            }
        }
        for (id, its_attack) in bitten {
            sim.entity_remove_buff(id, Q_MARK);
            let (gain, loss) = chomp(&self.p, its_attack);
            sim.entity_remove_buff(me, Q_TAKE);
            sim.add_buff(me, &stat_buff(Q_TAKE, self.p.q_t, |b| b.attack = gain));
            sim.entity_remove_buff(id, Q_LOSE);
            sim.add_buff(id, &stat_buff(Q_LOSE, self.p.q_t, |b| b.attack = -loss));
            self.n_chomp += 1;
            if often(self.n_chomp) {
                wlog(format!("{} CHOMP {} (attack {its_attack}): him +{gain} (attack {attack}), it -{loss} ({} in all)",
                             head(sim, me), name_of(sim, id), self.n_chomp));
            }
        }
    }

    /// Pillar of Ice: a pillar behind each champion marked at one; enemies are kept out of the standing pillars.
    fn pillars(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, at) = (e.team(), e.pos());
        let marked: Vec<(usize, (u64, u64))> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| sim.get_entity(id).filter(|c| c.team() != team && has(c, E_AT)).map(|c| (id, c.pos())))
            .collect();
        let mut risen = false;
        for (id, pos) in marked {
            sim.entity_remove_buff(id, E_AT);
            if risen {
                continue;   // one pillar a cast: the first champion marked sets it
            }
            risen = true;
            let spot = pillar_spot(at, pos, self.p.e_wall, PILLAR_GAP);
            self.pillars.push((spot, tick + self.p.e_t));
            self.n_pillar += 1;
            if often(self.n_pillar) {
                wlog(format!("{} PILLAR behind {} at ({}, {}) for {} ticks ({} in all)", head(sim, me), name_of(sim, id),
                             spot.0, spot.1, self.p.e_t, self.n_pillar));
            }
        }
        self.pillars.retain(|&(_, until)| tick < until);
        if self.pillars.is_empty() {
            return;
        }
        let mut moves = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || !matches!(u.kind(), Some(EntityKindV1::Champion | EntityKindV1::Minion)) {
                continue;
            }
            let mut p = u.pos();
            let mut moved = false;
            for &(c, _) in &self.pillars {
                if let Some(q) = push_out(c, p, self.p.e_wall) {
                    p = q;
                    moved = true;
                }
            }
            if moved {
                moves.push((u.id(), p));
            }
        }
        for (id, (x, y)) in moves {
            sim.entity_set_pos(id, x, y);
            self.n_push += 1;
            if self.n_push <= 20 || self.n_push % 500 == 0 {
                wlog(format!("{} WALL {} kept out of a pillar ({} pushes)", head(sim, me), name_of(sim, id), self.n_push));
            }
        }
    }

    /// One drain of Subjugate: pct% of the champion's maximum health as magic damage; he heals what it lost.
    fn drain_once(&mut self, sim: &mut StableSim<'_>, me: usize, id: usize, pct: usize, inside: bool) -> (usize, usize) {
        let Some(c) = sim.get_entity(id) else { return (0, 0) };
        let (hp0, max) = c.hp();
        sim.deal_damage_typed(me, id, share(max, pct), DamageTypeV1::Ap, AttackTypeV1::Skill);
        let hp1 = sim.get_entity(id).map_or(0, |c| c.hp().0);
        let lost = hp0.saturating_sub(hp1);
        let healed = self.heal_me(sim, me, lost, inside);
        (lost, healed)
    }

    /// Subjugate: a new `r_drain` steals the champion's own defence and magic resistance and drains it at once, then
    /// every r_p ticks for r_t.
    fn subjugate(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize, inside: bool) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let fresh: Vec<(usize, StatV1)> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter(|id| !self.drains.iter().any(|d| d.id == *id))
            .filter_map(|id| sim.get_entity(id).filter(|c| c.team() != team && c.is_alive() && has(c, R_DRAIN))
                .map(|c| (id, c.stat())))
            .collect();
        for (id, st) in fresh {
            let (d, m) = (share(st.defence, self.p.r_steal) as i32, share(st.magic_resistance, self.p.r_steal) as i32);
            let keep = self.p.r_t + self.p.r_keep;
            sim.entity_remove_buff(id, R_LOSE);
            sim.add_buff(id, &stat_buff(R_LOSE, keep, |b| {
                b.defence = -d;
                b.magic_resistance = -m;
            }));
            sim.entity_remove_buff(me, R_TAKE);
            sim.add_buff(me, &stat_buff(R_TAKE, keep, |b| {
                b.defence = d;
                b.magic_resistance = m;
            }));
            let (lost, healed) = self.drain_once(sim, me, id, self.p.r_pct0, inside);
            self.drains.push(Drain { id, start: tick, next: tick + self.p.r_p });
            self.n_drain += 1;
            if often(self.n_drain) {
                wlog(format!("{} SUBJUGATE {}: stole {d} defence / {m} magic resistance, drained {lost} (+{healed}) ({} in all)",
                             head(sim, me), name_of(sim, id), self.n_drain));
            }
        }
        let mut done = Vec::new();
        for k in 0..self.drains.len() {
            let Drain { id, start, next } = self.drains[k].clone();
            let alive = sim.get_entity(id).is_some_and(|c| c.is_alive() && has(&c, R_DRAIN));
            if !alive && tick > start + self.p.r_t {
                done.push(k);
                continue;
            }
            if alive && tick >= next && next <= start + self.p.r_t {
                self.drain_once(sim, me, id, self.p.r_pct, inside);
                self.drains[k].next = next + self.p.r_p;
            }
        }
        for k in done.into_iter().rev() {
            self.drains.remove(k);
        }
    }
}

impl StablePassive for Troll {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        self.domain = None;
        self.w_left = 0;
        self.near.clear();
        self.drains.clear();
        self.last_hp = sim.get_entity(me).map_or(0, |e| e.hp().0);
        wlog(format!("{} SPAWN: the add-on's Trundle (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        // the pillars stand on while he is dead (terrain)
        self.pillars(sim, me, tick);
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.domain = None;
            self.w_left = 0;
            self.near.clear();
            self.last_hp = 0;
            return;
        }
        let inside = self.domain(sim, me);
        // the domain's amplifier: every heal he got since last tick (a rise of his health) w_amp% bigger
        let hp = sim.get_entity(me).map_or(0, |e| e.hp().0);
        if inside && self.last_hp > 0 && hp > self.last_hp {
            let extra = (hp - self.last_hp) * self.p.w_amp / 100;
            if extra > 0 {
                sim.heal(me, me, extra);
            }
        }
        self.around(sim, me, inside);
        self.subjugate(sim, me, tick, inside);
        self.last_hp = sim.get_entity(me).map_or(0, |e| e.hp().0);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (King's Tribute, a fixed domain, terrain pillars, League's Chomp and Subjugate) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:troll"), Troll::default());
    host.log(LogLevel::Info, "league_trundle loaded (King's Tribute, a fixed domain, terrain pillars, League's Chomp and Subjugate).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"e_wall":12000,"p_pct":7,"r_steal":30,"x":1}"#);
        assert_eq!((p.e_wall, p.p_pct, p.r_steal), (12000, 7, 30));
        assert_eq!(p.w_r, Params::default().w_r);
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_tribute_is_a_share_of_the_fallen_and_doubles_on_the_domain() {
        let p = Params::default();
        assert_eq!(tribute(&p, 2000, false), 100);
        assert_eq!(tribute(&p, 2000, true), 250);   // x2, then +25%
        assert_eq!(tribute(&p, 10, false), 1);
        assert_eq!(tribute(&p, 0, false), 0);
    }

    #[test]
    fn chomp_takes_a_share_and_the_bitten_loses_half() {
        let p = Params::default();
        assert_eq!(chomp(&p, 100), (20, 10));
        assert_eq!(chomp(&p, 3), (1, 1));
        assert_eq!(chomp(&p, 0), (0, 0));
    }

    #[test]
    fn a_pillar_rises_behind_its_champion() {
        // Trundle at x 0, the champion at x 20000: the pillar's centre further right, its edge 3000 past the champion
        assert_eq!(pillar_spot((0, 50000), (20000, 50000), 9000, 3000), (32000, 50000));
        assert_eq!(pillar_spot((20000, 50000), (20000, 50000), 9000, 3000), (32000, 50000));   // on the spot: to the right
    }

    #[test]
    fn units_are_kept_out_of_a_pillar() {
        assert_eq!(push_out((50000, 50000), (52000, 50000), 9000), Some((59001, 50000)));
        assert_eq!(push_out((50000, 50000), (60000, 50000), 9000), None);
        assert_eq!(push_out((50000, 50000), (50000, 50000), 9000), Some((59001, 50000)));
    }

    #[test]
    fn the_domain_amplifies_heals() {
        assert_eq!(amped(100, true, 25), 125);
        assert_eq!(amped(100, false, 25), 100);
    }

    #[test]
    fn names_are_the_data_s() {
        for n in [W_ON, W_IN, E_AT, Q_MARK, Q_TAKE, Q_LOSE, R_DRAIN, R_TAKE, R_LOSE] {
            assert!(n.starts_with("league_trundle_"), "{n}");
        }
    }
}
