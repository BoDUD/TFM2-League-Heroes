//! 大小龙的规则（纯函数，单元测试在这里）：元素和刷新顺序、每层亚龙的数值、中和游戏自带的小龙 buff、龙魂、远古龙之力、
//! 纳什男爵之手的数字，和挂在水晶上的状态记录、事件的格式（README「给画面的接口」）。
//!
//! 模拟里的东西由 `lib.rs` 读出来交给这里；这里不碰模拟。

use mod_api_stable::*;

// ===================== 元素 =====================

/// 六种元素亚龙和远古巨龙。编号（`code`）就是状态记录、事件里的那一位：1 炼狱 … 6 化学科技，7 远古，0 = 没有。
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Element {
    Infernal = 1,
    Mountain = 2,
    Ocean = 3,
    Cloud = 4,
    Hextech = 5,
    Chemtech = 6,
    Elder = 7,
}

/// 六种元素亚龙（远古巨龙不在里面），按编号排。
pub const DRAKES: [Element; 6] =
    [Element::Infernal, Element::Mountain, Element::Ocean, Element::Cloud, Element::Hextech, Element::Chemtech];

impl Element {
    pub fn code(self) -> u8 {
        self as u8
    }

    pub fn from_code(c: u8) -> Option<Element> {
        match c {
            1 => Some(Element::Infernal),
            2 => Some(Element::Mountain),
            3 => Some(Element::Ocean),
            4 => Some(Element::Cloud),
            5 => Some(Element::Hextech),
            6 => Some(Element::Chemtech),
            7 => Some(Element::Elder),
            _ => None,
        }
    }

    /// buff 名、日志里的英文小写名。
    pub fn key(self) -> &'static str {
        match self {
            Element::Infernal => "infernal",
            Element::Mountain => "mountain",
            Element::Ocean => "ocean",
            Element::Cloud => "cloud",
            Element::Hextech => "hextech",
            Element::Chemtech => "chemtech",
            Element::Elder => "elder",
        }
    }

    /// 简体中文名（英雄联盟国服的叫法）。
    pub fn zh(self) -> &'static str {
        match self {
            Element::Infernal => "炼狱",
            Element::Mountain => "山脉",
            Element::Ocean => "海洋",
            Element::Cloud => "云端",
            Element::Hextech => "海克斯",
            Element::Chemtech => "化学科技",
            Element::Elder => "远古",
        }
    }

    /// 元素亚龙在层数表里的位置（0..6，按编号）；远古巨龙没有层数：None。
    pub fn slot(self) -> Option<usize> {
        (self != Element::Elder).then(|| self as usize - 1)
    }
}

// ===================== 刷新顺序 =====================

/// splitmix64：同一个数进去，哪台机器、哪份模拟出来都一样。
pub fn mix(mut z: u64) -> u64 {
    z = z.wrapping_add(0x9e37_79b9_7f4a_7c15);
    z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    z ^ (z >> 31)
}

/// 一局的元素顺序（英雄联盟的规矩）：第一条随机，第二条随机且和第一条不同，第三条和前两条都不同——第二条被拿下后峡谷变成
/// 第三条的元素，之后到龙魂为止都是它（龙魂也是它）。种子是模拟的种子（`sim.seed()`）：同一小局的两份预演和屏幕上的两遍
/// 都一样（league.log 的 SET 行：预演和画面同一个 seed），所以元素也一样。
pub fn order(seed: u64) -> [Element; 3] {
    let mut pool: Vec<Element> = DRAKES.to_vec();
    let mut out = [Element::Infernal; 3];
    let mut s = seed ^ 0x6c65_6167_7565_6472; // "leaguedr"
    for slot in out.iter_mut() {
        s = mix(s);
        *slot = pool.remove((s % pool.len() as u64) as usize);
    }
    out
}

/// 下一条（或活着的那条）龙的元素：已经有队伍拿到龙魂 -> 远古巨龙；否则按拿下的元素亚龙条数（两队一共）看顺序。
pub fn next_element(order: &[Element; 3], drakes_taken: u32, soul_claimed: bool) -> Element {
    if soul_claimed {
        return Element::Elder;
    }
    match drakes_taken {
        0 => order[0],
        1 => order[1],
        _ => order[2],
    }
}

// ===================== 每层亚龙 =====================

/// 各元素每层（整队、永久、叠加）：炼狱攻击力和法强 +8%，山脉护甲和魔抗 +10%，海洋每 5 秒回 3% 已损生命（[`OCEAN_EVERY`]），
/// 云端移速 +8%，海克斯攻速 +10%、技能冷却 -8%（`skill_cooldown_mult` 9：冷却封顶在 100 / 109 = 92%），化学科技韧性 +10%、
/// 生命偷取 +3%。
pub const INFERNAL_PCT: i32 = 8;
pub const MOUNTAIN_PCT: i32 = 10;
pub const OCEAN_PCT: usize = 3;
pub const OCEAN_EVERY: usize = 300;
pub const CLOUD_PCT: i32 = 8;
pub const HEXTECH_AS: i32 = 10;
pub const HEXTECH_CD: i32 = 9;
pub const CHEMTECH_TENACITY: usize = 10;
pub const CHEMTECH_VAMP: i32 = 3;

/// 一队拿下的某种元素亚龙的 buff：`league_dragons_dk_<元素>`，数值 = 每层 × 层数（只挂一个，层数变了换掉）。
pub const DK: &str = "league_dragons_dk_";

pub fn drake_name(e: Element) -> String {
    format!("{DK}{}", e.key())
}

pub fn drake_buff(e: Element, n: u8) -> BuffV1 {
    let k = n as i32;
    let mut b = BuffV1::named(&drake_name(e));
    match e {
        Element::Infernal => {
            b.attack_mult = INFERNAL_PCT * k;
            b.magic_power_mult = INFERNAL_PCT * k;
        }
        Element::Mountain => {
            b.defence_mult = MOUNTAIN_PCT * k;
            b.magic_resistance_mult = MOUNTAIN_PCT * k;
        }
        // the regen is a pulse of the hook's (ocean_heal): the buff only names the stacks
        Element::Ocean | Element::Elder => {}
        Element::Cloud => b.move_speed_mult = CLOUD_PCT * k,
        Element::Hextech => {
            b.attack_speed_mult = HEXTECH_AS * k;
            b.skill_cooldown_mult = HEXTECH_CD * k;
        }
        Element::Chemtech => {
            b.toughness = CHEMTECH_TENACITY * n as usize;
            b.vamp = CHEMTECH_VAMP * k;
        }
    }
    b
}

/// 海洋亚龙每 [`OCEAN_EVERY`] tick 回的生命：已损生命的 3% × 层数。
pub fn ocean_heal(hp: usize, max: usize, stacks: u8) -> usize {
    max.saturating_sub(hp) * OCEAN_PCT * stacks as usize / 100
}

// ===================== 中和游戏自带的小龙 buff =====================

/// 游戏自带的小龙奖励（GameSetting 的 `epic_permanent_stat`，每拿一条小龙给全队挂一个，死了也留着）。
pub const NATIVE: &str = "serpen_permanent_buff";
/// 中和它的 buff：每个英雄一个，数值是他身上所有 `serpen_permanent_buff` 加起来再取负（引擎把同名 buff 的数值全部加起来）。
pub const NAT: &str = "league_dragons_nat";

macro_rules! signed_fields {
    ($m:ident) => {
        $m!(attack, attack_mult, magic_power, magic_power_mult, defence, defence_mult, hp, hp_regen, magic_resistance,
            magic_resistance_mult, vamp, hp_mult, move_speed_mult, attack_speed_mult, skill_cooldown_mult,
            ult_cooldown_mult, radius_mult, crit_chance)
    };
}

/// 不能取负的字段（无符号、开关）：游戏的赛季补丁哪天给小龙 buff 加上这些，中和不掉，记进日志（`NEUTRALIZE … left`）。
pub fn unsigned_set(b: &BuffV1) -> Vec<&'static str> {
    let mut v = Vec::new();
    macro_rules! check {
        ($($f:ident),*) => { $( if b.$f != 0 { v.push(stringify!($f)); } )* };
    }
    check!(damage_reflect, damaged_amplify, damaged_reduce, defence_penetration, magic_resistance_penetration, toughness,
           heal_reduce, range, base_attack_enemy_max_hp_damage, self_max_hp_damage, skill_enemy_max_hp_damage,
           dot_amplify, base_attack_damaged_reduce, skill_damaged_reduce);
    if b.cc_immune {
        v.push("cc_immune");
    }
    if b.undying {
        v.push("undying");
    }
    if b.ignore_wall {
        v.push("ignore_wall");
    }
    v
}

/// 一个英雄身上的游戏小龙 buff（`native`：每个实例照游戏里读出来的数值，赛季补丁改了数也跟着）-> 中和它的 buff（全是 0：
/// None）和中和不掉的字段名。
pub fn neutralizer(native: &[BuffV1]) -> (Option<BuffV1>, Vec<&'static str>) {
    let mut n = BuffV1::named(NAT);
    let mut any = false;
    macro_rules! negate {
        ($($f:ident),*) => {
            $( let sum: i64 = native.iter().map(|b| b.$f as i64).sum();
               n.$f = (-sum).clamp(i32::MIN as i64, i32::MAX as i64) as i32;
               any |= sum != 0; )*
        };
    }
    signed_fields!(negate);
    let mut left: Vec<&'static str> = Vec::new();
    for b in native {
        for f in unsigned_set(b) {
            if !left.contains(&f) {
                left.push(f);
            }
        }
    }
    (any.then_some(n), left)
}

/// 有数值的字段写成一串（日志）：`attack_mult +4, move_speed_mult +1`。
pub fn stats_text(b: &BuffV1) -> String {
    let mut v: Vec<String> = Vec::new();
    macro_rules! put {
        ($($f:ident),*) => { $( if b.$f != 0 { v.push(format!("{} {:+}", stringify!($f), b.$f)); } )* };
    }
    signed_fields!(put);
    for f in unsigned_set(b) {
        v.push(f.to_string());
    }
    if v.is_empty() {
        "nothing".to_string()
    } else {
        v.join(", ")
    }
}

/// 两个 buff 的数值一样（名字、时长不比）。
pub fn same_stats(a: &BuffV1, b: &BuffV1) -> bool {
    let mut x = *b;
    x.name_buf = a.name_buf;
    x.name_len = a.name_len;
    x.duration_kind = a.duration_kind;
    x.duration_tick = a.duration_tick;
    x == *a
}

// ===================== 龙魂 =====================

/// 第一个拿到这么多条元素亚龙的队伍拿到龙魂（另一队之后再拿到也没有）。
pub const SOUL_AT: u8 = 4;

/// 一队这一条之后一共有 `team_total` 条：拿到龙魂没有。
pub fn soul_claimed(team_total: u8, soul_taken: bool) -> bool {
    !soul_taken && team_total >= SOUL_AT
}

/// 龙魂的标记（整局都在，死了复活补回）：`league_dragons_soul_<元素>`；云端龙魂带着移速 +15%，其余的效果是钩子做的。
pub const SOUL: &str = "league_dragons_soul_";
pub const CLOUD_SOUL_MS: i32 = 15;

pub fn soul_name(e: Element) -> String {
    format!("{SOUL}{}", e.key())
}

pub fn soul_buff(e: Element) -> BuffV1 {
    let mut b = BuffV1::named(&soul_name(e));
    if e == Element::Cloud {
        b.move_speed_mult = CLOUD_SOUL_MS;
    }
    b
}

/// 炼狱龙魂：每 3 秒，下一次对敌方英雄造成伤害时在他身上爆炸：魔法伤害 100 + 25% 攻击力 + 15% 法强，波及他身边 25000 以内的
/// 敌方英雄。
pub const INFERNAL_SOUL_CD: usize = 180;
pub const INFERNAL_SOUL_R: u64 = 25_000;

pub fn infernal_soul_damage(ad: usize, ap: usize) -> usize {
    100 + ad * 25 / 100 + ap * 15 / 100
}

/// 山脉龙魂：5 秒没受伤害后，一层护盾 200 + 15% 攻击力 + 10% 法强 + 8% 最大生命（补满到这么多，不叠）。
pub const MOUNTAIN_SOUL_IDLE: usize = 300;
pub const MOUNTAIN_SOUL_T: usize = 3_600;
/// 多久看一次要不要补盾。
pub const MOUNTAIN_SOUL_CHECK: usize = 30;

pub fn mountain_soul_shield(ad: usize, ap: usize, max_hp: usize) -> usize {
    200 + ad * 15 / 100 + ap * 10 / 100 + max_hp * 8 / 100
}

/// 海洋龙魂：对敌方英雄造成伤害后 4 秒里回 160 + 30% 攻击力 + 20% 法强 + 8% 最大生命（8 次、每 30 tick 一次），冷却 4 秒。
pub const OCEAN_SOUL_CD: usize = 240;
pub const OCEAN_SOUL_PULSES: u8 = 8;
pub const OCEAN_SOUL_EVERY: usize = 30;

pub fn ocean_soul_heal(ad: usize, ap: usize, max_hp: usize) -> usize {
    160 + ad * 30 / 100 + ap * 20 / 100 + max_hp * 8 / 100
}

/// 云端龙魂：放大招后移速 +50%，6 秒（`league_dragons_cloud_haste`）。大招冷却一下子涨上去这么多算放了大招。
pub const CLOUD_HASTE: &str = "league_dragons_cloud_haste";
pub const CLOUD_HASTE_MS: i32 = 50;
pub const CLOUD_HASTE_T: usize = 360;
pub const ULT_JUMP: usize = 60;

pub fn cloud_haste() -> BuffV1 {
    let mut b = BuffV1::timed(CLOUD_HASTE, CLOUD_HASTE_T);
    b.move_speed_mult = CLOUD_HASTE_MS;
    b
}

/// 海克斯龙魂：每 2.5 秒，下一次命中的敌方英雄放出连锁闪电，打他和他身边 40000 以内最近的另外两个敌方英雄：魔法伤害
/// 40 + 30% 攻击力 + 20% 法强，减速 90%、0.25 秒（`league_dragons_hex_slow`）。
pub const HEXTECH_SOUL_CD: usize = 150;
pub const HEXTECH_SOUL_R: u64 = 40_000;
pub const HEXTECH_SOUL_TARGETS: usize = 3;
pub const HEX_SLOW: &str = "league_dragons_hex_slow";
pub const HEX_SLOW_PCT: i32 = 90;
pub const HEX_SLOW_T: usize = 15;

pub fn hextech_soul_damage(ad: usize, ap: usize) -> usize {
    40 + ad * 30 / 100 + ap * 20 / 100
}

pub fn hex_slow() -> BuffV1 {
    let mut b = BuffV1::timed(HEX_SLOW, HEX_SLOW_T);
    b.move_speed_mult = -HEX_SLOW_PCT;
    b
}

/// 化学科技龙魂：生命低于 50% 时韧性 +15%、伤害 +12%、受到的伤害 -12%（`league_dragons_chem_low`；buff 没有「造成的伤害」
/// 这一项，+12% 攻击力和法强代替，README「和设计不一样的地方」）。
pub const CHEM_LOW: &str = "league_dragons_chem_low";
pub const CHEM_LOW_PCT: usize = 50;

pub fn chem_low(hp: usize, max: usize) -> bool {
    max > 0 && hp * 100 < max * CHEM_LOW_PCT
}

pub fn chem_low_buff() -> BuffV1 {
    let mut b = BuffV1::named(CHEM_LOW);
    b.toughness = 15;
    b.damaged_reduce = 12;
    b.attack_mult = 12;
    b.magic_power_mult = 12;
    b
}

// ===================== 远古龙之力 =====================

/// 远古龙之力：拿下远古巨龙的一方当时活着的英雄 90 秒（死了就没了）：对敌方英雄的伤害点燃他（真实伤害 50 + 10% 攻击力，
/// 1.5 秒里 3 次），着火的敌方英雄生命低于 20% 时被处决（击杀算这个英雄的）。
pub const ELDER: &str = "league_dragons_elder";
pub const ELDER_T: usize = 5_400;
pub const BURN: &str = "league_dragons_burn";
pub const BURN_T: usize = 90;
pub const BURN_PULSES: u8 = 3;
pub const BURN_EVERY: usize = 30;
pub const EXECUTE_PCT: usize = 20;
/// 被处决的英雄身上挂一下（只有名字，给画面放处决的大动静）。
pub const EXECUTED: &str = "league_dragons_executed";
pub const EXECUTED_T: usize = 60;

pub fn burn_total(ad: usize) -> usize {
    50 + ad * 10 / 100
}

/// 处决打出的真实伤害：护盾和生命的 4 倍再加最大生命（护盾先扣；减伤 75% 以内也打得死）。
pub fn execute_damage(hp: usize, shield: usize, max: usize) -> usize {
    (hp + shield) * 4 + max
}

/// 生命低于最大生命的 20%（严格低于）。
pub fn executable(hp: usize, max: usize) -> bool {
    max > 0 && hp > 0 && hp * 100 < max * EXECUTE_PCT
}

pub fn elder_buff(left: usize) -> BuffV1 {
    BuffV1::timed(ELDER, left.max(1))
}

// ===================== 纳什男爵之手 =====================

/// 纳什男爵之手：拿下纳什男爵（游戏里的莫甘德，`Epic`）的一方当时活着的英雄 120 秒（死了就没了）：攻击力、法强 +20%；
/// 他身边 140000 以内的己方小兵受到的伤害 -40%、攻击力 +30%（`league_dragons_baron_minion`，每 30 tick 续 45 tick）。
pub const BARON: &str = "league_dragons_baron";
pub const BARON_T: usize = 7_200;
pub const BARON_PCT: i32 = 20;
pub const MINION_BOOST: &str = "league_dragons_baron_minion";
pub const MINION_R: u64 = 140_000;
pub const MINION_REDUCE: usize = 40;
pub const MINION_ATTACK: i32 = 30;
pub const BOOST_EVERY: usize = 30;
pub const BOOST_T: usize = 45;

pub fn baron_buff(left: usize) -> BuffV1 {
    let mut b = BuffV1::timed(BARON, left.max(1));
    b.attack_mult = BARON_PCT;
    b.magic_power_mult = BARON_PCT;
    b
}

pub fn minion_boost() -> BuffV1 {
    let mut b = BuffV1::timed(MINION_BOOST, BOOST_T);
    b.damaged_reduce = MINION_REDUCE;
    b.attack_mult = MINION_ATTACK;
    b
}

// ===================== 给画面的接口：状态记录、事件 =====================

/// 活着的小龙身上的元素标记：`league_dragons_el_<元素>`（只有名字，从它出生起就挂着）。
pub const EL: &str = "league_dragons_el_";

pub fn marker(e: Element) -> String {
    format!("{EL}{}", e.key())
}

/// 状态记录（每个水晶上一个只有名字的 buff）：`league_dragons_st:` 后面 43 个字符，定长、十六进制，README 有逐位的表。
pub const ST: &str = "league_dragons_st:";
pub const ST_VERSION: char = '1';
pub const ST_LEN: usize = 43;
/// 事件（每个水晶上一个只有名字、`EV_T` tick 的 buff）：`league_dragons_ev:<序号 2><tick 5><种类 1><参数>`。
pub const EV: &str = "league_dragons_ev:";
pub const EV_T: usize = 1_800;
/// 没有队伍（状态记录里）。
pub const NO_TEAM: usize = 2;

/// 远古龙之力 / 纳什男爵之手在一队身上：(队伍, 拿着的人：按分路的位, 到哪个 tick)。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct HoldRec {
    pub team: usize,
    pub lanes: u8,
    pub until: usize,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Record {
    /// 写这份记录的 tick。
    pub tick: usize,
    /// 活着的那条龙的元素，没有活着的就是下一条的（1..7）。
    pub cur: u8,
    /// 这一局的顺序：第一条、第二条、峡谷（龙魂）的元素。
    pub order: [u8; 3],
    /// 两队（0 蓝、1 红）每种元素的层数，按元素编号 1..6 排。
    pub stacks: [[u8; 6]; 2],
    /// 拿到龙魂的队伍和元素。
    pub soul: Option<(usize, u8)>,
    pub elder: Option<HoldRec>,
    pub baron: Option<HoldRec>,
    /// 撞上创意工坊的「Elemental Drakes & Baron」（水晶上有它的 `sed_*`）：本包什么都不做。
    pub conflict: bool,
    pub serpen_alive: bool,
    pub epic_alive: bool,
    /// 到现在一共几件事（模 256）：画面看它变了就去读事件。
    pub seq: u8,
}

fn hex(n: usize, width: usize) -> String {
    let max = (1usize << (4 * width)) - 1;
    format!("{:0width$x}", n.min(max), width = width)
}

fn hold_text(h: &Option<HoldRec>) -> String {
    match h {
        Some(h) => format!("{}{}{}", h.team.min(1), hex(h.lanes as usize, 2), hex(h.until, 5)),
        None => format!("{NO_TEAM}00{}", hex(0, 5)),
    }
}

impl Record {
    /// 两队一共拿下了几条元素亚龙。
    pub fn drakes_taken(&self) -> u32 {
        self.stacks.iter().flatten().map(|&n| n as u32).sum()
    }

    /// HUD、说明框能说出来的龙魂元素：第三条小龙出现了才说（用户 2026-11-10：「为什么现在开局就显示龙魂是什么了 不符合逻辑
    /// 应该和英雄联盟一样啊 第三条小龙出来时才显示龙魂吧」）——拿了两条、第三条活着，或者已经拿了三条以上；龙魂被拿走了就不再说。
    pub fn soul_shown(&self) -> Option<Element> {
        if self.soul.is_some() {
            return None;
        }
        let n = self.drakes_taken();
        (n >= 3 || (n == 2 && self.serpen_alive)).then(|| Element::from_code(self.order[2])).flatten()
    }

    /// 挂在水晶上的名字（61 个字节，buff 名最多 64）。
    pub fn name(&self) -> String {
        let mut s = String::with_capacity(ST.len() + ST_LEN);
        s.push_str(ST);
        s.push(ST_VERSION);
        s.push_str(&hex(self.tick, 5));
        s.push_str(&hex(self.cur as usize, 1));
        for o in self.order {
            s.push_str(&hex(o as usize, 1));
        }
        for team in self.stacks {
            for n in team {
                s.push_str(&hex(n as usize, 1));
            }
        }
        match self.soul {
            Some((t, e)) => s.push_str(&format!("{}{}", t.min(1), hex(e as usize, 1))),
            None => s.push_str(&format!("{NO_TEAM}0")),
        }
        s.push_str(&hold_text(&self.elder));
        s.push_str(&hold_text(&self.baron));
        let flags = self.conflict as usize | (self.serpen_alive as usize) << 1 | (self.epic_alive as usize) << 2;
        s.push_str(&hex(flags, 1));
        s.push_str(&hex(self.seq as usize, 2));
        s
    }

    /// 读回一份记录（不是本包的、版本不对、长度不对：None）。
    pub fn parse(name: &str) -> Option<Record> {
        let body = name.strip_prefix(ST)?;
        if body.len() != ST_LEN || !body.starts_with(ST_VERSION) || !body.is_ascii() {
            return None;
        }
        let num = |from: usize, len: usize| usize::from_str_radix(&body[from..from + len], 16).ok();
        let hold = |at: usize| -> Option<Option<HoldRec>> {
            let team = num(at, 1)?;
            if team >= NO_TEAM {
                return Some(None);
            }
            Some(Some(HoldRec { team, lanes: num(at + 1, 2)? as u8, until: num(at + 3, 5)? }))
        };
        let mut r = Record { tick: num(1, 5)?, cur: num(6, 1)? as u8, ..Record::default() };
        for i in 0..3 {
            r.order[i] = num(7 + i, 1)? as u8;
        }
        for team in 0..2 {
            for e in 0..6 {
                r.stacks[team][e] = num(10 + 6 * team + e, 1)? as u8;
            }
        }
        let soul_team = num(22, 1)?;
        r.soul = (soul_team < NO_TEAM).then_some((soul_team, num(23, 1)? as u8));
        r.elder = hold(24)?;
        r.baron = hold(32)?;
        let flags = num(40, 1)?;
        (r.conflict, r.serpen_alive, r.epic_alive) = (flags & 1 != 0, flags & 2 != 0, flags & 4 != 0);
        r.seq = num(41, 2)? as u8;
        Some(r)
    }
}

/// 一件事（画面放公告用）。队伍 0 蓝、1 红；分路是 `LaneV1` 的编号；`lanes` 是按分路的位。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Ev {
    /// 一条元素亚龙出生（P）。
    DrakeSpawn { element: Element },
    /// 远古巨龙出生（E）。
    ElderSpawn,
    /// 一队拿下一条元素亚龙（D）：这一队拿下这种元素的第几层、一共几条。
    Drake { team: usize, element: Element, total: u8 },
    /// 一队拿到龙魂（S）。
    Soul { team: usize, element: Element },
    /// 一队拿下远古巨龙（K）：拿到远古龙之力的人。
    ElderKilled { team: usize, lanes: u8 },
    /// 远古龙之力的处决（X）：处决的人（队伍、分路），被处决的人在另一队的分路。
    Execute { team: usize, lane: u8, victim_lane: u8 },
    /// 一队拿下纳什男爵（B）：拿到纳什男爵之手的人。
    BaronKilled { team: usize, lanes: u8 },
    /// 撞上创意工坊的大小龙 mod（C）：本包什么都不做。
    Conflict,
}

impl Ev {
    pub fn code(&self) -> char {
        match self {
            Ev::DrakeSpawn { .. } => 'P',
            Ev::ElderSpawn => 'E',
            Ev::Drake { .. } => 'D',
            Ev::Soul { .. } => 'S',
            Ev::ElderKilled { .. } => 'K',
            Ev::Execute { .. } => 'X',
            Ev::BaronKilled { .. } => 'B',
            Ev::Conflict => 'C',
        }
    }

    fn args(&self) -> String {
        match *self {
            Ev::DrakeSpawn { element } => hex(element.code() as usize, 1),
            Ev::ElderSpawn | Ev::Conflict => String::new(),
            Ev::Drake { team, element, total } => format!("{}{}{}", team.min(1), hex(element.code() as usize, 1),
                                                          hex(total as usize, 1)),
            Ev::Soul { team, element } => format!("{}{}", team.min(1), hex(element.code() as usize, 1)),
            Ev::ElderKilled { team, lanes } | Ev::BaronKilled { team, lanes } => {
                format!("{}{}", team.min(1), hex(lanes as usize, 2))
            }
            Ev::Execute { team, lane, victim_lane } => format!("{}{}{}", team.min(1), hex(lane as usize, 1),
                                                               hex(victim_lane as usize, 1)),
        }
    }
}

/// 事件 buff 的名字：`league_dragons_ev:<序号 2><tick 5><种类><参数>`。
pub fn event_name(seq: u8, tick: usize, ev: &Ev) -> String {
    format!("{EV}{}{}{}{}", hex(seq as usize, 2), hex(tick, 5), ev.code(), ev.args())
}

/// 读回一件事：(序号, tick, 那件事)。
pub fn parse_event(name: &str) -> Option<(u8, usize, Ev)> {
    let b = name.strip_prefix(EV)?;
    if !b.is_ascii() || b.len() < 8 {
        return None;
    }
    let num = |from: usize, len: usize| b.get(from..from + len).and_then(|s| usize::from_str_radix(s, 16).ok());
    let seq = num(0, 2)? as u8;
    let tick = num(2, 5)?;
    let el = |at: usize| num(at, 1).and_then(|c| Element::from_code(c as u8));
    let ev = match b.as_bytes()[7] {
        b'P' => Ev::DrakeSpawn { element: el(8)? },
        b'E' => Ev::ElderSpawn,
        b'D' => Ev::Drake { team: num(8, 1)?, element: el(9)?, total: num(10, 1)? as u8 },
        b'S' => Ev::Soul { team: num(8, 1)?, element: el(9)? },
        b'K' => Ev::ElderKilled { team: num(8, 1)?, lanes: num(9, 2)? as u8 },
        b'X' => Ev::Execute { team: num(8, 1)?, lane: num(9, 1)? as u8, victim_lane: num(10, 1)? as u8 },
        b'B' => Ev::BaronKilled { team: num(8, 1)?, lanes: num(9, 2)? as u8 },
        b'C' => Ev::Conflict,
        _ => return None,
    };
    Some((seq, tick, ev))
}

/// 创意工坊的「Elemental Drakes & Baron」（smart_elemental_drakes）挂在水晶上的记录：`sed_timer1:…`、`sed_env_site:…`、
/// `sed1:…`（11-08 的 league.log 里 DIVERGE 行列着的那些）。
pub fn workshop_record(buff: &str) -> bool {
    buff.strip_prefix("sed").is_some_and(|r| r.starts_with('_') || r.starts_with(|c: char| c.is_ascii_digit()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_order_follows_league_and_the_seed() {
        for seed in 0..2_000u64 {
            let o = order(seed);
            assert!(o[0] != o[1] && o[1] != o[2] && o[0] != o[2], "seed {seed}: {o:?}");
            assert!(o.iter().all(|e| *e != Element::Elder));
            // the same seed, the same order: the presim twins and the screen's runs agree
            assert_eq!(order(seed), o);
        }
        // every element comes first now and then, and the seeds do not all agree
        for e in DRAKES {
            assert!((0..600u64).any(|s| order(s)[0] == e), "{e:?} never first");
            assert!((0..600u64).any(|s| order(s)[2] == e), "{e:?} never the rift");
        }
        assert!((0..50u64).map(order).collect::<std::collections::BTreeSet<_>>().len() > 20);
        // drake 1, drake 2, then the rift's element every time until the soul; the elder after it
        let o = [Element::Ocean, Element::Cloud, Element::Infernal];
        assert_eq!(next_element(&o, 0, false), Element::Ocean);
        assert_eq!(next_element(&o, 1, false), Element::Cloud);
        for n in 2..7 {
            assert_eq!(next_element(&o, n, false), Element::Infernal);
        }
        assert_eq!(next_element(&o, 4, true), Element::Elder);
        assert_eq!(next_element(&o, 0, true), Element::Elder);
    }

    #[test]
    fn stacks_add_up_per_element() {
        let b = drake_buff(Element::Infernal, 3);
        assert_eq!((b.attack_mult, b.magic_power_mult, b.name()), (24, 24, "league_dragons_dk_infernal"));
        let b = drake_buff(Element::Mountain, 2);
        assert_eq!((b.defence_mult, b.magic_resistance_mult), (20, 20));
        assert_eq!(drake_buff(Element::Cloud, 4).move_speed_mult, 32);
        let b = drake_buff(Element::Hextech, 2);
        assert_eq!((b.attack_speed_mult, b.skill_cooldown_mult), (20, 18));
        let b = drake_buff(Element::Chemtech, 1);
        assert_eq!((b.toughness, b.vamp), (10, 3));
        let o = drake_buff(Element::Ocean, 2);
        assert!(same_stats(&o, &BuffV1::named("x")), "ocean: a name, the regen is the hook's");
        // 3% of the missing health a stack every 5 s
        assert_eq!(ocean_heal(400, 1000, 1), 18);
        assert_eq!(ocean_heal(400, 1000, 3), 54);
        assert_eq!(ocean_heal(1000, 1000, 3), 0);
    }

    fn native(pct: i32, ms: i32) -> BuffV1 {
        let mut b = BuffV1::named(NATIVE);
        (b.attack_mult, b.magic_power_mult, b.defence_mult, b.magic_resistance_mult, b.move_speed_mult) = (pct, pct, pct, pct, ms);
        b
    }

    #[test]
    fn the_native_drake_buff_is_neutralized_per_stack() {
        // the 2027 season patch's numbers: +4% x4 and +1% move speed, two stacks
        let (n, left) = neutralizer(&[native(4, 1), native(4, 1)]);
        let n = n.expect("a neutralizer");
        assert_eq!((n.attack_mult, n.magic_power_mult, n.defence_mult, n.magic_resistance_mult, n.move_speed_mult),
                   (-8, -8, -8, -8, -2));
        assert!(left.is_empty());
        assert_eq!(n.name(), NAT);
        // summed with what it cancels: nothing left (the engine adds every instance's numbers up)
        let mut sum = BuffV1::named("sum");
        for b in [native(4, 1), native(4, 1), n] {
            sum.attack_mult += b.attack_mult;
            sum.move_speed_mult += b.move_speed_mult;
            sum.defence_mult += b.defence_mult;
        }
        assert_eq!((sum.attack_mult, sum.move_speed_mult, sum.defence_mult), (0, 0, 0));
        // the pre-patch numbers (3) and a patch that adds flat health and tenacity: the health goes, the tenacity is told
        let mut p = native(3, 0);
        p.hp = 25;
        p.toughness = 5;
        let (n, left) = neutralizer(&[p, native(3, 0), native(3, 0)]);
        let n = n.unwrap();
        assert_eq!((n.attack_mult, n.hp, n.move_speed_mult), (-9, -25, 0));
        assert_eq!(left, vec!["toughness"]);
        // no native buff: nothing to hang
        assert!(neutralizer(&[]).0.is_none());
        assert!(neutralizer(&[BuffV1::named(NATIVE)]).0.is_none(), "an all-zero buff needs nothing");
        assert_eq!(stats_text(&native(4, 1)),
                   "attack_mult +4, magic_power_mult +4, defence_mult +4, magic_resistance_mult +4, move_speed_mult +1");
    }

    #[test]
    fn the_soul_comes_at_exactly_four_for_the_first_team() {
        assert!(!soul_claimed(3, false));
        assert!(soul_claimed(4, false));
        assert!(!soul_claimed(4, true), "the other team at 4 later: no soul");
        assert_eq!(soul_buff(Element::Cloud).move_speed_mult, 15);
        assert!(same_stats(&soul_buff(Element::Infernal), &BuffV1::named("x")));
        assert_eq!(soul_name(Element::Hextech), "league_dragons_soul_hextech");
    }

    #[test]
    fn soul_and_elder_numbers() {
        assert_eq!(infernal_soul_damage(200, 100), 100 + 50 + 15);
        assert_eq!(mountain_soul_shield(200, 100, 2000), 200 + 30 + 10 + 160);
        assert_eq!(ocean_soul_heal(200, 100, 2000), 160 + 60 + 20 + 160);
        assert_eq!(hextech_soul_damage(200, 100), 40 + 60 + 20);
        assert_eq!(burn_total(300), 80);
        assert!(chem_low(499, 1000) && !chem_low(500, 1000) && !chem_low(0, 0));
        assert_eq!(hex_slow().move_speed_mult, -90);
        assert_eq!(cloud_haste().duration_tick, 360);
        let b = baron_buff(7200);
        assert_eq!((b.attack_mult, b.magic_power_mult, b.duration_tick), (20, 20, 7200));
        let m = minion_boost();
        assert_eq!((m.damaged_reduce, m.attack_mult, m.duration_tick), (40, 30, 45));
    }

    #[test]
    fn the_execute_is_below_a_fifth() {
        assert!(executable(199, 1000));
        assert!(!executable(200, 1000), "exactly 20% is not below it");
        assert!(!executable(201, 1000));
        assert!(executable(1, 1000));
        assert!(!executable(0, 1000), "dead already");
        assert!(!executable(5, 0));
        // through a shield and 75% damage reduction
        let d = execute_damage(150, 300, 1000);
        assert!(d / 4 >= 150 + 300 && d == 2800);
    }

    #[test]
    fn the_record_reads_back_and_fits() {
        let r = Record {
            tick: 0x1_2345,
            cur: 7,
            order: [3, 4, 1],
            stacks: [[4, 0, 1, 0, 0, 0], [0, 0, 0, 2, 0, 0]],
            soul: Some((0, 1)),
            elder: Some(HoldRec { team: 1, lanes: 0b10110, until: 0xa_bcde }),
            baron: None,
            conflict: false,
            serpen_alive: true,
            epic_alive: false,
            seq: 0x2f,
        };
        let name = r.name();
        // version 1 | tick 12345 | cur 7 | order 341 | blue 401000 | red 000200 | soul 01 | elder 1 16 abcde |
        // baron 2 00 00000 | flags 2 | seq 2f
        assert_eq!(name, "league_dragons_st:112345734140100000020001116abcde2000000022f");
        assert_eq!(name.len(), ST.len() + ST_LEN);
        assert!(name.len() <= BUFF_NAME_CAP && !name.contains("_sim:"));
        assert_eq!(Record::parse(&name), Some(r));
        // a conflict record
        let c = Record { conflict: true, cur: 2, order: [2, 5, 6], ..Record::default() };
        assert_eq!(Record::parse(&c.name()), Some(c));
        // a tick past five hex digits is clamped, not cut into the next field
        let big = Record { tick: 0x12_3456, ..Record::default() };
        assert_eq!(Record::parse(&big.name()).map(|r| r.tick), Some(0xf_ffff));
        assert!(Record::parse("league_dragons_st:2123").is_none());
        assert!(Record::parse("league_eggs_sim:3").is_none());
    }

    #[test]
    fn events_read_back() {
        let all = [
            Ev::DrakeSpawn { element: Element::Hextech },
            Ev::ElderSpawn,
            Ev::Drake { team: 1, element: Element::Ocean, total: 3 },
            Ev::Soul { team: 0, element: Element::Infernal },
            Ev::ElderKilled { team: 1, lanes: 0b11011 },
            Ev::Execute { team: 0, lane: 3, victim_lane: 2 },
            Ev::BaronKilled { team: 0, lanes: 0b11111 },
            Ev::Conflict,
        ];
        for (i, ev) in all.iter().enumerate() {
            let seq = (i as u8).wrapping_add(250);
            let name = event_name(seq, 0x3_4f00, ev);
            assert!(name.len() <= BUFF_NAME_CAP && !name.contains("_sim:"), "{name}");
            assert_eq!(parse_event(&name), Some((seq, 0x3_4f00, *ev)), "{name}");
        }
        assert_eq!(event_name(3, 0xa3f, &Ev::Drake { team: 0, element: Element::Infernal, total: 2 }),
                   "league_dragons_ev:0300a3fD012");
        assert!(parse_event("league_dragons_ev:0300a3fZ").is_none());
        assert_eq!(marker(Element::Elder), "league_dragons_el_elder");
    }

    #[test]
    fn the_workshop_mods_records_are_told_apart() {
        for n in ["sed_timer1:3840:8ca0:3840:4650:f", "sed_env_site:0:2af80:90880:j", "sed1:0:1:1:1:3a98:2:0", "sed_c:6b4:2d78:0",
                  "sed_state1:5"] {
            assert!(workshop_record(n), "{n}");
        }
        for n in ["seduce", "serpen_permanent_buff", "league_dragons_st:1", "tfm2_b2:0:0:0", "sed"] {
            assert!(!workshop_record(n), "{n}");
        }
    }

    #[test]
    fn names_fit() {
        for e in DRAKES.iter().chain([Element::Elder].iter()) {
            for n in [drake_name(*e), soul_name(*e), marker(*e)] {
                assert!(n.len() <= BUFF_NAME_CAP && !n.contains("_sim:"), "{n}");
            }
        }
        for n in [NAT, ELDER, BURN, EXECUTED, BARON, MINION_BOOST, CLOUD_HASTE, HEX_SLOW, CHEM_LOW] {
            assert!(n.starts_with("league_dragons_") && n.len() <= BUFF_NAME_CAP, "{n}");
        }
        // the soul's marker prefix catches no transient buff (lib.rs takes off what it no longer wants by prefix)
        for n in [CLOUD_HASTE, CHEM_LOW, HEX_SLOW, BURN, EXECUTED, MINION_BOOST] {
            assert!(!n.starts_with(SOUL) && !n.starts_with(DK), "{n}");
        }
    }
}
