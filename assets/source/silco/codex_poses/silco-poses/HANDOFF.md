# 希尔科动作包交付

15 张动作均已通过内置 image_gen 绘制，沿用输入包的定稿像素造型。最终 PNG 为 1254×1254、RGBA、alpha 仅 0/255，最低不透明像素位于 y=1176。处理仅清理透明杂点并平移底线，没有用代码绘制人物。

## 文件清单
- silco-pose-a_wind.png
- silco-pose-a_throw.png
- silco-pose-a_back.png
- silco-pose-q_wind.png
- silco-pose-q_throw.png
- silco-pose-e_show.png
- silco-pose-e_toss.png
- silco-pose-r_raise.png
- silco-pose-r_throw.png
- silco-pose-run1.png
- silco-pose-run2.png
- silco-pose-run3.png
- silco-pose-run4.png
- silco-pose-d_fall.png
- silco-pose-d_down.png

- raw/：15 张最初原稿及 a_back、q_throw、r_throw 的生图纠正稿，原始像素完整保留。最终三张采用 corrected 版本。
- pose-overview.png：15 姿势总览。
- generation-prompts.txt：实际使用的提示词与参考文件。
- manifest.json：尺寸、alpha、边界和工程检查状态。
- QA.json、SHA256SUMS.json：文件级检查和校验值。

## 视觉检查与尚需校准

已检查完整身体、手杖、服装、橙红伤疤眼和动作可辨识性；已修正普攻收势手中残留药剂、Q/R 投掷后手中残留储罐。Q/R 的弹道道具在特效包中单独提供。

本次完整交付的是生成动作素材，**并非骨架逐像素匹配的最终游戏帧**。生图未严格保持 13px 固定网格；头部不是每帧逐格复制，头脸倾斜、头身比例和四肢位置与参考存在偏差。走路帧仍沿用举药剂的空闲手，而原生走路参考的空闲手下垂；腰间药剂管数量也不保证每帧一致。死亡图的头随身体低垂。上述项目没有被文件检查判为通过。

导入时应从 raw/ 按实际像素密度回读，统一头部、手臂长度和步态锚点，再验收循环。脚底 y=1176 的处理是整图平移，包含漂浮道具时以最低可见点为准。未修改原仓库、游戏安装目录、动作表或配置，也未执行游戏内验证。
