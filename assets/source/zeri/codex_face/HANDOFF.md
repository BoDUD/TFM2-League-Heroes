# 泽丽脸部像素重画

日期：2026-10-11。输入：zeri_face_pack.zip。只处理脸部，没有改动仓库或已有动作资源。

主版：zeri_face.png / zeri_face_1x.png，与 A 方案相同。A–D 四版保留供比较；A 为亮绿近眼和较重睫毛，B 睫毛稍轻、嘴角较深，C 绿瞳更深、嘴形更收敛，D 远眼更窄且下巴阴影略重。

## 精确限制

四版均仅在原画布 x=60–67、y=68–75 的 8×8 格中修改。A 修改 12 格，B 修改 13 格，C 修改 11 格，D 修改 13 格。每一格修改前后的 RGBA 以及画布坐标、人物坐标见 pixel-changes.json。

框外与输入 design_1x.png 逐像素完全相同，包括发型、发髻、武器、双手、颈部、衣服和腿。原尺寸画布保持 128×128，放大图为 1024×1024，每像素严格重复成 8×8 纯色块，透明度只有 0 / 255，鞋底仍在第 99 行。

脸按原尺寸逐格绘制，没有将大图缩小到脸框。保留原有暖肤色、白色和唯一近黑色 #0A0411，使用深绿 #318F0A、浅绿 #9AC850、红棕嘴色 #A14633，并在部分方案采用 #8C2020。眼白、绿瞳、睫毛、脸颊白贴和嘴形都在框内。

## 文件

- zeri_face.png、zeri_face_1x.png：主版。
- zeri_face_A.png 至 zeri_face_D.png：四张完整放大图。
- zeri_face_A_1x.png 至 zeri_face_D_1x.png：原尺寸图。
- zeri_face_A_detail.png：主版紧凑全身预览。
- zeri_face_compare.png：四版头部 12 倍预览和完整 2 倍图。
- zeri_face_compare_with_reference.png：另附用户喜欢的脸部参考。
- palette-main.hex：主版全图实际色板。
- pixel-changes.json：精确变更清单、方案像素行。
- draw_zeri_faces.py：逐格绘制与校验脚本。
- raw/approved_design_1x.png、raw/pixel-maps.json：原始定稿和像素草图。本轮没有调用生图工具，所以没有生图原稿。

技术校验确认了修改范围、网格、透明度和位置。神态是否达到用户期望仍属视觉评价，没有将“完美”当作已证实结论，也未宣称通过游戏显示验收。
