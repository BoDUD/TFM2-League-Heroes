//! 本包哪些英雄有高清帧（PPU）：border.dll 的表，init 时交给 hd_engine。一行的意思和 league_main/src/hd.rs、
//! ragnarok/src/hd.rs 的一样（hd_engine src/hd.rs 的 Table）。
//!
//! 十二个人都是 Codex 按两倍密度画的（一格 256，脚底点 (128, 184)），tools/art/border_fix.py 收成游戏那种像素风（每人一套
//! 调色板、清掉杂点、同色系的 1 像素描边，形状一点不动），PPU 2.54：人站直 100–110 格，游戏里 38–43 个游戏像素，和联盟
//! 英雄一样高（2026-11-22 用户要放大到联盟大小：原来 PPU 3.3 只有 29–33 个游戏像素，统一放大 1.3 倍）。特效图不放大（EFFECTS 还是 3.3）：地上的圈、命中按游戏里的距离画。

use hd_engine::Table;

/// 英雄 id、一个游戏像素几格、图的 .fanim（border/ 里的原样）。
pub const HEROES: &[(&str, f32, &str)] = &[
    // 岑垒：珊瑚盾卫，站直 110 格（头发到脚底），43 个游戏像素；横楔的扫击、卸城的三道楔浪画在他自己的帧里
    ("border_cenlei", 2.54, include_str!("../../../border/champions/border_cenlei#anim.fanim")),
    // 绡轮：潮弩信使，站直 102 格；切角的拖影、放扣的扣环光画在她自己的帧里
    ("border_xiaolun", 2.54, include_str!("../../../border/champions/border_xiaolun#anim.fanim")),
    // 灯弥：提灯师，站直 100 格（呆毛到脚底），鳍翼跑图时收在背后
    ("border_dengmi", 2.54, include_str!("../../../border/champions/border_dengmi#anim.fanim")),
    // 铸沫：铜火锻匠，站直 111 格；压坯落锤的熔流和地面火星画在他自己的帧里
    ("border_zhumo", 2.54, include_str!("../../../border/champions/border_zhumo#anim.fanim")),
    // 伏梭：银梭斥候，站直 105 格；掠阶的银线画在他自己的帧里
    ("border_fusuo", 2.54, include_str!("../../../border/champions/border_fusuo#anim.fanim")),
    // 盐汐：盐晶法师，站直 102 格（马尾到脚底）
    ("border_yanxi", 2.54, include_str!("../../../border/champions/border_yanxi#anim.fanim")),    // 殷渡：开团坦克，站直 110 格；扣舷的撞角画在他自己的帧里
    ("border_yindu", 2.54, include_str!("../../../border/champions/border_yindu#anim.fanim")),
    // 澜缇：反击战士，站直 104 格
    ("border_lanti", 2.54, include_str!("../../../border/champions/border_lanti#anim.fanim")),
    // 鹭芯：追击刺客，站直 98 格；贴风的风痕画在她自己的帧里
    ("border_luxin", 2.54, include_str!("../../../border/champions/border_luxin#anim.fanim")),
    // 霁砚：远程炮台，站直 106 格
    ("border_jiyan", 2.54, include_str!("../../../border/champions/border_jiyan#anim.fanim")),
    // 钟砾：站桩射手，站直 105 格；压簧前臂的弹簧画在他自己的帧里
    ("border_zhongli", 2.54, include_str!("../../../border/champions/border_zhongli#anim.fanim")),
    // 雾绫：控场辅助，站直 101 格
    ("border_wuling", 2.54, include_str!("../../../border/champions/border_wuling#anim.fanim")),
];

/// 英雄在高清帧画出来的地方的大小（1.0 = 1 倍帧的大小，不列就是 1.0）。
pub const SIZES: &[(&str, f32)] = &[];

/// 身体随层数变大的英雄：本包没有。
pub const GROWTH: &[(&str, &str, f32)] = &[];

/// 身上有某个 buff 时画大一点的英雄：本包没有。
pub const FORMS: &[(&str, &[&str], f32, f32)] = &[];

/// 像英雄的图一样画高清的特效图（打在人身上的、贴在人身上的、地上的圈）。飞出去的弹道画面（_proj）是 1 倍，不在这里。
pub const EFFECTS: &[(&str, f32, &str)] = &[
    ("border_cenlei_fx", 3.3, include_str!("../../../border/effects/border_cenlei_fx#anim.fanim")),
    ("border_xiaolun_fx", 3.3, include_str!("../../../border/effects/border_xiaolun_fx#anim.fanim")),
    ("border_dengmi_fx", 3.3, include_str!("../../../border/effects/border_dengmi_fx#anim.fanim")),
    ("border_zhumo_fx", 3.3, include_str!("../../../border/effects/border_zhumo_fx#anim.fanim")),
    ("border_fusuo_fx", 3.3, include_str!("../../../border/effects/border_fusuo_fx#anim.fanim")),
    ("border_yanxi_fx", 3.3, include_str!("../../../border/effects/border_yanxi_fx#anim.fanim")),    ("border_yindu_fx", 3.3, include_str!("../../../border/effects/border_yindu_fx#anim.fanim")),
    ("border_lanti_fx", 3.3, include_str!("../../../border/effects/border_lanti_fx#anim.fanim")),
    ("border_luxin_fx", 3.3, include_str!("../../../border/effects/border_luxin_fx#anim.fanim")),
    ("border_jiyan_fx", 3.3, include_str!("../../../border/effects/border_jiyan_fx#anim.fanim")),
    ("border_zhongli_fx", 3.3, include_str!("../../../border/effects/border_zhongli_fx#anim.fanim")),
    ("border_wuling_fx", 3.3, include_str!("../../../border/effects/border_wuling_fx#anim.fanim")),
];

/// 画面节点画特效时缩成 1 / PPU 的特效：上面这几张只当 view_effects 播。
pub const DRAWN_EFFECTS: &[&str] = &["border_cenlei_fx", "border_xiaolun_fx", "border_dengmi_fx", "border_zhumo_fx",
                                         "border_fusuo_fx", "border_yanxi_fx", "border_yindu_fx", "border_lanti_fx",
                                         "border_luxin_fx", "border_jiyan_fx", "border_zhongli_fx", "border_wuling_fx"];

/// 界面上画 lo_ 帧的地方（选人卡片）缩小画的高个子英雄：放大到联盟大小以后，从头顶到脚底超过 40 个游戏像素（选人卡的画布
/// 40 高）的按 39 / 身高缩（和终末包一样），腿不会被名字栏挡住（tools/art/bp_card_audit.py 的 --legs 量法）。
pub const UI_SIZES: &[(&str, f32)] = &[
    ("border_cenlei", 0.89),    // 44.0 个游戏像素
    ("border_xiaolun", 0.94),    // 41.3 个游戏像素
    ("border_zhumo", 0.87),    // 44.7 个游戏像素
    ("border_fusuo", 0.91),    // 42.7 个游戏像素
    ("border_yanxi", 0.96),    // 40.7 个游戏像素
    ("border_yindu", 0.89),    // 44.0 个游戏像素
    ("border_lanti", 0.94),    // 41.3 个游戏像素
    ("border_jiyan", 0.90),    // 43.3 个游戏像素
    ("border_zhongli", 0.93),    // 42.0 个游戏像素
    ("border_wuling", 0.94),    // 41.3 个游戏像素
];

/// 本包的表，border.dll 在 init 时交给 hd_engine（src/lib.rs）。
pub fn table() -> Table<'static> {
    Table {
        pack: "border",
        heroes: HEROES.to_vec(),
        sizes: SIZES.to_vec(),
        growth: GROWTH.to_vec(),
        forms: FORMS.iter().map(|&(id, buffs, size, secs)| (id, buffs.to_vec(), size, secs)).collect(),
        effects: EFFECTS.to_vec(),
        drawn_effects: DRAWN_EFFECTS.to_vec(),
        ui_sizes: UI_SIZES.to_vec(),
        full_effects: Vec::new(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use hd_engine::hd::{checks, Heroes};

    #[test]
    fn heroes_are_found_by_id_and_resource_name() {
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.list.len(), HEROES.len() + EFFECTS.len());
        for &(id, ..) in HEROES {
            assert_eq!(h.get(id).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/border/champions/{id}#anim")).map(|x| x.id), Some(id));
        }
        assert!(h.get("border_nobody").is_none());
        assert!(h.get("ragnarok_lubu").is_none());
        assert_eq!(h.packs, vec!["border"]);
    }

    #[test]
    fn every_registered_sheet_is_ppu_times_as_wide() {
        checks::every_registered_sheet_is_ppu_times_as_wide(&table());
    }

    #[test]
    fn every_registered_sheet_has_hd_tags_for_all_its_tags() {
        checks::every_registered_sheet_has_hd_tags_for_all_its_tags(&table());
    }

    #[test]
    fn ui_sizes_shrink_heroes_with_lo_frames() {
        checks::ui_sizes_shrink_heroes_with_lo_frames(&table());
    }

    #[test]
    fn effect_sheets_have_a_dense_idle() {
        checks::effect_sheets_have_a_dense_idle(&table());
    }

    #[test]
    fn every_row_is_one_of_the_packs_heroes_once() {
        checks::ids_are_the_packs_once(&table());
    }

    #[test]
    fn the_table_reaches_a_host_unchanged() {
        checks::the_table_goes_through_the_text_unchanged(&table());
    }
}
