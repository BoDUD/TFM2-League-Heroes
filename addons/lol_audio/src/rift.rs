//! Rin 的召唤师峡谷（第三方地图 mod `tfm2_lol_map_test`，0.1.65 起）的虚空巢虫和峡谷先锋（用户 11-26：「巢虫、先锋应该报相应的吧
//! 可以做到吧」）。英雄联盟的播报员没有它们的台词：客户端播报包里 164 条事件、游戏数据里提到的所有播报事件都查过，野怪只有
//! 「拿下小龙」「拿下大龙」。所以放它们自己在英雄联盟里的声音（Map11.wad.client 的 NPC_Map11_Horde_SFX /
//! NPC_Map11_RiftHerald_SFX，build_audio.py 的 `MONSTER`）：巢虫钻出来、每只巢虫的死叫（四种轮着来）、剩下的巢虫退场、先锋出场的
//! 吼叫、先锋倒下、有一队把先锋放出来时碎眼的那一声。不排在播报员后面，当时就放。
//!
//! 认它们只看名字（游戏里是哪种实体不知道：Rin 的 DLL 自己生出来的）。野的（中立）和放出来的（某一队的）先锋分开：放出来的先锋
//! 出场是碎眼声，它撞塔死了不报。第一次看到这一场时只记下，不补放（复盘、中途接上的比赛）。

/// 巢虫的名字前缀（rift_voidgrub_L / rift_voidgrub_R：朝左、朝右两种画面）。
pub const GRUB: &str = "rift_voidgrub";
/// 峡谷先锋的名字。
pub const HERALD: &str = "tfm2_rift_herald";
/// 声音事件（sound/sfx/lol_audio_<名字>.sound_info）。
pub const GRUBS_SPAWN: &str = "lol_audio_grubs_spawn";
pub const GRUB_DEATH: &str = "lol_audio_grub_death";
pub const GRUBS_LEAVE: &str = "lol_audio_grubs_leave";
pub const HERALD_SPAWN: &str = "lol_audio_herald_spawn";
pub const HERALD_DEATH: &str = "lol_audio_herald_death";
pub const HERALD_SUMMON: &str = "lol_audio_herald_summon";
/// 巢虫的死叫有几种（`lol_audio_grub_death`、`_2` .. `_4`）。
pub const GRUB_VARIANTS: usize = 4;
/// Rin 0.1.65 的时间表（发布清单.json）：巢虫 14:45 退场、先锋 19:45 退场。这之后不见的是走了，不是被打死。
pub const GRUBS_GONE_T: usize = 885 * 60;
pub const HERALD_GONE_T: usize = 1185 * 60;
/// 退场前后这么多 tick 不见了算走了。
pub const GONE_SLACK: usize = 120;
/// 这么久以内出来的巢虫算同一波，只放一次。
pub const WAVE_T: usize = 600;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Who {
    Grub,
    Herald,
}

/// 名字是不是巢虫 / 先锋。
pub fn who(name: &str) -> Option<Who> {
    if name.starts_with(GRUB) {
        Some(Who::Grub)
    } else if name == HERALD {
        Some(Who::Herald)
    } else {
        None
    }
}

/// 这一 tick 看到的一只。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Unit {
    pub id: usize,
    pub who: Who,
    /// 中立的（野怪）；先锋被放出来以后是某一队的。
    pub wild: bool,
    pub alive: bool,
    pub at: (u64, u64),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cue {
    GrubsSpawn,
    /// 第几种死叫（0 起）。
    GrubDeath(usize),
    GrubsLeave,
    HeraldSpawn,
    HeraldDeath,
    HeraldSummon,
}

impl Cue {
    /// 这一声的声音事件。
    pub fn event(self) -> String {
        match self {
            Cue::GrubsSpawn => GRUBS_SPAWN.to_string(),
            Cue::GrubDeath(0) => GRUB_DEATH.to_string(),
            Cue::GrubDeath(k) => format!("{GRUB_DEATH}_{}", k % GRUB_VARIANTS + 1),
            Cue::GrubsLeave => GRUBS_LEAVE.to_string(),
            Cue::HeraldSpawn => HERALD_SPAWN.to_string(),
            Cue::HeraldDeath => HERALD_DEATH.to_string(),
            Cue::HeraldSummon => HERALD_SUMMON.to_string(),
        }
    }
}

/// 一场比赛里看到的巢虫、先锋。
#[derive(Debug, Default)]
pub struct Monsters {
    seen: bool,
    alive: Vec<Unit>,
    wave_at: Option<usize>,
    deaths: usize,
    left_at: Option<usize>,
}

impl Monsters {
    /// 这一 tick（`tick`）看到的 `now`：新出来的、死了的、不见了的各给一声（声音、在哪、放在谁身上）。
    pub fn step(&mut self, tick: usize, now: &[Unit]) -> Vec<(Cue, (u64, u64), Option<usize>)> {
        let mut out = Vec::new();
        let living: Vec<Unit> = now.iter().copied().filter(|u| u.alive).collect();
        if !self.seen {
            self.seen = true;
            self.alive = living;
            return out;
        }
        for u in &living {
            if self.alive.iter().any(|a| a.id == u.id) {
                continue;
            }
            match (u.who, u.wild) {
                (Who::Grub, true) => {
                    if self.wave_at.is_none_or(|t| tick > t + WAVE_T) {
                        out.push((Cue::GrubsSpawn, u.at, Some(u.id)));
                    }
                    self.wave_at = Some(tick);
                }
                (Who::Herald, true) => out.push((Cue::HeraldSpawn, u.at, Some(u.id))),
                (Who::Herald, false) => out.push((Cue::HeraldSummon, u.at, Some(u.id))),
                (Who::Grub, false) => {}
            }
        }
        for a in std::mem::take(&mut self.alive) {
            if living.iter().any(|u| u.id == a.id) {
                continue;
            }
            // 还在、但死了：被打死；整个不见了：快到退场的时候是走了，别的时候也当被打死（死了当场就收走的）
            let dead = now.iter().any(|u| u.id == a.id && !u.alive);
            let gone_t = match a.who {
                Who::Grub => GRUBS_GONE_T,
                Who::Herald => HERALD_GONE_T,
            };
            let left = !dead && tick + GONE_SLACK >= gone_t;
            match (a.who, a.wild, left) {
                (Who::Grub, true, false) => {
                    out.push((Cue::GrubDeath(self.deaths % GRUB_VARIANTS), a.at, None));
                    self.deaths += 1;
                }
                (Who::Grub, true, true) => {
                    if self.left_at.is_none_or(|t| tick > t + WAVE_T) {
                        out.push((Cue::GrubsLeave, a.at, None));
                    }
                    self.left_at = Some(tick);
                }
                (Who::Herald, true, false) => out.push((Cue::HeraldDeath, a.at, None)),
                _ => {}
            }
        }
        self.alive = living;
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn grub(id: usize, alive: bool) -> Unit {
        Unit { id, who: Who::Grub, wild: true, alive, at: (650_000, 570_000) }
    }

    fn herald(id: usize, wild: bool, alive: bool) -> Unit {
        Unit { id, who: Who::Herald, wild, alive, at: (660_000, 570_000) }
    }

    #[test]
    fn names() {
        assert_eq!(who("rift_voidgrub_L"), Some(Who::Grub));
        assert_eq!(who("rift_voidgrub_R"), Some(Who::Grub));
        assert_eq!(who("tfm2_rift_herald"), Some(Who::Herald));
        assert_eq!(who("epic_monster"), None);
        assert_eq!(Cue::GrubDeath(0).event(), "lol_audio_grub_death");
        assert_eq!(Cue::GrubDeath(3).event(), "lol_audio_grub_death_4");
        assert_eq!(Cue::GrubDeath(5).event(), "lol_audio_grub_death_2");
    }

    /// 8:00 三只一起出来：一声；一只只被打死：各一声死叫、轮着换；14:45 剩下的退场：一声，不算被打死。
    #[test]
    fn the_grubs_wave() {
        let mut m = Monsters::default();
        assert!(m.step(100, &[]).is_empty(), "the first look only notes");
        let wave = [grub(31, true), grub(32, true), grub(33, true)];
        let cues = m.step(28_800, &wave);
        assert_eq!(cues.iter().map(|c| c.0).collect::<Vec<_>>(), vec![Cue::GrubsSpawn]);
        assert!(m.step(28_803, &wave).is_empty());
        // one killed (it lies there dead), one gone at once (taken away the tick it died)
        let cues = m.step(30_000, &[grub(31, false), grub(32, true), grub(33, true)]);
        assert_eq!(cues, vec![(Cue::GrubDeath(0), (650_000, 570_000), None)]);
        let cues = m.step(30_300, &[grub(33, true)]);
        assert_eq!(cues.iter().map(|c| c.0).collect::<Vec<_>>(), vec![Cue::GrubDeath(1)]);
        // the last one leaves at 14:45
        let cues = m.step(GRUBS_GONE_T, &[]);
        assert_eq!(cues.iter().map(|c| c.0).collect::<Vec<_>>(), vec![Cue::GrubsLeave]);
    }

    /// 先锋：15:00 出场一声，被打死一声；放出来是某一队的：碎眼一声，它撞塔死了不报；19:45 没人打走了不报。
    #[test]
    fn the_herald() {
        let mut m = Monsters::default();
        m.step(0, &[]);
        assert_eq!(m.step(54_000, &[herald(50, true, true)]).iter().map(|c| c.0).collect::<Vec<_>>(), vec![Cue::HeraldSpawn]);
        assert_eq!(m.step(60_000, &[herald(50, true, false)]).iter().map(|c| c.0).collect::<Vec<_>>(), vec![Cue::HeraldDeath]);
        assert_eq!(m.step(60_600, &[herald(51, false, true)]).iter().map(|c| c.0).collect::<Vec<_>>(), vec![Cue::HeraldSummon]);
        assert!(m.step(62_000, &[herald(51, false, false)]).is_empty(), "the summoned one dying is no news");
        // another match: nobody took it, it leaves at 19:45
        let mut m = Monsters::default();
        m.step(0, &[]);
        m.step(54_000, &[herald(50, true, true)]);
        assert!(m.step(HERALD_GONE_T, &[]).is_empty());
    }

    /// 中途接上的比赛（复盘跳到中间）：第一眼看到的不补放。
    #[test]
    fn joined_late_nothing_replayed() {
        let mut m = Monsters::default();
        assert!(m.step(40_000, &[grub(31, true), herald(50, true, true)]).is_empty());
        assert_eq!(m.step(40_003, &[grub(31, false), herald(50, true, true)]).iter().map(|c| c.0).collect::<Vec<_>>(),
                   vec![Cue::GrubDeath(0)]);
    }
}
