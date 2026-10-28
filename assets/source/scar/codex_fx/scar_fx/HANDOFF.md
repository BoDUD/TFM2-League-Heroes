# 刀疤特效与技能图标交付

11 组特效、合计 58 帧，以及 3 个技能图标已完成。特效与图标均由内置 image_gen 绘制，原稿保留在 raw/。

## 使用文件

- scar_fx_*.png：每组一条水平动画带，所有帧等宽等高，按阅读顺序排列；为原尺寸精确最近邻放大 8 倍。
- pixel_1x/scar_fx_*.png：导入应使用的原尺寸逻辑像素动画带，帧大小与帧数见下表及 manifest.json。
- scar_icon_skill.png、scar_icon_skill2.png、scar_icon_ult.png：64×64，不透明，2×2 的像素格。
- raw/：11 张特效原稿和 3 张图标原稿，未经修改。
- generation-prompts.txt：实际提示词；原稿因生成画布限制采用多行布局，交付已切为单行。
- manifest.json：cell_1x、帧数、源图切格位置、源图内容边界、输出轮廓尺寸、对称方式、循环标记和源图 SHA-256。
- validation.json：14 项资产的尺寸、透明度、对称性与非空检查。
- fx-preview.png、icon-preview.png、previews/*.gif：检查用预览。GIF 100ms/帧仅用于审阅，不规定引擎时长。

## 规范化

脚本按每个生成帧的可见内容切出，依照提示中的闪光、爆炸和地面圈大小重新放入对应逻辑格。颜色取自给定色阶，以不透明样本多数色为主；保留源图高光的小色块，并采用 18% 覆盖门槛，防止细闪光在缩小时消失。没有用代码拼出新的特效形状。

全部帧硬透明 alpha=0/255，逐像素左右对称；q_bomb 还逐像素满足 180° 旋转对称，并裁掉生成球体的方形角落。保留其横向青绿条纹，不强制 90° 旋转一致。p_heal 和 r_guard 清空身体中部，地面效果放在格子底部，人物、滑板和长矛不包含在特效里。

58 帧均非空，每一组中的各帧均不相同。所有 8 倍图与 pixel_1x/ 逐像素对应。未改写游戏数据或进行游戏内合成验证。

## 帧表

| 特效 | 帧数 | cell_1x | 循环 |
|---|---:|---|---|
| scar_fx_a_hit.png | 4 | 16×16 | 否 |
| scar_fx_p_hit.png | 5 | 24×24 | 否 |
| scar_fx_p_heal.png | 5 | 36×42 | 否 |
| scar_fx_q_bomb.png | 4 | 10×10 | 是 |
| scar_fx_q_hit.png | 6 | 34×34 | 否 |
| scar_fx_q_stun.png | 6 | 20×10 | 是 |
| scar_fx_e_hit.png | 4 | 22×22 | 否 |
| scar_fx_r_bomb.png | 6 | 40×24 | 否 |
| scar_fx_r_land.png | 8 | 84×34 | 否 |
| scar_fx_r_hit.png | 4 | 18×20 | 否 |
| scar_fx_r_guard.png | 6 | 40×44 | 是 |
