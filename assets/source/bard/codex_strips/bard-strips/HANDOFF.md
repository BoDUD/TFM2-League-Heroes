# 巴德38帧动作细稿交付

38/38帧已生成，所有文件已齐；**视觉要求尚未完全达标，仍需修正，不能当作通过一致性验收的动作成品。** 原先生图额度阻断已恢复，本次补齐25帧，并修正死亡第3、6帧。

## 文件

根目录：跑步8、普攻5、Q(skill)5、W(skill2)5、E(skill2_e)4、R(ult)5、死亡6，共38张`bard_<动作>_<n>.png`。`raw/`保留全部未经修改的生成及尝试稿。`prompts/`、`generation-prompts.txt`记录实际提示词。`validation.json`记录每张对应raw、格式、边界、红线下像素数、选用提示词和哈希。`previews/`为7组灰底缩略预览，仅预览缩小，主图未缩。`history/`保留之前13帧交付说明；旧`bard_strips_partial.zip`只是历史快照。`pending-prompts/`现为历史计划提示词存档，已无缺帧。新包为`bard_strips_done.zip`，名称指帧数齐全，**不代表视觉验收通过**。

## 格式与处理

全部38张为原生1536×1024 RGBA、alpha仅0/255。唯一处理为alpha阈值去背景柔光；成品RGB与所选raw逐点完全相同，已断言验证。没有缩放、平移、裁切、改色、粗格整理、贴头、拼接武器或代码补画。图像生成约4–5px像素画，不宣称每格严格对齐。后帧均附同动作前帧；同一脸和刚体乐器靠生图参考约束，未实现逐像素一致。骨架位置/高度仅近似匹配，部分非死亡帧超出y980；具体数字见validation。

## 每帧选用提示词与未达到项

|帧|实际选用提示词|未达到项|
|---|---|---|
|bard_run_1.png|prompts/bard_run_1-corrections.txt (attempt3)|号角较短，整体尺寸位置偏差；8帧未形成严格闭合循环。|
|bard_run_2.png|prompts/bard_run_2.png-repair.txt|号角较短，整体尺寸位置偏差；8帧未形成严格闭合循环。|
|bard_run_3.png|prompts/bard_run_3.png-repair.txt|号角较短，整体尺寸位置偏差；8帧未形成严格闭合循环。|
|bard_run_4.png|prompts/bard_run_4.png-repair.txt|号角较短，整体尺寸位置偏差；8帧未形成严格闭合循环。|
|bard_run_5.png|prompts/bard_run_5.png-repair.txt|号角较短，整体尺寸位置偏差；8帧未形成严格闭合循环。|
|bard_run_6.png|prompts/bard_run_6.png-repair.txt|号角较短，整体尺寸位置偏差；8帧未形成严格闭合循环。|
|bard_run_7.png|prompts/bard_run_7.png-repair.txt|号角较短，整体尺寸位置偏差；8帧未形成严格闭合循环。|
|bard_run_8.png|prompts/bard_run_8.png-repair.txt|号角较短，整体尺寸位置偏差；8帧未形成严格闭合循环。|
|bard_attack_1.png|prompts/bard_attack_1.png.txt|准备可读，脚底超出980；尺寸位置漂移。|
|bard_attack_2.png|prompts/bard_attack_2.png.txt|手持直管与背后号角分离，未满足整件刚体。|
|bard_attack_3.png|prompts/bard_attack_3.png.txt|同上，头部/尺寸漂移。|
|bard_attack_4.png|prompts/bard_attack_4.png.txt|同上，随挥最高位可读。|
|bard_attack_5.png|prompts/bard_attack_5.png.txt|收势偏侧，未完整恢复设计待机，脚底超出980。|
|bard_skill_1.png|prompts/bard_skill_1.png.txt|举起可读，头/号角/尺寸漂移。|
|bard_skill_2.png|prompts/bard_skill_2.png.txt|蓄力可读，脚底略超出980。|
|bard_skill_3.png|prompts/bard_skill_3.png.txt|手持口与背后弯角分离，未满足整件刚体。|
|bard_skill_4.png|prompts/bard_skill_4.png.txt|同上；近侧/远侧手臂归属不够稳定。|
|bard_skill_5.png|prompts/bard_skill_5.png.txt|收势可读，轮廓比例漂移。|
|bard_skill2_1.png|prompts/bard_skill2_1.png.txt|仍有额外上方弯角，未满足单件乐器。|
|bard_skill2_2.png|prompts/bard_skill2_2.png.txt|抬手可读，脚底超出980。|
|bard_skill2_3.png|prompts/bard_skill2_3.png.txt|高举可读，头和比例漂移。|
|bard_skill2_4.png|prompts/bard_skill2_4.png.txt|仍偏高举，放下动作不够明确。|
|bard_skill2_5.png|prompts/bard_skill2_5.png.txt|收势可读，比例漂移。|
|bard_skill2_e_1.png|prompts/bard_skill2_e_1.png.txt|身前乐器可读，脚底超出980。|
|bard_skill2_e_2.png|prompts/bard_skill2_e_2.png.txt|出现重复/分离弯角，整件刚体未达标，脚底超出980。|
|bard_skill2_e_3.png|prompts/bard_skill2_e_3.png.txt|同上，前倾不足。|
|bard_skill2_e_4.png|prompts/bard_skill2_e_4.png.txt|收势可读，头和号角形状漂移。|
|bard_ult_1.png|prompts/bard_ult_1.png.txt|蓄力可读，脚底超出980；号角形状漂移。|
|bard_ult_2.png|prompts/bard_ult_2.png.txt|举过头可读，头/号角比例漂移。|
|bard_ult_3.png|prompts/bard_ult_3.png.txt|最高位与第2帧变化不足，轮廓漂移。|
|bard_ult_4.png|prompts/bard_ult_4.png.txt|向前下挥可读，位置尺寸漂移。|
|bard_ult_5.png|prompts/bard_ult_5.png.txt|收势可读，整体比例不等同设计。|
|bard_dead_1.png|prompts/bard_dead_1.png.txt|受击可读，头/号角/尺寸漂移。|
|bard_dead_2.png|prompts/bard_dead_2.png.txt|双臂张开且乐器脱手，位置比例漂移。|
|bard_dead_3.png|prompts/bard_dead_3.png-repair.txt|已重新生图修正肩扛错误；坐姿和脱手乐器可读，位置比例漂移。|
|bard_dead_4.png|prompts/bard_dead_4.png.txt|前倒不足，仍偏蹲跪姿；头和号角漂移。|
|bard_dead_5.png|prompts/bard_dead_5.png.txt|倒地可读，仍非严格趴伏，头部朝向保留两个眼孔；位置漂移。|
|bard_dead_6.png|prompts/bard_dead_6.png-repair.txt|已重新生图接近第5帧停留，但不是逐像素相同，仍有小幅位移。|

## 共通限制

没有做到所有帧的同一头部、同一件刚体号角、严格一致身高/位置。普攻和Q推出帧仍将背后弯角与手持直管分离；W第1、E第2–3帧有重复弯角。跑步交叉步和闭合循环不稳定。死亡第4帧前倒不足；第6帧接近第5帧但并非严格静止复制。这些已在逐帧列表标明，没有写成通过。所有组的并排图已目视检查。

本次仅交细稿原样；包内给Claude的读格、贴统一面具、武器补画、游戏数据或入库流程未执行。本说明在所有素材、提示词和验证文件更新后最后写入，随后仅执行ZIP打包验证。
