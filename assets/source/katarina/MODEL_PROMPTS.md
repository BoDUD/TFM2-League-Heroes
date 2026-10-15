# 卡特琳娜：侧身造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（上一个英雄的第 1 步用脚本逐格写，格子对了但样子丢了很多，用户没采用。）
> - **正面不用再画**：用户选了你第 0 步画的 **K1**（`1_front_K1.png`），原样就是正面造型；游戏里头顶到鞋底 38 行。
> - **这一轮只画侧身**（除了待机，所有动作都从侧身来）：**画两稿**，身体**约 3/4 转向画面右边**（胸口大半朝右，但还看得见一点胸甲），**和 K1 一样的画风、一样的格子大小（约 12 px 一格）、一样的人物大小**——就像同一个画师在同一张纸上把她转了个身。
> - **同一张脸**：侧身的头**照 K1 那颗 3/4 头画**（`4_face.png`：深红长发、白皙皮肤、两只绿眼睛都看得见、一只眼睛上的细竖疤、浅笑），不要画成侧脸剪影。

## 大小和位置

- 画布 **1024 × 1536 竖版**，和 K1 一样：**头发顶在 y ≈ 699**（`2_layout.png` 的绿线），**鞋底在 y ≈ 1509**（红线），**像素块和 K1 一样大（约 12 px 一格）**；人物和 K1 一样高、一样的身材。
- 布局图里的 3D 模型**只看位置和侧身的转法**，它是写实比例；**比例、粗细、头的大小照 K1**（偏 Q 版）。

## 侧身怎么画

- **身体约 3/4 转向画面右边**（像 `3_league_side.png` 左边的 75° 待机）：胸口大半朝右，**近侧（画面右边）的手臂和肩在前**；钢灰胸甲、露出的腰腹、交叉的棕皮带跟着转过来；**深红长发披在身后**（画面左边）；背后斜插的匕首刀柄从肩后露出来。
- **匕首**：照英雄联盟的待机（`3_league_side.png`）——**一只手把一把弯刃匕首举在胸前、刀刃朝右**，另一只手**低低地握着另一把朝前**；两把都是**银白刀身 + 深色刀柄**、轮廓连续、至少 2 格粗；**刀不挡脸**。
- **腿**：从侧面看**一前一后、大步分开、膝盖微弯**（近侧腿在前、颜色亮；远侧腿在后、暗一档），**银灰护胫 + 黑靴朝右**，两只鞋底踩在同一条地面线上；腿和 K1 一样粗、一样长。
- 同一个人：同样的头、同样的衣服和颜色、同样的大小。

## 干净

- 和 K1 一样的像素画：大小一致的方块、对齐成网格，**近黑外描边**，每种材质 3–4 档平涂，不要抖动、渐变、碎点、柔光；颜色只用 K1 里有的。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图四周有一圈半透明的红色光晕，这次请把 alpha 二值化，不要光晕）。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `katarina_model_pack.zip` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_front_K1.png` | 你第 0 步画的 K1（已选定的正面） | **样子、格子大小、比例、颜色**全照它 |
| `2_layout.png` | 侧身的布局：英雄联盟模型转到约 75° 放在竖版画布上，绿线 = 发顶 y 699，红线 = 鞋底 y 1509 | 位置、大小、侧身怎么转（**比例不照它**） |
| `3_league_side.png` | 英雄联盟的卡特琳娜：待机 75°、待机 90°、跑动 80°（都朝右） | 匕首怎么拿、腿一前一后、靴子朝右 |
| `4_face.png` | K1 的头（4 倍放大） | **每一帧都用这一张脸** |

## 提示词：`katarina-side-1.png`、`katarina-side-2.png`（两稿）

附 1、2、3、4。**用 image_gen 画。**

```text
Attached images: 1 an approved pixel-art design of this character, a woman assassin with two curved daggers, 3/4 front view (the LOOK, the PIXEL SQUARE SIZE of about 12 px, the chibi-ish proportions, the colours - copy them exactly); 2 a layout guide on the 1024x1536 canvas: a 3D model of her turned about 75 degrees toward the right, the green line = the top of her hair (y 699), the red line = her soles (y 1509) - ONLY for the place, the size and how the body turns, NOT for the proportions (it is realistic, the design is chibi-ish); 3 the 3D model side-on: her idle at 75 and 90 degrees and a run frame, all facing right - how she holds the daggers and how the legs stand; 4 her head from image 1 enlarged - the ONE FACE every picture of her keeps.
Draw with the image generator ONE pixel-art picture of the same woman, her body turned about THREE QUARTERS TOWARD THE IMAGE RIGHT: a 1024x1536 PORTRAIT PNG with a real transparent background (alpha only 0 or 255, no glow or haze round her). The same pixel art as image 1: the same square size (about 12 px, aligned on one grid), the same near-black outline, 3-4 flat shades per material, the same colours, the same height and build: the top of her hair at y 699, the soles at y 1509, both soles on one ground line.
THE BODY three quarters to the right: the chest mostly facing right but part of the dark steel chest plate still visible, the bare midriff, the crossed brown belts turned with her; the near arm and shoulder (image right) in front, the spiked dark steel shoulder guards and the spiked silver bracers; the long CRIMSON hair flowing down behind her back (image left); the brown dagger hilts showing over her shoulders from her back; black leather trousers with the silver blade ornaments on the thighs; the legs ONE IN FRONT OF THE OTHER, wide apart with the knees a little bent (the near leg in front in full tone, the far leg behind a shade darker), the silver-grey greaves and BLACK boots pointing RIGHT, as thick and long as in image 1.
THE HEAD: the same 3/4 head as image 4 - long crimson hair with the side-swept lock, fair skin, BOTH green eyes visible, the thin vertical scar over one eye, the faint smile - NOT a profile face.
THE DAGGERS as in her idle (image 3): one hand holds a curved dagger up in front of her chest, the blade pointing right; the other holds the second dagger low and forward; both bright SILVER-WHITE blades with dark hilts, at least 2 squares thick, clean continuous curves, never covering her face.
No effects (no blade trails, no glow), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1024×1536；真透明背景，**alpha 只有 0 / 255**，没有光晕。
- 画风、格子大小（约 12 px）、颜色、比例和 K1 一样，像同一个画师画的同一个人；**头是 `4_face.png` 那颗 3/4 头**（两只绿眼都看得见、竖疤、浅笑）。
- 身体约 3/4 转向右边，还看得见一部分胸甲；长发披在身后；背后刀柄露出来；腿一前一后、靴子朝右、鞋底在一条线上。
- 两把弯刃匕首银白、轮廓连续、不挡脸。
- 发顶约 y 699、鞋底约 y 1509。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/katarina-model/`）

- `katarina-side-1.png`、`katarina-side-2.png`；**image_gen 的原始生成图原样放 `outputs/katarina-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/katarina_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两稿都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），和 K1 的读回放一起比：头（贴 K1 的头，one-face-all-frames）、身高、颜色；用户选一稿。
- 第 2 步动作条从侧身出（待机用 K1 正面），帧保持 Codex 的原密度，最后整套 ppu_restyle crisp 到 PPU 1.5（米利欧、杰斯的做法）；匕首永远整块移动、不变形。
