# 艾瑞莉娅：只重画脸（给 Codex 的提示词）

> 艾瑞莉娅的游戏造型（`irelia/1_design.png`，22 × 42 格，8 倍放在 1024 画布上）是按你上一轮画的 `irelia-front-B.png`（`irelia/3_picture.png`）一格一格还原出来的。用户的意见：**「修的挺好的」**，但**「眼睛做的精致一点 更像刀妹一点」「嘴巴可以不画」**，要看**英雄联盟里刀妹的眼睛**（`irelia/5_league_face.png`）；我重画的两版眼睛（`irelia/7_rejected.png`）用户说**「眼睛还是太怪」**。
>
> 这一轮**只重画脸**：`1_design.png` 里红框里的格子（42 格图的第 8–14 行、第 9–17 列，9 × 7 格），**红框外面一格都不要改**（飞刃、头发、头顶尖角、身体都在别处处理）。

## 附图（压缩包 `irelia_face_pack.zip` 的 `irelia/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_design.png` | 整张设计（22 × 42）8 倍，在 1024 × 1024 画布上（鞋底在第 99 行）；**红框 = 只允许改的脸部区域** | 位置、大小，红框外照抄 |
| `2_face_box.png` | 头部 24 倍，每格标了行号/列号，红框同上 | 一格一格对位置 |
| `3_picture.png` | 你画的原稿 front-B | 长相、配色 |
| `4_picture_face.png` | 原稿的脸放大 | 脸型、头冠、发际线 |
| `5_league_face.png` | **英雄联盟里刀妹模型的脸** | **眼睛照它画** |
| `6_quality_bar.png` | 用户认可过的英雄的头部（格温、萨勒芬妮、辛德拉、泽丽、霞）8 倍 | 像素质量、五官画法 |
| `7_rejected.png` | 我画的两版脸（用户说眼睛太怪） | **不要画成这样** |
| `design_1x.png` | 设计的 1 倍原图（128 × 128） | 交回前逐像素对比红框外有没有变 |

## 刀妹的眼睛（照 `5_league_face.png`）

- 杏仁形、眼尾上挑的**凤眼**，冷静坚定；
- **上眼线又黑又粗**，在眼尾拉出一点上翘的尖；下眼线细、只到眼睛中间；
- **青蓝色（偏青绿）的大虹膜**：外圈深、里面亮，一格小白高光，瞳孔深色；眼白只在眼角露一点；
- **眉毛深蓝、粗，眉峰明显、往鼻梁方向压低**，和眼睛之间留一点皮肤；
- 3/4 侧脸朝画面右：近眼（画面左）完整，远眼（画面右）稍窄；
- **不画嘴**（用户：「嘴巴可以不画」）；鼻子最多一格阴影。

## 提示词

附图：`irelia/` 里的 1–7 号图，按顺序。

```text
Seven attached images. FIRST: a game sprite of Irelia (a calm, resolute Ionian warrior woman: long dark indigo-blue hair, a silver tiara with a V point on her forehead, a crimson crest on her head, crimson-and-silver armour, a bundle of floating blades behind her back), 22 x 42 squares, shown at 8x on a 1024x1024 canvas (128 x 128 squares); the RED BOX marks her face: rows 8-14 and columns 9-17 of the 22 x 42 figure, which are canvas squares x 59-67, y 66-72 (pixels x 472-543, y 528-583). SECOND: the head at 24x with every square numbered and the same red box. THIRD: the bigger picture this sprite was made from - her look. FOURTH: that picture's face, big. FIFTH: her face on her in-game 3D model - COPY ITS EYES. SIXTH: heads of other heroes of this game at 8x - the quality to match. SEVENTH: two faces drawn before that the user REJECTED ("the eyes look weird") - do not repeat them.
Task: redraw ONLY the squares inside the red box so her face looks like Irelia in the FIFTH image: sharp almond eyes with lifted outer corners, a thick black upper lash line that ends in a small upward wing at the outer corner, a thin lower lash line, big CYAN-TEAL irises (darker rim, brighter inside, a one-square white glint, a dark pupil), only a little eye white at the corners; thick dark-indigo eyebrows with a clear angle, pressed down toward the nose, with a little skin between brow and eye; a calm, determined, slightly stern look; the near eye (image-left) whole, the far eye (image-right) a little narrower (3/4 view turned to image-right). NO MOUTH (the user asked to leave it out); at most one square of nose shadow. Keep the silver tiara's V point on the forehead, the hairline and the fringe as they are, the face the SAME SIZE and in the SAME PLACE (skin about 7 squares wide); everything outside the red box must stay EXACTLY as it is, square for square.
Pixel art at game size: every square one flat colour, one crisp 8x8 block on the 8-px grid of the canvas, transparency only 0 or 255, no anti-aliasing, no gradients, no dithering; one near-black outline colour #0B021E. Colours from the sprite: skin #FED4B2, skin shade #FEB78B #FEA475 #D97B5B, eyes #1FE3FD #00B8E9 #008EE9 #8ED7F1, white #F4F4F8, brows/hair #191848 #232466 #2E2F84 #2E32B2 #4048D8, tiara #F4F4F8 #C7CBDE #A9AEC8, outline #0B021E.
Draw the face square by square at this size (you may sketch bigger first, but the delivered squares must be drawn at game size, not a downscale). Make FOUR different takes (A, B, C, D) on the eyes; each is the full canvas with only the red box changed.
Before finishing, check for each take: outside the red box the 1x image is pixel-identical to the given design; both eyes read clearly as Irelia's cyan eyes at 1x and 2x; no mouth; nothing outside the red box moved.
```

## 交付（`outputs/irelia-face/`）

- `irelia_face_A.png` … `irelia_face_D.png`：1024 × 1024（8 倍），整张图只有红框里变；
- `irelia_face_A_1x.png` … `irelia_face_D_1x.png`：128 × 128（1 倍），鞋底仍在第 99 行；
- `irelia_face_compare.png`：四个方案的脸 12 倍 + 整张 2 倍，旁边放英雄联盟的脸；
- `raw/`：生图原稿；`HANDOFF.md`（**最后写**：每个方案改了哪几格、红框外是否逐像素相同）；最好再打一个 `irelia_face_pack.zip`。

## 交回前自查

- [ ] 红框外逐像素和 `design_1x.png` 一样；脸没有变大，还在原来的位置；
- [ ] 1 倍、2 倍下看得清：青蓝色的凤眼、黑粗上眼线带眼尾、深蓝斜眉；不画嘴；
- [ ] 每格一个颜色、8 × 8 对齐、透明度只有 0/255、描边只有一种近黑；四个方案 A–D；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读回 1 倍图，确认红框外和设计一致，把红框里的格子写回 `design42/irelia42.txt`（我这边对红框外的修改保留），四个方案和英雄联盟的脸并排给用户挑；选定后做侧身版和动作帧。
