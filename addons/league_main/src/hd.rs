//! Which heroes have dense (PPU) frames - the parts that need no game.
//!
//! A hero listed in `HEROES` carries `hd_<tag>` beside every `<tag>` in its own sheet (tools/art/ppu_hd.py, the same
//! PPU there), each frame PPU times the 1x frame's size - a drawn one may be grown alike at both ends (its centre, the
//! pivot, kept), hd_idle exactly PPU times as wide (src/lookup.rs tells a changed table by it). src/lookup.rs hands every
//! reader of the hero's animations a table whose every tag holds the dense frames with their rects divided by PPU, and
//! every reader of its sheet a texture that reports its size divided by PPU: the same UVs (the dense squares), the 1x
//! sizes. The tags are read from the sheet's .fanim compiled in.

/// Champion id, pixels per 1x square, the sheet's .fanim (as shipped in league/).
pub const HEROES: &[(&str, f32, &str)] = &[
    ("league_yasuo", 2.2, include_str!("../../../league/champions/league_yasuo#anim.fanim")),
    ("league_gragas", 1.45, include_str!("../../../league/champions/league_gragas#anim.fanim")),
    ("league_zeri", 3.0, include_str!("../../../league/champions/league_zeri#anim.fanim")),
    ("league_vladimir", 1.8, include_str!("../../../league/champions/league_vladimir#anim.fanim")),
    ("league_karma", 2.2, include_str!("../../../league/champions/league_karma#anim.fanim")),
    ("league_ashe", 2.2, include_str!("../../../league/champions/league_ashe#anim.fanim")),
    ("league_irelia", 2.0, include_str!("../../../league/champions/league_irelia#anim.fanim")),
    ("league_kassadin", 2.42, include_str!("../../../league/champions/league_kassadin#anim.fanim")),
    ("league_corki", 2.2, include_str!("../../../league/champions/league_corki#anim.fanim")),
    ("league_garen", 1.9, include_str!("../../../league/champions/league_garen#anim.fanim")),
    ("league_braum", 1.98, include_str!("../../../league/champions/league_braum#anim.fanim")),
    ("league_mordekaiser", 2.0, include_str!("../../../league/champions/league_mordekaiser#anim.fanim")),
    ("league_soraka", 2.2, include_str!("../../../league/champions/league_soraka#anim.fanim")),
    ("league_nidalee", 2.2, include_str!("../../../league/champions/league_nidalee#anim.fanim")),
    ("league_galio", 1.65, include_str!("../../../league/champions/league_galio#anim.fanim")),
    ("league_nilah", 1.98, include_str!("../../../league/champions/league_nilah#anim.fanim")),
    ("league_kindred", 2.2, include_str!("../../../league/champions/league_kindred#anim.fanim")),
    ("league_malzahar", 1.38, include_str!("../../../league/champions/league_malzahar#anim.fanim")),
    // Smolder: PPU 1.5 (the user's pick), drawn at 85 % in his design itself (「感觉太大 得缩小一点」), so no SIZES row
    ("league_smolder", 1.5, include_str!("../../../league/champions/league_smolder#anim.fanim")),
    ("league_milio", 2.2, include_str!("../../../league/champions/league_milio#anim.fanim")),
    ("league_jayce", 1.5, include_str!("../../../league/champions/league_jayce#anim.fanim")),
    ("league_elise", 1.8, include_str!("../../../league/champions/league_elise#anim.fanim")),
    ("league_katarina", 1.5, include_str!("../../../league/champions/league_katarina#anim.fanim")),
    ("league_tahmkench", 1.2, include_str!("../../../league/champions/league_tahmkench#anim.fanim")),
    // Kalista: PPU 1.4 (the user's pick), drawn at 85 % in her frames themselves (「大小 85%，PPU 1.4」), so no SIZES row
    ("league_kalista", 1.4, include_str!("../../../league/champions/league_kalista#anim.fanim")),
    // Dr. Mundo: PPU 1.5 (the user's pick, 42 game rows hair to soles)
    ("league_drmundo", 1.5, include_str!("../../../league/champions/league_drmundo#anim.fanim")),
    // Pantheon: PPU 1.5 (the user's pick), his strips drawn at that density on the design's grid, so no SIZES row
    ("league_pantheon", 1.5, include_str!("../../../league/champions/league_pantheon#anim.fanim")),
    // Orianna: PPU 2.2 (the user's pick after 1.5 read muddy and 2.6 too sharp: 「PPU 2.2（84 行）」), posed by
    // tools/art/rig_orianna.py on that grid, so no SIZES row
    ("league_orianna", 2.2, include_str!("../../../league/champions/league_orianna#anim.fanim")),
    // Aphelios: PPU 1.5 (the user's pick), posed from the design's own squares at that density; 90 % (SIZES, the user:
    // 「厄斐琉斯模型是不是在游戏里太大了？」 then 「缩到 90%」 from a sheet: 47 px against the ADCs' 36-45)
    ("league_aphelios", 1.5, include_str!("../../../league/champions/league_aphelios#anim.fanim")),
    // Rell: PPU 1.5 (the user's pick), posed by tools/art/rig_rell.py on that grid (mounted 44 game rows, on foot 40), so no
    // SIZES row
    ("league_rell", 1.5, include_str!("../../../league/champions/league_rell#anim.fanim")),
    // Rek'Sai: Codex's step-1 takes read back square for square (A 57 rows = the user's 36 game px), posed by
    // tools/art/rig_reksai.py on that grid (57 / 36 = 1.58), pixelated to 1.2 by ppu_restyle (the user: 「雷克赛像素太高
    // 需要降低」, picked 1.2); no SIZES row
    ("league_reksai", 1.2, include_str!("../../../league/champions/league_reksai#anim.fanim")),
    // Urgot: posed at 1.5 squares a game pixel by tools/art/rig_urgot.py (「炮顶到腿尖 42 px，PPU 1.5」), brought to 1.2 by
    // ppu_restyle after the user saw him in game (「现在像素太高 要降低点」 -> 「1.2」); the size unchanged, so no SIZES row
    ("league_urgot", 1.2, include_str!("../../../league/champions/league_urgot#anim.fanim")),
    // Swain: posed by tools/art/rig_swain.py at the user's 1.5 squares a game pixel (40 game rows hair to soles; the demon
    // form's tags on the same body), so no SIZES row
    ("league_swain", 1.5, include_str!("../../../league/champions/league_swain#anim.fanim")),
    // Renata: posed by tools/art/rig_renata.py at the user's 1.5 squares a game pixel (36 game rows hair to soles; the R
    // machine in her own ult frames), so no SIZES row
    ("league_renata", 1.5, include_str!("../../../league/champions/league_renata#anim.fanim")),
    // Nasus: posed by tools/art/rig_nasus.py at the user's 1.2 squares a game pixel (44 game rows ear tips to soles; the big
    // body of Fury of the Sands its own design, 59 rows), so no SIZES row
    ("league_nasus", 1.2, include_str!("../../../league/champions/league_nasus#anim.fanim")),
    // Anivia: posed by tools/art/rig_anivia.py at the user's 1.2 squares a game pixel (38 game rows crown to the lowest
    // wing tip; the Rebirth egg half of that, its own tags), so no SIZES row
    ("league_anivia", 1.2, include_str!("../../../league/champions/league_anivia#anim.fanim")),
    // Jarvan IV: posed by tools/art/rig_jarvaniv.py at the user's 1.5 squares a game pixel (40 game rows helmet to soles,
    // the lance above), so no SIZES row
    ("league_jarvaniv", 1.5, include_str!("../../../league/champions/league_jarvaniv#anim.fanim")),
    // Ziggs: posed by tools/art/rig_ziggs.py at 1.5 squares a game pixel (32 game rows helmet to soles, the bombs held
    // out wide), brought to the user's 1.2 by ppu_restyle (「太高清了 降低点像素」), so no SIZES row
    ("league_ziggs", 1.2, include_str!("../../../league/champions/league_ziggs#anim.fanim")),
    // Maokai: posed by tools/art/rig_maokai.py at 1.5 squares a game pixel (40 game rows crown to the root feet; the
    // user's 「太模糊了 PPU调整一下像素」 raised it from 1.2), brought to the user's 1.3 by ppu_restyle (「太高清了 降低点像素」
    // -> 「1.3吧」), so no SIZES row
    ("league_maokai", 1.3, include_str!("../../../league/champions/league_maokai#anim.fanim")),
    // Gangplank: posed by tools/art/rig_gangplank.py at the user's 1.5 squares a game pixel (41 game rows hat to soles:
    // Codex's step-1 take read back uncut - 「PPU 用 1.5」), Q / R from Codex's gun-hand poses, so no SIZES row
    ("league_gangplank", 1.5, include_str!("../../../league/champions/league_gangplank#anim.fanim")),
    // Wukong: posed by tools/art/rig_wukong.py at the user's 1.5 squares a game pixel (38 game rows hair to soles, the
    // tail and the staff above; 「起码PPU1.5」), so no SIZES row
    ("league_wukong", 1.2, include_str!("../../../league/champions/league_wukong#anim.fanim")),
    // Cassiopeia: posed by tools/art/rig_cassiopeia.py at the user's 1.3 squares a game pixel (44 game rows crest to the
    // ground: 「44 ppu1.3 A」), so no SIZES row
    ("league_cassiopeia", 1.2, include_str!("../../../league/champions/league_cassiopeia#anim.fanim")),
    // Akshan: posed by tools/art/rig_akshan.py at the user's 1.5 squares a game pixel (38 game rows hair to soles, the
    // raised gun above; 「用 A，游戏里 38 像素高，PPU 1.5」), the aim arm and the walk from Codex on the same grid, so no SIZES row
    ("league_akshan", 1.2, include_str!("../../../league/champions/league_akshan#anim.fanim")),
    // Poppy: posed by tools/art/rig_poppy.py at the user's 1.3 squares a game pixel (36 game rows pigtails to soles, the
    // hammer's haft above: 「游戏里 36 像素高，PPU 1.3」); 85 % (SIZES, the user: 「波比在游戏里体型也太大 需要缩小」 - 44 px
    // with the standing hammer against the yordles' 32-40), her frames lowered 2 squares by the restyle (RESTYLE poppy lift_sq)
    ("league_poppy", 1.2, include_str!("../../../league/champions/league_poppy#anim.fanim")),
    // Volibear: posed by tools/art/rig_volibear.py at the user's 1.2 squares a game pixel (44 game rows ear top to soles:
    // 「44 像素，PPU 1.2」), the arm poses, the walk and Q from Codex on the same grid, so no SIZES row
    ("league_volibear", 1.2, include_str!("../../../league/champions/league_volibear#anim.fanim")),
    // Rammus: posed by tools/art/rig_rammus.py from Codex's step-1 takes at the user's 1.2 squares a game pixel (36 game rows
    // spike tips to soles: 「36 像素」「PPU 1.2」; the ball b_* and curl c_* tags the add-on swaps in), so no SIZES row
    ("league_rammus", 1.2, include_str!("../../../league/champions/league_rammus#anim.fanim")),
    // Zoe: posed by tools/art/rig_zoe.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (35 game rows
    // crown to soles: 「35 像素」「PPU 1.5」; skill_w / ult_exit / ult_back the kit's CasterAnimations), so no SIZES row
    ("league_zoe", 1.5, include_str!("../../../league/champions/league_zoe#anim.fanim")),
    // Yuumi: posed by tools/art/rig_yuumi.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (48 game rows
    // orb top to the book's bottom: 「32 像素」「PPU 1.5」), shown at 75 % (SIZES; 「还有模型太大」 -> 「75%（24 像素）」), her frames
    // lowered 6 squares by the restyle (RESTYLE yuumi lift_sq)
    ("league_yuumi", 1.5, include_str!("../../../league/champions/league_yuumi#anim.fanim")),
    // Quinn: posed by tools/art/rig_quinn.py from Codex's redraw of the user's picks at 2.0 squares a game pixel (38 game
    // rows crest to soles: 「38 像素」, then 「像素有点太低了 太多模糊的了 调一下PPU」; her legs drawn on League's bones; the
    // ride r_* tags the add-on swaps in), so no SIZES row
    ("league_quinn", 2.0, include_str!("../../../league/champions/league_quinn#anim.fanim")),
    // Cho'Gath: posed by tools/art/rig_chogath.py at the user's 1.2 squares a game pixel (「38 像素」「PPU 1.2」: Codex's step-1
    // take A-1 cut to 46 rows, the side view redrawn on the grid, Codex's action poses read back at its scale with the
    // idle's head), so no SIZES row; Feast's stacks draw his body bigger (GROWTH)
    ("league_chogath", 1.2, include_str!("../../../league/champions/league_chogath#anim.fanim")),
    // Karthus: posed by tools/art/rig_karthus.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (40 game
    // rows crown to soles: 「40 像素，PPU 1.5」; attack_w is Wall of Pain's cast in the attack, ult the 3 s Requiem), so no
    // SIZES row
    ("league_karthus", 1.5, include_str!("../../../league/champions/league_karthus#anim.fanim")),
    // Vex: posed by tools/art/rig_vex.py from Codex's step-1 takes at the user's 1.5 squares a game pixel (63 game rows from
    // her Shadow's ear tips to her soles, her own 51: 「34 像素」「PPU 1.5」; ult_dash / ult_hit the kit's CasterAnimations),
    // so no SIZES row
    ("league_vex", 1.5, include_str!("../../../league/champions/league_vex#anim.fanim")),
    // Zyra: posed by tools/art/rig_zyra.py on Codex's step-1 take A-1 at 1.7 squares a game pixel (74 game rows hair to
    // soles, her own face: 「提高点ppu像素吧」「脸部完全变形了啊」; every action on the 3/4 design: 「就用四分之三面来做啊」), so no
    // SIZES row
    ("league_zyra", 1.7, include_str!("../../../league/champions/league_zyra#anim.fanim")),
    // Powder (tft_powder, the tft pack in tft/: Teamfight Tactics' own units, its own mod; this DLL draws her dense
    // frames when both packs are enabled): the idle design and Codex's skeleton poses with one clean head, posed by
    // tools/art/rig_powder.py at 1.75 squares a game pixel (61 rows: 「35」, then 「PPU像素好低啊 能调一下吗」), shown at 90 % (SIZES)
    ("tft_powder", 1.75, include_str!("../../../tft/champions/tft_powder#anim.fanim")),
    // 2026-10-16 redo from Codex's pictures, the actions posed from the designs (tools/art/rig_<hero>_hd.py; Nami's after
    // League's own clips, tools/lol/league_joints.py), PPU 1.5 at their old heights, so no SIZES rows
    ("league_morgana", 1.5, include_str!("../../../league/champions/league_morgana#anim.fanim")),
    ("league_nami", 1.5, include_str!("../../../league/champions/league_nami#anim.fanim")),
    ("league_janna", 1.5, include_str!("../../../league/champions/league_janna#anim.fanim")),
    // Jax: Codex's redrawn chibi design facing front-right (assets/source/jax/PICTURE_PROMPT.md), posed after League's own
    // clips by tools/art/rig_jax_hd.py (his run league_braum's walk), PPU 1.5 at his old 36 rows, so no SIZES row
    ("league_jax", 1.5, include_str!("../../../league/champions/league_jax#anim.fanim")),
    // Xin Zhao (2026-10-18): Codex's chibi picture (assets/source/xinzhao/PICTURE_PROMPT_PPU.md) cut to 63 rows, posed
    // after League's own clips by tools/art/rig_xinzhao_hd.py, PPU 1.5 at his old 42 rows, so no SIZES row
    ("league_xinzhao", 1.5, include_str!("../../../league/champions/league_xinzhao#anim.fanim")),
    // Kai'Sa (2026-10-18): Codex's chibi picture (assets/source/kaisa/PICTURE_PROMPT_PPU.md) read back on its own grid,
    // posed after League's own clips by tools/art/rig_kaisa_hd.py (the run's legs Codex's redraw), PPU 1.45 at her old 42
    // rows, so no SIZES row
    ("league_kaisa", 1.45, include_str!("../../../league/champions/league_kaisa#anim.fanim")),
    // Camille (2026-10-18): Codex's design picture (assets/source/camille/PICTURE_PROMPT_PPU.md) read back on its own
    // grid and cut to 69 rows, the upper body posed after League's own clips by tools/art/rig_camille_hd.py, the legs of
    // her kicks and leaps Codex's drawing along League's guides, PPU 1.5 at her old 46 rows, so no SIZES row
    ("league_camille", 1.5, include_str!("../../../league/champions/league_camille#anim.fanim")),
    // Fiora (2026-10-18): Codex's design picture (assets/source/fiora/PICTURE_PROMPT_PPU.md) read back on one fitted
    // grid and cut to 60 rows with her whole head kept, posed after League's own clips by tools/art/rig_fiora_hd.py (the
    // blade drawn straight, the legs of her steps and lunges drawn on League's bones in the design's colours), PPU 1.5
    // at her old 40 rows, so no SIZES row
    ("league_fiora", 1.5, include_str!("../../../league/champions/league_fiora#anim.fanim")),
    // LeBlanc: PPU 2.0 (「PPU 2.0 原样」) - Codex's take A of 2026-10-02 as drawn (51 x 86 squares, the staff straightened),
    // posed after League's clips by tools/art/rig_leblanc_hd.py, the run on Codex's legs
    ("league_leblanc", 2.0, include_str!("../../../league/champions/league_leblanc#anim.fanim")),
    // Darius (2026-10-18): Codex's design picture (assets/source/darius/PICTURE_PROMPT_PPU.md) read back on its own
    // grid, nothing cut (56 x 61), posed after League's own clips by tools/art/rig_darius_hd.py (the axe hand and the axe
    // turned losslessly, the run on his own legs moved whole), PPU 1.45 at his old 42 rows, so no SIZES row
    ("league_darius", 1.45, include_str!("../../../league/champions/league_darius#anim.fanim")),
    // Riven (2026-10-18): Codex's design picture (assets/source/riven/PICTURE_PROMPT_PPU.md) read back on its own grid
    // (68 x 61), her sword one of Codex's angle drawings in her fist (tools/art/swords_riven_hd.py); idle, run, ult, hit
    // and death posed after League's clips by tools/art/rig_riven_hd.py, her three attacks (taking turns), Broken Wings
    // and Valor Codex's whole-frame redraws (tools/art/actions_riven_hd.py); PPU 1.5 at her old 40 rows, so no SIZES row
    ("league_riven", 1.5, include_str!("../../../league/champions/league_riven#anim.fanim")),
    // Yunara: PPU 1.5 (the user's pick), posed from the design's own squares at that density by tools/art/rig_yunara.py
    // (40 game rows ornaments to soles), so no SIZES row
    ("league_yunara", 1.5, include_str!("../../../league/champions/league_yunara#anim.fanim")),
];

/// Champion id, its size everywhere the dense frames are drawn (1.0 = the 1x frames' size): the anim tables' rects and
/// the texture's reported size are divided by PPU / size (src/lookup.rs: the cards, the encyclopedia, the face icons,
/// the BP slots draw him that much smaller, the UVs unchanged) and the battlefield scale is the game's / PPU x size
/// (src/view.rs), each about the frame's centre / the unit's position - so the hero's dense frames are drawn lower by
/// (1 / size - 1) x the pivot-to-soles distance and the soles stay where they were (tools/art/ppu_gragas.py SHIFT).
/// Gragas: the user, 2026-10-12: 「酒桶模型缩小一点 太大了」 (85%), then 「要改全改啊」, then 80% (「怎么看起来还是比诺手高这么多」) (the cards and the encyclopedia too);
/// 2026-10-13 after the restyle 「酒桶可以稍微放大点吧 现在也太小了」 -> 90% from a size sheet, then 「还是太小啊」 -> 100% - judged on a preview GIF that
/// drew him at 80% - then 「感觉又太大了？」 from a true-scale sheet -> 90% (40 game px, Darius 42); his frames
/// lifted by the restyle (RESTYLE gragas lift_sq).
/// Zeri: 「等等泽丽感觉游戏里有点小」, picked 105% from the size sheet (drawn RAISE rows higher: tools/art/ppu_zeri.py).
/// Kassadin: 「在游戏太小了吧」, picked 115%, then 「感觉太大了点？调到110%差不多吧」 (41 game px); after the restyle
/// 「刀妹和卡萨丁感觉在游戏里偏大啊」 -> 100% (39 game px; RESTYLE kassadin lift_sq -3 undoes the rig's 110% raise) and Irelia
/// 115% -> 105% (44 game px with her blades); his hd frames drawn RAISE
/// rows higher (tools/art/rig_kassadin.py).
/// Braum: 「布隆做的也有点大 得缩小一点」 (85%), then 「稍微调大点」 (90%, 39 game px); after the restyle (a tenth
/// shorter) 「布隆也有这个看起来小的问题」 next to Alistar -> 105% (the user took the suggestion: 「按照你的建议选吧」).
/// His hd frames come SHIFT rows lower from tools/art/rig_braum.py (its 90%) and the restyle lifts them back
/// (tools/art/ppu_restyle.py RESTYLE braum lift).
/// Mordekaiser: the user picked 110% with a thicker outline (C, Kassadin's way), then 「铁男感觉做的太大了吧？」 -> 95%,
/// then 「铁男再稍微调大点」 -> 100%; then 「为什么模型看起来小啊 牛头那种就看起来很大」「铁男再游戏里还是过于高清」 ->
/// 115% at PPU 2.0 (1.74 squares a game pixel), his frames lifted by the restyle (RESTYLE mordekaiser lift).
/// Then 「铁男和布隆游戏里偏大了」: Mordekaiser 100 % (47 game px, Nautilus 51), Braum 95 % (39 px, 55 wide with his
/// shield), picked from a true-scale sheet; their frames moved down by the restyle (RESTYLE lift_sq).
/// Then on game 0.6.4 (2026-10-14) 「铁男模型太小」「铁男到110%吧」: Mordekaiser 110 % (52 game px).
/// Soraka: 「稍微变大点」 -> 110% (her frames lifted 3 squares: tools/art/ppu_restyle.py RESTYLE soraka).
/// Nilah: 「模型别太大 参考泽丽之前改过一版」 -> 90% from a size sheet (about 38 game rows with the blade's tip); her frames
/// lowered 3 squares by the restyle (RESTYLE nilah lift_sq).
/// Galio: PPU 2.0 at 85 % first (「这做的也太大了吧 缩小点模型」), then 「加里奥在局内看起来太小了」「而且在局内还是太高清了」 ->
/// 100 % at PPU 1.5 (tools/art/rig_galio.py dense), picked from true-scale sheets; then 「在局内还是偏小啊」 (38 game px
/// crown to soles, Darius 42) -> 110 % at PPU 1.65 (still 1.5 squares a game pixel), his dense frames drawn RAISE rows higher (rig_galio.py
/// SIZE / RAISE).
/// Corki: grown 1.2x by the restyle (「飞机像泽丽那样变大点」), then 「飞机在游戏里是不是偏大了？」 - 48 x 37 game px, as wide as
/// Garen and a solid lump - shown at 80 % (「到80%吧」, from a true-scale sheet), then 「太小了库奇 调到90%吧」 -> 90 %;
/// he flies, so his frames are not lowered.
/// Pantheon: 90 % for a while (「感觉模型太大了」「缩到90%」, his upright design idle 46 px), then his idle took Codex's crouched
/// ready stance like every action and he is 100 % again (「局内模型为什么变这么小了」: running 32-36 px against Darius's 41).
/// Malzahar: 115 % from the size sheet (all actions from the 3/4 front), drawn at PPU 2.2 first, then 「像素有点高 降低点需要」 ->
/// PPU 1.38 (1.2 squares a game pixel at 115 %); he floats, his frames lifted by the restyle (RESTYLE malzahar lift).
/// Powder (tft_powder): 90 % (the user, 2026-10-19: 「人物模型太大 缩小一点」), her frames 2 squares lower (RESTYLE powder lift).
pub const SIZES: &[(&str, f32)] = &[("league_gragas", 0.90), ("league_zeri", 1.05), ("league_kassadin", 1.00),
                                    ("league_braum", 0.95), ("league_mordekaiser", 1.10),
                                    ("league_irelia", 1.05), ("league_soraka", 1.10), ("league_galio", 1.10), ("league_nilah", 0.90),
                                    ("league_corki", 0.90), ("league_malzahar", 1.15), ("league_aphelios", 0.90),
                                    ("league_poppy", 0.85), ("league_yuumi", 0.75),
                                    ("tft_powder", 0.90)];

/// Heroes whose body grows with a stack: (id, the buff whose instances on him are the stacks, growth a stack). Cho'Gath's
/// Feast (the user, 2026-10-19: 「变大可以无限 加生命」): every champion it eats is one more Permanent `league_chogath_r_stack`
/// on him (+health, tools/kit/build_chogath.py r_stack_hp) and his body is drawn r_grow % bigger a stack, no cap, about
/// his soles (src/view.rs: only the body's own commands, so his shadow and rings stay). The main pack loses the stacks
/// at his death (Permanent buffs end with it); the add-on league_chogath puts them back.
pub const GROWTH: &[(&str, &str, f32)] = &[("league_chogath", "league_chogath_r_stack", 0.05)];

/// Game pixels from a frame's centre (the unit's position) down to its soles (tools/art/ppu_rig.py FEET).
pub const FEET: f32 = 11.5;

/// The body's growth for `stacks` stacks of a GROWTH row (1.0 for none).
pub fn grown(per: f32, stacks: usize) -> f32 {
    1.0 + per * stacks as f32
}

/// Effect sheets drawn dense like a hero's sheet (tags `idle` / `hd_idle` only, PPU squares a game pixel, hd_idle PPU times
/// as wide): league_yuumi_ride, the cat lying on her book on the head of the ally Yuumi rides (the user: 「1.5 倍（21 格）」
/// for the 14-px picture; tools/art/import_yuumi_fx.py), league_zyra_thicket (below). Looked up like the heroes (src/lookup.rs); the battlefield's
/// entity scale (src/view.rs) never meets them - they are no entity's body.
pub const EFFECTS: &[(&str, f32, &str)] = &[
    ("league_yuumi_ride", 1.5, include_str!("../../../league/effects/league_yuumi_ride#anim.fanim")),
    // league_zyra's R thicket: Codex's squares 3 x 3 at PPU 2, 1.5 game px each - the picture 1.5 times as big for R's
    // radius 44000 (the user: 「R技能范围做大点」「不用重画啊 你调整一下不就行了吗」; tools/art/import_zyra_fx.py)
    ("league_zyra_thicket", 2.0, include_str!("../../../league/effects/league_zyra_thicket#anim.fanim")),
];

pub const PREFIX: &str = "hd_";

/// `lo_<tag>`: the same frames at [`UI_PPU`] squares a displayed game pixel (tools/art/ppu_hd.py add_lo) - what the BP
/// grid, the encyclopedia, the pick slots and the pick moment draw (src/lookup.rs ui_table; the user, 2026-10-13:
/// 「BP界面里看英雄还是太清晰」, picked the 1.5 row of the preview). The battlefield keeps the hd_ frames.
pub const LO_PREFIX: &str = "lo_";
pub const UI_PPU: f32 = 1.5;

/// Tall heroes drawn smaller wherever the UI draws lo_ frames (the ban/pick card above all): the card's canvas holds
/// about 40 game px at 2.2x and these idles are 45-58 px from the head to the feet, so the knees and feet hid behind
/// the name bar (the user, 2026-10-19: 「烈娜塔在BP格位置调一下吧 一半的腿 还有其他英雄也有这情况」, picked the
/// whole-body mock). Size = 39 / the idle's height, every HD hero whose card hid 6 px or more
/// (tools/art/bp_card_audit.py --legs); their banpick_center y set for that size. 1x heroes have no lo_ frames: not here.
pub const UI_SIZES: &[(&str, f32)] = &[
    ("league_camille", 0.82),
    ("league_cassiopeia", 0.85),
    ("league_drmundo", 0.87),
    ("league_elise", 0.80),
    ("league_galio", 0.67),
    ("league_janna", 0.81),
    ("league_jayce", 0.78),
    ("league_mordekaiser", 0.74),
    ("league_morgana", 0.84),
    ("league_nami", 0.76),
    ("league_nasus", 0.85),
    ("league_nidalee", 0.87),
    ("league_rell", 0.85),
    ("league_renata", 0.78),
    ("league_tahmkench", 0.87),
    // Zyra (#140): 43.5 game rows hair to soles at PPU 1.7 - 12.7 px of her legs hid under the card's canvas
    ("league_zyra", 0.89),
];

/// The `"lo_..."` animation names of a .fanim.
pub fn lo_tags(fanim: &str) -> Vec<String> {
    keys_with(fanim, LO_PREFIX)
}

/// The `"hd_..."` animation names of a .fanim (its keys under "anims"; no frame key starts with hd_).
pub fn hd_tags(fanim: &str) -> Vec<String> {
    keys_with(fanim, PREFIX)
}

fn keys_with(fanim: &str, prefix: &str) -> Vec<String> {
    let mut out = Vec::new();
    let b = fanim.as_bytes();
    let mut i = 0;
    while let Some(off) = fanim[i..].find('"') {
        let start = i + off + 1;
        let Some(len) = fanim[start..].find('"') else { break };
        let end = start + len;
        let name = &fanim[start..end];
        let mut j = end + 1;
        while j < b.len() && b[j].is_ascii_whitespace() {
            j += 1;
        }
        if j < b.len() && b[j] == b':' && name.starts_with(prefix) && !out.iter().any(|t| t == name) {
            out.push(name.to_string());
        }
        i = end + 1;
    }
    out
}

/// A registered hero: its PPU and the plain tags that have an hd copy.
pub struct Hero {
    pub id: &'static str,
    pub ppu: f32,
    /// the size it is shown at (SIZES; 1.0 when not listed)
    pub size: f32,
    pub tags: Vec<String>,
    /// the sheet has lo_ frames for every tag (the UI draws those)
    pub lo: bool,
    /// what the whole-body UI (the pick slot, the BP grid, the pick moment) divides a lo_ frame's pixels by:
    /// [`UI_PPU`] / its [`UI_SIZES`] size; the encyclopedia / face icons and the scoreboard divide by [`UI_PPU`]
    /// ([`Hero::ui_for`])
    pub ui: f32,
}

impl Hero {
    /// What a dense frame's pixels are divided by to give its shown size: PPU / size.
    pub fn shown(&self) -> f32 {
        self.ppu / self.size
    }

    /// The UI's divisor for a caller: `sized` (a whole-body drawer, src/build.rs ui_sized_*) takes the UI_SIZES size,
    /// the face crops (encyclopedia / face icons, scoreboard portraits) the plain [`UI_PPU`] - their face point is
    /// measured on the hero at that size (2026-10-20: Galio's and Mordekaiser's icons showed a crown / a belly).
    pub fn ui_for(&self, sized: bool) -> f32 {
        if sized { self.ui } else { UI_PPU }
    }
}

pub fn heroes() -> Vec<Hero> {
    HEROES
        .iter()
        .chain(EFFECTS.iter())
        .map(|&(id, ppu, fanim)| Hero {
            id,
            ppu,
            size: SIZES.iter().find(|s| s.0 == id).map_or(1.0, |s| s.1),
            tags: hd_tags(fanim).into_iter().map(|t| t[PREFIX.len()..].to_string()).collect(),
            lo: !lo_tags(fanim).is_empty(),
            ui: UI_PPU / UI_SIZES.iter().find(|s| s.0 == id).map_or(1.0, |s| s.1),
        })
        .collect()
}

/// The registered heroes, found by id with one hash lookup. The hooks ask for every resource the game looks up by name
/// and every entity on the battlefield each frame; a walk down the list compared up to 55 names, twice for each lookup
/// (2026-10-19 profile: league.dll's own time on the render thread was mostly that walk).
pub struct Heroes {
    pub list: Vec<Hero>,
    by_id: std::collections::HashMap<&'static str, usize>,
}

impl Heroes {
    pub fn new() -> Self {
        let list = heroes();
        let by_id = list.iter().enumerate().map(|(k, h)| (h.id, k)).collect();
        Heroes { list, by_id }
    }

    pub fn get(&self, id: &str) -> Option<&Hero> {
        // every registered id starts with league_ or tft_ (the tft pack's heroes): the base heroes, effects and UI names
        // go without hashing
        if !id.starts_with("league_") && !id.starts_with("tft_") {
            return None;
        }
        self.by_id.get(id).map(|&k| &self.list[k])
    }

    /// The hero a resource name is of: `.../league_yasuo#anim` (or the bare id) -> league_yasuo.
    pub fn of_name(&self, name: &str) -> Option<&Hero> {
        self.get(name.rsplit('/').next()?.split('#').next()?)
    }
}

impl Default for Heroes {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn heroes_are_found_by_id_and_resource_name() {
        let h = Heroes::new();
        assert_eq!(h.list.len(), HEROES.len() + EFFECTS.len());
        for &(id, ..) in HEROES {
            assert_eq!(h.get(id).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/league/champions/{id}#anim")).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/base/aseprite_resources/champions/{id}#sheet")).map(|x| x.id), Some(id));
        }
        assert!(h.get("league_lux").is_none());
        assert_eq!(h.get("tft_powder").map(|x| (x.id, x.size)), Some(("tft_powder", 0.90)));
        assert!(h.get("tft_nobody").is_none());
        assert!(h.of_name("asset/base/aseprite_resources/champions/alchemist#anim").is_none());
        assert!(h.of_name("asset/league/champions/league_ashe_fx#sheet").is_none());
        assert!(h.of_name("").is_none());
    }

    #[test]
    fn every_registered_sheet_has_hd_tags_for_all_its_tags() {
        for &(id, ppu, fanim) in HEROES {
            let hd = hd_tags(fanim);
            assert!(!hd.is_empty(), "{id}: no hd_ tags in its sheet (python tools/art/ppu_hd.py)");
            assert!(ppu > 1.0);
            // the plain tags: every top-level anim name that is not hd_
            let anims = &fanim[fanim.find("\"anims\"").unwrap()..];
            for t in ["idle", "run", "attack", "hit", "dead"] {
                assert!(anims.contains(&format!("\"{t}\"")), "{id}: no {t}");
                assert!(hd.contains(&format!("{PREFIX}{t}")), "{id}: no {PREFIX}{t}");
            }
            // lo_ frames: none, or one for every hd_ tag (the UI table maps every tag to its lo_ frames)
            let lo = lo_tags(fanim);
            if !lo.is_empty() {
                for h in &hd {
                    let want = format!("{LO_PREFIX}{}", &h[PREFIX.len()..]);
                    assert!(lo.contains(&want), "{id}: no {want} (python tools/art/ppu_hd.py --hero ...)");
                }
            }
        }
    }

    #[test]
    fn ui_sizes_shrink_heroes_with_lo_frames() {
        let h = Heroes::new();
        for &(id, size) in UI_SIZES {
            let hero = h.get(id).unwrap_or_else(|| panic!("{id}: not a registered hero"));
            assert!(hero.lo, "{id}: no lo_ frames - the UI draws its 1x frames, a UI size would not reach them");
            assert!(size > 0.5 && size < 1.0, "{id}: {size}");
            assert!((hero.ui - UI_PPU / size).abs() < 1e-6);
        }
        assert_eq!(h.get("league_zoe").map(|x| x.ui), Some(UI_PPU));
        // the face crops keep the plain UI size, so a hero's face point holds there too
        let galio = h.get("league_galio").unwrap();
        assert_eq!(galio.ui_for(false), UI_PPU);
        assert!(galio.ui_for(true) > UI_PPU);
    }

    #[test]
    fn effect_sheets_have_a_dense_idle() {
        let h = Heroes::new();
        for &(id, ppu, fanim) in EFFECTS {
            assert!(ppu > 1.0);
            assert_eq!(hd_tags(fanim), vec![format!("{PREFIX}idle")], "{id}: only idle / hd_idle (src/lookup.rs densify_table)");
            assert!(fanim.contains("\"idle\""), "{id}: no idle");
            assert!(lo_tags(fanim).is_empty(), "{id}: no UI frames for an effect");
            assert_eq!(h.of_name(&format!("asset/league/effects/{id}#anim")).map(|x| x.id), Some(id));
            assert_eq!(h.get(id).map(|x| x.size), Some(1.0), "{id}: an effect is never resized");
        }
    }

    #[test]
    fn tags_are_read_from_a_fanim() {
        let f = r#"{"anims":{"idle":{"frames":[{"duration":0.1,"data":{"x":0.0}}]},"hd_idle":{"frames":[]},"hd_run" : {}}}"#;
        assert_eq!(hd_tags(f), vec!["hd_idle".to_string(), "hd_run".to_string()]);
    }
}
