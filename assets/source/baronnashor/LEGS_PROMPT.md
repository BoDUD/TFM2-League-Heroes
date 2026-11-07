# 纳什男爵（金铲铲之战 · 第 16 赛季）：改腿第 1 步，只把待机图的腿改成蜘蛛腿（给 Codex 的提示词）

> 11-03 加腿时画成了**两条短短的后腿 + 象牙白三趾脚**（像恐龙），用户看了金铲铲里的样子说不对（附图 1、2）：金铲铲的纳什男爵**下半身是一根深紫色的分节柱子，底部一圈细长、带关节、往外张开的蜘蛛腿**，腿尖是尖的，扎在地上，**没有脚掌、没有脚趾**。
>
> 这一步**只改腿**：拿游戏里现在的待机图（附图 3，每格 11 像素），**髋部线（附图 4 的青色线）以上一格都不动**，线以下把两条后腿和白脚换成蜘蛛腿。画**两张**，用户挑一种：
> - **L6：6 条腿**（每边 3 条）：两边最大的一对在中间，前后各一对小一点的。
> - **L8：8 条腿**（每边 4 条），更像真正的蜘蛛。
>
> 用户选定以后，第 2 步再按选定的腿重画所有动作（普攻、技能、大招、受击、死亡）和 8 帧跑步。

## 要点

- **底图**（附图 3 `base/3_idle_11px.png`）：游戏里现在的待机图，58×94 格，每格 11 像素，放在 1254×1254 画布上（左上角在 (308, 110)），**格子和画布的 11 像素网格对齐**。交回的图要**同一张画布、同一套网格、人物位置不变**。
- **髋部线以上不动**（附图 4 的青色线，y = 880，第 70 行）：头、头冠、两只小蛇头、两只象牙白大爪、青绿腹甲、紫色鳞甲，**一格都不改**（我这边会逐格比对）。
- **线以下（第 70–94 行，24 格高）**：
  - **保留**线下面露出来的**青绿腹甲底部**和**两只象牙白大爪的爪尖**（它们属于身体和手臂，不是腿）。
  - 只去掉**两条紫色后腿**和**地面线上的两只象牙白三趾脚**。
  - 身体往下延续成一小段**深紫色的分节柱子**（和上面的鳞甲同色，横向一节一节），到离地两三格的地方收住，底部被腿挡住。
  - 从柱子底部一圈伸出**细长的蜘蛛腿**：每条腿先**往外、往上**伸到一个膝关节（高过柱子底部），再**往下、往外**折到地面，**腿尖是尖的**，正好扎在地面线上（附图 4 的灰线，y = 1144，第 94 行）。
  - **最大的一对在两侧中间**，膝关节最高，向外张得最开（每边超出身体 12–16 格）；前后的腿小一点、短一点。
  - 腿粗：靠身体那头 2–3 格，往腿尖越来越细，腿尖 1 格。
- **3/4 朝右**：**近处（朝外的一侧）的腿画在身体前面**，比远处的腿**亮一档**；**远处的腿**在身体后面，**暗一档**，部分被身体挡住。
- **颜色**：用身体鳞甲的紫色（现在腿上的那几档：#5A117B / #390D57 / #200B38，近处的腿可以用亮一点的 #8336E4 做高光），关节处一格亮紫高光，**腿尖用最暗的一档紫**。**腿上不要象牙白**（白色只留给上面的爪子和獠牙）。
- **描边和像素**：和底图一样，外轮廓 2 格宽的近黑描边，腿的描边和身体的接在一起；每种材质 3–4 档平涂，不要渐变、不要柔光、不要零散的杂色格。每格 11 像素、全不透明。
- **宽度**：算上腿，全身最宽约 80 格（880 像素），左右居中在身体下面，四周留边，不出画。
- 不画特效、地面、地洞、投影。真透明背景。

## 附图（在压缩包 `baronnashor_legs_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_reference.png` | 用户给的金铲铲截图：纳什男爵站在一圈蜘蛛腿上 | **腿长什么样**：几条、多长、怎么张开、腿尖扎地 |
| `refs/2_reference_baron.png` | 截图里的纳什男爵，放大 3 倍 | 同上，看得清楚些 |
| `base/3_idle_11px.png` | **要改的底图**：游戏里现在的待机图，每格 11 像素 | 画布、网格、人物位置；**髋部线以上照抄** |
| `base/4_hips_guide.png` | 同一张图加了参考线：青色 = 髋部线（以上不动），灰色 = 地面线（腿尖在这条线上） | 改哪里、腿尖落在哪 |
| `style/5_style_skarner_run.png` | 本包的斯卡纳（蝎子）跑步，8 倍放大，一格 = 一个像素 | **只看风格**：几条细腿在像素画里怎么画、怎么分前后 |
| `style/6_style_elise_legs.png` | 本包的伊莉丝，背上的蜘蛛腿，8 倍放大 | **只看风格**：细长、分节、带关节的尖腿怎么画 |

## 提示词：`baronnashor-legs-L6.png` / `baronnashor-legs-L8.png`（同一段提示词，先画 L6 再画 L8）

```text
Six attached images. Image 3 is a finished pixel-art game sprite on a 1254x1254 transparent canvas, every square 11 px on the canvas's 11 px grid: a huge purple VOID SERPENT standing upright, 3/4 view facing right - an armoured blue-violet head with a magenta-tipped purple crest, two small serpent heads on thin arms, two big ivory claws on purple arms, a teal segmented belly, purple scale armour, and BELOW ITS HIPS two short purple hind legs with ivory three-toed feet. Image 4 is the same picture with two guide lines: the CYAN line is its hips, the GREY line its ground.
EDIT IMAGE 3, ONLY BELOW THE CYAN LINE. Everything above the cyan line stays EXACTLY as it is, square for square: the head, the crest, both small heads, both ivory claws, the belly, the scales - do not move, redraw or recolour any of it. Keep the same canvas, the same 11 px grid and the same position.
Below the cyan line KEEP the bottom of the teal belly and the tips of the two ivory claws that reach a little below it (they belong to the body and the arms, not the legs); REMOVE only the two purple hind legs and the two ivory three-toed feet standing on the grey line, and give it SPIDER LEGS like images 1-2 (a screenshot of the same creature in its own game: the bottom of its body is a dark purple segmented column and a ring of long, thin, jointed, pointed legs spreads out from its base, the tips stabbing into the ground; NO feet, NO toes). Continue the body down as a short dark purple column of horizontal segments (the colours of its scale armour) ending two or three squares above the ground, hidden behind the legs. From the base of the column the legs splay out all round: each leg goes UP AND OUTWARD to a knee joint (higher than the base of the column), then bends DOWN AND OUTWARD to a SHARP POINTED TIP that touches the grey ground line. The BIGGEST pair at the middle of the sides, knees highest, spread widest (12-16 squares out past the body on each side); the front and rear legs smaller and shorter. Each leg 2-3 squares thick at the body, thinning to a 1-square point.
3/4 view facing right: the NEAR legs (on the side facing us) in FRONT of the body and one shade BRIGHTER; the FAR legs BEHIND the body, one shade DARKER, partly hidden by it. Colours: the body's scale purples (#5A117B, #390D57, #200B38; the near legs may use #8336E4 as their light shade), a one-square brighter purple highlight on each knee, the tips in the darkest purple. NO ivory on the legs (ivory stays on the claws and tusks above).
Same pixel art as image 3 (images 5-6 are STYLE ONLY, characters from the same game shown 8x so every square is one pixel: how thin jointed legs are drawn in this style): a 2-square near-black outline around every leg, joined to the figure's outline; every material in its own 3-4 flat shades, the shadow its own darkest shade; no stray single odd squares; no dithering, no gradients, no blur, no anti-aliasing, no soft glow; every pixel fully opaque, a genuine transparent background. With the legs the whole figure at most about 80 squares (880 px) wide, centred under the body, everything inside the canvas with margins. No effects, no ground plane, no hole, no cast shadow, no text, no frame, no other characters.
PICTURE L6 (baronnashor-legs-L6.png): SIX legs, three on each side - the big middle pair plus a smaller front pair and a smaller rear pair.
PICTURE L8 (baronnashor-legs-L8.png): EIGHT legs, four on each side, more like a true spider; the middle pairs the biggest.
```

## 交回前请检查

- 1254×1254，真透明背景（不是画出来的棋盘格），**每格 11 像素、对齐画布的网格**，人物位置和底图一样。
- **青色线以上和底图逐格一样**（头、头冠、小头、白爪、腹甲、鳞甲都没动）。
- 线以下：腹甲底部和两只白爪的爪尖还在；**没有原来的两条后腿和白脚**；一小段深紫分节柱子；**L6 六条 / L8 八条**细长、带关节、往外张开的腿；**腿尖是尖的，正好落在灰色地面线上**；最大的一对在两侧中间；近处的腿亮一档在身体前面，远处的暗一档在后面；**腿上没有象牙白**。
- 2 格宽的近黑描边，不糊、没有渐变、没有零散杂色格，全硬 alpha。
- 交付：`outputs/baronnashor-legs/baronnashor-legs-L6.png`、`baronnashor-legs-L8.png`；原始生成图放进 `outputs/baronnashor-legs/raw/`；附 `generation-prompts.txt`（实际用的提示词）；**最后**写 `outputs/baronnashor-legs/HANDOFF.md`（交付说明），再打包成 `outputs/baronnashor_legs_done.zip`。两张都画完再交，中间不要停。

## Claude 收到后（给 Claude 看）

1. 解压到 `assets/source/baronnashor/codex_legs/`。按 11 像素网格读回（`tools/art/design_baronnashor_hd.py` 读 A 的办法），量宽高；**第 0–69 行和 `hd/idle.png` 逐格比**（只允许腿伸上来盖住的几格不同）；腿尖都在第 94 行。
2. 两张都做成 1:1 的游戏尺寸，和现在的待机、斯卡纳、峡谷先锋放在一起出对比图给用户挑。
3. 选定后第 2 步：按选定的腿出动作包。19 个动作和 8 帧跑步的上半身沿用现在 Codex 画好的（`codex_poses`、`codex_run`），只重画腿；跑步改成蜘蛛的步法（两组腿交替：一边的前、后腿和另一边的中腿一起落地）。腿的骨架参考换成斯卡纳的跑步（不再用 T-Hex 的两条腿）。之后重新 rig、`ppu_restyle`、`ppu_hd`、`hero_reels --hero baronnashor`，各附加包的副本（佛耶戈、塞拉斯、妮蔻、俄洛伊）照常重新生成。
