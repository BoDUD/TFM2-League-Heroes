# 远古巨龙特效交付

2026-11-01，Asia/Tokyo。12/12张特效序列和3/3个技能图标已生成与导出，采用内置image_gen。形状来自生成原稿，没有程序拼方块代画特效。

## 文件与导入

- elderdragon_fx_<名字>.png：横向单行序列，每个逻辑像素最近邻放大8倍。
- pixel_1x/中的同名PNG：原尺寸游戏像素序列，导入使用这一份。
- elderdragon_icon_skill.png、elderdragon_icon_skill2.png、elderdragon_icon_ult.png：64×64图标（32×32逻辑像素放大2倍）。
- raw/：生成原稿，原样保留；raw/rejected/a_splash-too-thin.png为末帧多数取色后为空的失败首轮，不可导入。
- 同名GIF：12组动画预览；contact-sheet.jpg为整套概览。
- generation-prompts.txt、retry-prompts.txt、asset-specs.json、manifest.json、SHA256SUMS.txt：实际提示词、尺寸/帧数/对称方向/绑定及校验记录。

## 制作与检查

原稿以2列多行生成，按左至右、上至下读序；最终重排为横向单行。原稿实际尺寸与规则网格见manifest.json；每格划分为规定的逻辑像素单元，先限制到提示词色板，再在每个单元取多数色（透明度低于128或近黑背景计透明）。最后对每组镜像像素取较亮色，以严格满足对称；所有这些整理操作均非重新绘制形状。未假定生成器真的输出16px网格。

12组序列共68帧：a_hit4、a_splash4、q_fire6、q_hit4、ig6、p_exec6、e_cast6、e_slow6、e_guard6、r_slam8、r_stun6、r_vamp6。检查通过：每帧非空、每序列帧图不同、帧数和cell_1x尺寸正确、alpha仅0/255、q_fire上下逐像素对称且朝右、其余左右逐像素对称、8倍版与1倍版最近邻放大结果一致、GIF帧数正确、图标64×64。

已检查整套概览：龙焰为青白/深青色系；命中/引燃在身体两侧和脚下，中间留空；护体/吸血为周边环绕；落地为低位椭圆冲击波；图标分别体现吐息、拍翼和下砸。小尺寸效果的火星/风圈较为简化，应以pixel_1x为实际读数，而非高细节raw。

这只是美术与结构检查，未在游戏内验证层级、定位、帧时长、循环平滑或遮挡，manifest中的绑定沿用附件资料供后续导入，未实施运行时绑定或DLL修改。动作包仍有独立工程规格差异，见对应HANDOFF。
