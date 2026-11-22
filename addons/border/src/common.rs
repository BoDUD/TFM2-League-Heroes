//! 三个英雄共用的小件：读数据给的参数、几何、找单位、看 buff 和控制、配音的节奏。
//!
//! 记住的东西都在每个英雄被动的实例里（每场模拟一份），原生效果自己什么都不记，要的状态从单位身上的 buff 读：游戏会同时
//! 跑好几场模拟（预演），全局变量是共用的。只有参数（每场都一样）放在全局里。

use std::collections::HashMap;

use mod_api_stable::*;

pub const SECOND: usize = 60;

pub type Pt = (f64, f64);

/// 数据 `passive.params` 的 JSON（键排好序、值都是整数，`{"a":1,"b":2}`）-> 键值表。
pub fn parse_params(json: &str) -> HashMap<String, i64> {
    let mut out = HashMap::new();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        if let Ok(v) = v.trim().parse::<i64>() {
            out.insert(k.to_string(), v);
        }
    }
    out
}

/// 参数表里的一个数，没有就用默认的，负数当 0。
pub fn get(m: &HashMap<String, i64>, k: &str, default: usize) -> usize {
    m.get(k).map_or(default, |&v| v.max(0) as usize)
}

/// 一个英雄 border.dll 用的参数：默认值就是 tools/kit/build_<hero>.py 的 P（单元测试和生成的 .data_champion 对过），
/// 他的被动出生时用数据里的 `passive.params` 盖掉（configure）。放在全局里：每场模拟的数一样，原生效果没有被动实例也读得到
/// （佛耶戈附身、妮蔻变身时都用它）。
pub struct Params {
    keys: &'static [(&'static str, usize)],
    live: std::sync::RwLock<Option<Vec<usize>>>,
}

impl Params {
    pub const fn new(keys: &'static [(&'static str, usize)]) -> Self {
        Self { keys, live: std::sync::RwLock::new(None) }
    }

    pub fn get(&self, k: &str) -> usize {
        let Some(i) = self.keys.iter().position(|(n, _)| *n == k) else {
            debug_assert!(false, "unknown parameter {k}");
            return 0;
        };
        let live = self.live.read().unwrap_or_else(|e| e.into_inner());
        live.as_ref().map_or(self.keys[i].1, |v| v[i])
    }

    pub fn f(&self, k: &str) -> f64 {
        self.get(k) as f64
    }

    pub fn configure(&self, json: &str) {
        let m = parse_params(json);
        let v = self.keys.iter().map(|(k, d)| get(&m, k, *d)).collect();
        *self.live.write().unwrap_or_else(|e| e.into_inner()) = Some(v);
    }

    pub fn keys(&self) -> &'static [(&'static str, usize)] {
        self.keys
    }
}

/// 单元测试：生成的 .data_champion 里 passive.params 和 Params 的默认值一个不差。
#[cfg(test)]
pub fn check_kit_params(id: &str, table: &Params) {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../border/champion").join(format!("{id}.data_champion"));
    let text = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{}: {e}", path.display()));
    let at = text.find("\"params\"").expect("the kit has passive params");
    let open = at + text[at..].find('{').unwrap();
    let close = open + text[open..].find('}').unwrap();
    let m = parse_params(&text[open..=close]);
    let mut kit: Vec<(String, i64)> = m.into_iter().collect();
    kit.sort();
    let mut ours: Vec<(String, i64)> = table.keys().iter().map(|(k, v)| (k.to_string(), *v as i64)).collect();
    ours.sort();
    assert_eq!(kit, ours, "{id}: border.dll's defaults and the kit's passive.params differ - rerun tools/kit/build_<hero>.py or fix the table");
}

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 单位向量；太短的返回 None。
pub fn unit(v: Pt) -> Option<Pt> {
    let d = (v.0 * v.0 + v.1 * v.1).sqrt();
    (d >= 1.0).then(|| (v.0 / d, v.1 / d))
}

/// `to` 在不在从 `from` 朝 `dir`（单位向量）的扇形里：半径 `radius`（加上对方的身子 `body`），左右各 acos(cos_milli / 1000)。
/// 贴身的（离得比 `body` + 5000 还近）算在里面：贴在身上的人哪个方向都扫得到。
pub fn in_cone(from: Pt, dir: Pt, to: Pt, radius: f64, cos_milli: f64, body: f64) -> bool {
    let v = (to.0 - from.0, to.1 - from.1);
    let d = (v.0 * v.0 + v.1 * v.1).sqrt();
    if d > radius + body {
        return false;
    }
    if d <= body + 5_000.0 {
        return true;
    }
    (v.0 * dir.0 + v.1 * dir.1) / d >= cos_milli / 1000.0
}

pub fn pos_of(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

pub fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

pub fn team_of(sim: &StableSim<'_>, id: usize) -> Option<usize> {
    sim.get_entity(id).map(|e| e.team())
}

/// 生命比例（0..1），读不到当满血。
pub fn hp_ratio(sim: &StableSim<'_>, id: usize) -> f64 {
    sim.get_entity(id).map_or(1.0, |e| {
        let (now, max) = e.hp();
        if max == 0 {
            1.0
        } else {
            now as f64 / max as f64
        }
    })
}

/// 场上的英雄（活的死的都有）。
pub fn champions(sim: &StableSim<'_>) -> Vec<usize> {
    (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).filter(|&id| id != usize::MAX).collect()
}

/// 活着、选得中的英雄，按队伍挑：`same` 为 true 是和 `team` 同队的。
pub fn live_champions(sim: &StableSim<'_>, team: usize, same: bool) -> Vec<usize> {
    champions(sim)
        .into_iter()
        .filter(|&id| {
            sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable() && (e.team() == team) == same)
        })
        .collect()
}

/// 这一下能打的敌方单位：活着、选得中、不是塔也不是水晶（技能的 EnemyWithoutTower）。
pub fn hittable_enemy(sim: &StableSim<'_>, my_team: usize, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        e.is_alive()
            && e.is_targetable()
            && e.team() != my_team
            && !e.is_tower()
            && !matches!(e.kind(), Some(EntityKindV1::Tower) | Some(EntityKindV1::Nexus))
    })
}

/// 场上所有单位的 id（小兵、野怪、召唤物都在里面）。
pub fn all_units(sim: &StableSim<'_>) -> Vec<usize> {
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i).map(|e| e.id())).filter(|&id| id != usize::MAX).collect()
}

pub fn buffs_of(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    let Some(e) = sim.get_entity(id) else { return Vec::new() };
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect()
}

pub fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buffs_of(sim, id).iter().any(|b| b.name() == name)
}

pub fn count_buff(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    buffs_of(sim, id).iter().filter(|b| b.name() == name).count()
}

/// 身上有不受控制的 buff（数据的 cc_immune）。
pub fn cc_immune(sim: &StableSim<'_>, id: usize) -> bool {
    buffs_of(sim, id).iter().any(|b| b.cc_immune)
}

pub fn ccs_of(sim: &StableSim<'_>, id: usize) -> Vec<CcV1> {
    let Some(e) = sim.get_entity(id) else { return Vec::new() };
    (0..e.cc_count()).filter_map(|i| e.cc_at(i)).collect()
}

/// 被控住、出不了手（定身还能射，不算；被强制位移算）。
pub fn held(sim: &StableSim<'_>, id: usize) -> bool {
    ccs_of(sim, id).iter().any(|c| {
        matches!(CcKindV1::from_code(c.kind), Some(CcKindV1::Stun | CcKindV1::Airborne | CcKindV1::Taunt
            | CcKindV1::Fear | CcKindV1::Charm | CcKindV1::ForceMove))
    })
}

/// 被控着（给灯弥、岑垒挑队友时算威胁）：眩晕、击飞、定身、嘲讽、恐惧、魅惑、被推被拉。
pub fn controlled(sim: &StableSim<'_>, id: usize) -> bool {
    ccs_of(sim, id).iter().any(|c| {
        matches!(CcKindV1::from_code(c.kind), Some(CcKindV1::Stun | CcKindV1::Airborne | CcKindV1::Bind
            | CcKindV1::Taunt | CcKindV1::Fear | CcKindV1::Charm | CcKindV1::ForceMove))
    })
}

/// 正在放技能：施法的动作还在播（引擎给施法的人挂一个 `Animation` 控制，名字是动作的标签；league_ai_watch 这样认），
/// 普攻的不算。
pub fn casting(sim: &StableSim<'_>, id: usize) -> bool {
    ccs_of(sim, id).iter().any(|c| {
        CcKindV1::from_code(c.kind) == Some(CcKindV1::Animation) && is_spell_anim(c.name())
    })
}

/// 施法动作的标签：普攻（attack、attack_xxx、a_xxx）、站、走、挨打、倒下以外的都算。
pub fn is_spell_anim(name: &str) -> bool {
    let n = name.trim();
    !(n.is_empty()
        || n.starts_with("attack")
        || n.starts_with("a_")
        || matches!(n, "idle" | "run" | "hit" | "dead"))
}

/// 刚进冷却的技能（技能、技能 2、大招）：剩下的冷却离满的不到 `within` 拍，就是刚放的（`casting` 的后备）。
pub fn just_cast(sim: &StableSim<'_>, id: usize, within: usize) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].iter().any(|&s| {
        e.cooldown(s).is_some_and(|c| c.cooltime > within && c.remaining > 0 && c.cooltime - c.remaining.min(c.cooltime) < within)
    })
}

/// 这一下的伤害按攻击力、法强、最大生命的比例算：flat + ad% 攻击力 + ap% 法强 + hp% 最大生命。
pub fn amount(sim: &StableSim<'_>, id: usize, flat: usize, ad: usize, ap: usize, hp: usize) -> usize {
    let Some(e) = sim.get_entity(id) else { return flat };
    let s = e.stat();
    let max = e.hp().1;
    flat + s.attack * ad / 100 + s.magic_power * ap / 100 + max * hp / 100
}

pub fn slow_buff(name: &str, pct: usize, ticks: usize) -> BuffV1 {
    let mut b = BuffV1::timed(name, ticks);
    b.move_speed_mult = -(pct.min(95) as i32);
    b
}

/// 眩晕，对方不受控制时不给。返回给没给。
pub fn stun(sim: &mut StableSim<'_>, id: usize, ticks: usize) -> bool {
    if ticks == 0 || cc_immune(sim, id) {
        return false;
    }
    sim.apply_cc(id, &CcV1::stun(ticks as u64));
    true
}

/// 把一个名字的 buff 补到 `want` 层：多了全拿掉重挂，少了补上。`make` 给一层的样子。
pub fn set_stacks(sim: &mut StableSim<'_>, id: usize, name: &str, want: usize, make: impl Fn() -> BuffV1) {
    let have = count_buff(sim, id, name);
    if have == want {
        return;
    }
    if have > want {
        sim.entity_remove_buff(id, name);
        for _ in 0..want {
            sim.add_buff(id, &make());
        }
    } else {
        for _ in have..want {
            sim.add_buff(id, &make());
        }
    }
}

// ===================== 写进 buff 名字的坐标、线段 =====================

/// 方向的一个分量（-1..1）编成 0..2000 的整数（buff 名字里只放非负整数）。
pub fn enc_dir(v: f64) -> u64 {
    ((v.clamp(-1.0, 1.0) * 1000.0).round() as i64 + 1000) as u64
}

pub fn dec_dir(v: u64) -> f64 {
    (v as f64 - 1000.0) / 1000.0
}

/// `<prefix><x>_<y>`：一个点。
pub fn pt_name(prefix: &str, p: Pt) -> String {
    format!("{prefix}{}_{}", p.0.max(0.0).round() as u64, p.1.max(0.0).round() as u64)
}

/// 名字里 prefix 后面那串 `_` 隔开的整数。
pub fn parse_nums(prefix: &str, name: &str) -> Option<Vec<u64>> {
    name.strip_prefix(prefix)?.split('_').map(|s| s.parse::<u64>().ok()).collect()
}

pub fn parse_pt(prefix: &str, name: &str) -> Option<Pt> {
    let v = parse_nums(prefix, name)?;
    (v.len() == 2).then(|| (v[0] as f64, v[1] as f64))
}

/// 身上名字以 prefix 开头、后面是 `n` 个整数的 buff（按挂上的先后）。
pub fn named(sim: &StableSim<'_>, id: usize, prefix: &str, n: usize) -> Vec<(String, Vec<u64>)> {
    buffs_of(sim, id)
        .iter()
        .filter_map(|b| parse_nums(prefix, b.name()).filter(|v| v.len() == n).map(|v| (b.name().to_string(), v)))
        .collect()
}

/// 摘掉这些带数的 buff（别的同前缀的不动）。
pub fn clear_named(sim: &mut StableSim<'_>, id: usize, prefix: &str, n: usize) {
    for (name, _) in named(sim, id, prefix, n) {
        sim.entity_remove_buff(id, &name);
    }
}

/// 地上的一条线段：中点 `c`、单位方向 `d`（线段顺着 d），名字 `<prefix><cx>_<cy>_<dx>_<dy>`。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Seg {
    pub c: Pt,
    pub d: Pt,
}

impl Seg {
    pub fn name(&self, prefix: &str) -> String {
        format!("{prefix}{}_{}_{}_{}", self.c.0.max(0.0).round() as u64, self.c.1.max(0.0).round() as u64,
                enc_dir(self.d.0), enc_dir(self.d.1))
    }

    pub fn parse(prefix: &str, name: &str) -> Option<Seg> {
        let v = parse_nums(prefix, name)?;
        if v.len() != 4 {
            return None;
        }
        Some(Seg { c: (v[0] as f64, v[1] as f64), d: unit((dec_dir(v[2]), dec_dir(v[3])))? })
    }

    /// 顺着线段离中点多远（带正负）。
    pub fn along(&self, p: Pt) -> f64 {
        (p.0 - self.c.0) * self.d.0 + (p.1 - self.c.1) * self.d.1
    }

    /// 离线段所在直线多远（带正负：在哪一边）。
    pub fn across(&self, p: Pt) -> f64 {
        -(p.0 - self.c.0) * self.d.1 + (p.1 - self.c.1) * self.d.0
    }
}

/// 一个几乎不动、什么都不打的直线弹道当画面（往 `dir` 一拍挪 PICTURE_DRIFT，活 `ticks` 拍）：引擎把弹道的画面转到它走的方向。
pub const PICTURE_DRIFT: f64 = 20.0;

pub fn picture(sim: &mut StableSim<'_>, caster: usize, view: &str, noop: &str, at: Pt, dir: Pt, ticks: usize) -> bool {
    let Some(team) = team_of(sim, caster) else { return false };
    let to = (at.0 + dir.0 * PICTURE_DRIFT * ticks as f64, at.1 + dir.1 * PICTURE_DRIFT * ticks as f64);
    let spec = ProjectileSpawnV1 {
        caster_id: caster,
        team,
        x: at.0.max(0.0) as u64,
        y: at.1.max(0.0) as u64,
        radius: 1,
        speed: PICTURE_DRIFT as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: to.0.max(0.0) as u64,
        target_y: to.1.max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(view, noop, &spec)
}

/// 朝左的弹道画面要换上下翻过的那张（`_l`）。
pub fn lr(base: &str, dir: Pt) -> String {
    format!("{base}{}", if dir.0 < -1e-6 { "_l" } else { "_r" })
}

/// 强制位移：朝 `to` 挪过去（最多 `max_ticks` 拍、每拍至少 `speed`）。返回挪了几拍（太近不挪返回 0）。
pub fn force_move(sim: &mut StableSim<'_>, id: usize, from: Pt, to: Pt, speed: f64, max_ticks: usize) -> u64 {
    let d = dist(from, to);
    if d < 1_000.0 || speed <= 0.0 {
        return 0;
    }
    let ticks = (d / speed).ceil().clamp(1.0, max_ticks.max(1) as f64) as u64;
    let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks);
    mv.dx = (to.0 - from.0).round() as i64;
    mv.dy = (to.1 - from.1).round() as i64;
    mv.speed = (d / ticks as f64).ceil() as u64;
    sim.apply_cc(id, &mv);
    ticks
}

/// 摆着某个动作的姿势 `ticks` 拍（强制位移会把动作换掉）。
pub fn hold_pose(sim: &mut StableSim<'_>, id: usize, tag: &str, ticks: usize) {
    let mut pose = CcV1::of_kind(CcKindV1::Animation, ticks as u64);
    pose.set_name(tag);
    sim.apply_cc(id, &pose);
}

/// 输入里的目标单位（Targeting 的施法）。
pub fn target_of(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

/// 身子半径（读不到算 10000）。
pub fn body_of(sim: &StableSim<'_>, id: usize) -> f64 {
    sim.get_entity(id).map_or(10_000.0, |e| e.radius().max(1) as f64)
}

/// `center` 身边 `radius` 内能打的敌人（不算塔）。
pub fn enemies_near(sim: &StableSim<'_>, team: usize, center: Pt, radius: f64) -> Vec<usize> {
    all_units(sim)
        .into_iter()
        .filter(|&id| hittable_enemy(sim, team, id) && pos_of(sim, id).is_some_and(|p| dist(center, p) <= radius))
        .collect()
}

// ===================== 配音 =====================

/// Codex 每人九句：选人、普攻、走路、挨打、技能、技能 2、大招、倒下、胜利。事件 `<id>_v_<x>` 放片段 `<id>_vo_<x>`。
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Cue {
    /// 一局开始（第一条命出来两秒后），一局一次
    Pick,
    /// 普攻打到敌方英雄
    Attack,
    /// 走远路（身边没有敌方英雄、走了几秒）
    Move,
    /// 一下挨掉一大截
    Hit,
    Skill,
    Skill2,
    Ult,
    /// 倒下：每次都说
    Dead,
    /// 杀了敌方英雄
    Win,
}

impl Cue {
    pub fn line(self) -> &'static str {
        match self {
            Cue::Pick => "v_pick",
            Cue::Attack => "v_attack",
            Cue::Move => "v_move",
            Cue::Hit => "v_hit",
            Cue::Skill => "v_skill",
            Cue::Skill2 => "v_skill2",
            Cue::Ult => "v_ult",
            Cue::Dead => "v_dead",
            Cue::Win => "v_win",
        }
    }

    /// 同一句再说要隔多久。
    pub fn cooldown(self) -> usize {
        match self {
            Cue::Pick => usize::MAX,
            Cue::Attack => 30 * SECOND,
            Cue::Move => 60 * SECOND,
            Cue::Hit => 25 * SECOND,
            Cue::Skill | Cue::Skill2 => 20 * SECOND,
            Cue::Ult | Cue::Dead => 0,
            Cue::Win => 30 * SECOND,
        }
    }

    /// 大招和倒下不等别的句子说完多久（只隔一秒，免得叠在一起）。
    fn urgent(self) -> bool {
        matches!(self, Cue::Ult | Cue::Dead)
    }
}

pub const ALL_CUES: [Cue; 9] =
    [Cue::Pick, Cue::Attack, Cue::Move, Cue::Hit, Cue::Skill, Cue::Skill2, Cue::Ult, Cue::Dead, Cue::Win];

/// 任意两句之间至少隔这么久（大招、倒下只隔 URGENT_GAP）。
pub const VOICE_GAP: usize = 6 * SECOND;
pub const URGENT_GAP: usize = SECOND;

/// 一份模拟里的配音节奏。
#[derive(Clone, Debug, Default)]
pub struct Voice {
    last_any: Option<usize>,
    last: HashMap<Cue, usize>,
}

impl Voice {
    /// 现在能不能说这一句，能就记下来。
    pub fn pick(&mut self, cue: Cue, tick: usize) -> bool {
        let gap = if cue.urgent() { URGENT_GAP } else { VOICE_GAP };
        if self.last_any.is_some_and(|t| tick < t + gap) {
            return false;
        }
        if let Some(&t) = self.last.get(&cue) {
            if cue == Cue::Pick || tick < t.saturating_add(cue.cooldown()) {
                return false;
            }
        }
        self.last.insert(cue, tick);
        self.last_any = Some(tick);
        true
    }
}

/// 一个英雄这一拍的配音小账：上一拍三个技能的冷却（认出刚放的）、走了多久、出生几次。
#[derive(Clone, Debug, Default)]
pub struct Chatter {
    pub voice: Voice,
    cds: [usize; 3],
    walked: usize,
    last_pos: Option<Pt>,
    pub lives: usize,
    pub was_alive: bool,
    picked: bool,
    /// 这条命的第一拍：只记下技能的冷却，不当成刚放了（复活时技能可能还在冷却）
    fresh: bool,
    last_flinch: Option<usize>,
}

impl Chatter {
    pub fn say(&mut self, sim: &mut StableSim<'_>, id: &str, me: usize, cue: Cue) -> bool {
        if !self.voice.pick(cue, sim.tick()) {
            return false;
        }
        sim.play_sfx(&format!("{id}_{}", cue.line()), me, &InputTargetV1::target(me));
        true
    }

    /// 每拍：复活了没有、刚放了哪个技能、在不在赶路。活着才调。
    pub fn tick(&mut self, sim: &mut StableSim<'_>, id: &str, player: usize, me: usize) {
        let tick = sim.tick();
        if !self.picked && self.lives >= 1 && tick >= 2 * SECOND {
            self.picked = true;
            self.say(sim, id, me, Cue::Pick);
        }
        let cds = sim.get_player(player).and_then(|p| p.cooldowns()).map_or((0, 0, 0, 0), |c| c);
        let now = [cds.1, cds.2, cds.3];
        if !std::mem::take(&mut self.fresh) {
            for (slot, cue) in [(0, Cue::Skill), (1, Cue::Skill2), (2, Cue::Ult)] {
                if now[slot] > self.cds[slot] + 30 {
                    self.say(sim, id, me, cue);
                }
            }
        }
        self.cds = now;
        // 赶路：一拍挪 300 以上算在走，身边 70000 内没有敌方英雄，连着走 3 秒
        let at = pos_of(sim, me);
        let step = match (self.last_pos, at) {
            (Some(a), Some(b)) => dist(a, b),
            _ => 0.0,
        };
        self.last_pos = at;
        let team = team_of(sim, me).unwrap_or(0);
        let calm = at.is_some_and(|p| {
            live_champions(sim, team, false).iter().all(|&e| pos_of(sim, e).is_none_or(|q| dist(p, q) > 70_000.0))
        });
        if (300.0..6_000.0).contains(&step) && calm {
            self.walked += 1;
            if self.walked >= 3 * SECOND {
                self.walked = 0;
                self.say(sim, id, me, Cue::Move);
            }
        } else {
            self.walked = 0;
        }
    }

    /// 出生（复活是新单位）：记一条命。
    pub fn spawned(&mut self) {
        self.was_alive = false;
        self.last_pos = None;
    }

    /// 活着的这一拍：前一拍还死着就是新的一条命。返回这一拍活着没有。
    pub fn alive_now(&mut self, sim: &StableSim<'_>, me: usize) -> bool {
        let a = alive(sim, me);
        if a && !self.was_alive {
            self.lives += 1;
            self.fresh = true;
        }
        self.was_alive = a;
        a
    }

    pub fn attacked(&mut self, sim: &mut StableSim<'_>, id: &str, me: usize, target: usize) {
        let mine = team_of(sim, me);
        if sim.get_entity(target).is_some_and(|t| t.is_champion() && Some(t.team()) != mine) {
            self.say(sim, id, me, Cue::Attack);
        }
    }

    pub fn damaged(&mut self, sim: &mut StableSim<'_>, id: &str, me: usize, damage: usize) {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        if max > 0 && damage * 100 >= max * 8 {
            self.say(sim, id, me, Cue::Hit);
        }
    }

    /// 挨了一大下（最大生命的 5% 以上）身上冒一下受击特效 `<id>_hit`，每秒最多一次。
    pub fn flinch(&mut self, sim: &mut StableSim<'_>, id: &str, me: usize, damage: usize) {
        let tick = sim.tick();
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        if max == 0 || damage * 100 < max * 5 || self.last_flinch.is_some_and(|t| tick < t + SECOND) {
            return;
        }
        self.last_flinch = Some(tick);
        sim.play_view_effect(&format!("{id}_hit"), me, &InputTargetV1::target(me), 0, 0, 0);
    }

    pub fn killed(&mut self, sim: &mut StableSim<'_>, id: &str, me: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.say(sim, id, me, Cue::Win);
        }
    }

    pub fn died(&mut self, sim: &mut StableSim<'_>, id: &str, me: usize) {
        self.was_alive = false;
        self.say(sim, id, me, Cue::Dead);
    }
}

// ===================== 日志 =====================

/// 一个英雄的日志条数：前 `first` 条都记，之后每 `every` 条记一条。
pub struct Counter {
    n: std::sync::atomic::AtomicUsize,
}

impl Counter {
    pub const fn new() -> Self {
        Self { n: std::sync::atomic::AtomicUsize::new(0) }
    }

    pub fn next(&self) -> Option<usize> {
        let n = self.n.fetch_add(1, std::sync::atomic::Ordering::Relaxed) + 1;
        (n <= 80 || n % 200 == 0).then_some(n)
    }
}

impl Default for Counter {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_read_like_the_kit_writes_them() {
        let m = parse_params(r#"{"e_hits": 2, "p_cap": 25, "q_cos": 570}"#);
        assert_eq!(get(&m, "e_hits", 0), 2);
        assert_eq!(get(&m, "p_cap", 0), 25);
        assert_eq!(get(&m, "nope", 7), 7);
        assert_eq!(get(&parse_params(r#"{"x": -3}"#), "x", 9), 0);
    }

    #[test]
    fn cone_takes_the_front_and_the_point_blank() {
        let me = (0.0, 0.0);
        let right = (1.0, 0.0);
        // 正前方、半径内
        assert!(in_cone(me, right, (30_000.0, 0.0), 40_000.0, 570.0, 10_000.0));
        // 半径外（加上身子也不够）
        assert!(!in_cone(me, right, (51_000.0, 0.0), 40_000.0, 570.0, 10_000.0));
        // 身后
        assert!(!in_cone(me, right, (-30_000.0, 0.0), 40_000.0, 570.0, 10_000.0));
        // 贴身的哪个方向都算
        assert!(in_cone(me, right, (-12_000.0, 0.0), 40_000.0, 570.0, 10_000.0));
        // 55 度以内算、60 度以外不算（cos 0.57 约 55 度）
        let a = 50f64.to_radians();
        assert!(in_cone(me, right, (30_000.0 * a.cos(), 30_000.0 * a.sin()), 40_000.0, 570.0, 0.0));
        let b = 60f64.to_radians();
        assert!(!in_cone(me, right, (30_000.0 * b.cos(), 30_000.0 * b.sin()), 40_000.0, 570.0, 0.0));
    }

    #[test]
    fn spell_animations_are_not_attacks() {
        assert!(is_spell_anim("skill"));
        assert!(is_spell_anim("ult_cast"));
        assert!(is_spell_anim("skill2_dash"));
        assert!(!is_spell_anim("attack"));
        assert!(!is_spell_anim("attack_m"));
        assert!(!is_spell_anim("a_flash"));
        assert!(!is_spell_anim("idle"));
        assert!(!is_spell_anim(""));
    }

    #[test]
    fn lines_keep_their_distance() {
        let mut v = Voice::default();
        assert!(v.pick(Cue::Pick, 120));
        assert!(!v.pick(Cue::Pick, 120 + 100 * SECOND));
        assert!(!v.pick(Cue::Attack, 120 + VOICE_GAP - 1));
        assert!(v.pick(Cue::Attack, 120 + VOICE_GAP));
        // 同一句有自己的冷却
        assert!(!v.pick(Cue::Attack, 120 + VOICE_GAP + 10 * SECOND));
        // 大招只隔一秒
        assert!(v.pick(Cue::Ult, 120 + VOICE_GAP + URGENT_GAP));
        assert!(v.pick(Cue::Dead, 120 + VOICE_GAP + 2 * URGENT_GAP));
    }

    #[test]
    fn points_and_segments_ride_in_buff_names() {
        let n = pt_name("border_x_q_", (480_123.4, 12_000.0));
        assert_eq!(parse_pt("border_x_q_", &n), Some((480_123.0, 12_000.0)));
        assert_eq!(parse_pt("border_x_q_", "border_x_q_ms"), None);
        let s = Seg { c: (100_000.0, 200_000.0), d: unit((-3.0, 4.0)).unwrap() };
        let name = s.name("border_wuling_veil_");
        assert!(name.len() <= BUFF_NAME_CAP);
        let back = Seg::parse("border_wuling_veil_", &name).unwrap();
        assert_eq!(back.c, s.c);
        assert!((back.d.0 - s.d.0).abs() < 2e-3 && (back.d.1 - s.d.1).abs() < 2e-3);
        // 线上、两边
        let flat = Seg { c: (0.0, 0.0), d: (1.0, 0.0) };
        assert!((flat.along((5_000.0, 3_000.0)) - 5_000.0).abs() < 1e-9);
        assert!(flat.across((5_000.0, 3_000.0)) > 0.0);
        assert!(flat.across((5_000.0, -3_000.0)) < 0.0);
        assert_eq!(lr("border_x_r_wave", (-1.0, 0.0)), "border_x_r_wave_l");
        assert_eq!(lr("border_x_r_wave", (0.0, 1.0)), "border_x_r_wave_r");
    }

    #[test]
    fn every_cue_has_a_codex_line() {
        let nine = ["pick", "attack", "move", "hit", "skill", "skill2", "ult", "dead", "win"];
        let used: Vec<&str> = ALL_CUES.iter().map(|c| c.line().trim_start_matches("v_")).collect();
        assert_eq!(used, nine);
    }
}
