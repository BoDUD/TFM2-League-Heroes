# 泽丽：只重画脸（给 Codex 的提示词）

> 用户给了自己的一张泽丽（`zeri/3_picture.png`），要在游戏里做成 **40 格高**。我按格子把它还原成了 `zeri/1_design.png`（24 × 40，8 倍放在 1024 画布上）。用户的意见：**「眼睛嘴巴做的不太像泽丽，其他都挺好的」**；给了两张觉得可以的脸（`zeri/5_liked_faces.png`：「做成这样也行啊」）；我照着重画后（`zeri/7_rejected.png` 右边那张）又说 **「你改的脸还是有点诡异啊，让 Codex 帮忙吧」**。
>
> 这一轮**只重画脸**：`1_design.png` 里红框里的格子（40 格图的第 8–15 行、第 7–14 列，8 × 8 格），**红框外面一格都不要改**（发型、发髻、步枪、手、身体都已经通过）。

## 附图（压缩包 `zeri_face_pack.zip` 的 `zeri/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_design.png` | 已通过的整张设计（24 × 40）8 倍，在 1024 × 1024 画布上（鞋底在第 99 行，两脚中间在 x=512）；**红框 = 只允许改的脸部区域** | 位置、大小，红框外照抄 |
| `2_face_box.png` | 头部 24 倍，每格标了行号/列号，红框同上 | 一格一格对位置 |
| `3_picture.png` | 用户自己的泽丽原图 | **长相、神态** |
| `4_picture_face.png` | 原图的脸，盖上同样的 40 格网格（红框同上） | 原图里眼睛、创可贴、嘴落在哪几格 |
| `5_liked_faces.png` | 用户说「做成这样也行」的两张脸 | **画法可以参考：两格眼白 + 深绿瞳孔、粗黑睫毛、斜下的眉尾、白色菱形创可贴、红棕嘴** |
| `6_quality_bar.png` | 用户认可过的英雄的头部（格温、赛娜、萨勒芬妮、金克丝）8 倍 | 像素质量、五官画法 |
| `7_rejected.png` | 我画的两版脸（用户不认可） | **不要画成这样** |
| `design_1x.png` | 设计的 1 倍原图（128 × 128） | 交回前逐像素对比红框外有没有变 |

## 提示词

附图：`zeri/` 里的 1–7 号图，按顺序。

```text
Seven attached images. FIRST: an approved game sprite of Zeri (a lively Zaun street girl with lime hair, two spiky buns and an electric rifle), 24 x 40 squares, shown at 8x on a 1024x1024 canvas (128 x 128 squares); the RED BOX marks her face: rows 8-15 and columns 7-14 of the 24 x 40 figure, which are canvas squares x 60-67, y 68-75 (pixels x 480-543, y 544-607). SECOND: the head at 24x with every square numbered and the same red box. THIRD: the user's own picture of Zeri - her LOOK. FOURTH: that picture's face under the same 40-row grid, showing where her eyes, plaster and mouth fall. FIFTH: two small pixel faces the user said are fine - two white squares of eye white beside a dark-green iris (light green on top, darker below), a thick black lash over the eye that runs past its outer corner, a short black brow stroke slanting down toward the nose, a smaller far eye, a white diamond plaster on the cheek, a 2-3 square red-brown smirk. SIXTH: heads of other heroes of this game at 8x - the quality to match. SEVENTH: two faces drawn before that the user REJECTED ("not like Zeri", "looks weird") - do not repeat them.
Task: redraw ONLY the squares inside the red box so the face looks like Zeri in the THIRD image: confident and cheeky - a big bright eye on the image-left (her near eye) with white on its outer side and a green iris under a heavy black lash, her far eye (image-right) smaller and slightly narrowed, a short slanted brow, the small white plaster on her left cheek (image-left, under the near eye), a small red-brown smirk, a small pointed chin. Keep the face the SAME SIZE as in the FIRST image (skin about 6 squares wide and 7 rows from forehead to chin) and in the same place; the hair, buns, rifle, hand, neck and body outside the red box must stay EXACTLY as they are, square for square.
Pixel art at game size: every square one flat colour, one crisp 8x8 block on the 8-px grid of the canvas, transparency only 0 or 255, no anti-aliasing, no gradients, no dithering; one near-black outline colour #0A0411. Colours: skin #F8AB63, skin shadow #F2854B, white #F4F4F8, iris #318F0A and #9AC850 (or a lime #C2E212), lash/outline #0A0411, dark brown edge #43201C, mouth #A14633 or #8C2020, hair #EAFB4A #A9C907; the face is 3/4 view turned to image-right.
Draw the face square by square at this size (you may sketch bigger first, but the delivered squares must be drawn at game size, not a downscale). Make FOUR different takes (A, B, C, D) on the eyes and the mouth; each is the full canvas with only the red box changed.
Before finishing, check for each take: outside the red box the 1x image is pixel-identical to the given design; the near eye shows white + green clearly at 1x and 2x; the far eye is visible; the plaster and the smirk are there; nothing outside the red box moved.
```

## 交付（`outputs/zeri-face/`）

- `zeri_face_A.png` … `zeri_face_D.png`：1024 × 1024（8 倍），整张图只有红框里变；
- `zeri_face_A_1x.png` … `zeri_face_D_1x.png`：128 × 128（1 倍），鞋底仍在第 99 行；
- `zeri_face_compare.png`：四个方案的脸 12 倍 + 整张 2 倍，旁边放原图的脸；
- `raw/`：生图原稿；`HANDOFF.md`（**最后写**：每个方案改了哪几格、红框外是否逐像素相同）；最好再打一个 `zeri_face_pack.zip`。

## 交回前自查

- [ ] 红框外逐像素和 `design_1x.png` 一样（发型、发髻、枪、手、身体都没动）；
- [ ] 脸没有变大，还在原来的位置；
- [ ] 1 倍、2 倍下看得清：近眼眼白 + 绿瞳 + 粗睫毛，远眼也看得见，创可贴、坏笑的嘴都在；
- [ ] 每格一个颜色、8 × 8 对齐、透明度只有 0/255、描边只有一种近黑；四个方案 A–D；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按格子读回（`regrid.py` 或直接 4/8 采样），确认红框外和 v5 一致，把四个方案的脸和原图、用户喜欢的脸并排给用户挑；选定后写进 `design40/`，再做动作帧。
