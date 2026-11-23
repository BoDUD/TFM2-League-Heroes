//! 拂面（`baixi_fumian`）：川剧变脸红/黑/金三脸显示钩子（参照宙斯三形态钩子 `ragnarok/src/zeus.rs`）。
//!
//! 身上 buff：`baixi_fumian_face_blk` 黑脸、`baixi_fumian_face_gld` 金脸，都没有则是红脸。
//! `ult` 变脸动作本身已逐帧闪过红/黑/金三张脸，不替换；其余动作实时切为 `blk_*` / `gld_*`，阵亡保留死前脸谱。

use mod_api_stable::*;

use crate::voice::HeroVoice;

pub const ID: &str = "baixi_fumian";
pub const FACE_BLK: &str = "baixi_fumian_face_blk";
pub const FACE_GLD: &str = "baixi_fumian_face_gld";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Face {
    Red,
    Black,
    Gold,
}

impl Face {
    pub fn of(blk: bool, gld: bool) -> Face {
        if gld {
            Face::Gold
        } else if blk {
            Face::Black
        } else {
            Face::Red
        }
    }

    fn prefix(self) -> &'static str {
        match self {
            Face::Red => "",
            Face::Black => "blk_",
            Face::Gold => "gld_",
        }
    }
}

pub const FACE_TAGS: [&str; 7] = ["idle", "run", "hit", "dead", "attack", "skill", "skill2"];

pub fn anim_for(cur: &str, face: Face) -> Option<String> {
    let base = cur
        .strip_prefix("blk_")
        .or_else(|| cur.strip_prefix("gld_"))
        .filter(|b| FACE_TAGS.contains(b))
        .unwrap_or(cur);
    if !FACE_TAGS.contains(&base) {
        return None;
    }
    let want = format!("{}{base}", face.prefix());
    (want != cur).then_some(want)
}

#[derive(Default)]
pub struct Faces {
    seen: Vec<(usize, u64, Face)>,
}

impl Faces {
    pub fn face(&mut self, world: usize, key: u64, by_buff: Face, dead: bool) -> Face {
        let at = self.seen.iter().position(|e| e.0 == world && e.1 == key);
        if dead && by_buff == Face::Red {
            return at.map_or(Face::Red, |i| self.seen[i].2);
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
    use std::sync::{Mutex, Once};

    use super::{anim_for, Face, Faces, FACE_BLK, FACE_GLD};
    use game_places::hook::{
        Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR, VALUE,
    };

    const NAME: &[u8] = b"baixi_fumian";

    static FACES: Mutex<Faces> = Mutex::new(Faces { seen: Vec::new() });
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

    unsafe fn has(v: usize, name: &str) -> bool {
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        plausible(bp)
            && bn <= 256
            && (0..bn).any(|k| {
                let b = bp + k * BUFF_SIZE;
                let (p, n) = (q(b + 8), q(b + 0x10));
                plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
            })
    }

    unsafe fn dress(world: usize, ents: &[Ent]) {
        let Ok(mut faces) = FACES.try_lock() else { return };
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
            let dead = cur == "dead" || cur == "blk_dead" || cur == "gld_dead";
            let face = faces.face(world, key, Face::of(has(v, FACE_BLK), has(v, FACE_GLD)), dead);
            let Some(want) = anim_for(cur, face) else { continue };
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

    pub fn install_once() {
        HOOK.call_once(|| match game_places::hook::add("baixi_fumian", dress, |m: &str| crate::wlog(m)) {
            Ok(p) => crate::wlog(format!("fumian: three faces hook on: {p}")),
            Err(e) => crate::wlog(format!("fumian: three faces hook off ({e})")),
        });
    }
}

pub fn register(host: &StableHost, module: &mut StableMod) {
    module.add_native_passive(format!("{ID}:voice"), HeroVoice::new(ID));
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "baixi.dll: Fumian (3-face Opera mask display hook + voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn face_swap_anim_tags() {
        assert_eq!(anim_for("idle", Face::Black).as_deref(), Some("blk_idle"));
        assert_eq!(anim_for("run", Face::Gold).as_deref(), Some("gld_run"));
        assert_eq!(anim_for("blk_skill", Face::Gold).as_deref(), Some("gld_skill"));
        assert_eq!(anim_for("gld_idle", Face::Red).as_deref(), Some("idle"));
        assert_eq!(anim_for("ult", Face::Black), None);
        assert_eq!(anim_for("bp", Face::Gold), None);
    }

    #[test]
    fn corpse_keeps_face() {
        let mut f = Faces::default();
        assert_eq!(f.face(1, 5, Face::Gold, false), Face::Gold);
        assert_eq!(f.face(1, 5, Face::Red, true), Face::Gold);
        assert_eq!(f.face(1, 5, Face::Red, false), Face::Red);
    }
}
