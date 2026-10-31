# 远古巨龙动作姿势交付

2026-11-01，Asia/Tokyo。18/18张动作姿势原稿已全部生成，采用内置image_gen逐张参考定稿、头部、该姿势渲染和骨架；没有用程序绘制角色，也没有对动作源图缩放或重采样。

## 文件

正式图片为elderdragon-pose-<动作名>.png；raw/中同名文件为未改动原稿，与正式图片SHA256相同。动作包含a_back、a_bite、q_rear、q_breath、e_rear、e_slam、r_jump、r_land、run1至run8、d_fall、d_down。

另含generation-prompts.txt、retry-prompts.txt、manifest.json、SHA256SUMS.txt、contact-sheet.jpg和flight-review.gif。概览与GIF经过缩略，仅供审阅；导入应读取单张raw。raw/rejected/保留已退回的q_rear双头首轮，禁止导入；正式q_rear已重画为单头。

## 检查与限制

18张均为1254×1254 RGBA，PNG可解码，主文件与raw字节一致；姿势无外置火焰/风尘特效，倒地帧眼睛和嘴部熄光，8帧飞行图已齐。飞行GIF可见高举、平展和下拍姿态，但身体位置、头部形状与尺度仍有帧间波动，不能视为已验收的无跳变游戏动画。

生成器没有严格实现硬alpha：18张都有中间透明度。严格6px网格、逐格相同的头部、统一身体尺度和y=1176基线仍未达到工程验收标准。按要求保留原稿，未擅自重采样。实际主体包围盒、alpha档数和哈希见manifest.json。后续应按原稿实际网格读回并对齐头部/身体与基线，清理alpha后再导入。

本包完成18张动作源图的数量交付；上述工程差异明确保留，未声称运行时模型已完成。未修改游戏、仓库、DLL或配置，也未执行附件给其他代理的导入/提取流程。
