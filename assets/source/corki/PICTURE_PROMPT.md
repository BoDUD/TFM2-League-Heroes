# 库奇（英勇投弹手）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 库奇还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**角度**，人、飞机、颜色完全一样：**A = 英雄联盟里的待机，3/4 正面朝右**（机头和机枪朝画面右前方，附图 1）；**B = 同一个待机更靠近侧面**（机身侧面多露出来、机头朝画面右边，附图 8）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（3/4 正面和侧面两张）。
> - **他从不走路**：库奇是一个约德尔人飞行员，**坐在一架小型直升飞机（陀螺机）里**，飞机**悬停在空中**，没有腿、没有轮子着地。
> - **飞行员**（附图 3 头部特写）：**棕色皮革飞行头盔**，头盔顶上一根**银色小尖刺**和一根往后飘的**红色羽毛**；额头上一副**大圆框飞行护目镜，镜片黄色发光**（全身最亮的地方之一）；**一大把白色八字胡**，两边向外翘、很宽（他的招牌）；粉红色大鼻子；脖子上一条**红色围巾**往后飘；**绿色飞行服**，戴手套的手握着机舱边。只露出胸口以上，下半身在机舱里。
> - **飞机**：机身是**钢蓝灰色、像一个张着嘴的怪兽头**——机头上下两排**锯齿状的金属牙**，牙缝里伸出一把**深灰色的多管格林机枪**（朝画面右边）；机头上方两侧各一盏**金黄色的六角形灯**（像眼睛）；机舱边一圈**棕色皮革护垫**；机身后上方两根**金属杆**，各顶一副**木头色螺旋桨**（四片桨叶，黄褐色带浅色条纹）；两侧伸出**钢蓝色的后掠锯齿机翼**；机尾两根**红色喷口的推进器**（黄铜管子连着，红色喷口）；机身下面挂着**两个黄红格子花纹的炸弹**，炸弹头是**棕色金属尖头**，尾巴上有**黄铜色小尾翼**。
> - **姿势**：英雄联盟待机（附图 1、2），平稳悬停，机头朝右，飞行员脸转向观众，**脸（护目镜、八字胡）不能被螺旋桨杆或机翼挡住**。
> - **比例**：**飞行员可以比原版稍大一点**（游戏里只有 30 多像素高，护目镜和八字胡要看得清），但**飞机仍然是主体**，整体紧凑，不要画成一个巨大的方块。参照附图 10–12 的风格（你之前画的古拉加斯、维克托、泽丽）。
> - **画布用横版 1536×1024**：从螺旋桨顶到炸弹底约 520 px，从机翼尖到机枪口约 640 px，全部在画面里，不能出画。
> - 不画任何特效（炸弹爆炸、机枪火光、火箭、火焰带第 3 步再单独画；**螺旋桨画成静止的四片桨叶**，不画转动的模糊圈；推进器喷口不画火焰）；不画地面和影子（他悬停在空中，游戏里会在下面加一块小影子）。
> - 交付：`outputs/corki-picture/corki-model-A.png`、`outputs/corki-picture/corki-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `corki_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_corki_league_front.png` | 英雄联盟原版库奇待机，3/4 朝右 | 颜色、形状、**A 的角度** |
| `refs/2_corki_league_frontal.png` | 同一帧，正面 | 机头的牙、两盏金灯、机枪、两个炸弹 |
| `refs/3_corki_league_head.png` | 飞行员特写 | 头盔、尖刺、红羽毛、黄色护目镜、白八字胡、红围巾、绿衣服 |
| `refs/4_corki_league_back.png` | 同一帧的背后 | 螺旋桨杆、机翼、推进器 |
| `refs/5_corki_splash.png` | 官方加载画面 | 气质（勇敢、开心、老派飞行员） |
| `refs/6_corki_league_run.png` | 英雄联盟里他移动的几个瞬间 | 飞机前倾地飞 |
| `refs/7_corki_league_actions.png` | 普攻、Q 磷光炸弹、E 格林机枪、R 火箭轰击的瞬间 | 飞机怎么动 |
| `refs/8_corki_league_side_b.png` | 待机，更靠近侧面 | **B 的角度** |
| `refs/9_corki_league_side.png` | 待机的侧面（朝右） | 侧面看飞机轮廓 |
| `style/10_style_gragas.png` | 你之前的古拉加斯像素图 | **只看风格**（最近通过的一张） |
| `style/11_style_viktor.png` | 你之前的维克托像素图 | **只看风格**（海克斯机械） |
| `style/12_style_zeri.png` | 你之前的泽丽像素图 | **只看风格**（横版构图） |

## 提示词 A：`corki-model-A.png`（3/4 正面）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and the ANGLE of this picture; 2 the same from the front: the teeth of the nose, the two gold lamps, the gun, the two bombs; 3 the pilot close-up: the leather helmet, the spike and the red plume, the yellow goggles, the white moustache, the red scarf, the green suit; 4 the same from behind: the propeller poles, the wings, the thrusters; 5 the official illustration: his mood; 6 moments of him flying around; 7 moments of his attack and spells; 8 the idle nearer the side - not used in this version; 9 the idle from the side). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 a hextech machine character, image 12 a landscape composition).
Create ONE full pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 520 px from the top of the propellers to the bottom of the bombs and about 640 px from the wing tip to the gun's muzzle, centred, comfortable transparent margins, nothing cut off.
The character: Corki, the Daring Bombardier, a small yordle pilot SITTING IN A LITTLE GYROCOPTER that HOVERS in the air (he never walks; no legs, no wheels touching anything). THE PILOT (shown from the chest up, the rest inside the cockpit): a BROWN LEATHER FLYING HELMET with a SMALL SILVER SPIKE on top and a RED PLUME streaming back; BIG ROUND FLYING GOGGLES with GLOWING YELLOW LENSES; a HUGE WHITE HANDLEBAR MOUSTACHE sweeping out wide on both sides (his trademark); a big pink nose; a RED SCARF streaming back; a GREEN FLIGHT SUIT; gloved hands on the cockpit rim. THE CRAFT: a STEEL-BLUE body shaped like an OPEN-MOUTHED MONSTER HEAD - jagged METAL TEETH top and bottom at the nose, a DARK-GREY MULTI-BARREL GATLING GUN poking out of the mouth toward image right, two GOLDEN HEXAGONAL LAMPS on top of the nose like eyes, a BROWN LEATHER PAD around the cockpit rim; behind and above, TWO METAL POLES each holding a WOODEN FOUR-BLADED PROPELLER (ochre blades with pale stripes, drawn STILL, not as a blur); SWEPT JAGGED STEEL-BLUE WINGS on both sides; two BRASS-PIPED THRUSTERS with RED NOZZLES at the back; under the body hang TWO YELLOW-AND-RED CHECKERED BOMBS with BROWN METAL NOSE CONES and small BRASS FINS.
Pose: League's own idle (images 1 and 2): hovering level, the nose and the gun toward image right, the pilot's face turned toward the viewer; nothing covers the goggles or the moustache (keep the propeller poles and the wings clear of the face).
Proportions: the PILOT may be a little BIGGER than in the game model so his goggles and moustache read at a small size, but the CRAFT stays the bulk of the picture. Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right.
Style: detailed crisp pixel art like images 10-12 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the craft steel blue (pale blue-grey highlights, dark slate shadows), the teeth and the gun dark grey, the lamps and the goggles glowing gold-yellow, the helmet and the cockpit pad brown leather, the moustache white with pale grey shading, the scarf and the plume red, the suit olive green, the propellers ochre wood, the bombs yellow-and-red checks with brown nose cones, the pipes brass; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no muzzle flash, no exhaust flame, no propeller blur, no missiles, no fire), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`corki-model-B.png`（更靠近侧面）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look of this picture; 2 the same from the front: the teeth of the nose, the two gold lamps, the gun, the two bombs; 3 the pilot close-up: the leather helmet, the spike and the red plume, the yellow goggles, the white moustache, the red scarf, the green suit; 4 the same from behind: the propeller poles, the wings, the thrusters; 5 the official illustration: his mood; 6 moments of him flying around; 7 moments of his attack and spells; 8 THE IDLE NEARER THE SIDE - the ANGLE of this picture; 9 the idle from the side). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 a hextech machine character, image 12 a landscape composition).
Create ONE full pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), about 520 px from the top of the propellers to the bottom of the bombs and about 640 px from the wing tip to the gun's muzzle, centred, comfortable transparent margins, nothing cut off.
The character: Corki, the Daring Bombardier, a small yordle pilot SITTING IN A LITTLE GYROCOPTER that HOVERS in the air (he never walks; no legs, no wheels touching anything). THE PILOT (shown from the chest up, the rest inside the cockpit): a BROWN LEATHER FLYING HELMET with a SMALL SILVER SPIKE on top and a RED PLUME streaming back; BIG ROUND FLYING GOGGLES with GLOWING YELLOW LENSES; a HUGE WHITE HANDLEBAR MOUSTACHE sweeping out wide on both sides (his trademark); a big pink nose; a RED SCARF streaming back; a GREEN FLIGHT SUIT; gloved hands on the cockpit rim. THE CRAFT: a STEEL-BLUE body shaped like an OPEN-MOUTHED MONSTER HEAD - jagged METAL TEETH top and bottom at the nose, a DARK-GREY MULTI-BARREL GATLING GUN poking out of the mouth toward image right, two GOLDEN HEXAGONAL LAMPS on top of the nose like eyes, a BROWN LEATHER PAD around the cockpit rim; behind and above, TWO METAL POLES each holding a WOODEN FOUR-BLADED PROPELLER (ochre blades with pale stripes, drawn STILL, not as a blur); SWEPT JAGGED STEEL-BLUE WINGS on both sides; two BRASS-PIPED THRUSTERS with RED NOZZLES at the back; under the body hang TWO YELLOW-AND-RED CHECKERED BOMBS with BROWN METAL NOSE CONES and small BRASS FINS.
Pose: League's idle seen NEARER THE SIDE (image 8): hovering level, more of the craft's flank showing, the nose and the gun pointing image right, the pilot's face still turned three-quarters toward the viewer (both goggle lenses visible); nothing covers the goggles or the moustache (keep the propeller poles and the wings clear of the face).
Proportions: the PILOT may be a little BIGGER than in the game model so his goggles and moustache read at a small size, but the CRAFT stays the bulk of the picture. Keep the whole figure COMPACT, not a giant block.
Style: detailed crisp pixel art like images 10-12 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the craft steel blue (pale blue-grey highlights, dark slate shadows), the teeth and the gun dark grey, the lamps and the goggles glowing gold-yellow, the helmet and the cockpit pad brown leather, the moustache white with pale grey shading, the scarf and the plume red, the suit olive green, the propellers ochre wood, the bombs yellow-and-red checks with brown nose cones, the pipes brass; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no muzzle flash, no exhaust flame, no propeller blur, no missiles, no fire), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，螺旋桨、机翼尖、机枪口、两个炸弹都完整。
- 飞行员：棕色皮头盔、顶上银尖刺和红羽毛、黄色发光护目镜、又宽又翘的白八字胡、粉鼻子、红围巾、绿衣服，只露胸口以上。
- 飞机：钢蓝色怪兽头机身、上下两排金属牙、嘴里伸出深灰格林机枪（朝右）、机头两盏金色六角灯、棕色皮护垫、两根杆上的两副木螺旋桨（静止四片）、后掠锯齿机翼、两个红喷口推进器、机身下两个黄红格子炸弹。
- A 是 3/4 正面；B 更靠近侧面，但护目镜两片镜片都看得到。
- 脸（护目镜、八字胡）没有被杆子、机翼挡住；飞行员稍微放大、飞机仍是主体、整体紧凑。
- 悬停：没有腿、没有轮子；不画地面和影子；没有任何特效（没有枪口火光、喷口火焰、螺旋桨模糊圈）。
- 大像素块清楚，没有糊、没有柔光、没有渐变；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/corki-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/corki/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，**侧面朝右 + 3/4 正面两张**，记忆 side-view-design；Codex 直接画游戏尺寸，用原稿 2:1 描，绝不先画大再缩，古拉加斯的教训）。
- 他没有腿：待机和移动是整架飞机悬停上下浮动 1–2 格 + 螺旋桨转（桨叶换角度）+ 尾部喷口闪动，移动时机身稍前倾；地上一块小影子标落点（用户已确认）。动作全用侧面造型、同一张脸（护目镜 + 八字胡）贯穿所有帧，只有待机和 BP 卡用 3/4 正面。
