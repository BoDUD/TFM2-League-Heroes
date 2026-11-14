//! 狗群跟着她：主包把两只伙伴画进纳亚菲利自己的每一帧（待机、跑、普攻、技能、受击、阵亡），转向、站着 / 跑着都由游戏
//! 按她自己的帧自动处理（附加包没有单独画一个跟着单位跑的精灵的接口：客户端的 draw_sprite 读不到对局里的实体）。
//! 暴吼（大招起手的 `league_naafiri_pack4`）期间狗群是四只：照 league_gnar 的 view.rs（整身变巨型，game_places::hook::add
//! 一个接一个调用），名字是 `league_naafiri` 的实体身上有 `league_naafiri_pack4` 时，正在播的动作换成她图里四只狗的
//! `p4_*` 版本。阵亡时 buff 清掉：尸体按倒下前那一帧的狗群画。找不到槽时什么都不做，暴吼时还是两只狗。
//! 0.2.0（2026-11-14）：狗群是真的单位时她身上挂着 `league_naafiri_solo`，动作换成图里没有狗的 `solo_*` 版本（暴吼时也是：
//! 多来的两只也是单位）。

use std::sync::{Mutex, Once};

use super::{wlog, PACK4, SOLO};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 纳亚菲利在画面实体里的名字。
pub const NAME: &[u8] = b"league_naafiri";

/// 她图里每个动作都有四只狗的 `p4_*` 版本：游戏自动播的 idle / run / hit / dead / attack（普攻第一 tick）和数据用
/// `CasterAnimation` 播的 skill / skill2 / ult（暴吼）/ ult_b（飞扑）。
pub const FORM_TAGS: [&str; 9] = ["idle", "run", "hit", "dead", "attack", "skill", "skill2", "ult", "ult_b"];
const PREFIXES: [&str; 2] = ["p4_", "solo_"];

/// 她画几只狗：两只（她自己的帧）、四只（暴吼，`p4_*`）、一只都不画（狗群是真的单位，`solo_*`）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Form {
    #[default]
    Two,
    Four,
    Solo,
}

impl Form {
    /// From her buffs: the packmates as units win over the roar (the roar's two are units too then).
    pub fn of(four: bool, solo: bool) -> Form {
        if solo {
            Form::Solo
        } else if four {
            Form::Four
        } else {
            Form::Two
        }
    }
}

/// 正在播的动画名 + 画几只狗 → 该播的名字（不用换就是 None）。暴吼 / 单位结束时把本包换上去的 `p4_idle`、`solo_idle` 等换回来。
pub fn anim_for(cur: &str, form: Form) -> Option<String> {
    let base = PREFIXES.iter().find_map(|p| cur.strip_prefix(p)).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = match form {
        Form::Two => base.to_string(),
        Form::Four => format!("p4_{base}"),
        Form::Solo => format!("solo_{base}"),
    };
    (want != cur).then_some(want)
}

/// 每个纳亚菲利上一帧的狗群：(显示世界, 实体号) → 画几只。尸体按它画。
#[derive(Default)]
pub struct Packs {
    seen: Vec<(usize, u64, Form)>,
}

impl Packs {
    /// 这一帧该画几只：活着按 buff（记下来），播 dead 时用记下的。
    pub fn form(&mut self, world: usize, key: u64, now: Form, dead: bool) -> Form {
        let at = self.seen.iter().position(|e| e.0 == world && e.1 == key);
        if dead {
            return match at.map(|i| self.seen[i].2) {
                Some(f) if f != Form::Two => f,
                _ => now,
            };
        }
        match at {
            Some(i) => self.seen[i].2 = now,
            None => {
                self.seen.push((world, key, now));
                if self.seen.len() > 64 {
                    self.seen.remove(0);
                }
            }
        }
        now
    }
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    looks: Vec<(usize, u64, Form)>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new() });
static PACKS: Mutex<Packs> = Mutex::new(Packs { seen: Vec::new() });
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

/// 显示世界里每个纳亚菲利：暴吼时正在播的动作换成四只狗的版本。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut packs) = PACKS.try_lock() else { return };
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Naafiri seen {} times, {} animation names swapped in 10 s",
                st.calls, st.seen, st.writes));
        }
        st.last = Some(now);
        st.calls = 0;
        st.seen = 0;
        st.writes = 0;
    }
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
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        let named = |name: &str| plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
        });
        let (has, solo) = (named(PACK4), named(SOLO));
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let dead = cur == "dead" || cur == "p4_dead" || cur == "solo_dead";
        let form = packs.form(world, key, Form::of(has, solo), dead);
        let look = (world, key, form);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Naafiri #{key}: {} (playing {cur}{})", match form {
                Form::Four => "FOUR hounds",
                Form::Solo => "her solo frames (her packmates are units)",
                Form::Two => "two hounds",
            }, if dead && form != Form::of(has, solo) { ", pack remembered" } else { "" }));
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
        st.writes += 1;
    }
}

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match game_places::hook::add("league_naafiri", dress) {
            Ok((slot, prev)) => wlog(format!(
                "four hounds in the roar on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("four hounds off ({e}): the roar shows her two")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_pack() {
        assert_eq!(anim_for("idle", Form::Four).as_deref(), Some("p4_idle"));
        assert_eq!(anim_for("run", Form::Four).as_deref(), Some("p4_run"));
        assert_eq!(anim_for("ult_b", Form::Four).as_deref(), Some("p4_ult_b")); // the pounce after the roar
        assert_eq!(anim_for("skill", Form::Four).as_deref(), Some("p4_skill"));
        assert_eq!(anim_for("p4_attack", Form::Four), None);
        assert_eq!(anim_for("p4_idle", Form::Two).as_deref(), Some("idle")); // the roar is over
        assert_eq!(anim_for("idle", Form::Two), None);
        assert_eq!(anim_for("hd_idle", Form::Four), None); // not one of hers
        // 0.2.0: the packmates as units - her solo frames, in the roar too
        assert_eq!(anim_for("attack", Form::Solo).as_deref(), Some("solo_attack"));
        assert_eq!(anim_for("p4_run", Form::Solo).as_deref(), Some("solo_run"));
        assert_eq!(anim_for("solo_idle", Form::Two).as_deref(), Some("idle"));
        assert_eq!(anim_for("solo_dead", Form::Solo), None);
        assert_eq!(Form::of(true, true), Form::Solo);
        assert_eq!(Form::of(true, false), Form::Four);
        assert_eq!(Form::of(false, false), Form::Two);
    }

    #[test]
    fn the_corpse_keeps_the_pack_and_the_respawn_has_two() {
        let mut f = Packs::default();
        assert_eq!(f.form(1, 7, Form::Two, false), Form::Two);
        assert_eq!(f.form(1, 7, Form::Four, false), Form::Four); // roared
        assert_eq!(f.form(1, 7, Form::Two, true), Form::Four); // dead: the buff is gone, still four
        assert_eq!(f.form(1, 7, Form::Two, false), Form::Two); // respawned with two
        assert_eq!(f.form(1, 7, Form::Solo, false), Form::Solo); // the packmates are units
        assert_eq!(f.form(1, 7, Form::Two, true), Form::Solo); // dead: no pack drawn on her corpse
    }
}
