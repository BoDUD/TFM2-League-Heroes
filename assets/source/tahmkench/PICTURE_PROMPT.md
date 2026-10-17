# 塔姆·肯奇（河流之王）：先画像素风原图（第 0 步，给 Codex 的提示词）

> 塔姆是一只**戴小礼帽的巨大鲶鱼/蛤蟆样的河中恶魔**：头和身体连成一大团，一张占了半个身子的大嘴咧着笑，满口尖牙，嘴边垂着两根鲶鱼须。这一步请 Codex 照同一段提示词画**两版**全身像素风原图，让我挑一张。两版是同一个塔姆，长相、衣服、颜色、格子大小都一样，只有姿势不同：
> - **A**：英雄联盟的待机（附图 1），咧嘴得意地笑，嘴半张、露出两排牙。
> - **B**：英雄联盟的「凶相待机」（附图 6），嘴张到最大、露出粉色舌头和上下两排尖牙，两只手往两边张开，身子往前探。
>
> 之后第 1 步再按选中的那张做正面 + 侧面的造型。这一版每个游戏像素约 **1.8 格**，附图 9–12 是本包里的加里奥、布隆、酒桶、伊莉丝（伊莉丝和塔姆同样是 1.8 格）。你画的原图会直接按格子读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **不要 Q 版大头**：塔姆整个人就是一颗大头加一张大嘴，比例照原版。圆滚滚的大身子，大嘴占身子上半，**两条很短的粗腿**，手臂不长。不要把他画成大头小身子的卡通娃娃。
> - **头和脸**（附图 3 特写）：
>   - 头顶正中**一顶很小的黑色礼帽**，帽檐窄，帽带是暗红色，带上有一个**金色的卷曲饰物**。
>   - 皮肤是**浅黄绿 / 米绿色**，头顶和背上是**深一些的绿色条纹**。
>   - **近侧一只发光的黄绿色眼睛**，椭圆形，眼窝一圈偏紫的暗影，要看得清；远侧的眼睛被头挡住，最多露一点。
>   - **一张特别宽的大嘴**，从脸的一侧咧到另一侧，嘴里是**暗粉红 / 紫红的口腔**，上下两排**米白色的三角尖牙**。
>   - 吻部伸出**两根长长的鲶鱼须**，粉褐色，根部各套一个**金色的环**，向下垂过嘴边。
> - **衣服**（附图 1、2、4、7）：
>   - 肩上和背上披一件**棕色皮革的短披肩 / 大翻领**，边缘磨旧。
>   - 肚子前面是**暗红 / 酒红色的竖条纹马甲**，有两三个**金色的扣环**。
>   - 身后垂着**深藏青 / 近黑色的燕尾服下摆**。
>   - 近侧前臂套着**一只粗大的棕色皮护臂**，上面有金色的卷纹，手腕上一个**绿色宝石的金扣**。
>   - 手是绿色的，三四根粗手指，带**暗红的短爪**。
>   - 身后拖着**一条短粗的鱼尾**，尾巴尖是**暗红色的鳍**。
>   - 两只粗短的脚，脚趾带白色短爪。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**，两只脚底落在同一条地面线上。
> - **画布用横版 1536×1024**（他和尾巴加起来差不多一样宽）：**从帽顶到脚底约 836 px，也就是约 76 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），鱼须、尾巴、张开的手全在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。绿色皮肤要分出清楚的几档（亮米绿、米绿、绿、深绿）；嘴里的粉红、牙齿的米白、马甲的酒红、披肩的棕色要分得开，不要混成一团；暗色的燕尾服要有亮一点的边缘，看得出形状。
> - 不画任何特效（舌头甩出去、吞人、潜水的水花都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/tahmkench-picture/tahmkench-A.png`、`tahmkench-B.png`（1536×1024 横版，**真透明背景**）；原始生成图原样放进 `outputs/tahmkench-picture/raw/`；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/tahmkench_picture_done.zip`。

## 附图（压缩包 `tahmkench_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用这里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_tahm_idle.png` | 英雄联盟原版塔姆待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_tahm_frontal.png` | 同一帧，几乎正面 | 马甲、扣环、披肩、护臂、两只脚 |
| `refs/3_tahm_head.png` | 头部特写 | 小礼帽、黄绿色眼睛、大嘴尖牙、鲶鱼须和金环 |
| `refs/4_tahm_back.png` | 同一帧的背后 | 背上的绿色条纹、披肩、燕尾服下摆、鱼尾 |
| `refs/5_tahm_splash.png` | 官方加载画面 | 气质（贪婪、得意、危险）、礼帽和大嘴 |
| `refs/6_tahm_aggro.png` | 「凶相待机」，嘴张到最大 | B 的姿势 |
| `refs/7_tahm_side.png` | 待机的侧面（朝右） | 第 1 步用（这一步不用） |
| `refs/8_layout.png` | 布局示意（模型剪贴，只看位置和大小） | 横版画布上他的位置、脚底线（深灰） |
| `style/9_style_galio.png` | 本包的加里奥（大体型），8 倍放大，一格 = 一个像素 | **只看风格**：像素粗细、描边、明暗 |
| `style/10_style_braum.png` | 本包的布隆（8 倍） | **只看风格**（壮汉辅助） |
| `style/11_style_gragas.png` | 本包的酒桶（8 倍） | **只看风格**（大肚子） |
| `style/12_style_elise.png` | 本包的伊莉丝（8 倍，和塔姆一样每游戏像素 1.8 格） | **只看风格**：这个密度下格子有多细 |

## 提示词：`tahmkench-A.png` / `tahmkench-B.png`（同一段提示词，只换最后一句姿势）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a huge, greedy river demon like a giant catfish-toad wearing a tiny top hat (1 his idle in 3/4 view facing right - the look, the ANGLE and pose A of this picture; 2 the same nearly from the front: the waistcoat, its gold clasps, the leather cape, the bracer, both feet; 3 his head close-up: the tiny top hat, the glowing yellow-green eye, the huge toothy grin, the catfish whiskers with gold rings; 4 the same from behind: the green stripes on his back, the cape, the coat tails, the fish tail; 5 the official illustration: his mood; 6 his aggressive idle, the mouth wide open - pose B; 7 his idle from the side - not used here). Image 8 is THIS picture's layout guide: where he goes on the canvas, the dark grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 9-12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading. Image 12 has the same square density this picture needs.
Create ONE pixel-art picture of him, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha). He is about 836 px (about 76 squares) from the top of his hat to the soles of his feet, the soles about 64 px above the bottom edge (the dark grey line of image 8); the whiskers, the tail and the hands whole inside the picture, comfortable transparent margins, nothing cut off; both soles level on one ground line.
NOT CHIBI: his head and body are ONE big round mass - keep the game model's own proportions (image 1): a huge rounded body whose upper half is the enormous mouth, very short thick legs, short arms. Do not draw a big cartoon head on a small body.
THE HEAD: a TINY BLACK TOP HAT perched on the very top, a narrow brim, a dark red hat band with a curly GOLD ornament; skin of pale yellow-green / cream green, darker GREEN stripes over the top of the head and the back; ONE glowing YELLOW-GREEN almond eye on the near side with a purplish shadow round it, clearly readable (the far eye hidden by the head, at most a sliver); an enormous WIDE MOUTH stretching across the face, the inside dark pink / magenta, two rows of cream-white TRIANGULAR TEETH; two long CATFISH WHISKERS from the snout, pinkish-brown, each with a GOLD RING at its root, hanging down past the mouth.
THE CLOTHES: a worn BROWN LEATHER short cape / big collar over the shoulders and back; a WINE-RED vertically striped WAISTCOAT over the belly with two or three GOLD clasps; dark navy / near-black TAILCOAT tails behind; a thick BROWN LEATHER BRACER with gold swirls on the near forearm, a GREEN GEM in a gold clasp at the wrist; green hands with three or four thick fingers and short dark red claws; a short thick FISH TAIL behind him ending in DARK RED fins; two short thick feet with white claws.
THE VIEW: 3/4 view facing right (face to the front-right): the NEAR arm and leg on the image LEFT in full tone, the FAR ones on the image RIGHT a step darker; both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, no stray single odd squares: the skin in clear greens (bright cream green, cream green, green, dark green), the mouth pink, the teeth cream-white, the waistcoat wine red, the cape brown, the coat tails dark navy with lighter edge highlights so the shapes read, the gold small and bright, the eye yellow-green; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no tongue lash, no water, no bubbles, no glow), no background, no ground, no shadow, no text, no frame, no other characters.
POSE A (tahmkench-A.png): his idle (image 1) - a smug closed-lip grin opened just enough to show both rows of teeth, the arms hanging at his sides, the hands a little forward.
POSE B (tahmkench-B.png): his aggressive idle (image 6) - the mouth opened as wide as it goes, the pink tongue and both rows of fangs showing, both arms spread out to the sides with the claws open, the body leaning a little forward.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底）；1536×1024 横版；四周留边，鱼须、尾巴、手完整，不出画。
- **不是 Q 版**：头身一体的大圆身子，大嘴占上半身，两条很短的粗腿。
- 头：小黑礼帽（暗红帽带 + 金色卷饰）在头顶正中；米绿皮肤 + 头顶背上的深绿条纹；**近侧一只发光黄绿眼睛看得清**；超宽的大嘴、粉红口腔、两排米白尖牙；两根带金环的鲶鱼须垂过嘴边。
- 衣服：棕皮披肩、酒红竖条纹马甲 + 金扣环、深藏青燕尾下摆、近侧手臂的棕皮护臂 + 绿宝石金扣、绿手暗红爪、带暗红鳍的鱼尾、白爪的粗短脚。
- 从帽顶到脚底约 836 px（约 76 格）；近侧手脚在画面左边亮色、远侧在右边稍暗；脚底在同一条水平线上；没有任何特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- A、B 两版都画完后，最后写 `outputs/tahmkench-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/tahmkench_picture_done.zip`，这样我这边知道已经交付完了。中间不要停，两版都画完再交。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/tahmkench/codex_picture/`。**先在 8 倍下数描边台阶，量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_elise_hd.py` / `design_jayce_cut.py` 的办法，先量化到约 40 色再读，免得小块颜色丢失）。然后在 PPU 1.8 下和布隆、加里奥、酒桶、诺提勒斯、阿利斯塔的游戏帧并排，给用户挑 A / B 和大小。
- 头的占比照原版（[[head-share-like-oppi]]：大体型角色不做 Q 版头）。用户说脸不对时，先查头的大小，再动五官。
- 选定后写第 1 步：正面（3/4，待机 + 选人卡）+ 侧面（朝右，动作的底子），同一个高度、同一套格子。
