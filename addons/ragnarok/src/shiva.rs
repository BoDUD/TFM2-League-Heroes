//! 湿婆（`ragnarok_shiva`）数据做不到的部分：被动「节奏」、配音、倒地声，和轮回舞踊燃烧形态的显示。数据
//! （tools/kit/build_shiva.py）的 `passive` 是这里的 `ragnarok_shiva:rhythm`，参数 p_atk / p_as / p_max / p_t 从数据的
//! params 读；四臂连击、舞步、轮回舞踊（变身、形态里的火焰版本、结束时的高踢）全在数据里。
//!
//! 节奏（四只手臂跳的舞有节拍）：他每放一个技能（Q、E、R）记一拍，最多 p_max 拍；每拍攻击力 +p_atk%、攻速 +p_as%，
//! 挂在 `ragnarok_shiva_rhythm` 上（拍数变了换一个）。p_t 拍里没再放技能，拍子散掉。放技能是看技能的冷却从 0 跳上去
//! （小次郎、赫拉克勒斯的做法）。他死了拍子也散。
//!
//! 轮回舞踊：点燃那一刻数据给他挂 `ragnarok_shiva_tandava`（几秒）。游戏按名字自动播的待机、跑、普攻、两个技能、挨打、
//! 倒下数据换不了，这里的显示钩子（game_places::hook，宙斯、小次郎、赫拉克勒斯的做法）在他有这个 buff 时换成 Codex 画的
//! 燃烧形态（h_*）。变身（ult）和形态结束时的高踢（h_ult，数据用 CasterAnimation 放）不换。
//!
//! 配音（铃木达央的原声，Codex 截的六句）：一局第一次和敌方英雄交手说一句（终于轮到我了 / 别再得意了，五次里一次是
//! 「别错过这场热闹」），杀了英雄（久违地热血沸腾），点燃时偶尔「在终末跳到天亮」，复活时（打起精神）。每类有自己的冷却，
//! 任意两句之间至少隔一会儿。倒地：死的时候放身子着地（延迟在 sound_info 里，两种形态一样）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `shiva`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_shiva";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// 日志只记前面这些行，之后每一百行记一行
const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 100;
static LOGGED: AtomicUsize = AtomicUsize::new(0);

fn log(msg: String) {
    let n = LOGGED.fetch_add(1, Ordering::Relaxed) + 1;
    if n <= LOG_FIRST || n % LOG_EVERY == 0 {
        crate::wlog(format!("shiva #{n} {msg}"));
    }
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 每拍加多少攻击力，百分比
    pub p_atk: usize,
    /// 每拍加多少攻速，百分比
    pub p_as: usize,
    /// 最多几拍
    pub p_max: usize,
    /// 多少拍（一秒 60 拍）没再放技能就散
    pub p_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_atk: 4,
            p_as: 6,
            p_max: 4,
            p_t: 240,
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
            "p_atk" => p.p_atk = u.min(30),
            "p_as" => p.p_as = u.min(50),
            "p_max" => p.p_max = u.clamp(1, 12),
            "p_t" => p.p_t = u.clamp(30, 3600),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// 节奏的 buff 名字。
pub const RHYTHM: &str = "ragnarok_shiva_rhythm";

/// 一份模拟里的节拍：现在几拍、最后一拍在哪一拍（tick）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Beats {
    pub n: usize,
    pub last: usize,
}

impl Beats {
    /// 放了一个技能：记一拍（最多 p_max）。
    pub fn beat(&mut self, tick: usize, p: &Params) {
        self.n = (self.n + 1).min(p.p_max);
        self.last = tick;
    }

    /// 到这一拍为止拍子散了没有（散了就清零，返回 true）。
    pub fn fade(&mut self, tick: usize, p: &Params) -> bool {
        if self.n > 0 && tick >= self.last + p.p_t {
            self.n = 0;
            return true;
        }
        false
    }
}

/// n 拍的 buff（永久，拍数变了换一个，散了摘掉）。
pub fn rhythm_buff(n: usize, p: &Params) -> BuffV1 {
    let mut b = BuffV1::named(RHYTHM);
    b.attack_mult = (n * p.p_atk) as i32;
    b.attack_speed_mult = (n * p.p_as) as i32;
    b
}

/// 冷却从上一拍的 before 跳到 now：刚放了这个技能（跳上去超过半秒才算，冷却缩减、刷新不算）。
pub fn just_cast(before: usize, now: usize) -> bool {
    now > before + 30
}

/// 配音：事件。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手
    Start,
    /// 杀了敌方英雄
    Kill,
    /// 放了轮回舞踊（点燃）
    Ult,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        // 五份里一份是「别错过这场热闹」
        Cue::Start => &["v_entry", "v_challenge", "v_entry", "v_challenge", "v_festival"],
        Cue::Kill => &["v_excite"],
        Cue::Ult => &["v_dance"],
        Cue::Respawn => &["v_rally"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Kill => 25 * SECOND,
        Cue::Ult => 40 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 放大招时喊不喊：冷却到了也只有三成五的时候开口
pub const ULT_CHANCE: u64 = 35;

/// 一份模拟里的配音节奏：上一句的拍数、每类上次的拍数、每类轮到第几句。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    turn: HashMap<&'static str, usize>,
    started: bool,
}

impl Voice {
    fn key(cue: Cue) -> &'static str {
        match cue {
            Cue::Start => "start",
            Cue::Kill => "kill",
            Cue::Ult => "ult",
            Cue::Respawn => "respawn",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那句一局只说一次，按拍数挑，别的按顺序轮。
    pub fn pick(&mut self, cue: Cue, tick: usize) -> Option<&'static str> {
        if cue == Cue::Start && self.started {
            return None;
        }
        if self.last_any.is_some_and(|t| tick < t + VOICE_GAP) {
            return None;
        }
        let k = Self::key(cue);
        if self.last.get(k).is_some_and(|&t| tick < t.saturating_add(cue_cooldown(cue))) {
            return None;
        }
        let lines = lines_of(cue);
        let line = if cue == Cue::Start {
            self.started = true;
            lines[tick % lines.len()]
        } else {
            let turn = self.turn.entry(k).or_insert(0);
            *turn += 1;
            lines[(*turn - 1) % lines.len()]
        };
        self.last.insert(k, tick);
        self.last_any = Some(tick);
        Some(line)
    }
}

// ===================== 轮回舞踊形态的显示 =====================

/// 点燃以后的 buff（数据 build_shiva.py 的 tandava）。
pub const TANDAVA: &str = "ragnarok_shiva_tandava";
/// 燃烧形态有自己一套的动作（图里常态的原名，燃烧形态的 h_*）。变身（ult）本身不换。
pub const FORM_TAGS: [&str; 7] = ["idle", "run", "attack", "skill", "skill2", "hit", "dead"];

/// 正在播的动画名 + 有没有轮回舞踊的 buff → 该播的名字（不用换就是 None）。buff 没了把换上去的 h_ 换回来。
pub fn anim_for(cur: &str, burning: bool) -> Option<String> {
    let base = cur.strip_prefix("h_").filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if burning { format!("h_{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

#[cfg(windows)]
mod view {
    //! 显示钩子：走显示世界的实体表，名字是 ragnarok_shiva 的按有没有轮回舞踊的 buff 换正在播的动画名
    //! （宙斯 zeus.rs、小次郎 kojiro.rs、赫拉克勒斯 heracles.rs 的做法）。

    use std::sync::{Mutex, Once};

    use super::{anim_for, log, TANDAVA};
    use game_places::hook::{Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR,
                            VALUE};

    const NAME: &[u8] = b"ragnarok_shiva";

    static LOOKS: Mutex<Vec<(usize, u64, bool)>> = Mutex::new(Vec::new());
    static HOOK: Once = Once::new();

    #[link(name = "kernel32")]
    extern "system" {
        fn GetProcessHeap() -> isize;
        fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
        fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
    }

    unsafe fn q(addr: usize) -> usize {
        std::ptr::read_unaligned(addr as *const usize)
    }

    fn plausible(p: usize) -> bool {
        (0x10000..0x7fff_ffff_ffff).contains(&p)
    }

    /// 实体身上有没有这个名字的 buff。
    unsafe fn has(v: usize, name: &str) -> bool {
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
        })
    }

    /// 显示世界里每个湿婆：有轮回舞踊的 buff 就把那几个动作换成燃烧形态的。
    unsafe fn dress(world: usize, ents: &[Ent]) {
        for e in ents {
            let elem = e.elem;
            let v = elem + VALUE;
            if q(v + NAME_LEN_AT) != NAME.len() {
                continue;
            }
            let ptr = q(v + NAME_PTR);
            if !plausible(ptr) || std::slice::from_raw_parts(ptr as *const u8, NAME.len()) != NAME {
                continue;
            }
            let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
            if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
                continue;
            }
            let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
            let key = q(elem) as u64;
            let burning = has(v, TANDAVA);
            if let Ok(mut looks) = LOOKS.try_lock() {
                let look = (world, key, burning);
                if !looks.contains(&look) {
                    looks.retain(|l| !(l.0 == world && l.1 == key));
                    looks.push(look);
                    if looks.len() > 64 {
                        looks.remove(0);
                    }
                    log(format!("world {world:#x} Shiva #{key}: {} (playing {cur})",
                                if burning { "Tandava Karma" } else { "four arms" }));
                }
            }
            let Some(want) = anim_for(cur, burning) else { continue };
            let heap = GetProcessHeap();
            let fresh = HeapAlloc(heap, 0, want.len());
            if fresh.is_null() {
                continue;
            }
            std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
            std::ptr::write_unaligned((v + ANIM_CAP) as *mut usize, want.len());
            std::ptr::write_unaligned((v + ANIM_PTR) as *mut usize, fresh as usize);
            std::ptr::write_unaligned((v + ANIM_LEN) as *mut usize, want.len());
            if acap > 0 {
                HeapFree(heap, 0, aptr as *mut u8);
            }
        }
    }

    /// 登记显示钩子（一个进程一次）：本 DLL 在 init 里先 hd_engine::defer_display()，真正换槽等第一帧（lib.rs 的 Frame）。
    pub fn install_once() {
        HOOK.call_once(|| match game_places::hook::add("ragnarok_shiva", dress, |m: &str| crate::wlog(m)) {
            Ok(p) => crate::wlog(format!("shiva: Tandava Karma on: {p}")),
            Err(e) => crate::wlog(format!("shiva: Tandava Karma off ({e}): the four-arm frames only")),
        });
    }
}

// ===================== 游戏里 =====================

#[derive(Clone, Default)]
struct Rhythm {
    me: usize,
    p: Params,
    beats: Beats,
    was_alive: bool,
    lives: usize,
    /// 两个技能和大招的冷却上一拍是多少，用来认出这一拍刚放了
    cds: (usize, usize, usize),
    voice: Voice,
}

impl Rhythm {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(format!("[t={tick}] VOICE #{me}: {cue:?} -> {line}"));
    }

    /// 拍数变了：换上新拍数的 buff（零拍就只摘掉）。
    fn show(&mut self, sim: &mut StableSim<'_>, what: &str) {
        let me = self.me;
        sim.entity_remove_buff(me, RHYTHM);
        if self.beats.n > 0 {
            sim.add_buff(me, &rhythm_buff(self.beats.n, &self.p));
        }
        log(format!("[t={}] RHYTHM #{me}: {what} -> {} beat(s)", sim.tick(), self.beats.n));
    }
}

impl StablePassive for Rhythm {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(format!("[t={}] SPAWN #{me}: ragnarok.dll's Shiva (player {player}, team {team}), {:?}", sim.tick(), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if alive && !self.was_alive {
            self.lives += 1;
            self.beats = Beats::default();
            sim.entity_remove_buff(me, RHYTHM);
            if self.lives > 1 {
                self.say(sim, Cue::Respawn);
            }
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        let tick = sim.tick();
        if self.beats.fade(tick, &self.p) {
            self.show(sim, "faded");
        }
        let Some((_, q, e, r)) = sim.get_player(player).and_then(|p| p.cooldowns()) else { return };
        let (q0, e0, r0) = self.cds;
        self.cds = (q, e, r);
        for (cast, what) in [(just_cast(q0, q), "skill"), (just_cast(e0, e), "skill2"), (just_cast(r0, r), "ult")] {
            if cast {
                self.beats.beat(tick, &self.p);
                self.show(sim, what);
            }
        }
        if just_cast(r0, r) && (rng % 100) < ULT_CHANCE {
            self.say(sim, Cue::Ult);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        if sim.get_entity(target).is_some_and(|t| t.team() != my_team && t.is_champion()) {
            self.say(sim, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.me = me;
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.say(sim, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.was_alive = false;
        // 死了拍子散掉
        self.beats = Beats::default();
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// 湿婆的被动和显示钩子，注册进本包的模块（lib.rs 的 init，在 hd_engine::defer_display 之后）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("shiva: {ID} v{VERSION} (Shiva: rhythm, Tandava Karma, voice lines) registered"));
    module.add_native_passive(format!("{ID}:rhythm"), Rhythm::default());
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "ragnarok.dll: Shiva (rhythm, Tandava Karma, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let p = parse_params(r#"{"p_atk": 4, "p_as": 6, "p_max": 4, "p_t": 240}"#);
        assert_eq!(p, Params::default());
        assert_eq!(parse_params(r#"{"p_max": 0}"#).p_max, 1);
        assert_eq!(parse_params(r#"{"p_t": 5}"#).p_t, 30);
    }

    #[test]
    fn beats_add_up_to_the_cap_and_fade() {
        let p = Params::default();
        let mut b = Beats::default();
        for t in [100, 200, 300, 400, 500] {
            b.beat(t, &p);
        }
        assert_eq!(b, Beats { n: 4, last: 500 });
        // 最后一拍之后 p_t 拍以内还在，到了就散
        assert!(!b.fade(500 + p.p_t - 1, &p));
        assert_eq!(b.n, 4);
        assert!(b.fade(500 + p.p_t, &p));
        assert_eq!(b.n, 0);
        // 零拍不会「再散一次」
        assert!(!b.fade(10_000, &p));
        let buff = rhythm_buff(3, &p);
        assert_eq!(buff.name(), RHYTHM);
        assert_eq!((buff.attack_mult, buff.attack_speed_mult), (12, 18));
    }

    #[test]
    fn a_cast_is_a_cooldown_jumping_up() {
        assert!(just_cast(0, 360));
        assert!(!just_cast(360, 359));
        assert!(!just_cast(0, 20));
    }

    #[test]
    fn the_start_line_once_a_match_sometimes_the_festival() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_entry"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 304), Some("v_festival"));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Kill, 1000), Some("v_excite"));
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Ult, 1000 + VOICE_GAP), Some("v_dance"));
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 1000 + 25 * SECOND), Some("v_excite"));
    }

    /// Codex 的六句都用上，每句只在一类里。
    #[test]
    fn every_line_is_one_of_codexs_six() {
        let six = ["entry", "excite", "challenge", "rally", "festival", "dance"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Kill, Cue::Ult, Cue::Respawn] {
            for line in lines_of(cue) {
                let clip = line.trim_start_matches("v_");
                assert!(six.contains(&clip), "{line}");
                if !used.contains(&clip) {
                    used.push(clip);
                }
            }
        }
        used.sort();
        let mut all = six.to_vec();
        all.sort();
        assert_eq!(used, all);
    }

    #[test]
    fn the_burning_form_swaps_its_seven_actions() {
        for t in FORM_TAGS {
            assert_eq!(anim_for(t, true), Some(format!("h_{t}")));
            assert_eq!(anim_for(&format!("h_{t}"), false).as_deref(), Some(t));
            assert_eq!(anim_for(t, false), None);
        }
        // 变身和形态结束的高踢不换
        assert_eq!(anim_for("ult", true), None);
        assert_eq!(anim_for("h_ult", false), None);
        assert_eq!(anim_for("h_ult", true), None);
    }
}
