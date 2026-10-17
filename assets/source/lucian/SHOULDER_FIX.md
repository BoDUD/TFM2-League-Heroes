# 卢锡安：补后肩（13 帧，给 Codex）

> 用户看技能动作时指出：**“卢锡安怎么释放技能的释放模型变形了……肩膀那里失去一块”**。
> 凡是双枪都朝前的帧——**Q 第 2–5 帧、R 第 1–4 帧、被动连开两枪第 2–6 帧**，共 13 帧——脖子左边（画面左边，他的右肩，他朝右站）的**后肩没有画**：头的左下方、米白高领的上面和左边是空的背景，躯干像被咬掉了一块。待机里这个位置是他举起的那条手臂（一把枪举在头边），所以待机看得到肩膀；动作里那条手臂放下来去握第二把枪，肩膀就跟着没了。待机的上臂是朝上的，不能直接贴过来。
> **这一轮只补后肩和上臂**：其余每一格都和第一张图（`_1_now`）一模一样——头、脸、双枪、枪口闪光、外套、腿、位置都不动。
> 每帧交一张图：`lucian_<动作>_<帧>.png`（如 `lucian_skill_3.png`、`lucian_ult_1.png`、`lucian_passive_6.png`），和第一张图同样大小（768×768，就是这一格的 96×96 方块放大 8 倍）、人物在同一位置，透明底（做不到就纯品红 `#FF00FF`）。附 `HANDOFF.md`（用了哪段提示词、每帧补了哪些格、哪里没做到）。

## 后肩的规矩（每帧都要）

- **只在青色框里、现在是空的格子上画**（`_2_guide`）。框外的格子、框里已经有颜色的格子（高领、头、零星的金色小块）一格都不改。
- 画的是**他的后肩和上臂**：一块圆的肩头，从下巴的高度（不高过嘴）往左鼓出，比头的左边缘再往外 2–3 格，往下接上米白高领和外套，没有缺口；上臂从肩头往右（朝前）伸向双枪，藏在胸口和近侧手臂的后面，所以只露出肩头和上臂的开头（看引导图的虚线箭头）。
- 材质照待机和定稿：白外套的肩（米白 `#F3E6D1` / `#CFC1B4`，金边 `#CBA04B` / `#B48D3E`），袖子是深色（`#28272F` / `#2F2D36` / `#3A3A42`）；看 `lucian_idle.png` 里头左边那块肩和高领、英雄联盟那帧里肩上的白色肩甲和金边。
- **只用定稿的 19 色**：#181118 #2D2327 #28272F #2F2D36 #432541 #423536 #4F352C #3A3A42 #562E48 #77532D #3F6A74 #955F44 #66717C #B48D3E #CBA04B #A29690 #CFC1B4 #F3E6D1 #F4F2EA。不加新颜色；虹膜 `#3F6A74` 和眼白 `#F4F2EA` 只在眼睛上。
- **一圈近黑描边**（`#181118`）：新肩膀外面一格宽，和原来的剪影描边接上；里面的边和褶皱用材质自己最暗的色阶，不要第二圈黑。
- 每格一个纯色 8×8 方块，不抗锯齿、不半透明、不抖动、没有孤立的杂色格；什么都不能低于脚底线。

## 附图（每帧三张，另有两张共用）

| 文件 | 内容 |
|---|---|
| `<动作>_<帧>_1_now.png` | 这一帧现在的样子：这一格 96×96 方块放大 8 倍（768×768），灰底 `#E1E1E1` 是空的背景。**除了新肩膀，交回的图每一格都要和它一样** |
| `<动作>_<帧>_2_guide.png` | 同一帧：青色框（淡青底）是后肩要画的地方（现在都是空格），虚线箭头是上臂从肩头伸向双枪、藏在胸口和近侧手臂后面。青色框、箭头和字都不要画进图里 |
| `<动作>_<帧>_3_league.png` | 英雄联盟同一帧的渲染（同一格、同一站位点）：肩膀在哪、两条手臂怎么从两肩伸向双枪。Q 第 5 帧附的是英雄联盟第 4 帧（它的第 5 帧已经把枪举起来，我们的第 5 帧还是平举） |
| `lucian_idle.png` | 待机第 1 帧（8 倍，灰底）：后肩、高领、外套在头左边的样子 |
| `lucian_design.png` | 定稿（8 倍）：颜色、外套、肩和金边以它为准 |
| `guide_areas.json` | 每帧青色框的格子数和范围（格子坐标，从这一格左上角数） |

## 提示词（每帧一张，只替换 [pose] 和 [frame]）

每张附五张图：`<动作>_<帧>_1_now.png`、`<动作>_<帧>_2_guide.png`、`<动作>_<帧>_3_league.png`、`lucian_idle.png`、`lucian_design.png`。

```text
Five attached images. FIRST: this frame of the game sprite as it is now (pixel art at 8x: one 96x96-square cell, 768x768 px, every square 8x8 px; the light grey is empty background). SECOND: the same frame with a cyan GUIDE: the cyan-outlined, lightly tinted squares are where his BACK SHOULDER is missing (they are empty now), and the dashed cyan arrow is his upper arm reaching from that shoulder forward to the pistols, hidden behind his chest and the near arm (the guide is only a guide - do not draw it). THIRD: the same moment of the original 3D animation - where his shoulders are and how both arms come forward to the pistols. FOURTH: his idle frame (8x) - how his shoulder, high collar and white coat look left of his head. FIFTH: the approved design (8x) - his colors and the coat's shoulder with its gold trim.
Task: return this ONE frame exactly as the FIRST image, square for square, and ADD ONLY his back shoulder (the shoulder on the left of the image, left of his neck) and the start of his upper arm, drawn ONLY on the empty squares inside the cyan area. Every other square stays exactly as in the FIRST image: the head and face, both pistols and their muzzle flashes, the arms, the cream collar, the coat, the legs, and the place of the figure in the cell - do not move, redraw, recolor or clean up anything else.
The shoulder: a rounded shoulder cap of the white coat with its gold trim, starting at chin height (never higher than his mouth), bulging out to the left 2-3 squares beyond the left edge of his head and running down into the cream collar and the coat with no gap or notch; his upper arm leaves it going right, forward toward the pistols, and disappears behind his chest and the near arm, so only the shoulder cap and the start of the upper arm show (dark sleeve as in the FOURTH image). It must read as his torso's full shoulder line, matching the other shoulder, like the FOURTH image and the THIRD image's white shoulder plate.
Pixel rules: every square one crisp flat 8x8 block on the same grid as the FIRST image, no anti-aliasing, no blur, no semi-transparency, no dithering, no lone odd-colored squares; only these 19 colors: #181118 #2D2327 #28272F #2F2D36 #432541 #423536 #4F352C #3A3A42 #562E48 #77532D #3F6A74 #955F44 #66717C #B48D3E #CBA04B #A29690 #CFC1B4 #F3E6D1 #F4F2EA; the eye colors #3F6A74 and #F4F2EA nowhere but the eyes. ONE 1-square near-black (#181118) outline around the new shoulder, joining the existing outline; inside it the material's own darkest shade, never a second ring of black.
Pose: [pose] Frame: [frame]
Output: the whole 768x768 cell like the FIRST image, the figure in the same place, transparent background (if not possible: solid #FF00FF magenta). No guide, no text, no grid, no ground, no shadow, no effects added.
```

`[pose]`：
- skill：`Piercing Light (Q): both pistols held level at shoulder height, pointing right, firing a beam straight ahead; he is turned a little side-on and braced.`
- ult：`The Culling (R): planted wide stance, both pistols held forward at chest height, rapid fire one after the other.`
- passive：`Lightslinger (double shot): both pistols pointing forward at shoulder height, one a little above the other, firing one after the other.`

## 十三帧的 [frame]

- `lucian_skill_2.png`（附 `skill_2_1_now.png`、`skill_2_2_guide.png`、`skill_2_3_league.png`）：`SKILL frame 2: bracing: both pistols pushed forward together at shoulder height.`
- `lucian_skill_3.png`（附 `skill_3_1_now.png`、`skill_3_2_guide.png`、`skill_3_3_league.png`）：`SKILL frame 3: both pistols level at shoulder height, a faint glow gathering at the muzzles.`
- `lucian_skill_4.png`（附 `skill_4_1_now.png`、`skill_4_2_guide.png`、`skill_4_3_league.png`）：`SKILL frame 4: THE BEAM: a bright flash at both muzzles, pistols level at shoulder height (keep the flash as it is).`
- `lucian_skill_5.png`（附 `skill_5_1_now.png`、`skill_5_2_guide.png`、`skill_5_3_league.png`）：`SKILL frame 5: holding the shot, a slight recoil, both pistols still forward.`
- `lucian_ult_1.png`（附 `ult_1_1_now.png`、`ult_1_2_guide.png`、`ult_1_3_league.png`）：`ULT frame 1: the upper pistol kicks up with a small muzzle flash, the lower one level.`
- `lucian_ult_2.png`（附 `ult_2_1_now.png`、`ult_2_2_guide.png`、`ult_2_3_league.png`）：`ULT frame 2: both pistols level, forward at chest height.`
- `lucian_ult_3.png`（附 `ult_3_1_now.png`、`ult_3_2_guide.png`、`ult_3_3_league.png`）：`ULT frame 3: the lower pistol fires with a small muzzle flash, the upper one level.`
- `lucian_ult_4.png`（附 `ult_4_1_now.png`、`ult_4_2_guide.png`、`ult_4_3_league.png`）：`ULT frame 4: both pistols level, forward at chest height.`
- `lucian_passive_2.png`（附 `passive_2_1_now.png`、`passive_2_2_guide.png`、`passive_2_3_league.png`）：`DOUBLE SHOT frame 2: the rear pistol has come down: both pistols point forward at shoulder height.`
- `lucian_passive_3.png`（附 `passive_3_1_now.png`、`passive_3_2_guide.png`、`passive_3_3_league.png`）：`DOUBLE SHOT frame 3: the upper pistol fires (kicked up, small muzzle flash), the lower one level.`
- `lucian_passive_4.png`（附 `passive_4_1_now.png`、`passive_4_2_guide.png`、`passive_4_3_league.png`）：`DOUBLE SHOT frame 4: the upper pistol back level; both point forward.`
- `lucian_passive_5.png`（附 `passive_5_1_now.png`、`passive_5_2_guide.png`、`passive_5_3_league.png`）：`DOUBLE SHOT frame 5: the lower pistol fires (small muzzle flash), the upper one level.`
- `lucian_passive_6.png`（附 `passive_6_1_now.png`、`passive_6_2_guide.png`、`passive_6_3_league.png`）：`DOUBLE SHOT frame 6: both pistols level, pointing forward.`

## Claude 导入时（给 Claude 看）

- 交回的每张图按 8×8 方块逐格读回（先找网格，取每格中心色，映射到定稿 19 色；品红或透明是空）。
- 按两只眼睛（虹膜 `#3F6A74`）对到 `assets/source/native/lucian_<动作>.png` 原帧的眼睛，再用站位点 / 脚底线核对一遍，不按图的边缘对位。
- **只取新肩膀**：只取原帧里是空、又落在本包青色框（`guide_areas.json`，即`tools/art/lucian_shoulder.py` 的 `area()`）里的格子；原帧已有颜色的格子一格不动，框外 Codex 改动的格子全部丢掉。之后只在新肩膀外缘补一圈描边（`strips.complete_outline` 只作用在新加的格子上），检查新格子和身体连成一块、没有孤立格。
- 写回原条的同一格，重跑 `import_native.py --hero lucian` 和 `preview_lucian.py`；导入前后的 13 帧并排给用户看（游戏尺寸 + 放大），重钉 PR 里的 GIF。
