# 赛恩第2步：36帧动作初稿交付

## 文件与范围

普攻5、Q蓄力4、Q砸地5、E5、W4、R冲锋2、R撞击5、死亡6，共36帧。未额外绘制待机或跑步。

每帧根目录PNG为1536×1024，配套`*_1x.png`为219×146；共72张成品PNG。原始生图在`raw/`，未经重采样或覆盖。指定造型和来源文档也保存在`raw/`。

- `generation-prompts.txt`：36条实际提示词。
- `manifest.json`：每帧提示词、前帧引用与原稿/成品SHA256。
- `validation.json`：逐帧数值检查与处理记录。
- `cells.json`：包内原始帧序和时长，未修改。
- `preview/`：8个按原始时长播放的动作GIF，及4张逐帧查看卡。预览底色和标签不属于角色图。
- `../sion_strips_done.zip`：此目录完整打包。

## 已完成的检查

所有帧使用同一7px网格，原点(0,0)，大图与1倍图逐格一致。右侧3px和底部2px为网格余边。颜色仅来自指定27色，alpha仅0/255。所有成品第140行以下（y987及以下）均透明。

身体和动作由图像工具逐帧生成；地面对齐只按每帧最低非透明格做整数格平移，没有整个人缩放、没有脚本重画躯体。头部从指定101×75造型逐格复制，只平移，不缩放或旋转；已验证头部复制像素与来源一致。旧生成飘带及微小游离噪点已清理。这里的头部一致性验证针对来源头部的非透明像素，并不等同于整幅人物形状完全一致。

所有后续帧在生成时均附上同一动作当时已完成的上一帧。五个明确回到站姿的收招帧复用了包内指定待机造型，死亡6保持死亡5静止；各自生成原稿和处理候选仍在raw/保留。Q砸地2和死亡3另有补画修正版；对应旧候选也保留在raw/。

为让蓄力循环不换体量，蓄力4的最终选择复用蓄力3，仅把第53行以上的已生成举斧/手部区域上移一格，躯干、头和腿保持不变。R的两帧最终选择复用同一张冲锋上半身；为避免接缝，整张R1复用于R2，原始第2步腿候选在raw/，按包内说明后续替换走路腿。R两张最终PNG因此相同，尚不构成有步差的完整跑动循环。

## 尚未完全达到的要求

这批是动作初稿，尚未达到可直接入游戏的全部几何一致性要求。非收招帧的斧刃形状、斧柄长度、肩甲和护手轮廓仍有生成差异，不能宣称它们都是同一刚体的严格平移/旋转。部分姿势与骨架的位置、重心、身体比例也有偏差，67格站高并未对所有动态姿势逐部位严格锁定，第100列站位和每只靴底贴线也未全部严格达到。请据raw原稿及预览逐帧选用/修正。

E怒吼3/4采用了指定头部，以优先满足“每帧同一张头，只平移”，没有额外改变下颌笼来画张嘴。Q蓄力1/2后拉斧头的幅度仍不足；W2/3的手臂收到身前姿态仍有偏差。

源包中`now/sion_skill_charge_4.png`和`now/sion_skill2_w_4.png`完全透明：前者使用蓄力3骨架及上一帧补足参考，后者按说明回到指定待机造型。

没有绘制冲击波、护盾、裂地、声波等特效；没有导入游戏、调整真实出手时序、生成PPU帧或修改仓库。来源文档末尾给Claude的后续入库、独立审查、动画拼装和平衡模拟不属于本次执行范围。

## 逐帧记录

“地面对齐Δy”为读回后整数格平移，正值向下；不代表缩放。

| 文件 | 实际提示词 | 地面对齐Δy | 备注/限制 |
|---|---|---:|---|
| `sion_attack_1.png` | `raw/sion_attack_1-prompt.txt` | 0 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_attack_2.png` | `raw/sion_attack_2-prompt.txt` | 3 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_attack_3.png` | `raw/sion_attack_3-prompt.txt` | 0 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_attack_4.png` | `raw/sion_attack_4-prompt.txt` | 1 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_attack_5.png` | `raw/sion_attack_5-prompt.txt` | -4 | 收招复用指定造型 |
| `sion_skill_charge_1.png` | `raw/sion_skill_charge_1-prompt.txt` | 3 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收；斧头后拉幅度仍不足 |
| `sion_skill_charge_2.png` | `raw/sion_skill_charge_2-prompt.txt` | 2 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收；斧头后拉幅度仍不足 |
| `sion_skill_charge_3.png` | `raw/sion_skill_charge_3-prompt.txt` | 4 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_skill_charge_4.png` | `raw/sion_skill_charge_4-prompt.txt` | 1 | 原骨架为空，采用蓄力3骨架和前一帧作参考；举斧区域从蓄力3上移一格；躯干头腿不变；斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_skill_1.png` | `raw/sion_skill_1-prompt.txt` | 3 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_skill_2.png` | `raw/sion_skill_2-prompt.txt` | 6 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收；另有针对动作阶段的补画修正版 |
| `sion_skill_3.png` | `raw/sion_skill_3-prompt.txt` | -3 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_skill_4.png` | `raw/sion_skill_4-prompt.txt` | -5 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_skill_5.png` | `raw/sion_skill_5-prompt.txt` | -3 | 收招复用指定造型 |
| `sion_skill2_1.png` | `raw/sion_skill2_1-prompt.txt` | 7 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_skill2_2.png` | `raw/sion_skill2_2-prompt.txt` | 1 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_skill2_3.png` | `raw/sion_skill2_3-prompt.txt` | 0 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收；优先保留指定头部逐格一致，未另画张开的下颌 |
| `sion_skill2_4.png` | `raw/sion_skill2_4-prompt.txt` | -3 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收；优先保留指定头部逐格一致，未另画张开的下颌 |
| `sion_skill2_5.png` | `raw/sion_skill2_5-prompt.txt` | 1 | 收招复用指定造型 |
| `sion_skill2_w_1.png` | `raw/sion_skill2_w_1-prompt.txt` | 1 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_skill2_w_2.png` | `raw/sion_skill2_w_2-prompt.txt` | 2 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收；双手收到身前的姿势仍有偏差 |
| `sion_skill2_w_3.png` | `raw/sion_skill2_w_3-prompt.txt` | 0 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收；双手收到身前的姿势仍有偏差 |
| `sion_skill2_w_4.png` | `raw/sion_skill2_w_4-prompt.txt` | 1 | 收招复用指定造型 |
| `sion_ult_1.png` | `raw/sion_ult_1-prompt.txt` | -5 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_ult_2.png` | `raw/sion_ult_2-prompt.txt` | 3 | R上半身锁定1帧；第2步腿候选保留raw待换腿；斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_ult_hit_1.png` | `raw/sion_ult_hit_1-prompt.txt` | 0 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_ult_hit_2.png` | `raw/sion_ult_hit_2-prompt.txt` | 1 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_ult_hit_3.png` | `raw/sion_ult_hit_3-prompt.txt` | -2 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_ult_hit_4.png` | `raw/sion_ult_hit_4-prompt.txt` | -1 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_ult_hit_5.png` | `raw/sion_ult_hit_5-prompt.txt` | 0 | 收招复用指定造型 |
| `sion_dead_1.png` | `raw/sion_dead_1-prompt.txt` | 5 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_dead_2.png` | `raw/sion_dead_2-prompt.txt` | 0 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_dead_3.png` | `raw/sion_dead_3-prompt.txt` | -4 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收；另有针对动作阶段的补画修正版 |
| `sion_dead_4.png` | `raw/sion_dead_4-prompt.txt` | -2 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_dead_5.png` | `raw/sion_dead_5-prompt.txt` | -4 | 斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
| `sion_dead_6.png` | `raw/sion_dead_6-prompt.txt` | -5 | 静止帧复用死亡5；斧头/肩甲几何仍有生成差异，未通过刚体一致性验收 |
