# 烈娜塔最后一步：技能特效素材交付

2026-10-17。24 组特效、共 114 帧已生成并导出。

## 文件与使用方式

- 根目录 `renata_fx_*.png`：24 张8倍最近邻放大的横向精灵条，每张从左到右依次播放。
- `pixel_1x/`：24 张原尺寸 RGBA 精灵条，供切帧导入；每帧尺寸与帧数以 `manifest.json` 为准。
- `raw/`：24 张选用的 image_gen 原始输出，逐字节保留；`raw/iterations/` 另保存子弹、命中、E飞弹的修正前原稿。
- `manifest.json`：每张的 name、file、frames、cell_1x、symmetry，以及绑定、预览倍数、1倍文件路径和目标图表。
- `bindings.json`：新包提供的运行时绑定及显示大小说明。
- `preview.html`：打开即可逐帧播放全部24组，支持暂停和调整预览速度。
- `contact-sheet.png`：全部动画帧的静态总览。
- `generation-prompts.txt`、`repair-prompts.txt`：实际使用的生图与修正提示词。
- `validation.json`：逐帧可见像素数、平均亮度、90%亮度分位、白芯检测及源图分格边界。
- `checks-summary.json`：最终文件校验摘要。
- `processing/normalize_fx.py` 和 `processing/specs.json`：可复现的逐格取色导出脚本与参数，需要 Python、Pillow、NumPy。运行时会重新导出 PNG、manifest、validation；含额外绑定字段的本次最终 manifest 已随包保存。

## 覆盖内容

普攻/被动：a_shot、a_flash、a_hit、p_mark、p_pop。

E：e_missile、e_boom、e_hit、e_slow、e_shield。

Q：q_hand、q_hit、q_fling、q_land、q_crash_hit。

W：w_cast、w_buff、w_save。

R：r_cast、r_wave、r_hit、r_berserk、r_lash、r_lash_hit。

## 生成与规范化

全部特效形状来自内置 image_gen，没有用代码绘制新特效。参考只取自本次 renata_fx_pack；未打包原版贴图参考或以前的模型/走路包图片。

为避免很长的单行图丢帧，生图采用2×2或3×2等紧凑排列，再转换成横向精灵条。原稿可能具有生成器自行改变的尺寸；导入时请使用 `pixel_1x/`，不要按 raw 的大小切格。

规范化步骤：按透明间隙识别原稿的帧分界，去除共同空白边距，规范帧宽高比例；先把颜色归到每条提示词指定的调色板，再逐逻辑格统计。每格先按多数判定透明或不透明，不透明格取出现最多的调色板颜色。对称轴居中后，用对应的镜像格校正严格对称。围身特效清理指定身体留空区域，最深的发光轮廓提升为同调色板较亮档。最后导出1倍图和严格最近邻8倍图。没有使用半透明、柔光或插值缩放来制作最终导入图。

很小的子弹与火星在多数取色后曾丢失，因此追加了 a_shot、a_hit、e_missile 的定向重画；修正稿与初稿均保留。

## 已验证

- 对照清单恰好24个文件，合计114帧，无空帧。
- 每张1倍图均为 `[帧宽×帧数, 帧高]`，单行排列。
- 所有最终像素 alpha 只有0或255。
- a_shot、a_flash、e_missile、q_hand、r_wave 每帧严格上下对称；其他19组每帧严格左右对称。
- 8倍图逐像素等于1倍图的最近邻放大。
- 所有选用原稿与生成器输出的 SHA-256 相同。
- 对全部最终帧进行了静态目视检查；动画预览脚本通过 JavaScript 语法检查。未进行浏览器自动播放实测。

## 导入约定及边界

`cell_1x` 是包含留白的切帧尺寸，不能与 bindings 中的运行时效果显示范围混用。按原提示布局切帧：例如 a_shot 的单格是12×6，显示范围说明是10×4；r_cast 单格64×32，运行时说明64×30。

a_flash 使用角色细格，不进特效表，应由后续制作流程放入她的attack第3、4帧；r_cast、r_wave 归大图表 league_renata_big，其余按manifest和bindings处理。预览的100/150/250毫秒仅用于查看动画，不代表游戏播放参数。

本轮完成特效素材及导入文件准备，没有接入游戏工程、修改技能绑定、合并人物动画、构建或进行游戏内实测。最终挂点、层级、运行时缩放及实际战场观感仍由导入环节验证。多数取色会简化极细碎片，原稿保留供必要时复核。
