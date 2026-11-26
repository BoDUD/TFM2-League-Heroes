//! 本包哪些英雄有高清帧（PPU）：ragnarok.dll 的表，init 时交给 hd_engine。一行的意思和 league_main/src/hd.rs、
//! tft/src/hd.rs 的一样（hd_engine src/hd.rs 的 Table）。

use hd_engine::Table;

/// 英雄 id、一个游戏像素几格、图的 .fanim（ragnarok/ 里的原样）。
///
/// 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
/// 联盟英雄待机中位数 41.5 个游戏像素，本包原来 35，每个英雄的 PPU 除以 1.2（同样的像素画成 1.2 倍大，彼此的高矮不变）。
/// 下面注释里写的游戏像素是放大前的，乘 1.2 就是现在的。特效图（EFFECTS）不变：命中和范围按游戏里的距离走。
pub const HEROES: &[(&str, f32, &str)] = &[
    // 吕布（ragnarok_lubu）：Codex 画的 128 格原画就是高清帧，头发到脚底 66 格、翎子尖 73 格。原来 PPU 1.65（头顶 40），
    // 用户说比索尔高出不少，改成 1.94：同样的像素画成 85% 大，头顶 34、翎子 37.6 个游戏像素。1 倍帧由
    // tools/art/import_lubu.py 从高清帧缩出来，高清帧原样；他的特效图还是 1.65（下面 EFFECTS）。2026-11-21 换成 Codex 照动画
    // 第一季重画的两倍帧（assets/source/lubu/rebuild），PPU 都乘 2：身体 3.88、特效 3.3，个子不变
    ("ragnarok_lubu", 3.233, include_str!("../../../ragnarok/champions/ragnarok_lubu#anim.fanim")),
    // 索尔（ragnarok_thor）：同样是 Codex 的 128 格原画，头发到脚底 55 格、肩上雷槌顶 76 格；PPU 1.65，游戏里头顶 33、
    // 锤顶 46 个游戏像素（和缩过的吕布头顶齐平）。投锤的接锤单独一个标签 skill2_catch（锤子真飞回来才播）。
    // 2026-11-21 换成 Codex 照动画第一季重画的帧（assets/source/thor/rebuild，一格 256），他在格子里站高约 89 格，
    // PPU 2.67，游戏里还是 33 个游戏像素；特效图也按 2.67 出
    ("ragnarok_thor", 2.225, include_str!("../../../ragnarok/champions/ragnarok_thor#anim.fanim")),
    // 宙斯（ragnarok_zeus）：Codex 的 128 格原画，三种身体合在一张图里：老人（idle .. dead）头顶离脚底 51 格、膨胀（mu_*）
    // 67 格、阿陀磨须（ad_*）59 格，和索尔一样 PPU 1.65，游戏里 31 / 41 / 36 个游戏像素。站着、跑着、出手、挨打、倒下按身上
    // 的形态 buff 换成那种身体的帧（src/zeus.rs 的显示钩子），变身过程 expand / ult / revert 由数据播。
    // 2026-11-21 按两倍密度重出（tools/art/zeus_repixel.py），PPU 3.3，个子不变
    ("ragnarok_zeus", 2.75, include_str!("../../../ragnarok/champions/ragnarok_zeus#anim.fanim")),
    // 亚当（ragnarok_adam）：从 Codex 的原画按两倍密度重出的像素图（tools/art/adam_repixel.py：Codex 的版本发糊、
    // 描边断），一格 256、站高 108 格，PPU 3.3，游戏里还是 33 个游戏像素
    ("ragnarok_adam", 2.75, include_str!("../../../ragnarok/champions/ragnarok_adam#anim.fanim")),
    // 波塞冬（ragnarok_poseidon）：Codex 先交的 128 格站直约 58 格（PPU 1.65 是 35 个游戏像素），后来照重画那三个人的
    // 标准按两倍密度重画（assets/source/poseidon/rebuild，一格 256），PPU 3.3，个子不变
    ("ragnarok_poseidon", 2.75, include_str!("../../../ragnarok/champions/ragnarok_poseidon#anim.fanim")),
    // 佐佐木小次郎（ragnarok_kojiro）：Codex 直接按两倍密度画的（一格 256），站直 112 格，PPU 3.3，游戏里 34 个游戏像素；
    // 双刀待机、双刀普攻（niten_*）在同一张图里，二天岩流时 src/kojiro.rs 的显示钩子换上
    ("ragnarok_kojiro", 2.75, include_str!("../../../ragnarok/champions/ragnarok_kojiro#anim.fanim")),
    // 赫拉克勒斯（ragnarok_heracles）：Codex 直接按两倍密度画的，站直 121 格，PPU 3.3，游戏里 37 个游戏像素（大个子）；
    // 刻耳柏洛斯形态（c_*）在同一张图里，第十二御业以后 src/heracles.rs 的显示钩子换上
    ("ragnarok_heracles", 2.75, include_str!("../../../ragnarok/champions/ragnarok_heracles#anim.fanim")),
    // 开膛手杰克（ragnarok_jack）：Codex 直接按两倍密度画的，站直 115 格（连帽上的羽毛），PPU 3.3，35 个游戏像素
    ("ragnarok_jack", 2.75, include_str!("../../../ragnarok/champions/ragnarok_jack#anim.fanim")),
    // 雷电为右卫门（ragnarok_raiden）：Codex 直接按两倍密度画的，站直 123 格，PPU 3.3，37 个游戏像素（和赫拉克勒斯一样高）；
    // 肌肉解放的过渡 muscle_release 在同一张图里，数据在每条命第一次放八咫乌时播
    ("ragnarok_raiden", 2.75, include_str!("../../../ragnarok/champions/ragnarok_raiden#anim.fanim")),
    // 湿婆（ragnarok_shiva）：Codex 直接按两倍密度画的，站直 116 格，PPU 3.3，35 个游戏像素；轮回舞踊的燃烧形态（h_*）在同一张图里，
    // 变身以后 src/shiva.rs 的显示钩子换上
    ("ragnarok_shiva", 2.75, include_str!("../../../ragnarok/champions/ragnarok_shiva#anim.fanim")),
    // 释迦（ragnarok_buddha）：Codex 直接按两倍密度画的，站直 112 格（发髻），PPU 3.3，34 个游戏像素
    ("ragnarok_buddha", 2.75, include_str!("../../../ragnarok/champions/ragnarok_buddha#anim.fanim")),
    // 零福／波旬（ragnarok_zerofuku）：Codex 直接按两倍密度画的，零福站直 116 格、波旬连角 125 格，PPU 3.3，35 / 38 个游戏像素
    ("ragnarok_zerofuku", 2.75, include_str!("../../../ragnarok/champions/ragnarok_zerofuku#anim.fanim")),
    // 哈迪斯（ragnarok_hades）：Codex 直接按两倍密度画的，站直 115 格（立着的双叉枪尖到 159 格），一开始就按现在的 PPU 2.75 接，
    // 42 个游戏像素（枪尖 58）
    ("ragnarok_hades", 2.75, include_str!("../../../ragnarok/champions/ragnarok_hades#anim.fanim")),
    // 秦始皇（ragnarok_qin）：Codex 直接按两倍密度画的，站直 116 格，PPU 2.75，42 个游戏像素
    ("ragnarok_qin", 2.75, include_str!("../../../ragnarok/champions/ragnarok_qin#anim.fanim")),
    // 别西卜（ragnarok_beelzebub）：Codex 直接按两倍密度画的，站直 115 格，PPU 2.75，42 个游戏像素
    ("ragnarok_beelzebub", 2.75, include_str!("../../../ragnarok/champions/ragnarok_beelzebub#anim.fanim")),
    // 尼古拉·特斯拉（ragnarok_tesla）：Codex 直接按两倍密度画的机甲，站直 116 格，PPU 2.75，42 个游戏像素
    ("ragnarok_tesla", 2.75, include_str!("../../../ragnarok/champions/ragnarok_tesla#anim.fanim")),
    // 列奥尼达斯（ragnarok_leonidas）：Codex 直接按两倍密度画的，站直 115 格，PPU 2.75，42 个游戏像素；盾在 tools/art/leonidas_fix.py
    // 一律按同一个大小重贴过
    ("ragnarok_leonidas", 2.75, include_str!("../../../ragnarok/champions/ragnarok_leonidas#anim.fanim")),
    // 阿波罗（ragnarok_apollo）：Codex 直接按两倍密度画的，站直 116 格，PPU 2.75，42 个游戏像素；光弓和女神像在
    // tools/art/apollo_fix.py 一律按满的大小重贴过
    ("ragnarok_apollo", 2.75, include_str!("../../../ragnarok/champions/ragnarok_apollo#anim.fanim")),
    // 冲田总司、须佐之男、西蒙·海耶、洛基：Codex 交的是逻辑像素图集（Q 版像素画，人站直 56 格），tools/art/ragnarok_atlas.py 按两倍最近邻
    // 读进来（像素画只按整数倍放大），站直 112 格；PPU 8/3，42 个游戏像素，和别的终末英雄一样高
    ("ragnarok_okita", 2.667, include_str!("../../../ragnarok/champions/ragnarok_okita#anim.fanim")),
    ("ragnarok_susanoo", 2.667, include_str!("../../../ragnarok/champions/ragnarok_susanoo#anim.fanim")),
    ("ragnarok_simo", 2.667, include_str!("../../../ragnarok/champions/ragnarok_simo#anim.fanim")),
    ("ragnarok_loki", 2.667, include_str!("../../../ragnarok/champions/ragnarok_loki#anim.fanim")),
];

/// 英雄在高清帧画出来的地方的大小（1.0 = 1 倍帧的大小，不列就是 1.0）。
pub const SIZES: &[(&str, f32)] = &[];

/// 身体随层数变大的英雄：本包没有。
pub const GROWTH: &[(&str, &str, f32)] = &[];

/// 身上有某个 buff 时画大一点的英雄：本包没有。
pub const FORMS: &[(&str, &[&str], f32, f32)] = &[];

/// 像英雄的图一样画高清的特效图：吕布打在人身上的火花、天喰的冲击、碎盾，原画就是高清帧（tools/art/import_lubu.py）。
pub const EFFECTS: &[(&str, f32, &str)] = &[
    ("ragnarok_lubu_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_lubu_fx#anim.fanim")),
    // 索尔打在人身上的雷击、觉醒重砸的冲击、雷槌觉醒的红纹（飞出去的锤子是弹道画面，1 倍，不在这里）
    ("ragnarok_thor_fx", 2.67, include_str!("../../../ragnarok/effects/ragnarok_thor_fx#anim.fanim")),
    // 宙斯打在人身上的拳光、连拳的雷光、变身完成时脚下炸开的一圈（拳风、蓄力和变身的光画在他自己的帧里）
    // 宙斯的特效图和身体一样按两倍重出，3.3
    ("ragnarok_zeus_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_zeus_fx#anim.fanim")),
    // 亚当普攻打在人身上的火花（拳风、闪避、模仿标记、反击火花、时间之拳都画在他自己的帧里），和身体一样两倍重出
    ("ragnarok_adam_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_adam_fx#anim.fanim")),
    // 波塞冬打在人身上的命中水花、大洪水围住目标的环形戟影（戟风、连刺扇形、斜刺、蓄势画在他自己的帧里），
    // 和身体一样按两倍从 Codex 的原画重出（tools/art/poseidon_rebuild_fix.py），3.3
    ("ragnarok_poseidon_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_poseidon_fx#anim.fanim")),
    // 小次郎打在人身上的金属火花（燕返刀光、预判涟漪、双刀交错画在他自己的帧里）
    ("ragnarok_kojiro_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_kojiro_fx#anim.fanim")),
    // 赫拉克勒斯打在人身上的巨棒、拳头命中（弧光、狮头、变身的光环、拳风、砸地的冲击画在他自己的帧里）
    ("ragnarok_heracles_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_heracles_fx#anim.fanim")),
    // 杰克的飞刀命中、收招、看穿人心时那道异色的光（扇形飞刀、护弧、雾、手套触物画在他自己的帧里；飞出去的刀是
    // 弹道画面，1 倍，不在这里）
    ("ragnarok_jack_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_jack_fx#anim.fanim")),
    // 雷电的掌、八咫乌打在人身上的命中（掌风、四股的尘土和震环、八咫乌的气和冲击波、肌肉解放的红纹画在他自己的帧里）
    ("ragnarok_raiden_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_raiden_fx#anim.fanim")),
    // 湿婆打在人身上的银光、火焰命中（拳风、交叉、舞步、点燃、火鞭、火步画在他自己的帧里）
    ("ragnarok_shiva_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_shiva_fx#anim.fanim")),
    // 释迦打在人身上的棍击、观音盾的挡击，他身上的未来视和莲光（棍风、枪刃、撤步的气流、大圆寂刀的气和刀光画在他自己的帧里）
    ("ragnarok_buddha_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_buddha_fx#anim.fanim")),
    ("ragnarok_zerofuku_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_zerofuku_fx#anim.fanim")),
    // 哈迪斯打在人身上的枪击、德斯莫斯的命中（枪风、风压斩、砸地、尘土、伊科尔觉醒、德斯莫斯的突刺画在他自己的帧里）
    ("ragnarok_hades_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_hades_fx#anim.fanim")),
    // 秦始皇的指爪命中、气弹炸开的星（爪痕、神罗铠袖的护势、天凤回推、勾践剑的剑光和剑痕画在他自己的帧里；飞出去的气弹是
    // 弹道画面，1 倍，不在这里）
    ("ragnarok_qin_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_qin_fx#anim.fanim")),
    // 别西卜振动掌的命中（掌风、振动波、波纹、屏障、格挡涟漪、混沌的黑核和爆发画在他自己的帧里）
    ("ragnarok_beelzebub_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_beelzebub_fx#anim.fanim")),
    // 特斯拉的拳击命中、双拳的冲击、离场的闪光、神之监狱的牢笼（展开一次、再一圈一圈接着放，都是 view_effects，走高清；
    // 拳风、拖痕、到达的闪光画在他自己的帧里）
    ("ragnarok_tesla_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_tesla_fx#anim.fanim")),
    // 列奥尼达斯盾击和链盾的命中、方阵冲锋的冲击（钢弧、飞盘的尾迹、钢链回卷、盾沿的光、反弹的光箭、冲锋的尘土画在他自己的帧里）
    ("ragnarok_leonidas_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_leonidas_fx#anim.fanim")),
    // 阿波罗日轮拳和光箭的命中、光丝的收束（拳光、光丝投出、光弓成形和离弦的光、女神像显现的光、银箭的箭影画在他自己的帧里；
    // 飞出去的光箭是弹道画面，1 倍，不在这里）
    ("ragnarok_apollo_fx", 3.3, include_str!("../../../ragnarok/effects/ragnarok_apollo_fx#anim.fanim")),
    // 冲田、须佐之男、海耶、洛基：特效和人一个比例（Codex 按人画的大小），PPU 同人 8/3。挂在目标身上的命中、挂在自己身上的循环
    // （鬼子的气息、雪幕）在这里；出招的刀光、枪口焰、光迹画在他们自己的帧里
    ("ragnarok_okita_fx", 2.667, include_str!("../../../ragnarok/effects/ragnarok_okita_fx#anim.fanim")),
    ("ragnarok_susanoo_fx", 2.667, include_str!("../../../ragnarok/effects/ragnarok_susanoo_fx#anim.fanim")),
    ("ragnarok_simo_fx", 2.667, include_str!("../../../ragnarok/effects/ragnarok_simo_fx#anim.fanim")),
    ("ragnarok_loki_fx", 2.667, include_str!("../../../ragnarok/effects/ragnarok_loki_fx#anim.fanim")),
];

/// 画面节点画特效时缩成 1 / PPU 的特效：上面这张只当 view_effects 播，没有 buff 和弹道的画面，走普通的门就行。
pub const DRAWN_EFFECTS: &[&str] = &["ragnarok_lubu_fx", "ragnarok_thor_fx", "ragnarok_zeus_fx",
                                         "ragnarok_adam_fx", "ragnarok_poseidon_fx", "ragnarok_kojiro_fx",
                                         "ragnarok_heracles_fx", "ragnarok_jack_fx",
                                         "ragnarok_raiden_fx", "ragnarok_shiva_fx", "ragnarok_buddha_fx",
                                         "ragnarok_zerofuku_fx", "ragnarok_hades_fx", "ragnarok_qin_fx",
                                         "ragnarok_beelzebub_fx", "ragnarok_tesla_fx", "ragnarok_leonidas_fx",
                                         "ragnarok_apollo_fx", "ragnarok_okita_fx", "ragnarok_susanoo_fx",
                                         "ragnarok_simo_fx", "ragnarok_loki_fx"];

/// 界面上画 lo_ 帧的地方（选人卡片）缩小画的高个子英雄。
pub const UI_SIZES: &[(&str, f32)] = &[
    // 2026-11-22 整包放大 1.2 倍以后，这四个头顶到脚底 45-47 个游戏像素，选人卡（约 40 个游戏像素高）要挡住 6 像素以上的腿：
    // 照联盟的规矩（league_main/src/hd.rs 的 UI_SIZES，烈娜塔那次）缩到 39 / 身高，只缩选人卡和选中时的小框，百科和战场不缩
    ("ragnarok_heracles", 0.87),
    ("ragnarok_kojiro", 0.82),
    ("ragnarok_lubu", 0.85),
    ("ragnarok_raiden", 0.85),
];

/// 本包的表，ragnarok.dll 在 init 时交给 hd_engine（src/lib.rs）。
pub fn table() -> Table<'static> {
    Table {
        pack: "ragnarok",
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
            assert_eq!(h.of_name(&format!("asset/ragnarok/champions/{id}#anim")).map(|x| x.id), Some(id));
        }
        assert!(h.get("ragnarok_nobody").is_none());
        // 别的包的英雄在它们自己的表里
        assert!(h.get("league_yasuo").is_none());
        assert!(h.get("tft_powder").is_none());
        assert_eq!(h.packs, vec!["ragnarok"]);
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
