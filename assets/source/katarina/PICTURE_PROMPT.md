# 卡特琳娜（不祥之刃）：先画像素风原图（第 0 步，给 Codex 的提示词）

> 卡特琳娜是一个**冷酷自信的诺克萨斯女刺客**，双手各握一把弯刃匕首。这一步请 Codex 照同一段提示词画**两版**全身像素风原图（**K1、K2**，同一个人、同样的长相、衣服、颜色、格子大小，让我挑一张），姿势是英雄联盟的待机（附图 1、9）：**近侧手（画面左边）把一把匕首举在脸前、刀刃横在胸前朝右；远侧手（画面右边）把另一把匕首低低地伸向前方、弯刃朝下**，两腿大步分开、微微下蹲。之后第 1 步再按选中的画正面 + 侧面的造型。这一版每个游戏像素约 **1.5 格**（附图 10–13 是本包同样密度的加里奥、布隆、泽丽、奈德丽）：像素块清楚、整齐、大小一致，描边约 **2 格**，身材**偏 Q 版**。你画的原图会直接按格子读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–8）。
> - **头**（附图 3 特写）：一个漂亮、冷峻的年轻女人，头约占身高的**四分之一到三分之一**（Q 版）；**很长的直发，鲜艳的深红色**（亮部偏红橙、暗部酒红），侧分，一缕刘海斜着垂过额头一边，后面的长发披到腰下、飘在她身后（画面左边）；**白皙的皮肤**；**两只绿色的眼睛看得清**；**一只眼睛上有一道细细的竖疤**（从眉毛穿过眼睛到脸颊，附图 3）；**冷静自信的浅笑**；**脸朝右前方平视**。
> - **衣服**（附图 1、2、4、8）：**深炭黑的皮甲上衣**（胸前一片深灰钢色的甲片，带细的银色纹路），**露出腰腹**；肩上**深灰钢色的小肩甲，带几根短尖刺**；**深灰的短袖**；前臂上**银灰色的护腕，带尖刺**；**黑色手套**；胯上**两条交叉的棕色皮带**（银扣），腰后垂下**一条暗红色的布条**；**黑色紧身皮裤**，大腿外侧各有一片**银色的刃形装饰**；小腿上**银灰色的钢护胫**（膝盖处一圈），**黑色靴子**；**背后斜插着几把匕首**，从肩膀后面露出**棕色刀柄 + 银色柄头**（附图 1、4）。
> - **匕首**（附图 8 特写）：两把**弯刃匕首**，**银白色的刀身**带一点浅蓝灰的暗部和刻纹，**深色刀柄**；刀身清楚、亮、至少 2 格粗，**刀刃轮廓要连续、笔直地沿着弧线走**，不碎。近侧那把**不能挡住她的脸**。
> - **姿势**：3/4 正面朝右（脸朝右前方，胸口朝向看画的人），英雄联盟待机（附图 1）：两腿大步分开、膝盖微弯，**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗**，两只靴底落在同一条地面线上。
> - **比例**：**偏 Q 版、利落**——头大一点，腰细但不细长，腿不要太长；风格完全照附图 10–13；**不要细长的写实比例**。
> - **画布用竖版 1024×1536**：**她从头发顶到鞋底约 684 px，也就是约 57 格**，鞋底在离画布底边约 196 px 的地方（附图 9 的深灰线；浅灰线是头顶），匕首全部在画面里。
> - **像素块**：大小一致的方块，**每块 12 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个像素）；**外轮廓一圈 2 块宽的近黑描边**；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。红发要分出 3–4 档清楚的红（亮红、正红、深红、酒红），**不要和黑色皮甲混成一团**；暗色衣服要有亮的边缘高光，看得出甲片和皮带的形状。
> - 不画任何特效（刀光、红色残影、旋转的刀圈、匕首落地都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/katarina-picture/katarina-K1.png`、`katarina-K2.png`（1024×1536 竖版，**真透明背景**）；原始生成图原样放进 `outputs/katarina-picture/raw/`；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/katarina_picture_done.zip`。

## 附图（压缩包 `katarina_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_katarina_front.png` | 英雄联盟原版卡特琳娜待机，3/4 朝右 | 颜色、形状、**角度**、姿势 |
| `refs/2_katarina_frontal.png` | 同一帧，几乎正面 | 上衣、肩甲、皮带、护胫怎么做 |
| `refs/3_katarina_head.png` | 头部特写 | 红色长发、绿眼、**眼上的竖疤**、浅笑 |
| `refs/4_katarina_back.png` | 同一帧的背后 | 长发背面、背后斜插的匕首、腰后的暗红布条 |
| `refs/5_katarina_splash.png` | 官方加载画面 | 气质（冷酷自信）、匕首的样子 |
| `refs/6_katarina_actions.png` | 普攻、弹射之刃、伺机待发、瞬步、死亡莲华、跑动（侧面） | 第 2 步用（这一步不画） |
| `refs/7_katarina_side.png` | 待机的侧面（朝右） | 第 1 步用（这一步不用） |
| `refs/8_katarina_upper.png` | 上半身 + 匕首特写 | 弯刃匕首、肩甲尖刺、护腕、背后刀柄 |
| `refs/9_layout.png` | 布局示意（模型剪贴，只看位置和大小） | 竖版画布上人和匕首的位置、鞋底线（深灰）、头顶线（浅灰） |
| `style/10_style_galio.png` | 本包同样密度（每游戏像素 1.5 格）的加里奥待机（8 倍放大，一格 = 一个像素） | **只看风格**：像素粗细、描边、比例、头的大小 |
| `style/11_style_braum.png` | 同样密度的布隆（8 倍） | **只看风格** |
| `style/12_style_zeri.png` | 同样密度的泽丽（8 倍） | **只看风格**（女性角色的比例） |
| `style/13_style_nidalee.png` | 同样密度的奈德丽（8 倍） | **只看风格**（女性角色的比例） |

## 提示词：`katarina-K1.png` / `K2.png`（同一段提示词画两版）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-8 are 3D renders and art of a character from the game: a cold, confident young woman assassin with two curved daggers (1 her idle in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 2 the same nearly from the front: the armoured top, the shoulder guards, the belts, the greaves; 3 her head close-up: the long red hair, the green eyes, the thin vertical scar over one eye, the faint smile; 4 the same from behind: the hair, the dagger hilts on her back, the dark red cloth strip; 5 the official illustration: her mood and her daggers; 6 moments of her actions from the side - not drawn here; 7 her idle from the side - not used here; 8 a close-up of her upper body and the daggers). Image 9 is THIS picture's layout guide: where she and the daggers go on the canvas, the dark grey line is the ground, the light grey line the top of her hair. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi-ish proportions and head size.
Create ONE pixel-art picture of the woman, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha). She is about 684 px (about 57 squares) from the top of her hair to the soles of her boots, the soles about 196 px above the bottom edge (the dark grey line of image 9); both daggers whole inside the picture, comfortable transparent margins, nothing cut off; both soles level on one ground line.
THE WOMAN: THE HEAD, a little big (chibi-ish, about a quarter to a third of her height): very long straight hair of vivid CRIMSON RED (light parts red-orange, dark parts wine red), parted on the side, one lock falling across one side of the forehead, the long hair flowing down behind her back past her waist (on the image left); fair skin; TWO GREEN EYES clearly readable; a thin VERTICAL SCAR running through one eyebrow and eye down to the cheek; a calm confident faint smile; the face turned to the front-right, looking straight ahead. THE CLOTHES: a dark charcoal-black leather armoured top with a dark steel-grey chest plate with thin silver lines, the midriff bare; small dark steel shoulder guards with a few short spikes; dark grey short sleeves; silver-grey spiked bracers on the forearms; black gloves; two crossed BROWN leather belts on the hips with silver buckles, a DARK RED cloth strip hanging behind; tight black leather trousers with a silver blade-shaped ornament on the outside of each thigh; SILVER-GREY steel greaves on the shins with a ring at the knee over BLACK boots; several daggers sheathed diagonally on her back, their BROWN hilts with silver pommels showing over her shoulders.
THE DAGGERS: two CURVED daggers, bright SILVER-WHITE blades with a little light blue-grey shading and engraved lines, dark hilts; each blade at least 2 squares thick, its outline a clean continuous curve, never broken into specks.
THE POSE: her idle (image 1), 3/4 view facing right (face to the front-right, chest toward the viewer): the NEAR hand (image left) holds one dagger up in front of her face-level shoulder, the blade lying across her chest pointing right - it must NOT cover her face; the FAR hand (image right) holds the other dagger low and forward, its curved blade pointing down. Feet wide apart, knees a little bent: the NEAR leg on the image LEFT in full tone, the FAR leg on the image RIGHT a step darker; both soles on one ground line.
PROPORTIONS: chibi-ish and agile like images 10-13 - a slightly big head, a slim waist but not slender, short legs; NOT realistic long proportions.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and the daggers; inside it every material in its own 3-4 flat shades, no stray single odd squares: the hair in 3-4 clear reds (bright red, red, deep red, wine) kept apart from the black leather, the skin fair, the eyes green, the leather black with lighter grey edge highlights so the plates and belts read, the steel grey, the belts brown, the cloth dark red, the blades silver-white; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no blade trails, no red afterimages, no spinning blades, no glow), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底）；1024×1536 竖版；四周留边，人物和两把匕首完整，不出画。
- 头：深红色长直发（3–4 档红，和黑色皮甲分得开）、侧分刘海、长发披在身后；白皙皮肤；**两只绿眼睛看得清**；**一只眼睛上的细竖疤**；冷静浅笑；**平视前方**；头约占身高四分之一到三分之一。
- 衣服：炭黑皮甲上衣 + 钢灰胸甲、露腰、带尖刺的小肩甲、灰短袖、带尖刺的银灰护腕、黑手套、交叉的棕皮带、腰后暗红布条、黑皮裤 + 大腿银色刃饰、银灰护胫、黑靴、背后露出几把匕首的棕柄银头。
- 匕首：两把弯刃、银白刀身、深色刀柄、至少 2 格粗、轮廓连续不碎；近侧那把横在胸前**不挡脸**，远侧那把低低朝前、刀刃朝下。
- 从发顶到鞋底约 684 px（约 57 格）；偏 Q 版（像附图 10–13），不是细长的写实比例。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗；鞋底在同一条水平线上；没有任何特效。
- **每块 12 像素、大小一致、对齐网格**；2 块宽的近黑外描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两版都画完后最后写 `outputs/katarina-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/katarina_picture_done.zip`，这样我这边知道已经交付完了。中间不要停，两版都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/katarina/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 12 px），按它自己的格子读回（`tools/art/design_jayce_cut.py` 的办法），和同位置英雄（中单：泰隆、劫、阿卡丽、卡萨丁）并排给用户挑 K1 / K2 和大小、密度（选的是 PPU 1.5，约 38 个游戏行）。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：正面（3/4，待机 + 选人卡）+ 侧面（朝右，动作的底子），同一个高度、同一套格子；原稿 1:1 按格读回，绝不先画大再缩。匕首要直、轮廓连续。
- 同一张脸贯穿所有帧；跑步要有交叉步（两腿每半圈换前后，第 3、7 帧在身下交叉）。
