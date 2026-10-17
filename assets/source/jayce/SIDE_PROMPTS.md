# 杰斯：侧身造型重画（第 1 步重做，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。** 上一轮第 1 步是用脚本逐格写出来的：格子和头都对，但样子比你第 0 步画的 A2 / B2 简化太多（海军蓝长衣摆、胸前圆徽章、米白毛领没了，锤柄像一把刀片，炮形胸口被一大块金色盖住），用户没有采用。
> - **正面不用再画**：锤形正面就是你第 0 步画的 **A2**（`1_hammer_A2.png`），炮形正面就是 **B2**（`2_cannon_B2.png`），原样使用。
> - **这一轮只画侧身**（所有动作都从侧身来）：锤形、炮形**各画两稿**，身体**约 3/4 转向画面右边**（用户选的角度：胸口大半朝右，但还看得见一点胸甲和圆徽章），**和 A2 / B2 一样的画风、一样的格子大小、一样的人物大小**——就像同一个画师在同一张纸上把他转了个身。
> - **同一张脸**：侧身的头**照 A2 那颗 3/4 头画**（`6_face.png`：后梳深棕短发 + 一小撮刘海、麦色皮肤、浓眉、两只眼睛都看得见、自信微笑），不要画成侧脸剪影。

## 大小和位置

- **锤形侧身**：画布 **1024 × 1536 竖版**，和 A2 一样：**头发顶在 y ≈ 490**（`3_hammer_layout.png` 的绿线），**鞋底在 y ≈ 1497**（红线），**像素块和 A2 一样大（约 10–11 px 一格）**；人物和 A2 一样高、一样壮。
- **炮形侧身**：画布 **1536 × 1024 横版**，和 B2 一样：**头发顶在 y ≈ 103**（`4_cannon_layout.png` 的绿线），**鞋底在 y ≈ 966**（红线），**像素块和 B2 一样大（约 8 px 一格）**；人物和 B2 一样高、一样壮。
- 布局图里的 3D 模型**只看位置和侧身的转法**，它是写实比例；**比例、粗细、头的大小照 A2 / B2**（敦实、偏 Q 版）。

## 侧身怎么画

- **身体约 3/4 转向画面右边**（像 `5_league_side.png`）：胸口大半朝右，**近侧（画面右边）的手臂和肩在前**，大米金肩甲转到侧面；腰带、**海军蓝长衣摆**跟着转过来（衣摆在身后飘着）；胸甲和**圆徽章**还看得见一部分；**米白毛领**、**深红围巾**都在。
- **锤形**：照英雄联盟的待机（`5_league_side.png`）——双手握锤**斜着横在胸前**，**锤柄笔直**（不能弯、不能变成刀片，是一根银灰色的圆柄 + 红色握把 + 底端银灰尖钻），**大金色方块双锤头 + 橙色核心**在他肩膀上方、头的后面（画面左上），**锤头不挡脸**。
- **炮形**：炮**笔直水平**端在腰间，**炮口朝右**（炮口一圈开口），金色锤块折在炮管两侧、橙色核心，尾部尖钻在身后；膝盖微弯；**炮不要盖住整个胸口**，手臂、胸甲、腰带都要看得见。
- **腿**：从侧面看**一前一后**（近侧腿在前、颜色亮；远侧腿在后、暗一档），**靴子朝右**，两只鞋底踩在同一条地面线上；腿和 A2 / B2 一样粗、一样长。
- **两种形态是同一个人**：同样的头、同样的衣服和颜色、同样的大小。

## 干净

- 和 A2 / B2 一样的像素画：大小一致的方块、对齐成网格，**近黑外描边**，每种材质 3–4 档平涂，不要抖动、渐变、碎点、柔光；颜色只用 A2 / B2 里有的。
- **真透明背景，alpha 只能是 0 或 255**（上一轮第 0 步的图边缘有一圈半透明，这次请把 alpha 二值化）。不要网格线、文字、边框、影子、地面、特效（电光、光晕都不画）。

## 附图（压缩包 `jayce_side_pack.zip` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_hammer_A2.png` | 你第 0 步画的锤形 A2（已选定的正面） | **样子、格子大小、比例、颜色**全照它 |
| `2_cannon_B2.png` | 你第 0 步画的炮形 B2（已选定的正面） | 炮形的**样子、格子大小、比例、颜色** |
| `3_hammer_layout.png` | 锤形侧身的布局：英雄联盟模型转到约 60° 放在竖版画布上，绿线 = 发顶 y 490，红线 = 鞋底 y 1497 | 位置、大小、侧身怎么转（**比例不照它**） |
| `4_cannon_layout.png` | 炮形侧身的布局：横版画布，绿线 = 发顶 y 103，红线 = 鞋底 y 966 | 同上 |
| `5_league_side.png` | 英雄联盟的杰斯 60°（上）和 75°（下），左锤形、右炮形 | 武器怎么拿、腿一前一后、靴子朝右 |
| `6_face.png` | A2 的头（4 倍放大） | **每一帧都用这一张脸** |

## 提示词 1：锤形侧身 `jayce-hammer-side-1.png`、`-2.png`（两稿）

附 1、3、5、6、2。**用 image_gen 画。**

```text
Attached images: 1 an approved pixel-art design of this character with his giant hammer, 3/4 front view (the LOOK, the PIXEL SQUARE SIZE of about 10-11 px, the STOCKY proportions, the colours - copy them exactly); 3 a layout guide on the 1024x1536 canvas: a 3D model of him turned about 60 degrees toward the right, the green line = the top of his hair (y 490), the red line = his soles (y 1497) - ONLY for the place, the size and how the body turns, NOT for the proportions (it is realistic, the design is chibi-ish); 5 the 3D model side-on at 60 and 75 degrees, with the hammer (left) and with the cannon (right) - how he holds the weapon and how the legs stand; 6 his head from image 1 enlarged - the ONE FACE every picture of him keeps; 2 the same man with his weapon folded into a cannon (the same character, for reference).
Draw with the image generator ONE pixel-art picture of the same man with the hammer, his body turned about THREE QUARTERS TOWARD THE IMAGE RIGHT: a 1024x1536 PORTRAIT PNG with a real transparent background (alpha only 0 or 255). The same pixel art as image 1: the same square size (about 10-11 px, aligned on one grid), the same near-black outline, 3-4 flat shades per material, the same colours, the same height and build: the top of his hair at y 490, the soles at y 1497, both soles on one ground line.
THE BODY three quarters to the right: the chest mostly facing right but part of the cream-gold and red chest armour and its ROUND EMBLEM still visible; the near arm and shoulder (image right) in front, the big cream-gold shoulder plate turned to the side; the DEEP RED scarf and the CREAM fur collar; the brown leather coat, the belt with its gold buckle, the long DARK NAVY coat tails behind him; slate-blue trousers, cream-gold pointed knee guards, dark brown boots; the legs ONE IN FRONT OF THE OTHER (the near leg in front in full tone, the far leg behind a shade darker), the boots pointing RIGHT, as thick and long as in image 1.
THE HEAD: the same 3/4 head as image 6 - short dark brown swept-back hair with a small quiff, tanned skin, thick brows, BOTH eyes visible with highlights, a confident half smile - NOT a profile face.
THE HAMMER as in League's idle (image 5): held in both hands slanting across his chest, the shaft PERFECTLY STRAIGHT - a round silver-grey shaft with a red grip and a silver-grey drill spike at its lower end (never a blade); the HUGE GOLDEN double head of two square blocks with the ORANGE hextech core up above his shoulder behind his head (image upper left), never covering his face.
No effects (no lightning, no glow), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：炮形侧身 `jayce-cannon-side-1.png`、`-2.png`（两稿）

附 2、4、5、6、你刚画的锤形侧身、1。**用 image_gen 画。**

```text
Attached images: 2 an approved pixel-art design of this character with his CANNON, 3/4 front view (the LOOK, the PIXEL SQUARE SIZE of about 8 px, the STOCKY proportions, the colours - copy them exactly); 4 a layout guide on the 1536x1024 canvas: a 3D model of him turned about 60 degrees toward the right, the green line = the top of his hair (y 103), the red line = his soles (y 966) - ONLY for the place, the size and how the body turns, NOT for the proportions; 5 the 3D model side-on at 60 and 75 degrees, with the hammer (left) and with the cannon (right); 6 his head enlarged - the ONE FACE every picture of him keeps; then the hammer side view you just drew - how his body, coat and legs turn; 1 the same man with the hammer (for reference).
Draw with the image generator ONE pixel-art picture of the same man with the cannon, his body turned about THREE QUARTERS TOWARD THE IMAGE RIGHT: a 1536x1024 LANDSCAPE PNG with a real transparent background (alpha only 0 or 255). The same pixel art as image 2: the same square size (about 8 px, aligned on one grid), the same near-black outline, 3-4 flat shades per material, the same colours, the same height and build: the top of his hair at y 103, the soles at y 966, both soles on one ground line.
THE BODY as in the hammer side view: the chest mostly facing right, part of the chest armour and its ROUND EMBLEM still visible, the near arm in front, the shoulder plate to the side, the red scarf, the cream fur collar, the coat, the belt, the DARK NAVY coat tails behind; knees bent a little; the legs ONE IN FRONT OF THE OTHER (near leg in front in full tone, far leg behind a shade darker), the boots pointing RIGHT.
THE HEAD: the same 3/4 head as image 6 (both eyes visible, the half smile) - NOT a profile face.
THE CANNON: PERFECTLY STRAIGHT and LEVEL, held at his hip in both hands, the MUZZLE pointing RIGHT with its dark opening and ring; the silver-grey barrel, the square GOLDEN hammer blocks folded along both sides, the ORANGE core between them, the drill spike behind him; it must NOT hide his whole chest - his arms, the chest armour and the belt stay visible.
No effects (no lightning, no muzzle flash, no glow), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；锤形 1024×1536、炮形 1536×1024；真透明背景，**alpha 只有 0 / 255**。
- 画风、格子大小、颜色、比例和 A2 / B2 一样，像同一个画师画的同一个人；**头是 `6_face.png` 那颗 3/4 头**（两只眼都看得见）。
- 身体约 3/4 转向右边，还看得见一部分胸甲和圆徽章；海军蓝长衣摆、毛领、红围巾都在；腿一前一后、靴子朝右、鞋底在一条线上。
- 锤柄笔直、是圆柄不是刀片；锤头在肩后上方、不挡脸。炮笔直水平、炮口朝右、不盖住整个胸口。
- 锤形发顶约 y 490、鞋底约 y 1497；炮形发顶约 y 103、鞋底约 y 966。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/jayce-side/`）

- `jayce-hammer-side-1.png`、`jayce-hammer-side-2.png`、`jayce-cannon-side-1.png`、`jayce-cannon-side-2.png`；**image_gen 的原始生成图原样放 `outputs/jayce-side/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），和 A2 / B2 的读回放一起比：头（贴 A2 的头，one-face-all-frames）、身高、颜色；用户选一稿。
- 第 2 步动作条从侧身出，帧保持 Codex 的原密度，最后整套 ppu_restyle crisp 到 PPU 1.5（Milio 的做法）；武器永远笔直、整块移动。
