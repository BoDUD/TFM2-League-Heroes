# 斯莫德：在游戏格子上整张重画 B-01（第 1 步，给 Codex 的提示词）

> 上一轮（第 0 步）你交了 5 张，用户选了 **B-01**（`2_look_B01.png`，四条腿站着、大头、尾巴卷起来）。它的长相、配色、姿势都对，但它是约 **8 px 一格**、从角尖到脚底约 110 格；游戏里要的是 **48 格**（高清 PPU 1.5，游戏里约 32 像素高）。我按格子把它缩下来以后，**眼睛、小白牙、青绿鳞刺全糊了**。以前的英雄（格温、泽丽）碰到同样的问题，都是你**直接在游戏格子上整张重画**后变干净的（`4_example_picture.png` / `5_example_sprite.png` 是格温那次你交的图）。这一轮请照那次的做法，**只画一张正面（3/4 朝右）**，用户说不要侧面，之后所有动作都从这一张做：
>
> - 把 B-01 在 **16 × 16 px 的固定格子**上重画一遍（画布 1536 × 1024 横版 = **96 列 × 64 行**，格子从左上角对齐）。**大小、比例、姿势、位置完全照 `1_layout_grid.png`**（就是 B-01 本身，已经按比例放到格子上）：**两只小角的尖在第 11 行，脚底最低一行在第 58 行（共 48 格高）**，头顶的两小撮火苗在第 8–10 行；尾巴尖最左在第 19 列附近，前脚最右在第 76 列附近。每 16 × 16 px 一个颜色（原来 8 px 一格，现在格子大了一倍，细节要按新格子**重新安排**，不是把原图缩小）。
> - **最重要的是脸**（照 `2_look_B01.png` 和 `3_league_head.png`）：**两只大大的青绿色眼睛**，每只**至少 5 × 4 格**：近黑眼眶、白眼白、青绿虹膜、深色瞳孔、一格白亮点，两只眼睛清清楚楚；**咧嘴笑**，嘴是一条近黑的弧线，露出 **2–3 颗一格大的小白牙**；杏橙色的脸、奶油色的下巴和喉咙；头两侧的扇形大耳鳍、一排**青绿色叶片鳞刺**（每片至少 2 × 3 格，片与片之间有深色分开）、深红鳞冠中间一道紫色；两只短短的**青绿小角**，角尖上**两小撮橙黄火苗**（每撮约 3 × 3 格，硬边，不要光晕）。
> - **身体照 B-01**：四条腿站稳，**近侧（画面左边那条前腿）亮、远侧稍暗**，远侧后腿被身体挡住可以只露一点；奶油色横鳞肚子（3–4 道横纹）；翅膀收起来披在背上像斗篷（外面深海军蓝 / 深紫 + 一排青绿大鳞，往下渐变成深红 → 粉红，下摆几片尖）；前腿深酒红 + 前面一列深蓝紫鳞甲；**每只脚 3–4 个深蓝色小爪**，脚底平平地落在第 58 行；尾巴从屁股后面往上卷，上面红、下面杏色，尾巴尖一片深蓝色的大尾鳍，**不碰地面**。
> - **干净**（和格温那次一样）：每格一个颜色，大块平涂，每种材质 3–4 档；外轮廓一圈 **2 格宽的近黑描边**，里面少用黑；**不要小于一格的细节、不要碎点、不要半格、不要渐变抖动**；最多约 28 色；真透明背景（**全硬 alpha，只有 0 和 255**，不要半透明雾、不要光晕）。
> - 不画任何特效（只有头顶两小撮火苗算身体）、地面、影子、文字；**不要画黄色量格线和红线**。
> - 交付：`outputs/smolder-model/smolder-front.png`（1536 × 1024），再附一张 **1 倍读回图** `smolder-front_1x.png`（96 × 64，一格一个像素）；`generation-prompts.txt`；**所有原始生成稿原样放 `raw/`**（不要缩小、不要重描）；**最后**写 `HANDOFF.md`。如果一次画不准，可以多画几张（`smolder-front-2.png` …），都交上来让用户挑。

## 附图（压缩包 `smolder_model_pack.zip` 里，按顺序附上；一次最多附五张就先附 1、2、3、4、5，再画一张时可以换成 1、2、6、7、10）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_layout_grid.png` | B-01 放在 16 px 格子上（黄线量格子用；红线 = 第 11 行角尖、第 58 行脚底） | **大小、比例、姿势、位置**（不要画黄线、红线） |
| `2_look_B01.png` | B-01 原稿（用户选的） | 长相、配色、部件 |
| `3_league_head.png` | 英雄联盟里他的头（本地渲染） | 大眼睛、笑脸小白牙、鳞冠、耳鳍、鳞刺 |
| `4_example_picture.png` | 格温：你上次在格子上重画的图（用户认可，26 px 一格） | 怎么画：每格一个颜色 |
| `5_example_sprite.png` | 同一张的 1 倍图放大 8 倍 | 干净程度 |
| `6_style_galio.png` … `9_style_nidalee.png` | 包里 1.5 密度的英雄（8 倍放大，一格 = 一个像素） | 质量标准、描边粗细、眼睛的画法（泽丽） |
| `10_league_stand.png` | 英雄联盟里他四条腿站着，3/4 朝右 | 腿和脚怎么站 |

## 提示词：`smolder-front.png`

附图 1、2、3、4、5。

```text
Five attached images. Image 1 is the approved picture of this character placed on a measuring grid of 16x16-pixel squares (yellow lines; red lines mark row 11 and row 58): its SIZE, PROPORTIONS, POSE and PLACE are exactly what to keep - but it was drawn on small ~8-pixel squares and must now be drawn again on the BIG 16-pixel grid. Image 2 is the same picture without the grid: the LOOK to copy (shapes, colours, parts). Image 3 is the character's head on his in-game 3D model: the big eyes, the grin with small teeth, the crest, the ear fins, the leaf-like spikes. Image 4 is another character redrawn correctly on such a grid, and image 5 that sprite at 1x enlarged - copy that way of working: every square one flat colour, big clean areas, no half squares, no soft edges.
Create ONE pixel-art picture of Smolder, a 1536x1024 LANDSCAPE PNG with a real, fully transparent background (hard alpha only: 0 or 255, no haze, no glow), drawn on a FIXED GRID of 16x16-pixel squares aligned to the canvas's top-left corner (96 columns x 64 rows). Every square is exactly one flat colour. The figure is exactly 48 squares tall from the tips of the two small horns (row 11) to the soles (the last row of the feet is row 58), the two small flame tufts above the horns on rows 8-10; the tail fin reaches about column 19 on the left, the front paw about column 76 on the right; the same pose, layout and place as image 1 - a cute baby dragon STANDING ON FOUR LEGS, 3/4 view facing image right, big head raised, smiling, the folded wings over his back like a cape, the tail curling up behind him off the ground.
His look (image 2): an apricot-orange scaly face with a pale cream chin and throat; TWO BIG TEAL EYES, EACH AT LEAST 5x4 SQUARES - a near-black rim, white around, a teal iris, a dark pupil and a one-square white highlight - both clearly readable; a wide happy GRIN, a near-black curved mouth line showing 2-3 SMALL WHITE TEETH one square each; big fan-shaped ear fins on the sides of the head (crimson / dark navy outside, pale apricot inside); a row of TEAL LEAF-LIKE SPIKES along the fins, the cheeks and the neck, each at least 2x3 squares with dark gaps between them; a dark crimson crest over the head with a purple stripe; two short teal horns, each with a SMALL ORANGE-YELLOW FLAME TUFT on its tip (about 3x3 squares, hard edges, no glow). The body: a pale cream belly with 3-4 horizontal belly scales; the wings folded over his back like a cape - dark navy / dark purple outside with a row of big teal scales, fading down to crimson and then pink at the pointed lower edge; the forelegs dark wine red with a column of dark navy-purple scale plates down their front; 3-4 small dark navy claws on every foot; the near foreleg (image left of the pair) in full tone, the far one a shade darker; the far hind leg mostly hidden behind the body; all feet flat on row 58; the tail curling up from his hips, red on top and apricot underneath, ending in a big dark navy fin, never touching the ground.
Clean: big flat areas, every material in 3-4 flat shades, a TWO-SQUARE-THICK near-black outline around the silhouette, little black inside, nothing smaller than one square, no specks, no dithering, at most about 28 colours. No yellow or red lines, no effects, no ground, no shadow, no text.
```

## 交回前请检查

- 1536×1024 横版、真透明背景（全硬 alpha，没有半透明雾、没有光晕）；**每 16×16 px 一个颜色，格子从左上角对齐**（可以自己按格子取色检查）。
- 角尖在第 11 行，脚底最低一行在第 58 行（48 格），火苗在第 8–10 行；姿势、位置和 `1_layout_grid.png` 一致（四条腿站着、尾巴卷起、不碰地）。
- 两只眼睛每只至少 5×4 格，有眼白、青绿虹膜、瞳孔、白亮点；嘴是一条弧线，2–3 颗一格的小白牙；青绿鳞刺片片分开。
- 外轮廓 2 格近黑描边；没有小于一格的细节、碎点、抖动、黄线、红线、特效。
- 交付 `smolder-front.png` + `smolder-front_1x.png`（96×64）、`generation-prompts.txt`、`raw/`（原样），最后 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/smolder/codex_model/`；先看 raw/，用 regrid.py 按原稿自己的格子读回（不信 Codex 的 1x 读回），和 Codex 的读回并排；角尖到脚底应为 48 格（游戏里 32 行）。
- 在游戏实际大小（PPU 1.5）和 6× 下，与加里奥 hd_idle、布隆/泽丽 lo_idle、本包 ADC 并排给用户看；眼睛、牙、鳞刺要清楚。
- 用户认可后写第 2 步 `MODEL_STRIPS.md`：所有动作从这张 3/4 正面做（用户：不要侧面）；跑步四条腿交替（Caitlyn 的交叉步思路，四足版）；尾巴待机 / 走路都不贴地；同一张脸贯穿所有帧；翅膀只在 E 起飞时张开。
