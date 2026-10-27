# 麦迪动作姿势包

交付日期：2026-10-27。绘图工具：内置 image_gen.imagegen。

## 交付清单

15 张独立动作图：

- `maddie-pose-a_aim.png`、`maddie-pose-a_fire.png`、`maddie-pose-a_kick.png`、`maddie-pose-a_back.png`
- `maddie-pose-q_crouch.png`、`maddie-pose-q_fire.png`
- `maddie-pose-e_point.png`
- `maddie-pose-r_aim.png`、`maddie-pose-r_fire.png`
- `maddie-pose-run1.png` 至 `maddie-pose-run4.png`
- `maddie-pose-d_fall.png`、`maddie-pose-d_down.png`

另附 `raw/` 原始生成图与被替换初稿、`pixel_grid/` 逻辑格版本、`contact-sheet.png` 总览、`generation-prompts.txt` 实际提示词、`manifest.json` 和 `qa.json`。

## 制作与验证

以输入包的定稿、头部、动作渲染和骨架为参考逐张生成，没有用代码绘制人物替身。通缉指向首稿误画成端枪，已重画为扛枪并伸手指向；跑步 2、3 也做了针对性重画。所有原始输出均保留。

交付图在生成完成后作像素导出：按格内多数颜色读取、映射至定稿取出的调色板、清理半透明边缘、以最近邻放大。少量靠边的整体轮廓缩入安全边距，未添加枪火、子弹或技能特效。

15 张均实测为 1254×1254 RGBA，透明度仅为 0/255，每个 18×18 块内颜色完全一致，网格原点为左上角。尺寸、硬透明、网格、非空和基线检查记录于 `qa.json`。

## 坐标说明与导入边界

输入规格同时要求“左上角起 18 px 网格”和“脚底 y=1176”。1176 不是 18 的整数倍，二者无法同时精确满足。交付选择完整网格，最低有效像素下边界统一为 **y=1170**，比指定基线高 6 px。需要严格对齐原骨架时，应在导入后的角色锚点补偿 6 px；不要把本包描述为已精确满足 y=1176。

人物是生成式动作源稿。头部朝向与角色身份做了视觉检查，但未声称每张头部与 `1_head.png` 逐像素一致；手臂长度、枪长和骨架位置也没有通过逐关节误差验收。它们应在最终游戏尺寸导入时与已批准 idle 逐帧对齐。`pixel_grid/` 是 70×70 的逻辑缓冲，18 倍后裁成 1254×1254；以根目录 PNG 为主要交付文件。

这次只交付动作素材，没有改仓库、安装游戏资源、编排游戏动作时长或运行实机测试。
