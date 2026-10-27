# 范德尔 A/B 模型原画：候选交付，技术规格未通过

内置 image_gen 已生成 A 站姿和 B 格斗姿势。参考来自用户的 vander_pack0.zip。图片原样保存，未经脚本缩放、抠图或重绘。

文件：
- vander-A.png、vander-B.png：两张候选原画。
- raw/vander-A-original.png、raw/vander-B-original.png：原始生成文件，与候选逐字节一致。
- raw/vander-A-grid-attempt-not-selected.png：追加修正尝试，面部辨识度下降，未选用。
- generation-prompts.txt：最初 A/B 提示词。
- generation-followup.txt：实际 B 追加指令及修正提示词。
- qa.json：尺寸、alpha、主体范围。

两张实际均为 1254×1254 RGBA，有真实透明背景，但含半透明像素，未达到硬 alpha。A 的 alpha≥128 主体范围为 (363,358)-(918,1240)，B 为 (244,407)-(1032,1217)。1536×1536、A高638/B高572、脚底y1390、统一11px网格均未通过，A头身比例也偏细致像素插画。不要按11px直接读回，不要据此确定PPU。

A修正生成没有可靠解决规格且面部辨识度下降，因此未替换候选。后续需统一网格、画布、头身比例和硬alpha，再做游戏尺寸对照及动作。当前不能声明为通过技术验收的游戏精灵或完整可玩英雄。

未修改用户仓库、已有未提交文件、游戏安装或配置。未制作动画、未做游戏内测试。压缩包为 vander_picture_review.zip，供造型审阅。

