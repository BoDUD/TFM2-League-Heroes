# 范德尔动作素材交付
已生成并整理 15 张姿势：a_wind、a_punch、a_back、q_guard、e_crouch、e_upper、r_air、r_land、r_slam、run1–run4、d_fall、d_down。

每张输出为 1254×1254 RGBA、12px 对齐网格、硬 alpha（仅0/255），最低点在 y1176。美术来自内置 image_gen；整理仅取格、映射定稿配色、整体缩放/归位，没有用代码拼身体或绘制动作。raw/ 保存所选生成原稿，manifest.json 记录原稿尺寸、SHA256、输出位置与处理方法。生成器并未原生精确遵守所有网格要求，所以导入请使用整理后的 PNG，raw 用于重新取格。

e_crouch 背后的第三条手臂已用 image_gen 修正。q_guard 初次修正把拳套换到了另一条手臂，已弃用；交付版本按骨架重画，拳套臂横过胸前举到脸右侧，单条紫色护臂，另一只是绷带拳，脸保持可见。弃用图片不在本包内。

generation-prompts.txt 包含实际提示词和修正记录；generation-jobs.json 是初次生成任务。preview.png 为15姿势总览；run-preview.gif 仅为四帧跑步素材演示，140ms/帧，不代表游戏最终时序。

两包合计334项技术检查全部通过，结果见 validation.json：文件齐全、尺寸、硬alpha、12px网格、最低点和非空。仍需导入端按实际头部定位、密度与动作表调帧；生图不保证每张脸逐格一致或骨架关节精确重合，游戏内插帧、运行节奏、碰撞与界面裁切尚未验证。本交付是动作美术素材，不是已安装并完成实机测试的英雄。

