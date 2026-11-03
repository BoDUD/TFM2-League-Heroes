//! 卡尔萨斯附加包（用户选「被动做附加包」）：主包数据做不到的死亡契约。
//!
//! `mod.override_info` 把主包的卡尔萨斯换成 `override/` 里的副本（tools/kit/build_karthus.py 的 native=1）：数据和主包
//! 一样，只是被动挂本包的 `league_karthus:death_defied`（参数在英雄数据的 `passive.params` 里），多一个灵体的画面。
//!
//! - **死亡契约**：英雄联盟里卡尔萨斯死后化成灵体，7 秒内照样放技能，然后才倒下；灵体选不中、不受伤害、免控，不能走动、
//!   不能普攻。数据读不到血量，主包做不了。本包一直给他挂着「不死」`league_karthus_p_guard`，致命伤害只会把他打到 1 血；
//!   到 1 血（身上没有别人给的不死）时**化成灵体** `p_t` tick。
//! - **灵体照英雄联盟**（0.5.0，用户 2026-11-03：「死了灵体还能移动 还能有残血？」「这能和英雄联盟一样吗」「还有死了后为什么
//!   AI还攻击灵体 很奇怪啊」）：0.4.x 的灵体是 1 血、活着的他——游戏只认放逐是选不中，它只放了开头 12 tick：之后小兵、塔照打
//!   （1 血的英雄正是 AI 最想补的），挨每个英雄的钩子 `shun` 拦下的出手也照样飞来，头上挂着一条残血，移速 −100% 也挡不住位移。
//!   现在**整个灵体放逐着**（`entity_banish` `p_t` tick，扎亨复活的做法）：谁都选不中、打不到，没有血条，不能走、不能回城；
//!   放逐的锁定画面是他的灵体（`league_karthus_p_ghost_r` / `_l`，`tools/art/draw_karthus_ghost.py`，面朝最近的敌方英雄），
//!   每 tick 钉在倒下的地方。放逐也锁住他自己出手，所以**灵体的技能由本包放**（`spirit_casts`，数字、画面照主包）：亵渎一直
//!   烧（每 `E_PER` tick 圈里每个敌人），荒芜每 `Q_CD` tick 落在射程里最近的敌方英雄（没有就别的单位）脚下（`Q_DELAY` tick 后
//!   炸开，只炸到一个两倍），安魂曲好了又值得（`r_worth`）时引导 `R_CH` tick 打每个敌方英雄。击杀照样算他的。
//! - **灵体就是已经死了**（0.4.1，用户 2026-11-03：「灵体死了还能回城的？？？」「灵体出现就代表已经是死亡了 懂吗」「有时候
//!   死了又没灵体」）：不能回城，倒下后复活倒计时扣掉灵体待的时间（英雄联盟从化成灵体就开始算，`life.rs` 改游戏的剩余复活
//!   tick）。0.5.0：0.4.x 在 `on_dead` 里改，那时游戏还没把他记成阵亡（11-03 的日志全是 `RESPAWN NOT CUT (alive)`）；现在
//!   由 AI 钩子 `spirit_ai` 在他阵亡后的第一 tick 改。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_karthus.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_karthus";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_karthus") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 「不死」挂多久、多久续一次（一直挂着，化成灵体前不断）。
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;
/// 灵体倒下后，复活倒计时扣掉灵体待了的 tick，至少还剩这么多（`respawn_after_spirit`）。
pub const BACK_MIN: u64 = 60;
// 0.4.0 只在化成灵体时放逐他 12 tick（`FLUSH_T`，正在打他、追他的单位丢了目标）、之后免控（`p_ward`）：游戏里只有放逐让单位
// 选不中（tfm2-hero-mod 的 champion-data「Invisible is not untargetable」），放逐完小兵、塔、英雄又打上来。0.5.0 整个灵体放逐。

pub mod life;

fn sn(x: &str) -> String {
    format!("league_karthus_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KARTHUS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_karthus.log");
        }
    }
    PathBuf::from("league_karthus.log")
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

/// 名字是不是本包的「不死」（别的「不死」在身上时不化成灵体）。
pub fn ours(name: &str) -> bool {
    name == sn("p_guard") || name == sn("p_spirit")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

/// 倒下时剩的复活 tick `left` 扣掉灵体待了的 `spirit` tick，至少留 `BACK_MIN`（英雄联盟的死亡计时从化成灵体就开始）。
pub fn respawn_after_spirit(left: u64, spirit: u64) -> u64 {
    left.saturating_sub(spirit).max(BACK_MIN)
}

/// 游戏的 AI 是不是正在让他回城（league_graves 的写法）：下了回城命令，之后没有新命令时回城还在走，别的命令就停了。
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// 灵体挨的打（倒下时记日志，看钩子 `shun` 管不管用）：谁打的。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Hits {
    pub champions: usize,
    pub minions: usize,
    pub towers: usize,
    pub others: usize,
}

impl Hits {
    pub fn add(&mut self, kind: Option<EntityKindV1>) {
        match kind {
            Some(EntityKindV1::Champion) => self.champions += 1,
            Some(EntityKindV1::Minion) => self.minions += 1,
            Some(EntityKindV1::Tower) => self.towers += 1,
            _ => self.others += 1,
        }
    }
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_t: 420 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        if k == "p_t" {
            p.p_t = v;
        }
    }
    p
}

/// The player whose champion `id` is (None: a tower, a minion, a monster).
fn player_of(sim: &StableSim<'_>, id: usize) -> Option<usize> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find(|p| p.champion().is_some_and(|c| c.id() == id)).map(|p| p.id())
}

/// 灵体倒下时算谁的击杀：最后打他的还在就是他；他在灵体期间死了又复活（新的实体），算他玩家现在的英雄；都没有就算最近的
/// 活着的敌方英雄——从不算卡尔萨斯自己（0.4.2，league_sion 一样的毛病：11-02 的日志里赛恩 1/6 的倒下算成了自杀）。
fn killer(sim: &StableSim<'_>, me: usize, last: Option<usize>, player: Option<usize>) -> usize {
    if let Some(a) = last.filter(|&a| sim.get_entity(a).is_some()) {
        return a;
    }
    if let Some(c) = player.and_then(|p| sim.get_player(p)).and_then(|p| p.champion()).filter(|c| c.is_alive()) {
        return c.id();
    }
    let Some(e) = sim.get_entity(me) else { return me };
    let (team, here) = (e.team(), e.pos());
    let d2 = |p: (u64, u64)| (p.0 as f64 - here.0 as f64).powi(2) + (p.1 as f64 - here.1 as f64).powi(2);
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_champion() && u.is_alive())
        .min_by(|a, b| d2(a.pos()).total_cmp(&d2(b.pos())))
        .map_or(me, |u| u.id())
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

/// 灵体的 buff（副本里绑着灵体的画面）：不死、不受伤害、不能走动（英雄联盟的灵体站在原地放技能）。
fn spirit_buff(t: usize) -> BuffV1 {
    let mut s = BuffV1::timed(&sn("p_spirit"), t);
    s.undying = true;
    s.damaged_reduce = 100;
    s.move_speed_mult = -100;
    s
}

/// 灵体由本包放的技能（他放逐着自己出不了手）：钉住的位置，下一次荒芜、亵渎、亵渎圈画面的 tick，落下的荒芜（位置、炸开的
/// tick），安魂曲打下来的 tick，这个灵体放过安魂曲没有。
#[derive(Clone, Default)]
struct Cast {
    anchor: (u64, u64),
    q_next: usize,
    e_next: usize,
    ring_next: usize,
    booms: Vec<((u64, u64), usize)>,
    requiem: Option<usize>,
    r_used: bool,
}

/// 灵体的画面面朝哪边（效果图不会镜像，左右各画一张）：最近的敌方英雄在右边（或没有）就朝右。
pub fn side(me_x: u64, foe_x: Option<u64>) -> &'static str {
    match foe_x {
        Some(x) if x < me_x => "l",
        _ => "r",
    }
}

/// 单位的种类（读不到时按英雄、小兵、塔的判断）。
fn kind_of(e: &StableEntity<'_, '_>) -> Option<EntityKindV1> {
    e.kind().or_else(|| {
        if e.is_champion() {
            Some(EntityKindV1::Champion)
        } else if e.is_minion() {
            Some(EntityKindV1::Minion)
        } else if e.is_tower() {
            Some(EntityKindV1::Tower)
        } else {
            None
        }
    })
}

#[derive(Clone, Default)]
struct DeathDefied {
    p: Params,
    me: usize,
    /// 灵体开始的 tick（不是灵体时 None）。
    spirit: Option<usize>,
    /// 这条命还没化过灵体。
    ready: bool,
    /// 最后一个打他的（倒下时算击杀）。
    last_hit: Option<usize>,
    /// 最后一个打他的英雄的玩家：那个英雄在灵体期间死了又复活（新的实体），击杀算他的新英雄（`killer`）。
    last_player: Option<usize>,
    next_guard: usize,
    /// 这条命里见过他 1 血以上：游戏 0.6.4 开局第 0 tick 读到的血量是 0，那不是致命伤（赛恩附加包的教训）。
    alive_seen: bool,
    /// 这次灵体挨的打。
    hits: Hits,
    /// 灵体由本包放的技能。
    cast: Cast,
}

impl DeathDefied {
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
        self.ready = false;
        self.spirit = Some(now);
        self.hits = Hits::default();
        sim.entity_remove_buff(me, &sn("p_guard"));
        let Some((pos, team)) = sim.get_entity(me).map(|e| (e.pos(), e.team())) else { return };
        let nearest = foes_by_distance(sim, team, (pos.0 as f64, pos.1 as f64)).first().and_then(|f| sim.get_entity(f.0));
        let face = side(pos.0, nearest.map(|e| e.pos().0));
        // the whole spirit banished (0.5.0): untargetable for everyone, no health bar, rooted, recall-proof; the banish's
        // lock picture is his ghost where he fell (league_zaahen's revive) - before anything cc_immune, which it refuses
        let banished = sim.entity_banish(me, me, self.p.p_t + 2, &sn(&format!("p_ghost_{face}")), "");
        sim.add_buff(me, &spirit_buff(self.p.p_t + 2));
        self.cast = Cast { anchor: pos, q_next: now + 1, e_next: now + 1, ..Cast::default() };
        sim.play_sfx(&sn("p"), me, &InputTargetV1::target(me));
        sim.play_sfx(&sn("vo_p"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("spirit") {
            wlog(format!("{} SPIRIT #{k}: lethal damage caught at 1 hp (last hit by {}), a spirit for {} ticks{}", head(sim, me),
                         self.last_hit.map_or_else(|| "-".to_string(), |a| who(sim, a)), self.p.p_t,
                         if banished { format!(", banished with his ghost facing {face}") }
                         else { " - entity_banish refused: he stays targetable".to_string() }));
        }
    }

    /// 灵体放的技能（他放逐着出不了手，`Cast`）：亵渎一直烧，荒芜落在最近的敌人脚下，安魂曲在值得时引导。数字、画面照主包。
    fn spirit_casts(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, k: usize) {
        let Some((team, power, r_ready)) =
            sim.get_entity(me).map(|e| (e.team(), e.stat().magic_power.max(0) as usize, ready(&e, SkillSlotV1::Ult)))
        else {
            return;
        };
        let at = self.cast.anchor;
        let here = (at.0 as f64, at.1 as f64);
        let here_t = InputTargetV1::pos(at.0, at.1);
        // E Defile, burning the whole spirit (League's spirit keeps it on, free)
        if now >= self.cast.e_next {
            self.cast.e_next = now + E_PER;
            let (champs, others) = seen_foes(sim, team, here, E_R);
            for id in champs.iter().chain(&others).map(|f| f.0) {
                sim.deal_damage_typed(me, id, e_damage(power), DamageTypeV1::Ap, AttackTypeV1::Skill);
                sim.play_view_effect(&sn("e_hit"), me, &InputTargetV1::target(id), 0, 0, 0);
            }
            if now >= self.cast.ring_next {
                self.cast.ring_next = now + E_RING_EVERY;
                sim.play_view_effect(&sn("e_ring"), me, &here_t, 0, 0, 0);
            }
        }
        // Q Lay Waste: the blasts that fall now, then a new one
        let (due, keep): (Vec<_>, Vec<_>) = std::mem::take(&mut self.cast.booms).into_iter().partition(|b| b.1 <= now);
        self.cast.booms = keep;
        for (spot, _) in due {
            let (champs, others) = seen_foes(sim, team, (spot.0 as f64, spot.1 as f64), Q_R);
            let hit: Vec<usize> = champs.iter().chain(&others).map(|f| f.0).collect();
            let dmg = q_damage(power, hit.len());
            for &id in &hit {
                sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                let view = if hit.len() == 1 { "q_lone" } else { "q_hit" };
                sim.play_view_effect(&sn(view), me, &InputTargetV1::target(id), 0, 0, 0);
            }
            sim.play_view_effect(&sn("q_boom"), me, &InputTargetV1::pos(spot.0, spot.1), 0, 0, 0);
            sim.play_sfx(&sn("q_boom"), me, &InputTargetV1::pos(spot.0, spot.1));
        }
        if now >= self.cast.q_next {
            let (champs, others) = seen_foes(sim, team, here, Q_RANGE);
            if let Some(spot) = champs.first().or(others.first()).and_then(|f| sim.get_entity(f.0)).map(|e| e.pos()) {
                self.cast.q_next = now + Q_CD;
                self.cast.booms.push((spot, now + Q_DELAY));
                sim.play_view_effect(&sn("q_mark"), me, &InputTargetV1::pos(spot.0, spot.1), 0, 0, 0);
                sim.play_sfx(&sn("q"), me, &here_t);
            }
        }
        // R Requiem: one channel a spirit, when it is worth it and there is time to finish it
        match self.cast.requiem {
            Some(t) if now >= t => {
                self.cast.requiem = None;
                let foes = foes_by_distance(sim, team, here);
                for &(id, _) in &foes {
                    sim.deal_damage_typed(me, id, R_DMG + power * R_RATIO / 100, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    sim.play_view_effect(&sn("r_hit"), me, &InputTargetV1::target(id), 0, 0, 0);
                }
                sim.play_sfx(&sn("r_boom"), me, &here_t);
                if let Some(c) = counted("spirit_r_hit") {
                    wlog(format!("{} SPIRIT REQUIEM #{c}: {} enemy champions struck", head(sim, me), foes.len()));
                }
            }
            None if r_ready && !self.cast.r_used && r_in_time(k, self.p.p_t) => {
                let toll = foes_toll(sim, team, power);
                let hits: Vec<(usize, usize, usize)> = toll.iter().map(|f| (f.1, f.2, f.3)).collect();
                if r_worth(RWhen::Spirit, &hits, power) {
                    self.cast.r_used = true;
                    self.cast.requiem = Some(now + R_CH);
                    for &(id, ..) in &toll {
                        sim.add_buff(id, &BuffV1::timed(&sn("r_mark"), R_CH));
                    }
                    // seen by spirit_ai, which holds the game's AI's Requiem for R_CD after he is back
                    sim.add_buff(me, &BuffV1::timed(&sn("r_used"), self.p.p_t + 2));
                    sim.play_view_effect(&sn("r_cast"), me, &here_t, 0, 0, 0);
                    sim.play_sfx(&sn("r"), me, &here_t);
                    sim.play_sfx(&sn("vo_r"), me, &here_t);
                    if let Some(c) = counted("spirit_r") {
                        let (kills, low) = r_toll(&hits, power, SPIRIT_LOW);
                        wlog(format!("{} SPIRIT REQUIEM #{c}: channelling {R_CH} ticks - {kills} would die, {low} left under \
                                      {SPIRIT_LOW}%", head(sim, me)));
                    }
                }
            }
            _ => {}
        }
    }

    fn fall(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.spirit = None;
        self.cast.booms.clear();
        sim.entity_remove_buff(me, &sn("p_spirit"));
        let (hp, _) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        let killer = killer(sim, me, self.last_hit, self.last_player);
        sim.deal_damage_typed(killer, me, hp + 1000, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        if let Some(k) = counted("fall") {
            let h = self.hits;
            wlog(format!("{} FALL #{k}: the spirit's time is up, killed by {}; struck as a spirit by champions {} times, \
                          minions {}, towers {}, others {}", head(sim, me), who(sim, killer), h.champions, h.minions,
                         h.towers, h.others));
        }
    }
}

impl StablePassive for DeathDefied {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.ready = true;
        self.spirit = None;
        self.last_hit = None;
        self.last_player = None;
        self.next_guard = 0;
        self.alive_seen = false;
        self.hits = Hits::default();
        self.cast = Cast::default();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Karthus (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (hp, _) = e.hp();
        let pos = e.pos();
        let now = sim.tick();
        if let Some(t0) = self.spirit {
            let k = now.saturating_sub(t0);
            // a dead man does not walk: rooted where he fell (League's spirit stands and casts)
            if pos != self.cast.anchor {
                sim.entity_set_pos(me, self.cast.anchor.0, self.cast.anchor.1);
            }
            if k >= self.p.p_t {
                self.fall(sim, me);
            } else {
                self.spirit_casts(sim, me, now, k);
            }
            return;
        }
        if !self.ready {
            return;
        }
        if hp > 1 {
            self.alive_seen = true;
        }
        self.guard(sim, me, now);
        if hp <= 1 && self.alive_seen {
            let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
            if !other_undying(&list) {
                self.rise(sim, me, now);
            }
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, _: usize, attacker: usize, damage: usize) {
        let Some(kind) = sim.get_entity(attacker).filter(|_| attacker != self.me).map(|a| kind_of(&a)) else { return };
        if self.spirit.is_some() {
            // nothing should reach the spirit: who still does
            self.hits.add(kind);
            if let Some(k) = counted("spirit_hit") {
                wlog(format!("{} SPIRIT HIT #{k}: struck by {} ({damage} damage)", head(sim, self.me), who(sim, attacker)));
            }
        } else if damage > 0 {
            self.last_hit = Some(attacker);
            self.last_player = player_of(sim, attacker);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if self.spirit.is_some() {
            if let Some(k) = counted("spirit_kill") {
                wlog(format!("{} SPIRIT KILL #{k}: {} killed by the spirit", head(sim, me), who(sim, victim)));
            }
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _player: usize) {
        // the respawn timer counts the spirit (League's death timer runs from its start): spirit_ai cuts it the first tick
        // he is dead - here the game has not marked him dead yet (0.4.x: every try said `RESPAWN NOT CUT (alive)`)
        self.spirit = None;
        self.ready = false;
    }
}

// ===================== AI 钩子：灵体站着放技能，R 挑时机 =====================

/// Q 和 E 的施法距离、E 的圈、痛苦之墙找英雄的范围、普攻距离（build_karthus.py 的 q_range / e_cast / e_r / w_r /
/// atk_range；单元测试核对）。R 是全图的。
pub const Q_RANGE: f64 = 80000.0;
pub const E_RANGE: f64 = 55000.0;
pub const E_R: f64 = 55000.0;
pub const W_R: f64 = 60000.0;
pub const ATK_RANGE: f64 = 50000.0;

/// R 的伤害（build_karthus.py 的 r_dmg / r_ratio；单元测试核对）：魔法伤害，按目标魔抗 100 / (100 + mr) 打折
/// （league_ekko_rewind 的算法）。
pub const R_DMG: usize = 200;
pub const R_RATIO: usize = 75;
/// R 的引导（build_karthus.py 的 r_ch；单元测试核对）：灵体时开始的 R 引导完才倒下，最多等这么久。
pub const R_CH: usize = 180;
/// 泉水：离他这条命出生（开局、复活）的位置这么近以内。
pub const FOUNTAIN_R: f64 = 25000.0;
/// 灵体时放 R：能打死一个敌方英雄，或者把一个打到最大生命的这个百分比以下。
pub const SPIRIT_LOW: usize = 30;
/// 泉水里放 R：能打死一个，或者把至少 `FOUNTAIN_LOW_N` 个打到最大生命的 `FOUNTAIN_LOW`% 以下。
pub const FOUNTAIN_LOW: usize = 20;
pub const FOUNTAIN_LOW_N: usize = 2;
/// 拦下 R 时改成普攻的敌方英雄最远多远（再远就照游戏的 AI 原来的走路命令走，不穿过半张地图去打人）。
pub const HOLD_ATTACK_R: f64 = 70000.0;

/// 灵体由本包放的技能（0.5.0，build_karthus.py 的 q_cd / q_delay / q_r / q_dmg / q_ratio、e_per / e_dmg / e_ratio、r_cd；
/// 单元测试核对）：荒芜的冷却、标出落点后多久炸开、炸开的半径、伤害（只炸到一个两倍，英雄联盟的「孤立」）；亵渎每多少 tick
/// 烧一次、每次的伤害；R 的冷却（灵体放过安魂曲，复活后 `spirit_ai` 在这之前照样拦下游戏的 AI 的 R）。
pub const Q_CD: usize = 150;
pub const Q_DELAY: usize = 32;
pub const Q_R: f64 = 15000.0;
pub const Q_DMG: usize = 45;
pub const Q_RATIO: usize = 30;
pub const E_PER: usize = 15;
pub const E_DMG: usize = 10;
pub const E_RATIO: usize = 5;
pub const R_CD: usize = 4200;
/// 亵渎的圈（`e_ring`：主包 `e_on` 的画面放在地上）多久在灵体脚下重放一次。
pub const E_RING_EVERY: usize = 60;

/// 灵体的荒芜：炸到 `hit` 个敌人时每人的魔法伤害（只炸到一个两倍）。
pub fn q_damage(power: usize, hit: usize) -> usize {
    let d = Q_DMG + power * Q_RATIO / 100;
    if hit == 1 { d * 2 } else { d }
}

/// 灵体的亵渎：每 `E_PER` tick 每个敌人的魔法伤害。
pub fn e_damage(power: usize) -> usize {
    E_DMG + power * E_RATIO / 100
}

/// 灵体待到第 `k` tick（共 `p_t`）还来得及引导完安魂曲。
pub fn r_in_time(k: usize, p_t: usize) -> bool {
    k + R_CH + 1 <= p_t
}

/// R 打在魔抗 `mr` 的英雄身上的伤害（他的法强 `power`）。
pub fn r_damage(power: usize, mr: usize) -> usize {
    (R_DMG + power * R_RATIO / 100) * 100 / (100 + mr)
}

/// R 打完：(打死几个, 没死但剩的血不到最大生命 `low`% 的几个)。`foes`：每个敌方英雄的 (生命 + 护盾, 最大生命, 魔抗)。
pub fn r_toll(foes: &[(usize, usize, usize)], power: usize, low: usize) -> (usize, usize) {
    let mut kills = 0;
    let mut low_left = 0;
    for &(hp, max, mr) in foes {
        let d = r_damage(power, mr);
        if hp <= d {
            kills += 1;
        } else if (hp - d) * 100 <= low * max {
            low_left += 1;
        }
    }
    (kills, low_left)
}

/// 什么时候放 R（用户 2026-11-01：「最好改成死后放大 或者复活后在泉水放大 放大也要看敌方血量吧？不能乱放吧」）：死后的灵体里，
/// 或者复活后（回城后）在泉水里，而且要看敌方的血量；别的时候游戏的 AI 想放也拦下。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RWhen {
    Spirit,
    Fountain,
}

/// 这时候放 R 值不值：灵体里打死或打残（`SPIRIT_LOW`）一个就放；泉水里打死一个、或打残（`FOUNTAIN_LOW`）两个以上才放。
pub fn r_worth(when: RWhen, foes: &[(usize, usize, usize)], power: usize) -> bool {
    match when {
        RWhen::Spirit => {
            let (k, l) = r_toll(foes, power, SPIRIT_LOW);
            k + l >= 1
        }
        RWhen::Fountain => {
            let (k, l) = r_toll(foes, power, FOUNTAIN_LOW);
            k >= 1 || l >= FOUNTAIN_LOW_N
        }
    }
}

/// 正在施法（R 的引导也是）或被强制位移：不替 AI 按，按了会打断。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

fn busy(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| BUSY.iter().any(|k| k.code() == c.kind)))
}

fn spirit_on(e: &StableEntity<'_, '_>) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == sn("p_spirit"))
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 这一格现在能按：解锁了，冷却好了（引擎的「输入合法」不看冷却，league_pyke 的教训）。
fn ready(e: &StableEntity<'_, '_>, slot: SkillSlotV1) -> bool {
    e.cooldown(slot).is_some_and(|c| c.unlocked && (c.remaining == 0 || c.charges > 0))
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn at(e: &StableEntity<'_, '_>) -> (f64, f64) {
    (e.pos().0 as f64, e.pos().1 as f64)
}

/// 队伍 `team` 的敌方单位里能挑的：活着、选得中、`team` 看得见，不是塔、水晶、灵体，离 `from` 不超过 `reach`：
/// (英雄, 别的单位)，各自 (实体, 距离)，近的在前。看不见的不挑：灵体对着射程里的英雄按了几十到上百 tick 的 Q 放不出来
/// （2026-10-31、11-02 的日志），那时目标多半在草里。
fn seen_foes(sim: &StableSim<'_>, team: usize, from: (f64, f64), reach: f64) -> (Vec<(usize, f64)>, Vec<(usize, f64)>) {
    let mut champs = Vec::new();
    let mut others = Vec::new();
    for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower()
            || kind_of(&u) == Some(EntityKindV1::Nexus) || spirit_on(&u) || !sim.is_visible(team, u.id()) {
            continue;
        }
        let d = dist(from, at(&u));
        if d > reach {
            continue;
        }
        if u.is_champion() {
            champs.push((u.id(), d));
        } else {
            others.push((u.id(), d));
        }
    }
    champs.sort_by(|a, b| a.1.total_cmp(&b.1));
    others.sort_by(|a, b| a.1.total_cmp(&b.1));
    (champs, others)
}

/// 敌队活着、选得中的英雄，近的在前。
fn foes_by_distance(sim: &StableSim<'_>, team: usize, at: (f64, f64)) -> Vec<(usize, f64)> {
    let mut out: Vec<(usize, f64)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && u.is_champion())
        .map(|u| (u.id(), dist(at, (u.pos().0 as f64, u.pos().1 as f64))))
        .collect();
    out.sort_by(|a, b| a.1.total_cmp(&b.1));
    out
}

/// 他活着、拦下游戏的 AI 想放的 R 时改按什么：Q > E（在施法距离内）> 普攻最近的英雄（够不着就走过去）。
pub fn hold_pick(foes: &[(usize, f64)], ready: [bool; 2]) -> Vec<(InputKindV1, usize)> {
    let mut out = Vec::new();
    if ready[0] {
        out.extend(foes.iter().filter(|f| f.1 <= Q_RANGE).map(|f| (InputKindV1::Skill, f.0)));
    }
    if ready[1] {
        out.extend(foes.iter().filter(|f| f.1 <= E_RANGE).map(|f| (InputKindV1::Skill2, f.0)));
    }
    out.extend(foes.first().map(|f| (InputKindV1::Attack, f.0)));
    out
}

/// 敌队活着、选得中的英雄：(实体, 生命 + 护盾, 最大生命, 魔抗)，R 打完剩血最少的在前。
fn foes_toll(sim: &StableSim<'_>, team: usize, power: usize) -> Vec<(usize, usize, usize, usize)> {
    let mut out: Vec<(usize, usize, usize, usize)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && u.is_champion())
        .map(|u| (u.id(), u.hp().0 + u.shield(), u.hp().1.max(1), u.stat().magic_resistance.max(0) as usize))
        .collect();
    out.sort_by_key(|f| f.1.saturating_sub(r_damage(power, f.3)));
    out
}

/// 这一 tick 想怎么做（读 sim 时定好，读完再问游戏这些输入合不合法）。
enum Want {
    /// 泉水里放 R：按顺序试这些目标；(打死几个, 打残几个)。
    Fountain(Vec<usize>, (usize, usize)),
    /// 游戏的 AI 想放 R，这时候不放：改按这些（Q、E、近处的普攻），都不行就照它原来的走路命令。
    Hold(Vec<(InputKindV1, usize)>),
}

/// R 只在泉水里、敌方血量够低时放（`r_worth`），别的时候游戏的 AI 想放就拦下（用户 2026-11-01：「最好改成死后放大 或者复活后在
/// 泉水放大」）。灵体放逐着、自己出不了手，它的技能由被动放（`spirit_casts`，0.5.0），这里什么都不下；灵体放过安魂曲，复活回来
/// `R_CD` tick 内照样拦下（技能格没见过那一招，冷却是好的）。阵亡后的第一 tick 把复活倒计时扣掉灵体待的时间（`life.rs`；
/// 被动的 `on_dead` 那一刻游戏还没把他记成阵亡）。
#[derive(Clone, Default)]
struct SpiritAi {
    /// 他这条命出生的位置（泉水）：开局和每次复活后第一次看到他活着时记下。
    home: Option<(f64, f64)>,
    alive: bool,
    /// 游戏的 AI 最近一次下的走路命令：拦下它想放的 R 时照着走。
    last_move: Option<InputV1>,
    /// 这次灵体开始的 tick（阵亡后扣复活时间用）；灵体放过安魂曲的 tick。
    spirit_since: Option<usize>,
    r_used_at: Option<usize>,
}

impl StablePlayerAi for SpiritAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:spirit_ai")
    }

    /// 在 league_ult_press（100）之后：他的 R 由本钩子说了算。
    fn priority(&self) -> i32 {
        105
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let was = base.and_then(|b| InputKindV1::from_code(b.kind));
        if was == Some(InputKindV1::Move) {
            self.last_move = base;
        }
        let (want, names, line, spot) = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            if !pl.is_alive() {
                // his first tick dead after a spirit: League's death timer ran from the spirit's start
                if let Some(since) = self.spirit_since.take() {
                    let spent = tick.saturating_sub(since) as u64;
                    let left = pl.respawn_time() as u64;
                    let line = match life::shorten_respawn(&sim, player, respawn_after_spirit(left, spent)) {
                        Ok((was, now)) => format!("RESPAWN: {was} -> {now} ticks (the spirit's {spent} counted)"),
                        Err(why) => format!("RESPAWN NOT CUT ({why}): {left} ticks left, the spirit's {spent} not counted"),
                    };
                    if let Some(k) = counted("respawn") {
                        let at = pl.champion().map_or_else(|| format!("[t={tick}] player {player}"), |c| head(&sim, c.id()));
                        wlog(format!("{at} {line} #{k}"));
                    }
                }
                self.alive = false;
                return None;
            }
            let me = pl.champion()?;
            if !me.is_alive() {
                self.alive = false;
                return None;
            }
            let here = at(&me);
            if !self.alive || self.home.is_none() {
                self.home = Some(here);
                self.alive = true;
                self.spirit_since = None;
            }
            if spirit_on(&me) {
                // banished: nothing goes from here (the passive casts); when it began, and a Requiem it channelled
                self.spirit_since.get_or_insert(tick);
                if has_buff(&me, &sn("r_used")) && self.r_used_at.is_none_or(|t| tick > t + R_CD) {
                    self.r_used_at = Some(tick);
                }
                return None;
            }
            if busy(&me) {
                return None;
            }
            let in_home = self.home.is_some_and(|h| dist(here, h) <= FOUNTAIN_R);
            if !in_home && was != Some(InputKindV1::Ult) {
                return None; // nothing of ours to decide this tick
            }
            let power = me.stat().magic_power.max(0) as usize;
            let toll = foes_toll(&sim, me.team(), power);
            let hits: Vec<(usize, usize, usize)> = toll.iter().map(|f| (f.1, f.2, f.3)).collect();
            let r_ready = ready(&me, SkillSlotV1::Ult) && self.r_used_at.is_none_or(|t| tick >= t + R_CD);
            let qe = [ready(&me, SkillSlotV1::Skill), ready(&me, SkillSlotV1::Skill2)];
            let want = if in_home && r_ready && r_worth(RWhen::Fountain, &hits, power) {
                Want::Fountain(toll.iter().map(|f| f.0).collect(), r_toll(&hits, power, FOUNTAIN_LOW))
            } else if was == Some(InputKindV1::Ult) {
                let near: Vec<(usize, f64)> =
                    foes_by_distance(&sim, me.team(), here).into_iter().filter(|f| f.1 <= HOLD_ATTACK_R).collect();
                Want::Hold(hold_pick(&near, qe))
            } else {
                return None;
            };
            let ids: Vec<usize> = match &want {
                Want::Hold(c) => c.iter().map(|x| x.1).collect(),
                Want::Fountain(t, _) => t.clone(),
            };
            let names: HashMap<usize, String> = ids.into_iter().map(|t| (t, who(&sim, t))).collect();
            (want, names, head(&sim, me.id()), me.pos())
        };
        let name = |t: usize| names.get(&t).cloned().unwrap_or_else(|| format!("#{t}"));
        let first_valid = |ctx: &StableAiContext<'_>, cands: Vec<(InputKindV1, usize)>| {
            cands.into_iter().find_map(|(k, t)| {
                let input = InputV1::action(k, InputTargetV1::target(t));
                ctx.is_valid_input(&input).then_some((k, t, input))
            })
        };
        match want {
            Want::Fountain(targets, (kills, low)) => {
                let (_, t, input) = first_valid(ctx, targets.into_iter().map(|t| (InputKindV1::Ult, t)).collect())?;
                if let Some(k) = counted("r_fountain") {
                    wlog(format!("{line} R FOUNTAIN #{k}: Requiem from the fountain on {} - {kills} would die, {low} left \
                                  under {FOUNTAIN_LOW}%", name(t)));
                }
                Some(input)
            }
            Want::Hold(cands) => {
                let instead = first_valid(ctx, cands);
                let input = instead.map(|i| i.2).or(self.last_move).filter(|i| ctx.is_valid_input(i));
                if let Some(k) = counted("r_held") {
                    wlog(format!("{line} R HELD #{k}: the game's AI wanted Requiem away from the fountain and alive - {}",
                                 match (&instead, &input) {
                                     (Some((kind, t, _)), _) => format!("{kind:?} on {} instead", name(*t)),
                                     (None, Some(_)) => "its last walk instead".to_string(),
                                     _ => "standing instead".to_string(),
                                 }));
                }
                Some(input.unwrap_or_else(|| InputV1::move_to(spot.0, spot.1)))
            }
        }
    }
}

// ===================== 钩子：谁都不选灵体 =====================

/// 排在别的挑目标的钩子之后（最晚的是 league_sion 僵尸的 130），在蕾娜塔的狂暴（1_000_000）和解锁总闸
/// （league_unlock_guard，最后一个）之前。
pub const SHUN_PRIORITY: i32 = 200_000;
/// 改打别的单位：离出手的人这么近以内。
pub const SHUN_REACH: f64 = 90000.0;
/// 没有别的可打：退到灵体的亵渎圈外这么远（圈 `E_R` 外再加这些）。
pub const STEP_OUT: f64 = 15000.0;

/// 没有别的可打时往哪走：离灵体不到 `E_R + STEP_OUT` 就从灵体往自己这边退到那么远（叠在一起时往左），够远了就站着（None）。
pub fn step_out(me: (f64, f64), spirit: (f64, f64)) -> Option<(f64, f64)> {
    let keep = E_R + STEP_OUT;
    let d = dist(me, spirit);
    if d >= keep {
        return None;
    }
    let (ux, uy) = if d < 1.0 { (-1.0, 0.0) } else { ((me.0 - spirit.0) / d, (me.1 - spirit.1) / d) };
    Some(((spirit.0 + ux * keep).max(0.0), (spirit.1 + uy * keep).max(0.0)))
}

/// 英雄联盟的灵体谁都选不中：游戏的 AI（或别的钩子）让一个英雄普攻、放技能点向敌方的卡尔萨斯灵体时，改成同一格点向它
/// `SHUN_REACH` 内看得见的别的敌方英雄（普攻还可以是灵体那一队的小兵、召唤物，不打塔、不打野怪），近的先；都不行就退出
/// 亵渎的圈、站着。队友的技能（治疗、护盾）点向自己这边的灵体也一样（0.4.1：灵体是已经死了的人），改给 `SHUN_REACH` 内别的
/// 队友英雄；没有别的队友就照游戏的 AI（站着发呆比奶一下灵体更难看）。挂在每个英雄上：几乎每 tick 都没有新命令，或者命令不是点单位的，一读就走。
#[derive(Clone, Default)]
struct Shun;

/// 队伍 `team` 的英雄里能改给的（活着、选得中、不是灵体、不是 `but`），离 `from` 不超过 `reach`，近的在前。
fn mates(sim: &StableSim<'_>, team: usize, from: (f64, f64), reach: f64, but: usize) -> Vec<usize> {
    let mut out: Vec<(usize, f64)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() == team && u.id() != but && u.is_champion() && u.is_alive() && u.is_targetable() && !spirit_on(u))
        .map(|u| (u.id(), dist(from, at(&u))))
        .filter(|f| f.1 <= reach)
        .collect();
    out.sort_by(|a, b| a.1.total_cmp(&b.1));
    out.into_iter().map(|f| f.0).collect()
}

impl StablePlayerAi for Shun {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:shun")
    }

    fn priority(&self) -> i32 {
        SHUN_PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        let kind = InputKindV1::from_code(b.kind)?;
        if matches!(kind, InputKindV1::Move | InputKindV1::Return)
            || InputTargetKindV1::from_code(b.target.kind) != Some(InputTargetKindV1::Target) {
            return None;
        }
        let player = ctx.player_id();
        let (cands, here, spirit, ally, line, names) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            let s = sim.get_entity(b.target.target_id)?;
            if s.id() == me.id() || !spirit_on(&s) {
                return None;
            }
            let here = at(&me);
            let ally = s.team() == me.team();
            if ally && kind == InputKindV1::Attack {
                return None; // not an ally's order (Renata's berserk comes after this hook)
            }
            let cands: Vec<usize> = if ally {
                mates(&sim, me.team(), here, SHUN_REACH, s.id())
            } else {
                let (champs, others) = seen_foes(&sim, me.team(), here, SHUN_REACH);
                let mut c: Vec<usize> = champs.iter().map(|f| f.0).collect();
                if kind == InputKindV1::Attack {
                    // his side's minions and summons, not the jungle's monsters
                    c.extend(others.iter().map(|f| f.0).filter(|&t| sim.get_entity(t).is_some_and(|u| u.team() == s.team())));
                }
                c
            };
            let names: HashMap<usize, String> =
                cands.iter().chain([&s.id()]).map(|&t| (t, who(&sim, t))).collect();
            (cands, here, at(&s), ally, format!("{} {}", head(&sim, me.id()), who(&sim, me.id())), names)
        };
        let name = |t: usize| names.get(&t).cloned().unwrap_or_else(|| format!("#{t}"));
        let other = cands.into_iter().find_map(|t| {
            let input = InputV1::action(kind, InputTargetV1::target(t));
            ctx.is_valid_input(&input).then_some((t, input))
        });
        let (input, what) = match other {
            Some((t, input)) => (input, format!("{kind:?} on {}", name(t))),
            // no other ally for a heal or a shield: let it go (standing idle by the spirit would look worse, and the game's
            // AI would pick him again next tick)
            None if ally => return None,
            None => match step_out(here, spirit) {
                Some(p) => (InputV1::move_to(p.0 as u64, p.1 as u64), "out of Defile".to_string()),
                None => (InputV1::move_to(here.0 as u64, here.1 as u64), "a stand".to_string()),
            },
        };
        let tag = match (ally, kind == InputKindV1::Attack) {
            (true, _) => "shun_ally",
            (false, true) => "shun_attack",
            (false, false) => "shun_cast",
        };
        if let Some(k) = counted(tag) {
            wlog(format!("{line} SHUN #{k}: {kind:?} on the {} spirit {} -> {what}", if ally { "allied" } else { "enemy" },
                         name(b.target.target_id)));
        }
        Some(input)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Karthus: Death Defied's spirit) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:death_defied"), DeathDefied::default());
    module.add_player_input_ai(SpiritAi::default());
    module.add_player_input_ai(Shun);
    host.log(LogLevel::Info, "league_karthus loaded (Death Defied's spirit: untargetable, rooted, casting).");
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
    fn only_someone_elses_undying_holds_the_spirit_back() {
        let l = |v: &[(&str, bool)]| v.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        assert!(!other_undying(&l(&[("league_karthus_p_guard", true)])));
        assert!(!other_undying(&l(&[("league_karthus_p_spirit", true), ("league_karthus_e_on", false)])));
        assert!(other_undying(&l(&[("league_karthus_p_guard", true), ("league_soraka_w_guard", true)])));
    }

    #[test]
    fn the_respawn_counts_the_spirit() {
        // 25 s left at the fall, the spirit stood 7 s: 18 s left
        assert_eq!(respawn_after_spirit(1500, 420), 1080);
        // a Requiem held the fall 2 s longer: those count too
        assert_eq!(respawn_after_spirit(1500, 540), 960);
        // a short death timer: back a second after the fall, never at once
        assert_eq!(respawn_after_spirit(300, 420), BACK_MIN);
    }

    #[test]
    fn a_recall_runs_until_another_order() {
        let mv = Some(InputV1::move_to(1, 1));
        assert!(still_recalling(false, Some(InputV1::return_home())));
        assert!(still_recalling(true, None));
        assert!(!still_recalling(true, mv));
        assert!(!still_recalling(false, None));
    }

    #[test]
    fn params_parse() {
        assert_eq!(parse_params(r#"{"p_t":420}"#), Params::default());
        assert_eq!(parse_params(r#"{"p_t":300}"#).p_t, 300);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_karthus.py");
        let src = std::fs::read_to_string(path).expect("build_karthus.py");
        let d = Params::default();
        assert!(src.contains(&format!("\"p_t\": {}", d.p_t)), "p_t is not {} in build_karthus.P", d.p_t);
        assert!(src.contains(&format!("\"q_range\": {}", Q_RANGE as usize)), "q_range is not {Q_RANGE}");
        assert!(src.contains(&format!("\"e_cast\": {}", E_RANGE as usize)), "e_cast is not {E_RANGE}");
        assert!(src.contains(&format!("\"e_r\": {}", E_R as usize)), "e_r is not {E_R}");
        assert!(src.contains(&format!("\"w_r\": {}", W_R as usize)), "w_r is not {W_R}");
        assert!(src.contains(&format!("\"atk_range\": {}", ATK_RANGE as usize)), "atk_range is not {ATK_RANGE}");
        assert!(src.contains(&format!("\"r_dmg\": {R_DMG}, \"r_ratio\": {R_RATIO}")), "r_dmg / r_ratio are not {R_DMG} / {R_RATIO}");
        assert!(src.contains(&format!("\"r_ch\": {R_CH}")), "r_ch is not {R_CH}");
        // the spirit's own casts (0.5.0)
        for (k, v) in [("q_cd", Q_CD), ("q_delay", Q_DELAY), ("q_r", Q_R as usize), ("q_dmg", Q_DMG), ("q_ratio", Q_RATIO),
                       ("e_per", E_PER), ("e_dmg", E_DMG), ("e_ratio", E_RATIO), ("r_cd", R_CD)] {
            assert!(src.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in build_karthus.P");
        }
    }

    #[test]
    fn requiem_waits_for_low_enemies() {
        // 300 AP: 200 + 225 = 425 raw; 25 magic resist -> 340
        assert_eq!(r_damage(300, 0), 425);
        assert_eq!(r_damage(300, 25), 340);
        let foes = [(300, 1500, 25), (900, 1500, 25), (2000, 2500, 0)];
        // the first dies; the second is left at 560 of 1500 (37 %); the third at 1575 of 2500
        assert_eq!(r_toll(&foes, 300, 20), (1, 0));
        assert_eq!(r_toll(&foes, 300, 40), (1, 1));
        assert!(r_worth(RWhen::Spirit, &foes, 300));
        assert!(r_worth(RWhen::Fountain, &foes, 300));
        // nobody low: never from the fountain, never as a spirit
        let healthy = [(1400, 1500, 25), (2400, 2500, 0)];
        assert!(!r_worth(RWhen::Spirit, &healthy, 300));
        assert!(!r_worth(RWhen::Fountain, &healthy, 300));
        // one left at 25 %: enough for the spirit, the fountain wants two under 20 % (or a kill)
        let one = [(715, 1500, 25), (2400, 2500, 0)];
        assert!(r_worth(RWhen::Spirit, &one, 300));
        assert!(!r_worth(RWhen::Fountain, &one, 300));
        let two = [(600, 1500, 25), (600, 1500, 25)];
        assert!(r_worth(RWhen::Fountain, &two, 300));
    }

    fn codes(v: Vec<(InputKindV1, usize)>) -> Vec<(u32, usize)> {
        v.iter().map(|c| (c.0.code(), c.1)).collect()
    }

    #[test]
    fn the_banished_spirit_casts_lay_waste_defile_and_requiem() {
        // 「死了灵体还能移动 还能有残血？」「这能和英雄联盟一样吗」: the whole spirit is banished, its spells are the passive's
        assert_eq!(q_damage(0, 3), Q_DMG);
        assert_eq!(q_damage(100, 2), Q_DMG + Q_RATIO);
        assert_eq!(q_damage(100, 1), 2 * (Q_DMG + Q_RATIO), "one alone: twice (League's isolation)");
        assert_eq!(e_damage(200), E_DMG + 2 * E_RATIO);
        // a Requiem only while there is time to finish it before the spirit falls
        assert!(r_in_time(0, 420));
        assert!(r_in_time(420 - R_CH - 1, 420));
        assert!(!r_in_time(420 - R_CH, 420));
        // his ghost faces the nearest enemy champion (an effect picture is never mirrored)
        assert_eq!(side(500, Some(400)), "l");
        assert_eq!(side(500, Some(600)), "r");
        assert_eq!(side(500, None), "r");
    }

    #[test]
    fn a_held_requiem_turns_into_q_e_or_an_attack() {
        let (q, e, a) = (InputKindV1::Skill.code(), InputKindV1::Skill2.code(), InputKindV1::Attack.code());
        let foes = [(7, 20000.0), (8, 60000.0), (9, 500000.0)];
        assert_eq!(codes(hold_pick(&foes, [true, true])), [(q, 7), (q, 8), (e, 7), (a, 7)]);
        assert_eq!(codes(hold_pick(&foes, [false, false])), [(a, 7)]);
        assert!(hold_pick(&[], [true, true]).is_empty());
    }

    #[test]
    fn enemies_step_out_of_defile_then_stand() {
        let s = (100000.0, 100000.0);
        let p = step_out((120000.0, 100000.0), s).expect("inside the ring: out");
        assert!((p.0 - (100000.0 + E_R + STEP_OUT)).abs() < 1e-6 && (p.1 - 100000.0).abs() < 1e-6);
        assert_eq!(step_out((100000.0 + E_R + STEP_OUT, 100000.0), s), None);
        let on_it = step_out(s, s).expect("on the spirit: out");
        assert!(on_it.0 < s.0);
    }

    #[test]
    fn the_shun_comes_after_the_target_pickers() {
        // league_sion's zombie hook (130) is the last that picks targets; Renata's berserk (1_000_000) comes after
        assert!(SHUN_PRIORITY > 130 && SHUN_PRIORITY < 1_000_000);
    }

    #[test]
    fn hits_count_by_kind() {
        let mut h = Hits::default();
        for k in [Some(EntityKindV1::Champion), Some(EntityKindV1::Champion), Some(EntityKindV1::Tower), None] {
            h.add(k);
        }
        assert_eq!(h, Hits { champions: 2, minions: 0, towers: 1, others: 1 });
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_guard", "p_spirit", "p_ward", "p", "vo_p", "e_on", "w_cd"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
