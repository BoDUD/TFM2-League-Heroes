//! 阿克尚扩展包（用户 2026-10-18：「技能方案按 A 做（带扩展包）」「大招改rust也做不了吗」「做成复活队友的吧 游戏更新你就做动态寻址
//! 方便自动找」）。主包保持纯数据；`mod.override_info` 把主包的阿克尚换成 `override/` 里的副本（`make_override.py` 用
//! tools/kit/build_akshan.py 的 `native=1` 生成），本包补数据做不到的几件事：
//!
//! - **无所不用按目标计 3 下**（`league_akshan:hit`，打在每一枪、回旋镖、E 的每一枪、R 的每一发子弹上）：同一个目标第 3 下时给他
//!   3 tick 的 `league_akshan_p_go`，数据读到就打出额外伤害（英雄时加护盾）。主包只能数他打中任何人的次数。
//! - **恩怨相抵按已损失生命算**（`league_akshan:bullet`）：每发 `R_DMG + R_RATIO% AD`，目标每少 1% 生命多一点，到少了 `R_FULL`%
//!   时是 `R_MAX` 倍（英雄联盟 0–200% 加成在 67% 封顶）。引导中（`r_chan`、还没开火）被动每 tick 看一眼：存的子弹打得死射程里
//!   血最少的那个英雄，或者他快跑出射程，就给 `league_akshan_r_fire`，数据提前开火（英雄联盟里玩家手动提前放）。
//! - **放大招的时机**（AI 钩子 `league_akshan:ult`）：射程里有英雄生命 ≤ 50%（或存满能打死），自己身边 `R_SAFE` 内没有敌方英雄、
//!   自己生命 ≥ 40% 才放；AI 想在别的时候放就改成普攻 / 走过去。只按已解锁、冷却好的 R（低等级按 R 会让游戏 AI 崩溃）。
//! - **赴险夺人：恶徒和复活**（被动 `league_akshan:rogue`）：读游戏的击杀记录。敌方英雄杀了阿克尚的队友（不算他自己）就成为
//!   恶徒 60 秒（头上 `league_akshan_w_mark` 的图）；阿克尚朝恶徒附近时加移速。阿克尚击杀或助攻击杀恶徒：被这个恶徒杀死、还在等
//!   复活的队友 1 秒后在泉水复活（英雄联盟一样），阿克尚得 100 金，标记清除。
//! - **骄行荡寇击杀刷新**：阿克尚击杀或助攻击杀敌方英雄，E 的冷却清到 0.5 秒（英雄联盟一样）。
//!
//! **复活怎么做到的**：稳定接口里没有改复活时间的函数（`player_respawn_time` 只读）。游戏每个阵亡玩家身上有一个“剩余复活 tick”，
//! 每 tick 减 1，减到 0 时游戏自己在泉水重新生成英雄。本包在运行时读游戏的 `player_respawn_time` / `player_is_alive` 两个函数的
//! 机器码，自己找出“取玩家”的虚表槽、存活标记和剩余 tick 的偏移（`decode`，**动态寻址**：游戏更新后偏移变了也能找到），交叉核对
//! 两个函数一致；每次写之前还要求“阵亡、读到的值等于游戏接口读到的值、≥ 1”，只把它改小到 60 tick（绝不写 0：0 减 1 会变成
//! 永远不复活）。任何一步对不上就不写，只在日志里记一次：最坏只是不复活，不会出错。复活走的是游戏自己的复活流程（新英雄、满血、
//! 等级装备不变）。比赛会被重算好几遍（预演、观看、回放）：只在模拟里的被动钩子里写，用的都是模拟里的数据，结果每遍一样。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_akshan.log`，每次启动游戏重写，上一次的留在 .prev.log：`LAYOUT`
//! （找到的偏移）、`MARK`、`REVIVE`、`VIEW`、`BANNER`、`REFRESH`、`R FIRE`、`R HELD` / `R CAST`，限了条数。

use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod banner;

const ID: &str = "league_akshan";
const HERO: &str = "league_akshan";
const VERSION: &str = env!("CARGO_PKG_VERSION");

// ---- 主包数据里的名字（tools/kit/build_akshan.py）
pub const P_GO: &str = "league_akshan_p_go";
pub const R_CHAN: &str = "league_akshan_r_chan";
pub const R_OPEN: &str = "league_akshan_r_open";
pub const R_FIRE: &str = "league_akshan_r_fire";
/// The data's lock on the champion he aims at (r_ch ticks from the cast): taken off here once he fires early or the
/// channel ends (the user, 2026-10-23: 「应该是瞄准的时候没特效 导致玩家感觉没伤害」).
pub const R_SIGHT: &str = "league_akshan_r_sight";
pub const STORED: [&str; 5] =
    ["league_akshan_r_s1", "league_akshan_r_s2", "league_akshan_r_s3", "league_akshan_r_s4", "league_akshan_r_s5"];
pub const MARK: &str = "league_akshan_w_mark";
pub const W_HASTE: &str = "league_akshan_w_haste";
// sounds of the main pack (league/sound/sfx) the add-on plays
const SFX_MARK: &str = "league_akshan_w_mark";
const SFX_REVIVE: &str = "league_akshan_w_revive";
/// The revive's golden beam (tools/art/fx_akshan_revive.py): on Akshan as the Scoundrel falls, on each ally the tick he
/// stands again at his fountain - the revive showed nothing before (the user: 「我一直在游戏里看不出什么效果」).
const VIEW_REVIVE: &str = "league_akshan_w_revive";
/// How long a revived ally is watched for his return (the revive's REVIVE_T and some).
const BACK_WAIT: usize = 240;
const SFX_GOLD: &str = "league_akshan_w_gold";

// ---- 数字（和 build_akshan.P 一致：make_override.py 把 P 写进副本的 passive.params，测试核对）
pub const P_T: usize = 300;
pub const R_DMG: usize = 35;
pub const R_RATIO: usize = 25;
pub const R_MAX: usize = 3;
pub const R_FULL: usize = 67;
pub const R_REACH: u64 = 220_000;
pub const R_RANGE: u64 = 160_000;
const STACK: &str = "league_akshan_p_s";
const FLAG_T: usize = 3;
const MARK_T: usize = 3600;
const REVIVE_T: u64 = 60;
const GOLD: i64 = 100;
const E_LEFT: usize = 30;
const HASTE_R: u64 = 100_000;
const HASTE: i32 = 25;
const R_SAFE: u64 = 45_000;
const R_LOW: usize = 50;
const ULT_LEVEL: usize = 5;
// ---- Heroic Swing: the swing round a hook point (build_akshan: e_n x e_every ticks; the rope picture is 42 px)
pub const SW: &str = "league_akshan_sw";
pub const ROPE: &str = "league_akshan_e_rope";
pub const SWING_T: usize = 84;
pub const ROPE_R: f64 = 42_000.0;
const SWEEP: f64 = 2.0 * std::f64::consts::PI / 3.0; // 120 degrees round the hook
const HOOK_OFF: f64 = std::f64::consts::PI / 3.0; // the hook 60 degrees off the line to the target
const HAND: f64 = 20_000.0; // the rope at his hand's height (raised on the screen)
const MAP_LO: f64 = 10_000.0;
const MAP_HI: f64 = 950_000.0;
const MAP_MID: (f64, f64) = (480_000.0, 480_000.0);
const HARD: [CcKindV1; 8] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::ForceMove,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::BlockMoveSkill,
];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AKSHAN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_akshan.log");
        }
    }
    PathBuf::from("league_akshan.log")
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

const LOG_FIRST: usize = 60;
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

/// The sims the screen replays (the client's own match view, spectating, a replay) - not the server's presims nor the
/// background matches (origin unknown): their revives get the banner (banner.rs).
fn on_screen(sim: &StableSim<'_>) -> Option<(u64, u64)> {
    let o = sim.sim_origin().unwrap_or_default();
    matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay))
        .then_some((o.match_id, o.set_index))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn count_buff(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count())
}

// ===================== 计算（单元测试用） =====================

/// 一发恩怨相抵：最低伤害 x (100% .. R_MAX x 100%)，按目标少了多少生命（R_FULL% 时封顶）。
pub fn bullet_damage(attack: usize, hp: usize, max_hp: usize) -> usize {
    let base = R_DMG + R_RATIO * attack / 100;
    if max_hp == 0 {
        return base;
    }
    let missing = (max_hp.saturating_sub(hp) * 100 / max_hp).min(R_FULL);
    base * (100 + (R_MAX - 1) * 100 * missing / R_FULL) / 100
}

/// `n` 发连着打在一个人身上（每发按打之前的生命算）一共多少，护甲减伤前。
pub fn volley(attack: usize, mut hp: usize, max_hp: usize, n: usize) -> usize {
    let mut sum = 0;
    for _ in 0..n {
        let d = bullet_damage(attack, hp, max_hp);
        sum += d;
        hp = hp.saturating_sub(d);
    }
    sum
}

/// 被动第几下：之前同一目标有几层 -> (这一下是不是第 3 下, 之后留几层)。
pub fn next_hit(stacks: usize) -> (bool, usize) {
    if stacks >= 2 {
        (true, 0)
    } else {
        (false, stacks + 1)
    }
}

// ===================== 动态寻址：游戏的剩余复活 tick =====================

/// 从游戏的两个只读函数的机器码里读出来的布局。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct LifeLayout {
    /// 世界虚表里“按编号取玩家”的槽（字节偏移）。
    pub getp: usize,
    /// 玩家身上存活标记的偏移（0 = 阵亡，1 = 存活）。
    pub tag: usize,
    /// 紧跟着的值：存活时是英雄实体编号，阵亡时是剩余复活 tick。
    pub val: usize,
}

#[derive(Default, Debug, PartialEq, Eq)]
struct Scan {
    getp: Option<usize>,
    tag_cmp: Option<usize>,
    val: Option<usize>,
    tag_movzx: Option<usize>,
    dec_rdx: bool,
    load_data: bool,
    load_vt: bool,
}

/// ModRM 的位移（mod 01 = disp8，mod 10 = disp32；rm = 100 要 SIB，不认）：(reg, disp, 指令里 ModRM 之后的长度)。
fn modrm_disp(code: &[u8], at: usize) -> Option<(u8, usize, usize)> {
    let m = *code.get(at)?;
    let (md, reg, rm) = (m >> 6, (m >> 3) & 7, m & 7);
    if rm == 4 {
        return None;
    }
    match md {
        1 => Some((reg, *code.get(at + 1)? as i8 as isize as usize, 2)),
        2 => {
            let b = code.get(at + 1..at + 5)?;
            Some((reg, i32::from_le_bytes([b[0], b[1], b[2], b[3]]) as isize as usize, 5))
        }
        _ => None,
    }
}

/// 扫一个函数开头的 `len` 个字节，认出：`dec rdx`、从 [rcx] / [rcx+8] 取世界数据和虚表、`call [reg+X]`（取玩家的槽）、
/// `cmp byte [reg+T],0` + `je` 落到 `mov r64,[reg+V]`（存活标记和值），`movzx r32, byte [reg+T]`（存活标记）。
fn scan(code: &[u8]) -> Scan {
    let mut s = Scan::default();
    let mut i = 0;
    while i + 3 < code.len() {
        let rex = (0x40..=0x4f).contains(&code[i]);
        let (w, op) = if rex { (code[i] & 8 != 0, i + 1) } else { (false, i) };
        let b = code[op];
        if rex && code[i] == 0x48 && b == 0xff && code.get(op + 1) == Some(&0xca) {
            s.dec_rdx = true;
        }
        if w && b == 0x8b {
            if let Some(&m) = code.get(op + 1) {
                // mov r64,[rcx] (mod 00, rm 001) / mov r64,[rcx+8] (mod 01, rm 001, disp8 8)
                if m >> 6 == 0 && m & 7 == 1 {
                    s.load_data = true;
                }
                if m >> 6 == 1 && m & 7 == 1 && code.get(op + 2) == Some(&8) {
                    s.load_vt = true;
                }
            }
        }
        if b == 0xff {
            if let Some((2, disp, _)) = modrm_disp(code, op + 1) {
                s.getp.get_or_insert(disp);
            }
        }
        if b == 0x80 && s.tag_cmp.is_none() {
            if let Some((7, disp, n)) = modrm_disp(code, op + 1) {
                let imm = op + 1 + n;
                if code.get(imm) == Some(&0) && code.get(imm + 1) == Some(&0x74) {
                    let target = imm + 3 + code[imm + 2] as usize;
                    // the je lands on mov r64,[reg+V]
                    if let Some(&r) = code.get(target) {
                        if (0x48..=0x4f).contains(&r) && code.get(target + 1) == Some(&0x8b) {
                            if let Some((_, v, _)) = modrm_disp(code, target + 2) {
                                s.tag_cmp = Some(disp);
                                s.val = Some(v);
                            }
                        }
                    }
                }
            }
        }
        if b == 0x0f && code.get(op + 1) == Some(&0xb6) && s.tag_movzx.is_none() {
            if let Some((_, disp, _)) = modrm_disp(code, op + 2) {
                s.tag_movzx = Some(disp);
            }
        }
        i += 1;
    }
    s
}

/// 两个函数（剩余复活时间、是否存活）的机器码 -> 布局；交叉核对不过就 None。
pub fn decode(respawn_time: &[u8], is_alive: &[u8]) -> Option<LifeLayout> {
    let a = scan(respawn_time);
    let b = scan(is_alive);
    let (getp, tag, val) = (a.getp?, a.tag_cmp?, a.val?);
    let ok = a.dec_rdx
        && a.load_data
        && a.load_vt
        && b.dec_rdx
        && b.getp == Some(getp)
        && b.tag_movzx == Some(tag)
        && val == tag + 8
        && getp % 8 == 0
        && getp < 0x800
        && tag < 0x10000;
    ok.then_some(LifeLayout { getp, tag, val })
}

/// 跟过 jmp 跳板（E9 rel32 / EB rel8），最多 3 次。
unsafe fn follow(mut f: *const u8) -> *const u8 {
    for _ in 0..3 {
        match *f {
            0xe9 => {
                let r = i32::from_le_bytes(std::ptr::read_unaligned(f.add(1) as *const [u8; 4]));
                f = f.offset(5 + r as isize);
            }
            0xeb => f = f.offset(2 + *(f.add(1) as *const i8) as isize),
            _ => break,
        }
    }
    f
}

const SCAN_LEN: usize = 0x60;

/// 解码结果按两个函数的地址缓存（地址变了 = 换了游戏，重新解码）；None = 对不上，不写。
static LAYOUT: Mutex<Option<(usize, usize, Option<LifeLayout>)>> = Mutex::new(None);

const _: () = assert!(std::mem::size_of::<StableSim<'static>>() == std::mem::size_of::<*mut SimCtxV1>());

/// StableSim 里唯一的字段就是 SimCtxV1 指针（大小核对过）。
fn raw_ctx(sim: &StableSim<'_>) -> *mut SimCtxV1 {
    unsafe { *(sim as *const StableSim<'_> as *const *mut SimCtxV1) }
}

fn layout(sim: &StableSim<'_>) -> Option<LifeLayout> {
    let ctx = raw_ctx(sim);
    if ctx.is_null() {
        return None;
    }
    let vt = unsafe { (*ctx).sim };
    if vt.is_null() {
        return None;
    }
    let rt = unsafe { (*vt).player_respawn_time }? as usize;
    let al = unsafe { (*vt).player_is_alive }? as usize;
    let mut cache = LAYOUT.lock().unwrap_or_else(|e| e.into_inner());
    if let Some((a, b, l)) = *cache {
        if a == rt && b == al {
            return l;
        }
    }
    let l = unsafe {
        let (frt, fal) = (follow(rt as *const u8), follow(al as *const u8));
        decode(std::slice::from_raw_parts(frt, SCAN_LEN), std::slice::from_raw_parts(fal, SCAN_LEN))
    };
    match l {
        Some(l) => wlog(format!(
            "LAYOUT found: get_player slot +0x{:x}, life tag +0x{:x}, remaining ticks +0x{:x} (respawn_time 0x{rt:x}, is_alive 0x{al:x})",
            l.getp, l.tag, l.val
        )),
        None => wlog(format!(
            "LAYOUT NOT FOUND in respawn_time 0x{rt:x} / is_alive 0x{al:x}: the game changed, revives are off (nothing is written)"
        )),
    }
    *cache = Some((rt, al, l));
    l
}

type GetPlayer = unsafe extern "C" fn(*mut std::ffi::c_void, usize) -> *mut u8;

/// 把一个阵亡玩家的剩余复活 tick 改小到 `ticks`（至少 1）。所有核对都过了才写，写完用游戏接口读回核对。
fn shorten_respawn(sim: &StableSim<'_>, player: usize, ticks: u64) -> Result<(u64, u64), &'static str> {
    let l = layout(sim).ok_or("no layout")?;
    let p = sim.get_player(player).ok_or("no such player")?;
    if p.is_alive() {
        return Err("alive");
    }
    let api = p.respawn_time() as u64;
    let ctx = raw_ctx(sim);
    unsafe {
        let st = (*ctx).state as *const usize;
        if st.is_null() {
            return Err("no state");
        }
        if *(st as *const u8).add(0x18) != 0 {
            return Err("read-only simulation");
        }
        let (world, wvt) = (*st, *st.add(1));
        if world == 0 || wvt == 0 {
            return Err("no world");
        }
        let slot = *((wvt + l.getp) as *const usize);
        if slot == 0 {
            return Err("no get_player");
        }
        let getp: GetPlayer = std::mem::transmute(slot);
        let pp = getp(world as *mut std::ffi::c_void, player);
        if pp.is_null() {
            return Err("player not found");
        }
        let tag = std::ptr::read_unaligned(pp.add(l.tag) as *const u64);
        let cur = std::ptr::read_unaligned(pp.add(l.val) as *const u64);
        if tag != 0 {
            return Err("not dead in memory");
        }
        if cur != api || cur == 0 {
            return Err("memory and the game disagree");
        }
        let new = cur.min(ticks.max(1));
        if new < cur {
            std::ptr::write_unaligned(pp.add(l.val) as *mut u64, new);
        }
        if p.respawn_time() as u64 != new {
            return Err("read back differs");
        }
        Ok((cur, new))
    }
}

// ===================== 原生效果：被动计数、R 的子弹 =====================

fn stack_name(caster: usize) -> String {
    format!("{STACK}:{caster}")
}

fn hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    let name = stack_name(me);
    let had = count_buff(sim, target, &name);
    let (proc_, keep) = next_hit(had);
    sim.entity_remove_buff(target, &name);
    for _ in 0..keep {
        sim.add_buff(target, &BuffV1::timed(&name, P_T));
    }
    if proc_ {
        sim.add_buff(me, &BuffV1::timed(P_GO, FLAG_T));
        if let Some(k) = counted("proc") {
            wlog(format!("{} THIRD HIT on #{target} #{k}", head(sim, me)));
        }
    }
}

struct HitFx;
impl StableEffectType for HitFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        hit(sim, caster, input);
    }
}

fn bullet(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let Some(t) = sim.get_entity(target) else { return };
    if !t.is_alive() {
        return;
    }
    let (hp, max) = t.hp();
    let attack = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    let d = bullet_damage(attack, hp, max);
    sim.deal_damage_typed(me, target, d, DamageTypeV1::Ad, AttackTypeV1::Skill);
    if let Some(k) = counted("bullet") {
        wlog(format!("{} BULLET on #{target} {hp}/{max}: {d} before armour (attack {attack}) #{k}", head(sim, me)));
    }
}

struct BulletFx;
impl StableEffectType for BulletFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        bullet(sim, caster, input);
    }
}

// ===================== 骄行荡寇：绕钩点荡（真正的弧线 + 绳子） =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 荡的安排：(钩点, 起始角, 方向 ±1)。钩点在他身边 ROPE_R 处、偏离指向目标的方向 HOOK_OFF（两边各试一次），绕钩点转
/// SWEEP；钩点在他上方（屏幕上靠上、离镜头远的一侧，绳子从手往上拉，像荡秋千），其中选荡完离目标最近的那种（一样近时选钩点靠地图中间的）。英雄联盟里钩点是墙，TFM2 的地图没有这种墙，就挂在这一点。
pub fn swing_plan(me: (f64, f64), target: (f64, f64)) -> ((f64, f64), f64, f64) {
    let (dx, dy) = (target.0 - me.0, target.1 - me.1);
    let d = (dx * dx + dy * dy).sqrt();
    let base = if d < 1.0 { 0.0 } else { dy.atan2(dx) };
    let mut best: Option<(f64, (f64, f64), f64, f64)> = None;
    for side in [1.0, -1.0] {
        let h = base + side * HOOK_OFF;
        let a = (me.0 + ROPE_R * h.cos(), me.1 + ROPE_R * h.sin());
        let a0 = (me.1 - a.1).atan2(me.0 - a.0);
        for dir in [1.0, -1.0] {
            let th = a0 + dir * SWEEP;
            let end = (a.0 + ROPE_R * th.cos(), a.1 + ROPE_R * th.sin());
            // the hook above him on the screen (a smaller y: farther from the camera) - the rope rises from his hand like a
            // swing's; below him it lay along his body down to his feet (「看着这么奇怪」)
            let below = if a.1 > me.1 { 100_000.0 } else { 0.0 };
            let score = dist(end, target) + below + 0.1 * dist(a, MAP_MID);
            if best.is_none_or(|b| score < b.0) {
                best = Some((score, a, a0, dir));
            }
        }
    }
    let (_, a, a0, dir) = best.unwrap();
    (a, a0, dir)
}

/// 荡了 age tick 时他在哪（夹在地图里）。
pub fn swing_at(a: (f64, f64), a0: f64, dir: f64, age: usize) -> (f64, f64) {
    let th = a0 + dir * SWEEP * (age.min(SWING_T) as f64) / SWING_T as f64;
    ((a.0 + ROPE_R * th.cos()).clamp(MAP_LO, MAP_HI), (a.1 + ROPE_R * th.sin()).clamp(MAP_LO, MAP_HI))
}

fn sw_name(a: (f64, f64), a0: f64, dir: f64, t0: usize) -> String {
    format!(
        "{SW}:{}:{}:{}:{}:{t0}",
        a.0.round() as i64,
        a.1.round() as i64,
        (a0 * 1000.0).round() as i64,
        if dir > 0.0 { 1 } else { -1 }
    )
}

fn parse_sw(name: &str) -> Option<((f64, f64), f64, f64, usize)> {
    let rest = name.strip_prefix(SW)?.strip_prefix(':')?;
    let v: Vec<&str> = rest.split(':').collect();
    if v.len() != 5 {
        return None;
    }
    let ax: f64 = v[0].parse().ok()?;
    let ay: f64 = v[1].parse().ok()?;
    let a0: f64 = v[2].parse::<f64>().ok()? / 1000.0;
    let dir: f64 = v[3].parse().ok()?;
    let t0: usize = v[4].parse().ok()?;
    Some(((ax, ay), a0, dir, t0))
}

/// E 甩钩（数据在 E 起手第 2 tick 调，输入 = E 的目标）：定钩点，在他身上挂
/// `league_akshan_sw:<钩点x>:<钩点y>:<起始角x1000>:<方向>:<tick>`，之后每 tick 由被动荡他、画绳子。
fn swing_start(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(e) = sim.get_entity(me) else { return };
    let here = e.pos();
    let old: Vec<String> = (0..e.buff_count())
        .filter_map(|i| e.buff_at(i))
        .map(|b| b.name().to_string())
        .filter(|n| n.starts_with(SW))
        .collect();
    let target = match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|t| t.pos()),
        Some(InputTargetKindV1::Pos) => Some((input.x, input.y)),
        _ => None,
    };
    let Some(t) = target else { return };
    let (a, a0, dir) = swing_plan((here.0 as f64, here.1 as f64), (t.0 as f64, t.1 as f64));
    for n in old {
        sim.entity_remove_buff(me, &n);
    }
    let name = sw_name(a, a0, dir, sim.tick());
    sim.add_buff(me, &BuffV1::timed(&name, SWING_T + 30));
    if let Some(k) = counted("swing") {
        wlog(format!(
            "{} SWING round ({:.0}, {:.0}) from ({}, {}) toward #{} #{k}",
            head(sim, me),
            a.0,
            a.1,
            here.0,
            here.1,
            input.target_id
        ));
    }
}

struct SwingFx;
impl StableEffectType for SwingFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        swing_start(sim, caster, input);
    }
}

struct NoopFx;
impl StableEffectType for NoopFx {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

fn hard_cc(sim: &StableSim<'_>, id: usize) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| HARD.iter().any(|k| k.code() == c.kind))
}

/// 一节绳子：在他手的高度、他和钩点的正中，朝钩点（游戏把图转向它飞的方向），1 tick 就到头。
fn rope(sim: &mut StableSim<'_>, me: usize, at: (f64, f64), a: (f64, f64)) -> bool {
    let m = ((at.0 + a.0) / 2.0, (at.1 + a.1) / 2.0 - HAND);
    let (dx, dy) = (a.0 - at.0, a.1 - at.1);
    let d = (dx * dx + dy * dy).sqrt().max(1.0);
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team: sim.get_entity(me).map_or(0, |e| e.team()),
        x: m.0.round().max(0.0) as u64,
        y: m.1.round().max(0.0) as u64,
        radius: 1_000,
        speed: 1_000,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: (m.0 + dx / d * 1_000.0).round().max(0.0) as u64,
        target_y: (m.1 + dy / d * 1_000.0).round().max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(ROPE, &format!("{ID}:noop"), &spec)
}

// ===================== 被动：恶徒、复活、E 刷新、R 提前开火 =====================

#[derive(Clone, Debug, Default)]
struct Scoundrel {
    until: usize,
    /// 被他杀死的队友（玩家编号）。
    victims: Vec<usize>,
}

#[derive(Clone, Default)]
struct Rogue {
    /// 击杀记录读到第几条。
    seen: usize,
    /// 恶徒：敌方玩家编号 -> 标记。
    marks: BTreeMap<usize, Scoundrel>,
    /// 刚复活的队友（玩家编号, 等到第几 tick）：他站起来的那一 tick 在他身上放复活的光。
    back: Vec<(usize, usize)>,
}

/// 击杀记录里的“位置”就是分路（LaneV1 的编号）：按队伍和分路找玩家编号。
fn player_by_lane(sim: &StableSim<'_>, team: usize, lane: u32) -> Option<usize> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find(|p| p.team() == team && p.lane().map(|l| l.code()) == Some(lane)).map(|p| p.id())
}

impl Rogue {
    fn read_kills(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let n = sim.kill_log_count();
        if self.seen > n {
            self.seen = 0; // a new match in a reused passive
        }
        let Some(mine) = sim.get_player(player) else { return };
        let (my_team, my_lane) = (mine.team(), mine.lane().map(|l| l.code()));
        let now = sim.tick();
        while self.seen < n {
            let Some(k) = sim.kill_log_at(self.seen) else { break };
            self.seen += 1;
            let killer_team = k.killer_team;
            let victim_team = 1 - killer_team.min(1);
            let Some(victim) = player_by_lane(sim, victim_team, k.killed_position) else {
                if let Some(c) = counted("nolane") {
                    wlog(format!("{} kill log #{}: no player in lane {} of team {victim_team} #{c}", head(sim, me), self.seen - 1, k.killed_position));
                }
                continue;
            };
            let killer = player_by_lane(sim, killer_team, k.killer_position);
            let recent = now <= k.tick + 3;
            if victim_team == my_team {
                // an ally down (not me): his killer becomes a Scoundrel
                if victim == player {
                    continue;
                }
                if let Some(s) = killer {
                    let m = self.marks.entry(s).or_default();
                    m.until = k.tick + MARK_T;
                    if !m.victims.contains(&victim) {
                        m.victims.push(victim);
                    }
                    if let Some(e) = sim.get_player(s).and_then(|p| p.champion()).map(|e| e.id()) {
                        sim.entity_remove_buff(e, MARK);
                        sim.add_buff(e, &BuffV1::timed(MARK, MARK_T.saturating_sub(now - k.tick.min(now))));
                        if recent {
                            sim.play_sfx(SFX_MARK, me, &InputTargetV1::target(e));
                        }
                    }
                    // the match on screen in full, the presims capped (0.2.4: ~1.9k MARK lines a launch, 2026-11-01)
                    if on_screen(sim).is_some() || counted("mark").is_some() {
                        wlog(format!("{} MARK player {s} killed ally {victim} (victims {:?})", head(sim, me), m.victims));
                    }
                }
            } else {
                // an enemy down: my takedown?
                let assists: Vec<u32> = k.assist_positions.iter().take(k.assist_count as usize).copied().collect();
                let mine_kill = killer_team == my_team
                    && my_lane.is_some_and(|l| k.killer_position == l || assists.contains(&l));
                if !mine_kill || !recent {
                    continue;
                }
                // Heroic Swing: a champion takedown refreshes it to E_LEFT ticks
                if let Some(cd) = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill2)) {
                    if cd.remaining > E_LEFT {
                        sim.entity_reduce_cooldown(me, SkillSlotV1::Skill2, cd.remaining - E_LEFT);
                        if let Some(c) = counted("refresh") {
                            wlog(format!("{} REFRESH E {} -> {E_LEFT} (takedown of player {victim}) #{c}", head(sim, me), cd.remaining));
                        }
                    }
                }
                if let Some(m) = self.marks.remove(&victim) {
                    sim.player_add_gold(player, GOLD);
                    sim.play_sfx(SFX_GOLD, me, &InputTargetV1::target(me));
                    if let Some(e) = sim.get_player(victim).and_then(|p| p.champion()).map(|e| e.id()) {
                        sim.entity_remove_buff(e, MARK);
                    }
                    for v in m.victims {
                        let dead = sim.get_player(v).is_some_and(|p| !p.is_alive());
                        if !dead {
                            wlog(format!("{} REVIVE player {v}: already back", head(sim, me)));
                            continue;
                        }
                        match shorten_respawn(sim, v, REVIVE_T) {
                            Ok((was, now_)) => {
                                sim.play_sfx(SFX_REVIVE, me, &InputTargetV1::target(me));
                                sim.play_view_effect(VIEW_REVIVE, me, &InputTargetV1::target(me), 0, 0, 0);
                                self.back.push((v, now + BACK_WAIT));
                                wlog(format!(
                                    "{} REVIVE player {v}: Scoundrel {victim} down, respawn {was} -> {now_} ticks",
                                    head(sim, me)
                                ))
                            }
                            Err(why) => wlog(format!("{} REVIVE player {v} REFUSED: {why}", head(sim, me))),
                        }
                    }
                }
            }
        }
        // marks run out
        self.marks.retain(|_, m| m.until > now);
        // a revived ally standing again: the beam on him
        let mut left = Vec::new();
        for (v, until) in std::mem::take(&mut self.back) {
            match sim.get_player(v).filter(|p| p.is_alive()).and_then(|p| p.champion()).map(|e| e.id()) {
                Some(e) => {
                    sim.play_view_effect(VIEW_REVIVE, e, &InputTargetV1::target(e), 0, 0, 0);
                    sim.play_sfx(SFX_REVIVE, e, &InputTargetV1::target(e));
                    wlog(format!("{} BACK player {v}: the revive's beam on him", head(sim, me)));
                    // the screen's match: the big line as he stands up (banner.rs)
                    if let Some((m, s)) = on_screen(sim) {
                        let name = |id: usize| sim.get_entity(id).and_then(|x| x.name());
                        banner::note_revive(banner::Banner { m, s, tick: now, akshan: name(me).unwrap_or_else(|| ID.to_string()),
                                                             ally: name(e).unwrap_or_default() });
                    }
                }
                None if now < until => left.push((v, until)),
                None => {}
            }
        }
        self.back = left;
    }

    /// Moving toward the Scoundrels: move speed while one lives within HASTE_R (League: +80-120 toward them).
    fn haste(&self, sim: &mut StableSim<'_>, me: usize) {
        if sim.tick() % 30 != 0 || self.marks.is_empty() {
            return;
        }
        let r2 = HASTE_R * HASTE_R;
        let near = self.marks.keys().filter_map(|&s| sim.get_player(s).and_then(|p| p.champion())).any(|e| {
            e.is_alive() && sim.distance_sq(me, e.id()) <= r2
        });
        if near {
            let mut b = BuffV1::timed(W_HASTE, 31);
            b.move_speed_mult = HASTE;
            sim.entity_remove_buff(me, W_HASTE);
            sim.add_buff(me, &b);
        }
    }

    /// The lock comes off the enemy champions once he fires (r_open) or the channel is over (no r_chan).
    fn sight_off(&self, sim: &mut StableSim<'_>, me: usize) {
        if has_buff(sim, me, R_CHAN) && !has_buff(sim, me, R_OPEN) {
            return;
        }
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let locked: Vec<usize> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_champion() && has_buff(sim, u.id(), R_SIGHT))
            .map(|u| u.id())
            .collect();
        for id in locked {
            sim.entity_remove_buff(id, R_SIGHT);
        }
    }

    /// While R channels: fire early when the stored bullets kill the weakest champion in reach, or he is leaving it.
    fn release(&self, sim: &mut StableSim<'_>, me: usize) {
        if !has_buff(sim, me, R_CHAN) || has_buff(sim, me, R_OPEN) || has_buff(sim, me, R_FIRE) {
            return;
        }
        let n = STORED.iter().filter(|s| has_buff(sim, me, s)).count();
        if n == 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (team, attack) = (e.team(), e.stat().attack);
        let reach2 = R_REACH * R_REACH;
        let mut best: Option<(usize, usize, usize, usize, u64)> = None;
        for i in 0..sim.entity_count() {
            let Some(t) = sim.entity_at(i) else { continue };
            if !t.is_champion() || !t.is_alive() || t.team() == team {
                continue;
            }
            let d2 = sim.distance_sq(me, t.id());
            if d2 > reach2 {
                continue;
            }
            let (hp, max) = t.hp();
            let ratio = hp * 1000 / max.max(1);
            if best.is_none_or(|b| ratio < b.3) {
                best = Some((t.id(), hp + t.shield(), max, ratio, d2));
            }
        }
        let Some((id, ehp, max, _, d2)) = best else { return };
        let dmg = volley(attack, ehp.min(max), max, n);
        let leaving = d2 * 100 >= reach2 * 85;
        if dmg >= ehp || leaving {
            sim.add_buff(me, &BuffV1::timed(R_FIRE, FLAG_T));
            if let Some(k) = counted("fire") {
                let why = if dmg >= ehp { "lethal" } else { "leaving" };
                wlog(format!("{} R FIRE early ({why}): {n} stored, #{id} hp+shield {ehp} vs {dmg} #{k}", head(sim, me)));
            }
        }
    }
}

/// 每 tick：在荡就把他放到弧线上这一刻的位置、画一节绳子；荡完、被硬控就松手。
fn swing_tick(sim: &mut StableSim<'_>, me: usize) {
    let Some(e) = sim.get_entity(me) else { return };
    let mark = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).find(|n| n.starts_with(SW));
    let Some(name) = mark else { return };
    let Some((a, a0, dir, t0)) = parse_sw(&name) else {
        sim.entity_remove_buff(me, &name);
        return;
    };
    let age = sim.tick().saturating_sub(t0);
    if age > SWING_T || hard_cc(sim, me) {
        sim.entity_remove_buff(me, &name);
        if age <= SWING_T {
            wlog(format!("{} SWING cut by crowd control at {age}", head(sim, me)));
        }
        return;
    }
    let p = swing_at(a, a0, dir, age);
    sim.entity_set_pos(me, p.0.round() as u64, p.1.round() as u64);
    if !rope(sim, me, p, a) {
        if let Some(k) = counted("rope_refused") {
            wlog(format!("{} ROPE refused by spawn_projectile #{k}", head(sim, me)));
        }
    }
}

impl StablePassive for Rogue {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        if let Some((m, s)) = on_screen(sim).filter(|_| sim.tick() % 60 == 0) {
            banner::note_view(m, s);
        }
        swing_tick(sim, me);
        self.read_kills(sim, player, me);
        self.haste(sim, me);
        self.release(sim, me);
        self.sight_off(sim, me);
    }
}

// ===================== AI：什么时候放 R =====================

/// The AI is still recalling (game 0.6.5 decides when to go home and buy): its last order was a Return - it orders only
/// on its judgement ticks, a Return again while the recall lasts, nothing in between - and any other order ends it
/// (league_ult_press 0.5.0's rule).
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// How much farther from a champion the AI's walk must end to be a retreat (league_ult_press's `HOLD_AWAY`).
pub const AWAY: f64 = 10_000.0;

/// The AI walks away from `to` this tick (a retreat, a disperse from a lost objective): its Move ends more than `AWAY`
/// farther from it than the champion stands now.
pub fn walking_away(base: Option<InputV1>, me: (f64, f64), to: (f64, f64)) -> bool {
    let d = |a: (f64, f64), b: (f64, f64)| ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt();
    base.is_some_and(|b| b.kind == InputKindV1::Move.code() && d((b.x as f64, b.y as f64), to) > d(me, to) + AWAY)
}

#[derive(Clone, Default)]
struct UltAi {
    last_log: Option<usize>,
    /// the AI is recalling (`still_recalling`)
    recalling: bool,
}

fn ult_input(id: usize) -> InputV1 {
    InputV1::action(InputKindV1::Ult, InputTargetV1::target(id))
}

/// (想打的人, 他是不是被挡住) 由 AI 钩子挑：射程里生命比例最低、≤ R_LOW% 或存满就打得死的敌方英雄；身边 R_SAFE 内有敌方英雄、
/// 自己生命 < 40% 时不放。
fn pick_target(sim: &StableSim<'_>, me: &StableEntity<'_, '_>) -> Result<usize, &'static str> {
    let (my, team) = (me.id(), me.team());
    let (hp, max) = me.hp();
    if hp * 100 < max * 40 {
        return Err("own health below 40%");
    }
    let (safe2, range2) = (R_SAFE * R_SAFE, R_RANGE * R_RANGE);
    let attack = me.stat().attack;
    let mut best: Option<(usize, usize)> = None;
    for i in 0..sim.entity_count() {
        let Some(t) = sim.entity_at(i) else { continue };
        if !t.is_champion() || !t.is_alive() || t.team() == team {
            continue;
        }
        let d2 = sim.distance_sq(my, t.id());
        if d2 <= safe2 {
            return Err("an enemy champion right next to him");
        }
        if d2 > range2 || !t.is_targetable() {
            continue;
        }
        let (th, tm) = t.hp();
        let low = th * 100 <= tm * R_LOW || volley(attack, th + t.shield(), tm, STORED.len()) >= th + t.shield();
        let ratio = th * 1000 / tm.max(1);
        if low && best.is_none_or(|b| ratio < b.1) {
            best = Some((t.id(), ratio));
        }
    }
    best.map(|b| b.0).ok_or("no wounded champion in range")
}

impl StablePlayerAi for UltAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ult")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let wants_ult = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        // game 0.6.5's AI decides when to recall (and buy): the quiet ticks of a recall are busy too
        self.recalling = still_recalling(self.recalling, base);
        let busy = self.recalling || base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        let read = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let me = pl.champion().filter(|e| e.is_alive())?;
            let ready = pl.level() >= ULT_LEVEL && me.cooldown(SkillSlotV1::Ult).is_some_and(|c| c.unlocked && c.remaining == 0);
            let channeling = has_buff(&sim, me.id(), R_CHAN);
            let line = head(&sim, me.id());
            let pick = pick_target(&sim, &me);
            // the target's spot: a channel he starts himself waits while the AI walks away from it (0.6.5's retreats)
            let away = pick.as_ref().ok().and_then(|&t| sim.get_entity(t)).is_some_and(|t| {
                let (p, q) = (me.pos(), t.pos());
                walking_away(base, (p.0 as f64, p.1 as f64), (q.0 as f64, q.1 as f64))
            });
            (pick, ready, channeling, me.pos(), line, away)
        };
        let (pick, ready, channeling, my_pos, line, away) = read;
        if channeling {
            return None;
        }
        match pick {
            Ok(id) if ready && (wants_ult || (!busy && !away)) => {
                let input = ult_input(id);
                if ctx.is_valid_input(&input) {
                    if self.last_log.is_none_or(|t0| tick >= t0 + 60) {
                        self.last_log = Some(tick);
                        if line.starts_with("[view") || counted("r_cast").is_some() {
                            wlog(format!("{line} R CAST on #{id} ({})", if wants_ult { "the AI's R, retargeted" } else { "pressed" }));
                        }
                    }
                    return Some(input);
                }
                if wants_ult {
                    Some(InputV1::move_to(my_pos.0, my_pos.1))
                } else {
                    None
                }
            }
            Err(why) if wants_ult => {
                if self.last_log.is_none_or(|t0| tick >= t0 + LOG_EVERY) {
                    self.last_log = Some(tick);
                    wlog(format!("{line} R HELD: {why}"));
                }
                let target = base.and_then(|b| {
                    (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
                });
                if let Some(t) = target {
                    let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                    if ctx.is_valid_input(&attack) {
                        return Some(attack);
                    }
                }
                Some(InputV1::move_to(my_pos.0, my_pos.1))
            }
            _ if wants_ult => Some(InputV1::move_to(my_pos.0, my_pos.1)),
            _ => None,
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
        "=== {ID} v{VERSION} (Akshan: per-target Dirty Fighting, missing-health Comeuppance, Scoundrels and revives) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:hit"), HitFx);
    module.add_native_effect(format!("{ID}:bullet"), BulletFx);
    module.add_native_effect(format!("{ID}:swing"), SwingFx);
    module.add_native_effect(format!("{ID}:noop"), NoopFx);
    module.add_native_passive(format!("{ID}:rogue"), Rogue::default());
    module.add_player_input_ai(UltAi::default());
    module.add_player_input_ai(banner::Screen::default());
    // the revive banner: a single league_akshan.dll draws it itself; in league_addons the bundle's one client extension
    // (BundleClient) calls banner::draw
    #[cfg(not(league_bundle))]
    module.set_extension(banner::Overlay);
    host.log(LogLevel::Info, "league_akshan loaded (Dirty Fighting per target, Comeuppance on missing health, Scoundrels and revives).");
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

    fn hex(s: &str) -> Vec<u8> {
        let mut v: Vec<u8> = (0..s.len()).step_by(2).map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap()).collect();
        v.resize(SCAN_LEN, 0xcc);
        v
    }

    // TeamfightManager2.exe 0.6.4 (87,228,416 bytes, 2026-10-14): player_respawn_time 0x142e23260, player_is_alive 0x142e214b0
    const RESPAWN_TIME: &str = "554883ec30488d6c243048c745f8feffffff4885d2742348ffca488b014c8b41084889c141ff9058010000904885c0740980b89808000000740831c04883c4305dc3488b80a00800004883c4305dc3";
    const IS_ALIVE: &str = "554883ec30488d6c243048c745f8feffffff4885d2742748ffca488b014c8b41084889c141ff9058010000904885c0740d0fb680980800004883c4305dc3";

    #[test]
    fn decodes_the_0_6_4_getters() {
        let l = decode(&hex(RESPAWN_TIME), &hex(IS_ALIVE)).expect("layout");
        assert_eq!(l, LifeLayout { getp: 0x158, tag: 0x898, val: 0x8a0 });
    }

    // TeamfightManager2.exe 0.6.5 (87,009,792 bytes, 2026-10-21): player_respawn_time 0x142d693d0, player_is_alive
    // 0x142d67640 - the same code, the player's life fields 0x20 further on
    const RESPAWN_TIME_065: &str = "554883ec30488d6c243048c745f8feffffff4885d2742348ffca488b014c8b41084889c141ff9058010000904885c0740980b8b808000000740831c04883c4305dc3488b80c00800004883c4305dc3";
    const IS_ALIVE_065: &str = "554883ec30488d6c243048c745f8feffffff4885d2742748ffca488b014c8b41084889c141ff9058010000904885c0740d0fb680b80800004883c4305dc3";

    #[test]
    fn decodes_the_0_6_5_getters() {
        let l = decode(&hex(RESPAWN_TIME_065), &hex(IS_ALIVE_065)).expect("layout");
        assert_eq!(l, LifeLayout { getp: 0x158, tag: 0x8b8, val: 0x8c0 });
        // one build's getter with the other's: refused, nothing written
        assert!(decode(&hex(RESPAWN_TIME_065), &hex(IS_ALIVE)).is_none());
    }

    #[test]
    fn refuses_mismatched_code() {
        // is_alive reading another field
        let other = IS_ALIVE.replace("0fb6809808", "0fb680a008");
        assert!(decode(&hex(RESPAWN_TIME), &hex(&other)).is_none());
        // a different getter slot in one of them
        let slot = IS_ALIVE.replace("41ff9058010000", "41ff9060010000");
        assert!(decode(&hex(RESPAWN_TIME), &hex(&slot)).is_none());
        // nothing recognisable
        assert!(decode(&hex("c3"), &hex("c3")).is_none());
    }

    #[test]
    fn decodes_with_other_registers_and_disp8() {
        // cmp byte [rdx+0x40],0 ; je -> mov rcx,[rdx+0x48]; is_alive movzx eax, byte [rdx+0x40]
        let rt = "4885d2741e48ffca488b014c8b41084889c141ff5040904885c0740a807a4000740331c0c3488b4a48c3";
        let al = "4885d2741e48ffca488b014c8b41084889c141ff5040904885c074040fb64240c3";
        assert_eq!(decode(&hex(rt), &hex(al)), Some(LifeLayout { getp: 0x40, tag: 0x40, val: 0x48 }));
    }

    #[test]
    fn the_swing_ends_nearer_the_target_on_the_rope() {
        let me = (300_000.0, 500_000.0);
        let t = (360_000.0, 500_000.0);
        let (a, a0, dir) = swing_plan(me, t);
        assert!((dist(a, me) - ROPE_R).abs() < 1.0);
        assert!(a.1 < me.1, "the hook is not above him: {a:?}");
        let start = swing_at(a, a0, dir, 0);
        assert!(dist(start, me) < 2.0, "{start:?}");
        let end = swing_at(a, a0, dir, SWING_T);
        assert!((dist(end, a) - ROPE_R).abs() < 2.0);
        assert!(dist(end, t) < dist(me, t), "end {end:?} not nearer {t:?}");
        let mut prev = start;
        for k in 1..=SWING_T {
            let p = swing_at(a, a0, dir, k);
            assert!(dist(p, prev) < 1_500.0);
            prev = p;
        }
        let name = sw_name(a, a0, dir, 1234);
        assert!(name.len() <= 64, "{name}");
        let (pa, pa0, pdir, pt0) = parse_sw(&name).unwrap();
        assert!(dist(pa, a) < 1.0 && (pa0 - a0).abs() < 0.001 && pdir == dir && pt0 == 1234);
    }

    #[test]
    fn third_hit_procs() {
        assert_eq!(next_hit(0), (false, 1));
        assert_eq!(next_hit(1), (false, 2));
        assert_eq!(next_hit(2), (true, 0));
    }

    #[test]
    fn bullets_grow_with_missing_health() {
        // attack 200: min R_DMG + R_RATIO% of 200 (35 + 50 = 85)
        let min = R_DMG + R_RATIO * 2;
        assert_eq!(bullet_damage(200, 1000, 1000), min);
        // 67% missing or more: 3x
        assert_eq!(bullet_damage(200, 330, 1000), min * R_MAX);
        assert_eq!(bullet_damage(200, 10, 1000), min * R_MAX);
        // half way to the cap: about 2x
        let mid = bullet_damage(200, 665, 1000);
        assert!(mid > min * 19 / 10 && mid < min * 21 / 10, "{mid}");
        // each bullet is read on the health left
        assert!(volley(200, 1000, 1000, 5) > 5 * min);
    }

    #[test]
    fn the_copy_carries_the_numbers_and_the_native_parts() {
        let copy = include_str!("../override/league_akshan.data_champion");
        for (k, v) in [("r_dmg", R_DMG), ("r_ratio", R_RATIO), ("r_max", R_MAX), ("r_full", R_FULL), ("p_t", P_T)] {
            assert!(copy.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in ["league_akshan:hit", "league_akshan:bullet", "league_akshan:rogue", "league_akshan:swing", ROPE] {
            assert!(copy.contains(name), "the copy never uses {name}");
        }
        for name in [P_GO, R_CHAN, R_OPEN, R_FIRE, STORED[0], STORED[4]] {
            assert!(copy.contains(&format!("\"{name}\"")), "the copy never names {name}");
        }
        assert!(copy.contains(&format!("\"range\": {R_RANGE}")), "R's range is not {R_RANGE}");
        assert!(copy.contains(&format!("\"range\": {R_REACH}")), "the bullets' reach is not {R_REACH}");
    }
}
