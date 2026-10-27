# 范德尔特效素材交付
已生成并整理13张特效动画条，共73帧，以及3张64×64技能图标。

根目录 vander_fx_*.png 是8倍放大版；pixel_1x/ 是原尺寸导入版，均为单行、帧从左到右。图标 vander_icon_skill.png、vander_icon_skill2.png、vander_icon_ult.png 是64×64、2px网格。raw/ 保留 image_gen 母版，generation-prompts.txt 记录实际提示词，manifest.json 记录帧数、cell_1x、原稿布局/行边界、对称方法、源文件SHA256和每帧像素数。

a_hit 4帧 16×16；q_guard_in 5帧44×48；q_guard 6帧44×48；q_ready 6帧20×48；q_hit 6帧30×30；q_taunt 6帧16×44；e_dash 5帧32×14；e_hit 5帧22×32；e_stun 6帧18×44；r_slam 8帧88×30；r_hit 4帧18×20；r_hold 6帧44×50；p_watch 6帧40×12。以上尺寸均为单帧游戏像素。

所有美术均使用内置 image_gen 绘制，没有程序绘制替代特效。为避免极宽母版造成漏帧，生成时改为多行母版，取格后重排成所需横条；原稿实际分行与提示布局不同的部分按图复核后记录。按指定色阶映射，每格取前景多数颜色；输入alpha阈值128、前景覆盖至少35%即保留，输出alpha只有0/255，以免细光圈被透明背景投票吞没。每对左右格共同取色，确保每帧逐格严格对称。

q_ready 提取拳徽放在顶部；e_stun 提取星环放在顶部；q_taunt 提取上方怒气标记与下方光圈，中间身体留空；p_watch 提取光圈置于底部。其他特效保留生成的动作演变。导入请使用 pixel_1x/，不要把多行raw直接按单行切格。

preview.png 是总览，animation-preview.gif 为均匀140ms/帧的素材演示，不是游戏绑定时序。两包合计334项技术检查全部通过：31项素材齐全、73帧均非空、原尺寸/8倍尺寸一致、硬alpha、逐帧左右对称及头顶标记留空规则，详见validation.json。

角色数据、view_effects/view_buffs、技能图标槽位和DLL仍需在导入端绑定；未修改游戏安装或仓库，未运行游戏内亮度、遮挡、帧时序或性能测试。原稿的色块密度及渐变不一定符合最终规格，以整理后的pixel_1x为交付规格依据。

