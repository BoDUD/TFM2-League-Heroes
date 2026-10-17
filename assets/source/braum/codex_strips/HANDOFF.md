# 布隆动作帧交付

本包是 38 帧生成动作素材与标准化导出，尚未达到原稿头部、盾牌逐格复制的最终验收要求。未修改游戏、DLL、仓库或安装目录。

## 文件

- 根目录：38 张 `braum_<动作>_<n>.png`，1536×1024，透明背景；对应 38 张 `_1x.png`，256×170。
- `strips/`：7 个动作的 1 倍横向动作条。
- `previews/`：7 个动作 GIF 和全帧总览。
- `raw/`：内置 imagegen 输出的原始图，不重采样。生成工具并未遵守提示中的统一画布尺寸，导出流程按实际尺寸取帧。
- `cells.json`：沿用输入包的帧序与时长。
- `records/manifest.json`：每帧对应原图、裁切范围、导出比例、最终包围盒与时长。
- `records/validation.json`：帧数、尺寸、透明通道、48 色、网格和脚底线检查结果。
- `records/pack_braum.py`、`records/braum_sheets.json`：可复现导出流程；运行前需调整其中的源路径。

## 生成提示词与帧对应

使用内置 imagegen。所有动作均以输入包 `design/braum_design.png` 为模型参考，初轮部分附 `braum_design_on_canvas.png`。没有沿用包内 DLL 构建或安装指令。下面记录各原图的提示主题与顺序；完整英文调用文字保留于本次聊天工具记录。每张输出帧的来源由 manifest 精确对应。

| 输出 | 原图/提示主题 | 姿势顺序 |
|---|---|---|
| run 1–8 | run_generated.png；8-frame run loop, 4 columns × 2 rows, generous padding, same model, upright shield on image right | 左右交替迈步、过腿、腾空、落脚 |
| attack 1–5 | attack_generated.png；shield bash, 3 columns × 2 rows, last cell empty | 后收、蓄力举拳、前冲、压盾命中、回位 |
| skill 1–5 | skill_generated.png；Winter's Bite Q without ice | 扭身收盾、前摆、推出、保持、回位 |
| skill2 1–3 | skill2_generated.png；Unbreakable E, top three cells | 提盾、双手架盾、撑住 |
| w_leap 1–5 | w_leap_generated.png；W leap five poses, followed by remove background/halo edit | 下蹲、起跳、收腿腾空、屈膝落地、站起 |
| ult 1–6 | ult_generated.png；R shield slam six poses, followed by correction: ram-head rotates sideways with shield | 抓盾、过顶、跳起、下砸、深蹲、起身 |
| dead 1–6 | dead_generated.png；death six poses, head left, shield right, final supine | 踉跄、后仰、倒下、着地、仰躺、保持 |

共同要求：same approved bald moustached tattooed Braum; cream fur blue pauldron; dark trousers furry blue boots; ornate gold/dark-slate ram door shield, cyan eyes/gem; image-right shield; flat chunky pixel art; transparent; no poro, effects, text, grid, shadows or glow; consistent actor/weapon scale.

## 导出与已验证项

按目标像素覆盖区域的颜色多数票取样，映射回原稿 48 色；不以中心点采样。透明通道收为 0/255。大图用 6×6 整数像素块展开，底部补 4 行透明像素；因此 `_1x` 完整对应大图上方 1020 行。脚底界限为 y=978，以下全透明。跳跃帧有意离开地面。GIF 使用 cells.json 时长；GIF 格式会以 10ms 精度记录，例如 115ms 显示为 110ms。PNG/manifest 中保留原时长。

## 未达到的要求

- 头部与盾牌是生成模型重绘，**不是原稿逐格复制**。虽然沿用造型，胡须、脸、纹身、羊头与横梁细节仍有漂移。
- 盾牌未实现全帧严格同尺寸刚体。R/死亡横盾已经侧转羊头，但横纵比例仍被生成模型压扁；不能作为“92×64 格严格旋转”的合格证据。
- 不同动作的角色尺度有差异，尤其 R；脚底与画布一致并不等于头、盾、身体尺寸一致。
- 后续动作条没有逐帧附上一帧，也没有逐帧附对应 3D 骨架，因此姿势仅近似参考动作，**未证明骨架逐帧对位**。
- run 并非严格可验证的八相位步态，接环和脚滑仍需动画审阅。attack 的举拳有额外上摆，Q 的后摆幅度不足；E 头部暴露更多；W 手部与盾联系不够自然；dead 5/6 存在细微差异，最后保持帧未逐格锁定。
- 原稿轮廓和模型比例需要进一步逐帧精修；未进行游戏尺寸、地形遮挡、HUD 或实际对战验证。

因此：**38 帧、文件与预览齐全，格式检查通过；模型严格一致性与游戏验收未通过，不应直接标记最终完成或覆盖正式资产。**
