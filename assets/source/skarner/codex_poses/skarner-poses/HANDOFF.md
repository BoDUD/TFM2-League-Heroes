# 斯卡纳动作姿势交付说明

日期：2026-10-26

## 状态

**18张动作造型原稿已绘制并保存；严格动作素材验收未通过。** 本包不是已完成游戏接入的动画资产。源参考为用户提供的 skarner_pose_pack.zip，造型以其中2_design.png、头部1_head.png及2b_rock.png为依据；姿势参考对应骨架和League动作图。所有绘制和修订均使用内置image_gen；Python仅用于只读文件检查，没有逐格画图、裁剪、缩放或清理透明像素。

## 文件清单与目视记录

|文件|目视记录／待修项|
|---|---|
|skarner-pose-a_wind.png|选用 a_wind-final 修订：三尾上扬、双钳分开；仍未精确贴合骨架位置。|
|skarner-pose-a_strike.png|保留首稿（3枚毒刺可见）；两次前扎修订丢失第三尾，未选用。当前前扎幅度不足，仍需重画。|
|skarner-pose-q_dig.png|选用 q_dig-final，已补出第三枚毒刺；第三尾的连续路径与粗细仍需逐格核对。|
|skarner-pose-q_lift.png|三尾举石已绘制；身体及石头尺度与骨架存在偏差。|
|skarner-pose-t_wind.png|巨石后举已绘制；毒刺与石头的抓握关系、后仰幅度需修正。|
|skarner-pose-t_throw.png|三尾前甩、无巨石；尾长及最右端边距仍需核对。|
|skarner-pose-w_rear.png|选用 w_rear-final，移除多余第三钳；抬升高度、六腿完整性和骨架位置需核对。|
|skarner-pose-w_slam.png|低伏砸地已绘制；输出尺寸错误，不能直接做等尺寸动画帧。|
|skarner-pose-e_charge.png|后拖尾冲锋已绘制；输出尺寸错误，不能直接做等尺寸动画帧。|
|skarner-pose-e_grab.png|双钳收拢已绘制；头部与尾巴尺度需统一。|
|skarner-pose-r_lash.png|三尾前伸已绘制；输出尺寸错误，不能直接做等尺寸动画帧。|
|skarner-pose-r_hold.png|三尾向前下压已绘制；弧线和头部位置未精确对齐骨架。|
|skarner-pose-run1.png|跑步首帧；六足前后遮挡与原始骨架需再次逐格核对。|
|skarner-pose-run2.png|跑步过渡帧；输出1263×1246，身体位置漂移，不能直接与其余跑步图串帧。|
|skarner-pose-run3.png|另一组迈步已绘制；头部和躯干与run1仍有细节及尺度漂移。|
|skarner-pose-run4.png|另一组抬腿已绘制；头部和躯干与run1仍有细节及尺度漂移。|
|skarner-pose-d_rear.png|直立尾部死亡前段已绘制；角色及尾部高度偏离骨架。|
|skarner-pose-d_down.png|三尾平摊倒地已绘制；腿部遮挡、尾长、头部和整体尺寸仍需统一。|

## 验证结论

- 共18张独立PNG：12张普攻/技能姿势、4张跑步、2张死亡，无待机/挨打新增图。
- 14张尺寸为1254×1254；e_charge、r_lash、w_slam为1388×1133；run2为1263×1246。
- 所有图有真实透明背景，但18张均含部分透明像素，不满足alpha只能0/255。
- 18张均未通过从画布左上角起的9×9严格统一网格检查。不能直接按9px读回。
- 头部是生成模型重绘，未能逐像素复制1_head.png；躯干、尾长、钳长与脚底基线并未严格统一。不能声称已通过比例、骨架位置或连续动画验收。
- raw/保留全部生成文件，包含未选用/失败修订。仅根目录18张是本次选用候选；不得自动把raw/当作活动素材。特别是a_strike-final和a_strike-final2仍只有两条明确可辨尾巴，未采用；a_wind-revision与w_rear初稿多出钳子，也未采用。
- VALIDATION.md和validation.json记录尺寸、alpha、网格、可见bbox与SHA-256。检查脚本仅分析原始文件，未把后期加工冒充成生成结果。

## 其余交付文件

- generation-prompts.txt：每次成功生成与修订实际使用的提示词。
- raw/：原始生成图，不改像素，文件名保留修订编号。
- source-manifest.json：原始生成路径、选用图的对应关系，便于追溯。

## 未完成的下一道验收

先处理普攻扎下幅度、掘石第三尾连续性等姿势问题；再统一9px逻辑网格、硬alpha、头部逐像素复用、1254画布、身体比例与地面基线。跑步需在同一锚点和尺寸下完成4帧连续性验证。本次未写入TFM2仓库或安装模组，未生成图集/动画表，未执行游戏内运行验证。

