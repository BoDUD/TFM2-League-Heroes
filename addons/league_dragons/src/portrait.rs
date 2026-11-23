//! 界面上的小龙头像跟着这一条的元素（0.5.6，用户 2026-11-23：「小龙有个问题 这里模型没变 导致游戏对局里小龙头像也会一直
//! 显示这个官方的小龙 而不是随机的元素龙」，截图是游戏百科「地图资源」页）。
//!
//! 战场上的小龙是显示钩子按资源名换的（src/skin.rs），可界面上画小龙的地方——百科「地图资源」的格子（`object_slot` 的
//! `icon`）和右边的大图、比赛里右边击杀记录的两个头像格（`kill_log`）、中间的击杀大字（`center_kill`）、左下角点选单位的
//! 小面板（`champion_tooltip` 的 `face`）——都是游戏按名字 `asset/base/aseprite_resources/ingame/serpen` 自己取动画表、
//! 自己算 UV，不经过显示世界，所以一直是原版小龙。分两步：
//!
//! - `mod.override_info` 把 `ingame/serpen` 本身指到炼狱亚龙（和男爵的 `ingame/epic` 一样）。游戏算 UV 用的就是炼狱亚龙
//!   图上的帧，百科和头像至少都是联盟的亚龙——这一步不用任何代码。
//! - 每帧 `post_render`（游戏这一帧的界面命令已经排好、还没画）读界面那张渲染层 `"UI"` 的命令表（和 src/world.rs 读
//!   `"Game"` 同一个地方），画 `ingame/serpen` 的贴图命令：名字里的 `serpen` 换成一样长的别名（`drk_oc` 之类，
//!   `mod.override_info` 把它们各指到一种元素亚龙 / 远古巨龙），UV 换到那张图上——同一个动作的同一帧，相对帧中心的位置
//!   不变（六种元素亚龙是同一个模板，头都在帧的正中；远古巨龙宽 10 像素，往右挪 5），块的大小不变，所以画出来一样大。
//!   比赛画面上画这一刻的那一条（和身体同一个算法：src/skin.rs 的 `drake_at`，屏幕时钟往后看 1 秒）；还没刷出第一条时
//!   不改。比赛画面以外（百科）六种元素每 2 秒换一种。
//!
//! 名字是命令自己的 String（{容量, 指针, 长度}）时就地改那 6 个字节；容量是 [`BORROWED`] 的是借来的（游戏数据里共用的
//! 那一份），绝不改它，换成进程堆上新分配的一份（游戏用 HeapFree(GetProcessHeap()) 释放命令的名字，System 分配器就是这个
//! 堆），这条命令丢掉时游戏把它释放。认不出来（读不到帧、没有 `"UI"`、UV 落不进炼狱亚龙的任何一帧——比如
//! `mod.override_info` 没生效、UV 还是原版小龙图上的）就不改，日志 `PORTRAIT` 写明。

use std::alloc::{GlobalAlloc, Layout, System};
use std::sync::{LazyLock, Mutex};
use std::time::Instant;

use mod_api_stable::*;

use super::world::{self, Peek, Process, CMD};
use super::{counted, feed, wlog};

/// 界面那张渲染层。
pub const UI: &str = "UI";
/// 原版小龙那张图的名字的最后一段：`asset/base/aseprite_resources/ingame/serpen`（取图时可能带 `#sheet`）。
pub const NATIVE: &str = "serpen";
const NATIVE_PATH: &[u8] = b"/ingame/serpen";
/// (图, 别名, 图的宽高)。别名和 [`NATIVE`] 一样长，`mod.override_info` 把 `ingame/<别名>` 指到这张图；宽高由测试对着
/// effects/ 里的 png 核对。前六个是元素亚龙（百科里轮流），最后一个是远古巨龙。
pub const SHEETS: [(&str, &str, (u32, u32)); 7] = [
    ("league_drake_infernal", "drk_if", (2040, 887)),
    ("league_drake_mountain", "drk_mt", (2006, 877)),
    ("league_drake_ocean", "drk_oc", (2040, 887)),
    ("league_drake_cloud", "drk_cl", (2024, 877)),
    ("league_drake_hextech", "drk_hx", (2006, 877)),
    ("league_drake_chemtech", "drk_ch", (2006, 905)),
    ("league_drake_elder", "drk_el", (1965, 905)),
];
/// `mod.override_info` 把 `ingame/serpen` 指到的那张（[`SHEETS`] 的下标）：炼狱亚龙。
pub const STATIC: usize = 0;
/// 百科里轮流的几种（[`SHEETS`] 的头几张）、每种几毫秒。
const CYCLE: usize = 6;
const CYCLE_MS: u64 = 2000;
/// 名字的容量是这个数：借来的（`Cow::Borrowed`，游戏数据里共用的那一份）。
pub const BORROWED: u64 = 0x8000_0000_0000_0000;
const KIND_SPRITE: u8 = 0x03;
/// 名字也在 +8 的别的种类（矢量图、单位的图……）：画原版小龙的只记日志（看头像是不是走了别的种类）。
const OTHER_NAMED: [u8; 3] = [0x02, 0x04, 0x06];
/// 原版小龙的图名有多长：`asset/base/aseprite_resources/ingame/serpen`，带不带 `#sheet`。只读这两种长度的名字。
const NAME_LENS: [usize; 2] = [43, 49];
/// 一次读多少条命令。
const BLOCK: usize = 64;

// ---- 图上的帧

/// 一张图：宽高（像素）、每个 1x 动作的帧（像素矩形 x, y, 宽, 高），按 .fanim 里的顺序（待机在最前）。高清帧（`hd_`）不要：
/// 界面只画 1x 的。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Geom {
    pub dims: (f32, f32),
    pub tags: Vec<(String, Vec<[f32; 4]>)>,
}

static GEOMS: LazyLock<Vec<Geom>> = LazyLock::new(|| {
    SHEETS
        .iter()
        .map(|(name, _, d)| {
            let fanim = super::hd::EFFECTS.iter().find(|e| e.0 == *name).map_or("", |e| e.2);
            Geom { dims: (d.0 as f32, d.1 as f32), tags: frames_of(fanim) }
        })
        .collect()
});

/// .fanim 里 1x 动作的帧矩形（`anims` -> 动作 -> `frames` -> `data` 的 x / y / w / h），按文件里的顺序。
pub fn frames_of(fanim: &str) -> Vec<(String, Vec<[f32; 4]>)> {
    let b = fanim.trim_start_matches('\u{feff}').as_bytes();
    let mut i = 0;
    let Some(J::Obj(top)) = value(b, &mut i) else { return Vec::new() };
    let Some(J::Obj(anims)) = field(&top, "anims") else { return Vec::new() };
    anims
        .iter()
        .filter(|(tag, _)| !tag.starts_with("hd_"))
        .filter_map(|(tag, a)| {
            let J::Obj(a) = a else { return None };
            let Some(J::Arr(frames)) = field(a, "frames") else { return None };
            let rects = frames
                .iter()
                .filter_map(|f| {
                    let J::Obj(f) = f else { return None };
                    let Some(J::Obj(d)) = field(f, "data") else { return None };
                    let n = |k: &str| match field(d, k) {
                        Some(J::Num(v)) => Some(*v as f32),
                        _ => None,
                    };
                    Some([n("x")?, n("y")?, n("w")?, n("h")?])
                })
                .collect();
            Some((tag.clone(), rects))
        })
        .collect()
}

/// 够读 .fanim 的一小段 JSON。
#[derive(Debug)]
enum J {
    Obj(Vec<(String, J)>),
    Arr(Vec<J>),
    Num(f64),
    Str,
    Lit,
}

fn field<'a>(o: &'a [(String, J)], k: &str) -> Option<&'a J> {
    o.iter().find(|(n, _)| n == k).map(|(_, v)| v)
}

fn skip_ws(b: &[u8], i: &mut usize) {
    while *i < b.len() && b[*i].is_ascii_whitespace() {
        *i += 1;
    }
}

fn string(b: &[u8], i: &mut usize) -> Option<String> {
    if b.get(*i)? != &b'"' {
        return None;
    }
    *i += 1;
    let start = *i;
    while *b.get(*i)? != b'"' {
        if b[*i] == b'\\' {
            *i += 1;
        }
        *i += 1;
    }
    let s = String::from_utf8_lossy(&b[start..*i]).into_owned();
    *i += 1;
    Some(s)
}

fn value(b: &[u8], i: &mut usize) -> Option<J> {
    skip_ws(b, i);
    match *b.get(*i)? {
        b'{' => {
            *i += 1;
            let mut v = Vec::new();
            skip_ws(b, i);
            if b.get(*i)? == &b'}' {
                *i += 1;
                return Some(J::Obj(v));
            }
            loop {
                skip_ws(b, i);
                let k = string(b, i)?;
                skip_ws(b, i);
                if b.get(*i)? != &b':' {
                    return None;
                }
                *i += 1;
                v.push((k, value(b, i)?));
                skip_ws(b, i);
                match b.get(*i)? {
                    b',' => *i += 1,
                    b'}' => {
                        *i += 1;
                        return Some(J::Obj(v));
                    }
                    _ => return None,
                }
            }
        }
        b'[' => {
            *i += 1;
            let mut v = Vec::new();
            skip_ws(b, i);
            if b.get(*i)? == &b']' {
                *i += 1;
                return Some(J::Arr(v));
            }
            loop {
                v.push(value(b, i)?);
                skip_ws(b, i);
                match b.get(*i)? {
                    b',' => *i += 1,
                    b']' => {
                        *i += 1;
                        return Some(J::Arr(v));
                    }
                    _ => return None,
                }
            }
        }
        b'"' => string(b, i).map(|_| J::Str),
        b'-' | b'0'..=b'9' => {
            let start = *i;
            while *i < b.len() && matches!(b[*i], b'-' | b'+' | b'.' | b'e' | b'E' | b'0'..=b'9') {
                *i += 1;
            }
            std::str::from_utf8(&b[start..*i]).ok()?.parse().ok().map(J::Num)
        }
        _ => {
            while *i < b.len() && b[*i].is_ascii_alphabetic() {
                *i += 1;
            }
            Some(J::Lit)
        }
    }
}

// ---- 换算

/// 炼狱亚龙图（`from`）上的一块（UV：x, y, 宽, 高，按比例）换到 `to` 上：先找它落在哪一帧（块的中心在里面的那一帧，按
/// 动作在文件里的顺序找，待机在最前），换成 `to` 同一个动作的同一帧，相对帧中心的位置不变；出了那一帧就推回帧里，比帧
/// 还大的那一边对着帧中心。块的像素大小不变（画出来一样大）。落不进任何一帧：None（多半是 `mod.override_info` 没生效，
/// UV 还是原版小龙图上的）。
pub fn remap(from: &Geom, to: &Geom, uv: [f32; 4]) -> Option<[f32; 4]> {
    let (fw, fh) = from.dims;
    let r = [uv[0] * fw, uv[1] * fh, uv[2] * fw, uv[3] * fh];
    if !r.iter().all(|v| v.is_finite()) || r[2] <= 0.0 || r[3] <= 0.0 {
        return None;
    }
    let (cx, cy) = (r[0] + r[2] / 2.0, r[1] + r[3] / 2.0);
    for (tag, frames) in &from.tags {
        for (k, f) in frames.iter().enumerate() {
            if cx < f[0] || cx > f[0] + f[2] || cy < f[1] || cy > f[1] + f[3] {
                continue;
            }
            let t = to.tags.iter().find(|(n, _)| n == tag)?.1.get(k)?;
            let x = place(r[0] - (f[0] + f[2] / 2.0), r[2], t[0], t[2]);
            let y = place(r[1] - (f[1] + f[3] / 2.0), r[3], t[1], t[3]);
            let (tw, th) = to.dims;
            return Some([x / tw, y / th, r[2] / tw, r[3] / th]);
        }
    }
    None
}

/// 一条边：块的起点离帧中心 `off`、块长 `len`，放进起点 `at`、长 `size` 的帧：同样离中心，出界推回帧里，比帧长就对中。
fn place(off: f32, len: f32, at: f32, size: f32) -> f32 {
    if len >= size {
        at + (size - len) / 2.0
    } else {
        (at + size / 2.0 + off).clamp(at, at + size - len)
    }
}

/// 现在该画哪一张（[`SHEETS`] 的下标）：比赛画面上是这一刻的那一条（`drake`：src/skin.rs 的 `drake_at`；还没有就 None，
/// 不改，画静态的炼狱亚龙），别处六种元素按时间轮流。
pub fn which(on_match: bool, drake: Option<&str>, now_ms: u64) -> Option<usize> {
    if on_match {
        let d = drake?;
        SHEETS.iter().position(|s| s.0 == d)
    } else {
        Some((now_ms / CYCLE_MS) as usize % CYCLE)
    }
}

/// 名字里 `ingame/serpen` 的 `serpen` 从第几个字节起（它后面是结尾或 `#`）；不是原版小龙那张图：None。
pub fn native_at(name: &[u8]) -> Option<usize> {
    let at = name.windows(NATIVE_PATH.len()).position(|w| w == NATIVE_PATH)?;
    let end = at + NATIVE_PATH.len();
    (end == name.len() || name[end] == b'#').then_some(end - NATIVE.len())
}

// ---- 找、改

/// 一条要改的命令。
#[derive(Clone, Debug, PartialEq)]
pub struct Change {
    /// 命令的地址。
    pub cmd: usize,
    /// 名字：{容量, 指针, 长度}、原样、`serpen` 从第几个字节起。
    pub cap: u64,
    pub ptr: usize,
    pub name: Vec<u8>,
    pub pos: usize,
    pub uv: [f32; 4],
    pub uv_new: [f32; 4],
}

/// 找到的：要改的、落不进炼狱亚龙的帧没改的、别的种类画原版小龙的（只记日志）。
#[derive(Debug, Default)]
pub struct Found {
    pub changes: Vec<Change>,
    pub left: Vec<String>,
    pub other_kinds: Vec<String>,
}

/// 读一遍界面命令表（`list` 起 `n` 条）：画原版小龙图的贴图命令换成第 `k` 张要怎么改（只读，不写）。
pub fn find(p: &dyn Peek, list: usize, n: usize, k: usize) -> Found {
    let mut out = Found::default();
    let (from, to) = (&GEOMS[STATIC], &GEOMS[k]);
    let at = world::AT_SPRITE_NAME;
    let mut i = 0;
    while i < n {
        let take = BLOCK.min(n - i);
        let Some(block) = world::bytes(p, list + i * CMD, take * CMD) else { break };
        for j in 0..take {
            let c = &block[j * CMD..(j + 1) * CMD];
            let kd = world::kind(world::u64_in(c, 0));
            let sprite = kd == KIND_SPRITE;
            if !sprite && !OTHER_NAMED.contains(&kd) {
                continue;
            }
            let (cap, ptr, len) = (world::u64_in(c, at), world::u64_in(c, at + 8) as usize, world::u64_in(c, at + 16) as usize);
            if !NAME_LENS.contains(&len) {
                continue;
            }
            let Some(name) = world::bytes(p, ptr, len) else { continue };
            let Some(pos) = native_at(&name) else { continue };
            let text = String::from_utf8_lossy(&name).into_owned();
            if !sprite {
                out.other_kinds.push(format!("kind {kd:#x} #{} {text:?}", i + j));
                continue;
            }
            let uv = std::array::from_fn(|q| world::f32_in(c, world::AT_SPRITE_UV + 4 * q));
            match remap(from, to, uv) {
                Some(uv_new) => out.changes.push(Change { cmd: list + (i + j) * CMD, cap, ptr, name, pos, uv, uv_new }),
                None => out.left.push(format!("#{} {text:?} uv {uv:?}: not on a frame of the static Infernal Drake", i + j)),
            }
        }
        i += take;
    }
    out
}

/// 把命令的名字（+8 的 String）里的 `serpen` 换成 `alias`（一样长）：命令自己的就地改那几个字节；借来的（容量是
/// [`BORROWED`]）换成新分配的一份。别的样子：None，不动。
///
/// # Safety
/// `cmd` 是这一帧界面命令表里的一条命令，`ptr` / `cap` / `name` 是刚从它读出来的名字。
pub unsafe fn rename(cmd: usize, cap: u64, ptr: usize, name: &[u8], pos: usize, alias: &[u8]) -> Option<&'static str> {
    if alias.len() != NATIVE.len() || pos + alias.len() > name.len() {
        return None;
    }
    if cap & BORROWED == 0 && cap as usize >= name.len() {
        std::ptr::copy_nonoverlapping(alias.as_ptr(), (ptr + pos) as *mut u8, alias.len());
        return Some("in place");
    }
    if cap != BORROWED {
        return None;
    }
    let layout = Layout::from_size_align(name.len(), 1).ok()?;
    let new = System.alloc(layout);
    if new.is_null() {
        return None;
    }
    std::ptr::copy_nonoverlapping(name.as_ptr(), new, name.len());
    std::ptr::copy_nonoverlapping(alias.as_ptr(), new.add(pos), alias.len());
    let field = (cmd + world::AT_SPRITE_NAME) as *mut u64;
    field.write_unaligned(name.len() as u64);
    field.add(1).write_unaligned(new as u64);
    Some("a copy of its own")
}

/// 改一条：名字，然后 UV。
///
/// # Safety
/// 同 [`rename`]。
unsafe fn apply(ch: &Change, alias: &[u8]) -> Option<&'static str> {
    let how = rename(ch.cmd, ch.cap, ch.ptr, &ch.name, ch.pos, alias)?;
    let uv = (ch.cmd + world::AT_SPRITE_UV) as *mut f32;
    for (q, v) in ch.uv_new.iter().enumerate() {
        uv.add(q).write_unaligned(*v);
    }
    Some(how)
}

// ---- 每帧

struct Seen {
    /// 上次说过的话（认不出来的原因）：变了才记日志。
    told: String,
    /// 上一帧画的是哪一张、在不在比赛画面、哪一场：变了时把头几条改动写进日志。
    last: Option<(usize, bool, Option<(u64, u64)>)>,
    /// 这个情形下还要写几条改动。
    lines: usize,
}

static SEEN: Mutex<Seen> = Mutex::new(Seen { told: String::new(), last: None, lines: 0 });
static START: LazyLock<Instant> = LazyLock::new(Instant::now);
/// 情形一变写几条改动。
const LINES: usize = 4;

fn tell(seen: &mut Seen, line: String) {
    if seen.told != line {
        seen.told.clone_from(&line);
        if let Some(k) = counted("portrait") {
            wlog(format!("{line} #{k}"));
        }
    }
}

/// 每帧（客户端扩展的 post_render，画本包的东西之前）：界面上画原版小龙图的命令换成该画的那一张。
pub fn fix(ctx: &StableClient<'_>, on_match: bool) {
    let current = feed::current();
    let drake = if on_match {
        current.zip(game_places::clock::screen_tick()).and_then(|((m, s), t)| {
            super::skin::drake_at(&feed::events(m, s), t + super::skin::SPAWN_LEAD)
        })
    } else {
        None
    };
    let Some(k) = which(on_match, drake.as_deref(), START.elapsed().as_millis() as u64) else { return };
    // 静态的就是这一张：游戏自己画的就对
    if k == STATIC {
        return;
    }
    let Ok(mut seen) = SEEN.lock() else { return };
    let p = Process;
    let found = world::host_state(ctx)
        .ok_or_else(|| "the host's state is not where it was".to_string())
        .and_then(|state| {
            world::bytes(&p, state + world::STATE_FRAME, 8)
                .map(|b| world::u64_in(&b, 0) as usize)
                .filter(|f| world::plausible(*f))
                .ok_or_else(|| "no frame in the host's state".to_string())
        })
        .and_then(|frame| world::map_list(&p, frame, UI));
    let (list, n) = match found {
        Ok(v) => v,
        Err(why) => {
            tell(&mut seen, format!("PORTRAIT off: {why} - the drake's pictures in the UI stay the static Infernal Drake"));
            return;
        }
    };
    tell(&mut seen, format!("PORTRAIT on: the UI's \"{UI}\" commands are read"));
    let f = find(&p, list, n, k);
    let key = (k, on_match, current.filter(|_| on_match));
    if seen.last != Some(key) {
        seen.last = Some(key);
        seen.lines = LINES;
    }
    let alias = SHEETS[k].1.as_bytes();
    for ch in &f.changes {
        let how = unsafe { apply(ch, alias) };
        if seen.lines > 0 {
            seen.lines -= 1;
            if let Some(c) = counted("portrait_change") {
                wlog(format!("PORTRAIT {} ({}): {:?} -> {} ({how:?}), uv {:?} -> {:?} #{c}",
                             SHEETS[k].0, if on_match { "the match screen" } else { "off the match: the six in turn" },
                             String::from_utf8_lossy(&ch.name), SHEETS[k].1, ch.uv, ch.uv_new));
            }
        }
    }
    for line in f.left.iter().chain(f.other_kinds.iter()) {
        if let Some(c) = counted("portrait_left") {
            wlog(format!("PORTRAIT left as it is: {line} #{c}"));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::world::tests::{frame, put32f, sprite_cmd, FRAME};

    fn png_dims(path: &std::path::Path) -> (u32, u32) {
        let b = std::fs::read(path).unwrap();
        assert_eq!(&b[12..16], b"IHDR", "{}", path.display());
        (u32::from_be_bytes(b[16..20].try_into().unwrap()), u32::from_be_bytes(b[20..24].try_into().unwrap()))
    }

    fn effects() -> std::path::PathBuf {
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("effects")
    }

    #[test]
    fn the_aliases_are_as_long_as_serpen_and_the_sizes_are_the_pngs() {
        for (sheet, alias, dims) in SHEETS {
            assert_eq!(alias.len(), NATIVE.len(), "{alias}: the name is changed in place, byte for byte");
            assert!(alias.bytes().all(|c| c.is_ascii_lowercase() || c == b'_'), "{alias}");
            assert_eq!(png_dims(&effects().join(format!("{sheet}#sheet.png"))), dims, "{sheet}");
        }
        let names: Vec<_> = SHEETS.iter().map(|s| s.1).collect();
        let mut once = names.clone();
        once.dedup();
        assert_eq!(names, once);
    }

    #[test]
    fn the_override_points_serpen_and_every_alias_at_the_drakes() {
        let text = std::fs::read_to_string(std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("mod.override_info")).unwrap();
        let entry = |key: &str| -> Option<String> {
            let at = text.find(&format!("\"{key}\""))?;
            let rest = &text[at..];
            let r = rest.find("\"remapping\"")?;
            let v = &rest[r + 11..];
            let q0 = v.find('"')? + 1;
            let q1 = v[q0..].find('"')? + q0;
            Some(v[q0..q1].to_string())
        };
        let base = "asset/base/aseprite_resources/ingame";
        for part in ["sheet", "anim"] {
            assert_eq!(entry(&format!("{base}/serpen#{part}")).as_deref(),
                       Some(format!("asset/league_dragons/effects/{}#{part}", SHEETS[STATIC].0).as_str()));
            for (sheet, alias, _) in SHEETS {
                assert_eq!(entry(&format!("{base}/{alias}#{part}")).as_deref(),
                           Some(format!("asset/league_dragons/effects/{sheet}#{part}").as_str()), "{alias}#{part}");
            }
        }
    }

    #[test]
    fn the_frames_are_read_from_the_fanims() {
        assert_eq!(GEOMS.len(), SHEETS.len());
        for g in GEOMS.iter() {
            let tags: Vec<&str> = g.tags.iter().map(|(t, _)| t.as_str()).collect();
            assert_eq!(tags, ["idle", "base", "attack", "dead"], "only the 1x ones, in the file's order");
            assert_eq!(g.tags[0].1.len(), 8);
            assert_eq!(g.tags[0].1[0][..2], [0.0, 0.0]);
        }
        assert_eq!(GEOMS[STATIC].tags[0].1[0], [0.0, 0.0, 80.0, 75.0]);
        assert_eq!(GEOMS[6].tags[0].1[0], [0.0, 0.0, 90.0, 75.0], "the Elder is 10 px wider");
        assert!(frames_of("not json").is_empty());
    }

    fn px(g: &Geom, uv: [f32; 4]) -> [f32; 4] {
        [uv[0] * g.dims.0, uv[1] * g.dims.1, uv[2] * g.dims.0, uv[3] * g.dims.1]
    }

    fn close(a: [f32; 4], b: [f32; 4]) -> bool {
        a.iter().zip(b).all(|(x, y)| (x - y).abs() < 0.01)
    }

    #[test]
    fn a_whole_idle_frame_becomes_the_same_frame_of_another_drake() {
        let (from, ocean, elder) = (&GEOMS[STATIC], &GEOMS[2], &GEOMS[6]);
        let uv = [0.0, 0.0, 80.0 / from.dims.0, 75.0 / from.dims.1];
        // the same place on another sheet: its own width and height
        assert!(close(px(ocean, remap(from, ocean, uv).unwrap()), [0.0, 0.0, 80.0, 75.0]));
        // the Elder is 90 wide: the 80 in its middle, the picture as big as before
        assert!(close(px(elder, remap(from, elder, uv).unwrap()), [5.0, 0.0, 80.0, 75.0]));
    }

    #[test]
    fn a_face_crop_keeps_its_place_against_the_frame_centre() {
        let (from, ocean, elder) = (&GEOMS[STATIC], &GEOMS[2], &GEOMS[6]);
        // 18 x 18 round the head in the second idle frame (81, 0)
        let f = from.tags[0].1[2];
        let uv = [(f[0] + 31.0) / from.dims.0, (f[1] + 20.0) / from.dims.1, 18.0 / from.dims.0, 18.0 / from.dims.1];
        let o = ocean.tags[0].1[2];
        assert!(close(px(ocean, remap(from, ocean, uv).unwrap()), [o[0] + 31.0, o[1] + 20.0, 18.0, 18.0]));
        let e = elder.tags[0].1[2];
        assert!(close(px(elder, remap(from, elder, uv).unwrap()), [e[0] + 36.0, e[1] + 20.0, 18.0, 18.0]));
    }

    #[test]
    fn a_block_out_of_the_frame_is_pushed_back_and_one_off_every_frame_is_left() {
        let (from, ocean) = (&GEOMS[STATIC], &GEOMS[2]);
        // wider than the frame: centred on it
        let uv = [-10.0 / from.dims.0, 0.0, 100.0 / from.dims.0, 75.0 / from.dims.1];
        assert!(close(px(ocean, remap(from, ocean, uv).unwrap()), [-10.0, 0.0, 100.0, 75.0]));
        // somewhere no frame is (the native drake's UV on a sheet that is not ours): None
        let far = [0.99, 0.99, 0.005, 0.005];
        assert_eq!(remap(from, ocean, far), None);
        assert_eq!(remap(from, ocean, [0.0, 0.0, 0.0, 0.1]), None);
        assert_eq!(remap(from, ocean, [f32::NAN, 0.0, 0.1, 0.1]), None);
    }

    #[test]
    fn which_drake_on_the_match_screen_and_the_six_in_turn_elsewhere() {
        assert_eq!(which(true, Some("league_drake_ocean"), 0), Some(2));
        assert_eq!(which(true, Some("league_drake_elder"), 0), Some(6));
        assert_eq!(which(true, None, 0), None, "no drake yet: the static one");
        assert_eq!(which(true, Some("league_baron"), 0), None);
        let seen: Vec<_> = (0..7).map(|i| which(false, None, i * CYCLE_MS + 5).unwrap()).collect();
        assert_eq!(seen, [0, 1, 2, 3, 4, 5, 0], "never the Elder in the encyclopedia");
    }

    #[test]
    fn only_the_native_drakes_picture_is_taken_for_it() {
        assert_eq!(native_at(b"asset/base/aseprite_resources/ingame/serpen"), Some(37));
        assert_eq!(native_at(b"asset/base/aseprite_resources/ingame/serpen#sheet"), Some(37));
        assert_eq!(b"asset/base/aseprite_resources/ingame/serpen".len(), NAME_LENS[0]);
        assert_eq!(b"asset/base/aseprite_resources/ingame/serpen#sheet".len(), NAME_LENS[1]);
        assert_eq!(native_at(b"asset/base/aseprite_resources/ingame/serpen_monster"), None);
        assert_eq!(native_at(b"asset/base/aseprite_resources/ingame/serpent"), None);
        assert_eq!(native_at(b"asset/base/ui/icons/serpen"), None, "the header's team-coloured icon is not a picture of it");
        assert_eq!(native_at(b"asset/base/aseprite_resources/ingame/drk_oc"), None, "once changed it is left alone");
    }

    /// A fake frame whose "UI" map holds `cmds`, plus the names they point at.
    fn ui(cmds: Vec<Vec<u8>>, names: &[(usize, &[u8])]) -> crate::world::tests::Fake {
        let mut fake = frame(&[("Game", vec![]), (UI, cmds)]);
        for (at, n) in names {
            fake.regions.push((*at, n.to_vec()));
        }
        fake
    }

    fn uv_cmd(name_at: usize, len: usize, uv: [f32; 4]) -> Vec<u8> {
        let mut c = sprite_cmd(name_at, len, 10.0, 20.0, 5);
        for (q, v) in uv.into_iter().enumerate() {
            put32f(&mut c, world::AT_SPRITE_UV + 4 * q, v);
        }
        c
    }

    #[test]
    fn the_ui_map_is_found_and_only_the_native_drakes_sprites_are_changed() {
        const N1: usize = 0x80_0000;
        const N2: usize = 0x80_1000;
        const N3: usize = 0x80_2000;
        let native: &[u8] = b"asset/base/aseprite_resources/ingame/serpen#sheet";
        let other: &[u8] = b"asset/base/aseprite_resources/ingame/morgard#sheet";
        let g = &GEOMS[STATIC];
        let whole = [0.0, 0.0, 80.0 / g.dims.0, 75.0 / g.dims.1];
        let fake = ui(
            vec![uv_cmd(N1, native.len(), whole), uv_cmd(N2, other.len(), whole), uv_cmd(N3, native.len(), [0.99, 0.99, 0.005, 0.005])],
            &[(N1, native), (N2, other), (N3, native)],
        );
        let (list, n) = world::map_list(&fake, FRAME, UI).unwrap();
        assert_eq!(n, 3);
        let f = find(&fake, list, n, 2);
        assert_eq!(f.changes.len(), 1, "{f:?}");
        let ch = &f.changes[0];
        assert_eq!((ch.cmd, ch.ptr, ch.pos, ch.name.as_slice()), (list, N1, 37, native));
        assert!(close(px(&GEOMS[2], ch.uv_new), [0.0, 0.0, 80.0, 75.0]));
        assert_eq!(f.left.len(), 1, "the one off every frame is told, not changed");
        assert!(f.other_kinds.is_empty());
    }

    #[test]
    fn an_owned_name_is_changed_in_place_and_a_borrowed_one_gets_a_copy() {
        let native = b"asset/base/aseprite_resources/ingame/serpen#sheet".to_vec();
        // owned: the command's own bytes
        let mut own = native.clone();
        let mut cmd = vec![0u8; CMD];
        let how = unsafe {
            rename(cmd.as_mut_ptr() as usize, own.len() as u64, own.as_mut_ptr() as usize, &native, 37, b"drk_oc")
        };
        assert_eq!(how, Some("in place"));
        assert_eq!(own, b"asset/base/aseprite_resources/ingame/drk_oc#sheet");
        assert_eq!(cmd, vec![0u8; CMD], "the command itself untouched");
        // borrowed: never written; the command gets a copy of its own
        let shared = native.clone();
        let mut cmd = vec![0u8; CMD];
        let how = unsafe { rename(cmd.as_mut_ptr() as usize, BORROWED, shared.as_ptr() as usize, &native, 37, b"drk_el") };
        assert_eq!(how, Some("a copy of its own"));
        assert_eq!(shared, native);
        let (cap, ptr) = (world::u64_in(&cmd, world::AT_SPRITE_NAME), world::u64_in(&cmd, world::AT_SPRITE_NAME + 8) as usize);
        assert_eq!(cap as usize, native.len());
        let copy = unsafe { std::slice::from_raw_parts(ptr as *const u8, native.len()) }.to_vec();
        assert_eq!(copy, b"asset/base/aseprite_resources/ingame/drk_el#sheet");
        unsafe { System.dealloc(ptr as *mut u8, Layout::from_size_align(native.len(), 1).unwrap()) };
        // anything else: left alone
        let mut cmd = vec![0u8; CMD];
        let how = unsafe { rename(cmd.as_mut_ptr() as usize, BORROWED | 5, shared.as_ptr() as usize, &native, 37, b"drk_el") };
        assert_eq!(how, None);
        let how = unsafe { rename(cmd.as_mut_ptr() as usize, 10, shared.as_ptr() as usize, &native, 37, b"drk_el") };
        assert_eq!(how, None, "a capacity shorter than the name is not a String of its own");
        assert_eq!(cmd, vec![0u8; CMD]);
    }
}
