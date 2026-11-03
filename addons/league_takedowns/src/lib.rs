//! 参与击杀附加包：金克丝、崔丝塔娜、易的「击杀后」效果照英雄联盟算每一次参与击杀（击杀和助攻），易还有普攻减 Q 冷却、
//! 大招免疫减速（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据，只认得出她（他）自己打出的最后一击（league_jinx 的击杀检查），助攻看不见。`mod.override_info` 把三人换成
//! `override/` 里的副本（`make_override.py` 从主包生成），各挂本包的一个被动：
//!
//! - **金克丝 `league_takedowns:jinx`**：每一次英雄击杀和助攻都给「罪恶快感」——主包的四个 buff（攻速、三段移速，名字和
//!   数字照主包，`make_override.py` 核对），播主包的画面和音效。副本去掉数据里的击杀检查（不然她自己的击杀算两次）。
//!   v0.5.0（用户 2026-11-03：「金克丝刷新被动后少了点跑步的加速动作？」）：罪恶快感的前两档移速还在时，她跑起来播图里的
//!   冲刺跑 `run_x`（步频快 1.67 倍、上身前倾、身后两道残影），本包在显示世界里换动画名（`view.rs`）。
//! - **崔丝塔娜 `league_takedowns:tristana`**：每一次英雄击杀和助攻都刷新火箭跳跃（去掉主包的冷却标记 `league_tristana_w_cd`，
//!   播主包的「就绪」画面）。主包自己的击杀检查留着（同一个标记，去两次也一样）。
//! - **易 `league_takedowns:masteryi`**：每一次英雄击杀和助攻，阿尔法突袭和冥想（无极剑道）的剩余冷却减 `YI_CUT`%；
//!   无极剑道开着时再延长 `YI_EXTEND` tick。他每次普攻，阿尔法突袭冷却减 `YI_ATTACK_CUT` tick。无极剑道期间身上的
//!   减速都去掉（免疫减速）。副本的无极剑道去掉主包近似用的「冷却加快 40%」。
//!   v0.3.2（用户 2026-10-26：「剑圣会无限Q？」）：「普攻」原来用 `on_attack` 数，可它连技能的每一下伤害都算（接口说明：
//!   `on_attack` also fires for skills）——Q 的每一斩、E 的真实伤害、R 期间的每一下都在减 Q 的冷却，一次 Q 自己就把冷却
//!   减没了。现在只认真正的普攻：每 tick 看普攻栏的冷却，冷却变长（刚打出一下普攻，`attack_went_out`）才减；
//!   Q 在数据里是 BaseAttack 类型，也不算（它走的是技能栏的冷却）。每次减记一行 `YI ATTACK`（预模拟限量，见下面的日志）。
//!   v0.4.0（用户 2026-11-03：「剑圣的w满血时候会释放 这个也改一下」）：副本的技能 2 只剩无极剑道，W 冥想由本包照英雄联盟
//!   单独放——身边有敌方英雄、生命低于一半或一秒内掉了四分之一时才盘腿（`should_meditate`），自己 20 秒冷却，画面和数字照主包。
//!   每次记一行 `YI MEDITATE`。
//!
//! - **图奇 `league_takedowns:twitch`**：英雄联盟里身上有毒的敌方英雄死了就刷新埋伏。主包只认他自己的击杀（击杀检查留着），
//!   本包补上助攻：清掉 Q 的剩余冷却（`entity_reduce_cooldown`），播主包的刷新画面和声音（`TWITCH_RESET`）。
//!   v0.3.0 起 E「毒性爆发」照英雄联盟等时机：主包在他最近打中英雄 3 次后的下一下就引爆。副本里每一层毒旁边多调用
//!   原生效果 `league_takedowns:twitch_venom`，在中毒的英雄身上数层数（`TWITCH_VENOM`，最多 6 层）；引爆的那 5 处检查改读
//!   `TWITCH_E_GO`：有人满 6 层、或这一爆能毒死人（每层 6 + 16% 攻击力的物理伤害，按护甲折算）时本包才挂上。引爆本身还是
//!   主包的（每层毒各结算一次），看到主包的爆发标记就把层数清零。v0.3.1：那 5 处只在固定时刻读（W 落地后 68 tick、R 最后
//!   30 tick、连招冷却里的 W 键），标记那时多半没挂，游戏里 E 几乎不爆（10-24 的日志 1080 次 GO 都没被读走）；副本的每次普攻也读它，挂上后的下一箭就引爆。
//!   每次引爆记一行 `TWITCH E POP`。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_takedowns.log`，每次启动游戏重写：你看的那场（观战、回放）
//! 每一行都记；服务端的预模拟（每次启动几百场，每场的被动都是新的）每种先记 `LOG_FIRST` 行、之后每 `LOG_EVERY` 行记一行
//! （整个游戏一个计数：原来记在被动里的「前 40 行」「前 80 行」每场都从头数，2026-10-30 的 1.47 MB 里一半是 `YI ATTACK`）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_takedowns";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_takedowns") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 金克丝「罪恶快感」：主包的四个 buff（名字、持续 tick、攻速 %、移速 %）。
pub const JINX_EXCITED: [(&str, usize, i32, i32); 4] = [
    ("league_jinx_excited", 360, 25, 0),
    ("league_jinx_excited_ms1", 120, 0, 40),
    ("league_jinx_excited_ms2", 240, 0, 30),
    ("league_jinx_excited_ms3", 360, 0, 30),
];
pub const JINX_VIEW: &str = "league_jinx_excited";
/// 崔丝塔娜火箭跳跃的冷却标记和「就绪」画面。
pub const TRIS_W_CD: &str = "league_tristana_w_cd";
pub const TRIS_READY: &str = "league_tristana_w_ready";
/// 图奇埋伏刷新的画面和声音（主包同名）；一次减掉的冷却（比 Q 的 900 tick 长就是清零）。
pub const TWITCH_RESET: &str = "league_twitch_q_reset";
pub const TWITCH_CUT: usize = 3_600;
/// 图奇的毒层（记在每个英雄身上，最多 6 层，6 秒）、毒性爆发的旗子、冷却标记、爆发中的标记（主包同名）、距离和每层伤害。
pub const TWITCH_VENOM: [&str; 6] = ["league_takedowns_tw_v1", "league_takedowns_tw_v2", "league_takedowns_tw_v3",
                                     "league_takedowns_tw_v4", "league_takedowns_tw_v5", "league_takedowns_tw_v6"];
pub const TWITCH_VENOM_LIFE: usize = 360;
pub const TWITCH_E_GO: &str = "league_takedowns_tw_e_go";
pub const TWITCH_E_CD: &str = "league_twitch_e_cd";
pub const TWITCH_E_POP: &str = "league_twitch_e_pop";
pub const TWITCH_E_REACH: u64 = 120_000;
pub const TWITCH_E_BASE: usize = 6;
pub const TWITCH_E_AD: usize = 16;
/// 易：无极剑道的 buff，参与击杀减剩余冷却 %，延长 tick，普攻减 Q 冷却 tick。
pub const YI_HIGHLANDER: &str = "league_masteryi_highlander";
pub const YI_CUT: usize = 70;
pub const YI_EXTEND: usize = 240;
pub const YI_ATTACK_CUT: usize = 60;
/// 易的冥想（v0.4.0，用户 2026-11-03：「剑圣的w满血时候会释放 这个也改一下」）。主包把 W 冥想并进了 E 无极剑道（技能 2），
/// 游戏的 AI 放给自己回血的技能不看生命、好了就放（champion-data：「A heal on the caster is cast whenever it is ready」），所以
/// 一开打满血也先盘腿 0.75 秒；只按生命挡住冥想也不行，开打时技能 2 已经交了，真残血时它还在冷却。副本的技能 2 只剩无极剑道
/// （立刻生效），冥想由本包照英雄联盟单独放：身边 `YI_MED_NEAR` 内有敌方英雄，生命低于 `YI_MED_HP` 或 `YI_MED_WINDOW` tick
/// 内掉了最大生命的 `YI_MED_BURST`，冥想自己的冷却 `YI_MED_CD` 好了，没被控、不在出手中（参与击杀也减它剩余冷却的 `YI_CUT`%）。
/// 画面、数字照主包（`make_override.py` 核对）：盘腿 `YI_MED_ANIM` tick（`skill2` 动作），`YI_MEDITATE` buff `YI_MED_T` tick
/// 受到的伤害降低 `YI_MED_REDUCE`%，之后每 `YI_MED_PULSE` tick 回复 `YI_MED_HEAL` + `YI_MED_HEAL_AD`% 攻击力、共 `YI_MED_PULSES` 次。
pub const YI_MEDITATE: &str = "league_masteryi_meditate";
pub const YI_MED_ANIM: u64 = 45;
pub const YI_MED_T: usize = 60;
pub const YI_MED_REDUCE: usize = 40;
pub const YI_MED_PULSE: usize = 30;
pub const YI_MED_PULSES: usize = 4;
pub const YI_MED_HEAL: usize = 5;
pub const YI_MED_HEAL_AD: usize = 3;
pub const YI_MED_HP: f64 = 0.5;
pub const YI_MED_BURST: f64 = 0.25;
pub const YI_MED_WINDOW: usize = 60;
pub const YI_MED_NEAR: f64 = 60_000.0;
pub const YI_MED_CD: usize = 1_200;
/// 主包冥想的画面和声音。
pub const YI_MED_VIEW: &str = "league_masteryi_w_aura";
pub const YI_MED_SFX: &str = "league_masteryi_w_cast";
/// 放不出技能的控制，和出手中（动作还在播、被强制位移）。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TAKEDOWNS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_takedowns.log");
        }
    }
    PathBuf::from("league_takedowns.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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

/// Lines of each kind a launch: the server's presims (hundreds a launch, each with new passives - a count in the passive
/// counts one sim) the first `LOG_FIRST`, then every `LOG_EVERY`-th; the match on screen all of them.
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count this launch when it is to be written (`shown`: the match on screen).
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
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

// ===================== 小工具 =====================

fn buff_left(sim: &StableSim<'_>, id: usize, name: &str) -> Option<usize> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).map(|b| {
        if BuffDurationV1::from_code(b.duration_kind) == Some(BuffDurationV1::Time) { b.duration_tick } else { usize::MAX }
    }).max()
}

fn remaining(sim: &StableSim<'_>, id: usize, slot: SkillSlotV1) -> usize {
    sim.get_entity(id).and_then(|e| e.cooldown(slot)).map_or(0, |c| c.remaining)
}

/// `pct`% of the remaining cooldown off (rounded down).
pub fn cut(left: usize, pct: usize) -> usize {
    left * pct / 100
}

fn victim_is_champion(sim: &StableSim<'_>, victim: usize) -> bool {
    sim.get_entity(victim).is_some_and(|v| v.is_champion())
}

// ===================== 金克丝 =====================

#[derive(Clone, Default)]
struct Jinx {
    n: usize,
}

impl Jinx {
    fn excite(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        for (name, ticks, attack_speed, move_speed) in JINX_EXCITED {
            sim.entity_remove_buff(me, name);
            let mut b = BuffV1::timed(name, ticks);
            b.attack_speed_mult = attack_speed;
            b.move_speed_mult = move_speed;
            sim.add_buff(me, &b);
        }
        let at = InputTargetV1::target(me);
        sim.play_view_effect(JINX_VIEW, me, &at, 0, 0, 0);
        sim.play_sfx(JINX_VIEW, me, &at);
        self.n += 1;
        if tally(sim, "jinx excited").is_some() {
            wlog(format!("{} JINX EXCITED #{} ({why})", head(sim, me), self.n));
        }
    }
}

impl StablePassive for Jinx {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if tally(sim, "jinx spawn").is_some() {
            wlog(format!("{} SPAWN: the add-on's Jinx (player {player})", head(sim, me)));
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if victim_is_champion(sim, victim) {
            self.excite(sim, me, &format!("killed #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.excite(sim, me, "assist");
    }
}

// ===================== 崔丝塔娜 =====================

#[derive(Clone, Default)]
struct Tristana {
    n: usize,
}

impl Tristana {
    fn reset(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        if sim.entity_remove_buff(me, TRIS_W_CD) > 0 {
            sim.play_view_effect(TRIS_READY, me, &InputTargetV1::target(me), 0, 0, 0);
        }
        self.n += 1;
        if tally(sim, "tristana reset").is_some() {
            wlog(format!("{} TRISTANA W RESET #{} ({why})", head(sim, me), self.n));
        }
    }
}

impl StablePassive for Tristana {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if tally(sim, "tristana spawn").is_some() {
            wlog(format!("{} SPAWN: the add-on's Tristana (player {player})", head(sim, me)));
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if victim_is_champion(sim, victim) {
            self.reset(sim, me, &format!("killed #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.reset(sim, me, "assist");
    }
}

// ===================== 图奇 =====================

/// Venom stacks on a champion after one more (League caps them at 6).
pub fn venom_after(n: usize) -> usize {
    (n + 1).min(TWITCH_VENOM.len())
}

/// Contaminate now? `foes` (stacks, hp + shield, armour); `per` the physical damage of one stack before armour.
pub fn contaminate(foes: &[(usize, usize, usize)], per: usize) -> bool {
    foes.iter().any(|&(n, hp, def)| n >= TWITCH_VENOM.len() || (n > 0 && n * per * 100 / (100 + def) >= hp))
}

fn venom_of(e: &StableEntity<'_, '_>) -> usize {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i))
        .filter_map(|b| TWITCH_VENOM.iter().position(|n| b.name() == *n)).map(|k| k + 1).max().unwrap_or(0)
}

/// Data calls this next to every venom layer it puts on a unit (`input` = that unit): one more stack on a champion.
struct Venom;

impl StableEffectType for Venom {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, _caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let id = input.target_id;
        let Some(n) = sim.get_entity(id).filter(|e| e.is_champion() && e.is_alive()).map(|e| venom_of(&e)) else { return };
        for b in TWITCH_VENOM {
            sim.entity_remove_buff(id, b);
        }
        sim.add_buff(id, &BuffV1::timed(TWITCH_VENOM[venom_after(n) - 1], TWITCH_VENOM_LIFE));
    }
}

#[derive(Clone, Default)]
struct Twitch {
    n: usize,
    pops: usize,
    bursts: usize,
    bursting: bool,
}

impl StablePassive for Twitch {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if tally(sim, "twitch spawn").is_some() {
            wlog(format!("{} SPAWN: the add-on's Twitch (player {player})", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me).filter(|e| e.is_alive()) else { return };
        let (team, attack) = (e.team(), e.stat().attack);
        let has = |name: &str| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name);
        let (popping, ready, going) = (has(TWITCH_E_POP), !has(TWITCH_E_CD), has(TWITCH_E_GO));
        let reach = TWITCH_E_REACH * TWITCH_E_REACH;
        let foes: Vec<(usize, usize, usize, usize)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive() && u.team() != team && sim.distance_sq(me, u.id()) <= reach)
            .map(|u| (u.id(), venom_of(&u), u.hp().0 + u.shield(), u.stat().defence))
            .collect();
        if popping {
            if !self.bursting {
                self.bursts += 1;
                if tally(sim, "twitch pop").is_some() {
                    wlog(format!("{} TWITCH E POP #{}: stacks {:?}", head(sim, me), self.bursts,
                                 foes.iter().map(|f| f.1).collect::<Vec<_>>()));
                }
            }
            self.bursting = true;
            // the data's Contaminate resolves every layer now: the counts start over
            for f in foes.iter().filter(|f| f.1 > 0) {
                for b in TWITCH_VENOM {
                    sim.entity_remove_buff(f.0, b);
                }
            }
            return;
        }
        self.bursting = false;
        let per = TWITCH_E_BASE + attack * TWITCH_E_AD / 100;
        let list: Vec<(usize, usize, usize)> = foes.iter().map(|f| (f.1, f.2, f.3)).collect();
        if ready && !going && contaminate(&list, per) {
            sim.add_buff(me, &BuffV1::timed(TWITCH_E_GO, 30));
            self.pops += 1;
            if tally(sim, "twitch go").is_some() {
                let top = foes.iter().max_by_key(|f| f.1).map_or(0, |f| f.1);
                wlog(format!("{} TWITCH E GO #{}: stacks {:?}, most {top}, {per} a stack", head(sim, me), self.pops,
                             foes.iter().map(|f| f.1).collect::<Vec<_>>()));
            }
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        let left = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill)).map(|c| c.remaining).unwrap_or(0);
        if left == 0 {
            return;
        }
        sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, TWITCH_CUT);
        sim.play_view_effect(TWITCH_RESET, me, &InputTargetV1::target(me), 0, 0, 0);
        sim.play_sfx(TWITCH_RESET, me, &InputTargetV1::target(me));
        self.n += 1;
        if tally(sim, "twitch reset").is_some() {
            wlog(format!("{} TWITCH Q RESET #{} (assist, {left} ticks left)", head(sim, me), self.n));
        }
    }
}

// ===================== 易 =====================

#[derive(Clone, Default)]
struct MasterYi {
    n: usize,
    /// the attack slot's remaining cooldown last tick (None: not read yet)
    atk_prev: Option<usize>,
    cuts: usize,
    /// his health share over the last `YI_MED_WINDOW` ticks (tick, share); Meditate's own cooldown (the tick it is
    /// ready); the ticks its heals are due; how many he meditated
    hp_seen: std::collections::VecDeque<(usize, f64)>,
    med_ready: usize,
    med_heals: Vec<usize>,
    meds: usize,
}

/// A real auto attack went out this tick: the attack slot's cooldown grew (it only shrinks otherwise).
pub fn attack_went_out(prev: Option<usize>, now: usize) -> bool {
    prev.is_some_and(|p| now > p)
}

/// Meditate now: an enemy champion near (`foe_near`), its own cooldown over (`ready`), not controlled or in an action
/// (`free`), and hurt - below `YI_MED_HP` of his health, or `YI_MED_BURST` of it lost since `peak` (his highest share
/// over the last `YI_MED_WINDOW` ticks). At full health: never (the 11-03 report).
pub fn should_meditate(hp: f64, peak: f64, foe_near: bool, ready: bool, free: bool) -> bool {
    ready && free && foe_near && (hp < YI_MED_HP || peak - hp >= YI_MED_BURST)
}

fn has_cc(e: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
}

fn foe_champion_within(sim: &StableSim<'_>, me: usize, team: usize, at: (u64, u64), reach: f64) -> bool {
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|u| {
        if u.id() == me || u.team() == team || !u.is_champion() || !u.is_alive() || !u.is_targetable() {
            return false;
        }
        let (x, y) = u.pos();
        ((x as f64 - at.0 as f64).powi(2) + (y as f64 - at.1 as f64).powi(2)).sqrt() <= reach
    })
}

impl MasterYi {
    fn takedown(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let (q, w) = (remaining(sim, me, SkillSlotV1::Skill), remaining(sim, me, SkillSlotV1::Skill2));
        if q > 0 {
            sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, cut(q, YI_CUT));
        }
        if w > 0 {
            sim.entity_reduce_cooldown(me, SkillSlotV1::Skill2, cut(w, YI_CUT));
        }
        // Meditate is his own W now (League: a takedown cuts every basic ability)
        let now = sim.tick();
        if self.med_ready > now {
            self.med_ready -= cut(self.med_ready - now, YI_CUT);
        }
        let extended = match buff_left(sim, me, YI_HIGHLANDER) {
            Some(left) if left != usize::MAX => {
                // the copy's Highlander: the main pack's speeds, no cooldown share; made again, YI_EXTEND longer
                let mut b = BuffV1::timed(YI_HIGHLANDER, left + YI_EXTEND);
                let e = sim.get_entity(me);
                if let Some(old) = e.and_then(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == YI_HIGHLANDER)) {
                    b.attack_speed_mult = old.attack_speed_mult;
                    b.move_speed_mult = old.move_speed_mult;
                }
                sim.entity_remove_buff(me, YI_HIGHLANDER);
                sim.add_buff(me, &b);
                true
            }
            _ => false,
        };
        self.n += 1;
        if tally(sim, "yi takedown").is_some() {
            wlog(format!("{} YI TAKEDOWN #{} ({why}): Q {q} -> {}, W {w} -> {}{}", head(sim, me), self.n, q - cut(q, YI_CUT),
                         w - cut(w, YI_CUT), if extended { ", Highlander extended" } else { "" }));
        }
    }

    /// Meditate (League's W, the add-on's since v0.4.0): its heals as they fall due, then whether to sit down now
    /// ([`should_meditate`]); the picture, the damage cut and the heals are the main pack's.
    fn meditate(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, (hp, max), at, team, ad) = (e.is_alive(), e.hp(), e.pos(), e.team(), e.stat().attack);
        let free = !has_cc(&e, &NO_CAST) && !has_cc(&e, &BUSY);
        // a new match (the tick went back) or a death: nothing carries over
        if !alive || self.hp_seen.back().is_some_and(|&(t, _)| t > now) {
            self.hp_seen.clear();
            self.med_heals.clear();
            if alive {
                self.med_ready = 0;
            } else {
                return;
            }
        }
        let due = self.med_heals.iter().filter(|&&t| t <= now).count();
        if due > 0 {
            self.med_heals.retain(|&t| t > now);
            sim.heal(me, me, (YI_MED_HEAL + ad * YI_MED_HEAL_AD / 100) * due);
        }
        let share = if max > 0 { hp as f64 / max as f64 } else { 1.0 };
        self.hp_seen.push_back((now, share));
        while self.hp_seen.front().is_some_and(|&(t, _)| t + YI_MED_WINDOW < now) {
            self.hp_seen.pop_front();
        }
        let peak = self.hp_seen.iter().map(|&(_, s)| s).fold(share, f64::max);
        // the enemy look only when the rest says yes
        if !should_meditate(share, peak, true, now >= self.med_ready, free)
            || !foe_champion_within(sim, me, team, at, YI_MED_NEAR)
        {
            return;
        }
        let mut sit = CcV1::of_kind(CcKindV1::Animation, YI_MED_ANIM);
        sit.set_name("skill2");
        sim.apply_cc(me, &sit);
        let mut buff = BuffV1::timed(YI_MEDITATE, YI_MED_T);
        buff.damaged_reduce = YI_MED_REDUCE;
        sim.entity_remove_buff(me, YI_MEDITATE);
        sim.add_buff(me, &buff);
        let on = InputTargetV1::target(me);
        sim.play_view_effect(YI_MED_VIEW, me, &on, 0, 0, 0);
        sim.play_sfx(YI_MED_SFX, me, &on);
        self.med_heals = (1..=YI_MED_PULSES).map(|k| now + k * YI_MED_PULSE).collect();
        self.med_ready = now + YI_MED_CD;
        self.meds += 1;
        if tally(sim, "yi meditate").is_some() {
            wlog(format!("{} YI MEDITATE #{}: health {:.0}% (highest {:.0}% in the last {YI_MED_WINDOW} ticks)",
                         head(sim, me), self.meds, share * 100.0, peak * 100.0));
        }
    }
}

impl StablePassive for MasterYi {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if tally(sim, "yi spawn").is_some() {
            wlog(format!("{} SPAWN: the add-on's Master Yi (player {player})", head(sim, me)));
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if victim_is_champion(sim, victim) {
            self.takedown(sim, me, &format!("killed #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.takedown(sim, me, "assist");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.meditate(sim, me);
        // every real auto attack: Alpha Strike's cooldown YI_ATTACK_CUT shorter (not his skills' hits, v0.3.2)
        let atk = remaining(sim, me, SkillSlotV1::Attack);
        if attack_went_out(self.atk_prev, atk) {
            let q = remaining(sim, me, SkillSlotV1::Skill);
            if q > 0 {
                sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, YI_ATTACK_CUT);
                self.cuts += 1;
                if tally(sim, "yi attack").is_some() {
                    wlog(format!("{} YI ATTACK #{}: Q {q} -> {}", head(sim, me), self.cuts, q.saturating_sub(YI_ATTACK_CUT)));
                }
            }
        }
        self.atk_prev = Some(atk);
        if buff_left(sim, me, YI_HIGHLANDER).is_none() {
            return;
        }
        // Highlander: immune to slows (every buff on him that lowers his move speed goes) - not the game's own permanent
        // `sed_` buffs (sed_reward), which are no slow (league_sejuani 0.1.1's `is_slow`)
        let slows: Vec<String> = match sim.get_entity(me) {
            Some(e) => (0..e.buff_count()).filter_map(|i| e.buff_at(i))
                .filter(|b| b.move_speed_mult < 0 && !b.name().starts_with("sed_"))
                .map(|b| b.name().to_string()).collect(),
            None => return,
        };
        for name in slows {
            sim.entity_remove_buff(me, &name);
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Jinx, Tristana, Master Yi and Twitch on every takedown) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:jinx"), Jinx::default());
    module.add_native_passive(format!("{ID}:tristana"), Tristana::default());
    module.add_native_passive(format!("{ID}:masteryi"), MasterYi::default());
    module.add_native_passive(format!("{ID}:twitch"), Twitch::default());
    module.add_native_effect(format!("{ID}:twitch_venom"), Venom);
    view::install_once();
    host.log(LogLevel::Info, "league_takedowns v1 loaded (Jinx, Tristana and Master Yi on every takedown).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn twitch_pops_at_six_or_for_a_kill() {
        assert_eq!(venom_after(5), 6);
        assert_eq!(venom_after(6), 6);
        assert!(!contaminate(&[(3, 1000, 0)], 50));
        assert!(contaminate(&[(6, 5000, 0)], 50));
        assert!(contaminate(&[(3, 140, 0)], 50));
        assert!(!contaminate(&[(3, 140, 100)], 50));
        assert!(!contaminate(&[(0, 0, 0)], 50));
    }

    #[test]
    fn a_takedown_cuts_most_of_what_is_left() {
        assert_eq!(cut(400, YI_CUT), 280);
        assert_eq!(cut(0, YI_CUT), 0);
    }

    #[test]
    fn only_a_real_auto_attack_cuts_alpha_strike() {
        assert!(!attack_went_out(None, 48), "the first look only notes the cooldown");
        assert!(attack_went_out(Some(0), 48), "ready, then swung");
        assert!(attack_went_out(Some(3), 48), "swung again just before it was ready");
        assert!(!attack_went_out(Some(48), 47), "cooling down");
        assert!(!attack_went_out(Some(0), 0), "ready, no swing (his Q's and E's hits never touch the attack slot)");
    }

    #[test]
    fn the_names_fit() {
        for (n, ..) in JINX_EXCITED {
            assert!(n.len() <= BUFF_NAME_CAP);
        }
        assert!(YI_HIGHLANDER.len() <= BUFF_NAME_CAP);
        assert!(YI_MEDITATE.len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn yi_meditates_only_when_hurt_in_a_fight() {
        // 「剑圣的w满血时候会释放」: at full health, never
        assert!(!should_meditate(1.0, 1.0, true, true, true));
        assert!(!should_meditate(0.8, 0.9, true, true, true), "a scratch");
        // low, or a burst
        assert!(should_meditate(0.45, 0.45, true, true, true));
        assert!(should_meditate(0.7, 0.95, true, true, true), "a quarter gone within the window");
        // but only with an enemy champion near, its cooldown over, and free to sit down
        assert!(!should_meditate(0.3, 0.3, false, true, true));
        assert!(!should_meditate(0.3, 0.3, true, false, true));
        assert!(!should_meditate(0.3, 0.3, true, true, false));
    }

    #[test]
    fn meditate_matches_the_main_pack() {
        // the copy's Meditate is the add-on's: the main pack's skill2 must still carry these numbers (make_override.py
        // checks them too, against these constants)
        let src = include_str!("../../../league/champion/league_masteryi.data_champion");
        let s2 = &src[src.find("\"action_name\": \"skill2\"").expect("skill2")..];
        let s2 = &s2[..s2.find("\"action_name\": \"ult\"").unwrap_or(s2.len())];
        assert!(s2.contains(&format!("\"duration\": {YI_MED_ANIM}")));
        assert!(s2.contains(&format!("\"name\": \"{YI_MEDITATE}\"")) && s2.contains(&format!("\"damaged_reduce\": {YI_MED_REDUCE}")));
        assert!(s2.contains(&format!("\"period\": {YI_MED_PULSE}")) && s2.contains(&format!("\"duration\": {}", YI_MED_PULSE * YI_MED_PULSES)));
        assert!(s2.contains(&format!("\"amount\": {YI_MED_HEAL}")) && s2.contains(&format!("\"attack_ratio\": {YI_MED_HEAL_AD}")));
        assert!(s2.contains(YI_MED_VIEW) && s2.contains(YI_MED_SFX));
    }

    #[test]
    fn presim_lines_are_capped_for_the_launch_and_the_match_on_screen_is_not() {
        // one count for every sim of the launch (the passives' own counts started over in every presim)
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }
}
