# 希尔科（金铲铲之战 · 第 13 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 希尔科是金铲铲之战第 13 赛季（双城之战）的四费卡（炼金男爵 / 统领），祖安的化工男爵。金铲铲里他**拄着一根细长的手杖站着，另一只手举着一支发紫光的微光药剂瓶端详**。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **长相**：瘦削的中年男人，**苍白偏灰的皮肤**，颧骨高、脸颊凹、法令纹深、薄嘴唇、表情冷；**黑色的头发全部往后梳**，头顶的头发翘起来一撮、往后翘成尖；**一只眼睛（远处那只，画面右边）是伤疤眼**：眼白发红、瞳孔是**发光的橙红色**，眼睛周围一圈**暗紫红的疤痕和裂纹**；另一只眼睛正常（灰绿色）；
> - **身上**：**洋红 / 紫红色的衬衫**（立领、袖子卷到小臂），领口一条**白色的领巾**（像领结一样折在胸前）；外面一件**棕色马甲**，领子、前襟、下摆都镶**金边**，前襟两颗**金色盘扣**；手腕上**深棕色的皮护腕**；腰间皮带上挂着**一排 4 支发光的紫色微光药剂管**（竖着挂在胯前，紫色发光液体、铜色管帽）；**深棕色的长裤**，膝盖处一圈灰色的绑带；**深棕色的高筒靴**。
> - **手杖**：一根**细长的黑色手杖**（比他的腰还高），杖头是**绿色的玻璃握柄**和**灰色的金属球头**。
> - **微光药剂瓶**：一支小玻璃瓶，**洋红 / 紫色的发光液体**，**铜色的瓶盖**。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：拄着手杖**（金铲铲原样，附图 1–6、10a）：**3/4 朝右**，**近处的手（画面右）握着手杖**，手杖斜着拄在前脚的前面；**远处的手（画面左）把一支微光药剂瓶举在胸前**，他低头斜眼看着它；双脚分开站稳。
> - **B：不拿手杖**（附图 8、10b）：**3/4 朝右**，站直，**两只手都空着**：近处的手（画面右）自然垂在身侧、**松松地握着一支微光药剂瓶**，远处的手垂在身侧或背在身后；冷冷地看向右前方。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的辛吉德（祖安的炼金术士）、斯维因、杰斯和爆爆（本系列第一个金铲铲英雄），**只看风格**。
> - **长相照金铲铲的模型**（附图 1–5 是模型的待机渲染，附图 3 是脸部特写；附图 6 是官方原画，**伤疤眼、发型、气质和颜色以原画为准**；附图 7 是他施法时一只手高高举起的样子，只看手臂多长）。
> - **比例**：Q 版人类，**头约占身高的三分之一**（脸要大、要清楚），身材细长。
> - **脸要清楚**（附图 3 特写、附图 6 原画）：皮肤 3 档；**两只眼睛一样高**，每只至少 2×2 格；近处的眼睛灰绿色、有一格白色反光；**远处的伤疤眼 2×2 格亮橙红色**，周围一圈暗紫红的疤；深色的眉毛压得很低；嘴一格暗色；头发不能盖住眼睛。
> - **画布用正方形 1536×1536**。**A 和 B：从头顶（翘起的头发）到脚底都约 616 px，也就是约 56 格**；A 宽约 28 格（含手杖和举起的药剂瓶，最多 34 格），B 宽约 20 格（最多 26 格）。脚底在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。手杖、药剂瓶全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。发光的地方（伤疤眼、微光药剂、腰间的药剂管）用**更亮的一档平涂**表示，不要柔光。
> - 不画任何技能特效（储罐、畸变体、毒雾都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/silco-picture/silco-A.png`、`silco-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/silco-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/silco_picture_done.zip`。

## 附图（在压缩包 `silco_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_silco_34.png` | 金铲铲希尔科的模型，待机，3/4 朝右 | 颜色、形状、**角度**、手杖和药剂瓶怎么拿 |
| `refs/2_silco_front.png` | 同一个待机，正面 | 马甲、金边、领巾、腰间的药剂管 |
| `refs/3_silco_head.png` | 头部特写 | **头发、脸、领巾** |
| `refs/4_silco_side.png` | 侧面（右） | 身材厚度、靴子 |
| `refs/5_silco_back.png` | 背后 | 头发后面、马甲背面 |
| `refs/6_silco_art.png` | 官方原画（棋子卡面） | **伤疤眼**、脸、气质、颜色 |
| `refs/7_silco_spell.png` | 模型施法：一只手高举 | 只看手臂的长度 |
| `refs/8_silco_vial.png` | 模型不拿手杖、手拿药剂瓶 | **B**：不拿手杖时的身材 |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 头顶 |
| `refs/10b_layout_B.png` | B 的大小示意 | 只看大小和地面线（B 的手垂在身侧，不是端在胸前） |
| `style/11_style_singed.png` | 本包的辛吉德（祖安的炼金术士），8 倍放大，一格 = 一个像素 | **只看风格**：同一座城的人、药剂怎么画 |
| `style/12_style_swain.png` | 本包的斯维因（8 倍） | **只看风格**：瘦高的中年男人、冷脸、深色衣服 |
| `style/13_style_jayce.png` | 本包的杰斯（8 倍） | **只看风格**：双城之战的人物、马甲和金边 |
| `style/14_style_powder.png` | 本系列的爆爆（8 倍） | **只看风格**：金铲铲英雄在格子上的样子 |

## 提示词：`silco-A.png` / `silco-B.png`（同一段提示词，先画 A 再画 B）

十四张图都附上（没有 9 号），顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fourteen attached images. Images 1-8 show ONE character from a game: a gaunt, cold MIDDLE-AGED CRIME LORD - pale greyish skin, high cheekbones, hollow cheeks, deep lines from nose to mouth, thin lips, low heavy dark brows; BLACK HAIR slicked straight back, a spiky tuft rising and sweeping back at the top. His FAR EYE (image right) is SCARRED: a GLOWING ORANGE-RED eye with a reddish white, ringed by dark red-purple scar tissue and cracks; the near eye is normal, grey-green. A MAGENTA / RED-PURPLE SHIRT with a stand-up collar and sleeves rolled to the forearms, a WHITE CRAVAT folded at his throat; over it a BROWN WAISTCOAT with GOLD TRIM on the lapels, the front edges and the hem, two GOLD toggle clasps down the front; dark brown leather wrist cuffs; on his belt a row of FOUR GLOWING PURPLE SHIMMER VIALS hanging upright in front of his hips (glowing purple liquid, copper caps); dark brown trousers with a grey strap below each knee; tall dark brown boots. He carries a long thin BLACK CANE (taller than his waist) with a GREEN GLASS GRIP and a grey metal knob on top, and a small glass VIAL of GLOWING MAGENTA-PURPLE liquid with a copper cap. (1 his idle, 3/4 view facing right - the look, the ANGLE, how he holds the cane and the vial; 2 the same idle from the front: the waistcoat, the gold trim, the cravat, the vials at his belt; 3 his head close-up: the HAIR and the face; 4 from the side; 5 from behind; 6 the official art: THE SCARRED GLOWING EYE, his face, his mood and colours - follow it for the face; 7 his model with one arm thrown high: how long his arms are; 8 his model without the cane, for picture B.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the ground, the light line the top of his hair. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 an alchemist from the same city, 12 a tall thin cold older man in dark clothes, 13 a man from the same story in a waistcoat with gold trim, 14 a hero of this same series).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the hair, the cane, the vial); his soles level on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; GLOW drawn only as a brighter flat shade (the scarred eye, the vial, the vials at his belt), never a soft halo; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO spell effects (no canister, no monsters, no smoke, no sparkles); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi - his head about ONE THIRD of his body height, the face big and clear, turned to the front-right; a slim, upright body. FACE CLEAR: skin in 3 shades; TWO EYES at the SAME height, each at least 2x2 squares: the near eye grey-green with one white glint square, the FAR eye (image right) BRIGHT ORANGE-RED 2x2 squares with dark red-purple scar squares around it; heavy dark brows; a dark one-square mouth; the hair never over the eyes; the slicked-back hair with its tuft clearly rising at the top. THE COLOURS: hair black / dark grey in 3; skin pale grey-beige in 3; shirt magenta / red-purple in 3-4; cravat white / light grey in 2; waistcoat brown in 3 with gold trim in 2; belt vials glowing purple in 2-3 with copper caps; trousers and boots dark brown in 3; cane black in 2 with a green grip in 2 and a grey knob; the hand vial glowing magenta in 2-3 with a copper cap.
PICTURE A (silco-A.png): LEANING ON THE CANE, 3/4 view facing right (images 1-6 and 10a): his NEAR hand (image right) holds the cane by its green grip, the cane slanting down to the ground just in front of his front foot; his FAR hand (image left) raises a glowing Shimmer vial at chest height and he looks down sideways at it; feet apart, standing firm. About 616 px (about 56 squares) from the top of his hair to his soles, about 28 squares wide with the cane and the vial (never more than 34).
PICTURE B (silco-B.png): NO CANE, 3/4 view facing right (images 8 and 10b): he stands straight, BOTH HANDS FREE: his near hand (image right) hangs at his side loosely holding a glowing Shimmer vial, his far hand hangs at his side or rests behind his back; he looks coldly to the front-right. About 616 px (about 56 squares) from the top of his hair to his soles, about 20 squares wide (never more than 26); his soles on the ground line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、手杖、药剂瓶完整，不出画。
- **A**：约 616 px（约 56 格），3/4 朝右，**近处的手拄手杖、远处的手把微光药剂瓶举在胸前**；脚底在地面线上。
- **B**：约 616 px（约 56 格），**不拿手杖**，两只手垂在身侧，近处的手松松地拿着药剂瓶；脚底在地面线上。
- 两张都要：**往后梳的黑发 + 翘起的一撮**；**远处的伤疤眼亮橙红、周围暗紫红的疤**，两只眼睛一样高；**洋红衬衫 + 白领巾 + 金边棕马甲 + 腰间一排紫色药剂管 + 深棕长裤高筒靴**。
- 没有技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/silco-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/silco_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有希尔科自己的动作（我已经按动作片段渲染出来了，后面的骨架包会附上），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸用在所有帧、两只手（扔药剂、扔储罐时会举起来）、手杖、手里的药剂瓶、腰间的药剂管、马甲下摆。

| 动作 | 金铲铲里怎么做 / 我们的技能 |
|---|---|
| 待机 | 拄着手杖，举起药剂瓶端详 |
| 移动 | 拄着手杖慢慢走（金铲铲原样） |
| 普攻 | 甩手扔出一支微光药剂（金铲铲里是甩飞刀，我们换成药剂瓶） |
| 技能1「罐装畸变体」 | 一只手高高扬起，把储罐扔向敌人，储罐碎开放出畸变体（金铲铲的施法动作） |
| 技能2「微光注射」 | 把药剂瓶递向身边的队友 / 往自己手腕上扎 |
| 大招「炼金狂潮」 | 双手举起一个巨型储罐砸向敌群，绿色微光毒雾散开 |
| 死亡 | 弯腰捂着身体、手杖飞起、跪倒在地（金铲铲原样） |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/silco/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和辛吉德、斯维因、爆爆、诺拉、拉露恩按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_silco_picture.py`（模型在 Riot 客户端的 `TFTSet13.wad.client`；子网格 M_Body / ExtraShimmer（手里的药剂瓶）/ Knife（藏起来）/ M_Cane；七段动作只有路径哈希，`CLIPS` 里按内容命名）。
