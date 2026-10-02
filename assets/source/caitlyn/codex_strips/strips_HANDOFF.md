# 凯特琳动作条：全部重画版

旧版输出作废。本包重画 run、attack、passive、skill、skill2、e、ult、hit、dead，共 61 帧；待机 6 帧原文件保持不变，总计 67 帧。

## 文件与播放

导入用根目录的 10 张 caitlyn_*.png。每格 768×768，每个游戏像素是一个严格的 8×8 色块；透明度仅 0/255，只使用定稿的 24 色。图片尺寸、帧数、pivot 和毫秒时长见 manifest.json；caitlyn_cells.json 是参考包原件。Q 第 7 帧、W 第 4 帧、E 第 3 帧、R 第 7 帧、普攻第 3 帧、强化射击第 4 帧出手。preview.html 可暂停并拖动逐帧查看，GIF 用于快速视觉预览；精确时长以 JSON 和 HTML 为准。

## 重画和整理方式

全部 9 条重新生图；W 再修正直立枪长和投掷手臂，强化射击再修低姿态。整个身体和武器使用同一比例缩到游戏网格，保留原稿中的躯干、手臂和屈膝结构。行间分隔从透明空隙定位，避免上一排靴子混入下一排。头从定稿原样复制；以脸和下巴对齐现有身体，帽子向上延伸，避免把躯干挤扁。领巾按定稿的眼睛下方第 5 行定位。受击第 1 帧闭眼；死亡第 2–6 帧用定稿头整体旋转，最后两帧使用倒地原稿的头。移动头部横向相对 pivot 固定、上下起伏 1 格。恢复末帧使用定稿待机，Q 蓄力帧重新整理到正确出手时机。W 保留完整枪身和握枪手，在原有枪管上补足长度与描边。

## 每张实际使用的提示词

| 动作 | 提示词位置 |
|---|---|
| run | generation_prompts.json 的 assets[4] |
| attack | generation_prompts.json 的 assets[5] |
| passive | generation_prompts.json 的 assets[6]；edits[1] |
| skill | generation_prompts.json 的 assets[3] |
| skill2 | generation_prompts.json 的 assets[0]；edits[0] |
| e | generation_prompts.json 的 assets[2] |
| ult | generation_prompts.json 的 assets[7] |
| hit | generation_prompts.json 的 assets[8] |
| dead | generation_prompts.json 的 assets[1] |

generation_prompts.json 保存逐条完整提示词、三张参考图的作用说明和原始生图路径。原始生图路径是本机溯源信息，导入时只读本包根目录 PNG。

## 验证和限制

validation_report.json 记录逐帧文件检查：严格色块、二值透明、色板、定稿头的像素、眼睛蓝色位置、连通性、脚底线、空格透明，以及待机文件哈希一致性。文件检查通过不等于美术已经获得用户认可。

枪身和身体为重新绘制：枪的饰板、镜片、枪托并未做到与定稿逐格相同，除 W 直立枪管整理外，未对每一帧的枪长、手臂全程宽度和手掌尺寸作严格逐格认证。倒地最后两帧按参考包的例外保留重画头。未实际运行导入程序或启动游戏验证动画、枪口挂点、头像截取与选人卡片；这些不能标为通过。导入时保留报告，核对技能出手 tick，观察角色与血条、头像和卡片裁切的实际关系。

本包不含旧版混帧或旧版身体拼接图。
