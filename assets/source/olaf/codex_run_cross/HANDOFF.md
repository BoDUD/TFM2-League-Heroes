# 奥拉夫交叉步重画稿

内置 imagegen 编辑上半身动作条，按引导图补绘胯、腿、护胫与靴子；未导入游戏。

格式：3584×1536，4×2，8帧×120ms，112×96逻辑格，8倍整数导出；21色、二值透明与脚底线检查。

检查结果：{'size': [3584, 1536], 'frames': 8, 'binary_alpha': True, 'palette_only': True, 'grid8': True, 'below_floor_empty': True, 'upper_exact_pass': False, 'boot_positions_certified': False}

## 逐帧记录

| 帧 | 上半身不同像素数 | 近脚目标中心/底行 | 远脚目标中心/底行 | 靴子候选区域 |
|---|---|---|---|---|
| 1 | 623 | {'center_x': 54, 'sole_row': 81} | {'center_x': 51, 'sole_row': 76} | [{'center_x': 55.5, 'sole_row': 74, 'bbox': [54, 73, 58, 75], 'pixels': 5, 'leg_identity': None}, {'center_x': 63.0, 'sole_row': 76, 'bbox': [59, 73, 68, 77], 'pixels': 29, 'leg_identity': None}, {'center_x': 51.5, 'sole_row': 81, 'bbox': [46, 76, 58, 82], 'pixels': 52, 'leg_identity': None}] |
| 2 | 739 | {'center_x': 51, 'sole_row': 81} | {'center_x': 56, 'sole_row': 77} | [{'center_x': 62.0, 'sole_row': 74, 'bbox': [59, 73, 66, 75], 'pixels': 12, 'leg_identity': None}, {'center_x': 50.5, 'sole_row': 81, 'bbox': [45, 74, 57, 82], 'pixels': 60, 'leg_identity': None}] |
| 3 | 740 | {'center_x': 48, 'sole_row': 81} | {'center_x': 61, 'sole_row': 78} | [{'center_x': 57.5, 'sole_row': 78, 'bbox': [52, 73, 64, 79], 'pixels': 48, 'leg_identity': None}, {'center_x': 48.0, 'sole_row': 81, 'bbox': [43, 74, 54, 82], 'pixels': 59, 'leg_identity': None}] |
| 4 | 717 | {'center_x': 47, 'sole_row': 79} | {'center_x': 62, 'sole_row': 81} | [{'center_x': 43.0, 'sole_row': 78, 'bbox': [40, 73, 47, 79], 'pixels': 29, 'leg_identity': None}, {'center_x': 64.5, 'sole_row': 81, 'bbox': [59, 73, 71, 82], 'pixels': 60, 'leg_identity': None}] |
| 5 | 835 | {'center_x': 46, 'sole_row': 76} | {'center_x': 59, 'sole_row': 81} | [{'center_x': 42.5, 'sole_row': 75, 'bbox': [40, 73, 46, 76], 'pixels': 16, 'leg_identity': None}, {'center_x': 62.5, 'sole_row': 79, 'bbox': [57, 73, 69, 80], 'pixels': 57, 'leg_identity': None}] |
| 6 | 832 | {'center_x': 51, 'sole_row': 77} | {'center_x': 56, 'sole_row': 81} | [{'center_x': 51.0, 'sole_row': 79, 'bbox': [46, 73, 57, 80], 'pixels': 55, 'leg_identity': None}] |
| 7 | 832 | {'center_x': 56, 'sole_row': 78} | {'center_x': 53, 'sole_row': 81} | [{'center_x': 56.0, 'sole_row': 79, 'bbox': [47, 73, 66, 80], 'pixels': 89, 'leg_identity': None}] |
| 8 | 842 | {'center_x': 57, 'sole_row': 81} | {'center_x': 52, 'sole_row': 79} | [{'center_x': 46.5, 'sole_row': 75, 'bbox': [44, 73, 50, 76], 'pixels': 13, 'leg_identity': None}, {'center_x': 63.0, 'sole_row': 79, 'bbox': [58, 73, 69, 80], 'pixels': 52, 'leg_identity': None}] |

## 限制

生图没有精确保留上半身像素，靴子中心、抬脚高度和近远腿身份未通过逐帧验收，不能宣称全部交叉步要求完成。候选区域只是下腿处深色连通区域，不是已确认靴子；目标坐标单独列出，实际近远脚坐标保留为 null。请参考动画与引导图。导出只做色板、格子采样和整帧位置校准，没有脚本拼腿或复制上半身。
