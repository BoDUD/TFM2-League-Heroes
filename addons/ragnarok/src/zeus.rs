//! 宙斯（`ragnarok_zeus`）数据做不到的部分：配音，和三种身体的显示。数据（tools/kit/build_zeus.py）的 `passive` 是这里的
//! `ragnarok_zeus:voice`，没有参数；肌肉膨胀、阿陀磨须、变回老人这些规则和变身过程全在数据里。
//!
//! 三种身体：一个英雄、一个实体，形态是他身上的 buff（`ragnarok_zeus_mu` 膨胀、`ragnarok_zeus_ad` 阿陀磨须，都没有就是
//! 老人）。游戏按名字自动播的 idle / run / hit / dead 和三个出手动作（attack / skill / skill2）数据换不了，这里的显示钩子
//! （game_places::hook，纳尔、奈德丽附加包的做法）把正在播的名字换成那种身体的：膨胀 `mu_idle` …，阿陀磨须 `ad_idle` …。
//! 变身过程（`expand`、大招的 `ult`、`revert`）是数据播的，不碰。阵亡时 buff 清掉：尸体按倒下前那一帧的身体画。
//!
//! 配音（高木涉的原声，Codex 截的六句，宣传口号那句只放演示页）：一局第一次出场、肌肉膨胀、放连拳偶尔、杀了英雄、复活，
//! 每类有自己的冷却，任意两句之间至少隔一会儿。死的时候放 Codex 的倒地声。
//!
//! 日志写在本包的 ragnarok.log 里（行首 `zeus`）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

const ID: &str = "ragnarok_zeus";
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
        crate::wlog(format!("zeus #{n} {msg}"));
    }
}

// ===================== 形态 =====================

/// 形态 buff：阿陀磨须优先（压缩那一刻两个都在），其次膨胀。
pub const ADAMAS: &str = "ragnarok_zeus_ad";
pub const MUSCLE: &str = "ragnarok_zeus_mu";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Form {
    Elder,
    Muscle,
    Adamas,
}

impl Form {
    pub fn of(adamas: bool, muscle: bool) -> Form {
        if adamas {
            Form::Adamas
        } else if muscle {
            Form::Muscle
        } else {
            Form::Elder
        }
    }

    fn prefix(self) -> &'static str {
        match self {
            Form::Elder => "",
            Form::Muscle => "mu_",
            Form::Adamas => "ad_",
        }
    }
}

/// 三种身体各有一套的动作（图里老人的原名，膨胀 mu_*，阿陀磨须 ad_*）。
pub const FORM_TAGS: [&str; 7] = ["idle", "run", "hit", "dead", "attack", "skill", "skill2"];

/// 正在播的动画名 + 形态 → 该播的名字（不用换就是 None）。变回老人时把换上去的 mu_ / ad_ 换回来。
pub fn anim_for(cur: &str, form: Form) -> Option<String> {
    let base = cur.strip_prefix("mu_").or_else(|| cur.strip_prefix("ad_")).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = format!("{}{base}", form.prefix());
    (want != cur).then_some(want)
}

/// 每个宙斯上一帧的形态：(显示世界, 实体号) → 形态。尸体按它画。
#[derive(Default)]
pub struct Forms {
    seen: Vec<(usize, u64, Form)>,
}

impl Forms {
    /// 这一帧该画的形态：活着按 buff（记下来），播 dead 时 buff 没了就用记下的。
    pub fn form(&mut self, world: usize, key: u64, by_buff: Form, dead: bool) -> Form {
        let at = self.seen.iter().position(|e| e.0 == world && e.1 == key);
        if dead && by_buff == Form::Elder {
            return at.map_or(Form::Elder, |i| self.seen[i].2);
        }
        match at {
            Some(i) => self.seen[i].2 = by_buff,
            None => {
                self.seen.push((world, key, by_buff));
                if self.seen.len() > 64 {
                    self.seen.remove(0);
                }
            }
        }
        by_buff
    }
}

#[cfg(windows)]
mod view {
    //! 显示钩子：走显示世界的实体表，名字是 ragnarok_zeus 的按 buff 换正在播的动画名（league_gnar 的 view.rs 照抄）。

    use std::sync::{Mutex, Once};

    use super::{anim_for, log, Form, Forms, ADAMAS, MUSCLE};
    use game_places::hook::{Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR,
                            VALUE};

    const NAME: &[u8] = b"ragnarok_zeus";

    static FORMS: Mutex<Forms> = Mutex::new(Forms { seen: Vec::new() });
    static LOOKS: Mutex<Vec<(usize, u64, Form)>> = Mutex::new(Vec::new());
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

    /// 显示世界里每个宙斯：按身上的形态 buff 换正在播的动画名。
    unsafe fn dress(world: usize, ents: &[Ent]) {
        let Ok(mut forms) = FORMS.try_lock() else { return };
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
            let dead = cur == "dead" || cur == "mu_dead" || cur == "ad_dead";
            let form = forms.form(world, key, Form::of(has(v, ADAMAS), has(v, MUSCLE)), dead);
            if let Ok(mut looks) = LOOKS.try_lock() {
                let look = (world, key, form);
                if !looks.contains(&look) {
                    looks.retain(|l| !(l.0 == world && l.1 == key));
                    looks.push(look);
                    if looks.len() > 64 {
                        looks.remove(0);
                    }
                    log(format!("world {world:#x} Zeus #{key}: {form:?} (playing {cur})"));
                }
            }
            let Some(want) = anim_for(cur, form) else { continue };
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
        HOOK.call_once(|| match game_places::hook::add("ragnarok_zeus", dress, |m: &str| crate::wlog(m)) {
            Ok(p) => crate::wlog(format!("zeus: three bodies on: {p}")),
            Err(e) => crate::wlog(format!("zeus: three bodies off ({e}): only the changes show")),
        });
    }
}

// ===================== 配音规则（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    /// 一局第一次出场
    Start,
    /// 肌肉膨胀
    Expand,
    /// 放连拳（偶尔）
    Barrage,
    /// 杀了敌方英雄
    Kill,
    /// 复活回来
    Respawn,
}

pub const SECOND: usize = 60;
/// 任意两句之间至少隔这么久
pub const VOICE_GAP: usize = 8 * SECOND;

pub fn line_of(cue: Cue) -> &'static str {
    match cue {
        Cue::Start => "v_greet",
        Cue::Expand => "v_eager",
        Cue::Barrage => "v_fun",
        Cue::Kill => "v_taunt",
        Cue::Respawn => "v_anticipation",
    }
}

pub fn cue_cooldown(cue: Cue) -> usize {
    match cue {
        Cue::Start => usize::MAX,
        Cue::Expand => 30 * SECOND,
        Cue::Barrage => 30 * SECOND,
        Cue::Kill => 30 * SECOND,
        Cue::Respawn => 60 * SECOND,
    }
}

/// 放连拳时说不说：冷却到了也只有三成
pub const BARRAGE_CHANCE: u64 = 30;

/// 一份模拟里的配音节奏：上一句的拍数、每类上次的拍数。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<&'static str, usize>,
    started: bool,
}

impl Voice {
    fn key(cue: Cue) -> &'static str {
        line_of(cue)
    }

    /// 现在能不能说这一类，能就返回这句并记下来。出场那句一局只说一次。
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
        if cue == Cue::Start {
            self.started = true;
        }
        self.last.insert(k, tick);
        self.last_any = Some(tick);
        Some(line_of(cue))
    }
}

// ===================== 游戏里 =====================

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

#[derive(Clone, Default)]
struct ZeusVoice {
    me: usize,
    was_alive: bool,
    lives: usize,
    /// 上一拍是不是膨胀（数据的 `ragnarok_zeus_mu`）
    was_muscle: bool,
    /// 连拳的冷却上一拍是多少，用来认出这一拍刚放了连拳
    q_cd: usize,
    voice: Voice,
}

impl ZeusVoice {
    fn say(&mut self, sim: &mut StableSim<'_>, cue: Cue) {
        let tick = sim.tick();
        let Some(line) = self.voice.pick(cue, tick) else { return };
        let me = self.me;
        sim.play_sfx(&vo(line), me, &InputTargetV1::target(me));
        log(format!("[t={tick}] VOICE #{me}: {cue:?} -> {line}"));
    }
}

impl StablePassive for ZeusVoice {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // 复活是新的单位，死着的时候 on_update 不跑：这里先当成死的，下一拍活了就是新的一条命
        self.was_alive = false;
        self.was_muscle = false;
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        log(format!("[t={}] SPAWN #{me}: ragnarok.dll's Zeus (player {player}, team {team})", sim.tick()));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, player: usize, me: usize) {
        self.me = me;
        let Some((alive, muscle)) = sim.get_entity(me).map(|e| (e.is_alive(), has_buff(&e, MUSCLE))) else { return };
        if alive && !self.was_alive {
            self.lives += 1;
            let cue = if self.lives > 1 { Cue::Respawn } else { Cue::Start };
            self.say(sim, cue);
        }
        self.was_alive = alive;
        if !alive {
            self.was_muscle = false;
            return;
        }
        if muscle && !self.was_muscle {
            self.say(sim, Cue::Expand);
        }
        self.was_muscle = muscle;
        // 连拳的冷却从 0 跳上去就是刚放了
        let q_cd = sim.get_player(player).and_then(|p| p.cooldowns()).map_or(0, |c| c.1);
        if q_cd > self.q_cd + 30 && (rng % 100) < BARRAGE_CHANCE {
            self.say(sim, Cue::Barrage);
        }
        self.q_cd = q_cd;
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.me = me;
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.say(sim, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.was_alive = false;
        self.was_muscle = false;
        // 倒地声（延迟在 sound_info 里，对上死亡动作第 6 帧着地）
        let me = self.me;
        sim.play_sfx(&vo("dead"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// 宙斯的被动和显示钩子，注册进本包的模块（lib.rs 的 init，在 hd_engine::defer_display 之后）。
pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("zeus: {ID} v{VERSION} (Zeus: three bodies, voice lines) registered"));
    module.add_native_passive(format!("{ID}:voice"), ZeusVoice::default());
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "ragnarok.dll: Zeus (three bodies, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_body() {
        assert_eq!(anim_for("idle", Form::Muscle).as_deref(), Some("mu_idle"));
        assert_eq!(anim_for("run", Form::Adamas).as_deref(), Some("ad_run"));
        assert_eq!(anim_for("skill2", Form::Adamas).as_deref(), Some("ad_skill2"));
        assert_eq!(anim_for("mu_attack", Form::Adamas).as_deref(), Some("ad_attack")); // pressed down mid-swing
        assert_eq!(anim_for("ad_idle", Form::Elder).as_deref(), Some("idle")); // reverted
        assert_eq!(anim_for("idle", Form::Elder), None);
        assert_eq!(anim_for("mu_dead", Form::Muscle), None);
        // the changes are the data's own
        for t in ["expand", "ult", "revert", "idle_base", "bp"] {
            assert_eq!(anim_for(t, Form::Muscle), None, "{t}");
        }
    }

    #[test]
    fn adamas_wins_over_muscle() {
        assert_eq!(Form::of(true, true), Form::Adamas);
        assert_eq!(Form::of(false, true), Form::Muscle);
        assert_eq!(Form::of(false, false), Form::Elder);
    }

    #[test]
    fn the_corpse_keeps_its_body_and_the_respawn_is_old() {
        let mut f = Forms::default();
        assert_eq!(f.form(1, 7, Form::Elder, false), Form::Elder);
        assert_eq!(f.form(1, 7, Form::Muscle, false), Form::Muscle);
        assert_eq!(f.form(1, 7, Form::Elder, true), Form::Muscle); // dead: the buff is gone, still muscle
        assert_eq!(f.form(1, 7, Form::Elder, false), Form::Elder); // respawned old
        assert_eq!(f.form(1, 8, Form::Elder, true), Form::Elder); // another Zeus, never seen swollen
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert_eq!(v.pick(Cue::Start, 100), Some("v_greet"));
        assert_eq!(v.pick(Cue::Start, 100 + 600 * SECOND), None);
        assert_eq!(v.pick(Cue::Expand, 100 + VOICE_GAP - 1), None);
        assert_eq!(v.pick(Cue::Expand, 100 + VOICE_GAP), Some("v_eager"));
        assert_eq!(v.pick(Cue::Expand, 100 + VOICE_GAP + 30 * SECOND - 1), None);
        assert_eq!(v.pick(Cue::Kill, 100 + VOICE_GAP + 30 * SECOND), Some("v_taunt"));
    }

    /// Codex 的六句：五句这里放，宣传口号（battle_call）只放演示页。
    #[test]
    fn every_line_is_one_of_codexs() {
        let six = ["greet", "taunt", "eager", "fun", "battle_call", "anticipation"];
        for cue in [Cue::Start, Cue::Expand, Cue::Barrage, Cue::Kill, Cue::Respawn] {
            assert!(six.contains(&line_of(cue).trim_start_matches("v_")), "{cue:?}");
        }
    }
}
