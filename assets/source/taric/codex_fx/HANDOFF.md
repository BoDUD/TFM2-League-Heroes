# 塔里克独立特效素材包

共 14 张特效 PNG、93 帧。人物与已批准的动作素材保持独立，未修改人物的脸、模型或动作文件。

## 文件与导入

主目录为约定命名的 14 张图集；`manifest.json` 的 `assets[].frames[].rect` 为精确裁切区域 [x,y,宽,高]，同时列出建议游戏尺寸、绑定表及名称、锚点、循环标记与预览时长。`native/` 是每格缩为 1 像素的对应图，主图是最近邻放大 8 倍；`frames/` 是独立帧；`source/` 是本轮生成原稿。

主图全部为透明背景、0/255 二值透明度、严格 8×8 色块；逐项限制在各自指定色板中，排除了眼睛识别色 #279FF6。E 光束与 W 飞行宝石逐像素上下对称。E 蓄力前八帧宽度连通两端、厚度不超过格高四分之一，第九帧爆开。

不包括包内英雄联盟原版参考贴图。`preview-reference.png` 仅为用户批准的本轮人物造型，用于可选叠加预览，不进入特效图集。

## 逐项交接

| 编号 | PNG | 帧数 | 排布 | 输出尺寸 | 提示词 |
|---|---|---:|---|---|---|
| 1 | taric_fx_hit.png | 5 | 5×1 | 1280×256 | generation_prompts.json / 1 |
| 2 | taric_fx_p_hit.png | 6 | 6×1 | 1536×256 | generation_prompts.json / 2 |
| 3 | taric_fx_p_glow.png | 4 | 4×1 | 1152×384 | generation_prompts.json / 3；以 p_glow_correction.txt 为最终稿 |
| 4 | taric_fx_e_beam.png | 12 | 4×3 | 2048×480 | generation_prompts.json / 4 |
| 5 | taric_fx_e_hit.png | 6 | 6×1 | 1728×384 | generation_prompts.json / 5 |
| 6 | taric_fx_e_ally.png | 12 | 4×3 | 2048×768 | generation_prompts.json / 6 |
| 7 | taric_fx_q_cast.png | 8 | 4×2 | 2048×512 | generation_prompts.json / 7 |
| 8 | taric_fx_q_heal.png | 6 | 6×1 | 1536×384 | generation_prompts.json / 8 |
| 9 | taric_fx_w_bolt.png | 4 | 4×1 | 1024×128 | generation_prompts.json / 9 |
| 10 | taric_fx_w_bind.png | 6 | 6×1 | 1536×320 | generation_prompts.json / 10 |
| 11 | taric_fx_w_link.png | 4 | 4×1 | 1280×128 | generation_prompts.json / 11 |
| 12 | taric_fx_r_call.png | 10 | 10×1 | 2560×512 | generation_prompts.json / 12 |
| 13 | taric_fx_r_shine.png | 6 | 6×1 | 1728×384 | generation_prompts.json / 13 |
| 14 | taric_fx_r_invuln.png | 4 | 4×1 | 1152×384 | generation_prompts.json / 14 |

## 时序与尺寸说明

- E 光束与队友光圈：前 8 帧共 750 ms（每帧 93.75 ms）；第 9 帧开始爆发，后 4 帧共 200 ms。
- R 说明中“10 帧共 2.5 秒”与“第 9–10 帧于第 150 tick 落光”无法同时给出正时长的完整预览。本包优先保留 2.5 秒后生效：前 8 帧共 2500 ms，第 9–10 帧另加 100 ms 落光展示，预览总长 2600 ms。导入时请以生效事件 t=2500 ms 为准，或由游戏逻辑播放末两帧。
- 其他一次性效果采用 80 ms/帧的预览默认值，四帧循环采用 150 ms/帧；这些不是新设定的技能持续时间。正气凌人 4 秒、R 无敌 2.5 秒等 buff 寿命由游戏逻辑控制。
- GIF 只支持 10 ms 时间精度；精确小数毫秒时长以 manifest 和 HTML 预览为准。
- 源图为适应生图画布采用紧凑行列，最终图集已重排。E 光束采用 4 列×3 行、2048×480，消除了原说明中 512×160 单格与 6144×384 总尺寸的算术冲突。
- 地面光圈保持扁椭圆的俯视风格，实际光环有留白与星点，不应拿有效像素 bbox 代替整个帧矩形重新缩放每一帧。建议整体按 game_size 导入，避免播放时跳动。

## 遮挡与质量边界

被动星点已经另生成稀疏版本，所有帧上半部完全透明。护盾与无敌光罩中间保留空位；命中首帧及 R 落光包含短暂闪光。为保证实际叠加时脸和身体可读，预览把人物绘在这些光效之前，导入推荐采用同样层级；地面效果应在人物下层。

特效原稿由内置 image_gen 生成，未手绘替代；后处理仅做固定格采样、指定色板归一、二值透明、光束蓄力限高、中心线延伸、投射类上下对称及图集重排。原稿保留供继续美术调整。

所有帧已检查非空、独立、尺寸、色板、透明度、像素网格及指定对称性；已目视检查各组总览。循环星点按四帧闪烁/位移表达环绕，不是精确三维轨道模拟。未写入游戏资源目录，未验证游戏内遮挡、缩放或技能运行。

## 预览

解压后打开 preview.html。支持逐帧、暂停、速度、浅色背景和“叠加塔里克”。预览人物不会写进任何 taric_fx_*.png。
