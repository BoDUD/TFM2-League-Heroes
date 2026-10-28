# 敖兴动作素材交付

依据用户提供的 aoshin_pose_pack.zip 制作。图形来源为内置 image_gen，随后对生图进行调色板多数取样、统一网格与定位；没有使用程序绘制替代龙身。未修改仓库或安装游戏资产。

## 文件

15 张动作 PNG：

- aoshin-pose-a_coil.png
- aoshin-pose-a_lunge.png
- aoshin-pose-a_back.png
- aoshin-pose-q_rear.png
- aoshin-pose-q_breath.png
- aoshin-pose-e_rise.png
- aoshin-pose-r_call.png
- aoshin-pose-r_storm.png
- aoshin-pose-run1.png
- aoshin-pose-run2.png
- aoshin-pose-run3.png
- aoshin-pose-run4.png
- aoshin-pose-d_hit.png
- aoshin-pose-d_back.png
- aoshin-pose-d_away.png

另含 raw/ 原始生成图、raw/rejected/ 被拒绝的正面阵亡初稿、generation-prompts.txt 实际提示词、manifest.json 定位与参考清单、QA.json 格式检查、previews/contact-sheet.png 总览和 previews/flight.gif 四帧飞行预览。最终 d_back 省略第 5 张定稿骨架参考，追加仰面翻转要求；d_away 同样省略第 5 张参考，追加背向垂落要求。

## 已通过的格式检查

15/15：1254×1254，RGBA，alpha 仅 0/255；从 (0,0) 对齐的 12px 方格，实际网格画区 1248×1248，剩余右侧/底部 6px 透明；y≥1176 区域透明。采用各姿势参考的外接范围进行等比放置。原始生成文件保持原样，原始画布尺寸和 alpha 不一定符合整理版规格。

## 画面验收边界

完整交付了 15 个动作素材及其原稿，但尚不等于 15 帧全部达到附件的美术一致性验收要求。生成模型没有逐格固定同一张头：部分帧的面具、龙角、眼睛位置、爪形和身体比例有差异；部分姿势与骨架只能近似，尤其 a_back 仍有较长上扬尾巴，飞行 run1–run4 的头颈角度与身体体积仍有变化。当前没有通过“所有帧固定头部逐像素一致”和游戏内连播无抖动验收。

导入应先对照 raw/ 与已批准的 1_head.png，审核头部、粗细和动作幅度，再确定是否需要针对性重绘。flight.gif 为素材连播预览，不是游戏内运行证据。未执行游戏、骨骼绑定、运行时或地形遮挡验证；没有把这些项目标为通过。
