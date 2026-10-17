//! 烈娜塔附加包（用户 2026-10-17：「方案可以，全按推荐做（辅助、Util，布局 A，做扩展包，PPU 1.5）」）。主包保持纯数据；
//! `mod.override_info` 把主包的烈娜塔换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_renata.py 的 `native=1`
//! 生成：普攻照样挂印记但数据不再引爆、数据不再放 W、狂暴照样禁攻击禁技能但不带数据的「乱打一圈」，被动换成本包的
//! `league_renata:glasc`，普攻和大招的说明开头加【附加包】），本包把这三件事做成英雄联盟的样子：
//!
//! - **物尽其用**：队友真的出手打带印记的敌方英雄时引爆（league_braum 的做法：队友的普攻 / 技能冷却跳起来就是出手了；普攻看他身边
//!   最近的敌方单位是不是带印记的英雄，技能看他身边带印记的敌方英雄；POP_WAIT tick 后打中时还带着印记就引爆）：p_pop +
//!   p_pop_ap% 法强的魔法伤害、最大生命 p_pop_hp% 的真实伤害，去掉印记。主包的数据版是「印记附近有两个她这边的英雄就引爆」。
//! - **及时救难**（英雄联盟的规则）：她活着、W 不在冷却时每 WATCH tick 看一次，w_range 内的队友（不算她自己）身边 DANGER_NEAR 内
//!   有敌方英雄、又被硬控或生命不到 DANGER_HP，就挑生命比例最低的那个：攻速 +w_as%、移速 +w_ms%、w_t tick 不死（主包的 buff
//!   `league_renata_w_buff`，画面照主包）。期间受到致命伤害（生命到 1、身上没有别人的「不死」）就回满生命，再在 w_doom tick 内流失到
//!   1；这期间他参与击杀（击杀或助攻数变多）就保住、不再流失，没参与就阵亡（算离他最近的敌方英雄的）。主包的数据版是「不会阵亡、结束时
//!   回血」。
//! - **恶意收购**：被化学波扫中的敌方英雄（主包的 `league_renata_r_berserk`，数据已禁攻击、禁技能）真的转身打自己人：AI 钩子
//!   （`league_renata:berserk`，所有玩家）让他走向最近的队友，到 LASH_REACH 内就站住；本包按他自己的攻击间隔、用他自己的攻击力打那个
//!   队友（`deal_damage_typed`；引擎不认同队伤害就算在烈娜塔头上），挥一下（Animation "attack"）、播主包的 r_lash_hit。主包的数据版是
//!   「每 r_per 秒对身边的队友造成魔法伤害」。
//!
//! 被动在玩家身上、每份模拟各一份，她死了也照样每 tick 跑（救难、狂暴不因她阵亡停下）。日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_renata.log`，每次启动游戏重写，上一次的留在 .prev.log：`POP`、`BAILOUT`、
//! `REVIVE`、`SAVED`、`DOOMED`、`LASH`，都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_renata";
/// Written out (in the bundle `env!("CARGO_PKG_VERSION")` would be league_addons').
const VERSION: &str = "0.1.0";
/// 物尽其用的印记（主包数据：她打中敌方英雄时挂上）。
pub const MARK: &str = "league_renata_p_mark";
/// 及时救难（主包数据的 buff 名：画面绑在它上面）。
pub const W_BUFF: &str = "league_renata_w_buff";
/// 狂暴（主包数据：化学波扫中的敌方英雄）。
pub const BERSERK: &str = "league_renata_r_berserk";

/// 每隔几 tick 看一次要不要放 W（主包的看守也是 15）。
const WATCH: usize = 15;
/// 队友出手（冷却跳起）后多少 tick 算打中：普攻的前摇加飞行。
const POP_WAIT: usize = 10;
/// 普攻：他身边这么远内最近的敌方单位就是他打的；技能：这么远内带印记的敌方英雄。
const ATTACK_REACH: f64 = 75000.0;
const SKILL_REACH: f64 = 90000.0;
/// 队友危急：身边这么远内有敌方英雄，并且被硬控或生命比例不到 DANGER_HP。
const DANGER_NEAR: f64 = 60000.0;
const DANGER_HP: f64 = 0.45;
/// 狂暴：走向最近的队友（CHASE 内），到 LASH_REACH 内站住挥打；第一下在狂暴后 FIRST_SWING tick，攻击间隔读不到时 SWING。
const CHASE: f64 = 120000.0;
const LASH_REACH: f64 = 40000.0;
const FIRST_SWING: usize = 12;
const SWING: usize = 60;
const SWING_ANIM: u64 = 12;
/// 放不出技能的控制（她被控住时不放 W）；算「被硬控」的控制（league_milio 的表）。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];
const HARD: [CcKindV1; 6] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];
/// 同一句台词至少隔这么多 tick（主包的 vo_gap）。
const VO_GAP: usize = 600;

fn rn(name: &str) -> String {
    format!("{ID}_{name}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RENATA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_renata.log");
        }
    }
    PathBuf::from("league_renata.log")
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
const LOG_EVERY: usize = 50;

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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 印记的时长（日志用）。
    pub p_t: usize,
    /// 引爆：p_pop + p_pop_ap% 法强的魔法伤害，最大生命 p_pop_hp% 的真实伤害。
    pub p_pop: usize,
    pub p_pop_ap: usize,
    pub p_pop_hp: usize,
    /// 及时救难：冷却、时长、攻速、移速、找队友的距离、危急时的流失时长、她的施法动作。
    pub w_cd: usize,
    pub w_t: usize,
    pub w_as: usize,
    pub w_ms: usize,
    pub w_range: usize,
    pub w_r2: usize,
    pub fight_r: usize,
    pub w_anim: usize,
    pub w_doom: usize,
    /// 狂暴的时长（主包数据管；日志用）。
    pub r_t: usize,
    pub r_per: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_t: 240,
            p_pop: 30,
            p_pop_ap: 20,
            p_pop_hp: 3,
            w_cd: 1500,
            w_t: 300,
            w_as: 40,
            w_ms: 20,
            w_range: 80000,
            w_r2: 60000,
            fight_r: 70000,
            w_anim: 18,
            w_doom: 180,
            r_t: 105,
            r_per: 30,
        }
    }
}

/// `{"p_pop":30,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "p_t" => p.p_t = v,
            "p_pop" => p.p_pop = v,
            "p_pop_ap" => p.p_pop_ap = v,
            "p_pop_hp" => p.p_pop_hp = v,
            "w_cd" => p.w_cd = v,
            "w_t" => p.w_t = v,
            "w_as" => p.w_as = v,
            "w_ms" => p.w_ms = v,
            "w_range" => p.w_range = v,
            "w_r2" => p.w_r2 = v,
            "fight_r" => p.fight_r = v,
            "w_anim" => p.w_anim = v,
            "w_doom" => p.w_doom = v,
            "r_t" => p.r_t = v,
            "r_per" => p.r_per = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

/// 一个她这边的英雄（不算她）：id、位置、生命比例、被硬控没有。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Ally {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: f64,
    pub held: bool,
}

/// 危急：身边 DANGER_NEAR 内有敌方英雄，并且被硬控或生命比例不到 DANGER_HP。
pub fn in_danger(a: &Ally, enemies: &[(f64, f64)]) -> bool {
    enemies.iter().any(|e| dist(a.at, *e) <= DANGER_NEAR) && (a.held || a.hp < DANGER_HP)
}

/// 她在 `me`：`reach` 内危急的队友里生命比例最低的那个。
pub fn pick_bailout(me: (f64, f64), reach: f64, allies: &[Ally], enemies: &[(f64, f64)]) -> Option<usize> {
    allies
        .iter()
        .filter(|a| dist(me, a.at) <= reach && in_danger(a, enemies))
        .min_by(|a, b| a.hp.total_cmp(&b.hp))
        .map(|a| a.id)
}

/// 危急流失：每 tick 掉多少（最大生命在 `doom` tick 内掉光，至少 1）。
pub fn drain_step(max: usize, doom: usize) -> usize {
    (max / doom.max(1)).max(1)
}

/// 队友这次出手是哪种：普攻冷却跳起（Some(true)）、技能冷却跳起（Some(false)）、没出手（None）。冷却跳起 = 比上一 tick 多 5 以上。
pub fn swung(was: (usize, usize, usize, usize), now: (usize, usize, usize, usize)) -> Option<bool> {
    if now.0 > was.0 + 5 {
        Some(true)
    } else if now.1 > was.1 + 5 || now.2 > was.2 + 5 || now.3 > was.3 + 5 {
        Some(false)
    } else {
        None
    }
}

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buffs(sim, id).iter().any(|b| b.name() == name)
}

/// 身上有不是及时救难给的「不死」吗（基兰的符文、凯尔的大招等：让它们自己管）。
fn other_undying(sim: &StableSim<'_>, id: usize) -> bool {
    buffs(sim, id).iter().any(|b| b.undying && b.name() != W_BUFF)
}

fn cc_left(e: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> usize {
    (0..e.cc_count())
        .filter_map(|i| e.cc_at(i))
        .filter(|c| kinds.iter().any(|k| k.code() == c.kind))
        .map(|c| c.tick as usize)
        .max()
        .unwrap_or(0)
}

fn hp_share((now, max): (usize, usize)) -> f64 {
    if max > 0 {
        now as f64 / max as f64
    } else {
        1.0
    }
}

/// 某个英雄的玩家：(玩家 id, 击杀 + 助攻)。
fn takedowns(sim: &StableSim<'_>, champion: usize) -> Option<(usize, usize)> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find_map(|pl| {
        let c = pl.champion()?;
        (c.id() == champion).then(|| (pl.id(), pl.kills() + pl.assists()))
    })
}

/// 离 `at` 最近的、`team` 以外的活着的可选中单位（不算塔），`reach` 以内：(id, 是不是英雄)。
fn nearest_foe(sim: &StableSim<'_>, team: usize, at: (f64, f64), reach: f64) -> Option<(usize, bool)> {
    let mut best: Option<(usize, bool, f64)> = None;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        let d = dist(at, fpos(u.pos()));
        if d <= reach && best.is_none_or(|b| d < b.2) {
            best = Some((u.id(), u.is_champion(), d));
        }
    }
    best.map(|b| (b.0, b.1))
}

/// 离 `at` 最近的带印记的敌方英雄（`team` 以外），`reach` 以内。
fn nearest_marked(sim: &StableSim<'_>, team: usize, at: (f64, f64), reach: f64) -> Option<usize> {
    let mut best: Option<(usize, f64)> = None;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_champion() {
            continue;
        }
        let d = dist(at, fpos(u.pos()));
        if d <= reach && best.is_none_or(|b| d < b.1) && has_buff(sim, u.id(), MARK) {
            best = Some((u.id(), d));
        }
    }
    best.map(|b| b.0)
}

/// 狂暴的 `me` 最近的自己人（同队、活着、可选中、不是塔，英雄优先）：(id, 位置, 距离)，`reach` 以内。
fn nearest_friend(sim: &StableSim<'_>, me: usize, team: usize, at: (f64, f64), reach: f64) -> Option<(usize, (f64, f64), f64)> {
    let mut best: Option<(usize, (f64, f64), f64, bool)> = None;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.id() == me || u.team() != team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        let p = fpos(u.pos());
        let d = dist(at, p);
        if d > reach {
            continue;
        }
        let champ = u.is_champion();
        let better = match best {
            None => true,
            Some((_, _, bd, bc)) => (champ && !bc) || (champ == bc && d < bd),
        };
        if better {
            best = Some((u.id(), p, d, champ));
        }
    }
    best.map(|b| (b.0, b.1, b.2))
}

// ===================== 被动：杠杆（引爆、救难、狂暴） =====================

/// 一次及时救难：队友、他的玩家、结束的 tick，被救下后的流失（结束的 tick、击杀 + 助攻、最大生命）。
#[derive(Clone, Copy, Debug)]
struct Bail {
    ally: usize,
    until: usize,
    doom: Option<(usize, usize, usize)>,
}

#[derive(Clone, Default)]
struct Glasc {
    p: Params,
    /// 她这边各玩家上一 tick 的冷却（普攻、技能、技能 2、大招）。
    last_cd: HashMap<usize, (usize, usize, usize, usize)>,
    /// 等着算打中的出手：(队友, 敌方英雄, 第几 tick)。
    pending: Vec<(usize, usize, usize)>,
    /// W 好了的 tick；正在救的人。
    w_ready: usize,
    bail: Option<Bail>,
    /// 狂暴的敌方英雄 -> 下一下挥打的 tick。
    lash: HashMap<usize, usize>,
    /// 上次说 W 台词的 tick。
    vo_at: Option<usize>,
    was_alive: bool,
}

impl Glasc {
    /// 队友出手：冷却跳起来就记下他要打的带印记英雄，POP_WAIT tick 后还带着印记就引爆。
    fn ally_hits(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, now: usize) {
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            let pid = pl.id();
            let Some(c) = pl.champion() else { continue };
            if c.team() != team || c.id() == me {
                continue;
            }
            let Some(cd) = pl.cooldowns() else { continue };
            let was = self.last_cd.insert(pid, cd);
            let (Some(was), true) = (was, c.is_alive()) else { continue };
            let at = fpos(c.pos());
            let foe = match swung(was, cd) {
                Some(true) => match nearest_foe(sim, team, at, ATTACK_REACH) {
                    Some((f, true)) if has_buff(sim, f, MARK) => Some(f),
                    _ => None,
                },
                Some(false) => nearest_marked(sim, team, at, SKILL_REACH),
                None => None,
            };
            if let Some(f) = foe {
                if !self.pending.iter().any(|&(_, pf, _)| pf == f) {
                    self.pending.push((c.id(), f, now + POP_WAIT));
                }
            }
        }
        let due: Vec<(usize, usize, usize)> = self.pending.iter().copied().filter(|&(_, _, at)| at <= now).collect();
        self.pending.retain(|&(_, _, at)| at > now);
        for (ally, foe) in due.into_iter().map(|(a, f, _)| (a, f)) {
            if sim.get_entity(foe).is_some_and(|e| e.is_alive()) && has_buff(sim, foe, MARK) {
                self.pop(sim, me, foe, ally);
            }
        }
    }

    fn pop(&mut self, sim: &mut StableSim<'_>, me: usize, foe: usize, ally: usize) {
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let max = sim.get_entity(foe).map_or(0, |e| e.hp().1);
        let magic = self.p.p_pop + self.p.p_pop_ap * ap / 100;
        let fixed = (max * self.p.p_pop_hp / 100).max(1);
        sim.entity_remove_buff(foe, MARK);
        let a = sim.deal_damage_typed(me, foe, magic, DamageTypeV1::Ap, AttackTypeV1::Skill);
        let b = sim.deal_damage_typed(me, foe, fixed, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        let on = InputTargetV1::target(foe);
        sim.play_view_effect(&rn("p_pop"), me, &on, 0, 0, 0);
        sim.play_sfx(&rn("p_pop"), me, &on);
        if let Some(k) = counted("pop") {
            wlog(format!("{} POP #{k}: {} hit {} -> {magic} magic + {fixed} true{}", head(sim, me), who(sim, ally),
                         who(sim, foe), if a && b { "" } else { " (refused)" }));
        }
    }

    /// 及时救难：救着人时管流失和保命；没在救、W 好了时每 WATCH tick 找危急的队友。
    fn bailout(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, now: usize) {
        if let Some(b) = self.bail {
            self.bail = self.keep_bail(sim, me, b, now);
            return;
        }
        if now < self.w_ready || now % WATCH != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() || cc_left(&e, &NO_CAST) > 0 {
            return;
        }
        let at = fpos(e.pos());
        let mut allies = Vec::new();
        let mut enemies = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_champion() || !u.is_alive() {
                continue;
            }
            if u.team() != team {
                enemies.push(fpos(u.pos()));
            } else if u.id() != me {
                allies.push(Ally { id: u.id(), at: fpos(u.pos()), hp: hp_share(u.hp()), held: cc_left(&u, &HARD) > 0 });
            }
        }
        let Some(ally) = pick_bailout(at, self.p.w_range as f64, &allies, &enemies) else { return };
        let mut buff = BuffV1::timed(W_BUFF, self.p.w_t);
        buff.attack_speed_mult = self.p.w_as as i32;
        buff.move_speed_mult = self.p.w_ms as i32;
        buff.undying = true;
        sim.add_buff(ally, &buff);
        let on = InputTargetV1::target(ally);
        let at_me = InputTargetV1::target(me);
        sim.play_view_effect(&rn("w_cast"), me, &on, 0, 0, 0);
        sim.play_sfx(&rn("w"), me, &at_me);
        sim.play_sfx(&rn("w_buff"), me, &on);
        if self.vo_at.is_none_or(|t| now >= t + VO_GAP) {
            sim.play_sfx(&rn("vo_w"), me, &at_me);
            self.vo_at = Some(now);
        }
        let mut anim = CcV1::of_kind(CcKindV1::Animation, self.p.w_anim as u64);
        anim.set_name("skill_w");
        sim.apply_cc(me, &anim);
        self.w_ready = now + self.p.w_cd;
        self.bail = Some(Bail { ally, until: now + self.p.w_t, doom: None });
        if let Some(k) = counted("bailout") {
            let a = allies.iter().find(|a| a.id == ally).copied().unwrap_or_default();
            wlog(format!("{} BAILOUT #{k} on {} (hp {:.0}%{})", head(sim, me), who(sim, ally), a.hp * 100.0,
                         if a.held { ", held" } else { "" }));
        }
    }

    /// 一 tick 的救难：没出事到期就结束；受到致命伤害就回满、开始流失；流失中参与击杀就保住，到期没参与就阵亡。
    fn keep_bail(&mut self, sim: &mut StableSim<'_>, me: usize, mut b: Bail, now: usize) -> Option<Bail> {
        let (alive, (hp, max), at, team) = match sim.get_entity(b.ally) {
            Some(a) => (a.is_alive(), a.hp(), fpos(a.pos()), a.team()),
            None => return None,
        };
        if !alive {
            wlog(format!("{} BAILOUT ended: {} died anyway", head(sim, me), who(sim, b.ally)));
            return None;
        }
        let on = InputTargetV1::target(b.ally);
        match b.doom {
            None => {
                if now >= b.until {
                    if let Some(k) = counted("unused") {
                        wlog(format!("{} BAILOUT #{k} on {} ended unused", head(sim, me), who(sim, b.ally)));
                    }
                    return None;
                }
                if hp > 1 || other_undying(sim, b.ally) {
                    return Some(b);
                }
                // the lethal hit: full health that drains away over w_doom ticks, still undying meanwhile
                sim.entity_set_hp(b.ally, max);
                sim.entity_remove_buff(b.ally, W_BUFF);
                let mut buff = BuffV1::timed(W_BUFF, self.p.w_doom + 2);
                buff.attack_speed_mult = self.p.w_as as i32;
                buff.move_speed_mult = self.p.w_ms as i32;
                buff.undying = true;
                sim.add_buff(b.ally, &buff);
                sim.play_view_effect(&rn("w_save"), me, &on, 0, 0, 0);
                sim.play_sfx(&rn("w_save"), me, &on);
                let td = takedowns(sim, b.ally).map_or(0, |t| t.1);
                b.doom = Some((now + self.p.w_doom, td, max));
                if let Some(k) = counted("revive") {
                    wlog(format!("{} REVIVE #{k}: {} caught at 1 hp -> {max}, drains over {} ticks ({td} takedowns so far)",
                                 head(sim, me), who(sim, b.ally), self.p.w_doom));
                }
                Some(b)
            }
            Some((until, td, full)) => {
                let now_td = takedowns(sim, b.ally).map_or(0, |t| t.1);
                if now_td > td {
                    // a takedown: kept alive with what is left
                    sim.entity_remove_buff(b.ally, W_BUFF);
                    sim.play_view_effect(&rn("w_save"), me, &on, 0, 0, 0);
                    sim.play_sfx(&rn("w_save"), me, &on);
                    if let Some(k) = counted("saved") {
                        wlog(format!("{} SAVED #{k}: {} scored a takedown, keeps {hp}/{max}", head(sim, me), who(sim, b.ally)));
                    }
                    return None;
                }
                if now >= until {
                    sim.entity_remove_buff(b.ally, W_BUFF);
                    let killer = nearest_foe(sim, team, at, 200000.0).map_or(b.ally, |(f, _)| f);
                    let left = sim.get_entity(b.ally).map_or(hp, |e| e.hp().0);
                    sim.deal_damage_typed(killer, b.ally, left + 1000, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                    if let Some(k) = counted("doomed") {
                        wlog(format!("{} DOOMED #{k}: {} got no takedown, killed by {}", head(sim, me), who(sim, b.ally),
                                     who(sim, killer)));
                    }
                    return None;
                }
                sim.entity_set_hp(b.ally, hp.saturating_sub(drain_step(full, self.p.w_doom)).max(1));
                Some(b)
            }
        }
    }

    /// 狂暴的敌方英雄按自己的攻击间隔、用自己的攻击力打 LASH_REACH 内最近的自己人（走过去是 AI 钩子的事）。
    fn berserk(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, now: usize) {
        let mut mad = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() != team && u.is_alive() && u.is_champion() && has_buff(sim, u.id(), BERSERK) {
                mad.push(u.id());
            }
        }
        self.lash.retain(|id, _| mad.contains(id));
        for u in mad {
            let next = *self.lash.entry(u).or_insert(now + FIRST_SWING);
            if now < next {
                continue;
            }
            let Some(e) = sim.get_entity(u) else { continue };
            let (st, interval, at, side) = (e.stat(), e.attack_interval(), fpos(e.pos()), e.team());
            let Some((victim, _, _)) = nearest_friend(sim, u, side, at, LASH_REACH) else { continue };
            let theirs = sim.deal_damage_typed(u, victim, st.attack, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
            if !theirs {
                sim.deal_damage_typed(me, victim, st.attack, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
            }
            let mut anim = CcV1::of_kind(CcKindV1::Animation, SWING_ANIM);
            anim.set_name("attack");
            sim.apply_cc(u, &anim);
            sim.play_view_effect(&rn("r_lash_hit"), me, &InputTargetV1::target(victim), 0, 0, 0);
            self.lash.insert(u, now + if interval > 0 { interval } else { SWING });
            if let Some(k) = counted("lash") {
                wlog(format!("{} LASH #{k}: berserk {} hits its own {} for {} ({}){}", head(sim, me), who(sim, u),
                             who(sim, victim), st.attack, if theirs { "its own hit" } else { "credited to her" },
                             if interval > 0 { String::new() } else { format!(", interval unknown -> {SWING}") }));
            }
        }
    }
}

impl StablePassive for Glasc {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        if self.p != p {
            if let Some(k) = counted("params") {
                wlog(format!("params {params_json} -> {p:?} #{k}"));
            }
            self.p = p;
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team) = (e.is_alive(), e.team());
        let now = sim.tick();
        if alive != self.was_alive {
            if let Some(k) = counted("life") {
                wlog(format!("{} {} #{k}", head(sim, me), if alive { "ALIVE" } else { "DEAD" }));
            }
            self.was_alive = alive;
        }
        self.ally_hits(sim, me, team, now);
        self.bailout(sim, me, team, now);
        self.berserk(sim, me, team, now);
    }
}

// ===================== AI 钩子：狂暴的人走向自己人 =====================

/// 所有玩家都问：英雄身上有狂暴，就走向 CHASE 内最近的自己人，到 LASH_REACH 内站住（挥打是被动做的）；没有就不管。
#[derive(Clone, Default)]
struct Frenzy {
    last_log: Option<usize>,
}

impl StablePlayerAi for Frenzy {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:berserk")
    }

    fn priority(&self) -> i32 {
        1_000_000
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, _base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let sim = ctx.sim()?;
        let me = sim.get_player(player)?.champion()?;
        if !me.is_alive() || !has_buff(&sim, me.id(), BERSERK) {
            return None;
        }
        let at = fpos(me.pos());
        let (friend, to, d) = nearest_friend(&sim, me.id(), me.team(), at, CHASE)?;
        let now = sim.tick();
        if self.last_log.is_none_or(|t| now >= t + 60) {
            self.last_log = Some(now);
            if let Some(k) = counted("chase") {
                wlog(format!("{} BERSERK #{k}: {} goes for its own {} ({d:.0} away)", head(&sim, me.id()),
                             who(&sim, me.id()), who(&sim, friend)));
            }
        }
        if d <= LASH_REACH {
            Some(InputV1::move_to(at.0 as u64, at.1 as u64))
        } else {
            Some(InputV1::move_to(to.0 as u64, to.1 as u64))
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
        "=== {ID} v{VERSION} (Renata: Leverage popped by allies' hits, League's Bailout, a real berserk) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:glasc"), Glasc::default());
    module.add_player_input_ai(Frenzy::default());
    host.log(LogLevel::Info, "league_renata loaded (Leverage popped by allies' hits, League's Bailout, a real berserk).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"p_pop":40,"junk":7,"w_doom":120,"w_cd":900,"fight_r":65000}"#);
        assert_eq!((p.p_pop, p.w_doom, p.w_cd, p.fight_r), (40, 120, 900, 65000));
    }

    #[test]
    fn the_copy_carries_the_default_params() {
        let copy = include_str!("../override/league_renata.data_champion");
        let at = copy.find("\"passive_ref\": \"league_renata:glasc\"").expect("no league_renata:glasc passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("p_t", d.p_t), ("p_pop", d.p_pop), ("p_pop_ap", d.p_pop_ap), ("p_pop_hp", d.p_pop_hp),
                       ("w_cd", d.w_cd), ("w_t", d.w_t), ("w_as", d.w_as), ("w_ms", d.w_ms), ("w_range", d.w_range),
                       ("w_r2", d.w_r2), ("fight_r", d.fight_r), ("w_anim", d.w_anim), ("w_doom", d.w_doom),
                       ("r_t", d.r_t), ("r_per", d.r_per)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in [MARK, W_BUFF, BERSERK] {
            assert!(copy.contains(&format!("\"name\": \"{name}\"")), "the copy has no {name}");
        }
        assert!(!copy.contains("league_renata_w_bolt"), "the copy still casts the data's Bailout");
        assert!(!copy.contains("league_renata_p_probe"), "the copy still pops the mark in data");
    }

    #[test]
    fn bailout_goes_to_the_ally_in_most_danger() {
        let me = (0.0, 0.0);
        let enemy = [(30000.0, 0.0)];
        let low = Ally { id: 1, at: (20000.0, 0.0), hp: 0.30, held: false };
        let lower_far = Ally { id: 2, at: (90000.0, 0.0), hp: 0.10, held: false };
        let held = Ally { id: 3, at: (25000.0, 5000.0), hp: 0.80, held: true };
        let fine = Ally { id: 4, at: (10000.0, 0.0), hp: 0.90, held: false };
        assert_eq!(pick_bailout(me, 80000.0, &[low, lower_far, held, fine], &enemy), Some(1));
        assert_eq!(pick_bailout(me, 80000.0, &[held, fine], &enemy), Some(3));
        assert_eq!(pick_bailout(me, 80000.0, &[fine], &enemy), None);
        // nobody near an enemy champion: no Bailout
        assert_eq!(pick_bailout(me, 80000.0, &[low], &[(200000.0, 0.0)]), None);
    }

    #[test]
    fn the_drain_empties_the_bar_in_time() {
        assert_eq!(drain_step(1800, 180), 10);
        assert_eq!(drain_step(100, 180), 1);
        assert_eq!(drain_step(1000, 0), 1000);
    }

    #[test]
    fn an_ally_swings_when_a_cooldown_jumps() {
        assert_eq!(swung((0, 0, 0, 0), (60, 0, 0, 0)), Some(true));
        assert_eq!(swung((10, 0, 0, 0), (9, 0, 0, 0)), None);
        assert_eq!(swung((0, 0, 0, 0), (0, 300, 0, 0)), Some(false));
        assert_eq!(swung((0, 0, 0, 4), (0, 0, 0, 3000)), Some(false));
        assert_eq!(swung((5, 5, 5, 5), (9, 9, 9, 9)), None);
    }
}
