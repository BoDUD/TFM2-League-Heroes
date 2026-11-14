//! 维克托附加包（用户 2026-11-14：「吉格斯和维克托按照联盟的重做」——之前选的「按等级依次升级」改成英雄联盟的海克斯碎片）。
//!
//! 主包是纯数据：数据数不了碎片，也存不住跨死亡的计数（死亡会清掉自定义增益），所以主包按等级升级（`lv_e` / `lv_q` / `lv_w` /
//! `lv_r` 级），普攻里的护盾探针量他的等级。`mod.override_info` 把主包的维克托换成 `override/` 里的副本（`make_override.py`
//! 从 tools/kit/build_viktor.py 的 native=1 生成）：数据和主包一样，只是普攻里没有量等级的探针，被动换成本包的
//! `league_viktor:evolve`。
//!
//! - **海克斯碎片**（英雄联盟 V25.06 / V14.24：小兵和野怪 1 个、炮车 / 超级兵 / 史诗野怪 10 个、英雄参与击杀 20 个，每
//!   100 个碎片强化一个技能，R 在三个基础技能之后）：他补到的每个小兵、野怪（`on_unit_kill`，用什么打死的都算）`hex_unit`
//!   个，他的每个英雄击杀（`on_kill`）和助攻（`on_assist`）`hex_takedown` 个，他最后一击的史诗野怪 `hex_epic` 个（这个游戏的
//!   小兵不分炮车、超级兵）；攒够 `hex_cost` 个就按主包的顺序强化下一个：E 余波（`league_viktor_s1`）、Q 涡轮增压（`s2`）、
//!   W 磁化（`s3`）、R 完美风暴（`s4`），播主包的进化金光和声音。英雄联盟一局 30 分钟上下才攒齐四个，这里一局 10 分钟左右，
//!   所以一个强化的价钱 `hex_cost` 按这个游戏的节奏定：经典引擎模拟里他到主包 3 / 5 / 7 / 9 级（主包强化的时候）平均攒到的
//!   碎片（tools/kit/build_viktor.py 的 P）。碎片和强化死了也留着，强化的旗子每条命补回去。
//! - **面板上的碎片数**：攒着还没用掉的碎片挂成 `league_viktor_hex_<n>`，league.dll 的技能栏层数格读它（tools/kit/stack_nums.py
//!   的梯子规则）。
//! - **重力场的沉重引力每人各算**（英雄联盟 V14.24：重力场落下 0.75 秒后生效，场里的敌人每 0.25 秒叠一层，第五层晕眩 1.5 秒，
//!   每次施放每人一次）：主包数据数不了每个人在场里待了多久，只能在生效 `w_stun_at` tick 时把还在场里的都晕住；副本的重力场
//!   落地时调本包的 `:field`（给他挂上带着落点的记号 `league_viktor_wf:<x>:<y>`），被动接过来：生效（`w_arm`）以后，每个敌方单位
//!   在场里连着待满 `w_stun_at` tick（五层）就晕眩 `w_stun`，每人一次，离开场就从头叠；晕到第一个人时在场中心播主包的晕眩爆发。
//!   维克托死了重力场照旧（英雄联盟也是）。减速还是数据的。
//!
//! 数字都从英雄数据的 `passive.params` 来；状态在每个维克托自己的被动里（服务端预模拟和你看的那场各算各的）。本包不按任何技能键。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_viktor.log`，每次启动游戏重写：`SPAWN`、`HEX`（得了碎片：
//! 从哪来、现在多少）、`EVOLVE`（强化了哪个技能）、`FIELD`（重力场立起）、`GRAVITY`（谁在场里叠满五层被晕）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_viktor";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_viktor") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包维克托的名字（buff、画面、声音都以它开头）。
fn vk(x: &str) -> String {
    format!("league_viktor_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VIKTOR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_viktor.log");
        }
    }
    PathBuf::from("league_viktor.log")
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

/// 这次启动每种日志合计先记这么多行，之后每 `LOG_EVERY` 行记一行（服务端的预模拟也在写）。
const LOG_FIRST: usize = 60;
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，`make_override.py` 写进去）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 一个小兵、一个野怪给几个碎片（英雄联盟 1）。
    pub hex_unit: u64,
    /// 他最后一击的史诗野怪（英雄联盟 10，和炮车、超级兵一样）。
    pub hex_epic: u64,
    /// 一次英雄击杀或助攻（英雄联盟 20）。
    pub hex_takedown: u64,
    /// 一个强化的价钱（英雄联盟 100；这里按这个游戏的节奏，见 build_viktor.py 的 P）。
    pub hex_cost: u64,
    /// 重力场：落下多少 tick 后生效、在场里连着待多少 tick 晕（五层）、晕多久、半径（加身体）、落下后多久消失。
    pub w_arm: usize,
    pub w_stun_at: usize,
    pub w_stun: usize,
    pub w_r: u64,
    pub w_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { hex_unit: 1, hex_epic: 10, hex_takedown: 20, hex_cost: 40, w_arm: 45, w_stun_at: 60, w_stun: 90,
                 w_r: 30000, w_t: 240 }
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
            "hex_unit" => p.hex_unit = v,
            "hex_epic" => p.hex_epic = v,
            "hex_takedown" => p.hex_takedown = v,
            "hex_cost" => p.hex_cost = v,
            "w_arm" => p.w_arm = v as usize,
            "w_stun_at" => p.w_stun_at = v as usize,
            "w_stun" => p.w_stun = v as usize,
            "w_r" => p.w_r = v,
            "w_t" => p.w_t = v as usize,
            _ => {}
        }
    }
    p
}

// ===================== 碎片（单元测试用） =====================

/// 强化的顺序（主包按等级的顺序；英雄联盟 R 在三个基础技能之后）：(旗子, 日志里的名字)。
pub const AUGMENTS: [(&str, &str); 4] = [
    ("s1", "E Aftershock"),
    ("s2", "Q Turbocharge"),
    ("s3", "W Magnetize"),
    ("s4", "R Perfect Storm"),
];

/// 碎片从哪来。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source {
    Unit,
    Epic,
    Takedown,
}

impl Source {
    fn label(self) -> &'static str {
        match self {
            Source::Unit => "minion / monster",
            Source::Epic => "epic monster",
            Source::Takedown => "champion takedown",
        }
    }
}

/// 一个维克托的碎片：一共得了多少、还攒着多少、强化了几个。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Hex {
    pub total: u64,
    pub held: u64,
    pub augments: usize,
}

impl Hex {
    /// 得碎片；返回这次强化了哪几个（AUGMENTS 的下标）。
    pub fn gain(&mut self, p: &Params, source: Source) -> Vec<usize> {
        let n = match source {
            Source::Unit => p.hex_unit,
            Source::Epic => p.hex_epic,
            Source::Takedown => p.hex_takedown,
        };
        self.total += n;
        self.held += n;
        let mut out = Vec::new();
        while self.augments < AUGMENTS.len() && p.hex_cost > 0 && self.held >= p.hex_cost {
            self.held -= p.hex_cost;
            out.push(self.augments);
            self.augments += 1;
        }
        out
    }
}

/// 面板上的数：league.dll 的层数格读 `league_viktor_hex_` 后面的数（tools/kit/stack_nums.py 的梯子规则）。
pub fn count_name(held: u64) -> String {
    vk(&format!("hex_{held}"))
}

/// 一个单位是不是史诗野怪（大龙、小龙之类）。
fn epic(kind: Option<EntityKindV1>) -> bool {
    matches!(kind, Some(EntityKindV1::Epic | EntityKindV1::Serpen))
}

// ===================== 重力场（单元测试用） =====================

pub type Pt = (f64, f64);

/// 读不到身体半径时用的。
pub const BODY: f64 = 10_000.0;

/// 重力场落点的记号（数据调 `:field` 时挂在他身上，被动取走）。
pub const FIELD_MARK: &str = "league_viktor_wf:";
/// 记号挂几 tick（被动每 tick 都看）。
const MARK_T: usize = 3;

pub fn field_mark(x: u64, y: u64) -> String {
    format!("{FIELD_MARK}{x}:{y}")
}

pub fn parse_field(name: &str) -> Option<(u64, u64)> {
    let (x, y) = name.strip_prefix(FIELD_MARK)?.split_once(':')?;
    Some((x.parse().ok()?, y.parse().ok()?))
}

fn dist(a: Pt, b: Pt) -> f64 {
    (a.0 - b.0).hypot(a.1 - b.1)
}

/// 一个敌方单位：编号、位置、身体半径、现在免不免控。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub body: f64,
    pub immune: bool,
}

/// 一个重力场：中心、哪一 tick 生效、哪一 tick 消失、场里每个敌人连着待了几 tick、晕过谁（每次施放每人一次）。
#[derive(Clone, Debug, PartialEq)]
pub struct Field {
    pub at: Pt,
    pub armed: usize,
    pub until: usize,
    pub inside: Vec<(usize, usize)>,
    pub done: Vec<usize>,
}

impl Field {
    /// 在 `now` 落下的重力场。
    pub fn new(p: &Params, at: Pt, now: usize) -> Self {
        Field { at, armed: now + p.w_arm, until: now + p.w_t, inside: Vec::new(), done: Vec::new() }
    }

    /// 这一 tick：生效以后场里的敌人各多待一 tick（离开场就从头叠），待满 `w_stun_at`（第五层）、还没被这个场晕过、
    /// 现在不免控的晕眩（记进 `done`；免控的等它过去再晕）。
    pub fn step(&mut self, p: &Params, now: usize, units: &[Unit]) -> Vec<usize> {
        if now < self.armed || now >= self.until {
            return Vec::new();
        }
        let r = p.w_r as f64;
        let mut inside = Vec::new();
        let mut out = Vec::new();
        for u in units.iter().filter(|u| dist(u.at, self.at) <= r + u.body) {
            let t = self.inside.iter().find(|x| x.0 == u.id).map_or(0, |x| x.1) + 1;
            inside.push((u.id, t));
            if t >= p.w_stun_at.max(1) && !u.immune && !self.done.contains(&u.id) {
                self.done.push(u.id);
                out.push(u.id);
            }
        }
        self.inside = inside;
        out
    }
}

// ===================== 被动 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn cc_immune(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune))
}

#[derive(Clone, Default)]
struct Evolve {
    p: Params,
    hex: Hex,
    /// 面板上现在挂着的数。
    shown: Option<u64>,
    /// 上一次补旗子时他的身子（复活是新的实体）。
    body: Option<usize>,
    /// 立着的重力场、他是哪一队（死了也照算）。
    fields: Vec<Field>,
    team: Option<usize>,
}

impl Evolve {
    fn gain(&mut self, sim: &mut StableSim<'_>, me: usize, source: Source, what: &str) {
        let done = self.hex.gain(&self.p, source);
        if let Some(k) = counted("hex") {
            wlog(format!("{} HEX #{k}: +{} from {} ({what}): {} held, {} in all, {} augment(s)", head(sim, me),
                         match source { Source::Unit => self.p.hex_unit, Source::Epic => self.p.hex_epic,
                                        Source::Takedown => self.p.hex_takedown },
                         source.label(), self.hex.held, self.hex.total, self.hex.augments));
        }
        for i in done {
            let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
            if alive {
                let on_me = InputTargetV1::target(me);
                sim.play_view_effect(&vk("evo"), me, &on_me, 0, 0, 0);
                sim.play_sfx(&vk("evo"), me, &on_me);
            }
            if let Some(k) = counted("evolve") {
                wlog(format!("{} EVOLVE #{k}: {} ({} fragments in all){}", head(sim, me), AUGMENTS[i].1, self.hex.total,
                             if alive { "" } else { " - he is dead, the flag comes with his next life" }));
            }
        }
        self.keep(sim, me);
    }

    /// 强化的旗子挂在他身上（数据的 `SwitchByBuff` 读施法者的；死了复活旗子会没，这里补回去），面板上的数跟着碎片改。
    fn keep(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        if self.body != Some(me) {
            self.body = Some(me);
            self.shown = None;
        }
        for (flag, _) in AUGMENTS.iter().take(self.hex.augments) {
            let name = vk(flag);
            if !has(sim, me, &name) {
                sim.add_buff(me, &BuffV1::named(&name));
            }
        }
        let held = self.hex.held;
        if self.shown != Some(held) {
            if let Some(old) = self.shown {
                sim.entity_remove_buff(me, &count_name(old));
            }
            if held > 0 {
                sim.add_buff(me, &BuffV1::named(&count_name(held)));
            }
            self.shown = Some(held);
        }
    }
}

impl Evolve {
    /// 重力场：取走 `:field` 挂的记号立起重力场，立着的每一个给场里的敌人叠层、晕叠满的。
    fn watch_fields(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let mut marks = Vec::new();
        if let Some(e) = sim.get_entity(me) {
            self.team = Some(e.team());
            marks = (0..e.buff_count())
                .filter_map(|i| e.buff_at(i))
                .filter_map(|b| parse_field(b.name()).map(|at| (b.name().to_string(), at)))
                .collect();
        }
        for (name, (x, y)) in marks {
            sim.entity_remove_buff(me, &name);
            let at = (x as f64, y as f64);
            // the same mark read twice (it could not be taken off him): still one field
            if self.fields.iter().any(|f| f.at == at && f.until + MARK_T >= now + self.p.w_t) {
                continue;
            }
            self.fields.push(Field::new(&self.p, at, now));
            if let Some(k) = counted("field") {
                wlog(format!("{} FIELD #{k} at ({x}, {y}): armed in {} ticks, {} ticks inside stun {} ticks", head(sim, me),
                             self.p.w_arm, self.p.w_stun_at, self.p.w_stun));
            }
        }
        self.fields.retain(|f| f.until > now);
        let Some(team) = self.team else { return };
        if self.fields.is_empty() {
            return;
        }
        let units: Vec<Unit> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && u.is_targetable())
            .filter(|u| !u.is_tower() && !matches!(u.kind(), Some(EntityKindV1::Nexus | EntityKindV1::Tower)))
            .map(|u| {
                let (x, y) = u.pos();
                let body = u.radius();
                Unit { id: u.id(), at: (x as f64, y as f64), body: if body > 0 { body as f64 } else { BODY },
                       immune: false }
            })
            .collect();
        let units: Vec<Unit> = units.into_iter().map(|u| Unit { immune: cc_immune(sim, u.id), ..u }).collect();
        let p = self.p;
        let mut hits = Vec::new();
        for f in self.fields.iter_mut() {
            let first = f.done.is_empty();
            let got = f.step(&p, now, &units);
            if first && !got.is_empty() {
                hits.push((None, f.at));
            }
            hits.extend(got.into_iter().map(|id| (Some(id), f.at)));
        }
        for (id, at) in hits {
            let Some(id) = id else {
                // the field's own burst, as the main pack's stun moment
                sim.play_view_effect(&vk("w_burst"), me, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
                continue;
            };
            sim.apply_cc(id, &CcV1::stun(p.w_stun as u64));
            let on_him = InputTargetV1::target(id);
            sim.play_view_effect(&vk("w_stun"), me, &on_him, 0, 0, 0);
            let champion = sim.get_entity(id).is_some_and(|u| u.is_champion());
            if champion {
                sim.play_sfx(&vk("w_stun"), me, &on_him);
            }
            if let Some(k) = counted("gravity") {
                wlog(format!("{} GRAVITY #{k}: #{id} ({}) {} ticks in the field at ({:.0}, {:.0}) - stunned {} ticks",
                             head(sim, me), if champion { "champion" } else { "unit" }, p.w_stun_at, at.0, at.1, p.w_stun));
            }
        }
    }
}

/// 重力场落下（副本里在落点上）：给他挂上带着落点的记号，被动下一次看到就立起重力场。
struct FieldFx;

impl StableEffectType for FieldFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let at = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Pos) => Some((input.x, input.y)),
            Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|e| e.pos()),
            _ => None,
        };
        let Some((x, y)) = at else {
            wlog(format!("{} field: no point in the input (kind {})", head(sim, caster), input.kind));
            return;
        };
        sim.add_buff(caster, &BuffV1::timed(&field_mark(x, y), MARK_T));
    }

    /// The copy's W holds no `Stun` now: the AI reads the field's stun here.
    fn expected_cc_time(&self) -> Option<usize> {
        Some(Params::default().w_stun)
    }
}

/// 每隔这么多 tick 看一眼旗子和面板上的数。
const KEEP_EVERY: usize = 3;

impl StablePassive for Evolve {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Viktor (player {player}), {} held, {} augment(s), {:?}",
                         head(sim, me), self.hex.held, self.hex.augments, self.p));
        }
        self.keep(sim, me);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        let kind = sim.get_entity(victim).and_then(|e| e.kind());
        let (source, what) = if epic(kind) { (Source::Epic, "epic") } else { (Source::Unit, "cs") };
        self.gain(sim, me, source, &format!("{what} #{victim}"));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        let Some(v) = sim.get_entity(victim) else { return };
        if v.is_champion() {
            self.gain(sim, me, Source::Takedown, &format!("killed #{victim}"));
        } else if epic(v.kind()) {
            // an epic monster's last hit (League: 10, as a siege or super minion); minions and camps come by on_unit_kill
            self.gain(sim, me, Source::Epic, &format!("epic #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.gain(sim, me, Source::Takedown, "assist");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.watch_fields(sim, me);
        if sim.tick() % KEEP_EVERY == 0 || self.body != Some(me) {
            self.keep(sim, me);
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Viktor: Glorious Evolution by League's Hex Fragments, Gravity Field's Heavy Gravity per enemy) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:evolve"), Evolve::default());
    module.add_native_effect(format!("{ID}:field"), FieldFx);
    host.log(LogLevel::Info, "league_viktor loaded (Glorious Evolution by Hex Fragments, Heavy Gravity per enemy).");
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

    fn p() -> Params {
        Params::default()
    }

    #[test]
    fn params_from_the_kit() {
        // the override's own params are this file's defaults
        let text = include_str!("../override/league_viktor.data_champion");
        let at = text.find("\"passive_ref\": \"league_viktor:evolve\"").expect("the passive in the override");
        let body = &text[at..];
        let json = &body[body.find('{').unwrap()..=body.find('}').unwrap()];
        assert_eq!(parse_params(json), Params::default(), "{json}");
        assert_eq!(parse_params(r#"{"hex_cost":100,"hex_unit":2}"#), Params { hex_cost: 100, hex_unit: 2, ..p() });
        // the copy reads the flags this passive hangs and has no level probe of its own
        for (flag, _) in AUGMENTS {
            assert!(text.contains(&format!("\"buff_name\": \"league_viktor_{flag}\"")), "{flag} read in the copy");
        }
        assert!(!text.contains("league_viktor_pr_"), "the level probe is not in the copy");
        assert!(text.contains("\"name\": \"league_viktor_evo\""), "the evolution's picture");
        // W's stun is this add-on's: the copy calls :field and holds no Stun of its own
        assert!(text.contains("\"effect_ref\": \"league_viktor:field\""), "the field in the copy");
        assert!(!text.contains("\"type\": \"Stun\""), "no data stun left in the copy");
        for name in ["w_burst", "w_stun"] {
            assert!(text.contains(&format!("\"name\": \"league_viktor_{name}\"")), "{name}'s picture");
        }
    }

    #[test]
    fn the_field_mark_carries_its_point() {
        let m = field_mark(959_999, 123_456);
        assert_eq!(m, "league_viktor_wf:959999:123456");
        assert!(m.len() <= BUFF_NAME_CAP);
        assert_eq!(parse_field(&m), Some((959_999, 123_456)));
        assert_eq!(parse_field("league_viktor_s1"), None);
    }

    fn unit(id: usize, x: f64) -> Unit {
        Unit { id, at: (x, 0.0), body: BODY, immune: false }
    }

    #[test]
    fn heavy_gravity_stuns_each_enemy_after_five_stacks_once() {
        // League: armed 0.75 s after it lands, a stack every 0.25 s inside, the fifth stuns 1.5 s, once per cast per enemy
        let pp = p();
        let mut f = Field::new(&pp, (0.0, 0.0), 1000);
        let a = unit(1, 0.0);
        let b = unit(2, 35_000.0);     // inside: 30000 + his body
        let c = unit(3, 45_000.0);     // outside
        let mut stunned = Vec::new();
        for t in 1000..1300 {
            // b walks in only at 1100; a stands in the middle all along
            let units: Vec<Unit> = if t < 1100 { vec![a, c] } else { vec![a, b, c] };
            for id in f.step(&pp, t, &units) {
                stunned.push((id, t));
            }
        }
        assert_eq!(stunned, vec![(1, 1000 + 45 + 59), (2, 1100 + 59)], "60 ticks inside after the arming, each once");
        // the field is gone w_t after it landed
        assert_eq!(f.until, 1240);
        assert!(f.step(&pp, 1240, &[unit(9, 0.0)]).is_empty());
    }

    #[test]
    fn leaving_the_field_starts_over_and_immunity_waits() {
        let pp = p();
        let mut f = Field::new(&pp, (0.0, 0.0), 0);
        let mut got = Vec::new();
        for t in 45..200 {
            // in for 40 ticks, out for 10, then in again
            let here = !(85..95).contains(&t);
            let immune = (95..170).contains(&t);
            let u = Unit { immune, ..unit(1, if here { 0.0 } else { 90_000.0 }) };
            got.extend(f.step(&pp, t, &[u]).into_iter().map(|id| (id, t)));
        }
        // back in at 95: 60 ticks inside at 154, but immune until 170
        assert_eq!(got, vec![(1, 170)]);
    }

    #[test]
    fn league_s_fragments() {
        // League: 1 a minion or monster, 10 an epic monster, 20 a takedown; League's own price 100
        let league = Params { hex_cost: 100, ..p() };
        let mut h = Hex::default();
        for _ in 0..80 {
            assert!(h.gain(&league, Source::Unit).is_empty());
        }
        assert_eq!(h.gain(&league, Source::Takedown), vec![0], "80 cs + one takedown: the first augment");
        assert_eq!((h.held, h.total, h.augments), (0, 100, 1));
        assert!(h.gain(&league, Source::Epic).is_empty());
        assert_eq!(h.held, 10);
    }

    #[test]
    fn the_augments_come_in_the_main_packs_order_and_stop_at_four() {
        let mut h = Hex::default();
        let mut got = Vec::new();
        for _ in 0..20 {
            got.extend(h.gain(&p(), Source::Takedown));
        }
        assert_eq!(got, vec![0, 1, 2, 3], "E, Q, W, then R");
        assert_eq!(AUGMENTS.map(|a| a.0), ["s1", "s2", "s3", "s4"]);
        assert_eq!(h.augments, 4);
        assert_eq!(h.held, 20 * 20 - 4 * p().hex_cost, "fragments past the last augment are kept (the panel shows them)");
        // a takedown worth two augments at once
        let mut two = Hex::default();
        assert_eq!(two.gain(&Params { hex_takedown: 2 * p().hex_cost, ..p() }, Source::Takedown), vec![0, 1]);
        // a zero price never loops
        assert!(Hex::default().gain(&Params { hex_cost: 0, ..p() }, Source::Unit).is_empty());
    }

    #[test]
    fn fragment_count_on_the_panel() {
        // league.dll's stack box reads the number after `league_viktor_hex_` (tools/kit/stack_nums.py)
        assert_eq!(count_name(0), "league_viktor_hex_0");
        assert_eq!(count_name(37), "league_viktor_hex_37");
    }
}
