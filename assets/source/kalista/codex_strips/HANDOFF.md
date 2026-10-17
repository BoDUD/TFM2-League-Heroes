# 卡莉斯塔动作帧阶段交付：40/46，尚未完成验收

图片生成工具在制作R落地帧时返回 HTTP429 usage_limit_reached。当前提供40帧候选，其中34帧使用生成画稿逐格导出、6帧收尾直接复用批准的定稿。死亡6帧尚未制作。不能将本包标为全部完成或直接可用的正式游戏动作包。

## 文件与预览

- 根目录：40张1536×1024透明PNG，以及对应40张219×146的`_1x.png`。
- `raw/`：39张未重采样生成原稿和对应实际提示词；部分收尾原稿仅作记录，最终收尾采用定稿。
- `preview/`：run、attack、hop_b、hop_f、skill、skill2、ult、ult2共8组GIF与逐帧接触表。GIF灰底仅用于预览，PNG本体透明。
- `cells.json`：保留原包46帧清单与时长，不能据此误以为46张图均已存在。
- `palette.png`：批准造型的实际34色色板（原说明写40色，附件实际是34色）。
- `QA.json`：逐帧网格、包围盒、位置调整和来源记录。
- `STATUS.json`：实际可用/缺失清单、文件摘要、技术检查与生成额度阻塞。
- `pending/`：死亡6帧的待执行提示词，没有伪造对应图片。

## 导出方式与技术检查

原稿1536×1024。按原位置每7×7源像素读取，先把alpha低于224的柔光/半透明像素归透明，其余颜色映射到批准的34色，再对每格49个像素取多数颜色（包含透明票）；没有取中心点，也没有缩放人物。最后按格整数展开成7×7色块，画布右侧3px、底部2px透明。若原稿越过脚底线，只整格上移，调整量列在QA.json。

40帧已检查：画布尺寸、硬alpha、严格色板、7px格对齐、大图与1x逐格完全一致、y973及以下透明。六张回到蹲姿的收尾帧来自原批准造型，没有重新生成角色。

## 美术与动作验收未通过项

- 生成器没有逐格复用整颗头；头盔、脸、羽冠和铠甲细节在非收尾帧间仍有变化。不能声称“同一张脸贯穿所有帧”。
- 人物大小、髋腿相对位置与矛长仍有波动；尤其run帧间比例漂移，尚未达到固定骨架/刚体矛的要求。
- run有腿部变化，但未可靠实现1–4近腿在前、5–8远腿在前，以及第3/7帧交叉；跑步动作验收失败。
- 普攻手势可读，近侧手保留长矛；头和矛仍需同一尺度修整。
- Q第3/4帧确实空手、第5帧恢复持矛，但生成图把向右伸出的投掷臂画在远侧，近远侧手臂关系不符，需重画。
- E可读出伸手、握拳与回扯；动作幅度、拳头形状和恢复连续性仍需精修。
- R召唤可读出举手过头，甩出2/3帧可读出腾空；但站起高度、身体/头比例以及空中腿姿未按骨架精确一致。
- 前后跳方向大体可读，尚未精确锁定同一身高、髋腿比例和落地点。落地统一回定稿站位，尚未保留跳后的全部位移。
- 原稿普遍带有不需要的柔光；导出剔除了低alpha部分，部分细薄轮廓/手脚也可能丢格，需要逐像素清理。
- 死亡6帧完全缺失，不能通过复制站姿或对已有帧平移冒充。

当前图是候选素材与可检查的技术导出，未导入游戏、未完成动画打包/出手时间调整/平衡测试。

## 后续接续

工具报告图片额度预计于2026-10-16 20:33:15（日本时间）重置；此为工具返回时间，不保证届时服务一定可用。本次没有创建定时自动重试。恢复生成能力后先补死亡6帧，再修run换腿、Q投掷手、固定整头和刚体长矛，之后才能做正式验收。

## 每帧来源与提示词

|文件|来源/实际提示词|
|---|---|
|kalista_run_1.png|raw/kalista_run_1.png；raw/kalista_run_1.prompt.txt|
|kalista_run_2.png|raw/kalista_run_2.png；raw/kalista_run_2.prompt.txt|
|kalista_run_3.png|raw/kalista_run_3.png；raw/kalista_run_3.prompt.txt|
|kalista_run_4.png|raw/kalista_run_4.png；raw/kalista_run_4.prompt.txt|
|kalista_run_5.png|raw/kalista_run_5.png；raw/kalista_run_5.prompt.txt|
|kalista_run_6.png|raw/kalista_run_6.png；raw/kalista_run_6.prompt.txt|
|kalista_run_7.png|raw/kalista_run_7.png；raw/kalista_run_7.prompt.txt|
|kalista_run_8.png|raw/kalista_run_8.png；raw/kalista_run_8.prompt.txt|
|kalista_attack_1.png|raw/kalista_attack_1.png；raw/kalista_attack_1.prompt.txt|
|kalista_attack_2.png|raw/kalista_attack_2.png；raw/kalista_attack_2.prompt.txt|
|kalista_attack_3.png|raw/kalista_attack_3.png；raw/kalista_attack_3.prompt.txt|
|kalista_attack_4.png|raw/kalista_attack_4.png；raw/kalista_attack_4.prompt.txt|
|kalista_attack_5.png|最终采用批准定稿；生成尝试记录raw/kalista_attack_5.prompt.txt|
|kalista_hop_b_1.png|raw/kalista_hop_b_1.png；raw/kalista_hop_b_1.prompt.txt|
|kalista_hop_b_2.png|raw/kalista_hop_b_2.png；raw/kalista_hop_b_2.prompt.txt|
|kalista_hop_b_3.png|raw/kalista_hop_b_3.png；raw/kalista_hop_b_3.prompt.txt|
|kalista_hop_b_4.png|最终采用批准定稿；生成尝试记录raw/kalista_hop_b_4.prompt.txt|
|kalista_hop_f_1.png|raw/kalista_hop_f_1.png；raw/kalista_hop_f_1.prompt.txt|
|kalista_hop_f_2.png|raw/kalista_hop_f_2.png；raw/kalista_hop_f_2.prompt.txt|
|kalista_hop_f_3.png|raw/kalista_hop_f_3.png；raw/kalista_hop_f_3.prompt.txt|
|kalista_hop_f_4.png|最终采用批准定稿；生成尝试记录raw/kalista_hop_f_4.prompt.txt|
|kalista_skill_1.png|raw/kalista_skill_1.png；raw/kalista_skill_1.prompt.txt|
|kalista_skill_2.png|raw/kalista_skill_2.png；raw/kalista_skill_2.prompt.txt|
|kalista_skill_3.png|raw/kalista_skill_3.png；raw/kalista_skill_3.prompt.txt|
|kalista_skill_4.png|raw/kalista_skill_4.png；raw/kalista_skill_4.prompt.txt|
|kalista_skill_5.png|最终采用批准定稿；生成尝试记录raw/kalista_skill_5.prompt.txt|
|kalista_skill2_1.png|raw/kalista_skill2_1.png；raw/kalista_skill2_1.prompt.txt|
|kalista_skill2_2.png|raw/kalista_skill2_2.png；raw/kalista_skill2_2.prompt.txt|
|kalista_skill2_3.png|raw/kalista_skill2_3.png；raw/kalista_skill2_3.prompt.txt|
|kalista_skill2_4.png|raw/kalista_skill2_4.png；raw/kalista_skill2_4.prompt.txt|
|kalista_skill2_5.png|最终采用批准定稿；生成尝试记录raw/kalista_skill2_5.prompt.txt|
|kalista_ult_1.png|raw/kalista_ult_1.png；raw/kalista_ult_1.prompt.txt|
|kalista_ult_2.png|raw/kalista_ult_2.png；raw/kalista_ult_2.prompt.txt|
|kalista_ult_3.png|raw/kalista_ult_3.png；raw/kalista_ult_3.prompt.txt|
|kalista_ult_4.png|raw/kalista_ult_4.png；raw/kalista_ult_4.prompt.txt|
|kalista_ult_5.png|raw/kalista_ult_5.png；raw/kalista_ult_5.prompt.txt|
|kalista_ult2_1.png|raw/kalista_ult2_1.png；raw/kalista_ult2_1.prompt.txt|
|kalista_ult2_2.png|raw/kalista_ult2_2.png；raw/kalista_ult2_2.prompt.txt|
|kalista_ult2_3.png|raw/kalista_ult2_3.png；raw/kalista_ult2_3.prompt.txt|
|kalista_ult2_4.png|最终采用批准定稿；因额度限制未生成原稿|
|kalista_dead_1.png|未生成；pending/kalista_dead_1.prompt.txt|
|kalista_dead_2.png|未生成；pending/kalista_dead_2.prompt.txt|
|kalista_dead_3.png|未生成；pending/kalista_dead_3.prompt.txt|
|kalista_dead_4.png|未生成；pending/kalista_dead_4.prompt.txt|
|kalista_dead_5.png|未生成；pending/kalista_dead_5.prompt.txt|
|kalista_dead_6.png|未生成；pending/kalista_dead_6.prompt.txt|
