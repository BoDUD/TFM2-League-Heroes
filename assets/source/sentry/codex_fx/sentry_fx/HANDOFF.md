# 苍蓝哨戒 · 特效与图标交付

## 完整清单

13 张特效序列，共 66 帧：a_bolt(4)、q_zap(4)、q_beam(4)、r_sweep(6)、a_hit(4)、q_hit(4)、e_split(5)、e_ring(6)、r_open(6)、r_hit(5)、q_shred(6)、e_slow(6)、r_shred(6)。

3 张技能图标：sentry_icon_skill.png、sentry_icon_skill2.png、sentry_icon_ult.png，均为 64×64。

## 使用文件

- pixel_1x/sentry_fx_*.png：最终游戏像素序列，单行等宽切格，优先使用这些文件导入。
- 文件夹根目录 sentry_fx_*.png：对应 1× 序列的严格 8 倍最近邻版本。
- manifest.json：帧数、cell_1x、生成原图布局、每帧取样窗口、对称方式、绑定关系和检查状态。
- raw/：生图原稿原样保存；同名文件为选用原稿，含 before-* / attempt1 的为历史版本。
- generation-prompts.txt / revision-prompts.json：实际提示词与补充修正。
- source-bindings.json：来源包的绑定清单。
- fx-overview-1.png / fx-overview-2.png / icon-overview.png：预览图，不用于切格。

## 导出与检查

全部美术源图通过内置 image_gen 生成，没有用代码拼出特效形状。特效按源包允许的流程取色导出：去除低透明度光晕、映射到指定色阶、逐逻辑格取不透明像素的多数颜色；覆盖率不足 15% 的格透明。校正生图单元位置后拼成最终横条。对称通过保留已有像素并镜像成对位置实现。图标取回 32×32 逻辑格，2 倍导出为 64×64。

检查已通过：全部 13 张的帧数、每格尺寸、非空帧、0/255 alpha；a_bolt/q_zap/q_beam 每帧上下对称，其余除 r_sweep 外每帧左右对称；8× 图与 1× 图逐像素对应；3 个图标尺寸正确。q_zap 四帧均保留 2×2 近白亮芯。

## 几何与集成说明

r_sweep 已重新生成较小发射光点，并将各帧发射中心注册到 cell_1x 的 (5,35)。扫射的极限角度是画布内近似：100×70 格、中心发射、90 格光柱与 ±30° 无法同时完整容纳，因此压缩了垂直范围以避免出画。manifest 中有 angle_note；不能将此图宣称为严格六个数学角度。

其他光点、石片尺寸和光束外形也保留生图的视觉近似，机器检查通过不等于每个美术细节与文字逐格一致。r_open/e_split 的核心高度及脚下效果位置按目标布局取回；导入时仍需和角色实际核位置做叠加预览。此包不包含游戏配置修改、绑定实施或游戏内运行验证。
