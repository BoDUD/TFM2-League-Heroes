# 九尾妖狐 阿狸：尾巴第二次返修（给 Codex 的返修包）

> 用户（2026-10-01）："狐狸新模型的尾巴又太小 导致比赛内的尾巴特征不明显 尤其是比赛的时候 尾巴几乎被身体完全遮挡"。
> Claude 先用程序把你上一轮的尾巴放大、重新摆了位置，用户看了说"尾巴和屁股那里感觉有点脱节"，最后定下："狐狸做的不行 写好提示词让 codex 帮忙吧"。
> **这一轮还是只画尾巴**，身体逐格不动。

## 现在的问题

- 上一轮（`TAILS_REDO.md`）按英雄联盟原版把尾巴收成待机时约 20×22 格的一束；跑步、普攻、技能这些帧照原版的遮挡，尾巴缩到 8×9 格左右、藏在头发后面。
- 比赛里她大部分时间在跑、在打，所以几乎看不到尾巴：见 `card/now_match_size_2x.png`（接近比赛里的大小），第 2 行起几乎没有白色。
- 尾巴要从后腰长出来。Claude 的程序版把尾巴根放在了头发下沿，尾巴和屁股之间露出一道地面，看起来是"脱节"的。

## 要的样子

- **每一帧都看得见尾巴**：这是阿狸最重要的特征。原版里被身体挡住的帧，这次也要让尾巴从身后露出来，这一条优先于"照原版遮挡"。
- **尾巴从后腰（屁股上方）长出来**：每帧 guide 里的红点就是尾巴根，根部藏在身体后面；尾巴和屁股、后腰连在一起，中间不能露出地面。
- **大小**：待机时整束约 24–26 格宽、26–28 格高（比现在的 20×22 大一圈）。看得见 5–6 条（九条互相叠着），每条都是蓬松的大毛尾，有体积；白色为主，尾尖淡紫，阴影在下沿。
- **范围**：尾尖在腰和狐耳尖之间（最多高出狐耳尖 2 格）；膝盖以下不要有尾巴，绝不碰脚底线；身前（她朝右，右边）不要有尾巴；头顶正上方不要有。
- **每帧单独画**，尾巴跟着动作自然摆动，尾尖比尾根慢半拍。不要把同一束尾巴整体旋转、复制到每一帧（程序版就是这样，显得死板）。
  - 待机：往后上方张开的半扇形；6 帧用同一张（待机是定稿的一帧）。
  - 跑步：收拢，拖在身后，朝左略向上飘，随步子轻轻上下摆；至少一半露在身体和头发外面。
  - 普攻、Q（skill）、E（skill2）：随身体甩动，出手那一帧往后扬。
  - R（ult）：第 2–7 帧冲刺时拉成一束，水平拖在身后；第 1、8、9 帧同普攻。
  - 受击（hit）：往后扬。
  - 死亡（dead）：倒下时尾巴跟着落下；最后两帧趴在地上，尾巴搭在她的背和腿上，不要竖着立起来。
- `guide/tails_guide_<动作>.png` 里每帧：身体原样，**红点＝尾巴根，绿箭头＝尾巴大致的朝向，橙色＝尾巴大致可以占的范围**。橙色来自 Claude 被否的程序版，只用来看位置和大小，画法不要照它。

## 规则

- 只画尾巴。`body/ahri_<动作>.png` 是去掉尾巴的身体，身体的每一格（头、脸、眼睛、头发、狐耳、衣服、皮肤、腿）都不动。尾巴画在身体后面，身体盖在尾巴上；尾巴和身体之间保留一格黑边。
- 格子和排版完全照 `now/`：每帧 72×64 格（8 倍图一帧 576×512），帧数、顺序、每帧的位置不变，站位点见 `ahri_cells.json`。脚底线是站位点下 11 行，线下不能有像素。
- 8×8 方块、硬边、没有抗锯齿，透明度只有 0/255。
- 颜色只用这 6 种（`palette.png`）：`#F9F4FC`（毛色白）、`#CFCEFD`、`#BCBCFC`、`#B6B6FD`（淡紫阴影和尾尖）、`#B8B6CA`（灰紫暗部）、描边 `#06010C`（一格黑边）。
- 尾巴内部的分隔线不要多：几条尾巴之间用一格描边或暗部分开就够，不要画成羽毛扇或翅膀。
- 画风参考 `ref/tail_bundle_round1.png`（上一轮你画的尾束：蓬松、白、尾尖淡紫）：这次画得更大、更蓬，而且每帧按动作重画。
- 选人卡片：待机放大 2.2 倍放在 `#18161E` 黑底上（现在的样子见 `card/card_now_2.2x.png`），不能显得杂乱，不能拖地。

```text
Pixel art sprite REVISION for a small tactics game: chunky 8x8 squares, hard edges, no anti-aliasing, a 1-square dark outline #06010C. Character: Ahri, a fox-girl mage (long black hair, fox ears, red-and-white outfit) facing right. Redraw ONLY her fox tails in every frame of the attached strips. The body (the body/ strips: head, face, eyes, hair, ears, outfit, skin, legs, pose and position in the cell) stays exactly as it is, square for square, and covers the tails. The tails are her signature: they must be clearly visible in EVERY frame at match size, including the run, the attacks and the spells where League hides them behind her body - here they always show behind her. They grow from her lower back just above the hips (the red dot in each guide frame), joined to the body with no gap of background between the tail root and her hips. In the idle the bundle is about 24-26 squares wide and 26-28 squares tall: 5 to 6 big fluffy white fox tails visible (the nine overlap), each with volume, mostly white #F9F4FC with pale lavender tips and lower-edge shade (#CFCEFD, #BCBCFC, #B6B6FD, darkest #B8B6CA), a single-square #06010C outline around the tails and between body and tails, few inner lines (not a feather fan, not wings). The tips stay between her waist and at most 2 squares above her ear tips; nothing below her knees, nothing touching the ground line, nothing in front of her body (the right side), nothing straight above her head. Draw every frame on its own so the tails move with the action, the tips lagging behind the root: idle - a half-open fan back and up; run - gathered and streaming back to the left, slightly up, bobbing with the steps, at least half of them showing; attacks and spells - swinging with the body; the dash (ult frames 2-7) - stretched into one bundle trailing straight back; hit - flung back; death - falling with her, draped over her back and legs when she lies on the ground (not standing up). Same cell grid, frame count and order as the attached strips (72x64 squares per frame), transparent background, binary alpha.
```

## 交付

- `ahri_<动作>.png`（8 倍）和 `ahri_<动作>_1x.png`（1 倍），8 个动作：idle、run、attack、skill、skill2、ult、hit、dead，文件名、排版同 `now/`。
- `tail_layers/ahri_<动作>_tails_1x.png`：只有尾巴的图层（检查用）。
- 两张检查图：①待机放大 2.2 倍放在 `#18161E` 黑底上；②所有帧放大 2 倍放在橄榄绿地面 `#5D634E` 上（比赛里的样子），每帧都要看得见尾巴。
- `HANDOFF.md`：每个动作改了哪些帧、每帧尾巴大约露出多少、有没有没做到的地方；`manifest.json`（每帧的格子位置）。

## 附件

| 文件 | 内容 |
|---|---|
| `now/ahri_<动作>.png`、`now/ahri_<动作>_1x.png` | 现在的 8 条动作条（8 倍 / 1 倍，上一轮你交的） |
| `body/ahri_<动作>.png`、`body/ahri_<动作>_1x.png` | 同样的帧去掉了尾巴（你上一轮的尾巴图层逐格拿掉，被尾巴盖住的身体边补回描边）：在这上面画 |
| `guide/tails_guide_<动作>.png` | 每帧 4 倍：身体、尾巴根（红点）、尾巴朝向（绿箭头）、尾巴大致范围（橙色），绿线是脚底线 |
| `card/now_match_size_2x.png` | 现在所有帧在比赛大小下的样子（问题所在） |
| `card/card_now_2.2x.png` | 现在的待机在选人卡片上的样子 |
| `ref/tail_bundle_round1.png` | 上一轮你画的尾束（画风参考） |
| `ref/ahri_design.png` | 定稿（待机一帧，8 倍） |
| `palette.png` | 尾巴的 6 种颜色 |
| `ahri_cells.json` | 每帧的站位点（格子坐标） |
