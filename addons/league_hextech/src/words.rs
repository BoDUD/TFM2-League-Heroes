//! 屏幕上的字：简体、繁体、英文、韩语、日语（0.3.3 加韩语、日语，用户：「加上韩语日语」），别的语言用英文。认语言的办法和大小龙
//! 一样，看游戏自己的英雄名和技能名的写法（本包没有改游戏的文字）。海克斯的名字和效果在 [`super::augments`]（简繁英）和
//! [`super::kj`]（韩日）。
//!
//! 韩语、日语照英雄联盟韩服、日服的叫法：海克斯 = 증강 / オーグメント，刷新 = 새로고침 / リロール，队伍照游戏自己的
//! 「블루 / 레드」「ブルー / レッド」。

use super::augments::{Tier, AUGS};

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

    /// 海克斯表（简繁英三份）里的第几份；韩语、日语不在那张表里（[`super::kj`]）。
    pub fn index(self) -> usize {
        match self {
            Lang::Hans => 0,
            Lang::Hant => 1,
            _ => 2,
        }
    }
}

/// 按游戏自己的一段文字认语言：有韩文是韩语，有日文假名是日语；中文里繁体特有的字比简体特有的多就是繁体；别的都是英文。
pub fn lang_of(sample: &str) -> Lang {
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

/// 繁体才这样写的字，和它们的简体（英雄名、技能名里常见的）。
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

pub fn tier(lang: Lang, t: Tier) -> &'static str {
    match t {
        Tier::Silver => pick(lang, "银", "銀", "Silver", "실버", "シルバー"),
        Tier::Gold => pick(lang, "金", "金", "Gold", "골드", "ゴールド"),
        Tier::Prismatic => pick(lang, "棱彩", "稜彩", "Prismatic", "프리즘", "プリズム"),
    }
}

pub fn side(lang: Lang, team: usize) -> &'static str {
    if team == 0 {
        pick(lang, "蓝色方", "藍色方", "Blue", "블루", "ブルー")
    } else {
        pick(lang, "红色方", "紅色方", "Red", "레드", "レッド")
    }
}

pub fn name(lang: Lang, aug: usize) -> &'static str {
    match (lang, super::kj::of(aug)) {
        (Lang::Ko, Some(k)) => k.ko[0],
        (Lang::Ja, Some(k)) => k.ja[0],
        _ => AUGS[aug].name[lang.index()],
    }
}

pub fn desc(lang: Lang, aug: usize) -> &'static str {
    match (lang, super::kj::of(aug)) {
        (Lang::Ko, Some(k)) => k.ko[1],
        (Lang::Ja, Some(k)) => k.ja[1],
        _ => AUGS[aug].desc[lang.index()],
    }
}

/// 一个字大约多宽（以字号为单位，[`super::screen::em`] 一样的算法）。
fn char_em(c: char) -> f32 {
    if (c as u32) >= 0x2e80 {
        1.0
    } else if c == ' ' {
        0.3
    } else {
        0.56
    }
}

/// 这个字后面能断行（标点、空格）。
fn breaks_after(c: char) -> bool {
    matches!(c, '，' | '：' | '；' | '。' | '、' | '）' | ',' | ':' | ';' | ')' | ' ' | '.')
}

/// 不能放在行首的（逗号、句号、右括号……）：跟着上一行走。
fn closing(c: char) -> bool {
    matches!(c, '，' | '：' | '；' | '。' | '、' | '）' | ',' | ':' | ';' | ')' | '.' | '%')
}

/// 把一段说明折成几行，每行大约不超过 `max_em`（字号为单位）：在标点、空格后面断（离行首太近的不算），没有就在这里断
/// （中文任意两个字之间都能断）；标点不放在行首。0.3.0 的触发类说明长，卡片和说明框里折成两三行。
pub fn wrap(text: &str, max_em: f32) -> Vec<String> {
    let chars: Vec<char> = text.chars().collect();
    let mut lines = Vec::new();
    let mut start = 0;
    while start < chars.len() {
        while start < chars.len() && chars[start] == ' ' {
            start += 1;
        }
        if start >= chars.len() {
            break;
        }
        let (mut w, mut end, mut good) = (0.0f32, start, None);
        while end < chars.len() {
            let cw = char_em(chars[end]);
            if w + cw > max_em && end > start {
                break;
            }
            w += cw;
            if breaks_after(chars[end]) {
                good = Some(end + 1);
            }
            end += 1;
        }
        if end < chars.len() {
            let latin = (chars[end] as u32) < 0x2e80 && chars[end] != ' ';
            end = match good {
                // 在标点、空格后面断：不太靠近行首的（英文单词不拆开：有空格就在空格处）
                Some(g) if (g - start) * 2 >= end - start || (latin && chars[end - 1] != ' ') => g,
                _ => end,
            };
            while end < chars.len() && closing(chars[end]) {
                end += 1;
            }
        }
        let line: String = chars[start..end].iter().collect();
        lines.push(line.trim_end().to_string());
        start = end;
    }
    lines
}

/// 折成最多 `n` 行，每行差不多一样长（卡片上用）。
pub fn wrap_in(text: &str, n: usize) -> Vec<String> {
    let total: f32 = text.chars().map(char_em).sum();
    let mut max = (total / n.max(1) as f32).ceil().max(1.0);
    loop {
        let lines = wrap(text, max);
        if lines.len() <= n || max > total {
            return lines;
        }
        max += 0.5;
    }
}

/// 一行的长度（字号为单位）。
pub fn line_em(text: &str) -> f32 {
    text.chars().map(char_em).sum()
}

/// 只有一行地方时的说明：短的原样；长的（触发类）取到第一个冒号或逗号，后面「…」（开局面板、提示里用，全文在说明框和 BP 卡片上）。
pub fn brief(lang: Lang, aug: usize) -> String {
    let d = desc(lang, aug);
    if line_em(d) <= 20.0 {
        return d.to_string();
    }
    let chars: Vec<char> = d.chars().collect();
    let cut = chars.iter().enumerate().skip(4)
        .find(|(_, c)| matches!(c, '：' | '，' | ':' | ',' | '。' | '（' | '('))
        .map(|(i, _)| i);
    let mut out: String = match cut {
        Some(i) => chars[..i].iter().collect(),
        None => d.to_string(),
    };
    // 还是长：取头上二十几个字宽
    if line_em(&out) > 30.0 {
        out = wrap(&out, 26.0).into_iter().next().unwrap_or_default();
    }
    let out = out.trim_end();
    if out.len() < d.len() {
        format!("{out}…")
    } else {
        out.to_string()
    }
}

/// 【金】玻璃大炮 / [Gold] Glass Cannon / [골드] 유리 대포 / 【ゴールド】グラスキャノン
pub fn tagged(lang: Lang, aug: usize) -> String {
    let t = tier(lang, AUGS[aug].tier);
    match lang {
        Lang::En | Lang::Ko => format!("[{t}] {}", name(lang, aug)),
        _ => format!("【{t}】{}", name(lang, aug)),
    }
}

/// 开局面板的标题：海克斯大乱斗 · 开局海克斯（金）
pub fn opening_title(lang: Lang, t: Tier) -> String {
    let n = tier(lang, t);
    match lang {
        Lang::Hans => format!("海克斯大乱斗 · 开局海克斯（{n}）"),
        Lang::Hant => format!("海克斯大亂鬥 · 開局海克斯（{n}）"),
        Lang::En => format!("Hextech Mayhem · Opening augments ({n})"),
        Lang::Ko => format!("헥스테크 아수라장 · 시작 증강 ({n})"),
        Lang::Ja => format!("ヘクステック・メイヘム · 開始時のオーグメント（{n}）"),
    }
}

/// 开局面板下面那一行：之后在几级再选。
pub fn opening_next(lang: Lang, levels: [usize; 3]) -> String {
    let [a, b, c] = levels;
    match lang {
        Lang::Hans => format!("之后 {a} 级、{b} 级、{c} 级各再选一次（三选一）"),
        Lang::Hant => format!("之後 {a} 級、{b} 級、{c} 級各再選一次（三選一）"),
        Lang::En => format!("Again at levels {a}, {b} and {c} (one of three)"),
        Lang::Ko => format!("이후 {a}, {b}, {c}레벨에 한 번씩 더 선택 (3개 중 1개)"),
        Lang::Ja => format!("以降、レベル {a}・{b}・{c} でもう一度ずつ選択（3 つから 1 つ）"),
    }
}

/// 提示的第一行：蓝色方 金克丝 6 级 · 【金】玻璃大炮
pub fn toast_title(lang: Lang, team: usize, hero: &str, level: u8, aug: usize) -> String {
    let (s, t) = (side(lang, team), tagged(lang, aug));
    match lang {
        Lang::En => format!("{s} {hero} (level {level}) · {t}"),
        Lang::Hans => format!("{s} {hero} {level} 级 · {t}"),
        Lang::Hant => format!("{s} {hero} {level} 級 · {t}"),
        Lang::Ko => format!("{s} {hero} {level}레벨 · {t}"),
        Lang::Ja => format!("{s} {hero} レベル {level} · {t}"),
    }
}

/// 三张候选（刷新过的写出来）：三选一：钝器 / 玻璃大炮 / 灵巧（刷新掉：铁甲）
pub fn candidates(lang: Lang, cards: [u16; 3], first: [u16; 3]) -> String {
    let names: Vec<&str> = cards.iter().map(|&c| name(lang, c as usize)).collect();
    let gone: Vec<&str> = (0..3).filter(|&i| first[i] != cards[i]).map(|i| name(lang, first[i] as usize)).collect();
    let list = names.join(" / ");
    match (lang, gone.is_empty()) {
        (Lang::Hans, true) => format!("三选一：{list}"),
        (Lang::Hans, false) => format!("三选一：{list}（刷新掉：{}）", gone.join("、")),
        (Lang::Hant, true) => format!("三選一：{list}"),
        (Lang::Hant, false) => format!("三選一：{list}（刷新掉：{}）", gone.join("、")),
        (Lang::En, true) => format!("One of: {list}"),
        (Lang::En, false) => format!("One of: {list} (rerolled: {})", gone.join(", ")),
        (Lang::Ko, true) => format!("3개 중 1개: {list}"),
        (Lang::Ko, false) => format!("3개 중 1개: {list} (새로고침: {})", gone.join(", ")),
        (Lang::Ja, true) => format!("3 つから 1 つ：{list}"),
        (Lang::Ja, false) => format!("3 つから 1 つ：{list}（リロール：{}）", gone.join("、")),
    }
}

/// 鼠标放在头像上时那一块的标题：金克丝的海克斯
pub fn tip_title(lang: Lang, hero: &str) -> String {
    match lang {
        Lang::Hans | Lang::Hant => format!("{hero}的海克斯"),
        Lang::En => format!("{hero}'s augments"),
        Lang::Ko => format!("{hero}의 증강"),
        Lang::Ja => format!("{hero}のオーグメント"),
    }
}

/// 还没到的那几次：6 级 / 9 级…
pub fn tip_pending(lang: Lang, level: usize) -> String {
    match lang {
        Lang::Hans => format!("{level} 级再选"),
        Lang::Hant => format!("{level} 級再選"),
        Lang::En => format!("next at level {level}"),
        Lang::Ko => format!("{level}레벨에 선택"),
        Lang::Ja => format!("レベル {level} で選択"),
    }
}

/// 提示后面写谁选的：玩家自己点的「（你选的）」，BP 面板上没动、按 AI 推荐的「（AI 推荐）」，比赛里 AI 选的不写。
pub fn by_note(lang: Lang, by: u8) -> &'static str {
    match by {
        2 => pick(lang, "（你选的）", "（你選的）", " (yours)", " (직접 선택)", "（自分で選択）"),
        1 => pick(lang, "（AI 推荐）", "（AI 推薦）", " (AI's pick)", " (AI 추천)", "（AI のおすすめ）"),
        _ => "",
    }
}

// ===================== BP 面板 =====================

/// 第几次：开局 / 6 级
pub fn screen_name(lang: Lang, k: usize, levels: [usize; 3]) -> String {
    if k == 0 {
        return pick(lang, "开局", "開局", "Start", "시작", "開始").to_string();
    }
    let l = levels.get(k - 1).copied().unwrap_or(0);
    match lang {
        Lang::Hans => format!("{l} 级"),
        Lang::Hant => format!("{l} 級"),
        Lang::En => format!("Level {l}"),
        Lang::Ko => format!("{l}레벨"),
        Lang::Ja => format!("レベル {l}"),
    }
}

/// 标题栏上的入口：海克斯 · 已选 2/5
pub fn bp_button(lang: Lang, touched: usize, heroes: usize) -> String {
    match lang {
        Lang::Hans => format!("海克斯 · 已选 {touched}/{heroes}"),
        Lang::Hant => format!("海克斯 · 已選 {touched}/{heroes}"),
        Lang::En => format!("Augments {touched}/{heroes}"),
        Lang::Ko => format!("증강 {touched}/{heroes}"),
        Lang::Ja => format!("オーグメント {touched}/{heroes}"),
    }
}

pub fn bp_title(lang: Lang, locked: bool) -> String {
    let t = pick(lang, "海克斯大乱斗 · 给你的英雄选海克斯", "海克斯大亂鬥 · 給你的英雄選海克斯",
                 "Hextech Mayhem · your champions' augments", "헥스테크 아수라장 · 내 챔피언의 증강",
                 "ヘクステック・メイヘム · 自分のチャンピオンのオーグメント");
    if locked {
        format!("{t}{}", pick(lang, "（比赛开始了，已锁定）", "（比賽開始了，已鎖定）", " (locked: the match has started)",
                             " (경기 시작: 잠김)", "（試合開始：ロック済み）"))
    } else {
        t.to_string()
    }
}

/// 选中的那张卡上的字：玩家点的「你选的」，按了确定的 AI 推荐「已确定」，没动的「AI 推荐」。
pub fn bp_chosen(lang: Lang, by_user: bool, confirmed: bool) -> &'static str {
    if by_user {
        pick(lang, "已选 · 你选的", "已選 · 你選的", "Picked by you", "선택됨 · 직접 선택", "選択済み · 自分で選択")
    } else if confirmed {
        pick(lang, "已选 · 已确定", "已選 · 已確定", "Picked · confirmed", "선택됨 · 확정", "選択済み · 確定")
    } else {
        pick(lang, "已选 · AI 推荐", "已選 · AI 推薦", "Picked · AI's choice", "선택됨 · AI 추천", "選択済み · AI のおすすめ")
    }
}

/// 「确定 塔莉垭」：认下这个英雄现在的 4 张，跳到下一个。
pub fn bp_confirm(lang: Lang, hero: &str) -> String {
    match lang {
        Lang::Hans => format!("确定 {hero}"),
        Lang::Hant => format!("確定 {hero}"),
        Lang::En => format!("Confirm {hero}"),
        Lang::Ko => format!("{hero} 확정"),
        Lang::Ja => format!("{hero} を確定"),
    }
}

pub fn bp_confirmed(lang: Lang) -> &'static str {
    pick(lang, "已确定 ✓", "已確定 ✓", "Confirmed ✓", "확정됨 ✓", "確定 ✓")
}

pub fn bp_confirm_all(lang: Lang) -> &'static str {
    pick(lang, "全部确定", "全部確定", "Confirm all", "모두 확정", "すべて確定")
}

/// 刷新按钮上的字：刷新 / 已刷新 / 无可换（这一档的卡都在这个英雄的四次里了）。
pub fn bp_reroll(lang: Lang, used: bool, left: bool) -> &'static str {
    if used {
        pick(lang, "已刷新", "已刷新", "Rerolled", "새로고침됨", "リロール済み")
    } else if !left {
        pick(lang, "无可换", "無可換", "None left", "남은 카드 없음", "残りなし")
    } else {
        pick(lang, "刷新", "刷新", "Reroll", "새로고침", "リロール")
    }
}

pub fn bp_ai(lang: Lang) -> &'static str {
    pick(lang, "这个英雄全部按 AI 推荐", "這個英雄全部按 AI 推薦", "All AI picks for this one", "이 챔피언은 모두 AI 추천으로",
         "このチャンピオンはすべて AI のおすすめに")
}

pub fn bp_hint(lang: Lang) -> &'static str {
    pick(lang, "点卡片选中 · 每张卡能刷新一次 · 没动过的按 AI 推荐 · 选好按确定 · 比赛开始后锁定 · F7 开关",
         "點卡片選中 · 每張卡能刷新一次 · 沒動過的按 AI 推薦 · 選好按確定 · 比賽開始後鎖定 · F7 開關",
         "Click a card to pick it · each card rerolls once · untouched picks are the AI's · confirm when done · F7",
         "카드를 눌러 선택 · 카드마다 새로고침 1회 · 손대지 않은 건 AI 추천 · 다 고르면 확정 · 경기 시작 후 잠김 · F7",
         "カードをクリックで選択 · 各カード 1 回リロール可 · 触らなければ AI のおすすめ · 選んだら確定 · 試合開始後はロック · F7")
}

pub fn bp_turn(lang: Lang) -> &'static str {
    pick(lang, "轮到你选英雄了：先关掉面板（F7）", "輪到你選英雄了：先關掉面板（F7）", "Your turn to pick: close the panel first (F7)",
         "챔피언을 고를 차례입니다: 먼저 패널을 닫으세요 (F7)", "チャンピオンを選ぶ番です：先にパネルを閉じてください（F7）")
}

pub fn bp_none(lang: Lang) -> &'static str {
    pick(lang, "还没选英雄：选好了就能给他选海克斯", "還沒選英雄：選好了就能給他選海克斯", "No champion picked yet",
         "아직 고른 챔피언이 없습니다", "まだチャンピオンが選ばれていません")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn long_descriptions_fold_into_lines() {
        let fb = crate::augments::by_key("firebrand").unwrap();
        let d = desc(Lang::Hans, fb);
        for n in 1..=3 {
            let lines = wrap_in(d, n);
            assert!(lines.len() <= n, "{n}: {lines:?}");
            assert_eq!(lines.concat().replace(' ', ""), d.replace(' ', ""), "nothing lost");
            assert!(lines.iter().all(|l| !l.starts_with('，') && !l.starts_with('：')), "{lines:?}");
        }
        let two = wrap_in(d, 2);
        assert!((line_em(&two[0]) - line_em(&two[1])).abs() < 12.0, "{two:?}");
        // English breaks at spaces, never inside a word
        let en = desc(Lang::En, fb);
        for l in wrap(en, 30.0) {
            assert!(line_em(&l) <= 31.0, "{l}");
            assert!(en.contains(&l));
        }
        let words: Vec<&str> = en.split(' ').collect();
        for l in wrap(en, 30.0) {
            for w in l.split(' ') {
                assert!(words.contains(&w), "{w} cut out of a word");
            }
        }
        // a short one stays as it is; a long one up to its first colon
        assert_eq!(brief(Lang::Hans, 0), "攻击力 +20%");
        assert_eq!(brief(Lang::Hans, fb), "命中英雄时点燃 3 秒…");
        assert_eq!(brief(Lang::En, fb), "Hits burn champions for 3 s…");
        assert_eq!(brief(Lang::Ko, fb), "챔피언 적중 시 3초간 불태움…");
        assert_eq!(brief(Lang::Ja, fb), "チャンピオンに命中すると 3 秒間炎上…");
        for a in 0..crate::augments::AUGS.len() {
            for lang in Lang::ALL {
                assert!(line_em(&brief(lang, a)) <= 40.0, "{} {lang:?}: {}", crate::augments::AUGS[a].key, brief(lang, a));
                // every description fits a card in three lines at a readable size
                let lines = wrap_in(desc(lang, a), 3);
                let longest = lines.iter().map(|l| line_em(l)).fold(0.0, f32::max);
                assert!(lines.len() <= 3 && longest <= 44.0, "{} {lang:?}: {lines:?}", crate::augments::AUGS[a].key);
            }
        }
    }

    #[test]
    fn the_bp_panels_words() {
        assert_eq!(screen_name(Lang::Hans, 0, [6, 9, 12]), "开局");
        assert_eq!(screen_name(Lang::Hans, 2, [6, 9, 12]), "9 级");
        assert_eq!(screen_name(Lang::En, 3, [6, 9, 12]), "Level 12");
        assert_eq!(screen_name(Lang::Ko, 1, [6, 9, 12]), "6레벨");
        assert_eq!(screen_name(Lang::Ja, 0, [6, 9, 12]), "開始");
        assert_eq!(bp_button(Lang::Hans, 2, 5), "海克斯 · 已选 2/5");
        assert_eq!(bp_button(Lang::Ko, 2, 5), "증강 2/5");
        assert!(bp_title(Lang::Hans, true).ends_with("已锁定）"));
        assert_eq!(by_note(Lang::Hans, 2), "（你选的）");
        assert_eq!(by_note(Lang::Hans, 0), "");
        assert_eq!(bp_confirm(Lang::Hans, "塔莉垭"), "确定 塔莉垭");
        assert_eq!(bp_confirm(Lang::Ja, "タリヤ"), "タリヤ を確定");
        assert_eq!(bp_chosen(Lang::Hans, false, true), "已选 · 已确定");
        assert_eq!(bp_chosen(Lang::Hans, true, true), "已选 · 你选的");
        assert_eq!(bp_reroll(Lang::Ko, false, true), "새로고침");
    }

    #[test]
    fn the_language_is_read_from_the_games_text() {
        assert_eq!(lang_of("幽灵 灵魂收割 亡灵法师"), Lang::Hans);
        assert_eq!(lang_of("幽靈 靈魂收割 亡靈法師"), Lang::Hant);
        assert_eq!(lang_of("Ghost Necromancer"), Lang::En);
        assert_eq!(lang_of("유령 강령술사"), Lang::Ko);
        assert_eq!(lang_of("ゴースト 死霊術師"), Lang::Ja);
        assert_eq!(lang_of(""), Lang::En);
    }

    #[test]
    fn lines_read_well() {
        let gc = super::super::augments::by_key("glass_cannon").unwrap() as u16;
        let deft = super::super::augments::by_key("deft").unwrap() as u16;
        let bf = super::super::augments::by_key("blunt_force").unwrap() as u16;
        let ic = super::super::augments::by_key("ironclad").unwrap() as u16;
        assert_eq!(toast_title(Lang::Hans, 0, "金克丝", 6, gc as usize), "蓝色方 金克丝 6 级 · 【金】玻璃大炮");
        assert_eq!(candidates(Lang::Hans, [bf, gc, deft], [bf, gc, deft]), "三选一：钝器 / 玻璃大炮 / 灵巧");
        assert_eq!(candidates(Lang::Hans, [bf, gc, deft], [bf, gc, ic]), "三选一：钝器 / 玻璃大炮 / 灵巧（刷新掉：铁甲）");
        assert_eq!(tagged(Lang::En, gc as usize), "[Gold] Glass Cannon");
        assert_eq!(tagged(Lang::Ko, gc as usize), "[골드] 유리 대포");
        assert_eq!(tagged(Lang::Ja, gc as usize), "【ゴールド】グラスキャノン");
        assert_eq!(toast_title(Lang::Ko, 1, "징크스", 6, gc as usize), "레드 징크스 6레벨 · [골드] 유리 대포");
        assert_eq!(candidates(Lang::Ja, [bf, gc, deft], [bf, gc, ic]), "3 つから 1 つ：鈍器 / グラスキャノン / 器用（リロール：鉄甲）");
        assert_eq!(opening_title(Lang::Hant, Tier::Prismatic), "海克斯大亂鬥 · 開局海克斯（稜彩）");
        assert_eq!(opening_next(Lang::Hans, [6, 9, 12]), "之后 6 级、9 级、12 级各再选一次（三选一）");
        // every language has a name and a description for every augment
        for a in 0..super::super::augments::AUGS.len() {
            for lang in Lang::ALL {
                assert!(!name(lang, a).is_empty() && !desc(lang, a).is_empty(), "{a} {lang:?}");
            }
        }
    }
}
