//! 游戏的剩余复活 tick（照 league_akshan 的动态寻址，两边一起改）：稳定接口里没有改复活时间的函数（`player_respawn_time`
//! 只读）。游戏每个阵亡玩家身上有一个「剩余复活 tick」，每 tick 减 1，减到 0 时游戏自己在泉水重新生成英雄。运行时读游戏的
//! `player_respawn_time` / `player_is_alive` 两个函数的机器码，找出「取玩家」的虚表槽、存活标记和剩余 tick 的偏移
//! （[`decode`]，**动态寻址**：游戏更新后偏移变了也能找到），交叉核对两个函数一致；写之前还要求「阵亡、读到的值等于游戏
//! 接口读到的值、≥ 1」，只往小改、绝不写 0（0 减 1 会变成永远不复活）。任何一步对不上就不写，只记日志：最坏只是不生效。
//! 只读的模拟（游戏给画面、回放的那几份）不写。

use std::sync::Mutex;

use mod_api_stable::*;

use super::wlog;

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
            "LAYOUT NOT FOUND in respawn_time 0x{rt:x} / is_alive 0x{al:x}: the game changed, the respawn is not cut (nothing is written)"
        )),
    }
    *cache = Some((rt, al, l));
    l
}

type GetPlayer = unsafe extern "C" fn(*mut std::ffi::c_void, usize) -> *mut u8;

/// 把一个阵亡玩家的剩余复活 tick 改小到 `ticks`（至少 1）。所有核对都过了才写，写完用游戏接口读回核对。
pub fn shorten_respawn(sim: &StableSim<'_>, player: usize, ticks: u64) -> Result<(u64, u64), &'static str> {
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


#[cfg(test)]
mod tests {
    use super::*;

    fn hex(s: &str) -> Vec<u8> {
        let mut v: Vec<u8> = (0..s.len()).step_by(2).map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap()).collect();
        v.resize(SCAN_LEN, 0xcc);
        v
    }

    // league_akshan's: TeamfightManager2.exe 0.6.4 (87,228,416 bytes, 2026-10-14) and 0.6.5 (87,009,792 bytes, 2026-10-21)
    const RESPAWN_TIME: &str = "554883ec30488d6c243048c745f8feffffff4885d2742348ffca488b014c8b41084889c141ff9058010000904885c0740980b89808000000740831c04883c4305dc3488b80a00800004883c4305dc3";
    const IS_ALIVE: &str = "554883ec30488d6c243048c745f8feffffff4885d2742748ffca488b014c8b41084889c141ff9058010000904885c0740d0fb680980800004883c4305dc3";
    const RESPAWN_TIME_065: &str = "554883ec30488d6c243048c745f8feffffff4885d2742348ffca488b014c8b41084889c141ff9058010000904885c0740980b8b808000000740831c04883c4305dc3488b80c00800004883c4305dc3";
    const IS_ALIVE_065: &str = "554883ec30488d6c243048c745f8feffffff4885d2742748ffca488b014c8b41084889c141ff9058010000904885c0740d0fb680b80800004883c4305dc3";
    // 0.7.1 (94,043,136 bytes, 2026-11-04): 0.6.5's code and fields
    const RESPAWN_TIME_071: &str = "554883ec30488d6c243048c745f8feffffff4885d2742348ffca488b014c8b41084889c141ff9058010000904885c0740980b8b808000000740831c04883c4305dc3488b80c00800004883c4305dc3";
    const IS_ALIVE_071: &str = "554883ec30488d6c243048c745f8feffffff4885d2742748ffca488b014c8b41084889c141ff9058010000904885c0740d0fb680b80800004883c4305dc331c04883c4305dc3";

    #[test]
    fn decodes_the_games_getters() {
        assert_eq!(decode(&hex(RESPAWN_TIME), &hex(IS_ALIVE)), Some(LifeLayout { getp: 0x158, tag: 0x898, val: 0x8a0 }));
        assert_eq!(decode(&hex(RESPAWN_TIME_065), &hex(IS_ALIVE_065)),
                   Some(LifeLayout { getp: 0x158, tag: 0x8b8, val: 0x8c0 }));
        assert_eq!(decode(&hex(RESPAWN_TIME_071), &hex(IS_ALIVE_071)),
                   Some(LifeLayout { getp: 0x158, tag: 0x8b8, val: 0x8c0 }));
        // one build's getter with the other's: refused, nothing written
        assert!(decode(&hex(RESPAWN_TIME_065), &hex(IS_ALIVE)).is_none());
    }

    #[test]
    fn refuses_mismatched_code() {
        let other = IS_ALIVE.replace("0fb6809808", "0fb680a008");
        assert!(decode(&hex(RESPAWN_TIME), &hex(&other)).is_none());
        let slot = IS_ALIVE.replace("41ff9058010000", "41ff9060010000");
        assert!(decode(&hex(RESPAWN_TIME), &hex(&slot)).is_none());
        assert!(decode(&hex("c3"), &hex("c3")).is_none());
    }
}
