//! 画面上的字（简体、繁体、英文）：公告的标题和第二行、HUD 的标签。纯函数，单元测试在这里。
//!
//! 数字都从 `rules.rs` 来（每层的数值从 `rules::drake_buff` 读），玩法改了数，字跟着变。元素的中文名是英雄联盟国服的叫法
//! （`rules::Element::zh`），繁体是台服的写法，英文是英雄联盟的。队伍照用户给的样子叫「蓝色方」「红色方」。

use super::feed::What;
use super::rules::{self, Element};

/// 游戏的语言：简体、繁体，其他语言都用英文（league_eggs notice.rs 的做法）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Lang {
    Hans,
    Hant,
    En,
}

/// 认游戏的语言。先看本包改过的纳什男爵的名字（`asset/base/text/object?epic.name`：纳什男爵 / 巴龍 / Baron Nashor），
/// 认不出（别的语言、本包的文字没装上）再按阿克尚第一个技能名的写法（league_eggs、league_akshan 的做法）。
pub fn lang_of(baron: &str, skill1: &str) -> Lang {
    if baron.contains("纳什男爵") {
        return Lang::Hans;
    }
    if baron.contains("巴龍") {
        return Lang::Hant;
    }
    if baron.contains("Baron Nashor") {
        return Lang::En;
    }
    let has = |lo: u32, hi: u32| skill1.chars().any(|c| (lo..=hi).contains(&(c as u32)));
    if has(0xac00, 0xd7a3) || has(0x3040, 0x30ff) {
        Lang::En
    } else if skill1.contains('復') || skill1.contains('還') {
        Lang::Hant
    } else if has(0x4e00, 0x9fff) {
        Lang::Hans
    } else {
        Lang::En
    }
}

fn pick<T>(lang: Lang, hans: T, hant: T, en: T) -> T {
    match lang {
        Lang::Hans => hans,
        Lang::Hant => hant,
        Lang::En => en,
    }
}

/// 元素的名字：炼狱 / 煉獄 / Infernal。
pub fn element(lang: Lang, e: Element) -> &'static str {
    match lang {
        Lang::Hans => e.zh(),
        Lang::Hant => match e {
            Element::Infernal => "煉獄",
            Element::Mountain => "山脈",
            Element::Ocean => "海洋",
            Element::Cloud => "雲端",
            Element::Hextech => "海克斯",
            Element::Chemtech => "化學科技",
            Element::Elder => "遠古",
        },
        Lang::En => match e {
            Element::Infernal => "Infernal",
            Element::Mountain => "Mountain",
            Element::Ocean => "Ocean",
            Element::Cloud => "Cloud",
            Element::Hextech => "Hextech",
            Element::Chemtech => "Chemtech",
            Element::Elder => "Elder",
        },
    }
}

/// 这条龙的名字：炼狱亚龙 / 煉獄亞龍 / Infernal Drake；远古巨龙 / 遠古巨龍 / Elder Dragon。
pub fn drake(lang: Lang, e: Element) -> String {
    if e == Element::Elder {
        return pick(lang, "远古巨龙", "遠古巨龍", "Elder Dragon").to_string();
    }
    let n = element(lang, e);
    pick(lang, format!("{n}亚龙"), format!("{n}亞龍"), format!("{n} Drake"))
}

/// 龙魂：炼狱龙魂 / 煉獄龍魂 / Infernal Soul。
pub fn soul(lang: Lang, e: Element) -> String {
    let n = element(lang, e);
    pick(lang, format!("{n}龙魂"), format!("{n}龍魂"), format!("{n} Soul"))
}

/// 队伍（0 蓝、1 红）：蓝色方 / 藍色方 / Blue Team。
pub fn team(lang: Lang, t: usize) -> &'static str {
    let blue = t == 0;
    match lang {
        Lang::Hans => if blue { "蓝色方" } else { "红色方" },
        Lang::Hant => if blue { "藍色方" } else { "紅色方" },
        Lang::En => if blue { "Blue Team" } else { "Red Team" },
    }
}

/// HUD 每一行开头的队伍小标：蓝 / 藍 / BLUE。
pub fn team_tag(lang: Lang, t: usize) -> &'static str {
    let blue = t == 0;
    match lang {
        Lang::Hans => if blue { "蓝" } else { "红" },
        Lang::Hant => if blue { "藍" } else { "紅" },
        Lang::En => if blue { "BLUE" } else { "RED" },
    }
}

/// 元素圆点里的字（玩家的叫法：火龙、土龙、水龙、风龙、海克斯龙、化学龙；远古）。
pub fn glyph(lang: Lang, e: Element) -> &'static str {
    match (lang, e) {
        (Lang::En, Element::Infernal) => "In",
        (Lang::En, Element::Mountain) => "Mt",
        (Lang::En, Element::Ocean) => "Oc",
        (Lang::En, Element::Cloud) => "Cl",
        (Lang::En, Element::Hextech) => "Hx",
        (Lang::En, Element::Chemtech) => "Ch",
        (Lang::En, Element::Elder) => "El",
        (_, Element::Infernal) => "火",
        (_, Element::Mountain) => "土",
        (_, Element::Ocean) => "水",
        (Lang::Hans, Element::Cloud) => "风",
        (_, Element::Cloud) => "風",
        (_, Element::Hextech) => "海",
        (_, Element::Chemtech) => "化",
        (_, Element::Elder) => "古",
    }
}

/// tick 写成秒：300 -> "5"，150 -> "2.5"。
pub fn secs(ticks: usize) -> String {
    if ticks % 60 == 0 {
        (ticks / 60).to_string()
    } else {
        let tenths = (ticks * 10 + 30) / 60;
        format!("{}.{}", tenths / 10, tenths % 10)
    }
}

/// 倒计时：秒 -> "1:05"。
pub fn clock(secs: usize) -> String {
    format!("{}:{:02}", secs / 60, secs % 60)
}

/// 海克斯每层的「技能冷却 -x%」：`skill_cooldown_mult` 9 把冷却封顶在 100 / 109（92%）-> 8（四舍五入）。
pub fn hextech_cd_pct() -> i32 {
    let cd = rules::HEXTECH_CD;
    (100 * cd + (100 + cd) / 2) / (100 + cd)
}

/// 每拿一条这种元素亚龙全队多的（数字从 `rules::drake_buff` 读）。
pub fn stack_effect(lang: Lang, e: Element) -> String {
    let b = rules::drake_buff(e, 1);
    match e {
        Element::Infernal => {
            let p = b.attack_mult;
            pick(lang, format!("攻击力、法强 +{p}%"), format!("攻擊力、法強 +{p}%"),
                 format!("+{p}% attack damage and ability power"))
        }
        Element::Mountain => {
            let p = b.defence_mult;
            pick(lang, format!("护甲、魔抗 +{p}%"), format!("護甲、魔抗 +{p}%"), format!("+{p}% armor and magic resist"))
        }
        Element::Ocean => {
            let (s, p) = (secs(rules::OCEAN_EVERY), rules::OCEAN_PCT);
            pick(lang, format!("每 {s} 秒回复 {p}% 已损生命"), format!("每 {s} 秒回復 {p}% 已損生命"),
                 format!("{p}% missing health back every {s} s"))
        }
        Element::Cloud => {
            let p = b.move_speed_mult;
            pick(lang, format!("移速 +{p}%"), format!("移速 +{p}%"), format!("+{p}% move speed"))
        }
        Element::Hextech => {
            let (a, c) = (b.attack_speed_mult, hextech_cd_pct());
            pick(lang, format!("攻速 +{a}%、技能冷却 -{c}%"), format!("攻速 +{a}%、技能冷卻 -{c}%"),
                 format!("+{a}% attack speed, {c}% shorter cooldowns"))
        }
        Element::Chemtech => {
            let (t, v) = (b.toughness, b.vamp);
            pick(lang, format!("韧性 +{t}%、生命偷取 +{v}%"), format!("韌性 +{t}%、生命偷取 +{v}%"),
                 format!("+{t}% tenacity, +{v}% life steal"))
        }
        Element::Elder => String::new(),
    }
}

/// 龙魂的效果（数字从 `rules.rs` 来）。
pub fn soul_effect(lang: Lang, e: Element) -> String {
    match e {
        Element::Infernal => {
            let s = secs(rules::INFERNAL_SOUL_CD);
            pick(lang, format!("每 {s} 秒，下一次伤害敌方英雄时引发爆炸，波及他身边的敌方英雄"),
                 format!("每 {s} 秒，下一次傷害敵方英雄時引發爆炸，波及他身邊的敵方英雄"),
                 format!("every {s} s the next hit on a champion explodes, hurting the enemies around him"))
        }
        Element::Mountain => {
            let s = secs(rules::MOUNTAIN_SOUL_IDLE);
            pick(lang, format!("{s} 秒没受到伤害后获得一层护盾"), format!("{s} 秒沒受到傷害後獲得一層護盾"),
                 format!("a shield after {s} s without taking damage"))
        }
        Element::Ocean => {
            let s = secs(rules::OCEAN_SOUL_PULSES as usize * rules::OCEAN_SOUL_EVERY);
            pick(lang, format!("伤害敌方英雄后 {s} 秒内持续回复生命"), format!("傷害敵方英雄後 {s} 秒內持續回復生命"),
                 format!("hitting a champion heals over {s} s"))
        }
        Element::Cloud => {
            let (m, h, s) = (rules::CLOUD_SOUL_MS, rules::CLOUD_HASTE_MS, secs(rules::CLOUD_HASTE_T));
            pick(lang, format!("移速 +{m}%，放大招后移速再 +{h}%（{s} 秒）"),
                 format!("移速 +{m}%，放大招後移速再 +{h}%（{s} 秒）"),
                 format!("+{m}% move speed, +{h}% more for {s} s after the ultimate"))
        }
        Element::Hextech => {
            let s = secs(rules::HEXTECH_SOUL_CD);
            pick(lang, format!("每 {s} 秒，下一次命中放出连锁闪电，减速敌人"),
                 format!("每 {s} 秒，下一次命中放出連鎖閃電，減速敵人"),
                 format!("every {s} s the next hit chains lightning that slows"))
        }
        Element::Chemtech => {
            let b = rules::chem_low_buff();
            let (p, t, d, r) = (rules::CHEM_LOW_PCT, b.toughness, b.attack_mult, b.damaged_reduce);
            pick(lang, format!("生命低于 {p}% 时韧性 +{t}%、伤害 +{d}%、受到的伤害 -{r}%"),
                 format!("生命低於 {p}% 時韌性 +{t}%、傷害 +{d}%、受到的傷害 -{r}%"),
                 format!("below {p}% health: +{t}% tenacity, +{d}% damage, {r}% less damage taken"))
        }
        Element::Elder => String::new(),
    }
}

/// 拿到远古龙之力 / 纳什男爵之手的人：全队都拿到（5 个）写「全队」，一个都没有（都死着）写空。
fn holders(lang: Lang, ids: &[String], name: &dyn Fn(&str) -> String) -> String {
    if ids.len() >= 5 {
        return pick(lang, "全队", "全隊", "The whole team").to_string();
    }
    let names: Vec<String> = ids.iter().map(|x| name(x)).collect();
    names.join(pick(lang, "、", "、", ", "))
}

/// 一条公告的字：(标题, 第二行；没有第二行就是空的)。`name` 把英雄 id（`league_jinx`）换成游戏里的名字。
pub fn notice(lang: Lang, what: &What, name: &dyn Fn(&str) -> String) -> (String, String) {
    let (hans, hant, en): ((String, String), (String, String), (String, String));
    match what {
        What::DrakeSpawn { element } => {
            let e = *element;
            let fx = |l| stack_effect(l, e);
            hans = (format!("{}出现了！", drake(Lang::Hans, e)), format!("击杀后全队{}", fx(Lang::Hans)));
            hant = (format!("{}出現了！", drake(Lang::Hant, e)), format!("擊殺後全隊{}", fx(Lang::Hant)));
            en = (format!("The {} has spawned!", drake(Lang::En, e)), format!("Slay it: {} for the whole team", fx(Lang::En)));
        }
        What::ElderSpawn => {
            let p = rules::EXECUTE_PCT;
            hans = ("远古巨龙出现了！".into(), format!("击杀它的一方获得远古龙之力：点燃敌方英雄，生命低于 {p}% 时斩杀"));
            hant = ("遠古巨龍出現了！".into(), format!("擊殺牠的一方獲得遠古龍之力：點燃敵方英雄，生命低於 {p}% 時斬殺"));
            en = ("The Elder Dragon has spawned!".into(),
                  format!("Slay it for the Aspect of the Dragon: burn enemy champions, execute them below {p}% health"));
        }
        What::Drake { team: t, element, total } => {
            let (e, n) = (*element, *total);
            let soon = n + 1 == rules::SOUL_AT;
            hans = (format!("{}击杀了{}！", team(Lang::Hans, *t), drake(Lang::Hans, e)),
                    format!("全队{}（共 {n} 条{}）", stack_effect(Lang::Hans, e), if soon { "，再拿 1 条获得龙魂" } else { "" }));
            hant = (format!("{}擊殺了{}！", team(Lang::Hant, *t), drake(Lang::Hant, e)),
                    format!("全隊{}（共 {n} 隻{}）", stack_effect(Lang::Hant, e), if soon { "，再拿 1 隻獲得龍魂" } else { "" }));
            en = (format!("{} has slain the {}!", team(Lang::En, *t), drake(Lang::En, e)),
                  format!("{} for the whole team ({n} drake{}{})", stack_effect(Lang::En, e), if n == 1 { "" } else { "s" },
                          if soon { ", one more for the Dragon Soul" } else { "" }));
        }
        What::Soul { team: t, element } => {
            let e = *element;
            hans = (format!("{}获得了{}！", team(Lang::Hans, *t), soul(Lang::Hans, e)), soul_effect(Lang::Hans, e));
            hant = (format!("{}獲得了{}！", team(Lang::Hant, *t), soul(Lang::Hant, e)), soul_effect(Lang::Hant, e));
            en = (format!("{} has claimed the {}!", team(Lang::En, *t), soul(Lang::En, e)), soul_effect(Lang::En, e));
        }
        What::ElderKilled { team: t, holders: ids } => {
            let (s, p) = (secs(rules::ELDER_T), rules::EXECUTE_PCT);
            let who = |l| holders(l, ids, name);
            hans = (format!("{}击杀了远古巨龙！", team(Lang::Hans, *t)),
                    format!("{}获得远古龙之力 {s} 秒：点燃敌方英雄，生命低于 {p}% 时斩杀", who(Lang::Hans)));
            hant = (format!("{}擊殺了遠古巨龍！", team(Lang::Hant, *t)),
                    format!("{}獲得遠古龍之力 {s} 秒：點燃敵方英雄，生命低於 {p}% 時斬殺", who(Lang::Hant)));
            let w = who(Lang::En);
            en = (format!("{} has slain the Elder Dragon!", team(Lang::En, *t)),
                  if w.is_empty() {
                      format!("Aspect of the Dragon for {s} s: burn enemy champions, execute them below {p}% health")
                  } else {
                      format!("{w}: Aspect of the Dragon for {s} s - burn enemy champions, execute them below {p}% health")
                  });
        }
        What::Execute { killer, victim, .. } => {
            let (k, v) = (name(killer), name(victim));
            hans = (format!("远古龙之力：{k} 斩杀了 {v}！"), String::new());
            hant = (format!("遠古龍之力：{k} 斬殺了 {v}！"), String::new());
            en = (format!("Aspect of the Dragon: {k} executed {v}!"), String::new());
        }
        What::BaronKilled { team: t, holders: ids } => {
            let (s, p, r, a) = (secs(rules::BARON_T), rules::BARON_PCT, rules::MINION_REDUCE, rules::MINION_ATTACK);
            let who = |l| holders(l, ids, name);
            hans = (format!("{}击杀了纳什男爵！小兵得到强化", team(Lang::Hans, *t)),
                    format!("{}获得纳什男爵之手 {s} 秒：攻击力、法强 +{p}%，身边的己方小兵受到的伤害 -{r}%、攻击力 +{a}%",
                            who(Lang::Hans)));
            hant = (format!("{}擊殺了巴龍！小兵得到強化", team(Lang::Hant, *t)),
                    format!("{}獲得巴龍之手 {s} 秒：攻擊力、法強 +{p}%，身邊的己方小兵受到的傷害 -{r}%、攻擊力 +{a}%",
                            who(Lang::Hant)));
            let w = who(Lang::En);
            let fx = format!("Hand of Baron for {s} s - +{p}% attack damage and ability power, minions near them take {r}% less \
                              damage and hit {a}% harder");
            en = (format!("{} has slain Baron Nashor! Minions empowered", team(Lang::En, *t)),
                  if w.is_empty() { fx } else { format!("{w}: {fx}") });
        }
        What::Conflict => {
            hans = ("检测到创意工坊模组 Elemental Drakes & Baron".into(), "请在模组列表里关掉它，本模组的龙才会生效".into());
            hant = ("偵測到創意工坊模組 Elemental Drakes & Baron".into(), "請在模組列表裡關掉它，本模組的龍才會生效".into());
            en = ("Workshop mod \"Elemental Drakes & Baron\" detected".into(),
                  "Turn it off in the mod list for League's dragons to work".into());
        }
    }
    pick(lang, hans, hant, en)
}

// ===================== HUD =====================

/// HUD 顶上一行：这一条（活着的）或下一条龙。
pub fn dragon_status(lang: Lang, e: Element, alive: bool) -> String {
    let d = drake(lang, e);
    match (lang, alive) {
        (Lang::Hans, true) => format!("{d} 已刷新"),
        (Lang::Hans, false) => format!("下一条 {d}"),
        (Lang::Hant, true) => format!("{d} 已出現"),
        (Lang::Hant, false) => format!("下一隻 {d}"),
        (Lang::En, true) => format!("{d} is up"),
        (Lang::En, false) => format!("Next: {d}"),
    }
}

/// HUD 顶上一行：龙魂会是哪种元素（峡谷的元素，这一局的第三种），还没有哪一队拿到龙魂时写（用户：「龙魂是哪条元素的龙也没提示」）。
pub fn soul_hint(lang: Lang, e: Element) -> String {
    let el = element(lang, e);
    pick(lang, format!("龙魂：{el}"), format!("龍魂：{el}"), format!("Soul: {el}"))
}

/// `n` 层这种元素亚龙一共多的（`rules::drake_buff(e, n)` 的数字；海洋每层回复的百分比相加）。
pub fn stack_total(lang: Lang, e: Element, n: u8) -> String {
    if n <= 1 {
        return stack_effect(lang, e);
    }
    let b = rules::drake_buff(e, n);
    match e {
        Element::Infernal => {
            let p = b.attack_mult;
            pick(lang, format!("攻击力、法强 +{p}%"), format!("攻擊力、法強 +{p}%"), format!("+{p}% attack damage and ability power"))
        }
        Element::Mountain => {
            let p = b.defence_mult;
            pick(lang, format!("护甲、魔抗 +{p}%"), format!("護甲、魔抗 +{p}%"), format!("+{p}% armor and magic resist"))
        }
        Element::Ocean => {
            let (s, p) = (secs(rules::OCEAN_EVERY), rules::OCEAN_PCT * n as usize);
            pick(lang, format!("每 {s} 秒回复 {p}% 已损生命"), format!("每 {s} 秒回復 {p}% 已損生命"),
                 format!("{p}% missing health back every {s} s"))
        }
        Element::Cloud => {
            let p = b.move_speed_mult;
            pick(lang, format!("移速 +{p}%"), format!("移速 +{p}%"), format!("+{p}% move speed"))
        }
        Element::Hextech => {
            let a = b.attack_speed_mult;
            pick(lang, format!("攻速 +{a}%、技能冷却更快"), format!("攻速 +{a}%、技能冷卻更快"),
                 format!("+{a}% attack speed, faster cooldowns"))
        }
        Element::Chemtech => {
            let (t, v) = (b.toughness, b.vamp);
            pick(lang, format!("韧性 +{t}%、生命偷取 +{v}%"), format!("韌性 +{t}%、生命偷取 +{v}%"),
                 format!("+{t}% tenacity, +{v}% life steal"))
        }
        Element::Elder => String::new(),
    }
}

/// 鼠标停在 HUD 上时的说明框：每一行 (文字, 颜色 0xRRGGBBAA, 粗体)。两队现在的加成、每种元素每层的加成、龙魂、远古巨龙、
/// 纳什男爵（用户：「这个面板里面我也看不到详细的小龙加成说明 起码也要做到我悬浮的时候 有个说明框吧」）。
pub fn tip_lines(lang: Lang, rec: &rules::Record) -> Vec<(String, u32, bool)> {
    const GOLD: u32 = 0xff_d8_8a_ff;
    const DIM: u32 = 0xa8_a4_9c_ff;
    let mut out = vec![(pick(lang, "元素亚龙：拿下后全队永久加成，可以叠加", "元素亞龍：拿下後全隊永久加成，可以疊加",
                             "Elemental drakes: a permanent bonus for the whole team, stacking").to_string(), GOLD, true)];
    let sep = pick(lang, "、", "、", ", ");
    for t in 0..2 {
        let mut parts = Vec::new();
        for e in rules::DRAKES {
            let n = rec.stacks[t][e.slot().unwrap_or(0)];
            if n > 0 {
                parts.push(format!("{} ×{n}（{}）", element(lang, e), stack_total(lang, e, n)));
            }
        }
        let have = if parts.is_empty() { pick(lang, "还没有", "還沒有", "none yet").to_string() } else { parts.join(sep) };
        out.push((format!("{}：{have}", team(lang, t)), if t == 0 { 0x8c_9c_ff_ff } else { 0xff_8c_96_ff }, false));
    }
    out.push((pick(lang, "每一层：", "每一層：", "Each stack:").to_string(), DIM, false));
    for e in rules::DRAKES {
        out.push((format!("  {}  {}", drake(lang, e), stack_effect(lang, e)), colour_text(e), false));
    }
    match rec.soul.and_then(|(t, c)| Element::from_code(c).map(|e| (t, e))) {
        Some((t, e)) => out.push((format!("{}{}{}：{}", team(lang, t), pick(lang, "拿到了", "拿到了", " claimed "), soul(lang, e),
                                          soul_effect(lang, e)), colour_text(e), false)),
        None => {
            if let Some(e) = rec.soul_shown() {
                out.push((format!("{}（{}）：{}", soul(lang, e),
                                  pick(lang, "先拿满 4 条元素亚龙的一队获得", "先拿滿 4 隻元素亞龍的一隊獲得", "the first team to 4 drakes"),
                                  soul_effect(lang, e)), colour_text(e), false));
            }
        }
    }
    let (s, p) = (secs(rules::ELDER_T), rules::EXECUTE_PCT);
    out.push((pick(lang, format!("远古巨龙：龙魂之后刷新；击杀后 {s} 秒点燃敌方英雄，生命低于 {p}% 时斩杀"),
                     format!("遠古巨龍：龍魂之後刷新；擊殺後 {s} 秒點燃敵方英雄，生命低於 {p}% 時斬殺"),
                     format!("Elder Dragon: after a soul; its takers burn enemy champions for {s} s, executing below {p}%")),
              colour_text(Element::Elder), false));
    let (s, p, r, a) = (secs(rules::BARON_T), rules::BARON_PCT, rules::MINION_REDUCE, rules::MINION_ATTACK);
    out.push((pick(lang, format!("纳什男爵之手：{s} 秒攻击力、法强 +{p}%，身边己方小兵受到的伤害 -{r}%、攻击力 +{a}%"),
                     format!("巴龍之手：{s} 秒攻擊力、法強 +{p}%，身邊己方小兵受到的傷害 -{r}%、攻擊力 +{a}%"),
                     format!("Hand of Baron: {s} s of +{p}% attack damage and ability power; minions near take {r}% less damage, hit {a}% harder")),
              0xc8_9c_ff_ff, false));
    out
}

/// 说明框里一种元素的字色（元素颜色，太暗的提亮）。
fn colour_text(e: Element) -> u32 {
    match e {
        Element::Infernal => 0xff_8a_5a_ff,
        Element::Mountain => 0xe0_b8_7a_ff,
        Element::Ocean => 0x6c_e0_f0_ff,
        Element::Cloud => 0xe4_f2_ff_ff,
        Element::Hextech => 0xb0_a8_ff_ff,
        Element::Chemtech => 0xb4_f0_5a_ff,
        Element::Elder => 0xff_e0_a0_ff,
    }
}

/// HUD 顶上一行：纳什男爵活着。
pub fn baron_status(lang: Lang) -> &'static str {
    pick(lang, "纳什男爵 已刷新", "巴龍 已出現", "Baron Nashor is up")
}

/// 计时的标签：远古龙之力 / 纳什男爵之手。
pub fn timer_label(lang: Lang, baron: bool) -> &'static str {
    if baron {
        pick(lang, "男爵", "巴龍", "Baron")
    } else {
        pick(lang, "远古", "遠古", "Elder")
    }
}

/// 一队什么都还没有。
pub const NOTHING: &str = "—";

/// 撞上创意工坊的大小龙 mod 时 HUD 上一直写着的。
pub fn conflict_line(lang: Lang) -> &'static str {
    pick(lang, "创意工坊的 Elemental Drakes & Baron 开着：本模组的龙不生效",
         "創意工坊的 Elemental Drakes & Baron 開著：本模組的龍不生效",
         "Workshop \"Elemental Drakes & Baron\" is on: League's dragons are off")
}

#[cfg(test)]
mod tests {
    #[test]
    fn the_tooltip_says_each_teams_bonus_the_soul_and_the_epic_monsters() {
        let mut r = rules::Record { order: [6, 3, 2], ..rules::Record::default() };
        r.stacks[1] = [0, 0, 0, 0, 0, 1];           // red: one chemtech
        r.stacks[0] = [2, 0, 0, 0, 0, 0];           // blue: two infernal
        let lines: Vec<String> = tip_lines(Lang::Hans, &r).into_iter().map(|l| l.0).collect();
        let all = lines.join("
");
        assert!(all.contains("蓝色方：炼狱 ×2（攻击力、法强 +16%）") || all.contains("蓝方：炼狱 ×2（攻击力、法强 +16%）"), "{all}");
        assert!(all.contains("化学科技 ×1（韧性 +"), "{all}");
        assert!(all.contains("山脉龙魂（先拿满 4 条元素亚龙的一队获得）"), "{all}");
        assert!(all.contains("远古巨龙：龙魂之后刷新") && all.contains("纳什男爵之手："), "{all}");
        assert_eq!(soul_hint(Lang::Hans, Element::Mountain), "龙魂：山脉");
        // the soul's element only once the second drake is taken, as in League (the user: 「改成第二条死后显示」)
        let early = |taken: [u8; 6], alive: bool| {
            let mut e = rules::Record { order: [6, 3, 2], serpen_alive: alive, ..rules::Record::default() };
            e.stacks[0] = taken;
            tip_lines(Lang::Hans, &e).into_iter().map(|l| l.0).collect::<Vec<_>>().join("
")
        };
        assert!(!early([0; 6], true).contains("龙魂（"), "the first drake");
        assert!(!early([1, 0, 0, 0, 0, 0], true).contains("龙魂（"), "one taken, the second alive");
        assert!(early([1, 0, 0, 0, 0, 1], false).contains("山脉龙魂（"), "two taken, the third not out yet");
        // a soul claimed: who has it instead of the hint
        r.soul = Some((1, 2));
        let all: String = tip_lines(Lang::Hans, &r).into_iter().map(|l| l.0).collect::<Vec<_>>().join("
");
        assert!(all.contains("拿到了山脉龙魂："), "{all}");
    }

    use super::*;

    fn name(id: &str) -> String {
        match id {
            "league_jinx" => "金克丝".to_string(),
            "league_garen" => "盖伦".to_string(),
            "league_ahri" => "阿狸".to_string(),
            x => x.trim_start_matches("league_").to_string(),
        }
    }

    fn all_whats() -> Vec<What> {
        let ids = |v: &[&str]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>();
        let mut v = vec![What::ElderSpawn, What::Conflict,
                         What::ElderKilled { team: 0, holders: ids(&["league_jinx", "league_garen"]) },
                         What::ElderKilled { team: 1, holders: vec![] },
                         What::Execute { team: 0, killer: "league_jinx".into(), victim: "league_ahri".into() },
                         What::BaronKilled { team: 1, holders: ids(&["league_ahri"]) },
                         What::BaronKilled { team: 0, holders: ids(&["a", "b", "c", "d", "e"]) }];
        for e in rules::DRAKES {
            v.push(What::DrakeSpawn { element: e });
            v.push(What::Drake { team: 0, element: e, total: 1 });
            v.push(What::Drake { team: 1, element: e, total: 3 });
            v.push(What::Soul { team: 1, element: e });
        }
        v
    }

    /// The user's own examples, word for word (the title line).
    #[test]
    fn the_users_examples_read_as_given() {
        let t = |w: What| notice(Lang::Hans, &w, &name).0;
        assert_eq!(t(What::Drake { team: 0, element: Element::Infernal, total: 1 }), "蓝色方击杀了炼狱亚龙！");
        assert_eq!(t(What::Soul { team: 1, element: Element::Infernal }), "红色方获得了炼狱龙魂！");
        assert_eq!(t(What::ElderSpawn), "远古巨龙出现了！");
        assert_eq!(t(What::ElderKilled { team: 0, holders: vec![] }), "蓝色方击杀了远古巨龙！");
        assert_eq!(t(What::Execute { team: 0, killer: "league_jinx".into(), victim: "league_garen".into() }),
                   "远古龙之力：金克丝 斩杀了 盖伦！");
        assert_eq!(t(What::BaronKilled { team: 0, holders: vec![] }), "蓝色方击杀了纳什男爵！小兵得到强化");
        let (a, b) = notice(Lang::Hans, &What::Conflict, &name);
        assert_eq!(format!("{a}，{b}"), "检测到创意工坊模组 Elemental Drakes & Baron，请在模组列表里关掉它，本模组的龙才会生效");
    }

    #[test]
    fn the_second_lines_carry_the_effects_and_the_names() {
        let d = |w: What| notice(Lang::Hans, &w, &name).1;
        assert_eq!(d(What::Drake { team: 0, element: Element::Infernal, total: 2 }), "全队攻击力、法强 +8%（共 2 条）");
        assert_eq!(d(What::Drake { team: 1, element: Element::Ocean, total: 3 }),
                   "全队每 5 秒回复 3% 已损生命（共 3 条，再拿 1 条获得龙魂）");
        assert_eq!(d(What::DrakeSpawn { element: Element::Hextech }), "击杀后全队攻速 +10%、技能冷却 -8%");
        assert_eq!(d(What::DrakeSpawn { element: Element::Chemtech }), "击杀后全队韧性 +10%、生命偷取 +3%");
        assert_eq!(d(What::ElderKilled { team: 0, holders: vec!["league_jinx".into(), "league_garen".into()] }),
                   "金克丝、盖伦获得远古龙之力 90 秒：点燃敌方英雄，生命低于 20% 时斩杀");
        assert!(d(What::BaronKilled { team: 1, holders: vec!["league_ahri".into()] })
            .starts_with("阿狸获得纳什男爵之手 120 秒：攻击力、法强 +20%，身边的己方小兵受到的伤害 -40%、攻击力 +30%"));
        let five: Vec<String> = ["a", "b", "c", "d", "e"].iter().map(|x| x.to_string()).collect();
        assert!(d(What::BaronKilled { team: 1, holders: five }).starts_with("全队获得纳什男爵之手"));
        assert_eq!(d(What::Soul { team: 0, element: Element::Cloud }), "移速 +15%，放大招后移速再 +50%（6 秒）");
        assert_eq!(d(What::Soul { team: 0, element: Element::Hextech }), "每 2.5 秒，下一次命中放出连锁闪电，减速敌人");
        assert_eq!(d(What::Soul { team: 0, element: Element::Chemtech }), "生命低于 50% 时韧性 +15%、伤害 +12%、受到的伤害 -12%");
        assert!(d(What::Execute { team: 0, killer: "a".into(), victim: "b".into() }).is_empty());
    }

    #[test]
    fn traditional_and_english_too() {
        let hant = |w: What| notice(Lang::Hant, &w, &name);
        assert_eq!(hant(What::Drake { team: 1, element: Element::Mountain, total: 1 }).0, "紅色方擊殺了山脈亞龍！");
        assert_eq!(hant(What::BaronKilled { team: 0, holders: vec![] }).0, "藍色方擊殺了巴龍！小兵得到強化");
        assert_eq!(hant(What::Soul { team: 0, element: Element::Chemtech }).0, "藍色方獲得了化學科技龍魂！");
        let en = |w: What| notice(Lang::En, &w, &name);
        assert_eq!(en(What::Drake { team: 0, element: Element::Cloud, total: 1 }),
                   ("Blue Team has slain the Cloud Drake!".to_string(), "+8% move speed for the whole team (1 drake)".to_string()));
        assert_eq!(en(What::ElderSpawn).0, "The Elder Dragon has spawned!");
        assert_eq!(en(What::Execute { team: 1, killer: "league_ahri".into(), victim: "league_jinx".into() }).0,
                   "Aspect of the Dragon: 阿狸 executed 金克丝!");
    }

    #[test]
    fn every_notice_has_a_title_in_every_language() {
        for w in all_whats() {
            for lang in [Lang::Hans, Lang::Hant, Lang::En] {
                let (t, d) = notice(lang, &w, &name);
                assert!(!t.is_empty(), "{w:?} {lang:?}");
                assert!(!t.contains('{') && !d.contains('{') && !t.contains("league_"), "{w:?} {lang:?}: {t} / {d}");
                // only the execute has no second line
                assert_eq!(d.is_empty(), matches!(w, What::Execute { .. }), "{w:?} {lang:?}");
            }
        }
    }

    #[test]
    fn element_words_cover_every_element() {
        for e in rules::DRAKES.into_iter().chain([Element::Elder]) {
            for lang in [Lang::Hans, Lang::Hant, Lang::En] {
                assert!(!element(lang, e).is_empty() && !glyph(lang, e).is_empty());
                assert!(!drake(lang, e).is_empty() && !dragon_status(lang, e, true).is_empty());
            }
            if e != Element::Elder {
                assert!(!stack_effect(Lang::En, e).is_empty() && !soul_effect(Lang::Hant, e).is_empty());
            }
        }
        // the glyphs of one language tell the elements apart
        for lang in [Lang::Hans, Lang::Hant, Lang::En] {
            let mut g: Vec<&str> = rules::DRAKES.iter().map(|&e| glyph(lang, e)).collect();
            g.sort();
            g.dedup();
            assert_eq!(g.len(), 6, "{lang:?}");
        }
        assert_eq!(drake(Lang::Hans, Element::Elder), "远古巨龙");
        assert_eq!(soul(Lang::Hant, Element::Infernal), "煉獄龍魂");
        assert_eq!(dragon_status(Lang::Hans, Element::Ocean, false), "下一条 海洋亚龙");
        assert_eq!(dragon_status(Lang::En, Element::Elder, true), "Elder Dragon is up");
    }

    #[test]
    fn numbers_and_language() {
        assert_eq!((secs(300), secs(150), secs(5400), secs(7200)), ("5".into(), "2.5".into(), "90".into(), "120".into()));
        assert_eq!((clock(65), clock(120), clock(9)), ("1:05".into(), "2:00".into(), "0:09".into()));
        assert_eq!(hextech_cd_pct(), 8);
        assert_eq!(lang_of("纳什男爵", ""), Lang::Hans);
        assert_eq!(lang_of("巴龍", ""), Lang::Hant);
        assert_eq!(lang_of("Baron Nashor", "去而复还"), Lang::En);
        // our names not there (another language, or the texts not installed): Akshan's skill name decides
        assert_eq!(lang_of("莫尔加德", "去而复还"), Lang::Hans);
        assert_eq!(lang_of("Morgard", "復仇迴力鏢"), Lang::Hant);
        assert_eq!(lang_of("모르가드", "복수의 부메랑"), Lang::En);
        assert_eq!(lang_of("", "Avengerang"), Lang::En);
    }
}
