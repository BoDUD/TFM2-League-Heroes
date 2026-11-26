//! 零福／波旬（`ragnarok_zerofuku`）数据做不到的部分：配音、倒地声和波旬形态的显示。数据（tools/kit/build_zerofuku.py）的
//! `passive` 是这里的 `ragnarok_zerofuku:voice`，没有参数；不幸（被动）、两种形态的普攻和技能、破茧（变成波旬的 buff
//! `ragnarok_zerofuku_hajun`，一直挂到死）全在数据里。
//!
//! 波旬形态：游戏按名字自动播的待机、跑、普攻、两个技能、挨打、倒下数据换不了，这里的显示钩子（game_places::hook，湿婆、
//! 赫拉克勒斯的做法）在他有波旬的 buff 时换成 Codex 画的波旬（h_*）。破茧（ult）不换；波旬再放大招的 h_ult 是数据用
//! CasterAnimation 放的。波旬一直到死：死的那一下 buff 要是已经没了，倒下还是波旬的（记着他活着时最后是哪个形态）。
//!
//! 配音（Codex 截的六句官方原声：零福是村瀬歩，第四弹预告；波旬是稻田彻，第 15 话）：一局第一次和敌方英雄交手零福说一句
//! （「终于等到这一刻」，三次里一次是挑衅）；零福杀了英雄挑衅一句，波旬杀了英雄说「连斩未中」那句；零福放破茧时情绪爆发那句；
//! 波旬放魔臂横断时一半的时候质问那句；复活（又是零福）不解那句。每类有自己的冷却，任意两句之间至少隔一会儿。倒地：死的时候放
//! Codex 的着地声（延迟在 sound_info 里，对上死亡动作第 8 帧着地，两种形态一样）。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `zerofuku`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_zerofuku";
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
        crate::wlog(format!("zerofuku #{n} {msg}"));
    }
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局里第一次和敌方英雄交手（零福）
    Start,
    /// 零福杀了敌方英雄
    Kill,
    /// 波旬杀了敌方英雄
    HajunKill,
    /// 零福放了破茧
    Cocoon,
    /// 波旬放了魔臂横断
    Sever,
    /// 复活回来（又是零福）
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn lines_of(cue: Cue) -> &'static [&'static str] {
    match cue {
        // 三份里一份是挑衅
        Cue::Start => &["v_arrival", "v_arrival", "v_threat"],
        Cue::Kill => &["v_threat"],
        Cue::HajunKill => &["v_h_challenge"],
        Cue::Cocoon => &["v_outburst"],
        Cue::Sever => &["v_h_why"],
        Cue::Respawn => &["v_why"],
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Kill | Cue::HajunKill => 25 * SECOND,
        Cue::Cocoon | Cue::Sever => 30 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 波旬放魔臂横断时喊不喊：冷却到了也只有一半的时候开口（破茧每次都喊）
pub const SEVER_CHANCE: u64 = 50;

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
            Cue::HajunKill => "hajun_kill",
            Cue::Cocoon => "cocoon",
            Cue::Sever => "sever",
            Cue::Respawn => "respawn",
        }
    }

    /// 现在能不能说这一类，能就返回这次说哪句并记下来。交手那句一局只说一次，按拍数挑（同一局的几份模拟挑的一样），
    /// 别的按顺序轮。
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

// ===================== 波旬形态的显示 =====================

/// 破茧以后的 buff（数据 build_zerofuku.py 的 hajun，一直挂到死）。
pub const HAJUN: &str = "ragnarok_zerofuku_hajun";
/// 波旬有自己一套的动作（图里零福的原名，波旬的 h_*）。破茧（ult）本身和数据放的 h_ult 不换。
pub const FORM_TAGS: [&str; 7] = ["idle", "run", "attack", "skill", "skill2", "hit", "dead"];

/// 正在播的动画名 + 现在有没有波旬的 buff + 活着时最后是不是波旬 → 该播的名字（不用换就是 None）。
/// buff 没了把换上去的 h_ 换回来；倒下按活着时最后的形态（死的时候 buff 可能已经摘了）。
pub fn anim_for(cur: &str, hajun: bool, was_hajun: bool) -> Option<String> {
    let base = cur.strip_prefix("h_").filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let as_hajun = if base == "dead" { hajun || was_hajun } else { hajun };
    let want = if as_hajun { format!("h_{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

#[cfg(windows)]
mod view {
    //! 显示钩子：走显示世界的实体表，名字是 ragnarok_zerofuku 的按有没有波旬的 buff 换正在播的动画名
    //! （湿婆 shiva.rs、赫拉克勒斯 heracles.rs 的做法）。

    use std::sync::{Mutex, Once};

    use super::{anim_for, log, HAJUN};
    use game_places::hook::{Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR,
                            VALUE};

    const NAME: &[u8] = b"ragnarok_zerofuku";

    /// 每个零福（显示世界, 实体）活着时最后是不是波旬
    static FORMS: Mutex<Vec<(usize, u64, bool)>> = Mutex::new(Vec::new());
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

    /// 显示世界里每个零福：有波旬的 buff 就把那几个动作换成波旬的。
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
            let hajun = has(v, HAJUN);
            let dying = cur == "dead" || cur == "h_dead";
            let mut was = false;
            if let Ok(mut forms) = FORMS.try_lock() {
                let old = forms.iter().position(|f| f.0 == world && f.1 == key);
                was = old.is_some_and(|i| forms[i].2);
                // 死的时候不记：倒下那几帧 buff 可能已经摘了，记下来的还是活着时的形态
                if !dying && old.map_or(true, |i| forms[i].2 != hajun) {
                    if let Some(i) = old {
                        forms.remove(i);
                    }
                    forms.push((world, key, hajun));
                    if forms.len() > 64 {
                        forms.remove(0);
                    }
                    log(format!("world {world:#x} Zerofuku #{key}: {} (playing {cur})",
                                if hajun { "Hajun" } else { "Zerofuku" }));
                }
            }
            let Some(want) = anim_for(cur, hajun, was) else { continue };
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
        HOOK.call_once(|| match game_places::hook::add("ragnarok_zerofuku", dress, |m: &str| crate::wlog(m)) {
            Ok(p) => crate::wlog(format!("zerofuku: Hajun's frames on: {p}")),
            Err(e) => crate::wlog(format!("zerofuku: Hajun's frames off ({e}): Zerofuku's frames only")),
        });
    }
}

// ===================== 游戏里 =====================

#[derive(Clone, Default)]
struct ZerofukuVoice {
    me: usize,
    was_alive: bool,
    lives: usize,
    /// 这条命放过破茧没有（第一次放大招是破茧，之后是魔臂横断；死了复活又是零福）
    hajun: bool,
    /// 大招的冷却上一拍是多少，用来认出这一拍刚放了大招
    r_cd: usize,
    voice: Voice,
}

impl ZerofukuVoice {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(format!("[t={tick}] VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for ZerofukuVoice {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(format!("[t={}] SPAWN #{me}: ragnarok.dll's Zerofuku (player {player}, team {team})", sim.tick()));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if alive && !self.was_alive {
            self.lives += 1;
            self.hajun = false;
            if self.lives > 1 {
                self.say(sim, Cue::Respawn);
            }
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        // 大招的冷却从 0 跳上去就是刚放了：这条命第一次是破茧，之后是魔臂横断
        let r_cd = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.3);
        let cast = r_cd > self.r_cd + 30;
        self.r_cd = r_cd;
        if cast {
            if self.hajun {
                if (rng % 100) < SEVER_CHANCE {
                    self.say(sim, Cue::Sever);
                }
            } else {
                self.hajun = true;
                log(format!("[t={}] COCOON #{me}: Zerofuku -> Hajun for this life", sim.tick()));
                self.say(sim, Cue::Cocoon);
            }
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.me = me;
        let Some(my_team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let enemy_champion = sim.get_entity(target).is_some_and(|t| t.team() != my_team && t.is_champion());
        if enemy_champion && !self.hajun {
            self.say(sim, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.me = me;
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.say(sim, if self.hajun { Cue::HajunKill } else { Cue::Kill });
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.was_alive = false;
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// 零福的被动（声音）和波旬形态的显示钩子，注册进本包的模块（lib.rs 的 init，在 hd_engine::defer_display 之后）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("zerofuku: {ID} v{VERSION} (Zerofuku / Hajun: voice lines, the fall, Hajun's frames) registered"));
    module.add_native_passive(format!("{ID}:voice"), ZerofukuVoice::default());
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "ragnarok.dll: Zerofuku / Hajun (voice lines, Hajun's frames).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hajun_wears_his_own_frames_but_not_the_cocoon() {
        assert_eq!(anim_for("idle", true, false).as_deref(), Some("h_idle"));
        assert_eq!(anim_for("skill2", true, true).as_deref(), Some("h_skill2"));
        // buff 没了换回来
        assert_eq!(anim_for("h_run", false, true).as_deref(), Some("run"));
        // 已经对了就不动
        assert_eq!(anim_for("h_attack", true, true), None);
        assert_eq!(anim_for("attack", false, false), None);
        // 破茧和数据放的魔臂横断不换
        assert_eq!(anim_for("ult", true, true), None);
        assert_eq!(anim_for("h_ult", false, true), None);
    }

    #[test]
    fn hajun_falls_as_hajun_even_when_the_buff_is_gone() {
        assert_eq!(anim_for("dead", false, true).as_deref(), Some("h_dead"));
        assert_eq!(anim_for("h_dead", false, true), None);
        assert_eq!(anim_for("dead", true, false).as_deref(), Some("h_dead"));
        // 零福死了还是零福
        assert_eq!(anim_for("dead", false, false), None);
        assert_eq!(anim_for("h_dead", false, false).as_deref(), Some("dead"));
    }

    #[test]
    fn the_start_line_once_a_match_sometimes_the_threat() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 300), Some("v_arrival"));
        assert_eq!(v.pick(Cue::Start, 300 + 600 * SECOND), None);
        let mut w = Voice::default();
        assert_eq!(w.pick(Cue::Start, 302), Some("v_threat"));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Cocoon, 1000), Some("v_outburst"));
        // 刚说完，别的也不说
        assert_eq!(v.pick(Cue::HajunKill, 1000 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::HajunKill, 1000 + VOICE_GAP), Some("v_h_challenge"));
        // 杀人那句有自己的冷却
        assert_eq!(v.pick(Cue::HajunKill, 1000 + VOICE_GAP + 25 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::HajunKill, 1000 + VOICE_GAP + 25 * SECOND), Some("v_h_challenge"));
        // 复活一句，冷却到了就说
        let mut r = Voice::default();
        let said: Vec<_> = (0..3).map(|i| r.pick(Cue::Respawn, i * 61 * SECOND)).collect();
        assert_eq!(said, [Some("v_why"), Some("v_why"), Some("v_why")]);
    }

    /// Codex 截的六句都用上（零福四句、波旬两句）。
    #[test]
    fn every_line_is_one_of_codexs_six() {
        let six = ["arrival", "threat", "why", "outburst", "h_why", "h_challenge"];
        let mut used: Vec<&str> = Vec::new();
        for cue in [Cue::Start, Cue::Kill, Cue::HajunKill, Cue::Cocoon, Cue::Sever, Cue::Respawn] {
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
}
