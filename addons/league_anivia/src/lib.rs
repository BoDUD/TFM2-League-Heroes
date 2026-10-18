//! 艾尼维亚扩展包（用户选：「主包不做蛋，寒霜涅槃只放在扩展包里」「冰墙我要的是真的墙 可以卡住人的那种」）：主包数据做不到的三件事。
//!
//! `mod.override_info` 把主包的艾尼维亚换成 `override/` 里的副本（tools/kit/build_anivia.py 的 native=1）：数据和主包一样，只是
//! 被动挂本包的 `league_anivia:rebirth`，冰墙没有主包那圈 99% 减速（本包让墙真的挡路），E 不再用主包「被控 / 风暴成形」的近似翻倍。
//!
//! - **寒霜涅槃**：每 `egg_cd` tick 一次（阵亡不重置），受到致命伤害时不倒下（本包一直挂着「不死」`league_anivia_p_guard`，
//!   生命停在 1 就触发），变成冰蛋 `egg_t` tick：生命回满当作蛋的生命，禁普攻、禁技能；主包数据看到 `league_anivia_egg_go`
//!   播缩进蛋里的动作、挂双抗降低的 `league_anivia_egg_on`、每 30 tick 续一次蛋的动作。蛋被打碎就是她阵亡（击杀算打碎蛋的人）；
//!   撑过 `egg_t` tick 就挂 `league_anivia_egg_hatch`，数据播孵化，她带着蛋剩下的生命继续打（英雄联盟一样）。
//!   别人给的「不死」在身上时不触发。
//! - **真冰墙**：数据在 Q 晕到英雄 2 tick 后立墙（她身上新出现 `league_anivia_w_cd`），墙心就是那一 tick 她新放出、不在她脚下的
//!   区域的位置（投射物信息里没有名字，只有位置）。之后 `w_t` tick 里，每个单位（英雄、小兵、野怪，两边都算，她自己也算）的中心
//!   一进墙（竖着的长方形，半宽 `w_w`/2 + 单位半径，半高 `w_h`/2 + 单位半径）就放回上一 tick 的位置；立墙时站在墙上的被推到她那一侧（和主包数据的拖出一样：墙在被晕的人身后）。
//! - **冰冻翻倍**：数据给 Q 打中、成形风暴打中的英雄挂 `league_anivia_iced`（`ice_t` tick）；E 打中时她身上亮 1 tick 的
//!   `league_anivia_e_now`，本包在 `on_attack` 里看到它、目标身上又有冰冻，就把这一下伤害翻倍。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_anivia.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[cfg(windows)]
pub mod view;

/// 主包数据的蛋 buff（双抗降低，蛋在就有）：显示钩子按它把 idle / hit 换成蛋。
pub const FORM: &str = "league_anivia_egg_on";

const ID: &str = "league_anivia";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.3";

/// 「不死」挂多久、多久续一次。
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;
/// 主包数据读标记的余量：数据的蛋监视每 2 tick 看一次。
pub const FLAG_T: usize = 6;
/// 单位半径读不到时用的值。
pub const BODY: u64 = 6000;
/// 立墙那一 tick 她脚下这么近的新投射物不算墙（普攻、E 从她身上出发）。0.1.0 是 25000：被晕的近战英雄贴着她时，
/// 墙也被当成她脚下的东西丢掉。
pub const NEAR_ME: u64 = 3000;
/// `w_cd` 出现后最多再找这么多 tick 的墙心。
pub const WALL_LOOK: usize = 3;

fn sn(x: &str) -> String {
    format!("league_anivia_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ANIVIA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_anivia.log");
        }
    }
    PathBuf::from("league_anivia.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub egg_t: usize,
    pub egg_cd: usize,
    pub w_t: usize,
    pub w_w: u64,
    pub w_h: u64,
    pub ice_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { egg_t: 360, egg_cd: 14400, w_t: 300, w_w: 8000, w_h: 50000, ice_t: 180 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        match k {
            "egg_t" => p.egg_t = v as usize,
            "egg_cd" => p.egg_cd = v as usize,
            "w_t" => p.w_t = v as usize,
            "w_w" => p.w_w = v,
            "w_h" => p.w_h = v,
            "ice_t" => p.ice_t = v as usize,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 一面墙：中心、立起的 tick、她在哪一侧。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Wall {
    pub x: u64,
    pub y: u64,
    pub from: usize,
    /// 立墙时她在墙的左边（x 小的一侧）：墙上的单位推到这一侧。
    pub left: bool,
}

/// 单位中心在墙里（竖着的长方形，四边各加单位半径）。
pub fn inside(w: &Wall, p: &Params, x: u64, y: u64, r: u64) -> bool {
    x.abs_diff(w.x) < p.w_w / 2 + r && y.abs_diff(w.y) < p.w_h / 2 + r
}

/// 墙里的单位推到她那一侧（只改 x：墙是竖的）。
pub fn push_out(w: &Wall, p: &Params, r: u64) -> u64 {
    let edge = p.w_w / 2 + r + 1;
    if w.left { w.x.saturating_sub(edge) } else { w.x + edge }
}

/// 这一 tick 单位该在哪：进了墙就回到上一 tick 的位置（上一 tick 也在墙里，就推出去）。
pub fn hold(walls: &[Wall], p: &Params, last: Option<(u64, u64)>, now: (u64, u64), r: u64) -> Option<(u64, u64)> {
    let w = walls.iter().find(|w| inside(w, p, now.0, now.1, r))?;
    match last {
        Some(l) if !inside(w, p, l.0, l.1, r) => Some(l),
        _ => Some((push_out(w, p, r), now.1)),
    }
}

/// 立墙那一 tick 的墙心：她的投射物按位置（200 以内算一处）数个数，比上一 tick 多出来的那些位置里（离她 `NEAR_ME`
/// 以外），多出来最多的；一样多取离她远的。0.1.0 只认「上一 tick 那里一个都没有」的位置，可墙立在 Q 的炸点上，
/// 炸点上一 tick 就有 Q 挂的延时（2 tick 后立墙的那个），墙的两个区域就被当成旧的：游戏日志里六成的墙没立起来
/// （`WALL?` 约 950 次，`WALL` 约 550 次）。0.1.3：`prev` 是 `w_cd` 出现前一 tick 的，`now` 可以是之后 `WALL_LOOK` tick 里的
/// 任何一 tick（0.1.2 只在 `w_cd` 出现那一 tick 找，还有约三分之一没找到：区域可能晚一 tick 才列出来）；多出来的位置里
/// 只认至少两个叠在一处的（墙的 `w_out` 和 `w_mark` 一起出现；普攻、冰锥只有一个，墙还没列出来时不会被当成墙），
/// 先取那里投射物最多的，再取多出来最多的，再取离她远的。
pub fn wall_centre(prev: &[(u64, u64)], now: &[(u64, u64)], me: (u64, u64)) -> Option<(u64, u64)> {
    let near = |a: (u64, u64), b: (u64, u64)| a.0.abs_diff(b.0) < 200 && a.1.abs_diff(b.1) < 200;
    let from_me = |q: (u64, u64)| q.0.abs_diff(me.0).max(q.1.abs_diff(me.1));
    let mut best: Option<((u64, u64), (usize, usize, u64))> = None;
    for &q in now.iter().filter(|&&q| from_me(q) > NEAR_ME) {
        let more = now.iter().filter(|&&o| near(o, q)).count();
        let before = prev.iter().filter(|&&o| near(o, q)).count();
        if more <= before || more < 2 {
            continue;
        }
        let key = (more, more - before, from_me(q));
        if best.is_none_or(|(_, b)| key > b) {
            best = Some((q, key));
        }
    }
    best.map(|(q, _)| q)
}

/// 名字是不是本包的「不死」（别的「不死」在身上时不触发蛋）。
pub fn ours(name: &str) -> bool {
    name == sn("p_guard")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buffs(sim, id).iter().any(|b| b.name() == name)
}

#[derive(Clone, Default)]
struct Rebirth {
    p: Params,
    me: usize,
    /// 蛋下一次能用的 tick（跨命保留）。
    egg_ready_at: usize,
    /// 蛋开始的 tick（不在蛋里时 None）。
    egg: Option<usize>,
    next_guard: usize,
    /// 这条命里见过她 1 血以上（0.6.4 开局第 0 tick 读到的血量是 0，那不是致命伤）。
    alive_seen: bool,
    /// 上一 tick 她身上有没有 `w_cd`、她的投射物在哪。
    had_w_cd: bool,
    prev_proj: Vec<(u64, u64)>,
    /// `w_cd` 刚出现、墙心还没找到：出现的 tick 和那之前一 tick 她的投射物。
    rising: Option<(usize, Vec<(u64, u64)>)>,
    walls: Vec<Wall>,
    /// 墙立着时每个单位上一 tick 的位置。
    last_pos: HashMap<usize, (u64, u64)>,
}

impl Rebirth {
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

    fn curl(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        self.egg = Some(now);
        self.egg_ready_at = now + self.p.egg_cd;
        sim.entity_remove_buff(me, &sn("p_guard"));
        sim.entity_set_hp(me, max);
        sim.add_buff(me, &BuffV1::timed(&sn("egg_go"), FLAG_T));
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockSkill, self.p.egg_t as u64));
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockAttack, self.p.egg_t as u64));
        if let Some(k) = counted("egg") {
            wlog(format!("{} EGG #{k}: lethal damage caught at 1 hp, the egg holds {max} hp for {} ticks", head(sim, me),
                         self.p.egg_t));
        }
    }

    fn hatch(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.egg = None;
        sim.add_buff(me, &BuffV1::timed(&sn("egg_hatch"), FLAG_T));
        if let Some(k) = counted("hatch") {
            let (hp, max) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
            wlog(format!("{} HATCH #{k}: reborn with the egg's {hp} / {max} hp", head(sim, me)));
        }
    }

    /// 新立的墙：`w_cd` 刚出现的这一 tick，她新放出的区域的位置。
    fn watch_walls(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let mine: Vec<(u64, u64)> = (0..sim.projectile_count())
            .filter_map(|i| sim.projectile_at(i))
            .filter(|q| q.caster_id == me && !q.is_end)
            .map(|q| (q.x, q.y))
            .collect();
        let w_cd = has(sim, me, &sn("w_cd"));
        if w_cd && !self.had_w_cd {
            self.rising = Some((now, self.prev_proj.clone()));
        }
        if let Some((from, base)) = self.rising.take() {
            let me_pos = sim.get_entity(me).map_or((0, 0), |e| e.pos());
            match wall_centre(&base, &mine, me_pos) {
                Some((x, y)) => {
                    self.walls.push(Wall { x, y, from, left: me_pos.0 < x });
                    if let Some(k) = counted("wall") {
                        wlog(format!("{} WALL #{k}: at ({x}, {y}), {} ticks (found {} tick(s) after w_cd)",
                                     head(sim, me), self.p.w_t, now - from));
                    }
                }
                None if now >= from + WALL_LOOK => {
                    if let Some(k) = counted("wall_lost") {
                        wlog(format!("{} WALL? #{k}: w_cd rose at t={from} but no new zone of hers in {WALL_LOOK} ticks                                       ({} of her projectiles before, {} now)", head(sim, me), base.len(), mine.len()));
                    }
                }
                None => self.rising = Some((from, base)),
            }
        }
        self.had_w_cd = w_cd;
        self.prev_proj = mine;
    }

    /// 墙立着时：每个单位进墙就放回去。
    fn block(&mut self, sim: &mut StableSim<'_>, now: usize) {
        let w_t = self.p.w_t;
        self.walls.retain(|w| now < w.from + w_t);
        if self.walls.is_empty() {
            self.last_pos.clear();
            return;
        }
        let mut moves = Vec::new();
        let mut seen = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() {
                continue;
            }
            match e.kind() {
                Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Summon) => {}
                _ => continue,
            }
            let id = e.id();
            let now_pos = e.pos();
            let r = match e.radius() as u64 { 0 => BODY, r => r };
            let last = self.last_pos.get(&id).copied();
            let at = match hold(&self.walls, &self.p, last, now_pos, r) {
                Some(q) => {
                    moves.push((id, q, last.is_some()));
                    q
                }
                None => now_pos,
            };
            seen.insert(id, at);
        }
        for (id, (x, y), was) in moves {
            sim.entity_set_pos(id, x, y);
            if let Some(k) = counted(if was { "hold" } else { "push" }) {
                wlog(format!("{} {} #{k}: {} kept out of the wall at ({x}, {y})", head(sim, self.me),
                             if was { "HOLD" } else { "PUSH" }, who(sim, id)));
            }
        }
        self.last_pos = seen;
    }
}

impl StablePassive for Rebirth {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.egg = None;
        self.next_guard = 0;
        self.alive_seen = false;
        self.had_w_cd = false;
        self.prev_proj.clear();
        self.rising = None;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Anivia (player {player}, team {team}), {:?}, egg ready at t={}",
                         head(sim, me), self.p, self.egg_ready_at));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        if alive {
            self.watch_walls(sim, me, now);
        }
        self.block(sim, now);
        if !alive {
            return;
        }
        let (hp, _) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        if let Some(t0) = self.egg {
            if now >= t0 + self.p.egg_t {
                self.hatch(sim, me);
            }
            return;
        }
        if hp > 1 {
            self.alive_seen = true;
        }
        if now < self.egg_ready_at {
            return;
        }
        self.guard(sim, me, now);
        if hp <= 1 && self.alive_seen {
            let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
            if !other_undying(&list) {
                self.curl(sim, me, now);
            }
        }
    }

    /// E 的一下打在带冰冻的英雄身上：翻倍。
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if *damage == 0 || !has(sim, me, &sn("e_now")) || !has(sim, target, &sn("iced")) {
            return;
        }
        *damage *= 2;
        if let Some(k) = counted("iced") {
            wlog(format!("{} ICED #{k}: Frostbite doubled on {} ({})", head(sim, me), who(sim, target), *damage));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        if self.egg.take().is_some() {
            if let Some(k) = counted("broken") {
                wlog(format!("{} BROKEN #{k}: the egg was broken - she is dead", head(sim, self.me)));
            }
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Anivia: Rebirth's egg, a real Crystallize wall, Frostbite doubled on Iced) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:rebirth"), Rebirth::default());
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "league_anivia loaded (Rebirth's egg, a real wall, Frostbite on Iced).");
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

    fn p() -> Params {
        Params::default()
    }

    #[test]
    fn params_from_the_kit() {
        let q = parse_params(r#"{"egg_cd":14400,"egg_t":360,"ice_t":180,"w_h":50000,"w_t":300,"w_w":8000}"#);
        assert_eq!(q, Params::default());
    }

    #[test]
    fn a_unit_walking_into_the_wall_goes_back() {
        let w = [Wall { x: 500000, y: 400000, from: 0, left: true }];
        // from the left: last tick outside, now inside -> back to last
        assert_eq!(hold(&w, &p(), Some((488000, 400000)), (491000, 400000), 6000), Some((488000, 400000)));
        // from the right the same
        assert_eq!(hold(&w, &p(), Some((512000, 410000)), (509000, 410000), 6000), Some((512000, 410000)));
        // past the wall's end: free
        assert_eq!(hold(&w, &p(), Some((495000, 440000)), (500000, 440000), 6000), None);
    }

    #[test]
    fn on_the_wall_when_it_rises_pushed_to_her_side() {
        // she stands left of the wall: both out to the left, wherever they stood on it
        let w = [Wall { x: 500000, y: 400000, from: 0, left: true }];
        assert_eq!(hold(&w, &p(), None, (498000, 400000), 6000), Some((500000 - 10001, 400000)));
        assert_eq!(hold(&w, &p(), None, (503000, 400000), 6000), Some((500000 - 10001, 400000)));
        // she stands right of it: out to the right
        let w = [Wall { x: 500000, y: 400000, from: 0, left: false }];
        assert_eq!(hold(&w, &p(), None, (498000, 400000), 6000), Some((500000 + 10001, 400000)));
    }

    #[test]
    fn the_wall_is_the_new_zone_away_from_her() {
        let me = (300000, 400000);
        let prev = [(350000, 400000), (300500, 400000)];
        // a fresh bolt at her feet, the wall's two zones at the blast point, the old Q ball moved on
        let now = [(301000, 400000), (420000, 395000), (420000, 395000), (351600, 400000)];
        assert_eq!(wall_centre(&prev, &now, me), Some((420000, 395000)));
        assert_eq!(wall_centre(&prev, &[(301000, 400000)], me), None);
    }

    #[test]
    fn the_wall_on_the_blast_point_the_delay_stood_on() {
        // the tick before: Q's 2-tick delay stands on the blast point; now it is gone and the wall's two zones are there
        let me = (300000, 400000);
        let prev = [(420000, 395000)];
        let now = [(420000, 395000), (420000, 395000)];
        assert_eq!(wall_centre(&prev, &now, me), Some((420000, 395000)));
        // the delay still listed this tick too: one more than before is enough
        let now = [(420000, 395000), (420000, 395000), (420000, 395000)];
        assert_eq!(wall_centre(&prev, &now, me), Some((420000, 395000)));
        // a stunned melee champion right next to her: the wall 15000 away still counts, a new bolt at her feet loses
        let prev = [(315000, 400000)];
        let now = [(301000, 400000), (315000, 400000), (315000, 400000)];
        assert_eq!(wall_centre(&prev, &now, me), Some((315000, 400000)));
        // nothing new: no wall
        assert_eq!(wall_centre(&prev, &[(315000, 400000)], me), None);
    }

    #[test]
    fn a_tick_later_the_wall_beats_a_new_bolt() {
        // the snapshot before w_cd rose; a tick later the wall's two zones and a bolt already flying away from her
        let me = (300000, 400000);
        let prev = [(420000, 395000)];
        let now = [(470000, 400000), (420000, 395000), (420000, 395000)];
        assert_eq!(wall_centre(&prev, &now, me), Some((420000, 395000)));
        // the zones not listed yet, only the bolt new: no wall yet (look again next tick)
        assert_eq!(wall_centre(&prev, &[(470000, 400000)], me), None);
    }

    #[test]
    fn only_someone_elses_undying_holds_the_egg_back() {
        assert!(!other_undying(&[("league_anivia_p_guard".to_string(), true)]));
        assert!(other_undying(&[("league_zilean_r_rune".to_string(), true)]));
    }
}
