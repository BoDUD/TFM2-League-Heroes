# 拉露恩动作图交付

本包已完成14张动作图的生图、像素格整理和文件交付。源素材来自用户提供的 alune_pose_pack.zip；采用其中已定稿的坐姿造型，未沿用上一轮未定稿的高细节造型。

## 最终文件

每张为1254×1254 RGBA PNG、12px统一方格，透明度仅0或255：

- alune-pose-a_wind.png：普攻起手。
- alune-pose-a_throw.png：向右甩出月环。
- alune-pose-a_catch.png：站立接环。
- alune-pose-q_raise.png：站立举环。
- alune-pose-q_call.png：站立举拳引月。
- alune-pose-e_bless.png：坐姿祝福。
- alune-pose-r_raise.png：双手举环。
- alune-pose-r_call.png：指天后仰。
- alune-pose-run1.png、run2.png、run3.png、run4.png：四张坐姿滑行。
- alune-pose-d_fall.png：后仰跌落。
- alune-pose-d_down.png：倒地与破碎武器。

文件的完整名称与实测尺寸、包围框见manifest.json。除run2上浮一格外，底边位于y=1176基线，最下面的不透明像素行是1175；run2基线1164。四张移动图按相同的整体可见高度整理。

## 附件

- raw/：最终采用的未改动生图原稿；raw/rejected/：因多余月牙、重复月球、比例漂移等被淘汰的尝试，不用于切格。
- generation-prompts.txt：内置image_gen实际提示词，含修订前尝试。
- manifest.json：逐图实测数据。
- poses-preview.png：14图联系表。
- glide-preview.gif：四张移动帧的160ms预览，供检查；不是游戏动画时长设置。
- export-validation.json：尺寸、透明、网格和文件完整性检查。

全部角色绘画与修订均使用image_gen。后处理只对生成图取格、取色、完整画幅缩放和基线定位，没有用代码绘制或替代身体。1254不是12的整数倍，完整12px网格覆盖1248×1248，右/下最后6px保持透明。

## 视觉验收边界

已修正接环的大月牙误画、举环重复月球、召唤坐姿、举环比例和甩环多余圆环。角色脸、衣纹和武器仍存在生成模型造成的帧间差异；**没有达到头部逐像素完全相同、骨架逐点注册和每条手臂精确12格的严格验收标准**。举环的小环按简化蓝/青铜闭环表达，内部螺旋细节也未逐格复刻。四帧移动的轮廓高度相同不代表内部身体各部位完全注册。

因此本包是齐全、经过技术整理的动作素材交付，适合继续做游戏帧对齐和精修；不能将它声称为已通过游戏实机验收的动画。本次没有导入模组、修改技能数据或测试游戏运行。导入时应以raw原稿与用户定稿头部作进一步对齐，并分别检查头像、战斗框和地形遮挡。

最终技术检查：14/14张通过。文件SHA-256及逐项结果见export-validation.json。交付说明在最终检查后写入，再生成压缩包。
