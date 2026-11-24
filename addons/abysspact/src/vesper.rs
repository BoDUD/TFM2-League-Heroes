//! 烛灵 (`abysspact_vesper`) · 灵媒少女 · 辅助
//!
//! 招牌机制「烛冠」0–5 支蜡烛奶盾增幅 + R「回魂」唤回阵亡队友化魂再战 8 秒拿人头真复活:
//! - 被动「烛冠」：身边 5 万内每阵亡一名英雄（敌我都算）点亮 1 支头顶蜡烛（上限 5 支），
//!   头顶同步播放 4 帧跳动烛火 `candle_1..5`，每支令法强/治疗护盾增幅 +10%（上限 +50%）。
//! - 大招「回魂」：若最近 10 秒（600 ticks）内有友方英雄阵亡，复用阿克尚已验证的安全 `shorten_respawn` 将其原地唤回，
//!   以魂体形态再战 8 秒（480 ticks）：伤害不打折、减伤 50%、禁止治疗，周身罩淡紫白半透明光 `spirit`；
//!   8 秒内己方拿到任意击杀则当场**真复活**（回复至至少 30% 最大生命 + 暖金 `rebirth` 光圈）；
//!   若 8 秒内未拿人头则魂体散去。若近期无阵亡队友，则给身边 5 万内所有友军赋予 `100 + 60% AP`（享烛冠加成）护盾！

use std::collections::HashMap;
use std::sync::Mutex;
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_vesper";
pub const NATIVE_MARK: &str = "abysspact_vesper_native";
pub const CROWN_BUFF: &str = "abysspact_vesper_crown";
pub const SPIRIT_BUFF: &str = "abysspact_vesper_spirit";
pub const R_ASK: &str = "abysspact_vesper_r_ask";
pub const R_CAST_VOICE: &str = "abysspact_vesper_r_voice";

pub const CANDLE_CAP: usize = 5;
pub const CANDLE_RADIUS: u64 = 50_000;  // 5.0万
pub const FALLEN_WINDOW: usize = 600;   // 10.0s recent death window
pub const SPIRIT_TICKS: usize = 480;    // 8.0s spirit fight duration
pub const TRUE_REVIVE_HP_PCT: usize = 30;
pub const FALLBACK_SHIELD_RANGE: u64 = 50_000;

pub fn candle_buff_name(k: usize) -> Option<&'static str> {
    match k {
        1 => Some("abysspact_vesper_candle_1"),
        2 => Some("abysspact_vesper_candle_2"),
        3 => Some("abysspact_vesper_candle_3"),
        4 => Some("abysspact_vesper_candle_4"),
        5 => Some("abysspact_vesper_candle_5"),
        _ => None,
    }
}

pub fn fallback_shield_amount(ap: usize, candles: usize) -> usize {
    let base = 100 + ap.saturating_mul(60) / 100;
    base.saturating_mul(100 + candles.min(CANDLE_CAP) * 10) / 100
}

// ---------------------------------------------------------------------------
// Safe memory-verified respawn shortener (shared design with league_akshan)
// ---------------------------------------------------------------------------
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct LifeLayout {
    getp: usize,
    tag: usize,
    val: usize,
}

#[derive(Default)]
struct Scan {
    getp: Option<usize>,
    tag_cmp: Option<usize>,
    val: Option<usize>,
    tag_movzx: Option<usize>,
    dec_rdx: bool,
    load_data: bool,
    load_vt: bool,
}

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

fn decode(respawn_time: &[u8], is_alive: &[u8]) -> Option<LifeLayout> {
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

static LAYOUT: Mutex<Option<(usize, usize, Option<LifeLayout>)>> = Mutex::new(None);
const _: () = assert!(std::mem::size_of::<StableSim<'static>>() == std::mem::size_of::<*mut SimCtxV1>());

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
        decode(std::slice::from_raw_parts(frt, 0x60), std::slice::from_raw_parts(fal, 0x60))
    };
    *cache = Some((rt, al, l));
    l
}

type GetPlayer = unsafe extern "C" fn(*mut std::ffi::c_void, usize) -> *mut u8;

fn shorten_respawn(sim: &StableSim<'_>, player: usize, ticks: u64) -> Result<(u64, u64), &'static str> {
    let l = layout(sim).ok_or("no layout")?;
    let p = sim.get_player(player).ok_or("no player")?;
    if p.is_alive() {
        return Err("alive");
    }
    let api = p.respawn_time() as u64;
    let ctx = raw_ctx(sim);
    unsafe {
        let st = (*ctx).state as *const usize;
        if st.is_null() || *(st as *const u8).add(0x18) != 0 {
            return Err("read-only");
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
            return Err("null player");
        }
        let tag = std::ptr::read_unaligned(pp.add(l.tag) as *const u64);
        let cur = std::ptr::read_unaligned(pp.add(l.val) as *const u64);
        if tag != 0 || cur != api || cur == 0 {
            return Err("mismatch");
        }
        let new = cur.min(ticks.max(1));
        if new < cur {
            std::ptr::write_unaligned(pp.add(l.val) as *mut u64, new);
        }
        if p.respawn_time() as u64 != new {
            return Err("verify failed");
        }
        Ok((cur, new))
    }
}

// ---------------------------------------------------------------------------
// Vesper passive state
// ---------------------------------------------------------------------------
#[derive(Clone, Copy)]
struct SpiritState {
    player_id: usize,
    death_pos: (u64, u64),
    placed: bool,
    end_tick: usize,
    kills_at_start: usize,
}

#[derive(Clone, Default)]
struct VesperPassive {
    voice: Voice,
    candles: usize,
    /// player_id -> (was_alive, last_pos, is_ally)
    seen_players: HashMap<usize, (bool, (u64, u64), bool)>,
    /// Recently fallen allied champions: player_id -> (death_pos, death_tick).
    fallen_allies: HashMap<usize, ((u64, u64), usize)>,
    spirit: Option<SpiritState>,
}

impl VesperPassive {
    fn sync_candles(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        for k in 1..=CANDLE_CAP {
            if let Some(n) = candle_buff_name(k) {
                sim.entity_remove_buff(entity, n);
            }
        }
        sim.entity_remove_buff(entity, CROWN_BUFF);
        if self.candles > 0 {
            if let Some(n) = candle_buff_name(self.candles) {
                sim.add_buff(entity, &BuffV1::named(n));
            }
            let mut b = BuffV1::named(CROWN_BUFF);
            b.magic_power_mult = (self.candles * 10) as i32;
            sim.add_buff(entity, &b);
        }
    }

    fn count_team_kills(sim: &StableSim<'_>, my_team: usize) -> usize {
        let mut c = 0;
        for i in 0..sim.kill_log_count() {
            if let Some(k) = sim.kill_log_at(i) {
                if k.killer_team == my_team {
                    c += 1;
                }
            }
        }
        c
    }

    fn fallback_aoe_shield(&self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, my_pos: (u64, u64), ap: usize) {
        let amt = fallback_shield_amount(ap, self.candles);
        let r2 = FALLBACK_SHIELD_RANGE * FALLBACK_SHIELD_RANGE;
        let mut allies = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_alive() && e.is_champion() && e.team() == my_team && dist_sq(my_pos, e.pos()) <= r2 {
                allies.push(e.id());
            }
        }
        for aid in allies {
            sim.entity_add_shield(aid, amt, 240);
            sim.play_view_effect("abysspact_vesper_shield", entity, &InputTargetV1::target(aid), 0, 0, 0);
        }
        sim.play_sfx("abysspact_vesper_warm_shield", entity, &InputTargetV1::target(entity));
    }
}

impl StablePassive for VesperPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.voice.on_spawn(sim, HERO, entity);
        if self.candles > 0 {
            self.sync_candles(sim, entity);
        }
    }

    fn on_attack(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        target: usize,
        _damage: &mut usize,
    ) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, my_player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, ap)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.stat().magic_power))
        else {
            return;
        };
        let tick = sim.tick();

        // 1. Observe all players' life transitions: light candles (5万) & record fallen allies (10s)
        let candle_r2 = CANDLE_RADIUS * CANDLE_RADIUS;
        let mut lit_new = false;
        let pcount = sim.player_count();
        for i in 0..pcount {
            let Some(p) = sim.player_at(i) else { continue };
            let pid = p.id();
            let p_alive = p.is_alive();
            let p_team = p.team();
            let is_ally = p_team == my_team && pid != my_player;
            let cur_pos = p.champion().map(|c| c.pos());
            let prev = self.seen_players.get(&pid).copied();
            if let Some((was_alive, last_pos, _)) = prev {
                if was_alive && !p_alive {
                    // Champion just died!
                    if alive && self.candles < CANDLE_CAP && dist_sq(my_pos, last_pos) <= candle_r2 {
                        self.candles += 1;
                        lit_new = true;
                    }
                    if is_ally {
                        self.fallen_allies.insert(pid, (last_pos, tick));
                    }
                }
            }
            let store_pos = cur_pos.or_else(|| prev.map(|x| x.1)).unwrap_or(my_pos);
            self.seen_players.insert(pid, (p_alive, store_pos, is_ally));
        }
        self.fallen_allies.retain(|&pid, &mut (_, dt)| {
            tick.saturating_sub(dt) <= FALLEN_WINDOW && sim.get_player(pid).is_some_and(|p| !p.is_alive())
        });
        if lit_new && alive {
            self.sync_candles(sim, entity);
        }

        // 2. Maintain active R「回魂」8-second Spirit Form -> kill-triggered True Revive!
        if let Some(mut sp) = self.spirit {
            if !sp.placed {
                if let Some(ally_eid) = sim.get_player(sp.player_id).filter(|p| p.is_alive()).and_then(|p| p.champion()).map(|e| e.id()) {
                    sim.entity_set_pos(ally_eid, sp.death_pos.0, sp.death_pos.1);
                    let mut sb = BuffV1::timed(SPIRIT_BUFF, SPIRIT_TICKS);
                    sb.damaged_reduce = 50;
                    sb.heal_reduce = 100;
                    sim.add_buff(ally_eid, &sb);
                    sim.play_view_effect("abysspact_vesper_pillar", entity, &InputTargetV1::target(ally_eid), 0, 0, 0);
                    sim.play_sfx("abysspact_vesper_soul_form", entity, &InputTargetV1::target(ally_eid));
                    sp.placed = true;
                    self.spirit = Some(sp);
                } else if tick >= sp.end_tick {
                    self.spirit = None;
                }
            } else {
                let ally_info = sim
                    .get_player(sp.player_id)
                    .filter(|p| p.is_alive())
                    .and_then(|p| p.champion())
                    .map(|e| (e.id(), e.hp().0, e.hp().1));
                match ally_info {
                    None => self.spirit = None,
                    Some((ally_eid, cur, max_hp)) => {
                        let kills_now = Self::count_team_kills(sim, my_team);
                        if kills_now > sp.kills_at_start {
                            // TRUE REVIVE! Keep ally alive at >= 30% max HP + golden rebirth ring!
                            sim.entity_remove_buff(ally_eid, SPIRIT_BUFF);
                            let target_hp = cur.max(max_hp.saturating_mul(TRUE_REVIVE_HP_PCT) / 100).max(1);
                            sim.entity_set_hp(ally_eid, target_hp);
                            sim.play_view_effect("abysspact_vesper_rebirth", entity, &InputTargetV1::target(ally_eid), 0, 0, 0);
                            sim.play_sfx("abysspact_vesper_rebirth_ring", entity, &InputTargetV1::target(ally_eid));
                            self.spirit = None;
                        } else if tick >= sp.end_tick {
                            // 8s expired with no kill -> spirit fades away
                            sim.entity_remove_buff(ally_eid, SPIRIT_BUFF);
                            sim.entity_set_hp(ally_eid, 0);
                            sim.play_sfx("abysspact_vesper_candle_out", entity, &InputTargetV1::target(ally_eid));
                            self.spirit = None;
                        }
                    }
                }
            }
        }

        if !alive {
            return;
        }
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 3. Handle R「回魂」cast: revive most recent fallen ally into Spirit Form, else AoE shield!
        if consume_buff(sim, entity, R_ASK) {
            let recent = self
                .fallen_allies
                .iter()
                .max_by_key(|&(_, &(_, dt))| dt)
                .map(|(&pid, &(pos, _))| (pid, pos));
            let mut revived = false;
            if let Some((pid, dpos)) = recent {
                if shorten_respawn(sim, pid, 1).is_ok() {
                    self.fallen_allies.remove(&pid);
                    self.spirit = Some(SpiritState {
                        player_id: pid,
                        death_pos: dpos,
                        placed: false,
                        end_tick: tick + SPIRIT_TICKS,
                        kills_at_start: Self::count_team_kills(sim, my_team),
                    });
                    sim.play_view_effect("abysspact_vesper_pillar", entity, &InputTargetV1::pos(dpos.0, dpos.1), 0, 0, 0);
                    sim.play_sfx("abysspact_vesper_return_pillar", entity, &InputTargetV1::pos(dpos.0, dpos.1));
                    revived = true;
                }
            }
            if !revived {
                self.fallback_aoe_shield(sim, entity, my_team, my_pos, ap);
            }
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_vesper:vigil", VesperPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn candle_buffs_and_fallback_shield_scale_up_to_5_candles() {
        assert_eq!(candle_buff_name(0), None);
        assert_eq!(candle_buff_name(1), Some("abysspact_vesper_candle_1"));
        assert_eq!(candle_buff_name(5), Some("abysspact_vesper_candle_5"));
        assert_eq!(candle_buff_name(6), None);
        // base 100 + 60% of 100 AP = 160; 5 candles = +50% -> 240
        assert_eq!(fallback_shield_amount(100, 0), 160);
        assert_eq!(fallback_shield_amount(100, 5), 240);
        assert_eq!(fallback_shield_amount(100, 9), 240);
    }
}
