# 烬：最终特效素材交付

已完成 27 张独立特效 PNG，共 146 帧；另有 28 个 GIF 动画预览（减速的两行分别预览）。全部主要图形由 OpenAI imagegen 生成，未使用代码绘制或拼造特效形状。

## 文件与切帧

- 根目录 `jhin_fx_*.png`：按所给尺寸整理的等宽帧条带，RGBA 透明，硬边 8 像素方格，颜色限定在各条提示词的色阶内。
- `raw/`：各张最终采用的 imagegen 原稿，保留原始透明度和细节。原稿画布比例可能与规格不同。
- `pixel1x/`：整理后条带的方格原尺寸，根目录 PNG 是它们的最近邻 8 倍放大。这里的 1x 方格尺寸不等同于技能的游戏显示尺寸。
- `manifest.json`：导入用的逐帧坐标。`assets[].frames[].rect` 是根目录 PNG 的 `[x,y,w,h]`；`raw_rect` 用于同名 raw 原稿；`row` 和 `column`、`index` 均从 0 开始。锚点坐标相对于单帧左上角。
- `bindings.json` 与 manifest 中 `binding`、`game_display_size`：保留输入清单中的挂接名称及游戏显示大小。
- `prompts/`：每张最终生成或修整实际使用的提示词；`source-specification.md` 保留所给的视觉规格文本。
- `preview.html`、`overview.png`、`preview/`：完整预览；预览上的文字和暗底不属于特效 PNG。
- `validation.json`：尺寸、切帧、非空帧、透明度、色阶、方格、指定对称性、预览文件的校验记录。

## 导入约定

切根目录 PNG 时直接使用 manifest 的 `rect`，不要按原稿画布猜测。所有飞行弹道朝右，上下对称；减速两行左右对称。枪口类白色发射芯已注册到格子左边中点，朝左由游戏镜像。挂接到角色哪一动作帧及部位，见 binding 的原始说明。

`slowed` 第 1 行是 E 的减速，第 2 行是 R 的减速，每行独立循环 4 帧；不要将两行连成一条 8 帧动画。

文档中的第 3–6 帧对应 `w_root` 的零基索引 2–5，持有时循环这些帧。文档中的第 4–8 帧对应 `e_bloom` 的索引 3–7，导入时按 2 秒绽放阶段配置。装弹提示的预览为 2.2 秒，游戏也需配置 2.2 秒。其余 GIF 的 100 ms/帧主要供观察动画顺序；技能时序仍由游戏配置决定。

## 制作修整与实际限制

原稿采用按单张提示词生成的序列，之后只做切帧、最近邻尺寸整理、色阶映射、透明度硬化、锚点注册、镜像对称。第四枪枪口原稿帧间距不均，已按实际内容调整 `raw_rect` 后重新排成 5 个等宽单元。下落手雷已重新注册物体位置，最后两帧落点同为格子高度的三分之二；绽放莲花整理为约 2:1 的扁平地面形状。开幕特效已二次生图，中央留出透明人物空间；定身经过重绘以分开四条主藤蔓。

每帧的微小火星、花瓣轮廓与数量、烟雾形状属于生成画面近似，不是逐格手工临摹英雄联盟贴图。部分地面光环比规定的 2:1 更扁，整理稿保留了生成造型；需要严格比例时仍需局部调整。原稿不是严格原尺寸像素条，所以同时提供了硬边整理稿与原稿，便于选择。根目录 PNG 的透明度为 0/255；需要柔和渐隐时可以在游戏中调节绘制透明度，或从 raw 原稿切帧。

锚点元数据依照所给规格登记，地面圈与枪口在真实游戏缩放和动作中的重合尚需导入者实测。本次完成的是素材制作及切帧交付；游戏技能数据、动画播放配置与游戏内实测不在本次素材交付结果中。

本地参考贴图 `lol_fx_ref.png` 没有打入交付包。

## 每张使用的规格条目及实际帧数

| 原规格条目 | 文件 | 实际帧数 | 整理稿尺寸 | 最终实际提示词 |
|---|---|---:|---|---|
| 1 | `jhin_fx_a_bolt.png` | 4 | 2048×256 | `prompts/a_bolt.txt` |
| 2 | `jhin_fx_a4_bolt.png` | 4 | 2048×256 | `prompts/a4_bolt.txt` |
| 3 | `jhin_fx_a_cast.png` | 4 | 1024×256 | `prompts/a_cast.txt` |
| 4 | `jhin_fx_a_muzzle.png` | 4 | 1024×256 | `prompts/a_muzzle.txt` |
| 5 | `jhin_fx_a_hit.png` | 4 | 1024×256 | `prompts/a_hit.txt` |
| 6 | `jhin_fx_a4_muzzle.png` | 5 | 1920×256 | `prompts/a4_muzzle.txt` |
| 7 | `jhin_fx_a4_hit.png` | 5 | 1280×256 | `prompts/a4_hit.txt` |
| 8 | `jhin_fx_a_reload.png` | 8 | 4096×256 | `prompts/a_reload.txt` |
| 9 | `jhin_fx_q_nade.png` | 4 | 1024×256 | `prompts/q_nade.txt` |
| 10 | `jhin_fx_q_throw.png` | 4 | 1024×256 | `prompts/q_throw.txt` |
| 11 | `jhin_fx_q_boom.png` | 5 | 1280×256 | `prompts/q_boom.txt` |
| 12 | `jhin_fx_q_drop.png` | 4 | 1024×768 | `prompts/q_drop.txt` |
| 13 | `jhin_fx_w_shot.png` | 4 | 3072×128 | `prompts/w_shot.txt` |
| 14 | `jhin_fx_w_muzzle.png` | 5 | 1920×256 | `prompts/w_muzzle.txt` |
| 15 | `jhin_fx_w_hit.png` | 5 | 1280×256 | `prompts/w_hit.txt` |
| 16 | `jhin_fx_w_root.png` | 8 | 2560×256 | `prompts/w_root.txt` |
| 17 | `jhin_fx_e_seed.png` | 4 | 1024×256 | `prompts/e_seed.txt` |
| 18 | `jhin_fx_e_land.png` | 8 | 3072×256 | `prompts/e_land.txt` |
| 19 | `jhin_fx_e_bloom.png` | 10 | 5120×256 | `prompts/e_bloom.txt` |
| 20 | `jhin_fx_e_boom.png` | 7 | 1792×256 | `prompts/e_boom.txt` |
| 21 | `jhin_fx_e_hit.png` | 4 | 1024×256 | `prompts/e_hit.txt` |
| 22 | `jhin_fx_r_deploy.png` | 8 | 3072×320 | `prompts/r_deploy.txt` |
| 23 | `jhin_fx_r_muzzle.png` | 5 | 1920×256 | `prompts/r_muzzle.txt` |
| 24 | `jhin_fx_r_bullet.png` | 4 | 2048×128 | `prompts/r_bullet.txt` |
| 25 | `jhin_fx_r_hit.png` | 5 | 1280×256 | `prompts/r_hit.txt` |
| 26 | `jhin_fx_r_crit.png` | 6 | 1536×256 | `prompts/r_crit.txt` |
| 27 | `jhin_fx_slowed.png` | 8 | 2560×512 | `prompts/slowed.txt` |
