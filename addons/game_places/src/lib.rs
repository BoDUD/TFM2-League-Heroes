//! 运行时在游戏 EXE 里找地址（用户 2026-10-20：「变身的api 官方没提供的api 想个方法做个动态寻地址的 后面游戏更新了我们
//! 维护压力小一点」「包括ppu」）。
//!
//! league.dll（PPU 高清帧：取动画表 / 贴图、战场画身体、界面的调用点）和 15 个整身变身附加包（显示更新的槽）以前都按
//! 写死的 rva 找游戏里的函数，游戏一更新全部失效，要人用 tools/re/find_build.py 重找、改 16 处。现在：
//!
//! - 特征码（`sigs.rs`，由 tools/re/make_sigs.py 从 league_main/src/build.rs 列的版本离线生成：跳转 / 调用的目标和
//!   rip 相对位移由 capstone 判定后挖空）在加载时按字节搜 `.text`；调用点靠扫 `E8 rel32`；函数边界用 EXE 自己的
//!   `.pdata`；界面画英雄的五处按「四次取尺寸的间距」打分（同 find_build.py 第 5 步）。不需要反汇编器。
//! - [`resolve`]：找全 league.dll 要的每个地址（[`Places`]），找不到或不唯一就报错（league.dll 照旧退回 1x 帧）。
//! - [`display`]：显示更新函数和它的槽，所有挂这个槽的 DLL 共用；第一个找到的写进进程环境变量
//!   `LEAGUE_DISPLAY_PLACES`（在任何钩子改槽之前），后来的直接读——槽被改过以后就搜不到原指针了。
//!
//! 结构体里的偏移（显示世界 +0x138 表、实体值 +0x40 / +0x68 / +0xb8 / +0x1b4 等）没有改成动态：0.6.3 → 0.6.4 一个都没变；
//! 变了的话钩子在日志里看得出（「Kayn seen 0 times」之类），到时再查。
//! 文件版 [`Image::from_file`] 给测试和离线检查用：`cargo test -p league_main` 拿游戏目录里的 EXE 跑一遍 [`resolve`]，
//! 必须和 build.rs 列的地址完全一致。

use std::collections::{HashMap, HashSet};

pub mod hook;
pub mod sigs;

/// 一段特征码：`mask` 为 0 的字节不比。
#[derive(Clone, Copy, Debug)]
pub struct Pattern {
    pub bytes: &'static [u8],
    pub mask: &'static [u8],
}

impl Pattern {
    fn at(&self, code: &[u8], i: usize) -> bool {
        i.checked_add(self.bytes.len()).is_some_and(|e| e <= code.len())
            && self.bytes.iter().zip(self.mask).enumerate().all(|(k, (b, m))| *m == 0 || code[i + k] == *b)
    }
}

/// 一个 PE 映像里要用的部分：`.text`、`.rdata`、`.pdata` 的函数表。
pub struct Image<'a> {
    /// 映像基址（文件里的 ImageBase，或进程里的模块地址）：`.rdata` 里的指针 = base + rva
    pub base: u64,
    pub text_rva: usize,
    pub text: &'a [u8],
    pub rdata_rva: usize,
    pub rdata: &'a [u8],
    /// (起点 rva, 终点 rva)，按起点排好
    pub funcs: Vec<(usize, usize)>,
}

fn u16_at(b: &[u8], o: usize) -> Option<u16> {
    Some(u16::from_le_bytes(b.get(o..o + 2)?.try_into().ok()?))
}

fn u32_at(b: &[u8], o: usize) -> Option<u32> {
    Some(u32::from_le_bytes(b.get(o..o + 4)?.try_into().ok()?))
}

fn u64_at(b: &[u8], o: usize) -> Option<u64> {
    Some(u64::from_le_bytes(b.get(o..o + 8)?.try_into().ok()?))
}

/// PE 头：(映像基址, [(名字, rva, 映像里的大小, 文件偏移, 文件里的大小)], .pdata 的 (rva, 大小))
#[allow(clippy::type_complexity)]
fn headers(h: &[u8]) -> Option<(u64, Vec<([u8; 8], usize, usize, usize, usize)>, (usize, usize))> {
    let pe = u32_at(h, 0x3c)? as usize;
    if h.get(pe..pe + 4)? != b"PE\0\0" {
        return None;
    }
    let coff = pe + 4;
    let n = u16_at(h, coff + 2)? as usize;
    let opt_size = u16_at(h, coff + 16)? as usize;
    let opt = coff + 20;
    if u16_at(h, opt)? != 0x20b {
        return None; // PE32+ only
    }
    let base = u64_at(h, opt + 24)?;
    let dirs = opt + 112;
    let pdata = (u32_at(h, dirs + 3 * 8)? as usize, u32_at(h, dirs + 3 * 8 + 4)? as usize);
    let mut secs = Vec::new();
    for k in 0..n {
        let s = opt + opt_size + 40 * k;
        let name: [u8; 8] = h.get(s..s + 8)?.try_into().ok()?;
        secs.push((name, u32_at(h, s + 12)? as usize, u32_at(h, s + 8)? as usize, u32_at(h, s + 20)? as usize,
                   u32_at(h, s + 16)? as usize));
    }
    Some((base, secs, pdata))
}

fn named(n: &[u8; 8], want: &str) -> bool {
    n.split(|c| *c == 0).next() == Some(want.as_bytes())
}

fn funcs_of(raw: &[u8]) -> Vec<(usize, usize)> {
    let mut f: Vec<(usize, usize)> = raw
        .chunks_exact(12)
        .map(|c| (u32::from_le_bytes(c[0..4].try_into().unwrap()) as usize, u32::from_le_bytes(c[4..8].try_into().unwrap()) as usize))
        .filter(|f| f.0 != 0 && f.1 > f.0)
        .collect();
    f.sort_unstable();
    f
}

impl<'a> Image<'a> {
    /// 磁盘上的 EXE（测试、离线检查）。
    pub fn from_file(data: &'a [u8]) -> Result<Image<'a>, String> {
        let (base, secs, pdata) = headers(data).ok_or("not a PE32+ file")?;
        let sec = |name: &str| secs.iter().find(|s| named(&s.0, name)).ok_or(format!("no {name}"));
        let file = |s: &([u8; 8], usize, usize, usize, usize)| -> Result<&'a [u8], String> {
            data.get(s.3..s.3 + s.2.min(s.4)).ok_or_else(|| "section past the file".to_string())
        };
        let (t, r) = (sec(".text")?, sec(".rdata")?);
        let p = secs.iter().find(|s| s.1 <= pdata.0 && pdata.0 < s.1 + s.2).ok_or("no .pdata")?;
        let praw = data.get(p.3 + pdata.0 - p.1..p.3 + pdata.0 - p.1 + pdata.1).ok_or(".pdata past the file")?;
        Ok(Image { base, text_rva: t.1, text: file(t)?, rdata_rva: r.1, rdata: file(r)?, funcs: funcs_of(praw) })
    }

    /// 本进程的主模块（游戏 EXE），直接读映射好的内存。
    ///
    /// # Safety
    /// `module` must be the base of a PE32+ image mapped in this process (GetModuleHandleW(null)).
    pub unsafe fn from_module(module: usize) -> Result<Image<'static>, String> {
        let head = std::slice::from_raw_parts(module as *const u8, 0x1000);
        let (_, secs, pdata) = headers(head).ok_or("the module's headers are not PE32+")?;
        let sec = |name: &str| secs.iter().find(|s| named(&s.0, name)).ok_or(format!("no {name}"));
        let (t, r) = (sec(".text")?, sec(".rdata")?);
        let mem = |rva: usize, len: usize| std::slice::from_raw_parts((module + rva) as *const u8, len);
        Ok(Image {
            base: module as u64,
            text_rva: t.1,
            text: mem(t.1, t.2),
            rdata_rva: r.1,
            rdata: mem(r.1, r.2),
            funcs: funcs_of(mem(pdata.0, pdata.1)),
        })
    }

    /// [`Image::from_module`] without the .pdata function table (enough for [`display`]).
    ///
    /// # Safety
    /// As [`Image::from_module`].
    pub unsafe fn from_module_light(module: usize) -> Result<Image<'static>, String> {
        let head = std::slice::from_raw_parts(module as *const u8, 0x1000);
        let (_, secs, _) = headers(head).ok_or("the module's headers are not PE32+")?;
        let sec = |name: &str| secs.iter().find(|s| named(&s.0, name)).ok_or(format!("no {name}"));
        let (t, r) = (sec(".text")?, sec(".rdata")?);
        let mem = |rva: usize, len: usize| std::slice::from_raw_parts((module + rva) as *const u8, len);
        Ok(Image { base: module as u64, text_rva: t.1, text: mem(t.1, t.2), rdata_rva: r.1, rdata: mem(r.1, r.2),
                   funcs: Vec::new() })
    }

    /// `len` bytes at `rva` in .text or .rdata.
    pub fn read(&self, rva: usize, len: usize) -> Option<&'a [u8]> {
        for (start, s) in [(self.text_rva, self.text), (self.rdata_rva, self.rdata)] {
            if rva >= start && rva + len <= start + s.len() {
                return Some(&s[rva - start..rva - start + len]);
            }
        }
        None
    }

    /// Every rva in .text where `p` matches.
    pub fn find(&self, p: &Pattern) -> Vec<usize> {
        // the first unmasked byte as the anchor
        let Some(k) = p.mask.iter().position(|m| *m != 0) else { return Vec::new() };
        let first = p.bytes[k];
        let t = self.text;
        let mut out = Vec::new();
        let mut i = k;
        while i < t.len() {
            match t[i..].iter().position(|b| *b == first) {
                None => break,
                Some(off) => {
                    let at = i + off - k;
                    if i + off >= k && p.at(t, at) {
                        out.push(self.text_rva + at);
                    }
                    i += off + 1;
                }
            }
        }
        out
    }

    /// The target of the `call rel32` at `rva`, if one is there.
    pub fn call_target(&self, rva: usize) -> Option<usize> {
        let b = self.read(rva, 5)?;
        (b[0] == 0xe8).then(|| (rva as i64 + 5 + i32::from_le_bytes(b[1..5].try_into().unwrap()) as i64) as usize)
    }

    /// Every `call rel32` in .text to one of `targets`, in one pass: target -> call sites.
    pub fn calls_to(&self, targets: &HashSet<usize>) -> HashMap<usize, Vec<usize>> {
        let t = self.text;
        let mut out: HashMap<usize, Vec<usize>> = HashMap::new();
        let mut i = 0;
        while let Some(off) = t[i..].iter().position(|b| *b == 0xe8) {
            let at = i + off;
            if at + 5 <= t.len() {
                let rel = i32::from_le_bytes(t[at + 1..at + 5].try_into().unwrap()) as i64;
                let tgt = (self.text_rva as i64 + at as i64 + 5 + rel) as usize;
                if targets.contains(&tgt) {
                    out.entry(tgt).or_default().push(self.text_rva + at);
                }
            }
            i = at + 1;
        }
        out
    }

    /// The function (from .pdata) holding `rva`.
    pub fn func_of(&self, rva: usize) -> Option<(usize, usize)> {
        let i = self.funcs.partition_point(|f| f.0 <= rva);
        (i > 0 && self.funcs[i - 1].0 <= rva && rva < self.funcs[i - 1].1).then(|| self.funcs[i - 1])
    }

    /// The `call rel32` targets inside [from, to).
    fn calls_in(&self, from: usize, to: usize) -> Vec<usize> {
        let mut out = Vec::new();
        let mut a = from;
        while a + 5 <= to {
            if let Some(t) = self.call_target(a) {
                if self.func_of(t).is_some_and(|f| f.0 == t) {
                    out.push(t);
                }
            }
            a += 1;
        }
        out
    }

    /// The aligned qwords in .rdata equal to base + `rva`.
    pub fn pointers_to(&self, rva: usize) -> Vec<usize> {
        let want = (self.base + rva as u64).to_le_bytes();
        self.rdata
            .chunks_exact(8)
            .enumerate()
            .filter(|(_, c)| *c == want)
            .map(|(k, _)| self.rdata_rva + 8 * k)
            .collect()
    }
}

fn one<T: Copy + std::fmt::LowerHex>(what: &str, v: &[T]) -> Result<T, String> {
    match v {
        [x] => Ok(*x),
        [] => Err(format!("{what}: not found")),
        _ => Err(format!("{what}: {} candidates ({:#x}, {:#x}, ...)", v.len(), v[0], v[1])),
    }
}

/// league.dll 要的地址（rva），对应 league_main/src/build.rs 的 `Build`。
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Places {
    pub anim: usize,
    pub sheet: usize,
    pub hash: usize,
    pub display_fn: usize,
    pub display_slot: usize,
    pub battle_anim_ret: Vec<usize>,
    pub battle_size_ret: Vec<usize>,
    pub ui_anim_ret: Vec<usize>,
    pub ui_size_ret: Vec<usize>,
    pub ui_sized_anim_ret: Vec<usize>,
    pub ui_sized_size_ret: Vec<usize>,
    pub body_draw: usize,
    pub cmd_grow: usize,
    /// how each UI drawer was told apart (for the log)
    pub notes: Vec<String>,
}

/// A UI drawer candidate: (spacing score, its call of the anim lookup, its four size asks).
type Scored = (usize, usize, [usize; 4]);

/// An indirect call (`call reg`, `call r8-r15`, `call [reg+disp8]`) starting at `i`: its length.
fn indirect_call(code: &[u8], i: usize) -> Option<usize> {
    let b = |k: usize| code.get(i + k).copied();
    match (b(0)?, b(1)?, b(2)) {
        (0xff, m, _) if (0xd0..=0xd7).contains(&m) => Some(2),
        (0xff, m, Some(_)) if (0x50..=0x57).contains(&m) && m != 0x54 => Some(3),
        (0x41, 0xff, Some(m)) if (0xd0..=0xd7).contains(&m) => Some(3),
        (0x41, 0xff, Some(m)) if (0x50..=0x57).contains(&m) && m != 0x54 => Some(4),
        _ => None,
    }
}

/// Finds every place of [`Places`] in `img` by the patterns of [`sigs`] (find_build.py's steps without a disassembler).
pub fn resolve(img: &Image) -> Result<Places, String> {
    resolve_with(img, None)
}

/// [`resolve`], with the display handler and slot (rvas) given when already known - in the game process take them from
/// [`display`] (another DLL may have swapped the slot already, and then it can no longer be found by its pointer).
pub fn resolve_with(img: &Image, display: Option<(usize, usize)>) -> Result<Places, String> {
    use sigs::*;
    // 1. the hash and the 33 HashMap<String, _>::get heads calling it
    let hashes: HashSet<usize> = img.find(&HASH).into_iter().collect();
    let lookups: Vec<usize> = img
        .find(&ANIM)
        .into_iter()
        .filter(|f| img.call_target(f + HASH_CALL).is_some_and(|t| hashes.contains(&t)))
        .collect();
    let hash_t: Vec<usize> = {
        let mut v: Vec<usize> = lookups.iter().filter_map(|f| img.call_target(f + HASH_CALL)).collect();
        v.sort_unstable();
        v.dedup();
        v
    };
    let hash = one("the hash the lookups call", &hash_t)?;
    // 2. the battlefield frame lookup: a caller of a lookup with its two size asks at the old offsets
    let set: HashSet<usize> = lookups.iter().copied().collect();
    let callers = img.calls_to(&set);
    let mut hits = Vec::new();
    for f in &lookups {
        for c in callers.get(f).into_iter().flatten() {
            if BATTLE_ASKS.iter().all(|(d, x)| img.read(c + d, x.len()) == Some(*x)) {
                hits.push((*f, *c));
            }
        }
    }
    let (anim, frame_call) = match hits.as_slice() {
        [h] => *h,
        [] => return Err("the battlefield frame lookup's call: not found".into()),
        _ => return Err(format!("the battlefield frame lookup's call: {} candidates", hits.len())),
    };
    let frame_fn = img.func_of(frame_call).ok_or("the frame lookup has no .pdata entry")?;
    let mut sheets: Vec<usize> =
        img.calls_in(frame_fn.0, frame_fn.1).into_iter().filter(|t| set.contains(t) && *t != anim).collect();
    sheets.sort_unstable();
    sheets.dedup();
    let sheet = one("the sheet lookup in the frame lookup", &sheets)?;
    let mut battle_size_ret: Vec<usize> = BATTLE_ASKS.iter().map(|(d, x)| frame_call + d + x.len()).collect();
    // 3. the body draw: a caller of the frame lookup holding its four size asks at the old spacing
    let fset: HashSet<usize> = [frame_fn.0].into_iter().collect();
    let mut bodies = Vec::new();
    for c in img.calls_to(&fset).remove(&frame_fn.0).unwrap_or_default() {
        let Some(f) = img.func_of(c) else { continue };
        let Some(code) = img.read(f.0, f.1 - f.0) else { continue };
        let first = BODY_ASKS[0].1;
        let mut i = 0;
        while let Some(off) = code[i..].windows(first.len()).position(|w| w == first) {
            let p = f.0 + i + off;
            if BODY_ASKS.iter().all(|(d, x)| img.read(p + d, x.len()) == Some(*x)) {
                bodies.push((f.0, p));
            }
            i += off + 1;
        }
    }
    bodies.sort_unstable();
    bodies.dedup();
    let (body_draw, ask0) = match bodies.as_slice() {
        [b] => *b,
        [] => return Err("the body draw (four size asks at the old spacing): not found".into()),
        _ => return Err(format!("the body draw: {} candidates", bodies.len())),
    };
    battle_size_ret.extend(BODY_ASKS.iter().map(|(d, x)| ask0 + d + x.len()));
    // the entity render reads `movss xmm, [reg+0x1b4]` soon after its call of the body draw (the hooks rely on it)
    let bset: HashSet<usize> = [body_draw].into_iter().collect();
    let renders: Vec<usize> = img
        .calls_to(&bset)
        .remove(&body_draw)
        .unwrap_or_default()
        .into_iter()
        .filter(|c| {
            img.read(*c, 0x200).is_some_and(|w| {
                w.windows(8).any(|x| x[0] == 0xf3 && x[1] == 0x0f && x[2] == 0x10 && (0x80..0xc0).contains(&x[3])
                    && x[3] & 7 != 4 && x[4..] == [0xb4, 0x01, 0x00, 0x00])
            })
        })
        .collect();
    one("the entity render (movss [reg+0x1b4] after the body draw)", &renders)?;
    let body_fn = img.func_of(body_draw).ok_or("the body draw has no .pdata entry")?;
    let mut grows: Vec<usize> = img
        .calls_in(body_fn.0, body_fn.1)
        .into_iter()
        .filter(|g| img.read(*g, 0x40).is_some_and(|h| h.windows(GROW_MARK.len()).any(|w| w == GROW_MARK)))
        .collect();
    grows.sort_unstable();
    grows.dedup();
    let cmd_grow = one("grow_one of the 0xd0-byte draw commands", &grows)?;
    // 4. the display handler and its slot
    let (display_fn, display_slot) = match display {
        Some(d) => d,
        None => display_in(img)?,
    };
    // 5. the UI drawers: every caller of the anim lookup scored by its four indirect calls' spacing
    let aset: HashSet<usize> = [anim].into_iter().collect();
    let anim_callers = img.calls_to(&aset).remove(&anim).unwrap_or_default();
    let mut sites: Vec<(usize, Vec<Scored>)> = Vec::new();
    for (old_call, old) in UI {
        let mut scored = Vec::new();
        for c in &anim_callers {
            let Some(code) = img.read(*c, 0x800) else { continue };
            let mut asks = Vec::new();
            let mut i = 5;
            while i < code.len() {
                if let Some(n) = indirect_call(code, i) {
                    asks.push((c + i, c + i + n - (c + 5)));
                    i += n;
                } else {
                    i += 1;
                }
            }
            let mut best: Option<(usize, [usize; 4])> = None;
            for s in 0..asks.len().saturating_sub(3) {
                let w: Vec<usize> = asks[s..s + 4].iter().map(|a| a.1).collect();
                let d = (0..4).map(|j| (w[j] as i64 - w[0] as i64 - (old[j] as i64 - old[0] as i64)).unsigned_abs() as usize)
                    .sum::<usize>()
                    + (w[0] as i64 - old[0] as i64).unsigned_abs() as usize / 16;
                if best.is_none_or(|b| d < b.0) {
                    best = Some((d, [asks[s].0, asks[s + 1].0, asks[s + 2].0, asks[s + 3].0]));
                }
            }
            if let Some((d, w)) = best {
                scored.push((d, *c, w));
            }
        }
        scored.sort_unstable();
        sites.push((*old_call, scored));
    }
    let mut chosen: HashMap<usize, (Scored, String)> = HashMap::new();
    for (k, (_, scored)) in sites.iter().enumerate() {
        if let Some(first) = scored.first() {
            if first.0 <= 1 && (scored.len() == 1 || scored[1].0 >= first.0 + 5) {
                chosen.insert(k, (*first, "clear".into()));
            }
        }
    }
    for (k, (old_call, scored)) in sites.iter().enumerate() {
        if chosen.contains_key(&k) {
            continue;
        }
        let taken: HashSet<usize> = chosen.values().map(|v| v.0 .1).collect();
        let mut best: Option<(usize, Scored, bool)> = None;
        for s in scored {
            if taken.contains(&s.1) {
                continue;
            }
            let mismatch = chosen
                .iter()
                .map(|(j, v)| ((v.0 .1 as i64 - s.1 as i64) - (sites[*j].0 as i64 - *old_call as i64)).unsigned_abs() as usize)
                .min()
                .unwrap_or(usize::MAX);
            let total = s.0 + if mismatch < 0x100 { 0 } else { 5 };
            if best.as_ref().is_none_or(|b| total < b.0) {
                best = Some((total, *s, mismatch < 0x100));
            }
        }
        // at run time only a drawer next to one already found counts (find_build.py lets a human decide the rest)
        match best {
            Some((_, s, true)) => {
                chosen.insert(k, (s, "next to a found drawer".into()));
            }
            _ => return Err(format!("UI drawer {k}: no clear match (best spacing scores {:?})",
                                    sites[k].1.iter().take(2).map(|s| s.0).collect::<Vec<_>>())),
        }
    }
    let mut ui_anim_ret = Vec::new();
    let mut ui_size_ret = Vec::new();
    let mut notes = Vec::new();
    for k in 0..sites.len() {
        let ((d, c, w), how) = &chosen[&k];
        ui_anim_ret.push(c + 5);
        for a in w {
            let n = img.read(*a, 4).and_then(|b| indirect_call(b, 0)).unwrap_or(2);
            ui_size_ret.push(a + n);
        }
        notes.push(format!("UI drawer {k}: call {c:#x}, spacing {d}, {how}"));
    }
    let ui_sized_anim_ret: Vec<usize> = UI_SIZED.iter().map(|k| ui_anim_ret[*k]).collect();
    let ui_sized_size_ret: Vec<usize> = UI_SIZED.iter().flat_map(|k| ui_size_ret[4 * k..4 * k + 4].to_vec()).collect();
    // the hooks replace a 12-byte prologue + `sub rsp`
    for (name, f) in [("anim", anim), ("sheet", sheet), ("body draw", body_draw)] {
        if img.read(f, PROLOGUE.len()) != Some(PROLOGUE) {
            return Err(format!("{name} {f:#x}: not the prologue the hooks replace"));
        }
    }
    Ok(Places {
        anim,
        sheet,
        hash,
        display_fn,
        display_slot,
        battle_anim_ret: vec![frame_call + 5],
        battle_size_ret,
        ui_anim_ret,
        ui_size_ret,
        ui_sized_anim_ret,
        ui_sized_size_ret,
        body_draw,
        cmd_grow,
        notes,
    })
}

/// The display-update handler (by its head) and the .rdata slot pointing at it.
pub fn display_in(img: &Image) -> Result<(usize, usize), String> {
    // the listed build's pair first, by the handler's head alone (no scan; its slot may already hold another hook, as
    // the fixed-address add-ons always assumed)
    if sigs::DISPLAY.at(img.text, sigs::OLD_DISPLAY_FN.wrapping_sub(img.text_rva)) {
        return Ok((sigs::OLD_DISPLAY_FN, sigs::OLD_DISPLAY_SLOT));
    }
    let f = one("the display handler", &img.find(&sigs::DISPLAY))?;
    let s = one("the display slot", &img.pointers_to(f))?;
    Ok((f, s))
}

/// 进程环境变量：`<exe 映像大小>:<函数 rva>:<槽 rva>`，第一个找到的 DLL 写，别的 DLL 读（槽一被换就搜不到原指针了）。
pub const ENV: &str = "LEAGUE_DISPLAY_PLACES";

/// 本进程里显示更新函数和槽的地址（绝对地址）：先看环境变量（别的 DLL 已经找过），再在映像里找，找到就写进环境变量。
/// 调用方必须在换槽之前调用。
pub fn display() -> Result<(usize, usize), String> {
    #[cfg(windows)]
    {
        #[link(name = "kernel32")]
        extern "system" {
            fn GetModuleHandleW(name: *const u16) -> usize;
        }
        let module = unsafe { GetModuleHandleW(std::ptr::null()) };
        if module == 0 {
            return Err("no module handle".into());
        }
        // .text and .rdata only (the .pdata function table is for resolve)
        let img = unsafe { Image::from_module_light(module)? };
        let tag = img.text.len();
        if let Ok(v) = std::env::var(ENV) {
            let p: Vec<usize> = v.split(':').filter_map(|x| usize::from_str_radix(x.trim_start_matches("0x"), 16).ok()).collect();
            if let [size, f, s] = p[..] {
                if size == tag && sigs::DISPLAY.at(img.text, f.wrapping_sub(img.text_rva)) {
                    return Ok((module + f, module + s));
                }
            }
        }
        let (f, s) = display_in(&img)?;
        std::env::set_var(ENV, format!("{tag:x}:{f:x}:{s:x}"));
        Ok((module + f, module + s))
    }
    #[cfg(not(windows))]
    Err("not Windows".into())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_pattern_skips_its_masked_bytes() {
        let p = Pattern { bytes: &[0xe8, 0, 0, 0, 0, 0x48], mask: &[1, 0, 0, 0, 0, 1] };
        let code = [0x90, 0xe8, 1, 2, 3, 4, 0x48, 0xe8, 9, 9, 9, 9, 0x49];
        assert!(p.at(&code, 1));
        assert!(!p.at(&code, 7));
    }

    #[test]
    fn indirect_calls_are_told_by_their_bytes() {
        assert_eq!(indirect_call(&[0xff, 0xd3], 0), Some(2));
        assert_eq!(indirect_call(&[0x41, 0xff, 0xd7], 0), Some(3));
        assert_eq!(indirect_call(&[0xff, 0x53, 0x28], 0), Some(3));
        assert_eq!(indirect_call(&[0xff, 0x54, 0x24], 0), None); // a SIB form: not one of the asks
        assert_eq!(indirect_call(&[0xe8, 0x00], 0), None);
    }
}
