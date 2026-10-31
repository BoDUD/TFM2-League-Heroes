# 苍蓝雕纹魔像：18 张动作姿势

交付日期：2026-10-31（Asia/Tokyo）。使用内置 imagegen，造型参考仅取自 sentinel_pose_pack.zip。本包是动作原画交付，不包含游戏导入或运行验证。

## 文件清单

- sentinel-pose-a_raise.png、sentinel-pose-a_slam.png：普攻起手、落拳。
- sentinel-pose-q_raise.png、sentinel-pose-q_slam.png：双拳重砸。
- sentinel-pose-e_brace.png、sentinel-pose-e_roar.png：收拳护身、张臂。
- sentinel-pose-r_raise.png、sentinel-pose-r_slam.png：大招抬拳、猛砸。
- sentinel-pose-run1.png 至 sentinel-pose-run8.png：走路八帧。
- sentinel-pose-d_fall.png、sentinel-pose-d_down.png：跪倒、伏地；伏地独眼已熄灭。
- raw/：以上 18 张原始生成文件，以及一张带重复头部的弃稿 rejected-run2-double-head.png（不得导入）。
- generation-prompts.txt：最终提示词、参考路径和来源输出路径。
- validation.json：逐文件尺寸、可见包围盒、半透明像素数量及 SHA-256。
- index.html：原图浏览页。

## 已验证

18 张独立图齐全，全部 1254×1254 RGBA；成品与 raw 同名文件逐字节一致。没有对姿势图缩放、重采样、抠图、程序拼接身体或替换头部。均由画图模型逐张生成，附定稿、头部、对应 3D 姿势和骨架参考。run2 重复头部已通过重新生图修正。

## 规格偏差与导入注意

生成器未严格执行全硬 alpha、固定 8 px 网格、头部逐像素复制以及精确骨架投影。姿势间的体块、拳头尺寸和站位也有差异，不能直接视作已经对齐的游戏动作帧。可见包围盒和半透明像素已记录在 validation.json；不要把所有非零 alpha 的杂点当作身体边界。

8 张走路原稿有迈步差异，但未在游戏中证明连续循环平顺或严格的近远腿交替。普通重砸与大招落拳均已压低身体，但与提供的骨架仍为近似。死亡终态是伏地石堆造型，未声称散块与原生动画逐像素一致。

后续应从 raw 按各图实际格子读回，再按定稿体块统一模型比例、头部、地面 y=1176 和动作锚点。本次遵照“不再缩放或重新取样”的要求保留了动作原图，这些偏差没有通过代码掩盖。仅当上述像素一致性与循环检查完成后，才能称为可直接导入的最终游戏动画。
