//! 本包改的游戏文字（`text/object.i18n`、`text/ui.i18n`、`text/strategy.i18n`：莫尔加德 -> 纳什男爵 / 巴龍 / Baron Nashor，
//! 双角巨蛇 -> 元素亚龙 / 元素亞龍 / Elemental Drake）的检查。工作区没有 JSON 库，这里一个只认对象和字符串的小读法（i18n 文件
//! 里只有这两样）。

use super::rules::{self, DRAKES};
use super::words::{self, Lang};

#[derive(Clone, Debug, PartialEq)]
enum J {
    S(String),
    O(Vec<(String, J)>),
}

struct P {
    c: Vec<char>,
    i: usize,
}

impl P {
    fn ws(&mut self) {
        while self.i < self.c.len() && self.c[self.i].is_whitespace() {
            self.i += 1;
        }
    }

    fn value(&mut self) -> J {
        self.ws();
        match self.c[self.i] {
            '{' => self.object(),
            '"' => J::S(self.string()),
            c => panic!("only objects and strings in an i18n file: {c:?} at {}", self.i),
        }
    }

    fn object(&mut self) -> J {
        self.i += 1;
        let mut v: Vec<(String, J)> = Vec::new();
        loop {
            self.ws();
            if self.c[self.i] == '}' {
                self.i += 1;
                return J::O(v);
            }
            if !v.is_empty() {
                assert_eq!(self.c[self.i], ',', "at {}", self.i);
                self.i += 1;
                self.ws();
            }
            let k = self.string();
            self.ws();
            assert_eq!(self.c[self.i], ':', "at {}", self.i);
            self.i += 1;
            let val = self.value();
            assert!(!v.iter().any(|(x, _)| *x == k), "the key {k} twice");
            v.push((k, val));
        }
    }

    fn string(&mut self) -> String {
        assert_eq!(self.c[self.i], '"', "at {}", self.i);
        self.i += 1;
        let mut s = String::new();
        loop {
            let c = self.c[self.i];
            self.i += 1;
            match c {
                '"' => return s,
                '\\' => {
                    let e = self.c[self.i];
                    self.i += 1;
                    match e {
                        'n' => s.push('\n'),
                        't' => s.push('\t'),
                        '"' | '\\' | '/' => s.push(e),
                        'u' => {
                            let h: String = self.c[self.i..self.i + 4].iter().collect();
                            self.i += 4;
                            s.push(char::from_u32(u32::from_str_radix(&h, 16).unwrap()).unwrap());
                        }
                        _ => panic!("escape \\{e}"),
                    }
                }
                c => s.push(c),
            }
        }
    }
}

fn parse(text: &str) -> J {
    let mut p = P { c: text.trim_start_matches('\u{feff}').chars().collect(), i: 0 };
    let v = p.value();
    p.ws();
    assert_eq!(p.i, p.c.len(), "something after the top object");
    v
}

/// (语言, [(键, 文字)])，键是点分的（`match.log.red_epic`）。
fn load(name: &str) -> Vec<(String, Vec<(String, String)>)> {
    let path = format!("{}/../league_dragons/text/{name}.i18n", env!("CARGO_MANIFEST_DIR"));
    let J::O(langs) = parse(&std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"))) else {
        panic!("{path}: not an object")
    };
    fn flat(j: &J, at: &str, out: &mut Vec<(String, String)>) {
        match j {
            J::S(s) => out.push((at.to_string(), s.clone())),
            J::O(v) => {
                for (k, x) in v {
                    flat(x, &if at.is_empty() { k.clone() } else { format!("{at}.{k}") }, out);
                }
            }
        }
    }
    langs
        .iter()
        .map(|(lang, j)| {
            let mut v = Vec::new();
            flat(j, "", &mut v);
            (lang.clone(), v)
        })
        .collect()
}

fn get<'a>(file: &'a [(String, Vec<(String, String)>)], lang: &str, key: &str) -> &'a str {
    let l = &file.iter().find(|x| x.0 == lang).unwrap_or_else(|| panic!("no {lang}")).1;
    &l.iter().find(|x| x.0 == key).unwrap_or_else(|| panic!("no {lang} {key}")).1
}

fn placeholders(s: &str) -> Vec<String> {
    let mut v: Vec<String> = s.split('{').skip(1).filter_map(|x| x.split_once('}').map(|y| y.0.to_string())).collect();
    v.sort();
    v
}

const LANGS: [(&str, Lang); 3] = [("zh-hans", Lang::Hans), ("zh-hant", Lang::Hant), ("en", Lang::En)];

/// The game's own names (0.7.0's text/object, text/ui, text/strategy) that must be gone from what we merge in.
fn native_names(lang: &str) -> &'static [&'static str] {
    match lang {
        "zh-hans" => &["莫尔加德", "双角巨蛇", "瑟彭", "塞尔彭"],
        "zh-hant" => &["莫加德", "莫爾加德", "蛇彭", "瑟彭", "塞爾彭"],
        _ => &["Morgard", "Serpen"],
    }
}

/// Every key of the game's text/ui that names the Serpen or Morgard (game 0.7.0, all three languages).
const UI_KEYS: [&str; 21] = [
    "database_edit.number_field.epic_jungle",
    "database_edit.number_field.serpen_jungle",
    "database_edit.number_field.epic_minion_buff_duration",
    "database_edit.number_field.epic_minion_buff_range",
    "database_edit.number_morgard_buff_section",
    "database_edit.number_morgard_buff_increase_section",
    "database_edit.number_serpen_buff_section",
    "training.comp_test.history_objects",
    "training.comp_test.summary_objects",
    "match.log.red_epic",
    "match.log.blue_epic",
    "match.log.red_serpen",
    "match.log.blue_serpen",
    "ingame.epic",
    "ingame.serpen",
    "set_result.epic",
    "set_result.serpen",
    "set_result.graph_blue_epic",
    "set_result.graph_red_epic",
    "set_result.graph_blue_serpen",
    "set_result.graph_red_serpen",
];

#[test]
fn the_names_are_overridden_in_all_three_languages() {
    for file in ["object", "ui", "strategy"] {
        let f = load(file);
        let mut langs: Vec<&str> = f.iter().map(|x| x.0.as_str()).collect();
        langs.sort();
        assert_eq!(langs, vec!["en", "zh-hans", "zh-hant"], "{file}");
        for (lang, kv) in &f {
            for (k, v) in kv {
                assert!(!v.trim().is_empty(), "{file} {lang} {k} empty");
                // the placeholders keep their names ({Morgard}, {Serpen}): the game fills them in
                let shown: String = v.split('{').enumerate()
                    .map(|(i, x)| if i == 0 { x } else { x.split_once('}').map_or(x, |y| y.1) })
                    .collect();
                for n in native_names(lang) {
                    assert!(!shown.contains(n), "{file} {lang} {k} still says {n}: {v}");
                }
            }
        }
        if file == "strategy" {
            continue; // only the texts that named them, a different set in each language
        }
        // the same keys in every language, the same placeholders ({Count}, {Morgard} ...) in each
        let keys = |l: &str| {
            let mut v: Vec<String> = f.iter().find(|x| x.0 == l).unwrap().1.iter().map(|x| x.0.clone()).collect();
            v.sort();
            v
        };
        assert_eq!(keys("zh-hans"), keys("en"), "{file}");
        assert_eq!(keys("zh-hant"), keys("en"), "{file}");
        for k in keys("en") {
            let p = placeholders(get(&f, "en", &k));
            for (l, _) in LANGS {
                assert_eq!(placeholders(get(&f, l, &k)), p, "{file} {l} {k}");
            }
        }
    }
    let ui = load("ui");
    for (l, _) in LANGS {
        for k in UI_KEYS {
            get(&ui, l, k);
        }
        assert!(get(&ui, l, "match.log.red_epic").starts_with("<#f7b1b8ff>"));
        assert!(get(&ui, l, "match.log.blue_serpen").starts_with("<#adb9ffff>"));
        assert_eq!(placeholders(get(&ui, l, "training.comp_test.summary_objects")),
                   vec!["BlueTower", "Morgard", "RedTower", "Serpen"]);
    }
    assert_eq!(get(&ui, "zh-hans", "match.log.blue_epic"), "<#adb9ffff>蓝方<>击杀了纳什男爵！");
    assert_eq!(get(&ui, "zh-hans", "match.log.red_serpen"), "<#f7b1b8ff>红方<>击杀了元素亚龙！");
    assert_eq!(get(&ui, "zh-hant", "ingame.epic"), "巴龍擊殺");
    assert_eq!(get(&ui, "en", "set_result.serpen"), "Elemental Drake");
    let obj = load("object");
    for (l, lang, baron, drake) in [("zh-hans", Lang::Hans, "纳什男爵", "元素亚龙"), ("zh-hant", Lang::Hant, "巴龍", "元素亞龍"),
                                    ("en", Lang::En, "Baron Nashor", "Elemental Drake")] {
        assert_eq!(get(&obj, l, "epic.name"), baron);
        assert_eq!(get(&obj, l, "serpen.name"), drake);
        // the screen's language is read from this very name
        assert_eq!(words::lang_of(get(&obj, l, "epic.name"), ""), lang);
        assert_eq!(placeholders(get(&obj, l, "serpen.current_buff")), vec!["Count", "Stats"]);
    }
}

/// The descriptions (the encyclopedia's Serpen and Morgard) carry the gameplay's numbers.
#[test]
fn the_descriptions_carry_the_gameplay_numbers() {
    let obj = load("object");
    for (l, lang) in LANGS {
        let drakes = get(&obj, l, "serpen.buff_desc");
        for e in DRAKES {
            let part = format!("{} {}", words::element(lang, e), words::stack_effect(lang, e));
            assert!(drakes.contains(&part), "{l}: {part:?} not in {drakes}");
        }
        assert!(drakes.contains(&format!(" {} ", rules::SOUL_AT)), "{l}");
        let baron = get(&obj, l, "epic.buff_desc");
        for n in [words::secs(rules::BARON_T), format!("{}%", rules::BARON_PCT), format!("{}%", rules::MINION_REDUCE),
                  format!("{}%", rules::MINION_ATTACK)] {
            assert!(baron.contains(&n), "{l}: {n} not in {baron}");
        }
    }
}
