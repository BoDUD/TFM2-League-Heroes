//! 画面上的字（简体、繁体、英文、韩语、日语）：公告的标题和第二行、HUD 的标签。纯函数，单元测试在这里。
//!
//! 数字都从 `rules.rs` 来（每层的数值从 `rules::drake_buff` 读），玩法改了数，字跟着变。元素的中文名是英雄联盟国服的叫法
//! （`rules::Element::zh`），繁体是台服的写法，英文是英雄联盟的。队伍照用户给的样子叫「蓝色方」「红色方」。
//! 韩语、日语（0.5.10，用户：「不支持韩语和日语吗」「加上韩语日语」）照英雄联盟韩服、日服的叫法：원소 드래곤 / エレメンタルドラゴン、
//! 화염의 드래곤 / インファーナルドラゴン、장로 드래곤 / エルダードラゴン、내셔 남작 / バロンナッシャー、드래곤의 영혼 / ドラゴンソウル；
//! 队伍照游戏自己的「블루 팀 / 레드 팀」「ブルーチーム / レッドチーム」。

use super::feed::What;
use super::rules::{self, Element};

/// 游戏的语言：简体、繁体、英文、韩语、日语，其他语言都用英文（league_eggs notice.rs 的做法）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Lang {
    Hans,
    Hant,
    En,
    Ko,
    Ja,
}

impl Lang {
    pub const ALL: [Lang; 5] = [Lang::Hans, Lang::Hant, Lang::En, Lang::Ko, Lang::Ja];
}

/// 认游戏的语言。先看本包改过的纳什男爵的名字（`asset/base/text/object?epic.name`：纳什男爵 / 巴龍 / Baron Nashor /
/// 내셔 남작 / バロンナッシャー），认不出（别的语言、本包的文字没装上）再按阿克尚第一个技能名的写法（league_eggs、league_akshan 的做法）。
pub fn lang_of(baron: &str, sample: &str) -> Lang {
    if baron.contains("纳什男爵") {
        return Lang::Hans;
    }
    if baron.contains("巴龍") {
        return Lang::Hant;
    }
    if baron.contains("Baron Nashor") {
        return Lang::En;
    }
    if baron.contains("내셔 남작") {
        return Lang::Ko;
    }
    if baron.contains("バロンナッシャー") {
        return Lang::Ja;
    }
    // another mod's name for him: the game's own texts (src/screen.rs lang) - hangul is Korean, kana Japanese, and Chinese
    // is Traditional when it has more of Traditional's own characters than of Simplified's
    let has = |lo: u32, hi: u32| sample.chars().any(|c| (lo..=hi).contains(&(c as u32)));
    let count = |set: &str| sample.chars().filter(|c| set.contains(*c)).count();
    if has(0xac00, 0xd7a3) {
        Lang::Ko
    } else if has(0x3040, 0x30ff) {
        Lang::Ja
    } else if count(TRAD_ONLY) > count(SIMP_ONLY) {
        Lang::Hant
    } else if has(0x4e00, 0x9fff) {
        Lang::Hans
    } else {
        Lang::En
    }
}

/// This mod's own names for Baron (text/object.i18n): the language is known from them alone.
pub fn named_by_us(baron: &str) -> bool {
    ["纳什男爵", "巴龍", "Baron Nashor", "내셔 남작", "バロンナッシャー"].iter().any(|n| baron.contains(n))
}

/// Characters only Traditional Chinese writes, and their Simplified forms (common in skill and champion names).
const TRAD_ONLY: &str = "復還靈術師實點種體場隊員頭開關劍為們個來說這時會對動戰擊龍彈護衛變轉發雙氣傷敵減範圍線傳華擁擋擺擴擲撲擾憶鬥盜獵飛鋼鐵";
const SIMP_ONLY: &str = "复还灵术师实点种体场队员头开关剑为们个来说这时会对动战击龙弹护卫变转发双气伤敌减范围线传华拥挡摆扩掷扑扰忆斗盗猎飞钢铁";

fn pick<T>(lang: Lang, hans: T, hant: T, en: T, ko: T, ja: T) -> T {
    match lang {
        Lang::Hans => hans,
        Lang::Hant => hant,
        Lang::En => en,
        Lang::Ko => ko,
        Lang::Ja => ja,
    }
}

/// 冒号：中文、日文全角，韩文、英文半角加空格（韩文、英文的标点是半角的）。
fn colon(lang: Lang) -> &'static str {
    pick(lang, "：", "：", "：", ": ", "：")
}

/// 元素的名字：炼狱 / 煉獄 / Infernal / 화염 / インファーナル。
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
        Lang::Ko => match e {
            Element::Infernal => "화염",
            Element::Mountain => "대지",
            Element::Ocean => "바다",
            Element::Cloud => "바람",
            Element::Hextech => "마법공학",
            Element::Chemtech => "화학공학",
            Element::Elder => "장로",
        },
        Lang::Ja => match e {
            Element::Infernal => "インファーナル",
            Element::Mountain => "マウンテン",
            Element::Ocean => "オーシャン",
            Element::Cloud => "クラウド",
            Element::Hextech => "ヘクステック",
            Element::Chemtech => "ケミテック",
            Element::Elder => "エルダー",
        },
    }
}

/// 韩服的写法：화염의 / 대지의 / 바다의 / 바람의 + 名词，마법공학 / 화학공학 直接接（마법공학 드래곤）。
fn ko_of(e: Element) -> String {
    let n = element(Lang::Ko, e);
    if matches!(e, Element::Hextech | Element::Chemtech) {
        format!("{n} ")
    } else {
        format!("{n}의 ")
    }
}

/// 这条龙的名字：炼狱亚龙 / 煉獄亞龍 / Infernal Drake / 화염의 드래곤 / インファーナルドラゴン；远古巨龙 / 遠古巨龍 /
/// Elder Dragon / 장로 드래곤 / エルダードラゴン。
pub fn drake(lang: Lang, e: Element) -> String {
    if e == Element::Elder {
        return pick(lang, "远古巨龙", "遠古巨龍", "Elder Dragon", "장로 드래곤", "エルダードラゴン").to_string();
    }
    let n = element(lang, e);
    match lang {
        Lang::Hans => format!("{n}亚龙"),
        Lang::Hant => format!("{n}亞龍"),
        Lang::En => format!("{n} Drake"),
        Lang::Ko => format!("{}드래곤", ko_of(e)),
        Lang::Ja => format!("{n}ドラゴン"),
    }
}

/// 龙魂：炼狱龙魂 / 煉獄龍魂 / Infernal Soul / 화염의 영혼 / インファーナルソウル。
pub fn soul(lang: Lang, e: Element) -> String {
    let n = element(lang, e);
    match lang {
        Lang::Hans => format!("{n}龙魂"),
        Lang::Hant => format!("{n}龍魂"),
        Lang::En => format!("{n} Soul"),
        Lang::Ko => format!("{n}의 영혼"),
        Lang::Ja => format!("{n}ソウル"),
    }
}

/// 队伍（0 蓝、1 红）：蓝色方 / 藍色方 / Blue Team / 블루 팀 / ブルーチーム。
pub fn team(lang: Lang, t: usize) -> &'static str {
    if t == 0 {
        pick(lang, "蓝色方", "藍色方", "Blue Team", "블루 팀", "ブルーチーム")
    } else {
        pick(lang, "红色方", "紅色方", "Red Team", "레드 팀", "レッドチーム")
    }
}

/// HUD 每一行开头的队伍小标：蓝 / 藍 / BLUE / 블루 / ブルー。
pub fn team_tag(lang: Lang, t: usize) -> &'static str {
    if t == 0 {
        pick(lang, "蓝", "藍", "BLUE", "블루", "ブルー")
    } else {
        pick(lang, "红", "紅", "RED", "레드", "レッド")
    }
}

/// 元素圆点里的字（玩家的叫法：火龙、土龙、水龙、风龙、海克斯龙、化学龙；远古）。韩语取各自的一个字（화염 화、대지 대、바다 바、
/// 바람 풍、마법공학 마、화학공학的毒雾 독、장로 장），日语取片假名的头一个字。
pub fn glyph(lang: Lang, e: Element) -> &'static str {
    match (lang, e) {
        (Lang::En, Element::Infernal) => "In",
        (Lang::En, Element::Mountain) => "Mt",
        (Lang::En, Element::Ocean) => "Oc",
        (Lang::En, Element::Cloud) => "Cl",
        (Lang::En, Element::Hextech) => "Hx",
        (Lang::En, Element::Chemtech) => "Ch",
        (Lang::En, Element::Elder) => "El",
        (Lang::Ko, Element::Infernal) => "화",
        (Lang::Ko, Element::Mountain) => "대",
        (Lang::Ko, Element::Ocean) => "바",
        (Lang::Ko, Element::Cloud) => "풍",
        (Lang::Ko, Element::Hextech) => "마",
        (Lang::Ko, Element::Chemtech) => "독",
        (Lang::Ko, Element::Elder) => "장",
        (Lang::Ja, Element::Infernal) => "イ",
        (Lang::Ja, Element::Mountain) => "マ",
        (Lang::Ja, Element::Ocean) => "オ",
        (Lang::Ja, Element::Cloud) => "ク",
        (Lang::Ja, Element::Hextech) => "ヘ",
        (Lang::Ja, Element::Chemtech) => "ケ",
        (Lang::Ja, Element::Elder) => "エ",
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
                 format!("+{p}% attack damage and ability power"), format!("공격력, 주문력 +{p}%"), format!("攻撃力と魔力 +{p}%"))
        }
        Element::Mountain => {
            let p = b.defence_mult;
            pick(lang, format!("护甲、魔抗 +{p}%"), format!("護甲、魔抗 +{p}%"), format!("+{p}% armor and magic resist"),
                 format!("방어력, 마법 저항력 +{p}%"), format!("物理防御と魔法防御 +{p}%"))
        }
        Element::Ocean => {
            let (s, p) = (secs(rules::OCEAN_EVERY), rules::OCEAN_PCT);
            pick(lang, format!("每 {s} 秒回复 {p}% 已损生命"), format!("每 {s} 秒回復 {p}% 已損生命"),
                 format!("{p}% missing health back every {s} s"), format!("{s}초마다 잃은 체력의 {p}% 회복"),
                 format!("{s} 秒ごとに失った体力の {p}% を回復"))
        }
        Element::Cloud => {
            let p = b.move_speed_mult;
            pick(lang, format!("移速 +{p}%"), format!("移速 +{p}%"), format!("+{p}% move speed"), format!("이동 속도 +{p}%"),
                 format!("移動速度 +{p}%"))
        }
        Element::Hextech => {
            let (a, c) = (b.attack_speed_mult, hextech_cd_pct());
            pick(lang, format!("攻速 +{a}%、技能冷却 -{c}%"), format!("攻速 +{a}%、技能冷卻 -{c}%"),
                 format!("+{a}% attack speed, {c}% shorter cooldowns"), format!("공격 속도 +{a}%, 스킬 재사용 대기시간 -{c}%"),
                 format!("攻撃速度 +{a}%、スキルのクールダウン -{c}%"))
        }
        Element::Chemtech => {
            let (t, v) = (b.toughness, b.vamp);
            pick(lang, format!("韧性 +{t}%、生命偷取 +{v}%"), format!("韌性 +{t}%、生命偷取 +{v}%"),
                 format!("+{t}% tenacity, +{v}% life steal"), format!("강인함 +{t}%, 생명력 흡수 +{v}%"),
                 format!("行動妨害耐性 +{t}%、ライフスティール +{v}%"))
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
                 format!("every {s} s the next hit on a champion explodes, hurting the enemies around him"),
                 format!("{s}초마다 다음에 적 챔피언에게 피해를 입히면 폭발해 주변 적 챔피언에게도 피해"),
                 format!("{s} 秒ごとに、次に敵チャンピオンへダメージを与えると爆発し、周囲の敵チャンピオンにもダメージ"))
        }
        Element::Mountain => {
            let s = secs(rules::MOUNTAIN_SOUL_IDLE);
            pick(lang, format!("{s} 秒没受到伤害后获得一层护盾"), format!("{s} 秒沒受到傷害後獲得一層護盾"),
                 format!("a shield after {s} s without taking damage"), format!("{s}초 동안 피해를 받지 않으면 보호막 획득"),
                 format!("{s} 秒間ダメージを受けないとシールドを獲得"))
        }
        Element::Ocean => {
            let s = secs(rules::OCEAN_SOUL_PULSES as usize * rules::OCEAN_SOUL_EVERY);
            pick(lang, format!("伤害敌方英雄后 {s} 秒内持续回复生命"), format!("傷害敵方英雄後 {s} 秒內持續回復生命"),
                 format!("hitting a champion heals over {s} s"), format!("적 챔피언에게 피해를 입히면 {s}초 동안 체력 회복"),
                 format!("敵チャンピオンにダメージを与えると {s} 秒間体力を回復"))
        }
        Element::Cloud => {
            let (m, h, s) = (rules::CLOUD_SOUL_MS, rules::CLOUD_HASTE_MS, secs(rules::CLOUD_HASTE_T));
            pick(lang, format!("移速 +{m}%，放大招后移速再 +{h}%（{s} 秒）"),
                 format!("移速 +{m}%，放大招後移速再 +{h}%（{s} 秒）"),
                 format!("+{m}% move speed, +{h}% more for {s} s after the ultimate"),
                 format!("이동 속도 +{m}%, 궁극기 사용 후 {s}초 동안 이동 속도 추가 +{h}%"),
                 format!("移動速度 +{m}%、アルティメット使用後 {s} 秒間さらに +{h}%"))
        }
        Element::Hextech => {
            let s = secs(rules::HEXTECH_SOUL_CD);
            pick(lang, format!("每 {s} 秒，下一次命中放出连锁闪电，减速敌人"),
                 format!("每 {s} 秒，下一次命中放出連鎖閃電，減速敵人"),
                 format!("every {s} s the next hit chains lightning that slows"),
                 format!("{s}초마다 다음 적중 시 연쇄 번개가 튀어 적을 둔화"),
                 format!("{s} 秒ごとに、次の命中で連鎖する稲妻を放ち敵をスロウ"))
        }
        Element::Chemtech => {
            let b = rules::chem_low_buff();
            let (p, t, d, r) = (rules::CHEM_LOW_PCT, b.toughness, b.attack_mult, b.damaged_reduce);
            pick(lang, format!("生命低于 {p}% 时韧性 +{t}%、伤害 +{d}%、受到的伤害 -{r}%"),
                 format!("生命低於 {p}% 時韌性 +{t}%、傷害 +{d}%、受到的傷害 -{r}%"),
                 format!("below {p}% health: +{t}% tenacity, +{d}% damage, {r}% less damage taken"),
                 format!("체력 {p}% 미만일 때 강인함 +{t}%, 피해량 +{d}%, 받는 피해 -{r}%"),
                 format!("体力 {p}% 未満で行動妨害耐性 +{t}%、与ダメージ +{d}%、被ダメージ -{r}%"))
        }
        Element::Elder => String::new(),
    }
}

/// 峡谷的名字：云端峡谷 / 雲端峽谷 / Cloud Rift / 바람의 협곡 / クラウドリフト。
pub fn rift(lang: Lang, e: Element) -> String {
    let n = element(lang, e);
    match lang {
        Lang::Hans => format!("{n}峡谷"),
        Lang::Hant => format!("{n}峽谷"),
        Lang::En => format!("{n} Rift"),
        Lang::Ko => format!("{}협곡", ko_of(e)),
        Lang::Ja => format!("{n}リフト"),
    }
}

/// 这种峡谷的地形做什么（数字从 `rift.rs` 来）。
pub fn rift_effect(lang: Lang, e: Element) -> String {
    use super::rift;
    match e {
        Element::Cloud => {
            let p = rift::WIND_MS;
            pick(lang, format!("河道和野区吹起风道：英雄在风道里移速 +{p}%"), format!("河道和野區吹起風道：英雄在風道裡移速 +{p}%"),
                 format!("wind currents in the river and the jungle: +{p}% move speed inside them"),
                 format!("강가와 정글에 바람길이 생김: 바람길 안에서 이동 속도 +{p}%"),
                 format!("川とジャングルに風の流れが生まれる：流れの中では移動速度 +{p}%"))
        }
        Element::Hextech => {
            let s = secs(rift::GATE_CD);
            pick(lang, format!("野区和龙坑、男爵坑旁出现成对的传送门：脱战时朝着另一头走上去就传过去（每人 {s} 秒一次）"),
                 format!("野區和龍坑、巴龍坑旁出現成對的傳送門：脫戰時朝著另一頭走上去就傳過去（每人 {s} 秒一次）"),
                 format!("paired hex-gates in the jungle and by the pits: out of combat, walk onto one toward its twin to travel (once every {s} s)"),
                 format!("정글과 드래곤·내셔 남작 둥지 근처에 한 쌍의 관문이 생김: 전투 중이 아닐 때 반대편을 향해 올라서면 이동 ({s}초에 한 번)"),
                 format!("ジャングルとドラゴン・バロンの巣のそばに対になったゲートが現れる：非戦闘時にもう一方へ向かって乗ると移動（{s} 秒に一度）"))
        }
        Element::Ocean => {
            pick(lang, "河道和野区长出新的草丛和蜂蜜果实：草丛里藏身（出手就现形），受伤的英雄吃果实回血",
                 "河道和野區長出新的草叢和蜂蜜果實：草叢裡藏身（出手就現形），受傷的英雄吃果實回血",
                 "new brush and honeyfruit in the river and the jungle: hide in the brush (attacking reveals), the hurt eat fruit to heal",
                 "강가와 정글에 새 수풀과 꿀 열매가 자람: 수풀에 숨을 수 있고 (공격하면 드러남), 다친 챔피언은 열매를 먹어 회복",
                 "川とジャングルに新しい茂みとハニーフルーツが生える：茂みに隠れられ（攻撃すると見える）、傷ついたチャンピオンは実を食べて回復")
                .to_string()
        }
        Element::Chemtech => {
            pick(lang, "野区和龙坑旁升起毒雾：站在雾里敌人看不见（出手就现形）",
                 "野區和龍坑旁升起毒霧：站在霧裡敵人看不見（出手就現形）",
                 "chem-fog in the jungle and by the dragon pit: unseen inside it (attacking reveals)",
                 "정글과 드래곤 둥지 근처에 독안개가 피어오름: 안개 속에서는 적에게 보이지 않음 (공격하면 드러남)",
                 "ジャングルとドラゴンの巣のそばに毒霧が立ちこめる：霧の中では敵から見えない（攻撃すると見える）")
                .to_string()
        }
        Element::Mountain => {
            let p = -rift::RUBBLE_MS;
            pick(lang, format!("河道口和野区出现碎石堆：英雄走在上面移速 -{p}%"), format!("河道口和野區出現碎石堆：英雄走在上面移速 -{p}%"),
                 format!("rubble at the pits' mouths and in the jungle: -{p}% move speed on it"),
                 format!("둥지 입구와 정글에 돌무더기가 생김: 그 위에서 이동 속도 -{p}%"),
                 format!("巣の入り口とジャングルに瓦礫の山が現れる：その上では移動速度 -{p}%"))
        }
        Element::Infernal => {
            let p = rift::FIRE_PCT;
            pick(lang, format!("龙坑和男爵坑周围燃起火圈：英雄在火圈里攻击力和法强 +{p}%"),
                 format!("龍坑和巴龍坑周圍燃起火圈：英雄在火圈裡攻擊力和法強 +{p}%"),
                 format!("rings of fire round the dragon and Baron pits: +{p}% attack damage and ability power inside them"),
                 format!("드래곤·내셔 남작 둥지 주위에 불의 고리가 타오름: 고리 안에서 공격력과 주문력 +{p}%"),
                 format!("ドラゴンとバロンの巣の周りに炎の輪が燃え上がる：輪の中では攻撃力と魔力 +{p}%"))
        }
        Element::Elder => String::new(),
    }
}

/// 拿到远古龙之力 / 纳什男爵之手的人：全队都拿到（5 个）写「全队」，一个都没有（都死着）写空。
fn holders(lang: Lang, ids: &[String], name: &dyn Fn(&str) -> String) -> String {
    if ids.len() >= 5 {
        return pick(lang, "全队", "全隊", "The whole team", "팀 전체", "チーム全員").to_string();
    }
    let names: Vec<String> = ids.iter().map(|x| name(x)).collect();
    names.join(pick(lang, "、", "、", ", ", ", ", "、"))
}

/// 一条公告的字：(标题, 第二行；没有第二行就是空的)。`name` 把英雄 id（`league_jinx`）换成游戏里的名字。
pub fn notice(lang: Lang, what: &What, name: &dyn Fn(&str) -> String) -> (String, String) {
    use Lang::*;
    let none = String::new;
    match what {
        What::DrakeSpawn { element } => {
            let (e, fx) = (*element, stack_effect(lang, *element));
            let d = drake(lang, e);
            match lang {
                Hans => (format!("{d}出现了！"), format!("击杀后全队{fx}")),
                Hant => (format!("{d}出現了！"), format!("擊殺後全隊{fx}")),
                En => (format!("The {d} has spawned!"), format!("Slay it: {fx} for the whole team")),
                Ko => (format!("{d}이 등장했습니다!"), format!("처치하면 팀 전체 {fx}")),
                Ja => (format!("{d}が出現しました！"), format!("倒すとチーム全体に {fx}")),
            }
        }
        What::ElderSpawn => {
            let p = rules::EXECUTE_PCT;
            match lang {
                Hans => ("远古巨龙出现了！".into(), format!("击杀它的一方获得远古龙之力：点燃敌方英雄，生命低于 {p}% 时斩杀")),
                Hant => ("遠古巨龍出現了！".into(), format!("擊殺牠的一方獲得遠古龍之力：點燃敵方英雄，生命低於 {p}% 時斬殺")),
                En => ("The Elder Dragon has spawned!".into(),
                       format!("Slay it for the Aspect of the Dragon: burn enemy champions, execute them below {p}% health")),
                Ko => ("장로 드래곤이 등장했습니다!".into(),
                       format!("처치한 팀은 장로 드래곤의 힘을 얻음: 적 챔피언을 불태우고 체력 {p}% 미만이면 처형")),
                Ja => ("エルダードラゴンが出現しました！".into(),
                       format!("倒したチームはエルダードラゴンの力を得る：敵チャンピオンを燃やし、体力 {p}% 未満で処刑")),
            }
        }
        What::Drake { team: t, element, total } => {
            let (e, n) = (*element, *total);
            let soon = n + 1 == rules::SOUL_AT;
            let (tm, d, fx) = (team(lang, *t), drake(lang, e), stack_effect(lang, e));
            match lang {
                Hans => (format!("{tm}击杀了{d}！"), format!("全队{fx}（共 {n} 条{}）", if soon { "，再拿 1 条获得龙魂" } else { "" })),
                Hant => (format!("{tm}擊殺了{d}！"), format!("全隊{fx}（共 {n} 隻{}）", if soon { "，再拿 1 隻獲得龍魂" } else { "" })),
                En => (format!("{tm} has slain the {d}!"),
                       format!("{fx} for the whole team ({n} drake{}{})", if n == 1 { "" } else { "s" },
                               if soon { ", one more for the Dragon Soul" } else { "" })),
                Ko => (format!("{tm}이 {d}을 처치했습니다!"),
                       format!("팀 전체 {fx} (총 {n}마리{})", if soon { ", 1마리 더 잡으면 드래곤의 영혼" } else { "" })),
                Ja => (format!("{tm}が{d}を倒しました！"),
                       format!("チーム全体に {fx}（計 {n} 体{}）", if soon { "、あと 1 体でドラゴンソウル" } else { "" })),
            }
        }
        What::Soul { team: t, element } => {
            let (tm, s, fx) = (team(lang, *t), soul(lang, *element), soul_effect(lang, *element));
            match lang {
                Hans => (format!("{tm}获得了{s}！"), fx),
                Hant => (format!("{tm}獲得了{s}！"), fx),
                En => (format!("{tm} has claimed the {s}!"), fx),
                Ko => (format!("{tm}이 {s}을 획득했습니다!"), fx),
                Ja => (format!("{tm}が{s}を獲得しました！"), fx),
            }
        }
        What::ElderKilled { team: t, holders: ids } => {
            let (s, p) = (secs(super::settings::elder_t()), rules::EXECUTE_PCT);
            let (tm, w) = (team(lang, *t), holders(lang, ids, name));
            match lang {
                Hans => (format!("{tm}击杀了远古巨龙！"), format!("{w}获得远古龙之力 {s} 秒：点燃敌方英雄，生命低于 {p}% 时斩杀")),
                Hant => (format!("{tm}擊殺了遠古巨龍！"), format!("{w}獲得遠古龍之力 {s} 秒：點燃敵方英雄，生命低於 {p}% 時斬殺")),
                En => {
                    let fx = format!("Aspect of the Dragon for {s} s: burn enemy champions, execute them below {p}% health");
                    (format!("{tm} has slain the Elder Dragon!"),
                     if w.is_empty() { fx } else { format!("{w}: Aspect of the Dragon for {s} s - burn enemy champions, execute them below {p}% health") })
                }
                Ko => {
                    let fx = format!("장로 드래곤의 힘 {s}초 — 적 챔피언을 불태우고 체력 {p}% 미만이면 처형");
                    (format!("{tm}이 장로 드래곤을 처치했습니다!"), if w.is_empty() { fx } else { format!("{w}: {fx}") })
                }
                Ja => {
                    let fx = format!("エルダードラゴンの力 {s} 秒 — 敵チャンピオンを燃やし、体力 {p}% 未満で処刑");
                    (format!("{tm}がエルダードラゴンを倒しました！"), if w.is_empty() { fx } else { format!("{w}：{fx}") })
                }
            }
        }
        What::Execute { killer, victim, .. } => {
            let (k, v) = (name(killer), name(victim));
            match lang {
                Hans => (format!("远古龙之力：{k} 斩杀了 {v}！"), none()),
                Hant => (format!("遠古龍之力：{k} 斬殺了 {v}！"), none()),
                En => (format!("Aspect of the Dragon: {k} executed {v}!"), none()),
                Ko => (format!("장로 드래곤의 힘: {k} → {v} 처형!"), none()),
                Ja => (format!("エルダードラゴンの力：{k} が {v} を処刑！"), none()),
            }
        }
        What::BaronKilled { team: t, holders: ids } => {
            let (s, p, r, a) = (secs(super::settings::baron_t()), rules::BARON_PCT, rules::MINION_REDUCE, rules::MINION_ATTACK);
            let (tm, w) = (team(lang, *t), holders(lang, ids, name));
            match lang {
                Hans => (format!("{tm}击杀了纳什男爵！小兵得到强化"),
                         format!("{w}获得纳什男爵之手 {s} 秒：攻击力、法强 +{p}%，身边的己方小兵受到的伤害 -{r}%、攻击力 +{a}%")),
                Hant => (format!("{tm}擊殺了巴龍！小兵得到強化"),
                         format!("{w}獲得巴龍之手 {s} 秒：攻擊力、法強 +{p}%，身邊的己方小兵受到的傷害 -{r}%、攻擊力 +{a}%")),
                En => {
                    let fx = format!("Hand of Baron for {s} s - +{p}% attack damage and ability power, minions near them take {r}% less \
                                      damage and hit {a}% harder");
                    (format!("{tm} has slain Baron Nashor! Minions empowered"), if w.is_empty() { fx } else { format!("{w}: {fx}") })
                }
                Ko => {
                    let fx = format!("내셔 남작의 손아귀 {s}초 — 공격력, 주문력 +{p}%, 주변 아군 미니언이 받는 피해 -{r}%, 공격력 +{a}%");
                    (format!("{tm}이 내셔 남작을 처치했습니다! 미니언 강화"), if w.is_empty() { fx } else { format!("{w}: {fx}") })
                }
                Ja => {
                    let fx = format!("ハンド・オブ・バロン {s} 秒 — 攻撃力と魔力 +{p}%、周囲の味方ミニオンの被ダメージ -{r}%、攻撃力 +{a}%");
                    (format!("{tm}がバロンナッシャーを倒しました！ミニオン強化"), if w.is_empty() { fx } else { format!("{w}：{fx}") })
                }
            }
        }
        What::Rift { element } => {
            let (rf, fx) = (rift(lang, *element), rift_effect(lang, *element));
            match lang {
                Hans => (format!("峡谷变成了{rf}！"), fx),
                Hant => (format!("峽谷變成了{rf}！"), fx),
                En => (format!("The rift has turned into the {rf}!"), fx),
                Ko => (format!("협곡이 {rf}으로 바뀌었습니다!"), fx),
                Ja => (format!("リフトが{rf}に変わりました！"), fx),
            }
        }
        What::Conflict => match lang {
            Hans => ("检测到创意工坊模组 Elemental Drakes & Baron".into(), "请在模组列表里关掉它，本模组的龙才会生效".into()),
            Hant => ("偵測到創意工坊模組 Elemental Drakes & Baron".into(), "請在模組列表裡關掉它，本模組的龍才會生效".into()),
            En => ("Workshop mod \"Elemental Drakes & Baron\" detected".into(), "Turn it off in the mod list for League's dragons to work".into()),
            Ko => ("창작마당 모드 Elemental Drakes & Baron 감지됨".into(), "모드 목록에서 끄면 이 모드의 드래곤이 작동합니다".into()),
            Ja => ("ワークショップMOD「Elemental Drakes & Baron」を検出".into(), "MOD一覧でオフにすると、このMODのドラゴンが有効になります".into()),
        },
    }
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
        (Lang::Ko, true) => format!("{d} 등장"),
        (Lang::Ko, false) => format!("다음: {d}"),
        (Lang::Ja, true) => format!("{d} 出現中"),
        (Lang::Ja, false) => format!("次：{d}"),
    }
}

/// HUD 顶上一行：龙魂会是哪种元素（峡谷的元素，这一局的第三种），还没有哪一队拿到龙魂时写（用户：「龙魂是哪条元素的龙也没提示」）。
pub fn soul_hint(lang: Lang, e: Element) -> String {
    let el = element(lang, e);
    pick(lang, format!("龙魂：{el}"), format!("龍魂：{el}"), format!("Soul: {el}"), format!("드래곤의 영혼: {el}"),
         format!("ドラゴンソウル：{el}"))
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
            pick(lang, format!("攻击力、法强 +{p}%"), format!("攻擊力、法強 +{p}%"), format!("+{p}% attack damage and ability power"),
                 format!("공격력, 주문력 +{p}%"), format!("攻撃力と魔力 +{p}%"))
        }
        Element::Mountain => {
            let p = b.defence_mult;
            pick(lang, format!("护甲、魔抗 +{p}%"), format!("護甲、魔抗 +{p}%"), format!("+{p}% armor and magic resist"),
                 format!("방어력, 마법 저항력 +{p}%"), format!("物理防御と魔法防御 +{p}%"))
        }
        Element::Ocean => {
            let (s, p) = (secs(rules::OCEAN_EVERY), rules::OCEAN_PCT * n as usize);
            pick(lang, format!("每 {s} 秒回复 {p}% 已损生命"), format!("每 {s} 秒回復 {p}% 已損生命"),
                 format!("{p}% missing health back every {s} s"), format!("{s}초마다 잃은 체력의 {p}% 회복"),
                 format!("{s} 秒ごとに失った体力の {p}% を回復"))
        }
        Element::Cloud => {
            let p = b.move_speed_mult;
            pick(lang, format!("移速 +{p}%"), format!("移速 +{p}%"), format!("+{p}% move speed"), format!("이동 속도 +{p}%"),
                 format!("移動速度 +{p}%"))
        }
        Element::Hextech => {
            let a = b.attack_speed_mult;
            pick(lang, format!("攻速 +{a}%、技能冷却更快"), format!("攻速 +{a}%、技能冷卻更快"),
                 format!("+{a}% attack speed, faster cooldowns"), format!("공격 속도 +{a}%, 스킬 재사용 대기시간 감소"),
                 format!("攻撃速度 +{a}%、スキルのクールダウン短縮"))
        }
        Element::Chemtech => {
            let (t, v) = (b.toughness, b.vamp);
            pick(lang, format!("韧性 +{t}%、生命偷取 +{v}%"), format!("韌性 +{t}%、生命偷取 +{v}%"),
                 format!("+{t}% tenacity, +{v}% life steal"), format!("강인함 +{t}%, 생명력 흡수 +{v}%"),
                 format!("行動妨害耐性 +{t}%、ライフスティール +{v}%"))
        }
        Element::Elder => String::new(),
    }
}

/// 鼠标停在 HUD 上时的说明框：每一行 (文字, 颜色 0xRRGGBBAA, 粗体)。两队现在的加成、每种元素每层的加成、龙魂、远古巨龙、
/// 纳什男爵（用户：「这个面板里面我也看不到详细的小龙加成说明 起码也要做到我悬浮的时候 有个说明框吧」）。
pub fn tip_lines(lang: Lang, rec: &rules::Record, terrain: Option<Element>) -> Vec<(String, u32, bool)> {
    const GOLD: u32 = 0xff_d8_8a_ff;
    const DIM: u32 = 0xa8_a4_9c_ff;
    let c = colon(lang);
    let mut out = vec![(pick(lang, "元素亚龙：拿下后全队永久加成，可以叠加", "元素亞龍：拿下後全隊永久加成，可以疊加",
                             "Elemental drakes: a permanent bonus for the whole team, stacking",
                             "원소 드래곤: 처치하면 팀 전체에 영구 보너스, 중첩 가능",
                             "エレメンタルドラゴン：倒すとチーム全体に永続ボーナス、重複可").to_string(), GOLD, true)];
    let sep = pick(lang, "、", "、", ", ", ", ", "、");
    let (lp, rp) = if lang == Lang::Ko { (" (", ")") } else { ("（", "）") };
    for t in 0..2 {
        let mut parts = Vec::new();
        for e in rules::DRAKES {
            let n = rec.stacks[t][e.slot().unwrap_or(0)];
            if n > 0 {
                parts.push(format!("{} ×{n}{lp}{}{rp}", element(lang, e), stack_total(lang, e, n)));
            }
        }
        let have = if parts.is_empty() {
            pick(lang, "还没有", "還沒有", "none yet", "아직 없음", "まだなし").to_string()
        } else {
            parts.join(sep)
        };
        out.push((format!("{}{c}{have}", team(lang, t)), if t == 0 { 0x8c_9c_ff_ff } else { 0xff_8c_96_ff }, false));
    }
    out.push((pick(lang, "每一层：", "每一層：", "Each stack:", "1중첩마다:", "1 スタックごと：").to_string(), DIM, false));
    for e in rules::DRAKES {
        out.push((format!("  {}  {}", drake(lang, e), stack_effect(lang, e)), colour_text(e), false));
    }
    match rec.soul.and_then(|(t, c)| Element::from_code(c).map(|e| (t, e))) {
        Some((t, e)) => {
            let (tm, s, fx) = (team(lang, t), soul(lang, e), soul_effect(lang, e));
            let line = match lang {
                Lang::Hans | Lang::Hant => format!("{tm}拿到了{s}：{fx}"),
                Lang::En => format!("{tm} claimed {s}：{fx}"),
                Lang::Ko => format!("{tm} {s} 획득: {fx}"),
                Lang::Ja => format!("{tm}が{s}を獲得：{fx}"),
            };
            out.push((line, colour_text(e), false));
        }
        None => {
            if let Some(e) = rec.soul_shown() {
                out.push((format!("{}{lp}{}{rp}{c}{}", soul(lang, e),
                                  pick(lang, "先拿满 4 条元素亚龙的一队获得", "先拿滿 4 隻元素亞龍的一隊獲得", "the first team to 4 drakes",
                                       "원소 드래곤 4마리를 먼저 잡은 팀이 획득", "エレメンタルドラゴンを先に 4 体倒したチームが獲得"),
                                  soul_effect(lang, e)), colour_text(e), false));
            }
        }
    }
    // the rift's terrain, once it has changed (only on the game's own 5v5 map)
    if let Some(e) = terrain {
        out.push((format!("{}{c}{}", rift(lang, e), rift_effect(lang, e)), colour_text(e), false));
    }
    let (s, p) = (secs(super::settings::elder_t()), rules::EXECUTE_PCT);
    out.push((pick(lang, format!("远古巨龙：龙魂之后刷新；击杀后 {s} 秒点燃敌方英雄，生命低于 {p}% 时斩杀"),
                     format!("遠古巨龍：龍魂之後刷新；擊殺後 {s} 秒點燃敵方英雄，生命低於 {p}% 時斬殺"),
                     format!("Elder Dragon: after a soul; its takers burn enemy champions for {s} s, executing below {p}%"),
                     format!("장로 드래곤: 드래곤의 영혼 이후 등장. 처치하면 {s}초 동안 적 챔피언을 불태우고 체력 {p}% 미만이면 처형"),
                     format!("エルダードラゴン：ドラゴンソウルの後に出現。倒すと {s} 秒間、敵チャンピオンを燃やし体力 {p}% 未満で処刑")),
              colour_text(Element::Elder), false));
    let (s, p, r, a) = (secs(super::settings::baron_t()), rules::BARON_PCT, rules::MINION_REDUCE, rules::MINION_ATTACK);
    out.push((pick(lang, format!("纳什男爵之手：{s} 秒攻击力、法强 +{p}%，身边己方小兵受到的伤害 -{r}%、攻击力 +{a}%"),
                     format!("巴龍之手：{s} 秒攻擊力、法強 +{p}%，身邊己方小兵受到的傷害 -{r}%、攻擊力 +{a}%"),
                     format!("Hand of Baron: {s} s of +{p}% attack damage and ability power; minions near take {r}% less damage, hit {a}% harder"),
                     format!("내셔 남작의 손아귀: {s}초 동안 공격력, 주문력 +{p}%, 주변 아군 미니언이 받는 피해 -{r}%, 공격력 +{a}%"),
                     format!("ハンド・オブ・バロン：{s} 秒間、攻撃力と魔力 +{p}%、周囲の味方ミニオンの被ダメージ -{r}%、攻撃力 +{a}%")),
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
    pick(lang, "纳什男爵 已刷新", "巴龍 已出現", "Baron Nashor is up", "내셔 남작 등장", "バロンナッシャー出現中")
}

/// 计时的标签：远古龙之力 / 纳什男爵之手。
pub fn timer_label(lang: Lang, baron: bool) -> &'static str {
    if baron {
        pick(lang, "男爵", "巴龍", "Baron", "남작", "バロン")
    } else {
        pick(lang, "远古", "遠古", "Elder", "장로", "エルダー")
    }
}

/// 一队什么都还没有。
pub const NOTHING: &str = "—";

/// 撞上创意工坊的大小龙 mod 时 HUD 上一直写着的。
pub fn conflict_line(lang: Lang) -> &'static str {
    pick(lang, "创意工坊的 Elemental Drakes & Baron 开着：本模组的龙不生效",
         "創意工坊的 Elemental Drakes & Baron 開著：本模組的龍不生效",
         "Workshop \"Elemental Drakes & Baron\" is on: League's dragons are off",
         "창작마당의 Elemental Drakes & Baron이 켜져 있음: 이 모드의 드래곤이 작동하지 않음",
         "ワークショップの「Elemental Drakes & Baron」が有効：このMODのドラゴンは無効")
}

#[cfg(test)]
mod tests {
    #[test]
    fn the_tooltip_says_each_teams_bonus_the_soul_and_the_epic_monsters() {
        let mut r = rules::Record { order: [6, 3, 2], ..rules::Record::default() };
        r.stacks[1] = [0, 0, 0, 0, 0, 1];           // red: one chemtech
        r.stacks[0] = [2, 0, 0, 0, 0, 0];           // blue: two infernal
        let lines: Vec<String> = tip_lines(Lang::Hans, &r, None).into_iter().map(|l| l.0).collect();
        let all = lines.join("\n");
        assert!(all.contains("蓝色方：炼狱 ×2（攻击力、法强 +16%）") || all.contains("蓝方：炼狱 ×2（攻击力、法强 +16%）"), "{all}");
        assert!(all.contains("化学科技 ×1（韧性 +"), "{all}");
        assert!(all.contains("山脉龙魂（先拿满 4 条元素亚龙的一队获得）"), "{all}");
        assert!(all.contains("远古巨龙：龙魂之后刷新") && all.contains("纳什男爵之手："), "{all}");
        assert_eq!(soul_hint(Lang::Hans, Element::Mountain), "龙魂：山脉");
        // Korean and Japanese: the same lines in their words (Korean with half-width punctuation)
        let ko = tip_lines(Lang::Ko, &r, None).into_iter().map(|l| l.0).collect::<Vec<_>>().join("\n");
        assert!(ko.contains("블루 팀: 화염 ×2 (공격력, 주문력 +16%)") && ko.contains("대지의 영혼 (원소 드래곤 4마리를"), "{ko}");
        let ja = tip_lines(Lang::Ja, &r, None).into_iter().map(|l| l.0).collect::<Vec<_>>().join("\n");
        assert!(ja.contains("ブルーチーム：インファーナル ×2（攻撃力と魔力 +16%）") && ja.contains("マウンテンソウル（"), "{ja}");
        assert_eq!((soul_hint(Lang::Ko, Element::Ocean), soul_hint(Lang::Ja, Element::Cloud)),
                   ("드래곤의 영혼: 바다".to_string(), "ドラゴンソウル：クラウド".to_string()));
        // the soul's element only once the second drake is taken, as in League (the user: 「改成第二条死后显示」)
        let early = |taken: [u8; 6], alive: bool| {
            let mut e = rules::Record { order: [6, 3, 2], serpen_alive: alive, ..rules::Record::default() };
            e.stacks[0] = taken;
            tip_lines(Lang::Hans, &e, None).into_iter().map(|l| l.0).collect::<Vec<_>>().join("\n")
        };
        assert!(!early([0; 6], true).contains("龙魂（"), "the first drake");
        assert!(!early([1, 0, 0, 0, 0, 0], true).contains("龙魂（"), "one taken, the second alive");
        assert!(early([1, 0, 0, 0, 0, 1], false).contains("山脉龙魂（"), "two taken, the third not out yet");
        // a soul claimed: who has it instead of the hint
        r.soul = Some((1, 2));
        let all: String = tip_lines(Lang::Hans, &r, None).into_iter().map(|l| l.0).collect::<Vec<_>>().join("\n");
        assert!(all.contains("拿到了山脉龙魂："), "{all}");
        let ko: String = tip_lines(Lang::Ko, &r, None).into_iter().map(|l| l.0).collect::<Vec<_>>().join("\n");
        assert!(ko.contains("레드 팀 대지의 영혼 획득: "), "{ko}");
        // the rift's terrain once it has turned (the game's own 5v5 map): its own line, in every language
        assert!(!all.contains("峡谷："), "{all}");
        let with = |lang| tip_lines(lang, &r, Some(Element::Cloud)).into_iter().map(|l| l.0).collect::<Vec<_>>();
        assert!(with(Lang::Hans).contains(&"云端峡谷：河道和野区吹起风道：英雄在风道里移速 +20%".to_string()), "{:?}", with(Lang::Hans));
        assert!(with(Lang::Hant).iter().any(|l| l.starts_with("雲端峽谷：")) && with(Lang::En).iter().any(|l| l.starts_with("Cloud Rift:") || l.starts_with("Cloud Rift：")));
        assert!(with(Lang::Ko).iter().any(|l| l.starts_with("바람의 협곡: ")) && with(Lang::Ja).iter().any(|l| l.starts_with("クラウドリフト：")),
                "{:?} {:?}", with(Lang::Ko), with(Lang::Ja));
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
            v.push(What::Rift { element: e });
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

    /// The rift's turn: its name and what its terrain does, the numbers from rift.rs.
    #[test]
    fn the_rifts_turn_is_announced_with_what_it_does() {
        let n = |lang, e| notice(lang, &What::Rift { element: e }, &name);
        assert_eq!(n(Lang::Hans, Element::Cloud),
                   ("峡谷变成了云端峡谷！".to_string(), "河道和野区吹起风道：英雄在风道里移速 +20%".to_string()));
        assert_eq!(n(Lang::Hans, Element::Hextech).1,
                   "野区和龙坑、男爵坑旁出现成对的传送门：脱战时朝着另一头走上去就传过去（每人 20 秒一次）");
        assert_eq!(n(Lang::Hant, Element::Mountain), ("峽谷變成了山脈峽谷！".to_string(), "河道口和野區出現碎石堆：英雄走在上面移速 -30%".to_string()));
        assert_eq!(n(Lang::En, Element::Ocean).0, "The rift has turned into the Ocean Rift!");
        assert_eq!(n(Lang::Ko, Element::Cloud),
                   ("협곡이 바람의 협곡으로 바뀌었습니다!".to_string(), "강가와 정글에 바람길이 생김: 바람길 안에서 이동 속도 +20%".to_string()));
        assert_eq!(n(Lang::Ko, Element::Hextech).0, "협곡이 마법공학 협곡으로 바뀌었습니다!");
        assert_eq!(n(Lang::Ja, Element::Mountain),
                   ("リフトがマウンテンリフトに変わりました！".to_string(), "巣の入り口とジャングルに瓦礫の山が現れる：その上では移動速度 -30%".to_string()));
        // 0.5.16 起炼狱也有效果了（坑边火圈）
        assert_eq!(n(Lang::Hans, Element::Infernal),
                   ("峡谷变成了炼狱峡谷！".to_string(), "龙坑和男爵坑周围燃起火圈：英雄在火圈里攻击力和法强 +15%".to_string()));
        assert_eq!(n(Lang::En, Element::Infernal).1, "rings of fire round the dragon and Baron pits: +15% attack damage and ability power inside them");
        for e in rules::DRAKES {
            for lang in Lang::ALL {
                assert!(!rift_effect(lang, e).is_empty() && rift(lang, e).contains(element(lang, e)));
            }
        }
        assert!(rift_effect(Lang::En, Element::Elder).is_empty());
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

    /// 韩语、日语（0.5.10，用户「加上韩语日语」）：韩服、日服的叫法，数字和中文一样。
    #[test]
    fn korean_and_japanese_too() {
        let ko = |w: What| notice(Lang::Ko, &w, &name);
        assert_eq!(ko(What::Drake { team: 1, element: Element::Mountain, total: 1 }),
                   ("레드 팀이 대지의 드래곤을 처치했습니다!".to_string(), "팀 전체 방어력, 마법 저항력 +10% (총 1마리)".to_string()));
        assert_eq!(ko(What::Drake { team: 0, element: Element::Ocean, total: 3 }).1,
                   "팀 전체 5초마다 잃은 체력의 3% 회복 (총 3마리, 1마리 더 잡으면 드래곤의 영혼)");
        assert_eq!(ko(What::DrakeSpawn { element: Element::Hextech }),
                   ("마법공학 드래곤이 등장했습니다!".to_string(), "처치하면 팀 전체 공격 속도 +10%, 스킬 재사용 대기시간 -8%".to_string()));
        assert_eq!(ko(What::Soul { team: 0, element: Element::Infernal }).0, "블루 팀이 화염의 영혼을 획득했습니다!");
        assert_eq!(ko(What::BaronKilled { team: 0, holders: vec![] }).0, "블루 팀이 내셔 남작을 처치했습니다! 미니언 강화");
        assert_eq!(ko(What::ElderKilled { team: 1, holders: vec!["league_jinx".into(), "league_garen".into()] }).1,
                   "金克丝, 盖伦: 장로 드래곤의 힘 90초 — 적 챔피언을 불태우고 체력 20% 미만이면 처형");
        assert_eq!(ko(What::Execute { team: 0, killer: "league_jinx".into(), victim: "league_garen".into() }).0,
                   "장로 드래곤의 힘: 金克丝 → 盖伦 처형!");
        let five: Vec<String> = ["a", "b", "c", "d", "e"].iter().map(|x| x.to_string()).collect();
        assert!(ko(What::BaronKilled { team: 1, holders: five.clone() }).1.starts_with("팀 전체: 내셔 남작의 손아귀 120초 — 공격력, 주문력 +20%"));
        let ja = |w: What| notice(Lang::Ja, &w, &name);
        assert_eq!(ja(What::Drake { team: 0, element: Element::Cloud, total: 1 }),
                   ("ブルーチームがクラウドドラゴンを倒しました！".to_string(), "チーム全体に 移動速度 +8%（計 1 体）".to_string()));
        assert_eq!(ja(What::Drake { team: 1, element: Element::Chemtech, total: 3 }).1,
                   "チーム全体に 行動妨害耐性 +10%、ライフスティール +3%（計 3 体、あと 1 体でドラゴンソウル）");
        assert_eq!(ja(What::ElderSpawn).0, "エルダードラゴンが出現しました！");
        assert_eq!(ja(What::Soul { team: 1, element: Element::Ocean }).0, "レッドチームがオーシャンソウルを獲得しました！");
        assert_eq!(ja(What::BaronKilled { team: 1, holders: vec!["league_ahri".into()] }).1,
                   "阿狸：ハンド・オブ・バロン 120 秒 — 攻撃力と魔力 +20%、周囲の味方ミニオンの被ダメージ -40%、攻撃力 +30%");
        assert!(ja(What::BaronKilled { team: 1, holders: five }).1.starts_with("チーム全員：ハンド・オブ・バロン"));
        assert_eq!(ja(What::Execute { team: 1, killer: "league_ahri".into(), victim: "league_jinx".into() }).0,
                   "エルダードラゴンの力：阿狸 が 金克丝 を処刑！");
        // the HUD's own words
        assert_eq!((dragon_status(Lang::Ko, Element::Elder, true), dragon_status(Lang::Ja, Element::Infernal, false)),
                   ("장로 드래곤 등장".to_string(), "次：インファーナルドラゴン".to_string()));
        assert_eq!((baron_status(Lang::Ko), baron_status(Lang::Ja)), ("내셔 남작 등장", "バロンナッシャー出現中"));
        assert_eq!((team_tag(Lang::Ko, 0), team_tag(Lang::Ja, 1)), ("블루", "レッド"));
        assert_eq!((drake(Lang::Ko, Element::Chemtech), soul(Lang::Ko, Element::Cloud)), ("화학공학 드래곤".to_string(), "바람의 영혼".to_string()));
    }

    #[test]
    fn every_notice_has_a_title_in_every_language() {
        let hangul = |s: &str| s.chars().any(|c| ('\u{ac00}'..='\u{d7a3}').contains(&c));
        let kana = |s: &str| s.chars().any(|c| ('\u{3040}'..='\u{30ff}').contains(&c));
        for w in all_whats() {
            for lang in Lang::ALL {
                let (t, d) = notice(lang, &w, &name);
                assert!(!t.is_empty(), "{w:?} {lang:?}");
                assert!(!t.contains('{') && !d.contains('{') && !t.contains("league_"), "{w:?} {lang:?}: {t} / {d}");
                // only the execute has no second line
                assert_eq!(d.is_empty(), matches!(w, What::Execute { .. }), "{w:?} {lang:?}");
                // Korean is in hangul, Japanese in kana, the others in neither
                assert_eq!(hangul(&t), lang == Lang::Ko, "{w:?} {lang:?}: {t}");
                assert_eq!(kana(&t), lang == Lang::Ja, "{w:?} {lang:?}: {t}");
            }
        }
    }

    #[test]
    fn element_words_cover_every_element() {
        for e in rules::DRAKES.into_iter().chain([Element::Elder]) {
            for lang in Lang::ALL {
                assert!(!element(lang, e).is_empty() && !glyph(lang, e).is_empty());
                assert!(!drake(lang, e).is_empty() && !dragon_status(lang, e, true).is_empty());
                if e != Element::Elder {
                    assert!(!stack_effect(lang, e).is_empty() && !soul_effect(lang, e).is_empty() && !stack_total(lang, e, 3).is_empty());
                }
            }
        }
        // the glyphs of one language tell the elements apart
        for lang in Lang::ALL {
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
        assert_eq!(lang_of("내셔 남작", "Avengerang"), Lang::Ko);
        assert_eq!(lang_of("バロンナッシャー", "去而复还"), Lang::Ja);
        // our names not there (another language, or the texts not installed): Akshan's skill name decides
        assert_eq!(lang_of("莫尔加德", "去而复还"), Lang::Hans);
        assert_eq!(lang_of("Morgard", "復仇迴力鏢"), Lang::Hant);
        assert_eq!(lang_of("모르가드", "복수의 부메랑"), Lang::Ko);
        assert_eq!(lang_of("モルガード", "アヴェンジャラン"), Lang::Ja);
        assert_eq!(lang_of("", "Avengerang"), Lang::En);
        // no League Heroes: the game's own champions' texts
        assert_eq!(lang_of("Morgard", "幽靈 亡靈法師 護盾衛士"), Lang::Hant);
        assert_eq!(lang_of("莫尔加德", "幽灵 亡灵法师 护盾卫士"), Lang::Hans);
        assert!(named_by_us("纳什男爵") && named_by_us("巴龍") && named_by_us("Baron Nashor") && !named_by_us("Morgard"));
        assert!(named_by_us("내셔 남작") && named_by_us("バロンナッシャー") && !named_by_us("모르가드") && !named_by_us("モルガード"));
    }
}
